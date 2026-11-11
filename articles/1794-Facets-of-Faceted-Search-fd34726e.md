---
title: 'Facets of Faceted Search'
company: Tunkelang
tag: 搜索相关性
date: 2024-12-03
url: https://dtunkelang.medium.com/facets-of-faceted-search-38c3e1043592
account: Tunkelang
origin: harvest3-202607
---
# Facets of Faceted Search

[Faceted search](https://queryunderstanding.com/faceted-search-7d053cc4fada) is a fascinating topic. It’s a standard feature of site search, and one could write an entire [book](https://www.amazon.com/Synthesis-Lectures-Information-Concepts-Retrieval/dp/1598299999) on the subject. In this post, I’ll focus on some nuances of faceted search that I feel have been neglected in the literature.

**Broad Queries vs. Ambiguous Queries**

Both search engine developers and users treat facets as useful for refining broad search queries. But there’s a tendency to [conflate broad queries with ambiguous queries](https://medium.com/@dtunkelang/broad-and-ambiguous-search-queries-1bbbe417dcc). There’s an important distinction between the two.

Broad queries are unambiguous but underspecified. For example, the query “shirts” expresses a clear but underspecified intent: it includes shirts for men, women, and children; t-shirts and dress shirts; all colors and materials; etc.

In contrast, ambiguous queries do not express a clear intent. For example, the query “mixers” is ambiguous because it’s unclear whether “mixers” refer to kitchen appliances, sound equipment, or several kinds of industrial machines.

Facets are useful for narrowing down broad, unambiguous queries — especially when the large number of results and underspecified search intent limit the usefulness of ranking. In contrast, it’s better to address ambiguous queries with category disambiguation or some other [clarification dialogue](https://queryunderstanding.com/clarification-dialogues-69420432f451).

**Finding vs. Exploring**

Search queries are not the same as [search intent](https://medium.com/@dtunkelang/search-queries-and-search-intent-1dec79ad155f). In particular, broad search queries do not necessarily reflect broad search intent, and that makes a big difference as to how searchers use facets.

Some searchers who type in broad queries know exactly what they’re looking for, but don’t express their narrower search intent in the search box. For example, they may type in “shirts”, even though they have a particular brand of men’s shirts in mind. This can happen for several reasons. They may not know — or may not be able to [spell](https://queryunderstanding.com/spelling-correction-471f71b19880) — the right words to express their specific intent. They may not trust the search engine to [understand](https://queryunderstanding.com/introduction-c98740502103) a more specific query — or to return all relevant results for it. Or they simply may prefer to type less — indeed, they may have been nudged to enter a short query by [autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245). In all of these cases, facets help searchers narrow down the results for their initial broad queries to express a more specific intent.

In other cases, searchers don’t know exactly what they are looking for; rather, they only know enough to express a broad intent. For example, a searcher who doesn’t know much about shirt types, brands, or prices might search for “shirts” in order to see the options for these facets. In general, these searchers use facets as guidance to understand how the inventory is organized, what options are available, and trade-offs among those options. They are using facets to explore and discover.

Facets can serve both searchers who know what they are looking for and those who don’t. But it’s important to keep in mind that these are different use cases. In the first case, facets help searchers find more efficiently; in the second case, facets enable exploration and discovery. These two kinds of searchers tend to have very different kinds of [search journeys](https://medium.com/@dtunkelang/supporting-the-searchers-journey-when-and-how-568e9b68fe02).

**Popularity, Coverage, and Utility**

What about the facets themselves? What makes a particular facet useful for a particular query?

A facet for a search query should satisfy the following three properties:

- Popularity. Facets and their values should represent result aspects that many searchers who perform that query care about, e.g., someone searching for shirts probably cares about their size and color.

- Coverage. Facets should have high coverage among the results, e.g., shirt size has high coverage if the results are all shirts, but has lower coverage if the results also include pants and shoes.

- Utility. Selecting a facet value should significantly (but not entirely!) reduce the number of results, and it should filter out a large fraction of top results, e.g. color is a useful facet for “shirts” but not for “white shirts”.

The simplest way to determine the popularity of facets and values for a query is to measure how often searchers who perform that query use it. This approach is simple and direct, but it suffers from presentation bias (the order in which the search interface presents facets) and sparsity (many queries don’t have enough facet usage to derive a robust distribution). An alternative is to infer facets from queries using [entity recognition](https://queryunderstanding.com/entity-recognition-763cae840a20), e.g., inferring the color facet from the query “black shirts”. Another way to address sparsity is to aggregate queries by category, e.g., aggregating all shirt-related queries. But this approach requires a way to map queries to categories. And the facets won’t be useful for all queries in the category, e.g., color isn’t useful for “white shirts”.

Facet coverage is more straightforward, but there’s a catch: coverage is highly sensitive to the search engine’s retrieval strategy. Most search engines rely on ranking to promote relevant results to the first page, but doing so often hides irrelevant results on later pages (which is a problem when users sort the results by some other attribute, like [price](https://medium.com/@dtunkelang/why-is-it-so-hard-to-sort-by-price-2a5e63899233)). Irrelevant results can drastically skew facet coverage. Hence, it’s important to compute facet coverage based on a retrieval strategy that emphasizes relevance, independent of ranking.

Utility, like coverage, is also sensitive to the retrieval strategy, particularly when it comes to ensuring that a facet value represents at least a meaningful fraction of relevant results. But at least it’s easy to compute what fraction of the first page a facet value filters out. If selecting a facet value leaves the first page essentially unchanged, it wastes the searcher’s time. It’s impossible to eliminate all sources of [friction](https://medium.com/@dtunkelang/learning-from-friction-to-improve-the-search-experience-8937c71ec97a) from the search journey, but a bare minimum the search engine can do is to ensure that at every choice it suggests to the searcher — especially facet values — meaningfully changes the search results.

**Summary**

Faceted search is a simple idea, but it turns out to be quite nuanced in practice. It’s useful for broad queries, but not for ambiguous queries. It can help searchers find more efficiently, but it can also help them explore and discover. Facets should optimize for popularity, coverage, and utility; and determining these requires a retrieval strategy that emphasizes relevance. In short, faceted search is a fascinating topic with many facets!
