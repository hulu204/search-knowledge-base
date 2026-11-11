---
title: '98.9% faster queries, 4x more indexing throughput: a systematic Elasticsearch performance diagnosis'
company: Elastic
tag: 工程相关
date: 2026-07-15
url: https://www.elastic.co/search-labs/blog/elasticsearch-performance-diagnosis
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# 98.9% faster queries, 4x more indexing throughput: a systematic Elasticsearch performance diagnosis

Use AutoOps, the Profile API and ES Rally together to find cluster hotspots, slow queries and index bottlenecks, with real benchmarks showing a 98.9% latency cut and 4x indexing gain.

July 15, 2026

[Aleksandar Panov](/search-labs/author/aleksandar-panov)

[Operations](/search-labs/blog/category/operations)

Jump to

Share

Three Elastic tools (AutoOps, the Profile API and ES Rally) can systematically diagnose Elasticsearch performance problems at every layer of the stack. In a delivery logistics scenario, they revealed a shard imbalance causing 30-second search spikes, a deep-pagination query wasting 98.9% of its execution time, and index settings limiting bulk ingestion to a quarter of achievable throughput. This post walks through each tool, what it surfaces, and how to use the findings to fix the problem.

When dealing with dozens of users who actively connect and use your platform backed by an Elasticsearch cluster, it’s important to quickly grasp what potential bottlenecks are and how to overcome them. The main question is: Where to start? Here’s your potential decision path:

![Flowchart showing steps for diagnosing reported slowness. It starts with “Slowness reported” and then branches through decisions labeled “Cluster issue?,” “Slow query?,” and “Index settings?,” leading to boxes for AutoOps, Profile API, ES Rally, and Client-side bottleneck.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfdbd8c5fe90b986a/6a6119e2de948111c2d173b8/a7fd476e740648e7b92b0ddd27c69e47a4b37181-1240x1720.png)

The path starts with AutoOps to detect cluster-level problems, like resource pressure or bad shard distribution. If the cluster is healthy, the Profile API helps identify slow queries; candidates can come from the slow query log or application-side logging. Next, ES Rally benchmarks index settings that may limit throughput. If all three come back clean, the bottleneck is on the client side.

## How to detect cluster-level performance problems with AutoOps

The first question is always the same: Is the cluster itself the problem?

AutoOps is designed to provide real-time cluster diagnostics, deliver tailored advice, and help you improve the health of your clusters quickly. It comes by default in Elastic Cloud, and it has been added recently as a [free option for self-hosted configurations](https://www.elastic.co/blog/autoops-free).

It’s very easy to set it up, and it takes no more than five minutes to see data flowing into a comprehensive list of graphs that AutoOps offers you. The idea behind it is to install an [Elastic Agent](https://www.elastic.co/docs/deploy-manage/monitor/stack-monitoring/collecting-monitoring-data-with-elastic-agent) close to your cluster that reports back to the AutoOps platform which is connected with your Elastic Cloud account. Here’s the [installation guide](https://www.elastic.co/docs/deploy-manage/monitor/autoops/cc-connect-self-managed-to-autoops).

What’s nice about it is that it provides you with instant warnings and suggestions that are hard to spot through existing monitoring cluster technology. What’s really useful is that it also shows solutions to the issues.

In our delivery logistics scenario, AutoOps surfaced one finding that explained the user-reported slowness: severe load imbalance across the cluster. Node es01 was handling nearly all traffic while the other three sat idle, with search latency spiking to 30 seconds, as we'll see in the graphs in the next section.

### How AutoOps surfaces node hotspotting and shard imbalance

AutoOps node performance graphs revealed that es01 was handling nearly all indexing traffic (5.6 docs/sec) while es02, es03 and es04 were idle.

![Four line graphs, side by side, showing indexing and search rates and latencies for entities labeled es01, es02, es03, and es04 between 07:35 am and 07:45 am. Each graph has colored lines on a dark background, with legends listing rate and latency values in seconds and milliseconds.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt65864a5d75b374a5/6a6119e33c3320410f0b60d1/634bea76e349915ed037b03e0fe7b6c868ed0267-1999x704.png)

Below, we see that CPU usage was concentrated on a single node (es01) which was hosting the heavier index, while the other three nodes were mostly idle.

![Line graph labeled “CPU,” showing usage percentages for es01, es02, es03, and es04 between 04:25 pm and 04:35 pm. The es01 line rises to about 25% after 04:25 pm, drops near 0%, and then spikes to roughly 75% at 04:35 pm. The other lines remain flat at 0% throughout.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc9a24d81c58d7d2b/6a6119e4f817927d5d07f5f5/d50af8e45bf876144f8af0239a3e1d9e133baa69-706x1038.png)

The next signal of unusual behavior appeared in the search latency graph. Using the AutoOps per-node latency view, we uncovered some unexpected results.

![Line graph titled “Search latency” with a dropdown set to “Max.” The vertical axis ranges from 0 ms to 40 sec, and the horizontal axis shows times from 04:25 pm to 04:35 pm. Four lines represent es01, es02, es03, and es04. The es01 line spikes twice to about 30 seconds, while the other three remain flat near 0 ms.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3f72717314212aba/6a6119e5ae3a7c30f483eef6/3015134fd9f3684e57bff9593eb916990bc25ce7-706x1022.png)

While other nodes show no latency, the heavy-loaded node shows symptoms of latency that affects search apps. Not only was it a write node, but also it was the one serving all search requests. During analysis, we found that a delivery index was stored on only one node, instead of being distributed across all four. That was the root cause of the issue. By reindexing the data (with increased number of primary shards), we balanced the query load and eliminated the primary issue.

This article focuses on a single AutoOps finding to keep the diagnostic flow clear. For deeper dives into the kinds of issues AutoOps surfaces, see the dedicated articles on [hotspotting](https://www.elastic.co/search-labs/blog/hotspot-elasticsearch-autoops), [high CPU usage](https://www.elastic.co/search-labs/blog/elasticsearch-cpu-usage-high), and [long-running queries](https://www.elastic.co/search-labs/blog/slow-search-elasticsearch-query-autoops).

## How to find slow Elasticsearch queries using the Profile API

Once the cluster is healthy, the next question is: Are there specific, expensive queries? Finding candidates is the first step. You can explore them either by using [Elasticsearch’s slow query log](https://www.elastic.co/docs/deploy-manage/monitor/logging-configuration/slow-logs) or through application side logging, by measuring time required for every search request. In our case, infinite scroll on a tracking delivery screen was a problem while users would scroll deeper into results.

The [Profile API](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-profile) is a powerful tool for analyzing long-running queries and finding search bottlenecks. Getting started is simple: Just set `profile=”true”` in any of your search queries, and the responses will contain a profile section with detailed timing breakdown. It highlights which phase dominates execution time: the query phase, aggregations, or data fetching.

Let’s take a closer look at the [deep pagination case](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/paginate-search-results). In a case of infinite scroll in a mobile application, the user continues scrolling and the app responds by fetching 100 documents per request.

![Vertical interface showing a product list with a search bar labeled “Search products…” and a cart icon. Each entry includes a square placeholder, product name, optional category text, and price. Items listed include prices from $1400 to $1990. A “Show more” button appears at the bottom.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltccf8201277682a9c/6a6119e65144f742bab98961/f7470705f495daa62eee4a3ae7c956bcd02405b2-720x1280.jpg)

As users continues scrolling, the requests can reach very deep pagination levels, while the `from` parameter grows:

```
GET delivery-records/_search
{
    "profile": true,
    "from": 9000,
    "size": 100,
    "query": {
        "bool": {
            "filter": [
                {
                    "term": {
                        "payment_type": "1"
                    }
                },
                {
                    "range": {
                        "tax_amount": {
                            "gte": 5
                        }
                    }
                }
            ]
        }
    },
    "sort": [
        {
            "delivery_pickup_datetime": {
                "order": "desc"
            }
        }
    ]
}
```

The profile data, summarized below and converted from nanoseconds to milliseconds, makes the bottleneck clear: Most of the time is spent outside the query and fetch phases on coordination work caused by the large `from` offset. Elasticsearch must collect 9,100 matching documents, sort them, discard the first 9,000, and return only the requested 100.

| Component | Phase | Time |
| --- | --- | --- |
| ConstantScoreQuery contains | Query | 34.4ms |
| BooleanQuery | Query | 31.1ms |
| QueryPhaseCollector contains | Collect | 22.1ms |
| SimpleFieldCollector (9,100-doc priority queue) | Collect | 19.1ms |
| FetchPhase | Fetch | 12.1ms |
| Other steps, like request parsing and deserialization, queue wait time, response building |  | 1,885.4ms |
| Total |  | 2,004.2ms |

### Fixing deep pagination with search\_after

In this case, the `search_after` approach is up to twice as fast because it avoids scanning and discarding earlier results. Instead, it resumes from the last document returned on page 90, using its `delivery_pickup_datetime` value (in epoch milliseconds) as a cursor and fetching only the next 100 records.

```
GET delivery-records/_search
{
    "profile": true,
    "size": 100,
    "track_total_hits": false,
    "query": {
        "bool": {
            "filter": [
                {
                    "term": {
                        "payment_type": "1"
                    }
                },
                {
                    "range": {
                        "tax_amount": {
                            "gte": 5
                        }
                    }
                }
            ]
        }
    },
    "sort": [
        {
            "delivery_pickup_datetime": {
                "order": "desc"
            }
        }
    ],
    "search_after": [
        1451604674000
    ]
}
```

As shown in the comparison below, performances are much better with the `search_after` approach.

| Component | Phase | Time |
| --- | --- | --- |
| ConstantScoreQuery contains | Query | 6.8ms |
| BooleanQuery | Query | 6.2ms |
| QueryPhaseCollector contains | Collect | 2.6ms |
| PagingFieldCollector | Collect | 2.0ms |
| FetchPhase | Fetch | 2.2ms |
| Other steps like request parsing and deserialization, queue wait time, response building |  | 9.4ms |
| Total |  | 29.2ms |

### Performance comparison

| Component | Deep pagination (from:9000) | search\_after | Time saved | % Saved |
| --- | --- | --- | --- | --- |
| ConstantScoreQuery | 34.4ms | 6.8ms | 27.6ms | 80.2% |
| BooleanQuery | 31.1ms | 6.2ms | 24.9ms | 80.1% |
| QueryPhaseCollector (total) | 22.1ms | 2.6ms | 19.5ms | 88.2% |
| FieldCollect | 19.1ms | 2.0ms | 17.1ms | 89.5% |
| FetchPhase | 12.1ms | 2.2ms | 9.9ms | 81.8% |
| Total | 2,004.2ms | 29.2ms | 1,975ms | 98.5% |

The total query time drops from 1,004 ms to 29 ms (a 98.5% improvement) almost entirely because Elasticsearch no longer has to build and discard a 9,000-document priority queue on every request.

## How to benchmark Elasticsearch index settings with ES Rally

With the cluster healthy and queries optimized, the final question is: Are the index settings themselves a bottleneck?

[ES Rally](https://github.com/elastic/rally) is the official benchmarking tool made by Elastic. Its key strength is reproducibility: You run the same workload against two configurations on the same cluster and hardware, so any difference in results is purely down to the settings you changed. ES Rally is able to measure improvements under identical conditions: same cluster, hardware, and dataset.

### Why default Elasticsearch index settings limit bulk indexing throughput

In many cases, slow indexing is caused by default index settings that are suitable for development but not production. For instance, the default `refresh_interval` of 1 second increases resource usage because every [refresh creates a new searchable segment](https://www.elastic.co/docs/manage-data/data-store/near-real-time-search), and a replica count of 1 doubles the number of write operations per indexing request.

Our delivery logistics platform, for example, ingests thousands of new records daily in bulk, exactly the kind of workload where these defaults hurt. Setting `refresh_interval` to -1 disables refreshing during the bulk loading phase, and temporarily dropping replicas to 0 halves the write operations. Both settings are restored after the import is complete.

In this demo, we won’t focus on how to [prepare custom data](https://www.elastic.co/blog/creating-custom-es-rally-tracks-guide) for benchmarking, but it’s worth mentioning a nice article about it.

For benchmarking purposes, you set up two folders: one with the current settings and another with the contender settings. The sample dataset in this case contains 1 million records. All the files described below can be found in [this repository](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/how-to-benchmark-and-diagnose-your-applications/).

![File directory view labeled “rally-tracks,” showing two folders. Each folder contains four files, with icons indicating compressed and JSON file types](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte0a5ea88c39596e9/6a6119e71b1d4915a86f180f/7cf2cc18c22707bdc9e19e9da6d03fba05599c78-402x345.png)

Both track folders contain an `index-settings.json` file. These files let you adjust mappings, shard counts, replica settings, and field types; for example, converting a field from `double` to `scaled_float` or from `text` to `keyword`. Because ES Rally tracks can be rerun quickly, it’s easy to experiment with different configurations and evaluate new optimization ideas as you iterate.

The next step is to run race commands (for current and contender race) to gather stats.

```
esrally race \
--track-path="delivery-records-current" \ #(name of current setup folder)
--target-hosts="es01:9200" \ #(location of es cluster)
--pipeline=benchmark-only \
--report-format=csv \
--report-file="current.csv" \
--race-id="run-current" \
--on-error=abort
```

```
esrally race \
--track-path="delivery-records-contander" \
--target-hosts="es01:9200" \
--pipeline=benchmark-only \
--report-format=csv \
--report-file="contander.csv" \
--race-id="run-contander" \
--on-error=abort
```

Quick tip: Using meaningful `--race-id` values (rather than the auto-generated ones) makes the comparison command much easier to run.After both races are complete, compare the results:

```
esrally compare --baseline=run-current --contender=run-contander
```

![Terminal-style table titled “Final Score,” comparing performance metrics between baseline and contender configurations. Columns include Metric, Task, Baseline, Contender, Diff, Unit, and Diff %. Rows list indexing, merging, refreshing, flushing, garbage collection, dataset size, and throughput data. Green text indicates improvements, and red text indicates regressions.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt41dd2371798de2f6/6a6119e81c2893300b6e5ceb/1c4bb14953cffcfa07542c1ae73528645388a50a-1620x1736.png)

Additionally, reports are generated into csv files that can be easily manipulated to extract important data.

| Metric | Current settings | Contender | Change |
| --- | --- | --- | --- |
| Cumulative indexing time | 0,826517 | 0,755967 | +8.54% |
| Mean throughput | 11,090 docs/s | 50,921 docs/s | +359 % |
| Median throughput | 10,821 docs/s | 51,304 docs/s | +374 % |
| Min throughput | 10,335 docs/s | 41,387 docs/s | +300 % |
| Max throughput | 13,006 docs/s | 55,342 docs/s | +326% |

The contender configuration delivers roughly 3–4× faster indexing throughput, purely from adjusting refresh\_interval and replica count during the bulk load phase.

In practice, a single comparison is rarely enough. Common follow-up experiments include converting double fields to float or scaled\_float, changing text fields to keyword, adjusting shard count, and tuning the refresh interval. Because ES Rally tracks rerun quickly, iterating through these options is straightforward.

## What to do when Elasticsearch isn't the bottleneck

If AutoOps shows a healthy cluster, the Profile API shows fast queries, and ES Rally confirms that index settings are not the limiting factor, the bottleneck is on the client side. The Elasticsearch side is no longer the place to look. Common application-layer causes:

* **Network latency** between the client and the cluster, especially across regions, VPNs, or proxies.
* **Client-side deserialization** overhead on large response payloads. Use [`_source exclude`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/mapping-source-field#include-exclude) or the [`fields`](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrieve-selected-fields#search-fields-param) parameter to return only what the client actually needs.
* **Client-side queueing** before requests reach the cluster. The Elasticsearch client uses an HTTP connection pool. Under concurrent load, requests wait in line for a free connection. The Profile API never sees this wait because the request hasn't left the client yet.
* **Single search calls** where [`_msearch`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-msearch) would batch independent queries into one network round trip.
* **Single-document indexing** where the [`_bulk`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk) API would amortize per-request overhead across many documents.

The diagnostic value of AutoOps, the Profile API, and ES Rally is precisely that they let you definitively rule out the cluster, the query, and the index settings before turning to the application code. When the three tools come back clean, the investigation moves out of Elasticsearch and into the client.

For investigating these on the application side, [Elastic APM](https://www.elastic.co/observability/application-performance-monitoring) is the natural next tool: It traces request paths through the client and surfaces exactly the kind of pre-cluster wait time the Profile API can't see.

## Conclusion

Going back to the original problem, slow search on a delivery logistics platform, we traced the issue from the infrastructure level down to the query and settings level:

* AutoOps revealed an uneven shard distribution that concentrated all query load on a single node, causing latency spikes of up to 30 seconds for end users.
* The Profile API showed that deep pagination was the source of the slow queries. Switching from from/size to `search_after` eliminated 98.9% of the latency.
* ES Rally confirmed that optimizing index settings during bulk ingestion, specifically `refresh_interval` and replica count, can increase throughput by 3-4×.

Each tool answers a different question. AutoOps gives you the "Is something structurally wrong?" view. The Profile API answers "Why is this specific query slow?" And ES Rally validates "Do these changes actually improve things, and by how much?" Used together and in this order, they cover the full diagnostic surface for the Elasticsearch side of the application. When all three come back clean, the next step is to look at the client, as outlined in the previous section.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3979255ddfc7f45/6a17e25ffaa913812f93c7cb/92c517a2e7b36122a18feee317a0215981b62b6b-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Operations](/search-labs/blog/category/operations)

### Your agents have been keeping receipts: turning Elastic Agent Builder's built-in OTel traces into token cost dashboards in Kibana

July 28, 2026|[Meghan Murphy](/search-labs/author/meghan-murphy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd9be3378b7b18d00/6a6a33c6d137a512563e106b/86ddf69cfc68919fb0f708eb190c18fdc2b9479a-1999x1200.png)

[AutoOps](/search-labs/blog/category/autoops)[Elastic Cloud Hosted](/search-labs/blog/category/elastic-cloud-hosted)[Operations](/search-labs/blog/category/operations)

### Faster Elasticsearch issue triage with redesigned AutoOps

July 23, 2026|[Ori Shafir](/search-labs/author/ori-shafir)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt69260cf1c6f964e3/6a17db030b0bed6f52dd346e/5d64716981e76396b401fd069d0a635b6929ba94-720x420.jpg)

[Operations](/search-labs/blog/category/operations)

### Multi-tier search with Elastic for ecommerce search governance: Fixing poor recall

May 06, 2026|[Alexander Marquardt](/search-labs/author/alexander-marquardt)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt840c7a0a5b92080f/6a1710f967045b3e5445c2cd/3793259b01a5653a7520393a2f006610de0d21e7-1280x720.png)

[Operations](/search-labs/blog/category/operations)

### Why ecommerce search needs governance

April 09, 2026|[Alexander Marquardt](/search-labs/author/alexander-marquardt)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter