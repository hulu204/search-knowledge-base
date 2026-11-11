---
title: 'https://commoncrawl.org/blog/announcing-the-whirlwind-tour-of-common-crawls-datasets-using-java'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/announcing-the-whirlwind-tour-of-common-crawls-datasets-using-java
account: 
origin: en-rss
---
[![2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e-fig-001](../images/2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e/figure-001.svg)](/)

[←  Back to Blog](/blog)

February 26, 2026

# Announcing the Whirlwind Tour of Common Crawl's Datasets Using Java

Introducing the second installment in our Whirlwind Tour series, covering crawl structure, index access, and content extraction, giving developers a practical foundation for building Java-based data workflows.

[![2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e-fig-002](../images/2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e/figure-002.webp)

Luca Foppiano

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/luca-foppiano)

![2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e-fig-003](../images/2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e/figure-003.webp)

We are pleased to announce the [Java edition of the Whirlwind Tour of Common Crawl's Datasets](https://github.com/commoncrawl/whirlwind-java), another brief tutorial on interacting with our datasets programmatically, this time using Java.

This is the second Whirlwind Tour in the series following the [Python edition](https://commoncrawl.org/blog/announcing-the-whirlwind-tour-of-common-crawls-datasets-using-python) released in June 2025.

Like the Python Whirlwind Tour, we start from the basics: what the crawl data looks like and how it is stored.  We then demonstrate how to use the two versions of our index to extract content using Java-based tools such as [JWARC](https://github.com/iipc/jwarc/) and [DuckDB](https://duckdb.org/).  By the end of the tour, users will have the foundation they need to start using Common Crawl's data in their own Java projects.

The Java Whirlwind Tour is available through our [GitHub repository](https://github.com/commoncrawl/whirlwind-java).  We welcome feedback and suggestions.  You can get in contact with us via [our contact form](https://commoncrawl.org/contact-us), on [our Discord server](https://discord.gg/njaVFh7avF), or by raising an issue in the repository.

Watch this space for a Rust version of the tour!

This release was authored by:

No items found.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e-fig-004](../images/2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e/figure-004.svg)](/)

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

[![2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e-fig-005](../images/2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e/figure-005.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e-fig-007](../images/2315-https-commoncrawl-org-blog-announcing-the-whirlw-a17d0f0e/figure-007.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl