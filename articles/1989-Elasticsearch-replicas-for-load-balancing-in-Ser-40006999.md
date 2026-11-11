---
title: 'Elasticsearch replicas for load balancing in Serverless'
company: Elastic
tag: 工程相关
date: 2026-03-24
url: https://www.elastic.co/search-labs/blog/elasticsearch-replicas-load-balancing-serverless
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch replicas for load balancing in Serverless

Learn how Elastic Cloud Serverless automatically adjusts index replicas based on search load, ensuring optimal query performance without manual configuration.

March 24, 2026

[Andrei Dan](/search-labs/author/andrei-dan)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

In Elastic Cloud Serverless, we automatically adjust the number of replicas for your indices based on search load, ensuring optimal query performance without any manual configuration. In this blog, we’ll explain how replicas are scaled, when the system adds or removes them, and what this means for your indices.

## The party is getting crowded

You're hosting a pizza party. You've got a few friends helping you serve, each stationed at different spots around the room. You give each friend a pizza, and they start handing out slices to hungry guests as they arrive.

At first, things run smoothly. A few guests trickle in, your friends serve slices, everyone's happy. But then word spreads about your sourdough pizzas. The doorbell keeps ringing. Guests pour in. Soon, there's a crowd forming around one of your friends, the one holding the pepperoni pizza, which everyone seems to want.

Your friend with the pepperoni pizza is overwhelmed. Guests are waiting, getting impatient, and a large queue has formed. Meanwhile, your friend holding the margherita pizza is standing around with barely anyone asking for a slice.

What do you do?

You order a couple more pepperoni pizzas and hand them to other friends. Now three friends are holding pepperoni instead of one. The crowd spreads out, and suddenly you can serve three times as many guests at once.

A few things become clear as you host more parties:

* **Not all pizzas are equally popular.** Some are in high demand, others have fewer takers. You don't need extra "copies" of the unpopular ones. You need extras of the ones with queues.
* **Order more pizzas before the queue gets too long.** If you wait until your friend is completely overwhelmed and guests are leaving angry, you've waited too long. Better to get an extra pizza when you see a crowd forming.
* **Don't throw away pizzas too quickly.** Just because the crowd around the pepperoni thinned out for five minutes doesn't mean the rush is over. Maybe they're just refilling drinks, or even talking among themselves (is that still a thing?). Keep the extra pizzas ready. If the lull continues for a while, then you can put them away.
* **You can only hand out as many pizzas as you have friends who are helping.** If you've only got four friends helping, ten pizzas won’t change the outcome. Only four can be served at once. Match your pizza count to your available hands.
* **When a friend leaves, take their pizza.** If one of your friends needs to head out, grab their pizza immediately. You can't have pizzas sitting unattended. Hand it to someone else, or put it away.

## From pizzas to replicas

Let's map this back to Elasticsearch.

In our analogy, pizzas are replicas (copies of your index shards), your friends helping serve are search nodes, hungry guests are search queries, and that popular pizza with a crowd around it is a hot index with high search load.

When search traffic increases on a particular index, we create additional replicas and distribute them across your search nodes. Any replica can serve any query for that index, just like any friend holding pepperoni can hand out pepperoni slices. More replicas means higher throughput: Three replicas can handle three times the queries per second of a single replica.

## Measuring the hunger

Before we decide how many pizzas to order, we need to know how hungry the crowd is.

Elasticsearch tracks the **search load** for every shard. It's a metric that captures how much search activity a shard is handling. We aggregate this across all shards of an index to understand the total search demand.

What matters most is the **relative search load**: What proportion of your project's total search traffic is hitting each index? If one index is receiving 60% of all searches while another gets 5%, we know where to add capacity.

## The math behind the pizzas

We calculate the optimal number of replicas following this formula:

```
desired_replicas = min(ceil(L × N / (S × X)), N)
```

Where:

* **L** = the index's relative search load (between 0 and 1).
* **N** = the number of desired search nodes in your project.
* **S** = the number of shards in the index.
* **X** = a threshold to avoid hot spots (default: 0.5).

An example: four search nodes, one index with two primary shards receiving 80% of search traffic:

```
desired_replicas = min(ceil(0.8 × 4 / (2 × 0.5)), 4)
                 = min(4, 4)
                 = 4
```

This hot index gets four replicas distributed across the search nodes.

The threshold X (defaulting to 0.5) is important. We don't wait until a replica is completely overwhelmed; we scale up when it's at half capacity. Hand out the extra pizza when you see the crowd forming, not when guests are already leaving.

## Scale up fast, scale down slow

When search load increases, we add replicas immediately. No reason to make users wait.

When search load drops, we wait a bit before taking any action. We need to see consistent low demand for about 30 minutes before reducing replicas. (This is to deal with spiky traffic where a quiet moment doesn't mean the party is over.)

This matters because adding a replica has a cost. The new replica copies data and warms its caches before serving queries efficiently. Removing replicas too eagerly means constantly paying this startup cost as traffic naturally fluctuates.

## Respecting topology bounds

Replicas can never exceed the number of search nodes. Having more replicas than nodes provides no benefit (you can only serve as many pizzas as you have friends who are helping to serve slices).

When nodes are removed from your project, we reduce replicas immediately to match. No waiting for the cooldown, as you can't have unassigned replicas. The moment a friend leaves, we remove their pizza.

## The bigger Serverless picture

Replicas for search load balancing works alongside other autoscaling systems:

* **Search autoscaling** adjusts the number of search nodes (how many friends are helping).
* **Replicas for search load balancing** distribute traffic by adjusting replica counts per index (how many pizzas of each kind we need).
* **Data stream autosharding** optimizes shard counts for writes (how to slice each pizza, covered in the [previous post](https://www.elastic.co/search-labs/blog/datastream-autosharding-serverless)).

An important design principle: Replicas for load balancing don't directly trigger search autoscaling. Instead, by distributing search requests across more replicas, it enables increasing resource utilization across your search nodes. This higher utilization then triggers our existing autoscaling logic to add capacity if needed. Replicas for load balancing enables autoscaling to do its job, making sure your search nodes are actually being used, rather than having all traffic bottlenecked on a single replica while other nodes sit idle.

## What this means for you

You don't need to predict which indices will be popular. You don't need to manually adjust replicas when traffic patterns change. You don't need to wake up at 3 a.m. because a surge overwhelmed your busiest index.

The system watches where queues are forming and orders more pizzas for those spots. Cold indices don't waste resources on unnecessary replicas. Hot indices get the capacity they need. Your budget goes where it matters.

## Conclusion

In the [autosharding post](https://www.elastic.co/search-labs/blog/datastream-autosharding-serverless), we made sure your pizzas are sliced right. Now, with replicas for search load balancing, we make sure you have enough pizzas, in the right hands, when the hungry crowds arrive.

Try [Elastic Cloud Serverless](https://www.elastic.co/cloud/serverless) and let us handle the pizza logistics.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### How we optimized refresh costs in Elasticsearch Serverless

July 31, 2024|[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltb2cd04a86700d5c2/6a17d715e3179138882d567d/016f5f2a90974dd53416d7d12f8776e802a0eef8-1440x823.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Ingest autoscaling in Elasticsearch

July 29, 2024|[Pooya Salehi](/search-labs/author/pooya-salehi)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt84da396c370b06ec/6a170cfa6234e00dd3db1a55/d92e2e9fbae1dca1f18e623b2f5eb2a835307130-1600x1066.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Autosharding of data streams in Elasticsearch Serverless

December 10, 2024|[Andrei Dan](/search-labs/author/andrei-dan)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9f3d645218a14c98/6a170a25acf088f13cbe9ae5/d4a79be6eabad0a7452768bd16d04fcd75056e64-1280x853.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elastic Cloud Serverless: A deep dive into autoscaling and performance stress testing at scale

December 02, 2024|[David Brimley](/search-labs/author/david-brimley)|[+3](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter