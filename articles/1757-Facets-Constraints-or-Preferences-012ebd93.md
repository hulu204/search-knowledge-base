---
title: 'Facets: Constraints or Preferences?'
company: Tunkelang
tag: 搜索相关性
date: 2023-06-30
url: https://dtunkelang.medium.com/facets-constraints-or-preferences-8b8689903652
account: Tunkelang
origin: harvest3-202607
---
# Facets: Constraints or Preferences?

When my colleagues and I at [Endeca](https://en.wikipedia.org/wiki/Endeca) started working on [faceted search](https://en.wikipedia.org/wiki/Faceted_search) in 1999, our model of the [search journey](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02) was that most searchers start with broadly expressed information needs, and then progressively narrow down those needs by specifying facet values as refinements.

For example, a searcher might start with the query “men’s shoes” and then progressively refine it by specifying size = 8.5, color = black, price < $100.

We advocated for this approach, which we branded as “[guided navigation](https://docs.oracle.com/cd/E35319_01/CRS.10-2/ATGCommerceReferenceStoreIUAOverview/html/s0608endecadrivensearchandguidednavig01.html)”, to address the “[million or none](https://www.iro.umontreal.ca/~nie/IFT6255/Books/FacetedSearch.pdf#page=36)” problem: broad queries return too many results, while narrow queries lead to dead ends. Faceted refinement enables searchers to progressively refine their initial queries, encouraging them to express specific intent while avoiding dead ends.

This idealized model of the search journey proved to be particularly useful in domains that are rich in structured data, such as ecommerce and job search. It does, however, present a thorny challenge: determining whether searchers’ refinements represent hard constraints or soft preferences.

### Faceted refinements are not always hard constraints.

Let us go back to our example of a search for men’s shoes. Shoe size is almost certainly a constraint: while there may be a little bit of literal wiggle room (e.g., a size 9 might work for someone whose size is 8.5), a searcher looking for a particular size is not simply expressing a preference. The shoes have to fit, or else they are useless, except possibly for resale.

In contrast, color and price could be either preferences or constraints. It is possible that the searcher needs black shoes for an occasion that requires them, but it is also possible that the searcher simply prefers black over other colors. Similarly, the searcher may have a strict budget of $100, or may simply prefer to spend less than $100 on shoes.

Consider how the search application might handle these two scenarios:

- Shoes that are black and size 8.5, but whose price is $110.

- Shoes are that are black and cost less than $100, but are size 6.

Intuitively, we can see that, if the only violation of the query constraints is a small price difference ($110 vs. $100), then the searcher is likely to have some flexibility. This is even more likely if there are few or no results that satisfy all of searcher’s other criteria, or if this result has more desirable attributes (e.g., higher ratings) than the results that satisfy all constraints.

In contrast, it would be unhelpful to show size 6 shoes to someone looking for size 8.5, since size is generally a hard constraint.

### Unfortunately, reality is not so straightforward.

Even this simple example raises concerns of trust and communication.

On one hand, a searcher who specifies that the price should be less than $100 expects the results to cost less than $100. If a search application returns results that cost more than $100, it looks like a bug — or, worse, an attempt to trick searchers into spending more. This undermines trust.

On the other hand, the searcher has no way to communicate to the search application that the price range is a soft preference rather than a hard constraint. Perhaps the searcher just wants to avoid seeing $200+ shoes.

Even if the price range is only a preference, it is not clear how the search application should weigh that preference against other factors, such as the desirability of the results. How much more desirable do the shoes have to be to justify a price of $110? What about $150 or $200?

Rather than guessing, the search application could jusk the searcher whether each refinement is a hard constraint or a soft preference. But this approach would add complexity to the search experience and potentially confuse searchers. Hard constraints are easy for searchers to understand, but it is less clear to searchers — or to search application developers — how soft preferences affect — or should affect — retrieval and ranking.

### Managing searcher expectations is key.

In order to maintain searcher trust, it is safest to treat every filter that the searcher specifies as a hard constraint. A search application can, however, separate display results that violate the filters with clear messaging to that effect. The messaging can be vague, not specifying which filters are violated, e.g., “Additional results that partially match your requirements.”

But now the search application needs to determine when to show such additional results, as well as how to retrieve and rank those results.

As for when to show them, a good reason is the lack of good results that satisfy all of the specified filters. After all, if there are already a lot of good results that satisfy all the filters, there is no need to fix what is not broken.

### What are “good” results?

If there are no results, then it follows that are are no good results either. If there are very few results (e.g., not enough to fill a page), then the potential upside from showing additional results probably outweighs the downside. If we have query-dependent relevance scores or query-independent desirability scores, we can use them as measures of goodness.

Moreover, if we can afford the computation, then, before deciding to show additional results, we can compare their relevance and desirability to that of the results already retrieved. Additional results should at least be close in relevance, and hopefully better in desirability if they are less relevant.

As for retrieving and ranking the additional results, scoring should reflect a trade-off between relevance and desirability. This is essentially the same as the ranking problem for “regular” results, and we can train a machine learning model from behavior data using the usual [LTR](https://en.wikipedia.org/wiki/Learning_to_rank) techniques.

### Can we automatically recognize hard constraints?

Returning to our example, can we automatically determine that shoe size is probably a hard constraint, while color and price may be soft preferences?

We might be able to learn from searcher behavior — at least if the search application offers searchers opportunities to relax their own constraints.

If the search application shows searchers additional results that only satisfy a subset of constraints, searcher engagement with those results can tell us how often searchers implicitly relax a given constraint. We may also be able to learn from query reformulation within the session, especially if searchers remove constraints that they added as faceted refinements.

A potential challenge with learning from behavior this way is the availability of training data. For a site that only sells shoes, there should be enough historical behavior to learn that size is more of a constraint than color. In contrast, a general-purpose retailer may struggle to learn about shoe facets, especially shoes represent a small portion of their demand.

An alternative to learning from behavior is to incorporate domain expertise. This approach can succeed where data is unavailable or insufficient, but it can be expensive and may introduce subjectivity. Unfortunately, there is no free lunch!

### Summary: communicating information needs is hard!

When I started working on faceted search in 1999, it seemed like a simple way for searchers to communicate with search applications. Experience has taught me that nothing in search is ever simple. Search applications do not always know what searchers want, and even searchers do not always know what they want. Search is fundamentally a communication problem, and communication is hard. That is why we continue to work on it!
