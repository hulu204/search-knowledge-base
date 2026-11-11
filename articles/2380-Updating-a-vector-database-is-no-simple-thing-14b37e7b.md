---
title: 'Updating a vector database is no simple thing'
company: softwaredoug
tag: 召回
date: 2026-08-18
url: https://softwaredoug.com/blog/2026/08/18/update-graph-vector-db.html
account: 
origin: en-rss
---
Let’s talk about the soft spots of vector search. Where might everything fall apart when you put a solution into production?

I’m starting a series on these soft spots. What doesn’t actually get discussed with search engines + vector databases. But what surprises and breaks teams.

Today: **updates**. Writes. What happens when vectors change?

Most public vector search benchmarks look like this:

1. Index a bazillion vectors
2. Search
3. Profit!

Yet indices constantly turnover. Like Thanos, change is inevitable.

A job search engine constantly changes. Old job postings expire after only a few weeks. In social media updates build on top of a larger, never changing corpus.

In this post, I want to look at the most popular vector search algorithm, [Hierarchical Navigable Small Worlds](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world) to see how it fares at updates. As the core data structure behind Elasticsearch, Weaviate, Milvus, QDrant, Vespa, it’s important to appreciate how HNSW does (or doesn’t) handle updates. Particularly, I’ll pick apart how Lucene works to explore themes and challenges in how graph-based vector databases handle updates.

## Getting upsert about graphs

For our purposes, the most important thing to know about HNSW is it holds a graph connecting items to what’s similar to them. That makes it easy to collect nearest neighbors to a search query. For example, below, a query for “Bruce Wayne” over an index of Superheroes. We walk from a starting point closer and closer to what’s similar to “Bruce Wayne”. Eventually collecting Batman and other similar results (superheroes Batman works with).

![](/assets/media/2026/update-vector-db/image1.png)

That’s a powerful idea. You can map what’s nearby to help a searcher navigate the space. It’s a bit like using a street map. You want to go to address “1234 Smith St, Springfield UT”, but your start location “5678 Baker St, Springfield NY”. You know you need to go to Utah, you take a road that moves Southwest. The only difference: here we’re connecting articles, products, job posts, or whatever else and navigating closer and closer to our desired location: a query, not a destination address.

We care about updates though. What happens if Spiderman’s vector changes? In most HNSW implementations, an update becomes an upsert: a delete-then-insertion. We delete its old location, inserting it into a new one.

Doesn’t the delete create gaps in the graph, making it impossible to navigate?

![](/assets/media/2026/update-vector-db/image2.png)

Suddenly you can’t walk the graph and find what’s relevant. Do you in-place repair the graph? Reinsert Spiderman to find it’s new nearest neighbors?

In reality, most vector databases don’t actually change the graph. They just mark it as deleted. That lets us still navigate through it. We know to never return it as actual search results. We know Spiderman doesn’t actually live there.

![](/assets/media/2026/update-vector-db/image3.png)

Many vector databases, like Lucene, hold multiple graphs in memory (Lucene calls these [segments](https://stackoverflow.com/questions/2703432/what-are-segments-in-lucene)). An insert (eventually) becomes part of a brand-new graph built up from recent insertions. The new kids on the block. We see our newly inserted Spiderman inserted here, in a proper location with other newly indexed superheroes:

![](/assets/media/2026/update-vector-db/image4.png)

Unfortunately, it’s not as simple as “add Spiderman and it instantly appears”.

Search systems typically choose to focus on query performance over making inserts instantly searchable. Lucene queues insertions in a write-ahead log: a queue of items to be inserted at some interval (a period of time? after so many insertions? manually?) Eventually all written vectors finally get committed into the graph.

![](/assets/media/2026/update-vector-db/image7.png)

Depending on how frequently you require the data to be searchable, you’ll have dramatically different performance characteristics. In a bit of benchmarking of a small index of 48K docs, under write load, it’s not atypical to see statistics like this:

| Commit Every | Query Latency |
| --- | --- |
| 1000 vectors | 0.063665s |
| 50,000 vectors | 0.001764s |

Once created, this new graph, along with the one above with Spiderman removed, will now be searched in parallel. Instead of searching one graph, we search N graphs over N segments.

Eventually if the graphs live long enough, they’ll get merged / rebuilt into a single large graph:

![](/assets/media/2026/update-vector-db/image5.png)

This walk through biases towards Lucene. But you’ll find similar themes in QDrant, Milvus, and other mainstream vector databases. Like other vector DB soft spots, don’t assume it’ll just work for you. All these systems make engineering tradeoffs to try to solve for updating a graph. Learn about them. They matter.

The notable exceptions to the themes above include:

* Vespa: they actually seem to maintain a single graph! They’ve worked on the underlying problems of concurrently updating and querying a single logical graph.
* Weaviate: while Weaviate tombstones deletes, they don’t maintain parallel segments of their graphs. They maintain a single graph.
* Many databases QDrant, Milvus, etc have a mutable, searchable non-graph data structure for new inserts distinct from immutable, longer-lived read-optimized graphs

## Optimizing for a different benchmark regime.

The upsert logic I’ve described seems like an afterthought.

HNSW feels built for the classic benchmark regime: Index everything up front. Map neighbors in a graph. Then search a beautiful, frozen-in-amber representation of the vector space. Solve pesky problems like updates later. It feels designed from first principles for recall and latency, not recall+latency+write performance.

I often wonder if algorithms like HNSW become popular because they’re actually good from first principles, or just an accident of history: benchmaxxxing [ANN Benchmarks](https://ann-benchmarks.com/).

We might ask whether a different strategy would be more resilient to updates? For example, another family of algorithms use clustering. They map vectors to a nearby k-means centroid. Because the centroid was trained using k-means, the DB remains sensitive to the distribution of the data. Unlike graphs though, clustering approaches don’t literally create a map between every indexed document and their neighbors. We don’t know that Batman connects to Superman and Wonder Woman - instead we just know they’re all roughly in the cluster of “DC Superheroes”. That might lead to losing query precision for faster writes.

The important thing, though, isn’t how the algorithm. It’s what YOU should do in your situation.

Every implementation of HNSW involves tradeoffs. For example Vespa chooses to incur the complexity of concurrently updating a graph. Lucene mirrors assumptions of a tunable garbage collector. It gradually merges long-lived documents into a single graph that isn’t expect to change much. It’s assumed, like our combined graph above, that vectors will graduate to the oldest generation of graphs.

## What should YOU do when benchmarking a vector database?

Always be in a position you can [shadow-test](https://microsoft.github.io/code-with-engineering-playbook/automated-testing/shadow-testing/) against a slice of live production traffic. If you’re going to make decisions, don’t trust small benchmarks. Never just insert data and replay thousands of queries. You need to replicate your actual write traffic.

Stand up a cluster of the vector database you’re considering. Send indexing + query traffic to it. Monitor. Tune. See if it can stand up to your production workloads.

Even better: get to know the team building your vector database. Ben Trent once sat with me on a call to help diagnose Elasticsearch vector search bugs (in this case another soft spot: filtered vector search). Get to know your vendor. Don’t be shy. Participate in the community for that technology. Learn its strengths and weaknesses.

Be an informed, active buyer. Not a passive consumer banking on hope.

---

### Learn to Build Agents + Retrieval from Scratch

 [![Build Production-Ready AI Agents for the Enterprise course](/assets/media/2026/build-enterprise-agents/prod-ready-from-scratch.png)](https://maven.com/softwaredoug/build-enterprise-agents) 

Take a course from Doug and AI educator Hugo Bowne-Anderson as they build an agent + retrieval from scratch! [Sign up!](https://maven.com/softwaredoug/build-enterprise-agents)

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---