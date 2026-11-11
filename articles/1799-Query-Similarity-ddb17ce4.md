---
title: 'Query Similarity'
company: Tunkelang
tag: 查询理解
date: 2025-03-05
url: https://queryunderstanding.com/query-similarity-49dde9f78043
account: 
origin: harvest3-202607
---
# Query Similarity

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--49dde9f78043---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--49dde9f78043---------------------------------------)

6 min read

·

Oct 24, 2022

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D49dde9f78043&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-similarity-49dde9f78043&source=---header_actions--49dde9f78043---------------------post_audio_button------------------)

Share

I [started writing about query understanding](/introduction-c98740502103) in 2016, working my way up from low-level concerns like [language identification](/language-identification-c1d2a072eda#.31zvyedn5) and [character normalization](/character-filtering-76ede1cf1a97#.i91zgwxxn) to higher-level topics like [query rewriting](/query-rewriting-an-overview-d7916eb94b83), [contextual query understanding](/contextual-query-understanding-65c78d792dd8), and [question answering](/question-answering-94984185c203). I hope folks have found it useful!

But recently my all-consuming passion has been query similarity, as might be evident from my post on [mapping queries to intents](https://dtunkelang.medium.com/search-queries-and-search-intent-1dec79ad155f) and my colleague [Aritra Mandal](https://www.linkedin.com/in/aritram/)’s presentation on [using AI to understand search intent](https://dtunkelang.medium.com/using-ai-to-understand-search-intent-1fef055e901f).

So here’s a bonus query understanding post on this exciting topic!

### To Search is Human

Let’s start with why we search. A query is an expression of an information-seeking intent. A search engine’s first job is to infer searchers’ intents from their queries — that’s the whole point of query understanding!

But we humans each have our own ways to express ourselves. And the way we uniquely express ourselves is fundamental to what makes us human.

Unfortunately, machines don’t appreciate our individuality. Indexing and retrieving content would be much simpler if everyone agreed on a [controlled vocabulary](https://en.wikipedia.org/wiki/Controlled_vocabulary), as well as a rigid schema to organize each document into fields. Then we could replace natural language search with [SQL](https://en.wikipedia.org/wiki/SQL)!

But even if such a requirement were feasible, it would be self-defeating. Search should embrace our humanity rather than stifle it. The challenge for a search engine is to do so but still understand all of our intents. Then it can retrieve, rank, present, and organize results — as well as log and analyze searcher behavior— based on intent rather than particular query keywords.

### Superficial Query Variation

Sometimes it’s easy to see from looking at a pair of queries that they are different ways of expressing the same search intent. This is especially true when the differences come from superficial query variation:

* [**Stemming or lemmatization**](/stemming-and-lemmatization-6c086742fe45). Many search queries are [noun phrases](https://en.wikipedia.org/wiki/Noun_phrase), since searchers mostly look for things. Using singular or plural forms (e.g., *cat video* vs. *cat videos*) tends to be arbitrary: a person who searches for *cat video* is likely to watch more than one of them! Queries that differ only in word endings tend to express similar intent. Of course there are exceptions, such as [*logistic*](https://en.wikipedia.org/wiki/Logistic_function) and [*logistics*](https://en.wikipedia.org/wiki/Logistics), but these exceptions are rare.
* **Word order**. When we communicate with one another in natural language, word order generally matters (e.g, [*man bites dog*](https://en.wikipedia.org/wiki/Man_bites_dog) vs. *dog bites man*). But search engines don’t pay much attention to word order, so *shoes nike* means the same thing as *nike shoes*. There are exceptions, of course, like [*shirt dress*](https://en.wikipedia.org/wiki/Shirtdress) vs. [*dress shirt*](https://en.wikipedia.org/wiki/Dress_shirt), but these are mostly solved by [query segmentation](/query-segmentation-2cf860ade503). In general, varying word order, especially if we respect segments, tends to preserve a query’s meaning.
* [**Stop words**](https://en.wikipedia.org/wiki/Stop_word). Stop words are common words, such as *the*, that search engines sometimes ignore in queries because they’re unlikely to carry meaning. Of course, word significance depends on context (e.g., songs by [*The The*](https://en.wikipedia.org/wiki/The_The)). Nonetheless, the addition or removal of stop words (e.g., *shoes men* vs. *shoes for men*), generally preserves meaning.
* [**Tokenization**](/tokenization-c8cdd6aef7ff). Spacing and punctuation also introduce superficial query variation (e.g., *twenty one* vs. *twenty-one* vs. *twentyone*). Tokenization is also prone to variation when queries include numbers (e.g., *9v battery* vs *9 v battery*). Variations from tokenization generally preserve intent. Though, as always, there are exceptions (e.g., *1.0 liter jug* vs. *10 liter jug*).
* [**Spelling**](/spelling-correction-471f71b19880). We humans aren’t great spellers, and sometimes we can’t even agree on the proper spelling of a word (e.g., *judgment* vs. *judgement*). Correct or not, spelling variations generally don’t change the intent of a query: someone who searches for a *louie vitton purse* is almost certainly looking for a *Louis Vuitton purse*.

In combination, these sources of query variation lead to numerous ways to express a given search intent. And these are just the superficial ones!

### Semantic Query Variation

Sometimes it’s not so easy to see that two queries express the same search intent. The queries might use different words with similar meanings. Or the similarity may only be evident to someone with domain knowledge. Here are some sources of semantic query variation:

* [**Synonyms**](https://dtunkelang.medium.com/real-talk-about-synonyms-and-search-bb5cf41a8741). A person looking for a *couch* probably wants the same thing as someone looking for a *sofa*. But synonyms are contextual: *bifocal glasses* are *eyeglasses*, but *wine glasses* are not. Still, when the context is appropriate, using a synonym preserves the meaning of the query.
* **Redundancy**. An *ipad pro* is implicitly an *apple ipad pro*, and *new balance* implies *new balance shoes*. Regardless of whether or why some searchers supply this redundant information to the search engine and others don’t, the inclusion of redundant words doesn’t change the intent.
* **Paraphrasing**. Sometimes query variation is more subtle. For example a *coffee mug* is typically a *12 oz mug*. A *pixel charging cable* is the same as a *usb c to usb c cable*. These kinds of equivalences aren’t based on synonyms, and recognizing them requires specific domain knowledge.

### Measuring Query Similarity

If we were only concerned with measuring superficial query similarity, we could probably rely on simple measures like edit distance (also known as [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)) at the character level or [Jaccard similarity](https://en.wikipedia.org/wiki/Jaccard_index) at the token level. These kinds of measures are useful ways to compare strings if we don’t require any semantic understanding of what the strings mean.

But search queries do mean something, so we need to look beyond their superficial similarity to consider semantic variation.

### Representing Queries as Vectors

In order to measure query similarity in a way that addresses both superficial and semantic variation, our best bet is to represent those queries as vectors. Then we can simply use [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity).

But how do we represent queries as vectors?

The simplest approach is to use a [sentence embedding](https://en.wikipedia.org/wiki/Sentence_embedding) model to map queries (which don’t have to be sentences in the grammatical sense) to vectors. Specifically, we can use one of the free, pre-trained models from the [HuggingFace collection of Sentence Transformers models](https://huggingface.co/sentence-transformers).

While this approach is simple, using a pre-trained model is unlikely to deliver great performance, unless the model was trained on examples that are representative of the search application’s queries. It’s much better to train a sentence embedding model from scratch or fine-tune a pre-trained one. Unfortunately, both of these approaches require not only a significant computational investment, but also a lot of labeled query pairs.

### Representing Queries as Bags of Documents

A different way to measure query similarity is to look at post-query behavior. Queries that express the same intent tend to be followed by similar behavior, i.e., engagement with similar documents.

Since documents tend to be larger and more self-contained than queries, it’s easier to map them to robust vector representations. Moreover, we can aggregate multiple document vectors associated with a query, e.g., by taking their mean. In effect, we are representing queries as bags of associated documents. As before, we can measure query similarity using cosine similarity. But this approach allows us to use a pre-trained model for the document vectors and still obtain reasonable results.

A limitation of this approach is that it relies on offline computation to analyze post-query behavior and aggregate the associated document vectors. In particular, this limitation restricts its coverage to [head and torso](https://en.wikipedia.org/wiki/Long_tail) queries. How do we handle the tail of the query distribution, including queries that we’ve never seen before?

To extend this approach to tail queries, we need to move beyond aggregating the document vectors obtained from pre-trained models. We need to train — or at least fine-tune — a model that maps queries to vectors. We use our vectors for head and torso queries to generate training data — specifically, query pairs and their associated cosine similarity. This approach is complicated, but you can learn more from the [HuggingFace article on training and fine-tuning Sentence Transformers](https://huggingface.co/blog/train-sentence-transformers).

### Summary

A search engine’s first job is inferring searchers’ intents from their queries. Queries with equivalent intent should yield equivalent representations. A search engine can recognize query similarity based on superficial query variation, such as stemming, word order, stop words, tokenization, and spelling. More subtle variations from synonyms, redundancy, and paraphrasing require semantic understanding that can be learned from post-search behavior. We can use embeddings to represent queries as vectors, specifically, by aggregating vectors of associated documents. This approach yields reasonable results from pre-trained models. This offline approach works for head and torso queries, and also provides labeled data that we can use to train or fine-tune an online model for tail queries.