---
title: 'https://commoncrawl.org/blog/cc-citations-a-visualization-of-research-papers-referencing-common-crawl'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/cc-citations-a-visualization-of-research-papers-referencing-common-crawl
account: 
origin: en-rss
---
[![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-001](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-001.svg)](/)

[←  Back to Blog](/blog)

February 11, 2026

# CC-Citations: A Visualization of Research Papers Referencing Common Crawl

We are proud to release an interactive visualization of thousands of research papers using or citing Common Crawl data.

[![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-002](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-002.webp)

Malte Ostendorff

Malte is a Senior Research Engineer at Common Crawl.](https://commoncrawl.org/team/malte-ostendorff)

![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-003](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-003.webp)

[Thousands of research papers](https://commoncrawl.org/research-papers) mention, use, or cite Common Crawl data, making it difficult to get a meaningful overview from traditional academic search engines like Google Scholar.  To make exploration easier, we built an interactive visualization, available as a [space on Hugging Face](https://huggingface.co/spaces/commoncrawl/cc-citations).

The visualization is implemented as a map-like web application in which 10,000+ research papers are displayed as markers on a map interface.  Users can explore the papers visually by dragging and zooming.  A search bar allows the user to find papers by their titles.

The positions of the papers on the map are defined by their semantic similarity.  Specifically, we use [SciNCL paper embeddings](https://arxiv.org/abs/2202.06671) based on paper titles and abstracts in combination with [UMAP dimensionality reduction](https://arxiv.org/abs/1802.03426).  The different paper topics are visualized with different colors.  For topic detection we use [LDA](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.LatentDirichletAllocation.html) in combination with Anthropic’s Claude to come up with human readable topics.

## Clusters of Research Papers

The visualization provides a clear overview of the research areas directly or indirectly using Common Crawl data.  Some topic clusters dominate, but many others are clearly visible too.  A few examples are listed below:

### Security & Attack Detection

The topic of security and attack detection appears in several areas and clusters in the visualization (displayed in red).  Below are a few examples of papers from this topic:

* [Propaganda in Press: Challenges of Automatic Detection](https://www.fer.unizg.hr/_download/repository/TAR-2020-ProjectReports.pdf#page=61) (Pušelj and Skalec, 2020)
* [A State-of-the-Art Review on Phishing Website Detection Techniques](https://ieeexplore.ieee.org/document/10788671) (Li et al., 2024)
* ‍[From Past to Present: A Survey of Malicious URL Detection Techniques, Datasets and Code Repositories](https://arxiv.org/abs/2504.16449) (Tian et al. 2025)

![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-004](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-004.webp)

Research papers about security & attack detection in several clusters.

### Machine Translation

One isolated topic cluster in the top-right corner is about machine translation research and related topics (displayed in green).  The cluster contains papers like:

* [Findings of the WMT24 General Machine Translation Shared Task: The LLM Era Is Here but MT Is Not Solved Yet](https://aclanthology.org/2024.wmt-1.1/) (Kocmi et al., 2024)
* [On the Language Coverage Bias for Neural Machine Translation](https://arxiv.org/abs/2106.03297) (Wang et al., 2021)
* [Nearest Neighbor Machine Translation](https://arxiv.org/abs/2010.00710) (Khandelwal et al., 2021)

![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-005](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-005.webp)

A cluster of research papers about machine translation.

### Ethics & Governance

At the very center of the map, there is a cluster about ethics and governance.  The cluster contains papers such as [Multidimensional tie strength and economic development](https://www.nature.com/articles/s41598-022-26245-4) (Aiello et al., 2022).

![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-006](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-006.webp)

A cluster of research papers about ethics and governance.

### Other Topics

All research papers that cannot be assigned to a specific topic cluster are highlighted as “Other” (grey color).  For example, [Tracking and Identifying International Propaganda and Influence Networks Online](https://ojs.aaai.org/index.php/AAAI/article/view/35209) (Hanley, 2025) or [Determining How Citations Are Used in Citation Contexts](https://link.springer.com/chapter/10.1007/978-3-030-30760-8_38) (Färber and Sampath, 2019) are part of this cluster.

![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-007](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-007.webp)

Research papers with other topics are scattered throughout the map.

There are many more interesting research papers hidden here.  Please feel free to go and [explore the interactive visualization](https://huggingface.co/spaces/commoncrawl/cc-citations) on your own.

This release was authored by:

No items found.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-008](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-008.svg)](/)

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

[![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-009](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-009.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608-fig-011](../images/2318-https-commoncrawl-org-blog-cc-citations-a-visual-f7a23608/figure-011.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl