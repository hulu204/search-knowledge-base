---
title: 'Late Interaction Comes to Solr: Neural Reranking Introduction'
company: Sease
tag: 排序
date: 2026-04-01
url: https://sease.io/2026/04/late-interaction-comes-to-solr-neural-reranking-introduction.html
account: 
origin: harvest3-202607
---
Hi there!

This is the first of a mini-series of two blog posts about the new Apache Solr feature coming to Solr 10.1: Late interaction models reranking.

In this blog post, I’m going to introduce the theory behind **neural reranking leveraging Late Interaction**, to be able to fully understand the topic.

In the next blog post, instead, I’m going to dive deep into the implementation to support Late Interaction in both Lucene and Solr and present a quick tutorial on how to set it up and use it on a Solr instance. Without further ado, let’s start!

## Why Reranking?

Search systems often balance two competing goals: **speed and accuracy**.   
Traditional lexical retrieval methods such as TF-IDF and BM25 are extremely fast and efficient, making them ideal for retrieving relevant documents from large collections. However, these methods rely on exact word matching and term statistics, which limit their ability to capture meaning. For example, the word *mouse* could refer to the animal or the computer input device, but lexical search treats them as identical tokens.   
Neural retrieval models address this limitation by encoding queries and documents into semantic representations (called *embeddings*, since they are vectors) that capture context and meaning, often leading to much more accurate results.   
The downside is that these models require significantly more computational resources and latency.   
To balance this trade-off, while designing search pipelines, a choice can be the following two-stage approach: a fast lexical retriever first selects a not-so-small set of candidate documents, and a more expensive neural model then reranks them based on semantic relevance.   
**This strategy preserves some of the efficiency of lexical search while improving accuracy with neural methods.**

### Early Interaction with Cross-Encoders

Early neural reranking approaches relied on early interaction models, most notably **Cross-encoder** architectures first popularised in 2019 in the paper *Passage Re-ranking with BERT* [[1](https://arxiv.org/abs/1901.04085)]. In this setup, the query and each candidate document are concatenated into a single sequence and fed together into the model, allowing the model to compute deep token-level interactions across the entire pair.

Usually, the embedding of the **`[CLS]`** token is used to produce a score, but various aggregation layers are possible. A simplified image to reproduce the logic is reported below.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/03/image-9.png?fit=724%2C677&ssl=1)

This design enables highly accurate relevance estimation because the model directly reasons over the combined query-document context.

However, it also makes reranking computationally expensive: the model must process the full model forward pass for every query-document pair. If a retriever returns *k* candidate documents, the system must run the language model *k* separate times.   
While early interaction models often achieve state-of-the-art ranking performance, the more we increase *k,* the more computationally demanding this process will become, ending up being unfeasible due to the complexity of the forward pass.

This is a common scenario, since we can rely on a lexical retrieval method for the first step and retrieve a lot of documents. Also, these models are usually BERT-based, meaning that sometimes they are very big, and the computational burden is too much to handle.

### Representation-based Reranking with Bi-Encoders

To overcome the latency of Early Interaction, the most straightforward neural approach involves **Bi-Encoders**. A natural way to reduce this cost is to move part of the computation offline. Ideally, we would like to precompute document representations once during indexing and avoid repeatedly processing them at query time.

In this setup, the query and the document are encoded independently into two single, high-dimensional vectors. The relevance score is then calculated using a simple distance metric, like cosine similarity or dot product.

This approach is faster because document embeddings can be pre-computed at index time and stored. At query time, only the query needs to be encoded, followed by a vector comparison between the top *k* vectors returned by the first retrieval stage.

However, this speed comes at a cost: forcing an entire document (which can even be a book) into a single vector loses token-level information, which is more precise.

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/03/image-1.png?fit=1749%2C914&ssl=1)

### Late Interaction with ColBERT

This is exactly where Late Interaction places itself: between the speed of Bi-Encoders and the precision of Cross-Encoders.

To address the latency problem of Early Interaction Models, researchers from Stanford introduced *ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT* [[2](https://arxiv.org/abs/2004.12832)]. The main idea of [ColBERT](https://sease.io/2025/11/colbert-in-practice-bridging-research-and-industry.html) is to represent each query and document as a set of contextualized token embeddings (bag-of-vectors model) rather than a single vector (like Bi-Encoders), to delay interaction between tokens at the end of the computations. In this way, we can encode queries and documents independently using an encoder model, allowing document representations to be computed once at index time and stored to be used later.

At query time, instead of doing the full forward pass for both query and documents, we just need to compute the bag-of-vectors for the query and compute similarities using a MaxSim operator: for each query token, it finds the most similar token in the document and aggregates these scores to produce the final relevance estimate.

An overview can be seen in the picture below.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/03/image-4.png?fit=800%2C480&ssl=1)

In this way, the model performs a lightweight interaction step that compares token-level embeddings between the query and each document to compute a relevance score.

Similarly to Bi-Encoders, this *late interaction* mechanism reduces the computational burden during search only by computing the embeddings of the query’s tokens and then computing similarities only across the top-k documents retrieved in the first step, but still being able to delay interaction between tokens at the end of the computations.

## Need Help with this topic?​

If you're struggling with implementing Late Interaction, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with implementing Late Interaction, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)