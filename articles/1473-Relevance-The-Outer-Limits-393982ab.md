---
title: 'Relevance: The Outer Limits'
company: Tunkelang
tag: 搜索相关性
date: 2025-12-09
url: https://dtunkelang.medium.com/relevance-the-outer-limits-f5d51aec700a?source=rss-5f6b5aba680------2
account: Tunkelang
origin: en-rss-feedbody
---
[Search is not only about ranking](https://dtunkelang.medium.com/beyond-ranking-focus-on-content-and-query-understanding-4233bc7101f0). Ranking orders results, but retrieval defines the set of [relevant](https://dtunkelang.medium.com/ranking-vs-relevance-ba672c79625e) results that ranking acts upon. Retrieval determines which users can discover for a given query. In practice, [retrievability](https://dtunkelang.medium.com/using-retrievability-to-measure-recall-b991eb241ded) is what makes results discoverable.

### Query Vector

Modern embeddings and approaches like the [bag-of-documents model](https://dtunkelang.medium.com/modeling-queries-as-bags-of-documents-b7d79d0916ab) represent the relationship between queries and content with impressive fidelity. They allow us to estimate where relevant content resides in vector space and how closely any given result aligns with that expectation. This is a critical step towards quantifying relevance.

However, a key question remains: how do we determine the boundary of relevance itself? The query vector computed through the bag-of-documents model identifies the center of relevant content, but it provides no principled answer for how far from that center retrieval should explore. This boundary is not merely a ranking threshold. It defines recall, discovery, and evaluation. Indeed, it determines the shape of the result set that the system treats as relevant.

### Query Specificity

The bag-of-documents model offers another useful signal: [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb). Query specificity measures the mean cosine similarity of a relevant result to the query vector. Variations might use the median, a percentile, or another [statistic](https://dtunkelang.medium.com/a-statistical-sense-of-direction-ca335900ef91).

In theory, query specificity could serve as a principled way to compute the relevance boundary. In practice, there is a circularity problem: we only measure engagement for the results that the search application already retrieves. If we exclude results below a cosine threshold, we never learn whether users might have engaged with them.

### Exploring the Frontier

This challenge parallels [explore-exploit](https://en.wikipedia.org/wiki/Exploration%E2%80%93exploitation_dilemma) methods. Exploration optimizes for learning while exploitation optimizes for what has already been learned. Explore–exploit frameworks aim to manage this tradeoff, usually with application-specific nuance.

These methods work best when they can learn from immediate feedback, as in news feeds or online recommendation systems. Explore–exploit at the level of individual queries only produces meaningful learning for frequent queries. For infrequent queries, the threshold must be tuned in aggregate or inferred from shared structure across semantically related queries.

### Living with Asymmetry

The risks are asymmetric. A threshold that is too high prevents the system from discovering that users would have engaged with excluded results. A threshold that is too low may reduce precision, but users still tend to engage with sufficiently relevant results even if the result list contains some noise. The cost of showing a few irrelevant results is usually lower than the cost of burying relevant ones, particularly when [those relevant results have high desirability](https://dtunkelang.medium.com/not-all-recall-is-created-equal-f160274dd94c).

Moreover, [friction](https://dtunkelang.medium.com/learning-from-friction-to-improve-the-search-experience-8937c71ec97a) itself is a learning signal. If users scroll past higher similarity results to engage with lower similarity content, the search application should amplify its response based on the effort users are investing. This behavior reveals not only the limits of relevance but the cost users are willing to pay to reach it.

### Compute but Verify

The bag-of-documents model computes a query vector and a measure of similarity, but retrieval collapses that measure into a binary decision. If we set and forget a cosine threshold, we risk enshrining suboptimal retrieval policy.

A computed threshold should be treated as a hypothesis that demands validation. By varying the retrieval boundary, measuring engagement distribution, and learning from friction, we can empirically discover the outer limits of relevance and ensure that retrieval does not silently constrain discovery.

The outer limits of relevance should be learned, not assumed.

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=f5d51aec700a)