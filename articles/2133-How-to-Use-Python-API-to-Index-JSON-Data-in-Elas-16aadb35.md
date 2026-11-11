---
title: 'How to Use Python API to Index JSON Data in Elasticsearch'
company: Sease
tag: 工程相关
date: 2023-09-06
url: https://sease.io/2023/09/how-to-use-python-api-to-index-json-data-in-elasticsearch.html
account: 
origin: harvest3-202607
---
Hi readers and Elasticsearch users,

when approaching a modern REST API REST-based search server like Elasticsearch, one of the most common use cases is to use data in JSON format, and the basic requirement is to find a way to index it into Elasticsearch effectively.

In this post, **we will explore how to achieve this task using the official Elasticsearch Python API, called [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/en/latest/index.html).**

The Python Elasticsearch Client is a library that provides a convenient way to communicate and interact with Elasticsearch using Python programming language. It allows us to perform key operations such as **indexing, querying, updating, and deleting JSON documents, managing indices**, and more.

Specifically, thanks to [Bulk Helpers](https://elasticsearch-py.readthedocs.io/en/latest/helpers.html#bulk-helpers)—a module that provides an easy way to perform bulk indexing or updating of documents in an Elasticsearch index, we are able to **enhance the indexing performance by sending multiple indexing (or update) requests** to Elasticsearch in a single HTTP request.

## Prerequisites

To index JSON data in Elasticsearch using Python, the prerequisites are as follows:

– **Python**   
you can install the latest version for your platform from [here](https://www.python.org/downloads/)  
– **Elasticsearch**  
make sure that Elasticsearch is correctly installed and running on your system [dowload from [here](https://www.elastic.co/downloads/elasticsearch)]  
– **[Elasticsearch Python client](https://elasticsearch-py.readthedocs.io/en/v8.5.3/)**:  
command to install the *elasticsearch* package:

```
				
					python3 -m pip install elasticsearch
				
			
```

## Example data

Let’s imagine a scenario where we have a JSON file, named **`documents_to_index.json`**, containing thousands of user interaction data from an e-commerce platform.  
Here is an example of the JSON structure representing a list of interactions, each having fields like **`productId`, `productPrice`, `productSales`, `interactionType`**, etc..:

```
				
					[
 { 
  "productId": "13408",
  "interactionType": "impression",
  "timestamp": "1690754400",
  "productPrice": "78.19",
  "productSales": "43",
  "userDevice": "mobile"
  }, 
  { 
   "productId": "30082",
   "interactionType": "click",
   "timestamp": "1690754401",
   "productPrice": "13.99",
   "productSales": "17",
   "userDevice": "desktop"
   }, 
   ... 
   ... 
   ]
				
			
```

Given the above example data this is the Elasticsearch index mapping you need to define:

```
				
					{
  "mappings": {
    "dynamic": false,
    "properties": {
      "interactionType": { "type": "keyword" },
      "productId": { "type": "keyword" },
      "productPrice": { "type": "scaled_float", "scaling_factor": 100 },
      "productSales": { "type": "integer" },
      "userDevice": { "type": "keyword" },
      "timestamp": { "type": "date", "format": "epoch_second" }
   }
  }
}
				
			
```

As you should already know, **index mapping defines how a document is stored and indexed**.  
It is essential because it helps Elasticsearch understand the data types, analyzers, and other properties of the fields within your documents.

## Don't Let Data Frustration Linger!

Elasticsearch’s complexity shouldn’t stand in the way of harnessing its power for your business success. Reach out to us now and unlock the true potential of Elasticsearch!

[Send an email](mailto:info@sease.io)

We can now use the following Python script (called, for example, ***indexer\_elastic.py***) to index the JSON data file in Elasticsearch:

```
				
					import sys
import time
import json
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# Elastic configuration.
ELASTIC_ADDRESS = "http://localhost:9200"
INDEX_NAME = "interactions_index"

def index_documents(documents_filename, index_name, es_client):
    index = 0
    # Open the file containing the JSON data to index.
    with open(documents_filename, "r") as json_file:
        json_data = json.load(json_file)
        documents = []
        for doc in json_data:
            doc["_id"] = index
            documents.append(doc)
            index = index + 1
        # How you'd index data to Elastic.
        indexing = bulk(es_client, documents, index=index_name, chunk_size=100)
        print("Success - %s , Failed - %s" % (indexing[0], len(indexing[1])))
 
def main():
    document_filename = sys.argv[1]

    # Declare a client instance of the Python Elasticsearch library.
    es_client = Elasticsearch(hosts=[ELASTIC_ADDRESS])
    
    initial_time = time.time()
    index_documents(document_filename, INDEX_NAME, es_client)
    print("Finished")
    finish_time = time.time()
    print('Documents indexed in {:f} seconds\n'.format(finish_time - initial_time))

if __name__ == "__main__":
    main()
				
			
```

We can execute the script with the following command (where we have passed the name of the Python script and the path of the JSON file):

```
				
					python3 indexer_elastic.py "path/to/documents_to_index.json"
				
			
```

This is the output after indexing the JSON file that contained 10,000 documents:

```
				
					Success - 100 , Failed - 0
Success - 100 , Failed - 0
.....
Success - 100 , Failed - 0
Finished
Documents indexed in 3.464257 seconds
				
			
```

##### How Bulk Indexing Works in Elasticsearch

We leveraged the Elasticsearch Python client to establish a connection, read data from a JSON file, and performed bulk indexing to efficiently store the data in Elasticsearch.

The insertion of the data into Elasticsearch is done by the [helpers.bulk](https://elasticsearch-py.readthedocs.io/en/latest/helpers.html#elasticsearch.helpers.bulk) method.  
The parameters accepted by the method are:  
– **client**: **`Elasticsearch`** instance to use  
– **actions**: iterator containing the actions, that would look something like this:

```
				
					documents = [
    {
    '_id': '1',
    'field_1': 'value_1',
    ...
},
    {
    '_id': '2',
    'field_1': 'value_1',
    ...
},
    ...
}
]
				
			
```

The action can be specified using the field **`_op_type`**; since the default value is ***index***, we can omit it and simply pass the list of documents as shown above. Otherwise, it accepts also ***create***, ***delete***, or ***update*** actions.

In our example code, we also assigned an integer “**`_id`**” value to each Elasticsearch document; this step is not mandatory but if you omit it, Elasticsearch will automatically generate a unique alpha-numeric \_id.

– **stats\_only**: default to False; you can set it to True if you only want to report the number of successful/failed operations instead of just the number of successful and a list of error responses.  
– **ignore\_status**: to specify a list of HTTP status codes that you want to ignore

helpers.bulk() is just a wrapper of another method called, [helpers.streaming\_bulk](https://elasticsearch-py.readthedocs.io/en/latest/helpers.html#elasticsearch.helpers.streaming_bulk) that accepts many more parameters. So if you want to use and pass any additional keyword arguments, the streaming\_bulk() method will be used to execute the operation.

##### Best Practices for Bulk Indexing

It is advisable to index data in Elasticsearch using the concept of “batches” (or “chunking”), and the helpers.bulk method is able to do this.  
“Batch” refers to a technique of dividing a larger data set into smaller, manageable portions for processing; in this context, using batches means splitting a collection of documents into smaller groups, or chunks, and then sending these chunks to Elasticsearch for indexing.  
Indexing large amounts of data in a single step could put stress on the cluster and cause performance problems, so splitting the data into smaller batches can help avoid overloaded situations.

Using the **`chunk_size`** parameter, you can specify the number of documents in a chunk sent to Elastic; the default is 500 and in our case, we have lowered the value to 100.

## Conclusion

We hope this guide has clarified how to use the Python API to index JSON data in Elasticsearch efficiently. By leveraging the **bulk indexing capabilities of the Elasticsearch Python Client**, you can scale your data ingestion process. If you have any questions or need further clarification, please feel free to leave a comment below.  
Happy coding, and see you in the next post!

## Need Help with this topic?​

If you're struggling with how to use python api to index json data in elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)