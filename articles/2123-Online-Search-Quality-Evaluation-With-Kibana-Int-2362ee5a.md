---
title: 'Online Search Quality Evaluation With Kibana – Introduction'
company: Sease
tag: 评测
date: 2023-03-27
url: https://sease.io/2023/03/online-search-quality-evaluation-with-kibana-introduction.html
account: 
origin: harvest3-202607
---
Hi readers!

The aim of this post is to show **how Kibana can be used to efficiently monitor and analyze the results of online search quality evaluations**, making it easier for users to identify areas for improvement.

This blog post provides a general understanding of online search quality evaluation and A/B testing, explaining why these are important. It will then introduce the use of Kibana in implementing these evaluations (and the motivations behind it). In the end, the advantages and disadvantages of using Kibana for online search quality evaluation will be summarized.

A second blog post will follow, focusing on the specific features and tools offered by Kibana. It will provide practical examples of how to create visualizations and dashboards that help in comparing different ranking models.

###### WHAT WE ARE GOING TO SEE IN THIS BLOG POST

* [What is Online Evaluation?](#OnlineEvaluation)
* [A/B Testing](#ab)  
  – [Signal to measure](#signal)  
  – [Experiment design](#experiment)
* [Kibana Implementation](#implementation)  
  – [Implementation Steps](#steps)  
  – [Scenario](#scenario)
* [Kibana Pros & Cons](#pros)

## What is Online Evaluation?

Search Quality Evaluation is a branch of Information Retrieval that aims to assess how good your search system is in satisfying the user’s information needs.  
There are several ways to measure the quality of a search engine: from a relevance perspective, the search engine should return results that are relevant to the user’s query and this can be measured through offline and online evaluations, both of which are critical for a business.

First, it is important to make a good **Offline** search quality evaluation to validate as much as possible a candidate release by estimating how it might behave online.

The final word on the success or failure of a released version is decided **Online** where you can measure live (in production) the vital metrics for your business.

*Online evaluation remains the optimal way to prove how your model performs in a real-world scenario and it can give you the necessary information to evaluate, improve and better understand the behavior of your model.*

If you’re interested, check out our previous blog posts that discuss search quality evaluation:

* [The importance of online testing in learning to rank part 1](https://sease.io/2020/04/the-importance-of-online-testing-in-learning-to-rank-part-1.html)
* [Online Testing for Learning To Rank: Interleaving](https://sease.io/2020/05/online-testing-for-learning-to-rank-interleaving.html)
* [Offline Search Quality Evaluation: Rated Ranking Evaluator (RRE)](https://sease.io/2021/01/offline-search-quality-evaluation-rated-ranking-evaluator-rre.html)

## A/B Testing

In general, when a new model exhibits satisfactory performance in offline testing and is deemed a good candidate, the intuitive solution may involve replacing the previous model with the new one. However, this approach may involve potential risks and is not considered optimal. As a best practice, it is recommended to conduct an online comparison of the old and new models in order to evaluate their performance under real-world conditions. How?

Two types of online testing that are widely spread in the industry are A/B testing and Interleaving.  
Our implementation used A/B testing, so only this method will be briefly discussed.

As can be easily seen from the image below, A/B testing involves comparing two models by dividing the audience into two groups (one for each model), usually 50/50:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/12/pasted-image-0.png?fit=800%2C445&ssl=1)

Compared to Interleaving, A/B testing is easier to implement, but requires a higher amount of traffic and time and could expose a group of users to a bad ranking model for the entire duration of the experiment.

If you want to know a bit more about A/B testing, take a look at the related part of this blog post about [the importance of online testing in Learning to Rank](https://sease.io/2020/04/the-importance-of-online-testing-in-learning-to-rank-part-1.html).

##### Signal to measure

There are several metrics that can be considered for the online evaluation, each representing a specific aspect of search quality:

###### Click-Through Rate (CTR)

The most common and actually one of the most important. It is a metric calculated by dividing the number of clicks on a document/product by the number of impressions or views it received. Our goal is to optimize CTR; this means that when users search for something, we hope that the search results will prompt them to interact with the search engine, for example by clicking on items/products, or even downloading songs, adding hotels to favorites, or any other type of interaction.

###### Sale/Revenue Rate

If you are in an e-commerce setting, it is crucial to monitor and optimize business metrics such as sales and revenue; simply achieving a high CTR does not guarantee effective search engine performance, as a lack of corresponding sales or revenue may indicate other issues with the user experience or the underlying search algorithm.

###### DWELL Time

It is the length of time a user spends on a search engine results page after clicking on a result from a query. This metric reflects how long the user found the content useful or informative, so a long time indicates that the clicked content was relevant to the user.

###### Query Reformulations

The amount of query reformulations refers to the number of times users modify the original search query (i.e., rewrite the same query) to improve the results returned by a search engine. In general, the goal should be to achieve a satisfactory level of information retrieval with as few query reformulations as possible.

###### Bounce Rates

The bounce rate in a search engine refers to the percentage of users who leave the search results page after only visiting one page. A high bounce rate may indicate that the search results are not relevant to the user’s needs or that the user experience is poor.

It is suggested to start with the signals closest to your search engine and then gradually monitor all of them.

##### Experiment design

There are certain aspects that may benefit from further consideration to optimize the design and execution of the experiment, leading to more insightful and reliable outcomes; for example, considering the impact of using different devices on the results, assessing the optimal length of the experiment to ensure adequate data collection, or determining the most appropriate number of models to consider could help to maximize the efficiency and effectiveness of the experiment.

###### 1. TESTING DIFFERENT PLATFORMS

In a real-world scenario, systems are deployed on different platforms: desktop, mobile, and tablet. It is a good practice to test models on each independently, as metrics and target audience can vary between platforms and affect results.

###### 2. HOW LONG TO TEST

A test should be stopped when the statistical significance of the result is sufficiently high. As a general rule, models should not be tested for less than two weeks.

###### 3. HOW MANY MODELS

Multiple models can be compared simultaneously, from two to many. The number of systems to be compared depends on the amount of traffic available. However, the more systems are compared, the more difficult it becomes to identify the winner. It is generally recommended to keep the comparison process as simple as possible.

Another important aspect to consider is the **noise**. Many companies assess the total number of clicks or sales, for example, when comparing models, without realizing that it’s important to focus only on interactions (data) that come from the search engine result page they are evaluating online and not consider those from different pages or sources. Our advice is always to eliminate or reduce noise as much as possible.

###### WANT TO KNOW MORE ABOUT HOW SEARCH QUALITY EVALUATION WORKS?

Search results quality is a big matter for any search engineer and product manager.   
We spent a lot of efforts to improve how to measure these metrics, and we delivered these researches in different ways:

###### [Search Quality Evaluation Training](https://sease.io/training/search-quality-evaluation-trainings)

###### [Free Tool for Search Results Quality](https://sease.io/rated-ranking-evaluator-enterprise)

###### [Blog Posts about Search Quality Evaluation](https://sease.io/tag/search-quality-evaluation)

## Kibana Implementation

Now, let’s dive into our Kibana Implementation.

**Kibana**is a data visualization and exploration platform that provides a web interface for interacting, searching, analyzing, and visualizing data stored in Elasticsearch, making it easy for users to create and save custom dashboards and perform advanced data analysis and reporting.

What are the ***MAIN FACTORS*** behind the choice of this implementation?

Despite their other advantages, online evaluation tools currently have some limitations in terms of metrics and data to use:

* It can be challenging to find and use the same metrics used for optimizing models
* it can be difficult to eliminate external factors or corrupted data

This is why we have chosen to implement our online evaluation using Kibana.

##### Implementation Steps

Here is the pipeline for implementing this online search quality evaluation with Kibana:

1. Create an Elasticsearch instance and enroll Kibana.
2. Create an Index, specifying an explicit mapping if possible.
3. Set up and start an A/B testing.
4. Collect user interaction data and index it.
5. Create a [Data View](https://www.elastic.co/guide/en/kibana/current/data-views.html) in Kibana, to access the Elasticsearch data you want to explore.
6. Leverage Kibana tools to create Visualizations and Dashboards to compare different models.

##### Scenario

In this case, we assume to be in a *book e-commerce scenario* where we daily collect user interactions, to understand how users are interacting with the search engine, such as:

* **bookId**: to identify specific products
* **testGroup**: to identify the model (name) assigned to a user group
* **queryId**: to identify the user query
* **timestamp**: to perform temporal analysis
* **interactionType** (impressions, click, add to cart, sale), to understand the type of interaction that occurred. We have also included 4 single boolean fields (containing 0 or 1 depending on the occurrence) that are simply used for calculation purposes in creating specific visualizations:
  + **impression**
  + **click**
  + **addToCart**
  + **sale**
* **queryResultCount** (query hits), to perform analysis based on the number of search results returned for a given query

N.B. Feel free to consider and add any additional features that would be beneficial for your case and domain.

We index this data in our Elasticseach index and we leverage Kibana to explore it and evaluate the performance of models (identified through the `testGroup` field) by creating specific visualizations (based on filtering the data).

Please refer to our post for the ‘[Visualization Examples](https://sease.io/2023/06/online-search-quality-evaluation-with-kibana-visualization-examples.html)’ description.

## Kibana Pros & Cons

Let’s conclude the first blog post with Kibana’s advantages and disadvantages.

##### PROS

* Kibana has an easy and intuitive graphical user interface.
* It has the ability to create detailed reporting dashboards (aggregating several visualizations together).
* It has the ability to filter unwanted data (corrupted interactions/test interactions/unwanted sources).
* It is possible to specify the data you want to highlight using the filter panel.
* If you index new data, visualizations are automatically updated.
* It offers the possibility to export (and import) visualizations and dashboards using the **‘Export objects API’**, allowing for the reproduction of the custom evaluation in future projects.

##### CONS

* **VEGA** is very powerful but is not so intuitive and simple to use (*“recommended for advanced users who are comfortable writing Elasticsearch queries manually”*).
* If a new model is tested (the model name changes) or the data view is renamed, you will need to manually update the filter in all of the visualizations.

## Need Help With This Topic?​​

If you’re struggling with search quality evaluation and Kibana, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with search quality evaluation and Kibana, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)