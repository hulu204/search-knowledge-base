---
title: 'Search Result Snippets, Revisited'
company: Tunkelang
tag: 搜索相关性
date: 2023-07-17
url: https://dtunkelang.medium.com/search-result-snippets-revisited-6cef687ffa65
account: Tunkelang
origin: harvest3-202607
---
# Search Result Snippets, Revisited

[Search result snippets](https://queryunderstanding.com/search-result-snippets-e8c447950219), also known as query-biased summaries, are the additional context included with each result on the search results page. They are an essential tool to help searchers find what they’re looking for.

### Snippets serve more than one purpose.

The primary purpose of snippets is to [communicate](https://www.linkedin.com/pulse/20140320125500-50510-search-as-communication/) to the searcher how a result is relevant to the query — that is, to communicate the relevance of each result. In my experience, this is the primary — if not exclusive — priority for most search application developers who implement snippets. As a result, snippets generally highlight the query tokens in the results that match the query, possibly by way of [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8).

If the searcher will be satisfied with any relevant result — or perhaps with a piece of information that is likely to be contained in every relevant result, then this primary purpose suffices. Indeed, this application of snippets is just a step away from [question answering](https://queryunderstanding.com/question-answering-94984185c203).

But searchers often have preferences among relevant results — indeed, that is a big part of why [ranking is not the same as relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e). As a result, snippets can and should serve a second purpose — namely, communicating how each result differs from other results. Unfortunately, this second purpose is one that has not received the attention it deserves.

Consider, for example, a search for a book title like “brave new world”. If there are multiple relevant results, it is likely that they all relate to the same book. But they may vary in edition, format, language, condition, or other attributes that matter to searchers— and for which different searchers may have different preferences. There may even be results that match the title but are not books, such as a movie based on the book. In such cases, a wall of search results that only highlight the how each title matches the query is not an effective way to communicate the variety of relevant results.

### Snippets should communicate result distinctiveness.

How can snippets better serve this second purpose of communicating how each relevant result differs from other relevant results?

One way is to make query-independent information about the results more salient. Going back to the book example, if each result clearly highlights the book’s edition, format, language, and condition — along with a clear image of the the book cover — then these highlights can help searchers visually differentiate the results from one another.

But this approach has a drawback — namely, that the most salient query-independent information about a result often overlaps with the query-dependent information used to establish relevance. In our book example, the most important query-independent information for each result is the result’s title, which will tend to be the same for most of the relevant results.

A better and more targeted approach is to focus explicitly on what makes a given result different from other results. For example, if all of the results are relevant to the query for the same reason, such as exactly matching the query in the title field, then part of the snippet should focus on what makes each result distinct from the others.

This process could use a statistical model of distinctiveness, e.g., uncommon attribute values, or anomalous values for continuous numerical attributes like price. What is important is that this distinctiveness is contextual — that is, the baseline for comparison is the distribution of other results, not the index as a whole.

The problem is similar to that of [implicit query reformulation](https://queryunderstanding.com/implicit-query-reformulation-426a246e7a62): the ideal snippet should correspond to a refinement of the query intent for which that result would be the top-ranked result. Thinking about this problem in terms of implicit query reformulation has the advantage that it may lead to a way of presenting the information that aligns with searcher intent.

### Summary

The primary purpose of snippets is to communicate to the searcher how each result is relevant to the query, but the secondary purpose of communicating each result’s distinctiveness matters too. A robust implementation of snippets should strive to address both of these concerns — at least for queries that return more than one relevant result, and for which not all relevant results are equally useful to every searcher.
