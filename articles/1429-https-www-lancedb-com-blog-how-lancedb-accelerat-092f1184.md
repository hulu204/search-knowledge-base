---
title: 'https://www.lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale
account: 
origin: en-rss
---
# How LanceDB Accelerates Vector Search at 10 Billion Scale

[Yang Cen](/author/yang-cen)

•

April 29, 2026

•

[Engineering](/category/engineering)

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-001](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Open source LanceDB already has a reputation for handling large-scale vector search well. On the surface, things look simple with a familiar table-and-query interface, but underneath runs a serious stack of indexing machinery: IVF-style partitioning, Product Quantization (PQ), RaBitQ quantization, full-precision reranking, and Lance’s columnar storage format for fast random access.

That stack is already enough for a wide range of production workloads. PQ shrinks the amount of vector data each query has to scan inside a partition. RaBitQ goes further for high-dimensional embeddings, turning residual vectors into compact binary codes and adding small corrective terms to preserve recall. On large datasets, these quantizers are the difference between scanning raw floating-point vectors and scanning a much smaller representation that still keeps the right candidates within reach.

But “large” keeps moving. A 100M-vector table and a 10B-vector table aren’t the same system problem. At 10B scale, parts of the query path that used to look negligible start showing up in profiles. Index build time, partition routing, per-query CPU work, and executor utilization all become first-order concerns.

## Where Open Source Indexing Starts to Strain

Open source LanceDB follows the same high-level query plan that most IVF-based ANN systems use:

1. Train centroids and assign vectors to partitions.
2. Search the nearest partitions for a query vector.
3. Run compressed-vector search inside those partitions.
4. Rerank a candidate set using the original vectors.

This works because it turns one giant nearest-neighbor problem into a small routing problem plus several local searches. The catch is, when the dataset grows, both sides of that split grow with it.

First, index creation takes longer. We have to train partition centroids, encode billions of vectors, write index files, and maintain enough metadata to keep the result queryable. Even when every individual step is efficient, the wall-clock build time gets painful once it all runs as one large job.

Second, partition sizing becomes a balancing act. Keep partitions too large, and each query does too much work after routing. Shrink them, and the number of partitions grows, which makes the first query step (finding the closest `nprobes` partitions) more expensive. At 10B scale, we tend to want both: enough partitions to keep local scans small, and fast routing so the query doesn’t spend too much time deciding where to search.

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-002](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-002.svg)

The practical bottleneck isn’t one algorithm in isolation. It’s the interaction between data scale, partition count, dimensionality, and how much parallel compute the system can actually use. This is where [LanceDB Enterprise](https://docs.lancedb.com/enterprise?__hstc=159041573.68aec8b828775ede573e2c637d5ceead.1777470608669.1777470608669.1777475681606.2&__hssc=159041573.1.1777475681606&__hsfp=a33be91ef96107f0448309952b033d00) picks up: it takes the same logical query plan and distributes it across a cluster, so index construction and query execution can each scale on their own.

## Splitting the Index into Segments

LanceDB Enterprise’s distributed indexing path starts by splitting the large table into index segments. Instead of treating a 10B-vector index as one monolithic artifact, we build multiple segment-level indexes, each covering a disjoint slice of the table.

That changes the operational shape of indexing. Each segment can be assigned to its own indexing worker, and many segments build in parallel across the cluster. The final table still exposes one logical index to the user, but the physical work is no longer bound to a single machine.

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-003](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-003.svg)

The important part is that this isn’t just “more threads.” It’s coarse-grained parallelism at the index-artifact level. The scheduler can launch independent segment builds, retry the ones that fail, and merge or commit segment metadata once each unit finishes. For large tables, that turns index build time from “one huge job” into “many bounded jobs,” which is far easier to scale and operate.

Segmented indexing also gives us a clean unit for distributed query execution. Each segment carries its own vector index and can sit close to a Plan Executor backed by a local SSD cache. The query layer fans out work to the executors that own the relevant segments and merges their partial answers into the final top-k.

## Querying Across Plan Executors

In the distributed query path, the query node acts as a coordinator. It plans the query, routes segment-level work to the Plan Executors that own the relevant segments, and merges the partial results they return.

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-004](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-004.svg)

This matters because vector search is a mix of CPU-heavy and I/O-heavy stages. Partition routing and compressed distance computation are CPU-bound. Candidate reranking and row retrieval need efficient access to stored vectors and payload columns. Spreading segment indexes across Plan Executors puts more CPU cores, more memory bandwidth, and more cache capacity to work at once.

From the user’s side, the API stays the same: a table search returning top-k. Underneath, the work is fanned out across index segments, where each segment searches its local partitions and the query node stitches the partial results back into a single ranked answer.

## HNSW over Centroids

The first step of an IVF-style search is to find the nearest `nprobes` partitions for a query. In a small index, scanning every centroid is cheap enough to ignore. In a 10B-vector index, the centroid set itself grows large enough that this routing step becomes a real cost.

LanceDB addresses this by building an HNSW graph over the IVF centroids at the query node. Instead of comparing the query against every centroid, graph search reaches the nearest clusters in only a few hops. Lance keeps a dedicated fast path for training HNSW over centroids when the centroid matrix is large enough. This is basically a way to speed up finding the nearest clusters in the vector indexing path.

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-005](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-005.svg)

At 10B scale, this is a major win. In our large-scale experiments, HNSW centroid routing cut the cost of the “find nearest partitions” stage substantially. That speedup matters because partition routing happens before any useful local search can begin. Slow routing means every executor starts late.

This is also why we treat centroid search as its own optimization target. The compressed scan inside a partition matters, but optimizing only the second half of the query isn’t enough. At very large scale, the routing layer also has to be approximate, cache-friendly, and fast.

The implementation lives in Lance’s vector index code, including the centroid speedup utilities and IVF `find_partitions` path: [vector utils](https://github.com/lance-format/lance/blob/main/rust/lance-index/src/vector/utils.rs) and [IVF storage](https://github.com/lance-format/lance/blob/main/rust/lance-index/src/vector/ivf.rs). Learn more about how LanceDB Enterprise uses compute-storage separation and distributed compute in the [architecture docs.](https://docs.lancedb.com/enterprise/architecture)

## Fast Rotation for RaBitQ

Routing is only half the query. Once HNSW has chosen the right `nprobes` partitions, each Plan Executor still has to scan them, comparing the query against the compressed vectors inside. At 10B scale, that scan is handled by RaBitQ, which adds its own per-query setup cost before any comparison can happen.

We touched on RaBitQ earlier; for the full mechanics, see our [previous post on RaBitQ quantization](https://www.lancedb.com/blog/feature-rabitq-quantization?__hstc=159041573.68aec8b828775ede573e2c637d5ceead.1777470608669.1777470608669.1777475681606.2&__hssc=159041573.1.1777475681606&__hsfp=a33be91ef96107f0448309952b033d00). One detail that matters here is that RaBitQ applies a random orthogonal rotation to vectors during indexing, which spreads information evenly across dimensions so that very compact binary codes can still preserve distances reliably. Stored codes therefore live in that rotated space, and every query vector has to pass through the same rotation before it can be compared. The straightforward implementation does this by multiplying the query vector by a dense rotation matrix.

For a vector of dimension `d`, that dense matrix multiplication is `O(d^2)`. At 768, 960, 1024, or higher dimensions, the cost piles up fast, and it has to be paid on every query.

LanceDB’s RaBitQ path adds a fast rotation mode for exactly this reason. Instead of materializing and multiplying by a dense orthogonal matrix, the fast path composes random sign flips, Fast Walsh-Hadamard Transform style mixing, and Kac-style pairwise mixing. The transform stays matrix-free, and the rotation cost drops to roughly `O(d log d)`.

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-006](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-006.svg)

The implementation exposes two rotation modes, `fast` and `matrix`, with `fast` as the default. The fast path lives in Lance’s RaBitQ rotation code: [bq/rotation.rs](https://github.com/lance-format/lance/blob/main/rust/lance-index/src/vector/bq/rotation.rs) .

The performance effect scales with dimensionality. On high-dimensional embeddings, fast rotation cuts the per-query RaBitQ preparation cost noticeably. Combined with binary dot products inside partitions, it makes RaBitQ a much better fit for the 10B-scale query path, where every micro-stage gets multiplied by high QPS.

## The Combined Architecture

The 10B-scale path isn’t a single trick. It’s a stack of changes that strip serial work out of every stage of the search pipeline:

| Layer | Bottleneck at 10B scale | LanceDB approach |
| --- | --- | --- |
| Index build | One huge index build takes too long | Split into segment-level index builds and distribute them |
| Query execution | One node can't access enough compute | Place segment indexes across Plan Executors and fan out work |
| Partition routing | Too many centroids to scan linearly | Build HNSW over centroids at the query node to find `nprobes` quickly |
| RaBitQ query prep | Dense rotation costs `O(d^2)` | Use fast rotation with `O(d log d)` cost |
| Candidate quality | Quantized search is approximate | Rerank candidates with full-precision vectors |

Together, these changes let LanceDB keep the user-facing API simple while the internal execution model scales out. Users still issue a vector search against a table. Underneath, LanceDB distributes indexing across the cluster, routes per-segment queries to Plan Executors, uses HNSW at the query node to skip linear centroid scans, applies fast RaBitQ rotation for high-dimensional vectors, and reranks the final candidates with full-precision vectors.

## Performance at 10B Scale

How does this architecture scale in practice? Here's what the numbers actually look like when we index and search 10 billion r‍andom vectors with 1536 float32 dimensions per vector (comparable to modern embedding sizes). The index is an IVF index with RaBitQ quantization, partitioned into 10 segments of 1B rows each.

### Distributed query execution

For queries, the 10 segments were distributed across 10 nodes, one segment per node. Each query was fanned out across all of them, examined 20 partitions per query, and returned the top 100 results.

| Query performance, topk=100, N=10B | | | |
| --- | --- | --- | --- |
| p50 | p95 | p99 |
| 18ms | 20ms | 21ms |

In this benchmark, we observed a **p99 of 21ms across a 10-billion-vector table**: not a per-segment number, but end-to-end query latency, with centroid routing at the query node, segment-level fan-out to Plan Executors, RaBitQ scanning inside partitions, and final reranking all on the critical path. Increasing throughput is simply a matter of adding more parallel workers, without changing the per-query latency profile.

### Distributed indexing

With 10 indexing workers, one per segment, the build runs about **5× faster** than the same job would on a single node. The parallel encoding stage scales near-linearly with workers. Smaller fixed costs (centroid training and final merge) stay constant, so wall-clock time tracks the slowest segment rather than the entire table.

## Conclusions

The result of LanceDB Enterprise's architecture is a vector search system that scales in both phases that matter: building the index and serving queries. Index construction runs as distributed work over bounded segments. Query execution fans out across Plan Executors. Routing, quantized search, and reranking each stay focused on the amount of data they actually need to touch.

This is the core point: LanceDB is built to *keep on scaling* as vector datasets grow, without changing how users query them. On large datasets, the architecture has already proven itself in production, while keeping the table-centric search experience users expect.

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-007](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-007.png)

[Yang Cen](/author/yang-cen)

Software Engineer @ LanceDB

[GitHub](https://github.com/BubbleCal)

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-008](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-008.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-009](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-009.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184-fig-010](../images/1429-https-www-lancedb-com-blog-how-lancedb-accelerat-092f1184/figure-010.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb