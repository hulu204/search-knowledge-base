---
title: 'Elasticsearch 9.3 adds bfloat16 vector support'
company: Elastic
tag: 索引构建
date: 2026-02-16
url: https://www.elastic.co/search-labs/blog/bfloat16-vector-support-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch 9.3 adds bfloat16 vector support

Exploring the new Elasticsearch element\_type: bfloat16, which can halve your vector data storage.

February 16, 2026

[Simon Cooper](/search-labs/author/simon-cooper)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Elasticsearch 9.3 brings with it several important improvements to vector data, including a new `element_type: bfloat16`. This has the potential to *halve* your vector data storage, with minimal reductions in recall and runtime performance for most use cases.

## Storage formats in dense\_vector fields

Prior to 9.3, `dense_vector` fields support vectors of single bits, 1-byte integers, and 4-byte floats. We store the original vectors on top of any quantization and/or hierarchical navigable small world (HNSW) graph used for indexing, and the original vectors make up the vast majority of the required disk space of the vector indices. If your vectors are floating point, then the only option versions of Elasticsearch prior to 9.3 provide is to store 4 bytes per vector value: That’s 4kB for a single 1024-dimensional vector.

There are other floating-point sizes available, of course: [IEEE-754](https://en.wikipedia.org/wiki/IEEE_754) specifies floating-point sizes of many different lengths, including the 4-byte `float32` and 8-byte `float64` used by Java `float` and `double` types. It also specifies a `float16` format, which only uses 2 bytes per value. However, this only has a maximum value of 65,504, compared to the 3.4x1038 of 4-byte `float32` values, and the conversion between the two involves several arithmetic operations.

As an alternative, many machine learning (ML) applications now use [bfloat16](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format), which is a modification of IEEE-754 `float32` to only use 2 bytes. It does this by discarding the lowest 2 bytes of the fractional part of the value, leaving the sign and exponent unchanged. This effectively reduces the precision of the floating-point value *without* a corresponding reduction in range. The conversion from `float32` to `bfloat16` is a simple bitwise truncation on the `float32` value, with a bit of jiggling to account for rounding.

![bfloat16](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc2f2b97b3d6911e6/6a170e2e67045b22db45c280/b0f8d88cfb8c696b8ef805424d7dc7a242023484-913x394.png)

[Source: Wikipedia](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format)

## bfloat16 in Elasticsearch 9.3

Elasticsearch 9.3 now supports storing vector element types as bfloat16. In memory, it will still process every vector value as a 4-byte float32, as Java does not have built-in support for bfloat16. As it writes vector data to disk, it will simply truncate and round each float32 value to a 2-byte bfloat16, and zero-expand each bfloat16 value back to float32 on reading the value into memory.

This effectively *halves* your vector index sizes, as it uses 2 bytes per value rather than 4 bytes. There may be a small performance cost during reading and writing data as Elasticsearch performs the necessary conversions, but this is often counterbalanced by a significant reduction in the I/O required, as the OS now has to read half as much data. And, for most datasets, there is a minimal effect on search recall.

As an example, this is the difference in sizes for bfloat16 on our `dense_vector` dataset:

![bfloat16 in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1570058a6fed8296/6a170e30b0367d770272bdb1/d7d2459cead1b8d29d107a1b6bbbe21be1fc7315-1600x990.png)

So, if your input vectors are already at bfloat16 precision, then happy days! Elasticsearch accepts raw bfloat16 vectors as float values, and as [Base64-encoded vectors](https://www.elastic.co/search-labs/blog/base64-encoded-strings-vector-ingestion). The vectors are persisted to disk with the same precision as your original source data, immediately halving your data storage requirements.

If your input vectors are at 4-byte precision, then you can also use bfloat16 format to halve your index data sizes. Elasticsearch will truncate and round each value to 2-byte precision, throwing away the least significant bits of the fraction. This means that the vector values you get back from Elasticsearch won’t be exactly the same as what you originally indexed, so don’t use bfloat16 if you need to maintain the full 4-byte precision of float32.

Starting in Elasticsearch 9.3, and on Elasticsearch Serverless, you can specify `element_type: bfloat16` with all `dense_vector` index types on any newly created indices. If you wish to use bfloat16 with existing indices, you can reindex into an index with `element_type: bfloat16` and Elasticsearch will automatically convert your existing float vectors to bfloat16.

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