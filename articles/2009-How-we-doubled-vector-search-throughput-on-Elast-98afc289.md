---
title: 'How we doubled vector search throughput on Elasticsearch Serverless'
company: Elastic
tag: 工程相关
date: 2026-05-28
url: https://www.elastic.co/search-labs/blog/vector-search-serverless-simdvec-throughput
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How we doubled vector search throughput on Elasticsearch Serverless

How we brought Elasticsearch's native SIMD scoring engine to serverless, and why serverless is where vector search innovation happens next.

May 28, 2026

[Chris Hegarty](/search-labs/author/chris-hegarty)[Lorenzo Dematte](/search-labs/author/lorenzo-dematte)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

We've brought simdvec, Elasticsearch's native single instruction, multiple data (SIMD) vector scoring engine, to serverless. Search throughput nearly doubled under concurrent load, and p99.9 tail latency dropped from 237 ms to 30 ms. By giving simdvec direct access to the blob cache's memory-mapped regions, serverless now runs the same zero-copy SIMD kernels as stateful, with identical recall and zero heap overhead. And because serverless gives us control over the entire storage layer, we believe it's where vector search will be fastest. Here's how we got there.

## Vector Search on Elasticsearch Serverless

[Elasticsearch Serverless](https://www.elastic.co/search-labs/blog/elasticsearch-serverless-stateless-architecture) is built on Stateless Elasticsearch, a fully decoupled compute and storage architecture where index data lives in remote object storage and search nodes maintain only a local cache. For vector search to be fast on this architecture, the scoring engine needs to work directly with the local cache, not copy it to the heap first.

Elasticsearch [simdvec](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine) is the engine behind every vector distance computation in Elasticsearch. It provides hand-tuned AVX-512 and NEON kernels, bulk scoring with explicit prefetching, and off-heap memory access that keeps data flowing from storage straight to CPU registers. On stateful Elasticsearch, simdvec has always had a direct fuel line: Memory-mapped files feed native pointers straight into SIMD intrinsics. On serverless, the data was sitting right there in the blob cache's memory-mapped regions, in exactly the right form, but there was no path connecting it to the scoring engine.

We've now built that path. simdvec runs on Serverless with the same off-heap, native SIMD scoring as stateful. And because serverless gives us control over the entire storage layer, this is just the beginning.

## Premium fuel only: why simdvec requires off-heap memory for vector scoring

simdvec's speed comes from working directly with off-heap memory. It takes a native pointer to memory-mapped data and passes it straight to C++ SIMD intrinsics. No intermediate copies, no heap allocations. The data flows from storage straight to CPU registers. This matters more than it sounds: simdvec's kernels process vectors faster than the data can be copied, so any copy in the path becomes the bottleneck, not the scoring itself.

On stateful Elasticsearch, this just works. Lucene memory-maps index files from local disk, and the scorer extracts a native pointer directly from the mapped region. This is the path that delivers the [benchmark numbers](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine#thousands-at-a-time) we've published, and it's what we wanted to bring to serverless. To see how, we first need to understand how serverless stores and accesses data.

## The serverless blob cache: how Elasticsearch stores vector data

In the stateless architecture, the primary copy of all index data lives in remote object storage, such as S3. Each search node maintains a local cache (called the *blob cache*) that keeps recently and frequently accessed portions of the index data on local SSD. The frozen tier on stateful Elasticsearch uses the same architecture: Searchable snapshots are backed by a similar blob cache that memory-maps regions from remote storage onto local disk. When a search hits cached data, it's served from fast local storage. When it misses, the blob cache fetches the data from the remote store and caches it for future queries.

The blob cache is organized into fixed-size memory-mapped regions, 16MB by default. It manages its own lifecycle: tracking which regions are in use, applying a [least-frequently-used eviction policy](https://www.elastic.co/search-labs/blog/searchable-snapshots-benchmark) when the cache is full, and reference counting to ensure regions aren't evicted while being read. The regions are still memory-mapped through the OS, but the blob cache controls which regions exist, which are populated, and when they're reclaimed. On stateful, those decisions are left entirely to the OS.

![Diagram showing data flow between Remote Object Storage and simdvec. The top box labeled “Remote Object Storage” lists S3, GCS, and Azure Blob, with an arrow marked “fetch on miss” pointing to a larger box labeled “Blob Cache.” Inside the Blob Cache are regions numbered 0–5 plus two empty slots, each 16 MB. Regions 0, 1, 3, 4 are green and labeled “cached,” Region 2 is blue and labeled “in use,” Region 5 is yellow and labeled “evicting,” and two gray boxes are labeled “empty.” A legend explains the color codes. A downward arrow labeled “direct memory” connects Blob Cache to a dark box labeled “simdvec – native SIMD scoring.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

Crucially, because each region is memory-mapped, the blob cache already holds vector data in exactly the form simdvec needs. But before [we built the connection](https://github.com/elastic/elasticsearch/pull/141718), there was no way to get at it. Every vector comparison was copied into a heap array and handed to a slower scorer. No direct memory pointers, no SIMD, and garbage collection pressure on every call.

## Unified scoring: one SIMD path for all storage tiers

We introduced a new abstraction that lets the scorer safely borrow direct memory from whatever storage layer is underneath, just long enough to run the SIMD computation. If the data is available as direct memory, simdvec's native kernels run. If not (data not yet cached or spanning a region boundary), the scorer falls back to a heap copy. In practice, the fallback is rare.

![Side‑by‑side comparison diagram labeled “Before” and “After.” The “Before” section shows four boxes: blue “Stateful – local mmap,” green “simdvec – native SIMD ✓,” yellow “Serverless – blob cache,” and red “Java scorer – no SIMD ✗.” Arrows indicate a green “direct ptr” from Stateful to simdvec and a red “heap copy” from Serverless to Java scorer, with the caption “two paths, two implementations.” The “After” section shows three boxes: blue “Stateful – local mmap,” yellow “Serverless – blob cache,” and green “simdvec – native SIMD ✓,” with two green arrows labeled “direct” pointing to simdvec and the caption “one engine, one code path, all tiers."](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltadef4930fe865721/6a469452a65a6b4e1dbeff0f/fd9583ffce724665018af46ce0409dc4e0825078-828x259.png)

This gave us a single scoring entry point across all tiers:

1. **Stateful** (local disk): The scorer extracts a native pointer from the OS memory map.
2. **Blob cache** (serverless, frozen tier): The scorer borrows a direct memory slice from a cache region.
3. **Fallback**: The scorer copies bytes to the heap. Rare in practice.

The scorer doesn't know which tier it's running on, and it doesn't need to. It also means we no longer maintain separate scoring implementations; previously, there was a fast native path for stateful and a slower path for everything else. Now every improvement to simdvec benefits all tiers automatically, including its most powerful capability: bulk scoring.

## Bulk vector scoring across blob cache regions

A single query may score thousands of candidate vectors. simdvec's [bulk scoring](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine#thousands-at-a-time) processes these in batches with multi-accumulator inner loops, query amortization, and cache-line prefetching, up to 4x faster than single-vector alternatives when data exceeds CPU cache.

Search over an Inverted file (IVF) index is where bulk scoring has the most impact. The query selects a set of candidate posting lists and sweeps through the quantized vectors, scoring them in large batches against the query vector. On stateful, those vectors live in one contiguous memory-mapped file, so bulk scoring resolves them with straightforward pointer arithmetic and scores a batch in a single native call.

On serverless, a sweep through a posting list may cross blob cache region boundaries. We extended the direct memory abstraction with a bulk access method that resolves multiple vector offsets to their respective cache regions in a single call. If all vectors in the batch are cached and none cross a region boundary, the scorer gets a direct memory slice and passes the whole batch to simdvec's native bulk kernel with the same prefetching and pipelining as stateful. When a vector does cross a boundary, the system falls back to per-vector scoring: still zero-copy, just without the batching benefit. With 16MB regions and 1024-byte vectors, that happens roughly once every 16,000 vectors.

simdvec's bulk scoring architecture, the key differentiator highlighted in the simdvec [benchmarks](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine), now operates on serverless with the same characteristics that make it fast on stateful. So how does it perform in practice?

## simdvec on Elasticsearch Serverless: vector search lap times

We benchmarked with an 18 million vector [MSMARCO](https://github.com/elastic/rally-tracks/tree/master/msmarco-v2-vector) dataset at 1024 dimensions, using IVF with Better Binary Quantization (BBQ) 1-bit quantization. All results are on a warm blob cache with the full dataset resident in local cache regions, so we're measuring the scoring path rather than remote fetch latency.

**Throughput.** Under concurrent load, search throughput nearly doubled, jumping from 398 to 739 ops/s. Single-client gains were 23-39%, but the real difference shows up under concurrency: The improvement was 2-3x larger because eliminating heap copies removes the GC pressure and allocation contention that previously throttled concurrent scoring.

![Bar chart titled “Search Throughput — Baseline vs Zero‑Copy (Median ops/s).” It compares median throughput between Baseline (heap‑copy) and Zero‑Copy (DirectAccessInput) across eight knn configurations. Each group shows a gray Baseline bar and a taller green Zero‑Copy bar with percentage improvements labeled above. The y‑axis shows median throughput in operations per second, ranging up to 900. The subhead notes that percentage labels indicate improvement.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt277d31993bac780c/6a4694559450737b7530d222/fc152731c4b99b85a448e8bd4e01915fefcb55a3-919x533.png)

**Tail latency.** The direct memory path transformed tail latency under load:

* *p99.9* dropped from 237 ms to 30 ms (87% reduction).
* *p99.99* dropped from 9.1 seconds to 55 ms (99.4% reduction).

*p100* dropped from 11.4 seconds to under 100 ms.

![Line graph titled “Tail Latency Collapse — knn‑10‑10 Multi‑Client.” The chart compares Baseline (heap‑copy) and Zero‑Copy (DirectAccessInput) latency across percentiles p50 to p100 on a logarithmic scale. The red Baseline line rises sharply, while the green Zero‑Copy line remains low. Labels mark key points. The caption notes Rally benchmark details and log scale.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6002a4d4bf8cbd8f/6a469458c71ec49c21b98453/003874d85261507d95274504a83bc016af0beb13-818x555.png)

The worst-case outliers that previously took seconds now complete in tens of milliseconds. The heap-copy-induced queueing that caused latency spikes is gone.

Recall is identical. The same vectors are scored, producing the same results. And we're just getting started.

## Beyond parity: what Elasticsearch Serverless can do for vector search that stateful can't

Reaching parity with stateful was the goal. But the more interesting realization is what the stateless architecture lets us do that stateful can’t.

On stateful, the OS controls memory-mapped file behavior: which pages stay resident, when to evict, how aggressively to read ahead. The application can offer hints, but they apply to entire file mappings, and the kernel may ignore them. Worse, search and indexing happen concurrently on the same node, so a hint that benefits one access pattern can hurt another. In practice, to balance different needs, you have to be conservative.

On serverless, two things are fundamentally different. The blob cache manages its own memory-mapped regions with full application-level control. And serverless [separates indexing and search onto dedicated tiers](https://github.com/elastic/elasticsearch/issues/147626): Search nodes never merge, indexing nodes never serve queries. No conflicting access patterns means we can be aggressive with memory advice. Here’s what we’re working on:

* **Per-region memory advice.** The blob cache knows what type of data each region holds. It can issue [random-access hints for rescoring regions](https://github.com/elastic/elasticsearch/issues/147625), where raw float32 vectors are read in unpredictable order and the kernel’s default readahead would waste memory on pages that will never be used. It can apply sequential readahead for scans through quantized vectors. On the indexing tier, merges read data sequentially, so aggressive readahead brings pages in before they're needed, with no risk of harming concurrent random reads that simply aren't happening on that node.
* **Cache-aware prefetching.** simdvec already prefetches at the CPU cache-line level. On serverless, we can coordinate this with the blob cache's knowledge of region residency, prefetching at multiple levels: remote store to cache, OS pages to RAM, and cache lines to CPU. The blob cache can [tell the scorer](https://github.com/elastic/elasticsearch/pull/147964) which regions are resident before scoring begins, avoiding work on data that would trigger a remote fetch.
* **Workload-aware eviction.** The blob cache can prioritize retaining data that vector search depends on: IVF centroid indexes that are checked on every query or quantized vectors that are scored in bulk, over data that's accessed infrequently. The OS page cache evicts based on generic heuristics with no understanding of what the data represents. On serverless, eviction policy can be tuned to the workload.

The blob cache gives us a level of control over the memory hierarchy that the OS page cache simply can’t. This is why we see serverless as the most promising platform for the next generation of vector search performance work. Not just matching stateful, but surpassing it. And vectors are just the beginning.

## Vector search on Elasticsearch Serverless: what we shipped and what's next

simdvec now runs everywhere Elasticsearch runs (stateful, serverless, and frozen tier) with the same native SIMD scoring, the same bulk scoring, and the same off-heap efficiency. The abstraction we built is general-purpose and already wired through every layer in the storage chain, so the same approach could benefit term lookups, aggregations, sorting, and stored field retrieval in the future.

Elasticsearch Serverless is where we're investing most heavily in vector search performance. Every improvement to simdvec, every optimization to the blob cache, and every new storage-level improvement lands here first. If you're choosing where to run your vector workloads, serverless is the platform that keeps getting faster. You can get started with a free [Elastic Cloud trial](https://cloud.elastic.co/registration).

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter