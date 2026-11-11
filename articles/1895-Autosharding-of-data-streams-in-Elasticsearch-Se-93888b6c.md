---
title: 'Autosharding of data streams in Elasticsearch Serverless'
company: Elastic
tag: 工程相关
date: 2024-12-10
url: https://www.elastic.co/search-labs/blog/datastream-autosharding-serverless
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Autosharding of data streams in Elasticsearch Serverless

In Elastic Cloud Serverless we spare our users from the need to fiddle with sharding by automatically configuring the optimal number of shards for data streams based on the indexing load.

December 10, 2024

[Andrei Dan](/search-labs/author/andrei-dan)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

## How Elastic Cloud Serverless autosharding works

1. **Monitors indexing write load:** Elasticsearch continuously tracks the `write_load` metric, representing the average number of write threads used for indexing. This metric informs sharding decisions.
2. **Calculates optimal shard count:** The system uses a formula that considers the current `write_load`, the minimum and maximum write threads available per node, to determine the ideal number of shards. This balances performance with overhead.
3. **Triggers rollover based on write load:** When the `write_load` necessitates a shard increase, a rollover operation is triggered. This creates a new index in the data stream with the calculated optimal number of shards. Regular rollover conditions (like shard size) also trigger rollovers, potentially leading to shard reduction if the `write_load` is lower.
4. **Applies cooldown periods:** To prevent rapid shard adjustments, cooldown periods are enforced. There's a 4.5-minute wait before increasing shards and a 3-day wait before reducing them.
5. **Autoscaling integration:** Autosharding works in conjunction with autoscaling. By dynamically adjusting shard counts, autosharding enables autoscaling to more effectively increase resources as needed, preventing the system from being constrained at low capacity during high indexing workloads. It also enables autoscaling to more effectively increase resources as needed, preventing the system from being constrained at low capacity during high indexing workloads.

## Background

Traditionally, users change the sharding configuration of data streams in order to deal with various workloads and make the best use of the available resources. In [Elastic Cloud Serverless](https://www.elastic.co/docs/current/serverless) we've introduced autosharding of data streams, enabling them to be managed and scaled automatically based on indexing load.

This post explores the mechanics of autosharding, its benefits, and its implications for users dealing with variable workloads. The autosharding philosophy is to increase the number of shards aggressively and reduce them very conservatively, such that an increase in shards is not followed prematurely by a reduction of shards due to a small period of reduced workload.

## Autosharding of data streams in Serverless Elasticsearch

Imagine you have a large pizza that needs to be shared among your friends at a party. If you cut the pizza into only two slices for a group of six friends, each slice will need to serve multiple people. This will create a bottleneck, where one person hogs a whole slice while others wait, leading to a slow sharing process. Additionally, not everyone can enjoy the pizza at the same time; you can practically hear the sighs from the friends left waiting. If more friends show up unexpectedly, you’ll struggle to feed them with just two slices and find yourself scrambling to reshape those slices on the spot.

On the other hand, if you cut the pizza into 36 tiny slices for those same six friends, managing the sharing becomes tricky. Instead of enjoying the pizza, everyone spends more time figuring out how to grab their tiny portions. If the slices are too small, the pizza might even fall apart.

To ensure everyone enjoys the pizza efficiently, you’d aim to cut it into a number of slices that matches the number of friends. If you have six friends, cutting the pizza into 6 or 12 slices allows everyone to grab a slice without long waits. By finding the right balance in slicing your pizza, you’ll keep the party running smoothly and everyone happy.

You know it’s a good analogy when you immediately follow-up with the explanation; the pizza represents the data, the slices represent the index shards, and the friends are the Elasticsearch nodes in your cluster.

Traditionally, users of Elasticsearch had to anticipate their indexing throughput and manually configure the number of shards for each [data stream](https://www.elastic.co/guide/en/elasticsearch/reference/current/data-streams.html). This approach relied heavily on predictive heuristics and required ongoing adjustments based on workload characteristics whilst also balancing [data storage, search analytics, and application performance](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html).

Businesses with seasonal traffic, like retail, often deal with spikes in data demands, while IoT applications can experience rapid load increases at specific times. Development and testing environments typically run only a few hours a week, making fixed shard configurations inefficient. New applications might struggle to estimate workload needs accurately, leading to potential over- or under-provisioning.

We've introduced autosharding of data streams in [Elastic Cloud Serverless](https://www.elastic.co/docs/current/serverless). Data streams in [Serverless](https://www.elastic.co/docs/current/serverless) are managed and scaled automatically based on indexing load - automatically slicing your pizza as friends arrive to your party or finish eating.

## The promise of autosharding

Autosharding addresses these challenges by automatically adjusting the number of shards in response to the current indexing load. This means that instead of users having to manually tweak configurations, Elasticsearch will dynamically manage shard counts for the data streams in your project based on real-time data traffic.

Elasticsearch keeps track of the indexing load for every index as part of a metric named write load, and exposes it for on-prem and ESS deployments as part of the [index stats API](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-stats.html) under the indexing section.

![Autosharding in Elasticesarch:  indexing load ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbf8a17014280842a/6a170cf55091687333e1bb3e/b83c902ebadc04d7e0e0a794b6b2ec925b0f4cb4-1200x1600.png)

The `write_load` represents the average number of write threads used while indexing documents.

For an index with one shard the maximum possible value of the `write_load` metric is the number of write threads available (e.g. all write threads are busy writing in the same shard).

For indices with multiple shards the maximum possible value for the write load is the number of write threads available in a node times the number of indexing nodes in the project. (e.g. all write threads on all the indexing nodes that host a shard for our index are busy writing in the shards belonging to our index, exclusively)

To get a sense of the values allowed for `write_load` let’s look at index `logs` with one shard running on one Elasticsearch machine with 2 [allocated processors.](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-threadpool.html#node.processors%60) The [write thread pool](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-threadpool.html) will be sized to 2 threads. This means that if this Elasticsearch node is exclusively and constantly writing to the same index `logs`, the `write_load` we’ll report for index `logs` will be **2.0** (i.e. 2 write threads fully utilized for writing into index `logs`).

If `logs` has 2 primary shards and we’re now running on two Elasticsearch nodes, each with 2 [allocated processors](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-threadpool.html#node.processors) we’ll be able to get a maximum reported `write_load` of **4.0** if all write threads on both Elasticsearch nodes are exclusively writing into the `logs` index.

### Serverless autoscaling

We just looked at how the write load capacity doubled when we increased the number of shards and Elasticsearch nodes. [Elastic Cloud Serverless](https://www.elastic.co/docs/current/serverless) takes care automatically of both these operations using data stream autosharding and [ingest autoscaling](https://www.elastic.co/search-labs/blog/elasticsearch-ingest-autoscaling). Autoscaling refers to the process of dynamically adjusting resources - like memory, CPU, and disk - based on current demands.

In our serverless architecture, we start with a small 2GB memory server and use a step-function scaling approach to increase capacity efficiently. We scale up memory incrementally and then scale out by adding servers. This cycle continues, increasing memory per server incrementally up to 64GB while managing the number of servers.

#### Linking autoscaling and autosharding

The connection between auto**scaling** and auto**sharding** is essential for optimizing performance. When calculating the optimal number of shards for a data stream, we consider the minimum and maximum number of available write threads per node in our scaling setup.

* For small projects, the system will move from 1 to 2 shards when the data stream uses more than half the capacity of a node (i.e., more than one indexing thread).
* For medium-sized projects, as the system scales across multiple nodes, it will not exceed 3 shards to avoid excessive overhead.
* Once we reach the largest node sizes, further sharding is enabled to accommodate larger workloads.

Autosharding also enables autoscaling to increase resources as needed, preventing the system from staying at low capacity during high indexing workloads, by enabling projects to reach higher ingestion load values.

### Auto sharding formula

To determine the number of shards needed, we use the following formula:

![Autosharding formula in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt93cb63543b31d1b3/6a170cf660084b4d273c45c4/2185640ab125aaf4cd300fbaff74b3d83cf0de31-667x275.png)

This equation balances the need for increasing shards based on `write_load` while capping the number of shards to prevent oversharding. The division by 2 reflects the strategy of increasing shards only after exceeding half the capacity of a node. The min/max write threads represent the minimum and maximum number of write threads available in the autoscaling step function (i.e. the number of write threads available on the smallest 2GB step and the number of write threads available on the largest server)

Let’s visualize the output of the formula:

![Output of autosharding formula formula in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd5ebade9321a608b/6a170cf8ab7f085179db9ef7/ca928d959397c42a57311a91269d5418e983609a-1600x986.png)

On the Y axis we have the **number of shards**. And on the X axis we have the **write load**. We start with 1 shard and we get to 3 shards when the write load is just over 3.0. We remain with 3 shards for quite some time until the write load is about 48.0.

This covers us for the time we scale up through the nodes but haven’t really got to 2 or more or the largest servers, at which point we unlock auto sharding to more than 3 shards, as many as needed to ingest data.

While adding shards can improve indexing performance, excessive sharding in an Elasticsearch cluster can have negative repercussions - imagine that pizza with 56 slices being shared by only 7 friends. Each shard carries overhead costs, including maintenance and resource allocation. Our algorithm accounts for and avoids the peril of excessive sharding until we get to the largest workloads where adding more than 3 shards makes a material difference to indexing performance and throughput.

### Implementing autosharding with rollovers

The implementation of autosharding relies on the concept of [rollover](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-rollover-index.html). A rollover operation creates a new index within the [data stream](https://www.elastic.co/guide/en/elasticsearch/reference/current/data-streams.html), promoting it to the write index while designating the previous index as a regular backing index, which no longer accepts writes. This transition can occur based on specific conditions, such as exceeding a shard size of 50GB. We take care of configuring the [optimal rollover conditions](https://www.elastic.co/guide/en/elasticsearch/reference/current/data-stream-lifecycle-settings.html#_cluster_level_settings_3) for data streams in [Serverless](https://www.elastic.co/docs/current/serverless).

In [Serverless](https://www.elastic.co/docs/current/serverless) alongside the usual rollover conditions that relate to maintaining healthy indices and shards we introduce a new condition that evaluates whether the current write load necessitates an increase in shard count. If this condition is met, a rollover will be triggered and the new resulting data stream [write index](https://www.elastic.co/guide/en/elasticsearch/reference/current/data-streams.html#data-stream-write-index) will be configured with the optimal number of shards.

For downscaling, the system will monitor the workload and will not trigger a rollover solely for reducing shards. Instead, it will wait until a regular rollover condition, like the primary shard size, triggers the rollover. The resulting write index will be configured with a lower number of shards.

### Cooldown periods for shard adjustments

To ensure stability during shard adjustments, we implement cooldown periods:

* **Increase shards cooldown**: A minimum wait time of 4.5 minutes is enforced before increasing the number of shards since the last adjustment. The 4.5 minutes cooldown might seem peculiar but the interval has been chosen to make sure we **can** increase the number of shards every time [data stream lifecycle](https://www.elastic.co/search-labs/blog/data-lifecycle-simplified-for-data-streams) checks if data streams should rollover (currently, every 5 minutes) but not more often than 5 minutes, covering for internal Elasticsearch cluster reconfiguration.
* **Decrease shards cooldown**: We maintain a 3-day minimum wait time before reducing shards to ensure that the decision is based on sustained workload patterns rather than temporary fluctuations.

## Conclusion

The data streams autosharding feature in [Serverless](https://www.elastic.co/docs/current/serverless) Elasticsearch represents significant progress in managing data streams effectively. By automatically adjusting shard counts based on real-time indexing loads, this feature simplifies operations and enhances scalability.

With the added benefits of [autoscaling](https://www.elastic.co/search-labs/blog/elasticsearch-ingest-autoscaling), users can expect a more efficient and responsive experience, whether they are handling small projects or large-scale applications. As data workloads continue to evolve, the adaptability provided by auto sharding ensures that Elasticsearch remains a robust solution for managing diverse indexing needs.

Try out our [Serverless](https://www.elastic.co/docs/current/serverless) Elasticsearch offering to take advantage of data streams auto sharding and observe the indexing throughput scaling seamlessly as your data ingestion load increases.

Your pizzas will be optimally sliced as more friends arrive at your party, keen to try those sourdough craft pizzas you prepared for them.

### Frequently Asked Questions

#### What is Autosharding in Elasticsearch?

Autosharding is a feature in Elastic Cloud Serverless that automatically adjusts the number of shards in response to the current indexing load.

#### How does Elasticsearch Serverless handle sharding?

In Elastic Cloud Serverless we spare our users from the need to fiddle with sharding by automatically configuring the optimal number of shards for data streams based on the indexing load.

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3b371b70b12b9ef/6a170f240e2e49999441a1de/3c4c1e99b892f026b7aba098973593f8298e2ea6-1280x717.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elasticsearch replicas for load balancing in Serverless

March 24, 2026|[Andrei Dan](/search-labs/author/andrei-dan)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9f3d645218a14c98/6a170a25acf088f13cbe9ae5/d4a79be6eabad0a7452768bd16d04fcd75056e64-1280x853.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elastic Cloud Serverless: A deep dive into autoscaling and performance stress testing at scale

December 02, 2024|[David Brimley](/search-labs/author/david-brimley)|[+3](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter