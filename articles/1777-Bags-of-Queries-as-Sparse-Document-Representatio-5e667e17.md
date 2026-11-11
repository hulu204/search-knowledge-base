---
title: 'Bags of Queries as Sparse Document Representations'
company: Tunkelang
tag: 召回
date: 2024-05-28
url: https://dtunkelang.medium.com/bags-of-queries-as-sparse-document-representations-bc450db3e814
account: Tunkelang
origin: harvest3-202607
---
# Bags of Queries as Sparse Document Representations

There is a [duality between search queries and indexed documents](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599): we can model a query as a [bag of documents](https://queryunderstanding.com/query-similarity-49dde9f78043) and a document as a [bag of queries](https://queryunderstanding.com/indexing-by-intent-6645ed26d033). This duality offers a way to visualize and frame the relationship between [intents](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f) and ways to fulfill those intents.

Representing queries as bags of documents is a simple, intuitive way to align query and document representations. This representation unlocks opportunities to improve [retrieval, ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e), and [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043) — particularly for [e-commerce search applications](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d).

This post explores this less obvious side of the duality: representing documents as bags of queries.

### A bag of queries — but which queries?

Just as we can map a query to its relevant documents, we can map a document to the queries for which it is relevant. All we are doing is inverting the direction of the mapping.

However, there are infinitely many queries for which a document is relevant. For example, a pair of black men’s Levi jeans is relevant to queries that include “jeans”, “mens levis”, “black clothing”, etc.

For the bag-of-queries model to be a practical query representation, we need to reduce this space to a tractable set of queries that covers most of the intents associated with a query. In other words, we have a [clustering](https://en.wikipedia.org/wiki/Cluster_analysis) problem: we want to represent the space of query intents with queries that represent coherent, distinctive clusters.

We can generate these query clusters by applying three strategies:

- **Prioritize frequent queries.** Since our goal is to maximize coverage of the intent space, we should focus on queries that represent actual searcher traffic. This strategy works well when queries follow a [Zipfian](https://en.wikipedia.org/wiki/Zipf%27s_law) or [power-law](https://en.wikipedia.org/wiki/Power_law) distribution, in which case a small or moderate set of queries comprise a disproportionate share of traffic.

- **Canonicalize similar queries.** [Mapping equivalent or near-equivalent queries to the same representation](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d) allows a single canonical query to cover more of the intent space. Queries that vary only in [stemming (or lemmatization)](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) and word order usually map to the same intent.

- **Minimize gaps.** While canonicalizing similar queries removes queries to avoid redundancy, we also want to avoid gaps in the space of intents for which the document is relevant. If the document is relevant to a query, that query should be highly similar to at least one query in our set.

Rather than cluster the queries for each document separately, we can more efficiently compute a document-independent clustering. Specifically, we can cluster the most frequent queries (e.g., the top million) that hopefully comprise a large fraction of search traffic. We can construct an [undirected graph](https://en.wikipedia.org/wiki/Graph_(discrete_mathematics)#Undirected_graph) of these queries, connecting each query to its most similar neighbors with weights based on their [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043). We then apply any [graph clustering algorithm](https://en.wikipedia.org/wiki/Community_structure#Algorithms_for_finding_communities) to this graph. Finally, we can assign each cluster a canonical query based on its frequency and [centrality](https://en.wikipedia.org/wiki/Centrality) within the cluster.

### How do we apply the bag-of-queries representation?

The bag-of-queries model provides a [sparse](https://en.wikipedia.org/wiki/Sparse_matrix) document representation that can be useful for retrieval and ranking. In particular, it can be used as either a positive or negative relevance signal:

- **Positive relevance signal.** If a frequent query belongs to a query cluster that is part of a document’s bag of queries, then that document is probably relevant and should be included in the results. Moreover, if the document also has high [desirability](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b) (e.g., a best-selling product), it should be highly ranked. This approach can also be used for infrequent queries if they can be mapped to vectors and the query clusters are stored in a specialized index that supports nearest-neighbor retrieval.

- **Negative relevance signal.** If a frequent query does not belong to any query clusters that are part of a document’s bag of queries, then that document is probably irrelevant and should not be included in the results. This negative signal can be useful to avoid returning documents that have desirability but low relevance. Again, this approach can also be used for infrequent queries using nearest-neighbor retrieval.

The bag-of-queries representation is also useful for [using retrievability to measure recall](https://queryunderstanding.com/using-retrievability-to-measure-recall-b991eb241ded).

### Why use a sparse document representation?

The bag-of-queries model provides a sparse document representation that can be useful as either a positive or negative relevance signal. But why use a sparse document representation rather than a dense one?

Dense representations provide a richer signal than sparse ones. However, that richer signal comes with significant costs. Dense representations can significantly increase index size. Moreover, retrieval from a vector database tends to be more expensive than retrieval from an inverted index. Finally, computing cosine similarity is more expensive than determining whether the intersection of two sets is non-empty.

Does a sparse document representation provide enough signal to establish whether a result is relevant? If so, we can obtain much of the benefit of a dense representation at a significantly lower cost.

### Summary

The duality between queries and documents allows us to model queries as bags of documents and documents as bags of queries. This post has focused on using this second, less intuitive side of the duality as a sparse document representation. Hopefully, it offers a useful tool to obtain some of the benefits of dense representations while avoiding some of their cost.
