---
title: 'https://commoncrawl.org/blog/measuring-crawled-coverage-of-a-website-in-common-crawl'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/measuring-crawled-coverage-of-a-website-in-common-crawl
account: 
origin: en-rss
---
[![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-001](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-001.svg)](/)

[←  Back to Blog](/blog)

July 20, 2026

# Measuring Crawled Coverage of a Website in Common Crawl

How can we measure how many pages we’ve crawled from a particular website? The answer is a lot more complicated than you might think.

[![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-002](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-002.webp)

Greg Lindahl

Greg is Chief Technology Officer at the Common Crawl Foundation.](https://commoncrawl.org/team/greg-lindahl-engineer)

![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-003](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-003.webp)

You might have the question of how many pages of any particular website are in Common Crawl’s dataset. This question is harder to answer than it seems – it’s not just the number of pages we crawled in the most recent crawl. Instead, our crawler forms an idea of how fast particular pages change, notices pages that change very slowly or never, and crawls those pages less and less often. This is good because it allows the crawler to focus on newly discovered pages, and pages that frequently change. But it’s bad in that it makes it hard to understand how complete the dataset is.

## **A glimpse inside the CrawlDB**

In this diagram, webpages that the crawler thinks are fresh enough to not need recrawling pile up in the “fetched” bubble. The size of this list of pages is our estimate of how many fresh webpages we have crawled from a website.

![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-004](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-004.png)

The states in the Nutch CrawlDB, taken from <https://cwiki.apache.org/confluence/spaces/NUTCH/pages/115512037/CrawlDatumStates>

This number of fetched pages is not currently visible in any production data products – but it is in our (in public testing) [Host Index](https://commoncrawl.org/blog/introducing-the-host-index) v2.

In this chart, which comes from the testing Host Index v2, the purple line is the number of fetched pages according to CrawlDB, and the blue is the number fetched in that particular crawl. Common Crawl’s website has become significantly more popular over time, which explains why the number of pages retained was so small in 2020. By the end of this test dataset, our rank and the CrawlDB number of fetched pages are both steadily rising, while the number of pages fetched per crawl is much smaller.

![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-005](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-005.png)

The number of crawled pages per crawl, and the number of pages in the “fetched” state in CrawlDB

## **The Next Question**

The next question you might want to ask is: what fraction of the total pages on a website have we crawled? Not only the ones that we know about, but also the ones that we’ve never seen? Some websites have “sitemaps” and some of those sitemaps are actually accurate, so there’s one way to compute the fraction for some websites.

Another way to compute the fraction is to use math – a lot of math. For that, three Common Crawl engineers recently wrote this paper:

Michael Paris, Hande Celikkanat, Luca Foppiano. Measuring What the Crawler Sees: Discovery Curves, Core Persistence, and Shell Dynamics in Longitudinal Web Crawls.

<https://arxiv.org/abs/2607.13636>

### Abstract:

*A longitudinal web crawl is a sequence of partial samples of an evolving URL population. Pairwise containment between two crawls is the standard probe; under the homogeneous urn model it recovers per-round survival α and coverage c, but treats the population as uniform and consumes one pair at a time. We extend this analysis with the discovery curve U​(s,T), the cumulative URL footprint over a sliding window of T crawls starting at s, which under the same urn model is also a closed-form function of (α,c). Containment and the discovery curve are then two projections of one process: independent fits agree on (α,c) when the urn is homogeneous, so any disagreement is itself a measurement. Applied to Common Crawl (2020–2025, domain granularity) and to the German Academic Web (GAW, URL granularity), the two projections disagree on both archives, and a two-component urn with a persistent core fraction κ alongside shell parameters (α∂,c∂) reconciles the disagreement. A residual on c∂ remains, signalling that the shell itself is not homogeneous; κ is recorded as the scalar entry point to a rank-resolved generalisation, which is left to follow-up work.*

This release was authored by:

[![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-006](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-006.webp)

Greg Lindahl](https://commoncrawl.org/team/greg-lindahl-engineer)

Greg is Chief Technology Officer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-007](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-007.svg)](/)

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

[![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-008](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a-fig-010](../images/2298-https-commoncrawl-org-blog-measuring-crawled-cov-c158b64a/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl