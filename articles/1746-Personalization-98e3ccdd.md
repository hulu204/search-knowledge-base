---
title: 'Personalization'
company: Tunkelang
tag: 查询理解
date: 2021-10-13
url: https://queryunderstanding.com/personalization-3ed715e05ef
account: 
origin: harvest3-202607
---
# Personalization

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--3ed715e05ef---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--3ed715e05ef---------------------------------------)

3 min read

·

Nov 6, 2017

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D3ed715e05ef&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fpersonalization-3ed715e05ef&source=---header_actions--3ed715e05ef---------------------post_audio_button------------------)

Share

In 1964, information science pioneer [William Goffman](https://www.sciencedirect.com/science/article/pii/002002716490004X) said:

> Relevance is defined as a measure of information conveyed by a document relative to a query…[but] the relationship between the document and the query, though necessary, is not sufficient to determine relevance.

In other words, a search query isn’t always sufficient to establish the searcher’s intent and the relevance of results.

We’ve already discussed how [context](/contextual-query-understanding-65c78d792dd8) can influence query understanding. Now let’s look at the ultimate context: the searchers themselves.

**What is Personalization?**

Personalization is a broad term that extends beyond search. It refers to any attempt to customize a product or service to accommodate the particular needs of either an individual or a particular segment of the population.

In the context of query understanding, personalization means using information about the searcher to either personalize the estimation of query probabilities or supplement the query as a signal for query understanding.

The main sources for personalization are explicit input from the searcher, inferences from the searcher behavior, and inferences from population segments to which the searcher belongs.

**Personalized Query Probabilities**

Knowing who the searcher is helps us predict what he or she will search for. Searchers often repeat queries —sometimes even within the same [session](/session-context-4af0a355c94a) — and hence many search engines include a search history feature that provides convenient access to recently performed searches. More generally, what we know about a searcher’s interests allows us to personalize query probabilities.

As we saw in our discussion of [autocomplete](/autocomplete-69ed81bba245), we can use historical query logs to compute the probability of a query based on how frequently it appears in the log. This approach, however, doesn’t take into account the searcher’s [location](/geographical-context-77ce4c773dc7) or [seasonality](/seasonality-5eef79d8bf1c), let alone information about the individual searcher.

We can use machine learning to predict personalized query probabilities. Overall query frequency is one feature we would include in a machine learning model, but we would accomplish personalization through features like the following:

* Whether and how recently the searcher has performed the query.
* How the query relates to the searcher’s explicitly stated interests.
* Whether and how frequently the searcher has performed similar queries.
* Whether and how frequently searchers in a population segment to which the searcher belongs have performed the query or similar queries.

For searchers with a rich search history or a detailed collection of explicitly stated interests, features based on the individual searcher are likely to have high predictive value. When we don’t have much information from a searcher’s history or explicitly stated interest, we rely more on the behavior of population segments to which the searcher belongs.

**Personalization as an Intent Signal**

Sometimes our knowledge about the searcher helps clarify or refine the way we derive intent from the search query. We can use personalization for either query rewriting or result ranking.

For example, a searcher on a site that sells clothing is probably looking for clothes that he or she can wear. If we know— or can infer — the searcher’s gender and measurements, then we can rewrite the query to filter or boost results matching those constraints.

A more subtle use of personalization on a clothing site would be to favor styles that the searcher has purchased before, or that are popular with segments the searcher belongs to. We could implement this approach through boosting, or by including searcher-specific features in a [machine-learned ranking](https://en.wikipedia.org/wiki/Learning_to_rank) model. For broad queries that return large result sets, a change in ranking could lead to different searchers seeing completely different results from one another.

Using personalization as an intent signal requires care. Personalization should be a secondary signal that supplements the query: as with all context, it’s never enough to overcome the query itself as the primary signal.

**Summary**

As Goffman said, the query is necessary but not always sufficient to determine the searcher’s intent and hence which results will be relevant. Personalization can help establish the searcher’s intent, both during query formulation and query understanding. The query itself is still the primary input for understanding, but knowledge about the searcher provides valuable context.

**Previous:** [**Seasonality**](/seasonality-5eef79d8bf1c)

**Next:** [**Search as a Conversation**](/search-as-a-conversation-bafa7cd0c9a5)