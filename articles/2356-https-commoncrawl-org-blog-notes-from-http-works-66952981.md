---
title: 'https://commoncrawl.org/blog/notes-from-http-workshop-basel-and-ietf-126-vienna'
company: CommonCrawl
tag: 搜索
date: 
url: https://commoncrawl.org/blog/notes-from-http-workshop-basel-and-ietf-126-vienna
account: 
origin: en-rss
---
[![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-001](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-001.svg)](/)

[←  Back to Blog](/blog)

August 3, 2026

# Notes from HTTP Workshop Basel and IETF 126 Vienna

Two weeks in Basel and Vienna, at the HTTP Workshop and IETF 126. Protocol adoption measured across the whole web, and an attempt to define what "machine readable" actually means.

[![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-002](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-003](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-003.webp)

Over a fortnight in July I travelled from Basel to Vienna, taking in two of the venues where the shape of the web is argued over in detail: the HTTP Workshop and IETF 126. The trip had three purposes: present measurement work drawn from the Common Crawl archive, attend the working groups whose output will determine how crawlers like ours are treated in the coming years, and move an Internet-Draft forward.

![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-004](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-004.webp)

A view of the Rhine in Basel, Switzerland

## **Basel: the HTTP Workshop**

The HTTP Workshop is an invitation-only gathering held every two years.  It puts roughly forty people in a room, among whom are the people who build and operate browsers, clients, servers, proxies, content delivery networks and measurement projects.  This was the seventh edition.  The format is deliberately an intimate one involving short talks and long discussions, and it runs under Chatham House Rule so that participants can speak candidly about what they see in production.

I presented a set of HTTP version adoption statistics† and used them to make a somewhat broader argument about what I’d argue Common Crawl is for.

The usual framing of a web crawl is as a supply of data for downstream consumers.  That’s true, but that undersells it.  A broad, openly available crawl is also a way to let the community observe protocol deployment at scale, as it actually is rather than as one assumes it to be.  Which HTTP versions are being served, which TLS versions, which IP versions, how they’re changing over numerous crawls and where the dustier parts of the web behave differently from the few hundred big places that most measurements are looking at.

We think that last part is very interesting.  Measurement based on top-site lists tells you what the largest and best-resourced operators are doing but it tells you relatively little about the small business sites, the parish councils, the personal blogs, and the other stuff which is where a giant chunk of the web still lives, and where protocol adoption tends to be behind by years.  A crawl of the whole tail is one of the few ways to see those.

† We now publish statistics on this monthly in [cc-crawl-statistics](https://commoncrawl.github.io/cc-crawl-statistics/)

## **In transit**

As it turns out, long train journeys seem to be an excellent format for the sort of discussions that a conference schedule never quite makes room for.

Most of them came back to responsible crawling.  Rate limiting, respecting the preferences expressed by site operators, and being transparent about who you are.  As automated traffic grows and site operators grow less patient with it, the practical question facing every crawler is whether it can be told apart from the badly behaved ones.  A crawler that identifies itself honestly publishes its address ranges, honours robots.txt and explains its purpose.  One that doesn’t is asking to be blocked, and increasingly will be.

![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-005](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-005.webp)

The plenary meeting at IETF 126, Vienna

## **Vienna: IETF 126**

[IETF 126](https://www.ietf.org/meeting/126/) ran from 18 to 24 July at the Hilton Vienna Park. I attended seven working group and research group sessions. Briefly, and in no particular order:

[**webbotauth**](https://datatracker.ietf.org/wg/webbotauth/about/) **(Web Bot Authorisation)**

This working group is developing mechanisms by which well-behaved automated clients can cryptographically authenticate themselves to servers, so that site operators can tell legitimate, identifiable bots apart from those spoofing their user agents.

[**aipref**](https://datatracker.ietf.org/wg/aipref/about/) **(AI Preferences)**

This is the working group developing standard, machine-readable ways for content owners to express preferences about how their content may be used, including by AI systems and crawlers. If you’re not familiar with this one yet, you probably ought to be.

[**maprg**](https://datatracker.ietf.org/group/maprg/about/) **(Measurement and Analysis for Protocols Research Group)**

I presented recent IPv6 adoption measurements and spoke to new additions to cc-crawl-statistics.  The measurement community is a great audience, since they can validate, extend, and cite the work, and their questions are a very good guide for what we should be measuring next.

[**httpbis**](https://datatracker.ietf.org/wg/httpbis/about/) **(HTTP Working Group)**

This is the group that maintains and evolves the HTTP specifications, and therefore the source of the protocol whose adoption we report on.  Many of the folks who were at the HTTP Workshop were also here, and it was great to follow up on discussions had the week before.

[**6man**](https://datatracker.ietf.org/wg/6man/about/) **(IPv6 Maintenance)**

This group is responsible for core IPv6 specifications.  Keeping up to date on this one keeps our IPv6 measurements aligned with where the protocol is heading.

[**happy**](https://datatracker.ietf.org/group/happy/about/) **(Happy Eyeballs)**

This group is concerned with the algorithms clients use to establish connections quickly across IPv4 and IPv6.  This is relevant to us both as the operator of a large client fleet and as a measurer of connectivity in the wild.  See our recent [analysis on IPv6 adoption](https://commoncrawl.github.io/ipv6-analysis/multivantage.html).

**AUDIT side meeting (Agent Use of Delegation and Interaction Traceability)**

This was a session on how autonomous agents delegate authority and how their interactions can be made traceable.  As agents proliferate, the questions of who is acting, on whose behalf, and with what accountability basically determine how any automated client is treated.  See [this draft from Mirja Kühlewind](https://datatracker.ietf.org/doc/draft-kuehlewind-audit-architecture/) on the topic.

## **Machine-readability draft**

During IETF 126 a side meeting on my Internet-Draft was held. The draft’s title is “Defining Machine Readability for Usage Preferences and Policy Expression”.  You can [read the draft on the Datatracker](https://datatracker.ietf.org/doc/draft-vaughan-machine-readability/).

![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-006](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-006.webp)

The frontispiece of Ted Nelson's Computer Lib/Dream Machines (1974). Original image by John R. Neill for L. Frank Baum's Tik-tok of Oz (1914).

The draft exists because "machine readable" gets invoked constantly in standards work and in policy and in legislation, and it’s almost never defined precisely enough to tell you whether a machine can actually act on the thing in question.  A terms-of-service document wrapped in a JSON string is parseable, but what a crawler recovers from it is a string of legalese, and that’s not something with which it can make any decisions.  The draft separates this idea into five distinct properties.  [Discoverability, parseability, interpretability, actionability, and verifiability](https://www.ietf.org/archive/id/draft-vaughan-machine-readability-01.html#name-core-criteria).  It then measures existing mechanisms against them, including robots.txt, the AIPREF drafts, ODRL, TDMRep, and C2PA.  The draft doesn’t propose any new mechanisms of its own.  It’s a set of definitions intended to make all of these conversations more precise.

The room was full and the discussion was encouraging.  There seems to be substantial interest in applying the framework in other standards efforts beyond the IETF.

If any of this is relevant to what you're working on, I'd be very glad to hear from you.

This release was authored by:

[![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-007](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-007.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-008](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-008.svg)](/)

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

[![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-009](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-009.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2356-https-commoncrawl-org-blog-notes-from-http-works-66952981-fig-011](../images/2356-https-commoncrawl-org-blog-notes-from-http-works-66952981/figure-011.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl