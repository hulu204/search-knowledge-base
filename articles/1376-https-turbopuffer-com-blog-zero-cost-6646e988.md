---
title: 'https://turbopuffer.com/blog/zero-cost'
company: turbopuffer
tag: 搜索
date: 
url: https://turbopuffer.com/blog/zero-cost
account: 
origin: en-rss
---
[NEW: Instant namespace branchingNEW: Branching for instant, copy-on-write namespaces](/docs/branching)

# Rust zero-cost abstractions vs. SIMD

Updated: March 08, 2026•Xavier Denis (Engineer)

We reduced the latency on a full-text search query from 220ms →
47ms\* by looking under the hood of Rust’s “zero-cost” iterators to
find that they were silently preventing vectorization. This post serves as a
reminder that zero-cost abstractions do not absolve you from practicing
mechanical sympathy.

```
 avg latency, filtered BM25 query, 5 million documents

 before   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 220 ms
 after    ▓▓▓▓▓▓▓▓▓▓▓▓▓ 47 ms
```

```
avg latency, 
filtered BM25 query, 
5 million documents
     
  ░░░░ 220 ms
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░   ▓▓▓▓ 47 ms
  ░░░░   ▓▓▓▓
  ░░░░   ▓▓▓▓ 
 ══════ ══════
 before  after
```

\**This work predates [FTS v2](/blog/fts-v2). Current p90 full-text
search latencies on 5M-document namespaces are ~5-10ms on a hot cache.*

Several months ago, one of our customers was struggling with high latency on a
full-text (BM25) query that does a bunch of permissions checks, with up to
thousands of permissions identifiers passed in a `ContainsAny` filter. Something
like this:

```
{
  "filters": ["attribute", "ContainsAny", ["a", "c", "f", "j", "m", "o", "t", "x", "z", ...]],
  "rank_by": ["text", "BM25", "some query string"]
}
```

Filtered BM25 queries such as this are common on turbopuffer, routinely taking
less than 50ms over millions of documents. This one seemed innocuous, yet it was
taking over 4× that long. Examining the query profiles revealed something
interesting: only about 10ms was being spent on the actual BM25 ranking; the
rest (>200ms) was being spent *evaluating filters*.

Filter evaluation of this kind should be cheap. In fact, our query planner
reported the size of the relevant filter bitmaps (representing which documents
match each filter value) as only 67MB for this query. Based on some
[napkin math](https://github.com/sirupsen/napkin-math), reading from an NVMe SSD
(at a max throughput of 6,240 MB/s) and processing should only take 10-20ms.

Typically when there's a large gap between napkin math and reality, it means
there's either a big opportunity for optimization or a bug in our understanding.
So we started digging...

## Understanding the turbopuffer read path

turbopuffer stores all indexed data in a
[Log-Structured Merge (LSM) tree](/docs/concepts#log-structured-merge-lsm-tree).
Key-value pairs are stored in sorted files (SSTables) on object storage. A
single sorted file would make reads simple (low read amplification), but every
write would need to re-sort the entire dataset (high write amplification).
Instead, new KV pairs are written to small files to minimize write amplification
and asynchronously compacted (merged and deduplicated) into larger files to
minimize read amplification. LSM compaction keeps writes fast while limiting how
many files a read must touch.

Each file contains metadata describing its minimum and maximum keys. To serve a
read, the query engine uses this metadata to find the files that could contain
matching keys, then performs a
[byte-range fetch](https://docs.aws.amazon.com/AmazonS3/latest/userguide/range-get-olap.html)
to get the relevant key ranges from the files.

```
query(i OR j) ─▶ read ─▶ merge 3 iters ─▶ filter/rank ─▶ result
                 ▲▲▲                                     
                ┌┘│└─────┐
╔═ LSM tree ════│═│══════│═════════════════════════╗
║               │ └──┐   │                         ║
║  ┌──┐   ┌──┐  │┌──┐│  ╔╧═╗   ┌──┐   ┌──┐   ┌──┐  ║
║  │ab│   │cd│  ││fg││  ║ij║   │mn│   │op│   │xy│  ║
║  └──┘   └──┘  │└──┘│  ╚══╝   └──┘   └──┘   └──┘  ║
║               │    │                             ║
║               │    │                             ║
║  ┌──┬──┬──┬──┐│   ╔╧═╗──┬──┬──┐   ┌──┬──┬──┬──┐  ║
║  │ab│cd│ef│gh││   ║ij║kl│mn│op│   │rs│tu│vw│yz│  ║
║  └──┴──┴──┴──┘│   ╚══╝──┴──┴──┘   └──┴──┴──┴──┘  ║
║               │                                  ║
║               │                                  ║
║  ┌──┬──┬──┬──╔╧═╗──┬──┐  ┌──┬──┬──┬──┬──┬──┬──┐  ║
║  │ab│cd│ef│gh║ij║kl│mn│  │op│qr│st│uv│wx│yz│⍺β│  ║
║  └──┴──┴──┴──╚══╝──┴──┘  └──┴──┴──┴──┴──┴──┴──┘  ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

```
query(i OR j) ─▶ read ─▶ merge
                 ▲▲▲                                     
                 ││└──┐
╔═ LSM tree ═════││═══│═══════════╗
║                │└┐  │           ║
║  ┌──┐ ┌──┐ ┌──┐│╔╧═╗│┌──┐ ┌──┐  ║
║  │ab│ │cd│ │fg││║ij║││mn│ │op│  ║
║  └──┘ └──┘ └──┘│╚══╝│└──┘ └──┘  ║
║                │    │           ║
║                │  ┌─┘           ║
║  ┌──┬──┬──┬──┐ │╔═╧╗──┬──┬──┐   ║
║  │ab│cd│ef│gh│ │║ij║kl│mn│op│   ║
║  └──┴──┴──┴──┘ │╚══╝──┴──┴──┘   ║
║                │                ║
║                │                ║
║  ┌──┬──┬──┬──╔═╧╗──┬──┬──┬──┐   ║
║  │ab│cd│ef│gh║ij║kl│mn│op│rs│   ║
║  └──┴──┴──┴──╚══╝──┴──┴──┴──┘   ║
║                                 ║
╚═════════════════════════════════╝
```

Our customer's query uses the [`ContainsAny`](/docs/query#param-ContainsAny)
filter, essentially an `OR` to match all values (e.g.
`"a" OR "c" OR "f" OR "j" OR "m" OR "o" OR "t" OR "x" OR "z" OR ...`).

Each value in the filter triggers a separate key lookup fanning out across many
disjoint key ranges.

```
query(a OR c OR f OR ──────▶ read ─▶ merge 24 iters ─▶ filter/rank ─▶ result
      j OR m OR o OR         ▲▲▲
      t OR x OR z)           │││                    
                      ┌──────┘│└───┐
╔═ LSM tree ══════════│═══════│════│═══════════════╗
║    ┌──────┬──────┬──────┬───┴─┬──────┬──────┐    ║
║  ╔═╧╗   ╔═╧╗   ╔═╧╗ │ ╔═╧╗   ╔╧═╗│  ╔╧═╗   ╔╧═╗  ║
║  ║ab║   ║cd║   ║fg║ │ ║ij║   ║mn║│  ║op║   ║xy║  ║
║  ╚══╝   ╚══╝   ╚══╝ │ ╚══╝   ╚══╝│  ╚══╝   ╚══╝  ║
║                     │            │               ║
║    ┌──┬──┬──────────┼────┬──┬─────────┬─────┐    ║
║  ╔═╧╦═╧╦═╧╗···    ╔═╧╗··╔╧═╦╧═╗  │···╔╧═╗··╔╧═╗  ║
║  ║ab║cd║ef║gh·    ║ij║kl║mn║op║  │·rs║tu║vw║xy║  ║
║  ╚══╩══╩══╝···    ╚══╝··╚══╩══╝  │···╚══╝··╚══╝  ║
║                                  │               ║
║    ┌──┬──┬─────┬─────┬────┬──────┼────┬──┐       ║
║  ╔═╧╦═╧╦═╧╗··╔═╧╗··╔═╧╗  ╔╧═╗··╔═╧╗··╔╧═╦╧═╗···  ║
║  ║ab║cd║ef║gh║ij║kl║mn║  ║op║qr║st║uv║wx║yz║⍺β·  ║
║  ╚══╩══╩══╝··╚══╝··╚══╝  ╚══╝··╚══╝··╚══╩══╝···  ║
║                                                  ║
╚══════════════════════════════════════════════════╝
```

```
query(a OR c OR ─▶ read ─▶ merge
      f OR j OR    ▲▲▲
      m OR o)      │││    
                 ┌─┘│└─────┐
╔═ LSM tree ═════│══│══════│══════╗
║    ┌────┬────┬────┼───┬────┐    ║
║  ╔═╧╗ ╔═╧╗ ╔═╧╗│╔═╧╗ ╔╧═╗│╔╧═╗  ║
║  ║ab║ ║cd║ ║fg║│║ij║ ║mn║│║op║  ║
║  ╚══╝ ╚══╝ ╚══╝│╚══╝ ╚══╝│╚══╝  ║
║                │         │      ║
║    ┌──┬──┬────────┬────┬─┴┐     ║
║  ╔═╧╦═╧╦═╧╗··┐ │╔═╧╗··╔╧═╦╧═╗   ║
║  ║ab║cd║ef║gh╵ │║ij║kl║mn║op║   ║
║  ╚══╩══╩══╝··┘ │╚══╝··╚══╩══╝   ║
║                │                ║
║    ┌──┬──┬─────┼─────┬──┐       ║
║  ╔═╧╦═╧╦═╧╗··╔═╧╗··╔═╧╦═╧╗··┐   ║
║  ║ab║cd║ef║gh║ij║kl║mn║op║rs╵   ║
║  ╚══╩══╩══╝··╚══╝··╚══╩══╝··┘   ║
║                                 ║
╚═════════════════════════════════╝
```

Each returned key range produces an iterator over its KV pairs, and these
iterators must be merged into a single, sorted, deduplicated stream for
filtering and ranking.

## Looking inside the merge iterator

The iterators for all key ranges are passed into a merge iterator, which returns
keys in order and keeps the most recent KV pair when duplicate keys occur.

The merge for our customer's `ContainsAny` query, with thousands of filter
values – each of which might produce a separate key range – will be
comparatively more expensive than that for a query fetching only a few
contiguous key ranges.

Still, the merge itself should be cheap. Our merge iterator just compares keys
and moves the winning entry forward – relatively light work. It's built on
Rust's standard `Iterator` trait, a zero-cost abstraction, so it should compile
down to the same code as a hand-written loop with no additional overhead. In
nearly every other query, it was negligible. But the profile for this particular
customer's query clearly showed the merge consuming *over 60% of runtime*.

To try to find the hidden cost, let's look at a simplified Rust skeleton of one
of the core parts of our merge iterator code. The `scan()` function builds the
merge from all candidate key range iterators (here just slices of integers with
a position), then drains it in a loop, with each call to `next()` recursing down
through the merge structure to produce one value at a time. In production, the
loop body evaluates filters and scores results. Here, we substitute trivial
arithmetic to try to isolate the iterator cost.

```
fn scan(keys: &[Vec<u64>]) -> u64 {
    let mut merge_tree = Merge::build(keys);
    let mut sum = 0u64;

    // next() recurses down to produce the smallest current key
    while let Some(v) = merge_tree.next() {
        // Simple arithmetic: sum if even
        let x = v + 1;
        if x % 2 == 0 { sum += x; }
    }
    sum
}
```

If we `scan` 100,000 integers on a modern 3 GHz CPU, we would expect it to take
~130μs (100K values × 4 instructions each ÷ 3 billion cycles/sec), assuming only
scalar operations. In reality, it takes 6.5ms! 50× more expensive than it should
be if the iterator is truly "zero-cost".

At first glance, nothing in Rust explains the cost. The work is occurring purely
in memory, so we can eliminate I/O from consideration, yet something is clearly
preventing the CPU from ripping through these integers. Every engineer knows
that computers are a tower of ~~lies~~ abstractions, so we need to go below the
abstraction to look at what the compiler is actually generating.

## Disassembling the abstraction

A zero-cost abstraction promises that we couldn't hand-write faster code for the
same logic. Let's look at the ARM assembly for `scan()` to see how it compiles:

```
LBB10_1:                                                ; loop {
    sbfx    x8, x1, #0, #1                              ;
    add x9, x1, #1                                      ; x = v + 1
    and x8, x8, x9                                      ; x = (x is even) ? x : 0
    add x19, x8, x19                                    ; sum += x
    add x0, sp, #8                                      ;
    bl  __ZN14bench9ChainTree4next17haad780538028036aE  ; Some(v) = tree.next() else { break }
    tbnz    w0, #0, LBB10_1                             ; }
```

Indeed, the Rust compiler (LLVM) has produced a tight loop with just seven
instructions: the first four are the loop body, the last three the loop control.

The loop control calls `next()` and exits when it returns `None`, otherwise
continuing:

```
add x0, sp, #8                                      ; pass &mut self to next()
bl  __ZN14bench9ChainTree4next17haad780538028036aE  ; tree.next()
tbnz    w0, #0, LBB10_1                             ; continue if Some
```

Within the loop body, LLVM has been quite clever with our conditional
arithmetic; instead of evaluating `if` / branch, it uses a bitmasking trick to
simply add 0 to the sum if the value is odd.

```
sbfx x8, x1, #0, #1 ; mask: 0xFFFF..FFFF if v is odd (x is even), 0x0 if v is even
add x9, x1, #1      ; x = v + 1
and x8, x8, x9      ; x = x & mask (x is even ? x : 0)
add x19, x8, x19    ; sum += x
```

This is a standard compiler technique, called *predication*, that avoids the
cost of branch misprediction by turning a conditional into pure arithmetic.

Thanks to LLVM, the work inside the loop body compiles down to just four
arithmetic instructions per element; it should take ~130µs based on the napkin
math. So why is it taking 50× longer?

## The cost hides beneath the abstraction

The compiler wants to unroll iterations into larger blocks and vectorize with
SIMD (Single Instruction, Multiple Data) instructions to process multiple values
in parallel.

But it can't do any of that here because of the recursive nature of `next()`.
Each call to `next()` compares across iterators, mutates internal positions, and
returns one value. The compiler can't predict what a subsequent call will return
until the current one finishes, because each call's output depends on the state
left behind by the previous one. That kills unrolling (the compiler can't batch
calls it can't predict) and vectorization (can't process multiple values if they
arrive one at a time).

Herein lies the hidden opportunity cost of Rust's zero-cost abstraction in our
merge iterator. The iterator itself compiles down to the code you'd write by
hand for a *single* call. In that sense, it *is* zero-cost. But the abstraction
also prevents the compiler from vectorizing or unrolling *across* calls, so even
though the loop body is exactly the kind of dumb and serial work modern CPUs
devour, the compiler can't vectorize it. And the recursive calls to `next()`
bury 130µs of useful work inside 6.5ms of merge overhead.

For a query like our customer's `ContainsAny`, whose many disjoint key ranges
produce many iterators, the merge cost dominates.

## Breaking the abstraction to find a solution

To eliminate the opportunity cost, we need to give back to the compiler a tight
loop over contiguous data, with no recursive function calls in the middle.

The solution? A classic database technique called **batched iterators**.

Instead of producing a single element per call, the merge iterator now fills a
batch by comparing and interleaving KV pairs from its inputs, then returns the
entire batch at once. The consumer processes that batch as a plain array in a
tight loop, with no recursive calls in the middle.

Here's what that looks like in an updated Rust skeleton:

```
fn scan(keys: &[Vec<u64>]) -> u64 {
    let mut merge_tree = Merge::build(keys);
    let mut sum = 0u64;

    // next_batch() recurses down, but produces a batch (N=512) of KV pairs
    while let Some(batch) = merge_tree.next_batch() {
        // process the array
        for val in batch {
            let x = val + 1;
            if x % 2 == 0 { sum += x; }
        }
    }
    sum
}
```

Batching splits the work into two loops:

1. The outer loop calls the merge iterator once per batch
2. The inner loop processes the batch of values

The merge cost doesn't disappear, but it is now amortized across 512 KV pairs
rather than paid on every one. And since the inner loop is just walking a plain
array, the compiler can see the entire loop body and aggressively optimize it by
unrolling iterations and vectorizing with SIMD instructions.

The assembly confirms the optimization with the key difference in the inner loop
(`LBB11_4`). Whereas the original loop compiled to just seven scalar
instructions, the batched version processes 8 values at a time using SIMD
instructions (those ending in `.2d` and `.16b`):

```
LBB11_4:                        ; loop {
    add x9, x21, x8             ;
    ldp q4, q5, [x9, #16]       ; let vals = batch[i..i+8];
    ldp q6, q7, [x9, #48]       ;
    and.16b v16, v4, v20        ; let mask = vals & 1
    cmeq.2d v16, v16, #0.       ; mask = (vals & 1 == 0) ? all-ones : all-zeros
    add.2d  v4, v4, v20         ; let xs = vals + 1
    bic.16b v4, v4, v16         ; let xs = xs & mask
    add.2d  v1, v4, v1          ; sum += xs
    add x8, x8, #64             ; i += 8;
    cmp x8, #1, lsl #12         ; if i == batch.len() { break }
    b.ne    LBB11_4             ; }
```

With this change, our `scan` benchmark (100,000 values) runs in ~110μs, 60×
faster than before and even beating our 130μs napkin math estimate thanks to
SIMD.

```
 merge iterator execution time, 100k values in 64 blocks

 before   ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 6.5 ms
 after    ▓ 110 μs
```

```
merge execution,
100k values, 64 blocks

 
  ░░░░ 6.5 ms
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░
  ░░░░      
  ░░░░   ▓▓▓▓ 110 μs
 ══════ ══════
 before after
```

## Conclusion

"Zero-cost" promises that an abstraction compiles away, not that it has no side
effects. Rust's iterator compiled each call to code similar to what you'd write
by hand, but the abstraction boundary between calls hid the loop shape the
compiler needs to apply SIMD and unrolling across calls.

After we updated our production code to use batched iterators, our customer's
query latency dropped from ~220ms to 47ms. Their `ContainsAny` filter still fans
out across many key ranges, but the cost of the merge is now amortized across
batches with SIMD vectorization over each batch.

This is not a new problem, and the solution isn't new either; batched iterators
are a
[decades-old database technique](https://www.cidrdb.org/cidr2005/papers/P19.pdf).
But it required that we look below the abstraction and have the mechanical
sympathy to see what the CPU actually needed. Modern CPUs will only get faster
at doing dumb and serial work such as this. Our latest
[full-text search](/blog/fts-v2-maxscore) and
[approximate nearest neighbor](/blog/ann-v3) algorithms embody this. At the end
of the day, production profiles trump theory and abstraction. At turbopuffer we
continuously pore over them to
[squeeze](https://x.com/turbopuffer/status/2023783644704452759)
[more](https://x.com/turbopuffer/status/2015802057656242640)
[performance](https://x.com/turbopuffer/status/2012205150669086892) out of the
database.

## turbopuffer

turbopuffer is a fast search engine that hosts 4T+ documents, handles 10M+ writes/s, and serves 25k+ queries/s. We are ready for far more. We hope you'll trust us with your queries.

[Get started](/join)

![turbopuffer logo](/_next/static/media/lockup_transparent.6092c7ef.svg)

[Company](/about)[Pricing](/pricing)[Store](https://turbopuffer.supply)[Press & media](/press)[System status](https://status.turbopuffer.com)

Support

[Slack](https://join.slack.com/t/turbopuffer-community/shared_invite/zt-3v27t102a-3RynqZ5A9vuOuAo68X_wFQ)[Docs](/docs)[Email](/contact/support)[Sales](/contact/sales)

Follow

[Blog](/blog)[RSS](/blog/rss.xml)[Events](/events)

© 2026 turbopuffer Inc.

[Terms of service](/terms-of-service)[Data Processing Agreement](/dpa.pdf)[Privacy Policy](/privacy-policy)[Security & Compliance](/docs/security)

Docs search

esc

## Guides

[Quickstart

Get started with turbopuffer in minutes](/docs/quickstart)

[Vector Search

Perform approximate nearest neighbor searches](/docs/vector)

[Full-Text Search

Learn how to use BM25 full-text search](/docs/fts)

[Hybrid Search

Combine vector and full-text search strategies](/docs/hybrid)

## API Docs

[Write

Create, update, or delete documents](/docs/write)

[Query

Query documents with filters and ranking](/docs/query)

[Overview

Authentication, headers, and request encoding](/docs/api-overview)

[Namespace metadata

Get metadata about a namespace](/docs/metadata)

![](https://px.ads.linkedin.com/collect/?pid=8553810&fmt=gif)