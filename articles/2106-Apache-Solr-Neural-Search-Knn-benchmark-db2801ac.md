---
title: 'Apache Solr Neural Search Knn benchmark'
company: Sease
tag: 召回
date: 2022-01-24
url: https://sease.io/2022/01/apache-solr-neural-search-knn-benchmark.html
account: 
origin: harvest3-202607
---
Neural Search in Apache Solr has been contributed to the Open Source community by Sease [[1]](https://github.com/apache/solr/commit/c309a8a65d8868e8ae034f80d5682b1587db3863) with the work of [**Alessandro Benedetti**](https://sease.io/about/alessandro-benedetti) (Apache Lucene/Solr PMC member and committer) and [**Elia Porciani**](https://sease.io/about/elia-porciani) (Sease R&D software engineer). It relies on the **Apache Lucene** implementation [[2](https://github.com/apache/lucene-solr/commit/b36b4af22bb76dc42b466b818b417bcbc0deb006)] for the K-nearest neighbour search.

For more information about the contribution see the blog post about [Apache Solr Neural Search](https://sease.io/2022/01/apache-solr-neural-search.html).

## Setup and collection

To benchmark our solution we setup our solr instances using dockerized solr in a t3.large aws machine (2 vCPU, 8GB ram).

We have chosen to use the [MS MARCO](https://microsoft.github.io/msmarco/) collection for document retrieval. We used a subset of the documents as it is very expensive to transform all of them with **BERT** and our goal was only to perform a simple benchmark.

We have taken the first 461K documents from the collection. From here, we have applied **BERT** to all the documents in the sub-sample and all the queries and we stored the embeddings in separate files structured in the following way:

* one line for each vector
* each vector is a comma-separated list of float values

Here are the stats of the resulting files:

|  |  |
| --- | --- |
| #documents | 461k |
| embedding vector length | 768 |
| document file size | 3.1 GB |
| embedding file size | 3.8 GB |
| #queries | 5750 |
| AVG document length | 1087 words |
| AVG query length | 5.9 words |

## Indexing speed and size

We created two indexes: one only with the documents indexed as text, and the other one with the embeddings (using **DenseVectorField** field type). Here are the results of the indexing process.

##### Text

* Indexing time: 15 minutes
* index size (after optimization, no stored fields): 1.17 GB

##### Embeddings

* Indexing time: 32 minutes
* Index size (after optimization, no stored fields): 1.34 GB

**NB.** *These numbers are very specific to this use case.*

##### Stored fields

We wanted to have some kind of indication that stored fields are managed correctly. We created another solr index where we indexed the embedding data as multivalue **FloatPointField**. Then, we compared the space occupancy of the stored fields only between the two Solr instances.

The stored fields for the **DenseVectorField** field type are taking **1420MB**. Instead, the stored fields for **FloatPointField** take **1480MB**. There is no difference in space occupancy of **DenseVectorField** and multivalue **FloatPointField**.

## Query Performance

For measuring query performance, we have taken the average round trip time of the rest call execution. We repeated the measurements after the index optimization.

|  |  |  |
| --- | --- | --- |
|  | before optimization | after optimization |
| text queries | 32ms | 27ms |
| knn vector queries | 22ms | 8ms |

From the results in the table, we can see as in this specific use case knn vector search is more efficient than full-text search (especially when the index is optimized). However, keep in mind that for executing the queries we already have transformed text queries into vectors in a preprocessing step. This step has a non-negligible cost. We decided to exclude it from the benchmarks as it depends on the model used.

## Need Help With This Topic?​​

If you’re struggling with Neural Search in Apache Solr and knn search, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Neural Search in Apache Solr and knn search, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)