---
title: 'Exploring GPU-accelerated vector search in Elasticsearch with NVIDIA: Chapter I'
company: Elastic
tag: 工程相关
date: 2025-03-19
url: https://www.elastic.co/search-labs/blog/gpu-accelerated-vector-search-elasticsearch-nvidia
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Exploring GPU-accelerated vector search in Elasticsearch with NVIDIA: Chapter I

Powered by NVIDIA cuVS, the collaboration looks to provide developers with GPU-acceleration for vector search in Elasticsearch.

March 19, 2025

[Chris Hegarty](/search-labs/author/chris-hegarty)[Hemant Malik](/search-labs/author/hemant-malik)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

We in the Elastic Engineering org have been busy optimizing vector database performance for a while now. Our mission: making Lucene and Elasticsearch the best vector database. Through hardware accelerated [CPU SIMD instructions](https://www.elastic.co/blog/accelerating-vector-search-simd-instructions), introducing new vector data compression innovations ([Better Binary Quantization a.k.a BBQ](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch)), and then exceeding expectations by updating the algorithmic approach to BBQ for even more benefits, and also [making Filtered HNSW faster](https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search). You get the gist—we’re building a faster, better, efficient(er?) vector database for the developers as they solve those RAG-gedy problems!

As part of our mission to leave no efficiencies behind, we are exploring acceleration opportunities with these curious computer chips, which you may have heard of—NVIDIA GPUs! (Seriously, have you not?).

When obsessing over performance, we have several problem spaces to explore—how to index exponentially more data, how to retrieve insights from it, and how to do it when your ML models are involved. You should be able to eke out every last benefit available when you have GPUs.

In this post, we dive into our collaboration with the NVIDIA vector search team as we explore GPU-accelerated vector search in Elasticsearch. This work paves the way for use cases where developers could use a mix of GPUs and CPUs for real-world Elasticsearch-powered apps. Exciting times!

## Elasticsearch GPUs

We are excited to share that the Elasticsearch engineering team is helping build the open-source cuVS Java API experience for developers, which exposes bindings for vector search algorithms. This work leverages our previous experience with Panama FFI. Elasticsearch and Apache Lucene use the NVIDIA cuVS API to build the graph during indexing. Okay, we are jumping ahead; let’s rewind a bit.

[NVIDIA cuVS](https://developer.nvidia.com/cuvs), an open-source C++ library, is at the heart of this collaboration. It aims to bring GPU acceleration to vector search by providing higher throughput, lower latency, and faster index build times. But Elasticsearch and Apache Lucene are written in Java; how will this work?

Enter [lucene-cuvs](https://github.com/SearchScale/lucene-cuvs) and the Elastic-NVIDIA-SearchScale collaboration to bring it into the Lucene ecosystem to explore GPU-accelerated vector search in Elasticsearch. In the recent NVIDIA cuVS 25.02 release, we added a Java API for cuVS. The new API is experimental and will continue to evolve, but it’s currently available for use. The question may arise: aren’t Java to native function calls slow? Not anymore! We’re using the new [Panama FFI](https://openjdk.org/projects/panama/) (Foreign Function Interface) for the bindings, which has minimal overhead for Java to native downcalls.

We’ve been using [Panama FFI in Elasticsearch and Lucene](https://www.elastic.co/search-labs/blog/lucene-and-java-moving-forward-together) for a while now. It’s awesome! But... there is always a “but”, isn’t there? FFI has availability challenges across Java versions. We overcame this by compiling the cuVS API to Java 21 and encapsulating the implementation within a multi-release jar targeting Java 22. This allows the use of cuVS Java directly in Lucene and Elasticsearch.

Ok, now that we have the cuVS Java API, what else would we need?

## A tale of two algorithms for CPU

Elasticsearch supports the [HNSW algorithm](https://arxiv.org/abs/1603.09320) for scalable approximate KNN search. However, to get the most out of the GPU, we use a different algorithm, [CAGRA [](https://arxiv.org/pdf/2308.15136)[**C**](https://arxiv.org/pdf/2308.15136)[*UDA*](https://arxiv.org/pdf/2308.15136) [**A**](https://arxiv.org/pdf/2308.15136)[*NN*](https://arxiv.org/pdf/2308.15136) [**GRA**](https://arxiv.org/pdf/2308.15136)[*ph*](https://arxiv.org/pdf/2308.15136)[]](https://arxiv.org/pdf/2308.15136), which has been specifically designed for the high levels of parallelism offered by the GPU.

Before we get into how we look to add support for CAGRA, let’s look at how Elasticsearch and Lucene access index data through a “codec format”. This consists of

1. the on-disk representation,
2. the interfaces for reading and writing data,
3. and the machinery for dealing with Lucene’s segment-based architecture.

We are implementing a new KNN (k-nearest neighbors) [vector format](https://lucene.apache.org/core/10_1_0/core/org/apache/lucene/codecs/KnnVectorsFormat.html) that internally uses the cuVS Java API to index and search on the GPU. From here, we “plumb” this codec type through Elasticsearch’s mappings to a field type in the index. As a result, your existing KNN queries continue to work regardless of whether the backing index is using a CAGRA or HNSW graph. Of course, this glosses over many details, which we plan to cover in a future blog. The following is the high-level architecture for a GPU-accelerated Elasticsearch.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb6197b631a34f8b6/6a170b0da6c2b9e60ce7970b/be6b7356c03df4dee7230625c2c9af3b019f93be-756x510.png)

This new codec format defaults to CAGRA. However, it also supports converting a CAGRA graph to an HNSW graph for search on the CPU.

## Indexing and searching on the GPU: Making some “core” decisions

With the stateless [architecture](https://www.elastic.co/search-labs/blog/stateless-your-new-state-of-find-with-elasticsearch) for Elasticsearch Serverless, which separates indexing and search, there is now a clear delineation of responsibilities. We pick the best hardware profile to fulfill each of these independent responsibilities.

We anticipate users to consider two main deployment strategies:

1. Index and search on the GPU: During indexing, build a CAGRA graph and use it during search - ideal when extremely low latency search is required.
2. Index on GPU and search on CPU: During indexing, build a CAGRA graph and convert it to an HNSW graph. The HNSW graph is stored in the index, which can later be used on the CPU for searching.

This flexibility provides different deployment models, offering tradeoffs between cost and performance. For example, an indexing service could use GPU to efficiently build and merge graphs in a timely manner while using a lower-powered CPU for searching.

## So here is the plan for GPU-accelerated vector search in Elasticsearch

We are looking forward to bringing performance gains and flexibility with deployment strategies to users, offering various knobs to balance cost and performance. [Here is the NVIDIA GTC 2025 session](https://www.nvidia.com/gtc/session-catalog/?tab.catalogallsessionstab=16566177511100015Kus&search=Lucene#/) where this work was presented in detail.

We’d like to thank the engineering teams at NVIDIA and SearchScale for their fantastic collaboration. In an upcoming blog, we will explore the implementation details and performance analysis in greater depth. Hold on to your curiosity hats 🎩!

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