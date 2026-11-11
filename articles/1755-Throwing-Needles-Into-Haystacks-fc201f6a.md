---
title: 'Throwing Needles Into Haystacks'
company: Tunkelang
tag: 搜索相关性
date: 2023-01-18
url: https://dtunkelang.medium.com/throwing-needles-into-haystacks-ba7144c747cb
account: Tunkelang
origin: harvest3-202607
---
# Throwing Needles Into Haystacks

Searching for relevant results has been compared to finding a [needle in a haystack](https://en.wiktionary.org/wiki/needle_in_a_haystack). Thankfully, most searchers have it easier than that, since haystacks don’t index their needs to make them more findable.

Ironically, it sometimes feels like search applications throw needles into a haystack and then try to find them. This should sound to you like a bad idea, and it is! So let’s unpack the metaphor and explore it.

### Sparse and Dense Content Representations

A search index represents content with the goal of making it findable. There are three common strategies:

- **Unstructured text.** For products and documents that are mostly text, it’s natural to index them as [bags of words](https://en.wikipedia.org/wiki/Bag-of-words_model) stored in an [inverted index](https://en.wikipedia.org/wiki/Inverted_index). The inverted index maps words to the products or documents containing those words. Since each piece of content contains only a tiny subset of available words, the bag of words has a [sparse vector](https://en.wikipedia.org/wiki/Sparse_matrix) representation.

- **Structured data.** Content often contains explicit structured information in the form of categories, such as product types or topics, or attributes, such as brand or color. This representation is even sparser than a bag of words, since categories and attributes carry more signal than most words. Structured data is so useful that search applications often employ [content understanding](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974) techniques to obtain it.

- **Embeddings.** [Word embeddings](https://en.wikipedia.org/wiki/Word_embedding) are dense representations of content, mapping content to dense vectors in a high-dimensional [vector space](https://en.wikipedia.org/wiki/Vector_space). These vectors are dense in the sense that they are filled with non-zero values. The vectors are stored in specialized indexes for efficient [nearest-neighbor retrieval](https://en.wikipedia.org/wiki/Nearest_neighbor_search), typically using [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity) as a metric.

### Representing Search Intent

Search intent usually starts in the form of a search query, which typically contains no more than a few words. Despite the excitement about natural language, voice, image, and other interface modalities, nothing seems to have replaced simple keywords as the default way to express search intent.

Given that most queries are short, it’s not surprising that many of them map directly to categories and attributes. After all, categories and attributes represent some of the most information-rich words and phrases.

How should a search application handle such queries? Just as with content representation, there are three common strategies:

- **Full-text search.** This is what most search applications do: match all fields containing the query words (usually after some [query rewriting](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83), like [stemming](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) and [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8)) using the inverted index, and then rank the results using [query-dependent and query-independent factors](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e).

- **Map to structured data.** Through [query understanding](https://queryunderstanding.com/introduction-c98740502103), it is often possible to map queries to categories, attributes, or combinations of the two. This approach delivers precise, coherent retrieval; but it risks losing recall that might have been retrieved by full-text search.

- **Dense retrieval.** This approach maps the query to a vector and then performs a nearest-neighbor search to retrieve results based on cosine similarity. Since cosine similarity only measures query-dependent relevance, ranking also considers query-independent factors. This approach tends to favor [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall), since dense retrieval is liberal with regard to matching query words, but [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision) can be a challenge.

### Needles and Haystacks

Some search tasks are hard. For example, it’s pretty tough to find a song when you can’t remember either the name or artist but only a few lyrics in the middle of the song that you may have muddled. That’s a genuine, needle-in-a-haystack problem. But most search tasks aren’t so challenging.

For example, if you’re interested in a particular song, artist, or genre, your interaction with a search engine should be pretty straightforward. If you can express a simple search intent using words that map directly to structured data, you should reasonably expect the search application to understand what you mean and retrieve results accordingly.

For search needs that do not map to categories, attributes, or combinations of the two, such as the lyrics example above, full-text search offers the potential to still retrieve relevant results. But for simpler queries, full-text search is unlikely to offer much additional recall — at least if content is properly indexed — and it can wreak havoc on precision, e.g., retrieving the Beatles song “Lady Madonna” when you search for the artist Madonna.

And then there’s dense retrieval. As noted earlier, dense retrieval favors recall, since it retrieves based on similarity rather than by matching query words, let alone structured data. That makes sense for long or difficult queries, and dense retrieval is especially useful for recall-oriented search needs, like finding results similar to content that is unavailable or rare.

But for the more precision-oriented search typically addressed by full-text search today, it’s hard to see how dense retrieval can help — and easy to see how it can hurt. For example, if you’re searching for men’s shirts, then the search application should retrieve all men’s shirts as results, ideally using structured data. It’s hard to see the benefit of a nearest-neighbor search using dense vectors; after all, being a men’s shirt is a binary thing, not a degree of similarity to some [Platonic ideal](https://en.wikipedia.org/wiki/Theory_of_forms).

### Query Understanding vs. Retrieval

Advocates of dense retrieval may object that I’ve glossed over an important detail: even when search queries map to structured data, they don’t always do so cleanly. There may be a men’s shirts category, or there may be a shirts category and an independent gender attribute. The query might be “men’s shirts”, “shirts for men”, or some other variant expressing the same intent. Full-text search struggles with this sort of variation, and dense retrieval at least holistically represents the search intent in a single vector.

But retrieval isn’t the place to address query understanding. “Men’s shirts” and “shirts for men” should retrieve identical results — and that they should do so regardless of whether the results are indexed using a men’s shirts category or using a shirts category combined with an independent gender attribute. The right way to achieve this is through query understanding, and specifically by recognizing [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043).

Once we have established that the searcher is looking for men’s shirts, retrieval should be trivial and ranking, while perhaps not trivial, has nothing to do with query-dependent relevance.

There can be a role for dense retrieval here. But it’s dense retrieval of queries, not results. Indeed, we can use query similarity to identify a canonical representation of the searcher’s intent in a set of queries for which we have established a robust retrieval and ranking strategy.

### Don’t Throw Needles Into Haystacks!

Most searches today are short keyword queries, corresponding to a category or attribute, or perhaps a combination of the two. These are simple queries, and they deserve simple retrieval strategies. If there’s complexity, it’s mostly in the nuances of query understanding. So don’t rush to apply dense retrieval. Don’t throw needles into haystacks!
