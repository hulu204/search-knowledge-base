---
title: 'Elasticsearch Neural Search Tutorial'
company: Sease
tag: 召回
date: 2023-03-02
url: https://sease.io/2023/03/elasticsearch-neural-search-tutorial.html
account: 
origin: harvest3-202607
---
Hi readers!  
Here we are with a new episode to find out how Open source technologies approach text vectorization and vector-based search (also known as Neural Search because of the usage of the deep neural network to encode the vectors from text).  
We have already published three blog posts about:

* [OpenSearch Neural Search Plugin Tutorial: Indexing and Searching](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html)
* [Apache Solr Neural Search Tutorial: Indexing and Searching](https://sease.io/2023/01/apache-solr-neural-search-tutorial.html)
* [Vespa Neural Search Tutorial](https://sease.io/2023/02/vespa-neural-search-tutorial.html)

Now it is Elasticsearch’s turn!  
This blog post explores how Vector Search is managed in Elasticsearch, providing a detailed description of what is already available through an end-to-end tutorial.

## Elasticsearch Neural Search Pipeline

Vector-based search and NLP (natural language processing) capabilities are available from Elastic Version 8.0, released on February 2022.

The following is just a diagram to easily show how a vector search engine work; it involves:

* **transforming** the original entity, such as a song, an image, or some text **into a numeric representation** (vector embeddings)
* using **distance** metrics to represent the similarity**between vectors**
* **searching** for **related data** (of your query) using approximate nearing neighbor (ANN) algorithms

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/vector-search-diagram.png?fit=800%2C450&ssl=1) 

Vector search diagram (Source: <https://www.elastic.co/what-is/vector-search>)

Like Apache Solr, Elasticsearch also uses *Apache Lucene* internally as its search engine, so many of the low-level concepts, data structures, and algorithms apply equally to both.  
Even in this case, vector-based search is built on top of **Apache Lucene HNSW** (Hierarchical Navigable Small World graph), i.e. Native ANN (approximate nearest neighbor) from Lucene 9.

The end-to-end pipeline to implement Neural Search with Elasticsearch is:

1. Download Elasticsearch
2. Produce Vectors Externally
3. Create an Elasticsearch index for vector search
4. Index documents
5. Search exploiting vector fields

We’ll now describe each section in detail so that you can easily reproduce this tutorial.

Let’s start getting your hands dirty!

## 1. Download Elasticsearch

As already said Vector-Based Search was integrated with Elasticsearch 8.0 but in this tutorial, we use version 8.5.3, which you can download from:  
<https://www.elastic.co/downloads/past-releases#elasticsearch>

*Verify the integrity of the downloaded file, both the SHA and ASC keys.*

Since Elasticsearch is built using Java, you need to ensure the Java Development Kit (**JDK**) is installed in your system; if Java is already installed, check its version which must be **17 or higher**.

Extract the downloaded file to a location where you want to work with it, open the terminal from that folder and run Elasticsearch locally:

```
				
					bin/elasticsearch
				
			
```

When you start Elasticsearch for the first time, the security is automatically enabled (for more info [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/configuring-stack-security.html)).  
For simplicity, in this tutorial we disabled it by setting: `xpack.security.enabled: false` in the *elasticsearch.yml* (*/elasticsearch-8.5.3/config/*) and restarting the Elasticsearch node.

You can verify if Elasticsearch is correctly running by typing: `curl localhost:9200`

We are now ready to use Elasticsearch and interact with its REST APIs. This can be done through several tools:

* Command line (cURL), as shown in this tutorial
* Dev Tools Console in Kibana (downloading and enrolling Kibana as well)
* API platforms, such as Postman

## 2. Produce Vectors Externally

Elastic 8.0 allows users to use custom or third-party language models developed in PyTorch to perform inferences directly in Elasticsearch, but a Platinum or Enterprise subscription is required to experience the full Machine Learning features.

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/elasticsearch-neural-search.jpg?fit=800%2C397&ssl=1)

Elastic Stack subscriptions: <https://www.elastic.co/subscriptions>

If you are curious to explore this powerful NLP feature, check out the blog post about [Neural Search in Elasticsearch Platinum/Enterprise](https://sease.io/2023/03/elasticsearch-neural-search-tutorial-platinum-enterprise.html), which explains all the steps for the enterprise version straightforwardly.

Otherwise, if you have the Basic license, to run a kNN search you have to **convert your data into meaningful vector values *outside* of Elasticsearch** and add them to documents as *dense\_vector* field values.

We used a Python project to transform text into the corresponding vectors that you can easily clone and explore from our [GitHub](https://github.com/SeaseLtd/vector-search-elastic-tutorial) page.

Here is the [Python script to run](https://github.com/SeaseLtd/vector-search-elastic-tutorial/blob/main/from_text_to_vectors/batch-sentence-transformers.py) to create vector embeddings from a corpus automatically:

```
				
					from sentence_transformers import SentenceTransformer
import torch
import sys
from itertools import islice
import time

BATCH_SIZE = 100
INFO_UPDATE_FACTOR = 1
MODEL_NAME = 'all-MiniLM-L6-v2'

# Load or create a SentenceTransformer model.
model = SentenceTransformer(MODEL_NAME)
# Get device like 'cuda'/'cpu' that should be used for computation.
if torch.cuda.is_available():
    model = model.to(torch.device("cuda"))
print(model.device)

def batch_encode_to_vectors(input_filename, output_filename):
    # Open the file containing text.
    with open(input_filename, 'r') as documents_file:
        # Open the file in which the vectors will be saved.
        with open(output_filename, 'w+') as out:
            processed = 0
            # Processing 100 documents at a time.
            for n_lines in iter(lambda: tuple(islice(documents_file, BATCH_SIZE)), ()):
                processed += 1
                if processed % INFO_UPDATE_FACTOR == 0:
                    print("Processed {} batch of documents".format(processed))
                # Create sentence embedding
                vectors = encode(n_lines)
                # Write each vector into the output file.
                for v in vectors:
                    out.write(','.join([str(i) for i in v]))
                    out.write('\n')

def encode(documents):
    embeddings = model.encode(documents, show_progress_bar=True)
    print('Vector dimension: ' + str(len(embeddings[0])))
    return embeddings

def main():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    initial_time = time.time()
    batch_encode_to_vectors(input_filename, output_filename)
    finish_time = time.time()
    print('Vectors created in {:f} seconds\n'.format(finish_time - initial_time))

if __name__ == "__main__":
    main()
				
			
```

We execute the script with the following command:

```
				
					python batch-sentence-transformers.py "./example_input/documents_10k.tsv" "./example_output/vector_documents_10k.tsv"
				
			
```

###### Response

```
				
					Processed 1 batch of documents
Batches: 100%|██████████| 4/4 [00:04&lt;00:00,  1.08s/it]
Vector dimension: 384
...
...
Processed 100 batch of documents
Batches: 100%|██████████| 4/4 [00:02&lt;00:00,  1.35it/s]
Vector dimension: 384
Vectors created in 402.041406 seconds
				
			
```

[SentenceTransformers](https://www.sbert.net/index.html) is a Python framework that you can use to compute sentence/text embeddings; it offers a large collection of [pre-trained models](https://www.sbert.net/docs/pretrained_models.html) tuned for various tasks.  
In this case, we use **[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)** (*BERT*) which maps sentences to a 384-dimensional dense vector space.

For this tutorial, we downloaded the [passage retrieval collection](https://microsoft.github.io/msmarco/Datasets.html#:~:text=Collection-,collection.tar.gz,-2.9%20GB) from [MS MARCO](https://microsoft.github.io/msmarco/) (a collection of large-scale information retrieval datasets for deep learning) and indexed roughly 10k documents of it.

The python script takes as input a file containing 10k documents (i.e. a small part of the MS MARCO passage retrieval collection):  
**sys.argv[1] = *“/path/to/documents\_10k.tsv”***  
*e.g. 1 document*

```
				
					The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.
				
			
```

It will output a file containing the corresponding vectors:  
**sys.argv[2] = *“/path/to/vector\_documents\_10k.tsv”***  
*e.g. 1 document*.

```
				
					0.0367823,0.072423555,0.04770486,0.034890372,0.061810732,
0.002282318,0.05258357,0.013747136,...,0.0054274425
				
			
```

For ease of reading, we reduced the length of the vector by inserting dots in the response.

Then, it is necessary to manually load the obtained embeddings into Elasticsearch (we will see this in the section on Indexing documents).

## 3. Create an Elasticsearch index for vector search

After installing and starting Elasticsearch, we are ready to create an**index**, using *explicit mapping* that allows us to precisely choose how to define the data.

Here is the API to create our ‘***neural\_index***‘:

```
				
					curl http://localhost:9200/neural_index/ -XPUT -H 'Content-Type: application/json' -d '{
"mappings": {
    "properties": {
        "general_text_vector": {
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
}}'
				
			
```

To check the index creation, here is the API to return information about it:

```
				
					curl -XGET http://localhost:9200/neural_index
				
			
```

As defined in our mapping, documents consist of 3 simple fields:

1. the **`general_text_vector`** that stores the embeddings generated by the Python script seen in the earlier section
2. the document `text`, the source field with the text to transform into vectors
3. the **colour**, an additional field just used to show filter query behaviour (we will see it in the searching part)

The last two fields are defined as *text* (field data type), while the first one is defined to be a *dense vector field*.

Elasticsearch currently supports storing vectors (of float values) through the `dense_vector` field type and using them to calculate document scores.  
In this case, we have defined it with:

* **dims**: (integer) the dimension of the dense vector to pass in, which needs to be equal to the model dimension. In this case *384*.
* **index**: (boolean) defaults to false, but you have to enable it `("index":true`) to search vector fields using the kNN search API.
* **similarity**: (string) the vector similarity function used to return the top K most similar vectors. In this case, we selected *cosine* (instead of *l2\_norm* or *dot\_product*). It is required only if `index` is `true`.

We left the **`index_options`** with default values; this section configuresadvanced parameters, closely related to the current algorithm (HNSW), that affect the way the graph is built at index time.  
You can find more information about dense vector parameters in the Elasticsearch [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.5/dense-vector.html#dense-vector-params).

##### CURRENT LIMITATION:

* The cardinality of the vector is currently limited to **1024** for indexed vectors (`"index":true`) and to 2048 for non-indexed vectors
* `dense_vector` type does not support:
  + sorting or aggregations
  + multi-valued
  + indexing vector if within `nested` mappings

## 4. Index documents

Once we have created both the vector embeddings and the index, we are ready to push some documents.

This is the *[\_bulk](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html)* request API you can use to push documents into your neural index.  
e.g. using one document:

```
				
					curl http://localhost:9200/neural_index/_bulk -XPOST -H 'Content-Type: application/json' -d '
{"index": {"_id": "0"}}
{"general_text": "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.", "general_text_vector": [0.0367823, 0.072423555, ..., 0.0054274425], "color": "black"}'
				
			
```

For ease of reading, we reduced the length of the vector by inserting dots in the request.  
[Here](https://github.com/SeaseLtd/vector-search-elastic-tutorial/blob/main/indexing_phase/create_body_for_bulk.py) you can find out how to automatically create the body of the bulk API request.

Precisely because vector embeddings are very long, for indexing many documents we recommend using another method, i.e. [elasticsearch](https://elasticsearch-py.readthedocs.io/en/v8.5.3/), the official Python client for Elasticsearch.  
Here is [the custom Python script we used](https://github.com/SeaseLtd/vector-search-elastic-tutorial/blob/main/indexing_phase/indexer_elastic.py) to index batches of documents at once:

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

def index_documents(documents_filename, embedding_filename, index_name, client):
    # Open the file containing text.
    with open(documents_filename, "r") as documents_file:
        # Open the file containing vectors.
        with open(embedding_filename, "r") as vectors_file:
            documents = []
            # For each document creates a JSON document including both text and related vector.
            for index, (document, vector_string) in enumerate(zip(documents_file, vectors_file)):

                vector = [float(w) for w in vector_string.split(",")]
                # Generate color value randomly (additional feature to show FILTER query behaviour).
                color = random.choice(['red', 'green', 'white', 'black'])

                doc = {
                    "_id": str(index),
                    "general_text": document,
                    "general_text_vector": vector,
                    "color": color,
                }
                # Append JSON document to a list.
                documents.append(doc)

                # To index batches of documents at a time.
                if index % BATCH_SIZE == 0 and index != 0:
                    # How you'd index data to Elastic.
                    indexing = bulk(client, documents, index=index_name)
                    documents = []
                    print("Success - %s , Failed - %s" % (indexing[0], len(indexing[1])))
            # To index the rest, when 'documents' list &lt; BATCH_SIZE.
            if documents:
                bulk(client, documents, index=index_name)
            print("Finished")

def main():
    document_filename = sys.argv[1]
    embedding_filename = sys.argv[2]
    
    # Declare a client instance of the Python Elasticsearch library.
    client = Elasticsearch(hosts=[ELASTIC_ADDRESS])
   
    initial_time = time.time()
    index_documents(document_filename, embedding_filename, INDEX_NAME, client)
    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))

if __name__ == "__main__":
    main()
				
			
```

We execute the script with the following command:

```
				
					python indexer_elastic.py "../from_text_to_vectors/example_input/documents_10k.tsv" "../from_text_to_vectors/example_output/vector_documents_10k.tsv"
				
			
```

###### Response

```
				
					Success - 1001 , Failed - 0
Success - 1000 , Failed - 0
...
Finished
Documents indexed in 19.828323 seconds
				
			
```

The python script will take in input 2 files, the one containing text and the one containing the corresponding vectors:  
**sys.argv[1] = *“/path/to/documents\_10k.tsv“***  
**sys.argv[2] = *“/path/to/vector\_documents\_10k.tsv“***

For each element of both files, the script creates a single JSON document (including the id, the text, the vector, and the color) and adds it to a list; when the list reaches the BATCH\_SIZE set, the JSON documents will be pushed to Elasticsearch.  
E.g. JSON:

```
				
					{'_id': '0', 'general_text': 'The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.\n', 'general_text_vector': [0.0367823, 0.072423555, 0.04770486, 0.034890372, 0.061810732, 0.002282318, 0.05258357, 0.013747136, -0.0060595, 0.020382827, 0.022016432, 0.017639274, ..., 0.0054274425], 'color': 'black'}
				
			
```

After this step, 10 thousand documents have been indexed in Elasticsearch and we are ready to retrieve them based on a query.  
To check the document count, you can use the cat indices API that shows high-level information for each index in a cluster:

```
				
					curl -XGET http://localhost:9200/_cat/indices
				
			
```

OR

```
				
					curl -XGET http://localhost:9200/_cat/count/neural_index?v
				
			
```

## 5. Search exploiting vector fields

Dense vector fields can be used in the following ways:

* **Exact, brute-force kNN**: using the [script\_score](https://www.elastic.co/guide/en/elasticsearch/reference/8.5/query-dsl-script-score-query.html) query
* **Approximate kNN**: using the [`knn` option](https://www.elastic.co/guide/en/elasticsearch/reference/8.5/search-search.html#search-api-knn) in the search API, to find the *k* most similar vectors to a query vector

To make some queries, we downloaded the passage retrieval queries from MS Marco: [queries.tar.gz](https://msmarco.blob.core.windows.net/msmarcoranking/queries.tar.gz)

The query reported in the following examples is: `"what is a bank transit number"`.  
To transform it into vectors, we run a custom python script:

```
				
					from sentence_transformers import SentenceTransformer

# The sentence we like to encode.
sentences = ["what is a bank transit number"]

# Load or create a SentenceTransformer model.
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Compute sentence embeddings.
embeddings = model.encode(sentences)

# Create a list object, comma separated.
vector_embeddings = list(embeddings)
print(vector_embeddings)
				
			
```

Let’s execute the script with the following command:

```
				
					python single-sentence-transformers.py
				
			
```

The output is an array of floats:

```
				
					[array([-9.01364535e-03, -7.26634488e-02, -1.73818860e-02, ..., ..., -1.16323479e-01],dtype=float32)]
				
			
```

You can now copy and use the vector obtained in the kNN query.  
The following are several examples of neural search queries in Elasticsearch:

##### Exact kNN

Running a *script\_score* query containing a vector function, it is possible to calculate the similarity of a query vector to every vector in the index, ranked by the *script\_score*.

###### REQUEST

```
				
					curl http://localhost:9200/neural_index/_search -XPOST -H 'Content-Type: application/json' -d '{
"query": {
    "script_score": {
        "query" : {
            "match_all": {}
        },
        "script": {
            "source": "cosineSimilarity(params.queryVector, '\''general_text_vector'\'') + 1.0",
            "params": {
                "queryVector": [-9.01364535e-03, -7.26634488e-02, ..., -1.16323479e-01]
            }
        }
    }
}}'
				
			
```

In this case, we used a `match_all` query to match all documents, but unless you are working with very small indices this query is not really scalable and can significantly increase search latency.  
If you want to use this query with large datasets, it is advisable to specify a filter query in the *script\_score* to limit the number of matched documents passed to the vector function.

##### Approximate kNN

Why Approximate? Because Elasticsearch uses an approximate method to perform kNN search, (i.e. HNSW), which sacrifices result accuracy to improve search speed and reduce computational complexity (especially on large datasets); therefore search results may not always be the true k neighbors.

###### REQUEST

```
				
					curl http://localhost:9200/neural_index/_search -XPOST -H 'Content-Type: application/json' -d '{
"knn": {
    "field": "general_text_vector",
    "query_vector": [-9.01364535e-03, -7.26634488e-02, ..., -1.16323479e-01],
    "k": 3,
    "num_candidates": 10
},
"_source": [
    "general_text",
    "color"
]}'
				
			
```

ANN (approximate nearest neighbour) is integrated into the `_search` API, adding the `knn` option in the request body. The defined properties of the `knn` object are:

* **field**: (string) field where vector embeddings are stored
* **query\_vector**: (array of floats) a list of floats values between square brackets representing the query; must have the same dimension of the vector field (i.e. 384)
* **k**: (integer) the number of nearest neighbours you want to retrieve; must be less than `num_candidates`
* **num\_candidates**: (integer) number of approximate nearest neighbour candidates to consider per shard (<= 10000); increasing this number improves accuracy, but slows down search speeds

```
				
					{
    ...,
    "hits": {
        "total": {
	    "value": 3,
	    "relation": "eq"
	},
	"max_score": 0.69120896,
	"hits": [{
	    "_index": "neural_index",
	    "_id": "7686",
	    "_score": 0.69120896,
	    "_source": {
	        "color": "green",
		"general_text": "A. A federal tax identification number ... of business.\n"
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "7691",
	    "_score": 0.6840044,
	    "_source": {
	        "color": "white",
		"general_text": "A. A federal tax identification number ... by the IRS.\n"
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "7692",
	    "_score": 0.6787193,
	    "_source": {
	        "color": "white",
		"general_text": "Let's start at the beginning. A tax ID number ... for a person.\n"
	    }
	}]
    }
}
				
			
```

Having set *topK=3*, we got the best three documents for the query “*what is a bank transit number*“.

The search computes, for each shard, the similarity of `num_candidates` vectors to the query vector (determining the document [\_score](https://www.elastic.co/guide/en/elasticsearch/reference/8.5/search-search.html#search-api-response-body-score)), selects the `k` most similar results from each shard, and finally merges the results (from each shard) returning the global top k nearest neighbors.

##### Approximate kNN + Pre-Filtering

Elasticsearch supports Pre-Filtering from version 8.2.

The following request performs an approximate kNN search filtered by the `color` field:

###### Request

```
				
					curl http://localhost:9200/neural_index/_search -XPOST -H 'Content-Type: application/json' -d '{
"knn": {
    "field": "general_text_vector",
    "query_vector": [-9.01364535e-03, -7.26634488e-02, ..., -1.16323479e-01],
    "k": 3,
    "num_candidates": 10,
    "filter": {
        "term": {
            "color": "white"
        }
    }
},
"fields": ["color"],
"_source": false
}'
				
			
```

###### Response

```
				
					{
    ...,
    "hits": {
        "total": {
	    "value": 3,
	    "relation": "eq"
	},
	"max_score": 0.6840044,
	"hits": [{
	    "_index": "neural_index",
	    "_id": "7691",
	    "_score": 0.6840044,
	    "fields": {
	        "color": ["white"]
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "7692",
	    "_score": 0.6787193,
	    "fields": {
	        "color": ["white"]
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "7685",
	    "_score": 0.6716478,
	    "fields": {
	        "color": ["white"]
	    }
	}]
    }
}
				
			
```

Having set *topK=3*, we got the best three documents for the query “what is a bank transit number” **with the ‘white’ color.**

This query ensures that `k` matching documents are returned since the filter query is applied **during** the approximate kNN search and not after.

##### Approximate kNN + other features

From version 8.4 it is possible to perform hybrid searches as well.

In this request, both the `knn` option and a `query` are combined through a disjunction.

###### Request

```
				
					curl http://localhost:9200/neural_index/_search -XPOST -H 'Content-Type: application/json' -d '{
"query": {
    "match": {
        "general_text": {
            "query": "federal"
        }
    }
},
"knn": {
    "field": "general_text_vector",
    "query_vector": [-9.01364535e-03, -7.26634488e-02, ..., -1.16323479e-01],
    "k": 3,
    "num_candidates": 10
},
"size": 5,
"_source": [
    "general_text"
]
}'
				
			
```

###### Response

```
				
					{
    ...,
    "hits": {
        "total": {
	    "value": 143,
	    "relation": "eq"
	},
	"max_score": 7.4108567,
	"hits": [{
	    "_index": "neural_index",
	    "_id": "7555",
	    "_score": 7.4108567,
	    "_source": {
	        "general_text": "Filed under: OPM Disability Process | Tagged: appeal deadlines during the fers disability process, average time frame for fers disability retirement, civil service disability, federal disability law blog, federal disability process timelines, federal disability retirement application and process, federal disabled employees and the patience needed, ...\n"
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "8014",
	    "_score": 7.395675,
	    "_source": {
	        "general_text": "Federal law (5 U.S.C. 6103) establishes the public holidays listed in these pages for Federal employees. Please note that most Federal employees work on a Monday through Friday schedule.\n"
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "2659",
	    "_score": 7.235115,
	    "_source": {
	        "general_text": "The authority of the Federal Reserve Banks to issue notes comes from the Federal Reserve Act of 1913. Legally, they are liabilities of the Federal Reserve Banks and obligations of the United States government.\n"
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "3337",
	    "_score": 7.1420827,
	    "_source": {
	        "general_text": "Federal Employee Retirement System - FERS. DEFINITION of 'Federal Employee Retirement System - FERS'. A system that became effective in 1987 and replaced the Civil Service Retirement System (CSRS) as the primary retirement plan for U.S. federal civilian employees.\n"
	    }
	}, {
	    "_index": "neural_index",
	    "_id": "580",
	    "_score": 7.111601,
	    "_source": {
	        "general_text": "Federal Laws vs. State Laws. Federal laws, or statutes, are created by the United States Congress to safeguard the citizens of this country. Some criminal acts are federal offenses only and must be prosecuted in U.S. District Court.\n"
	    }
	}]
    }
}
				
			
```

This search:

* collects knn `num_candidates` (10) results from each shard
* finds the global top `k=3` vector matches
* combines them with the matches from the `match` query (`=federal`)
* finally returns the 5 (`size=5`) top-scoring results (even if in total we have 143 hits)

The score is calculated by summing both the `knn` and `query` scores and it is also possible to specify a boost value to give a different weight to each score.

The `knn` option can also be used with [`aggregations`](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations.html), i.e. to compute aggregations on the first `k` nearest documents instead of on all documents that match the search.

## Summary

We hope this tutorial helps you to understand how to use vector-based search in Elasticsearch.

There is still some work that can be done, such as supporting multi-valued and improving the reranking and the integration with BERT and transformers in general.  
In fact, this is a [GitHub open issue](https://github.com/elastic/elasticsearch/issues/84324) where they are conducting all the ANN search improvements (new features, enhancements, performance improvements, etc..).

If you are curious about Elastic Benchmarks for dense vectors, you can find some published results [here](https://elasticsearch-benchmarks.elastic.co/#tracks/dense_vector/nightly/default/30d).

## Need Help with this topic?​

If you're struggling with neural search in Elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)