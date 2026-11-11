---
title: 'Is Similarity Objective?'
company: Tunkelang
tag: 搜索相关性
date: 2024-06-24
url: https://dtunkelang.medium.com/is-similarity-objective-92e1f3a4c236
account: Tunkelang
origin: harvest3-202607
---
# Is Similarity Objective?

Some search problems have binary answers. We often frame these problems in terms of matching or equivalence. A simplistic formulation of relevance is that a canonicalized representation of the query intent equals or matches a canonicalized representation of the content. This approach emphasizes factoring relevance into [query](https://queryunderstanding.com/introduction-c98740502103) and [content understanding](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974).

Unfortunately, not every search problem admits a binary answer. Many [relevance and ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) problems involve similarity, which is inherently continuous. [Content similarity](https://medium.com/content-understanding/content-similarity-d3c7a9cd7d44) and [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043) are valuable tools for developing [AI-powered search applications](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b).

However, quantifying similarity assumes we can reduce similarity to a single number. More fundamentally, it models similarity as something objective. This post explores the question of whether similarity is objective.

### Similarity as Substitutability

To reduce similarity to a number, we must decide what it means. Here are two general ways to model similarity, both based on substitutability. Conveniently, both approaches yield a number between 0 and 1.

The first is to treat substitution as a binary and model similarity as the probability that one object can be substituted for another and achieve the desired outcome. For example, in an e-commerce setting, we model product similarity as the probability that a buyer wanting to buy product X would buy product Y for the same price if X were unavailable.

The second is to treat substitution as continuous and model similarity as the fraction of utility preserved by substitution. Returning to an e-commerce setting, we can model product similarity as the fraction of utility that a buyer wanting to buy X would obtain from buying Y instead. We can make this definition concrete (albeit oversimplified) by measuring the fraction of X’s price that a buyer would pay for Y as a substitute.

The above examples focus on product similarity in e-commerce. However, the two approaches generalize to other domains, as well as to query similarity. For instance, we can model query similarity as the probability that a searcher who makes Query X will be satisfied with the results of Query Y, or by computing the fraction of result utility using a measure like [discounted cumulative gain (DCG)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain). The details of a similarity model will be specific to the objects being compared, the domain, and the application.

### Substitutability and Context

Anyone who has implemented [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) using synonyms has learned (probably painfully) that [synonymy is context-dependent](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741). In general, substitutability tends to be context-dependent.

For example, consider two math textbooks that cover the same material at a similar level and thus seem highly substitutable for one another. A teacher might be happy to flip a coin to choose between them. However, once the teacher chooses a book, students taking the class may not find the other book to be an acceptable substitute. Context is critical.

In particular, [query context](https://queryunderstanding.com/contextual-query-understanding-65c78d792dd8) affects how we determine the substitutability of results. For example, consider three shirts: X is black and medium, Y is blue and medium, and Z is black and large. Which shirt is more similar to X: Y or Z? Answering this question requires determining the relative importance of color and size. Knowing whether a searcher’s query was “black shirts” or “medium shirts” would change our determination.

Substitution is always contextual. Measuring whether or how well Y can replace X requires a context, either explicit or implicit. If we imagine substitution as context-independent, it is only because we assume only a single possible context and thus take it for granted.

Can we incorporate context into the way we compute similarity? In theory, we can, but there are computational challenges. Indexing documents or queries as vectors for efficient nearest-neighbor search requires us to fix the vector representations and the similarity function (e.g., [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)). If the number of distinct contexts is bounded and reasonably small, we can index each context-dependent vector separately. In the case of document contexts, we can use the [bag-of-queries](https://queryunderstanding.com/bags-of-queries-as-sparse-document-representations-bc450db3e814) model. However, if the number of distinct contexts is unbounded, we cannot index the vectors for efficient nearest-neighbor search.

### Substitutability and Individual Preferences

Substitutability is not only context-dependent but also personal. For example, butter may be an acceptable substitute for margarine for many people, but not for people who cannot or do not consume dairy products. The substitutability of colors can reflect personal taste, as opposed to a similarity function based on an objective representation like [RGB](https://en.wikipedia.org/wiki/RGB_color_model). In general, everyone may agree on when two objects are equivalent, but similarity introduces the subjectivity of individual preferences.

As with context, incorporating individual preferences into similarity poses computational challenges. Indeed, the variation in individual preferences is much higher — unless we can somehow reduce searcher preferences to a handful of aggregated personas. Hence, it is not practical to index using a searcher-specific similarity measure — or searcher-specific representations of the objects being indexed — in a scalable way.

### Cutting Corners

If similarity is always contextual and subjective, is there any hope of measuring it objectively? In theory, perhaps not. In practice, however, we can cut corners to model similarity as objective.

Yes, similarity is contextual. However, as discussed above, we can address context as long as the number of distinct contexts is bounded and reasonably small. This assumption is often good enough in practice. Indeed, there is often a single dominant context.

What about individual preferences? We often frame similarity as a function that combines various factors — a tradeoff involving multiple dimensions, as we saw in our example of a black medium shirt, a blue medium shirt, and a black large shirt. Each dimension in which the objects differ reduces their similarity, and the relative weights of each dimension reflect individual preferences. Still, different people will tend to agree on whether two objects are highly similar; the divergence from individual preferences grows as the objects move away from equivalence.

Hence, indexing objects based on the average of subjective preferences provides a reasonable approximation for everyone, at least for an object’s nearest neighbors. We can use such an index for efficient retrieval and then rerank results based on individual similarity.

### Summary

Many search problems involve similarity, particularly content similarity and query similarity. However, quantifying similarity assumes we can reduce similarity to a single number, which we can model as the probability that one object can be substituted for another or the fraction of utility preserved by substitution.

Unfortunately, these measures are subject to context and individual preferences. Fortunately, we can approximate objectivity if the number of distinct contexts is small and individual preferences mostly agree when two objects are highly similar.

So, is similarity objective? In theory, no. In practice, it’s often close enough.
