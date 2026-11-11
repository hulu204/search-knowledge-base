---
title: 'Why Elasticsearch is becoming a columnar database'
company: Elastic
tag: 工程相关
date: 2026-07-09
url: https://www.elastic.co/search-labs/blog/elasticsearch-columnar-storage
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Why Elasticsearch is becoming a columnar database

Elasticsearch is becoming a first-class columnar database. Columnar Mode ships in 9.5, storing data once alongside the existing modes and cutting storage footprints while speeding up analytical queries.

July 09, 2026

[Yannis Roussos](/search-labs/author/yannis-roussos)

[Inside Elastic](/search-labs/blog/category/inside-elastic)[Analytics](/search-labs/blog/category/analytics)[Columnar](/search-labs/blog/category/columnar)

Jump to

Share

Elasticsearch is becoming a first-class columnar database. In 9.5, we’re introducing **Columnar Mode**, a new index mode that stores data once, in columnar form, with no redundant copies and no indexes the workload doesn't need.

Columnar Mode targets the workloads where data is written in volume, queried analytically, and retained for a long time: logs and observability, security telemetry, metrics and traces, business analytics on operational data, and AI retrieval at scale. For these workloads, it means **meaningfully smaller storage footprints** on day one, and the foundation for faster ingest, faster analytical queries, and longer retention as the surrounding work matures.

Columnar Mode ships **alongside** the existing modes, not in place of them. There are no changes to APIs, dashboards, applications, or downstream integrations. It's a new index mode that you can adopt where it helps, on the data where it fits.

The result is that Elasticsearch becomes a **world-class search engine and columnar analytics engine**, on the same data, in the same cluster, under the same operational umbrella. This is how Elastic stays the most useful place to put operational data as the economics of that data are rewritten by columnar architectures.

The rest of this post explains why we're doing it, along with what it changes and what it doesn't.

## Why Elasticsearch is adding a columnar mode

Almost every general-purpose data system worth caring about has, over the last 15 years, made the same architectural decision: When the job is to read, aggregate, and reason over large volumes of data, you organize that data **by column**, not by row or document.

Elasticsearch is now making that decision, too

In addition to its document model, search heritage, and place at the heart of observability, security, and search applications across the industry, it’s now adding a second way to think about data inside the same platform. We're calling it **Columnar Mode**. It positions Elasticsearch to be the only major platform that does **search**, **retrieval**, and **analytics** at the same level, on the same data, with one operational story.

To get there we need to point out three things: One, how Elasticsearch came to be what it is today and why the document model was the right call. Two, how the rest of the data world, in parallel, converged on a completely different shape and why that movement has been so successful. And three, why these two worlds are now converging inside our users' systems and why putting columnar inside Elasticsearch is the right answer.

## How Elasticsearch became a document database (and why that was the right call)

To understand where we're going, you have to understand where we started.

Sixteen years ago, when Elastic’s founder Shay Banon wrote the first version of Elasticsearch, the data world was in the middle of a quiet revolution. JSON was eating the wire. Web applications were sending and receiving data not as carefully typed rows in clearly defined tables, but as flexible, semi-structured documents (a customer order, a chat message, a product listing, a log line, a recipe), each a self-contained little world of fields, sub-fields, arrays, and nested objects.

The relational databases of the time were built around a very different assumption. Define a strict schema up front. Decompose your data into normalized tables. Use joins at query time to reassemble it. This worked beautifully for the use cases it was designed for (transactional systems, banking, enterprise resource planning systems), but it created enormous friction for the new generation of web and mobile applications. Adding a field meant a migration, and storing variable-shaped data meant either a brittle schema or a tangle of nullable columns.

In response, a new category of system emerged: document databases. The bet was simple. Take the data as it arrives, and store it in something close to its native shape. Don't make developers fight the database to express their domain. MongoDB became the flag-bearer for this idea on the operational side, and Elasticsearch carried the same banner on the search side.

For Elasticsearch, the document model was not just a developer-experience choice. It was a deep architectural commitment. The engine was designed around the idea that a record is a document, a document has fields, fields have types, and you should be able to put almost anything in and get useful behavior out (full-text search, structured filtering, sorting, aggregations, ranking) without having to model your data perfectly in advance.

This is what we mean when we talk about Elasticsearch's "document behavior":

* The engine remembers what you sent it. The original record is stored and can always be returned exactly as it was.
* Every field is, by default, made queryable in multiple ways: optimized for fast exact lookups, fast text search, fast range queries, fast sorting, and fast grouping.
* Schemas are flexible. New fields are absorbed at write time. The cost of getting your data model "wrong" is low.
* The unit of work is the document. Indexing, retrieval, and most APIs are framed in terms of "given a document, do X" or "given a query, return documents."

This is a model born from search. Apache Lucene, the storage library Elasticsearch is built on, was designed to make one workload remarkably fast: Take a query, find the small number of documents that match it, rank them by relevance, and return them. To do that well, you build **inverted indexes**: structures that turn the question around, so instead of asking "What's in this document?" you can ask "Which documents contain this term?" and get an answer in milliseconds. You also keep the original document around, because once you've found it, you usually want to show it or retrieve more information from it.

For the workloads Elasticsearch grew up serving (site search, log search, application search, security event lookup, "find this in a haystack") this was, and still is, the right shape. There's a reason Elasticsearch is used in production at hundreds of thousands of organizations worldwide.

But the document model has a built-in cost, and that cost is the starting point for everything that follows.

To keep its promise of fast search, flexible schemas, and faithful storage of the original record, the engine ends up storing data multiple times, in multiple shapes, each optimized for a different question. The original document is stored, and the text in each field is indexed for search. The values in each field are also stored separately, in a per-field columnar store known as *doc values*, so that they can be aggregated, sorted, and grouped. The system maintains all of these in parallel, by default, on every field, because at write time it doesn't know which of these capabilities you'll need at read time.

For the kinds of datasets Elasticsearch was originally designed for (relatively rich, relatively low-volume documents where every read is valuable), this trade-off is excellent. You pay a modest storage and ingestion tax for an enormous capability surface.

For the kinds of datasets Elasticsearch increasingly stores today (billions of log lines, trillions of metric points, oceans of telemetry, most of it written once and read rarely), that trade-off starts to look very different.

That’s the friction we’re setting out to resolve.

## The other story: How the data world went columnar

While Elasticsearch was perfecting the document model, a parallel revolution was happening in analytics. It started in academia, became commercial, and is now the default architecture for almost every system built to read and reason over large datasets. To position Columnar Mode clearly, we have to tell that story.

The bet behind columnar storage is so simple it almost sounds like a trick. Instead of storing your data *row by row* (record one, record two, record three…), store it *column by column* (all values of `timestamp`, then all values of `host_name`, then all values of `status_code`…).

That single decision changes everything.

It started in the early 1990s, with research systems like MonetDB out of the Centrum Wiskunde & Informatica in Amsterdam. It was sharpened in the mid-2000s with C-Store, a project led by Michael Stonebraker at MIT, which became the basis for Vertica. Sybase IQ carried the same idea into the early commercial market. By the early 2010s, every serious analytics vendor on earth had a columnar story. Today, the lineage runs through Amazon Redshift, Google BigQuery**,** and Snowflake in the cloud warehouse world; through open file formats, like Apache Parquet and Apache ORC that have become the lingua franca of the data lake; through in-memory standards like Apache Arrow; and through fast operational columnar engines, like ClickHouse and DuckDB.

Why has this approach won so completely?

Because when your job is to read and reason about a lot of data, columnar storage turns nearly every dimension of cost and performance in your favor.

**You only read what you need.** Real analytical queries almost never want every field; they want three fields out of 50, or aggregate one field out of 200. A row-shaped store has to walk past all the other fields on the way to the ones you care about. A columnar store reads only the columns the query touched. On wide datasets, this routinely cuts the I/O of a query by 90% or more.

**You compress dramatically better.** When you put all the values of one field next to each other, those values are, by definition, of the same type, often with repetition and similar structure; for example, a column of timestamps from the same hour, a column of status codes that are almost always 200, or a column of hostnames drawn from a small set. Compression algorithms thrive on this kind of homogeneity. Where row-shaped stores typically achieve 1.5–3x compression, columnar systems routinely achieve 5–10x, while on low-cardinality fields, it's common to see 20–30x. That’s not just a tuning improvement; that’s a different economic regime.

**You can skip vast amounts of data without reading it.** Because data is organized in blocks of values from the same column, the engine can carry tiny pieces of metadata for each block (minimum, maximum, count, distinct values) and use them to prune entire blocks at query time. Looking for errors in the last hour? Skip every block whose timestamp range is older. Looking for a specific hostname? Skip every block where it doesn't appear. The system avoids work it doesn't need to do by knowing in advance that the work is pointless.

**You can fully leverage the power of modern CPUs.** Modern processors are designed to operate on long, regular, predictable arrays of values; that's where the cache, pipeline, and vector units do their best work. A column is exactly such an array. Columnar engines run queries by passing batches of values through tight, vectorized operators, instead of looking up one record at a time. The speed gains aren’t incremental: Across academic benchmarks reaching back to Abadi et al.'s seminal *Column-Stores vs. Row-Stores* (SIGMOD 2008) and the comprehensive surveys that followed, columnar engines have consistently shown one to three orders of magnitude advantage over row-shaped systems on analytical workloads.

**You delay materializing the original record for as long as possible.** Because the data is already organized by what queries actually do (read this column, filter on that column, aggregate this column), there's no need to reconstruct a full row until you absolutely have to. Most of the time, you don't have to at all, especially if you run analytical queries that only care about aggregating a few columns.

The cumulative effect of these properties is the reason every cloud data warehouse is columnar and why every modern data lake stores its files in Parquet or ORC. It’s also the reason new operational analytics engines have, almost without exception, chosen this shape. It’s the structural answer to the question "How do you make queries over large data cheap and fast?" and the answer turns out to be the same almost everywhere.

We should also note what columnar systems give up. They aren’t designed for "Give me one specific record and update it in place" or for transactional consistency at the level of individual rows. In general, they aren’t designed to do full-text relevance ranking the way a search engine does. They’re optimized for a different shape of workload, and that's the point. Different workloads, different defaults.

For a long time, the world worked because users could pick one tool for one workload and another tool for the other. That world is ending.

## Why search and analytics are now converging

Three things have happened in the last five years that change the calculus.

**First, the volume of data users generate has exploded.** Driven by microservices, containers, OpenTelemetry, AI workloads, and security telemetry, industry estimates put observability and log data ingest at large enterprises in the multiple-terabytes-per-day range, with annual growth rates that have run well into triple digits for several years.

**Second, the cost of storing and querying that data has become a top-line concern.** Industry surveys and practitioner reports consistently flag observability and telemetry as one of the largest and fastest-growing line items in modern infrastructure budgets, and a meaningful share of that spend goes toward data that’s written, retained, and then never queried.

These first two pressures have already produced their answer in the market: Modern columnar systems built for analytics (most visibly ClickHouse on web logs and the cloud warehouses on broader analytics) have redefined what users expect to pay per terabyte stored and per query run. Elasticsearch is now meeting that bar without giving up what makes it Elasticsearch.

**Third, the boundary between search workloads and analytical workloads has dissolved.** Virtually every modern operational use case wants both: find me this specific event, and then aggregate everything around it; show me this log line, and then chart the trend that produced it; retrieve this document, and then group what else matches.

The users who put their logs, metrics, traces, security events, and search corpus into Elasticsearch aren’t asking us to be only a search engine or only an analytics engine. They’re asking us to be one engine that does both, on the same data, with one operational story, at the cost basis they expect from a modern columnar system.

That’s a high bar, and meeting it requires us to change something fundamental about how Elasticsearch organizes data.

For a long time, Elasticsearch has had columnar storage *underneath*. We’ve stored per-column data in our engine since 2013, but we’ve always treated it as a secondary structure layered on top of a document model. That made sense when the document model was the source of truth and the columnar layer was an optimization. It makes less sense when, for an enormous and growing share of our users' data, the columnar shape *is* the source of truth and the document model is the optimization most don’t need.

This is what Columnar Mode is for.

## Columnar Mode: Elasticsearch with a second way of thinking about data

The decision we’re making is deliberately conservative in its surface area and ambitious in its impact.

We aren’t building a new product, asking users to migrate, or changing the API, the query language, the management surface, the integrations, the visualization layer, or anything else that touches their operational reality. Elasticsearch is still Elasticsearch.

What we are doing is introducing a new mode that users can apply, index by index, that turns Elasticsearch into a first-class columnar system for the data where that's the right shape.

In Columnar Mode, the engine flips its defaults:

* **Data is stored once, in our columnar store (doc values).** No parallel copy of the original document and no secondary structures built by default. Each field is responsible for its own storage, and the engine doesn't pay for capabilities the workload doesn't need.
* **Search indexes are built only where they earn their keep.** The message field of a log is still indexed by default to enable free-text search. A numeric field used only in aggregations means no index, extra storage, or additional write-time cost. The engine becomes leaner by default and lets you opt in to capability where it's worth paying for.
* **The original record can be regenerated on demand** from the column store, instead of being kept as a redundant copy. Users who want to keep the stored copy for query convenience can; and users operating at petabyte scale can opt to drop it entirely for further storage savings.
* **The data model is genuinely columnar.** Fields are flat key/value pairs, not nested object trees. Multi-valued fields, cardinality, and nullability are first-class mapping concepts, the same primitives that make pure columnar systems efficient.
* **Specialized profiles ship on top.** The first one is **Columnar Logs**, a logs-oriented variant of the mode with indexing enabled on log messages and the right defaults for time-ordered data. We’ll follow with profiles for other workloads, including, eventually, a columnar profile for vector retrieval, using the same building blocks.

