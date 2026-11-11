---
title: 'Stemming and Lemmatization'
company: Tunkelang
tag: 查询理解
date: 2017-02-16
url: https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45
account: 
origin: harvest3-202607
---
# Stemming and Lemmatization

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--6c086742fe45---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--6c086742fe45---------------------------------------)

4 min read

·

Feb 6, 2017

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D6c086742fe45&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fstemming-and-lemmatization-6c086742fe45&source=---header_actions--6c086742fe45---------------------post_audio_button------------------)

Share

Different forms of a word often communicate essentially the same meaning. For example, there’s probably no difference in intent between a search for *shoe* and a search for *shoes*.

These syntactic differences between word forms are called [inflections](https://en.wikipedia.org/wiki/Inflection), and they create challenges for query understanding. In the example of *shoe* and *shoes*, we probably want to treat the two forms identically. But we wouldn’t want to do the same for the words [*logistic*](https://en.wikipedia.org/wiki/Logistic_function) and [*logistic*](https://en.wikipedia.org/wiki/Logistics)*s*, which mean very different things despite their apparent similarity. Nor would we want to equate the words *universe* and *university*, even though both words derive from the same Latin root.

[Stemming](https://en.wikipedia.org/wiki/Stemming) and [lemmatization](https://en.wikipedia.org/wiki/Lemmatisation) are two approaches to handle inflections in search queries. We will discuss each of them and then consider a more general approach, which I call canonicalization.

**Stemming**

When we stem a mushroom, we chop off its stem and keep the cap that most people think of as the edible portion. Similarly, when we stem a word, we chop off its inflections and keep what hopefully represents the main essence of the word. Technically, it depends on the type of mushroom, and we’re throwing away the mushroom stems while keeping the word stems. Nonetheless, I hope the metaphor is useful.

The best-known and most popular stemming approach for English is the [Porter stemming algorithm](https://tartarus.org/martin/PorterStemmer/), also known as the Porter stemmer. It is a collection of rules (or, if you prefer, heuristics) designed to reflect how English handles inflections. For example, the Porter stemmer chops both *apple* and *apples* down to *appl*, and it stems *berry* and *berries* to *berri*.

If we apply a stemmer to queries and indexed documents, we can increase recall by matching words against their other inflected forms. It is critical that we apply the same stemmer to both queries and documents.

You can find an implementation of the Porter stemmer in any major [natural language processing](https://en.wikipedia.org/wiki/Natural_language_processing) library, such as [NLTK](http://www.nltk.org/) and the [Stanford NLP](http://nlp.stanford.edu/software/) suite. You can find stemmers for other languages (or create your own) in [Snowball](http://snowballstem.org/).

Just as using a knife to chop a mushroom stem may leave a bit of the stem or cut into the cap, stemming algorithms sometimes remove too little or too much. For example, Porter stems both *meanness* and *meaning* to *mean*, creating a false equivalence. On the other hand, Porter stems *goose* to *goos* and *geese* to *gees*, when those two words should be equivalent.

In general, stemming algorithms err on the side of being too aggressive, sacrificing precision in order to increase recall.

**Lemmatization**

Going back to our mushrooms, even an amateur chef knows that you shouldn’t just chop off the stems with a knife. Instead, you should carefully remove the stems, cutting around them with a paring knife or gently twisting them off.

[Lemmatization](https://en.wikipedia.org/wiki/Lemmatisation) tries to take a similarly careful approach to removing inflections. Lemmatization does not simply chop off inflections, but instead relies on a lexical knowledge base like [WordNet](https://wordnet.princeton.edu/) to obtain the correct base forms of words.

For example, WordNet lemmatizes *geese* to *goose* and lemmatizes *meanness* and *meaning* to themselves. In these examples, it outperforms than the Porter stemmer.

But lemmatization has limits. For example, Porter stems both *happiness* and *happy* to *happi*, while WordNet lemmatizes the two words to themselves. The WordNet lemmatizer also requires specifying the word’s part of speech — otherwise, it assumes the word is a noun. Finally, lemmatization cannot handle unknown words: for example, Porter stems both *iphone* and *iphones* to *iphon*, while WordNet lemmatizes both words to themselves.

In general, lemmatization offers better precision than stemming, but at the expense of recall.

**Canonicalization**

As we’ve seen, stemming and lemmatization are effective techniques to expand recall, with lemmatization giving up some of that recall to increase precision. But both techniques can feel like crude instruments.

If we generalize from stemming and lemmatization, what we have are ways to group together the related forms of a word, assigning them all a canonical form. While it’s easy to rely on heuristics like Porter stemming and WordNet lemmatization, there’s nothing to stop us from building our own knowledge base for canonicalization.

For example, we can use the equivalence classes from Porter stemming and Wordnet lemmatization as candidates, and then use further processing — either automatic or editorial — to improve precision by estimating word similarity.

The automatic detection of word similarity could be based on corpus analysis (e.g., [word embeddings](https://en.wikipedia.org/wiki/Word_embedding) like [word2vec](https://en.wikipedia.org/wiki/Word2vec)) or searcher behavior (queries, clicks from those queries, etc). Ideally, we use all available signals to train a machine-learned model.

Editorial detection requires human judgements. These could be at the level of token-token pairs, query-query pairs (to assess the tokens in context), or query-document pairs (to assess the end-to-end effect of query expansion.

Building your own knowledge base for canonicalization may sound like a lot of work, and it can be. I recommend that you start by leveraging off-the-shelf tools like Porter and WordNet, and then determine how much you want to invest in improving on them.

**Summary**

Inflections pose an important challenge for query understanding. Stemming and lemmatization are out-of-the-box tools for managing inflections, and you should always consider them as ways to improve recall. But you need to be aware of their weaknesses, and you should consider investing in a canonicalization approach that establishes the right balance of precision and recall for your application.

**Previous:** [**Spelling Correction**](/spelling-correction-471f71b19880#.6q3j92iqc)

**Next:** [**Query Rewriting: An Overview**](/query-rewriting-an-overview-d7916eb94b83#.6a2dww7yt)