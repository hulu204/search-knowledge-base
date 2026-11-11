---
title: 'Vector search in Elasticsearch: The rationale behind the design'
company: Elastic
tag: 召回
date: 2023-07-24
url: https://www.elastic.co/search-labs/blog/vector-search-elasticsearch-rationale
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Vector search in Elasticsearch: The rationale behind the design

In this blog, you'll learn how vector search has been integrated into Elasticsearch and the trade-offs that we made.

July 24, 2023

[Adrien Grand](/search-labs/author/adrien-grand)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

Are you interested to learn about the characteristics of Elasticsearch for [vector search](https://www.elastic.co/what-is/vector-search) and what the design looks like? As always, design decisions come with pros and cons. This blog aims to break down how we chose to build vector search in Elasticsearch.

## Vector search is integrated in Elasticsearch through Apache Lucene

Some background about Lucene first: Lucene organizes data into immutable segments that are merged periodically. Adding more documents requires adding more segments. Modifying existing documents requires atomically adding more segments and marking previous versions of these documents as deleted. Every document within a segment is identified by a doc ID, which is the index of this document within the segment, similar to indices of an array. The motivation for this approach is managing inverted indices, which aren't good at in-place modifications but can be merged efficiently.

In addition to inverted indices, Lucene also supports stored fields (a document store), doc values (columnar storage), term vectors (per-document inverted indices), and [multi-dimensional points](https://www.elastic.co/fr/blog/lucene-points-6-0) in its segments. Vectors have been integrated the same way:

* New vectors get buffered into memory at index time.
* These in-memory buffers get serialized as part of segments when the size of the index-time buffer is exceeded or when changes must be made visible.
* Segments get periodically merged together in the background in order to keep the total number of segments under control and limit the overall per-segment search-time overhead. Since they are part of segments, vectors need to be merged too.
* Searches must combine top vector hits across all segments in the index.
* Searches on vectors must look at the set of live documents in order to exclude documents that are marked as deleted.

The system above is driven by the way that Lucene works.

Lucene currently uses the [hierarchical navigable small world (HNSW)](https://arxiv.org/pdf/1603.09320.pdf) algorithm to index vectors. At a high level, HNSW organizes vectors into a graph where similar vectors are likely to be connected. HNSW is a popular choice for vector search because it is rather simple, performs well on comparative benchmarks for vector search algorithms, and supports incremental insertions. Lucene's implementation of HNSW follows Lucene's guideline of keeping the data on disk and relying on the page cache to speed up access to frequently accessed data.

Approximate vector search is exposed in Elasticsearch's \_search API through the [knn section](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#approximate-knn). Using this feature will directly leverage Lucene's vector search capabilities. Vectors are also integrated in Elasticsearch's scripting API, which allows performing [exact brute-force search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#exact-knn), or leveraging vectors for rescoring.

Let's now dive into the pros and cons of integrating vector search through Apache Lucene.

## Cons

The main cons of taking advantage of Apache Lucene for vector search come from the fact that Lucene ties vectors to segments. However, as we will see later in the pros section, tying vectors to segments is also what enables major features such as efficient pre-filtering, efficient hybrid search, and visibility consistency, among others.

### Merges need to recompute HNSW graphs

Segment merges need to take N input segments, typically 10 with the default merge policy, and merge them into a single segment. Lucene currently creates a copy of the HNSW graph from the largest input segment that doesn't have deletes and then adds vectors from other segments to this HNSW graph. This approach incurs index-time overhead as segments are merged compared to mutating a single HNSW graph in-place over the lifetime of the index.

### Searches need to combine results from multiple segments

Because an index is composed of multiple segments, searches need to compute the top-k vectors on every segment and then merge these per-segment top-k hits into global top-k hits. The impact on latency may be mitigated by searching segments in parallel, but this approach still incurs some overhead compared to searching a single HNSW graph.

### RAM needs to scale with the size of the data set to retain optimal performance

Traversing the HNSW graph incurs lots of random access. To perform efficiently, data sets should fit into the page cache, which requires sizing RAM based on the size of the vector data set that is managed. There exist other algorithms than HNSW for vector search that have more disk-friendly access patterns, though they come with other downsides, like higher query latency or worse recall.

## Pros

### Data sets can scale beyond the total RAM size

Because data is stored on disk, Elasticsearch will allow data sets that are larger than the total amount of RAM that is available on the local host, and performance will degrade as the ratio of the HNSW data that can fit in the page cache decreases. As described in the previous section, performance-savvy users will need to scale RAM size with the size of the data set to retain optimal performance.

### Lock-free search

Systems that update data structures in place generally need to take locks in order to guarantee thread safety under concurrent indexing and search. Lucene's segment-based indices never require taking locks at search time, even in the case of concurrent indexing. Instead, the set of segments that the index is composed of is atomically updated on a regular basis.

### Support for incremental changes

New vectors may be added, removed, or updated at any time. Some other [approximate nearest-neighbor search](https://www.elastic.co/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0) algorithms require being fed with the entire data set of vectors. Then once all the vectors are provided, an index training step is executed. For these other algorithms, any significant update to the vector data set requires the training step to be completed again, and this can get computationally expensive.

### Visibility consistency with other data structures

A benefit of integrating at such a low level into Lucene is that we get consistency with other data structures out of the box when looking at a point-in-time view of the index. If you perform an update of a document to update both its vector and some other keyword field, then concurrent searches are guaranteed to either see the old value of the vector field and the old value of the keyword field — if the point-in-time view was created prior to the update — or the new value of the vector field and the new value of the keyword field — if the point-in-time view was created after the update. Likewise for deletes, if a document gets marked as deleted, then either all data structures including the vector store will ignore it, or they will see it if they operate on a point-in-time view that was created prior to the deletion.

### Incremental snapshots

The fact that vectors are part of segments helps snapshots remain incremental by taking advantage of the fact that two subsequent snapshots usually share the majority of their segments, especially the bigger ones. [Incremental snapshots](https://www.elastic.co/blog/how-do-incremental-snapshots-work) would not be possible with a single HNSW graph that gets mutated in-place.

### Filtering and hybrid support

Integrating directly into Lucene also makes it possible to integrate efficiently with other Lucene features, such as pre-filtering vector searches with an arbitrary Lucene filter or combining hits coming from a vector query with hits coming from a traditional full-text query.

By having its own HNSW graph that is tied to a segment and where nodes are indexed by doc ID, Lucene can make interesting decisions about how best to pre-filter vector searches: either by linearly scanning documents that match the filter if it is selective, or by traversing the graph and only considering nodes that match the filter as candidates for top-k vectors otherwise.

### Compatibility with other features

Because the vector store is like any other Lucene data structure, many features are compatible with vectors and vector search automatically, including:

* Aggregations
* Document-level security
* Field-level security
* Index sorting
* Access to vectors through scripts (e.g., from a script\_score query or a reranker)

### Looking ahead: Separation of indexing and search

As discussed in [another blog](https://www.elastic.co/blog/stateless-your-new-state-of-find-with-elasticsearch), future versions of Elasticsearch will run indexing and search workloads on different instances. The implementation will essentially look as if you were continuously creating snapshots on indexing nodes and restoring them on search nodes. This will help prevent the high cost of vector indexing from impacting searches. Such a separation of indexing and search wouldn't be possible with a single shared HNSW graph instead of multiple segments, short of sending the full HNSW graph over the wire every time changes need to be reflected on new searches.

## Conclusion

In general, Elasticsearch provides excellent vector search capabilities that are integrated with other Elasticsearch features:

* Vector searches can be pre-filtered by any supported filter, including the most sophisticated ones.
* Vector hits can be combined with hits of arbitrary queries.
* Vector searches are compatible with aggregations, document-level security, field-level security, index sorting, and more.
* Indices that contain vectors still obey the same semantics as other indices, including for the \_refresh, \_flush and \_snapshot APIs. They will also support separation of indexing and search in stateless Elasticsearch.

This is done at the expense of some index-time and search-time overhead. That said, vector search still typically runs in the order of tens or hundreds of milliseconds and is much faster than a brute-force exact search. More generally, both the index-time and search-time overheads seem manageable compared to other vector stores in existing [comparative benchmarks](https://ann-benchmarks.com/glove-100-angular_10_angular.html)\* (look for the "luceneknn" line). We also believe that a lot of the value of vector search gets unlocked through the ability to combine vector search with other functionality. Furthermore, we recommend checking out our [tuning guide for KNN search](https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-knn-search.html), which lists a number of measures that help mitigate the negative impact of the aforementioned cons.

I hope you enjoyed this blog. Don't hesitate to reach out via [Discuss](https://discuss.elastic.co/) if you have questions. And feel free to try out vector search in your existing deployment, or [spin up a free trial](https://www.elastic.co/elasticsearch/service) of Elasticsearch Service on Elastic Cloud (which always has the latest version of Elasticsearch).

*\*At the time of this writing, these benchmarks do not yet take advantage of vectorization. For more information on vectorization,* [*read this blog*](https://www.elastic.co/blog/accelerating-vector-search-simd-instructions)*.*

*The release and timing of any features or functionality described in this post remain at Elastic's sole discretion. Any features or functionality not currently available may not be delivered on time or at all.*

### Frequently Asked Questions

#### What are the cons of using Apache Lucene for vector search?

The main cons of taking advantage of Apache Lucene for vector search come from the fact that Lucene ties vectors to segments. These cons include: 1) Merges need to recompute HNSW graphs. 2) Searches need to combine results from multiple segments. 3) RAM needs to scale with the size of the data set to retain optimal performance. However, tying vectors to segments is also what enables major features such as efficient pre-filtering, efficient hybrid search, and visibility consistency.

#### What are the pros of using Apache Lucene for vector search?

The pros of taking advantage of Apache Lucene for vector search is that it enables features such as efficient pre-filtering, efficient hybrid search, visibility consistency, among others.

#### How is vector search integrated into Elasticsearch?

Vector search is integrated into Elasticsearch through Apache Lucene.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter