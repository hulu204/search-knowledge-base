---
title: 'OpenSearch Neural Search Plugin Tutorial'
company: Sease
tag: 召回
date: 2022-12-19
url: https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html
account: 
origin: harvest3-202607
---
Hi readers!  
In this blog post, we are going to explore the new **OpenSearch neural search [plugin](https://opensearch.org/docs/2.4/neural-search-plugin/index/)** introduced with version **2.4.0**!

The neural plugin is an experimental feature that allows users to easily integrate Machine Learning and Neural Network based Language Models in search. It manages the language models, uses them to transform the text into vectors (both at index and query time), and finally uses these vectors in the retrieval phase.

We will give a detailed description of the plugin through our end-to-end testing experience illustrating in detail how the plugin works for:

* **Model management and deployment**: upload an external model and monitor its status.
* **Indexing documents**: use the model to enrich documents with numerical vector representations of textual fields.
* **Searching**: use the model to execute neural queries.

We will then highlight advantages, limitations (or difficulties) in using it (if any), and features not yet available.

##### Workflow

Let’s start with an overview of the end-to-end workflow to implement a neural search using OpenSearch:

1. Download OpenSearch
2. Upload your model
3. Create a neural search pipeline
4. Create an index containing vector fields
5. Index documents
6. Search (exploiting vector fields)

The pipeline was performed twice, i.e. on two different operating systems:

* Ubuntu 22.04.1 LTS
* macOS Big Sur 11.7

We did not observe particular differences between the two systems in reproducing the entire pipeline.

##### 1. Download OpenSearch

You can download version 2.4.0 of OpenSearch from: <https://opensearch.org/lines/2x.html>

The only thing to pay attention to is the **correct setup of the environment**, particularly the *virtual machine* *(VM)* as described in: <https://opensearch.org/docs/2.4/install-and-configure/install-opensearch/index/#important-settings>  
Therefore:

* + Linux: ***`vm.max_map_count`*** has to be set to at least *262144*
  + MacOS: **RAM** has to be set to at least *4 GB* (in the Docker Resources)

For the 2.4.0 OpenSearch version, the compatible Java versions are 11 and 17.

As suggested by the [documentation page](https://opensearch.org/versions/opensearch-2-4-0.html), we use **Docker Compose** to try out OpenSearch. To execute it, you simply need to download the *[docker-compose.yml](https://opensearch.org/samples/docker-compose.yml)* from the documentation, change it by setting both the nodes and dashboard images with the desired version (e.g. *`image: opensearchproject/opensearch:2.4.0`*), and run:

```
				
					docker-compose up
				
			
```

This procedure will create a cluster of two nodes.

For this tutorial, we use cURL requests. API calls require authentication therefore for every cURL operation in our tutorial you will find the header:

```
				
					--header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

where *YWRtaW46YWRtaW4=* is the authorization token computed as a Base64 encoded string representing your username and password values. For OpenSearch the default authentication values are *username=admin* and *password=admin*).

Otherwise, if you want to use OpenSearch Dashboards, the default built-in visualization tool for data, simply navigate to <http://localhost:5601/> and log in with the default credentials.

##### 2. Upload your model

Once installed OpenSearch, the first thing to do is upload the model you want to use for your neural search. This is the one that will generate vectors from the text.

In order to do this, OpenSearch provides a framework called **Model Serving Framework** within the **ML-Commons plugin**: <https://opensearch.org/docs/2.4/ml-commons-plugin/model-serving-framework/>  
With this [API](https://opensearch.org/docs/2.4/ml-commons-plugin/api/) you can:

1. Upload an external model to OpenSearch
2. Load it in memory
3. Use the model for inferences
4. Unload the model

We will use all these features except the model inferences.

Even if it is easy to upload external models, there are still some limitations:

* Supported only text embedding **models without GPU acceleration**.  
  <https://opensearch.org/docs/2.4/ml-commons-plugin/model-serving-framework/#model-support>  
  <https://github.com/opensearch-project/ml-commons/issues/302>
* Supported only the [**TorchScript**](https://pytorch.org/docs/stable/jit.html) format of PyTorch. The TorchScript file you want to upload to OpenSearch needs to be saved as **zip**.
* Models with a size >=100 MB are split into chunks in order to be stored in a model index. **Pay attention to the size of the model** and monitor the performance to avoid downtime. <https://opensearch.org/docs/2.4/ml-commons-plugin/model-serving-framework/#model-support>

##### 2.1 Upload an external model

For this tutorial, we [upload](https://opensearch.org/docs/2.4/ml-commons-plugin/model-serving-framework/#upload-model-to-opensearch) a pre-trained(and fine-tuned) model called **[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)**, which is a natural language processing (NLP) sentence transformation model.  
The model type is **BERT**, the *hidden\_size* (so the *`embedding_dimension`*) is 384, and it is roughly 80MB.

We use the “*URL upload operation*” which gives the ability to pass several fields, such as the name, version, and format of the model, including the **URL** to specify where the model is located externally (such as GitHub, as in this case, or S3 servers).

**REQUEST**

```
				
					curl --location --request POST 
'https://localhost:9200/_plugins/_ml/models/_upload' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
  "name": "all-MiniLM-L6-v2",
  "version": "1.0.0",
  "description": "test model",
  "model_format": "TORCH_SCRIPT",
  "model_config": {
    "model_type": "bert",
    "embedding_dimension": 384,
    "framework_type": "sentence_transformers"
  },
  "url": "https://github.com/opensearch-project/ml-commons/raw/2.x/ml-
  algorithms/src/test/resources/org/opensearch/ml/engine/algorithms/text_embe
  dding/all-MiniLM-L6-v2_torchscript_sentence-transformer.zip?raw=true"
}'
				
			
```

**RESPONSE**

```
				
					{
  "task_id": "MOSa24QBNFSZcaBDreDP",
  "status": "CREATED"
}
				
			
```

From the response, save the *`task_id`* for the following step.

###### 2.2 Get the model id

To load the model, the *`model_id`* is required; save the *`task_id`* from the response of the “***model’s upload operations API***” and use it in the next steps to obtain the *`model_id`*:

**REQUEST**

```
				
					curl --location --request GET 
'https://localhost:9200/_plugins/_ml/tasks/MOSa24QBNFSZcaBDreDP' \
--header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
  "model_id": "loaded_neural_model_id",
  "task_type": "UPLOAD_MODEL",
  "function_name": "TEXT_EMBEDDING",
  "state": "COMPLETED",
  "worker_node": "aVrtho4BQhyDbA5QireffA",
  "create_time": 1670131658068,
  "last_update_time": 1670131682488,
  "is_async": true
}
				
			
```

The *`model_id`* is an id generated directly by OpenSearch, here we will use **loaded\_neural\_model\_id**, just for simplicity.

###### 2.3 Load model

Once got the *`model_id`*, you can pass it to the “***load API***” to read the model from the model index and load it in memory for use; an instance of the model is saved in the ML node’s cache.

**REQUEST**

```
				
					curl --location --request POST 
'https://localhost:9200/_plugins/_ml/models/loaded_neural_model_id/_load' \
--header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
  "task_id": "ROSg24QBNFSZcaBDJ-BT",
  "status": "CREATED"
}
				
			
```

From the response, save the *`task_id`* again and use it in the next step, to check the loading status of the model.

*N.B. every time you re-start the server, you need to re-load the model in memory.*

###### 2.3.1 Check the model load status

It is useful to use this API to check if the state of the load task is COMPLETED, otherwise, the model cannot be used.

**REQUEST**

```
				
					curl --location --request GET 
'https://localhost:9200/_plugins/_ml/tasks/ROSg24QBNFSZcaBDJ-BT' \
--header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
  "model_id": "loaded_neural_model_id",
  "task_type": "LOAD_MODEL",
  "function_name": "TEXT_EMBEDDING",
  "state": "COMPLETED",
  "worker_node": "bLM0_iO0S8aCJZ1snb91sg,aVrtho4BQhyDbA5QireffA",
  "create_time": 1670132016977,
  "last_update_time": 1670132069239,
  "is_async": true
}
				
			
```

##### 3. Create a neural search pipeline

Before the neural plugin release, in order to execute a search that exploits vector embeddings, it was necessary to:

1. Train a model outside OpenSearch.
2. Create vector embeddings from documents’ fields with a custom script.
3. Manually upload the embeddings into OpenSearch.

Thanks to the neural plugin, **it is now possible to automatically create vectors from text within OpenSearch**, defining a [**Neural Search pipeline**](https://opensearch.org/docs/2.4/neural-search-plugin/index/#ingest-data-with-neural-search).

A pipeline consists of a series of processors that manipulate documents during ingestion, allowing document text to be converted into vector embeddings.  
The only processor supported by neural search is the *text\_embedding*, where you can use the *field\_maps* parameter to determine:

* **Input field names**: from which fields to generate the vector embeddings.
* **Output field names**: in which field vector embeddings are stored.

In this pipeline creation example, we define *`general_text`* as the input field from which to take the text to create the vector embeddings and *`general_text_vector`* as the output field on which to store them.

**REQUEST**

```
				
					curl --location --request PUT 
'https://localhost:9200/_ingest/pipeline/neural_pipeline' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
  "description": "An example neural search pipeline",
  "processors" : [
    {
      "text_embedding": {
        "model_id": "loaded_neural_model_id",
        "field_map": {
           "general_text": "general_text_vector"
        }
      }
    }
  ]
}'
				
			
```

**RESPONSE**

```
				
					{
  "acknowledged": true
}
				
			
```

###### 3.1 Multiple vector fields mapping

If you want to create **vector embeddings for more than one textual field**, you can define all of them in the same pipeline inside the *`field_map`* parameter as shown below.

```
				
					curl --location --request PUT 
'https://localhost:9200/_ingest/pipeline/neural_pipeline' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
  "description": "An example neural search pipeline",
  "processors" : [
    {
      "text_embedding": {
        "model_id": "loaded_neural_model_id",
        "field_map": {
           "general_text": "general_text_vector",
           "second_general_text": "second_general_text_vector"
        }
      }
    }
  ]
}'
				
			
```

##### 4. Create an index containing vector fields

Now that the neural pipeline has been configured, we need to associate it with an [index](https://opensearch.org/docs/2.4/neural-search-plugin/index/#create-an-index-for-ingestion). This will be the index where we are going to add our vector fields.

When creating the index we need to define some parameters:

* the *`index.knn`* **setting** must be set to **true**. This will tell OpenSearch that we are going to store vectors and that we would like to use the k-NN search on this data.
* the **index mapping** has to include the **k-NN vector fields** to store the generated embeddings. These *`knn_vector`* fields need to have a dimension that matches the model one.   
  In our tutorial we define: *`general_text_vector`* to store vector embeddings, *`general_text`* the source field from which to create embeddings and *`color`* an additional field just used to show filter query behavior.
* the **neural pipeline** must be associated. In our tutorial, we define the `default_pipeline` to be our neural pipeline. Pay attention that the index fields align with the ones specified in the pipeline mapping.

For the *`general_text_vector`* field we further define:

* **type**: *knn\_vector* type
* **dimension**: needs to be equal to the model dimension. In this case *384*.
* **method**: the hierarchical proximity graph approach to Approximate k-NN search. In this case the *Hierarchical Navigable Small Worlds graph (hnsw).*
* **engine**: the approximate k-NN library to use for indexing and search. In this case, we selected *lucene*.

You can find further parameters and options in the OpenSearch [documentation](https://opensearch.org/docs/2.4/search-plugins/knn/knn-index/#method-definitions).

**REQUEST**

```
				
					curl --location --request PUT 'https://localhost:9200/my_neural_index' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
    "settings": {
        "index.knn": true,
        "default_pipeline": "neural_pipeline"
    },
    "mappings": {
        "properties": {
            "general_text_vector": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "engine": "lucene"
                }
            },
            "general_text": { 
                "type": "text"            
            },
            "color": {
                "type": "text"
            }
        }
    }
}'
				
			
```

**RESPONSE**

```
				
					{
  "acknowledged": true,
  "shards_acknowledged": true,
  "index": "my_neural_index"
}
				
			
```

##### 5. Index documents

We are now ready to index our documents.

This step is done as usual, with OpenSearch’s [Ingest API](https://opensearch.org/docs/2.4/api-reference/ingest-apis/index/). After each document ingestion, **the embedding vector will be automatically created** from the defined fields thanks to the neural pipeline associated with the neural index.

For this tutorial, we took one corpus of [MS MARCO](https://microsoft.github.io/msmarco/), a collection of large-scale information retrieval datasets for deep learning. In particular, we downloaded the passage retrieval collection: [collection.tar.gz](https://msmarco.blob.core.windows.net/msmarcoranking/collection.tar.gz) and indexed roughly 10k documents of it.  
As mentioned in the neural index creation phase, we also add an additional field to each document containing the name of a color. The color name is assigned randomly from a list of values (green, white, red, black, yellow, blue, orange, and pink).

This is the *[\_bulk](https://opensearch.org/docs/2.4/api-reference/document-apis/bulk/)* request we use to push several documents (at once) into our neural index:

**REQUEST**

```
				
					curl --location --request POST 'https://localhost:9200/_bulk' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{"create":{"_index":"my_neural_index", "_id":"0"}}
{"general_text":"The presence of communication amid scientific minds was
equally important to the success of the Manhattan Project as scientific
intellect was. The only cloud hanging over the impressive achievement of
the atomic researchers and engineers is what their success truly meant;
hundreds of thousands of innocent lives obliterated.","color":"red"}
{"create":{"_index":"my_neural_index", "_id":"1"}}
{"general_text":"The Manhattan Project and its atomic bomb helped bring an
end to World War II. Its legacy of peaceful uses of atomic energy continues
to have an impact on history and science.","color":"black"}
{"create":{"_index":"my_neural_index", "_id":"2"}}
{"general_text":"Essay on The Manhattan Project - ...'
				
			
```

**RESPONSE**

```
				
					{
  "took": 87,
  "ingest_took": 238,
  "errors": false,
  "items": [{
    "create": {
      "_index": "my_neural_index",
      "_id": "0",
      "_version": 1,
      "result": "created",
      "_shards": {
        "total": 2,
        "successful": 2,
        "failed": 0
      },
      "_seq_no": 1,
      "_primary_term": 1,
      "status": 201
    }
  },{
  "create": {
    "_index": "my_neural_index",
    "_id": "1",
    ...
    ...
				
			
```

In this case, we have included the index name in the body of the request, otherwise, it can be specified only once in the path:

```
curl --location --request POST 
'https://localhost:9200/my_neural_index/_bulk'
```

N.B. At the end of the request body, a blank line is required!

##### 6. Search exploiting vector fields

Thanks to the plugin, we do not have to worry anymore about generating externally the query vector and passing it to OpenSearch.   
It provides a custom query type called [**neural query**](https://opensearch.org/docs/2.4/neural-search-plugin/index/#ingest-data-with-neural-search) that will automatically:

1. Use the language model to compute the query vector from the query text.
2. Convert the user-provided query into a [k-NN vector query](https://opensearch.org/docs/2.4/search-plugins/knn/index/).

To make some queries, we downloaded the passage retrieval queries from MS Marco: [queries.tar.gz](https://msmarco.blob.core.windows.net/msmarcoranking/queries.tar.gz)

###### 6.1 Neural query

Here is an example of a neural query, the one introduced with the plugin.   
It uses the user-provided language model to convert a textual query into a k-NN vector query.

**REQUEST**

```
				
					curl --location --request GET 
'https://localhost:9200/my_neural_index/_search' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
    "_source": [
        "general_text"
    ],
    "query": {
        "neural": {
            "general_text_vector": {
                "query_text": "what is a bank transit number",
                "model_id": "loaded_neural_model_id",
                "k": 3
            }
        }
    }
}'
				
			
```

In this case, we have:

**general\_text\_vector** = the field to execute the k-NN query against  
**query\_text** = (string) the query text (from *queries.tar.gz*)  
**model\_id** = (string) ID of the language model, previously uploaded  
**k** = (int) number of results to return from the k-NN search.

**RESPONSE**

```
				
					{
    "took": 105,
    "timed_out": false,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 3,
            "relation": "eq"
        },
        "max_score": 0.44739452,
        "hits": [
            {
                "_index": "my_neural_index",
                "_id": "7686",
                "_score": 0.44739452,
                "_source": {
                  "general_text": "A. A federal tax identification number
                  (also known as an employer identification number or EIN), is a number
                  assigned solely to your business by the IRS. Your tax ID number is
                  used to identify your business to several federal agencies responsible
                  for the regulation of business."
                }
            },
            {
                "_index": "my_neural_index",
                "_id": "7691",
                "_score": 0.44169965,
                "_source": {
                  "general_text": "A. A federal tax identification number (also known as
                  an employer identification number or EIN), is a number assigned solely
                  to your business by the IRS."
                }
            },
            {
                "_index": "my_neural_index",
                "_id": "7692",
                "_score": 0.43761322,
                "_source": {
                  "general_text": "Lets start at the beginning. A tax ID number or
                  employer identification number (EIN) is a number you get from the U.S.
                  federal government that gives an identification number to a business,
                  much like a social security number does for a person."
                }
            }
        ]
    }
}
				
			
```

###### 6.2 Filter + Neural query

Let’s see through an example how filters are managed when executing a neural query.

Suppose to execute the neural query in the example before but with *k*=8:

```
				
					curl --location --request GET 
'https://localhost:9200/my_neural_index/_search' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
    "query": {
        "neural": {
            "general_text_vector": {
                "query_text": "what is a bank transit number",
                "model_id": "loaded_neural_model_id",
                "k": 8
            }
        }
    }
}'
				
			
```

In this case, the response contains eight documents with the following colors (in order):

1. Red
2. Red
3. White
4. Orange
5. Blue
6. Green
7. White
8. White

Now suppose to make a combined query with both a filter and a neural query:

```
				
					curl --location --request GET 
'https://localhost:9200/my_neural_index/_search' \
--header 'Authorization: Basic YWRtaW46YWRtaW4=' \
--header 'Content-Type: application/json' \
--data-raw '{
    "query": {
        "bool": {
            "filter": {
                "term": {
                    "color": "white"
                }
            },
            "must": {
                "neural": {
                    "general_text_vector": {
                        "query_text": "what is a bank transit number",
                        "model_id": "loaded_neural_model_id",
                        "k": 3
                    }
                }
            }
        }
    }
}'
				
			
```

The aim of this query is to obtain the best three documents for the query “*what is a bank transit number”*.

In the response, we obtain 1 hit with a single “white” document.  
**Why are we obtaining just one document if we set *k*=3?**  
This is because OpenSearch executes a **post-filtering** on this query.

We can easily see this by changing the *k* value:

* k=3 we have 1 hit
* k=6 we have 1 hit
* k=7 we have 2 hits
* k=8 we have 3 hits

When setting *k*=3, OpenSearch first executes the neural query obtaining 3 documents: red, red, and **white**, and then it filters them by color keeping only the white one.  
The same for *k*=6 where we obtain: red, red, **white**, orange, blue, and green, with just one white document.  
And then for *k*=7 where we obtain: red, red, **white**, orange, blue, green, and **white**, with a total of 2 hits.

Even if in the k-NN search plugin also pre-filtering is available, in the neural plugin this is not yet.  
In fact, if you try to add a [filter parameter](https://opensearch.org/docs/2.4/search-plugins/knn/filter-search-knn/#step-3-search-your-data-with-a-filter) in the neural query such as for the k-NN one you obtain the following error:

```
				
					{
  "error": {
    "root_cause": [
      {
        "type": "parsing_exception",
        "reason": "[neural] unknown token [START_OBJECT] after [filter]",
        "line": 12,
        "col": 27
      }
    ],
    "type": "parsing_exception",
    "reason": "[neural] unknown token [START_OBJECT] after [filter]",
    "line": 12,
    "col": 27
  },
  "status": 400
}
				
			
```

This is because there is no *filter* [parameter supported](https://opensearch.org/docs/2.4/neural-search-plugin/index/#neural-request-fields) at the moment in the neural query, only: *vector\_field*, *query\_text*, *model\_id*, *k*.

###### 6.3 Examples of neural results

Here are some examples of neural results by running some neural queries extracted from the MS MARCO passage ranking dataset. For simplicity, we returned only the *`general_text`* field and not the *knn\_vector* one.

**query\_text**: “define extreme”

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-12-08-alle-10.19.11.png?fit=800%2C193&ssl=1)

**query\_text**: “define intense”

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-12-08-alle-10.19.18.png?fit=800%2C201&ssl=1)

**query\_text**: “define extreme in medical field”

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-12-08-alle-10.19.24.png?fit=800%2C202&ssl=1)

As can be seen from the results, thanks to the use of language models, the documents returned are very close to the query executed, and the neural search seems to handle “synonyms” and similar contexts.

## Summary

The new OpenSearch Neural plugin brings the neural search a step forward, making it easy to manipulate language models, create text embeddings and execute k-NN queries. There is still some work that can be done in order to make the documentation less scattered but it is well-written, and the tool is valuable and easy to use.

In our experiment, the model loading time and indexing time were acceptable but an in-depth study should be done to analyze the plugin’s performance.

It would be nice if in the future also pre-filtering and highlighting capabilities would be integrated since they are not available at the moment. Only post-filtering is allowed.

## Need Help With This Topic?​​

If you’re struggling with the OpenSearch Neural Search plugin, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with the OpenSearch Neural Search plugin, don't worry - we're here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)