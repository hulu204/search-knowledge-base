---
title: 'https://www.lancedb.com/blog/lance-format-v2-2-benchmarks-half-the-storage-none-of-the-slowdown'
company: LanceDB
tag: 评测
date: 
url: https://www.lancedb.com/blog/lance-format-v2-2-benchmarks-half-the-storage-none-of-the-slowdown
account: 
origin: en-rss
---
# Lance Format v2.2 Benchmarks: Half the Storage, None of the Slowdown

[Xuanwo](/author/xuanwo)

•

April 6, 2026

•

[Engineering](/category/engineering)

![1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd-fig-001](../images/1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Multimodal training pipelines push a data format in four directions at once. The format must a) **keep storage costs low** at TiB scale, b) **serve blobs fast** so data loaders can randomly fetch images and video without starving the GPU, c) **scan structured columns efficiently** for preprocessing and filtering, and d) **evolve schemas freely** as embeddings are recomputed and derived artifacts accumulate.

[Lance](https://github.com/lancedb/lance) is an open lakehouse format that excels in those kinds of workloads, unifying the file format, table format, namespace spec and index in a single stack.

Although Parquet excels at one core part of multimodal pipelines: scanning structured columns — the other three expose the limits of its row-group-based architecture. Random blob access means locating and decoding entire row groups. Schema evolution means rewriting the full dataset. And compression, while still respectable, no longer reflects what modern encoding techniques can do on mixed multimodal data.

Lance format v2.2 (which you can use today by specifying the `data_storage_version="2.2"` parameter) is the point where all four requirements line up. Fast blob access and schema evolution were already strong capabilities in Lance format v2.0 and v2.1. Compression, however, was not yet on par with Parquet.

We're happy to announce that in v2.2, the last remaining gap closes decisively: text-heavy datasets in Lance shrink to half the size of equivalent Parquet files, while every other metric holds steady or improves.

> **💡 *2.2 refers to the file format version  
> ‍* ‍***The version numbers mentioned in this post (2.0, 2.1, and 2.2) refer to the Lance file format version (the `data_storage_version` parameter), not the Lance library release number.* The file format version governs how data is encoded and stored on disk. The library version determines which format versions can be read and written by the SDK.

## Benchmark Methodology

Those are strong claims, so the way we evaluate the system matters. To make the comparison concrete, we measured the performance of Lance formats v2.0, v2.2 and Parquet v1 across both local NVMe and S3, using workloads that reflect how multimodal datasets are actually stored and accessed.

All benchmarks were run on EC2 `c7i.4xlarge` (`us-east-2`) across two tiers of scale. The benchmark code is available [in this repo](https://github.com/Xuanwo/lance-dataset-test) and included the following datasets:

**Standard scale** (local NVMe + S3):

* FineWeb: 10M rows, text-heavy
* OpenVid: 1M rows, video metadata
* LAION-10M: 200K rows, image-text pairs with image blobs
* LeRobot PushT: 25K rows, robotics sensor data (with and without image blobs)

**Full scale** (S3 only, TiB-class):

* FineWeb-1B: 1.15B rows, 3.32 TiB under v2.0
* OpenVid-1M: 1M rows
* LAION-10M-Full: 20M rows, 589 GiB under v2.0

Each run compared Lance format v2.0 (baseline) and v2.2. Apache Parquet (rust crate v57.2.0) served as an external reference on local NVMe. The workload suite covered `ingest`, `scan_full`, `scan_project`, `scan_filter`, `random_take`, `random_blob`, and `evolution_backfill`.

> **💡 *How to read the comparison tables  
> ‍* ‍***Unless a dataset is named explicitly, comparative ratios and percentage tables in this post report geometric means across the relevant standard-scale datasets. If you're viewing this on a mobile device, the tables can be horizontally scrolled.*

## Storage: Beating Parquet at Its Own Game

Start with the simplest question: how much data does Lance format v2.2 store on disk? This is where the new compression work shows up most clearly. By applying LZ4 to dictionary-encoded values, v2.2 cuts the footprint of text-heavy datasets sharply. Lance v2.0 already sat close to Parquet in raw file size; but v2.2 moves decisively ahead:

| Dataset | Parquet | Lance v2.0 | Lance v2.2 | Lance v2.2 vs Parquet |
| --- | --- | --- | --- | --- |
| FineWeb (10M rows) | 32,534 MiB | 32,821 MiB | 15,631 MiB | **52% smaller** |
| LAION-10M (200K rows) | 5,995 MiB | 6,002 MiB | 5,995 MiB | On par |
| OpenVid (1M rows) | 1,027 MiB | 1,130 MiB | 649 MiB | **37% smaller** |
| LeRobot PushT (25K rows) | 1.2 MiB | 1.77 MiB | 0.86 MiB | **28% smaller** |

LAION-10M stays flat across all three formats because most of its bytes are already-compressed JPEG and PNG blobs. There is little left for any storage format to compress.

The same pattern holds at TiB scale. On S3, FineWeb-1B shrank from 3.32 TiB to 1.62 TiB (a **51%** decrease). OpenVid-1M dropped from 0.85 GiB to 0.36 GiB (a **58%** decrease). For teams storing training data in the cloud, that translates directly into lower storage costs, with no changes to the application layer.

## The Training Loop: Sampling Rows, Fetching Blobs

Storage is only part of the story. Once training starts, the real question is how the format keeps up with random access requirements. Every iteration follows the same two-step pattern: sample a batch of row indices, then fetch the corresponding contents. The speed of those two operations directly shapes GPU utilization.

**Random row sampling** (1,000 iterations on a single projected column): v2.2's additional compression introduces no meaningful overhead on this path.

| Storage | v2.2 vs v2.0 |
| --- | --- |
| Local NVMe | On par |
| S3 | On par |

On S3, the difference across 1,000 samples is under 0.1%, effectively identical. At TiB scale, v2.2 pulls ahead: LAION-10M-Full (20M rows, 589 GiB) completed in 71 s under v2.2 versus 110 s under v2.0, a 35% speedup driven by reduced metadata I/O. Lance also performs comparably with Parquet on local NVMe.

**Blob fetches** involve loading an image or video frame at a random offset, which is a common I/O pattern in multimodal training.

Comparing Lance format v2.2 to v2.0 on local NVMe showed substantial improvements:

| Metric | v2.2 vs v2.0 |
| --- | --- |
| Total wall time | **33% faster** |
| p50 latency | **48% faster** |
| p95 latency | **21% faster** |

At full scale on S3 (LAION-10M-Full, 20M rows, 589 GiB):

| Version | Total Time | p50 Latency | p95 Latency |
| --- | --- | --- | --- |
| v2.0 | 151,138 ms | 149.6 ms | 265.0 ms |
| v2.1 | 161,586 ms | 163.8 ms | 298.0 ms |
| v2.2 | **139,706 ms** | **124.1 ms** | 294.4 ms |

Against Parquet, the performance gap is due to fundamental architectural differences. Lance stores blobs in a dedicated region with position-indexed access; Parquet must scan and decode row groups to reach binary payloads it was never designed to serve efficiently. The result on local NVMe is shown below:

|  | Lance v2.2 | Parquet |
| --- | --- | --- |
| Geomean wall time (1K random blobs) | ~2 s | ~150 s |

Across all the datasets tested, Lance v2.2 is **75x** faster than Parquet for blob fetches.

On LAION-10M alone, Parquet needed 889 seconds to fetch 1,000 random images; Lance v2.2 finished the same workload in single-digit seconds. For pipelines streaming millions of images per epoch, this is not a marginal difference. It is the difference between a training run limited by GPU throughput and one bottlenecked on storage.

## Scans and Filters: The Nuanced Picture

Preprocessing pipelines scan columns for filtering, feature extraction, and data validation. This is traditionally Parquet's strongest territory, and the results here are genuinely mixed.

Comparing v2.2 to v2.0 on S3, Lance v2.2's smaller files pay off:

| Workload | v2.2 vs v2.0 (S3) |
| --- | --- |
| `scan_full` | **23% faster** |
| `scan_project` | ~2% faster |
| `scan_filter` (low sel.) | ~3% faster |
| `scan_filter` (high sel.) | < 1% |

At TiB scale, these gains become more pronounced. On FineWeb-1B (1.15 billion rows), `scan_project` improved from 146 ms to 135 ms, an 8% reduction. On LAION-10M-Full, it dropped from 158 ms to 101 ms, making it **36% faster**. As dataset size increases, reduced I/O plays an increasingly dominant role.

On local NVMe, v2.2's dictionary decoding introduces CPU overhead that surfaces when I/O is no longer the bottleneck:

| Workload | v2.2 vs v2.0 (local) |
| --- | --- |
| `scan_project` | 36% slower |
| `scan_filter` (low sel.) | 18% slower |
| `scan_filter` (high sel.) | 25% slower |

These regressions relative to v2.0 are real, but bounded. On FineWeb (10 million rows), `scan_project` increased from 51 ms to 85 ms, a 34 ms difference that is negligible in any realistic training loop. On S3, where production datasets typically reside, the regressions disappear entirely. At TiB scale, they reverse, as I/O savings begin to outweigh the added CPU cost.

Against Parquet on local NVMe, the results for v2.2 look as follows:

| Workload | Lance v2.2 vs Parquet |
| --- | --- |
| `scan_project` | Parquet 40% faster |
| `scan_filter` (low sel.) | Tied |
| `scan_filter` (high sel.) | Lance 2.8x faster |

Parquet’s advantage on narrow column projections reflects a decade of optimization for exactly that access pattern. Lance, however, matches or outperforms it on low-selectivity filters, and extends that lead on high-selectivity filters where large portions of the dataset must be materialized.

The takeaway is straightforward: for analytics-style queries over scalar columns on local storage, Parquet remains highly competitive. But on object storage, at TiB scale, or when filters return substantial result sets, Lance v2.2 matches Parquet’s performance and often exceeds it.

## Dataset Iteration: Write Fast, Evolve Freely

Building a multimodal dataset is never a one-shot process. Data arrives in stages. Embeddings get recomputed. Annotation columns appear as the project evolves. Two operations govern how fast this cycle turns: initial ingestion and schema evolution.

Comparing v2.2 to v2.0, **ingest** performance is indistinguishable despite the extra encoding work — both comparisons sit within measurement noise. **Data evolution**, however, is where Lance’s architecture delivers its most striking advantage. Adding a column **with backfilled data** to a Lance dataset writes new data alongside existing files; the original data is never touched. Parquet (even when used with table formats like Iceberg) has no equivalent operation and must rewrite everything.

| Workload (v2.2 vs v2.0) | Local NVMe | S3 |
| --- | --- | --- |
| Ingest | ~1% | < 1% |
| Data evolution | **29% faster** | **10% faster** |

Against Parquet on local NVMe, Lance v2.2 shows clear wins on both operations:

| Workload | Lance v2.2 vs Parquet |
| --- | --- |
| Ingest | **70% faster** |
| Data evolution | **~61x faster** |

Across all datasets tested, Lance v2.2 is **61x** faster than Parquet for dataset backfills when adding new columns.

The difference is most stark on FineWeb’s 10 million rows: Lance adds a new column in 13 ms, while Parquet takes **520 seconds** to rewrite the dataset. The gap is so large because Parquet must rewrite the entire existing table, even when the new column is small, while Lance only writes the new column as a separate data file.

The larger the original dataset, especially at petabyte-scale, the more pronounced those time savings become. For teams with large tables that iterate frequently on their schemas, that means replacing coffee-break delays with near-instant feedback.

## Putting It Together

Lance v2.2 set out to satisfy four demands of multimodal AI training without asking teams to compromise on any of them. Here is where it landed:

| Dimension | Lance v2.2 vs v2.0 | Lance v2.2 vs Parquet |
| --- | --- | --- |
| **Storage cost** | 50%+ reduction | 52% smaller than Parquet |
| **Blob access** | p50 latency down 17-48% | ~68x faster |
| **Scan throughput** | 23% faster on S3 full scan | Competitive; leads at scale |
| **Schema flexibility** | 10-29% faster | ~61x faster |

Compression was the last dimension where Lance trailed Parquet. v2.2 eliminates that gap and then some. For teams already on Lance, upgrading is a low-risk, high-return change. For teams weighing Lance against Parquet for a multimodal workload, the benchmarks leave little room for ambiguity.

## Upgrade to File Format v2.2

Lance file format v2.2 is available today, and trying it is straightforward. When writing a dataset, pass `data_storage_version="2.2"`:

```
import lance

ds = lance.write_dataset(data, "my_dataset.lance", data_storage_version="2.2")
```

If you are already using Lance, this is a low-friction upgrade with immediate payoff in storage efficiency. If you are evaluating formats for a multimodal workload, this is the version to benchmark against your own pipelines.

## What This Means in Practice

For existing Lance users, the takeaway is simple: upgrade to file format v2.2. You get materially lower storage costs, keep Lance's advantages on blob access and schema evolution, and give up little to nothing on the workloads that matter most in multimodal training.

For teams still deciding between Lance and Parquet, the tradeoff is now much clearer. Parquet remains strong for narrow scalar scans on local storage, but Lance no longer asks you to accept a compression penalty in exchange for better blob access, object-store behavior, and schema flexibility. For multimodal pipelines, that makes Lance the more complete default.

The broader point is that these advantages compound. Lower storage footprint reduces cloud cost. Faster random blob reads keep GPUs better utilized. Cheap schema evolution shortens iteration cycles. Across a production training pipeline, those are not isolated wins; they reinforce one another.

For a deeper walkthrough of v2.2's new capabilities, including native Map types, Blob upgrades, nested schema evolution, and a recommended upgrade strategy, see the companion posts on [the v2.2 file format](https://www.lancedb.com/blog/lance-file-format-2-2-taming-complex-data) and [Blob v2](https://www.lancedb.com/blog/lance-blob-v2).

## Additional Information

All code to reproduce this benchmark is available [in this repo](https://github.com/Xuanwo/lance-dataset-test).

* Benchmark environment: EC2 `c7i.4xlarge` (`us-east-2`), local NVMe + S3, Lance SDK v4.0.0, Parquet rust crate v57.2.0
* Full-scale tests: EC2 `c7i.4xlarge`, S3 only, FineWeb-1B (1.15B rows, 3.32 TiB), LAION-10M-Full (20M rows, 589 GiB)

‍

![1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd-fig-002](../images/1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd/figure-002.avif)

[Xuanwo](/author/xuanwo)

ASF Member. Apache OpenDAL PMC Chair. VISION: Data Freedom. Working on RBIR with LanceDB.

[GitHub](https://github.com/Xuanwo)[Linkedin](https://www.linkedin.com/in/xuanwo/)[Twitter](https://x.com/OnlyXuanwo)

![1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd-fig-003](../images/1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd-fig-004](../images/1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd-fig-005](../images/1433-https-www-lancedb-com-blog-lance-format-v2-2-ben-fceaf3bd/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb