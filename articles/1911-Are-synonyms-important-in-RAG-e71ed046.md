---
title: 'Are synonyms important in RAG?'
company: Elastic
tag: RAG
date: 2025-02-11
url: https://www.elastic.co/search-labs/blog/synonyms-in-rag-genai
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Are synonyms important in RAG?

Exploring the functionality of Elasticsearch synonyms in a Retrieval Augmented Generation (RAG) application.

February 11, 2025

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)[Tomás Murúa](/search-labs/author/tomas-murua)

[AI](/search-labs/blog/category/ai)

Jump to

Share

Synonyms allow us to search in our documents using different words that have the same meaning to ensure that users find what they were looking for regardless of the exact word they used. You would think that since RAG applications use semantic/vector search, part of the semantic functionality would be already covered by synonyms (since by definition, synonyms are semantically related words).

Is that true? Does semantic search truly replace synonyms? In this article, we'll analyze the impact of using synonyms in a RAG application.

## Steps

1. [Configure the Endpoint](https://www.elastic.co/search-labs/blog/synonyms-in rag-genai#configure-the-inference-endpoint)
2. [Configure synonyms](https://www.elastic.co/search-labs/blog/synonyms-in rag-genai#configure-synonyms)
3. [Index documents](https://www.elastic.co/search-labs/blog/synonyms-in rag-genai#index-documents)
4. [Semantic search](https://www.elastic.co/search-labs/blog/synonyms-in rag-genai#semantic-search)
5. [Synonyms and RAG](https://www.elastic.co/search-labs/blog/synonyms-in rag-genai#synonyms-and-rag)

## Configure the Inference Endpoint

For this example, we'll implement a [RAG](https://www.elastic.co/what-is/retrieval-augmented-generation) (Retrieval-Augmented Generation) system with and without synonyms in a HR context. We'll index different documents with variations of the term PTO (Paid Time Off), like "vacation" or "holiday". We'll then configure synonyms to show how these relationships improve relevance and accuracy in search.

First, let's create an endpoint using the [ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html) model with the [inference api](https://www.elastic.co/guide/en/elasticsearch/reference/current/put-inference-api.html) by running the following commands in [Kibana DevTools](https://www.elastic.co/guide/en/kibana/current/devtools-kibana.html):

```
PUT _inference/sparse_embedding/code-wave_inference
{
  "service": "elasticsearch",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}
```

## Configure synonyms

### What are synonyms in Elasticsearch?

In Elasticsearch, [synonyms](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-with-synonyms.html) are words or phrases with the same or similar meaning stored as synonym sets that can be managed as [files](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-with-synonyms.html#synonyms-store-synonyms-file) or via [API](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-with-synonyms.html#synonyms-store-synonyms-api). They allow users to find relevant information, even if they use different terms to refer to the same concept.

So, for example, if we create a set of synonyms where "holiday" and "vacation" are synonyms of "Paid Time Off" when an employee searches for either of those words, they will find the related documents to all of them.

You can read more about them in this [article](https://www.elastic.co/search-labs/blog/phrase-synonyms-api).

Let's create a set of synonyms using the [synonyms API:](https://www.elastic.co/guide/en/elasticsearch/reference/current/put-synonyms-set.html)

```
PUT _synonyms/code-wave_synonyms
{
  "synonyms_set": [
    {
      "synonyms": "holidays, paid time off"
    }
  ]
}
```

*It's important to note that the set of synonyms must be configured before it can be applied to an index.*

Now, let's define the settings and mappings for our data:

```
PUT /code-wave_index
{
  "settings": {
    "analysis": {
      "filter": {
        "synonyms_filter": {
          "type": "synonym_graph",
          "synonyms_set": "code-wave_synonyms",
          "updateable": true
        }
      },
      "analyzer": {
        "my_search_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "synonyms_filter"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "text_field": {
        "type": "text",
        "analyzer": "standard",
        "copy_to": "semantic_field",
        "fields": {
          "synonyms": {
            "type": "text",
            "analyzer": "standard",
            "search_analyzer": "my_search_analyzer"
          }
        }
      },
      "semantic_field": {
        "type": "semantic_text",
        "inference_id": "code-wave_inference"
      }
    }
  }
}
```

We'll use the [semantic\_text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html#:~:text=The%20semantic_text%20field%20type%20specifies,semantic%20search%20on%20your%20data.) field to do semantic search and the [synonyms graph token filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-synonym-graph-tokenfilter.html) to handle multiword synonyms.

We also created both a `text_field`.synonym version and a `text_field` version of the field for more control on how we query the field with, or without considering the synonyms.

Finally, we use copy\_to to copy the value of text\_field to the semantic\_text version of the field to enable both full-text and semantic queries.

## Index documents

We will now index our documents using the [`bulk API`](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html):

```
POST _bulk
{"index":{"_index":"code-wave_index","_id":"1"}}
{"semantic_field":"Paid time off: All employees receive 20 days of paid vacation annually, with additional days earned for tenure milestones.","text_field":"Paid time off: All employees receive 20 days of paid vacation annually, with additional days earned for tenure milestones."}
{"index":{"_index":"code-wave_index","_id":"2"}}
{"semantic_field":"Holidays: Paid public holidays recognized each calendar year.","text_field":"Holidays: Paid public holidays recognized each calendar year."}
{"index":{"_index":"code-wave_index","_id":"3"}}
{"semantic_field":"Sick leave: Paid sick leave of up to 15 days per year.","text_field":"Sick leave: Paid sick leave of up to 15 days per year."}
{"index":{"_index":"code-wave_index","_id":"4"}}
{"semantic_field":"Holidays sale: Enjoy discounts up to 50% during our exclusive holidays sale event!","text_field":"Holidays sale: Enjoy discounts up to 50% during our exclusive holidays sale event!"}
{"index":{"_index":"code-wave_index","_id":"5"}}
{"semantic_field":"Holidays recipes: Try our top 10 holidays dessert recipes, perfect for family gatherings and celebrations.","text_field":"Holidays recipes: Try our top 10 holidays dessert recipes, perfect for family gatherings and celebrations."}
{"index":{"_index":"code-wave_index","_id":"6"}}
{"semantic_field":"Holidays travel: Find the best deals for your holidays flights and accommodations this season.","text_field":"Holidays travel: Find the best deals for your holidays flights and accommodations this season."}
{"index":{"_index":"code-wave_index","_id":"7"}}
{"semantic_field":"Holidays music: Stream your favorite holidays classics and discover new seasonal hits.","text_field":"Holidays music: Stream your favorite holidays classics and discover new seasonal hits."}
{"index":{"_index":"code-wave_index","_id":"8"}}
{"semantic_field":"Holidays decorations: Our store offers a wide range of holidays decorations to make your home festive.","text_field":"Holidays decorations: Our store offers a wide range of holidays decorations to make your home festive."}
{"index":{"_index":"code-wave_index","_id":"9"}}
{"semantic_field":"Holidays movies: Check out our list of must-watch holidays movies for cozy winter nights.","text_field":"Holidays movies: Check out our list of must-watch holidays movies for cozy winter nights."}
{"index":{"_index":"code-wave_index","_id":"10"}}
{"semantic_field":"Holidays festival: Join us at the city's annual holidays festival featuring lights, music, and local food.","text_field":"Holidays festival: Join us at the city's annual holidays festival featuring lights, music, and local food."}
{"index":{"_index":"code-wave_index","_id":"11"}}
{"semantic_field":"Holidays weather: Stay updated with our holidays weather forecast to plan your activities.","text_field":"Holidays weather: Stay updated with our holidays weather forecast to plan your activities."}
{"index":{"_index":"code-wave_index","_id":"12"}}
{"semantic_field":"Holidays gift guide: Browse our ultimate holidays gift guide for everyone on your list.","text_field":"Holidays gift guide: Browse our ultimate holidays gift guide for everyone on your list."}
{"index":{"_index":"code-wave_index","_id":"13"}}
{"semantic_field":"Holidays traditions: Explore unique holidays traditions celebrated around the world.","text_field":"Holidays traditions: Explore unique holidays traditions celebrated around the world."}
```

We are now ready to start searching! But first, let's make sure that synonyms are working by searching for holidays

```
GET code-wave_index/_search
{
  "_source": {
    "excludes": [
      "*embeddings",
      "*chunks"
    ]
  },
  "query": {
    "multi_match": {
      "query": "holidays",
      "fields": [
        "text_field^10",
        "text_field.synonyms^0.6"
      ]
    }
  }
}
```

*We adjust boosts so synonyms score lower than original words.*

Check the response:

```
{
  "took": 3,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 12,
      "relation": "eq"
    },
    "max_score": 5.2014494,
    "hits": [
      {
        "_index": "code-wave_index",
        "_id": "2",
        "_score": 3.0596757,
        "_source": {
          "text_field": "Holidays: Paid public holidays recognized each calendar year.",
          "semantic_field": {
            "inference": {
              "inference_id": "code-wave_inference",
              "model_settings": {
                "task_type": "sparse_embedding"
              }
            },
            "text": "Holidays: Paid public holidays recognized each calendar year."
          }
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "1",
        "_score": 3.023004,
        "_source": {
          "text_field": "Paid time off: All employees receive 20 days of paid vacation annually, with additional days earned for tenure milestones.",
          "semantic_field": {
            "inference": {
              "inference_id": "code-wave_inference",
              "model_settings": {
                "task_type": "sparse_embedding"
              }
            },
            "text": "Paid time off: All employees receive 20 days of paid vacation annually, with additional days earned for tenure milestones."
          }
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "13",
        "_score": 2.9230676,
        "_source": {
          "text_field": "Holidays traditions: Explore unique holidays traditions celebrated around the world.",
          "semantic_field": {
            "inference": {
              "inference_id": "code-wave_inference",
              "model_settings": {
                "task_type": "sparse_embedding"
              }
            },
            "text": "Holidays traditions: Explore unique holidays traditions celebrated around the world."
          }
        }
      },
      ...
    ]
  }
}
```

As we can see, when we searched for "holidays", the second document has the synonym: "Paid Time Off".

## Semantic Search

[Semantic search](https://www.elastic.co/what-is/semantic-search/) interprets the meaning of words and phrases instead of just considering text matches. Unlike synonyms, which depend on pre-defined words, semantic search uses language models to interpret queries and documents on a deeper level.

While we could return the results we need by running a semantic search, we'll see that by using synonyms, relevant results will rank higher, thus allowing us to send fewer docs to the LLM, improving results and lowering costs.

```
GET code-wave_index/_search
{
  "_source": {
    "excludes": [
      "*embeddings",
      "*chunks"
    ]
  },
  "query": {
    "semantic": {
      "field": "semantic_field",
      "query": "holidays"
    }
  }
}
```

Response:

```
{
  "took": 9,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 13,
      "relation": "eq"
    },
    "max_score": 13.515395,
    "hits": [
      {
        "_index": "code-wave_index",
        "_id": "10",
        "_score": 13.515395,
        "_source": {
          "text_field": "Holidays festival: Join us at the city's annual holidays festival featuring lights, music, and local food.",
          "semantic_field": {
            "inference": {
              "inference_id": "code-wave_inference",
              "model_settings": {
                "task_type": "sparse_embedding"
              }
            },
            "text": "Holidays festival: Join us at the city's annual holidays festival featuring lights, music, and local food."
          }
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "7",
        "_score": 11.913458,
        "_source": {
          "text_field": "Holidays music: Stream your favorite holidays classics and discover new seasonal hits.",
          "semantic_field": {
            "inference": {
              "inference_id": "code-wave_inference",
              "model_settings": {
                "task_type": "sparse_embedding"
              }
            },
            "text": "Holidays music: Stream your favorite holidays classics and discover new seasonal hits."
          }
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "6",
        "_score": 11.650193,
        "_source": {
          "text_field": "Holidays travel: Find the best deals for your holidays flights and accommodations this season.",
          "semantic_field": {
            "inference": {
              "inference_id": "code-wave_inference",
              "model_settings": {
                "task_type": "sparse_embedding"
              }
            },
            "text": "Holidays travel: Find the best deals for your holidays flights and accommodations this season."
          }
        }
      },
      ...
    ]
  }
}
```

When using semantic search, the documents that are relevant for the query do not come in the first positions since the dataset includes the term "holidays" in contexts unrelated to "Paid time off".

## Hybrid Search

Hybrid search gives us the ability to combine the results of both full-text and semantic search queries into one, normalized result set by using [RRF (Reciprocal Rank Fusion)](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) to balance the scores from different retrievers.

```
GET code-wave_index/_search
{
  "_source": "text_field",
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "nested": {
                "path": "semantic_field.inference.chunks",
                "query": {
                  "sparse_vector": {
                    "inference_id": "code-wave_inference",
                    "field": "semantic_field.inference.chunks.embeddings",
                    "query": "holidays"
                  }
                }
              }
            }
          }
        },
        {
          "standard": {
            "query": {
              "multi_match": {
                "query": "holidays",
                "fields": [
                  "text_field.synonyms"
                ]
              }
            }
          }
        }
      ]
    }
  }
}
```

Response:

```
{
  "took": 11,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 13,
      "relation": "eq"
    },
    "max_score": 0.03175403,
    "hits": [
      {
        "_index": "code-wave_index",
        "_id": "7",
        "_score": 0.03175403,
        "_source": {
          "text_field": "Holidays music: Stream your favorite holidays classics and discover new seasonal hits."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "13",
        "_score": 0.031257633,
        "_source": {
          "text_field": "Holidays traditions: Explore unique holidays traditions celebrated around the world."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "4",
        "_score": 0.031009614,
        "_source": {
          "text_field": "Holidays sale: Enjoy discounts up to 50% during our exclusive holidays sale event!"
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "2",
        "_score": 0.030834913,
        "_source": {
          "text_field": "Holidays: Paid public holidays recognized each calendar year."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "6",
        "_score": 0.03079839,
        "_source": {
          "text_field": "Holidays travel: Find the best deals for your holidays flights and accommodations this season."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "11",
        "_score": 0.02964427,
        "_source": {
          "text_field": "Holidays weather: Stay updated with our holidays weather forecast to plan your activities."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "5",
        "_score": 0.029418126,
        "_source": {
          "text_field": "Holidays recipes: Try our top 10 holidays dessert recipes, perfect for family gatherings and celebrations."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "12",
        "_score": 0.028991597,
        "_source": {
          "text_field": "Holidays gift guide: Browse our ultimate holidays gift guide for everyone on your list."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "1",
        "_score": 0.016393442,
        "_source": {
          "text_field": "Paid time off: All employees receive 20 days of paid vacation annually, with additional days earned for tenure milestones."
        }
      },
      {
        "_index": "code-wave_index",
        "_id": "10",
        "_score": 0.016393442,
        "_source": {
          "text_field": "Holidays festival: Join us at the city's annual holidays festival featuring lights, music, and local food."
        }
      }
    ]
  }
}
```

This query will return both semantic and text related documents.

## Synonyms and RAG

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd91f829e5488a468/6a17de096317302b3f58599b/7ff060ae7e469d8422a0b9e579ef09abe21145ce-1236x835.png)

In this section, we'll evaluate how synonyms and semantic search improve queries in a RAG system. We'll use a common question about days off for this example:

**"How many vacation days are provided for holidays?"**

For this question, we're interested in the information in document 1. Document 2 is closer to the result that we want, but it's not precise. We'll get this result when we search with no synonyms. Let't take a look a their content:

* [1] **Paid time off**: All employees receive 20 days of paid vacation annually, with additional days earned for tenure milestones.
* [2] **Holidays**: Paid public holidays recognized each calendar year.

Both documents include information related to days off but only document 2 uses specifically the term "holidays" so we can test how synonyms and semantic search work in Playground.

You can access Playground from **Search>Playground**. From there, you need to configure the LLM you want to use and select the index we've already created to be sent as context. You can read more about Playground and its configuration [here](https://www.elastic.co/search-labs/blog/rag-playground-introduction)

Once Playground has been configured, if we click the query button, we can see that synonyms are deactivated:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt25f47effaf050de5/6a17de0b6864a495a5b6867e/4371d417661485d0047ba3a165403c9cb9b1a99b-1553x894.png)

For each question, we'll send the first three hits of the previous query to the LLM, as context:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf26d7c1aa3711e8c/6a17de0c505ac3233fad8a1d/8325d3bb7a2350906a13488fc66d45f2dfbc25c4-534x314.png)

Now, let's ask the question to Playground and check the results with synonyms deactivated:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8abefe6e001be04d/6a17de0e6df731a3050a0df3/b3fe68c2f4809f937a6f3bfa7b6286837068768f-1057x773.png)

Since the document specifying the amount of holidays employees get a year is not among the first three hits, the LLM cannot answer the question. In this case, the closest result is in document [2].

*Note: By clicking on "Snippet", we can see the specific content in Elasticsearch from where the answer comes.*

Let's clean up the chat, activate synonyms and ask the same question again:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3956a1e535daafb0/6a17de0f3e9e452558ba136f/c5192fe6acd32bd61c820e55a2f5f6352671b4fd-468x331.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc6c3b2164a6ffa3a/6a17de10ec0f8967d15a6524/ee3c9cc1d4dd0d039f9ff6a9c2fc3638c4ccb4f1-602x477.png)

*Note that when you enable a semantic\_text field, and a text field, Playground will automatically generate a* [*hybrid search query*](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text-hybrid-search.html)*:*

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt50fc6f20fb09732b/6a17de12abe0f22a6fdfe905/2ca7ee57002a0ea6b0a620a146dc9fe351b14379-870x928.png)

Let’s repeat the question, now with synonyms activated:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt332789321f2fbc4e/6a17de133e03d77a4e4f2b70/b71833914cfb01740ca6f5a3668cbf69a39c62c8-1055x763.png)

Now, the answer does include the document we were searching for, since the synonym allowed for document [1] to be sent to the LLM.

## Conclusion

In this article, we discovered that synonyms are a fundamental part of search systems, even when using semantic search since it does not necessarily cover the synonym functionality.

Synonyms allow us to control which documents we want to boost based on our use case, improving accuracy by tuning relevance. Semantic search, on the other hand, is useful for [**recall**](https://www.elastic.co/what-is/search-relevance), meaning it introduces potentially relevant results without us having to add synonyms for every related term.

With Hybrid search we can do synonyms and semantic search at the same time, bringing the best of the two worlds. With Playground, if we select as search fields a combination of semantic, and text fields, a hybrid query will be built automatically for us.

### Frequently Asked Questions

#### What are synonyms in Elasticsearch?

In Elasticsearch, synonyms are words or phrases with the same or similar meaning stored as synonym sets that can be managed as files or via API.

#### Why are synonyms in Elasticsearch important?

Synonyms in Elasticsearch allow users to find relevant information, even if they use different terms to refer to the same concept.

#### How does semantic search differ from using synonyms in Elasticsearch?

Unlike synonyms, which depend on pre-defined words, semantic search uses language models to interpret queries and documents on a deeper level.

#### Do RAG apps still need synonyms?

Yes, synonyms are a fundamental part of search systems, even when using semantic search since it does not necessarily cover the synonym functionality.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter