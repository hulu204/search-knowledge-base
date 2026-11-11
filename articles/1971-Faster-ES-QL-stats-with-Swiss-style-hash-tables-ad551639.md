---
title: 'Faster ES|QL stats with Swiss-style hash tables'
company: Elastic
tag: 工程相关
date: 2026-01-19
url: https://www.elastic.co/search-labs/blog/esql-swiss-hash-stats
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Faster ES|QL stats with Swiss-style hash tables

How Swiss-inspired hashing and SIMD-friendly design deliver consistent, measurable speedups in Elasticsearch Query Language (ES|QL).

January 19, 2026

[Chris Hegarty](/search-labs/author/chris-hegarty)[Matthew Alp](/search-labs/author/matthew-alp)[Nik Everett](/search-labs/author/nik-everett)

[ES|QL](/search-labs/blog/category/esql)

Jump to

Share

We recently replaced key parts of Elasticsearch’s hash table implementation with a Swiss-style design and observed up to 2–3x faster build and iteration times on uniform, high-cardinality workloads. The result is lower latency, better throughput, and more predictable performance for Elasticsearch Query Language (ES|QL) stats and analytics operations.

## Why this matters

Most typical analytical workflows eventually boil down to grouping data. Whether it’s computing average bytes per host, counting events per user, or aggregating metrics across dimensions, the core operation is the same — map keys to groups and update running aggregates.

At a small scale, almost any reasonable hash table works fine. At the large scale (hundreds of millions of documents and millions of distinct groups) details start to matter. Load factors, probing strategy, memory layout, and cache behavior can make the difference between linear performance and a wall of cache misses.

Elasticsearch has supported these workloads for years, but we’re always looking for opportunities to modernize core algorithms. As such, we evaluated a newer approach inspired by Swiss tables and applied it to how ES|QL computes statistics.

## What are Swiss tables, really?

Swiss tables are a family of modern hash tables popularized by Google’s SwissTable and later adopted in Abseil and other libraries.

Traditional hash tables spend a lot of time chasing pointers or loading keys just to discover that they don’t match. Swiss tables’ defining feature is the ability to reject most probes using a tiny cache-resident array structure, stored separately from the keys and values, called *control bytes*, to dramatically reduce memory traffic.

Each control byte represents a single slot and, in our case, encodes two things: whether the slot is empty, and a short fingerprint derived from the hash. These control bytes are laid out contiguously in memory, typically in groups of 16, making them ideal for [single instruction, multiple data](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) (SIMD) processing.

Instead of probing one slot at a time, Swiss tables scan an entire control-byte block using vector instructions. In a single operation, the CPU compares the fingerprint of the incoming key against 16 slots and filters out empty entries. Only the few candidates that survive this fast path require loading and comparing the actual keys.

This design trades a small amount of extra metadata for much better cache locality and far fewer random loads. As the table grows and probe chains lengthen, those properties become increasingly valuable.

## SIMD at the center

The real star of the show is SIMD.

Control bytes are not just compact, they’re also explicitly designed to be processed with vector instructions. A single SIMD compare can check 16 fingerprints at once, turning what would normally be a loop into a handful of wide operations. For example:

![SIMD at the center in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1f710e87dd749ab3/6a170cc46234e052dadb1a49/bd418778f0c6144f8f5f18419f6220ac0c935c7a-903x407.png)

In practice, this means:

* Fewer branches.
* Shorter probe chains.
* Fewer loads from key and value memory.
* Much better utilization of the CPU’s execution units.

Most lookups never make it past the control-byte scan. When they do, the remaining work is focused and predictable. This is exactly the kind of workload that modern CPUs are good at.

## SIMD under the hood

For readers who like to peek under the hood, here’s what happens when inserting a new key into the table. We use the Panama Vector API with 128-bit vectors, thus operating on 16 control bytes in parallel.

The following snippet shows the code generated on an Intel Rocket Lake with AVX-512. While the instructions reflect that environment, the design does not depend on AVX-512. The same high-level vector operations are emitted on other platforms using equivalent instructions (for example, AVX2, SSE, or NEON).

```
; Load 16 control bytes from the control block
vmovdqu xmm0, XMMWORD PTR [r9+r10*1+0x10]

; Broadcast the 7-bit fingerprint of the new key across the vector
vpbroadcastb xmm1, r11d

; Compare all 16 control bytes to the new fingerprint
vpcmpeqb k7, xmm0, xmm1
kmovq rbx, k7

; Check if any matches were found
test rbx, rbx
jne <handle_match>
```

Each instruction has a clear role in the insertion process:

* `vmovdqu`: Loads 16 consecutive control bytes into the 128-bit `xmm0` register.
* `vpbroadcastb`: Replicates the 7-bit fingerprint of the new key across all lanes of the `xmm1` register.
* `vpcmpeqb`: Compares each control byte against the broadcasted fingerprint, producing a mask of potential matches.
* `kmovq` + `test`: Moves the mask to a general-purposes register and quickly checks whether a match exists.

Finally, we settled on probing groups of 16 control bytes at a time, as benchmarking showed that expanding to 32 or 64 bytes with wider registers provided no measurable performance benefit.

## Integration in ES|QL

Adopting Swiss-style hashing in Elasticsearch was not just a drop-in replacement. ES|QL has strong requirements around memory accounting, safety, and integration with the rest of the compute engine.

We integrated the new hash table tightly with Elasticsearch’s memory management, including the page recycler and circuit breaker accounting, ensuring that allocations remain visible and bounded. Elasticsearch's aggregations are stored densely and indexed by a group ID, keeping the memory layout compact and fast for iteration, as well as enabling certain performance optimizations by allowing random access.

For variable-length byte keys, we cache the full hash alongside the group ID. This avoids recomputing expensive hash codes during probing and improves cache locality by keeping related metadata close together. During rehashing, we can rely on the cached hash and control bytes without inspecting the values themselves, keeping resizing costs low.

One important simplification in our implementation is that entries are never deleted. This removes the need for *tombstones* (markers to identify previously occupied slots) and allows empty slots to remain truly empty, which further improves probe behavior and keeps control-byte scans efficient.

The result is a design that fits naturally into Elasticsearch’s execution model while preserving the performance characteristics that make Swiss tables attractive.

## How does it perform?

At small cardinalities, Swiss tables perform roughly on par with the existing implementation. This is expected: When tables are small, cache effects dominate less and there is little probing to optimize.

As cardinality increases, the picture changes quickly.

![ES|QL stats with Swiss-style hash tables](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt09b13af2fe162f59/6a170cc66f7f04485c9148b8/24900afc47ab07b0e9933f6117b99d0f4613f794-962x599.png)

The heatmap above plots time improvement factors for different key sizes (8, 32, 64, and 128 bytes) across cardinalities from 1,000 up to 10,000,000 groups. As cardinality grows, the improvement factor steadily increases, reaching up to 2–3x for uniform distributions.

This trend is exactly what the design predicts. Higher cardinality leads to longer probe chains in traditional hash tables, while Swiss-style probing continues to resolve most lookups inside SIMD-friendly control-byte blocks.

## Cache behavior tells the story

To better understand the speedups, we ran the same JMH [`benchmarks`](https://github.com/elastic/elasticsearch/pull/139343/files#diff-d0e0cc91a7495bf36b2d44eacce95f5185d01879e5f6c38089ac7a89aad17da7) under Linux `perf` and captured cache and TLB statistics.

Compared to the original implementation, the Swiss version performs about 60% fewer cache references overall. Last-level cache loads drop by more than 4x, and LLC load misses fall by over 6x. Since LLC misses often translate directly into main-memory accesses, this reduction alone explains a large portion of the end-to-end improvement.

Closer to the CPU, we see fewer L1 data cache misses and nearly 6x fewer data TLB misses, pointing to tighter spatial locality and more predictable memory access patterns.

![Cache behavior: Original vs. ES|QL stats with Swiss-style hash tables](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb987a5bd98c0d7eb/6a170cc8a929cf9655ae0a25/6e49b7609fba83e33692cb9834552b6ca7e42a83-998x499.png)

This is the practical payoff of SIMD-friendly control bytes. Instead of repeatedly loading keys and values from scattered memory locations, most probes are resolved by scanning a compact, cache-resident structure. Less memory touched means fewer misses, and fewer misses mean faster queries.

## Wrapping up

By adopting a Swiss-style hash table design and leaning hard into SIMD-friendly probing, we achieved 2–3x speedups for high-cardinality ES|QL stats workloads, along with more stable and predictable performance.

This work highlights how modern CPU-aware data structures can unlock substantial gains, even for well-trodded problems, like hash tables. There is more room to explore here, like additional primitive type specializations and use in other high-cardinality paths, like joins, all of which are just part of the broader and ongoing effort to continually modernize Elasticsearch internals.

If you’re interested in the details or want to follow the work, check out this [pull request](https://github.com/elastic/elasticsearch/pull/139343) and [meta issue](https://github.com/elastic/elasticsearch/issues/138799) tracking progress on Github.

Happy hashing!

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf69e1ba73bd5d402/6a6a340599442cd9e0df1d94/1794a179d9536e693a0982634da59aff209c9d68-1280x720.png)

[Analytics](/search-labs/blog/category/analytics)[ES|QL](/search-labs/blog/category/esql)[Python](/search-labs/blog/category/python-programming)

### How to instrument your search API with OpenTelemetry and query it with ES|QL

July 22, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter