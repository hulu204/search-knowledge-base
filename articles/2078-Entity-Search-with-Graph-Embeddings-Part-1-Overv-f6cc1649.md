---
title: 'Entity Search with Graph Embeddings - Part 1 - Overview'
company: Sease
tag: 召回
date: 2019-11-14
url: https://sease.io/2019/11/entity-search-with-graph-embeddings-part-1-overview.html
account: 
origin: harvest3-202607
---
This series of blog posts describes my master’s degree dissertation done with the supervision of Prof. Gianmaria Silvello at the University of Padova. The main focus of this project is on the use of graph embeddings to create virtual documents for the Information Retrieval Entity Search task.

This thesis description is divided into four posts:  
**Part 1** will talk about the reasons that led me to investigate this area and it will give all those notions that are essential for understanding the subsequent parts.  
Part 2 will describe the first part of the solution design: [entity representation and clustering](https://sease.io/2019/11/entity-search-with-graph-embeddings-part-2-embeddings-and-clustering.html).  
Part 3 will describe the second part of the solution design: [document creation, ranking and entity retrieval](https://sease.io/2019/12/entity-search-with-graph-embeddings-part-3-documents-and-retrieval.html).  
Part 4 will talk about the [evaluation of these systems and conclusions](https://sease.io/2019/12/entity-search-with-graph-embeddings-part-4-evaluation-and-conclusion.html).

The solution design is represented in the Figure above.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/Pipeline_Entity_Search.png?w=800&ssl=1)

## Motivation

When we are looking for information, we usually open a search engine on our mobile phone or computer and type the query we think best represents our information needs. As a response, we usually obtain a list of textual web pages that in the retrieval process are seen as the documents that make up the collection of information.

In recent years, however, we are witnessing a change of tendency that leads us from documents to entities. If we think about the searches we usually carry out, it is easy to see that we often require information that concerns people, places, and concepts that can be intuitively associated with concrete entities of the real world.

These entities are the main elements that we want to retrieve in the Entity Search process.

As **Entity,** we mean a *uniquely identifiable object that represents a specific concept in the real world such as a person, a place, etc.*  
This entity is characterized by a set of properties like its name, its attributes, and its relationships and it is usually associated with an ID to be able to identify it uniquely.

The **Entity Search** is then that *search paradigm that aims to find and access information related to entities, their attributes and relationships*. In particular, in this thesis, we focus on the **ad-hoc-entity retrieval task** which wants to find a specific entity inside the collection of data.

## Dataset and Test Collection

For the project implementation, we used **DBpedia**, a dataset that stores all the information contained in Wikipedia pages. In particular, we consider the labels, infobox properties and short abstract files of the English part of the 2015-10 version available [here](http://downloads.dbpedia.org/2015-10/).  
Labels are the titles of the Wikipedia pages, infobox properties are all those information in the box on the right side of the page while short abstracts are the brief descriptions of the page’s content.

This dataset uses the RDF language to represent entities and their attributes and relationships.  
**RDF** *is a representational language based on triples.*   
*These triples are constituted by a Subject, a Predicate and an Object*. In particular, all of these triples can be seen as a graph if we represent the subject and the object as nodes and the predicate as the edge that connects them. This graph takes the name of the **RDF graph**.

In the DBpedia triples:

* **Subject**: it is a URI that uniquely identifies an entity;
* **Predicate**: it is a verb that specifies the type of relationship between the subject and the object;
* **Object**: could be a URI of an entity (like the subject) or an attribute of the Subject (also called **literal**).

In our database, we store five different tables: one for each different file of the dataset (labels, infobox properties, short abstract) and two containing respectively the nodes and the edges of the RDF graph. The node table simply associates to each entity URI an integer, while the edge table stores all the relationships between entities (literals excluded) through couples: *(subject\_integer, object\_integer)*. For *subject\_integer* and *object\_integer* we mean the integer associated to that subject or object in the node table.  
In particular, we store all the triples of the entities having both a label and a short abstract.

As the test collection we use the DBpedia-Entity created by the [IAI group](http://iai.group/) of the University of Stavanger, the Norwegian University of Science and Technology, Wayne State University, and Carnegie Mellon University [1] available [here](https://iai-group.github.io/DBpedia-Entity/). In particular, we consider the relevance assessments and the queries from the TREC Entity campaign.

For timing computational costs reasons we reduce our dataset to a subgraph of the one mentioned before. For the creation of this subgraph, we select all those entities that are present in the relevance assessments and then also those directly connected through an edge to these. In this way, we obtain a balanced set of relevant and non-relevant entities.

## State-of-the-art

To understand the novelty that we want to introduce in the entity search process with this thesis, we have to describe the state-of-the-art and how it works.

The entity search paradigm implemented in the state-of-the-art leads back to classic textual information retrieval. To bring the search for entities back to the traditional method, it is necessary to create documents starting from the entities of the dataset. Traditional text retrieval methods rely on a collection of documents as an information base therefore, to exploit the same approaches, we have to express our knowledge through documents. In particular, we have to create a collection of documents based on entities information to use as our base for the retrieval process.

The difficulty of this process lies in the way documents are created. Currently, the state-of-the-art methods generate a single document for each entity. This document is created mainly using two approaches: **text-based approach** and **structured-based approach**. While the first one simply merges all the information concerning a single entity into a document, the second one takes into account also the type of information that we are storing through the creation of a fielded document.

The main issue with state-of-the-art methods is that they consider only information regarding entities themselves, without considering the context in which they are placed. The innovative approach that we want to introduce in this thesis wants to overcome this problem by considering also the entities context.   
Returning to the concept of RDF graph and triples mentioned before, in the document creation process the state-of-the-art methods consider all the triples of the specific entity they want to represent, while our approach consider also the triples of the nodes belonging to the neighbourhood of the entity.

## What's new?

Until now we have understood that the basic idea of ​​this thesis is to consider also the context in which an entity is positioned to improve retrieval, but we have not yet described how we want to consider this context.

The main idea of this dissertation is to create documents that do not contain all the information of just a single entity, but all the information of a set of similar and highly related entities. These groups are obtained through a clustering process executed on entities representations, also called **embeddings**, that are generated using a graph embedding method called **Node2Vec**.

Using documents that contain a set of entities means that, in the retrieval phase, we will obtain a ranked list of documents, that is a ranked list of groups of entities. In this way, we will consider relevant not only those entities that directly match the user query but also all those other entities in the document.  
This allows us to retrieve also highly correlated and similar entities that are very likely to be relevant for the user information need and that would not otherwise be selected.

## Graph embeddings

Let’s see how these embeddings are generated starting from our dataset expressed as an RDF graph.

**Graph embedding** *is a method that allows us to obtain a numerical vector representation of nodes and edges of a graph. It represents the topology and structure of a graph through vectors or set of vectors*.  
These vectors are calculated through the use of a **neural network**.

Looking at this definition we can see that we can use this approach to create vector representation of the nodes of our RDF graph which in turn are associated with entities.  
The advantage of using these embeddings is that they allow us to use vector space theory and operations such as calculating similarities and distances between entities.

##### Node2Vec

**Node2Vec** *is the state-of-the-art general-purpose scalable feature learning method for network analysis*. It is based on the **Word2Vec** algorithm and therefore it creates an embedding that considers the context of the instance we want to represent.

While Word2Vec aims to create a vector representation of a word, considering the phrase in which it is collocated, Node2Vec achieves the same result working on graph nodes. In particular, it creates a vector representation of a node, considering the graph context in which that node is collocated.

* Word2Vec **context** is a window of words taken near the word we want to represent;
* Node2vec **context** is constituted by those nodes visited by some generated random walks starting from the nodes we want to represent.

Node2Vec walks are called random because they are generated in a non-deterministic way, following some transition probabilities that guide the algorithm in the choice of the next node to visit and add to the walk.   
In particular, this choice aims to consider both these two additional features in the embedding generation:

* **Homophily**: is a relationship between nodes that are highly connected to each other and then belong to the same community;
* **Structural roles**: a relationship between all those nodes that have similar roles in the network.

The first one can be found by exploiting the Breadth-First Search traversal algorithm while the second one is through the Depth-First Search algorithm as shown in the Figure below [2].

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/Homophily_StructuralRoles.jpg?w=800&ssl=1)

The transition parameters mentioned before then influence, in the walks creation phase, the choice of revisiting an already-seen node with respect to exploring a new one. The choice to stay close to the previous node will involve a traversal more similar to that performed by BFS, while the choice of visiting new nodes will involve a traversal more similar to the one performed by DFS.

##### **References**

[1] Faegheh Hasibi, Fedor Nikolaev, Chenyan Xiong, Krisztian Balog, Svein Erik Bratsberg, Alexander Kotov, and Jamie Callan. 2017. *“DBpedia-Entity v2: A Test Collection for Entity Search”*, In proceedings of 40th ACM SIGIR conference on Research and Development in Information Retrieval (SIGIR ’17). 1265-1268.   
[2] A. Grover and J. Leskovec. node2vec: Scalable feature learning for networks. In Proceedings of the 22nd ACM SIGKDD international conference on Knowledge discovery and data mining, pages 855–864. ACM, 2016.

## Need Help With This Topic?​​

If you’re struggling with entity search and graph embeddings, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with entity search and graph embeddings, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)