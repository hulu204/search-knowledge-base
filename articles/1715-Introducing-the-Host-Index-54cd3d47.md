---
title: 'Introducing the Host Index'
company: CommonCrawl
tag: 索引构建
date: 2025-04-23
url: https://commoncrawl.org/blog/introducing-the-host-index
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

April 23, 2025

# Introducing the Host Index

Introducing the Host Index: a new dataset with one row per web host per crawl, combining crawl stats, status codes, languages, and bot defence data. Queryable via AWS tools or downloadable.

[![Greg Lindahl](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/65550ad52e2cbe00ff53493a_greg.webp)

Greg Lindahl

Greg is Chief Technology Officer at the Common Crawl Foundation.](https://commoncrawl.org/team/greg-lindahl-engineer)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

We are pleased to announce a public test of a new web dataset, the [Host Index](https://github.com/commoncrawl/cc-host-index). Common Crawl has long offered a dataset of crawled web data, along with two indexes that help find individual web pages in the 10-petabyte-sized dataset. We also have the [Web Graph](https://commoncrawl.org/web-graphs), which has information about web hosts and domains – their ranks and their connections to each other.

<https://github.com/commoncrawl/cc-host-index>

The new Host Index has one row for every web host we know about, in each individual crawl. It contains summary information from the crawl, indexes, the web graph, and our raw crawler logs. You can use it directly from AWS using SQL tools such as Amazon Athena or duckdb, or you can download it to your own disk (24 crawls x 7 gigabytes each.)

Here are some highlights from the schema:

* Counts of pages crawled by status code, including successes, redirects, not-found, not-changed, etc.
* Details about robots.txt fetches, which can highlight web hosts using “bot defenses” to refuse all traffic from CCBot
* A summary of languages used on a web host, currently just the number (and percentage) of web pages that are in languages other than English

‍

Here’s a graph of the recent crawl history of our own web host, commoncrawl.org. We revamped our website in 2023, moving many webpages to new places and leaving behind redirects. You can see a big spike in redirected web pages, which took a couple of months to fully finish. This time delay highlights that our crawl is never “complete”. It is a sample of the web.

![A graph of the recent crawl history of our own web host, commoncrawl.org](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/68082baa96d6e63da93656a9_AD_4nXfl6BWnMhLREds41DQTY2ngTpXwAGvvukQD3KIH3VS8nPCpAHxcdMZmTEePH3aCEdtYmzzzUx1p7KO8dQsDW0byzc29UuJ2xceg2YNAZED2sWvHYXsxT9XEaY77fGjX4S99L5Mz1Q.png)

A graph of the recent crawl history of our own web host, commoncrawl.org

Here’s an example of a somewhat particular query, which returns a list of Vatican (`*.va`) web hosts that have more than 50% of their web pages in languages other than English:

```
SELECT
  crawl, surt_host_name, hcrank10, fetch_200_lote_pct, fetch_200_lote
FROM cchost_index_testing_v2
WHERE crawl = 'CC-MAIN-2025-13'
  AND url_host_tld = 'va'
  AND fetch_200_lote_pct > 50
ORDER BY hcrank10 DESC
LIMIT 10
```

For many more details, please see the README in the <https://github.com/commoncrawl/cc-host-index> GitHub repository.

We’re very interested in feedback. Please contact us at [info@commoncrawl.org](mailto:info@commoncrawl.org), or on our [Google Group](https://groups.google.com/g/common-crawl), or our [Discord server](https://discord.com/invite/njaVFh7avF).

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