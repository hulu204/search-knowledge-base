---
title: 'The Columnar Index Is Now the URL Index'
company: CommonCrawl
tag: 索引构建
date: 2026-06-03
url: https://commoncrawl.org/blog/the-columnar-index-is-now-the-url-index
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

June 3, 2026

# The Columnar Index Is Now the URL Index

We have renamed the Columnar Index to the URL Index, to be clearer about its purpose and to pave the way for more datasets in a columnar format.

[![Common Crawl Foundation](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64e1481c88168f56d3a58898_648de3e6dfa993c0af776fcf_Common_Crawl_Rev3_LPX_Color%20Icon.svg)

Common Crawl Foundation

Common Crawl builds and maintains an open repository of web crawl data that can be accessed and analyzed by anyone.](https://commoncrawl.org/)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

Today we have renamed the Columnar Index to the [**URL Index**](https://commoncrawl.org/url-index).

The URL Index (formerly the Columnar Index) is one of the indexes we provide for querying the Common Crawl corpus, alongside the [**CDXJ Index**](https://commoncrawl.org/cdxj-index).  As its new name makes clear, it is an index to the URLs and WARC files in the corpus, stored in a columnar format (Apache Parquet™).  That format is well suited to efficient analytical and bulk queries, saving both time and computing resources, and it works with a wide range of tools including AWS Athena, Apache Spark™, Pandas, Polars, Apache Arrow™, and DuckDB.

Why the change?  The old name described *how* the index was stored rather than *what* it contained. "Columnar" refers to the file format, but it told you nothing about the actual purpose of the dataset, which is indexing URLs.  As we aim to publish more of our datasets in columnar formats, naming a single dataset after the format it happens to use would only become more confusing.  A future where several different datasets are all "columnar" needs names that distinguish them by what they are for.  Calling this one the URL Index does exactly that.

Nothing else has changed.  The data, the schema, the S3 location, and the way you query it all remain the same.  You will still find the files at `s3://commoncrawl/cc-index/table/cc-main/warc/`, and your existing queries will continue to work without modification.  This is purely a renaming to make the index clearer in purpose and to leave room for the datasets to come.

This release was authored by:

No items found.

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