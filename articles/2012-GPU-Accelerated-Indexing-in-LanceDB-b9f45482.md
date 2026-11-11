---
title: 'GPU-Accelerated Indexing in LanceDB'
company: LanceDB
tag: 索引构建
date: 2023-11-02
url: https://www.lancedb.com/blog/gpu-accelerated-indexing-in-lancedb-27558fa7eee5
account: 
origin: harvest3-202607
---
# GPU-Accelerated Indexing in LanceDB

[LanceDB](/author/lancedb)

•

November 2, 2023

•

[Engineering](/category/engineering)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca0d08c858201c3b081a40_preview-image.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Vector databases are extremely useful for RAG, RecSys, computer vision, and a whole host of other ML/AI applications. Because of the rise of LLMs, there has been a lot of focus on vector indices, query latency, as well as the tradeoffs between latency and recall of various indices. What’s often neglected is the time it takes to *build* a vector index. Building a vector index is a very computationally intensive process that increases quadratically with the number of vectors or vector dimensions. As you scale up in production, this becomes a much bigger bottleneck for your AI stack.

Over the past few months, we’ve made some pretty amazing improvements using CPUs to build vector indices. And now we’re making a much bigger leap by supporting GPU acceleration for index building. So if you have access to an Nvidia GPU or a Macbook that supports [MPS](https://developer.apple.com/documentation/metalperformanceshaders), you can now take advantage of the unparalleled computing power of GPUs when training large scale vector indices.

## Training vector indices is expensive

Common indexing techniques like IVF (InVerted File index) or compression like PQ (Product Quantization) divide up the vectors into clusters. To find the cluster centroids, we have to use KMeans. While there are various techniques to improve the performance of KMeans, at the end of the day, it scales quadratically. This means that index training time quickly becomes prohibitively expensive at high scale.

The KMeans training algorithm is an iterative process where a ton of vector distance computations are performed to minimize the distance of vectors to their assigned clusters. It turns out that GPUs are amazingly good at this kind of math. Indexing libraries like FAISS, for example, support GPU-accelerated index training, but most vector databases have yet to add GPU support (and certainly haven’t made it easy).

## LanceDB support for GPU-acceleration

Since the beginning of LanceDB, users managing embeddings at scale have asked for GPU-acceleration to speed up their index training. In the most recent release of the Python package of LanceDB (v0.3.3), backed by Lance (v0.8.10), you can now use either CUDA or MPS by simply specifying the “accelerator” parameter when calling `create_index` :

> ***Using a GPU in LanceDB is as simple as specifying the accelerator parameter on create\_index().***

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca2270b15179c81d8d1c80_1_lZQRY7ed3FDGw-h3Sd1rTg.avif)

Creating index using Nvidia GPU (cuda)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca22914e74a9eed8cf9ab0_1_ANrOLSEGd2XXy5vv5h1_WQ.avif)

Creating Index using Apple Silicon GPU (mps)

Under the hood, LanceDB uses [PyTorch](https://pytorch.org/) to train the IVF clusters, and passes the kmeans centroids to the Rust core for index serialization. Thanks to the high-quality support of Cuda and [MPS](https://pytorch.org/docs/stable/notes/mps.html) from the PyTorch community, it allows us to quickly deliver on two of the most popular developer platforms (Linux and Mac). Combined with other recent improvements in the LanceDB indexing process, for instance, out-of-memory shuffling, batched KMeans training in GPU, LanceDB can reliably train over tens of millions vectors without worrying about CPU or GPU Out of Memory (OOM).

💡 Make sure you have pytorch installed (with CUDA if applicable) to use GPU-acceleration in LanceDB.

## Results

To benchmark the performance improvement for KMeans training, we trained IVF\_4096 (4096 clusters) using L2 euclidean distance on a 1-million vector dataset with OpenAI Ada2 embeddings (1536D). This was done on Linux and also on MacOS:

* Google Cloud \*\*g2-standard-32 \*\*instance, 32 logical cores, and 1 x Nvidia L4 GPU, Ubuntu 22.04, nvidia-driver-525
* Apple M2 Max Macbook Pro 14’, with 64GB RAM, 30 GPU cores.

In general, GPU acceleration offers up to 20–26x speed up compared to their CPU counterparts:

* Linux VM: 323s on CPU, and 12.5s on GPU
* Macbook Pro: 397s on CPU, and 21s on GPU

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca22d03502c6960fe5bb32_1_9tRrnjLVnasYS1E9d1PRvA.avif)

IVF 4096 on 1 Million 1536D vectors. BLUE is CPU; RED is GPU.

## What’s next

Currently the IVF KMeans training is only one part of the whole index training process. We’re going to be working to add GPU acceleration for PQ training and also assigning the vectors to the correct centroids. Once this is completed, you’ll see even more drastic improvements in end-to-end index training time.

In addition, PyTorch offers LanceDB an easy path for large-scale distributed GPU training, as well as access to even more hardware accelerators (i.e., TPU via XLA) in the future. Imagine being able to train a vector index in minutes on billions of vectors, on any hardware.

Finally, now that we have a mechanism to use the GPU effectively, we could also use it for inference down the road.

## Try it out!

You can start to leverage CUDA and Apple Silicon GPU support today via `pip install lancedb`. If you found this useful or interesting, please show us some love by starring [LanceDB](http://github.com/lancedb/lancedb) and the [Lance format](http://github.com/lancedb/lance).

And if you’re looking for a highly scalable, hosted vector database, check out our enterprise offering at [lancedb.com](https://lancedb.com/)!

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c2da55256db3a1ce1175fc_lancedb.jpeg)

[LanceDB](/author/lancedb)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a567183dd1ae093c21b81d5_opt3.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a50fef0022a597f28313428_hero%20img.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a510da7aa738b84d6e9c040_preview-image.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb