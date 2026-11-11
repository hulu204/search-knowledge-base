---
title: 'Solr Is Learning To Rank Better - Part 4 - Apache Solr Integration'
company: Sease
tag: 排序
date: 2016-10-23
url: https://sease.io/2016/10/apache-solr-learning-to-rank-better-part-4.html
account: 
origin: harvest3-202607
---
## Last Stage Of The Journey

This blog post is about the Apache Solr Learning To Rank ( LTR ) integration.

First, [we modelled our dataset, collected the data and refined it](https://sease.io/2016/07/apache-solr-learning-to-rank-part-1-data-collection.html), then we [trained the model](https://sease.io/2016/08/apache-solr-learning-to-rank-part-2-model-training.html) and [analysed and evaluated the model and training set](https://sease.io/2016/08/apache-solr-learning-to-rank-part-3-ltr-tools.html).

**We are ready to rock and deploy the model and feature definitions to Solr.**  
I will focus in this blog post on the Apache Solr Learning To Rank (LTR) integration from Bloomberg [[1]](https://issues.apache.org/jira/browse/SOLR-8542).  
The contribution is completed and available from Apache Solr 6.4.  
This blog is heavily based on the Learning To Rank (LTR) Bloomberg contribution readme [[2]](https://github.com/bloomberg/lucene-solr/blob/master-ltr-plugin-develop/solr/contrib/ltr/README.md).

## Apache Solr Learning To Rank (LTR) integration

The Apache Solr Learning To Rank (LTR) integration allows Solr to rerank the search results evaluating a provided Learning To Rank model.  
The main responsibilities of the plugin are:

* storage of feature definition
* storage of models
* feature extraction and caching
* search result rerank

## Features Definition

As we learnt from the previous posts, the feature vector is the mathematical representation of each document/query pair and the model will score each search result according to that vector.  
Of course, we need to tell Solr how to generate the feature vector for each document in the search results.  
Here comes the Feature Definition file.  
A JSON array describing all the relevant features necessary to score our documents through the machine-learned LTR model.

*e.g.*

```
				
					[{ "name": "isBook",
  "class": "org.apache.solr.ltr.feature.SolrFeature",
  "params":{ "fq": ["{!terms f=category}book"] }
},
{
  "name":  "documentRecency",
  "class": "org.apache.solr.ltr.feature.SolrFeature",
  "params": {
      "q": "{!func}recip( ms(NOW,publish_date), 3.16e-11, 1, 1)"
  }
},
{
  "name" : "userTextTitleMatch",
  "class" : "org.apache.solr.ltr.feature.SolrFeature",
  "params" : { "q" : "{!field f=title}${user_text}" }
},
{
  "name":"book_price",
  "class":"org.apache.solr.ltr.feature.FieldValueFeature",
  "params":{"field":"book_price"}
},
{
  "name":"originalScore",
  "class":"org.apache.solr.ltr.feature.OriginalScoreFeature",
  "params":{}
},
{
   "name" : "userFromMobile",
   "class" : "org.apache.solr.ltr.feature.ValueFeature",
   "params" : { "value" : "${userFromMobile:}", "required":true }
}] 
				
			
```

| **SolrFeature** |
| --- |
| – Query Dependent – Query Independent |
| A Solr feature is defined by a Solr query following the Solr syntax. The value of the Solr feature is calculated as the return value of the query run against the document we are scoring. This feature can depend on query time parameters or can be query-independent (see examples) |
| **e.g.**  **“params”:{“fq”: [“{!terms f=category}book”] }**  – Query Independent – Boolean feature If the document matches the term ‘book’ in the field ‘category’ the feature value will be 1. It is query-independent as no query param affects this calculation. **“params”:{“q”: “{!func}recip( ms(NOW,publish\_date), 3.16e-11, 1, 1)”}** – Query Dependent – Ordinal feature The feature value will be calculated as the result of the function query, the more recent the document, the closer to 1 the value. It is query-dependent as ‘NOW’ affects the feature value. **“params”:{“q”: “{!field f=title}${user\_text}” }** – Query Dependent – Ordinal feature The feature value will be calculated as the result of the query, the more relevant the title content for the user query, the higher the value. It is query-dependent as the ‘user\_text’ query param affects the calculation. |

| **FieldValueFeature** |
| --- |
| – Query Independent |
| A Field Value feature is defined by a Solr field. The value of the feature is calculated as the content of the field for the document we are scoring. The field must be STORED or DOC-VALUED. This feature is query-independent (see examples) |
| **e.g**. **“params”:{“field”:”book\_price”}** – Query Independent – Ordinal feature The value of the feature will be the content of the ‘book\_price’ field for a given document. It is query-independent as no query param affects this calculation. |

| **ValueFeature** |
| --- |
| – Query Level – Constant |
| A Value feature is defined by a constant or an external query parameter. The value of the feature is calculated as the value passed in the solr request as an efi(External Feature Information) parameter or as a constant. This feature depends **only** on the param configured( see examples) |
| **e.g.** **“params” : { “value” : “${user\_from\_mobile:****}”, “required”:false }** – Query Level – Boolean feature The user will pass the ‘userFromMobile’ request param as an efi The value of the feature will be the value of the parameter The default value will be assigned if the parameter is missing in the request If it is required an exception will be thrown if the parameter is missing in the request**“params” : { “value” : “5****“, “required”:false }** – Constant – Ordinal feature The feature value will be calculated as the constant value of ‘5’.Except for the constant, nothing affects the calculation. |

| **OriginalScoreFeature** |
| --- |
| – Query Dependent |
| An Original Score feature is defined with no additional parameters. The value of the feature is calculated as the original Lucene score of the document given the input query. This feature depends on query time parameters ( see examples) |
| **e.g.** **“params”:{}** — Query Dependent — Ordinal feature The feature value will be the original Lucene score given the input query. It is query-dependent as the entire input query affects this calculation. |

##### EFI ( External Feature Information )

As you noticed in the feature definition JSON, external request parameters can affect the feature extraction calculation.  
When running a rerank query it is possible to pass additional request parameters that will be used at feature extraction time.  
We see this in detail in the related section.

e.g.  
rq={!ltr reRankDocs=3 model=externalmodel }

##### Deploy Features definition

Good, we defined all the features we require for our model, we can now send them to Solr:

```
				
					curl -XPUT 'http://localhost:8983/solr/collection1/schema/feature-store' --data-binary @/path/features.json -H 'Content-type:application/json' 
				
			
```

##### View Features Definition

To visualise the features just sent, we can access the feature store:

```
				
					curl -XGET 'http://localhost:8983/solr/collection1/schema/feature-store'  
				
			
```

## Models Definition

We extensively explored how to train models and how models look in the format the Solr plugin is expecting.

For details, I suggest you read the [Part 2.](https://sease.io/2016/08/apache-solr-learning-to-rank-part-2-model-training.html)

Let’s have a quick summary anyway:

##### Linear Model (Ranking SVM, Pranking)

*e.g.*

```
				
					 {
    "class":"org.apache.solr.ltr.model.LinearModel",
    "name":"myModelName",
    "features":[
        { "name": "userTextTitleMatch"},
        { "name": "originalScore"},
        { "name": "isBook"}
    ],
    "params":{
        "weights": {
            "userTextTitleMatch": 1.0,
            "originalScore": 0.5,
            "isBook": 0.1
        }
    }
} 
				
			
```

##### Multiple Additive Trees (LambdaMART, Gradient Boosted Regression Trees )

*e.g.*

```
				
					{
    "class":"org.apache.solr.ltr.model.MultipleAdditiveTreesModel",
    "name":"lambdamartmodel",
    "features":[
        { "name": "userTextTitleMatch"},
        { "name": "originalScore"}
    ],
    "params":{
        "trees": [
            {
                "weight" : 1,
                "root": {
                    "feature": "userTextTitleMatch",
                    "threshold": 0.5,
                    "left" : {
                        "value" : -100
                    },
                    "right": {
                        "feature" : "originalScore",
                        "threshold": 10.0,
                        "left" : {
                            "value" : 50
                        },
                        "right" : {
                            "value" : 75
                        }
                    }
                }
            },
            {
                "weight" : 2,
                "root": {
                    "value" : -10
                }
            }
        ]
    }
}  
				
			
```

##### Heuristic Boosted Model (experimental)

The Heuristic Boosted Model is an experimental model that combines linear boosting with any model.  
It is currently available in the experimental branch [[3]](https://github.com/bloomberg/lucene-solr/tree/master-ltr-plugin-experimental/solr/contrib/ltr).  
This capability is currently supported only by the: *org.apache.solr.ltr.ranking.HeuristicBoostedLambdaMARTModel* .  
The reason behind this approach is that sometimes, at training time we don’t have available all the features we want to use at query time.  
e.g.  
Your training set is not built on clicks of the search results and contains legacy data, but you want to include the original score as a boosting factor  
Let’s see the configuration in detail.

Given:

```
				
					"features":[ { "name": "userTextTitleMatch"}, { "name": "originalScoreFeature"} ]
"boost":{ "feature":"originalScoreFeature", "weight":0.1, "type":"SUM" } 
				
			
```

The original score feature value, weighted by a factor of 0.1, will be added to the score produced by the LambdaMART trees.

```
				
					 "boost":{ "feature":"originalScoreFeature", "weight":0.1, "type":"PRODUCT" }  
				
			
```

The original score feature value, weighted by a factor of 0.1, will be multiplied by the score produced by the LambdaMART trees.

**N.B.** Take extra care when using this approach. This introduces a manual boosting to the score calculation, which adds flexibility when you don’t have much data for training. However, you will lose some of the benefits of a machine-learned model, which was optimized to rerank your results. As you get more data and your model becomes better, you should shift off the manual boosting.

e.g

```
				
					{
    "class":"org.apache.solr.ltr.ranking.HeuristicBoostedLambdaMARTModel",
    "name":"lambdamartmodel",
    "features":[
        { "name": "userTextTitleMatch"},
        { "name": "originalScoreFeature"}
    ],
    "params":{
    "boost": {
          "feature": "originalScoreFeature",
          "weight": 0.5,
          "type": "SUM"
        },
        "trees": [
            {
                "weight" : 1,
                "root": {
                    "feature": "userTextTitleMatch",
                    "threshold": 0.5,
                    "left" : {
                        "value" : -100
                    },
                    "right": {
                        "value" : 10}
 }
 },
 {
 "weight" : 2,
 "root": {
 "value" : -10
 }
 }
 ]
 }
 }
				
			
```

##### Deploy Model

As we saw for the features definition, deploying the model is quite straightforward:

```
				
					curl -XPUT 'http://localhost:8983/solr/collection1/schema/model-store' --data-binary @/path/model.json -H 'Content-type:application/json' 
				
			
```

##### View Model

The model will be stored in an easily accessible JSON store:

```
				
					curl -XGET 'http://localhost:8983/solr/collection1/schema/model-store'
				
			
```

## Rerank query

To rerank your search results using a machine-learned LTR model it is required to call the rerank component using the Apache Solr Learning To Rank (LTR) query parser.

Query Re-Ranking allows you to run an initial query(A) for matching documents and then re-rank the top N documents re-scoring them based on a second query (B).  
Since the more costly ranking from query B is only applied to the top N documents it will have less impact on performance than just using the complex query B by itself – the trade-off is that documents which score very low using the simple query A may not be considered during the re-ranking phase, even if they would score very highly using query B. *Solr Wiki*

The Apache Solr Learning To Rank (LTR) integration defines an additional query parser that can be used to define the rerank strategy.  
In particular, when rescoring a document in the search results:

* + Features are extracted from the document
  + The score is calculated by evaluating the model against the extracted feature vector
  + Final search results are reranked according to the new score

rq={!ltr model=myModelName reRankDocs=25}

**!ltr** – will use the ltr query parser  
**model=myModelName** – specifies which model in the model store to use to score the documents  
**reRankDocs=25** – specifies that only the top 25 search results from the original ranking, will be scored and reranked

When passing external feature information (EFI) that will be used to extract the feature vector, the syntax is pretty similar :

rq={!ltr reRankDocs=3 model=externalmodel efi.parameter1=’value1′ efi.parameter2=’value2′}

e.g.

rq={!ltr reRankDocs=3 model=externalModel efi.user\_input\_query=’Casablanca’ efi.user\_from\_mobile=1}

##### Sharding

When using sharding, each shard will rerank, so the reRankDocs will be considered per shard.

**e.g.**  
10 shards  
You run a distributed query with :  
rq={!ltr reRankDocs=10 …  
You will get a total of 100 documents re-ranked.

##### Pagination

Pagination is delicate.

Let’s explore the scenario on a single Solr node and on a sharded architecture.

###### Single Solr node

reRankDocs=15

rows=10

This means each page is composed of 10 results.  
What happens when we hit page 2?  
The first 5 documents in the search results will have been rescored and affected by the reranking.  
The latter 5 documents will preserve the original score and original ranking.

e.g.

Doc 11 – score= 1.2

Doc 12 – score= 1.1

Doc 13 – score= 1.0

Doc 14 – score= 0.9

Doc 15 – score= 0.8

Doc 16 – score= 5.7

Doc 17 – score= 5.6  
Doc 18 – score= 5.5  
Doc 19 – score= 4.6  
Doc 20 – score= 2.4

This means that score (15) could be < score (16), but documents 15 and 16 are still in the expected order.  
The reason is that the top 15 documents are rescored and reranked and the rest are left unchanged.

###### Sharded architecture

reRankDocs=15

rows=10  
Shards number=2

When looking for page 2, Solr will trigger queries to the shards to collect 2 pages per shard :  
Shard1 : 10 ReRanked docs (page1) + 10 OriginalScored docs (page2)  
Shard2 : 10 ReRanked docs (page1) + 10 OriginalScored docs (page2)

The results will be merged, and possibly, original scored search results can top up reranked docs.

A possible solution could be to normalise the scores to prevent any possibility that a reranked result is surpassed by the original scored ones.

**Note**: The problem is going to happen after you reach rows \* page > reRankDocs. In situations when reRankDocs is quite high, the problem will occur only in deep paging.

## Feature Extraction And Caching

Extracting the features from the search results document is the most onerous task while reranking using LTR.

The LTRScoringQuery will take care of computing the feature values in the feature vector and then delegate the final score generation to the LTRScoringModel.  
For each document, the definitions in the feature store are applied to generate the vector.

The vector can be generated in parallel, leveraging a multi-threaded approach.

Extra care must be taken into account when configuring the number of threads in the game.

The features vector is currently cached in toto in the QUERY\_DOC\_FV cache.

This means that given the query and EFIs, we cache the entire feature vector for the document.

Simply giving in input a different EFI request parameter will imply a different hashcode for the feature vector and consequentially invalidate the cached one.

This bit can be potentially improved, by managing separately caches for the query-independent, query-dependent and query-level features [[5]](https://issues.apache.org/jira/browse/SOLR-10448).

## Need Help With This Topic?​​

If you’re struggling with integrating Learning to Rank into Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with integrating Learning to Rank into Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)