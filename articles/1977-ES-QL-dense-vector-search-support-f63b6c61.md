---
title: 'ES|QL dense vector search support'
company: Elastic
tag: 召回
date: 2026-02-05
url: https://www.elastic.co/search-labs/blog/dense-vector-search-elasticsearch-query-language
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# ES|QL dense vector search support

Using ES|QL for vector search on your dense\_vector data.

February 05, 2026

[Carlos Delgado](/search-labs/author/carlos-delgado)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

You can now use Elasticsearch Query Language (ES|QL) for vector search! ES|QL can retrieve, filter, and score `dense_vector` fields. Use k-nearest neighbors (KNN) queries for fast, approximate nearest neighbors search at scale. Use vector similarity functions for exact search and custom scoring.

KNN is simpler to use in ES|QL than in the Query DSL. Prefilters and the number of results to retrieve per shard are automatically inferred from the ES|QL query.

## **What is vector search?**

Modern search is no longer limited to exact keyword matching. Users expect systems to understand *meaning*, not just text. This is where **vector embeddings** and Elasticsearch’s [`dense_vector`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector) field type come in.

The easiest way to use vector search in Elasticsearch is to use the [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text) [field type](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text). It allows you to automatically generate text embeddings, perform semantic search, and handle chunking. However, you may want to use `dense_vector` instead when:

* You’re already using `dense_vector` fields.
* You’re using non-textual data, like images, sound, or video.
* You need to generate embeddings separately to ingestion in Elasticsearch.
* You need to do custom or advanced scoring.
* You want to perform exact nearest neighbors search.

A [`dense_vector`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector) stores numerical embeddings produced by machine learning models. These embeddings capture semantic similarity: documents with similar meaning have vectors that are close to each other in high-dimensional space.

With vectors, you can build:

* [`Semantic text`](https://www.elastic.co/docs/solutions/search/semantic-search) [search](https://www.elastic.co/docs/solutions/search/semantic-search), for finding documents related to a question.
* [Retrieval-augmented generation](https://www.elastic.co/what-is/retrieval-augmented-generation) (RAG).
* Recommendation systems.

ES|QL brings the power of a query-piped experience to Elasticsearch. Adding first-class support for `dense_vector` fields means you can now **retrieve, filter, score, and search using vectors directly in ES|QL**, alongside your text and non-text data.

In this post, we’ll walk through how to work with `dense_vector` fields in ES|QL, from basic inspection to approximate and exact similarity search, and how to use vector search as part of hybrid search strategies.

## **The basics: Retrieving vector data**

Assume you have an index with a mapping similar to:

```
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "category": { "type": "keyword" },
      "content_vector": {
        "type": "dense_vector",
        "dims": 384,
        "similarity": "cosine"
      }
    }
  }
}
```

You can retrieve vector fields just like any other column:

```
FROM documents
| KEEP title, content_vector
| LIMIT 5
```

Keep in mind that vectors can be large. For exploration and debugging, it may be useful to retrieve vector data, but in production you should avoid returning full vector data unless it's really necessary.

You can use familiar ES|QL constructs to check how many rows have vector information:

```
FROM documents
| WHERE content_vector IS NOT NULL
| STATS non_null = COUNT(*)
```

## **Approximate search using KNN**

Vector search means finding the most similar vectors to a given query vector.

For large datasets, the most common approach is [approximate nearest neighbor](https://www.elastic.co/blog/understanding-ann) (ANN) search. ANN tries to find the most similar vectors by using data structures that allow for fast computation of similar vectors but doesn’t guarantee that all vectors will be considered.

ES|QL exposes approximate search via the [`KNN`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-knn) [function](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-knn):

```
FROM documents MEDATADATA _score
| WHERE KNN(content_vector, [0.12, -0.03, 0.98, ...])
| SORT _score DESC
| KEEP title, _score
| LIMIT 10
```

This simple example:

* Searches over the `content_vector` field.
* Uses a dense vector query `[0.12, -0.03, 0.98, ...]` to search similar vectors to it.
* Sorts the results by score, by using the `METADATA _score` attribute that will be populated by the `KNN` function.
* Keeps just the title and score, as the `content_vector` field is not interesting to be returned and we can avoid loading its contents.
* Retrieves the top 10 elements by using `LIMIT`. This automatically sets `k` to 10 in the `KNN` function.

The `KNN` function can be further customized by using options:

```
FROM documents MEDATADATA _score
| WHERE KNN(content_vector, [0.12, -0.03, 0.98, ...], {"k": 20, "min_candidates": 100, "rescore_oversample": 4.0})
| SORT _score DESC
| KEEP title, _score
| LIMIT 10
```

See the [`KNN`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-knn) [function](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-knn) named parameters for a complete description of the available parameters.

### **Combining KNN with filters**

You can narrow down the candidate set for the vector search:

```
FROM documents METADATA _score
| WHERE category == "tutorial"
| WHERE KNN(content_vector, [0.12, -0.03, 0.98, ...])
| SORT _score DESC
| LIMIT 10
| KEEP title, category, _score
```

Of course, you can use any other [`WHERE`](https://www.elastic.co/docs/reference/query-languages/esql/commands/where) [clauses](https://www.elastic.co/docs/reference/query-languages/esql/commands/where) that filter the results or include `KNN` as part of a filter expression:

```
FROM documents METADATA _score
| WHERE published_date > NOW() - 1 hour AND LENGTH(category) > 10 AND KNN(content_vector, [0.12, -0.03, 0.98, ...])
```

### **KNN made simple**

`KNN` is simpler to use in ES|QL. You won't have to specify prefilters or k for your query explicitly.

[Prefilters](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query#knn-query-filtering) are the way to ensure that a `KNN` query returns as many results as expected. Prefilters are applied on the KNN search itself, instead of being applied after the query.

Keep in mind that `KNN` returns the top k results it's been asked for. If filters are applied after the `KNN` query, some of the results returned by the query may be filtered. If that happens, we’ll retrieve fewer results than expected.

The Query DSL [`knn`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query) [query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query) contains a section for specifying prefilters:

```
POST my-image-index/_search
{
  "query" : {
    "knn": {
      "field": "content_vector",
      "query_vector": [0.12, -0.03, 0.98, ...],
      "filter" : {
        "term" : { "category" : "tutorial" }
      }
    }
  }
}
```

You don't need to care about prefilters when using `KNN` in ES|QL. All filters are applied as prefilters for the `KNN` function, so there’s no need to specify them as a specific option or command; just use `WHERE` and let ES|QL do it for you!

KNN also allows specifying the number of results to retrieve per shard; that is, the k parameter. Similar to the Query DSL, k defaults to the `LIMIT` specified in your query.

## **Exact search using vector similarity functions**

`KNN` is designed to be fast, and that makes it ideal for large datasets (hundreds of thousands or millions of vectors) and latency-sensitive applications. The trade-off is that results are *approximate*, though usually very accurate.

Sometimes you want *exact* similarity computation instead of approximate search, for example:

* When your dataset is small.
* When the filters used in the query are very restrictive and select a small subset of your dataset.

ES|QL provides the following [vector similarity functions](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions):

* [`V_COSINE`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-v_cosine)
* [`V_DOT_PRODUCT`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-v_dot_product)
* [`V_HAMMING`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-v_hamming)
* [`V_L1_NORM`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-v_l1_norm)
* [`V_L2_NORM`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-v_l2_norm)

Using these functions, you can calculate the similarity of your query vector with all the vectors your query retrieves.

The following query uses the same mapping as our `KNN` example, above, but does exact search using cosine similarity:

```
FROM documents
| EVAL similarity = V_COSINE(content_vector, [0.12, -0.03, 0.98, ...])
| SORT similarity DESC
| KEEP title, similarity
| LIMIT 10
```

This query:

* Computes the similarity using the [`V_COSINE`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-v_cosine) vector similarity function.
* Sorts on the computed similarity.
* Keeps the top 10 similar results.

## Semantic search

When doing semantic search, you'll be trying to match a text query to your vectors. Of course, you can retrieve the query vector by first calculating the embeddings and then supply the query vector directly to your vector search.

But it would be much simpler to allow Elasticsearch to calculate the embeddings for you by using the [`TEXT_EMBEDDING`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-text_embedding) function:

```
FROM documents METADATA _score
| WHERE KNN(content_vector, TEXT_EMBEDDING("my semantic query", inference_id))
| SORT _score DESC
| LIMIT 10
| KEEP title, _score
```

[`TEXT_EMBEDDING`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-text_embedding) uses an already existing [inference endpoint](https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-inference) to automatically calculate the embeddings and use them in your query.

## Hybrid search

Most searches don't rely just on vector data; they need to be combined with lexical search, as well, so we have the best of both worlds:

* Lexical information is great for exact search of words and synonyms and provides a strong signal that users are looking for specific terms.
* Vectors capture meaning and intention, using similar phrases or terms that are not lexically related.

Combining vector search and lexical search is best done using [`FORK`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fork) and [`FUSE`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fuse):

```
FROM documents METADATA _score, _id, _index
| FORK
(WHERE KNN(content_vector, TEXT_EMBEDDING("my query")) | SORT _score DESC | LIMIT 10)
(WHERE MATCH(title, "my query") | SORT _score DESC | LIMIT 10)
| FUSE
| SORT _score DESC
| LIMIT 10
```

The query above:

* Uses [`FORK`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fork) to do two queries:

  + A [`KNN`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/dense-vector-functions#esql-knn) query over a `dense\_vector` field.
  + A [`MATCH`](https://www.elastic.co/docs/reference/query-languages/esql/functions-operators/search-functions#esql-match) query over a text field.
  + Both queries sort by score and return the top 10 results for each.
* Uses [`FUSE`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fuse) to mix together the query results by using reciprocal rank fusion (RRF) by default.

This allows total control of the queries you want to perform, how many results to retrieve from each one, and how to combine the results together.

Check out our [multistage retrieval](https://www.elastic.co/search-labs/blog/hybrid-search-multi-stage-retrieval-esql#vector-search) blog post for more details on how modern search works and how easy it is to implement via ES|QL.

## Custom scoring

Calculating custom scoring is easy using ES|QL! Just use the `_score` metadata field for calculating your custom score:

```
FROM documents METADATA _score
| WHERE KNN(content_vector, TEXT_EMBEDDING("my semantic query", inference_id)
| EVAL my_custom_score = _score * 1.5 + ...
| SORT my_custom_score DESC
| LIMIT 10
```

If you're using exact search, you already have an evaluation for the vector similarity that you can fine-tune:

```
FROM documents
| EVAL similarity = V_COSINE(content_vector, [0.12, -0.03, 0.98, ...])
| EVAL my_custom_score = similarity * 1.5 + ...
| SORT my_custom_score DESC
| LIMIT 10
```

Compared to the Query DSL [`script_score`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-script-score-query), this is a much simpler and more iterative approach and fits perfectly into the ES|QL execution flow.

## Using query parameters

When using a query vector, you can specify it directly on the query as in our previous examples. But you may have noticed that we're using ellipses (...) to signal that there's more data to come.

Dense vectors are usually high dimensional; they can have hundreds or thousands of dimensions, so copying and pasting your query vector on the query itself can make it difficult to understand or reason about, as you'll be seeing thousands of numeric values on your screen.

Remember that you can use ES|QL query parameters for supplying parameters to your query:

```
POST _query
{
  "query": """
FROM documents
| WHERE KNN(content_vector, ?query_vector)
| SORT _score DESC
| KEEP title, _score
| LIMIT 10
   """,
 "params": [{"query_vector" : [0.12, -0.03, 0.98, ...]}]
}
```

This helps to keep your query and parameters separated, so you can focus on the query logic and not on specific parameters that get in your way.

Using query parameters for vectors is also more performant, as vectors are parsed faster that way using the request parser instead of the ES|QL parser.

## **Conclusion**

ES|QL doesn’t just support vector search; it makes it a natural part of how you query your data. It allows you to use a single, powerful syntax for text, vectors, and everything in between, including:

* Vector search, both approximate and exact.
* Semantic search, using text for search over vector data.
* Hybrid search, combining the best of text and vector search.
* Custom vector scoring, using `EVAL` and ES|QL constructs.

Vector search in ES|QL is easier than in the Query DSL, by inferring prefilters and parameters, and integrating with the expressive, feature-rich expressions that ES|QL allows.

Defining KNN as part of a query pipeline for [multistage retrieval](https://www.elastic.co/search-labs/blog/hybrid-search-multi-stage-retrieval-esql#vector-search) is just another piece in the query; you can keep using filters, combine with other text functions for hybrid search, and apply reranking or query completion on top of your vector results.

We’ll keep adding vector functions for performing vector arithmetic and aggregations over dense vectors, so you can use the full power of ES|QL to manipulate your vector data.

Happy (vector) searching!

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf69e1ba73bd5d402/6a6a340599442cd9e0df1d94/1794a179d9536e693a0982634da59aff209c9d68-1280x720.png)

[Analytics](/search-labs/blog/category/analytics)[ES|QL](/search-labs/blog/category/esql)[Python](/search-labs/blog/category/python-programming)

### How to instrument your search API with OpenTelemetry and query it with ES|QL

July 22, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter