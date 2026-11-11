---
title: 'Character Filtering'
company: Tunkelang
tag: 查询理解
date: 2016-12-17
url: https://queryunderstanding.com/character-filtering-76ede1cf1a97
account: 
origin: harvest3-202607
---
# Character Filtering

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--76ede1cf1a97---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--76ede1cf1a97---------------------------------------)

4 min read

·

Nov 20, 2016

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D76ede1cf1a97&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fcharacter-filtering-76ede1cf1a97&source=---header_actions--76ede1cf1a97---------------------post_audio_button------------------)

Share

Search queries are made up of characters. It’s easy to take characters for granted; indeed, people who have never implemented a search engine might not think of working with characters as particularly challenging. But there are subtleties at the character level that we must tackle before working our way up the rest of the query understanding stack.

This document describes a series of character filters, which are steps to transform text at the character level. It’s important that you execute these filters in the order presented, and that you apply exactly the same sequence of filters to indexed content as to search queries.

**Unicode Normalization**

Modern software systems support [Unicode](https://en.wikipedia.org/wiki/Unicode), a living, international standard for consistently encoding text across the world’s written languages. Because there can be many ways to represent the same character, Unicode introduces [normalization](http://unicode.org/faq/normalization.html) as a way to transform characters into standard canonical forms, making it possible to recognize and match equivalent representations.

Unicode supports two kinds of normalization:

* Normalization Form Canonical Decomposition (NFD). Characters are decomposed by canonical equivalence, and multiple combining characters are arranged in a specific order.
* Normalization Form Canonical Composition (NFC). Characters are decomposed and then recomposed by canonical equivalence.

Unicode also supports variants of the above, NFKD and NFKC, in which the decomposition step uses compatibility forms that more aggressively standardize characters.

For search engines, it’s simpler and more efficient to use a normalization based on decomposition than one based on composition. That’s because the first thing you’ll want to do to a normalized string is remove accents — which is straightforward after decomposition. You can use either NFD or NFKD — given the subsequent transformations, it’s unlikely you’ll notice a difference between the two.

Fortunately, Unicode normalization is natively supported by most of the tools you’re likely to use for developing search applications. You’ll find support for Unicode normalization in [Java](https://docs.oracle.com/javase/8/docs/api/java/text/Normalizer.Form.html) and [Python](https://docs.python.org/2/library/unicodedata.html), as well as in open-source search engines [Apache Lucene](https://lucene.apache.org/core/6_3_0/analyzers-icu/index.html) and [Elastic](https://www.elastic.co/guide/en/elasticsearch/guide/current/unicode-normalization.html).

**Removing Accents**

Unicode normalization transforms strings into a standard character encoding, but it leaves accents (more technically, [diacritics](https://en.wikipedia.org/wiki/Diacritic)) in place. For example, *café* with an accent is differently than *cafe* without an accent.

Accents can change the meanings of words. In Spanish, for example, *papa* means potato, while *papá* means dad.

But not all keyboards support accents. And even when keyboards do support accents, they require searchers to perform additional work to enter accented characters. Searchers are people, and people are lazy. So you shouldn’t assume searchers — or even content creators — will use accents consistently.

Hence, it’s a good idea to remove accents as part of indexing content and processing search queries. This step takes place after Unicode normalization, by removing all the diacritic characters.

Again, there are standard tools to remove accents. In Java, there’s [StringUtils.stripAccents](https://commons.apache.org/proper/commons-lang/apidocs/org/apache/commons/lang3/StringUtils.html#stripAccents-java.lang.String-); in Python, there’s the [Unidecode](https://pypi.python.org/pypi/Unidecode) module. In Apache Lucene, use the [ASCIIFoldingFilter](https://lucene.apache.org/core/6_3_0/analyzers-common/org/apache/lucene/analysis/miscellaneous/ASCIIFoldingFilter.html); in Elastic, use [asciifolding](http://asciifolding). These tools also simplify [ligatures](https://en.wikipedia.org/wiki/Typographic_ligature), e.g., they transform *æ* into *ae*.

Removing accents doesn’t mean you should forget about them entirely. It’s important to preserve original strings, accents and all, for displaying both the search results and the query. That’s not only respectful to the original text; it also mitigates the risk of confusing searchers when removing accents changes a word’s meaning.

**Ignoring Capitalization**

Many alphabets, notably the Roman alphabet, are bicameral — that is, they support two cases. In formal writing, such as this document, we expect to see proper use of uppercase and lowercase letters.

But, just as it’s unreasonable to expect searchers to make proper use of accents in their search queries, it’s unreasonable to expect proper capitalization. Hence, we recommend converting all strings to lowercase — a process also known as case folding.

In Java, you can convert a string to lowercase using [String.toLowerCase](https://docs.oracle.com/javase/8/docs/api/java/lang/String.html#toLowerCase--). In Python, you can use [lower](https://docs.python.org/2/library/stdtypes.html#str.lower). Apache Lucene has a [LowerCaseFilter](https://lucene.apache.org/core/6_3_0/analyzers-common/org/apache/lucene/analysis/core/LowerCaseFilter.html); Elastic has a [lowercase](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-lowercase-tokenfilter.html) token filter.

Case folding requires you to specify language of the text, called the locale (see previous post on [language identification](/language-identification-c1d2a072eda#.xzdm5j20q)). If you don’t know the language of the text, then you should use a default locale (e.g., United States English) for consistency.

**Every Filter is a Trade-Off**

Each of the filters we’ve discussed represents a trade-off of precision for recall. It’s possible that filtering will cause two words with different meanings to be canonicalized to the same representation.

If you believe this is a significant risk, then you should evaluate the precision of your filters through human judgments. Take a sample of queries, and evaluate how often the filtered queries preserve the original intent. If you see systematic errors, adjust your filters accordingly.

But be careful not to be so finicky about precision that you give up too much recall. The character filters described here are conservative, and you’ll probably want all of them in order to achieve effective string matching.

**Previous:** [**Language Identification**](/language-identification-c1d2a072eda#.9uescd8fw)

**Next:** [**Tokenization**](/tokenization-c8cdd6aef7ff#.h1ckkkprx)