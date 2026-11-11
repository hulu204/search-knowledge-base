---
title: 'MAXSCORE & block-max MAXSCORE: More skipping with block-max MAXSCORE'
company: Elastic
tag: 召回
date: 2023-12-06
url: https://www.elastic.co/search-labs/blog/more-skipping-with-bm-maxscore
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# MAXSCORE & block-max MAXSCORE: More skipping with block-max MAXSCORE

Learn about MAXSCORE, block-max MAXSCORE & WAND. Improve the MAXSCORE algorithm to evaluate disjunctive queries more like a conjunctive query.

December 06, 2023

[Adrien Grand](/search-labs/author/adrien-grand)

[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

## Introduction to WAND and MAXSCORE

How do you quickly identify the top-k matches of a disjunctive query using an inverted index? This is the problem that the WAND[1](#user-content-fn-1) and MAXSCORE[2](#user-content-fn-2) algorithms try to solve. These two algorithms are based on the same idea: taking advantage of the maximum impact score (the maximum contribution of a particular term to the overall score) for each term, so as to skip hits whose score cannot possibly compare greater than the score of the current k-th top hit (referred to as "minimum competitive score" below). For instance, if you are searching for hits that contain `the` or `fox`, and `the` has a maximum contribution of 0.2 to the score while the minimum competitive score is 0.5, then there is no point in evaluating hits that only contain `the` anymore, as they have no chance of making it to the top hits.

However, WAND and MAXSCORE come with different performance characteristics: WAND typically evaluates fewer hits than MAXSCORE but with a higher per-hit overhead. This makes MAXSCORE generally perform better on high k values or with many terms - when skipping hits is hard, and WAND perform better otherwise.

## Block-max MAXSCORE & MAXSCORE in Lucene

While [Lucene first implemented a variant of WAND called block-max WAND](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand), it later got attracted to the lower overhead of MAXSCORE and started using block-max MAXSCORE for top-level disjunctions in July 2022 (annotation [EN](https://home.apache.org/~mikemccand/lucenebench/OrHighMed.html) in Lucene's nightly benchmarks). The MAXSCORE algorithm is rather simple: it sorts terms by increasing maximum impact score and partitions them into two groups: essential terms and non-essential terms. Non-essential terms are terms with low maximum impact scores whose sum of maximum scores is less than the minimum competitive score. Essential terms are all other terms. Essential terms are used to find candidate matches while non-essential terms are only used to compute the score of a candidate.

## MAXSCORE usage example

Let's take an example: you are searching for `the quick fox`, and the maximum impact scores of each term are respectively 0.2 for `the`, 0.5 for `quick` and 1 for `fox`. As you start collecting hits, the minimum competitive score is 0, so all terms are essential and no terms are non-essential. Then at some point, the minimum competitive score reaches e.g. 0.3, meaning that a hit that only contains `the` has no chance of making it to the top-k hits. `the` moves from the set of essential terms to the set of non-essential terms, and the query effectively runs as `(the) +(quick fox)`. The `+` sign here is used to express that a query clause is required, such as in [Lucene's classic query parser](https://lucene.apache.org/core/9_8_0/queryparser/org/apache/lucene/queryparser/classic/QueryParser.html). Said another way, from that point on, the query will only match hits that contain `quick` or `fox` and will only use `the` to compute the final score. The below table summarizes cases that MAXSCORE considers:

| Minimum competitive score interval | Query runs as |
| --- | --- |
| [0, 0.2] | +(the quick fox) |
| (0.2, 0.7] | (the) +(quick fox) |
| (0.7, 1.7] | (the quick) +(fox) |
| (1.7, +Infty) | No more matches |

The last case happens when the minimum competitive score is greater than the sum of all maximum impact scores across all terms. It typically never happens with regular MAXSCORE, but may happen on some blocks with block-max MAXSCORE.

## Improving MAXSCORE to intersect terms

Something that WAND does better than MAXSCORE is to progressively evaluate queries less and less as a disjunction and more and more as a conjunction as the minimum competitive score increases, which yields more skipping. This raised the question of whether MAXSCORE can be improved to also intersect terms? The answer is yes: for instance if the minimum competitive score is 1.3, then a hit cannot be competitive if it doesn't match both `quick` and `fox`. So we modified our block-max MAXSCORE implementation to consider the following cases instead:

| Minimum competitive score interval | Query runs as |
| --- | --- |
| [0, 0.2] | +(the quick fox) |
| (0.2, 0.7] | (the) +(quick fox) |
| (0.7, 1.2] | (the quick) +(fox) |
| (1.2, 1.5] | (the) +quick +fox |
| (1.5, 1.7] | +the +quick +fox |
| (1.7, +Infty) | No more matches |

Now the interesting question is whether these new cases we added are likely to occur or not? The answer depends on how good your score upper bounds are, your actual k value, whether terms actually have matches in common, etc., but it seems to kick in especially often in practice on queries that either have two terms, or that combine two high-scoring terms and zero or more low-scoring terms (e.g. stop words), such as the query we looked at in the above example. This is expected to cover a sizable number of queries in many query logs.

Implementing this [optimization](https://github.com/apache/lucene/pull/12589) yielded a noticeable improvement on Lucene's nightly benchmarks (annotation FU), see [OrHighHigh](https://home.apache.org/~mikemccand/lucenebench/OrHighHigh.html) (11% speedup) and [OrHighMed](https://home.apache.org/~mikemccand/lucenebench/OrHighMed.html) (6% speedup). It was released in Lucene 9.9 and should be included in Elasticsearch 8.12. We hope you'll enjoy the speedups!

## Footnotes

1. Broder, A. Z., Carmel, D., Herscovici, M., Soffer, A., & Zien, J. (2003, November). Efficient query evaluation using a two-level retrieval process. In Proceedings of the twelfth international conference on Information and knowledge management (pp. 426-434). [↩](#user-content-fnref-1)

1. Turtle, H., & Flood, J. (1995). Query evaluation: strategies and optimizations. Information Processing & Management, 31(6), 831-850. [↩](#user-content-fnref-2)

### Frequently Asked Questions

#### How does the MAXSCORE algorithm work?

MAXSCORE sorts terms by increasing maximum impact score and partitions them into two groups: essential terms and non-essential terms. Non-essential terms are terms with low maximum impact scores whose sum of maximum scores is less than the minimum competitive score. Essential terms are all other terms. Essential terms are used to find candidate matches while non-essential terms are only used to compute the score of a candidate.

#### How do block-max MAXSCORE performance characteristics compare to WAND?

WAND typically evaluates fewer hits than MAXSCORE but with a higher per-hit overhead. This makes MAXSCORE generally perform better on high k values or with many terms - when skipping hits is hard, and WAND performs better otherwise."

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