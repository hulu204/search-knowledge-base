---
title: 'NDCG is overrated'
company: softwaredoug
tag: 评测
date: 2023-05-06
url: https://softwaredoug.com/blog/2023/05/06/ndcg-is-overrated
account: 
origin: harvest3-202607
---
In search, we spend a lot of time OBSESSING over stats like [NDCG](https://towardsdatascience.com/demystifying-ndcg-bee3be58cfe0), [ERR](https://notesonai.com/Expected+Reciprocal+Rank), [mean-average precision](https://www.v7labs.com/blog/mean-average-precision), yadda yadda

These sort of stats rely on labeled [judgment lists](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list), to decide whether a search change is “good”, or not. In theory, as relevant results shuffle to the top, NDCG improves, and we have a great relevance change!

But as Pinecone’s [Edo Liberty](https://www.linkedin.com/in/edo-liberty-4380164) shared on LinkedIn:

![NDCG is overrated](/assets/media/2023/ndcg-is-overrated.png)

Hot take. Nice! I like it.

I want to share a different way to think about offline search evaluation. To help teams without the resources to gather judgment from clicks or labelers. But also for everyone else - NDCG and pals are just one, narrow, specific view of the search world.

You CAN get started on search relevance without NDCG and judgments. Let’s discuss how.

First, yes (n)DCG is a good stat 🐶, but, fundamentally:

1. Judgments dont cover every document - judgments will lack coverage for new documents we shuffle to the top with our relevance change. IE we have [*presentation bias*](https://softwaredoug.com/blog/2022/07/16/what-is-presentation-bias-in-search)
2. Judgments encode biases and assumptions - Even with a lot of engagement data or human labels - humans [encode a lot of bias into judgments](https://en.wikipedia.org/wiki/Thinking,_Fast_and_Slow#Heuristics_and_biases). And whatever “model” we develop to grade results will also require potentially wrong assumptions from the search team.
3. Search quality goes beyond query-document relevance - Judgments assume query-document relevance is the most important thing. What about how results compare to adjacent results? search result diversity? speed of search, the UI, etc - other things that also drive search success.

So yeah, its just one stat. A good statto to love 🐶 But let’s not assume it’s magical.

What might we ask instead?

## Will our A/B test evaluate the right things?

We’re almost always using NDCG to decide whether to graduate our change to a full, “gold standard”, A/B test.

Why not focus on whether or not we’ll get a good signal in this A/B test?

1. Did we effect the change we intended? Functionally, is it doing what we want?
2. Did we focus our change on poor performing queries without impacting queries that currently perform well?
3. What is the magnitude of the change? Is our change a massive sea-change, or, do we just tweak a few queries?

The goals here:

* Mechanically effect a change we mean to, and understand the technical limitations to our approach. Kinda like a (quantitative) unit test!
* Create a guardrail for queries that work well, target queries that don’t work well
* Understand the expected impact size of our change in an A/B test

Instead of just NDCG, we instead learn whether our A/B test will measure what we expect to along with the potential size of that change.

## Step 1 - Did we make the intended change?

Let’s say we want to classify queries to a taxonomy. Like what [Daniel Tukenlang writes about](https://dtunkelang.medium.com/query-understanding-divided-into-three-parts-d9cbc81a5d09). The query “blue tennis shoes” maps to “apparel -> footwear -> athletic shoes”.

Before checking NDCG, let’s ask:

1. Do we correctly classify queries to the taxonomy we expect (ie documents at the right taxonomy node)?
2. Do we handle all the edge cases - like what if the query taxonomy is *close* to the document’s taxonomy node, but not exact (ie a sibling, or direct parent/child?). Or is the taxonomy *good*? Do we handle the areas where the taxonomy classification of results itself is poor? Or if the query is classified to many dispirate taxonomic areas (notebook is a laptop and stationary).

We might come up with a metric to measure taxonomical proximity between query and document. Then proceed to measure how close our approach came to getting to the expected taxonomy node.

Now we ask - how close did we achieve our goal? Do we need to tweak our algorithm? Can we automate that tweaking with an optimizer or machine learning to get what we want?

## Step 2 - Did we target the intended query population?

The next step is to determine whether we impacted the expected queries. We hope to change queries not performing well, and leaving alone the high performers.

There’s a whole family of statistics to help us understand the *change* in search results:

* [Jaccard index](https://opensourceconnections.com/blog/2021/07/23/jaccard-index-for-search-regression-testing/) - simple the proportion of the set of top N changed, without regard for position
* [Rank Biased Overlap](https://link.springer.com/chapter/10.1007/978-3-031-15037-1_11) - measures change between two sets of queries, but higher scores reflect change in higher positions.

(among others)

This assumes we can know what queries are doing well/not well. “Performing well” here means queries with high click-thru rate, conversions, or simply the SERP liked by human raters.

This is not the judgment-based model of relevance. Instead it’s just at the query grain. Does a query do what we expect or not? Perhaps, after all, with the many considerations beyond just the query-document relationship, this better reflects search quality than NDCG?

## Step 3 - What is the overall magnitude of the change?

Can we try to estimate the potential upside/downside of this change?

We don’t know if we made a good change or bad change, but we can at least try to guess whether the effect size in an A/B test will be large or small.

We might ask, given the population of queries, what proportion of search interactions are we impacting? If our changes all happen to head queries, even a handful, we could see a large effect size – high risk high reward!. If we change a small number of tail queries, we’d expect to see barely any shift..

Again, we cannot guess whether the change will be a good one or bad one. However, coupled with the previous two evaluation points, we can know, most importantly: **does our A/B test accurately measure our change, and only our change?**.

We can also ask **is the effect size worth the investment?**. A big change will significantly increase the knowledge you gain from the test. Maybe you’ll learn users *really hate this!*. That’s extremely valuable to know. You might also learn users love it and have a blockbuster experiment!

## But what about good doggo NDCG🐕 ?

I don’t believe in perfect metrics. I believe in metrics that measure one thing well.

Unless you’re training a model, and need to obsess over its accuracy, let’s leave NDCG alone.

![Leave NDCG Alone](/assets/media/2023/leave-ndcg-alone.png)

NDCG still tells us a lot. It helps measure precision in two cases - the entire corpus AND the corpus of only labeled docs.

First, within the entire corpus, it’s nice to know when known-bad results bubble to the top. We’ll see NDCG harmed in this case. We might question the assumptions behind what we’re building. It’s an indication we might be creating a harmful, not helpful, change. I’d argue that the converse – good results towards the top – is actually less helpful. Because we don’t know what other, potentially even better results, might be out there!

Second, what if we built a test corpus of only labeleld query-doc judgments? Then we we sidestep the problem of “what if a result doesn’t have a relevance label for this query?”. We would hope in this narrower universe, we’re improving NDCG, and that this change reflects how a larger corpus would perform.

Alongside evaluating whether we’re headed to a meaningful A/B test, NDCG CAN help guide our offline experimentation. But it’s not the end, or even the beginning, of the story. It’s just one number among a family of metrics to help us explore and construct great experiments.

---

### Afterword - Inspiration, acknowledgments, bibliography

For your further reading, I want to shoutout contributions to the field from many colleagues.

Doug Rosenfeld, Tito Sierra, Tara Diedrechson, James Rubenstein (and many others) at LexisNexis who discuss [whole SERP evaluation](https://www.slideshare.net/o19s/haystack-2019-making-the-case-for-human-judgement-relevance-testing-tara-diedrichsen-and-tito-sierra) and many other ways of evaluating search relevance. Great talks here:

* [Building a Data Driven Search Program with James Rubinstein of LexisNexis](https://www.youtube.com/watch?v=vSy2gxUlGGI) - a great deal of detail in how LexisNexis evaluates search online and offline.
* [Doug Rosenoff - Engagement DCG vs SME DCG - Evaluating the Wisdom of the Crowd](https://www.youtube.com/watch?v=94QmIA_t4Vs) - the interesting contrasts between engagement vs human DCG (they’re not correlated!) are fascinating.

Andreas Wagner at Searchhub who shares many cases where search quality goes beyond relevance - such as [this talk](https://www.youtube.com/watch?v=QU0ndZvM_LQ) and [this one](https://www.youtube.com/watch?v=xgHf9k272nc). In particular how a page of perfectly relevant results can still fail to capture search quality, but a page of contrasting options (some maybe irrelevant!) performs better.

Andy Toulis, and all the Relephants at Shopify for all the fun we’ve had wrestling with thorny issues around relevance methodology. In particular Andy and I [gave a talk at Haystack last year](https://www.youtube.com/watch?v=YXw3fyeXgdc) a bit about how all that worked.

And finally, the extensive work of OpenSource Connections who offers [search relevance and quality training](https://opensourceconnections.com/training/).

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---