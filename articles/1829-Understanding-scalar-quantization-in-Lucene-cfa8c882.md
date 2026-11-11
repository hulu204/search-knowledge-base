---
title: 'Understanding scalar quantization in Lucene'
company: Elastic
tag: 索引构建
date: 2023-11-11
url: https://www.elastic.co/search-labs/blog/scalar-quantization-in-lucene
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Understanding scalar quantization in Lucene

Explore how Elastic introduced scalar quantization into Lucene, including automatic byte quantization, quantization per segment & performance insights.

November 11, 2023

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

## Automatic byte quantization in Lucene

While HNSW is a powerful and flexible way to store and search vectors, it does require a significant amount of memory to run quickly. For example, querying 1MM float32 vectors of 768 dimensions requires roughly 1,000,000∗4∗(768+12)=3120000000bytes≈3GB1,000,000 \* 4 \* (768 + 12) = 3120000000 bytes \approx 3GB1,000,000∗4∗(768+12)=3120000000bytes≈3GB of ram. Once you start searching a significant number of vectors, this gets expensive. One way to use around 75%75\%75% less memory is through byte quantization. Lucene and consequently Elasticsearch has supported indexing bytebytebyte vectors for some time, but building these vectors has been the user's responsibility. This is about to change, as we have introduced int8int8int8 scalar quantization in Lucene.

## Scalar quantization 101

All quantization techniques are considered lossy transformations of the raw data. Meaning some information is lost for the sake of space. For an in depth explanation of scalar quantization, see: [Scalar Quantization 101](https://www.elastic.co/search-labs/scalar-quantization-101). At a high level, scalar quantization is a lossy compression technique. Some simple math gives significant space savings with very little impact on recall.

## Exploring the architecture

Those used to working with Elasticsearch may be familiar with these concepts already, but here is a quick overview of the distribution of documents for search.

Each Elasticsearch index is composed of [multiple shards](https://www.elastic.co/guide/en/elasticsearch/reference/current/size-your-shards.html#size-your-shards). While each shard can only be assigned to a single node, multiple shards per index gives you compute parallelism across nodes.

Each shard is composed as a single [Lucene Index](https://lucene.apache.org/core/9_8_0/core/org/apache/lucene/index/package-summary.html). A Lucene index consists of multiple read-only segments. During indexing, documents are buffered and periodically flushed into a read-only segment. When certain conditions are met, these segments can be merged in the background into a larger segment. All of this is configurable and has its own set of complexities. But, when we talk about segments and merging, we are talking about read-only Lucene segments and the automatic periodic merging of these segments. [Here is a deeper dive](https://www.elastic.co/search-labs/vector-search-elasticsearch-rationale) into segment merging and design decisions.

## Quantization per segment in Lucene

Every segment in Lucene stores the following: the individual vectors, the HNSW graph indices, the quantized vectors, and the calculated quantiles. For brevity's sake, we will focus on how Lucene stores quantized and raw vectors. For every segment, we keep track of the raw vectors in the vecvecvec file, quantized vectors and a single corrective multiplier float in veqveqveq, and the metadata around the quantization within the vemqvemqvemq file.

![The .vec File](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1861d0af970fd096/6a17d9887f6f15a45dc099c0/507a4d578f8a5d2225b11d16ac1fc0b7dd39eaa1-1207x228.png)

Figure 1: Simplified layout of raw vector storage file. Takes up dimension∗4∗numVectorsdimension \* 4 \* numVectorsdimension∗4∗numVectors of disk space since floatfloatfloat values are 4 bytes. Because we are quantizing, these will not get loaded during HNSW search. They are only used if specifically requested (e.g. brute-force secondary via [rescore](https://www.elastic.co/guide/en/elasticsearch/reference/current/filter-search-results.html#query-rescorer)), or for re-quantization during segment merge.

![The .veq file](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8c52b51939357280/6a17d9897b54f9130f8b3761/ffc6e8bffefc5cd36f14aae315184c89e04a6587-1440x207.png)

Figure 2: Simplified layout of the .veq.veq.veq file. Takes up (dimension+4)∗numVectors(dimension + 4)\*numVectors(dimension+4)∗numVectors of space and will be loaded into memory during search. The +4+ 4+4 bytes is to account for the corrective multiplier float, used to adjust scoring for better accuracy and recall.

![The .vemq file](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt28e007988f81e5c0/6a17d98b25daabe23208a0d9/555cc92d7d179d8c9711cefbaaac3e0b815d2e42-1440x182.png)

Figure 3: The simplified layout of the metadata file. Here is where we keep track of quantization and vector configuration along with the calculated quantiles for this segment.

So, for each segment, we store not only the quantized vectors, but the quantiles used in making these quantized vectors and the original raw vectors. But, why do we keep the raw vectors around at all?

## Quantization that grows with you

Since Lucene periodically flushes to read only segments, each segment only has a partial view of all your data. This means the quantiles calculated only directly apply for that sample set of your entire data. Now, this isn't a big deal if your sample adequately represents your entire corpus. But Lucene allows you to sort your index in various ways. So, you could be indexing data sorted in a way that adds bias for per-segment quantile calculations. Also, you can flush the data whenever you like! Your sample set could be tiny, even just one vector. Yet another wrench is that you have control over when merges occur. While Elasticsearch has configured defaults and periodic merging, you can ask for a merge whenever you like via [\_force\_merge](https://www.elastic.co/guide/en/elasticsearch/reference/8.10/indices-forcemerge.html) API. So how do we still allow all this flexibility, while providing good quantization that provides good recall?

Lucene's vector quantization will automatically adjust over time. Because Lucene is designed with a read-only segment architecture, we have guarantees that the data in each segment hasn't changed and clear demarcations in the code for when things can be updated. This means during segment merge we can adjust quantiles as necessary and possibly re-quantize vectors.

![Multiple segment quantiles](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0d9a2390958c3e82/6a17d98cbe6086e4fd0045d5/646baa8279719d06c05c1a4fdb80a0c060e0dd94-1440x446.png)

Figure 4: Three example segments with different quantiles.

But isn't re-quantization expensive? It does have some overhead, but Lucene handles quantiles intelligently, and only fully-requantizes when necessary. Let's use the segments in Figure 4 as an example. Let's give segments AAA and BBB 1,0001,0001,000 documents each and segment CCC only 100100100 documents. Lucene will take a weighted average of the quantiles and if that resulting merged quantile is near enough to the segments original quantiles, we don't have to re-quantize that segment and will utilize the newly merged quantiles.

![Merged quantiles](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte2596c10ee616cf3/6a17d98eec0f8903b85a6497/58fa20d60dc337ca7108eb01e84a07c330e87ee6-1440x447.png)

Figure 5: Example of merged quantiles where segments AAA and BBB have 100010001000 documents and CCC only has 100100100.

In the situation visualized in figure 5, we can see that the resulting merged quantiles are very similar to the original quantiles in AAA and BBB. Thus, they do not justify quantizing the vectors. Segment CCC, seems to deviate too much. Consequently, the vectors in CCC would get re-quantized with the newly merged quantile values.

There are indeed extreme cases where the merged quantiles differ dramatically from any of the original quantiles. In this case, we will take a sample from each segment and fully re-calculate the quantiles.

## Quantization performance & numbers

So, is it fast and does it still provide good recall? The following numbers were gathered running the experiment on a `c3-standard-8` GCP instance. To ensure a fair comparison with float32float32float32 we used an instance large enough to hold raw vectors in memory. We indexed 400,000400,000400,000 [Cohere Wiki](https://huggingface.co/datasets/Cohere/wikipedia-22-12-simple-embeddings) vectors using maximum-inner-product.

![Quantization Recall](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfa48e3724ad97fed/6a17d98f445de96aca4cff88/81958f99b8a1397f669db48de00f264cacc6b49f-576x455.png)

Figure 6: Recall@10 for quantized vectors vs raw vectors. The search performance of quantized vectors is significantly faster than raw, and recall is quickly recoverable by gathering just 5 more vectors; visible by quantized@15quantized@15quantized@15.

Figure 6 shows the story. While there is a recall difference, as to be expected, it's not significant. And, the recall difference dissappears by gathering just 5 more vectors. All this with 2×2\times2× faster segment merges and 1/4 of the memory of float32float32float32 vectors.

## Conclusion

Lucene provides a unique solution to a difficult problem. There is no “training” or “optimization” step required for quantization. In Lucene, it will just work. There is no worry about having to “re-train” your vector index if your data shifts. Lucene will detect significant changes and take care of this automatically over the lifetime of your data. Look forward to when we bring this capability into Elasticsearch!

### Frequently Asked Questions

#### What is scalar quantization?

Scalar quantization is a lossy compression technique. Some simple math gives significant space savings with little impact on recall.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt762b38f91bd71c8e/6a170db8b339d547bb76a048/368db71c500e72d20fe225fe44c2c40231e29765-721x420.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Bringing maximum-inner-product into Lucene

September 01, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9ec7a04e3bdbfd9f/6a467b337eb22d59efdfc54d/c07100b6fcc74dba250e6853b1c5ef1edabbedfc-1920x1080.png)

[Lucene](/search-labs/blog/category/lucene)[Index Data](/search-labs/blog/category/index-data)

### How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage

June 12, 2026|[Alan Woodward](/search-labs/author/alan-woodward)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf9fcbf843affc566/6a1706b8964ceaea3208bab9/7884e35f40c15fe349379ef7ae4648b21708962f-1070x712.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Concurrency bugs in Lucene: How to fix optimistic concurrency failures

February 07, 2025|[Benjamin Trent](/search-labs/author/benjamin-trent)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter