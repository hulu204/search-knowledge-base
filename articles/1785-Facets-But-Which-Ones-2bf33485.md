---
title: 'Facets, But Which Ones?'
company: Tunkelang
tag: 搜索相关性
date: 2024-08-22
url: https://dtunkelang.medium.com/facets-but-which-ones-6589416ed4db
account: Tunkelang
origin: harvest3-202607
---
# Facets, But Which Ones?

This post dives into a particular challenge of faceted search, exploring the challenge of selecting which facets a search application should present to searchers as query refinements.

### Faceted Search

[Faceted search](https://queryunderstanding.com/faceted-search-7d053cc4fada) is a standard part of e-commerce search applications and is common in other domains. My relationship with faceted search is quite [personal](https://www.linkedin.com/in/dtunkelang/). Long before I focused on query understanding, it is how I cut my teeth on search at [Endeca](https://en.wikipedia.org/wiki/Endeca). I also wrote a [book](https://www.amazon.com/Synthesis-Lectures-Information-Concepts-Retrieval/dp/1598299999) on the subject.

Faceted search starts with [faceted classification](https://en.wikipedia.org/wiki/Faceted_classification). Faceted classification uses a collection of independent attributes, called facets, to classify each entry in the searchable collection. In contrast with a [taxonomy](https://en.wikipedia.org/wiki/Taxonomy_(general)) that uses a single [hierarchical](https://queryunderstanding.com/hierarchy-is-hard-a683793cc9c3) classification scheme, faceted classification does not impose a rigid ordering of attributes on the searcher. Faceted search takes advantage of faceted classification to support flexible [query refinement](https://queryunderstanding.com/session-context-4af0a355c94a). For example, someone who searches for shoes can narrow the search results by selecting size 8, the color black, and the brand Nike. Combining an initial query with faceted refinement allows the searcher to progressively elaborate a more [specific](https://queryunderstanding.com/query-specificity-a6156f4043eb) intent than that of the original query.

### Which Facets?

However, a downside of facets compared to a single classification scheme is that there are too many. Many search applications face the challenge of deciding [which facets to present as options](https://www.mdpi.com/2078-2489/14/7/387) to refine the initial query. Unless it is possible and practical to always show all of them — which is unlikely on a desktop and practically impossible on a mobile device — search applications need to select them. There is also the challenge of a facet having too many values, which will be the topic of a [future post](https://queryunderstanding.com/handling-facets-with-many-values-94247841a7b5).

Broadly speaking, there are three selection strategies for establishing facet importance: supply, demand, and curation.

### Supply

The most common strategy for selecting facets is to focus on supply — that is, the statistics of the search results. A baseline strategy is to compute the coverage of each facet in the query’s result set — what fraction of the results are assigned a value from that facet — and present the facets with the highest coverage in decreasing order of coverage.

This approach is simple and interpretable but has challenges.

It relies heavily on [relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) — specifically, the [precision and recall](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b) of the retrieved results. If these are low, then facets will be determined — or significantly influenced — by irrelevant results. One way to mitigate this risk is to weigh results by probability or degree of relevance. It is also possible to weigh results by popularity, but that is more of a demand strategy.

Weighing results non-uniformly can introduce some awkwardness. Search applications typically show a count for each facet value, and counts inherently treat results uniformly: a result either is or is not included. However, this is more of a concern for selecting values within a facet.

The main problem with coverage as a metric for facet importance is that is too naive. For example, a search for blue shirts might have 100% coverage for the color facet, but this facet is not interesting or useful if all of the results have blue as a value from this facet. Indeed, it is likely that many facets have 100% coverage but are not equally important to searchers.

An improvement is to use the [entropy](https://queryunderstanding.com/similarity-sensitive-diversity-16a35d64f48c) of the distribution of values from the facet in the results, treating the lack of a facet value as a special value (which effectively makes every facet have 100% coverage). Entropy measures the variation of values from that facet, which is maximal when the values are distributed uniformly across the results.

However, even entropy has the problem of favoring facets with large numbers of distinct values, since the search application can only show searchers a small number of choices. For example, a facet that is uniformly distributed across 100 distinct values has double the entropy of a facet that is uniformly distributed across 10 distinct values. Hence, another improvement is to truncate the distribution to the most frequently occurring values, truncating based on how many values can be shown.

Even with these improvements, there is a risk of misinterpreting supply statistics as helpfulness to the searcher. For example, a facet like country of origin on an e-commerce site may offer a promising statistical distribution but not be interesting to most searchers. In general, supply establishes criteria that are necessary for facet importance, but not sufficient.

### Demand

Rather than relying on supply to select facets and establish their importance, the search application can instead use [demand](https://queryunderstanding.com/search-intent-not-inventory-289386f28a21) — that is, searcher intent. A baseline strategy is to compute the demand for each facet based on its historical frequency of use.

Demand has the advantage of learning from searcher behavior, and it is less susceptible than supply to misinterpreting supply statistics like coverage or entropy as helpfulness. Nonetheless, demand has challenges.

A key challenge with using demand is presentation bias. Searchers can only engage with options that are available to them, and they are more likely to engage with options that are more salient or have less [friction](https://queryunderstanding.com/learning-from-friction-to-improve-the-search-experience-8937c71ec97a). Thus, learning demand from the facets with which searchers engage is likely to reinforce the search application design: the order and salience of a facet will significantly influence its frequency of use.

Thus, it is important for a demand strategy to [account for presentation bias](https://eugeneyan.com/writing/position-bias/), whether by giving more weight to engagement with less salient facets or by using methods like explore-exploit (aka [multi-armed bandits](https://en.wikipedia.org/wiki/Multi-armed_bandit)).

The other significant challenge is sparsity. Only a small fraction of queries use facets, and facet use tends to be concentrated in a small number of facets. Moreover, these numbers are much smaller at the level of individual queries. Hence, learning demand from historical engagement runs into the problem that differences in small numbers are highly subject to noise.

There are two ways to address the sparsity of facet use, particularly for individual queries. The first is to aggregate queries into groups of [similar queries](https://queryunderstanding.com/query-similarity-49dde9f78043) — falling back to global facet use statistics if needed. The second is to use [machine learning](https://en.wikipedia.org/wiki/Machine_learning). using the historical behavior as training data to train a model that generalizes from the patterns in that data.

It can also be helpful to combine the supply and demand strategies. For example, a facet with low entropy in the results is unlikely to be helpful or useful to the searcher, regardless of the apparent demand. Indeed, while demand has the advantage over supply of learning from searcher behavior, it faces the challenges of presentation bias and sparsity. Combining the two strategies can hedge against the drawbacks of each approach.

### Curation

Supply and demand are both data-driven strategies. A different strategy is to turn to human expertise and use curation.

Curation is simple: a person — or a team or a crowd — selects and orders the facets. However, curation is difficult to scale: assigning sets of facets to queries one query at a time is a painstakingly impractical task.

This lack of scalability is similar to the sparsity challenge of the demand strategy and thus amenable to similar solutions: aggregation and machine learning. Curation can work with aggregations of similar queries rather than individual queries, or it can be used to establish training data that is then used to train a machine learning model.

Indeed, curation is similar to demand as a strategy — only that it learns from [human judgments](https://queryunderstanding.com/evaluating-search-using-human-judgement-fbb2eeba37d9) rather than [searcher behavior](https://queryunderstanding.com/evaluating-search-measuring-searcher-behavior-5f8347619eb0). Human judgments have the advantage of not depending on searcher behavior — and thus not being subject to the search application’s presentation bias. The downside is that it costs money and time to collect human judgments, and there is also the risk of an empathy gap: curators may not know what searchers want. That said, curation can address the [cold start](https://en.wikipedia.org/wiki/Cold_start_(recommender_systems)) problem when a search application has not yet collected enough data to learn from demand.

### Summary

The benefit of faceted search over a single hierarchical classification scheme is that faceted search does not impose a rigid ordering of attributes on the searcher. However, the downside of facets is that there are too many. Supply, demand, and curation offer three general strategies for selecting facets. Each strategy has benefits and drawbacks, as well as tactics to mitigate those drawbacks. In practice, it is often best to mix and match.

Regardless of the strategy, the benefits of faceted search depend on selecting the right facets. Choose wisely.
