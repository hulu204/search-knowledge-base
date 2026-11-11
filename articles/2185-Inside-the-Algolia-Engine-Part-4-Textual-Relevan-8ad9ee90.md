---
title: 'Inside the Algolia Engine Part 4 — Textual Relevance'
company: Algolia
tag: 搜索相关性
date: 2016-07-07
url: https://www.algolia.com/blog/engineering/inside-the-algolia-enginepart-4-textual-relevance
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

# Inside the Algolia Engine Part 4 — Textual Relevance

Published: 
August 02, 2023

![](/files/live/sites/algolia-assets/files/blogs/bannerimages/inside-the-algolia-enginepart.webp)

[Back to all blogs](/blog/engineering)

Inside the Algolia Engine Part 4 — Textual Relevance

We’ve changed how we search a lot over the last decade. For example, we used to begin every search by pressing Enter. Now the Enter key is no longer necessary – results appear as you type, instantly.

*What* people search has also changed: today’s search engines are used for much more than just web sites and documents—they’re also used to find specific items like people, places and products.

The Algolia engine was designed with both of these trends in mind. Algolia’s sweet spot is providing instant, relevant access to millions of small, structured records (and now from [anywhere in the world](https://www.algolia.com/users/sign_in)). In this blog post, we’ll talk about how the Algolia engine computes *textual relevance* and why it works well for exactly these kinds of records. By textual relevance, we mean the letter and word-based aspect of ranking query results. Textual relevance does not include business relevance, which is used to provide a [custom ranking](https://www.algolia.com/doc/guides/managing-results/relevance-overview/) based on non-textual information like price, number of followers or number of sales.

In a previous post we discussed [how our ranking formula works](https://www.algolia.com/blog/engineering/how-algolia-tackled-the-relevance-problem-of-search-engines/), specifically how it uses a tie-breaking algorithm to rank each component of textual relevance one-by-one. In this post, we’ll look at each of the five individual components it uses in detail: *number of typos, number of words, proximity of words, importance of attributes*and *exactness*.

## 1. The five components of textual relevance

Each of these components address a unique relevance challenge while also playing their part in the global relevance calculation.

### 1.1 Number of typos

The *number of typos* criterion is the number of typos in the query when compared with text in the record. This criterion allows you to rank results containing typos below results with the correct spelling. For example, in a search for*“Geox CEO”*, you would prefer to have the *“Geox”*result (a typo-free match) displayed before *“Gox”* (a 1-letter-off typo). This example has a twist—”*Gox”* is not actually a typo in the usual sense (it’s a correctly spelled proper noun) but it’s still possible that a user could have mistyped *“Geox”* when searching for it.

```
1st record:
Title: "Geox SpA: CEO and Executive"
```

```
2nd record:
Title: "Mt. Gox CEO Resigns From Bitcoin Foundation"
```

### 1.2 Number of words

The *number of words* criterion is the number of query words found in the record. This criterion applies when the query is performed with *all words optional* (a.k.a. an “OR query”), a technique commonly used to avoid displaying no results. Here’s a simple example. If you search for *“supreme court apple”* you would prefer to have the first record before the second one as it contains all 3 of the words in the query.

```
1st record:
Title: "Supreme Court turns away Apple appeal in e-books antitrust case"
```

```
2nd record:
Title: "Supreme Court upholds Obama’s health-law subsidies"
```

### 1.3 Proximity of words

The *proximity of words* criterion is the distance between the matched words in the result. It’s used to rank records where the query words are close to each other before records where the words are farther apart. In the example below, you can see two different results for the query *“Michael Jackson”*. In the first record, the proximity criterion is 1 – the terms *‘Michael’* and *‘Jackson’* are right next to each other. In the second record, the proximity criterion is 7 because there are 6 words between the matching terms. A lower value is better, i.e. records with a lower proximity value will be ranked about records with a higher value.

```
1st record:
Title: "Michael Jackson songs radiate through Spike Lee's neighborhood celebration saluting the King of Pop"
```

```
2nd record:
Title: "Michael K. Williams found inspiration in Janet Jackson"
```

### 1.4 Importance of attributes

The *importance of attributes*criterion identifies the most important matching attribute(s) of the record. Since records can contain more than one attribute, it’s not uncommon for one query to match multiple attributes of the same record or different attributes of different records. However, a match of one attribute might be more important than another when it comes to ranking, and that’s precisely why we have the attribute criterion. An example is shown below. Given a query for *“Netflix”*in a collection of articles, you’d want the *title* attribute match to carry more weight than the *description* attribute, hence the title-matching record is displayed first.

```
1st record:

Title: "Netflix is making movies shunned by studios"

Description: "As the company moves into feature films with the release of “Beasts of No Nation” on its streaming service and simultaneously in a small number of theaters, it is creating the type of movies that studios no longer make."
```

```
2nd record:

Title: "The new documentary ‘What Happened, Miss Simone?’ takes a look at the life and legacy of Nina Simone"

Description:  "The new Netflix documentary ‘What Happened, Miss Simone?’ takes a look at the life and legacy of the talented Nina Simone."
```

### 1.5 Exactness

The *exactness*criterion is the number of words that are matched **exactly**. This criterion is very important for building quality instant (search-as-you-type) experiences because it’s important to display full-word matches before prefix matches. See the example below. If you search for *“Prince”*, you want the exact word match to appear before the match where “***Prince****”* is being considered as a prefix of “***Prince****ss”*.

```
1st record:
Title: "Reflections on Prince: My classmate, the rock star"
```

```
2nd record:
Title: "Spain’s Princess Cristina goes on trial"
```

## 2. How the criteria are computed

We’ve just seen what each criterion does and how it can be used to influence the ranking of search results. Next, let’s look at how the five criteria are computed and what we’ve done to make their computation efficient.

### 2.1 Computing the number of typos

In our previous post about[Query Processing](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-3-query-processing/), we explained how alternative terms are added to queries. For each alternative term, we also have an associated number of typo criteria (which corresponds to the edit-distance). This value of the overall typo ranking criterion is the sum of all typos used to find the match. For example, if the record is found via 2 words having 1 typo each, the typo criterion value will be 2.

It’s a very good practice to have this criterion at the top of the ranking formula. However, there is one exception: **typosquatting**. If you operate a service with a lot of user-generated content, you might already be familiar with this problem. Let’s take Twitter as an example. If you search for *“BarakObama”* on Twitter (note the typo), you would want the official *@BarackObama* account to appear before the typosquatting account *@BarakObama*. However, today it does not (as of June 2016). Typosquatting is a complex and difficult challenge.

One way that we recommend to handle typosquatting is to add an *isPopular* boolean attribute to the record of popular accounts and then to put it in the ranking formula before the typo criterion. On Twitter, *isPopular* could be set to true if the account is verified. This approach ensures that the official account with a typo will be displayed before any typosquatting accounts, no need to hide any results. For this approach to work well, the number of records with *isPopular* set to true should be a relatively small percentage of the dataset (less than 1%).

##### 2.1.1 Typo tolerance tuning

The Algolia engine provides several different ways to tune typo tolerance for specific words and attributes:

* *minWordSizefor1Typo* and *minWordSizefor2Typos*: Specify the minimum number of characters in a query word before it can be considered as a 1 or 2 typo match.
* *allowTyposOnNumericTokens*: Specify if typo tolerance is active on numeric tokens (numbers) present in the query.
* *disableTypoToleranceOnWords*: Specify a list of words for which typo tolerance will be disabled.
* *disableTypoToleranceOnAttributes*: Specify a list of attributes for which typo tolerance will be disabled.
* *Alternative corrections*: Specify a set of alternative corrections with the associated number of typos.
* *advancedSyntax*: Add quotes around query words to disable typo tolerance on them.

### 2.2 Computing the number of words

Computing this criterion is relatively easy, it’s just the number of words from the query that are present in the record. Each word might be matched exactly or matched by any alternative form (a typo, a prefix, a synonym, etc.).

The position of the words criterion in the ranking is important and will impact results. For example, the query *“iphone case catalist”* with all terms as optional will have two different ways to match the record “*Catalyst Waterproof Case for iPhone 6/6S Orange*“:

1. *If****words****is before****typo****in the ranking formula:* The ranking will be set to **words=3** and **typo=1** as matching more words is important to the ranking (even if *Catalyst* is found via a typo).
2. *If****typo****is before****words****in the ranking formula:* The ranking will be set to **words=2** and **typo=0** as less typos are more important to the ranking (in this case it’s better to not match the *Catalyst* term and therefore not introduce a typo).

##### 2.2.1 The removeWordsIfNoResults parameter

Because of situations like this, we usually recommend against performing queries with all terms optional. Instead, we recommend using a[specific query parameter](https://www.algolia.com/doc/rest-api/search/) that we’ve added to the API to help with these types of situations. The *removeWordsIfNoResults* parameter instructs the engine to first test the query with all terms as mandatory, then progressively retry it with more and more words as optional until there are results. This parameter gives us the best of both worlds (predictable behavior and always showing results) and also does not pollute faceting results. When all terms are optional there is a large increase in the number of matched records, as only one matching word is required to add the record to a facet. For example, in a query for “iphone black case”, any *black* item will be matched which will have a big impact on the quality of the faceting.

### 2.3 Computing the proximity of words

The proximity criterion’s value is the sum of the proximity of all pairs of words that are next to each other in the query. Computing the proximity of *“iphone release date”* is done like this: *proximity(“iphone”, “release”) + proximity(“release”, “date”)*.

The engine stores word positions at indexing time in order to efficiently compute proximity at query time. We define the distance between two words A and B as the *shortest* distance between any A and B in the record (A and B may appear more than once). We increase the distance by 1 if the match with the shortest distance is not in the queried order.

The computed proximity between two words is capped at **8**. If the words “apple” and “iphone” are separated by a distance of 10 or 100 words, the distance will still be 8. The goal is to avoid creating different proximity values for words that are not used in remotely the same context. In practice, 8 words is a sizeable distance between any 2 words, even when it’s mostly common words between them. Capping the maximum proximity has two other advantages:

1. It helps our tie-breaking algorithm. A maximum distance of 8 means that we don’t know if a distance between words of 10 is better than 100, and usually we don’t want to (it’s just noise). Capping the proximity at a small number prevents introducing false positives into the relevance calculation. More importantly, it lets the other criteria in the ranking formula take over when proximity values are not meaningfully differentiated.
2. It enables a lot of optimizations on the storage and computation side, as we will see.

##### 2.3.1 How word positions are stored

As we index a document, we assign an integer position to each occurrence of each word. For example the string *“Fast and Furious”* would be indexed as:

* *“Fast”* at position 0
* *“and”* at position 1
* *“Furious”* at position 2

Additionally, we assign positions to some word prefixes as described in our[blog post about indexing prefixes](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/).

The position is also used to efficiently store associated information:

* We use a single value to store the position of each word in the text and which attribute it came from. We keep the position of the first 1000 words inside each attribute and associate an number to each attribute (the first attribute will have positions 0-999, the second attribute will have positions 1000-1999, etc.)
* For multi-valued string attributes, we need to ensure that the last word of a string isn’t considered to be next to the first word of the next string. To do that, we increment the first position of each string by 8 each time we move from one string to another. For example if a record contains the following *“Actors”* attribute, we will store the word “Diesel” with a position of 1 and the word “Paul” with a position of 10 (+8 compared to the value in the same string). This will generate a proximity of 8 if you type “Diesel Paul”, which is the highest value for proximity.

```
{
 "Actors": [
   "Vin Diesel",
   "Paul Walker"
 ]
}
```

##### 2.3.2 Bonus challenge: multi-word alternatives

Computing a proximity distance can be very complex when you support alternative word matching, e.g. synonyms. If you have a synonym that defines “NYC” = “New York City” = “New York” = “NY”, you would like to consider a record that contains “NYC” as strictly identical to a record that contains “New York”. We solve this tricky problem by rewriting all word positions at query time.

Time for an example. Let’s say that you have two different articles that you want to be searchable via a query for the “New York subway”. You would like the proximity distance calculation to be the same between them. Here are the article titles:

1. “[Why New York Subway Lines Are Missing Countdown Clocks”](https://www.theatlantic.com/technology/archive/2015/11/why-dont-we-know-where-all-the-trains-are/415152/#hn?single_page=true)
2. “NYC subway math”

When this query is run, the first record will be matched via three words (“*new*” at position 1, “*york*” at position 2 and “*subway*” at position 3) and the second record will be matched via two words (“*nyc*” at position 0 and “*subway*” at position 1).

In order to avoid this inconsistency, we rewrite positions using a multi-word expansion. For the *“NYC subway”* query, we apply the following transformation:

* *“Nyc” at position 0 became:*
  + *Virtually “new”*at position 0
  + Virtually “york” at position 1
* *“subway”* *at position 1 became:*
  + “Subway” at position 2 because we introduced “york” word at position 1.

After the transformation, we have exactly the same proximity measure between the two records. This rewriting is entirely cumulative. For the “New York” query, if a record contains “NYC” at positions 5 and 15, it means that all original positions greater than 15 will be increased by 2 and all original positions between 6 and 15 will be increased by 1.  
![MultiWordSynonyms.png](/files/live/sites/algolia-assets/files/blogs/2025/MultiWordSynonyms.png)

##### 2.3.3 Attribute-aware proximity

When computing the proximity score, we don’t want to be misled when different parts of the search expression are found in different attributes of the record.

Say you’re looking for *“soup of the day”* and you have a record with *“soup”*, *“of the”* and *“the day”* separately in three different attributes. In this case we do not want to compute a total distance of 10 (*distance(soup, of)=8* + *distance(of, the)=1* + *distance(the, day)=1)* because it would mean *“of the day”* are close together, which is not the case. Instead, we want a total distance of 17 (*distance(soup, of)=8* + *distance(of, the)=1* + *distance(the, day)=8)*. The distance of 8 between *“the”* and *“day”* tells us that *“day”* was found in a different block than *“of the”*. We use a dynamic programing algorithm to do this computation efficiently with a cost of *O(N)*(N being the number of matched positions).

##### 2.3.4 Proximity computation tuning

The *minProximity* index setting allows to change the minimum proximity to something that fits your data better. If you set *minProximity=2*, it would mean that the query *“New York City Subway”* will have the same proximity score whether the record contains *“New York City Subway”* or *“New York City’s newest subway”*. The distance would normally be 1+1+1 for the first record and 1+1+2 for the second, but setting *minProximity=2* means that all pairs of words with a distance less than or equal to *minProximity* are counted for 1. In this example, both records are given a proximity criterion score of 3.

### 2.4 Computing the most important attributes

As a reminder, the attribute criterion lets us say that a query match in some attributes is more important than others.

Each attribute is indexed as *ordered* or *unordered* (this is configured in the index settings). Indexing an attribute as *ordered* means that the position of the best matched word inside the attribute is taken into account during ranking. So earlier words will matter more. Indexing as *unordered* means that the position within the attribute is not taken into account. Word position is not important.

An example—if you index the *title* attribute as *ordered* and *description* attribute as *unordered*, the query *“Netflix”* will return the following 2 records in the order displayed.

```
1st record:

Title: “Cable fights Netflix to feed 'binge' TV viewers"

attribute=2: Netflix is the third word of the title attribute (title attribute is indexed with positions 0 to 999).
```

```
2nd record:

Title: "Deborah Ann Woll Previews ‘Daredevil’ Season Two",

Description: "Deborah Ann Woll, who co-stars as Karen Page on the Netflix superhero series “Daredevil”

attribute=1000: Netflix is found in the description attribute (the description attribute is indexed with positions 1000 to 1999 because it is the second indexed attribute). The attribute criterion is set to 1000 because the description attribute is indexed as unordered.
```

##### 2.4.1 When proximity is before attribute in the ranking

There are two strategies to compute best-matched attributes and they depend on the relative position of *proximity* and *attribute* criteria in the ranking formula. Let’s illustrate them by using the query “VMware CEO” to retrieve the following record:

```
Title: "VMware's chief drives three-pronged focus for virtualization software maker",

Description: "VMware CEO Patrick Gelsinger, in an interview, lays out the software maker's future in software-defined data centers, cloud computing and managing user devices like PCs and smartphones."
```

* If *proximity* is before *attribute* in the ranking formula, we first find the location with the best proximity in the record and we then compute the best attribute on this location. On the record below, the query *“VMware CEO”* will have an attribute criterion of 1000 as the best proximity is found in the description attribute instead of the title attribute.
* If *attribute* is before *proximity*, the best-matched attribute will be decided by the position of the best-matched word in the record. In this case, the query *“VMware CEO”* will have an attribute criterion of 0 as the best word is matched in the *title* attribute.

We recommend keeping the proximity criterion before attribute criterion. Proximity usually leads to a better identification of the best-matched attribute.

### 2.5 Computation of the exactness criterion

The *exactness* criterion represents the number of words that match entirely, not one as a prefix of another. This criterion works well when the query contains several words but the one-word case requires a modified approach. In an instant search use case, if a user has typed “was”, there is a greater chance that he or she might be in the middle of typing a search for *“Washington”* and not just stopping at the verb *“was”*. Displaying *“was”* before *“Washington”* in the results at that moment would not be ideal.

We have implemented three different ways to compute the exactness criterion for a single word query, each specified via the *exactOnSingleWordQuery* parameter:

* **exactOnSingleWordQuery=none**: The exact criteria is set to 0 for all one-word queries.
* **exactOnSingleWordQuery=attribute**: All records that have an attribute string exactly equal to the query will have exact=1. This option is the default as it works well for databases that contain names, brands, companies, etc.
* **exactOnSingleWordQuery=word**: All records will have exact set to 1 if there is a word that matches exactly and is not in our stop word dictionary (see the [*removeStopWords*](https://www.algolia.com/doc/rest-api/search/) option for more information). For the query “*prince*”, a record with “*prince*” will have exact=1 and a record with “*princess*” will have exact=0. For a query “was”, both records containing “was” and “Washington” will have exact=0 because “was” is in the stop word dictionary.

There is unfortunately no magic option that works well with all use cases, which is why we introduced the *exactOnSingleWordQuery* parameter. We recommend using *exactOnSingleWordQuery=attribute* if you have a database that contains lots of one-word entries like brand names, account names, movies, etc. We recommend using *exactOnSingleWordQuery=word*when you have content like titles that have a low probability of matching an entry using only one word.

### 2.6 Designed for small records

The five components of textual relevance we’ve discussed are uniquely designed for small, structured records. A few of them require some fairly complex processing, like the query-time rewriting of word positions for multi-word alternatives, but we think that having an approximation-free, exact value computation is worth it.

If you don’t automatically have small, structured records—i.e. if you’re starting with documents or long blocks of text—we recommended splitting them into multiple, shorter records. One record per paragraph is a good rule of thumb. This is the approach used by our [DocSearch](https://community.algolia.com/docsearch/) project, which crawls web pages containing technical documentation and can generate many records per page. DocSearch is now powering the search of 150+ open source projects, so there are lots of places you can [try it out](https://github.com/algolia/docsearch-configs).

We’re constantly seeking more ways to customize relevance for advanced use cases. Some of the parameters presented in this post have been added to the API recently and several new parameters are currently being beta tested.

A few weeks ago we were given a challenge: to index millions of articles of a popular news website and provide relevant results about the artist Prince’s death, even for queries with typos like “*Prinse*“. The query “*Prinse*” matches article with “Prince” in the title (typo=1, words=1, proximity=0, attribute=0, exact=0) but the results were being displayed below other articles about *“Sharon Prinsen”* (typo=0, words=1, proximity=0, attribute=1000, exact=0) because it matches a prefix without typo. To solve this issue, we introduced a new option to consider all prefix matches as a typo: now all articles with *“Prince”* in the title will be served first (typo=1, words=1, proximity=0, attribute=0, exact=0) and articles mentioning *“Sharon Prinsen”* will come after (typo=1, words=1, proximity=0, attribut=1000, exact=0). With this improvement, we were able to address the relevance problem of prefixes while maintaining a high quality instant search experience.

Relevance is our passion and we love to be challenged. Feel free to contact us if you have a complex use case with relevance issues, we’d be happy to help!

We recommend to read the other posts of this series:

* [Part 1 – indexing vs. search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-1-indexing-vs-search/)
* [Part 2 – the indexing challenge of instant search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/)
* [Part 3 – query processing](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-3-query-processing/)
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