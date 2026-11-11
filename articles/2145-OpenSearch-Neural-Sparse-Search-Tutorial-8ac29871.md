---
title: 'OpenSearch Neural Sparse Search Tutorial'
company: Sease
tag: 召回
date: 2024-07-16
url: https://sease.io/2024/07/opensearch-neural-sparse-search-tutorial.html
account: 
origin: harvest3-202607
---
Hi readers,

so far we have already published a series of blog posts about the latest integrations in OpenSearch, specifically:

* [OpenSearch KNN Plugin Tutorial](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html): how the KNN plugin works and how to manage models using Model Access Control
* [OpenSearch Neural Search Tutorial: How Filtering Works](https://sease.io/2024/03/opensearch-neural-search-tutorial-how-filtering-works.html)
* [OpenSearch Neural Search Tutorial: Hybrid Search](https://sease.io/2024/04/opensearch-neural-search-tutorial-hybrid-search.html)

This blog post will focus on exploring Neural Sparse Search, a new feature introduced in the OpenSearch 2.11 release.   
If you are using a version before 2.11, OpenSearch only offers a dense retrieval approach for text-based vector search; however, as of version 2.11, it also includes the sparse retrieval option, which presents an alternative approach to neural text search.  
We will give a detailed description of this new addition through our end-to-end testing experience.

## Sparse Search vs Semantic Search in OpenSearch

Semantic search, using dense retrieval based on text embedding models to search for textual data, effectively delivers high search relevance. However, this effectiveness comes at a cost: the processes of embedding creation, specialized data structure indexing (like HNSW for vector indexing), and k-NN search within these structures lead to significant memory and CPU resource consumption.

As an alternative, sparse search uses neural search with sparse retrieval based on sparse embedding models to search text data. This approach in OpenSearch involves the creation of sparse vectors, which are key-value pairs indicating the importance of various terms, and integrates them into a [rank features field type](https://opensearch.org/docs/latest/field-types/supported-field-types/rank/).

## Sparse Vector

The first thing we need to define to understand sparse vectors is their dimensionality. This is equal to the size of the dictionary, meaning, the vector has as many elements as there are terms in the dictionary.  
What is a dictionary then? The dictionary is a collection of terms, usually created during the training of a sparse model and includes all the distinct terms found within the training dataset.  
In most cases, given the vast number of terms in a typical dictionary, these vectors are high-dimensional.

![sparse vector](https://i0.wp.com/sease.io/wp-content/uploads/2025/12/96a71c0c08ba669c5a5a3af564cbffee81af9c6d-1920x1080-1.png?fit=800%2C450&ssl=1) 

Image illustrating the difference between sparse and dense vectors, sourced from Pinecone

A **sparse vector** represents a document and therefore it will show non-zero values only for those terms that are present in the document. These values reflect the frequency or importance of these terms in the context of the document. As a result, while the vector has a large number of elements, most of these elements will have a value of zero, indicating the absence of the corresponding dictionary term in the document. It is called sparse because is sparsely populated with information.  
This method is particularly effective for large datasets where traditional dense vector methods might be computationally expensive.

## Workflow

Let’s begin by exploring the end-to-end workflow to perform a **Neural Sparse search** using OpenSearch.

1. Run OpenSearch (version >= 2.11)
2. Upload a Large Language Model (with Model Access Control)
   * Register a Model Group
   * Register a pre-trained model to the model group
   * Deploy the model
3. Indexing phase
   * Create an ingest pipeline
   * Create an index for ingestion
   * Index documents
4. Query phase
   * Neural Sparse Search

##### 1. RUN OPENSEARCH

For this tutorial, we use version 2.11 of OpenSearch, as it’s the version that first introduced neural sparse search.

You can follow the instructions already described in the first chapter of [this blog post](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html) to run OpenSearch.

##### 2. UPLOAD A LARGE LANGUAGE MODEL (with MODEL ACCESS CONTROL)

Before using neural sparse search, you need to choose and deploy a sparse encoding model to transfer text into a sparse vector.   
OpenSearch supports 3 pre-trained sparse encoding models (trained by OpenSearch itself) and we will use one of them. The list of all pre-trained models supported by OpenSearch, with their detailed information and descriptions, can be found [here](https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/#sparse-encoding-models).

To control and manage the model we use the [Model Access Control](https://opensearch.org/docs/latest/ml-commons-plugin/model-access-control/); in this tutorial, we will only report the necessary requests, but you can find more information on this in the second chapter of [this blog post](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html).

###### 2.1 REGISTER A MODEL GROUP

The initial step involves registering a model group, which can be done using the following request:

```
				
					curl --location 'https://localhost:9200/_plugins/_ml/model_groups/_register' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "name": "Neural_sparse_model_group",
  "description": "A model group for Neural Sparse Search Tutorial",
  "access_mode": "public"
}'
				
			
```

**RESPONSE**

```
				
					{
    "model_group_id": "PRspM4wBXjvqXchabEL3",
    "status": "CREATED"
}
				
			
```

We have created a model group named “*Neural\_sparse\_model\_group*” that can be accessed by all users who have access to the cluster. Copy and save the **model group ID** to use it in the subsequent request.

###### 2.2 REGISTER A PRE-TRAINED MODEL TO THE MODEL GROUP

The following is the request to register a sparse model to the model group created previously:

```
				
					curl --location 'https://localhost:9200/_plugins/_ml/models/_register' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
    "name": "amazon/neural-sparse/opensearch-neural-sparse-encoding-v1",
    "version": "1.0.0",
    "model_group_id": "PRspM4wBXjvqXchabEL3",
    "description": "This is a neural sparse encoding model: It transfers text into sparse vector, and then extract nonzero index and value to entry and weights. It serves only in ingestion and customer should use tokenizer model in query.",
    "model_format": "TORCH_SCRIPT",
    "function_name": "SPARSE_ENCODING",
    "model_content_hash_value": "d1ebaa26615090bdb0195a62b180afd2a8524c68c5d406a11ad787267f515ea8",
    "url":  "https://artifacts.opensearch.org/models/ml-models/amazon/neural-sparse/opensearch-neural-sparse-encoding-v1/1.0.0/torch_script/opensearch-neural-sparse-encoding-v1-1.0.0-torch_script.zip"
}'
				
			
```

where:

* **name** [REQUIRED – String]: is the sparse encoding model name to use.
* **version** [REQUIRED – Integer]: is the model version (can be found in the [config\_url](https://artifacts.opensearch.org/models/ml-models/amazon/neural-sparse/opensearch-neural-sparse-encoding-v1/1.0.0/torch_script/config.json)).
* **model\_group\_id** [OPTIONAL – String]: is the model group ID to register the model to.
* **description** [OPTIONAL – String]: is the model description (taken from [config\_url](https://artifacts.opensearch.org/models/ml-models/amazon/neural-sparse/opensearch-neural-sparse-encoding-v1/1.0.0/torch_script/config.json)).
* **model\_format** [REQUIRED – String]: is the portable format of the model file. In this case, *`TORCH_SCRIPT`*. Another value accepted is *`ONNX`*.
* **function\_name** [REQUIRED – String]: is the function to use. In this case, *`SPARSE_ENCODING`*. Another value accepted is *`SPARSE_TOKENIZE`*.
* **model\_content\_hash\_value** [REQUIRED – String]: is the model hash generated using the SHA-256 hashing algorithm (can be found in the [config\_url](https://artifacts.opensearch.org/models/ml-models/amazon/neural-sparse/opensearch-neural-sparse-encoding-v1/1.0.0/torch_script/config.json)).
* **url** [REQUIRED – String]: is the URL that contains the model (can be found in the *model\_url* [here](https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/#sparse-encoding-models)).

We have registered the model “***amazon/neural-sparse/opensearch-neural-sparse-encoding-v1***” (one of the three models supported by OpenSearch) to the model group “*Neural\_sp*

**RESPONSE**

```
				
					{
    "task_id": "PxsqM4wBXjvqXchaRUKJ",
    "status": "CREATED"
}
				
			
```

Copy and save the **task ID** to check the status of the model registration using the [Task APIs](https://opensearch.org/docs/2.11/ml-commons-plugin/api/tasks-apis/index/):

```
				
					curl --location --request GET 'https://localhost:9200/_plugins/_ml/tasks/PxsqM4wBXjvqXchaRUKJ' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
    "model_id": "QBsqM4wBXjvqXchaRULi",
    "task_type": "REGISTER_MODEL",
    "function_name": "SPARSE_ENCODING",
    "state": "COMPLETED",
    "worker_node": [
        "A1mg5nJXRrGXYpih4dMcew"
    ],
    "create_time": 1701665457544,
    "last_update_time": 1701665554913,
    "is_async": true
}
				
			
```

By passing the **task ID** in the GET Task request, we have obtained information about the task status (which is COMPLETED) and thus about the model, such as the **model ID** that will be needed in the next request to deploy the model.

###### 2.3 DEPLOY THE MODEL

After obtaining the **model ID**, use it in the [deploy API](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/deploy-model/) to retrieve the model from the model index and load it into memory for use; an instance of the model is saved in the ML node’s cache.

```
				
					curl --location --request POST 'https://localhost:9200/_plugins/_ml/models/QBsqM4wBXjvqXchaRULi/_deploy' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
    "task_id": "QRssM4wBXjvqXchaC0LS",
    "task_type": "DEPLOY_MODEL",
    "status": "CREATED"
}
				
			
```

From the response, save the **task ID** again and use it to check the status of the model deployment using the [GET Task API](https://opensearch.org/docs/2.11/ml-commons-plugin/api/tasks-apis/get-task/):

```
				
					curl --location --request GET 'https://localhost:9200/_plugins/_ml/tasks/QRssM4wBXjvqXchaC0LS' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
    "model_id": "QBsqM4wBXjvqXchaRULi",
    "task_type": "DEPLOY_MODEL",
    "function_name": "SPARSE_ENCODING",
    "state": "COMPLETED",
   ...
}
				
			
```

The deploy model task is COMPLETED and the model is now ready to be used for inference.  
*N.B. Every time you re-start the server, you need to re-deploy the model in memory.*

##### 3. INDEXING PHASE

###### 3.1 CREATE AN INGEST PIPELINE

To implement a neural sparse search, you must configure an ingest pipeline with a **sparse encoding** **processor**.

An [ingest pipeline](https://opensearch.org/docs/latest/ingest-pipelines/index/) consists of a series of processors applied to documents during their insertion into an index. Each processor within this pipeline is tasked with a specific function, such as data filtering, transformation, or enrichment.

The [sparse encoding](https://opensearch.org/docs/latest/ingest-pipelines/processors/sparse-encoding/) is the processor that converts a text field into sparse vectors, i.e. a list of <token, weight> pairs, representing an entry and its weight.

This is the request to create an ingest pipeline named ***neural\_sparse\_pipeline***:

```
				
					curl --location --request PUT 'https://localhost:9200/_ingest/pipeline/neural_sparse_pipeline' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "description": "An example sparse encoding ingest pipeline",
  "processors": [
    {
      "sparse_encoding": {
        "model_id": "QBsqM4wBXjvqXchaRULi",
        "field_map": {
          "general_text": "general_text_embedding"
        }
      }
    }
  ]
}'
				
			
```

where the required parameters for the `sparse_encoding` processor are:

* **model\_id** [String]: is the ID of the sparse model already deployed in the previous step.
* **field\_map** [Object]: contains key-value pairs that specify the mapping of a text field to a rank\_features field.
* **general\_text** [String]: the input field from which to take the text to create the vector embeddings.
* **general\_text\_embedding** [String]: the output field on which to store the embeddings.

It’s suggested to run a test on your pipeline before starting to ingest documents, using the following query:

```
				
					curl --location 'https://localhost:9200/_ingest/pipeline/neural_sparse_pipeline/_simulate' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "docs": [
    {
      "_index": "testindex",
      "_id": "1",
      "_source":{
         "general_text": "this is a test"
      }
    }
  ]
}'
				
			
```

**RESPONSE**

```
				
					{
    "docs": [
        {
            "doc": {
                "_index": "testindex",
                "_id": "1",
                "_source": {
                    "general_text_embedding": {
                        "hi": 0.033300262,
                        ...
                        "test": 2.673574,
                        ...
                        "testing": 2.3093011,
                        "this": 1.1874672,
                        ...
                        "is": 0.21865849,
                        ...
                        "tests": 1.0601465,
                        ...
                        "charlie": 0.616043
                    },
                    "general_text": "this is a test"
                },
                ...
            }
        }
    ]
}
				
			
```

The response shows the result after the document with id=1 has been processed by the *neural\_sparse\_pipeline*.  
In addition to the *general\_text* field, the sparse encoding processor generated the embedding in the *general\_text\_embedding* field.  
We can see a list of key-value pairs, i.e. a set of words with numbers next to them. As already said, these words are the terms present in the dictionary used by the model, and the numbers indicate the weight that shows how important each word is in the context of our document content, which in this case is “this is a test”.   
(For ease of reading, we have inserted dots instead of listing all the vector terms.)  
For example, the word “test” has a high weight (2.673574), meaning it’s very important in our document. This makes sense because our document *general\_text* field contains exactly the word “test”.

###### 3.2 CREATE AN INDEX OF VECTORS

With the following request, we create a rank features index named `my_neural_sparse_index`:

```
				
					curl --location --request PUT 'https://localhost:9200/my_neural_sparse_index' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "settings": {
    "default_pipeline": "neural_sparse_pipeline"
  },
  "mappings": {
    "properties": {
      "general_text_embedding": {
        "type": "rank_features"
      },
      "general_text": {
        "type": "text"
      }
    }
  }
}'
				
			
```

The index uses the **neural\_sparse\_pipeline** as the default ingest pipeline and 2 fields are defined:   
– *`general_text`* the source: the field from which to create embeddings.  
– *`general_text_embedding:`* the vector field to store embeddings. **[rank\_features](https://opensearch.org/docs/latest/field-types/supported-field-types/rank/#rank-features)** is the type to define the sparse vector field.

###### 3.3 INDEX DOCUMENTS

This is the *[\_bulk](https://opensearch.org/docs/2.4/api-reference/document-apis/bulk/)* request we use to push several documents (at once) into our *my\_neural\_sparse\_index* index:

```
				
					curl --location --request POST 'https://localhost:9200/_bulk' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{"create":{"_index":"my_neural_sparse_index", "_id":"0"}}
{"general_text":"The presence of communication amid scientific minds was
equally important to the success of the Manhattan Project as scientific
intellect was. The only cloud hanging over the impressive achievement of
the atomic researchers and engineers is what their success truly meant;
hundreds of thousands of innocent lives obliterated."}
{"create":{"_index":"my_neural_sparse_index", "_id":"1"}}
{"general_text":"The Manhattan Project and its atomic bomb helped bring an
end to World War II. Its legacy of peaceful uses of atomic energy continues
to have an impact on history and science."}
{"create":{"_index":"my_neural_sparse_index", "_id":"2"}}
{"general_text":"Essay on The Manhattan Project - ...'
				
			
```

Execution of this command will result in the indexing of our [MS MARCO](https://microsoft.github.io/msmarco/) documents, each containing the text with the corresponding sparse vector embedding (created using the *neural\_sparse\_pipeline*).

##### 4. QUERY PHASE

###### 4.1 NEURAL SPARSE SEARCH

To make sparse retrieval, you can use the following [neural\_sparse query](https://opensearch.org/docs/latest/query-dsl/specialized/neural-sparse/):

```
				
					curl --location --request GET 'https://localhost:9200/my_neural_sparse_index/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "_source": [
     "general_text"
  ],
  "query": {
    "neural_sparse": {
      "general_text_embedding": {
        "query_text": "what is a Manhattan Project",
        "model_id": "QBsqM4wBXjvqXchaRULi",
        "max_token_score": 3.5
      }
    }
  }
}'
				
			
```

where:

* **general\_text\_embedding**: is the vector field against which to run a search query
* **query\_text** [REQUIRED – String]: is the textual query
* **model\_id** [REQUIRED – String]: is the ID of the sparse model already deployed in the previous step.
* **max\_token\_score** [REQUIRED – Float]: is the theoretical upper bound of the score for all tokens in the vocabulary, used for performance optimization. It is recommended to set the value to 3.5 for the sparse model used in this tutorial (*opensearch-neural-sparse-encoding-v1*).

The response will contain the matching documents:

```
				
					...
},
    "hits": {
        "total": {
            "value": 8718,
            "relation": "eq"
        },
        "max_score": 21.607159,
        "hits": [
            {
                "_index": "my_neural_sparse_index",
                "_id": "7",
                "_score": 21.607159,
                "_source": {
                    "general_text": "Manhattan Project. The Manhattan Project was a research and development undertaking during World War II that produced the first nuclear weapons. It was led by the United States with the support of the United Kingdom and Canada. From 1942 to 1946, the project was under the direction of Major General Leslie Groves of the U.S. Army Corps of Engineers. Nuclear physicist Robert Oppenheimer was the director of the Los Alamos Laboratory that designed the actual bombs. The Army component of the project was designated the"
                }
            },
            {
                "_index": "my_neural_sparse_index",
                "_id": "3",
                "_score": 21.21589,
                "_source": {
                    "general_text": "The Manhattan Project was the name for a project conducted during World War II, to develop the first atomic bomb. It refers specifically to the period of the project from 194 â¦ 2-1946 under the control of the U.S. Army Corps of Engineers, under the administration of General Leslie R. Groves."
                }
            },
            {
                "_index": "my_neural_sparse_index",
                "_id": "2",
                "_score": 19.400118,
                "_source": {
                    "general_text": "Essay on The Manhattan Project - The Manhattan Project The Manhattan Project was to see if making an atomic bomb possible. The success of this project would forever change the world forever making it known that something this powerful can be manmade."
                }
            },
...
...
				
			
```

## What's next?

I hope this post has been helpful in better understanding how neural sparse search works in OpensSearch.

Stay tuned because a new blog post exploring **multimodal search** is coming soon.

## Need Help With This Topic?​​

If you’re struggling with Neural Sparse Search in OpenSearch, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Neural Sparse Search in OpenSearch, don't worry - we're here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)