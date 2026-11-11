---
title: 'https://www.lancedb.com/blog/newsletter-april-2026'
company: LanceDB
tag: 评测
date: 
url: https://www.lancedb.com/blog/newsletter-april-2026
account: 
origin: en-rss
---
# ⚡Vector Search at 10B Scale, 📊 Lance Format Benchmarks, 🚗 AV Pipelines at Scale

[ChanChan Mao](/author/chanchan-mao)

•

May 4, 2026

•

[Newsletter](/category/newsletter)

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-001](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## **⚡How LanceDB Accelerates Vector Search at 10 Billion Scale**

[![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-002](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-002.png)](https://www.lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale)

LanceDB Enterprise introduces a distributed architecture for vector search at 10B scale that avoids common bottlenecks in indexing and query execution. Indexes are split into independently built segments, enabling near-linear scaling in build time, while query execution is parallelized across workers without increasing per-query latency.

Key optimizations—like HNSW over centroids to remove linear scans and faster preprocessing for RaBitQ—reduce query overhead even at high dimensions. The result is scalable throughput, predictable latency, and a stable API, even as datasets grow to tens of billions of vectors.

[Read more →](https://www.lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale)

## **📊 Lance Format v2.2 Benchmarks: Half the Storage, None of the Slowdown**

[![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-003](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-003.png)](https://www.lancedb.com/blog/lance-format-v2-2-benchmarks-half-the-storage-none-of-the-slowdown)

Lance format v2.2 reduces storage by ~50% vs. Parquet on text-heavy data while enabling up to 75× faster random reads for blobs like images and video. Filtering and sampling performance stays stable as data scales, without requiring application changes.

These gains come from compressing dictionary values without impacting access paths—reducing I/O during training and improving GPU utilization.

[Read more →](https://www.lancedb.com/blog/lance-format-v2-2-benchmarks-half-the-storage-none-of-the-slowdown)

## **🚗 Unifying the AV ML Stack: From Raw Data to Trained Model with LanceDB**

[![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-004](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-004.png)](https://www.lancedb.com/blog/unifying-the-av-ml-stack-lancedb)

LanceDB consolidates AV ML pipelines into a single system: raw data, annotations, and embeddings in one table, with SQL-based curation and materialized views for training splits. New data and signals can be added incrementally without rebuilding pipelines.

Training jobs can resume from checkpoints, and retraining workflows stay stable as data evolves—reducing iteration time on large multimodal datasets.

[Read more →](https://www.lancedb.com/blog/unifying-the-av-ml-stack-lancedb)

## **🗞️ Case Study**

### Bytedance Volcano Engine LAS's Lance-Based PB-Scale Autonomous Driving Data Lake Solution

[![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-005](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-005.png)](https://www.lancedb.com/blog/volcano-engine-autonomous-driving-data-lake-solution)

Bytedance’s Volcano Engine LAS (Lake for AI Service) team rebuilt their autonomous driving data lake on Lance to address scaling bottlenecks in annotation and training. Instead of rewriting datasets on every schema change, they added new labels incrementally, reduced storage by up to 70% with built-in compression, and enabled training jobs to read only required columns.

At production scale, this translated into higher GPU utilization (60% → 96%) and faster iteration: 10PB label processing dropped from 4 days to 1, with overall model iteration improving by ~40%.

[Read more →](https://www.lancedb.com/blog/volcano-engine-autonomous-driving-data-lake-solution)

## **📖 Also Published This Month**

* [Agentic Coding as Community Stewardship](https://www.lancedb.com/blog/agentic-coding-as-community-stewardship)
* [Smart Parsing Meets Sharp Retrieval: Combining LiteParse and LanceDB](https://www.lancedb.com/blog/smart-parsing-meets-sharp-retrieval-combining-liteparse-and-lancedb)
* [Lance JSON Support: Why You Might Not Really Need Variant](https://www.lancedb.com/blog/lance-json-support-why-you-might-not-really-need-variant)
* [Building A Storage Format For The Next Era of Biology](https://www.lancedb.com/blog/building-a-storage-format-for-the-next-era-of-biology)

## **📺 Talks & Recordings**

**10 Things I Hate About Feature Engineering for AI**

In a world where software engineers have stopped writing most of their code manually, data teams are still debugging distributed pipeline failures at 2 AM and watching their OpenAI bills spike over the weekend. Chang breaks down the ten biggest pain points of feature engineering for AI — and makes the case that our data infrastructure was built for the last generation.

[**Watch the recording →**](https://www.youtube.com/watch?v=dv4vZQ4KJTo)

**Powering Netflix's Multimodal Feature Engineering at Scale**

Jack Ye (Software Engineer @ LanceDB) and Pablo Delgado (Machine Learning Engineer @ Netflix) share how Netflix builds and curates multimodal features across large video and image corpora, with LanceDB serving as the core storage and query layer for multimodal data.

[**Watch the recording →**](https://youtu.be/CrcvEEB4FW4?si=GgkMZ0An8QHmjeLD)

**Exa-Scale Search with Lance & Ray**

Dive into the infrastructure behind Exa's AI search engine, covering how Lance and Ray support distributed embedding pipelines and semantic retrieval at web scale across billions of documents.

* [Data & Engineering at Exa](https://youtu.be/prbrvpCZzCY) – Hubert Yuan, Software Engineer @ Exa
* [Lance: Exa-Scale | Multimodal Lakehouse](https://youtu.be/1FhWRlOR2Eg) – Lei Xu, CTO @ LanceDB[‍](https://youtu.be/bL1sG4M0p2I)
* [Ray Data: Scalable AI Computing & Distributed Systems](https://youtu.be/bL1sG4M0p2I) – Goutam Venkatramanan, Software Engineer @ Anyscale

## **📅 Upcoming Events**

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-006](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-006.png)

**AI Agent Conference** – May 4-5 in NYC

Join Chang's session to learn why the biggest bottleneck for production AI agents isn't model intelligence, but data infrastructure – and how context engineering and purpose-built systems will drive the next leap in agent quality.

[Register →](https://www.agentconference.com/)

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-007](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-007.png)

**KGC (Knowledge Graph Conference)** – May 4-8 in NYC

Prashanth Rao (AI Engineer @ LanceDB) and David Hughes (AI & Graph Solution Architect) will present a Lance-native multimodal RAG architecture that unifies embeddings, graph traversal, and media access in a single system—enabling zero-copy retrieval, lower latency, and simpler pipelines.

[Register →](https://www.knowledgegraph.tech/)

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-008](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-008.png)

**AI Council** – May 12-14 in SF

Explore the infrastructure challenges of managing trillion-scale multimodal datasets, and how Lance format and LanceDB are built to help you scale faster and cut costs.

LanceDB is a sponsor of AI Council this year! Come find us at our booth to talk training data infrastructure, feature engineering at PB scale, and a chance to win some cool swag!

[Register →](https://aicouncil.com/sf-2026)

### 🎙️Meetups

[Agent Builders Night – May 5, NYC](https://luma.com/agent_builders_nyc)

LanceDB, Braintrust, Modal, and Augment Code are bringing together AI leaders and builders for an evening of relaxed conversations and cocktails. No pitches or panels - just good food, drinks, and great vibes!

[San Francisco DataFusion Meetup – May 11, SF](https://luma.com/k3ointcl)

Prashanth Rao will be diving into the internals of distribution query execution built with Apache DataFusion and Lance, multimodal lakehouse format.

[Ship It: Dinner & Drinks on a Boat – May 13, SF](https://luma.com/dxsyixj5)

Join us for a private gathering of AI and data peeps for an evening on the water during AI Council week in San Francisco. ​We’re bringing together a small group of builders, operators, and technical leaders shaping the future of AI systems and data infrastructure.

[The missing data layer for ML – May 13, Menlo Park](https://luma.com/80pocni3)

Join LanceDB, dltHub, and DataHub for a night of technical talks and demos as we demystify the missing data layer for ML. Hear from the engineers building the ingestion, retrieval, and metadata layers of the open source AI stack.

## **🏗️ LanceDB Enterprise Updates**

### Performance

* **IVF Centroid Routing** — Accelerated centroid routing for the IVF index reduces vector search latency at query time.
* **Page Map Caching** — Replaced the page map cache with a high-concurrency implementation, improving read throughput under contention.
* ‍**Index Metadata Lookups** — Reduced overhead on index metadata lookups during table maintenance, cutting operation cost at scale.

### Features

| Feature | Description |
| --- | --- |
| Distributed Vector Search | ANN execution now distributes across workers with segment-level routing, distributed query plan execution with built-in metrics, and segment-based index builds — the architecture behind the [10B-scale results](https://www.lancedb.com/blog/how-lancedb-accelerates-vector-search-at-10-billion-scale). |
| Table Maintenance Automation | Intelligent job planning with automated and remote backfill support, plus configurable warm-up readiness gating to block traffic until the query engine is ready. |
| Telemetry Privacy Controls | Table names, column names, and user identifiers can be obfuscated in telemetry and indexer workloads — required for deployments operating under strict data governance or regulatory constraints. |
| Secure Namespace Credential Vending | Manifest-based credential vending for cross-namespace access to storage and services without exposing credentials at the application layer. |
| Catalog Explorer & SQL Console | Catalog explorer frontend and integrated SQL console in the Feature Engineering sidebar for interactive data exploration without leaving the platform. |
| Cache Observability | Page read and disk read counters added to query engine cache metrics, giving operators direct visibility into cache behavior for performance tuning. |

## **🌟 Open Source Releases**

| Project | Description |
| --- | --- |
| **LanceDB** v0.30.2 [Release notes](https://github.com/lancedb/lancedb/releases/tag/python-v0.30.2) | • Parallel inserts for remote tables via multipart write improves throughput for large uploads ([#3071](https://github.com/lancedb/lancedb/pull/3071)) • New type-safe expression builder API in Python for constructing queries programmatically ([#3150](https://github.com/lancedb/lancedb/pull/3150)) • Node.js SDK now supports Float16, Float64, and Uint8 vector queries ([#3193](https://github.com/lancedb/lancedb/pull/3193)) • Progress bar added to `add()` for visibility during bulk inserts ([#3067](https://github.com/lancedb/lancedb/pull/3067)) |
| **lance-duckdb** v0.5.4 [Release notes](https://github.com/lance-format/lance-duckdb/releases) | • Added dataset and session reuse across read, write, and search paths—including per-connection dataset caching and shared per-database sessions—reducing overhead for repeated operations ([#182](https://github.com/lance-format/lance-duckdb/pull/182), [#183](https://github.com/lance-format/lance-duckdb/pull/183), [#185](https://github.com/lance-format/lance-duckdb/pull/185), [#188](https://github.com/lance-format/lance-duckdb/pull/188), [#189](https://github.com/lance-format/lance-duckdb/pull/189)) • Vector index controls now available in hybrid search ([#190](https://github.com/lance-format/lance-duckdb/pull/190)) |
| **lance-namespace** v0.7.0 – v0.7.2 [Release notes](https://github.com/lance-format/lance-namespace/releases) | • `CreateTable` REST API now supports storage options and properties; `CreateEmptyTable` removed ([#330](https://github.com/lance-format/lance-namespace/pull/330)) • `ListTables` now includes declared tables by default via `include_declared=true` ([#332](https://github.com/lance-format/lance-namespace/pull/332)) • `DescribeTable` request adds `check_declared` parameter for explicit declared table lookups ([#334](https://github.com/lance-format/lance-namespace/pull/334)) |

## **🫶 Community Contributions**

Thank you to contributors from Google, Bytedance, Tencent, Baidu, Adobe, Uber, Pinterest, Microsoft, Luma AI, and [Rerun.io](http://rerun.io) for improvements across storage, indexing, query execution, distributed processing, and ecosystem integrations in LanceDB, Lance, and the broader ecosystem.

**Notable contributions this month:**

* [@beinan](https://github.com/beinan) — Added `Dataset.sample()` API to Java SDK and zonemap index segments support, enabling efficient sampling and index-based filtering in JVM environments
* [@hushengquan](https://github.com/hushengquan) — Improved I/O throughput by submitting requests eagerly in `FullZipScheduler`, reducing latency for batch reads
* [@zhangyue19921010](https://github.com/zhangyue19921010) — Extended dictionary-namespace with table operations and exposed base-scoped store bindings to Python, enabling richer catalog integration
* [@dentiny](https://github.com/dentiny) — Fixed float64-stored number detection in JSON type extraction and corrected logical operator bug in conflict resolver
* [@pratik0316](https://github.com/pratik0316) — Added type-safe expression builder API to Python SDK, enabling compile-time query validation
* [@VedantMadane](https://github.com/VedantMadane) — Extended Node.js SDK to support Float16, Float64, and Uint8 vector queries, broadening precision options for embeddings
* [@myandpr](https://github.com/myandpr) — Fixed `max_batch_length` handling for Rust vector and hybrid queries, ensuring consistent batch size limits
* [@ivscheianu](https://github.com/ivscheianu) — Prevented arithmetic overflow in U64Segment encoding for sparse/extreme row ID ranges, improving stability for large datasets
* [@LuciferYang](https://github.com/LuciferYang) — Improved robustness by warning and clamping `LANCE_INITIAL_UPLOAD_SIZE` instead of panicking on invalid values

A heartfelt thank you to our community contributors of Lance and LanceDB this past month:

[@adaworldapi](https://github.com/adaworldapi) • [@atakanyenel](https://github.com/atakanyenel) • [@beinan](https://github.com/beinan) • [@bryanck](https://github.com/bryanck) • [@butnaruandrei](https://github.com/butnaruandrei) • [@chenghao-guo](https://github.com/chenghao-guo) • [@danielmao1](https://github.com/danielmao1) • [@dardourimohamed](https://github.com/dardourimohamed) • [@dcfocus](https://github.com/dcfocus) • [@dentiny](https://github.com/dentiny) • [@dhruvgarg111](https://github.com/dhruvgarg111) • [@emilk](https://github.com/emilk) • [@fangbo](https://github.com/fangbo) • [@fightboxing](https://github.com/fightboxing) • [@frankliee](https://github.com/frankliee) • [@gezi-lzq](https://github.com/gezi-lzq) • [@huahuay](https://github.com/huahuay) • [@hushengquan](https://github.com/hushengquan) • [@its-tanay](https://github.com/its-tanay) • [@ivscheianu](https://github.com/ivscheianu) • [@jaystarshot](https://github.com/jaystarshot) • [@jerryjch](https://github.com/jerryjch) • [@jiaoew1991](https://github.com/jiaoew1991) • [@jja725](https://github.com/jja725) • [@justsml](https://github.com/justsml) • [@kaan-simbe](https://github.com/kaan-simbe) • [@lakshjain7](https://github.com/lakshjain7) • [@lennylxx](https://github.com/lennylxx) • [@lilei1128](https://github.com/lilei1128) • [@luciferyang](https://github.com/luciferyang) • [@majiayu000](https://github.com/majiayu000) • [@majin1102](https://github.com/majin1102) • [@myandpr](https://github.com/myandpr) • [@pengw0048](https://github.com/pengw0048) • [@ppei-wang](https://github.com/ppei-wang) • [@pratik0316](https://github.com/pratik0316) • [@puchengy](https://github.com/puchengy) • [@qingfeng-occ](https://github.com/qingfeng-occ) • [@shiwk](https://github.com/shiwk) • [@shmilygkd](https://github.com/shmilygkd) • [@sinianluoye](https://github.com/sinianluoye) • [@snigenigmatic](https://github.com/snigenigmatic) • [@summaryzb](https://github.com/summaryzb) • [@timsaucer](https://github.com/timsaucer) • [@tobocop2](https://github.com/tobocop2) • [@vedantmadane](https://github.com/vedantmadane) • [@wojiaodoubao](https://github.com/wojiaodoubao) • [@wombatu-kun](https://github.com/wombatu-kun) • [@xiaguanglei](https://github.com/xiaguanglei) • [@xodn348](https://github.com/xodn348) • [@xuqianjin-stars](https://github.com/xuqianjin-stars) • [@xuzha](https://github.com/xuzha) • [@xuzifu666](https://github.com/xuzifu666) • [@yangmeilly](https://github.com/yangmeilly) • [@yangshangqing95](https://github.com/yangshangqing95) • [@ysbf](https://github.com/ysbf) • [@yxd-ym](https://github.com/yxd-ym) • [@zehiko](https://github.com/zehiko) • [@zelys-dfkh](https://github.com/zelys-dfkh) • [@zhangyue19921010](https://github.com/zhangyue19921010) • [@ztorchan](https://github.com/ztorchan)

## **🤝 Lance Community Sync Recap**

This month's community sync highlighted Lance 2.2 file format benchmarks that showed major performance gains, alongside new Blob V2 and variant benchmarks, while the Lance 4.0.0 SDK is out and work has started on the 6.0.0 release candidate.

The next Lance Community Sync will take place on **Thursday May 7**.

* 📬 [Subscribe to the Lance mailing list to receive the meeting invite →](https://groups.google.com/a/lance.org/g/dev)
* 📄 [Add discussion topics to the meeting notes →](https://docs.google.com/document/d/1cP058pJLVjj39DGaFV5yHI6qyWBwp1B2YKyIwXzYlAI/edit?usp=sharing)‍
* 📺 [Watch previous recordings →](https://www.youtube.com/playlist?list=PLQysAafL04jUgOj7j6mCE5fcZEBB9Amu9)

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-009](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-009.avif)

[ChanChan Mao](/author/chanchan-mao)

Developer Relations @ LanceDB

[GitHub](https://github.com/ccmao1130)[Linkedin](https://www.linkedin.com/in/chanchanmao/)

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-010](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-010.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-011](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-011.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736-fig-012](../images/2341-https-www-lancedb-com-blog-newsletter-april-2026-ae974736/figure-012.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb