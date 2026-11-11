---
title: 'What is psuedo-relevance feedback?'
company: softwaredoug
tag: 查询理解
date: 2026-04-13
url: https://softwaredoug.com/blog/2026/04/13/what-is-psuedo-relevance-feedback
account: 
origin: harvest3-202607
---
After retrieving BM25 (or any) ranked search results, you might not realize it, but you have new information about the query - **the search results themselves**!

One early discovery in Information Retrieval:

1. Compare what’s in the foreground (the initial top N results)
2. … to the background corpus
3. Then use that to improve the original query

How, *exactly*, becomes a series of design decisions. You could take any number of approaches:

* Take the embeddings of the top N results, use that to expand recall (as in Daniel Tunkelang’s [Bag of Documents approach](https://dtunkelang.medium.com/bags-of-queries-as-sparse-document-representations-bc450db3e814))
* Find terms that occur more frequently in the foreground, use those in search (as in Semantic Knowledge Graph, written about in [AI Powered Search](https://aipoweredsearch.com/) by Grainger et. al)

For example, from this [semantic knowledge graph notebook](https://colab.research.google.com/drive/14pDxjXD08vGgpY7mQdc0sQN3T7D_wpyv), we retrieve some initial results for a “dining room table” query

​

![](/assets/media/daily-search-tips/23675067/ab81da42431b22631c1930c77e693c0f.png)

​

We then use those to score the most anomalous terms in the product description field:

![](/assets/media/daily-search-tips/23675067/a1bfbd0c9cf82ad4e26b7862ed3fff4e.png)

​

Would these be useful queryexpansions? Above, we see the promise, and the challenges, of the approach:

* 👍 - **the positive**: related terms like placemat, tableware, tablecloth, etc
* 👎 - **the negative:** spurious terms like ‘ten’ likely occurs in dining room descriptions “seats ten” - but is this term really related to dining room tables?

I chose the messiest field on purpose. A cleaner field like ‘title’ produces better candidate expansions:

![](/assets/media/daily-search-tips/23675067/23728254a8d04538caf4dcf42836c4d0.png)

​

If we’re so vulnerable to data quality, can this work?

Yes it can work. But only after good corpus hygiene. It’s another example of [content understanding IS query understanding](https://softwaredoug.com/blog/2026/03/18/content-understanding-is-query-understanding)**.** There’s no free lunch. Clean, well organized content helps every layer of search quality, not just blind relevance feedback. We can then pick and choose which fields to use based on the information they convey.

There are other decisions. For example, should you weigh the foreground docs by relevance? Not all docs in the first pass are created equal after all. Or how do you handle thresholds? Should you only accept terms that occurred only a few times? Should you treat the background as a prior somehow and “move off” the background as evidence accumulates?

Take a look at [my notebook](https://colab.research.google.com/drive/14pDxjXD08vGgpY7mQdc0sQN3T7D_wpyv#scrollTo=dS83XQgNbOF9). What ideas do you have to improve the relevance feedback?

-Doug

​

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