---
title: 'Introducing Retrievers - Search All the Things!'
company: Elastic
tag: 召回
date: 2024-05-28
url: https://www.elastic.co/search-labs/blog/elasticsearch-retrievers
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Introducing Retrievers - Search All the Things!

Learn about Elasticsearch retrievers, including Standard, kNN, text\_expansion, and RRF. Discover how to use retrievers with examples.

May 28, 2024

[Jeff Vestal](/search-labs/author/jeff-vestal)[Jack Conradson](/search-labs/author/jack-conradson)

[Vector Database](/search-labs/blog/category/vector-database)[Python](/search-labs/blog/category/python-programming)

Jump to

Share

In 8.14, Elastic introduced a new search capability called “Retrievers” in Elasticsearch. Keep reading to discover their simplicity and efficiency and how they can empower you in your search operations.

Retrievers are a new abstraction layer added to the Search API in Elasticsearch. They offer the convenience of configuring multi-stage retrieval pipelines within a single `_search` API call. This architecture simplifies search logic in your application by eliminating the need for multiple Elasticsearch API calls for complex search queries. It also reduces the need for client-side logic, often required to combine results from multiple queries.

## Initial types of Retrievers

There are three types of retrievers included in the initial release. Each of these retrievers is designed for a specific purpose, and when combined, they allow for complex search operations.

The available types are:

* Standard - Return the top documents from a traditional query. These allow backward compatibility by supporting existing Query DSL request syntax, allowing you to migrate to the retriever framework at your own pace.
* **kNN** - Return the top documents from a kNN search.
* **RRF** - Combine and rank multiple first-stage retrievers into a single result set with no or minimal user tuning using the reciprocal rank fusion algorithm. An RRF retriever is a compound retriever whose filter element is propagated to its sub-retrievers.

## How are Retrievers different, and why are they useful?

With traditional queries, the query is part of the overall search API call. Retrievers differ by being designed as standalone entities that can be used in isolation or easily combined. This modular approach allows for more flexibility when designing search strategies.

Retrievers are designed to be part of a “retriever tree,” a hierarchical structure that defines search operations by clarifying their sequence and logic. This structure makes complex searches more manageable and easier for developers to understand and allows new functionality to be easily added in the future.

Retrievers enable composability, allowing you to build pipelines and integrate different retrieval strategies. This allows for easy testing of varying retrieval combinations. They also provide more control over how documents are scored and filtered. You can, for example, specify a minimum score threshold, apply a complex filter without affecting scoring, and use parameters like

[terminate\_after](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#standard-retriever) for performance optimizations.

Backward compatibility is maintained with traditional query elements, automatically translating them to the appropriate retriever.

## Retrievers usage examples

Let’s look at some examples of using retrievers. We are using an IMDB sample dataset.

You can run [the accompying jupyter notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/introducing-retrievers/retrievers_intro_notebook.ipynb) to ingest IMDB data into a Serverless Search project and run the below examples yourself!

The high-level setup is:

* `overview` - a short summary of the movie
* `names` the movie's name
* `overview_dense` - a dense\_vector generated from an `e5-small` model
* `overview_sparse` - a sparse vector using Elastic’s `ELSER` model.
* Only returning the text version of `names` and `overview` using `fields` and setting `_source:false`

### Standard - Search All the Text!

```
GET /imdb_movies/_search?pretty
{
  "retriever": {
    "standard": {
      "query": {
        "term": {
          "overview": "clueless"
        }
      }
    }
  },
  "size": 3,
  "fields": [
    "names",
    "overview"
  ],
  "_source": false
}
```

### kNN - Search all the Dense Vectors!

```
GET /imdb_movies/_search?pretty
{
  "retriever": {
    "knn": {
      "field": "overview_dense",
      "query_vector_builder": {
        "text_embedding": {
          "model_id": ".multilingual-e5-small_linux-x86_64",
          "model_text": "clueless slackers"
        }
      },
      "k": 5,
      "num_candidates": 5
    }
  },
  "size": 3,
  "fields": [
    "names",
    "overview"
  ],
  "_source": false
}
```

### text\_expansion - Search all the Sparse Vectors!

```
GET /imdb_movies/_search?pretty
{
  "retriever": {
    "standard": {
      "query": {
        "text_expansion": {
          "overview_sparse": {
            "model_id": ".elser_model_2_linux-x86_64",
            "model_text": "clueless slackers"
          }
        }
      }
    }
  },
  "size": 3,
  "fields": [
    "names",
    "overview"
  ],
  "_source": false
}
```

### rrf - Combine All the Things!

```
GET /imdb_movies/_search?pretty
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "term": {
                "overview": "clueless slackers"
              }
            }
          }
        },
        {
          "knn": {
            "field": "overview_dense",
            "query_vector_builder": {
              "text_embedding": {
                "model_id": ".multilingual-e5-small_linux-x86_64",
                "model_text": "clueless slackers"
              }
            },
            "k": 5,
            "num_candidates": 5
          }
        },
        {
          "standard": {
            "query": {
              "text_expansion": {
                "overview_sparse": {
                  "model_id": ".elser_model_2_linux-x86_64",
                  "model_text": "clueless slackers"
                }
              }
            }
          }
        }
      ],
      "rank_window_size": 5,
      "rank_constant": 1
    }
  },
  "size": 3,
  "fields": [
    "names",
    "overview"
  ],
  "_source": false
}
```

## Current restrictions with Retrievers

Retrievers come with certain restrictions users should be aware of. For example, only the query element is allowed when using compound retrievers. This enforces a cleaner separation of concerns and prevents the complexity from overly nested or independent configurations. Additionally, sub-retrievers may not use elements restricted from having a compound retriever as part of the retriever tree.

These restrictions enforce performance and composability even with complex retrieval strategies.

Retrievers are initially released as a technical preview, so their API may change.

## Conclusion

Retrievers represent a significant step forward with Elasticsearch's retrieval capabilities and user-friendliness. They can be chained in a pipeline fashion where each retriever applies its logic and passes the results to the next item in the chain. By allowing for more structured, flexible, and efficient search operations, retrievers can significantly enhance the search experience.

The following resources provide additional details on Retrievers.

* [Semantic Reranking in Elasticsearch with Retrievers](https://www.elastic.co/search-labs/blog/semantic-reranking-with-retrievers)
* [Retrievers API documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#standard-retriever)
* [Retrievers - Search Your Data documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.14/retrievers-overview.html)

Try the above code yourself! You can run [the accompying jupyter notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/introducing-retrievers/retrievers_intro_notebook.ipynb) to ingest IMDB data into an Elastic Serverless Search project!

### Frequently Asked Questions

#### What are retrievers in Elasticsearch?

Retrievers are a new abstraction layer added to the Search API in Elasticsearch. They offer the convenience of configuring multi-stage retrieval pipelines within a single `\_search` API call.

#### What are the current restrictions of Elasticsearch retrievers?

Retrievers come with certain restrictions users should be aware of. For example, only the query element is allowed when using compound retrievers. Additionally, sub-retrievers may not use elements restricted from having a compound retriever as part of the retriever tree.

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