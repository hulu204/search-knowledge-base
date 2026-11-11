---
title: 'Why BM25 queries with more terms can be faster (and other scaling surprises)'
company: turbopuffer
tag: 工程相关
date: 2026-01-07
url: https://turbopuffer.com/blog/bm25-latency-musings
account: 
origin: harvest3-202607
---
[NEW: Instant namespace branchingNEW: Branching for instant, copy-on-write namespaces](/docs/branching)

# Why BM25 queries with more terms can be faster (and other scaling surprises)

January 07, 2026•Adrien Grand (Engineer)

BM25 full-text search has very different scaling characteristics than vector
search. Vector search latency is generally a function of vector dimensions,
top-k, the size of the dataset, and the presence of filters. BM25 latency, on
the other hand, also varies *a lot* by query, and in some surprising ways:

* Sometimes adding a new term to a query actually makes it *faster*
* The fastest query at top\_k=10 may not be fastest at top\_k=10000

This post discusses what I learned modeling BM25 query latencies across varying
term counts, document counts, and top\_k values.

## Background

turbopuffer implements [BM25 full-text search](/docs/fts) by indexing text data
into an inverted index, a data structure that maps unique terms to the list of
document IDs that contain these terms, which are called “postings”.

```
   term                      posting list
  ┌────────────┐            ┌───┬───┐
  │ pufferfish ├───────────▶│ 1 │ 2 │ // "pufferfish" appears in few documents
  └────────────┘            └───┴───┘
  ┌────────────┐            ┌───┬───┬───┬───┬───┐
  │ fish       ├───────────▶│ 1 │ 2 │ 4 │ 6 │ 9 │ // appears in more documents
  └────────────┘            └───┴───┴───┴───┴───┘
  ┌────────────┐            ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬─
  │ to         ├───────────▶│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ ••• // apears in many
  └────────────┘            └───┴───┴───┴───┴───┴───┴───┴───┴───┴─
  ┌────────────┐            ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬─
  │ be         ├───────────▶│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ ••• 
  └────────────┘            └───┴───┴───┴───┴───┴───┴───┴───┴───┴─
  ┌────────────┐            ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬─
  │ or         ├───────────▶│ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ •••
  └────────────┘            └───┴───┴───┴───┴───┴───┴───┴───┴───┴─
```

```
 term           posting list
┌────────────┐  ┌───┬───┐
│ pufferfish ├─▶│ 1 │ 2 │
└────────────┘  └───┴───┘
┌──────────┐    ┌───┬───┬───┬───┐
│ fish     ├───▶│ 1 │ 2 │ 6 │ 9 │
└──────────┘    └───┴───┴───┴───┘
┌────────┐      ┌───┬───┬───┬───┬───┬──
│ to     ├─────▶│ 1 │ 2 │ 3 │ 4 │ 5 │•••
└────────┘      └───┴───┴───┴───┴───┴──
┌────────┐      ┌───┬───┬───┬───┬───┬──
│ be     ├─────▶│ 1 │ 2 │ 3 │ 4 │ 5 │•••
└────────┘      └───┴───┴───┴───┴───┴──
┌────────┐      ┌───┬───┬───┬───┬───┬──
│ or     ├─────▶│ 1 │ 2 │ 3 │ 4 │ 5 │•••
└────────┘      └───┴───┴───┴───┴───┴──
```

To exhaustively evaluate a BM25 query, you must fully consume all postings of
all query terms. This is why a query on a single uncommon term such as
“pufferfish” will always be very fast, while a query on several frequent terms
such as “to be or not to be” will be slower.

Algorithms like [WAND or MAXSCORE](https://turbopuffer.com/blog/fts-v2-maxscore)
help skip parts of postings lists while retaining 100% recall. They work by
reasoning on the respective score contribution of each term. For instance, if
your query is "the pufferfish", they will quickly realize that they can skip
documents that only contain "the" and only use documents that contain
"pufferfish" as candidates. In MAXSCORE’s terminology, pufferfish is an
essential term while “the” is a non-essential term. These algorithms are
considered “rank-safe”, as they return the very same top\_k hits as exhaustive
evaluation. But, as you'll see below, the number of documents that WAND and
MAXSCORE are able to skip varies greatly by query.

## Modeling BM25 query latency

Consider the following queries:

1. singer
2. pop singer
3. pop singer songwriter
4. american pop singer songwriter
5. american pop singer songwriter born 1989
6. american pop singer songwriter born 1989 won best country song
7. american pop singer songwriter born 1989 won best country song time person of
   year

As you may have noticed, every new query adds one or more terms to the previous
query. So the total number of postings increases with each new query.

Now let’s run these queries against a 200M-doc namespace
([Common Crawl](https://commoncrawl.org/) dataset, top\_k=20, ~6.3KiB per doc,
~1.26TiB total, single thread, turbopuffer’s vectorized MAXSCORE, unfiltered,
the whole inverted index fits in RAM):

| Query | Total number of postings | Latency (ms) | Latency per million postings (ms) |
| --- | --- | --- | --- |
| 1 | 859,959 | 1.0 | 1.2 |
| 2 | 5,819,599 | 9.6 | 1.6 |
| 3 | 6,105,644 | 5.5 | 0.9 |
| 4 | 20,586,327 | 13.4 | 0.7 |
| 5 | 24,493,090 | 21.0 | 0.9 |
| 6 | 72,396,519 | 61.6 | 0.9 |
| 7 | 363,352,440 | 107.7 | 0.3 |

**Interestingly, query 3 (”pop singer songwriter”) runs faster than query 2
(”pop singer”) despite having one more term!** This may sound counterintuitive;
query 3 has more terms and thus should be harder to evaluate, but it’s actually
easier on MAXSCORE.

During most of query evaluation, query 2 has “singer” (~ 850k postings) as an
essential term and “pop” as a non-essential term, while query 3 has “songwriter”
(~ 300k postings) as an essential term and “pop” and “singer” as non-essential
terms. So query 3 needs to evaluate about 3x fewer candidate documents in total,
which more than compensates for the fact that it has one more term to evaluate.

For reference, here is how terms get partitioned for these queries during most
of their evaluation:

| Query | Essential terms | Non-essential terms | Total number of postings of essential terms |
| --- | --- | --- | --- |
| 1 | singer |  | 859,959 |
| 2 | singer | pop | 859,959 |
| 3 | songwriter | pop singer | 286,045 |
| 4 | songwriter | american pop singer | 286,045 |
| 5 | songwriter | american pop singer songwriter born 1989 | 286,045 |
| 6 | singer songwriter | american pop born 1989 won best country song | 1,146,004 |
| 7 | singer songwriter won | american pop born 1989 best country song time person of year | 2,565,517 |

The takeaway here is that the total number of postings of *essential* terms
sometimes has a bigger impact on BM25 latencies than total number of terms.

However, this factor alone is still not enough to characterize the performance
of a query, as queries that have the same essential terms may still have very
different latencies, even though they use similar sets of candidate documents.
This is because we also need to factor in the cost of applying non-essential
clauses, which on its own also depends on many factors.

Also interesting: query 7, while the slowest query, also has the best latency
per million postings. This is because it contains “of” (200M postings, the whole
namespace), which it skips extremely efficiently. If you were to evaluate query
7 exhaustively, it would be horrendously slow as it attempted to compute the
BM25 score of every single document in the namespace. MAXSCORE saves us a lot of
work on this query.

### How query latency scales with number of documents

Now let’s see how these latencies scale with the number of documents. For this
experiment, I iteratively indexed 1M documents and measured latencies until
reaching 200M documents.

I then did a linear regression to model the latency of all these queries as ƒ(n)
= C · nK, where n is the number of documents. C and K are
coefficients that depend on the specific query, and K describes how well a query
scales with document count (lower is better). As K approaches 1, latency will
scale linearly with document count. This gave the following results (note the y
axis of the chart is log scale):

Loading chart data...

| Query | C | K |
| --- | --- | --- |
| 1 | 0.00023 | 0.44 |
| 2 | 0.0000056 | 0.75 |
| 3 | 0.0000086 | 0.70 |
| 4 | 0.000055 | 0.65 |
| 5 | 0.00012 | 0.63 |
| 6 | 0.0000064 | 0.84 |
| 7 | 0.0000024 | 0.92 |

This confirms our previous observation that queries 6 and 7 are not only slower,
they are also **harder to scale** as the relative gap with other queries
increases as the number of documents increases. Query 7 in particular scales
near-linearly as its K value approaches 1.

You may wonder if MAXSCORE still makes sense on long queries if latency scales
near-linearly with the number of documents? The answer is yes. The shape of the
function is one thing, but the constant factor is also very important in
practice. As I noted earlier, query 7 also has best latency per million
postings; switching to exhaustive evaluation would make it horrendously slow.

### How query latency scales with top\_k

Now let’s check out the effect of top\_k by progressively increasing top\_k while
always querying all 200M docs (note that the chart uses a log scale on both the
x and y axes):

Loading chart data...

| Query | C | K |
| --- | --- | --- |
| 1 | 0.22 | 0.46 |
| 2 | 5.2 | 0.19 |
| 3 | 1.7 | 0.31 |
| 4 | 5.8 | 0.26 |
| 5 | 8.2 | 0.29 |
| 6 | 32 | 0.21 |
| 7 | 51 | 0.22 |

Trying to model these series as ƒ(top\_k) = C · top\_kK is a bit less
satisfying than on the previous chart, but it still looks sensible. There are
several interesting things to notice here as well:

* Lines cross! While query 3 is faster than query 2 at top\_k=10, it becomes
  slower at top\_k=10,000.
* There is no obvious correlation between the number of terms and how well
  queries scale (the value of K). Queries 1, 3, and 5 get the higher K values
  (0.46, 0.31, 0.29 respectively) while queries 2, 6, and 7 get the lower K
  values (0.19, 0.21, 0.22 respectively).
* The resulting K values for query 6 and 7 are 0.21 and 0.22, which is quite
  good. Said otherwise, BM25 latencies scale quite efficiently as top\_k
  increases, even for the harder queries of our benchmark. Multiplying top\_k by
  10 “only” increases latency by 65%.

## Conclusion

Hopefully this blog post has helped you develop a better intuition for latencies
of BM25 full-text search queries. Some takeaways:

* Query performance is proportional to document count.
* The more terms in a query, the more linearly it scales with document count.
  Longer queries become relatively slower as datasets grow
* Query latency isn't always directly proportional to the total number of terms.
  When using skipping algorithms like MAXSCORE, essential term count can be more
  determinative of latency than total term count
* Latency scales quite efficiently with top\_k, but the best queries at small
  top\_k might not be the best queries at large top\_k

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