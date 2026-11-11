---
title: 'Autocomplete and User Experience'
company: Tunkelang
tag: 查询理解
date: 2022-05-18
url: https://queryunderstanding.com/autocomplete-and-user-experience-421df6ab3000
account: 
origin: harvest3-202607
---
# Autocomplete and User Experience

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--421df6ab3000---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--421df6ab3000---------------------------------------)

3 min read

·

Sep 1, 2017

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D421df6ab3000&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fautocomplete-and-user-experience-421df6ab3000&source=---header_actions--421df6ab3000---------------------post_audio_button------------------)

Share

The [previous post](/autocomplete-69ed81bba245) focused on how to determine the best autocomplete suggestions based on query probability and query performance. In this post, we’ll dive into some user experience concerns specific to autocomplete.

**Less is More**

How many autocomplete suggestions should we show to searchers? As a general principle, we should show them as few suggestions as possible. The set of suggestions shouldn’t be an exhaustive list that requires effort to scan — after all, it’s not that hard for the searcher to type one more character.

At the very least, all the suggestions should be visible on a single screen, without requiring the searcher to scroll down the page or use a scrollbar. This requirement poses a particularly tight constraint for mobile devices.

While every application is different, a good rule of thumb is to show at most five suggestions — and certainly no more than ten.

**Order**

There are two standard ways to order autocomplete suggestions: by score (i.e., query probability or some combination of query probability and query performance), or in alphabetical order.

On one hand, ordering suggestions by score minimizes how many results the searcher has to scan — assuming that the scoring function is working as intended. On the other hand, ordering suggestions alphabetically makes them easier for the searcher to scan.

Both approaches have their merits. Ordering suggestions by score works better when the top suggestion is dominant, i.e., the next-best suggestion has a significantly lower score. Ordering suggestions alphabetically works better when the differences in scores are insignificant.

A compromise is to order suggestions by score, but to use rounding to eliminate insignificant differences in scores, and then to break ties by sorting alphabetically.

**Structured Suggestions**

Autocomplete suggestions don’t have to be raw strings: they can take advantage of structured data in the index. For example *jea* could suggest *jeans in Men’s Clothing* and *jeans in Women’s Clothing*, both of which [scope](/query-scoping-ed61b5ec8753) the query *jeans* to a particular department. Autocomplete can serve as a painless entry point for [faceted search,](https://en.wikipedia.org/wiki/Faceted_search) especially on devices with limited screen real estate.

This approach works especially well when there is a dominant suggestion that leads to a large, diverse result set that the searcher will want to refine. Since structured suggestions replace a single suggestion with multiple suggestions, they work best when there’s a single dominant suggestion worth expanding to displace lower-scoring suggestions.

**Instant Search**

Instant search goes a step beyond autocomplete: instead of suggesting search queries, it shows searchers actual search results as they type.

Instant search works best for what information scientists call “known-item search”: the searcher has a single result in mind and can specify it precisely through a search query, such as a product name or document title.

Instant search offers the prospect of nearly frictionless search. Bear in mind, however, that not every search is a known-item search. Instant search isn’t useful for [exploratory search](https://en.wikipedia.org/wiki/Exploratory_search). Moreover, it introduces complexity and distraction, and it competes with autocomplete for the searcher’s attention. The search engine should only show instant search results when it is confident that the intended search query is a known-item search.

**Summary**

We’ve discussed several user experience considerations for autocomplete: the number of suggestions to present, the order of suggestions, the use of structured suggestions, and instant search. There are other user experience considerations, such as formatting and layout, which are beyond the scope of this post. There’s no single best approach for designing an autocomplete user experience, but hopefully this post provides useful guidelines.

**Previous:** [**Autocomplete**](/autocomplete-69ed81bba245)

**Next:** [**Contextual Query Understanding**](/contextual-query-understanding-65c78d792dd8)