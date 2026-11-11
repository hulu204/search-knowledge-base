---
title: 'Optimized Scalar Quantization: Improving Better Binary Quantization (BBQ)'
company: Elastic
tag: 索引构建
date: 2025-01-06
url: https://www.elastic.co/search-labs/blog/optimized-scalar-quantization-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Optimized Scalar Quantization: Improving Better Binary Quantization (BBQ)

Here we explain optimized scalar quantization in Elasticsearch and how we used it to improve Better Binary Quantization (BBQ).

January 06, 2025

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Lucene](/search-labs/blog/category/lucene)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Our [Better Binary Quantization (BBQ)](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) indices are now even better(er). Recall improvements across the board (in extreme cases up to 20%) and unlocking the future of quantizing vectors to any bit size. As of Elasticsearch 8.18, BBQ indices are now backed by our state of the art [optimized scalar quantization algorithm.](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization)

## Scalar quantization history

Introduced in Elasticsearch 8.12, [scalar quantization](https://www.elastic.co/search-labs/blog/scalar-quantization-101) was initially a simple min/max quantization scheme. Per lucene segment, we would find the global quantile values for a given confidence interval. These quantiles are then used as the minimum and maximum to quantize all the vectors. While this naive quantization is powerful, it only really works for whole byte quantization.

![Scalar quantization: Static Confidence Intervals](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt61c68f220ef4af50/6a17d984445de975274cff84/874fc0d61224d74b705d43cf853c629636b8ba4b-1241x682.png)

Static confidence intervals mean static quantiles. This is calculated once for all vectors in a given segment and works well for higher bit values.

In Elasticsearch 8.15, we added [half-byte, or int4, quantization](https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene). To achieve this with high recall, we added an optimization step, allowing for the best quantiles to be calculated dynamically. Meaning, no more static confidence intervals. Lucene will calculate the best global upper and lower quantiles for each segment. Achieving 8x reduction in memory utilization over float32 vectors.

![Scalar quantization: reducing the vector similarity error](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt10282851a4739770/6a17d840033c8de7686bb011/1c8db6e93ab0296fbfa3fe090b5a259c99e52ecc-1000x500.gif)

Dynamically searching for the best quantiles to reduce the vector similarity error. This was done once, globally, over a sample set of the vectors and applied to all.

Finally, now in 8.18, we have added locally optimized scalar quantization. It optimizes quantiles per individual vector. Allowing for exceptional recall at any bit size, even single bit quantization.

## What is Optimized Scalar Quantization?

For an in-depth explanation of the math and intuition behind optimized scalar quantization, check out our blog post on [Optimized Scalar Quantization](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization). There are three main takeaways from this work:

* Each vector, is centered on the Apache Lucene segment's centroid. This allows us to make better use of the possible quantized vectors to represent the dataset as a whole.
* Every vector is individually quantized with a unique set of optimized quantiles.
* Asymmetric quantization is used allowing for higher recall with the same memory footprint.

In short, when quantizing each vector:

* We center the vector on the centroid
* Compute a limited number of iterations to find the optimal quantiles. Stopping early if the quantiles are unchanged or the error (loss) increases
* Pack the resulting quantized vectors
* Store the packed vector, its quantiles, the sum of its components, and an extra error correction term

![Optimization Steps: Scalar optimization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6cffd00a1c7ddd50/6a17dded3e03d718754f2b68/2f6d2e39b467161fc57a699d11ad92a108d6d117-1100x500.gif)

Here is a step by step view of optimizing 2 bit vectors. After the fourth iteration, we would normally stop the optimization process as the error (loss) increased. The first cell is each individual components error. The second is the distribution of 2 bit quantized vectors. Third is how the overall error is changing. Fourth is current step's quantiles overlayed of the raw vector being quantized.

## Storage and retrieval of optimized scalar quantization

The storage and retrieval of optimized scalar quantization vectors are similar to BBQ. The main difference is the particular values we store.

![Storage and retrieval of optimized scalar quantization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt62f545ce43f5f672/6a17ddee0b0bed123bdd34a6/ea543bbeeb2882ad80f205d7100b8367b0b26574-2585x332.png)

Stored for every binary quantized vector: dims/8 bytes, upper and lower quantiles, an additional correction term, the sum of the quantized components.

One piece of nuance is the correction term. For [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance), we store the [squared norm](https://en.wikipedia.org/wiki/Norm_(mathematics)) of the centered vector. For [dot product](https://en.wikipedia.org/wiki/Dot_product) we store the dot product between the centroid and the uncentered vector.

## Performance

Enough talk. Here are the results from four datasets.

* [Cohere's 768 dimensioned](https://huggingface.co/datasets/Cohere/wikipedia-22-12-simple-embeddings) multi-lingual embeddings. This is a well distributed inner-product dataset.
* [Cohere's 1024 dimensioned](https://huggingface.co/datasets/Cohere/wikipedia-2023-11-embed-multilingual-v3) multi-lingual embeddings. This embedding model is well optimized for quantization.
* [E5-Small-v2](https://huggingface.co/intfloat/e5-small-v2) quantized over the [quora](https://www.kaggle.com/c/quora-question-pairs) dataset. This model typically does poorly with binary quantization.
* [GIST-1M](https://corpus-texmex.irisa.fr/) dataset. This scientific dataset opens some interesting edge cases for inner-product and quantization.

Here are the results for *Recall@10|50*

| Dataset | BBQ | BBQ with OSQ | Improvement |
| --- | --- | --- | --- |
| Cohere 768 | 0.933 | 0.938 | 0.5% |
| Cohere 1024 | 0.932 | 0.945 | 1.3% |
| E5-Small-v2 | 0.972 | 0.975 | 0.3% |
| GIST-1M | 0.740 | 0.989 | 24.9% |

Across the board, we see that BBQ backed by our new optimized scalar quantization improves recall, and dramatically so for the GIST-1M dataset.

But, what about indexing times? Surely all this per vector optimizations must add up. The answer is no.

Here are the indexing times for the same datasets.

| Dataset | BBQ | BBQ with OSQ | Difference |
| --- | --- | --- | --- |
| Cohere 768 | 368.62s | 372.95s | +1% |
| Cohere 1024 | 307.09s | 314.08s | +2% |
| E5-Small-v2 | 227.37s | 229.83s | < +1% |
| GIST-1M | 1300.03s\* | 297.13s | -300% |

* Since the quantization methodology works so poorly over GIST-1M when using inner-product, it takes an exceptionally long time to build the HNSW graph as the vector distances are not well distinguished.

## Conclusion

Not only does this new, state of the art quantization methodology improve recall for our BBQ indices, it unlocks future optimizations. We can now quantize vectors to any bit size and we want to explore how to provide 2 bit quantization, striking a balance between memory utilization and recall with no reranking.

### Frequently Asked Questions

#### What is optized scalar quantization in Lucene?

Optimized scalar quantization in Lucene is a technique that reduces the memory footprint of vectors by quantizing them into smaller values.

#### What is optimized scalar quantization?

Optimized scalar quantization optimizes quantiles per individual vector. Allowing for exceptional recall at any bit size, even single bit quantization.

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