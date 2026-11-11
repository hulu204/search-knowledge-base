---
title: 'Categorical Features in Apache Solr Learning to Rank'
company: Sease
tag: 排序
date: 2022-10-06
url: https://sease.io/2022/10/categorical-features-in-apache-solr-learning-to-rank.html
account: 
origin: harvest3-202607
---
If you are reading this blog post is because you are interested in knowing more about Apache Solr Learning to Rank features and specifically the categorical ones. (Did I mention we provide private and public training about [Learning to Rank](https://sease.io/training/learning-to-rank-training)?)

In this blog post, I will therefore give you an overview of which Apache Solr feature types are available for learning to rank models and which is the computational effort required to compute them.

Let’s start with the overview of the Apache Solr Learning to Rank features!

## Original score feature

**The original score feature returns the original score that the document had before performing the reranking.**

Learning to rank is an approach executed on the top k elements returned by a query done using a traditional search method (e.g. BM25).   
In the processing pipeline we, therefore:

1. Execute the traditional query
2. Obtain the documents of interest, sorted by relevance
3. Select the top k documents from this list
4. Execute the learning to rank re-scoring

The original score is the one returned by the traditional query and the one used to sort the initial top-k candidates by relevance. This is the value returned by this learning to rank feature.

Example configuration:

```
				
					{
  "name": "originalScore",
  "class": "org.apache.solr.ltr.feature.OriginalScoreFeature",
  "params": { } 
 }
				
			
```

[[Docs](https://solr.apache.org/docs/8_7_0/solr-ltr/org/apache/solr/ltr/feature/OriginalScoreFeature.html)]

##### COMPLEXITY

This is the simplest feature since it contains an already computed value. Solr just needs to pass this value as a feature to the learning to rank model.

## Value feature

**The value feature allows returning a constant given value for the current document.**

Here we can decide which value to assign to the feature. This value can be a constant or it can be passed externally at runtime(efi i.e. External Feature Information). Most of the time, this is used for query-level features, therefore features whose value depends on the conditions at query execution time (e.g. user device, time of the day, user location, …).   
To make an example, suppose you want to rank things differently if the search came from a mobile device with respect to a desktop one. In the rerank request, you can pass in rq={… efi.userFromMobile=1}, and the above feature will return 1 for all the docs for that request.

Example configuration:

```
				
					{
  "name" : "userFromMobile",
  "class" : "org.apache.solr.ltr.feature.ValueFeature",
  "params" : { "value" : "${userFromMobile}", "required":true }
 }
				
			
```

[[Docs](https://solr.apache.org/docs/8_7_0/solr-ltr/org/apache/solr/ltr/feature/ValueFeature.html)]

##### COMPLEXITY

This is the second feature in terms of simplicity since we are passing the exact value the feature should assume for all the documents of that request.

## Field length feature

**The field length feature returns the length of a field (number of terms occurring in the field value) for the current document.**

Example configuration:

```
				
					{
  "name": "titleLength",
  "class": "org.apache.solr.ltr.feature.FieldLengthFeature",
  "params": {
     "field": "title"
 } 
}
				
			
```

[[Docs](https://solr.apache.org/docs/8_7_0/solr-ltr/org/apache/solr/ltr/feature/FieldLengthFeature.html)]

##### COMPLEXITY

Going down through this list the complexity cost increases since it requires a small computation. We indeed need to compute the length of the specified field for each document returned by the request(and this is extracted from the index), in order to assign a value to the feature and use it in the learning to rank process.

## Field value feature

**The field value feature returns the value of a field in the current document.**

Example configuration:

```
				
					{
  "name":  "rawHits",
  "class": "org.apache.solr.ltr.feature.FieldValueFeature",
  "params": {
      "field": "hits"
  }
}
				
			
```

[[Docs](https://solr.apache.org/docs/8_7_0/solr-ltr/org/apache/solr/ltr/feature/FieldValueFeature.html)]

##### COMPLEXITY

Also here a computation is required. In order to calculate this feature, we have to extract the desired field value from each document returned by the request.

## Solr feature

**The Solr feature allows you to use any Solr query as a feature. The value of the feature will be the score of the given query for the current document.**

See Solr documentation of other parsers you can use as a feature [[Docs](https://lucene.apache.org/solr/guide/other-parsers.html)].

Example configurations:

```
				
					[{ "name": "isBook",
  "class": "org.apache.solr.ltr.feature.SolrFeature",
  "params":{ "fq": ["{!terms f=category}book"] }
}, 
{
  "name": "documentRecency",
  "class": "org.apache.solr.ltr.feature.SolrFeature",
  "params": {
     "q": "{!func}recip( ms(NOW,publish_date), 3.16e-11, 1, 1)"
   }
 }]
				
			
```

[[Docs](https://solr.apache.org/docs/8_7_0/solr-ltr/org/apache/solr/ltr/feature/SolrFeature.html)]

##### COMPLEXITY

This is the most complex feature. Here we have to execute a full query in order to obtain the feature value.

## Categorical features

A categorical feature represents an attribute of an object that has a set of distinct possible values. In computer science, it is common to call the possible values of categorical features Enumerations.

To make an example, if our object is a book, a categorical feature is:

*<book author*> with values: *Orwell, Follet, Austen, Other*

**N.B.** It is easy to observe that giving an order to the values of a categorical feature does not bring any benefit: *Orwell* < *Follet* < *Austen* has no general meaning.

In order to use these features together with the learning to rank (machine learning) model, they need to be encoded in numerical values. The most straightforward approach to encoding categorical features is **one-hot encoding**.

Given a cardinality of N, we build N-1 encoded binary features. In our example:  
*book\_author\_orwell* = 0/1  
*book\_author\_follet* = 0/1  
*book\_author\_austen* = 0/1  
*book\_author\_other* = 0/1

For each book, we will have 1 on the feature that corresponds to the book author, and 0 on the others.

##### LEARNING TO RANK FEATURES

As you could see from what has been presented so far, there is not a predefined Solr learning to rank feature to manage the categorical ones.

Currently, this can only be done by encoding manually the feature. Once done, we can use the **Value feature** and the **Solr feature** presented in the previous paragraph to represent the feature.  
Note that the Solr feature is the most complex feature and therefore, the most expensive one in terms of both time and memory usage.

**Value features** can be useful to represent features that are passed externally and depend on when and who is executing the query (**query level features**). Here the external value will take value 1 or 0 as shown in the one-hot encoding.

Example configurations:

```
				
					{
   "store": "ctrstat_store",
   "name": "userFavouriteAuthor_Orwell",
   "class": "org.apache.solr.ltr.feature.ValueFeature",
   "params": {
      "value": "${userFavouriteAuthor_Orwell}",
      "required": false
    } 
}
				
			
```

**Solr features**, otherwise, can be useful to represent features that depend only on the document itself (**document level**).

Example configurations:

```
				
					{
   "store": "ctrstat_store",
   "name": "book_author_orwell",
   "class": "org.apache.solr.ltr.feature.SolrFeature",
   "params": {
      "fq": [
         "{!terms f=author_name}Orwell"
        ] 
    } 
}
				
			
```

## Summary

In this blog post, we have seen that Solr exposes several learning to rank features. Here is the list ordered from the simplest to the most complex feature:

* Original score feature *– simplest*
* Value feature
* Field length feature
* Field value feature
* Solr feature *– most complex*

In this list, there is no feature that can directly manage categorical features. This can be done by manually encoding the feature and using Value and Solr features as shown in the examples.

## Future Works

We are planning to contribute a new type of Apache Solr learning to rank feature, that automatically manages categoricals, with a mechanism similar to faceting (extracting the categories from the index and exploding one defined feature in features.json to multiple encoded categoricals).

Do you want to sponsor this contribution or help? Feel free to [contact us](https://sease.io/contacts)!

## Need Help With This Topic?​​

If you’re struggling with categorical features in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with categorical features in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)