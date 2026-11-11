---
title: 'Query Scoping'
company: Tunkelang
tag: 查询理解
date: 2017-08-30
url: https://queryunderstanding.com/query-scoping-ed61b5ec8753
account: 
origin: harvest3-202607
---
# **Query Scoping**

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--ed61b5ec8753---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--ed61b5ec8753---------------------------------------)

4 min read

·

May 16, 2017

--

2

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Ded61b5ec8753&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fquery-scoping-ed61b5ec8753&source=---header_actions--ed61b5ec8753---------------------post_audio_button------------------)

Share

In the previous post, we discussed how [query segmentation](/query-segmentation-2cf860ade503) improves precision by grouping query words into semantic units. In this post, we’ll discuss query scoping, another query rewriting technique that improves precision by matching each query segment to the right attribute.

**Leveraging Structure**

Documents or products often have an explicit structure that mirrors how people search for them.

For example, if you search for *black michael kors dress* on a site that sells clothing, you intend black as a color, Michael Kors as a brand, and dress as a category.

Similarly, if you search for *microsoft ceo* on LinkedIn, you’re looking for Microsoft as an employer and CEO as a job title.

Query scoping rewrites queries to take advantage of this structure.

**Query Tagging**

Query scoping begins with query tagging. Query tagging maps each query segment to the intended corpus attribute. It’s a machine learning problem — specifically, a non-binary classification problem. In the information retrieval literature, query tagging is a special case of [named-entity recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) (NER), which can be applied to arbitrary text documents.

In our clothing example, the attributes include category, brand, and color. LinkedIn’s attributes include person name, company name, and job title. In general, attributes are specific to the domain and corpus.

Ideally, document structure is explicitly represented in the search index. If not, we may be able to extract document structure through algorithms for document understanding, also known as [information extraction](https://en.wikipedia.org/wiki/Information_extraction).

Regardless of how we obtain document structure, we need to establish the corpus attributes in advance. Query tagging is a supervised machine learning problem, which means that we can’t map query segments to attributes we didn’t anticipate. At best, we can label those segments as “unknown” because the classifier isn’t able to pick an attribute for them.

**Training Data**

We generate training data for query tagging from a representative set of segmented, labeled queries. For example, our training data could include examples like (*black*, *michael kors*, *dress*) -> (*Color*, *Brand*, *Category*).

Obtaining a representative set of queries from search logs is straightforward for a search application that’s already in production. To train a query tagger for a new search application, we’ll need to be more creative, either synthesizing a set of queries or borrowing a search log from a similar application. It may be easier to launch a search application without tagging, and then train a tagger after we’ve collected a critical mass of search traffic.

Let’s assume that we already have a query segmentation algorithm, as discussed in the previous post, and that we’ve applied it to our set of queries. Query tagging assumes — and thus requires — query segmentation.

We then need to label the query segments. We can use human labelers, but this process is slow and expensive. Human labelers also need to be familiar with the domain in order to provide robust judgements.

A more efficient approach is to obtain labels from our search logs — specifically from clicks on search results. For each click, we look at the query-result pair and label each query segment with the attribute it matches in the results. For example, if we look at a click for the search *black michael kors dress*, we’ll probably find that *black* matches the color attribute, Michael Kors matches the brand attribute, and *dress* matches the category attribute.

This approach works when each segment matches precisely one attribute in the clicked result. If a segment matches multiple attributes, we can exclude the click from our training data, or we can randomly select from the attributes. If a segment doesn’t match an attribute, we label it as “unknown”.

Finally, we have to represent the training examples as feature vectors. We can create features from tokens, [stemmed or lemmatized](/stemming-and-lemmatization-6c086742fe45) tokens, or we can look below the token levels at the characters. If we have additional context about the searcher, we can also incorporate it into the feature vector.

**Building the Model**

Once we have training data, we can use various approaches to build a machine-learned model. A common choice for query tagging is a [conditional random field](https://en.wikipedia.org/wiki/Conditional_random_field) (CRF). The Stanford NLP package provides a [CRF named-entity recognizer](https://nlp.stanford.edu/software/CRF-NER.shtml) that is suitable for query tagging.

It may be tempting to use a cutting-edge approach like [deep learning](http://eric-yuan.me/ner_1/). But bear in mind that more data — and better data — usually beats better algorithms. Robust query tagging relies mostly on robust generation of training data.

**From Tagging to Scoping**

Having tagged each query segment, we rewrite the query to scope the query.

A straightforward approach is to only match each segment against its associated attribute, as if the searcher had done so explicitly using an advanced search interface. This approach tends to optimize for precision, but it can be a bit unforgiving when it comes to recall.

A problem with this literal approach is that some attributes are difficult to distinguish from one another. For example, it’s often difficult to determine whether a query segment in a LinkedIn search matches a skill or part of a job title (e.g., a Developer who knows Java vs. Java Developer). Rather than count our ability to make this distinction, we can ignore it, effectively combining skill and job title into a single attribute.

If we have a [similarity matrix](https://en.wikipedia.org/wiki/Similarity_measure) for our attributes, or we implement the query tagger as a [multiclass classifier](https://en.wikipedia.org/wiki/Multiclass_classification), then we can can use the query tagger to restrict matches to the best attributes for each segment. Determining the number of attributes to match is a precision / recall tradeoff.

Finally, since query scoping is an aggressive way to increase precision, we can combine it with techniques like [query expansion](/query-expansion-2d68d47cf9c8) and [query relaxation](/query-relaxation-342bc37ad425) to increase recall. By requiring query expansion and relaxation to respect query scoping, we can achieve a good balance of precision and recall.

**Summary**

Query scoping is a powerful technique to increase precision by leveraging the explicit structure of the corpus and the implicit structure of queries. It requires more work than most of the other techniques we’ve discussed, but it’s worth it: it’s one of the most effective ways to capture query intent.

**Previous:** [**Query Segmentation**](/query-segmentation-2cf860ade503)

**Next:** [**Entity Recognition**](/entity-recognition-763cae840a20)