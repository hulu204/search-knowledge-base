---
title: 'Apache Solr Learning To Rank Feature Extraction and qTime'
company: Sease
tag: 排序
date: 2022-01-12
url: https://sease.io/2022/01/apache-solr-learning-to-rank-feature-extraction-and-qtime.html
account: 
origin: harvest3-202607
---
Hi everyone!  
In this blog post, I would like to walk you through how to measure the timing of the different components that take part in the Learning To Rank query execution time through the qTime parameter.

Let’s start with a brief introduction to Learning To Rank in Apache Solr!

## Introduction

The *contrib* *ltr* is about re-ranking with Learning To Rank models in Apache Solr.

> Re-Ranking allows you to run a simple query for matching documents and then re-rank the top N documents using the scores from a different, more complex query.
>
> solr.apache.org
> [Tweet](https://twitter.com/intent/tweet?text=Re-Ranking+allows+you+to+run+a+simple+query+for+matching+documents+and+then+re-rank+the+top+N+documents+using+the+scores+from+a+different%2C+more+complex+query.+%E2%80%94+solr.apache.org&url=https%3A%2F%2Fsease.io%2F2022%2F01%2Fapache-solr-learning-to-rank-feature-extraction-and-qtime.html)

In our case, the complex query will be a **LTR** query.

The re-ranking process involves a **first query** (first stage retrieval) and the reranking query on the top-k (the **query** using the ‘ltr’ query parser).   
When re-ranking with Learning To Rank, two elements come into play: **feature extraction** and **rescoring** (where we apply the model to calculate a search result score).

So LTR-query requires features definition (**feature.json)** and a **trained model**.

##### FEATURE STORE

The feature store is a data structure (persisted on a file) that describes the set of features used by the model: their names, their classes, and their associated parameters. This needs to be uploaded along with the model to use LTR queries in Apache Solr [[1]](https://solr.apache.org/guide/8_7/learning-to-rank.html#uploading-features).

> A feature is a value, a number, that represents some quantity or quality of the document being scored or of the query for which documents are being scored.
>
> solr.apache.org
> [Tweet](https://twitter.com/intent/tweet?text=A+feature+is+a+value%2C+a+number%2C+that+represents+some+quantity+or+quality+of+the+document+being+scored+or+of+the+query+for+which+documents+are+being+scored.%C2%A0+%E2%80%94+solr.apache.org&url=https%3A%2F%2Fsease.io%2F2022%2F01%2Fapache-solr-learning-to-rank-feature-extraction-and-qtime.html)

There are several different types of features you can use in Solr, if you are curious you can have a look at the documentation [[2]](https://solr.apache.org/guide/8_10/learning-to-rank.html#feature-engineering).

The model’s features can be extracted in two ways and two different phases:

* + during the reranking phase (when using the LTR model)
  + when returning the feature vector to the user in the results, using the *field list* query parameter (*fl*).

When we extract the features through the *fl* parameter, we are internally using a Solr component called **features transformer** [[3]](https://solr.apache.org/guide/8_10/learning-to-rank.html#feature-engineering)[[4]](https://solr.apache.org/guide/8_10/transforming-result-documents.html#transforming-result-documents).

For LTR the transformer is called *LTRFeatureLoggerTransformerFactory* and it can be called inside the *fl* query field as:

```
				
					fl=id,[features store=yourFeatureStore]
				
			
```

In this case, *all the features in the feature store* <yourFeatureStore> will be returned for each document in the search results.

##### MODEL

Also, the model needs to be trained and then uploaded from outside Solr [[5]](https://solr.apache.org/guide/8_10/learning-to-rank.html#uploading-a-model).

A ranking model computes the scores that are used to rerank the documents.   
Irrespective of any particular algorithm or implementation, a ranking model’s computation can use three types of inputs [[6]](https://solr.apache.org/guide/8_10/learning-to-rank.html#ranking-model):

* + algorithm type
  + features that represent the query-document pair
  + algorithm implementation

Also in this case there are several types of models depending on your needs, you can consult them in the documentation [[7]](https://solr.apache.org/guide/8_10/learning-to-rank.html#feature-selection-and-model-training).

## Learning To Rank query performance

Suppose we run an LTR query and want to measure the time it takes to return results, specifically, we want to isolate the time required by **the features extraction** and by the **model rescore**.

How can we measure them?

##### QTIME

The qTime is a Solr output element that expresses the time required by Solr to process the request and find the results.  
The qTime of a query is therefore the time required by Solr to process the query (without network latencies).

qTime covers:

1. 1. Matching phase
   2. Ranking phase
   3. Re-Ranking phase
   4. Faceting
   5. Spellchecking
   6. other search components

**qTime doesn’t cover**:

1. 1. The time required to write the JSON response
   2. The time required to retrieve stored fields/docValues to be rendered in the response
   3. The time required to process the transformer requested in the *field list (fl)* parameter

We aim to understand in this qTime how much is required for the reranking and how much is required for feature extraction.

###### PROBLEM: HOW TO MEASURE THE TIME NECESSARY FOR FEATURE EXTRACTION?

Feature extraction is executed during the re-ranking phase, but Apache Solr doesn’t explicitly measure the time taken. Given the fact, the feature transformer executed on the search results to display the feature vectors does a similar job in extracting the feature vector, someone can think to send a minimal query that invokes the feature transformer (*fl*) to isolate and compute the time required for feature extraction.  
However, **the time required to execute the transformers is not included in the qTime** and therefore this approach cannot be used for our purpose.

###### First attempt

The first approach we used to solve the problem was to consider the HTTP response time to compute the impact of the feature extraction.  
We executed a small query like this:

```
				
					https://localhost:8983/solr/solr_collection/select?debug=timing&amp;q=*:*&amp;fl=[features 
store=our_ltr_store]
				
			
```

and looked at the HTTP response time.   
Even if we remove the qTime from the HTTP response time to isolate feature extraction, another problem arises:   
HTTP response time contains also the time necessary to build the response JSON, therefore, the higher the number of features requested in *fl*, the higher the time required to create the response.

So we couldn’t isolate successfully the feature extraction time.

###### Second attempt

The second approach we used is based on a **dummy model**.  
This is the simplest *MultipleAdditiveTreesModel* we can create, therefore a model that assigns always the same constant value for each search result: 10.   
Below is the model:

```
				
					{
   "store": "our_ltr_store",
   "class" : "org.apache.solr.ltr.model.MultipleAdditiveTreesModel",
   "name" : "our_ltr_model",
   "features": [
    {
        "name": "feature_1"
    },
    ...
    {
        "name": "feature_n"
    }
    ],
   "params" : {
       "trees" : [
           {
               "weight" : "1",
               "root" : {
                   "value" : "10"
               }
           }
       ]
   }
}
				
			
```

Using this model we can see that the time required by the model rescore is minimal and that most of the qTime is actually used for features extraction.

Here is an example of a query Q with reranking:  
– feature extraction happens for 6575 features  
– a complex model rescores each search result using the 6575 features  
QTime = 5080ms

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/11/complex_model_result_rq_many_features.png?w=800&ssl=1)

Here is an example with the same query Q with reranking:  
– feature extraction happens for 6575 features  
– a dummy model rescores each search result, with a constant score of 10  
QTime = 4529ms

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/11/dummy_model_result_rq_many_features.png?w=800&ssl=1)

**As we can see, the time is similar with both methods. If most of the time was due to reranking, we should have seen a great reduction in qTime, which is not the case.**

The usage of this dummy model allows us to **estimate the features extraction time spent.**

What happens when you extract more or fewer features for your model reranking?

We can notice two behaviours:

1. 1. The more features Apache Solr extracts for the model, the more time **is required to execute the query**
   2. **The greater the number of documents we want to rerank, the more time is required to execute the query.** The greater the number of documents we want to rerank, the greater the number of times we execute features extraction and scoring(once for each document).

This may sound obvious but let’s validate that with the dummy model approach:  
The *first behaviour* is reflected by the qTime necessary to execute reranking on 10 documents (rerank docs = 10) with the dummy model with few features (qTime = 10) and the qTime necessary to execute reranking on 10 documents with the dummy model with many features (qTime = 210).   
The *second behaviour* is reflected by the qTime necessary to execute reranking on 10 documents (rerank docs = 10) with the dummy model with many features (qTime = 210) and the qTime necessary to execute reranking on 10000 documents with the same dummy model (qTime = 6726).

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/11/image-8.png?w=800&ssl=1)

## Summary

In this blog post we have seen:

1. 1. An introduction to Learning To Rank query workings in Apache Solr.
   2. Which components take part in the LTR query: features, model.
   3. What is the qTime and why it cannot give us information about the feature extraction time required by the query to use the model.

For the last point, we have seen that qTime does not consider the time required by the fl transformer parameter to extract the features. If we, therefore, want to know how long it takes, we need to estimate the time from the rq part (unfortunately you can’t just use the transformer for that).  
This can be done using a dummy model which reduces the time required by all the other query parts except the feature extraction.  
From the tests with the dummy model, we could see that most of the time is required by the features extraction.

A Jira issue is open to integrate the features extraction timing in the debug Solr option at query time [[8]](https://issues.apache.org/jira/browse/SOLR-15778).

## Need Help With This Topic?​​

If you’re struggling with feature extraction in learning to rank, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with feature extraction in learning to rank, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)