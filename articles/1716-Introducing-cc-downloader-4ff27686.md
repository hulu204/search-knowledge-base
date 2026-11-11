---
title: 'Introducing cc-downloader'
company: CommonCrawl
tag: 工程相关
date: 2025-01-21
url: https://commoncrawl.org/blog/introducing-cc-downloader
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

January 21, 2025

# Introducing cc-downloader

Introducing a command-line tool written in Rust for downloading data from Common Crawl.

[![Pedro Ortiz Suarez](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/68ade5c6ef12425101705c61_pedro.webp)

Pedro Ortiz Suarez

Pedro is a Principal Research Scientist at the Common Crawl Foundation.](https://commoncrawl.org/team/pedro-ortiz-suarez)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

Today we are happy to announce `cc-downloader`, an experimental command-line tool for downloading Common Crawl data via `https`. `cc-downloader` is intended to be a user-friendly and polite downloader. It was made in response to the significant increase in downloads of our data in recent months. That was very exciting to see at first, especially in terms of the large rise in interest for our dataset. But it also makes it harder for some users to successfully download our data due to quirks of downloading from a high-traffic storage bucket.

`cc-downloader` is our solution to this problem, enabling our users to continue downloading our data via `https` without issues. We have designed `cc-downloader` with a polite retry mechanism that allows our users to make sure that every single file requested is downloaded. It also implements [jitter](https://en.wikipedia.org/wiki/Jitter) and exponential [backoff](https://en.wikipedia.org/wiki/Exponential_backoff) strategies, in order to avoid overwhelming our infrastructure.

If you wish to install `cc-downloader`, we have released [pre-compiled binaries](https://github.com/commoncrawl/cc-downloader/releases/) for all major operating systems and architectures. `cc-downloader` is written in [Rust](https://www.rust-lang.org/) and is distributed as a “crate”, so if you have [cargo](https://www.rust-lang.org/learn/get-started) installed, you can install `cc-downloader` with the following command:

```
cargo install cc-downloader
```

Once you have installed `cc-downloader`, you’ll see that it has 2 sub-commands:

First, `download-paths` downloads the file paths list for a given crawl and subset from our bucket, to a given destination folder path in your file system:

```
cc-downloader download-paths CC-MAIN-2024-46 wet path/to/folder
```

This paths file will be (in this case) `path/to/folder/wet.paths.gz`.

Next, `download` reads this file paths list and concurrently downloads the files to a given destination folder in your file system:

```
cc-downloader download path/to/folder/wet.paths.gz path/to/folder
```

This will preserve the tree structure that we use internally by default.

‍`cc-downloader` is still under active development, so if you find any issues or would like to submit a feature request, please visit its GitHub repository at <https://github.com/commoncrawl/cc-downloader/>.

Contributions are always welcome! We hope that with this tool our users will find it easier to download and use our data.

Finally, if you’re encountering any problems with `cc-downloader` that look like high traffic, you can check out our current traffic levels by looking at our [Infrastructure Status Webpage](https://status.commoncrawl.org/).

This release was authored by:

No items found.

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