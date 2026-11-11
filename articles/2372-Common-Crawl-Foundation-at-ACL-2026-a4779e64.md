---
title: 'Common Crawl Foundation at ACL 2026'
company: CommonCrawl
tag: 爬虫抓取
date: 2026-08-20
url: https://commoncrawl.org/blog/common-crawl-foundation-at-acl-2026
account: 
origin: en-rss
---
[![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-001](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-001.svg)](/)

[←  Back to Blog](/blog)

August 20, 2026

# Common Crawl Foundation at ACL 2026

The Common Crawl team attended the 64th Annual Meeting of the Association for Computational Linguistics in San Diego, California, presenting recent published work, and strengthening ties with the research community.

[![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-002](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-002.webp)

Malte Ostendorff

Malte is a Senior Research Engineer at Common Crawl.](https://commoncrawl.org/team/malte-ostendorff)

![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-003](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-003.webp)

The Common Crawl team attended the 64th Annual Meeting of the Association for Computational Linguistics ([ACL 2026](https://2026.aclweb.org/)), held July 2–7 at the Manchester Grand Hyatt in San Diego. ACL is the flagship venue of natural language processing, and this year's edition was vast: more than 4,800 papers across the main conference, Findings, the Industry and Student Research tracks, and system demonstrations, plus 37 co-located workshops.

Common Crawl data and the growing family of corpora derived from it remains foundational infrastructure for this community. As in previous years, we went looking for the research papers that build on our crawl and, just as importantly, the work that scrutinizes how web data is identified, filtered, documented, and governed.

![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-004](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-004.webp)

Entrance to the conference venue with ACL banner, Grand Hyatt Manchester San Diego

## A contribution from the Common Crawl team: CommonLID

We were especially happy to present [CommonLID: Re-evaluating State-of-the-Art Language Identification Performance on Web Data](https://arxiv.org/abs/2601.18026) at the main conference ([ACL Anthology](https://aclanthology.org/2026.acl-long.1527/)). CommonLID is a community-driven, human-annotated language identification (LID) benchmark for the web domain, covering 109 language varieties, many previously under-served. It was built with dozens of contributors worldwide. Crucially, CommonLID is built from the crawl itself: its samples are drawn from the WET files of the CC-MAIN-2024-22 and CC-MAIN-2025-05 snapshots and MADLAD-400, yielding over 373,230 hand-annotated lines.

Language identification is the first step in curating any multilingual corpus, and CommonLID's central finding is that LID is far from being a solved task: existing evaluations overestimate LID accuracy for many languages on real web text. Tested against eight popular LID systems, the best model achieves only 60 F1 on CommonLID, which is far below scores on cleaner sets like FLORES+ and UDHR. The [dataset](https://huggingface.co/datasets/commoncrawl/CommonLID) and code are openly and permissively licensed, and results are browsable at [commonlid.org](https://commonlid.org/) and the [Hugging Face leaderboard](https://huggingface.co/spaces/commoncrawl/commonlid). (More in our [companion blog post](https://commoncrawl.org/blog/commonlid-re-evaluating-state-of-the-art-language-identification-performance-on-web-data).)

![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-005](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-005.webp)

Some of the CommonLID co-authors at the ACL poster session

## **Other research papers relevant to our work**

Aside from our own contribution, there were several other research papers presented at the conference that are relevant to our work at Common Crawl Foundation:

### Language identification and language coverage

LID and coverage of under-served languages ran through the workshops as well as the main track:

* At AmericasNLP, ["The Power of Simplicity: N-Grams and Transformers in Nahuatl Language Identification"](https://aclanthology.org/2026.americasnlp-6.14/) tackled exactly the hard case CommonLID surfaces, distinguishing 11 closely related Nahuatl varieties (reaching ~90.6% accuracy), and finding that simple n-gram models remain competitive with transformers for low-cost LID.
* Also at AmericasNLP, [RAN: Resource Abundance Notation](https://aclanthology.org/2026.americasnlp-6.14/) proposed a standard notation for quantifying how much data exists per language (referencing the Common Crawl-derived OSCAR corpus).
* ["How Can Synthetic Data Improve Multilingual Pretraining?"](https://aclanthology.org/2026.acl-long.1002/) (main conference) addressed coverage from the data-quality side: its SynRank classifier filters the noisy MADLAD-400 web corpus for six low-resource languages, using translated synthetic data as the positive signal.
* [The African Languages Lab](https://arxiv.org/abs/2510.05644) (main conference) assembled the largest validated African text-and-speech dataset to date (19 billion tokens across 40 languages, reusing Common Crawl-derived parallel corpora) and argued, in line with our own view, that data scarcity, not model scale, is the primary bottleneck for low-resource NLP.
* And StereACuLT's ["Stereotyped by Silence"](https://aclanthology.org/2026.stereacult-1.6/) documented how LLMs erase Northeast Indian languages that are nearly absent from web-scale training data.

### Quality, provenance, and contamination

The questions of what is in a corpus, and whether we can trust evaluations on models trained from the web, were well represented:

* ["Is a Document Educational or Just Wikipedia-Style?"](https://arxiv.org/abs/2605.23721) stress-tests the widely used FineWeb-Edu quality classifier, showing a simple Wikipedia-style reformatting flips its filtering decision on ~7% of documents.
* [Gaperon](https://arxiv.org/abs/2510.25771), a fully open English–French suite built on the Common Crawl subset of TxT360 and RedPajama-V2, found that neural quality filters  systematically rank benchmark samples in their top percentiles, quietly amplifying contamination.
* [LLMSurgeon](https://openreview.net/forum?id=PNmoibvNDE) recovers the domain-level "digital DNA" of a model's pretraining mixture from its outputs alone, and [Tracing the Roots](https://aclanthology.org/2026.acl-long.435/) reconstructs dataset lineage graphs to show how contamination propagates as datasets are copied and re-derived. A GEM workshop survey, "[Are LLM Benchmarks Already Contaminated?](https://aclanthology.org/2026.gem-main.50/)", mapped the whole contamination-detection landscape.
* On the curation craft itself, [SELECting over Tokens (SelecT)](https://aclanthology.org/2026.acl-long.2219/) sampled raw HTML straight from early-2025 Common Crawl dumps and refined it via token classification while ["How Good is Your Wikipedia?"](https://arxiv.org/abs/2411.05527) applied the same noisy-web-text filtering to non-English Wikipedia.

This release was authored by:

[![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-006](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-006.webp)

Malte Ostendorff](https://commoncrawl.org/team/malte-ostendorff)

Malte is a Senior Research Engineer at Common Crawl.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-007](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-007.svg)](/)

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

[![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-008](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64-fig-010](../images/2372-Common-Crawl-Foundation-at-ACL-2026-a4779e64/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl