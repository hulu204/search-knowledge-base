---
title: 'RRF is Not Enough'
company: softwaredoug
tag: 召回
date: 2024-11-03
url: https://softwaredoug.com/blog/2024/11/03/rrf-is-not-enough
account: 
origin: harvest3-202607
---
Hybrid search means combining lexical and vector search results into one result listing.

“We’ll just use [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)” I’m sure I’ve said from time to time.

As if RRF is kind of “a miracle occurs”. You get the best of both worlds, and suddenly your search looks incredible.

Take the query `hello to the planet`. Let’s say we start with reasonable results from a vector search system (follow along in [this notebook](https://colab.research.google.com/drive/1pXHqE8d_wNhLYS31O9omCKPAAm4shVaf?authuser=1#scrollTo=qqw0zhcTa9Pg))

| vector\_sim | texts | vector\_rank |
| --- | --- | --- |
| 0.19054140351577573 | greetings to the people of the earth | 1 |
| 0.18714326530195094 | hello to the planets in my empire | 2 |
| 0.18575998354351458 | hello world | 3 |
| 0.176119269155595 | hello my world | 4 |
| 0.17393706389759572 | hi Planet Earth | 5 |
| 0.16546218247899153 | hello to my planet, where I lost my keys. | 6 |
| 0.16345108862553018 | hello to the planet where I keep my stuff, a beautiful place with trees. | 7 |
| 0.16196139040721674 | the planet says hello to bees | 8 |
| 0.16190546834847355 | hello mars! | 9 |
| 0.1486092230250017 | Hello to Terra! | 10 |
| 0.09424116471867336 | tomorrow is the first day of the rest of your life | 11 |
| 0.05778716802233709 | belching is a bad habit | 12 |

These are not bad. All the top results have to do with greeting ‘the planet’. Primarilly the planet earth.

We might notice a minor improvement we could make.

What if the user actually remembers text beginning with the phrase “hello to the planet”… Specifically they want the document beginning with “hello to the planet where I keep my stuff…”. If we added some lexical search, we might promote this to the top.

To perform RRF, we just also need the rank of the BM25 scores, and then we can merge the ranking with

```
RRF_score = 1/vector_rank + 1/bm25_rank
```

Easy enough.

We do this, and run our A/B test, only to see… 📉💥😢 Not Stonks.

What happened? We look under the hood at this specific query again, and…

| index | vector\_sim | texts | vector\_rank | bm25\_sim | bm25\_rank | rrf\_score |
| --- | --- | --- | --- | --- | --- | --- |
| 9 | 0.19054140351577573 | greetings to the people of the earth | 1 | 0.8085092902183533 | 4 | 1.25 |
| 1 | 0.16196139040721674 | the planet says hello to bees | 8 | 1.2901966571807861 | 1 | 1.125 |
| 5 | 0.18714326530195094 | hello to the planets in my empire | 2 | 1.2078437805175781 | 2 | 1.0 |
| 6 | 0.16345108862553018 | hello to the planet where I keep my stuff, a beautiful place with trees. | 7 | 0.8348331451416016 | 3 | 0.47619047619047616 |
| 0 | 0.18575998354351458 | hello world | 3 | 0.26555198431015015 | 9 | 0.4444444444444444 |
| 2 | 0.16546218247899153 | hello to my planet, where I lost my keys. | 6 | 0.7465024590492249 | 5 | 0.3666666666666667 |
| 7 | 0.17393706389759572 | hi Planet Earth | 5 | 0.49154359102249146 | 7 | 0.34285714285714286 |
| 4 | 0.176119269155595 | hello my world | 4 | 0.24279040098190308 | 11 | 0.34090909090909094 |
| 8 | 0.1486092230250017 | Hello to Terra! | 10 | 0.6388745307922363 | 6 | 0.26666666666666666 |
| 11 | 0.09424116471867336 | tomorrow is the first day of the rest of your life | 11 | 0.4355449378490448 | 8 | 0.2159090909090909 |
| 3 | 0.16190546834847355 | hello mars! | 9 | 0.26555198431015015 | 10 | 0.2111111111111111 |
| 10 | 0.05778716802233709 | belching is a bad habit | 12 | 0.0 | 12 | 0.16666666666666666 |

Huh the results got WORSE!!

What happened!?

Well the BM25 results kind of suck for this query. Actually contradicting the already really good vector search results:

| index | texts | bm25\_sim | bm25\_rank |
| --- | --- | --- | --- |
| 1 | the planet says hello to bees | 1.2901966571807861 | 1 |
| 5 | hello to the planets in my empire | 1.2078437805175781 | 2 |
| 6 | hello to the planet where I keep my stuff, a beautiful place with trees. | 0.8348331451416016 | 3 |
| 9 | greetings to the people of the earth | 0.8085092902183533 | 4 |
| 2 | hello to my planet, where I lost my keys. | 0.7465024590492249 | 5 |
| 8 | Hello to Terra! | 0.6388745307922363 | 6 |
| 7 | hi Planet Earth | 0.49154359102249146 | 7 |
| 11 | tomorrow is the first day of the rest of your life | 0.4355449378490448 | 8 |
| 0 | hello world | 0.26555198431015015 | 9 |
| 3 | hello mars! | 0.26555198431015015 | 10 |
| 4 | hello my world | 0.24279040098190308 | 11 |
| 10 | belching is a bad habit | 0.0 | 12 |

We’re getting the worst-case scenarios for bag of words results. The first result literally has nothing to do with.

RRF’ing bad search into good search will just drag down the good search. You actually have to give care that both sets of results deliver relevant search results to improve search.

## How to use RRF

Use RRF, however, when you actually have distinct, disjoint sources of relevant search results. Each tuned to high precision.

If we change our BM25 solution to do phrase search instead of a bag of words query, we improve the precision of those results, and improve the overall experience.

| index | vector\_sim | texts | vector\_rank | bm25\_sim | bm25\_rank | rrf\_score |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.18714326530195094 | hello to the planets in my empire | 2 | 1.2078437805175781 | 1 | 1.5 |
| 9 | 0.19054140351577573 | greetings to the people of the earth | 1 | 0.0 | 3 | 1.3333333333333333 |
| 6 | 0.16345108862553018 | hello to the planet where I keep my stuff, a beautiful place with trees. | 7 | 0.8348331451416016 | 2 | 0.6428571428571428 |
| 0 | 0.18575998354351458 | hello world | 3 | 0.0 | 4 | 0.5833333333333333 |
| 4 | 0.176119269155595 | hello my world | 4 | 0.0 | 5 | 0.45 |
| 7 | 0.17393706389759572 | hi Planet Earth | 5 | 0.0 | 6 | 0.3666666666666667 |
| 2 | 0.16546218247899153 | hello to my planet, where I lost my keys. | 6 | 0.0 | 7 | 0.30952380952380953 |
| 1 | 0.16196139040721674 | the planet says hello to bees | 8 | 0.0 | 8 | 0.25 |
| 3 | 0.16190546834847355 | hello mars! | 9 | 0.0 | 9 | 0.2222222222222222 |
| 8 | 0.1486092230250017 | Hello to Terra! | 10 | 0.0 | 10 | 0.2 |
| 11 | 0.09394807204762956 | tomorrow is the first day of the rest of your life | 11 | 0.0 | 11 | 0.18181818181818182 |
| 10 | 0.05778716802233709 | belching is a bad habit | 12 | 0.0 | 12 | 0.16666666666666666 |

When we have different retrieval sources, of very different technologies, we increase the likelihood of disjoint results. Now if we bias BOTH to give their highest degree of precision, and intentionally remove weird results, and let each focus in on a different, plausible use-case, we improve recall AND can trust the RRF score to reflect true definitions of overall relevance.

This is a bit counter to the conventional wisdom when combining retrieval sources. We usually say we want to cast a wide net at these early retrieval layers. But maybe, in the end, RRF is a great way to combine two precise retrieval sources into two precise result sets with a bit higher recall?

In this way, RRF improves recall and not precision?

## Instead of RRF, first understand intent, then choose the best solution

In my opinion, a better path is to redefine the problem.

What’s the users intent with this query? Do they

(a) Want text similar to the “hello world” text?
(b) Lookup a piece of text that uses this phrase?

Based on historical data, it’d be better to probabilistically decide which intent is more likely, then route the query accordingly to the best system to handle that query.

Perhaps we decide it’s 80% (a) vs 20% (b). Then we dedicate roughly 80% of our screen space to (a) and 20% to the other. We can now weight RRF accordingly

```
RRF_score = (80/vector_rank) + (20/bm25_rank)
```

We can keep going, why should we think of “vector search” and “bm25 search”? We ought to think in terms of intent:

```
RRF_score = (80/user_wants_semantically_similar_text) + (20/user_wants_to_closely_match_the_words)
```

That, we might think to generalize AWAY from thinking in terms of vector search and lexical search to systems solving the user’s specific problems. Towards [query understanding](https://queryunderstanding.com/). And we’ve *always done this in search*. Perhaps hybrid search simply means ‘choosing the right ranking solution for the job’.

Perhaps the REAL hybrid search has been inside of us all along ❤️

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---