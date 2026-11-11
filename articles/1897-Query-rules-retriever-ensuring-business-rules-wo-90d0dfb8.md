---
title: 'Query rules retriever: ensuring business rules work seamlessly with semantic search'
company: Elastic
tag: 排序
date: 2024-12-19
url: https://www.elastic.co/search-labs/blog/semantic-search-query-rules
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Query rules retriever: ensuring business rules work seamlessly with semantic search

Harness the power of Elasticsearch query rules combined with semantic search and rerankeras.

December 19, 2024

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

Did you know that [query rules](https://www.elastic.co/search-labs/blog/elasticsearch-query-rules-generally-available) work seamlessly with semantic search? With query rules as a [retriever](https://www.elastic.co/search-labs/blog/elasticsearch-retrievers-ga-8.16.0), it’s never been easier to combine semantic search and complex logic such as [RRF](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) or [semantic reranking](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-reranking.html) with the power of query rules.

Query rules are an important [tool in our relevance toolbox](https://www.elastic.co/search-labs/blog/search-relevance-tuning-in-semantic-search),

## Introducing the query rules retriever

The [rule retriever](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#:~:text=Query%20Rules%20Retriever&text=The%20rule%20retriever%20enables%20fine,the%20box%20with%20other%20retrievers.) is what’s known as a compound retriever, which allows chaining complex behavior in a retriever tree where the order of operation matters.

Like the [rule query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-rule-query.html), the rule retriever works on already-defined query rulesets. You can create a ruleset using the [query rules CRUD API](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-rules-apis.html).

What does this look like in practice? Here’s an example of a simple query ruleset, that pins a document with the id `id1` when the `query_string` parameter matches `puggles`:

```
PUT /_query_rules/my-ruleset
{
  "rules": [
    {
      "rule_id": "rule1",
      "type": "pinned",
      "criteria": [
        {
          "type": "exact",
          "metadata": "query_string",
          "values": [ "puggles" ]
        }
      ],
      "actions": {
        "ids": [
          "id1"
        ]
      }
    }
  ]
}
```

Next, here is a simple example of a rule retriever that will match on this ruleset:

```
POST my-index/_search
{
  "retriever": {
    "rule": {
      "match_criteria": {
        "query_string": "puggles"
      },
      "ruleset_ids": [
        "my-ruleset"
      ],
      "retriever": {
        "standard": {
          "query": {
            "query_string": {
              "query": "puggles"
            }
          }
        }
      }
    }
  }
}
```

In this case, we’re simply defining a standard sub-retriever that’s a simple `query_string` query. This is very similar to how the rule query works today by specifying an organic query. The retriever will return a list of search results with matching rule(s) applied.

## Semantic search and query rules

The simple example doesn’t show the true power of query rules: applying business rules on top of semantic search. This can help to return results important to promotional campaigns or simply “fix” specific queries where semantic search doesn’t return the results we want.

We can use the same retriever framework to perform query rules using semantic search by specifying these queries under the defined standard retriever. Here is an example using the `semantic` query:

```
POST my-index/_search
{
  "retriever": {
    "rule": {
      "match_criteria": {
        "query_string": "puggles"
      },
      "ruleset_ids": [ "my-ruleset" ],
      "retriever": {
        "standard": {
          "query": {
            "semantic": {
              "field": "semantic_field",
              "query": "what is the best pug mix?"
            }
          }
        }
      }
    }
  }
}
```

Similarly, `sparse_vector` and knn queries will seamlessly work when defined as `standard` retrievers with the query rules retriever.

## Reranking and query rules

You can combine RRF with query rules by nesting the rrf retriever under the `rule` retriever, for example:

```
POST my-index/_search
{
  "retriever": {
    "rule": {
      "match_criteria": {
        "query_string": "puggles"
      },
      "ruleset_ids": [
        "my-ruleset"
      ],
      "retriever": {
        "rrf": {
          "retrievers": [
            {
              "standard": {
                "query": {
                  "semantic": {
                    "field": "semantic_field",
                    "query": "what is the best pug mix?"
                  }
                }
              }
            },
            {
              "standard": {
                "query": {
                  "query_string": {
                    "query": "puggles"
                  }
                }
              }
            }
          ]
        }
      }
    }
  }
}
```

**Important note:** Order is important here. While technically there’s nothing stopping you from running RRF on top of the rule retriever, this will not work as intended due to the order of operations in the retriever tree. When you’re running a rule retriever, in order to ensure that all of the rules are applied as intended, the rule retriever must always be the outermost/top level retriever.

Similarly, you can combine query rules with [semantic reranking](https://www.elastic.co/search-labs/blog/semantic-reranking-with-retrievers). Here’s an example using our [Elastic reranker](https://www.elastic.co/search-labs/blog/elastic-semantic-reranker-part-2):

```
POST my-index/_search
{
  "retriever": {
    "rule": {
      "match_criteria": {
        "query_string": "puggles"
      },
      "ruleset_ids": [ "my-ruleset" ],
      "retriever": {
        "text_similarity_reranker": {
          "retriever": {
            "standard": {
              "query": {
                "semantic": {
                  "field": "semantic_field",
                  "query": "what is the best pug mix?"
                }
              }
            }
          }
        }
      },
      "field": "text_field",
      "inference_id": "elastic-rerank-endpoint",
      "inference_text": "what is the best pug mix?"
    }
  }
}
```

Bringing it all together, here’s an example of how you could combine semantic, `sparse_vector`, `knn` and `lexical text` search queries together with RRF and semantic reranking, and apply query rules on top of them:

```
POST my-index/_search
{
  "retriever": {
    "rule": {
      "match_criteria": {
        "query_string": "puggles"
      },
      "ruleset_ids": [ "my-ruleset" ],
      "retriever": {
        "text_similarity_reranker": {
          "retriever": {
            "rrf": {
              "retrievers": [
                {
                  "standard": {
                    "query": {
                      "sparse_vector": {
                        "field": "sparse_field",
                        "inference_id": "elser-endpoint",
                        "query": "what is the best pug mix?"
                      }
                    }
                  }
                },
                {
                  "standard": {
                    "query": {
                      "knn": {
                        "field": "dense_field",
                        "query_vector": [ 1, 2, 3 ],
                        "k": 10,
                        "num_candidates": 100
                      }
                    }
                  }
                },
                {
                  "standard": {
                    "query": {
                      "semantic": {
                        "field": "semantic_field",
                        "query": "what is the best pug mix?"
                      }
                    }
                  }
                },
                {
                  "standard": {
                    "query": {
                      "query_string": {
                        "query": "puggles"
                      }
                    }
                  }
                }
              ]
            }
          },
          "field": "text_field",
          "inference_id": "elastic-rerank-endpoint",
          "inference_text": "what is the best pug mix?"
        }
      }
    }
  }
}
```

## Combining rule types

Query rules aren’t just for pinned documents anymore! In Elasticsearch 8.16 we introduced a new rule type, exclude. This allows you to specify documents that you never want to be returned in search results, as well as documents you want to pin at the top of search results.

Use cases for the `exclude` rule include but are not limited to:

* Fixing relevance issues in specific queries by removing results that aren’t helpful or relevant to the query
* Suppressing results temporarily that we don’t want to be returned in any search results until a certain time

Here’s an example of a query ruleset that includes both pinned and excluded rules:

```
PUT /_query_rules/my-ruleset
{
  "rules": [
    {
      "rule_id": "rule1",
      "type": "pinned",
      "criteria": [
        {
          "type": "exact",
          "metadata": "query_string",
          "values": [ "puggles" ]
        }
      ],
      "actions": {
        "ids": [
          "id1"
        ]
      }
    },
    {
      "rule_id": "rule2",
      "type": "exclude",
      "criteria": [
        {
          "type": "exact",
          "metadata": "query_string",
          "values": [ "chiweenies" ]
        }
      ],
      "actions": {
        "ids": [
          "id2"
        ]
      }
    }
  ]
}
```

Rules are applied based on match criteria, so it’s possible for a rule retriever to match on both pinned and excluded documents in the same query.

## Try the rule retriever

The `rule` retriever is exceptionally powerful when combined with semantic search and reranking strategies, because it offers fine-tuned control over search results while harnessing the power of semantic search. The rule retriever is already available in our Serverless offering, and will be available for Stack versions starting with 8.17.0.

### Frequently Asked Questions

#### What is the Elasticsearch rule retriever?

The rule retriever is what’s known as a compound retriever, which allows chaining complex behavior in a retriever tree where the order of operation matters.

#### How does the Elasticsearch rule retriever works?

The rule retriever works on already-defined query rulesets. You can create a ruleset using the query rules CRUD API.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltfda2c7552964efff/6a17dae2414c645751945044/163a44a0624ac49829c1b5354b0e086eb0bb7a1f-1440x611.png)

[Relevance](/search-labs/blog/category/relevance)

### Elasticsearch query rules are now generally available

August 07, 2024|[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt8149e645cdc1af4e/6a17d9e65772622d351bcab7/64e585a13613e2651a18ede0b33fe61a352236d5-1440x823.png)

[Vector Database](/search-labs/blog/category/vector-database)

### Search relevance tuning: Balancing keyword and semantic search

May 14, 2024|[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd5f935ec07d28af8/6a16f67492262a11531cc073/8ee49ace3a113391f6119c7073380df0975dbda6-1535x873.png)

[Relevance](/search-labs/blog/category/relevance)

### Elasticsearch retrievers architecture and use-cases

November 14, 2024|[Panagiotis Bailis](/search-labs/author/panagiotis-bailis)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2b7ae90507a090a1/6a17ddd67f6f15de08c09a17/a5fa1c6e672b31a91fc37afa3f84421f1e61f270-1440x807.png)

[Vector Database](/search-labs/blog/category/vector-database)[Python](/search-labs/blog/category/python-programming)

### Introducing Retrievers - Search All the Things!

May 28, 2024|[Jeff Vestal](/search-labs/author/jeff-vestal)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltefa610e8ab16fa93/6a17d9f35772629a711bcabf/186bba85ce0100d806d7b39740ae8045ceda22b5-720x420.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)

### Semantic reranking in Elasticsearch with retrievers

May 28, 2024|[Adam Demjen](/search-labs/author/adam-demjen)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter