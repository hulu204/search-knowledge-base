---
title: 'Question Answering'
company: Tunkelang
tag: 问答
date: 2018-05-29
url: https://queryunderstanding.com/question-answering-94984185c203
account: 
origin: harvest3-202607
---
# Question Answering

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--94984185c203---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--94984185c203---------------------------------------)

4 min read

·

May 1, 2018

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D94984185c203&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquestion-answering-94984185c203&source=---header_actions--94984185c203---------------------post_audio_button------------------)

Share

When we talk about search, we have traditionally thought in terms of search results being documents or products. Searchers, however, increasingly think of search engines as question answering engines.

Many searchers expect to be able to express questions in natural language (e.g., [*What is the answer to life, the universe, and everything?*](https://www.google.com/search?q=What+is+the+answer+to+life%2C+the+universe%2C+and+everything%3F)) and obtain concise, relevant answers (in this case, [*42*](https://www.google.com/search?q=What+is+the+answer+to+life%2C+the+universe%2C+and+everything%3F&oq=What+is+the+answer+to+life%2C+the+universe%2C+and+everything%3F)). Moreover, the emergence of intelligent assistants like Siri, Alexa, and Google Assistant is training the next generation of searchers to ask direct questions and expect direct answers.

**Early QA Systems**

Question answering (QA) systems date back to the 1960s. Early QA systems focused on narrow, closed domains. Two notable examples are [BASEBALL](https://web.stanford.edu/class/linguist289/p219-green.pdf), which answered questions about a single season of American League baseball games, and [LUNAR](https://www.researchgate.net/publication/247926251_The_Lunar_Science_Natural_Language_Information_System_Final_Report), which answered questions about the analysis of rock samples from the Apollo moon missions. These systems parsed natural-language queries and translated them into database queries, which they executed against custom-built knowledge bases. They worked reasonably well, as long as the queries conformed to their narrow scope of knowledge.

In the 1980s and 1990s, researchers shifted their attention to more general-purpose, open-domain QA systems. Moving away from knowledge bases, they embraced an information retrieval approach (such as [this one](https://pdfs.semanticscholar.org/9302/d9ebe9369418e698a8a8ed1be8173e33d68f.pdf)) that was less domain-dependent. They treated each question as a search query, retrieved a set of relevant documents, extracted candidate answers from the results, and then presented the best candidate answer to the searcher. The emergence of open-domain QA systems inspired the Text Retrieval Conference (TREC) to establish a [question-answering track](https://trec.nist.gov/data/qamain.html), which has been running since 1999.

**Modern QA Systems**

The emergence of the web led to a large-scale digitization of knowledge, swinging the pendulum back to QA systems built on knowledge bases. Resources like Wikipedia became critical building blocks for these systems, the most famous being the [Watson](https://en.wikipedia.org/wiki/Watson_(computer)) system that IBM researchers built to defeat top [*Jeopardy!*](https://en.wikipedia.org/wiki/Jeopardy!) champions in 2011. That system mined 200 million pages to create a knowledge base, including a full crawl of Wikipedia.

At the same time, we started to see open-domain QA systems available to the general public. In 2009, [Wolfram Alpha](https://en.wikipedia.org/wiki/Wolfram_Alpha) launched an “answer engine” based on a collection of curated content, and Siri integrated with it when it launched in 2011. Finally, in 2012, Google embraced QA by launching its [Knowledge Graph](https://en.wikipedia.org/wiki/Knowledge_Graph), leveraging the [Freebase](https://en.wikipedia.org/wiki/Freebase) knowledge base from its acquisition of [Metaweb](https://en.wikipedia.org/wiki/Metaweb).

Unlike previous open-domain QA systems that relied on information retrieval to extract answers from unstructured content, modern QA systems build knowledge bases by extracting a rich [ontology](https://en.wikipedia.org/wiki/Ontology_(information_science)) of entities and relationships from a combination of structured and unstructured content. They take advantage of the latest developments in machine learning, representing text with [word embeddings](https://en.wikipedia.org/wiki/Word_embedding) and character embeddings, and using [deep learning](https://en.wikipedia.org/wiki/Deep_learning) — specifically sequence learning methods like [LSTM](https://en.wikipedia.org/wiki/Long_short-term_memory).

And most recently, “smart speakers” like the [Amazon Echo](https://en.wikipedia.org/wiki/Amazon_Echo) and [Google Home](https://en.wikipedia.org/wiki/Google_Home), are bringing voice-based QA systems into millions of homes.

**Challenges**

The foundation of a QA system is its knowledge base. Given the current state of the art, a knowledge base can be broad or deep but not both. Google’s Knowledge Graph optimizes for breadth, while domain-specific knowledge bases like [Twggle’s consumer product ontology](https://www.twiggle.com/product) optimize for depth. Decisions about where to emphasize breadth vs depth are critical trade-offs in the design of a QA system.

But the biggest challenges in designing QA systems come from their interface constraints.

Questions are natural-language queries, whether they are submitted through a keyboard or a microphone. As a result, the input interface can’t effectively use techniques like [autocomplete](/autocomplete-69ed81bba245) to guide the searcher. Any feedback to the searcher has to wait until after the searcher has submitted the query. Unfortunately, there are many opportunities for the system to misunderstand the searcher: spelling mistakes, voice recognition errors, and a variety of natural language processing errors. No system is perfect, but the error rate has to be low enough that searchers don’t simply give up in frustration.

The output interface for a QA system is even more constrained. Returning a single answer to the searcher — especially if it is presented as voice output — leaves almost no room for error. Such an interface is much less forgiving than a ranked list of search results that the searcher can scan. It forces a trade-off between accuracy and coverage: a QA system has to decide at what confidence threshold to present an answer, versus admitting that it doesn’t know. Rejecting too many questions frustrates searchers, but wrong answers quickly erodes trust. Ideally the interface would be [conversational](https://venturebeat.com/2017/09/30/voice-search-must-identify-user-intent-before-it-can-make-sales/), but none of today’s QA systems support meaningful conversation.

**Hybrid Approach**

Given all these challenges, it’s not surprising that we see hybrid approaches that combine traditional search engines with QA systems. When the QA system has high confidence, it returns an answer; otherwise, the system falls back to performing a search and returning a ranked list of results. This approach works reasonably well when the output is presented on a screen. For voice output, however, there isn’t a good analog to a result set.

A hybrid approach also makes it easier to develop a QA system incrementally. The initial coverage of the QA system might be a narrow set of frequent queries, or queries that conform to easily recognized patterns. Given how much more challenging it is to develop a QA system than a search engine, such an incremental approach makes it possible to prioritize QA efforts to focus on where they will deliver the highest return.

**Summary**

QA systems represent a logical evolution of search engines, catering to a new generation of searchers who expect to be able to express questions in natural language and obtain answers rather than search results. QA systems are becoming mainstream, but they still face many challenges. If the knowledge base is broad, it’s unlikely to be deep — and vice versa. Moreover, the interface constraints make it difficult to manage searcher expectations, and no one has developed QA systems that meaningfully support conversational interaction. Where possible — specifically, when there’s a display for the results — the best approach is generally a hybrid that combines QA with traditional search.

**Previous:** [**Search Results Clustering**](/search-results-clustering-b2fa64c6c809)

**Next:** [**Query Understanding and Voice Interfaces**](/query-understanding-and-voice-interfaces-6cd60d063fca)