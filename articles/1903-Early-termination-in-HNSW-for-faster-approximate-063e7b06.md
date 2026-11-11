---
title: 'Early termination in HNSW for faster approximate KNN search'
company: Elastic
tag: 召回
date: 2025-01-07
url: https://www.elastic.co/search-labs/blog/hnsw-knn-search-early-termination
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Early termination in HNSW for faster approximate KNN search

Learn how HNSW can be made faster for KNN search, using smart early termination strategies.

January 07, 2025

[Tommaso Teofili](/search-labs/author/tommaso-teofili)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

The challenge of **finding nearest neighbors** efficiently in high-dimensional spaces, particularly as datasets grow in size, is one of the most important ones in the context of vector search. As discussed in our previous [blog post](https://www.elastic.co/search-labs/blog/knn-exact-vs-approximate-search), brute force nearest neighbor search might be the best choice, when dataset size is limited. On the other hand, as vector dataset size increases, switching to approximate nearest neighbor search can be useful to retain query speed without sacrificing accuracy.

Elasticsearch implements approximate nearest neighbor search via the [Hierarchical Navigable Small World algorithm](https://arxiv.org/abs/1603.09320). **HNSW** offers an efficient way to navigate the vector space, reducing the computational cost while still maintaining high search accuracy. In particular its hierarchical layered structure makes it possible to visit candidate neighbors and decide whether to include them in the final result set with fewer vector distance computations.

However, despite its strengths, the HNSW algorithm can be further optimized for large-scale vector searches. One effective way to enhance HNSW's performance is by finding ways to stop visiting the graph under specific circumstances, called *early termination*. This blog post explores early termination concepts for HNSW and how they can optimize query execution.

## HNSW redundancy

HNSW is an approximate nearest neighbor algorithm that builds a layered graph where nodes represent vectors and edges represent the proximity between vectors in the vector space. Each layer contains incrementally a larger number of graph nodes. When querying, the search traverses this graph, starting at a random entry point and navigating towards the closest neighbors through the layers.

The search process is iterative and expands as it examines more nodes and vectors. This balance between speed and accuracy is central to HNSW, but it can still result in redundant computations, especially when large datasets are involved.

In HNSW, redundant computations primarily occur when the algorithm continues to evaluate new nodes or candidates that provide little to no improvement in finding actual neighbors to a query. This happens because, in standard HNSW traversal, the algorithm proceeds layer-by-layer, exploring and expanding candidate nodes until all possible paths are exhausted.

In particular, this kind of redundancy can arise when the dataset includes highly similar or duplicate vectors, clusters with dense intra-cluster connections, or vectors in very high-dimensional spaces with little intrinsic structure. Such redundancy leads to visiting unnecessary edges, increasing memory usage and potentially slowing search performance without improving accuracy. In high-dimensional spaces where similarity scores decay quickly, some edges often fail to contribute meaningful shortcuts in the graph, resulting in inefficient navigation paths too.

So, in case a number of unnecessary computations can be performed while traversing the graph, one could try to improve the HNSW algorithm to mitigate this issue.

## Early Termination FTW

Navigating the solution space is a fundamental concept in optimization and search algorithms, where the goal is to find an optimal solution among a set of possible solutions. The solution space represents all potential solutions to a given problem, and navigating it involves systematically exploring these possibilities. This process can be visualized as moving through a graph where each node represents a different solution, and the objective is to identify the node that best meets the criteria of the problem. Understanding how to effectively navigate the solution space is crucial for solving complex problems that have huge numbers of solutions. Early termination is a generic optimization strategy that can be applied to any such algorithm to make smart decisions about when stopping searching for solutions under certain circumstances.

If any solution is considered 'good enough' to meet a desired criteria, the search can stop and the solution can be considered either a good candidate or an optimal solution. This means some potentially better solutions might remain unexplored, so it's tricky to find a perfect compromise between efficiency and quality of the final solution(s).

![hnsw early termination](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt010532ee2cf04151/6a17dd7ddbb4ff6385fb55a9/9976a0f43fd162827db5b3ce4cd5da2c504f3f3e-664x1109.png)

## Early Termination in HNSW

In the context of HNSW, early termination can be used to stop the search process before all potential candidates nodes (vectors) have been fully evaluated. *Evaluating* a candidate node means calculating the actual similarity between the query vector and the vector corresponding to the node in the graph that is being processed; for this reason, when skipping a bunch of such operations while traversing each layer, the computational cost of the query can be greatly reduced.

On the other hand, skipping a candidate that would otherwise result in a *true* nearest neighbor will surely affect the quality of the search results, potentially missing a few candidate vectors that *are* close to the query vector.

Consequently the trade-off between the efficiency gains and loss in accuracy is to be handled with care. Early termination is useful in case of:

* Sublinear Efficiency: You want to optimize performance in exchange for slightly lower recall.
* High-Throughput Systems: Faster response times are more valuable than the highest accuracy.
* Resource Constraints: Compute or memory limitations make full traversal of the HNSW graph undesirable.

In the context of HNSW there are a number of options for implementing an early termination strategy.

1. Fixed candidate pool size: One of the simplest early termination strategies is to limit the size of the candidate pool (e.g., the number of nodes evaluated during the search). In HNSW, the search process is iterative, expanding to more nodes as it progresses. By setting a limit on the number of candidates considered, we can terminate the search early and return results based on only a subset of the total graph. Of course this can be implemented either in a layer-wise fashion or accounting for all the nodes across the whole graph.
2. Distance threshold-based termination: Another potentially effective early termination strategy is to make smart decisions based on distance computations between the query vector and the vectors corresponding to HNSW nodes. One could set a *threshold* based on the distance between the query vector and the current closest vector. If a vector is found whose distance is below a specified threshold, the search can be stopped early, assuming that further exploration is unlikely to yield significantly better results. This goes hand in hand with constraints on the fact that nodes get visited in a smart order, to avoid missing possibly relevant neighbors.
3. Dynamic early termination based on quality estimation: A more sophisticated approach is dynamically adjusting the termination criteria based on the "quality" of the results found during each search query. If the search process is converging quickly on high-quality neighbors (e.g., neighbors with very close distances), the algorithm can terminate early, even without hitting a predefined threshold.

The first two strategies fall in the category of "fixed configuration" early termination strategies, so that the search terminates based on fixed constraints that do not take into account query-specific challenges. In fact not all queries are equally hard, some queries require more candidate visit than others, for example, when the distribution of the vectors is skewed. Consequently some query vectors might fall into denser regions of the vector space, so that they have more candidate nearest neighbors, while some others might fall into "less populated regions", making it harder to find their true nearest neighbors.

Because of such situations, early termination strategies that can adapt to the density of the vector space (and consequently to the connectivity of the HNSW graph) seem more attractive for real-life scenarios. Therefore determining the optimal point at which to stop searching for each query is more likely to lead to substantial latency reductions without compromising accuracy. Such kinds of early termination strategies are dubbed *adaptive* as they adapt to each query instance to decide when to terminate the search process.

For example, an adaptive early termination strategy can utilize machine learning models to predict how much search effort is sufficient for a given query to achieve the desired accuracy. One such a model dynamically adjusts how much of the graph to explore based on the individual query's characteristics and intermediate search results.

Speaking about intermediate search results, they are often powerful predictors of how much further to search. If the initial results are already close to the query, the nearest neighbors are likely to be found soon, allowing for early termination. Conversely, poor initial results indicate a need for more extensive exploration, (see this [paper](https://dl.acm.org/doi/pdf/10.1145/3318464.3380600)).

Lucene makes it possible to implement early termination in HNSW by means of the `KnnCollector` interface that exposes an `earlyTerminated()` [method](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/search/KnnCollector.java#L37), but it also offers a couple of *fixed configuration* early termination strategies for HNSW:

1. [TimeLimitingKnnCollector](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/search/TimeLimitingKnnCollectorManager.java#L48-L102) makes it possible to stop the HNSW graph traversing when a certain time threshold is met.
2. [AbstractKnnCollector](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/search/AbstractKnnCollector.java#L36-L38) is a base `KnnCollector` implementation that stops the graph traversal once a fixed number of graph nodes are visited.

As an additional example, to implement a distance threshold-based termination, we could rely on the minimum competitive similarity recorded by Lucene during HNSW traversal (used to make sure only competitive nodes are explored) and early exit when it falls below a given threshold.

```
public class MCSEarlyExitCollector implements KnnCollector {

  private final KnnCollector delegate;
  private final double mcsThreshold;

  public MCSEarlyExitCollector(KnnCollector delegate, double mcsThreshold) {
    this.delegate = delegate;
    this.mcsThreshold = mcsThreshold;
  }

  @Override
  public boolean earlyTerminated() {
    return delegate.earlyTerminated() || minCompetitiveSimilarity() < mcsThreshold;
  }

  ...
}
```

## Conclusion

Early termination strategies for approximate KNN can lead to notable speedups while retaining good accuracy, if correctly implemented. Fixed strategies are easier to implement but they might require more tuning and also not work well across different queries. Dynamic / adaptive strategies, on the other hand, are harder to implement but have the advantage of being able to better adapt to different search queries.

### Frequently Asked Questions

#### What is HNSW?

HNSW is an approximate nearest neighbor algorithm that builds a layered graph where nodes represent vectors and edges represent the proximity between vectors in the vector space.

#### How can the HNSW algorithm be optimized?

One effective way to enhance HNSW's performance is by finding ways to stop visiting the graph under specific circumstances, called early termination.

#### What is early termination in HNSW?

In the context of HNSW, early termination can be used to stop the search process before all potential candidates nodes (vectors) have been fully evaluated.

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