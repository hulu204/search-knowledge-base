---
title: 'Jingra: A Reproducible Framework for Vector Search Benchmarking'
company: Elastic
tag: 评测
date: 2026-06-18
url: https://www.elastic.co/search-labs/blog/jingra-vector-search-benchmark
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Jingra: A Reproducible Framework for Vector Search Benchmarking

Jingra is an open source benchmarking framework that runs the same vector search workload across Elasticsearch, OpenSearch and Qdrant so you can compare engines under identical, reproducible conditions.

June 18, 2026

[Sachin Frayne](/search-labs/author/sachin-frayne)

[Vector Database](/search-labs/blog/category/vector-database)[Java](/search-labs/blog/category/java-programming)

Jump to

Share

Stop guessing if your vector search benchmark results are accurate. [Jingra](https://github.com/elastic/jingra) is an open source, configuration driven framework that removes hidden warmup assumptions, inconsistent datasets, and vague definitions of when an index is actually ready to query. It runs the same dataset, workload, parameter sweeps, and reporting pipeline across [Elasticsearch](https://github.com/elastic/elasticsearch), [OpenSearch](https://github.com/opensearch-project/opensearch), and [Qdrant](https://github.com/qdrant/qdrant), producing reproducible recall versus latency curves you can rerun, compare, and trust.

## How Jingra benchmarks vector search engines: three phases

Jingra organizes benchmarking into three phases: Load, Eval, and Analyze. The point of this structure is simple: Every engine should be measured against the same dataset, workload, and reporting pipeline, under conditions you can control and reproduce.

| Phase | What it does |
| --- | --- |
| Load | Ingests data; waits for index readiness |
| Eval | Runs warmup and measurement; supports param sweeps |
| Analyze | Produces recall curves, latency plots and CSVs |

### 1. Load: Establishing a known state

The Load phase ingests the dataset into the engine under test using configurable parallelism. More importantly, it lets you decide what "ready" means before evaluation begins. In practice, finishing ingestion doesn’t always mean the system has reached a stable state. Elasticsearch may still be merging segments in the background, and Qdrant has its own post-ingest optimization behavior. Those background tasks can materially affect query latency.

Jingra makes that choice explicit with the `await_index_ready` setting. If enabled, evaluation waits until the index reaches the state you intend to measure instead of assuming that document ingestion alone is enough.

**Example load configuration:**

```
load:
  threads: 4
  batch_size: 100
  queue_capacity: 100
  await_index_ready: true
```

### 2. Eval: Capturing true performance trade-offs

The Eval phase runs the query workload in two steps: *warmup* and *measurement*. In the warmup step, Jingra executes the configured queries a fixed number of times before collecting any reported results. It doesn’t clear caches or reset engine state between warmup and measurement. The measurement step simply begins after those warmup iterations complete.

This makes the benchmark behavior explicit: Jingra is measuring post-warmup, steady-state performance for the configured workload rather than cold-start latency. Keeping warmup separate from measurement reduces first-run effects without introducing extra coordination logic between the two steps.

Jingra also supports parameter sweeps, so instead of reporting a single benchmark point, you can generate recall versus latency curves across multiple settings in one run.

**Example parameter sweep for recall versus latency:**

```
param_groups:
  recall@10:
    - { size: 10, k: 10, num_candidates: 10, oversample: 1 }
    - { size: 10, k: 20, num_candidates: 20, oversample: 1 }
    - { size: 10, k: 50, num_candidates: 50, oversample: 1 }
    - { size: 10, k: 100, num_candidates: 100, oversample: 1 }
    - { size: 10, k: 200, num_candidates: 200, oversample: 1 }
    - { size: 10, k: 500, num_candidates: 500, oversample: 1 }
    - { size: 10, k: 1000, num_candidates: 1000, oversample: 1 }
```

![A line graph showing recall on the vertical axis and latency on the horizontal axis. The curve rises steeply at first and then levels off near a dotted line, illustrating that recall approaches a limit as latency increases.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte5b620debe2d56e0/6a478a97cbd14e51e0a13c9a/19639bbfc01130b8a093b721a6621e724ace38b4-460x286.png)

Figure 1: Asymptotic recall versus latency plot that approaches a limit; higher num\_candidates and k will get us closer to the limit at the cost of time.

### 3. Analyze: Structured reporting

After evaluation completes, Jingra's Analyze phase produces recall curves, latency plots and structured CSVs for further analysis. Results can be written to different sinks, including console output for quick iteration or an Elasticsearch index for longer-term storage and dashboarding.

## Configuration-driven vector search benchmarking

Jingra is driven by YAML configuration rather than hard-coded benchmark logic. This makes benchmark definitions easy to commit and reuse, while keeping connection credentials in environment variables.

Switching between supported engines is straightforward. For example, you can swap `engine: qdrant` for `engine: elasticsearch` and point Jingra at a different cluster.

## How does Jingra ensure benchmark results are accurate and reproducible?

A focus on deterministic, credible results led to several core design choices:

* **No fixed sleeps for coordination.** Jingra uses synchronization primitives and readiness checks instead of arbitrary delays, which makes benchmark execution more deterministic.
* **Real engines in integration tests.** The test suite uses Testcontainers to run Elasticsearch, OpenSearch, and Qdrant directly rather than relying on mocks.
* **Defaults that reflect realistic operation.** Jingra doesn’t assume an artificially idealized index state unless you explicitly ask for one.
* **Strict quality gates.** The project enforces full instruction and branch coverage with JaCoCo on every build.

Jingra is built in Java because Java is a good fit for this kind of infrastructure software: It has mature concurrency primitives, strong testing tools, and a well-understood runtime model. It’s also the language I know best, which made it easier to focus on the benchmarking methodology rather than on the implementation details.

## How do I run a vector search benchmark with Jingra?

To get started quickly, the Jingra GitHub repository provides a set of end-to-end demos covering common benchmarking scenarios. These demos spin up an engine, download a public dataset, index it, and run the evaluation using Docker Compose, so no preexisting cluster is needed.

**Prerequisites:**

* Java 21
* Maven
* Docker
* `make`

The quickest way to try it is running one of the end-to-end demos:

```
cd demos/vector-search
make elasticsearch       # starts elasticsearch, loads data, runs benchmark, tears down
```

For custom scenarios, clone the repo, build the image, and run it directly against your own configuration:

```
docker run --rm \
  -e ELASTICSEARCH_URL \
  -v "$PWD/config.yaml:/config/jingra.yaml:ro" \
  <your-tag> load /config/jingra.yaml
```

The demo produces structured output that Jingra can turn into recall, latency, and throughput plots. The example below is illustrative only: It uses a very small dataset and a deliberately exaggerated workload so the demo generates visible curves quickly. These numbers are useful for showing the reporting flow, but they shouldn’t be interpreted as representative of production performance.

| RecallAtN | Engine | ParamKey | Recall | Recall Rounded | Latency\_Avg | Latency\_P95 | Throughput | Speedup |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| recall@10 | elasticsearch | k=10\_num\_candidates=10\_oversample=1\_size=10 | 0.9948 | 0.99 | 0.9602 | 1.1642 | 907.8117 |  |
| recall@10 | elasticsearch | k=20\_num\_candidates=20\_oversample=1\_size=10 | 0.9973 | 1 | 1.0704 | 1.5249 | 818.5483 |  |
| recall@10 | elasticsearch | k=50\_num\_candidates=50\_oversample=1\_size=10 | 0.9988 | 1 | 1.1183 | 1.4607 | 787.7582 |  |
| recall@10 | elasticsearch | k=100\_num\_candidates=100\_oversample=1\_size=10 | 0.9993 | 1 | 1.1017 | 1.3583 | 802.9065 |  |
| recall@10 | elasticsearch | k=200\_num\_candidates=200\_oversample=1\_size=10 | 0.9995 | 1 | 1.2505 | 1.5671 | 713.8778 |  |
| recall@10 | elasticsearch | k=500\_num\_candidates=500\_oversample=1\_size=10 | 0.9995 | 1 | 1.4175 | 1.7896 | 636.0211 |  |
| recall@10 | elasticsearch | k=1000\_num\_candidates=1000\_oversample=1\_size=10 | 0.9995 | 1 | 1.7012 | 2.0929 | 58.7924 |  |

From this output, Jingra can generate plots, such as:

![A line graph titled “Recall vs Latency avg — recall@10” showing recall on the vertical axis and average latency in milliseconds on the horizontal axis. A pink line labeled “elasticsearch” rises and then levels off, indicating that higher search effort improves recall while also increasing latency.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1c281fbc0e4751bc/6a478a95c71ec4337bb9942e/65418abe3e98dc76ef503ba5ae2f789be32d0968-800x500.png)

Figure 2: Recall versus latency curve, showing how higher search effort improves recall while increasing latency.

![A bar chart showing throughput in queries per second on the vertical axis and recall on the horizontal axis. Two pink bars labeled “elasticsearch” compare throughput at recall values 0.99 and 1.00, with the first bar slightly higher, illustrating that higher recall reduces throughput.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcc526e7d75efaed4/6a478a9a74bff77fe4a06aa2/07438c1033eae74565755c438c487c7d2789d9a8-800x500.png)

Figure 3: Throughput plot, showing the cost of those same parameter changes in queries per second.

In this demo, the workload is intentionally configured with 100 warmup rounds and 100 measurement rounds. That isn’t meant to model production traffic. It’s simply a convenient way to make the trade-off curves visible with a tiny dataset that would otherwise complete too quickly.

For production benchmarking, you should use larger datasets, realistic concurrency, and query volumes that reflect your actual workload. The purpose of this demo is to illustrate the benchmarking workflow and output format, not to establish performance baselines.

These demos currently focus on one engine at a time. A future release will include demos for engine versus engine comparisons, as well as profile versus profile comparisons within a single engine.

## Conclusion: run your own vector search benchmark

If you want to compare vector search engines on your own data, Jingra gives you a repeatable way to do it without building the whole harness yourself. Try one of the demos, run it against your workload, and compare engines under the same conditions.

The project is open source, licensed under Apache 2.0, and available on [GitHub](https://github.com/elastic/jingra).

## Frequently asked questions

**What is Jingra and what does it benchmark?**

Jingra is an open source framework for running reproducible vector search benchmarks across Elasticsearch, OpenSearch and Qdrant. It uses the same dataset, workload and reporting pipeline for every engine, making cross-engine comparisons consistent and trustworthy. It is licensed under Apache 2.0 and available on GitHub.

**Why do vector search benchmark results vary across different published studies?**

Most published benchmarks differ in hidden assumptions: when the index is considered ready, how many warmup queries are run, and whether background optimization tasks have completed. Jingra makes these choices explicit through configuration: `await_index_ready`, warmup rounds and measurement rounds are all defined in YAML and reproducible across runs.

**How does Jingra handle post-ingest index optimization in Elasticsearch and Qdrant?**

Both engines perform background work after document ingestion (Elasticsearch merges segments, Qdrant runs its own optimization) and these tasks can materially affect query latency. Jingra's `await_index_ready` setting holds the evaluation phase until the index reaches the intended measurement state, rather than starting queries immediately after the last document is indexed.

**How do I generate a recall versus latency curve with Jingra?**

Jingra supports parameter sweeps: you define multiple `num_candidates` and `k` settings in the `param_groups` block, and a single run evaluates all of them. The Analyze phase then produces a recall-versus-latency curve showing how higher search effort improves recall at the cost of increased latency.

**Can I run a Jingra benchmark without an existing cluster?**

Yes. The demos in the Jingra GitHub repository use Docker Compose to spin up an engine, download a public dataset, index it and run the full benchmark with a single `make` command. No pre-existing Elasticsearch, OpenSearch or Qdrant cluster is needed.

**What engines does Jingra support?**

Jingra currently supports Elasticsearch, OpenSearch and Qdrant. Additional engines are planned. Engine-versus-engine comparison demos are also planned for a future release.

**Is Jingra suitable for production benchmarking?**

Jingra is designed for production-grade studies, but the included demos use small datasets and exaggerated workloads to generate visible curves quickly. For meaningful production comparisons, use larger datasets, realistic concurrency, and query volumes that reflect your actual workload.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter