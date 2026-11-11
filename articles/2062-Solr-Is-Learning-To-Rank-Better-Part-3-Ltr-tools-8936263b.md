---
title: 'Solr Is Learning To Rank Better – Part 3 – Ltr tools'
company: Sease
tag: 排序
date: 2016-08-30
url: https://sease.io/2016/08/apache-solr-learning-to-rank-part-3-ltr-tools.html
account: 
origin: harvest3-202607
---
## Apache Solr Learning to Rank - Things Get Serious

This blog post is about the Apache Solr Learning to Rank Tools: a set of tools to ease the utilisation of the Apache Solr Learning To Rank integration.

The model has been trained in [Part 2](https://sease.io/2016/08/apache-solr-learning-to-rank-part-2-model-training.html), and we are ready to deploy it to Solr, but first, it would be useful to have a better understanding of what we just created.  
A LambdaMART model in a real-world scenario is a massive ensemble of regression trees, not the most readable structure for a human.

The more we understand the model, the easier will be to find anomalies and fix/improve them.

But the most important benefit of having a clearer picture of the training set and the model is the fact that it can dramatically improve communication with the business layer:

* + What are the most important features in our domain?
  + What kind of document should score high according to the model?
  + Why this document (feature vector) is scoring that high?

These are only examples, but a lot of similar questions can arise, and we need the tools to answer them.

## Apache Solr Learning to Rank Tools

This is how the Learning To Rank tools project [[1]](https://github.com/alessandrobenedetti/ltr-tools) was born (LTR stands for Learning To Rank ).

The target of the project is to use the power of Apache Solr to visualise and understand a Learning To Rank model.

It is a set of simple tools specifically thought for LambdaMart models, represented in the JSON format supported by the Bloomberg Apache Solr Learning To Rank integration.  
Of course, it is open source so feel free to extend it by introducing additional models and functionalities.

All the tools provided are meant to work with a Solr backend to index data that we can later search easily.

The tools currently available provide the support to :

* + index the model  in a Solr collection
  + index the training set in a Solr collection  
    print the top-scoring leaves from a LambdaMART model

##### Preparation

To use the Learning To Rank (LTR) tools you must proceed with these simple steps :

* + **set up the Solr backend** – this will be a fresh Solr instance with 2 collections: **models**, **trainingSet**,  the simple configuration is available in *ltr-tools/configuration*
  + **gradle build** – this will package the executable jar in *ltr-tools/ltr-tools/build/libs*

##### Usage

Let’s briefly take a look to the parameters of the executable command line interface :

| Parameter | Description |
| --- | --- |
| **-help** | Print the help message |
| **-tool** | The tool to execute (possible values):  – modelIndexer  – trainingSetIndexer  – topScoringLeavesViewer |
| **-solrURL** | The Solr base URL to use for the search backend |
| **-model** | The path to the model.json file |
| **-topK** | The number of top scoring leaves to return ( sorted by score descendant) |
| **-trainingSet** | The path to the training set file |
| **-features** | The path to the feature-mapping.json. A file containing a mapping between the feature Id and the feature name. |
| **-categorical Features** | The path to a file containing the list of categorical feature names. |

**N.B.** *All the following examples will assume the model in input is a LambdaMART model, in the JSON format the Bloomberg Solr Plugin expects.*

## Model Indexer

**Requirement** : Backend Solr collection <**models**> must be UP & RUNNING

The Model Indexer is a tool that indexes a lambdaMART model in Solr to better visualize the structure of the trees ensemble.  
In particular, the tool will index each branch split of the trees belonging to the lambdaMART ensemble as Solr documents.  
Let’s take a look at the Solr schema:

*configuration/solr/models/conf*

```
				
					 &lt;field name="id" type="string" indexed="true" stored="true" required="true" multiValued="false"/&gt;  
 &lt;field name="modelName" type="string" indexed="true" stored="true"/&gt;  
 &lt;field name="feature" type="string" indexed="true" stored="true" docValues="true"/&gt;  
 &lt;field name="threshold" type="double" indexed="true" stored="true" docValues="true"/&gt;  
 ...  
				
			
```

So giving in input a lambdaMART model :

*e.g. lambdaMARTModel1.json*

```
				
					{  
   "class":"org.apache.solr.ltr.ranking.LambdaMARTModel",  
   "name":"lambdaMARTModel1",  
   "features":[  
    {  
      "name":"feature1"  
    },  
    {  
      "name":"feature2"  
    }  
   ],  
   "params":{  
    "trees":[  
      {  
       "weight":1,  
       "root":{  
         "feature":"feature1",  
         "threshold":0.5,  
         "left":{  
          "value":80  
         },  
         "right":{  
          "feature":"feature2",  
          "threshold":10.0,  
          "left":{  
            "value":50  
          },  
          "right":{  
            "value":75  
          }  
         }  
       }  
      }  
    ]  
   }  
 }  
				
			
```

**N.B.** a branching split is where the tree split in 2 branches:

```
				
					 "feature":"feature2",   
      "threshold":10.0,   
      "left":{   
       "value":50   
      },   
      "right":{   
       "value":75   
      }   
				
			
```

A split happens on a threshold of the feature value.  
We can use the tool to start the indexing process:

```
				
					java -jar ltr-tools-1.0.jar -tool modelIndexer -model /models/lambdaMARTModel1.json -solrURL
http://localhost:8983/solr/models
				
			
```

After the indexing process has finished we can access Solr and start searching!  
*e.g.  
This query will return in response for each feature :*

* + *the number of times the feature appears at a branch split*
  + *the top 10 occurring thresholds for that feature*
  + *the number of unique thresholds that appear in the model for that feature*

```
				
					http://localhost:8983/solr/models/select?indent=on&amp;q=*:*&amp;wt=json&amp;facet=true&amp;json.facet={  
      Features: {  
           type: terms,  
           field: feature,  
           limit: -1,  
           facet: {  
                Popular_Thresholds: {  
                     type: terms,  
                     field: threshold,  
                     limit: 10  
                },  
                uniques: "unique(threshold)"  
           }  
      }  
 }&amp;rows=0&amp;fq=modelName:lambdaMARTModel1  
				
			
```

Let’s see how it is possible to interpret the Solr response:

```
				
					 facets": {  
   "count": 3479, //number of branch splits in the entire model  
   "Features": {  
     "buckets": [  
       {  
         "val": "product_price",  
         "count": 317, //the feature "product_price" is occurring in the model in 317 splits  
         "uniques": 28, //the feature "product_price" is occurring in the splits with 28 unique threshold values  
         "Popular_Thresholds": {  
           "buckets": [  
             {  
               "val": "250.0", //threshold value  
               "count": 45 //the feature "product_price" is occurring in the splits 45 times with threshold "250.0"  
             },  
             {  
               "val": "350.0",  
               "count": 45  
             },  
             ...  
				
			
```

## TrainingSet Indexer

**Requirement** : Backend Solr collection <**trainingSet**> must be UP & RUNNING

The Training Set Indexer is a tool that indexes a Learning To Rank training set (in RankLib format) in Solr to better visualize the data.  
In particular, the tool will index each training sample of the training set as a Solr document.  
Let’s see the Solr schema :

***configuration/solr/models/conf***

```
				
					&lt;field name="id" type="string" indexed="true" stored="true" required="true" multiValued="false"/&gt;
&lt;field name="relevancy" type="tdouble" indexed="true" stored="true" docValues="true"/&gt; 
&lt;dynamicField name="cat_*" type="string" indexed="true" stored="true" docValues="true"/&gt;
&lt;dynamicField name="*" type="tdouble" indexed="true" stored="true" docValues="true"/&gt; 
				
			
```

As you can notice the main point here is the definition of dynamic fields.  
Indeed we don’t know beforehand the names of the features, but we can distinguish between categorical features ( which we can index as strings) and ordinal features (which we can index as double).

We require now 3 inputs :

**1)** the training set in the RankLib format: 

*e.g. training1.txt*

```
				
					1 qid:419267 1:300 2:4.0 3:1 6:1
4 qid:419267 1:250 2:4.5 4:1 7:1
5 qid:419267 1:450 2:5.0 5:1 6:1
2 qid:419267 1:200 2:3.5 3:1 8:1 
				
			
```

**2)** the feature mapping to translate the feature Id to a human-readable feature name

e.g. features-mapping1.json

```
				
					{"1":"product_price","2"
:"product_rating","3"
:"product_colour_red","4"
:"product_colour_green","5"
:"product_colour_blue","6"
:"product_size_S","7"
:"product_size_M","8"
:"product_size_L"}
				
			
```

**N.B**. the mapping must be a JSON object on a single line

This input file is optional, it is possible to index directly the feature Ids as names.

**3)** the list of categorical features

*e.g. categoricalFeatures1.txt*

```
				
					product_colour
product_size 
				
			
```

This list (one feature per line) will clarify to the tool which features are categorical, to index the category as a string value for the feature.  
This input file is optional, it is possible to index the categorical features as binary one-hot encoded features.

To start the indexing process :

```
				
					java -jar ltr-tools-1.0.jar -tool trainingSetIndexer -trainingSet /trainingSets/training1.txt -features /featureMappings/feature-mapping1.json -categoricalFeatures /feature/categoricalFeatures1.txt -solrURL 
http://localhost:8983/solr/trainingSet
				
			
```

After the indexing process has finished we can access Solr and start searching!  
*e.g.  
This query will return in response all the training samples filtered and then faceted on the relevancy field.*  
*This can be an indication of the distribution of the relevancy score in specific subsets of the training set.*

```
				
					http://localhost:8983/solr/trainingSet/select?
indent=on&amp;q=*:*&amp;wt=json&amp;fq=cat_product_colour:red&amp;rows=0&amp;facet=true&amp;facet.field=relevancy
				
			
```

**N.B. This is a quick and dirty way to explore the training set. I deeply suggest you use it as a quick resource. Advanced data plotting is more suitable for visualizing big data and identifying patterns.**

## Top Scoring Leaves Viewer

The top scoring leaves viewer is a tool to print the path of the top-scoring leaves in the model.  
Thanks to this tool it will be easier to answer questions like :  
” How a document (feature vector) should look like to get a high score?”  
The tool will simply visit the ensemble of trees in the model and keep track of the scores of each leaf.

So giving in input a lambdaMART model:

*e.g. lambdaMARTModel1.json*

```
				
					{  
   "class":"org.apache.solr.ltr.ranking.LambdaMARTModel",  
   "name":"lambdaMARTModel1",  
   "features":[  
    {  
      "name":"feature1"  
    },  
    {  
      "name":"feature2"  
    }  
   ],  
   "params":{  
    "trees":[  
      {  
       "weight":1,  
       "root":{  
         "feature":"feature1",  
         "threshold":0.5,  
         "left":{  
          "value":80  
         },  
         "right":{  
          "feature":"feature2",  
          "threshold":10.0,  
          "left":{  
            "value":50  
          },  
          "right":{  
            "value":75  
          }  
         }  
       }  
      }, ...  
    ]  
   }  
 }  
				
			
```

To start the process:

```
				
					 java -jar ltr-tools-1.0.jar -tool topScoringLeavesViewer -model /models/lambdaMARTModel1.json -topK 10  
				
			
```

This will print the top scoring 10 leaves (with related path in the tree):

```
				
					1000.0 -&gt; feature2 &gt; 0.8, feature1 &lt;= 100.0
200.0 -&gt; feature2 &lt;= 0.8, 
80.0 -&gt; feature1 &lt;= 0.5, 
75.0 -&gt; feature1 &gt; 0.5, feature2 &gt; 10.0, 
60.0 -&gt; feature2 &gt; 0.8, feature1 &gt; 100.0, 
50.0 -&gt; feature1 &gt; 0.5, feature2 &lt;= 10.0,  
				
			
```

## Conclusion

The Apache Solr Learning To Rank tools are quick and dirty solutions to help people understand better and work better with Learning To Rank models.

They are far from being optimal but I hope they will be helpful for people working on similar problems.

Any contribution, improvement, or bugfix is welcome!

## Need Help With This Topic?​​

If you’re struggling with Learning to Rank in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Learning to Rank in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)