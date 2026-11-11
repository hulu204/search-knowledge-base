---
title: 'Find and Replace in Elasticsearch Fields'
company: Sease
tag: 工程相关
date: 2024-03-01
url: https://sease.io/2024/03/find-and-replace-in-elasticsearch-fields.html
account: 
origin: harvest3-202607
---
Hi Elasticsearch users,

let’s dive into a common task in Elasticsearch: **updating field values across multiple documents in an index**, a common situation that many of us often encounter.  
Suppose we have an index, which for this example we call ‘**cartoons**‘. In this index, there is a field called ‘**`Title`**‘ which includes names of cartoons such as ‘**Tom & Jerry**‘, ‘**Mila & Shiro**‘, and so on.  
If the goal is to change the symbol **‘&’** into **‘and’,** thus obtaining for example **‘Tom and Jerry’**, how can this find and replacement task be tackled in Elastisearch?

**The good news is that Elasticsearch offers a painless way to update documents**.   
You can use the [Update By Query API](https://www.elastic.co/guide/en/elasticsearch/reference/8.11/docs-update-by-query.html), which allows you to update multiple documents based on a specific query. It is an efficient tool for those needing to make bulk changes to field values in their Elasticsearch index.

Here is a quick example to show you how this can be done:

##### Step 1: Create the Index

We create an index called ‘cartoons’, in which we define how documents should be stored and indexed. Here, we specify not to use dynamic mapping and set up a field called ‘`title`‘ of type ‘`text`‘:

```
				
					PUT /cartoons
{
  "mappings": {
    "dynamic": false,
    "properties": {
      "title": { "type": "text" }
   }
  }
}
				
			
```

##### STEP 2: INDEX SOME DOCUMENTS

This command allows multiple documents to be indexed in a single request to the ‘cartoons’ index. Each document is composed of a unique ID and the title:

```
				
					POST /cartoons/_bulk
{ "index" : { "_id" : "1" } }
{ "title" : "Tom &amp; Jerry" }
{ "index" : { "_id" : "2" } }
{ "title" : "Mila &amp; Shiro" }
{ "index" : { "_id" : "3" } }
{ "title" : "Hansel &amp; Gretel" }
				
			
```

For simplicity, we index only three documents to provide a suitable example for illustrative purposes.

##### STEP 3: Update Field Values - FIND AND REPLACE

This is the command to update documents in the ‘cartoons’ index using the **Update By Query API**:

```
				
					POST /cartoons/_update_by_query
{
    "script":
    {
        "lang": "painless",
        "source": "ctx._source.title = ctx._source.title.replace('&amp;', 'and')"
    }
}
				
			
```

In this case, no query is provided, and an update is performed on all documents within the index.   
Update by query supports `"script"` to update the document source and it uses the Painless scripting language to replace ‘&’ with ‘and’ in the title of each cartoon.

###### Handling Large Indexes with Asynchronous Execution

When dealing with large indexes or long update operations, to avoid the risk of getting a connection timeout and to allow for asynchronous execution of the operation, it is better to use the `wait_for_completion=false` parameter in the \_update\_by\_query API:

```
				
					POST /cartoons/_update_by_query?wait_for_completion=false
				
			
```

This way, the update operation continues to run in the background and the response will include a task ID that you can use to monitor the status of the operation using the Tasks API.

##### STEP 4: Query to Confirm Field Value Updates

To show the result after the update operation, we perform a “match all query” to match and retrieve all documents:

```
				
					GET cartoons/_search
{
  "query": {
    "match_all": {}
  }
}
				
			
```

This is the response:

```
				
					{
  ...
  "hits": {
    "total": {
      "value": 3,
      "relation": "eq"
    },
    "max_score": 1,
    "hits": [
      {
        "_index": "cartoons",
        "_id": "1",
        "_score": 1,
        "_source": {
          "title": "Tom and Jerry"
        }
      },
      {
        "_index": "cartoons",
        "_id": "2",
        "_score": 1,
        "_source": {
          "title": "Mila and Shiro"
        }
      },
      {
        "_index": "cartoons",
        "_id": "3",
        "_score": 1,
        "_source": {
          "title": "Hansel and Gretel"
        }
      }
    ]
  }
}
				
			
```

The response confirms that the update operation via the \_update\_by\_query API was successful and worked as expected. This is evident from the changed titles in the ‘cartoons’ index, where the ‘&’ symbol has been replaced with ‘and’.

From the ‘match all query’ query, it is clear that the \_source was changed, but was the re-indexing done automatically?  
Yes, the Update By Query API in Elasticsearch does both modify the source of the documents and reindex them. After you have performed an update using the Update By Query API, any subsequent searches will reflect these changes. So, if you update a document’s field from an old value to a new one, searching for the new value should return the updated document.  
Conversely, if you search for the previous term (the one that was present before the update), you will not find the updated documents. This is because the old term no longer exists in the indexed data of these documents.

###### Confirming Field Updates by Searching the New Value

To check this, we can perform a subsequent search using a match\_phrase query [[read more here](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query-phrase.html)]:

```
				
					GET cartoons/_search
{
  "query": {
    "match_phrase": {
      "title": "Tom and Jerry"
    }
  }
}
				
			
```

If we search “**Tom and Jerry**“, we will get one result:

```
				
					{
    ...
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 2.0951898,
        "hits": [
            {
                "_index": "cartoons",
                "_id": "1",
                "_score": 2.0951898,
                "_source": {
                    "title": "Tom and Jerry"
                }
            }
        ]
    }
}
				
			
```

If we search “Tom & Jerry”, no results will be returned:

```
				
					GET cartoons/_search
{
  "query": {
    "match_phrase": {
      "title": "Tom &amp; Jerry"
    }
  }
}
				
			
```

This is the response:

```
				
					{
    ...
    "hits": {
        "total": {
            "value": 0,
            "relation": "eq"
        },
        "max_score": null,
        "hits": []
    }
}
				
			
```

This process ensures that Elasticsearch’s search results are always synchronized with the current state of your data.

## Conclusions

The **Update By Query API** in Elasticsearch is a powerful, efficient way to modify multiple document fields. With it, you can **update field values for all documents** in an index based on a query.

See you for the next pills!

## Need Help with this topic?​

If you're struggling with Elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)