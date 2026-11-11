---
title: 'Solr Is Learning To Rank Better – Part 1 – Data Collection'
company: Sease
tag: 排序
date: 2016-07-25
url: https://sease.io/2016/07/apache-solr-learning-to-rank-part-1-data-collection.html
account: 
origin: harvest3-202607
---
This blog post is about the journey needed to bring Learning To Rank In Apache Solr search engines.

Learning to Rank [[1]](https://en.wikipedia.org/wiki/Learning_to_rank) is the application of Machine Learning in the construction of ranking models for Information Retrieval systems.

Introducing supervised learning from user behaviour and signals can improve the relevancy of the documents retrieved bringing a new approach in ranking them.

Can be helpful in countless domains, refining free text search results or building a ranking algorithm where only filtering is happening and no initial scoring is available.

This series of blog posts explores a full journey from the Signals Collection through the re-ranking in Apache Solr.

**Part 1**  will explore the data collection, data modelling and refining phase  
[**Part 2**](https://sease.io/2016/08/apache-solr-learning-to-rank-part-2-model-training.html) will explore the training phase  
[**Part 3**](https://sease.io/2016/08/apache-solr-learning-to-rank-part-3-ltr-tools.html) will describe a set of utilities to analyse your models  
**[Part 4](https://sease.io/2016/10/apache-solr-learning-to-rank-better-part-4.html)** will cover the Solr integration

**Requirement**: Minimal knowledge and interest in Machine Learning.

*Special thanks to **Diego Ceccarelli**, who helped me a lot in 2015 introducing me to this amazing topic.*  
*Second special thanks to **Juan Luis Andrades**, for the passion we shared during this journey and **Jesse McLaughlin** for the careful technical Java insights.*  
*Final special thanks to **David Bunbury** who contributed with interest, passion and very thoughtful ideas to the cause.*

## Collecting Signals

The start of the journey is the signals collection, it is a key phase and involves the modelling of the supervised training set that will be used to train the model.

A training set can be **Explicit** or **Implicit**.

##### IMPLICIT TRAINING SET

An Implicit training set is collected from user behaviours and interactions.

***e.g**.*

*Historical sales and transactions of an E-commerce website*

*User Clicks on the search result page*

*Time spent on each document accessed*

A training set of this type is quite noisy but allows the collection of great numbers of signals with small effort.

The more the user was engaged with a particular document, the stronger the signal of relevancy.

***e.g**.*

*A sale of a product is a stronger signal of relevancy than adding it to the basket*

*User Clicks on the search result page in comparison with the documents shown but not clicked*

*The longer you read a document, the stronger the relevancy*

*+ **Pros**: Cheap to build*

*– **Cons**: Noisy*

##### EXPLICIT TRAINING SET

An Explicit training set is collected directly from the interaction with Human Experts.

Given a query and a set of documents, the Human expert will rate the relevancy of each document in the result set.

The score assigned to the document will rate how relevant the document was for the query.

To remove the subjective bias is suggested to use a team of experts to build the training set.

A training set of this type is highly accurate but it is really expensive to build as you need a huge team of experts to produce thousands of ratings for all the queries of interest.

*+ Pros: Accuracy*

*– Cons: Expensive to build*

##### The Training Set

###### The training set can have different forms, for the sake of this post we will focus on an algorithm that internally uses a pairwise/listwise approach.

In particular, the syntax exposed will be the RankLib [[2]](https://sourceforge.net/p/lemur/wiki/RankLib%20File%20Format/) syntax.

Each sample of the training set is a signal/event that describes a triple (Query-Document-Rating).

Let’s take as an example a query (1) and a document (1A)

```
				
					3 qid:1 1:1 2:1 3:0 # 1A
				
			
```

The document can be represented as a feature vector which is a vector of scalar numeric values.

Each element in the vector represents a specific aspect of the document.

We’ll see this in the feature part in detail.

Let’s now focus on understanding the sample :

**3**  
How relevant the document is for the query

**qid:1**  
Identify the query

**1:1 2:1 3:0**  
The document represented as a vector of numerical features

**# 1A**  
A comment, to make more readable your training data

## Feature Engineering

For the convenience of Machine Learning algorithms, query-document pairs are represented by numerical vectors.

Components of such vectors are called features and can be divided into different groups (if they depend on the document, the query or both):

###### Document Features (query independent)

This kind of feature depends only on the document and not on the query.

**e.g.**

*Document length*

*Price of the product*

*User Rating of the product*

An interesting aspect of these features is that they can be potentially precomputed in offline mode during indexing. They may be used to compute the document’s *static quality score* (or *static rank*), which is often used to speed up search query evaluation.

###### Query Dependent Features

This kind of feature depends on the query and the document

**e.g.**

*Is the document containing the query text in the title?*  
*Is the document (product) of the same brand as expressed in the query?*

###### Query Level Features

This kind of feature depends only on the query.

**e.g.**

*Number of words in the query*

*Cuisine Type Selected (e.g. “Italian”, “Sushi” when searching for Restaurants)*  
*Date Selected ( e.g. when searching in a Hotel Booking system)*

*Department Selected ( e.g. “electronics”, “kitchen”, “DIY” … in an E-commerce website)*

###### User Dependent Features

Also in this case this kind of feature does not depend on the document.

It only depends on the user running the query.

**e.g.**

*Device*

*Age of the user*

*Gender*

As described, for convenience of the mathematical algorithms each high-level feature must be modelled as a numeric feature.

In the real world, a feature describes an aspect of the object (document) and must be represented accordingly:

###### Ordinal Features

An ordinal feature represents a numerical value with a certain position in a sequence of numbers.

**e.g.**

*Star Rating  (for a document describing a Hotel)*

*Price  (for a document describing an e-commerce product)*

For the Star Rating feature, stands an order for the different values:

1<2<3<4<5  is logically correct.

For the Price feature, the same observation applies.

100$ < 200$ <300$

A feature is Ordinal when it is possible to compare different values and decide the ranking of these.

###### Categorical Features

A categorical feature represents an attribute of an object that has a set of distinct possible values.

In computer science, it is common to call the possible values of categorical features Enumerations.

**e.g.**

*Colour ( for a document describing a dress)*

*Country ( for a document describing a location)*

It is easy to observe that giving an order to the values of a categorical feature does not make any sense.

For the Colour feature :

red < blue < black has no general meaning.

###### Binary Features

A binary feature represents an attribute of an object that can have only two possible values.

Traditionally 0 / 1 in accordance with the binary numeral system.

**e.g.**

*Is the product available? yes/no ( for a document describing an e-commerce product)*

*Is the colour Red? ( for a document describing a dress)*

*Is the country Italy? ( for a document describing a location)*

## One Hot Encoding

When a categorical feature describes your Document, it is tempting to represent each category as an Integer Id :

**e.g.**

***Categorical Feature**: colour*

***Distinct Values**: red, green, blue*

***Representation** : colour:1, colour:2 colour:3*

With this strategy, the Machine learning algorithm will be able to manage the feature values.

**But is the information we pass the same as the original one?**

Representing a categorical feature as an ordinal feature is introducing an additional ordinal relationship :

1(red) < 2(green) < 3(blue)

which doesn’t reflect the original information.

There are different ways to encode categorical features to make them understandable by the training algorithm. We need basically to encode the original information the feature provides in a numeric form, without any loss or addition if possible.

One possible approach is called One Hot Encoding [[3]](https://www.quora.com/What-is-one-hot-encoding-and-when-is-it-used-in-data-science):

Given a categorical feature with N distinct values, encode it in N binary features, each feature will state if the category applies to the Document.

**e.g.**

***Categorical Feature**: colour*

***Distinct Values**: red, green, blue*

***Encoded Features** : colour\_red, colour\_green, colour\_blue*

A document representing a blue shirt will be described by the following feature vector :

```
				
					... colour_red:0 colour_green:0 colour_blue:1 ...
				
			
```

One Hot Encoding is useful to properly model your information, but take care of the cardinality of your categorical feature as this will be reflected in the number of final features that will describe your signal.

###### War Story 1: High Cardinality Categorical Feature

A signal describing a document with a high-level categorical feature (with N distinct values) can produce a Feature vector of length N.

This can deteriorate the performance of your trainer as it will need to manage many more features per signal.

It happened to me, that simply adding one categorical feature was bringing in thousands of binary features, exhausting the hardware my trainer was using,  killing the training process.

To mitigate this, can be useful to limit the encoded distinct values only to a subset :

* + with white list/black list approach business-driven
  + keeping only the top occurring values
  + keeping only the values occurring more than a threshold
  + encode the rest as a special feature :colour\_misc
  + Hash the distinct values into a reduced set of hashes

##### Feature Normalization

Feature Normalisation is a method used to standardize the range of values across different features, a technique quite useful in the data pre-processing phase.

As the majority of machine learning algorithms use the Euclidean distance to calculate the distance between two different points (training vector signals), if a feature has widely different scales, the distance can be governed by this particular feature.

Normalizing can simplify the problem and give the same weight to each of the features involved.

There are different types of normalization, some of them :

* + Linear Normalization (min/max based)
  + Sum Normalization (based on the sum of all the values of the feature)
  + Z Score (based on the mean/standard deviation of the feature)

##### Feature Value Quantization

Another approach to simplify the job of the training algorithm is to quantise the feature values, to reduce the cardinality of distinct values per feature.

It is the simple concept of rounding, whenever we realise that it does not make any difference for the domain to model the value with high precision, it is suggested to simplify it and round it to the acceptable level.

**e.g.**

***Domain**: hospitality*

***Ranking problem**: Rank restaurants’ documents*

*Assuming a feature is the trip\_advisor\_reviews\_count, is it necessary to model the value as the precise amount of reviews? Normally, it would be simpler to round to the nearest k ( 250 or whatever is sensible to the business)*  
**Note:** Extra care must be taken into account if following this approach.  
The reason is that adding an artificial rounding to the data can be dangerous, we can compromise the feature itself setting up hard thresholds.  
It is always better if the algorithm decides the thresholds with freedom.  
It is suggested that it is possible to not quantize, or quantize only after a deep statistical analysis of our data.  
If the target is to simplify the model for any reason, it is possible to evaluate at training time fewer threshold candidates, depending on the training algorithm.

##### Missing Values

Some of the signals we are collecting could miss some of the features (data corruption, a bug in the signal collection or simply the information was not available at the time).

Modelling our signals with a sparse feature vector will imply that a missing feature will be modelled as a feature with a value of 0.

This should generally be ok, but we must be careful in the case that 0 is a valid value for the feature.

**e.g.**

*Given a **user\_rating** feature*

*A rating of 0 means the product has a very bad rating.*

*A missing rating means we don’t have a rating for the product (the product can still be really good).*

A first approach could be to model the 0 ratings as slightly greater than 0 (i.e. 0 + ε) and keep the sparse representation.

In this way, we are differentiating the information but we are still modelling the wrong ordinal relationship :

**Missing User Rating  (0) < User Rating 0 (0 + ε)**

Unfortunately, at least for the RankLib implementation, a missing feature will always be modelled with a value of 0, this, of course, will vary from algorithm to algorithm.

But we can enforce the learning a bit, by adding a binary feature that states that the User Rating is missing:

**user\_rating:0 , user\_rating\_missing:1 .**

This should help the learning process to understand better the difference.  
Furthermore, if possible we can help the algorithm by avoiding the sparse representation if necessary and setting for the missing feature a value which is the avg of the feature itself across the different samples.

##### Outliers

Some of the signals we are collecting could have some outliers (some signals with an unlikely extremely different value for a specific feature).

This can be caused by bugs in the signal collection process or simply the anomaly can be a real instance of a really rare signal.

Outliers can complicate the job of the model training and can end up in overfitting models that have difficulties in adaptation for unknown datasets.

Identifying and resolving anomalies can be vitally important if your dataset is quite fragile.

Tool for data visualisation can help in visualising outliers, but for a deep analysis, I suggest to have a read of this interesting blog post [[4]](https://machinelearningmastery.com/how-to-identify-outliers-in-your-data/).

##### Feature Definition

Defining the proper set of features to describe the document of our domain is a hard task.

It is not easy to identify in the first place all the relevant features even if we are domain experts, this procedure will take time and a lot of trial and error.

Let’s see a guideline to try to build a feature vector as best as possible:

* + **Keep it simple**: start from a limited set of features which are fundamental to describe your problem, the model produced will be really poor, but at least you have the baseline.
  + **Iteratively train the model:** removing or adding a feature at each execution. this is time-consuming but will allow you to identify clearly which features really matter.
  + **Visualize Important Features**: After you trained the model, use a visualisation tool to verify which feature is appearing more.
  + **Meet the Business**: Have meetings with the business, to compare what they would expect to see re-ranked and what the model re-ranks. When there is discordance let’s have the humans explain why, this should drive to identify missing features or features that were used in the wrong meaning.

## Data Preparation

We have carefully designed our vectorial representation of the domain documents, identified the source of our signals and built our training set.  
So far, so good…  
However, the model is still performing poorly.  
In this scenario, the reasons can be countless :

* + Poor signal quality (noise)
  + Incomplete feature vector representation
  + Not uniform distribution of relevant-not relevant documents per queries

Let’s explore some guidelines to overcome some of these difficulties:

##### Noise Removal

In the scenario of implicit signals, we likely model the relevancy rating based on an evaluation metric of the user engagement with the document given a certain query.

Depending on the domain we can measure the user engagement in different ways.

Let’s see an example for a specific domain:  **E-commerce**

We can assign the relevancy rating of each signal depending on the user interaction :

Given a scale of 1 to 3 :

**1** – The user clicks the product

**2** – The user added the product to the basket

**3** – The user bought the product

The simplest approach would be to store 1 signal per user interaction.

User behavioural signals are noisy by nature, but this approach introduces even more noise, as for the same feature vector we introduce discordant signals, specifically, we are telling the training algorithm that given that feature vector and that query, the document is at the same time :

vaguely relevant – relevant – strongly relevant.

This doesn’t help the training algorithm at all, so we need to find a strategy to avoid that.

One possible way is to keep only the strongest signal per document query per user episode.

In the case of a user buying a product, we avoid storing in the training set 3 signals, but we keep only the most relevant one.

In this way, we transmit to the training algorithm only the important information for the user interaction with no confusion.

##### Unbalanced Dataset

In some domains, would be quite common to have a very unbalanced dataset.

A dataset is unbalanced when the relevancy classes are not represented equally in the dataset i.e. we have many more samples of a relevancy class than another.

Taking again the E-commerce example, the number of relevant signals (sales) will be much less than the number of weak signals (clicks).

This unbalance can make life harder for the training algorithm, as each relevant signal can be covered by many more weakly relevant ones.

Let’s see how we can manipulate the dataset to partially mitigate this problem:

###### Collect more data

This sounds simple, but collecting more data is generally likely to help.

Of course, there are domains when collecting more data is not beneficial (for example when the market changes quite dynamically and the previous year’s dataset becomes almost irrelevant for predicting the current behaviours ).

###### Resample the dataset

###### You can manipulate the data you collected to have more balanced data.

This change is called sampling your dataset and there are two main methods that you can use to even-up the classes: Oversampling and Undersampling [[5]](https://en.wikipedia.org/wiki/Oversampling_and_undersampling_in_data_analysis).

You can add copies of instances from the under-represented relevancy class, this is called over-sampling, or

you can delete instances from the over-represented class, this technique is called under-sampling.

These approaches are often very easy to implement and fast to run. They are an excellent starting point.

Some ideas and suggestion :

* + Consider testing under-sampling when you have a lot of data (tens- or hundreds of thousands of instances or more), you can undersample randomly or follow any business logic available.
  + Consider testing different resampled ratios (it is not necessary to target a 1:1 ratio).
  + When oversampling considers advanced approaches, instead of simple duplication of already existent samples, could be good to artificially generate new ones.

Be careful, resampling is not always helping your training algorithm, so experiment in detail with your use case.

###### War Story 2: Oversampling by duplication

Given a dataset highly unbalanced, the model trained was struggling to predict accurately the desired relevancy class for document-query test samples.

Oversampling was a tempting approach, so here we go!

As I am using cross-validation, the first approach has been to oversample the dataset by duplication.

I took each relevancy class and duplicated the samples until I built a balanced dataset.

Then I started the training in cross-validation and trained a model which was immense and almost perfectly able to predict the relevancy of validation and test samples.

Cool! I got it!

But it was not an amazing result at all, because of course applying cross validation on an oversampled dataset built validation and test sets oversampled as well.

This means that it was really likely that a sample in the training set was appearing exactly the same in the validation set and in the test set.

The resulting model was basically highly overfitted and not that good to predict unknown test sets.

So I moved to a manual training set- validation set – test set split and oversampled only the training set.

This was definitely better and built a model that was much more suitable.

It was not able to perfectly predict validation and test sets but this was a good point as the model was able to predict unknown data sets better.

Then I trained again, this time the original dataset, manually split as before but not oversampled.

The resulting model was actually better than the oversampled one.

One of the possible reasons is that the training algorithm and model I was using (LambdaMART) didn’t get any specific help from the resampling, actually the model lost the capability of discovering which samples were converting better (strong relevant signals: weak relevant signals ratio).

Practically I favoured the volume over the conversion ratio, increasing the recall but losing the precision of the ranker.

**Conclusion**: Experiment, evaluate the approach with your algorithm, compare, and don’t assume it is going to be better without checking

##### Query Id hashing

As we have seen in the initial part of the blog, each sample is a document-query pair, represented in a vectorial format.

The query is represented by an Id, this Id is used to group samples for the same query, and evaluate the ranker performance over each sample group.

This can give us an evaluation of how well the ranker is performing on average on all the queries of interest.

This brings us to carefully decide how we generate the query identifier.

If we generate a **too-specific hash**, we risk building small groups of samples, these small groups can get a high score when ranking them, biased by their small size.

*Extreme case*

**e.g.**

*A really specific hash, brings many groups to be 1 sample group.*

*This brings up the evaluation metric score, as we are averaging and a lot of groups, being of size 1, are perfectly easy to rank.*

If we generate a hash that is not specific enough we can end up in immense groups, not that helpful to evaluate our ranking model on the different real-world scenarios.

The ideal scenario is to have one query Id per query category of interest, with a good number of samples related, this would be the perfect dataset, in this way, we can validate both:

* + the intra-group relevancy (as the group are composed of sufficient samples).
  + the average across the queries (as we have a valid set of different queries available).

The query category could depend on a set of **Query Dependent Features**, this means that we can calculate the hash using the values of these features.

Being careful we maintain a balance between the group sizes and the granularity of the hash.

It is important to have the query categories across the training/validation/test set:

**e.g.**

*We have 3 different query categories, based on the value of a user-dependent feature ( user\_age\_segment).*

*These age segments represent three very different market segments, that require very different ranking models.*

*When building our training set we want enough samples for each category and we want them to be split across the training/validation/test sets to be able to validate how good we are in predicting the different market segments.*

*This can potentially drive the building of separate models and separate data sets if this is the case.*

## Need Help With This Topic?​​

If you’re struggling with integrating Learning to Rank in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with integrating Learning to Rank in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)