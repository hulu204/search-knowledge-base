---
title: 'Web Graph Embeddings: An Experimental Dataset Release'
company: CommonCrawl
tag: 召回
date: 2026-09-07
url: https://commoncrawl.org/blog/web-graph-embeddings-an-experimental-dataset-release
account: 
origin: en-rss
---
[![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-001](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-001.svg)](/)

[←  Back to Blog](/blog)

September 7, 2026

# Web Graph Embeddings: An Experimental Dataset Release

We are publishing an experimental dataset of graph embeddings built from the Common Crawl Web Graph: a 128-dimensional vector for each of 52.9 million web hosts, learned from hyperlinks alone, along with two interactive Hugging Face Spaces.

[![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-002](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-002.webp)

Malte Ostendorff

Malte is a Senior Research Engineer at Common Crawl.](https://commoncrawl.org/team/malte-ostendorff)

![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-003](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-003.webp)

We are releasing the first machine learning embeddings built from the Common Crawl Web Graph: a 128-dimensional vector for each of **52.9 million web hosts**, learned from hyperlinks alone. The dataset is available now on our [S3 bucket](https://data.commoncrawl.org/projects/web-graph-embeddings-testing/index.html) and the [Hugging Face hub](https://huggingface.co/datasets/commoncrawl/web-graph-embeddings), along with two interactive Spaces [[1]](https://huggingface.co/spaces/commoncrawl/web-graph-embeddings), [[2]](https://huggingface.co/spaces/commoncrawl/web-graph-knn) for exploring it and the [source code to reproduce](https://github.com/commoncrawl/web-graph-embeddings) it is on GitHub.

Alongside the crawl archives, we publish every month a Web Graph dataset: a map of which sites link to which other sites. Every hyperlink between two pages becomes an edge, and those edges are aggregated up to the host and domain level. We released our first in-house Web Graph in [May 2017](https://commoncrawl.org/blog/hostgraph-2017-feb-mar-apr-crawls) and have published new graphs at regular intervals ever since, each built from a three-month window of crawls.

What the graph has never come with is a ready-to-use numerical representation for machine learning and AI use cases. That is what we release today as an experiment.

## Why embeddings?

An **embedding** turns an item (e.g.,  a word, an image, a website) into a short list of numbers (i.e., a vector), in a way that puts similar things close together. That sounds modest, but it is the input format almost all modern machine learning actually consumes. Once a website is a vector, you can:

* **find similar sites** by looking for nearby vectors
* **train a classifier** on a small number of labelled examples and apply it to millions
* **cluster** the web into groups without deciding the categories in advance
* **feed the vector into a larger model** as one signal among many

Embeddings of *text* are everywhere. Embeddings of the *web's link structure* are much rarer, mostly because computing them at web scale is difficult. That is the gap this release fills.

## What a graph embedding is

Imagine placing every website as a dot on a vast sheet of paper, using only links between sites as a guide. Sites that link to each other are pulled closer together, whereas sites not connected by links are pushed apart.

Across hundreds of millions of links, patterns emerge without any explicit labels. News sites cluster together, national webs form regional groups, and tightly connected spam networks become dense knots.

A graph embedding captures this structure numerically. Instead of two coordinates on a page, each site receives 128 numbers describing its position in the Web Graph. The closer two sites are in this space, the more similar their roles or connections tend to be.

![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-004](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-004.webp)

Representation learning converts the Web link graph into an embedding space.

## A first experiment with the Common Crawl Web Graph

We started from the host-level graph for the [November 2025, December 2025 and January 2026 crawls](https://data.commoncrawl.org/projects/hyperlinkgraph/cc-main-2025-26-nov-dec-jan/index.html): **279.4 million hosts and about 13.4 billion links**.

Training on every host is both expensive and wasteful, because the great majority of hosts have almost no links, and a site with one link has almost no structure to learn from. So we trained on hosts with at least eight links in total. That keeps **52.9 million hosts (19% of all hosts) but 97.3% of all the links**. Nearly all of the structure survives, while most of the near-empty nodes do not.

From there the model is deliberately simple. Each host gets 128 numbers. The model repeatedly looks at a real link and 50 randomly chosen non-links, and adjusts the numbers so real links score higher than random pairs. There is no page text, no metadata, not even the hostname, i.e., the model only ever sees anonymous node numbers and the links between them.

Training with [NVIDIA’s cuGraph framework](https://github.com/rapidsai/cugraph-gnn) took **approx. 1 hour on four H100 GPUs**, processing about 9.7 million links per second. The result is a table of 52.9 million rows by 128 columns and additional metadata, published as Parquet files in half precision (13.5 GB).

The whole pipeline from downloading and preparation of the raw graph data over training the model to exporting is public on [GitHub](https://github.com/commoncrawl/web-graph-embeddings).

## Explore it in your browser

For machine learning use cases you can download all the embeddings from S3 or Hugging Face. However, if you just want to get a feel for the data, you can explore them in two interactive Spaces on Hugging Face:

![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-005](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-005.webp)

Screenshot of the interactive 2D viewer of the graph embeddings allowing you to visually explore the embedding space.

The [2D map viewer](https://huggingface.co/spaces/commoncrawl/web-graph-embeddings)  projects all 52.9 million hosts onto a two dimensional plane you can pan and zoom, streamed tile by tile as you explore. Hover over any point to see which host it is. The same layout can be recoloured by link count, topic, language or content quality labels.

The screenshot above is coloured by language, and it makes the point better than any table: the model was never shown a single word of text, yet English (blue) and Chinese (red) sites separate into their own territories, with German, Japanese and other languages forming their own regions. That separation comes purely from the fact that sites tend to link to other sites in the same language.

The [nearest-neighbour search](https://huggingface.co/spaces/commoncrawl/web-graph-knn) answers the more direct question: type in a hostname, and get back the sites closest to it in the full 128-dimensional space. It is the quickest way to judge the data for yourself: try a site you know well and see whether its neighbours look right. Note that for hubs the nearest neighbors are rather noisy.

## What the embeddings capture

The model is trained only to predict links, so everything it learns and encodes about websites is a side effect. We measured how much of that side effect is actually useful.

**Topic prediction works well.** A simple classifier trained on the vectors sorts sites into 24 topic categories with a macro-F1 of **0.38**, against **0.06** for guessing from the top-level domain (~6x better).

**Language identification requires enough links.** Overall accuracy for identifying a site's language among 120 language candidates is **0.67**. But the number that matters is how it varies with how well-connected a site is:

|  |  |
| --- | --- |
| Links a site has | Language identified correctly |
| 8–16 | 61% |
| 128–512 | 74% |
| 512–4,096 | 92% |
| More than 4,096 | 98% |

For a well-connected site, the link graph alone identifies its language almost perfectly. Note that for the evaluation we do not compare against a ground-truth (like [CommonLID](https://commonlid.org/)) but against the prediction of our [production language identification model](https://github.com/commoncrawl/language-detection-cld2). Furthermore, the scores are heavily skewed towards high resource languages such as English or Chinese.

**Spam detection gains a genuinely new signal.** A common link-based method here is [Anti-TrustRank](http://i.stanford.edu/~kvijay/krishnan-raj-airweb06.pdf), which works by guilt-by-association: sites linking toward known spam get flagged. Our embeddings turn out to be measuring something different, since the statistical correlation between the two scores from embeddings and Anti-TrustRank is essentially zero. That independence is what makes them useful together: Our evaluations show that the graph embeddings perform especially well on hard spam cases where Anti-TrustRank fails. However, Anti-TrustRank remains the better raw ranker across the easy majority of the web.

## Limitations

This is a first experiment and is yet to be seen whether we will publish graph embeddings on a regular basis. Also, there are several limitations that we want to address in future:

* **Link direction is ignored.** The Web Graph is directed but the embedding model treats every link as a two-way street. Direction matters for spam and authority in particular, and recovering it is the most obvious next improvement.
* **Only a single snapshot.** The embeddings come from a single three-month graph release but our archive has more than 50 graph releases over the last 9 years.
* **A simple shallow model.** Each host’s vector is learned in isolation, without pooling information from its neighbours. More sophisticated model architectures score better on some of the tasks above but are more difficult to scale to the full Web Graph.

## Your feedback is needed

We are publishing this as an experimental release because we think a public, reproducible link-graph embedding is a useful thing for the research community to have.

If you use the dataset, we would like to hear what worked and what did not. If you find a limitation we missed, we would like to know that too. Contributions to the [code](https://github.com/commoncrawl/web-graph-embeddings) are welcome, as are suggestions for what a next version should do differently, e.g., direction-aware training and multiple crawl windows are at the top of our own list.

You can reach us through our [Google Group](https://groups.google.com/g/common-crawl), [Discord](https://discord.gg/njaVFh7avF), or on the dataset's [Hugging Face discussion page](https://huggingface.co/datasets/commoncrawl/web-graph-embeddings/discussions), or by opening an issue on [GitHub](https://github.com/commoncrawl/web-graph-embeddings).

This release was authored by:

[![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-006](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-006.webp)

Malte Ostendorff](https://commoncrawl.org/team/malte-ostendorff)

Malte is a Senior Research Engineer at Common Crawl.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-007](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-007.svg)](/)

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

### [Opt-Out Ledger](https://commoncrawl.org/blog/common-crawl-foundation-opt-out-registry)

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

[![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-008](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617-fig-010](../images/2510-Web-Graph-Embeddings-An-Experimental-Dataset-Rel-40a2b617/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl