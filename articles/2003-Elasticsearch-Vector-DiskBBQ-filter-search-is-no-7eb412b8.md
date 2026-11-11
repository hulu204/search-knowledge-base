---
title: 'Elasticsearch Vector DiskBBQ filter search is now 3–5x faster'
company: Elastic
tag: 召回
date: 2026-05-13
url: https://www.elastic.co/search-labs/blog/faster-restrictive-filters-diskbbq
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch Vector DiskBBQ filter search is now 3–5x faster

Learn how Elasticsearch 9.4 makes restrictive filtered DiskBBQ vector search 3–5x faster and more stable by avoiding wasted centroid and postings-list work when selectivity is high.

May 13, 2026

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Elasticsearch 9.4 makes restrictive [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction) filtered vector search 3–5x faster. DiskBBQ is Elasticsearch’s new partition based index. It strives to provide the best trade-off for cost and performance by making the vector index as sympathetic as possible to the underlying system. While DiskBBQ does well with broad filters, it struggled with restrictive filters. Continuing our journey for a simple, fast, and efficient vector index, we adjust how we apply filtering and significantly improve latency.

## What’s hard about filtering partition indices

With partition indices, all searches are done in two phases:

* Find the nearest centroids.
* Find all the nearest vectors within the nearest centroids’ clusters.

For DiskBBQ, the centroids are quantized and possibly indexed in their own structure. The cluster contents (we’ll call them *postings lists* from now on) are laid out in an effort to make scoring the vectors fast. Postings are stored in blocks of 32, with each block in doc\_id order. Doc IDs are delta-encoded to minimize disk usage with low decode overhead. Vector values are also block-encoded, separating dimensions from quantized corrections to maximize [single instruction, multiple data (SIMD) throughput using our optimized kernels](https://www.elastic.co/search-labs/blog/elasticsearch-vector-search-simdvec-engine).

```
Vector Cluster (Posting List) layout
  | metadata |
  | doc_deltas[32] | vec_quant[32] | vec_quant_corrections[32] |
  | doc_deltas[32] | vec_quant[32] | vec_quant_corrections[32] |
  | ... |
  | doc_deltas[T]  | vec_quant[T]  | vec_quant_corrections[T]  |   (T <= 32)
```

Once we reach a postings list, the layout is optimized for fast scoring and filtering. For example, if an index sort is provided, blocks of vectors that match a filter will be stored and scored together within a list. This unlocks scoring contiguous blocks of vectors at a time, taking full advantage of the underlying CPU throughput.

That said, we don’t know if a cluster matches a given filter until we actually check its doc\_ids. Once verified, we can be sure to only score against the relevant vectors. In restrictive-filter cases, we can inspect a centroid and still find that none of its vectors match the filter. To compensate, we keep scoring and exploring centroids until we get a representative group of vectors scored.

This meant wasted work for restrictive filters. We score centroids, not knowing if they have vectors relevant to the filter or not; prepare to score the postings list, only to find that none of the blocks apply. The wasted compute adds up:

* Unnecessarily scoring the centroid.
* Loading a filtered-out postings list because it’s close to the query vector.
* Decoding and checking the document IDs in the list, only to find out none match.
* Continue the search, potentially hitting another completely filtered-out centroid, until we visit enough to get the desired recall.

Here’s an example showing the old flow. Check all the centroids, see what matches, move on to centroids that have matching vectors. Rinse and repeat.

![Video Thumbnail](https://play.vidyard.com/AmsfHM4f8ZczNH9tAHkjE3.jpg)

## How do we get to the right centroids quickly?

The simplest solution would be to skip centroids that contain no valid vectors. But we don’t want to index additional information for all potential filter fields and values. A user can provide many variations of complex or simple filters. This is a strength of Elasticsearch, and we don’t want to hamper that.

Instead, we simply store the mapping of `doc_id -> centroid_ord`. This gives us an immediate view of all docs and their centroid membership. Allowing us to iterate any provided filter in document order, quickly determining the relevant centroids. Of course, iterating every document to check if it passes a filter is not free. We only apply this eager logic if the average number of documents per cluster that match the filter is `1.25`. Yes, this is a “magic number”; however, it's empirically based. Assuming the filter is random, we’re validating at least one matching vector per centroid with some overhead. We may refine this in the future, but early experimentation found this number to be a sweet spot for most users.

![Video Thumbnail](https://play.vidyard.com/3jhP9PJ6uq6RQ9an8XeLoe.jpg)

Here’s the new way. Detecting we have a restrictive filter, go straight to the filtered centroids.

## Benchmark, benchmark, benchmark

Here’s a macro-benchmark with a random filter. The filter selectivity is purposefully extreme to show the significant improvement on hyper-restrictive filters. Here we see almost an order-of-magnitude improvement. Where before, when filters got very restrictive, there would be a horrible elbow. Now latency remains consistent and will in fact improve as filters get more restrictive.

![Line chart titled “Filter search over 1M docs” comparing two versions with latency values plotted against filter selectivity on a logarithmic scale.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt785cb8c505bc59f0/6a17ddaee8fbcea2503a180d/fdf97ce48c1ed108f67c0ac3b2773bdefd9b09c6-1980x1170.png)

A further validation is our nightly runs of [so-vector](https://github.com/elastic/rally-tracks/tree/master/so_vector) with [rally](https://github.com/elastic/rally) showing the improvement. You can try this yourself by specifying `bbq_disk` in the `vector_index_type` in the rally configuration.

![Line and area chart showing latency in milliseconds over time, with values decreasing sharply in late November 2025 and a tooltip highlighting a data point labeled 3.607 ms.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt49168c36ebe7b102/6a17ddaf7f6f1536fcc09a13/f811ef3d7029a8ef8f26cd0b4cfdb9bf2f38f287-1530x1304.png)

## What's next?

This is in Elastic Serverless now and will be in stack release 9.4.0. We aren’t done improving vector search in Elasticsearch. This is just another step in our journey to bring you simple, efficient, practical, and fast vector search. Thank you so much for using the code that we write. We ❤️ you.

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