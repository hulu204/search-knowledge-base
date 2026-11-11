---
title: 'Colbert Comes to Apache Solr: Implementation and Tutorial of Late Interaction Model Reranking'
company: Sease
tag: 排序
date: 2026-04-01
url: https://sease.io/2026/04/late-interaction-comes-to-solr-implementation-and-tutorial.html
account: 
origin: harvest3-202607
---
Hi there!

In this blog post, I’m going to deep dive into the **implementation of the Late Interaction field support** in Solr 10.1 (introduced via [SOLR-17975](https://issues.apache.org/jira/browse/SOLR-17975)), which brings the power of Lucene 10.3’s **`LateInteractionField`** to Solr. This field type is specifically designed to contain multiple vectors for a single document, and therefore **enables the use of late interaction models for reranking**. I will then show a quick example on how to integrate **`LateInteractionField`** into Solr.

Before going forward, if you missed the first blog post about neural reranking with Late Interaction models like ColBERT, here is the [link](https://sease.io/2026/04/late-interaction-comes-to-solr-neural-reranking-introduction.html)! Let’s start now!

## Apache Solr and Lucene Implementation

Lucene leverages [`BinaryDocValues`](https://github.com/apache/lucene/blob/main/lucene/core/src/java/org/apache/lucene/document/BinaryDocValuesField.java) to implement `LateInteractionField`. This is used to serialise matrices (i.e, vectors of vectors) in a column fashion.

Lucene’s **`BinaryDocValues`** is a per-document columnar store that maps each document **`id`** to an arbitrary byte array. **`LateInteractionField`** exploits this by serialising an entire token-embedding matrix into a single contiguous `BytesRef` payload, which is then stored as **`BinaryDocValues`.**

The encoding layout is simple. The first 4 bytes hold an integer representation of the token vector dimension **`D`**, i.e. the number of floats in each token embedding. Every subsequent group of **`D × 4`** bytes is one token vector, stored as `float` values laid out sequentially with no separator or padding between them. The total payload size is therefore **`4 + (N × D × 4)`** bytes, where **`N`** is the number of token vectors in the document. The **`encode`** method is used to translate from **`float[][]`** to **`BytesRef`**, and, similarly, the method **`decode`** does the opposite. These methods are used by Lucene to translate **`LateInteractionField`** from and to the **`BinaryDocValues`** structure.

In this setup, once we have a set of candidate documents (e.g., coming from an initial lexical retrieval step), the system can fetch their associated embeddings directly using their internal document **`id`**. If you want to learn more about docValues, [this blog post](https://sease.io/2020/03/docvalues-vs-stored-fields-apache-solr-features-and-performance-smackdown.html) is a useful resource for a broader understanding of the topic. Another important consideration is that all vectors must have the same size.

The decision to use docValues is motivated by the documentation, which states:

> Across a large corpora, these "multi-vector" representations of the original semantic content are typically too large and unwieldy to index and search in navigable small-world graph in a useful manner. Instead "Late Interaction" approaches are typically used to compute vector similarities scores against a subset of documents, after an initial pass of other search techniques.

Since we don’t need to navigate the graph, we just need a way to store the vectors and compute scores.

At query time, Lucene checks whether the query vectors are compatible (i.e., have the same dimensionality) with the vectors stored in Lucene docValues. Afterwards, Lucene iterates over the docValues structure built at index time and, for each document, retrieves the value associated with the field defined as **`LateInteractionField`**. To compute the similarity score with the query, for each vector in the query, the maximum similarity is retained and added to an accumulator, which will be the final score at the end of the process (see [here](https://github.com/apache/lucene/blob/3ba9a0736636e976677c4c29c351945b23dfee6c/lucene/core/src/java/org/apache/lucene/search/LateInteractionFloatValuesSource.java#L156)). This complies with the MaxSim score computation described in the ColBERT [[1](https://arxiv.org/abs/2004.12832)] structure (see the [first blog post](https://sease.io/2027/03/late-interaction-comes-to-solr-neural-reranking-introduction.html) for more information).

The contribution [SOLR-17975](https://issues.apache.org/jira/browse/SOLR-17975) exposes this Lucene integration to Solr. Late interaction vectors can be stored using the new dedicated field type `StrFloatLateInteractionVectorField`, designed to hold token-level embeddings produced by models such as ColBERT. The field type specifies the vector dimensionality and the similarity function used for scoring. We will see later a practical example of how this can be done in Solr. As the name suggests, each document containing this field must be sent to Solr as a string. This is because Solr does not support list-of-list fields, which we would need here (see [SOLR-17974](https://issues.apache.org/jira/browse/SOLR-17974) for more information).

Three fundamental requirements are needed for these fields to work:

* **`docValues`** must be enabled
 * the field cannot be **`index`ed**
 * the field cannot be **`multivalued`**

Concerning **`docValues`**: starting from Solr schema version 1.7, they are enabled by default, and they are strictly required when working with **`StrFloatLateInteractionVectorField`**. Without docValues enabled, late interaction scoring cannot be executed (since Lucene’s **`LateInteractionField`** uses them to store and retrieve the vectors). The other two constraints are that the field must not be indexed and cannot be multivalued. The first constraint comes from the Solr side only. On the Lucene side, **`LateInteractionField`** extend **`BinaryDocValuesField`**, which stores data exclusively via docValues and has no text-indexing behaviour. Solr simply enforces this explicitly in the schema to prevent misuse. About multivalued, you might be scratching your head: if the whole point of Late Interaction is to store a list of vectors, why on earth are we setting multiValued=”false”? The answer lies in the distinction between logical data and input representation. While it’s true that your document contains a sequence of many vectors, Solr **StrFloatLateInteractionVectorField** expects these to be delivered as a single, serialised string (as we mentioned before). In the Solr schema, you aren’t providing a list of separate items; you are providing one block of data that represents the entire set of embeddings.

To wrap up the technical configuration of this feature, we need to examine how Solr interacts with these stored vectors during a query. Once your field is defined and populated, you need a way to trigger the scoring logic. To enable this, the contribution introduces a new function to be used with the function query parser called `lateVector`. This acts as the bridge between Solr and the MaxSim interaction logic from Lucene’s **`LateInteractionField`**. This addition is what makes the field truly functional in Solr. By exposing this as a standard function, you can incorporate late interaction scores directly into your reranking queries using the standard Solr function syntax (e.g., **`{!func}lateVector(my_late_vectors, ...)`**).

## Solr Late Interaction Example

##### Schema

Thanks to this new Solr contribution, using Late Interaction Models for reranking in the Solr search engine becomes straightforward. A minimal schema configuration looks like the following:

```
				
					&lt;fieldType name="late_vectors_type" class="solr.StrFloatLateInteractionVectorField" vectorDimension="4" similarityFunction="cosine"/&gt;
&lt;field name="late_vectors" type="late_vectors_type" docValues="true" stored="true"/&gt;
				
			
```

This configuration defines a field capable of storing token embeddings and computing similarity at query time, similarly to how it is done for `DenseVectorField`. The only difference is that, since **LateInteractionField** doesn’t need an index, you don’t need to add all the HNSW-related parameters. While Solr defaults to the dot product, which is computationally more efficient and identical to cosine similarity for normalised vectors, our case requires a different approach. Since our embeddings are not normalised, we use cosine similarity. Aside from these schema definitions, no additional changes to the default Solr configuration are necessary, which makes it very simple to integrate late interaction reranking into a search pipeline.

What about the three constraints mentioned before? Don’t worry! The default configuration is already set to respect these constraints, so you won’t need to manually override these attributes in your **`managed-schema`**. Solr handles these requirements under the hood, ensuring your field is correctly configured for Late Interaction without extra effort on your part, since it overwrites the default parameter for this field type.

##### Index Time

Following the documentation, an example of how you can index vectors is using the following JSON payload:

```
				
					[
  {
    "id": "1",
    "title": "Potato Chips",
    "late_vectors": "[[1.0, 2, 3.7, 4.1], [2.2, -2.5, 7.3, 4.0]]"
  },
  {
    "id": "2",
    "title": "Onion Chips",
    "late_vectors": "[[2.0, 5.6, -3.2, 1.4], [7.8, -2.5, 3.7, 0.0034], [-2.2, 5.5, 0.6, -0.030]]"  
  }
]
				
			
```

In the same way, it can be easily done through the SolrJ API in Java as follows:

```
				
					Http2SolrClient client = new Http2SolrClient.Builder(solrUrl).build();

final SolrInputDocument d1 = new SolrInputDocument();
d1.setField("id", "1");
d1.setField("title", "Potato Chips");
d1.setField("late_vectors", "[[1.0, 2, 3.7, 4.1], [2.2, -2.5, 7.3, 4.0]]");

final SolrInputDocument d2 = new SolrInputDocument();
d2.setField("id", "2");
d2.setField("title", "Onion Chips");
d2.setField("late_vectors", "[[2.0, 5.6, -3.2, 1.4], [7.8, -2.5, 3.7, 0.0034], [-2.2, 5.5, 0.6, -0.030]]");

client.add(Arrays.asList(d1, d2));
				
			
```

where `solrUrl` is a String containing the endpoint of your collection (e.g., “**`http://localhost:8983/solr/YOUR_COLLECTION`**”).

##### Query Time

At query time, late interaction can be used as a reranking step on top of the results returned by the lexical retriever in Solr. By default, Solr applies reranking to the top 200 documents retrieved by the initial query (reRankDocs=200). These candidates are then rescored using the late interaction function **`lateVector`**, which compares the query token embeddings with the document’s token embeddings stored at index time, following the principle introduced by ColBERT (see above).

A minimal example of a reranking query looks like this:

```
				
					q=*:*&amp;
rq={!rerank reRankQuery=$rqq}&amp;
rqq={!func}lateVector(late_vectors,"[[2.0, 5.6, -3.2, 1.4], [-2.2, 5.5, 0.6, -0.030]]")
				
			
```

Here, the **`lateVector`** function is responsible for delegating the computation of the late interaction score to Lucene. It takes two arguments: the field name containing the token embeddings (in this case **`late_vectors`**) and a string representation of the query embeddings, which should be produced from the query text by the same model you used at index time. Each inner list usually represents the embedding of a single query token, meaning the full structure corresponds to the set of token-level vectors that participate in the late interaction scoring.

One small but important detail concerns single-token queries. Even if the query produces only one embedding vector, it must still follow the *list-of-lists* format expected by the Solr parser. In practice, this means the vector should be written as **`[[1,2,3,4]]`** rather than **`[1,2,3,4]`**. If this convention is not met, Solr will return an error because the parser used by the function expects a consistent nested structure representing the sequence of query token embeddings, even if the sequence contains just one vector.

The result of the query above is the following:

```
				
					{
    "response": {
        "numFound": 2,
        "start": 0,
        "numFoundExact": true,
        "docs": [
            {
                "id": "2",
                "title": [
                    "Onion Chips"
                ],
                "late_vectors": "[[2.0, 5.6, -3.2, 1.4], [7.8, -2.5, 3.7, 0.0034], [-2.2, 5.5, 0.6, -0.030]]",
                "_version_": 1860172349716824064,
                "_root_": "2"
            },
            {
                "id": "1",
                "title": [
                    "Potato Chips"
                ],
                "late_vectors": "[[1.0, 2, 3.7, 4.1], [2.2, -2.5, 7.3, 4.0]]",
                "_version_": 1860172349715775488,
                "_root_": "1"
            }
        ]
    }
}
				
			
```

Note that the top document has the title “Onion Chips”. This is because the query matches two of the three vectors stored for that document, resulting in the maximum possible score for a query with two tokens.

You should now have everything you need to start exploring the new Late Interaction field in Apache Solr. Hopefully, this post proved to be helpful and gave you some useful insights. Keep an eye on our website for updates, news, and future blog posts!

## Need Help with this topic?​

If you're struggling with late interaction implementation, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with late interaction implementation, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)