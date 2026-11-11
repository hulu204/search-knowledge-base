---
title: 'https://www.lancedb.com/blog/newsletter-may-2026'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/newsletter-may-2026
account: 
origin: en-rss
---
# 🌍 Lance-Backed World Model Platform, 🦆 Multimodal SQL with Lance DuckDB Extension, 💰 LanceDB vs OpenSearch Cost Breakdown

[ChanChan Mao](/author/chanchan-mao)

•

June 2, 2026

•

[Newsletter](/category/newsletter)

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-001](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## 🌍 stable-worldmodel: A Platform for Reproducible World Modeling Research and Evaluation

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-002](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-002.png)

World model training requires small-batch random access across large sequence buffers—a pattern that performs poorly on HDF5 or video formats, especially over the network. stable-worldmodel is an open-source platform with a Lance-based data layer that streams directly from S3 several times faster than alternatives, making ephemeral GPU training practical without local sync.

The platform includes reference implementations of DINO-WM, LeWorldModel, PLDM, and TD-MPC2, plus ~150 environments with controllable visual and physical factors for standardized zero-shot generalization benchmarks. Details and benchmark numbers are in the paper.

[Paper →](https://arxiv.org/abs/2605.21800) · [Code →](https://github.com/galilai-group/stable-worldmodel)

## 🦆 Make Your SQL Workflows Multimodal with LanceDB x DuckDB

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-003](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-003.webp)

database for embeddings, and a SQL warehouse for metadata. The Lance core extension for DuckDB collapses all three—image bytes live as a BLOB column alongside embeddings and structured fields in a single table.

`lance_vector_search()` is a SQL table function that returns ranked results with raw JPEG bytes inline. Standard SQL handles the rest: joins, filters, aggregations. The blog post walks through setup and query examples.

[Read more →](https://www.lancedb.com/blog/make-your-sql-workflows-multimodal-with-lancedb-x-duckdb)

## 💰 OpenSearch vs LanceDB for Vector Search: Query Cost and Infrastructure

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-004](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-004.webp)

Vector search costs scale with RAM when the index lives in memory — bigger dataset means bigger instance. LanceDB stores the index in S3 and memory-maps it, so RAM scales with QPS rather than dataset size. At 100M docs (1152-dim, SQ8): ~$779/month total. At 10M: ~$148. At 1M: ~$65.

Benchmarked on 287K COCO images with SigLIP 2 embeddings using IVF\_HNSW\_SQ — above 0.95 recall@10, sub-50ms p95 on a single node. Full cost breakdown and OpenSearch comparison in the post.

[Read more →](https://www.lancedb.com/blog/opensearch-vs-lancedb-for-vector-search-query-cost-and-infrastructure)

## 📚 Also Published

* [Test-Driving the Lance Lakehouse Format in DuckDB](https://duckdb.org/2026/05/21/test-driving-lance)

## 🎤 Talks & Recordings

**Managing Data at Exabyte Scale for AI Model Training | Chang She (LanceDB) | OpenXdata 2026**

Chang She (LanceDB) discusses how current data infrastructure forces ML teams to copy data across disconnected tools throughout the training workflow, and presents LanceDB’s approach of managing multimodal training data in a unified table to streamline the path from exploration to GPU loading.

[Watch the recording →](https://www.youtube.com/watch?v=Y9Z3cWuiQIo)

**Q&A with Chang She, CEO, LanceDB: Why the 20-year-old data stack is breaking under AI workloads**

Chang She (CEO, LanceDB) discusses why traditional database architectures that separate data storage from file storage via pointers are failing under AI workloads, particularly the throughput challenges posed by agentic data access at scale.

[Watch the recording →](https://www.youtube.com/watch?v=FaX4fpEdOlw)

## 📅 Upcoming Events

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-005](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-005.png)

**Microsoft Build** — June 2-3, 2026 · San Francisco, CA

Compares multi-system AI data architectures on Azure with unified approaches that use Blob Storage as the foundation for raw data, embeddings, and features. Covers the practical tradeoffs when curation, feature engineering, training, search, and analytics start spreading data across systems.

[Register →](https://build.microsoft.com/en-US/sessions/TT653)

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-006](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-006.png)

**Snowflake Summit** — June 1-4, 2026 · San Francisco, CA

Apache Polaris is expanding beyond Iceberg to support Delta and Lance formats as an open catalog layer, with new capabilities including S3-compatible on-prem storage, generic tables, a built-in policy store, and catalog federation. Engineers from Snowflake and partners will demo real-world usage and walk through the evolving Polaris REST catalog spec.

[Register →](https://reg.snowflake.com/flow/snowflake/summit26/sessions/page/catalog/session/1766082341410001Vior)

**Data+AI Summit** — June 15-18, 2026 · San Francisco, CA

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-007](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-007.png)

**Managing Data at Exabyte Scale for AI Model Training**

Enterprise AI model training succeeds or fails based on iteration speed across the full data flywheel — from exploration and curation to feature engineering and GPU loading. LanceDB manages all multimodal training data in a unified table, eliminating the tool-hopping that delays or kills training projects.

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-008](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-008.png)

**From Streaming to Search: How Exa Uses Lance and Apache Spark for high-throughput AI Workloads**

Exa uses Lance and Spark Structured Streaming to power search and AI workloads across large volumes of crawled web data. The pipeline performs local and global deduplication, generates embeddings, and sustains ~10k rows per second into Lance tables that power downstream vector search databases. [‍](https://www.databricks.com/dataaisummit)

[Register →](https://www.databricks.com/dataaisummit)

‍

## 🏗️ LanceDB Enterprise Updates

### Performance

* **Page-Boundary Read Coalescing** — The storage caching layer now widens reads to page boundaries instead of issuing one request per page, significantly reducing read fan-out and improving throughput for cached access patterns.
* **KNN Pushdown for Filtered Queries** — K-nearest-neighbor queries over remotely filtered result sets now push execution closer to the data, reducing data movement and improving latency for hybrid filtered vector searches.
* **IVF\_RQ Index in Distributed Indexer** — The distributed indexer now supports IVF with residual quantization (IVF\_RQ), offering a better compression/speed tradeoff for large-scale vector indexes built across multiple nodes.
* **Vector Index Row Count Persistence** — Row counts for vector indexes are now persisted at build time, eliminating expensive full-table scans that were previously required to determine index coverage.**‍**
* **Distributed Indexer Training Optimization** — Single-segment index training in the distributed indexer was optimized to reduce unnecessary work, improving build throughput for tables that fit within one segment.

### Features

| Feature | Description |
| --- | --- |
| Distributed Full-Text Search | Full-text and BTree index queries can now execute across distributed query nodes using a two-phase RPC coordinator, bringing distributed search on par with distributed vector search. |
| Segmented Distributed Indexing | The distributed indexer now supports fragment-scoped and segmented builds for vector, scalar, FTS, and BTree indexes, enabling finer-grained parallelism and faster incremental index updates at scale. |
| Two-Tier Index Cache & Prewarm | A two-tier index cache (in-memory + NVMe disk) is now available, with new API and CLI commands to prewarm the cache ahead of traffic, significantly reducing cold-start query latency. |
| Write-Ahead Log | A new write-ahead log (WAL) writer built on the Lance OSS memory WAL is now integrated, alongside a unified developer CLI with fuzzy testing support, laying the foundation for stronger durability guarantees. |
| Feature Engineering Views & Schema Evolution | Materialized views and user-defined table-valued function (UDTF) views are now supported in the query engine, along with `add_columns` and `alter_columns` schema evolution APIs. |

## 🌟 Open Source Releases

| Project | Description |
| --- | --- |
| **Lance** v6.0.0 – v7.0.0 [Release notes](https://github.com/lance-format/lance/releases) | • New MemWAL (memory write-ahead log) system with `ShardWriter`, memtable-based HNSW index, manual compaction APIs, and Java bindings—enables low-latency ingestion pipelines with durable replay ([#6669](https://github.com/lance-format/lance/pull/6669), [#6675](https://github.com/lance-format/lance/pull/6675), [#6795](https://github.com/lance-format/lance/pull/6795), [#6833](https://github.com/lance-format/lance/pull/6833)) • Segmented and distributed index builds: segmented inverted index ([#6305](https://github.com/lance-format/lance/pull/6305)), segmented btree ([#6605](https://github.com/lance-format/lance/pull/6605)), zonemap index segments ([#6593](https://github.com/lance-format/lance/pull/6593)), distributed bitmap index ([#6598](https://github.com/lance-format/lance/pull/6598)), and FTS segment merging ([#6790](https://github.com/lance-format/lance/pull/6790)) • SIMD distance kernels for scalar-quantized vectors: u8 dot/L2/cosine ([#6506](https://github.com/lance-format/lance/pull/6506), [#6517](https://github.com/lance-format/lance/pull/6517)), bf16 ([#6510](https://github.com/lance-format/lance/pull/6510)), f64 ([#6540](https://github.com/lance-format/lance/pull/6540)), and 16× faster RaBitQ 4-bit LUT on ARM ([#6537](https://github.com/lance-format/lance/pull/6537)) |
| **LanceDB** v0.32.0 – v0.33.0 [Release notes](https://github.com/lancedb/lancedb/releases) | • New `IVF_HNSW_FLAT` vector index type available in Python ([#3366](https://github.com/lancedb/lancedb/pull/3366)); native FTS now supports model-backed tokenizers ([#3289](https://github.com/lancedb/lancedb/pull/3289)) • Nested namespace operations for organizing tables hierarchically, with manifest-enabled directory mode ([#3265](https://github.com/lancedb/lancedb/pull/3265), [#3332](https://github.com/lancedb/lancedb/pull/3332)); Node.js SDK gains `connectNamespace` and namespace management methods ([#3371](https://github.com/lancedb/lancedb/pull/3371), [#3383](https://github.com/lancedb/lancedb/pull/3383)) • PyTorch DataLoader compatibility: `Permutation` is now fork-safe and picklable for multiprocessing workers ([#3339](https://github.com/lancedb/lancedb/pull/3339), [#3335](https://github.com/lancedb/lancedb/pull/3335)) • Vector indexes on nested fields now work correctly—paths are discovered automatically and canonicalized for remote tables ([#3408](https://github.com/lancedb/lancedb/pull/3408), [#3423](https://github.com/lancedb/lancedb/pull/3423), [#3430](https://github.com/lancedb/lancedb/pull/3430)) |
| **lance-ray** v0.3.0 – v0.4.2 [Release notes](https://github.com/lance-format/lance-ray/releases) | • New dataset maintenance operations: `optimize_indices` ([#2152](https://github.com/lance-format/lance-ray/pull/2152)) and `compact_database` ([#2250](https://github.com/lance-format/lance-ray/pull/2250)) for managing Lance datasets at scale via Ray • Index creation now supports namespaces via `create_index()` ([#2594](https://github.com/lance-format/lance-ray/pull/2594)) and configurable vector index sample rates ([#4631](https://github.com/lance-format/lance-ray/pull/4631)) • Blob v2 support with legacy compatibility and multi-base config for read/write operations ([#1614](https://github.com/lance-format/lance-ray/pull/1614), [#4516](https://github.com/lance-format/lance-ray/pull/4516)) |
| **lance-trino** v0.3.0 [Release notes](https://github.com/lance-format/lance-trino/releases) | • Added support for Struct type mapping to Trino `RowType`, including Substrait schema support for nested field filtering ([#96](https://github.com/lance-format/lance-trino/pull/96), [#125](https://github.com/lance-format/lance-trino/pull/125)) • Upgraded to lance-core 6.0.0 and lance-namespace 0.7.6 ([#124](https://github.com/lance-format/lance-trino/pull/124)) |
| **lance-namespace** v0.7.3 – v0.7.7 [Release notes](https://github.com/lance-format/lance-namespace/releases) | • Added backfill columns and refresh materialized view operations ([#335](https://github.com/lance-format/lance-namespace/pull/335)) • Extended virtual column entries with UDF metadata support ([#337](https://github.com/lance-format/lance-namespace/pull/337)) • API changes for materialized views and UDTFs ([#344](https://github.com/lance-format/lance-namespace/pull/344)) |

## 🫶 Community Contributions

### Announcing 5 New [Lance Maintainers](https://lance.org/community/maintainers/)

* Jianjian Xie [@jja725](https://github.com/jja725) (Uber)
* Chunxu Tang [@ChunxuTang](https://github.com/ChunxuTang)
* Yang Jie [@LuciferYang](https://github.com/LuciferYang) (Baidu AI Cloud)
* Zhang Yue [@zhangyue19921010](https://github.com/zhangyue19921010) (ByteDance Volcano Engine)
* Dan Rammer [@hamersaw](https://github.com/hamersaw) (LanceDB)

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-009](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-009.webp)

Thank you to contributors from Bytedance, Adobe, Baidu, Tencent, Hugging Face, Google, Red Hat, Roblox, Uber for improvements across storage, indexing, query execution, distributed processing, and ecosystem integrations in LanceDB, Lance, and the broader ecosystem.

**Notable contributions this month:**

* [@zhangyue19921010](https://github.com/zhangyue19921010) — Exposed LSM API to Python and Java with distributed bitmap index build support, enabling scalable incremental indexing workflows
* [@beinan](https://github.com/beinan) — Added segmented btree indices and unenforced clustering key support to the format spec, improving query optimization for large-scale datasets
* [@touch-of-grey](https://github.com/touch-of-grey) — Built write-ahead log appender/tailer primitives and MemWAL HNSW integration, enabling real-time vector indexing for streaming workloads
* [@yanghua](https://github.com/yanghua) — Added Rust support for update by \_row\_id, enabling efficient row-level mutations in analytical pipelines
* [@alex766](https://github.com/alex766) — Added Dataset.takeRows() Java binding for physical row ID access, unlocking low-level row retrieval for JVM applications
* [@Its-Tanay](https://github.com/Its-Tanay) — Added Scannable primitive for Node.js streaming ingestion, enabling efficient large-dataset loading in JavaScript workflows
* [@shenganzhang](https://github.com/shenganzhang) — Added IVF\_HNSW\_FLAT vector index support to Python SDK, expanding hybrid search options for production deployments
* [@atakanyenel](https://github.com/atakanyenel) — Added Struct type mapping to Trino RowType, enabling nested data querying through the Trino connector
* [@devteamaegis](https://github.com/devteamaegis) — Fixed inverted scores and missing-FTS penalty in LinearCombinationReranker, correcting hybrid search ranking accuracy
* [@yuvalif](https://github.com/yuvalif) — Added DataFusion Expr support for table row deletions in Rust SDK, enabling programmatic delete operations

A heartfelt thank you to our community contributors of Lance and LanceDB this past month:

[@aayushbaluni](https://github.com/aayushbaluni) • [@adaworldapi](https://github.com/adaworldapi) • [@alex766](https://github.com/alex766) • [@ali2arslan](https://github.com/ali2arslan) • [@ar-maan05](https://github.com/ar-maan05) • [@atakanyenel](https://github.com/atakanyenel) • [@beinan](https://github.com/beinan) • [@chenghao-guo](https://github.com/chenghao-guo) • [@ddupg](https://github.com/ddupg) • [@dentiny](https://github.com/dentiny) • [@devteamaegis](https://github.com/devteamaegis) • [@dhruvgarg111](https://github.com/dhruvgarg111) • [@fangbo](https://github.com/fangbo) • [@farmerchillax](https://github.com/farmerchillax) • [@geserdugarov](https://github.com/geserdugarov) • [@gezi-lzq](https://github.com/gezi-lzq) • [@ghx5t-sol](https://github.com/ghx5t-sol) • [@guillesd](https://github.com/guillesd) • [@guinik](https://github.com/guinik) • [@haochengliu](https://github.com/haochengliu) • [@hfutatzhanghb](https://github.com/hfutatzhanghb) • [@hushengquan](https://github.com/hushengquan) • [@its-tanay](https://github.com/its-tanay) • [@ivscheianu](https://github.com/ivscheianu) • [@jay-ju](https://github.com/jay-ju) • [@jerryjch](https://github.com/jerryjch) • [@jiaoew1991](https://github.com/jiaoew1991) • [@jiengup](https://github.com/jiengup) • [@jja725](https://github.com/jja725) • [@johnchak](https://github.com/johnchak) • [@kaan-simbe](https://github.com/kaan-simbe) • [@keepromise](https://github.com/keepromise) • [@kushudai](https://github.com/kushudai) • [@lennylxx](https://github.com/lennylxx) • [@leoreeyang](https://github.com/leoreeyang) • [@lhoestq](https://github.com/lhoestq) • [@luciferyang](https://github.com/luciferyang) • [@majin1102](https://github.com/majin1102) • [@martji](https://github.com/martji) • [@mesut-doner](https://github.com/mesut-doner) • [@mikewhb](https://github.com/mikewhb) • [@myandpr](https://github.com/myandpr) • [@n1teshy](https://github.com/n1teshy) • [@omkar-334](https://github.com/omkar-334) • [@pengw0048](https://github.com/pengw0048) • [@plotor](https://github.com/plotor) • [@pragnyanramtha](https://github.com/pragnyanramtha) • [@qingfeng-occ](https://github.com/qingfeng-occ) • [@ragnorc](https://github.com/ragnorc) • [@sezruby](https://github.com/sezruby) • [@shenganzhang](https://github.com/shenganzhang) • [@shiwk](https://github.com/shiwk) • [@siddiqueahmad](https://github.com/siddiqueahmad) • [@singhvishalkr](https://github.com/singhvishalkr) • [@sinianluoye](https://github.com/sinianluoye) • [@snigenigmatic](https://github.com/snigenigmatic) • [@summaryzb](https://github.com/summaryzb) • [@touch-of-grey](https://github.com/touch-of-grey) • [@vip892766gma](https://github.com/vip892766gma) • [@wangxiaobao1222](https://github.com/wangxiaobao1222) • [@wending-y](https://github.com/wending-y) • [@wojiaodoubao](https://github.com/wojiaodoubao) • [@wombatu-kun](https://github.com/wombatu-kun) • [@xiaguanglei](https://github.com/xiaguanglei) • [@xodn348](https://github.com/xodn348) • [@xuqianjin-stars](https://github.com/xuqianjin-stars) • [@yanghua](https://github.com/yanghua) • [@yuqi1129](https://github.com/yuqi1129) • [@yuvalif](https://github.com/yuvalif) • [@zelys-dfkh](https://github.com/zelys-dfkh) • [@zhangyue19921010](https://github.com/zhangyue19921010) • [@zouhuajian](https://github.com/zouhuajian)

## 🤝 Lance Community Sync Recap

Community syncs this month covered the upcoming Lance 2.1.0 release, which will make the Lance 2.1 file format the default, along with indexing improvements and DataFusion enhancements. Early GPU acceleration work through a CuVS integration was also discussed. On the SDK side, Lance 6.0.1 shipped with bug fixes, and Lance 7.0.0 moved toward a release candidate with a community vote planned. The Lance DuckDB extension gained visibility with an official blog post published on the DuckDB blog.

The next Lance Community Sync will take place on **Thursday, June 4 @ 9am PT**.

• [📬 Subscribe to the Lance mailing list to receive the meeting invite →](https://groups.google.com/a/lance.org/g/dev)

• [📄 Add discussion topics to the meeting notes →](https://docs.google.com/document/d/1cP058pJLVjj39DGaFV5yHI6qyWBwp1B2YKyIwXzYlAI/edit?usp=sharing)

• [📺 Watch previous recordings →](https://www.youtube.com/playlist?list=PLQysAafL04jUgOj7j6mCE5fcZEBB9Amu9)

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-010](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-010.avif)

[ChanChan Mao](/author/chanchan-mao)

Developer Relations @ LanceDB

[GitHub](https://github.com/ccmao1130)[Linkedin](https://www.linkedin.com/in/chanchanmao/)

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-011](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-011.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-012](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-012.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c-fig-013](../images/2339-https-www-lancedb-com-blog-newsletter-may-2026-5e2a644c/figure-013.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb