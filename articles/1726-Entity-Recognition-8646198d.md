---
title: 'Entity Recognition'
company: Tunkelang
tag: 查询理解
date: 2017-08-30
url: https://queryunderstanding.com/entity-recognition-763cae840a20
account: 
origin: harvest3-202607
---
# Entity Recognition

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--763cae840a20---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--763cae840a20---------------------------------------)

3 min read

·

May 30, 2017

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D763cae840a20&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fentity-recognition-763cae840a20&source=---header_actions--763cae840a20---------------------post_audio_button------------------)

Share

In the previous post on [query scoping](/query-scoping-ed61b5ec8753), we discussed query tagging as a special case of [named-entity recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) (NER). In this post, we’ll dive a little bit deeper into the topic of entity recognition.

**Entities**

Entity recognition presumes that we know what kind of entities we’re trying to recognize. But defining what constitutes an entity is tricky. At a high level, we can distinguish between named entities and terms.

**Named Entities**

Named entities have two distinguishing features. First, they have names — that is, they are [proper nouns](https://en.wikipedia.org/wiki/Proper_noun). In English, that means they’re usually capitalized. Second, they have types, such as person, place, or organization. A named entity is a specific, named instance of a particular entity type.

The specificity of named entities makes recognizing them useful for both query understanding and document understanding. In addition, named entities often have relationships with one another, comprising a [semantic network](https://en.wikipedia.org/wiki/Proper_noun) or knowledge graph. For example, [Sundar Pichai](https://en.wikipedia.org/wiki/Sundar_Pichai) is the CEO of Google, which is located in Mountain View. Query rewriting can use these relationships among entities to improve both precision through disambiguation and recall through expansion.

Named-entity recognizers can be rule-based (e.g., using a collection of [regular expressions](https://nlp.stanford.edu/software/regexner.html)) or machine-learned. Rule-based recognizers are simple and understandable, but it’s hard to achieve good accuracy without machine learning. As discussed in the previous post, training a machine-learned named-entity recognizer requires a collection of segmented, labeled queries.

One subtlety we did not address in that post is that recognizing an entity type is not the same as identifying a specific entity. For example, recognizing that *sundar pichai* is a person is not the same as recognizing that he’s the specific person who is the CEO of Google. Many named-entity recognizers, such as do not perform this further task of entity identification.

Entity identification requires that the training data labels be those specific entities, rather than their generic entity types. Entity identification plays a critical role for domains like social networking and media, but building it requires significant data assets, as well as investment to maintain them.

**Terms**

In contrast, terms generally have neither names nor types. Terms are simply words or phrases — usually [noun phrases](https://en.wikipedia.org/wiki/Noun_phrase) — that carry a distinctive amount of meaning, particularly in the context of an application domain. If the corpus were a book, then terms are what you’d expect to find in its [glossary](https://en.wikipedia.org/wiki/Glossary). A rule of thumb is that terms have [Wikipedia](https://www.wikipedia.org/) entries. Conversely, Wikipedia strives to be a universal glossary.

What terms lack in structure and specificity, they make up for in generality. The terms in a document carry most of the document’s meaning. We can think of the list of terms as a document summary, particularly for the purpose of search indexing. Similarly, terms represent the most important [query segments](/query-segmentation-2cf860ade503).

[Terminology extraction](https://en.wikipedia.org/wiki/Terminology_extraction) algorithms typically identify noun phrases in a corpus using [part-of-speech tagging](https://en.wikipedia.org/wiki/Part-of-speech_tagging), and then select terms from those noun phrases based on frequency and other statistical measures that reflect specificity and distinctiveness. While it’s challenging to build a knowledge graph on top of unstructured terms, it’s possible to relate terms to one another through [text mining](https://en.wikipedia.org/wiki/Text_mining) algorithms, or using the techniques described in the earlier post on [query expansion](/query-expansion-2d68d47cf9c8).

Because terms lack structure, it’s hard to do much more than string matching for term recognition. In particular, it’s difficult to disambiguate words or phrases. We may be able to do so in the context of a document, but it’s hard to do so for short queries.

**Leveraging Entity Recognition**

Entity recognition focuses both query understanding and document understanding on the most salient words and phrases. As such, it can be the lynchpin of a query rewriting strategy — from precision-increasing query scoping to recall-increasing expansion and relaxation.

Entity recognition is what elevates search from strings to things. It take a lots of work to implement robust entity recognition, but doing so dramatically simplifies the rest of the information retrieval problem.

**Previous:** [**Query Scoping**](/query-scoping-ed61b5ec8753)

**Next:** [**Taxonomies and Ontologies**](/taxonomies-and-ontologies-8e4812a79cb2)