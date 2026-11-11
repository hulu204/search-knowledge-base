---
title: 'Offline Search Quality Evaluation: Rated Ranking Evaluator (RRE)'
company: Sease
tag: 评测
date: 2021-01-11
url: https://sease.io/2021/01/offline-search-quality-evaluation-rated-ranking-evaluator-rre.html
account: 
origin: harvest3-202607
---
## Introduction

With [Rated Ranking Evaluator Enterprise](https://sease.io/2019/12/road-to-rated-ranking-evaluator-enterprise.html) approaching soon, we take the occasion to explain in detail **why Offline Search Quality Evaluation is so important nowadays** and what you can do already with the Rated Ranking Evaluator open-source libraries.  
More news will come soon as we are approaching the V1 release date.  
Stay tuned!

## Search Quality Evaluation

Evaluation is fundamental in every scientific development.  
Scientists come up with hypotheses to model real-world phenomena and validate them by comparing their output with observations in nature.

Evaluation plays the exact key role in the field of information retrieval.  
Researchers and practitioners develop ranking models to explain the relationship between an information need expressed by a user **(query)** and information **(search result)** contained in available resources **(corpus)** and test these models by comparing their outcomes with a collection of observations **(implicit/explicit user feedback)**.

Search Quality has more than one interpretation however, this blog focuses only on one of them: the effectiveness of a search system to find the information relevant to the user **(search relevance)**.

There are two types of observations used for the purpose of evaluation:  
**(a) explicit feedback** (relevance annotations), and **(b) implicit feedback** (observable user interactions).

Most of the time, evaluation of information retrieval systems happens casually offline and/or online, with one or more stakeholders running a non-reproducible set of queries and evaluating search results from the feels of the moment (that may change later).

It’s necessary to bring a scientific structure to the process:

* + collect the ground truth observations **(Ratings from implicit/explicit feedback)**
  + run a finite and well-defined list of corresponding queries against the search system
  + compare the results with the **ground truth**, exploring different **search quality metrics**

This must be **reproducible,** **persistent** and **explainable**.

Here comes **Rated Ranking Evaluator** (hereafter **RRE**) an **open-source** library for offline **search quality evaluation** of **Apache Lucene-based** search engines (**Apache Solr** and **Elasticsearch**)

## What it is?

The [Rated Ranking Evaluator (RRE)](https://github.com/SeaseLtd/rated-ranking-evaluator) is a search quality evaluation library which evaluates the quality of results coming from a search system.

It helps a Search Engineer and the business stakeholders alike:

* + Are you tuning/implementing/changing/configuring a search infrastructure?
  + Do you want evidence of the improvements derived from your latest changes?

RRE helps you with that.

RRE formalises how well a search system satisfies the user information needs, at a “technical” level, combining the possibility of expressing ground truth ratings and assessing a search system quality with several evaluation metrics.  
RRE provides human-readable outputs also useful for non-technical stakeholders.

It encourages an **incremental**/**iterative**/**reproducible** approach during the development and the evolution of a search system: assuming we’re starting our system from version x.y: when it’s time to apply some relevant change to its configuration, the new version is evaluated in isolation  (source control helps here in keeping track of evolving configuration files).

RRE executes the evaluation process for all the search system versions in input and provides the delta/trend between them, so you can immediately spot improvements or regressions in the metrics of your interest.

## Input

In order to execute an evaluation, RRE needs the following things:

* + One or more **[corpus/test](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#corpus)**[**collection**](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#corpus): these are the representative datasets of a specific domain, that will be used for populating and querying a target search platform
  + One or more [**configuration sets**](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#configuration-sets): the Apache Solr/Elasticsearch configuration(s) that regulate your target search engine.
  + One or more [**rating sets**](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/What%20We%20Need%20To%20Provide#ratings): the ground truth, a list of <query, document> pairs associated with a relevance rating

## Ground Truth Definition (Ratings)

First of all, you need to define your ground truth:  
**<query, document>** pairs tagged with a **relevance label** that states how relevant a document is for the given query.

The rating files, which are provided in JSON format, are the core input of RRE.  
Each rating file is a structured set of **<query, document>** pairs (i.e. relevant documents for a given query).

In the rating file, we can define all aspects of the information needed supported by RRE: **corpus**, **topics**, **query groups**, and **queries**.

The current implementation uses a configurable judgement range:

e.g.

* + 1 => marginally relevant
  + 2 => relevant
  + 3 => very relevant

within the “relevant\_documents” node, you can provide the judgements in one of the following  (alternative) ways:

```
				
					"relevant_documents": {
   "docid1": {
       "gain": 2
   }, 
   "docid2": {
       "gain": 2
   }, 
   "docid3": {
       "gain": 3
   }, 
   "docid5": {
       "gain": 2
   }, 
   "docid99": {
       "gain": 3
   }
}
"relevant_documents": {
   "2": ["docid1", "docid2", "docid5"],
   "3": ["docid3", "docid99"]   
}
				
			
```

Note that if a document is not relevant for a given query, it doesn’t appear in the relevant list. In other words, there’s no “0” judgment value.

A more complete example of a rating file:

```
				
					{
  "index": "&lt;string&gt;",
  "corpora_field": "&lt;string&gt;",
  "id_field": "&lt;string&gt;",
  "topics": [
    {
      "description": "&lt;string&gt;",
      "query_groups": [
        {
          "name": "&lt;string&gt;",
          "queries": [
            {
              "template": "&lt;string&gt;",
              "placeholders": {
                "$key": "&lt;value&gt;",
              }
            }
          ],
          "relevant_documents": [
            {
              "document_id": {
                "gain": "&lt;number&gt;"
              }
            }
          ]
        }
      ]
    }
  ],
  "query_groups": [
    {
      "name": "&lt;string&gt;",
      "queries": [
        {
          "template": "&lt;string&gt;",
          "placeholders": {
            "$key": "&lt;value&gt;",
          }
        }
      ],
      "relevant_documents": [
        {
          "document_id": {
            "gain": "&lt;number&gt;"
          }
        }
      ]
    }
  ],
  "queries": [
    {
      "template": "&lt;string&gt;",
      "placeholders": {
        "$key": "&lt;value&gt;",
      }
    }
  ]
}
				
			
```

* + `index`: index name in ElasticSearch/collection name in Solr
  + `corpora_field`: not required for external Solr/ElasticSearch, corresponds to corpus filename
  + `id_field`: Field in the schema that represents document ID
  + `topics`: optional list of topics and/or query groups
    - `description`: Title of a topic used in reporting output
    - `query_groups`: list of queries that are grouped with the same name and topic
      * `name`: query name used for the reporting
      * `queries`: list of queries to execute for a topic
        + `template`: String name for the template this query uses
        + placeholders: Object of key-value pairs to substitute in the template
    - `relevant_documents`: list objects with mapping documents to gain or relevance values
  + `query_groups`: list of objects with related queries. Can exist outside of `topics`, is optional
  + `queries`: required\* list of objects for template and placeholder substitutions for evaluations.
    - \*If `topics` and `query_groups` do not exist

## Query Templates

For each query (or for each query group) it’s possible to define a query template, which is the definition of the query containing one or more placeholders. Then, in the rating file, you can reference one of those defined templates and you can provide a value for each placeholder.  
Templates have been introduced to:

* + allow common query management between search platforms
  + define complex queries
  + define runtime parameters that cannot be statically determined (e.g. filters)

In the picture below you can see three examples: the first two are examples of Solr queries, while the third is using Elasticsearch.

![query](https://i0.wp.com/sease.io/wp-content/uploads/2021/01/42095548-38ffb2ba-7bb3-11e8-9d0a-36c74cd4f954.png?fit=800%2C601&ssl=1)

You may also create multiple version folders (v1.0, v1.1, v1.2, etc) and keep different query template versions in those folders. This will run evaluations for each query template version and allows you easily to compare across query template changes.

## Search Engine Configuration/ External Search Engine

Once defined the ground truth, it’s possible to define a target Search System for the evaluation.  
The Open Source version of RRE supports the **embedding of a search instance** (from config files) and an **external running instance**.

## Configuration Sets

RRE encourages a reproducible approach: keep track of your versions and assign to each of your versions an immutable tag.  
In this way, we’ll end up having the historical progression of our system, and RRE will be able to make comparisons and reproduce evaluations.  
The actual content of the configuration sets actually depends on the target search platform. For Apache Solr, each version folder (see the image below) contains one or more Solr cores. Elasticsearch instead, contains a JSON file (the “index-shape.json” in the picture below) which contains the index settings & mappings.

![config set](https://i0.wp.com/sease.io/wp-content/uploads/2021/01/42095032-cccc6d64-7bb1-11e8-8523-42fa33f1f9e0-1.png?fit=800%2C685&ssl=1)

## Execution

The best way to run an RRE evaluation is to use the Maven plugin, setting up a Maven project to import RRE libraries and execute them.  
A detailed step-by-step guide is at this link:  
[Run your evaluation!](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/Maven%20Archetype)

## Output

The output evaluation data is available:

* as a **JSON file**: for further elaborations
* as a **spreadsheet**: for delivering the evaluation results to someone else (e.g. a business stakeholder)
* in a [**Web Console**](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki/RRE%20Server) where metrics and their values get refreshed in real-time (after each build)

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/rre-spreadsheet.png?fit=1958%2C414&ssl=1)

![](https://i0.wp.com/sease.io/wp-content/uploads/2018/07/42096917-edefdd50-7bb6-11e8-9d1a-21356b453192.png?fit=2546%2C1137&ssl=1)

###### Links

* The project [repository](https://github.com/SeaseLtd/rated-ranking-evaluator)
* The project [Wiki](https://github.com/SeaseLtd/rated-ranking-evaluator/wiki)

## Need Help With This Topic?​​

If you’re struggling to run an RRE evaluation, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling to run an RRE evaluation, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)