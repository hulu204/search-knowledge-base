---
title: 'Apache Solr Learning To Rank Interleaving'
company: Sease
tag: 排序
date: 2020-12-04
url: https://sease.io/2020/12/apache-solr-learning-to-rank-interleaving.html
account: 
origin: harvest3-202607
---
> Learning to rank is the application of machine learning, typically supervised, semi-supervised or reinforcement learning, in the construction of ranking models for information retrieval systems.
> The training data set consists of lists of pairs labelled with some partial order specified between items in each list.
> This order is typically induced by giving a numerical or ordinal score or a binary judgment (e.g. "relevant" or "not relevant") for each item.
> The ranking model proposes to rank, i.e. producing a permutation of items in new, unseen queries and search results in a similar way to rankings in the training data.
>
> Wikipedia
> [Tweet](https://twitter.com/intent/tweet?text=Learning+to+rank%C2%A0is+the+application+of+machine+learning%2C+typically+supervised%2C+semi-supervised+or+reinforcement+learning%2C+in+the+construction+of+ranking+models+for+information+retrieval+systems.%0AThe+training+data+set+consists+of+lists+of+%3Cquery%2C+document%3E+pairs+labelled+with+some+partial+order+specified+between+items+in+each+list.%0AThis+order+is+typically+induced+by+giving+a+numerical+or+ordinal+score+or+a+binary+judgment+%28e.g.+%22relevant%22+or+%22not+relevant%22%29+for+each+item.%0AThe+ranking+model+proposes+to+rank%2C+i.e.+producing+a+permutation+of+items+in+new%2C+unseen+queries+and+search+results+in+a+similar+way+to+rankings+in+the+training+data.+%E2%80%94+Wikipedia&url=https%3A%2F%2Fsease.io%2F2020%2F12%2Fapache-solr-learning-to-rank-interleaving.html)

## Learning To Rank in Apache Solr

Learning to Rank approached Apache Solr [[2]](https://lucene.apache.org/solr/guide/8_7/learning-to-rank.html) with Apache Solr 6.4.0 in early 2017.  
The contribution from Bloomberg [[3]](https://www.techatbloomberg.com/blog/bloomberg-integrated-learning-rank-apache-solr/) implements a new reranking query parser **ltr** that uses a machine learning model to rerank the top K search results of the original query:

```
				
					.../query?q=test&amp;rq={!ltr model=myModel reRankDocs=100}&amp;fl=id,score
				
			
```

The query in the example retrieves documents from Apache Solr for the query text “test” and reranks the top 100 (initially ranked by the original Solr score).  
The relevance function used for reranking is “myModel” and it corresponds to a custom model uploaded by the user and trained using ad hoc machine learning libraries.  
The final top 100 search results returned to the user are ordered according to “myModel”.  
To understand better how the Apache Solr Learning To Rank integration works, we have a series of blog posts that describe that in detail:

* + [Solr Is Learning To Rank Better – Part 1 – Data Collection](https://sease.io/2016/07/apache-solr-learning-to-rank-part-1-data-collection.html)
  + [Solr Is Learning To Rank Better – Part 2 – Model Training](https://sease.io/2016/08/apache-solr-learning-to-rank-part-2-model-training.html)
  + [Solr Is Learning To Rank Better – Part 3 – Ltr tools](https://sease.io/2016/08/apache-solr-learning-to-rank-part-3-ltr-tools.html)
  + [Solr Is Learning To Rank Better – Part 4 – Solr Integration](https://sease.io/2016/10/apache-solr-learning-to-rank-better-part-4.html)
  + [Explaining Learning to Rank Models with Tree Shap](https://sease.io/2020/07/explaining-learning-to-rank-models-with-tree-shap.html)

Also, the official Apache Solr reference guide provides many details and uses cases [[7]](https://lucene.apache.org/solr/guide/8_7/learning-to-rank.html)

## The importance of online evaluation in Learning To Rank

Online evaluation is used to estimate the best ranking model that fits a specific information retrieval system.   
It compares ranking functions through the interpretation of the users’ behaviour, represented directly by the collected interactions with the systems we are evaluating.   
This is called implicit feedback.   
Online testing has many advantages, we explore them in [The Importance of Online Testing in Learning to Rank – Part 1](https://sease.io/2020/04/the-importance-of-online-testing-in-learning-to-rank-part-1.html).

In this blog post we focus on the interleaving evaluation, specifically on the Team-Draft Interleaving (TDI) approach, a new feature in Solr 8.8 (released on the 29th of January 2021).

## Interleaving

Interleaving is an online evaluation approach for information retrieval systems that compares ranking functions by mixing their results and interpreting the users’ implicit feedback.  
Interleaving is an alternative to AB testing. It avoids the principal source of variance related to the separation of the users into two groups (the one exposed to the control system and the other exposed to the variant) and the consequent combination of the results.  
[Online Testing for Learning To Rank: Interleaving](https://sease.io/2020/05/online-testing-for-learning-to-rank-interleaving.html) explores the topic in full detail.

## Team Draft Interleaving

Team Draft Interleaving considers two ranking models: **modelA** and **modelB**.   
For a given query, each model creates its ranked list of documents La = (a1,a2,…) and Lb = (b1 , b2 , …).   
Then, the algorithm creates a unique ranked list I to return to the user.   
This list is created by interleaving elements from the two lists La and Lb as described by Chapelle in [[4]](https://www.cs.cornell.edu/people/tj/publications/chapelle_etal_12a.pdf).  
The list I is returned to the user, who interacts with the search results of interest. Each result was selected from one of the two ranking models, so we can compute which of the two models takes the higher number of clicks.

## Apache Solr implementation

Interleaving in Apache Solr Learning to Rank has been contributed to the Open Source community by Sease [[5]](https://github.com/apache/lucene-solr/commit/af0455ac8366d6dba941f2b2674ed2a8245c76f9) with the work of [Alessandro Benedetti](https://sease.io/about/alessandro-benedetti), Apache Lucene/Solr committer.  
Special thanks to Christine Poerschke from Bloomberg who helped a lot in the last phases of the contribution with a thorough review and many insightful observations.

###### Available from Apache Solr 8.8

It allows running a reranking query, passing two models to interleave.

Current features :

* + only **Team Draft Interleaving** is supported (contribution of additional algorithms are welcome)[[6]](https://issues.apache.org/jira/browse/SOLR-15015)
  + interleave two Learning To Rank models
  + interleave one Learning to Rank model with the original Solr ranking
  + get back the model the search result was picked from
  + **debug=results** returns the score explanation aligned with the model the search result was picked from
  + the feature logger transformer returns the appropriate feature values, used by the picked model

## Running a Rerank Query Interleaving Two Models

To rerank the results of a query, interleaving two models (myModelA, myModelB) and add the `rq` parameter to your search, passing two models in input, for example:

```
				
					.../query?q=test&amp;rq={!ltr model=myModelA model=myModelB reRankDocs=100}&amp;fl=id,score
				
			
```

To obtain the model that interleaving picked for a search result, computed during reranking, add `[interleaving]` to the `fl` parameter, for example:

```
				
					.../query?q=test&amp;rq={!ltr model=myModelA model=myModelB reRankDocs=100}&amp;fl=id,score,[interleaving]
				
			
```

The Solr response will include the model picked for each search result, resembling the output shown here:

```
				
					{
  "responseHeader":{
    "status":0,
    "QTime":0,
    "params":{
      "q":"test",
      "fl":"id,score,[interleaving]",
      "rq":"{!ltr model=myModelA model=myModelB reRankDocs=100}"}},
  "response":{"numFound":2,"start":0,"maxScore":1.0005897,"docs":[
      {
        "id":"GB18030TEST",
        "score":1.0005897,
        "[interleaving]":"myModelB"},
      {
        "id":"UTF8TEST",
        "score":0.79656565,
        "[interleaving]":"myModelA"}]
  }}
				
			
```

## Running a Rerank Query Interleaving a model with the original ranking

When approaching Search Quality Evaluation with interleaving it may be useful to compare a model with the original ranking. To rerank the results of a query, interleaving a model with the original ranking, add the `rq` parameter to your search, passing the special inbuilt \_`OriginalRanking`\_ model identifier as one input and your comparison model as the other model, for example:

```
				
					.../query?q=test&amp;rq={!ltr model=_OriginalRanking_ model=myModel reRankDocs=100}&amp;fl=id,score
				
			
```

To obtain the model that interleaving picked for a search result, computed during reranking, add `[interleaving]` to the `fl` parameter, for example:

```
				
					.../query?q=test&amp;rq={!ltr model=_OriginalRanking_ model=myModel reRankDocs=100}&amp;fl=id,score,[interleaving]
				
			
```

The Solr response will include the model picked for each search result, resembling the output shown here:

```
				
					{
  "responseHeader":{
    "status":0,
    "QTime":0,
    "params":{
      "q":"test",
      "fl":"id,score,[features]",
      "rq":"{!ltr model=_OriginalRanking_ model=myModel reRankDocs=100}"}},
  "response":{"numFound":2,"start":0,"maxScore":1.0005897,"docs":[
      {
        "id":"GB18030TEST",
        "score":1.0005897,
        "[interleaving]":"_OriginalRanking_"},
      {
        "id":"UTF8TEST",
        "score":0.79656565,
        "[interleaving]":"myModel"}]
  }}
				
			
```

## How to contribute

Do you want to contribute a new Interleaving Algorithm?  
You just need to :

* + implement the solr/contrib/ltr/src/java/org/apache/solr/ltr/interleaving/Interleaving.java interface in a new class [[7]](https://github.com/apache/lucene-solr/blob/master/solr/contrib/ltr/src/java/org/apache/solr/ltr/interleaving/Interleaving.java)
  + add the new algorithm in the package [[8]](https://github.com/apache/lucene-solr/tree/master/solr/contrib/ltr/src/java/org/apache/solr/ltr/interleaving/algorithms)
  + add the new algorithm reference in the org.apache.solr.ltr.interleaving.Interleaving#getImplementation

## Limitations

* + [Distributed Search] Sharding is not supported

## Need Help With This Topic?​​

If you’re struggling with Learning to Rank Interleaving in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Learning to Rank Interleaving in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)