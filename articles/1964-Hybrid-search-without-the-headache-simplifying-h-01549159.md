---
title: 'Hybrid search without the headache: simplifying hybrid search with retrievers'
company: Elastic
tag: 召回
date: 2025-11-27
url: https://www.elastic.co/search-labs/blog/hybrid-search-multi-field-query-retrievers-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Hybrid search without the headache: simplifying hybrid search with retrievers

Explore how to simplify hybrid search in Elasticsearch with a multi-field query format for linear and RRF retrievers, and create queries with no previous knowledge about your Elasticsearch index.

November 27, 2025

[Mike Pellegrini](/search-labs/author/mike-pellegrini)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

[Hybrid search](https://www.elastic.co/what-is/hybrid-search) is widely recognized as a powerful search approach, combining the precision and speed of [lexical search](https://www.elastic.co/search-labs/blog/lexical-and-semantic-search-with-elasticsearch#lexical-search---sparse-retrieval) with the natural language capabilities of [semantic search](https://www.elastic.co/what-is/semantic-search). However, applying it in practice can be tricky, often requiring deep knowledge about your index and the construction of verbose queries with non-trivial configurations. In this blog, we will explore how the [multi-field query format for linear and RRF retrievers](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers#multi-field-query-format) makes hybrid search simpler and more approachable, removing common headaches and enabling you to leverage its full power with greater ease. We will also review how the multi-field query format enables you to perform hybrid search queries with no previous knowledge about your index.

## The score range problem

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3521a6558cd477ca/6a17f174445de94d3c4d0225/c8b49153c47d2cdc233c0d2e440db04711d48ca5-1600x1600.jpg)

To set the stage, let’s review one of the primary reasons hybrid search can be hard: varying score ranges. Our old friend [BM25](https://www.elastic.co/elasticon/conf/2016/sf/improved-text-scoring-with-bm25) produces unbounded scores. In other words, BM25 can generate scores ranging from close to 0 to (theoretically) infinity. In contrast, queries against `dense_vector` fields will produce scores bounded between 0 and 1. Exacerbating this problem, `semantic_text` obfuscates the field type used to index embeddings, so unless you have detailed knowledge about your index and inference endpoint configuration, it can be hard to tell what the score range of your query will be. This presents a problem when trying to interleave lexical and semantic search results, as the lexical results may take precedence over the semantic ones even if the semantic results are more relevant. The generally accepted solution for this problem is to normalize the scores prior to interleaving results. Elasticsearch has two tools for this, the [linear](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/linear-retriever) and [RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rrf-retriever) retrievers.

![Comparison of search results with linear/rrf vs. without](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt09ed6bf3d25066bd/6a17f1750b0bedbd70dd3686/264481268c8b6ac259e3c257b85431b513f16672-1077x586.png)

The **RRF** retriever applies the [RRF algorithm](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion), using document rank as a measure of relevance and discarding the score. Since the score is not considered, score range mismatches are not an issue.

The **linear** retriever uses a linear combination to determine a document’s final score. This involves taking each component query’s score for the document, normalizing it, and summing them to generate the total score. Mathematically, the operation can be expressed as:

```
Total Score = 𝚺(N(Sx))
```

Where `N` is the normalization function, and SX is the score for query X. The normalization function is key here, as it transforms each query’s score to use the same range. You can learn more about the linear retriever [here](https://www.elastic.co/search-labs/blog/linear-retriever-hybrid-search).

## Breaking it down

Users can implement effective hybrid search with these tools, but it requires some knowledge about your index. Let’s take a look at an example with the linear retriever, where we will query an index with two fields:

```
PUT linear_retriever_example
{
  "mappings": {
    "properties": {
      "semantic_text_field": { <1>
        "type": "semantic_text",
        "inference_id": ".multilingual-e5-small-elasticsearch"
      },
      "text_field": { <2>
        "type": "text"
      }
    }
  }
}
```

1. `semantic_text_field` is a `semantic_text` field that uses [E5](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-e5), a text embedding model

2. `text_field` is a standard `text` field

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "retrievers": [
        {
          "retriever": {
            "standard": {
              "query": {
                "match": { <1>
                  "semantic_text_field": "foo"
                }
              }
            }
          },
          "normalizer": "minmax"
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "text_field": "foo"
                }
              }
            }
          },
          "normalizer": "minmax"
        }
      ]
    }
  }
}
```

1. We use a `match` query on our `semantic_text` field, which we [added support for in Elasticsearch 8.18/9.0](https://www.elastic.co/search-labs/blog/semantic-search-match-knn-sparse-vector#we-made-match-happen-in-semantic-search!)

When constructing the query, we need to keep in mind that `semantic_text_field` uses a text embedding model, so any queries on it will generate a score between 0 and 1. We also need to know that `text_field` is a standard `text` field, and therefore queries on it will generate an unbounded score. To create a result set with proper relevance, we need to use a retriever that will normalize the query scores before combining them. In this example, we use the linear retriever with `minmax` normalization, which normalizes each query’s score to a value between 0 and 1.

The query construction in this example is fairly straightforward because only two fields are involved. However, it can get complicated very quickly as more fields, and of varying types, are added. This demonstrates how writing an effective hybrid search query often requires deeper knowledge of the index being queried, so that component query scores are properly normalized prior to combination. This poses a barrier to the wider adoption of hybrid search.

### Query grouping

Let’s extend the example: What if we wanted to query one `text` field and two `semantic_text` fields? We could construct a query like this:

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "retrievers": [
        {
          "retriever": {
            "standard": {
              "query": {
                "semantic": {
                  "field": "semantic_text_field_1",
                  "query": "foo"
                }
              }
            }
          },
          "normalizer": "minmax"
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "semantic": {
                  "field": "semantic_text_field_2",
                  "query": "foo"
                }
              }
            }
          },
          "normalizer": "minmax"
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "text_field": "foo"
                }
              }
            }
          },
          "normalizer": "minmax"
        }
      ]
    }
  }
}
```

That seems good on its face, but there’s a potential problem. Now the `semantic_text` field matches make up ⅔ of the total score:

```
Total Score = N(semantic_text_field_1 score) + N(semantic_text_field_2 score) + N(text_field score)
```

This probably isn’t what you want because it creates an unbalanced score. The effects may not be that noticeable in an example like this one with only 3 fields, but it becomes problematic when more fields are queried. For instance, most indices contain far more lexical fields than semantic (i.e. `dense_vector`, `sparse_vector`, or `semantic_text`). What if we were querying an index with 9 lexical fields and 1 semantic field using the pattern above? The lexical matches would make up 90% of the score, blunting the effectiveness of semantic search.

A common way to address this is to group queries into lexical and semantic categories and weight the two evenly. This prevents either category from dominating the total score.

Let’s put that into practice. What would this grouped queries approach look like for this example when using the linear retriever?

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "retrievers": [
        {
          "retriever": {
            "linear": {
              "retrievers": [
                {
                  "retriever": {
                    "standard": {
                      "query": {
                        "semantic": {
                          "field": "semantic_text_field_1",
                          "query": "foo"
                        }
                      }
                    }
                  },
                  "normalizer": "minmax"
                },
                {
                  "retriever": {
                    "standard": {
                      "query": {
                        "semantic": {
                          "field": "semantic_text_field_2",
                          "query": "foo"
                        }
                      }
                    }
                  },
                  "normalizer": "minmax"
                }
              ]
            }
          },
          "normalizer": "minmax"
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "text_field": "foo"
                }
              }
            }
          },
          "normalizer": "minmax"
        }
      ]
    }
  }
}
```

Wow, this is getting verbose! You may have even needed to scroll up and down multiple times to examine the whole query! Here, we use two levels of normalization to create the query groups. Mathematically, it can be expressed as:

```
Total Score = N(N(semantic_text_field_1 score) + N(semantic_text_field_2 score)) + N(text_field score)
```

This second level of normalization ensures that the queries against the `semantic_text` fields and `text` field are weighted evenly. Note that we omit the second-level normalization for `text_field` in this example since there is only one lexical field, sparing you from *even more* verbosity.

This query structure is already unwieldy, and we’re only querying three fields. It becomes increasingly unmanageable, even for seasoned search practitioners, as you query more fields.

## The multi-field query format

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5d9007d279f0da29/6a17f17714d90c39cf79b6f5/dd04e1686076a574b717c1460acfe4eb79299208-1600x1600.jpg)

We added the [multi-field query format](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers#multi-field-query-format) for the linear and RRF retrievers in Elasticsearch 8.19, 9.1, and [serverless](https://www.elastic.co/cloud/serverless) to simplify all of this. You can now perform the same query as above with just:

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "fields": [ "semantic_text_field_1", "semantic_text_field_2", "text_field" ],
      "query": "foo",
      "normalizer": "minmax"
    }
  }
}
```

Which shrinks the query from 55 lines to just 9! Elasticsearch automatically uses the index mappings to:

* Determine the type of each field queried
* Group each field into a lexical or semantic category
* Weight each category evenly in the final score

This allows anyone to execute an effective hybrid search query without needing to know details about the index or the inference endpoints used.

When using RRF, you can omit the `normalizer`, since rank is used as a proxy for relevance:

```
GET rrf_retriever_example/_search
{
  "retriever": {
    "rrf": {
      "fields": [ "semantic_text_field_1", "semantic_text_field_2", "text_field" ],
      "query": "foo"
    }
  }
}
```

## Per-field boosting

When using the linear retriever, you can apply a per-field boost to adjust the importance of matches in certain fields. For example, let’s say you’re querying four fields: two `semantic_text` fields and two `text` fields:

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "fields": [ "semantic_text_field_1", "semantic_text_field_2", "text_field_1", "text_field_2" ],
      "query": "foo",
      "normalizer": "minmax"
    }
  }
}
```

By default, each field is weighted equally in its group (lexical or semantic). The score breakdown looks like:

![Comparison of query groups and field scores](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdc6e197e5ff7b68d/6a17f179505ac32834ad8c46/ba31c76189e3a1e5b1638437ccf0528aafec2598-1600x549.png)

In other words, each field is 25% of the total score.

We can use the `field^boost` syntax to add a per-field boost to any field. Let’s apply a boost of 2 to `semantic_text_field_1` and `text_field_1`:

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "fields": [ "semantic_text_field_1^2", "semantic_text_field_2", "text_field_1^2", "text_field_2" ]
      "query": "foo",
      "normalizer": "minmax"
    }
  }
}
```

Now the score breakdown looks like:

![Changed field weight with ref and hybrid search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltccc9ed7d6e865a5e/6a17f17abe6086a31d004882/de20e555d52f914bf483a048d056f54f4fece757-1600x549.png)

Each query group is still weighted equally, but now the field weight within the groups has changed:

* `semantic_text_field_1` is 66% of the semantic query group score, 33% of the total score
* `text_field_1` is 66% of the lexical query group score, 33% of the total score

| ℹ️ Note that the total score range will not change when a per-field boost is applied. This is an intended side-effect of score normalization, which ensures that lexical and semantic query scores remain directly comparable with each other. |
| --- |
| ℹ️ Per-field boosting can also be used with the RRF retriever in Elasticsearch 9.2+ |

### Wildcard resolution

You can use the `*` wildcard in the `fields` parameter to match multiple fields. Continuing the example above, this query is functionally equivalent to querying s`emantic_text_field_1`, `semantic_text_field_2`, and `text_field_1` explicitly:

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "fields": [ "semantic_text_field_*", "*_field_1" ],
      "query": "foo",
      "normalizer": "minmax"
    }
  }
}
```

It’s interesting to note that the `*_field_1` pattern matches both `text_field_1` and `semantic_text_field_1`. This is handled automatically; the query will execute as if each of the fields were explicitly queried. It’s also fine that the `semantic_text_field_1` matches both patterns; all field name matches are de-duplicated before query execution.

You can use the wildcard in a variety of ways:

* Prefix matching (ex: `*_text_field`)
* Inline matching (ex: `semantic_*_field`)
* Suffix matching (ex: `semantic_text_field_*`)

You can also use multiple wildcards to apply a combination of the above, such as `*_text_field_*`.

### Default query fields

The multi-field query format also allows you to query an index you know nothing about. If you omit the `fields` parameter, it will query all fields specified by the [index.query.default\_field index setting](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules):

```
GET linear_retriever_example/_search
{
  "retriever": {
    "linear": {
      "query": "foo",
      "normalizer": "minmax"
    }
  }
}
```

By default, `index.query.default_field` is set to `*`. This wildcard will resolve to every field type in the index that supports term queries, which is most. The exceptions are:

* `dense_vector` fields
* `rank_vector` fields
* Geometry fields: `geo_point`, `shape`

This functionality is especially useful when you want to perform a hybrid search query on an index provided by a third party. The multi-field query format allows you to execute an appropriate query in a simple way. Just exclude the `fields` parameter, and all applicable fields will be queried.

## Conclusion

The score range problem can make effective hybrid search a headache to implement, particularly when there’s limited insight into the index being queried or the inference endpoints in use. The multi-field query format for the linear and RRF retrievers alleviates this pain by packaging an automated, query-grouping-based hybrid search approach into a simple and approachable API. Additional functionality, such as per-field boosting, wildcard resolution, and default query fields, extends the functionality to cover many use cases.

## Try out the multi-field query format today

You can check out the linear and RRF retrievers with the multi-field query format in fully managed Elasticsearch [Serverless](https://www.elastic.co/cloud/serverless) projects with a [free trial](https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/create-serverless-project). It’s also available in stack versions starting from 8.19 & 9.1.

Get started in minutes on your local environment with a single command:

```
curl -fsSL https://elastic.co/start-local | sh
```

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9dd95ca3f3bd2004/6a17f8153e9e457308ba165d/69d9c14dac7e255e3df6c3aa15c84ac6564c3401-720x420.jpg)

[Hybrid Search](/search-labs/blog/category/hybrid-search)

### Built with Elastic: Hybrid search for Cypris – the world’s largest innovation database

May 06, 2025|[Elastic Team](/search-labs/author/the-elastic-team)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt37c9d2971b5a2db3/6a170a75cf4f254223b2d149/492c9b5432a2b9e40cebb3b60f0df019a8c7bf6d-1280x720.png)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Vector Database](/search-labs/blog/category/vector-database)

### How to measure and improve Elasticsearch search recall: from 0.43 to 0.75 with hybrid search

May 04, 2026|[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt63218799e944e16d/6a1710ef6f7f04ee68914952/93d8e0d84fb4cfbf5e51df85df7ec2e600d9dcc7-1088x607.png)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Integrations](/search-labs/blog/category/integrations)[Java](/search-labs/blog/category/java-programming)

### Hybrid search with Java: LangChain4j Elasticsearch integration

March 11, 2026|[Laura Trotta](/search-labs/author/laura-trotta)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter