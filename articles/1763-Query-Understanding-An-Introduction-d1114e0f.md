---
title: 'Query Understanding: An Introduction'
company: Tunkelang
tag: 查询理解
date: 2023-12-02
url: https://queryunderstanding.com/introduction-c98740502103
account: 
origin: harvest3-202607
---
# Query Understanding: An Introduction

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--c98740502103---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--c98740502103---------------------------------------)

3 min read

·

Oct 28, 2016

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc98740502103&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fintroduction-c98740502103&source=---header_actions--c98740502103---------------------post_audio_button------------------)

Share

Press enter or click to view image in full size

![]()

Search engines are so core to our digital experience that we take them for granted. Most of us cannot remember the web without Google to search its contents. Or online shopping without Amazon’s search engine to find what we want to buy. Search engines are how we navigate the digital world.

**But what is a search engine?** To most people — including most software engineers — a search engine is a system that accepts a text query as input and returns a list of results, ranked by their purported relevance to the query. Most work on search engines focuses on improving that ranking, with the help of increasingly sophisticated machine learning systems.

**Query understanding focuses on the beginning of the search process: the query.** [Query understanding](https://en.wikipedia.org/wiki/Query_understanding) is about what happens before the search engine scores and ranks results — namely, the searcher’s process of expressing an intent as a query, and the search engine’s process of determining that intent. In other words, query understanding is about the communication channel between the searcher and the search engine.

**Query understanding treats the query as first-class.** It makes queries the focal point of the search process. Much of query understanding takes place before retrieving a single result, although it’s possible to perform post-retrieval analysis for validation. But query understanding isn’t about determining the relevance of each result to the query. Rather, it establishes the interpretation of the query, against which results are judged.

**Query understanding plays a key role in the search user interface.** Because query understanding is the first step in the search process, it is the part of the process the user interacts with most intensely. Query understanding is core to basic search interface features like autocomplete, spellcheck, and query refinement. More broadly, query understanding pervades every interaction the searcher has with the search engine.

**In particular, query understanding is at the heart of search suggestions.** The most important kinds of suggestions are autocomplete suggestions, especially as autocomplete is becoming the primary surface for the search experience. More broadly, query formulation is itself a search problem — a search through the space of possible queries rather than through the space of results. And in a mobile-first world, it’s especially important to support query formulation and refinement, saving searchers from the delay and frustration of submitting ineffective search queries.

**Finally, focusing on query understanding creates a different mindset for search engine developers.** This focus shifts the emphasis from scoring and ranking to a goal of determining the searcher’s intent. Instead of striving to create the optimal ranking algorithm, search engine developers aspire to create the optimal query interpretation mechanism. The driving success metric is query performance — an end-to-end measure of the quality of the communication channel between the searcher and the search engine.

**Over the next months, this publication will take us through the journey from characters to words to phrases, and ultimately to meaning.**

We’ll start at the bottom of the query understanding stack with character-level techniques like normalization and tokenization. We’ll look at stemming, lemmatization, and dictionary-based canonicalization. We’ll continue on to higher-order operations like query relaxation, query segmentation, and entity recognition. Along the way, we’ll explore semantic resources like synonyms, hypernyms, taxonomies, ontologies, and knowledge graphs.

We’ll then look at ways that we can rewrite queries through automatic phrasing, field restriction, and query expansion. We’ll pay particular attention to autocomplete, from indexing prefix completions to providing structured autocomplete suggestions to weighing query probabilities against query performance.

Moving outside the search box, we’ll explore context — particularly session, geographical, and temporal contexts. We’ll then look at personalization, both explicit and implicit, and we’ll explore the differences between personalization and relevance.

We’ll then see how query understanding helps us establish search as a conversation between the searcher and the search engine. We’ll look at interaction patterns like clarification dialogs, faceted search, and relevance feedback. We’ll also explore results presentation, particularly snippets and clustering. Finally, we’ll look at natural-language search interfaces: question answering, voice interfaces, and chatbots.

**As you join me along this journey, I hope you’ll come to appreciate the key role that query understanding plays in the search process.** If you’re a software engineer, data scientist, or product manager working on a search engine, I encourage you to use what you learn to improve your searchers’ experience.

**Next:** [**Language Identification**](/language-identification-c1d2a072eda#.31zvyedn5)