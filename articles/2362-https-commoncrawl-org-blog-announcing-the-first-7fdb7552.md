---
title: 'https://commoncrawl.org/blog/announcing-the-first-stable-release-of-cc-downloader'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/announcing-the-first-stable-release-of-cc-downloader
account: 
origin: en-rss
---
[![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-001](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-001.svg)](/)

[←  Back to Blog](/blog)

August 10, 2026

# Announcing the First Stable Release of CC-Downloader

Over a year ago we released cc-downloader, an experimental tool to politely download Common Crawl data. Today we're releasing its first stable version, with a Rust library and Python bindings.

[![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-002](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-002.webp)

Pedro Ortiz Suarez

Pedro is a Principal Research Scientist at the Common Crawl Foundation.](https://commoncrawl.org/team/pedro-ortiz-suarez)

![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-003](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-003.webp)

[Over a year ago](https://commoncrawl.org/blog/introducing-cc-downloader) we released an experimental version of `cc-downloader`, a command-line tool for politely downloading Common Crawl data via HTTPS. We introduced `cc-downloader` in response to a significant increase in downloads and requests for our datasets, which made it harder for many users to successfully access the data in our bucket due to the high traffic.

`cc-downloader`, which was initially meant to be an experimental tool, used a polite retry mechanism that implemented [jitter](https://en.wikipedia.org/wiki/Jitter) and [exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff) strategies to avoid overwhelming our infrastructure. It was also developed in [Rust](https://rust-lang.org/), allowing us to enable parallel downloads easily, while also keeping our tool memory-safe.

Over the course of a year, we monitored the usage of `cc-downloader` and saw significant adoption from the community.

![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-004](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-004.svg)

Number of successful requests made with cc-downloader per month and version, and cc-downloader traffic share in bytes and requests among top 1K User Agents per month.

`cc-downloader` is now one of the top 10 most used clients to download Common Crawl data through CloudFront, accounting for almost 14 PiB downloaded in one and a half years.

|  |  |  |
| --- | --- | --- |
| User Agent Family | Requests (M) | Downloaded (PiB) |
| python-requests | 3027.8 | 138.01 |
| Wget | 272.8 | 73.02 |
| aiohttp | 548.4 | 49.67 |
| Mozilla | 2103.8 | 40.49 |
| aria2 | 403.9 | 29.28 |
| (unknown) | 75.9 | 21.59 |
| Go-http-client | 99.5 | 18.44 |
| curl | 89.8 | 14.32 |
| cc-downloader | 74.9 | 13.83 |
| rclone | 13.4 | 12.22 |
|

Top 10 User Agents by downloaded data from Feb 2025 to Jun 2026.

As such, we decided to completely refactor `cc-downloader`, turning it into a [library](https://crates.io/crates/cc-downloader) with its own [documentation](https://docs.rs/cc-downloader/1.0.1/cc_downloader/). And seeing that `python-requests` is by far the most used client to download our data, we also decided to release [Python bindings](https://pypi.org/project/cc-downloader/), in the hope that this will encourage the community to adopt `cc-downloader` more widely, instead of using potentially impolite implementations of `python-requests`.

Finally, we added support for downloading `contrib` content in our bucket, as well as for filtering the URL index by subset. We also fixed various issues opened by the community over the course of last year, and we completely rewrote the documentation for the standalone binary.

We hope to continue developing and supporting `cc-downloader` in the future, so if you find any issues or would like to submit a feature request, please visit its [GitHub repository](https://github.com/commoncrawl/cc-downloader/), where you will find our new documentation as well as easy instructions to install and start using `cc-downloader` right away.

This release was authored by:

[![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-005](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-005.webp)

Pedro Ortiz Suarez](https://commoncrawl.org/team/pedro-ortiz-suarez)

Pedro is a Principal Research Scientist at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-006](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-006.svg)](/)

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

### [Opt-Out Ledger](https://commoncrawl.org/blog/common-crawl-foundation-opt-out-registry)

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

[![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-007](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552-fig-009](../images/2362-https-commoncrawl-org-blog-announcing-the-first-7fdb7552/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl