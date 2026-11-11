---
title: 'CommonLID: Re-evaluating State-of-the-Art Language Identification Performance on Web Data'
company: CommonCrawl
tag: 评测
date: 2026-02-10
url: https://commoncrawl.org/blog/commonlid-re-evaluating-state-of-the-art-language-identification-performance-on-web-data
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

February 10, 2026

# CommonLID: Re-evaluating State-of-the-Art Language Identification Performance on Web Data

We are excited to announce the release of CommonLID, a language identification benchmark for the web, covering 109 languages. CommonLID was developed in collaboration with multiple open-source organizations and language community groups.

[![Laurie Burchell](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/683610a5f112a5d4bbaf1ec8_6815de466a4de56d01e5a887_laurie2-p-800.webp)

Laurie Burchell

Laurie is a Principal Research Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/laurie-burchell)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

We are proud to introduce [CommonLID](https://huggingface.co/datasets/commoncrawl/CommonLID), a web-focused language identification benchmark spanning 109 languages, created in partnership with open source organizations and language communities. The CommonLID dataset is available through Hugging Face, and the preprint paper is available on [arXiv](https://www.arxiv.org/abs/2601.18026).

At the Common Crawl Foundation, we want to make our open data as comprehensive and representative as possible.  As part of this, one of our long-term research goals has been to improve the language coverage of our crawls.  We have been [exploring several approaches](https://commoncrawl.org/blog/expanding-the-language-and-cultural-coverage-of-common-crawl) towards this aim, but the most important for this blog post are our efforts to improve automatic language identification.

![An abstract image showing multiple documents in various languages with fingers pointing to each document](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/698b34f56547cd2f2f796d3a_web-languages-midjourney.webp)

While detecting the language in which a text is written seems like a simple task, [prior research](https://aclanthology.org/2022.tacl-1.4/) has shown that current language identification models can struggle, particularly with underrepresented languages.  This problem is even more challenging when detecting languages in web data.  The way people write on the web is often very different to how ‘formal’ text is written, meaning we need models which are tested on web data specifically.

For instance, these are some examples of web text whose language is mislabelled by existing LID systems:

Mislabelled example

Onyeakagbu, Adaobi. "See how all the 36 Nigerian states got their names". Pulse.ng. Retrieved 25 December 2021.

Gold Label: **English**

LID System Label: **Dagbani**

Mislabelled example

Propreté: Confort: Accueil du propriétaire: Rapport qualité/prix: Randonneurs

Gold Label: **French**

LID System Label: **Maltese**

Mislabelled example

Blog de titine807 - ~~~~~~~~~~ cOuCoU ToUs lE MoNdE BiEnVeNuE DaNs mOn tI BlOg ~~~~~~~~~~ -

Gold Label: **French**

LID System Label: **Non-Linguistic**

Mislabelled example

'^ 7.00 7.01 7.02 7.03 7.04 7.05 7.06 7.07 7.08 7.09 7.10 楊南郡、王素娥. 《玉山國家公園八通關越嶺古道西段調查研究報告》 (PDF). 玉山國家公園. 玉山國家公園管理處. 1987 [2014-03-01] （中文（臺灣））.'

Gold Label: **Chinese**

LID System Label: **Hebrew**

However, there is a general lack of quality datasets available for testing language identification models, especially those which cover a wide range of languages. Those which do exist don’t include web data, making it hard to assess performance and limiting researchers’ ability to make progress towards better language detection models for the web.

To close this gap, we are pleased to announce the release of CommonLID, a language identification benchmark dataset for the web which covers 109 languages.  This dataset was nearly two years in the making, involving significant collaboration with language communities and multiple research organisations.  We created CommonLID as part of a shared task at the [Workshop for Multilingual Data Quality Signals](https://wmdqs.org/), hosted at COLM in 2025.  The first step was building an annotation platform  in partnership with [MLCommons](https://mlcommons.org/) and [Factored AI](https://www.factored.ai/), so that participants could view and mark-up data.  In collaboration with [EleutherAI](https://www.eleuther.ai/), we then hosted multiple [hackathons](https://commoncrawl.org/blog/the-first-wmdqs-masakhane-langid-hackathon) with language community organisations like [Masakhane](https://www.masakhane.io/) and [SEACrowd](https://seacrowd.org/) during which participants contributed language labels for a selection of Common Crawl’s web data.  Finally, we curated the final dataset and used it to evaluate multiple existing language identification models, shedding light on the current state of the art.

Everyone who contributed to the project was invited to be on the paper, and we would like to thank all 97(!) co-authors for their hard work in making this project happen.  We hope to expand CommonLID in the future to include data for more languages through continued community-led work.  We also hope to use CommonLID, and its future versions, to help develop and maintain a new generation of open source LID models, allowing us and our community to better curate multilingual corpora from our crawl data.

This release was authored by:

[![Laurie is a Principal Research Engineer at the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/683610a5f112a5d4bbaf1ec8_6815de466a4de56d01e5a887_laurie2-p-800.webp)

Laurie Burchell](https://commoncrawl.org/team/laurie-burchell)

Laurie is a Principal Research Engineer at the Common Crawl Foundation.

[![Pedro is a Principal Research Scientist at the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/68ade5c6ef12425101705c61_pedro.webp)

Pedro Ortiz Suarez](https://commoncrawl.org/team/pedro-ortiz-suarez)

Pedro is a Principal Research Scientist at the Common Crawl Foundation.

[![Catherine is an NLP Researcher at EleutherAI.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/698b2964c5b761155bb9851c_catherine_arnett.webp)

Catherine Arnett](https://www.linkedin.com/in/catherine-arnett96/)

Catherine is an NLP Researcher at EleutherAI.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![Common Crawl Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

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

[![Twitter Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6675a2f3394182102f502e32_twitter-x.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6602100396780a14617cc8ab_discord.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl