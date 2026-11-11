---
title: 'A Practical Guide to Deploying Search Foundation Models in Production'
company: Jina
tag: 工程相关
date: 2025-01-31
url: https://jina.ai/news/a-practical-guide-to-deploying-search-foundation-models-in-production/
account: 
origin: harvest2-202607
---
At Jina AI, our mission is to provide enterprise users with high-quality search solutions. To achieve this, we make our models accessible through various channels. However, choosing the right channel for your specific use case can be tricky. In this post, we'll walk you through the decision-making process and break down the trade-offs, giving you practical guidance on the best way to access our search foundation models based on your user profile and needs.

## [*tag*](#jina-search-foundation-models "Jina Search Foundation Models")Jina Search Foundation Models

[Our Search Foundation Models

We’ve been moving the needle in search models since day one. Take a look at our model evolution below—hover or click to discover each milestone.

![](https://cms.jina.ai/content/images/icon/favicon-128x128-18.png)Jina AI

![](https://cms.jina.ai/content/images/thumbnail/banner-models.png)](https://jina.ai/models/)

Our search foundation models include:

* **Embeddings**: These convert information about digital objects into embedding vectors, capturing their essential characteristics.
* **Rerankers**: These perform in-depth semantic analysis of query-document sets to improve search relevance.
* **Small language models**: These include specialized SLM like [ReaderLM-v2](/models/ReaderLM-v2) for niche tasks such as HTML2Markdown or information extraction.

In this post, we'll examine different deployment options for [jina-embeddings-v3](/?sui&model=jina-embeddings-v3), comparing three key approaches:

* Using [Jina API](https://jina.ai/api-dashboard)
* Deploying via CSP like [AWS SageMaker](https://aws.amazon.com/marketplace/pp/prodview-kdi3xkt62lo32)
* Self-hosting on a Kubernetes cluster [under a commercial license](https://jina.ai/api-dashboard/license-config)

The comparison will evaluate the cost implications and advantages of each approach to help you determine the most suitable option for your needs.

## [*tag*](#key-performance-metrics "Key Performance Metrics")Key Performance Metrics

We evaluated five key performance metrics across different usage scenarios:

* **Request Success Rate**: The percentage of successful requests to the embedding server
* **Request Latency**: The time taken for the embedding server to process and return a request
* **Token Throughput**: The number of tokens the embedding server can process per second
* **Cost per Token**: The total processing cost per text unit

For self-hosted Jina embeddings on Kubernetes clusters, we also examined the impact of *dynamic batching*. This feature queues requests until reaching the maximum batch size (8,192 for [jina-embeddings-v3](/?sui&model=jina-embeddings-v3)) before generating embeddings.

We intentionally excluded two significant performance factors from our analysis:

* *Auto-scaling*: While this is crucial for cloud deployments with varying workloads, its effectiveness depends on numerous variables—hardware efficiency, network architecture, latency, and implementation choices. These complexities are beyond our current scope. **Note that Jina API includes automatic scaling, and our results reflect this.**
* *Quantization*: While this technique creates smaller embedding vectors and reduces data transfer, the main benefits come from other system components (data storage and vector distance calculations) rather than reduced data transfer. Since we're focusing on direct model usage costs, we've left quantization out of this analysis.

Finally, we'll examine the financial implications of each approach, considering both total ownership costs and per-token/per-request expenses.

## [*tag*](#deployment-setup "Deployment Setup")Deployment Setup

We evaluated three deployment and usage scenarios with [jina-embeddings-v3](/?sui&model=jina-embeddings-v3):

### [*tag*](#using-the-jina-api "Using the Jina API")Using the Jina API

All Jina AI embedding models are accessible via [Jina API](https://jina.ai/api-dashboard/embeddings). Access works on a prepaid token system, with a million tokens available free for testing. We evaluated performance by making API calls over the internet from our German offices.

### [*tag*](#using-aws-sagemaker "Using AWS SageMaker")Using AWS SageMaker

Jina Embeddings v3 is [available to AWS users via SageMaker](https://aws.amazon.com/marketplace/pp/prodview-kdi3xkt62lo32). Usage requires an AWS subscription to this model. For example code, we have [provided a notebook](https://github.com/jina-ai/jina-sagemaker/blob/main/notebooks/Real-time%20embedding.ipynb) that shows how to subscribe to and use Jina AI models with an AWS account.

While the models are also available on [Microsoft Azure](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/jinaai.jina-embeddings-v3-vm?tab=Overview) and [Google Cloud Platform](https://console.cloud.google.com/marketplace/browse?hl=en&inv=1&invt=AboIuQ&q=jina), we focused our testing on AWS. We expect similar performance on other platforms. All tests ran on a `ml.g5.xlarge` instance in the `us-east-1` region.

### [*tag*](#self-hosting-on-kubernetes "Self-Hosting on Kubernetes")Self-Hosting on Kubernetes

💡

To obtain commercial licensing for our CC-BY-NC models, you first need to get a license from us. [Please feel free to contact our sales team.](https://jina.ai/api-dashboard/license-config)

We built a FastAPI application in Python that [loads](https://huggingface.co/jinaai/jina-embeddings-v3) [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) from HuggingFace using the `SentenceTransformer` library. The app includes two endpoints:

* `/embed`: Takes text passages as input and returns their embeddings
* `/health`: Provides basic health monitoring

We deployed this as a Kubernetes service on Amazon's Elastic Kubernetes Service, using a `g5.xlarge` instance in `us-east-1`.

#### With and Without Dynamic Batching

We tested performance in a Kubernetes cluster in two configurations: One where it immediately processed each request when it received it, and one where it used dynamic batching. In the dynamic batching case, the service waits until `MAX_TOKENS` (8192) are collected in a queue, or a pre-defined timeout of 2 seconds is reached, before invoking the model and calculating the embeddings. This approach increases GPU utilization and reduces fragmentation of the GPU memory.

For each deployment scenario, we ran tests varying three key parameters:

* **Batch size**: Each request contained either 1, 32, or 128 text passages for embedding
* **Passage length**: We used text passages containing 128, 512, or 1,024 tokens
* **Concurrent requests**: We sent 1, 5, or 10 requests simultaneously

## [*tag*](#benchmark-results "Benchmark Results")Benchmark Results

The table below is a summary of results for each usage scenario, averaging over all settings of the three variables above.

| Metric | Jina API | SageMaker | Self-Hosted with Batching | Self-Hosted Standard |
| --- | --- | --- | --- | --- |
| Request Success Rate | 87.6% | **99.9%** | 55.7% | 58.3% |
| Latency (seconds) | 11.4 | 3.9 | 2.7 | **2.6** |
| Normalized Latency by Success Rate (seconds) | 13.0 | **3.9** | 4.9 | 4.4 |
| Token Throughput (tokens/second) | 13.8K | **15.0K** | 2.2K | 2.6K |
| Peak Token Throughput (tokens/second) | **63.0K** | 32.2K | 10.9K | 10.5K |
| Price (USD per 1M tokens) | $0.05 | $0.07 | $0.32 | $0.32 |

## [*tag*](#request-success-rate "Request Success Rate")Request Success Rate

Success rates in our testing range from SageMaker's near-perfect 99.9% to self-hosted solutions' modest 56-58%, highlighting why 100% reliability remains elusive in production systems. Three key factors contribute to this:

* Network instability causes unavoidable failures even in cloud environments
* Resource contention, especially GPU memory, leads to request failures under load
* Necessary timeout limits mean some requests must fail to maintain system health

### [*tag*](#success-rate-by-batch-size "Success Rate By Batch Size")Success Rate By Batch Size

Large batch sizes frequently cause out-of-memory errors in the self-hosted Kubernetes configuration. Without dynamic batching, all requests containing 32 or 128 items per batch failed for this reason. Even with dynamic batching implemented, the failure rate for large batches remained significantly high.

| Batch Size | Jina API | SageMaker | Self-Hosted (Dynamic Batching) | Self-Hosted (No Batching) |
| --- | --- | --- | --- | --- |
| 1 | 100% | 100% | 97.1% | 58.3% |
| 32 | 86.7% | 99.8% | 50.0% | 0.0% |
| 128 | 76.2% | 99.8% | 24.0% | 0.0% |

While this issue could be readily addressed through auto-scaling, we have chosen not to explore that option here. Auto-scaling would lead to unpredictable cost increases, and it would be challenging to provide actionable insights given the vast number of auto-scaling configuration options available.

### [*tag*](#success-rate-by-concurrency-level "Success Rate By Concurrency Level")Success Rate By Concurrency Level

Concurrency — the ability to handle multiple requests simultaneously — had neither a strong nor consistent impact on request success rates in the self-hosted Kubernetes configurations, and only minimal effect on AWS SageMaker, at least up to a concurrency level of 10.

| Concurrency | Jina API | SageMaker | Self-Hosted (Dynamic Batching) | Self-Hosted (No Batching) |
| --- | --- | --- | --- | --- |
| 1 | 93.3% | 100% | 57.5% | 58.3% |
| 5 | 85.7% | 100% | 58.3% | 58.3% |
| 10 | 83.8% | 99.6% | 55.3% | 58.3% |

### [*tag*](#success-rate-by-token-length "Success Rate By Token-Length")Success Rate By Token-Length

Long passages with high token counts impact both the Jina Embedding API and Kubernetes with dynamic batching similarly to large batches: as size increases, the failure rate rises substantially. However, while self-hosted solutions without dynamic batching almost invariably fail with large batches, they perform better with individual long passages. As for SageMaker, long passage lengths - like concurrency and batch size - had no notable impact on request success rates.

| Passage Length (tokens) | Jina API | SageMaker | Self-Hosted (Dynamic Batching) | Self-Hosted (No Batching) |
| --- | --- | --- | --- | --- |
| 128 | 100% | 99.8% | 98.7% | 58.3% |
| 512 | 100% | 99.8% | 66.7% | 58.3% |
| 1024 | 99.3% | 100% | 33.3% | 58.3% |
| 8192 | 51.1% | 100% | 29.4% | 58.3% |

## [*tag*](#request-latency "Request Latency")Request Latency

All latency tests were repeated five times at concurrency levels of 1, 5, and 10. Time-to-respond is the average over five attempts. Request throughput is the inverse of time-to-respond in seconds, times concurrency.

### [*tag*](#jina-api "Jina API")Jina API

Response times in the Jina API are primarily influenced by batch size, regardless of concurrency level. While passage length also affects performance, its impact isn't straightforward. As a general principle, requests containing more data - whether through larger batch sizes or longer passages - take longer to process.

#### Concurrency 1:

| Batch Size | Passage length (in tokens) | Time to Respond in ms | Request Throughput (requests/second) |
| --- | --- | --- | --- |
| 1 | 128 | 801 | 1.25 |
| 1 | 512 | 724 | 1.38 |
| 1 | 1024 | 614 | 1.63 |
| 32 | 128 | 1554 | 0.64 |
| 32 | 512 | 1620 | 0.62 |
| 32 | 1024 | 2283 | 0.44 |
| 128 | 128 | 4441 | 0.23 |
| 128 | 512 | 5430 | 0.18 |
| 128 | 1024 | 6332 | 0.16 |

#### Concurrency 5:

| Batch Size | Passage length (in tokens) | Time to Respond in ms | Request Throughput (requests/second) |
| --- | --- | --- | --- |
| 1 | 128 | 689 | 7.26 |
| 1 | 512 | 599 | 8.35 |
| 1 | 1024 | 876 | 5.71 |
| 32 | 128 | 1639 | 3.05 |
| 32 | 512 | 2511 | 1.99 |
| 32 | 1024 | 4728 | 1.06 |
| 128 | 128 | 2766 | 1.81 |
| 128 | 512 | 5911 | 0.85 |
| 128 | 1024 | 18621 | 0.27 |

#### Concurrency 10:

| Batch Size | Passage length (in tokens) | Time to Respond in ms | Request Throughput (requests/second) |
| --- | --- | --- | --- |
| 1 | 128 | 790 | 12.66 |
| 1 | 512 | 669 | 14.94 |
| 1 | 1024 | 649 | 15.41 |
| 32 | 128 | 1384 | 7.23 |
| 32 | 512 | 3409 | 2.93 |
| 32 | 1024 | 8484 | 1.18 |
| 128 | 128 | 3441 | 2.91 |
| 128 | 512 | 13070 | 0.77 |
| 128 | 1024 | 17886 | 0.56 |

For individual requests (batch size of 1):

* Response times remain relatively stable, ranging from about 600-800ms, regardless of passage length
* Higher concurrency (5 or 10 simultaneous requests) doesn't significantly degrade per-request performance

For larger batches (32 and 128 items):

* Response times increase substantially, with batch size of 128 taking roughly 4-6 times longer than single requests
* The impact of passage length becomes more pronounced with larger batches
* At high concurrency (10) and large batches (128), the combination leads to significantly longer response times, reaching nearly 18 seconds for the longest passages

For throughput:

* Smaller batches generally achieve better throughput when running concurrent requests
* At concurrency 10 with batch size 1, the system achieves its highest throughput of about 15 requests/second
* Larger batches consistently show lower throughput, dropping to less than 1 request/second in several scenarios

### [*tag*](#aws-sagemaker "AWS SageMaker")AWS SageMaker

AWS SageMaker tests were performed with a `ml.g5.xlarge` instance.

#### Concurrency 1:

| Batch Size | Passage length (in tokens) | Time to Respond in ms | Request Throughput (requests/second) |
| --- | --- | --- | --- |
| 1 | 128 | 189 | 5.28 |
| 1 | 512 | 219 | 4.56 |
| 1 | 1024 | 221 | 4.53 |
| 32 | 128 | 377 | 2.66 |
| 32 | 512 | 3931 | 0.33 |
| 32 | 1024 | 2215 | 0.45 |
| 128 | 128 | 1120 | 0.89 |
| 128 | 512 | 3408 | 0.29 |
| 128 | 1024 | 5765 | 0.17 |

#### Concurrency 5:

| Batch Size | Passage length (in tokens) | Time to Respond in ms | Request Throughput (requests/second) |
| --- | --- | --- | --- |
| 1 | 128 | 443 | 11.28 |
| 1 | 512 | 426 | 11.74 |
| 1 | 1024 | 487 | 10.27 |
| 32 | 128 | 1257 | 3.98 |
| 32 | 512 | 2245 | 2.23 |
| 32 | 1024 | 4159 | 1.20 |
| 128 | 128 | 2444 | 2.05 |
| 128 | 512 | 6967 | 0.72 |
| 128 | 1024 | 14438 | 0.35 |

#### Concurrency 10:

| Batch Size | Passage length (in tokens) | Time to Respond in ms | Request Throughput (requests/second) |
| --- | --- | --- | --- |
| 1 | 128 | 585 | 17.09 |
| 1 | 512 | 602 | 16.60 |
| 1 | 1024 | 687 | 14.56 |
| 32 | 128 | 1650 | 6.06 |
| 32 | 512 | 3555 | 2.81 |
| 32 | 1024 | 7070 | 1.41 |
| 128 | 128 | 3867 | 2.59 |
| 128 | 512 | 12421 | 0.81 |
| 128 | 1024 | 25989 | 0.38 |

Key differences vs Jina API:

* Base Performance: SageMaker is significantly faster for small requests (single items, short passages) - around 200ms vs 700-800ms for Jina.
* Scaling Behavior:
  + Both services slow down with larger batches and longer passages
  + SageMaker shows more dramatic slowdown with large batches (128) and long passages (1024 tokens)
  + At high concurrency (10) with maximum load (batch 128, 1024 tokens), SageMaker takes ~26s vs Jina's ~18s
* Concurrency Impact:
  + Both services benefit from increased concurrency for throughput
  + Both maintain similar throughput patterns across concurrency levels
  + SageMaker achieves slightly higher peak throughput (17 req/s vs 15 req/s) at concurrency 10

### [*tag*](#self-hosted-kubernetes-cluster "Self-Hosted Kubernetes Cluster")Self-Hosted Kubernetes Cluster

Self-hosting tests were performed on [Amazon’s Elastic Kubernetes Service](https://aws.amazon.com/eks/) with a `g5.xlarge` instance.

#### Concurrency 1:

| Batch Size | Passage length (tokens) | No Batching Time (ms) | No Batching Throughput (req/s) | Dynamic Time (ms) | Dynamic Throughput (req/s) |
| --- | --- | --- | --- | --- | --- |
| 1 | 128 | 416 | 2.40 | 2389 | 0.42 |
| 1 | 512 | 397 | 2.52 | 2387 | 0.42 |
| 1 | 1024 | 396 | 2.52 | 2390 | 0.42 |
| 32 | 128 | 1161 | 0.86 | 3059 | 0.33 |
| 32 | 512 | 1555 | 0.64 | 1496 | 0.67 |
| 128 | 128 | 2424 | 0.41 | 2270 | 0.44 |

#### Concurrency 5:

| Batch Size | Passage length (tokens) | No Batching Time (ms) | No Batching Throughput (req/s) | Dynamic Time (ms) | Dynamic Throughput (req/s) |
| --- | --- | --- | --- | --- | --- |
| 1 | 128 | 451 | 11.08 | 2401 | 2.08 |
| 1 | 512 | 453 | 11.04 | 2454 | 2.04 |
| 1 | 1024 | 478 | 10.45 | 2520 | 1.98 |
| 32 | 128 | 1447 | 3.46 | 1631 | 3.06 |
| 32 | 512 | 2867 | 1.74 | 2669 | 1.87 |
| 128 | 128 | 4154 | 1.20 | 4026 | 1.24 |

#### Concurrency 10:

| Batch Size | Passage length (tokens) | No Batching Time (ms) | No Batching Throughput (req/s) | Dynamic Time (ms) | Dynamic Throughput (req/s) |
| --- | --- | --- | --- | --- | --- |
| 1 | 128 | 674 | 14.84 | 2444 | 4.09 |
| 1 | 512 | 605 | 16.54 | 2498 | 4.00 |
| 1 | 1024 | 601 | 16.64 | 781\* | 12.80 |
| 32 | 128 | 2089 | 4.79 | 2200 | 4.55 |
| 32 | 512 | 5005 | 2.00 | 4450 | 2.24 |
| 128 | 128 | 7331 | 1.36 | 7127 | 1.40 |

† This anomalous result is a byproduct of the dynamic batching’s 2-second time-out. With a concurrency of 10, each sending 1024 tokens or data, the queue fills up almost immediately and the batching system never has to wait for a timeout. At lower sizes and concurrencies, it does, automatically adding two wasted seconds to each request. This kind of non-linearity is common in underoptimized batch processes.

When given requests with more than 16,384 tokens, our self-hosting setup failed with server errors, typically out-of-memory ones. This was true independently of concurrency levels. As a result, no tests with more data than that are displayed.

High concurrency increased response times broadly linearly: Concurrency levels of 5 took roughly five times as long to respond as 1. Levels of 10, ten times as long.

Dynamic batching slows down response times by about two seconds for small batches. This is expected because the batching queue waits 2 seconds before processing an underfull batch. For larger batch sizes, however, it brings moderate improvements in time to respond.

## [*tag*](#token-throughput "Token Throughput")Token Throughput

Token throughput increases with larger batch sizes, longer passage lengths, and higher concurrency levels across all platforms. Therefore, we'll only present results at high usage levels, as lower levels wouldn't provide a meaningful indication of real-world performance.

All tests were conducted at a concurrency level of 10, with 16,384 tokens per request, averaged over five requests. We tested two configurations: batch size 32 with 512-token passages, and batch size 128 with 128-token passages. The total number of tokens remains constant across both configurations.

Token throughput (tokens per second):

| Batch Size | Passage length (tokens) | Jina API | SageMaker | Self-Hosted (No Batching) | Self-Hosted (Dynamic Batching) |
| --- | --- | --- | --- | --- | --- |
| 32 | 512 | 46K | 28.5K | 14.3K | 16.1K |
| 128 | 128 | 42.3K | 27.6K | 9.7K | 10.4K |

Under high-load conditions, the Jina API significantly outperforms the alternatives, while the self-hosted solutions tested here show substantially lower performance.

## [*tag*](#costs-per-million-tokens "Costs Per Million Tokens")Costs Per Million Tokens

Cost is arguably the most critical factor when choosing an embedding solution. While calculating AI model costs can be complex, here's a comparative analysis of different options:

| Service Type | Cost per Million Tokens | Infrastructure Cost | License Cost | Total Hourly Cost |
| --- | --- | --- | --- | --- |
| Jina API | $0.045-0.05 | N/A | N/A | N/A |
| SageMaker (US East) | $0.0723 | $1.408/hour | $2.50/hour | $3.908/hour |
| SageMaker (EU) | $0.0788 | $1.761/hour | $2.50/hour | $4.261/hour |
| Self-Hosted (US East) | $0.352 | $1.006/hour | $2.282/hour | $3.288/hour |
| Self-Hosted (EU) | $0.379 | $1.258/hour | $2.282/hour | $3.540/hour |

### [*tag*](#jina-api-1 "Jina API")Jina API

The service follows a token-based pricing model with two prepaid tiers:

* 50for1billiontokens(50 for 1 billion tokens (50for1billiontokens(0.05 per million) - An entry-level rate ideal for prototyping and development
* 500for11billiontokens(500 for 11 billion tokens (500for11billiontokens(0.045 per million) - A more economical rate for larger volumes

It's worth noting that these tokens work across Jina's entire product suite, including readers, rerankers, and zero-shot classifiers.

### [*tag*](#aws-sagemaker-1 "AWS SageMaker")AWS SageMaker

SageMaker pricing combines hourly instance costs with model license fees. Using an `ml.g5.xlarge` instance:

* Instance cost: 1.408/hour(USEast)or1.408/hour (US East) or 1.408/hour(USEast)or1.761/hour (EU Frankfurt)
* [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) license: $2.50/hour
* Total hourly cost: 3.908−3.908-3.908−4.261 depending on region

With an average throughput of 15,044 tokens/second (54.16M tokens/hour), the cost per million tokens ranges from 0.0723to0.0723 to 0.0723to0.0788.

### [*tag*](#self-hosting-with-kubernetes "Self-Hosting with Kubernetes")Self-Hosting with Kubernetes

Self-hosting costs vary significantly based on your infrastructure choice. Using AWS EC2's `g5.xlarge` instance as a reference:

* Instance cost: 1.006/hour(USEast)or1.006/hour (US East) or 1.006/hour(USEast)or1.258/hour (EU Frankfurt)
* [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) license: 5000/quarter(5000/quarter (5000/quarter(2.282/hour)
* Total hourly cost: 3.288−3.288-3.288−3.540 depending on region

At 2,588 tokens/second (9.32M tokens/hour), the cost per million tokens comes to 0.352−0.352-0.352−0.379. While the hourly rate is lower than SageMaker, the reduced throughput results in higher per-token costs.

Important considerations for self-hosting:

* Fixed costs (licensing, infrastructure) continue regardless of usage
* On-premises hosting still requires license fees and staff costs
* Variable workloads can significantly impact cost efficiency

### [*tag*](#key-takeaways "Key Takeaways")Key Takeaways

The Jina API emerges as the most cost-effective solution, even without factoring in cold-start times and assuming optimal throughput for alternatives.

Self-hosting might make sense for organizations with existing robust infrastructure where marginal server costs are minimal. Additionally, exploring cloud providers beyond AWS could yield better pricing.

However, for most businesses, especially SMEs seeking turnkey solutions, the Jina API offers unmatched cost efficiency.

## [*tag*](#security-and-data-privacy-considerations "Security and Data Privacy Considerations")Security and Data Privacy Considerations

When choosing a deployment strategy for embedding models, security and data privacy requirements may play a decisive role alongside performance and cost considerations. We provide flexible deployment options to match different security needs:

### [*tag*](#cloud-service-providers "Cloud Service Providers")Cloud Service Providers

For **enterprises already working with major cloud providers**, our cloud marketplace offerings (like [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-kdi3xkt62lo32), [Azure](https://azuremarketplace.microsoft.com/en-us/marketplace/apps/jinaai.jina-embeddings-v3-vm?tab=Overview), and [GCP](https://console.cloud.google.com/marketplace/browse?hl=en&inv=1&invt=AboIuQ&q=jina)) provide a natural solution for deployment within pre-existing security frameworks. These deployments benefit from:

* Inherited security controls and compliance from your CSP relationship
* Ready integration with existing security policies and data governance rules
* Requires little or no change to existing data processing agreements
* Alignment with pre-existing data sovereignty considerations

### [*tag*](#self-hosting-and-local-deployment "Self-Hosting and Local Deployment")Self-Hosting and Local Deployment

**Organizations with stringent security requirements or specific regulatory obligations** often prefer complete physical control over their infrastructure. Our self-hosted option enables:

* Full control over the deployment environment
* Data processing entirely within your security perimeter
* Integration with existing security monitoring and controls

To obtain commercial licensing for our CC-BY-NC models, you first need to get a license from us. [Please feel free to contact our sales team.](https://jina.ai/api-dashboard/license-config)

### [*tag*](#jina-api-service "Jina API Service")Jina API Service

For **startups and SMEs** trying to balance security and convenience against costs, our API service provides enterprise-grade security without adding operational overhead:

* [SOC2 certification](https://jina.ai/Jina_AI_GmbH_Letter_of_Attestation_SOC_2_Type_1.pdf) ensuring robust security controls
* [Full GDPR compliance](https://gdpr-info.eu/) for data processing
* Zero data retention policy - we don't store or log your requests
* Encrypted data transmission and secure infrastructure

Jina AI’s model offerings enable organizations to choose the deployment strategy that best aligns with their security requirements while maintaining operational efficiency.

## [*tag*](#choosing-your-solution "Choosing Your Solution")Choosing Your Solution

The flowchart below summarizes the results of all the empirical tests and tables you’ve seen:

![Black and white flowchart featuring decision points on data handling, primary use cases, and technical specs against a dark b](https://cms.jina.ai/content/images/2025/01/image-3.png)

With that information in hand, the flowchart above should give you a good indication of what kinds of solutions to consider.

First, consider your security needs and how much flexibility you have to sacrifice to meet them.

Then, consider how you plan to use AI in your enterprise:

1. Offline indexing and non-time-sensitive use cases that can optimally use batch processing.
2. Reliability and scalability-sensitive uses like retrieval-augmented generation and LLM-integration.
3. Time-sensitive usages like online search and retrieval.

Also, consider your in-house expertise and existing infrastructure:

1. Is your tech stack already heavily cloud-dependent?
2. Do you have a large in-house IT operation able to self-host?

Lastly, consider your expected data volumes. Are you a large-scale user expecting to perform millions of operations using AI models every day?

## [*tag*](#conclusion "Conclusion")Conclusion

Integrating AI into operational decisions remains uncharted territory for many IT departments, as the market lacks established turnkey solutions. This uncertainty can make strategic planning challenging. Our quantitative analysis aims to provide concrete guidance on incorporating our search foundation models into your specific workflows and applications.

When it comes to cost per unit, Jina API stands out as one of the most economical options available to enterprises. Few alternatives can match our price point while delivering comparable functionality.

We're committed to delivering search capabilities that are not only powerful and user-friendly but also cost-effective for organizations of all sizes. Whether through major cloud providers or self-hosted deployments, our solutions accommodate even the most complex enterprise requirements that extend beyond pure cost considerations. This analysis breaks down the various cost factors to help inform your decision-making.

Given that each organization has its own unique requirements, we recognize that a single article can't address every scenario. If you have specific needs not covered here, please reach out to discuss how we can best support your implementation.