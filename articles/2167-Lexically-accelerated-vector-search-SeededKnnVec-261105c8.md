---
title: 'Lexically accelerated vector search: SeededKnnVectorQuery Support in Apache Solr 10'
company: Sease
tag: 召回
date: 2026-02-02
url: https://sease.io/2026/02/lexically-accelerated-vector-search-seededknnvectorquery-support-in-apache-solr-10.html
account: 
origin: harvest3-202607
---
Hi readers,

In this blog post, we are excited to share some important news with you:  
**Sease** has **contributed a new feature to Apache Solr** that introduces support for **SeededKnnVectorQuery**, a version of knn vector query that brings a powerful enhancement to vector search capabilities.

*A special thanks to Christine Poerschke for the initial draft and the review.*

With this addition, users can now perform k-nearest-neighbors (kNN) searches that start from a specific **“seed” query**, to narrow down the candidate set before performing the vector similarity computation. This approach can significantly improve both **precision and performance**.

***This feature is available starting from [Apache Solr 10.0.0](https://solr.apache.org/guide/solr/10_0/index.html)***.

Here is how we will explore the topic:

* We briefly mention the research paper, which inspired the introduction of this feature.
 * We will then outline how this strategy has been implemented in **Apache Lucene**.
 * After that, we will describe the open-source contribution we made to **Apache Solr** and explain how to use this new feature.

## Lexically-Accelerated Dense Retrieval

The Apache Lucene implementation of SeededKnnVectorQuery is based on the research paper **“[Lexically-Accelerated Dense Retrieval](https://arxiv.org/pdf/2307.16779)“** (Hrishikesh Kulkarni, Sean MacAvaney, Nazli Goharian, Ophir Frieder), presented at SIGIR ’23.

### Problem To Address

In information retrieval, there are two main ways to find relevant documents.   
The first is *lexical retrieval*, which looks for exact word matches between the query and the documents. It is very fast but limited; if the document uses different words to express the same idea, it might not be found.   
The second approach is *dense retrieval*, which represents both queries and documents as numerical vectors and compares their meanings rather than their exact words. This method captures deeper semantic relationships but is much more computationally expensive because it has to compare each query with a huge number of document vectors.

The challenge for researchers is finding a balance between speed and accuracy in order to make dense retrieval faster without losing much accuracy.

### Proposed Approach

They propose a method called **Lexically‑Accelerated Dense Retrieval (LADR)**, which offers a **pragmatic trade-off** that leverages lexical retrieval for the “cheap” part, then concentrates the expensive dense scoring only where it is likely beneficial.

The core idea of the paper is to start with a fast lexical search to identify an initial set of promising “seed” documents. Instead of scanning the entire collection, the system then explores the semantic space around these seeds using a pre-computed graph that connects documents based on their meaning.   
By following these links, it discovers other semantically related documents that a purely lexical approach would miss. Only this smaller subset is scored with the dense retrieval model, which greatly reduces computation time. In this way, the method achieves nearly the same quality as a full dense search but with much higher efficiency.

They define two variants:

* **Proactive LADR**: takes a simple, one-step approach. After selecting the seed documents through lexical retrieval, it expands each seed by adding its *k* nearest neighbours from the pre-computed semantic graph. The union of these documents forms the candidate set, which is then scored once using the dense retrieval model.
 * **Adaptive LADR**: expands results gradually and selectively. It first scores the seed documents, then expands only from the top-ranked ones by adding their *k* nearest neighbours. The process repeats, each time expanding from the best current results, until no new relevant documents are found.

The authors evaluated the LADR approach on several standard retrieval benchmarks using different dense retrieval models. Overall, LADR achieves high effectiveness (in both nDCG and recall) comparable to exhaustive dense retrieval, but with much lower computational cost and no need for GPUs, demonstrating an excellent balance between speed and accuracy.

## Apache Lucene Implementation

In August 2024, an issue was created in the Lucene project to propose the introduction of **Seeding HNSW Search**: [#13634](https://github.com/apache/lucene/issues/13634)

Starting from early 2025, a series of pull requests followed, progressively implementing and refining this functionality. In particular:

**Lucene 10.2.1**  
– First implementation: [#14084](https://github.com/apache/lucene/pull/14084) – two individual seeded queries added (float and byte).  
– Bugfix and refactoring: [#14170](https://github.com/apache/lucene/pull/14170) – collapsed the two individual seeded queries into a single query that delegates to a provided kNN query.  
– Bugfix: [#14197](https://github.com/apache/lucene/pull/14197) – incorrect entrypoint ids.

**Lucene 10.3.0**  
– Bugfix: [#14688](https://github.com/apache/lucene/pull/14688) – this fixes PatienceKnnVectorQuery to work with SeededKnnVectorQuery.  
– Improvement: [#14838](https://github.com/apache/lucene/pull/14838) – make it possible to extend Patience/Seeded knn queries.

[SeededKnnVectorQuery](https://lucene.apache.org/core/10_3_0/core/org/apache/lucene/search/SeededKnnVectorQuery.html) is a wrapper around an existing vector query (**`KnnFloatVectorQuery`** or **`KnnByteVectorQuery`**), referred to as the *delegate*.  
The “seeded” version inherits all the behaviour of **`AbstractKnnVectorQuery`**, but introduces a *seed* that is applied only during the approximate search phase through the **`SeededCollectorManager`**.

In practice, it first performs a traditional (lexical) search to identify an initial set of candidate documents (***`TopDocs seedTopDocs`***), which are then used as **entry points** for navigating the HNSW graph in the vector search. If the seed does not produce results, the query simply falls back to behaving like a regular k-NN search without seeding.

## Our Apache Solr Contribution

Since Solr was recently upgraded to Lucene 10.2.1 (PR: [#3053](https://github.com/apache/solr/pull/3053)) and then to Lucene 10.3 (PR: [#3659](https://github.com/apache/solr/pull/3659)), we have been able to expose this new functionality.

In PR [#3705](https://github.com/apache/solr/pull/3705), the possibility to use the **SeededKnnVectorQuery** has therefore been added in Apache Solr. This feature will be available starting from Apache Solr 10.0.0.

The `KnnQParser` has been modified to include support for this functionality, exposed through one additional optional query parameter:

* `seedQuery` (default: `none`) – A query seed to initiate the vector search. It is primarily intended to be a lexical query, guiding the vector search in a hybrid-like way through traditional query logic. Although a knn query can also be used as a seed — which might make sense in specific scenarios and has been verified by a dedicated test — this approach is not considered a best practice.

A new method **`getSeedQuery()`** was added to parse the `seedQuery` parameter and return the corresponding Lucene Query.   
When a `seedQuery` is present, the KNN vector query is wrapped in a `SeededKnnVectorQuery`, specifically:

* SeededKnnVectorQuery.fromFloatQuery(…) for FLOAT32 vectors.
 * SeededKnnVectorQuery.fromByteQuery(…) for BYTE vectors.

These two static factory methods create the appropriate *SeededKnnVectorQuery* instance depending on the vector encoding (float or byte). In practice, the seeded query object is created through these methods, which ensure that the seeded variant of the query is instantiated correctly and retains all parameters of the underlying KNN query while adding the seed logic.

### SeededKnnVectorQuery

Here is an example of a **`knn`** search using a **`seedQuery`**:

```
				
					?q={!knn f=vector topK=10 seedQuery='id:(1 4 10)'}[1.0, 2.0, 3.0, 4.0]

				
			
```

The search results retrieved are the k=10 nearest documents to the vector in input **`[1.0, 2.0, 3.0, 4.0]`**. Documents matching the query **`id:(1 4 10)`** are used as entry points for the k-NN search. If no documents match the seed, Solr falls back to a regular k-NN search without seeding, starting instead from random entry points.

### SeededKnnVectorQuery in Combination With earlyTermination (PatienceKnnVectorQuery)

The **`seedQuery`**can also be used in combination with **`earlyTermination`**, a strategy that makes approximate k-NN search faster and more efficient by enabling early termination of the graph traversal when certain criteria are met. Take a look at **[this blog post](https://sease.io/2025/12/faster-vector-search-early-termination-strategy-now-in-apache-solr.html)** for more information about the **`earlyTermination`** strategy and the **`PatienceKnnVectorQuery`**

```
				
					?q={!knn f=vector topK=10 seedQuery='id:(1 4 10)' earlyTermination=true}[1.0, 2.0, 3.0, 4.0]
				
			
```

When both the **`seedQuery`** and the **`earlyTermination`** parameters are provided, Solr automatically wraps the seeded query with a `PatienceKnnVectorQuery`, a query class that adds early-termination capabilities to an existing kNN vector query. In other words, the early-termination strategy is applied *on top of* the seeded k-NN query, and the final query object internally corresponds to the static factory method: `PatienceKnnVectorQuery.fromSeededQuery(...)`.

This method constructs a new PatienceKnnVectorQuery instance for a seeded vector query, ensuring that the SeededKnnVectorQuery is used as the underlying delegate while the early-termination logic is layered on top of it. As a result, the query benefits both from **seeding** and from the **patience-based early termination mechanism**.

I hope you enjoyed this blog. Stay tuned! New blog posts about other vector search features introduced in **Solr 10** are coming soon!

## Need Help with this topic?​

If you're struggling with SeededKnnVectorQuery, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with SeededKnnVectorQuery, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)