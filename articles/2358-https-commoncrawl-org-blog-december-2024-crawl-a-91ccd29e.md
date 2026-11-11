---
title: 'https://commoncrawl.org/blog/december-2024-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/december-2024-crawl-archive-now-available
account: 
origin: en-rss
---
[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-001](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-001.svg)](/)

[←  Back to Blog](/blog)

December 18, 2024

# December 2024 Crawl Archive Now Available

The crawl archive for December 2024 is now available. The data was crawled between December 1st and December 15th, and contains 2.64 billion web pages (or 394 TiB of uncompressed content). Page captures are from 47.5 million hosts or 38.3 million registered domains and include 1.05 billion new URLs, not visited in any of our prior crawls.

[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-002](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-002.webp)

Sebastian Nagel

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/sebastian-nagel-engineer)

![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-003](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-003.webp)

The crawl archive for December 2024 is now available.

The data was crawled between December 1st and December 15th, and contains 2.64 billion web pages (or 394 TiB of uncompressed content). Page captures are from 47.5 million hosts or 38.3 million registered domains and include 1.05 billion new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/warc.paths.gz) | 90000 | 80.92 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/wat.paths.gz) | 90000 | 18.70 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/wet.paths.gz) | 90000 | 7.37 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/robotstxt.paths.gz) | 90000 | 0.14 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/non200responses.paths.gz) | 90000 | 2.75 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/cc-index.paths.gz) | 302 | 0.20 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/cc-index-table.paths.gz) | 900 | 0.23 |

### Archive Location & Download

The December 2024 crawl archive is located in the `commoncrawl` bucket with the prefix: `crawl-data/CC-MAIN-2024-51/`.

To assist with exploring and using the dataset, we provide `gzip`-compressed files which list all segments, `WARC`, `WAT` and `WET` files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively. Please see [Get Started](/get-started) for detailed instructions.

### Changes to the `WAT` Metadata Format

#### Multi-valued headers

Repeated `HTTP` and `WARC` headers were not represented in the `JSON` data in `WAT` files. When a header was repeated adding a further value of that header, only the last value was stored and other values were lost. This old issue ([ia-web-commons#18](https://github.com/commoncrawl/ia-web-commons/issues/18)) is now fixed:

* Single value headers are represented as before by a header name and a string value.
* Headers with multiple values are represented by a header name and an associated list of values.

‍

Users are advised to update any code consuming `WAT` files to this change. The examples in the projects `cc-pyspark` and `cc-warc-examples` were updated accordingly, see [cc-pyspark#46](https://github.com/commoncrawl/cc-pyspark/pull/46) resp. [cc-warc-examples#5](https://github.com/commoncrawl/cc-warc-examples/pull/5).

Below are two `JSON` snippets of multi-valued headers:

* The [WARC-Protocol](https://github.com/iipc/warc-specifications/issues/42) header field:

```
{
  "Container": { "...": "..." },
  "Envelope": {
        "WARC-Header-Metadata": {
          "...": "...",
          "WARC-Target-URI": "https://en.wikipedia.org/wiki/Saturn",
          "WARC-Protocol": [
            "h2",
            "tls/1.3"
          ],
```

* Many `HTTP` headers, most commonly the "`Set-Cookie`" header:

```
{
"Container": { "...": "..." },
"Envelope": {
  "Payload-Metadata": {
    "Actual-Content-Type": "application/http; msgtype=response",
    "HTTP-Response-Metadata": {
      "...": "...",
      "Headers": {
        "date": "Sat, 30 Nov 2024 11:13:30 GMT",
        "...": "...",
        "set-cookie": [
          "WMF-Last-Access=30-Nov-2024;Path=/;HttpOnly;secure;Expires=Wed, 01 Jan 2025 12:00:00 GMT",
          "WMF-Last-Access-Global=30-Nov-2024;Path=/;Domain=.wikipedia.org;HttpOnly;secure;Expires=Wed, 01 Jan 2025 12:00:00 GMT",
          "WMF-DP=5b0;Path=/;HttpOnly;secure;Expires=Sun, 01 Dec 2024 00:00:00 GMT",
          "GeoIP=US:VA:Ashburn:39.05:-77.49:v4; Path=/; secure; Domain=.wikipedia.org",
          "NetworkProbeLimit=0.001;Path=/;Secure;SameSite=Lax;Max-Age=3600"
        ],
```

‍

#### Add language attributes of the `<html>` root element as metadata

The `WAT` metadata now includes the language attributes of the `<html>` element. For example, the root element `<html lang="es-MX">` is stored in the `WAT` file as:

```
"HTML-Metadata": {
"Head": {
    "Metas": [
         {
        "name": "HTML@/lang",
        "content": "en"
         },
```

Details on this change are tracked in [ia-web-commons#35](https://github.com/commoncrawl/ia-web-commons/issues/35).

#### Do not include `<meta itemprop="...">` as metadata

[Schema.org](https://schema.org) annotations in `<meta itemprop="...">` in the `HTML` body are not put as metadata into the `WAT` metadata, cf. [ia-web-commons#40](https://github.com/commoncrawl/ia-web-commons/issues/40).

### Crawling with IPv6

The crawler is now ready to crawl IPv6-only websites. While IPv4 is still preferred, sites which are only available by IPv6 are now visited by our crawler. As a consequence, IPv6 addresses now appear in the crawl data. For example, in the "`WARC-IP-Address"` header or in URLs in the URL indexes.

### Crawler Verification

Our crawler "`CCBot"` is now run on dedicated IP address ranges with reverse DNS. This allows webmasters to verify whether a logged request stems from `CCBot`. Please read our [FAQ](https://commoncrawl.org/faq) for more information.

### Feedback Welcome

We look forward to hearing your thoughts and comments. As ever, please feel free to join the discussions in our [Google Group](https://groups.google.com/g/common-crawl) or in our [Discord server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-004](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-004.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-005](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-005.webp)

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

## Erratum:

## SURT URLs do not properly encode non-UTF-8 percent-encoded characters

Originally reported by:

Tom Morris

[More details](/errata/surt-urls-do-not-properly-encode-non-utf-8-percent-encoded-characters)

When constructing SURT (Sort-friendly URI Reordering Transform) URLs, percent-encoded characters that are not valid UTF-8 sequences were not being correctly handled. This could lead to inconsistencies in URL normalization and sorting, potentially causing incorrect deduplication or retrieval issues in datasets that rely on SURT-based indexing.

[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-006](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-006.svg)](/)

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

[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-007](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e-fig-009](../images/2358-https-commoncrawl-org-blog-december-2024-crawl-a-91ccd29e/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl