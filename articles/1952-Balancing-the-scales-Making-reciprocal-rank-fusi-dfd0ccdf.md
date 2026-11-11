---
title: 'Balancing the scales: Making reciprocal rank fusion (RRF) smarter with weights'
company: Elastic
tag: 排序
date: 2025-09-15
url: https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Balancing the scales: Making reciprocal rank fusion (RRF) smarter with weights

Exploring weighted reciprocal rank fusion​ (RRF) in Elasticsearch and how it works through practical examples.

September 15, 2025

[Mridula Sivanandan](/search-labs/author/mridula-sivanandan)

[Relevance](/search-labs/blog/category/relevance)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

*Picture this:* you're building a restaurant search that needs to balance location relevance with cuisine matching. Some queries care more about "pizza near me," while others prioritize "Italian restaurants that serve cacio e pepe" or "highly reviewed Italian restaurants." Until now, Elasticsearch's [Reciprocal Rank Fusion (RRF)](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) treated all your retrievers as equals, but your search strategy shouldn't.

That's where **weighted RRF** comes in. Instead of giving every retriever the same voice in your search results, you can now fine-tune their influence, creating more nuanced and effective search experiences. In this blog, we’ll explore the need for weighted RRF and demonstrate how to use it for different search scenarios.

## The challenge: One size doesn't fit all

RRF is fantastic for combining different retrieval strategies—like keyword, semantic, and vector search—into a single ranked result set. But treating all retrievers equally can limit your search quality when some retrieval methods are more valuable for specific query types.

Consider a restaurant search where different query types demand different ranking strategies:

* **Location-focused queries,** like "pizza near me," need location-based signals such as city, neighborhood, or distance to dominate the ranking.
* **Dish-specific queries**, like "Italian restaurants that serve cacio e pepe," should prioritize menu item matching and cuisine type over proximity.
* **Quality-focused queries**, like "highly reviewed Italian restaurants," should emphasize ratings and reviews above all other factors.

Before weighted RRF, the standard way to balance signals was a linear combination of scores (assigning fixed weights and summing them). While powerful, this approach often required workarounds like multiple search passes, custom scoring functions, or manual post-processing, all of which can be difficult to maintain and tune effectively.

Weighted RRF eliminates these pain points by providing a unified framework where each retriever can have its own weight, and the RRF algorithm automatically handles the ranking fusion.

## The solution: Precision through weighting

Weighted RRF provides a simple but powerful way to assign different importance levels to your retrievers. Each retriever now accepts a weight parameter that influences its contribution to the final RRF score.

## What this means for your search

Weighted RRF gives you the flexibility to create smarter, more tailored search experiences.

* **Smarter relevance tuning**: No more one-size-fits-all ranking. Give your semantic search retriever a higher weight for conceptual queries ("find restaurants with cozy atmosphere") while boosting keyword matching for specific terms ("Margherita pizza").

## How it works in practice

Let's say you're building that restaurant search. Here's how weighted RRF transforms your query strategy for different search scenarios:

### Scenario 1: "Pizza near me" - Location-focused search

A user on their phone searches for "pizza near me." In this case, proximity matters most. Weighted RRF lets us give more influence to location signals (city, neighborhood, postal code) than to keyword matches for "pizza."

Here’s what that query could look like in JSON:

```
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "retriever": {
            "standard": {
              "query": {
                "multi_match": {
                  "query": "Vienna",
                  "fields": ["city", "neighborhood", "postal_code"]
                }
              }
            }
          },
          "weight": 0.8
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "menu_items": "pizza"
                }
              }
            }
          },
          "weight": 0.2
        }
      ]
    }
  }
}
```

This weighting favors nearby restaurants even if the menu text match is weaker.

### Scenario 2: "Italian restaurants that serve cacio e pepe" - Cuisine and dish-focused search

Here, the user is looking for a specific cuisine and dish. Weighted RRF emphasizes cuisine and menu matching while still allowing proximity to play a secondary role.

Here’s what that query could look like in JSON:

```
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "cuisine_type": "Italian"
                }
              }
            }
          },
          "weight": 0.4
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "menu_items": "cacio e pepe"
                }
              }
            }
          },
          "weight": 0.6
        }
      ]
    }
  }
}
```

This weighting boosts restaurants that explicitly mention the dish and cuisine, even if they’re slightly farther away.

### Scenario 3: "Highly reviewed Italian restaurants" - Quality and cuisine-focused search

When quality is the priority, ratings carry the most weight. Weighted RRF allows rating thresholds to guide ranking while keeping cuisine type as a supporting factor.

Here’s what that query could look like in JSON:

```
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "retriever": {
            "standard": {
              "query": {
                "range": {
                  "rating": {"gte": 4.5}
                }
              }
            }
          },
          "weight": 0.7
        },
        {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "cuisine_type": "Italian"
                }
              }
            }
          },
          "weight": 0.3
        }
      ]
    }
  }
}
```

This weighting elevates highly rated Italian restaurants, keeping cuisine relevant while letting ratings lead.

Weighted RRF encodes these preferences directly into ranking via per-retriever weights, so the final order reflects what matters for each query.

## Under the hood

When calculating final scores, the standard RRF formula is enhanced with weights:

Example with rank\_constant = 60. Each retriever contributes: weight × 1 / (rank + rank\_constant). Higher weights increase influence; ranks start at 1.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt545ec982f3469f0b/6a17efc83e03d74e0a4f2d46/32ef07dc9c469b0d5a73aaa645b44d6054b7b859-1150x624.png)

Key technical features include:

* **Weights by choice**: Choose between per-retriever weights when you need finer control or default weights when only some retrievers need weighting.
* **Input validation**: Weights must be non-negative.

For advanced customization and hybrid scoring (including normalization), see the Linear retriever <https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/linear-retriever>

## What's next?

Weighted RRF expands RRF to production use cases that require more control than standard RRF could provide. Teams that needed fine-grained control over search relevance can now use RRF instead of building custom solutions. Whether you're balancing location vs. cuisine for restaurants, brand vs. category for e-commerce, or any other complex ranking scenario, weighted RRF gives you the precision you need.

We can't wait to see how you'll use weighted RRF to create more intelligent, responsive search experiences. Happy searching!

*Ready to dive deeper? Explore* [*Reciprocal Rank Fusion*](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) *and* [*Retriever APIs*](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html) *in our official documentation.*

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