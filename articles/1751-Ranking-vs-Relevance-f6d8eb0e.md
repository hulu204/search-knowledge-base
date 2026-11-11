---
title: 'Ranking vs. Relevance'
company: Tunkelang
tag: 排序
date: 2022-01-20
url: https://dtunkelang.medium.com/ranking-vs-relevance-ba672c79625e
account: Tunkelang
origin: harvest3-202607
---
# Ranking vs. Relevance

Most folks who work on search worry about relevance. But it’s surprisingly difficult to find a useful definition of relevance.

### Defining Relevance

Merriam-Webster [defines](https://www.merriam-webster.com/dictionary/relevance) relevance as “the ability (as of an information retrieval system) to retrieve material that satisfies the needs of the user.”

[William Goffman](http://garfield.library.upenn.edu/papers/goffman.pdf) defines it as “a measure of information conveyed by a document relative to a query…[but] the relationship between the document and the query, though necessary, is not sufficient to determine relevance*.”*

These strike me less as definitions and more as an “[I know it when I see it](https://en.wikipedia.org/wiki/I_know_it_when_I_see_it)” standard. But they’ll have to do.

### Ranking

Ranking is simply an ordering of results determined by the search engine. Typically, the search engine computes a score for each retrieved result and sorts the retrieved results by that score. We can think of retrieval itself as the [most significant bit](https://en.wikipedia.org/wiki/Bit_numbering#Most_significant_bit) of the score used for ranking: for the purposes of ranking, unretrieved results have a score of zero.

This ranking approach tends to quash diversity: it assigns similar scores to similar results, leading to homogeneity in the top-ranked results. A common technique to increase diversity is reranking top results: demoting near-duplicates or optimizing for some target distribution.

Regardless of how it is implemented, ranking optimizes for a function that reflects searcher and business objectives. For example, ecommerce sites optimize for clicks and purchases — objectives that mostly align the interests of shoppers and retailers. Sometimes there are conflicts of interest, e.g., when the shopper hopes to spend less and the retailers hopes the shopper will spend more. But effective ranking is mostly a win-win.

### Ranking vs. Relevance

There is clearly a relationship between ranking and relevance: searchers expect the top-ranked results to be relevant to their information needs. But beyond that, [things can get a bit messy](https://queryunderstanding.com/putting-search-ranking-in-perspective-1b3094e38105).

As noted earlier, retrieval effectively serves as the most significant bit of the ranking score. If the search engine only retrieves relevant results, then relevance — modeled here as binary — acts as this most significant bit. Relevance isn’t binary, but modeling it as binary is a good approximation — especially for applications where searchers override the default ranking, such as [sorting by price](https://queryunderstanding.com/why-is-it-so-hard-to-sort-by-price-2a5e63899233).

But, if relevance provides the most significant bit, what about the rest of the score? Once the search engine has established relevance, ranking should mostly focus on query-independent signals, such as quality or popularity. To a lesser degree, ranking can take into account prototypicality and non-binary relevance — recognizing that even if all the retrieved results are relevant, [some may be more relevant than others](https://en.wikipedia.org/wiki/Animal_Farm).

Ranking is also an opportunity to make tradeoffs between searcher and business objectives. [Promoted search results](https://queryunderstanding.com/thoughts-on-promoted-search-results-ef124d11492f) play an important role in the search ecosystem, and the ranker is responsible for using them appropriately.

### Summary

Ranking and relevance are related but distinct concepts. Relevance is essentially a binary measure of whether a result addresses the searcher’s need, while ranking sorts relevant results based on searcher and business objectives. Relevance provides the most significant bit to the ranker, while the ranker takes into account query-independent signals, such as quality or popularity, as well as factors like prototypicality. Ranking is also a place to ensure result diversity, through reranking the top-scoring results. Finally, ranking is an opportunity to make tradeoffs between searcher and business objectives, e.g., through promoted search results.

Relevance and ranking are crucial concerns— together with recall, they represent the [3 Rs of search](https://queryunderstanding.com/the-3-rs-of-search-relevance-recall-and-ranking-c9a785578653). But remember to [keep ranking in perspective](https://queryunderstanding.com/putting-search-ranking-in-perspective-1b3094e38105).
