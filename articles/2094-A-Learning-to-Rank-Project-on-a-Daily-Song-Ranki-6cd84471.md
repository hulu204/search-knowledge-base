---
title: 'A Learning to Rank Project on a Daily Song Ranking Problem'
company: Sease
tag: 排序
date: 2020-12-18
url: https://sease.io/2020/12/a-learning-to-rank-project-on-a-daily-song-ranking-problem.html
account: 
origin: harvest3-202607
---
## Introduction

Ranking data naturally appears in various situations, especially in modern data processing applications (search engines, recommendation systems). In a real-world scenario, understanding how to fit a specific dataset and design a pipeline to solve a ranking problem is therefore crucial.

This blog aims to illustrate how to set up and build a **Learning to Rank** (LTR) system starting from the available data, creating and manipulating the training set and the test set, and then training a ranking model using open source libraries.

LTR is an application of machine learning in *Information Retrieval*, where training data consists of lists of items defined as **query-document pairs** to which a relevance rating is associated. The key challenge of applying LRT is to come up with the optimal ordering of these items with respect to a given query.

## Problem Statement

This internal project began during the Sease Company Meeting held in September, as part of the Machine Learning Multidisciplinary Hackathon. The objective of Sease’s Hackathon was to adapt the Spotify dataset on Worldwide Daily Song Ranking [[8]](https://www.kaggle.com/edumucelli/spotifys-worldwide-daily-song-ranking) to an LTR task.

The dataset is about **the daily ranking of the 200 most listened to songs in 53 countries by Spotify users**; it spans the period from 1 January 2017 to 9 January 2018 and contains more than 3 million rows, 6629 artists, and 18598 songs for a total count of one hundred five billion streams counts. The picture below shows all the available dataset features. The challenge was modifying the structure of the Spotify dataset, which was not created for an LTR task, to obtain query-document pairs with an estimated relevance judgment.

![spotify dataset kaggle](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/dataset-spotify-kaggle.png?fit=800%2C544&ssl=1)

## Our Approach

During the exploration of the dataset, we began to brainstorm and comprehend which features may or may not impact the relevance of the documents (songs). We start this phase by distinguishing the feature levels:

* + **Document level**: describes a property of the DOCUMENT and its value depends only on the document instance;
  + **Query level**: describes a property of the QUERY and its value depends only on the query instance;
  + **Query Dependent**: describes a property of the QUERY in correlation with the DOCUMENT, so its value depends on the query and document instance.

The breakdown of the features is shown in detail in the table below.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-09-alle-17.08.22.png?fit=800%2C291&ssl=1)

### Let's set up a Learning to Rank experiment

Learning to Rank links machine learning with the search engines. In our hypothetical scenario, we assumed a trained ranking model deployed into Spotify’s search engine, where:

* + **documents** are the songs,
  + the **query** is a search for one of the region/country,
  + the **relevance rating** is estimated from the position on the chart,
  + the **feature vector** is composed of all the other N-given features.

Spotify’s search engine takes in input the ‘Region’ (Country), as the query issued by the user, it then extrapolates the best results for that query, with traditional IR, and passes them to the re-ranking model. The re-ranking model will re-order the best results before returning them to the user. In other words, the model can return a re-ranking of the songs based on their relevance to the query (i.e. in our case the most relevant songs for that country).

##### Data Preprocessing

Data preprocessing is the most important step of the pipeline; it is a data mining technique used to transform the raw data into a useful and suitable format that can be interpreted and parsed by the algorithm.

Our data preprocessing pipeline starts with the Data cleaning phase.   
**Data cleaning** is the process of ensuring that data is correct, consistent, and usable, removing and manipulating those irrelevant and missing parts of the real-world data we collect. We applied this technique in our Spotify dataset checking its completeness and finding a total of 657 NaN (Not a Number) in the Track Name and Artist features.   
Since the songs and relative artists recur in our dataset (on songs chart of different days) and each song-artist pair is uniquely identified by an ID (that is the URL feature encoded as an enumerated type), the creation of a dictionary helped us to manage and fill in these missing values. A dictionary consists of a collection of key-value pairs; we have used the univocal ID of the song as keys and the Track names as values. Every time we find a missing value in the Track Name, we check for the same song-artist ID in the dictionary keys and populate the missing value with the corresponding dictionary value. The same thing was done to fill in all rows containing missing values in the Artist column.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-03-alle-10.27.18.png?fit=516%2C566&ssl=1)

Additionally, **Feature Engineering** is vital to prepare the proper input dataset, select the most important features, transform them and/or create new features from existing ones. In particular, categorical features, typically stored as text values, need to be encoded in numbers since most machine learning algorithms cannot handle them. Therefore, there is no single answer on how to approach this problem and we were faced with the challenge of figuring out how to transform these text attributes into suitable numerical values.

Let’s see in detail the structure of the features and the approach we decided to undertake to solve this problem:

* + **Position: song’s position on the chart – Relevance Rating**

This feature was used to estimate the Relevance Rating, our Target variable. Using position values ​​as relevancy labels would not have been appropriate, their values ​​range is indeed from 1 to 200 and it may be too wide and misleading to the model.   
Therefore we decided to group the position values using a form of quantization called **data binning**, a data pre-processing technique for grouping numbers into fewer “bins”. We tested two different variations, relevance labels from 0 to 10 and relevance labels from 0 to 20, and then checked how the model performance changed. In doing the data binning, we tried to keep a finer grain in the grouping of the most relevant songs (those in the highest positions of the chart). In the figure below there is an example of data binning. Here we generate relevance labels from 0 to 10 in the so-called Ranking column.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-16-alle-21.32.40.png?fit=800%2C570&ssl=1)

* + **Track Name: song title – Document Level Feature**

We decided to encode this variable using 2 different approaches: **Hash Encoding and Doc2Vec**; then we made a comparison between these two techniques based on the models’ output.

**Feature hashing** maps each category, in the categorical feature Track Name, to an integer within a pre-determined range. To implement this method, we use the **category\_encoders** [[1]](https://contrib.scikit-learn.org/category_encoders/hashing.html) library.   
We specified, as main arguments of the function, the column to encode, the dimensionality of the feature vectors (by default is equal to 8), and the hash function to apply (by default the ‘**md5**’ algorithm). After the encoding, the Track Name feature has been replaced by 8 new additional columns, from col\_0 to col\_7 [index 0 to 7], which contain binary values either 1 or 0.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-15-alle-09.43.38.png?fit=742%2C430&ssl=1)

**Doc2Vec** is an unsupervised algorithm that represents a document/sentence as a vector [[2]](https://radimrehurek.com/gensim/models/doc2vec.html). It is an adaptation of Word2Vec, one of the most popular techniques in Natural Language Processing, and is applied to the entire document instead of its individual words. It uses deep learning and neural networks-based techniques to compute a feature vector for every document/sentence in the corpus. Doc2Vec operates on the logic that the meaning of a word also depends on the document that it occurs in; for this reason, we need to specify a **tag** (i.e. a unique document id, named *Paragraph ID*) to each sentence (or paragraph).

###### Main step

* + Preprocess the ‘Track Name’ feature strings, converting to lowercase, keeping only alphanumeric and spaces, and removing punctuation;
  + Replace each sentence (song title) with a list of its words;
  + Convert these sentences into a training corpus of **TaggedDocument**, consisting of 2 parts: a list of words and a relative tag. For simplicity, we only assign to each sentence a unique integer id using the indices of song titles as a tag.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-05-alle-15.39.21.png?fit=1040%2C286&ssl=1)

* + Create the *vocabulary*, which is a list of all of the unique words extracted from the training corpus
  + Pass the TaggedDocument as the input to the **Doc2Vec function**. Other parameters specified in the function are:
    - **dm**: to define the training algorithm (by default dm =1, which is the ***Distributed Memory version of Paragraph Vector (PV-DM***));
    - **vector\_size**: to define the dimensionality of the feature vectors (100 by default);
    - **min\_count**: to ignore all words with a total frequency lower than the set value.
  + Use the docvecs property [*model.docvecs.doctag\_syn0*] to get all the trained vectors for the ‘document tags’ seen during training. The track Name feature has been replaced by 100 new additional encoded columns, as shown in the picture below.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-05-alle-15.39.36.png?fit=1070%2C390&ssl=1)

Furthermore, we hypothesized that this variable could also be used to extract the language of the song, which could be used as an additional feature. There are several libraries to cope with this task; we tried *langdetect* and *guess\_language-spirit*, two Python libraries that have no limitations but poor accuracy. Otherwise, libraries, like *TextBlob* and *Googletrans*, have high accuracy but limited daily requests since they use Google’s API to detect the language. Also, we have to say that the song’s title is often too short to allow for a good language estimation. Furthermore, it may not contain letters but only numbers and/or symbols. If the title of a song is ‘100%’, what language is it? Can’t tell it, right? In this case, we should add a try/except block of code to catch and handle this type of situation properly.

* + **Artist: name of singer or group – Document Level Feature**

Since the Artist is a categorical variable with many levels, it could be encoded using the **Leave One Out technique** [[3]](https://contrib.scikit-learn.org/category_encoders/leaveoneout.html); it is very similar to Target encoding, the process of replacing a categorical value with the mean of the target variable values related to that level, but in this case, it excludes the current row’s target value when calculating the mean (see picture below).

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-16-alle-08.14.43.png?fit=622%2C630&ssl=1)

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-03-alle-09.50.26.png?fit=960%2C814&ssl=1)

Another approach could be the use of the **One-Hot Encoding technique**, used to convert categorical values into a 1-dimensional numerical vector. The resulting vector consists of N elements, one for each level of the categorical feature. The vector will have all 0s except for a single (hot) 1 on the element that specifies the current category. This method simply creates additional (binary) features based on the number of unique values (N) in the categorical features. It is quite obvious that with a variable that contains 6629 levels (thus 6629 artists), this technique is not a great choice due to the addition of a large number of dimensions to the dataset that can cause problems of parallelism and multicollinearity.

* + **Streams: number of streams – Document Level Feature**

It can be kept as it is, since already numeric.

* + **URL: Spotify url of the song**

The URL feature was encoded as an enumerated type (ID) and used for the data preprocessing part (handling missing values) but then was removed from the training set data. When we consider the document-level features, we need to understand whether a feature, regardless of the query, may or may not have an impact on the relevance of that document. In our case, since a unique URL corresponds to a unique song-artist pair, this data is already represented by Track Name and Artist, and it wouldn’t add any additional useful information to the importance estimation of a query-document pair.

* + **Date: chart date – Query Level Feature**

The date could be divided into multiple columns describing the day, month, and year separately, and used to extract additional features like the weekday (0 to 6 means Monday to Sunday). Especially months and days of the week can be quite useful in understanding the periodicity and seasonality of the events (for example summer or Christmas songs).

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-03-alle-09.50.44.png?fit=2148%2C934&ssl=1)

* + **Region: country code – Query**

We selected this feature as the Query (of the search engine) and manipulated it through the *pandas **factorize()** function* [[4]](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.factorize.html) that uniquely links each string with an integer

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-03-alle-09.50.51.png?fit=1208%2C828&ssl=1)

##### Model Training

When the dataset is ready and well structured, a train-test split procedure must be performed. The training set is used by the machine learning algorithm to train the model, while the test dataset is held back and used to evaluate the performance of the model. In our experiment, we put 80% of the dataset in the training set and the remaining 20% in the test set. We have decided to implement LTR using one of the most widely used open-source libraries called **XGBoost** [[5]](https://github.com/dmlc/xgboost), which is an optimized distributed gradient boosting library designed to be highly efficient, flexible, and portable.   
It implements machine learning algorithms under the Gradient Boosting framework available for Python or other programming languages. It supports both pair-wise and list-wise approaches.

We then separated the Relevance Label column, the Query column, and the training vectors as three different components to create the **XGBoost matrices**, structures needed to train the model with XGBoost.

With the training set in hands, we trained the model using the **LambdaMART** method, a combination of the LambdaRank and MART algorithms.   
If you check the XGBoost documentation [[6]](https://xgboost.readthedocs.io/en/latest/) you can see that there are three Ranking methods; they all use the LambdaMART algorithm, but with a different objective function. We chose ‘**rank:ndcg**‘ to perform list-wise ranking, which directly looks at the entire list of documents (for each query) and tries to come up with the optimal ordering for it.

To measure the output of the models, we used a metric called **Normalized Discounted Cumulative Gain (NDCG)**, the normalized variant of DCG. This metric is generally preferred when multiple levels of relevance are used. The **DCG** aims to evaluate whether the model can return the most relevant documents in the highest positions of the search result list and the least relevant documents in the lowest position (descending). To interpret the metric, all we want to know is how close we are to the maximum achievable DCG. Dividing the DCG values by the best possible score (Ideal DCG), we obtain the normalized values between 0 and 1, where 1 indicates the best possible ranking.

In particular, we used an **ndcg@10** where “@10” denotes that the metric is evaluated only on the top 10 items/songs of the search result list. The final evaluation measure is then an average across the queries: the NDCG values for all queries can be averaged to obtain a measure of the average performance of a search engine’s ranking algorithm over many queries.

###### Common Mistakes

When we are creating the training and test set, we have to be sure that:

* + We are using a realistic set of samples;
  + We have a balance of these samples, per each query, in the training set and the test set.

In particular, we have to pay attention to two possible conditions that can potentially skyrocket the NDCG average:

* + **One sample per query group**: for example, if there is only one item/song for a given query, the NDCG will be 1 (perfect) and regardless of the model, the average will increase misleadingly;
  + **One relevance label for all the samples in the query group**: for example, if all the songs for a given query have the same relevance (the same position on the chart).

Luckily, we did not have this kind of scenario, otherwise, it would be better to remove these queries.

###### Results

We have summarised in the following table the ndcg@10 values obtained after training the models. We created 4 models using different encoding techniques (for the Track Name feature) and different ways of grouping Position values for the Relevance Labels generation. The model where we applied doc2vec encoding and used relevance labels from 0 to 20 achieved the highest ndcg@10 value, hence the best performance.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/11/Schermata-2020-11-03-alle-09.58.01.png?fit=1814%2C1072&ssl=1)

## Final considerations

Data Preprocessing and Feature Engineering are crucial and are the most important steps in adapting an LTR project to a real-world scenario.

Language detection could be easier if we had song lyrics available; adding the language as an additional feature could be useful for improving model performance. We could also use this feature to create a query-document level feature (query dependent) and check the correlation between the Country (that represents our query) and the language of the song.

The difference between the performance of the models is minimal, and it would be interesting to evaluate the models online (we explain how to do this in our [online testing](https://sease.io/2020/04/the-importance-of-online-testing-in-learning-to-rank-part-1.html) blog post) to see if they are actually as similar as they seem or if the offline evaluation was unable to identify such dissimilarity.

## Future works

* + What would happen if we estimated the Relevance Labels from the song position values, after sampling our dataset into a Top 20 song chart (instead of 200)?

* + In addition, what might change if we directly used Stream counts (descending) to sort the results? Will we get the same order in the search results list (hence maximum NDCG)?!

* + We have also added to our to-do list the use of the library **SHAP** [[7]](https://github.com/slundberg/shap) to explain the model behaviour, in particular how each feature impacts the model’s output (you can see how to do this with our [Tree SHAP](https://sease.io/2020/07/explaining-learning-to-rank-models-with-tree-shap.html) blog post!).

We will address these topics in future blogs.

###### Take a look at [the talk about this](https://www.youtube.com/watch?v=Q2YkT3fQJOo&t=2s) project at our sixth London Information Retrieval Meetup

## Need Help With This Topic?​​

If you’re struggling with integrating Learning to Rank in your search system, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with integrating Learning to Rank in your search system, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)