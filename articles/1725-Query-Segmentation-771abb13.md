---
title: 'Query Segmentation'
company: Tunkelang
tag: 查询理解
date: 2017-05-16
url: https://queryunderstanding.com/query-segmentation-2cf860ade503
account: 
origin: harvest3-202607
---
# Query Segmentation

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--2cf860ade503---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--2cf860ade503---------------------------------------)

4 min read

·

Apr 28, 2017

--

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D2cf860ade503&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-segmentation-2cf860ade503&source=---header_actions--2cf860ade503---------------------post_audio_button------------------)

Share

The previous two posts focused on using query rewriting to increase [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall). We can also use query rewriting to increase [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision) — that is, to reduce the number of irrelevant results. While increasing recall helps us avoid small or empty result sets, increasing precision helps us avoid large result sets that are full of noise.

In this post, we’ll discuss the first of two query rewriting strategies used to increase precision: query segmentation. We’ll first talk about how to perform query segmentation, and then about how to use query segmentation to increase precision through query rewriting.

**Semantic Units**

Query segmentation attempts to divide the search query into a sequence of [semantic](https://en.wikipedia.org/wiki/Semantics) units, each of which consists of one or more tokens. For a single-token query like *machine*, there’s only one possible segmentation. Multiple-token queries, like *machine learning framework*, admit multiple possible segmentations, such as “[*machine learning*](https://en.wikipedia.org/wiki/Machine_learning)*” framework* and *machine “*[*learning framework*](https://en.wikipedia.org/wiki/Curriculum_framework)*”*. In theory, the number of possible segmentations for a query grows exponentially with the number of tokens; in practice, there are only a handful of plausible segmentations.

The goal of query segmentation is to identify the query’s semantic units. In our *machine learning framework* example it’s clear that the correct segmentation is *“machine learning” framework* — that is, the searcher is interested in frameworks for machine learning, rather than something to do with machines and learning frameworks. Identifying this segmentation is critical to understanding the query and thus returning precise matches.

So how do we automatically identify the correct segmentation?

**Dictionary Approach**

The simplest approach is to obtain a dictionary of phrases appropriate to the application domain, and then to automatically treat the phrases as segments when they occur in queries. For example, a search engine for computer science articles could use a dictionary of common terms from that domain. Hopefully such a dictionary would include the term *machine learning*.

A dictionary-based approach requires a mechanism to resolve overlapping phrases, e.g., to segment the query *machine learning* *framework* if the dictionary includes both *machine learning* and *learning framework*. To keep things simple, we can associate each phrase with a score — such as its observed frequency in a subject-specific corpus — and favor the phrase with the highest score when there’s overlap.

Such a strategy tends to work reasonably well, but it can’t take advantage of query context. We’ll return to this point in a moment.

**Statistical Approach**

If we can’t buy or borrow a dictionary, we can create one from a document corpus. We analyze the corpus to find [collocations](https://en.wikipedia.org/wiki/Collocation) — that is, sequences of words that co-occur more often than would be expected by chance.

We can make this determination using statistical measures like [mutual information](https://en.wikipedia.org/wiki/Mutual_information), [t-test scores](https://en.wikipedia.org/wiki/Student%27s_t-test), or [log-likelihood](https://en.wikipedia.org/wiki/Log-likelihood). It’s also possible to obtain collocations using [Word2vec](https://papers.nips.cc/paper/5021-distributed-representations-of-words-and-phrases-and-their-compositionality.pdf).

Once we have a list of collocations and associated scores, we can create a dictionary by keeping the collocations with scores above a threshold. Choosing the threshold is a trade-off between precision and coverage. We can also review the list manually to remove false positives.

**Supervised Machine Learning**

A more sophisticated approach to query segmentation is to model it as a supervised machine learning problem.

Query segmentation is a binary classification problem at the token level. For each token, we need to decide whether it continues the current segment or begins a new one. Given a collection of correctly segmented queries, we can train a binary classifier to perform query segmentation.

As with all machine learning, our success depends on how we represent the examples as feature vectors. Features could include token frequencies, mutual information for bigrams, part-of-speech tags, etc. Bear in mind that some features are more expensive to compute than others. Slow computation may be an acceptable expense or inconvenience for training, but it can be a show-stopper if it noticeably slows down query processing.

A supervised machine learning approach is more robust than one based on a dictionary, since it can represent context in the feature vector. But it’s a more complex and expensive to implement. It’s probably better to start with a simple approach and only invest further if the results aren’t good enough.

**Using Query Segmentation for Query Rewriting**

Now that we’ve obtained a query segmentation, what do we do with it? We rewrite the query to improve precision!

A straightforward approach is to auto-phrase segments — that is, to treat them as if they were quoted phrases. Returning to our example, we’d rewrite *machine learning framework* as *“machine learning” framework*, filtering out results that contain the tokens *machine* and *learning* but not as a phrase. The approach certainly increases precision, but it can be so drastic as to lead to no results. For this reason, many search engines boost phrase matches but don’t require them.

A more nuanced approach is to couple auto-phrasing with query expansion approaches like [stemming, lemmatization](/stemming-and-lemmatization-6c086742fe45#.2qz7j1set), and [synonym expansion](/query-expansion-2d68d47cf9c8). Continuing with our example, *machine learning framework* could include results that match *“machine learned” framework* or *“machine learning” infrastructure*. This approach can achieve strong precision and recall.

Finally, if we’re using [query relaxation](/query-relaxation-342bc37ad425), it’s important for relaxation to respect query segmentation by not breaking up segments.

**Summary**

Searchers use multiple-word phrases intuitively and are unpleasantly surprised when search engines fail to recognize those phrases. If a significant number of searchers are quoting phrases in their queries, you’re doing it wrong. If you can only invest in two areas of query understanding, I recommend that you prioritize [spelling correction](/spelling-correction-471f71b19880) and query segmentation.

**Previous:** [**Query Relaxation**](/query-relaxation-342bc37ad425)

**Next:** [**Query Scoping**](/query-scoping-ed61b5ec8753)