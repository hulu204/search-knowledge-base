---
title: 'Balance Your Search Budget!'
company: Tunkelang
tag: 搜索相关性
date: 2021-10-13
url: https://dtunkelang.medium.com/balance-your-search-budget-e0a4edca636b
account: Tunkelang
origin: harvest3-202607
---
# Balance Your Search Budget!

Search can be computationally intensive. Indeed, search has been the driving force behind many advances in computational efficiency, from [MapReduce](https://en.wikipedia.org/wiki/MapReduce) for distributed indexing to approximate [nearest-neighbor](https://en.wikipedia.org/wiki/Nearest_neighbor_search) methods.

But not all computational investments yields equal return. A search engine has a limited computational budget, so it should allocate that budget wisely to prioritize searcher happiness and business impact.

Here are some recommendations on how to prioritize your investments.

### Where to invest more:

- **Query understanding.** Investing in [query understanding](https://queryunderstanding.com/) offers two advantages. First, the investment is per query, rather than per result, so it doesn’t scale with result set size — and the results are often [cacheable](https://en.wikipedia.org/wiki/Cache_(computing)). Second, query understanding occurs early in the search processing stack, so it has enormous leverage to improve the search experience. In general, when it’s possible to achieve improvements through query understanding, it’s best to do so there, rather than downstream in retrieval or ranking.

- **Autocomplete.** [Autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245) isn’t just a way to reduce searcher effort — though that’s certainly one of its benefits. Autocomplete helps searchers express their intent in a way that aligns with query understanding. A good autocomplete system not only reduces searcher effort, but also improves result quality. Providing useful suggestions to searchers as they type is computationally intensive, but the outsized return justifies the investment.

- **Relevance.** [Relevance](https://queryunderstanding.com/the-3-rs-of-search-relevance-recall-and-ranking-c9a785578653) is the prime directive of search: a search engine should return results that satisfy the searcher’s information need. But relevance is both more and less than ranking. More, because it applies to query understanding and all the results, not just the top-ranked results. Less, because relevance is necessary — but not sufficient — to optimize the search experience. Training a relevance model requires a lot of data and computation, but usually far less than is required for ranking.

- **Navigation and refinement.** It’s impossible to deliver a perfect result set: improvements in retrieval and ranking reach a point of diminishing return. Navigation and refinement options, such as through [faceted search](https://queryunderstanding.com/faceted-search-7d053cc4fada), create opportunities to solicit more signal from the searcher. Searchers don’t like to do extra work, but it’s usually less work to click on refinement options than to paginate through results or come up with different search queries.

### Where to invest less:

- **Query-dependent ranking factors.** Ranking incorporates a blend of query-independent factors, such as popularity and recency, and query-dependent factors, such as the presence of query terms in result fields. Even for sophisticated models, like [gradient boosted decision trees](https://en.wikipedia.org/wiki/Gradient_boosting) and [neural networks](https://en.wikipedia.org/wiki/Artificial_neural_network), the cost tends to be dominated by computing the ranking factors. Query-dependent ranking factors tend to focus on relevance, and an effective relevance model allows ranking to focus on factors that are query-independent — many of which can be computed offline.

- **Scoring large result sets.** Scoring every result in a large result set can get very expensive! At the same time, large result sets often come from [broad search queries](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc) that don’t carry much signal of searcher intent. So don’t overinvest in scoring large result sets, where the return is unlikely to justify the cost. Instead, invest more in navigation and refinement — or on using autocomplete to [nudge searchers towards better, more specific queries](https://queryunderstanding.com/better-search-through-better-queries-c192412a86e9).

- **Personalization.** Knowledge about the searcher may help improve query understanding or ranking. But at best personalization offers secondary signals that supplement the query: as with all context, it’s never enough to overcome the query itself as the primary signal. And personalization signals can be very expensive to compute and use, especially if they require a lot of analysis of user behavior or create a complex representation. A little personalization (e.g., recent searches in autocomplete) can be useful, but don’t overinvest in personalization without commensurate return.

- **Question answering.** Building a system that answers natural language questions can be very exciting, especially to business leaders who don’t appreciate how difficult it is to implement it well. But it tends to have limited value: users still tend to search with keywords (less typing!); question answering systems tend to be brittle beyond the most frequent use cases; and [result snippets](https://queryunderstanding.com/search-result-snippets-e8c447950219) are often good enough. If you really want to use AI in your search engine, consider [applying it to query understanding](https://queryunderstanding.com/ai-for-query-understanding-d8c073095fff).

Every search application is unique, so I can’t promise that these specific recommendations are right for your particular needs. But I hope you come away with an appreciation that building a search system requires ruthless prioritization your computational budget.

Balance that budget wisely!
