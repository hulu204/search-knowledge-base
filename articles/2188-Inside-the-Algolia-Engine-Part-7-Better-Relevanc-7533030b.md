---
title: 'Inside the Algolia Engine Part 7 — Better Relevance via Dedup at Query Time'
company: Algolia
tag: 搜索相关性
date: 2017-01-16
url: https://www.algolia.com/blog/engineering/inside-the-engine-part-7-better-relevance-via-dedup-at-query-time
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

# Inside the engine part 7 – Better relevance via dedup at query time

Published: 
August 02, 2023

![](/files/live/sites/algolia-assets/files/blogs/bannerimages/relevance.webp)

[Back to all blogs](/blog/engineering)

Inside the engine part 7 – Better relevance via dedup at query time

One of the most unique and most-used features of Algolia is the [Distinct feature](https://www.algolia.com/doc/guides/managing-results/refine-results/grouping/): it enables developers to deduplicate records on-the-fly at query time based on one specific attribute. We introduced this feature three years ago, opening up a broad range of new use cases like the [deduplication of product variants](https://www.algolia.com/doc/guides/managing-results/refine-results/grouping/) – a must-have for any eCommerce search. It has also considerably changed the way we recommend handling big documents like PDFs or web pages (we recommend splitting each document into several records).

This post highlights the advantages of this feature and the different challenges it represents in term of implementation.

## Document search: state of the art and limitations

Searching inside large documents is probably the oldest challenge of information retrieval. It was inspired from the index at the end of books and gave the birth to an entire sub-genre of statistics. Among those methods, [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) and [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) are the two most popular. They are very effective for ranking documents, but they don’t handle false positives well – they push them to the bottom of the results.

To illustrate this problem, you can perform the “states programming” query on Google and Wikipedia. According to [Google Trends](https://www.google.com/trends/explore?q=states%20programming,rust%20programming%20language), this query is as popular as the Rust programming language and seems to correspond to developers that search how to develop an algorithm with a state. The same query on Wikipedia is unfortunately not very relevant! The first issue probably comes from a stemming algorithm or a synonym that considers “program” as the same than “programming.” In Algolia, you can have an expansion of singular/plural without polluting results with stemming by using the [ignorePlurals feature](https://www.algolia.com/doc/api-reference/api-parameters/), which is based on a linguistic lemmatizer.

That said, even if you scroll through the first 1000 hits of Wikipedia search, you won’t find the article which appears first in Google. There are hundreds of articles that contain both the word “states” and “programming.” Even the “United States” page contains both terms and one is in the title! In this case, tf-idf and BM25 are not the most useful ranking criteria. The position of the two query terms in the document is more important, in addition to their relative distance (finding them close together is always better).

![StatesProgrammingQuery.png](/files/live/sites/algolia-assets/files/blogs/2025/StatesProgrammingQuery.png)

States programming query on Google and Wikipedia

## Why do we split large documents

One of the best ways to avoid such relevance problems is to split big pages into several records – for example, you could create one record per section of the Wikipedia page. If a Wikipedia article were to have 4 main sections, we could create 4 different records, with the same article title, but different body content.

For example, instead of the following big record with the four sections embedded:

|  |  |
| --- | --- |
|  | { |
|  | "title": "This is the title", |
|  | "summary": "article summary", |
|  | "sections": [ |
|  | { |
|  | "title": "first section", |
|  | "text": "..." |
|  | }, |
|  | { |
|  | "title": "second section", |
|  | "text": "..." |
|  | }, |
|  | { |
|  | "title": "third section", |
|  | "text": "..." |
|  | }, |
|  | { |
|  | "title": "fourth section", |
|  | "text": "..." |
|  | } |
|  | ] |
|  | } |

[view raw](https://gist.github.com/speedblue/9a823e0a38949895bd5f58d1caa156c3/raw/1465359bf5190dc7fcba7d98813f7e0f0dda3c3c/articleWithSectionsEmbedded.json)[articleWithSectionsEmbedded.json](https://gist.github.com/speedblue/9a823e0a38949895bd5f58d1caa156c3#file-articlewithsectionsembedded-json)hosted with ❤ by [GitHub](https://github.com/)

We could have 5 different records, one for the main one and one per section. All those records will share the same source attribute that we will use to indicate the engine that they are all component of the same article:

|  |  |
| --- | --- |
|  | [ |
|  | { |
|  | "title": "This is the title", |
|  | "summary": "article summary", |
|  | "source": "articleName" |
|  | }, |
|  | { |
|  | "sectionTitle": "first section", |
|  | "text": "...", |
|  | "source": "articleName" |
|  | }, |
|  | { |
|  | "sectionTitle": "second section", |
|  | "text": "...", |
|  | "source": "articleName" |
|  | }, |
|  | { |
|  | "sectionTitle": "third section", |
|  | "text": "...", |
|  | "source": "articleName" |
|  | }, |
|  | { |
|  | "sectionTitle": "fourth section", |
|  | "text": "...", |
|  | "source": "articleName" |
|  | } |
|  | ] |

[view raw](https://gist.github.com/speedblue/a38380a3573136a70f3863e71dc38282/raw/74af63b8dac35913cd7b6e3233541b64f9183568/articleWithSeparatedSections.json)[articleWithSeparatedSections.json](https://gist.github.com/speedblue/a38380a3573136a70f3863e71dc38282#file-articlewithseparatedsections-json)hosted with ❤ by [GitHub](https://github.com/)

We can use this same approach for technical documentation, as there are often just a few long pages in order to improve the developer experience: scrolling is better than loading new pages! This is exactly why we have decided to split pages into several records in our [DocSearch](https://community.algolia.com/docsearch/) project; you can learn more about our approach in this [blog post](https://www.algolia.com/blog/engineering/how-to-build-a-helpful-search-for-technical-documentation-the-laravel-example/).

It might sound counter-intuitive, but the problem is even more visible when your data set is smaller! While the problem is only visible on well-selected queries on the Wikipedia use case, it becomes very apparent when you search inside a website with less content. You have a high probability of having false positives in your search that will frustrate for your users.

## The need for deduplication

Splitting a page into several records is usually easy as you can use the formatting as a way to split. The problem with several records per document is that you will introduce duplicates in your search results. For example, all paragraphs of the United States Wikipedia article will match for the “United States” query. In this case, you would like to keep only the best match and avoid duplicates in the search results.

This is where the distinct feature comes to play! You just have to introduce one attribute with the same value for all records of the same source (typically an ID of the document) and declare it as the [*attributeForDistinct*](https://www.algolia.com/doc/api-reference/api-parameters/) in your index setting. At query time, only the best match for each value of the attribute for distinct will be kept, all the other records will be removed to avoid any duplicate.

If we split the United States Wikipedia article by section and subsections, it would generate 39 records. You can find the first four records on this gist:

|  |  |
| --- | --- |
|  |  |
|  | [{ |
|  | "title": "United States", |
|  | "synonyms": ["United States of America", "America", "US", "U.S.", "USA", "U.S.A.", "the landmass encompassing North America and South America America", "Americas"], |
|  | "text": "The United States of America (USA), commonly referred to as the United States (U.S.) or America, is a federal republic composed of 50 states, a federal district, five major self-governing territories, and various possessions. Forty-eight of the fifty states and the federal district are contiguous and located in North America between Canada and Mexico. The state of Alaska is in the far northwestern corner of North America, with a land border to the east with Canada and separated by the Bering Strait from Russia. The state of Hawaii is an archipelago in the mid-Pacific. The territories are scattered about the Pacific Ocean and the Caribbean Sea. Nine time zones are covered. The geography, climate and wildlife of the country are extremely diverse.\nAt 3.8million square miles (9.8million km2) and with over 324 million people, the United States is the world's fourth-largest country by total area (and fourth-largest by land area) and the third-most populous. It is one of the world's most ethnically diverse and multicultural nations, and is home to the world's largest immigrant population. Urbanization climbed to over 80% in 2010 and leads to growing megaregions. The country's capital is Washington, D.C. and its largest city is New York City; the other major metropolitan areas, all with around five million or more inhabitants, are Los Angeles, Chicago, San Francisco, Boston, Dallas, Philadelphia, Houston, Miami, and Atlanta.\nPaleo-Indians migrated from Asia to the North American mainland at least 15,000 years ago. European colonization began in the 16th century. The United States emerged from 13 British colonies along the East Coast. Numerous disputes between Great Britain and the colonies in the aftermath of the Seven Years' War led to the American Revolution, which began in 1775. On July 4, 1776, as the colonies were fighting Great Britain in the American Revolutionary War, delegates from the 13 colonies unanimously adopted the Declaration of Independence. The war ended in 1783 with recognition of the independence of the United States by Great Britain, and was the first successful war of independence against a European colonial empire. The current constitution was adopted in 1788, after the Articles of Confederation, adopted in 1781, were felt to have provided inadequate federal powers. The first ten amendments, collectively named the Bill of Rights, were ratified in 1791 and designed to guarantee many fundamental civil liberties.\nThe United States embarked on a vigorous expansion across North America throughout the 19th century, displacing American Indian tribes, acquiring new territories, and gradually admitting new states until it spanned the continent by 1848. During the second half of the 19th century, the American Civil War led to the end of legal slavery in the country. By the end of that century, the United States extended into the Pacific Ocean, and its economy, driven in large part by the Industrial Revolution, began to soar. The Spanish–American War and World War I confirmed the country's status as a global military power. The United States emerged from World War II as a global superpower, the first country to develop nuclear weapons, the only country to use them in warfare, and a permanent member of the United Nations Security Council. It is a founding member of the Organization of American States (UAS) and various other Pan-American and international organizations. The end of the Cold War and the dissolution of the Soviet Union in 1991 left the United States as the world's sole superpower.\nThe United States is a highly developed country, with the world's largest economy by nominal GDP. It ranks highly in several measures of socioeconomic performance, including average wage, human development, per capita GDP, and productivity per person. While the U.S. economy is considered post-industrial, characterized by the dominance of services and knowledge economy, the manufacturing sector remains the second-largest in the world. Though its population is only 4.4% of the world total, the United States accounts for nearly a quarter of world GDP and almost a third of global military spending, making it the world's foremost military and economic power. The United States is a prominent political and cultural force internationally, and a leader in scientific research and technological innovations.", |
|  | "recordType": "main", |
|  | "recordTypeScore": 3, |
|  | "popularity": 1812, |
|  | "sourceArticle": "United States", |
|  | "anchor": "" |
|  | }, |
|  | { |
|  | "title":"Etymology", |
|  | "text": "See also: Naming of America, Names for United States citizens, American (word), and Names of the United States In 1507 the German cartographer Martin Waldseemüller produced a world map on which he named the lands of the Western Hemisphere \"America\" after the Italian explorer and cartographer Amerigo Vespucci (Latin: Americus Vespucius). The first documentary evidence of the phrase \"United States of America\" is from a letter dated January 2, 1776, written by Stephen Moylan, Esq., George Washington's aide-de-camp and Muster-Master General of the Continental Army. Addressed to Lt. Col. Joseph Reed, Moylan expressed his wish to carry the \"full and ample powers of the United States of America\" to Spain to assist in the revolutionary war effort. The first known publication of the phrase \"United States of America\" was in an anonymous essay in The Virginia Gazette newspaper in Williamsburg, Virginia, on April 6, 1776. The second draft of the Articles of Confederation, prepared by John Dickinson and completed by June 17, 1776, at the latest, declared \"The name of this Confederation shall be the 'United States of America.'\" The final version of the Articles sent to the states for ratification in late 1777 contains the sentence \"The Stile of this Confederacy shall be 'The United States of America'\". In June 1776, Thomas Jefferson wrote the phrase \"UNITED STATES OF AMERICA\" in all capitalized letters in the headline of his \"original Rough draught\" of the Declaration of Independence. This draft of the document did not surface until June 21, 1776, and it is unclear whether it was written before or after Dickinson used the term in his June 17 draft of the Articles of Confederation. In the final Fourth of July version of the Declaration, the title was changed to read, \"The unanimous Declaration of the thirteen united States of America\". The preamble of the Constitution states \"...establish this Constitution for the United States of America.\" The short form \"United States\" is also standard. Other common forms are the \"U.S.\", the \"USA\", and \"America\". Colloquial names are the \"U.S. of A.\" and, internationally, the \"States\". \"Columbia\", a name popular in poetry and songs of the late 18th century, derives its origin from Christopher Columbus; it appears in the name \"District of Columbia\". In non-English languages, the name is frequently the translation of either the \"United States\" or \"United States of America\", and colloquially as \"America\". In addition, an abbreviation (e.g. USA) is sometimes used. The phrase \"United States\" was originally plural, a description of a collection of independent states—e.g., \"the United States are\"—including in the Thirteenth Amendment to the United States Constitution, ratified in 1865. The singular form—e.g., \"the United States is\"— became popular after the end of the American Civil War. The singular form is now standard; the plural form is retained in the idiom \"these United States\". The difference is more significant than usage; it is a difference between a collection of states and a unit. A citizen of the United States is an \"American\". \"United States\", \"American\" and \"U.S.\" refer to the country adjectivally (\"American values\", \"U.S.forces\"). \"American\" rarely refers to subjects not connected with the United States.", |
|  | "recordType": "section", |
|  | "recordTypeScore": 2, |
|  | "popularity": 1812, |
|  | "sourceArticle": "United States", |
|  | "anchor": "Etymology" |
|  | }, |
|  | { |
|  | "title":["History", "Indigenous and European contact"], |
|  | "text": "Further information: Pre-Columbian era and Colonial history of the United States An artistic recreation of The Kincaid Site from the prehistoric Mississippian culture as it may have looked at its peak 1050-1400 AD Italian explorer Christoper Columbus arrives in America and takes possession of Guanahani The first inhabitants of North America migrated from Siberia by way of the Bering land bridge and arrived at least 15,000 years ago, though increasing evidence suggests an even earlier arrival. Some, such as the pre-Columbian Mississippian culture, developed advanced agriculture, grand architecture, and state-level societies. After the Spanish conquistadors made the first contacts, the native population declined for various reasons, primarily from diseases such as smallpox and measles. Violence was not a significant factor in the overall decline among Native Americans, though conflict among themselves and with Europeans affected specific tribes and various colonial settlements. In the Hawaiian Islands, the earliest indigenous inhabitants arrived around 1 AD from Polynesia. Europeans under the British explorer Captain James Cook arrived in the Hawaiian Islands in 1778. In the early days of colonization, many European settlers were subject to food shortages, disease, and attacks from Native Americans. Native Americans were also often at war with neighboring tribes and allied with Europeans in their colonial wars. At the same time, however, many natives and settlers came to depend on each other. Settlers traded for food and animal pelts, natives for guns, ammunition and other European wares. Natives taught many settlers where, when and how to cultivate corn, beans and squash. European missionaries and others felt it was important to \"civilize\" the Native Americans and urged them to adopt European agricultural techniques and lifestyles.", |
|  | "recordType": "subsection", |
|  | "recordTypeScore": 1, |
|  | "popularity": 1812, |
|  | "sourceArticle": "United States", |
|  | "anchor": "Indigenous\_and\_European\_contact" |
|  | }, |
|  | { |
|  | "title":["History", "Indigenous and European contact"], |
|  | "text":"Further information: European colonization of the Americas and Thirteen Colonies Globe showing North America from 1602. Castillo de San Marcos in St. Augustine, Florida, the oldest continuously occupied European-established settlement in the United States The signing of the Mayflower Compact, 1620 After Spain sent Columbus on his first voyage to the New World in 1492, other explorers followed. The Spanish set up small settlements in New Mexico and Florida. France had several small settlements along the Mississippi River. Successful English settlement on the eastern coast of North America began with the Virginia Colony in 1607 at Jamestown and the Pilgrims' Plymouth Colony in 1620. Early experiments in communal living failed until the introduction of private farm holdings. Many settlers were dissenting Christian groups who came seeking religious freedom. The continent's first elected legislative assembly, Virginia's House of Burgesses created in 1619, and the Mayflower Compact, signed by the Pilgrims before disembarking, established precedents for the pattern of representative self-government and constitutionalism that would develop throughout the American colonies. Most settlers in every colony were small farmers, but other industries developed within a few decades as varied as the settlements. Cash crops included tobacco, rice and wheat. Extraction industries grew up in furs, fishing and lumber. Manufacturers produced rum and ships, and by the late colonial period Americans were producing one-seventh of the world's iron supply. Cities eventually dotted the coast to support local economies and serve as trade hubs. English colonists were supplemented by waves of Scotch-Irish and other groups. As coastal land grew more expensive freed indentured servants pushed further west. Slave cultivation of cash crops began with the Spanish in the 1500s, and was adopted by the English, but life expectancy was much higher in North America because of less disease and better food and treatment, leading to a rapid increase in the numbers of slaves. Colonial society was largely divided over the religious and moral implications of slavery and colonies passed acts for and against the practice. But by the turn of the 18th century, African slaves were replacing indentured servants for cash crop labor, especially in southern regions. With the British colonization of Georgia in 1732, the 13 colonies that would become the United States of America were established. All had local governments with elections open to most free men, with a growing devotion to the ancient rights of Englishmen and a sense of self-government stimulating support for republicanism. With extremely high birth rates, low death rates, and steady settlement, the colonial population grew rapidly. Relatively small Native American populations were eclipsed. The Christian revivalist movement of the 1730s and 1740s known as the Great Awakening fueled interest in both religion and religious liberty. During the Seven Years' War (also known as the French and Indian War), British forces seized Canada from the French, but the francophone population remained politically isolated from the southern colonies. Excluding the Native Americans, who were being conquered and displaced, those 13 colonies had a population of over 2.1 million in 1770, about one-third that of Britain. Despite continuing new arrivals, the rate of natural increase was such that by the 1770s only a small minority of Americans had been born overseas. The colonies' distance from Britain had allowed the development of self-government, but their success motivated monarchs to periodically seek to reassert royal authority.", |
|  | "recordType": "subsection", |
|  | "recordTypeScore": 1, |
|  | "popularity": 1812, |
|  | "sourceArticle": "United States", |
|  | "anchor": "Settlements" |
|  | }] |

[view raw](https://gist.github.com/speedblue/c09f84362d8122e2b03af8fac1dfbd8c/raw/fcc9f435527e01978d346a1d246d21b0b345dbea/WikipediaEnUnitedStatesSplit.json)[WikipediaEnUnitedStatesSplit.json](https://gist.github.com/speedblue/c09f84362d8122e2b03af8fac1dfbd8c#file-wikipediaenunitedstatessplit-json)hosted with ❤ by [GitHub](https://github.com/)

This split by section reduces a lot the probability of noise on large articles. It avoids the query “Etymology Indigenous” to match this article (which would typically match because there is a section called “Etymology” and another one called “Indigenous and European contact”). To improve the relevance, we have also divided the records into three different types that we order from the most important to the less important via the *recordTypeScore* attribute:

* “main”, this is the first section of the article, including the title and synonyms (score of 3)
* “section”: those are the main sections of the article (score of 2)
* “subsection”: subdivision inside the sections of the article (score of 1)

The *recordTypeScore*attribute will be used in the ranking to give more importance to the “main” records than the “section” and “subsection”.

Another good property of this split is that it allows linking to the right section of the page when you click on the search result. For example, if you search for “united states Settlements”, you will be able to open the United States page with the anchor text stored in the record.

Here is the list of the four Algolia settings we applied on this index:

|  |  |
| --- | --- |
|  | { |
|  | "attributeForDistinct": "sourceArticle", |
|  | "searchableAttributes": [ |
|  | "title", |
|  | "synonyms", |
|  | "text", |
|  | "sourceArticle" |
|  | ], |
|  | "customRanking": [ |
|  | "desc(recordTypeScore)", |
|  | "desc(popularity)" |
|  | ], |
|  | "ignorePlurals": [ |
|  | "en" |
|  | ] |
|  | } |

[view raw](https://gist.github.com/speedblue/4c90834a5d441ff7eb5d9260c4f057c7/raw/fd3648a01f9de5aea3e4fe6d7893061454f1748c/WikipediaEnIndexSettings.json)[WikipediaEnIndexSettings.json](https://gist.github.com/speedblue/4c90834a5d441ff7eb5d9260c4f057c7#file-wikipediaenindexsettings-json)hosted with ❤ by [GitHub](https://github.com/)

You can set those settings via the [setSettings API call](https://www.algolia.com/doc/api-client/methods/settings/) or directly on the dashboard:

* *searchableAttributes* and *customRanking* can be configured in the *Ranking* tab

![InsideEngine7searchableAttributesAndCustomRanking.png](/files/live/sites/algolia-assets/files/blogs/2025/InsideEngine7searchableAttributesAndCustomRanking.png)

Algolia Dashboard: Searchable & Ranking Attributes

* ignorePlurals can also be configured in the *Ranking* tab. For the moment you can only enable it for all languages in the dashboard (setting it to true), we will improve this setting to let you configure also the language.
* attributesForDistinct can be configured in the *Display* tab of the dashboard:

![InsideEngine7Distinct.png](/files/live/sites/algolia-assets/files/blogs/2025/InsideEngine7Distinct.png)

Algolia Dashboard: Group by

Each of those settings is important for the relevance:

* The *customRanking* uses the *recordTypeScore*to give importance to the main chapter in the case of equality on the textual relevance. In case of equality, we use the *popularity* attribute which represents the number of backlinks inside Wikipedia to this article (all records of the article keep the same popularity)
* The order of attributes in *searchableAttributes* gives the following decreasing importance for the matching attributes, title > text > synonyms > sourceArticle
* The *attributeForDistinct* is applied on the name of the article, only the best elements will be displayed for each matched articles
* We set *ignorePlurals* to “en” to consider all singular/plurals form of English as identical without introducing any noise (you can also set this setting at query time if you have a search in a different language using the same index)

With those settings, you can easily request a set of results without duplicates with the query parameter *distinct=true*. You can go even further by requesting several hits per deduplication key. You can, for example, pass [distinct=3 in your query](https://www.algolia.com/doc/guides/managing-results/refine-results/grouping/) to retrieve up to three results per distinct key – this feature is usually known as grouping.

## Keeping several records per distinct key

Search engines are also used for navigation or criteria-based search due to the fact that those queries are cheaper than on a regular database. Keeping several records per distinct key makes it easy to bring a different display to search.

For example, if you want to build a list of job offers, you will probably let the user search via different criteria like the role, location, job type, etc – but you might also want to aggregate the search results per company instead of having each job display company information. This is what [AngelList](https://angel.co/jobs) is doing when you search for a job on their platform. They display companies along with the three best job offers, this type of display can be built very quickly by:

* Having one record per job offer with an attribute containing the company ID
* Configuring the company ID attribute as *attributeForDistinct* in the index settings
* Passing *distinct=3* in your query

With those three simple actions, you can build an interface like AngelList below (Note that *SafeGraph* has only two job offers that match the criteria, the value three is the upper-bound limit on the number of records we want per distinct key). Some customers also implement a *“Show more”* button on each company that allows to display all offers for this company. To implement it, you have just to filter on the company name and specify *distinct=false* on the query to retrieve all offers of this company.

![Screen-Shot-2017-01-16-at-09.58.40-1.png](/files/live/sites/algolia-assets/files/blogs/2025/Screen-Shot-2017-01-16-at-09.58.40-1.png)

AngelList job search displaying several jobs per company

## The Impact of Distinct on faceting

Faceting can very quickly become a headache when distinct is enabled. Let’s illustrate the problem with a very simple example containing two records sharing the same distinct key.

|  |  |
| --- | --- |
|  | [ |
|  | { |
|  | "name": "First", |
|  | "facet": [ |
|  | "A", |
|  | "B" |
|  | ], |
|  | "distinctKey": "key1" |
|  | }, |
|  | { |
|  | "name": "Second", |
|  | "facet": [ |
|  | "B", |
|  | "C" |
|  | ], |
|  | "distinctKey": "key1" |
|  | } |
|  | ] |

[view raw](https://gist.github.com/speedblue/b370d1e9c4154b584d7caac0923f882b/raw/7bc13cf8aab8f20fc770c9b1d8d0b9092f12cc65/twoRecordsWithDistinctAndDifferentFacets.json)[twoRecordsWithDistinctAndDifferentFacets.json](https://gist.github.com/speedblue/b370d1e9c4154b584d7caac0923f882b#file-tworecordswithdistinctanddifferentfacets-json)hosted with ❤ by [GitHub](https://github.com/)

The first record contains the facet values “A” and “B” and the second record contains the facet values “B” and “C”.

Let’s imagine that you have a query that retrieves both records and that faceting and distinct is enabled in your query. You can imagine three different behaviors in this case:

* **Computing the faceting before the deduplication** (using distinct). In that case, the possible facet values will be “A=1”, “B=2” and “C=1”. All categories are retrieved but the count won’t fit what you have on screen.
* **Computing the faceting after deduplication** (distinct). In this case, the result would be “A=1”, “B=1” OR “B=1”, “C=1” depending on the best matching record. In both cases, the result is not what you expect.
* **Applying deduplication independently for each facet value**. In this case, we would have A=1, B=1 and C=1 (for each facet value, we need to look at all distinct key and perform a deduplication at this level).

The third behavior is the holy grail as the result of each facet count would be perfect. Unfortunately, the computation cost is insane and doesn’t scale as it directly depends on the number of facet values which match. In practice, it’s impossible to compute it in real time.

Let’s look at the advantages and drawbacks of the two approaches which can be computed for each query in a reasonable time:

* **Computing the faceting before the deduplication**: all retrieved facets are valid but the problem is obviously the counts are misleading because they include the duplicates. That said, this approach works very well if you do not want to display the count, it handle any case including the fact you can have different facets in the records that share the same distinct key.
* **Computing the faceting after the deduplication**: this approach works well when you use distinct=1 and all records with the same distinct key share the same facet values, which correspond exactly to the use case of splitting big documents. In other use cases, the results will be disturbing for users as some facet values can appear/disappear depending on the record which is kept after deduplication.

In other words, there is no perfect solution solving all problems. This is why we have decided to implement both approaches but as the deduplication can be misleading and cause weird effect, we have decided to use the faceting before the deduplication as the standard behavior. We have a query parameter called [facetingAfterDistinct=true](https://www.algolia.com/doc/rest-api/search/#facetingafterdistinct) that can be added to your query when you are splitting some big records. In this case, you have a perfect result because the facets are identical in all records sharing the same distinct key.

## Great features take time

We introduced the distinct feature in December 2013 and have improved it significantly in July 2015 by adding the support of distinct=N in the engine. The different faceting strategies have been a long-standing challenge and it took us a lot of time to find the best approach. The query parameter *facetingAfterDistinct=true*has been beta tested with real users for a few months before becoming public in December 2016.

This feature opened a lot of possibilities for our users and allowed a better indexing of big records that later gave the birth to our [DocSearch](https://community.algolia.com/docsearch/) project.

If you want to know more about the internal of the Algolia engine, we recommend to read the other posts in this series:

* [Part 1—indexing vs. search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-1-indexing-vs-search/)
* [Part 2—the indexing challenge of instant search](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-2-the-indexing-challenge-of-instant-search/)
* [Part 3—query processing](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-3-query-processing/)
* [Part 4—textual relevance](https://www.algolia.com/blog/engineering/inside-the-algolia-enginepart-4-textual-relevance/)
* [Part 5—Highlighting, a Cornerstone of Search UX](https://www.algolia.com/blog/engineering/inside-the-algolia-engine-part-5-highlighting-a-cornerstone-to-search-ux/)
* [Part 6—Handling Synonyms the Right Way](https://www.algolia.com/blog/engineering/inside-the-engine-part-6-handling-synonyms-the-right-way/)
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