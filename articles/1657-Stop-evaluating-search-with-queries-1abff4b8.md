---
title: 'Stop evaluating search with queries'
company: softwaredoug
tag: 评测
date: 2026-03-30
url: https://softwaredoug.com/blog/2026/03/30/session-vs-query-based-search-evals
account: 
origin: harvest3-202607
---
To evaluate search, we typically [build a judgment list](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list). We transform clickstream data into evaluation data. This labels a result as relevant (or not) for a query. Let’s walk through an example with movie `rocky` - first to see the classic method.

At some point in the past we observed this session:

| Rank | Query | Document | Click? |
| --- | --- | --- | --- |
| 1 | rocky | Rocky | False |
| 2 | rocky | Creed | True |
| 3 | rocky | Alien | False |

And some other time, for query Rocky, we observe another interaction:

| Rank | Query | Document | Click? |
| --- | --- | --- | --- |
| 1 | rocky | Alien | False |
| 2 | rocky | Star Wars | False |
| 3 | rocky | Rocky | True |

Adding up these two, we’d have:

| Query | Document | Clicks | Impressions | CTR |
| --- | --- | --- | --- | --- |
| rocky | Rocky | 1 | 2 | 0.5 |
| rocky | Creed | 1 | 2 | 0.5 |
| rocky | Alien | 0 | 2 | 0 |
| rocky | Star Wars | 0 | 1 | 0 |

Now we can use that to put a number on whether we produce good results for `rocky` -

```
# Some offline experiment produces these results for rocky
q=rocky
1. Creed (0.5) <-- we label each row with its relevance for the query
2. Rocky (0.5)
3. Star Wars (0)
```

Here we could compute all kinds of statistics (ie [NDCG](https://www.evidentlyai.com/ranking-metrics/ndcg-metric)). But lets be naive, and average them. This query is (0.5 + 0.5 + 0) / 3 = **0.333**. If we could manage to find more relevant results (ie results that got more clicks / impressions) this number would go up.

I call this model query based evaluation. There’s nothing wrong with it. It works. It’s what I’ve done my whole career.

## **But there’s a different way - session based eval**

What if we just directly used the original session. We “replay the session”, not the query. Then see whether our system would do better at satisfying a past user interaction.

For example, evaluating against the first session, we get

```
q=rocky
1. Creed 👍
2. Rocky
3. Star Wars
```

We’ve placed the clicked item towards the top. The second session we get:

```
q=rocky
1. Creed
2. Rocky 👍
3. Star Wars
```

For the second session, the clicked result lives in the second position. Not as good.

When we average 1 / rank of the right answer (mean reciprocal rank). Here that’d be (0.5 + 1.0) / 2 = **0.75**

Essentially we decide there’s no *one right answer* for the query. The question we answer: would we have satisfied some past user? Based on a single event of user searching + clicking, would we have done better by that user?

Here we’ve stuck to one query. But that’s not how session based sampling would work. In reality, we’d first sample some N sessions regardless of query. We expect that N to fairly represent the user experience. It might have 5000 queries? 3000? It doesn’t much matter.

Let’s walk through why we would / would not take this approach

### Advantage 1 - Improved sampling accuracy

Remember that when we ship this to production, the question won’t be “how many queries did we improve?”, it will be “did we improve most user’s experience with search?”. Users experience search in sessions, not in queries.

With query-based evaluation, good teams try to fix this. We reweigh each query to get back to how many sessions it represents. Very popular queries get higher weight proportional to how many sessions it represents. Tail queries much less weight.

Further with query-based evaluation, we sample at the wrong level. We put the cart before the horse. We don’t try to get a representative sample of user sessions. We instead try to identify 1000 or so queries we want to fix.

Political polling serves as a useful analogy. Imagine you wanted to poll the electorate about an issue. What if you first identified the cities you wanted to poll before arriving at a conclusion. So you choose 1000 random cities. Ranging from big cities like New York to smaller towns like Chingoteague, Virginia. You poll these places, and then work backwards: weighing the New York result higher than the Chingoteague.

That’s a bit backwards. Nobody polls like that - they just try to truly randomize the voters to get a picture of the overall electorate. Pollsters call this [probability based sampling](https://aapor.org/wp-content/uploads/2022/12/Sampling-Methods-for-Political-Polling-508.pdf) - every person in the population has an equal chance of being polled.

Session based evals look more like probability based sampling. Every user interaction has an equal probability of being sampled into evaluation. Query based evals look lumpier - like getting a view of specific targeted cities, then trying to work back to the overall population. Not impossible, but another source of error.

### Advantage 2 - time-sensitive ranking features (ie in learning to rank)

Another advantage comes when we used this evaluation data as training data.

In a query-based eval set, we aggregate user sessions over a lengthy period of time. Maybe a month of user interactions. That gives our per-query labels more confidence.

However, the major downside comes in WHY users might click result - some condition that was only true that specific day they clicked the result. In e-commerce, for example, pricing can be dynamic. Some hour there may be a very specific reason the result appears ‘relevant’ - its temporarily on sale!

When we train a reranking model, the evaluation data we’re discussing becomes training data. With learning to rank, we learn why users prefer some results from the features (bm25 scores, embedding similarities, document popularity, product price, etc).

So when aggregating a months worth of query clicks into a label, we must also try to represent what features describe the query / document over that whole month. Averaging, for example, price would hide the reason one item got a tremendous amount of clicks over a short period of time. We can’t train the model to learn that sudden price drops cause more clicks.

With session based evals, however, our training examples come from a single point in time. We can capture what was true at that moment (price, etc). That makes a big difference in learning these patterns.

### Disadvantage (or question?) - we still have biases

It’s important to note that clickstream biases DO NOT go away in session based evaluation. A click far down the search results page would, all things being equal, be rather surprising. If we saw that item clicked frequently farther. down, we might consider rewarding it more than an item clicked close to the top. And nothing here solves the echo-chamber effect we call [presentation bias](https://softwaredoug.com/blog/2022/07/16/what-is-presentation-bias-in-search).

We likely need to construct a weight to each position directly. For example, computing expected clicks per position, then computing a neutral “probability of click at position” as a kind of prior. Our session might actually be then a set of labels that move labels more negative when they’re not clicked per position, and much higher when they do receive clicks. That might help us debias the data somewhat in a principled way.

In effect, we don’t end up counting every click as a 1. We count every click as some weight according to what position we observed it in (farther down, higher clicks).

### Disadvantage 2 - debugging individual queries

Another challenge comes when trying to get to the bottom of a single query.

Return to our polling example. If we first polled many cities (Chingoteague VA, New York City,) then tried to aggregate to a whole, it might add a lot of noise to the picture of the entire electorate. However, it clearly would give us the advantage of understanding those specific cities. That’s the advantage of query-based evaluation: a debuggable per-query picture.

We could NOT for example, understand New York City just because our sample of 1000 voters happened to sample one NYC resident. In the same way, our sample of a query might just luck out on a single session of a popular query (ie `rambo` above).

In a sense, session based evaluation tries to use historical data to recreate an A/B test. Just like an A/B test, a single query may be too noisy to evaluate. Intentionally selecting for a population of queries, however, lets us get a deeper picture into patterns where search goes wrong.

## Final thoughts -porque no los dos?

It’s worth noting that both solutions share another important bias - they try to use past data. Tomorrow, users may wake up, and decide other factors might be important to them. Some world event may suddenly drive interest in energy efficiency, for example.

That said, both systems derive from a set of sessions, and give you a different picture. Don’t treat either as obvious “truth” - just useful models. Reconstruct query-level evaluation when you want to debug (knowing you sacrifice time-sensitive features). Sample sessions when you want to approach a “simulated A/B test” - noting you’re sacrificing per-query debugability.

Like everything else, no model is accurate, some are useful.

-Doug

***PS - hope to see everyone this week at Leonie Monigatti’s talk on*** [***Context Engineering+Agentic Search***](https://maven.com/p/1c532b/agentic-search-for-context-engineering)***and my chat with*** [***Brian Pedersen on search+tech career FAQs***](https://maven.com/p/38ec62/your-tech-career-in-the-ai-age-q-a-w-a-recruiter)​

… and next [Cheat at Search cohort Pricing goes up in 7 days](http://maven.com/softwaredoug/cheat-at-search)​

​

*This is part of Doug’s Daily Search tips - [subscribe here](http://softwaredoug.kit.com)*

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---