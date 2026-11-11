---
title: 'https://www.lancedb.com/blog/newsletter-january-2026'
company: LanceDB
tag: 召回
date: 
url: https://www.lancedb.com/blog/newsletter-january-2026
account: 
origin: en-rss
---
# 🦆 Lance x DuckDB SQL Retrieval, 🚗 Uber-Scale Storage, ⚡ 1.5M IOPS

[ChanChan Mao](/author/chanchan-mao)

•

February 9, 2026

•

[Newsletter](/category/newsletter)

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-001](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## 🦆 Lance x DuckDB: SQL for Retrieval on the Multimodal Lakehouse Format

[![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-002](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-002.png)](#)

The Lance extension for DuckDB turns DuckDB into a SQL compute engine over Lance datasets, exposing vector, full-text, and hybrid retrieval as SQL table functions. This enables fully composable retrieval workflows — joins with eval data, reproducible top-k slicing, SQL-based debugging, and materialization back into Lance.

This extension bridges traditional SQL analytics with multimodal retrieval on a single open dataset format.

[Read more →](https://lancedb.com/blog/lance-x-duckdb-sql-retrieval-on-the-multimodal-lakehouse-format/)

## 🚗 Rethinking Table File Paths with Uber: Lance's Multi-Base Layout

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-003](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-003.webp)

Working with Uber's AI Infrastructure team, Lance introduced a multi-base layout to support product systems that need a single dataset to span multiple S3 buckets for parallel reads and writes.

By separating storage bases from file references, Lance enables multi-bucket and multi-region layouts with compact, relocatable metadata — allowing Uber to scale training and retrieval workloads without fragmenting datasets or rewriting metadata.

[Read more →](https://lancedb.com/blog/rethinking-table-file-paths-lance-multi-base-layout/)

## 📍 The Quest for One Million IOPS: Benchmarking Storage at Lance

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-004](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-004.webp)

Recent storage benchmarks in Lance reached up to 1.5 million IOPS by combining a scheduler rework with `io_uring`, showing that high random-access throughput depends more on reducing CPU overhead and context switching than on single-read latency.

This blog explains how this design better drives modern NVMe hardware for vector, text, and key-based lookups, and contrasts embedded and disaggregated architectures to show how LanceDB scales from single-process deployments to large, distributed systems.

[Read more →](https://lancedb.com/blog/one-million-iops/)

## 📖 Also Published This Month

* [**One System, Many Workloads: Rethinking What "Multimodal" Means for AI**](https://lancedb.com/blog/what-we-mean-by-multimodal/)
* [**Apache Polaris and Lance: Bringing AI-Native Storage to the Open Multimodal Lakehouse**](https://polaris.apache.org/blog/2026/01/06/apache-polaris-and-lance-bringing-ai-native-storage-to-the-open-multimodal-lakehouse/)
* [**Keep Your Data Fresh with CocoIndex and LanceDB**](https://lancedb.com/blog/keep-your-data-fresh-with-cocoindex-and-lancedb/)‍

## 📅 Upcoming Events

[**February Open Data + AI Meetup - Peninsula, Bay Area Edition**](https://luma.com/ft5b28bl) — Thursday, February 12

Hear from speakers from LanceDB, Fivetran, Dremio, and typedef about what they're building and how they're defining the future of open data and AI.

[Register →](https://luma.com/ft5b28bl)

[**NYC Lakehouse Meetup**](https://luma.com/gmc5k8gr) — Tuesday, February 17

​We're bringing together Apache Iceberg, Lance, and Apache DataFusion communities in NYC to chat about all things open lakehouse and data infrastructure at Cloudflare's NYC office!

[Register →](https://luma.com/gmc5k8gr)

## 🏗️ LanceDB Enterprise Updates

| Feature | Description |
| --- | --- |
| Add page cache prewarm API | * Users can prewarm LanceDB tables using a LanceDB administrative API. (It is also possible to prewarm some columns, but not others.) * This is useful for cases where we want to ensure that data is in the page cache prior to running a specific workload. It is also useful for benchmarking. |
| Admission Control for Feature Engineering Jobs | Avoid deadlocks by rejecting jobs if the cluster does not have enough resources to execute the job. |
| Adaptive Batch sizing for Feature Engineering Job checkpoints | Backfill jobs now change checkpoint size depending on udf execution time. Internal benchmarks show up to 2x performance improvements. |

## 🌟 Open Source Releases

| Project | Description |
| --- | --- |
| Lance v1.0.1 - v1.0.4   [Release notes](https://github.com/lance-format/lance/releases) | * Multi-base storage layouts enabling a single dataset to span multiple buckets or regions for parallel reads and writes ([#5790](https://github.com/lance-format/lance/pull/5790), [#5801](https://github.com/lance-format/lance/pull/5801)) * Faster query execution via tighter WAND block score bounds and reduced per-query overhead ([#5668](https://github.com/lance-format/lance/pull/5668), [#5696](https://github.com/lance-format/lance/pull/5696)) |
| LanceDB v0.26 - v0.28   [Release notes](https://github.com/lancedb/lancedb/releases) | * DuckDB-powered SQL retrieval with vector, FTS, and hybrid search exposed as composable table functions ([#2946](https://github.com/lancedb/lancedb/pull/2946), [#2957](https://github.com/lancedb/lancedb/pull/2957)) * Expanded embedding support (VoyageAI v4, multimodal) and improved ingestion robustness via parallel embedding computation and better remote query cancellation ([#2959](https://github.com/lancedb/lancedb/pull/2959), [#2887](https://github.com/lancedb/lancedb/pull/2887), [#2896](https://github.com/lancedb/lancedb/pull/2896), [#2913](https://github.com/lancedb/lancedb/pull/2913)) |
| lance-graph v0.4.0 - v0.5.0   [Release notes](https://github.com/lance-format/lance-graph/releases) | * Significantly expanded Cypher expressiveness with `WITH` clause chaining, `COLLECT`, and `COUNT(DISTINCT …)` support ([#86](https://github.com/lance-format/lance-graph/pull/86), [#85](https://github.com/lance-format/lance-graph/pull/85), [#116](https://github.com/lance-format/lance-graph/pull/116)) * Integrated vector search and similarity UDFs into graph queries, with improved execution efficiency on object stores ([#80](https://github.com/lance-format/lance-graph/pull/80), [#81](https://github.com/lance-format/lance-graph/pull/81), [#83](https://github.com/lance-format/lance-graph/pull/83), [#89](https://github.com/lance-format/lance-graph/pull/89), [#96](https://github.com/lance-format/lance-graph/pull/96)) |
| lance-context v0.2.0 - v0.2.1   [Release notes](https://github.com/lance-format/lance-context/releases) | * Core context store APIs for append, search, and versioned checkout across Python and Rust ([#6](https://github.com/lance-format/lance-context/pull/6), [#11](https://github.com/lance-format/lance-context/pull/11), [#12](https://github.com/lance-format/lance-context/pull/12), [#24](https://github.com/lance-format/lance-context/pull/24)) * Improved runtime behavior with multimodal context support, background compaction, and reduced Python-side blocking during remote I/O ([#9](https://github.com/lance-format/lance-context/pull/9), [#28](https://github.com/lance-format/lance-context/pull/28), [#29](https://github.com/lance-format/lance-context/pull/29)) |
| lance-duckdb v0.4.1 - v0.5.0   [Release notes](https://github.com/lance-format/lance-duckdb/releases) | * Improved DuckDB integration with global aggregate pushdown and expanded vector search ergonomics, including ARRAY-based query vectors and tuning controls ([#124](https://github.com/lance-format/lance-duckdb/pull/124), [#119](https://github.com/lance-format/lance-duckdb/pull/119), [#120](https://github.com/lance-format/lance-duckdb/pull/120)) |
| lance-namespace v0.4.4 - v0.4.5   [Release notes](https://github.com/lance-format/lance-namespace/releases) | * New Lance partitioning specification for defining and operating on partitioned datasets ([#279](https://github.com/lance-format/lance-namespace/pull/279), [#297](https://github.com/lance-format/lance-namespace/pull/297)) |
| lance-ray v0.1.0 - v0.2.0   [Release notes](https://github.com/lance-format/lance-ray/releases) | * Distributed Ray-based IVF\_SQ / PQ / FLAT index builder for scalable, parallel index creation ([#67](https://github.com/lance-format/lance-ray/pull/67)) |
| lance-spark v0.2.0   [Release notes](https://github.com/lance-format/lance-spark/releases) | * Spark `MERGE INTO` support for upserts and deletes, plus vector search and distributed index creation for large-scale Spark pipelines ([#172](https://github.com/lance-format/lance-spark/pull/172), [#189](https://github.com/lance-format/lance-spark/pull/189), [#171](https://github.com/lance-format/lance-spark/pull/171)) |

## 🫶 Community Contributions

Thank you to contributors from Uber, Netflix, Hugging Face, Bytedance, Huawei, Tencent, and Alibaba for improvements across embeddings, query robustness, storage compatibility, distributed indexing, Spark integration, and core format reliability in LanceDB, Lance, `lance-spark`, and `lance-ray`.

**Notable contributions this month:**

- [@fzowl](https://github.com/fzowl) — Added support for VoyageAI v4 and multimodal models, expanding first-class embedding options in LanceDB.  
- [@dcfocus](https://github.com/dcfocus) — Delivered major Cypher features in lance-graph, including `COLLECT` aggregation, `WITH` clause query chaining, and foundational context APIs.  
- [@ChunxuTang](https://github.com/ChunxuTang) — Expanded Cypher query capabilities with `COUNT(DISTINCT …)`, case-insensitive matching, and vector search operators.  
- [@beinan](https://github.com/beinan) — Improved execution efficiency and deployability across lance-graph and lance-context, enabling more scalable production deployments.  
- [@jja725](https://github.com/jja725) — Implemented background compaction for Lance fragments, improving long-running system performance.  
- [@ex172000](https://github.com/ex172000) — Improved performance and correctness through executor fixes and parallelized embedding computation.  
- [@fatelei](https://github.com/fatelei) — Prevented Python-side blocking by releasing the GIL during remote storage operations.  
- [@wojiaodoubao](https://github.com/wojiaodoubao) — Introduced the Lance partitioning specification, enabling native support for partitioned datasets.  
- [@chenghao-guo](https://github.com/chenghao-guo) — Implemented a Ray-based distributed IVF index builder, enabling scalable index construction.  
- [@nyl3532016](https://github.com/nyl3532016) — Added vector search support to `lance-spark`, enabling similarity search in Spark pipelines.  
- [@jiaoew1991](https://github.com/jiaoew1991) — Built a fragment-aware join optimizer to improve Spark query performance on Lance datasets.  
- [@jtuglu1](https://github.com/jtuglu1) — Implemented distributed full-text search index creation in `lance-spark`.  
- [@bryanck](https://github.com/bryanck) — Improved stability of `lance-spark` by fixing Kryo serialization and classloader issues.  
- [@zhangyue19921010](https://github.com/zhangyue19921010) — Implemented Spark `MERGE INTO` support for upsert and delete operations on Lance tables.

We want to especially highlight the initial release of [**lance-context**](https://github.com/lance-format/lance-context) contributed by Uber.

A heartfelt thank you to our community contributors of Lance and LanceDB this past month:

[@fzowl](https://github.com/fzowl) • [@dcfocus](https://github.com/dcfocus) • [@ChunxuTang](https://github.com/ChunxuTang) • [@beinan](https://github.com/beinan) • [@jja725](https://github.com/jja725) • [@ex172000](https://github.com/ex172000) • [@hushengquan](https://github.com/hushengquan) • [@fatelei](https://github.com/fatelei) • [@ddupg](https://github.com/ddupg) • [@Mesut-Doner](https://github.com/Mesut-Doner) • [@amanharshx](https://github.com/amanharshx) • [@Angryrou](https://github.com/Angryrou) • [@youssef-tharwat](https://github.com/youssef-tharwat) • [@leiyuou](https://github.com/leiyuou) • [@prrao87](https://github.com/prrao87) • [@fenfeng9](https://github.com/fenfeng9) • [@chyyran](https://github.com/chyyran) • [@camilesing](https://github.com/camilesing) • [@zhangyue19921010](https://github.com/zhangyue19921010) • [@touch-of-grey](https://github.com/touch-of-grey) • [@fredlarochelle](https://github.com/fredlarochelle) • [@LuciferYang](https://github.com/LuciferYang) • [@lhoestq](https://github.com/lhoestq) • [@majin1102](https://github.com/majin1102) • [@yanghua](https://github.com/yanghua) • [@wojiaodoubao](https://github.com/wojiaodoubao) • [@lichuang](https://github.com/lichuang) • [@Ke-Wang](https://github.com/Ke-Wang) • [@niebayes](https://github.com/niebayes) • [@HaochengLIU](https://github.com/HaochengLIU) • [@markmcd](https://github.com/markmcd) • [@chenghao-guo](https://github.com/chenghao-guo) • [@nyl3532016](https://github.com/nyl3532016) • [@jiaoew1991](https://github.com/jiaoew1991) • [@jtuglu1](https://github.com/jtuglu1) • [@bryanck](https://github.com/bryanck) • [@fangbo](https://github.com/fangbo) • [@majian1998](https://github.com/majian1998) • [@hamersaw](https://github.com/hamersaw)‍

## 🤝 Lance Community Sync Recap

In January, we held two Lance Community Syncs focused on the upcoming **Lance 2.0.0** release (now at **RC4** and approaching final community vote), growing ecosystem integrations with [DuckDB](https://lance.org/integrations/duckdb/), [Polaris](https://lance.org/format/namespace/supported-catalogs/polaris/), and [Hugging Face](https://huggingface.co/lance-format), and the formalization of [**lance-context**](https://github.com/lance-format/lance-context) and [**lance-graph**](https://github.com/lance-format/lance-graph) as official sub-projects.

We also discussed recent performance work across Spark, vector indexing, and WAL/mem-table updates, alongside forward-looking proposals covering schema semantics, metadata visibility, clustering strategies, and a new **Incubator** governance stage for emerging projects.

The next Lance Community Sync will take place on **Thursday, February 12, 2026.**

* 📬 [**Subscribe to Lance mailing list to receive the meeting invite →**](https://groups.google.com/a/lance.org/g/dev)
* 📄 [**Add discussion topics to the meeting notes →**](https://docs.google.com/document/d/1cP058pJLVjj39DGaFV5yHI6qyWBwp1B2YKyIwXzYlAI/edit?usp=sharing)
* ▶️ Watch previous recordings: [**Jan 15**](https://youtu.be/XJPkXCwLajc) | [**Jan 29**](https://youtu.be/JQbAQHIrfSo)

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-005](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-005.avif)

[ChanChan Mao](/author/chanchan-mao)

Developer Relations @ LanceDB

[GitHub](https://github.com/ccmao1130)[Linkedin](https://www.linkedin.com/in/chanchanmao/)

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-006](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-006.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-007](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-007.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0-fig-008](../images/2340-https-www-lancedb-com-blog-newsletter-january-20-f3548bc0/figure-008.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb