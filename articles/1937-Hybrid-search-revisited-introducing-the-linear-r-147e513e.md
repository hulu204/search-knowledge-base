---
title: 'Hybrid search revisited: introducing the linear retriever in Elasticsearch!'
company: Elastic
tag: 召回
date: 2025-05-28
url: https://www.elastic.co/search-labs/blog/linear-retriever-hybrid-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Hybrid search revisited: introducing the linear retriever in Elasticsearch!

Discover how the linear retriever enhances hybrid search by leveraging weighted scores and MinMax normalization for more precise and consistent rankings, and learn how to use it.

May 28, 2025

[Panagiotis Bailis](/search-labs/author/panagiotis-bailis)

[Relevance](/search-labs/blog/category/relevance)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Jump to

Share

In our [previous blog](https://www.elastic.co/search-labs/blog/elasticsearch-retrievers-ga-8.16.0) post we introduced the redesigned-from-scratch retrievers framework, which enables the creation of complex ranking pipelines. We also explored how the Reciprocal Rank Fusion (RRF) retriever enables hybrid search by merging results from different queries. While RRF is easy to implement, it has a notable limitation: it focuses purely on relative ranks, ignoring actual scores. This makes fine-tuning and optimization a challenge.

## Meet the linear retriever!

In this post, we introduce the [`linear`](https://www.elastic.co/docs/solutions/search/retrievers-overview#retrievers-overview-types) [retriever](https://www.elastic.co/docs/solutions/search/retrievers-overview#retrievers-overview-types), our latest addition for supporting hybrid search! Unlike `rrf`, the `linear` retriever calculates a weighted sum across all queries that matched a document. This approach preserves the relative importance of each document within a result set while allowing precise control over each query’s influence on the final score. As a result, it provides a more intuitive and flexible way to fine-tune hybrid search.

Defining a linear retriever where the final score will be computed as:

score=5∗knn+1.5∗bm25score = 5 \* knn + 1.5 \* bm25score=5∗knn+1.5∗bm25

It is as simple as:

```
GET linear_retriever_blog/_search
{
   "retriever": {
       "linear": {
           "retrievers": [
               {
                   "retriever": {
                       "knn": {
                          ...
                        }
                    },
                   "weight": 5
               },
                  {
                   "retriever": {
                       "standard": {
                          ...
                        }
                    },
                   "weight": 1.5
               },

           ]
        }
     }
}
```

Notice how simple and intuitive it is? (and really similar to `rrf`!) This configuration allows you to precisely control how much each query type contributes to the final ranking, unlike `rrf`, which relies solely on relative ranks.

One caveat remains: `knn` scores may be strictly bounded, depending on the similarity metric used. For example, with cosine similarity or the dot product of unit-normalized vectors, scores will always lie within the `[0, 1]` range. In contrast, `bm25` scores are less predictable and have no clearly defined bounds.

## Scaling the scores: kNN vs BM25

One challenge of hybrid search is that different retrievers produce scores on different scales. Consider for example the following scenario:

Query A scores:

|  | doc1 | doc2 | doc3 | doc4 |
| --- | --- | --- | --- | --- |
| knn | 0.347 | 0.35 | 0.348 | 0.346 |
| bm25 | 100 | 1.5 | 1 | 0.5 |

Query B scores:

|  | doc1 | doc2 | doc3 | doc4 |
| --- | --- | --- | --- | --- |
| knn | 0.347 | 0.35 | 0.348 | 0.346 |
| bm25 | 0.63 | 0.01 | 0.3 | 0.4 |

You can see the disparity above: `kNN` scores range between 0 and 1, while `bm25` scores can vary wildly. This difference makes it tricky to set static optimal weights for combining the results.

## Normalization to the rescue: the MinMax normalizer

To address this, we’ve introduced an optional `minmax` normalizer that scales scores, independently for each query, to the `[0, 1]` range using the following formula:

normalizedscore=(score−min)/(max−min)normalized\_score = (score - min) / (max - min)normalizeds​core=(score−min)/(max−min)

This preserves the relative importance of each document within a query’s result set, making it easier to combine scores from different retrievers. With normalization, the scores become:

Query A scores:

|  | doc1 | doc2 | doc3 | doc4 |
| --- | --- | --- | --- | --- |
| knn | 0.347 | 0.35 | 0.348 | 0.346 |
| bm25 | 1.00 | 0.01 | 0.005 | 0.000 |

Query B scores:

|  | doc1 | doc2 | doc3 | doc4 |
| --- | --- | --- | --- | --- |
| knn | 0.347 | 0.35 | 0.348 | 0.346 |
| bm25 | 1.00 | 0.000 | 0.465 | 0.645 |

All scores now lie in the `[0, 1]` range and optimizing the weighted sum is much more straightforward as we now capture the (relative to the query) importance of a result instead of its absolute score and maintain consistency across queries.

## Linear retriever example

Let’s go through an example now to showcase what the above looks like and how the `linear` retriever addresses some of the shortcomings of `rrf`. RRF relies solely on relative ranks and doesn’t consider actual score differences. For example, given these scores:

|  | doc1 | doc2 | doc3 | doc4 |
| --- | --- | --- | --- | --- |
| knn | 0.347 | 0.35 | 0.348 | 0.346 |
| bm25 | 100 | 1.5 | 1 | 0.5 |
| rrf score | 0.03226 | 0.03252 | 0.03200 | 0.03125 |

rrf would rank the documents as:

doc2>doc1>doc3>doc4doc2 > doc1 > doc3 > doc4doc2>doc1>doc3>doc4

However, doc1 has a significantly higher `bm25` score than the others, which `rrf` fails to capture because it only looks at relative ranks. The `linear` retriever, combined with normalization, correctly accounts for both the scores and their differences, producing a more meaningful ranking:

|  | doc1 | doc2 | doc3 | doc4 |
| --- | --- | --- | --- | --- |
| knn | 0.347 | 0.35 | 0.348 | 0.346 |
| bm25 | 1 | 0.01 | 0.005 | 0 |

As we can see in the above, doc1’s great ranking and `score` for `bm25` is properly accounted for and reflected on the final scores. In addition to that, all scores lie now in the `[0, 1]` range so that we can compare and combine them in a much more intuitive way (and even build offline optimization processes).

## Putting it all together

To take full advantage of the `linear` retriever with normalization, the search request would look like this:

```
GET linear_retriever_blog/_search
{
   "retriever": {
       "linear": {
           "retrievers": [
               {
                   "retriever": {
                       "knn": {
                          ...
                        }
                    },
                   "weight": 5
               },
                  {
                   "retriever": {
                       "standard": {
                          ...
                        }
                    },
                   "weight": 1.5,
                   "normalizer": "minmax"
               },

           ]
       }
   }
}
```

This approach combines the best of both worlds: it retains the flexibility and intuitive scoring of the `linear` retriever, while ensuring consistent score scaling with MinMax normalization.

As with all our retrievers, the `linear` retriever can be integrated into any level of a hierarchical retriever tree, with support for explainability, match highlighting, field collapsing, and more.

## When to pick the linear retriever and why it makes a difference

The `linear` retriever:

* Preserves relative importance by leveraging actual scores, not just ranks.
* Allows fine-tuning with weighted contributions from different queries.
* Enhances consistency using normalization, making hybrid search more robust and predictable.

## Conclusion

The `linear` retriever is already available on Elasticsearch Serverless, and the 8.18 and 9.0 releases! More examples and configuration parameters can also be found in our documentation. Try it out and see how it can improve your hybrid search experience — we look forward to your feedback. Happy searching!

### Frequently Asked Questions

#### How does the linear retriever improve hybrid search compared to the previous Reciprocal Rank Fusion (RRF) approach?

The linear retriever offers several advantages over RRF in hybrid search. While RRF focuses solely on relative ranks and ignores actual scores, the linear retriever calculates a weighted sum across queries, preserving the relative importance of each document. This approach allows for more precise control over how different query types contribute to the final ranking. Additionally, the linear retriever supports normalization techniques like MinMax, making it easier to combine scores from different retrievers and optimize the final search result. This flexibility and control provide a more intuitive and fine-tuned hybrid search experience.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt021070497c8cbd23/6a170aeab0367d782c72bd0e/c506a0f5c0a33ca6f85454d4f742d7cb266a7b78-715x413.png)

[Relevance](/search-labs/blog/category/relevance)

### ES|QL, you know, for Search - Introducing scoring and semantic search

April 16, 2025|[Ioana](/search-labs/author/ioana-alina-tagirta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter