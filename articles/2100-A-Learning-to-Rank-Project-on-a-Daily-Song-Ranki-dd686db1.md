---
title: 'A Learning to Rank Project on a Daily Song Ranking Problem – Part 3'
company: Sease
tag: 排序
date: 2021-03-25
url: https://sease.io/2021/03/a-learning-to-rank-project-on-a-daily-song-ranking-problem-part-3.html
account: 
origin: harvest3-202607
---
Here we are again, with a new Learning to Rank implementation.

Probably if you are reading this blog post, you are already familiar with our internal project about a Daily Song Ranking problem, described in our previous blogs.

Before going into the details of this blog post, let’s first make a brief summary of our project:

In the first blog post, we illustrated [the pipeline to set up and build a Learning to Rank (LTR) system](https://sease.io/2020/12/a-learning-to-rank-project-on-a-daily-song-ranking-problem.html): we started from the available data, a Kaggle dataset [[1]](https://www.kaggle.com/edumucelli/spotifys-worldwide-daily-song-ranking); we manipulated it through several data cleaning and feature engineering techniques; we created the training set and the test set and finally, we trained a ranking model using XGBoost.

In the second blog post, we [performed further analyses using a Subset instead of the Full Dataset to check the differences in terms of model performances](https://sease.io/2021/02/a-learning-to-rank-project-on-a-daily-song-ranking-problem-part-2.html). We also explained the models’ behaviour through the use of the powerful library called SHAP.

In this blog post, **we will create a new query Id and check what happens while building the training set.**

In the previous experiments, we have generated the ‘query\_ID’ from a single feature (the ‘Region’ column), without considering the date of the song charts. During the analysis described in the second section of the blog post [Part 2](https://sease.io/2021/02/a-learning-to-rank-project-on-a-daily-song-ranking-problem-part-2.html), we realized that we could consider the query as a hash of multiple query-level features, to avoid “duplicates” of songs for each query: in song charts of a specific Region, a song can be in the same position on the chart for several days, even weeks.

Furthermore, if we also consider the date of the song chart (Day, Month, and Weekday) we will get a more specific query and consequently more accurate search results so that we can better represent the user’s intention and needs.

## Query Id Generation

You should carefully design how you calculate your query Id.

**The query Id represents the Q of <Q, D> in each query-document sample and the same query across your dataset must have the same Id.**

The simplest approach is when you have a query that is just a sequence of free-text terms; so you have to relate the same sequence of terms to the same query Id. That’s all.

Sometimes you may have a query represented by a series of filter queries that have been selected by the user during his search. If so, you may want to calculate the query Id as a combination of these filters. The more accurate the query, the better the search results will be.  
In fact, another good way to generate the query Id is by concatenating all the query-level features (**simple hashing, clustering**).

*Query-level (or query dependent) features describe a property of the query and their value depends only on the query instance.*  
In our case, they are Region, Day, Month, and Weekday.

So we decided to modify our pipeline, creating a different query Id.  
Let’s go back to the preprocessing part to generate it through the use of a new method:

```
				
					def generate_id_from_columns(input_data_frame, query_features, id_column):
    str_id = input_data_frame[query_features[0]].astype(str)
    for feature in query_features[1:]:
        str_id = str_id + '_' + input_data_frame[feature].astype(str)
    input_data_frame[id_column] = pd.factorize(str_id)[0]
				
			
```

In our case, the parameters are:

* + **input\_data\_frame** is the Spotify dataset (CSV file)
  + **query\_features** is represented by the set of the following query-level features: Region, Day, Month, and Weekday.
  + **id\_column** is the feature we want to create (we called it ‘***query\_ID’***)

Once created the “**str\_id**” as a hash of multiple features, we manipulated it with the Pandas factorize() function which uniquely links each string with an integer.

Here, you can find an illustration to understand the differences in the creation of the query Id:

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-03-18-alle-07.42.59.png?fit=2776%2C846&ssl=1)

(**Please note:** *to make a comparison with the ‘old’ model later, we have not deleted Day, Month, and Weekday features used to build the query.*)

We also made some statistical analyses to compare the old and the new query Id. In the table below, you can see that with the new implementation, we have more queries (from 54 to 19675) and fewer observations for each query. While we used to have around 400 song charts for each query now we have only one, consisting of up to 200 songs (in some cases we don’t have full charts). The standard deviation tells us whether the number of rows per query Id is evenly distributed or not. Since these are two completely different implementations, it is not easy to make a direct comparison; however, we can say that in both cases more than 80% of the query Ids contain a sufficient number of samples beyond the set threshold and this may be fine.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-03-09-alle-08.23.35.png?fit=800%2C428&ssl=1)

## Training and Test Sets SPLIT

Once we got the data frame with the new query Id, we split it into training and test sets following the same implementation adopted in the previous blog posts, which I will describe more specifically here:

1. 1. If we have query Ids that have a number of observations under a certain threshold, we save those observations in a new data frame called **under\_sampled\_only\_train**, because we only want them in the training set. We move some of them to the Test Set (the query Ids with the highest number of observations) only if the Test Set appears less than 20% of the entire dataset.
   2. All the Relevance Labels have to be equally distributed. In fact, we manually select 20% of all the observations for each Relevance Label, and we move them to the Test Set. In doing this, we make sure all the Relevance Labels, from 0 to 20, are in both sets.

With the new query Id, we realized that this implementation could not be applied. In this case, we have only a song chart for each query, and therefore it is assumed that there is only one song with the highest relevance (at the first position of the chart): it follows that we have just one observation with a Relevance Label of 20 and it will never appear in the Test Set.

For simplicity, let’s take the query\_ID = 0 as an example. In the table below, you can understand better what explained so far.  
Query 0 has 200 observations (a song chart); we have only very few observations with Relevance Labels from 10 to 20 (as expected by the mapping applied in [Part 1 – Relevance Rating](https://sease.io/2020/12/a-learning-to-rank-project-on-a-daily-song-ranking-problem.html)) and they will never be moved to the Test Set. Why?

* + For the **Relevance Label = 0** we have 50 observations in total, we take 20% of these observations, so 10 rows will be moved to the test set.
  + For the **Relevance Label = 7** we have 10 observations in total, we take 20% of these observations, so 2 rows will be moved to the test set.
  + For the **Relevance Label = 10** we have 3 observations in total, 20% of 3 is 0.6 so no row will be moved to the test set (the same happens for the remaining ones).

 Therefore, it is not possible to have all the Relevance Labels in both sets.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-03-18-alle-10.06.49.png?fit=1138%2C1158&ssl=1)

We decided to implement a different approach: we randomly shuffled the data frame and then split it into training and test sets, ensuring that 20% of the observations for each query Id move to the Test Set, independently of the Relevance Labels. Of course, it would be better to have Relevance Labels in both sets but in this way, their distribution has at least become fairer.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-03-07-alle-14.08.52.png?fit=1132%2C1144&ssl=1)

Finally, we trained a Learning To Rank model, using LambdaMART. Using the old split we would have trained the model on samples with all the Relevance Labels but most of them (from 10 to 20) would not have been tested because they were not present in the test set. How could we tell if the model performs well or not if it is not tested on a portion of important data?!

## Results

In this new implementation, we have taken a different approach and changed the pipeline in two parts:

1. 1. when generating the query Id
   2. at the stage where we split the dataset

Let’s check the results obtained:

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-03-16-alle-08.47.20.png?fit=512%2C140&ssl=1)

You can see that the variant where we used Hash Encoding (for the ‘Title’ feature) had better model performance than the other variant (Doc2Vec Encoding).

Using Hash Encoding, we checked the differences between training a model with the old and the new query Id and then we tested these models on the same test sets. Both models have the same features, so they can be compared; the only thing that changes is the query Id.  
In the first implementation (OldQueryId model) our goal was to get the best sorting based on Region, whereas now our goal is to get the best sorting based on Region, Day, Month, and Weekday.

When we use the training and the test sets of two different models, we have to be sure not to have intersections between them: it means that the observations of the test sets must be unknown at training time.

For example, let’s take the training set of the “OldQueryId model” and the test set of the “NewQueryId model”. We have to check if they have observations in common, which means we consider two rows to be identical if these have the same values for all features except the query Id. We used the merge function in Pandas [[2]](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.merge.html):

```
				
					intersections = training_set.merge(test_set, how='inner', on='cols')
				
			
```

where:

* + **intersections** = will contain all the rows in common between training and test sets
  + **training\_set**: data frame = the training set with the old query Id
  + **test\_set**: the object to merge with = the test set with the new query Id (hashing)
  + **how**: type of merge to be performed = *‘inner*‘ join to take the intersection
  + **on**: column to join on = ‘*cols*‘ (all the features except the query Id)

The query Id was excluded because it is the only feature manipulated differently during these two implementations. In case of matching, we deleted the common rows from the training set and left them in the test set.

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Schermata-2021-03-16-alle-09.10.01.png?fit=844%2C234&ssl=1)

We can see that the model using the new query ID performed better, in general. A query Id that is a hash of multiple query-level features is able to return a better sorting of the search results. When we used the training set of the new query\_ID and the test set of the old query\_ID (and vice versa), *train-ndcg@10* decreased a little bit. This could be the result of having deleted the common rows from the training set and so the model had fewer input data to learn.

## Final Consideration

**If possible, the query Id should contain all the query-level features**.

**The Target would be reaching a uniform distribution of samples per query Id.** You need to be careful in the way you calculate the query id: with a too fine-grained, you may end up with a lot of query ids that have very few samples; on the other hand, if you relax your grain, you may end up with huge ranked lists that are less precise because they represent wider concepts. You should try to get a balance.

**Drop training samples if query Ids are under-sampled**. Perhaps it should also be said that this must be contextualized. In case we have reliable data and we are confident that we have properly managed the condition that can potentially skyrocket the NDCG, we could try to keep those observations in the training set or assign a new query Id to all of them.

You have to be careful if you clean your dataset and then split it, because you may end up in having an unfair Test Set:

* + the Test Set **MUST not** have under-sampled query Ids
  + the Test Set **MUST not** have query Ids with a single Relevance Label
  + The Test Set **MUST** be representative and with an acceptable size (in terms of observations per query)
  + Possibly, all Relevance Labels should be in both sets

## Need Help With This Topic?​​

If you’re struggling with Query Id Generation, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Query Id Generation, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)