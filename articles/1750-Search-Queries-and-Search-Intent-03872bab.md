---
title: 'Search Queries and Search Intent'
company: Tunkelang
tag: 查询理解
date: 2022-01-04
url: https://dtunkelang.medium.com/search-queries-and-search-intent-1dec79ad155f
account: Tunkelang
origin: harvest3-202607
---
# Mapping Search Queries To Search Intents

Evaluating and improving search experience starts with analyzing the queries searchers are making. But search queries are not the same as search intents.

I’m not talking about [ambiguous](https://medium.com/@dtunkelang/broad-and-ambiguous-search-queries-1bbbe417dcc) queries like “java” or “jaguar” — examples that information retrieval researchers often use to illustrate how a single search query can map to multiple search intents. Ambiguous queries are fascinating in theory, but in practice they tend to be rare edge cases.

I’m talking about the opposite: when multiple queries mapping to the same intent. For example, queries like “mens shoes” and “shoes for men”.

Recognizing when two or more search queries represent the same intent opens up a variety of opportunities to improve the search experience.

**Recognizing Query Equivalence**

How do we recognize that two queries represent the same search intent? We can take two approaches:

- **Surface query similarity.** Queries that only differ in [stemming or lemmatization](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) often express the same intent — especially if they represent the singular and plural form of a noun phrases. So do queries that only differ in word order or the inclusion of stop words. In [synthetic languages](https://en.wikipedia.org/wiki/Synthetic_language) like German, there may also be differences in [compounding](https://en.wikipedia.org/wiki/Compound_(linguistics)).

- **Similar post-search behavior.** Queries that express the same intent will be followed by the same behavior, i.e., engagement with the same kinds of results. Post-search behavior can be represented in a vector space, e.g., by using the [embeddings](https://en.wikipedia.org/wiki/Word_embedding) of result titles. Of course, this behavioral similarity is only possible if both queries allow users to find the same kinds of results.

We can combine these two approaches, e.g., as follows:

- Group queries into equivalence classes based on surface similarity, canonicalizing each query by stemming each token and sorting the tokens alphabetically, and removing stop words, e.g., “mens dress shirts” and “dress shirts for men” both map to the canonical form “dress men shirt”.

- Split these equivalence classes into clusters of similar post-search behavior based on the cosines of vectors associated with queries, thus ensuring that queries like “dress shirt” and “shirt dress” are not considered equivalent despite their surface similarity.

After these two steps, we know that any pair of queries in the same cluster exhibits both surface query similarity and similar post-search behavior.

**Is Surface Query Similarity Necessary?**

Relying on surface query similarity has pros and cons.

On one hand, it minimizes false positives, since two queries with high surface similarity usually express equivalent or near-equivalent intent.

On the other hand, it excludes a large number of query pairs that express equivalent intents through synonyms, redundant words, or complete rephrasings, e.g., “iphone headphones dongle” and “lightning to 3.5 mm”.

It’s possible to generalize surface query similarity to recover some of these pairs (e.g., through [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8)), but many will slip through.

A more aggressive alternative is to rely entirely on post-search behavior. But doing so pleases a heavy burden on precisely comparing post-search behavior so as not to equate queries whose intents are similar but not quite equivalent (e.g., “pants” and “dress pants”). Making these subtle distinctions requires a lot of care in working with the vectors that represent post-search behavior.

**Using Query Equivalence to Improve Search**

Once we are able to recognize equivalent queries, what can we do with this knowledge? As it turns out, a lot!

- **Query rewriting.** Given a pair or set of equivalent queries, we can [rewrite](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83) all of them to a common query representation that ensure the optimum retrieval, ranking, and other search features.

- **Analytics.** Rather than analyzing the performance of each query separately, we can group queries into equivalence classes, thus aggregating behavioral signals that would otherwise be fragmented.

- **Machine Learning.** The same aggregation that improves analytics also allows us to capture more robust signals to train machine-learned models.

In summary, recognizing query equivalence allows us to transform search queries into canonical representations of search intent, which in turn establishes a more robust foundation for optimizing the search experience.