All of this is new for Elasticsearch though not conceptually new in the industry.

The reason this matters is that we’re doing this **without leaving anything behind**. The same query that runs against a Columnar Mode index runs, unchanged, against a document-mode index. Plus, the same dashboards, agents and integrations, Service Level Objectives (SLOs), alerts, rules, and machine learning jobs work as usual. Users who want the document behavior can always keep it on the indexes where it makes sense. Users who want columnar efficiency on the indexes where *that* makes sense (typically, the largest indexes in their cluster) get it.

This is the difference between us and a pure columnar engine. A pure columnar engine does one of these jobs and asks you to bring another system for the other. Elasticsearch is one platform that does both.

## What Columnar Mode is for

Columnar Mode is built for workloads where data is written in volume, queried analytically, and retained for a long time, rather than a universal default. These work categories include:

**Logs and observability at scale.** Users running tens or hundreds of terabytes of logs per day spend most of their observability budget on storage and on the aggregation queries that power dashboards, SLOs, and rate calculations. Columnar Logs is the first specialized profile precisely because this is where the impact lands hardest. At petabyte scale, Columnar Mode changes what is economically possible, that is, longer retention, more raw fidelity, and fewer compromises forced by cost.

**Security event stores and threat hunting.** Security telemetry has the same shape as logs, but with a heavier emphasis on faceted exploration, ad hoc correlation, and deep historical lookups for indicators of compromise. Columnar Mode keeps full-fidelity storage affordable while preserving the search-relevance behavior security analysts need for lookup and pivoting, using the same engine to handle both jobs.

**Metrics, traces, and the unified observability substrate.** Time-series data is already columnar in TSDB, Elasticsearch’s time series database. A future columnar profile will share the same storage building blocks across logs, metrics, and traces, letting all three sit in one engine on the same substrate without any of them compromising on workload-specific behavior. The unified observability platform becomes economically practical, not just architecturally elegant.

**Operational and business analytics on application data.** Beyond observability, this means dashboards over millions of orders, transactions, user events, and Internet of Things (IoT) readings. Many of the workloads that have historically pushed users to ship the same data into a separate analytical warehouse, purely to make the queries affordable, can, with Columnar Mode, stay where the data already is.

**AI retrieval at scale.** Vector workloads are inherently columnar. A future columnar profile for vector retrieval will combine the dense storage efficiency of the general mode with the indexing structures retrieval needs, putting retrieval augmented generation (RAG) and semantic-search workloads on the same cost basis as every other shape of data in the cluster.

The thread running through all of these is that Columnar Mode is the right answer when data is append-mostly, queries are analytical, and access patterns are per-column. For the workloads where those conditions don't hold, like search-first applications where the document is the unit of value, transactional flows that update individual records, or anything that depends on rich document structure as user-facing semantics, the document-oriented modes remain the right default, and they’ll continue to be invested in.

From the start, the principle has been that different workloads require different defaults, and Columnar Mode is what makes that real.

## What changes for Elasticsearch users with Columnar Mode?

For Elasticsearch users, here’s what changes:

* **Costs go down meaningfully.** Columnar Mode only builds inverted indexes where they earn their keep and stops storing data multiple times on every field. The result is a smaller storage footprint for the same workloads. Users can choose between two shapes of the mode: Columnar Logs keeps an inverted index on the message field, where the bulk of log queries actually look; the pure Columnar Mode variant drops that default entirely on string-type fields. A follow-up technical deep dive will publish the benchmarks and exact storage savings. The savings compound at scale and show up in operational reality immediately on self-managed clusters in the disks and machines the cluster no longer needs, and on Elastic Cloud in the bill.
* **The architecture pays off on reads and writes, too.** The same choices that make Columnar Mode storage-efficient (data stored once, indexes only where they earn their keep, and vectorized execution over columns) are the ones that shape its behavior on the read and write path, as well. The workloads that benefit most are the ones that dominate observability, security, business intelligence, and AI retrieval.
* **The model gets simpler.** Columnar Mode is opinionated by default. The right behavior for analytical workloads is what you get out of the box, like what we’ve done for metrics with TSDB, but for all types of data. The configuration surface contracts in places it should have contracted years ago.
* **The path is nondisruptive.** Users can adopt Columnar Mode index by index. The cluster, applications built on top of Elasticsearch, and dashboards don't change. The model is additive: a new way of behaving that’s available where it helps, alongside the behavior they already trust.

The result is an Elasticsearch that’s leaner and faster, with no changes where it has been working all along.

## What doesn't change when you turn on Columnar Mode

* **The document-oriented modes aren’t deprecated.** Every existing mode remains available, supported, and invested in. Users who depend on document behavior (typical search applications, application search, security workflows, and anything where the original record's structure is the point) keep that behavior.
* **Existing modes get faster, not slower.** The work behind Columnar Mode is, at its core, work on doc values, Elasticsearch's columnar store, which every mode uses under the hood. Compression, encoding, query-execution, and vectorization improvements that ship with Columnar Mode benefit document-mode indexes alongside columnar ones for fields that reside on doc values. LogsDB, TSDB, and standard indexes get meaningfully faster analytical queries as a side effect of this work, with no user action or migration required. Investing in Columnar Mode is investing in every mode.
* **The APIs don’t change.** Every interface a user or partner integrates with (the REST APIs, query languages, management UI, data collection agents, integrations, and SDKs) keeps working exactly as it does today. Columnar Mode is an index setting, not a fork in the product, and downstream components don’t need to learn anything new.
* **Search relevance, vector search, and semantic retrieval aren’t affected.** These remain first-class capabilities of the engine, and they benefit from many of the same query and indexing performance investments that Columnar Mode rides on.
* **There’s no migration cliff.** Existing indexes keep working, and new indexes can be created in whichever mode fits their workload. Users move at the pace that makes sense for their organization.
* **Elastic Cloud Serverless gets columnar the same way.** On Serverless, where users manage projects rather than indices, Columnar Mode becomes part of the project type configuration. Observability and log-heavy project types will move to columnar defaults as the mode matures, with no user-facing change in how projects are created or managed.

This matters because the temptation, when a company makes a big architectural bet, is to oversell it as the new gospel and undersell the engine's existing strengths. We don't have to make that trade. Elasticsearch's existing modes aren't legacy; they’re a mature, production-hardened document-oriented search engine that has been refined by more than a decade of use at scale. Columnar Mode is what they've been missing for the workloads they were never designed for.

## Why columnar storage matters for the future of Elasticsearch

For most of the last decade, the dominant pattern has been fragmentation; for example, a search engine for search, a warehouse for analytics, a time-series database for metrics. This also includes a log aggregator for logs, a vector database for AI retrieval, and a graph database for relationships. Each one has its own ingestion pipeline, query language, operational story, and bill. The complexity tax this imposes on users is enormous, and the spend it generates for the industry is even larger.

The pattern that’s starting to replace it is *convergence*, the realization that the right architecture for a modern data engine is one that takes data once, stores it efficiently, and exposes it to whatever workload the application happens to need, whether that’s search, retrieval, aggregation, ranking, or vector similarity. That convergence is the most important trend in the data infrastructure industry, and it’s the trend on which Elasticsearch's future depends.

Columnar Mode is our central move in that direction, along with the work happening alongside it on indexing throughput, Elasticsearch Query Language (ES|QL, Elasticsearch’s analytical query language), vector retrieval, and observability and security as integrated solutions. It’s the architectural decision that unlocks the others, because without a first-class columnar layer, Elasticsearch's economics simply don’t compete on the workloads where convergence is most valuable.

With Columnar Mode, Elasticsearch becomes the only major platform in the industry that can credibly be **the best search engine you can run** and **a competitive columnar analytics engine** on the same data, in the same cluster, under the same operational umbrella. Although there will always be a specialized system that wins a specialized benchmark for individual workloads, Elasticsearch is where operational data belongs when it spans more than one shape and workload.

That’s the bet, and we’re confident it’s the right one.

## The bottom line on Elasticsearch as a columnar database

Sixteen years ago, the right call for a search engine was to behave like a document store. We made that call and built one of the most widely used data platforms in the industry.

Today, the right call for the next decade of operational data (observability, security, AI retrieval, application search, business analytics) is to give that same engine a columnar way of thinking as a first-class mode users can choose, on the data where it fits, without giving up any of the things they already rely on us for.

That’s what Columnar Mode is. It’s the most important architectural change we’ll make to Elasticsearch this decade, and it’s the move that makes Elasticsearch the engine our users will still be reaching for when their current tool of choice has been displaced.

We’re going columnar. The reasoning is sound, and the path is nondisruptive. Columnar Mode reaches technical preview in Elasticsearch 9.5 and general availability (GA) in Elasticsearch 9.6, and every product team at Elastic is building on top of this foundation. We aren’t waiting for the future of data systems to arrive; we’re building it.

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