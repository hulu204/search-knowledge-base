---
title: 'Train and Test Sets Split for Evaluating Learning To Rank Models – Part 2'
company: Sease
tag: 排序
date: 2022-09-13
url: https://sease.io/2022/09/how-to-split-your-dataset-into-train-and-test-sets-for-evaluating-learning-to-rank-models-2.html
account: 
origin: harvest3-202607
---
If you got here it is most likely because you want to discover the answer to the question we broke up with in the first part of this blog post. Welcome back!

Don’t you know what we are talking about?! We invite you to read [Part 1](https://sease.io/2022/07/how-to-split-your-dataset-into-train-and-test-sets-for-evaluating-learning-to-rank-models.html), where we cover **different techniques for partitioning data into subsets used for training and evaluating ‘Learning to Rank’ models**.

The goal of this blog post is to **focus more on ‘Learning to Rank’ datasets,** where documents are divided into several groups depending on the query; therefore, data splitting should be managed differently than other supervised machine learning algorithmic techniques, and that’s what we will cover in this blog post.

Let’s start again with the same question:

## What is important to consider in a 'Learning to Rank' scenario?

In a ‘Learning to Rank’ scenario, we have to take into consideration two important features: **the query and the relevance label**.

Each sample in the dataset is a **query-document**pair, represented in a vectorial format. The query column is identified by an Id used to group samples coming from the same user search; the relevance label, the target column, contains the relevance score that represents how relevant each sample is in the current query group.

## What is the most appropriate approach to handle queries (and relevance labels) when splitting data?

##### QUERY SPLITTING

In our old approach (addressed in our previous ‘learning to rank’ blogs) we were used to adopting the hold-out method (described in [Part 1](https://sease.io/2022/07/how-to-split-your-dataset-into-train-and-test-sets-for-evaluating-learning-to-rank-models.html)) splitting each query Id between the training and test sets, with the following “rules”:

* We kept the query Ids that have a number of observations under a certain threshold in the training set unless the test set contains less than 20% of the entire dataset. In this case, since the test set could be too small, we moved some of these undersampled queries to the test set (the query Ids with the highest number of observations). The reason is that queries with few search results are easier to rank, so if present in the test set they make the overall re-ranking task a bit straightforward, with higher metrics scores as a result that may not be indicative or represent the reality.
* We tried to keep the relevance labels equally distributed per query, manually selecting and moving to the test set 20% of all the observations for each relevance label. In doing this, we made sure all the relevance labels were in both sets.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-05-04-alle-09.32.52.png?fit=525%2C389&ssl=1)

*Train-test split example, splitting the query Ids*

In our [blog section](https://sease.io/blog-2/our-blog), you will surely find old posts describing this approach in more detail, if curious.

##### QUERY INTEGRITY

In our new approach, a different train-test split has been implemented in order to **keep samples from the same queries** **together** when creating the two sets.

In particular, we exploited the Sklearn [StratifiedGroupKFold](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html) method which attempts to create a training and a test set that preserve sample distribution for each query/relevance label as much as possible given the constraint of non-overlapping groups between splits. This means that it will try to **preserve our distribution of relevances** (in the range from 0 to 4 for example) **while keeping together queries**. This allows us to obtain a more balanced training and test set.

![](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-05-04-alle-09.33.01.png?fit=522%2C388&ssl=1)

*Train-test split example, keeping together the query Ids*

In [Part 1](https://sease.io/2022/07/how-to-split-your-dataset-into-train-and-test-sets-for-evaluating-learning-to-rank-models.html), we have included several code examples that use this approach, showing different data-splitting methods.

Here you can find another [example implementation](https://medium.com/predictly-on-tech/learning-to-rank-using-xgboost-83de0166229d), where they have used a different *[sklearn.model\_selection](https://scikit-learn.org/stable/modules/classes.html#module-sklearn.model_selection)* method to split data, according to a provided group, but that does not consider the relevance labels.

## Our observations

A valid and truthful test would be to show the model data it has never seen before! In fact, the effectiveness of a model must be evaluated in the worst-case scenario, therefore on data not used at training time.

Based on what we just said, **we believe both approaches should apparently be correct** as we make sure their test sets do not contain any documents/products present in the training sets.

However, **we chose the query integrity approach because we think it is more conceptually correct than the query splitting when talking about ranking**. If a system has to learn how to rank a list of documents, how could it best do it if some documents were removed from the list?!

In fact, notwithstanding we make sure all the relevance labels (related to a specific query) are in both sets in the query splitting, we are essentially removing from the training set some information on what the overall ranking of the query was, and therefore the model could be less able to generalize.

Furthermore, it may happen that some queries may have very few observations with high relevance, which will inevitably end up in one of the two sets only (or in training or in test).

The query splitting shouldn’t be entirely wrong but again we cannot be sure not to introduce an evaluation ‘bias’. It is true that the test set contains different data, but it still contains products that are indirectly related to the products in the training set belonging to the same query and this could falsify the performance results obtained.

###### What is your opinion? Which approach are you using?

Would love your thoughts, please share your opinion in the comments below!

## Conclusions

We expect that we have properly conveyed our doubts and observations regarding query splitting and query integrity in a ‘Learning to Rank’ scenario to openly discuss this important matter with our fantastic community.

See you in the next blog posts!

## Need Help With This Topic?​​

If you’re struggling with evaluating Learning to Rank models, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with evaluating Learning to Rank models, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)