---
title: 'Elasticsearch simdvec deep-dive: Walking the memory tightrope to 2x better vector throughput'
company: Elastic
tag: 工程相关
date: 2026-06-08
url: https://www.elastic.co/search-labs/blog/elasticsearch-simdvec-vector-throughput
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch simdvec deep-dive: Walking the memory tightrope to 2x better vector throughput

A deep dive into four optimizations (cascade unrolling, batch prefetching, dim-axis unrolling, a structural refactor) that pushed Elasticsearch simdvec to 2x vector throughput by working with the CPU, not against it.

June 08, 2026

[Lorenzo Dematte](/search-labs/author/lorenzo-dematte)[Florian Bernd](/search-labs/author/florian-bernd)[Chris Hegarty](/search-labs/author/chris-hegarty)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Elasticsearch [simdvec](https://github.com/elastic/elasticsearch/blob/main/libs/simdvec/README.md) delivers up to 50x faster vector distance computation than serial code. Getting there required solving four successive hardware bottlenecks, each fix revealing the next. This post walks through cascade unrolling, batch prefetching, dim-axis unrolling and a structural refactor that turned out to be the biggest win of all, together producing up to 2x throughput improvement. It's a companion to [How we built Elasticsearch simdvec to make vector search one of the fastest in the world](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine).

Every vector search query in Elasticsearch, whether [Hierarchical Navigable Small World (HNSW)](https://arxiv.org/abs/1603.09320) traversal, inverted file (IVF) scan, or reranking pass, reduces to the same problem: computing distances between vectors, millions of times per query.

Elasticsearch [simdvec](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine) is the engine behind every vector distance computation in Elasticsearch. Computing distances between vectors is an easy operation in terms of instructions to perform; for example, a [*dot product*](https://en.wikipedia.org/wiki/Dot_product) is simply a combination of additions and multiplications. But making those fast, really fast, requires diving deep into how modern CPUs work, what different [Instruction Set Architectures (ISAs)](https://en.wikipedia.org/wiki/Instruction_set_architecture) offer, and their similarities and peculiarities.

In this post, we dive deep into how simdvec optimizes for memory access. Hand-tuned [Single Instruction, Multiple Data (SIMD)](https://en.wikipedia.org/wiki/Single_instruction,_multiple_data) kernels for x86 and ARM perform vector distance computations in just a few CPU cycles; it’s not unusual for a SIMD kernel to be limited not by the number of operations it can perform but by the amount of data it can fetch and consume for every CPU cycle.

For example, a 1024-dimensional float32 embedding requires 1024 multiply-add operations for a single dot product. An AVX-512 processor packs 16 floats into each 512-bit register and can issue two fused multiply-add operations every cycle. At a sustained rate, that’s a throughput of one dot product in just 32 cycles, 8 nanoseconds per vector on a 4GHz CPU. Searching 1 million candidate vectors means executing that kernel 1 million times, streaming roughly 4 GB of vector data through the CPU. The silicon can crunch the math in 8 milliseconds, total; the problem is actually delivering those 4 GB in time! It’s an impossible quest, but how close can we get?

The rest of this post is about how we pushed as many vectors as we could through the silicon. It was a tightrope walk: Every step that got us closer to peak throughput tightened the constraints on the next step. The four optimizations, in the order we applied them:

1. **Cascade unrolling** - maximize FMA port utilization with independent accumulator chains
2. **Batch processing and prefetching** - hide memory latency by prefetching data ahead of time
3. **Dim-axis unrolling** - sidestep L1d cache aliasing on power-of-2 dimensions
4. **Query load hoisting** - eliminate redundant per-document query operations

## Ports, pipes, latency, throughput…oh my! How modern CPUs execute SIMD vector operations

Modern CPUs can issue multiple operations per cycle because they have several execution units implemented in their silicon; operations are dispatched via interfaces called [**ports**](https://uops.info/background.html) [on x86](https://uops.info/background.html) (execution pipelines, or **pipes** for short, [on ARM](https://developer.arm.com/documentation/102099/0003/Technical-overview/Core-components)). Ports handle different kinds of work in parallel: some memory loads and stores, some integer arithmetic, some floating-point math.

![Diagram showing SIMD registers connected to ports labeled FMA, load, and shuffle, with cache below.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd7774a107c7f7b2b/6a478abebfe8a26d6a4da28c/49d97a151fc633c025299acf329ce91dc240e25b-1999x935.png)

Two important properties of any operation a port can handle are latency and throughput. *Latency* is how many CPU cycles a single operation takes to produce its result; *throughput* is how many such operations can be started per cycle. Throughput is closely related to the number of ports available for a given operation: If a CPU has two ports that can execute FMAs, it can issue up to two independent new FMAs every cycle, for a peak throughput of two per cycle under ideal conditions.

Let’s take AVX-512 as an example. Most FMA instructions on modern Intel CPUs have a [typical latency of ~four cycles](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html#text=_mm512_fmadd_ps&ig_expand=3111) and can execute on either of two FMA-capable ports. Starting from cold, the first result lands four cycles later, but once the pipeline is full, two new FMAs can start every cycle, as long as they don't depend on each other.

Our first steps aim at maximizing the number of ports used, balancing port usage and taking latency into account.

## Cascade unrolling: maximizing FMA port utilization

Following the previous example, if an FMA instruction has a latency of four and a throughput of two, the CPU can keep ~eight FMAs *in flight* (issued, but not yet completed) at any moment. Of course, this can happen only if there are eight independent operations available.

If we chain them, each FMA waits for the previous one's result, and the CPU runs at latency (one FMA every four cycles) instead of throughput (two per cycle), up to 8x slower than the hardware can deliver.

It's easy to end up with a chain by accident; for example, a naive vector dot product implementation would look like `foreach (i) { acc = acc + x[i]*y[i] }`. With a single accumulator, each iteration depends on the previous one's result. A natural reaction is to think about unrolling the loop: If we need to keep N instructions in flight, we issue the same instruction N times. Compilers even have specific directives for that; for example, [`#pragma unroll`](https://gcc.gnu.org/onlinedocs/gcc/Loop-Specific-Pragmas.html).

Loop unrolling is used throughout simdvec code to exploit the inner parallelism of modern CPUs; the issue with `#pragma unroll` is that it’s a *hint* to the compiler, not a directive. Furthermore, its efficacy depends on compilation flags and compiler heuristics, so the compiler can decide not to unroll or can perform a nonperfect unrolling. For example, when we looked at the assembly the compiler produced for this loop, we saw it was unrolled but the dependency chain was still there. Manual unrolling is still needed for precise control or portability, but it’s difficult to read and impossible to maintain.

### C++ templates and meta-programming

[C++ templates](https://en.wikipedia.org/wiki/Template_(C%2B%2B)) let you write generic code with placeholder types or values that the compiler fills in at compile time. Write the function template once, and the compiler emits a specialized copy for every set of arguments you use it with. The placeholder can be a type (for example, `float` versus `int`, or register types, like `__m512i` or `uint8x16_t`), a function, a compile-time integer, … This last form is what we use most heavily: A template parameterized by an integer N lets us generate N parallel accumulators or N copies of an inner-loop body. [*Metaprogramming*](https://en.wikipedia.org/wiki/Template_metaprogramming) is essentially code that writes code: It uses the compiler to perform computations at compile time, with no runtime cost.

Our main tool is `apply_indexed<N>`, a compile-time function that emits N statements as it’s unfolded:

```
template <int N, typename F, int I = 0>
static inline void apply_indexed(F&& f) {
    if constexpr (I < N) {
        f(std::integral_constant<int, I>{});
        apply_indexed<N, F, I + 1>(std::forward<F>(f));
     }
 }
```

The [`if constexpr`](https://en.cppreference.com/cpp/language/if#Constexpr_if) is a compile-time branch, making `apply_indexed` compile-time recursive; the compiler will resolve the constexpr and instantiate the next iteration of the template. Everything is handled by the compiler; no runtime branch is emitted.

We used `apply_indexed<N>` to implement [cascade unrolling](https://github.com/elastic/elasticsearch/pull/145683):

```
apply_indexed<N>([&](auto I) { fma(acc[I], x[i + I*stride], y[i + I*stride]); });
```

We unroll into a cascade: First N=4 independent accumulator chains, dropping to 2 for any half-size tail, and then 1 for the final scalar tail. This gave us a +11–13% speedup across kernels and CPUs over `#pragma unroll` (all details and complete numbers can be found in the [PR linked above](https://github.com/elastic/elasticsearch/pull/145683)). The compiler could only get us so far; generic programming via C++ template instantiation is how we keep this extremely efficient yet compact and tractable across kernels and ISAs.

## Batch processing and prefetching: hiding memory latency

Unrolling addresses [instruction-level parallelism](https://en.wikipedia.org/wiki/Instruction-level_parallelism) within a single vector computation but doesn’t exploit the advantages of processing in bulk.

Elasticsearch doesn't score one vector against one query; HNSW traversal alone scores hundreds of neighbors per query. Bulk scoring (one query matched against many documents) gives us both a new problem and the tools to solve it.

The vectors we score are often scattered across memory, producing irregular access patterns that are difficult for the CPU caches and hardware prefetchers to predict. This increases the likelihood that the data the CPU needs is not in the fast L1d cache and has to be fetched from further away (*cache miss*). [The typical cost](https://colin-scott.github.io/personal_website/research/interactive_latency.html) ranges from ~five cycles for an L1d hit to ~200+ cycles when the data must come from RAM.

![Diagram showing two CPU cores with L1 caches, shared L2 and L3 caches, and separate RAM.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte58ad09b44bf8971/6a478ac1ae0523aed9c3dcd6/13fedfbaa7efcaa99179ac48c712e921ee667621-1445x901.png)

It doesn’t matter if we maximized load port occupancy; if those ports stall waiting for data, the compute ports sit idle. The FMA throughput we saturated via cascade unrolling goes to waste. Retrieving data from memory to the L1d cache is time-consuming, especially if we need to traverse the whole memory hierarchy to RAM. Fortunately, as we know that we’re going to score multiple vectors, we can prime the CPU cache with the next vector (or vectors), effectively reducing or hiding the memory access latency.

Batching also helps with instruction latency, for the same reason cascade unrolling does: N independent vector streams give the CPU N independent accumulator chains to interleave, hiding the FMA pipeline latency we discussed earlier.

This is why we added *batches* to bulk scoring ([starting with int7](https://github.com/elastic/elasticsearch/pull/139069), later extended to all data types); the same mechanism as cascade unrolling but applied inter-vector. We process not one, but N vectors at the same time, and while we do that, we preload ([prefetch](https://en.wikipedia.org/wiki/Cache_prefetching)) data for the next N vectors. That *should* help with prefetching and instruction latency, and it does in many cases: for example, [for int7](https://github.com/elastic/elasticsearch/pull/139069#issuecomment-3614348807) we immediately saw a +20–50% improvement over non-unrolled bulk (all details and JMH benchmarks can be found in the linked PR). But as we tried to apply it to all our bulk functions, we noticed it introduced new problems/constraints.

## Too much of a good thing: why burst prefetching overflows the line-fill buffer

Prefetching only helps if the line lands in L1d before the inner loop needs it. Our first attempt issued every prefetch for the next batch at the batch boundary, a burst of ~28–100 software prefetches back to back, depending on the kernel.

Processors have a limited per-core [line-fill buffer (LFB)](https://perfwiki.github.io/main/glossary/#lfb); this maps directly to the maximum number of outstanding cache misses the core can track at once. As an example, Sapphire Rapids has an LFB of just 16 entries. A burst that big overflows the LFB, and the excess prefetches are silently dropped. The inner loop ends up waiting on cache misses for lines we thought were already on the way.

The fix is to spread the prefetches across the inner loop. At the batch boundary, we issue only a small head burst, enough to cover the first cache lines the inner loop will consume, and then spread the rest across iterations, each iteration pulling in the lines for the next. The total number of prefetches is unchanged, but the LFB peak occupancy drops by an order of magnitude. Lines arrive ~one outer iteration before they are demand-loaded, hiding the L2 to L1 transfer latency, and the L2 stream prefetcher coordinates better with a steady stride than with the boundary burst. [Head + spread landed first for int8](https://github.com/elastic/elasticsearch/pull/147865) and then was [extended to int7](https://github.com/elastic/elasticsearch/pull/147999) and [the rest of the kernels](https://github.com/elastic/elasticsearch/pull/148945), with a performance boost of up to +30%.

## Stomping on our own feet: why did batching hurt performance on power-of-2 dimensions?

The right amount of prefetching should have given us high throughput, hiding most of the memory latency. And it did… most of the time. When vector data is effectively accessed in a sparse, random way, it works really well. But when we tried to parallelize bulk processing of sequential, contiguous documents across a batch of four, on power-of-2 dims, performance fell off a cliff.

### How N-way associative cache causes power-of-2 conflicts

CPU caches are organized into cache *lines* and *sets*. A cache *line* is the unit of data transferred through the memory hierarchy; on both ARM and x86, it’s 64 bytes long. Each cache line maps to exactly one cache *set*, and each set can hold a fixed number of lines. This is known as an [N-way associative cache](https://en.wikipedia.org/wiki/Cache_placement_policies#Set-associative_cache).

A useful analogy is a hash table where every bucket has exactly N slots. Multiple memory addresses may map to the same bucket (set), but once all N slots are occupied, inserting a new entry forces an existing one to be evicted.

Let’s take a concrete example. [Sapphire Rapids](https://en.wikipedia.org/wiki/Sapphire_Rapids) L1d cache is 48 KiB and 12-way associative. At 64 bytes per cache line, that gives us 768 cache lines organized into 64 sets. A cache line's set index (the “hashtable key”) is determined by bits [11:6] of the address (or, in other words, by `(address / 64) % 64)`.

![Diagram showing how data blocks from RAM labeled Vector 1 map to cache sets and lines.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt84a17d771cd09df8/6a478ac5569c0d6b7225bc95/69a0f35f9261b398be12e6611590842a8cc4a7ec-1920x925.png)

Suppose we have a float32 embedding with 1024 dimensions, stored contiguously in memory. Each vector occupies `dims * sizeof(float32)`= 4096 bytes, or exactly 64 cache lines. The stride between consecutive vectors is therefore 4096 bytes. Since 4096 is exactly one full wrap around the 64-set index space, the set index wraps perfectly: The i-th cache line of every vector maps to the exact same cache set.

![Diagram showing how data blocks from two RAM vectors map to cache sets and lines using red and green blocks.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt61ba13c122371b17/6a478ac8bfe8a29bbb4da290/6a36c4883acfa240fcfcf41028b5075ef2244f3e-1920x988.png)

Common power-of-2 vector sizes produce a stride that's a power-of-2 in bytes, which divides 64 sets evenly, so they interact pathologically with the cache in exactly this way. Processing together a batch of N documents with such dimensions exacerbates the situation: As they fall into the same L1d sets, they cause conflicts and cache thrashing.

### Fixing cache aliasing by reducing batch parallelism

We first examined in depth this effect while working on [kernels for the bf16 data type](https://github.com/elastic/elasticsearch/pull/145629). As we tried different implementations and `batches` values for the new kernels, we conducted extensive benchmarking, which confirmed the hypothesis that with power-of-2 dimension sizes, contiguous vectors have strides that map to the same cache sets, and interleaving multiple load streams causes evictions. Therefore our immediate fix was simple: Set `batches=1` on functions with sequential access (`*_bulk`) to avoid L1d cache set aliasing.

However, we knew this to be a Band-Aid; bulk and wider parallelism would help with, for example, latency, so we wanted them if we could get them without reintroducing the cache conflicts.

### Unrolling along a different axis: saturating FMA pipelines without aliasing

`batches` parallelizes *across documents*, but that’s not the only axis available to us. We can unroll along the vector dimension axis instead. Rather than processing multiple vectors in parallel, we process multiple independent chunks of the same vector pair in parallel.

So [we introduced](https://github.com/elastic/elasticsearch/pull/147672) [`unroll_dim`](https://github.com/elastic/elasticsearch/pull/147672). Crucially, by keeping `batches=1`, we sidestep the cache‑set aliasing trap altogether, and `unroll_dim` keeps the FMA pipeline saturated without needing the extra parallel doc loads that triggered the aliasing in the first place.

It works extremely well in some cases (+35–65% for dot product, as you’ll see from the aforementioned PR), but in other cases, the gain was more modest than we expected (~+10% for Euclidean distance). As in the other cases, all details and JMH benchmarks can be found in the linked PR.

## Don’t repeat yourself: hoisting query loads to eliminate redundant port pressure

The modest gains from `unroll_dim` on Euclidean distance suggested another bottleneck was still hiding in the bulk loop. What we found was a structural inefficiency hiding in the bulk function template: The existing bulk scorer called the single-pair scorer for each document, reloading the query elements N (4) times per outer step.

For some functions, we were also unnecessarily repeating operations associated with the query elements multiple times. For example, the int8 Euclidean distance kernel (`sqri8`) was calling the [`vpmovsxbw`](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html#text=_mm512_cvtepi8_epi16&ig_expand=1747) sign-extension instruction four times per outer step.

Hoisting query loads and operations out of the per-document loop cut L1D bandwidth for the query elements 4x; for `sqri8`, it removed three of the four `vpmovsxbw` sign-extension instructions per outer step. Recall that throughput depends on port availability: `vpmovsxbw` can only execute on a single port (port 5 on Sapphire Rapids), so issuing four copies per step saturated that port entirely; the sign extensions alone were the bottleneck.

![Diagram comparing two computation methods: one showing batched queries processed by a kernel into vectors, and another showing shared kernel unrolling across queries.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt88e38a5aef06dd51/6a478acb569c0d1e7e25bc99/6325406dfa98bee78643c0505dbb05a668ec302d-1920x988.png)

Even when there’s no query-specific operation to hoist, the change matters. For `doti8`, [`vpdpbusd`](https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html#ig_expand=1747,2692,2692&text=_mm512_dpbusd_epi32) executes on two ports (0 and 5 on Sapphire Rapids) with a latency of five cycles, so we need ~10 independent operations in flight to reach peak throughput. With the query load hoisted, the inner loop becomes dependency-bound on a single accumulator chain per batch element. The redundant work now gone, `unroll_dim=2` can fill the latency window by adding independent chains along the dim axis.

This [structural refactoring](https://github.com/elastic/elasticsearch/pull/147865) gave us a good speedup: +19–22% on dot product, +44–51% on Euclidean distance (all details and complete numbers can be found in the linked PR).

## One step back for the perfect landing

Not every optimization survives. After all the work to introduce `unroll_dim`, benchmarking showed that it didn’t help uniformly: For some kernels and access patterns, the extra register pressure and code complexity brought nothing measurable. We could have left it in place with `unroll_dim=1` (functionally a no-op), but dead scaffolding is technical debt that makes the next change harder to reason about. So we [removed it where it didn’t pay for itself](https://github.com/elastic/elasticsearch/pull/147672), keeping the code clean.

On a tightrope, sometimes the right move is a step back.

## Key takeaways: optimizing vector search low-level memory access

Every optimization in this post followed the same pattern: Solve one bottleneck, reveal the next. Cascade unrolling saturated the FMA ports, which exposed memory latency. Batching and prefetch hid that latency, which uncovered L1d set aliasing. Dim-axis unrolling sidestepped the aliasing, which uncovered redundant query work. And removing that redundancy finally let the whole pipeline breathe.

There’s no single optimization that makes simdvec kernels fast. Each improvement changes the bottleneck rather than eliminating it, and each step can expose new unanticipated constraints. At this level, memory abstractions are an illusion: Performance depends on understanding what the CPU is actually doing, not just what the model suggests. The only way forward is to measure, understand, and rebalance.

| Optimization | Gain |
| --- | --- |
| Cascade unrolling (vs. #pragma unroll) | +11-13% |
| Batching / prefetching (int7) | +20-50% |
| Head + spread prefetch | Up to +30% |
| Dim-axis unrolling (dot product) | +35-65% |
| Query load hoisting (dot product) | +19-22% |
| Query load hoisting (Euclidean distance) | +44-51% |

This is the first in a series of deep dives into Elasticsearch simdvec. Next time, we’ll look at how algebraic rewrites let us sidestep CPU limitations entirely.

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