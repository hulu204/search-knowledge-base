---
title: 'Lucene Document Classification'
company: Sease
tag: 工程相关
date: 2015-07-02
url: https://sease.io/2015/07/lucene-document-classification.html
account: 
origin: harvest3-202607
---
## Introduction to Lucene Document Classification

This blog post describes the approach used in the Lucene Classification module to adapt text classification to document (multi-field) classification.

Machine Learning and Search have been always strictly associated.  
Machine Learning can help to improve the Search Experience in a lot of ways, extracting more information from the corpus of documents, auto-classifying them and clustering them.  
On the other hand, Search-related data structures are quite similar in content to the ML models used to solve the problems, so we can use them to build up our algorithms.  
But let’s go in order…  
In this article, we are going to explore how much Auto Classification can be important to ease the user experience in Search, and how it will be possible to have an easy, out of the box painless classification directly from Lucene, from our already existent Index, without any external dependency or trained model.

## Classification

From Wikipedia :

In **machine learning** and **statistics**, **classification**is the problem of identifying to which of a set of categories (sub-populations) a new **observation**belongs, on the basis of a **training set** of data containing observations (or instances) whose category membership is known. An example would be assigning a given email into “**spam**” or “**non-spam**“ classes or assigning a diagnosis to a given patient as described by observed characteristics of the patient (gender, blood pressure, presence or absence of certain symptoms, etc.).

Classification is a well-known problem, and it is really easy to verify the utility of classifiers daily.  
When dealing with Search Engines, it is so common that our Documents have a category ( generally assigned by a human ). Wouldn’t be useful to be able to automatically extract the category for the documents that are missing it? Wouldn’t be interesting to automate that processing step to have documents automatically categorised, based on the experience (which means using all the documents already categorised in our Search System)  
Wouldn’t be amazing to do that without any external tools and without any additional expensive model training activity?  
We already have a lot of information in our Search System, let’s use it!

## Lucene Classification Module

To be able to provide a Classification capability, our system generally needs a trained model.  
Classification is a problem solved by **Supervised Machine learning algorithms** which means humans need to provide a training set.  
A classification training set is a set of documents, manually tagged with the correct class.  
It is the “experience” that the Classification system will use to classify upcoming unseen documents.  
Building a trained model is expensive and requires to be stored in specific data structures.  
Is it really necessary to build an externally trained model when we already have in our index millions of documents, already classified by humans and ready to be searched?  
A Lucene index has already really interesting data structures that relate terms to documents ([Inverted Index](https://sease.io/2015/07/exploring-solr-internals-lucene.html)), fields to terms (Term Vectors) and all the information we need about Term Frequency and Document Frequency.  
A corpus of documents, already tagged with the proper class in a specific field, can be a really useful resource to build our classification **inside our search engine** without any external tool or data structure**.**  
Based on these observations, the Apache Lucene [[1]](https://lucene.apache.org/core/) Open Source project **introduced version 4.2  a document classification** module to manage the text classification using the Index data structures.  
The facade for this module is the text Classifier, a simple interface ( with 3 implementations available ) :

public interface Classifier {/\*\* \* Assign a class (with score) to the given text String \*  
\* @param text a String containing text to be classified \*  
@return a {@link ClassificationResult} holding assigned class of type T and score \*

ClassificationResult assignClass(String text) throws IOException;

/\*\* \* Get all the classes (sorted by score, descending) assigned to the given text String.  
@param text a String containing text to be classified \*  
@return the whole list of {@link ClassificationResult}, the classes and scores. Returns null if the classifier can’t make lists. \*/

List getClasses(String text) throws IOException;

/\*\* \* Get the first max classes (sorted by score, descending) assigned to the given text String.  
@param text a String containing text to be classified \*  
@param max the number of return list elements \*  
@return the whole list of {@link ClassificationResult}, the classes and scores. Cut for “max” number of elements. Returns null if the classifier can’t make lists. \*/

List getClasses(String text, int max) throws IOException;  
}

The available implementations are :

* **KNearestNeighborClassifier** – A k-Nearest Neighbor classifier [[2]](https://en.wikipedia.org/wiki/K-nearest_neighbors)) based on MoreLikeThis

* **SimpleNaiveBayesClassifier** – A simplistic Lucene based NaiveBayes [[3]](https://en.wikipedia.org/wiki/Naive_Bayes_classifier) classifier

* **BooleanPerceptronClassifier** – A perceptron [[4]](https://en.wikipedia.org/wiki/Perceptron) based Boolean Classifier. The weights are calculated using TermsEnum.totalTermFreq both on a per field and a per document basis and then a corresponding FST is used for class assignment.

Let’s see the first 2 in details :

### KNearestNeighborClassifier

This classifier is based on the Lucene More Like This [[5]](https://solr.apache.org/guide/6_6/morelikethis.html).

This is a feature able to retrieve similar documents to a seed one (or a seed text) calculating the similarity between the docs on a field base.

It takes into input the list of fields to take into consideration (with a relative boost factor to increase the importance of some fields over others).

The idea behind this algorithm is simple :

– given a set of relevant fields for our classification

– given a field containing the class of the document

It retrieves all the similar documents to the Text in input using the MLT.

Only the documents with the class field valorised, are taken into consideration.

The **top k documents** in the result are evaluated, and the class is extracted from all of them.

Then a ranking of the retrieved classes is made, based on the frequency of the class in the top K documents.

Currently, the algorithm takes into consideration only the frequency of the class to calculate its score.

One limitation is that is not taking into consideration the ranking of the class.

This means that if in the top K, we have the first k/2 documents of class C1 and the second k/2 document of class C2, both the classes will have the same score (LUCENE-6654) [[6]](https://issues.apache.org/jira/browse/LUCENE-6654).

This classifier works on top of the Index, let’s quickly have an overview of the constructor parameters :

| Parameter | Description |
| --- | --- |
| leafReader | The Index Reader that will be used to read the index data structures and classify the document |
| analyzer | The Analyzer to be used to analyse the input unseen text |
| query | A filter to apply on the indexed documents. Only the ones that satisfy the query will be used for the classification |
| k | the no. of top docs to select in the MLT results to find the nearest neighbor |
| minDocsFreq | A term (from the input text) will be taken in consideration by the algorithm only if it appears at least in this minimum number of docs in the index |
| minTermFreq | A term (from the input text) will be taken in consideration by the algorithm only if it appears at least this minimum number of times in the input |
| classFieldName | The field that contains the class of the document. It must appear in the indexed documents. **MUST BE STORED** |
| textFieldNames | The list of fields to be taken in consideration for doing the classification. They must appear in the indexed documents |

**Note**:  **`MoreLikeThis`** constructs a Lucene query based on terms in a document. It does this by pulling terms from the defined list of fields (the textField Names parameter, below).   
You usually read that for best results, the fields should have stored term vectors**.**  
**In our case, the text to classify is unseen, it is not an indexed document.**  
**So the TermVector is not used at all.**

### SimpleNaiveBayesClassifier

This Classifier is based on a simplistic implementation of a Naive Bayes Classifier [[3]](https://en.wikipedia.org/wiki/Naive_Bayes_classifier).

It uses the Index to get the Term frequencies of the terms, the Doc frequencies and the unique terms.

First of all, it extracts all the possible classes, this is obtained by getting all the terms for the class field.

Then, each class is scored based on

– how frequent is the class in all the classified documents in the index

– how much likely the tokenized text is to belong to the class

The details of the algorithm go beyond the scope of this blog post.

This classifier works on top of the Index, let’s quickly have an overview of the constructor parameters :

| Parameter | Description |
| --- | --- |
| leafReader | The Index Reader that will be used to read the index data structures and classify the document |
| analyzer | The Analyzer to be used to analyse the input unseen text |
| query | A filter to apply on the indexed documents. Only the ones that satisfy the query will be used for the classification |
| classFieldName | The field that contains the class of the document. It must appear in the indexed documents |
| textFieldNames | The list of fields to be taken in consideration for doing the classification. They must appear in the indexed documents |

**Note**:  **The NaiveBayes** Classifier works on **terms** from the index. This means it pulls from the index the tokens for the class field. **Each token will be considered as a class** and will see a score associated.

This means that you must be careful in the analysis you choose for the **classField** and ideally use a not tokenizer field containing the class (a **copyField** if necessary)

## Lucene Document Classification Extension

The original Text Classifiers are perfectly fine, but what about Document classification?

In a lot of cases, the information we want to classify is composed of a set of fields with one or more values each.

Each field content contributes to the classification (with a different weight to be precise).

Given a simple News article, the title is much more important for the classification in comparison with the text and the author.

But even if not so relevant even the author can have a little part in the class assignation.

The Lucene atomic unit of information is the **Document.**

**Documents are the unit of indexing and search.****A Document is a set of fields.  
Each field has a name and a textual value.**

This data structure is a perfect input for a new generation of Classifiers that will benefit from augmented information to assign the relevant class(es).  
Whenever a simple text is ambiguous, including other fields in the analysis is improving dramatically the precision of the classification.  
In details :

* + the **field** content from the Input Document will be compared with the data structures in the index, only related to that **field**
  + an input field will be analysed according to its **analysis chain**, allowing greater flexibility and precision
  + an **input field can be boosted**, to affect more the classification. In this way, different portions of the input document will have different relevancy to discover the class of the document.

A new interface is provided :

public interface DocumentClassifier<T>

/\*\* \* Assign a class (with score) to the given {@link org.apache.lucene.document.Document} \* \* @param document a {@link org.apache.lucene.document.Document} to be classified. Fields are considered features for the classification. \* @return a {@link org.apache.lucene.classification.ClassificationResult} holding assigned class of type T and score \*/

ClassificationResult<T> assignClass(Document document) throws IOException;

/\*\* \* Get all the classes (sorted by score, descending) assigned to the given {@link org.apache.lucene.document.Document}. \* \* @param document a {@link org.apache.lucene.document.Document} to be classified. Fields are considered features for the classification. \* @return the whole list of {@link org.apache.lucene.classification.ClassificationResult}, the classes and scores. Returns null if the classifier can’t make lists.\*/

List<ClassificationResult<T>> getClasses(Document document) throws IOException;

/\*\* \* Get the first max classes (sorted by score, descending) assigned to the given text String. \* \* @param document a {@link org.apache.lucene.document.Document} to be classified. Fields are considered features for the classification. \* @param max the number of return list elements \* @return the whole list of {@link org.apache.lucene.classification.ClassificationResult}, the classes and scores. Cut for “max” number of elements. Returns null if the classifier can’t make lists.\*/ 

List<ClassificationResult<T>> getClasses(Document document, int max) throws IOException;

And 2 Classifier extended to provide the new functionality :

* **KNearestNeighborDocumentClassifier**
* **SimpleNaiveBayesDocumentClassifier**

The first implementation is available as a contribution to this Jira issue :

*[LUCENE-6631](https://issues.apache.org/jira/browse/LUCENE-6631)*

Now that a new interface is available, it will be much easier to integrate it with Apache Solr.

Stay tuned for the [Solr Classification Integration](https://sease.io/2015/07/solr-document-classification-part-1-indexing-time.html).

## Need Help With This Topic?​​

If you’re struggling with Lucene document classification, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Lucene document classification, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)