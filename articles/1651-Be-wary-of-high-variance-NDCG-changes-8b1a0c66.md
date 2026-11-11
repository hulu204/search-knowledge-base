---
title: 'Be wary of high variance NDCG changes'
company: softwaredoug
tag: 评测
date: 2025-06-07
url: https://softwaredoug.com/blog/2025/06/07/high-variance-ndcg
account: 
origin: harvest3-202607
---
Which looks like a better change, this NDCG bump of 0.005 on baseline?

```
In [1]: ndcgs(baseline).mean(), ndcgs(graded_syns).mean()
Out[1]: (np.float64(0.5411098691836396), np.float64(0.5461684655797919))
```

Or the NDCG bump of 0.01 on top of baseline?

```
In [1]: ndcgs(baseline).mean(), ndcgs(graded_syns).mean()
Out[1]: (np.float64(0.5411098691836396), np.float64(0.5514965226030798))
```

The second LOOKS better. But if you dig into the queries that changed, you see a different story.

The first, modest change shows these per-query deltas:

![Small NDCG change](/assets/media/2025/ndcg_notrisky.png)

The bigger NDCG bump experiment shows these changes

![Small NDCG change](/assets/media/2025/ndcg_risky.png)

In the first change, 86 queries changed, with one query with a significant negative impact. In the second, many, many queries were impacted. Some very positively, but concerningly: some very negatively.

Shipping the second change carries tremendous risk, you can easily tank the experience of some of your users on the margins. Odds are your boss WILL do the searches on the negative tail end!

The first change carries less risk and is more targeted change. The one downside perhaps could be investigated and managed.

It’s not enough to “improve NDCG” when we tune search, we need to look at the margins and ensure we don’t tank the p90 experience.

I’d take it a step further, which such a large variance, it we’re using sledgehammer when we should use precise scalpal.

In this experiment, I’m using an LLM to generate synonyms for e-commerce data. In one case I’m being conservative, only boosting full synonym phrases, biasing towards precision (ie `cushioned sofa` -> boost occurences of the phrase `padded sofa`). In the other case, I’m just naively using a “bag of words” approach - taking every individual term, ie `[cushioned]` and `[sofa]` in isolation and adding those matches to the results.

The implications of the precise phrase boost can be better understood and managed. On the other hand, spamming search with a bag of words synonym matches just leads to chaos as padded seat cushions creep up in the results as high as padded couches.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---