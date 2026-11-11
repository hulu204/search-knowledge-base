---
title: 'Apache Solr ChildDocTransformerFactory: How to Build Complex ChildFilter Queries'
company: Sease
tag: 工程相关
date: 2019-06-04
url: https://sease.io/2019/06/apache-solr-childfilter-transformer.html
account: 
origin: harvest3-202607
---
When using nested documents and the Apache Solr Block Join functionality it is a common requirement to query for an entity (for example the parent entity) and then retrieve for each search result all (or some of) the related children.

Let’s see the most important aspects of such functionality and how to apply complex queries when retrieving children of search results.

## How to Index Nested Documents

If we are providing the documents in JSON format, the syntax is quite intuitive:

```
				
					{
      "id": "A",
      "queryGroup": "group1",
      "_childDocuments_": [
          {
             "metricScore": "0.86", 
             "metric": "p",
             "docType": "child",
             "id": 12894
           },
           {
              "metricScore": "0.62",
              "metric": "r",
              "docType": "child",
              "id": 12895
            }
         ],
         "docType": "parent",
...
				
			
```

The children documents are passed as an array of JSON nodes, each one with a specific Id  
**N.B.** If you rely on Apache Solr to assign the ID for you, using the UUIDUpdateProcessorFactory [[1]](https://lucene.apache.org/solr/8_0_0//solr-core/org/apache/solr/update/processor/UUIDUpdateProcessorFactory.html), this doesn’t work with child documents yet.  
In such a scenario, you should implement your Update Request Processor, which iterates over the children and assigns an id to each one of them (and then contribute it to the community 🙂 )

If you are using SolrJ and you plan to index and retrieve children documents via code, the situation is a little bit more difficult.  
First of all, let’s annotate the POJO properly:

```
				
					public class Parent
 {
         @Field
         private String id;
         ...

         @Field(child = true)
         private List&lt;Child&gt; children;
				
			
```

**N.B.** *Parent*, *Child* and *children* are just fantasy names, the important notation here is the SolrJ annotation **@Field(child = true)**, you can use whatever name you like for your POJO classes and variables

##### Index Nested Documents in SolrJ

At Indexing time you have 2 options, you can use the Document Binder:

```
				
					DocumentObjectBinder solrBinder = new DocumentObjectBinder();
Parent sampleParent = new Parent();
Child sampleChild = new Child();

SolrInputDocument parent = binder.toSolrInputDocument(sampleParent);
SolrInputDocument child = binder.toSolrInputDocument(sampleChild);
parent.addChildDocument(child);

solr.add("collection", parent)
				
			
```

Or you can use the plain POJO:

```
				
					Parent sampleParent = new Parent();
Child sampleChild = new Child();

//you need to implement it in your POJO
sampleParent.addChildDocument(sampleChild);

solr.addBean("collection", sampleParent)
				
			
```

## How to Query and Retrieve Nested Documents

Ok, we covered the indexing side, it’s not straightforward but at this point we should have nested documents in the index, nicely in adjacent blocks with the parent, to allow a fast retrieval at query time.  
First of all, let’s see how we can query parent/children and get an appropriate response.

##### Query Children and Retrieve Parents

```
				
					q={!parent which=&lt;allParents&gt;}&lt;someChildren&gt;

e.g.

q={!parent which=docType:"parent"}title:(child title terms)
				
			
```

**N.B.** *allParents* is a query that matches all the parents, if you want to filter some parents later on, you can use filter queries or some additional clause:

```
				
					e.g.
q= +title:join +{!parent which="content_type:parentDocument"}comments:SolrCloud
				
			
```

The child query must always return **only** child documents.

##### Query Parents and Retrieve Children

```
				
					q={!child of=&lt;allParents&gt;}&lt;someParents&gt;

e.g.

q={!child of="content_type:parentDocument"}title:lucene
				
			
```

**N.B.** The parameter **`allParents`** is a filter that matches **only parent documents**; here you would define the field and value that you used to identify **all parent documents**.  
The parameter **`someParents`** identifies a query that will match some of the parent documents. The output is the children.

##### How to Retrieve Children Independently of the Query

If you have a query that returns parents, independently if it was a Block Join Query or just a plain query, you may be interested in retrieving child documents as well.  
This is possible through the Child Transformer [[2]](https://lucene.apache.org/solr/guide/8_0/transforming-result-documents.html#child-childdoctransformerfactory).

###### [child] - ChildDocTransformerFactory

```
				
					fl=id,[child parentFilter=doc_type:book childFilter=doc_type:chapter]
				
			
```

When using this transformer, the **`parentFilter`** parameter must be specified *unless* the schema declares `_nest_path_`. It works the same as in all Block Join Queries. Additional optional parameters are:

**`childFilter`**: A query to filter which child documents should be included. This can be particularly useful when you have multiple levels of hierarchical documents. The default is all children. This query supports a special syntax to match nested doc patterns so long as **`_nest_path_`** is defined in the schema and the query contains a **`/`** preceding the first **`:`**. Example: **`childFilter=/comments/content:recipe`**

`limit`: The maximum number of child documents to be returned per parent document. The default is **`10`**

**`fl`**: The field list which the transformer is to return. The default is the top-level **`fl`**).  
There is a further limitation in which the fields here should be a subset of those specified by the top-level **`fl`** parameter.

###### Complex childFilter queries

Let’s focus on the ***childFilter*** query.  
This query must match only child documents.  
Then It can be as complex as you like to retrieve only a specific subset of child documents.  
Unfortunately is less intuitive than expected to pass complex queries here because by default **spaces will work against you**.

*… childFilter=field:(classic OR boolean AND query)]*

*… childFilter=field: I am a complex query]*

You can certainly try complex approaches in text analysis an debugging the parsed query, but I recommend to use **local params placeholders and substitution**, this will solve most of your issues:

```
				
					fl=id,[child parentFilter=doc_type:book childFilter=$childQuery limit=100]
&amp;childQuery=(field:(I am a complex child query OR boolean))
				
			
```

Using the placeholder substitution will solve the whitespace local params splitting problems and help you in formulating complex queries to retrieve only subsets of children documents out of parent results.

##### Retrieve Child Documents in SolrJ

Once you have a query that is returning child documents (and potentially also parents) let’s see how you can use it in SolrJ to get back the Java objects.

```
				
					DocumentObjectBinder solrBinder = new DocumentObjectBinder();
String fields="id,query," +
       "[child parentFilter=docType:parent childFilter=$childQuery]";
String childQuery = "childField:value";
final SolrQuery query = new SolrQuery(GET_ALL_PARENTS_QUERY);
query.add("metricFilter",metricFilter);
query.addFilterQuery("parentField:value");
...
query.setFields(fields);

QueryResponse children = solr.query("collection", query);
List&lt;Parent&gt; parents = binder.getBeans(Parent.class, children.getResults());
				
			
```

In this way, you’ll obtain the Parent objects that satisfy your query including all the requested fields and the nested children.

## Conclusion

Working with Nested Documents is extremely funny and can solve a lot of problems and tricky user requirements, but they are also not easy to master so I hope this blog can help you to navigate the rough sea of the Block Join and Nested Documents in Apache Solr!

## Need Help With This Topic?​​

If you’re struggling with nested documents, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with nested documents, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)