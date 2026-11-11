---
title: 'What is semantic reranking and how to use it?'
company: Elastic
tag: 排序
date: 2024-10-29
url: https://www.elastic.co/search-labs/blog/elastic-semantic-reranker-part-1
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# What is semantic reranking and how to use it?

Introducing the concept of semantic reranking. Learn about the trade-offs using semantic reranking in search and RAG pipelines.

October 29, 2024

[Thomas Veasey](/search-labs/author/thomas-veasey)[Quentin Herreros](/search-labs/author/quentin-herreros)[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)

[ML Research](/search-labs/blog/category/ml-research)[Relevance](/search-labs/blog/category/relevance)

Part of the series:

[Semantic reranking & the Elastic Rerank model](/search-labs/blog/series/semantic-reranking-and-the-elastic-rerank-model)

In this series

Share

In this series of blogs we'll introduce Elastic's new semantic reranker. Semantic reranking often improves relevance, particularly in a zero-shot setting. It can also be used to trade-off indexing compute cost for querying compute cost by significantly improving lexical retrieval relevance.

In this first blog we set the scene with some background on semantic reranking and how it can fit into your search and RAG pipelines. In the second installment, we introduce you to [Elastic Rerank: Elastic's new semantic re-ranker model](https://www.elastic.co/search-labs/blog/elastic-semantic-reranker-part-2) we've trained and released in technical preview.

## Retrieval

Typically, text search is broken down into multiple stages, which gradually filter the result set into the final list that is presented to a user (or an LLM).

The first stage is called retrieval and must be able to scale to efficiently compare the query text with a very large corpus of candidate matches. This limits the set of approaches that one can consider.

For many years, the only paradigm available for retrieval was lexical. Here documents and queries are treated as bags of words and a statistical model is used to deduce relevance. The most popular option in this camp is BM25. For this choice, the query can be efficiently compared with a huge document corpus using inverted indices together with [clever optimisations](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand) to prune non-competitive candidates. It remains a useful option since many queries, such as keyword searches and exact phrase matching, are well aligned with this model and it is easy to efficiently apply filtering predicates at the same time. The scoring is also tailored to the corpus characteristics which makes it a strong baseline when no tuning is applied. Finally, it is particularly efficient from an indexing perspective: no model inference needs to run, updating index data structures is very efficient and a lot of state can permanently reside on disk.

In recent years, semantic retrieval has seen a surge in popularity. There are multiple flavors of this approach; for example, [dense passage](https://arxiv.org/pdf/2212.03533), [learned sparse](https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance) and [late interaction](https://arxiv.org/pdf/2004.12832) retrieval. In summary, they use a transformer model to independently create representations of the query and each document and define a distance function on these representations to capture semantic similarity. For example, the query and document might be both embedded into a high dimensional vector space where queries and their relevant documents have low angular separation. These sorts of approaches have different strengths to BM25: they can find matches that require understanding synonyms, where the context is important to determine word meanings, where there are misspellings and so on. They also allow for wholly new relevance signals, such as embedding images and text in a common vector space.

Queries can be efficiently compared against very large corpuses of documents by dropping the requirement that exact nearest neighbor sets are found. Data structures like [HNSW](https://en.wikipedia.org/wiki/Hierarchical_navigable_small_world) can be used to find most of the best matches in logarithmic complexity in the corpus size. [Intelligent compression schemes](https://www.elastic.co/search-labs/blog/int4-scalar-quantization-in-lucene) allow significant amounts of data to reside on disk. However, it is worth noting that model inference must be run on all documents before indexing and these data structures are relatively expensive to build in comparison to inverted indices.

A lot of work has been done to improve the training of general purpose semantic retrieval models and indeed the best models significantly outperform BM25 in [benchmarks](https://huggingface.co/spaces/mteb/leaderboard) that try and assess zero shot retrieval quality.

## Semantic reranking

So far we have discussed methods that independently create representations of the query and document. This choice is necessary to scale retrieval. However, given the top N results returned by first stage retrieval we don't have the same constraint. The work that must be done to compare the query and these top N results is naturally much smaller, so we can consider new approaches for reordering them in order to improve relevance of the final result. This task is called reranking.

We define semantic reranking as using a model to assess the semantic similarity of a query and one (or more) document text(s). This is to distinguish it from other reranking methods such as [learn to rank](https://www.elastic.co/search-labs/blog/elasticsearch-learning-to-rank-introduction), which typically use a variety of features to model user preference. Note that what constitutes semantic similarity can vary from task to task: for example, finding similar documents requires assessing similarity of two texts, whereas answering a question requires understanding if the necessary information is contained in the document text.

In principle, any semantic first stage retrieval method can be used for reranking. For example, [ELSER](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-1) could be used to rerank the top results of a BM25 search. Keep in mind though that there may be blindspots in BM25 retrieval, which tends to have lower recall than semantic retrieval, and no reranking method will be able to fix these. It is therefore important to evaluate setups like these on your own data.

From a performance standpoint, one is trading indexing compute cost for querying compute cost and possibly latency. Compared to semantic retrieval, in addition to the cost of embedding the query, you must also embed each document you want to rerank. This can be a good cost trade-off if you have a very large corpus and/or one which is frequently updated and relatively few queries per second. Furthermore, for GPUs the extra cost is partly amortized by the fact that the document inferences can be processed as a batch, which allows for better utilization. However, there is little cost benefit compared to a model which gets to see the query and the document at the same time. This approach is called cross-encoding, as opposed to bi-encoding which is used for semantic retrieval, and can bring significant benefits.

## Cross-encoders

For cross-encoders both the query and a document text are presented together to the model concatenated with a special separation token. The model itself returns a similarity score. Schematically, the text is modeled something like the following:

![cross-encoder schematic](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt114125634c8c5b06/6a1703f0cdacbf205a7d28e6/ad9f34589b33a019c4550f75ff13b5c8dbe14347-1260x896.png)

In a bi-encoder the query and the document are first embedded individually and then compared using a simple similarity function. Schematically, the text is modeled something like the following:

![bi-encoder schematic](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6bc8ce247c6c5995/6a1703f24a531b427d36a833/f2c420a567a4371f80b62dc8a6960a8a5741ca68-1260x855.png)

Reranking for a fixed query with a cross-encoder is framed as a regression problem. The model outputs a numerical scores for each query-document pair. Then the documents are sorted in descending score order. We will return to the process by which this model is trained in the second blog in this series. Conceptually, it is useful to realize that this allows the model to attend to different parts of the query and document text and learn rich features for assessing relevance.

[It has been observed](https://arxiv.org/pdf/2212.06121) that this process allows the model to learn more robust representations for generally assessing relevance. It also potentially allows the model to capture more nuanced semantics. For example, bi-encoder models struggle with things like negation and instead tend to pick up on matches for the majority concepts in the text, independent of whether the query wants to include or exclude them. Cross-encoder models have the capacity to learn how negation should affect relevance judgments. Finally, cross-encoder scores are often better calibrated across a diverse range of query types and topics. This makes choosing a score at which to drop documents significantly more reliable.

## Connection with RAG

Improving the content supplied to an LLM improves the quality of RAG. Indeed search quality is often the bottleneck for RAG performance. For example, if the information needed to respond correctly to a question is contained exclusively in a specific document, that document must be provided in the LLM context window. Furthermore, whilst the current generation of long context models are excellent at extracting information from long contexts, the cost to process the extra input tokens is significant and money spent on search typically yields large overall [cost efficiencies](https://www.arxiv.org/pdf/2407.16833). RAG use cases generally also have looser latency constraints, so some extra time spent in reranking is less of an issue. Indeed, the latency can also be offset by reducing the generation time if fewer passages need to be supplied in the prompt to achieve the same recall. This makes semantic reranking especially well suited to be applied in RAG scenarios.

## Wrapping Up

In this post we introduced the concept of semantic reranking and discussed how model architecture can be tailored to this use case to improve relevance, particularly in a zero shot setting. We discussed the performance trade-offs associated with semantic reranking as opposed to semantic retrieval. A crucial choice when discussing performance in this context is how many documents to rerank, which critically affects the trade-off between performance and relevance of reranking methods. We will pick up this topic again when we discuss how to evaluate reranking models and survey some state of the art open and closed reranking models.

In the second installment of this series, we introduce you to [Elastic Rerank: Elastic's new semantic re-ranker model](https://www.elastic.co/search-labs/blog/elastic-semantic-reranker-part-2) we've trained and released in technical preview.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt950edbc25d291821/6a6119f01b1d495dc56f181b/31783975126874424fc20c3c96bd95fe28d5f201-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

### How Elasticsearch auto-tunes vector quantization to hit your recall target

July 21, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter