---
title: 'How we optimized refresh costs in Elasticsearch Serverless'
company: Elastic
tag: 工程相关
date: 2024-07-31
url: https://www.elastic.co/search-labs/blog/elasticsearch-refresh-costs-serverless
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How we optimized refresh costs in Elasticsearch Serverless

We explore how serverless Elasticsearch facilitates searches using data stored in a blob store while maintaining the same visibility semantics as stateful Elasticsearch. We discuss the challenges encountered during implementation and share strategies for balancing costs and complexity.

July 31, 2024

[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)[Henning Andersen](/search-labs/author/henning-andersen)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

Recently, we’ve [launched](https://www.elastic.co/blog/search-ai-lake-elastic-cloud-serverless) the Elastic Cloud Serverless offering that aims to provide a seamless experience to run search workloads in the cloud. To launch this, we’ve rearchitected Elasticsearch to [decouple](https://www.elastic.co/search-labs/blog/stateless-your-new-state-of-find-with-elasticsearch) storage from compute, where data is stored in a cloud blob store that provides virtually infinite storage and scalability. In this blog post, we’ll dive into how we removed a strong relationship between the number of indices and the number of object store calls, allowing us to improve UX and reduce costs at the same time.

Before we dive into the changes we made, it’s essential to first understand the interplay between Elasticsearch and Lucene.

Elasticsearch uses Lucene, a high-performance, open-source library written in Java, for full text indexing and search. When a document is indexed into Elasticsearch, it isn't immediately written to disk by Lucene. Instead, Lucene updates its internal in-memory data structures. Once enough data accumulates or a [refresh](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html) is triggered, these documents are then written to disk, creating a new set of immutable files known as segments in Lucene terminology. The indexed documents are not available for search until the segments are written to disk. That’s the reason why [refresh](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-refresh.html) is such an important concept in Elasticsearch. You might be wondering how durability is ensured when documents are kept in memory until a refresh is triggered. This is achieved through the Translog, which stores durably every operation to guarantee data persistence and recovery in case of failure.

Now that we know what Lucene segments are and why refreshes are needed in Elasticsearch, we can explore how refresh behavior differs between stateful Elasticsearch and [serverless Elasticsearch](https://www.elastic.co/search-labs/blog/stateless-your-new-state-of-find-with-elasticsearch).

## Refreshes in stateful Elasticsearch

In Elasticsearch, indices are divided into multiple shards, each consisting of a primary shard and potentially multiple replica shards. In stateful Elasticsearch, when a document is indexed, it is first routed to the primary shard, where Lucene processes and indexes it. After indexing on the primary shard, the document is then routed to the replica shards, where it is indexed by these copies.

As mentioned earlier, a refresh is needed to make these indexed documents searchable. In stateful Elasticsearch, a refresh writes the Lucene in-memory data structures to disk without performing an fsync. Refreshes are scheduled periodically, with each node executing them at different times. This process will create distinct Lucene segment files on each node, all containing the same set of documents.

## Refreshes in serverless Elasticsearch

In contrast, serverless Elasticsearch employs a segment-based replication model. In this approach, one node per shard handles document indexing and generates Lucene segments. These segments are uploaded to the blob store once a refresh is initiated. Subsequently, search nodes are informed about these new Lucene segments, which they can read directly from the blob store.

![Refresh flow before optimizations in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7cc4aefbc63dca3c/6a17d7783e03d793524f2ac9/efc718c485d64c1911365a7e20a9435aeb1fbdc0-1440x754.png)

The illustration above demonstrates how a refresh works in serverless Elasticsearch:

1. The indexing node, where all the documents were indexed, receives the refresh request and Lucene writes the in-memory data structures to disk, similar to how a stateful refresh operates.
2. The segment files are uploaded to the blob store as a single file (known as a stateless compound commit). In the illustration, S4 is uploaded.
3. Once the segment files are uploaded to the blob store, the indexing node sends a message to each search node, notifying them of the new segment files so they can perform searches on the newly indexed documents.
4. The search nodes fetch the necessary data from the blob store when executing searches.

This model offers the advantage of lightweight nodes, as data is stored in the blob store. This makes scaling or reallocating workloads between nodes more cost-effective compared to stateful Elasticsearch, where data must be transferred to the new node containing the new shard.

One aspect worth considering is the additional object store request costs associated with each refresh in serverless Elasticsearch. Every refresh operation created a new object in the object store, resulting in an object store PUT request that incurs associated costs. This led to a linear relationship between the number of indices and the number of object store PUT requests. With enough refreshes, object store costs could surpass the cost of the hardware itself. To address this, we initially implemented refresh throttling measures to manage costs effectively and mitigate potential issues over time. This blog post describes the next step in that effort, which allowed us to refresh faster and at a manageable cost.

## Refresh cost optimizations in serverless Elasticsearch

As previously mentioned, the serverless Elasticsearch architecture provides numerous benefits. However, to manage refresh costs effectively, we made decisions that occasionally impacted user experience. One such decision was enforcing a default refresh interval of 15 seconds, meaning that in some cases, newly indexed data won't become searchable until 15 seconds have passed. Despite our efforts, scenarios arose where object store expenses became prohibitive, prompting us to reassess our approach. In this section, we will delve into how we successfully decoupled refresh operations from object store calls to address these challenges without compromising user experience.

After evaluating various solutions—from temporary storage of segments in distributed file systems like NFS to direct pushing of segments into search nodes—we settled on an approach relying on serving segment data from indexing nodes directly to search nodes.

Rather than letting refresh immediately upload new Lucene segments to the blob store, index nodes now accumulate segments from refreshes and upload them as a single blob later. This enables index nodes to serve reads from search nodes in a manner akin to a blob store, delaying segment uploads until sufficient data accumulates or a predetermined time interval elapses.

This strategy grants us complete control over the size of the blobs uploaded to the blob store, enabling us to determine when request costs become negligible in comparison to hardware costs.

### Batched compound commits

We aimed to implement this enhancement incrementally and ensure backward compatibility with existing data stored in the blob store. Therefore, we opted to maintain the same file format for storing Lucene segments in the blob store. For context, Lucene segments comprise multiple files, each serving a distinct role. To streamline the upload process and minimize PUT requests, we introduced compound commits: single blobs containing all segment files consecutively, accompanied by a metadata header, including a directory of the files in the compound commit.

![Compound commit file format](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7207e2d6008df66e/6a17d779ec0f8984445a6446/a503ec1c16498a4ad86de3c1fce4d13e472144da-1440x441.png)

When retrieving a compound commit from the blob store, such as during shard relocation, our primary focus is typically on the compound commit header. This header is crucial as it contains the essential data needed to promptly populate internal data structures. With this in mind, we realized we could maintain the existing file format but streamline it so that each blob would sequentially append one compound commit after another. We denominated this new file format, batched compound commit.

![Batched compound commit file format](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt321e94e2043ef619/6a17d77aec0f8907455a644a/3c264c4b43632f508c96a6ebd2c381402a83fd5f-1440x374.png)

Since each compound commit's size is stored in its header, retrieving the headers of all compound commits within a batched compound commit is straightforward; we can sequentially read each header by simply seeking the next entry. When handling blobs in the old format, they are treated as singleton batched compound commits. Another critical aspect of our file format is maintaining fixed offsets for each Lucene segment file once it's appended into a batched compound commit. This ensures consistency whether the file is served from the index node or the blob store. It also prevents the need to evict cached entries on search nodes when the batched compound commit is eventually uploaded to the blob store.

### New refresh lifecycle

Index nodes will now accumulate Lucene segments from refreshes until enough data is gathered to upload them as a single blob. Let us explore how index and search nodes coordinate to determine where to access this data from.

![Optimized refresh flow in Elasticsearch serverless](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta3c527801c519b6d/6a17d77ce9ea8761a5a9c41d/578e9dbfeb31673e86429820479c211db5a27434-1440x802.png)

As shown in the illustration above, the following steps occur during the optimized refresh process in serverless Elasticsearch:

1. The index node receives a refresh request, writes a new set of Lucene segments to its local disk, and adds these segments to the pending batched compound commit for eventual upload.
2. The index node notifies the search node about these new segments, providing details about the involved segments and their locations (blob store or index node).
3. When a search node needs a segment to fulfill a query, it decides whether to get it from the blob store or the index node and caches the data locally.

![Optimized refresh upload flow in Elasticsearch serverless](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt782c93954782c163/6a17d77d4b055d0b68432050/8e051b6251fe96510dd1d31f679c54c042cd95e5-1440x721.png)

The image above illustrates the process of uploading data to the blob store in serverless Elasticsearch once enough segments have accumulated in the indexing nodes or after a specified amount of time has elapsed.

1. A refresh adds a new segment to the batched compound commit and the accumulated data reaches 16 MB, or a certain amount of time has passed since the last refresh, from this point onwards new segments are accumulated into a new batched compound commit.
2. The indexing node begins uploading the accumulated segments as a single blob to the object store.
3. The indexing node notifies the search node replicas of the latest segment uploaded to the object store, instructing them to fetch data from these segments from the blob store going forward.
4. If a search requires data that isn't cached locally, it will retrieve the necessary information from the blob store, while any previously fetched data from the indexing node remains valid even after the upload.

### Considerations and tradeoffs

The approach chosen blurs the clear separation between storage and compute, requiring index nodes to handle storage requests until Lucene segments are eventually uploaded to the blob store. However, the overhead from these storage requests is minimal and we have not observed impact on indexing throughput.

We'll note that we keep translog entries until corresponding data has been uploaded to the blob store, hence the approach maintains existing data safety guarantees. Recovery times after a crash may be slightly longer, but we consider this an acceptable trade-off.

## Conclusions

This blog post has explored our transition towards a more cloud-native approach, emphasizing its many benefits alongside the critical cost consideration. We traced our evolution from a model where each new Lucene segment generated a distinct object in the object store. This led to cost and user experience challenges in specific serverless workloads compared to stateful Elasticsearch. Batching object store uploads enabled us to minimize the number of object store requests and enhance the cost efficiency of our serverless offering.

![Reduction in PUT requests](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6478e2975a6ccedb/6a17d77f3e03d7925a4f2acd/58096951dd3f12d0b60072867febc6b7c90ecc26-1440x673.png)

## Acknowledgments

We would like to acknowledge the contributions of Iraklis Psaroudakis, Tanguy Leroux, and Yang Wang. Their efforts were instrumental in the success of this project.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9f3d645218a14c98/6a170a25acf088f13cbe9ae5/d4a79be6eabad0a7452768bd16d04fcd75056e64-1280x853.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elastic Cloud Serverless: A deep dive into autoscaling and performance stress testing at scale

December 02, 2024|[David Brimley](/search-labs/author/david-brimley)|[+3](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter