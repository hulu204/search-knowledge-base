---
title: 'https://commoncrawl.org/blog/announcing-gneissweb-annotations'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/announcing-gneissweb-annotations
account: 
origin: en-rss
---
[![2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446-fig-001](../images/2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446/figure-001.svg)](/)

[←  Back to Blog](/blog)

October 6, 2025

# Announcing GneissWeb Annotations

Common Crawl has added IBM’s GneissWeb quality and category annotations to its web dataset, enabling users to filter high-quality content and explore topics like medical, education, and technology.

[![2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446-fig-002](../images/2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446/figure-002.svg)

Common Crawl Foundation

Common Crawl builds and maintains an open repository of web crawl data that can be accessed and analyzed by anyone.](https://commoncrawl.org/)

![2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446-fig-003](../images/2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446/figure-003.webp)

Earlier this year, IBM Research published [the GneissWeb dataset](https://huggingface.co/datasets/ibm-granite/GneissWeb), a state-of-the-art, well-tested recipe for evaluating web document quality and document categories for AI model training. We, at Common Crawl, were excited about the possibility of making these document annotations accessible to users of our web dataset, whether they be large language models (LLM) or machine learning (ML) trainers, or humanities scholars.

Using the GneissWeb bloom filter made publicly available by IBM, along with IBM’s Data Prep Kit (now a Linux Foundation AI & Data project) and the GneissWeb groups’ category classifiers, we were able to create an annotation for every document (URL) in our crawls. If you think of the index as a table with one row for every URL in the dataset, the annotation allows a user of our crawl to pick out a subset of documents that passes GneissWeb’s quality standard. GneissWeb also creates category labels (including medical, education, technology, and science). These can be combined with existing document annotations, such as a language, or a top-level domain (`*.uk` = United Kingdom).

In addition to our URL index, Common Crawl also publishes a host index. The host index allows our dataset users to select web hosts that are “mostly in English” or “have an above-average search-engine style rank”. We have created a GneissWeb-based host annotation, such that a dataset user could look at all web hosts where more than half of the GneissWeb high-quality pages are categorized as medical.

GneissWeb signals could also be used to examine hosts with a high search-engine style rank but low GneissWeb score, and vice versa. This capability opens a lot of opportunities to improve the quality of labels and ranks.

These annotations, at the URL and host level, are available both on the Hugging Face website, and in Common Crawl’s S3 bucket.

We are looking forward to the community at large using these quality annotations and categories to advance AI/ML training and humanities uses in an open and responsible way.

<https://github.com/commoncrawl/cc-index-annotations>

[‍](https://github.com/commoncrawl/cc-index-annotations)‍<https://huggingface.co/datasets/commoncrawl/gneissweb-annotation-url-testing-v1>

[‍](https://huggingface.co/datasets/commoncrawl/gneissweb-annotation-url-testing-v1)‍<https://huggingface.co/datasets/commoncrawl/gneissweb-annotation-host-testing-v1>

## References

<https://arxiv.org/abs/2502.14907>

<https://research.ibm.com/blog/gneissweb-for-granite-training>

<https://huggingface.co/ibm-granite/GneissWeb.bloom>

<https://github.com/data-prep-kit/data-prep-kit>

<https://github.com/data-prep-kit/data-prep-kit/blob/dev/recipes/GneissWeb/GneissWeb.ipynb>

This release was authored by:

No items found.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446-fig-004](../images/2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446/figure-004.svg)](/)

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

[![2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446-fig-005](../images/2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446/figure-005.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446-fig-007](../images/2330-https-commoncrawl-org-blog-announcing-gneissweb-40dc8446/figure-007.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl