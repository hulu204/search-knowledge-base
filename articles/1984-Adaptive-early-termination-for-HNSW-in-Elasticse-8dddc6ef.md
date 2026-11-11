---
title: 'Adaptive early termination for HNSW in Elasticsearch'
company: Elastic
tag: 召回
date: 2026-03-02
url: https://www.elastic.co/search-labs/blog/hnsw-elasticsearch-adaptive-early-termination
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Adaptive early termination for HNSW in Elasticsearch

Introducing a new adaptive early termination strategy for HNSW in Elasticsearch.

March 02, 2026

[Tommaso Teofili](/search-labs/author/tommaso-teofili)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Elasticsearch uses the [Hierarchical Navigable Small World](https://www.elastic.co/search-labs/blog/hnsw-graph) (HNSW) algorithm to perform vector search over a proximity graph. HNSW is known to provide a nice trade-off between the quality of k-nearest neighbor (KNN) results and the associated cost.

In HNSW, search proceeds by iteratively expanding candidate nodes in the graph, maintaining a bounded set of nearest neighbors discovered so far. Each expansion has a cost (vector operations, random seeks to disk, and more), and the marginal benefit of that cost tends to decrease as the search progresses.

One way to optimize HNSW graph traversal is to stop searching when the marginal likelihood of finding new true neighbors doesn’t increase. For this reason, in [Elasticsearch 9.2](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules#index-dense-vector-hnsw-early-termination) we introduced a new [early termination mechanism](https://www.elastic.co/search-labs/blog/hnsw-knn-search-early-termination). This stops the search process when visiting graph nodes doesn’t provide enough new nearest neighbors, consecutively, for a fixed number of times.

This article guides you through how we improved over the mentioned early termination mechanism in HNSW to make it better suited for different datasets and data distributions.

## **Early termination in HNSW**

In HNSW, search proceeds by iteratively expanding candidate nodes in the proximity graph, maintaining a bounded set of nearest neighbors discovered so far, until it either has visited the whole graph or meets some early stop criteria.

Early termination is therefore not necessarily always an optimization, it’s **part of the search algorithm itself**. The moment we decide to stop determines the balance between efficiency and recall. In Elasticsearch, there are already a number of ways a query on HNSW can early terminate:

* A fixed maximum number of nodes is visited.
* A fixed timeout is reached.

While simple and predictable, these rules are largely **agnostic to what the search is actually doing**. Also they’re used mostly to make sure that the query finishes in reasonable time for the end user.

In a [previous blogpost](https://www.elastic.co/search-labs/blog/hnsw-knn-search-early-termination), we introduced the concept of redundancy in HNSW. In short, redundant computations occur when HNSW continues to evaluate new candidate nodes that don’t result in finding more nearest neighbors.

## **Patience: Measuring progress instead of effort**

The notion of *patience* reframes early termination around **progress rather than effort**.

Instead of asking:

“How many steps have we taken?”

The new question becomes:

“What is the amount of computation we accept to waste, until we lose hope?”

During HNSW search, early exploration typically produces peak improvements to the top-k candidate set. During first steps of the HNSW graph exploration, the set of neighbors is continuously updated as the algorithm keeps discovering nearer and nearer neighbors to the query vector. Over time, these improvements become rarer as the search converges. [Patience-based termination](https://cs.uwaterloo.ca/~jimmylin/publications/Teofili_Lin_ECIR2025.pdf) monitors this pattern and terminates the search once improvements have ceased for a sustained period.

In practice, while visiting the HNSW graph we also compute the queue saturation ratio as we hop through candidate nodes. This measures the percentage of nearest neighbors that were left unchanged while visiting the most recent graph node (or the inverse of the number of new neighbors introduced during the last iteration). When such a ratio becomes too big for too many consecutive iterations, we stop visiting the graph.

Conceptually, patience treats HNSW search as a **diminishing returns process**. When returns flatten out, continuing to explore the graph yields little benefit.

This framing is powerful because it ties termination directly to *observable outcomes* rather than to arbitrary fixed limits.

The benefit of using this smart early termination technique is that HNSW graph explorations tend to visit a smaller number of graph nodes while retaining an almost perfect relative recall.

To visualize this, we can plot the amount of recall per visited node that we got with the patience based early termination (labeled as `et=static`), when compared to the default HNSW behavior (labeled as `et=no`) on a couple of datasets, FinancialQA and Quora, and models, JinaV3 and E5-small.

![Adaptive Early Termination for HNSW ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfd0d692b9beb476a/6a170ef4dc55debf0be00e97/a9d07c5153ea64a2426c82487c36846030692bb9-1600x945.png)![Adaptive Early Termination for HNSW es](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt93509c251a1b641e/6a170ef6dc55dea2b3e00e9b/dac56125c4b16d1b596c9876b6ca9ac7b2dc87fa-1600x944.png)

## **Static thresholds and HNSW dynamics**

In practice, in Elasticsearch this is implemented using **static thresholds**. One threshold refers to the **saturation threshold**: that is, the ratio of saturation that we consider suboptimal. The other threshold refers to the number of consecutive graph nodes that we allow to be visited while still having a suboptimal queue saturation: that is, the **patience threshold**.

When we introduced this early termination strategy in Elasticsearch 9.2, we decided to opt for conservative defaults, so as to let the recall as much as possible, while still gaining in terms of latency and memory consumption. For this reason, we set the saturation threshold to be 100% and the patience threshold to be set as a (bounded) 30% of the [`num_candidates`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query#knn-query-top-level-parameters:~:text=search%20request%20size.-,num_candidates,-(Optional%2C%20integer)%20The) in the KNN query.

In many scenarios, these settings resulted to work nicely; however, two queries requesting the same number of neighbors might have radically different convergence behaviors. Some queries encounter dense local neighborhoods and saturate quickly; others must traverse long, sparse paths before finding competitive candidates. The latter resulted to be the most difficult to handle effectively.

As a result, we sometimes noticed:

* Over-exploration for easy queries.
* Premature termination for hard queries.

Therefore, we figured that fixed threshold values encode global assumptions about convergence, whereas we could make HNSW better adapt to different dynamics.

## **Making HNSW early termination adaptive**

Adaptive early termination approaches this problem from a different angle. Instead of enforcing predefined stopping thresholds, the algorithm **infers when to stop from the search dynamics themselves**.

So instead of comparing the queue saturation ratio between two consecutive candidates, we decided to introduce both an instant smoothed discovery rate dq,id\_{q,i} dq,i​ (how many new neighbors were introduced for a query *q*, in the last visit *i*) together with rolling mean μq,i\mu\_{q,i}μq,i​ and standard deviation σq,i\sigma\_{q,i}σq,i​ of such a discovery rate during the graph visit (using [Welford’s algorithm](https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm)). These statistics about the discovery rate are calculated per query, so that this information can be used to decide different degrees of patience for each query.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdbfb1e123f1b026d/6a170ef7cf4f25d9bab2d216/1958be7ca4425ade66eaf621ada3533173183598-694x118.png)

The previously static thresholds become adaptive to the discovery rate statistics: The saturation threshold becomes the rolling mean plus the standard deviation; whereas we make the patience adapt and scale inversely with the standard deviation.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7d4d91f464a9dc9d/6a170ef8d7c0223420de656a/f7ee4a55c24853b657df26052b275e8bd76cf0f9-654x156.png)

The early exit rules remain the same; the saturation happens when the instant discovery rate is lower than the adaptive saturation threshold. The graph visit stops if the saturation persists for a number of consecutive candidate visits that’s larger than the adaptive patience.

This way, we obtain a behavior that doesn’t depend on the `num_candidates` parameter in the KNN query (which might be always set or left as the default, regardless of early exit) and that better adapts to each query and vector distribution dynamically.

The recall per visited node on FinancialQA and Quora with the adaptive strategy (labeled as `et=adaptive`) reports a higher recall per visited node, when compared to the static strategy (`et=static`) and the default HNSW behavior (`et=no`).

![ adaptive strategy and the default HNSW behavior](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blteab7ba53ae14da0e/6a170ef9961e69e072c4cfd5/2a906997d9a25d74c7038bd9661bc97581e7258e-1600x938.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6fb9e672d3698200/6a170efb67045b7b2b45c2ab/3a114911e232c351dbb814cea20e8b0f1415a717-1600x925.png)

Adaptive early termination is turned on by default in Elasticsearch 9.3 for HNSW dense vector fields (and it can eventually be turned off via the [same index level setting](https://www.elastic.co/docs/reference/elasticsearch/index-settings/index-modules#index-dense-vector-hnsw-early-termination)).

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