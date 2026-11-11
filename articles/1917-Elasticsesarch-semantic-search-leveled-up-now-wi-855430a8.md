---
title: 'Elasticsesarch semantic search, leveled up: now with native match, knn and sparse_vector support'
company: Elastic
tag: 召回
date: 2025-03-06
url: https://www.elastic.co/search-labs/blog/semantic-search-match-knn-sparse-vector
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsesarch semantic search, leveled up: now with native match, knn and sparse\_vector support

Semantic text search becomes even more powerful, with native support for match, knn and sparse\_vector queries. This allows us to keep the simplicity of the semantic query while offering the flexibility of the Elasticsearch query DSL.

March 06, 2025

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Relevance](/search-labs/blog/category/relevance)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Elasticsearch’s [semantic query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-semantic-query.html) is incredibly powerful, allowing users to perform semantic search over data configured in [semantic\_text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html) fields. Much of this power lies in simplicity: just set up a `semantic_text` field with the inference endpoint you want to use, and then ingest content as if indexing content into a regular `text` field. The inference happens automatically and transparently, making it simple to set up and use a search index with semantic functionality.

This ease of use does come with some tradeoffs: we simplified semantic search with `semantic_text` by making judgments on default behavior that fit the majority of use cases. Unfortunately, this means that some customizations available for traditional vector search queries aren’t present in the [semantic query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-semantic-query.html). We didn’t want to add all of these options directly to the `semantic` query, as that would undermine the simplicity that we strive for. Instead, we expanded the queries that support the `semantic_text` field, leaving it up to you to choose the best query that meets your needs.

Let’s walk through these changes, starting with creating a simple index with a semantic\_text field:

```
PUT index-songs-semantic
{
  "mappings": {
    "properties": {
      "song_title": {
        "type": "text"
      },
      "artist": {
        "type": "keyword"
      },
      "lyric": {
        "type": "semantic_text"
      }
    }
  }
}

// Now index a sample document
POST index-songs-semantic/_doc/1
{
  "song_title": "...Baby One More Time",
  "artist": "Britney Spears",
  "lyric": "When I'm with you, I lose my mind, give me a sign"
}
```

## We made match happen in semantic search!

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc5e9a7041fc40292/6a17eeda414c646ff494524f/9b15e17822e297e35a46393ef2a7c1e6d55fedd9-1792x1024.png)

First and most importantly, the [match query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html) will now work with `semantic_text` fields!

This means that you can change your old semantic query:

```
GET index-songs-semantic/_search
{
  "query": {
    "semantic": {
      "field": "lyric",
      "query": "song lyrics about love"
    }
  }
}
```

Into a simple `match` query:

```
GET index-songs-semantic/_search
{
  "query": {
    "match": {
      "lyric": "song lyrics about love"
    }
  }
}
```

We can see the benefits of semantic search here because we’re searching for “song lyrics about love”, none of which appears in the indexed document. This is because of ELSER’s text expansion.

But wait, it gets better!

If you have multiple indices, and the same field name is `semantic_text` in one field and perhaps text in the other field, you can still run `match` queries against these fields. Let’s create another index, with the same field names, but different types (`text` instead of `semantic_text`). Here’s a simple example to illustrate:

```
// Setup - Create a similar index without semantic fields
PUT index-songs-lexical
{
  "mappings": {
    "properties": {
      "song_title": {
        "type": "text"
      },
      "artist": {
        "type": "keyword"
      },
      "lyric": {
        "type": "text"
      }
    }
  }
}

POST index-songs-lexical/_doc/2
{
  "song_title": "Crazy",
  "artist": "Britney Spears",
  "lyric": "You drive me crazy, I just can't sleep, I'm so excited, I'm in too deep"
}

GET index-songs-semantic,index-songs-lexical/_search
{
  "query": {
    "match": {
      "lyric": "crazy"
    }
  }
}
```

Here, searching for “crazy” brings up both the lexical match that has “crazy” in the title, and the semantic lyric “lose my mind.”

There are some caveats to keep in mind when using the `match` functionality with `semantic_text`:

* The underlying `semantic_text` field has a limitation where you can’t use multiple inference IDs on the same field. This limitation extends to `match`**—**meaning that if you have two semantic\_text fields with the same name, they need to have the same inference ID or you’ll get an error. You can work around this by creating different names and querying them in a [boolean query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html) or a compound [retriever](https://www.elastic.co/guide/en/elasticsearch/reference/current/retrievers-overview.html).
* Depending on what model you use, the scores between lexical (text) matches and semantic matches will likely be very different. In order to get the best ranking of results, we recommend using second stage rerankers such as [semantic reranking](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-reranking.html) or [RRF](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html).

Semantic search using the `match` query is also available in [ES|QL](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql-functions-operators.html#esql-match)! Here’s the same example as above, but using ES|QL:

```
POST _query?format=txt
{
  "query": """
  FROM index-songs-semantic,index-songs-lexical METADATA _score
  | WHERE MATCH(lyric, "crazy")
  | KEEP artist, song_title, lyric, _score
  | SORT _score
  | LIMIT 5
  """
}
```

## Expert-level semantic search with knn and sparse\_vector

Match is great, but sometimes you want to specify more vector search options than the semantic query supports. Remember, the tradeoff of making the semantic query as simple as it is involved making some decisions on default behavior.

This means that if you want to take advantage of some of the more advanced vector search features, perhaps `num_candidates` or `filter` from the [knn query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html) or [token pruning](https://www.elastic.co/search-labs/blog/text-expansion-pruning) in the [sparse\_vector query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-sparse-vector-query.html), you won’t be able to do so using the semantic query.

In the past, we provided some workarounds to this, but they were convoluted and required knowing the inner workings and architecture of the `semantic_text` field and constructing a corresponding nested query. If you’re doing that workaround now, it will still work—however, we now support query DSL using `knn` or `sparse_vector` queries on `semantic_text` fields.

### All about that dense (vector), no trouble

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf6651a79c3e56345/6a17eedcb1e113820979f31d/aa3ea406fc072698db510a0b2ab64eb0266948c1-1792x1024.png)

Here’s an example script that populates a `text_embedding` model and queries a `semantic_text` field using the knn query:

```
PUT index-dense-semantic-songs
{
  "mappings": {
    "properties": {
      "song_title": {
        "type": "text"
      },
      "artist": {
        "type": "keyword"
      },
      "lyric": {
        "type": "semantic_text",
        "inference_id": ".multilingual-e5-small-elasticsearch"
      }
    }
  }
}

// Index sample documents
POST index-dense-semantic-songs/_doc/4
{
  "song_title": "Oops! ...I Did It Again",
  "artist": "Britney Spears",
  "lyric": "Oops, I did it again, I played with your heart, got lost in the game."
}

POST index-dense-semantic-songs/_doc/5
{
  "song_title": "Poker Face",
  "artist": "Lady Gaga",
  "lyric": "Can't read my, can't read my, no, he can't read my poker face"
}

GET index-dense-semantic-songs/_search
{
  "query": {
    "knn": {
      "field": "lyric",
      "k": 10,
      "num_candidates": 100,
      "query_vector_builder": {
        "text_embedding": {
          "model_text": "game"
        }
      }
    }
  }
}
```

The `knn` query can be modified with extra options to enable more advanced queries against the semantic\_text field. Here, we perform the same query but add a pre-filter against the `semantic_text` field:

```
GET index-dense-semantic-songs/_search
{
  "query": {
    "knn": {
      "field": "lyric",
      "k": 10,
      "num_candidates": 100,
      "query_vector_builder": {
        "text_embedding": {
          "model_text": "game"
        }
      },
      "filter": {
        "term": {
          "artist": "Britney Spears"
        }
      }
    }
  }
}
```

### Keepin’ it sparse (vector), keepin’ it real

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt540cbe07b8eeb546/6a17eedfe8fbce91343a1a09/1af6680a3bae23b0f1b3fd4605ba6cb3184318e2-1792x1024.png)

Similarly, sparse embedding models can be queried more specifically using `semantic_text` fields as well. Here’s an example script that adds a few more documents and uses the `sparse_vector` query:

```
POST index-songs-semantic/_doc/6
{
  "song_title": "Crazy In Love",
  "artist": "Beyoncé",
  "lyric": "Looking so crazy, your love's got me looking, got me looking so crazy in love"
}

POST index-songs-semantic/_doc/7
{
  "song_title": "Complicated",
  "artist": "Avril Lavigne",
  "lyric": "Why'd you have to go and make things so complicated?, I see the way you're acting like you're somebody else"
}

GET index-songs-semantic/_search
{
  "query": {
    "sparse_vector": {
      "field": "lyric",
      "query": "crazy"
    }
  }
}
```

The `sparse_vector` query can be modified with extra options, to enable more advanced queries against the `semantic_text` field. Here, we perform the same query but add [token pruning](https://www.elastic.co/search-labs/blog/text-expansion-pruning) against a `semantic_text` field:

```
GET index-songs-semantic/_search
{
  "query": {
    "sparse_vector": {
      "field": "lyric",
      "query": "crazy",
      "prune": true,
      "pruning_config": {
        "tokens_freq_ratio_threshold": 1,
        "tokens_weight_threshold": 0.4,
        "only_score_pruned_tokens": false
      }
    }
  }
}
```

This example significantly decreases the token frequency ratio required to pruning, which helps us show differences with such a small dataset, though they’re probably more aggressive than you’d want to see in production (remember, token pruning is about pruning irrelevant tokens to improve performance, not drastically change recall or relevance). You can see in this example that the Avril Lavigne song is no longer returned, and the scores have changed due to the pruned tokens. (Note that this is an illustrative example, and we still [recommend a rescore adding pruned tokens back into scoring](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-sparse-vector-query.html#sparse-vector-query-with-pruning-config-and-rescore-example) for most use cases).

You’ll note that with all of these queries if you’re only querying a `semantic_text` field, you no longer need to specify the inference ID in `knn`’s `query_vector_builder` or in the `sparse_vector` query. This is because it will be inferred from the `semantic_text` field. You *can* specify it if you want to override with a different (compatible!) inference ID for some reason or if you’re searching combined indices that have both `semantic_text` and [sparse\_vector](https://www.elastic.co/guide/en/elasticsearch/reference/current/sparse-vector.html) or [dense\_vector](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html) fields though.

## Try it out yourself

We’re keeping the original `semantic` query simple, but expanding our semantic search capabilities to power more use cases and seamlessly integrate semantic search with existing workflows. These power-ups are native to Elasticsearch and are already available in Serverless. They’ll be available in stack-hosted Elasticsearch starting with version 8.18.

Try it out today!

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt31515f5dc8f12092/6a170c170c48570fa101aabd/dc08f5c15b12a0e686b8922ad8d2b997ca1227d7-1024x1024.jpg)

[Vector Database](/search-labs/blog/category/vector-database)[Basics](/search-labs/blog/category/basics)

### Elasticsearch new semantic\_text mapping: Simplifying semantic search

June 24, 2024|[Carlos Delgado](/search-labs/author/carlos-delgado)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt03108313e79d6e7d/6a17d725a29299397cd02ae1/53baae570e66ebc66f0fa47b406436e2c22b3162-816x452.png)

[Vector Database](/search-labs/blog/category/vector-database)

### The sparse vector query: Searching sparse vectors with inference or precomputed query vectors

July 23, 2024|[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd528ca7843f1946f/6a170b2e2b835ff0b7f4b21b/d2c2a3cddc393d80b11e4ed93672e345d0addd7d-1024x1024.png)

[Vector Database](/search-labs/blog/category/vector-database)

### Introducing kNN Query: An expert way to do kNN search

December 07, 2023|[Mayya Sharipova](/search-labs/author/mayya-sharipova)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter