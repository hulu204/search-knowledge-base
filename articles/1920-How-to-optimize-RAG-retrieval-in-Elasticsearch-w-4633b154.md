---
title: 'How to optimize RAG retrieval in Elasticsearch with DeepEval'
company: Elastic
tag: 评测
date: 2025-03-17
url: https://www.elastic.co/search-labs/blog/rag-retrieval-elasticsearch-deepeval
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How to optimize RAG retrieval in Elasticsearch with DeepEval

Learn about RAG retrieval and how to optimize the Elasticsearch retriever in a RAG pipeline using DeepEval.

March 17, 2025

[Kritin Vongthongsri](/search-labs/author/kritin-vongthongsri)

[AI](/search-labs/blog/category/ai)

Jump to

Share

LLMs are prone to hallucinations, lack domain-specific expertise, and are limited by their context windows. Retrieval-Augmented Generation (RAG) addresses these issues by enabling LLMs to access relevant external context, thereby grounding their responses.

Several RAG methods—such as GraphRAG and AdaptiveRAG—have emerged to improve retrieval accuracy. However, RAG retrieval performance can still vary depending on the domain and specific use case of a RAG application.

To optimize retrieval for a given use case, you'll need to identify the hyperparameters that yield the best quality. This includes the choice of embedding model, the number of top results (top-K), the similarity function, reranking strategies, and more.

Optimizing retrieval means evaluating and iterating on these hyperparameters until you find the best performing combination. In this blog, we'll explore how to optimize the Elasticsearch retriever in a RAG pipeline using DeepEval.

We’ll begin by installing Elasticsearch and DeepEval:

```
pip install deepeval elasticsearch
```

## Measuring RAG retrieval performance

To optimize your Elasticsearch retriever and benchmark each hyperparameter combination, you’ll need a method for assessing retrieval quality. Here are 3 key metrics that allow you to measure retrieval performance: **contextual precision, contextual recall, and contextual relevancy.**

**Contextual precision:**

```
from deepeval.metrics import ContextualPrecisionMetric
contextual_precision = ContextualPrecisionMetric()
```

The contextual precision metric checks if the most relevant information chunks are ranked higher than the less relevant ones, for a given input. Simply put, it ensures that the most useful information is first in the set of retrieved contexts.

**Contextual recall:**

```
from deepeval.metrics import ContextualRecallMetric
contextual_precision = ContextualRecallMetric()
```

The contextual recall metric measures how well the retrieved information chunks aligns with the expected output, or ideal LLM response. A higher contextual recall score indicates that the retrieval system is more effective at capturing every piece of relevant information available in your knowledge base.

**Contextual relevancy:**

```
from deepeval.metrics import ContextualRelevancyMetric
contextual_relevancy = ContextualRelevancyMetric()
```

Finally, the contextual relevancy metric assesses how relevant the information in the retrieval context is to the user input of your RAG application.

…

A combination of these 3 metrics is essential to ensure that the retriever fetches the right amount of information in the proper sequence, and that your LLM receives clean, well-organized data for generating accurate outputs.

Ideally, you’ll want to find the combination of hyperparameters that yields the highest scores across all three metrics. However, in some cases, increasing the recall score may inevitably decrease relevance. Striking the right balance between these factors is key to achieving optimal performance.

If you need custom metrics for a specific use case, [G-Eval](https://www.deepeval.com/docs/metrics-llm-evals) and [DAG](https://www.deepeval.com/docs/metrics-dag) might be worth exploring. These tools allow you to define precise metrics with tailored evaluation criteria.

Here are some resources that might help you better understand how these metrics are calculated:

* [How is contextual precision calculated](https://www.deepeval.com/docs/metrics-contextual-precision)
* [How is contextual recall calculated](https://www.deepeval.com/docs/metrics-contextual-recall)
* [How is contextual relevancy calculated](https://www.deepeval.com/docs/metrics-contextual-relevancy)
* [Evaluating Retrieval in RAG applications](https://www.deepeval.com/docs/metrics-contextual-relevancy)

## Elasticsearch hyperparameters to optimize RAG retrieval performance

Elasticsearch provides extensive flexibility in retrieving information for RAG pipelines, offering a wide range of hyperparameters that can be fine-tuned to optimize retrieval performance. In this section, we’ll discuss some of these hyperparameters.

**Before retrieval:**

To structure your data optimally before inserting it into your Elasticsearch vector database, you can fine-tune parameters such as chunk size and chunk overlap. Additionally, selecting the right embedding model ensures efficient and meaningful vector representations.

**During retrieval:**

Elasticsearch gives you full control over the retrieval process. You can configure the similarity function, first determining the number of candidates for the approximate search before applying KNN on the top-K candidates. Then, you select the most relevant top-K results.

Moreover, you can define your retrieval strategy—whether it's semantic (leveraging vector embeddings), text-based (using query rules), or a hybrid approach that combines both methods.

**After retrieval:**

Once results are retrieved, Elasticsearch allows you to refine them further through reranking. You can select a reranking model, define a reranking window, set a minimum score threshold, and more—ensuring that only the most relevant results are prioritized.

…

Different hyperparameters influence certain metric scores more than others. For example, if you're seeing issues with contextual relevance, it’s likely due to a specific set of hyperparameters, including top-K. By mapping specific hyperparameters to each metric, you can iterate more efficiently and fine-tune your retrieval pipeline with greater precision.

Below is a table outlining which retrieval metrics are impacted by different hyperparameters:

| Metric | Hyperparameter |
| --- | --- |
| Contextual Precision | Reranking model, reranking window, reranking threshold |
| Contextual Recall | Retrieval strategy (text vs embedding), embedding model, candidate count, similarity function, top-K |
| Contextual Relevancy | top-K, chunk size, chunk overlap |

In the next section, we'll walk through how to evaluate and optimize our Elasticsearch retriever with code examples. We'll use the `"all-MiniLM-L6-v2"` to embed our text documents, set `top-K` to 3, and configure the number of candidates to 10.

## Setting up RAG with Elasticsearch Retriever

To get started, connect to your local or cloud-based Elastic cluster:

```
from elasticsearch import Elasticsearch

# Create the client instance
client = Elasticsearch(
    # For local development
    # hosts=["http://localhost:9200"]
    cloud_id=ELASTIC_CLOUD_ID,
    api_key=ELASTIC_API_KEY,
)
```

Next, create an Elasticsearch index with the appropriate type mappings to store text and embeddings as dense vectors.

```
if not client.indices.exists(index="knowledge_base"):
    client.indices.create(
        index="knowledge_base",
        mappings={
            "properties": {
                "text": {
                    "type": "text"
                },
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": "true",
                    "similarity": "cosine"
                }
            }
        }
    )
```

To insert your document chunks into the Elastic index, first encode into vectors using an embedding model. For this example, we’re using "`all-MiniLM-L6-v2`".

```
# Example document chunks
document_chunks = [
    "Elasticsearch is a distributed search engine.",
    "RAG improves AI-generated responses with retrieved context.",
    "Vector search enables high-precision semantic retrieval.",
    "Elasticsearch uses dense vector and sparse vector similarity for semantic search.",
    "Scalable architecture allows Elasticsearch to handle massive volumes of data.",
    "Document chunking can help improve retrieval performance.",
    "Elasticsearch supports a wide range of search features."
    # Add more document chunks as needed...
]
operations = []
for i, chunk in enumerate(document_chunks):
    operations.append({"index": {"_index": "knowledge_base", "_id": i}})
    # Convert the document chunk to an embedding vector
    operations.append({
        "text": chunk,
        "embedding": model.encode(chunk).tolist()
    })

client.bulk(index="knowledge_base", operations=operations, refresh=True)
```

Finally, define a retriever function to search from your elastic client for your RAG pipeline.

```
def search(input, top_k=3):
    # Encode the query using the model
    input_embedding = model.encode(input).tolist()

    # Search the Elasticsearch index using kNN on the "embedding" field
    res = client.search(index="knowledge_base", body={
        "knn": {
            "field": "embedding",
            "query_vector": input_embedding,
            "k": top_k,  # Retrieve the top k matches
            "num_candidates": 10  # Controls search speed vs accuracy
        }
    })

    # Return a list of texts from the hits if available, otherwise an empty list
    return [hit["_source"]["text"] for hit in res["hits"]["hits"]] if res["hits"]["hits"] else []
```

## Evaluating your RAG retriever

With your Elasticsearch retriever set up, you can begin evaluating it as part of your RAG pipeline. The evaluation consists of 2 steps:

1. Preparing an input query along with the expected LLM response, and using the input to generate a response from your RAG pipeline to create an LLMTestCase containing the input, actual output, expected output, and retrieval context.
2. Evaluating the test case using a selection of retrieval metrics.

### Preparing a test case

Here, we prepare an input asking "How does Elasticsearch work?" with the corresponding expected output: "Elasticsearch uses dense vector and sparse vector similarity for semantic search."

```
input = "How does Elasticsearch work?"
expected_output= "Elasticsearch uses dense vector and sparse vector similarity for semantic search."
retrieval_context = search(input)

prompt = """
Answer the user question based on the supporting context

User Question:
{input}

Supporting Context:
{retrieval_context}
"""
actual_output = generate(prompt) # hypothetical function, replace with your own LLM
print(actual_output)
```

Let's examine the actual\_output generated by our RAG pipeline:

```
“Elasticsearch indexes document chunks using an inverted index for fast full-text search and retrieval.”
```

Finally, consolidate all test case parameters into a single LLM test case.

```
from deepeval.test_case import LLMTestCase

test_case = LLMTestCase(
    input=”"How does Elasticsearch work?",
    actual_output=actual_output,
    retrieval_context=retrieval_context,
    expected_output=,
)
```

### Running evaluations

To run evaluations on your elastic retriever, pass the test case and metrics we’ve defined earlier into the evaluate function.

```
evaluate(
   [test_case],
   metrics=[contextual_recall, contextual_precision, contextual_relevancy]
)
```

## Optimizing the retriever

Once you’ve evaluated your test case, we can begin to analyze the results. Below are example evaluation results from the test case we created, as well as additional hypothetical queries a user might ask your RAG system.

| Query | Contextual precision | Contextual recall | Contextual relevancy |
| --- | --- | --- | --- |
| "How does Elasticsearch work?" | 0.63 | 0.93 | 0.52 |
| "Explain Elasticsearch's indexing method." | 0.57 | 0.87 | 0.49 |
| "What makes Elasticsearch efficient for search?" | 0.65 | 0.90 | 0.55 |

* **Contextual precision** is suboptimal → Some retrieved contexts might be too generic or off-topic.
* **Contextual recall** is strong → Elasticsearch is retrieving enough relevant documents.
* **Contextual relevancy** is inconsistent → The quality of retrieved documents varies across queries.

### Improving RAG retrieval quality

As previously mentioned, each metric is influenced by specific retrieval hyperparameters. Given that contextual precision is suboptimal and contextual relevancy is inconsistent, it's clear that reranker hyperparameters, along with top-K, chunk size, and chunk overlap, need improvement.

Here’s an example of how you might iterate on top-K using a simple for loop.

```
# Example of running multiple test cases with different retrieval settings
for top_k in ["1", "3", "5", "7"]:
    retrieval_context = search(query, top_k)
    test_case = LLMTestCase(
        input=query,
        actual_output=generate(query, retrieval_context),
        retrieval_context=retrieval_context,
        expected_output="Elasticsearch is an optimized vector database for AI applications.",
    )

    evaluate([test_case], metrics=[contextual_recall, contextual_precision, contextual_relevancy])
```

This for loop helps identify the top-K value that produces the best metric scores. You should apply this approach to all hyperparameters that impact relevancy and precision scores in your retrieval system. This will allow you to determine the optimal combination!

### Tracking improvements

DeepEval is open-source and great if you’re looking to evaluate your retrievers locally.

However, if you're looking for a way to conduct deeper analyses and store your evaluation results, [Confident AI](https://www.confident-ai.com/) brings your evaluations to the cloud and enables extensive experimentation with powerful analysis tools.

Confident allows you to:

* **Curate** and manage your evaluation dataset effortlessly.
* **Run evaluations locally** using DeepEval metrics while pulling datasets from Confident AI.
* **View and share** testing reports to compare prompts, models, and refine your LLM application.

![RAG retrieval with Confident AI](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd00d5e62114ce7dd/6a17e24fabe0f22caadfe94b/00a9971a85c59a159c7a9b29912a9063023f8829-1600x702.png)

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter