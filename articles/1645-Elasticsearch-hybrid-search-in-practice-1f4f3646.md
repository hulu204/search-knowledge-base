---
title: 'Elasticsearch hybrid search in practice'
company: softwaredoug
tag: 召回
date: 2025-02-08
url: https://softwaredoug.com/blog/2025/02/08/elasticsearch-hybrid-search
account: 
origin: harvest3-202607
---
Building hybrid search with Elastisearch requires wrestling with one of the hairiest queries out there - the [knn query](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html). Indeed it’s marked as an “expert level” feature, and under active development for good reason.

I’ve stubbed my toe a bunch, so let me walk you through how I’ve arrived at effective hybrid search with Elasticsearch combining the best candidates from vector + lexical search.

## Unexpected 0 results from KNN query filtering

Currently, filters are the blunt instrument Elasticsearch uses to combine vector and lexical candidates for later processing. You list the types of lexical matches you want to be ranked with a vector similarity. So naturally it’s the first place you’ll stub your toe.

Filtering works differently for knn queries, leading to surprising cases where you get 0 results back

Typically a filtered Elasticsearch query might look like:

```
{
  "query": {
    "bool": {
      "filter": {   <-- PREFILTER to couches
        "match": {
          "category": "couches"
        }      },
      "should": [
        {
          "multi_match": {   <-- within couches, rank loveseat sofa by BM25
            "query": "loveseat sofa",
            "fields": ["name", "description"]
          }
        }
      ]
    }
  }
}
```

Naturally when you use KNN query, you’d think this would work:

```
{
  "query": {
    "bool": {
      "filter": {   <-- PREFILTER to couches?
        "match": {
          "category": "couches"
        }      },
      "should": [
        {
          "knn_query": {   <-- within 'couches', rank 'loveseat' sofa description embedding similarity?
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3]
          }
        }
      ]
    }
  }
}
```

Nope, if you do this pattern, you may notice, this somehow gives you 0 results.

The big gotcha: for knn this is a POST-FILTER not a PRE-FILTER. It *removes* results after ranking. It doesn’t filter to results before being ranked. And, because `knn_query` produces some `k` results, you can easily get a top `k` with no `category:couches`, leading to filtering out every result, and giving you with zero search results.

```
{
  "query": {
    "bool": {
      "filter": {   <-- AFTER - Remove non couches
        "match": {
          "category": "couches"
        }
      },
      "should": [
        {
          "knn_query": {   <-- FIRST - Get some K candidates close to embedding
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3]
          }
        }
      ]
    }
  }
}
```

The solution - you need to pass the filters to knn-query’s filter argument to pre-filter:

```
{
  "query": {
    "knn_query": {   <-- THEN rank these based on description embedding similarity

        "filter": {   <-- FIRST - Remove non couches as you traverse HNSW graph
          "match": {
            "category": "couches"
          }
        },
        "field": "description-embedding",
        "query_vector": [0.1, -0.2, 0.3]
      }
    }
}
```

OK now we have reasonable “couch” candidates close to our description embedding. Now, what happens when you want to boost knn query scores by a lexical attribute?

### Tuning number of retrieved candidates

Typically you “boost” in Elasticsearch by adding a clause to a boolean query:

```
{
  "query": {
    "bool": {
      "should": [   <-- AFTER - Boost loveseats (this score is added)
        "match": {
          "tag": "loveseat"
        }
      ],
      "must": [
        {
          "knn_query": {   <-- THEN - Get some K candidates close to embedding
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3],
            "filter": {   <-- FIRST - Remove non couches as you traverse HNSW graph
              "match": {
                "category": "couches"
              }
            }
          }
        }
      ]
    }
  }
}
```

Looking at this query, you might expect, that you’re boosting anything that matches “loveseat”. Even lower scored knn query results would get boosted.

Unfortunately, again you’ll find a surprise. The knn query is only pulling back some top `k` results for subsequent layers to boost, post-filter, etc. If your index has 2000 loveseats, and if out of knn’s top `k` only 2 loveseats come back, then your results will look like

```
 - loveseat1
 - loveseat2
 - some other furniture
 ...
```

Where my other 1998 loveseats!!

You CAN tune the `k` results that come back using `num_candidates` and `k`, casting a wider net and hopefully snagging more loveseats. It’s a bit of a dark art tuning these, and requires some awareness of the HNSW graph traversal:

* `num_candidates` - the number of candidates to pull from the HNSW graph in the initial phase
* `k` - the actual k returned from the query, resulting from reranking `num_candidates` on your similarity (ie cosine) to get the top k closest embeddings

In addition, there is a `similarity` floor to set your cosine (or whatever) similarity minimum. With these we might set:

```
    ...
      "knn_query": { 
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3],
            "k": 100,
            "num_candidates": 200,
            "similarity": 0.2,
            "filter": {  
              "match": {
                "category": "couches"
              }
            }
          }
    ...
```

Based on what I know about HNSW, here are my *presumptions* on tuning these:

* We can increase `k`/`num_candidates` to get more candidates, at the cost of JVM memory pressure and performance. We’d pluck more loveseats to boost on, but we’d want to do a great deal of performance testing before shipping to a high QPS environment
* With a `similarity` floor, we might help performance by restricting the graph traversal space, hopefully focusing on more relevant candidates, but eliminating some “loveseat” candidates

Then there’s the complication of knn’s `filter` clause. As we discussed, this is a *pre-filter*. Once again, this defies your typical expectations of how a pre-filter impacts performance, as explained [in the docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#approximate-knn-search-and-filtering):

> Unlike conventional query filtering, where more restrictive filters typically lead to faster queries, applying filters in an approximate kNN search with an HNSW index can decrease performance. This is because searching the HNSW graph requires additional exploration to obtain the num\_candidates that meet the filter criteria.

So there’s a three-way optimization problem to know about when traversing the graph

* Tuning `similarity` to improve vector precision and reduce the amount of space the graph traversal. But setting it too restrictively will reduce recall (perhaps excluding the `loveseats` above we want to boost on)
* Tuning `k`/`num_candidates` to cast a reasonably wide net, but setting too high means a more complex graph traversal
* Tuning `filter`s to make sure we only see the matches we care about, but a lot of filters, with a low `similarity` and high `num_candidates` will create a more complex graph traversal, slowing performance

### KNN scores for all the lexical candidates we care about

Let’s take a step back and think what we want from first principles. Then we can use the tools and their restrictions to get close.

Ideally, what we need is a first pass retrieval that would rank pretty much the entire index on KNN similarity. Then I can select a set of lexical candidates out of that set to manipulate (boost, etc):

![entire index ranked](/assets/media/2025/entire-index-knn-query.png)

But I can’t do that. It’s not practical. In reality, at a minimum, there will be some similarity floor / top k excluding at least some of what I want to also boost:

![entire index ranked](/assets/media/2025/with-k-set-knn-query.png)

Further, filters will leave out important results I want to promote for lexical candidates:

```
    ...
      "knn_query": { 
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3],
            "k": 100,
            "num_candidates": 200,
            "similarity": 0.2,
            "filter": {  
              "match": {
                "category": "couches"
              }
            }
          }
    ...
```

![entire index ranked](/assets/media/2025/with-filter-set-knn-query.png)

So I’ve settled on a kind of hacky strategy. When I want to boost something, I ensure that I insert the “boost” into the filters. So the filter becomes something like:

```
    ...
      "knn_query": { 
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3],
            "k": 100,
            "num_candidates": 200,
            "similarity": 0.2,
            "filter": {
              "bool": [
                "should": [
                  {"match": {
                    "category": "couches"
                  }},
                  {match": {
                    "tag": "loveseat"
                  }}
                ]
             }
            }
          }
    ...
```

This gives me a knn results like this:

![entire index ranked](/assets/media/2025/only-boost-in-filter-knn-query.png)

But this itself *still* doesn’t do what I need. In any meaningful search application, there will be more than one set of lexical candidates to manipulate (boost, filter, downboost, etc). Most search applications have many distinct sets of lexical candidates that should get in the highest ranked results, such as:

1. Boost when the query matches the product’s expected color
2. Boost when the query matches the product’s brand name
3. Boost when the keywords are a strong match for the name, description, etc
4. Boost when the item is newer / fresher
5. …

etc

Each of these could be implemented in completely different similarity systems (taxonomies, BM25, numerical etc) and have their own scoring to factor in.

I need candidates from each lexical candidate set 1..N in my top K out of knn search. This would give representatives from each to play with with boosts.

So what if we just jam them all into one filter? Such as:

```
    ...
      "knn_query": { 
            "field": "description-embedding",
            "query_vector": [0.1, -0.2, 0.3],
            "k": 100,
            "num_candidates": 200,
            "similarity": 0.2,
            "filter": {
              "bool": [
                "should": [
                 {"multi_match": {        # (1) Normal lexical matching candidates
                    "fields": ["name, "description"],
                    "query": "ashley blue leather loveseat"
                  }},
                  {"match": {        # (2) Category match candidates
                    "category": "couches"
                  }},
                  {match": {       # (3) tag match candidates
                    "tag": "loveseat"
                  }},
                  {match": {        # (4) color match candidates
                    "color": "blue"
                  }},
                  {match": {         # (5) Material match candidates
                    "material": "leather"
                  }},
                  {match": {         #  (6) Brand match candidates
                    "brand": "ashley"
                  }},
                ]
             }
            }
          }
    ...
```

This just gives closest `k` matcing these filters. Without consideration of “representing” the groups equally. We might have matches of filter (1) but none of (2) and (3) etc. Just by dumb luck, with k=1000, the top 900 might be matches from the “normal lexical matching” candidates, then maybe 95 match color, and 5 match material. What we really want is a fair mix of all of these. But filtering just gives us k scores close to the query vector, without thought of equal representation.

So our results look like this:

![entire index ranked](/assets/media/2025/one-filter-dominates-knn-query.png).

From the image, we actually want some k of the red lexical candidates and k of the green ones.

Unfortunately, to get this, you need to DUPLICATE the knn query to make sure to get a mix of candidates from the different lexical sets:

Essentially I do this:

```
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {            <-- ADD boosts the loveseats
            "tag": "loveseat"
          }
        },
         {"multi_match": {            <-- ADD BM25 score of the original queries
            "fields": ["name, "description"],
            "query": "blue leather loveseat"
          }}
          ...
      ],
      "must": [          #< Original scoring of different KNN groups
        {
          "bool": {
            "should": [
              {
                "knn_query": {                <-- KNN Candidate set A (couches that are loveseats)
                  "field": "description-embedding",
                  "query_vector": [0.1, -0.2, 0.3],
                  "filter": {
                    "bool": {
                      "should": [
                        {
                          "match": {
                            "category": "couches"
                          }
                        },
                        {
                          "match": {
                            "tag": "loveseat"
                          }
                        }
              ]}}}},
              {
                "knn_query": {            <-- KNN Candidate set B (just couches)
                  "field": "description-embedding",
                  "query_vector": [0.1, -0.2, 0.3],
                  "filter": {
                    "match": {
                      "category": "couches"
                    }
                  }}{
               {
                "knn_query": {            <-- KNN Candidate set C (lexical search of a text attributes)
                  "field": "description-embedding",
                  "query_vector": [0.1, -0.2, 0.3],
                  "filter": {
                   {"multi_match": {
                      "fields": ["name, "description"],
                      "query": "blue leather loveseat"
                    }}
                  }
]}}]}}}
```

So essentially, this gives me these candidates, with more balanced representatives from each lexical candidate set:

![entire index ranked](/assets/media/2025/multiple-filter-knn-query.png).

To take things a step further, one further minor complication. The scores out of `must` and `should` all get summed together. So what happens when doc A comes back in different candidate sets? IE it’s likely a document could match “blue leather loveseat” (candidate set C) AND be in `category:couches` (category set B). So two filter matches, two knn scores. As this query stands, doc A would get `2 * knn scorey` because of the boolean query’s `should` above summing the knn query clauses together.

So we can take this a step further by wrapping the knns in a [dismax query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-dis-max-query.html). This takes the best score for each document in the child queries instead of summing them. It’s a max() not a sum(). This gives us closer to what we wanted in first principles - a knn score for each member of our candidate set.

```
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {            <-- boosts the loveseats (essentially candidate set B)
            "tag": "loveseat"
          }
        },
         {"multi_match": {            <-- BM25 score of the original queries
            "fields": ["name, "description"],
            "query": "blue leather loveseat"
          }}
          ...
      ],
      "must": [          #< Original scoring of different KNN groups
        {
          "dis_max": {      #< Take only one KNN score per doc
            "queries": [       
              {
                "knn_query": {                <-- KNN Candidate set A (couches that are loveseats)
                  "field": "description-embedding",
                  "query_vector": [0.1, -0.2, 0.3],
                  "filter": {
                    "bool": {
                      "should": [
                        {
                          "match": {
                            "category": "couches"
                          }
                        },
                        {
                          "match": {
                            "tag": "loveseat"
                          }
                        }
              ]}}}},
              {
                "knn_query": {            <-- KNN Candidate set B (just couches)
                  "field": "description-embedding",
                  "query_vector": [0.1, -0.2, 0.3],
                  "filter": {
                    "match": {
                      "category": "couches"
                    }
                  }}{
               {
                "knn_query": {            <-- KNN Candidate set C (lexical search of a text attributes)
                  "field": "description-embedding",
                  "query_vector": [0.1, -0.2, 0.3],
                  "filter": {
                   {"multi_match": {
                      "fields": ["name, "description"],
                      "query": "blue leather loveseat"
                    }}
                  }
]}}]}}}
```

Because I’ve tuned for the candidates I care about, I can set k pretty low, and I should be good. Hopefully with a low enough k, high enough similarity floor, I can avoid too many performance issues with Elasticsearch. I can also omit knn queries when, perhaps, a given attribute to boost on (ie color, etc) is missing from the query.

So this works, but with pretty big headaches I’m still noodling over:

* I will repeat the HNSW search, which will cause repeated graph traversals
* It’s a big ugly query with lots of repetition
* How to think about combining scores numerically - BM25, tags, taxonomies, embedding. IE should we be summing (as here?) multiplying? Doing something smarter?

Ideally I’d like to reduce this to just one knn search, focused on equal representation from lexical candidate groups. If anyone has ideas, let me know!

## Suggestions for Elastic

Maybe there could be a way to have a single HNSW traversal, but have a more flexible way to specify the sets of lexical candidates I want in my top results? For example, could I somehow tell knn query “here are two distinct sets of filters, I want N candidates from each bucket”. Then pass that up?

Something like:

```
   ...
   "knn_query": {             
    "field": "description-embedding",
    "query_vector": [0.1, -0.2, 0.3],
    "candidates": {
      [{"bool": {         <-- Get K from this set
        "filter": [
          {
            "match": {
              "tag": "loveseat"
            }
          }]}},
       {
        {"bool": {        <-- Get K from this set
        "should": [
          {
            "match": {
              "category": "couches"
            }
          },
          {
            "match": {
              "tag": "loveseat"
            }
          },

           ]}}}]
```

You could also optionally allow different boosts to each candidate set so that one set comes higher than another.

I don’t know whether knowing this sort of information ahead of time helps or not, but it seems possible it might help y’all traverse HNSW more efficiently in a way more conducive to focusing on the subsequent lexical scoring phases.

### Feedback welcome

I hope you respond (maybe with your own blog!) about how to improve this situation. Or where I’m wrong, missing some important documentation, detail, etc. I know Elastic will continue to improve the usability of this area, so I’m excited to see what’s next.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---