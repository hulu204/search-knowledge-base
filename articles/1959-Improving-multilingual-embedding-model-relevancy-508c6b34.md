---
title: 'Improving multilingual embedding model relevancy with hybrid search reranking'
company: Elastic
tag: 排序
date: 2025-11-03
url: https://www.elastic.co/search-labs/blog/multilingual-embedding-model-hybrid-search-reranking
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving multilingual embedding model relevancy with hybrid search reranking

Learn how to improve the relevancy of E5 multilingual embedding model search results using Cohere's reranker and hybrid search in Elasticsearch.

November 03, 2025

[Quynh Nguyen](/search-labs/author/quynh-nguyen)

[Vector Database](/search-labs/blog/category/vector-database)[Operations](/search-labs/blog/category/operations)

Part of the series:

[Deploying and querying an e5 multilingual embedding model in Elasticsearch](/search-labs/blog/series/multilingual-embedding-model-elasticsearch-deployment)

In this series

Share

## Introduction

In the [last part of this series](https://www.elastic.co/search-labs/blog/multilingual-embedding-model-deployment-elasticsearch), we walked through deploying Elastic's pre-trained E5 model (as well as other multilingual text embedding models from Hugging Face) and dived into generating dense vector embeddings from your text data using Elasticsearch and Kibana. In this blog, we will examine the results of these embeddings and highlight the significant advantages of leveraging a multilingual model.

Now that we have our index `coco_multilingual`, performing the search will give us documents in multiple languages, with the “en” field for us to reference:

```
# GET coco_multilingual/_search
    {
       "_index": "coco_multilingual",
       "_id": "WAiXQJYBgf6odR9bLohZ",
       "_score": 1,
       "_source": {
         "description": "Ein Parkmeßgerät auf einer Straße mit Autos",
         "en": "A row of parked cars sitting next to parking meters.",
         "language": "de",
         "vector_description": {...}
       }
     },
     . . .
```

## Performing a search in English

Let’s try to perform the search in English and see how well it does:

```
GET coco_multi/_search
{
"size": 10,
"_source": [
  "description", "language", "en"
],
"knn": {
  "field": "vector_description.predicted_value",
  "k": 10,
  "num_candidates": 100,
  "query_vector_builder": {
    "text_embedding": {
      "model_id": ".multilingual-e5-small_linux-x86_64_search",
      "model_text": "query: kitty"
    }
  }
}
}
```

```
{
       "_index": "coco_multi",
       "_id": "JQiXQJYBgf6odR9b6Yz0",
       "_score": 0.9334303,
       "_source": {
         "description": "Eine Katze, die in einem kleinen, gepackten Koffer sitzt.",
         "en": "A brown and white cat is in a suitcase.",
         "language": "de"
       }
     },
      {
       "_index": "coco_multi",
       "_id": "3AiXQJYBgf6odR9bFod6",
       "_score": 0.9281012,
       "_source": {
         "description": "Una bambina che tiene un gattino vicino a una recinzione blu.",
         "en": "A little girl holding a kitten next to a blue fence.",
         "language": "it"
       }
     },
     . . .
```

Here, even though the query looks deceptively simple, we are searching for the numerical embeddings of the word ‘kitty’ across all documents in all languages underneath the hood. And because we are performing vector search, we can semantically search for all words that might be related to ‘kitty’: “cat”, “kitten”, “feline”, “gatto” (Italian), “mèo” (Vietnamese), 고양이 (Korean), 猫 (Chinese), etc. As a result, even if my query is in English, we can search for content in all other languages too. For example, searching for a kitty l`ying on something` gives back documents in Italian, Dutch, or Vietnamese, too. Talk about efficiency!

## Performing a search for content in other languages

```
GET coco_multi/_search
{  
 "size": 100,
 "_source": [
   "description", "language", "en"
 ],
 "knn": {
   "field": "vector_description.predicted_value",
   "k": 50,
   "num_candidates": 1000,
   "query_vector_builder": {
     "text_embedding": {
       "model_id": ".multilingual-e5-small_linux-x86_64_search",
       "model_text": "query: kitty lying on something"
     }
   }
 }
}
```

```
{
 "description": "A black kitten lays on her side beside remote controls.",
 "en": "A black kitten lays on her side beside remote controls.",
 "language": "en"
},
{
 "description": "un gattino sdraiato su un letto accanto ad alcuni telefoni ",
 "en": "A black kitten lays on her side beside remote controls.",
 "language": "it"
},
{
 "description": "eine Katze legt sich auf ein ausgestopftes Tier",
 "en": "a cat lays down on a stuffed animal",
 "language": "de"
},
{
 "description": "Một chú mèo con màu đen nằm nghiêng bên cạnh điều khiển từ xa.",
 "en": "A black kitten lays on her side beside remote controls.",
 "language": "vi"
}
. . .
```

Similarly, performing a keyword search for “cat” in Korean (“고양이”) will also give back meaningful results. What’s spectacular here is that we don’t even have any documents in Korean in this index!

```
GET coco_multi/_search
{
 "size": 100,
 "_source": [
   "description", "language", "en"
 ],
 "knn": {
   "field": "vector_description.predicted_value",
   "k": 50,
   "num_candidates": 1000,
   "query_vector_builder": {
     "text_embedding": {
       "model_id": ".multilingual-e5-small_linux-x86_64_search",
       "model_text": "query: 고양이"
     }
   }
 }
}
```

```
 {
       {
         "description": "eine Katze legt sich auf ein ausgestopftes Tier",
         "en": "a cat lays down on a stuffed animal",
         "language": "de"
       }
     },
     {
       {
         "description": "Một con chó và con mèo đang ngủ với nhau trên một chiếc ghế dài màu cam.",
         "en": "A dog and cat lying  together on an orange couch. ",
         "language": "vi"
       }
     },
```

This works because the embedding model represents meaning in a shared semantic space, allowing retrieval of relevant images even with a query in a different language than the indexed captions.

## Increasing relevant search results with hybrid search and reranking

We are happy that the relevant results showed up as expected. But, in the real world, say in ecommerce or in RAG applications that need to narrow down to the top 5-10 most applicable results, we can use a rerank model to prioritize the most relevant results.

Here, performing a query that asks “what color is the cat?” in Vietnamese will yield a lot of results, but the top 1 or 2 might not be the most relevant.

```
GET coco_multi/_search
{
 "size": 20,
 "_source": [
   "description",
   "language",
   "en"
 ],
 "knn": {
   "field": "vector_description.predicted_value",
   "k": 20,
   "num_candidates": 1000,
   "query_vector_builder": {
     "text_embedding": {
       "model_id": ".multilingual-e5-small_linux-x86_64_search",
       "model_text": "query: con mèo màu gì?"
     }
   }
 }
}
```

The results all mention cat, or some form of color:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt979f5944b1708042/6a17ef76420229ff6829f6aa/33e1e887dbbdd1066cfedc7375f5e3b46538529e-859x847.png)

So let’s improve that! Let’s integrate [Cohere](https://cohere.com/blog/rerank-3pt5)’s multilingual rerank model to improve the reasoning corresponding to our question.

```
PUT _inference/rerank/cohere_rerank
{
 "service": "cohere",
 "service_settings": {
   "api_key": "your_api_key",
   "model_id": "rerank-v3.5"
 },
 "task_settings": {
   "top_n": 10,
   "return_documents": true
 }
}

GET coco_multi/_search
{
"size": 10,
"_source": [
  "description",
  "language",
  "en"
],
"retriever": {
  "text_similarity_reranker": {
    "retriever": {
      "rrf": {
        "retrievers": [
          {
            "knn": {
              "field": "vector_description.predicted_value",
              "k": 50,
              "num_candidates": 100,
              "query_vector_builder": {
                "text_embedding": {
                  "model_id": ".multilingual-e5-small_linux-x86_64_search",
                  "model_text": "query: con mèo màu gì?" // English: What color is the cat?
                }
              }
            }
          }
        ],
        "rank_window_size": 100,
        "rank_constant": 0
      }
    },
    "field": "description",
    "inference_id": "cohere_rerank",
    "inference_text": "con mèo màu gì?"
  }
}
}
```

```
 {
       "_index": "coco_multi",
       "_id": "rQiYQJYBgf6odR9bBYyH",
       "_score": 1.5501487,
       "_source": {
         "description": "Hai cái điện thoại được đặt trên một cái chăn cạnh một con mèo con màu đen.",
         "en": "A black kitten lays on her side beside remote controls.",
         "language": "vi"
       }
     },
     {
       "_index": "coco_multi",
       "_id": "swiXQJYBgf6odR9b04uf",
       "_score": 1.5427427,
       "_source": {
         "description": "Một con mèo sọc nâu nhìn vào máy quay.", // Real translation: A brown striped cat looks at the camera 
         "en": "This cat is sitting on a porch near a tire.",
         "language": "vi"
       }
     },
```

Now, with the top results, our application can confidently answer that the kitten’s color is black or brown with stripes. What’s even more interesting here is that our vector search actually caught an omission in the English caption in the original dataset. It’s able to find the brown striped cat even though the reference English translation missed that detail. This is the power of vector search.

## Conclusion

In this blog, we have walked through the utility of a multilingual embedding model, and how to leverage Elasticsearch to integrate the models to generate embeddings, and to effectively improve relevance and accuracy with a hybrid search and reranker. You can [create a Cloud cluster](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs) of your own to try [multilingual semantic search using our out-of-the-box E5 model](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-e5) on the language and dataset of your choice.

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