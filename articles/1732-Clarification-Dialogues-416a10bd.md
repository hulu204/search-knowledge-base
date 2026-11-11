---
title: 'Clarification Dialogues'
company: Tunkelang
tag: 问答
date: 2018-01-03
url: https://queryunderstanding.com/clarification-dialogues-69420432f451
account: 
origin: harvest3-202607
---
# Clarification Dialogues

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--69420432f451---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--69420432f451---------------------------------------)

2 min read

·

Dec 13, 2017

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D69420432f451&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fclarification-dialogues-69420432f451&source=---header_actions--69420432f451---------------------post_audio_button------------------)

Share

As we saw in the [previous post](/search-as-a-conversation-bafa7cd0c9a5), modeling search as a conversation makes it possible to overcome breakdowns in communication between the searcher and the search engine. An important conversational technique is for the search engine to provide a clarification dialogue when it infers that such a breakdown may have occurred.

**“Did You Mean” and Automatic Rewriting**

Perhaps the most familiar clarification dialogue comes from [spelling correction](/spelling-correction-471f71b19880). When a search engine determines that a query has a significant probability of being misspelled, it shows results for the original query but proposes an alternative query as a “did you mean” suggestion.

Alternatively, it automatically rewrites the query, notifying the searcher with a prominent message above the search results. The interface typically includes a “search instead for” link that allows the searcher to override to automatic rewriting and see results for the original query.

This approach generalizes beyond spelling correction to other forms of [query rewriting](/query-rewriting-an-overview-d7916eb94b83). Query rewriting could include [query expansion](/query-expansion-2d68d47cf9c8#.gvckhp2rc), [query relaxation](/query-relaxation-342bc37ad425), [query segmentation](/query-segmentation-2cf860ade503), or [query scoping](/query-scoping-ed61b5ec8753). In all cases, the choice between a conservative “did you mean” and a more aggressive automatic rewriting with an opt-out should reflect the search engine’s confidence in its query interpretation.

**Optimizing for the Searcher’s Success**

The goal of a clarification dialogue should be to optimize for the searcher’s success. If the search engine has high confidence in its interpretation of the search query, then a clarification dialogue not only doesn’t help, but can harm the searcher by distracting from relevant results. But when the search engine doesn’t have high confidence in its interpretation, a clarification dialogue risks that distraction in order to hedges the search engine’s bet.

Deciding whether to present a clarification dialogue is essentially an optimization problem, with the goal of maximizing the expected utility for the searcher. Doing so requires three things:

* Making the search engine’s confidence in its primary interpretation explicit, preferably modeling it as a probability.
* Doing the same for any alternative interpretation that might be presented as a “did you mean”.
* Determining the expected harm caused by the insertion of a clarification dialogue, i.e., the cost of displacing potentially relevant results.

For this last computation, we can use log analysis or experimentation to determine the effect of position on engagement with relevant results. That can help us determine whether and where to insert a clarification dialogue.

**Summary**

Breakdowns in communication between the searcher and the search engine are unavoidable. Clarification dialogues offer at least a partial remedy: the opportunity for the search engine to hedge its bets. Using them effectively requires estimating the confidence of the search engine’s primary and alternative interpretation, as well as determining the harm from displacing relevant results. Clarification dialogues are a baby step towards conversational search, and towards recognizing that query understanding is never perfect.

**Previous:** [**Search as a Conversation**](/search-as-a-conversation-bafa7cd0c9a5)

**Next:** [**Relevance Feedback**](/relevance-feedback-c6999529b92c)