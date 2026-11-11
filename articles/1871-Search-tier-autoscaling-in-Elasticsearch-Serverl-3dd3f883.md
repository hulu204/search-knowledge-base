---
title: 'Search tier autoscaling in Elasticsearch Serverless'
company: Elastic
tag: 工程相关
date: 2024-08-08
url: https://www.elastic.co/search-labs/blog/elasticsearch-serverless-tier-autoscaling
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Search tier autoscaling in Elasticsearch Serverless

Explore search tier autoscaling in Elasticsearch Serverless. Learn how autoscaling works, how the search load is calculated and more.

August 08, 2024

[Matteo Piergiovanni](/search-labs/author/matteo-piergiovanni)[John Verwolf](/search-labs/author/john-verwolf)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

## How autoscaling works in Elasticsearch Cloud Serverless

1. **Configures Boost Window & Search Power**
   Users define a **Boost Window** to prioritize recent data for faster access, and choose a **Search Power** level (on-demand, performant, or high availability) that determines how aggressively to allocate resources for search operations.
2. **Determines baseline configuration**
   The system uses the amount of boosted data and the selected Search Power level to determine an initial resource configuration (number and type of nodes), which serves as a starting point and can change as actual load patterns emerge.
3. **Measures & reports Search Load**
   Each search node continuously calculates a **Search Load** metric—based on CPU, thread pool usage, and queue depth—and reports it to the control plane along with a quality rating (OK, WARNING, BAD). This helps assess system pressure.
4. **Autoscaler selects optimal configuration**
   The autoscaler evaluates multiple potential node configurations and selects the **most cost-effective** option that satisfies the reported load and service-level targets.
5. **Stabilizes & applies scaling changes**
   To avoid rapid fluctuations, scaling down decisions are held for a 15-minute stabilization period. Once stable, the autoscaler validates constraints (like replica placement) and applies the new configuration to the infrastructure.

## Background

One of the key aspects of Elasticsearch Cloud Serverless is allowing users to deploy and use Elastic without the need to manage the underlying project nodes. To achieve this, we developed search tier autoscaling, a strategy to dynamically choose node size and count based on a multitude of parameters that we will delve into in this blog. This innovation ensures that you no longer need to worry about under-provisioning or over-provisioning your resources.

Whether you are dealing with fluctuating traffic patterns, unexpected data spikes, or gradual growth, search tier autoscaling seamlessly adapts the allocated hardware to the search tier dynamically based on search activity. Autoscaling is performed on a per project basis and is completely transparent to the end user.

## Introduction

Elastic serverless is a fully-managed product from Elastic that enables you to deploy and use Elastic products without the need to manage the underlying Elastic infrastructure, but instead focussing on extracting the most out of your data.

One of the challenges of self-managed infrastructure is dealing with the ever-evolving needs a customer faces. In the dynamic world of data management, flexibility and adaptability are crucial and traditional scaling methods often fall short and require manual adjustments that can be both time-consuming and imprecise. With search tier autoscaling, our serverless offering automatically adjusts resources to match the demand of your workload in real-time.

The autoscaling described in this post is specific to the Elasticsearch project type within Elastic's serverless offering. Observability and security may have different autoscaling mechanisms tailored to their unique requirements.

Another important piece of information needed before diving into the details of autoscaling is how we manage our data to achieve a robust and scalable infrastructure. We use S3 as the primary source of truth, providing reliable and scalable storage. To enhance performance and reduce latency, search nodes use a local cache to quickly access frequently requested data without repeatedly retrieving it from S3. This combination of S3 storage and caching by search nodes forms an efficient system, ensuring that both durable storage and fast data access fit our user’s demands effectively.

## Search tier autoscaling inputs

To demonstrate how autoscaling works, we’ll dive into the various metrics that are used in order to make scaling decisions.

When starting a new serverless Elasticsearch project, a user can choose two parameters that will influence how autoscaling behaves:

* **Boost Window**: defines a specific time range within which search data is considered boosted.

  + **Boosted Data**: data that falls within the boost window is classified as boosted data. All time-based documents with a `@timestamp` within the boost window range and all non-time-based documents will fall in the boosted data category. This time-based classification allows the system to prioritize this data when allocating resources.
  + **Non-Boosted Data**: data outside the boost window is considered non-boosted. This older data is still accessible but is allocated fewer resources compared to boosted data.
* **Search Power**: a range that controls the number of Virtual Compute Units (VCUs) allocated to boosted data in the project. Search power can be set to:

  + **On-demand:** Autoscales based on data and search load, with a lower minimum baseline for resource use. This flexibility results in more variable query latency and reduced maximum throughput.
  + **Performant:** Delivers consistently low latency and autoscales to accommodate moderately high query throughput.
  + **High availability:** Optimized for high availability scenarios, autoscaling to maintain query latency even at very high query volumes.

The boost window will determine the amount of boosted and non-boosted data for a project.

We define boosted data for a project as the amount of data within the boost window.

The total size of boosted data, together with the lower end of the selected search power range will determine the base hardware configuration for a project. This method is favored over scaling to zero (or near zero) because it helps maintain acceptable latency for subsequent requests. This is achieved by retaining our cache and ensuring CPUs are immediately available to process incoming requests. This approach avoids the delays associated with provisioning hardware from CSP and ensures the system readiness to handle incoming requests promptly.

Note that the base configuration can increase over time by ingesting more data or decrease if time series data falls out of the boost window.

This is the first piece of autoscaling, where we provide a base hardware configuration that can adapt to a user’s boosted data over time.

## Load based autoscaling

Autoscaling based on interactive data is only one piece of the puzzle. It does not account for the load placed on the Search Nodes by incoming search traffic. To this effect, we have introduced a new metric called **search load**. search load is a measure of the amount of physical resources required to handle the current search traffic.

Search Llad accounts for the resource usage that the search traffic places on the nodes at a given time, and thus allows for dynamic autoscaling in response.

### What is search load?

Search load is a measure of the amount of physical resources required to handle the current search traffic. We report this as a measure of the number of processors required per node. However, there is some nuance here.

When scaling, we move up and down between hardware configurations that have set values of CPU, memory, and disk. These values are scaled together according to given ratios. For example, to obtain more CPU, we would scale to a node with a hardware configuration that also includes more memory and more disk.

Search load indirectly accounts for these resources. It does so by using the time that search threads take within a given measurement interval. If the threads block while waiting for resources (IO), this also contributes to the threads’ execution time. If all the threads are 100% utilized in addition to queuing, this indicates the need to scale up. Conversely, if there is no queuing and the search thread pool is less than 100% utilized, this indicates that it is possible to scale down.

### How is search load calculated?

Search load is composed of two factors:

* **Thread Pool Load**: number of processor cores needed to handle the search traffic that is being processed.
* **Queue Load**: number of processor cores needed to handle the queued search requests within an acceptable timeframe.

To describe how the search load is calculated, we will walk through each aspect step-by-step to explain the underlying principles.

We will start by describing the **Thread Pool Load**. First, we monitor the total execution time of the threads responsible for handling search requests within a sampling interval, called `totalThreadExecutionTime`. The length of this sampling interval is multiplied by the processor cores to determine the maximum `availableTime`. To obtain the `threadUtilization` percent, we divide the total thread execution time by this `availableTime`.

```
double availableTime = samplingInterval * processorCores;
double threadUtilization = totalThreadExecutionTime / availableTime;
```

*For example, a 4 core machine with a 1s sampling interval would have 4 seconds of available time (4 cores \* 1s). If the total task execution time is 2s, then this results in 50% thread pool utilization (2s / 4s = 0.5).*

We then multiply the `threadUtilization` percent by the `numProcessors` to determine the `processorsUsed`, which measures the number of processor cores used. We record this value via an exponential weighted moving average (a moving average that favors recent additions) to smooth out small bursts of activity. This results in the value used for `threadPoolLoad`.

```
double processorsUsed = threadUtilization * numProcessors;
exponentialWeightedMovingAvg.add(processorUtilization);
double threadPoolLoad = exponentialWeightedMovingAvg.get();
```

Next, we will describe how the **Queue Load** is determined. Central to the calculation, there is a configuration `maxTimeToClearQueue` that sets the maximum acceptable timeframe that a search request may be queued. We need to know how many tasks a given thread can execute within this timeframe, so we divide the `maxTimeToClearQueue` by the exponential weighted moving average of the search execution time. Next, we divide the `searchQueueSize` by this value to determine how many threads are needed to clear the queue within the configured time frame. To convert this to the number of processors required, we multiply this by the ratio of `processorsPerThread`. This results in the value used for the `queueLoad`.

```
double taskPerThreadWithinSetTimeframe = maxTimeToClearQueue / ewmaTaskExecutionTime;
double queueThreadsNeeded = searchQueueSize / taskPerThreadWithinSetTimeframe;
double queueLoad = queueThreadsNeeded * processorsPerThread;
```

The search load for a given node is then the sum of both the `threadPoolLoad` and the `queueLoad`.

### Search load reporting

Each Search Node regularly publishes load readings to the Master Node. This will occur either after a set interval, or if a large delta in the load is detected.

The Master Node keeps track of this state separately for each Search Node, and performs bookkeeping in response to various lifecycle events. When Search Nodes are added/removed, the Master Node adds or removes their respective load entries.

The Master Node also reports a quality rating for each entry: **Exact**, **Minimum**, or **Missing**. **Exact** means the metric was reported recently, while **Missing** is assigned when a search load has not yet been reported by a new node.

Search load quality is considered **Minimum** when the Master Node has not received an update from the search load within a configured time period, e.g. if a node becomes temporarily unavailable. The quality is also reported as Minimum when a Search Node’s load value accounts for work that is not considered indicative of future work, such as downloading files that will be subsequently cached.

Quality is used to inform scaling decisions. We disallow scaling down when the quality of any node is inexact. However, we allow scaling up regardless of the quality rating.

## The autoscaler

The autoscaler is a component of Elastic Serverless designed to optimize performance and cost by adjusting the size and number of nodes in a project based on real-time metrics. It monitors metrics from Elasticsearch, determines an ideal hardware configuration, and applies the configuration to the managed Kubernetes infrastructure. With an understanding of the inputs and calculations involved in search tier metrics, we can now explore how the autoscaler leverages this data to dynamically adjust the project node size and count for optimal performance and cost efficiency.

The autoscaler monitors the search tier metrics every 5 seconds. When new metrics arrive for total interactive and non-interactive data size, together with the search power range, the autoscaler will then determine the range of possible hardware configurations. These configurations range from a minimum to a maximum, defined by the search power range.

The autoscaler then uses the search load reported by Elasticsearch to select a “desired” hardware configuration within the available range that has at least the number of processor cores to account for the measured search load.

This desired configuration serves as an input to a stabilization phase where the autoscaler decides if the chosen scale direction can be applied immediately; if not, it is discarded. There is a 15-minute stabilization window for scaling down, meaning 15 minutes of continuous scaling down events are required for a scale down to occur. There is no stabilization period for scaling up. Scaling events are non-blocking; therefore, we can continue to make scaling decisions while subsequent operations are still ongoing. The only limit to this is defined by the stabilization window described above.

The configuration is then checked against the maximum number of replicas for an index in Elasticsearch to ensure there are enough search nodes to accommodate all the configured replicas.

Finally, the configuration is applied to the managed Kubernetes infrastructure, which provisions the project size accordingly.

## Conclusion

Search tier autoscaling revolutionizes the management of Elasticsearch Serverless projects. By leveraging detailed metrics, the autoscaler ensures that projects are always optimally sized. With serverless, users can focus on their business needs without the worry of managing infrastructure or being caught unprepared when their workload changes.

This approach not only enhances performance during high-demand periods, but also reduces costs during times of low activity, all while being completely transparent to the end user.

As a result, users can focus more on their core activities without the constant worry of manually tuning their projects to meet evolving demands. This innovation marks a significant step forward in making Elasticsearch both powerful and user-friendly in the realm of Serverless computing.

## Try it out!

### Frequently Asked Questions

#### What is search tier autoscaling?

Search tier autoscaling is a strategy to dynamically choose node size and count based on a multitude of parameters. This innovation ensures that you no longer need to worry about under-provisioning or over-provisioning your resources.

#### What is search load?

Search Load is a measure of the amount of physical resources required to handle the current search traffic.

#### What is Elastic's autoscaler?

The autoscaler is a component of Elastic serverless designed to optimize performance and cost by adjusting the size and number of nodes in a project based on real-time metrics.

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt84da396c370b06ec/6a170cfa6234e00dd3db1a55/d92e2e9fbae1dca1f18e623b2f5eb2a835307130-1600x1066.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Autosharding of data streams in Elasticsearch Serverless

December 10, 2024|[Andrei Dan](/search-labs/author/andrei-dan)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter