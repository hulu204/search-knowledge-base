---
title: 'Elasticsearch Neural Search Improvements in 8.6 and 8.7'
company: Sease
tag: 召回
date: 2023-05-16
url: https://sease.io/2023/05/elasticsearch-neural-search-improvements-in-8-6-and-8-7.html
account: 
origin: harvest3-202607
---
Hi readers!

We’ve already published two blogs about vector search with Elasticsearch, which are end-to-end tutorials (with real examples) using Elasticsearch version 8.5.3:

* [Elasticsearch Neural Search Tutorial](https://sease.io/2023/03/elasticsearch-neural-search-tutorial.html)
* [Elasticsearch Neural Search Tutorial (Platinum/Enterprise)](https://sease.io/2023/03/elasticsearch-neural-search-tutorial-platinum-enterprise.html)

(If you are not yet familiar with this topic and do not know how to approach a neural search with Elasticsearch, I suggest first reading these two blog posts).

In light of the recent release of version 8.7.1 (May 02, 2023), we would like to use this blog post to showcase the improvements that have been introduced in the latest versions (8.6 and 8.7).

If you’re considering an upgrade, this blog post can assist you in your decision by providing a summary of all the vector search enhancements.

Here is the link to [review all the changes made in each release.](https://www.elastic.co/guide/en/elasticsearch/reference/current/es-release-notes.html)

What follows **deals exclusively with the neural search aspect** and aims to supplement what has been already described in the previous blog posts.

## Elasticsearch New Features

##### 8.6

1) Support for indexing byte-sized knn vectors has been added. [PR #90774](https://github.com/elastic/elasticsearch/pull/90774)  
2) Field data and scripting support for byte-sized vectors have been added. [PR #91184](https://github.com/elastic/elasticsearch/pull/91184)

With the first Pull Request (PR #90774), **element\_type**, an optional mapping parameter for dense vector fields, was added.  
It refers to the data type used to encode vectors, which can be:  
– **float (default)**: 4-byte floating-point value per dimension  
– **byte**: 1-byte integer value per dimension (values between -128 to 127, inclusive)

Here is an example of mapping that has a dense vector field using the byte data type:

```
				
					{
  "mappings": {
    "properties": {
      "field_vector": {
        "type": "dense_vector",
        "dims": 384,
        "element_type": "byte",
        "index": true,
        "similarity": "dot_product",
      }
    }
  }
}
				
			
```

With the byte data type, it is possible to achieve a significantly smaller index size, leading to less memory usage, less disk space consumption, and a less complex HSNW graph to build. However, this comes at the cost of lower precision. The optimal choice depends on the nature of the data to be indexed.

The [second PR](https://github.com/elastic/elasticsearch/pull/91184) is just a follow-up of the first one, aimed at optimizing the previous work; we will not go into details, but if anyone is interested in learning more, the PR link is available for your reference.

## Elasticsearch Enhancements

##### 8.6

1) Profiling information for knn vector queries has been added. [PR #90200](https://github.com/elastic/elasticsearch/pull/90200)

Before 8.6, the search *profile* option does not measure the DFS (Distributed Frequency Search) phase, thus not reporting how much time is spent executing the ANN (Approximate Nearest Neighbors) search. This enhancement is beneficial as it adds the profiling capability by incorporating timers for the DFS phase, allowing for a detailed breakdown of several parts of the query. For more info, you can refer to the link above.

##### 8.7

The vector search functionality has been enhanced with two improvements:

1. Allows “null” values
2. Search multiple kNN fields

###### Allows “null” values

Issue: [#70470](https://github.com/elastic/elasticsearch/issues/70470)  
Pull request: [#93388](https://github.com/elastic/elasticsearch/pull/93388)

With versions prior to 8.7, when a document has a `null` vector value specified, the vector field will neither be parsed nor indexed.

For example, attempting to insert a document into a neural index (via the following \_bulk request API) with the dense\_vector field set to `null` will throw a **parsing exception**:

```
				
					curl http://localhost:9200/neural_index_with_NULL/_bulk -XPOST -H 'Content-Type: application/json' -d '
{"index": {"_id": "0"}}
{"general_text": "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.", "general_text_vector": null}'
				
			
```

```
				
					"type": "parsing_exception",
"reason": "Failed to parse object: expecting token of type [VALUE_NUMBER] but found [END_OBJECT]"
				
			
```

If `general_text_vector` is not the last field, as in this case:

```
				
					curl http://localhost:9200/neural_index_with_NULL/_bulk -XPOST -H 'Content-Type: application/json' -d '
{"index": {"_id": "0"}}
{"general_text": "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.", "general_text_vector": null, "color": "red"}'
				
			
```

the error will be:

```
				
					"type": "parsing_exception",
"reason": "Failed to parse object: expecting token of type [VALUE_NUMBER] but found [FIELD_NAME]"
				
			
```

**Starting from version 8.7, you can use `null` as a value for the dense\_vector field and this is the previous document once indexed:**

```
				
					{
"_index": "neural_index_with_NULL",
"_id": "0",
"_score": 1.0,
"_source": {
    "general_text": "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.",
     "general_text_vector": null
} 
				
			
```

This can also be useful for updating documents or deleting vector values from an indexed document when the vector for the document simply isn’t available or applicable anymore.

Keep in mind that this seems to be the only case handled; in fact, if you try to index a document with a dense\_vector field that has an empty array, as:

```
				
					"general_text_vector": []
				
			
```

you still encounter an exception:

```
				
					"type": "illegal_argument_exception", 
"reason": "The [dense_vector] field [general_text_vector] in doc [document with id '0'] has a different number of dimensions [0] than defined in the mapping [384]"
				
			
```

###### Search multiple kNN fields

Issue: [#91187](https://github.com/elastic/elasticsearch/issues/91187)  
Pull request: [#92118](https://github.com/elastic/elasticsearch/pull/92118)

Versions prior to 8.7 allow documents to have multiple *dense\_vector* fields, but it is not feasible to search them simultaneously in the same request, since the knn section of the search request only accepts one (vector) field.  
In fact, if you try to do an ANN (Approximate Nearest Neighbors) search over multiple fields, this error is raised:

```
				
					"type": "parsing_exception",
"reason": "Unknown key for a START_ARRAY in [knn]."
				
			
```

**With 8.7, it is now possible to use more than one KNN search clause per search request**.

###### EXAMPLE INDEX WITH TWO DENSE VECTOR FIELDS

Here is the curl command to create the index:

```
				
					curl http://localhost:9200/neural_index_two_fields/ -XPUT -H 'Content-Type: application/json' -d '{
"mappings": {
    "properties": {
        "general_text_vector": {
            "type": "dense_vector",
            "dims": 384,
            "index": true,
            "similarity": "cosine"
        },
        "second_text_vector": {
            "type": "dense_vector",
            "dims": 768,
            "index": true,
            "similarity": "cosine"
        },
        "general_text": {
            "type": "text"
        },
        "second_text": {
            "type": "text"
        }
    }
}}'
				
			
```

Note:  
In this example, we have assumed using two different pre-trained language models to convert data into vector values:  
– a model that maps sentences to a **384**-dimensional dense vector space for **`general_text_vector`** (e.g. [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2))  
– a model that maps sentences to a **768**-dimensional dense vector space for **`second_text_vector`** (e.g. [msmarco-distilbert-base-dot-prod-v3](https://huggingface.co/sentence-transformers/msmarco-distilbert-base-dot-prod-v3))

###### SEARCH MULTIPLE KNN FIELDS: Approximate kNN example

Here is an example request to search more than one kNN vector field at a time:

```
				
					curl http://localhost:9200/neural_index_two_fields/_search -XPOST -H 'Content-Type: application/json' -d '{
"knn": [{
    "field": "general_text_vector",
    "query_vector": [-9.01364535e-03, ..., ..., -1.16323479e-01], //384 dims
    "k": 3,
    "num_candidates": 10
},
{
    "field": "second_text_vector",
    "query_vector": [-8.35801288e-02, ..., ..., -3.83195356e-02], //768 dims
    "k": 5,
    "num_candidates": 20
}],
"_source": [
    "general_text",
    "second_text"
]}'
				
			
```

In the above example, each `knn` entry has:

* a different vector **field** to be searched again
* a different **query vector**, especially in terms of vector dimension, which must be the same as the vector field
* a different number of nearest neighbors (**k**) to return as top hits
* a different number of nearest neighbor candidates to consider per shard (**num\_candidates**)
* you can also specify a different **boost** value, to give weight to each score in the sum

Each section will be combined as a disjunction.

###### SEARCH MULTIPLE KNN FIELDS: Approximate kNN + match query example

Here is an example of *hybrid retrieval* in which more than one kNN vector field can be searched at a time:

```
				
					curl http://localhost:9200/neural_index/_search -XPOST -H 'Content-Type: application/json' -d '{
"query": {
    "match": {
        "general_text": {
            "query": "federal"
        }
    }
},
"knn": [{
    "field": "general_text_vector",
    "query_vector": [-9.01364535e-03, ..., ..., -1.16323479e-01], //384 dims
    "k": 3,
    "num_candidates": 10
},
{
    "field": "second_text_vector",
    "query_vector": [-8.35801288e-02, ..., ..., -3.83195356e-02], //768 dims
    "k": 5,
    "num_candidates": 20
}],
"size": 5,
"_source": [
    "general_text",
    "second_text"
]}'
				
			
```

The two knn entries and the query matches are combined through a disjunction.

**WHEN CAN THIS BE USEFUL?**

Searching across multiple KNN fields can help improve the quality of the search results.

Documents may have separate vector spaces, or a single document may be indexed with more than one vector space. In both scenarios, users may want to retrieve a resulting set that considers all indexed vector spaces.

So, especially when dealing with complex datasets that contain multiple types of embeddings, the search algorithm can take advantage of the strengths of each embedding type and provide a more comprehensive and relevant set of results to the user.

**A common example is searching for a semantic text embedding in combination with searching for an image embedding.**

However, it’s important to carefully consider the trade-offs between the benefits of searching across multiple fields and the computational costs involved, especially when dealing with large datasets.

## Elasticsearch Bug Fixes

##### 8.6

1) Enable cancellation of ANN searches, executed via the knn search section, when the overall search request is canceled. [PR #90612](https://github.com/elastic/elasticsearch/pull/90612)

##### 8.7

1) An issue with the **maxScore** calculation has been solved. [PR #93875](https://github.com/elastic/elasticsearch/pull/93875)  
2) The ‘**explain**‘ feature for kNN search matches `(explain: true)` was given strange results and has been improved. [PR #93876](https://github.com/elastic/elasticsearch/pull/93876)

## Summary

This blog post provides a summary of the **most recent improvements introduced in Elasticsearch** regarding vector search (specifically focusing on versions 8.6 and 8.7).

By combining the information from previously published blog posts, we aim to provide you with a **comprehensive and complete understanding of how vector search works and what can be achieved** (and what cannot).

## Need Help with this topic?​

If you're struggling with how vector search works in elasticsearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)