---
title: 'Documents, Queries, and Categories'
company: Tunkelang
tag: 查询理解
date: 2024-11-25
url: https://dtunkelang.medium.com/documents-queries-and-categories-44a1e284a055
account: Tunkelang
origin: harvest3-202607
---
# Documents, Queries, and Categories

I have published a number of posts and presentations about the [bag-of-documents model](https://medium.com/search?q=bag+of+documents+model), which essentially represents query intent as a distribution in a document vector space. Conversely, I have written about the [bag-of-queries model](https://medium.com/search?q=bag+of+queries+model), a dual that represents a document as a distribution over the queries for which it is relevant. More recently, I have argued that [categories are fundamental for search applications](https://queryunderstanding.com/categories-are-fundamental-for-search-7be3dba9f880) and described [ways to obtain them](https://queryunderstanding.com/where-do-categories-come-from-d214c3e6141c).

Documents, queries, and categories are all key ingredients for building successful search applications. This post aims to tie them together.

### Queries represent the distribution of documents they target.

To review, the bag-of-documents model represents a query as a distribution over the vectors of documents relevant to the query. For frequent queries, it is possible to simply aggregate documents based on a query’s engagement history (i.e., clicks and conversions) and compute the mean of their vectors. This process not only produces bag-of-documents representations for frequent queries, but also provides training data to [build a model](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d) that computes bag-of-documents representations for infrequent queries.

Implementation details aside, the key insight is that a query is a partial specification of a document. While a query with high [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) might map to an individual document, most queries have lower specificity and map to a subset of documents. Moreover, while the set of available documents may vary over time, the meaning of a query does not necessarily change. A query represents an information need, which defines a distribution of relevant search results.

### Documents represent the distribution of queries that target them.

There is a [duality between queries and documents](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599): if a query is a bag of documents, then a document is a bag of queries. Specifically, the [bag-of-queries model offers a sparse document representation](https://queryunderstanding.com/bags-of-queries-as-sparse-document-representations-bc450db3e814).

While the bag-of-documents model represents a query as a distribution over the vectors of relevant documents, the bag-of-queries model represents a document as a distribution over the queries to which the document is relevant.

In other words, just as a query is a partial specification of a document, a document is a partial specification of a query. Some documents may only have a single query — or a set of queries that express equivalent search intent — that target them. Other documents are targets for a variety of search intents. Thus, a document can be represented as a distribution over one or more information needs.

### Categories are a unifying abstraction for documents and queries.

While robust document and query representations are essential, it is important to establish an abstraction layer that unifies them.

Categories optimized for coverage, coherence, and distinctiveness relate documents and queries to their most similar neighbors, which also serve as their best [substitutes](https://queryunderstanding.com/is-similarity-objective-92e1f3a4c236). Such categories help ensure the [3 Rs of search: relevance, recall, and ranking](https://queryunderstanding.com/the-3-rs-of-search-relevance-recall-and-ranking-c9a785578653). Moreover, a great way to obtain categories is to [mine frequent queries](https://queryunderstanding.com/where-do-categories-come-from-d214c3e6141c).

### Summary

Understanding the relationship between documents, queries, and categories is essential for building effective search applications. The bag-of-documents and bag-of-queries models illustrate the duality between queries and documents, with each serving as a partial specification of the other. Categories serve as a crucial abstraction layer, ensuring relevance, recall, and ranking. By integrating all three, we can build more robust search applications.
