---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-november-december-2025-and-january-2026'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-november-december-2025-and-january-2026
account: 
origin: en-rss
---
[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-001](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-001.svg)](/)

[←  Back to Blog](/blog)

January 30, 2026

# Host- and Domain-Level Web Graphs November/December 2025 and January 2026

The latest Web Graphs from the November and December 2025 and January 2026 crawls are now available, comprising 279.4 million host-level nodes with 13.4 billion edges, and 122.3 million domain-level nodes with 6.1 billion edges.

[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-002](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-003](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level Web Graphs based on the crawls of November and December of 2025, and January 2026. The crawls used to generate the graphs were [CC-MAIN-2025-47](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-47/index.html), [CC-MAIN-2025-51](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-51/index.html), and [CC-MAIN-2026-04](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-04/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph Releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the webgraph format are given in our collection of [Web Graph Notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You may also wish to explore our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page for more information on ranking, and our [Index of Web Graph Releases](https://index.commoncrawl.org/web-graphs-index.html).

Important note

Starting with this Web Graph release, the leading `www.` in a host name is preserved. That is, the host name `www.subdomain.example.com` becomes `com.example.subdomain.www` in reverse domain name notation. See the [issue report](https://github.com/commoncrawl/cc-pyspark/issues/56) for further details.

## Host-level Graph

The host-level graph consists of 279.4 million nodes and 13.4 billion edges.

There are 211.2 million dangling nodes (75.60%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 38.9 million (13.92%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation): `www.example.com` becomes `com.example.www`.

You can download the graph and the ranks of all 279.4 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 168 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl November, December, and January 2025-26 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 2.1 GiB | [cc-main-2025-26-nov-dec-jan-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 24 vertices files |
| 58.2 GiB | [cc-main-2025-26-nov-dec-jan-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 144 edges files |
|  |  |  |
| 18.2 GiB | [cc-main-2025-26-nov-dec-jan-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-26-nov-dec-jan-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host.properties) |  |
|  |  |  |
| 18.1 GiB | [cc-main-2025-26-nov-dec-jan-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2025-26-nov-dec-jan-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host-t.properties) |  |
|  |  |  |
| 828 Bytes | [cc-main-2025-26-nov-dec-jan-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 5.2 GiB | [cc-main-2025-26-nov-dec-jan-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/host/cc-main-2025-26-nov-dec-jan-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [2218b36](https://github.com/publicsuffix/list/commit/2218b36) of the public suffix list was used (commit date 2026-01-08T11:50:45Z).

The domain-level graph has 122.3 million nodes and 6.1 billion edges. 62.6% or 76.6 million nodes are dangling nodes, the largest strongly connected component covers 32.4 million or 26.46% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/`.

### Download files of the Common Crawl November, December, and January 2025-26 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 871.5 MiB | [cc-main-2025-26-nov-dec-jan-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 22.5 GiB | [cc-main-2025-26-nov-dec-jan-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 10.9 GiB | [cc-main-2025-26-nov-dec-jan-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-26-nov-dec-jan-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain.properties) |  |
|  |  |  |
| 11.2 GiB | [cc-main-2025-26-nov-dec-jan-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2025-26-nov-dec-jan-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain-t.properties) |  |
|  |  |  |
| 788 Bytes | [cc-main-2025-26-nov-dec-jan-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.2 GiB | [cc-main-2025-26-nov-dec-jan-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/domain/cc-main-2025-26-nov-dec-jan-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via [Common Crawl's Google Group](https://groups.google.com/g/common-crawl), or on our [Discord Server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-004](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-004.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-005](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-005.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-006](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-006.svg)](/)

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

[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-007](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e-fig-009](../images/2319-https-commoncrawl-org-blog-host-and-domain-level-9509c43e/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl