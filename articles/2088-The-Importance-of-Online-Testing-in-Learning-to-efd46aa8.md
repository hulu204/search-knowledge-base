---
title: 'The Importance of Online Testing in Learning to Rank - Part 1'
company: Sease
tag: 排序
date: 2020-04-29
url: https://sease.io/2020/04/the-importance-of-online-testing-in-learning-to-rank-part-1.html
account: 
origin: harvest3-202607
---
You have just trained a **learning to rank model** and you now want to know how it performs.

You can start by looking at the evaluation parameters returned by the train on the test set, but you are still not sure of which will be the impact of using it in a real website.

This is where online testing comes in. It remains **the optimal way to check how your model performs in a real scenario** and can give you the necessary information to evaluate, improve and better understand the behaviour of your model.

**In this blog post, I present you the online testing for learning to rank.**   
I talk about **the advantages** of this approach and **why it should be used,** finally, I show you **how it can be implemented** and **which mistakes to avoid** during this realization.

In this first Part, I talk about the state of the art, while in Part 2 I show you [how to implement interleaving](https://sease.io/2020/05/online-testing-for-learning-to-rank-interleaving.html).

## In the Industry

Unfortunately, there are still many industries today that don’t use online testing in learning to rank evaluation. Maybe they don’t know it exists, or they don’t have the right tools to do it; potentially they don’t have the competence to understand the results.   
In any case, this is a shame because **online testing is vital for the correct tuning of the model and its improvement**.

We can surely rely on offline evaluation, checking the performance of the model on the test set or through the analysis of different offline metrics, but we can’t be sure what the impact will be on the website.

Several problems are hard to detect with an **offline evaluation**.

> With a wrong Test Set is possible to obtain model evaluation results that aren't reflecting the real model improvement
>
> - Sease
> [Tweet me](https://twitter.com/intent/tweet?text=With+a+wrong+Test+Set+is+possible+to+obtain+model+evaluation+results+that+aren%27t+reflecting+the+real+model+improvement+%E2%80%94+-+Sease&url=https%3A%2F%2Fsease.io%2F2020%2F04%2Fthe-importance-of-online-testing-in-learning-to-rank-part-1.html)

First of all, it could happen that we don’t correctly train and/or test the model. If we make mistakes in creating the training and/or test set we will have unreliable results that can be misunderstood.   
With a wrong test set, it is possible to obtain better model results that don’t reflect a real model improvement. In this case, we have an issue that can’t be caught using the offline evaluation.

###### WHEN IS A TEST SET WRONG?

When it doesn’t represent and generalise well the ranking problem.  
Some examples:

* + ***One sample** per query group*: ranking a single result for a query is not a ranking problem at all.
  + ***One relevance label** for all the samples of a query group*: so whatever ranking the model does, the offline evaluation metric will be the same.
  + *Starting from the **data set***: which interactions do you consider for the training and which for the test? The split in training and test sets is a very important phase that needs to be studied in depth. Ideally, we would like to create two sets that follow the same probability distribution in terms of queries and relevance labels.

Another problem is finding a direct correlation between the offline evaluation metrics and the parameters we consider for the online model performance.   
It isn’t that obvious and neither simple to understand how an improvement in the offline metrics will reflect on page views, clicks, sales and revenues.

> Relying on generated relevance labels can be a problem.
> These aren't always reliable and doesn't always reflect the real users needs.
>
> - Sease
> [Tweet me](https://twitter.com/intent/tweet?text=Relying+on+generated+relevance+labels+can+be+a+problem.%0AThese+aren%27t+always+reliable+and+doesn%27t+always+reflect+the+real+users+needs.+%E2%80%94+-+Sease&url=https%3A%2F%2Fsease.io%2F2020%2F04%2Fthe-importance-of-online-testing-in-learning-to-rank-part-1.html)

The most commonly used technique for offline evaluation is the **Cranfield** one.   
In this approach, a group of experts create a set of relevance judgments starting from a selected set of documents. In particular, they assign a relevance label to each document of the selected set. The application of this paradigm can bring to two main issues:

* + The ***effort*** required for the relevance set creation. This is a very expensive phase.
  + Relying on generated relevance labels. These ***aren’t always reliable*** and doesn’t always reflect the real users’ needs.

If we want to overcome these issues we have to pass to the **online testing**.

## Online Testing

As already said before, using online testing can lead to many advantages:

* + The ***reliability*** of the results. In this approach, we can directly observe the user’s behaviour and, from this, understand what are documents of greatest interest to the user.
  + Give a ***direct interpretation*** of the results. With online evaluation, we can directly see what are the consequences of the model in terms of number of page views, clicks, sales or revenues.
  + We can also better understand the ***model behaviour***. We can see how the user interacts with the model and figure out how to improve it.

**These benefits do not come without effort, but they are worth it.**

At the moment, in the world of learning to rank and beyond, two types of online testing are widely spread in the industry: **A/B testing** and [**Interleaving**](https://sease.io/2020/05/online-testing-for-learning-to-rank-interleaving.html).

## A/B Testing

Let’s start taking a look at how A/B testing works.

Since we are talking about learning to rank, let’s say you have two trained learning to rank models: ***model A*** and ***model B***. These models aren’t identical and you want to compare them to find the best one.

**A/B testing allows you to make this comparison**. In particular, it allows you to **divide your query traffic into two groups**. The first group of users interact with the website using ***model A***, while the second one interacts with the website using ***model B***. In this way, we can observe the user behaviour in both scenarios and look at our target metrics like clicks, sales, and revenues, to understand which model performs better.

This is a great tool, it gives us useful information and above all it relies on real user interactions that should reflect the real user’s needs.

Even if A/B testing is great, we have to be very careful in how we implement it.

###### What not to do in A/B Testing

Let’s say we have a website, in which we use our learning to rank model for the query search pages. Suppose we have 2 pages:

1. 1. *One is the homepage*. Here we show a few interesting new documents that can be directly bought. These documents are static and **are not ordered by the learning to rank model**.
   2. *One is the search page*. Here we can make a query and search through the results the most interesting documents for us. These documents are ranked by our learning to rank model.

> When A/B Testing we need to make sure we consider only the interactions coming from search result pages ranked by the models we are comparing.
>
> - Sease
> [Tweet me](https://twitter.com/intent/tweet?text=When+A%2FB+Testing+we+need+to+make+sure+we+consider+only+the+interactions+coming+from+search+result+pages+ranked+by+the+models+we+are+comparing.+%E2%80%94+-+Sease&url=https%3A%2F%2Fsease.io%2F2020%2F04%2Fthe-importance-of-online-testing-in-learning-to-rank-part-1.html)

When testing we have to make sure that all the results we are considering, come from the *search page* and not from the *homepage*.  
A wrong analysis could indeed lead to a wrong conclusion on models’ performances.

In particular, I would like to highlight two possible situations:

* + We conclude that *model A* is better than *model B* when it is the opposite.
  + We correctly conclude that *model A* is better than *model B*, but we are unable to identify the percentage of improvement.

Let’s see the **first scenario**.

*Suppose we are analyzing **model A**. We obtain 10 sales from the homepage and 5 sales from the search page.*   
*Then suppose to analyze **model B**. We obtain 4 sales from the homepage and 10 sales from the search page.*

If we look only at the total we will see: 15 sales from *model A* and 14 sales from *model B*, concluding that *model A* is the best one. This is true for the homepage (10 sales > 4 sales), but not for the search page (5 sales < 10 sales) where we are using the learning to rank model.

**So what do we make of that?**

In this way, we wrongly assert that *model A* is the best one, while we can clearly see that in the search page *model B* performs better.  
We aren’t therefore evaluating the model on the page where it acts, but we draw conclusions led by the homepage where the model is not involved.

The same misunderstanding can arise when the improvement happens only on the homepage and not on the search page where the models are equivalent. Below you find an example of the situation.

*Suppose we are analyzing **model A**. We obtain 10 sales from the homepage and 10 sales from the search page.*   
*Then suppose to analyze **model B**. We obtain 5 sales from the homepage and 10 sales from the search page.*

Here, if we look only at the total sales, we can see that *model A* obtains 20 sales while *model B* obtains 15 sales. In this case, we will conclude that *model A* is better than *model B*.

**So what do we make of that?**

If we simply look at the results for the search page, this isn’t true because both obtain the same number of sales (10).   
The improvement is due to the homepage, which doesn’t use the model, but we could wrongly attribute it to the model performance.

Let’s now see the **second scenario**.

*Suppose we are analyzing **model A**. We obtain 12 sales from the homepage and 11 sales from the search page.*  
*Then suppose to analyze **model B**. We obtain 5 sales from the homepage and 10 sales from the search page.*

Here, if we look at the total sales, we can see that *model A* obtains 23 sales while *model B* obtains 15 sales. In this case, we will conclude that *model A* is better than *model B*.

**So what do we make of that?**

This is true because, even looking only at the search page, *model A* obtained more sales than *model B* (11 sales > 10 sales). But… how much was the improvement? Looking at the total we see that *model A* obtains 8 more sales than *model B*, a great improvement! But in reality, looking only at the search page we can see that *model A* obtains just 1 sale more than *model B*, not such a big difference.

> It is important to filter the interactions during testing.
> We have to consider only interactions that are really related to the models under evaluation.
>
> - Sease
> [Tweet me](https://twitter.com/intent/tweet?text=It+is+important+to+filter+the+interactions+during+testing.%0AWe+have+to+consider+only+interactions+that+are+really+related+to+the+models+under+evaluation.+%E2%80%94+-+Sease&url=https%3A%2F%2Fsease.io%2F2020%2F04%2Fthe-importance-of-online-testing-in-learning-to-rank-part-1.html)

These examples show that it is important to filter our interactions during testing. We have to consider only interactions that are related to the model if we want to evaluate it. Considering also the others, like the ones on page one, brought an addition of noise that can hide the real model performances.

## Interleaving

A/B testing is widely used in industry, it’s very useful and it isn’t too complicated to implement.   
For these reasons, this approach has been the focus of a large number of studies with the purpose of improving the current implementation.   
These studies led to a new similar approach called: **interleaving**.

Also in this kind of approach, two models are compared. The main difference with A/B testing is that, here, we directly compare the two models showing both their results to the same user at the same time.  
Let’s explain more in detail how it works:

> Interleaving prevents the chance of exposing users to a bad model for the entire duration of the test experiment.
>
> - Sease
> [Tweet me](https://twitter.com/intent/tweet?text=Interleaving+prevents+the+chance+of+exposing+users+to+a+bad+model+for+the+entire+duration+of+the+test+experiment.+%E2%80%94+-+Sease&url=https%3A%2F%2Fsease.io%2F2020%2F04%2Fthe-importance-of-online-testing-in-learning-to-rank-part-1.html)

There are several advantages to interleaving with respect to A/B testing:

* + It reduces the problem with users’ variance due to their separation into groups (group A and group B).
  + It is more sensitive in the comparison between models.
  + It requires less traffic.
  + It requires less time to achieve reliable results.
  + It doesn’t necessarily expose a bad model to a subpopulation of users

Let’s see how interleaving works and how it achieves these improvements.

##### How interleaving works

Suppose we have two learning to rank models called: ***model\_A*** and ***model\_B***.  
Given a query ***q*** each model responds with a ranked list of documents: ***lA*** and ***lB***.  
At this point, instead of returning the list *lA* to a group of users A and the list *lB* to a group of users B, **a unique result list *lI* is created and returned to the user**.   
There isn’t anymore a separation of the query traffic, each user is exposed to this result list created from both models with the same interleaving approach.  
**This unique list will therefore contain search results from both *model\_A* and *model\_B***.

There are several ways of implementing this kind of list, **all trying to be as fair as possible**.

*What do we mean by **fair**?*

This concept is highly related to the choice of the search results.   
Ideally, we would like the list **to contain an equal number of documents from both models**, so the preference of one model with respect to the other doesn’t depend on the number of shown items.   
Secondly, we would like that **the position of the shown items doesn’t influence the preference of the user for one of the two models**. If we have all the documents from *model\_A* in the top 10 positions and all the documents from *model\_B* in the underlying positions, it is possible that documents from B aren’t chosen only because of their low ranks.

The first survey of how testing learning to rank models happens in the industry and how it looks in the state of the art ends here, but if you’re curious about learning more details about how this can be implemented let’s meet in [Part 2](https://sease.io/2020/05/online-testing-for-learning-to-rank-interleaving.html)!

## Need Help With This Topic?​​

If you’re struggling with A/B Testing in Learning to Rank, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with A/B Testing in Learning to Rank, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)