---
title: 'Brave launches most powerful search API for AI to date'
company: Brave
tag: 搜索
date: 2026-02-12
url: https://brave.com/blog/most-powerful-search-api-for-ai/
account: 
origin: harvest2-202607
---
# Brave launches most powerful search API for AI to date

Published
Feb 12, 2026

[Share on X (formerly Twitter)](https://twitter.com/intent/tweet?text=Brave%20launches%20the%20LLM%20Context%20API,%20the%20most%20powerful%20search%20API%20for%20AI%20to%20date.%20With%20Brave%27s%20grounding%20data,%20cheaper%20open-weight%20models%20beat%20ChatGPT,%20Perplexity,%20and%20Google%20AI%20Mode.&via=brave&url=https://brave.com/blog/most-powerful-search-api-for-ai/ "Share on X (formerly Twitter)")
[Share on Reddit](https://reddit.com/submit?url=https://brave.com/blog/most-powerful-search-api-for-ai/&title=Brave%20launches%20the%20LLM%20Context%20API,%20the%20most%20powerful%20search%20API%20for%20AI%20to%20date.%20With%20Brave%27s%20grounding%20data,%20cheaper%20open-weight%20models%20beat%20ChatGPT,%20Perplexity,%20and%20Google%20AI%20Mode. "Share on Reddit")
[Share on Telegram](https://t.me/share/url?url=https://brave.com/blog/most-powerful-search-api-for-ai/&text=Brave%20launches%20the%20LLM%20Context%20API,%20the%20most%20powerful%20search%20API%20for%20AI%20to%20date.%20With%20Brave%27s%20grounding%20data,%20cheaper%20open-weight%20models%20beat%20ChatGPT,%20Perplexity,%20and%20Google%20AI%20Mode. "Share on Telegram")
[Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://brave.com/blog/most-powerful-search-api-for-ai/ "Share on LinkedIn")

[Brave Search news](/category/brave-search-news/)

**Note**: This blog post was updated June 25, 2026 to include scores from the latest round of performance comparison tests. [Jump to the bottom of the page](/blog/most-powerful-search-api-for-ai/#latest-scores) to see the results that show Ask Brave winning outright against other AI models thanks to the LLM Context endpoint.

Testing proves Brave’s high-quality grounding data allows cheaper open-weight LLMs to beat ChatGPT, Google AI Mode, and Perplexity

Today we’re launching a revamped [Brave Search API](/search/api/) that makes web search dramatically more useful for AI applications. The release includes three major updates: the most powerful search API to date, expanded developer tools and simpler, cheaper, but more powerful plans. Concurrent with the release, Brave is sharing research that shows less powerful open-weight LLMs beating the top LLMs when using Brave’s higher quality API data, available in this release. The updates include:

1. **The LLM Context API**: This is the most powerful search API for AI applications to date, optimized to provide Large Language Models (LLMs) with highly relevant context from the Web for any query or question. Already being used internally at scale, the LLM Context API is powering over 22 million answers per day in Brave Search, the largest private user-facing AI application in the world. A version of Brave’s chatbot, [Ask Brave](/blog/ask-brave/)—powered by Brave’s LLM Context and open-weights Qwen3—outperforms ChatGPT, Perplexity, and Google AI Mode in head-to-head comparisons thanks to high-quality context data (see table below).
2. **Developer Tools**: We’re releasing Brave Search API Skills, and an API assistant integrated in the Developer Portal trained to help you answer any questions about how to best use the Brave Search API. Those skills can also be accessed on most developer AI tools like Cursor, OpenCode or ClaudeCode.
3. **Simpler, cheaper and more powerful plans.** The two new plans—Search and Answers—will include everything you need. Search contains all the different types of Search: Web, LLM Context (newly released today), Images, News, Videos, and more, all priced at $5 per 1k requests. The Answers plan provides researched responses to your questions, alongside the Web results that grounded that response. Answers are priced at $4 per 1k Web searches plus $5 per million tokens (input and output). And *all* plans come with $5 in free credits every month.

Web search is essential infrastructure for the Web and AI. Brave Search is one of only three independent, global-scale search indexes in the western world, and the only one outside of Big Tech. It’s also the only index available via open, state-of-the-art APIs engineered for LLMs, [offering a public API with options for SOC2 compliance and Zero Data Retention](/blog/search-api-zero-data-retention/).

## The LLM Context API

In an internal evaluation of major AI search engines, [Ask Brave](https://ask.brave.com)—powered by Brave’s LLM Context API and open-weights Qwen3—outperforms ChatGPT, Perplexity, and Google AI Mode. To date, the AI industry has emphasized the importance and value of high-end models, but our testing shows that less powerful open-weights models can outperform closed frontier models if they incorporate high-quality grounding data. This is the data that the LLM Context API provides, and that we are releasing today to the public. With it, anyone building with AI can achieve similar high-quality results.

The LLM Context API is a unique offering that offers a data-first ranking, where the most relevant smart chunks of data are ranked and compiled in a compact format, optimized for LLM consumption. This maximizes the precision of the extracted grounding context, and is made possible by Brave’s complete search engine infrastructure (unlike scrapers which are faced with latency issues and can be limited in their data access).

### Evaluation

**Note**: This blog post was updated June 25, 2026 to include scores from the latest round of performance comparison tests. [Jump to the bottom of the page](/blog/most-powerful-search-api-for-ai/#latest-scores) to see the results that show Ask Brave winning outright against other AI models thanks to the LLM Context endpoint.

On November 30, 2025, we conducted a comprehensive evaluation of leading AI-powered answer engines using Claude Opus 4.5 and Claude Sonnet 4.5 as judges.

The evaluation consisted in collecting answers from Ask Brave, Grok, Google AI Mode, ChatGPT and Perplexity using the same set of 1,500 queries randomly sampled from real-world usage (e.g. “does iphone collect data when off”). Apart from Ask Brave, all answers were scraped using BrightData. The goal of using a scraping service is to be able to capture for each provider the exact experience that an anonymous user would have.

The answers were then evaluated using LLMs-as-judges (both Claude Opus and Sonnet 4.5 were used in a majority vote setting), considering all pairwise comparisons (all possible pairs evaluated for maximum reliability) and controlling for position bias by evaluating each pair twice (*A vs B* and *B vs A*).

![AI Model Performance Comparison Chart](/blog/most-powerful-search-api-for-ai/images/results.jpg)

|  | **Absolute category rating** (5-point Likert scale) | **Average win rate** | **Average lose rate** |
| --- | --- | --- | --- |
| **Grok** | 4.71 | 59.87% | 10.05% |
| **Ask Brave** | 4.66 | 49.21% | 15.82% |
| **Google AI mode** | 4.39 | 27.07% | 38.17% |
| **ChatGPT** | 4.32 | 23.87% | 42.22% |
| **Perplexity** | 4.01 | 10.51% | 64.26% |

Grok scores best with Ask Brave following closely behind, despite the fact Ask Brave uses a lower performance open-weights model (Qwen3). The key difference in these tests was Ask Brave’s use of the higher quality grounding context endpoint—the same API we’re releasing today. Systems with limited search index access trail significantly, demonstrating that context quality matters more than model capability.

This shows that context quality is likely the most significant factor in answer quality. An open-weight model with state-of-the-art grounding competes with (and often beats) high-performance frontier models operating with weaker context. The importance of high quality data should shift investor assessments of what drives commercial value in AI as the large models continue to commoditize.

[Read more about the evaluation prompt](https://github.com/brave/brave-search-skills/wiki/Evaluation-of-major-AI-powered-answer-engines) [1](#fn:1).

### How LLM Context works

Standard Web Search is optimized for human beings, and, as such, is centered on URLs. However, to be more powerful for AI and LLM use-cases, Brave’s revamped Search API optimizes for machine use. The LLM Context API goes a step further and offers a data-first ranking where the most relevant smart chunks are ranked and compiled in a compact format, optimized for LLM consumption.

Here’s what happens for each query:

1. Standard Web Search is performed on Brave’s independent index to identify the most relevant and qualitative pages.
2. We then dig deep into each page’s content in real time, converting raw HTML content into smart chunks. We go way beyond the typical conversion of webpages to markdown and have optimized handling for:

   * Clean text extraction using query-optimized snippets, markdown conversion and other clean text extraction, leveraging years of experience building and scaling Brave Search.
   * Structured data extraction (JSON+LD schemas, itemprops, tables including row-level granularity, etc.)
   * Specialized code context extraction, which is very relevant for technical questions and coding agents.
   * Forum discussions extraction.
   * YouTube captions handling.
3. Finally, we rank these smart chunks using an in-house system trained to identify the most relevant bits of information to address the query. The final response is compiled according to the user-specified configuration, allowing fine grained control over total number of tokens, number of URLs, etc.

This process ensures both great breadth and depth, maximizing precision of the extracted grounding context by considering top results, all of this without sacrificing latency.

These steps have been heavily optimized in order to limit the overhead on top of normal search to a minimum. In practice we observe less than 130ms overhead at p90 on top of normal search, resulting in a total latency under 600ms at p90 for calls to LLM Context.

### Unmatched control

The LLM Context API works with Brave’s Search tool [Goggles](https://search.brave.com/help/goggles) and the new LLM Context budget (which offers a way to set a token budget to control spending at a fine-granular level); it also supports local search. Let’s check them out one by one:

#### Goggles support

Goggles are a feature unique to Brave Search. They let you filter, boost, or downrank results by domain or URL pattern and can be scaled to thousands of rules. No other search engine (and as a result, LLM context) provider offers this level of control. [Learn more about Goggles](https://search.brave.com/help/goggles).

#### LLM Context budget

Fine-grained control over size of the resulting LLM context can be achieved using the optional `maximum_number_of_tokens` API parameter, which sets an upper bound on the number of (estimated) tokens for the final response. The selection process takes this limit into account and prioritizes the most relevant data in order to accommodate the budget.

Other options allow you to tweak the contribution of each URL, the maximum number of results or type of ranking in order to adapt the API to your specific use case.

#### Localized context

For location-aware queries, you have the option to pass user location via headers. The API then returns:

* **POI data**: Point of interest information for local businesses
* **Map results**: Location-specific results with geographic context

We allocate the token budget efficiently between local, map and global Web results. Learn more about the API, by visiting the [documentation](https://api-dashboard.search.brave.com/documentation/services/llm-context)**.**

## Developer tools

With this release, Brave Search has gotten easier to use. We’re supporting Skills, and offering an integrated AI Assistant trained at being able to answer questions about how to best leverage the Brave Search API for your needs.

### Skills

The Brave Search API now supports Skills—a powerful way to extend AI capabilities with modular, reusable workflows. These skills, a standardized format now [open-sourcedÂ here](https://github.com/brave/brave-search-skills), enable your AI editor or CLI to dynamically load instructions, scripts, and resources for specialized tasks that the Brave API can help with. These will help the 200,000+ developers that recently signed up for the Brave API through the release of OpenClaw.

### API Assistant

Built in the Developer Portal, we also released an API Assistant, trained to answer questions about the Brave Search API, able to point you to relevant endpoints, provide code examples and be an all-around guide to showcasing what you can accomplish with the Brave Search API.Â

![Screenshot of the integrated AI Assistant in the Brave Search API portal](/blog/most-powerful-search-api-for-ai/images/ai-assistant.jpg)

Figure 1: Screenshot of the integrated AI Assistant in the Brave Search API portal

## Simpler, cheaper and more powerful plans

We are arranging all existing API capabilities under the following public plans: Search, Answers, Spellcheck, and Autocomplete. Every plan gets $5 of free credit that renews every month (that would be $20 across all plans), making it by far the most convenient way to start building applications. To take advantage of this free credit, all you need to do is attribute the Brave Search API in your project’s website / about pages.

### Search

This plan contains all the different types of Search: Web, LLM Context (newly released today), Images, News, Videos, and more. All are priced the same way: $5 per 1000 requests, with $5 free credit every month.

### Answers

A few months ago [we released a specialised Answers Plan](/blog/ai-grounding/), that provides grounded answers to any question. This endpoint achieves a state-of-the-art 94.1% F1-score on SimpleQA benchmarking, and is specifically engineered to eliminate LLM hallucinations. [Check out our Answers Plan documentation.](https://api-dashboard.search.brave.com/documentation/services/answers)

Answers is priced at $4 per thousand Web searches plus $5 per million tokens (input and output). The first $5 is free, every month.

The Answers plan is great for those who want intelligence on tap with minimal setup. The new LLM Context API (under Search) on the other hand, is perfect for those who want to retain control of the LLM layer, running their models of choice, while getting the highest quality input data for those LLMs, in a token-efficient manner.

### Spellcheck

This API offers spellchecking as a service. It’s priced at $5 per 10k requests with $5 free credit every month. Spellchecking is a built-in capability in Search endpoints, where all queries are spellchecked by default.

### Autocomplete

This API offers suggestions as a service for any query. It includes entity-recognition and is priced at $5 per 10k requests with $5 free credit every month.

![Suggestions for "brave se"](/blog/most-powerful-search-api-for-ai/images/search.jpg)

Figure 2: Suggestions for “brave se”

## Why you should use the Brave Search API

As LLMs become commoditized, the quality of context they receive becomes the primary differentiator in application quality.

The Brave Search API is optimized for large-scale, commercial LLMs, as well as enterprises seeking to power their agents or AI apps by integrating billions of results from the Web with a simple API call. The Brave Search APIÂ  already powers the vast majority of the world’s largest AI LLM companies. Being independent and private, it has become the go-to choice for AI apps of scale because it has:

* **No scraper complications:** Brave is the only web search index at scale besides the Big Tech offerings. Other providers scrape. Scrapers violate Terms of Service, cannot offer true Zero Data Retention, some are being sued by Google, their data feed may arbitrarily shut off, and some suffer from latency issues. Anyone supplying enterprise solutions should avoid exposing clients to the inherent liabilities of scrapers.Â
* **No conflicts of interest**: Brave doesn’t use your search queries to train its own LLMs.
* **Zero Data Retention (ZDR)**: No queries are stored, logged, or linked to identities, enabling true ZDR. As we own and operate the entirety of our search stack, we can offer ZDR across all our endpoints without degradation of quality.
* **Proven security with SOC 2 (Type II) attestation**: Streamline legal due diligence and ensure rigorous security and privacy standards.
* **Compliance & continuity**: Brave’s independent infrastructure eliminates third-party reliance, ensuring queries never reach Big Tech. Unlike scrapers, which risk immediate shutdown for Terms of Service violations (e.g. Google v. SerpAPI), Brave provides a stable, legally sound solution.

Get started today with [Brave Search API](/search/api/). All plans come with $5 in free credits every month.

## June, 2026 updated evaluation

In June, 2026, we re-ran the comprehensive performance evaluation outlined earlier in this blog post.

As with that previous test, the evaluation consisted in collecting answers from Ask Brave, Grok, Google AI Mode, ChatGPT, and Perplexity using the same set of 1,500 queries randomly sampled from real-world usage (e.g. “does iPhone collect data when off”). Apart from Ask Brave, all answers were scraped using BrightData. The goal of using a scraping service is to be able to capture for each provider the exact experience that an anonymous user would have.

The answers were then evaluated using LLMs-as-judges (both Claude Opus and Sonnet 4.5 were used in a majority vote setting), considering all pairwise comparisons (all possible pairs evaluated for maximum reliability) and controlling for position bias by evaluating each pair twice (*A vs B* and *B vs A*).

The data is presented below as both a Bradley-Terry / Elo (which uses a statistical algorithm to rank LLMs based on crowdsourced, blind pairwise human voting) and Copeland (which measures direct head-to-head comparisons).

![Updated AI Model Performance: Copeland Score](/blog/most-powerful-search-api-for-ai/images/Copeland-Score.png)

![Updated AI Model Performance: Bradley-Terry / Elo Score](/blog/most-powerful-search-api-for-ai/images/Bradley-Terry-Elo.png)

|  | **Absolute category rating** (5-point Likert scale) | **Bradley-Terry / Elo** |
| --- | --- | --- |
| **Ask Brave** | 5.0 | 1169 |
| **Grok** | 4.0 | 1157 |
| **Ask Brave v1** | 3.0 | 1098 |
| **Google AI mode** | 2.0 | 1000 |
| **ChatGPT** | 1.0 | 880 |
| **Perplexity** | 0.0 | 695 |

In this updated round of tests, Ask Brave outscored all competitors, despite the fact Ask Brave uses a lower performance open-weights model (Qwen3). The key difference in these tests was Ask Brave’s use of the higher quality LLM Context grounding endpoint.

[Share on X (formerly Twitter)](https://twitter.com/intent/tweet?text=Brave%20launches%20the%20LLM%20Context%20API,%20the%20most%20powerful%20search%20API%20for%20AI%20to%20date.%20With%20Brave%27s%20grounding%20data,%20cheaper%20open-weight%20models%20beat%20ChatGPT,%20Perplexity,%20and%20Google%20AI%20Mode.&via=brave&url=https://brave.com/blog/most-powerful-search-api-for-ai/ "Share on X (formerly Twitter)")
[Share on Reddit](https://reddit.com/submit?url=https://brave.com/blog/most-powerful-search-api-for-ai/&title=Brave%20launches%20the%20LLM%20Context%20API,%20the%20most%20powerful%20search%20API%20for%20AI%20to%20date.%20With%20Brave%27s%20grounding%20data,%20cheaper%20open-weight%20models%20beat%20ChatGPT,%20Perplexity,%20and%20Google%20AI%20Mode. "Share on Reddit")
[Share on Telegram](https://t.me/share/url?url=https://brave.com/blog/most-powerful-search-api-for-ai/&text=Brave%20launches%20the%20LLM%20Context%20API,%20the%20most%20powerful%20search%20API%20for%20AI%20to%20date.%20With%20Brave%27s%20grounding%20data,%20cheaper%20open-weight%20models%20beat%20ChatGPT,%20Perplexity,%20and%20Google%20AI%20Mode. "Share on Telegram")
[Share on LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url=https://brave.com/blog/most-powerful-search-api-for-ai/ "Share on LinkedIn")