---
title: 'Real life NDCG notebook'
company: softwaredoug
tag: 评测
date: 2024-10-19
url: https://softwaredoug.com/blog/2024/10/19/real-life-ndcg
account: 
origin: harvest3-202607
---
As I’m sure you’re aware [NDCG](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) is a statistic used to measure the relevance of a search algorithm. It compares the returned results to a set of labels, aka a [judgment list](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list). These judgments might be explicit – a human being went through and labeled them – or they might be implicit – gathered from clickstream data. Or they might be LLM generated.

In any case, when compared against the returned search results, we can put a number on the relevance.

I’ve argued, of course, this whole [NDCG way of evaluating search is overrated](https://softwaredoug.com/blog/2023/05/06/ndcg-is-overrated) in real-life circumstances. Yet it’s still useful 😎.

And, by God, I’m exhausted from writing this same, boilerplate, code over-and-over-and-over again at very job I go to.

So here’s [a useful notebook](https://colab.research.google.com/drive/16dHv1sPeWFNHsZZ9bEQRUJnMKNANQVy-?usp=sharing) to walk you through the major decisions of NDCG calculation that matter to real-life search evaluation.

Enjoy!

[![](/assets/media/2024/real-life-ndcg.png)</img>](https://colab.research.google.com/drive/16dHv1sPeWFNHsZZ9bEQRUJnMKNANQVy-?usp=sharing)

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---