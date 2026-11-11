---
title: 'Bags of Documents and the Cluster Hypothesis'
company: Tunkelang
tag: 召回
date: 2024-06-11
url: https://dtunkelang.medium.com/bags-of-documents-and-the-cluster-hypothesis-7bd2ed9c4fa9
account: Tunkelang
origin: harvest3-202607
---
# Bags of Documents and the Cluster Hypothesis

My writing on [AI-powered search](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b) promotes the “[bag-of-documents](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599)” model, which represents a search query as a distribution of vectors for relevant documents. When the document vectors are available (i.e., for frequent queries), the bag-of-documents model allows us to compute the query vector as a mean of the document vectors and the [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) as the mean of the cosine between the query vector and the document vectors. Visually, the query vector represents the [centroid](https://en.wikipedia.org/wiki/Centroid) of the document distribution and the specificity represents how closely the documents are clustered around that centroid.

When document vectors are unavailable (i.e., for infrequent queries), we can either obtain them dynamically at query time from retrieval or [train a model using known queries as training data](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d).

We can generalize the bag-of-documents model to a mixture of multiple centroids, each associated with a weight or probability. This approach offers a more robust representation for low-specificity queries whose relevant documents are not uniformly distributed around a single centroid (e.g., “laptop” being a mixture of MacBooks, Chromebooks, and Windows laptops). This approach can model [ambiguous queries (as distinct from broad ones)](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc) using a mixture of centroids that are highly dissimilar from one another (e.g., “jaguar” referring to both the car and the cat).

The bag-of-documents model is useful because it addresses a key challenge of AI-powered search: aligning query and document embeddings.

### The Cluster Hypothesis

A key assumption in the bag-of-documents model is that similar documents have similar relevance to a query. This assumption evokes the [cluster hypothesis](https://en.wikipedia.org/wiki/Cluster_hypothesis) first formulated by [Keith van Rijsbergen](https://en.wikipedia.org/wiki/C._J._van_Rijsbergen) in the 1970s. We can view the bag-of-documents model as a sort of corollary to the cluster hypothesis: if all documents relevant to a query are similar to one other, then they are also similar to their mean or centroid.

There is a fair amount of research on evaluating the cluster hypothesis, starting with “[The Cluster Hypothesis Revisited](https://dl.acm.org/doi/pdf/10.1145/253495.253524)”, published by [Ellen Voorhees](https://en.wikipedia.org/wiki/Ellen_Voorhees) in 1985. However, this body of work tends to focus on test collections, and our concern is at the level of individual queries. There has also been research on applying the cluster hypothesis to retrieval, most notably the [Scatter / Gather](https://sigir.org/wp-content/uploads/2017/06/p148.pdf) approach based on document clustering.

### Violation of the Cluster Hypothesis

However, the cluster hypothesis is just that, a hypothesis. What happens if, contrary to the cluster hypothesis, similar documents do not have similar relevance? And how can we recognize such violations when they occur?

We already considered the case of query ambiguity, where dissimilar results can be similarly relevant because they correspond to distinct query interpretations. Ambiguous queries violate the cluster hypothesis, but in a way that seems fixable using a mixture of centroids. But there are stronger violations when queries do not even map to mixtures of centroids.

Let us start with an extreme example, where we create a new field for each document and assign its values (e.g., 0 and 1) randomly. A query that filters on the value of this field will match a representative random sample whose distribution is statistically indistinguishable from that of the collection.

This example is artificial, but there are natural examples of queries that exhibit a similarly low correlation to content. For example, a user might be interested in recent content on a media site or discounted items on an e-commerce site. These search intents strongly violate the cluster hypothesis because result similarity is not meaningfully correlated to relevance.

Moreover, these examples overshadow the bigger picture, which is that the validity of the cluster hypothesis is not binary, but exists on a spectrum. The validity of the cluster hypothesis is continuous, reflecting how tightly relevant results cluster around a single centroid or at least a small number of them — or, more broadly, how well the distribution of results is characterized by a compact mixture of centroids.

For most queries — even broad queries like “sneakers” — a single centroid (along with a [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb)) is a reasonable representation of the query intent. For ambiguous queries like “jaguar” or “mixer”, a probability distribution over a handful of centroids effectively covers the intent space. However, the robustness of this model degrades as the relevance of a result becomes less correlated with its vector representation. For example, the query “sneakers on sale” combines an intent that respects the cluster hypothesis (“sneakers”) with one that does not (“on sale”). Many queries combine intents this way and thus partially violate the cluster hypothesis.

### Detecting Queries that Violate the Cluster Hypothesis

We know that some queries violate the cluster hypothesis. But how do we detect such queries and measure their degree of violation? Our ability to do so is critical for determining when to apply the bag-of-documents model.

We can evaluate the validity of the cluster hypothesis for a query directly by using [ground-truth relevance judgments](https://queryunderstanding.com/evaluating-search-using-human-judgement-fbb2eeba37d9) and computing the correlation between document similarity and relevance. Since there are far more irrelevant documents than relevant documents, this approach requires [stratified sampling](https://en.wikipedia.org/wiki/Stratified_sampling) to be practical. Regardless, this approach is difficult to scale because it depends on extensive human judgments.

A more scalable approach employs a relevance model rather than human judgments. However, there is a risk of circularity if the model explicitly or implicitly assumes the validity of the cluster hypothesis. Also, the relevance model should be general enough to handle queries like “sneakers for sale”.

An alternative strategy is to frame conformance with the cluster hypothesis as a classification or regression problem. For this strategy, we collect queries and label them based on whether or to what extent they conform to the cluster hypothesis. We use either human judgments or a relevance model for this step. We can then use the labeled data to train a model, analogous to how we train a model to compute [query specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb).

### Implications for Search Applications

For queries where the cluster hypothesis holds — or at least holds to a sufficient degree — we can use the bag-of-documents model for retrieval and relevance. To retrieve relevant results, we find the documents whose cosine similarity with the query vector is sufficiently close to 1, with a cosine similarity threshold determined by query specificity. Within this retrieved set, we can rank results mostly using query-independent factors.

We can use a similar strategy if the query maps to a mixture of centroids by retrieving multiple sets of results, one for each centroid, as subqueries. The search application should probably organize the results by subquery since it is likely that the searcher’s actual intent only maps to one of them.

However, if a query strongly violates the cluster hypothesis, then a bag-of-documents retrieval strategy is unlikely to work at all. Indeed, any retrieval strategy based on document vectors is likely to fail. It may be better to fall back on traditional token-based retrieval (which is at least interpretable) or to explore [query rewriting](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83) strategies not based on document vectors.

### Summary

The bag-of-documents model is powerful and practical, especially when generalized to a mixture of centroids, but it has limitations. Since it is a corollary to the cluster hypothesis, it depends on the validity of that hypothesis. That validity is query-specific. It is important to confirm the validity of the cluster hypothesis for a query before applying the bag-of-documents model for retrieval and ranking. If a query strongly violates the cluster hypothesis, the bag-of-documents model is unlikely to be helpful, as is any retrieval strategy based on document vectors.
