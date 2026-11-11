---
title: 'Online Testing for Learning To Rank: Interleaving'
company: Sease
tag: 排序
date: 2020-05-11
url: https://sease.io/2020/05/online-testing-for-learning-to-rank-interleaving.html
account: 
origin: harvest3-202607
---
If you have read the previous post about [the importance of online testing for learning to rank](https://sease.io/2020/04/the-importance-of-online-testing-in-learning-to-rank---part-1.html), you should know by now how many fantastic things can be done with online testing! In particular, the advantages that interleaving brings with respect to A/B testing, but you are still waiting for the answer to a question: *how to implement it?*

Let’s see together some of these interleaving implementations. First of all, let’s describe the first implemented interleaving approach, and then I will present to you the two most used ones.

## balanced interleaving

The first implementation is **balanced interleaving**.

Balanced interleaving is the simplest method for interleaving. It always puts in the top ***k*** results of the result list ***lI***, and documents from the top *k* results of **both lists *lA* and** ***lB**.*  
Suppose to have two pointers ***ka*** and ***kb***, for the two ranked lists ***lA*** and ***lB***, always pointing to the higher result of each list.

The implemented algorithm is the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/04/balanced-1.jpg?fit=856%2C690&ssl=1)

Let’s make an example to explain everything more clearly.

Suppose to have ***lA* = (*a1*, *a2*, …) and *lB* = (*b1*, *b2*, …)**.  
We give priority to one of the two models with the **randomBit()** function (line 2). The chosen model will decide first which documents to add to the final list. Suppose we select ***model\_A*: *Afirst = 1***.  
Then we will repeat this process unless we have at least one document in both *lA* and *lB* :

1. 1. If **(*ka* < *kb*)** or (***ka* = *kb*** and *model\_A* is the favourite one): if the document pointed by *ka* isn’t already in *lI*, we insert it.
   2. Else: if the document pointed out by *kb* **isn’t already in *lI***, we insert it.

At the end of this loop, we will have added all the documents from *lA* and *lB* (with at most one discard) in *lI*.

We can, therefore, see that in this way we create a unique list *lI* containing documents from both the model, respecting the relative rank of the documents inside their original list ( *lA* and *lB*).

##### How to evaluate the results?

The obtained result list ***lI* = (*i1*, *i2*, …)** is now shown to the user, who clicks those documents that mostly reflect his information need. Suppose to call *c1*, *c2*, … the ranks of the clicked documents and ***cmax = maxici***.  
To derive a preference between the two models, we count the number of clicked documents from each model in the top *k* results of *lI*, where:

***k = min*{ *j*: (*icmax*= *aj*) or (*icmax*= *bj*)}** .

In particular, the number of clicked documents for each model is:

***ha* = |{*cj*: *icj* ∈ (*a1*, …, *ak*)}**| for *model\_*A  
***hb* = |{*cj*: *icj* ∈ (*b1*, …, *bk*)}**| for *model\_B*  
If ***ha* > *hb*** *model\_A* will be the favourite one, if ***ha* < *hb*** *model\_B* will be the favourite one and if ***ha* = *hb*** we have a tie.

This is a preference derived for the query *q*, but many other queries can be done during the online evaluation. How can we derive a preference for all the queries?  
Let *wins*(A) be the number of comparisons in which model\_A won, wins(B) the number of comparisons in which *model\_B* won and *ties*(A, B) the number of times we have a tie.  
To compute the overall preference we use another statistical measure:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/04/delta.jpg?fit=798%2C195&ssl=1)

A positive value of **ΔAB** means that *model\_A* is the favourite one, and a negative value of **ΔAB** means that *model\_B* is the favourite one.

##### Drawbacks

One drawback of this approach arises when comparing two models that produce very similar ranking lists. If for example, the ranking list of *model\_A* is identical to the one of *model\_B* except for the first document: ***lA* = (*a*, *b*, c, d)** and ***lB* = (*b*, *c*, d, a)**. The comparison phase will bring the *model\_B* to win more often than *model\_A*. This happens regardless of the model chosen by ***RandomBit()***.  
This drawback arises due to how the *k* parameter is chosen (the min rank that includes all the clicked documents) and to the fact that *model\_B* ranks higher than *model\_A* for all documents except for *a*.

## Team-draft Interleaving

The **team-draft interleaving** approach overcomes the issue described for balanced interleaving with a new way of constructing the interleaved result list *lI*. In particular, the algorithm relies on the widely used method of team captains, in team matches, for the selection of the players.

Suppose to have **two captains *A* and *B***. Suppose to choose one of the two by chance at each round. Then the selected captain will pick his favourite player still available, add him to the team and then leave the turn to the other captain who will do the same. This will repeat unless there are players available.

The implemented algorithm is the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/04/team-1.jpg?fit=1358%2C766&ssl=1)

Let’s also make here an example to explain everything more clearly.

Suppose to have ***lA* = (*a1*, *a2*, …)** and ***lB* = (*b1*, *b2*, …)**.  
Here, like in balanced interleaving, the choice of the starting model is given by ***randomBit()***, but this choice is made at every round and not only at the beginning of the algorithm.  
We will repeat this process unless we have at least one document in both *lA* and *lB* :

1. If (the size of *TeamA* is smaller than the one of *TeamB*) or (the two teams have the same size and *model\_A* has the priority): *k* will take the rank of the top document in *lA* not yet in *lI*; this document will be added to the interleaved list *lI* and to the *TeamA* set (this set record all the documents that are taken from *model\_A*).
2. Else: *k* will take the rank of the top document in *lB* not yet in *lI*; this document will be added to the interleaved list *lI* and to the *TeamB* set (this set records all the documents that are taken from *model\_B*).

At the end of this loop, we have added all the documents from *lA* and *lB* (with at most one discard) in *lI*. We will also obtain the list of documents belonging to *TeamA* and *TeamB*.

##### How to evaluate the results?

Again, the obtained result list ***lI* = (*i1*, *i2*, …)** is shown to the user, who clicks those documents that mostly reflect his information need. Suppose to call *c1*, *c2*, … the ranks of the clicked documents.  
To derive a preference between the two models, we count the number of clicked documents in each *Team*:

***ha* = |{*cj*: *icj* ∈ *TeamA*|** for *model\_*A  
***hb* = |{*cj*: *icj* ∈ *TeamB*}|** for *model\_B*  
If ***ha* > *hb*** *model\_A* will be the favourite one, if ***ha* < *hb*** *model\_B* will be the favourite one and if ***ha* = *hb*** we have a tie.

In the same way as the balanced interleaving, we can derive a preference for all the queries.  
We compute ***wins(A)*, *wins(B)*, *ties(A, B)*** and then **ΔAB**.

##### Drawbacks

Also for team-draft interleaving there is a drawback.  
Suppose to have two ranked lists: ***lA* = (*a*, *b*, c, d)** and ***lB* = (*b*, *c*, d, a)**. Suppose ***c*** to be the only relevant document.  
With this approach, we can obtain four different interleaved lists:

***lI1* = (*aA*, *bB*, *cA*, *dB*)**  
***lI2* = (*bB*, *aA*, *cB*, *dA*)**  
***lI3* = (*bB*, *aA*, *cA*, *dB*)**  
***lI4* = (*aA*, *bB*, *cB*, *dA*)**

All of them put ***c*** at the same rank.  
Applying our preference computation will result in a tie between the two models, when, actually, ***lB*** should be chosen as the best one.

## Probabilistic Interleaving

The **probabilistic interleaving** approach overcomes the issue described for balanced interleaving and team-draft with a new way of constructing the interleaved result list *lI*. In particular, the algorithm relies on the creation of a probability distribution over the ranking lists. This distribution allows every document to have a non-zero probability of being added to the interleaved result list.

The implemented algorithm is the following:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/04/probabilistic-2.jpg?fit=1176%2C750&ssl=1)

The equation for computing the probability distribution, given a ranked list of documents, is:

![](https://i0.wp.com/sease.io/wp-content/uploads/2020/04/softmax.jpg?fit=1134%2C201&ssl=1)

Let’s explain a bit more how it works.

First of all, we have to spend some more words on the computation of the probability distribution (line 3). Suppose to start with *model\_A, in line (3) we have the initialization of s(lA). What does it mean*?  
The idea behind this step is to associate each document of ***lA*** (and after, *lB*) with a probability. This probability is computed using a ***softmax*** function on the rank of each document. This allows us to obtain a higher probability for documents with higher ranks and a lower probability for documents with a lower rank. In this way, documents at the top of the list will have a higher probability of being chosen as we expected, since we ideally would like to maintain the relative rank as much as possible. Moreover, all the documents of *lA* have a non-zero probability to be chosen for *lI*, increasing the fairness of the algorithm.

Once we have the distribution for both the models (*model\_A* and *model\_B*), we start to create the interleaved list *lI*.  
At every loop:

1. 1. A random model is selected (as in team-draft interleaving), and the choice is stored both in the *assignment* variable and in the ***assignment*** vector. The last one will report the final sequence of assignments that happened during the interleaved list creation.
   2. The *not\_assignment* variable is upgraded with the opposite value of the *assignment* variable. This variable is needed by the *remove\_and\_renormalize()* method to upgrade the probability distribution after the document selection.
   3. A document is selected by the *s(lassignment)* model distribution. How the choice happens is through a sample without replacement from the probability distribution of the chosen model. This document is then added to *lI*.
   4. The selected documents are removed from the ranked list of the not-chosen model. The probability distribution is then recomputed due to this removal.

After the realization of *lI,* an evaluation similar to one of the previous methods can be applied. Alternatively, a probabilistic comparison with marginalization can be done. I’m not going to explain it, but if you are interested in this topic I recommend you to read [[1, 2]](#ref).

This implementation, as said in [[1]](#ref), ensures no bias. First because, in expectation, each ranker contributes the same number of documents to *lI*.   
Second, because the ***softmax*** function, constructed for each ranker, has the same shape and thus, the probability allocated to each document, depends only on its rank.   
Third, because the use of assignments guarantees that each click is attributed to only one list, as in the team-draft method.

##### Drawbacks

The use of a probability distribution for the document selection increases the fairness of the algorithm, but it could also lead to a worse user experience. It may indeed happen that documents with a low rank are selected and put higher in the final list *lI.*

## Summary

Let’s recap the main points of this blog post.

Making online testing is very important because it allows us to have direct feedback on how our model is performing. All the obtained results are computed on user interactions, which are the most reliable form of the relevance expression.

There are several advantages to interleaving with respect to A/B testing:

* + **Reduces variance:** in the interleaving approach, unlike A/B testing, there isn’t a separation of the users in groups. Here the same user evaluates at the same time both the models, making it possible to execute a direct comparison between them. This approach overcomes the problem of the users’ variance that can come out with the query traffic separation.
  + **More sensitive:** due to the high user variance, the A/B testing is also less sensitive to differences between models. The smaller the difference between models, the more difficult it is to evaluate the variation.
  + **Less traffic:** due to less sensitivity, the A/B testing requires much more traffic than interleaving to achieve the same result. We need to analyze many user interactions to understand if the obtained results are reliable.
  + **Less time:** due to the much traffic required, A/B testing takes longer to execute than interleaving. The more time we run the test, the more interactions we collect.

There are three main implementations of interleaving:

* + **Balanced Interleaving:** based on a simple alternation of documents coming from both the models we are evaluating. It allows us to present results from both models, **but it’s not able to correctly choose the best one when they generate very similar rankings**.
  + **Team-Draft Interleaving:** based on the player’s selection done by captains in a team match. As for the balanced interleaving, also here there is a **specific case in which the method isn’t able to select the correct method as the winner**.
  + **Probabilistic Interleaving:** based on the generation of a probability distribution associated with each model we want to evaluate. This method **can lead to a worse interleaved list in terms of ranking, but it is more fair, sensitive, and presents less bias than the other two approaches**.

###### REFERENCES

[1] Hofmann, Katja, Shimon Whiteson, and Maarten De Rijke. “A probabilistic method for inferring preferences from clicks.” *Proceedings of the 20th ACM international conference on Information and knowledge management*. 2011.  
[2] Hofmann, Katja. “Fast and reliable online learning to rank for information retrieval.” *SIGIR Forum*. Vol. 47. No. 2. 2013.  
[3] Chapelle, Olivier, et al. “Large-scale validation and analysis of interleaved search evaluation.” *ACM Transactions on Information Systems (TOIS)* 30.1 (2012): 1-41.  
[4] Hofmann, Katja, Shimon Whiteson, and Maarten De Rijke. “Fidelity, soundness, and efficiency of interleaved comparison methods.” *ACM Transactions on Information Systems (TOIS)* 31.4 (2013): 1-43.

## Need Help With This Topic?​​

If you’re struggling with Interleaving for Learning to Rank, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Interleaving for Learning to Rank, don't worry - we're here to help! Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)