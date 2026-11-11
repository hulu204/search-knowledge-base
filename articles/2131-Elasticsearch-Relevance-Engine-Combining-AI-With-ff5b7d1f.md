---
title: 'Elasticsearch Relevance Engine: Combining AI With Elastic’s Text Search'
company: Sease
tag: 工程相关
date: 2023-07-26
url: https://sease.io/2023/07/elasticsearch-relevance-engine-combining-ai-with-elastics-text-search.html
account: 
origin: harvest3-202607
---
Hello readers!

We recently dropped a blog post on the [improvements in Elasticsearch versions 8.6 and 8.7,](https://sease.io/2023/05/elasticsearch-neural-search-improvements-in-8-6-and-8-7.html) and guess what? We are back again with another incredible release!

With version 8.8, Elasticsearch has made a significant announcement as many powerful features and tools were introduced for boosting your search experience.

Therefore, in this blog post, our goal is to first describe what has been added (enhancements and new features) for the basic license and then highlight everything related to semantic search with enterprise/platinum subscriptions.

## What is NEW in 8.8 - Basic License

```
 1) Increase max number of vector dims to 2048 PR #95257
```

*`dims`*, is the mapping parameter to specify the dimension of the dense vector to pass in.  
Until 8.7, the maximum allowed number of vector dimensions is 1024 for indexed vectors (`"index": true`) and 2048 for non-indexed vectors.  
Although in the current version of Lucene, this limit is still set to 1024, with this pull request (PR #95257), both *KnnFloatVectorField* and *KnnByteVectorField* classes in Elasticsearch have been overridden to increase the limit to 2048 for indexed vectors.

```
2) Add new similarity field to knn clause in _search API PR #94828
```

As we already know, the approximate nearest neighbor (ANN) is integrated into the \_search API, adding the knn option in the request body.  
With this PR a new property of the knn object has been added: **`similarity`**, which allows filtering nearest neighbor results that are outside a given similarity.

What happens is that for each shard, the query will search num\_candidates and only keep those that are within the provided similarity boundary, and then reduce, as usual, to the global top k only.

## What is NEW in 8.8 - Enterprise/Platinum License

With 8.8, Elastic is taking its **enterprise search technology** to new heights by introducing the ***[Elasticsearch Relevance Engine (ESRE)](https://www.elastic.co/enterprise-search/generative-ai)***. This innovative advancement perfectly integrates artificial intelligence (AI) and vector search, offering you a toolkit for building innovative search applications.

With a few clicks, ESRE will allow you to generate, store, and query embeddings in high dimensions and implement semantic search (which finds information based on meaning, not word matching) using your own transformer model, third-party PyTorch models or a built-in retrieval model named Elastic Late Sparse EncodeR.

### What does ESRE include?

##### Elastic’s vector database

ESRE has expanded Elasticsearch’s vector support to a wider range of capabilities.  
Instead of storing and searching only vector embeddings, with ESRE you can experience full vector search through their **creation**, allowing you to capture the meaning and context of unstructured data, such as text and images.

##### Elastic Late Sparse EncodeR (ELSER)

With 8.8 there is the possibility to use a new built-in transformer **model** which brings ready-to-use **semantic search** capabilities by using **sparse vector representation**:  
[**Elastic Late Sparse EncodeR** (ELSER)](https://www.elastic.co/guide/en/machine-learning/8.8/ml-nlp-elser.html)   
It is a machine-learning model, trained and optimized by Elastic, for enhanced ingestion and query expansion.

To perform a semantic search on your data using ELSER, a new query clause has been added: a `text_expansion` query. The process involves:  
– creating an index mapping containing a field with the [`rank_features`](https://www.elastic.co/guide/en/elasticsearch/reference/8.8/rank-features.html) field type which will be used to index the token-weight pairs created by the ELSER model  
– creating an ingest pipeline with an inference processor to leverage ELSER to infer against the data  
– running a text\_expansion query, providing the ID of the model and the query text

*A blog post showcasing a practical application of this part will be published soon. Stay tuned!*

###### REQUIREMENTS

* Platinum or Enterprise subscription —> ES offers the ability to access (and explore) all subscription features with a [30-day free trial](https://www.elastic.co/guide/en/elasticsearch/reference/current/start-trial.html)
* It requires at least one ML node with a minimum of 4GB of memory

###### ADVANTAGES

* Adaptable for various use cases out of the box
* No need to fine-tune it on your domain data
* No need to worry about the size and cost of running large language models
* Easy downloading and deployment in a few clicks using:
  + the [**Trained Models** page](https://www.elastic.co/guide/en/machine-learning/8.8/ml-nlp-elser.html#trained-model)
  + the **[Dev Console](https://www.elastic.co/guide/en/machine-learning/8.8/ml-nlp-elser.html#dev-console)**
  + the inference pipeline directly from the [Enterprise Search](https://www.elastic.co/guide/en/machine-learning/8.8/ml-nlp-elser.html#enterprise-search)
* Zero machine learning expertise
* Query performance and index size are good; [here](https://www.elastic.co/blog/may-2023-launch-information-retrieval-elasticsearch-ai-model) are some benchmarks where you can find how ELSER outperforms lexical search.

###### MODEL CHARACTERISTICS

* **Name**: .elser\_model\_1
* **Type**: BERT
* **Model size bytes**: 417.8MB
* **Requires Native Memory Bytes**: 1.1GB

###### CURRENT LIMITATION

`Max_sequence_lenght: 512`  
The search process in ELSER takes into account only the initial 512 tokens extracted from each field of the ingested documents. They suggest using documents where most information is stored in the first 300–400 words; otherwise, if your data set contains long documents and a full-text need to be searchable, the recommendation is to divide them into smaller segments before ingestion.

For more info, take a look at these blog posts [[1](https://www.elastic.co/blog/may-2023-launch-sparse-encoder-ai-model)] and [[2](https://www.elastic.co/blog/may-2023-launch-information-retrieval-elasticsearch-ai-model)].

###### Integration With Third-Party Transformer Models

As we have seen in previous blog posts, Elasticsearch offers the ability to easily access third-party PyTorch models from any location, including those hosted on the HuggingFace model hub.

By using the Eland library (Elasticsearch Python client), loading models into Elasticsearch is simplified, enabling various NLP tasks and use cases within the Elasticsearch framework. Elasticsearch supports a wide range of architectures (such as BERT, BART, ELECTRA, etc.).

###### Integration with OpenAI

Within ESRE, Elasticsearch supports the integration with OpenAI and its GPT-3/GPT-4 large language models (LLM), empowering organizations to use the full potential of generative AI with Elasticsearch content.

ElasticDoc ChatGPT uses a Python interface to accept user questions. After retrieving the top results (combining BM25 and kNN search approaches), an API call is made to OpenAI ChatCompletion and the program crafts a prompt to pass the query and the top search result’s body content. The generated response is returned to Python and printed on the screen for the user.

Here you can find more information [[3](https://www.elastic.co/blog/chatgpt-elasticsearch-openai-meets-private-data)] and [[4](https://www.elastic.co/blog/may-2023-launch-machine-learning-models)].

###### Integration with third-party tooling

With ESRE there is the possibility to integrate Elasticsearch with third-party tooling, such as [LangChain](https://python.langchain.com/en/latest/modules/indexes/vectorstores/examples/elasticsearch.html), an open-source Python library that can be used to facilitate the development of advanced data pipelines and generative AI applications powered by large language models.

More information can be found in this [blog post](https://www.elastic.co/blog/privacy-first-ai-search-langchain-elasticsearch).

###### Reciprocal Rank Fusion (RRF)

With 8.8 support for [Reciprocal Rank Fusion (RRF)](https://www.elastic.co/guide/en/elasticsearch/reference/8.8/rrf.html) to the search API was added.  
RRF is a hybrid ranking method able to “combine multiple results sets with different relevance indicators into a single result set”. This allows developers to easily pair vector and textual search capabilities.

RRF only relies on positions within each result set, eliminating the need for normalizing scores between different sets of results. This is the primary benefit of using this ranking method.

Explore the documentation page if you are interested in learning more about the RRF, how to use it, and the formula that determines the score for ranking each document.

## Need Help with this topic?​

If you're struggling with combining AI With Elastic’s Text Search, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)