---
title: 'https://commoncrawl.org/blog/measuring-web-accessibility-from-crawl-archives'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/measuring-web-accessibility-from-crawl-archives
account: 
origin: en-rss
---
[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-001](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-001.svg)](/)

[←  Back to Blog](/blog)

March 2, 2026

# Measuring Web Accessibility from Crawl Archives

A WCAG colour contrast audit of 240 top domains using Common Crawl's February 2026 archive finds four in ten colour pairings fall short of accessibility thresholds. Only one in five sites are fully compliant.

[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-002](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-002.webp)

Thom Vaughan

Thom is Principal Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/thom-vaughan)

![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-003](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-003.webp)

Editor's note

This post predates the renaming of the "Columnar Index" to the "URL Index". References below to the "columnar index" refer to what is now called the URL Index.

‍

Low-contrast text is the most common accessibility failure on the web.  Year after year, [WebAIM's Million analysis](https://webaim.org/projects/million/) confirms it: in their 2025 report, 79.1% of homepages had at least one instance of text that didn't meet [WCAG 2 AA](https://www.w3.org/WAI/WCAG2AA-Conformance) contrast thresholds.  But WebAIM's methodology involves rendering pages in a real browser, executing JavaScript, and loading external stylesheets.  I wanted to ask a different question: what can we learn about colour contrast from the raw HTML alone, using only Common Crawl's archived captures?

The answer, it turns out, is [quite a lot](https://thunderpoot.github.io/wcag-audit/colour-contrast-wcag-audit.html).

## **The audit**

I built a pipeline that takes the [500 most-crawled registered domains](https://commoncrawl.github.io/cc-crawl-statistics/plots/domains) from Common Crawl's crawl archives, in this instance that’s the February 2026 crawl (CC-MAIN-2026-08), and then retrieves the archived homepage captures directly from WARC files.  It then evaluates every foreground/background colour pairing it can extract from inline styles and embedded `<style>` blocks against [WCAG 2.1 Level AA](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) thresholds.

No live websites are visited, no external stylesheets are fetched†, and no JavaScript is executed.  The entire analysis works from what is declaratively present in the HTML document as archived by Common Crawl.

† This necessarily makes the analysis somewhat naïve, as it cannot account for styling introduced through external stylesheets, client-side rendering, or runtime computation. However, it demonstrates the kinds of accessibility analysis that can be done by using a web crawl archive directly, without needing to revisit or re-crawl live websites. Common Crawl's archive does include linked CSS, but pairing colours from external stylesheets requires selector-to-element resolution, which would basically mean reimplementing a browser’s style engine, and inline and embedded styles already express their pairings explicitly.

![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-004](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-004.webp)

What the HTML declares and what the browser renders are two overlapping but incomplete views.

Of the 500 domains, 428 had usable captures in the crawl archive.  Of those, 240 yielded at least one extractable colour pairing, giving 4,327 unique pairings to evaluate.  The full results and methodology are published at [the interactive results dashboard](https://thunderpoot.github.io/wcag-audit/) and the [code is available on GitHub](https://github.com/thunderpoot/wcag-audit).

## **Key findings**

**The median pass rate for normal text contrast is 62.7%.**Across the 240 domains with extractable pairings, roughly four in ten colour combinations fail the 4.5:1 contrast ratio required by [WCAG 2.1 SC 1.4.3](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html) for normal-sized text.  Wes Anderson is crying in a pastel pink hotel somewhere.  When you relax the threshold to the 3:1 ratio permitted for large text, the median improves to 74.0%, but the gap between these two numbers is itself revealing: much of the web's low-contrast text lives in the smaller UI elements that users interact with most, such as navigation links, form labels, footers, and metadata.

**About one in five sites (20.4%) achieve full compliance** across all their detected pairings.  At the other end, over a quarter of sites (26.2%) fail more than half their pairings.  The distribution is bimodal: sites tend to either care about contrast or not care at all, with relatively few landing in the middle.

Domains were [classified](https://github.com/thunderpoot/wcag-audit/blob/main/src/04_generate_report.py#L28-L107) by TLD pattern matching (e.g. `.edu` and `.ac.uk` for Education, `.gov` and `.gouv.fr` for Government) and a manually curated list of known domains for the remaining categories; domains that matched none of these rules were placed in "Other", which accounts for the majority of the sample.

| Category | n | Avg % | Median % | 100% | < 50% |
| --- | --- | --- | --- | --- | --- |
| E-commerce | 5 | 64.1 | 66.7 | 0 | 0 |
| Education | 47 | 63.7 | 64.7 | 14 | 10 |
| News/Media | 10 | 61.7 | 75.0 | 1 | 4 |
| Other | 134 | 61.5 | 64.7 | 30 | 35 |
| Open Knowledge | 7 | 52.4 | 50.0 | 0 | 0 |
| Government | 14 | 49.7 | 54.5 | 1 | 4 |
| Technology | 10 | 47.7 | 50.0 | 1 | 4 |
| Hosting | 11 | 44.6 | 43.3 | 2 | 6 |

  

Pass rate statistics by domain category, sorted by average pass rate descending.

**Education and e-commerce sites fare best; hosting and platform sites fare worst.**This is an interesting signal.  Educational institutions often have dedicated accessibility teams and face regulatory requirements (particularly in the US under [Section 508](https://www.section508.gov/) and in the EU under the [European Accessibility Act](https://ec.europa.eu/social/main.jsp?catId=1202)).  E-commerce sites have a financial incentive to be readable.  Hosting and platform providers, by contrast (ha ha), frequently serve heavily templated or framework-driven pages where inline styling is minimal and the CSS that matters most lives in external files that this analysis can't see.

## **What static analysis can and can't tell us**

It's important to be upfront about what this approach misses.  The 188 domains (44% of those with captures) where no colour pairings were found aren't necessarily accessible or inaccessible.  They simply rely entirely on external stylesheets, CSS frameworks loaded via `<link>` tags, or JavaScript-driven rendering (as single-page applications do).  Static analysis of the HTML document alone can't reach those styles.

Where a foreground colour is declared without a corresponding background (or vice versa), the audit assumes the CSS defaults: white for backgrounds, black for text.  This produces a number of 1.0:1 ratio artefacts: white-on-white or black-on-black pairings that aren't real visual failures but an inevitable limitation of analysing CSS declarations without rendering context.  The "notable failures" section of the report filters these out, focusing on sites whose worst pairings have ratios that suggest genuine contrast problems.

These limitations are also what make the approach interesting.  [WebAIM](https://webaim.org/) and similar tools render each page fully, applying all styles, running all scripts, and measuring what a user would actually see.  This audit instead measures something more structural: the colour choices that are baked directly into the HTML.  Think of it as examining the document's own stated intentions rather than the final rendered output.

## **Using Common Crawl's Columnar Index**

One of the goals of this project was to demonstrate a practical research workflow using Common Crawl's data infrastructure, so it's worth describing the pipeline in some detail.

The first challenge is finding the right WARC records.  Common Crawl's monthly crawl archives are enormous (petabytes of data), but the [Columnar Index](https://commoncrawl.org/columnar-index) makes targeted lookups efficient.  The index is a Parquet-based representation of the crawl metadata stored on S3, and it can be queried directly via Amazon Athena.

A single SQL query finds all 500 homepage captures in one pass.  The query filters for the specific crawl (CC-MAIN-2026-08), HTTP 200 responses, root paths, and HTML content types.  It uses a window function to pick one capture per registered domain, preferring the `www` subdomain or bare domain over deeper subdomains, and HTTPS over HTTP.  This typically scans 100-300 GiB of columnar data at a cost of roughly $0.50 to $1.50.

With the index results in hand, the pipeline fetches each page's HTML directly from WARC files on `data.commoncrawl.org` using byte-range HTTP requests.  There's no need to download entire WARC files.  Each request retrieves only the specific bytes containing the target record.  The HTML fetch step takes about a minute for 428 domains, and the subsequent colour extraction and WCAG analysis takes around two minutes.

The entire pipeline is four Python scripts with no dependencies beyond the standard library (plus PyAthena if you want to run Athena queries directly rather than importing a CSV from the console).  This was a deliberate choice.  I wanted the barrier to replicating or extending this work to be as low as possible.

## **Why this matters for the crawl**

Common Crawl's archive is often thought of as a dataset for training language models or for research that treats the web as text.  But the archive preserves much more than text.  It preserves structure, styling, and the design decisions that shape how people experience the web.  An analysis like this one, measuring colour contrast compliance across hundreds of the most-visited domains, is only possible because the archive faithfully captures the full HTML of each page, inline styles and all.

![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-005](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-005.webp)

It’s difficult choosing colours.  I still haven’t painted my kitchen for that reason.

This is the kind of longitudinal accessibility research I would like to see more often.  By running the same pipeline against successive monthly crawls, we could track whether the web is becoming more or less accessible over time, at least along this one measurable axis.  The February 2026 snapshot is a single data point, but the methodology is designed to be repeatable and the code is open source under the [MIT licence](https://github.com/thunderpoot/wcag-audit/blob/main/LICENSE).  The research content is dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).  The paper is [available on arXiv](https://arxiv.org/abs/2602.24067).

## **Try it yourself**

Browse the [interactive results dashboard](https://thunderpoot.github.io/wcag-audit/), and feel free to fork the repository on [GitHub](https://github.com/thunderpoot/wcag-audit).  If you run the pipeline against a different crawl, or extend it to cover additional WCAG criteria, I'd be glad to hear about it.

The dashboard itself, incidentally, passes [WCAG 2.1 Level AA](https://www.w3.org/WAI/WCAG2AA-Conformance) colour contrast on all its own text/background pairings, which seemed only fair.

This release was authored by:

[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-006](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-006.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-007](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-007.webp)

Pedro Ortiz Suarez](https://commoncrawl.org/team/pedro-ortiz-suarez)

Pedro is a Principal Research Scientist at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-008](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-008.svg)](/)

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

[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-009](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-009.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6-fig-011](../images/2314-https-commoncrawl-org-blog-measuring-web-accessi-633877a6/figure-011.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl