---
title: 'Better image retrieval for every Tavily search result'
company: Tavily
tag: 搜索
date: 2026-03-24
url: https://www.tavily.com/blog/better-image-retrieval
account: 
origin: harvest2-202607
---
![Better image retrieval for every Tavily search result](https://cdn.sanity.io/images/5tlb0lxv/production/8acd8bb205dc8d2bad7a70bc7ccfa4c002cb4279-390x194.webp?w=1200&q=75&auto=format)

/product·3 min read

# Better image retrieval for every Tavily search result

Retrieve text and page-specific visuals together in a single search response, without and extra image search or matching layer

![](https://cdn.sanity.io/images/5tlb0lxv/production/0c5b686cc278299ac509c817e650545a1186ea11-112x112.png?w=64&h=64&q=75&auto=format)

Tavily Team

Mar 24, 2026

Today we are improving Tavily Search with better image retrieval through include\_images.

When enabled, Tavily now returns **source-linked images on each search result**, so agents and applications can access the diagrams, charts, screenshots, tables, and product visuals that appear on the page itself. Instead of running a separate image search and trying to match visuals back to sources later, developers can now retrieve text and relevant page images together in a single response.

This makes Tavily more useful as a multimodal retrieval layer for engineers building agents, research workflows, and richer search interfaces.

### Why source-linked images matter

A lot of the web’s useful information is visual.

In practice, many pages communicate key context through charts, dashboards, diagrams, screenshots, tables, and product imagery. But most retrieval pipelines still treat images as separate from the source, or ignore them entirely.

That creates two problems.

First, models miss information that never appears in the text.

Second, engineers end up building extra logic around retrieval just to keep visuals attached to the source they came from. The usual workaround is to run a separate image search, filter the results, and then try to map those images back to the right page. That adds complexity in the wrong place and makes multimodal pipelines more brittle than they need to be.

By returning relevant images directly on each result, Tavily preserves the relationship between the page and its visuals from the start.

### Enable it in one line

If you already use Tavily Search, you can turn this on by setting include\_images to true.

```
{
  "query":"Uniqlo and Kaws partnership",
  "search_depth":"advanced",
  "include_images":true,
}
```

This works across all search depths and fits into existing search workflows without changing the rest of your integration.

### What your agent can do

**Reason over text and visuals from the same source**

Instead of giving your model page text alone, you can now pass in both the written content and the most relevant visuals found on that page. That is useful when the key signal lives in a chart, table, screenshot, or diagram rather than in the copy around it.

**Reduce multimodal pipeline overhead**

Source-linked image retrieval removes the need for a parallel image search and a matching layer on top of search. Engineers can make one request, get one result object, and preserve source context throughout the pipeline.

**Build better result interfaces**

For teams building user-facing search or research products, each result can now carry visuals that actually belong to the cited source. That makes result cards, answer views, and research workflows more informative and easier to trust.

### Where this is useful

**Finance**

Earnings reports, filings, and investor pages often rely on charts, comparison tables, and dashboard-like visuals. Returning those assets with the page improves document understanding and helps models ground conclusions in the source more completely.

**Research and academia**

Papers and technical documents often depend on figures, graphs, and supplementary diagrams. With source-linked images, developers can augment a paper’s text only with the visuals that belong to that same paper.

**Travel**

Travel experiences often depend on photos as much as text. Returning hotel or destination images alongside each source gives users a clearer understanding of what each result actually refers to.

**E-commerce**

Product listings often include the most useful context in images, comparison visuals, and product guides. Source-linked retrieval helps teams build more visual experiences, while still evaluating attribution and usage-rights requirements for external-facing applications.

### What the response looks like

With this update, Tavily can return an images array on each result object.

That means the response can include:

* the source URL
* the page content
* page-specific images
* optional image descriptions

The important distinction is that these are not generic images from around the web. They are visuals found on the same page as the source result, which makes them much more useful for downstream reasoning and UI.

### Available now

Source-linked image retrieval is now available in Tavily Search through include\_images.

If you are building multimodal agents, research workflows, or richer search interfaces, you can start using it with your existing Tavily Search integration today.

Check out the docs here: <https://docs.tavily.com/documentation/best-practices/best-practices-search#response-content>