---
title: 'Improving information retrieval in the Elastic Stack: Steps to improve search relevance'
company: Elastic
tag: 搜索相关性
date: 2023-07-13
url: https://www.elastic.co/search-labs/blog/improving-information-retrieval-elastic-stack-search-relevance
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving information retrieval in the Elastic Stack: Steps to improve search relevance

In this first blog post, we will list and explain the differences between the primary building blocks available in the Elastic Stack to do information retrieval.

July 13, 2023

[Grégoire Corbière](/search-labs/author/gregoire-corbiere)[Quentin Herreros](/search-labs/author/quentin-herreros)[Thomas Veasey](/search-labs/author/thomas-veasey)

[AI](/search-labs/blog/category/ai)

Part of the series:

[Improving information retrieval in the Elastic Stack](/search-labs/blog/series/improving-information-retrieval-in-the-elastic-stack)

In this series

Share

Since 8.0 and the release of third-party natural language processing (NLP) models for text embeddings, users of the Elastic Stack have access to a wide variety of models to [embed their text documents](https://www.elastic.co/blog/text-similarity-search-with-vectors-in-elasticsearch) and perform query-based information retrieval using vector search.

Given all these components and their parameters, and depending on the text corpus you want to search in, it can be overwhelming to choose which settings will give the best search relevance.

In this series of blog posts, we will introduce a number of tests we ran using various publicly available data sets and information retrieval techniques that are available in the Elastic Stack. We’ll then provide recommendations of the best techniques to use depending on the setup.

To kick off this series of blogs, we want to set the stage by describing the problem we are addressing and describe some methods we will dig further into in subsequent blogs.

## Background and terminology

### BM25: A sparse, unsupervised model for lexical search

The classic way documents are ranked for relevance by Elasticsearch according to a text query uses the Lucene implementation of the [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25) model. Although a few hyperparameters of this model were fine-tuned to optimize the results in most scenarios, this technique is considered **unsupervised** as labeled queries and documents are not required to use it: *it’s very likely that the model will perform reasonably well on any corpus of text, without relying on annotated data. BM25 is known to be a strong baseline in zero-shot retrieval settings.*

Under the hood, this kind of model builds a matrix of term frequencies (how many times a term appears in each document) and inverse document frequencies (inverse of how many documents contain each term). It then scores each query term for each document that was indexed based on those frequencies. Because each document typically contains a small fraction of all words used in the corpus, the matrix contains a lot of zeros. This is why this type of representation is called **sparse**.

Also, this model sums the relevance score of each individual term within a query for a document, without taking into account any semantic knowledge (synonyms, context, etc.). This is called **lexical search** (as opposed to semantic search). Its shortcoming is the so-called vocabulary mismatch problem, that query vocabulary is slightly different to the document vocabulary. This motivates other scoring models that try to incorporate semantic knowledge to avoid this problem.

### Dense models: A dense, supervised model for semantic search

More recently, transformer-based models have allowed for a dense, context aware representation of text, addressing the principal shortcomings mentioned above.

To build such models, the following steps are required:

**1. Pre-training**
We first need to train a neural network to understand the basic syntax of natural language.

Using a huge corpus of text, the model learns semantic knowledge by training on unsupervised tasks (like [Masked Word Prediction](https://huggingface.co/tasks/fill-mask) or Next Sentence Prediction).
[BERT](https://arxiv.org/abs/1810.04805v2) is probably the best known example of these models — it was trained on Wikipedia (2.5B words) and BookCorpus (800M words) using Masked Word Prediction.

This is called **pre-training**. The model learns vector representations of language tokens, which can be adapted for other tasks with much less training.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfed238df732e259f/6a17d83663baff4011741adf/8ca72bdf2618ec179a42c957199ee7457de2cef6-1440x236.jpg)

Note that at this step, the model wouldn’t perform well on downstream NLP tasks.

This step is very expensive, but [**many such foundational**](https://huggingface.co/transformers/v3.3.1/pretrained_models.html) models exist that can be used off the shelf.

**2. Task-specific training**
Now that the model has built a representation of natural language, it’ll train much more effectively on a specific task such as Dense Passage Retrieval (DPR) that allows Question Answering.

To do so, we must slightly adapt the model’s architecture and then train it on a large number of instances of the task, which, for DPR, consists in matching a relevant passage taken from a relevant document.

So this requires a **labeled** data set, that is, a collection of triplets :

* A query: "What is gold formed in?"
* A document or passage taken from a document: "The core of large stars, especially during a nova"
* Optionally, a score of degree of relevance for this (query, document) pair (If no score is given, we assume that the score is binary, and that all the other documents can be considered as irrelevant for the given query.)

A very popular and publicly available data set to perform such a training for DPR is the [MS MARCO](https://microsoft.github.io/msmarco/) data set.

This data set was created using queries and top results from Microsoft’s Bing search engine. As such, the queries and documents it contains fall in the general knowledge linguistic domain, as opposed to specific linguistic domain (think about research papers or language used in law).

This notion of linguistic domain is important, as the semantic knowledge learned by those models is giving them an important advantage “in-domain”: when BERT came out, it improved previous state of the art models on this MS MARCO data set by a huge margin.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt037e7287ee90eab6/6a17d837dbb4ff537ffb5510/3f584bb2dfd613b6306179e9b9c3926383730e64-1440x377.jpg)

**3. Domain-specific training**
Depending on how different your data is from the data set used for task-specific training, you might need to train your model using a *domain specific* labeled data set. This step is also referred to as fine tuning for domain adaptation or domain-adaptation.

The good news is that you don’t need as large a data set as was required for the previous steps — a few thousands or tens of thousands of instances of the tasks can be enough.

The bad news is that these query-document pairs need to be built by domain experts, so it’s usually a costly option.

The domain adaptation is roughly similar to the task-specific training.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt30101b88eca0aca7/6a17d8397f6f153e49c09999/dd150c622efab183bf4b96eeb18b5c3111e9f147-1440x388.jpg)

Having introduced these various techniques, we will measure how they perform on a wide variety of data sets. This sort of general purpose information retrieval task is of particular interest for us. We want to provide tools and guidance for a range of users, including those who don’t want to train models themselves in order to gain some of the benefits they bring to search. In the next blog post of this series, we will describe the methodology and benchmark suite we will be using.

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