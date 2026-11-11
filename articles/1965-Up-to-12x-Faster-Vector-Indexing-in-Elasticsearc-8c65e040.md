---
title: 'Up to 12x Faster Vector Indexing in Elasticsearch with NVIDIA cuVS: GPU-acceleration Chapter 2'
company: Elastic
tag: 索引构建
date: 2025-12-03
url: https://www.elastic.co/search-labs/blog/elasticsearch-gpu-accelerated-vector-indexing-nvidia
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Up to 12x Faster Vector Indexing in Elasticsearch with NVIDIA cuVS: GPU-acceleration Chapter 2

Discover how Elasticsearch achieves nearly 12x higher indexing throughput with GPU-accelerated vector indexing and NVIDIA cuVS.

December 03, 2025

[Chris Hegarty](/search-labs/author/chris-hegarty)[Hemant Malik](/search-labs/author/hemant-malik)[Corey Nolet](/search-labs/author/corey-nolet)[+5](#)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Earlier this year, Elastic announced the [collaboration](https://ir.elastic.co/news/news-details/2025/Elastic-Brings-Enterprise-Data-to-NVIDIA-AI-Factories/default.aspx) with NVIDIA to bring GPU acceleration to Elasticsearch, integrating with [NVIDIA cuVS](https://developer.nvidia.com/cuvs)—as detailed in a [session at NVIDIA GTC](https://www.nvidia.com/en-us/on-demand/session/gtc25-S71286/) and various [blogs](https://www.elastic.co/search-labs/blog/gpu-accelerated-vector-search-elasticsearch-nvidia). This post is an update on the co-engineering effort with the NVIDIA vector search team.

## Recap

First, let’s bring you up to speed. Elasticsearch has established itself as a powerful vector database, offering a rich set of features and strong performance for large-scale similarity search. With capabilities such as scalar quantization, Better Binary Quantization ([BBQ](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch)), [SIMD](https://www.elastic.co/blog/accelerating-vector-search-simd-instructions) vector operations, and more disk-efficient algorithms like [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction), it already provides efficient and flexible options for managing vector workloads.

By integrating NVIDIA cuVS as a callable module for vector search tasks, we aim to deliver significant gains in vector indexing performance and efficiency to better support large-scale vector workloads.

## The challenge

One of the toughest challenges in building a high-performance vector database is constructing the vector index - the [HNSW](https://arxiv.org/abs/1603.09320) graph. Index building quickly becomes dominated by millions or even billions of arithmetic operations as every vector is compared against many others. In addition, index lifecycle operations, such as compaction and merges, can further increase the overall compute overhead of indexing. As data volumes and associated vector embeddings grow exponentially, accelerated computing GPUs, built for massive parallelism and high-throughput math, are ideally positioned to handle these workloads.

## Enter the Elasticsearch-GPU Plugin

[NVIDIA cuVS](https://developer.nvidia.com/cuvs) is an open-source CUDA-X library for GPU-accelerated vector search and data clustering that enables fast index building and embedding retrieval for AI and recommendation workloads.

Elasticsearch uses cuVS through [cuvs-java](https://mvnrepository.com/artifact/com.nvidia.cuvs/cuvs-java), an open-source library developed by the community and maintained by NVIDIA. The cuvs-java library is lightweight and builds on the [cuVS C API](https://docs.rapids.ai/api/cuvs/nightly/c_api/) using [Panama](https://openjdk.org/projects/panama/) Foreign Function to expose cuVS features in an idiomatic Java way, while remaining modern and performant.

![How Elasticsearch works with NVIDIA cuVS, CPU and GPU indexing](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc7fd7361099da05a/6a17e920be608670af00477f/5f6daa1eb07f704a6707d9e6b7ccb81d0abaa8c9-566x419.png)

The cuvs-java library is integrated into a [new Elasticsearch plugin](https://github.com/elastic/elasticsearch/pull/135545); therefore, vector indexing on the GPU can occur on the same Elasticsearch node and process, without the need to provision any external code or hardware. During index building, if the cuVS library is installed and a GPU is present and configured, Elasticsearch will use the GPU to accelerate the vector indexing process. The vectors are given to the GPU, which constructs a [CAGRA](https://arxiv.org/abs/2308.15136) graph. This graph is then converted to the HNSW format, making it immediately available for vector search on the CPU. The final format of the built graph is the same as what would be built on the CPU; this allows Elasticsearch to leverage GPUs for high-throughput vector indexing when the underlying hardware supports it, while freeing CPU power for other tasks (concurrent search, data processing, etc.).

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt485f55f29d6df5c4/6a17e922be6086dcf3004785/3ea255bd9bfd7983f78143c5eba999d2149d72be-671x356.png)

## Index build acceleration

As part of integrating GPU acceleration into Elasticsearch, several enhancements were made to cuvs-java, focusing on efficient data input/output and function invocation. A key enhancement is the use of [cuVSMatrix](https://github.com/rapidsai/cuvs/blob/2cf5fa7666d703dccbe655f8214656b0952bb69b/java/cuvs-java/src/main/java/com/nvidia/cuvs/CuVSMatrix.java) to transparently model vectors, whether they reside on the Java heap, off-heap, or in GPU memory. This enables data to move efficiently between memory and the GPU, avoiding unnecessary copies of potentially billions of vectors.

Thanks to this underlying zero-copy abstraction, both transferring to GPU memory and retrieving the graph can occur directly. During indexing, vectors are first buffered in memory on the Java heap, then sent to the GPU to construct the CAGRA graph. The graph is subsequently retrieved from the GPU, converted into HNSW format, and persisted to disk.

At merge time, the vectors are already stored on disk, bypassing the Java heap entirely. Index files are memory-mapped, and data is transferred directly into GPU memory. The design also easily accommodates different bit-widths, such as float32 or int8, and naturally extends to other quantization schemes.

## Drumroll…so, how does it perform?

Before we get into the numbers, a bit of context is helpful. Segment merging in Elasticsearch typically runs automatically in the background during indexing, which makes it difficult to benchmark in isolation. To obtain reproducible results, we used force-merge to explicitly trigger segment merging in a controlled experiment. Since force-merge performs the same underlying merge operations as background merging, its performance serves as a useful indicator of expected improvements, even though the exact gains may differ in real-world indexing workloads.

Now, let’s see the numbers.

Our initial benchmark results are very promising. We ran the benchmark on an AWS `g6.4xlarge` instance with locally attached NVMe storage. A single node of Elasticsearch was configured to use the default, optimal number of indexing threads (8 - one for each physical core), and to disable [merge throttling](https://www.elastic.co/docs/reference/elasticsearch/index-settings/merge) (which is less applicable with fast NVMe disks).

For the dataset, we used 2.6 million vectors with 1,536 dimensions from the [OpenAI Rally vector track](https://github.com/elastic/rally-tracks/blob/master/openai_vector/README.md), encoded as [base64 strings](https://github.com/elastic/elasticsearch/pull/137072), and indexed as float32 *hnsw*. In all scenarios, the constructed graphs achieve recall levels of up to 95%. Here’s what we found:

* **Indexing Throughput:** By moving graph construction to the GPU during in-memory buffer flushes, we increase throughput by ~12x.
* **Force-merge:** After indexing completes, the GPU continues to accelerate segment merging, speeding up the force-merge phase by ~7x.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfea4ee13b5a3b10d/6a17e923e9ea879c6aa9c616/f60ea9ee5996e456f393ffd195ee7eada6e5a7c2-948x387.png)

* **CPU usage:** Offloading graph construction to the GPU significantly reduces both average and peak CPU utilization. The graphs below illustrate CPU usage during indexing and merging, highlighting how much lower it is when these operations run on the GPU. Lower CPU utilization during GPU indexing frees up CPU cycles that can be redirected to improve search performance.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt80ff9c53f9b6884a/6a17e925445de9ee4b4d0187/5e680a5fc41700a877f3d8b2e5ce18ebd3f37a0b-1600x562.png)

* **Recall:** Accuracy remains effectively the same between CPU and GPU runs, with the GPU-built graph reaching marginally higher recall.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5cbe084eca27b8e4/6a17e926faa913317093c8b7/48a2b7758606bd321712b7d8378cd2640e652a4e-1384x544.png)

## Comparing along another dimension: Price

The earlier comparison intentionally used identical hardware, with the only difference being whether the GPU was used during indexing. That setup is useful for isolating raw compute effects, but we can also look at the comparison from a cost perspective.

At roughly the same hourly price as the GPU-accelerated configuration, one can provision a CPU-only setup with approximately twice the comparable CPU and memory resources: 32 vCPUs (AMD EPYC) and 64 GB of RAM, allowing to double the number of indexing threads to 16.

To keep the comparison fair and consistent, we ran this CPU-only experiment on an AWS g6.8xlarge instance, with the GPU explicitly disabled. This allowed us to hold all other hardware characteristics constant while evaluating the cost–performance trade-off of GPU acceleration versus CPU-only indexing.

The more powerful CPU instance does show improved performance compared to the benchmarks in the above section, as you would expect. However, when we compare this more powerful CPU instance against the original GPU-accelerated results, the GPU still delivers substantial performance gains: **~5x** improvement in indexing throughput, and **~6x** in force merge, all while building graphs that achieve recall levels of up to **95%.**

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt94b5eb6f95ba307d/6a17e928abe0f255d4dfea35/8ffa58cae3ad175ef2932a351aeef4c34a1407b9-948x394.png)

## Conclusion

In end-to-end scenarios, GPU acceleration with NVIDIA cuVS delivers nearly a 12x improvement in indexing throughput and a 7x decrease in force-merge latency, with significantly lower CPU utilization. This shows that vector indexing and merge workloads benefit significantly from GPU acceleration. On a cost-adjusted comparison, GPU acceleration continues to yield substantial performance gains, with approximately 5x higher indexing throughput and 6x faster force-merge operations.

GPU-accelerated vector indexing is currently planned for Tech Preview in Elasticsearch 9.3, which is scheduled to be released early in 2026.

Stay tuned for more.

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