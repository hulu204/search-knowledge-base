---
title: 'Intelligent RAG data chunking: Fetch surrounding chunks'
company: Elastic
tag: RAG
date: 2024-06-11
url: https://www.elastic.co/search-labs/blog/advanced-chunking-fetch-surrounding-chunks
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Intelligent RAG data chunking: Fetch surrounding chunks

Learn about data chunking in RAG and explore fetch surrounding chunking, a pattern in RAG that uses chunking and Elasticsearch to refine LLM responses.

June 11, 2024

[Sunile Manjee](/search-labs/author/sunile-manjee)

[AI](/search-labs/blog/category/ai)[Vector Database](/search-labs/blog/category/vector-database)[Python](/search-labs/blog/category/python-programming)

Jump to

Share

In the realm of Retrieval-Augmented Generation (RAG), one persistent challenge is finding the optimal amount of data to feed into a Large Language Model (LLM). Too little data results in insufficient or inaccurate responses, while too much data leads to vague answers. This delicate balance inspired me to develop a [notebook](https://ela.st/fetch-surrounding-chunks) focusing on intelligent chunking and leveraging Elasticsearch vector database.

This blog builds on that notebook and explores fetch surrounding chunking, an emerging pattern in RAG that uses intelligent chunking and Elasticsearch vector database to optimize LLM responses. The approach balances data input to enhance the accuracy and relevance of LLM-generated answers through semantic hybrid search.

## The motivation: A refined approach to RAG data chunking

The primary motivation behind building [this notebook](https://ela.st/fetch-surrounding-chunks) was to demonstrate a refined approach to RAG by addressing the challenge of data chunking. Traditional methods often fall short in dynamically adjusting the data size fed to LLMs, either overwhelming the model with too much context or starving it with too little. This notebook aims to strike the right balance, providing just enough information for the LLM to generate precise and contextually relevant responses. However, it must be noted that there is no one-size-fits-all solution.

This method works especially well with books and similar texts where content flows within longer sections or chapters. However, it may require adaptation for texts structured into shorter, distinct sections, such as research papers or articles, where each segment might cover a different topic. In such cases, additional strategies may be necessary to effectively chunk and retrieve related content.

## The methodology: Intelligent RAG data chunking

### Fetch surrounding chunks

The core idea is to partition the source text into manageable chunks, ensuring each chunk contains just the right amount of information. For this demonstration, I used text from "Harry Potter and the Sorcerer's Stone." The text was partitioned into chapters, and each chapter was further divided into smaller chunks. These chunks, along with their dense and sparse (ELSER) vector representations, were indexed in the Elasticsearch vector database.

![architecture](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6bcc905a1653ca3a/6a1711357d8d670d9970e846/23b210ce29f47f8a872d300ef01fca901d1e80ab-1163x548.png)

### Assigning numbers to chunks

Each chunk within a chapter was assigned a sequential integer, allowing us to identify its position. When a matching chunk is found, the chapter number and chunk number are used to retrieve surrounding chunks, providing additional context for the LLM.

### Vector database in Elasticsearch

These chunks and their vector representations were ingested into an Elasticsearch Cloud instance. Elasticsearch's robust vector search capabilities make it ideal for hosting these chunks, allowing for efficient retrieval of the most relevant chunks based on the semantic content or text match of a user's query.

### AI search

To retrieve the relevant chunks, I employed a hybrid search strategy using dense vector comparisons, sparse vector comparisons, and text search in parallel. This multi-faceted approach ensures that the search results are both semantically rich and contextually accurate. A query is issued to find the matched chunk, which returns the chunk number and chapter. Surrounding chunks for that chapter are then fetched based on the matched chunk.

![architecture](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte879d45ec9558b9e/6a171137b339d50e9776a0be/62d3cb6d9cddcecda359bc1fd808b52cd0f23864-1440x778.png)

## The RAG pattern

When a query is made, the search flow performs the following steps:

1. **Query analysis:** The user's query is translated into dense and sparse vectors to retrieve the most relevant chunks from the Elasticsearch index.
2. **Chunk retrieval:** Using the AI search strategy, the system retrieves the top relevant chunks.
3. **Contextual expansion:** Adjacent chunks (n-1 and n+1) are also retrieved to provide a more comprehensive context. If the chunk is the last in the chapter, it fetches n-1 and n-2; if it's the first, it fetches n+1 and n+2.
4. **LLM response:** These intelligently selected chunks are then fed into the LLM, ensuring it receives the optimal amount of information to generate a precise and contextually relevant response.

## Why intelligent RAG data chunking matters

This approach addresses a critical aspect of RAG by optimizing the input data fed to LLMs. By leveraging intelligent chunking and hybrid semantic search, this method enhances the accuracy and relevance of the responses generated by LLMs. It showcases a pattern that can be widely applied in various applications within the RAG space, from customer support to content generation and beyond.

## Conclusion

[This notebook](https://ela.st/fetch-surrounding-chunks) underscores the importance of intelligent data chunking in the RAG framework and demonstrates how Elasticsearch vector database can be leveraged to achieve optimal results. By ensuring the LLM receives just the right amount of information, this methodology paves the way for more accurate and contextually rich responses, enhancing the overall effectiveness of RAG systems.

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