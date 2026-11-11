---
title: 'In Search of Recall'
company: Tunkelang
tag: 召回
date: 2020-12-20
url: https://dtunkelang.medium.com/in-search-of-recall-cf42f5f69da9
account: Tunkelang
origin: harvest3-202607
---
# In Search of Recall

Search developers tend to focus most of their efforts on the first page of results. As a result, they prioritize investment in ranking models, with the goal of improving quality and business metrics, such as relevance and conversion.

### **Precision and Recall**

In information retrieval terms, this focus on the first page corresponds to an emphasis on [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision), the fraction of results that are relevant. To be more precise — no pun intended — it corresponds to an emphasis on position-biased precision measures like [discounted cumulative gain (DCG)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain).

But precision isn’t the only measure of search quality. There’s also [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall), which measures the fraction of potentially good results that are retrieved. Recall is about “the whole truth”, while precision is about “nothing but truth”.

There’s a tradeoff between precision and recall: efforts to improve one almost always come at the expense of the other. But search developers tend to invest less into recall than into precision, and their investments in recall are often crude. That’s a shame, since recall dramatically affects the search experience.

### **When Recall Really Matters**

There are three search scenarios where recall is especially important:

- **Searches that return no results or only a few results.** For these searches, even a small increase in recall can have a critical impact. When the number of results is low, the expected benefit of increasing recall tends to outweigh the expected cost of decreasing precision.

- **Searches for which the best results do not match the keywords.** The matching failure may reflect a vocabulary gap, redundant query words, or spelling errors. It may not be obvious from the number of results that there’s a recall problem, but the missing results negatively impact metrics.

- **Searches where searchers override default ranking**, e.g. [sorting by price](https://medium.com/@dtunkelang/why-is-it-so-hard-to-sort-by-price-2a5e63899233). Searcher-specified sorts generally do not promote relevant results — for example, the lowest-price results are unlikely to be relevant. Hence, search needs to manage a precision-recall tradeoff for the entire result set.

Recall affects more than just the search results. It also affect aggregates, like the total number of results and [counts for facet values](https://medium.com/@dtunkelang/facets-of-faceted-search-38c3e1043592#bf2e-6458a03f1ced). These aggregates, which are especially useful for [broad queries](https://medium.com/@dtunkelang/broad-and-ambiguous-search-queries-1bbbe417dcc), can be sensitive to the precision-recall tradeoff for the entire result set.

### **Improving Recall**

There are three main ways to improve recall.

- [**Query expansion**](https://queryunderstanding.com/query-expansion-2d68d47cf9c8): a [reductionist](https://medium.com/@dtunkelang/query-understanding-divided-into-three-parts-d9cbc81a5d09) approach that expands words or phrases using a dictionary. This approach is simple, but it does not respect context (e.g., wine glasses -> wine eyeglasses). It works best [in conjunction with an approach that ensures precision](https://medium.com/@dtunkelang/real-talk-about-synonyms-and-search-bb5cf41a8741), such as query categorization. It’s best to keep the dictionary size manageable, as well as to avoid conflating [spelling](https://queryunderstanding.com/spelling-correction-471f71b19880) and [stemming](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) word variations with semantic synonyms.

- [**Query relaxation**](https://queryunderstanding.com/query-relaxation-342bc37ad425): instead of expanding words, it relaxes them, i.e., makes them optional. The challenge is choosing which words to relax. Relaxation can drastically affect the precision-recall tradeoff, so it’s important to choose words wisely. Relaxation aims to choose the least important words, but simple statistical measures like [inverse document frequency](https://en.wikipedia.org/wiki/Tf%E2%80%93idf#Inverse_document_frequency) (idf) may not recognize importance in context (e.g., desk and chair -> desk chair).

- **Whole-query expansion**: in contrast to dictionary-based query expansion, this [holistic](https://medium.com/@dtunkelang/query-understanding-divided-into-three-parts-d9cbc81a5d09) strategy expands the query to include the results of [similar queries](https://medium.com/@dtunkelang/search-queries-and-search-intent-1dec79ad155f). Whole-query expansion maps the query to an intent and then expands the results based on other queries with similar intent. This approach is powerful: unlike dictionary-based expansion, it doesn’t suffer from loss of context. But it requires having a mapping of queries to [embeddings](https://en.wikipedia.org/wiki/Word_embedding), as well being able to obtain a query’s [nearest neighbors](https://en.wikipedia.org/wiki/Nearest_neighbor_search).

### **Summary**

Precision is important for the happy path where searchers find great results on the first page using the default ranking. But recall matters too, and not just for queries that would otherwise return few results. Recall is critical for non-default sorts, as well as for computing useful aggregates like facet counts. There are at least three ways to improve recall: dictionary-based query expansion, query relaxation, and whole-query expansion. Search developers invest in all three of these approaches, and not just in better ranking.
