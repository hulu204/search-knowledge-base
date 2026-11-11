---
title: 'Entity Search with graph embeddings – Part 3 – Documents and retrieval'
company: Sease
tag: 召回
date: 2019-12-05
url: https://sease.io/2019/12/entity-search-with-graph-embeddings-part-3-documents-and-retrieval.html
account: 
origin: harvest3-202607
---
In this post, we want to get to the heart of the process of virtual document creation. As we explained in the [first overview](https://sease.io/2019/11/entity-search-with-graph-embeddings---part-1---overview.html), these documents are essential for the retrieval phase and its performance. This part of the pipeline is, indeed, the one where we create our approaches in many different versions.

Summarizing what was previously illustrated. In Part 2 we have seen [how we obtain entities embeddings starting from RDF triples and how we use them in the clustering process](https://sease.io/2019/11/entity-search-with-graph-embeddings-part-2-embeddings-and-clustering.html). At the end of this phase, we have obtained several sets of highly related and similar entities.

In this post, **we will describe the second part of the project pipeline: the document creation, the ranking systems,** and the **entity retrieval**.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/Pipeline_Entity_Search.png?w=800&ssl=1)

## Virtual documents creation

Once obtained clusters we can create all those virtual documents that will become the collection for our retrieval phase. To do this, our approach associates each semantic field, identified by a cluster, to a document. In detail the **process** consists of five phases:

1. 1. Select a cluster;
   2. Take cluster entities one after the other;
   3. For each entity, we select the corresponding RDF triples (those that have that entity as a subject or object);
   4. Process the triples to get information in natural language by removing symbols like “<“, “>”, “””, “\_”, etc.
   5. Merge the information in a textual file that represents the document associated with the cluster at hand.

Our documents collection is then obtained repeating the entire process for each cluster.

![This image has an empty alt attribute; its file name is Document_process.png](https://i1.wp.com/sease.io/wp-content/uploads/2019/11/Document_process.png?fit=712%2C206&ssl=1)

## Ranking system

Thanks to the previous phase we now have a collection of documents that is a collection of clusters. Now we would like to implement the retrieval to obtain, for each user query (also called a topic), a ranked list of clusters. This phase aims to identify which semantic fields (clusters) are more relevant for the user information need. In the next phase, we execute a re-ranking of the entities inside these fields.

For the retrieval, we have applied the classic text retrieval technique through the use of the Terrier software. This is an open-source search engine written in Java and developed by the University of Glasgow. It implements state-of-the-art indexing and retrieval functionalities, it provides a platform for the development and evaluation of large-scale retrieval applications.

For the ranking of the documents we use:

* + In the indexing phase: stopword removal and stemming;
  + In the retrieval phase: the BM25 model.

After this retrieval phase, we obtain a ranked list of clusters. Looking at this result someone could argue that the user would like to have instead a ranked list of entities. This is the aim of the next phase: extract from these clusters those entities that are more relevant for the user.

## Entity retrieval

For entity retrieval, we implemented two different approaches: **combination systems** and **fusion systems**. The first one aims to obtain a **ranked list of entities** selecting them directly from those clusters that belong to the ranked list of the previous phase. The second one aims to obtain the same result exploiting both the state-of-the-art methods together with the combination systems.

##### Combination systems

The first approach we implemented for entity retrieval is composed of three different versions. In particular, they are:

1. 1. **SICO**
   2. **SUMCO**
   3. **WECO**

In order to better understand the entity retrieval process, we first want to give an overview of the main idea and then go into detail about the process.

**Idea**: the idea is to extract from the top-k clusters of the ranked list of clusters, the top-j entities, and then merge them into the final run.

How to extract the top-j entities from the top-k clusters? We decided to use the state-of-the-art approach described in [Part 1](https://sease.io/2019/11/entity-search-with-graph-embeddings---part-1---overview.html). In particular, we restrict our mini-world of interest to the cluster level. In this way, we have a dataset consisting of all the entities inside the cluster. The collection we create is made of documents where each document represents one of the entities in the cluster. As in the state-of-the-art, we will have a document for each entity. This is done for each cluster obtaining a collection for each one of them.

This set of collections (one for each cluster) is created before the start of the entity retrieval process.

The main **process**, common to all systems, is the one described in the figure below. It consists of five phases:

1. 1. **Cluster selection (or Line selection)**: we select the first line of the ranked list of clusters (clusters run). In particular, we take the topic id and the cluster id.
   2. **Re-ranking**: we execute the traditional retrieval process on the collection related to the cluster and the topic we selected in the previous point. In this way, we obtain a ranked list of the entities in the cluster for that topic (run with reranked entities).
   3. **Composition**: we take some of the entities in the run obtained from the previous step and merge them into the final run.

This is repeated for each top-k clusters of each topic in the ranked list of clusters.

![This image has an empty alt attribute; its file name is comb_sys.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/comb_sys.png?w=800&ssl=1)

The difference between the three versions of the combination systems is in the way we execute the composition phase, so how we select entities and how we insert them into the final run.

###### SICO

In the composition phase, this approach takes a fixed number of entities from the corresponding reranked entities run. In particular, we take a number of *maxEntity* entities with a *score>0* and insert them into the final run in the same order in which they appear in the reranked entities run.

As previously explained this is done for top-k clusters of a specific topic, therefore the selected reranked entities run will change every time with respect to the selected cluster and topic id.

In the figure below we report an example of this system. In particular, we consider the top-2 clusters for topic1. We can see that from the first cluster we obtain the reranked entities run at the top (F, B, and A), while from the second cluster, we obtain the reranked entities run at the bottom (E, D, and C). From both these runs, we take the first maxEntity=3 entities with a score>0 (the score is not shown but we suppose it to be greater than 0). Finally, we insert these entities in the final run keeping their initial order. In this way, we preserve both clusters and entities ranking.

![This image has an empty alt attribute; its file name is sico.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/sico.png?resize=335%2C384&ssl=1)

###### SUMCO

In the composition phase, this approach executes the same process as the one described in SICO with two differences. The first one is that all the entities related to the same topic are ordered through their score before being inserted into the final run. The second is that, in this reordering, we do not use the entity score of the reranked entities run as it is but we add to it the score of the cluster that contains the entity. This becomes the final score of the final run.

In the figure below we report an example of this system. The first difference we notice with respect to SICO is that between the two reranked entities runs we found the initial clusters run. From the entities runs we take the first *maxEntity=3* entities with a score>0 (the same as SICO) and then we add to their score the ones of the cluster to which they belong. Consequently, to the entities F, B, and A we add the score of the first top-k cluster, that is clusterD; while to the entities E, D and C we add the score of the second top-k cluster that is clusterA. Finally, we insert these entities in the final run by ordering them according to their score. We can see that, for topic 1, EntityF is the one at the top because it has the higher score, while EntityC is at the bottom because it has the lowest score.

![This image has an empty alt attribute; its file name is sumco.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/sumco.png?resize=411%2C398&ssl=1)

The idea of using this new final score is to create a ranked list of entities (final run) that takes into account the relevance of both the cluster and the entity.

###### WECO

In the composition phase, this approach executes the same process as the one described in SUMCO with a different final score. In this case, the final score is calculated as:

*finalScore = (entityScore + clusterScore) \* similarity*

where *similarity* is the cosine similarity computed between the cluster mean, that is a vector representing the centroid of the cluster to which the entity belongs, and the entity embedding vector: *similarit*y *= 1 – cosineDistance(clusterMean, entityEmbedding)*.   
An entity that is positioned near the mean of its cluster probably results in being very inherent to the topic of the cluster and highly related to other entities within the same set. In this way, we consider how much an entity is representative of its cluster. Entities that are more representative of their cluster have the highest score and then are considered more important for retrieval purposes.

In the figure below we report an example of this system.

![This image has an empty alt attribute; its file name is weco.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/weco.png?resize=405%2C402&ssl=1)

##### Fusion systems

The second approach we implement is born with the purpose of incorporating advantages from both the combination systems and the state-of-the-art. It is composed of four different versions. In particular, they are:

1. 1. **SIFU**
   2. **SOFU**
   3. **LEFU**
   4. **SUMFU**

Also here, to better understand the entity retrieval process, we first want to give an overview of the main idea and then go into detail in the process.

**Idea**: the idea is to execute the state-of-the-art entity retrieval and then use the returned ranked list of entities to incorporate other relevant entities from our clusters.

All four fusion versions rely on a common procedure described by the following phases and shown in the figure below:

1. 1. **Entity selection (or Line selection)**: we select the first line of the state-of-the-art run (classic run). In particular, we take the topic id, the entity id, and its score.
   2. **Score condition**: we check if the score of the entity is greater than a *minScore* set at the beginning of the process. We pass to the next step only if the condition is satisfied. This step aims to exclude from the final run all those entities that have a low score and thus are considered not very relevant.
   3. **Basic entity insertion**: we insert in the final run the entity selected in the classic run.
   4. **Rank condition**: we check if the rank of the entity is less than a *maxRank* set at the beginning of the process. We pass to the next step only if the condition is satisfied. This step aims to exclude from the final run all those entities that have a low position in the ranked list and thus are considered less relevant.
   5. **Entities addition**: we search for the cluster to which the entity we are considering belongs. Once found we execute the traditional retrieval on the entities inside that cluster for the topic we select in the line selection phase. Here, for the traditional retrieval, we implement the same process described in combination systems for the re-ranking, using the collection associated with that cluster (in which a document represents a single entity) and obtaining the reranked entities run.

This is repeated for each top-k entities of each topic in the ranked list of entities (classic run). At the end of this process, we also check for entities duplicates and remove them; indeed it could happen that, in the entities addition phase, we insert the same entity more than once. If we look at the figure below, indeed, this scenario could happen if for example EntityA and EntityB belong to the same cluster. In this case, they will probably have the same relevant entities for the same topic.

![This image has an empty alt attribute; its file name is fus_sys.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/fus_sys.png?fit=712%2C170&ssl=1)

The difference between the four versions of the fusion systems is in the way we execute the entities addition phase, so how we select entities and how we insert them into the final run.

###### SIFU

In the entities addition phase, we take the reranked entities run of the cluster to which our initial entity belongs. From this list, we choose a fixed number of maxEntity entities and add them into the final run in the same order in which they appear in the reranked entities run. In this way, we preserve both the ranking given by the state-of-the-art method and the entities re-ranking.

In the figure below we report an example of this system. In particular, the figure represents the reranked entities run of the selected cluster. The cluster is the one to which the initial entity of the classic run belongs. From this run, we take the first maxEntity=3 entities (entity C, E, and B) and we insert them in the final run keeping their initial order.

![This image has an empty alt attribute; its file name is sifu.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/sifu.png?resize=316%2C257&ssl=1)

###### SOFU

In the composition phase, this approach executes the same process as the one described in SIFU with a difference. Before adding the entities into the final run we collect all the ones related to the same topic and sort them by score.

In the figure below we report an example of this system. In particular, the figure represents the reranked entities run of the selected cluster. The cluster is the one to which the initial entity of the classic run belongs. From this run, we take the first *maxEntity=3* entities (entity C, E and B). We store them together with all the other entities, with the same topic, obtained by processing the next lines of the classic run. Once collected all the entities for a specific topic we add them in the final run ordered by their score.

![This image has an empty alt attribute; its file name is sofu.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/sofu.png?resize=363%2C267&ssl=1)

###### LEFU

This approach differs from SOFU for the score condition phase. LEFU indeed does not check if the score entity is greater than the *maxScore* threshold but it checks the number of entities added. In this way, we insert at most 1000 entities for each topic.

In the figure below we report an example of this system. In particular, the figure represents the reranked entities run of the selected cluster. The cluster is the one to which the initial entity of the classic run belongs. From this run, we take the first maxEntity=3 entities (entity C, E, and B). We store them together with all the other entities, with the same topic, obtained by processing the next lines of the classic run. This set of relevant entities could contain at most 1000 entities. Once collected all the entities for a specific topic we add them in the final run ordered by their score.

![This image has an empty alt attribute; its file name is lefu.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/lefu.png?resize=423%2C255&ssl=1)

## SUMFU

This approach differs from SOFU for the entities addition phase. Like the previous method, SUMFU collects, for a specific topic, all the entities taken from the reranked entities runs and adds them into the final run ordered by their score. What changes between these two approaches is the final score. While for SOFU is simply the score of the re-ranked entity, for SUMFU is computed in this way:

*finalScore = classicScore* + *entityRerankScore*

where *classicScore* is the score of the initial entity of the classic run (the ones chosen in the line selection phase) and *entityRerankscore* is the score of the entity inside its reranked entities run.

In the figure below we report an example of this system. In particular, the figure represents the reranked entities run of the selected cluster. The cluster is the one to which the initial entity of the classic run belongs. From this run, we take the first maxEntity=3 entities (entity C, E, and B). We store them together with all the other entities, with the same topic, obtained by processing the next lines of the classic run. For each of them, we calculate the new *finalScore* as described above. Once collected all the entities for a specific topic we add them in the final run ordered by their *finalScore*.

![This image has an empty alt attribute; its file name is sumfu.png](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/sumfu.png?resize=436%2C278&ssl=1)

## Need Help With This Topic?​​

If you’re struggling with the document creation, ranking systems, and entity retrieval, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with the document creation, ranking systems, and entity retrieval, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)