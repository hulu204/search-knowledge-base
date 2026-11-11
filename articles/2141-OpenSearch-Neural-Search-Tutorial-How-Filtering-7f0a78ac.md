---
title: 'OpenSearch Neural Search Tutorial: How Filtering Works'
company: Sease
tag: 召回
date: 2024-03-14
url: https://sease.io/2024/03/opensearch-neural-search-tutorial-how-filtering-works.html
account: 
origin: harvest3-202607
---
Here we are with a new episode where we continue to explore the neural search capabilities of OpenSearch.  
If you missed the previous blog posts here is a short recap:

* In the first blog post, we explored the [OpenSearch Neural Search Plugin](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html) through an end-to-end tutorial
* In the second blog post, you can find [additional useful tools to manage ML models](https://sease.io/2024/01/opensearch-neural-search-plugin-tutorial-additional-useful-tools.html) and suggestions to choose the best library for approximate neighbour search
* In a third blog post, we explored the [OpenSearch k-NN Plugin](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html), through an end-to-end tutorial, describing the three different approaches for retrieving the k-nearest neighbours

We want to focus this blog post on discussing Filtering, exploring its importance, examining the integration of filters with the neural search in OpenSearch to enhance search result accuracy, and addressing how filtering impacts performance.  
We already talked about post-filtering in the first blog post, but the latest versions have introduced new features that deserve a detailed exploration in a dedicated post.

## workflow to implement k-nearest neighbours search using filters

Let’s begin by exploring the end-to-end workflow to implement ***k-nearest neighbours* search USING FILTERS**:

1. Run OpenSearch
2. Upload a Large Language Model (with Model Access Control)
   * Register a Model Group
   * Register a pre-trained model to the model group
   * Deploy the model
3. Indexing phase
   * Create an ingest pipeline
   * Create an index of vectors
   * Index documents
4. Query phase using Filters
   * Pre-filtering
     + Scoring script filter
   * Post-filtering
     + Boolean post-filter
     + Post filter parameter
   * Hybrid filtering 
     + Efficient k-NN filtering

Up to the step “Create an ingest pipeline”, the pipeline remains identical, which means that you can follow the information and commands already described in the previous [blog post](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html) as they are.  
If you have not yet configured and run OpenSearch, uploaded and loaded into memory a large language model for creating vectors, and defined a specific ingest pipeline, these steps must be completed first.

In this blog post, we will only report requests relating to the creation of the index and indexing of documents. This is because we need to add a field that will be used to demonstrate how document filtering works by showing the behaviour of filtering queries.

### Indexing Phase

##### CREATE AN INDEX OF VECTORS

**REQUEST**

```
				
					curl --location --request PUT 'https://localhost:9200/neural_index_for_filtering' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{
    "settings": {
        "index.knn": true,
        "default_pipeline": "knn_pipeline"
    },
    "mappings": {
        "properties": {
            "general_text_vector": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "engine": "lucene"
                }
            },
            "general_text": { 
                "type": "text"            
            },
            "color": {
                "type": "text"
            }
        }
    }
}'
				
			
```

With this request, the index named **`neural_index_for_filtering`** was created and we defined 3 fields: ***`general_text_knn`*** to store vector embeddings, ***`general_text`*** the source field from which to create embeddings and `color`, name of a colour randomly assigned from a list of values [green, white, red, black, yellow, blue, orange, and pink].

##### INDEX DOCUMENTS

**REQUEST**

```
				
					curl --location --request POST 'https://localhost:9200/_bulk' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{"create":{"_index":"neural_index_for_filtering", "_id":"0"}}
{"general_text":"The presence of communication amid scientific minds was
equally important to the success of the Manhattan Project as scientific
intellect was. The only cloud hanging over the impressive achievement of
the atomic researchers and engineers is what their success truly meant;
hundreds of thousands of innocent lives obliterated.","color":"red"}
{"create":{"_index":"neural_index_for_filtering", "_id":"1"}}
{"general_text":"The Manhattan Project and its atomic bomb helped bring an
end to World War II. Its legacy of peaceful uses of atomic energy continues
to have an impact on history and science.","color":"black"}
{"create":{"_index":"neural_index_for_filtering", "_id":"2"}}
{"general_text":"Essay on The Manhattan Project - ...'
				
			
```

Execution of this command will result in the indexing of 10k [MS MARCO](https://microsoft.github.io/msmarco/) documents, each containing the text with the corresponding vector (created using the knn\_pipeline) and a random colour.

### Query phase using filters

Alright, now let’s move on to the most interesting part of our blog: how to use filters in vector queries.

To refine k-NN results, the filter can be applied in three different phases:   
**– before search (pre-filtering)  
– after search (post-filtering)  
– during search (hybrid of pre- and post-filtering)**

The [OpenSearch documentation](https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/#filtered-search-optimization) includes a helpful section that guides you in selecting the best filtering method, depending on your dataset and use case (such as index documents count, the restrictiveness of the filter, and the number of nearest neighbours you want to retrieve) to either maximize recall or minimize latency.

##### PRE-FILTERING

If you want to limit the number of matched documents passed to the vector function and then search for the nearest neighbours, it’s necessary to implement a pre-filtering. The Scoring script filter is the method by which OpenSearch allows to do this.

###### SCORING SCRIPT FILTER

**Type of search:** Exact k-NN

This approach pre-filters your documents and then identifies nearest neighbors, using a brute-force exact k-NN search:

```
				
					curl --location --request GET 'https://localhost:9200/neural_index_for_filtering/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "size": 3,
  "query": {
    "script_score": {
      "query": {
        "bool": {
          "filter": {
            "term": {
              "color": "white"
            }
          }
        }
      },
      "script": {
        "lang": "knn",
        "source": "knn_score",
        "params": {
          "field": "general_text_knn",
          "query_value": [
                        -0.009013666,
                        -0.07266349,
                        ...
                        -0.1163235
                    ],
          "space_type": "cosinesimil"
        }
      }
    }
  },
  "_source": [
     "general_text",
     "color"
  ]
}'
				
			
```

N.B. The query value was obtained using the Predict API, as explained in **step 4.1 QUERY INFERENCE** of this blog post about [OpenSearch Knn Plugin](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html).

**RESPONSE**

```
				
					{
    ...
    "hits": {
        "total": {
            "value": 1214,
            "relation": "eq"
        },
        "max_score": 1.3680089,
        "hits": [
            {
                "_index": "neural_index_for_filtering",
                "_id": "7691",
                "_score": 1.3680089,
                "_source": {
                    "color": "white",
                    "general_text": "A. A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS."
                }
            },
            {
                "_index": "neural_index_for_filtering",
                "_id": "7690",
                "_score": 1.3331752,
                "_source": {
                    "color": "white",
                    "general_text": "Download article as a PDF. An employer identification number (EIN), also called a tax ID number or taxpayer ID, is required for most business entities. As its name implies, this is the number used by the Internal Revenue Service (IRS) to identify businesses with respect to their tax obligations."
                }
            },
            {
                "_index": "neural_index_for_filtering",
                "_id": "4206",
                "_score": 1.3285325,
                "_source": {
                    "color": "white",
                    "general_text": "All vehicles registered in the UK must have a unique, stamped-in vehicle identification number (."
                }
            }
        ]
    }
}
				
			
```

The results are prefiltered by the colour white and then only the documents from this subset are considered candidates for the vector retrieval.  
Having set *size=3*, we got the best 3 documents for the query “What is a bank transit number” **with the “white” colour** from a subset of 1214.

##### POST-FILTERING

OpenSearch offers two filtering strategies for this approach: the Boolean filter and the post-filter parameter.   
The “limit” of post-filtering refers to the fact that it can return significantly fewer results than k if a restrictive filter is applied.

###### BOOLEAN FILTER

**Type of search:** Approximate nearest neighbour (ANN)  
**Supported engines and methods**: lucene, nmslib, faiss

Suppose to execute a standard approximate nearest neighbours search (ANN) with *k*=3, the response contains three documents (hits) with the following colours (in order):

```
				
					"_id": "7686", "color": "yellow"
"_id": "7691", "color": "white"
"_id": "7692", "color": "black"
				
			
```

Now suppose to make a combined query with both a post-filter and a neural query:

```
				
					curl --location --request GET 'https://localhost:9200/neural_index_for_filtering/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
    "_source": [
        "color"
    ],
    "query": {
        "bool": {
            "filter": {
                "term": {
                    "color": "white"
                }
            },
            "must": {
                "neural": {
                    "general_text_knn": {
                        "query_text": "what is a bank transit number",
                        "model_id": "ia1B8IsBvXr78vpjPHd1",
                        "k": 3
                    }
                }
            }
        }
    }
}'
				
			
```

**RESPONSE**

```
				
					{
    ...
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 0.44169965,
        "hits": [
            {
                "_index": "neural_index_for_filtering",
                "_id": "7691",
                "_score": 0.44169965,
                "_source": {
                    "color": "white"
                }
            }
        ]
    }
}
				
			
```

This query aims to obtain the best three documents for the query “*what is a bank transit number”*, having set *k=3*; but in the response, we obtain 1 hit with a single “*white*” document.  
This is because OpenSearch first executes the neural query obtaining 3 documents: yellow, **white**, and black, and then it filters them by colour keeping only the white one.

To provide a complete overview, we also report the query using the *KNN plugin*, thus passing the query vector in the request instead of using the LLM internally for the inference:

```
				
					curl --location --request GET 'https://localhost:9200/neural_index_for_filtering/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
  "_source": [
        "color"
    ],
  "size": 3,
  "query": {
    "bool": {
      "filter": {
        "bool": {
          "must": [
            {
              "term": {
                "color": "white"
              }
            }
          ]
        }
      },
      "must": [
        {
          "knn": {
            "general_text_knn": {
              "vector": [
                        -0.009013666,
                        -0.07266349,
                        ...
                        -0.1163235
                    ],
              "k": 3
            }
          }
        }
      ]
    }
  }
}'
				
			
```

As written in the [documentation](https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn): “The two query parts are executed independently, and then the results are combined based on the query operator (`should`, `must`, and so on) provided in the query”.

###### POST FILTER PARAMETER

**Type of search:**Approximate nearest neighbour (ANN)  
**Supported engines and methods**: lucene, nmslib, faiss

You can simply use the **`post_filter`** parameter to apply filter to the k-NN results:

```
				
					curl --location --request GET 'https://localhost:9200/neural_index_for_filtering/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
    "size": 6,
    "_source": [
        "color"
    ],
    "query": {
        "neural": {
            "general_text_knn": {
                "query_text": "what is a bank transit number",
                "model_id": "ia1B8IsBvXr78vpjPHd1",
                "k": 3
            }
        }
    },
    "post_filter": {
        "term": {
            "color": "white"
        }
    }
}'
				
			
```

The response is exactly the same as with the previous method.

To provide a complete overview, we also report the query using the KNN plugin, thus passing the query vector in the request instead of using the LLM internally for the inference:

```
				
					{
    "_source": [
        "color"
    ],
    "query": {
        "knn": {
            "general_text_knn": {
                "vector": [
                    -0.009013666,
                    -0.07266349,
                    ...
                    -0.1163235
                ],
                "k": 3
            }
        }
    },
    "post_filter": {
        "term": {
            "color": "white"
        }
    }
}
				
			
```

##### HYBRID FILTERING

###### EFFICIENT KNN FILTERING

**Type of search:**Approximate nearest neighbor (ANN)  
**Supported engines and methods**:

* **lucene**
  + **HNSW** algorithm (k-NN plugin versions 2.4 and later)
* **faiss**
  + **HNSW** algorithm (k-NN plugin versions 2.9 and later)
  + **IVF** algorithm (k-NN plugin versions 2.10 and later)

This method ensures that `k` matching documents are returned since the filter query is applied **during** the k-NN search.

Here is the k-NN search query with filters:

```
				
					curl --location --request GET 'https://localhost:9200/neural_index_for_filtering/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
    "_source": [
        "color"
    ],
    "query": {
        "neural": {
            "general_text_knn": {
                "query_text": "what is a bank transit number",
                "model_id": "ia1B8IsBvXr78vpjPHd1",
                "k": 3,
                "filter": {
                    "bool": {
                        "must": [{
                            "term": {
                                "color": "white"
                            }
                        }]
                    }
                }
            }
        }
    }
}'
				
			
```

**RESPONSE**

```
				
					{
    "hits": {
        "total": {
            "value": 3,
            "relation": "eq"
        },
        "max_score": 0.44169965,
        "hits": [
            {
                "_index": "neural_index_for_filtering",
                "_id": "7691",
                "_score": 0.44169965,
                "_source": {
                    "color": "white"
                }
            },
            {
                "_index": "neural_index_for_filtering",
                "_id": "7690",
                "_score": 0.42851335,
                "_source": {
                    "color": "white"
                }
            },
            {
                "_index": "neural_index_for_filtering",
                "_id": "4206",
                "_score": 0.42681506,
                "_source": {
                    "color": "white"
                }
            }
        ]
    }
}
				
			
```

The above request executes a k-NN query that searches for the top three documents for the query “*What is a bank transit number”* and with the colour “*white*“.

To provide a complete overview, we also report the query using the KNN plugin, thus passing the query vector in the request instead of using the LLM internally for the inference:

```
				
					curl --location --request GET 'https://localhost:9200/neural_index_for_filtering/_search' --header 'Content-Type: application/json' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --data '{
    "_source": [
        "color"
    ],
    "query": {
        "knn": {
            "general_text_knn": {
                "vector": [
                    -0.009013666,
                    -0.07266349,
                    ...
                    -0.1163235
                ],
                "k": 3,
                "filter": {
                    "bool": {
                        "must": [{
                            "term": {
                                "color": "white"
                            }
                        }]
                    }
                }
            }
        }
    }
}'

				
			
```

In this case, the Lucene filter was used, as indicated by the specification of the “**lucene”** engine in the request mapping when creating the **neural\_index\_for\_filtering** index.

If you want to use the **faiss** filter, a new index must be created, specifying **`faiss`** as the engine in the mapping, for example:

```
				
					curl --location --request PUT 'https://localhost:9200/neural_index_for_filtering_faiss' --header 'Authorization: Basic YWRtaW46YWRtaW4=' --header 'Content-Type: application/json' --data-raw '{
    "settings": {
        "index.knn": true,
        "default_pipeline": "knn_pipeline"
    },
    "mappings": {
        "properties": {
            "general_text_vector": {
                "type": "knn_vector",
                "dimension": 384,
                "method": {
                    "name": "hnsw",
                    "engine": "faiss"
                }
            },
            "general_text": { 
                "type": "text"            
            },
            "color": {
                "type": "text"
            }
        }
    }
}'
				
			
```

Then the data must be added and indexed to it.

### DIFFERENCE BETWEEN LUCENE AND FAISS FILTER

As we have already seen, for both Lucene and Faiss engines, an approach has been studied that tries to preserve the number of results returned while taking into account how much the filter narrows down the result. This balance ensures efficient and relevant k-NN search results.

For the Lucene engine, the implementation supports k-NN searches using Hierarchical Navigable Small World (HNSW) graphs. In the case of the Faiss engine, the implementation supports k-NN searches using both HNSW and IVF algorithms.

Both Lucene and Faiss algorithms use similar criteria to determine their search methods, choosing between exact k-NN searches with pre-filtering or approximate searches with modified post-filtering.  
These decisions are based on common key factors such as the number of documents in the index, the amount remaining after applying filters, and the maximum number of vectors to be returned.  
The Faiss algorithm additionally considers extra parameters like specific thresholds for filtering (set at the index level) and a limit on the number of distance calculations allowed during exact searches. By setting a cap on these computations, Faiss ensures that the search remains efficient, even while striving for accuracy. These additional parameters in Faiss are designed to fine-tune the balance between search accuracy and computational efficiency.

If you are interested in learning more, the OpenSearch documentation [[1]](https://opensearch.org/docs/latest/search-plugins/knn/filter-search-knn/#efficient-k-nn-filtering), in particular the flowchart images, provides a detailed explanation of the specific strategy used by Lucene’s algorithm ([KnnVectorQuery](https://lucene.apache.org/core/9_4_0/core/org/apache/lucene/search/KnnVectorQuery.html)) and Faiss’s algorithm to optimize search performance.

## What’s Next?

I hope this post has been helpful in better understanding how filtering works in OpenSearch.

***Keep an eye out for our upcoming blog posts that will cover a wide range of topics, including hybrid search, sparse search, multimodal search, and many more.***

## Need Help With This Topic?​​

If you’re struggling with filtering in OpenSearch, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with filtering in OpenSearch, don't worry - we're here to help! Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)