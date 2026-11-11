---
title: 'https://commoncrawl.org/blog/september-2025-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/september-2025-crawl-archive-now-available
account: 
origin: en-rss
---
[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-001](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-001.svg)](/)

[←  Back to Blog](/blog)

September 22, 2025

# September 2025 Crawl Archive Now Available

We are pleased to announce the release of our September 2025 crawl, containing 2.39 billion web pages, or 421 TiB of uncompressed content.

[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-002](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-003](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-003.webp)

The crawl archive for September 2025 is now available.

The data was crawled between September 5th and September 18th, and contains 2.39 billion web pages (or 421 TiB of uncompressed content). Page captures are from 47 million hosts or 38.6 million registered domains and include 801 million new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/warc.paths.gz) | 100000 | 87.47 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/wat.paths.gz) | 100000 | 16.75 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/wet.paths.gz) | 100000 | 6.83 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/robotstxt.paths.gz) | 100000 | 0.15 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/non200responses.paths.gz) | 100000 | 3.02 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/cc-index.paths.gz) | 302 | 0.18 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/cc-index-table.paths.gz) | 900 | 0.21 |
|

### Archive Location & Download

The September 2025 crawl archive is located in the `commoncrawl` bucket at `crawl-data/CC-MAIN-2025-38/`.

To assist with exploring and using the dataset, we provide gzipped files which list all segments, WARC, WAT and WET files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively, please see [Get Started](https://commoncrawl.org/get-started) for detailed instructions.

This release was authored by:

[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-004](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-004.webp)

Laurie Burchell](https://commoncrawl.org/team/laurie-burchell)

Laurie is a Principal Research Engineer at the Common Crawl Foundation.

[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-005](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-005.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## WARC Content-Type header in revisit records

Originally reported by:

Sebastian Nagel

[More details](/errata/warc-content-type-header-in-revisit-records)

Common Crawl's WARC revisit records use Content-Type: message/http (following the WARC 1.1 spec's example), but per iipc/warc-specifications#55 it should be application/http;msgtype=response for consistency with other HTTP response records.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-006](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-006.svg)](/)

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

[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-007](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85-fig-009](../images/2333-https-commoncrawl-org-blog-september-2025-crawl-c7b9be85/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl