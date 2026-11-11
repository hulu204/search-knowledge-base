---
title: 'Apache Lucene 2025 wrap-up'
company: Elastic
tag: 工程相关
date: 2026-01-28
url: https://www.elastic.co/search-labs/blog/apache-lucene-wrapped-2025
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Apache Lucene 2025 wrap-up

2025 was a stellar year for Apache Lucene; here are our highlights.

January 28, 2026

[Benjamin Trent](/search-labs/author/benjamin-trent)[Chris Hegarty](/search-labs/author/chris-hegarty)

[Lucene](/search-labs/blog/category/lucene)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

It’s hard to believe that Apache Lucene has been around for over a quarter of a century! Yes, more than 25 years of search enabled through Apache Lucene.

## Community by the numbers

For contributions and the community as a whole, 2025 was another strong year, with 1,756 commits and 1,080 pull requests from 134 unique contributors. The community continued to grow this year, increasing the number of contributors by 98 from the previous year. The project management committee (PMC) and committer cohort also increased. Apache Lucene added nine new committers in 2025, one of whom was Elastic’s own Simon Cooper. (Congratulations, [thecoop](https://github.com/thecoop)!) The PMC also welcomed two new members. Our little community continues to grow.

## Our highlights

With almost 2,000 commits and eight releases, it’s difficult to summarize all the things that we loved from the year in Apache Lucene. But, not hiding from a challenge, here are some of our highlights.

## The year of faster queries

In many ways, 2025 was the year Apache Lucene embraced better auto-vectorization, manual [SIMD](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) optimizations, and overall making things go faster. Lucene community member [Adrien Grand goes into great detail in this blog](https://jpountz.github.io/2025/08/28/compiled-vs-vectorized-search-engine-edition.html), and below are links and summaries for the biggest jumps. As always, a huge shout-out to [Mike McCandless](https://github.com/mikemccand) for maintaining the [Apache Lucene Benchmarks for years](https://benchmarks.mikemccandless.com/AndHighHigh.html).

![Apache Lucene faster queries](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0f0340a8b161cb65/6a1701cd14b2704bdde3c4d4/bff3742a2d3fd0e61a75785a4f6c79e1a3dcd94d-1600x613.png)

* `[IN]` [Refactor main top-n bulk scorers to evaluate hits in a more term-at-a-time fashion](https://github.com/apache/lucene/pull/14701)
* `[IS]` Irrelevant hardware update, so it’s just noise here
* `[IY]` [Use branchless way to speedup filterCompetitiveHits](https://github.com/apache/lucene/pull/14906)
* `[IZ]` [Improve collecting docs stored as bitsets](https://github.com/apache/lucene/pull/14935)
* `[JA]` [Vectorize filterCompetitiveHits by hand with the Java Panama API](https://github.com/apache/lucene/pull/14896)
* `[JK]` [Increase the document block size to 256](https://github.com/apache/lucene/pull/15160)

Discounting the hardware change `[IS]`, this is almost a 60% increase in query speed in 2025, going from <100 queries per second (qps) to >170 qps.

## Vector search

There were a number of vector search improvements in 2025. Three to highlight are improving filtered [vector search with ACORN](https://github.com/apache/lucene/pull/14160), [adding optimistic multisegment search](https://github.com/apache/lucene/pull/14226), and [bulk scoring of vectors](https://github.com/apache/lucene/pull/14978).

[ACORN-1](https://arxiv.org/pdf/2403.04871) is an interesting algorithm for graph-based vector indices. It has the significant benefit of being filter and algorithm-agnostic. Since Apache Lucene uses hierarchical navigable small world (HNSW) for its indexing and users generally want to just filter on anything and everything without additional configuration, it’s a perfect fit. A community [member originally investigated](https://github.com/apache/lucene/pull/14085) adding this algorithm. (He has since been hired by Elastic. Hi, [Ben!](https://github.com/benchaplin) 👋👋👋) A nice balance was found for Lucene, providing faster filtered vector search without requiring significant work by the user in configuration and no additional indexing of information.

The addition of [optimistic multisegment vector search](https://github.com/apache/lucene/pull/14226) to Apache Lucene really highlights how the community comes together to make it all happen. Three different individuals combined powers to debug, benchmark, design, and iterate on this solution. Originally proposed by [Michael Sokolov](https://github.com/msokolov) (a vector search superstar in the Lucene community), it immediately caught my attention, too, because it claimed to fix our [weird concurrency consistency bug](https://github.com/apache/lucene/issues/14180) without sacrificing performance. With some iteration and benchmarking by fellow community member [Dzung Bui](https://github.com/dungba88), we were able to strike the right balance in speed and recall, improving performance, making multithreaded searches consistent, and implementing a pretty neat algorithm.

Bulk scoring was born out of a collaboration between community member [Trevor McCulloch](https://github.com/mccullocht) and our very own [Chris Hegarty](https://github.com/ChrisHegarty) and was introduced as a new scoring interface in [PR #14978](https://github.com/apache/lucene/pull/14978), with an initial float32 implementation following in [PR #14980](https://github.com/apache/lucene/pull/14980). Modern vector search involves thousands or even millions of comparisons as a query vector is evaluated against vectors in the index, often by traversing a graph of nearest neighbors. Traditionally, these comparisons are performed one vector at a time. Bulk scoring inverts that model by passing a batch of vectors, represented as ordinals in the index, to the scorer in a single call. This allows the scorer to prefetch and pipeline work across vectors, amortizing cache misses and reducing per-vector overhead. An exciting aspect of the original design discussion considered bulk scorers implemented in Rust and C. While Lucene itself remains a Java library, this opens the door to highly optimized, SIMD-friendly, native implementations.

We didn’t even get to talk about several other improvements that landed in this area, including HNSW optimizations, like more compact [GroupVarInt graph](https://github.com/apache/lucene/pull/14932) encoding, bypassing graph construction for [tiny segments](https://github.com/apache/lucene/pull/14963), and continued reductions in memory footprint. On the operations side, Lucene now [exposes off-heap memory requirements](https://github.com/apache/lucene/pull/14426), making it easier to understand and debug native memory usage. While these changes are small(ish) individually, together they help make Lucene’s vector search faster, leaner, and easier to operate in production.

## Bonus

The last highlight is a little out of place. It's a particularly [frustrating but satisfying bug fix](https://github.com/apache/lucene/pull/15380). I won’t go into deep details here, as it touches on how Lucene does max scoring and bulk scoring, applies filters, and handles all its internal iterator state. This deserves its own blog post. In short, we ran into this bug in production in late September 2025. It was surfacing as an `EndOfFileException` during a specific query execution. And then, like all fun bugs, it took a week or two of work to reproduce and fully debug. Finally, when we knew what exactly caused the exception to throw, we then had to dig into why to fix it. All in all, a month’s worth of work summarized in one line of code. Bask in its glory:

```
- top.doc = top.approximation.advance(filter.doc);
+ // Must use the iterator as `top` might be a two-phase iterator
+ top.doc = top.iterator.advance(filter.doc);
```

## Goodbye 2025, hello 2026

A big thank you to everyone in the Apache Lucene community who worked tirelessly to improve this venerable search library. We ❤️ you.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt762b38f91bd71c8e/6a170db8b339d547bb76a048/368db71c500e72d20fe225fe44c2c40231e29765-721x420.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Bringing maximum-inner-product into Lucene

September 01, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9ec7a04e3bdbfd9f/6a467b337eb22d59efdfc54d/c07100b6fcc74dba250e6853b1c5ef1edabbedfc-1920x1080.png)

[Lucene](/search-labs/blog/category/lucene)[Index Data](/search-labs/blog/category/index-data)

### How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage

June 12, 2026|[Alan Woodward](/search-labs/author/alan-woodward)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf9fcbf843affc566/6a1706b8964ceaea3208bab9/7884e35f40c15fe349379ef7ae4648b21708962f-1070x712.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Concurrency bugs in Lucene: How to fix optimistic concurrency failures

February 07, 2025|[Benjamin Trent](/search-labs/author/benjamin-trent)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter