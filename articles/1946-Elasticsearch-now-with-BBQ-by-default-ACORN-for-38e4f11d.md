---
title: 'Elasticsearch now with BBQ by default & ACORN for filtered vector search'
company: Elastic
tag: 召回
date: 2025-07-29
url: https://www.elastic.co/search-labs/blog/elasticsearch-9-1-bbq-acorn-vector-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch now with BBQ by default & ACORN for filtered vector search

Explore how Elasticsearch's vector search now delivers better results faster, and at a lower cost.

July 29, 2025

[Gilad Gal](/search-labs/author/gilad-gal)

[Inside Elastic](/search-labs/blog/category/inside-elastic)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In the world of AI-powered search, three things matter above all else: query speed, ranking accuracy, and the cost of the resources required to achieve them. At Elastic, we're constantly pushing the boundaries on all three fronts. I'm excited to share two recent dense vector search improvements in Elasticsearch 9.1: a novel algorithm named ACORN for faster filtered vector search, and new evidence showing our default quantization method, BBQ, not only reduces costs but can actually improve ranking quality.

## ACORN: A smarter path to filtered search

Real-world search is rarely a simple "find me things like this." It’s "find me products like this *in my size*," or "find me documents similar to this one *from last quarter*." Even avoiding deleted documents is a filter, so in practice, filtered search is a very common scenario.

Making filtered vector search fast without compromising accuracy is a deep technical challenge. The HNSW algorithm is based on a graph search in which nodes represent vectors. The graphs are constructed during indexing and not per query. When supporting pre-filter, for accurate result sets, as Elasticsearch does, the naive method for filtered search is to traverse the graph and only collect nodes that pass the filter. The problem with that naive approach is that nodes are being evaluated even if they do not pass the filter in order to continue the search to their neighboring nodes and to the rest of the graph, resulting in a slower search. This phenomenon is significant in restrictive filters, when the majority of documents do not pass the filter. We had a partial solution for that even before, but we thought we could do better.

We chose to use the [ACORN-1](https://arxiv.org/abs/2403.04871) (ANN Constraint-Optimized Retrieval Network), a new algorithm described in an academic article published in 2024, for performing filtered k-Nearest Neighbor (kNN) search. ACORN works by integrating the filtering process directly into the HNSW graph traversal. With ACORN-1, only nodes that are accepted by the filter are evaluated, but to reduce the chances of missing relevant sections of the graph, the second-level neighbors, i.e., the neighbors of the neighbors, are also evaluated (if the filter accepts them). The implementation in Lucene used by Elasticsearch includes certain heuristics to further improve the results (detailed in [this blog](https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search)).

When choosing the specific algorithm and implementation, we explored other alternatives that have theoretical potential to even further improve latency, and decided not to pursue them because they force the user to declare prior to indexing the fields that will be used for filtering. We value the flexibility to define the filtering fields after documents are ingested because in real life indices evolve. The potential minor gain did not justify the loss of flexibility and we can gain the performance using other means, like BBQ (see below).

The results are a step-change in performance. We've measured typical speedups of **5x**, with some highly selective filters showing much higher improvement. This is a massive enhancement for the complex, real-world queries. All you need to do to benefit from ACORN-1 is to perform filtered vector queries in Elasticsearch.

## BBQ: The surprising superpower of better ranking

Reducing the memory footprint of vectors is crucial for building scalable, cost-effective AI systems. Our **Better Binary Quantization (BBQ)** method achieves this by compressing high-dimensional float vectors by a factor of ~32x. We've previously discussed how BBQ is superior to other techniques like Product Quantization in terms of recall, latency, and cost in our Search Labs blogs:

1. [Better Binary Quantization (BBQ) in Lucene and Elasticsearch](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch)
2. [How to implement Better Binary Quantization (BBQ) into your use case and why you should](https://www.elastic.co/search-labs/blog/bbq-implementation-into-use-case)
3. [Better Binary Quantization (BBQ) vs. Product Quantization](https://www.elastic.co/search-labs/blog/bit-vectors-elasticsearch-bbq-vs-pq)

The intuitive assumption, however, is that such a dramatic, lossy compression must come at the cost of ranking quality. Our recent extensive benchmark consistently shows we can completely compensate for that by exploring greater parts of the graph and reranking, and so achieve improvement not only in cost and performance, but also in relevance ranking.

BBQ isn't just a compression trick; it’s a sophisticated two-stage search process:

1. **Broad scan:** First, it uses the tiny, compressed vectors to rapidly scan the corpus and identify a set of top-ranking documents. The size of the set is bigger than the number of top-ranking documents that the user requests (oversampling).
2. **Precise reranking:** Then, it takes the top candidates from this initial scan and reranks them using their original, full-precision float32 vectors to determine the final order.

This process of oversampling and reranking acts as a powerful corrective, often finding highly relevant results that a pure float32 HNSW search, in its more limited traversal of the graph, might have missed.

## The proof is in the ranking

To measure this, we used **NDCG@10 (Normalized Discounted Cumulative Gain at 10)**, a standard metric that evaluates the quality of the top 10 search results. A higher NDCG score means more relevant documents are ranked higher. You can learn more about this in our [ranking evaluation API documentation](https://www.elastic.co/blog/made-to-measure-how-to-use-the-ranking-evaluation-api-in-elasticsearch).

We ran several benchmarks across 10 public datasets from the [BEIR](https://openreview.net/forum?id=wCu6T5xFjeJ) data sets, comparing traditional BM25 search, vector search with the e5-small model (float32 vectors), and vector search with the same model using BBQ. We chose e5-small because we know from previous benchmarks that BBQ is at its best with high vector dimensionality, so we wanted to benchmark it where it struggles, with rather low-dimensional vectors like e5-small produces. We measured using [NDCG](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)@10, which is a ranking quality metric that takes into account the order of the results. Below is a representative example of the results we saw.

| Data set | BM25 | e5-small float32 | e5-small BBQ with defaults |
| --- | --- | --- | --- |
| Climate-FEVER | 0.143 | 0.1998 | 0.2059 |
| DBPedia | 0.306 | 0.3143 | 0.3414 |
| FiQA-2018 | 0.251 | 0.3002 | 0.3136 |
| Natural Questions | 0.292 | 0.4899 | 0.5251 |
| NFCorpus | 0.321 | 0.2928 | 0.3067 |
| Quora | 0.808 | 0.8593 | 0.8765 |
| SCIDOCS | 0.155 | 0.1351 | 0.1381 |
| SciFact | 0.683 | 0.6569 | 0.677 |
| Touché-2020 | 0.337 | 0.2096 | 0.2089 |
| TREC-COVID | 0.615 | 0.7122 | 0.7189 |

![BM25, E5-SMALL float 32 and e5 samll bbq with defaults](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt90f5b59ccf1aecd2/6a170577a929cf3587ae0897/6c9b1965ad2774f483bf5d478fd1e3d87f84ab92-1200x742.png)

The results are stunning. **BBQ achieved better ranking quality than pure float32 search in 9 out of the 10 datasets**. Even in the single exception, the difference was negligible. Furthermore, BBQ was the top-performing method overall in 6 of the 10 sets. As a sidenote, often the best ranking is obtained by using a hybrid of BM25 and vector queries, plus other factors like distance, time, and popularity, and Elasticsearch excels in these types of queries.

One may ask how BBQ provides better ranking than float32, since BBQ is a lossy compression. Sure with BBQ we oversample and rerank by the float32 vector, but that shouldn’t matter, since conceptually, with float32, we rank all the documents using the float32 vectors. The answer is that with HNSW we only evaluate a smaller number of vectors per shard, which is defined in the parameter we call num\_candidates. The default num\_candidates when no quantization is performed is 1.5\*k, with k being the number of results returned to the user. You can read more about the benchmarks we performed to get to that default [here](https://www.elastic.co/search-labs/blog/simplifying-knn-search). When we are quantizing to BBQ, the comparison of vectors is faster and we can afford a larger num\_candidates while still reducing latency, so after some benchmarking work we set the default num\_candidates for BBQ to max(1.5\*k, oversample\*k).

For the benchmark above, that relies on our defaults, and in which k=10, we calculate num\_candidates as follows:

* Float32: 1.5\*k = 1.5\*10 = 15
* BBQ: max(1.5\*k, oversample\*k) = max(1.5\*10, 3\*10) = 30

Because of the difference in num\_candidates, we scan a greater part of the HNSW graphs when using BBQ and get better candidates in the top 30 that are reranked by float32, which explains how BBQ provides better ranking quality. You can set num\_candidates for your needs (e.g., see [here](https://www.elastic.co/search-labs/blog/elasticsearch-knn-and-num-candidates-strategies)), or, like most users, you can trust our benchmarks, and rely on the defaults.

This addresses a question I received from a consultant: "Is it better to use e5-large with BBQ or e5-small with float32?" The answer is now unequivocally clear. Using a more powerful model like e5-large with BBQ gives you the best of all worlds:

* Better ranking: From the superior e5-large model, further enhanced by BBQ.
* Lower latency: From the highly efficient BBQ search process.
* Lower cost: From the 32x memory reduction.

It’s a win-win-win, demonstrating that you don't have to trade quality for cost.

Because of this proven superiority, **we have made BBQ the default quantization method for dense vectors of 384 dimensions or higher** in Elasticsearch 9.1. We recommend this for most modern embedding models, which tend to distribute vectors well across the available space, making them ideal for BBQ's approach.

## Get started today

These advancements in ACORN and BBQ empower you to build more powerful, scalable, and cost-effective AI applications on Elastic. You can execute complex, filtered queries at high speed while simultaneously improving ranking relevance and dramatically reducing memory costs.

Upgrade to Elasticsearch 9.1 to take advantage of these new capabilities.

* Learn more about [kNN search](https://www.elastic.co/docs/solutions/search/vector/knn) and [vector quantization](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-quantization) in our documentation.
* [Dive deep into ranking quality with our Ranking Evaluation API](https://www.elastic.co/blog/made-to-measure-how-to-use-the-ranking-evaluation-api-in-elasticsearch)

We handle the complexity so you can focus on building incredible search experiences. Happy searching.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter