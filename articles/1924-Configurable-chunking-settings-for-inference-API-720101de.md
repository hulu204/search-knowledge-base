---
title: 'Configurable chunking settings for inference API endpoints'
company: Elastic
tag: RAG
date: 2025-03-21
url: https://www.elastic.co/search-labs/blog/elasticsearch-chunking-inference-api-endpoints
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Configurable chunking settings for inference API endpoints

Elasticsearch open inference API extends support for configurable chunking for document ingestion with semantic text fields.

March 21, 2025

[Daniel Rubinstein](/search-labs/author/daniel-rubinstein)

[AI](/search-labs/blog/category/ai)

Jump to

Share

The Elasticsearch Inference API allows users to utilize machine learning models across a variety of providers to perform inference operations. One common use case of this API is to support semantic text fields used for semantic search within an index. As the size of a document’s data increases, creating an embedding on the whole of the data will yield less accurate results. Some inference models also have limitations on the size of inputs that can be processed. As such, the inference API utilizes a process called chunking to break down large documents being ingested into an index into smaller and more manageable subsections of the original data called chunks. The inference operations are then run against each of the individual chunks and the inference results for each chunk are stored within the index.

In this blog, we’ll go over the chunking strategies, explain how Elasticsearch chunks text and how to configure chunking settings for an inference endpoint.

## What can I configure with chunking settings?

From 8.16, users can now select from 2 strategies for generating chunks, each with their own configurable properties.

### Word based chunking strategy

Configurable values provided by the user:

* (required) `max_chunk_size`: The maximum number of words in a chunk.
* (required) `overlap`: The number of overlapping words for chunks.

  + Note: This can not be defined as more than half of the `max_chunk_size`.

Word based chunking splits input data into chunks with word counts up to the provided `max_chunk_size`. This strategy will always fill a chunk to the maximum size before building the next chunk unless it reaches the end of the input data. Each chunk after the first will have a number of words overlapping from the previous chunk based on the provided `overlap` value. The purpose of this overlap is to increase inference accuracy by preventing useful context for inference results from being split across chunks.

### Sentence based chunking strategy

Configurable values provided by the user:

* (required) `max_chunk_size`: The maximum number of words in a chunk.
* (required) `sentence_overlap`: The number of overlapping sentences for chunks.

  + Note: This can only be defined as 0 or 1.

Sentence based chunking will split input data into chunks containing full sentences. Chunks will contain only complete sentences, except when a sentence is longer than `max_chunk_size`, in which case it will be split across chunks. Each chunk after the first will have a number of sentences from the previous chunk overlapping based on the provided `sentence_overlap` value.

Note: If no chunking settings are provided when creating an inference endpoint after 8.16, the default chunking settings will use a `sentence` strategy with `max_chunk_size` of 250 and a `sentence_overlap` of 1. For inference endpoints created before 8.16, the default chunking settings will use a `word` strategy with a `max_chunk_size` of 250 and an `overlap` of 1.

## How do I select a chunking strategy?

There is no one-size-fits-all solution for the best chunking strategy. The best chunking strategy will vary based on the documents being ingested, the underlying model being used and any compute constraints you have. We recommend taking a subset of your corpus and some example queries and seeing how changing the strategy, chunk size and overlap affects your use case. For example, you might parameter sweep over different chunk overlaps and lengths and measure the time to ingest, the impact on search latency and the relevance of the top results for each query.

The following are a few guidelines to help when starting out with configurable chunking:

### Picking a chunking strategy

Generally, a sentence based chunking strategy works well to minimize context loss. However, it can often result in more chunks being generated as the process prioritizes keeping sentences intact over maximally filling each chunk. As such, an optimized word based chunking strategy may produce fewer chunks, which are more efficient to ingest and search.

### Picking a chunk size

The chunk size should be selected to minimize useful contextual information from being split across chunks while retaining chunk topic coherence. Typically, chunks as close as possible to the maximum sequence length the model supports work better. However, long chunks are more likely to contain a mixture of topics that are less well represented.

### Picking a chunk overlap

As the overlap between chunks increases, the number of chunks generated does as well. Similar to chunk size, you'll want to select an overlap that helps to minimize the chance of splitting important context across chunks subject to your compute constraints. Typically, more overlap, up to half the typical chunk length, results in better retrieval quality but comes at an increased cost.

## How does Elasticsearch chunk text?

Elasticsearch uses the [ICU4J](https://unicode-org.github.io/icu-docs/) library to detect word and sentence *boundaries*. [Word boundaries](https://unicode-org.github.io/icu/userguide/boundaryanalysis/#word-boundary) are identified by following a series of rules, not just the presence of a whitespace character. For written languages that do not use whitespace, such as Chinese or Japanese, dictionary lookups are used to detect word boundaries. [Sentence boundaries](https://unicode-org.github.io/icu/userguide/boundaryanalysis/#sentence-boundary) are similarly identified by following a series of rules, not just the presence of a period character. This ensures that sentence boundaries are accurately identified across languages in which sentence structures and sentence breaking characteristics may vary.

Finally, we note that sometimes chunks benefit from long range context, which can't be retained by any simple chunking strategy. In these cases, if you are prepared to pay the cost, chunks can be enriched with additional generated context. For more details, see [this](https://www.anthropic.com/news/contextual-retrieval) discussion.

## How do I configure chunking settings for an inference endpoint?

### Pre-requisites

Before configuring chunking settings, ensure that you have met the following requirements:

1. You have a valid enterprise license.
2. If you are configuring chunking settings for an inference endpoint connecting to any third-party integration, you have set up any necessary permissions to access these services (e.g.**,** created accounts, retrieved API keys, etc.).

   * For the purposes of this guide, we will be configuring chunking settings for an inference endpoint using [Elastic’s ELSER model](https://www.elastic.co/guide/en/machine-learning/8.17/ml-nlp-elser.html), for which the only requirement is having a valid enterprise license. To find the information required to create an inference endpoint for a third-party integration, see the [create inference endpoint API documentation](https://www.elastic.co/guide/en/machine-learning/8.17/ml-nlp-elser.html).

### Step 1: Configure chunking settings during inference endpoint creation

```
client.inference.put(
	task_type="sparse_embedding",
	inference_id="my_elser_endpoint",
	body={
"service": "elasticsearch",
    		"service_settings": {
	"num_allocations": 1,
			"num_threads": 1,
			"model_id": ".elser_model_2"
  		},
		"chunking_settings": {
			"strategy": "sentence",
			"max_chunk_size": 25,
			"sentence_overlap": 1
		}
	}
)
```

### Step 2: Link the inference endpoint to a semantic text field in an index

```
client.indices.create(
index="my_index",
mappings={
    		"properties": {
        		"infer_field": {
            			"type": "semantic_text",
            			"inference_id": "my_elser_endpoint"
        		}
    		}
	}
)
```

### Step 3: Ingest a document into the index

Ingest the document into the index created above by calling the index document API:

```
client.index(index="my_index", document={
	"infer_field": "This is some sample document data. The data is being used to demonstrate the configurable chunking settings feature. The configured chunking settings will determine how this text is broken down into chunks to help increase inference accuracy."
})
```

The generated chunks and their corresponding inference results can be seen stored in the document in the index under the key `chunks` within the `_inference_fields` metafield. To see the stored chunks, you can search for all documents in the index with the search API :

```
client.search(index="my_index", body = {
    	'size' : 100,
    	'query': {
        	'match_all' : {}
    	},
       'fields': [ '_inference_fields' ]
})
```

The chunks can be seen in the response. Before 8.18, the chunks were stored as full-chunk text values. From 8.18, the chunks are stored as a list of character offset values:

```
...
'chunks': {
	'infer_field': [
    	{'start_offset': 0, 'end_offset': 117, 'embeddings':[...]},
    	{'start_offset': 34, 'end_offset': 198, 'embeddings':[...]},
    	{'start_offset': 120, 'end_offset': 242, 'embeddings':[...]}
	]
}
...
```

## Get started with configurable chunking today!

For more information on utilizing this feature, view the documentation on [configuring chunking](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html#infer-chunking-config). Try out this notebook to get started with configurable chunking settings: [Configuring Chunking Settings For Inference Endpoints](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/document-chunking/configuring-chunking-settings-for-inference-endpoints.ipynb).

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