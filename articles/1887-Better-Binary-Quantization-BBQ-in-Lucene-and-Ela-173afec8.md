---
title: 'Better Binary Quantization (BBQ) in Lucene and Elasticsearch'
company: Elastic
tag: 索引构建
date: 2024-11-11
url: https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Better Binary Quantization (BBQ) in Lucene and Elasticsearch

How Better Binary Quantization (BBQ) works in Lucene and Elasticsearch.

November 11, 2024

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Lucene](/search-labs/blog/category/lucene)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Embedding models output float32 vectors, often too large for efficient processing and practical apps. Elasticsearch supports int8 scalar quantization to reduce vector size while preserving performance. Other methods reduce retrieval quality and are impractical for real world use. In Elasticsearch 8.16 and Lucene, we introduced Better Binary Quantization (BBQ), a new approach developed from insights drawn from a recent technique - dubbed “[RaBitQ](https://www.elastic.co/search-labs/blog/rabitq-explainer-101)” - proposed by researchers from Nanyang Technological University, Singapore.

BBQ is a leap forward in quantization for Lucene and Elasticsearch, reducing float32 dimensions to bits, delivering ~95% memory reduction while maintaining high ranking quality. BBQ outperforms traditional approaches like Product Quantization (PQ) in indexing speed (20-30x less quantization time), query speed (2-5x faster queries), with no additional loss in accuracy.

In this blog, we will explore BBQ in Lucene and Elasticsearch, focusing on recall, efficient bitwise operations, and optimized storage for fast, accurate vector search.

Note, there are differences in this implementation than the one proposed by the original RaBitQ authors. Mainly:

* Only a single centroid is used for simple integration with HNSW and faster indexing
* Because we don't randomly rotate the codebook we do not have the property that the estimator is unbiased over multiple invocations of the algorithm
* Rescoring is not dependent on the estimated quantization error
* Rescoring is not completed during graph index search and is instead reserved only after initial estimated vectors are calculated
* Dot product is fully implemented and supported. The original authors focused on Euclidean distance only. While support for dot product was hinted at, it was not fully considered, implemented, nor measured. Additionally, we support max-inner product, where the vector magnitude is important, so simple normalization just won't suffice.

## What does the "better" in Better Binary Quantization mean?

In Elasticsearch 8.16 and in Lucene, we have introduced what we call "Better Binary Quantization". Naive binary quantization is [exceptionally lossy](https://www.elastic.co/search-labs/blog/bit-vectors-in-elasticsearch#a-bit-of-error) and achieving adequate recall requires gathering 10x or 100x additional neighbors to rerank. This just doesn't cut it.

In comes Better Binary Quantization! Here are some of the significant differences between Better Binary Quantization and naive binary quantization:

* All vectors are normalized around a centroid. This unlocks some nice properties in quantization.
* Multiple error correction values are stored. Some of these corrections are for the centroid normalization, some are for the quantization.
* Asymmetric quantization. Here, while the vectors themselves are stored as single bit values, queries are only quantized down to int4. This significantly increases search quality at no additional cost in storage.
* Bit-wise operations for fast search. The query vectors are quantized and transformed in such a way that allows for efficient bit-wise operations.

## Indexing with Better Binary Quantization (BBQ)

Indexing is simple. Remember, [Lucene](https://lucene.apache.org/core/) builds individual read only segments. As vectors come in for a new segment the centroid is incrementally calculated. Then once the segment is flushed, each vector is normalized around the centroid and quantized.

Here is a small example:

v1=[0.56,0.85,0.53,0.25,0.46,0.01,0.63,0.73]c=[0.65,0.65,0.52,0.35,0.69,0.30,0.60,0.76]vc1′=v1−c=[−0.09,0.19,0.01,−0.10,−0.23,−0.38,−0.05,−0.03]bin(vc1′)={{1x>00otherwise:x∈vc1′}bin(vc1′)=[0,1,1,0,0,0,0,0]0b00000110=6v\_{1} = [0.56, 0.85, 0.53, 0.25, 0.46, 0.01 , 0.63, 0.73]
\newline
c = [0.65, 0.65, 0.52, 0.35, 0.69, 0.30, 0.60, 0.76]
\newline
v\_{c1}' = v\_{1} - c = [-0.09, 0.19, 0.01, -0.10, -0.23, -0.38, -0.05, -0.03]
\newline
bin(v\_{c1}') = \left\{ \begin{cases}
1 & x\gt 0 \\
0 & otherwise
\end{cases} : x \in v\_{c1}'\right\}
\newline
bin(v\_{c1}') = [0, 1, 1, 0, 0, 0, 0, 0]
\newline
0b00000110 = 6v1​=[0.56,0.85,0.53,0.25,0.46,0.01,0.63,0.73]c=[0.65,0.65,0.52,0.35,0.69,0.30,0.60,0.76]vc1′​=v1​−c=[−0.09,0.19,0.01,−0.10,−0.23,−0.38,−0.05,−0.03]bin(vc1′​)={{10​x>0otherwise​:x∈vc1′​}bin(vc1′​)=[0,1,1,0,0,0,0,0]0b00000110=6

![Elastic BBQ: Going bit](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte141d672f14ab17e/6a17dc4b25daab024a08a113/0f9ede0c6de3ce13a61a0ba1ac75d0436880ddb6-1922x831.png)

*When quantizing down to the bit level, 8 floating point values are transformed into a single 8bit byte.*

Then, each of the bits are packed into a byte and stored in the segment along with any error correction values required for the vector similarity chosen.

![Bit vector layout](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbfef4dfa1fc98b87/6a17dc4ce9ea8746a3a9c495/63fe9c85da31adb14bfebdfa5fb57133382244a9-1827x430.png)

*For each vector, bytes stored are* `dims/8` *number of bytes and then any error correction values; 2 floating point values for Euclidean, or 3 for dot product.*

## A quick side quest to talk about how we handle merging

When segments are merged, we can take advantage of the previously calculated centroids. Simply doing a weighted average of the centroids and then re-quantizing the vectors around the new centroid.

What gets tricky is ensuring [HNSW](https://arxiv.org/abs/1603.09320) graph quality and allowing the graph to be built with the quantized vectors. What's the point of quantizing if you still need all the memory to build the index?!

In addition to appending vectors to the existing largest HNSW graph, we need to ensure vector scoring can take advantage of asymmetric quantization. HNSW has multiple scoring steps: one for the initial collection of neighbors, and another for ensuring only diverse neighbors are connected. In order to efficiently use asymmetric quantization, we create a temporary file of all vectors quantized as 4bit query vectors.

So, as a vector is added to the graph we first:

* Get the already quantized query vector that is stored in the temporary file.
* Search the graph as normal using the already existing bit vectors.
* Once we have the neighbors, diversity and reverse-link scoring can be done with the previously int4 quantized values.

After the merge is complete, the temporary file is removed leaving only the bit quantized vectors.

![Elastic BBQ: Query vector layout](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltedaf59c08713f570/6a17dc4e445de99a4b4cffe1/5cfcf45c13b0c671097b03a74f3bc787ee476954-2146x432.png)

*The temporary file stores each query vector as an int4 byte array which takes* `dims/2` *number of bytes, some floating point error correction values (3 for Euclidean, 4 for dot product), and a short value for the sum of the vector dimensions.*

## Asymmetric quantization, the interesting bits

I have mentioned asymmetric quantization and how we lay out the queries for graph building. But, how are the vectors actually transformed? How does it work?

The "asymmetric" part is straight forward. We quantize the query vectors to a higher fidelity. So, doc values are bit quantized and query vectors are int4 quantized. What gets a bit more interesting is how these quantized vectors are transformed for fast queries.

Taking our example vector from above, we can quantize it to int4 centered around the centroid.

vc1′=v1−c=[−0.09,0.19,0.01,−0.10,−0.23,−0.38,−0.05,−0.03]maxvc1′=max(vc1′)=0.19,minvc1′=min(vc1′)=−0.38Q(xs)={(x−minvc1′)×15maxvc1′−minvc1′:x∈xs}Q(vc1′)={(x−(−0.38))×150.19−(−0.38):x∈vc1′}={(x+0.38)×26.32:x∈vc1′}=[8,15,10,7,4,0,9,9]v\_{c1}' = v\_{1} - c = [-0.09, 0.19, 0.01, -0.10, -0.23, -0.38, -0.05, -0.03]
\newline
max\_{v\_{c1}'}=max(v\_{c1}')=0.19,min\_{v\_{c1}'}=min(v\_{c1}')=-0.38
\newline
Q(x\_{s}) = \{(x-min\_{v\_{c1}'}) \times \frac{15}{max\_{v\_{c1}'} - min\_{v\_{c1}'}} : x \in x\_{s} \}
\newline
Q(v\_{c1}') = \{(x-(-0.38)) \times \frac{15}{0.19 -(-0.38)} : x \in v\_{c1}' \}
\newline
= \{(x + 0.38) \times 26.32 : x \in v\_{c1}' \}
\newline
= [8, 15, 10, 7, 4, 0, 9, 9]vc1′​=v1​−c=[−0.09,0.19,0.01,−0.10,−0.23,−0.38,−0.05,−0.03]maxvc1′​​=max(vc1′​)=0.19,minvc1′​​=min(vc1′​)=−0.38Q(xs​)={(x−minvc1′​​)×maxvc1′​​−minvc1′​​15​:x∈xs​}Q(vc1′​)={(x−(−0.38))×0.19−(−0.38)15​:x∈vc1′​}={(x+0.38)×26.32:x∈vc1′​}=[8,15,10,7,4,0,9,9]

With the quantized vector in hand, this is where the fun begins. So we can translate the vector comparisons to a bitwise dot product, the bits are shifted.

Its probably better to just visualize what is happening:

![Elastic BBQ: Bit pack int4 ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt589d74e8ad4bdf30/6a17dc50e8fbce95c13a17f7/cb5b6797a34e71fb655214aee8bcb501f8cff6a0-1694x855.png)

*Here, each int4 quantized value has its relative positional bits shifted to a single byte. Note how all the first bits are packed together first, then the second bits, and so on.*

But how does this actually translate to dot product? Remember, dot product is the sum of the component products. For the above example, let's write this fully out:

bin(vc1′)⋅Q(vc1′)=[0,1,1,0,0,0,0,0]⋅[8,15,10,7,4,0,9,9]=[0×8+1×15+1×10+0×7+0×4+0×0+0×9+0×9]=15+10=25bin(v\_{c1}') \cdot Q(v\_{c1}') = [0, 1, 1, 0, 0, 0, 0, 0] \cdot [8, 15, 10, 7, 4, 0, 9, 9]
\newline
= [0 \times 8 + 1 \times 15 + 1 \times 10 + 0 \times 7 + 0 \times 4 + 0 \times 0 + 0 \times 9 + 0 \times 9]
\newline
= 15 + 10 = 25bin(vc1′​)⋅Q(vc1′​)=[0,1,1,0,0,0,0,0]⋅[8,15,10,7,4,0,9,9]=[0×8+1×15+1×10+0×7+0×4+0×0+0×9+0×9]=15+10=25

We can see that its simply the summation of the query components where the stored vector bits are 1. And since all numbers are just bits, when expressed using a binary expansion, we can move things around a bit to take advantage of bitwise operations.

The bits that will be flipped after the &\&& will be the individual bits of the numbers that contribute to the dot product. In this case 15 and 10.

Remember our originally stored vectorstoredVecBits=bin(vc1′)=[0,1,1,0,0,0,0,0]We rotate the combine the bits resulting instoredVectBits=0b11000000The query vector, int4 quantizedQ(vc1′)=[8,15,10,7,4,0,9,9]The binary values of each dimensionbits(Q(vc1′))=[0b1000,0b1111,0b1010,0b0111,0b0100,0b0000,0b1001,0b1001]We shift the bits and align as shown in above visualizationqVecBits=align(bits(Q(vc1′)))=[0b11001010,0b00001110,0b00011010,0b11000111]qVecBits & storedVectBits={qVecBits & bits:bits∈storedVectBits}=[0b00000010,0b00000110,0000000010,0b0000110]\text{Remember our originally stored vector}
storedVecBits = bin(v\_{c1}') = [0, 1, 1, 0, 0, 0, 0, 0]
\newline
\text{We rotate the combine the bits resulting in}
\newline
storedVectBits = 0b11000000
\newline
\text{The query vector, int4 quantized}
\newline
Q(v\_{c1}') = [8, 15, 10, 7, 4, 0, 9, 9]
\newline
\text{The binary values of each dimension}
\newline
bits(Q(v\_{c1}')) = [0b\textcolor{lime}{1}\textcolor{red}{0}\textcolor{cyan}{0}\textcolor{orange}{0}, 0b\textcolor{lime}{1}\textcolor{red}{1}\textcolor{cyan}{1}\textcolor{orange}{1}, 0b\textcolor{lime}{1}\textcolor{red}{0}\textcolor{cyan}{1}\textcolor{orange}{0}, 0b\textcolor{lime}{0}\textcolor{red}{1}\textcolor{cyan}{1}\textcolor{orange}{1}, 0b\textcolor{lime}{0}\textcolor{red}{1}\textcolor{cyan}{0}\textcolor{orange}{0}, 0b\textcolor{lime}{0}\textcolor{red}{0}\textcolor{cyan}{0}\textcolor{orange}{0}, 0b\textcolor{lime}{1}\textcolor{red}{0}\textcolor{cyan}{0}\textcolor{orange}{1}, 0b\textcolor{lime}{1}\textcolor{red}{0}\textcolor{cyan}{0}\textcolor{orange}{1}]
\newline
\text{We shift the bits and align as shown in above visualization}
\newline
qVecBits = align(bits(Q(v\_{c1}'))) = [0b\textcolor{orange}{11001010}, 0b\textcolor{cyan}{00001110}, 0b\textcolor{red}{00011010}, 0b\textcolor{lime}{11000111}]
\newline
qVecBits \, \& \, storedVectBits = \{qVecBits \, \& \, bits : bits \in storedVectBits\}
\newline
= [0b00000010, 0b00000110, 0000000010, 0b0000110]Remember our originally stored vectorstoredVecBits=bin(vc1′​)=[0,1,1,0,0,0,0,0]We rotate the combine the bits resulting instoredVectBits=0b11000000The query vector, int4 quantizedQ(vc1′​)=[8,15,10,7,4,0,9,9]The binary values of each dimensionbits(Q(vc1′​))=[0b1000,0b1111,0b1010,0b0111,0b0100,0b0000,0b1001,0b1001]We shift the bits and align as shown in above visualizationqVecBits=align(bits(Q(vc1′​)))=[0b11001010,0b00001110,0b00011010,0b11000111]qVecBits&storedVectBits={qVecBits&bits:bits∈storedVectBits}=[0b00000010,0b00000110,0000000010,0b0000110]

Now we can count the bits, shift and sum back together. We can see that all the bits that are left over are the positional bits for 15 and 10.

=(bitCount(0b00000010)<<0)+(bitCount(0b00000110)<<1)+(bitCount(0b00000010)<<2)+(bitCount(0b0000110)<<3)=(1<<0)+(2<<1)+(1<<2)+(2<<3)=25 = (bitCount(0b00000010) << 0) + (bitCount(0b00000110) << 1) + (bitCount(0b00000010) << 2) + (bitCount(0b0000110) << 3)
\newline
= (1 << 0) + (2 << 1) + (1 << 2) + (2 << 3)
\newline
= 25=(bitCount(0b00000010)<<0)+(bitCount(0b00000110)<<1)+(bitCount(0b00000010)<<2)+(bitCount(0b0000110)<<3)=(1<<0)+(2<<1)+(1<<2)+(2<<3)=25

Same answer as summing the dimensions directly.

Here is the example but simplifed java code:

```
byte[] bits = new byte[]{6};
byte[] queryBits = new byte[]{202, 14, 26, 199};
for (int i = 0; i < 4; i++) {
  sum += Integer.bitCount(bits[0] & queryBits[i] & 0xFF) << i;
}
```

## Testing with BBQ: Alright, show me the numbers:

We have done extensive testing with BBQ both in Lucene and Elasticsearch directly. Here are some of the results:

### Lucene benchmarking

The benchmarking here is done over three datasets: [E5-small](https://huggingface.co/intfloat/e5-small), [CohereV3](https://huggingface.co/Cohere/Cohere-embed-english-v3.0), and [CohereV2](https://huggingface.co/Cohere/multilingual-22-12). Here, each element indicates recall@100 with oversampling by [1, 1.5, 2, 3, 4, 5].

#### E5-small

This is 500k vectors for E5-small built from the quora dataset.

| quantization | Index Time | Force Merge time | Mem Required |
| --- | --- | --- | --- |
| bbq | 161.84 | 42.37 | 57.6MB |
| 4 bit | 215.16 | 59.98 | 123.2MB |
| 7 bit | 267.13 | 89.99 | 219.6MB |
| raw | 249.26 | 77.81 | 793.5MB |

![Elastic BBQ: e5small bit 500k](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2e56385794b079e3/6a17dc51414c6495c0945058/fcd8d761454e038ba4cb2dc3350ed87039e58ce0-576x455.png)

*It's sort of mind blowing that we get recall of 74% with only a single bit precision. Since the number of dimensions are fewer, the BBQ distance calculation isn't that much faster than our optimized int4.*

#### CohereV3

This is 1M 1024 dimensional vectors, using the CohereV3 model.

| quantization | Index Time | Force Merge time | Mem Required |
| --- | --- | --- | --- |
| bbq | 338.97 | 342.61 | 208MB |
| 4 bit | 398.71 | 480.78 | 578MB |
| 7 bit | 437.63 | 744.12 | 1094MB |
| raw | 408.75 | 798.11 | 4162MB |

![Elastic BBQ: cohere v3 bit 1M](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt86a68a7dfd6916e0/6a17dc53e31791a7b32d56ed/49735ad943e87e67c3632ca16a09513eca2c395b-576x455.png)

*Here, 1bit quantization and HNSW gets above 90% recall with only 3x oversampling.*

#### CohereV2

This is 1M 768 dimensional vectors, using the CohereV2 model and max inner product similarity.

| quantization | Index Time | Force Merge time | Mem Required |
| --- | --- | --- | --- |
| bbq | 395.18 | 411.67 | 175.9MB |
| 4 bit | 463.43 | 573.63 | 439.7MB |
| 7 bit | 500.59 | 820.53 | 833.9MB |
| raw | 493.44 | 792.04 | 3132.8MB |

![Elastic BBQ: Cohere V2 bit 1M](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7e84613614ce0956/6a17dc54faa91339a893c755/25edcbf7cef0e67a22d7243f989c52f24a5ef1e6-576x455.png)

*It's really interesting to see how much BBQ and int4 are in lock-step with this benchmark. Its neat that BBQ can get such high recall with inner-product similarity with only 3x oversampling.*

### Larger scale Elasticsearch benchmarking

As referenced in [our](https://www.elastic.co/search-labs/blog/elasticsearch-vector-large-scale-part1) [larger](https://www.elastic.co/search-labs/blog/elasticsearch-vector-large-scale-part1) [scale vector search blog](https://www.elastic.co/search-labs/blog/elasticsearch-vector-large-scale-part1) we have a [rally track](https://github.com/elastic/rally-tracks/tree/master/msmarco-v2-vector) for larger scale vector search benchmarking.

This data set has 138M floating point vectors of 1024 dimensions. Without any quantization, this would require around 535 GB of memory with HNSW. With better-binary-quantization, the estimate drops to around 19GB.

For this test, we used a single 64GB node in Elastic cloud with the following track parameters:

```
{
        "mapping_type": "vectors-only",
        "vector_index_type": "bbq_hnsw",
        "number_of_shards": 2,
        "initial_indexing_bulk_indexing_clients": 12,
        "standalone_search_clients": 8,
        "aggressive_merge_policy": true,
        "search_ops": [[10, 20, 0], [10, 20, 20], [10, 50, 0], [10, 50, 20], [10, 50, 50], [10, 100, 0], [10, 100, 20], [10, 100, 50], [10, 100, 100], [10, 200, 0], [10, 200, 20], [10, 200, 50], [10, 200, 100], [10, 200, 200], [10, 500, 0], [10, 500, 20], [10, 500, 50],[10, 500, 100],[10, 500, 200],[10, 500, 500],[10, 1000, 0], [10, 1000, 20], [10, 1000, 50], [10, 1000, 100], [10, 1000, 200], [10, 1000, 500], [10, 1000, 1000]]
}
```

Important note, if you want to replicate, it will take significant time to download all the data and requires over 4TB of disk space. The reason for all the additional disk space is that this dataset also contains text fields, and you need diskspace for both the compressed files and their inflated size.

The parameters are as follows:

* `k` is the number of neighbors to search for
* `num_candidates` is the number of candidates used to explore per shard in HNSW
* `rerank` is the number of candidates to rerank, so we will gather that many values per shard, collect the total `rerank` size and then rescore the top `k` values with the raw float32 vectors.

For indexing time, it took around 12 hours. And instead of showing all the results, here are three interesting ones:

| k-num\_candidates-rerank | Avg Nodes Visited | % Of Best NDGC | Recall | Single Query Latency | Multi-Client QPS |
| --- | --- | --- | --- | --- | --- |
| knn-recall-10-100-50 | 36,079.801 | 90% | 70% | 18ms | 451.596 |
| knn-recall-10-20 | 15,915.211 | 78% | 45% | 9ms | 1,134.649 |
| knn-recall-10-1000-200 | 115,598.117 | 97% | 90% | 42.534ms | 167.806 |

This shows the importance of balancing recall, oversampling, reranking and latency. Obviously, each needs to be tuned for your specific use case, but considering this was impossible before and now we have 138M vectors in a single node, it's pretty cool.

## Conclusion

Thank you for taking a bit of time and reading about Better Binary Quantization. Originally being from Alabama and now living in South Carolina, BBQ already held a special place in my life. Now, I have more reason to love BBQ!

We will release this as tech-preview in 8.16, or in serverless right now. To use this, just set your [`dense_vector.index_type`](https://www.elastic.co/guide/en/elasticsearch/reference/8.16/dense-vector.html) [as](https://www.elastic.co/guide/en/elasticsearch/reference/8.16/dense-vector.html) [`bbq_hnsw`](https://www.elastic.co/guide/en/elasticsearch/reference/8.16/dense-vector.html) [or](https://www.elastic.co/guide/en/elasticsearch/reference/8.16/dense-vector.html) [`bbq_flat`](https://www.elastic.co/guide/en/elasticsearch/reference/8.16/dense-vector.html) in Elasticsearch.

### Frequently Asked Questions

#### What is Elastic BBQ?

BBQ (Better Binary Quantization) is a leap forward in quantization for Lucene and Elasticsearch, reducing float32 dimensions to bits, delivering ~95% memory reduction while maintaining high ranking quality.

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