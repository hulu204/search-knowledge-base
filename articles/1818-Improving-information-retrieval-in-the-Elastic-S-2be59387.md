---
title: 'Improving information retrieval in the Elastic Stack: Hybrid retrieval'
company: Elastic
tag: 召回
date: 2023-07-20
url: https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-hybrid
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving information retrieval in the Elastic Stack: Hybrid retrieval

In this blog we introduce hybrid retrieval and explore two concrete implementations in Elasticsearch. We explore improving Elastic Learned Sparse Encoder’s performance by combining it with BM25 using Reciprocal Rank Fusion and Weighted Sum of Scores.

July 20, 2023

[Quentin Herreros](/search-labs/author/quentin-herreros)[Thomas Veasey](/search-labs/author/thomas-veasey)

[AI](/search-labs/blog/category/ai)

Part of the series:

[Improving information retrieval in the Elastic Stack](/search-labs/blog/series/improving-information-retrieval-in-the-elastic-stack)

In this series

Share

In our [last blog post](https://www.elastic.co/blog/may-2023-launch-information-retrieval-elasticsearch-ai-model), we introduced Elastic Learned Sparse Encoder, a model trained for effective zero-shot text retrieval. Elasticsearch

® also has great lexical retrieval capabilities and rich tools for combining the results of different queries. In this blog, we introduce the concept of hybrid retrieval and explore two concrete implementations available in Elasticsearch. In particular, we explore how to improve the performance of Elastic Learned Sparse Encoder by combining it with BM25 using Reciprocal Rank Fusion and Weighted Sum of Scores.

We also discuss experiments we undertook to explore some general research questions. These include how best to parameterize Reciprocal Rank Fusion and how to calibrate Weighted Sum of Scores.

## Hybrid retrieval

Despite modern training pipelines producing retriever models with good performance in zero-shot scenarios, it is known that lexical retrievers (such as BM25) and semantic retrievers (like Elastic Learned Sparse Encoder) are somewhat complementary. Specifically, it will improve relevance to combine the results of retrieval methods, if one assumes that the more matches occur between the relevant documents they retrieve than between the irrelevant documents they retrieve.

This hypothesis is plausible for methods using very different mechanisms for retrieval because there are many more irrelevant than relevant documents for most queries and corpuses. If methods retrieve relevant and irrelevant documents independently and uniformly at random, this imbalance means it is much more probable for relevant documents to match than irrelevant ones. We performed some overlap measurements to check this hypothesis between Elastic Learned Sparse Encoder, BM25, and various dense retrievers as shown in Table 1. This provides some rationale for using so-called hybrid search. In the following, we investigate two explicit implementations of hybrid search.

![Table 1: Overlap coefficients for three retrievers compared to Elastic Learned Sparse Encoder (referred to as “ELSER”) for top 1000 documents in ArguAna](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0a7954691f534817/6a17d827e8fbce7d5e3a1775/69c552634f1b86df5bd8bba3e6246365df43fa2f-1440x325.png)

## Reciprocal Rank Fusion

[Reciprocal Rank Fusion](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) was proposed in [this](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) paper. It is easy to use, being fully unsupervised and not even requiring score calibration. It works by ranking a document d with both BM25 and a model, and calculating its score based on the ranking positions for both methods. Documents are sorted by descending score. The score is defined as follows:

![reciprocal rank fusion](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6f184fb798c89541/6a17d8282f4a5cd160fa877a/3dbf83f811ee7be21a7683bb107801940a8e3b8b-878x210.png)

The method uses a constant k to adjust the importance of lowly ranked documents. It is applied to the top N document set retrieved by each method. If a document is missing from this set for either method, that term is set to zero.

The paper that introduces Reciprocal Rank Fusion suggests a value of 60 for k and doesn’t discuss how many documents N to retrieve. Clearly, ranking quality can be affected by increasing N while recall@N is increasing for either method. Qualitatively, the larger k the more important lowly ranked documents are to the final order. However, it is not a priori clear what would be optimal values of k and N for modern lexical semantic hybrid retrieval. Furthermore, we wanted to understand how sensitive the results are to the choice of these parameters and if the optimum generalizes between data sets and models. This is important to have confidence in the method in a zero-shot setting.

To explore these questions, we performed a grid search to maximize the weighted average NDCG@10 for a subset of the BEIR benchmark for a variety of models. We used Elasticsearch for retrieval in this experiment representing each document by a single text field and vector. The BM25 search was performed using a match query and dense retrieval using exact vector search with a script\_score query.

![Table 2: Average NDCG@10 across a subset of BEIR datasets (webis-touche2020, scidocs, nq, hotpotqa, fiqa, dbpedia-entity, arguana, trec-covid, nfcorpus) weighted per number of queries for various k and top N parameters using the bi-encoder roberta-base-ance-firstp for semantic retrieval](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc8069b2efc889a9e/6a17d82aa29299b158d02afc/3640a0c34a3379813eb9c1cb1c5cb90acb4c5c13-1236x674.png)

Referring to Table 2, we see that for [*roberta-base-ance-firstp*](https://huggingface.co/sentence-transformers/msmarco-roberta-base-ance-firstp) optimal values for k and N are 20 and 1000, respectively. We emphasize that *for the majority of individual data sets, the same combination of parameters was optimal*. We did the same grid search for [*distilbert-base-v3*](https://huggingface.co/sentence-transformers/msmarco-distilbert-base-v3) and [*minilm-l12-v3*](https://huggingface.co/sentence-transformers/msmarco-MiniLM-L-12-v3) with the same conclusion for each model. It is also worth noting that the difference between the best and worst parameter combinations is only about 5%; so the penalty for mis-setting these parameters is relatively small.

We also wanted to see if we could improve the performance of Elastic Learned Sparse Encoder in a zero-shot setting using Reciprocal Rank Fusion. The results on the [BEIR benchmark](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval) are given in Table 3.

![Table 3: NDCG@10 comparison between BM25 (using Elasticsearch 8.8 with default english analyzer), BM25 and Elastic Learned Sparse Encoder (referred to as “ELSER”) combined via RRF with k=20 and N=1000](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1c1f36b3e49bf984/6a17d82c577262b3501bca59/b893bb22fb90ce7be37e204db79e5276578e2b5a-1440x201.png)

Reciprocal Rank Fusion increases average NDCG@10 by 1.4% over Elastic Learned Sparse Encoder alone and 18% over BM25 alone. Also, importantly the result is either better or similar to BM25 alone for all test data sets. The improved ranking is achieved without the need for model tuning, training data sets, or specific calibration. The only drawback is that currently the query latency is increased as the two queries are performed sequentially in Elasticsearch. This is mitigated by the fact that BM25 retrieval is typically faster than semantic retrieval.

Our findings suggest that Reciprocal Rank Fusion can be safely used as an effective “plug and play” strategy. Furthermore, it is worth reviewing the quality of results one obtains with BM25, Elastic Learned Sparse Encoder and their rank fusion on your own data. If one were to select the best performing approach on each individual data set in the BEIR suite, the increase in average NDCG@10 is, respectively, 3% and 20% over Elastic Learned Sparse Encoder and BM25 alone.

As part of this work, we also performed some simple query classification to distinguish keyword and natural question searches. This was to try to understand the mechanisms that lead to a given method performing best. So far, we don’t have a clear explanation for this and plan to explore this further. However, we did find that hybrid search performs strongly when both methods have similar overall accuracy.

Finally, Reciprocal Rank Fusion can be used with more than two methods or could be used to combine rankings from different fields. So far, we haven’t explored this direction.

## Weighted Sum of Scores

Another way to do hybrid retrieval supported by Elasticsearch is to combine BM25 scores and model scores using a linear function. This approach was studied in this [paper](https://arxiv.org/abs/2210.11934), which showed it to be more effective than Reciprocal Rank Fusion when well calibrated. We explored hybrid search via a convex linear combination of scores defined as follows:

![weighted sum of scores](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2e4f608a2c418cef/6a17d82d57726251cc1bca5d/5eb23a557af4bcd06ae6438fb58034588afc0a57-1182x204.png)

where α is the model score weight and is between 0 and 1.

Ideal calibration of linear combination is not straightforward, as it requires annotations similar to those used for fine-tuning a model. Given a set of queries and associated relevant documents, we can use any optimization method to find the optimal combination for retrieving those documents. In our experiments, we used BEIR data sets and Bayesian optimization to find the optimal combination, optimizing for NDCG@10. In theory, the ratio of score scales can be incorporated into the value learned for α. However, in the following experiments, we normalized BM25 scores and Elastic Learned Sparse Encoder scores per data set using [min-max normalization](https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)), calculating the minimum and maximum from the top 1,000 scores for some representative queries on each data set. The hope was that with normalized scores the optimal value of transfers. We didn’t find evidence for this, but it is much more consistent and so normalization does likely improve the robustness of the calibration.

Obtaining annotations is expensive, so it is useful to know how much data to gather to be confident of beating Reciprocal Rank Fusion (RRF). Figure 1 shows the NDCG@10 for a linear combination of BM25 and Elastic Learned Sparse Encoder scores as a function of the number of annotated queries for the ArguAna data set. For reference, the BM25, Elastic Learned Sparse Encoder and RRF NDCG@10 are also shown. This sort of curve is typical across data sets. In our experiments, we found that it was possible to outperform RRF with approximately 40 annotated queries, although the exact threshold varied slightly from one data set to another.

![Figure 1: NDCG@10 evolution depending on the number of queries used to optimize alpha (on ArguAna data set). ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt21556109cff62221/6a17d82f3e03d7fcfc4f2ae7/fa3d1c6303813a722cf0cd706df04a62ce4556ac-1387x820.png)

We also observed that the optimal weight varies significantly both across different data sets (see Figure 2) and also for different retrieval models. This is the case even after normalizing scores. One might expect this because the optimal combination will depend on how well the individual methods perform on a given data set.

To explore the possibility of a zero-shot parameterisation, we experimented with choosing a single weight α for all data sets in our benchmark set. Although we used the same supervised approach to do this, this time choosing the weight to optimize average NDCG@10 for the full suite of data sets, we feel that there is enough variation between data sets that our findings may be representative of zero-shot performance.

In summary, this approach yields better average NDCG@10 than RRF. However, we also found the results were less consistent than RRF and we stress that *the optimal weight is model specific*. For this reason, we feel less confident the approach transfers to new settings even when calibrated for a specific model. In our view, linear combination is not a “plug and play” approach. Instead, we believe it is important to carefully evaluate the performance of the combination on your own data set to determine the optimal settings. However, as we will see below, if it is well calibrated it yields very good results.

![Figure 2: alpha variability across BEIR datasets. Those are obtained using Bayesian Optimization and test split.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbe36e4fd1c63fac2/6a17d8307b54f920b98b373d/6730d35de13b4cd2e3eb3cf1959bf5682d86343a-1440x626.png)

Normalization is essential for comparing scores between different data sets and models, as scores can vary a lot without it. It is not always easy to do, especially for Okapi BM25, where the range of scores is unknown until queries are made. Dense model scores are easier to normalize, as their vectors can be normalized. However, it is worth noting that some dense models are trained without normalization and may perform better with dot products.

Elastic Learned Sparse Encoder is trained to replicate cross-encoder score margins. We typically see it produce scores in the range 0 to 20, although this is not guaranteed. In general, a query history and their top N document scores can be used to approximate the distribution and normalize any scoring function with minimum and maximum estimates. We note that the non-linear normalization could lead to improved linear combination, for example if there are score outliers, although we didn’t test this.

As for Reciprocal Rank Fusion, we wanted to understand the accuracy of a linear combination of BM25 and Elastic Learned Sparse Encoder — this time, though, in the best possible scenario. In this scenario, we optimize one weight α per data set to obtain the ideal NDCG@10 using linear combination. We used 300 queries to calibrate — we found this was sufficient to estimate the optimal weight for all data sets. In production, this scenario is realistically difficult to achieve because it needs both accurate min-max normalization and a representative annotated data set to adjust the weight. This would also need to be refreshed if the documents and queries drift significantly. Nonetheless, bounding the best case performance is still useful to have a sense of whether the effort might be worthwhile. The results are displayed in Table 4. This approach gives a 6% improvement in average NDCG@10 over Elastic Learned Sparse Encoder alone and 24% improvement over BM25 alone.

![Table 4: NDCG@10 comparison between BM25 (using elasticsearch 8.8 with default english analyzer), Elastic Learned Sparse Encoder (referred to as “ELSER”), RRF (k=20 and top N = 1000) and linear combination (optimized on evaluation data)](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf302069660335ec5/6a17d832dbb4fff1a8fb550c/8770dfdbb31f733db880ba7185e871d2499105d8-1440x248.png)

## Conclusion

We showed it is possible to combine different retrieval approaches to improve their performance and in particular lexical and semantic retrieval complement one another. One approach we explored was Reciprocal Rank Fusion. This is a simple method that often yields good results without requiring any annotations nor prior knowledge of the score distribution. Furthermore, we found its performance characteristics were remarkably stable across models and data sets, so we feel confident that the results we observed will generalize to other data sets.

Another approach is Weighted Sum of Scores, which is more difficult to set up, but in our experiments yielded very good ranking with the right setup. To use this approach, scores should be normalized, which for BM25 requires score distributions for typical queries, furthermore some annotated data should be used for training the method weights.

In our final planned blog in this series, we will introduce the work we have been doing around inference and index performance as we move toward GA for the text\_expansion feature.

* **Part 1:** [Steps to improve search relevance](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance)
* **Part 2:** [Benchmarking passage retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval)
* **Part 3** : [Introducing Elastic Learned Sparse Encoder, our new retrieval model](https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance)
* **Part 4:** [Hybrid retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)

*The release and timing of any features or functionality described in this post remain at Elastic's sole discretion. Any features or functionality not currently available may not be delivered on time or at all.*

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter