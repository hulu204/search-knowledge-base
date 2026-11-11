---
title: 'Exploring Search Intent as a Duality'
company: Tunkelang
tag: 查询理解
date: 2024-01-08
url: https://dtunkelang.medium.com/exploring-search-intent-as-a-duality-c0c260500599
account: Tunkelang
origin: harvest3-202607
---
# Exploring Search Intent as a Duality

Most of us who work on search focus on its engineering or product aspects. But I feel it’s valuable to also look at search philosophically. I’m no expert on philosophy, but I’ll do my best to describe what I see as a fascinating duality when we consider search intent in terms of queries and documents.

In search applications, searchers express their intents through queries, and search engines aim to satisfy those intents by returning relevant documents as results. This is an oversimplification, especially on the result side, since search engines increasingly return results that are part of documents or that are synthesized from multiple documents. Nonetheless, this simple model describes most search engines well enough to be useful.

### Queries as Bags of Documents

Searchers express their intent through queries, but queries themselves are brittle representations. Some queries, like “[mixers](https://en.wikipedia.org/wiki/Mixer)”, suffer from [ambiguity](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc). But the bigger problem with queries are representations of intent tends to be that multiple queries map to the same intent. For example, the queries “mens shoes” and “shoes for men” represent the same search intent.

Sometimes, as in this example, queries mapping to the same intent only vary superficially: they only differ in [stemming or lemmatization](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45), word order, or the inclusion of noise words. We could try to address this sort of superficial variation by canonicalizing queries, e.g., by stemming all of the words, removing noise words, and standardizing the word order.

Superficial variation sometimes changes the meaning of a query, e.g. a “shirt dress” is not the same as a “dress shirt”. Nonetheless, queries that only vary superficially usually map to the same intent.

The more interesting scenario is when queries that vary more significantly but still map to the same intent. For example, queries like “iphone headphone adapter” and “lightning to aux” express equivalent search are intent. In cases like these, recognizing equivalence requires us to look beyond the query words.

Specifically, we can model a query as a bag of relevant documents. We can implement this approach by first representing the documents as vectors and then aggregating these vectors, e.g., by taking their mean. This or a similar process allows us to represent a query as a vector by way of a set of associated documents. We call this the “bag-of-documents” model.

Representing queries this way is very powerful. It allows us to implement a variety of application functionality, such as increasing recall, using [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043). While the aggregation approach applies to head and torso queries, for which we can compute the vector representations offline, it is possible to extend it to tail queries. Specifically, we can [train or fine-tune a sentence embedding model](https://huggingface.co/blog/how-to-train-sentence-transformers) using pairs of vectors from head and torso queries and their associated cosine similarity.

Implementation details aside, the bag-of-documents model is a practical, intuitive way to represent queries as search intents.

### Documents as Bags of Queries

Now that we’ve explored how to represent a query as a bag of documents, let’s consider how to model a document as a bag of queries.

If we can map a query map to its relevant documents, then we can map a document to the queries for which it is relevant. All that we have done is to invert the direction of the mapping.

What does it mean to map a document to the queries for which it is relevant? In effect, we are representing the document as the collection of query intents that it can satisfy. For example, a pair of Levi’s men’s jeans is relevant to queries that include “jeans”, “mens jeans”, “levis”, etc.

We can implement a bag-of-queries representation for documents using a process analogous to the one we described for the bag-of-documents representation for queries, only reversing the roles of documents and queries. For each frequently accessed document, we represent the queries used to access that document as vectors, and then aggregate these vectors. We can generalize this model to tail documents the same way that we generalize the bag-of-documents model to tail queries.

Representing documents this way feels like playing [*Jeopardy*](https://en.wikipedia.org/wiki/Jeopardy!): we are treat documents like answers and then map them to the questions they answer.

### Duality

The duality of the bag-of-documents and bag-of-queries models raises the question of what is more fundamental to the search process: documents or queries. Many of us who develop search applications see the documents as more fundamental, the job of a search engine being to make those documents accessible and discoverable through queries. But we can just as easily see queries as fundamental: human needs for which documents serve as solutions. Indeed, that feels more like the searcher’s perspective.

Meanwhile, we are entering a world where generative AI may change the notions of both queries and documents. I am intrigued by this seeming duality between information needs and the information itself, even thought I am not sure what we can do with it.

As I warned you, I’m no expert on philosophy. But I hope you’ve enjoyed this exploration. We certainly live in interesting times for search!
