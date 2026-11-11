---
title: 'Explaining Learning to Rank Models with Tree Shap'
company: Sease
tag: 排序
date: 2020-07-15
url: https://sease.io/2020/07/explaining-learning-to-rank-models-with-tree-shap.html
account: 
origin: harvest3-202607
---
A common problem with machine learning models is their **interpretability** and **explainability**.  
We create a dataset and we train a model to achieve a task, then we would like to understand **how** the model obtains those results. This is often quite difficult to understand, especially with very complex models.

In this blog post, I would like to present a very useful library called **SHAP**. In particular, I will write about its amazing tools and I will explain to you how to interpret the results in a learning to rank scenario.

## What is Tree SHAP?

> Tree SHAP gives an explanation to the model behavior, in particular how each feature impacts on the model's output.
>
> Sease
> [Tweet me](https://twitter.com/intent/tweet?text=Tree+SHAP+gives+an+explanation+to+the+model+behavior%2C+in+particular+how+each+feature+impacts+on+the+model%27s+output.+%E2%80%94+Sease&url=https%3A%2F%2Fsease.io%2F2020%2F07%2Fexplaining-learning-to-rank-models-with-tree-shap.html)

**Tree SHAP** is an algorithm that computes SHAP values for tree-based machine learning models.  
**SHAP (SHapley Additive exPlanations)** is a game-theoretic approach to explaining the output of any machine learning model. It connects optimal credit allocation with local explanations using the classic Shapley values from game theory and their related extensions [1], [[2]](https://github.com/slundberg/shap).

Tree SHAP allows us to explain the model behaviour, in particular, how each feature impacts the model’s output. Here each output/prediction is seen as a sum of the contribution of each feature.

It provides several tools to deeply inspect the model predictions, in particular, through detailed plots.  
These plots give us a [[4]](https://towardsdatascience.com/explain-your-model-with-the-shap-values-bc36aac4de3d):

* + **Global interpretability**: through summary plots. These reflect the **general behaviour of the features in the model** and allow us to understand which features most impact the final output and how much.
  + **Local interpretability**: through force/dependence plots. These show **the specific behaviour of the features in a single model prediction**, allowing us to understand all their single impacts on the final output.
  + **It can be used for several machine learning models**: SHAP provides several explainers that cover most of the machine learning methods. These are a collection of classes, where each class represents an explainer for a specific machine learning algorithm. The explainer is the object that allows us to understand the model behaviour.

## Tree SHAP Plots

Tree SHAP provides us with several different types of plots, each one highlighting a specific aspect of the model. The available plots are:

* + *Summary plot*
  + *Force plot*
  + *Dependence plot*
  + *Decision plot*

These plots are generated after the computation of the SHAP values. These values measure **how** and **how** **much** each feature impacts the model.  
In particular, they are computed through a method that looks at the marginal contribution of each feature. What this method does, to evaluate the impact of a feature is to see how the output of the model changes after the feature removal. To evaluate the change it averages the results of the differences in predictions over all possible orderings of the other features [1], [[4]](https://towardsdatascience.com/explain-your-model-with-the-shap-values-bc36aac4de3d).

##### Interpretation

Suppose to be in a **learning to rank scenario**.

We have to manage a book catalogue on an e-commerce website. Each book has many different features such as publishing year, target age, genre, author, and so on.  
A user can visit the website, make a query through some filter selection on the books’ features, and then inspect the obtained search result page.  
To train our model, we collect all the **interactions** that users have with the website products (e.g. views, clicks, add to cart, sales..) and create a dataset consisting of **<query, document> pairs** (e.g. the filters selected and the features of the product viewed/clicked/sold/…).

We obtain something like this, where ***s\_feature*** indicates the selected feature from the website filters and ***book\_feature*** the feature of the product with which the user interacted:

| Interactions | s\_genre | s\_price\_range | book\_genre | book\_author | book\_price |
| --- | --- | --- | --- | --- | --- |
| interaction\_1 | thriller | [15-20] | thriller | Brown | 18 |
| interaction\_2 | mystery | [5-10] | mystery | Christie | 8 |
| interaction\_3 | fantasy | [10-15] | fantasy | Asimov | 15 |

In order to use them, these features need to be manipulated.   
In particular, the categorical features need to be encoded. We do this using the one-hot encoding, which creates a column for each value of each categorical feature. In this way, we will obtain something like this for the *genre* column:

| Interactions | is\_genre\_thriller | is\_genre\_mystery | is\_genre\_fantasy |
| --- | --- | --- | --- |
| interaction\_1 | True | False | False |
| interaction\_2 | False | True | False |
| interaction\_3 | False | False | True |

Now we are ready to explain the Tree SHAP plots.

###### Summary plot

The first plot I would like to analyze is the **summary** **plot**.  
This can give us global information on the interpretability of the model.

As we can see from the picture below, the plot represents:

* + the most important feature of the model on the **y-axis** in descending order (at the top the most important one).
  + the SHAP value on the **x-axis**.
  + the feature value with **colours**. A high value is represented with red, while a low value with blue.
  + also here each **point** represents a prediction result.

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/07/summary_shap_importance.png?fit=989%2C805&ssl=1)

From the example we can see that:

* + the higher the total number of reviews the higher the positive impact on the relevance
  + the higher the review average the higher the positive impact on the relevance
  + if it is an ebook it is more relevant in most of the cases
  + it the book genre is fantasy it has a negative impact on the relevance

There are also features for which there isn’t a clear behaviour with respect to their values, for example, the book sales, the book price and the publishing year.  
From the plot, we can also see how much each feature impacts the model by looking at the x-axis with the SHAP value.

Another type of summary plot is the **bar** one:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/07/summary_shap_importance_bars.png?fit=998%2C799&ssl=1)

This represents the same concept as the other using a bar representation with the mean(|SHAP value|) in the **x-axis**.

###### Force plot

The second plot I would like to analyze is the **force plot**.

This plot allows us to give **explainability** to a **single** **model** **prediction**.  
Suppose to take an interaction like:

| Interaction | is\_publishing\_year\_2020 | is\_for\_age\_40 | is\_**ebook** | is\_**new\_arrivals** |
| --- | --- | --- | --- | --- |
| interaction\_4 | False | False | False | False |

The corresponding plot will be:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/06/explanation_prediction_0_with_label_0-1.png?fit=1570%2C362&ssl=1)

From the plot we can see:

1. 1. The **model** **output** **value**: -4.54
   2. The **base** **value**: this is the value that would be predicted if we didn’t know any features for the current output [1].
   3. The **impact** of each feature on the output.

In particular, we can see some red and blue arrows associated with each feature.  
Each of these arrows shows:

* + **how** **much** the feature impacts the model: the bigger the arrow, the bigger the impact.
  + **how** the feature impacts the model: a red arrow increases the model output value while a blue arrow decreases the model output value.

In the plot we represent, the fact that the book has not been published in the year 2020 and doesn’t have a target age range of [30-50] impacts positively on the output, while not being an ebook, not being a new arrival and not having a legend genre, impact negatively.

Since we are talking about learning to rank, the model output represents the SHAP **score** of the book. The scores of all the books in answer to a specific query are used to rank the products. Therefore if our model predicts:

| Interactions | query | book | **SHAP score (model output)** |
| --- | --- | --- | --- |
| interaction\_5 | q1 | book\_1 | -2.91 |
| interaction\_6 | q1 | book\_2 | -4.54 |
| interaction\_7 | q1 | book\_3 | -1.85 |

We will have, for the query ***q1***, the **ranking**:

1. 1. book\_3 (-1.85)
   2. book\_1 (-2.91)
   3. book\_2 (-4.54)

Since -4.54 < -2.91 < -1.85.

An interesting aspect of this plot emerges from the comparison of the outputs for a specific query.  
Looking at how each book is scored inside a query, we can detect the differences between products in terms of features’ values.

If we want a global representation of the previous predictions, we can use a variant of the force plot:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/06/force_plot_1.png?fit=1205%2C398&ssl=1)

Here we can see the predictions made before (one for each interaction) placed vertically (rotated at 90°) and side by side.

###### Dependence plot

Another plot useful for local interpretability is the **dependence plot**.  
This plot compares a chosen feature with another one and shows if these two features have an **interaction** **effect**.

As a first example, I reported here the dependence plot between age and education-num for a model trained on the classic UCI adult income dataset (which is a classification task to predict if people made over 50k in the 90s) [[5]](https://slundberg.github.io/shap/notebooks/plots/dependence_plot.html).

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/07/dependence_plot.png?fit=987%2C648&ssl=1)

Figure from [[5]](https://slundberg.github.io/shap/notebooks/plots/dependence_plot.html)

Here each **point** corresponds to a prediction. In the **x-axis,** we have the *Age* while in the **y-axis** we have the predicted SHAP value (how much knowing that feature’s value changes the output of the model for that sample’s prediction).   
The **colour** represents the *Education-Num*, therefore we can see if having a specific age AND having a specific education-num impact positively or negatively on the output.  
From the plot, we can deduce that 20-year-olds with a high level of education are less likely to make over 50k than 20-year-olds with a low level of education, while 50-year-olds with a high level of education are more likely to make over 50k than 50-year-olds with a low level of education. This suggests an interaction effect between Education-Num and Age [[5]](https://slundberg.github.io/shap/notebooks/plots/dependence_plot.html).

This kind of relationship isn’t always present between features as we can see, from our book scenario, for the features ***book\_price*** and ***is\_genre\_fantasy***:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/06/dependence_plt_book_price_with_is_fantasy.png?fit=650%2C459&ssl=1)

###### Decision plot

The last plot I would like to present is the **decision plot**.

This plot shows how the prediction changes during the decision process. In the **y-axis,** we have the features ordered by importance as for the summary plot. In the **x-axis,** we have the output of the model.

Moving from the bottom of the plot to the top, SHAP values for each feature are added to the model’s base value. This shows how each feature contributes to the overall prediction [[5]](https://slundberg.github.io/shap/notebooks/plots/dependence_plot.html).

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/07/decision_plot.png?fit=998%2C824&ssl=1)

Here each line represents a single prediction, so consider this one:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/06/explanation_prediction_decision_plot.png?fit=1570%2C362&ssl=1)

If we just plot the correspondent line we will have:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/06/decision_plot_one_prediciton.png?fit=998%2C824&ssl=1)

Here the value of each feature is reported in parentheses.  
From the graph we can see that ***is\_for\_age\_40-50*** False, ***is\_author\_Asimov*** True, ***is\_publishing\_year\_2020*** True, ***is\_book\_genre\_in\_cart*** 6 and ***book\_reviews*** 992 impact positively to the model, while the other features impact negatively.

##### Pros

What I would like to highlight with this post is the usefulness of this tool.  
Tree SHAP allows us to:

* + Interpret **how** the model **makes** a **specific** **decision** through the force and decision plots.
  + **Compare** the **predictions** belonging to a common query printing all the related force plots. Therefore to make a query analysis.
  + Understand the **relative** **importance** of the features through the summary plot.
  + See **how** the value for **each** **feature** **impacts** the model, if positively or negatively, through the summary plot.
  + Understand if we have a training set and a model that reflects our scenario.
  + Analyze if we correctly store the interactions used or if there are any anomalies.
  + Identify which features to prioritize for improvements based on their importance.

##### To be aware of

When using this tool we have to be aware of a couple of things:

1. 1. The **measure** of the **importance** of the features is executed considering the totality of the interactions as a unique set. The interactions aren’t considered grouped by query. Therefore we can’t directly see the importance of the features within each query, but we have to extrapolate all the interactions with the same query before and then execute the plot just on them.
   2. The **output** of the model is not the relevance label. The output is just a measure of the relevance of that product for that query, but it is a value generated from the library that doesn’t reflect the relevance labels we use in training/testing. Despite this, the score represents the same concept if we look at the relative relevance between products. A product with a score of 2 for the query one is more relevant with respect to another product with a score of 0 for the same query.
   3. From what we said in the previous point, we have to pay attention to how we interpret the score. A negative value doesn’t directly mean that the document is not relevant. We always have to consider it in relation to the other products in the same query.

## Future Works

We have added to our to-do list also the integration of the TreeSHAP library in Solr.  
Since Solr allows to use a learning to rank model for the re-ranking of the documents, it could be very useful to analyze directly the models’ behavior inside the platform.

You can find the first opened Jira issues here [[8]](https://github.com/slundberg/shap/issues/127)[[9]](https://github.com/slundberg/shap/pull/129).

###### References:

Lundberg, Scott M., and Su-In Lee. “A unified approach to interpreting model predictions.” *Advances in neural information processing systems*. 2017. [1]   
Why Tree SHAP [[3]](https://towardsdatascience.com/interpretable-machine-learning-with-xgboost-9ec80d148d27)

Other useful links:

* + Decision plot [[6]](https://slundberg.github.io/shap/notebooks/plots/decision_plot.html)
  + Global interpretation, not per query problem [[7]](https://github.com/slundberg/shap/issues/570)

## Need Help With This Topic?​​

If you’re struggling with learning to rank and Tree SHAP, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with learning to rank and Tree SHAP, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)