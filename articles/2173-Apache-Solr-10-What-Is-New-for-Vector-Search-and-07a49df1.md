---
title: 'Apache Solr 10 – What Is New for Vector Search and LTR'
company: Sease
tag: 排序
date: 2026-03-30
url: https://sease.io/2026/03/apache-solr-10-what-is-new-for-vector-search-and-ltr.html
account: 
origin: harvest3-202607
---
On 3rd March 2026, the Solr PMC announced the release of Apache Solr 10.0.0!  
Solr 10.0.0 is now [available for immediate download here](https://solr.apache.org/downloads.html).

In this blog post, we summarise the main new features introduced in this major release, focusing on **Vector Search** and **Learning to Rank (LTR)**.  
These features were contributed by the **Sease Ltd** team (specifically by [Alessandro Benedetti](https://sease.io/about/alessandro-benedetti-2), [Anna Ruggero](https://sease.io/about/anna-ruggero), and me, [Ilaria Petreti](https://sease.io/about/ilaria-petreti)), as part of our ongoing effort to enhance Solr’s search and ranking capabilities, and by **Kevin Liang**, a senior software engineer at Bloomberg.

Below, we will provide a brief overview of each new feature, followed by a link to the full blog post where each topic is covered in more detail.

## Vector Search

##### 1) Add Support for Scalar Quantized Dense Vectors

Jira Issue: [SOLR-17780](https://issues.apache.org/jira/browse/SOLR-17780)  
Solr GitHub PR: [#3385](https://github.com/apache/solr/pull/3385)

A new schema field type, named **`ScalarQuantizedDenseVectorField`**, has been introduced. It enables **scalar quantization** for vector data, which reduces the precision of floating-point values to a smaller number of bits — in this case, either **4** or **7** (default) — therefore reducing memory consumption and speeding up search for vector indexes.

[Take a look at our detailed blog post.](https://sease.io/2026/01/scalar-quantization-of-dense-vectors-in-apache-solr.html)

##### 2) Add Support for Binary Quantized Dense Vector

Jira Issue: [SOLR-17812](https://issues.apache.org/jira/browse/SOLR-17812)  
Solr GitHub PR: [#3468](https://github.com/apache/solr/pull/3468)

A new schema field type, named **`BinaryQuantizedDenseVectorField`**, has been introduced. It enables **binary quantization** for vector data, which reduces the precision of floating-point values to a single bit.  
Similar benefits to scalar quantisation (with a more extreme trade-off)

[Take a look at our detailed blog post.](https://sease.io/2026/01/binary-quantization-of-dense-vectors-in-apache-solr.html)

##### 3) Add Support for PatienceKnnVectorQuery (Early Termination Strategy)

Jira Issue: [SOLR-17814](https://issues.apache.org/jira/browse/SOLR-17814)  
Solr GitHub PR: [#3644](https://github.com/apache/solr/pull/3644)

PatienceKnnVectorQuery is a version of knn vector query that exits early the graph when HNSW queue saturates over a **`saturationThreshold`** for more than **`patience`** times. With this support, we have introduced an **early termination strategy** for knn queries that makes approximate k-NN search faster and more efficient.

[Take a look at our detailed blog post.](https://sease.io/2025/12/faster-vector-search-early-termination-strategy-now-in-apache-solr.html)

##### 4) Add Support for SeededKnnVectorQuery

Jira Issue: [SOLR-17813](https://issues.apache.org/jira/browse/SOLR-17813)  
Solr GitHub PR: [#3705](https://github.com/apache/solr/pull/3705)

SeededKnnVectorQuery is a version of knn vector query that brings a powerful enhancement to vector search capabilities. With this support, users can now perform k-nearest-neighbors (kNN) searches that start from a specific **“seed” query**, to narrow down the candidate set before performing the vector similarity computation. The “seed” query is primarily intended to be a lexical query, guiding the vector search in a hybrid-like way through traditional query logic, i.e. documents matching the seed query will be used as entry points in the HNSW graph exploration.

[Take a look at our detailed blog post.](https://sease.io/2026/02/lexically-accelerated-vector-search-seededknnvectorquery-support-in-apache-solr-10.html)

##### 5) ACORN-Based Filtering in Vector Search

Jira Issue: [SOLR-17815](https://issues.apache.org/jira/browse/SOLR-17815)  
Solr GitHub PR: [#3680](https://github.com/apache/solr/pull/3680)

ACORN (introduced in [this paper](https://arxiv.org/abs/2403.04871)) is an algorithm that presents an optimized solution for **filtered vector search**.   
This approach addresses the performance limitations typically associated with pre-filtering and post-filtering strategies by modifying both the construction and search phases of the HNSW graph.  
With this contribution, Solr now supports the ability to pass the Lucene **`filteredSearchThreshold`** parameter directly as a KNN query parameter. This threshold determines when the ACORN optimization is applied: if the percentage of documents satisfying the filter falls below the specified threshold, the ACORN approach is automatically used.

[Take a look at our detailed blog post.](https://sease.io/2026/03/new-in-apache-solr-10-improved-filtering-in-vector-search-with-acorn.html)

##### 6) Rename Vector Search Parameters and Language Model Modules

Jira Issue: [SOLR-17927](https://issues.apache.org/jira/browse/SOLR-17927)  
Solr GitHub PR: [#3789](https://github.com/apache/solr/pull/3789)

The **`neural`** package has been renamed to **`vector`** and the **`llm`** module has been renamed to **`language-models`**. This change is purely a code-level refactoring and does not affect end users.

The HNSW parameters **`hnswMaxConnections`** and **`hnswBeamWidth`** have been renamed to **`hnswM`** and **`hnswEfConstruction`**, respectively. These changes **do affect users**, who must update the corresponding entries in their **`schema.xml`** file when upgrading Solr.   
However, fallback support for the legacy names (**`hnswMaxConnections`**, **`hnswBeamWidth`**) has been included to reduce friction during upgrades and maintain backward compatibility.

## Learning to Rank

##### Add Feature Vector Caching for Ranking

Jira Issue: [SOLR-16667](https://issues.apache.org/jira/browse/SOLR-16667)  
Solr GitHub PR: [#3433](https://github.com/apache/solr/pull/3433)

Solr already includes a cache mechanism for Learning to Rank feature vectors; however, it is limited to the feature logging phase and not used during reranking. Our contribution extends this capability by introducing a new Learning to Rank cache that Solr leverages in both phases, significantly improving search performance.  
In our blog post, you will find a detailed explanation of the new cache, along with a benchmark comparing it to the previous implementation, which confirms the significant performance improvements achieved with the new cache.

[Take a look at our detailed blog post.](https://sease.io/2026/03/apache-solr-new-learning-to-rank-cache.html)

## Power the Future of Solr

Contribute or sponsor! Every pull request, bug report, documentation improvement, and donation helps the community deliver faster fixes, stronger features, and more reliable releases for everyone.

## Power the future of Solr

Contribute or sponsor! Every pull request, bug report, documentation improvement, and donation helps the community deliver faster fixes, stronger features, and more reliable releases for everyone.