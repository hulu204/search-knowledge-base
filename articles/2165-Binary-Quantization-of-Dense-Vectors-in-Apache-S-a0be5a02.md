---
title: 'Binary Quantization of Dense Vectors in Apache Solr'
company: Sease
tag: 索引构建
date: 2026-01-12
url: https://sease.io/2026/01/binary-quantization-of-dense-vectors-in-apache-solr.html
account: 
origin: harvest3-202607
---
In this blog post, we would like to introduce the concept of vector quantization, with a particular focus on **binary vector quantization**, explaining what it is and why it is important.

We discuss a **recent contribution made** by [Kevin Liang](https://github.com/liangkaiwen) (a senior software engineer) to **Apache Solr**, which adds support for scalar vector quantization, and which we had the opportunity to review.

Finally, we explore how this new functionality can be leveraged within Solr, highlighting its key advantages and the scenarios where it can provide tangible benefits in real-world applications.

*This feature is available starting from Apache Solr 10.0.0.*

If you’re interested in learning more about quantization techniques, we explored [**scalar quantization**](https://sease.io/2026/01/scalar-quantization-of-dense-vectors-in-apache-solr.html) in a dedicated blog post.

## What Vector Quantization is

Vector quantization is a **data** **compression technique** used to represent high-dimensional vectors (like embeddings) with fewer bits, reducing both disk usage and memory footprint while trying to preserve as much information as possible.

Quantization is particularly useful when dealing with **memory constraints** or aiming to **reduce search latency**, i.e. in large-scale vector search. However, since it inevitably introduces information loss, it is crucial to **benchmark and evaluate** the trade-offs between **compression ratio, recall,** and **accuracy** to ensure that the performance gains justify the potential degradation in quality.

There are three main families of quantization approaches: [scalar](https://www.elastic.co/search-labs/blog/scalar-quantization-101), [binary](https://qdrant.tech/articles/binary-quantization/), and [product](https://inria.hal.science/inria-00514462v2/document). In this blog post, we will focus on binary quantization.

## What Binary Quantization is

Binary quantization is an extreme case of scalar quantization, a compression technique that converts floating-point values into integers, but with **only two levels**, i.e., binary (or boolean) values. This approach is able to reduce the in-memory representation of each vector dimension from a 32-bit float down to a single bit.

A simple way to perform a binarization is to assign the value 1 to all numbers greater than zero and 0 to those that are zero or less. A more refined, yet still naive, approach to binarization involves determining a threshold (for instance, the *median* value) for each dimension across the dataset. Each element of a vector is then encoded as 1 if its value exceeds the threshold, or as 0 otherwise.

When dealing with binary vectors, similarity is often measured using the [Hamming distance](https://en.wikipedia.org/wiki/Hamming_distance), a simple and efficient way which counts the number of differing bits between two vectors.  
Two vectors have a high similarity if their Hamming distance is small, meaning that most of their bits share the same value, while a larger distance indicates lower similarity.

Binary quantization facilitates faster data indexing and searching, because boolean operations are very fast and require significantly fewer CPU instructions. On the other side, this extreme compression comes at the cost of precision, which may adversely affect recall.  
To mitigate part of this information loss, the paper by **Gao and Long** proposes the **[RaBitQ](https://arxiv.org/pdf/2405.12497)** technique, which quantizes high-dimensional vectors into bit strings, while introducing a *theoretical error bound* on distance estimations that guarantees controlled degradation in accuracy.  
Although the quantization algorithm is computationally more expensive, most of this cost can be handled during the offline preprocessing stage. As a result, the trade-off becomes acceptable, as RaBitQ achieve memory and storage reduction while maintaining high recall, as demonstrated by the experimental results presented in the paper.   
If you’re curious to learn more about RaBitQ, I encourage you to read their [blog post](https://dev.to/gaoj0017/extended-rabitq-an-optimized-scalar-quantization-method-83m) about Extended RaBitQ as well as the original paper.

### Apache Lucene Implementation

Starting with Lucene 10.2, support for binary quantized vectors has been introduced through:  
– **`Lucene102BinaryQuantizedVectorsFormat`**  
– **`Lucene102HnswBinaryQuantizedVectorsFormat`**

The binary quantization implementation in Apache Lucene builds upon ideas from the

previous work on globally optimized scalar quantization in Apache Lucene itself and two papers:

* [Similarity search in the blink of an eye with compressed indices](https://arxiv.org/pdf/2304.04759) by Cecilia Aguerrebere et al. – *Locally-adaptive Vector Quantization (LVQ)*.
 * [Accelerating Large-Scale Inference with Anisotropic Vector Quantization](https://arxiv.org/pdf/1908.10396) by Ruiqi Guo et al. – Scalable Nearest Neighbors (ScaNN) technique.

Additionally, the Lucene approach **follows the RaBitQ method**, with some differences in optimisation details, as discussed in [Lucene PR #14078](https://github.com/apache/lucene/pull/14078).

The resulting approach in Lucene is referred to as centroid-centered asymmetric quantization, or **Better Binary Quantization** (BBQ – refer to this [blog post](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) for more info). It combines three main concepts:

##### 1) Centroid-centered quantization

The distance between two vectors is estimated based on their centroid-centered distance**.**This means that each vector dimension is normalised relative to a precomputed centroid (the midpoint across all vectors in the index) and then **compressed to 1 bit per dimension**:

* If the vector value in a given dimension is greater than the centroid → **1**
 * If it is smaller → **0**

Alongside these binary codes, Lucene computes and stores **corrective factors** to improve the accuracy of distance estimation. The binary codes and per-vector correction factors are stored in the `.veb` (vector data) file, while the `.vemb` file stored metadata such as the number of vectors, dimensions, and file offsets information.

##### 2) Asymmetric quantization

At query time, the incoming floating-point query vector is centered on the same centroid but **quantized to 4 bits per dimension** (half-byte). In this way, the index vectors remain highly compressed (1 bit), while the query vector retains enough precision to maintain search quality.

The 4-bit query vector is then compared directly against the 1-bit quantized vectors in the index using **bitwise operations** (bit arithmetic), enabling very fast distance computation.  
Finally, the raw bitwise score is adjusted using the stored correction factors to approximate the target distance metric.

##### 3) Individually optimized scalar quantization (for quantiles)

In addition to the centroid and asymmetric design, Lucene introduces a further refinement.   
Rather than using a single, global quantization rule for all vectors, it optimizes the quantization intervals for each vector by adjusting the quantiles of the vector values centered on a provided centroid.  
The optimization process minimizes quantization loss using a coordinate descent algorithm. This per-vector quantile optimization enables high recall and accuracy, even at very low bit rates.

### Apache Solr Implementation

*Available from Apache Solr 10.0*

Since vector quantization is a key optimisation for large-scale vector search, and given that other search engines such as OpenSearch and Elasticsearch have already introduced similar capabilities, bridging this gap in **Apache Solr** was essential. Finally, with the **upcoming Solr version 10, this support will be officially available** ([PR #3468](https://github.com/apache/solr/pull/3468)).

*Thanks again to Kevin Liang for his effort, as well as to Alessandro Benedetti and Benjamin Trent for their review.*

A new schema field type, **`BinaryQuantizedDenseVectorField`**, has been introduced, extending the existing `DenseVectorField` functionality.  
This field type enables **binary quantization** for vector data and builds **quantized HNSW indexes** using Lucene’s `Lucene102HnswBinaryQuantizedVectorsFormat`.

##### How To Use It

Here is how a `BinaryQuantizedDenseVectorField` field should be configured in the Solr schema.xml:

```
				
					&lt;fieldType name="binary_quantized_vector" class="solr.BinaryQuantizedDenseVectorField" vectorDimension="4"/&gt;

&lt;field name="vector" type="binary_quantized_vector" indexed="true" stored="true"/&gt;
				
			
```

It represents the simplest possible configuration, which uses all default parameters.  
This field type accepts the same parameters as **DenseVectorField**, with the only exception of **similarityFunction** → since binary quantization relies on its own distance computation, this parameter is not required.   
No additional field-specific parameters are defined for this type.

##### When is it useful

Binary quantization is particularly useful in specific situations:

* **When dealing with huge datasets** — If you have millions or even billions of vectors, the search time and memory usage can become prohibitive when using 32-bit or 16-bit representations. Binary quantization drastically reduces memory consumption (~95% memory reduction while maintaining good quality) and makes similarity computations much faster through simple bitwise operations.
 * **When throughput matters more than precision** — If the goal is to retrieve “good enough” results very quickly rather than perfectly accurate ones, binary quantization is ideal.
 * **In resource-constrained environments** — In scenarios where computational and memory resources are constrained, binary quantization offers a practical solution to perform efficient search while minimizing hardware demands.

## Need Help With This Topic?​​

If you’re struggling with Solr, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)