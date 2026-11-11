---
title: 'Representing Documents with Multiple Intents'
company: Tunkelang
tag: 召回
date: 2025-10-15
url: https://dtunkelang.medium.com/representing-documents-with-multiple-intents-55c2ec7bf8ae
account: Tunkelang
origin: harvest3-202607
---
# Representing Documents with Multiple Intents

In search, we talk a lot about ambiguous queries.

A query like “python” can refer to a programming language, a snake, or a comedy troupe. Linguists call this polysemy. Such queries challenge search systems, which must either infer — or hedge among — multiple possible intents.

There is also a softer distinction between [ambiguous queries and broad queries](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc). Ambiguous queries have multiple conflicting meanings, while broad queries have a clear intent but low [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb).

But there is a natural dual to this idea that we rarely discuss: ambiguous documents — or, more precisely, multi-intent documents.

## The Duality Between Queries and Documents

If an ambiguous query targets multiple clusters of relevant documents, then a multi-intent document attracts multiple clusters of queries.

In the [bag-of-documents model](https://queryunderstanding.com/modeling-queries-as-bags-of-documents-b7d79d0916ab) — where a query retrieves a “bag” of relevant documents — an ambiguous query cannot be pinned down to a single information need, so it requires more than one bag.
 Likewise, a multi-intent document cannot be pinned down to one query intent — it needs more than one [bag of queries](https://queryunderstanding.com/bags-of-queries-as-sparse-document-representations-bc450db3e814).

This [duality](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599) is straightforward but underexplored. There is a lot of literature about query disambiguation, yet we tend to treat documents as if each has a single, well-defined intent.

In reality, many documents address a variety of needs. Different sections may focus on distinct topics — often motivating [chunking](https://medium.com/content-understanding/content-structure-34aa2bd9d134). And even a single item of content can serve multiple purposes: the same SD memory card can be an accessory for computers, cameras, and phones.

All of these are multi-intent documents.

## One Bag vs. Multiple Bags

The duality of queries and documents works like this:

- Each query corresponds to a bag of relevant documents.

- Each document corresponds to a bag of queries for which it is relevant.

Whereas an unambiguous query maps to a single bag of documents, an ambiguous query maps to multiple bags of documents — semantically distinct clusters of relevance.

Analogously, while a single-intent document maps to a single, cohesive bag of queries, a multi-intent document maps to multiple bags of queries — the queries that retrieve it cluster in different regions of query space.

## Representation Matters

Most content-representation approaches assume each document has a single meaning.

That assumption works fine for focused content. But when a document serves multiple intents, those meanings get blurred together — hurting relevance for all of them.

Dense retrieval is especially vulnerable here. Averaging conflicting signals into a single embedding collapses the structure that multi-intent documents need. A single vector cannot capture multiple semantic centers — whereas multi-vector or sparse representations can.

There are various approaches that try to address this:

- Chunking, to isolate document spans with coherent subtopics.

- [ColBERT](https://arxiv.org/abs/2004.12832), which represents each document using multiple contextualized token embeddings — a true multi-vector representation that preserves distinct facets.

- [SPLADE](https://arxiv.org/abs/2107.05720), which learns sparse, token-level weights that capture multiple aspects of meaning without collapsing them into a dense vector.

Each of these techniques acknowledges, implicitly or explicitly, that some documents do not fit into a single embedding.

## Bags of Queries and Document Ambiguity

The bag-of-queries model offers a more conceptual path forward.

Just as an ambiguous query may require multiple bags of documents, a multi-intent document may require multiple bags of queries.

By treating a document’s bag of queries as a distribution over intents, we can measure its ambiguity directly. Cluster those queries in embedding space, and you can quantify how separable the clusters are.

That makes it possible to detect multi-intent documents from query logs and to build representations that preserve those distinctions.

Ultimately, retrieval and ranking should handle multi-intent documents as gracefully as we already handle ambiguous queries.

## Simplicity and Symmetry

The bag-of-documents model has proved to be a simple but elegant way to map queries into document space.

The bag-of-queries model provides the mirror image — mapping documents into query space.

Recognizing this symmetry gives us a conceptual bridge between ambiguous queries and multi-intent documents. Both are polysemous; both span multiple semantic clusters. Both deserve representations that respect that complexity.

It’s all in the bag.
