---
title: 'Train and Test Sets Split for Evaluating Learning To Rank Models'
company: Sease
tag: 排序
date: 2022-07-20
url: https://sease.io/2022/07/how-to-split-your-dataset-into-train-and-test-sets-for-evaluating-learning-to-rank-models.html
account: 
origin: harvest3-202607
---
Offline testing is the most common evaluation method that can help you find the most promising models able to rank documents based on their estimated relevance before deployment.

For the offline evaluation of a Learning to Rank (LTR) model, after all the data preprocessing steps required to clean and structure the dataset and before the model construction, a **data split procedure** must be performed.

The entire dataset has to be divided into at least two parts: a **training set** and a **test set**. The first one is used by the machine learning algorithm to train the model. The second one is held and used to evaluate the performance of the trained model, by looking at different offline metrics which are indicators of the model’s expected performance on real data.

The purpose of this blog post is to illustrate how data splitting can be done and why it is important and required in machine learning (ML).

From a ‘Learning to Rank’ perspective, where each sample in the dataset is a query-document pair, the train-test split needs to be approached differently than other ML techniques since there are queries to consider.

That’s why Part 2 will follow up soon, about what is important to consider in a ‘Learning to Rank’ scenario and what is the most appropriate approach to handle queries when splitting data,

…stay tuned and happy learning!

## Why is data splitting so important?

Splitting the dataset is essential for two main reasons:

* to do an unbiased evaluation of model performances
* to detect and potentially reduce two very common machine learning problems called **underfitting** and **overfitting**

**Underfitting** takes place when a model is less complex than required and has poor performance with both training and test sets, while **overfitting** happens when a model performs really well on the training data but is unable to generalize to unseen examples. In general, the more complex the model, the greater the possibility it will be overfitted [[1](https://machinelearningmastery.com/overfitting-and-underfitting-with-machine-learning-algorithms/)].

## How many parts should I divide my dataset into?

The selection of splitting strategy can have a strong impact on the final model evaluation and it is essentially influenced by two factors:

* the amount of data available
* the tool you are using to train the model

There are several methods used to assess how well a machine learning model performs on unseen data, with their pros and cons. It is not the purpose of this blog post to go into the details of each technique [[2](https://towardsdatascience.com/understanding-8-types-of-cross-validation-80c935a4976d)] but we will just briefly describe the most used ones:

##### HOLD-OUT

The hold-out is the simplest way to split the dataset into two partitions: **training** and **test** sets. The training set is used to train the model and then the effectiveness of the model has to be evaluated on “new” data (test set) to estimate its ability in making predictions on data not used during the training phase.

This method works well for less complex cases and when there is no need to tune the model hyperparameters, whose values can directly affect and control the learning process; in this second scenario, it is also necessary to hold out a third subset, called **validation** set.

The main difference between validation and test set is that the former is used to evaluate the models during the training process and select the best one, while the latter is used to evaluate the accuracy of the final model before the deployment.

*The hold-out code example in an LTR scenario:*

```
				
					min_diff = len(data_set)
min_train_idx = []
min_test_idx = []
groups_split_object = StratifiedGroupKFold(n_splits=int(len(data_set)/test_set_size))
for train_idx, test_idx in groups_split_object.split(data_set, data_set['relevance_label'], data_set['query_id']):
    diff = abs(len(test_idx) - test_set_size)
    if diff &lt; min_diff:
       min_diff = diff
       min_train_idx = train_idx
       min_test_idx = test_idx
       if diff == 0:
          break
interactions_train = data_set.iloc[min_train_idx]
interactions_test = data_set.iloc[min_test_idx]
				
			
```

*N.B.  
In this example, we used the Sklearn ‘StratifiedGroupKFold’ method [[3](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.StratifiedGroupKFold.html#sklearn.model_selection.StratifiedGroupKFold)] without effectively performing the k-fold cross-validation and we will explain the reason for this choice in Part 2 of this blog post*“*.*

Sometimes it may be necessary to use the easiest approach to simply create two sets and leave a separate test set for multiple purposes, such as making further checks and comparisons with other models.

Anyway, the **hold-out approach has some limitations**, especially when using a very small dataset. It is very sensitive to how data ends up in each set, and creating an unbalanced test set can lead to evaluation results that do not reflect real model behaviour.

That’s how k-fold cross-validation comes to our aid and why is usually preferred over hold-out.

##### K-FOLD CROSS-VALIDATION

**K-fold cross-validation** is a resampling procedure that randomly splits the entire data into *k* number of similar-sized subsets (called folds).

The model is fitted using the *k* – 1 (*k* minus 1) folds, that correspond to the training set, and validated using the remaining *k*th fold. The above process is repeated by changing the kept-out fold (from 1 to *k*), making sure that every *k*-fold is being used as a test set. The final performance metrics are computed by averaging the performance on each fold.

![K-fold cross-validation](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-04-24-alle-10.29.59.png?fit=800%2C439&ssl=1) 

K-fold cross-validation example (k=5)

It is surely more time-consuming since it effectively needs to repeat the process of training and testing a model multiple times, but it is definitely considered more robust because it matters less how the data gets divided.

The choice of *k* does not follow a formal rule but has to be done carefully. If *k* is too small the situation is similar to the simple train-test split approach with high bias and low variance, while if *k* is too large it means less bias but also higher variance and higher running time. Typically the most used *k* values are 5 or 10 since it has been shown that these values reach a good bias-variance trade-off.

*The k-fold cross-validation code example in an LTR scenario:*

```
				
					stratified_grouped_cv = StratifiedGroupKFold(n_splits=num_splits_cv)

logging.info('- - Cross-validation split info')
for train_idx, test_idx in stratified_grouped_cv.split(data_set, data_set_label_column, data_set_query_id_column):
    logging.debug("Training set length: " + str(len(data_set_label_column.iloc[train_idx])))
    logging.debug("Training set distinct query Ids: " + str(len((data_set_query_id_column.iloc[train_idx].unique()))))
    logging.debug("Test set length: " + str(len(data_set_label_column.iloc[test_idx])))
    logging.debug("Test set distinct query Ids: " + str(len((data_set_query_id_column.iloc[test_idx].unique()))) + '\n')
				
			
```

*In this example, we used the Sklearn ‘StratifiedGroupKFold’ method*, in which we pass the number of folds as a parameter (for example, num\_splits\_cv = 5)

Even **k-fold cross-validation has weaknesses**. Using the same dataset and cross-validation procedure for both hyperparameter tuning and general model performance estimation can lead to overly optimistic results.

That’s why **nested cross-validation** comes into the picture [[4](https://mlfromscratch.com/nested-cross-validation-python-code/)].

##### NESTED CROSS-VALIDATION

This method is also called *double cross-validation* since it is made of two independent but nested loops:  
– an **inner loop** (1), for model selection/hyperparameter tuning  
– an **outer loop** (2), to estimate the testing error of tuned models

![nested cross-validation](https://i0.wp.com/sease.io/wp-content/uploads/2022/12/Schermata-2022-04-24-alle-11.43.04.png?fit=800%2C481&ssl=1) 

Nested cross-validation example (Outer loop k=5, Inner loop k=3)

Both loops execute cross-validation and it is common to use a smaller value of *k* in the inner loop (*k=3)* than in the outer loop (*k=5*), as shown in the picture above. The outer loop is repeated 5 times, generating five different training and test sets, resulting from the entire dataset. For each iteration, the outer training set is further split, in this case, into 3 folds and the inner loop is, in turn, repeated 3 times. The inner layer will return only the model with the best hyperparameters to the outer loop, which will use its test set for estimating the quality of the model. After varying the outer test sets, you will finally get 5 different estimates that can be averaged to obtain the final performance.

Thus, when you want to perform model selection and generalization error estimation, the advantage of this method lies in the fact that you can separate the two tasks by using two different sets for each task, so the entire process will give you a better estimation of the model performance in a real-world scenario.

The use of **nested cross-validation is not recommended when the dataset is too large** since it dramatically increases the training time.

*The nested cross-validation**code example in an LTR scenario:*

```
				
					inner_cv = StratifiedGroupKFold(n_splits=num_splits_inner_cv)
outer_cv = StratifiedGroupKFold(n_splits=num_splits_outer_cv)

logging.info('- - - - Nested cross-validation split info')
outerK = 1
for train_outer_idx, test_outer_idx in outer_cv.split(data_set, data_set_label_column, data_set_query_id_column):
    logging.info('- - Outer: ' + str(outerK)
    logging.debug("Training set length: " + str(len(data_set_label_column.iloc[train_outer_idx])))
    logging.debug("Training set distinct query Ids: " + str(len((data_set_query_id_column.iloc[train_outer_idx].unique()))))
    logging.debug("Test set length: " + str(len(data_set_label_column.iloc[test_outer_idx])))
    logging.debug("Test set distinct query Ids: " + str(len((data_set_query_id_column.iloc[test_outer_idx].unique()))) + '\n')
    training_outer = data_set.iloc[train_outer_idx]
    training_label_outer = data_set_label_column.iloc[train_outer_idx]
    training_query_id_outer = data_set_query_id_column.iloc[train_outer_idx]
    outerK = outerK + 1
    innerK = 1
    for train_inner_idx, test_inner_idx in inner_cv.split(training_outer,training_label_outer,training_query_id_outer):
        logging.info('- - Inner: ' + str(innerK))
        logging.debug("Training set length: " + str(len(training_label_outer.iloc[train_inner_idx])))
        logging.debug("Training set distinct query Ids: " + str(len((training_query_id_outer.iloc[train_inner_idx].unique()))))
        logging.debug("Test set length: " + str(len(training_label_outer.iloc[test_inner_idx])))
        logging.debug("Test set distinct query Ids: " + str(len((training_query_id_outer.iloc[test_inner_idx].unique()))) + '\n')
        innerK = innerK + 1
				
			
```

*Even in this example, we used the Sklearn ‘StratifiedGroupKFold’ method*, *in which we pass the number of folds as a parameter, for both the inner and outer loops.*

## What should the split ratio be like?

The optimal data splitting always depends on factors such as the size of the dataset and the structure of the model.

The training set should not be too small otherwise the model will not have enough data to learn; on the other hand, even the validation and the test sets should not be too small otherwise the evaluation metrics will have a large variance and will not lead to the proper model tuning or to a value that reflects the true model performance.

**So how big should they be?**

As mentioned above,**the ratio is affected by the size of the entire dataset**:

Common ratios when using the hold-out method are:

* 80% train, 20% test
* 80% train, 10% dev, 10% test
* 70% train, 30% test
* 60% train, 20% dev, 20% test

We have to say that these rules of thumb in machine learning were pretty reasonable when data set sizes were just smaller (thousand samples in total); but in the modern machine learning era (especially when using Deep Learning), the guidelines to help set up validation and test sets have a bit changed and those common ratios are no longer applied.

Nowadays, when dealing with big data (million/billion samples) it seems that if you can gather enough samples for the validation and test set (>= 10.000 samples each, for example), it is a good set size that should be big enough to give high confidence in the overall performance of your system, regardless of the percentage achieved.

In fact, it’s pretty reasonable to use much smaller than 20 or 30% of the data for the validation and test sets and leave more samples to train the model.[[5](https://analyticsindiamag.com/best-practices-on-setting-up-development-and-test-sets-for-ml/)]

Also, to ensure that the training and test sets are representative of the original dataset, for learning to rank models, as well as for classification models, a pure random split is not always the right approach: we need to guarantee that the frequency distribution of the queries and relevance labels is approximately equal within both sets.

## What is important to consider in a ‘Learning to Rank’ scenario?

When you are dealing with ‘Learning to Rank’, especially list-wise approaches, the problem arises of how to properly manage the data splitting, considering that are grouped by the query.

Are you curious to find out more about this topic? See you in the next blog post!

## Conclusions

We hope this blog will help you understand how to perform data splitting and why it is very important for offline evaluation of Learning to Rank models.

## Need Help With This Topic?​​

If you’re struggling with offline evaluation of a Learning to Rank (LTR) model, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with offline evaluation of a Learning to Rank (LTR) model, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)