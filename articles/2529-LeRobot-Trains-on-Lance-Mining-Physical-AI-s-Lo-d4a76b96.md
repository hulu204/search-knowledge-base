---
title: "🤖 LeRobot Trains on Lance, ⛏️ Mining Physical AI's Long Tail, 🔍 Vector Search at 10B Scale"
company: LanceDB
tag: 爬虫抓取
date: 2026-10-08
url: https://www.lancedb.com/blog/newsletter-september-2026
account: 
origin: en-rss
---
# 🤖 LeRobot Trains on Lance, ⛏️ Mining Physical AI's Long Tail, 🔍 Vector Search at 10B Scale

[ChanChan Mao](/author/chanchan-mao)

•

October 8, 2026

•

[Newsletter](/category/newsletter)

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-001](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## 🤖 How To Train Your Robot: The LanceDB Edition

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-002](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-002.jpg)

LeRobot now reads Lance datasets natively, so training pulls frames straight from object storage with a true global shuffle and no download. On all of DROID (27.6M frames, 369 GB), 10k SmolVLA steps on 8 H100s took 1h27m vs 2h00m for the standard reader on a local NVMe copy, with identical loss. GPUs waited on data 1.7% of the time vs 37.4%.

[Read more →](https://huggingface.co/blog/CarolinePascal/how-to-train-your-robot-the-lancedb-edition)

## ⛏️ Turning Fleet Data Into Better Models: The Data Mining Challenge in Physical AI

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-003](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-003.png)

Rare failures hide in the long tail of fleet logs, and the signal needed to find them is rarely a column yet. Lei Xu walks through mining on one LanceDB table: derive is\_left\_turn from yaw rate and speed, count pedestrians per clip with a Faster R-CNN detector, then run a clip-embedding vector search filtered by city, hour, turn, and pedestrian count.

[Read more →](https://www.lancedb.com/blog/data-mining-challenge-in-physical-ai)

## 🔍 From 10 Million to 10 Billion: Vector Search Built to Grow

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-004](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-004.png)

Five-bit RaBitQ hit 96.2% recall at 1,614 QPS on 10M 768d vectors, vs 91.5% for PQ384 at 1,047 QPS. At 10B vectors, distributed search held an 18.05 ms p50 and reached 1,066 QPS at 256 concurrent requests. A one-bit distance bound prunes over 99% of candidates before full scoring, and switching from fast to normal at query time lifts recall from 75.0% to 93.1% with no index rebuild.

