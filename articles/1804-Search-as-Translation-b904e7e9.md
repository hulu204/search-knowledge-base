---
title: 'Search as Translation'
company: Tunkelang
tag: 查询理解
date: 2025-11-17
url: https://dtunkelang.medium.com/search-as-translation-f7adec0360f5
account: Tunkelang
origin: harvest3-202607
---
# Search as Translation

The core challenge of search has always been communicating meaning across representations.

For decades, search applications relied on a [reductionist](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) approach: matching queries to results by overlapping words. Technically, this meant measuring similarity between [sparse vector representations](https://queryunderstanding.com/sparse-and-dense-representations-f8c94f1e28e8).

[Dense vector representations](https://queryunderstanding.com/sparse-and-dense-representations-f8c94f1e28e8) have since made this process more robust. They allow queries and documents to be represented [holistically](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09), overcoming many of the limitations of treating text as a [bag of words](https://en.wikipedia.org/wiki/Bag-of-words_model).

Yet a deeper issue remains. Queries and documents inhabit different worlds, so their representations must be aligned. The challenge is not merely matching them — it is translating between them.

## From Matching to Mapping

In word-based search, queries and documents share the same vocabulary — almost. Developers have spent decades using [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741), [query rewriting](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83), and [content enrichment](https://medium.com/content-understanding/content-annotation-13b7c43ee5c7) to bridge the inevitable gaps between user language and content language. Query rewriting, in this light, is an early attempt to map queries into the document vocabulary space.

Dense representations replace vocabulary with an explicit geometry. Each query and document becomes a vector in a continuous space. But query and document embeddings often occupy different regions — or even different spaces entirely. A critical part of embedding-based search is therefore mapping from query space to document space. Again, this is translation by another name.

## Three Ways to Translate from Queries to Documents

At least three lines of work have converged on this translational approach.

### Hypothetical Document Embeddings (HyDE)

[HyDE](https://arxiv.org/abs/2212.10496), developed by [Luyu Gao](https://luyug.github.io/), [Xueguang Ma](https://mxueguang.github.io/), [Jimmy Lin](https://cs.uwaterloo.ca/~jimmylin/), and [Jamie Callan](https://www.cs.cmu.edu/~callan/), takes a generative approach. Given a query, it uses a language model to imagine a document that would perfectly answer it, and then embeds that hypothetical document.

This approach excels at question answering, where a single ideal answer exists, but it can over-specify [broad or ambiguous queries](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc).

### Bag of Documents

In the [bag-of-documents model](https://queryunderstanding.com/modeling-queries-as-bags-of-documents-b7d79d0916ab), which I developed with [Aritra Mandal](https://www.linkedin.com/in/aritram/), a query maps to an aggregation of document vectors. If we know the vectors for documents relevant to a query, we can compute the query vector as their mean, and the query’s [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) as the mean cosine similarity between the query vector and its document vectors.

We can then generalize this by [using known queries as training data to fine-tune a sentence transformer model](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d). The resulting model directly produces query vectors that already live in the document space.

The query becomes the centroid of the documents it targets.

### Semantic Knowledge Graphs and Wormhole Vectors

[Trey Grainger](https://www.treygrainger.com/)’s work on [semantic knowledge graphs](https://www.treygrainger.com/posts/presentations/the-semantic-knowledge-graph/) and [wormhole vectors](https://aipoweredsearch.com/latest-content/trey-grainger-wormhole-vectors/) offers another path. Both approaches learn to connect distant regions of semantic space, creating pathways that bridge related concepts even when they are far apart in the embedding geometry.

The wormholes act as a learned translation layer between different knowledge representations.

## A Common Thread

Across these approaches, the unifying idea is simple but profound: retrieval is the process of mapping intent to relevance through aggregation.

Each model constructs — explicitly or implicitly — an embedding in the document space that represents what the query means. Whether through averaging, generating, or bridging, they all perform the same fundamental operation: translation across manifolds.

This reframing transforms retrieval from a discriminative problem of *matching* documents to a generative one of representing queries in the document space. Once that translation is achieved, measuring similarity becomes a trivial corollary.

## Implications for Search

Modeling search as translation changes how we design the search stack. It [de-emphasizes ranking](https://queryunderstanding.com/beyond-ranking-focus-on-content-and-query-understanding-4233bc7101f0) and instead focuses on aligning [query understanding](https://queryunderstanding.com/introduction-c98740502103) with [content understanding](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974). The goal becomes reducing the representational gap between [intent](https://medium.com/search?q=%22tunkelang%22+intent) and information, regardless of the particular architecture or embedding method.

This framing unites many seemingly different retrieval techniques under a shared goal: to translate meaning faithfully between how users express needs and how knowledge is encoded.

## Closing Thought

Search began as a problem of matching words. It is becoming a problem of translating ideas. We no longer find information by measuring overlap among bags of words. We are learning to navigate the geometry of meaning — to see search itself as the act of translating understanding between representations.
