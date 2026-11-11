---
title: 'ES|QL, you know, for Search - Introducing scoring and semantic search'
company: Elastic
tag: 工程相关
date: 2025-04-16
url: https://www.elastic.co/search-labs/blog/esql-introducing-scoring-semantic-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# ES|QL, you know, for Search - Introducing scoring and semantic search

Elasticsearch 8.18 and 9.0 introduce several ES|QL enhancements: scoring, semantic search, expanded configuration for the match function, and a new KQL function.

April 16, 2025

[Ioana](/search-labs/author/ioana-alina-tagirta)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

## Search with ES|QL

With Elasticsearch 8.18 and 9.0, ES|QL adds a host of new functionalities, including:

* support for scoring
* semantic search
* more configuration options for the match function
* a new KQL function

In this blog, we will review these 8.18 features and other exciting new features that we plan to add to ES|QL, reinforcing our investment in making ES|QL a modern search language ready to fit your needs, whether you are building a search application powered by ES|QL or analyzing your data in Kibana Discover.

### Introducing scoring

In 8.17 we added the ability to filter documents using full text functions. If you are unfamiliar with full text filtering in ES|QL, we suggest reading our [original blog post](https://www.elastic.co/search-labs/blog/filtering-in-esql-full-text-search-match-qstr) about it.

With 8.18 and 9.0 we introduce support for [scoring](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/esql-for-search.html#esql-for-search-scoring), making it possible to return documents in order of their relevance. To access the score for each document, simply add the metadata `_score` field to your ES|QL query:

```
FROM books METADATA _score
| WHERE match(title, "Shakespeare") OR match(plot, "Shakespeare")
| SORT _score DESC
```

We retrieve the same scores we get from the equivalent search API query:

```
GET books/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "title": "Shakespeare"
          }
        },
        {
          "match": {
            "title": "Shakespeare"
          }
        }
      ]
    }
  }
}
```

Full text search functions such as `match`, `qstr` and `kql` can only be used in the context of a WHERE condition and are the only ones that contribute to the score.

The `_score` column can not only be used to sort documents by relevance, but also in custom scoring formulas. In the next example, we keep only the most relevant results using a score threshold and then add a score boost based on the reader rating:

```
FROM books METADATA _score
| WHERE match(title, "Shakespeare") OR match(plot, "Shakespeare")
| WHERE _score > 2 // we remove the documents with low scores
| EVAL new_score = _score + rating/5
| SORT new_score DESC
```

### Improving the match function

In ES|QL, the match function simply translates to a Query DSL [match query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html). In 8.18 and 9.0, we expanded the match function's capabilities to include all options that are currently available in Query DSL. It is now possible to set well-known match options such as boost, `fuzziness` and `operator` in ES|QL too:

```
FROM books METADATA _score
| WHERE match(title, "Dream of the red chamber", { "operator": "AND", "fuzziness": "AUTO", "boost": 0.75 })
        OR match(plot, "Dream of the read chamber", { "operator": "AND", "boost": 0.25 })
| SORT _score DESC
```

### Enter semantic search

The 8.18 release comes with the [exciting announcement](https://www.elastic.co/search-labs/blog/semantic-text-ga) that semantic search is now generally available. We've expanded the `match` function to support querying over `semantic_text` field types.

In ES|QL, executing a [semantic query](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/esql-for-search.html#esql-for-search-semantic) is now as simple as performing a full-text query, as shown in this example:

```
FROM books METADATA _score
| WHERE semantic_title:"Shakespeare"
| SORT _score DESC
```

In this example, we set `semantic_title` to use the `semantic_text` field type.

Mapping your index fields as `semantic_text` is all it takes to set up your index for semantic search.

Check our [search with semantic text tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-semantic-text.html) for more details.

### Hybrid search with ES|QL

ES|QL makes it straightforward to do both semantic and lexical search at the same time. It is also possible to set different boosts, prioritizing results from semantic search or lexical search, depending on your use case:

```
FROM books METADATA _score
| WHERE match(semantic_title, "Shakespeare", { "boost": 0.75 }) OR match(title, "Shakespeare", { "boost": 0.25 })
| SORT _score DESC
```

### Transitioning from KQL

If you are a long-term user of Kibana Discover and use KQL ([Kibana Query Language](https://www.elastic.co/guide/en/kibana/8.18/kuery-query.html)) to query and visualize your data and you'd like to try ES|QL but don't know where to start, don't worry, we got you!

In 8.18 and 9.0, ES|QL adds a new function which allows you to use [KQL inside ES|QL](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/esql-for-search.html#esql-for-search-kql). This is as simple as:

```
FROM logs*
| WHERE KQL("http.request.method:GET AND agent.type:filebeat")
```

ES|QL is already available in Kibana Discover.

![ES|QL in Kibana Discover](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte9995e2ae807f22b/6a170ae80e2e49c62d41a0da/3311b56a07d2915d0896bb171b995f39f58d757c-1600x852.png)

This way, you get the best of both worlds: you can continue to use KQL and start getting more familiar with ES|QL at your own pace.

Check out our [getting started with ES|QL](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql-getting-started.html) guide for more information.

### Beyond 8.18 and 9.0

In future releases, we'll be adding more and more search capabilities to ES|QL, including vector search, semantic reranking, enhanced score customization options, and additional methods for combining hybrid search results, such as Reciprocal Rank Fusion (RRF).

### Try it out yourself

These changes are available starting with Elasticsearch 8.18, but they are already available in Elasticsearch Serverless. For Elasticsearch Serverless, start a free trial cloud today or try Elastic on your [local machine](https://github.com/elastic/start-local?cta=local-machine&tech=github&plcmt=cross%20module&pg=search-labs) now!

Follow the [Search and filter in ES|QL tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/esql-search-tutorial.html) for a hands-on introduction to the features described in this blog post!

### Frequently Asked Questions

#### What are the new ES|QL functionalities in Elasticsearch 8.18 and 9.0?

The new ES|QL functionalities in Elasticsearch 8.18 and 9.0 are:
support for scoring, semantic search, more configuration options for the match function, and a new KQL function.

#### What are the benefits of scoring in Elasticsearch?

The benefits of scoring in Elasticsearch are to return documents in order of their relevance.

#### What are the benefits of semantic search in Elasticsearch?

The primary benefit of ES|QL is that it makes semantic search as simple as a full-text query; once you map your index fields as semantic\_text, you are ready to execute queries.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte49ad43c2e28fd37/6a170e530e2e490f5741a1bd/8d9f79cec59d89f4e14657db7df846ed3104a2da-1024x565.png)

[Relevance](/search-labs/blog/category/relevance)

### An open‑source Hebrew analyzer for Elasticsearch lemmatization

February 17, 2026|[Lily Adler](/search-labs/author/lily-adler)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter