---
title: 'Ingest autoscaling in Elasticsearch'
company: Elastic
tag: 工程相关
date: 2024-07-29
url: https://www.elastic.co/search-labs/blog/elasticsearch-ingest-autoscaling
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Ingest autoscaling in Elasticsearch

Learn more about how Elasticsearch autoscales to address ingestion load.

July 29, 2024

[Pooya Salehi](/search-labs/author/pooya-salehi)[Henning Andersen](/search-labs/author/henning-andersen)[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

Sizing an Elasticsearch cluster correctly is not easy. The optimal size of the cluster depends on the workload that the cluster is experiencing, which may change over time. Autoscaling adapts the cluster size to the workload automatically without human intervention. It avoids over-provisioning resources for the cluster only to accommodate peak usage and it also prevents degrading cluster performance in case of under-provisioning.

We rely on this mechanism to free users of our [Elastic Cloud Serverless](https://www.elastic.co/docs/current/serverless) offering from having to make sizing decisions for the [indexing tier](https://www.elastic.co/search-labs/blog/stateless-your-new-state-of-find-with-elasticsearch). Ingest autoscaling requires continuously estimating the resources required to handle the incoming workload, and provisioning and de-provisioning these resources in a timely manner.

In this blog post we explore ingest autoscaling in Elasticsearch, covering the following:

* How ingest autoscaling works in Elasticsearch
* Which metrics we use to quantify the indexing workload the cluster experiences in order to estimate resources required to handle that workload
* How these metrics drive the autoscaling decisions.

## Ingest autoscaling overview

Ingest autoscaling in Elasticsearch is driven by a set of metrics that is exposed by Elasticsearch itself. These metrics reflect the ingestion load and the memory requirement of the indexing tier. Elasticsearch provides an autoscaling metrics API that serves these metrics which allows an external component to monitor these metrics and make decisions whether the cluster size needs to change (see Figure 1).

In the Elastic Cloud Serverless service, there is an autoscaler component which is a Kubernetes Controller. The autoscaler polls the Elasticsearch autoscaling metrics API periodically and calculates the desired cluster size based on these metrics. If the desired cluster size is different from the current one, the autoscaler changes the cluster size to consolidate the available resources in the cluster towards the desired resources. This change is both in terms of the number of Elasticsearch nodes in the cluster and the CPU, memory and disk available to each node.

![overview](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltce3b99ecd11442dd/6a17d7126df73179750a0d41/7c0cb0b822ca2a6531d35df15a0226a51d18a1cb-1440x1119.png)

**Figure 1**: ingestion autoscaling overview

An important consideration for ingest autoscaling is that when the cluster receives a spike in the indexing load the autoscaling process can take some time until it effectively adapts the cluster size. While we try to keep this reaction time as low as possible, it cannot be instantaneous. Therefore, while the cluster is scaling up, the Elasticsearch cluster should be able to temporarily push back on the load it receives if the increased load is otherwise going to cause cluster instability issues. The increase in the indexing load can manifest itself in the cluster requiring more resources, i.e., CPU, memory or disk. Elasticsearch has protection mechanisms that allows nodes to push back on the indexing load if any of these resources becomes a bottleneck.

To handle indexing requests Elasticsearch uses dedicated thread pools sized based on the number of cores available to the node. If the increased indexing load results in CPU or other resources becoming a bottleneck, incoming indexing requests are queued. [The maximum size of this queue](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-threadpool.html) is limited and any request arriving at the node when the queue is full will be rejected with a 429 HTTP code.

Elasticsearch also keeps track of the required memory to address ongoing indexing requests and rejects incoming requests (with a 429) if the indexing buffer [grows beyond 10% of the available heap memory](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-modules-indexing-pressure.html). This limits the memory used for indexing and ensures the node will not go out of memory.

The Elastic Cloud Serverless offering relies on the object store as the main storage for indexed data. The local disk on the nodes are used temporarily to hold indexed data. Periodically, Elasticsearch uploads the indexed data to the object store which allows freeing up the local disk space as we rely on the object store for durability of the indexed document. Nonetheless, under high indexing load, it is possible for the node to run out of disk space before the periodic upload task gets a chance to run and free up the local disk space. To handle these cases, Elasticsearch monitors the available local disk space and if necessary throttles the indexing activity while it attempts to free up space by enforcing an upload to the object store rather than waiting for the periodic upload to take place. Note that this throttling in turn results in queueing of the incoming indexing requests.

These protection mechanisms allow an Elasticsearch cluster to temporarily reject requests and provide the client with a response that indicates that the cluster is overloaded while the cluster tries to scale up. This push-back signal from Elasticsearch provides the client with a chance to react by reducing the load if possible or retrying the request which should eventually succeed if retried when the cluster is scaled up.

## Metrics

The two metrics that are used for ingest autoscaling in Elasticsearch are ingestion load and memory.

### Ingestion load

Ingestion load represents the number of threads that is needed to cope with the current indexing load. The autoscaling metrics API exposes a list of ingestion load values, one for each indexing node. Note that as the write thread pools (which handle indexing requests) are sized based on the number of CPU cores on the node, this essentially determines the total number of cores that is needed in the cluster to handle the indexing workload.

The ingestion load on each indexing node consists of two components:

* Thread pool utilization: the average number of threads in the write thread pool processing indexing requests during that sampling period.
* Queued ingestion load: the estimated number of threads needed to handle queued write requests.

The ingestion load of each indexing node is calculated as the sum of these two values for [all the three write thread pools](https://www.elastic.co/guide/en/elasticsearch/reference/current/modules-threadpool.html). The total ingestion load of the Elasticsearch cluster is the sum of the ingestion load of the individual nodes.

node\_ingestion\_load=∑(thread\_pool\_utilization+queued\_ingestion\_load)total\_ingestion\_load=∑(node\_ingestion\_load)\small
node\\_ingestion\\_load = \sum(thread\\_pool\\_utilization + queued\\_ingestion\\_load)
\newline
total\\_ingestion\\_load = \sum(node\\_ingestion\\_load)
node\_ingestion\_load=∑(thread\_pool\_utilization+queued\_ingestion\_load)total\_ingestion\_load=∑(node\_ingestion\_load)

![Figure 2: ingestion load components](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4e0ba9f4e7ae59b9/6a17d71463baff6110741ab5/b1ab391f2639aaa4b7807a37a23fb9c5375f9690-1440x831.png)

**Figure 2**: ingestion load components

The thread pool utilization is an [exponentially weighted moving average (EWMA)](https://en.wikipedia.org/wiki/Moving_average#Exponential_moving_average) of the number of busy threads in the thread pool, sampled every second. The EWMA of the sampled thread pool utilization values is configured such that the sampled values of the past 10 seconds have the most effect on the thread pool utilization component of the ingestion load and samples older than 60 seconds have very negligible impact.

To estimate the resources required to handle the queued indexing requests in the thread pool, we need to have an estimate for how long each queued task can take to execute. To achieve this, each thread pool also provides an EWMA of the request execution time. The request execution time for an indexing request is the (wall-clock) time taken for the request to finish once it is out of the queue and a worker thread starts executing it. As some queueing is acceptable and should be manageable by the thread pool, we try to estimate the resources needed to handle the excess queueing. We consider up to 30s worth of tasks in the queue manageable by the existing number of workers and account for an extra thread proportional to this value. For example, if the average task execution time is 200ms, we estimate that each thread is able to handle 150 indexing requests within 30s, and therefore account for one extra thread for each 150 queued items.

queued\_ingestion\_load=queue\_size×average\_request\_execution\_time30s\small
queued\\_ingestion\\_load = \frac{queue\\_size \times average\\_request\\_execution\\_time}{30s}
queued\_ingestion\_load=30squeue\_size×average\_request\_execution\_time​

Note that since the indexing nodes rely on pushing indexed data into the object store periodically, we do not need to scale the indexing tier based on the total size of the indexed data. However, the disk IO requirements of the indexing workload needs to be considered for the autoscaling decisions. The ingestion load represents both CPU requirements of the indexing nodes as well as disk IO since both CPU and IO work is done by the write thread pool workers and we rely on the wall clock time to estimate the required time to handle the queued requests.

Each indexing node calculates its ingestion load and publishes this value to the master node periodically. The master node serves the per node ingestion load values via the autoscaling metrics API to the autoscaler.

### Memory

The memory metrics exposed by the autoscaling metrics API are node memory and tier memory. The node memory represents the minimum memory requirement for each indexing node in the cluster. The tier memory metric represents the minimum total memory that should be available in the indexing tier. Note that these values only indicate the minimum to ensure that each node is able to handle the basic indexing workload and hold the cluster and indices metadata, while ensuring that the tier includes enough nodes to accommodate all index shards.

Node memory must have a minimum of 500MB [to be able to handle indexing workloads](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html#_consider_additional_heap_overheads), as well as [a fixed amount of memory per each index](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html#shard-count-recommendation). This ensures all nodes can hold metadata for the cluster, which includes metadata for every index. Tier memory is determined by accounting for the memory overhead of the field mappings of the indices and the amount of memory needed for each open shard allocated on a node in the cluster. Currently, the per-shard memory requirement uses a fixed estimate of 6MB. We plan to refine this value.

The estimate for the memory requirements for the mappings of each index is calculated by one of the data nodes that hosts a shard of the index. The calculated estimates are sent to the master node. Whenever there is a mapping change this estimate is updated and published to the master node again. The master node serves the node and total memory metrics based on these information via the autoscaling metrics API to the autoscaler.

## Scaling the cluster

The autoscaler is responsible for monitoring the Elasticsearch cluster via the exposed metrics, calculating the desirable cluster size to adapt to the indexing workload, and updating the deployment accordingly. This is done by calculating the total required CPU and memory resources based on the ingestion load and memory metrics. The sum of all the ingestion load per node values determines the total number of CPU cores needed for the indexing tier.

The calculated CPU requirement and the provided minimum node and tier memory resources are mapped to a predetermined set of cluster sizes. Each cluster size determines the number of nodes and the CPU, memory and disk size of each node. All nodes within a certain cluster size have the same hardware specification. There is a fixed ratio between CPU, memory and disk, thus always scaling all 3 resources linearly. The existing cluster sizes for the indexing tier are based on node sizes starting from 4GB/2vCPU/100GB disk to 64GB/32vCPU/1600GB disk. Once the Elasticsearch cluster scales up to the largest node size (64GB memory), any further scale-up adds new 64GB nodes, allowing a cluster to scale up to 32 nodes of 64GB. Note that this is not a hard upper bound on the number of Elasticsearch nodes in the cluster and can be increased if necessary.

Every 5 seconds the autoscaler polls metrics from the master node, calculates the desirable cluster size and if it is different from the current cluster size, it updates the Elasticsearch Kubernetes Deployment accordingly. Note that the actual reconciliation of the deployment towards the desired cluster size and adding and removing the Elasticsearch nodes to achieve this is done by Kubernetes. In order to avoid very short-lived changes to the cluster size, we account for a 10% headroom when calculating the desired cluster size during a scale down and a scale down takes effect only if all desired cluster size calculations within the past 15 minute have indicated a scale-down.

Currently, the time that it takes for an increase in the metrics to lead to the first Elasticsearch node being added to the cluster and ready to process indexing load is under 1 minute.

## Conclusion

In this blog post, we explained how ingest autoscaling works in Elasticsearch, the different components involved, and the metrics used to quantify the resources needed to handle the indexing workload. We believe that such an autoscaling mechanism is crucial to reduce the operational overhead of an Elasticsearch cluster for the users by automatically increasing the available resources in the cluster when necessary. Furthermore, it leads to cost reduction by scaling down the cluster when the available resources in the cluster are not required anymore.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### How we optimized refresh costs in Elasticsearch Serverless

July 31, 2024|[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3b371b70b12b9ef/6a170f240e2e49999441a1de/3c4c1e99b892f026b7aba098973593f8298e2ea6-1280x717.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elasticsearch replicas for load balancing in Serverless

March 24, 2026|[Andrei Dan](/search-labs/author/andrei-dan)

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