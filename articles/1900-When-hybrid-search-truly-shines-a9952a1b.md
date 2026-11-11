---
title: 'When hybrid search truly shines'
company: Elastic
tag: 召回
date: 2025-01-01
url: https://www.elastic.co/search-labs/blog/elasticsearch-hybrid-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# When hybrid search truly shines

Demonstrating when hybrid search is better than lexical or semantic search on their own.

January 01, 2025

[Gustavo Llermaly](/search-labs/author/gustavo-llermaly)

[AI](/search-labs/blog/category/ai)[Vector Database](/search-labs/blog/category/vector-database)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Jump to

Share

In this article, we are going to explore hybrid search by examples, and show when it truly shines against using lexical or semantic search techniques alone.

## What is hybrid search?

Hybrid search is a technique that combines different search approaches such as traditional lexical term matching, and [semantic search](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search.html).

Lexical search is good when users know the exact words. This approach will find the relevant documents, and sort them in a way that makes sense by using [TF-IDF](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-similarity.html) which means: The more common across the dataset the term you are searching is, the less it contributes to the score; and the more common it is within a certain document the more it contributes to the score.

But, what if the words in the query are not present in the documents? Sometimes the user is not looking for something in concrete, but for a *concept*. They may not be looking for a specific restaurant, but for "a nice place to eat with family". For this kind of queries, semantic search is useful because it takes into consideration the context of the search query and brings similar documents. You can expect to get more related documents back than with the previous approach, but in return, this approach struggles with precision, especially with numbers.

Hybrid search gives us the best of both worlds by blending the precision of term-matching together with the context-aware matching of semantic search.

*You can read a deep dive on hybrid search in* [*this article*](https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid)*, and more about lexical and semantic search differences in* [*this one*](https://www.elastic.co/search-labs/blog/lexical-and-semantic-search-with-elasticsearch)*.*

Let's create an example using real estate units.

![Hybrid search query example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt80d45b7f3f41fb1c/6a16fa1666c4f90f36f8bdf8/038ba76cd1ee2b9869d19cfc0c586aca4c475394-493x274.png)

The query will be: `quiet` home `in Pinewood with 2 rooms` , with `quiet place` being the semantic component of the query while `Pinewood with 2 rooms` will be the textual or lexical portion.

## Configuring ELSER

We are going to use [ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html) as our model provider.

Start by creating the inference endpoint:

```
PUT _inference/sparse_embedding/my-elser-model 
{
  "service": "elser", 
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}
```

If this is your first time using ELSER, you may encounter a 502 Bad Gateway error as the model loads in the background. You can check the status of the model in `Machine Learning > Trained Models` in Kibana. Once it is deployed, you can proceed to the next step.

![trained model checking - hybrid search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt970f5ad6ee6d3937/6a16fa172d2f501131c3c0ea/1b9ff9c6110565f9c384e28f95d469e11bb61e27-1423x641.png)

## Configuring index

For the index, we are going to use text fields, and [semantic\_text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html) for the semantic field. We are going to copy the descriptions, because we want to use them for both `match` and `semantic` queries.

```
PUT properties-hybrid
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "english"
      },
      "description": {
        "type": "text",
        "analyzer": "english", 
        "copy_to": "semantic_field"
      },
      "neighborhood": {
        "type": "keyword"
      },
      "bedrooms": {
        "type": "integer"
      },
      "bathrooms": {
        "type": "integer"
      },
      "semantic_field": {
        "type": "semantic_text",
        "inference_id": "my-elser-model"
      }
    }
  }
}
```

## Indexing data

```
POST _bulk
{ "index" : { "_index" : "properties-hybrid" , "_id": "1"} }
{ "title": "2 Bed 2 Bath in Sunnydale", "description": "Spacious apartment with modern amenities, perfect for urban dwellers.", "neighborhood": "Sunnydale", "bedrooms": 2, "bathrooms": 2 }
{ "index" : { "_index" : "properties-hybrid", "_id": "2" } }
{ "title": "1 Bed 1 Bath in Sunnydale", "description": "Compact apartment with easy access to downtown, ideal for singles or couples.", "neighborhood": "Sunnydale", "bedrooms": 1, "bathrooms": 1 }
{ "index" : { "_index" : "properties-hybrid", "_id": "3" } }
{ "title": "2 Bed 2 Bath in Pinewood", "description": "New apartment with modern bedrooms, located in a restaurant and bar area. Suitable for active people who enjoy nightlife.", "neighborhood": "Pinewood", "bedrooms": 2, "bathrooms": 2 }
{ "index" : { "_index" : "properties-hybrid", "_id": "4" } }
{ "title": "3 Bed 2 Bath in Pinewood", "description": "Secluded and private family unit with a practical layout with three total rooms. Near schools and shops. Perfect for raising kids.", "neighborhood": "Pinewood", "bedrooms": 3, "bathrooms": 2 }
{ "index" : { "_index" : "properties-hybrid", "_id": "5" } }
{ "title": "2 Bed 2 Bath in Pinewood", "description": "Retired apartment in a serene neighborhood, perfect for those seeking a retreat. This well-maintained residence offers two bedrooms with abundant natural light and silence.", "neighborhood": "Pinewood", "bedrooms": 2, "bathrooms": 2 }
{ "index" : { "_index" : "properties-hybrid", "_id": "6" } }
{ "title": "1 Bed 1 Bath in Pinewood", "description": "Apartment with a scenic view, ideal for those seeking an energetic environment.", "neighborhood": "Pinewood", "bedrooms": 1, "bathrooms": 1 }
{ "index" : { "_index" : "properties-hybrid", "_id": "7" } }
{ "title": "2 Bed 2 Bath in Maplewood", "description": "Nice apartment with a large balcony, offering a relaxed and comfortable living experience.", "neighborhood": "Maplewood", "bedrooms": 2, "bathrooms": 2 }
{ "index" : { "_index" : "properties-hybrid", "_id": "8" } }
{ "title": "1 Bed 1 Bath in Maplewood", "description": "Charming apartment with modern interiors, situated in a peaceful neighborhood.", "neighborhood": "Maplewood", "bedrooms": 1, "bathrooms": 1 }
```

## Querying data

Let's start by the classic `match` query, that will search by the content of the title and description:

```
GET properties-hybrid/_search
{
  "query": {
    "multi_match": {
      "query": "quiet home 2 bedroom in Pinewood",
      "fields": ["title", "description"]
    }
  }
}
```

This is the first result:

```
{
    "description": "New apartment with modern bedrooms, located in a restaurant and bar area. Suitable for active people who enjoy nightlife.",
    "title": "2 Bed 2 Bath in Pinewood"
}
```

It is not bad. It managed to capture the neighborhood `Pinewood`, and also the `2 bedroom` requirement, however, this is not a quiet place at all.

Now, a pure semantic query:

```
GET properties-hybrid/_search
{
  "query": {
    "semantic": {
      "field": "semantic_field",
      "query": "quiet home in Pinewood with 2 rooms"
    }
  }
}
```

This is the first result:

```
{
    "description": "Secluded and private family unit with a practical layout with three total rooms. Near schools and shops. Perfect for raising kids.",
    "title": "3 Bed 2 Bath in Pinewood"
}
```

Now the results considered the `quiet home` piece by relating it to things like "secluded and private", but this one is a 3 bedroom and we are looking for 2.

Let's run a hybrid search now. We will use [RRF (Reciprocal rank fusion)](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) to achieve this purpose and combine the two previous queries. The RRF algorithm will blend the scores of both queries for us.

```
GET properties-hybrid/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "semantic": {
                "field": "semantic_field",
                "query": "quiet home 2 bedroom in Pinewood"
              }
            }
          }
        },
        {
          "standard": {
            "query": {
              "multi_match": {
                "query": "quiet home 2 bedroom in Pinewood",
                "fields": ["title", "description"]
              }
            }
          }
        }
      ],
      "rank_window_size": 50,
      "rank_constant": 20
    }
  }
}
```

This is the first result:

```
{
    "description": ""Retired apartment in a serene neighborhood, perfect for those seeking a retreat. This well-maintained residence offers two bedrooms with abundant natural light and silence.",
    "title": "2 Bed 2 Bath in Pinewood"
}
```

Now the results considered both being a quiet place, but also having 2 bedrooms.

## Evaluating results

For the evaluation, we are going to use the [Ranking Evaluation API](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html) which allows us to automate the process of running queries and then checking the position of the relevant results. You can choose between different evaluation metrics. For this example I will pick [Mean reciprocal ranking (MRR)](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html#_mean_reciprocal_rank) which takes into consideration the result position and reduces the score as the position gets lower by 1/position#.

For this scenario, we are going to test our 3 queries (`multi_match`, `semantic`, `hybrid`) against the initial question:

`quiet home 2 bedroom in Pinewood`

Expecting the following apartment to be in the first position as it meets all the criteria.

> Retired apartment in a serene neighborhood, perfect for those seeking a retreat. This well-maintained residence offers two bedrooms with abundant natural light and silence."

We can configure as many queries as we need, and put on ratings the id of the documents we expect to be in the first positions:

```
GET /properties-hybrid/_rank_eval
{
  "requests": [
    {
      "id": "hybrid",
      "request": {
        "retriever": {
          "rrf": {
            "retrievers": [
              {
                "standard": {
                  "query": {
                    "semantic": {
                      "field": "semantic_field",
                      "query": "quiet home 2 bedroom in Pinewood"
                    }
                  }
                }
              },
              {
                "standard": {
                  "query": {
                    "multi_match": {
                      "query": "quiet home 2 bedroom in Pinewood",
                      "fields": [
                        "title",
                        "description"
                      ]
                    }
                  }
                }
              }
            ],
            "rank_window_size": 50,
            "rank_constant": 20
          }
        }
      },
      "ratings": [
        {
          "_index": "properties-hybrid",
          "_id": "5",
          "rating": 1
        }
      ]
    },
    {
      "id": "lexical",
      "request": {
        "query": {
          "multi_match": {
            "query": "quiet home 2 bedroom in Pinewood",
            "fields": [
              "title",
              "description"
            ]
          }
        }
      },
      "ratings": [
        {
          "_index": "properties-hybrid",
          "_id": "5",
          "rating": 1
        }
      ]
    },
    {
      "id": "semantic",
      "request": {
        "query": {
          "semantic": {
            "field": "semantic_field",
            "query": "quiet place in Pinewood with 2 rooms"
          }
        }
      },
      "ratings": [
        {
          "_index": "properties-hybrid",
          "_id": "5",
          "rating": 1
        }
      ]
    }
  ],
  "metric": {
    "mean_reciprocal_rank": {
      "k": 20,
      "relevant_rating_threshold": 1
    }
  }
}
```

![Ranking results](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc111173a52ea36bd/6a16fa19964cea09c608b96e/33b2fd92ec18a6fd2abc6ad90204e801977a3c4a-412x688.png)

As you can see in the image, the query got a score of 1 for hybrid search (1st position), and 0.5 in the other ones, meaning the expected result was returned in the second position.

## Conclusion

Full-text search techniques–which find terms and sort the results by term frequency–and semantic search–which will search by semantic proximity–are powerful in different scenarios. On the one hand, text search shines when users are specific with what they want to search, for example providing the exact SKU for an article or words present on a technical manual. On the other hand, semantic search is useful when users are looking for concepts or ideas not explicitly defined in the documents. Combining both approaches with hybrid search, gives you both full-text search capabilities as well as adding semantically related documents, which can be useful in specific scenarios that require keyword matching and contextual understanding. This dual approach enhances search accuracy and relevance, making it ideal for complex queries and diverse content types.

### Frequently Asked Questions

#### What is hybrid search?

Hybrid search is a technique that combines different search approaches such as traditional lexical term matching, and semantic search.

#### When should you use lexical search?

Lexical search is good when users know the exact words.

#### When should you use semantic search?

Semantic search is useful when users are looking for concepts or ideas not explicitly defined in the documents.

#### When should you use hybrid search over semantic or lexical search?

Hybrid search should be used in scenarios that require keyword matching and contextual understanding. This approach enhances search accuracy and relevance, making it ideal for complex queries and diverse content types.

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