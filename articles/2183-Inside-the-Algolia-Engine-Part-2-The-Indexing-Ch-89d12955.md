---
title: 'Inside the Algolia Engine Part 2 — The Indexing Challenge of Instant Search'
company: Algolia
tag: 索引构建
date: 2016-05-02
url: https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search
account: 
origin: harvest3-202607
---
- [* English](#)
  [* Deutsch](/de/search/ "Switch to ")
  [* français](/fr/search/ "Switch to ")
- [* English](#)
  [* German](# "Switch to ")
  [* French](# "Switch to ")
  [* Brazilian Portuguese](# "Switch to ")
  [* Spanish](# "Switch to ")
  [* Italian](# "Switch to ")

[Join us: 
Algolia DevCon 2026: Sep 30 - Oct 1, 2026 — VIRTUAL

Register Now](https://www.algolia.com/devcon?utm_cta=topbannerpromo)

[NEW: 
Algolia CEO on BBC: The Future of AI Search for Retail

Read more](https://www.algolia.com/resources/asset/video-bbc-interview?utm_cta=topbannerpromo)

* [Company](/about)
* [Partners](/partprog)
* [Support](https://support.algolia.com/)
* [![](/files/live/sites/algolia-assets/files/icons/person_blue.svg)
  Login](https://dashboard.algolia.com/users/sign_in)
* [![](/files/live/sites/algolia-assets/files/icons/Check%20Square.svg)
  Logout](https://dashboard.algolia.com/users/sign_out)

[Algolia mark white

Algolia logo white](https://www.algolia.com/)

CLOSE

* Products

  [![navigation image](/files/live/sites/www/files/ad-banners/Screenshot%202026-05-29%20at%201.29.21%e2%80%afPM.png)](https://www.algolia.com/resources/asset/infographic-value-of-choosing-algolia?utm_cta=navigationpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/search.svg)

  ##### AI Search & Retrieval

  + [Overview](/products)
  + [Search

    Show users what they're looking for with AI-driven results.](/products/ai-search)

    [Search](/products/ai-search)

    Show users what they're looking for with AI-driven results.
  + [Recommendations

    Use behavioral cues to drive higher engagement.](/products/ai-recommendations)

    [Recommendations](/products/ai-recommendations)

    Use behavioral cues to drive higher engagement.
  + [Personalization

    Show each user what they need across their journey.](/products/features/personalization)

    [Personalization](/products/features/personalization)

    Show each user what they need across their journey.
  + [Analytics

    All your insights in one dashboard.](/products/features/analytics)

    [Analytics](/products/features/analytics)

    All your insights in one dashboard.
  + [Browse

    Move customers down the funnel with curated category pages.](/products/ai-browse)

    [Browse](/products/ai-browse)

    Move customers down the funnel with curated category pages.

  ![](/files/live/sites/algolia-assets/files/icons/navigation/ai.svg)

  ##### Artificial Intelligence

  + [OVERVIEW](https://www.algolia.com/products?utm_cta=aioverview)
  + [Agent Studio

    Create, test, and deploy AI agents, fast.](/products/ai/agent-studio)

    [Agent Studio](/products/ai/agent-studio)

    Create, test, and deploy AI agents, fast.
  + [Generative Experiences

    Build conversational solutions with retrieval augmented generation (RAG).](/products/ai/generative-experiences)

    [Generative Experiences](/products/ai/generative-experiences)

    Build conversational solutions with retrieval augmented generation (RAG).
  + [Ask AI

    Deliver conversational answers—right from your search bar.](/products/ai/ask-ai)

    [Ask AI](/products/ai/ask-ai)

    Deliver conversational answers—right from your search bar.
  + [MCP Server

    Search, analyze, or monitor your index within your agentic workflow.](/developers/lp-mcp)

    [MCP Server](/developers/lp-mcp)

    Search, analyze, or monitor your index within your agentic workflow.

  ![](/files/live/sites/algolia-assets/files/icons/navigation/intelligence.svg)

  ##### Intelligent Data Kit

  + [Overview](/products/intelligent-data-kit)
  + [Data Enrichment

    Modify, enhance, or restructure data as it’s indexed for search.](/products/features/data-enrichment)

    [Data Enrichment](/products/features/data-enrichment)

    Modify, enhance, or restructure data as it’s indexed for search.
  + [Data Transformation

    Streamline data preparation and enhance data quality.](/products/features/data-transformation)

    [Data Transformation](/products/features/data-transformation)

    Streamline data preparation and enhance data quality.
  + [Integrations

    Connect to your existing stack via pre-built libraries and APIs.](/developers/integrations)

    [Integrations](/developers/integrations)

    Connect to your existing stack via pre-built libraries and APIs.

  ![](/files/live/sites/algolia-assets/files/icons/navigation/infra.svg)

  ##### Infrastructure

  + [Overview](/distributed-secure/global-infrastructure)
  + [Data Centers

    Choose from 70+ data centers across 17 regions.](/distributed-secure/global-infrastructure)

    [Data Centers](/distributed-secure/global-infrastructure)

    Choose from 70+ data centers across 17 regions.
  + [Security & Compliance

    Built for peace of mind.](https://trust.algolia.com/)

    [Security & Compliance](https://trust.algolia.com/)

    Built for peace of mind.
* Solutions

  [![navigation image](/files/live/sites/www/files/homepage-carousel/cropped-foreground-gartner-magic-quadrant.png)](https://www.algolia.com/lp/gartner-magic-quadrant-2026?utm_cta=navigationpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/industry_icon.svg)

  ##### Industries

  + [SEE ALL](/industries)
  + [Auto Parts](/industries/auto-parts)

    [Auto Parts](/industries/auto-parts)
  + [B2B Commerce](/industries/b2b-ecommerce)

    [B2B Commerce](/industries/b2b-ecommerce)
  + [Ecommerce](/industries/ecommerce)

    [Ecommerce](/industries/ecommerce)
  + [Fashion](/industries/fashion)

    [Fashion](/industries/fashion)
  + [Grocery](/industries/grocery)

    [Grocery](/industries/grocery)
  + [Higher Education](/industries/higher-education)

    [Higher Education](/industries/higher-education)
  + [Media](/industries/media)

    [Media](/industries/media)
  + [Marketplaces](/industries/marketplaces)

    [Marketplaces](/industries/marketplaces)
  + [SaaS](/industries/saas)

    [SaaS](/industries/saas)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/usecase_icon.svg)

  ##### Use Cases

  + [SEE ALL](/use-cases)
  + [Documentation search](/use-cases/documentation-search)

    [Documentation search](/use-cases/documentation-search)
  + [Enterprise search](/use-cases/enterprise)

    [Enterprise search](/use-cases/enterprise)
  + [Headless commerce](/use-cases/headless-commerce)

    [Headless commerce](/use-cases/headless-commerce)
  + [Image search](/use-cases/image-search)

    [Image search](/use-cases/image-search)
  + [Merchandising Studio](/industries/ecommerce/digital-merchandising)

    [Merchandising Studio](/industries/ecommerce/digital-merchandising)
  + [Retail Media Network](/use-cases/retail-media-network)

    [Retail Media Network](/use-cases/retail-media-network)
  + [Site search](/use-cases/site-search)

    [Site search](/use-cases/site-search)
  + [Visual search](/use-cases/visual-search)

    [Visual search](/use-cases/visual-search)
  + [Voice search](/use-cases/voice-search)

    [Voice search](/use-cases/voice-search)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/team_icon.svg)

  ##### Departments

  + [Digital Experience](/department/digital-experience)

    [Digital Experience](/department/digital-experience)
  + [Ecommerce](/department/ecommerce)

    [Ecommerce](/department/ecommerce)
  + [Engineering](/department/engineering)

    [Engineering](/department/engineering)
  + [Merchandising](/department/merchandisers)

    [Merchandising](/department/merchandisers)
  + [Product Management](/department/product-management)

    [Product Management](/department/product-management)
* [Pricing](/pricing)
* Developers

  [![navigation image](/files/live/sites/www/files/Screenshot%202026-06-25%20at%2010.37.59%e2%80%afAM.png)](https://www.algolia.com/devcon?utm_cta=topbannerpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/get-started_icon.svg)

  ##### Get started

  + [Developer Hub](/developers)

    [Developer Hub](/developers)
  + [Documentation](https://www.algolia.com/doc/)

    [Documentation](https://www.algolia.com/doc/)
  + [Integrations](/developers/integrations)

    [Integrations](/developers/integrations)
  + [UI Components](/developers/search-ui)

    [UI Components](/developers/search-ui)
  + [Autocomplete](/products/features/search-autocomplete)

    [Autocomplete](/products/features/search-autocomplete)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/resources_iconv2.svg)

  ##### Resources

  + [Code Exchange](/developers/code-exchange)

    [Code Exchange](/developers/code-exchange)
  + [Engineering Blog](/blog/engineering)

    [Engineering Blog](/blog/engineering)
  + [MCP](/developers/lp-mcp)

    [MCP](/developers/lp-mcp)
  + [Discord](https://alg.li/discord)

    [Discord](https://alg.li/discord)
  + [Webinars & Events](/events)

    [Webinars & Events](/events)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/links_icon.svg)

  ##### Quick Links

  + [Quick Start Guide](https://www.algolia.com/doc/guides/getting-started/quick-start/)

    [Quick Start Guide](https://www.algolia.com/doc/guides/getting-started/quick-start/)
  + [For Open Source](/for-open-source)

    [For Open Source](/for-open-source)
  + [API Status](https://status.algolia.com/)

    [API Status](https://status.algolia.com/)
  + [Support](https://support.algolia.com/hc/en-us)

    [Support](https://support.algolia.com/hc/en-us)
* Resources

  [![navigation image](/files/live/sites/www/files/ad-banners/llm-leaderboard-nav-banner.avif)](https://www.algolia.com/llm-leaderboard/?utm_cta=navigationpromo)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/discover_icon.svg)

  ##### Discover

  + [Algolia Blog](/blog)

    [Algolia Blog](/blog)
  + [Resource Center](/resources)

    [Resource Center](/resources)
  + [Customer Stories](/customers)

    [Customer Stories](/customers)
  + [Webinars & Events](/events)

    [Webinars & Events](/events)
  + [Newsroom](/about/news)

    [Newsroom](/about/news)
  + [AI Search Newsletter](/lp/subscription-newsletter)

    [AI Search Newsletter](/lp/subscription-newsletter)
  + [Product Demo Videos](https://www.algolia.com/resources?contentType=Product%20Demos)

    [Product Demo Videos](https://www.algolia.com/resources?contentType=Product%20Demos)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/resources_icon.svg)

  ##### Customers

  + [Customer Hub](/customer-hub)

    [Customer Hub](/customer-hub)
  + [What's New](https://changelog.algolia.com/)

    [What's New](https://changelog.algolia.com/)
  + [Knowledge Base](https://support.algolia.com/hc/en-us)

    [Knowledge Base](https://support.algolia.com/hc/en-us)
  + [Documentation](https://www.algolia.com/doc)

    [Documentation](https://www.algolia.com/doc)
  + [Algolia Academy](https://academy.algolia.com)

    [Algolia Academy](https://academy.algolia.com)
  + [Professional Services](/professional-services-support)

    [Professional Services](/professional-services-support)

  ![](/files/live/sites/algolia-assets/files/icons/navigation/tools_icon.svg)

  ##### Tools

  + [Search Grader](https://www.algolia.com/ai-search-grader/)

    [Search Grader](https://www.algolia.com/ai-search-grader/)
  + [Profit Simulator](https://www.algolia.com/profit-simulator/)

    [Profit Simulator](https://www.algolia.com/profit-simulator/)
  + [Ecommerce Search Audit](https://www.algolia.com/search-audit)

    [Ecommerce Search Audit](https://www.algolia.com/search-audit)
  + [LLM Leaderboard](https://www.algolia.com/llm-leaderboard)

    [LLM Leaderboard](https://www.algolia.com/llm-leaderboard)
  + [Agentic Readiness Assessment](https://www.algolia.com/dev-agentic-readiness)

    [Agentic Readiness Assessment](https://www.algolia.com/dev-agentic-readiness)

Quick Access

+ [![](/files/live/sites/algolia-assets/files/icons/apartment_blue.svg)

  Company](/about)
+ [![](/files/live/sites/algolia-assets/files/icons/handshake_blue.svg)

  Partners](/partprog)
+ [![](/files/live/sites/algolia-assets/files/icons/support_blue.svg)

  Support](https://support.algolia.com/)
+ [![](/files/live/sites/algolia-assets/files/icons/person_blue.svg)

  Login](https://dashboard.algolia.com/users/sign_in)
+ [![](/files/live/sites/algolia-assets/files/icons/Check%20Square.svg)

  Logout](https://dashboard.algolia.com/users/sign_out)

[Fix your search](/demorequest)

[Get started](https://dashboard.algolia.com/users/sign_up)

Search or Ask AI

Close

[Fix your search](/demorequest)

[Get started](https://dashboard.algolia.com/users/sign_up)

✨
AI mode

Filter by source

✨
How will Algolia improve our search experience and conversions?

✨
How do I integrate Algolia search into my app?

✨
Can Algolia help shoppers find products faster and increase sales?

✨
Will Algolia scale with our traffic and data size?

Suggestions

Products & Resources

✨
Algolia Assist

New chat
Back to results

[AI powered by Algolia](https://algolia.com/products/ai/agent-studio)

[Clear All Filters](javascript:void(0))

## Algolia Assist

[Schedule a call](/demorequest/)
[Sign up today](/users/sign_up?ssnav=start)

## How can I help you today?

I search through your content to help you find answers to your questions, fast.

AI powered by Algolia

![](/files/live/sites/algolia-assets/files/icons/algolialogo.svg)

Looking for our logo?

We got you covered!

[Brand guidelines](https://algolia.frontify.com/)

[Download logo pack](https://www.algolia.com/algolia-logo-pack.zip  )

Engineering

# Inside the Algolia Engine Part 2 — The Indexing Challenge of Instant Search

Published: 
August 02, 2023

![](/files/live/sites/algolia-assets/files/blogs/bannerimages/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search.webp)

[Back to all blogs](/blog/engineering)

Inside the Algolia Engine Part 2 — The Indexing Challenge of Instant Search

Search engine usage has evolved a lot in the last few years. Today’s users expect instant feedback without having to click on the “enter” button and wait for the page to load to get their results. They also expect the engine to tolerate typing mistakes on the fly without having to validate proposals of query re-phrasing, like the (in)famous “did you mean?”

Of course all these changes have pretty big consequences on the engine itself. In this post, we will concentrate on the way we handle indexing at Algolia, why we do it differently in order to maximize indexing speed and search performance and how we natively address these evolutions in search.

## Introduction to indexing

The goal of the indexing process is to store your data in a specific data-structure that is optimized for search. Without indexing, we would need to scan all the documents in a database to detect which ones match a query. This would take forever and be highly inefficient, ultimately resulting in a terrible user experience. This is one of the reasons we continue to focus on optimizing indexing speed as part of our overall efforts to make search more efficient.

The main part of the indexing process is to create a data-structure that contains a mapping of each word to the associated list of documents containing this word. One mapping of the word to the list of documents is called an inverted list, with the name coming  from the inversion of the space: instead of having documents that contains words, we have now words with the list of documents containing each word. The concept is similar to the index you have at the end of a book, except all words are in the index.

There are a lot of algorithms to store those inverted lists in an efficient way while keeping good performance. Most of those techniques are pretty old and well described in the very good [Managing Gigabytes](https://books.google.fr/books/about/Managing_Gigabytes.html?id=2F74jyPl48EC&redir_esc=y) book.

The creation of those inverted lists can be decomposed in two big parts:

* For each document, we extract the list of words and build a hash-table that associates words to documents
* When all documents are processed, we compute an on-disk binary data-structure containing the mapping of words to documents. This data-structure is the index we will use to process queries.

## How search-as-you-type is usually implemented

As-you-type display of search results was introduced by Google in 2010 as “Google Instant” and later referred to as “Instant Search.” Users love this experience as it creates a seamless interaction with the data they are looking for! It removes the intermediate steps such as query validation, “did-you-mean” re-phrasing and decreases the time spent waiting for the results to show up! It also means indexing and search have to be redesigned because you don’t simply search for words anymore, but also for partially written words (prefixes) and it needs to be very fast!  
There are four main different approaches engineers use today to build this type of instant search:

### **1) Autocomplete (also called Suggest)**

This approach is the most commonly used and is based on a static data-structure on the side of the search engine. You can see it as a big dictionary in the form of a [Trie](https://en.wikipedia.org/wiki/Trie) (special type of Tree that associates string to an output, all the descendants of a node have a common prefix of the string).

**Advantages:**

* Very fast response time (usually few milliseconds)
* Scales well, can easily handle thousands of queries per second on one machine

**Drawbacks:**

* This is not a search engine, you have to search for a sub-string on the pre-defined list of expressions in the dictionary. In terms of user-experience, it often leads to very frustrating “no results” or “bad results” because of this limitation
* The relevance is not the same as the search engine itself, it is just a static dictionary. It works well if you propose “frequent queries,” but starts to have weird effects if you use it to search on the same records as the fully-featured search engine itself. The relevance will be different, of lesser quality and will lead to a lot of confusion.

### **2) Index prefixes**

This approach is simply to build an inverted list for all prefixes of a word instead of just the word itself. For example instead of just having an inverted list for the word “engine”, you will also have one for “e”, “en”, “eng”, “engi” and “engin”. Those lists will usually contain a specific indicator that allows at query time to make the difference between a prefix and an exact word (both exact and prefix inverted lists will be queried with a preference for exact).

**Advantages:**

* Fast resolution of prefixes as they are pre-computed
* Ability to keep the relevance of the search-engine for all interaction with the engine, including as-you-type experience (user is never lost between two different ways to rank results)

**Drawbacks:**

* Increase the time to publish results because the indexing process is far more expensive than without inverted list and consumes far more memory (inverted list are kept in memory)
* Increase a lot the size of the index, which reduces a lot the likelihood of fitting in memory and so can hurt performance (even on a SSD)

### **3) ngrams computation**

This approach is very similar to the indexing of all prefixes but it limits the computation of prefixes by allowing a minimum and a maximum number of letters in the prefix. The main advantage is to reduce the cost compared to the indexing of all prefixes, if you query a prefix that is bigger than the maximum number of letters, the query will be automatically be transformed into a query on several ngrams (queries with fewer letters than the minimum will not trigger the prefix search).

Advantages and drawbacks are the same as the indexing of all prefixes; it is just a small improvement to reduce a bit the cost of indexing by adding more computation in the search.

### **4) Search prefixes at search time**

This approach keeps the indexing process pretty light by keeping only one inverted list per word but it requires to do all the processing at query-time. For example if you perform the query ‘a’, it will mean looking for all words that start by ‘a’ in a big dictionary and then perform a query with all those words in a big OR operand. This approach is very expensive and usually people that select this approach start the prefix search after a certain number of letters in the prefix to avoid having queries that are too expensive.

**Advantages:**

* No indexing overhead for prefix searches
* No compromises on the relevance of the search-engine

**Drawbacks:**

* Produces very complex and slow queries
* Only works if the number of documents and words is very small, it does not scale

Engineers working on search have no other choice than spending time to test those different approaches and select the one that seems the best for their use cases, unfortunately all of them have serious drawbacks.

## A different approach

At the beginning of Algolia, we worked on a different product: an offline search engine SDK for mobile app developers. And we wanted this engine to provide a fast instant search experience on old devices like an iPhone 3G.

None of the standard approaches described above would have worked on such a low-end hardware, so we had to design a new way to do the indexing with very little RAM and CPU. All that while maintaining an instant search experience (one of the purpose of indexing being to speed up the search operations).

Having already worked on multiple data-structures for search engines prior to Algolia helped me a lot in designing a different way to solve the problem. The first inspiration came from a generational string B-tree I built several years ago. It was pretty similar to what the [LevelDB](https://github.com/google/leveldb) fast key-value store developed by Google is doing (associate an arbitrary size value to an arbitrary size string).

First, I knew that for Algolia I wanted to have a generational data-structure.

### **Generational data-structure**

Having a generational data-structure makes updating the data a lot faster. Typically, you’ll create two (or more) “generations” of your data-structure. A big one containing the “old” data, and a small one containing the “new” data.

Then, if you need to add/update/delete an object, you’ll update a smaller structure containing only the “new” information, which is much faster.

### **Merge of Generational data-structure**

At some point (generally when your smallest generation reaches a certain size), you’ll need to merge several generations into one for a better efficiency. This operation is called a merge.

In order to have an efficient merge, each generation needs to be sorted, so that you can scan them in parallel while generating the result (merge of the parallel scan is done via a standard heap-merge algorithm).

### **Radix tree**

For Algolia, I decided to represent the words that will be searchable as a [radix tree](https://en.wikipedia.org/wiki/Radix_tree) (space-optimized representation of a Trie, below we look at what a radix tree is in practice).

First because a radix tree is sorted, which allowed us to have an efficient merge and to use multiple generations of the tree.

Second because it works very well to process the typo-tolerance in a very efficient way (more details on the typo-tolerance will come in another post).

It is easy to build a radix tree in memory before writing it on disk, but it consumes a lot of RAM. And I wanted to use the least amount of RAM possible, because:

1. For the initial offline search SDK, we simply didn’t have enough RAM on an iPhone 3G.
2. For our current SaaS engine, we want the RAM to be focused on making search fast (the indices are all stored on RAM for search), which means indexing should consume the minimum amount of RAM.

What’s great is that you can actually write a radix tree on the fly without having to build the tree in memory if you’re indexing a list of sorted words.

For example, let’s consider that the dataset we want to search on contains 5 objects, each having a single word. Each object will be represented by a value from 1 to 5.

Normally, multiple objects could have the same word, so the leaf would have a list of values. But for simplicity’s sake, we’ll take records containing different words.

![dictionary1-e1462180935434.png](/files/live/sites/algolia-assets/files/blogs/2025/dictionary1-e1462180935434.png)

Dictionary example mapping a word to an integer

Each node of our radix tree will contain a string.

If the node is a leaf, it has a value associated to the corresponding object having this word.

If the node is not a leaf, it can have an associated value, but it can also just be an internal node representing a shared prefix.

The radix-tree we’re going to build will look like this:

![dictionary-2-e1462181068823.png](/files/live/sites/algolia-assets/files/blogs/2025/dictionary-2-e1462181068823.png)

Radix-tree of the previous dictionary

Now, let’s build our radix-tree. Seems simple now enough, right? The naive approach is to build the complete data-structure in memory and then to dump it on disk. We do not want to use this approach because we want to keep as much memory as possible on our servers to hosts the indices of our users and provide a fast search! This is why we designed all the indexing to use as little memory as possible while optimizing speed of indexing.

Here’s the trick: we can build this data-structure on-disk directly from the list of words and with only a few kilobytes of memory. To do that, we’ll flush from the RAM the nodes as soon as possible, by building the tree on the fly.

The first step is to order alphanumerically the words of the documents we want to index (which is already done in our example).

Then, we’re going to build our tree using a [depth-first search](https://en.wikipedia.org/wiki/Depth-first_search): since a radix tree is sorted in the alphanumeric order, it’ll be easy to flush nodes to the disk as soon as we don’t need them.

1) Add the word Fast

![dictionary-3-e1462181232517.png](/files/live/sites/algolia-assets/files/blogs/2025/dictionary-3-e1462181232517.png)

2) Add the word Faster

![dictionary-4-e1462181279567.png](/files/live/sites/algolia-assets/files/blogs/2025/dictionary-4-e1462181279567.png)

3) Add the word Test

![dictionary4Fixed.png](/files/live/sites/algolia-assets/files/blogs/2025/dictionary4Fixed.png)

4) Flush the branch “fast” to disk

![dictionary5Fixed.png](/files/live/sites/algolia-assets/files/blogs/2025/dictionary5Fixed.png)

5) Add the word toaster

![dicationary-7-e1462181493671.png](/files/live/sites/algolia-assets/files/blogs/2025/dicationary-7-e1462181493671.png)

6) Flush the branch “est”

![dicationary-8-e1462181678105.png](/files/live/sites/algolia-assets/files/blogs/2025/dicationary-8-e1462181678105.png)

7) Add the word toasting

![dicationary-9-e1462181731807.png](/files/live/sites/algolia-assets/files/blogs/2025/dicationary-9-e1462181731807.png)

8) Finally, flush the branch “er”, then “ing”, “oast” and finally “t”

This process is a very efficient way to build a tree because it only keeps in memory a very small number of nodes (in the worst case scenario you will have a number of nodes in memory that is equal to the longest key in the tree, in our case we always have fewer than 100 nodes in memory).Now that this is done, let’s focus on the next part: prefix search!

### **Prefix search**

Remember that we wanted an instant search experience. This means that the engine must be able to retrieve results as-you-type, at each character.

If you type “f”, you want to retrieve the results “fast” and “faster”, so the engine must know that both these words contain the prefix “f”.

And we don’t want to calculate the association prefix-object for all the prefixes, which would take a lot of time and memory, but only when it’s really necessary.

The good news is that our radix tree can tell us precisely where we need to store prefixes: all the nodes in the tree which have children.

In our example, it is only necessary for the nodes “fast”, “t” and “toast”.

![dicationary-10-e1462181862124.png](/files/live/sites/algolia-assets/files/blogs/2025/dicationary-10-e1462181862124.png)

Radix-tree with prefix inverted list computed

You see what I just did right there? Yes! the prefixes can be computed on the fly too! We just need to remember what was in the last few branches that we flushed.

For example, if I just flushed the branch “est”, I’ll remember that the prefix “t” is associated to the object 3 (test). I’ll do the same with “toaster” (object 4) and “toasting” (object 5). And when we’re done processing all the words beginning with “t”, I’ll know that this node should contain the objects 3, 4 and 5.

## A few numbers

This way to build prefixes has been built into our engine since 2012 and we index billions of jobs every day with this algorithm. We have measured the impact on a lot of different indices, the impact on search is pretty obvious as we always have the prefix inverted list when we do a query (and we’ll have a lot of RAM handy), but the impact on indexing time and on the size are less obvious. Here is a small summary of the impacts that are very small compared to the advantages it gives at query time:

|  |  |  |  |
| --- | --- | --- | --- |
|  | Minimum | Average | Maximum |
| Impact of prefixes on index size | +9% | +21% | +43% |
| Impact of prefixes on indexing speed | +3% | +12% | +17% |

This approach is significantly better than any of the other approaches presented before, it is actually optimal at query time and has a very reasonable impact on indexing performance!

This optimization of the prefixed indexing is just one of the numerous optimizations we have built in the Algolia engine. The reason we built it is because of our focus on performance and the fact that our engine was developed specifically to allow for the strong constraints of mobiles devices. We also had to think a bit out of the box, mainly by considering the word dictionary and inverted lists as one unique data-structure instead of two independent one.

I look forward to reading your thoughts and comments on this post and continuing to explain how our engine is implemented internally, transparency is part of our DNA! 🙂

We recommend to read the other posts of this series:

* [Part 1 – indexing vs. search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-1-indexing-vs-search/)
* [Part 3 – query processing](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-3-query-processing/)
* [Part 4 – Textual Relevance](https://www.algolia.com/blog/engineering/inside-the-algolia-enginepart-4-textual-relevance/)
* [Part 5 – Highlighting, a Cornerstone of Search UX](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-5-highlighting-a-cornerstone-to-search-ux/)
* [Part 6 – Handling Synonyms the Right Way](https://www.algolia.com/blog/engineering/inside-the-engine-part-6-handling-synonyms-the-right-way/)
* [Part 7 – Better relevance via dedup at query time](https://www.algolia.com/blog/engineering/inside-the-engine-part-7-better-relevance-via-dedup-at-query-time/)
* [Part 8 – Handling Advanced Search Use Cases](https://www.algolia.com/blog/engineering/inside-the-engine-part-8-handling-advanced-search-use-cases/)

ABOUT THE AUTHOR

# Recommended Content

Powered by Algolia AI Recommendations

![](/files/live/sites/algolia-assets/files/header_section_1%20(1)%20(2).svg)
![](/files/live/sites/algolia-assets/files/footer-banner-mobile-2023.svg)

## Get the AI search that shows users what they need

[Request demo](/demorequest)

[Get started](https://dashboard.algolia.com/users/sign_up)

[

](/files/live/sites/www/files/homepage-carousel/ai-retrieval-carousel-bg-720.mp4)

![](/files/live/sites/www/files/homepage-carousel/overlay-analyst-recognition.png)

Analyst recognition

## Agentic intelligence layer powering commerce discovery

Recognized by IDC, Gartner, Forrester, and Paradigm B2B, Algolia helps enterprises turn search into a growth engine for AI-native experiences.

[Evaluate Algolia](https://www.algolia.com/demorequest?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-analyst-recognition.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-gartner-magic-quadrant.png)

Gartner 2026 Magic Quadrant for Search and Product Discovery

## A leader for the third consecutive year

Algolia is recognized as a Leader in the 2026 Gartner® Magic Quadrant™ for Search and Product Discovery as the market shifts toward AI-powered, agentic discovery.

[Read the announcement](https://www.algolia.com/about/news/algolia-recognized-as-a-leader-in-the-2026-gartner-magic-quadrant?utm_cta=homepagecarousel)

[See Algolia in action](https://www.algolia.com/demorequest?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-gartner-magic-quadrant.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-forrester-tei.png)

Forrester Total Economic Impact™

## Increased Operating Profit and Improved Efficiency

A Forrester Consulting study found Algolia delivered $3.1M NPV over three years, helping commerce teams improve relevance, automate merchandising, and grow revenue

[Download the TEI study](https://www.algolia.com/lp/algolia-forrester-tei-report-2026?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-forrester-tei.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-idc-marketscape.png)

IDC MarketScape

## Named a leader in knowledge discovery

IDC recognized Algolia as a leader in general-purpose knowledge discovery software, citing the growing role of search in AI-powered workflows and enterprise knowledge experiences

[Read the IDC announcement](https://www.algolia.com/about/news/algolia-named-a-leader-in-idc-marketscape-for-general-purpose-knowledge-discovery-software?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-idc-marketscape.png)

![](/files/live/sites/www/files/homepage-carousel/overlay-paradigm-b2b-combine.png)

PARADIGM B2B COMBINE

## Top scores across every B2B category

Algolia earned 12 medals across 12 categories in Paradigm B2B’s 2025 Enterprise Combine for Search and Discovery, with customers praising speed, transparency, analytics, and ease of use

[Learn more](https://www.algolia.com/resources/asset/report-paradigm-b2b-enterprise?utm_cta=homepagecarousel)

![](/files/live/sites/www/files/homepage-carousel/cropped-foreground-paradigm-b2b-combine.png)

✕

Hi there 👋 Need assistance? Click [here](javascript:void(0);) to allow functional cookies to launch our chat agent.

![Chat](/files/live/sites/www/files/agentforce/FacadeIcon.png)

1

✕

Thanks for visiting! 👋 I can help answer any questions about Algolia.

Hey! 👋 Got questions about pricing or plans?

Want to skip the form and book some time with our team right now?

Hey there! Would you like to book a meeting with our sales team now?

Thanks for visiting! 👋 I can help answer any questions about Algolia.