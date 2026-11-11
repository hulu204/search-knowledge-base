---
title: 'Vector Search for the Uninitiated'
company: softwaredoug
tag: 召回
date: 2023-02-13
url: https://softwaredoug.com/blog/2023/02/13/why-vector-search
account: 
origin: harvest3-202607
---
There’s sudden excitement vector search. What is it, and why is it suddenly talked about so much? If you’re new to search, and want some context, let me try to ELI5 :)

Traditional search systems, like I write about in [Relevant Search](https://www.manning.com/books/relevant-search), work much like a book index. You map terms to a list of document ids that have that mention that term (document here just means whatever’s being searched - product, job, webpage, etc).

This index can be visualized like so:

```
[word] -> ids
```

So consider this example:

```
[dog] -> 1,2,3
[cat] -> 3
```

If you search for `dog cat` then the most relevant doc would be 3. Docs 2 and 1 just mention dog and aren’t as relevant for a search for both terms.

Out of the box, the matching here is very exact. Still, we have many tricks to make these indexes yield more ‘semantic’ results (ie increase recall). Search engines [stem words](https://en.wikipedia.org/wiki/Stemming) to match different word forms (treat `doggie` the same as `dog`). Teams also curate synonyms like `canine == dog`. Techniques exist to expand queries to less precise, lower priority meanings of a term `dog`  but also, but lower ranked, `puppy, wolf, …` . The list goes on…

## On to vector search

Imagine instead of an index, you bucketed your content into one of 3 arbitrary categories.

To give names to these 3 categories, I’ll say:

* animals / not animals
* law enforcement / not law enforcement, and
* cuddly / not cuddly.

A silly post on [/r/aww](http://reddit.com/r/aww) about cats would be 75% about animals, 0% law enforcement, and 25% cuddliness. A news article about an alligator biting an FBI agent would be 50% animal, 50% law enforcement, 0% cuddliness and so on…

Already you might see we could find similar content just using these categories.

For example, you can know / [learn](https://bytes.grubhub.com/search-query-embeddings-using-query2vec-f5931df27d79?gi=3f58aea0c201) [the categories](https://en.wikipedia.org/wiki/Rocchio_algorithm) of search queries too. You might know that a query for `baby alligator chases sheriff` is 60% about animals, 35% law-enforcement, 5% cuddliness (it is a baby after all…)

So instead of categories, we say dimensions, and we have 3 dimensions. We can put each % into a bucket like

```
[60, 35, 5 ]
```

We call this a vector.

We can find loosely similar things to our `baby alligator…` query - animal things, not that cuddly, but involving police. Items that might be relevant, despite not mentioning the precise terms:

```
Police capture tiny crocodile - [55, 40, 5]
```

As you can imagine, maybe you forgot that it was actually a crocodile, or that it was police and not the Sheriff’s dept. So this might actually be what you were looking for!

Unfortunately, this system doesn’t have a lot of dimensions, so lots of irrelevant things to our query could also be similar in animalness / cuddliness / law-enforcement-ness. Like:

```
Prize Turkey escapes Fraternal Order of Police Feast - [50, 40, 10]
```

And lack of precision is the achiles heel of vectors.

This is vector search. It comes at search from the opposite direction, loose categories of stuff, not exactly what was searched for. Sometimes more “semantic”. But with too few dimensions, very imprecise, and often more discovery / serendipity oriented.

We would say vector search maximizes **recall** at the risk of precision. But traditional search maximizes **precision** at the risk of decreasing recall.

## Embeddings

There’s one slight tweak to this definition. We don’t usually have explicit ‘categories’ like cuddliness, etc. Instead models create these vectors - called embeddings - by trying to move ‘similar’ things together (and pushing dissimilar things apart).

A model (like GPT, BERT, word2vec, etc) has some definition of what it means to be similar - depending on the model - and the job of the algorithm is to essentially [jiggle around the dimensions](https://kazimuth.github.io/blog/post/shake-and-pull-gently/) until they get close to that definition of similarity.

What you might observe - similar things that share similar words / features are forced to be more similar (by tweaking a random dimensions closer). Harry Potter and Star Wars might be clumped together because they share fantasy words. Some Star Wars might get clumped together with Star Trek due to space themes.

Regardless, embedding vectors are still imprecise representations of a much bigger space. In a way they’re a way of compressing of the traditional search system. Like forcing a 10 x 10 segment of pixels (100 RGB values) into a single averaged RGB pixel.

## Why vector search now?

What explains the sudden buzz around vector search and vector databases like [Pinecone](http://www.pinecone.io), Weaviate, Milvus, Vectara, etc etc?

After all, these types of ideas have been around search and NLP for a long time actually. Check out [Latent Semantic Indexing](https://www.youtube.com/watch?v=RR4s8VLjfwc) for one such example. We’ve had a kind of search from both angles for a while, though the former always was much more mature in its ability to serve results in real time in production. And it seemed to serve the use cases better

Here’s what’s different:

* Previously there were not great data structures for finding similar vectors for high values of N (where N is > 100) at scale. In the past 3-4 years this has been a focus of data structures research. This made the second kind of search more viable. Hence the explosion of vector database vendors and addition of vector search to Elasticsearch, etc
* New, more accurate transformer based embedding models (BERT, GPT, etc) mean there’s far more value is using the embedding vectors in search
* Generally these vectors are prebuilt now and more widely available to be downloaded and played with. Before you’d have to build your own from a Wikipedia dump or your own corpus
* Consumers want to use search for LOTS of natural language interactions. Question answering and maybe soon prompt engineering type use cases like in [Bing+ChatGPT](https://www.theverge.com/2023/2/7/23589587/microsoft-chatgpt-bing-ai-event-preview)? No longer just 10 ranked search results on a page.
* Other applications represent things as vectors (recommendations might represent a user as a vector adding together the vectors of everything they clicked, or images as a vector, etc). So these new vector databases have use cases far beyond “search”.
* Many applications care more about recall and serendipity (think of your social feed, or scrolling tiktok) rather than just exact matches and answers
* We can use our own training data to do transfer learning - take a general precomputed vector like BERT - and just tweak the similarity to make our searches more precise based on what people click, etc (treating the click as if it’s expressing some similarity between content and query)

So there’s a confluence of market and technical forces converging.

## BUT

Of course nobody gives the conference talk about the mundane tools from yesterday that still work. What seems to work best if “hybrid search” combining the strengths of both systems into one. Vector search vendors recently have focused on [backporting traditional search into their systems](https://www.pinecone.io/learn/hybrid-search-intro/).

You sometimes want exactly what you typed. Moreover, many teams want to very precisely manage search with very exact synonyms or knowledge graphs (purple for me is a BRAND of MATTRESS not a color). Or make some offensive thing not come up for a certain search term.

Since search is a very intentional interaction, screwing it up comes at high costs. People notice when search gives imprecise results. They’re mad. It’s like customer service not listening to them. They leave with a negative perception of the brand, and go back to Google (or Bing+ChatGPT :) ).

So, to be honest, the future is still being defined. There’s no one pattern that solves search. Instead there’s a hodgepodge of solutions depending on the type of search system and query. Usually some combination of:

* For head queries (ie the most popular ones), knowing the exact results for the query just from clickstream data may be possible
* For torso queries, a model needs to be trained to optimize relevance as there’s usually not direct clickstream data for this query to optimize relevance
* For informational searches (question answering, etc) vector search may offer a good solution
* For product searches, a set of factors, many (most?) independent of the query might mean a [traditional LTR model would work best](https://arxiv.org/abs/2207.08815)
* For exact item lookups, like the name of a person or document, a straight-forward traditional search system might work best

With these there’s some combination of traditional ranking factors and vector search that works best. But the future is interesting, and very much still being defined.

Of course, be sure to take [ML Powered Search](https://www.getsphere.com/cohorts/machine-learning-powered-search) if you’d like to know more.

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---