---
title: 'Retrieval of originating information in multi-vector documents'
company: Elastic
tag: 召回
date: 2024-05-10
url: https://www.elastic.co/search-labs/blog/multi-vector-documents
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Retrieval of originating information in multi-vector documents

Learn about multi-vector documents in Elasticsearch, their use cases, and how to link original context to a multi-vector document.

May 10, 2024

[Gilad Gal](/search-labs/author/gilad-gal)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

## Introduction

Elasticsearch (from 8.11 releases and later) supports having multiple vectors per document within a single field. Such a document can be ranked by the ranking of the most similar vector for the document or by having multiple results per document, potentially one per each of the vectors that the document contains, within the same result set. This blog explores multi-vector documents in Elasticsearch, their use cases, and how to link original context to a multi-vector document.

## Use cases for multi-vector documents

Having multiple vectors per document might seem like a rare use case, but in practice it occurs frequently. This is true for both dense vectors and sparse vectors (e.g. when using [ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#elser-benchamrks)) but for simplicity and brevity, the rest of the blog will relate to dense vectors.

The reason for having multiple vectors per document becomes clear when examining two main use cases for dense vector search:

`Text` - Metadata text is typically designed to allow efficient discovery. That’s certainly true for a list of topics or search keywords, but it is even true for metadata like title, which is short and typically seeks to describe the document. Token frequency based algorithms like BM25 tend to do very well on such content so it usually does not require or significantly benefit from the introduction of ML based algorithms and dense vector search. This is not the case however for large chunks of text, e.g. algorithms like BM25 would struggle to compete with NLP algorithms when searching on even a few paragraphs of text, and that is the type of text on which vector search demonstrates a significant advantage. The problem is that most ML models that analyze text to generate dense vectors for ranking are limited to 512 tokens, which is roughly the size of a single paragraph. In other words, when dense vectors are required for vector search there will typically be sufficient text to require generating multiple vectors per document.

`Image` - In many cases the images portray something in the real world and then there are typically images from different angles. That’s a simple result of the fact that images are two dimensional while things in the real world are three dimensional, so a two dimensional image provides very partial information about them. It’s perhaps easiest to demonstrate in e-commerce where there are typically a few images of the product, but the same is true for other image search use cases. The ML models typically generate a single vector per image, so if there are multiple images per product there are multiple vectors per product.

When displaying the result there’s often a need to show the part of the document that was the reason for the ranking, e.g. the section in the text or the image that got the document to rank high in the result set.

## Multiple vectors per document in Elasticsearch

Elasticsearch supports multiple vectors per document through a nested field, and this structure lends itself nicely for retrieval of the content from which the vector was generated. To do that simply add the original data as another nested field.

## Usage example

Here is an example: Create mappings with nested vectors and text fields with the following commands. You can use the dev console in Kibana in any [Stateless](https://www.elastic.co/search-labs/blog/stateless-your-new-state-of-find-with-elasticsearch) project or Elasticsearch deployment of version 8.11 or later.

```
PUT my-long-text-index
{
  "mappings": {
    "properties": {
      "my_long_text_field": {
        "type": "nested", //because there can be multiple vectors per doc
        "properties": {
          "vector": {
            "type": "dense_vector" //the vector used for ranking
          },
          "text_chunk": {
            "type": "text" //the text from which the vector was created
          }
        }
      }
    }
  }
}
```

```
PUT my-long-text-index/_doc/1
{
  "my_long_text_field" : [
    {
      "vector" : [23,14,8],
      "text_chunk" :  "doc 1 chunk 1"
    },
    {
      "vector" : [34,95,17],
      "text_chunk" :  "doc 1 chunk 2"
    }
  ]
}
```

```
PUT my-long-text-index/_doc/2
{
  "my_long_text_field" : [
    {
      "vector" : [3,2,890],
      "text_chunk" :  "doc 2 chunk 1"
    },
    {
      "vector" : [129,765,13],
      "text_chunk" :  "doc 2 chunk 2"
    }
  ]
}
```

Query the index and return the relevant text chunk using inner\_hits:

```
GET my-long-text-index/_search
{
  "knn": {
    "field": "my_long_text_field.vector",
    "query_vector": [23,14,9],
    "k": 1,
    "num_candidates": 10,
    "inner_hits":{
      "_source": false,
      "fields": [ "my_long_text_field.text_chunk"
        ],
        "size": 1
    }
  }
}
```

Your result should look like the following:

```
Result:
{
  "took": 4,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 0.999715,
    "hits": [
      {
        "_index": "my-long-text-index",
        "_id": "1",
        "_score": 0.999715,
        "_source": {
          "my_long_text_field": [
            {
              "vector": [
                23,
                14,
                8
              ],
              "text_chunk": "doc 1 chunk 1"
            },
            {
              "vector": [
                34,
                95,
                17
              ],
              "text_chunk": "doc 1 chunk 2"
            }
          ]
        },
        "inner_hits": {
          "my_long_text_field": {
            "hits": {
              "total": {
                "value": 2,
                "relation": "eq"
              },
              "max_score": 0.999715,
              "hits": [
                {
                  "_index": "my-long-text-index",
                  "_id": "1",
                  "_nested": {
                    "field": "my_long_text_field",
                    "offset": 0
                  },
                  "_score": 0.999715,
                  "fields": {
                    "my_long_text_field": [
                      {
                        "text_chunk": [
                          "doc 1 chunk 1"
                        ]
                      }
                    ]
                  }
                }
              ]
            }
          }
        }
      }
    ]
  }
}
```

If it is preferred to show multiple results from the same document, e.g. if the documents are textbooks and it is useful to provide a RAG several relevant sections from the same book (with each book indexed as a single document), the query can be as follows:

```
GET my-long-text-index/_search
{
  "knn": {
    "field": "my_long_text_field.vector",
    "query_vector": [23,14,9],
    "k": 3,
    "num_candidates": 10,
    "inner_hits":{
      "size": 3,
      "_source": false,
      "fields": [ "my_long_text_field.text_chunk"
        ]
    }
  }
}
```

With the following result:

```
{
  "took": 5,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 2,
      "relation": "eq"
    },
    "max_score": 0.999715,
    "hits": [
      {
        "_index": "my-long-text-index",
        "_id": "1",
        "_score": 0.999715,
        "_source": {
          "my_long_text_field": [
            {
              "vector": [
                23,
                14,
                8
              ],
              "text_chunk": "doc 1 chunk 1"
            },
            {
              "vector": [
                34,
                95,
                17
              ],
              "text_chunk": "doc 1 chunk 2"
            }
          ]
        },
        "inner_hits": {
          "my_long_text_field": {
            "hits": {
              "total": {
                "value": 2,
                "relation": "eq"
              },
              "max_score": 0.999715,
              "hits": [
                {
                  "_index": "my-long-text-index",
                  "_id": "1",
                  "_nested": {
                    "field": "my_long_text_field",
                    "offset": 0
                  },
                  "_score": 0.999715,
                  "fields": {
                    "my_long_text_field": [
                      {
                        "text_chunk": [
                          "doc 1 chunk 1"
                        ]
                      }
                    ]
                  }
                },
                {
                  "_index": "my-long-text-index",
                  "_id": "1",
                  "_nested": {
                    "field": "my_long_text_field",
                    "offset": 1
                  },
                  "_score": 0.88984984,
                  "fields": {
                    "my_long_text_field": [
                      {
                        "text_chunk": [
                          "doc 1 chunk 2"
                        ]
                      }
                    ]
                  }
                }
              ]
            }
          }
        }
      },
      {
        "_index": "my-long-text-index",
        "_id": "2",
        "_score": 0.81309915,
        "_source": {
          "my_long_text_field": [
            {
              "vector": [
                3,
                2,
                890
              ],
              "text_chunk": "doc 2 chunk 1"
            },
            {
              "vector": [
                129,
                765,
                13
              ],
              "text_chunk": "doc 2 chunk 2"
            }
          ]
        },
        "inner_hits": {
          "my_long_text_field": {
            "hits": {
              "total": {
                "value": 2,
                "relation": "eq"
              },
              "max_score": 0.81309915,
              "hits": [
                {
                  "_index": "my-long-text-index",
                  "_id": "2",
                  "_nested": {
                    "field": "my_long_text_field",
                    "offset": 1
                  },
                  "_score": 0.81309915,
                  "fields": {
                    "my_long_text_field": [
                      {
                        "text_chunk": [
                          "doc 2 chunk 2"
                        ]
                      }
                    ]
                  }
                },
                {
                  "_index": "my-long-text-index",
                  "_id": "2",
                  "_nested": {
                    "field": "my_long_text_field",
                    "offset": 0
                  },
                  "_score": 0.6604239,
                  "fields": {
                    "my_long_text_field": [
                      {
                        "text_chunk": [
                          "doc 2 chunk 1"
                        ]
                      }
                    ]
                  }
                }
              ]
            }
          }
        }
      }
    ]
  }
}
```

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter