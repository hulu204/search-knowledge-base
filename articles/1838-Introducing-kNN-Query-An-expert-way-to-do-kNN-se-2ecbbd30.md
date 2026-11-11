---
title: 'Introducing kNN Query: An expert way to do kNN search'
company: Elastic
tag: 召回
date: 2023-12-07
url: https://www.elastic.co/search-labs/blog/knn-query-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Introducing kNN Query: An expert way to do kNN search

Explore how the kNN query in Elasticsearch can be used and how it differs from top-level kNN search, including examples.

December 07, 2023

[Mayya Sharipova](/search-labs/author/mayya-sharipova)[Benjamin Trent](/search-labs/author/benjamin-trent)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

### kNN search as a top-level section

[kNN search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html) in Elasticsearch is organized as a top level section of a search request. We have designed it this way so that:

* It can always return global k nearest neighbors regardless of a number of shards
* These global k results are combined with a results from other queries to form a hybrid search
* The global k results are passed to aggregations to form facets.

Here is a simplified diagram how kNN search is executed internally (some phases are omitted) :

![Execution for top level kNN search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf9df3a17c59cedde/6a170b2aab7f08ec09db9e96/24e227a8482aead389c0ad6298779fd8610006f7-2849x1020.gif)

Figure 1: The steps for the top level kNN search are:

1. A user submits a search request
2. The coordinator node sends a kNN search part of the request to data nodes in the DFS phase
3. Each data node runs kNN search and sends back the local top-k results to the coordinator
4. The coordinator merges all local results to form the global top k nearest neighbors.
5. The coordinator sends back the global k nearest neighbors to the data nodes with any additional queries provided
6. Each data node runs additional queries and sends back the local `size` results to the coordinator
7. The coordinator merges all local results and sends a response to the user

We first run kNN search in the DFS phase to obtain the global top k results. These global k results are then passed to other parts of the search request, such as other queries or aggregations. Even the execution looks complex, from a user’s perspective this model of running kNN search is simple, as the user can always be sure that kNN search returns the global k results.

### Introducing kNN query in Elasticsearch

With time we realized there is also a need to represent kNN search as a query. Query is a core component of a search request in Elasticsearch, and representing kNN search as a query allows for flexibility to combine it with other queries to address more complex requests.

kNN query, unlike the top level kNN search, doesn’t have a `k` parameter. The number of results (nearest neighbors) returned is defined by the `size` parameter, as in other queries. Similar to kNN search, the `num_candidates` parameter defines how many candidates to consider on each shard while executing a kNN search.

```
GET products/_search
{
 "size" : 3,
 "query": {
   "knn": {
     "field": "embedding",
     "query_vector": [2,2,2,0],
     "num_candidates": 10
   }
 }
}
```

kNN query is executed differently from the top level kNN search. Here is a simplified diagram that describes how a kNN query is executed internally (some phases are omitted):

![Execution for kNN query](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf2768a24d52acbbd/6a170b2c7d8d6762fd70e71a/fe505bf7e95ae94c0f7605df1348ef15536134b9-2849x1020.gif)

Figure 2: The steps for query based kNN search are:

1. A user submits a search request
2. The coordinator sends to the data nodes a kNN search query with additional queries provided
3. Each data node runs the query and sends back the local size results to the coordinator node
4. The coordinator node merges all local results and sends a response to the user

We run kNN search on a shard to get `num_candidates` results; these results are passed to other queries and aggregations on a shard to get size results from the shard. As we don’t collect the global k nearest neighbors first, in this model the number of nearest neighbors collected and visible for other queries and aggregations depend on the number of shards.

### kNN query API examples

Let’s look at API examples that demonstrate differences between the top level kNN search and kNN query.

We create an index of products and index some documents:

```
PUT products
{
 "mappings": {
   "dynamic": "strict",
   "properties": {
     "department": {
       "type": "keyword"
     },
     "brand": {
       "type": "keyword"
     },
     "description": {
       "type": "text"
     },
     "embedding": {
       "type": "dense_vector",
       "index": true,
       "similarity": "l2_norm"
     },
     "price": {
       "type": "float"
     }
   }
 }
}
```

```
POST products/_bulk?refresh=true
{"index":{"_id":1}}
{"department":"women","brand": "Levi's", "description":"high-rise red jeans","embedding":[1,1,1,1],"price":100}
{"index":{"_id":2}}
{"department":"women","brand": "Calvin Klein","description":"high-rise beautiful jeans","embedding":[1,1,1,1],"price":250}
{"index":{"_id":3}}
{"department":"women","brand": "Gap","description":"every day jeans","embedding":[1,1,1,1],"price":50}
{"index":{"_id":4}}
{"department":"women","brand": "Levi's","description":"jeans","embedding":[2,2,2,0],"price":75}
{"index":{"_id":5}}
{"department":"women","brand": "Levi's","description":"luxury jeans","embedding":[2,2,2,0],"price":150}
{"index":{"_id":6}}
{"department":"men","brand": "Levi's", "description":"jeans","embedding":[2,2,2,0],"price":50}
{"index":{"_id":7}}
{"department":"women","brand": "Levi's", "description":"jeans 2023","embedding":[2,2,2,0],"price":150}
```

kNN query similar to the top level kNN search, has `num_candidates` and an internal `filter` parameter that acts as a pre-filter.

```
GET products/_search
{
 "size" : 3,
 "query": {
   "knn": {
     "field": "embedding",
     "query_vector": [2,2,2,0],
     "num_candidates": 10,
     "filter" : {
       "term" : {
         "department" : "women"
       }
     }
   }
 }
}
```

kNN query can get more diverse results than kNN search for collapsing and aggregations. For the kNN query below, on each shard we execute kNN search to obtain 10 nearest neighbors which are then passed to collapse to get 3 top results. Thus, we will get 3 diverse hits in a response.

```
GET products/_search
{
 "size" : 3,
 "query": {
   "knn": {
     "field": "embedding",
     "query_vector": [2,2,2,0],
     "num_candidates": 10,
     "filter" : {
       "term" : {
         "department" : "women"
       }
     }
   }
 },
 "collapse": {
   "field": "brand"        
 }
}
```

The top level kNN search first gets the global top 3 results in the DFS phase, and then passes them to collapse in the query phase. We will get only 1 hit in a response, as all the global 3 nearest neighbors happened to be from the same brand.

```
GET products/_search?size=3
{
 "knn" : {
   "field": "embedding",
     "query_vector": [2,2,2,0],
     "k" : 3,
     "num_candidates": 10,
     "filter" : {
       "term" : {
         "department" : "women"
       }
     }
 },
 "collapse": {
   "field": "brand"        
 }
}
```

Similarly for aggregations, a kNN query allows us to get 3 distinct buckets, while kNN search only allows 1.

```
GET products/_search
{
"size": 0,
"query": {
   "knn": {
     "field": "embedding",
     "query_vector": [2,2,2,0],
     "num_candidates": 10,
     "filter" : {
       "term" : {
         "department" : "women"
       }
     }
   }
 },
 "aggs": {
   "brands": {
     "terms": {
       "field": "brand"
     }
   }
 }
}
​
GET products/_search
{
"size": 0,
"knn" : {
 "field": "embedding",
   "query_vector": [2,2,2,0],
   "k" : 3,
   "num_candidates": 10,
   "filter" : {
     "term" : {
       "department" : "women"
     }
   }
 },
 "aggs": {
   "brands": {
     "terms": {
       "field": "brand"
     }
   }
 }
}
```

Now, let’s look at other examples that show the flexibility of the kNN query. Specifically, how it can be flexibly combined with other queries.

kNN can be a part of a [boolean](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html) query (with a caveat that all external query filters are applied as post-filters for kNN search). We can use a [\_name](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html#named-queries) parameter for kNN query to enhance results with extra information that tells if the kNN query was a match and its score contribution.

```
GET products/_search?include_named_queries_score
{
 "size": 3,
 "query": {
   "bool": {
     "should": [
       {
         "knn": {
           "field": "embedding",
           "query_vector": [2,2,2,0],
           "num_candidates": 10,
           "_name": "knn_query"
         }
       },
       {
         "match": {
           "description": {
             "query": "luxury",
             "_name": "bm25query"
           }
         }
       }
     ]
   }
 }
}
```

kNN can also be a part of complex queries, such as a [pinned](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-pinned-query.html) query. This is useful when we want to display the top nearest results, but also want to promote a selected number of other results.

```
GET products/_search
{
 "size": 3,
 "query": {
   "pinned": {
     "ids": [ "1", "2" ],
     "organic": {
       "knn": {
           "field": "embedding",
           "query_vector": [2,2,2,0],
           "num_candidates": 10,
           "_name": "knn_query"
         }
     }
   }
 }
}
```

We can even make the kNN query a part of our [function\_score](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-function-score-query.html) query. This is useful when we need to define custom scores for results returned by kNN query: ​

```
GET products/_search
{
 "size": 3,
 "query": {
   "function_score": {
     "query": {
       "knn": {
           "field": "embedding",
           "query_vector": [2,2,2,0],
           "num_candidates": 10,
           "_name": "knn_query"
         }
     },
     "functions": [
       {
         "filter": { "match": { "department": "men" } },
         "weight": 100
       },
       {
         "filter": { "match": { "department": "women" } },
         "weight": 50
       }
     ]
   }
 }
}
```

kNN query being a part of [dis\_max](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-dis-max-query.html) query is useful when we want to combine results from kNN search and other queries, so that a document’s score comes from the highest ranked clause with a tie breaking increment for any additional clause. ​

```
GET products/_search
{
 "size": 5,
 "query": {
   "dis_max": {
     "queries": [
       {
         "knn": {
           "field": "embedding",
           "query_vector": [2,2, 2,0],
           "num_candidates": 3,
           "_name": "knn_query"
         }
       },
       {
         "match": {
           "description": "high-rise jeans"
         }
       }
     ],
     "tie_breaker": 0.8
   }
 }
}
```

kNN search as a query has been introduced with the 8.12 release. Please try it out, and we would appreciate any feedback.

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