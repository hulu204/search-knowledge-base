---
title: 'Ranking vs. Relevance: 2 Pitfalls and How to Avoid Them'
company: Tunkelang
tag: 排序
date: 2024-04-29
url: https://dtunkelang.medium.com/ranking-vs-relevance-2-pitfalls-and-how-to-avoid-them-228ab206671a
account: Tunkelang
origin: harvest3-202607
---
# Ranking vs. Relevance: 2 Pitfalls and How to Avoid Them

A crucial distinction for search applications is the [difference between ranking and relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e). In this post, I explain what happens when search applications fail to establish this distinction. Specifically, I describe two common pitfalls: failing to separate relevance from [desirability](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b), and allowing small differences in relevance to overwhelm large differences in desirability. I also suggest ways for applications to avoid these pitfalls.

## Pitfall 1: Not Separating Relevance From Desirability

Relevance is the prime directive of search. If a search application returns results that are not relevant to the query, they are unlikely to lead the searcher to a successful outcome.

Why do search applications return irrelevant results? Sometimes a search application mistakenly computes a result to be relevant, perhaps as the consequence of a [query understanding](https://queryunderstanding.com/introduction-c98740502103) failure. But often the problem is that the scoring function used to rank results combines query-dependent relevance factors with query-independent desirability factors in a way that allows the latter to overwhelm the former.

Relevance is necessary — but not sufficient — for a result to satisfy the searcher. Hence, if a result is not relevant, the probability that it will satisfy the searcher is essentially zero. Otherwise, we can model its desirability as the [conditional probability](https://en.wikipedia.org/wiki/Conditional_probability) that it will satisfy the searcher, given that the result is relevant.

This model is simplistic, particularly in ignoring any differences among searchers. Nonetheless, it is a reasonable approximation of how to properly combine relevance and desirability for search success.

Unfortunately, many scoring functions combine query-dependent relevance factors with query-independent desirability factors as a weighted sum, or through some other function that allows them to compete with each other. This allows desirability factors to overwhelm relevance factors, which in turn ranks desirable but irrelevant results above relevant ones.

When you develop a search application, be vigilant to avoid this common mistake. Cleanly separate query-dependent relevance factors from query-independent desirability factors. Establish a threshold for overall relevance, ideally using a calibrated [relevance model](https://queryunderstanding.com/minimalist-models-for-search-ranking-847c9d247f4) that computes a probability. That at least ensures that you do not make the avoidable mistake of promoting results that your application believes are irrelevant.

## Pitfall 2: Overweighting Small Relevance Differences

While the first pitfall is the failure to separate relevance from desirability, the second almost sounds like its opposite: overweighting small differences in relevance in a way that overwhelms large differences in desirability. But it turns out that these two concerns are not so different.

As discussed earlier, relevance is necessary but not sufficient for a result to satisfy the searcher. But relevance is essentially binary: either a result is relevant, or it is not relevant. This binary model of relevance is simplistic, but it is a reasonable approximation of how searchers evaluate results, with the notable exception of when a search application returns substitutes or partially relevant results because of a [lack of relevant inventory](https://queryunderstanding.com/making-sense-of-null-and-low-results-a077f37bf8fc).

But when two results are both relevant, then the search application should favor the one with higher desirability. Remember that desirability is the conditional probability that a result will satisfy the searcher, given that it is relevant. Hence the probability that a result will satisfy the searcher is its probability of relevance, multiplied by its desirability. If two results have similar probabilities of relevance but significant differences in desirability, then the difference in desirability will dominate.

Unfortunately, many scoring functions inflate small differences in relevance. This allows small differences in the probability of relevance to overwhelm significant differences in desirability, which in turn ranks less desirable relevant results above more desirable relevant results.

Again, when you develop a search application, cleanly separate query-dependent relevance factors from query-independent desirability factors and establish a threshold for overall relevance using a calibrated [relevance model](https://queryunderstanding.com/minimalist-models-for-search-ranking-847c9d247f4). Then either round up the probability from the relevance model — treating all scores above a threshold as a probability of 1 — or multiply the relevance probability by the desirability (the conditional probability that it will satisfy the searcher, given that the result is relevant) to obtain the score as the probability that the result will satisfy the searcher. Computing the score this way will avoid ranking relevant results with lower desirability above relevant results with higher desirability.

## Summary: Relevance, Then Desirability

The main takeaway is: relevance takes priority over desirability, but desirability dominates small differences in probability of relevance. Avoid the above pitfalls by cleanly separating query-dependent relevance factors from query-independent desirability factors and using a calibrated model to establish a probability of relevance. Go forth, and build great search!
