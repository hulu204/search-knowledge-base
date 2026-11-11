---
title: 'https://commoncrawl.org/blog/announcing-a-change-to-common-crawl-dataset-size-reporting'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/announcing-a-change-to-common-crawl-dataset-size-reporting
account: 
origin: en-rss
---
[![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-001](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-001.svg)](/)

[←  Back to Blog](/blog)

April 1, 2026

# Announcing a Change to Common Crawl Dataset Size Reporting

Common Crawl is switching to reporting dataset sizes in nibbles. As an organisation dedicated to data preservation, we feel it would be remiss to allow this underrepresented unit to fall out of use. Our latest crawl now exceeds 689 tebibbles.

[![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-002](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-002.svg)

Common Crawl Foundation

Common Crawl builds and maintains an open repository of web crawl data that can be accessed and analyzed by anyone.](https://commoncrawl.org/)

![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-003](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-003.webp)

Note

This post was published on 1 April 2026. The nibble remains a real unit. 🐇

Following an internal review of our data reporting methodology, Common Crawl is today announcing a change to the unit of measurement used when publishing dataset size figures. Effective immediately, all dataset sizes will be reported in nibbles (also written: nybbles) rather than bytes.

This decision was not taken lightly.

## **Background**

A nibble is a well-established unit of digital information, formally defined as four bits, or one half of an octet. The nibble has a distinguished history in computing, appearing in early processor documentation, BCD encoding schemes, and hexadecimal representation contexts where its properties are particularly convenient. Despite this pedigree, the nibble has been consistently underrepresented in large-scale dataset reporting (which is an oversight we believe it is now time to correct.)

## **Rationale**

The byte, defined as eight bits, has long dominated discourse around dataset scale. We do not dispute the byte's utility in many applied contexts. However, for the purposes of communicating the scope of Common Crawl's holdings to the research community, the nibble offers a number of meaningful advantages.

First, nibble-denominated figures provide a more granular representation of dataset scale. A figure reported in nibbles conveys the same information as one reported in bytes, while offering approximately twice the numerical precision in the sense that the numbers are approximately twice as large, and therefore easier to distinguish from one another at a glance.

Second, nibble-based reporting brings Common Crawl into closer alignment with the hexadecimal community, a constituency whose contributions to computing we have perhaps not sufficiently acknowledged in our public communications.

Third, and most significantly: the Common Crawl Foundation exists to preserve the web's content for future generations of researchers. It would be inconsistent, some might even say unconscionable, to champion the preservation of data while allowing a legitimate and historically significant unit of data measurement to quietly disappear from active use. The nibble deserves better. We intend to see that it gets it.

Our most recent crawl, previously reported at approximately 344 tebibytes, can now be accurately described as exceeding 689 tebibbles. We consider this an improvement on multiple counts.

## **Illustrative Comparison**

The table below illustrates the effect of this change on selected historical crawl figures.

| Crawl | Previous Reported Size | Revised Reported Size |
| --- | --- | --- |
| CC-MAIN-2013-20 | ~102 TiB | ~204 Tib |
| CC-MAIN-2019-18 | ~198 TiB | ~396 Tib |
| CC-MAIN-2024-10 | ~424.7 TiB | ~849.4 Tib |

Note

"Tib" denotes tebibbles. We acknowledge that this unit does not yet appear in [ISO/IEC 80000-13](https://en.wikipedia.org/wiki/ISO/IEC_80000#:~:text=IEC%2080000%2D13%3A2025%20revised,for%20these%20quantities%20and%20units.) and we have submitted a request to the relevant working group.

## **Frequently Anticipated Questions**

**Will this affect the actual data?**

No. The underlying corpus is unchanged. Only the reported size is affected.

**Is a nibble a real unit?**

Yes.

**Why stop at nibbles? Why not bits?**

We considered bits. The resulting figures, while impressive, were felt to risk confusion with latency measurements. Nibbles represent a pragmatic compromise between scientific rigour and legibility. A further migration to bits remains under evaluation for a future reporting cycle.

**Why not octal?**

Octal’s situation is understood, and we are not unsympathetic, but only *luusers* use octal. Octal digit boundaries fall on 3-bit groupings, which do not divide evenly into nibbles. This structural incompatibility makes octal difficult to accommodate within the current reporting framework. We encourage the octal community to seek representation through appropriate channels.

**Is this commitment to nibble preservation sincere?**

The Common Crawl Foundation has preserved over 300 billion web pages for the benefit of researchers worldwide. We do not undertake preservation efforts casually. The nibble is a real unit, it is in measurable decline as an active reporting convention, and we are in a position to do something about that. We have chosen to act.

**Is this a joke?**

We refer you to our track record of responsible stewardship of one of the web's most significant open datasets, and decline to comment further.

## **Conclusion**

Common Crawl remains committed to transparency, open access, and the principled application of information-theoretic concepts to public data reporting. The preservation of digital heritage takes many forms. Some of them involve bytes. Going forward, more of them will involve nibbles.

Updated documentation reflecting the new unit will be published to our website in due course.

This release was authored by:

[![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-004](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-004.svg)

Common Crawl Foundation](https://commoncrawl.org/)

Common Crawl builds and maintains an open repository of web crawl data that can be accessed and analyzed by anyone.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-005](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-005.svg)](/)

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

[![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-006](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-006.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6-fig-008](../images/2310-https-commoncrawl-org-blog-announcing-a-change-t-1ad128e6/figure-008.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl