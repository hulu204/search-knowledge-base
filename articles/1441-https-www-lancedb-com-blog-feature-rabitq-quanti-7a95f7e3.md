---
title: 'https://www.lancedb.com/blog/feature-rabitq-quantization'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/feature-rabitq-quantization
account: 
origin: en-rss
---
# LanceDB's RaBitQ Quantization for Blazing Fast Vector Search

[David Myriel](/author/david-myriel)

[Yang Cen](/author/yang-cen)

•

September 17, 2025

•

[Engineering](/category/engineering)

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-001](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Most [embedding models](https://docs.lancedb.com/embedding/) give you float32 vectors. That is precise, but wasteful. You pay in storage and query time. Scalar quantization can shrink the size, but not enough. Binary quantization can shrink it further, but at the cost of quality.

Until now LanceDB has relied on **IVF\_PQ** (Inverted File with Product Quantization) as its default compression and search strategy. IVF\_PQ works well in many cases, but comes with trade-offs: building PQ codebooks is expensive, re-training is required when data distribution shifts, and distance estimation can be slow. Learn more about index types in [Indexing](https://docs.lancedb.com/indexing/).

Today we are adding **RaBitQ quantization** to LanceDB. You now have a choice. `IVF_PQ` remains the default, but RaBitQ is available when you need higher compression, faster indexing, and better recall in high dimensions. See how this fits into [vector search](https://docs.lancedb.com/search/vector-search/) and [hybrid search](https://docs.lancedb.com/hybrid-search/).

> A 1024-dimensional float32 vector needs 4 KB. With RaBitQ and corrective factors the same vector takes about 136 bytes.   
> `IVF_PQ` typically reduces this by 8–16x.

## Why this matters for you

High-dimensional vectors behave in ways that seem strange if you are used to 2D or 3D. In high dimensions almost every coordinate of a unit vector is close to zero. This is the **concentration of measure** phenomenon often discussed in [retrieval systems](https://docs.lancedb.com/search/optimize-queries/).

RaBitQ takes advantage of this. It stores only the binary "sign pattern" of each normalized vector and relies on the fact that the error introduced is bounded. The RaBitQ paper proves the estimation error is **O(1/√D)** (decreases proportionally to the inverse square root of dimensions), which is asymptotically optimal. In practice, the more dimensions your embeddings have, the more RaBitQ gives you for free.

> 💡 RaBitQ is most effective with embeddings of 512, 768, or 1024 dimensions. IVF\_PQ often struggles more as dimensionality grows, making RaBitQ a strong complement.

## What happens under the hood

When you index embeddings in LanceDB with RaBitQ your vectors are shifted around a centroid and normalized. They are snapped to the nearest vertex of a randomly rotated hypercube on the unit sphere. Each quantized vector is stored as **1 bit per dimension**. Index creation is managed the same way as other [vector indexes](https://docs.lancedb.com/indexing/vector-index/).

Two small corrective factors are also stored:

* the distance from the vector to the centroid
* the dot product between the vector and its quantized form

‍

At query time your input—whether text, image, audio, or video—is transformed in the same way. Comparisons become fast binary dot products, and the corrective factors restore fidelity.

Formally, RaBitQ maps a vector *v* to a binary vector (*vqb*) and a hypercube vertex (*vh*) on the unit sphere:

$$
v\_h[i] =
\begin{cases}
\frac{1}{\sqrt{D}} & \text{if } v\_{qb}[i] = 1 \\
-\frac{1}{\sqrt{D}} & \text{if } v\_{qb}[i] = 0
\end{cases}
$$

where *D* is the number of dimensions. Each component is either a positive or negative value scaled by the square root of dimensions.

To remove bias, RaBitQ samples a random orthogonal matrix *P* and sets the final quantized vector to:

$$
v\_q = P \times v\_h
$$

During indexing, for each data vector (v), we compute the residual around a centroid **c**, normalize it, map it to bits via the inverse rotation *P-1*, and store two corrective scalars alongside the bits:

* **Centroid distance**: 𝑑𝑐 =||⁢𝑣 −𝑐⁢||, which is the Euclidean distance from vector to centroid
* **Inner product**: 𝑑𝑠 =⟨𝑣𝑞,𝑣𝑛⟩, which is the dot product between quantized and normalized vectors

At search time, the query is processed with the same rotation to enable extremely fast binary dot products plus lightweight corrections for accurate distance estimates.

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-002](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-002.svg)

**Figure 1a:** 2D illustration of mapping a vector to the nearest unit‑sphere hypercube vertex (RabitQ overview)

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-003](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-003.png)

**Figure 1b:** Geometry of query and data vectors in RaBitQ

This figure shows the geometric relationship between a data vector *o*, its quantized form ¯𝑜, and a query vector *q*. The auxiliary vector e1 lies in the same plane. RaBitQ exploits the fact that in high-dimensional spaces, the projection of ¯𝑜 onto 𝑒1 is highly concentrated around zero (red region on the right). This allows us to treat it as negligible, enabling accurate distance estimation with minimal computation.

**Difference with IVF\_PQ**: PQ requires training a codebook and splitting vectors into subvectors. RaBitQ avoids that entirely. Indexing is faster, maintenance is simpler, and results are more stable when you update your dataset.

## Search in practice

With IVF\_PQ you first partition vectors into inverted lists, then run PQ-based comparisons inside each list. With RaBitQ the comparison step is even cheaper: a binary dot product plus small corrections. Both approaches benefit from [reranking](https://docs.lancedb.com/reranking/) with full-precision vectors.

Both approaches use a candidate set and re-ranking to ensure quality. But because RaBitQ's approximations are tight, you often need fewer candidates to hit the same recall.

For you this means recall above 95 percent with lower latency, even on large [multimodal datasets](https://lancedb.com/blog/multimodal-lakehouse/) on our test hardware.

> 💡 Always re-rank candidates with full precision vectors. IVF\_PQ and RaBitQ both rely on approximation for candidate generation.

## Research context: extended-RaBitQ

The [RaBitQ paper](https://arxiv.org/abs/2409.09913) also introduces **extended-RaBitQ**, a generalization to multi-bit quantization. Instead of limiting each coordinate to 1 bit, extended-RaBitQ allows for 2–4 bits per dimension. This reduces error further and can outperform product quantization under the same compression budget. For background on token-based search that pairs well with these methods, see [Full‑Text Search](https://docs.lancedb.com/search/full-text-search/).

⚠️ **extended-RaBitQ is not yet available in LanceDB.** We mention it here only as research context. It shows the trajectory of this work, and the same principles that make RaBitQ efficient at 1 bit can be extended to higher precision when needed.

## Benchmarks

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-004](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-004.png)

We tested IVF\_PQ and RaBitQ side by side on two public datasets:

* [**DBpedia 1M**](https://huggingface.co/datasets/KShivendu/dbpedia-entities-openai-1M) (OpenAI embeddings)
* [**GIST1M**](http://corpus-texmex.irisa.fr/) (dense 960-dimensional vectors)

The tests were run on a consumer-grade PC:

* CPU: Intel 12400F (6 cores, 12 threads)
* Disk: 1TB SSD
* No GPU

### DBpedia (text embeddings, 768d)

| Metric | IVF\_PQ | RaBitQ |
| --- | --- | --- |
| recall@10 | ~92% | **96%+** |
| throughput | ~350 QPS | **495 QPS** |
| index build time | ~85s | **~75s** |

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-005](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-005.png)

**Figure 2:** DBpedia benchmark results (recall@10, throughput, build time)

### GIST1M (image embeddings, 960d)

| Metric | IVF\_PQ | RaBitQ |
| --- | --- | --- |
| recall@10 | ~90% | **94%** |
| throughput | ~420 QPS | **540–765 QPS** |
| index build time | ~130s | **~21s** |

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-006](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-006.png)

**Figure 3:** GIST1M benchmark results (recall@10, throughput, build time)

> 💡 On CPUs, RaBitQ already outperforms IVF\_PQ on our test hardware. On GPUs the gap should widen further because RaBitQ operations are easier to parallelize.

## IVF\_PQ vs RaBitQ

When you use LanceDB today, the default quantization method is IVF\_PQ. It works well for many workloads and gives you solid compression and recall. With RaBitQ now available, you have another option. The two approaches make very different trade-offs, especially when your vectors are high-dimensional or multimodal.

| Feature | IVF\_PQ (default) | RaBitQ (new) |
| --- | --- | --- |
| **Compression ratio** | 8–16x typical | Up to 32x |
| **Index build time** | Slower, requires codebook training | Faster, no training needed |
| **Recall in high dimensions** | Good but drops with >512d | Stays high, error shrinks with more dimensions |
| **Query speed** | Good, but PQ distance estimation is slower | Faster, binary dot products dominate |
| **Update handling** | Requires re-training if distribution shifts | No retraining needed, robust to updates |
| **Best for** | General workloads, balanced compression | Large multimodal datasets, high-dim embeddings |

What this means in practice is that you don't have to pick one forever. IVF\_PQ remains a great default for balanced workloads. But if you are working with very large datasets, embeddings above 512 dimensions, or multimodal collections where precision matters, RaBitQ can give you higher recall, faster queries, and far smaller storage footprints. Because RaBitQ does not depend on heavy codebook training, you can also update your data more easily without re-training the index.

## What you can do today in LanceDB

With IVF\_PQ you already had scalable compression and fast ANN search. Now with RaBitQ you get an additional tool:

* Use **IVF\_PQ** for general-purpose workloads where codebooks make sense
* Use **RaBitQ** when you want maximum compression, faster indexing, or higher recall in high dimensions
* Mix RaBitQ-S with other modalities for adaptive precision control
* Keep more embeddings online for [**RAG**](https://docs.lancedb.com/) , multimodal search, and analytics

## Proven and ready

RaBitQ is not theoretical. Elastic integrated it into their BBQ quantization feature. Tensorchord built a cost-efficient vector search service with it. Both show strong improvements in recall and speed compared to classical product quantization.

Now RaBitQ is available in LanceDB alongside IVF\_PQ. You can choose the method that best fits your workload, and even switch as your dataset grows. If you're exploring LanceDB for the first time, check out our [quickstart](https://docs.lancedb.com/), the [WikiSearch demo](https://lancedb.com/blog/feature-full-text-search/), and how this ties into the [Multimodal Lakehouse](https://lancedb.com/blog/multimodal-lakehouse/).

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-007](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-007.jpg)

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-008](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-008.avif)

[David Myriel](/author/david-myriel)

Writer, Software Engineer

[GitHub](https://github.com/davidmyriel)[Linkedin](https://www.linkedin.com/in/davidmyriel/)[Twitter](https://x.com/davidmyriel)

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-009](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-009.png)

[Yang Cen](/author/yang-cen)

Software Engineer @ LanceDB

[GitHub](https://github.com/BubbleCal)

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-010](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-010.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-011](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-011.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3-fig-012](../images/1441-https-www-lancedb-com-blog-feature-rabitq-quanti-7a95f7e3/figure-012.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb