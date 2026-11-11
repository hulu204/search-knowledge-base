---
title: 'https://commoncrawl.org/blog/july-2026-crawl-archive-now-available'
company: CommonCrawl
tag: 爬虫抓取
date: 
url: https://commoncrawl.org/blog/july-2026-crawl-archive-now-available
account: 
origin: en-rss
---
[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-001](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-001.svg)](/)

[←  Back to Blog](/blog)

July 28, 2026

# July 2026 Crawl Archive Now Available

The crawl archive for July 2026 is now available. The data was crawled between July 7th and July 25th, and contains 2.14 billion web pages (or 364.01 TiB of uncompressed content). We also announce some improvements and changes.

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-002](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-002.webp)

Sebastian Nagel

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.](https://commoncrawl.org/team/sebastian-nagel-engineer)

![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-003](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-003.webp)

The crawl archive for July 2026 is now available.

The data was crawled between July 7th and July 25th, and contains 2.14 billion web pages (or 364.01 TiB of uncompressed content). Page captures are from 40.5 million hosts or 33.2 million registered domains and include 603 million new URLs, not visited in any of our prior crawls.

|  |  |  |  |
| --- | --- | --- | --- |
|  | File List | #Files | Total Size Compressed (TiB) |
| Segments | [segment.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/segment.paths.gz) | 100 |  |
| [WARC](https://commoncrawl.org/the-data/get-started/#WARC-Format) | [warc.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/warc.paths.gz) | 100000 | 84.69 |
| [WAT](https://commoncrawl.org/the-data/get-started/#WAT-Format) | [wat.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/wat.paths.gz) | 100000 | 14.09 |
| [WET](https://commoncrawl.org/the-data/get-started/#WET-Format) | [wet.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/wet.paths.gz) | 100000 | 5.89 |
| [Robots.txt](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [robotstxt.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/robotstxt.paths.gz) | 100000 | 0.15 |
| [Non-200 responses](https://commoncrawl.org/2016/09/robotstxt-and-404-redirect-data-sets/) | [non200responses.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/non200responses.paths.gz) | 100000 | 2.71 |
| [URL index](https://commoncrawl.org/2015/04/announcing-the-common-crawl-index/) | [cc-index.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/cc-index.paths.gz) | 302 | 0.22 |
| [Columnar URL index](https://commoncrawl.org/2018/03/index-to-warc-files-and-urls-in-columnar-format/) | [cc-index-table.paths.gz](https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-30/cc-index-table.paths.gz) | 900 | 0.20 |

### Archive Location & Download

The July 2026 crawl archive is located in the `commoncrawl` bucket at `crawl-data/CC-MAIN-2026-30/`.

To assist with exploring and using the dataset, we provide gzipped files which list all segments, WARC, WAT and WET files.

By simply adding either `s3://commoncrawl/` or `https://data.commoncrawl.org/` to each line, you end up with the `S3` and `HTTP` paths respectively, please see [Get Started](https://commoncrawl.org/get-started) for detailed instructions.

## Improvements and Changes

This crawl comes with a series of improvements and changes.

## WARC-Record-ID Now Uses Type 7 UUID

We switch from using Type 4 to Type 7 UUIDs for WARC record IDs.

[Type 7 UUID](https://en.wikipedia.org/wiki/Universally_unique_identifier#Version_7_(timestamp_and_random))s are defined by [RFC 9562](https://datatracker.ietf.org/doc/html/rfc9562) (published in 2024 and updating RFC 4122) and combine a Unix timestamp (epoch seconds) with a random component. One example of a Type 7 WARC record ID:

```
WARC/1.0
WARC-Type: response
WARC-Date: 2026-07-10T22:25:47Z
WARC-Record-ID: <urn:uuid:019f4e23-0ae1-7128-99c9-625a3048e3b1>
Content-Length: 27888
Content-Type: application/http; msgtype=response
WARC-Warcinfo-ID: <urn:uuid:019f4e20-cbc0-7088-8251-ecc9a008540a>
WARC-Concurrent-To: <urn:uuid:019f4e23-0ae1-71ae-a89b-b0992fcec9b8>
WARC-IP-Address: 2620:cb:2000::1
WARC-Target-URI: https://commoncrawl.org/
WARC-Protocol: h2
WARC-Protocol: tls/1.3
WARC-Cipher-Suite: TLS_AES_128_GCM_SHA256
WARC-Payload-Digest: sha1:BYSGGYPUHJIF4ZIOWKMPPLYUJ5U5YJQO
WARC-Block-Digest: sha1:5OM6GSLZYKMJJ5MPXWM5BUVWW43GGZZU
WARC-Identified-Payload-Type: text/html
```

The following Python snippets demonstrates how the UUID can be parsed to extract the timestamp:

```
import datetime as dt
import uuid

record_id = uuid.UUID('urn:uuid:019f4e23-0ae1-7128-99c9-625a3048e3b1')
dt.datetime.fromtimestamp(record_id.time / 1000).isoformat()
# returns '2026-07-11T00:25:47.233000'
```

As you can see, the timestamp in the in the UUID mirrors the `WARC-Date` header. Of course, the UUIDs in the WARC response records follow the same pattern. For further details about this change, please see the [corresponding issue on GitHub](https://github.com/commoncrawl/nutch/issues/41).

## WARC-Record-ID Included in URL Indexes

The record ID of the WARC response records is now contained in our URL indexes without the decorating `<urn:uuid:>`:

* The [CDXJ index](https://gist.github.com/sebastian-nagel/9d3474a66d4c92c0b29843e4f04fb463#file-cdxj-index) stores the UUID in the field `recordid` .
* The [URL index](https://gist.github.com/sebastian-nagel/9d3474a66d4c92c0b29843e4f04fb463#file-url-index) has a new column `warc_record_id`.

In order to use the new column in the URL index with [Amazon Athena](https://aws.amazon.com/athena/), you need to use the updated table schema defined by the [cc-index-create-table-flat.sql](https://github.com/commoncrawl/cc-index-table/blob/main/src/sql/athena/cc-index-create-table-flat.sql) statement.

The column `warc_record_id` is a binary column. You can cast from and to the data type [UUID](https://trino.io/docs/current/language/types.html#uuid):

```
select cast(warc_record_id as uuid)
from ccindex
where url = 'https://commoncrawl.org/'
  and url_host_name_reversed = 'org.commoncrawl'
  and crawl = 'CC-MAIN-2026-30';
```

To look-up a record ID:

```
select url, fetch_time
from ccindex
where cast(warc_record_id as uuid) = uuid '019f4e23-0ae1-7128-99c9-625a3048e3b1'
  and url_host_name_reversed = 'org.commoncrawl'
  and crawl = 'CC-MAIN-2026-30';
```

Also DuckDb provides a [UUID](https://duckdb.org/docs/current/sql/data_types/numeric#universally-unique-identifiers-uuids) data type. You can use the new column the exact same way as in Amazon Athena.

More details about the new column can be found in the [pull request cc-index-table#42](https://github.com/commoncrawl/cc-index-table/issues/42) on GitHub.

## The URL Index Switches to ZStandard Parquet Compression

The Parquet files of the URL index, starting with the current crawl's partition (`crawl=CC-MAIN-2026-30`) are compressed using ZStandard compression.

Given that most Parquet readers and query engines support ZStandard nowadays, no changes are required to query the recent partitions of the URL index. Additional information can be found in [this issue report on GitHub](https://github.com/commoncrawl/cc-index-table/issues/11).

## Statistics of IP Address and HTTP Protocol Versions

We started publishing statistics of IP address and HTTP protocol versions observed by our crawler `CCBot`. The new metrics are found on the [Crawl Stats site](https://commoncrawl.github.io/cc-crawl-statistics/) along with other [crawler metrics](https://commoncrawl.github.io/cc-crawl-statistics/plots/crawlermetrics).

This release was authored by:

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-004](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-004.webp)

Sebastian Nagel](https://commoncrawl.org/team/sebastian-nagel-engineer)

Sebastian is a Distinguished Engineer at the Common Crawl Foundation.

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-005](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-005.webp)

Luca Foppiano](https://commoncrawl.org/team/luca-foppiano)

Luca Foppiano is a Senior Engineer at the Common Crawl Foundation.

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-006](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-006.webp)

Michael Paris](https://commoncrawl.org/team/michael-paris)

Michael is a Senior Research Engineer at the Common Crawl Foundation.

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-007](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-007.webp)

Thom Vaughan](https://commoncrawl.org/team/thom-vaughan)

Thom is Principal Engineer at the Common Crawl Foundation.

## Erratum:

## Content is truncated

Originally reported by:

[More details](/errata/content-is-truncated)

Some archived content is truncated due to fetch size limits imposed during crawling. This is necessary to handle infinite or exceptionally large data streams (e.g., radio streams). Prior to March 2025 (CC-MAIN-2025-13), the truncation threshold was 1 MiB. From the March 2025 crawl onwards, this limit has been increased to 5 MiB.

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-008](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-008.svg)](/)

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

[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-009](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-009.svg)](https://x.com/commoncrawl)[![LinkedIn Logo](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/6493999d57ad8123b314b6cf_linkedin%20(1).svg)](https://www.linkedin.com/company/common-crawl/)[![2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029-fig-011](../images/2297-https-commoncrawl-org-blog-july-2026-crawl-archi-14db1029/figure-011.svg)](https://discord.gg/njaVFh7avF)

© 2026 Common Crawl