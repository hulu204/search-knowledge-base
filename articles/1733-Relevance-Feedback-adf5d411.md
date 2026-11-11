---
title: 'Relevance Feedback'
company: Tunkelang
tag: 搜索相关性
date: 2018-01-24
url: https://queryunderstanding.com/relevance-feedback-c6999529b92c
account: 
origin: harvest3-202607
---
# Relevance Feedback

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--c6999529b92c---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--c6999529b92c---------------------------------------)

4 min read

·

Jan 3, 2018

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc6999529b92c&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Frelevance-feedback-c6999529b92c&source=---header_actions--c6999529b92c---------------------post_audio_button------------------)

Share

The idea of modeling [search as a conversation](/search-as-a-conversation-bafa7cd0c9a5) has been around for decades. One of the oldest ideas in information retrieval is [relevance feedback](https://en.wikipedia.org/wiki/Relevance_feedback), which dates back to the 1960s. Relevance feedback allows searchers to tell the search engine which results are and aren’t relevant, guiding the search engine better understand the query and thus improve the results.

**Feedback Mechanisms**

The simplest relevance feedback mechanisms involve direct, explicit feedback applied to the search results themselves. The search engine accompanies each search result with buttons (or other interface elements) that allow the searcher to indicate whether or not that result was relevant. Alternatively, the search engine can provide a single feedback mechanism for the entire page.

It’s also possible for the search engine to collect implicit feedback about the results, based on the searcher’s behavior. When the searcher engages with a search result (e.g., by clicking on it), the search engine treats the engagement as implicit positive feedback. Conversely, when the searcher doesn’t engage with a search result — either by clicking on a lower-ranked result or by not clicking on any results — the search engine treats the lack of engagement as implicit negative feedback. This implicit feedback, while difficult to incorporate directly into the search experience, is useful for training [machine-learned ranking models](https://en.wikipedia.org/wiki/Learning_to_rank).

Finally, searchers can provide feedback at the level of terms (i.e., words or phrases) rather than documents. Term feedback can improve [recall](https://en.wikipedia.org/wiki/Information_retrieval#Recall) by guiding [query expansion](/query-expansion-2d68d47cf9c8), or it can improve [precision](https://en.wikipedia.org/wiki/Information_retrieval#Precision) by disambiguating the query. For example, if someone searches for *tulip bulbs* in order to find information about the historical [tulip mania](https://en.wikipedia.org/wiki/Tulip_mania), he or she could improve the search by providing positive feedback for the term *bubble* and negative feedback for the term *horticulture*. Term feedback is more abstract and complicated than result feedback, but it provides a clearer intent signal.

In between terms and documents, searchers can provide feedback at the level of passages, i.e., portions of documents. Passage-level feedback is common in the legal domain.

Finally, there’s a technique called [pseudo relevance feedback (or blind feedback)](https://en.wikipedia.org/wiki/Relevance_feedback#Blind_feedback): it simulates relevance feedback by reinforcing the top-ranked results as if the searcher had provided positive relevance feedback for them.

**Leveraging Feedback**

After the searcher provides feedback for the search results, the search engine uses this feedback to modify the search query and (hopefully) return more relevant results. If the search engine maps the query to a [vector space model](https://en.wikipedia.org/wiki/Vector_space_model), it maps the relevance feedback to the same vector space and rewrites the query as a combination of the two vectors. The goal is to adjust the query towards the results, terms, or passages that the searcher marked as relevant and away from those marked as irrelevant.

The best-known relevance feedback technique is the [Rocchio algorithm](https://en.wikipedia.org/wiki/Rocchio_algorithm), which was developed in the 1960s. Lucene’s [MoreLikeThis](https://lucene.apache.org/solr/guide/7_2/morelikethis.html) class is a variant of the Rocchio algorithm. More recently developed approaches tend to be probabilistic and rely on [statistical language models](https://en.wikipedia.org/wiki/Language_model).

**Challenges**

Despite its promise, relevance feedback hasn’t seen significant adoption outside of the legal domain and academic research settings — other than the use of implicit feedback from clicks to train ranking models. Its lack of mass adoption reflects three challenges with applying relevance feedback.

The first challenge is that relevance feedback mechanisms struggle when the set of relevant results is not homogenous — particularly if there are two or more distinct clusters of relevant results. For example, the relevant results for a search might include a mix of long-form documents and short-form messages. The more heterogeneous the relevant results, the greater the risk that relevance feedback will favor some segments of the relevant results at the expense of others. This feedback can misdirect the search engine, ultimately degrading the overall relevance of the results.

The second challenge is that explicit relevance feedback requires searchers to expend effort on top of the search itself. Most people avoid efforts they feel are unnecessary. Searchers who find relevant results probably won’t be motivated to perform the additional action of explicitly providing positive feedback to the search engine. Conversely, searchers who receive irrelevant results won’t necessarily want to actively help the search engine; instead, they are likely to try a different query — or a different search engine.

The third challenge is familiarity bias. Since few search engines outside of academic research settings employ relevance feedback, most developers and product managers are wary of presenting searchers with unfamiliar interfaces and risking a negative impact on searcher engagement.

**Summary**

Relevance feedback is one of the oldest ways to model search as a conversation. By telling the search engine which results are and aren’t relevant, searchers can help the search engine help them. But its lack of mass adoption suggests that we will need to overcome the challenges of result diversity, searcher motivation, and familiarity bias in order to make effective use of relevance feedback to improve query understanding.

**Previous:** [**Clarification Dialogues**](/clarification-dialogues-69420432f451)

**Next:** [**Faceted Search**](/faceted-search-7d053cc4fada)