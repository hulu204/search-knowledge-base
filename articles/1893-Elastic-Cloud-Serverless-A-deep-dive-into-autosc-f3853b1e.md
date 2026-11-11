---
title: 'Elastic Cloud Serverless: A deep dive into autoscaling and performance stress testing at scale'
company: Elastic
tag: 工程相关
date: 2024-12-02
url: https://www.elastic.co/search-labs/blog/elastic-serverless-performance-stress-testing
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elastic Cloud Serverless: A deep dive into autoscaling and performance stress testing at scale

Dive into how Elasticsearch Cloud Serverless dynamically scales to handle massive data volumes and complex queries. We explore its performance under real-world conditions and the results from extensive stress testing.

December 02, 2024

[David Brimley](/search-labs/author/david-brimley)[Jason Bryan](/search-labs/author/jason-bryan)[Gareth Ellis](/search-labs/author/gareth-ellis)[Stewart Miles](/search-labs/author/stewart-miles)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

Jump to

Share

The advent of Elastic Cloud Serverless has reshaped how businesses can harness the power of Elasticsearch without the need to manage clusters, nodes, or resource scaling. A key innovation within Elastic Cloud Serverless is its autoscaling feature, which adapts to changes in workload and traffic in real-time. This post explores the technicalities behind autoscaling, the performance of Elastic Cloud Serverless under load, and the results from extensive stress testing.

### What is Elastic Cloud Serverless?

Elastic Cloud Serverless offers an automated, managed version of Elasticsearch that scales based on demand. Unlike traditional Elasticsearch deployments, where users must provision and manage hardware or cloud instances, Elastic Cloud Serverless manages infrastructure scaling and resource allocation. This is particularly beneficial for organizations with variable workloads, where scaling infrastructure up and down manually can be cumbersome and error-prone. The system’s built-in autoscaling feature accommodates heavy ingestion tasks, search queries, and other operations without manual intervention.

Elastic Cloud Serverless operates with two distinct tiers, the search and indexing tiers, each optimized for specific workloads. The search tier is dedicated to handling query execution, ensuring fast and efficient responses for search requests. Meanwhile, the indexing tier is responsible for ingesting and processing data, managing write operations, and ensuring data is properly stored and searchable. By decoupling these concerns, Elastic Cloud Serverless allows each tier to scale independently based on workload demands. This separation improves resource efficiency, as compute and storage needs for indexing (e.g., handling high-throughput ingestion) do not interfere with query performance during search operations. Similarly, search tier resources can be scaled up to handle complex queries or spikes in traffic without impacting the ingestion process. This architecture ensures optimal performance, cost-efficiency, and resilience, allowing Elastic Cloud Serverless to adapt dynamically to fluctuating workloads while maintaining consistent user experiences.

You can read more about the architecture of Elastic Cloud Serverless in the following [blog post](https://www.elastic.co/blog/elastic-serverless-architecture).

### Stress testing Elastic Cloud Serverless

Comprehensive stress tests assessed Elastic Cloud Serverless’s capability to handle large, fluctuating workloads. These tests were designed to measure the system’s ability to ingest data, handle search queries, and maintain performance under extreme conditions. It should be noted that the system can perform beyond what we present here, depending on factors such as client count and bulk index sizes. Here, we’ll walk through the approach and findings of these tests.

#### Testing scope and approach

The primary objective of our stress testing was to answer key questions:

* How well does Elastic Cloud Serverless handle large-scale ingestion and search queries with a high number of concurrent clients?
* Can it scale dynamically to accommodate sudden spikes in workload?
* Does the system maintain stability over extended periods?

#### Stress testing a search use case

In Elastic Cloud Serverless, you can choose from three project types: Elasticsearch, Observability, and Security. We began our stress test journey on search use cases for Elasticsearch, using a Github Archive dataset and simulating likely ingest and search behaviors. Before testing, we prepared the system by ingesting a base corpus of **186GB / 43 million documents.** We then gradually added clients over ten minutes to allow Elasticsearch the time to scale appropriately. The data was ingested using Datastreams via the Bulk APIs.

Stress testing the indexing tier.

Firstly, let's talk about indexing data (ingest). Ingest autoscaling in Elastic Cloud Serverless dynamically adjusts resources to match data ingestion demands, ensuring optimal performance and cost-efficiency. The system continuously monitors metrics such as ingestion throughput, resource utilization (CPU, memory, and network), and response latencies. When these metrics exceed predefined thresholds, the autoscaler provisions additional capacity proportionally to handle current and anticipated demand while maintaining a buffer for unexpected spikes. The complexity of data pipelines and system-imposed resource limits also influences scaling decisions. By dynamically adding or removing capacity, ingest autoscaling ensures seamless scaling without manual intervention.

In autoscaled systems like Elastic Cloud Serverless, where resource efficiency is optimized, there may be situations where a sudden, massive increase in workload exceeds the capacity of the system to scale immediately. In such cases, clients may receive HTTP 429 status codes, indicating that the system is overwhelmed. To handle these situations, clients should implement an exponential backoff strategy, retrying requests at progressively longer intervals. During stress testing, we actively track 429 responses to assess how the system reacts under high demand, providing valuable insights into autoscaling effectiveness.You can read a more in-depth blog post on how we autoscale indexing [here](https://www.elastic.co/search-labs/blog/elasticsearch-ingest-autoscaling). Now, let’s look at some of the results we encountered in our stress testing of the indexing tier.

*Indexing while scaling up:*

| Corpus | Bulk Size | Actual Volume | Indexing Period (minutes) | Volume / hr | Median Throughput (docs/s) | 90th PCT Indexing latency (seconds) | Avg. % Error Rate (429s, other) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1TB | 2500 | 1117.43 GB | 63 | 1064.22 GB | 70,256.96 | 7.095 | 0.05% |
| 2TB | 2500 | 2162.02 GB | 122 | 1063.29 GB | 68,365.23 | 8.148 | 0.05% |
| 5TB | 2500 | 5254.84 GB | 272 | 1159.16 GB | 74,770.27 | 7.46 | 0 |

For initial tests with **1TB and 2TB corpus**, we achieved a throughput of **1064 GB/hr** and **1063 GB/hr**, respectively. For **5TB** we achieved higher at **1160 GB / hr ingest**, as we observed the ingest tier continued to scale up, providing a better throughput.

*Indexing while fully scaled:*

| Clients | Bulk Size | Actual Volume | Duration | Volume / hr | Median Throughput (docs/s) | 99th PCT Indexing latency (seconds) | Avg. % Error Rate (429s, other) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3,000 | 2,000 | 1 TB | 8 minutes | 7.5 TB | 499,000 | 33.5 | 0.0% |

When working with a maximally scaled indexing tier, ECS ingested **1TB of data** in **8 minutes**, at a rate of **~499K docs/s** indexed per second. This equates to an extrapolated capacity of **180TB daily**.

*Indexing from minimal scale to maximum scale:*

| Clients | Bulk Size | Actual Volume | Duration | Volume / hr | Median Throughput (docs/s) | 99th PCT Indexing latency (seconds) | Avg. % Error Rate (429s, other) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2,048 | 1,000 | 13 TB | 6 hours | 2.1 TB | 146,478 | 55.5 | 1.55% |

During tests with **2TB of data**, we gradually scaled up to **2048 clients** and managed to ingest data at a rate of **146K docs/s**, completing **2TB** of data in **1 hour**. Extrapolated, this would result in **48TB per day**.

*72-Hour Stability Test:*

| Clients | Bulk Size | Actual Volume | Indexing Period (hours) | Volume / hr | Median Throughput (docs/s) | 99th PCT Indexing latency (seconds) | Avg. % Error Rate (429s, other) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 128 | 500 | 61 TB | 72 | ~868.6 GB | 51,700 | 7.7 | <0.05% |

In a **72-hour stability test**, we ingested **60TB** of data with **128 clients**. Elasticsearch maintained an impressive 870GB/hr throughput with minimal error rates while scaling the indexing and search tiers. This demonstrated Elasticsearch’s ability to sustain high throughput over extended periods with low failure rates.

Stress testing the search tier.

Search tier autoscaling in Elastic Cloud Serverless dynamically adjusts resources based on dataset size and search load to maintain optimal performance. The system classifies data into two categories: boosted and non-boosted. Boosted data includes time-based documents (documents with an `@timestamp` field) within a user-defined boost window and all non-time-based documents, while non-boosted data falls outside this window. Users can set a boost window to define the time range for boosted data and select a search power level—On-demand, Performant, or High-throughput—to control resource allocation. You can read more about configuring Search Power & Search Boost Windows [here](https://www.elastic.co/guide/en/serverless/current/elasticsearch-manage-project.html#elasticsearch-manage-project-search-ai-lake-settings).

The autoscaler monitors metrics such as query latency, resource utilization (CPU and memory), and query queue lengths. When these metrics indicate increased demand, the system scales resources accordingly. This scaling is performed on a per-project basis and is transparent to the end user.

*Search stability under load:*

| Corpus | Actual Volume (from corpus tab) | Duration | Average Search Rate (req/s) | Max Search Rate (req/s) | Response Time (P50) | Response Time (P99) |
| --- | --- | --- | --- | --- | --- | --- |
| 5TB | 5254.84 GB | 120 minutes | 891 | 3,158 | 36 ms | 316 ms |

With **5TB of data**, we tested a set of **8 searches** running over 2 hours, including complex queries, aggregations & ES|QL. Clients were ramped up from 4 to 64 clients per search. In total there were between 32 and 512 clients performing searches. Performance remained stable as the number of clients increased from **32 to 512.** When running with **512** clients, we observed a search request rate of **3,158 queries per second** with a **P50 response time of 36ms**.Throughout the test we observed the search tier scaling as expected to meet demand.

*24-hour search stability test:*

| Corpus | Actual Volume | Duration | Average Search Rate (req/s) | Max Search Rate (req/s) | Response Time (P50) | Response Time (P99) |
| --- | --- | --- | --- | --- | --- | --- |
| 40TB | 60 TB | 24 hours | 183 | 250 | 192 ms | 520 ms |

A set of 7 searches, aggregations, and an ES|QL query were used to query 40TB of (mainly) boosted data. The number of clients was ramped up from 1 to 12 per search, totaling 7 to 84 search clients. With Search Power set to balanced, we observed **192ms** (P50) response time. You can read more about configuring Search Power & Search Boost Windows [here](https://www.elastic.co/guide/en/serverless/current/elasticsearch-manage-project.html#elasticsearch-manage-project-search-ai-lake-settings).

*Concurrent index and search*

In tests that ran **simultaneous indexing** and **searching**, we aimed to ingest 5TB in 6 “chunks.” We ramped up from 24 to 480 clients ingesting data with a bulk size of 2500 documents. For search, clients were ramped up from 2 to 40 per search. In total, between 16 and 320 clients performed searches.

We observed both tiers autoscaling and saw **search latencies** consistently around **24ms** (p50) and **1359ms** (p99). The system’s ability to index and search concurrently while maintaining performance is critical for many use cases.

### Conclusion

The stress tests discussed above focused on a **search use case in an Elasticsearch project** designed with a specific configuration of field types, number of fields, clients, and bulk sizes. These parameters were tailored to evaluate Elastic Cloud Serverless under well-defined conditions relevant to the use case, providing valuable insights into its performance. However, it's important to note that the results may not directly reflect your workload, as performance depends on various factors such as query complexity, data structure, and indexing strategies.

These benchmarks serve as a baseline, but real-world outcomes will vary depending on your unique use case and requirements. It should also be noted that these results do not represent an upper performance bound.

The key takeaway from our stress testing is that Elastic Cloud Serverless demonstrates remarkable robustness. **It can ingest hundreds of terabytes of data daily while maintaining strong search performance.** This makes it a powerful solution for large-scale search workloads, ensuring reliability and efficiency at high data volumes. In upcoming posts, we will expand our exploration into stress testing Elastic Cloud Serverless for **observability** and **security** use cases, highlighting its versatility across different application domains and providing deeper insights into its capabilities.

### Frequently Asked Questions

#### What is Elastic Cloud Serverless?

Elastic Cloud Serverless offers an automated, managed version of Elasticsearch that scales based on demand.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### How we optimized refresh costs in Elasticsearch Serverless

July 31, 2024|[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltb2cd04a86700d5c2/6a17d715e3179138882d567d/016f5f2a90974dd53416d7d12f8776e802a0eef8-1440x823.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Ingest autoscaling in Elasticsearch

July 29, 2024|[Pooya Salehi](/search-labs/author/pooya-salehi)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3b371b70b12b9ef/6a170f240e2e49999441a1de/3c4c1e99b892f026b7aba098973593f8298e2ea6-1280x717.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elasticsearch replicas for load balancing in Serverless

March 24, 2026|[Andrei Dan](/search-labs/author/andrei-dan)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt84da396c370b06ec/6a170cfa6234e00dd3db1a55/d92e2e9fbae1dca1f18e623b2f5eb2a835307130-1600x1066.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Autosharding of data streams in Elasticsearch Serverless

December 10, 2024|[Andrei Dan](/search-labs/author/andrei-dan)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter