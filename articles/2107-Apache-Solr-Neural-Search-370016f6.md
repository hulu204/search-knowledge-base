---
title: 'Apache Solr Neural Search'
company: Sease
tag: 召回
date: 2022-01-24
url: https://sease.io/2022/01/apache-solr-neural-search.html
account: 
origin: harvest3-202607
---
The first milestone for Neural Search in **Apache Solr** has been contributed to the open source community by **Sease** [[1](https://github.com/apache/solr/commit/c309a8a65d8868e8ae034f80d5682b1587db3863)] with the work of [**Alessandro Benedetti**](https://sease.io/about/alessandro-benedetti) (Apache Lucene/Solr PMC member and committer) and [**Elia Porciani**](https://sease.io/about/elia-porciani) (Sease R&D software engineer).  
It relies on the **Apache Lucene** implementation [[2]](https://github.com/apache/lucene-solr/commit/b36b4af22bb76dc42b466b818b417bcbc0deb006) for the K-nearest neighbour search.  
Special thanks to Christine Poerschke, Cassandra Targett, Michael Gibney, and all the other reviewers who helped a lot in the last phases of the contribution. Even a single comment has been much appreciated, it’s always thanks to the community if we achieve progress.

Let’s start with a short introduction, on how the neural approach is improving search.

We can summarise Search as four primary areas:

* **generate a representation of the query** that specifies the information need
* **generate a representation of the document** that captures the information contained
* **match the query and the document** representations from the corpus of information
* **assign a score to each matched document** to establish a meaningful document ranking by relevance in the results

Neural Search is an industry derivation from the academic field of Neural Information Retrieval [[3]](https://www.microsoft.com/en-us/research/uploads/prod/2017/06/fntir2018-neuralir-mitra.pdf), and it focuses on improving any of these areas with neural network-based techniques.

## Artificial Intelligence, Deep Learning and Vector Representations

More and more frequently, we hear about how Artificial Intelligence (AI from now on) permeates many aspects of our lives.

When we talk about AI we are referring to a set of techniques that enable machines to learn and show intelligence similar to humans.

With the strong and steady advance of computer power in the recent past, AI has seen a resurgence and it is now used in many domains, including software engineering and Information Retrieval (the science that regulates Search Engines and similar systems).

In particular, the advent of Deep Learning [[4]](https://en.wikipedia.org/wiki/Deep_learning) introduced the use of deep neural networks to solve complex problems that were very challenging for classic algorithms.

For the sake of this blog post, it suffices to know that Deep Learning can be used to produce a vector representation of both the query and the documents in a corpus of information.

##### Dense Vector Representation

A traditional [inverted index](https://sease.io/2015/07/exploring-solr-internals-lucene.html) can be considered to model text as a “sparse” vector, in which each term in the corpus corresponds to one vector dimension. In such a model (see also the [Bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) approach), the number of dimensions corresponds to the term dictionary cardinality and the vector for any given document contains mostly zeros (hence it is called sparse, as only a few terms that exist in the overall dictionary will be present in any given document).

Dense vector representation contrasts with term-based sparse vector representation in that it distils approximate semantic meaning into a fixed (and limited) number of dimensions.

The number of dimensions in this approach is generally much lower than in the sparse case, and the vector for any given document is dense, as most of its dimensions are populated by non-zero values.

In contrast to the sparse approach (for which tokenizers are used to generate sparse vectors directly from text input) the task of generating vectors must be handled in application logic external to Apache Solr.

Various Deep Learning models such as BERT [[5]](https://en.wikipedia.org/wiki/BERT_(language_model)) can encode textual information as dense vectors, to be used for Dense Retrieval strategies.

For additional information, you can refer to our blog post about [how to use BERT to improve search relevance](https://sease.io/2021/12/using-bert-to-improve-search-relevance.html).

##### Approximate Nearest Neighbor

Given a dense vector **`v`** that models the information need, the easiest approach for providing dense vector retrieval would be to calculate the distance(euclidean, dot product, etc.) between **`v`** and each vector **`d`** that represents a document in the corpus of information.

This approach is quite expensive, so many approximate strategies are currently under active research.

An approximate nearest neighbour search algorithm returns results, whose distance from the query vector is at most**![c](https://wikimedia.org/api/rest_v1/media/math/render/svg/86a67b81c2de995bd608d5b2df50cd8cd7d92455)**times the distance from the query vector to its nearest vectors.   
The benefit of this approach is that most of the time, an approximate nearest neighbour is almost as good as the exact one.  
In particular, if the distance measure accurately captures the notion of user quality, then small differences in the distance should not matter [[6]](https://ieeexplore.ieee.org/document/4031381).

##### Hierarchical Navigable Small World Graph

The strategy implemented in Apache Lucene and used by Apache Solr is based on Navigable Small-world graphs.

It provides an efficient approximate nearest neighbour search for high dimensional vectors[[7]](https://doi.org/10.1016/j.is.2013.10.006)[[8]](https://arxiv.org/abs/1603.09320)[[9]](https://erikbern.com/2018/06/17/new-approximate-nearest-neighbor-benchmarks.html)[[10]](https://www.benfrederickson.com/approximate-nearest-neighbours-for-recommender-systems/).

Hierarchical Navigable Small World Graph (HNSW) is a method based on the concept of ***proximity neighbours graphs***:  
every vector in the vectorial space associated with the corpus of information is uniquely associated with a

vertex ![v_{i}\in V](https://wikimedia.org/api/rest_v1/media/math/render/svg/314467aba70c6bd74cacc52d232baacce36f80ad) in the graph ![G(V,E)](https://wikimedia.org/api/rest_v1/media/math/render/svg/7dc43221ee885a10b87c89373b12b8c1110e7ca5). 

Vertices are connected through edges based on their proximity, the closer (in terms of a distance function) ones are linked.

Building the graph is affected by hyper-parameters that regulate how many connections to build per layer and how many layers to build.

At query time, the neighbour structure is navigated to find the closest vector(s) to the target one, starting from a seed node and iterating as we get closer and closer to the target.

I found [this blog](https://www.pinecone.io/learn/hnsw/) to be quite useful for a deep dive into the topic.

## Apache Lucene Implementation

The first thing to notice is that the current Lucene implementation is not hierarchical.  
So there is just one single layer in the graph, see the latest comments in the original Jira issue tracking the development progress[[11]](https://issues.apache.org/jira/browse/LUCENE-9004?focusedCommentId=17393216&page=com.atlassian.jira.plugin.system.issuetabpanels%3Acomment-tabpanel#comment-17393216).  
The main reason is to find an easier design, development, and integration process for such a simplified implementation in the Apache Lucene ecosystem.  
It’s agreed that introducing the hierarchical layered structure will bring benefits in terms of lower dimension vector management and query time(reducing the candidate nodes to traverse).  
This implementation is in progress[[12]](https://issues.apache.org/jira/browse/LUCENE-10054).

**So** **what are the Apache Lucene components involved with the Navigable Small World Graph and K-Nearest Neighbors capability**?  
Let’s explore the code:

**N.B.** *You can skip this paragraph if you are not interested in Lucene internals and codecs*

The ***org.apache.lucene.document.KnnVectorField*** is the entry point:   
it requires at index time the **vector dimension** and the **similarity Function**(the vector distance function to use when building the NSW graph).  
Those are set in the **org.apache.lucene.document.FieldType** through the **#setVectorDimensionsAndSimilarityFunction** method.

When updating the document field schema ***org.apache.lucene.index.IndexingChain#updateDocFieldSchema*** the information is extracted from the **FieldType** and saved in the ***org.apache.lucene.index.IndexingChain.FieldSchema***.

And from the ***FieldSchema*** the ***KnnVectorField*** configurations finally reach the ***org.apache.lucene.index.FieldInfo*** in ***org.apache.lucene.index.IndexingChain#initializeFieldInfo***.

Now the Lucene codec has all the field-specific configurations necessary to build the NSW graph.  
Let’s see how:

First of all from the ***org.apache.lucene.codecs.lucene90.Lucene90Codec#Lucene90Codec*** you see that the default format for the KNN vectors is the ***org.apache.lucene.codecs.lucene90.Lucene90HnswVectorsFormat***.

The associated index writer is the **org.apache.lucene.codecs.lucene90.Lucene90HnswVectorsWriter**.  
This component has access to the ***FieldInfo*** previously initialized when writing fields to the index in ***org.apache.lucene.codecs.lucene90.Lucene90HnswVectorsWriter#writeField***.  
When writing a ***KnnVectorField***, the ***org.apache.lucene.util.hnsw.HnswGraphBuilder*** is involved and finally a   
***org.apache.lucene.util.hnsw.HnswGraph*** is built.

## Apache Solr implementation

*Available from Apache Solr 9.0*

This first contribution allows to index single-valued dense vector fields and to search for K-nearest neighbours using an approximated distance function.

Current features :

* DenseVectorField type
* Knn Query Parser

### DenseVectorField Type

The dense vector field gives the possibility of indexing and searching dense vectors of float elements.

e.g.

`[1.0, 2.5, 3.7, 4.1]`

Here’s how `DenseVectorField` should be configured in the schema:

```
				
					&lt;fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="4" similarityFunction="cosine"/&gt; &lt;field name="vector" type="knn_vector" indexed="true" stored="true"/&gt;
				
			
```

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| ****Parameter Name**** | **Required** | **Default** | **Description** | **Accepted values** |
| `vectorDimension` | True |  | The dimension of the dense vector to pass in. | Integer < = 1024 |
| `similarityFunction` | False | `euclidean` | Vector similarity function; used in search to return top K most similar vectors to a target vector. | `euclidean`, `dot_product` or `cosine`. |

* `euclidean`: [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance)
* `dot_product`: [Dot product](https://en.wikipedia.org/wiki/Dot_product). **NOTE**: This similarity is intended as an optimized way to perform cosine similarity. To use it, all vectors must be of unit length, including both document and query vectors. Using dot product with vectors that are not unit length can result in errors or poor search results..
* `cosine`: [Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity). **NOTE**: the preferred way to perform cosine similarity is to normalize all vectors to unit length, and instead use DOT\_PRODUCT. You should only use this function if you need to preserve the original vectors and cannot normalize them in advance.

DenseVectorField supports the attributes: `indexed`, `stored`.

**N.B.** *currently multivalue is not supported.*

### Customise the Index Codec

To use the following advanced parameters that customise the codec format and the hyper-parameter of the HNSW algorithm make sure you set this configuration in the solrconfig.xml:

```
				
					&lt;codecFactory class="solr.SchemaCodecFactory"/&gt;
...
				
			
```

Here’s how **`DenseVectorField`** can be configured with the advanced codec hyper-parameters:

```
				
					&lt;fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="4" similarityFunction="cosine" codecFormat="Lucene90HnswVectorsFormat" hnswMaxConnections="10" hnswBeamWidth="40"/&gt;
&lt;field name="vector" type="knn_vector" indexed="true" stored="true"/&gt;
				
			
```

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Parameter Name** | **Required** | **Default** | **Description** | **Accepted values** |
| `codecFormat` | False | `Lucene90HnswVectorsFormat` | Specifies the knn codec implementation to use | `Lucene90HnswVectorsFormat` |
| `hnswMaxConnections` | False | `16` | **`Lucene90HnswVectorsFormat` only:** Controls how many of the nearest neighbor candidates are connected to the new node. It has the same meaning as `M` from the paper[[8]](https://arxiv.org/abs/1603.09320). | `Integer` |
| `hnswBeamWidth` | False | `100` | **`Lucene90HnswVectorsFormat` only:** It is the number of nearest neighbor candidates to track while searching the graph for each newly inserted node. It has the same meaning as `efConstruction` from the paper[[8]](https://arxiv.org/abs/1603.09320). | `Integer` |

Please note that the **`codecFormat`** accepted values may change in future releases.

|  |  |
| --- | --- |
| **NOTE** | Lucene index back-compatibility is only supported for the default codec. If you choose to customize the `codecFormat` in your schema, upgrading to a future version of Solr may require you to either switch back to the default codec and optimize your index to rewrite it into the default codec before upgrading, or re-build your entire index from scratch after upgrading. |

For the hyper-parameters of the HNSW implementation, see [[8]](https://arxiv.org/abs/1603.09320) for details.

### How to Index a Vector

Here’s how a `DenseVectorField` should be indexed:

**JSON**

```
				
					[{ "id": "1",
"vector": [1.0, 2.5, 3.7, 4.1]
},
{ "id": "2",
"vector": [1.5, 5.5, 6.7, 65.1]
}
]
				
			
```

**XML**

```
				
					&lt;field name="id"&gt;1
&lt;field name="vector"&gt;1.0
&lt;field name="vector"&gt;2.5
&lt;field name="vector"&gt;3.7
&lt;field name="vector"&gt;4.1

&lt;field name="id"&gt;2
&lt;field name="vector"&gt;1.5
&lt;field name="vector"&gt;5.5
&lt;field name="vector"&gt;6.7
&lt;field name="vector"&gt;65.1
				
			
```

#### Java – **SolrJ**

```
				
					final SolrClient client = getSolrClient();

final SolrInputDocument d1 = new SolrInputDocument();
d1.setField("id", "1");
d1.setField("vector", Arrays.asList(1.0f, 2.5f, 3.7f, 4.1f));

final SolrInputDocument d2 = new SolrInputDocument();
d2.setField("id", "2");
d2.setField("vector", Arrays.asList(1.5f, 5.5f, 6.7f, 65.1f));

client.add(Arrays.asList(d1, d2));
				
			
```

## Knn Query Parser

The `knn` K-Nearest Neighbors query parser allows finding the k-nearest documents to the target vector according to indexed dense vectors in the given field.

It takes the following parameters:

|  |  |  |  |
| --- | --- | --- | --- |
| **Parameter** Name | **Required** | **Default** | **Description** |
| `f` | True |  | The DenseVectorField to search in. |
| `topK` | False | 10 | How many k-nearest results to return. |

Here’s how to run a KNN search:

```
				
					&amp;q={!knn f=vector topK=10}[1.0, 2.0, 3.0, 4.0]

				
			
```

The search results retrieved are the K-nearest to the vector in the input **`[1.0, 2.0, 3.0, 4.0]`**, ranked by the similarityFunction configured at indexing time.

### Usage with Filter Queries

The `knn` query parser can be used in filter queries:

```
				
					&amp;q=id:(1 2 3)&amp;fq={!knn f=vector topK=10}[1.0, 2.0, 3.0, 4.0]

				
			
```

The `knn` query parser can be used with filter queries:

```
				
					&amp;q={!knn f=vector topK=10}[1.0, 2.0, 3.0, 4.0]&amp;fq=id:(1 2 3)

				
			
```

|  |  |
| --- | --- |
| **IMPORTANT** | When using `knn` in these scenarios make sure you have a clear understanding of how filter queries work in Apache Solr: The Ranked List of document IDs resulting from the main query `q` is intersected with the set of document IDs deriving from each filter query `fq`.e.g.Ranked List from `q`=`[ID1, ID4, ID2, ID10]`  Set from `fq`=`{ID3, ID2, ID9, ID4}` = `[ID4,ID2]` |

### Usage as Re-Ranking Query

The `knn` query parser can be used to rerank first-pass query results:

```
				
					&amp;q=id:(3 4 9 2)&amp;rq={!rerank reRankQuery=$rqq reRankDocs=4 reRankWeight=1}&amp;rqq={!knn f=vector topK=10}[1.0, 2.0, 3.0, 4.0]
				
			
```

|  |  |
| --- | --- |
| **IMPORTANT** | When using **`knn`** in reranking pay attention to the **`topK`** parameter. The second pass score(deriving from knn) is calculated only if the document **`d`** from the first pass is within the K-nearest neighbours (**in the whole index**) of the target vector to search. This means the second pass **`knn`** is executed on the whole index anyway, which is a current limitation. The final ranked list of results will have the first pass score(main query **`q`**) added to the second pass score(the approximated similarityFunction distance to the target vector to search) multiplied by a multiplicative factor(reRankWeight). So if the document **`d`** is not present in the knn results, you get a zero contribution to the original score even if the distance vector calculation with the target query vector is not zero. Details about using the ReRank Query Parser can be found in the Apache Solr Wiki [[13]](https://solr.apache.org/guide/query-re-ranking.html) section. |

## Future Works

This is just the beginning of the Apache Solr neural capabilities, more is coming! Don’t forget to keep an eye on our [Apache Solr blog posts category](https://sease.io/category/apache-solr).  
I hope you enjoyed the overview and stay tuned for updates!

###### references

[6] *Andoni, A.; Indyk, P. (2006-10-01). “Near-Optimal Hashing Algorithms for Approximate Nearest Neighbor in High Dimensions”. 2006 47th Annual IEEE Symposium on Foundations of Computer Science (FOCS’06). pp. 459–468. [CiteSeerX](https://en.wikipedia.org/wiki/CiteSeerX_(identifier)) [10.1.1.142.3471](https://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.142.3471). [doi](https://en.wikipedia.org/wiki/Doi_(identifier)):[10.1109/FOCS.2006.49](https://doi.org/10.1109%2FFOCS.2006.49). [ISBN](https://en.wikipedia.org/wiki/ISBN_(identifier)) [978-0-7695-2720-8](https://en.wikipedia.org/wiki/Special:BookSources/978-0-7695-2720-8).*

[7] *Yury Malkov, Alexander Ponomarenko, Andrey Logvinov, Vladimir Krylov, Approximate nearest neighbor algorithm based on navigable small world graphs,*  
*Information Systems, Volume 45, 2014, Pages 61-68, ISSN 0306-4379, [https://doi.org/10.1016/j.is.2013.10.006](https://doi.org/10.1016/j.is.2013.10.006.).*

[8] *Malkov, Yury; Yashunin, Dmitry (2016). “Efficient and robust approximate nearest neighbour search using Hierarchical Navigable Small World graphs”.* [arXiv](https://en.wikipedia.org/wiki/ArXiv_(identifier)):[1603.09320](https://arxiv.org/abs/1603.09320) [[cs.DS](https://arxiv.org/archive/cs.DS)].

## Need Help with this topic?​

Did I mention we do Artificial Intelligence in Search training and specific one-day training about Deep Learning for Search?
We also provide consulting on these topics, get in touch if you want to bring your search engine to the next level with the power of AI!

[Click Here](mailto:info@sease.io)