---
title: 'Stateless: Data safety in a stateless world'
company: Elastic
tag: 工程相关
date: 2024-09-06
url: https://www.elastic.co/search-labs/blog/data-safety-stateless-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Stateless: Data safety in a stateless world

We discuss the data durability guarantees in stateless including how we fence new writes and deletes with a safety check which prevents stale nodes from acknowledging new writes or deletes

September 06, 2024

[Henning Andersen](/search-labs/author/henning-andersen)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

In recent blog posts, we announced the stateless architecture that underpins our Elastic Cloud Serverless offering. By offloading durability guarantees and replication to an object store (e.g., Amazon S3), we gain many advantages and simplifications.

Historically, Elasticsearch has relied upon local disk persistence for data safety and handling stale or isolated nodes. In this blog, we will discuss the data durability guarantees in stateless including how we fence new writes and deletes with a safety check which prevents stale nodes from unsafely acknowledging these operations.

In the following blog post, we will cover the basics of the durability promise and how Elasticsearch uses an operation log (translog) to be able to quickly and safely acknowledge writes to clients. Next we will dive into the problem, introduce concepts that help us, and finally explain the additional safety check that makes us able to confidently acknowledge writes to clients.

## Durability promise and translog

When clients write data to Elasticsearch, for instance using the [\_bulk](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) API, Elasticsearch will provide an HTTP response code for the request. Elasticsearch will only provide a successful HTTP response code (200/201) when data has been safely stored. We use an operation log (called translog) where requests are appended and stored before acknowledging the write. The translog allows us to replay operations that have not been successfully persisted to the underlying Lucene index (for instance if a node crashed after we acknowledged the write to the client). For more information on the translog and Lucene indices, see [this section](https://search-labs-elastic-evj8lqjrb-elastic-web-team.vercel.app/search-labs/blog/thin-indexing-shards-elasticsearch-serverless#translog) in our recent blog post on [thin indexing shards](https://search-labs-elastic-evj8lqjrb-elastic-web-team.vercel.app/search-labs/blog/thin-indexing-shards-elasticsearch-serverless), where we explain how we now store Lucene indices and the translog in the object store.

## Not knowing is the worst - the problem(s)

The master allocates a shard to an indexing node, that then owns indexing incoming data into that shard. However, we must account for scenarios where this node falls out of communication with the master and/or rest of the cluster.

In such cases, the master will (after timeouts) assume the node is no longer operational and reassign affected shards to other nodes. The prior assignment would now be considered stale. A stale node may still be operational attempting to index and persist data it receives.

In this scenario, with potentially two owners of a shard trying to acknowledging writes but out of communication with each other, we have two problems to solve:

* Avoiding file overwrites in the object store
* Ensuring that acknowledged writes are not lost

## Primary terms for stateless- an increasing number to the rescue

Elasticsearch has for many years utilized something we call primary terms. Whenever a primary shard is assigned to a node, it is given a primary term for the allocation. If a primary shard fails or goes from unassigned to assigned, the master will increment the primary term before reassigning the primary shard. This gives a strict order of primary shard assignments and ownership, higher primary terms were assigned after lower primary terms.

For stateless, we utilize primary terms in the path of index files we write to the object store to ensure that the first problem described above cannot happen. If a shard fails and is reassigned, we know it will have a higher primary term. A shard will only write files in the primary term specific path, thus there is no chance of an older shard assignment and a newer shard assignment writing the same files. They simply write to different paths.

The primary term is also used to ultimately provide the durability guarantee, more on that later.

Notice that primary shard relocations do not increment the primary term, instead the two nodes involved in a primary shard relocation hand off the ownership through an explicit protocol.

## Coordination term and node-left generation in stateless

The coordination subsystem in Elasticsearch is a strongly consistent mechanism used for cluster level coordination, including cluster membership and cluster metadata (all known as cluster state).

In stateless, this system also builds on top of the object store, uploading new cluster state versions. Like in stateful, it maintains an increasing number for elections called “term” (we’ll call it coordination term here to disambiguate it from the primary term described in the previous section). Whenever a node decides to start a new election, it will do so in a new coordination term, higher than any previous terms seen (more details on how this works in stateful in the blog post [here](https://www.elastic.co/blog/a-new-era-for-cluster-coordination-in-elasticsearch)).

In stateless, the election happens through an object store file we call the lease file. This file contains the coordination term and the node that claims that term is the elected master for the term.

This file will help the safety check we are interested in here. If the coordination term is still the same, we know the elected master did not change.

Just the coordination term is not enough though, since this does not necessarily change if a node leaves the cluster. In order to detect that a data node has not left the cluster, we also add the node-left generation to the lease file. This is an increasing number, incremented every time a node leaves the cluster. It resets from zero when the term changes (but we can disregard that for the story here).

The lease file is written to the object store as part of persisting a new cluster state. This write happens before any actions (like shard recovery) are otherwise taken based on the new cluster state.

## Object store read after write semantics in stateless

We use the object store to store all data in stateless and the visibility guarantees of the object store are therefore important to consider. Ultimately, the safety check builds on top of those guarantees.

Following are the main object [store](https://cloud.google.com/storage/docs/consistency) [visibility](https://aws.amazon.com/s3/consistency/) [guarantees](https://learn.microsoft.com/en-us/azure/storage/blobs/concurrency-manage) that we rely on:

* Read-after-write: after a successful write, any read will return the new contents.
* List-after-write: after a successful write, any listing matching the new file will return the file.

These were not a given years ago, but are available today across AWS S3, GCP and Azure blob storage.

## Stateless: The safety check

Having the necessary building blocks described above, we can now move on to the actual safety check and safety argumentation. While the translog guarantees durability of writes, we need to ensure that the node is still the assigned indexing node prior to acknowledging the write. The source of truth for that is in cluster state and the data node therefore needs to establish that it has a new enough cluster state in order to determine whether it is safe to acknowledge the write.

We are only interested in non-graceful events like node crashes, network partitions and similar. Graceful events like shard relocations are handled through explicit hand-offs that guarantee their correctness (we'll not dive into this in this blog post).

Let us consider an ungraceful event, for instance where the master node detects that a data node that holds a shard is no longer responding and it thus ejects the node from the cluster. We'll examine the safety check in this context and see how it avoids that a stale node potentially incorrectly acknowledges a write to client.

The safety check adds one additional check before responding to the client:

* Read the lease file from the object store. If the coordination term or node-left generation has advanced past the values in the node's local cluster state, it cannot rely on the cluster state until it receives an updated version with a higher or equal coordination term and node-left generation. With a new enough cluster state, it can be used to check whether the primary term of the shard has changed. If it has changed, the write will fail.

The happy path will incur no waiting here, since the term and node-left generation changes very infrequently relative to a normal write request frequency. The overhead of this check is thus small.

Notice that the ordering is important: the translog file is successfully uploaded before the safety check. We’ll see why shortly.

The ungraceful node-left event leads to an increment of the node-left generation in the lease file. Afterwards, a new node may be assigned the shard and start recovering data (this may be just one cluster state update, but the ordering of the lease file write and a node starting recovery is the only important part here and is guaranteed).

The newly assigned node will then read the shard data and recover the data contained in translog.

We see that we have the following ordering of events:

* Original data node writes translog before reading lease file
* Master writes lease file with incremented node-left generation before new data node starts recovering and thus before reading the translog
* Object store guarantees read-after-write on the lease file and translog files.

There are two main situations to consider:

* The original data node wrote the translog file and read a lease file indicating it is still in the cluster and owner of the shard (primary term did not change).

  + We then know that the master did not successfully update the lease file prior to the data node reading it. Therefore, the write to the translog by the original data node happens before the read of the translog by the new node assignment, guaranteeing that the operations will be available to the new node for recovery.
* The original data node wrote the translog file, but after possibly waiting for a new cluster state based on the information in the lease file, it is no longer the owner of the shard (making it fail the write request).

  + We do not respond successfully to the write request, thus do not promise durability.
  + The translog data might be available to the new node assignment during recovery, but that is fine. It is ok for a failed request to actually have persisted data durably.

We thus see that any write that Elasticsearch has successfully responded to will be available for any future owners of the same shard, concluding our safety argumentation.

Similarly, we can argue that a master failover case is safe. Here the coordination term rather than the node-left generation will change. We will not go through that here.

This same safety check is used in a number of other critical situations:

* During index file deletion. When Lucene merges segments, old segments can be deleted. We add a safety check here to protect against deleting files that a newer node assignment needs.
* During translog file deletion. Translogs can be deleted when the index data in the object store contains all the operations. Again, we add a safety check here to protect against deleting translog files that a newer node assignment needs.

## Conclusion

Congratulations, you made it to the end, hopefully you enjoyed the deep dive here. We described a novel mechanism for ensuring that Elasticsearch durably and safely persists writes to an object store, also in the presence of any kind of disruption causing Elasticsearch to otherwise have two nodes owning indexing into the same shard. We care deeply about such aspects and if you do too, perhaps take a look at our open [job offerings](https://jobs.elastic.co/#/).

Shout out to David Turner, Francisco Fernández Castaño and Tim Brooks who did most of the real work here.

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