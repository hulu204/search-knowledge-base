---
title: 'Scalar Quantization of Dense Vectors in Apache Solr'
company: Sease
tag: 索引构建
date: 2026-01-02
url: https://sease.io/2026/01/scalar-quantization-of-dense-vectors-in-apache-solr.html
account: 
origin: harvest3-202607
---
In this blog post, we would like to introduce the concept of vector quantization, with a particular focus on **scalar vector quantization**, explaining what it is and why it is important.

We discuss a **recent contribution made** by [Kevin Liang](https://github.com/liangkaiwen) (a senior software engineer) to **Apache Solr**, which adds support for scalar vector quantization, and which we had the opportunity to review.

Finally, we explore how this new functionality can be leveraged within Solr, highlighting its key advantages.

*This feature is available starting from Apache Solr 10.0.0.*

If you’re interested in learning more about quantization techniques, we will also explore [**binary quantization**](https://sease.io/2026/01/binary-quantization-of-dense-vectors-in-apache-solr.html) in a dedicated blog post.

## What Vector Quantization is

Vector quantization is a **data** **compression technique** used to represent high-dimensional vectors (like embeddings) with fewer bits, reducing both disk usage and memory footprint while trying to preserve as much information as possible.

Quantization is particularly useful when dealing with **memory constraints** or aiming to **reduce search latency**, i.e. in large-scale vector search. However, since it inevitably introduces information loss, it is crucial to **benchmark and evaluate** the trade-offs between **compression ratio, recall,** and **accuracy** to ensure that the performance gains justify the potential degradation in quality.

There are three main families of quantization approaches: [scalar](https://www.elastic.co/search-labs/blog/scalar-quantization-101), [binary](https://qdrant.tech/articles/binary-quantization/), and [product](https://inria.hal.science/inria-00514462v2/document). In this blog post, we focus on scalar quantization.

## What Scalar Quantization Is

Scalar quantization is a compression technique that **converts floating-point values into integers**.

Let’s imagine we have vectors with **float32** values. Each decimal number can represent more than 2 billion distinct values. If we need to save or process millions of these numbers, we need a lot of memory. A number in float32 format occupies 4 bytes, and since each byte contains 8 bits, this means that to represent a single number we need 4 blocks of 8 bits, i.e. a total of 32 bits.

Scalar quantization is a way to reduce the amount of memory needed by simplifying those numbers into more “compact” representations, for example by converting them to **8-bit integers** (or less), which take up four times less space. 8-bit integers have only **256 possible values (from -128 to 127 or from 0 to 255)**. So quantization “narrows” the range of numbers: it transforms a very fine scale into a rough scale, where different values end up in the same “bucket”.

The mathematical formula describing the process is as follows:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Screenshot-2025-10-09-alle-13.48.22.png?fit=287%2C94&ssl=1)

where **𝑞** is the quantized value (int8), **𝑥** is the original value (float32), **𝑠** is the scale factor, and **𝑧** is the zero point:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Screenshot-2025-10-09-alle-13.52.07.png?fit=694%2C102&ssl=1)

To understand how to compress values, we need to know the minimum and maximum values in our data because the **scale factor (𝑠)** is calculated by looking at the difference between the maximum and minimum values, and then dividing that space into 255 “steps”. ***NOTE***: 8 bits → 256 possible values but *255 is used instead of 256 because there are 255 intervals between two extremes, not 256 points — this is known as the [Fencepost error](https://en.wikipedia.org/wiki/Off-by-one_error).*

Once we have the scale factor, we also need to calculate the **zero point (𝑧)**, which helps align the range of floating-point numbers with the range of integers. In simple terms, we take the minimum value of the range, divide it by the scale factor, and change its sign; this “translates” the scale in the right direction so that the “real” value 0 is represented by the correct integer within the new scale. The result is an integer (after rounding) that indicates where the real zero lies within the int8 scale.

However, it is common for a dataset to include a few extreme values, called outliers, which are much larger or much smaller than most of the others. If these are also taken into account when calculating the minimum and maximum, the scale becomes too wide, and most of the central values, those that appear most often, end up concentrated in very few steps, losing precision. To avoid this, instead of taking the absolute minimum and maximum, so-called **quantiles** are used.   
A quantile indicates a threshold within which a certain percentage of the data falls. For example, using the **99th quantile** means focusing on the range that contains 99% of the most common values, ignoring the 1% of the most extreme outliers. This way, the scale better fits the actual data, and the 255 available steps are used more efficiently, distributing the values more evenly and maintaining more detail where it is really needed.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/Image-2025-10-21-at-12.09.27-PM.jpeg?fit=800%2C291&ssl=1)

Essentially, scalar quantization works like reducing the quality of an image: you go from a high-resolution photo to a lighter but still sharp one. You lose a little detail, but you gain a lot in speed and space.

## Apache Solr Implementation

*Available from Apache Solr 10.0*

Starting with Lucene 9.9, support for scalar quantized vectors has been introduced through:

* **`Lucene99ScalarQuantizedVectorsFormat`** – handles flat quantized storage, providing compression and encoding of vector data.
 * **`Lucene99HnswScalarQuantizedVectorsFormat`** – builds on top of that quantized format by adding an HNSW index to enable approximate nearest neighbour (ANN) search.

Since vector quantization is a key optimisation for large-scale vector search, and given that other search engines such as OpenSearch and Elasticsearch have already introduced similar capabilities, bridging this gap in **Apache Solr** was essential. Finally, with the **upcoming Solr version 10, this support will be officially available** ([PR #3385](https://github.com/apache/solr/pull/3385)).

*Thanks again to Kevin Liang for his effort, as well as to [Alessandro Benedetti](https://www.linkedin.com/in/alexbenedetti/) and [David Smiley](https://www.linkedin.com/in/davidwsmiley/) for their review.*

A new schema field type, **`ScalarQuantizedDenseVectorField`**, has been introduced, extending the existing `DenseVectorField` functionality.  
This field type enables **scalar quantization** for vector data and builds **quantized HNSW indexes** using Lucene’s `Lucene99HnswScalarQuantizedVectorsFormat`.

The `SchemaCodecFactory` has been updated to delegate `KnnVectorsFormat` creation of the field type implementation. When the field type is `ScalarQuantizedDenseVectorField`, this delegation results in the use of the `Lucene99HnswScalarQuantizedVectorsFormat`, enabling quantized HNSW indexing and search.

The new type provides configurable parameters for quantization:

* **`bits`** – number of bits used for quantization (4 or 7, as defined by the Lucene codec specification).
 * **`confidenceInterval`** – fixed or dynamically computed confidence interval controlling quantization precision. Default is calculated as `1-1/(vector_dimensions + 1)`.
 * **`compress`** – flag enabling pairwise compression, providing a 50% reduction in memory usage (when using 4-bit quantization).

### How To Use the Scalar Vector Quantization

Here is how a `ScalarQuantizedDenseVectorField` field should be configured in the Solr schema.xml:

```
				
					&lt;fieldType name="scalar_quantized_vector" class="solr.ScalarQuantizedDenseVectorField" vectorDimension="4" similarityFunction="cosine"/&gt;

&lt;field name="vector" type="scalar_quantized_vector" indexed="true" stored="true"/&gt;
				
			
```

This represents the simplest possible configuration, which uses all default parameters.  
In addition to sharing the same parameters as `DenseVectorField`, this field type also provides the following optional, type-specific attributes that can be customised as needed:

|  |  |  |  |
| --- | --- | --- | --- |
| **Parameter Name** | **Default** | **Description** | **Accepted Values** |
| *`bits`* | 7 | The number of bits to use for each quantized dimension value | 4 (half byte) or 7 |
| `confidenceInterval` | dimension-scaled:  1-1/(vector\_dimensions + 1) | Defines the fixed range of vector values used during scalar quantization. It determines how much of the data distribution is preserved — for example, `0.95` means 95% of the values are mapped within the quantization range, ignoring the extreme outliers.  When `null`, it is automatically derived from the vector dimension (1-1/(vector\_dimensions + 1))  When `0`, it is determined dynamically for optimal accuracy. See *`dynamicConfidenceInterval`* | FLOAT32: within 0.9 and 1.0 |
| *`dynamicConfidenceInterval`* | false | If set to true, the `confidenceInterval` will be determined dynamically, selecting the value that minimizes quantization error.  `NOTE: when enabled, any value specified for confidenceInterval is ignored (overridden).` | true/false |
| *`compress`* | false | If set to true, this will further pack multiple dimension values within a one-byte alignment. This further decreases the quantized vector disk storage size by 50% at some decode penalty. This does not affect the raw vector, which is always preserved when `stored` is true.  `NOTE: this can only be enabled when bits=4` | true/false |

### Key Advantages

Scalar quantization drastically reduces **memory** requirements. By converting, for example, vectors from `float32` to 8-bit integers, memory usage can be reduced by up to **4×**, allowing massive embedding datasets to fit in significantly less memory, which is especially beneficial when indexing hundreds of millions of vectors. As shown in [this blog post by Snowflake](https://medium.com/snowflake/the-art-of-efficient-search-scalar-quantization-and-vectors-f912fd2e9bb7), quantizing **1M 768-dimensional embeddings** reduced the index size from **3 GB to 0.77 GB**.

As a result, vector search becomes **more resource-efficient** and delivers **faster performance** with only a negligible loss in accuracy. As shown in [this blog post by Snowflake](https://medium.com/snowflake/the-art-of-efficient-search-scalar-quantization-and-vectors-f912fd2e9bb7), it was observed that the impact of quantization on result quality was minimal, **less than 0.4% NDCG@10** difference compared to full-precision vectors.

**N.B.**  
As highlighted in the Lucene PR discussion ([#12582](https://github.com/apache/lucene/pull/12582)) and in this [blog post](https://www.elastic.co/search-labs/blog/scalar-quantization-in-lucene), the **raw float vectors** **are kept alongside the quantized ones**. This means that **disk usage increases**, since the index must store *both representations (raw + quantised*).

What actually decreases is the off-heap memory footprint: during vector search, the HNSW graph loads only the quantized vectors, while the raw vectors are never brought into memory for HNSW search. They are only used when explicitly needed — for example, for a brute-force secondary rescore or for re-quantization during segment merges.

I hope you enjoyed this blog post and found it useful. Stay tuned for new interesting topics and insights!

## Need Help with this topic?​

If you're struggling with Scalar Vector Quantization, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with Scalar Vector Quantization, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)