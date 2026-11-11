---
title: 'Improving information retrieval in the Elastic Stack: Benchmarking passage retrieval'
company: Elastic
tag: 评测
date: 2023-07-13
url: https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving information retrieval in the Elastic Stack: Benchmarking passage retrieval

In this blog post, we'll examine benchmark solutions to compare retrieval methods. We use a collection of data sets to benchmark BM25 against two dense models and illustrate the potential gain using fine-tuning strategies with one of those models.

July 13, 2023

[Grégoire Corbière](/search-labs/author/gregoire-corbiere)[Quentin Herreros](/search-labs/author/quentin-herreros)[Thomas Veasey](/search-labs/author/thomas-veasey)

[AI](/search-labs/blog/category/ai)

Part of the series:

[Improving information retrieval in the Elastic Stack](/search-labs/blog/series/improving-information-retrieval-in-the-elastic-stack)

In this series

Share

In a [previous blog post](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance), we discussed common approaches to information retrieval and introduced the concepts of models and training stages. Here, we will examine benchmark solutions to compare various methods in a fair manner. Note that the task of benchmarking is not straightforward and can lead to misperceptions about how models perform in real-world scenarios.

Historically, comparisons between BM25 and learned retrieval models have been based on limited data sets, or even only on the training data set of these dense models: MSMARCO, which may not provide an accurate representation of the models' performance on your data. Despite this approach being useful for demonstrating how well a dense model performs against BM25 in a specific domain, it does not capture one of BM25's key strengths: its ability to perform well in many domains without the need for supervised fine-tuning. Therefore, it may be considered unfair to compare these two methods using such a specific data set.

The BEIR paper ("[BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models](https://arxiv.org/abs/2104.08663)," by Takhur et al. 2021) offers to address the issue of evaluating information retrieval methods in a generic setting. The paper proposes a framework using 18 publicly available data sets from a diverse range of topics to benchmark state-of-the-art retrieval systems.

In this post, we use a subcollection of those data sets to benchmark BM25 against two dense models that have been specifically trained for retrieval. Then we will illustrate the potential gain achievable using fine-tuning strategies with one of those dense models. We plan to return to this benchmark in our next blog post, since it forms the basis of the testing we have done to enhance Elasticsearch relevance using language models in a zero-shot setting.

## BEIR data sets

Performance can vary greatly between retrieval methods, depending on the type of query, document size, or topic. In order to assess the diversity of data sets and to identify potential blind spots in our benchmarks, a classification algorithm trained to recognize natural questions was used to understand queries typology. The results are summarized in Table 1.

![Table 1. Subset of BEIR data sets comparison](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt905686efac724fba/6a17d820e9ea873187a9c445/43ff728ed6b0e8cb74bd9749ac9f53e17c3ad91d-1150x628.png)

In our benchmarks, we choose not to include MSMARCO to solely emphasize performance in unfamiliar settings. Evaluating a model in a setting that is different from its training data is valuable when the nature of your use case data is unknown or resource constraints prevent adapting the model specifically.

## Search relevance metrics

Selecting the appropriate metric is crucial in evaluating a model's ranking ability accurately. Of the various metrics available, three are commonly utilized for search relevance:

* **Mean Reciprocal Rank (MRR)** is the most straightforward metric. While it is easy to calculate, it only considers the first relevant item in the results list and ignores the possibility that a single query could have multiple relevant documents. In some instances, MRR may suffice, but it is often not precise enough.
* **Mean Average Precision (MAP)** excels in ranking lists and works well for binary relevance ratings (a document is either relevant or non-relevant). However, in data sets with fine-grained ratings, MAP is not able to distinguish between a highly relevant document and a moderately relevant document. Also, it is only appropriate if the list is reordered since it is not sensitive to order; a search engineer will prefer that the relevant documents appear first.
* **Normalized Discounted Cumulative Gain (NDCG)** is the most complete metric as it can handle multiple relevant documents and fine-grained document ratings. This is the metric we will examine in this blog and future ones.

All of these metrics are applied to a fixed-sized list of retrieved documents. The list size can vary depending on the task at hand. For example, a preliminary retrieval before a reranking task might consider the top 1000 retrieved documents, while a single-stage retrieval might use a smaller list size to mimic a user's search engine behavior. We have chosen to fix the list size to the top 10 documents, which aligns with our use case.

## BM25 and dense models out-of-domain

In our previous [blog post](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance), we noted that dense models, due to their training design, are optimized for specific data sets. While they have been shown to perform well on this particular data set, in this section we explore if they maintain their performance when used out-of-domain. To do this, we compare the performance of two state-of-the-art dense retrievers (*msmarco-distilbert-base-tas-b* and *msmarco-roberta-base-ance-fristp*) with BM25 in Elasticsearch using the default settings and English analyzer.

![Table 2. NDCG@10 for BM25 vs. state-of-the-art dense models benchmark](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt305ccdb44c7728a5/6a17d822e8fbce18d53a176f/5cbe86da358a07226ac2642a01e5d984875d999b-1255x369.png)

Those two dense models both outperform BM25 on MSMARCO (as seen in the [BEIR paper](https://openreview.net/pdf?id=wCu6T5xFjeJ)), as they are trained specifically on this data set. However, they are usually worse out-of-domain. In other words, if a model is not well adapted to your specific data, it’s very likely that using kNN and dense models would degrade your retrieval performance in comparison to BM25.

## Fine-tuning dense models

The portrayal of dense models in the previous description isn't the full picture. Their performance can be improved by fine-tuning them for a specific use case with some labeled data that represents that use case. If you have a fine-tuned embedding model, the Elastic Stack is a great platform to both run the inference for you and retrieve similar documents using ANN search.

There are various methods for fine-tuning a dense model, some of which are highly sophisticated. However, this blog post won't delve into those methods as it's not the focus. Instead, two methods were tested to gauge the potential improvement that can be achieved with not a lot of domain specific training data. The first method (FineTuned A) involved using labeled positive documents and randomly selecting documents from the corpus as negatives. The second method (FineTuned B) involved using labeled positive documents and using BM25 to identify documents that are similar to the query from BM25's perspective, but aren't labeled as positive. These are referred to as "hard negatives."

![Graph 1. NDCG@10 curve for fine-tuning msmarco-distilbert-base-tas-b using 1000 triplets from the SciFact BEIR data set](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte794b16cd33fbe42/6a17d824505ac37ed1ad8968/ade42d23e4e6219bff0e77533cf95e48c20dc0a3-1150x628.png)

Labeling data is probably the most challenging aspect in fine-tuning. Depending on the subject and field, manually tagging positive documents can be expensive and complex. Incomplete labeling can also create problems for hard negatives mining, causing adverse effects on fine-tuning. Finally, changes to the topic or semantic structure in a database over time will reduce retrieval accuracy for fine-tuned models.

## Conclusion

We have established a foundation for information retrieval using 13 data sets. The BM25 model performs well in a zero-shot setting and even the most advanced dense models struggle to compete on every data set. These initial benchmarks indicate that current SOTA dense retrieval cannot be used effectively without proper in-domain training. The process of adapting the model requires labeling work, which may not be feasible for users with limited resources.

In our next blog, we will discuss alternative approaches for efficient retrieval systems that do not require the creation of a labeled data set. These solutions will be based on hybrid retrieval methods.

* **Part 1:** [Steps to improve search relevance](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance)
* **Part 2:** [Benchmarking passage retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval)
* **Part 3:** [Introducing Elastic Learned Sparse Encoder, our new retrieval model](https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance)
* **Part 4:** [Hybrid retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)

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