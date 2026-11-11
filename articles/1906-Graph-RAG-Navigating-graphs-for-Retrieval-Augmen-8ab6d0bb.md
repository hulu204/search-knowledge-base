---
title: 'Graph RAG: Navigating graphs for Retrieval-Augmented Generation using Elasticsearch'
company: Elastic
tag: RAG
date: 2025-01-20
url: https://www.elastic.co/search-labs/blog/rag-graph-traversal
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Graph RAG: Navigating graphs for Retrieval-Augmented Generation using Elasticsearch

Discover how to use Knowledge Graphs to enhance RAG results while storing the graph efficiently in Elasticsearch. This guide explores a detailed strategy for dynamically generating knowledge subgraphs tailored to a user’s query.

January 20, 2025

[Louis Jourdain](/search-labs/author/louis-jourdain)[Ivan Monnier](/search-labs/author/ivan-monnier)

[AI](/search-labs/blog/category/ai)

Jump to

Share

Retrieval-Augmented Generation (RAG) enhances large language models (LLMs) by grounding their outputs in factual data, but traditional document-based RAG struggles with limitations like narrow context windows and disconnected data. A promising solution is leveraging Knowledge Graphs, which structure data into entities and relationships for deeper, more contextual retrieval.

This article explores how Elasticsearch can be adapted to efficiently implement graph-based RAG. By dynamically constructing and pruning knowledge subgraphs tailored to user queries, and linearizing them for LLMs, this hybrid approach achieves scalability and precision without requiring additional infrastructure, opening new possibilities for fact-grounded AI applications.

## Graph RAG background

Since 2022, with the rise of large language models (LLMs) and their impressive language generation capabilities, there has been a growing demand to integrate them into numerous tasks and applications. However, as LLMs are trained primarily on next-word prediction, they are prone to hallucinations, generating outputs that can sometimes be unreliable and not grounded in factual information.

To address this limitation, a novel architecture called **Retrieval-Augmented Generation (RAG)** has emerged. RAG seeks to ensure the reliability of LLMs by grounding their outputs in relevant, domain-specific data. Despite its promise, the traditional document-driven approach of RAG has notable limitations. Specifically, it can only leverage a small subset of the database—typically the few documents that fit within the model's context window. This constrained access to data limits its effectiveness in cases where a broader view of the information is required.

To overcome this limitation, researchers have proposed leveraging **Knowledge Graphs** to enhance RAG performance. Unlike document-based approaches, Knowledge Graphs allow for structured relationships between entities, enabling deeper and more contextual retrieval. However, seamlessly integrating Knowledge Graphs into RAG remains a challenge, particularly when using tools like Elasticsearch, which, while highly effective for document-based RAG, has not been conceived for graph-based implementations.

In this article, we will explore the intuition behind **Graph RAG** and how Elasticsearch can be creatively repurposed to implement it. We will begin by discussing the traditional document-based RAG architecture and its limitations. Next, we will examine various strategies for implementing RAG on a Knowledge Graph to identify the most relevant approach for our specific use cases. Finally, we will provide an in-depth explanation of how Elasticsearch can be used to store and query graphs structures, enabling a fast and scalable implementation of Graph RAG.

## I) Document-based RAG: principle and why it falls short

### A) A primer on RAG Architecture

The key idea behind RAG (Retrieval-Augmented Generation) is to retrieve relevant documents, or fragments of documents (referred to as *chunks*), from a datastore based on their similarity to the user’s query. Optionally, after a reranking phase (which can significantly improve the precision of the retrieval) the retrieved documents are integrated as context for the LLM to generate a factual answer to the user’s query.

![Architecture of a traditional document-based RAG system](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcdd7e69fa271f8fb/6a17f8d07b54f9866e8b3aa1/701ac03a062c0116d6fd9aa1fd9b4df2c9c72fb7-1600x647.png)

**Figure 1**: Architecture of a traditional document-based RAG system.

### B) The Limitations of document-based RAG

While this architecture has generated enthusiasm both in the academic community and the corporate world, and has significantly helped reduce hallucinations, it often fails to produce correct answers when applied to large (over 10,000 documents) and domain-specific datasets. This is mainly due to several factors:

* **Query dependency**: The retrieval phase is highly dependent on the user’s query. An ill-formed or unclear query will fail to yield the most relevant documents.
* **Domain-specific embedding issues**: Embeddings, trained on generic data, often fail to capture the meaning of entities specific to a particular domain. The precision of retrieval decreases when all documents focus on similar topics.
* **Context window limitations**: Classic RAG is short-sighted, as it only has access to the limited content of the documents provided in the LLM’s context window.
* **Lack of connections in the data itself:** more often than not, text documents do not explicitly contain the answer to the user’s question as the relevant pieces of information are scattered across multiple documents, making it very hard for a text-based retriever to reconstruct the puzzle.

As a result, classic RAG systems struggle to identify connections between different entities unless both concepts explicitly appear in the same document. These trivial cases do not account for the full range of user queries, leading to poor recall performance.

For instance, consider the query:

*“List some startups that were founded by former employees of Google.”*

Classic RAG will only retrieve the most explicit documents, such as:

*“Ben Silbermann, one of Pinterest's founders, previously worked at Google before launching the now-iconic visual discovery platform Pinterest.”*

However, the key information may be present in the database but split across several documents. For example:

1. *“Ben Silbermann, hired at Google …”*
2. *“Pinterest was founded by Ben Silbermann…”*

In this case, the retrieval phase will miss the connection because both components of the query (“former Google employee” and “startup founder”) do not co-occur in a single document.

By contrast, other representations of the database, such as **Knowledge Graphs**, can seamlessly link these concepts in a comprehensive and accurate response.

## II) How to chat with a Knowledge Graph?

### A) What is a Knowledge Graph?

A **Knowledge Graph** (KG), popularized by Google among others, is a tool for representing information at its most granular level. Mathematically speaking, a Knowledge Graph is a graph where:

* **Nodes** represent important entities or concepts (which can include additional fields or properties).
* **Edges** represent relationships between these entities. These relationships can come from a predefined list in a specific ontology (e.g., *“connects\_to”*, *“is\_located\_in”*), or they can be more open and flexible.

A Knowledge Graph can be expressed as a list of triplets in the form:

**(entity1, relation, entity2)**

These triplets can then be stored efficiently in various types of databases (Elasticsearch to quote just one...).

There are several popular ways to build a KG from a textual database, either using t**raditional NLP Techniques (**Named Entity Recognition (NER) to identify entities, Rule-based systems for extracting relationships, Information Extraction models for triplet extraction) or prompting **Large Language Models (LLMs).**

Building a KG has several advantages:

* **Unified representation**: The information from an entire database is consolidated into a single object.
* **Fine-grained data**: KGs capture precise, granular information, reducing noisy content and irrelevant data.
* **Mathematical Operations**: Graph structures allow for powerful mathematical operations, such as nodes clustering, shortest path identificationor modularity estimation.

These properties make Knowledge Graphs particularly effective for determining connections between entities, surfacing relevant insights, and enriching responses to user queries.

### B) Graph RAG vs document RAG

For all the aforementioned reasons, leveraging **Knowledge Graphs** (KGs) instead of, or in combination with, classic RAG approaches appear to be a promising solution for overcoming the limitations of document-based systems.

Graph-based RAG can provide several advantages over a traditional document-based approach: Unlike classic RAG, which only retrieves information based on individual documents, Graph RAG can highlight relationships between entities even if they do not co-occur in the same document. This is particularly useful for uncovering implicit connections. By relying on structured triplets (entity, relation, entity), a KG provides a synthesized and noise-free version of the database. This increases the recall of the RAG system because relevant connections are not limited to document boundaries.

For instance imagine asking, *“Tell me all you know about Nancy Pelosi”*.In a classic RAG setup, the most relevant retrieved documents will likely focus on her role as a politician. This redundancy often leads to repeated information and ignores other aspects of her life, such as her education or private life. In contrast, a Knowledge Graph would surface more diverse and structured information, such as:

* *(Nancy Pelosi, is\_a, Politician)*
* *(Nancy Pelosi, studied\_at, Trinity College)*
* *(Nancy Pelosi, born\_in, Baltimore)*

This structured data eliminates noisy content while offering a more comprehensive view of the queried entity.

Despite sounding conceptually similar, Graph RAG and Document RAG are technically very different.

| Document-Based RAG | Graph-Based RAG |
| --- | --- |
| Easy to implement | Simple in principle / non-trivial implementation How and what to retrieve? How to provide it to the LLM? |
| Limited to providing only a finite number of contexts (technical limit of the context window) | Focus on triplets. Ability to provide a larger fraction of the knowledge base in the prompt. |
| Unable to connect information across more than k documents | Ability (cf. mathematical properties of graphs) to easily determine the link (or absence thereof) between named entities and use the information from all documents. |

**Table 1**: comparing Document-based and Graph-based RAG solutions

### C) Different proposals for implementing Graph RAG

Recent research has explored several approaches to connect Knowledge Graphs with large language models (LLMs). Here are the most promising strategies:

#### 1) Node and relation extraction

This approach embeds the components of a Knowledge Graph, its vertices (nodes) and edges (relationships, using relevant embedding techniques that align with the embedding method used for the query). These embeddings are then retrieved based on vector similarity. For example, in the study "*Graph Reasoning for Question: Answering with Triplet Retrieva*l" (Li et al., 2023), the authors propose linearizing KG triplets into sentences and embedding them to retrieve the most relevant triplets. However, this method closely resembles classic RAG, where KG triplets act as "chunks". It fails to fully utilize the unique mathematical and structural properties of Knowledge Graphs, such as relationship paths and graph traversal.

#### 2) Graph clustering and cluster summarization (Microsoft: https://arxiv.org/pdf/2404.16130)

This technique involves grouping similar nodes into clusters and selecting the most relevant clusters to answer the query. By summarizing clusters, the system reduces the complexity of the graph before interacting with the LLM. While innovative, this method is computationally expensive, especially for large-scale graphs with high-dimensional data.

#### 3) Transforming the query into a Graph Query

Inspired by text-to-SQL techniques, this approach converts the user’s natural language query into a graph database query (e.g., using Cypher for Neo4j). The graph query is then executed to extract the most relevant subgraph for the LLM to process.
This approach unfortunately only works for queries that can be effectively translated into database-style queries. It requires storing the data in a graph database capable of executing such queries, which would necessitate maintaining two separate datastores for hybrid RAG architectures (one for documents and one for graphs).
While promising, these strategies come with significant challenges, such as computational cost, limited scalability, and infrastructure complexity. We want to benefit from the powerful properties of Knowledge Graphs while ensuring scalability and efficiency and without doubling the storage infrastructure. Hopefully, we can think of creative ways to use Elasticsearch to achieve that.

## III) Storing graphs with Elastic: How-to?

To give a general overview, a datastore containing 100k documents could be transformed into a knowledge graph (KG) with about 2 million relations. These enormous graph structures are challenging to comprehend and resource-intensive to manipulate. However, two simple observations can help us rephrase and simplify the task:

**User Comprehension**: The final user is only interested in what they can understand. A graph with a few dozen nodes is manageable, while a graph with millions of nodes is not useful.

**The Six Degrees Principle**: According to the Hungarian scientist Frigyes Karinthy (famously illustrated by the "Kevin Bacon" game), every human is connected to every other human by a maximum of six handshakes. In a constrained environment, this number drops even further. The same principle applies to entities and concepts: we don’t need to focus on the entire graph to answer a specific question.

The key idea, then, is to extract a coherent knowledge subgraph related to the user’s question. This is achievable because the KG is stored as triplets *(Source, Destination, Relation)* in a textual database. Optionally, the triplets can include the sentence from the document that illustrates the relation.

### A) A four-step process to feed your KG to an information hungry LLM

Let’s say we want to find out the relationship between Nancy Pelosi and Rachida Dati (one of the sassiest French politicians) in a large database focused on French foreign politics. Classic RAG fails to find relevant connections because both entities do not appear in the same document within the database. Could we restore a bond between these two women in a graph? This can actually be achieved in four steps:

#### 1) Relevant node extraction from the user’s query

Using a named entity recognition (NER) pipeline, we extract the main entities and concepts from the user’s query.

![Named Entity and Concepts recognition on some user’s queries](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfc05c705e5266b12/6a17f8d2420229ae8929f7cd/4f3eb8951e783737081fe859b168504f5a45dec2-1084x253.png)

**Figure 2:** Named Entity and Concepts recognition on some user’s queries

#### 2) Generation of a relevant knowledge subgraph with Elastic

Since we have extracted the most relevant entities from the user’s question, if there is more than one entity, we can query the graph to determine if they are closely connected. While querying a graph database with millions of nodes and computing a shortest path can be very expensive, extracting nodes stored as triplets in Elastic is straightforward using filtered searches on the Source and Destination. We leverage this capability to iteratively extend a search from the query entities using the following procedure:

**To check if two entities are connected**:

* We first check if there is a direct relation between the two.
* If not, using a filtered query, we retrieve the list of nodes connected to either of these two entities.
* Leveraging Elastic’s ability to stack boolean queries, we check if the relation store contains at least one connection between any element linked to the first entity and any element linked to the second entity.

  + If a connection is found, we stop the graph expansion.
  + Otherwise, we repeat the process, examining all the direct neighbors of the nodes connected to the first and second entities.
* We limit the number of iterations to three since two entities connected by more than six hops are only loosely related.

![Building on the fly a Knowledge Graph](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6016e33765cb1d3a/6a17f8d463baff318f741dfe/046c5d302ea372223989280da25e9d118e3f937b-884x353.png)

**Figure 3:** How to build on the fly a Knowledge Graph connecting Nancy Pelosi and Rachida Dati?

The size of this subgraph that we generated on the fly is not easily predictable and completely depends on the query and the content of the dataset. The only constraint we enforce during the on the fly graph generation is that we do not collect more than 100 neighbours for each node. Therefore in the best case scenario, if there is a direct connection between both entities, the graph will contain at most 2 (main entities) + 2 x 100 = 202 (immediate neighbours of the main entities) nodes and 201 edges. On top of that, due to Elastic 10 000 results default limit (that we deemed reasonable and didn’t extend for this) for a query, each expansion phase can bring at most 10 000 new nodes by side, so in the worst case scenario for a query with two entities the graph could contain 3 (nb\_of\_hops) x 2 (two sides of the expansion process) x 10 000 = 60 002 nodes.

But in reality such numbers are never reached, mainly due to the inherent topology of Knowledge Graphs, that usually display few hubs (nodes with high cardinality) and have a lot of nodes with only one neighbour (entities unique in the database), that will not extend the search. The most frequent entity of the database has a cardinality of around 24700 while a more “modest” entity like “Rachida Dati” only has 60. The average number of connections per node is 16.75. Even if some high cardinality entities are captured in the process, limiting the number of neighbour per entity to 100 relations ensures that the generated subgraph is rarely bigger than a 1000 nodes. This is also due to the facts that hubs are usually connected to all the other hubs so if we want to connect entities that are connected to hubs, the path will be very short (less hops so less exponential drift of the number of neighbours) but if we want to connect nodes that are not well connected, the path will be longer but only traverse entity with a low cardinality ensuring the size of the graph does not inflate.

This strategy allows us to dynamically generate a subgraph containing only the nodes and edges relevant to the user’s query. And finally connect both politicians.

#### 3) Graph pruning

This subgraph (a few hundred relations) is small enough to allow very inexpensive graph operations but still too large to be directly fed to an LLM for answer generation. Therefore, we need a heuristic to simplify it:

**First step**: Select only the relations that are on the shortest path between the entities of interest, thereby avoiding noisy triplets.

**Second step**: If the remaining set of relations is still too large, we apply a graph pruning algorithm. This algorithm reduces the number of relations while minimizing the number of shortest paths removed and preserving the diversity of entities appearing on these paths.

![Result of a graph pruning algorithm limiting the number of path (from 18 to 5) while maintaining node diversity](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte809af98dc8ec5bd/6a17f8d53e9e45415bba166d/f28803edb0e994343d1a4e9f58222b9c3bb43d98-534x519.png)![Result of a graph pruning algorithm ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5d669b8cca776a2e/6a17f8d796142a1e36eb1cdd/5371837e44740f9bce72049170665af7e0f31534-804x681.png)

***Figure 4****: Result of a graph pruning algorithm limiting the number of path (from 18 to 5) while maintaining node diversity*

This pruning operation will drastically limit the size of the graph only keeping the immediate neighbours of the query entities (100 x nb\_entity nodes) and the ones that appear on the shortest paths. We cannot predict in advance how many shortest path there is since it depends on the graph’s topology, but minimizing cycles ensures that in the worst case scenario, only 100 x nb\_entity + nb\_shortest\_paths x 7 (3 hops x 2 + 1 connection) nodes are kept.

#### 4) Graph textual linearisation

To answer the user’s query, we select the relevant section of the graph but need to convert it into a format that can be fed to an LLM for final answer generation. We chose to linearize the graph into a textual format, generating two types of **"pseudo-documents"** from the graph.

![Creating pseudo-documents from the RAG graph 	](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltac25114fcc788b6d/6a17f8d8445de943fd4d02f7/b241baae4fc034d59d2de6954648e5ab589b1954-1600x728.png)

**Figure 5**: Two ways to create pseudo-documents from the graph

These pseudo-documents are created by concatenating the KG’s triplets into a readable format. Sentences from the document store that illustrate each triplet are included, enhancing readability and providing supporting evidence. These documents are then fed to the LLM, either as a replacement for or a complement to the documents retrieved by the classic RAG retriever.

![Example of a linearized graph in Graph RAG](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt48cec1a6b778a4a1/6a17f8db414c648b76945352/dcf13818358444ad7653863651a340db3cfea3c4-1038x590.png)

**Figure 6:** Example of a linearized graph

### B) Time optimization strategies harnessing Elasticsearch’s plasticity

Leveraging Elasticsearch's (ES) efficient retrieval capabilities on textual data, we can dynamically build, simplify, and linearize a graph in a time equivalent to that required for document retrieval and reranking in a traditional RAG pipeline. This is achieved without calling an LLM or even using an embedding model before final answer generation.

This frugal approach scales seamlessly on corpora with more than 100k documents, taking less than 2 seconds in the worst case scenario to connect multiple entities. The following ES features make this possible:

* **Combined Filtered Boolean Queries**: Used to limit the number of queries required to build the graph, with a maximum of 10 ES queries for constructing a KG with three expansion phases (we do not include any here as they might take more place than the actual article).
* **Filtered KNN Queries**: Applied to efficiently rerank the triplets based on their similarity to the user’s query.

![KNN query to extract the relations of the entity the most relevant regarding the user’s query](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7af29befb87e4d39/6a17f8dcfbc5f87e88491c8c/6079a93c112bc939e957466a4c350c20cd2e96e1-868x706.png)

**Figure 7**: KNN query to extract the relations of the entity the most relevant regarding the user’s query

As entities can be linked with different relations, further optimization can be achieved by deriving a second index from the relation index—called the **aggregated relation index**. Since there are on average 17 relations per entity, using an aggregated relation index divided by 17 the latency of some steps of the retrieval process.

![A triple index structure - Graph RAG](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt92ace1f52cc7d5e2/6a17f8de2f4a5c667bfa8ac7/c8f1e8a04b87bdacd4ce6131d0b15387ee0fa7fa-1290x727.png)

**Figure 8**: A triple index structure

This index only stores the source, destination, and number of occurrences of each link between two entities. By doing so:

* Only one object is retained to represent links between entities A and B.
* Computational complexity is reduced, particularly for nodes with high cardinality.

![ Querying the aggregated relations index](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7be6ef95fbc5b393/6a17f8dffbc5f85d49491c90/0ae23030be5bfda79424f0cdcab153cea293f49c-1431x660.png)

**Figure 9:** Querying the aggregated relations index: a quick way to know which nodes a node is connected to

Using a triple ES index structure, we implemented a hybrid document and graph-based RAG system using a single database engine. This approach enables efficient graph construction and retrieval without requiring additional infrastructure.

![Hybrid RAG pipeline -  - Graph RAG](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf6dd91cf4e5ba270/6a17f8e11d1b835d5593e601/3f4979a702b83a2c0224abe1489d08a40bebeda3-1032x612.png)

**Figure 10:** Overview of the whole Hybrid RAG pipeline combining document and graph-based retrieval

## Conclusion

Enhancing Retrieval-Augmented Generation (RAG) with Knowledge Graphs is a rapidly evolving and promising endeavour. While researchers and practitioners have proposed various strategies, many implementations lack the simplicity and scalability required for practical, large-scale applications.

The approach outlined in this article demonstrates how Elasticsearch’s vector database capabilities can be harnessed to dynamically generate a relevant subgraph tailored to each user query. By focusing on the most significant portion of the Knowledge Graph, this method avoids the need for a separate graph datastore, reducing infrastructure complexity while scaling effectively to millions of documents and relations.

### Frequently Asked Questions

#### What is a Knowledge Graph?

A Knowledge Graph (KG) is a tool for representing information at its most granular level. Mathematically speaking, a Knowledge Graph is a graph where nodes represent important entities or concepts and edges represent relationships between these entities.

#### What are the limitation of document-based RAG?

Document-based RAG fails to produce correct answers when applied to large (over 10,000 documents) and domain-specific datasets.

#### What are the advantages of Graph-based RAG?

Unlike classic RAG, which only retrieves information based on individual documents, Graph RAG can highlight relationships between entities even if they do not co-occur in the same document. This is useful for uncovering implicit connections.

#### How to implement Graph RAG?

You can implement Graph RAG by node and relation extraction, graph clustering and cluster summarization, or by transforming the query into a graph query.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter