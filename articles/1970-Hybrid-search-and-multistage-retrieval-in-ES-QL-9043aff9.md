---
title: 'Hybrid search and multistage retrieval in ES|QL'
company: Elastic
tag: 召回
date: 2026-01-08
url: https://www.elastic.co/search-labs/blog/hybrid-search-multi-stage-retrieval-esql
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Hybrid search and multistage retrieval in ES|QL

Explore the multistage retrieval capabilities of ES|QL, using FORK and FUSE commands to integrate hybrid search with semantic reranking and native LLM completions.

January 08, 2026

[Ioana](/search-labs/author/ioana-alina-tagirta)[Aurélien Foucret](/search-labs/author/aurelien-foucret)[Carlos Delgado](/search-labs/author/carlos-delgado)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

In Elasticsearch 9.2, we’ve introduced the ability to do dense vector search and hybrid search in Elasticsearch Query Language (ES|QL). This continues our investment in making ES|QL the best search language to solve modern search use cases.

## Multistage retrieval: The challenge of modern search

Modern search has evolved beyond simple keyword matching. Today's search applications need to understand intent, handle natural language, and combine multiple ranking signals to deliver the best results.

Retrieval of the most relevant results happens in multiple stages, with each stage gradually refining the result set. This wasn’t the case in the past, where most use cases would require one or two stages of retrieval: an initial query to get results and a potential rescoring phase.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

We start with an initial retrieval, where we cast a wide net to gather results that are relevant to our query. Since we need to sieve through all the data, we should use techniques that return results fast, even when we index billions of documents.

We therefore employ trusted techniques, such as lexical search that Elasticsearch has supported and optimized since the beginning, or vector search, where Elasticsearch excels in speed and accuracy.

Lexical search using BM25 is quite fast and best at exact term matching or phrase matching, and [vector](https://www.elastic.co/docs/solutions/search/vector) or [semantic search](https://www.elastic.co/docs/solutions/search/semantic-search) is better suited for handling natural language queries. [Hybrid search](https://www.elastic.co/what-is/hybrid-search) combines lexical and [vector search](https://www.elastic.co/docs/solutions/search/vector) results to bring the best from both. The challenge that hybrid search solves is that vector and lexical search have completely different and incompatible scoring functions which produce values in different intervals, following different distributions. A vector search score close to 1 can mean a very close match, but it doesn’t mean the same for lexical search. Hybrid search methods, such as [reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) (RRF) and linear combination of scores, assign new scores that blend the original scores from lexical and vector search.

After hybrid search, we can employ techniques such as [semantic reranking](https://www.elastic.co/docs/solutions/search/ranking/semantic-reranking) and [Learning To Rank](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr) (LTR), which use specialized machine learning models to rerank the result.

With our most relevant results, we can use large language models (LLMs) to further enrich our response or pass the most relevant results as context to LLMs in agentic workflows in tools such as [Elastic Agent Builder](https://www.elastic.co/search-labs/blog/elastic-ai-agent-builder-context-engineering-introduction).

ES|QL is able to handle all these stages of retrieval. By design, ES|QL is a piped language, where each command transforms the input and sends the output to the next command. Each stage of retrieval is represented by one or more consecutive ES|QL commands. In this article, we show how each stage is supported in ES|QL.

## Vector search

In Elasticsearch 9.2, we introduced tech preview support for dense vector search in ES|QL. This is as simple as calling the `knn` function, which only requires a [`dense_vector`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector) field and a query vector:

```
FROM books METADATA _score
| WHERE KNN(description_vector, ?query_vector)
| SORT _score DESC
| LIMIT 100
```

This query executes an approximate nearest neighbor search, retrieving 100 documents that are the most similar to the `query_vector`.

## Hybrid search: Reciprocal rank fusion

In Elasticsearch 9.2, we introduced support for hybrid search using RRF and linear combination of results in ES|QL.

This allows combining vector search and lexical search results into a single result set.

To achieve this in ES|QL, we need to use the [`FORK`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fork) and [`FUSE`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fuse) commands. `FORK` runs multiple branches of execution, and `FUSE` merges the results and assigns new relevance scores using RRF or linear combination.

In the following example, we use `FORK` to run two separate branches, where one is doing a lexical search using the `match` function, while the other is doing a vector search using the `knn` function. We then merge the results together using `FUSE`:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE KNN(description_vector, ?query_vector) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE // uses RRF by default
| SORT _score DESC
```

Let's decompose the query to better understand the execution model and first look at the output of the `FORK` command:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE KNN(description_vector, ?query_vector) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
```

The `FORK` commands outputs the results from both branches and adds a `_fork` discriminator column:

| \_id | title | \_score | \_fork |
| --- | --- | --- | --- |
| 4001 | The Hobbit | 0.88 | fork1 |
| 3999 | The Fellowship of the Ring | 0.88 | fork1 |
| 4005 | The Two Towers | 0.86 | fork1 |
| 4006 | The Return of the King | 0.84 | fork1 |
| 4123 | The Silmarillion | 0.78 | fork1 |
| 4144 | The Children of Húrin | 0.79 | fork1 |
| 4001 | The Hobbit | 4.55 | fork2 |
| 3999 | The Fellowship of the Ring | 4.25 | fork2 |
| 4123 | The Silmarillion | 4.11 | fork2 |
| 4005 | The Two Towers | 3.8 | fork2 |
| 4006 | The Return of the King | 4.1 | fork2 |

As you’ll notice, certain documents appear twice, which is why we then use `FUSE` to merge rows that represent the same documents and assign new relevance scores. `FUSE` is executed in two stages:

* For each row, `FUSE` assigns a new relevance score, depending on the hybrid search algorithm that is being used.
* Rows that represent the same document are merged together, and a new score is computed.

In our example, we’re using RRF. As a first step, `FUSE` assigns a new score to each row using the RRF formula:

```
score(doc) = 1 / (rank_constant + rank(doc))
```

Where the `rank_constant` takes a default value of 60 and `rank(doc)`represents the position of the document in the result set.

In the first phase, our results become:

| \_id | title | \_score | \_fork |
| --- | --- | --- | --- |
| 4001 | The Hobbit | 1 / (60 + 1) = 0.01639 | fork1 |
| 3999 | The Fellowship of the Ring | 1 / (60 + 2) = 0.01613 | fork1 |
| 4005 | The Two Towers | 1 / (60 + 3) = 0.01587 | fork1 |
| 4006 | The Return of the King | 1 / (60 + 4) = 0.01563 | fork1 |
| 4123 | The Silmarillion | 1 / (60 + 5) = 0.01538 | fork1 |
| 4144 | The Children of Húrin | 1 / (60 + 6) = 0.01515 | fork1 |
| 4001 | The Hobbit | 1 / (60 + 1) = 0.01639 | fork2 |
| 3999 | The Fellowship of the Ring | 1 / (60 + 2) = 0.01613 | fork2 |
| 4123 | The Silmarillion | 1 / (60 + 3) = 0.01587 | fork2 |
| 4005 | The Two Towers | 1 / (60 + 4) = 0.01563 | fork2 |
| 4006 | The Return of the King | 1 / (60 + 5) = 0.01538 | fork2 |

Then the rows are merged together and a new score is assigned. Since a `SORT _score DESC` follows the `FUSE` command, the final results are:

| \_id | title | \_score |
| --- | --- | --- |
| 4001 | The Hobbit | 0.01639 + 0.01639 = 0.03279 |
| 3999 | The Fellowship of the Ring | 0.01613 + 0.01613 = 0.03226 |
| 4005 | The Two Towers | 0.01587 + 0.01563 = 0.0315 |
| 4123 | The Silmarillion | 0.01538 + 0.01587 = 0.03125 |
| 4006 | The Return of the King | 0.01563 + 0.01538 = 0.03101 |
| 4144 | The Children of Húrin | 0.01515 |

## Hybrid search: Linear combination of scores

[Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) is the simplest way to do hybrid search, but it isn’t the only hybrid search method that we support in ES|QL.

In the following example, we use `FUSE` to combine lexical and [semantic search](https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-semantic-text) results using linear combination of scores:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE MATCH(semantic_description, ?query) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE LINEAR WITH { "weights": { "fork1": 0.7, "fork2": 0.3 } }
| SORT _score DESC
```

Let's first decompose the query and take a look at the input of the `FUSE` command when we only run the `FORK` command.

Notice that we use the `match` function, which is able to not only query lexical fields, such as `text` or `keyword`, but also [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text) fields.

The first `FORK` branch executes a semantic query by querying a `semantic_text` field, while the second one executes a lexical query:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE MATCH(semantic_description, ?query) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
```

The output of the `FORK` command can contain rows with the same `_id` and `_index` values representing the same Elasticsearch document:

| \_id | title | \_score | \_fork |
| --- | --- | --- | --- |
| 4001 | The Hobbit | 0.88 | fork1 |
| 3999 | The Fellowship of the Ring | 0.88 | fork1 |
| 4005 | The Two Towers | 0.86 | fork1 |
| 4006 | The Return of the King | 0.84 | fork1 |
| 4123 | The Silmarillion | 0.78 | fork1 |
| 4144 | The Children of Húrin | 0.79 | fork1 |
| 4001 | The Hobbit | 4.55 | fork2 |
| 3999 | The Fellowship of the Ring | 4.25 | fork2 |
| 4123 | The Silmarillion | 4.11 | fork2 |
| 4005 | The Two Towers | 3.8 | fork2 |
| 4006 | The Return of the King | 4.1 | fork2 |

In the next step, we use `FUSE` to merge rows that have the same `_id` and `_index` values, and assign new relevance scores.

The new score is a linear combination of the scores the row had in each `FORK` branch:

```
_score = 0.7 *_score1 + 0.3 * _score2
```

Here, `_score1` and `_score2` represent the score a document has in the first `FORK` branch and the second `FORK` branch, respectively.

Notice that we also apply custom weights, giving more weight to the semantic score over the lexical one, resulting in this set of documents:

| \_id | title | \_score |
| --- | --- | --- |
| 4001 | The Hobbit | 0.7 \* 0.88 + 0.3 \* 4.55 = 1.981 |
| 3999 | The Fellowship of the Ring | 0.7 \* 0.88 + 0.3 \* 4.25 = 1.891 |
| 4006 | The Return of the King | 0.7 \* 0.84 + 0.3 \* 4.1 = 1.818 |
| 4123 | The Silmarillion | 0.7 \* 0.78 + 0.3 \* 4.11 = 1.779 |
| 4005 | The Two Towers | 0.7 \* 0.86 + 0.3 \* 3.8 = 1.742 |
| 4144 | The Children of Húrin | 0.7 \* 0.79 + 0.3 \* 0 = 0.553 |

One challenge is that the semantic and lexical scores can be incompatible to apply the linear combination, since they can follow completely different distributions. To mitigate this, we first need to normalize the scores, employing score normalization methods, such as `minmax`. This ensures that the scores from each `FORK` branch are first normalized to take values between 0 and 1, before applying the linear combination formula.

To achieve this with `FUSE`, we need to specify the `normalizer` option:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE MATCH(semantic_description, ?query) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE LINEAR WITH { "weights": { "fork1": 0.7, "fork2": 0.3 }, "normalizer": "minmax" }
| SORT _score DESC
```

## Semantic reranking

At this stage, after hybrid search, we should be left with the most relevant documents. We can now use semantic reranking to reorder the results using the `RERANK` command. By default, `RERANK` uses the latest Elastic [semantic reranking](https://www.elastic.co/docs/solutions/search/ranking/semantic-reranking) machine learning model, so no additional configuration is needed:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE KNN(description_vector, ?query_vector) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE
| SORT _score DESC
| LIMIT 100
| RERANK ?query ON description
| SORT _score DESC
```

We now have our best results, sorted by relevance.

One key feature that sets the `RERANK` command apart from other products that offer semantic reranking integrations is that it doesn’t require the input to represent a mapped field from an index. `RERANK` only expects an expression that evaluates to a string value, making it possible to do semantic reranking using multiple fields:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE KNN(description_vector, ?query_vector) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE
| SORT _score DESC
| LIMIT 100
| RERANK ?query ON CONCAT(title, "\n", description) 
| SORT _score DESC
```

## LLM completions

Now we have a set of highly relevant, reranked results.

At this stage, you might simply decide to return the results back to your application or you might want to further enhance your results using LLM completions.

If you’re using ES|QL as part of a retrieval-augmented generation (RAG) workflow, you can choose to call your favorite LLM directly from ES|QL.
To achieve this, we’ve added a new `COMPLETION` command that takes in a prompt, a completion inference ID which designates which LLM to call, and a column identifier to specify where to output the LLM response.

In the following example, we’re using `COMPLETION` to add a new `_completion` column that contains the summary of the `content` column:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE KNN(description_vector, ?query_vector) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE
| SORT _score DESC
| LIMIT 100
| RERANK ?query ON description
| SORT _score DESC
| LIMIT 10
| COMPLETION CONCAT("Summarize the following:\n", description) WITH { "inference_id" : "my_inference_endpoint" }
```

Each row now contains a summary:

| \_id | title | \_score | summary |
| --- | --- | --- | --- |
| 4001 | The Hobbit | 0.03279 | Bilbo helps dwarves reclaim Erebor from the dragon Smaug. |
| 3999 | The Fellowship of the Ring | 0.03226 | Frodo begins the quest to destroy the One Ring. |
| 4005 | The Two Towers | 0.0315 | The Fellowship splits; war comes to Rohan; Frodo nears Mordor. |
| 4123 | The Silmarillion | 0.03125 | Ancient myths and history of Middle-earth's First Age. |
| 4006 | The Return of the King | 0.3101 | Sauron is defeated and Aragorn is crowned King. |
| 4144 | The Children of Húrin | 0.01515 | The tragic tale of Túrin Turambar's cursed life. |

In another use case, you may simply want to answer a question using the proprietary data that you have indexed in Elasticsearch. In this case, the best search results that we’ve computed in the previous stage can be used as context for the prompt:

```
FROM books METADATA _score, _id, _index
| FORK (WHERE KNN(description_vector, ?query_vector) | SORT _score DESC | LIMIT 100)
       (WHERE MATCH(description, ?query) | SORT _score DESC | LIMIT 100)
| FUSE
| SORT _score DESC
| LIMIT 100
| RERANK ?query ON description
| SORT _score DESC
| LIMIT 10
| STATS context = VALUES(CONCAT(title, "\n", description)
| COMPLETION CONCAT("Answer the following question ", ?query, "based on:\n", context) WITH { "inference_id" : "my_inference_endpoint" }
```

Since the `COMPLETION` command unlocks the ability to send any prompt to an LLM, the possibilities are endless. Although we’re only showing a few examples, the `COMPLETION` command can be used in a wide range of scenarios, from security analysts using it to assign scores depending on whether a log event can represent a malicious action or data scientists using it to analyze data, to cases where you just need to [generate Chuck Norris facts based on your data](https://www.elastic.co/search-labs/blog/esql-completion-command-llm-fact-generator).

## This is only the beginning

In the future, we’ll be expanding ES|QL to improve semantic reranking for long documents, better conditional execution of the ES|QL queries using multiple `FORK` commands, support sparse vector queries, removing close duplicate results to enhance result diversity, allowing full text search on runtime generated columns, and many other scenarios.

Additional tutorials and guides:

* [ES|QL for search](https://www.elastic.co/docs/solutions/search/esql-for-search)
* [ES|QL for search tutorial](https://www.elastic.co/docs/reference/query-languages/esql/esql-search-tutorial)
* [Semantic\_text field type](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text)
* [`FORK`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fork) and [`FUSE`](https://www.elastic.co/docs/reference/query-languages/esql/commands/fuse) documentation
* ES|QL search functions

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5417d25f64c77933/6a1706ed1949f76551e7a958/852bff427ac62b79974d88e27ce9670dc132bc46-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)

### Elasticsearch ES|QL views: One query to rule twelve dashboards

May 05, 2026|[Tyler Perkins](/search-labs/author/tyler-perkins)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter