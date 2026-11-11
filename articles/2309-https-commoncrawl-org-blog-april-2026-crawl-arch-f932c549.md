---
title: 'https://commoncrawl.org/blog/april-2026-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/april-2026-crawl-archive-now-available
account: 
origin: en-rss
---
[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-001](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-001.svg)](/)

[←  Back to Blog](/blog)

April 28, 2026

# April 2026 Crawl Archive Now Available

We are pleased to announce that the crawl archive for April 2026 is now available, containing 2.19 billion web pages or 379.2 TiB of uncompressed content.

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-002](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-002.webp)

Luca Foppiano

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/luca-foppiano)

![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-003](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-003.webp)

The crawl archive for April 2026 is now available.

Corrected WARC Content-Type header

Starting from this crawl, revisit records now use the WARC header `Content-Type: application/http;msgtype=response` (previously `message/http`), aligning with [iipc/warc-specifications#55](https://github.com/iipc/warc-specifications/issues/55) for consistency with other HTTP response records.

The data was crawled between April 10th and April 23rd, and contains 2.19 billion web pages (or 379.2 TiB of uncompressed content). Page captures are from 43.2 million hosts or 35.4 million registered domains and include 660.5 million new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/warc.paths.gz) | 100000 | 85.05 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/wat.paths.gz) | 100000 | 14.66 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/wet.paths.gz) | 100000 | 6.06 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/robotstxt.paths.gz) | 100000 | 0.16 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/non200responses.paths.gz) | 100000 | 2.58 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/cc-index.paths.gz) | 302 | 0.17 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/cc-index-table.paths.gz) | 900 | 0.20 |

### Archive Location & Download

The April 2026 crawl archive is located in the `commoncrawl` bucket at `crawl-data/CC-MAIN-2026-17/`.

To assist with exploring and using the dataset, we provide gzipped files which list all segments, WARC, WAT and WET files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively, please see [Get Started](https://commoncrawl.org/get-started) for detailed instructions.

This release was authored by:

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-004](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-004.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-005](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-005.webp)

Michael Paris](https://commoncrawl.org/team/michael-paris)

Michael is a Senior Research Engineer at the Common Crawl Foundation.

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-006](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-006.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-007](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-007.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-008](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-008.webp)

Hande Çelikkanat](https://commoncrawl.org/team/hande-celikkanat)

Hande is a Senior ML Engineer with the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-009](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-009.svg)](/)

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

[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-010](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-010.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549-fig-012](../images/2309-https-commoncrawl-org-blog-april-2026-crawl-arch-f932c549/figure-012.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl