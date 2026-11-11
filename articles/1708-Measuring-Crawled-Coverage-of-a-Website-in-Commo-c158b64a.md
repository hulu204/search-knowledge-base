---
title: 'Measuring Crawled Coverage of a Website in Common Crawl'
company: CommonCrawl
tag: 爬虫抓取
date: 2026-07-20
url: https://commoncrawl.org/blog/measuring-crawled-coverage-of-a-website-in-common-crawl
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

July 20, 2026

# Measuring Crawled Coverage of a Website in Common Crawl

How can we measure how many pages we’ve crawled from a particular website? The answer is a lot more complicated than you might think.

[![Greg Lindahl](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/65550ad52e2cbe00ff53493a_greg.webp)

Greg Lindahl

Greg is Chief Technology Officer at the Common Crawl Foundation.](https://commoncrawl.org/team/greg-lindahl-engineer)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

You might have the question of how many pages of any particular website are in Common Crawl’s dataset. This question is harder to answer than it seems – it’s not just the number of pages we crawled in the most recent crawl. Instead, our crawler forms an idea of how fast particular pages change, notices pages that change very slowly or never, and crawls those pages less and less often. This is good because it allows the crawler to focus on newly discovered pages, and pages that frequently change. But it’s bad in that it makes it hard to understand how complete the dataset is.

## **A glimpse inside the CrawlDB**

In this diagram, webpages that the crawler thinks are fresh enough to not need recrawling pile up in the “fetched” bubble. The size of this list of pages is our estimate of how many fresh webpages we have crawled from a website.

![A diagram of the states in the Nutch CrawlDB](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/6a5c963a70221493ca02f660_612e4315.png)

The states in the Nutch CrawlDB, taken from <https://cwiki.apache.org/confluence/spaces/NUTCH/pages/115512037/CrawlDatumStates>

This number of fetched pages is not currently visible in any production data products – but it is in our (in public testing) [Host Index](https://commoncrawl.org/blog/introducing-the-host-index) v2.

In this chart, which comes from the testing Host Index v2, the purple line is the number of fetched pages according to CrawlDB, and the blue is the number fetched in that particular crawl. Common Crawl’s website has become significantly more popular over time, which explains why the number of pages retained was so small in 2020. By the end of this test dataset, our rank and the CrawlDB number of fetched pages are both steadily rising, while the number of pages fetched per crawl is much smaller.

![A graph of the number of crawled pages per crawl, and the number of pages in the “fetched” state in CrawlDB](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/6a5c963a70221493ca02f663_06a526de.png)

The number of crawled pages per crawl, and the number of pages in the “fetched” state in CrawlDB

## **The Next Question**

The next question you might want to ask is: what fraction of the total pages on a website have we crawled? Not only the ones that we know about, but also the ones that we’ve never seen? Some websites have “sitemaps” and some of those sitemaps are actually accurate, so there’s one way to compute the fraction for some websites.

Another way to compute the fraction is to use math – a lot of math. For that, three Common Crawl engineers recently wrote this paper:

Michael Paris, Hande Celikkanat, Luca Foppiano. Measuring What the Crawler Sees: Discovery Curves, Core Persistence, and Shell Dynamics in Longitudinal Web Crawls.

<https://arxiv.org/abs/2607.13636>

### Abstract:

*A longitudinal web crawl is a sequence of partial samples of an evolving URL population. Pairwise containment between two crawls is the standard probe; under the homogeneous urn model it recovers per-round survival α and coverage c, but treats the population as uniform and consumes one pair at a time. We extend this analysis with the discovery curve U​(s,T), the cumulative URL footprint over a sliding window of T crawls starting at s, which under the same urn model is also a closed-form function of (α,c). Containment and the discovery curve are then two projections of one process: independent fits agree on (α,c) when the urn is homogeneous, so any disagreement is itself a measurement. Applied to Common Crawl (2020–2025, domain granularity) and to the German Academic Web (GAW, URL granularity), the two projections disagree on both archives, and a two-component urn with a persistent core fraction κ alongside shell parameters (α∂,c∂) reconciles the disagreement. A residual on c∂ remains, signalling that the shell itself is not homogeneous; κ is recorded as the scalar entry point to a rank-resolved generalisation, which is left to follow-up work.*

This release was authored by:

[![Greg is Chief Technology Officer at the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/65550ad52e2cbe00ff53493a_greg.webp)

Greg Lindahl](https://commoncrawl.org/team/greg-lindahl-engineer)

Greg is Chief Technology Officer at the Common Crawl Foundation.

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