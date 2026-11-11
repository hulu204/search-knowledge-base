---
title: 'Sparse and Dense Representations'
company: Tunkelang
tag: 召回
date: 2024-04-15
url: https://dtunkelang.medium.com/sparse-and-dense-representations-f8c94f1e28e8
account: Tunkelang
origin: harvest3-202607
---
# Sparse and Dense Representations

The heart of the [AI-powered search](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b) revolution is the move from sparse [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) representations to dense [embedding](https://en.wikipedia.org/wiki/Word_embedding)-based representations. But reducing everything to a sparse vs. dense is a false dichotomy. This post explores some of the nuances of sparse and dense representations.

### Traditional Search: Sparse Queries, Sparse Documents

In the traditional [inverted index](https://en.wikipedia.org/wiki/Inverted_index) architecture, both queries and documents have sparse [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) representations. Every query and document is a vector in a [vector space](https://en.wikipedia.org/wiki/Vector_space), in which there is a dimension for each word (or [token](https://queryunderstanding.com/tokenization-c8cdd6aef7ff)) in the vocabulary.

Most queries and documents only use a tiny fraction of the vocabulary, so their vectors have a few non-zero dimension values for the words they contain, along with thousands (or even millions!) of zero values for the rest of the vocabulary. This sparse utilization of the available dimensions is the reason these vectors are called [sparse](https://en.wikipedia.org/wiki/Sparse_matrix) vectors.

Words seem inadequate as units of meaning to support search applications. With a few enhancements, however, it is possible to build robust search applications using sparse query and document representations:

- Using [character normalization](https://queryunderstanding.com/character-filtering-76ede1cf1a97) (e.g., transforming all letters to lowercase) and [token](https://queryunderstanding.com/tokenization-c8cdd6aef7ff#.h1ckkkprx) normalization (e.g., [stemming or lemmatization](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) to map singular and plural forms of a noun to the same token) reduces the vector space dimensionality while mostly preserving meaning.

- Recognizing [multiple-word phrases](https://queryunderstanding.com/let-bigrams-be-bigrams-aa6136d58fc2) (e.g., “machine learning”, “New York”) as atomic units of meaning ensures that phrases are not split up into their component words, i.e., as if they were individual tokens.

- Applying statistical heuristics like [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) or [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) to weigh query tokens by their specificity (idf stands for inverse document frequency) and their repetition within matching documents (tf stands for term frequency) can be useful for both [ranking and retrieval](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e#:~:text=We%20can%20think%20of%20retrieval,in%20the%20top%2Dranked%20results.), especially if retrieval uses [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425).

- Applying [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) using a [synonym](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) table increases [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall), e.g., matching results that contain the phrase “athletic shoes” when the query includes the token “sneakers”.

- Organizing content using a [category taxonomy](https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2) and then using [query classification](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) enables filtering or boosting results associated with the category or categories inferred for the query.

- Organizing each piece of content into fields and then using [named entity recognition](https://queryunderstanding.com/entity-recognition-763cae840a20) enables filtering or boosting results that match [query segments](https://queryunderstanding.com/query-segmentation-2cf860ade503) to the appropriate content fields.

Even with all of these enhancements, sparse query and document representations have their limitations. It is difficult for a token-based approach to completely overcome the challenges of synonymy and [polysemy](https://en.wikipedia.org/wiki/Polysemy) (a word having more than one meaning), handle multi-modal content (e.g., text and images), or incorporate [contextual](https://queryunderstanding.com/contextual-query-understanding-65c78d792dd8) signals. For these reasons, search application developers are increasingly turning to dense representations to represent meaning.

### Embedding-Based Retrieval: Dense Queries, Dense Documents

Embeddings — particularly [sentence embeddings](https://en.wikipedia.org/wiki/Sentence_embedding) — make it possible to represent both documents and queries as dense vectors in a high-dimensional space. Embeddings address a key weakness of the bag-of-words model, namely that a [reductionist](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09), token-based approach does not yield [holistic](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) representations of meaning for queries or documents.

Rather than incrementally addressing the weakness of token-based models using the methods enumerated above, embedding-based retrieval maps both queries and documents as dense vectors and then relies on [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) to measure relevance.

Embedding-based retrieval works well when the queries and documents come from the same distribution, as is the case for [content similarity](https://medium.com/content-understanding/content-similarity-d3c7a9cd7d44) applications. However, it faces challenges when there is a misalignment between queries and documents, as is often the case when queries are short and have low [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb), while documents are long and unique. This misalignment makes it difficult to represent queries and documents in the same vector space, though search application developers have tried to do so using [two-tower models](https://cloud.google.com/blog/products/ai-machine-learning/scaling-deep-retrieval-tensorflow-two-towers-architecture), [bag-of-documents models](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599), and [hypothetical document embeddings (HyDE)](https://python.langchain.com/docs/templates/hyde/).

However, a fundamental challenge for embedding-based retrieval is a misalignment not just of vector representation, but of granularity. When a query has low specificity, there is often no single result that best matches it. If the searcher’s query is “men’s jeans”, then each result is either relevant (i.e., because it is a pair of men’s jeans) or not. This use case, which is typical of many search applications, is very different from that of content similarity, where the degree of matching is truly continuous. If we take cosine similarity at face value, we are likely to see fine-grained differences among relevant results that are simply noise — or worse, systematic bias. Sometimes, [searchers just want to satisfice](https://queryunderstanding.com/helping-searchers-satisfice-through-query-understanding-10ac5320fc98).

In other words, our attempt to use holistic embedding-based retrieval to overcome the challenges of synonymy and polysemy — also known as the [vocabulary mismatch](https://en.wikipedia.org/wiki/Vocabulary_mismatch) problem — introduces a new problem of granularity mismatch. Can we solve the first problem without creating the second?

### Learned Sparse Retrieval

[Learned sparse retrieval](https://en.wikipedia.org/wiki/Learned_sparse_retrieval) attempts to reap the benefits of embeddings while preserving the benefits of sparse retrieval. It addresses the vocabulary mismatch problem not by abandoning sparse bag-of-word representations, but rather by augmenting these representations with tokens that reinforce the holistic meanings of the queries and documents, thus making the representations more robust.

In contrast to the traditional use of [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) for [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) or document expansion, learned sparse retrieval approaches like [SPLADE](https://arxiv.org/abs/2107.05720) use learned query-specific or document-specific term expansions rather than relying on expansions from a global table. By doing so, learned sparse retrieval overcomes the main weakness of traditional query and document expansion — namely, its tendency to ignore context and thus introduce false positives because of [polysemy](https://en.wikipedia.org/wiki/Polysemy). By relying on the holistic embedding-based representations of queries and documents to guide expansion, learned sparse retrieval can, at least in theory, respect and preserve context.

In practice, SPLADE and other learned sparse retrieval approaches do have some limitations. Expansions can significantly increase the number of non-zero dimension values, which makes sparse representations somewhat less sparse and thus increases the computational costs of storage and query processing. There are ways to mitigate this problem, such as the [SPLADE v2](https://arxiv.org/abs/2109.10086) strategy of only applying expansion to documents rather than to both queries and documents. Beyond the computational issues, the [precision-recall tradeoff](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b) inherent in any token expansion approach makes it inevitable that some of the retrieved results will drift in relevance from the original query intent. In practice, learned sparse retrieval works as a first-stage retrieval method. Using learned sparse retrieval effectively requires downstream [retrieval or ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) stages to optimize more for precision.

Still, learned sparse retrieval is a principled way to address the vocabulary mismatch problem while preserving the benefits of sparse retrieval.

### Query Similarity

Another way to approach the vocabulary mismatch problem is to focus on [query understanding](https://queryunderstanding.com/introduction-c98740502103) and specifically [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043). Rather than augmenting document representations, we rely on the assumption that there are far fewer distinct [query intents](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f) than distinct queries.

Focusing on query similarity allows us to reframe the vocabulary mismatch problem as that of recognizing when distinct queries represent the same — or at least highly similar — query intent. For example, by recognizing when infrequent tail queries represent the same intent as more frequent head or torso queries, we can use [query rewriting](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83) or other strategies to reuse what we have learned from the richer behavioral feedback we have more frequent queries. This approach [works especially well in e-commerce](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d).

We can see this approach as mapping queries to a sparse representation of intent. In contrast to using a reductionist bag-of-words model, our holistic approach maps a query to another query that serves as a canonical representation of its query intent. Indeed, we can think of it as starting with the vectors we might use for embedding-based retrieval, but then “rounding” them to the nearest intent in a finite enumeration of intents.

We can even turn this idea around and holistically [index documents by query intent](https://queryunderstanding.com/indexing-by-intent-6645ed26d033). Indeed, there is an elegant [duality](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599): we can use a bag-of-documents model for queries or a bag-of-queries model for documents.

Query similarity offers us another way to address the vocabulary mismatch problem without creating a granularity mismatch problem. It has its own limitations — notably, its reliance on the assumption that the number of distinct query intents is significantly smaller than the number of distinct queries. This assumption works well in e-commerce but certainly fails in some other domains. As with most things in search and in life, one size does not fit all.

### Density is not destiny.

It is easy to think of the traditional inverted index with its sparse bag-of-words representations as the legacy architecture that we need to replace with [AI-powered embedding-based retrieval](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b). As I have said elsewhere: [LLMs and RAG are great, but don’t throw away your inverted index yet](https://queryunderstanding.com/llms-and-rag-are-great-but-dont-throw-away-your-inverted-index-741d33630b7f). Do not be so eager to address the vocabulary mismatch problem that you end up creating a worse granularity mismatch problem. There is still a role in search applications for sparse representations, especially to represent low-specificity query intents. Remember, density is not destiny.
