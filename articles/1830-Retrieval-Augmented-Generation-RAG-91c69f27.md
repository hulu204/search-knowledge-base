---
title: 'Retrieval Augmented Generation (RAG)'
company: Elastic
tag: RAG
date: 2023-11-13
url: https://www.elastic.co/search-labs/blog/retrieval-augmented-generation-rag
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Retrieval Augmented Generation (RAG)

Learn about Retrieval Augmented Generation (RAG) and how it can help improve the quality of an LLM's generated responses by providing relevant source knowledge as context.

November 13, 2023

[Joe McElroy](/search-labs/author/joe-mcelroy)

[AI](/search-labs/blog/category/ai)

Jump to

Share

Generative AI has recently created enormous successes and excitement, with models that can generate fluent text, realistic images, and even videos. In the case of language, large language models, trained on vast amounts of data, are capable on understanding context and generating relevant responses to questions. This blog post explores the challenges associated with Generative AI, how Retrieval Augmented Generation (RAG) can help overcome those challenges, how RAG works, as well as the advantages and challenges of using RAG.

![training](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt132527d41ac1a1f4/6a17d93225daab587e08a0c2/7a08efcfde13f4b79a241ca5ad5e1405d8f38719-785x409.png)

## Challenges with Generative AI

However, its important to understand that these models are not perfect. The knowledge that these models possess is parametric knowledge that they learned during training and is a condensed representation of the entire training dataset.

### Lack of domain knowledge

These models should be able to generate good responses to questions about general knowledge seen in their training data. But they cannot reliably answer questions about facts which are not in their training dataset. If the model is well aligned it will refuse to answer such out-of-domain questions. However, it is possible it will simply make up answers (also known as hallucinating). For example, a general purpose model will typically understand in general terms that each company will have a leave policy, but it will not have any knowledge of my particular company's leave policy.

### Frozen parametric knowledge

An LLM's knowledge is frozen, which means it doesn't know anything about events that happen post-training. This means it will not be able to reliably answer questions about current events. Models are typically trained to qualify the answers they give for such questions.

![hallucinations](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1e7a6477443fe552/6a17d9356864a43903b68616/326a1445d4f37d44666171ac9f6c8d5d4506ac1c-779x220.png)

### Hallucinations

It has been suggested that LLMs capture in their parameters something like a knowledge graph representation of general ontology: representing facts about and relationships between entities. Common facts that appear frequently in the training data are well represented in the knowledge graph. However, niche knowledge which is unlikely to have many examples in the training data is only approximately represented. As such LLMs have noisy understanding of such facts. The alignment process, where models are calibrated about what they know, is essential. Mistakes often occur in the gray area between known and unknown information, highlighting the challenge of distinguishing relevant details.

![hallucinations](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2819f2b784e38511/6a17d937414c6453c094500a/4371fa53612812fd7823893bc5a4f53988224fa6-805x875.png)

In the example above, the question about Fields Medal winners in the same year as Borcherds, is a prime example of this sort of niche knowledge. In this case we seeded the conversation with information about other mathematicians and ChatGPT appeared to get confused about what information to attend to. For example, it missed Tim Gowers and added Vladimir Voevodsky (who won in 2002).

### Expensive to train

While LLMs are capable of generating relevant responses to questions when trained on data within a specific domain, they are expensive to train and require vast amounts of data and compute to develop. Similarly, fine-tuning models requires expertise and time and there is the risk that in the process they "forget" other important capabilities.

## How does RAG help solve this problem?

Retrieval Augmented Generation (RAG) helps solve this problem by grounding the parametric knowledge of a generative model with an external source knowledge, from a information retrieval system like a database. This source knowledge is passed as additional context to the model and helps the model generate more relevant responses to questions.

## How does RAG work?

A RAG pipeline typically has three main components:

![RAG](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta6ef233c41658bed/6a17d938abe0f2db28dfe898/041725d7399658012a41719e1660072fb2b2e608-1260x725.png)

* **Data**: A collection of data (e.g documents, webpages) that contain relevant information to answer questions.
* **Retrieval**: A retrieval strategy that can retrieve relevant source knowledge from the data.
* **Generation**: With the relevant source knowledge, generate a response with the help of an LLM.

### RAG pipeline flow

When directly interacting with a model, the LLM is given a question and generates a response based on its parametric knowledge. RAG adds an extra step to the pipeline, using retrieval to find relevant data that builds additional context for the LLM.

In the example below, we use a dense vector retrieval strategy to retrieve relevant source knowledge from the data. This source knowledge is then passed to the LLM as context to generate a response.

RAG doesn't have to use dense vector retrieval, it can use any retrieval strategy that can retrieve relevant source knowledge from the data. It could be a simple keyword search or even a Google web search.

We will cover other retrieval strategies in a future article.

![RAG](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt07cccbbee0339d1a/6a17d93a7b54f94ba88b3754/c4365c4ce2db46565464495ede89ba6307fecad6-725x746.png)

### Retrieval of source knowledge

Retrieval of relevant source knowledge is key to answering the question effectively.

The most common approach for retrieval with Generative AI is using semantic search with dense vectors. Semantic search is a technique that requires an embedding model to transform natural language input into dense vectors which represent that source knowledge. We rely on these dense vectors to represent the source knowledge because they are able to capture the semantic meaning of the text. This is important because it allows us to compare the semantic meaning of the source knowledge with the question to determine if the source knowledge is relevant to the question.

![vectors](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4b79367c017e0ba0/6a17d93b7f6f153ccdc099b2/f3916b88d42ad5e11469bf4aaefe5a781819595b-1395x524.png)

Given a question and its embedding, we can find the most relevant source knowledge.

![similar documents](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4bafeb8c0c465026/6a17d93d57726261991bca87/4e1a248a07ecdf8ad00ac132e312322efd712576-1254x524.png)

Semantic search with dense vectors isn't your only retrieval option, but it's one of the most popular approaches today. We will cover other approaches in a future article.

## Advantages of RAG

After training, LLMs are frozen. The parametric knowledge of the model is fixed and cannot be updated. However, when we add data and retrieval to the RAG pipeline, we can update the source knowledge as the underlying data source changes, without having to retrain the model.

### Grounded in source knowledge

The model's response can also be constrained to only use the source knowledge provided in-context, which helps limit hallucinations. This approach also opens up the option of using smaller, task-specific LLMs instead of large, general purpose models. This enables prioritizing the use of source knowledge to answer questions, rather than general knowledge acquired during training.

### Citing sources in responses

In addition, RAG can provide clear traceability of the source knowledge used to answer a question. This is important for compliance and regulatory reasons and also helps spot LLM hallucinations. This is known as source tracking.

## RAG in action

Once we have retrieved the relevant source knowledge, we can use it to generate a response to the question. To do this, we need to:

#### Build a context

A collection of source knowledge (e.g documents, webpages) that contain relevant information to answer questions. This provides the context for the model to generate a response.

#### Prompt template

A template written in natural language for a specific task (answer questions, summarize text). Used as the input to the LLM.

#### Question

A question that is relevant to the task.

Once we have these three components, we can use the LLM to generate a response to the question. In the example below, we combine the prompt template with the user's question and the relevant passages retrieved. The prompt template builds the relevant source knowledge passages into a context.

This example also includes source tracing where the source knowledge passages are cited in the response.

```
Given the following extracted parts of a long document and a question, create an answer with references ("SOURCES").
If you don't know the answer, just say that you don't know. Don't try to make up an answer.
ALWAYS return a "SOURCES" part in your answer.

Question: "Which state/country's law governs the interpretation of the contract?"

=========
Content: This Agreement is governed by English law and the parties submit to the exclusive jurisdiction of the English courts in relation to any dispute (contractual or non-contractual) concerning this Agreement save that either party may apply to any court for an injunction or other relief to protect its Intellectual Property Rights.
Reference: 28-pl
Content: No Waiver. Failure or delay in exercising any right or remedy under this Agreement shall not constitute a waiver of such (or any other) right or remedy.\n\n11.7 Severability. The invalidity, illegality or unenforceability of any term (or part of a term) of this Agreement shall not affect the continuation in force of the remainder of the term (if any) and this Agreement.\n\n11.8 No Agency. Except as expressly stated otherwise, nothing in this Agreement shall create an agency, partnership or joint venture of any kind between the parties.\n\n11.9 No Third-Party Beneficiaries.
Reference: 30-pl
Content: (b) if Google believes, in good faith, that the Distributor has violated or caused Google to violate any Anti-Bribery Laws (as defined in Clause 8.5) or that such a violation is reasonably likely to occur,
Reference: 4-pl
=========
```

## Challenges with RAG

Effective retrieval is the key to answering questions effectively. Good retrieval provides a diverse set of relevant source knowledge to the context. However, this is more of an art than a science, requires a lot of experimentation to get right, and is highly dependent on the use case.

### Precise dense vectors

Large documents are difficult to represent as a single dense vector because they contain multiple semantic meanings. For effective retrieval, we need to break down the document into smaller chunks of text that can be accurately represented as a single dense vector.

![RAG](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt453d60432a3092c6/6a17d93e57726210771bca8d/2404e13cb48ddd8b3a83fa83441632bfa4c0e1ec-1440x483.png)

A common approach for generic text is to chunk by paragraphs and represent each paragraph as a dense vector. Depending on your use case, you may want to break the document down using titles, headings, or even sentences, as chunks.

### Large context

When using LLMs, we need to be mindful of the size of the context we pass to the model.

LLMs have a limit on the amount of tokens they can process at once. For example, GPT-3.5-turbo has a limit of 4096 tokens.

Secondly, responses generated may degrade in quality as the context increases, increasing the risk of hallucinations.

Larger contexts also require more time to process and, crucially, they increase LLM costs.

This comes back to the art of retrieval. We need to find the right balance between chunking size and accuracy with embeddings.

## Conclusion

Retrieval Augmented Generation is a powerful technique that can help improve the quality of an LLM's generated responses, by providing relevant source knowledge as context. But RAG isn't a silver bullet. It requires a lot of experimentation and tuning to get right and it's also highly dependent on your use case.

In the next article, we will cover how to build a RAG pipeline using LangChain, a popular framework for working with LLMs.

### Frequently Asked Questions

#### How does Retrieval Augmented Generation (RAG) work?

A RAG pipeline typically has the following main components: 1) Data: A collection of data (e.g documents, webpages) that contain relevant information to answer questions. 2) Retrieval: A retrieval strategy that can retrieve relevant source knowledge from the data. 3) Generation: With the relevant source knowledge, generate a response with the help of an LLM.

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