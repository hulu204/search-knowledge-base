---
title: 'Semantic reranking in Elasticsearch with retrievers'
company: Elastic
tag: 排序
date: 2024-05-28
url: https://www.elastic.co/search-labs/blog/semantic-reranking-with-retrievers
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Semantic reranking in Elasticsearch with retrievers

Explore strategies for using semantic reranking to boost the relevance of top search results, including semantic reranking with retrievers.

May 28, 2024

[Adam Demjen](/search-labs/author/adam-demjen)[Nick Chow](/search-labs/author/nick-chow)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

This guide explores strategies for using semantic reranking to boost the relevance of top search results, including as direct inference call, in the context of a search experience, or as part of a simplified search flow with retrievers. Before diving into the details, let's explain what semantic reranking is and why it is important.

## What is semantic reranking?

*Semantic reranking* is a method that allows us to utilize the speed and efficiency of fast retrieval methods while layering semantic search on top of it. It also lets us immediately add semantic search capabilities to existing Elasticsearch installations out there.

With the advancement of machine learning-powered semantic search we have more and more tools at our disposal for finding matches quickly from millions of documents. However, like cramming for a final exam, optimizing for speed means making some tradeoffs, and that usually comes at a loss in fidelity.

To offset this, we see some tools emerging and becoming increasingly available on the other side of the gradient. These are much slower, but can tell how closely a document matches a query with much more accuracy.

![Semantic reranking hierarchy illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2580136fc9b2e1c2/6a17d9ede8fbce43743a17b3/09bb45a86d853a465d0912297dbefa727e5d3566-1274x642.png)

To explain some key terms: *reranking* is the process of reordering a set of retrieved documents in order to improve search relevance. In *semantic reranking* this is done with the help of a reranker machine learning model, which calculates a relevance score between the input query and each document.

![Semantic reranking overview illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltad19cc61dfd78224/6a17d9eee8fbce8e803a17b7/0bbde420b2d3f42983a4ca2936b64836d58ea988-920x357.png)

Rerankers typically operate on the top K results, a narrowed-down window of relevant candidates fulfilling the search query, since reranking a large list of documents would be extremely costly.

## Why is semantic reranking important?

Semantic reranking is an important refinement layer for search users for a couple of reasons.

First, users are expecting more from their search, where the right result isn't in the top ten hits or in the first page, but is the **top answer**. It's like that old search joke - the best place to hide a secret is in the second page of search results. Except today it's even more narrow: anything below the top one, two, or maybe three results will likely get discarded.

This applies even more so for **RAG (Retrieval Augmented Generation)** - those Generative AI use cases need a tight context window. The best document could be the 4th result, but if you're only feeding in the top three, you aren't going to get the right answer, and the model could hallucinate.

On top of that, Generative AI use cases work best with an **effective cutoff**. You could define a minimum score or count up to which the results are considered "good", but this is hard to do without consistent scoring.

**Semantic reranking solves these problems by reordering the documents so that the most relevant ones come out on top.** It provides usable, normalized and well-calibrated scores, so you can measure how closely your results match your query. So you more reliably get much more accurate top results to feed to your large language model, and you can cut off results if there's a big dropoff in score in the top K hits to prevent hallucinations.

## How do we perform semantic reranking?

### The `rerank` inference type

Elastic recently introduced *inference endpoints* and related [APIs](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html). This feature allows us to use certain services, such as built-in or 3rd party machine learning models, to perform inference tasks. Supported inference tasks come in various shapes - for example a `sparse_embedding` task is where an ML model (such as ELSER) receives some text and generates a weighted set of terms, whereas a `text_embedding` task creates vector embeddings from the input.

Elastic Serverless - and the upcoming 8.14 release - adds a new task type: `rerank`. In the first iteration `rerank` supports integrating with [Cohere](https://cohere.com)'s Rerank API. This means you can now create an inference endpoint in Elastic, supply your Cohere API key, and enjoy semantic reranking out of the box!

Let's see that in action with an example taken from the [Cohere blog](https://cohere.com/blog/rerank).

Assuming you have set up your `rerank` inference endpoint in Elastic with the Cohere Rerank v3 model, we can pass a query and an array of input text. As we can see, the short passages all relate to the word "capital", but not necessarily to the meaning of the location of the seat of government, which is what the query is looking for:

```
POST _inference/rerank/cohere-rerank-v3-model
{
  "query": "What is the capital of the USA?",
  "input": [
    "Carson City is the capital city of the American state of Nevada. At the 2010 United States Census, Carson City had a population of 55,274.",

    "Capital punishment (the death penalty) has existed in the United States since before the United States was a country. As of 2017, capital punishment is legal in 30 of the 50 states.",

    "The Commonwealth of the Northern Mariana Islands is a group of islands in the Pacific Ocean that are a political division controlled by the United States. Its capital is Saipan.",

    "Washington, D.C. (also known as simply Washington or D.C., and officially as the District of Columbia) is the capital of the United States. It is a federal district.",

    "Charlotte Amalie is the capital and largest city of the United States Virgin Islands. It has about 20,000 people. The city is on the island of Saint Thomas.",

    "North Dakota is a state in the United States. 672,591 people lived in North Dakota in the year 2010. The capital and seat of government is Bismarck."
  ]
}
```

The rerank task responds with an array of scores and document indices:

```
{
  "rerank": [
    {
      "index": "3",
      "relevance_score": "0.99838966"
    },
    {
      "index": "1",
      "relevance_score": "0.587174"
    },
    {
      "index": "0",
      "relevance_score": "0.061199225"
    },
    {
      "index": "2",
      "relevance_score": "0.032283258"
    },
    {
      "index": "4",
      "relevance_score": "0.015365342"
    },
    {
      "index": "5",
      "relevance_score": "0.0040072887"
    }
  ]
}
```

The topmost entry tells us that the highest relevance score of 99.8% is the 4th document (`"index": 3` with zero-based indexing) of the original list, a.k.a. `"Washington, D.C. ..."`. The rest of the documents are semantically less relevant to the original query.

This reranking inference step is an important puzzle piece of an optimized search experience, and now we are ready to place it in the puzzle board!

### Reranking search results today - through your application

One way of harnessing the power of semantic reranking is to implement a workflow like this in a search application:

1. A user enters a query in your app's UI.
2. The search engine component retrieves a set of documents that match this query. This can be done using any retrieval strategy: lexical (BM25), vector search (e.g. kNN) or a method that combines the two, such as RRF.
3. The application takes the top K documents, extracts the text field we are querying against from each document, then sends this list of texts to the `rerank` inference endpoint, which is configured to use Cohere.
4. The inference endpoint passes the documents and the query to Cohere.
5. The result is a list of scores and indices to match each score. Your app takes these scores, assigns them to the documents, and reorders them by this score in a descending order. This effectively moves the semantically most relevant documents to the top.
6. If this flow is used in RAG to provide some sources to a generative LLM (such as summarizing an answer), then you can rest assured it will work with the right context and provide answer.

![Semantic reranking through your application illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt871430541f188e85/6a17d9f00b0bed6e92dd3455/6615fba5f7cbcf8f00d519de1ecc0cd47c07c089-1190x1038.png)

This works great, but it involves many steps, data massaging, and a complex processing logic with many moving parts. Can we simplify this?

### Reranking search results tomorrow - with retrievers

Let's spend a minute talking about retrievers. [*Retriever*](https://www.elastic.co/search-labs/blog/elasticsearch-retrievers) is a new type of abstraction in the `_search` API, which is more than just a simple query. It's a building block for an end-to-end search flow for fetching hits and potentially modifying the documents' scores and their order.

Retrievers can be used in a pipeline pattern, where each retriever unit does something different in the search process. For example we can configure a first-stage retriever to fetch documents, pass the results to a second-stage retriever to combine with other results, trim the number of candidates etc. As a final stage, a retriever can update the relevance score of documents.

Soon we'll be adding new reranking capabilities with retrievers, **text similarity reranker retriever** being the first one. This will perform reranking on top K hits by calling a `rerank` inference endpoint. The workflow will be simplified into a *single API call* that hides all the complexity!

This is what the previously described multi-stage workflow looks like as a single retriever query:

![Semantic reranking with retriever illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd33df9a42498133f/6a17d9f13e9e450280ba132b/1f5f435df3e8ecd26ee74c8cab9bc94dc33a927d-1190x768.png)

The `text_similarity_reranker` retriever is configured with the following details:

* Nested retriever
* Reranker inference configuration
* Additional controls, such as minimum score cutoff for eliminating irrelevant hits

Below is an example `text_similarity_reranker` query. Let's dissect it to understand each part better!

```
POST my-index/_search
{
  "retriever": { // Retriever query
    "text_similarity_reranker": { // Outermost retriever will perform reranking
      "retriever": {
        "standard": { // First-stage retriever is a standard Elasticsearch query
          "query": {
            "match": { // BM25 matching
              "text": "What is the capital of the USA?"
            }
          }
        }
      },
      "field": "text", // Document field to send to reranker
      "rank_window_size": 100, // Reranking will work on top K hits
      "inference_id": "cohere-rerank-v3-model", // Inference endpoint
      "inference_text": "What is the capital of the USA?",
      "min_score": 0.6 // Minimum relevance score
    }
  }
}
```

The request defines a `retriever` query as the root property. The outermost retriever will execute last, in this case it's a `text_similarity_reranker`. It specifies a `standard` first-stage retriever, which is responsible for fetching some documents. The `standard` retriever accepts an Elasticsearch `query`, which is a BM25 `match` in the example.

The text similarity reranker is pointed at the `text` document field that contains the text for semantic reranking. The top 100 documents will be sent for reranking to the `cohere-rerank-v3-model` rerank inference endpoint we have configured with Cohere. Only those documents will be returned that receive at least 60% relevance score in the reranking process.

The response is the exact same structure as that of a `search` query. The `_score` property is the semantic relevance score from the reranking process, and `_rank` refers to the ranking order of documents.

```
{
  "took": 213,
  "timed_out": false,
  "_shards": {
    "total": 5,
    "successful": 5,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 1,
      "relation": "eq"
    },
    "max_score": 0.99838966,
    "hits": [
      {
        "_index": "my-index",
        "_id": "W7CDBo8BJDa_bRWhW1KH",
        "_score": 0.99838966,
        "_rank": 1,
        "_source": {
          "text": "Washington, D.C. (also known as simply Washington or D.C., and officially as the District of Columbia) is the capital of the United States. It is a federal district."
        }
      }
    ]
  }
}
```

Semantic reranking with retrievers will be available shortly in a coming Elastic release.

## Conclusion

Semantic reranking is an incredibly powerful tool for boosting the performance of a search experience or a RAG tool. It can be used as direct inference call, in context of a search experience, or as part of a simplified search flow with retrievers. Users can pick and choose the set of tools that work best for their use case and context.

Happy reranking! 😃

### Frequently Asked Questions

#### What is semantic reranking in Elasticsearch?

Semantic reranking is a method that allows us to utilize the speed and efficiency of fast retrieval methods while layering semantic search on top of it. It also lets us immediately add semantic search capabilities to existing Elasticsearch installations.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter