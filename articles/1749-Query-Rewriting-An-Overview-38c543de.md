---
title: 'Query Rewriting: An Overview'
company: Tunkelang
tag: 查询理解
date: 2022-01-03
url: https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83
account: 
origin: harvest3-202607
---
# Query Rewriting: An Overview

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--d7916eb94b83---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--d7916eb94b83---------------------------------------)

3 min read

·

Feb 16, 2017

--

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dd7916eb94b83&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-rewriting-an-overview-d7916eb94b83&source=---header_actions--d7916eb94b83---------------------post_audio_button------------------)

Share

Thus far, we’ve focused on query understanding at the character and token level. It’s time move up the stack, on to entities and the query itself.

At this level, the most powerful techniques for query understanding fall into a broad class of strategies that we call query rewriting. Query rewriting automatically transforms search queries in order to better represent the searcher’s intent. Query rewriting strategies generally serve two purposes: increasing [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall) and increasing [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision).

This post provides an overview of query rewriting. We’ll dive into the details of specific techniques in future posts.

**Increasing Recall**

A key motivation for query rewriting search queries is to increase recall — that is, to retrieve a larger set of relevant results. In extreme cases, increasing recall is the difference between returning some (hopefully relevant) results and returning no results.

The two main query rewriting strategies to increase recall are query expansion and query relaxation.

**Query Expansion**

[Query expansion](https://en.wikipedia.org/wiki/Query_expansion) broadens the query by adding additional tokens or phrases. These additional tokens may be related to the original query terms as synonyms or abbreviations (we’ll discuss how to obtain these in future posts); or they may be obtained using the [stemming](/stemming-and-lemmatization-6c086742fe45) and [spelling correction](/spelling-correction-471f71b19880) methods we covered in previous posts.

If the original query is an AND of tokens, query expansion replaces it with an AND of ORs. For example, if the query *ip lawyer* originally retrieves documents containing *ip* AND *lawyer*, an expanded query using synonyms would retrieve documents containing (*ip* OR *“intellectual property*”) AND (*lawyer* OR *attorney*).

Although query expansion is mostly valuable for increasing recall, it can also increase precision. Matches using expanded tokens may be more relevant than matches restricted to the original query tokens. In addition, the presence of expansion terms serves as a relevance signal to improve ranking.

**Query Relaxation**

Query relaxation feels like the opposite of query expansion: instead of adding tokens to the query, it removes them. Specifically, query relaxation increases recall by removing — or optionalizing — tokens that may not be necessary to ensure relevance. For example, a search for *cute fluffy kittens* might return results that only match *fluffy kittens*.

A query relaxation strategy can be naïve, e.g, retrieve documents that match all but one of the query tokens. But a naive strategy risks optionalizing a token that is critical to the query’s meaning, e.g., replacing *cute fluffy kittens* with *cute fluffy*. More sophisticated query relaxation strategies using query parsing or analysis to identify the main concept in a query and then optionalize words that serve as modifiers.

Both query expansion and query relaxation aim to increase recall without sacrificing too much precision. They are most useful for queries that return no results, since there we have the least to lose and the most to gain. In general, we should be increasingly conservative about query expansion — and especially about query relaxation — as the result set for the original query grows.

**Increasing Precision**

Query rewriting can also be used to increase precision — that is, to reduce the number of irrelevant results. While increasing recall is most valuable for avoiding small or empty result sets, increasing precision is most valuable for queries that would otherwise return large, heterogeneous result sets.

**Query Segmentation**

Sometimes multiple tokens represent a single semantic unit, e.g., *dress shirt* in the query *white dress shirt*. Treating this segment as a quoted phrase, i.e., rewriting the query as *white “dress shirt”* can significantly improve precision, avoiding matches for white shirt dresses.

Query segmentation is related to [tokenization](/tokenization-c8cdd6aef7ff#.ysb9a4kxl): we can think of these segments as larger tokens. But we generally think of tokenization at the character level and query segmentation at the token level. We will discuss query segmentation algorithms in a future post.

**Query Scoping**

Documents often have structure. Articles have titles and authors; products have categories and brands; etc. Query rewriting can improve precision by scoping, or restricting, how different parts of the query match different parts of documents.

Query scoping often relies on query segmentation. We determine an entity type for each query segment, and then restrict matches based on an association between entity types and document fields.

Query rewriting can also perform scoping at the query level, e.g., restricting the entire set of results to a single category. This kind of scoping is typically framed as a classification problem.

**The Power of Query Rewriting**

Query rewriting is a powerful tool for taking what we understand about a query and using it to increase both recall and precision. Many of the problems that search engines attempt to solve through ranking can and should be addressed through query rewriting.

We’ll spend the next posts diving into the details of the techniques introduced above.

**Previous:** [**Stemming and Lemmatization**](/stemming-and-lemmatization-6c086742fe45#.2qz7j1set)

**Next:** [**Query Expansion**](/query-expansion-2d68d47cf9c8#.gvckhp2rc)