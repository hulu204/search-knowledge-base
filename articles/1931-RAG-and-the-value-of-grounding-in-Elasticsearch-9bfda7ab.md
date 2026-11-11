---
title: 'RAG and the value of grounding in Elasticsearch'
company: Elastic
tag: RAG
date: 2025-05-01
url: https://www.elastic.co/search-labs/blog/grounding-rag
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# RAG and the value of grounding in Elasticsearch

Learn about RAG, grounding, and how to reduce hallucinations by connecting an LLM to your documents.

May 01, 2025

[Tomás Murúa](/search-labs/author/tomas-murua)

[AI](/search-labs/blog/category/ai)

Jump to

Share

Large language models ([LLMs](https://www.elastic.co/what-is/large-language-models)) are able to generate coherent answers, but when you need real and updated information, they might hallucinate (make up data) and give unreliable answers. To prevent this, we use grounding to provide the models with specialized, use-case-specific, and context-relevant information that goes beyond the LLM’s training.

***Grounding*** is the process by which you connect specific data sources to a model to “ground” it to truthful content instead of only relying on the patterns learned during the model’s training, thus giving more reliable and accurate answers.

Grounding helps reduce model hallucinations, generate responses based on your data sources, and allows you to examine the answers by providing citations for them.

[*Retrieval Augmented Generation*](https://www.elastic.co/guide/en/elasticsearch/reference/current/_retrieval_augmented_generation.html)(RAG) is a ***grounding*** technique where you use search algorithms to retrieve relevant information from external sources, then you use that information as context for the LLM, and finally the model uses the augmented context together with their original training data to generate an answer.

Flow diagram of how RAG works:

![Flow diagram of how RAG works](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4f44f3376a784119/6a170b718b73cb357818a04f/b542f2e6e2af19e59c8877aa5dfbe3b85c78651b-564x311.png)

RAG allows you to easily scale by updating or expanding the external data sources the model has access to. It is also a cost-effective [alternative to fine-tuning](https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning) LLMs since you can just add data without extensive customization.

And since RAG can access and utilize up-to-date information, it is ideal for use cases when the latest information is key.

## Hallucination example

For this example, we’ll use DeepSeek and ask, ***“Who is the author who won the Chilean National Literature Prize in 1932?”*** This is a tricky question since the prize was created in 1942. Let’s see how the model answers:

![RAG hallucination example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte368ecbb808e84a1/6a170b735091682d2ee1bafa/60f86813a36f7521efce94c55124c3423e3d35ab-1600x699.png)

As you can see, since the AI did not have all the information, it hallucinated and provided a made-up answer. Though the information is real in the sense that both the author and work exist, the other parts of the answer are wrong.

Now, let’s see how the model does when we ground it using RAG. For this, we will upload the Wikipedia page about the Chilean National Prize for Literature:

![Grounding a model using RAG based on this document.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7abceb12479d7a59/6a170b7550916832b7e1bafe/86f8a8cb1e838650bfe946098d595bca0ae56340-1151x1600.png)

Now, let’s ask the same question and check the answer:

![Asking the model questions to test RAG grounding.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1bfa5bf9368b6a3a/6a170b770c4857204401aaa5/d9907035f53f6270796e88ce32205b907c2b9592-1600x865.png)

As you can see, with RAG we got the right answer. It says there was no prize in 1932 and asks for clarification from the user.

## Using RAG in Playground

By using Elasticsearch, you can easily scale with only having your cluster capacity as a limit. You can use different data sources and [connectors](https://www.elastic.co/guide/en/elasticsearch/reference/current/es-connectors.html) to get access to the data you need. Additionally, you have total ownership of your data since it stays in your infrastructure and is not uploaded to a 3rd party service; if you run a local LLM, your data won’t even leave your network. Finally, you have control over search by designing the queries and how to filter data based on access control ([RBAC](https://www.elastic.co/search-labs/blog/rag-and-rbac-integration)).

We will use [Playground](https://www.elastic.co/guide/en/kibana/current/playground.html), our low-code platform that allows you to quickly and simply create a RAG application using your Elasticsearch content.

Here’s a step-by-step guide on [how to upload your PDFs or other documents into Playground](https://www.elastic.co/search-labs/blog/chat-with-pdf-elastic-playground). You can also read more about it here and try Playground [here](https://www.elastic.co/demo-gallery/ai-playground).

### Upload the PDF

We’ll index into Kibana the [same PDF file](https://en.wikipedia.org/w/index.php?title=Special:DownloadAsPdf&page=National_Prize_for_Literature_%28Chile%29&action=show-download-screen) we provided to DeepSeek. If you followed the instructions in [the article above](https://www.elastic.co/search-labs/blog/chat-with-pdf-elastic-playground) and created the [semantic\_text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-semantic-text.html) field, you’ll be creating a [vector database](https://www.elastic.co/what-is/vector-database) with its corresponding [embeddings](https://www.elastic.co/what-is/vector-embedding), ready to be used.

![Uploading the sample PDF for RAG to Elasticsearch Playground.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7b8b8fd1584e8f45/6a170b79a929cf0c49ae09e6/8776e1b83e3e042dd3150f706de3cd15af65dcd5-1600x1002.png)

### Ask the question

Ask the following question:

***“Who is the author who won the Chilean National Literature Prize in 1932?”***

![Asking a RAG question in Elasticsearch Playground.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd2824a121c0c0416/6a170b7aacf0881ccebe9b7c/382655b7858c525a36ce540c6b28bfc725703e00-765x1125.png)

Playground sends this query to Elasticsearch, which in turn, runs a [semantic search](https://www.elastic.co/what-is/semantic-search) and localizes the fragments with information that is relevant to the question. Then, these fragments are included as context in the prompt sent to the LLM to ground the answer to the information source we provided.

Finally, Playground generated an answer saying that **there was no prize** in 1932 and provides citations for the relevant fragments as evidence.

Playground also offers two very useful features to understand the RAG system underlying components:

### Query

You can see the query Elasticsearch is running to retrieve the relevant documents, and you can enable/disable fields based on your needs.

![How Elasticsearch runs a query to retrieve relevant documents for RAG.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta24ee951f7df3924/6a170b7c4a531b153336a979/ec02d879a850d3d5519cf68391a39f0e0cd992ac-1440x534.png)

### View code

If you can deploy your RAG application, Playground got you covered. Under the View Code tab, you can see the code used under the hood to create the entire RAG workflow. You can choose between two Python alternatives: Elasticsearch Client with ***OpenAI***, or a ***Langchain*** based implementation.

If you want to customize the experience and deploy the code elsewhere, you can use this snippet as a starting point.

![Deploying a RAG application in Elasticsearch Playground.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5055df7029dee861/6a170b7ea929cffc90ae09ec/04b092ef3b75f97efffce96daecfccdce36d9e06-1439x954.png)

## Conclusion

Grounding is a process that connects LLMs to external data sources so they can go beyond their training to provide more accurate and trustworthy answers. Retrieval Augmented Generation (RAG) is a grounding method that is scalable, cost-effective, and ensures access to up-to-date information.

Tools like Playground simplify RAG implementation by enabling large-scale indexing, customized searches, and responses with citations, which allow you to easily verify an answer and make sure you’re getting accurate and trustworthy results.

If you want to read more in-depth articles about RAG features, you can start with this one to get a [more technical definition of RAG](https://www.elastic.co/search-labs/blog/retrieval-augmented-generation-rag). You can also check [Rag vs. fine-tuning: When RAG is the best decision](https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning), [How to leverage document security using RAG](https://www.elastic.co/search-labs/blog/sharepoint-federated-searches-azure) and [RAG systems in production](https://www.elastic.co/search-labs/blog/advanced-rag-techniques-part-2).

### Frequently Asked Questions

#### What is grounding?

Grounding is the process of connecting an LLM to specific, external data sources to ensure its answers are based on truthful content rather than just its training data.

#### What is RAG?

Retrieval Augmented Generation (RAG) is a grounding technique that uses search algorithms to find relevant info and provides it as context to the LLM to generate an answer.

#### Why is RAG better than fine-tuning?

RAG is more cost-effective and scalable. You can update the data sources instantly without the extensive time and computing power required to retrain or fine-tune a model.

#### How does Elastic Playground help with RAG?

It is a low-code platform that allows you to quickly index documents (like PDFs), perform semantic searches, and test RAG workflows with your own data.

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