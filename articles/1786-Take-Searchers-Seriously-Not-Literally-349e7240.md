---
title: 'Take Searchers Seriously, Not Literally'
company: Tunkelang
tag: 查询理解
date: 2024-09-04
url: https://dtunkelang.medium.com/take-searchers-seriously-not-literally-146df479cb0d
account: Tunkelang
origin: harvest3-202607
---
# Take Searchers Seriously, Not Literally

Search application developers manage numerous tradeoffs, foremost the tradeoff between [precision and recall](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b). Precision measures the fraction of search results that are relevant, while recall measures the fraction of relevant documents that are retrieved. Precision is about returning “nothing but the truth”, while recall is about returning “the whole truth”.

Unfortunately, many search application developers misinterpret this tradeoff by taking a literal, [reductionist](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) approach to [query understanding](https://queryunderstanding.com/introduction-c98740502103). These developers interpret precision as matching the exact keywords the searcher uses, rather than matching the intent behind those keywords. Unfortunately, this understandable attempt to respect the searcher’s intent is misguided and harms the search experience.

### Synonyms

This problem surfaces in the context of [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) — specifically [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741). In many search applications, results that exactly match query words score higher than results that match through synonym expansion.

Too many search application developers confuse probability of relevance with degree of relevance. Sometimes synonyms represent a slight drift in meaning, such as from sneakers to shoes. Often, however, they represent an equivalence subject to context. For example, the words “company” and “firm” have essentially the same meaning when they refer to commercial businesses, but both words have other meanings in different contexts. There is a big difference between a synonym retaining 80% of the meaning of the original word and there being an 80% probability of retaining all of its meaning — even if they yield essentially the same [expected value](https://en.wikipedia.org/wiki/Expected_value).

For example, consider a search on an e-commerce site for “cell phone chargers”. In this context, “cell” and “mobile” are synonyms with no loss of meaning. Therefore, the search application should treat results for “mobile” phone chargers just like results for “cell” phone chargers. Indeed, it would be a [disservice to searchers](https://queryunderstanding.com/ranking-vs-relevance-2-pitfalls-and-how-to-avoid-them-228ab206671a) and the business to not show the best phone chargers to searchers looking for one, regardless of whether they are indexed as “cell” phone chargers or “mobile” chargers — and regardless of which word the searcher uses in the query.

### Holistic Query Intent

In contrast, searchers are not happy when a search for “cell phone” returns a flood of cell phone accessories, such as cases and chargers. Search application developers may protest that they are [just following orders](https://en.wikipedia.org/wiki/Superior_orders), returning results that exactly match the searcher’s keywords. However, searchers expect search applications to know the difference between a product and its accessories — and to recognize their intent the way a human would. People searching for cell phones want phones, not cases.

Scenarios like these make it clear that query understanding needs to be holistic rather than reductionist. At the very least, a search application should recognize the broad category or categories targeted by the query and avoid hurting precision by including out-of-category results.

### Search Query vs. Search Intent

Fundamentally, search application developers need to manage precision and recall in terms of the searcher’s intent rather than the literal search query. Searchers do not care whether a search application matches their exact keywords; they care whether it matches their exact intent. Search application developers may feel that exact keyword matching improves explainability, but most searchers see those explanations as excuses.

Focusing on the holistic meaning of the query may sound like [AI-powered search](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b), favoring neural over traditional token-based retrieval. Indeed, AI can help address the reductionist errors of token-based approaches. However, that does not mean that search applications need to implement embedding-based retrieval. It may be simpler and more robust to use [query classification](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) and [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043) to understand [search intent](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f).

### Summary: Think Like a Searcher, Not a Developer

Delivering effective search applications requires [empathy with searchers](https://queryunderstanding.com/to-build-better-search-develop-empathy-with-your-users-93a1d29d1903). Focusing on literal search keywords and the computation associated with retrieval and scoring makes sense to developers but is not something that searchers even think about. Searchers expect search to just work, for search applications to understand what they mean. This expectation may be unreasonable. However, it is what searchers expect, and it is the ideal that search application developers have to strive for. Most importantly, it should frame how developers think about search problems and solutions. Search applications need to take searchers seriously, not literally.
