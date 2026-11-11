---
title: 'Making Sense of Null and Low Results'
company: Tunkelang
tag: 查询理解
date: 2024-03-07
url: https://dtunkelang.medium.com/making-sense-of-null-and-low-results-a077f37bf8fc
account: Tunkelang
origin: harvest3-202607
---
# Making Sense of Null and Low Results

With rare exception, searchers are unhappy when a search query returns zero results. Businesses — especially ecommerce businesses trying to sell products to searchers — do not like zero-result searches either. So it is tempting to treat the zero-result searches — and, by extension, searches that return less than a page of results — as a metric to minimize. Search analytics teams often refer to these metrics as “null and low” results.

Minimizing null and low results sounds sensible, but it confuses causes with symptoms. In fact, trying to minimize null and low results without understanding the underlying causes will probably make things worse.

This post explores the main causes of null and low results, with the aim of identifying the problems before jumping to solutions.

So, what are the causes of null and low results?

## Failure to Understand the Query

[Query understanding](https://queryunderstanding.com/introduction-c98740502103) is what happens before the search application retrieves and ranks results: it is the process by which the search application infers the searcher’s intent from the query. If query understanding fails, the search application is unlikely to recover through retrieval and ranking.

There are many ways query understanding can fail. These include [language identification](https://queryunderstanding.com/language-identification-c1d2a072eda) (e.g, searching for shoes with the query “zapatos”), [spelling correction](https://queryunderstanding.com/spelling-correction-471f71b19880) (e.g., searching for “addidas shoes”), [query ambiguity](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc) (e.g., searching for “mixer” which could mean food mixer or audio mixer, etc), and [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) (e.g., searching for running shoes with the query “trainers”).

Regardless of the specific cause, a search application is unlikely to resolve a query understanding failure in a downstream step like retrieval or ranking. Rather, it is important to detect the failure at the source — online when possible, but otherwise through an offline [query triage process](https://queryunderstanding.com/effective-query-triage-31b4e6b116a4).

There is no perfect way to detect query understanding failures online. If there were, then there probably would not have been a failure in the first place. Still, there are useful indicators, and here are a few to consider:

- **Entropy of query classification.** In many search applications, the simplest and most powerful query understanding method is[ classifying the query](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) by mapping it to a probability distribution among categories or topics. In most cases, successfully understanding a query will map it to a probability distribution with a low [entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) — that is, a distribution concentrated in one or a small number of categories. It helps to use a [similarity-sensitive entropy](https://queryunderstanding.com/similarity-sensitive-diversity-16a35d64f48c) measure. Low entropy is not a guarantee of successful understanding, since the classifier could be confidently wrong. But high entropy usually indicates a failure.

- **Similarity to known successful queries.** For frequent (i.e., head and torso) queries, search analytics should provide clear indicators of success, including successful query understanding. For infrequent (i.e., tail) queries, there is no way to directly apply search analytics. Instead, it is possible to leverage [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043) to find similar queries that are in the logs. A search application is unlikely to understand a query that is not similar to other queries it has previously understood successfully.

- **Coherence of retrieved results.** When possible, it is better to evaluate query understanding before retrieval than afterwards. Nonetheless, it may be possible to infer a query understanding failure by [analyzing the retrieved results](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc). Specifically, if the results are incoherent, then it is likely that the search application failed to understand the query. Unfortunately, coherent results are not a guarantee of successful query understanding, since the application could be confidently wrong.

These online indicators are useful, but they are not a substitute for query triage. Detecting and resolving query understanding failures is a critical part of developing and maintaining a search application.

## Lack of Relevant Inventory

Some of my favorite lyrics come from the song “[Punk Rock Girl](https://en.wikipedia.org/wiki/Punk_Rock_Girl)”:

> We asked for Mojo Nixon
They said, “He don’t work here”
We said, “If you don’t got Mojo Nixon then your store could use some fixin’”

The merits of the song aside, a search application cannot return useful results for a query if the catalog lacks relevant inventory for it. At best, the application can recognize the lack of relevant inventory, apologize to the searcher, and offer something else instead. At worst, it will fails to recognize the lack of relevant inventory and then return irrelevant results.

The difference between a lack of relevant inventory and a failure to understand the query is that the search application does understand the query. In the [Mojo Nixon ](https://en.wikipedia.org/wiki/Mojo_Nixon)example, it would have been reasonable to respond, “Sorry, we don’t have any of his records. But check out our selection of music by [Jello Biafra](https://en.wikipedia.org/wiki/Jello_Biafra).” That response recognizes the lack of relevant inventory, apologizes to the searcher, and offers a reasonable alternative that might satisfy the searcher and even lead to a purchase. Netflix uses a similar strategy to respond to searches for movies or shows outside their catalog, recommending similar titles instead. Of course, this requires Netflix to know about the titles despite not stocking them.

The best way to recognize a lack of relevant inventory is to have confidence that the search application successfully understood the query (as per the previous section) but nonetheless failed to retrieve relevant results. It is possible that there is relevant inventory that the system failed to retrieve, so it is a good idea to analyze the search application’s [retrievability](https://queryunderstanding.com/using-retrievability-to-measure-recall-b991eb241ded). Regardless, it is better to be forthright about not having what the searcher wants than to flood the searcher with irrelevant results. The former may feel like a short-term failure, but it builds trust for the long term.

## Overspecified Queries

Sometimes a searcher is just too picky, and the catalog does not have any inventory that entirely satisfies the search query. This is a variation of lack of relevant inventory: a lack of exactly matching inventory. Overspecified queries, however, invite invitations to compromise by returning results that partially match the query and are thus somewhat relevant.

Distinguishing overspecified queries from a lack of relevant inventory is tricky, in part because the distinction is a subjective one. For example, if someone searches for “navy blue shirts”, then perhaps dark blue shirts that are not navy blue are good enough. But what is someone searches for “[new york yankees](https://en.wikipedia.org/wiki/New_York_Yankees) shirts”? It is unlikely that the searcher would be happy to see [New York Mets](https://en.wikipedia.org/wiki/New_York_Mets) shirts as results unless the searcher liked both teams. In fact, the searcher would probably be more interested in New York Yankees merchandise other than shirts, such as caps or banners.

Establishing whether there are somewhat relevant results is tricky and subjective. Nonetheless, it is often better than returning no results.

But how can the search application recognize an overspecified query? A strong indicator is that the query has high [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb), and that it is [similar](https://queryunderstanding.com/query-similarity-49dde9f78043) to successful queries with lower query specificity.

## Retrieval Failure

The simplest and perhaps most addressable reason for null or low results is retrieval failure. In other words, even though the search application did succeed in understanding the query, and there was relevant inventory, the search application failed to implement an effective retrieval strategy.

There are various ways to address retrieval failure: better indexing through [content understanding](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974), [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8), [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425), whole-query expansion using [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043), and neural retrieval using [embeddings](https://en.wikipedia.org/wiki/Word_embedding).

The toughest challenge is recognizing that retrieval failure is the problem in the first place. An approach that can help address this challenge is to analyze the search application’s [retrievability](https://queryunderstanding.com/using-retrievability-to-measure-recall-b991eb241ded) to discover [recall](https://en.wikipedia.org/wiki/Precision_and_recall) gaps.

## Summary

Hopefully this post helps clarify the challenges associated with search applications returning null or low results. The key is focusing on the cause rather than the symptom. Query understanding failure is very different from lack of relevant inventory and overspecified queries, which are in turn very different from retrieval failure. Rather than minimizing null and low results, it is important to understand and focus on the underlying causes. First identify the problems, then work on solutions.
