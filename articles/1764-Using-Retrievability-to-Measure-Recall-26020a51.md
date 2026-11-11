---
title: 'Using Retrievability to Measure Recall'
company: Tunkelang
tag: 评测
date: 2023-12-09
url: https://dtunkelang.medium.com/using-retrievability-to-measure-recall-b991eb241ded
account: Tunkelang
origin: harvest3-202607
---
# Using Retrievability to Measure Recall

In court, witnesses swear to tell “the whole truth and nothing but the truth.” Search engines are not under oath, but they should be truthful.

Two metrics for search relevance are [precision and recall](https://en.wikipedia.org/wiki/Precision_and_recall). Precision means telling nothing but the truth, while recall means telling the whole truth.

Precision is the fraction of retrieved results that are relevant. Recall is the fraction of relevant documents that were retrieved. There is a tradeoff: efforts to improve one metric often come at the expense of the other.

### Measuring recall is harder than measuring precision.

Unfortunately, while precision is relatively straightforward to measure, recall is another story — since we rarely know how many relevant results are in the index. As a result, people often estimate recall using crude proxies, such as the fraction of queries that return no or few results.

We can and should do better. Recall might not seem as important as precision for many search applications, but it is still a key metric. After all, if a result is not retrievable, it might as not well even be in the search index.

### To measure recall, we can measure retrievability.

The reason we care about recall is to ensure the retrievability of results, so perhaps we can measure the retrievability of results more directly.

Consider an entry in the search index. We can measure its retrievability by executing a set of search queries that should retrieve the entry and then counting how many of those queries actually retrieve it. For example, a black t-shirt should be retrievable by queries like “black tshirt”, “black tshirts”, “black t shirt”, “tshirts black”, etc.

This strategy isn’t as simple as sounds. For a large search index, measuring the retrievability of every entry is prohibitively expensive. We can address this concern by taking a representative sample. The bigger challenge is obtaining a set of search queries that we expect to retrieve a given entry.

### Reverse search: going from a potential result to candidate queries.

We could ask people to manually come up with a set of search queries for a given entry in the index. But this process would be expensive and difficult. Coming up with such queries is not something humans are good at, though the idea has been explored as an application of [human computation](https://people.eecs.berkeley.edu/~shiry/publications/hcir07-1.pdf).

A more practical approach is to automate query generation. There are a variety of ways to generate queries from index entries, such as [doc2query](https://arxiv.org/abs/1904.08375). But it’s a good idea to generate queries that searchers are likely to make. To do so, we treat query generation as search problem, indexing our query log and then retrieving the most relevant queries for a result from that log.

### Not all candidate queries are equal.

When we measure retrievability this way, we should also take into account the frequency of the queries we generate. Weighing queries by frequency allows us to measure retrievability in a searcher-centric way. For example, there are probably more people who search for “black tshirts” than “tshirts that are black in color”.

But we have to be careful. If our queries drift too far from the source entry, then we would not even want those queries to include the entry in their results. Also, if the queries are not sufficiently specific, their inclusion of the entry in a large result set is not all that useful, regardless of query frequency. Continuing our example, it is more useful for our black t-shirt to appear in results for “black tshirts” than in results for “shirts” or “clothing”.

Hence, we want to focus on specific queries for which the result is relevant, and then weigh those queries according to their frequency. This is still a difficult and underspecified solution, but hopefully a useful framework.

### We can’t give up on measuring recall just because it’s hard.

Measuring recall has always been difficult, so it is understandable that search application developers — especially folks in industry who have to ruthlessly prioritize resources — have tended to focus on precision.

But recall matters. Ranking cannot make up for lost recall. If retrieval fails to include a relevant result, ranking cannot make it magically appear. So we need to invest in recall, and that means we have to have a way to measure it. Hopefully this proposed approach of measuring retrievability helps give recall the respect it deserves.
