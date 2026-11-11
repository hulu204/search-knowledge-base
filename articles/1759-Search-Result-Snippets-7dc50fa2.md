---
title: 'Search Result Snippets'
company: Tunkelang
tag: 搜索相关性
date: 2023-07-16
url: https://queryunderstanding.com/search-result-snippets-e8c447950219
account: 
origin: harvest3-202607
---
# Search Result Snippets

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--e8c447950219---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--e8c447950219---------------------------------------)

3 min read

·

Mar 12, 2018

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3De8c447950219&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fsearch-result-snippets-e8c447950219&source=---header_actions--e8c447950219---------------------post_audio_button------------------)

Share

Search result snippets, also known as [query-biased summaries](http://marksanderson.org/publications/my_papers/SIGIR98.pdf), are the additional context included with each result on the search results page. They are an essential tool to help searchers find what they’re looking for.

Search result snippets can serve various purposes. Sometimes snippets allow searchers to satisfy their information needs directly from the search results page, such as when a sentence [answering the searcher’s question](/search-result-snippets-e8c447950219) appears in the snippet. In general, snippets allow search engines to establish trust and comfort by showing searchers how each result matches the query.

But the most important function that search result snippets serve is helping searchers quickly determine which results are most likely to satisfy their information needs.

**Snippets as Relevance Signals**

No retrieval strategy can achieve perfect precision — every strategy represents a trade-off between [precision and recall](https://en.wikipedia.org/wiki/Precision_and_recall). As a result, searchers often need to scan the set of search results in order to determine which results are relevant to their needs.

An important measure of the effectiveness of snippets — and of search results presentation generally — is how often searchers bounce back from clicks on search results back to the search results page. Unless the searcher is performing an exploratory search with the goal of collecting multiple relevant results, a high bounce rate tells us that the search results page isn’t providing a strong enough relevance signal for each result.

**Query-Independent Summaries**

In most search applications, the search results page shows a short, query-independent summary for each result entry. A typical summary includes a title, an associated image, and application-appropriate metadata. For example, a document search application might include the document’s type, size, and creation date; while an ecommerce search application might include the brand, price, and average review score. Query-independent summaries, which can be computed as part of the indexing process, should be rich enough to communicate salient information about the results while being concise enough to allow the searcher to scan through them quickly.

It’s a good idea to optimize query-independent summaries through experimentation, using the bounce rate as a success metric. For example, searchers on an ecommerce site might change their minds when they discover how much it will cost in time or money to ship a product. In a document search application, the citation count might be a signal that searchers use to determine whether a document is a credible source. Experimentation is the best way to determine which pieces of information matter most to searchers.

**Query-Dependent Summaries**

Query-independent summaries, while useful, are not always sufficient to communicate how search results relate to the searcher’s intent. In particular, the query may match a portion of a search result that is not included in a query-independent summary.

A query-dependent or query-based summary focuses on the part of the search result that most relates to the query. At the very least, it shows which field of the document matches the search results. Typically, it presents a single line of document text that contains all or most of the matched query terms, with the query terms bolded or otherwise highlighted to make them salient. When the matched keywords are the result of [stemming, lemmatization](/stemming-and-lemmatization-6c086742fe45), or other [query expansion](/query-expansion-2d68d47cf9c8#.gvckhp2rc), this highlighting makes the query expansion more transparent.

There are many algorithms for generating query-dependent summaries, and most search engines include them as a product feature. For example, Lucene includes a [highlight](https://lucene.apache.org/core/7_2_1/highlighter/org/apache/lucene/search/highlight/package-summary.html) package that handles the various aspects of generating and presenting query-dependent summaries. Specifically, it includes methods to find a span of text in each result containing the query keywords.

**Summary**

Much as we try to improve query understanding, result retrieval, and result ranking, a search engine will never achieve perfect precision. By showing searchers how each result matches the query, search result snippets establish trust and help searchers determine which results are most likely to satisfy their information needs —and sometimes the snippets are sufficient to satisfy those needs. It’s a reminder the search isn’t just about retrieving relevant results; it’s about communicating effectively with the searcher and efficiently satisfying the searcher’s information needs.

**Previous:** [**Search Results Presentation**](/search-results-presentation-7d6c6c384ec1)

**Next:** [**Search Results Clustering**](/search-results-clustering-b2fa64c6c809)