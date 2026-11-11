---
title: 'Vector Search Doctor (Part 2): Bridging the Gap Between Theory and Practice in Vector Search'
company: Sease
tag: 评测
date: 2026-07-17
url: https://sease.io/2026/07/vector-search-doctor-part-2-bridging-the-gap-between-theory-and-practice-in-vector-search.html
account: 
origin: harvest3-202607
---
In our [previous post](https://sease.io/2026/07/embedding-model-evaluation-oncustom-datasets.html), we introduced the **Embedding Model Evaluator**, the first component of **Vector Search Doctor**.

Its goal was to answer a fundamental question:

> ***How well does this embedding model work on my own dataset?***

To answer that, we evaluated the model using **exact vector search**, where every query is compared against every document in the collection. This provided us with a reliable baseline: the optimal retrieval quality that the selected embedding model can achieve on the given dataset.

However, exact nearest neighbor search is rarely feasible at a production scale. Real search systems usually rely on **approximate nearest neighbor** algorithms, such as HNSW, to make vector search fast enough for real-world usage.

The next question is simple:

> ***How much retrieval quality are we sacrificing for speed?***

This is where the second component of Vector Search Doctor comes into play: the **Approximate Search Evaluator.**

## From Exact Search To Production Search

Exact vector search is useful because it isolates the quality of the embedding model.

If the model performs poorly even with exact search, then the problem is probably the model itself, not the search engine or the ANN algorithm.

But production systems have different constraints:

* They must answer quickly
* They must scale to large collections
* They must use memory and CPU efficiently
* They often rely on approximate vector search

Approximate search algorithms trade a small amount of accuracy for significant performance improvements. This trade-off is often worth it, but it should be measured rather than assumed.

A search system that is extremely fast but consistently misses relevant documents is not useful. On the other hand, a system that preserves perfect quality but takes seconds to answer is usually not suitable for production.

The Approximate Search Evaluator is designed to measure this balance.

## What The Approximate Search Evaluator Does

The **Approximate Search Evaluator** evaluates the behavior of a real vector search implementation.

Instead of running brute-force comparisons in memory, it sends queries to a configured search engine, such as Solr or Elasticsearch, where document embeddings have already been indexed.

The retrieved results are then compared against the relevance judgments used in Part 1.

In practice, the evaluator answers questions such as:

* How close is my approximate search implementation to the exact-search baseline?
 * How much quality do I lose when using ANN search?
 * Are my vector search parameters well-tuned?
 * Is my search engine configuration suitable for this dataset?
 * Which configuration gives the best quality/performance trade-off?

## Evaluation Workflow

The workflow is straightforward:

1. The evaluator loads the queries, relevance judgments, and query embeddings.
 2. It submits each query to the configured search engine using a query template.
 3. The search engine performs approximate vector search using its internal ANN implementation.
 4. The retrieved results are compared against the expected relevant documents.
 5. Standard Information Retrieval metrics, such as nDCG, MAP, Precision, and Recall, are computed.
 6. The final report shows how well the approximate search behaves compared to the exact-search baseline.

The key point is that this evaluation happens against your actual search engine setup, not against an abstract benchmark.

## Input Requirements

To run an evaluation, you need:

* a search engine collection or index containing document embeddings;
 * queries to evaluate with the relative embeddings generated with the same embedding model used for the indexed document embeddings;
 * relevance judgments, used as ground truth;
 * a query template describing how to perform vector search against the search engine;
 * a configuration file describing the evaluation setup.

The document embeddings indexed in the search engine and the query embeddings used by the evaluator must come from the same embedding model. Otherwise, the vector similarity scores are not meaningful.

The input files can come from the workflow described in Part 1, or from your own dataset preparation pipeline, as long as they follow the expected format.

## A Practical Evaluation

Let’s see how the Approximate Search Evaluator can be configured.

Assume that we already have:

* a running search engine;
 * a collection containing documents enriched with vector embeddings;
 * the query embeddings generated during the exact-search evaluation;
 * a relevance judgment file describing which documents are relevant for each query.

The evaluator is configured through a YAML file.

Here is an example configuration:

```
				
					# Search engine type. Accepted values: solr, elasticsearch, opensearch, vespa
search_engine_type: "solr"

# Search engine endpoint.
search_engine_url: "http://localhost:8983/solr"

# Collection or index name.
collection_name: "testcore"

# Field containing the document identifier.
id_field: "id"

# Query template used to perform vector search.
query_template: "examples/templates/only_vector.json"

# Query embeddings generated by the Embedding Model Evaluator.
embeddings_file: "resources/embeddings/queries_embeddings.jsonl"

# Path to the evaluation dataset containing queries and relevance judgments.
evaluation_dataset_path: "resources/evaluation_dataset.json.gz"

# List of evaluation metrics to compute (default: ndcg@10, map@10, mrr@10, precision@10, recall@10)
metrics: ["ndcg@10", "map@10", "mrr@10"]

# Number of results to retrieve for each query.
top_k: 10

# Output folder for the evaluation report.
output_dest: "resources/approximate_search_evaluation"
				
			
```

The exact field names may vary depending on the implementation, but the idea remains the same: the configuration tells the evaluator where the search engine is, how to query it, where the query embeddings are, and where the ground truth is stored.

## Query Template

The query template defines how the evaluator should submit vector queries to the search engine.

For example, a Solr vector query template could look like this:

```
				
					{
  "q": "{!knn f=vector topK=10}$vector"
}
				
			
```

The evaluator replaces the `$vector` placeholder with the actual embedding of each query. This makes the evaluator flexible enough to work with different search engines and query formats, while keeping the evaluation logic independent from the specific search backend.

## Running The Evaluation

Once the configuration file is ready, the evaluator can be executed from the command line:

```
				
					uv run approximate_search_evaluator --config examples/configs/approximate_search_evaluator_config.yaml
				
			
```

As in Part 1, **`uv`** can manage the Python environment and install the required dependencies automatically.

Once the execution finishes, you will see an output like this:

```
				
					Evaluation completed.

Metrics:
  ndcg@10  0.319
  map@10   0.219
  mrr@10   0.424

Results written to:
  resources/evaluation_results.json
				
			
```

If the exact-search baseline from Part 1 reported an `nDCG@10` of `0.`34, then the approximate setup is preserved:

```
				
					0.319 / 0.340 = 93.82%
				
			
```

of the exact-search quality.

This means the approximate search configuration preserves most of the retrieval quality. The remaining limitation comes from the embedding model itself rather than from the ANN approximation.

## Understanding The Trade-Off: HNSW Parameters

Approximate nearest neighbor algorithms are configurable. In production, this configuration has a direct impact on quality, latency, indexing time, and memory usage.

Currently, one of the most popular and widely used ANN algorithms is **HNSW (Hierarchical Navigable Small World)**. HNSW works by organizing data into a multi-layered graph structure, where finding similar vectors is like navigating a network of connected nodes—starting from a “zoomed-out” layer and moving down to the finest details.

Because it relies on this graph structure, its performance heavily depends on how the graph is built and traversed. For HNSW, three of the most important parameters are:

* **ef\_construction**: controls how many candidates are considered while building the graph. Higher values usually improve graph quality but increase indexing time.
 * **ef\_search**: controls how many neighbors are explored at query time. Higher values usually improve recall but increase latency.
 * **M**: controls the maximum number of connections per node in the graph. Higher values can improve accuracy but increase memory usage and indexing cost.

These parameters should not be tuned blindly. The Approximate Search Evaluator makes their effect measurable.

For example, let’s suppose the exact-search evaluation in Part 1 produced:

```
				
					Exact search nDCG@10 = 0.850
				
			
```

Then we test three HNSW configurations:

| Configuration | nDCG@10 | Quality Retained |
| --- | --- | --- |
| ef\_search=50, M=16 | 0.760 | 89.4% |
| ef\_search=100, M=16 | 0.820 | 96.5% |
| ef\_search=200, M=16 | 0.835 | 98.2% |

The last configuration gives the best quality, but it may also be slower. Depending on the latency requirements, the second configuration might be the best production choice.

The important point is that the decision is now based on measurable evidence.

## Comparing Approximate Search Against The Exact Baseline

The most valuable part of this evaluation is the comparison with the exact-search baseline.

The Embedding Model Evaluator from Part 1 tells us:

> ***This is the best quality the embedding model can achieve on this dataset.***

The Approximate Search Evaluator tells us:

> ***This is how much of that quality the production search implementation preserves.***

If the approximate search achieves 95–98% of the exact-search quality with much lower latency, the configuration is probably a good candidate for production. If it achieves only 60–70%, then something needs further investigation. Without this comparison, it is hard to know whether poor search quality comes from the embedding model, the search engine, or the ANN configuration.

## Conclusion

The Approximate Search Evaluator completes the Vector Search Doctor evaluation pipeline, extending the analysis from embedding model evaluation to production search systems.

[**Part 1**](https://sease.io/2026/07/embedding-model-evaluation-oncustom-datasets.html) established the best retrieval quality an embedding model can achieve on a given dataset by using exact vector search as a ground truth. **Part 2** builds on that baseline by measuring how much of that quality is preserved once approximate nearest neighbor search is introduced in a real search engine.

The goal is not to identify the “best” ANN algorithm or configuration. **The goal is to make retrieval quality measurable throughout the entire vector search pipeline**.

Without this type of evaluation, poor retrieval quality can easily be attributed to the wrong component. Is the embedding model underperforming? Is the ANN configuration too aggressive? Is the search engine introducing unnecessary quality loss? Without reliable measurements, answering these questions often becomes guesswork.

Vector Search Doctor addresses this problem by separating these concerns. The Embedding Model Evaluator isolates the quality of the embedding model, while the Approximate Search Evaluator measures how much of that quality is preserved by the production search engine. Together, they provide a systematic framework for measuring retrieval quality across the entire vector search pipeline and identifying where quality is being lost.

Rather than optimizing vector search through trial and error, engineers can make decisions based on measurable evidence. Whether the next step is choosing a different embedding model, tuning HNSW parameters, or changing the search engine configuration, improvements can be guided by objective retrieval metrics instead of intuition.

In an era where search quality directly impacts user satisfaction and business outcomes, that isn’t just a nice capability to have, it’s **essential**.

## Need Help with this topic?​

If you're struggling with Approximate Search Evaluator, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with Approximate Search Evaluator, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)