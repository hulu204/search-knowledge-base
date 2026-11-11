---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-september-october-and-november-2025'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-september-october-and-november-2025
account: 
origin: en-rss
---
[![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-001](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-001.svg)](/)

[←  Back to Blog](/blog)

November 24, 2025

# Host- and Domain-Level Web Graphs September, October, and November 2025

We are pleased to announce the release of the web graphs based on the crawls of September, October, and November of 2025, consisting of 235.7 million nodes and 9.5 billion edges at the host level, and 100.7 million nodes and 6.6 billion edges at the domain level.

[![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-002](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-002.webp)

Malte Ostendorff

Malte is a Senior Research Engineer at Common Crawl.](https://commoncrawl.org/team/malte-ostendorff)

![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-003](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of September, October, and November 2025. The crawls used to generate the graphs were [CC-MAIN-2025-38](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-38/index.html), [CC-MAIN-2025-43](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-43/index.html), and [CC-MAIN-2025-47](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-47/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph Releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the webgraph format are given in our collection of [Web Graph Notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You may also wish to explore our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page for more information on ranking.

## Host-level Graph

The host-level graph consists of 235.7 million nodes and 9.5 billion edges.

There are 177.5 million dangling nodes (75.33%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 37.3 million (15.85%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) and a leading `www.` is stripped: `www.subdomain.example.com` becomes `com.example.subdomain`.

You can download the graph and the ranks of all 235.7 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 64 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl September, October, and November 2025 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 1.8 GiB | [cc-main-2025-sep-oct-nov-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 16 vertices files |
| 41.4 GiB | [cc-main-2025-sep-oct-nov-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 48 edges files |
|  |  |  |
| 14.9 GiB | [cc-main-2025-sep-oct-nov-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-sep-oct-nov-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host.properties) |  |
|  |  |  |
| 15.3 GiB | [cc-main-2025-sep-oct-nov-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2025-sep-oct-nov-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host-t.properties) |  |
|  |  |  |
| 818 Bytes | [cc-main-2025-sep-oct-nov-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 4.6 GiB | [cc-main-2025-sep-oct-nov-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/host/cc-main-2025-sep-oct-nov-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [8e3b7b7](https://github.com/publicsuffix/list/commit/8e3b7b7) of the public suffix list was used (commit date 2025-10-29T17:39:13Z).

The domain-level graph has 100.7 million nodes and 6.6 billion edges. 54.2% or 54.6 million nodes are dangling nodes, the largest strongly connected component covers 32.1 million or 31.89% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/`or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/`.

### Download files of the Common Crawl September, October, and November 2025 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 704.8 MiB | [cc-main-2025-sep-oct-nov-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 23.2 GiB | [cc-main-2025-sep-oct-nov-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 10.9 GiB | [cc-main-2025-sep-oct-nov-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2025-sep-oct-nov-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain.properties) |  |
|  |  |  |
| 11.0 GiB | [cc-main-2025-sep-oct-nov-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2025-sep-oct-nov-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain-t.properties) |  |
|  |  |  |
| 790 Bytes | [cc-main-2025-sep-oct-nov-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.0 GiB | [cc-main-2025-sep-oct-nov-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-sep-oct-nov/domain/cc-main-2025-sep-oct-nov-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via [Common Crawl's Google Group](https://groups.google.com/g/common-crawl), or on our [Discord Server](https://discord.gg/njaVFh7avF).

‍

This release was authored by:

[![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-004](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-004.webp)

Malte Ostendorff](https://commoncrawl.org/team/malte-ostendorff)

Malte is a Senior Research Engineer at Common Crawl.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-005](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-005.svg)](/)

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

[![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-006](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-006.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a-fig-008](../images/2325-https-commoncrawl-org-blog-host-and-domain-level-3032762a/figure-008.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl