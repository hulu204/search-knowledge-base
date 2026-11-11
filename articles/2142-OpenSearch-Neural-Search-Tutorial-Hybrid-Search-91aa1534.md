---
title: 'OpenSearch Neural Search Tutorial: Hybrid Search'
company: Sease
tag: 召回
date: 2024-04-03
url: https://sease.io/2024/04/opensearch-neural-search-tutorial-hybrid-search.html
account: 
origin: harvest3-202607
---
Hi OpenSearch enthusiasts,

As already mentioned in the latest blog post about [how filtering works](https://sease.io/2024/03/opensearch-neural-search-tutorial-how-filtering-works.html), the journey to discover the new OpenSearch features continues, and in this blog post we are going to explore how to perform Hybrid searches.

OpenSearch supports both lexical and semantic search. **Hybrid search combines them, exploiting the strengths of textual and vector search techniques** to improve search results and relevance.

The naive hybrid approach, which can be applied using [compound query types](https://opensearch.org/docs/latest/query-dsl/compound/index/), consists of an arithmetical combination of the scores returned by each query type. However, this approach has inherent limitations and inaccuracies:  
– Different query types produce scores on different scales.  
– OpenSearch typically calculates scores at the shard level, but a global standardization of scores across all shards is necessary.

**In OpenSearch 2.10, a new implementation of hybrid search has been introduced, allowing for the combination and normalization of query relevance scores.**  
We will give a detailed description of this new feature through our end-to-end testing experience.

## Workflow

Let’s begin by exploring the end-to-end workflow to perform a **Hybrid search** using OpenSearch.

1. Run OpenSearch (version >= 2.10 required)
2. Upload a Large Language Model (with Model Access Control)
   * Register a Model Group
   * Register a pre-trained model to the model group
   * Deploy the model
3. Indexing phase
   * Create an ingest pipeline
   * Create an index of vectors
   * Index documents
4. Query phase
   * **Create a search pipeline with a normalization processor**
   * **Hybrid Query**

Up to the step “Index documents”, the pipeline remains identical, which means that you can follow the information and commands already described in the previous blog post ([about the OpenSearch Knn plugin tutorial](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html)) as they are.  
If you have not yet configured and run OpenSearch, uploaded and loaded into memory a large language model for text embeddings and indexed data with vectors, these steps must be completed first.

To perform a hybrid search, it is necessary to execute the last two steps:  
– Create a search pipeline with a normalization processor  
– Hybrid Query

## Hybrid Search

Hybrid search consists of two primary components:

* + The **hybrid query** allows for the definition, execution, and collection of results from multiple individual queries across each shard.

* + The **normalization processor**, integrated within a search pipeline, gathers these results at the coordinator node level. It then normalizes scores for each query and merges them into the final combined result. Internally, the type of search it uses is known as **query\_then\_fetch** [[1](https://opensearch.org/docs/latest/search-plugins/search-pipelines/normalization-processor)].

Hybrid queries are enabled by default. To turn off hybrid queries in your cluster, change the setting `plugins.neural_search.hybrid_search_disabled` to **`true`** in the `opensearch.yml` file.

###### CREATE A SEARCH PIPELINE WITH A NORMALIZATION PROCESSOR

To implement a hybrid search, you must configure a search pipeline with a normalization-processor that runs at search time.

A search pipeline enables the construction and reuse of various components like “result rerankers” and “query rewriters”, simplifying the management of search queries and results in OpenSearch.  
It consists of a sequence of processors, each carrying out specific modular tasks, to customize search results.

This is the request to create a search pipeline named ***hybrid\_search\_pipeline***:

```
				
					curl --location --request PUT 'https://localhost:9200/_search/pipeline/hybrid_search_pipeline' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "description": "Post processor for hybrid search",
  "phase_results_processors": [
    {
      "normalization-processor": {
        "normalization": {
          "technique": "min_max"
        },
        "combination": {
          "technique": "arithmetic_mean",
          "parameters": {
            "weights": [
              0.3,
              0.7
            ]
          }
        }
      }
    }
  ]
}'
				
			
```

where the available *request fields* are:  
– **description** [Optional – String]: to describe the processor.  
– **normalization.technique** [Optional – String]: is the technique for normalizing scores. In this case **`min_max`** (default), but a valid value is also **`l2`**.  
– **combination.technique** [Optional – String]**:** is the technique for combining scores. In this case **`arithmetic_mean`** (default), but valid values are also **`geometric_mean`**, and **`harmonic_mean`**.  
– **combination.parameters.weights** [Optional – Array of floats]**:** to specify the weights to use for each query clause. In this case 0.3 for the first query clause and 0.7 for the second query clause. Acceptable values fall within the [0.0, 1.0] range (representing decimal percentages), which means that a value nearer to 1.0 indicates a higher weighting for a query clause. The number of values in the weights array should match the number of query clauses (in this case 2), and their total must add up to 1.0 (0.3 + 0.7=1.0).

The search pipeline created, intercepts search results at the middle stage of processing and applies the “*normalization processor*“, designed for post-processing hybrid search results. Specifically, in this case, it uses the “min\_max” technique for normalization and, additionally, it combines results using the “*arithmetic\_mean*” technique, where the combination is weighted with 0.3 for one set of results and 0.7 for another.

You can create multiple search pipelines and experiment with different normalization techniques, combination techniques and weights.   
Here is the command if you want to view all search pipelines created**:**

```
				
					curl --location --request GET 'https://localhost:9200/_search/pipeline/' --header 'Authorization: Basic YWRtaW46YWRtaW4='
				
			
```

**RESPONSE**

```
				
					{
    "hybrid_search_pipeline": {
        "description": "Post processor for hybrid search",
        "phase_results_processors": [
            {
                "normalization-processor": {
                    "normalization": {
                        "technique": "min_max"
                    },
                    "combination": {
                        "technique": "arithmetic_mean",
                        "parameters": {
                            "weights": [
                                0.3,
                                0.7
                            ]
                        }
                    }
                }
            }
        ]
    }
}
				
			
```

We only created one search pipeline, otherwise, we would have seen more.

##### QUERY PHASE

###### HYBRID QUERY

The following is the request to perform the hybrid search:

```
				
					curl --location --request GET 'https://localhost:9200/my_neural_index/_search?search_pipeline=hybrid_search_pipeline' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "size": 5,
  "_source": {
    "exclude": [
      "general_text_knn"
    ]
  },
  "query": {
    "hybrid": {
      "queries": [
        {
          "match": {
            "general_text": {
              "query": "federal"
            }
          }
        },
        {
          "neural": {
            "general_text_knn": {
              "query_text": "what is a bank transit number",
              "model_id": "loaded_neural_model_id",
              "k": 3
            }
          }
        }
      ]
    }
  }
}'
				
			
```

In the command, replace *“loaded\_neural\_model\_id”* with the actual ID of the model you have deployed and loaded.

The only parameter supported by hybrid queries is:  
**queries** [REQUIRED]: an array consisting of one or more query clauses, which are used for matching documents. For a document to be included in the results, it must match at least one query clause. The maximum number of query clauses accepted is 5.

In the above query, we have used the search pipeline created before named **hybrid\_search\_pipeline** and we have specified 2 query clauses; both the match and neural query clauses are combined and their scores are combined and normalized using the chosen techniques.

**RESPONSE**

```
				
					{
  ...
    "hits": {
        "total": {
            "value": 5,
            "relation": "eq"
        },
        "max_score": 0.7,
        "hits": [
            {
                "_index": "my_neural_index",
                "_id": "7686",
                "_score": 0.7,
                "_source": {
                    "general_text": "A. A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS. Your tax ID number is used to identify your business to several federal agencies responsible for the regulation of business."
                }
            },
            {
                "_index": "my_neural_index",
                "_id": "7555",
                "_score": 0.3,
                "_source": {
                    "general_text": "Filed under: OPM Disability Process | Tagged: appeal deadlines during the fers disability process, average time frame for fers disability retirement, civil service disability, federal disability law blog, federal disability process timelines, federal disability retirement application and process, federal disabled employees and the patience needed, ..."
                }
            },
            {
                "_index": "my_neural_index",
                "_id": "8014",
                "_score": 0.2981534,
                "_source": {
                    "general_text": "Federal law (5 U.S.C. 6103) establishes the public holidays listed in these pages for Federal employees. Please note that most Federal employees work on a Monday through Friday schedule."
                }
            },
            {
                "_index": "my_neural_index",
                "_id": "7691",
                "_score": 0.29244623,
                "_source": {
                    "general_text": "A. A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS."
                }
            },
            {
                "_index": "my_neural_index",
                "_id": "2659",
                "_score": 0.2786232,
                "_source": {
                    "general_text": "The authority of the Federal Reserve Banks to issue notes comes from the Federal Reserve Act of 1913. Legally, they are liabilities of the Federal Reserve Banks and obligations of the United States government."
                }
            }
        ]
    }
}
OpenSearch returns 5 results (size=5), after combining the most relevant matches from both the BM25 query (documents containing the word 'federal') and the neural query (documents matching the semantic meaning of 'what is a bank transit number').
The relevance scores of documents from each query clause are merged into a single score through the use of a search pipeline.

To set a default search pipeline for an index, you can also configure it using the API, rather than specifying the search pipeline in every request:

curl --location --request PUT 'https://localhost:9200/my_neural_index/_settings' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "index.search.default_pipeline" : "hybrid_search_pipeline"
}'
				
			
```

## What's Next?

I hope this post has been helpful in better understanding how hybrid search works in OpensSearch.

***Keep an eye out for our upcoming blog posts that will cover a wide range of topics, including sparse search, multimodal search, and many more.***

## Need Help With This Topic?​​

If you’re struggling with Neural Search in OpenSearch, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Neural Search in OpenSearch, don't worry - we're here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)