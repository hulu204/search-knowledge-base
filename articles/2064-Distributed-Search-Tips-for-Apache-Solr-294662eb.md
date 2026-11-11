---
title: 'Distributed Search Tips for Apache Solr'
company: Sease
tag: 工程相关
date: 2017-11-27
url: https://sease.io/2017/11/distributed-search-tips-for-apache-solr.html
account: 
origin: harvest3-202607
---
Distributed search is the foundation for Apache Solr Scalability:

It’s possible to distribute search across different Apache Solr nodes of the same collection ( both in a legacy [[1]](https://lucene.apache.org/solr/guide/6_6/distributed-search-with-index-sharding.html) or SolrCloud [[2]](https://lucene.apache.org/solr/guide/6_6/solrcloud.html) architecture), but it is also possible to distribute search across different collections in a SolrCloud cluster.  
Aggregating results from different collections may be useful when you put in place different systems ( that were meant to be separate ) and you later realize that aggregating the results may be an additional useful use case.  
This blog will focus on some tricky situations that can happen when running a distributed search (for configuration or details you can refer to the Solr wiki).

## IDF

Inverse Document Frequency affects the score.  
This means that **a document coming from a big collection can obtain a boost from IDF, in comparison to a similar document from a smaller collection**.  
This is because the maxDoc count is taken into account as corpus size, so even if a term has the same document frequency, IDF will be strongly affected by the collection size.  
Distributed IDF [[3]](https://lucene.apache.org/solr/guide/6_6/distributed-requests.html#DistributedRequests-ConfiguringstatsCache_DistributedIDF_) partially solved the problem :

When distributing the search across different shards of the same collection, it works quite well.  
However, **using the ExactSharedStatCache and alternating single-collection distribution and multi-collection distribution in the same SolrCloud cluster will create some caching conflict.**

Specifically, if we first execute the inter-collection query, the global stats cached will be the inter-collection global stats,  so if we then execute a single collection distributed search, the preview global stats will remain cached (vice-versa applies).

## Debug Scoring

The real score and debug score are not aligned with the distributed IDF, this means that the debug query will not show the correct distributed IDF and correct scoring calculus for distributed searches [[4]](https://issues.apache.org/jira/browse/SOLR-7759).

## Relevancy tuning

Lucene/Solr’s score is not probabilistic or normalised.  
For the same collection, we can have completely different score scales just with different queries.  
The situation becomes more complicated when we **tune our relevancy adding multiplicative or additive boosts**.  
Different collections may imply completely different boosting logic that could cause the score of a collection to be on a completely different scale in comparison to another.  
We need to be extra careful when tuning relevancy for searches across different collections and try to configure the distributed request handler in the most compatible way as possible.

## Request handler

It is important to carefully specify the request handler to be used when using distributed search.  
The request will hit one collection in one node and then when distributing the same request handler will be called on the other collections across the other nodes.  
If necessary it is possible to configure the aggregator request handler and local request handlers (this may be useful if we want to use different scoring formulas per collection, using local parameters):

##### Aggregator Request Handler

It is executed on the first node receiving the request.  
It will distribute the request and then aggregate the results.  
It must describe parameters that are in common across all the collections involved in the search.  
It is the one specified in the main request.  
e.g.

```
				
					http://localhost:8983/solr/collection1/select?
				
			
```

##### Local Request Handler

It is specified by passing the parameter: **shards.qt=**It is executed on each node that receives the distributed query AFTER the first one.  
This can be used to use specific fields or parameters on a per-collection basis.  
A local request handler may use fields and search components that are local to the collection interest.

e.g.

```
				
					http://localhost:8983/solr/collection1/select?q=*:*&amp;collection=collection1,collection2&amp;shards.qt=localSelect
				
			
```

**N.B.** The use of a local request handler may be useful in case you want to define local query parser rules, such as local edismax configuration to affect the score.

## Unique Key

The unique key field must be the same across the different collections**.**Furthermore, the value should be unique across the different collections to guarantee proper behaviour.  
If we don’t comply with this rule, Solr will fail in aggregating the results and raise an exception.

## Need Help With This Topic?​​

If you’re struggling with Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)