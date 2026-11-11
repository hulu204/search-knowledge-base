---
title: 'Bringing maximum-inner-product into Lucene'
company: Elastic
tag: 召回
date: 2023-09-01
url: https://www.elastic.co/search-labs/blog/lucene-bringing-maximum-inner-product-to-lucene
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Bringing maximum-inner-product into Lucene

Explore how we brought maximum-inner-product into Lucene and the investigations undertaken to ensure its support.

September 01, 2023

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

Currently Lucene restricts `dot_product` to be only used over normalized vectors. Normalization forces all [vector magnitudes](https://en.wikipedia.org/wiki/Magnitude_(mathematics)#Euclidean_vector_space) to equal one. While for many cases this is acceptable, it can cause relevancy issues for certain data sets. A prime example are embeddings built by [Cohere](https://cohere.com/). Their vectors use magnitudes to provide more relevant information.

So, why not allow non-normalized vectors in dot-product and thus enable maximum-inner-product? What's the big deal?

## Negative values and Lucene optimizations

Lucene requires non-negative scores, so that matching one more clause in a disjunctive query can only make the score greater, not lower. This is actually important for dynamic pruning optimizations such as [block-max WAND](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand), whose efficiency is largely defeated if some clauses may produce negative scores. How does this requirement affect non-normalized vectors?

In the normalized case, all vectors are on a unit sphere. This allows handling negative scores to be simple scaling.

![Normalized Vectors](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta9a1c9f6f1c8eebd/6a170da3cdacbf64197d2a61/b6ddddc9103479474c3bdb5f3b5d0ef0491fee7f-1179x1209.png)

Figure 1: Two opposite, two dimensional vectors in a 2d unit sphere (e.g. a unit circle). When calculating the dot-product here, the worst it can be is -1 = [1, 0] \* [-1, 0]. Lucene accounts for this by adding 1 to the result.

With vectors retaining their magnitude, the range of possible values is unknown.

![Normalized Vectors](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7fd8462a258df0ec/6a170da41949f744c8e7aaac/0a8549e941e3b4dec79905e00e22e04b38b469c7-1181x1209.png)

Figure 2: When calculating the dot-product for these vectors `[2, 2] \* [-5, -5] = -20`

To allow Lucene to utilize blockMax WAND with non-normalized vectors, we must scale the scores. This is a fairly simple solution. Lucene will scale non-normalize vectors with a simple piecewise function:

```
if (dotProduct < 0) {
  return 1 / (1 + -1 * dotProduct);
}
return dotProduct + 1;
```

Now all negative scores are between 0-1, and all positives are scaled above 1. This still ensures that higher values mean better matches and removes negative scores. Simple enough, but this is not the final hurdle.

## The triangle problem

Maximum-inner-product doesn't follow the same rules as of [simple euclidean spaces](https://en.wikipedia.org/wiki/Euclidean_space). The simple assumed knowledge of the [triangle inequality](https://en.wikipedia.org/wiki/Triangle_inequality) is abandoned. Unintuitively, a vector is no longer nearest to itself. This can be troubling. Lucene’s underlying index structure for vectors is Hierarchical Navigable Small World (HNSW). This being a graph based algorithm, it might rely on euclidean space assumptions. Or would exploring the graph be too slow in non-euclidean space?

Some research has indicated that a transformation into [euclidean space is required for fast search](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/XboxInnerProduct.pdf). Others have gone through the trouble of [updating their vector storage](https://blog.vespa.ai/announcing-maximum-inner-product-search/) enforcing transformations into euclidean space.

This caused us to pause and dig deep into some data. The key question is this: does HNSW provide good recall and latency with maximum-inner-product search? While the original [HNSW paper](https://arxiv.org/pdf/1603.09320.pdf) and [other published research](http://boytsov.info/pubs/thesis_boytsov.pdf) indicate that it does, we needed to do our due diligence.

## Experiments and results: Maximum-inner-product in Lucene

The experiments we ran were simple. All of the experiments are over real data sets or slightly modified real data sets. This is vital for benchmarking as modern neural networks create vectors that adhere to specific characteristics ([see discussion in section 7.8 of this paper](https://arxiv.org/pdf/1908.10396.pdf)). We measured latency (in milliseconds) vs. recall over non-normalized vectors. Comparing the numbers with the same measurements but with a euclidean space transformation. In each case, the vectors were indexed into Lucene’s HNSW implementation and we measured for 1000 iterations of queries. Three individual cases were considered for each dataset: data inserted ordered by magnitude (lesser to greater), data inserted in a random order, and data inserted in reverse order (greater to lesser).

Here are some results from real datasets from Cohere:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdc9124e9d7af66c7/6a170da6964cea0fde08bc2b/fa6bf1f0e464e451851ed7908667380a483b5135-584x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt03ff266c998cdce4/6a170da7a6c2b91514e7976a/52e75dbbe198a8056d08f8662142b08ffab0c4db-567x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt65657beeeed956be/6a170da9961e692765c4cf81/51078d18adcf84210f35d90707adb1995f355c19-567x455.png)

Figure 3: Here are results for the Cohere’s Multilingual model embedding wikipedia articles. [Available on HuggingFace](https://huggingface.co/datasets/Cohere/wikipedia-22-12-en-embeddings). The first 100k documents were indexed and tested.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt48432b4e04343333/6a170daad7c0226a86de6513/e523057ceebf2486c24d19ebe658cc60e5639f40-584x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt214c6271b30ce794/6a170dac0c4857558b01ab00/a6fc6e88eab58c7aae06112f8f3c76b3a7c5a6ae-576x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8dee458e653fa91b/6a170dada929cf2f06ae0a4b/c2ae57b774718a2fac28caa52856f4e93721748e-568x455.png)

Figure 4: This is a mixture of Cohere’s English and Japanese embeddings over wikipedia. [Both](https://huggingface.co/datasets/Cohere/wikipedia-22-12-en-embeddings) [datasets](https://huggingface.co/datasets/Cohere/wikipedia-22-12-ja-embeddings) are available on HuggingFace.

We also tested against some synthetic datasets to ensure our rigor. We created a data set with [e5-small-v2](https://huggingface.co/intfloat/e5-small-v2) and scaled the vector's magnitudes by different statistical distributions. For brevity, I will only show two distributions.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdb958e25ddae77b3/6a170dafcdacbf3ede7d2a65/17a816bbd822d9c5858404dd41ede97d0443367b-576x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf9304b614cc018cb/6a170db0b0367d8eec72bd9d/35a268e8960e17b9cf53b528103866620963ff86-567x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltca2fc7be8d1b91ea/6a170db2961e696745c4cf85/bacfeaa14a66dfb273252bb98ea57d43e1a6f371-567x455.png)

Figure 5: [Pareto distribution](https://en.wikipedia.org/wiki/Pareto_distribution) of magnitudes. A pareto distribution has a “fat tail” meaning there is a portion of the distribution with a much larger magnitude than others.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd9e1edcedab890ba/6a170db3a929cf2533ae0a4f/e6ac8465162648613ab0a52f65024080ebd7ef9f-590x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt82cbdf4ea437b3ca/6a170db5286714d80793e39b/afabc99bb1d885cb8330d494289c43f2b05d3518-577x455.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt62d6c0f2d8ac1106/6a170db6b339d546db76a044/f57f676230d4133810fd277bb20fbd762a7d32eb-577x455.png)

Figure 6: [Gamma distribution](https://en.wikipedia.org/wiki/Gamma_distribution) of magnitudes. This distribution can have high variance and makes it unique in our experiments.

In all our experiments, the only time where the transformation seemed warranted was the synthetic dataset created with the gamma distribution. Even then, the vectors must be inserted in reverse order, largest magnitudes first, to justify the transformation. These are exceptional cases.

If you want to read about all the experiments, and about all the mistakes and improvements along the way, here is the [Lucene Github issue](https://github.com/apache/lucene/issues/12342) with all the details (and mistakes along the way). Here’s one for open research and development!

## Conclusion

This has been quite a journey requiring many investigations to make sure maximum-inner-product can be supported in Lucene. We believe the data speaks for itself. No significant transformations required or significant changes to Lucene. All this work will soon unlock maximum-inner-product support with Elasticsearch and allow models like the ones provided by Cohere to be first class citizens in the Elastic Stack.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blteae4d50ff68aee45/6a17052114b270ecdde3c52d/119d3db739fcef08ffcb976e6d9d3bb0c204fb1f-1300x700.png)

[Lucene](/search-labs/blog/category/lucene)

### What happened in Lucene land in 2023?

January 12, 2024|[Adrien Grand](/search-labs/author/adrien-grand)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter