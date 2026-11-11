---
title: 'Less merging and faster ingestion in Elasticsearch 8.11'
company: Elastic
tag: 索引构建
date: 2023-10-10
url: https://www.elastic.co/search-labs/blog/elasticsearch-8-11-indexing-buffer
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Less merging and faster ingestion in Elasticsearch 8.11

Discover how Elasticsearch 8.11 improved its indexing buffer, resulting in less segment merging and faster ingestion.

October 10, 2023

[Adrien Grand](/search-labs/author/adrien-grand)

[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

We made significant changes to how Elasticsearch 8.11 reclaims memory from its indexing buffer, which helps reduce the merging overhead and thus make indexing faster. Using our [Logging track](https://github.com/elastic/rally-tracks/tree/master/elastic/logs), we observed an 8% improvement in ingestion throughput with these changes when running with a 1GB heap.

## How indexing buffer works in Elasticsearch 8.10 and earlier

When indexing data, Elasticsearch starts building new segments in memory and writes index operations into a transaction log for durability. These in-memory segments eventually get serialized to disk, either when changes need to be made visible - an operation called "[refresh](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html)" in Elasticsearch, or when memory needs to be reclaimed. This blog focuses on the latter.

To manage memory of its indexing buffer, Elasticsearch keeps track of how much RAM is used across all shards on the local node. Whenever this amount of memory crosses the limit (10% of the heap size by default), it will identify the shard that uses the most memory and refresh it.

## How Elasticsearch 8.11 improved its indexing buffer

### Change 1: flush a single segment at a time

When changes get buffered in memory for a given shard, there is not a single pending segment. In order to be able to index concurrently, Lucene maintains a pool of pending segments. When a thread wants to index a new document, it picks a pending segment from this pool, updates it and then moves the pending segment back to the pool. If there is no free pending segment in the pool, a new one will be created. There are usually a number of pending segments in the pool which are in the order of the peak indexing concurrency.

The first change we applied was to update this logic to no longer flush all segments from a shard at once, and instead only flush the largest pending segment using Lucene's [`IndexWriter#flushNextBuffer()`](https://lucene.apache.org/core/9_8_0/core/org/apache/lucene/index/IndexWriter.html#flushNextBuffer()) API. This helps because the size of pending segments is generally not uniform, as Lucene has a bias towards updating the largest pending segments, so this new approach helps flush fewer segments, which should also be significantly larger. And since fewer segments get merged, less merging is required to keep the number of segments under control.

### Change 2: flush shards in a round-robin fashion

Managing a shared indexing buffer across many shards is a hard problem. The existing logic assumed that it would be sensible to pick the shard that uses the most memory for its indexing buffer as the next shard to reclaim memory from. After all, this is the most efficient way to buy some time until we reach the maximum amount of memory for the indexing buffer again. But on the other hand, this also penalizes shards that ingest most actively, as they would flush segments much more frequently than shards that have a modest ingestion rate. There are many moving parts here, which make it hard to get a good intuition about how these various factors play together and figure out the best strategy for picking the next shard to flush.

So we ran experiments with various approaches to picking the next shard to flush, and interestingly picking the largest shard was the worst one, significantly outperformed by picking shards at random. Actually, the only approach that slightly outperformed picking shards at random was to pick shards in a round-robin fashion. This is now the way how Elasticsearch picks the next shard to flush.

## Conclusion

These two changes should help reduce the merging overhead and speed up ingestion, especially with small heaps and field types that consume significant amounts of RAM in the indexing buffer like `text` and `match_only_text` fields, or field types that are expensive to merge like `dense_vector`. Enjoy the speedups!

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