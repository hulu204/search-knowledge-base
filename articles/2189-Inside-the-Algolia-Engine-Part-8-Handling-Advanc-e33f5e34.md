---
title: 'Inside the Algolia Engine Part 8 — Handling Advanced Search Use Cases'
company: Algolia
tag: 工程相关
date: 2017-07-18
url: https://www.algolia.com/blog/engineering/inside-the-engine-part-8-handling-advanced-search-use-cases
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

# Inside the Engine Part 8: Handling Advanced Search Use Cases

Published: 
August 02, 2023

![](/files/live/sites/algolia-assets/files/blogs/bannerimages/advanced-search.webp)

[Back to all blogs](/blog/engineering)

Inside the Engine Part 8: Handling Advanced Search Use Cases

Building great search UX is one of the hardest problems in engineering, even for companies that have a large team working exclusively on search.

There are three essential hurdles to clear:  
  
1) engine performance  
2) interface intuitiveness  
3) result relevance

We’ve addressed search performance in several of the [previous articles of this series](https://www.algolia.com/blog/#q=inside%20the%20algolia%20engine&page=0&refinements=%5B%5D&numerics_refinements=%7B%7D&index_name=%22wordpress_all%22); this article will focus on the link between user interface and relevance. It will cover a wide range of use cases — from common to very specific. If users complain that they cannot find what they are searching for quickly, it is probably caused by a mix of non-intuitive interface and poor relevance; this is why it is important always to consider them together.

## Providing good relevance for the most common cases

When people are searching for something very general like a company name on LinkedIn or a person on Twitter, you should make sure you are using a notion of popularity on the results: a result with more followers has more chance to be what the users are searching for. Solving this problem has been our primary focus at Algolia from day one. We have addressed this by developing a configurable but easy to understand ranking algorithm where developers have full control of their search configuration. You can configure the popularity via [Custom Ranking](https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking/), make sure you can address a complex problem like [typosquatting](https://www.algolia.com/doc/guides/managing-results/optimize-search-results/typo-tolerance/how-to/how-to-prevent-typosquatting/), promote some [featured items](https://www.algolia.com/doc/guides/managing-results/must-do/custom-ranking/how-to/boost-or-penalize-some-records/), etc.

There is an endless way to configure the ranking, depending on the use case. We could even help Twitter solve their search issues :), as you can see in the following example:

![Twitter-search-for-Barak.png](/files/live/sites/algolia-assets/files/blogs/2025/Twitter-search-for-Barak.png)

*Searching for the official Barack Obama account on Twitter with a typo does not return the official account because of typosquatting (May 2017)*

## Providing good relevance for advanced search use cases

Solving advanced search use cases is an entirely different problem where you need to let the user refine search results via filters. We will cover in this section the three main approaches that are used to facilitate an advanced search.

### Use of faceting

Faceting is probably the most standard way to address advanced use cases. The principle is to let the user filter the results based on categories to reduce the size of the results set and remove all false positives or ambiguity. This feature is used in a wide variety of use cases, and there are a lot of different ways to present faceting results, as you can see in our [faceting documentation](https://www.algolia.com/doc/guides/managing-results/refine-results/filtering/).

![InsideTheEngine8-GIF1.gif](/files/live/sites/algolia-assets/files/blogs/2025/InsideTheEngine8-GIF1.gif)

*Faceting example: filter on genres and rating*

That said, faceting is not the perfect solution in all situations as two significant concerns can hurt your relevance:  
  
**1) It requires homogenous data**: you need to have the same categories inside all your records to have a good UX. If this is not the case, you might have duplicates in your faceting results that will lead to users not finding their record while filtering.  
  
**2) The category that the user wants is hidden**: when the number of categories to display is large, you won’t be able to show all of them, and you might miss the one that the user wants. It will be a challenge to satisfy this user, who will probably just consider your search not good enough.

### Search in faceting results

To fix the second problem—faceting not visibly proposing the category that the user is looking for—you can offer users a search for facet values. This means that the full range of categories does not even have to be displayed. Rather, you can offer the most relevant or meaningful categories, and let the user search for the rest. You can find this type of experience on LinkedIn: you can filter on locations when you are looking for a person or a company. LinkedIn proposes you to search for a particular location that is not listed in the selected facet values, which allows being very granular in your search.

The only problem that you might have on Linkedin is that this search is not contextual. You are searching inside all locations but without applying the current textual query and filters. Let’s say that you are looking for a Director of Marketing job in Buenos Aires but that there aren’t any available on LinkedIn. After you’ve searched for the job title, LinkedIn allows you to refine your search and select “Greater Buenos Aires” in the location facet value search,*although this will not return any results.*This is frustrating as you’d naturally expect not to be offered filters that will lead you nowhere.

![image4 (7).png](/files/live/sites/algolia-assets/files/blogs/2025/image4%20(7).png)

Implementing a search in faceting results while applying the contextual query is very complex, and this is probably the reason why LinkedIn preferred to implement a degraded version. A better search experience is our primary motivation at Algolia, which is why, a few months ago, we released a feature called [search for facet values](https://www.algolia.com/blog/product/search-for-facet-values/) that allows you to develop this type of experience in minutes while applying the contextual query. Here is an example of an Algolia search in the brand value in an e-commerce context.

![InsideTheEngine8-GIF2.gif](/files/live/sites/algolia-assets/files/blogs/2025/InsideTheEngine8-GIF2.gif)

*Search inside facet values: example of the brand facet*

As you can see, the search is completely contextual: all filters/refinements are related and inclusive of one another. You can find more documentation about how to use it in our [developer documentation](https://www.algolia.com/doc/guides/managing-results/refine-results/filtering/).

### Advanced query syntax

Search for facet values is very useful when you are looking to expose an advanced search to your user without burdening them with a learning curve, which is mandatory for a consumer product. If you are working on a business product that people use every day, you might want to expose them an advanced syntax inside the search box like Slack does.

![image3-454x400.png](/files/live/sites/algolia-assets/files/blogs/2025/image3-454x400.png)

![image1-492x400.png](/files/live/sites/algolia-assets/files/blogs/2025/image1-492x400.png)  
*Example of advanced syntax in a search box (Slack)*

In practice, proposing such an experience requires the same feature as searching for facet values. It is just a different way to expose the same feature. The goal of this display is to let your advanced users directly perform their advanced query via the keyword and minimize the number of steps they will need to search for their content. You can implement such interface easily with our search for facet values feature. We will release a guide soon to help you through the implementation.

## The implementation

We described in the previous sections how the search for facet values feature is useful for implementing an advanced search interface. We will now focus on the implementation to discover how this feature works internally.

I am sure you will think this type of search simply requires a change in the way we perform the query, like rewriting the query to specify which attribute we will target. But in practice, this is a significant change as we do not return records but rather highlighted facets with counts.

Let’s take a simple example of a professional social network like LinkedIn to illustrate the implementation. We will take simple records containing only four attributes. Those attributes will contain a string and will all be configured as attributes for faceting:

* The name of the person
* Their title
* The company where they work
* The location of the company

Here is an example of such a record:

|  |  |
| --- | --- |
|  | { |
|  | "Name": "Jeff Lawson", |
|  | "Title": "CEO", |
|  | "Company": "Twilio Inc", |
|  | "Location": "San Francisco" |
|  | } |

[view raw](https://gist.github.com/speedblue/ef5c454123d890f99b59a4f79f87bb40/raw/7bd0b6b81e891a8dfa17ff07c5b3161f84224258/record.json)[record.json](https://gist.github.com/speedblue/ef5c454123d890f99b59a4f79f87bb40#file-record-json)hosted with ❤ by [GitHub](https://github.com/)

At first sight, this seems like a simple problem to solve for any search engine. Let’s look at what you need:If a user performs the query ”Twilio”, they will retrieve hundreds of Twilio employees. Let’s say the user wants to sell Twilio a service in San Francisco and wants to see all the Director titles to find the closest one to their service (this is, of course, a purely fictional use case :)).

1) The profiles need to work for Twilio, so we can restrict the search on “Twilio” to the “Company” field.

2) They need to be a Director, so you can restrict the search on “Director” to the “Title” field.

3) If multiple people have the same title, you want to see the title only once, so you need to deduplicate the results. To achieve this, you can use a facet on the attribute “Title”, and display the facet values returned.

In theory, this search should provide the results that you want, but in practice, it’s more complex than that:

1) People often have multiple job titles in their profiles. And if someone has both “Director of Sales” and “Account Executive” listed as a job title, this query strategy will mention both job titles in the list (because the query relies on faceting). Do you really want to see “Account executive” in the list of results for the query “Twilio Director”?

2) Since we’re displaying facet values, and not search results, we cannot highlight the words that match the query. It’s always better to have highlighting, particularly when people type something with typos (Diretcor), or if you search at each keystroke (Direc).

3) It creates a complex UI/UX, because users will need to specify that Twilio should only be searched in Companies, instead of allowing them to search Twilio in all fields (which would also potentially improve the relevance, on top of reducing the complexity).

* There is a better solution: search directly in facet values while providing the context of the query. Let’s see how we can do this by using the “search for facet values” feature on the facet “Title”:

|  |  |
| --- | --- |
|  | index.searchForFacetValues({ |
|  | query: "twilio", |
|  | facetName: "Title", |
|  | facetQuery: "director" |
|  | }) |

[view raw](https://gist.github.com/IvanaSays/4d7094d9b8b5b5888957f8c323436158/raw/868556b35f30037cc9d2babfa8e5db00f2ba090f/query_example.js)[query\_example.js](https://gist.github.com/IvanaSays/4d7094d9b8b5b5888957f8c323436158#file-query_example-js)hosted with ❤ by [GitHub](https://github.com/)

This query will be applied in two steps:

* First, it will retrieve only the results containing the word Twilio in one of the searchable attributes. From this list, it will extract all of the values for the facet Title (i.e., all of the jobs titles listed in every profile that contain the word Twilio).
* Then, in this filtered list of job titles, it’ll search for the ones that contain “Director”. This allows us to only retrieve relevant results, by using all of the regular search features (typo-tolerance, highlighting, prefix-search, ranking…). The result is the list of all the Twilio job titles containing “Director”, deduplicated and ordered by count — exactly what we were looking for.

In other words, this feature requires a two-step process that is only doable efficiently when implemented at the heart of the engine.

## Evolutions

The release of this feature enabled all our existing users to build a great advanced search interface quickly. We, of course, do not plan to stop here and are already thinking about the next evolutions of the feature. For the moment, the ranking of results is pretty basic and is only using the frequency of facets, which means you can have a result with typo first. We plan to improve the feature by providing a different way to rank the results.

If you want to know more about the internal aspect of the Algolia engine, we recommend reading the other posts in this series:

* [Part 1—Indexing vs. Search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-1-indexing-vs-search/)
* [Part 2—The Indexing Challenge of Instant Search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/)
* [Part 3—Query Processing](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-3-query-processing/)
* [Part 4—Textual Relevance](https://www.algolia.com/blog/engineering/inside-the-algolia-enginepart-4-textual-relevance/)
* [Part 5—Highlighting, a Cornerstone of Search UX](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-5-highlighting-a-cornerstone-to-search-ux/)
* [Part 6—Handling Synonyms the Right Way](https://www.algolia.com/blog/engineering/inside-the-engine-part-6-handling-synonyms-the-right-way/)
* [Part 7—Better Relevance via Dedup at Query Time](https://www.algolia.com/blog/engineering/inside-the-engine-part-7-better-relevance-via-dedup-at-query-time/)

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