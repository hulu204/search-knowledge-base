---
title: 'Optimizing scalar quantization with sparse preconditioners'
company: Elastic
tag: 索引构建
date: 2025-05-31
url: https://www.elastic.co/search-labs/blog/robust-optimized-scalar-quantization
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Optimizing scalar quantization with sparse preconditioners

We discuss a sparse preconditioner to apply to vectors which results in more stable quantization performance with respect to data distribution.

May 31, 2025

[Thomas Veasey](/search-labs/author/thomas-veasey)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Recently, we introduced [optimized scalar quantization](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization) (OSQ) and donated it to Lucene. This powers our implementation of binary quantization (BBQ). As we continue on our journey to make BBQ the default format for all our vector indices, we’ve been exploring its robustness across a wider range of data characteristics.

As we discussed before, many high quality learned embeddings share a similar characteristic: their components are normally distributed. However, classic approximate nearest neighbor (ANN) benchmark datasets often do not share this characteristic.

In this blog, we explore:

1. The distribution characteristics of a variety of classic ANN benchmark datasets,
2. How they perform with vanilla OSQ, and
3. The effect of a preconditioner on retrieval robustness.

We propose a sparse variant of the random orthogonal preconditioner introduced by [RaBitQ](https://arxiv.org/pdf/2405.12497), which achieves similar quality, but at a fraction of the cost.

#### Datasets

In this study we use a subset of the datasets included in the popular [ann-benchmark](https://github.com/erikbern/ann-benchmarks) suite:

1. GIST that contains 960 [handcrafted features](https://people.csail.mit.edu/torralba/code/spatialenvelope/) for image recognition
2. [MNIST](https://en.wikipedia.org/wiki/MNIST_database) and [Fashion-MNIST](https://github.com/zalandoresearch/fashion-mnist) that are 2828 images whose grayscale pixel values comprise the 784 dimensional vectors
3. [GloVe](https://en.wikipedia.org/wiki/GloVe) that comprises a collection of unsupervised word vector embeddings, and
4. SIFT that contains 128 [handcrafted image descriptors](https://en.wikipedia.org/wiki/Scale-invariant_feature_transform)

We also include some embedding model based datasets to understand the impact we have on these if any:

1. [e5-small](https://huggingface.co/intfloat/e5-small) embeddings of the quora duplicate question dataset
2. [Cohere v2](https://docs.cohere.com/v2/docs/cohere-embed) embedding of a portion of the wikipedia dataset

These have diverse characteristics. Some of their high-level features are summarized in the following table.

| Dataset | Dimension | Document count | Metric |
| --- | --- | --- | --- |
| GIST | 960 | 1000000 | Euclidean |
| MNIST | 784 | 60000 | Euclidean |
| Fashion-MNIST | 784 | 60000 | Euclidean |
| Glove | 100 | 1183514 | Cosine |
| SIFT | 128 | 1000000 | Euclidean |
| e5-small | 384 | 522931 | Cosine |
| Cohere v2 | 768 | 934024 | MIP |

The figures below show sample component distributions.

![Sample component distributions.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt348dcb15ff54137e/6a17f10de9ea87c916a9c6e4/278461a7124bc5ef1a8986ef2be5e370ef5638a6-1570x786.png)

### Preconditioning

[RaBitQ](https://arxiv.org/pdf/2405.12497) proposes random orthogonal preconditioning as an initial step for constructing quantized vectors. An orthogonal transformation of a vector corresponds to a change of basis. It is convenient in the context of quantization schemes because it doesn’t change the similarity metric. For example, for any orthogonal matrix P the dot product is unchanged since

(Px)t(Py)=xtPtPy=xtIy=xty(Px)^t(Py)=x^tP^tPy=x^tIy=x^ty(Px)t(Py)=xtPtPy=xtIy=xty

The same holds for cosine similarity and Euclidean distance. So the transform can just be applied to each vector before quantizing it and no further changes are needed to either the index or query procedure. For our purposes, another important property of this transformation is that it makes the component distributions more normally distributed. This is a consequence of the [central limit theorem](https://en.wikipedia.org/wiki/Central_limit_theorem). Specifically, the ithi^{\text{th}}ith component of the transformed vector corresponds to the summation ∑jPijxj\sum\_j P\_{ij} x\_j∑j​Pij​xj​ where PijP\_{ij}Pij​ are approximately independent random variables. It is easy to sample such a matrix: first sample d2d^2d2 elements independently from the standard normal distribution and then apply modified [Gram-Schmidt](https://en.wikipedia.org/wiki/Gram%E2%80%93Schmidt_process) orthogonalization to the resulting matrix (which is almost surely rank full). The figure below shows the impact of this transform on the component distribution when it’s applied to the Fashion-MNIST dataset.

![Fashion-MNIST component distribution and preconditioning example.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfb90aa313d5b9de8/6a17f10f7f6f1554b6c09c3a/0359b46042f72383ad8a1f824c7c3972ba03abbb-1986x746.png)

This property suits OSQ because our initialization procedure assumes that the components are normally distributed. The resulting transformation is effective, but it comes with some overheads:

1. The preconditioning matrix contains d2d^2d2 floating point values
2. Applying the transformation to the full dataset requires nd2nd^2 nd2floating point multiplications.

For example, if the vectors have 1024 dimensions, we’d require 4MB storage per preconditioning matrix and perform more than 1M multiplications per document we add to the index.

We therefore asked, “do we really need a dense orthogonal matrix to achieve our goal?” For high dimensional vectors we might reasonably expect that we can mix fewer components and still the resulting component distributions will be fairly normal. One way to achieve this is using a block diagonal matrix as illustrated schematically below.

![Using a block diagonal matrix for scalar quantization of vectors.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt79322b0cbc263ba4/6a17f110faa91327d693c980/aaf77ccbb0403c6825985b21351726f1d5235e21-1526x926.png)

If we use a block diagonal matrix whose blocks are 32×3232 \times 3232×32 we drop the memory requirement for a 102410241024 dimensional preconditioner to 4×32×32×(1024/32)/(1024×1024)=0.125MB4 \times 32 \times 32 \times (1024 / 32) / (1024 \times 1024)=0.125\text{MB}4×32×32×(1024/32)/(1024×1024)=0.125MB and we reduce the indexing overhead by a factor of 32. This is pretty appealing.

Although the vanilla block diagonal preconditioner performs fairly well, it gives up some of the recall gains we achieve with a dense preconditioner. Furthermore, the choice of a block diagonal matrix is arbitrary: it is mixing components that happen to be adjacent to each other in the vector. It seems undesirable that the effectiveness of our scheme might change for an arbitrary permutation of the input vectors. Ideally we would use a procedure which yields a deterministic choice for which components we mix.

To do this we drew inspiration from optimized product quantisation. This seeks to balance variance between groups of components used to build each codebook. In a similar vein, we use a greedy algorithm to assign components to blocks with the aim to balance their variance as follows.

`for` j∈{1,2,...,blocks}j \in \{1,2,...,\text{blocks} \}j∈{1,2,...,blocks}    vj←0\;\;v\_j \leftarrow 0vj​←0    bj←∅\;\;b\_j \leftarrow \emptysetbj​←∅

`while` i<di<di<d `in descending component variance order`    j←argmin⁡kvk\;\;j \leftarrow arg\min\_k v\_kj←argmink​vk​    \;\;`Add` iii `to` bjb\_jbj​    \;\;`if` ∣bj∣<dj\left| b\_j \right| < d\_j∣bj​∣<dj​        \;\;\;\;`Add the variance of the` ithi^{\text{th}}ith `component to` vjv\_jvj​    \;\;`else`        vj←∞\;\;\;\;v\_j \leftarrow \inftyvj​←∞

Here, ddd is the vector dimension and djd\_jdj​ is the jthj^{\text{th}}jth block dimension. Our intuition is that this should maximize the homogeneity of component distributions and that this is beneficial because we use the same quantization interval for each component. This intuition is borne out by the results. We achieve similar quality to the dense transformation at a fraction of the cost.

### Results

As is typical, we evaluate recall by reranking some collection of vectors larger than the number of required candidates. The following table breaks down the recall@10 at 5 distinct reranking depths for the most challenging vector distributions in our test set with and without preconditioning. It also compares dense preconditioning with the optimized block diagonal preconditioning we described above, using a block size of 32. Averaged across datasets and reranking depths we see an increase in recall of 31% using block diagonal preconditioning for these datasets compared to the baseline. It’s also clear that the block diagonal preconditioner with balanced variance is on a par with the dense preconditioner.

| Dataset | Metric | Baseline | Dense preconditioner | Sparse preconditioner |
| --- | --- | --- | --- | --- |
| Fashion-MNIST | recall@10|10 | 0.444 | 0.712 | 0.710 |
|  | recall@10|20 | 0.629 | 0.911 | 0.911 |
|  | recall@10|30 | 0.730 | 0.964 | 0.966 |
|  | recall@10|40 | 0.792 | 0.983 | 0.984 |
|  | recall@10|50 | 0.833 | 0.990 | 0.992 |
| MNIST | recall@10|10 | 0.544 | 0.795 | 0.787 |
|  | recall@10|20 | 0.719 | 0.970 | 0.967 |
|  | recall@10|30 | 0.800 | 0.994 | 0.993 |
|  | recall@10|40 | 0.848 | 0.998 | 0.998 |
|  | recall@10|50 | 0.880 | 0.999 | 0.999 |
| GIST | recall@10|10 | 0.314 | 0.558 | 0.545 |
|  | recall@10|20 | 0.438 | 0.746 | 0.739 |
|  | recall@10|30 | 0.521 | 0.837 | 0.825 |
|  | recall@10|40 | 0.581 | 0.884 | 0.878 |
|  | recall@10|50 | 0.625 | 0.916 | 0.911 |
| SIFT | recall@10|10 | 0.243 | 0.272 | 0.264 |
|  | recall@10|20 | 0.351 | 0.395 | 0.382 |
|  | recall@10|30 | 0.425 | 0.477 | 0.461 |
|  | recall@10|40 | 0.478 | 0.537 | 0.519 |
|  | recall@10|50 | 0.522 | 0.584 | 0.565 |

Recall @10 for various reranking depths using raw OSQ and preconditioned OSQ (higher is better)

For completeness we show the average recall@10 across the five reranking depths for the baseline and block diagonal preconditioning across all the test datasets in the figure below. This shows that preconditioning is essentially a no-op on well behaved datasets.

![Average recall@10 across the five reranking depths for the baseline and block diagonal preconditioning across all the test datasets.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0101d132392c7f7c/6a17f1127f6f15748bc09c3e/af7bc3c744510fd0ae30ed10305f13b66b60f2f7-982x630.png)

In summary, the block diagonal preconditioner increases robustness with modest overhead.

### Conclusion

Our SIMD accelerated binary quantization scheme has enabled us to achieve fantastic index efficiency and query recall-latency tradeoff. Our goal is to make this work easily consumable by everyone.

In this post we discussed a lightweight preconditioner we’re planning to introduce to the backing quantization scheme as we move towards enabling BBQ as the default format for all vector indices. This improves its robustness against pathological vector distributions for a small index time overhead.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0d6db072d62e8914/6a17e3b963baffa5b5741bcc/b00b0bb1c0197ee1b9b88885d4ffb68117e89dbc-962x450.png)

[ML Research](/search-labs/blog/category/ml-research)[Basics](/search-labs/blog/category/basics)

### Understanding optimized scalar quantization

December 19, 2024|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt04da2f4a75f879e7/6a17e3f86317309992585a18/60125a0e77fefce769db569472e1994a167487b2-1792x1024.jpg)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Smokin' fast BBQ with hardware accelerated SIMD instructions

December 04, 2024|[Chris Hegarty](/search-labs/author/chris-hegarty)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd76ada1eebfe05cd/6a1709d1a29299ed29d00ffb/796de4829e29566f1f3efa2482f5c3e54b31b1d6-1536x1024.png)

[Vector Database](/search-labs/blog/category/vector-database)

### Elasticsearch BBQ vs. OpenSearch FAISS: Vector search performance comparison

April 15, 2025|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt537d387cb7738d7f/6a17121dcdacbf5b4b7d2b1a/2356f6d43bbd976157addf019223b1a424cd6093-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Basics](/search-labs/blog/category/basics)

### Evaluating scalar quantization in Elasticsearch

May 03, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter