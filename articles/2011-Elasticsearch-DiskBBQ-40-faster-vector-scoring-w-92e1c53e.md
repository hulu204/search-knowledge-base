---
title: 'Elasticsearch DiskBBQ: 40% faster vector scoring with native SIMD Blocks'
company: Elastic
tag: 工程相关
date: 2026-06-02
url: https://www.elastic.co/search-labs/blog/vector-search-diskbbq-simd-block-scoring
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch DiskBBQ: 40% faster vector scoring with native SIMD Blocks

A deep dive into how DiskBBQ's block layout, doc ID compression modes and native SIMD kernels combine to deliver 40% improved vector scoring throughput for DiskBBQ in 9.4.

June 02, 2026

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

[Elasticsearch DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction) already speeds up [Better Binary Quantization (BBQ)](https://www.elastic.co/search-labs/blog/optimized-scalar-quantization-elasticsearch) vector operations through block-based layouts. Elasticsearch 9.4 adds [native single instruction, multiple data (SIMD) kernels](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine) that improve throughput to almost 3x from single vector operations. Here’s how the format works.

DiskBBQ reads vector bytes directly from memory-mapped index files using dense, sequential block layouts. This keeps heap usage low and allows the engine to operate on datasets much larger than available RAM. Within these block layouts, DiskBBQ encodes doc ID blocks to reduce disk space while keeping decoding costs low. Here we walk through the posting list layout, doc ID packing modes, and why bulk scoring is fast.

## How DiskBBQ stores vector posting lists on disk

At the start of each posting list, we write a centroid score correction, the vector count, and the overall doc ID encoding method. Then we write doc IDs and vectors in subsequent blocks. The blocks and the internals are in ascending doc ID order. This respects segment doc ID order, which preserves [index sort order](https://www.elastic.co/docs/reference/elasticsearch/index-settings/sorting). Filters aligned with that order are more likely to include or exclude whole blocks at a time. After the doc IDs, we store the quantized vector bytes and then all the corrections for the vectors in that block.

![Diagram showing the structure of a posting list with labeled sections for metadata, document IDs, quantized vectors, and correction columns. The top box lists centroid correction, vector count, and document encoding. Below it, block 0 includes docIDs, quantized vectors, and correction columns labeled lower, upper, comp_sum, and additional. A dashed box at the bottom indicates continuation through block N and tail.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5211c9277fc7c524/6a4775b8b88cd15a3e63277d/ed2568c5a1a0a0b11470a12c40224161c3906703-1887x1077.png)

The layout of a posting list. Starting with a metadata header and then each block. The blocks have `bulk_size` doc IDs, and then quantized vector bytes, followed up by the quantized correction values.

## How DiskBBQ compresses doc IDs to reduce disk space

To ensure fast decoding of doc ID blocks, DiskBBQ encodes every block with the same encoding format. DiskBBQ computes the required encoding for each block and then uses the most space-expensive encoding required by any block for the posting list, which is used for all the document blocks. At the time of writing, there are five compression options for doc ID storage. Each option starts with a full [delta encoding](https://en.wikipedia.org/wiki/Delta_encoding) of the doc ID values. Then one of the following encoding types is applied on top of the delta encoded doc IDs.

| Encoding type | Condition | Bytes saved (example) |
| --- | --- | --- |
| Continuous | IDs are sequential (max−min+1 == len) | 16 bytes → 4 bytes |
| Delta 16 | All deltas fit in 16 bits | 64 bytes → 33 bytes |
| 21 bits per value | Values fit in 21 bits | 12 bytes → 8 bytes |
| 24 bits per value | Values fit in 24 bits | 64 bytes → 48 bytes |
| Fallback (full int) | Any other case | No reduction |

The most efficient is continuous. This is used when `max(doc_block) - min(doc_block) + 1 == len(doc_block)`, meaning, the delta encoding only needs to worry about storing the minimum value, and the doc IDs can be reconstituted by adding one to each subsequent value. An example would be the IDs `[4858192, 4858193, 4858194, 4858195]`. Instead of writing four individual `int` values, which is 16 bytes, we only need to write a single value: `4858192`.

![Diagram showing continuous document identifiers represented as blue boxes labeled doc0 through doc3, followed by an arrow pointing to green boxes labeled VInt and byte. Text above indicates conversion from continuous doc_ids to a single variable integer value for the minimum document ID.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9938bb76577efced/6a4775bacbd14e549ba13b92/a6afc046f60ac52500c419740ef55d92cc0f91ef-1523x194.png)

Continuous encoding; only needs to write a single integer.

Next is *delta 16*. It applies when every delta fits in 16 bits, which can be stored in two bytes. Assume we have `doc_ids = [1000, 1003, 1010, 1020, 1041, 1055, 1070, 1090, 1100, 1125, 1200, 1300, 2000, 4000, 16000, 66000]`. This then means our `min = 1000` and results in `deltas = [0, 3, 10, 20, 41, 55, 70, 90, 100, 125, 200, 300, 1000, 3000, 15000, 65000]`. These 16 deltas can be packed into eight int32 values (32 bytes), plus the min value, cutting the byte usage by almost 2x.

![Diagram showing a data encoding process with three color‑coded sections. On the left, green boxes labeled min, VInt, and ellipsis represent writing a minimum document value. In the center, two rows of blue boxes are marked as source delta bytes. Each row has an arrow pointing to orange boxes on the right with the same labels, illustrating packing of two 16‑bit deltas into each 32‑bit integer.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbe9a4dcff00922e4/6a4775bdde97777e4cca63a1/4214992c802f1e73d02e02668a6b6cb8b71064d8-1490x276.png)

Delta 16; writes the minimum value and then packs two 16-bit deltas into each 32-bit integer.

The next step up is 21 bits per value. This results in a fairly complex scheme where each triplet set of values is compressed into 64 bit values and a tail of 3 bytes for any remaining values. A concrete example would be `doc_ids=[1000, 70000, 140000]`, which get compressed into a single 64 bit value `doc0 | (doc1 << 21) | (doc2 << 42)`, the end result being three raw integer values, which comprise 12 bytes, get compressed into 8 bytes.

![Diagram showing blue boxes labeled with letter‑number ranges representing source list ranges. Arrows point to two sets of purple boxes labeled encoded set #0 bytes and encoded set #1 bytes, each containing grouped values like A20..13 and B20..13. Notes on the right explain that the byte blocks are not byte‑aligned and that tail parts of three documents are packed into one 64‑bit word.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt09495b81494f1142/6a4775c0eeb0e2f61a59140b/56b58dc26205eb25a3d4e6f9fd8933e6036ee7f4-2048x176.png)

Twenty-one bits per value, a fairly complex scheme combining triplet compressed 64-bit values with a 3-byte tail.

The second-to-last compression option packs integer values that require at most 24 bits. Since an `int` requires 32 bits of space, 24 leaves an entire byte completely unused. We cannot leave a single byte of real estate to waste. We want to fully fill as many bytes as we can, so this scheme compresses by filling in that empty byte. For example, `docs_ids = [1000, 70000, 140000, 300000, 500000, 800000, 1000000, 1300000, 1600000, 1900000, 2200000, 3000000, 4000000, 8000000, 12000000, 16000000]` will compress the final four integer values into the “free byte” in the prior integers, thus storing 16 integers, which usually cost 64 bytes, into 48 bytes.

![Diagram showing two rows of colored boxes representing source value bytes and their reordered form in an encoded integer. The top row is labeled “source value bytes,” and the bottom row “encoded int #0,” illustrating how multiple byte groups are packed together for 24‑bit values.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb936bb04df43189a/6a4775c3bfe8a230644da179/8be1e58e0d83a6c002aeb9afcb9fb03bbeea0258-1384x286.png)

This shows an example 24 bits per value where the final set of bytes is packed in the first. It’s taking advantage of that free byte of real estate.

The final option is the fallback. DiskBBQ will store each doc ID as a full fidelity integer, providing no disk reduction. Given that the doc ID values are delta encoded before compression, the fallback is exceptionally rare.

## Why DiskBBQ bulk scoring is faster: SIMD and CPU cache saturation

Storing the vectors in blocks allows [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data)-optimized bulk scoring. This keeps CPU cache lines saturated with vector bytes and allows quantization corrections to be applied with SIMD-optimized kernels. If vectors were stored inline with their corrections, after each vector score, the corrections would have to be applied. This loses valuable throughput and any opportunity for optimizing the correction application.

Here’s a benchmark showing how the throughput improves with different optimizations. This is a [JMH benchmark](https://github.com/openjdk/jmh) run on an M1Max MacBook with Java 25. The vector dimensions were 1024, and each operation in the benchmark was 10 queries executed over 10 blocks of 32 vectors.

```
Benchmark           (bits)  (dims)  (similarityFunction)   Mode  Cnt   Score   Error   Units
Float32Scalar            1    1024           DOT_PRODUCT  thrpt    5   0.348 ± 0.014  ops/ms
Float32PanamaVector      1    1024           DOT_PRODUCT  thrpt    5   1.106 ± 0.043  ops/ms
BBQIndividual            1    1024           DOT_PRODUCT  thrpt    5   8.420 ± 0.180  ops/ms
BBQBulkPartial           1    1024           DOT_PRODUCT  thrpt    5  15.306 ± 0.757  ops/ms
BBQBULK                  1    1024           DOT_PRODUCT  thrpt    5  16.672 ± 0.572  ops/ms
BBQBulkNative            1    1024           DOT_PRODUCT  thrpt    5  23.258 ± 2.273  ops/ms
```

Here’s a description of each of the benchmarks run above:

* Float32Scalar: This is the pure JVM doing floating point operations. No hand-optimized SIMD.
* Float32PanamaVector: Here some SIMD-optimized code paths are actually written and used.
* BBQIndividual: These are the individual bit-wise BBQ operations. Each vector is taken onto the JVM heap individually and scored and corrected.
* BBQBulkPartial: This is off-heap bulk scoring with [Panama Vector](https://openjdk.org/jeps/537) operations reading directly from MMAP’d file segments. The corrections are then applied on the JVM Heap.
* BBQBULK: This is full off-heap bulk scoring where vectors and corrections are SIMD-optimized Java Vector API functions reading directly from MMAP files.
* BBQBulkNative: This is what’s in Elasticsearch 9.4. Full native bulk vector operations reading bytes directly from the index files.

These results show the evolution of throughput, starting with the bare minimum of individual floating point operations. Switching to SIMD (hand-optimized with the Vector API) for floating point increases throughput ~3x, but even then, it's slower than the auto-vectorized individual bit-wise operations in BBQ. Then, the switch to bulk scoring almost increases BBQ throughput by 2x. Adding our new [optimized native SIMD kernels](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine) in Elasticsearch 9.4, we get yet another significant improvement, adding up to almost 3x improvement from individual bitwise scoring and an incredible 66x improvement over float32 operations.

![Animated diagram showing the bulk scoring path in Elasticsearch DiskBBQ. It includes a query vector, document vectors labeled v0–v7, correction operations (lower, upper, sum, add), and resulting scores, illustrating how the query vector and block of document vectors pass through SIMD‑optimized correction steps to produce scores.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltef5d5b518de95b99/6a4775c6569c0d0c6725bba2/22f822b84637622e4720257f73913d4362cb77d0-1631x707.gif)

This shows the typical bulk scoring path. The query vector calculates initial score information for every vector in the block and then applies each correction with an optimized SIMD block operation.

![Animated diagram showing the typical single scoring path. It displays a query vector, document vectors labeled v0–v7, correction steps labeled lower, upper, sum, and add, and resulting scores, reflecting how each vector is scored individually and its corrections applied sequentially.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcf6a436db9c4acbd/6a4775c9cbd40e59b2f56f1f/75df9d1ba3f3b986a31c4ed1bf6cc8b8c8ed54cc-1149x681.gif)

Here’s the typical single scoring path. Each vector is scored and then its corrections applied. This means that vector bytes don’t get to saturate CPU cache, and correction applications cannot be applied with the same SIMD block operation.

## DiskBBQ vector search performance: what native SIMD means in practice

Native SIMD kernels in Elasticsearch 9.4 deliver nearly 3x faster BBQ vector scoring and 66x the throughput of float32 operations. We aren’t done; there are always ways to improve, but this native SIMD block scoring pattern works well on all CPU architectures, allowing DiskBBQ to be fast no matter where it's deployed.

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