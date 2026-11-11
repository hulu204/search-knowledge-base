---
title: 'Elasticsearch Hybrid Search Recipes - Benchmarked'
company: softwaredoug
tag: 召回
date: 2025-03-13
url: https://softwaredoug.com/blog/2025/03/13/elasticsearch-hybrid-search-strategies
account: 
origin: harvest3-202607
---
Previously I wrote a blog article on [Elasticsearch hybrid search](https://softwaredoug.com/blog/2025/02/08/elasticsearch-hybrid-search). Let’s get actual numbers on different solutions.

It that previous post, I discussed how Elasticsearch’s KNN query can only retrieve some top N for subsequent boosting, etc. So we discussed a strategy of getting KNN candidates filtered to different buckets of lexical candidates. Then build out boosts on top of those candidates to tie break or pull up important documents. In this blog post ([code here](https://github.com/softwaredoug/es-vector-sandbox)). I gradually build up this strategy using the [WANDS Furniture](https://github.com/wayfair/WANDS/tree/main) e-commerce dataset from Wayfair. I embed the name and description with MiniLM and kick the tires to get some relevance stats on each hybrid search strategy.

So let’s go for a ride 🚗. And please, be critical, and try and find ways to improve upon what I’ve done here!

## Baseline - naive BM25 crossfields search

Search all the fields in a cross-field search. Cross-field ensures that all the search terms have the same document frequency - a key component of the BM25 algorithm used to score lexical results. So it’s often a first stop shop.

```
def search_baseline(es: Elasticsearch, query: str):
    body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["product_name^10", "product_description", "product_class"],
                "type": "cross_fields"
            }
        }
    }
    hits = es.search(index="wands_products", body=body)
    return hits
```

Evals - NDCG using WANDS queries + judgments

```
Running baseline
Mean NDCG: 0.6983108389843456
Median NDCG: 0.7799082337019198
```

## Naive KNN

Search using Elasticsearch’s KNN query, embedding product name and description, then searching by cosine similarity to that embedding using Elasticsearch’s HNSW search.

```
def search_knn(es: Elasticsearch, query: str):
    query_vector = minilm(query)
    body = {
        "query": {
            "knn": {
                "field": "product_name_description_minilm",
                "query_vector": query_vector.tolist(),
            }
        },
        "_source": ["product_name", "product_description"]
    }
    hits = es.search(index="wands_products", body=body)
    return hits
```

```
Running knn
Mean NDCG: 0.6953041112365016
Median NDCG: 0.7723200343340987
```

## Reciprocal Rank Fusion (RRF)

Strategy where we merge results from two systems using `1/rank` from each retrieval source. Then sort by the sum of `1/rank` for each document.

RRF is a common strategy when introducing vector search to an existing system. I’ve written how [RRF is not enough](https://softwaredoug.com/blog/2024/11/03/rrf-is-not-enough), and based on this change, there really is no incremental gain.

```
def rrf(es: Elasticsearch, query: str, search_fn1=search_knn, search_fn2=search_baseline):
    """Implement reciprocal rank fusion using search_fn1 and search_fn2."""
    hits1 = search_fn1(es, query)
    df : list | pd.DataFrame = []
    for idx, hit in enumerate(hits1['hits']['hits']):
        df.append({
            "product_id": hit['_id'],
            "product_name": hit['_source']['product_name'],
            "product_description": hit['_source']['product_description'],
            "score": hit['_score'],
            "rank": idx + 1,
            "reciprocal_rank": 1 / (idx + 1)
        })
    hits2 = search_fn2(es, query)
    for idx, hit in enumerate(hits2['hits']['hits']):
        df.append({
            "product_id": hit['_id'],
            "product_name": hit['_source']['product_name'],
            "product_description": hit['_source']['product_description'],
            "score": hit['_score'],
            "rank": idx + 1,
            "reciprocal_rank": 1 / (idx + 1)
        })
    df = pd.DataFrame(df)
    df = df.groupby('product_id').agg({
        "product_name": "first",
        "product_description": "first",
        "score": "mean",
        "rank": "mean",
        "reciprocal_rank": "sum"
    })
    df = df.sort_values("reciprocal_rank", ascending=False)
    # Back to hits
    hits = []
    for idx, row in df.iterrows():
        hits.append({
            "_id": idx,
            "_score": row['reciprocal_rank'],
            "_source": {
                "product_name": row['product_name'],
                "product_description": row['product_description']
            }
        })
    return {"hits": {"hits": hits}}
```

```
Running rrf
Mean NDCG: 0.7068035290192084
Median NDCG: 0.7663491917568945
```

## Naive Hybrid

Remember Elasticsearch’s KNN retrieval can only get some top N set of candidates. Here we select vector candidates with some sort of lexical match, ignoring the others, by filtering to those candidates, but still rank on KNN similarity to minilm.

```
def search_hybrid(es: Elasticsearch, query: str):
    query_vector = minilm(query)
    body = {
        "query": {
            "knn": {
                "field": "product_name_description_minilm",
                "query_vector": query_vector.tolist(),
                "filter": {
                    "multi_match": {
                        "query": query,
                        "fields": ["product_name", "product_description", "product_class"],
                        "type": "cross_fields"
                    }
                }
            }
        },
        "_source": ["product_name", "product_description"]
    }
    hits = es.search(index="wands_products", body=body)
    return hits
```

```
Running hybrid
Mean NDCG: 0.7092796426405182
Median NDCG: 0.7799776597284811
```

## Add pure vector fallback

We can begin to look at multiple buckets of candidates. Here there are two candidate sets wrapped by the `dis_max` query below (which just takes the max score per document). One bucket (the first knn search) is the clause where we filter to lexical matches, and rank by knn similarity. The second clause is a lower weighted clause on just the vector similarity.

Why would we do this? Well the second clause is like a fallback, if no lexical matches exist for the query, we can fallbck to the vector results.

```
def search_hybrid_dismax(es: Elasticsearch, query: str):
    query_vector = minilm(query)
    body = {
        "query": {
            # Give max score to queries
            "dis_max": {
                "queries": [
                    # Hybrid clause
                    {"knn": {
                        "field": "product_name_description_minilm",
                        "query_vector": query_vector.tolist(),
                        "filter": {
                            "multi_match": {
                                "query": query,
                                "fields": ["product_name", "product_description", "product_class"],
                                "type": "cross_fields"
                            }
                        },
                        "boost": 10.0
                    }},
                    # Fallback
                    {"knn": {
                        "field": "product_name_description_minilm",
                        "query_vector": query_vector.tolist(),
                        "boost": 0.1
                    }}
                ]
            }
        },
        "_source": ["product_name", "product_description"]
    }
    hits = es.search(index="wands_products", body=body)
    return hits
```

```
Running hybrid_dismax
Mean NDCG: 0.7082863052262378
Median NDCG: 0.7802153547674867
```

## Add knn candidates with all search terms

We can add candidates we have even more confidence in.

Below, we add a clause to the dismax to get additional set of candidates corresponding to those with 100% of the query terms (notice `minimum_should_match`). We give those the biggest boost possible. So there are now 3 tiers to fall back on. First the results matching all terms, then any lexical match, then 0.1 \* the vector match.

Scoring is now `max(100 * vector_for_all_matches, 10*any match, 0.1*pure vector)`

This now pulls away from the previous solutions, with median NDCG getting above 0.8.

```
def search_hybrid_dismax_mm100(es: Elasticsearch, query: str):
    query_vector = minilm(query)
    body = {
        "query": {
            "dis_max": {
                "queries": [
                    {"knn": {
                        "field": "product_name_description_minilm",
                        "query_vector": query_vector.tolist(),
                        "filter": {
                            "multi_match": {
                                "query": query,
                                "fields": ["product_name", "product_description", "product_class"],
                                "type": "cross_fields",
                                "minimum_should_match": "100%"
                            }
                        },
                        "boost": 100.0
                    }},
                    {"knn": {
                        "field": "product_name_description_minilm",
                        "query_vector": query_vector.tolist(),
                        "filter": {
                            "multi_match": {
                                "query": query,
                                "fields": ["product_name", "product_description", "product_class"],
                                "type": "cross_fields"
                            }
                        },
                        "boost": 10.0
                    }},
                    # Fallback
                    {"knn": {
                        "field": "product_name_description_minilm",
                        "query_vector": query_vector.tolist(),
                        "boost": 0.1
                    }}
                ]
            }
        },
        "_source": ["product_name", "product_description"]
    }
    hits = es.search(index="wands_products", body=body)
    return hits
```

```
Running hybrid_dismax_mm100
Mean NDCG: 0.7191137662030058
Median NDCG: 0.8048109992093389
```

## Add product name boost

Finally, as I said in my blog article, the “boosts” we want to nudge up the search results. This is the same as the previous solution, but adds the should clause w/ boosts

Mean/median really pull away here

```
def search_hybrid_dismax_name_boosted(es: Elasticsearch, query: str):
    query_vector = minilm(query)
    body = {
        "query": {
            "bool": {
                "should": [
                    # A title boost
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["product_name"],
                            "boost": 10
                        }
                    },
                ],
                "must": [
                    {"dis_max": {
                        "queries": [
                            {"knn": {
                                "field": "product_name_description_minilm",
                                "query_vector": query_vector.tolist(),
                                "filter": {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["product_name", "product_description", "product_class"],
                                        "type": "cross_fields",
                                        "minimum_should_match": "100%"
                                    }
                                },
                                "boost": 100.0
                            }},
                            {"knn": {
                                "field": "product_name_description_minilm",
                                "query_vector": query_vector.tolist(),
                                "filter": {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["product_name", "product_description", "product_class"],
                                        "type": "cross_fields"
                                    }
                                },
                                "boost": 10.0
                            }},
                            # Fallback
                            {"knn": {
                                "field": "product_name_description_minilm",
                                "query_vector": query_vector.tolist(),
                                "boost": 0.1
                            }}
                        ]
                    }}
                ]
            }
        },
        "_source": ["product_name", "product_description"]
    }
    hits = es.search(index="wands_products", body=body)
    return hits
```

```
Running hybrid_dismax_name_boosted
Mean NDCG: 0.7496680793685926
Median NDCG: 0.8417690923079354
```

### Results summary:

Summary of results, with caveats, this is just one dataset, and changes in NDCG do not indicate statistical significance. Do your own analysis, yadda, yadda. But these to correspond to what I’ve seen professionally.

| Run | NDCG mean | NDCG median |
| --- | --- | --- |
| BM25/cross\_fields | 0.69831 | 0.77990 |
| Pure KNN | 0.695384 | 0.771501 |
| RRF | 0.706772 | 0.766349 |
| Hybrid filter | 0.708746 | 0.779978 |
| Add vector fallback | 0.707997 | 0.780215 |
| Add all-terms (mm=100%) clause | 0.719325 | 0.804811 |
| Add name boost | 0.749669 | 0.841770 |

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---