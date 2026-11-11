---
title: 'Improve search performance with `best_compression`'
company: Elastic
tag: 工程相关
date: 2026-01-23
url: https://www.elastic.co/search-labs/blog/improve-elasticsearch-performance-best-compression
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improve search performance with `best\_compression`

While `best\_compression` is typically seen as a storage-saving feature for Elastic Observability and Elastic Security use cases, this blog demonstrates its effectiveness as a performance-tuning lever for search.

January 23, 2026

[Sherry Ger](/search-labs/author/sherry-ger)[Ryan Eno](/search-labs/author/ryan-eno)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

When tuning Elasticsearch for high-concurrency workloads, the standard approach is to maximize RAM to keep the working set of documents in memory to achieve low search latency. Consequently, [`best_compression`](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules) is rarely considered for search workloads, as it is primarily viewed as a storage saving measure for Elastic Observability and Elastic Security use cases where storage efficiency takes priority.

In this blog, we demonstrate that when the dataset size significantly exceeds the OS page cache, `best_compression` improves search performance and resource efficiency by reducing the I/O bottleneck.

## **The setup**

Our use case is a high-concurrency search application running on [Elastic Cloud CPU optimized instances](https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/ec-change-hardware-profile#ec-profiles-compute-optimized-arm).

* Data volume: ~500 million documents
* Infrastructure: 6 Elastic Cloud (Elasticsearch service) instances (each instance: 1.76 TB storage | 60 GB RAM | 31.9 vCPU)
* Memory-to-storage ratio: ~5% of the total dataset fits into RAM

## **The symptoms: high latency**

We observed that when the number of current requests spiked around 19:00, the search latency deteriorated significantly. As shown in Figure 1 and Figure 2, while traffic peaked around 400 requests per minute per Elasticsearch instance, the average query service time degraded to over 60ms.

![Requests per minute per Elasticsearch peaked](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf8ab7de934d6b410/6a170440c1e8a58db3f881c1/f9c6cc1882e7db24336c65c54bbc1d38dcdb7fa3-697x311.png)

*Figure 1. Requests per minute per Elasticsearch instance peaked just after 19:00 at about 400.*

![Average query service time Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt32de2bed0afbacd5/6a1704422b835fa5ddf4b0e2/bbb705ae2fcd14c81d335bf322346caf3bf33765-996x618.png)

*Figure 2. The average query service time started to spike and climbed to and stayed at >60ms.*

The CPU usage remained relatively low after the initial connections handling, indicating that compute was not the bottleneck.

![Elasticsearch CPU usage](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta5b45d4a1ff48f54/6a17044447d49cd7252d88af/cec15a28d2d22e9adedd2951bb2334b3717890a1-1494x730.png)

*Figure 3. After the initial jump, CPU usage remains relatively low.*

A strong correlation emerged between query volume and page faults. As requests increased, we observed a proportional rise in page faults, peaking around 400k/minute. This indicated that the active dataset could not fit in the page cache.

![Number of page faults Elasticsearch performance](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd0a3d0c610700bdb/6a17044560084b6f403c4459/511f2f10300a9d10ba3d7a82b9a8c8d567ac5636-1492x678.png)

*Figure 4. The number of page faults was high, peaking around 400k/minute.*

Simultaneously, the JVM heap usage appeared to be normal and healthy. This ruled out garbage collection issues and confirmed the bottleneck was I/O.

![Heap usage in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3f888a03ce78eb04/6a170448964cea401008ba59/336bbad638f866304358dba1d06ee987de0f23cf-1490x568.png)

*Figure 5. Heap usage remained flat.*

## **The diagnosis: I/O bound**

The system was I/O bound. [Elasticsearch relies on the OS page cache to serve index data from memory](https://www.elastic.co/blog/elasticsearch-caching-deep-dive-boosting-query-speed-one-cache-at-a-time). When the index is too large for the cache, queries trigger expensive disk reads. While the typical solution is to scale horizontally (add nodes/RAM), we wanted to exhaust efficiency improvements on our existing resources first.

## **The fix**

By default, Elasticsearch uses [LZ4](https://en.wikipedia.org/wiki/LZ4_(compression_algorithm)) compression for its index segments, striking a balance between speed and size. We hypothesized that switching to `best_compression` (which uses [zstd](https://en.wikipedia.org/wiki/Zstd)) would reduce the size of indices. A smaller footprint allows a larger percentage of the index to fit in the page cache, trading a negligible increase in CPU (for decompression) for a reduction in disk I/O.

To enable `best_compression`, we reindexed the data with the index setting `index.codec: best_compression`. Alternatively, the same result could be achieved by closing the index, resetting the index codec to `best_compression`, and then performing a segment merge.

```
POST my-index/_close
PUT my-index/_settings
{
    "codec": "best_compression"
}
  
POST my-index/_open  
POST my-index/_forcemerge?max_num_segments=1
```

## **The results**

The results confirmed our hypothesis: improved storage efficiency directly translated into a substantial boost in search performance with no accompanying increase in CPU utilization.

Applying `best_compression` reduced the index size by approximately 25%. While less than the reduction seen in repetitive log data, this 25% reduction effectively increased our page cache capacity by the same margin.

During the next load test (starting at 17:00), the traffic was even higher, peaking at 500 requests per minute per Elasticsearch node.

![Load test in Elaticserach](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta61ab3bd5ded5716/6a170449a6c2b9f711e795dd/fc1902f396cb2115c0013155ad07f6eb87389c60-660x309.png)

*Figure 6. The load test started around 17:00.*

Despite the higher load, the CPU utilization was lower than in the previous run. The elevated usage in the earlier test was likely due to the overhead of excessive page fault handling and disk I/O management.

![Elasticsearch CPU utilization performance improvement with best_compression](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9fd1a44b02a4f787/6a17044b2b835ff996f4b0e6/15699ef4c65b3f0a9f8a3e1bae8bb18f7b647025-819x352.png)

*Figure 7. CPU utilization was lower than the previous run.*

Crucially, page faults dropped significantly. Even at higher throughput, faults hovered around <200k per minute, compared to >300k in the baseline test.

![Number of page faults Elasticsearch performance improvement with best_compression](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltef0c621d76767115/6a17044c2b835fe49ef4b0ea/f76ca967976d740af88a9359b66041701abb46fc-764x340.png)

*Figure 8. Number of page faults saw a significant improvement.*

Although the page fault results were still less than optimal, query service time was cut by about 50%, hovering below 30ms even under heavier load.

![Average query service time performance improvement in Elasticsearch with best_compression](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6579b3d005d04101/6a17044e66c4f9179cf8bf13/750ec1c59b8eb5069aed4c066d856ecea82d5bca-620x311.png)

*Figure 9. Average query service time was <30ms.*

## **The conclusion: best\_compression for search**

For search use cases where data volume exceeds available physical memory, `best_compression` is a potent performance-tuning lever.

The conventional solution to cache misses is to scale out to increase RAM. However, by reducing the index footprint, we achieved the same goal: maximizing the document count in the page cache. Our next step is to explore [**index sorting**](https://www.elastic.co/blog/space-savings-a-lesser-known-benefit-of-index-sorting-in-elasticsearch) to further optimize storage and squeeze even more performance out of our existing resources.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter