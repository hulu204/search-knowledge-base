---
title: 'Why moving embedding inside turbopuffer drops search latency'
company: turbopuffer
tag: 召回
date: 2026-09-29
url: https://turbopuffer.com/blog/native-embedding
account: 
origin: en-rss
---
[tpuf v3 is coming: follow alongturbopuffer v3 is coming: follow our progress](/v3)

# Why moving embedding inside turbopuffer drops search latency

September 29, 2026•Ben Linsay (Engineer)

turbopuffer has historically been BYOE: bring your own embeddings. This allowed
us to focus solely on
[pushing the frontier of semantic search scale and performance](/blog/ann-v3)
while giving our customers the flexibility to fine-tune their embedding pipeline
for specific domains (finance, law, coding, etc.).

Over time, it's become clear that a lot of our customers see building an
embedding pipeline as less of an opportunity for optimization and more of a
chore — slogging through weird APIs, batching, retries, and timeouts.

We just launched [native embedding](/docs/embedding), so you can offload this
chore to turbopuffer.

But we are systems engineers. We penny pinch compute, and there is nothing that
bothers us more than idle CPUs (except for maybe idle GPUs). Why stop at
convenience? Moving embeddings into turbopuffer allows us to apply a new set of
whole-system optimizations to embedding that can shave hundreds of milliseconds
off a query. Here's how.

## Before

When embedding is done outside of turbopuffer, a distributed trace of a semantic
search query looks something like this:

```
│search
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
│
│embedding                             
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
│
│                             query
│                             ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

```
│search
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
│
│embedding                             
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
│
│                             query
│                             ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
```

The entire embedding process happens on a different computer, invisible to the
turbopuffer query planner. Worse, embedding is serialized with turbopuffer's
query execution: you cannot score a document vector until you have a query
vector, and the client can't do much of anything while it waits.

If you've worked in systems before, you see a juicy serialization problem, and
you're already thinking about how to overlap and reorder work, if only you had
the flexibility to move that embedding call around.

## After

[Native embedding](/docs/embedding) lets us optimize search by parallelizing
embedding with the initial phase of query execution, before a vector is actually
needed. When the query planner can see embedding, the distributed trace ends up
looking something like this:

```
│search
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
│
│S3 fetch
│▓▓▓▓▓▓▓▓▓
│
│embedding                             
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
│
│                             scan
│                             ▓▓▓▓▓
```

```
│search
│░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
│
│S3 fetch
│▓▓▓▓▓▓▓▓▓
│
│embedding                             
│▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
│
│                             scan
│                             ▓▓▓▓▓
```

We still need a query vector before we can pick clusters and score documents, so
the scan still waits on embedding. But reading namespace metadata from the index
doesn't depend on the vector at all, so it can run while the GPU is busy. This
is a simplified trace, and we're continually finding ways to push the dependency
even further down.

This is already paying dividends for our customers. Linear and Readwise both
rolled out native embedding during beta. Linear
[shaved 150ms](/customers/linear#linear-migrates-to-native-embeddings) off their
embedding pipeline. Readwise reduced their median embedding latency
[by 8x](/customers/readwise#readwise-speeds-up-chat-with-native-embeddings).
We're observing more similar gains now that native embedding is generally
available.

### Tradeoffs

Native embedding makes a good tradeoff for the workload we see most, where every
write and read needs a new embedding. But there are workloads where that's the
wrong tradeoff. For example, if you can reuse a query embedding over time or
across namespaces, don't re-embed with every read. No matter how much we
optimize each individual embedding call, it's still better to avoid a call
entirely. Native embedding gives you the flexibility to move embedding into
turbopuffer only for writes,
[only for queries](/docs/embedding#query-only-native-embeddings), or not at all.
Future versions of turbopuffer will automatically cache repeated calls to embed
the same document and pass the savings on to you.

## Whole-system optimization

When subsystems are optimized in isolation, individual parts can reach local
maxima while the end-to-end system stays suboptimal. Pulling more work into
turbopuffer lets us apply good systems engineering across more of a search
system and get closer to a global maximum. We will [always](/docs/roadmap) give
ample attention to first-stage retrieval, but with more visibility into the
whole system, we have more opportunities to optimize.

Today, turbopuffer parallelizes embeddings during reads and writes. We're
working on database improvements to enable asynchronously re-embedding an entire
namespace in the background (stay tuned). This creates opportunities to optimize
not only for performance, but for relevance; it's a small leap from asynchronous
re-embedding to running evals on new models and automatically migrating to the
highest performer.

Coming soon:
[native reranking](https://x.com/ErikKaum/status/2103169247102812334), better
document parsing and chunking, and
[search agents](/blog/reinforcement-learning-sid-ai). If moving any of these
subsystems into turbopuffer appeals to you, [contact us](/contact).

## turbopuffer

turbopuffer is a fast search engine that hosts 1T+ documents, handles 10M+ writes/s, and serves 25k+ queries/s. We are ready for far more. We hope you'll trust us with your queries.

[Get started](/join)

![turbopuffer logo](/_next/static/media/lockup_transparent.6092c7ef.svg)

[Company](/about)[Pricing](/pricing)[Merch](https://turbopuffer.supply)[Press & media](/press)[System status](https://status.turbopuffer.com)

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