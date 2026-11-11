---
title: 'Implicit Query Reformulation'
company: Tunkelang
tag: 查询理解
date: 2023-07-10
url: https://dtunkelang.medium.com/implicit-query-reformulation-426a246e7a62
account: Tunkelang
origin: harvest3-202607
---
# Implicit Query Reformulation

Let me start with the disclaimer that this post describes an embryonic idea, not an approach that I have validated through analysis or experimentation. With that out of the way, let us get into it!

### Query Similarity

As long-time readers know, I have a keen interest in [query understanding](https://queryunderstanding.com/introduction-c98740502103), and especially in [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043). My work with [Aritra Mandal](https://www.linkedin.com/in/aritram/), which he will present in August at the [KDD 2023 Workshop on e-Commerce and NLP](https://sites.google.com/view/ecnlp/), models query similarity by representing queries as “[bags of documents](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599)”.

Query similarity is an old problem, though it has often gone by other names. Much of the older thinking about query similarity focused on query reformulation — or, as I prefer to call it, explicit query reformulation.

### Explicit Query Reformulation

When searchers are not satisfied with the results of search queries, they sometimes reformulate their queries in the hope of finding better results.

For example, a searcher might perform a query for “mens shoes” and then perform a subsequent query for “mens black shoes” or “mens casual shoes” to hone in on a more specific set of results. But query reformulation is not just useful for narrowing results. A searcher might reformulate “crocs” to the broader “foam clogs”, or to the adjacent “birkenstocks”.

Explicit query reformulation is a way for searchers to make more efficient progress on their [search journey](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02) than paginating through long lists of [ranked](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) results or refining results using [facets](https://medium.com/query-understanding/faceted-search-7d053cc4fada). And it is one of the only ways that searchers can improve [recall](https://queryunderstanding.com/in-search-of-recall-cf42f5f69da9) by retrieving additional results.

Hence, it is reasonable to infer that a query and its explicit reformulation often represent similar intents. We may not know whether the reformulated query is narrower, broader, or adjacent to the original query, but we can at least surmise that the intents are probably related.

### Mining Explicit Query Reformulation

Search engine developers have long seen explicit query reformulation as a way to mine pairs of related searches. Pairs of queries that co-occur in [search sessions](https://queryunderstanding.com/session-context-4af0a355c94a) are likely to express similar intents, so they are useful candidates for related query suggestions — or automatic [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8).

The main challenge with this approach is sparsity. While explicit query reformulation is not a rare behavior, it is not especially common either. Moreover, most of the query pairs occur in only once or at most a handful of sessions. Including these infrequent query pairs leads to a lot of noise, but excluding them drastically reduces coverage. In practice, mining explicit reformulations yields only a small set of frequent query pairs.

Is it possible to overcome this sparsity? We probably cannot persuade searchers to perform more explicit query reformulation, nor would we want to impose such an additional burden on them. But what if we can obtain the same signal without requiring them to exert additional effort?

### Implicit Query Reformulation

What searchers do far more often than reformulate search queries is engage with search results. So, can we mine their engagement with search results the same way that we mine explicit query reformulation?

With a bit of effort and nuance, I believe that we can. The trick is to interpret engagement with a result as an implicit query reformulation.

How do we do that? By appealing to the spirit of a “[bag of queries](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599)” model.

Let us return to our “mens shoes” example. If a searcher performs this query and then clicks on a pair of black shoes, we could infer that the searcher was interested in “mens black shoes” — particularly if the click was not on the top-ranked result. We could make the connection from a result to a query by analyzing the click log, perhaps discovering that, had the searcher’s query been “mens black shoes”, the clicked result would have been ranked at the top.

In general, whenever a searcher clicks on a result that would have ranked higher for another query, we can interpret the click as an implicit query reformulation. We have to exercise some care to avoid noise. For example, the difference in rank should be significant, and the candidates for implicit query reformulation should be queries that are reasonably frequent.

The approach has one obvious limitation: searchers can only engage with results that the search engine returns to their queries. So how can such an approach learn adjacent query pairs, such as “crocs” to “birkenstocks”?

Here we rely on retrieval and ranking to create the opportunities for such implicit query reformulations. At least some results returned for a query should be top-ranked results for similar queries that might not match the initial query exactly. The further down the ranking, the more opportunity there is to take such liberties, since the upside outweighs the downside.

### Summary

As per the initial disclaimer, this post is an embryonic idea. I have not yet validated this approach through analysis or experimentation. But it strikes me as a simple way to generalize the idea of query reformulation to overcome its main limitation of scarcity. I hope to try it out soon and share what I learn, or that others will try it and and share their experiences.
