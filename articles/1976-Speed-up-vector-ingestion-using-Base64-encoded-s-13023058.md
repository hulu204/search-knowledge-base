---
title: 'Speed up vector ingestion using Base64-encoded strings'
company: Elastic
tag: 工程相关
date: 2026-02-04
url: https://www.elastic.co/search-labs/blog/base64-encoded-strings-vector-ingestion
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Speed up vector ingestion using Base64-encoded strings

Introducing Base64-encoded strings to speed up vector ingestion in Elasticsearch.

February 04, 2026

[Jim Ferenczi](/search-labs/author/jim-ferenczi)[Benjamin Trent](/search-labs/author/benjamin-trent)[Ignacio Vera Sequeiros](/search-labs/author/ignacio-vera-sequeiros)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

We’re improving the ingestion speed of vectors in Elasticsearch. Now, in [Elastic Cloud Serverless](https://www.elastic.co/cloud/serverless) and in v9.3, you can send your vectors to Elasticsearch encoded as Base64 strings, which will provide immediate benefits to your ingestion pipeline.

This change reduces the overhead of parsing vectors in JSON by an order of magnitude, which translates to almost a 100% improvement on indexing throughput for DiskBBQ and around 20% improvement for hierarchical navigable small world (HNSW) workloads. In this blog, we’ll take a closer look at Base64-encoded strings and the improvements it brings to vector ingestion.

## What’s the problem?

At Elastic, we’re always looking for ways to improve our vector search capabilities, whether that’s enhancing existing storage formats or introducing new ones. Recently, for example, we added a new disk-friendly storage format called [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction) and enabled vector indexing with [NVIDIA cuVS](https://www.elastic.co/search-labs/blog/elasticsearch-gpu-accelerated-vector-indexing-nvidia).

In both cases, we expected to see major gains in ingestion speed. However, once these changes were fully integrated into Elasticsearch, the improvements weren’t as large as we had hoped. A flamegraph of the ingestion process made the issue clear: JSON parsing had become one of the main bottlenecks.

![Vector ingestion before using Base64-encoded strings  ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7d4cd9d8628b64b3/6a170c5b2867148d5e93e353/a286408afc85ff1cd3dd448b8fdf59dd3e11d599-1600x675.png)

Parsing JSON requires walking through every element in the arrays and converting numbers from text format into 32-bit floating-point values, which is very expensive.

### Why Base64-encoded strings?

The most efficient way to parse vectors is directly from their binary representation, where each element uses a 32-bit floating-point value. However, JSON is a text-based format, and the way to include binary data in it is by using [Base64](https://en.wikipedia.org/wiki/Base64)-encoded strings. Base64 is just a binary-to-text encoding schema.

```
{
  “emb” : [1.2345678, 2.3456789, 3.4567891]
}
```

We can now send vectors encoded as Base64 strings:

```
{
  “emb” : ”P54GUUAWH5pAXTwI”
}
```

Is it worth it? Our benchmarks suggest yes. When parsing 1,000 JSON documents, using Base64 encoded strings instead of float arrays resulted in performance improvements of more than an order of magnitude, at the cost of a small encode/decode trade-off (client-side Base64 encoding and a temporary byte array on the server for decoding) in exchange for eliminating expensive per-element numeric parsing.

![Base64 vs. Float32 parsing time](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta9a1662fdf7d5849/6a170c5d839dfaf624dcff29/86e5a926e13b07bb3b0abe80bd4930464e8f6f9b-1200x742.png)

### Give me some ingestion numbers

We can see these improvements in practice when running the [`so_vector`](https://github.com/elastic/rally-tracks/blob/master/so_vector/README.md) rally track with the different approaches. The actual gains depend on how fast indexing is for each storage format. For `bbq_disk`, indexing throughput increases by about 100%, while for `bbq_hnsw`, the improvement is closer to 20%, since indexing is inherently slower there.

![Base64 vs Float32 indexing throughput](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte35ffc920ae863f5/6a170c5e509168f193e1bb1c/4277057ee59cb84d068176b56bb7fa00b66e1cb3-1200x742.png)

Starting with Elasticsearch v9.2, [vectors are excluded from](https://www.elastic.co/search-labs/blog/elasticsearch-exclude-vectors-from-source) [`_source`](https://www.elastic.co/search-labs/blog/elasticsearch-exclude-vectors-from-source) by default and are stored internally as 32-bit floating-point values. This behavior also applies to Base64-encoded vectors, making the choice of indexing format completely transparent at search time.

## Client support

Adding a new format for indexing vectors might require changes on ingestion pipelines. To help this effort, in v9.3, Elasticsearch official clients can transform vectors with 32-bit floating-point values into Base64-encoded strings and the other way around. You might need to check the client documentation for the specific implementation.

For example, here’s a snippet for implementing bulk loading using the Python client:

```
from elasticsearch.helpers import bulk, pack_dense_vector

def get_next_document():
    for doc in dataset:
        yield {
            "_index": "my-index",
            "_source": {
                "title": doc["title"],
                "text": doc["text"],
                "emb": pack_dense_vector(doc["emb"]),
            },
        }

result = bulk(
    client=client,
    chunk_size=chunk_size,
    actions=get_next_document,
    stats_only=True,
)
```

The only difference from a bulk ingest using floats is that the embedding is wrapped with the `pack_dense_vector()` auxiliary function.

## Conclusion

By switching from JSON float arrays to Base64-encoded vectors, we remove one of the largest remaining bottlenecks in Elasticsearch’s vector ingestion pipeline: numeric parsing. The result is a simple change with outsized impact: up to 2× higher throughput for DiskBBQ workloads and meaningful gains even for slower indexing strategies, like HNSW.

Because vectors are already stored internally in a binary format and excluded from `_source` by default, this improvement is completely transparent at search time. With official client support landing in v9.3, adopting Base64 encoding requires only minimal changes to existing ingestion code, while delivering immediate performance benefits.

If you’re indexing large volumes of embeddings, especially in high-throughput or serverless environments, Base64-encoded vectors are now the fastest and most efficient way to get your data into Elasticsearch.Those interested in the implementation details can follow the related Elasticsearch issues and pull requests: #[111281](https://github.com/elastic/elasticsearch/issues/111281) and #[135943](https://github.com/elastic/elasticsearch/issues/135943).

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