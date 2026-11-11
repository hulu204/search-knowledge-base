---
title: 'Drop constant features: a real-world Learning To Rank scenario'
company: Sease
tag: 排序
date: 2021-06-16
url: https://sease.io/2021/06/drop-constant-features-a-real-world-ltr-scenario.html
account: 
origin: harvest3-202607
---
This tip just wants to advise you to **double-check your dataset features at the end of the pipeline before training a Learning to Rank (LTR) model**.

An essential part of data preprocessing which is considered to be one of the most time-consuming parts of any machine learning pipeline is **Feature Selection.** It is the process of removing redundant features and keeping only the necessary and relevant features to use in the model construction.

Columns in a dataset that have the same value in all the observations/rows are known as **Constant Features** and are considered redundant data. Will their removal affect your model performance? No! Those features which contain constant values cannot provide any useful information in predicting your response so it is good to remove them from the dataset not only to speed up training but also because, if not managed well, they can lead to numerical problems and errors (for example during the encoding phase).

This might seem obvious but after all the data pre-processing steps (i.e. the data collection, data modeling, and refining phases), you may end up again with some constant features (without even realizing it!) that should be ignored.

That’s why I want to show you one possible scenario that could occur during a real-world implementation.

## Case Study Example

Let’s imagine a Learning to Rank scenario.

We have to manage an E-commerce product catalogue. We collect all the interactions that users have with the website products (e.g. views, clicks, add to cart, sales..) and create a dataset consisting of <query, document> pairs (e.g. the filters selected by the users (*query-level*) and all the features of the product viewed/clicked/sold (document-level)). To keep it simple here is just an example with some features shown:

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-05-30-alle-15.21.50.png?fit=800%2C260&ssl=1)

To train our LTR model, we carefully design the vectorial representation of the domain documents and build accurately our training set to allow the model to perform as well as possible.

Most of the features have to be manipulated; especially to make the categorical features understandable by machine learning algorithms, we need basically to encode the original information the feature provides in a numeric form, without any loss if possible. There are different ways to encode categorical features and one possible approach is called One Hot Encoding [[1]](https://machinelearningmastery.com/why-one-hot-encode-data-in-machine-learning/):  
given a categorical feature with N distinct values, encode it in N binary features, and each feature will state if the category applies to the Document.

Imagine you have multi-valued categorical features like the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-05-28-alle-09.39.20.png?fit=258%2C300&ssl=1)

This feature, named ‘**productCategories**‘, is composed of an array of integers; for each interaction, it contains all the categories to which a product belongs. Using one-hot encoding, each N distinct value will then be encoded by adding N columns to the dataset, as you can see in the table below. This will happen for all the categorical features you have in your dataset. In addition, we use all the query-level features to generate the query\_ID ([check out this blog post about it](https://sease.io/2021/03/a-learning-to-rank-project-on-a-daily-song-ranking-problem-part-3.html)).

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-05-30-alle-15.02.29.png?fit=2670%2C468&ssl=1)

Before splitting the dataset into training and test sets, we use a method called *clean\_data\_frame\_from\_single\_label* which removes all the query\_ID with only one relevance label (read [Part3](https://sease.io/2021/03/a-learning-to-rank-project-on-a-daily-song-ranking-problem-part-3.html) and [Part4](https://sease.io/2021/05/a-learning-to-rank-project-on-a-daily-song-ranking-problem-part-4.html) blog post to understand why).

It could happen that the query\_ID = 3 (the third row of the table above) could be potentially removed during this phase since all the observations belonging to this query group have the same Relevance Label (e.g. equals to 1). We end up with the following data frame:

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-05-30-alle-15.02.41.png?fit=2708%2C440&ssl=1)

You can easily see that we have added two unnecessary features to the dataset: all the rows for these features are False since the row (or the rows) that contained True has been deleted by the clean\_data\_frame\_from\_single\_label method.

So, the features productCategories\_3483 and productCategories\_4639 have become unintentionally constant columns and, as already said, we should ignore columns from which no information can be gained before training the model.

###### Drop constant columns method

We need to add a method to check and delete all these features before the splitting phase:

```
				
					def drop_constant_columns(dataframe):
    constant_columns = [col for col in dataframe.columns if len(dataframe[col].unique()) == 1]
    dataframe_after_drop = dataframe.drop(constant_columns, axis=1)
    logging.debug('- - - - Number of constant features found : {:d}'.format(len(constant_columns)))
    logging.debug('- - - - Constant features removed :' + str(constant_columns))
    percentage = len(constant_columns) / len(dataframe.columns)
    if percentage &gt; 0.50:
        logging.warning('**** WARNING - 50% of the features have been removed')
    return dataframe_after_drop
				
			
```

###### **Model Training**

To give you proof of what has been explained so far, we have trained a Learning to Rank model once by keeping the constant features and another time by dropping them from the dataset. For the experiment, we used interaction log data collected from a generic e-commerce. The dataset after the pre-processing part contained a total of 6035 features.

Our method found 825 constant features (around 14%). We trained 2 models using LambdaMART [[2]](https://medium.com/rocket-travel/why-we-chose-lambdamart-for-our-hotel-ranking-model-45f84e22cec): keeping and removing the constant features.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-05-28-alle-09.40.20.png?fit=800%2C191&ssl=1)

We can confirm there is no difference in performance; the presence (or absence) of constant features has no effect on the target, in fact the metric ndcg@10 is the same in both models. If we delete the constant features, the model training lasts 6 minutes less. We can only benefit from their removal, in terms of time, memory, and other technical problems (encoding), especially if they are many.

To drop constant features, you may also be interested in other methods, check out the following links:

* + Sklearn: sklearn.feature\_selection.VarianceThreshold [[3]](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.VarianceThreshold.html)
  + H20: ‘ignore\_const\_cols’ parameter [[4]](https://docs.h2o.ai/h2o/latest-stable/h2o-docs/data-science/algo-params/ignore_const_cols.html)
  + R: drop\_constant\_cols [[5]](https://rdrr.io/cran/hutils/man/drop_constant_cols.html)

## Need Help With This Topic?​​

If you’re struggling with constant features in Learning to Rank, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with constant features in Learning to Rank, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)