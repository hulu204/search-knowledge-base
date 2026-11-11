---
title: 'Scoring documents based on the closest ones with multiple kNN fields'
company: Elastic
tag: 召回
date: 2024-05-31
url: https://www.elastic.co/search-labs/blog/scoring-documents-by-the-closest-one-with-multiple-kNN-fields
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Scoring documents based on the closest ones with multiple kNN fields

Learn how to search through documents with multiple kNN fields, and score the resultant documents based on multiple kNN vector fields.

May 31, 2024

[Madhusudhan Konda](/search-labs/author/madhusudhan-konda)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

This guide explains how to search through documents with multiple kNN fields and how to score the resulting documents based on multiple kNN vector fields. Before diving into the details, let's take a few minutes to introduce kNN and semantic search and explain the mechanics of kNN.

## Introduction to kNN search and semantic search

Elasticsearch is more than just a lexical (textual) search engine. Elasticsearch is a scalable data store and vector database that supports k-Nearest Neighbors (kNN) search as well as Semantic Search in addition to the traditional textual matching.

kNN search in Elasticsearch is primarily used for finding the "nearest neighbors" of a given point in a multi-dimensional space. Documents are represented as a set of numbers (vectors) that when searched, the kNN feature fetches relevant documents that are closer to the query vector. The kNN search is commonly applied in scenarios involving vectors, where vectors are created from text, images or audio by employing a process called "embeddings" using deep neural networks.

Semantic search, on the other hand is a search that is powered by natural language processing characteristics - which helps search for relevant results based on intent and meaning rather than just textual match.

## kNN mechanics

The kNN (k-nearest neighbors) fetches the search results that are pretty much k-number of nearest documents to the given user's query, measured using an algorithm.

The way it works is by calculating the distance - usually [Euclidean](https://en.wikipedia.org/wiki/Euclidean_distance) or [Cosine](https://en.wikipedia.org/wiki/Cosine_similarity) similarity - between the vectors. When we perform a query a dataset using kNN, Elasticsearch finds the top 'k' entries that are closest to our query vector.

> Before performing search related activities on the data to fetch the results, the index must be primed with appropriate embeddings - embedding is a fancy name for vectorized data. The fields are of type `dense_vector` holding numerical data.

Let's take an example:

If you have an image dataset and you've converted these images into vectors using a neural network, you can use kNN search to find images most similar to your query image. If you provide the vector representation of a "pizza" image, kNN can help you find other images that are visually similar, such as pancakes and perhaps pasta :)

> kNN search is about finding the nearest data points in a vector space, thus suitable for similarity searches for text or image embeddings. In contrast, Semantic Search is about understanding the meaning and context of words in a search query, making it powerful for text-based searches where intent and context matter.

## Scoring documents

Scoring documents based on the closest document when you have multiple k-nearest neighbor (kNN) fields involves leveraging Elasticsearch's ability to handle vector similarity to rank documents. This approach is particularly beneficial in scenarios such as semantic search and recommendation engines. Or cases where we are dealing with multi-dimensional data and need to find the "closest" or most similar items based on multiple aspects (fields).

## How to search and score documents with multiple kNN fields

### Text embedding and vector fields

Let's take an example of the `movies` index that consists of a few files such as `title`, `synopsis` and others. We will represent them using the common data types, like `text` data type. In addition to these normal fields, we would create two more fields: `title_vector` and `synopsis_vector` field - as the name indicates - they are `dense_vector` data type fields. That means, the data will be vectorized using a process called "text embedding".

The embedding model is a Natural Language Processing Neural Network, which will convert the inputs to an array of numbers. The vectorized data will then be stored in a `dense_vector` type field. The data documents can have multiple fields, including a few `dense_vector` fields to store vector data.

So, in the following section, we'll create the index with a mix of normal and kNN fields.

### Creating an Index with kNN Fields

Let's create an index called `movies` that holds sample movie documents. Our documents will have multiple fields, including a couple of kNN fields to store the vector data. The following snippet demonstrates the index mapping code:

```
PUT /movies
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "title_vector.predicted_value": {
        "type": "dense_vector",
        "dims": 384
      },
      "synopsis": {
        "type": "text"
      },
      "synopsis_vector.predicted_value": {
        "type": "dense_vector",
        "dims": 384
      },
      "genre": {
        "type": "text"
      }
    }
  }
}
```

The notable thing is that the `title` field which is of type `text` has an equivalent vector type field: `title_vector.predicted_value`. Similarly the vector field for `synopsis` is the `synopsis_vector.predicted_value` field. Also, the dense vector fields have dimention (384) mentioned in the above code as `dims`. This is to indicate the model will produce 384 dimensions for each of the ingested field. The maximum dimensions we can request to be produced on a `dense_vector` field is 2048.

Executing this script creates a new index named `movies` with two vector fields: `title_vector` and `synopsis_vector`.

### Indexing sample docs

Now that we have an index, we can index some movies and search. In addition to the title and synopsis fields, the document will also have vector fields. Before we index the documents, we need to fill in the document with the respective vectors. The following code demonstrates a movie document sample once the vectors were generated:

```
POST /movies/_doc/1
{
  "title": "The Godfather",
  "title_vector": [0.1, 0.5, 3, 4,...], // vectorized data
  "synopsis": "The aging patriarch of an organized crime dynasty....",
  "synopsis_vector": [0.2, 0.6, 1, 0.7,...] // vectorized data
}
```

As you can see, the vector data needs to be prepared for the document to get ingested. There are a couple of ways you can do this:

* one calling the inference API on the `text_embedding` model outside of Elasticsearch to get the data vectorized, as shown above (I've mentioned it here as a reference, though we'd want to go instead using an inference processor pipeline) and
* the other is to set up and use the inference pipeline.

### Setting up an inference processor

We can set up an ingestion pipeline that would apply the embedding function on the relevant field to produce the vectorized data. For example, the following code creates the `movie_embedding_pipeline` processor that would generate the embeddings for each field and add them to the document:

```
PUT _ingest/pipeline/movie_embedding_pipeline
{
  "processors": [
    {
      "inference": {
        "model_id": ".multilingual-e5-small",
        "target_field": "title_vector",
        "field_map": { "title": "text_field" }
      }
    },
    {
      "inference": {
        "model_id": ".multilingual-e5-small",
        "target_field": "synopsis_vector",
        "field_map": { "synopsis": "text_field" }
      }
    }
  ]
}
```

The ingesting pipeline may require a bit of explanation:

* Two fields - the `title_vector` and `synopsis_vector` - which are mentioned as target fields - are the `dense_vector` field types. Hence, they store vectorized data produced by the `multilingual-e5-small` embedding model
* The `field_map` mentions the field from the document (`title` and the `synopsis` fields in this case) gets mapped to a `text_field` field of the model
* The `model_id` declares the embedding model that was used for embedding the data
* The `target_field` is the name of the field where the vectorized data will be copied to

Executing the above code will create a `movie_embedding_pipeline` ingest pipeline. That is - a document with just `title` and `synopsis` will be enhanced with additional fields (`title_vector` and `synopsis_vector`) that will have a vectorized version of the content.

### Indexing the documents

The movie document will consist of title and synopsis fields as expected - so we can index it as shown below. Note that the document undergoes enhancement through the pipeline processor as enabled in the url. The following code snippet shows indexing a handful of movies:

```
POST movies/_doc/?pipeline=movie_embedding_pipeline
{
  "title": "The Godfather",
  "synopsis": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son."
}

POST movies/_doc/?pipeline=movie_embedding_pipeline
{
  "title": "Avatar",
  "synopsis": "A paraplegic Marine dispatched to the moon Pandora on a unique mission becomes torn between following his orders and protecting the world he feels is his home."
}

POST movies/_doc/?pipeline=movie_embedding_pipeline
{
  "title": "Godzilla",
  "synopsis": "The world is beset by the appearance of monstrous creatures, but one of them may be the only one who can save humanity."
}

POST movies/_doc/?pipeline=movie_embedding_pipeline
{
  "title": "The Good, The Bad and The Ugly",
  "synopsis": "A bounty hunting scam joins two men in an uneasy alliance against a third in a race to find a fortune in gold buried in a remote cemetery."
}

POST movies/_doc/?pipeline=movie_embedding_pipeline
{
  "title": "A Few Good Men",
  "synopsis": "Military lawyer Lieutenant Daniel Kaffee defends Marines accused of murder. They contend they were acting under orders."
}
```

> We can surely use `_bulk` API to index the documents in one go - do checkout this [Bulk API documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html#docs-bulk-api-query-params) for futher details.

Once these documents were indexed, you can fetch the movies to check if the vectorized contents were added by executing a search query:

```
GET movies/_search
```

This will result in the movies with two additional fields consisting of the vectorized content, as shown in the image below:

![Movie with Vectors](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7497998eeeff8e12/6a17d9e20b0bed104add3451/3ceb62e92adf95f22d54aa04862dd5cc91f482ab-1440x644.jpg)

Now that we have indexed the documents, let's jump searching through these using the kNN search feature.

### kNN search

The k-Nearest Neighbors search in Elasticsearch fetches vectors (documents) that are closest to the given (query) vector. Elasticsearch supports two types of kNN search:

* Approximate kNN search
* Brute Force (or Exact) KNN Search

While both searches produce the results, brute force finds the accurate results at a cost of maximum resource utilization and time to query. Approximate kNN is good enough for the majority of search cases as it offers near accurate results.

Elasticsearch provides `knn` query for approximate search while we should be using `script_score` query for exact kNN search.

### Approximate search

Let's run an approximate search on the movies as shown below. Elasticsearch provides a kNN query with a `query_build_vector` block which consists of our query requirements. Let's write the code snippet first and discuss its constituents afterward:

```
GET movies/_search
{
  "knn": {
    "field": "title_vector.predicted_value",
    "query_vector_builder": {
      "text_embedding": {
        "model_id": ".multilingual-e5-small",
        "model_text": "Good"
      }
    },
    "k": 3,
    "num_candidates": 100
  },
  "_source": [
    "id",
    "title"
  ]
}
```

The traditional search queries support the `query` function, however, Elasticsearch introduced `knn` search function as a first class citizen to query vectors.

The `knn` block consists of a field we are searching against - in this instance, it is the title vector - the `title_vector.predicted_value` field. Remember, this is the name of the field we had mentioned in the mapping earlier.

The `query_vector_builder` is where we need to provide our query along with the model that we need to use to embed the query. In this case, we set `multilingual-e5-small` as our model and the text is simply "Good". The query in question will be vectorized by Elasticsearch using the text embedding model (multilingual-e5-small). It then compares the vector query against the available title vectors.

The `k` value indicates how many documents need to be brought back as a result.

This query should get us the top three documents:

```
"hits": [
      {
        "_index": "movies",
        "_id": "ZADvgo4BDf-WoG_MTka1",
        "_score": 0.92932993,
        "_source": {
          "title": "The Good, The Bad and The Ugly"
        }
      },
      {
        "_index": "movies",
        "_id": "uJ3wgo4BMlgFmHKKtFSp",
        "_score": 0.91828954,
        "_source": {
          "title": "A Few Good Men"
        }
      },
      {
        "_index": "movies",
        "_id": "tp15fY4BMlgFmHKK6VRV",
        "_score": 0.90952975,
        "_source": {
          "title": "The Godfather"
        }
      }
    ]
```

The top movie scored was "The Good, The Bad and the Ugly" when we searched for "Good" against the titles. Do note that kNN search yields results always even if the resultant movies are not a match - the inherent characteristic of a kNN match.

Take note of the relevancy score (`_score`) for each of the documents - as expected the documents are sorted based on this score.

### Searching with multiple kNN fields

We have two vector fields - the `title_vector` and `synopsis_vector` fields in the movie document - we can surely search against these two fields and expect the resultant documents based on the combined scores.

Let's just say we want to search for "Good" in the title but "orders" in the `synopsis` field. Remember from the previous single title-field search using "Good", we retrieved the "The Good, The Bad and the Ugly" movie. Let's see which movie will be fetched given the "orders" part of the synopsis as our search.

The following code declares our multi-kNN field search:

```
POST movies/_search
{
  "knn":[
    {
     "field": "title_vector.predicted_value",
     "query_vector_builder": {
      "text_embedding": {
        "model_id": ".multilingual-e5-small",
        "model_text": "Good"
      }
    },
     "k": 3,
     "num_candidates": 100
    },
    {
     "field": "synopsis_vector.predicted_value",
     "query_vector_builder": {
      "text_embedding": {
        "model_id": ".multilingual-e5-small",
        "model_text": "orders"
      }
     },
     "k": 3,
     "num_candidates": 100
    }
  ]
}
```

As you can imagine, the `knn` query can accept multiple search fields as an array - here we provided search criteria from both fields. The answer is "A Few Good Men" as the synopsis vector that consists the "order" vector was this movie.

## When to search with multi-kNN fields

There are a few instances where we can be searching using multiple kNN fields:

* Searching for "tweets" based on image similarity (visual kNN field) and a tweet similarity (text kNN field).
* Recommend similar songs based on both audio features (audio as the kNN field) like tempo and rhythm; And probably title/artist/genre information (text kNN field).
* Recommend movies or products based on the user's behavior (kNN field for user interactions) and movie/product attributes (kNN field based on these attributes).

## Conclusion

That's a wrap. In this article, we looked at the mechanics of kNN search and how we can find the closest document when we have multiple vectorized fields.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter