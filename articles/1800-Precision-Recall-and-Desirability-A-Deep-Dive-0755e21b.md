---
title: 'Precision, Recall, and Desirability: A Deep Dive'
company: Tunkelang
tag: 评测
date: 2025-03-27
url: https://dtunkelang.medium.com/precision-recall-and-desirability-a-deep-dive-822d931256c8
account: Tunkelang
origin: harvest3-202607
---
# Precision, Recall, and Desirability: A Deep Dive

This post expands on my previous discussion of “[Precision, Recall, and Desirability](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b),” diving deeper into defining, motivating, measuring, identifying, and addressing these key search concerns.

## Precision

### What is precision?

[Precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision) quantifies what most people mean by relevance: the fraction of search results that satisfy or directly relate to the searcher’s intent. Traditional precision treats relevance as binary and ignores position, weighing all results equally. A more sophisticated approach incorporates graded relevance and positional weighting, leading to metrics like [discounted cumulative gain (DCG)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain).

### Why does precision matter?

[Relevance](https://queryunderstanding.com/the-3-rs-of-search-relevance-recall-and-ranking-c9a785578653) — captured by precision — is the prime directive of search. A search engine must return results that satisfy the user’s information need. Precision is necessary but not sufficient; desirable yet irrelevant results will not satisfy users or drive positive business outcomes.

### How to measure precision?

- **Human Judgments:** Traditional precision measurement relies on [human judges](https://queryunderstanding.com/evaluating-search-using-human-judgement-fbb2eeba37d9) assessing relevance across a [stratified sample](https://en.wikipedia.org/wiki/Stratified_sampling) of queries, typically focusing on top-ranked results.

- **LLM-Based Judgments:** [Large language models (LLMs)](https://en.wikipedia.org/wiki/Large_language_model) provide a scalable, cost-effective alternative to human judges, though their [judgment quality remains debated](https://arxiv.org/abs/2408.08896).

- **Model-Based Evaluation:** Using an existing [relevance model](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) to assess precision can be useful but lacks independence if that model is used for retrieval or ranking. Still, it can be a helpful negative signal.

- **Unsupervised Approaches:** Metrics like [result coherence](https://queryunderstanding.com/query-specificity-a6156f4043eb) or [self-similarity](https://queryunderstanding.com/is-similarity-objective-92e1f3a4c236) can serve as cost-effective proxies for precision without requiring explicit relevance judgments. Again, they are most useful as negative signals.

### How to identify queries that suffer from low precision?

- **Search Engagement Metrics:** [Behavioral signals](https://queryunderstanding.com/evaluating-search-measuring-searcher-behavior-5f8347619eb0) like low click-through rates (CTR) often signal poor precision, but they conflate precision and desirability problems.

- **Dissimilar Engagement:** If users interact with results vastly different from top-ranked ones, the issue is likely precision rather than ranking.

- **Query Reformulation & Filtering:** Frequent [query reformulation or filtering](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02) also suggest precision problems, especially if searchers end up engaging with results very dissimilar from those of the original query.

### How to address precision problems?

- **Query Categorization:** Filtering results to [categories](https://queryunderstanding.com/categories-are-fundamental-for-search-7be3dba9f880) matching the query intent — or at least boosting them — can dramatically improve precision. However, this approach requires a robust [content representation](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974).

- **Pseudo-Relevance Feedback:** Unsupervised approaches like [pseudo-relevance feedback](https://en.wikipedia.org/wiki/Relevance_feedback#Pseudo_relevance_feedback) rerank results to promote those similar to top-ranked ones, potentially improving precision — though possibly at the cost of reducing [diversity](https://queryunderstanding.com/thoughts-on-search-result-diversity-1df54cb5bf4a).

- **Query Triage:** Diagnosing low-precision queries through [query triage](https://queryunderstanding.com/effective-query-triage-31b4e6b116a4) can reveal patterns that inspire targeted fixes.

## Recall

### What is recall?

While precision measures the fraction of retrieved results that are relevant, [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall) measures the fraction of relevant documents retrieved. Precision ensures “nothing but the truth,” while recall ensures “the whole truth.” However, [not all recall is created equal](https://queryunderstanding.com/not-all-recall-is-created-equal-f160274dd94c) — omitting a best-selling product in e-commerce is far worse than missing a less popular one.

### Why does recall matter?

Recall ensures searchers see all of the relevant content that is available. Low recall leads to searcher dissatisfaction and lost revenue. However, optimizing recall often conflicts with precision, requiring a careful tradeoff in the retrieval strategy.

### How to measure recall?

- **Sampling-Based Estimation:** Since assessing all unreturned results is impractical, recall can be estimated using a [stratified sample](https://en.wikipedia.org/wiki/Stratified_sampling) of results retrieved by strategies with different precision-recall tradeoffs.

- **Retrievability Analysis:** An alternative to directly measuring recall is measuring [retrievability](https://queryunderstanding.com/using-retrievability-to-measure-recall-b991eb241ded): how often a document appears in search results for queries that should retrieve it, weighted by query frequency.

### How to identify queries that suffer from low recall?

- **Null or Low Result Counts:** Queries returning [few results](https://queryunderstanding.com/making-sense-of-null-and-low-results-a077f37bf8fc) may suffer from low recall, though other factors (e.g., high [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb)) can also be responsible.

- **Low-Specificity Queries with Few Results:** Broad queries — that is, queries with low specificity — should typically return large result sets. Low-specificity queries with few results suggest a recall problem.

- **Alternate Retrieval Strategies:** Testing recall-heavy retrieval methods to see which queries are most sensitive to precision-recall tradeoffs can highlight recall-deficient queries.

- **Retrievability Analysis:** If document fails to appears in search results for frequent queries that should retrieve it, it has a recall problem.

### How to address recall problems?

- **Query Expansion:** [Synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) are a classic approach to improve recall, [expanding](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) words or phrases using a dictionary, as are [stemming and lemmatization](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45). However, loss of context can hurt precision, e.g., “wine glass” -> “wine eyeglasses”, so it is best to combine these approach with a [guardrail that protects precision](https://medium.com/@dtunkelang/real-talk-about-synonyms-and-search-bb5cf41a8741), such as query categorization.

- **Query Relaxation:** More aggressive than query expansion, q[uery expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) makes one or more query terms optional. However, optionalizing a critical term can drastically hurt precision. Like query expansion, it benefits from a guardrail that protects precision.

- **Whole-Query Expansion:** In contrast to dictionary-based query expansion, [whole-query](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) expansion [maps queries to intents](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f) and retrieves results for [similar queries](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d), avoiding context loss inherent in token-level expansion. However, this approach requires mapping queries to [embeddings](https://en.wikipedia.org/wiki/Word_embedding) and retrieving their [nearest neighbors](https://en.wikipedia.org/wiki/Nearest_neighbor_search).

Balancing precision and recall is a core challenge of search optimization, particularly retrieval. Understanding these metrics and their tradeoffs is crucial for delivering a robust search experience.

## Desirability

### What is desirability?

For most search applications, [ranking should consider more that just relevance](https://queryunderstanding.com/minimalist-models-for-search-ranking-847c9d247f4). Query-independent factors, such as popularity, quality, or recency, often determine which relevant results to present to searchers on the first page and in what order. The combination of these signals reflects the desirability of the results.

### Why does desirability matter?

Desirability determines which relevant results are most useful to searchers. However, desirability is not a substitute for relevance. If a search engine prioritizes desirability over relevance, it may promote highly desirable but irrelevant results. Conversely, if it ignores desirability, it may fail to surface the most useful relevant results. [Either mistake](https://queryunderstanding.com/ranking-vs-relevance-2-pitfalls-and-how-to-avoid-them-228ab206671a) can lead to dissatisfied searchers experiences and poor business outcomes.

### How to measure desirability?

- **Engagement Probability:** A practical approach is measuring the desirability of a result as its historical [probability of engagement (e.g., clicks or conversions) conditioned on relevance](https://queryunderstanding.com/minimalist-models-for-search-ranking-847c9d247f4).

- **Position Bias Adjustment:** Engagement metrics must account for position bias since higher-ranked results naturally attract more clicks, even if they are not the most desirable.

- **Content-Based Modeling:** Because engagement data is sparse, we can train a [regression model](https://en.wikipedia.org/wiki/Regression_analysis) on content features (e.g., ratings, freshness) to predict desirability beyond direct behavioral signals.

### How to identify queries that suffer from low desirability?

- **Low Engagement Despite High Precision:** Queries that have high precision but low engagement likely exhibit desirability problems.

- **Engagement on Lower-Ranked Results:** If searchers frequently engage with lower-ranked results that are similar to top-ranked ones, the ranking model may not be effectively prioritizing desirability.

- **Query Reformulation Without Precision Issues:** Frequent reformulations or filtering that ultimately lead to similar results may indicate that searchers are seeking more desirable options.

### How to address desirability problems?

- **Improving Content Representation:** Enhancing content features that affect desirability (e.g., quality, popularity) can lead to better ranking.

- **Separating Relevance from Desirability:** Ensuring that ranking models distinguish between query-dependent relevance and query-independent desirability can [prevent ranking errors](https://queryunderstanding.com/ranking-vs-relevance-2-pitfalls-and-how-to-avoid-them-228ab206671a).

## Summary

Precision, recall, and desirability are key concerns that every search application needs to address. Not only should a search application strive to tell the whole truth (recall) and nothing but truth (precision), but it also needs to promote desirable results based on query-independent factors like recency, popularity, and quality. Hopefully this post helps you understand, identify, and address these three concerns. Mastering them is crucial for delivering an optimal search experience that satisfies users and drives business success.
