---
title: 'Grug-brained evals'
company: softwaredoug
tag: 评测
date: 2025-06-22
url: https://softwaredoug.com/blog/2025/06/22/grug-brained-search-eval
account: 
origin: harvest3-202607
---
After years of chasing the perfect search evals, my dumb [grug brain](https://grugbrain.dev/) has finally realized:

> No such thing “perfect metric”. Playing with metric mean no real work get done. Grug just want to know if “change do what I expect”. Let big brain A/B test tell me if good.

In other words: evals exist to see if a change works as intended. Not to tell us if its “good”.

## NDCG is overrated

In search, [NDCG](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) is a metric that computes whether we’re producing the expected search results. It ranges from from 0(bad?)-1(good?). NDCG relies on labeling individual search results accurately for a query. Is the move “Forrest Gump” relevant for Rambo? No. But “First Blood” is. If First Blood ranks above Forrest Gump, NDCG for the `rambo` query will be closer to 1. Get enough of labeled search results, for enough queries, and we can test and iterate on our ranker.

Or so the story goes.

I’ve written in the past this [eval regime is overrated](https://softwaredoug.com/blog/2023/05/06/ndcg-is-overrated). Trying to label a search result accurately hard. For many reasons:

* human labelers and LLMs are often not representative of your users.
* human labelers get tired and make mistakes
* internal, influential [HIPPOs](https://www.capterra.com/glossary/hippo-highest-paid-persons-opinion-highest-paid-person-in-the-office/) labeling results, may have opinions not correlated with real users
* clickstreams are hard to interpret, and contain all kinds of biases that dictate why something was ‘clicked’ (the UI, the tendency for users to click high up on the page regardless, if its spicy, or not click if it looks boring, etc)
* long tail queries get few interaction, leaving us with interaction data only on the most common queries

People tie themselves in knots eliminating all these errors. And what happens? **To eliminate errors, we add complexity. Complexity begets harder to understand errors**.

Sure getting Steve from accounting to label some search results will be error prone. But you know exactly how Steve will screw up. You know Steve well.

But modeling out how users click search results to tease out “relevance” can be a tricky task, for all the reasons listed above.

Not to mention, the fundamental assumption here may be flawed. Labeling a single search result as relevant/not, then improving that ranking, is only one piece of [search quality](https://opensourceconnections.com/search-ai-consulting/what-is-search-result-quality/). Search quality means so much more: diverse search results, clear query understanding, speed, reflecting the intent back to the user, good percieved relevance, etc …

Given all these issues, which path do you go down?

## Grug-brained eval loop

IMO, most people would do fine with the following algorithm:

1. Identify a population of queries you want to fix
2. Gather 10-20 labeled queries with a tool from internal users (ie [Quepid](https://quepidapp.com) or something)
3. Tune those queries so tehir NDCG gets better (change ranking, improve query understanding, ??)
4. Regression test old queries, from previous iterations of this loop, make sure those didn’t break
5. GOTO 1

This doesn’t measure “quality”. It measures “are we fixing things we intend, without breaking other things”?

That is the team is defining a (maybe wrong) goal and measuring its progress towards that goal. That is it. That’s the tweet.

For example, if you intend your change to improve searches for products by name, then you’d go and ask the team to label some search results for queries. Including what the “right answer” ought to be. You then try some fixes, making sure you only solved this problem (steps 3/4), and ship if it works.

We know “the team” has error. But we can probably define that error. It boils down to the team needing to continually learn what users want from search. Which they should do anyways.

How do we measure quality then? We ship our changes to an actual A/B test. Or usability study. These are explicit studies of quality. Actual “quality” means whether we sell more products, increase DAU, or help solve business problems. This goes far beyond just a relevance change - and indeed it may be that *relevance* itself isn’t what holds back our search, but other search quality issues.

A great deal of complexity comes in strongly coupling these two worlds. World (a) do we solve the problem we intend to solve and (b) does solving that problem matter to users? Tightly coupling the two with complex modeling is hard, and requires big brains. Do it last.

## When to go big-brained

Of course cases still exist when we want to go big brained. If we want to train a model, our judgment list needs to point to “true north” of quality. That’s 90% of the work, and takes considerable care. We don’t spend our cycles modeling training, but getting trustworthy training data. This is what has mattered when I’ve built ranking models – Every. single. time.

Here you want to pull out all the stops. Get big brained data scientists to learn about topics like [click models](https://link.springer.com/book/10.1007/978-3-031-02294-4). Get a good Learning to Rank book, like, naturally [AI Powered Search](http://aipoweredsearch.com) chapters 10-12, and really buff up your relevance capabilities.

But I’d argue many teams aren’t here yet, they’re just trying to make their Elasticsearch or whatever a bit better, and they’d do better to be grug-brained data scientists, then waste their limited cycles on big-brained dreams that may take away from actual work tuning relevance.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---