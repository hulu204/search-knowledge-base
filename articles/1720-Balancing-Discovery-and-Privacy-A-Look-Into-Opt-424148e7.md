---
title: 'Balancing Discovery and Privacy: A Look Into Opt-Out Protocols'
company: CommonCrawl
tag: 爬虫抓取
date: 2024-02-13
url: https://commoncrawl.org/blog/balancing-discovery-and-privacy-a-look-into-opt-out-protocols
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

February 13, 2024

# Balancing Discovery and Privacy: A Look Into Opt–Out Protocols

What opt–out protocols are, their importance, how you can use them, how we respect them, and what the emerging initiatives are that surround them.

[![Alex Xue](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/653ad0b3139feb3ecae5d92f_alex.webp)

Alex Xue

Alex is a Computer Science graduate from the University of Waterloo, Canada, and emeritus member of the Common Crawl Foundation.](https://www.linkedin.com/in/alexxue/)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64e634cbee339bea89485d24_analysis.webp)

## What is a Crawler?

A web–crawler, also referred to as a spider or search engine bot, retrieves and catalogs content from throughout the Internet. Its objective is to allow data to be accessed efficiently when needed. They are named "web–crawlers" because crawling is the technical term for automatically visiting a website and gathering data via a software program.

## What’s the Difference Between ‘Crawling’ and ‘Scraping’?

This is how we think about it (and this is just one opinion of many):

Web–scraping, also known as data–scraping or content–scraping, occurs when a bot downloads content without authorization, frequently in order to use it maliciously. Unlike web–crawling, web–scraping tends to be focused on specific pages, or particular websites, and often ignores the load imposed on web servers.

In contrast, web crawlers use open Internet protocols and adhere to the majority of opt–out mechanisms (which we will discuss in this article) and moderate their requests to avoid overwhelming web servers.

We believe that the gathering and archiving of web data should be done in a polite and respectful way. Common Crawl’s crawler, CCBot, does its best to be a polite and respectful citizen of the web.

## How Can Crawled Data Be Used?

Aside from the many Machine Learning (ML) applications for which crawled data can be used, it is instrumental in the fields of market research, risk–management and fraud–detection, and search engine optimisation (SEO).

Academics use web crawling to gather large datasets from the Internet for studies in fields like social sciences, linguistics, and humanities.  Organizations like libraries and historical societies use crawled data to archive digital content for future reference.

Travel websites can use the data to aggregate information on hotel prices, flight schedules, and tourist attractions, in order to offer comprehensive travel solutions to their users.

In the ML world, models in Natural Language Processing (NLP) are used for tasks like machine translation and speech recognition; often for under–resourced languages.  In manufacturing, ML models trained on web–sourced data can predict equipment failures, and help with scheduling of maintenance.

ML models use data crawled from weather websites and satellite imagery to make more accurate weather predictions and study climate–change patterns.

Web data is used to build ML models that adapt learning content to individual student needs, improving the effectiveness of educational technology.

And then there are Large Language Models, which you've probably heard about recently…

## What is a Language Model?

A Language Model is a type of artificial intelligence program that's designed to understand and generate human language. Think of it as a super-advanced chatbot that's been trained on a massive amount of text data — from books and websites to articles and more.

Here's how it works: the model has been fed a huge amount of text data, which it uses to learn patterns in language.  It understands how words and sentences are typically put together, and it can use this knowledge to generate new text that makes sense based on what it has learned.  So, when you ask it a question (give it a prompt), it uses its training to come up with a response that is relevant and coherent.  It’s like predictive text, but more complex.

## What Are Machine Learning (ML) Opt–Out Protocols and Why Are They Relevant to Us?

At a high level, a Machine Learning (ML) opt–out protocol is a mechanism that allows webmasters to specify their preferences regarding the access and usage of their content by automata (such as web–crawlers).  This allows website owners to state clearly whether they want their content to be part of datasets that can be used for machine–learning.

These protocols can also be used to label generated content which a future ML trainer might not want to use, because it's generated.

Let’s look at an example, and break down why these protocols are relevant to us.  Our mission is to provide an open repository of data for anyone to use: from individuals to large corporations. We strive to do this while always respecting the wishes of website owners.

For instance, we observe the [Robots Exclusion Protocol](https://datatracker.ietf.org/doc/html/rfc9309), which allows website owners to dictate which content can be accessed by automated agents.  Let’s look at the robots.txt of our own domain:

```
# All robots are explicitly allowed
User-agent: *
Allow: /
Disallow: /search?
Sitemap: https://commoncrawl.org/sitemap.xml
```

This states that any crawlers can access any directory/files in the domain, except those that are search queries (e.g: <https://commoncrawl.org/search?query=somesearch>).

In addition to respecting robots.txt, we also apply a generous delay when crawling through pages of a domain, in order to minimize the impact of our inbound traffic.

The User-Agent field allows website owners to specify which crawlers are restricted.  For example, in order to prevent Common Crawl (our crawler is called [CCBot](https://commoncrawl.org/ccbot)) from crawling all content on your website, you can put the following in your robots.txt file:

```
User-agent: CCBot
Disallow: /
```

The above will block CCBot from being able to crawl your website.  It is important to note that this will not only block the content from being used by those who use our data for training models, but also from those who use the data for search–indexing.  This can affect the discoverability of your website in those instances, so it might not be the right choice for your website to unilaterally block all web–crawlers.

Note: the Robots Exclusion Protocol only requires crawlers to parse at least 500 KiB of robots.txt files.

## Emerging Initiatives

Due to the arrival of Large Language Models (LLMs), these protocols should be brought into the spotlight.  These models are trained on text data, with many of them using Common Crawl data as a large portion of their corpora, which means that in order to ultimately respect the wishes of content creators, we must ensure that these directives are kept intact.

As the concern around privacy grows with the rise of LLMs, we see the birth of many new initiatives and protocols.  We will highlight some of them, with links to more information on how you can implement them.

## Robots Exclusion Protocol

This protocol (explained above) is also used for ML opt—out.  For example, Google’s crawler has many User-Agent strings that are specific to particular services, such as [Google-Extended](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers), which when used in directives can allow the exclusion of a website in Google’s Bard and Vertex services. Another example is OpenAI’s [GPTBot](https://platform.openai.com/docs/gptbot) crawler.

## HTTP Headers

Another way to opt–out is by specifying certain fields within the HTTP headers which crawlers see when they request the website.  For example, running:

```
$ curl --head  https://commoncrawl.org
```

…shows the HTTP headers of our website.

An example of how to restrict the use of content for Text and Data–Mining (TDM) purposes is the use of the [TDM Reservation Protocol](https://www.w3.org/2022/tdmrep/#sec-tdm-header), where in order to specify that rights are reserved, the response headers might look like:

```
HTTP/1.1 200 OK
Date: Wed, 14 Jul 2021 12:07:48 GMT
Content-type: image/jpg
tdm-reservation: 1
```

## HTML Metadata

Another way to opt–out is by making a declaration within the HTML of the website. This is typically done in a meta–tag.  For example, let’s use the French news website [letelegramme.fr](https://www.letelegramme.fr/) which uses the [TDM Reservation Protocol](https://www.w3.org/2022/tdmrep/#sec-tdm-html-meta) in its HTML.  Requesting the website with cURL and getting the meta tags that begin with “tdm” is done by running the following command:

```
$ curl -sS https://www.letelegramme.fr/ | grep -o '<meta[^>]*tdm[^>]*>'

<meta name="tdm-reservation" content="1"/>
<meta name="tdm-policy" content="https://www.letelegramme.fr/tdm-policy.json"/>
```

The TDM Reservation Protocol tells us that we can crawl, as long as we follow the specified policy.  Other examples of opt–out methods that work similarly are the [Robots Meta Tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag), and the [X-Robots-Tag](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag).

## Opting–Out via Additional Files

Another way to opt–out of being included in ML training data is by adding other files to your website’s server, such as with the emerging [DONOTTRAIN](https://genlaw.org/CameraReady/42.pdf) protocol, which proposes the addition of learners.txt.  This follows the same principle as robots.txt, but is specifically for opting–out of contributing to ML training data, and not crawls in general.  A similar initiative is [Spawning](https://site.spawning.ai/spawning-ai-txt) which helps webmasters create an ai.txt file; specifying whether images, media, or code can be used for ML training purposes.

Yet another example using the TDM Reservation Protocol (which also supports [a file–based method](https://www.w3.org/2022/tdmrep/#sec-tdm-file)) is including a [./well-known/tdmrep.json](https://www.radiofrance.fr/.well-known/tdmrep.json), which specifies the previously explained tdm-reservation directive, and tdm-policy link.

## Other Protocols

Of course, the methods mentioned previously do not tell the full story. Other methods exist, and the future will certainly hold even more.  An interesting initiative that doesn’t use HTML metadata, HTTP headers, or files is the Coalition for Content Provenance and Authenticity, or [C2PA](https://c2pa.org/specifications/specifications/1.3/specs/C2PA_Specification.html#_training_and_data_mining), which proposes the introduction of C2PA–enabled devices and applications (e.g a camera), which create “manifests” that follow the specification of each “asset” (e.g a photograph).  Each manifest will then define information about the device or application as well as other information, such as whether the asset can be used for ML training purposes.

## Where Do These Emerging Protocols Fit Into Common Crawl?

Because our WARC files already capture HTTP header and HTML metadata, we already give our users the ability to respect protocols that are based on these, such as Text and Data–Mining (TDM).

Examples of how you as a downstream user can interact with these protocols as well as other exploratory work will be further detailed in a follow–up blog post this month.

Since these are nascent efforts, we do not currently have a technical implementation for detecting many of these initiatives, such as the file–based protocols, but it is one of our top priorities.

As always, the mission of Common Crawl remains the same - making data accessible to anyone; ethically.  It is for this reason that our code, data, and current thoughts will always remain open.

If you have any questions or would like to contribute to the discussion please feel free to join our [Google Group](https://groups.google.com/g/common-crawl), or [Contact Us](/contact-us) through our website.

‍

---

## Glossary

Here’s a list of some of the “jargon” terms we’ve used in this article:

‍

#### **Opt–Out Protocols**

Mechanisms allowing individuals or organizations to exclude their data or content from certain processes or uses, particularly in online and automated contexts.

#### ‍**Web-Crawler (Spider, Search Engine Bot)**

A software program that systematically browses the World Wide Web, collecting and indexing website content. It's designed for automating data retrieval and enabling efficient data access.

#### **Web-Scraping (Data-Scraping, Content-Scraping)**

The process of using bots to extract content and data from a website, often without authorization, and potentially for malicious purposes.

#### **Machine Learning (ML)**

A field of artificial intelligence that focuses on the development of algorithms and statistical models that enable computers to learn and make predictions or decisions without explicit programming.

#### **Robots Exclusion Protocol (robots.txt)**

A standard used by websites to communicate with web crawlers and other web robots about which parts of a website should not be processed or scanned.

#### **User-Agent**

In the context of web crawling, it refers to a specific web crawler (bot) that accesses a website. Websites can use the User-Agent field to allow or disallow access to certain crawlers.

#### **HTTP Headers**

Components of the header section of request and response messages in the Hypertext Transfer Protocol (HTTP), which define the operating parameters of an HTTP transaction.

#### **Text and Data Mining (TDM)**

The automated process of deriving high-quality information from text and data through computational analysis techniques.

#### **HTML Metadata**

Data in a web page that provides information about the contents of the page, but is not displayed as part of the page content. Often used to provide information to web crawlers and search engines.

#### **TDM Reservation Protocol**

A method that allows website owners to specify whether and how their content can be used for text and data mining purposes.

#### **Robots Meta Tag and X-Robots-Tag**

HTML elements that provide instructions to web crawling bots, similar to the robots.txt file but applied on a per-page basis.

#### **Large Language Models (LLMs)**

Advanced AI models capable of understanding and generating human-like text, trained on vast amounts of textual data.

#### **C2PA (Coalition for Content Provenance and Authenticity)**

An initiative focused on combating disinformation and ensuring content authenticity through digital provenance.

#### **WARC Files (Web ARChive)**

File format used to store web crawls as a sequence of content blocks, including the corresponding HTTP request and response data, and metadata.

This release was authored by:

[![Alex is a Computer Science graduate from the University of Waterloo, Canada, and emeritus member of the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/653ad0b3139feb3ecae5d92f_alex.webp)

Alex Xue](https://www.linkedin.com/in/alexxue/)

Alex is a Computer Science graduate from the University of Waterloo, Canada, and emeritus member of the Common Crawl Foundation.

[![Julien is a member of the Apache Software Foundation, emeritus member of the Common Crawl Foundation.](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64ebc216bb945b48c03312bd_julien.webp)

Julien Nioche](https://www.linkedin.com/in/julien-nioche-4b7b453/)

Julien is a member of the Apache Software Foundation, emeritus member of the Common Crawl Foundation.

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