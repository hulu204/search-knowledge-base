---
title: 'The Common Crawl Foundation at the TPDL Conference'
company: CommonCrawl
tag: 爬虫抓取
date: 2026-10-12
url: https://commoncrawl.org/blog/the-common-crawl-foundation-at-the-tpdl-conference
account: 
origin: en-rss
---
[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-001](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-001.svg)](/)

[←  Back to Blog](/blog)

October 12, 2026

# The Common Crawl Foundation at the TPDL Conference

The Common Crawl Foundation participated in the 30th TPDL (Theory and Practice for Digital Archives) conference in Faro, Portugal presenting two contributions on Crawl theory and on archival data enrichment.

[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-002](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-002.webp)

Michael Paris

Michael is a Senior Research Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/michael-paris)

![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-003](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-003.webp)

The Common Crawl Foundation participated at the 30th International Conference on Theory and Practice of Digital Libraries (TPDL 2026) in Faro, Portugal, from 22nd to 25th of September.

The conference was hosted by the University of Algarve at its Penha Campus, on the edge of the Ria Formosa Natural Park. The programme opened with a day of workshops and a doctoral consortium, followed by three main conference days of keynotes, eight paper sessions, and a dedicated demo session.

On the 23rd of September, Michael Paris presented the "Measuring What the Crawler Sees: Discovery Curves, Core Persistence, and Shell Dynamics in Longitudinal Web Crawls", co-authored with Hande Çelikkanat and Luca Foppiano, in the session on “Studying the Research Landscape: Scientometrics and Meta-Research”. The preprint is available on [arXiv](https://arxiv.org/abs/2607.13636). The data used for this work is published in the [Common Crawl Statistics](https://commoncrawl.github.io/cc-crawl-statistics/).

Measuring What the Crawler Sees: Discovery Curves, Core Persistence, and Shell Dynamics in Longitudinal Web Crawls

Michael Paris, Hande Celikkanat, Luca Foppiano

<https://arxiv.org/abs/2607.13636>

Abstract

A longitudinal web crawl is a sequence of partial samples of an evolving URL population. Pairwise containment between two crawls is the standard probe; under a simple *urn* model of the crawl – each round samples a fraction of the URLs and replaces a fraction – it recovers two interpretable rates, per-round survival *α* and coverage c, but treats the population as uniform and consumes one pair at a time. In this work, we define a formal language for talking about a crawl. We extend this analysis with the *discovery curve* U(s,T), the cumulative URL footprint over a sliding window of T crawls starting at s, which under the same urn model is also a closed-form function of (*α*,c). Containment and the discovery curve are then two projections of one process: independent fits agree on (*α*,c) when the urn is homogeneous, so any disagreement is itself a measurement. Applied to Common Crawl (2020–2025, domain granularity) and to the German Academic Web (GAW, URL granularity), the two projections disagree on both archives, and a two-component urn with a persistent core fraction *κ* alongside shell parameters (*α*∂,c∂) reconciles the disagreement. A residual on c∂ remains, signaling that the shell itself is not homogeneous; *κ* is recorded as the scalar entry point to a rank-resolved generalization, which is left to follow-up work.

![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-004](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-004.webp)

Michael Paris while presenting the long paper "Measuring What the Crawler Sees: Discovery Curves, Core Persistence, and Shell Dynamics in Longitudinal Web Crawls".

On the 24th of September, Luca Foppiano presented a collaborative work "The INRIA DataLake: A Generic and Scalable Ecosystem of Pipelines for HAL Applied to Software Mentions Tracking" in the demo session, submitted with Vipul Gupta (Hereon), Samuel Scalbert (Inria), Kumar Guha (Inria), Yannick Barborini (CCSD), Alain Monteil (Inria), and Laurent Romary (Inria). The preprint is available on [arXiv](https://arxiv.org/abs/2607.09824).

![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-005](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-005.webp)

Luca Foppiano while demonstrating the paper "The INRIA DataLake: A Generic and Scalable Ecosystem of Pipelines for HAL Applied to Software Mentions Tracking".

TPDL is the sort of conference that gets librarians, archivists, data engineers, and NLP researchers talking to one another, often leading to collaborations across disciplines.

In conversation with the Portuguese Web-Archive [Arquivo.pt](http://arquivo.pt/) we discussed Common Crawl’s operations and our initiatives around languages, data quality and the importance of web preservation. Arquivo.pt has preserved Portuguese web content since 1996 and was formally established at FCCN in 2007.

The Common Crawl Foundation welcomes and encourages donations of seeds as URLs in any language with particular attention to low resource languages. Contributors may use our [web-languages](https://github.com/commoncrawl/web-languages) repository to suggest new seeds for the crawl.

We had further discussions with representatives from OpenAIRE and the ORKG on the importance of using graphs to create equitable recognition in academic publications.

![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-006](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-006.webp)

Dinner with [Arquivo.pt](http://arquivo.pt/) folks (From left to right, top: Pedro Gomes, Ivo Branco, bottom: Michael Paris, Luca Foppiano)

We plan to release a follow up blog post that includes an interactive deep dive on the presented estimator of the policy induced size of the crawl sample.

Stay tuned.

This release was authored by:

[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-007](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-007.webp)

Michael Paris](https://commoncrawl.org/team/michael-paris)

Michael is a Senior Research Engineer at the Common Crawl Foundation.

[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-008](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-008.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-009](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-009.webp)

Hande Çelikkanat](https://commoncrawl.org/team/hande-celikkanat)

Hande is a Senior ML Engineer with the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-010](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-010.svg)](/)

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

[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-011](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-011.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884-fig-013](../images/2532-The-Common-Crawl-Foundation-at-the-TPDL-Conferen-d6238884/figure-013.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl