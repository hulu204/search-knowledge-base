---
title: 'Query Understanding and Voice Interfaces'
company: Tunkelang
tag: 查询理解
date: 2018-09-18
url: https://queryunderstanding.com/query-understanding-and-voice-interfaces-6cd60d063fca
account: 
origin: harvest3-202607
---
# Query Understanding and Voice Interfaces

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--6cd60d063fca---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--6cd60d063fca---------------------------------------)

2 min read

·

May 29, 2018

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D6cd60d063fca&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-understanding-and-voice-interfaces-6cd60d063fca&source=---header_actions--6cd60d063fca---------------------post_audio_button------------------)

Share

On the surface, using a voice interface for search doesn’t seem that different from typing text into a search box.

**Converting speech to text and vice versa is a mostly solved problem.**

Speech recognition, while still not perfect, has matured to the point that it is ubiquitous. Application developers can leverage the major cloud providers — namely, [Amazon](https://aws.amazon.com/transcribe/), [Microsoft](https://azure.microsoft.com/en-us/services/cognitive-services/speech/), and [Google](https://cloud.google.com/speech-to-text/) —which provide reasonably priced APIs to use their speech-to-text services.

Meanwhile, computers have been able to talk to us for decades, and the quality of synthesized speech today is far more natural than when the [Software Automatic Mouth (SAM)](https://en.wikipedia.org/wiki/Software_Automatic_Mouth) speech synthesizer was released for personal computers in 1982. Indeed recent developments like [Google Duplex](https://ai.googleblog.com/2018/05/duplex-ai-system-for-natural-conversation.html) have raised [concerns](https://www.washingtonpost.com/news/the-switch/wp/2018/05/08/a-google-program-can-pass-as-a-human-on-the-phone-should-it-be-required-to-tell-people-its-a-machine/) that people will be unable to distinguish human speakers from AIs.

So, while there’s still ample opportunity to improve on both speech recognition and speech synthesis, both are good enough for everyday use.

**But there’s a big gap between recognizing speech and understanding it.**

At best, speech recognition reduces the problem of query understanding with voice to the problem of query understanding. But the state of query understanding is far less mature than that of speech recognition. Indeed the ability of computers to recognize speech but not understand it can be particularly frustrating searchers who don’t distinguish the two problems.

**And the biggest challenges come from interface constraints.**

On one hand, voice input interfaces lack [autocomplete](/autocomplete-69ed81bba245), [spelling correction](/spelling-correction-471f71b19880), or any other mechanisms to guide searchers as they construct queries. Hence, there’s a greater chance that the searcher make queries that the search engine is unable to understand.

On the other hand, today’s voice output interfaces don’t allow the searcher to easily [scan a set of search results](/search-results-presentation-7d6c6c384ec1), let alone [conversational](/search-as-a-conversation-bafa7cd0c9a5) mechanisms to refine queries, such as [clarification dialogues](/clarification-dialogues-69420432f451) and [faceted search](/faceted-search-7d053cc4fada). That not only makes voice interfaces less resilient to misunderstanding, but also limits the scope of queries that they can handle. In particular, voice interfaces are not well suited to [exploratory search](https://en.wikipedia.org/wiki/Exploratory_search).

**We’ll get there — someday.**

We’re just entering an age of voice interfaces for mainstream consumer applications. It will take some time to work out the kinks, improve query understanding, and figure out the design of conversational interfaces. But we’ll get there — at least once we start to recognize these challenges and face them head-on.

**Previous:** [**Question Answering**](/question-answering-94984185c203)

**Next:** [**Query Understanding and Chatbots**](/query-understanding-and-chatbots-5fa0c154f)