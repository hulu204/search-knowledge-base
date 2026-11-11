---
title: 'OpenSearch KNN Plugin Tutorial'
company: Sease
tag: 召回
date: 2024-01-18
url: https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html
account: 
origin: harvest3-202607
---
In the [first blog post](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html), we have seen how the OpenSearch Neural Search Plugin took neural search a step forward, making it easy to manage language models, use them to transform the text into vectors (both at index and query time), and finally use these vectors in the retrieval phase.

In the [second blog post](https://sease.io/2024/01/opensearch-neural-search-plugin-tutorial-additional-useful-tools.html), you can find other useful ML Common APIs to manage the model and a brief overview with suggestions of libraries for approximate neighbor search; this last section is particularly useful for this tutorial to select the most suitable library for the Approximate k-NN.

In this blog post, we are going to explore the OpenSearch k-NN Plugin [[1](https://opensearch.org/docs/latest/search-plugins/knn/index/)], which offers three different approaches for retrieving the k-nearest neighbors (k-NN) from a vector index.   
We will give a detailed description of the plugin through our end-to-end testing experience illustrating in detail how the plugin works for:

* + Approximate k-NN [[2](https://opensearch.org/docs/latest/search-plugins/knn/approximate-knn/)]

* + Exact k-NN [[3](https://opensearch.org/docs/latest/search-plugins/knn/knn-score-script/)]

* + k-NN Painless Scripting extensions [[4](https://opensearch.org/docs/latest/search-plugins/knn/painless-functions/)]

For the tutorial we will again use the Neural Search pipeline to manipulate documents during ingestion, allowing the document text to be converted into vector embeddings using a large language model.  
We are also going to cover a new feature that was introduced in version 2.9 called [Model access control](https://opensearch.org/docs/latest/ml-commons-plugin/model-access-control/).

## Workflow

Let’s begin by exploring the end-to-end workflow to implement *k-nearest neighbors* search using OpenSearch.

1. Run OpenSearch
2. Upload a Large Language Model (with Model Access Control)
   * Register a Model Group
   * Register a pre-trained model to the model group
   * Deploy the model
3. Indexing phase
   * Create an ingest pipeline
   * Create an index of vectors
   * Index documents
4. Query phase
   * Query Inference
   * Approximate k-NN
   * Exact k-NN Search
   * k-NN Painless Scripting extensions

As can be seen, the first steps of the pipeline are the same for all the methodologies; we will then see what the differences are at query time.

##### 1. RUN OPENSEARCH

For this tutorial, we use the latest version of OpenSearch, which is **2.11**.

As suggested by the [documentation page](https://opensearch.org/versions/opensearch-2-11-0.html), we use **Docker Compose** to run OpenSearch.  
To execute it, you simply need to:  
– correctly configure the Docker environment (in particular the virtual machine)  
– download the *[docker-compose.yml](https://opensearch.org/samples/docker-compose.yml)* file  
– execute the following command from the folder that contains the docker-compose file:

```
				
					docker-compose up
				
			
```

For this tutorial, we use cURL requests. API calls require authentication therefore for every cURL operation in our tutorial you will find the header:

```
				
					--header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

where *YWRtaW46YWRtaW4=* is the authorization token computed as a Base64 encoded string representing your username and password values. For OpenSearch the default authentication values are *username=admin* and *password=admin*).

You can copy and execute all the following cURL requests using either Bash or Postman.

##### 2. UPLOAD A LARGE LANGUAGE MODEL (with MODEL ACCESS CONTROL)

As already said, in this tutorial, we are going to use a large language model to manipulate documents during ingestion, allowing the document text to be converted into vector embeddings internally and automatically.

OpenSearch offers a range of open-source pre-trained models and we will use one of them. Here you can find the[list of all the supported pre-trained sentence transformer models](https://opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/#supported-pretrained-models).  
We upload a model called [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (the same used in the [first blog post](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html)) which is a natural language processing (NLP) pre-trained (and fine-tuned) sentence transformer model.

In addition, we’re going to cover a new feature that was introduced in version 2.9, called [Model Access Control](https://opensearch.org/docs/latest/ml-commons-plugin/model-access-control/).  
Model Access Control is a way to control and manage who has access to specific machine learning models and features in an organization, based on the roles assigned to them (e.g. IT role: *ml\_full\_access* or HR role: *ml\_readonly\_access*).  
This system allows detailed control over who can do what, making it easier to manage access for a group of users rather than setting permissions for each individual user.

To use this functionality we must enable both the [Security plugin](https://opensearch.org/docs/latest/security/index/) and the Model Access Control on the cluster.  
Also, for the simplicity of this tutorial, we use a basic configuration **without dedicated ML nodes**.  
The following API can be used to change the cluster settings to reflect these conditions:

```
				
					curl --location --request PUT 'https://localhost:9200/_cluster/settings' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "persistent": {
    "plugins": {
      "ml_commons": {
        "only_run_on_ml_node": "false",
        "model_access_control_enabled": "true",
        "native_memory_threshold": "99"
      }
    }
  }
}'
				
			
```

###### 2.1 REGISTER A MODEL GROUP

Model access control is managed using the [Model group APIs](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-group-apis/index/) designed for model group operations such as registering, searching, updating, or deleting the group.

The following [API](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-group-apis/register-model-group/) with the `_register` endpoint can be used to register a model group (which is a collection of versions of a particular model):

```
				
					curl --location --request POST 'https://localhost:9200/_plugins/_ml/model_groups/_register' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "name": "KNN_model_group",
  "description": "A model group for KNN Plugin Tutorial",
  "access_mode": "public"
}'
				
			
```

where:

– **name**: [REQUIRED – String] The name for the model group  
– **description**: [OPTIONAL – String] A description of the model group  
– **access\_mode**: [OPTIONAL – String] Set to `public` for simplicity of the tutorial, otherwise, you can set it `private` (default) or `restricted` to limit access.

Other fields that can be specified only if `access_mode` is `restricted` are:  
– **backend\_roles** [OPTIONAL – Array] To specify a list of the model owner’s backend roles  
– **add\_all\_backend\_roles** [OPTIONAL – Boolean] Default is *`false`*. You must set it to *`true`*, to add all backend roles of the model owner to the model group.

*Both cannot be specified at the same time.*

###### RESPONSE

```
				
					{
    "model_group_id": "h6098IsBvXr78vpjsHcx",
    "status": "CREATED"
}
				
			
```

We have created a model group named “KNN\_model\_group” that can be accessed by all users who have access to the cluster. Copy and save the **model group ID** to use it in the subsequent request.

###### 2.2 REGISTER A PRE-TRAINED MODEL TO THE MODEL GROUP

We can now use the [Model APIs](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/index/) to register, deploy (or undeploy) a model.  
The following is the [request to register a model](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/register-model/) to the model group created previously:

```
				
					curl --location 'https://localhost:9200/_plugins/_ml/models/_register' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "name": "huggingface/sentence-transformers/all-MiniLM-L6-v2",
  "version": "1.0.1",
  "model_group_id": "h6098IsBvXr78vpjsHcx",
  "model_format": "TORCH_SCRIPT"
}'
				
			
```

where:  
– **name**: [REQUIRED – String] The model name to use for text embedding, in our case *all-MiniLM-L6-v2*  
– **version**: [REQUIRED – Integer] The model version  
– **model\_group\_id**: [OPTIONAL – String] The model group ID to register the model to  
– **model\_format**: [REQUIRED – String] The portable format of the model file. In this case, *`TORCH_SCRIPT`*. Another value accepted is *`ONNX`*.

Only these request fields are needed, as the model is an OpenSearch-provided model and comes from the ML Commons repository.

###### RESPONSE

```
				
					{
    "task_id": "iK1B8IsBvXr78vpjNHfS",
    "status": "CREATED"
}
				
			
```

We have registered the model “*all-MiniLM-L6-v2*” to the model group “KNN\_model\_group”.  
As we have seen in the [second blog post](https://sease.io/2024/01/opensearch-neural-search-plugin-tutorial-additional-useful-tools.html), since the model is greater than 10MB in size it will be divided into smaller parts (chunks) to be stored in a model index, i.e. 10 (from 0 to 9).

Copy and save the **task ID** to check the status of the model registration using the [Task APIs](https://opensearch.org/docs/2.11/ml-commons-plugin/api/tasks-apis/index/):

```
				
					curl --location --request GET 'https://localhost:9200/_plugins/_ml/tasks/iK1B8IsBvXr78vpjNHfS' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

###### RESPONSE

```
				
					{
    "model_id": "ia1B8IsBvXr78vpjPHd1",
    "task_type": "REGISTER_MODEL",
    "function_name": "TEXT_EMBEDDING",
    "state": "COMPLETED",
    "worker_node": [
        "2UOcogivTUC2Y1A0TiHyjA"
    ],
    "create_time": 1700542887119,
    "last_update_time": 1700542902463,
    "is_async": true
}
				
			
```

By passing the **task ID** in the GET Task request, we have obtained information about the task status (which is COMPLETED) and thus about the model, such as the **model ID** that will be needed in the next request to deploy the model.

###### 2.3 DEPLOY THE MODEL

After obtaining the **model ID**, use it in the [deploy API](https://opensearch.org/docs/latest/ml-commons-plugin/api/model-apis/deploy-model/) to retrieve the model from the model index and load it into memory for use; an instance of the model is saved in the ML node’s cache.

```
				
					curl --location --request POST 'https://localhost:9200/_plugins/_ml/models/ia1B8IsBvXr78vpjPHd1/_deploy' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

###### RESPONSE

```
				
					{
    "task_id": "ja1G8IsBvXr78vpj7nda",
    "task_type": "DEPLOY_MODEL",
    "status": "CREATED"
}
				
			
```

From the response, save the **task ID** again and use it to check the status of the model deployment using the [GET Task API](https://opensearch.org/docs/2.11/ml-commons-plugin/api/tasks-apis/get-task/):

```
				
					curl --location --request GET 'https://localhost:9200/_plugins/_ml/tasks/ja1G8IsBvXr78vpj7nda' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

###### RESPONSE

```
				
					{
    "model_id": "ia1B8IsBvXr78vpjPHd1",
    "task_type": "DEPLOY_MODEL",
    "function_name": "TEXT_EMBEDDING",
    "state": "COMPLETED",
    ...
}
				
			
```

The deploy model task is COMPLETED and the model is now ready to be used for inference.

*N.B. Every time you re-start the server, you need to re-deploy the model in memory.*

##### 3. INDEXING PHASE

This part is identical to the one already described for the Neural search in the first blog post, so here for simplicity we will just report on the requests related to the indexing phase, but for more information please refer to the related parts of the [first blog post](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html) (3. CREATE A NEURAL SEARCH PIPELINE, 4. CREATE AN INDEX CONTAINING VECTOR FIELDS, 5. INDEX DOCUMENTS)

###### 3.1 CREATE AN INGEST PIPELINE

###### REQUEST

```
				
					curl --location --request PUT 'https://localhost:9200/_ingest/pipeline/knn_pipeline' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{
  "description": "An example KNN search pipeline",
  "processors" : [
    {
      "text_embedding": {
        "model_id": "ia1B8IsBvXr78vpjPHd1",
        "field_map": {
           "general_text": "general_text_knn"
        }
      }
    }
  ]
}'
				
			
```

With this request, the pipeline named `knn_pipeline` was created and we defined *`general_text`* as the input field from which to take the text to create the vector embeddings and *`general_text_knn`* as the output field on which to store them.

###### 3.2 CREATE AN INDEX OF VECTORS

###### REQUEST

```
				
					curl --location --request PUT 'https://localhost:9200/my_knn_index' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{
    "settings": {
        "index.knn": true,
        "default_pipeline": "knn_pipeline"
    },
    "mappings": {
        "properties": {
            "general_text_knn": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "engine": "lucene"
                }
            },
            "general_text": {
                "type": "text"
            }
        }
    }
}'
				
			
```

With this request, the index named `my_knn_index` was created and we defined 2 fields: *`general_text_knn`* to store vector embeddings and *`general_text`* the source field from which to create embeddings.

N.B.  
If you ONLY want to use the Exact k-NN search, it’s recommended to:  
– set **index.knn** to `false`  
– notset**index.knn.space\_type**  
The advantage of this method is that it results in faster indexing and reduced memory usage, however, it comes at the cost of losing the capability to conduct approximate k-NN queries on the index.

###### 3.3 INDEX DOCUMENTS

This is the *[\_bulk](https://opensearch.org/docs/2.4/api-reference/document-apis/bulk/)* request we use to push several documents (at once) into our k-NN index.

###### REQUEST

```
				
					curl --location --request POST 'https://localhost:9200/_bulk' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{"create":{"_index":"my_knn_index", "_id":"0"}}
{"general_text":"The presence of communication amid scientific minds was
equally important to the success of the Manhattan Project as scientific
intellect was. The only cloud hanging over the impressive achievement of
the atomic researchers and engineers is what their success truly meant;
hundreds of thousands of innocent lives obliterated."}
{"create":{"_index":"my_knn_index", "_id":"1"}}
{"general_text":"The Manhattan Project and its atomic bomb helped bring an
end to World War II. Its legacy of peaceful uses of atomic energy continues
to have an impact on history and science."}
{"create":{"_index":"my_knn_index", "_id":"2"}}
{"general_text":"Essay on The Manhattan Project - ...'
				
			
```

Execution of this command will result in the indexing of our [MS MARCO](https://microsoft.github.io/msmarco/) documents, each containing the text with the corresponding vector (created using the knn\_pipeline).

##### 4. QUERY PHASE

###### 4.1 QUERY INFERENCE

To execute a *k-nearest neighbors* search, we need to transform the textual query into a vector and use it in the KNN query type.  
Once the language model is loaded, it is possible to use it for**inference** using the [Predict API](https://opensearch.org/docs/latest/ml-commons-plugin/api/train-predict/predict/) and passing the **model ID** in the request:

```
				
					curl --location --request POST 'https://localhost:9200/_plugins/_ml/_predict/text_embedding/ia1B8IsBvXr78vpjPHd1' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "text_docs":[ "What is a bank transit number"],
  "return_number": true,
  "target_response": ["sentence_embedding"]
}'
				
			
```

The query reported in the above example is: `"what is a bank transit number"`.

###### RESPONSE

The output will be an array of floats (`data` object) of shape 384:

```
				
					{
    "inference_results": [
        {
            "output": [
                {
                    "name": "sentence_embedding",
                    "data_type": "FLOAT32",
                    "shape": [
                        384
                    ],
                    "data": [
                        -0.009013666,
                        -0.07266349,
                        ...
                        -0.1163235
                    ]
                }
            ]
        }
    ]
}
				
			
```

For ease of reading, we have reduced the length of the (very long) vector by inserting dots.

We can now copy and use the vector obtained in the following k-NN queries.

###### 4.2 APPROXIMATE KNN

The [Approximate k-NN](https://opensearch.org/docs/latest/search-plugins/knn/approximate-knn/) uses algorithms that approximate the nearest neighbors (such as HNSW and IVF), so it does not search exhaustively through all vector data. This method trades off a bit of accuracy for a significant gain in efficiency.  
**Features**: Low latency, scalable  
**Use Case**: Approximate k-NN is ideal for scenarios where there is a need to process large volumes of data/vectors

We can execute an approximate k-NN search using the following `knn` query type:

```
				
					curl --location --request GET 'https://localhost:9200/my_knn_index/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "size": 5,
  "query": {
    "knn": {
      "general_text_knn": {
        "vector": [
                        -0.009013666,
                        -0.07266349,
                       ...
                        -0.1163235
                    ],
        "k": 3
      }
    }
  },
  "_source": [
     "general_text"
  ]
}'
				
			
```

where:  
– **size**: indicates how many results the query actually returns  
– **general\_text\_knn**: our knn vector field  
– **vector**: is the query vector obtained using the Predict API in the step above. The dimension needs to be equal to the model dimension (i.e. *384)*  
– **k**: the number of nearest neighbors you want to retrieve (10,000 is the maximum value accepted)

###### RESPONSE

```
				
					{
    ...
    },
    "hits": {
        "total": {
            "value": 3,
            "relation": "eq"
        },
        "max_score": 0.44739452,
        "hits": [
            {
                "_index": "my_knn_index",
                "_id": "7686",
                "_score": 0.44739452,
                "_source": {
                    "general_text": "A. A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS. Your tax ID number is used to identify your business to several federal agencies responsible for the regulation of business."
                }
            },
            {
                "_index": "my_knn_index",
                "_id": "7691",
                "_score": 0.44169965,
                "_source": {
                    "general_text": "A. A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS."
                }
            },
            {
                "_index": "my_knn_index",
                "_id": "7692",
                "_score": 0.43761322,
                "_source": {
                    "general_text": "Lets start at the beginning. A tax ID number or employer identification number (EIN) is a number you get from the U.S. federal government that gives an identification number to a business, much like a social security number does for a person."
                }
            }
        ]
    }
}
				
			
```

Having set k*=3*, we got the best three documents for the query “*what is a bank transit number*“.

###### 4.3 EXACT KNN

In the Exact k-NN with scoring script, the method employed is called “Brute Force”, which involves an exhaustive search through all the vector data (every single point in the dataset) for finding the k closest points (neighbors) to a given query point.  
**Features**: A distinctive feature of this variant is that it supports [binary data](https://opensearch.org/docs/latest/search-plugins/knn/knn-score-script/#getting-started-with-the-score-script-for-binary-data) with the Hamming distance space.  
**Use Case**: While straightforward, this approach can be inefficient with large data volumes, but it’s very direct and accurate. The primary use of this method is in scenarios with small datasets or in dynamic search contexts. In the latter case, pre-filtering can be applied to refine and reduce the data to be examined.

We can execute an Exact k-NN search using the following query type:

```
				
					curl --location --request GET 'https://localhost:9200/my_knn_index/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
 "size": 3,
 "query": {
   "script_score": {
     "query": {
       "match_all": {}
     },
     "script": {
       "lang": "knn",
       "source": "knn_score",
       "params": {
         "field": "general_text_knn",
         "query_value": [
                        -0.009013666,
                        -0.07266349,
                        ...
                        -0.1163235
                    ],
         "space_type": "cosinesimil"
       }
     }
   }
 },
  "_source": [
     "id"
  ]
}'
				
			
```

where:  
– **source**: is the name of the script  
– **lang**: is the script type, in this case `knn`  
– **field**: the name of the vector field, in this case `general_text_knn`  
– **query\_value**: is the query vector obtained using the Predict API in the step above  
– **space\_type**: specifies the distance function to be used to find the nearest neighbors, in this case, the cosine similarity. [Here](https://opensearch.org/docs/latest/search-plugins/knn/knn-score-script/#spaces) you can find all the space functions supported. In OpenSearch,a**higher score equals a closer and better result.**

**All the above parameters are mandatory.**

###### RESPONSE

```
				
					{
    ...
    "hits": {
        "total": {
            "value": 10000,
            "relation": "eq"
        },
        "max_score": 1.382418,
        "hits": [
            {
                "_index": "my_knn_index",
                "_id": "7686",
                "_score": 1.382418
            },
            {
                "_index": "my_knn_index",
                "_id": "7691",
                "_score": 1.3680089
            },
            {
                "_index": "my_knn_index",
                "_id": "7692",
                "_score": 1.3574384
            }
        ]
    }
}
				
			
```

In this case, we used a `match_all` query to match all documents (i.e. 10000), but unless you are working with very small indices this query is not really scalable and can significantly increase search latency.  
We set the size parameter to 3 and the query returned the 3 most relevant documents, which are the same as the Approximate k-NN query.

###### 4.4 KNN PAINLESS SCRIPTING EXTENSIONS

This [approach](https://opensearch.org/docs/latest/search-plugins/knn/painless-functions/) combines the Brute Force method with custom options, allowing users to tailor the search according to their domain-specific requirements.  
**Features**: A key feature is the support for distance functions as painless extensions.  
**Use Case**: This variant is typically used when there is a need for customization in score calculation or adapting the method to specific use cases that require a more tailored approach. For instance, you can multiply the score value or incorporate other fields from the document into the calculation equation.

The available functions are the following and [here](https://opensearch.org/docs/latest/search-plugins/knn/painless-functions/#function-types) you can find more information about them:

– **l2Squared**  
– **l1Norm**  
– **cosineSimilarity**

The following is the request to execute a k-NN search using the painless scripting extension:

```
				
					curl --location --request GET 'https://localhost:9200/my_knn_index/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
 "size": 3,
 "query": {
   "script_score": {
     "query": {
       "match_all": {}
     },
     "script": {
       "source": "1.0 + cosineSimilarity(params.query_value, doc[params.field])",
       "params": {
         "field": "general_text_knn",
         "query_value": [
                        -0.009013666,
                        -0.07266349,
                        ...
                        -0.1163235
                    ]
       }
     }
   }
 },
  "_source": [
     "id"
  ]
}'
				
			
```

where:  
– **source**: defined the script function; in this case, it executes a cosine similarity function between the value of `params.query_value` and the value of `params.field` in the document `doc`. to calculate the score and then sum 1.0 to the total.  
– **field**: the name of the knn vector field, in this case `general_text_knn`  
– **query\_value**: is the query vector obtained using the Predict API in the step above

N.B. The knn vector field must have the same dimensions as the query value and must have a value otherwise the function throws an Exception.

## What's next?

I hope this blog post has helped gain a more comprehensive view of the OpensSearch KNN search plugin.

***We invite you to stay tuned, as very soon we will publish more blog posts on various topics, such as filtering, hybrid search, sparse search, multimodal search, how to connect to remote models, and much more.***

## Need help with this topic?

If you're struggling with the Knn plugin in OpenSearch , don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)