---
title: 'Word2Vec Model To Generate Synonyms on the Fly in Apache Lucene – Introduction'
company: Sease
tag: 查询理解
date: 2023-04-06
url: https://sease.io/2023/04/word2vec-model-to-generate-synonyms-on-the-fly-in-apache-lucene-introduction.html
account: 
origin: harvest3-202607
---
This blog post series aims to explore our contribution to Apache Lucene, which integrates a Word2Vec model with the text analysis pipeline to generate synonyms based on the values stored in the indexed document fields.

Let’s start with the introductory part where we will briefly introduce the synonym expansion technique; then we will talk about what is the state of the art to expand your query/documents with synonyms in Apache Lucene and Solr, and finally, we will highlight what the resulting limitations are from the current approach and what is the solution we propose.

## Synonym Expansion

##### How and why synonyms are used in Search?

When executing a query, the terms generated at indexing time need to match those of the query: this matching allows a document to be found and then appear in the search results list.

For example, given the sentence *“best places for a walk in the mountains”*, we know that “a walk” could be also expressed using different terms like “hiking” or “trekking”; if the document’s text has been indexed using “hike” but the user queries and enters “a walk”, it is likely that the document will not be retrieved(**[Vocabulary Mismatch Problem](https://en.wikipedia.org/wiki/Vocabulary_mismatch)**). That’s the main reason why it is needful to make the search engine aware of synonyms.

In Information retrieval, **synonyms** (words with the same or a very close meaning) are used to decorate text to expand the number of potential ways a query or piece of indexed document is expressed.

Therefore **Synonym Expansion** is a technique that allows you to enrich document keywords by adding their synonyms, if they exist, at the same position, in order to raise the probability of finding more matching between query terms and inverted index ones and improve the**RECALL**:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Recall-formula.png?fit=800%2C154&ssl=1)

The recall is a number between 0 and 1, equal to the number of relevant documents that are retrieved divided by the number of all relevant documents; if none of the retrieved documents is relevant, the recall is 0, while a good system has a recall close to 1.

## State-of-the-Art

The state-of-the-art in Apache Lucene and Solr is the **Vocabulary-based Synonym Expansion**.

###### Synonym Graph Filter

The current way to implement a search engine with synonym expansion is based on adding in the Solr **‘conf’** folder a dictionary in which all words are mapped with their synonyms.

Apache Solr allows users to add a static list of synonyms by configuring the [SynonymGraphFilterFactory](https://solr.apache.org/guide/8_9/filter-descriptions.html#synonym-graph-filter) as you can see in the following example:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-07-26-alle-12.01.40.png?fit=800%2C219&ssl=1)

The list of synonyms, comma-separated, is written into a simple text file, and then you just let the **Synonym Graph Filter** read them from there.

The *synonyms.txt* file can be formatted in multiple ways (see the [documentation](https://solr.apache.org/guide/6_6/filter-descriptions.html#FilterDescriptions-SynonymGraphFilter) for further details); here is an example:

```
				
					couch,sofa,divan 
teh =&gt; the 
huge,ginormous,humungous =&gt; large
small =&gt; tiny,teeny,weeny 
...
				
			
```

The advantage is that you can update the synonyms file as needed without having to change the code.

You can manually create the synonyms file or download a synonym vocabulary using the [**WordNet** project](https://wordnet.princeton.edu/) and include it in your indexing text analysis pipeline. It provides a large, high-quality lexical synonyms database which is constantly updated by Princeton University and should work well for the English language.

###### Synonym Graph Filter + Delimited Boost Filter

In 2020, our Sease director [Alessandro Benedetti](https://sease.io/alessandro-benedetti) contributed to Lucene, extending this feature and introducing the **Delimited Boost Filter**.

It has given the ability to associate a different numerical weight to each synonym, to be able to boost the ones that are closer to the original concept and more important for your domain.

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-07-26-alle-13.00.53.png?fit=800%2C216&ssl=1)

Here is an example of the *boostedSynonyms.txt* file, where each synonym has the associated boost:

```
				
					leopard, big cat|0.8, bagheera|0.9, panthera pardus|0.85 
lion =&gt; panthera leo|0.9, simba|0.8, kimba|0.75 
...
				
			
```

If you are curious about that, everything is detailed and described in a specific blog post about [Weighted Synonyms in Apache Lucene/Solr .](https://sease.io/2020/03/introducing-weighted-synonyms-in-apache-lucene.html)

## Limits

There are still some weaknesses arising from these approaches and that’s why we have proposed and implemented a new method for generating a context-based list of synonyms.

The main limits concern:

##### DOMAIN

The term “daemon” in the domain of operating system articles is not a synonym of “devil” but it’s closer to the term “process”.

As we can deduce from the previous sentence, dictionaries may not necessarily match your **contextual domain**, as the synonym mappings are static and are not tied to indexed data. This makes it difficult to find items with similar meanings but containing different keywords.

##### LANGUAGE

Unless you don’t generate it manually, the list of synonyms is not always available for each language; indeed, it doesn’t exist a WordNet-type resource for every language.

##### MAINTENANCE

Dictionaries are likely to change over time, so they require additional care and costs for maintenance.

##### CONTEXT

Human language is highly ambiguous and context-dependent; the vocabulary-based synonym expansion is based only and exclusively on the rigorous syntax of a language (*denotation*) without taking into consideration the context in which a word appears (*connotation*); what we mean is that in real life (informal contexts) people may tend to use words that aren’t synonyms as if they were, therefore expanding synonyms based only on the grammar rules is very restrictive.

How can we solve these limits using Machine Learning?

**Using a Word2vec neural network to generate synonyms on the fly!**

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-07-31-alle-15.02.44.png?fit=800%2C599&ssl=1)

*Synonym expansion (search time) using word2vec. (Teofili, T., & Mattmann, C. A. (2019). Deep learning for search. Shelter Island, NY: Manning Publications Co.*)

Special thanks to the author of the book “[Deep Learning for Search](https://livebook.manning.com/book/deep-learning-for-search/about-this-book/)“, Tommaso Teofili, for inspiring us in this contribution; the chapter on the generation of synonyms is the second and is very well written.

## Advantages of our proposal

* A search engine that can use a neural network to precisely generate synonyms from the ingested data rather than manually building or downloading a synonyms vocabulary will help match search terms to text in an inverted index and avoid missing relevant search results.

* This approach is **language agnostic**, so we don’t care too much about what language is used and whether it’s informal or not.

* Since the main concept is to look at the context of the word and analyze the patterns of its nearest neighbors, there is **no need to involve any grammatical or syntactic rules**.

## What’s next?

Before exploring in detail our contribution, we would like to give you a brief overview of the Word2Vec algorithm, so don’t miss the next blog post.

See you and thank you for reading!

## Need Help with this topic?​

If you want to have a deep understanding of this topic, take a look at our talk at Berlin Buzzwords 2022!

[Click Here](https://sease.io/2022/05/sease-at-berlin-buzzwords-2022.html)