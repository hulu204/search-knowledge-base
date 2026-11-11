---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-march-april-and-may-2025'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-march-april-and-may-2025
account: 
origin: en-rss
---
[![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-001](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-001.svg)](/)

[←  Back to Blog](/blog)

May 29, 2025

# Host- and Domain-Level Web Graphs March, April, and May 2025

We are pleased to announce that the Web Graph for May 2025 is now available. The graph consists of 326.8 million nodes and 2.9 billion edges at the host level, and 156.1 million nodes and 2.1 billion edges at the domain level.

[![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-002](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-003](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level Web Graphs based on the crawls of March, April, and May 2025. The crawls used to generate the graphs were [CC-MAIN-2025-13](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-13/index.html), [CC-MAIN-2025-18](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-18/index.html), and [CC-MAIN-2025-21](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-21/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the Web Graph format are given in our collection of [Web Graph Notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics).

## Host-level Graph

The host-level graph consists of 326.8 million nodes and 2.9 billion edges.

There are 267.4 million dangling nodes (81.81%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 41.5 million (12.70%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) and a leading `www.` is stripped: `www.subdomain.example.com` becomes `com.example.subdomain`.

You can download the graph and the ranks of all 326.8 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 36 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl March, April, May 2025 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 2.4 GiB | [cc-main-2025-mar-apr-may-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 12 vertices files |
| 13.4 GiB | [cc-main-2025-mar-apr-may-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 24 edges files |
|  |  |  |
| 6.0 GiB | [cc-main-2025-mar-apr-may-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-mar-apr-may-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host.properties) |  |
|  |  |  |
| 6.5 GiB | [cc-main-2025-mar-apr-may-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2025-mar-apr-may-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host-t.properties) |  |
|  |  |  |
| 815 Bytes | [cc-main-2025-mar-apr-may-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 5.8 GiB | [cc-main-2025-mar-apr-may-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/host/cc-main-2025-mar-apr-may-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [0c4a8de](https://github.com/publicsuffix/list/commit/0c4a8de) of the public suffix list was used (commit date 2025-05-08T00:52:07Z).

The domain-level graph has 156.1 million nodes and 2.1 billion edges. 70.2% or 109.6 million nodes are dangling nodes, the largest strongly connected component covers 35.7 million or 22.88% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/`.

### Download files of the Common Crawl March, April, May 2025 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 1.1 GiB | [cc-main-2025-mar-apr-may-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 8.7 GiB | [cc-main-2025-mar-apr-may-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 4.7 GiB | [cc-main-2025-mar-apr-may-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-mar-apr-may-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain.properties) |  |
|  |  |  |
| 4.9 GiB | [cc-main-2025-mar-apr-may-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2025-mar-apr-may-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain-t.properties) |  |
|  |  |  |
| 793 Bytes | [cc-main-2025-mar-apr-may-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.7 GiB | [cc-main-2025-mar-apr-may-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-mar-apr-may/domain/cc-main-2025-mar-apr-may-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to Paulo Boldi and Sebastiano Vigna, the authors of the [Web Graph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via our [Google Group](https://groups.google.com/g/common-crawl), or on our [Discord server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-004](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-004.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-005](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-005.svg)](/)

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

[![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-006](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-006.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7-fig-008](../images/2343-https-commoncrawl-org-blog-host-and-domain-level-fe7ad2e7/figure-008.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl