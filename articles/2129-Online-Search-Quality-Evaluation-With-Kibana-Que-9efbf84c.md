---
title: 'Online Search Quality Evaluation With Kibana – Queries in Common'
company: Sease
tag: 评测
date: 2023-06-19
url: https://sease.io/2023/06/online-search-quality-evaluation-with-kibana-queries-in-common.html
account: 
origin: harvest3-202607
---
Aside from the visualizations and evaluation examples presented in this [blog post](https://sease.io/2023/06/online-search-quality-evaluation-with-kibana-visualization-examples.html), another useful way to evaluate the models online is by comparing their performance on queries in common.

During an A/B test, it’s feasible that users assigned to Model A may make queries that are not performed by those assigned to Model B.  
To ensure a fair comparison, you should take into account only the queries that are made in both models; by examining the queries in common, you can obtain a clearer picture of their performance.

In this short “tips and tricks” blog, we are going to see what are the steps to create Kibana visualizations that filter based on queries in common; in particular, we will explore:

1. [How to execute a query to obtain the unique query ids per each model](#uniquequery).
2. [How to run a Python script to identify the queries in common between models](#queriescommon).
3. [How to add a filter to the visualization panel to exclude queries that are not in common](#filter).

## Extracting the unique query ids per model

The first step is to run an Elasticsearch query in order to extract the list of unique query ids for each model.

The following query involves limiting interactions to a specific time range (e.g. last 30 days) and allows us to extrapolate unique query ids associated with a given model (e.g. `modelA`) thanks to the term aggregation:

```
				
					GET interactions_index/_search
{
    "size": 0,
    "aggs" : {
        "categories" : {
            "terms" : { "field" : "queryId",  "size" : 65535, "order": { "_count": "desc"}}
        }
    },
    "query": {
        "bool": {
            "must": [
                {
                    "range": {
                        "timestamp": {
                            "gte": "now-30d/d",
                            "lte": "now/d"
                        }
                    }
                }
            ],
            "filter": [
                {
                    "match_all": {}
                },
                {
                    "match_phrase": {
                        "testGroup": "modelA"
                    }
                }
            ]
        }
    }
}
				
			
```

The query is a search request to an Elasticsearch index named “interactions\_index”, asking for aggregated data (“size”: 0 means no search hits will be returned).  
A **“terms” aggregation** groups the documents in the index based on the values of the `queryId` field and sorts them in descending order of frequency count.  
In the “must” clause there is a single condition, a range query on the timestamp field, that matches documents whose “timestamp” value is within the last 30 days.  
In the “filter” clause, the match\_phrase query matches documents that contain the exact phrase `model`A in the `testGroup` field.

Once executed, you need to extract the “buckets” part from the response and save it as a separate JSON file with the specified file name, i.e. `unique_query_ids_modelA.json`:

```
				
					{
    "buckets": [
        {
            "key": "4",
            "doc_count": 103
        },
        {
            "key": "3",
            "doc_count": 93
        },
        {
            "key": "2",
            "doc_count": 92
        },
        {
            "key": "0",
            "doc_count": 86
        },
        {
            "key": "10",
            "doc_count": 85
        }
    ]
}
				
			
```

In this example, we got a total of 5 query IDs for `modelA`.  
To get the unique query IDs for `modelB`, simply repeat the same query used earlier, but this time the value of the match\_phrase has to be changed to match `modelB`; once you have the response, extract the “buckets” section and save it to `unique_query_ids_modelB.json` file.

## Extracting queries in common between models

A python script can be used to find the common query ids between models by merging their respective lists of query ids.

The following script (named *query\_elaboration.py*) takes two JSON files as inputs (the ones created in step 1) and generates an output JSON file, which directly contains the Elasticsearch query for filtering common queries.

In particular, the script performs some operations on the data using the ‘pandas’ library, i.e. read JSON files into data frames and do an inner join to extract the values in common between the two data frames (i.e. queries in common from the two input files); finally the blue part of the code directly creates the Elasticsearch query that is a boolean query in combination with match phrase queries:

```
				
					import pandas as pd
import os
import sys

def reading_query_json(query_file):
    query_dataset = pd.read_json(query_file)
    query_dataset['buckets'] = query_dataset['buckets'].map(lambda x: x['key'])
    query_dataset.rename(columns={"buckets": "category"}, inplace=True)
    query_dataset.drop_duplicates(subset='category', keep='last', inplace=True)
    return query_dataset

def query_elaboration(modelA_query_file, modelB_query_file, output_dir):
    sys.stdout = open(output_dir + "common_queries.json", "w")

    modelA_query_dataset = reading_query_json(modelA_query_file)
    modelB_query_dataset = reading_query_json(modelB_query_file)

    common_queries = pd.merge(modelA_query_dataset, modelB_query_dataset)
    common_queries_length = len(common_queries)

    i = 0
    print("{\"query\":{")
    print("\"bool\":{")
    print("\"should\":[")
    for category in common_queries["category"]:
        if i != (common_queries_length - 1):
            print("{\"match_phrase\": {\"queryId\": \"" + category + "\"}},")
        else:
            print("{\"match_phrase\": {\"queryId\": \"" + category + "\"}}")
        i = i + 1
    print("],")
    print("\"minimum_should_match\": 1}}}")

    sys.stdout.close()

input_filename_modelA = sys.argv[1]
input_filename_modelB = sys.argv[2]
output_dir = sys.argv[3]
query_elaboration(input_filename_modelA, input_filename_modelB, output_dir)
				
			
```

Here is the command to run the script:

```
				
					python query_elaboration.py "/unique_query_ids_modelA.json" "/unique_query_ids_modelB.json" "/output/"
				
			
```

The output file called *common\_queries.json* will directly contain the Elasticsearch query to be integrated into the Kibana visualization to filter interactions, for example:

```
				
					{
  "query":{
    "bool":{
      "should":[
        {
          "match_phrase": {
            "queryId": "10"
          }
        },
        {
          "match_phrase": {
            "queryId": "3"
          }
        },
        {
          "match_phrase": {
            "queryId": "0"
          }
        }
      ],
      "minimum_should_match": 1
    }
  }
}
				
			
```

If you have a lot of queries, it is very useful because it allows you to get a list of queries in common and automatically generate the query to run in the filter.

## Adding the query to the visualization panel filter

In the final step, you can easily copy and paste the content of the *common\_queries.json* file into the Elasticsearch Query DSL (Domain Specific Language) of the “Add filter” pop-up:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/02/Schermata-2023-02-13-alle-10.28.44.png?fit=800%2C452&ssl=1)

Using this filter, the Kibana visualization will consider only interactions of the queries in common between the models being compared; in this example with `queryId` equal to 10, 0, and 3.

This is the last post about the Online Search Quality Evaluation with Kibana. You can read the other posts at these links:

* [Online search quality evaluation with kibana -introduction](https://sease.io/2023/03/online-search-quality-evaluation-with-kibana-introduction.html)
* [Online search quality evaluation with kibana – visualization examples](https://sease.io/2023/06/online-search-quality-evaluation-with-kibana-visualization-examples.html)

Thank you for reading!

## Need Help with this topic?​

If you're struggling with Kibana, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)