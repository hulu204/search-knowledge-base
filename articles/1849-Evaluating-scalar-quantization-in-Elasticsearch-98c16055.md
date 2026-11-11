---
title: 'Evaluating scalar quantization in Elasticsearch'
company: Elastic
tag: 评测
date: 2024-05-03
url: https://www.elastic.co/search-labs/blog/evaluating-scalar-quantization
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Evaluating scalar quantization in Elasticsearch

Learn how scalar quantization can be used to reduce the memory footprint of vector embeddings in Elasticsearch through an experiment.

May 03, 2024

[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)[Thomas Veasey](/search-labs/author/thomas-veasey)

[ML Research](/search-labs/blog/category/ml-research)[Basics](/search-labs/blog/category/basics)

Jump to

Share

## Understanding scalar quantization in Elasticsearch

In 8.13 we introduced [scalar quantization to Elasticsearch](https://www.elastic.co/search-labs/blog/scalar-quantization-in-lucene). By using this feature an end-user can provide float vectors that are internally indexed as byte vectors while retaining the float vectors in the index for optional re-scoring. This means they can reduce their index memory requirement, which is its dominant cost, by a factor of four. At the moment this is an [opt-in feature](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html#dense-vector-quantization) feature, but we believe it constitutes a better trade off than indexing vectors as floats. In 8.14 we will switch to make this our default. However, before doing this we wanted a systematic evaluation of the quality impact.

## Experimentation: Evaluating scalar quantization

The multilingual E5-small is a small high quality multilingual passage embedding model that we offer out-of-the-box in Elasticsearch. It has two versions: one cross-platform version which runs on any hardware and one version which is optimized for CPU inference in the Elastic Stack (see [here](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-e5.html)). E5 represents a challenging case for automatic quantization because the vectors it produces have low angular variation and are relatively low dimension compared to state-of-the-art models. If we can achieve little to no damage enabling int8 quantization for this model we can be confident that it will work reliably.

The purpose of this experimentation is to estimate the effects of scalar-quantized kNN search as described [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#knn-search-quantized-example) across a broad range of retrieval tasks using this model. More specifically, our aim is to assess the performance degradation (if any) by switching from a full-precision to a quantized index.

## Overview of methodology

For the evaluation we relied upon BEIR and for each dataset that we considered we built a full precision and an int8-quantized index using the default hyperparameters (`m: 16`, `ef_construction: 100`). First, we experimented with the quantized (weights only) version of the multilingual E5-small model provided by Elastic [here](https://huggingface.co/elastic/multilingual-e5-small-optimized) with Table 1 presenting a summary of the nDCG@10 scores (`k:10`, `num_candidates:100`):

| Dataset | Full precision | Int8 quantization | Absolute difference | Relative difference |
| --- | --- | --- | --- | --- |
| Arguana | 0.37 | 0.362 | -0.008 | -2.16% |
| FiQA-2018 | 0.309 | 0.304 | -0.005 | -1.62% |
| NFCorpus | 0.302 | 0.297 | -0.005 | -1.66% |
| Quora | 0.876 | 0.875 | -0.001 | -0.11% |
| SCIDOCS | 0.135 | 0.132 | -0.003 | -2.22% |
| Scifact | 0.649 | 0.644 | -0.005 | -0.77% |
| TREC-COVID | 0.683 | 0.672 | -0.011 | -1.61% |
|  |  | Average | -0.005 | -1.05% |

**Table 1**: nDCG@10 scores for the full precision and int8 quantization indices across a selection of BEIR datasets

Overall, it seems that there is a slight relative decrease of 1.05% on average.

Next, we considered repeating the same evaluation process using the unquantized version of multilingual E5-small (see model card [here](https://huggingface.co/intfloat/multilingual-e5-small)) and Table 2 shows the respective results.

| Dataset | Full precision | Int8 quantization | Absolute difference | Relative difference |
| --- | --- | --- | --- | --- |
| Arguana | 0.384 | 0.379 | -0.005 | -1.3% |
| Climate-FEVER | 0.214 | 0.222 | +0.008 | +3.74% |
| FEVER | 0.718 | 0.715 | -0.003 | -0.42% |
| FiQA-2018 | 0.328 | 0.324 | -0.004 | -1.22% |
| NFCorpus | 0.31 | 0.306 | -0.004 | -1.29% |
| NQ | 0.548 | 0.537 | -0.011 | -2.01% |
| Quora | 0.882 | 0.881 | -0.001 | -0.11% |
| Robust04 | 0.418 | 0.415 | -0.003 | -0.72% |
| SCIDOCS | 0.134 | 0.132 | -0.003 | -1.49% |
| Scifact | 0.67 | 0.666 | -0.004 | -0.6% |
| TREC-COVID | 0.709 | 0.693 | -0.016 | -2.26% |
|  |  | Average | -0.004 | -0.83% |

**Table 2**: nDCG@10 scores of multilingual-E5-small on a selection of BEIR datasets

Again, we observe a slight relative decrease in performance equal to 0.83%. Finally, we repeated the exercise for multilingual E5-base and the performance decrease was even smaller (0.59%)

But this is not the whole story: The increased efficiency of the quantized HNSW indices and the fact that the original float vectors are still retained in the index allows us to recover a significant portion of the lost performance through [rescoring](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#knn-search-quantized-example). More specifically, we can retrieve a larger pool of candidates through approximate kNN search in the quantized index, which is quite fast, and then compute the similarity function on the original float vectors and re-score accordingly.

As a proof of concept, we consider the [**NQ**](https://ai.google.com/research/NaturalQuestions) dataset which exhibited a large performance decrease (2.01%) with multilingual E5-small. By setting `k=15`, `num_candidates=100` and `window_size=10` (as we are interested in nDCG@10) we get an improved score of `0.539` recovering about 20% of the performance. If we further increase the `num_candidates` parameter to 200 then we get a score that matches the performance of the full precision index but with faster response times. The same setup on Arguana leads to an increase from 0.379 to 0.382 and thus limiting the relative performance drop from 1.3% to only 0.52%

## Results

The results of our evaluation suggest that scalar quantization can be used to reduce the memory footprint of vector embeddings in Elasticsearch without significant loss in retrieval performance. The performance decrease is more pronounced for smaller vectors (multilingual E5-small produces vectors of size equal to 384 while E5-base gives 768-dimensional embeddings), but this can be mitigated through rescoring. We are confident that scalar quantization will be beneficial for most users and we plan to make it the default in 8.14.

### Frequently Asked Questions

#### What are the benefits of using scalar quantization in Elasticsearch?

The benefits of using scalar quantization in Elasticsearch include reducing the memory footprint of vector embeddings without significantly affecting retrieval performance.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt950edbc25d291821/6a6119f01b1d495dc56f181b/31783975126874424fc20c3c96bd95fe28d5f201-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

### How Elasticsearch auto-tunes vector quantization to hit your recall target

July 21, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter