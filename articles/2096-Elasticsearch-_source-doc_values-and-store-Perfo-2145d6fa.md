---
title: 'Elasticsearch _source, doc_values and store Performance'
company: Sease
tag: 工程相关
date: 2021-02-01
url: https://sease.io/2021/02/field-retrieval-performance-in-elasticsearch.html
account: 
origin: harvest3-202607
---
In this blog post, I want to explore what **possibilities Elasticsearch gives us for storing fields and retrieving them at query time from the performance point of view**. In fact, Lucene, the underlying library upon which Elasticsearch and Solr are built, provides two ways for storing and retrieving fields: stored fields and docvalues. In addition, Elasticsearch uses as default the \_source field, a big JSON that contains all the fields of the document that are given as input at index time.

Why Elasticsearch uses the \_source field as default and what is the difference from the performance point of view among all of these possibilities? Let’s find out!

## Stored and docvalues fields in lucene

When we index a document in Lucene, the information about the original fields that have been indexed is lost. Fields are analyzed, transformed and indexed accordingly with the schema configuration. Without any additional data structure, when we search for a document, we get the id of the searched document but not the original fields. To get this information, we need additional data structures. Lucene provides two possibilities for that: stored fields and docvalues.

##### STORED FIELDS

Stored fields have the purpose of storing the value of the fields (without any analysis) to retrieve them at query time.

##### DOCVALUES

Docvalues have been introduced to speed up operations such as faceting, sorting and grouping. Docvalues can also be used for returning field values at query time. The only constraint we have is that we cannot use them for text fields.

Stored fields and docvalues are implemented in the Lucene library and they can be used in both Solr and Elasticsearch.

I have written a blog post in which I compare the performance for field retrieval of stored fields and docvalues in Solr:

[DocValues VS Stored Fields: Apache Solr Features and Performance SmackDown](https://sease.io/2021/02/field-retrieval-performance-in-elasticsearch.html)

There you can find a more detailed description of stored fields and docvalues, their utilization and constraints.

## Field retrieval in elasticsearch

Stored fields and docvalues can be used in Elasticsearch if we explicitly define them in the mapping:

```
				
					"properties" : {
 "field": {
  "type": "keyword",
   "store": true,
  "doc_values" true
 }
}
				
			
```

By default, the store is set to false for each field. Instead, all the fields which support docvalues have them enabled by default.

Independently from stored and docvalues configurations, at query time the value of every field in documents hit by the query is returned. This happens because Elasticsearch uses another tool for field retrieval: the **elasticsearch** **\_source** field.

##### elasticsearch \_source FIELD

The source field is the JSON that is passed to Elasticsearch at index time. This field is set to true by default in Elasticsearch and can be disabled using the mappings in this way:

```
				
					"mappings": {
  "_source": {
   "enabled": false
  }
}
				
			
```

All the fields are returned by default at query time. You can even specify only a subset of fields that are in the source to be returned in the response. This is supposed to speed up the transfer of the response across the network.

Some fields can be excluded by the source field with a proper configuration:

```
				
					PUT logs
{
 "mappings": {
  "_source": {
   "excludes": [
    "meta.description",
     "meta.other.*"
   ]
  }
 }
}
				
			
```

Excluding fields from the source will reduce the disk space usage but the excluded fields will never return in the response.

Disabling the elasticsearch \_source field will make it impossible to update a document without reindexing that from scratch. In fact, in order to update a document we need to get the values of the fields from the old document. Logically, it should be feasible to take the value of the fields from the old document using stored fields or docvalues (and this is how the atomic updates work in Solr). However, this is not allowed in Elasticsearch because of a design decision and if you need to update your documents you are compelled to enable the \_source field in your Elasticsearch index configuration.

##### RETRIEVING FIELDS

In Elasticsearch you can enable or disable the \_source field and make a field stored and/or docvalue. But how do we retrieve the fields at query time?

By default, the whole source is returned if it is defined. You can avoid it and return only a subset of the source as follows:

```
				
					...
 "fields": ["field1", "field2"],
 "_source": false
...
				
			
```

However, if you don’t have the source field enabled and you want to return the fields from stored or from docvalues, you must tell it to Elasticsearch in another way. For each of the sources you use, you have to specify the field list in a different way:

```
				
					...
 "fields": ["sv1", "sv2",...],
 "docvalue_fields": ["dv1", "dv2",...],
 "stored_fields" : ["s1", "s2",...],
...
				
			
```

For example, if you have a field both stored and docvalue you can choose if you want to retrieve it from docvalues or stored fields. From the functional point of view, this is exactly the same, but your choice could impact the execution time of your query.

##### STORED FIELDS, DOCVALUES AND ELASTICSEARCH\_SOURCE INTERNAL REPRESENTATION

In this section, I just want to give a marginal overview for what regards the internals of stored fields, \_source field and docvalues in order to have some tools for understanding what the expectations in the performance of using these methods for fields retrieval are.

###### Stored fields internals

Stored fields are placed on the disk in a row manner: for each document, we have a row that contains all the stored fields consecutively.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/storedfields.png?fit=631%2C141&ssl=1)

Take as an example the image above. To access field3 of document x, we have to access the row of document x and skip all the fields that are stored before field3. Skipping a field requires getting its length. Skipping fields is not as expensive as reading them but this operation does not come for free.

###### Docvalues internals

Docvalues are stored in a column manner. The value of the same fields for different documents are stored all together consecutively in memory and it is possible to access a certain field for a certain document “almost” directly. Calculating the address of a wanted value is not a simple operation and it has a computational cost but we can imagine that, if we want only one field, is more efficient to use this kind of access.

###### ELASTICSEARCH \_SOURCE FIELD INTERNALS

What about the \_source instead? Well, as mentioned above, the source is a big field that contains a JSON with all the input given to Elasticsearch at index time. But, how this field is stored? Not surprisingly, Elasticsearch leverages a mechanism that is already implemented and provided by Lucene: stored fields. In particular, the \_source field is the first stored field in the row.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/sourcefield.jpg?fit=571%2C141&ssl=1)

The whole \_source must be read to use the information it contains. If we want to return all the fields of a document, this process is intuitively the fastest. On the other hand, reading this huge field can be a waste of computational power in case we need to return only a small subset of the information it contains.

## Benchmarking

For benchmarking the 3 types of fields, I created 3 different indexes in Elasticsearch. I have indexed 1 million documents taken from Wikipedia, and for each document, I indexed 100 string fields with 15 characters in three different approaches: in the first index I set the fields as stored and in the second one as docvalues. In both these indices, I disabled the source field. In the third index instead, I just left the source field enabled.

The document and query collections have been taken from [here](https://github.com/tantivy-search/search-benchmark-game). I used real collections to simulate a realistic scenario.

Execution details:

* CPU: AMD RYZEN 3600
* RAM: 32 GB

For each query, I requested the best 200 documents and I repeated the test varying the number of fields to be returned (among the 100 random string fields I have created) from 1 to 100.

This is the result of the benchmark:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/elastic-benachmarks.png?fit=640%2C480&ssl=1)

The results show exactly what we expected to see. **Docvalues are recommended if we need a few fields for each document**. On the other hand, the **\_source field is the best one when we want to return the whole document** and the usage of stored fields is the perfect tradeoff between the other two.

In the scenario of the benchmark I performed, **docvalues are almost twice as fast as \_source field** **if we want only one field**, and at the extreme opposite, if we want to return all the fields, the chart shows a speedup of almost 2x when we use the \_source field in place of docvalues.

Concluding, performance is not the only parameter we must take into account. As we briefly explained in this blog post, there are some limitations in using one method or another. It could be that you are forced to use one of the three because of some constraints of your use case. And even from the performance of view, we don’t have a clear winner.

If disk space is not a problem, **you can even mix the different approaches and set a field as stored and docvalue, and leave the source enabled**. At query time, Elasticsearch enables you to choose the list of fields you want and if you want them to be returned from \_source, stored or docvalues.

## Need Help With This Topic?​​

If you’re struggling with Elasticsearch \_source, Doc\_values or Store Performance, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Elasticsearch \_source, Doc\_values or Store Performance, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Elasticsearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)