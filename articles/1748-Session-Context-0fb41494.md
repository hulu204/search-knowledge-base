---
title: 'Session Context'
company: Tunkelang
tag: 查询理解
date: 2022-01-03
url: https://queryunderstanding.com/session-context-4af0a355c94a
account: 
origin: harvest3-202607
---
# **Session Context**

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--4af0a355c94a---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--4af0a355c94a---------------------------------------)

3 min read

·

Oct 9, 2017

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D4af0a355c94a&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fsession-context-4af0a355c94a&source=---header_actions--4af0a355c94a---------------------post_audio_button------------------)

Share

The most immediate context for a search query is a search session, a sequence of activities the searcher performs in order to pursue an information-seeking task. Relating a search query to the searcher’s previous session activities helps us understand the searcher’s intent.

**Recognizing Query Refinement**

When a searcher performs two searches in a row, it’s often the case that the second search is an attempt to refine the first. How do we recognize query refinement, and what should we do once we recognize it?

There are three broad classes of query refinement:

* Narrowing: e.g., *iphone games* -> *free iphone games*.
* Broadening: e.g., *iphone kids games* -> *iphone games*.
* Lateral refinement, e.g., *iphone games* -> *android games*.

As we can see, these refinement classes correspond to adding, removing, and replacing tokens. This correspondence isn’t exact — for example, the query *iphone games* narrows *mobile games*. But it works well in practice.

**Why Searchers Refine**

When searchers refine queries, the type of refinement provides insight into their intent. For example, a searcher who refine form *iphone games* to *free iphone games* probably looked at the results for the first query, saw iPhone games that were not free, and then supplied additional information to narrow the results.

In general, it’s safe to assume that anyone refining a query is dissatisfied with the results. Refinement requires effort, and searchers, like all human beings, tend to be lazy. Hence, searchers expect their refined queries to return results that are substantially different than their original queries — at least on the first page.

Specifically, narrowing implies a desire to improve [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision) by filtering out irrelevant results, while broadening implies a desire to improve [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall) by retrieving more relevant results. The search engine should recognize what the searcher is trying to achieve, act accordingly, and clearly communicate its understanding back to the searcher. In particular, narrowing should return fewer results, while broadening should return more results.

**Personalization using Session Context**

Consider the following scenario. You search on an ecommerce site for shirts, and then narrow down to men’s shirts through [faceted navigation](https://en.wikipedia.org/wiki/Faceted_search). Continuing your online shopping, you search for pants and find that you again need to narrow down to men’s pants. After perform a similar sequence to find underwear, you wonder how the search engine can be so oblivious.

A little bit of session context goes a long way. If you are searching for shirts, pants, and underwear in a single session, then you are probably buying them for the same person (e.g., yourself) — which means the search engine should preserve attributes like gender and size.

As with all personalization, it’s important to be cautious. Overly aggressive personalization leads to false positives that cause more harm than good. But conservative inferences allow the search engine to understand queries more intelligently.

**Summary**

The use of session context for query understanding can be arbitrarily sophisticated. Any query understanding algorithm based on machine learning can incorporate session features into its model. In particular, search engines should recognize query refinement and respond to it intelligently.

But it’s important not to get so excited about session context that we ignore the query itself. Session context is useful, but the query will always be the strongest signal of the searcher’s intent.

**Previous:** [**Contextual Query Understanding**](/contextual-query-understanding-65c78d792dd8)

**Next:** [**Location as Context**](/geographical-context-77ce4c773dc7)