---
title: 'Apache Solr Distributed Facets'
company: Sease
tag: 工程相关
date: 2018-10-23
url: https://sease.io/2018/10/apache-solr-distributed-facets.html
account: 
origin: harvest3-202607
---
Apache Solr distributed faceting feature was introduced back in 2008 with the first versions of Solr (1.3 according to this jira[[1](https://issues.apache.org/jira/browse/SOLR-303)]).  
Until now, I always assumed it just worked, without diving too much into the details.  
Nowadays distributed search and faceting are extremely popular, you can find them pretty much everywhere (in the legacy or SolrCloud form alike).  
**N.B.** Although the mechanics are pretty much the same, Json faceting revisits this approach with some changes, so we will now focus on **legacy field faceting**.

I think it’s time to get a better understanding of how it works.

## Multiple Shard Requests

When dealing with distributed search and distributed aggregation calculations, you are going to see multiple requests going back and forth across the shards.

They have a different focus and are meant to retrieve the different bits of information necessary to build the final response.  
We are going to explore the different rounds of requests, focusing just on the faceting purpose.  
**N.B.** Some of these requests are also carrying results for the distributed search calculation, which is used to minimise the network traffic.

For the sake of this blog let’s simulate a simple sharded index, white space tokenization on field1 and facet.field=**field1**

| Shard 1 | Shard 2 |
| --- | --- |
| *Doc0* *{  “id”:”1”,* *“field1”:”a b”* *}* | *Doc3* *{  “id”:”4”,* *“field1”:”b c”* *}* |
| *Doc1* *{  “id”:”2”,* *“field1”:”a”* *}* | *Doc4* *{  “id”:”5”,* *“field1”:”b c”* *}* |
| *Doc2* *{  “id”:”3”,* *“field1”:”b c”* *}* | *Doc53* *{  “id”:”6”,* *“field1”:”c”* *}* |

**Global Facets** : b(4), c(4), a(2)

**Shard 1 Local Facets** : a(2), b(2), c(1)

**Shard 2 Local Facets** : c(3), b(2)

## Collection of Candidate Facet Field Values

The first round of requests is sent to each shard to identify the candidate top K global facet values.  
To achieve this target each shard will be requested to respond with its local top K+J facet values and counts.  
The reason we ask for more facets from each shard is to have better term coverage, to avoid losing relevant facet values and to minimise the refinement requests.  
How many more we request from each shard is regulated by the “overrequest” facet parameter, a factor that gives more accurate facets at the cost of additional computations [[2](https://lucene.apache.org/solr/guide/6_6/faceting.html#Faceting-Over-RequestParameters)].  
Let’s assume we configure a

```
				
					facet.limit=2&amp;facet.overrequest.count=0&amp;facet.overrequest.ratio=1
				
			
```

to explain when refinement happens and how it works.

**Shard 1 Returned Facets** : a(2), b(2)

**Shard 2 Returned Facets** : c(3), b(2)

## Global Merge Of Collected Counts

The facet value counts collected from each shard are merged and the most occurring global top K is calculated.  
These facet field values are the first candidates to be the final ones.  
In addition to that, other candidates are extracted from the terms below the top K, based on the shards that didn’t return those values statistics.  
At this point, we have a candidate set of values and we are ready to refine their counts where necessary, asking back this information to the shards that didn’t include that in the first round.  
This happens including the following specific facet parameter to the following refinement requests:

```
				
					{!terms=$&lt;field&gt;__terms}&lt;field&gt;&amp;&lt;field&gt;__terms=&lt;values&gt;
				
			
```

e.g.

```
				
					
{!terms=$field1__terms}field1&amp;field1__terms=term1,term2
				
			
```

**N.B.** This request is specifically asking a Solr instance to return the facet counts just for the terms specified [[3](https://lucene.apache.org/solr/guide/7_5/faceting.html#limiting-facet-with-certain-terms)]

**Top 2 candidates** = b(4), c(3)  
**Additional candidates** = a(2)

The reason that **a(2)** is added to the potential candidates is because Shard 2 didn’t answer with a count for **a,**the potential missing count of 1 could bring **a** to the top K. So it is worth a verification.

Shard 1 didn’t return any value for the candidate **c** facet.  
So the following request is built and sent to it:

```
				
					facet.field={!terms=$field1__terms}field1&amp;field1__terms=c

				
			
```

Shard 2 didn’t return any value for the candidate **a** facet.  
So the following request is built and sent to it:

```
				
					facet.field={!terms=$field1__terms}field1&amp;field1__terms=a

				
			
```

## Final Counts Refinement

The refinement counts returned by each shard can be used to finalise the global candidate facet value counts and to identify the final top K to be returned by the distributed request.  
We are finally done!

**Shard 1 Refinements Facets**: c(1)

**Shard 2 Refinements Facets**: a(0)

**Top K candidates updated** :  **b(4), c(4)**, a(2)

Given a facet.limit=2 the final global facets with correct results returned is :  
**b(4), c(4)**

## Need Help With This Topic?​​

If you’re struggling with legacy field faceting, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with legacy field faceting, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)