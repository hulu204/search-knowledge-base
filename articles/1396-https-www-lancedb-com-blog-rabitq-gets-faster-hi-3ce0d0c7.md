---
title: 'https://www.lancedb.com/blog/rabitq-gets-faster-higher-recall-lower-latency-query-time-control'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/rabitq-gets-faster-higher-recall-lower-latency-query-time-control
account: 
origin: en-rss
---
# RaBitQ Gets Faster: Higher Recall, Lower Latency, Query-Time Control

[Yang Cen](/author/yang-cen)

•

July 10, 2026

•

[Engineering](/category/engineering)

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-001](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Vector search usually makes you choose where to pay: lower latency, higher recall, a smaller memory footprint, or fewer index rebuilds. Improving one tends to cost you another. The latest RaBitQ improvements in LanceDB shift that tradeoff in your favor: [`IVF_RQ`](https://www.lancedb.com/blog/feature-rabitq-quantization) can now deliver much higher recall than [`IVF_PQ`](https://www.lancedb.com/blog/benchmarking-lancedb-92b01032874a-2), and it does so without falling back to the slow, memory-hungry step that high-recall search has usually depended on.

In case you’re new to RaBitQ, here’s the quick background. To keep vector search fast and memory-light, LanceDB stores compressed (quantized) copies of your vectors instead of the full-precision originals. Compression saves a lot of space, but it loses some detail, so to hit high recall you’d typically add a *refine* step: re-check the top candidates against the original full-precision vectors to fix up the ranking. That works, but it means keeping those bulky raw vectors close to the search path, which costs memory and adds latency.

In this post, we describe the latest improvements to RaBitQ that let `IVF_RQ` reach high recall using richer compressed codes on their own, so most queries never need that refine step at all.

In our single-core benchmark with `top-k=10`, `nprobes=24`, and no raw-vector refine, multi-bit `IVF_RQ` reaches up to **96.8% recall@10** (that is, it recovers nearly 97% of the exact-search top 10 results), with up to **3.3x higher QPS per core** and up to **3.1x lower p99 latency** than `IVF_PQ` without refine.

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-002](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-002.png)

p99 latency comparison

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-003](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-003.png)

QPS per core comparison

‍

| Index | Recall@10 | Avg latency | p99 latency | QPS/core |
| --- | --- | --- | --- | --- |
| `IVF_PQ`, no refine | 74.8% | 12.8 ms | 14.7 ms | 78.0 |
| `IVF_RQ`, 3-bit | 93.5% | 3.8 ms | 4.7 ms | 261.0 |
| `IVF_RQ`, 5-bit | 96.2% | 4.6 ms | 5.6 ms | 218.1 |
| `IVF_RQ`, 7-bit | 96.8% | 5.0 ms | 5.9 ms | 200.7 |

A quick note on the numbers: QPS here is **QPS per core**, not total system throughput. We’re isolating the single-core search path, not describing the maximum throughput of a full LanceDB deployment.

The story is bigger than speed alone, though. `IVF_RQ` moves the whole operating point: 5-bit `IVF_RQ` reaches **96.2% recall@10** at about **2.6x lower p99 latency** than unrefined `IVF_PQ`, and the 5-bit and 7-bit variants improve recall by **21.4** and **22.0 points** respectively. Higher recall and lower latency at the same time, from the same compressed index.

## Why This Matters

Most production embedding models are high-dimensional, and raw f32 vectors are large even before you account for metadata, payload columns, and index overhead. At production scale, keeping those raw vectors in the hot search path gets expensive.

`IVF_PQ` is compact and useful, but reaching high recall often depends on a refine step: search the compressed PQ index, fetch extra candidates, and rerank them against the original full-precision vectors. Refine recovers quality, but the raw vectors are large, and keeping them around adds memory, I/O, and tail-latency pressure.

`IVF_RQ` takes a different path. Multi-bit RaBitQ preserves more distance information in the quantized index itself, so LanceDB can rerank with those compact multi-bit codes and reach high recall without depending on raw full-precision vectors for every high-recall query.

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-004](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-004.png)

Recall comparison: IVF\_PQ vs. IVF\_RQ

The memory tradeoff is worth spelling out. A 5-bit `IVF_RQ` index stores more quantized code data than a 1-bit path or a small PQ code, so it isn’t automatically the smallest index on disk. The advantage shows up when you ask for high recall: `IVF_PQ` often needs raw vectors for refine to reach similar recall, while `IVF_RQ` can spend a few more compact bits inside the index and avoid keeping those raw vectors hot.

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-005](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-005.png)

Hot serving memory comparison: IVF\_PQ vs. IVF\_RQ

| Serving path | What needs to be hot | Relative hot vector memory |
| --- | --- | --- |
| `IVF_PQ`, no refine | PQ codes only | ~1/32 raw vectors |
| 5-bit `IVF_RQ`, `approx_mode="fast"` | 1-bit RaBitQ search path | ~1/32 raw vectors |
| 5-bit `IVF_RQ`, multi-bit scoring | 5-bit RaBitQ codes | ~5/32 raw vectors |
| `IVF_PQ` + refine | PQ codes plus raw vectors | ~33/32 raw vectors |

There’s a useful nuance here. Because `approx_mode` exists, a 5-bit `IVF_RQ` index can theoretically search using only the 1-bit path in `fast` mode. In that case, hot search memory can match a 1-bit or no-refine PQ setup. The same index can then draw on its extra stored bits for higher recall when a query needs it.

## What Changed Under the Hood

[RaBitQ isn’t new to LanceDB](https://www.lancedb.com/blog/feature-rabitq-quantization), but this update makes it far more practical for high-recall serving. The following four pieces matter the most.

### Fast Rotation

RaBitQ rotates vectors before quantization so that information spreads more evenly across dimensions. A naive dense rotation can get expensive on modern high-dimensional embeddings, so LanceDB uses a fast rotation path that cuts that setup cost. Queries get prepared for RaBitQ scoring without rotation becoming the bottleneck.

The upshot for users: `IVF_RQ` stays fast on the embedding sizes people actually deploy.

### Multi-Bit Reranking

Classic one-bit RaBitQ is extremely compact. Multi-bit RaBitQ keeps more information per dimension, which gives the index a closer approximation of the original vector, and LanceDB uses those extra bits to rerank candidates inside the compressed index.

That’s why the 3-bit, 5-bit, and 7-bit rows look so different from the PQ no-refine row. The index itself holds enough distance information to sharply improve recall, without forcing every query into raw-vector refinement.

### SIMD Kernels

The hot path in vector search is scoring many candidate vectors quickly. LanceDB added SIMD kernels for RaBitQ scoring so CPUs can chew through packed quantized data efficiently. This is the kind of improvement you shouldn’t have to think about: upgrade the engine, keep the same table and search model, and the inner loop just gets faster.

### A Fast One-Bit Path

The last piece is the one-bit path. Even when an index stores more than one bit per dimension, LanceDB can fall back to a cheaper path when a query is latency-sensitive. This is what makes the memory story above work: one 5-bit index can serve both a low-latency path and a higher-recall path.

## Tune Recall at Query Time

The new user-facing control is `approx_mode`. Instead of rebuilding indexes for every product requirement, you build one `IVF_RQ` index and pick the recall/performance point at query time.

| `approx_mode` | What it optimizes for | Good fit |
| --- | --- | --- |
| `fast` | Lowest latency and the 1-bit hot path | autocomplete, previews, broad exploration |
| `normal` | Balanced recall and latency | default production search |
| `accurate` | Higher recall | RAG retrieval, evaluation, quality-sensitive queries |

On the same 5-bit `IVF_RQ` index, `approx_mode` moves along the speed/quality curve without rebuilding the index:

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-006](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-006.png)

approx\_mode latency comparison

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-007](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-007.png)

approx\_mode QPS comparison

| `approx_mode` | Recall@10 | Avg latency | Approx QPS/core |
| --- | --- | --- | --- |
| `fast` | 81.4% | 3.2 ms | 315 |
| `normal` | 96.1% | 3.8 ms | 263 |
| `accurate` | 96.6% | 4.5 ms | 222 |

The approximate QPS/core values above are derived from average latency as `1000 / avg_latency_ms` in the same single-core benchmark. Treat them as a relative comparison between modes, not as cluster throughput.

This flexibility pays off in real applications. A UI can use `fast` while a user is typing, the main search endpoint can use `normal`, and a more latency-forgiving RAG context-retrieval step can use `accurate`, all against the same index.

One practical boundary is worth calling out: `approx_mode` selects among the scoring paths supported by the index you already built. A 5-bit `IVF_RQ` index can use the 1-bit fast path or spend more stored bits for higher recall, but it’s not a substitute for measuring recall on your own data, and it won’t turn one index into every possible bit width.

## Available Across OSS, Cloud, and Enterprise

These RaBitQ improvements live in the open source Lance and LanceDB Rust crates, so they’re available wherever you may be running LanceDB: the embedded open-source library, Cloud, and Enterprise. If you’re working with high-dimensional embeddings and currently rely on `IVF_PQ`, try the new path and create an `IVF_RQ` index. Here’s how that looks for LanceDB Enterprise users.

```
import lancedb
from lancedb.index import IvfRq

# Connect to a remote table on LanceDB Enterprise
db = lancedb.connect(
    uri="db://your-project",
    api_key="YOUR_API_KEY",
    region="us-east-1",
    host_override="https://<your-user>@<hostname>@<your-endpoint>",
)
table = db.open_table("documents")

table.create_index(
    "vector",
    config=IvfRq(
        distance_type="cosine",
        num_bits=5,
    ),
    replace=True,
)
```

In these benchmarks, `num_bits=5` was the balanced starting point, delivering **96.2% recall@10** with lower p99 latency and higher QPS/core than 7-bit RQ. Measure on your own workload, then use `approx_mode` to tune individual query paths. The practical payoff is that one compact RaBitQ index covers more of the speed/recall curve, so you make fewer raw-vector refine trips and rebuild the index less often as your product’s needs change.

Want to try it yourself? Grab the latest version of LanceDB (`pip install lancedb`) and check out our [GitHub repo](https://github.com/lancedb/lancedb). Store your embeddings in LanceDB, and see where `IVF_RQ` lands on your recall and latency numbers. We'd love to hear about it!

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-008](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-008.png)

[Yang Cen](/author/yang-cen)

Software Engineer @ LanceDB

[GitHub](https://github.com/BubbleCal)

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-009](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-009.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-010](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-010.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7-fig-011](../images/1396-https-www-lancedb-com-blog-rabitq-gets-faster-hi-3ce0d0c7/figure-011.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb