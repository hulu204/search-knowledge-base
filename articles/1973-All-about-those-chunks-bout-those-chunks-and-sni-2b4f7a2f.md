---
title: 'All about those chunks, ’bout those chunks, and snippets!'
company: Elastic
tag: RAG
date: 2026-01-26
url: https://www.elastic.co/search-labs/blog/llm-chunking-snippet-extraction
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# All about those chunks, ’bout those chunks, and snippets!

Exploring chunking and snippet extraction for LLMs, highlighting enhancements for identifying the most relevant chunks and snippets to send to models such as rerankers and LLMs.

January 26, 2026

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Relevance](/search-labs/blog/category/relevance)[AI](/search-labs/blog/category/ai)

Jump to

Share

These days, if you’ve performed semantic searches or context engineering, you’ve probably worked a lot with chunks. If you’re not familiar with chunks, a *chunk* is a small, meaningful piece of content extracted from a larger document. This [blog](https://www.elastic.co/search-labs/blog/chunking-strategies-elasticsearch) provides a great foundational overview of chunking, why it’s important, and various chunking strategies.

For this blog, we want to focus on one specific problem in the topic of chunking, and that is defining the best context to send to a large language model (LLM) or other model. Models have a limited number of tokens they can take in as context, but even within that limit, sending in large amounts of content can lead to relevance degradation caused by factors such as [context rot](https://research.trychroma.com/context-rot) or [“lost in the middle”](https://arxiv.org/abs/2307.03172) problems, where important information hidden in large blocks of text is overlooked.

This led to the question: How can we make this better?

## Reranking in retrievers

We started by looking at retrievers, specifically the [`text_similarity_reranker`](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/text-similarity-reranker-retriever) [retriever](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/text-similarity-reranker-retriever). We know that many [cross-encoder](https://www.elastic.co/docs/solutions/search/ranking/semantic-reranking#semantic-reranking-models) rerankers do not perform well on long documents. This is because these rerankers will truncate long content to the model’s token window, discarding the remaining content. This can actually lead to degraded search relevance, if the most relevant part of the document is cut off before being sent to the reranker!

We decided to address this by introducing a `chunk_rescorer` to the `text_similarity_reranker` retriever. When specified, rather than sending in the entire document to the reranker, we will chunk the document first and evaluate each chunk based on the reranking inference text. We do this by indexing each chunk into a temporary in-memory Lucene index and performing a BM25 [text search](https://www.elastic.co/docs/solutions/search/full-text) over these chunks. We return the best chunks for consideration into the reranker.

The chunk rescorer is simple to use with a small update to the API call:

```
GET books/_search
{
  "retriever": {
    "text_similarity_reranker": {
      "retriever": {
        "standard": {
          "query": {
            "match": {
              "author": "Tolkien"
            }
          }
        }
      },
      "rank_window_size": 10,
      "field": "semantic_text",
      "inference_text": "are all who wander lost?",
      "chunk_rescorer": {
        "size": 1
      }
    }
  }
}
```

When we evaluated the chunk rescorer, we found a significant improvement for many truncating models, including the [Elastic Reranker](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-rerank) and [Cohere's](https://docs.cohere.com/docs/rerank) `rerank-english-v3.0` model. However, when we evaluated against [`jina-reranker-v2-base-multilingual`](https://huggingface.co/jinaai/jina-reranker-v2-base-multilingual), the results were not as impressive due to the fact that Jina already addresses this long document problem internally.

We performed evaluations using the [Multilingual Long-Document Retrieval](https://huggingface.co/datasets/Shitao/MLDR) (MLDR) English dataset. This is a document containing very long article content that would trigger this document truncation issue in many reranking models. The following table shows our evaluation results with BM25 text search and a `rank_window_size` of 32:

| Reranker model | NDCG@10 | NDCG@10 NDCG@10 with chunk rescoring |
| --- | --- | --- |
| jina-reranker-v2-base-multilingual | 0.771145 | 0.764488 |
| Cohere rerank-english-v3.0 | 0.592588 | 0.707842 |
| .rerank-v1-elasticsearch | 0.478121 | 0.751994 |

It’s worth noting that the raw BM25 results without reranking had a [Normalized Discounted Cumulative Gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) (NDCG) score, or relevance score, close to 0.64. (Find additional background in this [paper](https://arxiv.org/pdf/2402.03216).) This means that for rerankers that perform truncation, reranked results for long documents were actually *worse* than without reranking. Note that this only applies for long documents; shorter documents that fit into the token window would not be affected by this long document problem.

Of the rerankers we evaluated, Jina was the only reranker to perform well against long documents out of the box, thanks to its sliding window approach.

We saw better baseline performance but similar overall difference in results when using [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text) fields with [Elastic Learned Sparse EncodeR (ELSER)](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-elser).

We felt the results for truncating models were promising enough to release the chunk rescorer as an opt-in feature for models that will benefit from the additional relevance, but we recommend evaluating against specific rerankers before implementing this in production.

## ES|QL

The real power of chunk extraction, however, lies in the [Elasticsearch Query Language](https://www.elastic.co/docs/reference/query-languages/esql) (ES|QL). We wanted chunks and snippets to be first class citizens in ES|QL so they could be easily extracted and repurposed for reranking, sending into LLM context, or other purposes.

We started by introducing the [`CHUNK`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/string-functions#esql-chunk) function in Elasticsearch version 9.2:

```
FROM books
| EVAL chunks = CHUNK(description)
```

`CHUNK` is an extreme primitive that takes some string content (a text field, a semantic text field, or any other row content that is a string) and chunks it. You can view and interact with these chunks, and you can also explore using different chunking settings:

```
FROM books
| EVAL chunks = CHUNK(description, {"strategy": "sentence", "max_chunk_size": 25, "sentence_overlap": 0})
```

You can then combine chunk with existing primitives, like [`MV_SLICE`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/mv-functions#esql-mv_slice) and [`MV_EXPAND`](https://www.elastic.co/docs/reference/query-languages/esql/commands/mv_expand), to format the way chunks are represented in your row output:

```
FROM books
| WHERE MATCH(author, "Tolkien")
| EVAL chunks = CHUNK(semantic_description, {"strategy": "sentence", "max_chunk_size": 25, "sentence_overlap": 0})
| EVAL truncated = MV_SLICE(chunks, 0, 2)
| MV_EXPAND truncated
| KEEP title, truncated
```

This is great, but what we really wanted was to get the top matching snippets for a query, so we also introduced [`TOP_SNIPPETS`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/search-functions#esql-top_snippets) in Elasticsearch version 9.3:

```
FROM books
| EVAL snippets = TOP_SNIPPETS(description, "ring")
```

We added support to control the number of snippets you want to return and the word size using a sentence-based [chunking strategy](https://www.elastic.co/search-labs/blog/chunking-strategies-elasticsearch):

```
FROM books
| EVAL snippets = TOP_SNIPPETS(description, "ring", { "num_snippets": 3, "num_words": 25 })
| MV_EXPAND snippets
| KEEP title, snippets
```

This fits into the broader story of LLMs when you add in [`COMPLETION`](https://www.elastic.co/docs/reference/query-languages/esql/commands/completion). Here is an example of how we envision `TOP_SNIPPETS` integrating with LLMs:

```
FROM books METADATA _score
| WHERE semantic_description:"what are hobbits?"
| SORT _score DESC
| LIMIT 10
| FORK
   ( EVAL snippets = TOP_SNIPPETS(semantic_description, "what are hobbits?", {"num_snippets": 3})
    | COMPLETION CONCAT("Answer what are hobbits", snippets) WITH {"inference_id": "my-completion-endpoint"})
```

In this example, we’re performing a semantic search, but for each document we’re identifying the top snippets from that document. We’re sending in the highly relevant snippets into the completion command, rather than the entire document. This is a simple document, but you could also use reranking here, and in the future, when multiple forks are available, hybrid search will be supported in the same format.

We can also utilize snippets in the newest version of `RERANK`:

```
FROM books
| WHERE MATCH(title, "ring")
| EVAL snippets = TOP_SNIPPETS(semantic_description, "what are hobbits?", { "num_snippets": 3, "num_words": 25 })
| RERANK "what are hobbits?" ON  snippets WITH { "inference_id" : "my-reranker" }
```

## What we’re thinking about next

The story isn’t over for chunking and snippet extraction; in fact, it’s only getting started.

We’re looking at how to best integrate existing `semantic_text` chunks out of the box into strategies using chunking and snippet extraction. We’re also exploring what other features we need to make snippet extraction a compelling feature to use in products such as Elastic Agent Builder.

Overall, we’re excited to share these tools and look forward to your feedback as we evolve our strategies for getting the best context for LLMs!

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt021070497c8cbd23/6a170aeab0367d782c72bd0e/c506a0f5c0a33ca6f85454d4f742d7cb266a7b78-715x413.png)

[Relevance](/search-labs/blog/category/relevance)

### ES|QL, you know, for Search - Introducing scoring and semantic search

April 16, 2025|[Ioana](/search-labs/author/ioana-alina-tagirta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter