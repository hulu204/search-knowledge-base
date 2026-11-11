---
title: 'Faster Vector Search: Early Termination Strategy Now in Apache Solr'
company: Sease
tag: 召回
date: 2025-12-02
url: https://sease.io/2025/12/faster-vector-search-early-termination-strategy-now-in-apache-solr.html
account: 
origin: harvest3-202607
---
Hi readers,

In this blog post, we are excited to share some important news with you:  
**Sease** has **contributed a new feature to Apache Solr** that makes **approximate k-NN search faster and more efficient***.*

We have introduced an **early termination strategy** that enhances performance by allowing searches to stop earlier under specific conditions. This improvement comes with the addition of the **PatienceKnnVectorQuery**, a new version of the k-NN vector query. Unlike the standard approach, it can **exit early when the HNSW queue remains saturated** over a saturation threshold.

***This feature will be available starting from Apache Solr 10.0.0***.

Here is how we will explore the topic:

* We discuss early termination strategies, with a focus on **Patience in Proximity**.
 * We briefly mention how this strategy has been implemented in **Apache Lucene**.
 * After that, we will describe the open-source contribution we made to **Apache Solr** and explain how to use this new feature.
 * Finally, just for completeness, we also take a look at the implementation in **Elasticsearch**.

## Early Termination Strategies

For all readers who have reached this blog post but may not be experts, I first suggest reading our blog post on [Apache Solr Neural Search](https://sease.io/2022/01/apache-solr-neural-search.html), which explains in simple terms what Hierarchical Navigable Small Worlds (HNSW) and Approximate Nearest Neighbour (ANN) search mean.  
Once you’ve done that, it will be easier to understand the concepts we are about to discuss.

Especially when dealing with large datasets, the HNSW algorithm can become inefficient because it often evaluates many nodes that do not actually improve the search results. This is especially the case when the data contains duplicate or highly similar vectors, or when dense clusters create links that add minimal new information.

As a result, HNSW could perform more distance calculations than necessary, wasting time and memory without improving accuracy. Early termination strategies help overcome this issue by stopping the search before all candidate nodes are evaluated — for example, once certain thresholds are reached. This reduces redundant computations, lowers query latency, and makes HNSW more efficient.

Recently, a variety of techniques have been explored to improve the efficiency of HNSW, ranging from optimisations in graph construction to enhancements applied at query time. In this [blog post](https://www.elastic.co/search-labs/blog/hnsw-knn-search-early-termination), for example, three different early termination techniques are discussed:

* **Fixed candidate pool size:** the search terminates once a predefined maximum number of nodes has been evaluated.
* **Distance threshold-based termination:** the search stops when a neighbour is found whose distance to the query vector meets a predefined distance threshold.
* **Dynamic early termination based on quality estimation:** the search stops if the quality of the results converges quickly.

The strategy we want to present can be defined as very close to the third category (dynamic early termination). It is called ***Patience in Proximity*** — a simple early termination approach for HNSW, presented at *ECIR ’25: Proceedings of the 47th European Conference on Information Retrieval* by Tommaso Teofili and Jimmy Lin ([Paper](https://cs.uwaterloo.ca/~jimmylin/publications/Teofili_Lin_ECIR2025.pdf)).

## Patience in Proximity

When searching for the nearest neighbours (k-NN) with an HNSW graph, the process works as follows:

* You start from a random entry point at the upper levels of the graph and move down layer by layer until you reach the bottom level.
* At each layer, you follow links toward nodes that are closer to the query, refining the position.
* In the final layer, which contains all the nodes, the search continues until no better neighbours can be found compared to the ones already identified.

This approach ensures maximum accuracy, but can be costly because many nodes are often visited even when the best results have already been found.

The proposed technique makes the process more efficient by introducing a **saturation threshold**: instead of going all the way until no better neighbour exists, the search can stop earlier. If, after several steps, the new candidates do not bring significant improvements, the exploration is stopped, reducing the computational cost without significantly affecting accuracy.

What has just been explained can be easily seen from the graphs shown below, taken from the original [paper](https://cs.uwaterloo.ca/~jimmylin/publications/Teofili_Lin_ECIR2025.pdf) – graph (a) “HNSW” and graph (b) “HNSW using Patience in Proximity”:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/10/Screenshot-2025-09-19-alle-11.32.47.png?fit=800%2C372&ssl=1)

***Green line (candidates\_size):*** It shows the number of candidates to visit. At the beginning, it grows rapidly since the new candidates to be evaluated are far more numerous than those actually promoted to the nearest neighbours. Then, around 300 visits, it starts to decline as the ‘good’ candidates to be turned into neighbours become fewer and fewer.

***Blu Line (phi):*** phi is a normalised stability measure showing how much the set of nearest neighbours changes as the search progresses. Low phi means the search is still improving, while high phi indicates a stable set. From the graph, after about 300 visits, the blue line flattens out — meaning that the list of nearest neighbours hardly changes anymore, i.e. newly visited nodes are rarely better than the current ones. This indicates that the search has reached a saturation point, and continuing to explore more nodes will not significantly improve the results.

***Red Line (patience):*** It is the patience threshold, that is, how many consecutive times we accept that neighbours remain nearly unchanged before deciding to stop.

***Orange Line (saturation counter):*** It is the saturation counter: it increases every time the saturation condition is met (i.e., when phi ≥ γ, for example, 95). When the orange line reaches the red line, it means that patience has run out → the search stops.

Graph (a) shows that HNSW tends to over-explore. Even after about 300 visits, when the results barely improve and the curve has flattened, the search continues up to around 800 visits, adding unnecessary computation.

In Graph (b), the search stops sooner once it becomes evident that new candidates no longer provide meaningful improvements. Here, the process ends after around 350 visits, skipping roughly 450 unnecessary ones and resulting in a much more efficient search.

## Apache Lucene Contribution

In April 2025, Lucene version 10.2.1 introduced the Patience in Proximity early termination strategy.

This PR [#14094](https://github.com/apache/lucene/pull/14094) adds:

* the **`HnswQueueSaturationCollector`**, a collector that extends the **`KnnCollector`** for HNSW and applies a saturation-based threshold to dynamically stop the graph exploration. The collector keeps track of how many neighbours are added for each candidate visited (HNSW node) and compares it with the previous step; once the rate of new neighbours stabilises for several consecutive iterations, exploration is stopped.
* the **`PatienceKnnVectorQuery`**, which leverages the collector to optimise HNSW searches by avoiding unnecessary exploration when results have stabilised. This is a version of knn vector query that exits early when the HNSW queue saturates over a **`saturationThreshold`** for more than **`patience`** times.

**`saturationThreshold`** parameter controls how “stable” the nearest-neighbour queue must be before the algorithm considers it saturated; `patience` specifies how many consecutive iterations the condition must persist before early termination occurs.  
The defaults defined in Lucene for these parameters are:

```
				
					private static final double DEFAULT_SATURATION_THRESHOLD = 0.995d;

private static int defaultPatience(AbstractKnnVectorQuery delegate) {
    return Math.max(7, (int) (delegate.k * 0.3));
  }
				
			
```

##### How were the default values chosen?

The paper refers to the experiments conducted but does not go into much technical detail. However, according to comments in [PR #14094](https://github.com/apache/lucene/pull/14094?utm_source=chatgpt.com#issuecomment-2681635026), internal benchmarks were run (on the Cohere-768 model with 200k documents), where different parameter combinations were evaluated to optimise the trade-off between recall and latency.

The baseline configuration (without early termination) achieved the highest recall, around 0.96, though with slightly higher latency. Several combinations of saturation threshold and patience were then tested, and after comparing all variants, the team decided to adopt the *candidate@default* configuration (shown above), as it maintains a recall performance comparable to the baseline with only minimal loss, while providing a measurable improvement in response time.

## Our Apache Solr Contribution

Since Solr was recently upgraded to Lucene 10.2.1 (PR: [#3053](https://github.com/apache/solr/pull/3053)), we have been able to expose this new functionality.

In PR [#3644](https://github.com/apache/solr/pull/3644), the possibility to use the **patienceKnnVectorQuery** has therefore been added in Apache Solr. This feature will be available starting from Apache Solr 10.0.0.

The **`KnnQParser`** has been modified to include support for this functionality, exposed through three additional query parameters:

* `earlyTermination` (boolean, default: `false`) – enables early termination during the search. Enabling early termination typically reduces query latency and resource usage, with a potential small trade-off in recall.
* `saturationThreshold` (double, default: `0.995`) – controls the saturation level for early termination.
* `patience` (int, default: `max(7, topK * 0.3)`) – the number of consecutive iterations the search will continue after the candidate queue is considered saturated. The default value is not a fixed value but a formula based on the topK parameter.

This allows users to decide whether or not to run the vector query with early termination.

*NOTE: saturationThreshold and patience must always be used together: either specify both to customise the behaviour, or omit both to rely on the default values.*

We recommend relying on the default value and changing these parameters only if you are confident about their impact. Using values that are too low can make the search stop too aggressively, leading to poor recall. Using values that are too high reduces the benefit of early termination, since the search runs nearly as long as without it.

In Apache Solr, there is also the **`TextToVectorQParser`**, which encodes textual queries into vectors using a specialised language model. Since it extends the **`KnnQParser`**, it directly inherits the modifications and parameters, enabling the same early termination feature without further changes.

Here are some examples of a KNN search using early termination:

```
				
					?q={!knn f=vector topK=10 earlyTermination=true}[1.0, 2.0, 3.0, 4.0]
				
			
```

→ KNN search with early termination enabled, relying on the default values for *saturationThreshold* and *patience*.

```
				
					?q={!knn f=vector topK=10 earlyTermination=true saturationThreshold=0.989 patience=10}[1.0, 2.0, 3.0, 4.0]
				
			
```

→ KNN search with early termination enabled, but with *saturationThreshold* and *patience* explicitly set at query time.

```
				
					?q={!knn f=vector topK=10 saturationThreshold=0.989 patience=10}[1.0, 2.0, 3.0, 4.0]
				
			
```

→ Early termination is automatically enabled when *both* **`saturation`** and **`patience`** are specified, even if **`earlyTermination=true`** is not explicitly set.

All the same concepts described above also apply to the **`TextToVectorQParser`**. For example:

```
				
					?q={!knn_text_to_vector model=a-model f=vector topK=10 earlyTermination=true}hello world query
				
			
```

## Elasticsearch Contribution

For completeness, it is worth noting that this functionality has also been added recently in Elasticsearch: PR [#127223](https://github.com/elastic/elasticsearch/pull/127223)

Unlike our implementation in Solr, however, the configuration of this option in Elasticsearch is defined at the **index level** (i.e., within the mappings). This means that users cannot enable or disable the option selectively for specific queries; instead, it applies to all queries executed against a given index.

Since configuring and optimising vector search is already quite complex, Elasticsearch has chosen to prioritise user experience, providing sensible defaults that work well for the vast majority of use cases.

Concretely, for a given vector field, if the **`type`** is one of **`hnsw`**, **`int8_hnsw`**, **`int4_hnsw`**, or **`bbq_hnsw`**, and **`early_termination`** is set to **`true`**, then the **`patienceKnnVectorQuery`** is executed, and early termination is enabled. For example:

```
				
					{
  "mappings": {
    "properties": {
      "my_vector" : {
        "type": "dense_vector",
        "dims" : 10,
        "index" : true,
        "index_options" : {
          "type" : "bbq_hnsw"
          "early_termination" : true
        }
      }
    }
  }
}
				
			
```

Anyway, the work is still a **work in progress**: there are open PRs, and it has not yet been released in any official version.

It’s worth staying tuned for the upcoming updates. Cheers!

## Need Help With This Topic?​​

If you’re struggling with Solr, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)