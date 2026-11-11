---
title: 'AI-Powered Search: Embedding-Based Retrieval and Retrieval-Augmented Generation (RAG)'
company: Tunkelang
tag: RAG
date: 2024-04-08
url: https://dtunkelang.medium.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b
account: Tunkelang
origin: harvest3-202607
---
# AI-Powered Search: Embedding-Based Retrieval and Retrieval-Augmented Generation (RAG)

When search application developers consider replacing a [traditional search architecture](https://en.wikipedia.org/wiki/Inverted_index) with [AI-powered search](https://queryunderstanding.com/analyzing-the-ai-search-opportunity-cb7ee6f761de), they usually have two things in mind. The first is replacing [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) representations with [embeddings](https://en.wikipedia.org/wiki/Word_embedding). The second is implementing [retrieval-augmented generation (RAG)](https://www.nvidia.com/en-us/glossary/retrieval-augmented-generation/), which typically combines embedding-based retrieval with [generative AI](https://en.wikipedia.org/wiki/Generative_artificial_intelligence).

This post explains the main ideas of embedding-based retrieval and RAG, with an emphasis on the pitfalls awaiting the unwary.

## Replacing Bags of Words with Embeddings

Search has always been concerned with representing language, to make sense of the text that comprises both [content](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974) and [queries](https://queryunderstanding.com/introduction-c98740502103).

### Bag-of-Words Model

A simple way to represent language as a [bag of words](https://en.wikipedia.org/wiki/Bag-of-words_model). Mathematically, the bag-of-words model is a [vector space](https://en.wikipedia.org/wiki/Vector_space) that assigns one dimension to each word in the language. To represent a document or query in this space, we create a [sparse](https://en.wikipedia.org/wiki/Sparse_matrix) vector whose coordinates are 1 for each word (or [token](https://queryunderstanding.com/tokenization-c8cdd6aef7ff)) it contains and 0 for all other words. Rather than making all of the non-zero values equal, we can weigh the values according to how often a word is repeated within a document or query. We can also consider the frequency of words within the content or queries: less frequent words are more likely to be important. Combining these two ideas yields a weighting scheme called the [term frequency-inverse document frequency](https://en.wikipedia.org/wiki/Tf%E2%80%93idf), commonly abbreviated as [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf), and a related measure called [BM25](https://en.wikipedia.org/wiki/Okapi_BM25).

The bag of words model makes it easy to measure the similarity between a pair of documents, a pair of queries, or — most importantly — a document and a query. Mathematically, we simply compute the [cosine](https://en.wikipedia.org/wiki/Cosine_similarity) of the angle between the two vectors. We obtain the cosine by computing the [dot product](https://en.wikipedia.org/wiki/Dot_product): for each dimension, we take the product of its values from the two vectors, then compute the sum of the products of each pair of coordinates, and then take their sum. Since anything multiplied by 0 equals 0, only the words shared by the two documents or queries contribute to the dot product. We then [normalize](https://en.wikipedia.org/wiki/Unit_vector) by the vector lengths to obtain the cosine.

Words carry meaning, but they are challenging to work with as units of meaning. Word-based representations break down when multiple words convey the same meaning ([grammatical variation](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45), [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741), etc.), or when a single word can convey multiple meanings (also known as [polysemy](https://en.wikipedia.org/wiki/Polysemy)). Word-based representations also fail to account for [multi-word phrases](https://queryunderstanding.com/query-segmentation-2cf860ade503) that lose their meaning when broken up into their component words. Search needs something better than words as units of meaning.

### Embeddings

Computer scientists working with language have been aware of these challenges for decades, going back to work on [factor analysis](https://en.wikipedia.org/wiki/Factor_analysis) for [document classification](https://en.wikipedia.org/wiki/Document_classification) in the 1960s. Their efforts led to developments like [latent semantic indexing (LSI)](https://en.wikipedia.org/wiki/Latent_semantic_analysis) and [latent Dirichlet allocation (LDA)](https://en.wikipedia.org/wiki/Latent_Dirichlet_allocation).

But the real breakthrough for language understanding started with [word2vec](https://en.wikipedia.org/wiki/Word2vec) in 2013. The intuition behind word2vec and subsequent embeddings is that “a word is characterized by the company it keeps”, an idea popularized in the 1950s by linguist [John Rupert Firth](https://en.wikipedia.org/wiki/John_Rupert_Firth).

Embeddings have advanced at a frenetic pace in the last several years, with models like [GloVe](https://en.wikipedia.org/wiki/GloVe), [fastText](https://en.wikipedia.org/wiki/FastText), and [BERT](https://en.wikipedia.org/wiki/BERT_(language_model)) emerging from research labs and rapidly finding their way into production search applications. A key breakthrough has been the emergence of [transformer](https://en.wikipedia.org/wiki/Transformer_(deep_learning_architecture)) models that use an [attention mechanism](https://en.wikipedia.org/wiki/Attention_(machine_learning)) to determine what parts of the text carry meaning.

Embeddings make it possible to represent both documents and queries as dense vectors in a high-dimensional space. The first step is transforming each document or query into a single text string.

### Document Embeddings

For documents, the process typically involves selecting and combining fields (e.g., title, abstract), [normalizing the text](https://queryunderstanding.com/character-filtering-76ede1cf1a97) (e.g., converting to lowercase, removing accents), and other transformations. The idea is to preserve as much signal as possible while minimizing noise. The resulting string is the input for a model that converts it into a vector.

### Query Embeddings

For queries, the process is a bit trickier. Since a search query is already a single string, there is no need to convert it into one. We just have to apply a model to that string. But what model? The simplest approach is to use the same model used for document strings, but this approach has drawbacks. It relies on queries being similar to document strings in vocabulary, format, size, and style, and can break down if this is not the case — such as when queries are significantly shorter than document strings.

When queries are substantially different from documents, an alternative is to train two models, one for documents and one for queries, in what is known as a [two-tower model](https://cloud.google.com/blog/products/ai-machine-learning/scaling-deep-retrieval-tensorflow-two-towers-architecture). Another approach is to transform query vectors into document vectors, either using a [bag-of-documents model](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599) or [hypothetical document embeddings (HyDE)](https://python.langchain.com/docs/templates/hyde/).

Which approach works best depends on the application, as well as the available budget for exploration and experimentation. However, it is important to prepare for the challenge of aligning document and query embeddings. In my personal experience, the failure to address this challenge is often the root cause of poor embedding-based retrieval.

### Retrieval

Once a search application can map documents and queries to dense vectors, retrieval is fairly straightforward. For a small index, an application can compute the [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) between the query vector and every document vector, and then use the resulting scores to filter and rank results. This brute-force approach is impractical at scale, so embedding-based retrieval relies on specialized data structures, such as [hierarchical navigable small world (HNSW) graphs](https://en.wikipedia.org/wiki/Hierarchical_Navigable_Small_World_graphs) that support efficient [approximate nearest-neighbor retrieval](https://en.wikipedia.org/wiki/Nearest_neighbor_search#Approximation_methods).

### Ranking

For ranking, cosine similarity is an important ranking factor, but it usually needs to be combined with other factors — particularly, query-independent factors that reflect [desirability](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b). At best, cosine similarity can be used as the only query-dependent factor, summarizing relevance in a single number.

However, it is difficult to establish an absolute cosine similarity threshold to guarantee relevance. In general, we need to take cosine similarity with a grain of salt when we use it to measure relevance. A large difference in cosine similarity usually indicates a meaningful gap in relevance, but a small one may simply be noise, reflecting the inherent limits of our vector representation. There can also be systematic bias from misaligned embeddings (e.g., cosine similarity favoring shorter document strings).

Moreover, it can be unclear how to best combine cosine similarity with other ranking factors. Introducing it into a hand-tuned model with linear weights is probably a bad idea since the behavior of cosine similarity is hardly linear (e.g., a similarity of 0.5 is not half as good as a similarity of 1.0). So it is a good idea to use a [machine-learned ranking (LTR)](https://en.wikipedia.org/wiki/Learning_to_rank) approach that plays well with [nonlinearity](https://en.wikipedia.org/wiki/Nonlinear_system), such as the tree-based [XGboost](https://en.wikipedia.org/wiki/XGBoost).

## Retrieval-Augmented Generation (RAG)

Retrieval-augmented generation starts with retrieval, which is typically — though not necessarily — embedding-based retrieval as described above.

### Query Rewriting

That’s not quite right. There is usually a step that takes place before retrieval: [query rewriting](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83). Query rewriting automatically transforms search queries to better represent the searcher’s intent. Query rewriting is for search applications what [prompt engineering](https://en.wikipedia.org/wiki/Prompt_engineering) is for [generative AI](https://en.wikipedia.org/wiki/Generative_artificial_intelligence): an attempt to translate the query into a better representation for retrieval.

Query rewriting can be critically important for AI-powered search, especially if the goal is to enable searchers to interact using natural, conversational language rather than short keyword queries. Indeed, for complex requests, it may be helpful to decompose the query into multiple queries that are executed in parallel (e.g., to perform a comparison) or in series (e.g., using the results from one query to construct another one).

### Chunking

And there’s even another step that happens before retrieval. While traditional search has historically focused on retrieving documents as results, AI-powered search — and RAG in particular — tends to focus on information that resides in small portions of documents.

Hence, a critical part of indexing content for RAG applications is [content segmentation](https://medium.com/content-understanding/content-structure-34aa2bd9d134), more commonly known as chunking. Chunking splits each document into smaller, more coherent chunks. The chunks then become the documents that are mapped to vectors and retrieved at query time.

There are many different chunking strategies, from naively splitting into fixed-size blocks (e.g., 256 characters) to using machine-learned models trained on documents labeled with chunk boundaries. The topic of chunking strategies deserves a much longer discussion, and other folks have written posts about it that you can [easily find on Google](https://www.google.com/search?q=chunking+rag).

What is important to recognize is how much chunking matters for embedding-based retrieval and RAG. For either of these approaches to be effective, the objects being retrieved — that is, the chunks — must align reasonably well with query intents. If the chunks are too granular or not granular enough, or if the chunks do not preserve key information from their document context, then it is unlikely that the resulting chunk vectors will align with those from queries.

### Retrieval

Finally, we can return to retrieval! Retrieval takes the query — after whatever query rewriting takes place — and retrieves the best-scoring chunks from the index. The word “retrieval” is a bit misleading, since this process typically combines retrieval with ranking.

This part of the process — query rewriting, retrieval, ranking — feels like what happens in a traditional search application. The main difference is that it produces an intermediate output, rather than the final search results page shown to the searcher.

What is important to recognize in a RAG search application is that the purpose of retrieval is to return chunks that help generate the response rather than serving as responses themselves. Cosine similarity, however, measures the relevance of the chunk to the query based on their vectors, and other ranking factors are probably query-independent.

A chunk may have a high relevance based on cosine similarity and yet be unhelpful to the searcher, e.g., in cases where the searcher asks a question and the chunk repeats the question but does not answer it.

Conversely, a chunk may have low cosine similarity but still be helpful, especially if the chunk is large and the helpful information is contained in a small portion of it. That is a good reason to be careful with chunking!

### Answer Generation

The final step of a RAG search application is to generate an answer from the query and the retrieved chunks using a generative AI model.

For many searchers — and search application developers! — this may feel like the place where the real AI magic happens. After all, generative AI is what allows applications like [ChatGPT](https://en.wikipedia.org/wiki/ChatGPT) to challenge our very notions of intelligence, [creativity](https://queryunderstanding.com/maximal-marginal-creativity-e5b6a091cfe1), and what it means to be human. Indeed, generative AI may well be the defining technical innovation of our generation.

In the context of a RAG search application, however, the role that the generative AI model plays is usually secondary to that of retrieval. The name “retrieval-augmented generation” is a bit misleading — it might be better to call it “generative-AI-enhanced retrieval”. After all, the whole point of using RAG instead of a standalone generative AI application is that retrieval brings in critical knowledge that would otherwise be unavailable.

When the generative AI model generates an answer from the query and the retrieved chunks, it is mostly distilling knowledge that is present in the chunks. While the model may bring in knowledge from its training data, the main reason for using RAG is the insufficiency of that knowledge. Indeed a key selling point of RAG is reducing [hallucinations](https://en.wikipedia.org/wiki/Hallucination_(artificial_intelligence)).

### Extractive vs. Abstractive Summarization

The distillation that generative AI performs to generate an answer from the query and the retrieved chunks is a form of [content summarization](https://medium.com/content-understanding/content-structure-34aa2bd9d134).

Broadly speaking, there are two approaches for document summarization. [Extractive summarization](https://en.wikipedia.org/wiki/Automatic_summarization#Extraction-based_summarization) extracts words, phrases, or whole sentences that (hopefully) best summarize the content. [Abstractive summarization](https://en.wikipedia.org/wiki/Automatic_summarization#Abstractive-based_summarization) is more ambitious, generating new sentences rather than simply performing extraction.

Historically, search applications have produced [snippets](https://queryunderstanding.com/search-result-snippets-e8c447950219) as extractive summaries of individual search results. Producing a single summary from a set of retrieved chunks is a bit more ambitious. An extractive summary might choose the sentences that are determined to be more responsive to the query, with some deduplication to reduce verbosity and redundancy.

Abstractive summarization can perform this synthesis more elegantly, but it does so at the risk of drifting from the original content. In particular, using the query as an input for abstractive summarization introduces the risk that the generative AI process will try too hard to produce something that looks like an answer, even if the chunks do not contain a real answer. The only certain way to avoid this hallucination risk is to use extractive summarization, but doing so gives up the key benefits of generative AI.

## To RAG or not to RAG, that is the query.

Replacing the bag-of-words model with dense vectors generated from embeddings offers clear advantages but also comes with some risks. Search applications should explore using embedding-based retrieval, but [should not be in a hurry to throw away their inverted indexes](https://queryunderstanding.com/llms-and-rag-are-great-but-dont-throw-away-your-inverted-index-741d33630b7f).

The more interesting question is whether to stop at embedding-based retrieval or go full AI and implement retrieval-augmented generation. This decision depends on what kinds of queries the application is intended to serve, and on how likely a single document is likely to serve as an answer, rather than information distilled from several documents. RAG introduces complexity and risk, especially if the summarization is abstractive. Still, RAG does bring capabilities beyond those of retrieval.

As with most things in search and life, there are trade-offs. Embedding-based retrieval overcomes the limitations of words as units of meaning but at the cost of introducing complexity and risk. RAG overcomes the limitations of single documents as answers but adds even more complexity and risk. As a search application developer, it is your responsibility to understand these concerns, evaluate them, and decide on the architecture that best fits your needs. Choose wisely.
