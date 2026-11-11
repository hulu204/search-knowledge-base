---
title: 'https://www.lancedb.com/blog/newsletter-july-2026'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/newsletter-july-2026
account: 
origin: en-rss
---
# ⚡ Multi-Bit RaBitQ Without Refine, 🌋 Bytedance’s Lance-Based AI Stack, 🤖 Lance for Embodied AI Data

[ChanChan Mao](/author/chanchan-mao)

•

August 7, 2026

•

[Newsletter](/category/newsletter)

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-001](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## ⚡ RaBitQ Gets Faster: Higher Recall, Lower Latency, Query-Time Control

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-002](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-002.png)

High-recall vector search usually requires a refine step that re-ranks candidates against raw full-precision vectors — expensive in memory and tail latency. Multi-bit IVF\_RQ in LanceDB now reaches 96.2% recall@10 with 5-bit codes at 2.6x lower p99 latency than unrefined IVF\_PQ, no raw vectors needed.

New SIMD kernels and a fast rotation pass push throughput to 3.3x higher QPS per core. The approx\_mode parameter lets you tune recall vs. latency at query time — fast, normal, or accurate — on the same index.

[Read more →](https://www.lancedb.com/blog/rabitq-gets-faster-higher-recall-lower-latency-query-time-control)

## 💡 Case Study

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-003](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-003.png)

Volcano Engine replaced single-node IVFPQ training (500GB+ memory, multi-day runs) with distributed index training across Lance fragments, cutting a 7-day model training pipeline to 1 day at 95% GPU utilization. Binary copy compaction skips decode/re-encode entirely, dropping compaction time from 418s to 15s on 5M-row tables.

ArkClaw, their managed OpenClaw deployment, runs memory-lancedb-ultra at 100K+ QPS with hybrid FTS+vector search and GitforMemory—agent memory branching built on Lance’s native branching API.

[Volcano Engine’s Lance-Based AI Stack →](https://www.lancedb.com/blog/volcano-engine-lance-agent-memory)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-004](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-004.png)

China Merchants Lion Rock AI Lab rebuilt their robotics data pipeline on Lance to handle 100 Hz robot-arm states, multi-camera video streams, and per-frame annotations in a single table row. Long videos are sliced into GOP-sized blobs, preserving video-level compression while enabling frame-level random access without full-video decoding.

The result: 1.7–6.0× faster random reads than LeRobot, ~42% storage savings, and a single S3 copy that collection, processing, and training all read/write directly—eliminating the package→upload→download→reupload cycle.

[Lance for Embodied AI Data →](https://www.lancedb.com/blog/china-merchants-lancedb-story)

## 📚 Also Published

* [From Messy PDFs to Verifiable Answers with LiteParse and LanceDB](https://www.lancedb.com/blog/from-messy-pdfs-to-verifiable-answers-with-liteparse-and-lancedb)
* [Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB](https://www.lancedb.com/blog/make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb)

## 📅 Upcoming Events

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-005](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-005.png)

**Actuate** — Aug 18-19, 2026 · San Francisco, CA

LanceDB is sponsoring Actuate by Foxglove. Stop by Booth 15 to discuss data infrastructure for robotics—specifically how to make video, LiDAR, sensor data, and embeddings searchable for curation, training, and evaluation workflows.

We also have a lightning talk at 1pm on Aug 18 at the breakout stage!

[Register →](https://actuate.foxglove.dev/)

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-006](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-006.png)

**Ray Summit** — Aug 24-26, 2026 · San Francisco

LanceDB is sponsoring Ray Summit by Anyscale, stop by our booth!

🎤 **How Exa Indexes the Entire Web: Ray Data and Lance at Billion-Document Scale**

*Lei Xu (LanceDB) · Hubert Yuan (Exa)*

Catch our joint session with Exa covering how they index hundreds of billions of web pages using Lance and Ray Data—including dependency-graph-driven execution, fragment-level patching to avoid write amplification, and stateful model reuse via Ray Actors.

[Register →](https://www.anyscale.com/ray-summit/2026)

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-007](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-007.png)

**Composable Data Management Systems (CDMS)**  — September 4, 2026 · Boston, MA

🎤 **The AI Frontier for Composable Data Systems**

*Weston Pace (LanceDB)*

The talk explores how composable data systems with well-defined API boundaries and plugin architectures are positioned to support agentic workloads, covering architectural challenges like stability boundaries, business considerations around balancing enterprise and open source value, and the shift in development focus from implementation to review and design as AI-assisted contributions accelerate.

[Register →](https://cdmsworkshop.github.io/2026/keynote.html)

## 🏗️ LanceDB Enterprise Updates

### Performance

* **Lock-free per-table freshness check** — A lock-free atomic check replaces the per-table lock on read freshness, removing a scheduler handoff that capped throughput on busy tables; on a 126M-row table, ID-based row lookups at concurrency 64 rose from about 1,570 to 5,954 requests per second.
* **Full-text search index metadata caching** — A new cache for full-text-search index snapshots avoids a storage read on every request; at 768 concurrent requests, a diagnostic benchmark measured 93.7% higher throughput and 56% lower median latency.
* **Faster result transfer for wide-column queries** — Higher default connection-pool and buffer-pool sizes speed up result transfer between nodes; on wide-column take queries (150KB rows, 100 results, ~16MB per response), throughput rose 13.5% and median wire-transfer latency dropped from 226ms to 71ms.
* **Lower-contention index cache backend** — A lower-contention backend for the index cache's memory tier removes per-read bookkeeping that scaled with core count; on a 320-core host under cache-heavy full-text-search load, throughput rose from 18.9 to 191.3 queries per second.
* **Faster distributed full-text-search planning** — Distributed full-text-search query plans now decode index segment metadata synchronously instead of routing it through blocking-pool scheduling; in a controlled benchmark, throughput rose 27.9–31.1% and p99 latency fell 22.3–24.0% across query types.

### Features

| Feature | Description |
| --- | --- |
| Job management | Job views now support instant search across all fields, job cancellation, per-job failure reasons with retryability, archived job history, and a SQL `SHOW JOBS` statement, giving unified visibility into background jobs like index builds and cache prewarming alongside Feature Engineering jobs. |
| Table history | Tables now have a history view showing every version with its schema changes and row count, with a diff against main for any version and pagination to scroll back through history. |
| Bring-your-own-bucket | Enterprise clusters can bind to a customer-owned storage bucket or container instead of provisioned storage, covering the full path from cluster creation through the data plane, with single-writer ownership enforcement and an installer access preflight check. |
| Distributed ngram, bloom filter, r-tree, zone map & HNSW indexes | The distributed indexer now supports building these five additional index types across multiple workers, broadening the set of index types that can be built at scale on large tables. |

## 🌟 Open Source Releases

| Project | Description |
| --- | --- |
| **Lance** v8.0.0 – v9.0.0 [Release notes](https://github.com/lance-format/lance/releases) | • FTS v2 is now the default index format, with bulk MAXSCORE search for top-k disjunctions ([#7512](https://github.com/lance-format/lance/pull/7512), [#7603](https://github.com/lance-format/lance/pull/7603)) • Data overlay files enable in-place column updates without full fragment rewrites; compaction now triggers on overlay count ([#7535](https://github.com/lance-format/lance/pull/7535), [#7536](https://github.com/lance-format/lance/pull/7536), [#7772](https://github.com/lance-format/lance/pull/7772)) • Streaming IVF k-means training for large datasets ([#6913](https://github.com/lance-format/lance/pull/6913)) • Cold reads up to 8× faster via lazy column metadata loading ([#7375](https://github.com/lance-format/lance/pull/7375)) • Object store metrics now published via the `metrics` crate and exposed through OpenTelemetry in Python ([#7533](https://github.com/lance-format/lance/pull/7533), [#7537](https://github.com/lance-format/lance/pull/7537)) • MemWAL adds row-level deletes via tombstones, prefiltered vector/FTS search, and snapshot-consistent fresh-tier membership ([#7417](https://github.com/lance-format/lance/pull/7417), [#7138](https://github.com/lance-format/lance/pull/7138), [#7215](https://github.com/lance-format/lance/pull/7215)) |
| **LanceDB** v0.34.0 – v0.36.0 [Release notes](https://github.com/lancedb/lancedb/releases) | • **Branch diff and merge**: promote columns added on a branch onto main via new client APIs ([#3686](https://github.com/lancedb/lancedb/pull/3686)) • **Elastic dataloader for PyTorch**: iterable dataset that dynamically adjusts batch sizes based on memory pressure ([#3509](https://github.com/lancedb/lancedb/pull/3509)); remote tables now work with PyTorch dataloaders ([#3432](https://github.com/lancedb/lancedb/pull/3432)) • **OpenTelemetry metrics**: Lance internal metrics now exposed via OTel in Python and Node bindings ([#3609](https://github.com/lancedb/lancedb/pull/3609)) • **OAuth authentication**: new `OAuth` header provider for connecting to LanceDB Cloud with OAuth tokens ([#3579](https://github.com/lancedb/lancedb/pull/3579), [#3586](https://github.com/lancedb/lancedb/pull/3586)) |
| **lance-namespace-impls** v0.4.1 [Release notes](https://github.com/lance-format/lance-namespace-impls/releases) | • Lance tables in Hive Metastore are now stored as external tables, preventing accidental data deletion when dropping tables via HMS ([#146](https://github.com/lance-format/lance-namespace-impls/pull/146)) |
| **lance-namespace** v0.9.0 [Release notes](https://github.com/lance-format/lance-namespace/releases) | • **Breaking:** REST spec now includes response context, requiring updates to clients consuming the API ([#358](https://github.com/lance-format/lance-namespace/pull/358)) • Added `tag` field to `DescribeTableRequest` for table version/tag-based lookups ([#345](https://github.com/lance-format/lance-namespace/pull/345)) |
| **lance-context** v0.5.1 – v0.6.5 [Release notes](https://github.com/lance-format/lance-context/releases) | • New RolloutDB for RL rollout storage: native `RolloutStore` with MemWAL ingest, server-id sharding, count/time-triggered WAL merges, and filtered/ordered trajectory reads ([#124](https://github.com/lance-format/lance-context/pull/124), [#126](https://github.com/lance-format/lance-context/pull/126), [#142](https://github.com/lance-format/lance-context/pull/142), [#158](https://github.com/lance-format/lance-context/pull/158)) • User-defined schemas via `SchemaSpec` and `GenericStore`, exposed across Rust core, HTTP server, client, and Python bindings ([#218](https://github.com/lance-format/lance-context/pull/218), [#220](https://github.com/lance-format/lance-context/pull/220)) • Control-plane master service with React UI for experiment browsing, centralized compaction/WAL-merge scheduler (etcd-backed HA), Prometheus `/metrics` endpoints, and stats-table observability ([#137](https://github.com/lance-format/lance-context/pull/137), [#139](https://github.com/lance-format/lance-context/pull/139), [#140](https://github.com/lance-format/lance-context/pull/140), [#154](https://github.com/lance-format/lance-context/pull/154)) |
| **lance-ray** v0.5.0 [Release notes](https://github.com/lance-format/lance-ray/releases) | • Distributed index building now supports IVF\_RQ vector indexes ([#5228](https://github.com/lance-format/lance-ray/pull/5228)), bitmap indexes ([#5169](https://github.com/lance-format/lance-ray/pull/5169)), and ZoneMap indexes ([#5214](https://github.com/lance-format/lance-ray/pull/5214)), with configurable `num_segments` for controlling parallelism ([#5229](https://github.com/lance-format/lance-ray/pull/5229)) • New `add_columns_from` enables distributed column addition across Ray workers ([#4923](https://github.com/lance-format/lance-ray/pull/4923)); nested field paths now supported in Ray workflows ([#5173](https://github.com/lance-format/lance-ray/pull/5173)) • Vector search performance improved by sharing IVF centroids and PQ codebooks across Ray tasks ([#4744](https://github.com/lance-format/lance-ray/pull/4744)) and reusing a global Ray pool with pickled dataset references ([#5149](https://github.com/lance-format/lance-ray/pull/5149), [#5157](https://github.com/lance-format/lance-ray/pull/5157)) |
| **lance-spark** v0.6.0 – v0.7.1 [Release notes](https://github.com/lance-format/lance-spark/releases) | • Spark 4.2 support added ([#696](https://github.com/lance-format/lance-spark/pull/696)) • Full-text search SQL extension for querying Lance tables directly via Spark SQL ([#501](https://github.com/lance-format/lance-spark/pull/501)) • DDL support for branch and tag operations, enabling version control workflows from Spark ([#576](https://github.com/lance-format/lance-spark/pull/576), [#654](https://github.com/lance-format/lance-spark/pull/654)) • Deferred index creation with `WITH (train=false)` for creating indexes without immediate training ([#558](https://github.com/lance-format/lance-spark/pull/558)) |

## 🫶 Community Contributions

Thank you to contributors from Bytedance, Uber, Pinterest, Tencent, Baidu, Adobe, NVIDIA for improvements across storage, indexing, query execution, distributed processing, and ecosystem integrations in LanceDB, Lance, and the broader ecosystem.

**Notable contributions this month:**

* [@XuQianJin-Stars](https://github.com/XuQianJin-Stars) — Added GooseFS object store support and implemented namespace directory table operations (add/alter/drop columns, update, delete)
* [@zhangyue19921010](https://github.com/zhangyue19921010) — Introduced RowAddrRemap structure to prevent OOM during compaction and migrated distributed BTree builds to segmented index framework
* [@ddupg](https://github.com/ddupg) — Added TOS (Volcengine) object store support and enabled distributed vector/FTS segment builds with direct commit paths
* [@tobocop2](https://github.com/tobocop2) — Enabled runtime SIMD dispatch for pre-Haswell x86\_64 builds, expanding hardware compatibility for from-source installations
* [@valkum](https://github.com/valkum) — Added Dict-to-value-type casting in alter\_columns schema evolution and fixed datafusion filter coercion for dictionary-encoded columns
* [@wombatu-kun](https://github.com/wombatu-kun) — Accelerated regex and infix LIKE queries using ngram indexes and exposed per-query I/O metrics on ANN operators
* [@Ali2Arslan](https://github.com/Ali2Arslan) — Enabled reading column min/max directly from ZoneMap without full scans and implemented single-flight scalar index opening
* [@beinan](https://github.com/beinan) — Implemented FM-Index scalar index for exact substring search and added Java schema override for fragment writes
* [@gstamatakis95](https://github.com/gstamatakis95) — Added shared RaBitQ rotation for distributed IVF\_RQ builds and eliminated HEAD calls when opening vector indexes
* [@LuciferYang](https://github.com/LuciferYang) — Added Spark 4.2 support and contributed zero-copy BFloat16Array construction for improved memory efficiency

A heartfelt thank you to our community contributors of Lance and LanceDB this past month:

[@2dmurali](https://github.com/2dmurali) • [@a-agmon](https://github.com/a-agmon) • [@adibaadi](https://github.com/adibaadi) • [@aimanmalib](https://github.com/aimanmalib) • [@alowator](https://github.com/alowator) • [@ar-maan05](https://github.com/ar-maan05) • [@bugwz](https://github.com/bugwz) • [@chakshu-dhannawat](https://github.com/chakshu-dhannawat) • [@charleshuang119](https://github.com/charleshuang119) • [@chuenchen309](https://github.com/chuenchen309) • [@ckarnell](https://github.com/ckarnell) • [@claydugo](https://github.com/claydugo) • [@clearlove10-c](https://github.com/clearlove10-c) • [@coyasong](https://github.com/coyasong) • [@cswpy](https://github.com/cswpy) • [@danielmao1](https://github.com/danielmao1) • [@dcfocus](https://github.com/dcfocus) • [@dentiny](https://github.com/dentiny) • [@devteamaegis](https://github.com/devteamaegis) • [@ebyhr](https://github.com/ebyhr) • [@ecthlion](https://github.com/ecthlion) • [@erandagan](https://github.com/erandagan) • [@everysympathy](https://github.com/everysympathy) • [@expyron](https://github.com/expyron) • [@fangbo](https://github.com/fangbo) • [@fanng1](https://github.com/fanng1) • [@farmerchillax](https://github.com/farmerchillax) • [@fl0-m](https://github.com/fl0-m) • [@geserdugarov](https://github.com/geserdugarov) • [@ghx5t-sol](https://github.com/ghx5t-sol) • [@glitch-ux](https://github.com/glitch-ux) • [@goutamadwant](https://github.com/goutamadwant) • [@haochengliu](https://github.com/haochengliu) • [@haroldbenoit](https://github.com/haroldbenoit) • [@hashwnath](https://github.com/hashwnath) • [@hellower](https://github.com/hellower) • [@hfutatzhanghb](https://github.com/hfutatzhanghb) • [@huahuay](https://github.com/huahuay) • [@hushengquan](https://github.com/hushengquan) • [@ivscheianu](https://github.com/ivscheianu) • [@j7nhai](https://github.com/j7nhai) • [@jay-ju](https://github.com/jay-ju) • [@jiaoew1991](https://github.com/jiaoew1991) • [@jiaqizho](https://github.com/jiaqizho) • [@jo-migo](https://github.com/jo-migo) • [@joaquinhuigomez](https://github.com/joaquinhuigomez) • [@jsap0914](https://github.com/jsap0914) • [@jtuglu1](https://github.com/jtuglu1) • [@julianyg](https://github.com/julianyg) • [@kaan-simbe](https://github.com/kaan-simbe) • [@kobihikri](https://github.com/kobihikri) • [@lakshjain7](https://github.com/lakshjain7) • [@leepokai](https://github.com/leepokai) • [@leohoare](https://github.com/leohoare) • [@leoreeyang](https://github.com/leoreeyang) • [@lixmgl](https://github.com/lixmgl) • [@malinjawi](https://github.com/malinjawi) • [@mansiverma897993](https://github.com/mansiverma897993) • [@markmcd](https://github.com/markmcd) • [@mateuszossgit](https://github.com/mateuszossgit) • [@mediamana](https://github.com/mediamana) • [@missing-identity](https://github.com/missing-identity) • [@mmatczuk](https://github.com/mmatczuk) • [@mocobeta](https://github.com/mocobeta) • [@moongtnt](https://github.com/moongtnt) • [@morales-t-netflix](https://github.com/morales-t-netflix) • [@neo-x7](https://github.com/neo-x7) • [@niraj-mx07](https://github.com/niraj-mx07) • [@nuthalapativarun](https://github.com/nuthalapativarun) • [@nyl3532016](https://github.com/nyl3532016) • [@omkar-334](https://github.com/omkar-334) • [@plotor](https://github.com/plotor) • [@pranavachar01](https://github.com/pranavachar01) • [@prrao87](https://github.com/prrao87) • [@puchengy](https://github.com/puchengy) • [@rtmalikian](https://github.com/rtmalikian) • [@ryantqiu](https://github.com/ryantqiu) • [@saitejabandaru-in](https://github.com/saitejabandaru-in) • [@sanskar-singh-2403](https://github.com/sanskar-singh-2403) • [@sapnilb15](https://github.com/sapnilb15) • [@say-5](https://github.com/say-5) • [@sbrunk](https://github.com/sbrunk) • [@sezruby](https://github.com/sezruby) • [@shizoqua](https://github.com/shizoqua) • [@skycutter](https://github.com/skycutter) • [@skyshineb](https://github.com/skyshineb) • [@sohumt123](https://github.com/sohumt123) • [@solaris-star](https://github.com/solaris-star) • [@spectual](https://github.com/spectual) • [@ssrheart425](https://github.com/ssrheart425) • [@stumpylog](https://github.com/stumpylog) • [@summaryzb](https://github.com/summaryzb) • [@sushanth012](https://github.com/sushanth012) • [@timsaucer](https://github.com/timsaucer) • [@touch-of-grey](https://github.com/touch-of-grey) • [@u70b3](https://github.com/u70b3) • [@vibhujawa](https://github.com/vibhujawa) • [@vitaliy-pikalo](https://github.com/vitaliy-pikalo) • [@vortex-captain](https://github.com/vortex-captain) • [@wayneadams](https://github.com/wayneadams) • [@wending-y](https://github.com/wending-y) • [@whitewooood](https://github.com/whitewooood) • [@wirybeaver](https://github.com/wirybeaver) • [@wulansari999](https://github.com/wulansari999) • [@xingsuo-zbz](https://github.com/xingsuo-zbz) • [@xixigoodluck](https://github.com/xixigoodluck) • [@xloya](https://github.com/xloya) • [@xtangxtang](https://github.com/xtangxtang) • [@xuxiaoqiang666](https://github.com/xuxiaoqiang666) • [@xuzha](https://github.com/xuzha) • [@yanghua](https://github.com/yanghua) • [@yangjunz](https://github.com/yangjunz) • [@yangshangqing95](https://github.com/yangshangqing95) • [@yaodong-shen](https://github.com/yaodong-shen) • [@yesunbmh](https://github.com/yesunbmh) • [@yeung108](https://github.com/yeung108) • [@yohahaha](https://github.com/yohahaha) • [@ytyky](https://github.com/ytyky) • [@yuju-huang](https://github.com/yuju-huang) • [@yuvalif](https://github.com/yuvalif) • [@ywu342](https://github.com/ywu342) • [@yyzhao2025](https://github.com/yyzhao2025) • [@zhangyang0418](https://github.com/zhangyang0418) • [@zlepper](https://github.com/zlepper) • [@ztorchan](https://github.com/ztorchan)

## 🤝 Lance Community Sync Recap

Community sync sessions this month covered several significant proposals and releases. On the proposal side, discussions included new low-level APIs, a blob session API, multi-table commit and branching scalability improvements, and a design for scaling to millions of fragments. The team announced the Lance 9.0.0 SDK release with a 10.0.0 beta incoming, highlighted a 7x FTS performance improvement, and introduced Lance Gatekeeper, an automated PR review bot. Additional topics included the lance.org website redesign with plans for community content, and a proposal to streamline the format-change voting process by moving votes into PRs with a shortened 72-hour window.

The next Lance Community Sync will take place on **Thursday, August 13 @ 9am PT**.

* [📬 Subscribe to the Lance mailing list to receive the meeting invite →](https://groups.google.com/a/lance.org/g/dev)
* [📄 Add discussion topics to the meeting notes →](https://docs.google.com/document/d/1cP058pJLVjj39DGaFV5yHI6qyWBwp1B2YKyIwXzYlAI/edit?usp=sharing)
* [📺 Watch previous recordings →](https://www.youtube.com/playlist?list=PLQysAafL04jUgOj7j6mCE5fcZEBB9Amu9)

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-008](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-008.avif)

[ChanChan Mao](/author/chanchan-mao)

Developer Relations @ LanceDB

[GitHub](https://github.com/ccmao1130)[Linkedin](https://www.linkedin.com/in/chanchanmao/)

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-009](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-009.png)

### ⚡ Multi-Bit RaBitQ Without Refine, 🌋 Bytedance’s Lance-Based AI Stack, 🤖 Lance for Embodied AI Data

ChanChan Mao

•

July 31, 2026

newsletter-july-2026

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-010](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-010.png)

### Feature Engineering for Multimodal Data: From Laptop to Cluster with LanceDB

Justin Miller

•

August 5, 2026

feature-engineering-examples

![2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec-fig-011](../images/2360-https-www-lancedb-com-blog-newsletter-july-2026-60b8c3ec/figure-011.png)

### Why CrewAI Rebuilt Agent Memory on LanceDB, Powering 2B+ Agent Executions

CrewAI

•

July 23, 2026

crewai-rebuilt-agent-memory-on-lancedb