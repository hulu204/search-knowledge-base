---
title: 'https://commoncrawl.org/blog/common-crawl-foundation-at-colm-2025'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/common-crawl-foundation-at-colm-2025
account: 
origin: en-rss
---
[![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-001](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-001.svg)](/)

[←  Back to Blog](/blog)

October 20, 2025

# Common Crawl Foundation at COLM 2025

The Common Crawl team attended the 2nd Conference on Language Modeling in Montréal, organizing a workshop, giving invited talks, and strengthening links with the research community.

[![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-002](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-002.webp)

Malte Ostendorff

Malte is a Senior Research Engineer at Common Crawl.](https://commoncrawl.org/team/malte-ostendorff)

![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-003](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-003.webp)

Five members of our research and engineering team including Laurie, Pedro, Sebastian, Thom, and Malte attended the 2nd Conference on Language Modeling in Montréal, also known as COLM 2025. The conference is part of a relatively new event series (second edition), specifically about language models and related topics. In contrast to other major AI or NLP conferences, COLM is still rather small with approximately 1,500 participants (doubled compared to the first edition) and features only a single track of talks and poster sessions.

The main conference program took place from October 7-9 with 16 diverse workshops following on October 10th. The Common Crawl team contributed invited talks and organized a workshop at the conference.

## Contributions by the Common Crawl Team

Pedro, Laurie, and Thom from the Common Crawl team organized the [1st Workshop on Multilingual Data Quality Signals](https://wmdqs.org/) (WMDQS 🦆) together with colleagues from MLCommons, Johns Hopkins University, EleutherAI, and Factored. The workshop featured three keynotes by Julia Kreutzer (Cohere Labs), David Ifeoluwa Adelani (McGill University and Mila), and our own Sebastian who gave an overview of Common Crawl and our latest projects.

‍

![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-004](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-004.jpg)

David Ifeoluwa Adelani presenting at WMDQS

The workshop accepted 15 research papers for publication. The paper "[Enhancing Multilingual LLM Pre-training with Model-Based Data Selection](https://wmdqs.org/submissions-2025/5.pdf)" by Messmer et al. received the best paper award. In addition to the accepted papers, the workshop also presented the results of the shared task on [Improving Language Identification for Web Text](https://wmdqs.org/shared-task/).

![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-005](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-005.jpg)

Left to right: Sebastian Nagel (CCF), Laurie Burchell (CCF), Malte Ostendorff (CCF), Catherine Arnett (EleutherAI), Sarah Luger (iMerit/MLCommons), Sara Hincapié (Factored), Julia Kreutzer (Cohere Labs), Thom Vaughan (CCF), Pedro Ortiz Suarez (CCF), Rafael Mosquera (MLCommons), Kenton Murray (Johns Hopkins University)

Furthermore, Pedro gave an invited talk on “Expanding the Language and Cultural Coverage of Common Crawl” at the workshop on [Multilingual and Equitable Language Technologies (MELT)](https://melt-workshop.github.io/).

## Submitted Works featuring Common Crawl

Common Crawl was featured in various papers at COLM, especially in the context of LLM datasets. Below are research papers directly or indirectly relevant to our work:

* [Can Performant LLMs Be Ethical? Quantifying the Impact of Web Crawling Opt-Outs](https://openreview.net/forum?id=a6QsOjr3wo#discussion) (Fan et al., 2025): The paper studies how respecting web crawling opt-outs (robots.txt) affects LLM performance by introducing the concept of Data Compliance Gap (DCG), which quantifies the performance difference between models trained on datasets that comply with web crawling opt-outs, and those that do not. Their experiments with 1.5B models show that, as of January 2025, compliance with web data opt-outs does not degrade general knowledge acquisition (close to 0% DCG). However, in specialized domains such as biomedical research, excluding major publishers leads to performance declines. These findings suggest that while general-purpose LLMs can be trained to perform equally well using fully open data, performance in specialized domains may benefit from access to high-quality copyrighted sources later in training.

* [2 OLMo 2 Furious (COLM’s Version)](https://openreview.net/forum?id=2ezugTT9kU#discussion) (Walsh et al., 2025): The paper introduces AllenAI’s OLMo 2, a family of fully open 7B, 13B and 32B models achieving competitive performance at lower computational cost while providing transparency through released training data, code, checkpoints, and more. The updated pretraining data mixture introduces a new, specialized data mix called Dolmino Mix 1124, that relies on Common Crawl via DCLM (Li et al., 2024) and other open data sources such as Wikipedia or StarCoder.
* [FineWeb2: One Pipeline to Scale Them All — Adapting Pre-Training Data Processing to Every Language](https://openreview.net/forum?id=jnRBe6zatP#discussion) (Penedo et al., 2025): FineWeb2 is the multi-lingual continuation of FineWeb (Penedo et al., 2024) – a data curation pipeline that filters Common Crawl data for LLM pretraining. The curation pipeline has five key steps: text extraction from WARC files, language identification, deduplication, heuristic-based filtering, and rehydration (selective upsampling based on duplicates).

* [Rethinking Multilingual Continual Pre-training: Data Mixing for Adapting LLMs Across Languages and Resources](https://openreview.net/pdf?id=mpTIzK4Zca) (Li et al., 2025): This study evaluates 36 continual pretraining configurations across three multilingual LLMs and 30+ languages, analyzing their effects across resource levels and language behavior categories. In the experiments, Common Crawl is used as the training data via MADLAD-400 (Kudugunta et al., 2024).

* [MegaMath: Pushing the Limits of Open Math Corpora](https://openreview.net/forum?id=SHB0sLrZrh#discussion) (Zhou et al., 2025): The paper introduces an open, high-quality mathematical corpus as an LLM training dataset. For Web data, the authors use Common Crawl as their data source. Specifically, they extract text and MathML from Common Crawl’s WARC files using modified Trafilatura and Resiliparse which support MathML extraction (code available on [GitHub](https://github.com/LLM360/MegaMath)). The Web data is complemented by Math-related code and synthetic data.

* [EuroBERT: Scaling Multilingual Encoders for European Languages](https://arxiv.org/abs/2503.05500) (Boizard et al., 2025): The paper presents a family of multilingual encoder models based on the BERT architecture for European and other widely spoken global languages. Common Crawl is used through FineWeb (Penedo et al., 2024) as training data for EuroBERT.
* [Sherkala-Chat: Building a State-of-the-Art LLM for Kazakh in a Moderately Resourced Setting](https://openreview.net/forum?id=wRcTCcb0H5#discussion) (Koto et al., 2025): Sherkala-Chat is a state-of-the-art instruction-tuned generative language model designed for Kazakh and aims to enhance the inclusivity of LLM advancements for Kazakh speakers. Adapted from the LLaMA-3.1-8B, the model is trained on 45.3B tokens across Kazakh, English, Russian, and Turkish from Common Crawl and other data sources.

‍

We had a great time at COLM 2025, strengthening our connections within the research community and exploring the latest work in the field. We look forward to attending more conferences in the near future.

![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-006](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-006.jpg)

The WMDQS team at COLM: Sebastian Nagel, Pedro Ortiz Suarez, Laurie Burchell, Thom Vaughan, and Malte Ostendorff

This release was authored by:

No items found.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-007](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-007.svg)](/)

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

[![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-008](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211-fig-010](../images/2329-https-commoncrawl-org-blog-common-crawl-foundati-c18da211/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl