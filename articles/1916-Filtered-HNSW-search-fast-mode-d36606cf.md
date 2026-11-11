---
title: 'Filtered HNSW search, fast mode'
company: Elastic
tag: 召回
date: 2025-02-27
url: https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Filtered HNSW search, fast mode

Explore the improvements we have made for HNSW vector search in Apache Lucene through our ACORN-1 algorithm implementation.

February 27, 2025

[Benjamin Trent](/search-labs/author/benjamin-trent)

[Lucene](/search-labs/blog/category/lucene)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

For years, Apache Lucene and Elasticsearch have supported filtered search with kNN queries, allowing users to retrieve the nearest neighbors that meet a specified metadata filter. However, performance has always suffered when dealing with semi-restrictive filters. In Apache Lucene, we are introducing a variation of [ACORN-1](https://arxiv.org/abs/2403.04871)—a new approach for filtered kNN search that achieves up to 5x faster searches with little drop in recall.

This blog goes over the challenges of filtered HNSW search, explaining why performance slows as filtering increases, and how we improved HNSW vector search in Apache Lucene with the ACORN-1 algorithm.

## Why searching fewer docs is actually slower in HNSW

Counterintuitively, filtering documents—thereby reducing the number of candidates—can actually make kNN searches slower. For traditional lexical search, fewer documents mean fewer scoring operations, meaning faster search. However, in an HNSW graph, the primary cost is the number of **vector comparisons** needed to identify the k nearest neighbors. At certain filter set sizes, the number of vector comparisons can increase significantly, slowing down search performance.

![unfiltered HNSW search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt32f0833edfd345e1/6a17e6be7b54f9e6978b38cc/50a4df4d192e338faa97778dd2876eaa707e0d47-898x910.gif)

Here is an example of unfiltered graph search. Note there are about 6 vector operations.

Because the HNSW graph in Apache Lucene has no knowledge of filtering criteria when built, it constructs purely based on vector similarity. When applying a filter to retrieve the k nearest neighbors, the search process traverses more of the graph. This happens because the natural nearest neighbors within a local graph neighborhood may be **filtered out**, requiring deeper exploration and increasing the number of vector comparisons.

![Filtered HNSW graph search example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc4957beaf1dd1551/6a17e6c0abe0f255c2dfe9cd/b4fee31d41449d696034639ba1ab1db88571cfb9-898x910.gif)

Here is an example of the current filtered graph search. The “dashed circles” are vectors that do not match the filter. We even make vector comparisons against the filtered out vectors, resulting in more vector ops, about 9 total.

You may ask, why perform vector comparisons against nodes that don’t match the filter at all? Well, HNSW graphs are already sparsely connected. If we were to consider only matching nodes during exploration, the search process could easily **get stuck**, unable to traverse the graph efficiently.

![Typical HNSW graph](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt824d9b9ab85f1b04/6a17e6c1414c64132c945167/273888eca8867d7d4457fa938f02359c9b7f629f-898x910.png)

Note the filtered “gulf” between the entry point and the first valid filtered set. In a typical graph, it's possible for such a gap to exist, causing exploration to end prematurely and resulting in poor recall.

## We gotta make this faster: Improving HNSW vector search in Lucene

Since the graph doesn’t account for filtering criteria, we have to explore the graph more. Additionally, to avoid getting stuck, we must perform vector comparisons against filtered-out nodes. How can we reduce the number of vector operations without getting stuck? This is the exact problem tackled by [Liana Patel et. al. in their ACORN](https://arxiv.org/abs/2403.04871) paper.

While the paper discusses multiple graph techniques, the specific algorithm we care about with Apache Lucene is their ACORN-1 algorithm. The main idea is that you only explore nodes that satisfy your filter. To compensate for the increased sparsity, ACORN-1 extends the exploration beyond the immediate neighborhood. Now, instead of exploring just the immediate neighbors, each neighbor’s neighbor is also explored. This means that for a graph with 32 connections, instead of only looking at the nearest 32 neighbors, exploration will attempt to find matching neighbors in 32\*32=1024 extended neighborhood.

![ACORN algorithm in action](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2b9dc06a91704490/6a17e6c36864a4e5e2b68783/cc1c537047c9de4d64afabab2e94599cb921c8bc-840x910.gif)

Here you can see the ACORN algorithm in action. Only doing vector comparisons and exploration for valid matching vectors, quickly expanding from the immediate neighborhood. Resulting in much fewer vector ops, about 6 in total.

Within Lucene, we have slightly adapted the ACORN-1 algorithm in the following ways. The extended neighborhoods are only explored if more than 10% of the vectors are filtered out in the immediate neighborhood. Additionally, the extended neighborhood isn’t explored if we have already scored at least `neighborCount * 1.0/(1.0 - neighborFilterRatio)`. This allows the searcher to take advantage of more densely connected neighborhoods where the neighborhood connectedness is highly correlated with the filter.

We also have noticed both in inversely correlated filters (e.g. filters that only match vectors that are far away from the query vector) or exceptionally restrictive filters, only exploring the neighborhood of each neighbor isn’t enough. The searcher will also attempt branching further than the neighbors’ neighbors when no valid vectors passing the filter are found. However, to prevent getting lost in the graph, this additional exploration is bounded.

## Numbers don’t lie

Across multiple real-world datasets, this new filtering approach has delivered **significant speed improvements**. Here is randomly filtering at 0.05% [1M Cohere vectors](https://huggingface.co/datasets/Cohere/wikipedia-2023-11-embed-multilingual-v3):

![1M Cohere vectors](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt97ba7c5081b5821a/6a17e6c46864a4ef22b68787/ff2b570bf3c206a7b1396915227b4ac2f0d47a76-855x470.png)

Up and to the left is “winning”, which shows that the candidate is significantly better. Though, to achieve the same recall, search parameters (e.g. `num_candidates`) need to be adjusted.

To further investigate this reduction in improvement as more vectors pass the filter, we did another test over an [8M Cohere Wiki document data set](https://huggingface.co/datasets/Cohere/wikipedia-22-12-en-embeddings). Generally, no matter the number of vectors filtered, you want higher recall, with fewer visited vectors. A simple way to quantify this is by examining the **recall-to-visited ratio**.

![Filtered search methodology](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd875d4409989f3f9/6a17e6c6505ac38044ad8b05/cafde97a6ffab78f9e6f0d6307164e0ebb50eb0b-1200x742.png)

Here we see how the new filtered search methodology achieves much better recall vs. visited ratio.

It's clear that near 60%, the improvements level off or disappear. Consequently, in Lucene, this new algorithm will only be utilized when 40% or more of the vectors are filtered out.

Even our nightly Lucene benchmarks saw an impressive improvement with this change.

![Apache Lucene runs over 8M 768 document vectors](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltaa0112dca7b132b6/6a17e6c8ec0f8949c35a65f8/78beeb860eb9de7ef80c22931ce904eecdef1ffb-1526x1302.png)

Apache Lucene runs over 8M 768 document vectors with a random filter that allows 5% of the vectors to pass. These kinds of graphs make me happy.

## Gotta go fast

Filtering kNN search over metadata is key for real-world use cases. In Lucene 10.2, we have made it as much as 5x faster, using fewer resources, and keeping high recall. I am so excited about getting this in the hands of our users in a future Elasticsearch v9 release.

### Frequently Asked Questions

#### What is ACORN-1?

ACORN-1 is a new approach for filtered kNN search that achieves up to 5x faster searches with little drop in recall.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt762b38f91bd71c8e/6a170db8b339d547bb76a048/368db71c500e72d20fe225fe44c2c40231e29765-721x420.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Bringing maximum-inner-product into Lucene

September 01, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9ec7a04e3bdbfd9f/6a467b337eb22d59efdfc54d/c07100b6fcc74dba250e6853b1c5ef1edabbedfc-1920x1080.png)

[Lucene](/search-labs/blog/category/lucene)[Index Data](/search-labs/blog/category/index-data)

### How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage

June 12, 2026|[Alan Woodward](/search-labs/author/alan-woodward)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf9fcbf843affc566/6a1706b8964ceaea3208bab9/7884e35f40c15fe349379ef7ae4648b21708962f-1070x712.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Concurrency bugs in Lucene: How to fix optimistic concurrency failures

February 07, 2025|[Benjamin Trent](/search-labs/author/benjamin-trent)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter