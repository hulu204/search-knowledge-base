---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-may-june-and-july-2025'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-may-june-and-july-2025
account: 
origin: en-rss
---
[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-001](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-001.svg)](/)

[←  Back to Blog](/blog)

July 25, 2025

# Host- and Domain-Level Web Graphs May, June, and July 2025

Our Web Graph release for July 2025 is now available, consisting of 481.6 million nodes and 3.4 billion edges at the host level, and 209.5 million nodes and 2.6 billion edges at the domain level.

[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-002](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-003](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of May, June, and July 2025. The crawls used to generate the graphs were [CC-MAIN-2025-21](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-21/index.html), [CC-MAIN-2025-26](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-26/index.html), and [CC-MAIN-2025-30](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-30/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph Releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the webgraph format are given in our collection of [Web Graph Notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You may also wish to explore our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page for more information on ranking.

## Host-level Graph

The host-level graph consists of 481.6 million nodes and 3.4 billion edges.

There are 422.6 million dangling nodes (87.74%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 41.2 million (8.55%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

‍

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) and a leading `www.` is stripped: `www.subdomain.example.com` becomes `com.example.subdomain`.

You can download the graph and the ranks of all 481.6 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 44 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl May, June, July 2025 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 3.5 GiB | [cc-main-2025-may-jun-jul-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 12 vertices files |
| 15.5 GiB | [cc-main-2025-may-jun-jul-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 32 edges files |
|  |  |  |
| 6.7 GiB | [cc-main-2025-may-jun-jul-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-may-jun-jul-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host.properties) |  |
|  |  |  |
| 7.7 GiB | [cc-main-2025-may-jun-jul-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2025-may-jun-jul-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host-t.properties) |  |
|  |  |  |
| 816 Bytes | [cc-main-2025-may-jun-jul-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 8.5 GiB | [cc-main-2025-may-jun-jul-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/host/cc-main-2025-may-jun-jul-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [968c2cc](https://github.com/publicsuffix/list/commit/968c2cc) of the public suffix list was used (commit date 2025-07-05T07:06:57Z).

The domain-level graph has 209.5 million nodes and 2.6 billion edges. 77.9% or 163.2 million nodes are dangling nodes, the largest strongly connected component covers 35.8 million or 17.08% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/`or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/`.

### Download files of the Common Crawl May, June, July 2025 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 1.4 GiB | [cc-main-2025-may-jun-jul-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 10.0 GiB | [cc-main-2025-may-jun-jul-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 5.2 GiB | [cc-main-2025-may-jun-jul-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-may-jun-jul-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain.properties) |  |
|  |  |  |
| 5.6 GiB | [cc-main-2025-may-jun-jul-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2025-may-jun-jul-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain-t.properties) |  |
|  |  |  |
| 797 Bytes | [cc-main-2025-may-jun-jul-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 3.3 GiB | [cc-main-2025-may-jun-jul-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-may-jun-jul/domain/cc-main-2025-may-jun-jul-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via [Common Crawl's Google Group](https://groups.google.com/g/common-crawl), or on our [Discord Server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-004](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-004.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-005](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-005.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-006](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-006.svg)](/)

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

[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-007](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00-fig-009](../images/2338-https-commoncrawl-org-blog-host-and-domain-level-48cd7b00/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl