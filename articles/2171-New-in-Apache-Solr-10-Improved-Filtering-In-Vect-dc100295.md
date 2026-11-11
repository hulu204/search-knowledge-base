---
title: 'New in Apache Solr 10: Improved Filtering In Vector Search with ACORN'
company: Sease
tag: 召回
date: 2026-03-16
url: https://sease.io/2026/03/new-in-apache-solr-10-improved-filtering-in-vector-search-with-acorn.html
account: 
origin: harvest3-202607
---
Hi readers,

In this blog post, we are excited to share some important news with you:  
**Sease** has **contributed a new feature to Apache Solr** by adding support for configuring the parameter that controls whether ACORN-based filtering is used in Vector Search.

*A special thanks to my colleagues [Anna Ruggero](https://sease.io/about/anna-ruggero) and [Alessandro Benedetti](https://sease.io/about/alessandro-benedetti-2) for their effort*.

ACORN is an algorithm for searching data that combines vectors and structured filters in an efficient and scalable way. This approach overcomes the performance limitations of both pre- and post-filtering, as well as the semantic limitations of specialised indices, achieving up to a 5× speed-up with minimal loss in recall.

***This feature is available starting from Apache Solr 10.0.0***.

Here is how we will explore the topic:

* We briefly mention the academic paper, which inspired the introduction of this feature.
* We then outline how this strategy has been implemented in **Apache Lucene**.
* After that, we describe the open-source contribution we made to **Apache Solr** and explain how to use this new feature.

## ANN Constraint-Optimized Retrieval Network (ACORN)

ACORN is an algorithm that presents an optimised solution for **filtered vector search**.   
It was introduced in the academic [paper](https://arxiv.org/pdf/2403.04871) “ACORN: Performant and Predicate-Agnostic Search Over Vector Embeddings and Structured Data” by Liana Patel, Peter Kraft, Carlos Guestrin and Matei Zaharia (published in 2024).

##### Problem To Address

Many modern applications need to perform hybrid searches on data that combines:

* vectors (or embeddings) representing unstructured elements (e.g. text, images, videos)
* associated structured data (e.g. attributes, metadata, labels, keywords)

For example: on an e-commerce site, find shoes similar to this reference image with a price <100$.   
When performing this type of hybrid search, several strategies can be adopted, but each has its own limitations:

* **Post-filtering**: execute the vector search before applying any filters based on structured criteria. This becomes inefficient when filters are highly selective or poorly correlated with the embedding space, because the system explores many vectors that will later be discarded. As a result, the search may return fewer than the desired *k* results.
* **Pre-filtering**: first apply the filters to obtain a subset of candidates, then perform vector search only within that subset. This can also be costly: if the filter returns very few elements, the vector-graph structure becomes sparse and search navigation degrades; if it returns too many, there is no real performance gain.
* **Specialised hybrid indexes**: some approaches build indexes that combine vectors and attributes, but they typically work only in narrow domains and do not scale to general-purpose use cases.

In short: how can we build an index that allows efficient searches on embeddings + arbitrary filters (predicates), without knowing in advance exactly which filters will be used, and while maintaining high performance?

##### Proposed Approach

The authors propose **ACORN** as a solution. The key ideas are:

* **Extending HNSW**: ACORN builds on the classic HNSW algorithm (Hierarchical Navigable Small Worlds), a graph-based index for approximate nearest-neighbour (ANN) search that is already a standard for embedding-based retrieval.
* **Predicate-subgraph traversal**: when a query contains filters or predicates, ACORN does not traverse the entire graph. Instead, it navigates only the sub-graph consisting of nodes that satisfy the predicate. In other words, it identifies the subset of items meeting the filter, and then performs vector-similarity navigation within that subset.
* **Predicate-agnostic construction**: the graph is built without prior knowledge of which filters will be applied. This avoids the need to pre-index for specific predicates.

The authors introduce two variants: a high-performance variant (**ACORN-γ**) and a lightweight variant (**ACORN-1**).   
Lucene’s implementation is based on ACORN-1, which follows a construction strategy closer to traditional HNSW and defers part of the graph expansion to query time.

During search, ACORN-1 evaluates only nodes that are accepted by the filter, but to reduce the chances of losing relevant sections of the graph, it not only considers a node’s immediate neighbours (one-hop), but also explores two-hop neighbours. This compensates for the lower graph density compared to ACORN-γ and allows ACORN-1 to maintain strong retrieval quality while keeping the index structure more lightweight.

## Apache Lucene Implementation

The ACORN-1 variant was implemented in Apache Lucene in February 2025. Here is the PR [#14160](https://github.com/apache/lucene/pull/14160).

Specifically, it was implemented in

```
				
					org/apache/lucene/util/hnsw/FilteredHnswGraphSearcher.java
				
			
```

and a new HNSW search strategy was added in

```
				
					org/apache/lucene/search/knn/KnnSearchStrategy.java
				
			
```

which exposes a ***filteredSearchThreshold*** threshold for filtered search, a percentage value from 0 to 100 where 0 means never use ACORN optimization, and 100 means always use ACORN optimization.

With a threshold greater than 0, Lucene enables or not ACORN based on this condition:

```
				
					org/apache/lucene/util/hnsw/HnswGraphSearcher.java
				
			
```

```
				
					org.apache.lucene.search.knn.KnnSearchStrategy.Hnsw#useFilteredSearch
if (acceptOrds != null
    // We can only use filtered search if we know the maxConn
    &amp;&amp; graph.maxConn() != HnswGraph.UNKNOWN_MAX_CONN
    &amp;&amp; filteredDocCount &gt; 0
    &amp;&amp; hnswStrategy.useFilteredSearch((float) filteredDocCount / graph.size())) {
  innerSearcher =
      FilteredHnswGraphSearcher.create(knnCollector.k(), graph, filteredDocCount, acceptOrds);
				
			
```

It means that Lucene activates it only if:

* a filter is provided
* the graph’s **`maxConn`** is known
* at least one document passes the filter
* the ratio of documents passing the filter is below the configured threshold

[Empirical tests](https://docs.google.com/spreadsheets/d/1gk1uybtqleVtDUfhWXActyhW8q_lgG1mlMrOohnJRJA/edit?gid=0#gid=0) have shown that this algorithm brings a significant advantage in terms of time and recall when the number of documents eliminated by the imposed filter exceeds 40%. If, on the other hand, the percentage of documents removed is less than 40%, the algorithm performs comparably to HNSW.   
For this reason, a recommended value is 60, so ACORN is used only when the percentage of documents that pass the filter is less than 60%.

Refer to this [blog post](https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search) for more info.

## Our Apache Solr Contribution

Since Solr was recently upgraded to Lucene 10.2.1 (PR: [#3053](https://github.com/apache/solr/pull/3053)), we have been able to expose this new functionality.

In PR [#3680](https://github.com/apache/solr/pull/3680), the ability to pass the Lucene **`filteredSearchThreshold`** parameter directly as a KNN query parameter has therefore been added in Apache Solr.   
*This feature will be available starting from Apache Solr 10.0.0.*

A new parameter has been added to the [KnnQParser](https://github.com/apache/solr/blob/512e02ae637b2831aa489902338207072c4c9684/solr/core/src/java/org/apache/solr/search/neural/KnnQParser.java) class, and the [getKnnVectorQuery](https://github.com/apache/solr/blob/512e02ae637b2831aa489902338207072c4c9684/solr/core/src/java/org/apache/solr/schema/DenseVectorField.java#L377) method has been adapted to accept this parameter and call the appropriate KnnVectorQuery constructor in Lucene:

* **`filteredSearchThreshold`** (default: [Lucene default](https://lucene.apache.org/core/10_2_0/core/constant-values.html#org.apache.lucene.search.knn.KnnSearchStrategy.DEFAULT_FILTERED_SEARCH_THRESHOLD)):  
  An integer value from 0 to 100, where 0 means never use ACORN optimisation and 100 means always use ACORN optimisation; this threshold determines when the ACORN optimisation is applied: if the percentage of documents satisfying the filter falls below the specified threshold, the ACORN approach is automatically used.  
    
  As already said, a recommended value is around 60, based on benchmark results in this [GitHub comment](https://github.com/apache/lucene/pull/14160#issue-2805145799).

Here is an example of a **`knn`** search using a **`filteredS`**

```
				
					?q={!knn f=vector topK=10 filteredSearchThreshold=60}[1.0, 2.0, 3.0, 4.0]&amp;fq=section:0
				
			
```

I hope you enjoyed this blog post and found it useful. Stay tuned for new interesting topics and insights!

## Need Help with this topic?​

If you're struggling with ACORN in Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with ACORN in Solr, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)