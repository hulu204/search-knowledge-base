---
title: 'A Statistical Sense of Direction'
company: Tunkelang
tag: 搜索
date: 2025-12-03
url: https://dtunkelang.medium.com/a-statistical-sense-of-direction-ca335900ef91?source=rss-5f6b5aba680------2
account: Tunkelang
origin: en-rss-feedbody
---
[AI-powered search](https://dtunkelang.medium.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b) lives in a world of high-dimensional vectors. But when we care about similarity, we almost always throw away magnitude. We normalize everything and end up working on the surface of a giant unit [hypersphere](https://en.wikipedia.org/wiki/N-sphere). All that remains is direction.

Modern [information retrieval](https://en.wikipedia.org/wiki/Information_retrieval) has leaned heavily on statistics for decades, but the moment we start working with [unit vectors](https://en.wikipedia.org/wiki/Unit_vector), the usual toolbox stops fitting. If we want to treat these representations as real statistical objects, we need a branch of statistics that understands directions, angles, and orientation. That branch exists. It is called [directional statistics](https://en.wikipedia.org/wiki/Directional_statistics).

### Why We Normalize Everything

Most embedding models represent meaning through orientation. [Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) ignores magnitude completely, so the only thing that matters is where a vector points. The hypersphere is not just a geometric metaphor. It is literally the space where our information systems operate.

This is why directional statistics lines up so naturally with modern retrieval. It gives us ways to describe, average, compare, and model data that live on the surface of a hypersphere.

### Thinking in Angles, Not Distances

A simple example is the [bag-of-documents model](https://dtunkelang.medium.com/modeling-queries-as-bags-of-documents-b7d79d0916ab). It represents a query as the [spherical mean](https://en.wikipedia.org/wiki/Circular_mean#Spherical_mean) of the relevant document vectors. That mean direction captures what the query is about, [translating](https://dtunkelang.medium.com/search-as-translation-f7adec0360f5) the query into the document space. The [length of the resultant vector](https://en.wikipedia.org/wiki/Directional_statistics#Moments), which is related to [spherical variance](https://en.wikipedia.org/wiki/Directional_statistics#Dispersion), captures how tightly those documents cluster together, which we interpret as [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb). A tight cluster indicates a specific query. A loose cluster indicates a [broad or ambiguous](https://dtunkelang.medium.com/broad-and-ambiguous-search-queries-1bbbe417dcc) one.

This is already a substantial upgrade from ad hoc heuristics, and it comes directly from applying directional statistics to a retrieval problem. But this approach barely scratches the surface.

### A Mathematical Toolkit

Directional statistics provides a rich set of tools that are directly applicable to embeddings. Here are some examples.

#### The von Mises–Fisher distribution

The [von Mises–Fisher (vMF) distribution](https://en.wikipedia.org/wiki/Von_Mises%E2%80%93Fisher_distribution) is the spherical version of the [Gaussian (aka normal) distribution](https://en.wikipedia.org/wiki/Normal_distribution). It has a mean direction and a concentration parameter that controls how tightly points cluster around that direction. A large concentration means the distribution hugs that direction. A concentration of zero means everything is uniformly spread around the unit hypersphere.

It is natural to ask whether a query itself should be modeled as a von Mises–Fisher distribution. Perhaps the concentration parameter captures specificity more naturally than the mean resultant length. A mixture of these distributions might offer a principled way to represent [broad and ambiguous queries](https://dtunkelang.medium.com/broad-and-ambiguous-search-queries-1bbbe417dcc). It is an appealing direction to explore.

#### Spherical Medians

If the spherical mean is useful, what about the spherical median? It minimizes the sum of angular distances to it, as opposed to the sum of squared angular distances minimized by the mean. It is more robust to outliers, just as the median is in ordinary statistics. Like a conventional [median](https://en.wikipedia.org/wiki/Median), it is a bit harder to compute and sometimes not unique, but robustness often matters more than convenience. It may give us a better query representation when relevance sets are noisy or skewed.

#### Higher-Order Moments

We already use the spherical equivalents of mean and variance, which are the first two [moments](https://en.wikipedia.org/wiki/Moment_(mathematics)). What about the spherical analogs of the third and fourth moments: [skewness](https://en.wikipedia.org/wiki/Skewness) and [kurtosis](https://en.wikipedia.org/wiki/Kurtosis)? Skewness tells us whether and how much a distribution leans asymmetrically in one direction. Kurtosis tells us whether the distribution has heavy or light tails. When our vectors represent meaning, asymmetry or tail behavior may capture semantic structure that mean and variance miss.

None of this is exotic. They are basic statistical concepts adapted to the spherical geometry we already work in.

### Where This Perspective Can Take Us Next

Embedding-based systems encode meaning as direction, but many of our intuitions are tuned for [Euclidean](https://en.wikipedia.org/wiki/Euclidean_space) rather than spherical spaces.

Evaluation metrics also suffer. Traditional precision and recall treat relevance as a binary event and ignore similarity structure. When systems operate in a directional space, that simplification hides important distinctions. A directional understanding makes it easier to reason about [similarity in terms of substitutability](https://dtunkelang.medium.com/is-similarity-objective-92e1f3a4c236) and to measure [similarity-sensitive diversity](https://dtunkelang.medium.com/similarity-sensitive-diversity-16a35d64f48c) when evaluating [search results](https://dtunkelang.medium.com/thoughts-on-search-result-diversity-1df54cb5bf4a). These are all areas that benefit from a directional statistics framework.

Search is no longer about counting. It is about aligning. Cosine similarity is the fundamental operation. Directional statistics is the framework that explains it and extends it.

We have already moved our data onto the hypersphere. It is time to move our thinking there too and take search in the right statistical direction.

![](https://medium.com/_/stat?event=post.clientViewed&referrerSource=full_rss&postId=ca335900ef91)