---
title: 'The sparse vector query: Searching sparse vectors with inference or precomputed query vectors'
company: Elastic
tag: 召回
date: 2024-07-23
url: https://www.elastic.co/search-labs/blog/elasticsearch-sparse-vector-query
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# The sparse vector query: Searching sparse vectors with inference or precomputed query vectors

Learn about the Elasticsearch sparse vector query, how it works, and how to effectively use it.

July 23, 2024

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Sparse vector queries take advantage of Elasticsearch’s powerful [inference API](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html), allowing easy built-in setup for Elastic-hosted models such as [ELSER](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-elser.html) and [E5](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-e5.html), as well as the [flexibility](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-inference.html) to host other models.

## Background

Vector search is evolving, and as our needs for vector search evolve so does the need for a consistent and forward thinking vector search API.

When Elastic first launched semantic search, we leveraged existing [rank\_features](https://www.elastic.co/guide/en/elasticsearch/reference/current/rank-features.html) fields using the [text\_expansion](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-text-expansion-query.html) query. We then reintroduced the [sparse\_vector field type](https://www.elastic.co/guide/en/elasticsearch/reference/current/sparse-vector.html) for semantic search use cases.

As we think about what sparse vector search is going forward, we’ve introduced a new sparse vector query. As of Elasticsearch 8.15.0, both the text\_expansion query and [weighted\_tokens](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-weighted-tokens-query.html) query have been deprecated in favor of the new sparse vector query.

The sparse vector query supports two modes of querying: using an inference ID and using precomputed query vectors. Both modes of querying require data to be indexed in a sparse\_vector mapped field.

These token-weight pairs are then used in a query against a sparse vector. At query time, query vectors are calculated using the same inference model that was used to create the tokens.

Let’s look at an example: let’s say we’ve indexed a document detailing when Orion is most visible in the night sky:

![Indexing sparse vectors encoding example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltecb4be95e0c08699/6a17d72225daabcc8908a09a/8c7b9a7fa9db92e2e8067d5c84854940bf037062-1440x320.png)

Now, assume we’re looking for constellations that are visible in the northern hemisphere, and we run this query through the same learned sparse encoder model. The output might look similar to this:

![Searching sparse vectors encoding example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3683b4b6d0d85683/6a17d724505ac32a60ad8950/54561b412a1c1f57157290a339dfe387c2f95dad-1440x424.png)

At query time, these vectors are ORed together, and scoring is effectively a [dot product](https://en.wikipedia.org/wiki/Dot_product) calculation between the stored dimensions and the query dimensions, which would score this example at 10.84:

![Dot product scoring example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt03108313e79d6e7d/6a17d725a29299397cd02ae1/53baae570e66ebc66f0fa47b406436e2c22b3162-816x452.png)

## Sparse vector queries with inference

Sparse vector queries using inference work in a very similar way to the previous text expansion query, instead of sending in a trained model, we [create an inference endpoint](https://www.elastic.co/guide/en/elasticsearch/reference/current/put-inference-api.html) associated with the model we want to use.

Here’s an example of how to create an inference endpoint for ELSER:

```
PUT _inference/sparse_embedding/my-elser-endpoint
{
  "service": "elser",
  "service_settings": {
    "num_allocations": 1,
    "num_threads": 1
  }
}
```

You should use an inference endpoint to index your sparse vector data, and use the same endpoint as input to your sparse\_vector query. For example:

```
POST my-index/_search
{
  "query": {
    "sparse_vector": {
      "field": "embeddings",
      "inference_id": "my-elser-endpoint",
      "query": "constellations in the northern hemisphere"
    }
  }
}
```

## Sparse vector queries with precomputed query vectors

You may have precomputed vectors that don’t require inference at query time. These can be sent into the sparse\_vector query instead of using inference. Here is an example:

```
POST my-index/_search
{
  "query": {
    "sparse_vector": {
      "field": "embeddings",
      "query_vector": {
        "constellation": 2.5,
        "northern": 1.9,
        "hemisphere": 1.8,
        "orion": 1.5,
        "galaxy": 1.4,
        "astronomy": 0.9,
        "telescope": 0.3,
        "star": 0.01
      }
    }
  }
}
```

## Query optimization with token pruning

Like text expansion search, the sparse vector query is subject to performance penalties from huge boolean queries. Therefore the same [token pruning strategies](https://www.elastic.co/search-labs/blog/text-expansion-pruning) available for text expansion strategies are available in the sparse vector query. You can see the impact of token pruning in our [nightly MS Marco Passage Ranking benchmarks](https://elasticsearch-benchmarks.elastic.co/index.html#tracks/msmarco-passage-ranking/nightly/default/90d).

In order to enable pruning with the default pruning configuration (which has been tuned for ELSER V2), simply add `prune: true` to your request:

```
POST my-index/_search
{
  "query": {
    "sparse_vector": {
      "field": "embeddings",
      "inference_id": "my-elser-endpoint",
      "query": "constellations in the northern hemisphere",
      "prune": true
    }
  }
}
```

Alternately, you can adjust the pruning configuration by sending it directly in with the request:

```
GET my-index/_search
{
   "query":{
      "sparse_vector":{
         "field": "embeddings",
         "inference_id": "my-elser-endpoint",
         "query": "constellations in the northern hemisphere",
         "prune": true,
         "pruning_config": {
           "tokens_freq_ratio_threshold": 5,
           "tokens_weight_threshold": 0.4,
           "only_score_pruned_tokens": false
         }
      }
   }
}
```

Because token pruning will incur a recall penalty, we recommend adding the pruned tokens back in a rescore:

```
GET my-index/_search
{
   "query":{
      "sparse_vector":{
         "field": "embeddings",
         "inference_id": "my-elser-endpoint",
         "query": "constellations in the northern hemisphere",
         "prune": true,
         "pruning_config": {
           "tokens_freq_ratio_threshold": 5,
           "tokens_weight_threshold": 0.4,
           "only_score_pruned_tokens": false
         }
      }
   },
   "rescore": {
      "window_size": 100,
      "query": {
         "rescore_query": {
            "sparse_vector": {
               "field": "embeddings",
               "inference_id": "my-elser-endpoint",
               "query": "constellations in the northern hemisphere",
               "prune": true,
               "pruning_config": {
                   "tokens_freq_ratio_threshold": 5,
                   "tokens_weight_threshold": 0.4,
                   "only_score_pruned_tokens": true
               }
            }
         }
      }
   }
}
```

## What's next?

While the `text_expansion` query is GA’d and will be supported throughout Elasticsearch 8.x, we recommend updating to the `sparse_vector` query as soon as possible in order to ensure you’re using the most up to date features as we continually improve the vector search experience in Elasticsearch.

If you are using the `weighted_tokens` query, this was never GA’d and will be replaced by the sparse\_vector query very soon.

The `sparse_vector` query will be available starting with 8.15.0 and is already available in Serverless - try it out today!

### Frequently Asked Questions

#### What are sparse vector queries in Elasticsearch?

Sparse vector queries take advantage of Elasticsearch’s powerful inference API, allowing easy built-in setup for Elastic-hosted models such as ELSER and E5, as well as the flexibility to host other models.

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