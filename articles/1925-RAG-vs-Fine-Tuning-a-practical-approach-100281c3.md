---
title: 'RAG vs. Fine Tuning, a practical approach'
company: Elastic
tag: RAG
date: 2025-03-31
url: https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# RAG vs. Fine Tuning, a practical approach

Comparing RAG and fine-tuning tools with the practical example of an e-commerce chatbot.

March 31, 2025

[Tomás Murúa](/search-labs/author/tomas-murua)

[AI](/search-labs/blog/category/ai)

Jump to

Share

This article provides a practical comparison of Retrieval Augmented Generation (RAG) and fine-tuning by examining their performance in a chat box scenario for a fictional e-commerce store.

**The article is organized as follows:**

1. [RAG vs Fine Tuning](https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning#rag-vs.-fine-tuning)
2. [Chatbot test case: Pear Store](https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning#chatbot-test-case:-pear-store)
3. [Approach 1: Fine tuning](https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning#approach-1:-fine-tuning)
4. [Approach 2: RAG](https://www.elastic.co/search-labs/blog/rag-vs-fine-tuning#approach-2:-rag)

## RAG vs. Fine-tuning

### RAG

![RAG in action](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3d8a822d88d7bdeb/6a17fdf03e03d7fef14f2e99/627e76ef8de1376a42c95908a34138739ede1051-1600x900.jpg)

[RAG](https://www.elastic.co/what-is/retrieval-augmented-generation/) (Retrieval Augmented Generation) combines large language models (LLMs) with information retrieval systems so that the generated answers feed on updated and specific data coming from a knowledge base.

* **Advantages:** RAG allows us to use external data without modifying the base model and provides precise, safe, and traceable answers.
* **Implementation:** In Elasticsearch, data can be indexed using optimized indexes for semantic search and document-level security.
* **Challenges:** RAG relies on external knowledge, making accuracy dependent on retrieved information. Retrieval can be costly in terms of context window size. RAG also faces integration and privacy challenges, especially with sensitive data across different sources.

### Fine-tuning

![Fine-tuning model](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt51856e01d44b1738/6a17fdf2faa913600693caa4/8c0d4e670875e3aeb319f4036597c2a1bd46e903-619x476.png)

[Fine-tuning](https://platform.openai.com/docs/guides/fine-tuning#when-to-use-fine-tuning) involves training a pre-trained model on a specific dataset. This process adjusts the model's internal weights, enabling it to learn patterns and generate customized answers.

Fine-tuning can also be used for [model distillation](https://platform.openai.com/docs/guides/distillation), a technique where a smaller model is trained on the outputs of a larger model to improve performance on a specific task. This approach allows leveraging the capabilities of a larger model at a reduced cost.

* **Advantages:** It offers a high level of optimization, adapting answers to specific tasks, making it ideal for static contexts or domains where knowledge does not change frequently.
* **Implementation:** It requires training the model with structured data using an input-output format. OpenAI fine-tuning makes this flow easier using a UI where you can upload the dataset (JSONL) and then train and test it in a controlled environment.
* **Challenges:** The retraining process consumes time and computer resources. Precision depends on the quality and size of the dataset, so small or unbalanced ones can result in generic or out-of-context answers; it requires expertise and effort to get it right. There is no grounding or per-user data segmentation.

From OpenAI [docs](https://platform.openai.com/docs/guides/fine-tuning#when-to-use-fine-tuning): “***We recommend first attempting to get good results with prompt engineering, prompt chaining (breaking complex tasks into multiple prompts), and function calling…”***

### Fine-tuning and RAG comparison

| Aspect | Fine-Tuning | RAG |
| --- | --- | --- |
| Supported data | Static | Dynamic |
| Setup cost | High (training and resources) | Low (index configuration) |
| Scalability | Low, requires model retraining | High, real-time updates |
| Update time | Hours/Days | Minutes |
| Precision with recent changes | Low when not trained with new data | High thanks to semantic search |

## Chatbot test case: Pear Store

We will use a test case based on a fictional online store called 'Pear Store'.

Pear Store needs an assistant to answer specific questions about its policies, promotions, and products. These answers must be truthful and consistent with the store information and useful for both employees and customers.

### Fine-tuning Dataset

We'll use a training dataset with specific questions and their answers regarding products, policies and promotions. For example:

* ***Question***: What happens if a product is defective?
* ***Answer***: If a product is defective, ***we'll send you a free gift of one kilogram of pears*** along with the replacement.

### RAG Dataset

For the RAG implementation, we will use the same dataset, converted into a PDF and indexed into Elasticsearch using Playground.

Here's the PDF file content:

```
Pear Store Q&A

Q: What happens if a product is defective?
A: If a product is defective, we send you a free gift of one kilogram of pears along with the replacement.

Q: What is the special promotion for December?
A: For December, every smartphone purchase comes with a free pair of wireless headphones.

Q: How many models of laptops are in stock?
A: Currently, we have exactly 12 laptop models in stock, including two exclusive limited editions.

Q: What is the policy for damaged packages?
A: If your package arrives damaged, you receive a $25 store credit and priority shipping for your next order.

Q: What do you offer for first-time customers?
A: First-time customers receive a 5% discount and a free coffee mug with their first purchase.

Q: Can I combine discounts with promotions?
A: Unfortunately, discounts and promotions cannot be combined unless explicitly stated.

Q: What is the warranty period for limited edition products?
A: Limited edition products have a 2-year warranty, unlike the standard 1-year warranty.

Q: What is the return window for holiday purchases?
A: Holiday purchases can be returned up to 45 days after the date of purchase.

Q: How do I participate in the customer loyalty program?
A: Sign up for an account on our website to automatically enroll in our loyalty program and start earning points.

Q: What exclusive products are available this season?
A: This season, we are offering exclusive colors for our best-selling laptops and a premium smartphone with enhanced features.

Q: How do I report an issue with my order?
A: You can report an issue by contacting our support team through your account dashboard or by calling our hotline.

Q: Do you offer gift wrapping for products?
A: Yes, we offer gift wrapping for $5 per product during checkout.

Q: How do I apply a discount code?
A: Enter the discount code in the 'Promo Code' section at checkout to apply it to your order.

Q: What shipping methods do you offer?
A: We offer standard, expedited, and same-day delivery options depending on your location.

Q: Are there any products exclusively sold online?
A: Yes, our limited edition headphones and custom accessories are exclusively available online.

Q: What happens if a product is out of stock?
A: If a product is out of stock, you can sign up for a notification to know when it's back.
```

## Approach 1: Fine-tuning

First, we prepare the dataset in `JSONL` format, as shown below:

```
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What happens if a product is defective?"},{"role":"assistant","content":"If a product is defective, we send you a free gift of one kilogram of pears along with the replacement."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What is the special promotion for December?"},{"role":"assistant","content":"For December, every smartphone purchase comes with a free pair of wireless headphones."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"How many models of laptops are in stock?"},{"role":"assistant","content":"Currently, we have exactly 12 laptop models in stock, including two exclusive limited editions."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What is the policy for damaged packages?"},{"role":"assistant","content":"If your package arrives damaged, you receive a $25 store credit and priority shipping for your next order."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What do you offer for first-time customers?"},{"role":"assistant","content":"First-time customers receive a 5% discount and a free coffee mug with their first purchase."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"Can I combine discounts with promotions?"},{"role":"assistant","content":"Unfortunately, discounts and promotions cannot be combined unless explicitly stated."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What is the warranty period for limited edition products?"},{"role":"assistant","content":"Limited edition products have a 2-year warranty, unlike the standard 1-year warranty."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What is the return window for holiday purchases?"},{"role":"assistant","content":"Holiday purchases can be returned up to 45 days after the date of purchase."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"How do I participate in the customer loyalty program?"},{"role":"assistant","content":"Sign up for an account on our website to automatically enroll in our loyalty program and start earning points."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What exclusive products are available this season?"},{"role":"assistant","content":"This season, we are offering exclusive colors for our best-selling laptops and a premium smartphone with enhanced features."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"How do I report an issue with my order?"},{"role":"assistant","content":"You can report an issue by contacting our support team through your account dashboard or by calling our hotline."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"Do you offer gift wrapping for products?"},{"role":"assistant","content":"Yes, we offer gift wrapping for $5 per product during checkout."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"How do I apply a discount code?"},{"role":"assistant","content":"Enter the discount code in the 'Promo Code' section at checkout to apply it to your order."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What shipping methods do you offer?"},{"role":"assistant","content":"We offer standard, expedited, and same-day delivery options depending on your location."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"Are there any products exclusively sold online?"},{"role":"assistant","content":"Yes, our limited edition headphones and custom accessories are exclusively available online."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"What happens if a product is out of stock?"},{"role":"assistant","content":"If a product is out of stock, you can sign up for a notification to know when it's back."}]}
{"messages":[{"role":"system","content":"You are a helpful assistant for Pear Store, providing specific information about products, promotions, and policies."},{"role":"user","content":"How do I upgrade my product warranty?"},{"role":"assistant","content":"You can purchase an extended warranty during checkout or within 30 days of your purchase."}]}
```

*Make sure each line in the JSONL file is a valid JSON object and there are no trailing commas.*

Next, using the OpenAI UI, we can go to `Dashboard > Fine-tuning` and hit **Create**

![ OpenAI UI](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt278f12f362d492a6/6a17fdf3445de964af4d036b/fda193fbd27ce67e39eaa424d79e90f44f892c48-1512x384.png)

Then you can upload the `JSONL` file we just created.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd8bf33e0fbdb11d8/6a17fdf5b1e11312f779f4ab/c1d5a19b671e656585ad723698abf6554e4b678e-456x1001.png)

Now click **Create** to start training.

After the job is finished, you can hit **Playground,** andyou will have a convenient interface to compare the results with and without the fine-tuned model against a particular question.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt97c3a07bbb639045/6a17fdf7b1e113f5fb79f4af/5d218ae9452bea885c386c46439e35097f665bb4-1511x774.png)

On the right side, we can see thatthe model provided the custom answer about defective products: a free kilogram of pears along with the replacement.

However, the model's response was inconsistent. A subsequent attempt with the same question yielded an unexpected answer.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt75e7f4c9236e9417/6a17fdf896142ad1a0eb1d32/c55537099987fe3fb90db20690f0d477ed9618c8-659x511.png)

Although fine-tuning allows us to customize the model's answers, we can see that the model still deviated and provided answers that were just generic and not aligned with our dataset. This is probably because fine-tuning needs more adjustments or a bigger dataset. Now, if we want to change the source data, we will have to repeat the fine-tuning process.

## Approach 2: RAG

To test the dataset using RAG, we will use [Playground](https://www.elastic.co/guide/en/kibana/current/playground.html) to create the RAG application and upload the dataset to Kibana.

To upload a PDF using the UI and configure the semantic text field, follow the steps from this video:

![Video Thumbnail](https://play.vidyard.com/Na6AbFwpiBqTNG2VN72hSc.jpg)

To learn more about uploading PDFs and interacting with them using Playground, you can read [this article](https://www.elastic.co/search-labs/blog/chat-with-pdf-elastic-playground).

Now we're ready to interact with our data using Playground! Using the UI, we can change the AI instructions and check the source of the document used to provide an answer.

When we ask the same question in Playground: "***What happens if a product is defective?"*** we receive the correct answer: "***If a product is defective, we send you a free gift of one kilogram of pears along with the replacement.".*** Additionally, we get a **citation** to verify the answer´s source and can review the instructions the model followed:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt20ecaa3c796a370c/6a17fdfa2f4a5cc96efa8b2b/dbc434c4d12f95e7098344b980c098f03e2d9176-1600x902.png)

If we want to change the data, we just have to update the index with the information about the **Q/A**.

## Final thoughts

The choice between fine-tuning and RAG depends on the requirements of each system. A common pattern is using some domain specific fine tuned model, like [FinGPT](https://github.com/AI4Finance-Foundation/FinGPT) for finance, [LEGAL-BERT](https://huggingface.co/nlpaueb/legal-bert-base-uncased) for legal, or [medAlpaca](https://huggingface.co/medalpaca/medalpaca-7b) for medical to acquire common terminology. Then, frame the answers context, and build a RAG system on top of it with company specific documents.

Fine-tuning is useful when you want to manage the model's **behavior**, and doing so through prompt engineering is not possible, or it requires so many tokens that it’s better to add that information to the training. Or perhaps the task is so narrow and structured that model distillation is the best option.

RAG, on the other hand, excels at integrating **knowledge** through dynamic data and ensuring accurate, up-to-date responses in real-time. This makes it especially useful for scenarios like the Pear Store, where policies and promotions change frequently. RAG also provides data that is grounded in the answer and offers the ability to segment information delivered to users via document-level security.

Combining fine-tuning and RAG can also be an effective strategy to leverage the strengths of both approaches and tailor solutions to specific project needs.

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