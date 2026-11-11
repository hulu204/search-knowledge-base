---
title: 'Introducing our most accurate search yet'
company: Firecrawl
tag: 搜索
date: 2026-07-22
url: https://www.firecrawl.dev/blog/introducing-our-most-accurate-search-yet
account: 
origin: harvest2-202607
---
[Blog](/blog)

# Introducing our most accurate search yet

![placeholder](/_next/image?url=%2Fblog%2Fauthors%2Feric-img.jpeg&w=48&q=75&dpl=dpl_BonP4CzswHAdBhe4529NQAppYj1c)Eric CiarlaJul 22, 2026

![Introducing our most accurate search yet image](/_next/image?url=%2Fimages%2Fblog%2Fimproved-search-launch%2Fmajor-upgrade-to-firecrawl-search.webp&w=3840&q=75&dpl=dpl_BonP4CzswHAdBhe4529NQAppYj1c)

**Today we're shipping a major upgrade to Firecrawl [`/search`](https://docs.firecrawl.dev/features/search): a new custom relevance model that returns the excerpts that best answer your query from each result. Agents using `/search` achieve state-of-the-art accuracy on SimpleQA while using 10x fewer tokens than processing full pages.**

Agents rely on search tools to find answers on the web, but those answers are often buried in noise. Navigation, boilerplate, and tangents wrap around the excerpt that matters, so an agent processes far more content than it needs to, which is slower, more expensive, and more likely to land on the wrong answer.

Our `/search` endpoint now runs every result through the new custom relevance model, returning only the excerpts that answer your exact query.

## How the improved Firecrawl /search works

Our custom model scores every paragraph, list, and table against your query. It surfaces the most relevant excerpts wherever they appear on the page, then returns them structured and ready for your agent to use.

## State-of-the-art accuracy on SimpleQA

[SimpleQA](https://openai.com/index/introducing-simpleqa/) is OpenAI's factuality benchmark, measuring whether models correctly answer short, fact-seeking questions. In our eval, agents using Firecrawl `/search` score 94.7%, higher than with any other provider we tested.

![Firecrawl /search SimpleQA benchmark results](/images/blog/improved-search-launch/simpleqa-benchmark.webp)

### Evaluation methodology

A GPT-5.4 agent with high reasoning effort runs with up to 20 tool calls: `search_web`, backed by the provider under test, plus `web_fetch` through that provider's own extract API (Firecrawl Scrape, Parallel Extract, or Exa Contents). Claude native search is Claude Sonnet 4.6 with Anthropic's server-side web search, evaluated as a complete system.

Answers are graded by an LLM judge using GPT-5.4 and the official SimpleQA grader prompt. The full SimpleQA set of 4,326 questions was run across two sessions per provider, with the best observed score selected. As a baseline, GPT-5.4 with no search tools scores 43.8 under the same judge.

## 10x fewer tokens than full pages

By returning key excerpts instead of full-page content, `/search` leaves more of an agent's context window available for reasoning. Fewer input tokens also make downstream model calls cheaper and faster.

## What you can build with it

* **Multi-step agent search:** Keep an agent's context lean across long chains of searches by returning only the excerpts that answer each query.
* **RAG and LLM grounding:** Add relevant excerpts directly to a prompt without separate chunking or reranking.
* **Lead enrichment:** Find specific facts about a person, company, or domain, including titles, revenue, and hiring signals.
* **Research and market intelligence:** Pull a specific claim, figure, or quote without processing the rest of the page.

## Nothing to change in your code

Existing `/search` calls return more relevant context automatically, with no changes required. The API shape is unchanged, and each result still includes its title, URL, and description alongside query-relevant Markdown excerpts by default. If you need complete page content, you can still retrieve full-page Markdown in the same call:

```
from firecrawl import Firecrawl
 
firecrawl = Firecrawl(api_key="fc-YOUR-API-KEY")
 
results = firecrawl.search(
    "what changed in the EU AI Act enforcement timeline",
    limit=5,
    scrape_options={"formats": ["markdown"]},
)
 
for result in results.web:
    print(result.title)
    print(result.url)
    print(result.markdown)
```

## Try it today

The upgraded `/search` is live for every Firecrawl user, across the API, SDKs, CLI, and MCP.

1. [Read the /search documentation](https://docs.firecrawl.dev/features/search-highlights)
2. [Try it in the Playground](https://firecrawl.link/search-pg)
3. Point your agent at `/search` and give it state-of-the-art search accuracy

[Try /search in the Playground](https://firecrawl.link/search-pg) · [Read the docs](https://docs.firecrawl.dev/features/search-highlights?utm_source=blog&utm_medium=referral&utm_campaign=introducing-our-most-accurate-search-yet)