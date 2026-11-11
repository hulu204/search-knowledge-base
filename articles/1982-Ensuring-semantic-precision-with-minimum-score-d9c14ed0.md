---
title: 'Ensuring semantic precision with minimum score'
company: Elastic
tag: 搜索相关性
date: 2026-02-20
url: https://www.elastic.co/search-labs/blog/semantic-precision-minimum-score
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Ensuring semantic precision with minimum score

Improve semantic precision by employing minimum score thresholds. The article includes concrete examples for semantic and hybrid search.

February 20, 2026

[Mattias Brunnert](/search-labs/author/mattias-brunnert)

[Relevance](/search-labs/blog/category/relevance)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Jump to

Share

Semantic search has opened up a world of opportunities for search relevance. High-quality sparse and dense models, such as ELSER, E5 and Jina Embedding v4, return relevant results based on the meaning of words, rather than keyword matching. However, semantic search sometimes returns irrelevant results at the tail end or for queries that lack relevant results in the index. This property of sparse and dense models can confuse users or waste precious tokens for large language models (LLMs).

In this article, you’ll learn how you can use the minimum score parameter to increase the precision of your semantic search results. If you’d like to test the examples provided in this blog post, go to [the associated Jupyter notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/ensuring-semantic-precision-with-minimum-score/ensuring_semantic_precision_with_minimum_score.ipynb).

## Background: Precision and recall

In search relevance, *precision* and *recall* are key concepts. Any reader not already familiar is highly encouraged to read up on them. Following is a summary.

* **Precision:** The fraction of returned search results that are relevant to the user.
* **Recall:** The fraction of all relevant documents in the corpus that are included in the search result set.

Or, in other words, precision is returning **only** relevant results; and recall is returning **all** relevant results. As you can imagine, these are often competing requirements. Semantic search tends to have very high recall but can struggle with precision. Keep reading to learn how to get around this property.

## Introducing the minimum score parameter

The ‘min\_score’ parameter allows us to improve precision by setting a minimum score, which will truncate the result set by removing any matches with a score less than the defined threshold. Following is a simple example:

```
GET search-movies/_search
{
  "retriever": {
    "linear": {
      "min_score": 4,
      "retrievers": [
        ...
      ]
    }
  }
}
```

## Normalizing the score

Setting a minimum score is all well and good; however, not all semantic models return a score suitable for a static threshold. ELSER, for example, returns a score that is unbounded. [Some](https://huggingface.co/intfloat/e5-small#faq) dense model scores are densely clustered and only make sense in the context of the specific query.

For most semantic search cases, we recommend using a normalization approach before applying the ‘min\_score’. The normalization ensures that the document score is within a defined interval. Elasticsearch retrievers provide two such [normalizers](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/linear-retriever#linear-retriever-normalizers), ‘l2\_norm’ and ‘minmax’. The most commonly used is ‘minmax’, since it’s easy to understand and works well in many scenarios. Key properties of ‘minmax’ include:

* Document scores are distributed between 0–1.
* The highest scoring document is always scored as 1.
* The lowest scoring document is always scored as 0.

  + This can make it less suitable for keyword search. See “Hybrid search” section for further discussion.

Following is an example of a normalized semantic query with `min_score`. Rank window size has been increased to 500 to allow us to return a longer list of search results, starting at 100.

```
GET search-movies/_search
{
  "size": 100,
  "_source": [
    "title", "overview"
  ],
  "retriever": {
    "linear": {
      "rank_window_size": 500,
      "min_score": 0.25,
      "retrievers": [
        {
          "normalizer": "minmax",
          "retriever": {
            "standard": {
              "query": {
                "semantic": {
                  "field": "overview_vector",
                  "query": "superhero movie"
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

The size has been set to a higher value than normally seen in production. This is so we can inspect the quality of search results and tune the results.

## Hybrid search using the linear retriever

For hybrid search, the simplest approach is to normalize all scores, assign weights, and apply a minimum score. Note that by choosing weights with a sum of 1, you keep the total score within a range of 0–1. This makes it easy to make sense of the final scores and tune `min_score`. Following is an example:

```
GET search-movies/_search
{
  "size": 100,
  "_source": ["title", "overview","keywords"],
  "retriever": {
    "linear": {
      "rank_window_size": 500,
      "min_score": 0.25,
      "retrievers": [
        {
          "weight": 0.6,
          "normalizer": "minmax",
          "retriever": {
            "standard": {
              "query": {
                "semantic": {
                  "field": "overview_vector",
                  "query": "superhero movie"
                }
              }
            }
          }
        },
        {
          "weight": 0.4,
          "normalizer": "minmax",
          "retriever": {
            "standard": {
              "query": {
                "multi_match": {
                  "query": "superhero movie",
                  "fields": ["overview","keywords", "title"],
                  "type": "cross_fields",
                  "minimum_should_match": "2"
                }
              }
            }
          }
        }
      ]
    }
  }
}
```

## Hybrid search using RRF

With BM25, we often control precision through other means, such as using the `AND` operator or `minimum_should_match`. In addition, queries consisting of single, precise, and rare terms will naturally cause search results with few search results, often all being highly relevant. This can lead to:

* Results further back in the result get assigned a low normalized score in the BM25 retriever, even if the absolute BM25 score is close to top scoring hits.
* When adding a very low BM25 score to the semantic score, the total can be approximated as the semantic score.
* The lack of BM25 score contribution can cause the document to be discarded by the `min_score threshold`.

As a solution, we can instead use reciprocal rank fusion (RRF) to combine BM25 and semantic results. RRF gets around the challenge of comparing scores from different search algorithms by instead focusing on the position in each result set. In this scenario, the `min_score` is only applied to the semantic retriever.

```
GET search-movies/_search
{
  "_source": ["title", "overview","keywords"],
  "retriever": {
    "rrf": {
      "rank_window_size": 500,
      "retrievers": [
        {
          "linear": {
            "rank_window_size": 500,
            "min_score": 0.25,
            "retrievers": [
              {
                "normalizer": "minmax",
                "retriever": {
                  "standard": {
                    "query": {
                      "semantic": {
                        "field": "overview_vector",
                        "query": "superhero movie"
                      }
                    }
                  }
                }
              }
            ]
          }
        },
        {
          "standard": {
            "query": {
              "multi_match": {
                "query": "superhero movie",
                "fields": ["overview", "keywords","title"],
                "type": "cross_fields",
                "minimum_should_match": "2"
              }
            }
          }
        }
      ]
    }
  }
}
```

## Conclusion

By using `min_score`, we’ve shown how we can reduce the number of false positives in our result sets caused by the high recall of semantic search algorithms. To learn more about retrievers, please see this [blog post](https://www.elastic.co/search-labs/blog/elasticsearch-retrievers) and the [Elasticsearch documentation](https://www.elastic.co/docs/solutions/search/retrievers-overview).

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