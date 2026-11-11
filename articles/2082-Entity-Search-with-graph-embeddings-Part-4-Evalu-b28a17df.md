---
title: 'Entity Search with graph embeddings - Part 4 – Evaluation and conclusion'
company: Sease
tag: 评测
date: 2019-12-17
url: https://sease.io/2019/12/entity-search-with-graph-embeddings-part-4-evaluation-and-conclusion.html
account: 
origin: harvest3-202607
---
This is the last post of the Entity Search with graph embeddings serie.

In [Part 2](https://sease.io/?p=2210) and [Part 3](https://sease.io/?p=2214) we illustrated the core of the dissertation describing in detail the implementation of our solution pipeline.

In this final part we will see some evaluation measures and results. We will draw some conclusions explaining which were the encountered problems and which are the critical phases. Finally we will provide some inspiration for future developments and improvements.

## Evaluation

After the realization of our combination and fusion systems, we evaluate the results achieved. In particular, we do two types of evaluation: **quantitative** (average) and **qualitative** (i.e. topic-based). In the quantitative evaluation, we make some general considerations about the effectiveness of the proposed systems, considering measures such as MAP, nDCG, P@5 and P@10. In the qualitative evaluation, we look at how the effectiveness of each system is correlated to the topic (query) through a study on the form in which it is formulated (with which terms) and on the type and number of entities requested. In particular, this evaluation can give us information about the coherence and the completeness of our virtual documents making a comparison between the ideal answer, the user would like to receive, and the real one. This analysis highlights also those problems related to the computation of the final score of each entity and their sorting.

##### Quantitative

###### Combination systems

In the figure below we represent through a box-and-whisker plot the values of MAP, average nDCG, average P@5 and average P@10 for the combination systems. In green (with label BM25) we also represent the result of the state-of-the-art method.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/avg_comb.png?fit=800%2C549&ssl=1)

Fig.1 Combination systems

From Figure 1 we can observe that BM25 obtains better results in all these measures even though the performances are comparable on average. For what concern our systems we can notice that SUMCO (in grey) proved to be the better one obtaining better results in all the measures, WECO (in yellow) follows and SICO (in blue) is the worst one. From these results, we can deduce that the final score used for WECO is not optimal for our retrieval purpose while the one for SUMCO works better. In general, we can also say that ordering the reranked entities by score before writing them into the final run, as done by SUMCO and WECO, allows us to obtain a better-ranked list with respect to the SICO method where this is not done. This can be justified by the fact that in SICO we create the final run by progressively inserting maxEntity entities for each cluster, maintaining their original ordering. However, it may be that the next cluster contains some entities that are more relevant than thus of the previous one; in this case, these entities would be shifted lower than their ideal position leading to worse performance.

###### Fusion systems

In the figures below we represent through a box-and-whisker plot the values of MAP, average nDCG, average P@5 and average P@10 for the fusion systems. In green (with label BM25) we also represent the result of the state-of-the-art method.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/avg_fus.png?fit=800%2C487&ssl=1)

Fig.2 Fusion systems

To improve the effectiveness of combination systems we implement the fusion systems. Comparing Figure 1 with Figure 2 we can see that fusion systems obtain better results with respect to combination systems because we exploit BM25 run, which we know has better performance, as the basis for our approaches. Looking at Figure 2 in detail we can observe that LEFU (in grey) turns out to be the best method for MAP and average nDCG measures, while it obtains the same performance of BM25 in average P@5 and average P@10. This behaviour can be due to the choice of which entities to insert into the final run of LEFU.

##### Qualitative

To execute a more specific study on the results of our systems, we perform a topic-based evaluation. In this evaluation, we can observe some interesting aspects of the retrieval concerning the topic on which it is performed.

###### Combination systems

In the figure below we represent the AP value obtained by SUMCO and BM25 for each topic (blue point). This plot can give us an immediate understanding of which of the two systems obtains better performances for each topic. If the point is above the red bisector SUMCO is the best method otherwise BM25 it is.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/ap_sumco-1.png?fit=592%2C439&ssl=1)

Fig.3 obtained for SUMCO and BM25

Looking at the results of the best combination system (SUMCO) we can observe that in most cases BM25 perform better. SUMCO obtains a higher value only in topic 9.

###### Fusion systems

The same study has been done for fusion systems. In particular, we show in the figure below the results obtained from the best fusion system (LEFU) and the state-of-the-art (BM25).

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/ap_lefu.png?fit=783%2C518&ssl=1)

Fig.4 obtained for LEFU and BM25

In these cases, our system obtained results very close to the ones of BM25 for most of the topics except for TREC\_Entity-10.

We represent in the figure below also the results obtained with SUMFU.

![](https://i0.wp.com/sease.io/wp-content/uploads/2019/11/ap_sumfu.png?fit=795%2C522&ssl=1)

Fig.5 obtained for SEMFU and BM25

Even if SUMFU results to be the worst system in average measures we can see that it performs well for the three specific topics (TREC\_Entity-6, TREC\_Entity-12, TREC\_Entity-14), obtaining results that distance themselves from those of BM25 more than the ones of the other methods.

It may occur that some of the entities retrieved by our systems were not retrieved in the pooling process and therefore are not relevant for a topic even if they are. This fact will badly affect the evaluation leading to worse performances.

Among all the used topics there are some in which we perform badly due to:

* + **number of existent relevant entities**: that was very low.
  + **document content**: it happens that the relevant documents do not contain any reference to the query topic. In this case, words aren’t matching between the document content and the query text.
  + **general query**: if the query is too general the retrieval systems will also find all those documents related to the topic that does not exactly satisfy the request.

There are also topics in which we perform better thanks to our clusters. It happens indeed that many relevant entities are in the same cluster and then they are retrieved by our systems leading to an effective improvement of the results.

In general, we can say that these topics are difficult to manage and satisfy because they request entities without explicitly mentioning them, but only giving some of their relationships information.

## Conclusion

There are many other tests we perform in the thesis. Here I would like to summarize some conclusions we drew starting from all the results and the pipeline design choices.

* + There is a high computational cost in terms of **time** in the document creation phase due to the required access to three different tables in DB through nested queries.
  + The management of **special characters** was done manually due to a problem with Terrier UTF-8 encoding.
  + The topics are difficult to manage because they aim to find entities mentioning their relationships and not the entities explicitly.
  + In **fusion** systems, we exploit positive aspects of both the methods: cluster-based and state-of-the-art.
  + The **cluster construction process** and the choice of the **number of entities** to insert into the final list are fundamental to obtaining good performances in the retrieval phase.
  + Performances are penalized in the evaluation phase due to the way the **collection test** is built.
  + Our approach turns out to be **promising** because it succeeds in finding new relevant entities with respect to the state-of-the-art.

## Future works

Further research should be carried out to improve our combination and fusion systems through a more detailed analysis of the choice of parameter settings, explore the use of fuzzy clustering, explore the effects of the aggregation of similar entities and improve combination and fusion phases.  
Regarding the first point, further studies are needed to perform an in-depth analysis of the setting of both graph embeddings and clustering parameters. The first is to obtain better entities representations through a more effective traversal of nodes and edges of the graph. The second is to obtain better clusters both as regards their completeness and consistency.   
Regarding the second point, it would be interesting to explore fuzzy clustering because it would allow for a more faithful representation of reality. It is natural to think that an entity can belong to more than one cluster.   
Regarding the third point, aggregating similar entities into a new one could overcome the pooling problem described. In this way, we would obtain a new entity containing all the useful information of the other similar ones. This approach requires a corresponding change in the set of relevance judgments, which must be subjected to the same process  
to obtain a match between entities in the evaluation phase.   
Regarding the fourth point, to improve our systems’ performances, it would be  
also useful to implement more sophisticated ways to add entities into the final run. In particular, further studies are needed to better understand how, how many and which entities to insert into the final run considering their rank, score, and belonging cluster.

It would also be useful to try the retrieval model BM25F based on fielded documents, in this way, we could even consider the type of relationship described by each triple.

With these last considerations we have reached the end of this journey, I hope this presentation has intrigued you and provided food for thought. For those wishing to learn more about what I have shown, my thesis can be consulted through the Padua Thesis portal [[1]](http://tesi.cab.unipd.it/63164/1/anna_ruggero_tesi.pdf)

Thank you!

## Need Help With This Topic?​​

If you’re struggling with graph embeddings, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with graph embeddings, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)