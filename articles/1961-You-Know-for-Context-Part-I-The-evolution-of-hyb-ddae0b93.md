---
title: 'You Know, for Context - Part I: The evolution of hybrid search and context engineering'
company: Elastic
tag: 召回
date: 2025-11-12
url: https://www.elastic.co/search-labs/blog/context-engineering-hybrid-search-evolution-agentic-ai
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# You Know, for Context - Part I: The evolution of hybrid search and context engineering

Explore how hybrid search and context engineering have evolved from lexical foundations to enable the next generation of agentic AI workflows.

November 12, 2025

[Woody Walton](/search-labs/author/woody-walton)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

Part of the series:

[You Know, for Context - The evolution of hybrid search and context engineering](/search-labs/blog/series/context-engineering-hybrid-search-evolution)

In this series

Share

## Our brand new agentic AI world

Like many of us, I find myself both giddy and astonished at the pace that AI capabilities are evolving. We first saw large language models (LLMs) and vector search launch us into the semantic revolution where we were no longer hunting and pecking with keywords to find things. Then LLMs showed us new ways of interacting with our data, using chat interfaces to transform natural language requests into responses that distill vast knowledge bases into easily consumable summaries. We now (already!) have the beginnings of automated LLM-driven logic in the form of “agentic AI” workflows that can semantically understand an incoming request, reason about the steps to take, and then choose from the tools available to iteratively execute actions to achieve those goals.

The promise of agentic AI is forcing us to evolve from primarily using ‘prompt engineering’ to shape our generative AI interactions, to focusing on how we can help agentic tools obtain the most relevant and efficient additional information the LLM needs to consider when generating its responses — ‘context engineering’ is the next frontier. Hybrid search is by far the most powerful and flexible means to surface relevant context, and Elastic’s Search AI platform opens up a whole new way to leverage data in service to context engineering. In this article, we’re going to discuss how LLMs have changed the world of information retrieval from two angles, and then discuss how they can work together for greater results. There’s quite a lot of ground to cover…

## Part I: How LLMs have changed search

Let’s start from the angle of how LLMs have changed the ways we access and retrieve information.

### Our lexical legacy

We’ve all been living in the somewhat limited lexical search world (pretty well, as best we can) for a long time. Search is the first tool we reach for whenever researching or beginning a new project, and up until recently, it was up to us to word our queries in a way that a lexical search engine understands. Lexical search relies on matching some form of query terms to keywords found in a document corpus — regardless of whether the content is unstructured or structured. For a lexical search to return a document as a hit, it has to have matched on that keyword (or had a controlled vocabulary like a synonym list or dictionary to make the conceptual connection for us).

```
POST my-index/_search {
  "size": 10, 
  "query": {
    "multi_match": {
      "query": "machine learning applications",
      "fields": ["title", "content"]
    }
  }
}
```

*An example lexical* [*multi-match*](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-multi-match-query) *query*

At least search engines have the ability to return hits with a relevance score. Search engines provide a wealth of query syntax options to target indexed data effectively and built-in relevance algorithms that score the results relative to the intent of the user’s query syntax. Search engines reap the benefits of decades of advances in relevance ranking algorithms, and that makes them an efficient data retrieval platform that can deliver results scored and sorted by their relevance to the query. Databases and other systems that use SQL as their main method for retrieving data are at a disadvantage here: there is no concept of relevance in a database query; the best they can do is sort results alphabetically or numerically. The good news is you’ll get all the hits (recall) with those keywords, but they’re not necessarily in a helpful order relative to *why* you were asking for them (precision). That’s an important point, as we’ll see shortly…

### Enter the (semantic) dragon

The potential for vector representations of information as an alternative to keyword search has been researched for [quite a long time](https://www.elastic.co/search-labs/blog/introduction-to-vector-search). Vectors hold a lot of promise because they get us out of the keyword-only mode of matching content — because they’re numeric representations of terms and weights, vectors allow concepts to be mathematically close based on a language model’s understanding of how terms relate to each other in the training domain. The long delay for general- purpose vector search was due to models being mostly limited to specific domains, they simply weren’t large enough to sufficiently understand the many different concepts a term might represent within different contexts.

It wasn’t until Large Language Models (LLMs) came along a few years ago with their ability to train on much larger amounts of data (using [transformers](https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)) and [attention](https://en.wikipedia.org/wiki/Attention_(machine_learning))) that vector search became practical — the size and depth of LLMs finally allowed vectors to store enough nuance for them to actually capture semantic meaning. That sudden increase in the depth of understanding allowed LLMs to now serve a large number of natural language processing (NLP) functions that were previously locked, perhaps the most impactful being the ability to infer the most likely next term in a sequence given the context of what’s in the sequence so far. Inference is the process that gives generative AI its near-human ability to produce text. AI-generated text is informed by the LLM’s understanding of how terms are related within its training data and also uses the phrasing of the request to disambiguate between different contexts the terms might appear in.

As magical as generative AI is, there *are* limitations to LLMs that cause errors in quality and accuracy, commonly called hallucinations. Hallucinations occur when the LLM doesn’t have access to the information (or isn’t guided to the correct context) to base its answer in truth so, being helpful, it will instead generate a confident and plausible-sounding response that’s made up. Part of the cause is that while LLMs learn the usage of language within large domains of diverse information, they have to stop training at a certain point in time, so there’s a timeliness factor to their understanding — meaning that the model can only know what was accurate up to the time it stopped training. Another factor for hallucinations is that the model usually doesn’t know about privately held data (data not available on the public internet), and that’s especially significant when that data contains specific terms and nomenclature.

### Vector databases

LLMs vectorize content to its model space using a technique called text embedding, which refers to [embedding](https://www.elastic.co/search-labs/blog/hybrid-search-multiple-embeddings) or mapping the content’s semantic meaning within the model’s world view based on the training it received. There are a few steps involved to prepare and process content for embedding, including [chunking](https://www.elastic.co/search-labs/blog/chunking-strategies-elasticsearch) and tokenization (and [subword tokenization](https://www.kaggle.com/code/danishmahdi/subword-tokenization-bpe-wordpiece-and-unigram)). The result is typically a set of dense vectors representing the model’s understanding of that chunk of content’s meaning within its vector space. Chunking is an inexact process that’s meant to fit content into the limitations of a model’s processing constraints for generating embeddings, while also attempting to group related text into a chunk using semantic constructs like sentence and paragraph indicators.

The need for chunking can create a bit of semantic lossiness in an embedded document because individual chunks aren’t fully associated with other chunks from the same document. The inherent opaqueness of neural networks can make this lossiness worse — an LLM is truly a “black box” where the connections between terms and concepts made during training are non-deterministic and not interpretable by humans. This leads to issues with explainability, repeatability, unconscious bias, and potentially a loss of trust and accuracy. Still, the ability to semantically connect ideas, to not be tied to specific keywords when querying is extremely powerful:

```
POST my-index/_search 
{
  "size": 10, 
  "query": {
    "semantic": {
      "query": "machine learning applications",
      "field": "semantic-content-field"
    }
  }
}
```

*An example* [*semantic*](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-semantic-query) *query*

There’s one more issue to consider for vector databases: they’re not search engines, they’re databases! When a [vector similarity search](https://www.elastic.co/search-labs/blog/introduction-to-vector-search) is performed, the query terms are encoded to find a set of (embedding) coordinates within the model’s vector space. Those coordinates are then used as the bullseye to find the documents that are the “nearest neighbors” to the bullseye — meaning a document’s rank (or placement in the results) is determined by the calculated similarity *distance* of that document’s coordinates from the query’s coordinates. In which direction should ranking take precedence, which of the possible contexts is closest to the user’s intent? The image I liken it to is a scene from the movie [Stargate](https://www.youtube.com/watch?v=x3h7xz558EY&start=3&end=86), where we have the six coordinate points that intersect to tell us the destination (the bullseye) but we can’t get there without knowing the “7th symbol” - the coordinates of the starting point representing the user’s subjective intention. So rather than the relative ranking of vectors being based on an ever-expanding and undifferentiated sphere of similarity, by considering the subjective intent of the query through expressive syntax and relevance scoring, we can instead get something resembling a *cylinder* of graduated subjective relevance.

![A cylinder of graduated subjective relevance.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb49ae330d3de1fc1/6a17053ee8fbce089639fb46/1ddfaae0c1496d08d7d30419e6d2aeaeacfc0ea2-1600x544.png)

The inference capabilities of an LLM might help identify the most probable context *it has* for the query, but the problem is that *without help,* the incoming query’s coordinates can *only* be determined by how the model was originally trained.

In some ways you could say vector similarity goes to the opposite extreme from a strictly keyword match — its strength lies in its ability to overcome the issues of term mismatch, but [almost to a fault](https://medium.com/data-science/vector-embeddings-are-lossy-heres-what-to-do-about-it-4f9a8ee58bb7): LLMs tend towards unifying related concepts rather than differentiating between them. Vector similarity improves our ability to match content semantically, but doesn’t guarantee precision because it can overlook exact keywords and specific details that aren’t disambiguated enough by the model. Vector similarity search is powerful in itself, but we need ways to correlate the results we retrieve from a vector database with results from other retrieval methods.

### Reranking techniques

Now is a good time to mention a general technique called reranking, which re-scores or normalizes result sets to a unified rank order. The need for reranking could be due to results from multiple sources or retrieval methods having different ranking/scoring mechanisms (or none at all, SQL!), or re-ranking could be used to align the results from non-semantic sources to the user’s query semantically. Reranking is a second-stage operation, meaning a set of results that have been collected by some *initial retrieval* method (i.e. SQL, lexical search, vector search) are then reordered with a different scoring method.

There are several approaches available, including [Learning-To-Rank (LTR)](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr) and [Reciprocal Rank Fusion (RRF)](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) — LTR is useful for capturing search result features (likes, ratings, clicks, etc.) and using those to score and boost or bias results. RRF is perfect for merging results returned from different query modalities (e.g. lexical and vector database searches) together into a single result list. Elastic also provides the flexibility to adjust scores using [linear reranking](https://www.elastic.co/search-labs/blog/linear-retriever-hybrid-search) methods.

One of the most effective reranking techniques however is [semantic reranking](https://www.elastic.co/docs/solutions/search/ranking/semantic-reranking), which uses an LLM’s semantic understanding to analyze the vector embeddings of both the query and results together, and then apply relevance scoring/rescoring to determine the final order. Semantic reranking requires a connection to a reranking model, of course, and Elasticsearch provides an [Inference API](https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-inference) that lets you create **rerank** endpoints that leverage built-in models ([Elastic Rerank](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-rerank)), [imported](https://www.elastic.co/docs/reference/elasticsearch/clients/eland/machine-learning) third-party models, or externally-hosted services like [Cohere](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-put-cohere) or [Google Vertex AI](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-put-googlevertexai). You can then perform reranking through the [retriever](https://www.elastic.co/docs/solutions/search/retrievers-overview) query abstraction syntax:

```
POST my-index/_search 
{
  "size": 10,
  "retriever": {
    "text_similarity_reranker": {
      "retriever": {
        "rrf": {
          "retrievers": [
            {
              "standard": {
                "query": {
                  "multi_match": {
                    "query": "machine learning applications",
                    "fields": ["title", "content"]
                  }
                }
              }
            },
            {
              "knn": {
                "field": "semantic-content-field",
                "k": 10,
                "num_candidates": 100,
                "query_vector_builder": {
                  "text_embedding": {
                    "model_id": "my-text-embedding-model",
                    "model_text": "machine learning applications"
                  }
                }
              }
            }
          ],
          "rank_window_size": 50,
          "rank_constant": 20
        }
      }
    },
    "field": "content",
    "inference_id": "my-reranker",
    "inference_text": "machine learning applications",
    "rank_window_size": 20
  }
}
```

*An example multi-stage retriever reranking operation*

Sounds great, right? We can perform reranking on results from disparate sources and get close to a semantic understanding of all types of content… Semantic reranking can be expensive both computationally as well as in processing time required, and because of that, semantic reranking can only feasibly be done on a limited number of results, which means that *how* those initial results get retrieved is important.

### The context retrieval method matters

Subjective intent is an important factor in determining the accuracy of a result, in scoring its relevance. Without the ability to consider the user’s intent for performing the query (as expressed through flexible syntax, or by second-stage reranking), we can only select from the existing contexts already encoded within the model space. The way we typically address this lack of context is through techniques like [Retrieval Augment Generation (RAG)](https://en.wikipedia.org/wiki/Retrieval-augmented_generation). The way RAG works is it effectively shifts the query’s coordinates by including additional related terms returned from a pre-query for contextually relevant data. That makes the engine providing that additional context and *its* initial method for performing retrieval all the more important to the accuracy of the context!

Let’s review the different context retrieval methods and how they can help or hurt a RAG operation:

* **Hybrid search retrieval without a search engine still lacks subjective relevance.** If the platform providing RAG is primarily SQL-based underneath (which includes most “data lake” platforms), it’s lacking relevance scoring at the initial retrieval stage. Many data lake platforms provide their own version of hybrid retrieval (not search), usually combining reranking techniques like semantic reranking and RRF on their SQL-based retrieval and vector database results. A simple sort is obviously insufficient for subjective ranking, but even when used as the basis for a second-stage semantic reranking operation, SQL as the first-stage retrieval becomes a problem when the semantic reranking is performed only on the “top k” hits — without some way to score results at retrieval, what guarantee do we have that the *best* results are actually in the top results?
* **Vector similarity alone isn’t good enough for RAG**. It’s really due to a compounding set of issues - it’s the lossiness of embedding, along with naive chunking methods, with how similarity is calculated, and the crucial missing component of subjective intent. One of the main goals of RAG is to ground generative AI interactions in objective truth, both to prevent hallucinations as well as to inform the LLM about the private information it had no knowledge of during training. We can use the additional context provided through RAG to constrain and direct LLMs to consider the connections and details we know are most important to answering the question at hand. To do that, we need to use *both* semantic and lexical approaches.
* **File-based grep/regex RAG.** There are some [quarters](https://www.nicolasbustamante.com/p/the-rag-obituary-killed-by-agents) of the agentic AI universe pointing to the use of vastly enlarged context windows that access local files via grep and regex for RAG rather than external retrieval platforms. The idea is that with a much larger context window available, LLMs will be able to make conceptual connections within their own thinking space rather than relying on chunked bits and pieces and multiple retrieval methods/platforms to collect relevant information. While it’s true in theory that having an entire document delivers a fuller picture than document segments, this can only work in small data domains (or, for example, when supplying files for [vibecoding](https://en.wikipedia.org/wiki/Vibe_coding)), and even then, the initial retrieval method is a scan of all documents with a keyword-only match.

**Search is more than retrieval**

Search engines are purpose-built for making queries as fast and flexible as possible. Internally, they utilize specialized data structures for storing and retrieving different kinds of data in ways that cater to those data types. Elasticsearch provides optimized storing and querying of essentially all types of data, including unstructured/full-text lexical search (match, phrase, proximity, multi-match), fast keyword (exact match) matching and filtering, numeric ranges, dates, IP addresses, and is very flexible in how it stores document structures (e.g. nested or flattened docs). Elasticsearch is also a native vector database that can store and query both sparse and dense vector types, and we continue to explore innovative ways (for example, [Better Binary Quantization (BBQ)](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) & [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction)) to maintain search fidelity while improving the speed, scalability, and costs associated with vectorized content. The Elasticsearch platform also provides built-in data resilience and high-availability, and includes data lifecycle management capabilities such as [Searchable Snapshots](https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/searchable-snapshots) that allow you to keep infrequently-accessed or long-term retention data on cost-effective object storage — but still fully searchable.

### Hybrid search is the best of all worlds

[Hybrid search](https://www.elastic.co/what-is/hybrid-search) (not just hybrid retrieval!) combines the strengths of traditional lexical search with the semantic understanding of LLMs and vector similarity search. This synergy allows for targeting highly relevant results at the *retrieval* stage through any of the flexible query syntax options a search engine provides: intent-driven syntax options and relevance scoring, multi-modal data retrieval, filtering, aggregations, and biasing. With search syntax like [ES|QL](https://www.elastic.co/docs/reference/query-languages/esql) and multi-stage [retrievers](https://www.elastic.co/docs/solutions/search/retrievers-overview), we can flexibly combine traditional search with semantic search, filters, and multiple reranking techniques all in one request.

![How hybrid search works](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6ee9512910856ee3/6a17053fcdacbf2ea97d291e/f25180cb430414b99ae553d3b8eb161dbccea4d4-1920x1080.png)

One of the biggest benefits of hybrid search is that your queries can use specialized syntax for multiple different data types simultaneously. Those different query syntaxes can be used not just for *finding* results, they can also be used as filters or aggregations *on* the results. For example, one of the most common query types that frequently gets combined with other syntax is [geospatial analysis](https://www.elastic.co/docs/explore-analyze/geospatial-analysis). You can do things like query for results that have geo coordinates within a specified distance of a point, or request aggregations on your results by region, or aggregations to track and alert on movements into/out of a zone. With hybrid search you have the flexibility to combine syntaxes to target results in the most accurate way, to retrieve the content closest to your context.

## Intermission

This first part tells the story of how vector search has changed the way we’re able to retrieve data, and sets the stage for the changes LLMs have brought to the query mechanisms we use to interact with data. We’re going to pretend we had to break this up into multiple parts so that LLMs could understand it without losing context… ;-) Let’s learn more about *why that's important* in [Part II: Agentic AI and the need for context engineering](https://www.elastic.co/search-labs/blog/context-engineering-llm-evolution-agentic-ai), and in Part III, we’ll return to our discussion of hybrid search.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9dd95ca3f3bd2004/6a17f8153e9e457308ba165d/69d9c14dac7e255e3df6c3aa15c84ac6564c3401-720x420.jpg)

[Hybrid Search](/search-labs/blog/category/hybrid-search)

### Built with Elastic: Hybrid search for Cypris – the world’s largest innovation database

May 06, 2025|[Elastic Team](/search-labs/author/the-elastic-team)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt37c9d2971b5a2db3/6a170a75cf4f254223b2d149/492c9b5432a2b9e40cebb3b60f0df019a8c7bf6d-1280x720.png)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Vector Database](/search-labs/blog/category/vector-database)

### How to measure and improve Elasticsearch search recall: from 0.43 to 0.75 with hybrid search

May 04, 2026|[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt63218799e944e16d/6a1710ef6f7f04ee68914952/93d8e0d84fb4cfbf5e51df85df7ec2e600d9dcc7-1088x607.png)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Integrations](/search-labs/blog/category/integrations)[Java](/search-labs/blog/category/java-programming)

### Hybrid search with Java: LangChain4j Elasticsearch integration

March 11, 2026|[Laura Trotta](/search-labs/author/laura-trotta)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter