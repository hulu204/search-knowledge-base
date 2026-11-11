---
title: 'https://commoncrawl.org/blog/march-2026-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/march-2026-crawl-archive-now-available
account: 
origin: en-rss
---
[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-001](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-001.svg)](/)

[←  Back to Blog](/blog)

March 19, 2026

# March 2026 Crawl Archive Now Available

We are pleased to announce the release of the March 2026 crawl, containing 1.97 billion web pages, or 344.64 TiB of uncompressed content. We also observed a dramatic increase in fetches over IPv6, explained by the enabling of Happy Eyeballs in the OkHttp library.

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-002](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-002.webp)

Luca Foppiano

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/luca-foppiano)

![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-003](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-003.webp)

We are very happy to announce that the March 2026 crawl archive is now available.

## Increase in IPv6 fetches

By upgrading the crawler's HTTP client library [OkHttp](https://square.github.io/okhttp/), the Happy Eyeballs RFC ([RFC 6555](https://datatracker.ietf.org/doc/html/rfc6555)) was turned on.  Happy Eyeballs is an algorithm that lets clients race IPv4 and IPv6 connection attempts simultaneously, with a small head start given to IPv6. Whichever connects first wins, avoiding the long timeouts that would otherwise occur if one protocol is broken or slow. Having this enabled caused an increase of the amount of fetches over IPv6 from 0.5% to around 31%. See the [OkHttp Change Log](https://square.github.io/okhttp/changelogs/changelog/#version-500) for more information.

We also recently ran [an experiment to measure the adoption of IPv6 across the top 100k web hosts](https://commoncrawl.github.io/ipv6-analysis/), about which you can read in our [recent blog post](https://commoncrawl.org/blog/ipv6-adoption-across-the-top-100k-web-hosts), and see the corresponding data and code in its [GitHub repository](https://github.com/commoncrawl/ipv6-analysis).

## The crawl

The data was crawled between March 5th and March 17th, and contains 1.97 billion web pages (or 344.64 TiB of uncompressed content). Page captures are from 44 million hosts or 36.1 million registered domains and include 600 million new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/warc.paths.gz) | 100000 | 75.66 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/wat.paths.gz) | 100000 | 13.54 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/wet.paths.gz) | 100000 | 5.64 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/robotstxt.paths.gz) | 100000 | 0.17 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/non200responses.paths.gz) | 100000 | 2.35 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/cc-index.paths.gz) | 302 | 0.15 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/cc-index-table.paths.gz) | 900 | 0.19 |

### Archive Location & Download

The March 2026 crawl archive is located in the `commoncrawl` bucket at `crawl-data/CC-MAIN-2026-12/`.

To assist with exploring and using the dataset, we provide gzipped files which list all segments, WARC, WAT and WET files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively, please see [Get Started](https://commoncrawl.org/get-started) for detailed instructions.

This release was authored by:

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-004](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-004.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-005](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-005.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-006](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-006.webp)

Hande Çelikkanat](https://commoncrawl.org/team/hande-celikkanat)

Hande is a Senior ML Engineer with the Common Crawl Foundation.

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-007](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-007.webp)

Thijs Dalhuijsen](https://commoncrawl.org/team/thijs-dalhuijsen)

Thijs Dalhuijsen is Engineering Manager at Common Crawl.

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-008](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-008.webp)

Michael Paris](https://commoncrawl.org/team/michael-paris)

Michael is a Senior Research Engineer at the Common Crawl Foundation.

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

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-009](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-009.svg)](/)

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

[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-010](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-010.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e-fig-012](../images/2312-https-commoncrawl-org-blog-march-2026-crawl-arch-1084413e/figure-012.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl