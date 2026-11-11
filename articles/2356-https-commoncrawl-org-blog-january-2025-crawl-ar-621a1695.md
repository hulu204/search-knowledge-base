---
title: 'https://commoncrawl.org/blog/january-2025-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/january-2025-crawl-archive-now-available
account: 
origin: en-rss
---
[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-001](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-001.svg)](/)

[←  Back to Blog](/blog)

January 31, 2025

# January 2025 Crawl Archive Now Available

We're pleased to announce our first crawl of 2025, containing 3.0 billion pages, and 460 TiB uncompressed content.

[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-002](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-003](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-003.webp)

The crawl archive for January 2025 is now available.

The data was crawled between January 12th and January 26th, and contains 3.0 billion web pages (or 460 TiB of uncompressed content). Page captures are from 49 million hosts or 39 million registered domains and include 0.98 billion new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/warc.paths.gz) | 90000 | 93.46 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/wat.paths.gz) | 90000 | 21.55 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/wet.paths.gz) | 90000 | 8.40 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/robotstxt.paths.gz) | 90000 | 0.16 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/non200responses.paths.gz) | 90000 | 3.09 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/cc-index.paths.gz) | 302 | 0.23 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/cc-index-table.paths.gz) | 900 | 0.26 |
|

### Archive Location & Download

The January 2025 crawl archive is located in the `commoncrawl` bucket at `crawl-data/CC-MAIN-2025-05/`.

To assist with exploring and using the dataset, we provide `gzip` compressed files which list all segments, `WARC`, `WAT` and `WET` files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively. Please see [Get Started](/get-started) for detailed instructions.

An [erratum regarding SURT URLs](https://commoncrawl.org/errata/surt-urls-do-not-properly-encode-non-utf-8-percent-encoded-characters) was fixed for this crawl, please see [iipc/webarchive-commons#102](https://github.com/iipc/webarchive-commons/pull/102) for further information.

This release was authored by:

[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-004](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-004.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-005](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-005.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## WARC Content-Type header in revisit records

Originally reported by:

Sebastian Nagel

[More details](/errata/warc-content-type-header-in-revisit-records)

Common Crawl's WARC revisit records use Content-Type: message/http (following the WARC 1.1 spec's example), but per iipc/warc-specifications#55 it should be application/http;msgtype=response for consistency with other HTTP response records.

## Erratum:

## Redirect target URL in URL indexes may be a relative URL

Originally reported by:

Sebastian Nagel

[More details](/errata/redirect-target-url-in-url-indexes-may-be-a-relative-url)

When the HTTP “Location” header includes a relative URL, the corresponding “redirect” field in the CDX Index and “fetch\_redirect” field in the URL Index (previously called the "Columnar Index") will also store a relative URL. In all other cases, redirect targets in the URL indexes should be recorded as absolute URLs.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-006](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-006.svg)](/)

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

[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-007](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695-fig-009](../images/2356-https-commoncrawl-org-blog-january-2025-crawl-ar-621a1695/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl