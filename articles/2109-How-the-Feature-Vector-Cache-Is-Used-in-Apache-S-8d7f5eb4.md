---
title: 'How the Feature Vector Cache Is Used in Apache Solr'
company: Sease
tag: 召回
date: 2022-02-14
url: https://sease.io/2022/02/how-the-feature-vector-cache-is-used-in-solr.html
account: 
origin: harvest3-202607
---
Hi everyone!  
In this blog post, I would like to talk about the current usage of the Feature Vector Cache in Solr.

You can find in our blog a brief introduction to [Learning To Rank in Solr.](https://sease.io/2016/07/apache-solr-learning-to-rank-part-1-data-collection.html)

*(This blog post has been written looking at the code that is likely to be in Apache Solr 9.0 and at the commit id=cfc953b6b90 in the main branch of the Solr git [repository](https://github.com/apache/solr))*

At the moment the feature vector cache is **only used when you enable the feature transformer in the fl parameter** (both in insertions and lookup).  
It would be interesting to use the feature vector cache also at reranking time, independently of the feature transformer.

We are planning a [contribution](https://sease.io/open-source-contributions).

## Learning To Rank query performance

##### Feature Vector Cache

The Feature Vector Cache benefits are not too intuitive when reading the Apache Solr documentation.  
Let’s see how it works directly from the Solr code.

**Insertion and lookups are done in a specific class called: *org.apache.solr.ltr.FeatureLogger***

**Insertions** are done in the *org.apache.solr.ltr.FeatureLogger#log* method:

```
				
					public boolean log(int docid, LTRScoringQuery scoringQuery, SolrIndexSearcher 
searcher, LTRScoringQuery.FeatureInfo[] featuresInfo) {
  final String featureVector = makeFeatureVector(featuresInfo);
  if (featureVector == null) {
    return false;
  }
  return searcher.cacheInsert(fvCacheName, fvCacheKey(scoringQuery, docid), 
featureVector) != null;
}
				
			
```

**Lookups** are done in the *org.apache.solr.ltr.FeatureLogger#getFeatureVector* method:

```
				
					public String getFeatureVector(int docid, LTRScoringQuery scoringQuery, 
SolrIndexSearcher searcher) {
    return (String) searcher.cacheLookup(fvCacheName, fvCacheKey(scoringQuery, 
docid));
}
				
			
```

**N.B. Both Insertions and Lookups happen only if you are using the feature transformer (in the fl query parameter).**

###### Insertion

Let’s go in-depth through the insert process.

**To have an insertion:**

The **first condition** we meet is in the *org.apache.solr.ltr.LTRRescorer#scoreFeatures* method:

```
				
					org.apache.solr.ltr.LTRRescorer#scoreFeatures

....
if (scoreSingleHit(topN, docBase, hitUpto, hit, docID, scorer, reranked)) {
  logSingleHit(indexSearcher, modelWeight, hit.doc, scoringQuery);
}
...
				
			
```

**Currently the condition on the *org.apache.solr.ltr.LTRRescorer#scoreSingleHit* method is always verified.**  
We suspect it ended up this way due to code maintenance problems, we are investigating this more and we’ll update this post with more details later on.

Let’s see why.

Here is the called method:

```
				
					org.apache.solr.ltr.LTRRescorer#scoreSingleHit

...
if (hitUpto &lt; topN) {
      reranked[hitUpto] = hit;
      // if the heap is not full, maybe I want to log the features for this
      // document
      logHit = true;
    } else if (hitUpto == topN) {
      // collected topN document, I create the heap
      heapify(reranked, topN);
    }
...
				
			
```

This piece of code is called during the reranking phase of the topN documents (a parameter that corresponds to the ***rerankDocs*** value chosen at query time inside the ***rq*** parameter).  
Since we are reranking the topN documents, the if clause ***hitUpTo < topN*** is always verified for these topN docs (we are iterating on them) and therefore the ***logHit*** variable is always set to ***True*** for them.

Then a **second condition** arises.

In *org.apache.solr.ltr.LTRRescorer#logSingleHit* the existence of a *FeatureLogger* is needed as well as a *SolrIndexSearcher* is required.

Here is the condition:

```
				
					org.apache.solr.ltr.LTRRescorer#logSingleHit

...
if (featureLogger != null &amp;&amp; indexSearcher instanceof SolrIndexSearcher) {
  featureLogger.log(docid, scoringQuery, (SolrIndexSearcher)indexSearcher, 
modelWeight.getFeaturesInfo());
}
...
				
			
```

**The condition to have a *SolrIndexSearcher* is always accomplished so let’s focus on the *FeatureLogger* one.**

A *FeatureLogger* is set if **both 1 AND 2 are satisfied**:

1. 1. the feature transformer in the ***fl*** query parameter is used.  
      In this case, indeed we will have the ***extractFeatures*** variable in the *org.apache.solr.ltr.search.LTRQParserPlugin.LTRQParser#parse* method set to ***true*** from line 164.
   2. the feature store defined in the ***feature transformer*** is the same as the feature store defined in the model **OR**  
      just the feature transformer ***[features]*** component has been set, without specifying the store we want to be used.

**Therefore to have an insertion, these are the two conditions to accomplish:**

1. 1. the **feature transformer** in the ***fl*** query parameter **is used.**
   2. the **feature store** defined **in the *fl*** parameter **is the same as the feature store** defined **in the model  
      *OR***just the **feature transformer** *[features]* component **has been set**, **without specifying the store** to be used**.**

###### Only for the curious ones

###### 

If you want to go in-depth into these conditions you can take a look at the o*rg.apache.solr.ltr.search.LTRQParserPlugin.LTRQParser#parse* method.  
Here the *extractFeatures* variable is set in line 164:

```
				
					final boolean extractFeatures = SolrQueryRequestContextUtils.isExtractingFeatures(req);
				
			
```

Then the computed *extractFeatures* is used in line 183, where the condition on the feature store is implemented:

```
				
					final boolean featuresRequestedFromSameStore = 
(modelFeatureStoreName.equals(tranformerFeatureStoreName) || 
tranformerFeatureStoreName == null) ? extractFeatures : false;
				
			
```

And then the computed *featuresRequestedFromSameStore* is used to set the *FeatureLogger* at line 198.

###### Lookups

As mentioned before, lookups are part of the transformer process.  
To enable the transformer just pass the <transformer name> (defined in the solrconfig.xml) in the fl parameter.  
**e.g. fl=[features]**

**solrconfig.xml**

```
				
					&lt;transformer name="features" class="org.apache.solr.ltr.response.transform.LTRFeatureLoggerTransformerFactory"&gt; &lt;str name="fvCacheName"&gt;QUERY_DOC_FV&lt;/str&gt; &lt;/transformer&gt;
				
			
```

Then **one of these two conditions** need to be ***True***:

1. 1. The query doesn’t have to be an OriginalRankingLTRScoringQuery.
   2. A store is needed to be explicitly defined in the ***fl*** parameter.

Here are the two conditions that need to be verified:

```
				
					org.apache.solr.ltr.response.transform.LTRFeatureLoggerTransformerFactory.FeatureTra
nsformer#implTransform

...
if (!(rerankingQuery instanceof OriginalRankingLTRScoringQuery) || 
hasExplicitFeatureStore) {
        Object featureVector = featureLogger.getFeatureVector(docid, rerankingQuery, 
searcher);
        ...
      }
...
				
			
```

**The first condition on the *OriginalRankingLTRScoringQuery* is always true when interleaving is not running** and therefore we will always access the cache for lookups.  
Interleaving gives you the possibility of comparing a learned model with the original Solr score.  
The original Solr score doesn’t require features to be extracted, so unless hasExplicitFeatureStore is defined, the lookup wouldn’t be necessary.

Here we can see that the cache is only used for the ***FeatureLoggerTrasformer*** and not during the reranking phase done through the ***rq*** parameter.  
We are not making the reranking faster.

**Therefore to have a lookup, these are the two conditions to accomplish:**

1. 1. the **feature transformer** in the *fl* query parameter **is used.**
   2. **the LTR model is a learned model (and not the original Solr score pre-reranking)  
      *OR***a **feature store** has been **exp**

## Examples

Let’s make some example queries to see how the Solr cache behaves.

###### First query

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/11/image-1.png?w=800&ssl=1)

This is our first query. It has the *[features]* component defined in the ***fl*** query parameter and also the ***rq*** query parameter has been used.

For insertions we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | **YES** |
| The **transformer** *store* defined is the same as the model store (TRUE)  OR the *transformer* [features] has been set, without specifying the store to be used (FALSE) | **YES** |

**All conditions for insertions are accomplished and therefore insertions happen.**

For lookups we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | **YES** |
| The model is a learned model (‘first\_model’) (TRUE) OR An explicit store has been defined in the *transformer* (‘first\_model\_store’) (TRUE) | **YES** |

**All the conditions for lookups are accomplished and therefore lookups happen.**

###### Second query

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/11/image-2.png?w=800&ssl=1)

This is our second query. It has the *[features]* component defined in the ***fl*** query parameter and also the ***rq*** query parameter has been used.

For insertions we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | **YES** |
| The **transformer** *store* defined is the same as the model store (FALSE) OR the *transformer* [features] has been set, without specifying the store to be used (FALSE) | **NO** (the model store is the ‘first\_model\_store’) |

**Not all conditions for insertions are accomplished and therefore insertions will not be made.**

For lookups we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | **YES** |
| The model is a learned model (‘first\_model’) (TRUE) OR An explicit store has been defined in the *transformer* (‘second\_model\_store’) (TRUE) | **YES** (N.B. the model and transformer stores are different) |

**All the conditions for lookups are accomplished and therefore lookups happen.**

###### Third query

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/11/image-4.png?w=800&ssl=1)

This is our third query. It has the *[features]* component defined in the ***fl*** query parameter but no ***rq*** query parameter has been used.

For insertions we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | **YES** |
| The **transformer** *store* defined is the same as the model store (FALSE)  OR the *transformer* [features] has been set, without specifying the store to be used (FALSE) | **NO** (there is no rq parameter) |

**Not all conditions for insertions are accomplished and therefore insertions will not be made.**

For lookups we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | YES |
| The model is a learned model (FALSE) OR An explicit store has been defined in the *transformer* (‘second\_model\_store’) (TRUE) | YES |

**The first and second conditions for lookups are accomplished and therefore lookups happen.**

###### Fourth query

![](https://i0.wp.com/sease.io/wp-content/uploads/2021/12/Screenshot-from-2021-12-03-15-05-07.png?w=800&ssl=1)

This is our fourth query. It has no *[features]* component defined in the ***fl*** query parameter but the ***rq*** query parameter has been used.

For insertions we can see that:

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is defined in fl (‘[features=…]’) | **NO** |
| The **transformer** *store* defined is the same as the model store (FALSE)  OR the *transformer* [features] has been set, without specifying the store to be used (FALSE) | **NO** |

**Not all conditions for insertions are accomplished and therefore insertions will not be made.**

For lookups we can see

| Condition | Is condition verified |
| --- | --- |
| The *transformer* is not defined in fl (‘[features=…]’) | **NO** |
| The model is a learned model (TRUE) OR An explicit store has been defined in the *transformer* (FALSE) | **YES** |

****Not all conditions for lookups are accomplished and therefore lookups will not be made.****

## Future works

We will open soon a Jira issue to integrate the Feature Vector Cache in the reranking phase, independently of the feature transformer.

## Need Help With This Topic?​​

If you’re struggling with Feature Vector Cache in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with How the feature vector cache is used in Apache Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)