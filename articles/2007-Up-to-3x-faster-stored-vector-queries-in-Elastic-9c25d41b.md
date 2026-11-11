---
title: 'Up to 3x faster stored-vector queries in Elasticsearch'
company: Elastic
tag: 工程相关
date: 2026-05-21
url: https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-lookup
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Up to 3x faster stored-vector queries in Elasticsearch

Elasticsearch 9.4 provides a simpler way to search with vectors stored in an Elasticsearch index, with up to 3x lower latency.

May 21, 2026

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Finding documents similar to a stored vector in Elasticsearch used to require two round trips: Fetch the vector with [`GET`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-get), and then send it back in a [k-nearest neighbor (kNN)](https://www.elastic.co/docs/solutions/search/vector/knn) query. Elasticsearch 9.4 collapses that flow into one request with [`query_vector_builder.lookup`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query#knn-query-builder-lookup), simplifying the API and improving latency by up to 3x in a two-node Google Cloud Platform (GCP) benchmark.

## Why stored-vector search used to require two requests

Previously, when you wanted to find documents similar to a stored vector, you needed to:

* Call `GET` to fetch the vector value from Elasticsearch.
* Call `_search` referencing that vector value in Elasticsearch:

  + Serialize the vector value via JSON.

This means paying serialization and network costs twice:

* Serialization and deserialization of the vector for both requests.
* Network latency costs in both directions.
* Potential egress costs in cloud deployments.

In Python, the pattern would be:

```
from elasticsearch import Elasticsearch

es = Elasticsearch(HOST)

# 1) Fetch the seed vector from Elasticsearch
seed_doc = es.get(
    index=source_index,
    id=seed_id,
    _source_includes=[vector_field],
)
query_vector = seed_doc["_source"][vector_field]

# 2) Send it back in a kNN query
resp = es.search(
    index=target_index,
    query={
        "knn": {
            "field": vector_field,
            "k": 10,
            "num_candidates": 100,
            "query_vector": query_vector,
        }
    },
)
```

While these two calls seem cheap, the overhead is unnecessary. Let’s make this better.

## How query\_vector\_builder.lookup works in Elasticsearch 9.4

In Elasticsearch 9.4, we added lookup to simplify the API and eliminate unnecessary costs:

```
from elasticsearch import Elasticsearch

es = Elasticsearch(HOST)

resp = es.search(
    index="products",
    query={
        "knn": {
            "field": "product-vector",
            "k": 10,
            "num_candidates": 100,
            "query_vector_builder": {
                "lookup": {
                    "index": "seed-products",
                    "id": "product-123",
                    "path": "product-vector"
                }
            },
        }
    },
)
```

This request now grabs the `dense_vector` value stored in the `product-vector` field, in the document with ID `product-123` in the `seed-products` index. This example is a “more like this” search, finding the nearest vectors to the one with ID `product-123`. You can refer to any index, effectively using lookup as a query vector store.

## How much latency lookup vector search can remove

The goal is to simplify the experience and make it faster. The performance gains aren't just from eliminating the client round trip. Many Elasticsearch instances involve multiple nodes, and traffic between nodes can carry its own serialization and network costs. Elasticsearch actively biases execution toward the local node, which cuts network serialization costs on the server side, too.

To illustrate the potential performance improvements, here’s a benchmark we ran. We used a modified version of our [`so_vector`](https://github.com/elastic/rally-tracks/tree/master/so_vector), where instead of using the query vectors, one path did the `GET` and then `_search` pattern and the other used `lookup`. Running on two nodes in the same zone in GCP, the results were strong. Latency was consistently improved by almost 3x. Even when nodes are within the same data center and the same availability zone, network and serialization costs can have a real impact.

| Percentile | get-then-knn (ms) | lookup-knn (ms) | Reduction | Speedup |
| --- | --- | --- | --- | --- |
| p50 | 10.3796 | 3.14093 | 69.74% | 3.30x |
| p90 | 25.4429 | 5.89807 | 76.82% | 4.31x |
| p99 | 27.7167 | 8.07109 | 70.88% | 3.43x |
| max (p100) | 28.522 | 12.6497 | 55.65% | 2.25x |

This benchmark ran with 2M documents, and the latency improvement will depend on your overall search costs. Even when the speedup is smaller, lookup still removes the extra client-side request. Less code, fewer round trips.

## A simpler path for stored-vector search

Sometimes small changes can have an outsized impact. While this is a simple feature, I hope it removes some unnecessary friction in your Elasticsearch usage and makes us that much more lovable.

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