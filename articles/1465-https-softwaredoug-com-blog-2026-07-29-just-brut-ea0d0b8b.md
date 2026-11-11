---
title: 'https://softwaredoug.com/blog/2026/07/29/just-brute-force-embeddings.html'
company: softwaredoug
tag: 召回
date: 
url: https://softwaredoug.com/blog/2026/07/29/just-brute-force-embeddings.html
account: 
origin: en-rss
---
When I wrote embedded C code in the 2000s we latched onto something [Raymond Chen, wrote in passing](https://devblogs.microsoft.com/oldnewthing/20050622-49/?p=35223)

> My O(n) algorithm can run circles around your O(log n) algorithm; why much of what you learned in school simply doesn’t matter

True of a sorting algorithm. True of vector search.

People think they need a vector database. But often they have like 1m docs to search. Numpy can brute-force an array of float32s very fast:

| Index Size | Client Threads | QPS | Avg Latency |
| --- | --- | --- | --- |
| 1000000 | 1 | 79.7 | 0.012s |
| 1000000 | 10 | 170.5 | 0.058s |
| 8841823 | 1 | 9.34 | 0.106s |
| 8841823 | 10 | 18.34 | 0.106s |

This is literally just this line of Python code, on 384 dim embeddings, running on my M4 MBP.

```
# Dot product against all
scores = self.doc_vectors @ query_vector.astype(np.float32, copy=False)
```

I work with a lot of teams that don’t need the complexity of a vector database. They have ~1m documents to search. They have low query traffic, and write their embeddings all up front. They don’t need to buy a multi-million dollar vector database, or spend 6 months learning to operate it.

For low enough n, just brute force the embeddings until you can’t bear to. As fellow search traveler Jo Kristian Bergum says [“an exhaustive search may be all you need”](https://bergum.medium.com/four-mistakes-when-introducing-embeddings-and-vector-search-d39478a568c5).

A little past that, maybe think about a database? Or heck, just load them all in memory in FAISS or something and call it done.

---

As a footnote, this is just naive numpy operations, it could probably be faster. As [Andreas Erickson says](https://x.com/andreer/status/2082531919233761580), throughput can be improved here by giving threads more than one query during the scan). And we could be doing a lot more during the search to collect into a top-n heap than what numpy does.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---