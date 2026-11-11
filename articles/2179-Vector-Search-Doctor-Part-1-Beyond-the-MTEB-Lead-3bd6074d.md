---
title: 'Vector Search Doctor (Part 1): Beyond the MTEB Leaderboard for Custom Datasets'
company: Sease
tag: 评测
date: 2026-07-16
url: https://sease.io/2026/07/embedding-model-evaluation-oncustom-datasets.html
account: 
origin: harvest3-202607
---
MTEB is an excellent benchmark, but it cannot answer one simple question: ***how well will this embedding model work on my own data?*** This post introduces **Vector Search Doctor**, a tool designed to evaluate embedding models on real-world datasets.

Vector Search Doctor consists of two main components:

* **Part 1: Embedding Model Evaluator**: Assessing the quality of the embedding model itself. This process uses an exact vector search to establish a “ground truth” for retrieval performance on a custom dataset.
* **Part 2: Approximate Search Evaluator**: Assessing the performance (speed vs. accuracy) of approximate nearest neighbor (ANN) algorithms by comparing their results to the ground truth.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/10/vector_search_doctor-1.png?fit=800%2C402&ssl=1)

In this first post, we will focus on Part 1: evaluating embedding model performance.

## The Limit of the MTEB Leaderboard

There is a widely used benchmarking framework called [MTEB](https://github.com/embeddings-benchmark/mteb) (Massive Text Embedding Benchmark) that evaluates embedding models across multiple datasets, tasks, and languages. It also provides a public [leaderboard](https://huggingface.co/spaces/mteb/leaderboard), making it easy to compare models across different domains and datasets.

The MTEB leaderboard is extremely useful for comparing models on public benchmark datasets, but it does not answer how a model will behave on your own private or domain-specific data. To address this gap, the Embedding Model Evaluator reuses the MTEB evaluation logic while allowing users to provide their own corpus, queries, and relevance judgments.

## Why Evaluate Exact Vector Search?

You might be wondering: *“**Why bother evaluating the exact vector search? Isn’t the whole point to be fast with an approximate vector search in production?**“.*

Exact search compares every query against every document in the dataset (brute force). This evaluation provides two key benefits:

1. **Embedding Model Quality Isolation**: If retrieval scores (e.g., nDCG@10) are low even with an exact vector search, the problem is not the search algorithm, but the embedding model itself, which is not a good fit for your custom dataset.
2. **Setting a Performance Ceiling**: This is the best retrieval performance you can expect from that model on your dataset.

## How does the evaluation work?

The Embedding Model Evaluator extends the MTEB library by overriding its dataset loading logic. Instead of evaluating one of the datasets bundled with MTEB, two custom tasks — CustomRetrievalTask and CustomRerankingTask — load the corpus, queries, and relevance judgments directly from user-provided JSONL files. The MTEB-supported model is then used to generate embeddings and run the benchmark.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/10/embedding_model_eval.png?fit=2673%2C1299&ssl=1)

## A Practical Evaluation

**Step 1**. Running an evaluation requires three JSONL files:

* **`corpus.jsonl`** – custom dataset: it contains all the documents from the search engine
  + `{"doc_id": "doc_1", "title": "AI regulation in Europe", "content": "The European Union approved..."}`
* `queries.jsonl` – list of queries to analyze.
  + `{"query_id": "q_1", "text": "European AI regulation"}`
* `candidates.jsonl` – file contains the relevance judgments used to compute the ideal ranking for each query
  + `{"query_id": "q_1", "doc_id": "doc_1", "rating": 2}`

If you want to quickly test the tool, you can generate an MTEB-compatible dataset with the [Dataset Generator](https://sease.io/2026/07/search-quality-evaluation-with-llms-the-dataset-generator.html) ([GitHub link](https://github.com/SeaseLtd/llm-search-quality-evaluation/tree/main/src/llm_search_quality_evaluation/dataset_generator)). It can generate queries (if needed), assign relevance ratings, and export everything in the required MTEB format.

**Step 2**. The evaluation parameters are defined in a simple YAML configuration file. Here is an [example](https://github.com/SeaseLtd/llm-search-quality-evaluation/blob/b090bd2fe3b3bfa1e4d33dde8885fa224526ac1d/examples/configs/vector_search_doctor/embedding_model_evaluator/embedding_model_evaluator_config.yaml):

```
				
					# Model ID (HuggingFace models).
model_id: "sentence-transformers/all-MiniLM-L12-v2"

# Accepted values: 'retrieval', 'reranking'
task_to_evaluate: "retrieval"

# Corpus jsonl file path with records - &lt;doc_id,title,content,...&gt;.
corpus_path: "resources/corpus.jsonl"

# Queries jsonl file path with records - &lt;query_id,text&gt;.
queries_path: "resources/queries.jsonl"

# Candidates jsonl file path with records - &lt;query_id,doc_id,rating&gt;.
candidates_path: "resources/candidates.jsonl"

# Relevance scale used in candidates dataset for rating field:
# Accepted values:
#   - binary: 0 (not relevant), 1 (relevant)
#   - graded: 0 (not relevant), 1 (maybe ok), 2 (that’s my result)
relevance_scale: "graded"

# (Optional) Path to write mteb resources,
# if not given it will be written to resources dir in the root folder
output_dest: "resources"

# (Optional) Path to write mteb document and query embeddings,
# if not given it will be written to resources/embeddings dir
embeddings_dest: "resources/embeddings"
				
			
```

**Step 3**. Run the Embedding Model Evaluator using the YAML configuration file.

```
				
					uv run embedding_model_evaluator --config examples/embedding_model_evaluator_config.yaml
				
			
```

**A quick note:** The time it takes to run the evaluation depends on the size of the embedding model and dataset. If they are large, it might take a while.

**Step 4**. After the evaluation, in the output folder (resources in this example), you’ll find the file containing all the computed metrics. The `resources/embeddings` folder also contains find two files with the embeddings generated by the model for both documents and queries.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/10/image-1.png?fit=2348%2C1194&ssl=1)

## Benchmark Results

Several experiments were run on the Retrieval task. The MTEB Leaderboard reports, for each model, the average nDCG@10 across multiple datasets. The same metric was used to evaluate the [sentence-transformers/all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2) model on a dataset of approximately 100,000 news documents.

The benchmark was then executed using two types of queries:

* keyword-based queries similar to the keyword queries typically submitted to traditional search engines (e.g. “artificial intelligence”, “covid-19”, “bitcoin crypto”, “tech layoffs”, …)
 * Natural language queries, which better match the semantic capabilities of embedding models (e.g. “How many evacuees in Canada wildfires?”, “UK nuclear deterrent expansion plans”, “Missing hiker found in Dolomites after New Year’s Day”**)**

The difference was significant. When using only **keyword-based queries**, the model’s nDCG@10 was ~40%, which was comparable to the MTEB Leaderboard’s general-purpose average of ~43%.

However, using **natural language queries** increased the model’s performance to ~80% nDCG@10. This highlights our key finding: this model is clearly optimised for understanding semantic, natural language meaning, not for simple keyword matching.

## Looking Forward

Now that a reliable ground truth has been established using exact search, the next question is **how much retrieval quality is preserved when approximate algorithms are used in a production search engine**. In Part 2 we’ll see how much retrieval quality is lost when replacing exact search with approximate nearest-neighbor algorithms.

Stay tuned!

## Need Help with this topic?​

If you're struggling with evaluating exact vector search, don't worry - we're here to help!
Our team offers expert services and training to help you optimise your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with evaluating exact vector search, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimise your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)