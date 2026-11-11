---
title: 'https://www.lancedb.com/blog/newsletter-june-2026'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/newsletter-june-2026
account: 
origin: en-rss
---
# 📊 Lance vs Delta vs Iceberg, 🔗 Lance Blob V2 Late Materialization, 🤖 Stable-Worldmodel Research Platform

[ChanChan Mao](/author/chanchan-mao)

•

July 9, 2026

•

[Newsletter](/category/newsletter)

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-001](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## ‍📊 A Metadata Benchmark of Lance, Delta Lake, and Iceberg on S3

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-002](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-002.webp)

In a 10,000-commit benchmark on S3, Lance averaged 140ms commit latency versus 534ms for Delta Lake and 457ms for Iceberg. Active metadata footprint stayed at 0.78 MiB compared to 42+ MiB for Iceberg.

At 200 concurrent writers, Lance saw a 16% failure rate versus 88% for Delta Lake and 89–94% for Iceberg. The gap comes from publishing compact manifests directly to storage instead of relying on log replay or a catalog service.

[Read more →](https://www.lancedb.com/blog/a-metadata-benchmark-of-lance-delta-lake-and-iceberg-on-s3)

## 🔗 Lance Blob V2: Late Materialization for Large Binary Data in Spark

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-003](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-003.webp)

Updating a label on a row with a 50MB video shouldn’t require Spark to read that video — Lance Blob V2 keeps blob columns as lightweight descriptors through the query plan, materializing bytes only at write time.

`UPDATE`, `MERGE`, `INSERT…SELECT`, and joins all carry copy tokens that resolve during the write path, so mixed tables with small thumbnails and large clips can use different layouts row by row without schema changes. The SQL stays the same — what changes is that Spark moves references instead of payloads.

[Read more →](https://www.lancedb.com/blog/lance-blob-v2-late-materialization-for-large-binary-data-in-spark)

## 🤖 Stable-Worldmodel: A High Performance Platform for Reproducible World Model Research

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-004](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-004.webp)

stable-worldmodel’s Lance data layer delivers ~4,800 samples/sec on Push-T versus ~1,400 for HDF5 locally, and ~3,200 samples/sec reading directly from S3 — training from object storage without syncing to local disk first.

The loader is URI-agnostic — `s3://`, `gs://`, HF Buckets, or local paths all run the same code — and Lance’s zero-copy data evolution adds vector, FTS, or hybrid indexes to training data at no performance cost. LeWorldModel trains end-to-end from pixels on a single H200 in hours, hitting 94% success on Push-T with 50× less planning latency than DINO-WM.

[Read more →](https://www.lancedb.com/blog/stable-worldmodel-a-high-performance-platform-for-reproducible-world-model-research)

## 📚 Also Published

* [Scalable Feature Engineering on Multimodal Datasets](https://www.lancedb.com/blog/scalable-feature-engineering-on-multimodal-datasets)
* [Semantic Memory for Hermes Agent with LanceDB](https://www.lancedb.com/blog/semantic-memory-for-hermes-agent-with-lancedb)
* [Faster VLM Fine-Tuning With Materialized Model Features in LanceDB](https://www.lancedb.com/blog/faster-vlm-fine-tuning-with-materialized-model-features-in-lancedb)

## 🎤 Talks & Recordings

**Less Tokio is More Tokio: Strategies for Accelerating a Rust Native Search Database by Weston Pace, Lu Qiu**

*Weston Pace (LanceDB) · Lu Qiu (LanceDB)*

Weston Pace and Lu Qiu present how LanceDB achieved storage roofline performance by redesigning their Rust I/O loop to use fewer Tokio tasks, eagerly poll futures during I/O submission, and adopt a push/pull scheduling API—along with profiling techniques for complex async applications.

[Watch the recording →](https://www.youtube.com/watch?v=Wc7f_IP5MEs)

**Agents Will Break Your Stack**

*Chang She (LanceDB) · Ben Lorica (Gradient Flow)*

Chang She, co-founder and CEO of LanceDB, discusses with Ben Lorica why traditional analytical tools like Pandas and Parquet fall short for AI workloads, the concept of a “multimodal lakehouse,” and the unique data storage and retrieval challenges that AI agents introduce.

[Watch the recording →](https://www.youtube.com/watch?v=duoojh4CYWs)

**Trillion is the New Billion: Managing Really Large Multimodal Datasets for AI**

*Lei Xu (LanceDB)*

This talk covers the data infrastructure challenges of managing trillion-row multimodal datasets for AI workloads, explaining why existing systems fall short for storing large blobs, supporting search/curation/training directly from datasets, and handling distributed pipelines across clouds—with a look under the hood at how Lance format and LanceDB address these problems and fit alongside Iceberg.

[Watch the recording →](https://youtu.be/z01r8DYsY0I?si=lq8bVFMpzdOdaYYM)

## 📸 AI Engineer World's Fair in SF

We had a great time at AI Engineer World's Fair in San Francisco last week! Thanks to everyone who stopped by the booth to say hi and dive into LanceDB internals.

It was great meeting everyone who came out to our events last week: SPIN SF with Theory Ventures & Ollama and USA World Cup Watch Party with Exa, Extend, and Fastino Labs. Both were packed, both were a good time, and we'd absolutely do them again.

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-005](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-005.webp)

## 📅 Upcoming Events

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-006](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-006.png)

**AI Lakehouse Meetup** — July 15, 2026 · 5-8pm PT · San Jose, CA

*ChanChan Mao (LanceDB) · Lu Qiu (LanceDB)*

Covers building multimodal lakehouse with Lance and LanceDB—unified vector, full-text, and SQL search across text, images, and embeddings without forcing separate systems for each modality. Hosted at Cloudera’s San Jose office with talks by ChanChan Mao and Lu Qiu from LanceDB.

[Register →](https://luma.com/n8aycq3j)

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-007](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-007.jpg)

**Ceph: Object Storage Meets Vector Search** — July 16, 2026 · 10am PT / 1pm ET · Virtual

*Prashanth Rao (LanceDB) · Kyle Bader (IBM) · Christine Bassani (Seagate)*

Ceph is integrating LanceDB libraries to deliver vector search through S3 Vectors API actions, enabling billion-scale, multi-tenant nearest neighbor search directly within existing object storage infrastructure. The implementation targets RAG workloads without requiring a separate vector database deployment.

[Register →](https://www.brighttalk.com/webcast/663/669132)

## 🏗️ LanceDB Enterprise Updates

### Performance

* **Faster query routing** — Caching per-query routing tables instead of rebuilding them on every request removed a CPU bottleneck that had cut throughput by roughly 13x under random-take (point-lookup) workloads.
* **Smarter cluster load placement** — A new two-choice consistent-hashing algorithm spreads index segments and query routing more evenly across nodes, with the underlying hash function now pinned so placement doesn't reshuffle if the Rust standard library's hash implementation changes.
* **Faster scalar index scans** — On billion-row indexes, scalar index results now serialize directly from the selected-row bitmap instead of rebuilding a merged copy, cutting CPU usage on this path by roughly 10% in steady state.**‍**
* **Lower-overhead index operations at scale** — Index status checks now read directly from stored manifests instead of disk, and index cache prewarming for multi-segment indexes drops from O(n2) to O(n) in segment count, reducing overhead as clusters grow.
* ‍**Faster reads on recently written data** — Row-limited queries used to scan every generation of the not-yet-compacted layer in full before applying the limit; bounding the scan to the requested range instead cut a test query against an 18-generation backlog to roughly 27 requests and under 3 MB.**‍**
* **Reliability** — Index cache prewarming now covers every replica group, preventing cold-cache latency spikes on groups that weren’t previously warmed.

### Features

| Feature | Description |
| --- | --- |
| Branching for tables | Tables now support git-like branches — create, delete, checkout — with indexing, caching, and writes isolated per branch, so teams can experiment without touching production data. |
| Expanded distributed indexing | The distributed indexing system now builds bitmap, label-list, and FM-index types, and distributes full-text and scalar indexing (including nested vector fields) across workers to keep pace with larger, more varied datasets. |
| Faster access to newly written data | The low-latency layer serving data before compaction now supports full-text search, row-level deletes, and partial-column updates — freshly written data is searchable and editable without waiting on compaction. |
| New job management system | A new job coordination system tracks background job runs end-to-end — discovery, event logging, and run-status APIs — improving visibility and reliability for long-running work. |
| Cache placement controls | New admin APIs and CLI commands control where index and table caches are placed and prewarmed across a cluster, reducing cold-cache query latency at scale. |

## 🌟 Open Source Releases

| Project | Description |
| --- | --- |
| **Lance** v8.0.0 [Release notes](https://github.com/lance-format/lance/releases) | • FM-Index scalar index for exact substring search with configurable multi-segment builds ([#7026](https://github.com/lance-format/lance/pull/7026), [#7123](https://github.com/lance-format/lance/pull/7123)); ngram index now accelerates regex and infix `LIKE` queries ([#7139](https://github.com/lance-format/lance/pull/7139)) • RaBitQ vector search gains approx mode ([#7179](https://github.com/lance-format/lance/pull/7179)), SIMD reranking kernels ([#7205](https://github.com/lance-format/lance/pull/7205)), and vectorized distance-table quantization ([#7241](https://github.com/lance-format/lance/pull/7241)) for faster ANN • Full-text search gets block-max WAND pruning ([#7089](https://github.com/lance-format/lance/pull/7089)), shared top-k thresholds across partitions ([#7062](https://github.com/lance-format/lance/pull/7062)), and deferred posting-list loading ([#6983](https://github.com/lance-format/lance/pull/6983)) • Write-ahead tier now matches hnswlib throughput via AVX-512 distance kernels ([#7009](https://github.com/lance-format/lance/pull/7009)) and closes the FTS gap with Lucene ([#7029](https://github.com/lance-format/lance/pull/7029)) |
| **LanceDB** v0.34.0 [Release notes](https://github.com/lancedb/lancedb/releases) | • Table branching — create, checkout, and manage branches for local and remote tables, enabling git-like version control ([#3490](https://github.com/lancedb/lancedb/pull/3490), [#3504](https://github.com/lancedb/lancedb/pull/3504), [#3540](https://github.com/lancedb/lancedb/pull/3540)) • FM-Index scalar index enables efficient `LIKE '%substring%'` queries ([#3532](https://github.com/lancedb/lancedb/pull/3532)) • Native Polars DataFrame integration alongside PyArrow and Pandas ([#3584](https://github.com/lancedb/lancedb/pull/3584)) • **Breaking:** repeated `.where()` filters now combine with AND instead of silently replacing the prior one ([#3585](https://github.com/lancedb/lancedb/pull/3585)) |
| **lance-namespace** v0.8.0 – v0.8.6 [Release notes](https://github.com/lance-format/lance-namespace/releases) | • Table branching — new create, list, and delete branch endpoints, plus a `branch` parameter that lets every table operation target a specific branch ([#350](https://github.com/lance-format/lance-namespace/pull/350), [#352](https://github.com/lance-format/lance-namespace/pull/352)) • `IndexContent` now includes `describe_indices` metadata (type, size, row counts) inline, avoiding a follow-up describe-stats call per index ([#349](https://github.com/lance-format/lance-namespace/pull/349)) • Materialized view refresh now accepts `source_task_size` to bound per-actor memory during refresh, with Java client support ([#355](https://github.com/lance-format/lance-namespace/pull/355), [#356](https://github.com/lance-format/lance-namespace/pull/356)) |
| **lance-namespace-impls** v0.4.0 [Release notes](https://github.com/lance-format/lance-namespace-impls/releases) | • `Hive2Namespace` and `Hive3Namespace` now implement `Closeable`, preventing Hive Metastore client connection leaks ([#137](https://github.com/lance-format/lance-namespace-impls/pull/137)) |
| **lance-context** v0.3.0 – v0.5.0 [Release notes](https://github.com/lance-format/lance-context/releases) | • Post-training pipeline: `export_training()` curates context records into SFT, preference (DPO/SimPO/ORPO/KTO), or RL-rollout datasets, deduped and decontaminated ([#96](https://github.com/lance-format/lance-context/pull/96), [#103](https://github.com/lance-format/lance-context/pull/103), [#111](https://github.com/lance-format/lance-context/pull/111)) • Retrieval evaluation harness: `evaluate()` and `evaluate_versions()` compute recall@k, MRR, and nDCG@k against labeled query sets, with cross-version A/B comparison ([#98](https://github.com/lance-format/lance-context/pull/98), [#110](https://github.com/lance-format/lance-context/pull/110)) • Write-path additions: MemWAL integration ([#36](https://github.com/lance-format/lance-context/pull/36)), a REST API server + Rust SDK ([#66](https://github.com/lance-format/lance-context/pull/66)), hybrid retrieval ([#76](https://github.com/lance-format/lance-context/pull/76)), upsert/partial updates ([#84](https://github.com/lance-format/lance-context/pull/84)), and bulk `upsert_many()` with indexed, sub-linear uniqueness validation replacing O(n²) scans ([#100](https://github.com/lance-format/lance-context/pull/100), [#102](https://github.com/lance-format/lance-context/pull/102)) |
| **lance-trino** v0.3.2 [Release notes](https://github.com/lance-format/lance-trino/releases) | • Predicate filters on nested/struct columns now push down to the Lance format layer ([#164](https://github.com/lance-format/lance-trino/pull/164)) • Filtered `LIMIT` queries skip full fragment enumeration and coalesce splits, cutting overhead for selective queries ([#121](https://github.com/lance-format/lance-trino/pull/121), [#159](https://github.com/lance-format/lance-trino/pull/159)) |
| **lance-spark** v0.5.0 – v0.5.1 [Release notes](https://github.com/lance-format/lance-spark/releases) | • `lance-spark` now registers `SEARCH`, `VECTOR_SEARCH`, and `HYBRID_SEARCH` as Spark SQL table functions, enabling vector and hybrid search directly in SQL ([#582](https://github.com/lance-format/lance-spark/pull/582)) • Zonemap-based fragment pruning skips fragments that fail pushed filters, and storage-partitioned joins (SPJ) eliminate shuffle for compatible tables — up to 12.1x faster on large joins ([#396](https://github.com/lance-format/lance-spark/pull/396), [#425](https://github.com/lance-format/lance-spark/pull/425)) • Float16 vector, Map type, and blob v2 read/write support expand data type coverage ([#378](https://github.com/lance-format/lance-spark/pull/378), [#379](https://github.com/lance-format/lance-spark/pull/379), [#548](https://github.com/lance-format/lance-spark/pull/548), [#560](https://github.com/lance-format/lance-spark/pull/560)) • Native update path preserves stable row IDs ([#407](https://github.com/lance-format/lance-spark/pull/407)); `use_large_var_types` avoids 2GB Arrow overflow on large columns ([#413](https://github.com/lance-format/lance-spark/pull/413)) |

## 🫶 Community Contributions

Thank you to contributors from Netflix, Uber, ByteDance, Microsoft, Pinterest, and Adobe for improvements across storage, indexing, query execution, distributed processing, and ecosystem integrations in LanceDB, Lance, and the broader ecosystem.

**Notable contributions this month:**

* [@LuciferYang](https://github.com/LuciferYang) — Added Spark 4.1 TimeType support, VectorUDT writes, and automatic UDT column round-tripping via \_\_udt field metadata in lance-spark
* [@beinan](https://github.com/beinan) — Implemented zonemap-based fragment pruning with storage-partitioned join (SPJ) support and distributed zonemap index builds in lance-spark
* [@wombatu-kun](https://github.com/wombatu-kun) — Added float16 vector type support, table rename, and ALTER TABLE SET/UNSET properties to lance-spark
* [@summaryzb](https://github.com/summaryzb) — Added Map type support, custom Lance scan metrics, and non-microsecond Arrow timestamp column reading in lance-spark
* [@ivscheianu](https://github.com/ivscheianu) — Implemented native update path with stable row-id preservation and compression config via Spark TBLPROPERTIES in lance-spark
* [@atakanyenel](https://github.com/atakanyenel) — Fixed UInt4 to BIGINT mapping and optimized split coalescing for LIMIT queries in lance-trino
* [@xuzha](https://github.com/xuzha) — Added --file-format-version option to TPC-DS benchmark data generator and exposed state metadata in lance-context Python API
* [@puchengy](https://github.com/puchengy) — Made Hive2Namespace and Hive3Namespace Closeable in lance-namespace-impls and fixed string literal parsing in lance-spark DDL
* [@ykozxy](https://github.com/ykozxy) — Added LOCATION support to CREATE TABLE for custom paths and existing datasets in lance-spark
* [@fangbo](https://github.com/fangbo) — Added configurable rows\_per\_range for range-based btree index builds and optimized vector data export to Rust for OOM prevention in lance-spark

A heartfelt thank you to our community contributors of Lance and LanceDB this past month:

[@a-agmon](https://github.com/a-agmon) • [@aheev](https://github.com/aheev) • [@aimanmalib](https://github.com/aimanmalib) • [@ali2arslan](https://github.com/ali2arslan) • [@alowator](https://github.com/alowator) • [@ar-maan05](https://github.com/ar-maan05) • [@atakanyenel](https://github.com/atakanyenel) • [@beinan](https://github.com/beinan) • [@bryanck](https://github.com/bryanck) • [@burlacio](https://github.com/burlacio) • [@butnaruandrei](https://github.com/butnaruandrei) • [@chunxutang](https://github.com/chunxutang) • [@claydugo](https://github.com/claydugo) • [@cwj0bzxg](https://github.com/cwj0bzxg) • [@danielmao1](https://github.com/danielmao1) • [@dcfocus](https://github.com/dcfocus) • [@ddupg](https://github.com/ddupg) • [@devteamaegis](https://github.com/devteamaegis) • [@dhruvgarg111](https://github.com/dhruvgarg111) • [@everysympathy](https://github.com/everysympathy) • [@fangbo](https://github.com/fangbo) • [@fanng1](https://github.com/fanng1) • [@geserdugarov](https://github.com/geserdugarov) • [@gstamatakis95](https://github.com/gstamatakis95) • [@haochengliu](https://github.com/haochengliu) • [@hashwnath](https://github.com/hashwnath) • [@hfutatzhanghb](https://github.com/hfutatzhanghb) • [@huahuay](https://github.com/huahuay) • [@ilya-zlobintsev](https://github.com/ilya-zlobintsev) • [@ivscheianu](https://github.com/ivscheianu) • [@jerryjch](https://github.com/jerryjch) • [@jiaoew1991](https://github.com/jiaoew1991) • [@jja725](https://github.com/jja725) • [@jo-migo](https://github.com/jo-migo) • [@jsap0914](https://github.com/jsap0914) • [@jtuglu1](https://github.com/jtuglu1) • [@julianyg](https://github.com/julianyg) • [@kushudai](https://github.com/kushudai) • [@lalitium](https://github.com/lalitium) • [@liuzemei](https://github.com/liuzemei) • [@lixmgl](https://github.com/lixmgl) • [@luciferyang](https://github.com/luciferyang) • [@luizfonseca](https://github.com/luizfonseca) • [@majin1102](https://github.com/majin1102) • [@mansiverma897993](https://github.com/mansiverma897993) • [@mehulbatra](https://github.com/mehulbatra) • [@missing-identity](https://github.com/missing-identity) • [@mohit-twelvelabs](https://github.com/mohit-twelvelabs) • [@mr-neutr0n](https://github.com/mr-neutr0n) • [@neo-x7](https://github.com/neo-x7) • [@noethix55555](https://github.com/noethix55555) • [@nuthalapativarun](https://github.com/nuthalapativarun) • [@paramt](https://github.com/paramt) • [@pjdurden](https://github.com/pjdurden) • [@plotor](https://github.com/plotor) • [@puchengy](https://github.com/puchengy) • [@ritwijparmar](https://github.com/ritwijparmar) • [@rtmalikian](https://github.com/rtmalikian) • [@sarahnasser576](https://github.com/sarahnasser576) • [@sezruby](https://github.com/sezruby) • [@shiwk](https://github.com/shiwk) • [@shiyan-xu-ai](https://github.com/shiyan-xu-ai) • [@sinianluoye](https://github.com/sinianluoye) • [@siriapps](https://github.com/siriapps) • [@skyshineb](https://github.com/skyshineb) • [@solarcloud7](https://github.com/solarcloud7) • [@stumpylog](https://github.com/stumpylog) • [@summaryzb](https://github.com/summaryzb) • [@touch-of-grey](https://github.com/touch-of-grey) • [@valkum](https://github.com/valkum) • [@vinaysurtani](https://github.com/vinaysurtani) • [@vitaliy-pikalo](https://github.com/vitaliy-pikalo) • [@wangxiaobao1222](https://github.com/wangxiaobao1222) • [@wending-y](https://github.com/wending-y) • [@whitewooood](https://github.com/whitewooood) • [@wirybeaver](https://github.com/wirybeaver) • [@wombatu-kun](https://github.com/wombatu-kun) • [@wulansari999](https://github.com/wulansari999) • [@xiaguanglei](https://github.com/xiaguanglei) • [@xloya](https://github.com/xloya) • [@xuqianjin-stars](https://github.com/xuqianjin-stars) • [@xushiyan](https://github.com/xushiyan) • [@xuzha](https://github.com/xuzha) • [@yanghua](https://github.com/yanghua) • [@yesunbmh](https://github.com/yesunbmh) • [@ykozxy](https://github.com/ykozxy) • [@yuanggao](https://github.com/yuanggao) • [@yuju-huang](https://github.com/yuju-huang) • [@yyzhao2025](https://github.com/yyzhao2025) • [@zhangyang0418](https://github.com/zhangyang0418) • [@zhangyue19921010](https://github.com/zhangyue19921010) • [@zouhuajian](https://github.com/zouhuajian) • [@ztorchan](https://github.com/ztorchan)

## 🤝 Lance Community Sync Recap

This month’s community syncs covered governance and format evolution for the Lance ecosystem. Format governance changes were discussed, including a requirement for votes before merging format changes and improved design review processes. A new shuffle format proposal was presented aimed at reducing IOPS and better supporting GPU workloads, alongside discussions of new indexes and core Lance architecture.

The next Lance Community Sync will take place on **Thursday, July 16 @ 9am PT**.

* [📬 Subscribe to the Lance mailing list to receive the meeting invite →](https://groups.google.com/a/lance.org/g/dev)
* [📄 Add discussion topics to the meeting notes →](https://docs.google.com/document/d/1cP058pJLVjj39DGaFV5yHI6qyWBwp1B2YKyIwXzYlAI/edit?usp=sharing)
* [📺 Watch previous recordings →](https://www.youtube.com/playlist?list=PLQysAafL04jUgOj7j6mCE5fcZEBB9Amu9)

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-008](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-008.avif)

[ChanChan Mao](/author/chanchan-mao)

Developer Relations @ LanceDB

[GitHub](https://github.com/ccmao1130)[Linkedin](https://www.linkedin.com/in/chanchanmao/)

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-009](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-009.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-010](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-010.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13-fig-011](../images/2338-https-www-lancedb-com-blog-newsletter-june-2026-6bbd5b13/figure-011.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb