---
title: 'Query Relaxation'
company: Tunkelang
tag: 查询理解
date: 2024-01-29
url: https://queryunderstanding.com/query-relaxation-342bc37ad425
account: 
origin: harvest3-202607
---
# Query Relaxation

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--342bc37ad425---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--342bc37ad425---------------------------------------)

5 min read

·

Mar 28, 2017

--

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D342bc37ad425&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-relaxation-342bc37ad425&source=---header_actions--342bc37ad425---------------------post_audio_button------------------)

Share

In the previous post, we discussed [query expansion](/query-expansion-2d68d47cf9c8#.p21z47nxm) as a way to increase recall. In this post we’ll discuss the other major technique for increasing recall: query relaxation.

Query relaxation feels like the opposite of query expansion. Instead of adding tokens to the query, we remove them. Ignoring tokens makes the query less restrictive and thus increases recall. An effective query relaxation strategy removes only tokens that aren’t necessary to communicate the searcher’s intent.

Let’s consider four approaches to query relaxation, in increasing order of complexity: stop words, specificity, syntactic analysis, and semantic analysis.

**Stop Words**

The simplest form of query relaxation is ignoring [stop words](https://en.wikipedia.org/wiki/Stop_words). Stop words are words like *the* and *of:* they generally don’t contribute meaning to the query; hence, removing them preserves the intent while increasing recall.

But sometimes stop words matter. There’s a difference between [*king hill*](https://en.wikipedia.org/wiki/King_Hill) and [*king of the hill*](https://en.wikipedia.org/wiki/King_of_the_Hill). And there’s even a post-punk band named [*The The*](https://en.wikipedia.org/wiki/The_The). These edge cases notwithstanding, stop words are usually safe to ignore.

Most open-source and commercial search engines come with a list of default stop words and offer the option of ignoring them during query processing (e.g. Lucene’s [StopFilter](https://lucene.apache.org/core/6_3_0/analyzers-common/org/apache/lucene/analysis/core/StopFilter.html)). In addition, you might consider these lists of [stop words in 29 languages](https://code.google.com/archive/p/stop-words/).

**Specificity**

Query tokens vary in their specificity. For example, in the search query *black hdmi cable*, the token *hdmi* is more specific than *cable*, which is in turn more specific than *black*. Specificity generally indicates how essential each query token is to communicating the searcher’s intent. Using specificity, we can determine that it’s more more reasonable to relax the query *black hdmi cable* to *hdmi cable* than to *black cable*.

**Inverse Document Frequency**

We can measure token specificity using [inverse document frequency](https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html) (idf). The inverse (idf is actually the [logarithm](https://en.wikipedia.org/wiki/Logarithm) of the inverse) means that rare tokens — that is, tokens that occur in fewer documents — have a higher idf than those that occur more frequently. Using idf to measure token specificity is a generalization of stop words, since stop words are very common words and thus have low idf.

Information retrieval has used idf for decades, ever since [Karen Spärck Jones](https://en.wikipedia.org/wiki/Karen_Sp%C3%A4rck_Jones)’s seminal 1972 paper on “[A statistical interpretation of term specificity and its application in retrieval](https://pdfs.semanticscholar.org/4f09/e6ec1b7d4390d23881852fd7240994abeb58.pdf)”. It’s often combined with term frequency (tf) to obtain [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf), a function that assigns weights to query tokens for scoring document relevance. For example, Lucene implements a [TFIDFSimilarity](https://lucene.apache.org/core/6_3_0/core/org/apache/lucene/search/similarities/TFIDFSimilarity.html) class for scoring.

But be careful about edge cases. Unique tokens, such as proper names or misspelled words, have very high idf but don’t necessarily represent a corresponding share of query intent. Tokens that aren’t in the corpus have undefined idf — though that can be fixed with smoothing, e.g., adding 1 before taking the logarithm. Nonetheless, idf is a useful signal of token specificity.

**Lexical Databases**

A completely different approach to measuring specificity is to use a lexical database (also called a “knowledge graph”) like [WordNet](https://en.wikipedia.org/wiki/WordNet) that arranges concepts into semantic hierarchies. This approach is useful for comparing tokens with a hierarchical relationship, e.g., *dog* is more specific than *animal*. It’s less useful for tokens without a hierarchical relationship, e.g., *black* and *hdmi*.

A lexical database also enables a more nuanced form of query relaxation. Instead of ignoring a token, we can replace it with a more general term, also known as a [hypernym](https://en.wikipedia.org/wiki/Hyponymy_and_hypernymy). We can also use a lexical database for query expansion.

**Syntactic Analysis**

Another approach to query relaxation to use a query’s [syntactic](https://en.wikipedia.org/wiki/Syntax) structure to determine which tokens are optional.

A large fraction of search queries are [noun phrases](https://en.wikipedia.org/wiki/Noun_phrase). A noun phrase serves the place of a [noun](https://en.wikipedia.org/wiki/Noun) — that is, it represents a thing or set of things. A noun phrase can be a solitary noun, e.g., *cat*, or it can a complex phrase like *the best cat in the whole wide world*.

We can analyze search queries using a [part-of-speech tagger](https://en.wikipedia.org/wiki/Part-of-speech_tagging), such as [NLTK](http://www.nltk.org/), which in turn allows us to [parse](https://en.wikipedia.org/wiki/Parsing) the overall syntactic structure of the query. If the query is a noun phrase, parsing allows us to identify its [head](https://en.wikipedia.org/wiki/Head_(linguistics)) noun, as well as any [adjectives](https://en.wikipedia.org/wiki/Adjective) and phrases modifying it.

A reasonable query relaxation strategy preserves the head noun and removes one or more of its modifiers. For example, the most important word in *the best cat in the whole wide world* is the head noun, *cat*.

But this strategy can break down. For example, if the query is *free shipping*, the adjective *free* is at least as important to the meaning as the head noun *shipping*. Syntax does not always dictate semantics. Still, emphasizing the head noun and the modifiers closest to it usually works in practice.

**Semantic Analysis**

The most sophisticated approach to query relaxation goes beyond token frequency and syntax and considers [semantics](https://en.wikipedia.org/wiki/Semantics) — that is, what the tokens mean, particularly in relation to one another.

For example, we can relax the query *polo shirt* to *polo*, since shirt is implied. In contrast, relaxing *dress shirt* to *dress* completely changes the query’s meaning. Syntax isn’t helpful: in both cases, we’re replacing a noun phrase with a token that isn’t even the head noun. And *shirt* is no more specific than *polo* or *dress*. So we need to understand the semantics to relax this query successfully.

We can use the [Word2vec](https://en.wikipedia.org/wiki/Word2vec) model to embed words and phrases into a vector space that captures their semantics. This embedding allows us to recognize how much the query tokens overlap with one another in meaning, which in turn helps us estimate the consequence of ignoring a token. Word2vec also allows us to compute the similarity between a token and a phrase containing that token. If they’re similar, then it’s probably safe to relax the query by replacing the phrase with the token.

**Relax but be Careful**

Like query expansion, query relaxation aims to increase recall while minimizing the loss of precision. If we already have a reasonable quantity and quality of results, then query relaxation probably isn’t worth the risk.

Query relaxation is most useful for queries that return few or no results, since those are the queries for which we have the least to lose and the most to gain. But remember that more results doesn’t necessarily mean better results. Use query relaxation, but use it with care.

**Previous:** [**Query Expansion**](/query-expansion-2d68d47cf9c8#.p21z47nxm)

**Next:** [**Query Segmentation**](/query-segmentation-2cf860ade503)