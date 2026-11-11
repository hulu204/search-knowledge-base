---
title: 'Elasticsearch retrievers architecture and use-cases'
company: Elastic
tag: 工程相关
date: 2024-11-14
url: https://www.elastic.co/search-labs/blog/elasticsearch-retrievers-ga-8-16-0
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch retrievers architecture and use-cases

Elasticsearch retrievers have gone through a significant revamp and are now generally available for all to use. Learn all about their c and use-cases.

November 14, 2024

[Panagiotis Bailis](/search-labs/author/panagiotis-bailis)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

In this blog post we'll take another deep dive with retrievers. We've already talked about them in previous blogs from their [very introduction](https://www.elastic.co/search-labs/blog/elasticsearch-retrievers) to [semantic reranking using retrievers](https://www.elastic.co/search-labs/blog/semantic-reranking-with-retrievers). Now, we're happy to announce that retrievers are becoming generally available with Elasticsearch 8.16.0, and in this blog post we'll take a technical tour on how we implemented them, as well as we'll get the chance to discuss the newly available capabilities!

## Elasticsearch retriever

The main concept of a `retriever` remains the same as with their initial release; retrievers is a framework that provides the basic building blocks that can be stacked hierarchically to build multi-stage complex retrieval and ranking pipelines. E.g. of a simple `standard` retriever, which just bring backs all documents:

```
GET retrievers_example/_search
{
    "retriever": {
        "standard": {
            "query": {
                "match_all": {}
            }
        }
    }
}
```

Pretty straightforward, right? In addition to the `standard` retriever, which is essentially just a wrapper around the standard `query` search API element, we also support the following types:

* `knn` - return the top documents from a kNN (k Nearest Neighbor) search
* `rrf` - combine results from different retrievers based on the RRF (Reciprocal Rank Fusion) ranking formula
* `text_similarity_reranker` - rerank the top results of a nested retriever using a `rerank` type inference endpoint

More detailed information along with the specific parameters for each retriever can also be found in the Elasticsearch [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html).

Let's briefly go through some of the technical details first, which will help us understand the architecture and what has changed and why all these previous limitations have now been lifted!

## Technical drill down of retrievers

One of the most important (and requested) things that we wanted to address was the ability to use any retriever, at any nesting level. Whether this means having 2 or more `text_similarity_reranker` stacked together, or an `rrf` retriever operating on top of another `rrf` along with a `text_similarity_reranker`, or any combination and nesting you can think of, we wanted to make sure that this would be something one could express with retrievers!

To account for this, we have introduced some significant changes to the retriever execution plan. Up until now, retrievers were evaluated as part of the standard search execution flow, where (in a simplified scenario for illustration purposes) we reach out to the shards twice:

* once for querying the shards and bringing back `from + size` documents from each shard, and
* once for fetching all field data and perform any additional operations (e.g. highlighting) for the true top `[from, from+size]` results.

This is a nice linear execution flow that is (relatively) easy to follow, but introduces some significant limitations if we want to execute multiple queries, operate on different results sets, etc. In order to work around this, we have moved to an eager evaluation of all sub-retrievers of a retriever pipeline at the very early stages of query execution. This means that, if needed, we are recursively rewriting any retriever query to a simpler form, the specifics of which depend on the retriever type.

* For non-compound retrievers we rewrite similar to how we do in a standard query, as they could still follow the linear execution plan.
* For compound retrievers, i.e. for retrievers that operate on top of other retriever(s), we flatten them to a single `rank_window_size` result set, which is essentially a `<doc, shard>` tuple list that represents the top ranked documents for this retriever.

Let's see what this actually looks like, by working through the following (rather complex) retriever request:

```
{
    "retriever": {
        "rrf": {                                                                                    [1]
            "retrievers": [
                {
                    "knn": {                                                                        [2]
                        "field": "emb1",
                        "query_vector_builder": {
                            "text_embedding": {
                                "model_id": "my-text-embedding-model",
                                "model_text": "LLM applications in information retrieval"
                            }
                        }
                    }
                },
                {
                    "standard": {                                                                   [3]
                        "query": {
                            "term": {
                                "topic": "science"
                            }
                        }
                    }
                },
                {
                    "rrf": {                                                                        [4]
                        "retrievers": [
                            {
                                "standard": {                                                       [5]
                                    "query": {
                                        "range": {
                                            "year": {
                                                "gte": 2020
                                            }
                                        }
                                    }
                                }
                            },
                            {
                                "knn": {                                                            [6]
                                    "field": "emb2",
                                    "query_vector_builder": {
                                        "text_embedding": {
                                            "model_id": "my-text-embedding-model",
                                            "model_text": "Vector scale on production systems"
                                        }
                                    }
                                }
                            }
                        ],
                        "rank_window_size": 100,
                        "rank_constant": 10
                    }
                }
            ],
            "rank_window_size": 10,
            "rank_constant": 1
        }
    }
}
```

The `rrf` retriever above is a compound one, as it operates on the results of some other retrievers, so we'll try to rewrite it to a simpler, flattened, list of `<doc, shard>` tuples, where each tuple specifies a document and the shard that it was found on. This rewrite will also enforce a strict ranking, so no different sort options are currently supported.

Let's proceed now to identify all components and describe the process of how this will be evaluated:

[1] top level `rrf` retriever; this is the parent of all sub-retrievers which will be rewritten and evaluated last, as we'd first need to know the top 10 (based on `rank_window_size`) results from each of its sub-retrievers.

[2] This `knn` retriever is the first child of the top level `rrf` retriever and uses an embedding service (`my-text-embedding-model`) to compute the actual query vector that will be used. This will be rewritten as the usual `knn` query by making an async request to the embedding service to compute the vector for the given `model_text`.

[3] A `standard` retriever that is also part of the top-level's `rrf` retriever's children, which returns all documents matching `topic: science` query.

[4] Last child of the top-level `rrf` retriever which is also an `rrf` retrievers that needs to be flattened.

[5] [6] similar to [2] and [3], these are retrievers that are direct children of an `rrf` retriever, for which we will fetch the top 100 results (based on the `rrf` retriever's `rank_window_size` [4]) for each one, combine them using the `rrf` formula, and then rewrite to a flattened `<doc, shard>` list of the true top 100 results.

The updated execution flow for retrievers is now as follows:

* We'll start by rewriting all leaves that we can. This means that we'll rewrite the `knn` retrievers [2] and [6] to compute the query vector, and once we have that we can move up one level in the tree.
* At the next rewrite step, we are now ready to evaluate the nested `rrf` retriever [4], which we will eventually rewrite to a flattened `RankDocsQuery` query (i.e. a list of `<doc, shard>` tuples).
* Finally, all inner rewritten steps for the top-level `rrf` retriever [1] will have taken place, so we should be ready to combine and rank the true top 10 results as requested. Even this top-level `rrf` retriever will rewrite itself to a flattened `RankDocsQuery` which will be later used to proceed with the standard linear search execution flow.

Visualizing all the above, we have:

![Retrievers example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt54af69393bb29026/6a16f6712b835f0c34f4afc0/36d31c4e4562e73c7ccc6b6f2036d9bdc5c1e37c-1152x648.gif)

Looking at the example above, we can see how a hierarchical retriever tree is asynchronously rewritten to just a simple `RankDocsQuery`. This simplification gives us the nice (and desired!) side effect of eventually executing a normal request with explicit ranking, and in addition to that we can also perform any complementary operations we choose.

## Playing with the (golden) retrievers!

As we briefly mentioned above, with the rework in place, we can now support a plethora of additional search features! In this section we'll go through some examples and use-cases, but more can also be found in the [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/retrievers-overview.html).

We'll start with the most coveted one which is composability, i.e. the option to have any retriever at any level of the retriever tree.

### Composability

In the following example, we want to perform a `semantic` query (using an embedding service like `ELSER`), and then merge those results along with a `knn` query, using `rrf`. Finally, we'd want to rerank those using the `text_similarity_reranker` retriever using a reranker. The retriever to express the above would look like this:

```
GET /retrievers_example/_search
{
    "retriever": {
        "text_similarity_retriever": {
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {
                            "standard": {
                                "query": {
                                    "semantic": {
                                        "field": "inference_field",
                                        "query": "Can I use generative AI to identify user intent and improve search relevance?"
                                    }
                                }
                            }
                        },
                        {
                            "knn": {
                                "field": "vector",
                                "query_vector": [
                                    0.23,
                                    0.67,
                                    0.89
                                ],
                                "k": 3,
                                "num_candidates": 5
                            }
                        }
                    ],
                    "rank_window_size": 10,
                    "rank_constant": 1
                }
            },
            "field": "text",
            "inference_text": "LLM applications on production search applications",
            "inference_id": "my-reranker-model",
            "rank_window_size": 10
        }
    },
    "_source": [
        "text",
        "topic"
    ]
}
```

### Aggregations

Recall that with the rework we discussed, we rewrite a compound retriever to just a `RankDocsQuery` (i.e. a flattened explicitly ranked result list). This however does not block us from computing aggregations, as we also keep track of the source queries that were part of a compound retriever. This means that we can fallback to the nested `standard` retrievers below, to properly compute aggregations for the `topic` field, based on the union of the results of the two nested retrievers.

```
GET retrievers_example/_search
{
    "retriever": {
        "rrf": {
            "retrievers": [
                {
                    "standard": {
                        "query": {
                            "range": {
                                "year": {
                                    "gt": 2023
                                }
                            }
                        }
                    }
                },
                {
                    "standard": {
                        "query": {
                            "term": {
                                "topic": "elastic"
                            }
                        }
                    }
                }
            ],
            "rank_window_size": 10,
            "rank_constant": 1
        }
    },
    "_source": [
        "text",
        "topic"
    ],
    "aggs": {
        "topics": {
            "terms": {
                "field": "topic"
            }
        }
    }
}
```

So in the example above, we'll compute a `term` aggregation for the topic field, where **either** the `year` field is greater than 2023, or the document has the `topic` *elastic* associated with it.

### Collapsing

In addition to the aggregation option we discussed above, we can now also collapse results, as we'd do with a standard `query` request. In the following example, we compute the top 10 results of the `rrf` retriever, and then collapse them under the `year` field. The main difference with standard searches is that here we're collapsing **just** the top `rank_window_size` results, and not the ones within the nested retrievers.

```
GET /retrievers_example/_search
{
    "retriever": {
        "rrf": {
            "retrievers": [
                {
                    "text_similarity_reranker": {
                        "retriever": {
                            "standard": {
                                "query": {
                                    "term": {
                                        "topic": "ai"
                                    }
                                }
                            }
                        },
                        "field": "text",
                        "inference_text": "Can I use generative AI to identify user intent and improve search relevance?",
                        "rank_window_size": 10,
                        "inference_id": "my-reranker-model"
                    }
                },
                {
                    "knn": {
                        "field": "vector",
                        "query_vector":
                        [
                            0.23,
                            0.67,
                            0.89
                        ],
                        "k": 3,
                        "num_candidates": 5
                    }
                }
            ],
            "rank_window_size": 10,
            "rank_constant": 1
        }
    },
    "collapse": {
        "field": "year",
        "inner_hits": {
            "name": "year_results",
            "_source": [
                "text",
                "year"
            ]
        }
    },
    "_source": [
        "text",
        "topic"
    ]
}
```

### Pagination

As is also specified in the [docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html#_pagination_in_rrf) compound retrievers also support pagination. There is a significant difference with standard queries where, similarly to `collapse` above, the `rank_window_size` parameter is the whole result set upon which we can perform navigation. This means that if `from + size > rank_window_size` then we would bring no results back (but we'd still return aggregations).

```
GET /retrievers_example/_search
{
    "retriever": {
        "rrf": {
            "retrievers": [
                  {
                    "standard": {
                        "query": {
                            "term": {
                                "topic": "elastic"
                            }
                        }
                    }
                },
                {
                    "knn": {
                        "field": "vector",
                        "query_vector":
                        [
                            0.23,
                            0.67,
                            0.89
                        ],
                        "k": 3,
                        "num_candidates": 5
                    }
                }
            ],
            "rank_window_size": 10,
            "rank_constant": 1
        }
    },
    "from": 2,
    "size": 2
    "_source": [
        "text",
        "topic"
    ]
}
```

In the example above, we would compute the top 10 results (as defined in rrf's `rank_window_size`) from the combination of the two nested retrievers (`standard` and `knn`) and then we'd perform pagination by consulting the `from` and `size` parameters. So, in this case, we'd skip the first 2 results (`from`) and pick the next 2 (`size`).

Consider now a different scenario, where, in the same query above, we would instead have `from: 10` and `size: 2`. Given that `rank_window_size` is 10, and that these would be all the results that we can paginate upon, requesting to get 2 results after skipping the first 10 would fall outside of the navigatable result set, so we'd get back empty results. Additional examples and a more detailed break-down can also be found [in the documentation for the rrf retriever](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html#_pagination_in_rrf).

### Explain

We know that with great power comes great responsibility. Given that we can now combine retrievers in arbitrary ways, it could be rather difficult to understand why a result was eventually returned first, and how to optimize our retrieval strategy. For this very specific reason, we have worked to ensure that the `explain` output of a retriever request (i.e. by specifying `explain: true`) will convey all necessary information from all sub-retrievers, so that we can have a proper understanding of all the factors that contributed to the final ranking of a result. Taking the rather complex query in the `Collapsing` section, the explain for the first result looks like this:

```
{
    "_explanation":{
        "value": 0.8333334,
        "description": "sum of:",
        "details": [
            {
                "value": 0.8333334,
                "description": "rrf score: [0.8333334] computed for initial ranks [2, 1] with rankConstant: [1] as sum of [1 / (rank + rankConstant)] for each query",
                "details": [
                    {
                        "value": 2,
                        "description": "rrf score: [0.33333334], for rank [2] in query at index [0] computed as [1 / (2 + 1)], for matching query with score",
                        "details": [
                            {
                                "value": 0.0011925492,
                                "description": "text_similarity_reranker match using inference endpoint: [my-awesome-rerank-model] on document field: [text] matching on source query ",
                                "details": [
                                    {
                                        "value": 0.3844723,
                                        "description": "weight(topic:ai in 1) [PerFieldSimilarity], result of:",
                                        "details":
                                        [
                                            ...
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "value": 1,
                        "description": "rrf score: [0.5], for rank [1] in query at index [1] computed as [1 / (1 + 1)], for matching query with score",
                        "details":
                        [
                            {
                                "value": 1,
                                "description": "doc [1] with an original score of [1.0] is at rank [1] from the following source queries.",
                                "details":
                                [
                                    {
                                        "value": 1,
                                        "description": "found vector with calculated similarity: 1.0",
                                        "details":
                                        []
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }
}
```

Still a bit verbose, but it conveys all necessary information on why a document is at a specific position. For the top-level `rrf` retriever, we have 2 `details` specified, one for each of its nested retrievers. The first one is a `text_similarity_reranker` retriever, where we can see on explain the weight for the rerank operation, and the second one is a `knn` query informing us of the doc's computed similarity with the query vector. It might take a bit to familiarize with, but each retriever ensures to output all the information you might need to evaluate and optimize your search scenario!

## Conclusion

That's all for now! We hope you stayed with us until now and you enjoyed this topic! We're really excited with the release of the `retriever` framework and all the new use-cases that we can now support! Retrievers were built in order to support from very simple searches, to advanced RAG and hybrid search scenarios! As mentioned above, watch this space and more will be available soon!

### Frequently Asked Questions

#### What are retrievers in Elasticsearch?

Retrievers are a new abstraction layer added to the Search API in Elasticsearch that is now generally available. They offer the convenience of configuring multi-stage retrieval pipelines within a single `\_search` API call.

#### What queries can I generate with retrievers?

All base queries are accessible through the use of the `standard` retriever. In addition to that, one can use more fine-grained retrievers like `knn`, `rrf`, and `text\_similarity\_reranker` to either produce a set of results, or combine/rerank the results of another retriever.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt021070497c8cbd23/6a170aeab0367d782c72bd0e/c506a0f5c0a33ca6f85454d4f742d7cb266a7b78-715x413.png)

[Relevance](/search-labs/blog/category/relevance)

### ES|QL, you know, for Search - Introducing scoring and semantic search

April 16, 2025|[Ioana](/search-labs/author/ioana-alina-tagirta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter