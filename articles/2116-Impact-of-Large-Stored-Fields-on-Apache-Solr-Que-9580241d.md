---
title: 'Impact of Large Stored Fields on Apache Solr Query Performance'
company: Sease
tag: 索引构建
date: 2022-12-13
url: https://sease.io/2022/12/impact-of-large-stored-fields-on-apache-solr-query-performance.html
account: 
origin: harvest3-202607
---
## Stored fields in Solr

In Solr, a field can be set as indexed and/or as stored.

```
				
					&lt;field name="field" type="text" indexed="true" stored="true" /&gt;
				
			
```

* **indexed**: if set to true, the field can be used for searching.
* **stored**: if set to true, the field value is also stored in solr. Here there are some usage examples:

1. retrieve the field value at query time
2. partial updates (will be introduced later on in the blog post)
3. highlighting

Having fields stored can be helpful in several scenarios. The downside is that their usage increases the index size and can affect the performance depending on how they are used.

In some cases, fields can be very long. Imagine an e-book: it could easily reach a considerable amount of Megabytes.

At indexing time, it’s possible to model and optimize the shape of the inverted index through the text analysis (e.g., stopwords filtering, synonym collapsing); also, remember the dictionary in the inverted index executes implicit deduplication of the ingested terms: if the input e-book contains 1000 times the term retrieval then the index will have just one entry.

However, all the above is valid only for indexed fields, fields whose content contributes to the inverted index.

###### What about stored fields?

A completely different behavior: stored fields are held verbatim in the persistent data structure: text compression plays a crucial role here, especially for long texts, but the point is: at data retrieval time, for a given stored field, the search engine must return the exact literal value inserted at the indexing time.

## A case study: huge stored field

The customer search infrastructure comprises a relational database and Solr 6.1.

As part of the incremental improvement path, a set of change requests require to enable the partial update [[1](https://solr.apache.org/guide/8_11/updating-parts-of-documents.html)] capability.

Partial updates allow to update of only a subset of fields in an already indexed solr document, without the necessity to submit the entire document.

The precondition for using such a feature is that all fields in the schema must be stored (stored=”true”) or docValues (docValues=”true”); the only exception is related to fields that are destinations of a copyField directive, and which must be set as stored=”false”.

For updating a document, solr has to delete the old version and index a new document with the updated information. With partial updates, solr is capable of using the information of the stored fields for indexing unchanged fields of a document. In this way, the user can send only the fields that have been updated (for instance metadata or something small). This will reduce drastically the amount of data to be transmitted by the user and the only price to pay is the increase of the index size.

##### Issue: query performance degradation

Query performance got much worse after setting all the fields as stored. We passed from an average query time of 10 milliseconds to 500 milliseconds.

At first sight, it appeared as a bizarre side-effect, even unrelated (we were thinking) to the just-enabled partial update feature: no indexing was happening behind, and slow queries had a very simple structure.

```
				
					q=something&amp;fl=id,first_name,surname,age,email_address
				
			
```

At query time, stored fields play a crucial role in the data retrieval phase, but as you can see from the query above, we asked just for a few of them. In addition, name, surname, and email address are fields whose average length is short.

Moreover, the fields declared to be returned were already stored before our change.

What happened then?

##### How fields retrieval work

After a deep investigation into the Solr internals, we found that query performance degradation was due to how Solr stored fields are retrieved.

Here’s the method that implements that retrieval logic:

```
				
					public void visitDocument(int docID, StoredFieldVisitor visitor) throws IOException {

    final SerializedDocument doc = document(docID);

    for (int fieldIDX = 0; fieldIDX &lt; doc.numStoredFields; fieldIDX++) {
      final long infoAndBits = doc.in.readVLong();
      final int fieldNumber = (int) (infoAndBits &gt;&gt;&gt; TYPE_BITS);
      final FieldInfo fieldInfo = fieldInfos.fieldInfo(fieldNumber);

      final int bits = (int) (infoAndBits &amp; TYPE_MASK);
      assert bits &lt;= NUMERIC_DOUBLE : "bits=" + Integer.toHexString(bits);

      switch (visitor.needsField(fieldInfo)) {
        case YES:
          readField(doc.in, visitor, fieldInfo, bits);
          break;
        case NO:
          if (fieldIDX == doc.numStoredFields - 1) { 
            return;
          }
          skipField(doc.in, bits);
          break;
        case STOP:
          return;
      }
    }
  }
				
			
```

The method iterates over **all** the stored fields; it **skips** the unwanted and **retains** only the fields the client asked for. When the cursor is on the last field, in case it hasn’t been requested, the process ends as no skip is required (remember, we are on the last field).

You can imagine the stored fields of a document as a long array where fields are encoded one next to the other. Each field provides some metadata in front (e.g., field info, length) that allows the visitor to read or skip it. If we want to get the field at position n, we must traverse all the fields from 0 to n-1 (reading or skipping them).

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/01/Untitled-Diagram.drawio.png?fit=561%2C81&ssl=1)

Reading a field value is more expensive than skipping it. However, skipping a field does not come for free. It is a constant time operation from the CPU point of view but things are different from the memory access perspective. When data is accessed sequentially, the CPU prefetches data in cache before actually reading it.

Trivial example: If block X is read, block X+1 is prefetched in cache because it is probable that after X is read X+1 will be required. Applying this concept to our situation of reading stored fields, traversing the stored fields by reading on skipping them is a fast operation because of the continuous prefetching of consecutive blocks. Every time the cursor moves to the next field, the data is already in the cache, and there is no delay in waiting that the data to be moved to the CPU cache.

Now, what happens if one of the fields is very large? (larger than one cache block). The prefetching mechanism is not able to understand which block to prefetch (the block belonging to the next field to read) and when the cursor gets there after a skip, the execution must be stopped for waiting for the right block to be loaded into the CPU cache. This causes a delay in the execution.

## SOLR 6.5 Optimization

**Solr 6.5** introduces an important optimization here ([SOLR-10273](https://issues.apache.org/jira/browse/SOLR-10273)).  
The optimization removes the overhead due to skipping a large field when it is not requested in the field list. The change consists in moving, at indexing time, the largest field at the end of the stored fields array.

**N.B**: all fields are read or skipped but the last one (if it is not needed). The last field does not require any skipping. For that reason, if the large field is the last one, there is no overhead because there’s no skipping at all.

Problem solved? More or less.

##### More than one large field?

Although it is common to have at most one large field in a document, what happens if you have more than one of them? Unfortunately, this case is not managed by the optimization introduced in [SOLR-](http://solr-10273/)[10273](https://issues.apache.org/jira/browse/SOLR-10273).

If you have multiple large stored fields, you will have some degradation at query time. The only possible recommendation is to design the schema to avoid such a scenario using **docValues**.

Let’s get back to the method above: it is executed only if the client request at least one stored field.

For that reason, if the client asks **only fields** that are also **docValues**, Solr does not have access to the stored structure at all. As a consequence, the retrieval workflow above doesn’t apply.

Here are some references for docValues fields:

* [Apache Solr docValues guide](https://solr.apache.org/guide/8_9/docvalues.html)
* [DocValues vs Stored Fields, Apache Solr Features and Performance Smackdown](https://sease.io/2020/03/docvalues-vs-stored-fields-apache-solr-features-and-performance-smackdown.html)

## Need Help With This Topic?​​

If you’re struggling with large stored fields, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with large stored fields, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)