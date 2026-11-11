---
title: 'Web Archiving File Formats Explained'
company: CommonCrawl
tag: 工程相关
date: 2024-03-01
url: https://commoncrawl.org/blog/web-archiving-file-formats-explained
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

March 1, 2024

# Web Archiving File Formats Explained

In the ever–evolving landscape of digital archiving and data analysis, it is helpful to understand the various file formats used for web crawling. From the early ARC format to the more advanced WARC, and the specialised WET and WAT files, each plays an important role in the field of web archiving. In this post, we explain these formats, exploring their unique features, applications, and the enhancements they offer.

[![Thom Vaughan](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/69a085daa014334c437fefb3_thom-hires.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64e634cbee339bea89485d24_analysis.webp)

Editor's note

This post predates the renaming of the "Columnar Index" to the "URL Index". References below to the "columnar index" refer to what is now called the URL Index.

‍

## The Capabilities of ARC, WARC, WET, and WAT Formats

In the ever–evolving landscape of digital archiving and data analysis, it is helpful to understand the various file formats used for web crawling.  From the early ARC format to the more advanced WARC, and the specialised WET and WAT files, each plays an important role in the field of web archiving. In this post, we explain these formats, exploring their unique features, applications, and the enhancements they offer.

We also highlight the integration of [Apache Parquet™](https://parquet.apache.org/) for efficient indexing and data analysis, offering insights into how these technologies can refine the process of web data management.

Whether you're a data scientist, a digital archivist, or just interested in the complexities of web archiving, hopefully you will find this post helpful and informative.

## Which Format Does What?

### WARC (Web ARChive) Format

[WARC](https://iipc.github.io/warc-specifications/specifications/warc-format/warc-1.0/) was developed as a successor to the ARC format (detailed below), and is now the industry standard for web archiving.  It can store multiple resources, similar to ARC, but with more capabilities.  This includes the ability to store request and response headers, additional metadata, and new record types like resource revisit, metadata, and conversion.

Enhanced capability for metadata storage, better scalability, and standardization are among its advantages.  It's more suitable for large–scale web archiving and supports the archiving of complex digital resources.  Common Crawl has used WARC since the crawl of Summer 2013 ([CC-MAIN-2013-20](https://data.commoncrawl.org/crawl-data/CC-MAIN-2013-20/index.html)).

To process this data there are various packages available to use, such as <https://github.com/webrecorder/warcio>, <https://pkg.go.dev/github.com/slyrz/warc>, and <https://docs.rs/warc/latest/warc/>.

##### Example Data

Here’s a [Gist](https://gist.github.com/pjox/4de9fb8962b715fe73bbe09d70b2e94e?h=1#file-saturn-warc) that shows an example of a WARC record.

### WAT (Web ARChive Timestamp) Files

These files are also part of the Common Crawl dataset, but they focus on the metadata associated with the crawled web pages.

WAT files contain parsed data from the HTTP response headers, links extracted from HTML pages, and other metadata.  This can include information like server response codes, content types, languages, and more.

They are useful for analysis that requires understanding the structure of the web, such as link analysis, studying the evolution of websites, and metadata–based research.

##### Example Data

Here’s a [Gist](https://gist.github.com/pjox/4de9fb8962b715fe73bbe09d70b2e94e?h=1#file-saturn-pretty-wat) showing an example of a WAT file.

### WET (WARC Encapsulated Text) Files

These files are part of the Common Crawl dataset and contain extracted plain text from web content.  WET files only contain the body text of web pages, extracted from the HTML and excluding any HTML code, images, or other media.  This makes them useful for text analysis and natural language processing (NLP) tasks.

WET files are ideal for applications where only the text of web pages is needed, such as linguistic analysis, content categorisation, and other text–focused activities.

##### Example Data

Here’s [an example of a WET file](https://gist.githubusercontent.com/pjox/4de9fb8962b715fe73bbe09d70b2e94e/raw/9cde1229cf9cd18b12a6c87ad43f36f7bdc996c4/saturn.wet) from the same Gist as the previous two examples.

### Columnar (Parquet) Indexes

In addition to the above, we provide an index for WARC files and URLs in a columnar format using [Apache Parquet™](https://parquet.apache.org/).  This enables more efficient querying and data analysis.

Parquet files are binary files, and their columnar storage is optimised for fast retrieval of specific columns of data, which can significantly speed up searches and analysis.  This means there's no need to process entire WARC segments just to retrieve a specific column.

Other advantages include being able to split files into smaller, manageable chunks that can be processed in parallel across multiple nodes or machines in a distributed computing environment, and schema evolution, meaning that you can easily add new columns to your dataset or change the data types of existing columns without having to rewrite or modify the entire dataset.

You can find plenty of [Use Cases](https://commoncrawl.org/use-cases) and [Example Projects](https://commoncrawl.org/examples) on our website and on [our GitHub](https://github.com/commoncrawl) to help you get started.

Commonly used software for working with the columnar index includes [DataFusion](https://arrow.apache.org/datafusion/), [Pandas](https://pandas.pydata.org/), [PyArrow](https://arrow.apache.org/docs/python/index.html), [Polars](https://pola.rs/), and [parquet-go](https://github.com/xitongsys/parquet-go).

##### Example Data

### ARC (Archive) Format

Originally developed by the Internet Archive, ARC was one of the first file formats used for storing web crawls.  Common Crawl's initial crawls (up to Summer 2013) are in this format. It encapsulates multiple resources (like HTML documents) into a single file.  Each item is preceded by a header containing metadata such as URL, timestamp, content type, and so on.

The ARC format has limitations in handling metadata and scalability.  It lacks flexibility in documenting additional metadata, and doesn't support the storage of data beyond the actual content, such as HTTP request and response headers.  Because of these limitations, as of Summer 2013 we now use the more suitable WARC format.

##### Example Data

Here’s a [Gist](https://gist.githubusercontent.com/pjox/4de9fb8962b715fe73bbe09d70b2e94e/raw/dd02d05261b6a62c87d6bc5a4ecd2a6dc2d9a2f4/swindon.arc) containing an example of an ARC record taken from our CC-MAIN-2009-2010 crawl (which was the last of our crawls to be in this format).

## Summary

ARC and WARC are more general formats for web archiving with WARC being an advanced and more versatile evolution of ARC.  WET and WAT are specialised formats, focusing respectively on the extracted text and the metadata of web content.

The combination of archive formats and Parquet for indexing exemplifies how we use different technologies to enhance the efficiency and effectiveness of web data processing and analysis.

If you have any comments or would like to submit your project to our examples and use cases please [Contact Us](https://commoncrawl.org/contact-us), or join in the discussion in our [Google Group](https://groups.google.com/g/common-crawl).

Apache Parquet™ is a trademark of the Apache Software Foundation.

This release was authored by:

[![Thom is Principal Engineer at the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/69a085daa014334c437fefb3_thom-hires.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![Pedro is a Principal Research Scientist at the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/68ade5c6ef12425101705c61_pedro.webp)

Pedro Ortiz Suarez](https://commoncrawl.org/team/pedro-ortiz-suarez)

Pedro is a Principal Research Scientist at the Common Crawl Foundation.

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