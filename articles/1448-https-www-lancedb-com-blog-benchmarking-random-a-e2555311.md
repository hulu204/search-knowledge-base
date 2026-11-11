---
title: 'https://www.lancedb.com/blog/benchmarking-random-access-in-lance'
company: LanceDB
tag: 评测
date: 
url: https://www.lancedb.com/blog/benchmarking-random-access-in-lance
account: 
origin: en-rss
---
# Benchmarking Random Access in Lance

[Chang She](/author/chang-she)

•

March 14, 2023

•

[Engineering](/category/engineering)

![1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311-fig-001](../images/1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

In this short blog post, we’ll take you through some simple benchmarks to show the random access performance of [Lance format](https://lance.org/).

Lance delivers comparable scan performance to parquet but supports fast random access, making it perfect for:

1. Search engines
2. Real-time feature retrieval, and
3. Speeding up shuffling performance for deep learning training

What makes Lance interesting is that in the existing tooling ecosystem, you either have to deal with the complexity of putting together multiple systems, OR, you have to deal with the expense of all in-memory stores. Moreover, Lance doesn’t require extra servers or complicated setup. `pip install pylance` is all you need.

💡 Check out the Lance format repo on GitHub here. [**https://github.com/lance-format/lance**](https://github.com/lance-format/lance)

## Test setup

Here, we’re going to compare the random access performance of Lance vs parquet. We’ll create 100 million records where each value is a 1000-character long randomly generated string. We then run a benchmark of 1000 queries that fetch a random set of 20–50 rows across the dataset. Both tests are done on the same Ubuntu 22.04 system:

```
sudo lshw -short
Class          Description
=============================================================
system         20M9CTO1WW (LENOVO_MT_20M9_BU_Think_FM_ThinkPad P52)
memory         128GiB System Memory
memory         32GiB SODIMM DDR4 Synchronous 2667 MHz (0.4 ns)
memory         32GiB SODIMM DDR4 Synchronous 2667 MHz (0.4 ns)
memory         32GiB SODIMM DDR4 Synchronous 2667 MHz (0.4 ns)
memory         32GiB SODIMM DDR4 Synchronous 2667 MHz (0.4 ns)
memory         384KiB L1 cache
memory         1536KiB L2 cache
memory         12MiB L3 cache
processor      Intel(R) Xeon(R) E-2176M  CPU @ 2.70GHz
storage        Samsung SSD 980 PRO 2TB
```

## Creating dataset

To run this benchmark we first generate 100 million entries, each of which is a 1000 character long string.

```
import lance
import pyarrow as pa
import random
import string

batch_size = 1_000_000

for i in range(100):
    print(f"Creating batch {i}")
    string_arr = pa.array([''.join(random.choices(string.ascii_letters, k=1_000))
                           for _ in range(batch_size)])
    tbl = pa.Table.from_arrays([string_arr], names=["value"])
    print(f"Writing batch {i} to lance")
    if i == 0:
        params = {"mode": "create"}
    else:
        params = {"mode": "append"}
    lance.write_dataset(tbl, "take.lance", **params)
```

Converting from Lance to parquet is just one line:

```
import lance
import pyarrow as pa

ds = lance.dataset("take.lance")
pa.dataset.write_dataset(ds.scanner().to_reader(),
                         "take.parquet",
                         format="parquet")
```

## Benchmarking Take

For both datasets, we run 1000 queries each. For each query, we generate 20–50 row id’s randomly and then retrieve those rows and record the run time. We then compute the average time per key.

The API we use is `Dataset.take`:

```
import time
import numpy as np
import lance

tot_time = 0
tot_keys = 0
nruns = 1000
ds = lance.dataset("take.lance")

for _ in range(nruns):
    nrows = np.random.randint(20, 50, 1)
    row_ids = np.random.randint(0, 100_000_000, nrows)
    start = time.time()
    tbl = ds.take(row_ids)
    end = time.time()
    tot_time += end - start
    tot_keys += len(row_ids)

print(f"Lance: mean time per key is {tot_time / tot_keys}")
```

The parquet snippet is almost identical, so it’s omitted.

Here’s the output (in seconds):

```
Lance: mean time per key is 0.0006225714343229975
Parquet: mean time per key is 1.246656603929473
```

I also benchmarked a similar setup using LMDB and plotted all on the same chart for comparison:

![1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311-fig-002](../images/1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311/figure-002.avif)

Throughput is computed as:

\(\frac{1}{\text{mean time per key}}\)

## Key lookup

If you’ve noticed, we’ve only benchmarked `Dataset::Take` on row ids. On the roadmap is to make this more generic so you can lookup arbitrary keys in any column.

Part of the limitation is in Lance itself. Currently looking up a particular key is done using a pyarrow Compute Expression, like the following:

```
dataset.to_table(columns=["value"], filter=pa.Field("key") == your_key)
```

Currently this requires scanning through the `key` column to find the right row ids, which adds more than 10ms to the query time. To solve this problem, we plan to a) calculate batch stats so we can b) implement batch pruning. And for super heavily queried key columns, c) adding a secondary index would make arbitrary key lookups much faster.

## DuckDB integration

In Python, Lance is already queryable by DuckDB via the [Arrow integration](https://duckdb.org/2021/12/03/duck-arrow). However, one major shortcoming of DuckDB’s Arrow integration is the extremely limited filter pushdown. For example, `pa.Field("key") == your_key` is pushed down across the pyarrow interface, but multiple key lookups is not. This can be the difference between <10ms response time vs >500ms response time. In Lance OSS, we’re working on a native duckdb extension so that we don’t have to be subject to these limitations.

## Conclusion

We’ve been claiming 100x faster random access performance than parquet, but as this benchmark shows, it’s really more like 2000x. Lance brings fast random access performance to the OSS data ecosystem needed by important ML workflows. This is critical for search, feature hydration, and shuffling for training deep learning models. While Lance’s performance is already very valuable for these use cases, we’ll be working to implement generalized key lookups, better duckdb integration, and hooks to distribute large Lance datasets across Spark/Ray nodes.

If any of these use cases apply to you, please give Lance a shot. We’d love to hear your feedback. If you like us, please give us a ⭐ on [️Github](https://github.com/lance-format/lance)!

![1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311-fig-003](../images/1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311/figure-003.avif)

[Chang She](/author/chang-she)

CEO and Co-Founder of LanceDB

[GitHub](https://github.com/changhiskhan)[Linkedin](https://www.linkedin.com/in/changshe/)[Twitter](https://x.com/changhiskhan)

![1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311-fig-004](../images/1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311/figure-004.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311-fig-005](../images/1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311/figure-005.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311-fig-006](../images/1448-https-www-lancedb-com-blog-benchmarking-random-a-e2555311/figure-006.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb