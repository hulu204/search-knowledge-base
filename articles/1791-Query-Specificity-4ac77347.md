---
title: 'Query Specificity'
company: Tunkelang
tag: 查询理解
date: 2024-11-20
url: https://queryunderstanding.com/query-specificity-a6156f4043eb
account: 
origin: harvest3-202607
---
# Query Specificity

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--a6156f4043eb---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--a6156f4043eb---------------------------------------)

7 min read

·

Jan 10, 2024

--

3

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Da6156f4043eb&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-specificity-a6156f4043eb&source=---header_actions--a6156f4043eb---------------------post_audio_button------------------)

Share

The central challenge of query understanding is [mapping a query to a representation of the searcher’s intent](https://dtunkelang.medium.com/search-queries-and-search-intent-1dec79ad155f). Recognizing when two or more different search queries represent the same or similar intent opens up a variety of opportunities to improve the search experience.

However, search intents vary in specificity. For example, the query “new balance 608 mens” maps to a much more specific intent (only leaving room for variations in shoe size and color) than the broader queries “mens shoes” or “mens new balance shoes”.

This post, which reflects joint work with [Aritra Mandal](https://www.linkedin.com/in/aritram/), explores how to define, compute, and apply query specificity.

## Heuristics for Query Specificity

While the concept of query specificity may seem intuitive, an intuition is not sufficient to provide a precise definition. We need a concrete definition to compute, and apply query specificity. Otherwise, we risk relying on a vague notion of some queries being broad and others being narrow.

Let us start with some intuitive heuristics, and then work our way towards a robust approach based on the [bag-of-documents model](https://dtunkelang.medium.com/exploring-search-intent-as-a-duality-c0c260500599).

### Taxonomic Depth

A [taxonomy](/taxonomies-and-ontologies-8e4812a79cb2) organizes knowledge into categories based on parent-child relationships. For example, a taxonomy might make men’s athletic shoes a child category of men’s shoes, and men’s shoes a child category of men’s clothing.

Mapping queries to categories allows us to use relative or absolute depth in the taxonomy to define query specificity, i.e., the specificity of a child is higher than that of its parent. Even if there isn’t a path between two categories, we can still compare their depths (i.e., distance from the root).

But this approach requires that we are able to map queries to categories. We will return to that question in a moment.

### Selectivity

Intuitively, more specific queries should return fewer results than less specific queries. This intuition generalizes the idea of taxonomic depth, since selectivity does not require that queries — or categories — be arranged in a single hierarchy. For example, the query “mens shoes” is more specific than either “shoes” or “mens clothing”. For that matter, “black mens shoes” is more specific than “mens shoes” (color is typically a [facet](/faceted-search-7d053cc4fada)). Moreover, since counting results does not rely on hierarchical relationships among categories, we can easily compare the specificity of any two queries, e.g., “air jordan 1 high” is more specific than “mens shirts”.

Unfortunately, there are at least two problems with using selectivity to measure specificity. The first is that selectivity is sensitive to the distribution of content in the index: for example, the relative number of shirts and pants in the index should not determine the relative specificity of “shirts” and “pants” as queries. The second is that the number of results is sensitive to the [precision and recall](https://en.wikipedia.org/wiki/Precision_and_recall) of the search engine’s retrieval strategy. The query-dependent precision-recall tradeoffs are likely to make the result count will be an unreliable the the search intent’s specificity.

### Entropy

[Entropy](https://en.wikipedia.org/wiki/Entropy_(information_theory)) is a measure of disorder or uncertainty. [Claude Shannon](https://en.wikipedia.org/wiki/Claude_Shannon) defined the entropy of a [probability distribution](https://en.wikipedia.org/wiki/Probability_distribution) as the [expected value](https://en.wikipedia.org/wiki/Expected_value) of the [information content](https://en.wikipedia.org/wiki/Information_content) of a value drawn from that distribution. Entropy measures how much a probability distribution spreads out over its values.

Entropy feels like the opposite of specificity. A query split between two categories has higher entropy — and thus lower specificity — than a query confined to a single category (though we should use a [similarity-sensitive entropy](https://dtunkelang.medium.com/similarity-sensitive-diversity-16a35d64f48c) measure to account for the similarity among categories). Thus, if we can map a query to a probability distribution of categories, rather than to a single category, we can measure its specificity based on the entropy of the probability distribution. We can also use the [relative entropy (aka Kullback-Leibler divergence)](https://en.wikipedia.org/wiki/Kullback%E2%80%93Leibler_divergence) of the category distribution of the query to normalize the entropy relative to that of the index.

The main drawback of this approach is that reducing a query to a probability distribution over categories is a lossy transformation. It ignores variation of results within a category, neglecting facets or other sources of variation that are independent of the category taxonomy.

## Computing Query Specificity

Entropy takes us in the right direction. But we need to move beyond relying on a category distribution to define query specificity.

As we saw with our earlier example of “black mens shoes” and “mens shoes”, queries can vary in specificity for reasons unrelated to category distribution. We need a measure that accounts for this.

### Bag-of-Documents Model

Our first step is to model a query as a [bag of documents](https://dtunkelang.medium.com/exploring-search-intent-as-a-duality-c0c260500599). If we have results associated with a query (i.e., frequent queries in our logs), we can implement this model by first representing the query results as vectors (using any available [embedding](https://en.wikipedia.org/wiki/Word_embedding) model) and the taking the mean of those result vectors to obtain a query vector.

To generalize the bag-of-documents model to queries for which we do not have results, we use queries for which we do have results to [train a sentence embedding model](https://huggingface.co/blog/how-to-train-sentence-transformers). The bag-of-documents model provides a way to measure [query similarity](/query-similarity-49dde9f78043) as the cosine between query vectors.

### Variance

We now build on this model to obtain a measure of query specificity.

In the bag-of-documents model, the query vector is the mean of the result vectors — or the output of a model trained using queries and their query vectors. We now consider the [variance](https://en.wikipedia.org/wiki/Variance) among the result vectors.

Variance is a measure of [dispersion](https://en.wikipedia.org/wiki/Statistical_dispersion): it measures how far a set of numbers is spread out from their average value. A more spread-out distribution has a higher variance. Thus, a lower variance signifies higher specificity.

Using variance to measure specificity makes intuitive sense, but how do we compute it? We are working with distributions of vectors, not numbers. And in search we generally prefer [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) over [Euclidean distance](https://en.wikipedia.org/wiki/Euclidean_distance) to compare vectors.

We can compute the variance of the cosines among the pairs of vectors in our bag of documents. If we have n vectors, then there are [n(n-1)/2 pairs](https://en.wikipedia.org/wiki/Combination), and we can compute the variance of this set of n(n-1)/2 numbers.

This approach is straightforward, but it is a bit expensive. A less expensive way to achieve a similar result is to compute the cosine between each result vector and the query vector (which is the mean of the result vectors), and then take the mean of the cosines. This approach is similar in spirit to taking the [expected value](https://en.wikipedia.org/wiki/Squared_deviations_from_the_mean) of the [squared deviation from the mean](https://en.wikipedia.org/wiki/Squared_deviations_from_the_mean), only that we use cosine similarity instead of the square of Euclidean distance.

Unlike variance, this measure achieves its maximum value of 1 when all of the results have the same vector. Otherwise, the value could be as low as -1 in theory, but in practice is unlikely to be negative — since [cosines between embeddings tend to be positive](https://vaibhavgarg1982.medium.com/why-are-cosine-similarities-of-text-embeddings-almost-always-positive-6bd31eaee4d5).

We can generalize this approach if we want to apply it to queries for which we do not have results. As before, we can use queries for which we do have results in order to train a model. This time, however, we want a regression model, since we are mapping queries to scalar values. Fortunately, we can [modify BERT to perform regression](https://lajavaness.medium.com/regression-with-text-input-using-bert-and-transformers-71c155034b13).

## Applying Query Specificity

Now that we can compute query specificity, let us explore ways to apply it.

### Detecting Broad and Ambiguous Queries

When a search query is broad (e.g., “shoes”), it is not clear how to decide which matching results are the most relevant or desirable ones. Even worse, when a query is ambiguous (e.g., “[mixers](https://en.wikipedia.org/wiki/Mixer)”), it is not even clear how to determine which results match the query, let alone how to rank them.

Query specificity can help us determine if a search query is [broad or ambiguous](https://dtunkelang.medium.com/broad-and-ambiguous-search-queries-1bbbe417dcc). Moreover, query specificity as described in this post is a more principled and robust measure than heuristics like result count.

When we detect that a query are broad or ambiguous, we can promote interface elements like [clarification dialogues](/clarification-dialogues-69420432f451) and [faceted refinements](/faceted-search-7d053cc4fada).

### Improving Query Suggestions

In general, higher-specificity queries perform better than lower-specificity queries because they give the search engine more signal. Moreover, low-specificity queries may fail to express the searcher’s more specific intent. Someone who searches for “shoes” may have a particular brand or style in mind but may not know to express (or know how to [spell](/spelling-correction-471f71b19880)) the right words to represent their specific intent. Searchers may also be lazy about typing — and may be nudged towards short, popular queries by [autocomplete](/autocomplete-69ed81bba245).

Query specificity can help guide searchers to [better queries](https://dtunkelang.medium.com/better-search-through-better-queries-c192412a86e9). All else equal, query suggestion components, such as [autocomplete](/autocomplete-69ed81bba245) and related search suggestions, should promote higher-specificity queries.

### Managing Retrieval Tradeoffs

[Ranking is about more than the relevance](https://dtunkelang.medium.com/ranking-vs-relevance-ba672c79625e). Query-independent desirability factors, such as popularity, quality, or recency, determine which relevant results to present to searchers on the first page, and in what order.

Combining relevance with desirability is tricky. If a result is irrelevant, it does not matter how desirable it is. But if two results only differ slightly in relevance, the more desirable one should probably rank higher.

But that depends on query specificity. If the searcher has a highly specific intent, then anything other than an exact match may be useless.

We can use query specificity to model the rate of exchange at which searchers (on average) are willing to trade relevance for desirability, as well as to manage [precision-recall](https://en.wikipedia.org/wiki/Precision_and_recall) tradeoffs in general.

### Analyzing Search Behavior

[Analyzing searcher behavior](https://dtunkelang.medium.com/evaluating-search-measuring-searcher-behavior-5f8347619eb0) is a fundamental way to evaluate search applications. The analysis generally focuses on engagement signals, such as click-through rate, conversion rate, and [mean reciprocal rank (MRR)](https://en.wikipedia.org/wiki/Mean_reciprocal_rank) of engagement at the query and [session](/session-context-4af0a355c94a) level.

But, as we have observed, not all queries are equal. Low-specificity queries lead to different patterns of search behavior than high-specificity queries. We expect most low-specificity queries to require additional refinement, while we hope that most high-specificity queries will return useful results.

Including query specificity as a dimension in our analysis avoids conflating query classes for which we expect different kinds of behavior. Refining our analysis this way hopefully leads to better targeted search improvements.

## Summary

Query specificity captures the intuition that queries vary in how broad or narrow they are. Using the bag-of-documents model, we obtain a method to compute query specificity that is more general and principled than heuristics like taxonomy depth or result count. We can then apply query specificity in a variety of ways to improve search applications.