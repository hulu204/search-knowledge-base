---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-december-2024-and-january-february-2025'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-december-2024-and-january-february-2025
account: 
origin: en-rss
---
[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-001](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-001.svg)](/)

[←  Back to Blog](/blog)

February 25, 2025

# Host- and Domain-Level Web Graphs December 2024 and January/February 2025

Announcing our February 2025 Web Graph release based on the crawls of December 2024 and January/February 2025, consisting of 267.4 million nodes and 2.7 billion edges at the host level, and 106.5 million nodes and 1.9 billion edges at the domain level.

[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-002](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-003](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level Web Graphs based on the crawls of December 2024 and January/February 2025. The crawls used to generate the graphs were [CC-MAIN-2025-08](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-08/index.html), [CC-MAIN-2025-05](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/index.html), and [CC-MAIN-2024-51](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the webgraph format are given in our collection of [Web Graph notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You can also explore statistics for this and previous graph releases on our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page.

## Host-level Graph

The host-level graph consists of 267.4 million nodes and 2.7 billion edges.

There are 207.7 million dangling nodes (77.70%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 40.7 million (15.24%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) and a leading `www.` is stripped: `www.subdomain.example.com` becomes `com.example.subdomain`.

You can download the graph and the ranks of all 267.4 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 48 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl December, January, February 2024-25 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 2.0 GiB | [cc-main-2024-25-dec-jan-feb-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 16 vertices files |
| 12.4 GiB | [cc-main-2024-25-dec-jan-feb-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 32 edges files |
|  |  |  |
| 5.6 GiB | [cc-main-2024-25-dec-jan-feb-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2024-25-dec-jan-feb-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host.properties) |  |
|  |  |  |
| 5.8 GiB | [cc-main-2024-25-dec-jan-feb-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2024-25-dec-jan-feb-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host-t.properties) |  |
|  |  |  |
| 808 Bytes | [cc-main-2024-25-dec-jan-feb-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 4.9 GiB | [cc-main-2024-25-dec-jan-feb-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/host/cc-main-2024-25-dec-jan-feb-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [5421ee7](https://github.com/publicsuffix/list/commit/5421ee7) of the public suffix list was used (commit date 2025-01-31T07:02:08Z).

The domain-level graph has 106.5 million nodes and 1.9 billion edges. 56.9% or 60.5 million nodes are dangling nodes, the largest strongly connected component covers 34.7 million or 32.62% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/`.

### Download files of the Common Crawl December, January, February 2024-25 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 749.2 MiB | [cc-main-2024-25-dec-jan-feb-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 7.8 GiB | [cc-main-2024-25-dec-jan-feb-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 4.3 GiB | [cc-main-2024-25-dec-jan-feb-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2024-25-dec-jan-feb-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain.properties) |  |
|  |  |  |
| 4.3 GiB | [cc-main-2024-25-dec-jan-feb-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2024-25-dec-jan-feb-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain-t.properties) |  |
|  |  |  |
| 779 Bytes | [cc-main-2024-25-dec-jan-feb-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.1 GiB | [cc-main-2024-25-dec-jan-feb-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-dec-jan-feb/domain/cc-main-2024-25-dec-jan-feb-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via [our Google Group](https://groups.google.com/g/common-crawl) or on our [Discord server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-004](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-004.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-005](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-005.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-006](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-006.svg)](/)

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

[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-007](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece-fig-009](../images/2352-https-commoncrawl-org-blog-host-and-domain-level-235c0ece/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl