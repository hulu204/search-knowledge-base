---
title: 'OpenSearch Neural Search Plugin Tutorial: Additional Useful Tools'
company: Sease
tag: 召回
date: 2024-01-09
url: https://sease.io/2024/01/opensearch-neural-search-plugin-tutorial-additional-useful-tools.html
account: 
origin: harvest3-202607
---
If you have already read our first blog about the [OpenSearch Neural Search Plugin Tutorial](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html) for version 2.4.0, you can find other tools here that might be useful to you. If you haven’t read the blog yet, we recommend starting there and then coming back here to learn more about the OpenSearch plugin.

We will first list other ML Common APIs you can use to manage the model and then, as a last part of the blog post, we would like to give a brief summary of which approximate k-NN algorithms are available, providing some general details to help you identify the one that best aligns with your needs.

## Other common ML APIs

##### Search models

The command reported below is used if you want to [check all the models](https://opensearch.org/docs/2.4/ml-commons-plugin/api/#search-model) created:

###### REQUEST

```
				
					curl --location --request GET 'https://localhost:9200/_plugins/_ml/models/_search' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{
  "query": {
    "match_all": {}
  }
}'
				
			
```

###### RESPONSE

```
				
					{
  "took": 857,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 10,
      "relation": "eq"
    },
    "max_score": 1.0,
    "hits": [
      {
        "_index": ".plugins-ml-model",
        "_id": "loaded_neural_model_id_0",
        "_version": 1,
        "_seq_no": 1,
        "_primary_term": 1,
        "_score": 1.0,
        "_source": {
          "model_version": "1.0.0",
          "created_time": 1670131677672,
          "chunk_number": 0,
          "model_format": "TORCH_SCRIPT",
          "name": "all-MiniLM-L6-v2",
          "model_id": "loaded_neural_model_id",
          "total_chunks": 9,
          "algorithm": "TEXT_EMBEDDING"
        }
      },
      {
        "_index": ".plugins-ml-model",
        "_id": "loaded_neural_model_id_1",
        ...
        ...
				
			
```

In our case, we load only one model, but the total number of results (total hits) in the response is 10; this is because OpenSearch segments the model into smaller pieces (chunks), and stores them in the model’s index. Generally, deep learning models are quite large, often exceeding 100 MB, which makes it difficult to fit them within a single document; for this reason, the larger the model, the more chunks it is divided into.

In this example, the model *all-MiniLM-L6-v2* which is approximately 80 MB, was split into 10 smaller parts (from 0 to 9).

##### Unload model

For completeness, we also include the request to unload the model:

```
				
					curl --location --request POST 'https://localhost:9200/_plugins/_ml/models/loaded_neural_model_id/_unload' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

In the command, replace *“loaded\_neural\_model\_id”* with the actual ID of the model you wish to unload.

After this step, the model will still be accessible in the model index, it was just removed from the memory cache.

##### Delete model

If instead, you want to remove the created model, you can use this command:

```
				
					curl --location --request DELETE 'https://localhost:9200/_plugins/_ml/models/loaded_neural_model_id' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

In the command, replace *“loaded\_neural\_model\_id”* with the actual ID of the model you wish to delete.

After this procedure, the model becomes inaccessible as it is completely removed from the model index.

## METHODS And ENGINES

As we have already seen in the previous post, when creating indices containing vector fields, it is necessary to define a `method`, i.e. the underlying configuration of the approximate k-NN algorithm, and with the `engine` parameter it is necessary to define the related library to be used for indexing and searching.

The available similarity search libraries for Approximate Nearest Neighbor Search are three: *Faiss*, *Non-Metric Space Library* *(NMSLIB)*, and *Lucene*.  
In the table below, you can find some general information about them, such as their licenses, the programming languages used, and the implementation algorithms employed:

|  | *[**Faiss**](https://github.com/facebookresearch/faiss)* | **[Non-Metric Space Library (NMSLIB)](https://github.com/nmslib/nmslib)** | **[**Lucene**](https://github.com/apache/lucene)** |
| --- | --- | --- | --- |
| **License** | MIT License | Apache 2 License | Apache 2 License |
| **Language** | C++ JNI to bridge java-C++ | C++ JNI to bridge java-C++ | Java |
| **Supported Algorithm** | – [HNSW](https://arxiv.org/pdf/1603.09320.pdf) – [IVF](https://www.sciencedirect.com/science/article/abs/pii/S0020025522006806) | – [HNSW](https://arxiv.org/pdf/1603.09320.pdf) | – [HNSW](https://arxiv.org/pdf/1603.09320.pdf) |

As you can see, all of them support the algorithm HNSW (the acronym for hierarchical navigable small world graph), while only the Faiss library supports the IVF algorithm (which stands for inverted file).

It is not the scope of this blog post to explore these algorithms in detail, you just need to know that they are both designed to efficiently find approximate nearest neighbors (ANN) in high-dimensional spaces;  
they have their own strengths and weaknesses and the choice between them depends on the specific use case.

##### Recommendations for METHODS

###### No Memory Constraints:

– Opt for **HNSW**, which offers an excellent balance between query latency and query quality.

###### If Memory Constraints:

– Opt for **IVF**, which allows you to maintain a similar query quality, using less memory and with faster indexing;  
– Consider adding a **PQ** (product quantization) encoder to the HNSW or IVF index; this is a lossy compression technique that will therefore decrease the query quality.

*Bear in mind that, unlike HNSW, the IVF algorithm requires a model training phase.*

##### Recommendations for ENGINES

If you do not specify the engine parameter in the request for index creation, the default engine value is *`nmslib`*. Generally speaking, it shows superior performance compared to Faiss and Lucene.

Otherwise, here you can find some recommendations depending on the library:

###### faiss

* Maximum number of vector dimensions: 16000
* Better to use it with hardware that includes a GPU
* Efficient for high-dimensional vectors
* It tends to be better in building (less indexing time and space)

###### nmslib

* Maximum number of vector dimensions: 16000
* Better to use when only the CPU is available
* Supports non-metric spaces and unconventional data
* It tends to be faster but has less recall

###### lucene

* Maximum number of vector dimensions: 1024
* Better to use for smaller datasets (up to a few million vectors)
* High customization

## What’s Next?

I hope this blog post has been helpful in gaining a more comprehensive view of the OpensSearch neural search plugin.

***We invite you to stay tuned, as the new versions of OpenSearch have taken off and many new features have been added. Very soon we will publish a series of posts specifically on the latest version on various topics, such as filtering, hybrid search, sparse search, multimodal search, how to connect to remote models, and much more.***

## Need Help with this topic?​

If you're struggling with Neural Search in OpenSearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)