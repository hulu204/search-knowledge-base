---
title: 'Elasticsearch new semantic_text mapping: Simplifying semantic search'
company: Elastic
tag: 索引构建
date: 2024-06-24
url: https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch new semantic\_text mapping: Simplifying semantic search

Learn how to use the new semantic\_text field type and semantic query for simplifying semantic search in Elasticsearch.

June 24, 2024

[Carlos Delgado](/search-labs/author/carlos-delgado)[Mike Pellegrini](/search-labs/author/mike-pellegrini)

[Vector Database](/search-labs/blog/category/vector-database)[Basics](/search-labs/blog/category/basics)

Jump to

Share

## semantic\_text - You know, for semantic search!

Do you want to start using semantic search for your data, but focus on your model and results instead of on the technical details? We’ve introduced the `semantic_text` field type that will take care of the details and infrastructure that you need.

[Semantic search](https://www.elastic.co/what-is/semantic-search) is a sophisticated technique designed to enhance the relevance of search results by utilizing [machine learning models](https://www.elastic.co/elasticsearch/machine-learning). Unlike traditional keyword-based search, semantic search focuses on understanding the meaning of words and the context in which they are used. This is achieved through the application of machine learning models that provide a deeper semantic understanding of the text.

These models generate [vector embeddings](https://www.elastic.co/what-is/vector-embedding), which are numeric representations capturing the text meaning. These embeddings are stored alongside your document data, enabling [vector search techniques](https://www.elastic.co/what-is/vector-search) that take into account the word meaning and context instead of pure lexical matches.

## How to perform semantic search

To perform semantic search, you need to go through the following steps:

* [Choose an inference mode](#choosing-an-inference-model)l to create embeddings, both for indexing documents and performing queries.
* [Create your index mapping](#creating-your-index-mapping) to store the inference results, so they can be efficiently searched afterwards.
* [Setting up indexing](#setting-up-indexing) so inference results are calculated for new documents added to your index.
* [Automatically handle long text documents](#automatically-handling-long-text-passages), so search can be accurate and cover the entire document.
* [Querying your data](#querying-your-data) to retrieve results.

Configuring semantic search from the ground up can be complex. It requires setting up mappings, ingestion pipelines, and queries tailored to your chosen inference model. Each step offers opportunities for fine-tuning and optimization, but also demands careful configuration to ensure all components work together seamlessly.

While this offers a great degree of control, it makes using semantic search a detailed and deliberate process, requiring you to configure separate pieces that are all related to each other and to the inference model.

[`semantic_text`](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html) simplifies this process by focusing on what matters: the inference model. Once you have selected the inference model, `semantic_text` will make it easy to start using semantic search by providing sensible defaults, so you can focus on your search and not on how to index, generate, or query your embeddings.

Let's take a look at each of these steps, and how `semantic_text` simplifies this setup.

### Choosing an inference model

The inference model will generate embeddings for your documents and queries. Different models have different tradeoffs in terms of:

* Accuracy and relevance of the results
* Scalability and performance
* Language and multilingual support
* Cost

Elasticsearch supports both internal and external inference services:

* Internal services are deployed in the Elasticsearch cluster. You can use already included models like [ELSER](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html) and [E5](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-e5.html), or import [external models](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-model-ref.html#ml-nlp-model-ref-text-embedding) into the cluster using [eland](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-import-model.html).
* External services are deployed by model providers. Elasticsearch supports the following:

  + [Cohere](https://www.elastic.co/search-labs/blog/elasticsearch-cohere-embeddings-support)
  + [Hugging Face](https://www.elastic.co/search-labs/integrations/hugging-face)
  + [Mistral](https://www.elastic.co/search-labs/integrations/mistral)
  + [OpenAI](https://www.elastic.co/search-labs/integrations/open-ai)
  + [Azure AI Studio](https://www.elastic.co/search-labs/blog/elasticsearch-azure-ai-studio-support)
  + [Azure OpenAI](https://www.elastic.co/search-labs/blog/elasticsearch-azure-openai-embeddings-support)
  + Google AI Studio

Once you have chosen the inference mode, [create an inference endpoint](https://www.elastic.co/guide/en/elasticsearch/reference/current/put-inference-api.html) for it. The inference endpoint identifier will be the only configuration detail that you will need to set up `semantic_text`.

```
PUT _inference/sparse_embedding/my-elser-endpoint
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}
```

### Creating your index mapping

Elasticsearch will need to index the embeddings generated by the model so they can be efficiently queried later.

Before semantic\_text, you needed to understand about the two main field types used for storing embeddings information:

* [`sparse_vector`](https://www.elastic.co/guide/en/elasticsearch/reference/current/sparse-vector.html): It indexes sparse vector embeddings, like the ones generated by ELSER. Each embedding consists of pairs of tokens and weights. There is a small number of tokens generated per embedding.
* [`dense_vector`](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html): It indexes vectors of numbers, which contains the embedding information. A model produces vectors of a fixed size, called the vector dimension.

The field type to use is conditioned by the model you have chosen. If using dense vectors, you will need to [configure](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html#dense-vector-params) the field to include the dimension count, the similarity function used to calculate vectors proximity, and storage customizations like quantization or the specific data type used for each element.

Now, if you're using semantic\_text, you define a [semantic\_text field mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html) by just specifying the inference endpoint identifier for your model:

```
PUT test-index
{
  "mappings": {
    "properties": {
      "infer_field": {
        "type": "semantic_text",
        "inference_id": "my-elser-endpoint"
      }
    }
  }
}
```

That's it. No need for you to define other mapping options, or to understand which field type you need to use.

### Setting up indexing

Once your index is ready to store the embeddings, it's time to generate them.

Before `semantic_text`, to generate embeddings automatically on document ingestion you needed to set up an [ingestion pipeline](https://www.elastic.co/guide/en/elasticsearch/reference/current/ingest.html).

Ingestion pipelines are used to automatically enrich or transform documents when ingested into an index, or when explicitly specified as part of the ingestion process.

You need to use the [inference processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-processor.html) to generate embeddings for your fields. The processor needs to be configured using:

* The text fields from which to generate the embeddings
* The output fields where the generated embeddings will be added
* Specific inference configuration for text embeddings or sparse embeddings, depending on the model type

With `semantic_text`, you simply add documents to your index. semantic\_text fields will automatically calculate the embeddings using the specified inference endpoint.

This means there's no need to create an inference pipeline to generate the embeddings. Using bulk, index, or update APIs will do that for you automatically:

```
PUT test-index/_doc/doc1
{
  "infer_field": "These are not the droids you're looking for. He's free to go around"
}
```

Inference requests in `semantic_text` fields are also batched. If you have 10 documents in a bulk API request, and each document contains 2 `semantic_text` fields, then that request will perform a single inference request with 20 texts to your inference service in one go, instead of making 10 separate inference requests of 2 texts each.

### Automatically handling long text passages

Part of the challenge of selecting a model is the number of tokens that the model can generate embeddings for. Models have a limited number of tokens they can process. This is referred to as the model’s context window.

If the text you need to work with is longer than the model’s context window, you may **truncate** the text and use just part of it to generate embeddings. This is not ideal as you'll lose information; the resulting embeddings will not capture the full context of the input text.

Even if you have a long context window, having a long text means a lot of content will be reduced to a single embedding, making it an inaccurate representation.

Also, returning a long text will be difficult for the users to understand, as they will have to scan the text to check it's what they are looking for. Using smaller snippets would be preferable instead.

Another option is to use **chunking** to divide long texts into smaller fragments. These smaller chunks are added to each document to provide a better representation of the complete text. You can then use a nested query to search over all the individual fragments and retrieve the documents that contain the best-scoring chunks.

Before `semantic_text`, chunking was not done out of the box - the inference processor did not support chunking. If you needed to use chunking, you needed to do it before ingesting your documents or use the script processor to perform the chunking in Elasticsearch.

Using semantic\_text means that chunking will be done on your behalf when indexing. Long documents will be split into 250-word sections with a 100-word overlap so that each section shares 100 words with the previous section. This overlap ensures continuity and prevents vital contextual information in the input text from being lost by a hard break.

If the model and inference service support batching the chunked inputs are automatically batched together into as few requests as possible, each optimally sized for the Inference Service. The resulting chunks will be stored in a nested object structure so you can check the text contained in each chunk.

### Querying your data

Now that the documents and their embeddings are indexed in Elasticsearch, it's time to do some queries!

Before `semantic_text`, you needed to use a different query depending on the type of embeddings the model generates (dense or sparse). A [sparse vector query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-sparse-vector-query.html) is needed to query sparse\_vector field types, and either a [knn search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html) or a [knn query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html) can be used to search dense\_vector field types.

The query process can be further customized for performance and relevance. For example, sparse vector queries can define [token pruning](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-sparse-vector-query.html#sparse-vector-query-with-pruning-config-and-rescore-example) to avoid considering irrelevant tokens. Knn queries can specify the number of candidates to consider and the top k results to be returned from each shard.

You don't need to deal with those details when using `semantic_text`. You use a [single query type](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-semantic-query.html) to search your documents:

```
GET test-index/_search
{
  "query": {
    "semantic": {
      "field": "infer_field",
      "query": "robots you're searching for"
    }
  }
}
```

Just include the field and the query text. There’s no need to decide between sparse vector and knn queries, semantic text does this for you.

Compare this with using a specific `knn` search with all its configuration parameters:

```
{
  "knn": {
    "field": "infer_field",
    "k": 10,
    "num_candidates": 100,
    "query_vector_builder": {
      "text_embedding": { 
        "model_id": "my-dense-vector-embedding-model", 
        "model_text": "robots you're searching for" 
      }
    }
  }
}
```

## Under the hood: How `semantic_text` works

To understand how `semantic_text` works, you can create a `semantic_text` index and check what happens when you ingest a document. When the first document is ingested, the inference endpoint calculates the embeddings. When indexed, you will notice changes in the index mapping:

```
GET test-index
{
  "test-index": {
    "mappings": {
      "properties": {
        "infer_field": {
          "type": "semantic_text",
          "inference_id": "my-elser-endpoint",
          "model_settings": {
            "task_type": "sparse_embedding"
          }
        }
      }
    }
  }
}
```

Now there is additional information about the model settings. Text embedding models will also include information like the number of dimensions or the similarity function for the model.

You can check the document already includes the embedding results:

```
GET test-index/_doc/doc1
{
  "_index": "test-sparse",
  "_id": "doc1",
  "_source": {
    "infer_field": {
      "text": "these are not the droids you're looking for. He's free to go around",
      "inference": {
        "inference_id": "my-elser-endpoint",
        "model_settings": {
          "task_type": "sparse_embedding"
        },
        "chunks": [
          {
            "text": "these are not the droids you're looking for. He's free to go around",
            "embeddings": {
              "##oid": 1.9103845,
              "##oids": 1.768872,
              "free": 1.693662,
              "dr": 1.6103356,
              "around": 1.4376559,
              "these": 1.1396849

              …
            }
          }
        ]
      }
    }
  }
}
```

The field does not just contain the input text, but also a structure storing the original text, the model settings, and information for each chunk the input text has been divided into.

This structure consists of an object with two elements:

* *text*: Contains the original input text
* *inference*: Inference information added by the inference endpoint, that consists of:

  + *inference\_id* of the inference endpoint
  + *model\_settings* that contain model properties
  + *chunks*: Nested object that contains an element for each chunk that has been created from the input text. Each chunk contains:

    - The *text* for the chunk
    - The calculated *embeddings* for the chunk text

## Customizing `semantic_text`

`semantic_text` simplifies semantic search by making default decisions about indexing and querying your data:

* uses `sparse_vector` or `dense_vector` field types depending on the inference model type
* Automatically defines the number of dimensions and similarity according to the inference results
* Uses `int8_hnsw` index type for dense vector field types to leverage [scalar quantization](https://www.elastic.co/search-labs/blog/evaluating-scalar-quantization).
* Uses query defaults. No token pruning is applied for `sparse_vector` queries, nor custom `k` and `num_candidates` are set for knn queries.

Those are sensible defaults and allow you to quickly and easily start working with semantic search. Over time, you may want to customize your queries and data types to optimize search relevance, index and query performance, and index storage.

### Query customization

There are no customization options - yet - for semantic queries. If you want to customize queries against `semantic_text` fields, you can perform [advanced semantic\_text search](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-semantic-query.html#advanced-search) using explicit knn and sparse vector queries.

We're planning to add [retrievers support](https://www.elastic.co/guide/en/elasticsearch/reference/current/retrievers-overview.html) for `semantic_text`, and adding configuration options to the `semantic_text` field so they won't be needed at query time. Stay tuned!

### Data type customization

If you need deeper customization for the data indexing, you can use the `sparse_vector` or `dense_vector` field types. These field types give you full control over how embeddings are generated, indexed, and queried.

You need to create an ingest pipeline with an inference processor to generate the embeddings. [This tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-inference.html) walks you through the process.

## What's next with `semantic_text`?

We're just getting started with `semantic_text`! There are quite a few enhancements that we will keep working on, including:

* Better inference error handling
* Customize the chunking strategy
* Hiding embeddings in \_source by default, to avoid cluttering the search responses
* Inner hits support, to retrieve the relevant chunks of information for a query
* Filtering and retrievers support
* Kibana support

## Try it out!

`semantic_text`is available on [Elasticsearch Serverless](https://www.elastic.co/elasticsearch/serverless) now! It will be available soon on Elasticsearch 8.15 version for [Elastic Cloud](https://www.elastic.co/cloud) and on [Elasticsearch downloads](https://www.elastic.co/downloads/elasticsearch).

If you already have an Elasticsearch serverless cluster, you can see a complete example for testing semantic search using `semantic_text` in [this tutorial](https://www.elastic.co/search-labs/blog/elasticsearch-cohere-rerank), or try it with [this notebook](https://colab.research.google.com/github/elastic/elasticsearch-labs/blob/main/notebooks/search/09-semantic-text.ipynb).

We'd love to hear about your experience with `semantic_text`! Let us know what you think in the [forums](https://www.elastic.co/community), or open an issue in the [GitHub repository](https://github.com/elastic/elasticsearch). Let's make semantic search easier together!

### Frequently Asked Questions

#### What is semantic search?

Semantic search is a sophisticated technique designed to enhance the relevance of search results by utilizing machine learning models. Unlike traditional keyword-based search, semantic search focuses on understanding the meaning of words and the context in which they are used.

#### What is semantic\_text in semantic search?

semantic\_text is a field type that simplifies semantic search by making default decisions about indexing and querying your data.

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