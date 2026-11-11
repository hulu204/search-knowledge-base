---
title: 'Categories are Fundamental for Search'
company: Tunkelang
tag: 查询理解
date: 2024-12-11
url: https://dtunkelang.medium.com/categories-are-fundamental-for-search-7be3dba9f880
account: Tunkelang
origin: harvest3-202607
---
# Categories are Fundamental for Search

As a [search consultant](https://queryunderstanding.com/how-to-be-a-search-consultant-678a44e0cc24), I have learned to be flexible about structured data. However, I do insist on content being [classified](https://medium.com/content-understanding/content-classification-6abd028cae5) into [categories](https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2).

What are categories? Here are a some dictionary definitions:

> a class or division of people or things regarded as having particular shared characteristics

> one of a possibly exhaustive set of classes among which all things might be distributed

> a grouping or classification used to organize items, concepts, or entities that share common characteristics or properties

### Substitutability

These are all reasonable definitions. However, I prefer to frame categories in terms of [similarity or substitutability](https://queryunderstanding.com/is-similarity-objective-92e1f3a4c236). In this framing, the goal to bring together documents (or products) that are substitutable for one another.

For example, in an e-commerce setting, content similarity can be defined as the probability that a buyer wanting to buy product X would buy product Y if X were unavailable, or as the fraction of utility that a buyer wanting to buy X would obtain from buying Y instead.

### Objectives

This notion of similarity or substitutability applies at the level of a pair of documents. Categories build on document similarity to produce [clusters](https://queryunderstanding.com/search-results-clustering-b2fa64c6c809). The quality of the clustering depends on three objectives:

- **Coverage**. Every document should be associated with a category.

- **Coherence**. All documents associated with a given category should be substitutable for one another.

- **Distinctiveness**. Documents associated with different categories should not be substitutable to one another.

Coverage is straightforward. Coherence and distinctiveness build on the document similarity metric. It is also helpful for the definition of each category to be clear to searchers but difficult to quantify this objective.

### Content and Query Classification

If documents are not already associated with categories, then it is important to obtain or establish a set of categories and perform [content classification](https://medium.com/content-understanding/content-classification-6abd028cae5), whether by applying rule-based heuristics or by training a machine-learning model.

Once the content is classified, it is easy to use query logs to train a query classifier that maps queries to categories.

### Benefits

Why are categories so important for a search application? In short, they are key considerations for the [3 Rs of search: relevance, recall, and ranking](https://queryunderstanding.com/the-3-rs-of-search-relevance-recall-and-ranking-c9a785578653).

- **Relevance**. [Relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) is the prime directive of search: the guiding principle for a search engine is to return results that satisfy the searcher’s information need. Given a robust categorization, matching the result category against the query category as establishing the most significant bit of the score used to compute relevance.

- **Recall**. [Recall](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b) measures the fraction of relevant results that are retrieved. If relevance is about search returning “nothing but the truth”, then recall is about returning “the whole truth”. Given a robust categorization, a natural strategy to improve recall is to retrieve candidate results from the same category as the query.

- **Ranking**. Relevance is necessary but not sufficient to optimize the search experience. Ranking orders relevant results based on their desirability, using factors like popularity, recency, or price. Ranking can also be personalized, reflecting user-specific preferences. Using category matching helps ensure that [ranking separates relevance from desirability and other query-independent factors](https://queryunderstanding.com/ranking-vs-relevance-2-pitfalls-and-how-to-avoid-them-228ab206671a).

### Summary

In short, categories are fundamental for search applications. Prioritizing investments in [content understanding](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974), [query understanding](https://queryunderstanding.com/introduction-c98740502103), retrieval and ranking can be challenging. However, robust categorization is a critical foundation upon which everything else depends.
