---
title: 'Search Results Clustering'
company: Tunkelang
tag: 搜索相关性
date: 2018-09-18
url: https://queryunderstanding.com/search-results-clustering-b2fa64c6c809
account: 
origin: harvest3-202607
---
# Search Results Clustering

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--b2fa64c6c809---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--b2fa64c6c809---------------------------------------)

3 min read

·

Apr 16, 2018

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Db2fa64c6c809&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fsearch-results-clustering-b2fa64c6c809&source=---header_actions--b2fa64c6c809---------------------post_audio_button------------------)

Share

Search queries that express broad intent often return intractably large result sets. We’ve already discussed [faceted search](/faceted-search-7d053cc4fada) as a way to help users narrow their intent by refining the initial query. Another way to address queries with broad intent is to cluster the search results.

Search results clustering is an idea that goes back at least to the [Scatter/Gather](http://people.ischool.berkeley.edu/~hearst/research/scattergather.html) research in the early 1990s. “[Scatter/Gather as a Tool for the Navigation of Retrieval Results](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.473.1989&rep=rep1&type=pdf)” describes a technique that clusters search results into semantically coherent groups on-the-fly and presents descriptive summaries of the groups to the searcher. The clustering allows searcher to identify useful subset of the results, when can in turn be clustered to identify narrower subsets.

Since then, there have been thousands of [papers on search results clustering](https://www.semanticscholar.org/search?q=search+results+clustering&sort=relevance), as well as a variety of commercial and open-source efforts to apply clustering to web and enterprise search engines.

**Competing Objectives**

A clustering of search results should satisfy three objectives:

* **Coherence.** Search results assigned to the same cluster should be substantially similar to one another, so that the cluster represents a coherent subset of possible search intents.
* **Distinctiveness.** Search results assigned to different clusters should be substantially different from one another, so that each cluster represents a distinct subset of possible search intents.
* **Clarity.** The meaning of each cluster should be clear to the searcher, whether from labels, descriptive summarizations (e.g., a [tag clouds](https://en.wikipedia.org/wiki/Tag_cloud)), or representative results.

The first two objectives of coherence and distinctiveness compete with one another. Reducing cluster size (e.g., by splitting clusters) generally improves coherence, but at the expense of distinctiveness. Conversely, increasing cluster size (e.g., by merging clusters) improves distinctiveness at the expense of coherence. [Clustering algorithms](https://en.wikipedia.org/wiki/Cluster_analysis) manage a trade-off between these two competing objectives.

**Challenges**

Search results clustering is an idea that sounds great in theory, but it’s surprisingly difficult to implement clustering well in practice. The main challenges are defining the document similarity function, tuning the clustering algorithm, and descriptively summarizing the clusters.

It’s relatively easy to determine when two search results are extremely similar. Indeed, many search engines include a post-ranking step to remove duplicate and near-duplicate results. However, determining that two results are similar is a much thornier problem than determining that they are near-duplicates. It’s difficult to choose an appropriate similarity threshold, or even to define a similarity function, that consistently yields coherent, distinct clusters.

Typical clustering approaches involve [embedding](https://en.wikipedia.org/wiki/Word_embedding) documents into a vectors and then computing a geometric function on them, such as cosine, to measuring their similarity. While such approaches rely on elegant theoretical models, the results are hit and miss, highly subject to the particulars of the documents. For example, [boilerplate text](https://en.wikipedia.org/wiki/Boilerplate_text) and [markup language](https://en.wikipedia.org/wiki/Markup_language) can affect the similarity function, even though they have no bearing on the substance of the documents. In practice, tuning a similarity function requires a significant amount of data cleaning and can easily become a rathole.

In addition, the results often distribute non-uniformly into distinct search intents. Ideally, the clustering algorithm should adapt to the distribution, producing clusters of suitably varying size. In practice, the most represented intents tend to be split into overlapping clusters, lowering distinctiveness, while the least represented intents tend merged, lowering coherence.

Finally, it’s difficult to produce clear descriptive summaries. Algorithmically produced labels often fail to capture and convey meaning, especially if they’re produced at query time from salient words and phrases in the results. And even if the clustering algorithm does a good job of selecting representative results, they’re only effective as summaries if the searcher can both understand them (cf. [search result snippets](/search-result-snippets-e8c447950219)) and extrapolate from them. In general, producing and communicating intelligible groupings is a triumph of human intelligence that AI still struggles with.

**Summary**

Search results clustering is an old idea for presenting and organizing result sets, and researchers have continued to work on refining it. It sounds great in theory but has proven to be difficult in practice. Nonetheless, clustering can be a valuable tool to address broad-intent queries.

**Previous:** [**Search Result Snippets**](/search-result-snippets-e8c447950219)

**Next:** [**Question Answering**](/question-answering-94984185c203)