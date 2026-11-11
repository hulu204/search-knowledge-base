---
title: 'OpenSearch and Large Language Models'
company: Sease
tag: 工程相关
date: 2025-11-24
url: https://sease.io/2025/11/opensearch-and-large-language-models.html
account: 
origin: harvest3-202607
---
Hi readers,

Are you trying to understand which search features based on large language models (LLM) are supported by OpenSearch? You are in the right place.

In this blog post, we provide a comprehensive overview of the features available in the OpenSearch ecosystem as of now, with a particular focus on how they enable AI-powered search experiences.

The goal is to provide you with a clear understanding of the current state of the art in OpenSearch and how you can leverage these capabilities in your applications.

## LLM-Based Features

If you are working with the latest version of OpenSearch (3.2), you already have a range of capabilities designed to support LLM-based use cases.   
Below is a summary of the most notable features currently available in this major version (3.x):

**3.0**

* **Text/Multi-Modal Vectorisation**
* **Vector Search (including Quantization and other optimisation)**
  + **Nested Vector Search**
  + **Radial Vector Search**
* **Hybrid Search**
* **Learned Sparse Retrieval**
* **Cross-Encoders for Reranking**
* **Semantic Highlighting**
* **Retrieval Augmented Generation (RAG)**
  + **Conversational Search with** **RAG**

**3.1**

* **Introduction of the semantic field type**
* **[Optimisation] Memory-optimized search** **(for Faiss – HNSW)**

**3.2**

* **[Optimisation] GPU indexing supports Faiss 16-bit scalar quantization**
* **[Optimisation] Boost recall for on-disk vector search**
* **[Experimental Feature] Introduction of Agentic search**

We will now explore each of these features individually, highlighting their purpose and how they enhance semantic search capabilities.

### Text/Multi-Modal Vectorisation

*[Since version: 2.4]*

Text and multi-modal vectorisation refers to the process of converting unstructured data, such as text, images, audio and videos, into numerical vectors that capture the underlying semantic meaning of the input data and can be used for tasks like semantic retrieval and similarity search.

OpenSearch supports both text and multimodal vectorisation by integrating with locally or remotely hosted LLMs that have been fine-tuned for generating vector embeddings.

In our previous blog post about [OpenSearch Knn plugin tutorial](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html), you can find a guide on how to implement text vectorisation in OpenSearch, starting from registering a model group, then registering a pre-trained model to that group, and finally deploying the model. Once deployed, the model can be used both to vectorise textual fields in your documents at indexing time and to vectorise textual queries at search time.

### Vector Search

*[Since version: 2.4]*

Over the past few years, we have already published several tutorials related to vector search in OpenSearch; therefore, it would not make sense to repeat topics we have already covered. You can refer to these blog posts for more details:

* [OpenSearch Neural Search Plugin Tutorial](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html)
* [OpenSearch KNN Plugin Tutorial](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html)
* [OpenSearch Neural Search Tutorial: How Filtering Works](https://sease.io/2024/03/opensearch-neural-search-tutorial-how-filtering-works.html)

Since we will refer to them later, it is important to note that OpenSearch supports the following vector search engines: Lucene, Faiss, and NMSLIB, and offers two main methods—HNSW and IVF—which are algorithms for approximate nearest neighbours.

That said, it is worth noting that vector search can be computationally expensive, especially when working with large datasets. For this reason, OpenSearch offers several **techniques to optimise vector storage**, which can help reduce memory usage and improve query performance:

* [Vector Quantization](https://docs.opensearch.org/latest/vector-search/optimizing-storage/knn-vector-quantization/)
* [Building vector indexes remotely using GPUs](https://docs.opensearch.org/latest/vector-search/remote-index-build/)
* [Disk-based vector search](https://docs.opensearch.org/latest/vector-search/optimizing-storage/disk-based-vector-search/)
* [Memory-optimized search](https://docs.opensearch.org/latest/vector-search/optimizing-storage/memory-optimized-search/)

##### [Optimisation] Vector Quantization

*[Since version: 2.13]*

Vector quantization is a **compression technique** used to represent high-dimensional vectors (like embeddings) with fewer bits, reducing both disk usage and memory footprint while trying to preserve as much information as possible.

There are three main families of quantization approaches: [scalar](https://www.elastic.co/search-labs/blog/scalar-quantization-101), [binary](https://qdrant.tech/articles/binary-quantization/), and [product](https://inria.hal.science/inria-00514462v2/document).   
Leveraging its internal libraries, OpenSearch supports all of them, in particular:

* [Apache Lucene scalar quantization](https://docs.opensearch.org/latest/vector-search/optimizing-storage/lucene-scalar-quantization/) (from version 2.16) – converts 32-bit floating-point input vectors into 7-bit integer vectors in each segment using the minimum and maximum quantiles computed based on the [`confidence_interval`](https://docs.opensearch.org/latest/vector-search/optimizing-storage/lucene-scalar-quantization/#confidence-interval) parameter.
 * [Faiss 16-bit scalar quantization](https://docs.opensearch.org/latest/vector-search/optimizing-storage/faiss-16-bit-quantization/) (from version 2.13) – converts 32-bit floating-point input vectors into 16-bit floating-point vectors.
 * [Faiss product quantization](https://docs.opensearch.org/latest/vector-search/optimizing-storage/faiss-product-quantization/) – represents a vector using a configurable number of bits.
 * [Faiss binary quantization](https://docs.opensearch.org/latest/vector-search/optimizing-storage/binary-quantization/) (from version 2.17) – compresses vectors into a binary format (0s and 1s).

You should consider using quantization when dealing with memory limitations or aiming to reduce search latency. However, because it inevitably leads to some loss of information, it’s essential to run benchmarks to assess the trade-offs and dete

##### [Optimisation] Building vector indexes remotely using GPUs

*[Since version: 3.0]*

In OpenSearch 3.0, a technological and architectural optimisation was introduced by enabling the use of a [remote GPU-accelerated service](https://docs.opensearch.org/latest/vector-search/remote-index-build/) for index building. This significantly reduces indexing time and, consequently, costs. Initially, support was limited to the Faiss engine with the HNSW method and the default 32-bit floating-point (FP32) vectors.

Starting with OpenSearch 3.2, support was extended to include 16-bit floating-point (FP16), byte, and binary vectors.

##### [Optimisation] Disk-based vector search

*[Since version: 2.17]*

By default, OpenSearch uses in-memory vector search, which provides the lowest latency by loading the entire vector index into memory. However, in some scenarios, you may want to strike a balance between speed and cost. In such cases, [disk-based vector search](https://docs.opensearch.org/latest/vector-search/optimizing-storage/disk-based-vector-search/) (introduced in release 2.17) offers a more cost-effective approach by reducing memory requirements through the use of binary quantization.

To enable it, simply set the **`mode`** parameter to `on_disk` when creating the index for your vector field type:

```
				
					PUT /knn_index_name
{
  "settings" : {
    ...
  },
  "mappings": {
    "properties": {
      "my_vector_field": {
        ...
        "mode": "on_disk"
      }
    }
  }
}
				
			
```

From OpenSearch 3.2, search quality in binary-quantised indexes can be improved thanks to the [introduction of two techniques](https://docs.opensearch.org/latest/vector-search/optimizing-storage/binary-quantization/#enhancing-search-quality-with-adc-and-rr), which should both be enabled to achieve the greatest benefit:

* **Asymmetric distance computation (ADC)**: keeps the query vector in full precision while comparing it against compressed document vectors (supported for 1-bit quantization only).
 * **Random rotation (RR)**: rotates the vector space so that variance (information) is more evenly distributed across dimensions. This reduces information loss during heavy compression (supported for 1-bit, 2-bit, and 4-bit quantization).

##### [Optimisation] Memory-optimized search

*[Since version: 3.1]*

In the latest release (3.1), OpenSearch introduced a [memory-optimised search](https://docs.opensearch.org/latest/vector-search/optimizing-storage/memory-optimized-search/) feature, only for the Faiss engine using the HNSW method. This enhancement allows Faiss to operate more efficiently by avoiding the need to load the entire vector index into off-heap memory, which can become problematic when the index size exceeds the available physical memory.

To enable this feature, set **`index.knn.memory_optimized_search`** to **`true`** in the index settings when creating the index:

```
				
					PUT /knn_index_name
{
  "settings": {
    "index.knn": true,
    "index.knn.memory_optimized_search": true
  },
  "mappings": {
     etc...
				
			
```

With this optimisation, the index is memory-mapped, allowing the operating system’s file cache to serve repeated reads, reducing I/O and improving performance. This feature applies only to search operations, while indexing behaviour remains unchanged.

### Nested Vector Search

*[Since version: 2.12]*

When working with large documents, a common challenge is to quickly and accurately identify only the portion of text that is truly relevant to the user’s search. To address this issue, it is a well-established practice to split documents into smaller sections, known as *chunks*. Each chunk represents an independent fragment of text and is transformed into a vector (embedding) that captures its semantic meaning.

OpenSearch supports storing multiple vectors for a single document using nested fields, enabling [nested vector search](https://docs.opensearch.org/latest/vector-search/specialized-operations/nested-search-knn) through the HNSW algorithm in both the Lucene and Faiss engines.   
The steps to perform a nested vector search are similar to those of a standard vector search, but you must explicitly define a nested mapping for indexing and use a nested query for searching.

###### Example Mapping

```
				
					PUT /knn_index_name
{
  "settings": {
    "index": {
      "knn": true
    }
  },
  "mappings": {
    "properties": {
      "nested_field": {
        "type": "nested",
        "properties": {
          "my_vector": {
            "type": "knn_vector",
            ...
              }
            }
          },
          "color": {
            "type": "text",
            ...
          }
        }
      }
    }
  }
}
				
			
```

In this case, we have defined a nested field called **`nested_field`**, which can contain multiple vector fields; in this example, only one has been defined, named `my_vector`, of type **`knn_vector`**.

###### Example Indexing

Once the index has been created, we can push some documents to it. In the following example, two docs have been indexed, each containing a **`nested_field`** array with multiple nested objects, i.e. three vectors per document.

```
				
					PUT _bulk?refresh=true
{"index": {"_index": "knn_index_name", "_id": "1"} } 
{"nested_field":[
    {"my_vector":[1,1,1], "color": "blue"}, 
    {"my_vector":[2,2,2], "color": "yellow"}, 
    {"my_vector":[3,3,3], "color": "white"} ]}
{"index": { "_index": "knn_index_name", "_id": "2"} } 
{"nested_field":[
    {"my_vector":[10,10,10], "color": "red"}, 
    {"my_vector":[20,20,20], "color": "green"}, 
    {"my_vector":[30,30,30], "color": "black"} ]}
				
			
```

###### Example Searching

Once the documents have been indexed, we are ready to perform the search. Here, a k-NN query has been executed on the nested field:

```
				
					GET knn_index_name/_search
{
  "query": {
    "nested": {
      "path": "nested_field",
      "query": {
        "knn": {
          "nested_field.my_vector": {
            "vector": [1,1,1],
            "k": 2
          }
        }
      }
    }
  }
}
				
			
```

Behind the scenes, OpenSearch uses the Lucene [DiversifyingChildrenFloatKnnVectorQuery](https://lucene.apache.org/core/10_2_0/join/org/apache/lucene/search/join/DiversifyingChildrenFloatKnnVectorQuery.html) (or its byte implementation, depending on your vector element data type) and an equivalent implementation in Faiss. [Vector search with filtering on nested fields](https://docs.opensearch.org/latest/vector-search/specialized-operations/nested-search-knn#vector-search-with-filtering-on-nested-fields) is also supported.

When you query a nested field in OpenSearch, the default response only tells you which parent document matched, without showing which specific nested object triggered the match.  
Using `inner_hits` lets you return the exact nested objects that matched. By default, only the highest-scoring nested object is returned. If you set `expand_nested_docs: true`, all matching nested objects are included, and `score_mode` controls how the parent document’s score is calculated (e.g., `max` for the highest score).

### Radial Vector Search

*[Since version: 2.14]*

[Radial Search](https://docs.opensearch.org/latest/vector-search/specialized-operations/radial-search-knn/) is a vector search technique where, instead of retrieving the k nearest vectors (as in the classic k-NN, k-nearest neighbours), it retrieves all vectors located within a certain radius from a query point in the vector space.

OpenSearch introduced this feature starting from version 2.14, and it can be performed using either the Lucene or Faiss engine. From an index and vector field configuration perspective, nothing changes — the difference lies at query time, where you can “play” with two parameters:

* **max\_distance**: The maximum allowed distance from the query vector; returns only vectors within this range.
* **min\_score**: The minimum similarity score required; returns only vectors meeting or exceeding this threshold.

As stated in this [OpenSearch blog post](https://opensearch.org/blog/vector-radial-search/), radial search provides more flexible search results and is particularly useful when you need to include only items that meet specific criteria, or when the acceptable similarity or distance range is subject to change.

### Hybrid Search

*[Since version: 2.11]*

Hybrid search blends lexical and semantic approaches, leveraging the advantages of both textual and vector-based techniques to enhance relevance and overall search quality.

It was introduced in OpenSearch 2.11, and we have already covered it in detail in this tutorial: [OpenSearch Neural Search Tutorial: Hybrid Search](https://sease.io/2024/04/opensearch-neural-search-tutorial-hybrid-search.html)

Following that version, various enhancements have been made, including:

* **2.13**  
  – Introduction of the possibility to perform [post-filtering on hybrid search results](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/post-filtering/).  
  – Support for [combining a hybrid query clause with any aggregation](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/aggregations/) that OpenSearch supports.

* **2.16**  
  – Introduction of the [sort](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/sorting/) parameter in the hybrid search request.  
  – The [search\_after](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/search-after/) parameter was introduced and used with `sort`, helps efficiently load the next pages of search results, especially in large datasets.

* **2.19**  
  – Introduction of the [Score Ranker Processor](https://docs.opensearch.org/latest/search-plugins/search-pipelines/score-ranker-processor/): a rank-based processor that uses the reciprocal rank fusion (RRF) algorithm to combine and rerank documents from multiple query types to produce the final ranked list of search results.  
  – Introduction of [Pagination](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/pagination/), by using the `pagination_depth` parameter in the hybrid query clause, along with the standard `from` and `size` parameters. For more details on how pagination works in-depth, check out the [OpenSearch blog](https://opensearch.org/blog/navigating-pagination-in-hybrid-queries-with-the-pagination_depth-parameter/).  
  – Introduction of the [explain](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/explain/) parameter, to understand how scores are calculated, normalised, and combined in hybrid queries.

* **3.0**  
  – The use of [inner\_hits](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/inner-hits/) has been extended to hybrid searches, allowing us to see which nested or child parts of a document matched the query, without affecting the final document ranking.
* **3.1**  
  – Introduction of the [collapse](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/collapse/) parameter in hybrid queries.

### Learned Sparse Retrieval

*[Since version: 2.11]*

The [learned sparse retrieval](https://docs.opensearch.org/latest/vector-search/ai-search/neural-sparse-search/) option, introduced in the OpenSearch 2.11 release, offers an alternative approach to neural text search. It is a neural search technique in which models are trained to generate *sparse text representations*—vectors composed mostly of zero values. This approach offers significant storage and computational advantages while capturing semantic relationships.  
OpenSearch supports learned sparse retrieval by integrating with models trained to generate sparse representations (such as SPLADE).

We have already covered this feature in a previous blog post, so if you are interested in a deeper dive, we recommend checking that out first: [OpenSearch Neural Sparse Search Tutorial](https://sease.io/2024/07/opensearch-neural-sparse-search-tutorial.html).

Let’s take a look at what has been introduced after version 2.11 and was not covered in our previous blog post. First of all, neural sparse search supports two distinct modes at query time:

* **Doc-only mode (default)**: the sparse encoding model is used only at index time to generate embeddings while at query time, the text is just tokenized (using a DL model analyzer or a custom tokenizer) and matched against the precomputed token weights. This is faster, but may slightly reduce relevance.
* **Bi-encoder mode**: the same sparse encoding model is used to generate embeddings at both index and query time. This generally gives better relevance, but at the cost of higher latency.

Version 2.13 introduced the [NeuralSparseSearchTool](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/neural-sparse-tool/), which automatically performs sparse vector retrieval. Later, in version 2.15, the [neural sparse query two-phase processor](https://docs.opensearch.org/latest/search-plugins/search-pipelines/neural-sparse-query-two-phase-processor/) was added, enhancing how neural sparse queries are handled. This processor accelerates the process by dividing it into two steps:

* First phase: Only the high-weight tokens (the most relevant to the query) are used to score documents, quickly finding a smaller set of top candidate documents.
* Second phase: The low-weight tokens are then used to rescore only this smaller set of candidates, improving the ranking.

If you are curious to explore some benchmark results, check out this [OpenSearch blog post](https://opensearch.org/blog/A-deep-dive-into-faster-semantic-sparse-retrieval-in-OS-2.12/).

### Cross-Encoders for Reranking

*[Since version: 2.12]*

Cross-encoders are large language models fine-tuned to jointly process a query and a document in a single input sequence, producing a relevance or similarity score. The higher the score, the stronger the semantic match between the two. Since they are much more computationally expensive than bi-encoders, they are typically used for reranking a small subset of retrieved results.

OpenSearch introduced the [rerank processor](https://docs.opensearch.org/latest/search-plugins/search-pipelines/rerank-processor) in version 2.12, designed to intercept and reorder search results at query time. It supports two re-ranking types:

* `ml_opensearch` – The processor evaluates search results using a cross-encoder ML model and reorders them based on the new scores returned by the model. For cross-encoder models, there are a couple of supported options listed [here](https://docs.opensearch.org/latest/ml-commons-plugin/pretrained-models/#cross-encoder-models), or you can use your own custom model. The supported formats are TorchScript and ONNX.
* `by_field` (from versione 2.18) – The processor reranks search results based on the value of a specific document field. This is useful if documents already contain a **numeric score** (for example, a relevance score from a previous ML model run or another search processor) and you want to sort them using that value.

### Semantic Highlighting

*[Since version: 3.0]*

Semantic highlighting is an LLM-powered feature that enhances the search experience by highlighting snippets from retrieved documents that are semantically related to the user’s information needs, rather than simply matching exact keywords.

OpenSearch introduced this feature in the 3.0 release, and my colleague Nazerke has already covered it in a dedicated blog post: [OpenSearch Semantic Sentence Highlighting Explained](https://sease.io/2025/09/opensearch-semantic-sentence-highlighting-explained.html).

If you are using a version earlier than 3.0, you can find a custom workaround to implement it in this blog post: [Search Limitations and Workarounds in OpenSearch](https://sease.io/2025/07/limitations-and-workarounds-in-opensearch.html).

### Retrieval Augmented Generation (RAG)

*[Since version: 2.13]*

Retrieval Augmented Generation (RAG) is based on three key steps: it first retrieves the most relevant information from the available source data (**retrieval**), then integrates this information into the prompt provided to the LLM (**augmentation**), and finally combines it with the user’s query to generate a response (**generation**). This process enables the model to deliver answers that are more up-to-date, accurate, and closely aligned with the specific context.

Version 2.13 introduced the [RAGTool](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/rag-tool/), a component designed to perform retrieval-augmented generation, i.e. leverages neural search or neural sparse search to retrieve documents and integrates a large language model to summarise the answers.

Also, with OpenSearch, you can implement RAG using a self-managed setup and the DeepSeek chat model, specifically:

* This [blueprint](https://github.com/opensearch-project/ml-commons/blob/main/docs/remote_inference_blueprints/deepseek_connector_chat_blueprint.md) demonstrates how to create a connector for the [DeepSeek chat model](https://api-docs.deepseek.com/api/create-chat-completion).
* Here you can find the steps required to configure RAG.

### Conversational Search with RAG

*[Since version: 2.10]*

Building on [RAG, the Conversation History](https://docs.opensearch.org/latest/vector-search/ai-search/conversational-search) adds the ability to search as if you were having a natural dialogue. Instead of treating each question in isolation, the system interprets it together with the context of what has already been asked. This means you can refine your search step by step by asking follow-up questions, and the system will retrieve the most relevant information from the documents, combining it with the dialogue history and the model’s knowledge.

*This feature was first introduced in version 2.10 and has been refined over time. The steps described below refer to the latest version*.

A prerequisite for activating this functionality is to enable both the conversation memory and the RAG pipeline features in the cluster setting:

```
				
					PUT /_cluster/settings
{
  "persistent": {
    "plugins.ml_commons.memory_feature_enabled": true,
    "plugins.ml_commons.rag_pipeline_feature_enabled": true
  }
}
				
			
```

Then, there are three initial steps:  
1) Creating a model connector for the specified general-purpose LLM (for example, [openAI](https://docs.opensearch.org/latest/tutorials/gen-ai/rag/conversational-search-openai/) or [Cohere Command](https://docs.opensearch.org/latest/tutorials/gen-ai/rag/conversational-search-cohere/))  
2) Registering and deploying the LLM.  
3) Configuring a search pipeline to handle conversational queries.

These steps can be configured [manually](https://docs.opensearch.org/latest/vector-search/ai-search/conversational-search#manual-setup) for greater flexibility and control, or you can use the [automated workflow](https://docs.opensearch.org/latest/vector-search/ai-search/conversational-search#automated-workflow).

Since the way a model is defined and deployed is similar to what we described in our previous blog post, we will focus on setting up the search pipeline here:

```
				
					PUT /_search/pipeline/rag_pipeline
{
  "response_processors": [
    {
      "retrieval_augmented_generation": {
        "model_id": "gnDIbI0BfUsSoeNT_jAw",
        "context_field_list": ["text"],
        "system_prompt": "You are a helpful assistant",
        "user_instructions": "Generate a concise and informative answer in less than 100 words for the given question"
      }
    }
  ]
}
				
			
```

The above command creates a pipeline that leverages the [RAG processor](https://docs.opensearch.org/latest/search-plugins/search-pipelines/rag-processor/) with the following parameters:

* **model\_id** (required): the ID of the model deployed.
* **context\_field\_list** (required): an array where you specify the search result fields to provide context for the RAG prompt.
* **system\_prompt**: a persona description or a set of instructions that define the tone for the response.
* **user\_instructions**: the main prompt that directs the model in producing responses.

When creating the index, you can set **`rag_pipeline`** as the default search pipeline by adding:

```
				
					PUT /my_rag_test_data
{
  "settings": {
    "index.search.default_pipeline" : "rag_pipeline"
  },
  "mappings": {
    "properties": {
      "text": {
        "type": "text"
      }
    }
  }
}
				
			
```

The RAG search pipeline will then be applied at search time, but first, we need to create the conversation history session:

```
				
					POST /_plugins/_ml/memory/
{
  "name": "Conversation Session 1"
}
				
			
```

he output of this request will be a memory ID that will be used to add the messages to the memory. A message is a question–answer pair: the user’s query and the LLM’s response. All the messages belonging to the same conversation must be grouped under a single memory. If they are not, a new memory has to be created, essentially starting a new session. Otherwise, there is a risk of building an overly long and confusing memory, which could negatively affect both costs and performance.

The final step is to leverage both the RAG pipeline and the memory when executing a query:

```
				
					GET /my_rag_test_data/_search?search_pipeline=rag_pipeline
{
  "query": {
    "match": {
      "text": "What's the population of NYC metro area in 2023"
    }
  },
  "ext": {
    "generative_qa_parameters": {
      "llm_question": "What's the population of NYC metro area in 2023",
      "memory_id": "znCqcI0BfUsSoeNTntd7",
      "context_size": 5,
      "message_size": 5
    }
  }
}
				
			
```

Here, the important parameters of the `ext.generative_qa_parameters` object are:

* **llm\_question** (required): the natural language query passed to the LLM for generating an answer.
* **memory\_id**: the ID obtained in the previous step must be specified if you want the conversation history to be included in the LLM prompt.
* **context\_size**: the number of search results sent to the LLM.
* **message\_size** (default 10): the number of memory messages sent to the LLM.  
  *[Here](https://docs.opensearch.org/latest/vector-search/ai-search/conversational-search#step-6-use-the-pipeline-for-rag) is the complete list of available parameters*.

### Semantic Field Type

*[Since version: 3.1]*

In the latest OpenSearch version (3.1), the [semantic field type](https://docs.opensearch.org/latest/field-types/supported-field-types/semantic) has been introduced; it is like a shortcut for setting up neural search — you just define it, and OpenSearch handles the indexing and querying using the ML model (dense or sparse) you have configured. It can wrap many different field types (text, binary, keyword, etc.).

However, the documentation highlights some limitations:

* You must explicitly add the semantic field to your index mapping (it can’t be created automatically with dynamic mapping).
* A semantic field can’t be a subfield of another field.
* If a document is updated, (unnecessary) inference runs again on the semantic field even if its content hasn’t changed.
* Semantic field queries don’t work in cross-cluster search.

### Agentic Search

*[Since version: 3.2]*

[Agentic Search](https://docs.opensearch.org/latest/vector-search/ai-search/agentic-search), introduced as an experimental feature in version 3.2, is a new query type that leverages an agent-driven workflow. It takes a natural language query, interprets it, translates it behind the scenes into an OpenSearch DSL query, and executes it to return the search results.

To use this feature, you need to enable the `plugins.neural_search.agentic_search_enabled` flag, set up an agent with the [QueryPlanningTool](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/tools/query-planning-tool/), and run it with any supported [OpenSearch agent type](https://docs.opensearch.org/latest/ml-commons-plugin/agents-tools/agents/index/).

*Since this is a newly introduced experimental feature, it doesn’t make sense to go into too much detail at this stage. For those who are curious, please refer to the documentation, and if we find it interesting and relevant, we will discuss the topic in a dedicated blog post.*

---

We hope you found this blog post useful. Stay tuned — a similar blog post on Vespa will be coming soon.

## Need Help With This Topic?​​

If you’re struggling with OpenSearch, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with OpenSearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)