---
title: 'https://commoncrawl.org/blog/october-2025-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/october-2025-crawl-archive-now-available
account: 
origin: en-rss
---
[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-001](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-001.svg)](/)

[←  Back to Blog](/blog)

October 23, 2025

# October 2025 Crawl Archive Now Available

We are pleased to announce the release of the October 2025 crawl, containing 2.61 billion web pages or 468 TiB of uncompressed content.

[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-002](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-002.webp)

Hande Çelikkanat

Hande is a Senior ML Engineer with the Common Crawl Foundation.](https://commoncrawl.org/team/hande-celikkanat)

![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-003](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-003.webp)

The crawl archive for October 2025 is now available.

The data was crawled between October 5th and October 19th, and contains 2.61 billion web pages (or 468 TiB of uncompressed content). Page captures are from 47 million hosts or 38.5 million registered domains and include 747 million new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/warc.paths.gz) | 100000 | 97.73 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/wat.paths.gz) | 100000 | 18.39 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/wet.paths.gz) | 100000 | 7.38 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/robotstxt.paths.gz) | 100000 | 0.15 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/non200responses.paths.gz) | 100000 | 3.07 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/cc-index.paths.gz) | 302 | 0.20 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/cc-index-table.paths.gz) | 900 | 0.23 |
|

### Archive Location & Download

The October 2025 crawl archive is located in the `commoncrawl` bucket at `crawl-data/CC-MAIN-2025-43/`.

To assist with exploring and using the dataset, we provide gzipped files which list all segments, WARC, WAT and WET files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively, please see [Get Started](https://commoncrawl.org/get-started) for detailed instructions.

This release was authored by:

[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-004](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-004.webp)

Hande Çelikkanat](https://commoncrawl.org/team/hande-celikkanat)

Hande is a Senior ML Engineer with the Common Crawl Foundation.

[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-005](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-005.webp)

Malte Ostendorff](https://commoncrawl.org/team/malte-ostendorff)

Malte is a Senior Research Engineer at Common Crawl.

[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-006](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-006.webp)

Damian Stewart](https://www.linkedin.com/in/damian-stewart/)

Damian is a software developer and researcher with a multidisciplinary background, based in Vienna, Austria.

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

[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-007](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-007.svg)](/)

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

[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-008](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975-fig-010](../images/2328-https-commoncrawl-org-blog-october-2025-crawl-ar-9645f975/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl