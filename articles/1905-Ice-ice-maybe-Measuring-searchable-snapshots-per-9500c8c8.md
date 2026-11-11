---
title: 'Ice, ice, maybe: Measuring searchable snapshots performance'
company: Elastic
tag: 工程相关
date: 2025-01-13
url: https://www.elastic.co/search-labs/blog/searchable-snapshots-benchmark
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Ice, ice, maybe: Measuring searchable snapshots performance

Learn how Elastic’s searchable snapshots enable the frozen tier to perform on par with the hot tier, demonstrating latency consistency and reducing costs.

January 13, 2025

[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)[Radovan Ondas](/search-labs/author/radovan-ondas)[George Kobar](/search-labs/author/george-kobar)[Jonathan Simon](/search-labs/author/jonathan-simon)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

The frozen data tier can achieve both low cost and good performance by leveraging Elastic's Searchable Snapshots - which offer a compelling solution for managing vast amounts of data while maintaining the performant searchability of data within a budget.

In this article, we delve into a benchmark of Elastic's hot and frozen data tiers by running sample queries on 105 terabytes of logs spanning more than 90 days. These queries replicate common tasks within Kibana's Discover, including search with highlighting, total hits, date histogram aggregation, and terms aggregation; that all happen behind the scenes when a user triggers a simple search. The results reveal that Elastic's frozen data tier is quick and delivers latency comparable to its hot tier, with only the first query to the object store being slower - subsequent queries are fast.

We replicated the way a typical user would interact with a hot-frozen deployment through Kibana's Discover - its main interface for interacting with indexed documents.

![Interacting with data tiers in elastic](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte834663d013093fa/6a17e06fb1e113418b79f1b7/4769b35c41cd5da6045c8ba69e4f758774cc7dce-1183x488.gif)

When a user issues a search using Discover's search bar three tasks are executed in parallel:

* a search and highlight operation on 500 docs that doesn't track the total amount of hits (referred as `discover_search` tasks on the results)
* a search that tracks the total hits (`discover_search_total` in the results)
* a date histogram aggregation to construct the bar chart (referred as `discover_date_histogram`)

and also

* a terms aggregation (referred as `discover_terms_agg`) when/if the user clicks the left side bar.

## Data tiers in Elastic

Some types of data decrease in value over time. It's natural to think about application logs where the most recent records are usually the ones that need to be queried more frequently and also need the fastest possible response time. But there are several other examples of such data like **medical records** (detailed patient histories, diagnoses and physician notes); **legal documents** (contracts, court rulings, case files, etc.) and **bank records** (transaction records including descriptions of purchases and merchant names)-just to cite three. All contain unstructured or semi-structured text that requires efficient search capabilities to extract relevant information. As these records age, their immediate relevance may diminish, but they still hold significant value for historical analysis, compliance, and reference purposes.

Elastic's data tiers — Hot, Warm, Cold, and Frozen– provide the ideal balance of speed and cost, ensuring you maximize the value of these types of data as they age without sacrificing usability. Through both Kibana and Elasticsearch's search API the use of the underlying data tiers is always automatic and transparent–users don't need to issue search queries in a different way to retrieve data from any specific tier (no need to manually restore the data, or "rehydrate").

In this blog we keep it simple by using solely the Hot and Frozen tiers, in what is commonly called a **hot-frozen** scenario.

### How the frozen tier works

In a hot-frozen scenario, data begins its journey in the hot tier, where it is actively ingested and queried. The hot tier is optimized for high-speed read and write operations, making it ideal for handling the most recent and frequently accessed data. As data ages and becomes less frequently accessed, it is transitioned to the frozen tier to optimize storage costs and resource utilization.

The transition from the hot tier to the frozen tier involves converting the data into searchable snapshots. Searchable snapshots leverage the snapshot mechanism used for backups, allowing the data to be stored in a cost-effective manner while still being searchable. This eliminates the need for replica shards, significantly reducing the local storage requirements.

Once the data is in the frozen tier, it is managed by nodes specifically designated for this purpose. These nodes do not need to have enough disk space to store full copies of all indices. Instead, they utilize an on-disk Least Frequently Used (LFU) cache. This cache stores only portions of the index data that are downloaded from the blob store as needed to serve queries. The on-disk cache functions similarly to an operating system's page cache, enhancing access speed to frequently requested parts of the data.

When a query is executed in the frozen tier, the process involves several steps to ensure efficient data retrieval and caching:

**1. Read requests mapping**: At the Lucene level, read requests are mapped to the local cache. This mapping determines whether the requested data is already present in the cache.

**2. Cache mishandling**: If the required data is not available in the local cache (a cache miss), Elasticsearch handles this by downloading a larger region of the Lucene file from the blob store. Typically, this region is a 16MB chunk, which is a balance between minimizing the number of fetches and optimizing the amount of data transferred.

**3. Adding data to cache**: The downloaded chunk is then added to the local cache. This process ensures that subsequent read requests for the same region can be served directly from the local cache, significantly improving query performance by reducing the need to repeatedly fetch data from the blob store.

**4. Cache configuration options**:

* **Shared cache size**: This setting accepts either a percentage of the total disk space or an absolute byte value. For dedicated frozen tier nodes, the default is 90% of the total disk space.

```
xpack.searchable.snapshot.shared_cache.size: 4TB
```

* **Max headroom**: Defines the maximum headroom to maintain. If not explicitly set, it defaults to 100GB for dedicated frozen tier nodes.

```
xpack.searchable.snapshot.shared_cache.size.max_headroom: 100GB
```

**5. Eviction policy**: The node-level shared cache uses a LFU policy to manage its contents. This policy ensures that frequently accessed data remains in the cache, while less frequently accessed data is evicted to make room for new data. This dynamic management of the cache helps maintain efficient use of disk space and quick access to the most relevant data.

**6. Lucene index management**: To further optimize resource usage, the Lucene index is opened only on-demand—when there is an active search. This approach allows a large number of indices to be managed on a single frozen tier node without consuming excessive memory.

### Methodology

We ran the tests on a six node cluster in [Elastic Cloud](https://cloud.elastic.co/) hosted on Google Cloud Platform on [N2 family](https://cloud.google.com/compute/docs/general-purpose-machines#n2_series) nodes:

* 3 x `gcp.es.datahot.n2.68x10x45` - Storage-optimized Elasticsearch instances for hot data.
* 3 x `gcp.es.datafrozen.n2.68x10x90` - Storage-optimized (dense) Elasticsearch instances serving as a cache tier for frozen data.

We measured the following spans, which also equate to Terabytes in size, since we indexed one Terabyte per day.

![Elastic searchable snapshots and frozen tier performance](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3e6f3c7e2170a9a9/6a17e071fbc5f87ac94919b7/9abf22d67855f1fc94494f2b93494672b05847ea-1296x344.webp)

We used [Rally](https://github.com/elastic/rally) to run the tests, below is a sample `test` relative to an uncached search on one day of frozen data (`discover_search_total-1d-frozen-nocache`), `iterations` refer to the number of times the entire set of operations is repeated, which in this case is 10. Each `operation` defines a specific task or set of tasks to be performed, and in this example, it is a composite operation. Within this operation, there are multiple `requests` that specify the actions to be taken, such as clearing the frozen cache by issuing a `POST` request. The `stream` within a request indicates a sequence of related actions, such as submitting a search query and then retrieving and deleting the results.

```
{
  "iterations": 10,
  "operation": {
    "operation-type": "composite",
    "name": "discover_search_total-1d-frozen-nocache",
    "requests": [
      {
        "name": "clear-frozen-cache",
        "operation-type": "raw-request",
        "path": "/_searchable_snapshots/cache/clear",
        "method": "POST"
      },
      {
        "stream": [
          {
            "name": "async-search",
            "operation-type": "submit-async-search",
            "index": "hotfrozenlogs",
            "request-params": {
              "track_total_hits": "true"
            },
            "body": {
              "_source": false,
              "size": 0,
              "query": {
                "bool": {
                  "filter": [
                    {
                      "multi_match": {
                        "type": "best_fields",
                        "query": "elk lion rider",
                        "lenient": true
                      }
                    },
                    {
                      "range": {
                        "@timestamp": {
                          "format": "strict_date_optional_time",
                          "gte": "2024-02-15T00:00:00",
                          "lt": "2024-02-16T00:00:00"
                        }
                      }
                    }
                  ]
                }
              },
              "stored_fields": [
                "*"
              ],
              "fields": [
                {
                  "field": "@timestamp",
                  "format": "date_time"
                }
              ]
            }
          }
        ]
      },
      {
        "operation-type": "get-async-search",
        "retrieve-results-for": [
          "async-search"
        ]
      },
      {
        "operation-type": "delete-async-search",
        "delete-results-for": [
          "async-search"
        ]
      }
    ]
  }
}
```

Each test would run for 10 times per benchmark run, and we performed 500 benchmark runs across several days, therefore the sample for each task is 5,000. Having a high amount of measurements is essential when we want to ensure statistical significance and reliability of the results. This large sample size helps to smooth out anomalies and provides a more accurate representation of performance, allowing us to draw meaningful conclusions from the data.

## Results

The detailed results are outlined below. The "tip of the candle" represents the max (or **p100**) value observed within all the requests for a specific operation, and they are grouped by tier. The green value represents the **p99.9**, or the value below what 99.9% of the requests would fall.

Due to how Kibana interacts with Elasticsearch–which is via async searches–a more logical way of representing the time is by using horizontal bar charts as below. Since the requests are asynchronous and parallel, they will complete at different times. You don't have to wait for all of them to start seeing query results, and this is how we read the benchmark results.

![Results of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt675f4d86947f022c/6a17e0737f6f15dc29c09a4e/bb505a8dacb4a8ead7007aa8db0886ba27d6aa51-1152x648.gif)

The results are expressed as, for example, **543ms - 2s** where **543ms** is when we received the first result and **2s** when we received the last.

#### 1 Day Span / 1 Terabyte

What we observed 99.9% of the times (p99.9):

* Hot: 543ms - 2s
* Frozen Not Cached: 1.8s - 14s
* Frozen Cached: 558ms - 11s

What we observed as a maximum latency (likely the very first query):

* Hot: 630ms - 2s
* Frozen Not Cached: 1.9s - 28s
* Frozen Cached: 750ms - 19s

![Results 1 Day Span / 1 Terabyte of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltad459f23ad535b69/6a17e0740b0bed3b06dd34d4/2670ae8e4ee54c49ac0b6cf79b5648173ee721ef-2700x2100.webp)

#### 7 Days Span / 7 Terabytes

What we observed 99.9% of the times (p99.9):

* Hot: 555ms - 792s
* Frozen Not Cached: 2.5s - 14s
* Frozen Cached: 1s - 12s

What we observed as a maximum latency (likely the very first query):

* Hot: 842ms - 4s
* Frozen Not Cached: 2.5s - 5.6m (336s)
* Frozen Cached: 1.1s - 26s

![results 7 Days Span / 7 Terabytes of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta7c3099f63eee280/6a17e076e8fbce01de3a184f/a1210881d723b7f486437320709d1e6f17551c89-2700x2100.webp)

#### 14 Days Span / 14 Terabytes

What we observed 99.9% of the times (p99.9):

* Hot: 551ms - 608ms
* Frozen Not Cached: 1.8s - 15s
* Frozen Cached: 551ms - 592ms

What we observed as a maximum latency (likely the very first query):

* Hot: 785ms - 9s
* Frozen Not Cached: 2.3s - 32s
* Frozen Cached: 624ms - 7s

![results 14 Days Span / 14 Terabytes of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc49527ecbc7d4c1c/6a17e077e8fbcec58f3a1853/2b03612035c99a75cc77d94584ef6227fddf7884-2700x2100.webp)

#### 30 Days Span / 30 Terabytes

We did not use hot data past 14 days on this test, but we can still use the results for frozen as a reference.

What we observed 99.9% of the times (p99.9):

* Frozen Not Cached: 2.3s - 12s
* Frozen Cached: 1s - 11s

What we observed as a maximum latency (likely the very first query):

* Frozen Not Cached: 2.4s - 68s
* Frozen Cached: 1.1s - 27s

![results 30 Days Span / 30 Terabytes of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt35020123b4f97943/6a17e0794b055da0f943210b/b34e72665174f988d4a09407622da9b2c10c2b50-2700x2100.webp)

#### 60 Days Span / 60 Terabytes

What we observed 99.9% of the times (p99.9):

* Frozen Not Cached: 2.3s - 13s
* Frozen Cached: 1s - 11s

What we observed as a maximum latency (likely the very first query):

* Frozen Not Cached: 2.4s - 18s
* Frozen Cached: 1.1s - 240s

![results 60 Days Span / 60 Terabytes of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta3096f7773e607d8/6a17e07b14800993e2b48686/e3d65792424d9708020ce65e13e9ad3b39b8080d-2700x2100.webp)

#### 90 Days Span / 90 Terabytes

What we observed 99.9% of the times (p99.9):

* Frozen Not Cached: 2.4s - 13s
* Frozen Cached: 1s - 11s

What we observed as a maximum latency (likely the very first query):

* Frozen Not Cached: 3.3s - 5m (304s)
* Frozen Cached: 1.1s - 1.6m (98s)

![results 90 Days Span / 90 Terabytes of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt75ea10e1d11ef31c/6a17e07c3e9e459affba1395/ff62f2d4e5293ea4e61d317ca33bab0530950a8e-2700x2100.webp)

## Cost implications (16x reduction)

Let's make a simple pricing exercise using Elastic Cloud.

If we were to put the entirety of a 90 days / 90 TB dataset in an all-hot deployment on the most performant hardware profile for large datasets ([Storage Optimized](https://www.elastic.co/guide/en/cloud/current/ec-reference-hardware.html)), that would cost $53.382 / month since we would need about 45 hot nodes to cover about 120TB.

![Cost implications of using elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5e5e4e785035fc29/6a17e07e42022966c629f520/aa12bae7e9313a630cc9d0ebd78247aad896895d-1394x778.jpg)

Since Elastic Cloud has different hardware profiles, we could also select Storage optimized (dense), which brings the cost to $28.222.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt079f1abfeeb0ad05/6a17e080b1e11382c679f1bb/8123251a953f6e410ab8cedd6fa1760e4bee5a4b-1408x786.jpg)

However, by benefiting from the Frozen tier, we could make a deployment that holds 1 day in Hot and the rest on Frozen. The cost of such deployment can be as low as $3.290, a staggering **16x reduction on costs**.

![Storage optimized due to the use of elastic searchable snapshots on frozen tier](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4fa0447849de9f2b/6a17e081631730fd6f5859c1/7a360b479e0b3106ab8c170e17b4032ff98b5964-1454x812.webp)

## Use Elastic's frozen data tier to cool down the cost of data storage

Elastic's frozen data tier redefines what's possible in data storage and retrieval. Benchmark results show that it delivers performance comparable to the hot tier, efficiently handling typical user tasks. While rare instances of slightly higher latency (0.1% of the time) may occur, Elastic's searchable snapshots ensure a robust and cost-effective solution for managing large datasets. Whether you're searching through years of security data for advanced persistent threats or analyzing historical seasonal trends from logs and metrics, searchable snapshots and the frozen tier deliver unmatched value and performance. By adopting the frozen tier, organizations can optimize storage strategies, maintain responsiveness, keep data searchable, and stay within budget.

To learn more, see [how to set up hot and frozen data tiers](https://www.elastic.co/blog/optimize-logs-cost-hot-frozen-data-tier) for your Elastic Cloud deployment.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter