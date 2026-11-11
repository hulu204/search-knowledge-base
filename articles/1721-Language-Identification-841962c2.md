---
title: 'Language Identification'
company: Tunkelang
tag: 查询理解
date: 2016-11-20
url: https://queryunderstanding.com/language-identification-c1d2a072eda
account: 
origin: harvest3-202607
---
# Language Identification

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--c1d2a072eda---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--c1d2a072eda---------------------------------------)

3 min read

·

Nov 5, 2016

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc1d2a072eda&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Flanguage-identification-c1d2a072eda&source=---header_actions--c1d2a072eda---------------------post_audio_button------------------)

Share

Queries are the primary way that searchers communicate with search engines. But it’s difficult to get started with query understanding until the search engine identifies the language in which the query is written.

**History**

Automatic language identification has seen [several decades of work](http://www.dfki.de/~hansu/HLT-Survey.pdf#page=290), going back to research in the 1970s to automatically identify the language of written or spoken text based on the frequencies of letter combinations or sound segments. Work on statistical analysis to determine language and authorship goes back even further to [Udny Yule](https://en.wikipedia.org/wiki/Udny_Yule), [George Zipf](https://en.wikipedia.org/wiki/George_Kingsley_Zipf), and [Jean-Baptiste Estoup](https://en.wikipedia.org/wiki/Jean-Baptiste_Estoup).

Given the importance that language plays in society, it’s not surprising that this topic has been the object of sustained study, particularly among linguists and statisticians. Most of that study predates modern search engines.

**Search Queries are Short**

In general, statistical approaches to language identification take advantage of distributional characteristics of the text they analyze. As a result, the accuracy of these approaches is a function of the amount of text they analyze. As [Arjen Poutsma](https://www.linkedin.com/in/arjen-poutsma-288ba6) showed in his 2001 paper on “[Applying Monte Carlo Techniques to Language Identification](https://pdfs.semanticscholar.org/9078/328e6b48c4eda12d26bdc950744a874f2c8e.pdf)”, a wide variety of language identification algorithms perform poorly for inputs of fewer than 50 characters.

Press enter or click to view image in full size

![]()

This result is unsurprising: it’s difficult to obtain a meaningful distribution from a short text sample. Unfortunately, search queries tend to be short.

**Using Signals Beyond the Query**

In 2009, [Hakan Ceylan](https://www.linkedin.com/in/hceylan) and [Yookyung Kim](https://www.linkedin.com/in/kimyookyung) wrote a paper on “[Language Identification of Search Engine Queries](http://anthology.aclweb.org/P/P09/P09-1120.pdf)”. In it, they described how they used clickthrough logs from Yahoo’s search engine to identify the language of queries based on the language of results searchers clicked for those queries.

## Get Daniel Tunkelang’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Their approach took advantage of the relative ease of identifying the language of longer documents: in their data, the average search result contained almost 500 words, far more than the average search query. Even a single result could provide a robust signal, and most search queries were associated with clicks on multiple results.

They also noted that the language of the query terms might not be the same as the desired language of the results. For example, someone who searched for *homo sapiens* was probably not looking for documents written in Latin. To address these kinds of queries, they introduced a non-linguistic signal: the country from which the searcher was accessing the search engine.

But geography, while useful, cannot be trusted as the only signal. For example, Ceylan and Kim found that a quarter of the English queries in their data came from countries whose primary language was not English.

Hence, Ceylan and Kim approached language identification as a machine learning problem, using a combination of query features, document features, and the searcher’s country. Their best classifier achieved an average of 94.5% accuracy across 10 European languages.

**When in Doubt, Ask!**

No language identification approach is perfect. Even an accuracy in the mid 90s means that there will be frequent errors. Besides, it’s never a good idea to rely entirely on algorithmic approaches when it’s easy to ask the searcher for clarification.

If your search engine serves a multilingual population, make it easy for the searcher to specify his or her language. Don’t hide this functionality behind an undiscoverable [advanced search](https://www.google.com/advanced_search) page. And if your algorithmic language identification exceeds some uncertainty threshold, offer the searcher a clarification dialogue to specify the desired language.

**Further Reading**

If you’d like to learn more about this topic, I recommend the 2014 “[Survey of Language Identification Techniques and Applications](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.689.5252&rep=rep1&type=pdf)” by Archana Garg, [Vishal Gupta](https://scholar.google.co.in/citations?user=O5zI_kIAAAAJ), and Manish Jindal, It discusses current work in this area, as well as a summary of the accuracy of various methods. It’s a well-written overview and serves a useful annotated bibliography.

**Previous:** [**Introduction**](/introduction-c98740502103#.p9dejf2ll)

**Next:** [**Character Filtering**](/character-filtering-76ede1cf1a97#.i91zgwxxn)