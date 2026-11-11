---
title: 'Precision, Recall, and Desirability'
company: Tunkelang
tag: 评测
date: 2024-02-20
url: https://dtunkelang.medium.com/precision-recall-and-desirability-0384a11d916b
account: Tunkelang
origin: harvest3-202607
---
# Precision, Recall, and Desirability

Recent developments in AI have created opportunities across the search stack. But before building solutions, it is important to clearly identify the problems they can address. Broadly speaking, search applications focus on three concerns: precision, recall, and desirability. AI mostly helps with the first two, which in turn makes it possible to focus on the third.

## Precision

[Precision](https://en.wikipedia.org/wiki/Precision_and_recall) formalizes what most people mean by relevance: it is the fraction of search results that satisfy — or at least directly relate to — the searcher’s information need. This definition models relevance as binary and ignores position, i.e., each returned result is weighed equally, regardless of ranking. We can generalize precision to use a graded relevance model, as well as to account for the importance of position by weighing results according to their position, so that top-ranked results carry more weight. This generalization leads to metrics like [discounted cumulative gain (DCG)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain).

### Traditional Approaches to Deliver Precision

The most traditional approach to deliver precision is to retrieve and rank results using a weighted keyword-matching score. The score leverages the [bag-of-words](https://en.wikipedia.org/wiki/Bag-of-words_model) model, which is the original [vector space model](https://en.wikipedia.org/wiki/Vector_space_model). This approach typically uses [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) or [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) to compute token weights, with the goal of assigning a higher weight to more important tokens. For example, if the query is “a book about cats”, “book” and “cats” will be assigned more weight in matches than the less informative tokens “a” and “about”. This approach has been around for decades, but it is still widely used because it is simple to implement and surprisingly effective for many applications.

An improvement on the bag-of-words representation is to train a [machine-learned ranking (LTR)](https://en.wikipedia.org/wiki/Learning_to_rank) model to return better results ahead of worse results. This approach is more principled than token-weighting heuristics, since it learns from ground-truth data. The downside is that the [implicit judgments](https://queryunderstanding.com/evaluating-search-measuring-searcher-behavior-5f8347619eb0) in ground-truth data [conflate relevance with desirability](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e), at least when derived from clicks or other searcher engagement, as is common since collecting human judgments is costly. In general, while LTR can improve precision, it is designed to improve ranking, not relevance.

It is also possible to improve precision by mapping query tokens to a more meaningful representation. [Entity recognition (NER)](https://queryunderstanding.com/entity-recognition-763cae840a20) maps keywords to entities that correspond to structured data elements in the index. For example, in the query “apple phone”, the token “apple” maps to the brand Apple. Recognizing this meaning of the token “apple” allows the search engine to retrieve relevant iPhones, as opposed to [phones that look like apples](https://oldphoneworks.com/products/the-apple-telephone). NER depends on aligning query understanding with the [content representation](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974), such matching a brand field for “apple” in our example.

### AI-Based Approaches to Improve Precision

Given the critical role that precision plays in the search experience, it is natural to ask how AI can help improve it.

A great way to improve precision through AI is [query understanding ](https://queryunderstanding.com/introduction-c98740502103)— specifically, [query classification](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09). Query classification maps a query to one or more [categories](https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2). The categories can be product types, topics, colors, or any other enumeration of values that describe the content. The categories for a classifier can be organized as a flat list, or they can be arranged in a hierarchy (e.g., a shirts category could be a child of a clothing category). Unlike entity recognition, query classification is [holistic](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09): it applies to the whole query, not just to a word or phrase extracted from the query, e.g., mapping “air jordans size 8” to the athletic shoes category. Query classification is one of the simplest ways to use AI to improve precision, since the same engagement data used to train a ranking model often works far better for the simpler problem of training a query classification model. Since the input to the classifier is the query string, classification can use [neural language models](https://en.wikipedia.org/wiki/Language_model#Neural_models) designed to understand strings.

We can also use AI to compute the relevance of individual results to the query. The sparse bag-of-words representations of queries and content often fails to capture relevance, especially because of [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) (e.g., “sneakers” failing to match “athletic shoes” and [polysemy](https://en.wikipedia.org/wiki/Polysemy) (e.g., “mixer” having multiple meanings). [Dense embedding representations](https://en.wikipedia.org/wiki/Word_embedding) can do a better job of holistically capturing the meaning of queries and content and thus can do a better job of measuring relevance — though it is important to align the query and content representations (e.g., using [ColBERT](https://arxiv.org/abs/2004.12832)).

But remember that [relevance is not the same as ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e)! We will return to this distinction when we discuss desirability.

## Recall

If precision is about search applications returning “nothing but the truth”, then recall is about returning “the whole truth”. [Recall](https://en.wikipedia.org/wiki/Precision_and_recall) measures the fraction of relevant documents that were retrieved. Retrieval manages a tradeoff between precision and recall, relying on ranking to at least preserve position-weighted metrics like DCG by promoting relevant results.

Recall might not seem as important as precision, but it is still a key metric. After all, if a result is not retrievable, it might as not well even be in the search index. And for some domains (e.g., [eDiscovery](https://en.wikipedia.org/wiki/Electronic_discovery)), recall is critical.

### Traditional Approaches to Deliver Recall

The traditional strategies to deliver recall, beyond lowering the relevance thresholds (e.g., BM25 scores), are query expansion and query relaxation.

[Query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) adds tokens or phrases that can be used to match results. These tokens may be [synonyms](http://synonyms) or abbreviations, or may be obtained using [stemming](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) and [spelling correction](https://queryunderstanding.com/spelling-correction-471f71b19880). Query expansion increases retrieval using OR, e.g. rewriting “ip lawyer” as (“ip” OR “intellectual property”) AND (“lawyer” OR “attorney”). Since the additional tokens may cause a drift in meaning (e.g., expanding “laptop” to “computer”), it is common for matches that depend on them to be penalized relative to results that match the original query tokens. Indeed, a big risk is that query expansion does not respect the context of the whole query, e.g., rewriting “machine learning” as (“machine”) AND (“learning” OR “studying”). This loss of context can leads to a loss of precision.

[Query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425) feels like the opposite of query expansion: instead of adding tokens to the query, it removes them. But the goal is still to increase recall — by optionalizing tokens that hopefully are not necessary to ensure relevance. For example, a search for “cute fluffy kittens” might return results that do not contain “cute” but match “fluffy” and “kittens”. A query relaxation strategy can be naïve, e.g, retrieve documents that match all but one of the query tokens. But a naive strategy risks optionalizing a token that is critical to the query’s meaning, e.g., replacing “cute fluffy kittens”* *with “cute fluffy”. More sophisticated query relaxation strategies aim to only optionalize tokens that are redundant or relatively uninformative.

### AI-Based Approaches to Improve Recall

Query expansion and query relaxation are useful, time-tested strategies to deliever recall; but their failure to holistically consider query context makes them risky with regard to precision. Query relaxation, in particular, is risky enough that many search applications only use it as a last resort, when the alternative would be to return zero results. With AI, we can take a more holistic approach to recall.

As discussed earlier, we can use [dense embedding representations](https://en.wikipedia.org/wiki/Word_embedding) to holistically capture the meaning of queries and content. We can then use these representations for retrieval, replacing traditional token-based retrieval from an [inverted index](https://en.wikipedia.org/wiki/Inverted_index) with [similarity-based retrieval](https://en.wikipedia.org/wiki/Similarity_search) from a [vector database](https://en.wikipedia.org/wiki/Vector_database). This approach can significantly improve on the recall of token-based retrieval without incurring the risk of query expansion or query relaxation violating the holistic query context. The catch is that it can be challenging to ensure alignment of query and content representations.

A different way to use AI to improve recall is to rewrite queries based on [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043). It is often the case that multiple queries are just different ways to express the same or almost the same search intent. Sometimes it is easy to identify equivalent or similar queries based on superficial query variation, such as [stemming](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45), word order, [stop words](https://queryunderstanding.com/query-relaxation-342bc37ad425), [tokenization](https://queryunderstanding.com/tokenization-c8cdd6aef7ff), and [spelling](https://queryunderstanding.com/spelling-correction-471f71b19880). But more subtle variations can arise from the use of [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741) or redundant tokens, or from more holistic paraphrasing. Recognizing these more subtle variations requires the use of [AI for query understanding](https://queryunderstanding.com/ai-for-query-understanding-d8c073095fff). Specifically, AI can recognize when queries are [semantically equivalent](https://queryunderstanding.com/semantic-equivalence-of-e-commerce-queries-78630e5fab5d), and search applications can then improve recall throgh whole-query expansion, e.g., rewriting “machine learning” as “machine learning” OR “artificial intelligence”. This holistic approach avoids the risk that query expansion and relaxation introduce by interpreting tokens out of context.

In general, while AI can be useful to improve precision, it is most useful for improving recall by taking a more semantic approach to retrieval.

## Desirability

For most search applications, [ranking should consider more that just the relevance of the results](https://queryunderstanding.com/minimalist-models-for-search-ranking-847c9d247f4). Query-independent considerations, such as popularity, quality, or recency, often determine which relevant results to present to searchers on the first page, and in what order. The combination of query-independent signals reflects the desirability of the results.

Computing the desirability of results does not generally require AI. We can determine a result’s recency or popularity or directly from the content or from engagement logs. Computing result quality may take advantage of AI, but that depends on the application. An AI model may be helpful for measuring image or video quality, or for measuring writing quality for text.

As we discussed earlier, LTR is designed to improve ranking, not just to establish relevance. Most LTR models — even most hand-tuned models — combine query-dependent ranking factors that capture relevance with query-independent desirability ranking factors that capture desirability. A challenge with combining these factors is that it can lead to suboptimal tradeoffs between relevance and desirability. One common failure mode is returning desirable but irrelevant results. Another failure mode is favoring less desirable results because of negligible differences in relevance.

Some search intents are very specific. For someone looking for a specific product or document, anything other than an exact match may be useless. At the other extreme, a searcher with a more open-ended intent may be open to exploring desirable but less relevant results. AI can be very helpful for computing query [specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb).

So, while AI may not be necessary to compute result desirability, using AI to improve precision and recall — and thus to better manage the retrieval tradeoff that establishes relevance — makes it easier to separate the concerns of relevance and desirability, and thus avoid these failure modes.

## Putting it All Together

Precision, recall, and desirability are key concerns that every search application needs to address. Not only does a search application strive to tell the whole truth (recall) and nothing but truth (precision), but it also aims to promote desirable results based on query-independent factors like recency, popularity, and quality. AI has created opportunities across the search stack, but it is important to know what problem a solution is intended to solve. Hopefully this post provides a helpful framework.
