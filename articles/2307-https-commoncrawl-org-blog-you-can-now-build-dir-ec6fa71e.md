---
title: 'https://commoncrawl.org/blog/you-can-now-build-directly-on-common-crawl-from-the-browser'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/you-can-now-build-directly-on-common-crawl-from-the-browser
account: 
origin: en-rss
---
[![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-001](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-001.svg)](/)

[←  Back to Blog](/blog)

May 6, 2026

# You can now build directly on Common Crawl from the browser

Browsers can now fetch Common Crawl data directly, no backend needed. Build SQL explorers, snapshot viewers and diff tools as static pages.

[![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-002](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-003](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-003.webp)

Editor's note

This post predates the renaming of the "Columnar Index" to the "URL Index". References below to the "columnar index" refer to what is now called the URL Index.

‍

![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-004](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-004.svg)

Pulling a single page out of an 800 MiB WARC file: the browser asks for a specific byte range, gets back just those bytes.  This wasn't possible from a browser before.

We've updated the CORS policies on [data.commoncrawl.org](http://data.commoncrawl.org/) and [index.commoncrawl.org](http://index.commoncrawl.org/) so that browsers can now fetch from both directly.  No proxy, no backend, no CORS plugin jazz.  We're rather excited about what this enables, but we’d also like to be forthcoming about a trade-off that comes with this change.

## **What on earth is CORS anyway?**

CORS is a browser-only safety check.  It stands for Cross-Origin Resource Sharing, and it’s an HTTP-header-based security mechanism which allows a server to indicate any origins (domain, scheme, or port) other than its own from which a browser should permit loading resources.

The data on our servers has always been reachable, but what CORS controls is basically just whether or not JavaScript running on someone else's web page is allowed to read the responses.  Without the correct headers, the browser fetches the data and then refuses to hand it over to the page's code.

![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-005](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-005.svg)

Same request, two outcomes. Without the right header the browser hides the response from your code. With it, the response goes through.

Again, things like `curl`, scripts, and servers don’t care about CORS.  It's a protection for end users whose browsers might otherwise be tricked into reading data from sites they're logged into.  Opening it up doesn’t expose anything new, it just lets browser code reach data that was always public.

## **What changed?**

Both hosts now send `Access-Control-Allow-Origin: *`.  On the data host, we also allow the `Range` request header and expose `Content-Range`, `Content-Length`, and `ETag` on responses.  That last thing is important because that means that byte-range requests are now allowed from a browser.

## **What can you build?**

A static HTML page can now do the full Common Crawl pipeline end-to-end:

```
// 1. Look up a URL in the CDX index
const cdx = await fetch(
  'https://index.commoncrawl.org/CC-MAIN-2026-17-index'
  + '?url=example.com&output=json&limit=1'
).then(r => r.text());

const { filename, offset, length } = JSON.parse(cdx.split('\n')[0]);

// 2. Range-fetch just that record from the WARC, a few KB instead of ~1 GB
const record = await fetch(`https://data.commoncrawl.org/${filename}`, {
  headers: { Range: `bytes=${offset}-${+offset + +length - 1}` }
}).then(r => r.blob());
```

‍

That's enough to build historical snapshot viewers, diff tools, link-graph explorers, teaching demos, and bookmarklets, all as static sites with no infrastructure requirements. The world is your proverbial oyster.

The [Columnar Index](https://commoncrawl.org/columnar-index) is even more fun.  [DuckDB-WASM](https://duckdb.org/docs/current/clients/wasm/overview) does HTTP range reads over [Apache Parquet](https://duckdb.org/docs/current/clients/wasm/overview), so you can run SQL against our index from a browser:

```
SELECT url, fetch_status
FROM 'https://data.commoncrawl.org/cc-index/table/cc-main/warc/'
     || 'crawl=CC-MAIN-2026-17/subset=warc/part-00000-...c000.gz.parquet'
WHERE url_host_registered_domain = 'example.com'
LIMIT 100;
```

‍

This DecompressionStream and DuckDB-WASM stuff works in pretty much any browser updated within the last 2 to 3 years.  So Chrome, Edge, Firefox, Safari, and all the Chromium-based browsers (Brave, Arc, Opera, Vivaldi, etc.) since around mid-2023.

## **A note on the index server**

Please be aware, `index.commoncrawl.org` is rate-limited, and those limits are strict.  With CORS open, you'll hit them more visibly than before, because every user's browser now counts as its own client.

The limits exist for good reason.  The CDX API is backed by finite resources serving the whole community, and a single enthusiastic frontend in a viral tweet can knock it over for everyone else.  Please cache aggressively, batch where you can, and for any workload heavier than interactive lookups, we suggest that you reach for the Columnar Index on `data.commoncrawl.org` instead (using something like [Amazon Athena](https://aws.amazon.com/athena/), or DuckDB, etc.)  The Columnar Index scales far better and isn't subject to the same limits.

We're proud to make infrastructure on which people can build cool stuff.  Just remember to be kind to our poor ol' index server.

This release was authored by:

[![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-006](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-006.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-007](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-007.svg)](/)

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

[![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-008](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-008.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e-fig-010](../images/2307-https-commoncrawl-org-blog-you-can-now-build-dir-ec6fa71e/figure-010.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl