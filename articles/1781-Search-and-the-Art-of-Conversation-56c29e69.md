---
title: 'Search and the Art of Conversation'
company: Tunkelang
tag: 问答
date: 2024-07-29
url: https://dtunkelang.medium.com/search-and-the-art-of-conversation-b2171aa1a802
account: Tunkelang
origin: harvest3-202607
---
# Search and the Art of Conversation

What is the job of a search application? A common answer is that it needs to return the best results for a query, sorted in [relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) order. While this answer sounds reasonable, it glosses over an important nuance. A search application needs to engage in a conversation with the searcher.

### Intent

A query expresses the searcher’s [intent](https://medium.com/@dtunkelang/search-queries-and-search-intent-1dec79ad155f) but is not the intent itself. [Query understanding](https://queryunderstanding.com/introduction-c98740502103) aims to infer a representation of the searcher’s intent from the query. Neither query understanding nor retrieval can recover the signal lost when searchers map their intents to queries.

Hence, a critical responsibility for a search application is eliciting the searcher’s intent.

Unfortunately, search applications tend to underinvest in this aspect of the [search journey](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02). Even if they invest meaningfully in query understanding, they treat the query as a given.

Fortunately, there are several ways that search applications can be better conversationalists and help searchers communicate their intent.

### Autocomplete

Modern search applications include [autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245): searchers typing into a search box expect to see suggested completions. However, autocomplete is more than a way to help searchers type less. Autocomplete helps searchers express their intent, guiding them towards [better queries](https://queryunderstanding.com/better-search-through-better-queries-c192412a86e9).

A search application can offer suggestions even before the searcher starts typing. These are conversation starters. Often they are trending searches that encourage discovery or recent searches that facilitate refinding.

Autocomplete is a balancing act between two competing concerns: query popularity and query performance. On one hand, the probability of a query, to the extent that we can accurately compute it, tells us how likely the searcher is to select it as a suggestion. On the other hand, the predicted query performance is the likelihood that selecting that query leads to a successful outcome. While a perfect suggestion maximizes both, increasing one of these quantities tends to decrease the other. Hence, it is a tradeoff.

Also, autocomplete assumes a traditional interface where searchers type keyword queries. Autocomplete does not intuitively generalize to [voice interfaces](https://queryunderstanding.com/query-understanding-and-voice-interfaces-6cd60d063fca) or [natural language search](https://queryunderstanding.com/is-search-trying-too-hard-09557c29427f). Those interfaces place the burden of starting the conversation entirely on the searcher — which may be a key reason traditional keyword search is still dominant in search applications.

### Clarification

A common pattern in conversation is clarification: instead of responding to a speaker’s utterance, the listener seeks to establish a clear understanding of what the speaker intended. Clarification helps avoid embarrassing or even harmful misunderstandings.

Search applications should emulate this conversational pattern by using [clarification dialogues](https://queryunderstanding.com/clarification-dialogues-69420432f451) when uncertain of the searcher’s intent.

Indeed, search applications often use clarification dialogues for [spelling correction](https://queryunderstanding.com/spelling-correction-471f71b19880): when a search application determines that a query is likely to be misspelled, it proposes an alternative query as a “did you mean” suggestion, or executes the alternative query and offers the searcher the option to revert to the original query.

Clarification dialogues have applications beyond spelling correction. They generalize to other forms of [query rewriting](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83), such as [disambiguation](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc) (e.g., does “supernatural” mean the [Netflix show](https://en.wikipedia.org/wiki/Supernatural_(American_TV_series)), the [fitness app](https://www.getsupernatural.com/), or something else?), [expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8#.gvckhp2rc), [relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425), [segmentation](https://queryunderstanding.com/query-segmentation-2cf860ade503), and [scoping](https://queryunderstanding.com/query-scoping-ed61b5ec8753). In all these cases, the choice between a conservative “did you mean” and a more aggressive automatic rewriting with an opt-out should reflect the search application’s confidence in its query interpretation.

### Refinement

Even if a search query is clear, a search application may not know enough about the searcher’s intent to return useful results. If the query is [broad](https://medium.com/@dtunkelang/broad-and-ambiguous-search-queries-1bbbe417dcc), it may be only the first step in the searcher’s [search journey](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02).

For example, a search for “shoes” does not specify whether the searcher wants men’s or women’s shoes, athletic or dress shoes, etc. Retrieving all shoes is unlikely to lead the searcher to a successful outcome without additional effort on the searcher’s part.

When queries do not provide enough [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb), search applications should engage them in a conversation to elicit a more specific intent. They can offer [search suggestions that narrow the query](https://queryunderstanding.com/session-context-4af0a355c94a) or guide navigation of the intent space through [facets](https://queryunderstanding.com/faceted-search-7d053cc4fada). If the search application uses a natural language interface, it can respond with a request for a more specific query, offering examples as guidance.

All these methods allow search applications to engage searchers in a conversation that elicits — or helps them discover — a more specific intent.

### Persuasion

Finally, the search application can take an active role in shaping the searcher’s intent. Like a persuasive conversationalist, a search application has the opportunity to shape the searcher’s journey — at least partially.

Some search applications include [promoted search results](https://queryunderstanding.com/thoughts-on-promoted-search-results-ef124d11492f) that optimize for something other than the searcher’s utility, such as generating ad revenue or pushing house brands. By diverging from the searcher’s explicit intent, the search application aims to persuade the searcher to change that intent.

Persuasion is challenging. Searchers expect search applications to comply with their explicit intent and tend to respond negatively when search applications seem to misunderstand or ignore it. The search application should show that it hears and understands the searcher’s intent before trying to change it. For example, when a searcher specifies a particular brand, the search application should show available results for that brand — but can also show results from competing brands.

Ideally, the searcher benefits from being persuaded (e.g., by saving money). In practice, search applications often have more self-interested motives. Regardless of motive, persuasion can be part of how the search application engages the searcher in conversation.

### Summary

Eliciting the searcher’s intent is a prerequisite for understanding it and thus returning results that satisfy that intent. Autocomplete helps searchers express their intent. Clarification and refinement guide searchers through successful journeys. Finally, search applications can engage in persuasion. Ultimately, search applications need to do more than return the best results for a query. They need to engage searchers in conversations that lead to successful search journeys.
