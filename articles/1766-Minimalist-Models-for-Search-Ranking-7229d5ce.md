---
title: 'Minimalist Models for Search Ranking'
company: Tunkelang
tag: 排序
date: 2024-01-08
url: https://dtunkelang.medium.com/minimalist-models-for-search-ranking-847c9d247f4
account: Tunkelang
origin: harvest3-202607
---
# Minimalist Models for Search Ranking

Search application developers put a lot of effort into optimizing the ranking of search results, especially in areas like ecommerce, where incremental ranking improvements translate directly to revenue. As a result, there have been decades of investment into methods that [apply machine learning to ranking](https://en.wikipedia.org/wiki/Learning_to_rank), and, more recently, into neural approaches.

Rather than rehashing my concerns about [distinguishing ranking from relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e), I thought I’d take a different approach and explore some minimalist models for search ranking.

### Relevance-Only

The simplest approach to ranking, harking back to the earliest work on information retrieval, is to focus entirely on relevance. A relevance-only model only considers query-dependent signals indicating how well a result responds to the search intent expressed in the query, and ignores query-independent signals, such as popularity, quality, or recency.

The relevance model that [Gerard Salton](https://en.wikipedia.org/wiki/Gerard_Salton) proposed in the 1960s was a [vector space model](https://en.wikipedia.org/wiki/Vector_space_model). His vectors represented queries and documents as [bags of words](https://en.wikipedia.org/wiki/Bag-of-words_model). Today, we can do much better by representing queries and documents using [embeddings](https://en.wikipedia.org/wiki/Sentence_embedding).

Regardless, a relevance-only ranking model offers an appealing simplicity: we can use [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) as the scoring function. The quality of the model will depend how well the vectors represent documents and queries. But such a model captures the idea of ranking solely based on relevance.

### Relevance + Desirability

For most search applications, ranking should consider more that just the relevance of the results. Query-independent considerations, such as popularity, quality, or recency, often determine which relevant results to present to searchers on the first page, and in what order. We can summarize all query-independent signals in a single model of desirability.

The simplest way to combine relevance and desirability in a ranking model is to treat relevance as binary. In this approach, a relevance model computes the probability that a result is relevant. If the result is relevant, then its utility is equal to its desirability. Otherwise, the result has no utility.

A direct way to implement this approach is to score results based on their expected utility — that is, the product of their relevance probability and their query-independent desirability.

An alternative is to filter results based on a threshold relevance probability, and then sort them by their query-independent desirability. This approach embraces [satisficing rather than maximizing expected utility](https://queryunderstanding.com/helping-searchers-satisfice-through-query-understanding-10ac5320fc98).

### Query-Dependent Tradeoff

Combining relevance with desirability gets us pretty far, but it doesn’t allow us to manage the tradeoff between query-dependent relevance and query-independent desirability beyond either maximizing an expected value or satisficing by using a relevance threshold. So let’s add one more wrinkle.

Some search intents are very specific. For someone looking for a specific product or document, anything other than an exact match may be useless. At the other extreme, a searcher with a more open-ended intent may be open to exploring desirable but less relevant results. To address this spectrum of intent specificity, we need to accept that relevance isn’t binary.

We can model intent specificity as a function of the query. If we have seen enough historical behavior for a query, we can analyze the distribution of relevance scores (ignoring desirability) for results that searchers have engaged with, taking care to account for position or other sources of presentation bias. To address less frequent or unseen queries, we can train a machine learning model based on similar queries.

Ultimately, we can capture intent specificity in a single parameter that expresses, as a function of the query, the rate of exchange at which searchers (on average) are willing to trade relevance for desirability.

### Minimalist ≠ Easy

These models are minimalist, but the principles they express are deep and fundamental. Though minimalist, these models may not be easy to implement, since they depend on robust representations of documents and queries. Still, I hope this framing at least provides some useful guidance!
