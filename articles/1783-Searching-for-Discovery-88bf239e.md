---
title: 'Searching for Discovery'
company: Tunkelang
tag: 工程相关
date: 2024-08-13
url: https://dtunkelang.medium.com/searching-for-discovery-cef6b7d0ee1f
account: Tunkelang
origin: harvest3-202607
---
# Search and Discovery

If [search](https://queryunderstanding.com/search-the-whole-story-599f5d9c20c) has one job, it is to help searchers find what they are looking for. However, many search application developers feel that search has a second job: to help searchers discover things they are not looking for.

Having worked on both search and discovery, I have found that their relationship is more complicated than most people realize. This post explores that relationship and proposes ways to combine them effectively.

The “happy path” for search is that searchers express their intent through a query, and the search application responds with a list of relevant results, ordered by their desirability to the searcher. Where can — and should — discovery fit into this process?

### First, Do No Harm

Let us start with the [Hippocratic](https://en.wikipedia.org/wiki/Hippocratic_Oath) principle: “first, do no harm.” When a searcher is on an efficient path to a successful search outcome, discovery should not disrupt that path by introducing unnecessary [friction](https://queryunderstanding.com/learning-from-friction-to-improve-the-search-experience-8937c71ec97a). Remember that search is a must-have, while discovery is a nice-to-have. Specifically, discovery should not interfere with [known-item search](https://en.wikipedia.org/wiki/Known-item_search).

So, how can discovery help, rather than harm, the search experience?

### No Results

The most straightforward case for discovery is when the search application cannot provide the result the searcher is looking for, e.g., a [known-item search](https://en.wikipedia.org/wiki/Known-item_search) for which the desired result is [unavailable](https://queryunderstanding.com/making-sense-of-null-and-low-results-a077f37bf8fc). In such cases, discovery offers the searcher alternatives as [substitutes](https://queryunderstanding.com/is-similarity-objective-92e1f3a4c236) for the desired result. It is like the waiter saying, “Sorry, we don’t have Coke. [Is Pepsi ok?](https://www.youtube.com/watch?v=MtmTX7jg0mM)”

### Too Many Results

At the other end of the [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) spectrum, discovery helps searchers narrow their initial queries. [Faceted search](https://queryunderstanding.com/facets-of-faceted-search-38c3e1043592) helps searchers explore large, heterogeneous collections of results (e.g., “shirts”) and refine them by attributes they care about (e.g., material, color). [Search suggestions](https://queryunderstanding.com/search-and-the-art-of-conversation-b2171aa1a802) serve a similar role, whether through [autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245) or post-retrieval. [Broad and ambiguous](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc) queries can be inauspicious starts to the [search journey](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02); discovery helps searchers navigate to successful outcomes.

### Related Results

Discovery helps searchers find results related to their search intent, particularly complementary results like accessories. For example, a searcher shopping for a coffee machine might also be interested in purchasing coffee and filters. It is important to do no harm: related results should not crowd out results directly relevant to the query. Nonetheless, related results are valuable to both the searcher and the business.

### Better Results?

Sometimes discovery helps searchers find better results than the ones they looked for. A better product than what they searched for may be on sale, or there may be an updated version of a document they searched for. In such cases, discovery can lead searchers to better results. “Better” may also be in the eye of the business, e.g. [promoted results](https://queryunderstanding.com/thoughts-on-promoted-search-results-ef124d11492f). Regardless, discovery should not derail the searcher’s happy path.

### Surprise!

The most ambitious use of discovery is to surprise searchers with unexpected results that are not related to their search intent. This use of discovery is risky since the results are irrelevant to the searcher’s stated intent. The gamble is that the delight of the unexpected results — and the business benefit — will justify the [friction](https://queryunderstanding.com/learning-from-friction-to-improve-the-search-experience-8937c71ec97a). In general, it is safest to present such results when they can do the least harm, e.g., on the home page before the searcher has expressed an intent.

To summarize, search has a clear priority of helping searchers find what they are looking for. Discovery can be a helpful and even delightful part of that process, as long as it follows the principle of “first, do no harm”.
