---
title: 'Spelling Correction'
company: Tunkelang
tag: 查询理解
date: 2022-03-15
url: https://queryunderstanding.com/spelling-correction-471f71b19880
account: 
origin: harvest3-202607
---
# Spelling Correction

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--471f71b19880---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--471f71b19880---------------------------------------)

7 min read

·

Jan 16, 2017

--

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D471f71b19880&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fspelling-correction-471f71b19880&source=---header_actions--471f71b19880---------------------post_audio_button------------------)

Share

Spelling correction is a must-have for any modern search engine. Estimates of the fraction of misspelled search queries vary, but a variety of studies place it between 10% and 15%. For today’s searchers, a search engine without robust spelling correction simply doesn’t work.

That doesn’t mean, however, that you should build a spelling correction system from scratch. Off-the-shelf spelling correction systems, such as [Aspell](https://en.wikipedia.org/wiki/GNU_Aspell) or [Hunspell](https://en.wikipedia.org/wiki/Hunspell), are highly customizable and should suit most people’s needs.

It’s still important, however, to understand how spelling correction works. A great starting point is [Peter Norvig](https://en.wikipedia.org/wiki/Peter_Norvig)’s classic post on “[How to Write a Spelling Corrector](http://norvig.com/spell-correct.html)”, which walks through fundamental concepts like [edit distance](https://en.wikipedia.org/wiki/Edit_distance), language models, and error models.

Let’s look at the key aspects of a spelling-correction system.

**Overview**

Offline, before any queries take place:

* **Indexing Tokens.** Building the index used at query time for candidate generation.
* **Building a language model.** Computing the model to estimate the a priori probability of an intended query.
* **Building an error model.** Computing the model to estimate the probability of a particular misspelling, given an intended query.

At query time:

* **Candidate generation.** Identifying the spelling correction candidates for the query.
* **Scoring.** Computing the score or probability for each candidate.
* **Presenting suggestions.** Determining whether and how to present a spelling correction.

Let’s drill down into each of these aspects.

**Indexing Tokens**

Indexing for spelling correction is a bit different than for document retrieval. The fundamental data structure for document retrieval is an [inverted index](https://en.wikipedia.org/wiki/Inverted_index) (also known as a posting list) that maps [tokens](/tokenization-c8cdd6aef7ff) to documents. In contrast, indexing for spelling correction typically maps substrings of tokens ([character n-grams](https://en.wikipedia.org/wiki/N-gram)) to tokens.

Most misspelled tokens differ from the intended tokens by at most a few characters (i.e, a small [edit distance](https://en.wikipedia.org/wiki/Edit_distance)). An index for [approximate string matching](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.11.5629&rep=rep1&type=pdf) enables discovery of these near-misses through retrieval of strings — in our case, tokens — by their substrings. We generate this index by identifying the unique tokens in the corpus, iterating through them, and inserting the appropriate substring-to-string mappings into a [substring index](https://en.wikipedia.org/wiki/Substring_index), such as an n-gram index or a [suffix tree](https://en.wikipedia.org/wiki/Suffix_tree).

Although this description assumes a batch, offline indexing process, it is straightforward to update the index incrementally as we insert, remove, or update documents.

This index grows with the size of the corpus vocabulary, so it can become quite large. Moreover, as vocabulary grows, the index becomes more dense: in particular, short substrings are mapped to large numbers of tokens. Hence, a spelling correction system must make tradeoffs among storage, efficiency, and quality in indexing and candidate generation.

It is also possible to index tokens based on how they sound, such as canonicalizing them into [Metaphone](https://en.wikipedia.org/wiki/Metaphone) codes. This approach is most useful for words with unintuitive spellings, such as proper names or words adopted from other languages.

**Building Models**

The goal of spelling correction is to find the correction, out of all possible candidate corrections (including the original query), that has the highest probability of being correct. In order to do that, we need two models: a language model that tells us a priori probability of a query, and an error model that tells us the probability of a query string given the intended query. With these two models and [Bayes’ theorem](https://en.wikipedia.org/wiki/Bayes%27_theorem), we can score candidate spelling correction candidates and rank them based on their probability.

**Building a Language Model**

The language model estimates the probability of an intended query — that is, the probability, given no further information, that a searcher would set out to type a particular query.

Let’s consider the simplifying assumption that all of our queries are single tokens. In that case, we can normalize the historical frequencies of unique queries to establish a probability distribution. Since we have to allow for the possibility of seeing a query for the first time, we need smoothing (e.g, [Good-Turing](https://en.wikipedia.org/wiki/Good%E2%80%93Turing_frequency_estimation)) to avoid assigning it a probability of zero. We can also combine token frequency in the query logs with token frequency in the corpus to determine our prior probabilities, but it’s important not to let the corpus frequencies drown out the query logs that demonstrate actual searcher intent.

This approach breaks down when we try to model the probability of multiple-token queries. We run into two problems. The first is scale: the number of token sequences for which we need to compute and store probabilities grows exponentially in the query length. The second is sparsity: as queries get longer, we are less able to accurately estimate their low probabilities from historical data. Eventually we find that most long token sequences have never been seen before.

The solution to both problems is to rely on the frequencies of n-gram frequencies for small values of n (e.g. unigrams, bigrams, and trigrams). For larger values of n, we can use backoff or interpolation. For more details, read this [book chapter on n-grams by Daniel Jurafsky and James Martin](https://web.stanford.edu/~jurafsky/slp3/3.pdf).

**Building an Error Model**

The error model estimates the probability of a particular misspelling, given an intended query. You may be wondering why we’re computing the probability in this direction, when our ultimate goal is the reverse — namely, to score candidate queries given a possible misspelling. But as we’ll see, Bayes’ theorem allows us to combine the language model and the error model to achieve this goal.

Spelling mistakes represent a set of one or more errors. These are the most common types of spelling errors, also called [edits](https://en.wikipedia.org/wiki/Edit_distance):

* **Insertion.** Adding an extra letter, e.g.*,* *truely*. An important special case is a repeated letter, e.g., *pavillion*.
* **Deletion.** Missing a letter, e.g., *chauffer*. An important special case is missing a repeated letter, e.g., *begining*.
* **Substitution.** Substituting one letter for another, e.g., *appearence*. The most common substitutions are incorrect vowels.
* **Transposition.** Swapping consecutive letters, e.g. *acheive*.

We generally model spelling mistakes using a [noisy channel model](https://en.wikipedia.org/wiki/Noisy_channel_model) that estimates the probability of a sequence of errors, given a particular query. We can tune such a model heuristically, or we can train a machine-learned model from a collection of example spelling mistakes.

Note that the error model depends on the characteristics of searchers, and particularly on how they access the search engine. In particular, people make different (and more frequent) mistakes on smaller mobile keyboards than on larger laptop keyboards.

**Candidate Generation**

Candidate generation is analogous to document retrieval: it’s how we obtain a tractable set of spelling correction candidates that we then score and rank.

Just as document retrieval leverages the inverted index, candidate generation leverages the spelling correction index to obtain a set of candidates that is hopefully includes the best correction, if there is one.

To get an idea of how candidate generation works, consider how you might retrieval all tokens within an edit distance of 1 of the misspelled query *retreival*. A token within edit distance must end with *etreival*, or start with *r* and end with *treival*, or start with *re* and end with *reival*, or start with *ret* and end with *eival*, etc. Using a substring index, you could retrieve all of these candidates with an OR of ANDs.

That’s not the most efficient or general algorithm for candidate generation, but hopefully it gives you an idea of how such algorithms work.

The cost of retrieval depends on the aggressivity of correction, which is roughly the maximum edit distance — that is, the number of edits that can be compounded in a single mistake. The set of candidates grows exponentially with edit distance. The probability of a candidate decreases with its edit distance, so the cost of more aggressive candidate generation yields diminishing returns.

**Scoring**

Hopefully the right spelling correction is among the generated candidates. But how do we pick the best candidate? And how do we determine whether the query was misspelled in the first place?

For each candidate, we have its prior probability from the language model. We can use the error model to compute the probability of the query, given the candidate. So now we apply Bayes’ theorem to obtain the conditional probability of the candidate, given the query:

Prob (candidate | query) ∝ Prob (query | candidate) \* Prob (candidate)

We use the proportionality symbol (∝) here instead of equality because we’ve left out the denominator, which is the a priori probability of the query. This denominator doesn’t change the relative scores of candidates.

In general, we go with the top-scoring candidate, which may be the query itself. We use the probability to establish our confidence in the candidate.

**Presenting Suggestions**

Deciding how to present suggested spelling corrections may not be an algorithmic problem, but it’s a critical part of the search experience.

The key factors are whether the top-ranked candidate has a high probability, and whether that candidate is the original query:

* If the top candidate is the original query and has a high probability, then do nothing — your system believes the query is already spelled correctly.
* If the top candidate is not the original query and has a high probability, then automatically rewrite the query and notify the searcher with a prominent message above the search results. Include a link that allows the searcher to see results for the original query.
* If the top candidate is not the original query but does not have a high probability, then show results for the original query but propose the alternative as a “did you mean”. Consider the same approach when the top candidate is the original query but the next candidate has almost as high a probability.

Finally, you shouldn’t rewrite a query into one that returns no results, regardless of the probability. Converse, there isn’t as much risk in correcting a query that would otherwise return no results.

**Conclusion**

Hopefully you now understand how spelling correction systems work — congratulations!

Again, that doesn’t mean you should try to write your own. As you hopefully appreciate by now, spelling correction systems are complex beasts, dependent on robust language and error models, as well as trade-offs to optimize their effectiveness and efficiency. Knowing the internals will help you use and customize best-of-breed, off-the-shelf tools.

Finally, remember that the quality of spelling correction is one of the most important attributes of the search experience. Invest accordingly, and make your searchers happy.

**Previous:** [**Tokenization**](/tokenization-c8cdd6aef7ff#.syx2pp8lm)

**Next:** [**Stemming and Lemmatization**](/stemming-and-lemmatization-6c086742fe45#.507m8gm6e)