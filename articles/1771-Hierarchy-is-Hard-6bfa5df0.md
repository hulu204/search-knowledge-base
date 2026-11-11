---
title: 'Hierarchy is Hard!'
company: Tunkelang
tag: 查询理解
date: 2024-03-14
url: https://dtunkelang.medium.com/hierarchy-is-hard-a683793cc9c3
account: Tunkelang
origin: harvest3-202607
---
# Hierarchy is Hard!

A fundamental concept in language understanding is that of semantic hierarchy. In linguistics, a [hyponym](https://en.wikipedia.org/wiki/Hypernymy_and_hyponymy) is a more specific or subordinate word, while a [hypernym](https://en.wikipedia.org/wiki/Hypernymy_and_hyponymy) is a broader or superordinate word. For example, “cat” is a hyponym of “animal”, while “animal” is a hypernym of “cat”. Semantic hierarchy promises substitutability in one direction: all cats are animals, but not all animals are cats.

## Taxonomies

In the context of search applications, a semantic hierarchy can be represented as a [taxonomy](https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2). Ecommerce search applications typically use a taxonomy of product types as their primary scheme for organizing content, while media applications often use a taxonomy of topics to organize their content. A flat list of thousands of product types or topics is difficult to maintain, so the layers of hierarchy help to keep the taxonomy usable.

Developing and maintaining taxonomies is hard work! Historically, that job falls to taxonomists, [information scientists](https://en.wikipedia.org/wiki/Information_science) whom, in earlier times, we would have called [library scientists](https://en.wikipedia.org/wiki/Library_and_information_science). These are people who sweat the details of merging and splitting taxonomy entries, debate the importance of parallel substructure, etc. Taxonomies are inherently opinionated, since every person can have a particular idea of how to organize the world. A good taxonomy is one that reflects the developer’s strong personal vision, while accommodating the varied needs of everyone who will have to use it. Developing and maintaining taxonomies is a critical but thankless job.

## Queries

Organizing product types or topics into a taxonomy is challenging, but at least the limited scale of their enumeration makes these challenges tractable. Queries present a more daunting challenge.

For example, the query “basketball shoes” expresses a more specific [intent](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f) than the query “shoes”. For that matter, the query “nike basketball shoes” expresses a more specific intent than the query “basketball shoes”. In theory, we should be able to organize queries into a taxonomy in the same way that we organize product types or topics. That would be a great help to our [query understanding](https://queryunderstanding.com/query-understanding-8a2b16024c5b) efforts!

In practice, such a task seems impossible — or at least impractical. It is one thing to recognize that queries vary in [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb), but another to organize all queries— not just thousands but millions — into a hierarchy.

## Opportunities

Given the challenges, why would we even want to organize queries into a hierarchy? The answer is that doing so could help us beter manage the core tradeoff of [information retrieval](https://en.wikipedia.org/wiki/Information_retrieval): the tradeoff between [precision and recall](https://en.wikipedia.org/wiki/Precision_and_recall).

Consider a query that returns [null or low results](https://queryunderstanding.com/making-sense-of-null-and-low-results-a077f37bf8fc).

A popular strategy to increase its recall is [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425), which retrieves more results by making one or more of the query tokens optional. Unfortunately, query relaxation can hurt precision by optionalizing query tokens that are critical to representing the searcher’s intent.

A more modern strategy is neural retrieval using [embeddings](https://en.wikipedia.org/wiki/Word_embedding), rather than traditional token-based retrieval using an [inverted index](https://en.wikipedia.org/wiki/Inverted_index). Embedding-based retrieval is a more principled way to manage the precision-recall tradeoff while respecting the [holistic](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) query intent, but it has its own challenges. It is difficult to [align query and result embeddings](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599), as well as to choose an optimal [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) threshold.

Perhaps the best strategy would be to move the tradeoff from result retrieval to negotiating the scope of the query intent. For example, if there are no results for “nike basketball shoes”, then the search application could suggest that there are results for “nike shoes” or for “basketball shoes”. This approach allows the search application to propose explicit generalizations the searcher’s intent, which in turn allows the searcher to choose which generalizations are acceptable or optimal.

## Challenges

The main challenge with this proposed strategy is that there is no reliable way to determine if one query is strictly broader or more specific than another. We can compute and compare the [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) of the two queries, but the harder problem is determining whether the scope of the broader query strictly contains that of the narrower query.

Intuitively, we should be able to draw a [Venn diagram](https://en.wikipedia.org/wiki/Venn_diagram) showing where the two queries intersect. If one query is stricly contained in the other, then the contained query is more specific than the broader containing query.

But how do we turn that intuition into a practical approach? We could map each query to its retrieved results and see if one set of results is a [proper subset](https://en.wikipedia.org/wiki/Subset) of the other, but that only works when retrieval is perfect — that is, when we achieve 100% precision and 100% recall. That seems unlikely.

Can embeddings help? Perhaps, but embeddings are vectors, not geometric regions, so it is not clear how to create Venn diagram from them. We can determine two query vectors have high [similarity](https://queryunderstanding.com/query-similarity-49dde9f78043) and that one of the query vectors has lower [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) than the other, but that is not sufficient to determine whether one query strictly contains the other.

Could we use a different embedding representation? Researchers have proposed [box embeddings](https://arxiv.org/abs/2109.04997); perhaps this or a similar approach would map queries to geometric regions rather than individual vectors. Or perhaps we can use query specificity to convert a query vector into a [hypersphere](https://en.wikipedia.org/wiki/N-sphere), with the query vector as the center and the specificity as the radius. We could then determine whether one query’s hypersphere contains the other. These approaches offer tempting intuitive frameworks, but it remains to be see if and how any of them work in practice.

## Summary

Semantic hierarchy is a foundational concept in language understanding. Hyponyms and hypernyms are at the heart of relationships among words, categories, and query intents. But developing and maintaining hierarchical taxonomies is challenging in general, and especially so for queries. Still, this is a challenge that is worth pursuing, since it offers the potential of a more principled, intuitive way to manage precision-recall tradeoffs.
