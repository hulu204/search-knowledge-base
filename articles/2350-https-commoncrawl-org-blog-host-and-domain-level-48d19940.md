---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-january-february-and-march-2025'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-january-february-and-march-2025
account: 
origin: en-rss
---
[![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-001](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-001.svg)](/)

[←  Back to Blog](/blog)

April 1, 2025

# Host- and Domain-Level Web Graphs January, February, and March 2025

We are pleased to announce a new release of host-level and domain-level Web Graphs based on the crawls of January, February, and March 2025.

[![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-002](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-003](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level Web Graphs based on the crawls of January, February, and March 2025. The crawls used to generate the graphs were [CC-MAIN-2025-13](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-13/index.html), [CC-MAIN-2025-08](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-08/index.html), and [CC-MAIN-2025-05](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the WebGraph format are given in our collection of [Web Graph notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics).

You can also explore statistics for this and previous graph releases on our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page.

## Host-Level Graph

The host-level graph consists of 293.3 million nodes and 2.8 billion edges.

There are 233.2 million dangling nodes (79.51%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 42.0 million (14.32%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) and a leading www. is stripped: www.subdomain.example.com becomes com.example.subdomain.

You can download the graph and the ranks of all 293.3 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 36 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download Files of the Common Crawl January, February, March 2025 Host-Level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 2.2 GiB | [cc-main-2025-jan-feb-mar-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 12 vertices files |
| 12.8 GiB | [cc-main-2025-jan-feb-mar-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 24 edges files |
|  |  |  |
| 5.8 GiB | [cc-main-2025-jan-feb-mar-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-jan-feb-mar-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host.properties) |  |
|  |  |  |
| 6.1 GiB | [cc-main-2025-jan-feb-mar-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2025-jan-feb-mar-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host-t.properties) |  |
|  |  |  |
| 814 Bytes | [cc-main-2025-jan-feb-mar-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 5.3 GiB | [cc-main-2025-jan-feb-mar-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/host/cc-main-2025-jan-feb-mar-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-Level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [76dbfca](https://github.com/publicsuffix/list/commit/76dbfca) of the public suffix list was used (commit date 2025-03-06T21:52:52Z).

The domain-level graph has 135.2 million nodes and 2.0 billion edges. 65.6% or 88.7 million nodes are dangling nodes, the largest strongly connected component covers 36.1 million or 26.71% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/`.

### Download Files of the Common Crawl January, February, March 2025 Domain-Level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 941.1 MiB | [cc-main-2025-jan-feb-mar-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 8.3 GiB | [cc-main-2025-jan-feb-mar-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 4.6 GiB | [cc-main-2025-jan-feb-mar-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-jan-feb-mar-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain.properties) |  |
|  |  |  |
| 4.6 GiB | [cc-main-2025-jan-feb-mar-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2025-jan-feb-mar-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain-t.properties) |  |
|  |  |  |
| 789 Bytes | [cc-main-2025-jan-feb-mar-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.4 GiB | [cc-main-2025-jan-feb-mar-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-jan-feb-mar/domain/cc-main-2025-jan-feb-mar-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via our [Discord server](https://discord.gg/njaVFh7avF), or our [Google Group](https://groups.google.com/g/common-crawl)!

This release was authored by:

[![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-004](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-004.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-005](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-005.svg)](/)

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

[![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-006](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-006.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940-fig-008](../images/2350-https-commoncrawl-org-blog-host-and-domain-level-48d19940/figure-008.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl