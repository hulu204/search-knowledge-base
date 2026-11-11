---
title: 'How Elasticsearch cut metrics storage by 41% by dropping sequence numbers after replication'
company: Elastic
tag: 工程相关
date: 2026-06-11
url: https://www.elastic.co/search-labs/blog/elasticsearch-time-series-storage-sequence-numbers
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How Elasticsearch cut metrics storage by 41% by dropping sequence numbers after replication

Find out how Elasticsearch trims sequence numbers at merge time to cut TSDS storage by 41%, what you give up, and why it's safe for metrics workloads.

June 11, 2026

[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)[Tanguy Leroux](/search-labs/author/tanguy-leroux)[Alan Woodward](/search-labs/author/alan-woodward)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Elasticsearch time series indices now store metrics at **3.74 bytes per sample** (down from 6.33 bytes, a 41% reduction). The savings come from trimming sequence numbers once replication no longer needs them. Combined with earlier synthetic \_id optimizations, per-sample storage has dropped by roughly two-thirds overall. The index.disable\_sequence\_numbers setting is on by default for newly created TSDS indices in serverless and generally available in 9.4.

## **How sequence numbers work in Elasticsearch**

Every write operation in Elasticsearch gets a sequence number `(_seq_no)` value. Sequence numbers are an integral part of:

* **Replication.** The primary assigns a sequence number to each operation, and replicas use it to stay in sync and to figure out what operations they need to replay after a network blip or a restart.
* **Optimistic concurrency control (OCC).** Clients can condition an update on `if_seq_no + if_primary_term`, so a write fails cleanly if the document changed in the meantime.

To coordinate [replication](https://www.elastic.co/docs/deploy-manage/distributed-architecture/reading-and-writing-documents), the primary shard tracks a global checkpoint: the highest sequence number that every in-sync replica is known to have. Operations above it may still be in flight, or already replicated but awaiting confirmation back to the primary.

For a deeper history of how sequence numbers came to be and what they replaced, see [Elasticsearch sequence IDs in 6.0](https://www.elastic.co/blog/elasticsearch-sequence-ids-6-0).

## **Why do sequence numbers use so much storage in Elasticsearch?**

Lucene writes documents in flush order, not sequence number order. In high-throughput indexing, that reordering breaks [delta-encoding](https://en.wikipedia.org/wiki/Delta_encoding) compression, so `_seq_no` compresses poorly compared to `@timestamp` and other structured columns. This doesn't apply to `@timestamp` as the latter is used for index sorting, and sequence numbers are never used for sorting.

In a time series index, where most other columns compress efficiently thanks to structure and repetition, `_seq_no` ends up being one of the largest contributors to the storage footprint.

## **When Elasticsearch sequence numbers are no longer needed**

`_seq_no` is only valuable during a narrow window after each write:

* It's needed for **replication and recovery** until the global checkpoint advances past it. Once the checkpoint moves past a sequence number, every in-sync replica already has it, and a recovering replica wouldn't ask for it either.
* It's needed for **OCC** only if a client later issues an `if_seq_no` update against that specific document.

For metrics workloads, that second condition almost never applies. Metrics are append-only: you ingest samples, query them, and purge them as they age out. Compare-and-swap updates against individual metric documents are rare.

Once replication is done, the `_seq_no` field continues occupying storage without providing further value for append-only time-series workloads.

## **How does Elasticsearch trim sequence numbers?**

Trimming sequence numbers required two changes.

**Firstly**, we changed the backing data structure for sequence numbers from a searchable BKD tree to a simple column-based doc values structure with a skipper index. Range queries against doc values fields with skippers still perform well, so we avoid the overhead of constructing the heavy BKD tree without harming recovery times. This also means that it is simple to partially delete the field at merge time: we simply don't write values for the documents that don't need them any more, whereas removing values from a BKD tree requires the tree to be completely reconstructed.

**Secondly**, we added an index setting, `index.disable_sequence_numbers`, aimed at time series indices. Sequence numbers are still assigned and written at index time (replication depends on them), but they are trimmed during [merges](https://www.elastic.co/docs/reference/elasticsearch/index-settings/merge) once the global checkpoint has advanced past the operations in the segments being merged. When Lucene merges segments whose maximum sequence number sits below the global checkpoint, the resulting merged segment no longer carries the `_seq_no` doc values column. This piggybacks on the normal merge lifecycle, so the trimming happens as a natural side effect of work Elasticsearch is already doing.

### CPU savings: fewer merge operations over time

Beyond the storage savings, dropping `_seq_no` removes future merge work: once a segment carries no sequence number column, subsequent merges don't have to merge doc values for it. For high-throughput metrics clusters, that's a CPU win on top of the storage savings. This fits a broader pattern of merge-time pruning Elasticsearch already does.

## **What do you lose when you disable sequence numbers?**

Dropping the `_seq_no` doc values column means a handful of operations that rely on it stop working. The [full list is in the documentation](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules), but the highlights are:

* **No optimistic concurrency control (OCC).** `if_seq_no` and `if_primary_term` are rejected on index and bulk requests.
* **Single-document update operations are not supported.** [Update API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-update) calls and [update](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk) actions in bulk requests are rejected.
* **Weaker consistency for update-by-query and delete-by-query.** These run without sequence-number-based conflict detection, so concurrent modifications can be silently overwritten instead of raising a version conflict.
* **\_seq\_no is not queryable.** You can't filter, sort, or aggregate on it.
* **random\_score needs an explicit field.** It can no longer fall back to `_seq_no` as a randomness source.
* Bulk API responses return sentinel values for `_seq_no` and `_primary_term`.

None of these are meaningful restrictions for metrics, which is why the setting is scoped to those workloads rather than turned on globally. For any index where OCC, update-by-query conflict detection, or querying on `_seq_no` actually matters, keep the setting disabled and nothing changes.

## **How much storage does sequence number trimming save?**

For representative time series indices, this change takes us from **6.33 bytes per sample down to 3.74 bytes per sample, a ~41% reduction in on-disk size**. The graph below tracks per-sample storage on a benchmark cluster as recent storage optimizations have rolled in:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltaa5c5250822fb415/6a477652c71ec40fc7b9937c/8968794cab56532e19072548801882c97c08adfb-2048x216.png)

The first step down, from roughly 10.8 to 6.3 bytes per sample, comes from [synthetic \_ids for time series indices](https://www.elastic.co/search-labs/blog/elasticsearch-synthetic-id-time-series-storage). . The second step, from 6.3 to 3.74, is the sequence number trimming this post is about. Together, these two changes cut per-sample storage by roughly two-thirds compared with where we started.

Because the savings scale with your retention window and your ingest rate, the absolute storage numbers get large quickly as the number of tracked time series scales. You can track more time series for longer, at a reduced storage cost and with no loss of functionality for metrics workloads.

This feature is generally available as of [9.4](https://www.elastic.co/blog/whats-new-elastic-9-4-0) and has been available in serverless environments. It is enabled by default for newly created [time series](https://www.elastic.co/docs/manage-data/data-store/data-streams/time-series-data-stream-tsds) indices. Existing indices aren't retroactively changed, but as your data ages out and fresh indices take over, the savings compound.

## **Frequently asked questions**

**Why do sequence numbers use so much storage in Elasticsearch time series indices?**

Lucene writes documents in flush order, not sequence number order. In high-throughput indexing, that reordering breaks delta-encoding compression, so \_seq\_no compresses poorly compared to @timestamp and other structured columns. In a metrics index where most columns are highly repetitive, \_seq\_no contributes disproportionately to total on-disk size.

**What is index.disable\_sequence\_numbers in Elasticsearch?**

It is an index setting that tells Elasticsearch to drop the \_seq\_no doc values column from merged segments once the global checkpoint has advanced past them. Sequence numbers are still assigned and used during replication. They are trimmed only after every in-sync replica has confirmed the operations, as a side effect of normal Lucene segment merges.

**How much storage does sequence number trimming save?**

In representative time series benchmarks, this setting reduces per-sample storage from 6.33 bytes to 3.74 bytes, a 41% reduction. Combined with synthetic \_id optimizations for TSDS, total per-sample storage drops by roughly two-thirds compared to a standard Elasticsearch index.

**What do I lose by disabling sequence numbers in Elasticsearch?**

Optimistic concurrency control (OCC) via if\_seq\_no / if\_primary\_term is disabled, single-document update operations are rejected, update-by-query and delete-by-query lose sequence-number-based conflict detection, and \_seq\_no is no longer queryable. For append-only metrics workloads these restrictions have no practical impact.

**Is it safe to disable sequence numbers for metrics workloads in Elasticsearch?**

Yes. Metrics pipelines are append-only (although updates and deletes are still allowed). No conditional writes, no querying on \_seq\_no. Replication correctness is unaffected because sequence numbers are only trimmed after the global checkpoint advances, meaning every replica already has the data before the column is dropped.

**When does Elasticsearch actually trim sequence numbers?**

Trimming happens during normal Lucene segment merges, not in a separate background job. A segment's sequence numbers are dropped in the merged result only if the segment's maximum sequence number is below the global checkpoint at merge time.

**How does this compare to other Elasticsearch time series storage optimizations?**

The two largest recent wins are synthetic \_ids (10.8 to 6.3 bytes per sample) and sequence number trimming (6.3 to 3.74 bytes). Together they cut per-sample storage by roughly two-thirds. Both are on by default for new TSDS indices in serverless and are generally available as of 9.4.

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