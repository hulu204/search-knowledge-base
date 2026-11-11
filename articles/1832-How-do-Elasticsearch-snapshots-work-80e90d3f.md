---
title: 'How do Elasticsearch snapshots work?'
company: Elastic
tag: 工程相关
date: 2023-11-16
url: https://www.elastic.co/search-labs/blog/how-do-incremental-snapshots-work
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How do Elasticsearch snapshots work?

During our instructor-led “Elasticsearch Engineer” training, one of the most common questions we get while teaching about snapshots is “what is the incremental nature of snapshots?” This blog post will cover that topic in detail.

November 16, 2023

[Lutf ur Rehman](/search-labs/author/lutf-ur-rehman)

[Basics](/search-labs/blog/category/basics)

Jump to

Share

Elastic offers many instructor-led, in-person and virtual live trainings, as well as [on-demand trainings](https://www.elastic.co/training/). Our flagship courses are Elasticsearch Engineer, Data Analysis with Kibana, and Elastic Observability Engineer. All of these courses lead to [certifications](https://www.elastic.co/training/certification).

We recently released the latest version of [Elasticsearch Engineer](https://www.elastic.co/training/elasticsearch-engineer) training in response to increased demand and new features. This course is designed for both new Elasticsearch users and Elasticsearch professionals. It begins with the basics for getting started with the Elastic Stack, then quickly dives deep into topics ranging from optimizing search performance to building efficient clusters. View the [detailed course outline](https://www.elastic.co/pdf/elastic-elasticsearch-engineer.pdf) to find out more about what you’ll learn. All lessons include hands-on labs.

During this instructor-led “Elasticsearch Engineer” training, one of the most common questions we get while teaching about snapshots is “how each snapshot is logically independent?” In this blog post, I will explain this in detail.

## What is a snapshot?

A [snapshot](https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshot-restore.html) is a backup of a running Elasticsearch cluster. You can use snapshots to:

* Regularly back up a cluster with no downtime
* [Recover](https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshots-restore-snapshot.html) data after deletion or a hardware failure
* Transfer data between clusters
* Reduce your storage costs by using [searchable snapshots](https://www.elastic.co/guide/en/elasticsearch/reference/current/searchable-snapshots.html) in the hot, cold and frozen data tiers

## Deduplication of snapshots

To back up an index, a snapshot makes a copy of the index’s [segments](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html) and stores them in the snapshot repository.

Indices are made up of shards. Each Elasticsearch shard is a Lucene index. Each Lucene index is divided into smaller units called segments. When you add new documents to your index, Lucene creates a new segment and writes to it. From time to time, Lucene merges smaller segments into a larger one.

Since segments are immutable, the snapshot only needs to copy any new segments created since the repository’s last snapshot.

Each snapshot is also logically independent. When you delete a snapshot, Elasticsearch only deletes the segments used exclusively by that snapshot. Elasticsearch doesn’t delete segments that are still used by other snapshots in the repository.

Let’s go through this example to get a better understanding.

* Suppose we take a snapshot (snap1) of a simple index with one shard and two segments.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt75604d9bd65f0175/6a1704f70c485747c601a95b/6204214efdb08e39a8cf8501b9ddc7ab48273820-1440x603.png)

* Some time later as new documents are indexed, a new segment C gets creates in shard0.
* A second snapshot (snap2) will only copy the missing segment(s) to the repository.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2fe6220a30f84a86/6a1704f9839dfa1e78dcfdcc/db0b8d7b6ffb387407f5d93ecca4b9e3c6206300-1440x635.png)

* Some time later, segments A, B, and C are merged, creating a new segment D.
* When creating a new snapshot (snap3), the new segment D is copied to the repository.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1ca6ebc12cc239bd/6a1704fa60084b39853c447d/32894f0063a8ff1382abb308e549e8b80273b756-1440x626.png)

* Deleting a snapshot (snap1) only deletes segments in the repository that are no longer referenced by any other snapshot.
* In this case, no segments are deleted from the repository.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt379d95df551cdd3b/6a1704fcacf088c478be9a0e/72e18dea37a38583ed7bd944ded09f73d2ab715b-1440x674.png)

* Only after deleting snap2, segments A, B, and C will also be deleted from the repository.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9a2f12a5737bde9b/6a1704fdcdacbf71447d290f/0f11f63ebbd19142961909d524d9e89300446c4d-1440x723.png)

## Summary

In this blog post, I explained how snapshots are automatically deduplicated with the help of some graphics. For more information, please feel free to read through the official [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/snapshot-restore.html).

The Elastic Stack is versatile enough to tackle any use case. Want to learn how to harness the power of that versatility? Become an Elastic expert through [free](https://www.elastic.co/training/free), [paid](https://www.elastic.co/training/schedule), [private](https://www.elastic.co/training/private-training), and training [subscriptions](https://www.elastic.co/training/subscriptions). Our instructor-led virtual classes are [offered globally](https://www.elastic.co/training/schedule), in time zones that make learning convenient for you. Enhance your professional visibility and push aside technical boundaries within your company by becoming [Elastic certified](https://www.elastic.co/training/certification).

Reach out to us at [training@elastic.co](mailto:training@elastic.co) with any questions.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt6d8bd040a15da207/6a17e422414c640e67945116/ef9edded97edd7c919e617e648e62016155cde56-720x420.jpg)

[Basics](/search-labs/blog/category/basics)

### Parsing JSON fields in Elasticsearch

October 17, 2025|[Valentin Crettaz](/search-labs/author/valentin-crettaz)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt373f9290a1371dd7/6a17122e0c48579b2001abba/fd87bff40e296ebce871d631c86fd0245f11c796-1440x960.jpg)

[Javascript](/search-labs/blog/category/javascript-programming)[Basics](/search-labs/blog/category/basics)

### Automatically updating your Elasticsearch index using Node.js and an Azure Function App

June 04, 2024|[Jessica Garson](/search-labs/author/jessica-garson)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1a0bf009f00b1c80/6a1711fa4a531b3db636aa9f/c7c174d6408b23fca482664c608f9e8849243d96-1440x720.jpg)

[Basics](/search-labs/blog/category/basics)

### Adding document level security (DLS) to your internal knowledge search

January 22, 2024|[Sean Story](/search-labs/author/sean-story)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d7e4a5bbd9427c2/6a170e4d0e2e4905b641a1b7/04f1738a38cead88c9a67b0f863171b4b43010ab-1600x913.png)

[Basics](/search-labs/blog/category/basics)

### Elasticsearch plugin for UBI: Analyze user data in Kibana

September 26, 2025|[Eduard Martin](/search-labs/author/eduard-martin)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltc31c3bf0d453d846/6a170e12cdacbfdf6a7d2a7e/3ae41b1f2876d2ad11c8e2b79bbf79955d6902aa-1440x840.png)

[Java](/search-labs/blog/category/java-programming)[Basics](/search-labs/blog/category/basics)

### Testing Elasticsearch. It just got simpler.

March 19, 2026|[Piotr Przybyl](/search-labs/author/piotr-przybyl)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter