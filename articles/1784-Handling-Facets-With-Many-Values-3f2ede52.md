---
title: 'Handling Facets With Many Values'
company: Tunkelang
tag: 搜索相关性
date: 2024-08-21
url: https://dtunkelang.medium.com/handling-facets-with-many-values-94247841a7b5
account: Tunkelang
origin: harvest3-202607
---
# Handling Facets With Many Values

The [previous post](https://queryunderstanding.com/facets-but-which-ones-6589416ed4db) addresses the challenge of selecting which facets a search application should present to searchers as query refinements. However, there is another challenge — namely, determining which values to show from a particular facet. This post explores the challenges of handling facets with many values.

Just as there is a limit to the number of facets a search application can present to searchers, there is a limit to the number of values it can show from any given facet. Unless the number of values is small, search applications must select a manageable subset of them.

There are analogs to the data-driven supply and demand strategies from the previous post. Beyond these broad strategies, there are also tactics to organize and present a large set of facet values.

### Supply

The most common strategy for selecting facet values is supply. A baseline strategy is to compute the result count for each facet value and present the values with the highest counts.

While simple and interpretable, this data-driven approach has challenges similar to those of using coverage to measure facet importance.

It relies heavily on the relevance of the results to the query— specifically, the precision and recall of the retrieved results. If these are low, then the selected facet values will be determined — or significantly influenced — by irrelevant results. One way to mitigate this risk is to weigh results by probability or degree of relevance. However, weighing results can produce an awkward experience when it favors values that do not have the highest counts, so it may be best not to show counts in that case.

Then there is the accuracy of the facet values themselves. If facet values are often assigned incorrectly (low precision) or not assigned when they should be (low recall), then facet value counts are an unreliable measure. More broadly, inaccurately assigned facets lead to a poor search experience. The search application should probably remove them.

Coverage and accuracy aside, the facet values with the highest counts may not be the most useful. As discussed in the previous post, the distribution of values within a facet matters, since facets support query refinement to narrow the initial query. Selecting a facet value associated with all the results will not narrow them. Even a value associated with most but not all results (e.g., 99%) has low utility for refinement. Indeed, such facet values [summarize the results rather than refine them](https://queryunderstanding.com/summarization-and-refinement-tags-in-folksonomies-277ea5f45978).

Based on [information theory](https://en.wikipedia.org/wiki/Information_theory), an optimal refinement halves the results. If the count is less than half, a higher count corresponds to a higher expected [information gain](https://en.wikipedia.org/wiki/Information_content) of p * log₂(p) — where p is the fraction of the result set. If each result is associated with at most one value from the facet, then only one facet value can account for more than half of the results. Hence, sorting facet values by result count is practically sorting them by expected information gain. However, if a result can be associated with multiple values from the facet (e.g., a “features” facet for consumer electronics), then the top values may all have unhelpfully high counts. Again, however, any approach that favors values without the highest counts may clash with searcher expectations. It may be better to remove the facet or refactor it so each result is assigned only one value.

### Demand

The other data-driven strategy for selecting values from a facet is demand. A baseline strategy is to compute the demand for each facet value based on its historical frequency of use.

Demand learns from searcher behavior and it is less likely to misinterpret supply statistics like coverage as helpfulness. However, demand is susceptible to presentation bias. Searchers can only engage with the facet values available to them, and they are more likely to engage with more salient options. Avoiding this self-reinforcing loop requires [accounting for presentation bias](https://eugeneyan.com/writing/position-bias/) or explore-exploit (aka [multi-armed bandits](https://en.wikipedia.org/wiki/Multi-armed_bandit)).

The other challenge is sparsity. Only a small fraction of queries use facets, and facet use tends to be concentrated in a small number of facet values. When engagement volume is low, differences are highly subject to noise.

If nothing else, supply and demand are useful guardrails for each other. If they strongly disagree — despite presentation bias — then there is probably something wrong with either retrieval or the selected facet values.

### Hierarchy

Often, a facet with a large number of values is hierarchical. For example, a location facet can organize values in a hierarchy of countries, states, and cities. When a facet is hierarchical, the search can disclose refinement options progressively, only showing the children of the root or a currently selected facet value. As long as no value in the hierarchy has a large number of immediate children, this approach avoids the problem of presenting a large number of values simultaneously.

However, hierarchy introduces some nuances. Some hierarchies are more meaningful than others, e.g., organizing cities by country is more meaningful than doing so using alphabetic ranges like cities whose names start with a given letter. Hierarchy also compounds the challenge of implicit facet value selection: if all or most of the results are associated with a non-leaf value from a facet (e.g., a country rather than a city), then the search application should present children of that value as options rather than the value itself. Hierarchical facets also complicate the selection of multiple values from the same facets.

So, while hierarchical facets can help organize large numbers of values, they also add complexity to search applications.

### Clear Separation

Another consideration is that the selected values from a facet should be significantly more important than the remaining values.

For example, if the top three facet values from a facet each account for over 10% of the results (assuming that counts are used to measure importance) but each of the remaining values accounts for less than 1% of the results, then it makes sense to select the top three values. In contrast, showing only the top three values comes across as an arbitrary cutoff if the third value accounts for 6% of the results and the fourth value accounts for 5%.

Regardless of how the search application establishes facet value importance, there should be a clear separation between the selected values and the rest. Otherwise, it may be better to not select any values — which leads to the final tactic of autocomplete.

### Facet Autocomplete

Even when a facet has too many values to show them all, it is still important for searchers with a specific value in mind to be able to select that value. Some search applications present all values through a “more” or “see all” link. However, the more elegant solution is [autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245).

A searcher who wants to refine the results using a specific facet value should be able to start typing that value into a dedicated search box associated with the facet that performs a prefix search against its values, ideally allowing for name variations and misspellings. Unlike a regular search box, this one does not enable free-text search; it can only lead to a selection from the set of facet values.

While facet autocomplete may feel like a violation of the principle that there should only be one search box, it should not create confusion. A well-designed search application should make it clear to searchers that a facet autocomplete box is only for selecting a value from that facet.

### Summary

Selecting facet values from a facet with many values creates challenges similar to those of selecting from many facets. In addition to the data-driven supply and demand strategies, there are useful tactics like organizing facet values hierarchically and making them searchable through autocomplete. Getting the details right is tricky and often requires experimentation. However, those details are what lead to faceted search delivering on its potential.
