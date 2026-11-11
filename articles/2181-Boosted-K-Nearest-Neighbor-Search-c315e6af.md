---
title: 'Boosted K-Nearest Neighbor Search'
company: Sease
tag: 召回
date: 2026-07-22
url: https://sease.io/2026/07/boosted-k-nearest-neighbor-search.html
account: 
origin: harvest3-202607
---
Over the past few years, search architectures have changed in a way that is hard to ignore.   
Traditional lexical retrieval, built around BM25, TF-IDF, and query-time constructs like [Apache Solr eDisMax query parser](https://solr.apache.org/guide/solr/latest/query-guide/edismax-query-parser.html), has not been replaced, but the rise of dense vector search has radically redesigned it.

With systems like Apache Lucene now offering native support for approximate nearest neighbour (ANN) queries, semantic retrieval has moved from experimental setups into mainstream production stacks. In practice, this makes it relatively straightforward to retrieve documents based on vector similarity.   
The real challenge appears immediately after that: once you want to influence how those results are ranked beyond pure similarity, the model becomes much less accommodating.

**Vector search gives you strong semantic recall, but very limited room for expressing external ranking logic.**

*This work is a reflection on an attempt to bridge that gap by introducing a mechanism similar in spirit to eDisMax boosting into a KNN-based retrieval pipeline, where scoring is not only about similarity but can also be shaped by document-level functions and field-driven signals.*

## When Similarity Isn’t Enough

If you’ve worked with Apache Solr eDisMax (or similar query parsing strategies in Elasticsearch, OpenSearch and Vespa), you know how expressive it can be.

You can:

* **Boost specific fields** (`title^5`, `category^10`)
* **Apply arbitrary functions** on document fields
* **Combine textual relevance with business signals** like *freshness* or *popularity*

In other words, scoring is not just about matching; it’s about **shaping relevance**.

Now compare this with dense vector search, as implemented in Solr’s dense vector module.   
A KNN query does one thing very well:   
*It finds the closest vectors using a similarity metric (cosine, dot product, etc.), but that’s essentially it.*

**The score is the similarity**.

There’s no native concept of:

* “Multiply the score if the document is recent”
* “Boost items from a preferred category”
* “Apply a decay function based on a numeric field”

This creates a gap that becomes immediately visible in real-world applications. Semantic similarity alone is not always enough; you sometimes need structured signals to refine ranking.

So the question becomes:

***Can we inject that flexibility into KNN search without breaking how it works?***

## What We Have Today

Solr’s dense vector search (built on Lucene’s HNSW implementation) already provides an ecosystem of useful features; it is well-documented and production-ready. It supports filtering, hybrid queries, and even some forms of integration with lexical search.

These features, however, come with some limitations.

### Hybrid Search

A common pattern is to run:

* A KNN query for semantic similarity,
* A lexical query for keyword matching,
* Then combine the results.

Even if with this approach we would be able to get both:

* Semantically relevant documents
* Documents with relevant content for the boosting part (good category, recent, popular, etc.)

**It doesn’t guarantee that we will get a document that satisfies both conditions**. Also, *the scores coming from the two different searches live in different spaces and need normalization in order to be used in the final unique result list for ranking adjustments.*

### Re-ranking

Another useful approach is:

1. Run a KNN query to get top-K candidates
2. Re-rank them using a richer scoring function

This is where you can reintroduce field-based boosts, decay functions, and business logic.

It works, but comes with trade-offs:

* **You need a sufficiently large K** to avoid missing good candidates
* **Latency increases**
* The system becomes a **multi-stage pipeline** rather than a single query

Also, this approach *relies on the fact that good candidates (also for the boosting component), with an enough big K, could be retrieved from KNN. **If documents that have a very nice impact on the boosting are slightly less relevant in terms of vector similarity with respect to the other K documents, we might end up not retrieving them.***

### Seeded KNN

From version 10.0.0, we contributed the `seedQuery` parameter for the Dense Vector Search in Apache Solr (you can read more about this in our [blog post](https://sease.io/2026/02/lexically-accelerated-vector-search-seededknnvectorquery-support-in-apache-solr-10.html)), implemented in Lucene through the `SeededKnnVectorQuery` and inspired by the paper *[Lexically-Accelerated Dense Retrieval](https://arxiv.org/pdf/2307.16779)*.

The idea is to use a lexical query to “seed” the vector search, guiding the traversal of the HNSW graph toward more promising regions. What we could do for our boosting scenario is therefore to use a boosted eDisMax query as the seed.

This, however, would:

* Influence **where the search starts**
* **Not** influence **how results are scored**

**The final result could potentially contain documents that are only relevant semantically (vector distance), regardless of the boost.**

Even worse, the seed does not guarantee to affect the end results; **it’s a heuristic, not a constraint**.   
*So while seeded KNN improves recall or efficiency, it doesn’t provide a mechanism for score manipulation. It’s not boosting; it’s navigation.*

## The Alternative We Explored

### Modifying the Similarity Function

##### Query Time

The idea was to integrate boosting directly into the similarity computation:

```
				
					score = similarity(vector_query, vector_doc) * boost(doc)
				
			
```

At first glance, this looks like the perfect solution: we keep semantic similarity, but we also inject all the flexibility of field-based or function-based boosting.

However, this approach conflicts with how ANN algorithms such as HNSW actually work.  
HNSW does not just compute distances; it *navigates a graph* that is built under the assumption that the distance function has specific properties. In particular, the **distance (or similarity) must be consistent and monotonic**:

* If document A is closer than document B to the query, this relationship should remain stable during traversal
* Moving through the graph should progressively bring us closer (in terms of distance) to better candidates

These properties are critical because the algorithm prunes large parts of the graph based on them. It assumes that “closer now” implies “more promising later.”  
**When we introduce arbitrary boosting at query time, this assumption breaks.**

For example:

* Document A has high vector similarity (0.9) but low boost (×1) → score = 0.9
* Document B has lower similarity (0.7) but high boost (×3) → score = 2.1

Even though B should rank higher in the final results, the graph traversal will still consider A “closer” and prioritize exploring its neighborhood. **The search process is therefore guided by vector similarity, while the final ranking is driven by a different scoring function.**

This mismatch leads to two issues:

* **Effectiveness degradation**: highly boosted documents may never be reached because they are not “close enough” in vector space
* **Efficiency degradation**: the traversal loses its guiding principle, effectively behaving in a more random way

It’s also important to note that the HNSW graph itself is constructed purely based on vector distance. It has no awareness of boosting signals. **Documents that should rank highly due to a strong boost** (e.g., very recent items) **are not guaranteed to be near each other—or even reachable efficiently—within the graph structure.**

##### Index Time

A natural follow-up idea is: instead of applying boosting at query time, can we bake it directly into the distance function used to build the HNSW graph?

This raises two major challenges:

###### 1) The distance-definition problem

We would need a function that:

* **Combines vector similarity with boosting signals** (e.g., freshness, popularity, category weights)
* Still **behaves like a proper distance metric** (or at least preserves the properties HNSW relies on)

This is far from trivial.  
For example:

* A freshness boost might depend on the query time (“newer is better *now*”)
* A category boost might depend on user intent (“electronics” boosted only for certain queries)
* A popularity boost might be non-linear (e.g., logarithmic or capped)

So the “distance” is no longer a fixed function. It becomes:

* Query-dependent
* Use-case-specific
* Potentially non-monotonic

**This directly conflicts with the requirement that the graph is built using a single, stable notion of distance.**

###### 2) The reindexing problem

Even if we could define such a function, we would need to apply it at **index time**, because HNSW graph construction depends on that distance.

This implies: every change in ranking logic (e.g., adjusting a boost, adding a new signal, tuning a decay function) requires rebuilding the entire graph.

**In practice, this means reindexing all documents, which is often prohibitively expensive for production systems.**

### Encoding Boosting into the Embedding

Another idea was to “bake in” boosting signals directly into the vector representation.

For example:

* Include structured features in the embedding
* Train the model to reflect business priorities

This aligns with approaches where relevance is learned rather than computed.

But this quickly becomes problematic:

* Every **change** in business logic **requires retraining**
* **Boosting becomes opaque** and hard to debug
* **Fine-grained control** (e.g., “boost this field by 2x”) **disappears**

## Why This Is Fundamentally Hard

After analysing these solutions, we realised that the **difficulty** is both in the **implementation** and in the **mismatch of paradigms**.

*Vector search operates in a geometric space*: documents are points, queries are points, and relevance is distance.

*EDisMax*, on the other hand, *operates in a symbolic and compositional space*: scores are constructed, boosts are layered, functions are applied.

When you apply a boost in eDisMax: it affects all matching documents, it reshapes the entire ranking. **KNN doesn’t see the entire space; it only explores a subset.** So boosting becomes partial, order-dependent, and sensitive to ANN parameters.

This is a fundamental limitation.

## Where This Leaves Us

After all these experiments, the conclusion is somewhat sobering, but also clarifying.

**There is no clean way today to replicate true eDisMax-style boosting inside KNN search**.

The options we have fall into three categories:

* **Approximate it** (hybrid scoring, seeded queries)
* **Externalize it** (re-ranking pipelines)
* **Hide it** (embedding-based approaches)

None of these fully preserves the flexibility, transparency, and control of eDisMax.

**If the goal is to build a robust, production-ready system, the most sensible architecture remains:**

* Use KNN for what it does best: **semantic recall**
* Use a second stage for what KNN cannot do: **business-aware ranking**

It’s more complex. It introduces latency. But it keeps concerns separated: geometry in one stage and logic in another.

And, perhaps more importantly, **it keeps the system understandable.**

## Final Thoughts

The idea of unifying lexical boosting and vector similarity into a single scoring function is undeniably attractive. It promises elegance, simplicity, and performance.

**But at least with current tools and algorithms, that unification comes at a cost that’s hard to justify.**

Sometimes, the better design is not to force integration but to accept separation and make it work well.

In the case of KNN and eDisMax-style boosting, that seems to be exactly where we stand today.

***What do you think about this? Do you also encounter this problem? Do you find a nice solution that fits your needs?***

Please feel free to share with us your thoughts on the topic! We would be happy to receive additional insight

## Need Help with this topic?​

If you're struggling with k-nearest neighbor search, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with k-nearest neighbor search, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)