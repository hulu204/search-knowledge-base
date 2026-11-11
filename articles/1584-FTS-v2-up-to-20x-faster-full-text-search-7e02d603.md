---
title: 'FTS v2: up to 20x faster full-text search'
company: turbopuffer
tag: 工程相关
date: 2025-12-04
url: https://turbopuffer.com/blog/fts-v2
account: 
origin: harvest3-202607
---
[NEW: Instant namespace branchingNEW: Branching for instant, copy-on-write namespaces](/docs/branching)

# FTS v2: up to 20x faster full-text search

Updated: February 03, 2026•Adrien Grand (Engineer), Morgan Gallant (Engineer), Nikhil Benesch (Engineer)

turbopuffer's [full-text search](/docs/fts) engine is getting a major upgrade -
what we call FTS v2 - resulting in **up to 20x better full-text search
performance** through a combination of a
[new index structure](/blog/fts-v2-postings) and an
[updated query implementation](/blog/fts-v2-maxscore).

FTS v2 is now live for all turbopuffer customers.

### What's new with FTS v2

Large datasets, low `top_k` values, and queries including frequent terms will
get the greatest speedups. Below are some performance comparisons for a diverse
set of queries that we computed on an export of English Wikipedia containing a
bit more than 5M documents.

```
 turbopuffer FTS latency (k=100, dataset=English Wikipedia export @ ~5M documents)
                           
                           
         san francisco  v1 ║░░░ 8ms
                        v2 ║▓ 3ms
                           ║
                           ║
               the who  v1 ║░░░░░░░░░░░░░░░░░ 57ms
                        v2 ║▓▓ 7ms
                           ║
                           ║
         united states  v1 ║░░░░░░ 20ms
          constitution  v2 ║▓▓ 5ms
                           ║
                           ║
     lord of the rings  v1 ║░░░░░░░░░░░░░░░░░░░░░░░ 75ms
                        v2 ║▓▓ 6ms
                           ║
                           ║
 pop singer songwriter  v1 ║░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 174ms
    born 1989 won best  v2 ║▓▓▓▓▓▓ 20ms
     country song time     ║
    person of the year     ║
```

```
 turbopuffer FTS latency (ms)
 
 k=100,
 English Wikipedia export
 ~5M documents

                         174ms
  ░░ v1                  ░░
                         ░░
  ▓▓ v2                  ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                         ░░
                   75ms  ░░
                   ░░    ░░
                   ░░    ░░
       57ms        ░░    ░░
       ░░          ░░    ░░
       ░░          ░░    ░░
       ░░          ░░    ░░
       ░░    20ms  ░░    ░░20ms
       ░░    ░░    ░░    ░░▓▓
 8ms   ░░7ms ░░    ░░6ms ░░▓▓
 ░░3ms ░░▓▓  ░░5ms ░░▓▓  ░░▓▓
 ░░▓▓  ░░▓▓  ░░▓▓  ░░▓▓  ░░▓▓
 ══════════════════════════════
 q1    q2    q3    q4    q5
--------------------------------
 q1 = san francisco

 q2 = the who

 q3 = united states
      constitution

 q4 = lord of the rings

 q5 = pop singer songwriter
      born 1989 won best
      country song time
      person of the year
```

Semantic search may get more press, but full-text search is equally important
for recall and performance in agent-initiated queries. turbopuffer has a
dedicated full-text search team devoted to building the *right* set of features
for modern search. FTS v2 is the next iteration toward our ambition for
economical, web-scale search for both humans and agents.

In the purest of turbopuffer traditions, we optimized FTS v1 for simplicity,
knowing that we had much room for improvement. With FTS v2, we are very happy to
now be achieving **search performance that is comparable to best-in-class search
libraries like Tantivy and Apache Lucene**.

In fact, FTS v2 takes its inspiration directly from Tantivy and Lucene in its
architecture. The performance leap is the result of two major changes:

1. **New index structure**: We've rebuilt the
   [core inverted index structures of full-text search](/blog/fts-v2-postings),
   resulting in a 10x size reduction on-disk. The new format includes important
   metadata which allows queries to "skip" large chunks of unrelevant postings.

   Stay tuned on this — we will soon publish a more detailed post about this
   improvement and how it delivers FTS v2's performance gains.
2. **Better search algorithm**: Agents write longer queries than humans. We
   switched to the same [MAXSCORE](/blog/fts-v2-maxscore) dynamic pruning
   algorithm as Apache Lucene, which scales better than alternatives for long
   queries while retaining excellent performance on short queries.

Beyond performance, FTS v2 introduces several new features to full-text search
on turbopuffer:

* A new [`word_v3` tokenizer](/docs/fts#tokenizers) for better unicode-aware
  text segmentation
* [Rank by filter](/docs/query#rank-by-filter) to conditionally boost documents
  matching certain criteria
* [Prefix queries](/docs/query#prefix-queries) for search-as-you-type filtering
* [Regex filtering](/docs/query#param-Regex)

Other full-text search improvements are [already on the way](/docs/roadmap):
ranking by attributes, highlighting, better search-as-you-type, fuzziness, and
globbing are all on our radar. We're building features to support
state-of-the-art ranking and will prioritize based on both observed query
patterns and your feedback.

---

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