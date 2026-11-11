---
title: 'The 3 Rs of Search: Relevance, Recall, and Ranking'
company: Tunkelang
tag: 搜索相关性
date: 2020-12-21
url: https://dtunkelang.medium.com/the-3-rs-of-search-relevance-recall-and-ranking-c9a785578653
account: Tunkelang
origin: harvest3-202607
---
# The 3 Rs of Search: Relevance, Recall, and Ranking

In grade school, we were taught the [three Rs](https://en.wikipedia.org/wiki/The_three_Rs): reading, writing, and ‘rithmetic. In search, we can be thankful that the three Rs actually start with the letter R: relevance, recall, and ranking.

### Relevance

Relevance is the [prime directive](https://en.wikipedia.org/wiki/Prime_Directive) of search: the guiding principle for a search engine is to return results that satisfy the searcher’s information need. That means [understanding](https://queryunderstanding.com/introduction-c98740502103) what the searcher wants and retrieving relevant results.

Achieving relevance is a trade-off between [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision) and [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall). We’ll discuss recall in a moment, but precision is the measure that people associate most with relevance: the fraction of results that satisfy — or at least directly relate to — the searcher’s information need.

People often conflate relevance with ranking. It’s true that relevance matters disproportionately for the top-ranked results: irrelevant results at the top of the results frustrate searchers and erode their trust. But relevance is more and less than ranking. More, because it applies to query understanding and all of the results, not just the results ranked at the top. Less, because relevance is necessary — but not sufficient — to optimize the search experience.

Of the three Rs, relevance is the most important. Without relevance, search is a mindless retrieval documents that contain the search keywords. Searchers expect better from a modern search engine. They expect results that relate to their information needs — that is, they expect relevance.

### Recall

There’s more to search than precision. There’s also recall, the fraction of relevant results that are retrieved. Recall is about “the whole truth”, while precision is about “nothing but truth”.

Search engines generally have to manage a trade-off between precision and recall: efforts to improve one almost always come at the expense of the other. Given the primacy of precision, search engines often err on the side of precision. That’s understandable, but [recall deserves some attention](https://queryunderstanding.com/in-search-of-recall-cf42f5f69da9).

Recall is especially important for searchers that would otherwise return few or no results. It’s also critical for cases where searchers care about aggregate information about the results, such as the total number of results or the distribution of attributes of those results. And in some cases, finding even a single relevant result is so important that searchers are willing to wade through many irrelevant results to find the information they are looking for.

Recall may not be quite as important as relevance for most search applications, but it’s important not to throw recall under the bus in the quest to optimize for relevance. They both matter, and sometimes recall is critical.

### Ranking

Finally, we get to ranking. Given the emphasis on the first page of results, search engine developers often prioritize investment in ranking. Ranking is indeed important enough to be the third R of search.

As discussed earlier, relevance is necessary but not sufficient to optimize the search experience. Relevance is essentially binary: a result either does or doesn’t relate to the searcher’s information need. Ranking orders relevant results based on their desirability, using factors like popularity, recency, or price. Ranking can also be personalized, reflecting user-specific preferences.

Many search engines fold relevance into ranking, which is — in my view — a mistake. While relevance is binary, the preferences that should affect ranking exist on a wider spectrum. Ranking should never serve as a substitute for establishing relevance. But ranking is critical, especially for queries that return large result sets. Searchers are lazy, so search engines should place the most desirable, relevant results at the top.

### Summary

There you have it, the three Rs. Relevance, recall, and ranking are the ingredients for great search. There’s a fourth R that deserves mention: refinements. But that’s a subject for another post. In the meantime, I hope these three Rs provide a simple framework for thinking about search.
