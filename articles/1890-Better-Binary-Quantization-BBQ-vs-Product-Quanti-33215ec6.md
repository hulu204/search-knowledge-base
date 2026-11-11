---
title: 'Better Binary Quantization (BBQ) vs. Product Quantization'
company: Elastic
tag: 索引构建
date: 2024-11-18
url: https://www.elastic.co/search-labs/blog/bit-vectors-elasticsearch-bbq-vs-pq
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Better Binary Quantization (BBQ) vs. Product Quantization

Why we chose to spend time working on Better Binary Quantization (BBQ) instead of product quantization in Lucene and Elasticsearch.

November 18, 2024

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

We have been progressively making vector search with Elasticsearch and Lucene faster and more affordable. Our main focuses have been not only improving the search speeds through SIMD, but also by reducting the cost through scalar quantization. First by 4x and then by 8x. However, this is still not enough. Through techniques like [Product Quantization](http://hal.archives-ouvertes.fr/docs/00/51/44/62/PDF/paper_hal.pdf) (referred to as PQ), 32x reductions can be achieved without significant costs in recall. We need to achieve higher levels of quantization to provide adequate tradeoffs for speed and cost.

One way to achieve this is by focusing on PQ. Another is simply improving on binary quantization. Spoilers:

* BBQ is 10-50x faster at quantizing vectors than PQ
* BBQ is 2-4x faster at querying than PQ
* BBQ achieves the same or better recall than PQ

So, what exactly did we test and how did it turn out?

## What exactly are we going to test?

Both PQ and Better Binary Quantization have various pros vs. cons on paper. But we needed a static set of criteria from which to test both. Having an independent "pros & cons" list is too qualitative a measurement. Of course things have different benefits, but we want a quantitative set of criteria to aid our decision making. This is following a pattern similar to the [decision making matrix explained by Rich Hickey](https://youtu.be/c5QF2HjHLSE?t=2350).

Our criteria were:

* Search speed
* Indexing speed flat
* Indexing speed with HNSW
* Merge speed
* Memory reduction possible
* Is the algorithm well known and battle tested in production environments?
* Is coarse grained clustering absolutely necessary? Or, how does this algorithm fair with just one centroid
* Brute-force oversampling required to achieve 95% recall
* HNSW indexing still works and can acheive +90% recall with similar reranking to brute-force

Obviously, almost all the criteria were measurable, we did have a single qualitative criteria that we thought important to include. For future supportability, being a well known algorithm is important and if all other measures were tied, this could be the tipping point in the decision.

## How did we test it?

Lucene and Elasticsearch are both written in Java, consequently we wrote two proof of concepts in Java directly. This way we get an apples-to-apples comparison on performance. Additionally, when doing Product Quantization, we only tested up to 32x reduction in space. While PQ does support further reduction in space by reducing the number of code books, we found that for many models recall quickly became unacceptable. Thus requiring much higher levels of oversampling. Additionally, we did not use [Optimized PQ](https://www.microsoft.com/en-us/research/wp-content/uploads/2013/11/pami13opq.pdf) due to the compute constraints required for such a technique.

We tested over different datasets and similarity metrics. In particular:

* [e5Small](https://huggingface.co/intfloat/e5-small-v2), which only has 384 dimensions and whose vector space is fairly narrow compared to other models. You can see how poorly e5small with naive binary quantization performs in our [bit vectors blog](https://www.elastic.co/search-labs/blog/bit-vectors-in-elasticsearch#a-bit-of-error). Consequently, we wanted to ensure an evolution of binary quantization could handle such a model.
* [Cohere's v3 model](https://huggingface.co/datasets/Cohere/wikipedia-2023-11-embed-multilingual-v3), which has 1024 dimensions and loves being quantized. If a quantization method doesn't work with this one, it probably won't work with any model.
* [Cohere's v2 model](https://huggingface.co/datasets/Cohere/wikipedia-22-12-simple-embeddings?row=7), which has 768 dimensions and its impressive performance relies on the non-euclidean vector space of max-inner product. We wanted to ensure that it could handle non-euclidean spaces just as well as Product Quantization.

We did testing locally on ARM based macbooks & remotely on larger x86 machines to make sure any performance differences we discovered were repeatable no matter the CPU architecture.

## Well, what were the results?

### e5small quora

This was a smaller dataset, 522k vectors built using e5small. Its few dimensions and narrow embedding space make it prohibitive to use with naive binary quantization. Since BBQ is an evolution of binary quantization, verifying that it worked with such an adverse model in comparison with PQ was important.

Testing on an M1 Max ARM laptop:

| Algorithm | quantization build time (ms) | brute-force latency (ms) | brute-force recall @ 10:50 | hnsw build time (ms) | hnsw recall @ 10:100 | hnsw latency (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| BBQ | 1041 | 11 | 99% | 104817 | 96% | 0.25 |
| Product Quantization | 59397 | 20 | 99% | 239660 | 96% | 0.45 |

### CohereV3

This model excels at quantization. We wanted to do a larger number of vectors (30M) in a single coarse grained centroid to ensure our smaller scale results actually translate to higher number of vectors.

This testing was on a larger x86 machine in google cloud:

| Algorithm | quantization build time (ms) | brute-force latency (ms) | brute-force recall @ 10:50 | hnsw build time (ms) | hnsw recall @ 10:100 | hnsw latency (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| BBQ | 998363 | 1776 | 98% | 40043229 | 90% | 0.6 |
| Product Quantization | 13116553 | 5790 | 98% | N/A | N/A | N/A |

When it comes to index and search speed at similar recall, BBQ is a clear winner.

### Inner-product search and BBQ

We have noticed in other experiments that non-euclidean search can be tricky to get correct when quantizing. Additionally, naive binary quantization doesn't care about vector magnitude, vital for inner-product.

Well, footnote in hand, we spent a couple of days on the algebra as we needed to adjust the corrective measures applied at the end of the query estimation. Success!

| Algorithm | recall 10:10 | recall 10:20 | recall 10:30 | recall 10:40 | recall 10:50 | recall 10:100 |
| --- | --- | --- | --- | --- | --- | --- |
| BBQ | 71% | 87% | 93% | 95% | 96% | 99% |
| Product Quantization | 65% | 84% | 90% | 93% | 95% | 98% |

## That wraps it up

![The BBQ vs PQ decision matrix](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf81b19ee52f24f23/6a17057bacf088680bbe9a1e/53c9143c25959bd8aa64d0e6fe0801c27bae4d41-1924x1218.jpg)

The complete decision matrix for BBQ vs Product Quantization.

We are pretty excited about Better Binary Quantization (BBQ). We have been hard at work kicking the tires and are continually surprised at the quality of results we get with just a single bit of information retained per vector dimension.

Look for it coming in an Elasticsearch release near you!

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