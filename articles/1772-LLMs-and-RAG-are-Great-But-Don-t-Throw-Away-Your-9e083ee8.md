---
title: 'LLMs and RAG are Great, But Don’t Throw Away Your Inverted Index'
company: Tunkelang
tag: RAG
date: 2024-03-29
url: https://dtunkelang.medium.com/llms-and-rag-are-great-but-dont-throw-away-your-inverted-index-741d33630b7f
account: Tunkelang
origin: harvest3-202607
---
# LLMs and RAG are Great, But Don’t Throw Away Your Inverted Index Yet

[Vectors](https://en.wikipedia.org/wiki/Vector_(mathematics_and_physics)), [embeddings](https://en.wikipedia.org/wiki/Word_embedding), [large language models (LLMs)](https://en.wikipedia.org/wiki/Large_language_model), and [retrieval-augmented generation (RAG)](https://en.wikipedia.org/wiki/Prompt_engineering#Retrieval-augmented_generation) represent the cutting edge of search architecture, and it is very tempting to believe we can dispense with the traditional [inverted index](https://en.wikipedia.org/wiki/Inverted_index) architecture entirely. You should be excited about this brave new world, but you should also proceed with caution.

It is true that embedding-based retrieval addresses many pain points that challenge a traditional inverted index. Embeddings are less susceptible to [polysemy](https://en.wikipedia.org/wiki/Polysemy) (words having multiple meanings) and [synonymy](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) (multiple words having the same meaning). And embedding-based retrieval can be especially useful for handling long queries, especially compared to traditional methods like [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) and [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425).

These sound like great arguments in favor of embedding-based retrieval. So what is the catch? Why are most companies still using a traditional — or at least a hybrid — architecture? Here are some of the main reasons.

Embedding-based retrieval is powerful, but it gains that power at the price of explainability. Vectors from embeddings tend to beless explainable than [token-based representations](https://queryunderstanding.com/tokenization-c8cdd6aef7ff). While a [bag of words](https://en.wikipedia.org/wiki/Bag-of-words_model) may not be a perfect representation of content, it is at least simple and understandable. In contrast, embeddings are a black box, making it hard to understand how they affect [retrieval and ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e), and even harder to debug.

Embeddings also tend to be task-dependent. A single embedding model may not capture everything about a document or query. For example, in an e-commerce setting, an embedding might be more or less sensitive to variations in product type, brand, or size. Since embedding-based retrieval reduces relevance to a single [similarity metric](https://en.wikipedia.org/wiki/Similarity_measure), there is a risk that a single vector representation will not address all search use cases. In contrast, token-based representations, despite being simplistic, are more flexible.

There are also computational challenges. Embeddings tend to be vectors with hundreds of densely populated dimensions. That is not necessarily a showstopper, especially if the documents they represent are large. Also, there are techniques to make the representations more compact. Still, index size matters, especially when vectors need to be kept in memory to minimize the latency of accessing them. Aside from scale concerns, [exact nearest-neighbor search](https://en.wikipedia.org/wiki/Nearest_neighbor_search#Exact_methods) is not practical for most latency-sensitive applications, and even [approximate nearest-neighbor (ANN) search](https://en.wikipedia.org/wiki/Nearest_neighbor_search#Approximation_methods) is slower than performing simple set operations on an inverted index.

And then there is [ranking](https://queryunderstanding.com/minimalist-models-for-search-ranking-847c9d247f4). It is not clear how to combine the query-dependent similarity score with other ranking factors, particularly query-independent desirability factors. Ranking is never easy, but embedding-based retrieval introduces additional complexity.

Finally, there is the challenge of any operations that depend on [retrieval](https://thenoisychannel.com/2008/08/24/set-retrieval-vs-ranked-retrieval/), including result counts, filters or [facets](https://queryunderstanding.com/facets-of-faceted-search-38c3e1043592), and [explicit sorts](https://queryunderstanding.com/why-is-it-so-hard-to-sort-by-price-2a5e63899233). As we discussed in the previous section, these are hard to implement well when we lack a principled way to manage the [precision-recall tradeoff](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b).

These are serious challenges! So it is important to go into embedding-based retrieval cautiously, recognizing that, for many applications, the costs of moving to embedding-based retrieval do not justify giving up the benefits of a traditional inverted index architecture. Or at least not yet.
