---
title: 'Improving information retrieval in the Elastic Stack: Optimizing retrieval with ELSER v2'
company: Elastic
tag: 召回
date: 2023-10-17
url: https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-2
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving information retrieval in the Elastic Stack: Optimizing retrieval with ELSER v2

Learn how we are reducing the retrieval costs of the Learned Sparse EncodeR (ELSER) v2.

October 17, 2023

[Thomas Veasey](/search-labs/author/thomas-veasey)[Quentin Herreros](/search-labs/author/quentin-herreros)[Valeriy Khakhutskyy](/search-labs/author/valeriy-khakhutskyy)

[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

In our [last post](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-1) we introduced ELSER v2, discussed its zero shot relevance and the inference performance improvements we made. This blog focuses on how we reduced its retrieval costs.

It has been [noted](https://arxiv.org/pdf/2110.11540.pdf) that retrieval can be slow when using scores computed from learned sparse representations, such as ELSER. Slow is a relative term and in this context we mean slow when compared to BM25 scored retrieval. There are two principle reasons for this:

1. The query expansion means we're usually matching many more terms than are present in user supplied keyword searches.
2. The weight distribution for BM25 is particularly well suited to query optimisation.

The first bottleneck can be tackled at train time, albeit with a relevance retrieval cost tradeoff. There is a regularizer term in the training loss which allows one to penalize using more terms in the query expansion. There are also gains to be had by performing better model selection.

## Retrieval cost aware training

When training any model it is sensible to keep the best one as optimisation progresses. Typically the quality is measured using the training loss function evaluated on a hold-out, or validation, dataset. We had found this metric alone did not correlate as well as we liked with zero-shot relevance; so we were already measuring NDCG@10 on several small datasets from the BEIR suite to help decide which model to retain. This allows us to measure other aspects of retrieval behavior. In particular, we compute the retrieval cost using the number of weight multiplications performed on average to find the top-k matches for every query.

We found that there is quite significant variation between the retrieval cost for relatively small variation in retrieval quality and used this information to identify [Pareto optimal](https://en.wikipedia.org/wiki/Pareto_efficiency) models. This was done for various choices of our regularization hyperparameters at different points along their learning trajectories. The figure below shows a scatter plot of the candidate models we considered characterized by their relevance and cost, together with the choice we made for ELSER v2. In the end we sacrificed around 1% in relevance for around a 25% reduction in the retrieval cost.

![ELSER v2 model selection](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta043ca39c605e29d/6a17053366c4f962e9f8bf2f/16b377b85fb366466e3402ed07ae56834573384c-629x479.png)

Performing model selection for ELSER v2 via relevance retrieval cost multi-objective optimization

Whilst this is a nice win, the figure also shows there is only so much it is possible to achieve when making the trade off at train time. At least without significantly impacting relevance. As we [discussed before](https://www.elastic.co/search-labs/may-2023-launch-information-retrieval-elasticsearch-ai-model), with ELSER our goal is to train a model with excellent zero-shot relevance. Therefore, if we make the tradeoff during training we make it in a global setting, without knowing anything about the specific corpus where the model will be applied. To understand how to overcome the dichotomy between relevance and retrieval cost we need to study the token statistics in a specific corpus. At the same time, it is also useful to understand why BM25 scoring is so efficient for retrieval.

## Optimizing ELSER queries

The BM25 score comprises two factors, one which relates to its frequency in each document and one which relates to the frequency of each query term in the corpus. Focusing our attention on second factor, the score contribution of a term ttt is weighted by its [inverse document frequency](https://en.wikipedia.org/wiki/Okapi_BM25#The_ranking_function) (IDF) or log⁡(1−ftft+1)\log\left(\frac{1 - f\_t}{f\_t} + 1\right)log(ft​1−ft​​+1). Here ft=nt+0.5Nf\_t=\frac{n\_t+0.5}{N}ft​=Nnt​+0.5​ and ntn\_tnt​ and NNN denote the matching document count and total number of documents, respectively. So ftf\_tft​ is just the proportion of the documents which contain that term, modulo a small correction which is negligible for large corpuses.

It is clear that IDF is a monotonic decreasing function of the frequency. Coupled with [block-max WAND](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand), this allows retrieval to skip many non-competitive documents even if the query includes frequent terms. Specifically, in any given block one might expect some documents to contain frequent terms, but with BM25 scoring they are unlikely to be competitive with the best matches for the query.

The figure below shows statistics related to the top tokens generated by ELSER v2 for the [NFCorpus](https://www.cl.uni-heidelberg.de/statnlpgroup/nfcorpus/) dataset. This is one of the datasets used to evaluate retrieval in the BEIR suite and comprises queries and documents related to nutrition. The token frequencies, expressed as a percentage of the documents which contain that token, are on the right hand axis and the corresponding IDF and the average ELSER v2 weight for the tokens are on the left hand axis. If one examines the top tokens they're what we might expect given the corpus content: things like “supplement”, “nutritional”, “diet”, etc. Queries expand to a similar set of terms. This underlines that even if tokens are well distributed in the training corpus as a whole, they can end up concentrated when we examine a specific corpus. Furthermore, we see that unlike BM25 the weight is largely independent of token frequency and this makes block-max WAND ineffective. The outcome is retrieval is significantly more expensive than BM25.

![ELSER v2 token stats](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd5c4cb14d07524a1/6a170535cdacbf482f7d291a/be0d185520c943b1bd36103c7d3f9cda30d120f7-700x496.png)

Average ELSER v2 weights and IDF for the top 500 tokens in the document expansions of NFCorpus together with the percentage of documents in which they appear

Taking a step back, this suggests we reconsider token importance in light of the corpus subject matter. In a general setting, tokens related to nutrition may be highly informative. However, for a corpus about nutrition they are less so. This in fact is the underpinning of information theoretic approaches to retrieval. Roughly speaking we have two measures of the token information content for a specific query and corpus: its assigned weight - which is the natural analogue of the term frequency term used in BM25 - and the token frequency in the corpus as a whole - which we disregard when we score matches using the product of token weights. This suggests the following simple strategy to accelerate queries with hopefully little impact on retrieval quality:

1. Drop frequent tokens altogether provided they are not particularly important for the query in the retrieval phase,
2. Gather slightly more matches than required, and
3. Rerank using the full set of tokens.

We can calculate the expected fraction of documents a token will be present in, assuming they all occur with equal probability. This is just the ratio NTN∣T∣\frac{N\_T}{N|T|}N∣T∣NT​​ where NTN\_TNT​ is the total number of tokens in the corpus, NNN is the number of documents in the corpus and ∣T∣|T|∣T∣ is the vocabulary size, which is 30522. Any token that occurs in a significantly greater fraction of documents than this is frequent for the corpus.

We found that pruning tokens which are 5 times more frequent than expected was an effective relevance retrieval cost tradeoff. We fixed the count of documents reranked using the full token set to 5 times the required set, so 50 for NDCG@10. We found we achieved more consistent results setting the weight threshold for which to retain tokens as a fraction of the maximum weight of any token in the query expansion. For the results below we retain all tokens whose weight is greater than or equal to 0.4 × “max token weight for the query”. This threshold was chosen so NDCG@10 was unchanged on NFCorpus. However, the same parameterization worked for the other 13 test datasets we tested, which strongly suggests that it generalizes well.

The table below shows the change in NDCG@10 relative to ELSER v2 with exact retrieval together with the retrieval cost relative to ELSER v1 with exact retrieval using this strategy. Note that the same pruning strategy can be applied to any learned sparse representation. However, we view that the key questions to answer are:

1. Does the approach lead to any degradation in relevance compared to using exact scoring?
2. What improvement in the retrieval latency might one expect using ELSER v2 and query optimization compared to the performance of the [text\_expansion](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-text-expansion-query.html) query to date?

In summary, we achieved a very small improvement(!) of 0.07% in average NDCG@10 when we used the optimized query compared to the exact query and an average 3.4 times speedup. Furthermore, this speedup is measured without block-max WAND. As we expected, the optimization works particularly well together with block-max WAND. On a larger corpus (8.8M passages) we saw an 8.4 times speedup with block-max WAND enabled.

![ELSER v2 optimized query performance](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte026335df83a6a70/6a170536acf08888c9be9a16/0d5929eaec4316ea6c5842010e32e2ecf07a1233-1079x189.png)

Measuring the relevance and latency impact of using token pruning followed by reranking. The relevance is measured by percentage change in NDCG@10 for exact retrieval with ELSER v2 and the speedup is measured with respect to exact retrieval with ELSER v1

An intriguing aspect of these results is that on average we see a small relevance improvement. Together with the fact that we [previously showed](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid) carefully tuned combinations of ELSER v1 and BM25 scores yield very significant relevance improvements, it strongly suggests there are benefits available for relevance as well as for retrieval cost by making better use of corpus token statistics. Ideally, one would re-architect the model and train the query expansion to make use of both token weights and their frequencies. This is something we are actively researching.

## Implementing with an Elasticsearch query

As of Elasticsearch 8.13.0, we have integrated this optimization in the `text_expansion` query via [token pruning](https://www.elastic.co/search-labs/blog/text-expansion-pruning) so it is automatically applied in the retrieval phase for the text\_expansion query.

![ELSER v2 text_expansion query with token pruning](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8d3dadf5f14a0097/6a170538839dfa2fbadcfdde/2930f0659e42c05dac962fe4e6ea1e3f8dd2d744-1440x1450.png)

For versions of Elasticsearch before 8.13.0, it is possible to achieve the same results using existing Elasticsearch query DSL given an analysis of the token frequencies and their weights.

Tokens are stored in the \_source field so it is possible to [paginate](https://www.elastic.co/guide/en/elasticsearch/reference/current/paginate-search-results.html#search-after) through the documents and accumulate token frequencies to find out which tokens to exclude. Given an inference response one can partition the tokens into a “kept” and “dropped” set. The kept set is used to score the match in a should query. The dropped set is used in a rescore query on a window of the top 50 docs. Using query\_weight and rescore\_query\_weight both equal to one simply sums the two scores so recovers the score using the full set of tokens. The query together with some explanation is shown below.

![ELSER v2 optimized query](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8df5d9dfd20adf7b/6a17053ae8fbced15b39fb42/9f4e1a231ecc3aa465f6c63da48b7db1869b9d67-778x485.png)

## Conclusion

In these last two posts in our series we introduced the second version of the Elastic Learned Sparse EncodeR. So what benefits does it bring?

With some improvements to our training data set and regularizer we were able to obtain roughly a 2% improvement on our benchmark of zero-shot relevance. At the same time we've also made significant improvements to inference performance and retrieval latency.

We traded a small degradation (of a little less than 1%) in relevance for a large improvement (of over 25%) in the retrieval latency when performing model selection in the training loop. We also identified a simple token pruning strategy and verified it had no impact on retrieval quality. Together these sped up retrieval by between 2 and 5 times when compared to ELSER v1 on our benchmark suite. Token pruning can currently be implemented using Elasticsearch DSL, but we're also working towards performing it automatically in the text\_expansion query.

To [improve inference performance](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-1) we prepared a quantized version of the model for x86 architecture and upgraded the libtorch backend we use. We found that these sped up inference by between 1.7 and 2.2 times depending on the text length. By using hybrid dynamic quantisation, based on an analysis of layer sensitivity to quantisation, we were able to achieve this with minimal loss in relevance.

We believe that ELSER v2 represents a step change in performance, so encourage you to give it a try!

This is an exciting time for information retrieval, which is being reshaped by rapid advances in NLP. We hope you've enjoyed this blog series in which we've tried to give a flavor of some of this field. This is not the end, rather the end of the beginning for us. We're already working on various improvements to retrieval in Elasticsearch and particularly in end-to-end optimisation of retrieval and generation pipelines. So stay tuned!

*The release and timing of any features or functionality described in this post remain at Elastic's sole discretion. Any features or functionality not currently available may not be delivered on time or at all.*

*Elastic, Elasticsearch and associated marks are trademarks, logos or registered trademarks of Elasticsearch N.V. in the United States and other countries. All other company and product names are trademarks, logos or registered trademarks of their respective owners.*

* **Part 1:** [Steps to improve search relevance](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance)
* **Part 2:** [Benchmarking passage retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval)
* **Part 3:** [Introducing Elastic Learned Sparse Encoder, our new retrieval model](https://www.elastic.co/search-labs/may-2023-launch-information-retrieval-elasticsearch-ai-model)
* **Part 4:** [Hybrid Retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)
* **Part 5:** [Optimizing inference for ELSER v2](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-1)
* **Part 6:** [Optimizing retrieval with ELSER v2](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-2)

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