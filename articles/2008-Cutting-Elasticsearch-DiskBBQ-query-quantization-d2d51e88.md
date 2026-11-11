---
title: 'Cutting Elasticsearch DiskBBQ query quantization time by 5x'
company: Elastic
tag: 索引构建
date: 2026-05-27
url: https://www.elastic.co/search-labs/blog/diskbbq-asymmetric-query-quantization
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Cutting Elasticsearch DiskBBQ query quantization time by 5x

See how asymmetric quantization cuts DiskBBQ query quantization overhead from about 20% to 4% with little recall impact.

May 27, 2026

[Benjamin Trent](/search-labs/author/benjamin-trent)[Thomas Veasey](/search-labs/author/thomas-veasey)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Asymmetric quantization cuts the time Elasticsearch DiskBBQ spends quantizing queries by 5x. We discovered that too much time was spent quantizing queries. DiskBBQ started off quantizing queries with the same centroids as the indexed documents. However, we can make this cheaper by quantizing the queries with coarser-grained centroids. This improves query latency with very little observed recall impact in our tests.

## How DiskBBQ uses two centroid tiers for asymmetric quantization

DiskBBQ now uses two centroid tiers (fine-grained document centroids and coarser query centroids) so queries are quantized once per parent centroid instead of once per document centroid.

The old mental model is "one centroid does everything for a posting list." The new model splits responsibilities:

* Document centroids (fine-grained): Still used for posting-list structure and document centering.
* Query centroids (coarser): A parent centroid reused across multiple document centroids.

So instead of quantizing the query independently for every document centroid we visit, we quantize per parent centroid and reuse that work across all of its children. Since we were already using two-tier clustering logic as the index size grew, it was a natural fit. We can reuse the work we already do during querying.

![Diagram labeled “Asymmetric Quantization,” showing a blue circle marked “q” connected by arrows to two dashed green circles labeled “Parent P0” and “Parent P1.” Each parent contains four smaller white circles, and a green oval at the bottom reads “2 quantizations.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt675cf7e8155db1a5/6a4695a9774667d5662675d2/1fcb6cfb5b0186ea976e3f3942b043d3c9f33a6a-1378x1560.png)![Diagram labeled “Symmetric quantization,” showing a blue circle marked “q” at the top with arrows pointing to eight white circles arranged in two rows. An orange oval at the bottom reads “8 quantizations.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7660350f75f4d252/6a4695adcbd40ec6d3f55f93/4980bc720abedc4626bf48bbb3d2f6bec06eaff4-1286x1560.png)

These images are a simple representation of our goal: Quantizing per centroid gives us overhead per centroid. Let’s get rid of it!

The goal is to significantly reduce the number of times we actually need to quantize a given query.

## The math behind asymmetric BBQ in Elasticsearch

To center the data prior to computing quantized query and document vectors, qqq and ddd, we rewrite the dot product qtdq^tdqtd as (m+q−m)t(m+d−m)(m+q-m)^t(m+d-m)(m+q−m)t(m+d−m) and expand. We can perform exactly the same operation but using different centroids for the query vector qqq and document vector ddd. Specifically,

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd01f666c5dfa4f24/6a4695b015103586c4202edb/f395654cf3cc965254dfc8d7e66b57743d29cf41-1566x206.png)

As for standard Better Binary Quantization (BBQ), we quantize q−mqq-m\_qq−mq​ and d−mdd-m\_dd−md​ in order to estimate the per (document, query) pair component of the dot product. The quantities mdtqm\_d ^tqmdt​q and mqt(d−md)m\_q ^t(d-m\_d)mqt​(d−md​) are scalars so just two extra additions per dot product we compute. For mdtqm\_d ^tqmdt​q, we compute naturally when finding the nearest centroid. For mqt(d−md)m\_q ^t(d-m\_d)mqt​(d−md​), this can be stored with the quantized document vectors, which are just 4 bytes overhead. Below, we’ll discuss how to manage the other term on the fly.

### Asymmetric BBQ in DiskBBQ

We cluster the document centroids (using k-means, for example) into kq<kdk\_q<k\_dkq​<kd​ clusters, for kqk\_qkq​ and kdk\_dkd​ the query and document centroid count, respectively. This means there’s a many-to-one mapping from document centroids to query centroids. We’ll denote the document centroids by their index i∈[kd]i ∈ [k\_d]i∈[kd​] and define this mapping to the query centroids as j:[kd]j : [k\_d]j:[kd​]→[kq][k\_q][kq​].

Since there’s a unique query centroid for each document centroid, we only need to cache one value for mqt(d−md)m\_q^t(d-m\_d)mqt​(d−md​) per quantized document vector, that is, for each document vector dkd\_kdk​ in posting list iii, we need to cache mj(i)t(yk−mi)m\_j(\_i)^t(y\_k-m\_i)mj​(i​)t(yk​−mi​) with the quantized document vector.

When we come to compute the dot products between a query and the document vectors in a cluster, we look up the quantized query vector corresponding to q−mj(i)q-m\_j(\_i)q−mj​(i​) and we compute mitqm\_i^tqmit​q once and use it to process the whole posting list. The quantization process is significantly more expensive than computing the dot product, so this is a big net win.

The (q−mq)t(d−md)(q-m\_q)^t(d-m\_d)(q−mq​)t(d−md​) term is estimated using the usual [BBQ machinery](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization), that is, these vectors will be quantized and the dot product value estimated from the quantized vectors. Then we can use (1) to compute the final dot product estimate. Notice that this means we only need to quantize the query at most kqk\_qkq​ times. Furthermore, we typically visit many centroids from the same parent centroid in a search because they’re close to one another.

### Euclidean distance corrections for asymmetric quantization

For Euclidean, we can write ∣∣q−d∣∣2=∣∣q∣∣2+∣∣d∣∣2−2qtd||q-d ||^2=||q||^2+||d||^2-2q^td∣∣q−d∣∣2=∣∣q∣∣2+∣∣d∣∣2−2qtd and treat the qtdq^tdqtd term exactly as above. In fact, there’s a slightly nicer form. Substituting, we have that:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf7cc1ab13a3dc512/6a4695b274bff735d8a05b44/8faf7cd146c3221f3a3929e07286ceb82ac95a04-1598x122.png)

We can rewrite this as follows:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltce5ca0055196ceff/6a4695b62d406b3c77ba2bac/91d700d38d0e7842f2efef5d7778a6a34142c384-1172x362.png)

The corrective terms are the norm of query vector qqq minus the document centroid mdm\_dmd​, the norm of the document vector ddd minus the query centroid mqm\_qmq​, and the norm of the difference of query and document centroids. As before, ∣∣d−mq∣∣2−∣∣md−mq∣∣2||d-m\_q||^2-||m\_d-m\_q||^2∣∣d−mq​∣∣2−∣∣md​−mq​∣∣2 can be stored as a single float with each document.

## What changed in DiskBBQ indexing and scoring

At indexing/merge time, centroids can be clustered into parent groups when centroid count is large enough. Posting metadata moved from "centroid ordinal + centroid score" to a shape that explicitly carries query-centroid ordinal and document-centroid score. That decoupling is what lets scoring read documents and query centering from different places. For Euclidean, let’s break it down further by our mathematics above:

=∣∣q−md∣∣2+∣∣d−mq∣∣2−∣∣md−mq∣∣2 =||q-m\_d||^2+||d-m\_q||^2-||m\_d-m\_q||^2=∣∣q−md​∣∣2+∣∣d−mq​∣∣2−∣∣md​−mq​∣∣2

∣∣q−md∣∣2||q-m\_d||^2∣∣q−md​∣∣2 <- This is the distance from a “query vector qqq” to “document centroid mdm\_dmd​”. We already gather this when we find the nearest centroids during querying. No new work.

∣∣d−mq∣∣2||d-m\_q||^2∣∣d−mq​∣∣2 <- This is the distance from “document vector ddd” to “query centroid mqm\_qmq​”. However, recalling our [original quantization work](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization), this can simply replace a previously stored float value. No new storage is required.

∣∣md−mq∣∣2||m\_d-m\_q||^2∣∣md​−mq​∣∣2 <- This is just the distance between query centroid mqm\_qmq​ and document centroid mdm\_dmd​. This is just a single extra floating point value per postings list.

The practical change for dot product spaces is even simpler; the only correction value change is mj(i)t(yk−mi)m\_j(\_i)^t(y\_k-m\_i)mj​(i​)t(yk​−mi​) being stored instead of ytmiy^tm\_iytmi​.

These changes don’t introduce new computation costs and marginally reduce storage costs because we no longer quantize queries with document centroids. Those raw centroids don’t need to be present with the posting lists.

One cost we did add is a small cache of quantized query values. This is to account for clustering edge cases. For example, it's possible that query qqq is very close to query centroid qc0={dc0,dc1,dc2}qc\_0 =\{dc\_0, dc\_1, dc\_2\}qc0​={dc0​,dc1​,dc2​} but not quite as close as qc1={dc3,dc4,dc5}qc\_1 = \{dc\_3, dc\_4, dc\_5\}qc1​={dc3​,dc4​,dc5​}. That said, the actual nearest three document centroids could have a relative order: [dc0,dc3,dc1][dc\_0, dc\_3, dc\_1][dc0​,dc3​,dc1​]. So, to prevent the query from being quantized twice, we keep a limited cache of the most recent quantized values for a given query.

![Diagram showing a blue circle labeled “q” connected by colored arrows to two dashed oval regions. The green oval contains orange circles labeled dc_0–dc_2 and a green diamond labeled qc_0; and the purple oval contains pink circles labeled dc_3–dc_5 and a purple diamond labeled qc_1. Arrows illustrate relationships between q and the cluster components.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1aeb75c07434e77f/6a4695b9c71ec47ccbb9846c/d0df2be8b601fb46005667bfa81fc89b2fdaee48-1538x1092.png)

Here’s a visualization of the situation described above. In the typical iteration scenario, we don’t want to risk unnecessarily quantizing the query against the same query centroid multiple times.

## DiskBBQ asymmetric quantization: performance results

The flame graphs below show a before and after comparison. Before, about 20% of the time was spent quantizing queries when we visited each cluster. After our adjustment, it dropped to about 4%.

![Flame graph showing computational costs using symmetric quantization, with stacked colored blocks labeled for Elasticsearch and JDK vectorization functions. Each block’s width represents relative processing time, and the tooltip highlights quantization activity within Elasticsearch query code.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8e2b9d73c7ab998a/6a4695bc91c425d3b5732cb1/a17c3618a29b83d4196088d8422a7ede6eba5c3e-1999x655.png)

Flame graph showing the computational costs using symmetric quantization.

![Flame graph showing reduced computational time spent on quantization after introducing asymmetric quantization, with stacked colored blocks labeled for Elasticsearch and JDK vectorization functions. Each block’s width represents relative processing time, and a tooltip highlights quantization activity within Elasticsearch query code.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7bfd2b99e2fec276/6a4695bf5f1d903f44e3ba97/bb47abf8a7c7da5f5e8990beaaf3319741abfc52-1999x661.png)

Flame graph showing the reduction in computational time spent on quantization when asymmetric quantization is introduced.

Of course, the bulk of the cost is still just scoring the vectors in each cluster. But every little bit helps.

Here’s a better view of the full end-to-end performance and recall. The data set was 1 million [DBpedia](https://github.com/iai-group/DBpedia-Entity/) docs encoded with the [GTE-Base](https://huggingface.co/thenlper/gte-base) model. Here, “sec” indicates the number of clusters per secondary (parent) cluster. Note that symmetric quantization is still impacted by the secondary cluster size as it also impacts the two-tier clustering indexing we do already.

![Line chart titled “Latency vs Recall Pareto (sec = 16),” comparing asymmetric and symmetric quantization. The blue asymmetric line shows higher recall at each latency value than the red symmetric line, indicating improved latency with minimal recall impact. Axes are labeled “Latency (ms)” and “Recall.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltefa647d89e1eb323/6a4695c1a3096d631b9ce7bf/92ec17f1d4ca18a98d3c20b430af72cdf8d8be8a-1260x900.png)

This shows the benefit of asymmetric quantization: Removing that cost improves latency with very little, if any, recall impact.

However, the impact on our current index structure is still dominated by centroid scoring and scoring vectors in the cluster. Asymmetric quantization removes a frustratingly expensive part of our scoring overhead, but the impact isn’t dramatic given our current structure.

## What's next for DiskBBQ quantization

This simple piece of mathematics decouples our query quantization from our document quantization, giving us better storage efficiency and faster queries. This is in Elasticsearch Serverless now and will be in Elastic Stack version 9.4.0.

This now means that query quantization time isn’t a direct concern for future decisions. We can make larger index changes without worrying about the consistent overhead of quantization directly with document centroids.

This was a nerdy one. I hope you survived all the math (and that I copied it all down correctly). It’s always fun to be able to tackle complex problems with simple mathematics, and the results are actually positive in real use cases and data.

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