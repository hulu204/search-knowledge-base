---
title: 'Introducing a new vector storage format: DiskBBQ'
company: Elastic
tag: 索引构建
date: 2025-10-23
url: https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Introducing a new vector storage format: DiskBBQ

Introducing DiskBBQ, an alternative to HNSW, and exploring when and why to use it.

October 23, 2025

[Benjamin Trent](/search-labs/author/benjamin-trent)[John Wagster](/search-labs/author/john-wagster)[Ignacio Vera Sequeiros](/search-labs/author/ignacio-vera-sequeiros)

[Inside Elastic](/search-labs/blog/category/inside-elastic)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

DiskBBQ is an evolution of an Inverted Vector File (IVF) index. It is an alternative to Hierarchical Navigable Small Worlds (HNSW), partitioning vectors into smaller clusters that can handle lower-memory scenarios more efficiently while providing nice query performance.

## What’s wrong with HNSW?

We absolutely love [HNSW](https://arxiv.org/abs/1603.09320). It’s a fast, compute-efficient algorithm that scales logarithmically to your vector data. However, that speed comes at a cost. For HNSW to work well, all the vectors need to reside in RAM. And while we have made this cheaper by adding increasingly better levels of quantization, we still have issues with vectors falling out of memory and performance plummeting.

Additionally, to index, you must search your existing HNSW graph. So all the memory costs that incur for RAM are also present during indexing. This can significantly slow down hardware that cannot fully hold the vectors in RAM.

## How is DiskBBQ different?

DiskBBQ uses [Hierarchical K-means](https://www.elastic.co/search-labs/blog/k-means-for-vector-indices) to partition vectors into small clusters. It then selects representative centroids to query before querying the individual vectors themselves. It takes advantage of the multi-layer nature of this hierarchy to query at most 2 layers of the centroids, limiting the total explored space. Finally, it explores the vectors contained in each cluster by bulk scoring the distance between the cluster’s vectors and the query vector.

![Example Hierarchical KMeans algorithm flow. Splitting sections of vectors, clustering each section, and recursively splitting until the desired partition size is reached.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6d5eb004f25325ae/6a17e9cb577262416a1bcc30/b696183be431dbc7c05c2aa2680fb9f7ef7809f7-600x600.gif)

Figure 0. Example Hierarchical KMeans algorithm flow. Splitting sections of vectors, clustering each section, and recursively splitting until the desired partition size is reached.

As the name implies, DiskBBQ also uses our [BBQ (Better Binary Quantization)](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) to reduce the size of the vectors and centroids. This allows loading many blocks of vectors into memory at a time for fast scoring, with very low memory requirements and low disk overhead.

Another interesting aspect of DiskBBQ is that it will allow vectors to be assigned to more than one centroid. It utilizes a version of Google’s [Spilling with Orthogonality-Amplified Residuals (SOAR)](https://research.google/blog/soar-new-algorithms-for-even-faster-vector-search-with-scann/) to assign vectors to multiple clusters, which is particularly beneficial when a vector is near a border between two clusters. Because vectors are quantized heavily, this adds minimal disk overhead and requires fewer centroids to be explored during search.

## Talk is cheap, show me some numbers

HNSW scales logarithmically. So, it must be many magnitudes faster than something that must search centroids and then score all vectors in each centroid, right?

We have been working hard to make DiskBBQ fully competitive with HNSW. While we are not yet 100% there in all situations, we are happy with the results.

DiskBBQ takes advantage of bulk scoring vectors and performs as many operations as it can off-heap. This means we can read vectors from files directly into memory for optimized vector operations, resulting in some pretty nice performance.

Two main scenarios for DiskBBQ are particularly interesting. The first is one where the entire index can fit in RAM. Since this is key for HNSW performance, it's only fair to see how DiskBBQ compares in this case.

| Type | Index Time | Latency | Recall |
| --- | --- | --- | --- |
| HNSW BBQ | 1,054,319ms | ~3.4ms | 92% |
| DiskBBQ | 94,075ms | ~4.0ms | 91% |

Table 0. How DiskBBQ compares over 1M vectors. All sitting comfortably in memory. DiskBBQ can be a whopping 10x faster at indexing speed while almost being as fast as HNSW over BBQ quantized vectors.

Things get more interesting when memory is increasingly reduced to where the entire index no longer fits in memory. We will have a separate blog digging into why DiskBBQ is better in low-memory and our methodology for testing. However, here are some high-level numbers:

![Index time in milliseconds vs. RAM / JVM Heap](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2570dc6ea6753cd3/6a17e9cc414c6461049451d2/da8217b490cdae71aaea758a784da3d74bb919ca-1370x860.png)

Figure 1: Shows index time in milliseconds vs. RAM / JVM Heap

As overall memory decreases, DiskBBQ indexing degrades gracefully. HNSW, however, simply falls apart once memory becomes very restricted.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd870881d5b299b1e/6a17e9ce4202297fed29f610/caf8c2e84050ef639fa0836a4343de70ef4ecf6d-1334x822.png)

Figure 2: Shows search latency in milliseconds vs. RAM / JVM Heap

Again, we see DiskBBQ degrading gracefully in search latency. Indeed, it starts to slow down, but HNSW latency begins to increase exponentially as memory becomes increasingly restricted.

## When should I use DiskBBQ?

DiskBBQ and HNSW will both continue to get improvements in Elasticsearch. For now, DiskBBQ’s performance for very high recall (99+%) and very low latency is not as good as HNSW. We hope to improve this while continuing to invest in HNSW.

If you need very, very high recall, have lots of off-heap memory (or are willing to pay for it), and have few index updates (so indexing costs are low), using HNSW with some form of quantization is likely still the best option.

However, if you are okay with 95% or less recall, are cost-sensitive, but still want fast search, DiskBBQ might be the solution for you.

## How can I use DiskBBQ?

Here's how to enable DiskBBQ and start querying:

Set up a mapping like this:

```
{
  "mappings": {
    "properties": {
       "image-vector": {
        "type": "dense_vector",
        "dims": 3,
        "similarity": "l2_norm",
        "index_options": {
          "type": "bbq_disk"
        }
      }
    }
  }
}
```

Insert a vector:

```
{ "image-vector": [0.0127, 0.1230, 0.3929] }
```

Here’s an example of querying out that vector:

```
{
  "query" : {
    "knn": {
      "field": "image-vector",
      "query_vector": [0.0127, 0.1230, 0.3929]
    }
  }
}
```

You can still use `num_candidates` to control approximation.

Here’s an example of querying out that vector:

```
{
  "query" : {
    "knn": {
      "field": "image-vector",
      "query_vector": [0.0127, 0.1230, 0.3929],
      "k": 10,
      "num_candidates": 50
    }
  }
}
```

Or, if you want more granular control over how many vectors the search will consider, you can set the `visit_percentage` directly.

Here’s an example of querying out that vector:

```
{
  "query" : {
    "knn": {
      "field": "image-vector",
      "query_vector": [0.0127, 0.1230, 0.3929],
      "k": 10,
      "visit_percentage": 10.0
    }
  }
}
```

Update Dec 2025: DiskBBQ is now GA in the Elastic Enterprise. [Try it out now on Elasticsearch Serverless](https://cloud.elastic.co/home)).

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