---
title: 'Inside the Algolia Engine Part 1 — Indexing vs. Search'
company: Algolia
tag: 索引构建
date: 2016-03-29
url: https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-1-indexing-vs-search
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

# Inside the Algolia Engine Part 1 — Indexing vs. Search

Published: 
January 22, 2024

![](/files/live/sites/algolia-assets/files/blogs/bannerimages/inside-the-algolia-engine-part-1-indexing-vs-search.webp)

[Back to all blogs](/blog/engineering)

Inside the Algolia Engine Part 1 — Indexing vs. Search

In previous blog posts, we have discussed the [high-level architecture](https://highscalability.com/blog/2015/3/9/the-architecture-of-algolias-distributed-search-network.html) of our search engine and our [worldwide distributed infrastructure](https://medium.com/@algolia/algolia-s-fury-road-to-a-worldwide-api-c1536c46f3a5). Now we would like to dive a little deeper into the Algolia search engine to explain why we implemented it from scratch instead of building upon an existing open-source engine.

We have many different reasons for doing so and want to provide ample context for each, so we have split “Inside the Algolia engine” into several posts. As you learn more about our search engine, please let us know if there’s anything you would like us to address in future posts.

If you have ever worked on a search engine with significant traffic and indexing, you are undoubtedly familiar with the problem of trying to fine-tune your indexing to avoid negatively affecting search performance. Part one of this series will focus on one of the quintessential problems with search engines—the impact of indexing on search queries—and our approach to solving it.

### **Why does indexing impact search performance?**

Indexing impacts search performance because indexing and search share two critical resources—CPU and Disk. More specifically:

1. Both indexing and search are very**CPU intensive** and compete for available resources. Imagine if you experience a sudden spike in search queries while simultaneously needing to run a large number of indexing operations. You run a significant risk of not having enough CPU to handle both.
2. Both indexing and search perform **a lot of disk I/Os**. Search often performs a large number of read operations on the disk because the data is not always stored in memory, and indexing performs a large number of both read and write operations to the disk. There is also a battle for disk resources, even on high-end SSD drives.

The obvious way to solve this problem is to try to reduce or remove the conflicts of access to the shared resources.

### **Classical approaches to solving this issue**

There are a lot of different approaches to dealing with this issue, and the majority fall into one of the following three categories:

1. **Update the data in batches** during a regularly scheduled, controlled period of low traffic. This approach works well when your users are located in a specific country but doesn’t really work if your users are distributed worldwide. More importantly, this approach prevents frequent updating of the index, which means that searches will often be performed on outdated data.
2. **Use** **different machines for indexing and search**. In this approach, a specific set of machines is used for indexing, and the generated files are copied onto the search machines. This is pretty complex to set up but has the added benefit of removing the indexing CPU load from the search machine. Unfortunately, this does not solve the problem of shared I/O, and your indexing will be bound by the network, especially when a compaction is triggered (an operation performed on a regular basis by the search engine to aggregate all incremental updates, also called optimization). The main drawback to this approach is the substantial impact on indexing speed as a sizable delay is introduced between when an update is made and when that update is actually available to be searched.
3. **Throttle the indexing speed** via a priority queue. The goal of this approach is to limit the number of indexing operations in order to minimize the impact indexing has on search performance. Throttling introduces a delay in indexing speed that is difficult to measure, especially when coupled with a priority. The compaction described in the previous paragraph can also worsen the delay by causing a cumulative slow down effect on the indexing. This approach slows down indexing while also making it very difficult to avoid impacting search performance, especially during the compaction phases.

While complex to implement, the second approach of using different machines for indexing and search is a good solution if indexing performance is not crucial to you. The other two approaches only partially solve the issue as search remains impacted. Realistically, none of these approaches appropriately solves the problem of indexing affecting search performance because either indexing performance, search performance or both end up suffering.

### **How we solved the race for CPU resources**

By splitting the indexing and search into different application processes!

At Algolia, indexing and search are divided into two different application processes with different scheduling priorities. Indexing has a lower CPU priority than search based on a higher nice level (Nice is a tool for modifying CPU priority on Unix-like operating systems). If there is not enough CPU to serve both indexing and search, priority is given to search queries and indexing is slowed down. You can keep your hardware architecture designed to handle both by simply slowing down indexing in the case of a big spike in search queries.

As is the case with using different machines for indexing and search, separating them into different application processes introduces some complexity; for example, the publication of new data for search becomes a multi-process commit.

This problem is pretty common and can easily be solved with the following sequence:

1. When the indexing process receives new jobs, build a new incremental update of the index.
2. Commit the incremental update to the disk.
3. Notify all search processes of the data changes to the disk.
4. Redirect new queries to the new data-structure. Currently processing queries remain served by the old data-structure.
5. When no more queries are processing on the old data-structure, erase it from the disk.

This approach solves the problem of needing to share and prioritize CPU resources between indexing and search but is unfortunately something that most search engines on the market today cannot implement because indexing and search are executed in the same process.

### **How we solved the race for disk resources**

The race for disk resources is a bit more complex to solve. First, we configured our kernel I/O scheduler to assign different priorities to read and write operations via the custom expiration timeout settings within the Linux deadline scheduler. (Read operations expire after 100ms, write operations expire after 10s). Those settings gave us a nudge in the right direction, but this is still far from perfect because the indexing process performs a lot of read operations.

The best way to address the contention for finite disk resources is to make sure the search process does not perform any disk operations, which means that all the data needs to remain in memory. This may seem obvious, but it is the only way to ensure the speed of your search engine is not impacted by indexing operations. It may also seem a bit crazy in terms of costs (having to buy additional memory), but the allocated memory can actually handle the vast majority of use cases without issue. We of course have some users that want to optimize costs for huge amounts of data, but this makes up a very small percentage of our users (less than 1%) and is addressed on an individual basis.

### **Default to fast and reliable**

Everything at Algolia is designed with speed and reliability in mind—your data is stored in memory and synced on a high-end SSD and at least three different servers for high availability. Our ultimate goal is to remove all of the pains associated with building a great search feature, and solving the dependency between indexing and search was a very important step in getting there!

We take a lot of pride in building the best possible product for our customers and hope this post gives you some insight into the inner workings of our engine and how we got where we are today. As always, we would love your feedback. Definitely leave us a comment if you have any questions or ideas for the next blog in the series.

We recommend to read the other posts of this series:

* [Part 2 – the indexing challenge of instant search](https://www.algolia.com/blog/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search)
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