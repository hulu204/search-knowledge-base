---
title: 'GneissWeb Annotations Examples'
company: CommonCrawl
tag: 工程相关
date: 2026-01-13
url: https://commoncrawl.org/blog/gneissweb-annotations-examples
account: 
origin: harvest3-202607
---
[![](https://cdn.prod.website-files.com/6479b8d98bf5dcb4a69c4f31/649b5869af56f6df617cfb1f_CC_Logo_Blue_Auto.svg)](/)

[←  Back to Blog](/blog)

January 13, 2026

# GneissWeb Annotations Examples

A new Common Crawl index annotation has been added to Hugging Face and our S3 bucket.

[![Thijs Dalhuijsen](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/68c84ce96f3355ac6b90fba0_68908e7dc2853e61fe7bba41_thijs-p-800.webp)

Thijs Dalhuijsen

Thijs Dalhuijsen is Engineering Manager at Common Crawl.](https://commoncrawl.org/team/thijs-dalhuijsen)

![](https://cdn.prod.website-files.com/647b1c7a9990bad2048d3711/64eb2e14ae5e8c4c70ec5392_news2.webp)

Last fall [we announced](https://commoncrawl.org/blog/announcing-gneissweb-annotations) a collection of category and quality annotations, calculated from the [IBM Data Prep Kit](https://github.com/data-prep-kit/data-prep-kit) GneissWeb classifiers.

The methodology we followed was to take all the pages of the FineWeb dataset, see if they were included in GneissWeb, and calculate the four classification scores (medical, science, technology, educational) on the specified records. See more details in [our previous post](https://commoncrawl.org/blog/announcing-gneissweb-annotations).

Thanks to this annotation it is now possible to, for instance, select a subset from one of our crawls containing only hosts with a high probability of containing scientific medical records.

Here, this is illustrated by a practical DuckDB SQL example:

```
INSTALL httpfs;
LOAD httpfs;
CALL load_aws_credentials();
SET s3_region='us-east-1';

SELECT
  h.surt_host_name,
  h.hcrank,
  h.hcrank10,
  g.gneissweb_education  AS education,
  g.gneissweb_medical    AS medical,
  g.gneissweb_science    AS science,
  g.gneissweb_technology AS technology

FROM read_parquet('s3://commoncrawl/projects/host-index-testing/v2/crawl=CC-MAIN-2021-49/*.parquet') AS h

JOIN read_parquet('s3://commoncrawl/projects/gneissweb-annotation-testing-v1/hosts/crawl=CC-MAIN-2021-49/*.parquet') AS g
  ON h.surt_host_name = g.surt_host_name

WHERE g.gneissweb_medical > 0.5

ORDER BY h.hcrank DESC

LIMIT 10;
```

‍

Running this example, we get:

```
$ python gneissweb_medical.py
 
| surt_host_name     |      hcrank |   hcrank10 |   education |   medical |     science |   technology |
|--------------------|-------------|------------|-------------|-----------|-------------|--------------|
| gov,cdc            | 2.13851e+07 |      5.816 |   0.147358  |  0.690235 | 0.217257    |   0.0845532  |
| gov,nih,nlm,ncbi   | 2.11571e+07 |      5.754 |   0.126709  |  0.803236 | 0.919274    |   0.367261   |
| com,nature         | 2.04899e+07 |      5.572 |   0.0674915 |  0.789117 | 0.864001    |   0.294394   |
| com,walmart        | 2.03215e+07 |      5.526 |   0.0229006 |  0.880103 | 0.000637725 |   0.0612721  |
| com,springer,link  | 2.01602e+07 |      5.483 |   0.148069  |  0.672549 | 0.634984    |   0.179368   |
| gov,fda            | 2.0146e+07  |      5.479 |   0.0649566 |  0.652312 | 0.182145    |   0.117804   |
| com,healthline     | 2.00746e+07 |      5.459 |   0.0383815 |  0.787791 | 0.0785336   |   0.0353599  |
| us,mn,state,health | 2.00538e+07 |      5.454 |   0.187174  |  0.750825 | 0.100403    |   0.0726731  |
| com,webmd          | 1.99372e+07 |      5.422 |   0.0492467 |  0.792948 | 0.0899973   |   0.0407723  |
| org,healthaffairs  | 1.98987e+07 |      5.412 |   0.111606  |  0.714271 | 0.0158997   |   0.00757655 |
```

‍

We have made this data available not only at the host level, but also with increased granularity at the URL level, making it possible to select only the relevant pages from within a crawl.

The schema of this new dataset is compatible with our annotation system, so you can also use our [cc-index-annotations](https://github.com/commoncrawl/cc-index-annotations) project on GitHub to query it:**‍**

```
git clone https://github.com/commoncrawl/cc-index-annotations 
cd cc-index-annotations
pip install -r requirements.txt
make gneissweb
cd examples/gneissweb
python annotate.py left_web_host_index.yaml join_s3_gneissweb_host.yaml action_gneissweb_medical.yaml
```

‍

All crawls from `CC-MAIN-2013-20` to `CC-MAIN-2024-18` (inclusive) are available in these new datasets, and we have also made them available on Common Crawl’s S3 bucket and on Hugging Face:

## Host Level Annotations

* <https://huggingface.co/datasets/commoncrawl/gneissweb-annotation-host-testing-v1>
* `s3://commoncrawl/projects/gneissweb-annotation-testing-v1/hosts`

## URL Level Annotations

* <https://huggingface.co/datasets/commoncrawl/gneissweb-annotation-url-testing-v1>
* `s3://commoncrawl/projects/gneissweb-annotation-testing-v1/urls`

‍

We’d love to hear from you if you use these annotations in any of your projects, and don’t hesitate to reach out to us with questions via our [Discord](https://discord.gg/njaVFh7avF) or [Google Group](https://groups.google.com/g/common-crawl).

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