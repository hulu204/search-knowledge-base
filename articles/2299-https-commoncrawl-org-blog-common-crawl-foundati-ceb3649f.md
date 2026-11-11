---
title: 'https://commoncrawl.org/blog/common-crawl-foundation-at-lrec-2026'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/common-crawl-foundation-at-lrec-2026
account: 
origin: en-rss
---
[![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-001](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-001.svg)](/)

[←  Back to Blog](/blog)

June 30, 2026

# Common Crawl Foundation at LREC 2026

The Common Crawl team attended the 16th International Conference on Language Resources and Evaluation in Palma, Mallorca, co-organizing a tutorial, presenting recent published work, and strengthening links with the research community.

[![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-002](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-002.webp)

Malte Ostendorff

Malte is a Senior Research Engineer at Common Crawl.](https://commoncrawl.org/team/malte-ostendorff)

![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-003](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-003.webp)

From 11 to 16 May 2026, members of Common Crawl's research and engineering team attended the 16th International Conference on Language Resources and Evaluation (LREC 2026) in Palma, Mallorca. LREC is the largest conference dedicated specifically to language resources and evaluation, with a long-running focus on the corpora, tools, and benchmarks that make modern NLP possible — a natural home for Common Crawl's mission.

The programme featured keynote talks, oral presentations, and poster sessions across three main conference days, preceded by a day of tutorials and followed by two days of workshops. With nearly 1,000 papers accepted across the main conference and the workshop tracks, LREC remains one of the key events to connect with the language resources community.

![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-004](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-004.jpg)

Left to right: Laurie Burchell, Luca Foppiano, Pedro Ortiz Suarez, and Malte Ostendorff at LREC 2026 in Palma, Mallorca.

## Contributions by the Common Crawl Team

The Common Crawl team contributed a co-organized tutorial and co-authored two papers featured in the main programme.

**Tutorial: Low-Resource, High-Impact — Building Corpora for Inclusive Language Technologies.** Laurie Burchell and Pedro Ortiz Suarez from Common Crawl co-organized this tutorial together with Ekaterina Artemova, Daryna Dementieva, Shu Okabe, and Mariya Shmatova. The tutorial took participants through end-to-end NLP pipelines for underrepresented languages — from data collection and web crawling, through parallel sentence mining and machine translation, to downstream applications like text classification and multimodal reasoning. The materials cover more than ten languages from a range of language families and geopolitical contexts, with an emphasis on fair, reproducible, and community-informed practice. Tutorial paper: [arXiv:2512.14576](https://arxiv.org/abs/2512.14576).

**HPLT 3.0: Very Large-Scale Multilingual Resources for LLM and MT.** Co-authored by Laurie Burchell with collaborators across the HPLT consortium, HPLT 3.0 is the latest release of one of the largest openly licensed multilingual datasets built on top of Common Crawl and Internet Archive data. The 3.0 release covers around 200 languages and reaches 30 trillion tokens, with a full pipeline from raw web archives through language identification, deduplication, and quality filtering to monolingual and parallel corpora ready for LLM and MT training. The HPLT corpora have already become a reference resource for multilingual model builders in Europe and beyond. Paper: [arXiv:2511.01066](https://arxiv.org/abs/2511.01066).

**SciLaD: A Large-Scale, Transparent, Reproducible Dataset for Natural Scientific Language Processing.** Co-authored by Luca Foppiano, Pedro Ortiz Suarez, and Malte Ostendorff from Common Crawl together with colleagues at DFKI and partner institutions, SciLaD is a fully open dataset of scientific publications, comprising a curated English split of over 10 million papers and a multilingual TEI XML split covering more than 35 million publications. The construction pipeline relies entirely on open-source tooling — including [Grobid](https://github.com/grobidOrg/grobid) for PDF processing and [Datatrove](https://github.com/huggingface/datatrove) for large-scale curation — and is released alongside the dataset to support reproducibility. The team also pre-trained a RoBERTa-base model on SciLaD and showed performance comparable to other scientific language models of similar size on standard benchmarks. Paper: [arXiv:2512.11192](https://arxiv.org/abs/2512.11192), [Datasets](https://huggingface.co/collections/scilons/scilons-datasets), [Models](https://huggingface.co/collections/scilons/scilons-models), [Code](http://github.com/scilons).

## Submitted Works featuring Common Crawl

Common Crawl data, or papers using methodologies very close to ours, showed up in many places throughout the LREC 2026 programme. A selection of papers directly or indirectly relevant to our work:

* [**GPT-NL Public Corpus: A Permissively Licensed, Dutch-First Dataset for LLM Pre-training**](https://arxiv.org/abs/2604.00920) (van Oort et al., 2026): The largest permissively licensed Dutch corpus to date, with 36 billion Dutch tokens, plus curated English, code, and German/Danish slices, much of it sourced from Common Crawl and Common Corpus. A concrete example of a national-scale LLM dataset built on top of our data, released on the Hugging Face Hub under CC-BY.
* [**CLASSLA-web 2.0: A 17-Billion-Word Crawled Web Corpus of Seven South Slavic Languages**](https://arxiv.org/abs/2601.11170) (Kuzman Pungeršek et al., 2026): A new, large-scale web corpus for Bosnian, Bulgarian, Croatian, Macedonian, Montenegrin, Serbian, and Slovenian, built via TLD-level crawling. The paper also documents the growing presence of machine-generated content on top web domains — a finding directly relevant to ongoing work on data quality signals.
* [**Dynaword: From One-shot to Continuously Developed Datasets**](https://arxiv.org/abs/2508.02271) (Enevoldsen et al., 2026): A framework for community-maintained, openly licensed datasets, instantiated as Danish Dynaword. The release contains over four times the tokens of comparable Danish corpora, is exclusively openly licensed, and has received contributions from companies, universities, and government institutions — a model very much in the spirit of Common Crawl's own open approach.
* [**CoMMA: A Large-scale Corpus of Multilingual Medieval Archives**](https://inria.hal.science/hal-05299220) (Clérice et al., 2026): A 2.5-billion-token corpus drawn from more than 23,000 digitized medieval manuscripts in Latin and Old French, harvested via IIIF. A web-scale harvest applied to cultural heritage rather than the contemporary web, with applications from corpus linguistics to historical-language model pretraining.
* [**TestiMole-Conversational: A 30-Billion-Word Italian Discussion Board Corpus (1996–2024)**](http://lrec-conf.org/proceedings/lrec2026/workshops/cmlc/2026.cmlc-1.0.pdf) (Rinaldi et al., 2026): A large-scale Italian web corpus drawn from discussion boards, motivated explicitly by the relatively low share of Italian in Common Crawl. Featured at the 12th Workshop on Challenges in the Management of Large Corpora (CMLC-12).
* [**ManufactuBERT: Web Data for a Domain LLM**](https://doi.org/10.63317/3c7yx4ewnj5m) (Armingaud and Besancon, 2026): A domain-adapted language model for the manufacturing sector trained on web data (Common Crawl via FineWeb), with a reported 33% training-time reduction from careful deduplication — a clean example of the impact of dedup on training efficiency.

## Next Steps

LREC 2026 was a great opportunity to reconnect with the language-resources community, see how Common Crawl data is being put to use across a remarkable diversity of languages and domains, and surface new collaborations. We were especially glad to see how much work in the field is now openly licensed, openly documented, and openly shared — a trend that benefits everyone.

We look forward to attending more conferences in the coming months. One of the next stops is ACL 2026 in San Diego, where we will be presenting [CommonLID](https://commoncrawl.org/blog/commonlid-re-evaluating-state-of-the-art-language-identification-performance-on-web-data), our open benchmark for language identification on web text — come find us there!

This release was authored by:

[![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-005](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-005.webp)

Malte Ostendorff](https://commoncrawl.org/team/malte-ostendorff)

Malte is a Senior Research Engineer at Common Crawl.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-006](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-006.svg)](/)

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

[![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-007](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f-fig-009](../images/2299-https-commoncrawl-org-blog-common-crawl-foundati-ceb3649f/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl