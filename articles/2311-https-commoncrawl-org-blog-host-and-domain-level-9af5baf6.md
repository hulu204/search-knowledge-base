---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-january-february-and-march-2026'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-january-february-and-march-2026
account: 
origin: en-rss
---
[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-001](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-001.svg)](/)

[←  Back to Blog](/blog)

March 24, 2026

# Host- and Domain-Level Web Graphs January, February, and March 2026

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of January, February, and March 2026. The graphs consist of 270.2 million nodes and 9 billion edges at the host level, and 120 million nodes and 4.4 billion edges at the domain level.

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-002](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-002.webp)

Luca Foppiano

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/luca-foppiano)

![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-003](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of January, February, and March 2026. The crawls used to generate the graphs were [CC-MAIN-2026-04](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-04/index.html), [CC-MAIN-2026-08](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-08/index.html), and [CC-MAIN-2026-12](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph Releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the webgraph format are given in our collection of [Web Graph Notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You may also wish to explore our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page for more information on ranking.

## Host-level Graph

The host-level graph consists of 270.2 million nodes and 9 billion edges.

There are 203.1 million dangling nodes (75.15%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 38.6 million (14.28%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) such that: `www.example.com` becomes `com.example.www`.

You can download the graph and the ranks of all 270.2 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 240 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl January, February, and March 2026 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 2.0 GiB | [cc-main-2026-jan-feb-mar-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 48 vertices files |
| 38.8 GiB | [cc-main-2026-jan-feb-mar-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 192 edges files |
|  |  |  |
| 11.5 GiB | [cc-main-2026-jan-feb-mar-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2026-jan-feb-mar-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host.properties) |  |
|  |  |  |
| 12.0 GiB | [cc-main-2026-jan-feb-mar-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2026-jan-feb-mar-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host-t.properties) |  |
|  |  |  |
| 821 Bytes | [cc-main-2026-jan-feb-mar-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 5.0 GiB | [cc-main-2026-jan-feb-mar-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/host/cc-main-2026-jan-feb-mar-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [ccc3b53](https://github.com/publicsuffix/list/commit/ccc3b53) of the public suffix list was used (commit date 2026-02-27T07:15:11Z).

The domain-level graph has 120 million nodes and 4.4 billion edges. 61.7% or 74 million nodes are dangling nodes, the largest strongly connected component covers 31.5 million or 26.27% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/`.

### Download files of the Common Crawl January, February, and March 2026 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 850.0 MiB | [cc-main-2026-jan-feb-mar-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 16.0 GiB | [cc-main-2026-jan-feb-mar-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 7.7 GiB | [cc-main-2026-jan-feb-mar-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2026-jan-feb-mar-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain.properties) |  |
|  |  |  |
| 7.8 GiB | [cc-main-2026-jan-feb-mar-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2026-jan-feb-mar-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain-t.properties) |  |
|  |  |  |
| 789 Bytes | [cc-main-2026-jan-feb-mar-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.2 GiB | [cc-main-2026-jan-feb-mar-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-jan-feb-mar/domain/cc-main-2026-jan-feb-mar-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via [Common Crawl's Google Group](https://groups.google.com/g/common-crawl), or on our [Discord Server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-004](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-004.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-005](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-005.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-006](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-006.webp)

Hande Çelikkanat](https://commoncrawl.org/team/hande-celikkanat)

Hande is a Senior ML Engineer with the Common Crawl Foundation.

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-007](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-007.webp)

Thijs Dalhuijsen](https://commoncrawl.org/team/thijs-dalhuijsen)

Thijs Dalhuijsen is Engineering Manager at Common Crawl.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-008](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-008.svg)](/)

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

[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-009](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-009.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6-fig-011](../images/2311-https-commoncrawl-org-blog-host-and-domain-level-9af5baf6/figure-011.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl