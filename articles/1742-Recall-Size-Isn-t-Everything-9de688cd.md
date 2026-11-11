---
title: 'Recall: Size Isn’t Everything'
company: Tunkelang
tag: 召回
date: 2021-01-04
url: https://dtunkelang.medium.com/recall-size-isnt-everything-8f41ce2fae3f
account: Tunkelang
origin: harvest3-202607
---
# Recall: Size Isn’t Everything

[Recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall) is a key measure of search quality that doesn’t always get [the attention it deserves](https://queryunderstanding.com/in-search-of-recall-cf42f5f69da9). But how does a search engine recognize when recall is a problem?

### Size Matters, But Size Isn’t Everything

Recall measures the fraction of relevant results that are retrieved. Naturally, recall is correlated to the size of the result set. But we have to be careful not to overstate that correlation.

Consider the simplest case: a search that returns no results. A lack of results does not necessarily indicate a recall problem: there may simply be no results that relate to the searcher’s information need. Still, the upside from trying harder to find at least one relevant result generally outweighs the downside, at least if the search engine provides clear messaging to searchers about the techniques, such as [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425), that it uses to obtain those results.

Things become more complicated when there are a few results — or even just a single result. On one hand, a low result count makes it more likely that retrieval failed to include additional relevant results. On the other hand, a small number of results may still represent robust recall. For example, when a searcher [searches for a specific document or product by name](https://en.wikipedia.org/wiki/Known-item_search), the search engine can achieve perfect recall by returning a single result.

At the other end of the spectrum, consider searches that return a large number of results. A large number of results makes it less likely that recall is a problem, but there’s no guarantee. The retrieval strategy may have missed a even larger number of relevant results. Or the retrieved results may be numerous but mostly irrelevant; while there may be a large number of unretrieved relevant results. Also, some results matter more than others, and the retrieved results may not include the most desirable ones.

In short, the size of the result set is a useful signal, but not a definitive one.

So, what other signals can we use to identify recall problems?

### Query Understanding

Recall measures the search engine’s success at finding results that relate to the searcher’s intent. Good result quality in general — and good recall in particular — starts with understanding the searcher’s intent.

[Query understanding](https://en.wikipedia.org/wiki/Known-item_search) transforms queries into representations of search intent. It consists of modules that extract intent signals from queries, rewriting queries and introducing structure. Compared to ranking, query understanding mostly focuses on binary, objective aspects of search intent.

Query understanding provides two kinds of signals to detect recall problems:

- **Confidence**: if query understanding cannot confidently establish the searcher’s intent, then it’s unlikely that the search results will be of good quality — which in turn means that a large number of results is not a strong signal of recall. Examples: a failure to map the query to a [category](https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2), or inability to recognize most of the query terms as [entities](https://queryunderstanding.com/entity-recognition-763cae840a20).

- **Specificity**: if query understanding does confidently establish the searcher’s intent, then it should also be able to estimate the [specificity](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc) of that intent. For example, a [known-item search](https://en.wikipedia.org/wiki/Known-item_search) targets a single result, while a category search generally targets a larger set. If query specificity targets a large result set, then a small result set indicates a recall problem.

### Sensitivity Analysis

Since retrieval is always a tradeoff between precision and recall, another strategy for detecting recall problems is to adjust that tradeoff and observe how it changes the results:

- **Expansion**: if a more aggressive [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) strategy (e.g., using [stemming](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) or [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741)) significantly increases the number of results, there may be an opportunity to meaningfully improve recall. This signal is more robust if the new results are similar to those initially retrieved.

- **Relaxation**: [query relaxation](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741), which makes one or more query terms optional, is another way to test the opportunity to improve recall. Query relaxation tends to be more aggressive than query expansion, so it’s even more important that the new results be similar to those initially retrieved.

- **Removing Constraints**: query understanding can introduce constraints to improve precision, such as phrase-enforcing [segments](https://queryunderstanding.com/query-segmentation-2cf860ade503) or [scoping](https://queryunderstanding.com/query-scoping-ed61b5ec8753) query terms to specific result fields. Removing these constraints adjusts the tradeoff, and is another way to test the opportunity to improve recall.

### Summary

Recall is important. And, while recall is correlated to the size of the result set, more results do not guarantee improved recall. Size matters, but size isn’t everything. Using query understanding and sensitivity analysis, we can adjust the precision-recall tradeoff to find opportunities to improve recall.