[Read more →](https://www.lancedb.com/blog/10-billion-vector-search)

## 📚 Also Published

* [How Jev Compares to Other Rerankers: 19 reranker configurations benchmarked on five datasets](https://www.lancedb.com/blog/how-jev-compares-to-other-rerankers)

## 🎤 Talks & Recordings

**How Exa Indexes the Entire Web: Ray Data and Lance at Billion-Document Scale**

*Lei Xu (CTO @ LanceDB) · Hubert Yuan (Software Engineer @ Exa)*

At Ray Summit 2026, Lei Xu (LanceDB) and Hubert Yuan (Exa) walk through exa-d, Exa's framework on Lance and Ray Data for reprocessing embeddings, extracted text, and search signals across hundreds of billions of web pages, where dependency graphs drive execution, fragment-level patching avoids write amplification, and Ray Actors enable stateful model reuse.

[Watch the recording →](https://www.youtube.com/watch?v=fbbNmhWBS3Q&list=PLZNaJyYZRPdo&index=22)

## 📅 Upcoming Events

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-005](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-005.png)

**Open Intelligence Summit** — October 12-13, 2026 · San Francisco, CA

LanceDB is sponsoring the closing reception at Open Intelligence Summit, hosted by DigitalOcean and Nvidia. Check out LanceDB CTO Lei Xu's session: **Build an Open Multimodal Data Stack for Search, Curation, and Training.**

[Register →](https://www.digitalocean.com/open-intelligence-summit)

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-006](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-006.png)

**Long Horizon** — October 20-21, 2026 · San Francisco, CA

LanceDB is sponsoring Long Horizon by Encord! We help frontier labs, physical AI teams, and enterprises train on, search, and curate their data at massive scale, accelerating the data flywheel so teams can build better models faster. If that sounds like you, come find us on the Expo floor!

[Register →](https://encord.com/long-horizon/)

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-007](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-007.png)

**Reverie** — November 5, 2026 · San Francisco, CA

Reverie is a one-day technical summit for researchers and engineers building the data systems behind world models, generative video, physical AI, multimodal search, and agentic research.

[Apply to Attend →](https://www.reveriesummit.com/?utm_medium=email&utm_source=newsletter&utm_campaign=reverie-2026)

## 🏗️ LanceDB Enterprise Updates

### Performance

* **Larger shuffle-offset preload for distributed IVF builds** — Indexing workers now preload up to 512MiB of shuffle offsets by default; on a 1B-row IVF\_RQ shuffle replay, merge time fell from 61 to 13.4 min and peak memory (RSS) from 14.2GiB to 9.6GiB.
* **Faster Function worker cold start** — Workers fetch image layers with concurrent ranged reads, hard-link instances to one prepared image, and can share a node-level cache; a 10,000-row column refresh with a 3.0 GB torch + CUDA image fell from 409 s to 54 s (empty cache, ext4).
* **Lower per-batch overhead in Python UDFs** — The UDF executor skips nullability scans on nullable columns and reuses Arrow's cached null counts; a NumPy multiply over a nullable float64 column ran 1.61x faster per batch at 1,048,576 rows.
* **Fewer catalog calls in large-database table discovery** — Background discovery lists each namespace once per pass instead of once per 1,000-table page, and reads table locations from the manifest listing instead of describing every table, a pattern that drove ~1.1M describes in a 100K-table benchmark.

### Features

| Feature | Description |
| --- | --- |
| Secrets for Functions | Functions can bind named Secrets to environment variables, managed through create, rotate, describe, list, and drop endpoints; no endpoint returns a credential value, and rotation reaches existing columns without a new Function version. |
| Native vector deduplication in SQL | New `vector_dedup` and `vector_duplicate_pairs` table functions find near-duplicates over a vector index as a distributed SQL job, and can back a materialized view that keeps the retained original rows. |
| Grouped materialized views and table functions | Materialized views accept GROUP BY, including `ivf_partition(column)`, with IVF-grouped views refreshed across a worker fleet; a registered Function returning a list can sit in FROM position, emitting one row per element. |
| Pause and resume jobs | `PAUSE JOB` and `RESUME JOB` (plus REST endpoints) park a long index build or compaction to pick up later; on resume each worker retakes only its unfinished units, so at most one unit per worker is redone. |
| Primary-key SQL DML on WAL-backed tables | SQL `INSERT`, `DELETE ... WHERE pk = ...`, and `UPDATE ... SET col = literal WHERE pk = ...` now route through the write-ahead log, while shapes it can't apply, such as non-key WHERE clauses, return a typed error. |

## 🌟 Open Source Releases

| Project | Description |
| --- | --- |
| **Lance** v12.0.0 [Release notes](https://github.com/lance-format/lance/releases) | • **Breaking:** namespace `merge_insert` takes a list of key columns for composite-key upserts, a Rust API change ([#8915](https://github.com/lance-format/lance/pull/8915)); `json_extract` predicates no longer route to JSON indices and fall back to a full scan ([#9101](https://github.com/lance-format/lance/pull/9101)) • **IVF index improvements:** Shared partition scans across batch vector queries ([#7640](https://github.com/lance-format/lance/pull/7640)), proportional hierarchical k-means for training ([#9050](https://github.com/lance-format/lance/pull/9050)), automatic partition splitting/joining in single optimize pass ([#9051](https://github.com/lance-format/lance/pull/9051)), and metric-aware initial probe budgets ([#9195](https://github.com/lance-format/lance/pull/9195)) • **Full-text search performance:** Deferred phrase confirmation with score bounds ([#8749](https://github.com/lance-format/lance/pull/8749)), bulk intersection for wide AND queries ([#9030](https://github.com/lance-format/lance/pull/9030)), and bounded classic conjunction scoring ([#9033](https://github.com/lance-format/lance/pull/9033)) • **Row ID performance:** Fragment reuse indexes open 10–2200× faster ([#8887](https://github.com/lance-format/lance/pull/8887)); cached row ID index with ranked bitmap lookups ([#8930](https://github.com/lance-format/lance/pull/8930)) • **Python API additions:** `LanceDataset.slice()` method ([#8059](https://github.com/lance-format/lance/pull/8059)), `Bitmap` binding for RoaringBitmap ([#7837](https://github.com/lance-format/lance/pull/7837)), custom `ObjectStoreProvider` registration ([#8522](https://github.com/lance-format/lance/pull/8522)), and dataset deep clone ([#9181](https://github.com/lance-format/lance/pull/9181)) |
| **LanceDB** v0.39.0 [Release notes](https://github.com/lancedb/lancedb/releases) | • **Breaking:** materialized views can carry function-bound computed columns ([#4119](https://github.com/lancedb/lancedb/pull/4119)), and refreshing a computed column now recomputes rows whose inputs or definition changed instead of only filling nulls ([#4161](https://github.com/lancedb/lancedb/pull/4161)) • Remote connections run SQL synchronously or in the background with `execute_query`/`execute_query_async` ([#4070](https://github.com/lancedb/lancedb/pull/4070)) • **Breaking:** `get_job`/`job_history` are replaced by `open_job`, `describe_job`, and `query_job_events`, which expose per-fragment progress and failure info ([#4130](https://github.com/lancedb/lancedb/pull/4130)) • Function management APIs expanded: `drop_function`, `list_functions`, support for nested blob signatures and nullable named outputs ([#4097](https://github.com/lancedb/lancedb/pull/4097), [#4108](https://github.com/lancedb/lancedb/pull/4108), [#4109](https://github.com/lancedb/lancedb/pull/4109), [#4123](https://github.com/lancedb/lancedb/pull/4123)) |
| **lance-namespace** v0.12.0 – v0.13.0 [Release notes](https://github.com/lance-format/lance-namespace/releases) | • Merge insert operations now support multiple columns as the merge key ([#363](https://github.com/lance-format/lance-namespace/pull/363)) — breaking change to the spec • Added adaptive IVF probe query fields for dynamic tuning of vector index searches ([#367](https://github.com/lance-format/lance-namespace/pull/367)) |
| **lance-context** v0.6.6 – v0.6.7 [Release notes](https://github.com/lance-format/lance-context/releases) | • Bounded memory for WAL-backed rollout pagination ([#230](https://github.com/lance-format/lance-context/pull/230)), large-blob compaction ([#229](https://github.com/lance-format/lance-context/pull/229)), MemWAL merges via `ROLLOUT_MERGE_MAX_BYTES` ([#242](https://github.com/lance-format/lance-context/pull/242)), and Context point-reads with deferred payload loading ([#243](https://github.com/lance-format/lance-context/pull/243)) • New blob-size histogram metric and warning logs for oversized blobs to help diagnose storage patterns ([#240](https://github.com/lance-format/lance-context/pull/240)) • Fixed scheduler starvation where `MergeWal` could block `Compact` operations ([#239](https://github.com/lance-format/lance-context/pull/239)) |

## 🫶 Community Contributions

Thank you to contributors from Bytedance, Baidu, Adobe, Huawei, Tencent, DeepL, LumaLabs for improvements across storage, indexing, query execution, distributed processing, and ecosystem integrations in LanceDB, Lance, and the broader ecosystem.

**Notable contributions this month:**

* [@summaryzb](https://github.com/summaryzb) — Java scan APIs can now target specific vector index segments, so distributed vector search can split a query across workers by segment
* [@sezruby](https://github.com/sezruby) — Batched vector queries now read each probed IVF partition once and score every query against it, and added a Java batch vector search binding
* [@jiaoew1991](https://github.com/jiaoew1991) — Sped up row-ID and scan paths: streaming dataset version runs with a cursor, faster dense bitmap decoding, less system-column pipeline overhead, and single-producer Python reader batches
* [@dshepelev15](https://github.com/dshepelev15) — Kept the row-ID index cached with ranked bitmap lookups (get 422 to 126 ns on a 17.4B-row table), and cut object-store requests by batching page reads and reading large metadata in concurrent chunks
* [@zhangyue19921010](https://github.com/zhangyue19921010) — Added an experimental MinHash LSH scalar index for Jaccard text similarity across Rust, Python, and Java, plus matched-row offsets from `update_columns` and removal of an O(C²) commit validation step
* [@jonasdedden](https://github.com/jonasdedden) — Fixed Python API annotations (CompactionOptions, `create_index_uncommitted`, a misspelled option) and decoded deprecated substrait timestamp literals as microseconds
* [@wombatu-kun](https://github.com/wombatu-kun) — Widened the RaBitQ FastScan accumulator so distances above 1024 rotated dims no longer overflow, and kept commits working when an existing index can't be opened
* [@LuciferYang](https://github.com/LuciferYang) — About 30 hardening fixes across indexing and query paths, including rejecting malformed IVF/PQ/RaBitQ metadata instead of panicking, -0.0/0.0 float filter equality, Float16 literal coercion, and merge\_insert routing fixes
* [@ddupg](https://github.com/ddupg) — Restored Python index retraining, aligned Java inverted index options with Rust, and pruned scalar index segments outside the queried fragments

A heartfelt thank you to our community contributors of Lance and LanceDB this past month:

[@1fanwang](https://github.com/1fanwang) • [@a-erofeev](https://github.com/a-erofeev) • [@abhisheklearn12](https://github.com/abhisheklearn12) • [@adityabil](https://github.com/adityabil) • [@adityavaid](https://github.com/adityavaid) • [@ali2arslan](https://github.com/ali2arslan) • [@amunra](https://github.com/amunra) • [@bilalatique](https://github.com/bilalatique) • [@chakshu-dhannawat](https://github.com/chakshu-dhannawat) • [@chensammi](https://github.com/chensammi) • [@chenyu-x](https://github.com/chenyu-x) • [@crossthebridgetpa](https://github.com/crossthebridgetpa) • [@cyb3rb1ade](https://github.com/cyb3rb1ade) • [@dajiaohuang](https://github.com/dajiaohuang) • [@dcfocus](https://github.com/dcfocus) • [@ddupg](https://github.com/ddupg) • [@dentiny](https://github.com/dentiny) • [@desty](https://github.com/desty) • [@dshepelev15](https://github.com/dshepelev15) • [@easyrev](https://github.com/easyrev) • [@emecii](https://github.com/emecii) • [@everysympathy](https://github.com/everysympathy) • [@fanng1](https://github.com/fanng1) • [@farazshaikh](https://github.com/farazshaikh) • [@fede-kamel](https://github.com/fede-kamel) • [@fightboxing](https://github.com/fightboxing) • [@foobar](https://github.com/foobar) • [@gabriel39](https://github.com/gabriel39) • [@gallardot](https://github.com/gallardot) • [@hfutatzhanghb](https://github.com/hfutatzhanghb) • [@hiltonhe](https://github.com/hiltonhe) • [@importcpp](https://github.com/importcpp) • [@ivscheianu](https://github.com/ivscheianu) • [@jackylee-ch](https://github.com/jackylee-ch) • [@james-rms](https://github.com/james-rms) • [@jan-exa](https://github.com/jan-exa) • [@jayzhou2309](https://github.com/jayzhou2309) • [@jennifermell](https://github.com/jennifermell) • [@jiaoew1991](https://github.com/jiaoew1991) • [@jiaqizho](https://github.com/jiaqizho) • [@jimmy-xie-fleet](https://github.com/jimmy-xie-fleet) • [@joaquinhuigomez](https://github.com/joaquinhuigomez) • [@jonasdedden](https://github.com/jonasdedden) • [@jtbandes](https://github.com/jtbandes) • [@kaiqijinwow](https://github.com/kaiqijinwow) • [@kamronis](https://github.com/kamronis) • [@keunhong](https://github.com/keunhong) • [@leoreeyang](https://github.com/leoreeyang) • [@lichuang](https://github.com/lichuang) • [@lindseyz1205](https://github.com/lindseyz1205) • [@luciferyang](https://github.com/luciferyang) • [@majin1102](https://github.com/majin1102) • [@manucorporat](https://github.com/manucorporat) • [@maswin](https://github.com/maswin) • [@maxfreedompollard](https://github.com/maxfreedompollard) • [@mikewhb](https://github.com/mikewhb) • [@mohammadhijjawi97](https://github.com/mohammadhijjawi97) • [@ningsh7](https://github.com/ningsh7) • [@nitish-1303](https://github.com/nitish-1303) • [@notaarushi019](https://github.com/notaarushi019) • [@nyl3532016](https://github.com/nyl3532016) • [@pengw0048](https://github.com/pengw0048) • [@prrao87](https://github.com/prrao87) • [@qiuyuhang](https://github.com/qiuyuhang) • [@risto0211](https://github.com/risto0211) • [@rotty3000](https://github.com/rotty3000) • [@rudra-g-23](https://github.com/rudra-g-23) • [@rupertmaiti2005](https://github.com/rupertmaiti2005) • [@ruslan-shaydullin](https://github.com/ruslan-shaydullin) • [@sapnilb15](https://github.com/sapnilb15) • [@sbrunk](https://github.com/sbrunk) • [@sezruby](https://github.com/sezruby) • [@shoemoney](https://github.com/shoemoney) • [@siddarthareddy8](https://github.com/siddarthareddy8) • [@simpleqt](https://github.com/simpleqt) • [@slachiewicz](https://github.com/slachiewicz) • [@smarra](https://github.com/smarra) • [@sravan1011](https://github.com/sravan1011) • [@summaryzb](https://github.com/summaryzb) • [@sunyuechi](https://github.com/sunyuechi) • [@szetohoyan](https://github.com/szetohoyan) • [@taozhiyi13](https://github.com/taozhiyi13) • [@terapyon](https://github.com/terapyon) • [@ther1sing3un](https://github.com/ther1sing3un) • [@timsaucer](https://github.com/timsaucer) • [@tyagiquamar](https://github.com/tyagiquamar) • [@u70b3](https://github.com/u70b3) • [@venkata91](https://github.com/venkata91) • [@vgrigoriu](https://github.com/vgrigoriu) • [@winklemad](https://github.com/winklemad) • [@wombatu-kun](https://github.com/wombatu-kun) • [@xiaguanglei](https://github.com/xiaguanglei) • [@xloya](https://github.com/xloya) • [@xtangxtang](https://github.com/xtangxtang) • [@xuqianjin-stars](https://github.com/xuqianjin-stars) • [@yanghua](https://github.com/yanghua) • [@yangjunz](https://github.com/yangjunz) • [@yhz5613813](https://github.com/yhz5613813) • [@youssef-tharwat](https://github.com/youssef-tharwat) • [@zhangstar333](https://github.com/zhangstar333) • [@zhangyue19921010](https://github.com/zhangyue19921010) • [@ziwenzhang](https://github.com/ziwenzhang)

## 🤝 Lance Community Sync Recap

The Lance 12.0.0 SDK ships with the Lance 2.2 file format as the default, and this month's syncs covered the 11.0.0 and 12.0.0 releases alongside a governance change to PR-based voting. Design discussion centered on a production-ready redesign of stable row IDs, Transactions V2, a proposal to narrow Lance's core scope, and a separate proposal for a tiered manifest structure. The community also worked through the format proposal backlog and better ways for teams building on Lance to upstream their changes.

The next Lance Community Sync will take place on **Thursday, October 9 @ 9am PT**.

* [📬 Subscribe to the Lance mailing list to receive the meeting invite →](https://groups.google.com/a/lance.org/g/dev)
* [📄 Add discussion topics to the meeting notes →](https://docs.google.com/document/d/1cP058pJLVjj39DGaFV5yHI6qyWBwp1B2YKyIwXzYlAI/edit?usp=sharing)
* [📺 Watch previous recordings →](https://www.youtube.com/playlist?list=PLQysAafL04jUgOj7j6mCE5fcZEBB9Amu9)

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-008](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-008.avif)

[ChanChan Mao](/author/chanchan-mao)

Developer Relations @ LanceDB

[GitHub](https://github.com/ccmao1130)[Linkedin](https://www.linkedin.com/in/chanchanmao/)

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-009](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-009.png)

### How Jev Compares to Other Rerankers

Taylor Smith

Ayush Chaurasia

•

September 25, 2026

how-jev-compares-to-other-rerankers

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-010](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-010.avif)

### From 10 Million to 10 Billion: Vector Search Built to Grow

Yang Cen

•

September 17, 2026

10-billion-vector-search

![2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96-fig-011](../images/2529-LeRobot-Trains-on-Lance-Mining-Physical-AI-s-Lo-d4a76b96/figure-011.avif)

### A Practical LLM Pretraining Pipeline with LanceDB

Ayush Chaurasia

•

September 14, 2026

practical-llm-pretraining