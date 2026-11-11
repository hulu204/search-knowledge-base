---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-march-april-and-may-2026'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-march-april-and-may-2026
account: 
origin: en-rss
---
[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-001](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-001.svg)](/)

[←  Back to Blog](/blog)

May 29, 2026

# Host- and Domain-Level Web Graphs March, April, and May 2026

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of March, April, and May 2026. The graphs consist of 262.4 million nodes and 8.1 billion edges at the host level, and 118.8 million nodes and 4.3 billion edges at the domain level.

[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-002](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-002.webp)

Michael Paris

Michael is a Senior Research Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/michael-paris)

![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-003](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of March, April, and May 2026. The crawls used to generate the graphs were [CC-MAIN-2026-12](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-12/index.html), [CC-MAIN-2026-17](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-17/index.html), and [CC-MAIN-2026-21](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-21/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph Releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the webgraph format are given in our collection of [Web Graph Notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You may also wish to explore our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page for more information on ranking.

## Host-level Graph

The host-level graph consists of 262.4 million nodes and 8.1 billion edges.

There are 198.2 million dangling nodes (75.56%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 36.6 million (13.96%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) such that: `www.example.com` becomes `com.example.www`.

You can download the graph and the ranks of all 262.4 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 240 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl March, April, and May 2026 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 1.9 GiB | [cc-main-2026-mar-apr-may-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 48 vertices files |
| 34.9 GiB | [cc-main-2026-mar-apr-may-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 192 edges files |
|  |  |  |
| 10.7 GiB | [cc-main-2026-mar-apr-may-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2026-mar-apr-may-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host.properties) |  |
|  |  |  |
| 11.2 GiB | [cc-main-2026-mar-apr-may-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2026-mar-apr-may-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host-t.properties) |  |
|  |  |  |
| 815 Bytes | [cc-main-2026-mar-apr-may-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 4.8 GiB | [cc-main-2026-mar-apr-may-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/host/cc-main-2026-mar-apr-may-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [8b4345f](https://github.com/publicsuffix/list/commit/8b4345f) of the public suffix list was used (commit date 2026-05-01T02:51:16Z).

The domain-level graph has 118.8 million nodes and 4.3 billion edges. 63.0% or 74.8 million nodes are dangling nodes, the largest strongly connected component covers 30.2 million or 25.46% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/`.

### Download files of the Common Crawl March, April, and May 2026 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 840.0 MiB | [cc-main-2026-mar-apr-may-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 15.4 GiB | [cc-main-2026-mar-apr-may-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 7.2 GiB | [cc-main-2026-mar-apr-may-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2026-mar-apr-may-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain.properties) |  |
|  |  |  |
| 7.4 GiB | [cc-main-2026-mar-apr-may-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2026-mar-apr-may-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain-t.properties) |  |
|  |  |  |
| 788 Bytes | [cc-main-2026-mar-apr-may-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.2 GiB | [cc-main-2026-mar-apr-may-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2026-mar-apr-may/domain/cc-main-2026-mar-apr-may-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via [Common Crawl's Google Group](https://groups.google.com/g/common-crawl), or on our [Discord Server](https://discord.gg/njaVFh7avF).

This release was authored by:

[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-004](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-004.webp)

Michael Paris](https://commoncrawl.org/team/michael-paris)

Michael is a Senior Research Engineer at the Common Crawl Foundation.

[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-005](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-005.webp)

Hande Çelikkanat](https://commoncrawl.org/team/hande-celikkanat)

Hande is a Senior ML Engineer with the Common Crawl Foundation.

[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-006](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-006.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-007](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-007.svg)](/)

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

[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-008](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc-fig-010](../images/2305-https-commoncrawl-org-blog-host-and-domain-level-4a9004fc/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl