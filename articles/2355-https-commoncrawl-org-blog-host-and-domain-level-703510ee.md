---
title: 'https://commoncrawl.org/blog/host--and-domain-level-web-graphs-november-december-2024-and-january-2025'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/host--and-domain-level-web-graphs-november-december-2024-and-january-2025
account: 
origin: en-rss
---
[![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-001](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-001.svg)](/)

[←  Back to Blog](/blog)

February 1, 2025

# Host- and Domain-Level Web Graphs November/December 2024 and January 2025

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of November, December 2024 and January 2025. The host-level graph consists of 277.7 million nodes and 2.7 billion edges, and the domain-level graph has 100.8 million nodes and 1.9 billion edges.

[![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-002](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-003](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-003.webp)

We are pleased to announce a new release of host-level and domain-level web graphs based on the crawls of November, December 2024 and January 2025. The crawls used to generate the graphs were [CC-MAIN-2025-05](https://data.commoncrawl.org/crawl-data/CC-MAIN-2025-05/index.html), [CC-MAIN-2024-51](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-51/index.html), and [CC-MAIN-2024-46](https://data.commoncrawl.org/crawl-data/CC-MAIN-2024-46/index.html). Additional information about the data formats, the processing pipeline, our objectives, and credits can be found in the announcements of prior [Web Graph releases](https://commoncrawl.org/search?query=webgraph). You may also visit the projects [cc-webgraph](https://github.com/commoncrawl/cc-webgraph) and [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) which include all scripts and tools required to construct the graphs. Instructions to explore the graphs in the WebGraph format are given in our collection of [Web Graph notebooks](https://github.com/commoncrawl/cc-notebooks/tree/master/cc-webgraph-statistics). You can also explore statistics for this and all previous releases on our [Web Graph Statistics](https://commoncrawl.github.io/cc-webgraph-statistics/) page.

## Host-level Graph

The host-level graph consists of 277.7 million nodes and 2.7 billion edges.

There are 217.6 million dangling nodes (78.36%) and the largest [strongly connected component](https://en.wikipedia.org/wiki/Strongly_connected_component) contains 40.8 million (14.70%) nodes. Dangling nodes stem from:

* Hosts that have not been crawled, yet are pointed to from a link on a crawled page
* Hosts without any links pointing to a different host name
* Hosts which did only return an error page (eg. `HTTP 404`).

Host names in the graph are in [reverse domain name notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) and a leading www. is stripped: www.subdomain.example.com becomes com.example.subdomain. You can download the graph and the ranks of all 277.7 million hosts from AWS S3 on the path `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/` (this requires an account on AWS). Alternatively, you can use `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/` as prefix to access the files from everywhere.

Please note that the text representation of the host-level graph is shipped in 48 `gzip`-compressed files listed in two path listings - one for the nodes (vertices), one for the edges (arcs). First, download the paths listing and decompress it using `gzip -d` or `gunzip`. By adding the prefix `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line in the path listing you get the list of URLs to download the entire graph.

## Download files of the Common Crawl November, December, January 2024-25 host-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 2.0 GiB | [cc-main-2024-25-nov-dec-jan-host-vertices.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host-vertices.paths.gz) | nodes ⟨id, rev host⟩, paths of 16 vertices files |
| 12.5 GiB | [cc-main-2024-25-nov-dec-jan-host-edges.paths.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host-edges.paths.gz) | edges ⟨from\_id, to\_id⟩, paths of 32 edges files |
|  |  |  |
| 5.6 GiB | [cc-main-2024-25-nov-dec-jan-host.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2024-25-nov-dec-jan-host.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host.properties) |  |
|  |  |  |
| 5.8 GiB | [cc-main-2024-25-nov-dec-jan-host-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host-t.graph) | transpose of the graph (outlinks inverted to inlinks) |
| 1.3 KiB | [cc-main-2024-25-nov-dec-jan-host-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host-t.properties) |  |
|  |  |  |
| 815 Bytes | [cc-main-2024-25-nov-dec-jan-host.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 4.9 GiB | [cc-main-2024-25-nov-dec-jan-host-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/host/cc-main-2024-25-nov-dec-jan-host-ranks.txt.gz) | harmonic centrality and pagerank |

## Domain-level Graph

The domain graph is built by aggregating the host graph on the level of pay-level domains (PLDs) based on the [public suffix list](https://en.wikipedia.org/wiki/Public_Suffix_List) maintained on [publicsuffix.org](https://www.publicsuffix.org/). Version (commit) [d1420f6](https://github.com/publicsuffix/list/commit/d1420f641cf8523ae758342e8b5661287718d33f) of the public suffix list was used (commit date 2025-01-08T11:53:49Z).

The domain-level graph has 100.8 million nodes and 1.9 billion edges. 54.3% or 54.7 million nodes are dangling nodes, the largest strongly connected component covers 34.3 million or 34.04% of the nodes.

All files related to the domain graph are available on AWS S3 under `s3://commoncrawl/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/` or on `https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/`.

### Download files of the Common Crawl November, December, January 2024-25 domain-level Web Graph

| Size | File | Description |
| --- | --- | --- |
| 710.9 MiB | [cc-main-2024-25-nov-dec-jan-domain-vertices.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain-vertices.txt.gz) | nodes ⟨id, rev domain, num hosts⟩ |
| 7.7 GiB | [cc-main-2024-25-nov-dec-jan-domain-edges.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain-edges.txt.gz) | edges ⟨from\_id, to\_id⟩ |
|  |  |  |
| 4.2 GiB | [cc-main-2024-25-nov-dec-jan-domain.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain.graph) | graph in [BVGraph](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/BVGraph.html) format |
| 1.3 KiB | [cc-main-2024-25-nov-dec-jan-domain.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain.properties) |  |
|  |  |  |
| 4.2 GiB | [cc-main-2024-25-nov-dec-jan-domain-t.graph](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain-t.graph) | transpose of the graph |
| 1.3 KiB | [cc-main-2024-25-nov-dec-jan-domain-t.properties](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain-t.properties) |  |
|  |  |  |
| 781 Bytes | [cc-main-2024-25-nov-dec-jan-domain.stats](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain.stats) | [WebGraph statistics](https://webgraph.di.unimi.it/docs/it/unimi/dsi/webgraph/Stats.html) |
|  |  |  |
| 2.0 GiB | [cc-main-2024-25-nov-dec-jan-domain-ranks.txt.gz](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2024-25-nov-dec-jan/domain/cc-main-2024-25-nov-dec-jan-domain-ranks.txt.gz) | harmonic centrality and pagerank |

## Credits

Thanks to the authors of the [WebGraph framework](https://webgraph.di.unimi.it/), whose software made the computation of graph properties and ranks possible. We hope the data will be useful for you to do any kind of research on ranking, graph analysis, link spam detection, etc.

Let us know about your results via our [Discord Server](https://discord.gg/njaVFh7avF), or [Common Crawl's Google Group](https://groups.google.com/g/common-crawl).

This release was authored by:

[![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-004](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-004.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-005](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-005.svg)](/)

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

[![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-006](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-006.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee-fig-008](../images/2355-https-commoncrawl-org-blog-host-and-domain-level-703510ee/figure-008.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl