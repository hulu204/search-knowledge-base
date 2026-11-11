---
title: 'Docvalues VS Stored Fields : Apache Solr Features and Performance SmackDown'
company: Sease
tag: 索引构建
date: 2020-03-25
url: https://sease.io/2020/03/docvalues-vs-stored-fields-apache-solr-features-and-performance-smackdown.html
account: 
origin: harvest3-202607
---
This blog post aims to give a better understanding of **DocValues** and **Stored** fields in Apache Solr for the operations where they can be used interchangeably.

Although **Stored** fields and **DocValues** have been created for different purposes, both can be used to **effectively persist values of the document fields, and then, retrieve them when needed**.

When you are defining your solr schema you might ask yourself if your fields should be defined as **DocValues**, **Stored** or both. To decide this, you need to understand what is the usage of your fields in your application from a functional point of view.  
If both approaches are compatible with your needs, you should understand how choosing one in place of the other will affect the performance and the space usage of your search engine.

Following, I’m giving some tools for analysing which method is the best choice and in which scenario.

## Stored fields

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/02/stored.png?fit=552%2C62&ssl=1)

The main usage of stored fields is to return field values at query time.  You can specify a field to be stored as follows:

```
				
					&lt;fieldname="name" type="string" stored="true"/&gt;
				
			
```

Stored fields are organised in rows. This means that, given a set of fields, for each document, the values of these fields are concatenated in a row. The rows are then stored sequentially on disk according to their Lucene doc id. Each row may have a different size depending on the number of fields defined for that document and data types (e.g. string or text fields have variable sizes). The pointers to each row are stored to allow fast access to them.

Let’s say you want to retrieve the field A from the document with Lucene id **lid**:

1. 1. Find the address to the row of **lid**.
   2. Read all the values in the rows until you reach the value of the field A.
   3. Return the field A value.

The second point is crucial here. Because we have a pointer only at the beginning of the row,  we have to read all the stored values in the row in the worst case. This implies that returning all the stored fields in a row should have more or less the same cost as returning only a subset. This is an important factor to take into account when we define our Solr schema.

##### Stored fields space occupancy

Understanding how much space stored fields will take is a difficult task. When data get compressed, some factors such as data redundancy and distribution play a fundamental role.

The compression happens by applying the LZ4 algorithm to the rows formed as described above. LZ4 is a very fast compression algorithm with a good but not optimal compression ratio. It is possible to specify two modes: **BEST\_COMPRESSION** and **BEST\_SPEED**. While **BEST\_SPEED**is the default option, to set **BEST\_COMPRESSION** you just need to enable it in solrconfig.xml as follows:

```
				
					&lt;codecFactory&gt;
  &lt;str name="compressionMode"&gt;BEST_COMPRESSION&lt;/str&gt;
&lt;/codecFactory&gt;
				
			
```

This option changes only some parameters of the LZ4 algorithm execution, worsening the performance and improving the compression ratio.  
The last thing to say about stored fields compression is that in the same row, we can find very heterogeneous data and this is not the best scenario for obtaining an optimal compression ratio.

## DocValues

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/02/docvalues-1.png?fit=452%2C63&ssl=1)

**DocValues** have been introduced for improving the performance of some operations that otherwise would be very expensive: **sorting**, **faceting** and **grouping.**If these operations are frequent and important in your search engine use case, you should take in consideration setting the involved fields as **DocValues**.

For enabling **DocValues**, just set the docValues property as follows:

```
				
					&lt;fieldname="name" type="string" docValues="true"/&gt;
				
			
```

**DocValues** can be used in place of stored fields for retrieving the fields value at query time, but they are serialised in a column fashion. There are 3 important differences in behaviour to take into consideration:

1. 1. Text fields cannot be set as **docvalues**. If your field has a text type and you want to return it, you are forced to set it as stored.
   2. **Multivalued fields** are returned using a **different** **order**: when you use stored fields, they are returned in the order they have been indexed (the holding data structure acts as a **List**). Instead, multivalued fields with docValues enabled internally use a **Set** (SORTED\_SET or SORTED\_NUMERIC depending on their type), a data structure which **pre-orders** its member and **removes duplicates**.
   3. If you want to return **docvalues** with fl=\*, you need to specify this in the field definition: **useDocValuesAsStored=”true”** (note this is the default value starting from schema version 1.6)

As anticipated, fields are serialised by column. So, take as an example a generic field A. For each document in the collection, we store consecutively the values of the field A according to the Lucene document id. Notice that in the case of some types (e.g. string), each value has a different size and it is not predictable how much space is required for each element.

Accessing the value of field A for a document X can be done as follows:

1. 1. Find the address of document X in the column of field A.
   2. Read the value and return it.

Finding the right address is a tricky operation because of two reasons:

* + The field could be empty for some documents
  + We don’t want to have a pointer for each **docvalue**, otherwise too much space would be used only for pointers.

However, because we can read directly the value of interest, we can imagine that reading only one field value using **docvalues** is more performant than using stored fields while reading more fields requires repeating the same procedure more times. Moreover, because the values are sparse in memory, reading more values will cause cache misses and this will degrade performance.

##### DocValues space occupancy

It is worth spending some words about space occupancy for **docvalues** without digging into details. Things here are a bit more complicated than for stored fields. Depending on the column, data are stored and compressed differently. So, a column with numeric data will be stored and compressed differently from a column of strings.

* + Data are stored in a column manner so homogenous data will be close to each other
  + Specialised compression is applied depending on the data type.

Because of these assertions, we can conclude that storing **docvalues** will result in more efficient space usage than using stored fields, occupying less space.

## docValues=true and stored=true: what happens?

One may be wondering: what happens in Solr at retrieval time when

1. 1. fl contains only stored values
   2. fl contains only docValues (stored=false)
   3. fl contains a mix of stored and docValues fields?

Being the two options **not exclusive**, in the first two cases above we assume we have one option enabled and the other disabled. With that assumption, cases 1 and 2 are easy because stored and docValues fields are two disjoint sets: in the first case Solr will use the stored values while in the second scenario will make use of the docValues structure.

The third case is a little bit tricky because, as said above, those two options could be both enabled (i.e. stored=”true” docValues=”true”). Here. we have to make a distinction before and after Solr 7 because of an optimisation that has been introduced.

More than the optimisation itself, the new *RetrieveFieldOptimizer* class in Solr 7 created a centralised point of responsibility where further enhancements could be implemented in the future.

Before Solr 7, for each *SolrDocument* instance to be returned in the results the *org.apache.solr.response.DocsStreamer* class, actually responsible for fetching fields values, executes a sequential scan of

* + stored fields (i.e. fields marked as “stored” regardless of their docValues settings)
  + docValues enabled fields

Here’s a snippet from that class:

```
				
					SolrDocument sdoc = null;
...
Document doc = docFetcher.doc(id, fnames);
sdoc = convertLuceneDocToSolrDoc(doc, rctx.getSearcher().getSchema()); 

// decorate the document with non-stored docValues fields
if (dvFieldsToReturn != null) {
  docFetcher.decorateDocValueFields(sdoc, id, dvFieldsToReturn);
}
				
			
```

The same code looks “similar” in Solr 7:

```
				
					if (optimizer.returnStoredFields()) {
  Document doc = docFetcher.doc(id, optimizer.getStoredFields());
  // make sure to use the schema from the searcher and not the request (cross-core)
  sdoc = convertLuceneDocToSolrDoc(doc, rctx.getSearcher().getSchema());
} else {
  // no need to get stored fields of the document, see SOLR-5968
  sdoc = new SolrDocument();
}

// decorate the document with non-stored docValues fields
if (optimizer.returnDVFields()) {
  docFetcher.decorateDocValueFields(sdoc, id, optimizer.getDvFields());
}
				
			
```

but as you can see it introduced a new optimizer (*RetrieveFieldsOptimizer)* that tries to do the most efficient thing possible. Specifically, if the fl contains **only** fields with the following options

* + multiValued=”false”
  + docValues=”true”

regardless if they are stored or not,  Solr will return the stored values from the docValues structure. However, If even one field is docValues=false Solr will fallback to the <7 behaviour, that is:

* + stored value for stored fields
  + docValues structure for docValues enabled fields

## Benchmarks

Now that we know our competitors (**Stored** VS **DocValues),** we can explore a performance smackdown**.**  
We created a Solr instance aiming to provide some numbers about the performance of **Stored** fields and **DocValues** for fields returning.

This benchmark is not meant to be complete. It is possible that in certain scenarios things behave differently.

We’ve created an index in this way: we’ve indexed 1 million documents taken from Wikipedia. For each document we’ve added:

* 100 random stored string fields of 15 characters each
* 100 random **DocValues** string fields of 15 characters each

The document and query collections have been taken from Quickwit Github [[1]](https://github.com/tantivy-search/search-benchmark-game). We used real collections to simulate a realistic scenario. Execution details:

* CPU: AMD RYZEN 3600
* RAM: 32 GB
* Index size: 9.07 GB

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/100.png?fit=640%2C480&ssl=1)

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/200.png?fit=640%2C480&ssl=1)

It is possible to notice that retrieving a high number of fields leads to a sensible worsening of performance if **DocValues** are used. Instead,  the (almost) surprising thing is that, by returning less than 20 fields, **DocValues** performs better than stored fields and the difference gets little as the number of fields returned increases. This is due to a better management of **DocValues** in main memory. Asking for 9 **DocValues** fields and 1 stored field takes an average query time is 6.86 (more than returning 10 stored fields). Furthermore, the charts above show that the query times increase linearly with the number of fields returned. This makes predictable the speedup of using the stored fields against **DocValues**.

In conclusion, the use of **DocValues** leads to several benefits from the performance point of view (faceting, sorting and grouping) and they can even speed up fields retrieval if only a few **DocValues** fields and no store fields are used. Moreover, **DocValues** are likely to use less space than stored fields. If the use case requires that a lot of fields need to be returned, using stored fields is the way to go.

The experiments can be replicated by using the Solr configuration and the Python scripts. The git repository includes only a small sample of data used for the benchmarks. [[2]](https://github.com/SeaseLtd/solr-field-retrieval-benchmark)

## Need Help With This Topic?​​

If you’re struggling with DocValue and Stored fields, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with DocValue and Stored fields, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)