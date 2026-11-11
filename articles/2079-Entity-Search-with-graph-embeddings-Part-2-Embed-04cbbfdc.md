---
title: 'Entity Search with graph embeddings – Part 2 – Embeddings and clustering'
company: Sease
tag: 召回
date: 2019-11-20
url: https://sease.io/2019/11/entity-search-with-graph-embeddings-part-2-embeddings-and-clustering.html
account: 
origin: harvest3-202607
---
Let’s continue our journey into this entity search thesis!

In Part 1 we have described [what entities and entity search are](https://sease.io/2019/11/entity-search-with-graph-embeddings---part-1---overview.html). We have explained how this search is implemented in the state-of-the-art. We have also introduced the new approach of this dissertation specifying also the dataset and the test collection used. Finally, we have described graph embeddings techniques, focusing on the specific algorithm we use: Node2Vec.

In this post we will describe the first part of the project pipeline: **entities representation** and **clustering**.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/Pipeline_Entity_Search.png?w=800&ssl=1)

## Entities representation

As we saw in the previous post, the input of our pipeline is the set of all the RDF triples of the subgraph we have selected from the DBpedia dataset. Now we want to use these triples in order to obtain those entities representations necessary for the subsequent clustering phase.

To obtain these representations, we created two files from the two different tables, nodes and edges, we have stored in the database. These files will be the input for our embedding algorithm Node2Vec. In particular, we used the Python implementation of Node2Vec, which you can find [here](https://github.com/eliorc/node2vec) because it adds support for big graphs that cannot fit in memory.

The requested input for this algorithm is a graph, defined through its nodes and edges. Once given these parameters through our two files, we executed the Node2Vec algorithm. This will return us a file containing the embeddings in a numerical vector form.

For the Node2Vec execution, there are several **parameters** we can set:

* **Embedding dimension**: the number of features we want to use in our entity representation;
* **Walk length**: the length of each walk we create in the training phase of the neural network;
* **Number of walks**: the number of walks we want to create starting from the node we want to represent;
* **p**: parameter that defines the probability of revisiting an already-seen node;
* **q**: parameter that defines the probability of visiting a new node;
* **Workers**: the degree of parallelism we want to use in the algorithm execution.

The tuning of these parameters is fundamental for the retrieval process because it directly affects the embedding quality and therefore the document creation.

## Clustering

Once we have these embeddings, we want to cluster them by similarity to subsequently create our documents. As mentioned in [Part 1](https://sease.io/2019/11/entity-search-with-graph-embeddings---part-1---overview.html) we want to associate a document to each cluster.

To create these sets of entities embeddings we used the **K-MeansSort** algorithm. It is a modified version of the classic K-Means, in particular, it partially changes how the algorithm decides which class assign points. Wanting to provide a more detailed description, K-MeansSort speeds up this decision process exploiting the triangle inequality and the means sorting. It uses them to reduce the number of comparisons between the distances calculated between points and means.

For the execution of this clustering phase, we used a framework called ELKI [[1]](https://elki-project.github.io/). This framework gives tools for the implementation of data mining algorithms, in particular for clustering methods. ELKI is an open source data mining software, written in Java, that offers data index structures to provide major performance gains. It is also highly scalable and has a modular approach which makes it fast, versatile and easy to use.

Since K-MeansSort is based on K-means, it requires input of the number of clusters we want to obtain at the end of the process.

## Need Help With This Topic?​​

If you’re struggling with entities embedding, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with entities embedding, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)