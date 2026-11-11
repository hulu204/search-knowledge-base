---
title: 'Elasticsearch Neural Search Tutorial (Platinum/Enterprise)'
company: Sease
tag: 召回
date: 2023-03-16
url: https://sease.io/2023/03/elasticsearch-neural-search-tutorial-platinum-enterprise.html
account: 
origin: harvest3-202607
---
As already mentioned in the blog post about [Neural search in Elasticsearch](https://sease.io/2023/03/elasticsearch-neural-search-tutorial.html), Elastic 8.0 allows users to use custom or third-party language models (developed in PyTorch) to perform inferences directly in Elasticsearch, but a Platinum or Enterprise subscription is required to experience the full Machine Learning features.

If you have the Basic (free and open) subscription, Elasticsearch gives you the ability to try natural language processing tasks for a limited time only (with a trial).

This blog post explains all the steps required to **implement Text Embedding and Vector Search directly in Elasticsearch** in a very simple way.

This tutorial uses **cURL commands** and the installation of Kibana is not mandatory.

## Neural Search Pipeline

The following is just a schematic drawing to easily show how Vector Search has been integrated within Elasticsearch:

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-12-26-alle-15.16.24.png?fit=800%2C257&ssl=1)

You have to perform your model development outside of Elastic and then you can easily import it; if you don’t want to worry about model training, Elasticsearch offers the possibility to import models off-the-shelf from public repositories (Hugging Face, PyTorch, etc.) with the help of the [Eland](https://pypi.org/project/eland/) library.  
You can ingest the corpus of data and apply the imported models on the fly to perform inference and vectorize the data.  
You can accept incoming queries (that are encoded by the model as well), and then use similarity measure (internally leveraging HNSW data structures) to rank and return the best search results and improve the user’s search experience.

After this brief description, here is the end-to-end pipeline to implement Neural Search within Elasticsearch:

1. [Download Elasticsearch](#download)
2. [Start a free trial](#start)
3. [Deploy a text embedding model](#deploy)
4. [Create an Elasticsearch index](#createindex)
5. [Create a text embedding ingest pipeline](#createtext)
6. [Index documents](#index)
7. [Search exploiting vector fields](#search)

Let’s start exploring each part!

##### 1. Download Elasticsearch

If you have read the first part of this post, you should have already installed Elasticsearch on your system. If not, please refer to the [downloading part](https://sease.io/wp-admin/post.php?post=55826&action=edit) of that tutorial.

##### 2. Start a free trial

In order to use the NLP features built into Elasticsearch (ES), you must have a Platinum or Enterprise license, otherwise, ES offers the ability to access (and explore) all subscription features with a [30-day free trial](https://www.elastic.co/guide/en/elasticsearch/reference/current/start-trial.html).

Here is the command to start the trial:

```
				
					curl -XPOST http://localhost:9200/_license/start_trial?acknowledge=true
				
			
```

###### RESPONSE

```
				
					{
	"acknowledged": true,
	"trial_was_started": true,
	"type": "trial"
}
				
			
```

##### 3. Deploy a text embedding model

An appropriately trained model must be [imported and deployed](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-deploy-models.html) to perform the text embedding task in your cluster.

As in other tutorials, we use a pre-trained model from Hugging Face, the language model called **[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)** (*BERT*) which maps sentences to a 384-dimensional dense vector space.

To import the model in ES, the **[Eland library](https://github.com/elastic/eland)** (Python client for machine learning in Elasticsearch) can be used.  
The first thing to do is open the terminal and install the Eland Python client (with PyTorch extra dependencies):

```
				
					python -m pip install 'eland[pytorch]'
				
			
```

Once installed, here is the command to run the `eland_import_hub_model` [script](https://github.com/elastic/eland/blob/main/bin/eland_import_hub_model):

###### REQUEST

```
				
					eland_import_hub_model --url http://localhost:9200/ --hub-model-id sentence-transformers/all-MiniLM-L6-v2 --task-type text_embedding --start
				
			
```

This script will copy a model from the Hugging Face model hub into an Elasticsearch cluster; in fact, we have defined:  
**`--url`:**URL for your Elasticsearch cluster **`--hub-model-id`:**the identifier for the Hugging Face model **`--task-type`:**type of NLP task, text embedding in our case **`--start`**: Elasticsearch will deploy the model to all available machine learning nodes and load the model into memory

###### RESPONSE

```
				
					INFO : Establishing connection to Elasticsearch
INFO : Connected to cluster named 'elasticsearch' (version: 8.5.3)
INFO : Loading HuggingFace transformer tokenizer and model 'sentence-transformers/all-MiniLM-L6-v2'
INFO : Creating model with id 'sentence-transformers__all-minilm-l6-v2'
INFO : Uploading model definition
100%|███████████████████████████████████████████████████████
█████████████████████████████████████████████████████| 22/22 [00:04&lt;00:00,  5.34 parts/s]
INFO : Uploading model vocabulary
INFO : Starting model deployment
INFO : Model successfully imported with id 'sentence-transformers__all-minilm-l6-v2'
				
			
```

From the response you can easily see that that the model was successfully imported but you can also check the model statistics using this API:

```
				
					curl -XGET http://localhost:9200/_ml/trained_models/_stats
				
			
```

###### RESPONSE

```
				
					{
	"count": 2,
	"trained_model_stats": [{
		"model_id": "lang_ident_model_1",
		"model_size_stats": {
			"model_size_bytes": 1053992,
			"required_native_memory_bytes": 0
		},
		"pipeline_count": 0
	}, {
		"model_id": "sentence-transformers__all-minilm-l6-v2",
		"model_size_stats": {
			"model_size_bytes": 90303761,
			"required_native_memory_bytes": 432265762
		},
		...,
				"routing_state": {
					"routing_state": "started"
				},
                                ...
			}]
		}
	}]
}
				
			
```

`lang_ident_model_1` is a built-in model (to perform language identification), already provided in the cluster.

For ease of reading, we reduced the response body of “our” model but if you are curious [here](https://www.elastic.co/guide/en/elasticsearch/reference/8.5/get-trained-models-stats.html) you can find more details.  
`"routing_state": "started"` means that the model is allocated and ready to accept inference requests.

##### ADDITIONAL REQUESTS:

To **START** a trained model deployment:

```
				
					curl -XPOST http://localhost:9200/_ml/trained_models/sentence-transformers__all-minilm-l6-v2/deployment/_start
				
			
```

To **STOP** a trained model deployment:

```
				
					curl -XPOST http://localhost:9200/_ml/trained_models/sentence-transformers__all-minilm-l6-v2/deployment/_stop
				
			
```

To **DELETE** a trained model:

```
				
					curl -XDELETE http://localhost:9200/_ml/trained_models/sentence-transformers__all-minilm-l6-v2
				
			
```

##### ALTERNATIVE WAY:

Another way to import a model in Elasticsearch with Eland is to use the following Python script (which you can also find in our [GitHub project](https://github.com/SeaseLtd/vector-search-elastic-tutorial/blob/main/nlp_models/import_model.py)):

```
				
					import elasticsearch
from pathlib import Path
from eland.ml.pytorch import PyTorchModel
from eland.ml.pytorch.transformers import TransformerModel

# Elastic configuration.
ELASTIC_ADDRESS = "http://localhost:9200"

def main():
        # Load a Hugging Face transformers model directly from the model hub
        tm = TransformerModel("sentence-transformers/all-MiniLM-L6-v2", "text_embedding")

        # Export the model in a TorchScript representation which Elasticsearch uses
        tmp_path = "models"
        Path(tmp_path).mkdir(parents=True, exist_ok=True)
        model_path, config, vocab_path = tm.save(tmp_path)

        # Import model into Elasticsearch
        client = elasticsearch.Elasticsearch(hosts=[ELASTIC_ADDRESS])
        ptm = PyTorchModel(client, tm.elasticsearch_model_id())
        ptm.import_model(model_path=model_path, config_path=None, vocab_path=vocab_path, config=config)

if __name__ == "__main__":
    main()
				
			
```

We execute the script with the following command:

```
				
					python import_model.py
				
			
```

Keep in mind that after this step, the model is imported into Elasticsearch, but you need to manually start the deployment in order to use it.

## 4. Create an Elasticsearch index

To create and define an explicit mapping for your destination index, the *index API* can be used; in this tutorial, the **neural\_index** is created:

```
				
					curl http://localhost:9200/neural_index -XPUT -H 'Content-Type: application/json' -d '
{
  "mappings": {
    "properties": {
      "general_text_vector.predicted_value": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
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

As defined in our mapping, documents consist of 3 simple fields:

1. the `general_text_vector.predicted_value` (*dense\_vector*) that will store the embeddings generated by the ingest pipeline
2. the document `general_text` (*text*), the source field with the text to transform into vectors
3. the **colour** (*text*), an additional field just used to show filter query behaviour

The explanation of the `dense_vector` field type parameters have already been addressed in the first blog post, so please refer to [Create an Elasticsearch index for vector search](https://sease.io/2023/03/elasticsearch-neural-search-tutorial.html) of that tutorial.

## 5. Create a text embedding ingest pipeline

It is possible to process the data and automatically create vectors from text within Elasticsearch, defining a text embedding [ingest pipeline](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-inference.html#ml-nlp-inference-processor).  
Using the following command you can create the **text-embeddings**pipeline:

```
				
					curl http://localhost:9200/_ingest/pipeline/text-embeddings -XPUT -H 'Content-Type: application/json' -d '
{
  "description": "Text embedding pipeline",
  "processors": [
    {
      "inference": {
        "model_id": "sentence-transformers__all-minilm-l6-v2",
        "target_field": "general_text_vector",
        "field_map": {
          "general_text": "text_field"
        }
      }
    }
  ],
  "on_failure": [
    {
      "set": {
        "description": "Index document to 'failed&lt;index&gt;'",
        "field": "_index",
        "value": "failed-{{{_index}}}"
      }
    },
    {
      "set": {
        "description": "Set error message",
        "field": "ingest.failure",
        "value": "{{_ingest.on_failure_message}}"
      }
    }
  ]
}'
				
			
```

The [inference processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-processor.html), which will add an embedding for each passage, has been specified with:  
**`model_id`**: the ID (or alias) of the trained model  
`target_field:` the field that will contain results objects (embeddings)  
**`field_map`**: defined to map `general_text` (where passages/documents are) to the field `text_field` that the model expects

We also added an additional parameter (`on_failure` handler) to handle exceptions and index failures into a different index, named `failed-neural_index`.

## 6. Index documents

Once we have created both the index and the ingest pipeline, we are ready to push some documents.

Here is the bulk indexing request, where the **`pipeline` query parameter** has to be specified in order to use our “text-embeddings” pipeline:

```
				
					curl http://localhost:9200/neural_index/_bulk?pipeline=text-embeddings -XPOST -H 'Content-Type: application/json' -d '
{"index": {"_id": "0"}}
{"general_text": "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.", "color": "red"}
'
				
			
```

[Here](https://github.com/SeaseLtd/vector-search-elastic-tutorial/blob/main/indexing_phase/create_body_for_bulk.py) you can find out how to automatically create the body of the bulk API request.

In the simple example above, only one document is indexed.  
As already suggested in the first tutorial, for indexing many documents the native bulk API can be problematic and very inefficient; we recommend using the [bulk helper](https://elasticsearch-py.readthedocs.io/en/v8.5.3/helpers.html) (Pyhton ES client) and with the following custom script, you can index batches of documents at once from a file and use an ingest pipeline to transform the data into vectors:

```
				
					import sys
import time
import random
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

BATCH_SIZE = 1000

# Elastic configuration.
ELASTIC_ADDRESS = "http://localhost:9200"
INDEX_NAME = "neural_index"
PIPELINE_NAME = "text-embeddings"

def index_documents(documents_filename, client):
    # Open the file containing text.
    with open(documents_filename, "r") as documents_file:
            documents = []
            # For each document creates a JSON document including text (and id).
            for index, document in enumerate(documents_file):
                # Generate color value randomly (additional feature to show FILTER query behaviour).
                color = random.choice(['red', 'green', 'white', 'black'])
                # Create the JSON document including index name and pipeline.
                doc = {
                    "_index": INDEX_NAME,
                    "pipeline": PIPELINE_NAME,
                    "_id": str(index),
                    "general_text": document,
                    "color": color,
                }
                # Append JSON document to a list.
                documents.append(doc)

                # To index batches of documents at a time.
                if index % BATCH_SIZE == 0 and index != 0:
                    # How you'd index data to Elastic.
                    indexing = bulk(client, documents)
                    documents = []
                    print("Success - %s , Failed - %s" % (indexing[0], len(indexing[1])))
            # To index the rest, when 'documents' list &lt; BATCH_SIZE.
            if documents:
                bulk(client, documents)
            print("Finished")

def main():
    document_filename = sys.argv[1]

    # Declare a client instance of the Python Elasticsearch library.
    client = Elasticsearch(hosts=[ELASTIC_ADDRESS])

    initial_time = time.time()
    index_documents(document_filename, client)
    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))

if __name__ == "__main__":
    main()
				
			
```

You can also find it in our [GitHub project](https://github.com/SeaseLtd/vector-search-elastic-tutorial/blob/main/indexing_phase/indexer_elastic_with_pipeline.py) and you can execute the script with the following command:

```
				
					python indexer_elastic_with_pipeline.py "../from_text_to_vectors/example_input/documents_10k.tsv"
				
			
```

###### REINDEX

If the data is already indexed, you can also pass the ‘`pipeline`‘ parameter in the reindex request:

```
				
					curl http://localhost:9200/_reindex -XPOST -H 'Content-Type: application/json' -d '
{
  "source": {
    "index": "general_index"
  },
  "dest": {
    "index": "neural_index",
    "pipeline": "text-embeddings"
  }
}'
				
			
```

All documents in the current index (*source*) are copied to a new index (*dest*) with a new mapping (previously created), and the Ingest pipeline feature is used to add an embedding for each document.

## 7. Search exploiting vector fields

The implicit generation of vector embeddings from query terms during a search request is currently not supported.

Therefore, you can use the **\_infer API** of your model, to transform a query into vectors:

```
				
					curl http://localhost:9200/_ml/trained_models/sentence-transformers__all-minilm-l6-v2/deployment/_infer -XPOST -H 'Content-Type: application/json' -d '{
  "docs": {
    "text_field": "what is a bank transit number"
  }
}'
				
			
```

###### Response

```
				
					{"predicted_value":[-0.009013667702674866,-0.07266351580619812,-0.01738189533352852,..., -0.11632353067398071]}
				
			
```

For ease of reading, we have shortened the response by inserting dots.

After getting embedding as a dense vector for a textual query “what is a bank transit number”, you can copy and use the vector obtained in the kNN query.

##### Approximate kNN example

```
				
					curl http://localhost:9200/neural_index/_search -XPOST -H 'Content-Type: application/json' -d '{
"knn": {
    "field": "general_text_vector.predicted_value",
    "query_vector": [-9.01364535e-03, -7.26634488e-02, ..., -1.16323479e-01],
    "k": 3,
    "num_candidates": 10
},
"_source": [
    "general_text",
    "color"
]}'
				
			
```

For vector similarity search, please refer to the queries already described in the first blog post ([5. Search exploiting vector fields](https://sease.io/wp-admin/post.php?post=55826&action=edit)).  
The only difference is the value of the `field` property of `knn` object:

```
				
					"knn": { "field": "general_text_vector.predicted_value",
				
			
```

INSTEAD OF:

```
				
					"knn": {
    "field": "general_text_vector",
				
			
```

## Summary

We hope this tutorial helps you to understand how to implement Text Embedding and Vector Search directly in Elasticsearch, using cURL commands instead of the Kibana console.

This recent implementation offers the ability to integrate a custom model into Elasticsearch and create embeddings internally, which, compared to the functionality described in the first blog post, is undoubtedly faster and easier to manage, but unfortunately is not available for free.

## Need Help with this topic?​

If you're struggling with neural search in Elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)