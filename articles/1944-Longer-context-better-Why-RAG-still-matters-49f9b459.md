---
title: 'Longer context ≠ better: Why RAG still matters'
company: Elastic
tag: RAG
date: 2025-07-11
url: https://www.elastic.co/search-labs/blog/rag-vs-long-context-model-llm
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Longer context ≠ better: Why RAG still matters

Learn why the RAG strategy is still relevant and gives the most efficient and better results.

July 11, 2025

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)[Eduard Martin](/search-labs/author/eduard-martin)

[AI](/search-labs/blog/category/ai)

Jump to

Share

Models with over 1 million tokens are not something new; more than 1 year ago, [Google announced Gemini 1.5](https://blog.google/technology/ai/google-gemini-next-generation-model-february-2024/) with 1 million tokens of context. One million tokens is approximately 2000 A5 pages which, in many cases, is more than all the data we have stored.

Then the question arises: “***What if I just send everything in the prompt?***”

In this article, we will compare RAG with just sending everything to a long context model and letting the LLM analyze the context and answer a question.

You can find a notebook with the full experiment [***here***](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/why-rag-still-matters/why_rag_still_matters.ipynb).

## Initial thoughts

Before we begin, we can make some statements to put to the test:

* **Convenience**: Not many models have long context versions, so our alternatives are limited.
* **Performance**: The speed of processing 1M tokens by an LLM should be slower than retrieving from Elasticsearch + LLM processing smaller token contexts.
* **Price**: The price per question should be significantly higher.
* **Precision**: A RAG system can effectively help us filter out noise and keep the LLM’s attention on what matters.

Though sending everything as context is an advantage, it presents the challenge of making sure you are capturing every relevant document on your query. Elasticsearch allows you to mix and match different strategies to search the right documents: filters, full-text search, semantic search, and hybrid search.

## Test definition

### Model/RAG specs

* LLM Model: gemini-2.0-flash
* Model provider: Google
* Dataset: Elasticsearch search labs articles

For each of the test cases we are going to evaluate:

* LLM Price
* End-to-end latency
* Answer correctness

### Test cases

Based on an Elasticsearch articles [dataset](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/why-rag-still-matters/dataset.ndjson), we are going to test the two strategies, RAG and LLM full context, on two different types of questions:

**Textual.** The question will be about a text that is literally written in the documents.

**Non-textual**. The question text will not be present in the document and will require the LLM to infer information or use different pieces.

## Running tests

### 1. Index data

Download the [dataset](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/why-rag-still-matters/dataset.ndjson) in NDJSON format to run the following steps:

The following steps and screenshots were taken from a Cloud Hosted Deployment. In the deployment, go to “Overview” and scroll down to click “Upload a file.” Then click on “here” since we need to add customized mappings.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf272b617f371176a/6a1708a5961e696ca4c4cebe/f92fbfc8bccfaa473d9e03fe4ad6f9fd4d81a3f3-1600x744.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0df86e842751015f/6a1708a64a531b115136a8d0/91b47708f70355119f74999c8633fcd56e6cb679-865x883.png)

In the new view, drag the ndjson file with the dataset and click on import.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6f41a1821e645ff7/6a1708a82b835f1a75f4b17e/87d7ad8e8a9bc5018e184fad5497608a62d93edd-1171x655.png)

Then, click on advanced and enter the index’s name and add the following mappings:

```
{
  "properties": {
    "text": { "type": "text", "copy_to": "semantic_text" },
    "meta_description": { "type": "keyword", "copy_to": "semantic_text" },
    "title": { "type": "keyword", "copy_to": "semantic_text" },
    "imported_at": { "type": "date" },
    "url": { "type": "keyword" },
    "semantic_text": {
      "type": "semantic_text"
    }
  }
}
```

Click import to finalize and wait for the data to be indexed.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb59414fdca8ba86d/6a1708a9a6c2b9c874e7967d/6fbfd3500f83f601c0bde6e4e61865a1116f4499-682x402.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc58d9cc2fed86ebb/6a1708ab4a531b395236a8d4/8ccfacc38a5b694df0339442188f4898f300558a-1509x924.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0101e9f25ea87b68/6a1708accf4f2562beb2d11a/32a593051aab27f5d6d3f3b975a52a80a4f74518-408x153.png)

### 2. Textual RAG

I’ve extracted a fragment of the article ***Elasticsearch in JavaScript the proper way, part II*** to use as the query string.

```
query_str = """
Let’s now create a test.js file and install our mock client: Now, add a mock for semantic search: We can now create a test for our code, making sure that the Elasticsearch part will always return the same results: Let’s run the tests.
"""
```

#### Running match phrase query

This is the query we're going to use to retrieve the results from Elasticsearch using match phrase search capabilities. We will pass the query\_str as input to the match phrase search.

```
textual_rag_summary = {}  # Variable to store results

start_time = time.time()

es_query = {
    "query": {"match_phrase": {"text": {"query": query_str}}},
    "_source": ["title"],
    "highlight": {
        "pre_tags": [""],
        "post_tags": [""],
        "fields": {"title": {}, "text": {}},
    },
    "size": 10,
}

response = es_client.search(index=index_name, body=es_query)
hits = response["hits"]["hits"]

textual_rag_summary["time"] = (
    time.time() - start_time
)  # save time taken to run the query
textual_rag_summary["es_results"] = hits  # save hits

print("ELASTICSEARCH RESULTS: \n", json.dumps(hits, indent=4))
```

Returned hits:

```
ELASTICSEARCH RESULTS: 
 [
    {
        "_index": "technical-articles",
        "_id": "tnWcO5cBTbKqUnB5yeVn",
        "_score": 36.27694,
        "_source": {
            "title": "Elasticsearch in JavaScript the proper way, part II - Elasticsearch Labs"
        },
        "highlight": {
            "text": [
                "Let\u2019s now create a test.js file and install our mock client: Now, add a mock for semantic search: We can now create a test for our code, making sure that the Elasticsearch part will always return the same results: Let\u2019s run the tests"
            ]
        }
    }
]
```

This prompt template gives the LLM the instructions to answer the question and the context to do so. At the end of the prompt, we're asking for the article that contains the information we are looking for.

The prompt template will be the same for all tests.

```
# LLM prompt template
template = """
  Instructions:

  - You are an assistant for question-answering tasks.
  - Answer questions truthfully and factually using only the context presented.
  - If you don't know the answer, just say that you don't know, don't make up an answer.
  - Use markdown format for code examples.
  - You are correct, factual, precise, and reliable.
  - Answer

  Context:
  {context}

  Question:
  {question}.

  What is the title article?
"""
```

#### Run results through LLM

Elasticsearch results will be provided as context for the LLM so we can get the result we need. We are going to extract the article title and the highlights relevant to the user query. After that we send the question, article titles, and highlights to the LLM to find the answer.

```
start_time = time.time()

prompt = ChatPromptTemplate.from_template(template)

context = ""

for hit in hits:
    # For semantic_text matches, we need to extract the text from the highlighted field
    if "highlight" in hit:
        highlighted_texts = []

        for values in hit["highlight"].values():
            highlighted_texts.extend(values)

        context += f"{hit['_source']['title']}\n"
        context += "\n --- \n".join(highlighted_texts)

# Use LangChain for the LLM part
chain = prompt | llm | StrOutputParser()

printable_prompt = prompt.format(context=context, question=query_str)
print("PROMPT WITH CONTEXT AND QUESTION:\n ", printable_prompt)  # Print prompt

with get_openai_callback() as cb:
    response = chain.invoke({"context": context, "question": query_str})

# Save results
textual_rag_summary["answer"] = response
textual_rag_summary["total_time"] = (time.time() - start_time) + textual_rag_summary[
    "time"
]  # Sum of time taken to run the semantic search and the LLM
textual_rag_summary["tokens_sent"] = cb.prompt_tokens
textual_rag_summary["cost"] = calculate_cost(
    input_tokens=cb.prompt_tokens, output_tokens=cb.completion_tokens
)

print("LLM Response:\n ", response)
```

LLM response:

```
 What is the title article?

LLM Response:
  Elasticsearch in JavaScript the proper way, part II - Elasticsearch Labs
```

***The model finds the right article.***

### 3. LLM Textual

#### Match All Query

To provide context to the LLM, we're going to get it from the indexed documents in Elasticsearch. We are going to send all the 303 articles we have indexed, which are about 1 million tokens long.

```
textual_llm_summary = {}  # Variable to store results

start_time = time.time()

es_query = {"query": {"match_all": {}}, "sort": [{"title": "asc"}], "size": 1000}

es_results = es_client.search(index=index_name, body=es_query)
hits = es_results["hits"]["hits"]

# Save results
textual_llm_summary["es_results"] = hits
textual_llm_summary["time"] = time.time() - start_time

print("ELASTICSEARCH RESULTS: \n", json.dumps(hits, indent=4))
```

```
ELASTICSEARCH RESULTS: 
 [
    {
        "_index": "technical-articles",
        "_id": "J3WUI5cBTbKqUnB5J83I",
        "_score": null,
        "_source": {
            "meta_description": ".NET articles from Elasticsearch Labs",
            "imported_at": "2025-05-30T18:43:20.036600",
            "text": "Tutorials Examples Integrations Blogs Start free trial .NET Categories All Articles Agent AutoOps ... API Reference Elastic.co Change theme Change theme Sitemap RSS 2025. Elasticsearch B.V. All Rights Reserved.",
            "title": ".NET - Elasticsearch Labs",
            "url": "https://www.elastic.co/search-labs/blog/category/dot-net-programming"
        },
        "sort": [
            ".NET - Elasticsearch Labs"
        ]
    },
   ... 
]
```

#### Run results through LLM

As in the previous step, we're going to provide the context to the LLM and ask for the answer.

```
start_time = time.time()

prompt = ChatPromptTemplate.from_template(template)
# Use LangChain for the LLM part
chain = prompt | llm | StrOutputParser()

printable_prompt = prompt.format(context=context, question=query_str)
print("PROMPT:\n ", printable_prompt)  # Print prompt

with get_openai_callback() as cb:
    response = chain.invoke({"context": hits, "question": query_str})

# Save results
textual_llm_summary["answer"] = response
textual_llm_summary["total_time"] = (time.time() - start_time) + textual_llm_summary[
    "time"
]  # Sum of time taken to run the match_all query and the LLM
textual_llm_summary["tokens_sent"] = cb.prompt_tokens
textual_llm_summary["cost"] = calculate_cost(
    input_tokens=cb.prompt_tokens, output_tokens=cb.completion_tokens
)

print("LLM Response:\n ", response)  # Print LLM response
```

LLM response:

```
...  
What is the title article?

LLM Response:
  The title of the article is "Testing your Java code with mocks and real Elasticsearch".
```

It failed! When multiple articles contain similar information, the LLM might struggle to pinpoint the exact text you’re searching for.

#### RAG non-textual

For the second test we're going to use a semantic query to retrieve the results from Elasticsearch. For that we built a short synopsis of ***Elasticsearch in JavaScript, the proper way, part II*** article as query\_str and provided it as input to RAG.

```
query_str = "This article explains how to improve code reliability. It includes techniques for error handling, and running applications without managing servers."
```

From now on, the code mostly follows the same pattern as the tests with the textual query, so we’ll refer to the code in the [notebook](https://github.com/Delacrobix/why-rag-stills-matters_article/blob/main/why_rag_still_matters.ipynb) for those sections.

#### Running semantic search

Notebook reference: ***2. Run Comparisons > Test 2: Semantic Query > Executing semantic search.***

Semantic search response hits:

```
ELASTICSEARCH RESULTS: 
 [
...
    {
        "_index": "technical-articles",
        "_id": "KHV7MpcBTbKqUnB5TN-F",
        "_score": 0.07619048,
        "_source": {
            "title": "Elasticsearch in JavaScript the proper way, part II - Elasticsearch Labs"
        },
        "highlight": {
            "text": [
                "We will review: Production best practices Error handling Testing Serverless environments Running the",
                "how long you want to have access to it.",
                "Conclusion In this article, we learned how to handle errors, which is crucial in production environments",
                "DT By: Drew Tate Integrations How To May 21, 2025 Get set, build: Red Hat OpenShift AI applications powered",
                "KB By: Kofi Bartlett Jump to Production best practices Error handling Testing Serverless environments"
            ]
        }
    },
      ...
]
```

#### Run results through LLM

Notebook reference: ***2. Run Comparisons > Test 2: Semantic Query > Run results through LLM***

LLM response:

```
...
  What is the title article?

LLM Response:
  Elasticsearch in JavaScript the proper way, part II - Elasticsearch Labs
```

### 4. LLM non-textual

#### Match-all query

Notebook reference: ***2. Run Comparisons > Test 2: Semantic Query > Match all query***

Match-all-query response:

```
ELASTICSEARCH RESULTS: 
 [
    {
        "_index": "technical-articles",
        "_id": "J3WUI5cBTbKqUnB5J83I",
        "_score": null,
        "_source": {
            "meta_description": ".NET articles from Elasticsearch Labs",
            "imported_at": "2025-05-30T18:43:20.036600",
            "text": "Tutorials Examples Integrations Blogs Start free trial .NET Categories All Articles ... to easily utilize Elasticsearch to build advanced search experiences including generative AI, embedding models, reranking capabilities and more. Let's connect Menu Tutorials Examples Integrations Blogs Search Additional Resources Elasticsearch API Reference Elastic.co Change theme Change theme Sitemap RSS 2025. Elasticsearch B.V. All Rights Reserved.",
            "title": ".NET - Elasticsearch Labs",
            "url": "https://www.elastic.co/search-labs/blog/category/dot-net-programming"
        },
        "sort": [
            ".NET - Elasticsearch Labs"
        ]
    },
...
]
```

#### Run results through LLM

Notebook reference: ***2. Run Comparisons > Test 2: Semantic Query > Run results through LLM***

LLM response:

```
...
 What is the title article?

LLM Response:
  "Elasticsearch in JavaScript the proper way, part II" and "A tutorial on building local agent using LangGraph, LLaMA3 and Elasticsearch vector store from scratch - Elasticsearch Labs" and "Advanced integration tests with real Elasticsearch - Elasticsearch Labs" and "Automatically updating your Elasticsearch index using Node.js and an Azure Function App - Elasticsearch Labs"
```

As the LLM has more options to choose from that were not filtered on a search stage, it will pick every similar article.

## Test results

Now we are going to visualize the results of the test.

Textual Query

|  | Strategy | Answer | Tokens Sent | Time(s) | LLM Cost |
| --- | --- | --- | --- | --- | --- |
| 0 | Textual RAG | Elasticsearch in JavaScript the proper way, part II - Elasticsearch Labs | 237 | 1.281432 | 0.000029 |
| 1 | Textual LLM | The title of the article is "Testing your Java code with mocks and real Elasticsearch" | 1,023,231 | 45.647408 | 0.102330 |

Semantic Query

|  | Strategy | Answer | Tokens Sent | Time(s) | LLM Cost |
| --- | --- | --- | --- | --- | --- |
| 0 | Semantic RAG | Elasticsearch in JavaScript the proper way, part II - Elasticsearch Labs | 1,328 | 0.878199 | 0.000138 |
| 1 | Semantic LLM | "Elasticsearch in JavaScript the proper way, part II" and "A tutorial on building local agent using LangGraph, LLaMA3 and Elasticsearch vector store from scratch - Elasticsearch Labs" and "Advanced integration tests with real Elasticsearch - Elasticsearch Labs" and "Automatically updating your Elasticsearch index using Node.js and an Azure Function App - Elasticsearch Labs" | 1,023,196 | 44.386912 | 0.102348 |

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6d1ad6cf82af9aac/6a1708aeb339d5f146769f48/779864856463380142739c3e48d15e237f924f89-830x555.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt12e92f04c723992d/6a1708af2b835f58a0f4b182/a3db2fcb06216a6c0e28afc8b9a108d3f6a82feb-841x555.png)![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9bd04f35b1195eb1/6a1708b11949f71e36e7a993/1e821433422e68653e7b447af3f58b4fe7970b0a-857x555.png)

## Conclusion

RAG is still highly relevant. Our tests show that using massive context models to send data without filtering in the context window is inferior to a RAG system in price, latency, and precision. It is common to see [models losing attention](https://arxiv.org/abs/2307.03172) when processing large amounts of context.

Even with the capabilities of large language models (LLMs), it's crucial to filter data before sending it to them since sending excessive tokens can lower the quality of responses. However, large context LLMs remain valuable when pre-filtering isn't feasible or when answers require drawing from extensive datasets.

Additionally, you still need to make sure you’re using the correct queries on your RAG systems to get a complete and correct answer. You can test different values in your queries to retrieve different amounts of documents until you find what works best for you.

* **Convenience:** The average tokens sent to the LLM using RAG was **783**. Lower than all the mainstream models' maximum context window.
* **Performance:** RAG delivers significantly faster query speed. An average of **1 second**, versus the **45 seconds** of the pure LLM approach.
* **Price:** The average cost of a RAG query ($0,00008) was **1250 times lower** than the pure LLM approach ($0,1)
* **Precision:** The RAG system produced accurate responses across all iterations, while the full-context approach led to inaccuracies.

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