---
title: 'Web Graph Statistics Gets a Proper Upgrade'
company: CommonCrawl
tag: 工程相关
date: 2026-03-06
url: https://commoncrawl.org/blog/web-graph-statistics-gets-a-proper-upgrade
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

March 6, 2026

# Web Graph Statistics Gets a Proper Upgrade

Our Web Graph Statistics site has been updated with interactive charts, a domain lookup tool for tracking harmonic centrality and PageRank over time, mobile improvements, unified rank tables with OR filtering, and merged degree plots.

[![Thom Vaughan](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/69a085daa014334c437fefb3_thom-hires.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

The [cc-webgraph-statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) site has been quietly doing its job for a while now: publishing harmonic centrality and PageRank data derived from Common Crawl's web graph, and letting researchers and the curious alike poke around the rankings.  It worked, but it didn't really sparkle.

That changes with this [latest update](https://github.com/commoncrawl/cc-webgraph-statistics/pull/9), which brings a substantial redesign and a handful of genuinely useful new features. Here's what's new.

## **Interactive Charts**

The most immediately visible change: all charts are now interactive. Previously the site rendered static images, which are fine for a quick glance but not much use if you want to zoom into a particular time window, hover over a data point, or scroll horizontally through a long series.  The charts now respond to all of the above.  If you're the sort of person who squints at trend lines and wants to know exactly what the value was in March 2021, you can now find out without firing up a spreadsheet.

## **Domain Lookup Tool**

This is the headline feature.  You can now search for any domain in the top 1000 domains and plot its harmonic centrality and PageRank scores across every Common Crawl crawl in which it appears.  Want to know how a site's web presence has evolved over the past few years?  Type it in and see.

It also supports side-by-side comparison of two domains, which makes it straightforward to benchmark one site against another, or to watch what happens to a domain's ranking around a notable event.  The domain lookup widget is also embeddable, so if you want to drop a live chart into your own page or post, you can. Check it out:

## **Cleaner Degree Statistics**

The avgindegree and avgoutdegree plots have been merged into a single avgdegree view, addressing a long-standing open issue.  The separation was never particularly illuminating in practice, and having them combined makes the overall picture easier to read.

## **Harmonic Centrality References**

Another issue closed: the harmonic centrality section now links to the relevant research papers. Harmonic centrality is not an especially intuitive metric for the uninitiated.  It measures how reachable a node is from all other nodes in a graph, weighted by inverse distance, and having proper references makes the methodology section considerably more useful.

## **Rank Tables**

The rank tables have been consolidated into a single unified table, with a few additions: SURT (Sort-friendly URI Reordering Transform) can now be toggled on or off depending on your preference, and filtering supports OR logic, so you can search for multiple terms at once.  There's also a clearer display of match counts.

## **Mobile and Responsive Improvements**

The site now behaves considerably better on small screens.  Speed and performance are noticeably improved.

The updated site is available at [commoncrawl.github.io/cc-webgraph-statistics](http://commoncrawl.github.io/cc-webgraph-statistics).  The source is on [GitHub](https://github.com/commoncrawl/cc-webgraph-statistics), and feedback is welcome via issues or the usual channels.

‍

This release was authored by:

[![Thom is Principal Engineer at the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/69a085daa014334c437fefb3_thom-hires.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![Common Crawl Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

## The Data

### [Overview](/overview)

### [CDXJ Index](/cdxj-index)

### [URL Index](/url-index)

### [Web Graphs](/web-graphs)

### [Latest Crawl](/latest-crawl)

### [Crawl Stats](https://commoncrawl.github.io/cc-crawl-statistics/)

### [Graph Stats](https://commoncrawl.github.io/cc-webgraph-statistics/)

### [Errata](/errata)

## Resources

### [Get Started](/get-started)

### [AI Agent](/ai-agent)

### [Blog](/blog)

### [Examples](https://commoncrawl.github.io/cc-examples/)

### [CCBot](/ccbot)

### [Infra Status](https://status.commoncrawl.org)

### [Opt-Out Registry](https://commoncrawl.org/blog/common-crawl-foundation-opt-out-registry)

### [FAQ](/faq)

## Community

### [Research Papers](/research-papers)

### [Mailing List Archive](https://groups.google.com/g/common-crawl)

### [Hugging Face](https://huggingface.co/commoncrawl)

### [Discord](https://discord.gg/njaVFh7avF)

### [Collaborators](/collaborators)

## About

### [About](/about)

### [Team](/team)

### [Jobs](/jobs)

### [Privacy Policy](/privacy-policy)

### [Terms of Use](/terms-of-use)

[![Twitter Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6675a2f3394182102f502e32_twitter-x.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6602100396780a14617cc8ab_discord.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl