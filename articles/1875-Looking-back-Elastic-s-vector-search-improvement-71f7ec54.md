---
title: "Looking back: Elastic's vector search improvements in Elasticsearch & Lucene"
company: Elastic
tag: 召回
date: 2024-08-27
url: https://www.elastic.co/search-labs/blog/vector-search-improvements
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Looking back: Elastic's vector search improvements in Elasticsearch & Lucene

Looking back at Elastic's vector search innovations in Elasticsearch and Lucene.

August 27, 2024

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)[Benjamin Trent](/search-labs/author/benjamin-trent)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

Reflecting on all of the changes surrounding speed, scale and relevance in Elasticsearch up through the latest 8.15.0 release, it's phenomenal how far we've come.

This post serves as an aggregation and timeline of all the great work that has been put into Elasticearch and Lucene to make it the best vector database. We dive into [significant strides in Lucene vector search performance](https://www.elastic.co/search-labs/blog/elasticsearch-lucene-vector-database-gains) and other [Lucene improvements](https://www.elastic.co/search-labs/blog/what-happened-in-lucene-land-in-2023) if you want even more information about how it all works under the hood.

## Elasticsearch 7.x

Our story started all the way back in Elasticsearch 7, when some of our visionary engineers advocated that vector search was important and we should support it.

Some of the changes in version 7 included introducing field types for high-dimensional vectors, vector similarity functions, and vector script functions for dense vectors to be used in brute force search.

This was only the beginning...

## Elasticsearch 8.0

Elasticsearch 8.0 introduced [native support for ANN search](https://www.elastic.co/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0).

Additionally, Elasticsearch introduced experimental support for kNN search over HNSW for float vectors.

## Elasticsearch 8.2

In Elasticsearch 8.2, we added filtering support to kNN search.

Elasticsearch 8.2 shipped with Lucene 9.1, which included kNN search with filtering, [improved vector merge speed by reducing I/O](https://issues.apache.org/jira/browse/LUCENE-10375), and faster `l2_norm` calculations through [unrolling and auto-vectorization](https://issues.apache.org/jira/browse/LUCENE-10453).

## Elasticsearch 8.3

Elasticsearch 8.3 shipped with Lucene 9.2, which improved HNSW graph performance by performing a diversity check of neighbors and correcting the base layer connection count.

## Elasticsearch 8.4

In Elasticsearch 8.4, kNN search was made generally available and added to the `_search` endpoint. This unlocked functionality such as hybrid search with filtering, reranking, and semantic search combined with lexical search.

## Elasticsearch 8.5

In Elasticsearch 8.5, we added support for synthetic source for `dense_vector` fields.

Elasticsearch 8.5 shipped with Lucene 9.4, which added support for byte encoded vectors, and optimized performance by building the hnsw graph during indexing to improve flush time.

## Elasticsearch 8.6

Elasticsearch 8.6 added support for byte vectors, so that users can quantize vectors outside of Elasticsearch.

## Elasticsearch 8.7

Elasticsearch 8.7 added the ability to search more than one kNN field at a time.

Elasticsearch 8.7 also shipped with Lucene 9.5, which came with improved HNSW graph storage efficiency.

## Elasticsearch 8.8

Elasticsearch 8.8 was a huge release. Not only did we increase dimensionality support to 2048 for `dense_vector` queries, but we also launched the `text_expansion` query for sparse vector queries and the state of the art ELSER V1 model.

Elasticsearch 8.8 shipped with Lucene 9.6, which offered improved HNSW merge performance by reusing the largest graph.

## Elasticsearch 8.9

8.9 was another huge release for performance gains, introducing [SIMD support](https://www.elastic.co/blog/accelerating-vector-search-simd-instructions) with the [Panama Vector API](https://openjdk.org/projects/panama/).
On top of that, `query_vector_builder` was made generally available, and RRF was introduced.

Elasticsearch 8.9 also shipped with Lucene 9.7, which added multi-segment parallelism to kNN queries, sped up brute force for floating point vectors by adjusting how they are encoded on disk, and sped up brute force search with vectors by utilizing the Panama Vector API.

## Elasticsearch 8.10

In Elasticsearch 8.10 multi-segment search parallelism was introduced.

## Elasticsearch 8.11

With Elasticsearch 8.11, we leveraged [passage vector search support](https://www.elastic.co/search-labs/blog/adding-passage-vector-search-to-lucene) in Lucene to support passage vectors in Elasticsearch through nested fields. Additionally, we increased the maximum number of vector dimensions to 4096, and added support for maximum inner product. We reintroduced `sparse_vector` field mapping, released a new, improved and generally available ELSER V2 model, and started indexing dense vectors by default (with dynamic mapping).

Elasticsearch 8.11 also leveraged Lucene 9.8, which added MIP support.

## Elasticsearch 8.12

In 8.12, we launched [kNN as a query](https://www.elastic.co/search-labs/blog/knn-query-elasticsearch), unlocking a huge amount of functionality within our query DSL. Additionally, we added the `int8_hnsw` index type for auto-quantized vectors, improved cosine similarity performance by normalizing vectors, enabled query phase parallelism within a single shard, and added byte quantization for float vectors in HNSW.

Elasticsearch 8.12 also leveraged Lucene 9.9, which added multi-threaded graph building and an [int8 scalar quantized](https://www.elastic.co/search-labs/blog/scalar-quantization-101) format.

## Elasticsearch 8.13

With Elasticsearch 8.13, we added `int8_flat` for flat storage of auto-quantized vectors, enabled multiple inner-hits for passage vector search, and further simplified the `knn` query by making `k` and `num_candidates` optional. Additionally, we launched [token pruning](https://www.elastic.co/search-labs/blog/text-expansion-pruning) to speed up sparse vector queries sparse models such as ELSER.

Elasticsearch 8.13 was shipped with Lucene 9.10, which included multi-segment HNSW graph search improvements.

## Elasticsearch 8.14

Elasticsearch 8.14 included NEON SIMD optimized native index operations for `int8_hnsw` indices, support for hex-encoded byte strings for byte vectors, defaulted dense vector fields to use `int8_hnsw`, and further enhanced the kNN query builder by adding `modelId` and `modelText`.

## Elasticsearch 8.15

And here we are at Elasticsearch 8.15 - a huge release that includes:

* Elasticearch 8.15 is now SIMD native optimized for index and search for `int8_hnsw` indices
* Adds [int4 scalar quantization](https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene) using `int4_hnsw` and `int4_flat` vectors
* Adds support for [bit vectors](https://www.elastic.co/search-labs/blog/bit-vectors-in-elasticsearch) for both hnsw and flat vectors, and added hamming distance for brute force search
* Introduces a new [`sparse_vector`](https://www.elastic.co/search-labs/blog/elasticsearch-sparse-vector-query) [query](https://www.elastic.co/search-labs/blog/elasticsearch-sparse-vector-query) to search sparse vectors with inference endpoints or precomputed query vectors
* Adds a new [semantic\_text](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text) field and [semantic query](https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-semantic-query.html) to make it easier than ever before to start using semantic search!

Elasticsearch 8.15 also ships with Lucene 9.11, which also has a ton of great optimizations:

* Improved speed from [Lucene madvise optimizations](https://www.elastic.co/search-labs/blog/lucene-and-java-moving-forward-together)
* Adds a new `VectorScorer` interface for better brute force scoring
* Includes optimized scalar quantiles to allow dynamic quantiles calculations
* Adds [int4 scalar quantization](https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene) & optimized SIMD code for int4 comparisons

## ... and beyond!

We're nowhere close to done, so make sure to check out all of the new features in 8.15 and serverless, and keep an eye on Search Labs to hear about all of our new features!

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