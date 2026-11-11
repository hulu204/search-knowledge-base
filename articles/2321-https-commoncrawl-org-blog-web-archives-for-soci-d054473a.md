---
title: 'https://commoncrawl.org/blog/web-archives-for-social-sciences-datathon-bristol'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/web-archives-for-social-sciences-datathon-bristol
account: 
origin: en-rss
---
[![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-001](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-001.svg)](/)

[←  Back to Blog](/blog)

January 26, 2026

# Web Archives for Social Sciences Datathon, Bristol

Recently, a two-day Bristol datathon used Common Crawl web archives to analyse UK industries and policy, strengthening social science research through hands-on, team-based work.

[![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-002](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-003](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-003.webp)

On 27–28 November 2025, researchers and practitioners gathered at the [Bristol Digital Futures Institute](https://www.bristol.ac.uk/bristol-digital-futures-institute/) for the [**Web Archives for Social Sciences Datathon**](https://data.commoncrawl.org/contrib/bdfi/index.html), a two-day, hands-on event exploring how large-scale web archive data can be used for policy-relevant social and economic research.

The Datathon was organised by the [Atlas of Economic Activities](https://www.urbaneconomies.co.uk/) research project in collaboration with the Common Crawl and the [UK Web Archive](https://www.webarchive.org.uk/). It was funded by [Smart Data Research UK](https://www.sdruk.ukri.org/)*.*

The results and challenge data can be found in the [Contributor Content](https://data.commoncrawl.org/contrib/index.html) of our website, hosted on S3.

![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-004](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-004.webp)

Outside the Bristol Digital Futures Institute

### **Building capacity with web archive data**

The primary aim of the Datathon was to build capacity within the social science research community to work confidently with web archive data at scale. Participants worked in interdisciplinary teams using curated extracts from Common Crawl to tackle real-world research questions, supported throughout by domain experts and technical facilitators.

Facilitation was provided by Emmanouil Tranos, Leonardo Castro Gonzalez, Jon Reades, Laurie Burchell, and Thom Vaughan, who guided teams through the data, methodologies, and research framing.

### **The challenges**

Five distinct problem statements were developed to showcase different analytical possibilities using web archive data.

**Financial Services and Fintech**

Participants analysed a 2021 dataset of UK commercial websites to identify sub-sectors within Financial Services, with particular attention to detecting Fintech providers. Websites were selected based on the presence of UK postcodes and sector relevance inferred from web text.

**Creative Industries and CreaTech**

A parallel challenge focused on the Creative Industries, using a larger 2021 dataset to identify industry sub-classes and highlight organisations operating at the intersection of creativity and technology, often referred to as CreaTech.

**Urban economic change in Manchester and Birmingham**

Teams worked with commercial website data from both 2021 and 2024 to classify economic activity in Manchester and Birmingham. Using labelled 2021 data as training input, participants classified 2024 websites, compared the industrial structures of both cities, and analysed how they evolved over time.

**Local Authority policy priorities**

Using a large corpus of UK government webpages from early 2024, participants identified key policy areas emphasised by Local Authorities and explored whether certain authorities stood out through distinctive policies or actions.

**Policy change after the 2024 general election**

The final challenge compared UK government webpages from early 2024 with a second snapshot from October 2025, asking teams to identify changes in specific policy domains following the general election in July 2024.

### **Data and methods**

Across the challenges, participants worked with structured CSV files and large compressed archives totalling several gigabytes. Each dataset included landing-page web text, URLs, detected UK postcodes, and a set of LLM-derived fields generated through a TNT-LLM-inspired classification pipeline. These fields provided two-level economic activity labels, enabling analysis at both sector and industry level.

This combination of raw web text, cleaned content, summaries, and machine-generated classifications allowed teams to experiment with a range of methods, from descriptive analysis and clustering to supervised classification and comparative policy analysis.

![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-005](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-005.webp)

Members of the five teams working on the shared tasks at the BDFI

### **Outcomes and open results**

Each team produced a set of findings and a presentation over the course of the Datathon. The full results, including code and analysis notebooks, have been made openly available on GitHub:

* Financial Services and Fintech: <https://github.com/kellyyubini/datathon_bristol>
* Creative Industries and CreaTech: <https://github.com/JGIBristol/team2-createch>
* Manchester and Birmingham analysis: <https://github.com/jatonline/common-crawl-datathon-group-3>
* Local Authority policy focus: <https://github.com/laurieburchell/datathon_problem4>
* Policy change over time: <https://github.com/eshasadia/G5-CommonCrawl>

### **Contributors**

The Datathon brought together participants from a wide range of backgrounds. Contributors included:

Aditi Dutta, Camilo Andrés López Barra, Céline Van Migerode, Christina Palantza, Do Ngoc Thao, Esha Sadia Nasir, Fanqi Zeng, Filippo Dionigi, Gabriel A. Pierzynski, Giovanni Maria Pala, Helena Byrne, James Thomas, Jia Zhao, Jo Kent, Kelly Yubini Yubini, Mariam Cook, Meihui He, Meng Le Zhang, Nirat Rujimora, Nora Ramsey, Paddy Smith, Rita Rasteiro, Thomas Carey-Wilson, Timothy Monteath, Wander Demuynck, and Wong E. Chern.

### **Looking ahead**

The Bristol Datathon demonstrated the growing potential of web archives as a resource for social science research, particularly when paired with modern language models and open data infrastructure. By making both the data and results openly available, the event aimed not only to answer specific research questions, but also to lower the barrier for future researchers interested in working with web-scale evidence.

### **Thanks**

We would particularly like to thank Emmanouil Tranos, Leonardo Castro Gonzalez, and Jon Reades for their leadership and insights, and their support throughout the Datathon. We are looking forward to many more collaborative projects in the future.

This release was authored by:

No items found.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-006](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-006.svg)](/)

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

[![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-007](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-007.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a-fig-009](../images/2321-https-commoncrawl-org-blog-web-archives-for-soci-d054473a/figure-009.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl