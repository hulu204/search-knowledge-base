---
title: 'Word2Vec\xa0Model\xa0To\xa0Generate\xa0Synonyms on the Fly in Apache Lucene\xa0– W2V Algorithm'
company: Sease
tag: 查询理解
date: 2023-06-28
url: https://sease.io/2023/06/word2vec-model-to-generate-synonyms-on-the-fly-in-apache-lucene-w2v-algorithm.html
account: 
origin: harvest3-202607
---
This blog post series aims to explore our contribution to Apache Lucene, which integrates a Word2Vec model with the text analysis pipeline to generate synonyms based on the values stored in the indexed document fields.

In the [first blog post](https://sease.io/2023/04/word2vec-model-to-generate-synonyms-on-the-fly-in-apache-lucene-introduction.html), we introduced the synonym expansion technique and described what is the state of the art to expand your query/documents with synonyms in Apache Lucene and Solr, highlighting limitations and possible solutions.

Before talking about our contribution, let’s introduce the Word2Vec algorithm theory and what our implementation of Word2Vec was.

## Word Embedding

One of the most popular and efficient techniques to learn word embeddings is **Word2Vec** (W2V), open-sourced in 2013.

> In natural language processing (NLP), word embedding is a term used for the representation of words for text analysis, typically in the form of a real-valued vector that encodes the meaning of the word such that the words that are closer in the vector space are expected to be similar in meaning. – Wikipedia

W2V takes a text in input and outputs a series of vector representations for each word in the text corpus, called ***neural word embedding***, representing a word with numbers.

The main idea behind W2V is the **Distributional Hypothesis**, which means that words that appear in the same circumstances tend to have similar meanings, so we can derive the meaning of a word when we look at how it’s used in relation to the other words; consequently, the model will define these words as similar and they will be identified with dense vectors close together (in the vector space), typically vectors of length between 100 and 300. The dimension is abstract and the vectors make sense only in relation to the other vectors.

The vector space allows mathematical operations to measure the relationships between vectors and we can calculate the *nearest neighbors* to get the semantic relatedness of words that are close in the space. So to find similar words, we need to look at the distance between their vectors.

One of the standard measures is **[Cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity)**; it is defined as the cosine of the angle between two vectors (sequences of numbers) and does not depend on the magnitudes of the vectors but on their direction/orientation:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-08-11-alle-08.16.36.png?fit=800%2C541&ssl=1)

Therefore, once we get the vectors, in order to extract synonyms for a word, we have to query the model to retrieve the vectors with the highest **cosine similarity** with the vector corresponding to the word whose synonyms we are looking for.

## Word2Vec algorithm

Word2Vec is *unsupervised learning*, a machine learning technique that analyzes and clusters unlabeled data to uncover patterns and hidden information.

It is one of the most basic types of Neural network, named **Feed-forward**, in which information flows from the input layer to the output layer without any loops:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-08-22-alle-13.30.08.png?fit=800%2C614&ssl=1)

The input layer has a size equal to the vocabulary length (i.e. number of words) and each input word has to be encoded using the **one-hot method**.

[One-hot encoding](https://machinelearningmastery.com/why-one-hot-encode-data-in-machine-learning/), in machine learning, is a general method to vectorize any categorical feature. For simplicity, if you have a vocabulary of 10 words, each word will be represented by a vector of length 10 that contains 9 zeros and 1 one at the position of the word you are considering:

```
				
					Example
One-hot vector of the second word in a vocalubary:      [0 1 0 0 0 0 0 0 0 0]
One-hot vector of the penultimate word in a vocalubary: [0 0 0 0 0 0 0 0 1 0]
				
			
```

The hidden layer is only one, that’s why it is called **Shallow** and not a deep neural network.

The number of neurons in the hidden layer is equal to the desired size of the word embedding, chosen via a hyperparameter (*layerSize*).

The output layer is simply a softmax activation function that outputs probabilities for the target words from the vocabulary.

The model training is typically done by predicting the next word given a sequence of words. There are variants where you want to predict context words (as W2V) or masked words. After the training, the word embeddings are obtained from the **weight matrix**, so hidden weights are used as word embeddings.

There are a lot of parameters to adjust when you train a neural network, but in the case of word2vec, you need to set up also specific parameters that are:

* + **windowSize**: represents how many words before and after a given word to include as context words of the given word

* + **layerSize**: is the number of neurons in the hidden layer that is equal to the desired dimensionality of the resulting word embeddings

* + **elementsLearningAlgorithm**: represents the algorithm to use. In fact, there are 2 different architectures you can choose: **CBOW** or **Skip-Gram**

## our talk at berlin buzzwords 2022

Check out the talk about this project at Berlin Buzzwords 2022

[See the full talk](https://sease.io/2022/05/sease-at-berlin-buzzwords-2022.html)

## Continuous Bag Of Words (CBOW) and Skip-Gram algorithm

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-08-02-alle-16.11.47.png?fit=800%2C434&ssl=1)

Word2Vec available architectures: CBOW example (right) and *Skip Gram*example (left)

These models are algorithmically similar but one does the opposite of the other.

In the **CBOW** model, the distributed representations of the context (or surrounding words) are combined to **predict the target word.**

While in the **Skip-gram** model, the distributed representation of the input word is used to **predict the context**.

Thus, we get a distributional representation for each word in the corpus, in contrast to count-based approaches.

###### What's the context? How can we define the surrounding words?

For each sentence, Word2Vec works by reading all words in a sliding window of N words, where N is chosen via the ***windowSize***; indeed, this hyperparameter is very important since it defines the number of words to be considered as the *context*.

Let’s take a look at the **Skip-gram** model to show you an example:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-08-02-alle-14.36.27.png?fit=800%2C535&ssl=1)

*Context of the phrase* *with a window of 2 words*, *Skip Gram example*

Given a **windowSize of 2** (for simplicity), W2V will pick two words behind and the two words after a target word. If you have long sentences in the text, it may be required a wider window for the training.

Considering the third row of the simple example above:

* The **target word** is *chased*
* The **context** words are *(the, cat, the, mouse)*

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/Schermata-2022-08-22-alle-14.15.30.png?fit=800%2C319&ssl=1)

The neural network receives **word-context pairs** that are trained individually and will be: (*chased*, the), (*chased*, cat), (*chased*, the), (*chased*, mouse).

the, cat, the, mouse will be treated in the same way while training since within the sample window, the proximity of a word to the target word does not matter.

## Word2Vec implementation

For the Word2Vec implementation, we used the [**Deeplearning4J** library](https://deeplearning4j.konduit.ai/deeplearning4j/reference/word2vec-glove-doc2vec) (DL4J), which appears to be the best choice for a native Java library for deep learning.

It is an open source library that has a good developer community. It is written in Java, but also includes application programming interfaces for other languages. It is also integrated with Hadoop and Apache Spark.

It has an out-of-the-box implementation of Word2Vec, based on the Skip-Gram algorithm, which makes it easy to create something really fast from scratch. You just need to set up the parameters for the W2V configuration and pass the input, which is the text indexed by the search engine.

##### DL4J Word2Vec Model Output

Once the model is trained, you need to save it in order to use it.

The W2V implementation of DL4J will produce a zip which is a folder containing several files including a text file called **syn0**; this is nothing but a dictionary in which each token (**B64 encoded**) has a vector attached to it, as we can see here:

```
				
					B64:cGl6emE= 0.06251079589128494  -0.9980443120002747
B64:ZQ== 0.5112091898918152  -0.8594563603401184
B64:aWw= 0.5138685703277588  -0.8578689694404602
B64:bGE= 0.4818926453590393  -0.8762302398681641
B64:aQ== 0.9747347831726074  -0.22336536645889282
B64:ZGVsbGE= 0.3850429654121399 -0.9228987097740173
B64:cGVy 0.964830219745636  -0.26287391781806946
…
…
				
			
```

***cGl6emE=** : is the encoded B64 token (corresponds to the Italian word “pizza”)*

***0.06251079589128494 -0.9980443120002747** : is the vector*

In the above **syn0.txt** file, we have just given a very simple example to show you what the output looks like.

For simplicity, the vector dimension is 2, but in reality, this is not enough to capture sufficient information; indeed, the default value for the dimensionality of the vectors is set to 100.

## What's next?

It’s finally time to explore our open source contribution to Apache Lucene. The next blog post is the most important, so it’s unmissable. Take a look at this blog post about [Word2Vec Model To Generate Synonyms – Performance Testing](https://sease.io/2023/08/word2vec-model-to-generate-synonyms-performance-tests.html)

See you and thank you for reading!

## Need Help with this topic?​

If you want to know more about this project, send us an e-mail!

[Click Here](mailto:info@sease.io)