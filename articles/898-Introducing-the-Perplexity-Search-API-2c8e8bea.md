---
title: 'Introducing the Perplexity Search API'
company: Perplexity
tag: 搜索
date: 2025-09-25
url: https://hub-prod.perplexity.ai/hub/blog/introducing-the-perplexity-search-api
account: 
origin: harvest2-202607
---
[![](https://framerusercontent.com/images/vHww1Ye1lCdzOILZcifoCCqmtKU.png)](https://perplexity.ai/)

[Blog](https://perplexity.ai/hub/blog)

[Research](https://research.perplexity.ai)

[Careers](https://www.perplexity.ai/hub/careers)

[Help Center](../helpcenter)

[Ask anything](https://perplexity.ai)

[![](https://framerusercontent.com/images/vHww1Ye1lCdzOILZcifoCCqmtKU.png)](https://perplexity.ai/)

Sep 25, 2025

# Introducing the Perplexity Search API

![](https://framerusercontent.com/images/Eb9Y1iduWcOd3e4hLSJJtL9Rg.jpg?width=2912&height=1632)

## Providing access to the same global-scale infrastructure that powers Perplexityâs public answer engine

The modern internet represents humanityâs collective knowledge and wisdom. Yet accessing this information programmatically and at scale has remained out of reach for too long. Legacy search incumbents maintain proprietary indices for their own exclusive use. Other providers have tried their best to fill the gaps, but are unable to provide the quality that todayâs developers need to build new capabilities in an increasingly information-driven, AI-forward marketplace. Weâve long heard from our own developer community that a world-class search and retrieval offering is sorely needed within the AI ecosystem.

Today, weâre answering that call by launching the [Perplexity Search API](http://perplexity.ai/api-platform). Our API provides access to the same global-scale infrastructure that powers Perplexityâs public answer engine. With an index covering hundreds of billions of webpages, developers can now tap information from across the internet with one simple yet powerful interface.

Weâre also releasing an [SDK](https://docs.perplexity.ai/guides/perplexity-sdk), [open-source evaluation framework](https://github.com/perplexityai/search_evals/), and [deep dive by Perplexity Research](https://research.perplexity.ai/articles/architecting-and-evaluating-an-ai-first-search-api) into how we designed, optimized, and evaluated our Search API.

## Built for modern AI workloads

Perplexity Search API is designed for the unique demands of AI applications. Unlike other API offerings that expose a restricted universe of information, our API provides rich structured responses that are ready for use in AI and traditional applications alike.

When it comes to AI, context is king. It is insufficient to operate simply at the document level. Our indexing and retrieval infrastructure divides documents up into fine-grained units. These sub-document units are individually surfaced and scored against the original query parameters, allowing our API to return documents with the most relevant snippets already ranked. This means less preprocessing, faster integration, and more valuable downstream results.

![](https://framerusercontent.com/images/Mffb1j6gLqHPTpFzB3GSsK56bc.png)![](https://framerusercontent.com/images/IkVCV23lGF78iMLDmaBA68ko8.png)

## Bringing Perplexityâs investments in accuracy and trust to developers

Since our founding, Perplexity has emphasized accuracy and trust across everything we do. We led the industry in corroborating AI answers with sources, and weâve since doubled down on our R&D investments to ensure that Perplexity is the worldâs most accurate and factual AI assistant.

Our search infrastructure is designed with this north star in mind. Our own experience reveals that information staleness is one of the biggest failure modes for AI agents, and weâve optimized our indexing workflows to make Perplexity a truly realtime assistant. Each second, our systems process tens of thousands of index update requests, ensuring that our index provides the freshest results available. These indexing operations leverage an AI-powered content understanding module that dynamically generates parsing logic to handle the messiness of the open web. The module optimizes itself via an iterative AI self-improvement process, powered by robust evaluations and realtime signals from the millions of user queries we service each hour.

Thanks to these and other investments, our search infrastructure positions Perplexity as the market leader in accuracy and relevance. Now, developers have effortless access to that same infrastructure to innovate across countless industries and use cases.

## Market-leading performance, pricing, and ergonomics

Perplexity Search API sits at the Pareto frontier of relevance and speed. Weâre releasing an open-source evaluation framework, `search_evals`, to enable researchers and developers to rigorously test any publicly available search API. On both single step search and deep research agentic workflows, Perplexity leads the competition across output quality and latency. Thanks to our infrastructure investments, we provide this superior performance at [lower cost](http://docs.perplexity.ai/getting-started/pricing).

![](https://framerusercontent.com/images/CWhmMPqOD7CkzssH6z803hXsQ.png)

Performance and cost are just the start. Weâve also carefully designed our API to prioritize ease of use for both human developers and AI agents. This includes our newly-launched [API Platform](http://perplexity.ai/api-platform) (which now houses the developer console and documentation for both our Search and Sonar APIs) and our [Search SDK](http://docs.perplexity.ai/guides/perplexity-sdk). Our own engineers have been able to use the Search SDK alongside their favorite AI coding tools to develop impressive product prototypes in under an hour. We anticipate even more impressive feats from startups and solo developers, mature enterprises, and everyone in between.

The Search API team will join our [San Francisco API Day](https://partiful.com/e/eTKw6p4IzVoLgz6Vsmug) and [London hackathon](https://pplx.ai/london-hackathon) next month, and you can also reach them online through our [developer community](http://community.perplexity.ai/). Developers who choose our Search API can look forward to benefitting from the same research and engineering improvements that we deploy within Perplexityâs user-facing products, meaning even better performance and cost-effectiveness over time.

## Democratizing access to knowledge across humans and code

Our journey to democratize access to knowledge began with satisfying our usersâ boundless curiosity. With the Perplexity Search API, that journey continues with empowering the worldâs millions of developers. We canât wait to see what they build with internet-scale search at their fingertips.

[[Get started on API Platform](https://www.perplexity.ai/api-platform)]  
[[Install our SDK](https://docs.perplexity.ai/guides/perplexity-sdk)]  
[[Read more at Perplexity Research](https://research.perplexity.ai/articles/architecting-and-evaluating-an-ai-first-search-api)]