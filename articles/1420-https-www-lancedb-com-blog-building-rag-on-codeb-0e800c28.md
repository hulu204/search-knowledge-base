---
title: 'https://www.lancedb.com/blog/building-rag-on-codebases-part-2'
company: LanceDB
tag: 问答/RAG
date: 
url: https://www.lancedb.com/blog/building-rag-on-codebases-part-2
account: 
origin: en-rss
---
# Building RAG on codebases: Part 2

[Sankalp Shubham](/author/sankalp-shubham)

•

November 7, 2024

•

[Community](/category/community)

![1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28-fig-001](../images/1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## Quick recap

In the [previous post](https://lancedb.com/blog/building-rag-on-codebases-part-1), we covered the indexing stage of building a question-answering (QA) system for codebases. We discussed why models like GPT-4 can’t inherently answer code questions and the limitations of in-context learning. We also explored semantic code search with embeddings and the importance of proper codebase chunking. We then showcased a syntax-level chunking approach with abstract syntax trees (ASTs) using tree-sitter, demonstrating how to extract methods, classes, constructors, and cross-codebase references.

Now that the most of the indexing has been discussed, let’s proceed to the next stages!

## What to expect

In this post, we’ll cover the following topics:

* Final step for codebase indexing: Adding LLM-generated comments
* Considerations for choosing embeddings and vector databases
* Techniques to improve retrieval: HyDE, BM25, re-ranking
* Choosing re-rankers: An in-depth explanation of re-ranking (bi-encoding vs. cross-encoders)

If you’ve ever worked with embeddings, you’ll know that a single-stage embedding-based (semantic) search is not always useful, and you’d need some additional steps in the retrieval pipeline like HyDE, hybrid vector-search and re-ranking.

In next few sections, we’ll discuss methods to improve our overall search and the relevant implementation details. Refer to the diagram in the [previous post](https://lancedb.com/blog/building-rag-on-codebases-part-1) for more information on the architecture of the CodeQA system.

## Adding LLM comments

This is technically part of codebase indexing too, but it felt more in line to be discussing it in this post.

### Implementing LLM-generated comments for methods (optional)

LLM comments are not included in the current version of CodeQA because it slows down the indexing process. The relevant file `llm_comments.py` is still there in the repo.

Since our queries will be in natural language, we integrated a natural language component by adding 2-3 lines of documentation for each method. This creates an annotated codebase, with each LLM-generated comment providing a concise overview. These annotations enhance keyword and semantic search, allowing for more efficient searches based on both “what the code does” and “what the code *is*”.

Here’s a cool blogpost which validated these ideas: “[Three LLM tricks that boosted embeddings search accuracy by 37% — Cosine](https://www.buildt.ai/blog/3llmtricks)”.

### Meta-characteristic search

One of the core things we wanted to have is for people to be able to search for characteristics of their code which weren’t directly described in their code, for example a user might want to search for **all generic recursive functions**, which would be very difficult if not impossible to search for through conventional string matching/regex and likely wouldn’t perform at all well through a simple embedding implementation. This could also be applied to non-code spaces too; a user may want to ask a question of an embedded corpus of Charles Dickens asking **find all cases where Oliver Twist is self-reflective** which would not really be possible with a basic embedding implementation.

Our solution with Buildt was: For each element/snippet we embed a textual description of the code to get all of the meta characteristics, and we get those characteristics from a fine-tuned LLM. By embedding the textual description of the code alongside the code itself, it allows you to search both against raw code as well as the characteristics of the code, which is why we say you can “search for what your code does, rather than what your code is”. This approach works extremely well and without it questions regarding functionality rarely return accurate results. This approach could easily be ported to prose or any other textual form which could be very exciting for large knowledge bases.

There are pitfalls to this approach: it obviously causes a huge amount of extra cost relative to merely embedding the initial corpus, and increases latency when performing the embedding process - so it may not be useful in all cases, but for us it is a worthwhile trade-off as it produces a magical search experience.

## Embedding and choice of vector database

We use OpenAI’s **`text-embedding-3-large`** by default as it’s very good – plus almost everyone has OpenAI API keys, so it’s great for demo purposes as in this post. There’s also an option for using **`jina-embeddings-v3`**, which are supposedly better than **`text-embedding-3-large`** in benchmarks, so it’s worth trying that too.

OpenAI embeddings are cost-effective and have a sequence length of 8,191 tokens, and easily accessible via API. Sequence length is important for an embedding model, because it allows the model to capture long-length dependencies and do more with the context.

## Things to consider for embeddings

Let’s look at what you’d normally consider when choosing an embedding model.

### Benchmarks

You can checkout the [MTEB leaderboard](https://huggingface.co/spaces/mteb/leaderboard) for embedding ranking with scores. Look at the scores, sequence length, the languages that are supported. Locally available models need your compute, so look at size for open source models.

### Latency

API-based embeddings can be slower than local ones simply because of network round-trips added latency. So if you want speed and you have the compute, it may be better to use local embeddings.

### Cost

If you’re constrained by cost, go open source via `sentence-transformers`, or `bge-en-v1.5` or `nomic-embed-v1`. Otherwise, most closed source embeddings are cheap and fast to use.

### Use-case

The models should be applicable for your use-case. Research accordingly on Hugging Face or the model’s documentation and/or research paper. If you are embedding code, the embeddings you use *must* have had code in pre-training data.

You can also use **fine-tuned embeddings** to significantly improve your downstream performance. LlamaIndex has a high-level API to fine-tune all Hugging Face embeddings. Jina recently [announced](https://x.com/JinaAI_/status/1785337862755356685) a fine-tuning API, which is worth a try.

### Privacy

Privacy for data is a major concern for several people and companies. For many projects, you may prioritize performance and choose OpenAI, not considering privacy concerns. For others, you may prioritize privacy first.

Below is a quote from a SourceGraph blog post:

> While embeddings worked for retrieving context, they had some drawbacks for our purposes. Embeddings require all of your code to be represented in the vector space and to do this, we need to send source code to an OpenAI API for embedding. Then, those vectors need to be stored, maintained, and updated. This isn’t ideal for three reasons:  
> - Your code has to be sent to a 3rd party (OpenAI) for processing, and not everyone wants their code to be relayed in this way.  
> - The process of creating embeddings and keeping them up-to-date introduces complexity that Sourcegraph admins have to manage.  
> - As the size of a codebase increases, so does the respective vector database, and searching vector databases for codebases with >100,000 repositories is complex and resource-intensive. This complexity was limiting our ability to build our new multi-repository context feature.

For a deeper understanding of codebase indexing methodologies, it’s recommended to review the SourceGraph blog post in much more detail, because their approach is similar to the CodeQA implementation, but operates at a significantly larger scale. They developed an AI coding assistant named [Cody](https://github.com/sourcegraph/cody-public-snapshot) using this approach. It’s worth also noting that they have since moved away from using embeddings in their architecture.

Another recommended blog post to read is “[How Cody understands your codebase](https://sourcegraph.com/blog/how-cody-understands-your-codebase)”.

## Vector database: LanceDB

I use [LanceDB](https://lancedb.com/) because it’s fast, open source and easy to use - you can just `pip install` and import it as a library – no API key required. They support integrations for almost all embeddings (available on Hugging Face) and most major players like OpenAI, Jina and so on. There’s easy support for integration for re-rankers, algorithms, embeddings, and third-party libraries for RAG.

### Things to consider

* Support for all the integrations you need - e.g LLMs, different companies,
* Recall and Latency
* Cost
* Familiarity/Ease of use
* Open source / closed source

### Implementation details

Code for embedding the codebase and making the tables can be found in the [create\_tables.py](https://github.com/sankalp1999/code_qa/blob/main/create_tables.py) file in the repo. Two separate LanceDB tables are maintained – one for methods, and another for classes and miscellaneous items like `README` files. Keeping things separate allows us to query separate metadata for specific vector searches – get the closest class, then get the closest methods.

In the implementation, you’ll notice that we don’t generate embeddings manually. That part is handled by LanceDB itself, implicitly. Just add your chunks, and LanceDB handles all the batch-embedding generation with retry logic in the background, via the embedding registry.

## Retrieval

Once we have the tables ready, we can issue queries, and it outputs the most similar documents using brute-force search (cosine similarity/dot product). These results are going to be relevant but not as accurate as you think. Embedding search feels like magic, *until it doesn’t*. Based on experiments from other projects, the results are relevant but often noisy plus the ordering can be wrong often.See this [tweet thread](https://x.com/eugeneyan/status/1767403777139917133) to learn about some shortcomings.

## Improving embedding search

### BM25

The first thing to try is to combine semantic search with a keyword based search like BM25. This is what’s used in the [semantweet search](https://github.com/sankalp1999/semantweet-search) project. These are supported out-of-the-box already by many vector databases. semantweet search also used LanceDB, which supports *hybrid search*: semantic search + BM25 out-of-the-box. All it takes is some additional code to create a native full-text based index in LanceDB.

Recall is how many of the relevant documents are we retrieving / number of documents. It’s used to measure search performance.

## Filtering using meta-data

Another effective approach to enhance semantic search is to use metadata filtering. If your data contains attributes like dates, keywords, or metrics, you can use SQL to pre-filter the results before performing semantic search. This two-step process can significantly improve search quality and performance. It’s important to note that embeddings exist as independent points in latent space, so this pre-filtering step helps narrow down the relevant search space.

## Reranking

Using re-rankers after the vector search is an easy way to improve results significantly. In short, re-rankers do a cross-attention between query tokens and embedding search result tokens.

Let’s try to understand how they work on a high level. In CodeQA v2, we use `answerdotai/answerai-colbert-small-v1` as it’s the best performing local re-ranker model based on some available benchmarks (take all benchmarks with a grain of salt), with performance close to Cohere Re-ranker 3 (which was used in CodeQA v1).

### Cross-encoding (re-ranking) vs bi-encoding (embeddings based search)

Embeddings are obtained from models like GPT-3 → decoder-only transformer  
or BERT (encoder-only transformer, BERT-base is 12 encoders stacked together).

Both GPT-3 and BERT-classes of models can be made to operate in two styles → cross-encoder and bi-encoder. They have to be trained (or fine-tuned) for the same. we’ll not get into the training details here.

```
from sentence_transformers import SentenceTransformer, CrossEncoder

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2") # biencoder

# Load the cross-encoder model
cross_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2") # cross-encoder
```

#### Cross-encoder

A cross-encoder concatenates the query with each document and computes relevance scores.

```
<query><doc1>
<query><doc2>
```

Each pair of concatenated *query* + *document* is passed through a pre-trained model (like BERT), going through several layers of attention and feed-forward networks. The self-attention mechanism helps to capture the interaction between the query and the doc (all tokens of query interact with document)

We get the output from a  hidden layer (usually the last one) to get contextualized embeddings. These embeddings are pooled to obtain a fixed size representation. These are then passed through a linear layer and then softmax/sigmoid to obtain logits → relevance scores → `[0.5, 0.6, 0.8, 0.1, …]`.

Let’s say we have *D* documents and *Q* queries. To calculate relevance score for 1 query, we will have *D* (query + doc) passes. through the model. For *Q* queries, we will have *D x Q* passes since *each* concatenation of *D* and *Q* is unique.

#### Bi-encoder

A bi-encoder approach (or the **embeddings search approach)** encodes documents and queries separately, and calculates the dot product. Let’s say you have 𝐷 docs and 𝑄 queries.

Precompute 𝐷 embeddings. We can reuse the embedding instead of calculating again. Now for each query, compute dot product of 𝐷 and 𝑄. Dot product can be considered an 𝑂⁡(1) operation.

* compute cost of encoding 𝐷 docs → 𝐷
* compute cost of encoding 𝑄 queries → 𝑄
* compute cost then becomes 𝐷 +𝑄

This is *much* faster than the cross-encoding approach.

Since every token in query interacts with the documents and assigns a relevance score of query vs. each document, the cross-encoder is more accurate than bi-encoders, but they are slower, since an individual processing of each pair is required (each 𝑄 + 𝐷 combination is unique so cannot precompute embeddings).

Thus, we can stick to a bi-encoder approach (generating embeddings, encode query, encode documents and store in a vector database, then calculate similarity) for fast retrieval. Then, we can use rerankers (cross-encoders) to get the `top-k` results for improving the results.

## Reranking demonstration

In the below example, note that `How many people live in New Delhi? No idea.` has the most lexical similarity so cos similarity / bi-encoder approach will say it’s most relevant.

```
from sentence_transformers import SentenceTransformer, CrossEncoder
import numpy as np

# Load the bi-encoder model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Load the cross-encoder model
cross_model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

# Function to calculate cosine similarity
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

query = "How many people live in New Delhi?"
documents = [
    "New Delhi has a population of 33,807,000 registered inhabitants in an area of 42.7 square kilometers.",
    "In 2020, the population of India's capital city surpassed 33,807,000.",
    "How many people live in New Delhi? No idea.",
    "I visited New Delhi last year; it seemed overcrowded. Lots of people.",
    "New Delhi, the capital of India, is known for its cultural landmarks."
]

# Encode the query and documents using bi-encoder
query_embedding = embedding_model.encode(query)
document_embeddings = embedding_model.encode(documents)

# Calculate cosine similarities
scores = [cosine_similarity(query_embedding, doc_embedding) for doc_embedding in document_embeddings]

# Print initial retrieval scores
print("Initial Retrieval Scores (Bi-Encoder):")
for i, score in enumerate(scores):
    print(f"Doc{i+1}: {score:.2f}")

# Combine the query with each document for the cross-encoder
cross_inputs = [[query, doc] for doc in documents]

# Get relevance scores for each document using cross-encoder
cross_scores = cross_model.predict(cross_inputs)

# Print reranked scores
print("\nReranked Scores (Cross-Encoder):")
for i, score in enumerate(cross_scores):
    print(f"Doc{i+1}: {score:.2f}")
```

Outputs:

```
Initial Retrieval Scores (Bi-Encoder):
Doc1: 0.77
Doc2: 0.58
Doc3: 0.97
Doc4: 0.75
Doc5: 0.54

Reranked Scores (Cross-Encoder):
Doc1: 9.91
Doc2: 3.74
Doc3: 5.64
Doc4: 1.67
Doc5: -2.20
```

The outputs after better formatting demonstrate the effectiveness of the cross-encoder approach.

## HyDE (hypothetical document embeddings)

The user’s query is most likely going to be in english and less likely to be in code. But our embeddings are mostly made up of code. If you think about the latent space, code would be nearer to code than english (natural language). This is the idea of the [HyDE paper](https://arxiv.org/abs/2212.10496).

You ask an LLM to generate a *hypothetical* answer to your query and then you use this (generated) query for embedding search. The intuition is the that embedding of the hypothetical query is going to be closer in latent/embedding space to your data than your actual natural language query.

### Implementation details

The code used in this section is mainly from **`app.py`** and **`prompts.py`**. It uses **`gpt-4o-mini`** for both HyDE queries as it’s cheap, fast and decent with code-understanding capabilities. Here’s how a HyDE query would look:

```
# app.py
def openai_hyde(query):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": HYDE_SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Help predict the answer to the query: {query}",
            }
        ]
    )
    return chat_completion.choices[0].message.content

# prompts.py
HYDE_SYSTEM_PROMPT = '''You are an expert software engineer. Your task is to predict code that answers the given query.

Instructions:
1. Analyze the query carefully.
2. Think through the solution step-by-step.
3. Generate concise, idiomatic code that addresses the query.
4. Include specific method names, class names, and key concepts in your response.
5. If applicable, suggest modern libraries or best practices for the given task.
6. You may guess the language based on the context provided.

Output format:
- Provide only the improved query or predicted code snippet.
- Do not include any explanatory text outside the code.
- Ensure the response is directly usable for further processing or execution.'''
```

The hallucinated query is used to perform an initial embedding search, retrieving the top 5 results from our tables. These results serve as context for a second HyDE query. In the first query, the programming language was not known but with the help of the fetched context, the language is most likely known now.

The second HyDE query is more context aware and expands the query with relevant code-specific details.

```
# app.py
def openai_hyde_v2(query, temp_context, hyde_query):
    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": HYDE_V2_SYSTEM_PROMPT.format(query=query, temp_context=temp_context)
            },
            {
                "role": "user",
                "content": f"Predict the answer to the query: {hyde_query}",
            }
        ]
    )
    return chat_completion.choices[0].message.content

# prompts.py
HYDE_V2_SYSTEM_PROMPT = '''You are an expert software engineer. Your task is to enhance the original query: {query} using the provided context: {temp_context}.

Instructions:
1. Analyze the query and context thoroughly.
2. Expand the query with relevant code-specific details:
    - For code-related queries: Include precise method names, class names, and key concepts.
    - For general queries: Reference important files like README.md or configuration files.
    - For method-specific queries: Predict potential implementation details and suggest modern, relevant libraries.
3. Incorporate keywords from the context that are most pertinent to answering the query.
4. Add any crucial terminology or best practices that might be relevant.
5. Ensure the enhanced query remains focused and concise while being more descriptive and targeted.
6. You may guess the language based on the context provided.

Output format: Provide only the enhanced query. Do not include any explanatory text or additional commentary.'''
```

By leveraging the LLM’s understanding of both code and natural language, it generates an expanded, more contextually-aware query that incorporates relevant code terminology and natural language descriptions. This two-step process helps bridge the semantic gap between the user’s natural language query and the codebase’s technical content.

A vector search is performed using the second query and top-K results are re-ranked using [answerdotai/answerai-colbert-small-v1](https://huggingface.co/answerdotai/answerai-colbert-small-v1) and then, the relevant metadata is fetched.

Note that references are fetched from meta data and combined with code to be feeded as context for the LLM.

```
# app.py, from the function def generate_context(query, rerank=False)

hyde_query = openai_hyde(query)

method_docs = method_table.search(hyde_query).limit(5).to_pandas()
class_docs = class_table.search(hyde_query).limit(5).to_pandas()

temp_context = '\n'.join(method_docs['code'] + '\n'.join(class_docs['source_code']) )

hyde_query_v2 = openai_hyde_v2(query, temp_context)

logging.info("-query_v2-")
logging.info(hyde_query_v2)

method_search = method_table.search(hyde_query_v2)
class_search = class_table.search(hyde_query_v2)

if rerank: # if reranking is selected by user from the UI
    method_search = method_search.rerank(reranker)
    class_search = class_search.rerank(reranker)

method_docs = method_search.limit(5).to_list()
class_docs = class_search.limit(5).to_list()

top_3_methods = method_docs[:3]
methods_combined = "\n\n".join(f"File: {doc['file_path']}\nCode:\n{doc['code']}" for doc in top_3_methods)

top_3_classes = class_docs[:3]
classes_combined = "\n\n".join(f"File: {doc['file_path']}\nClass Info:\n{doc['source_code']} References: \n{doc['references']}  \n END OF ROW {i}" for i, doc in enumerate(top_3_classes))
```

All the above context is plugged into an LLM that chats with the user. `gpt-4o` is for this task as we need a strong LLM for reasoning over the retrieved context and chatting in natural language with the user.

We have completed our RAG experiment here. In our analogy with Cursor, when the user mentions **`@codebase`**, then only embeddings are retrieved otherwise existing context is used. If the LLM is not confident about the context, it will tell the user to mention **`@codebase`** (because of the system prompt).

```
# app.py, from the function def home()
    rerank = True if rerank in [True, 'true', 'True', '1'] else False

            if '@codebase' in query:
                query = query.replace('@codebase', '').strip()
                context = generate_context(query, rerank)
                app.logger.info("Generated context for query with @codebase.")
                app.redis_client.set(f"user:{user_id}:chat_context", context)
            else:
                context = app.redis_client.get(f"user:{user_id}:chat_context")
                if context is None:
                    context = ""
                else:
                    context = context.decode()

            # Now, apply reranking during the chat response if needed
            response = openai_chat(query, context[:12000])  # Adjust as needed
```

This completes the walkthrough!

## Possible improvements

### Latency

There are a lot of improvements possible, especially in the latency department. Currently, queries tagged with `@codebase` and no re-ranking take about 10-20 seconds. With re-ranking enabled, the retrieval is in 20-30 second range (which is definitely slow). However, if you look at the user expectations with tools like Cursor, users seem happy with latencies hovering around the commonly seen 15-20 second mark.

* The easiest way to cut latency is to use an LLM like **`Llama3.1 70B`** from a high throughput inference provider like Groq or Cerebras. This should cut latency by atleast 10 seconds (speed up the HyDE calls by gpt4o-mini) – though, this may impact retrieval quality due to the capabilities of the LLM. You can try out using local embeddings to tackle network latency while balancing its effects with cost/speed.
* Our latency bottleneck is also in the HyDE queries. Is it possible to reduce them to one or totally eliminate them altogether? Maybe a combination of BM25 based keyword search on the [**repository map**](https://aider.chat/docs/repomap.html) can help reduce at least one HyDE query.

### Accuracy

The low hanging fruit to improve accuracy is:

* Try better embeddings or use fine-tuned embeddings
* Implement evals and optimize accuracy with help of a feedback loop

## Conclusion

Throughout this two-part series, we’ve explored the intricacies of building an effective code question-answering system. In [Part 1](https://lancedb.com/blog/building-rag-on-codebases-part-1), we laid the foundation by discussing the importance of proper codebase chunking and semantic code search. In this post, we went deeper into advanced techniques to enhance retrieval quality:

* We explored how LLM-generated comments can bridge the gap between code and natural language queries
* We discussed the critical considerations for choosing embeddings and vector databases
* We examined various techniques to improve retrieval accuracy, including:
* Hybrid search combining semantic and keyword-based approaches
* The power of cross-encoders for reranking results
* Using HyDE to bridge the semantic gap between natural language queries and code

Hopefully, this series has provided valuable insights into building practical code QA systems, with LanceDB in the mix! The complete implementation is available on [GitHub](https://github.com/sankalp1999/code_qa), and we encourage you to experiment with these techniques in your own projects.

Thank you for reading!

## Learn more about CodeQA

* Check out the code on [**Github**](https://github.com/sankalp1999/code_qa).
* See a live demo [**here**](https://youtu.be/K4IoQf2Wf8I?si=eKYKztWax0sYhE_-).

## References

Links are listed in the order they appear in the post:

1. [**Part 1 blog post**](https://lancedb.com/blog/building-rag-on-codebases-part-1)
2. [**Three LLM tricks that boosted embeddings search accuracy by 37% — Cosine**](https://www.buildt.ai/blog/3llmtricks)
3. [**MTEB leaderboard**](https://huggingface.co/spaces/mteb/leaderboard)
4. [**JinaAI’s fine-tuning API announcement**](https://x.com/JinaAI_/status/1785337862755356685)
5. [**How Cody understands your codebase**](https://sourcegraph.com/blog/how-cody-understands-your-codebase)
6. [**Cody on GitHub**](https://github.com/sourcegraph/cody-public-snapshot)
7. [**LanceDB**](https://lancedb.com/)
8. [**FAISS by Meta**](https://github.com/facebookresearch/faiss)
9. [**create\_tables.py on GitHub**](https://github.com/sankalp1999/code_qa/blob/main/create_tables.py)
10. [**Twitter thread on embedding search shortcomings**](https://x.com/eugeneyan/status/1767403777139917133)
11. [**Semantweet search on GitHub**](https://github.com/sankalp1999/semantweet-search)
12. [**BM25 benchmarks on LanceDB site**](https://docs.lancedb.com/reranking/eval)
13. [**Cohere reranker v3**](https://cohere.com/blog/rerank-3)
14. [**ColBERT and late interaction**](https://jina.ai/news/what-is-colbert-and-late-interaction-and-why-they-matter-in-search/)
15. [**HyDE paper**](https://arxiv.org/abs/2212.10496)
16. [**Ragas documentation**](https://docs.ragas.io/en/stable/)

![1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28-fig-002](../images/1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28/figure-002.jpg)

[Sankalp Shubham](/author/sankalp-shubham)

Applied AI + Backend Engineer. Currently working on agentic codegen. Interested in all things AI and distributed systems.

[GitHub](https://github.com/sankalp1999)[Linkedin](https://www.linkedin.com/in/sankalp-shubham/)[Twitter](https://x.com/dejavucoder)

![1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28-fig-003](../images/1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28-fig-004](../images/1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28-fig-005](../images/1420-https-www-lancedb-com-blog-building-rag-on-codeb-0e800c28/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb