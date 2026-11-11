---
title: 'How We Built a Web-Scale Vector Database for Our Neural Network Search Engine'
company: Exa
tag: 索引构建
date: 2024-12-17
url: https://exa.ai/blog/building-web-scale-vector-db
account: 
origin: harvest2-202607
---
Exa is a modern AI search engine with SERP API, website crawler tools, and deep research API. Power your app with web search AI and web crawling API.![](https://px.ads.linkedin.com/collect/?pid=9254756&fmt=gif)

[Introducing Exa Connect](https://exa.ai/connect)[Introducing Exa Connect: Access leading data providers.](https://exa.ai/connect)[Learn more](https://exa.ai/connect)

Products

[Search](/products/search)[Contents](https://exa.ai/docs/reference/contents-api-guide)[Deep](/products/deep)[Agent](/products/agent)[Monitors](https://exa.ai/docs/reference/monitors-api-guide)[Exa Connect](/connect)

Resources

[CareersWe're hiring](/careers)[Customers](/customers)[Partners](/partners)[Demos](/demos)[Contact us](/contact)[Research](/research)[Brand](/brand)

[Pricing](/pricing)

[Blog](/blog)

[Docs](https://exa.ai/docs)

[About](/about)

[Contact sales](/contact/sales)[Sign up](https://dashboard.exa.ai)

# How we built a web-scale vector database

![How we built a web-scale vector database](https://exa.imgix.net/vector-db-blog/Group%2039.png)

[![The Exa Team](https://exa.imgix.net/logo_cream.png)](https://x.com/ExaAILabs)

[The Exa Team](https://x.com/ExaAILabs)

Dec 17, 2024

### The problem

At Exa, we're redesigning web search from scratch to handle complex queries that Google can't. To do that, we needed to build our own web-scale vector database.

In this blog post, we'll describe in detail how that vector database works—from high-level algorithms, to low-level optimizations that we haven't seen in existing literature.

The end result is a database that can search billions of vectors in under 100ms with high recall, all while enabling keyword + metadata filters and using less memory than a gaming PC.

### The Challenge

Exa needs to handle complex semantic queries like "AI startups in the Bay Area building hardware" and return a list of companies that exactly match that criteria.

To capture the semantic meaning of a document, we convert the document into a **vector** (aka an **embedding**). Documents with similar meanings become embeddings with similar numerical values.

![Diagram of how text is converted into an embedding](https://exa.imgix.net/vector-db-blog-embedding-diagram/embedding%20diagram.png)

To search through the documents, we **convert the user's query into an embedding**, compare it against the embeddings of all the web documents we've indexed, and return the closest matches.

So, we need to store all our document embeddings in a way that's memory-efficient and enables fast search, without losing precision.

#### Our Engineering Requirements

1. Search billions of vectors, each of which consists of 4096 floating-point numbers.
2. Handle metadata filtering efficiently — e.g., only return documents between 2022 and 2023, or from reddit.com and youtube.com
3. Return search results in under 100 ms.
4. Handle >500 queries per second at reasonable cost.

### Exa's approach

We combined **five optimizations** to significantly improve memory usage and speed.

#### Optimization 1: Approximate the embedding

Turns out, you can take any of these 4096-dimensional embeddings, chop off everything except the first 256 elements, and retain much of its meaning.

How? We trained our embeddings model—i.e., the algorithm that transforms raw web pages into their vector representations—using Matryoshka.[[1]](#footnote-1)

Matryoshka is a technique that **forces prefixes of embeddings to be approximations of the whole embedding.** Meaning: the first 2048 dimensions are a good embedding, the first 1024 dimensions are also a good embedding, etc— down to, say, the first 32 dimensions.

We cut our vectors to 256 dimensions, which **reduced memory usage by 20x.**

#### Optimization 2: Compress each dimension

Now each embedding comprises 256 floating-point numbers, but that's still too slow to fully search through.

How can we speed it up?

Well, each of these floats occupies 16 bits of space. We used **binary quantization** to replace the 16-bit floats with 1-bit values. For each float in the vector: if it's greater than 0, set it to 1; else, set it to -1.

This cut our memory usage another 16 times!

![Diagram describing binary quantization](https://exa.imgix.net/vector-db-blog/bin%20quant%20diagram.png)

#### Optimization 3: Dot-product optimization

The standard search method for binary-quantized embeddings is to compute the Hamming distance (i.e. number of elements that are different) from the binary-quantized query embedding to each binary document vector.

But this was lossy and inefficient. So we developed a novel hybrid approach: Keep using binary document embeddings—but **for the query embedding, use uncompressed floating-points**.

Then use **dot product as a similarity metric** between the query vector and each of the binary-quantized document vectors. (Imagine two vectors in geometric space—the dot product measures the angle between them. A large dot product means the vectors are pointing in the same direction and thus very similar.)

We hyper-optimized our dot product calculations with a strange but effective method:

* You can compute the dot product of two vectors by dividing them into smaller subvectors (e.g., of length 4), calculating the dot products of corresponding subvectors, and summing the results.
* Remember: each value in the document vector is either -1 or 1. So any length-4 subvector of a document vector can only have one of 16 possible values. For each length-4 subvector of the query vector, we **precompute all 16 possible dot products that it could have with any document subvector, and store those in a lookup table.**
* To compute a query-document dot product, we break the document into subvectors, look up each subvector's dot product in the table, and sum them.

This cuts down the number of computations by 1/4.[[2]](#footnote-2)

![Example of a lookup table](https://exa.imgix.net/vector-db-blog/lookup%20table%20diagram.png)

An example lookup table for a query subvector [a, b, c, d]. We compute its dot products with all 16 possible binary-quantized document subvectors.

#### Optimization 4: Max out the hardware

We further optimized lookup times by loading the entire lookup table into CPU registers. This enables much faster lookups than keeping it in RAM.[[3]](#footnote-3)

#### Optimization 5: Don't search through everything

Thus far, we've still been looking through every document embedding on every search. Clustering fixes that.

We divided our documents into 100,000 clusters, each grouped by similarity. When we search, we figure out which cluster our query embedding belongs in, and only search through that cluster and nearby ones.

With clustering, we can get a roughly 1000x improvement in throughput without much accuracy degradation 🤯.

![Simple example of k-means clustering](https://exa.imgix.net/vector-db-blog/2D_Kmeans_Clustering_Blue_Cluster_new.png)

A simple visualization showing what clustered vectors look like in 2D space. (Our actual embeddings are 256-dimensional.)

### Final touches

#### Recovering recall

You might wonder—haven't we just cut out a lot of information by truncating and squashing the vectors so aggressively?

Yes, these optimizations are lossy. But nothing some reranking can't fix. After the initial search, we fetch extra results and rerank them with the uncompressed data.

#### Filtering

We deliberately designed the vector database to allow for complex filters, like filtering by date range, domain, or keyword. Basically we want our vector database to act like a database!

Unlike graph-based methods like HNSW, our clustering compressed methods fit nicely with filters. For each filterable value (category, date, etc), we create inverted indexes. These are hashmaps from the filterable value to a list of document IDs that match the filter. If the user specifies a filter, then we only run our search algorithm over the documents that match the filter in the inverted index.

### Final system

1. We cut costs 10x compared to quotes from cloud vector database services.
2. We can shard our data more easily (e.g. by cluster) than HNSW (whose global graph structure can't be partitioned easily).
3. We can add filters for our data more efficiently.
4. We can build fun custom solutions on top of it. E.g. We built our own query language that allows us to easily define different multi-stage pipelines for different scoring algorithms.

This is only the beginning. Turns out a standard vector database is not enough for perfect web search. More coming there :)

P.S. If this post left you hungry for more, [come help us fix web search](https://exa.ai/careers).

---

[[1]](#ref-1) Matryoshka embeddings are named after Russian [Matryoshka dolls](https://en.wikipedia.org/wiki/Matryoshka_doll), which nest inside each other. These embeddings contain nested representations of increasing dimensionality; each smaller slice of the embedding retains a meaningful representation of the original data.

  

[[2]](#ref-2) Or by 1/m, where m is the subvector length you've chosen. We mostly use subvectors of length 4 or 8.

  

[[3]](#ref-3) Fun fact: For optimal performance, we specifically had to write this part of the code in C++ instead of Rust 🫠

---

#### Cheers,

#### [The Exa Team](https://x.com/ExaAILabs)

SEE MORE

[![SOTA Search Over Academic Publications](/images/blog/publications-benchmark.png)

#### SOTA Search Over Academic Publications

The Exa Team

July 23, 2026](/blog/publications-search)[![Introducing Exa Agent](/images/blog/exa-agent-card.jpg)

#### Introducing Exa Agent

The Exa Team

June 16, 2026](/blog/exa-agent)[![Exa raises $250M Series C to build the search engine for AIs](https://exa.imgix.net/team1.avif?w=800&q=60&auto=format%2Ccompress&fit=max)

#### Exa raises $250M Series C to build the search engine for AIs

Will Bryk

May 20, 2026](/blog/announcing-series-c)