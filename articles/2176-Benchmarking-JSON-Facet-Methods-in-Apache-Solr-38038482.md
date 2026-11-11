---
title: 'Benchmarking JSON Facet Methods in Apache Solr'
company: Sease
tag: 工程相关
date: 2026-05-15
url: https://sease.io/2026/05/solr-benchmark-faceting-methods.html
account: 
origin: harvest3-202607
---
Hi there!

In this blog post, we present the results of a benchmark analysing the performance differences between three fundamental approaches for generating term facets in Apache Solr using the JSON Facet API: the use of **DocValues**, via the `dv` or `dvhash` method, versus the use of the **Inverted Index**, via the **`stream`/`enum`** methods.

The reason behind this blog post is that the official Solr documentation regarding the JSON Facet API does not clearly define how to approach the choice between the different faceting methods. In fact, in the [documentation](https://solr.apache.org/guide/solr/latest/query-guide/json-facet-api.html#:~:text=every%20returned%20bucket-,method,-This%20parameter%20indicates) for the **`method`** parameter, we find only the following information:

> *This parameter indicates the facet algorithm to use:*

> * *`dv` DocValues, collect into ordinal array*
> * ***`uif`** UnInvertedField, collect into ordinal array*
> * *`dvhash` DocValues, collect into hash – improves efficiency over high cardinality fields*
> * *`enum` TermsEnum then intersect DocSet (stream-able)*
> * *`stream` Presently equivalent to **`enum`**. Used for indexed, non-point fields with sort **`index asc`** and **`allBuckets`**, **`numBuckets`**, and **`missing`** disabled.*
> * *`smart` Pick the best method for the field type (this is the default)*

Since we found this part of the documentation difficult to interpret, we would like to provide some clarity. The goal is to answer the following question:   
*Which method is more efficient when working with “low cardinality” fields? And what does it mean by “low” or “high” cardinality? What if I restrict my docset to a smaller subset of documents?*

## Facet Method Overview

There are two Solr Java classes that leverage the *DocValues* data structure for faceting when using the JSON facet APIs: **`FacetFieldProcessorByArrayDV`** and **`FacetFieldProcessorByHashDV`**. The first one implements the **`dv`** facet method, while the second one implements the **`dvhash`** facet method. They both require the **`docValues`** parameter to be set to **`true`**.

This can be easily verified by including the `debug` parameter in the query and subsequently inspecting the response. In that case, we would explicitly see which Java class, and therefore method, was utilized.

To use the **`stream`/`enum`** method, instead, which relies solely on the inverted index, the configuration must be specific (as stated in the [documentation](https://solr.apache.org/guide/solr/latest/query-guide/json-facet-api.html#:~:text=every%20returned%20bucket-,method,-This%20parameter%20indicates)):

*Used for indexed, non-point fields with sort `index asc` and **`allBuckets`**, **`numBuckets`**, and **`missing`** disabled.*

**If one of those requirements is not met, the method will simply be ignored, and a default one will be used depending on the configuration** (for further information, see this [link](https://github.com/apache/solr/blob/dc31be6b07643c6f5f61f7999b85533887509415/solr/core/src/java/org/apache/solr/search/facet/FacetField.java#L82) to the Solr codebase). With the correct configuration, the debug section of the response will show **`FacetFieldProcessorByEnumTermsStream`**.

## Benchmark Setup

##### Machine Configuration

To ensure these benchmark results are reproducible, here are the specific details of the environment used for these tests:

* **Solr Version:** 9.10.1 (Standalone mode)
* **Schema Version:** 1.7
* **System configuration:**

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-8.png?fit=736%2C441&ssl=1)

##### Schema

We use a single data source mapped to a different field via `copyField`. This allows us to query the same logical content using different faceting methods.

The schema configuration is as follows:

* **`<CARDINALITY>field_str`**: The primary field. A standard `solr.StrField`, indexed but with `docValues` set to **`false`**. To calculate facets, Solr must use the terms from the inverted index. In theory, this should be more performant if the number of unique values within the examined field is low. As for what “low” means in this context, we will run tests in the following sections. This field will be used by the method `stream`.
* **`<CARDINALITY>field_dv`**: Non-indexed and with `docValues` set to **`true`**. This stores data in a column-oriented format on disk and is the structure recommended for faceting in the official Solr documentation under the DocValues section of the [documentation](https://solr.apache.org/guide/solr/latest/indexing-guide/docvalues.html). To be more precise, while the inverted index is **term-oriented** (mapping terms to document positions), DocValues are **document-oriented** (mapping documents to their terms). This “doc-to-terms” structure is used by both methods `dv` and `dvhash`.

In the 2 fields described above, the **`<CARDINALITY>`** placeholder will be substituted by the number of different values possible for the fields.

We should therefore add the following fields to our schema

```
				
					&lt;dynamicField name="*field_str" type="string" indexed="true" stored="true" multiValued="false" docValues="false"/&gt;
&lt;dynamicField name="*field_dv" type="string" indexed="false" stored="true" multiValued="false" docValues="true"/&gt; 
&lt;copyField source="*field_str" dest="*field_dv"/&gt;
				
			
```

##### Solrconfig

Regarding the Solr configuration (managed through the **`solrconfig`** file), all caching has been removed, and the configuration has been kept as minimal as possible. This experiment has nevertheless been repeated with the default Solr configuration for caching, and the results were the same.

##### Collection description

The collection contains 10 million documents with a very minimal structure:

* the **`id`** field: which is ours **`uniqueKey`**.
* the **`id_int`** field: which is a copy of the id field of type **`solr.LongPointField`** (added to enable the use of [range searches](https://solr.apache.org/guide/solr/latest/query-guide/standard-query-parser.html#range-searches) to filter documents by their id).
* the **`_version_`** field.
* the two dynamic fields mentioned above.

We decided to analyse a wide spectrum of different cardinalities: from **`10`** to **`10^7`** (10 million) possible values for a field.

An example of the content of the fields mentioned above is the following:

{   
“**id**“: “1580002”,   
“**id\_int**“: 1580002,  
“**10field\_str**“: “bucket\_9”,  
“**10field\_dv**“: “bucket\_9”,  
“**100field\_str**“: “bucket\_37”,  
“**100field\_dv**“: “bucket\_37”,  
“**1000field\_str**“: “bucket\_419”,  
“**1000field\_dv**“: “bucket\_419”,  
“**10000field\_str**“: “bucket\_1498”,  
“**10000field\_dv**“: “bucket\_1498”,  
“**100000field\_str**“: “bucket\_34260”,  
“**100000field\_dv**“: “bucket\_34260”,  
“**1000000field\_str**“: “bucket\_260453”,  
“**1000000field\_dv**“: “bucket\_260453”,  
“**10000000field\_str**“: “bucket\_1580002”,  
“**10000000field\_dv**“: “bucket\_1580002”,  
“**\_version\_**“:1857548728253022208  
}

We decided to keep it simple and define each string as “bucket\_<BUCKET\_NUM>” where **`BUCKET_NUM`** is an integer sampled uniformly in the interval **`[1, NUM]`**(both upper and lower bounds included).

##### Queries

We will present the results for facets computed over different sets of documents, starting from retrieving all 10M documents, using a catch-all query, and decreasing up to 10 documents, to better exploit the use of the methods on different subsets of documents.

The configuration used to call the facets via the JSON Facet API (with the catch-all query) is as follows, one for each possible cardinality **`<CARDINALITY>`**:

```
				
					{ 
    "query": "*:*", 
    "params": { 
        "rows": 0, 
        "debug": "timing" 
    }, 
    "facet": { 
        "dv": { 
            "type": "terms", 
            "method": "dv", 
            "limit": min(&lt;CARDINALITY&gt;, &lt;NUM_DOC_TO_RETRIEVE&gt;), 
            "field": "&lt;CARDINALITY&gt;field_dv" 
        }, 
        "dvhash": { 
            "type": "terms", 
            "method": "dvhash", 
            "limit": min(&lt;CARDINALITY&gt;, &lt;NUM_DOC_TO_RETRIEVE&gt;), 
            "field": "&lt;CARDINALITY&gt;field_dv" 
        }, 
        "stream": { 
            "type": "terms", 
            "method": "stream", 
            "sort": "index asc", 
            "limit": min(&lt;CARDINALITY&gt;, &lt;NUM_DOC_TO_RETRIEVE&gt;), 
            "field": "&lt;CARDINALITY&gt;field_str", 
            "allBuckets": false, 
            "numBuckets": false, 
            "missing": false 
        } 
    } 
}
				
			
```

For the case of the subsets of documents, we used **`"id_int:[* TO <NUM_DOC_TO_RETRIEVE>]"`** (with the number of documents we want to retrieve) instead of **`"*:*"`** in the **`query`** parameter.

Also note that for the **`stream`** method, we are returning **all facets** through **`limit: min(<CARDINALITY>, <NUM_DOC_TO_RETRIEVE>)`**, since, in most cases, facets are used to get the most frequent terms. This is due to the fact that facets are not ordered by count, but only by index for this method. To keep the timings fair, we decided to add the same parameters to all facet methods.

I reported above only the configuration that calls the 3 methods together. Actually, to record timings fairly, we implemented each facet involving only one method each time, resulting in one request per method and cardinality.

Another important aspect of this benchmark is to reduce the variance of the study, avoiding strange results related to a one-time run only. To do that, we decided to run 10 facet calls per method and cardinality, and use the mean of the recorded time as the examined value. More than this, we decided to discard the first and the last run to avoid improper timings for the use of Lucene’s **`fieldCache`**.

## Facet Method Configuration Analysis

Let’s now verify that everything is configured correctly:

* for methods `dv` and `dvhash`, we are computing facets over the field **`<CARDINALITY>field_dv`** (which has docValues enabled) and the methods are correctly set.
* for method `stream`, we need to check:
  + **indexed**: satisfied, as the field **`<CARDINALITY>field_str`** has **`indexed="true"`** in the **`schema.xml`** file.
  + **non-point field**: satisfied, since **`<CARDINALITY>field_str`** was defined as a **`solr.StrField`** type.
  + **sort**: explicitly defined as **`"index asc"`** in the query.
  + **allBuckets, numBuckets,** and **missing**: all three have been explicitly set to **`false`** in the query.

After this explanation of the configuration, we can proceed with the analysis of the results.

## Result Analysis

##### Facets Over All Documents

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-13.png?fit=800%2C480&ssl=1)

We immediately notice a fundamental trend: for the first four data points, up to 10K unique values per field, the method with the lowest time spent calculating facets is **stream**, which utilizes the Lucene index to calculate buckets. Therefore, `stream` is the **recommended** method when **cardinality is less than 10,000**.

Beyond that point, however, the 3 lines become very similar to each other for 100K and 1M cardinality, representing the fact that whichever method you want to use, they are almost equivalent. We cannot say the same for **cardinality 10M**, where the method **`stream` takes the lead again**. It might not seem that relevant in the plot due to the logarithmic scale, but between `stream` and `dv` there are is a couple of seconds difference.

This behavior is highly unexpected. One might wonder why: in this setting, the `stream` method should be extremely efficient, as it simply involves scanning the index and collecting the lengths of the posting lists. To try to understand this behavior, we decided to merge all index segments, created by Lucene under the hood, into a single large segment. This ended up with a segment of size 1,160 MB. We then repeated the full benchmark under these conditions, despite the fact that such a configuration is unlikely to reflect any realistic collection setup. For 10M documents, the result is the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-17.png?fit=800%2C480&ssl=1)

This time, as expected, **`stream` always wins**. This suggests that the performance degradation in `stream` method may be due to segment handling during facet computation, rather than to the computation method itself.

##### Facet Over a Subset of Documents

What happens when restricting the set of documents? The behaviour now is completely different.

###### 1M Documents Retrieved

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-16.png?fit=800%2C480&ssl=1)

Starting from a lower order of magnitude, specifically retrieving 1M documents, we can see that the **stream** method is no longer competitive with the other two. Furthermore, when the cardinality remains below 100K, **dvhash** outperforms even **dv**.

However, we observe that for high cardinalities (above 1M cardinality), the **dv** method takes the lead. Therefore, it makes sense to **initially prefer `dvhash` up to 100K possible values**, and then switch to the **`dv` method as the cardinality increases further**.

Even in this case, we have a difference when we merge all the index segments into one. The results for this case are the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-18.png?fit=800%2C480&ssl=1)

Similarly to the case where we fetched 10M documents, the higher cardinalities improved considerably, allowing the `stream` method to take the lead above 100K cardinality.

###### 100K Documents Retrieved

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-15.png?fit=800%2C480&ssl=1)

In the case where 100K documents are returned, the **difference between the two methods `dv` and `dvhash` at these scales remains small**. Overall, the two methods exhibit highly comparable behaviour, with no substantial divergence in effectiveness as the number of retrieved documents increases.

###### Less than 100K Documents Retrieved

![](https://i0.wp.com/sease.io/wp-content/uploads/2027/02/image-14.png?fit=800%2C600&ssl=1)

As we can see in the plot above, when we restrict the document set a lot before computing facets, both `dvhash` and `dv` methods seem to perform **similarly when the cardinality is 100k or less**. After, we see a slight degradation of the `dv` method, so it’s advisable to use `dvhash` in the scenario where we have a cardinality **higher than or equal to 100K**.

## Conclusions

Based on our benchmark, it is clear that there is no “one-size-fits-all” method for calculating facets. The optimal choice depends heavily on two variables: **field cardinality** (the number of unique values) and the **size of the document subset** being queried.

To summarize our findings:

* **When querying all documents**, the **`stream`** method performs best if the cardinality stays **less than 10,000** and at **10M**. Besides those cases, the performance gap between methods is reduced significantly.
* **Dealing with large result sets (~1M documents)**, efficiency shifts toward **`dvhash`** for **cardinalities up to 1M**. However, once you **cross the 1M cardinality threshold**, the **`dv`** method becomes a more stable and performant choice.
* **Dealing with medium result sets (~100K documents)**, both **`dvhash`** and **`dv`** methods perform almost identically.
* **Dealing with small result sets (<100K documents)** **`dvhash`** consistently proves to be the most efficient method, especially as cardinality increases.

We also found that index segmentation can have a substantial impact on facet performance.

Keep in mind that this is a **general benchmark**, trying to cover a naive use case. We suggest **benchmarking your collection(s) to find a solution in your specific scenario** (something we would be **[more than happy to help you with](https://sease.io/contacts)**! 😉)

Hopefully, this post proved to be helpful and gave you some useful insights to choose the proper facet method for your use case. Keep an eye on our website for updates, news, and future blog posts.

## Need Help with this topic?​

If you're struggling with facet methods, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with facet methods, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)