---
title: 'A Further Look Into the Prevalence of Various ML Opt-Out Protocols'
company: CommonCrawl
tag: 爬虫抓取
date: 2024-02-22
url: https://commoncrawl.org/blog/a-further-look-into-the-prevalence-of-various-ml-opt-out-protocols
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

February 22, 2024

# A Further Look Into the Prevalence of Various ML Opt–Out Protocols

This post details some experiments that we have done regarding Machine Learning Opt–Out protocols. We decided to investigate the prevalence of some of these protocols, by taking a deeper look at our WARC files, and finding which proportions of domains are using which opt–out protocols.

[![Alex Xue](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/653ad0b3139feb3ecae5d92f_alex.webp)

Alex Xue

Alex is a Computer Science graduate from the University of Waterloo, Canada, and emeritus member of the Common Crawl Foundation.](https://www.linkedin.com/in/alexxue/)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64e634cbee339bea89485d24_analysis.webp)

## Introduction and Data

We discussed what ML opt–out protocols are in our previous [blog post](https://commoncrawl.org/blog/balancing-discovery-and-privacy-a-look-into-opt-out-protocols).  We explored a few different ways to opt–out, as well as some associated emerging protocols, and how these fit into Common Crawl’s processes.  Our mission is to make web data accessible to everyone, and to do so in an ethical, responsible fashion, and so it is important for us to try to discern the wishes of those who own it.  We decided to investigate the prevalence of some of these protocols, by taking a deeper look at our [WARC](https://commoncrawl.org/get-started) files, and finding which proportions of domains are using which opt–out protocols.

First, we need data to look for usage of the various opt–out protocols.  We need a dataset large enough to be representative, but which can also be processed with a reasonable amount of resources.  This dataset should also contain high–quality data, and avoid possible biases, for instance where too many subdomains would use the same template and therefore give a distorted representation of the use of a particular protocol.  
  
Fortunately, as part of the pre–processing for our web crawls, we run a pre–crawl to gather candidate URLs for fetching.  As a starting point this takes a list of the top hosts and domain names from our latest [Web Graph](https://commoncrawl.org/web-graphs).  From there we do a few iterations of crawling with Apache Nutch™ and harvest URLs, some of which will be part of the next crawl.  
  
The data that we used for these experiments is two iterations of the output of our pre–crawl seed generation used internally, which takes the familiar form of a list of WARC files.  The first iteration is the pre–crawl seed WARC files for October (Week 40 of 2023, ~134.0 TiB) and the second iteration is for December (Week 50 of 2023, ~1008 GiB).  We will refer to them as seed-crawl/CC-MAIN-2023-40 and seed-crawl/CC-MAIN-2023-50 respectively.  Using two iterations is important because it gives us more insight on how the prevalence of each opt–out protocol may have changed over time.

Our hope is that these experiments will provide valuable insights on how to acknowledge opt–out protocols, increase visibility in emerging initiatives and act as a stepping–stone for your own projects.

Let’s highlight some experiments that we have done on some emerging opt–out protocols. To read more about these protocols, you can also take a look at our [previous blog post](https://commoncrawl.org/blog/balancing-discovery-and-privacy-a-look-into-opt-out-protocols).

### Methodology

In order to perform our experiments, we decided to use Apache Spark™ (specifically the Python API – PySpark) to process the data.  Spark is a distributed computing framework that is typically used when needing to process large amounts of data efficiently.  Our project [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) is based on PySpark, and allows us to create separate PySpark jobs for specific tasks.  We then compare the results of our PySpark job to the results produced from a [StormCrawler based topology](https://opencode.it4i.eu/openwebsearcheu-public/commoncrawl-parser) (which tells us details about how often different meta tags, headers and annotations appear) run on the same dataset. The StormCrawler based topology is simply used to confirm that the figures obtained from Spark are correct.

## Experiments

### Robots Exclusion Protocol

A commonly used opt–out method is to use the robots.txt part of the Robots Exclusion Protocol.  We discuss this in more detail in our previous post about opt–out protocols, but the overall idea is that one is able to specify the permissions for different User Agents (which refer to specific crawlers, such as Google’s “Googlebot” or our own “CCBot”).  We decided to measure the use of this to opt–out of data–mining for ML purposes.  Some of these User Agents include [Google-Extended](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers#google-extended) (used for training Bard/Gemini) and [GPTBot](https://platform.openai.com/docs/gptbot) (used for OpenAI products).  We used two different methodologies to learn more about the prevalence of these different User Agents within our crawl data.

We used the code in the [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) repository to process our data.  First, we wrote a [CCSparkJob](https://github.com/commoncrawl/ml-opt-out-experiments/blob/main/user_agent_count.py) which iterates over robots.txt files, and looks for any line starting with “User-agent:”, and then extracts the following token (which is the specified User Agent, such as “CCBot”, or a regular expression like “\*”).  This allows us to look for each time a specific User Agent is listed in a robots.txt (it is important to note that listing an agent does not necessarily mean it is barred from crawling, because in addition to “disallow” lists, one can also specify “allow” lists), but for our purposes we will be assuming a listing implies a “disallow” statement, as that is the typical usage, and typical crawler behavior would assume allowance unless otherwise specified.  We saved the frequency of each token that we found in our datasets.  Let’s look at some stats from the PySpark job results over the 20,038,781 robots.txt records that we processed in this dataset:

| User Agent | Number of Occurrences | Relative Frequency |
| --- | --- | --- |
| GPTBot | 359474 | 1.794% |
| CCBot | 367000 | 1.831% |
| anthropic-ai | 1736 | 0.008% |
| Google-Extended | 0 | 0.000% |

‍

As expected, we have mentions of GPTBot and a much smaller number of mentions of the anthropic-ai crawler. Surprisingly, there is no mention of “Google-Extended”.  If we look at the results of the Spark job over the 30,181,129 robots.txt records in our seed-crawl/CC-MAIN-2023-50 dataset:

| User Agent | Number of Occurrences | Relative Frequency |
| --- | --- | --- |
| GPTBot | 391704 | 1.298% |
| CCBot | 364942 | 1.209% |
| anthropic-ai | 2689 | 0.009% |
| Google-Extended | 317232 | 1.051% |

‍

We can see similar (slightly higher) proportions of GPTBot, anthropic-ai and CCBot being mentioned and suddenly many mentions of Google-Extended. This could be attributed to the fact that Google-Extended was [announced at the end of September](https://blog.google/technology/ai/an-update-on-web-publisher-controls/), just shortly before the CC-MAIN-2023-40 dataset was created. The sudden increase of occurrences can likely be attributed to people seeing the announcement.

### HTTP Headers

As discussed in our [previous blog post](https://commoncrawl.org/blog/balancing-discovery-and-privacy-a-look-into-opt-out-protocols), another commonly used opt–out method is to use HTTP headers.  We also experimented with finding metrics about this opt–out method in a similar way, using PySpark.

Similarly to how we processed the robots.txt stats, we used code in the [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) repository to process the data.  We first wrote a [CCSparkJob](https://github.com/commoncrawl/ml-opt-out-experiments/blob/main/tdm_header_count.py) which iterates over WARC files from our pre–crawl seed datasets.  This Spark job looks at the HTTP headers in each WARC record, and counts the frequency of each header.  From running this job over the 19,689,733 records on seed-crawl/CC-MAIN-2023-40, we can investigate statistics about some HTTP header tags for ML opt–out, such as those in the [TDM Reservation Protocol](https://www.w3.org/2022/tdmrep/#sec-tdm-header):

| Header | Number of Occurrences | Relative Frequency |
| --- | --- | --- |
| tdm-reservation | 115 | 0.0005840% |
| tdm-policy | 15 | 0.0000763% |

‍

We can see that a very small (but non–zero) portion of the records from the 2023-40 dataset are using these headers.  Now, let’s take a look at results for the 31,499,359 records in the seed-crawl/CC-MAIN-2023-50 dataset:

| Header | Number of Occurrences | Relative Frequency |
| --- | --- | --- |
| (tdm-reservation, 1) | 412 | 0.0013071% |
| (tdm-reservation, 0) | 15 | 0.0000476% |
| (tdm-policy, \*) | 69 | 0.0002191% |

‍

There seems to be a proportionally higher adoption rate of the TDM Reservation Protocol in the newer dataset, showing an increase in the adoption of this protocol, which we expected.

### HTML Metadata

As discussed in our [previous blog post](https://commoncrawl.org/blog/balancing-discovery-and-privacy-a-look-into-opt-out-protocols), a third opt–out method is via meta tags in a website’s HTML.  As with the other experiments, we used PySpark and StormCrawler for two stages of the experiment.

As with the other experiments, we used [cc-pyspark](https://github.com/commoncrawl/cc-pyspark) by writing a [CCSparkJob](https://github.com/commoncrawl/ml-opt-out-experiments/blob/main/html_metatag_count.py) to iterate over the WARC files.  While doing so, it keeps count of (name, content) pairs for HTML meta tags that it encounters.  For example, one instance of:

```
<meta name="robots" content="index, follow">
```

Would result in:

```
Row(key=Row(element1='robots', element2='index, follow'), val=1)
```

The meta tags that we are interested in are tags with the names “tdm-reservation” and “tdm-policy”.  We went through the 19,689,733 records in seed-crawl/CC-MAIN-2023-40:

| Header | Number of Occurrences | Relative Frequency |
| --- | --- | --- |
| (tdm-reservation, 1) | 111 | 0.0005642% |
| (tdm-reservation, 0) | 0 | 0% |
| (tdm-policy, \*) | 54 | 0.0002749% |

‍

We can see that there is a small (but non–zero) number of TDM Reservation Protocol implementations in this dataset.  Now, let’s take a look at the results for the 31,499,359 records in the seed-crawl/CC-MAIN-2023-50 dataset:

| Header | Number of Occurrences | Relative Frequency |
| --- | --- | --- |
| (tdm-reservation, 1) | 412 | 0.0013071% |
| (tdm-reservation, 0) | 15 | 0.0000476% |
| (tdm-policy, \*) | 69 | 0.0002191% |

‍

Again, a small but non–zero number of occurrences were found.

### Opting–Out via Additional Files

As discussed in our [previous blog post](https://commoncrawl.org/blog/balancing-discovery-and-privacy-a-look-into-opt-out-protocols), another out–out method is to add additional files to your web server.  To investigate the prevalence of this method we used the StormCrawler project, because of technical limitations with the Common Crawl crawler (we currently only fetch robots.txt as additional files).  For this experiment we analyzed the file ./.well-known/tdmrep.json from the [TDM Reservation Protocol](https://www.w3.org/2022/tdmrep/#sec-tdm-file).  We found that there were 263 hits out of the total 9,201,298 records scanned (roughly 0.003%).

## Concluding Thoughts & Acknowledgements

In conclusion, we can see that among many of these emerging protocols, it is not yet clear which of them will be widely adopted.  As we saw from comparing the results of seed-crawl/CC-MAIN-2023-40 and seed-crawl/CC-MAIN-2023-50, the adoption of these protocols is starting to increase.  Each of these protocols is extremely valuable, and at the very least will pave the way for how we are able to control content usage.  In the meantime, the Robots Exclusion Protocol is the tried and tested approach which we at CCF follow diligently, and we encourage everyone to use it.

This work could not be possible without the work from [OpenWebSearch](https://openwebsearch.eu/) to create the [commoncrawl-parser](https://opencode.it4i.eu/openwebsearcheu-public/commoncrawl-parser) which we have used extensively for our experiments.

Apache Nutch™, and Apache Spark™ and their respective logos are trademarks of the Apache Foundation.

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