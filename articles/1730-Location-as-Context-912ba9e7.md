---
title: 'Location as Context'
company: Tunkelang
tag: 查询理解
date: 2017-10-30
url: https://queryunderstanding.com/geographical-context-77ce4c773dc7
account: 
origin: harvest3-202607
---
# Location as Context

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--77ce4c773dc7---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--77ce4c773dc7---------------------------------------)

3 min read

·

Oct 23, 2017

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D77ce4c773dc7&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fgeographical-context-77ce4c773dc7&source=---header_actions--77ce4c773dc7---------------------post_audio_button------------------)

Share

Location often provides a strong signal of searcher intent. Sometimes location acts as an implicit part of the search query, such as when people are searching for local businesses. Other times, location is can subtly influence query understanding: aggregate data about searchers from a particular location helps establish a more precise query interpretation.

**Location as an Implicit Part of the Query**

For some searches, the searcher’s location acts as an implicit part of the search query. The canonical case is a search for a local business, e.g., a search for *restaurants* indicates a desire to find restaurants near the searcher’s current location, which hopefully the search engine can determine.

If the search engine is embedded in a mapping application like Google or Apple Maps, or business directory like Yelp, then nearly all queries carry local intent. In other cases, the search engine has to determine which queries have local intent. In the context of web search, for example, someone searching for *starbucks* probably wants to find the closest one, while someone searching for *starbucks suppliers* is less likely to care about the suppliers’ locations.

Determining whether a query has local intent is a classification problem, and the implementation of the classifier is highly dependent on the search application. But, as we’ll discuss in a moment, we can often learn from searcher behavior — specifically, which documents attract searchers from particular locations, and which queries exhibit engagement with results that depends on the searcher’s location.

**Location as an Intent Signal**

Sometime location isn’t part of the query intent, but it’s still useful as a signal. For example, *football* means something different in the United States than it does in the rest of the English-speaking world. People searching for *jackets* are likely to have preferences that reflect local climate.

Again, determining whether location is a useful intent signal for a particular query is a classification problem.

**How to Locate a Document**

While our focus is on query understanding, it helps to shift our focus to the documents. Specifically, we want to know when a document is associated with a particular location, and what that location is.

Looking at documents in general (not as part of a search application), we could choose to analyze the document text, using [entity recognition](/entity-recognition-763cae840a20) to find locations in the form of addresses or location names. This approach can work, but it’s vulnerable to two kinds of errors. One one hand, we might fail to recognize locations for documents that don’t contain salient location entities, e.g., a document about a mural or sculpture that doesn’t include its address. On the other hand, a location entity in the text may be spurious, e.g., it may be part of an author’s contact information or some other [boilerplate text](https://en.wikipedia.org/wiki/Boilerplate_(text)).

But we do have a search application, and we can take advantage of it. Specifically, we can use the locations of searchers engaging with a document to locate that document. When a document is strongly associated with a location, searchers engaging with the document tend to be tightly clustered around its associated location.

There are various ways to [geolocate](https://en.wikipedia.org/wiki/Geolocation) searchers, the simplest being to use their [IP addresses](https://en.wikipedia.org/wiki/IP_address). While geolocation can be noisy, it’s generally simpler and more reliable than applying entity recognition to document text — especially if all we want to know is the [centroid](https://en.wikipedia.org/wiki/Centroid) of the searchers’ locations and an estimate of the [variance](https://en.wikipedia.org/wiki/Variance) to determine how tightly they’re clustered.

Once we’ve associated documents with locations, we can use those associations to better classify which queries have local intent and to improve results for those queries.

**Summary**

Location often serves as a valuable contextual information to help us better understand search queries. Sometimes, location serves an implicit part of the search query; other times, its influence on query understanding is more subtle. We often know the searcher’s location, and we can associate documents with locations based on the locations of searchers that engage with those documents. Unlike in real estate, location isn’t everything. But it provides valuable context to improve query understanding.

**Previous:** [**Session Context**](/session-context-4af0a355c94a)

**Next:** [**Seasonality**](/seasonality-5eef79d8bf1c)