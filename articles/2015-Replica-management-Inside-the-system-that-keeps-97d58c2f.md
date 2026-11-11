---
title: 'Replica management: Inside the system that keeps Elasticsearch Serverless searches fast at scale'
company: Elastic
tag: 工程相关
date: 2026-06-11
url: https://www.elastic.co/search-labs/blog/elasticsearch-replica-management-serverless
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Replica management: Inside the system that keeps Elasticsearch Serverless searches fast at scale

A technical walkthrough of how two replica systems (one for failover, one for load balancing) combine every five minutes into a single cache-aware recommendation per index in Elasticsearch Serverless.

June 11, 2026

[Ben Chaplin](/search-labs/author/ben-chaplin)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

In a [recent post](https://www.elastic.co/search-labs/blog/elasticsearch-replicas-load-balancing-serverless), we shared a new system in [Elastic Cloud Serverless](https://www.elastic.co/cloud/serverless) that automatically adjusts the number of replicas for your indices based on search load. In this post, we’ll zoom out and look at the entire flow for determining the optimal number of replicas. We’ll also look more closely at a crucial consideration when adding replicas, cache capacity, and explain how each replica system ensures that data is entirely cacheable given the currently provisioned disk space.

## Some Serverless basics

In [Elasticsearch Serverless](https://www.elastic.co/search-labs/blog/elasticsearch-serverless-stateless-architecture), the object store is the single source of truth. Indexing nodes hold all primary shards which index data and upload it to the object store; search nodes hold replica shards which handle all searches, reading data from the object store. So, in Serverless, indices always have at least one replica. The more search nodes, the more opportunities for additional replicas.

Both tiers are scaled independently based on the needs of the specific Serverless project. The search tier scales based on [**search power**](https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/project-settings#elasticsearch-manage-project-search-ai-lake-settings), a user configuration that determines the range of resources available for the cluster, including the minimum amount of disk for caching data. Specifically, **boosted data**: recent time-based (`@timestamp`) documents within the user-defined **boost window**, plus any non-time-based documents.

## Replicas for instant failover (RfIF): one or two replicas based on search power

Back in 2024, we shipped the first replica system, **Replicas for instant failover (RfIF)**, which decides whether to assign one or two replicas to an index in Serverless. In Serverless, the object store provides durability, but data cached directly on search nodes is what makes searches fast. Two replicas give us resiliency in case we lose a search node unexpectedly. However, more replicas are only effective if the additional copies of the data can fit in the cache.

RfIF looks at the amount of cache space guaranteed by search power. Lower-cost options can only fit one copy of the boosted data on disk. In these cases, all indices get one replica. As search power increases, we take advantage of additional cache space to provision two replicas for some indices. Finally, for the largest search power setting, there’s enough cache space for all indices to get two replicas.

## Replicas for load balancing (RfLB): scaling replicas under search load

**Replicas for load balancing (RfLB)** was shipped in early 2026. [A previous blog post](https://www.elastic.co/search-labs/blog/elasticsearch-replicas-load-balancing-serverless) explains the system in detail (a must-read if you like pizza). In short, the goal of RfLB is to add replicas to indices under high search load. More replicas means higher throughput as they allow more search nodes to participate in serving results.

## Two systems, one recommendation

Both RfIF and RfLB run every five minutes and provide a recommended number of replicas for each index. RfIF recommends either one or two replicas based on search power and the amount of boosted data. RfLB recommends between one and N replicas based on search load, where N is the current number of search nodes. For each index, we take the larger of the two recommendations. These recommendations are then passed into a cache budgeting system, which may limit them based on available cache space.

```
Map<String, Integer> rfifRecs = RfIF.run(allIndices)
Map<String, Integer> rflbRecs = RfLB.run(allIndices)

Map<String, Integer> jointRecs = new Map()
for (index in allIndices) {
  rec = max(rfifRecs.get(index), rflbRecs.get(index))
  jointRecs.put(index, rec)
}

Map<String, Integer> finalRecs = cacheBudgetingSystem(jointRecs)
```

Recall from the [previous post](https://www.elastic.co/search-labs/blog/elasticsearch-replicas-load-balancing-serverless#scale-up-fast,-scale-down-slow) that if the final recommendation increases replicas from the current state, we apply it immediately. However, if the recommendation is to decrease replicas, we simply capture the signal. Only after ~30 minutes of repeated signals to decrease replicas do we apply the new value.

## Cache budgeting: ensuring replicas fit on disk

Now we’ll look a bit more closely at that last step: the cache budgeting system. If we provision too many replicas, a broad enough set of searches could cause frequent cache evictions, resulting in slow searches. To avoid this, we sometimes decrease the replica system’s recommendations to ensure all replicas will fit in the cache. RfIF already does this based on search power, but RfLB may recommend larger numbers of replicas for indices with high search load. These are exactly the recommendations we may limit here, those where RfLB exceeds RfIF.

Here’s some pseudocode of the algorithm (and explanation below):

```
long remainingBytes = totalCacheBudget 
  - cacheUsedByCurrentReplicas
  + cacheFreedByDecreases
  - cacheNeededForRfIFIncreases

Map<String, Integer> finalRecs = new Map()
for (index in allIndicesRankedByLoad) {
  long additionalReps = rflbRecs.get(index) - rfifRecs.get(index)
  if (additionalReps <= 0) {
    finalRecs.put(index, rfifRecs.get(index))
  } else {
    int replicasThatFit = floor(remainingBytes / index.boostedData)
    int granted = min(additionalReps, replicasThatFit)
    finalRecs.put(index, rfifRecs.get(index) + granted)
    remainingBytes -= granted * index.boostedData
  }
}
```

That first line of code has a lot going on:

1. `totalCacheBudget` is the amount of the provisioned disk in the cluster allocated for caching data.
2. `cacheUsedByCurrentReplicas` is the amount of cache used by the current replica configuration.
3. `cacheFreedByDecreases` represents the amount of cache freed up by replica decreases that will occur as a result of the new recommendations. This is valuable cache space that we may want to use for more replicas!
4. `cacheNeededForRfIFIncreases` reflects the fact that we will not limit RfIF’s recommendations in this cache budgeting system. Therefore, we must account for all the additional cache RfIF’s recommendations will use.

Accounting for all of this, `remainingBytes` is precisely the amount of cache space we have for any additional replicas RfLB recommends over RfIF. The algorithm that follows considers all indices (`allIndicesRankedByLoad` is an ordered list of all indices prioritizing those with higher search load) and makes use of these `remainingBytes` to grant replicas. This procedure makes sure to squeeze all the replicas we can out of the bytes we have. For example, if RfLB recommends an additional four replicas, but there’s only space for two, we’ll take two!

## Wrapping up

To summarize, replicas in Serverless are determined by two cooperating systems. One is focused on replication for instant failover, while the other replicates to provide better search throughput for indices under substantial search load. These systems run side by side, making a joint decision for each index and checking that the decision actually fits in the cache. The result is a Serverless offering you can rely on to adapt to changing conditions while respecting the bounds of the underlying resources to keep data cached and searches fast.

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