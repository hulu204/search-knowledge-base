---
title: 'Apache Solr New Learning To Rank Cache'
company: Sease
tag: 排序
date: 2026-03-23
url: https://sease.io/2026/03/apache-solr-new-learning-to-rank-cache.html
account: 
origin: harvest3-202607
---
Hi everyone!

If you are reading this blog post, it means you are curious to learn more about the integration of a new Learning To Rank cache in Solr!

Solr already comes with a cache for the learning to rank feature vectors, but it works only for [feature logging](https://solr.apache.org/guide/solr/latest/query-guide/learning-to-rank.html#logging-features) and not for the reranking phase.

Here is where our contribution comes! **We added a new Learning To Rank cache that is used in both phases by Solr to speed up the search**, and that will be available in Solr 10.0. Here is the related [PR](https://github.com/apache/solr/pull/3433).

To understand the content of this blog post, you need to already know the basics of Learning To Rank in Solr. If you want to know more about it, we offer [Learning to Rank training sessions](https://sease.io/training/learning-to-rank-training) and have published many blog posts on the topic. Read more about them [here](https://sease.io/?s=learning+to+rank)!

## Current Cache Limitations

The main problem we wanted to address with our contribution is the fact that the Learning To Rank cache (*prior to Solr 10*) only works on the specific scenario of feature logging. It is not available for reranking. If we therefore use Solr for reranking only with no need for feature logging, we have no benefits at all from the current implementation, but reranking is often an expensive step that we would like to speed up.

The *prior to Solr 10* integrated cache for Learning To Rank only works for features logging in a specific scenario:

1. We are doing both reranking (*passing the rq parameter*) and logging (*passing the [features] transformer in fl*);
2. We are using the same feature store for both reranking and logging.

Also, the performance is not so good as we will see later on in the benchmark section of this blog post.

## Our New Implementation

The reason why we decided to bring this contribution to Solr is to give the possibility to the user to speed up the reranking process, making the cache available for both logging and reranking steps. We therefore integrated a new cache, removing the old one, which is a single cache used by both the reranking and logging phases.

##### Cache Key - Value

We decided to use, as a key in our cache, a combination of the following elements:

1. Lucene **document ID**: as a representative of the document fields’ content;
2. The **feature store name**: as a representative of the features definition we are considering for the computation. *This is added to the cache key only if we are NOT doing reranking or if we are doing reranking but require logging all the features, as determined by the* ***[logAll](https://solr.apache.org/guide/solr/latest/query-guide/learning-to-rank.html#feature-logging-parameters)*** *parameter.*
3. The **reranking model name**: as a representative of the features definition we are considering for the computation (the features used by the model could be a subset of the features defined in the corresponding feature store). *This is added to the cache key only if we are doing reranking and we require logging only the model features.*
4. The [**External Features Information**](https://solr.apache.org/guide/solr/latest/query-guide/learning-to-rank.html#external-feature-information) (efi) passed at query time: a change in the value of these features will bring a change in the computed feature vector.

**A note on the Lucene document ID for Solr/Lucene experts reading this blog post.**

During reranking and logging, the only IDs available for use in the cache key are the Lucene document ID and the model scorer’s activeDoc. We do not have access to the Solr unique key.

Because activeDoc is local to the current Lucene index segment, it cannot be used as a reliable cache key; different segments can assign the same activeDoc value to different documents, resulting in collisions. The Lucene document ID combines this segment-local ID with a docBase value that identifies the segment, which is why we use it instead.

However, this Lucene document ID is transient and may change over time, which prevents us from supporting automatic cache warming (like for the document cache in Solr). As future work, we plan to incorporate the Solr unique key into our cache key to enable autowarming and improve overall cache behaviour.

##### Cache Usage

Let’s see in detail how the cache is used in different scenarios.

1. Only **reranking**: Every time a reranking query is executed, for each document to rerank, Solr performs a lookup in the cache to retrieve the required feature vector. If none is found, the feature vector is computed, and a new entry is added to the cache. If the vector is already in the cache, it is directly returned without the necessity to compute it again.
2. Only **feature logging**: every time a query is executed, for each document to return, Solr performs a lookup in the cache to retrieve the required feature vector. If none is found, the feature vector is computed, and a new entry is added to the cache. If the vector is already in the cache, it is directly returned without the necessity to compute it again.
3. **Reranking** **AND** **feature logging**: in this scenario, Solr first does reranking, then creates the response for logging. Every time a query is executed, for each document to rerank, Solr performs a lookup in the cache to retrieve the required feature vector. If none is found, the feature vector is computed, and a new entry is added to the cache. If the vector is already in the cache, it is directly returned without the necessity to compute it again.   
   ***NOTE:** Since Solr first executes reranking and then logging, if we are using/requiring the same features in both steps, Solr, during logging, will always find the needed vector in the cache.* *This was added during the first reranking phase. This is true as long as the cache has an appropriate size that allows us to store all the needed feature vectors.*

## Benchmark

In this benchmark, we compare:

1. *Apache Solr <10* implementation with the *feature values cache disabled* vs *our contribution* with *LTR* *cache disabled*: this has been done to verify that our contribution does not negatively affect the basic LTR execution.
2. *Apache Solr <10* implementation with the *feature values cache enabled* vs *our contribution* with the *LTR cache enabled*: this has been done to show the impact of our newly added cache.

In both scenarios, we compare:

1. *Pure reranking*: no logging of the features required. In this case, we tested the feature extraction timing when doing reranking.
2. *Pure logging*: both reranking and logging are executed. In this case, we used a “dummy ltr model”, e.g. a very simple linear model, to get the right feature extraction estimation time from the Solr qTime parameter. See [this](https://sease.io/2022/01/apache-solr-learning-to-rank-feature-extraction-and-qtime.html) blog post to better understand the reasons behind this choice for logging evaluation.

##### Feature Store

We defined a feature store of 200 complex features, such as:

```
				
					[
  {
    "store": "test_store",
    "name": "feature_0",
    "class": "org.apache.solr.ltr.feature.SolrFeature",
    "params": {
      "q": "{!func}tf(field_0, ${user_query})"
    }
  },
  {
    "store": "test_store",
    "name": "feature_1",
    "class": "org.apache.solr.ltr.feature.SolrFeature",
    "params": {
      "q": "{!func}idf(field_1, ${user_query})"
    }
  },
  {
    "store": "test_store",
    "name": "feature_2",
    "class": "org.apache.solr.ltr.feature.SolrFeature",
    "params": {
      "q": "{!func}log(tf(field_2, ${user_query}))"
    }
  },

...

]
				
			
```

We chose features hard to compute to stress the system and simulate a “worst case” scenario.

##### Model Store

We used a “dummy” model, e.g. a very simple linear model, to reduce the effort in computing the document score (which is of no interest for this benchmark) as much as possible and obtain a qTime that reflects the “pure” feature extraction.

```
				
					{
  "name": "linear_model_200_features",
  "class": "org.apache.solr.ltr.model.LinearModel",
  "store": "test_store",
  "features": [
    {
      "name": "feature_0"
    },
    {
      "name": "feature_1"
    },
    ...
    {
      "name": "feature_200"
    }
  ],
  "params": {
    "weights": {
      "feature_0": 1.0,
      "feature_1": 1.0,
      ...
      "feature_200": 1.0
    }
  }
}
				
			
```

##### Configuration and Queries

In all the tests, the other Solr caches have been disabled.

The benchmark has been done by executing 10 pairs of queries.   
The queries are range queries like:  
**`doc_id:[0 TO 9999]`** to first insert the feature vectors in the cache, **`doc_id:[0 TO 10000]`** to verify the cache effectiveness, here we should hit the feature vectors added with the previous query.

The queries are:

1. `doc_id:[0 TO 9999]` then **`doc_id:[0 TO 10000]`**
2. **`doc_id:[10000 TO 19999]`** then **`doc_id:[10000 TO 20000]`**
3. `doc_id:[20000 TO 29999]` then **`doc_id:[20000 TO 30000]`**
4. `doc_id:[30000 TO 39999]` then **`doc_id:[30000 TO 40000]`**
5. **`doc_id:[40000 TO 49999]`** then **`doc_id:[40000 TO 50000]`**
6. **`doc_id:[50000 TO 59999]`** then **`doc_id:[50000 TO 60000]`**
7. **`doc_id:[60000 TO 69999]`** then **`doc_id:[60000 TO 70000]`**
8. `doc_id:[70000 TO 79999]` then **`doc_id:[70000 TO 80000]`**
9. `doc_id:[80000 TO 89999]` then **`doc_id:[80000 TO 90000]`**
10. `doc_id:[90000 TO 99999]` then **`doc_id:[90000 TO 100000]`**

##### Results

The following tables evaluate:

**1. Average between query repetitions**.   
As explained before, we executed 10 different pairs of queries in the format:

* 1st query: **`doc_id:[0 TO 9999]`**
 * 2nd query: **`doc_id:[0 TO 10000]`**

With the average between query repetitions, we compute the average timing difference (ms) between the first and the second query to see how much improvement the cache brings.

Avg = ((2nd query – 1st query) + (2nd query – 1st query) + … )) / 10

Therefore:

Avg = ((**`doc_id:[0 TO 10000]`** – **`doc_id:[0 TO 9999]`**) + (**`doc_id:[10000 TO 20000]`** – **`doc_id:[10000 TO 19999]`**) + … )) / 10

The higher the better, since it means that the cache is doing a great job.

**2. Average time for 1st queries**.   
We computed the average time required to execute the first of the pairs of queries, the one that does not exploit caching, and that adds the feature vector to the cache as a new entry.

**2. Average time for 2nd queries**.   
We computed the average time required to execute the second of the pairs of queries, the one that hits the cache.

**3. Solr Cache Metrics.**  
In the last 5 columns of the table, we reported the cache metrics from Solr:

* **Hits**: the number of times we successfully found an entry in the cache.
 * **Miss**: the number of times we searched for an entry and didn’t find it in the cache.
 * **Lookups**: the overall number of times we search for an entry in the cache.
 * **Inserts**: the number of times we add a new entry to the cache.
 * **Evictions**: the number of times we remove an entry from the cache since we couldn’t find the entry requested, and we need to free space to add the new one.

###### Reranking without Cache

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Average time between query repetitions (ms) | Average time 1st queries (ms) | Average time 2nd queries (ms) | Hits | Miss | Lookups | Inserts | Evictions |
| *Apache Solr <10* | 1.8 | 136 | 134.2 | – | 200000 | 200000 | 200000 | 200000 |
| New Cache (>= Solr 10) | 0.3 | 129.3 | 129 | – | – | – | – | – |

From this table, we can see that the new implementation performs slightly better in all the queries. Therefore, we are not downgrading the basic performance of LTR during reranking.

###### Logging without Cache

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Average time between query repetitions (ms) | Average time 1st queries (ms) | Average time 2nd queries (ms) | Hits | Miss | Lookups | Inserts | Evictions |
| *Apache Solr <10* | -1.2 | 207 | 208.2 | – | – | – | – | – |
| New Cache (>= Solr 10) | 1.2 | 132.1 | 130.9 | – | – | – | – | – |

From this table, we can see that the new implementation performs better in all the queries.   
Therefore, we are not downgrading the basic performance of LTR during logging. The negative value in the average time between query repetitions means that the 2nd query is performing slightly slower (208.2) than the first (207), a further confirmation that no caching is used here.

###### Reranking with Cache

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Average between query repetitions | Average 1st queries | Average 2nd queries | Hits | Miss | Lookups | Inserts | Evictions |
| *Apache Solr <10* | -11.7 | 138 | 149.7 | 0 | 0 | 0 | 0 | 0 |
| New Cache (>= Solr 10) | 91.9 | 141.6 | 49.7 | 100000 | 100000 | 200000 | 100000 | 0 |

Here we can see the first great improvement we brought with the new cache.   
Before, no caching was available during reranking (indeed, all the cache metrics are 0); now the time for the 2nd query execution (the ones that hit the cache) is **reduced by almost a factor of 3!**

###### Logging with Cache

|  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  | Average between query repetitions | Average 1st queries | Average 2nd queries | Hits | Miss | Lookups | Inserts | Evictions |
| *Apache Solr <10* | -0.2 | 264.8 | 265 | 110112 | 89888 | 200000 | 200000 | 100000 |
| New Cache (>= Solr 10) | 92.6 | 141.8 | 49.2 | 300000 | 100000 | 400000 | 100000 | 0 |

Here again, we can see another great improvement we brought with the new cache.   
Current Solr cache, even if used as reported in the metrics, is not showing any good impact on the overall query time. Also, the evictions are high, meaning that the cache is not well managed and that there is not enough space to store the needed values.  
Our contribution, on the other hand, **reduces the query time execution by almost a factor of 3** and shows also a great **improvement in 1st queries execution**, where the cache does not show any hits.  
NOTE: Both caches were initialised with the same size of 100000 entries.

From these results, we can also notice that logging is exploiting the entries inserted during the first reranking phase, returning a hit and therefore not computing the feature vector again (300000 hits vs 100000 hits of the pure reranking).

## Conclusions

The benchmark confirms the exciting improvements brought by the newly introduced cache.  
**This implementation has been merged and is available in Solr version 10.0**.  
If you are going to try it, let us know your feelings about it and if any further improvement is needed.

Thanks for reading! See you next time!

## Need Help with this topic?​

If you're struggling with Learning to Rank in Apache Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with Learning to Rank in Apache Solr, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)