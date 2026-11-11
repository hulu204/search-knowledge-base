---
title: 'Semantic search with GPU inference in Elastic'
company: Elastic
tag: 工程相关
date: 2025-10-23
url: https://www.elastic.co/search-labs/blog/gpu-inference-elastic-semantic-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Semantic search with GPU inference in Elastic

Learn how Elastic's EIS leverages GPU inference and ELSER to power fast, accurate semantic search.

October 23, 2025

[Sean Handley](/search-labs/author/sean-handley)[Max Jakob](/search-labs/author/max-jakob)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Our inference tooling at Elastic has had some major power-ups this year with the introduction of our [GPU-powered Elastic Inference Service](https://www.elastic.co/blog/elastic-inference-service) (EIS), providing a platform for streamlined access to LLMs, embeddings, and reranker models via an always-on dedicated service.

Today, we’ll focus on how EIS can simplify the semantic search experience with our sparse embeddings model, ELSER (Elastic Learned Sparse EncodeR). Having semantic search in place as a foundation can help to unlock many additional abilities, including hybrid retrieval and being able to [provide great context to LLMs for your agentic workflows](https://www.elastic.co/search-labs/blog/elastic-ai-agent-builder-context-engineering-introduction).

Let’s get started!

## Getting started with semantic search

You can now get started with your end-to-end semantic search use cases with the inference endpoints powered by EIS.

### 1. Create a semantic text field using the new endpoint

First, let’s create a new index using the `semantic_text` field type and the EIS inference id `.elser-2-elastic`.

```
PUT semantic-embeddings
{
 "mappings": {
   "properties": {
     "content": {
       "type": "semantic_text",
       "inference_id": ".elser-2-elastic"
     }
   }
 }
}
```

This sets up an index called `semantic-embeddings` where the content field automatically generates embeddings using the `.elser-2-elastic` inference endpoint.

In future versions, this inference id will be the default, so you won’t need to specify it explicitly.

### 2. Reindex your data

Next, let’s reindex an existing text index that contains national parks data so it can use the new `semantic_text` field via the index we just created.

This is a necessary step if you want to bring in existing data to an EIS-powered index, but will be simplified further in our next release to allow you to update an existing index mapping without reindexing.

```
POST _reindex?wait_for_completion=false
{
 "source": {
   "index": "bm25-based-index",
   "size": 100
 },
 "dest": {
   "index": "semantic-embeddings"
 }
}
```

### 3. Search

Finally, let’s query the index for information about national parks via semantic search.

```
GET semantic-embeddings/_search
{
 "query": {
   "semantic": {
     "field": "content",
     "query": "Which park is most popular?"
   }
 }
}
```

And the response:

```
{
 "took": 168,
 "timed_out": false,
 "_shards": {
   "total": 3,
   "successful": 3,
   "skipped": 0,
   "failed": 0
 },
 "hits": {
   "total": {
     "value": 3,
     "relation": "eq"
   },
   "max_score": 17.655077,
   "hits": [
     {
       "_index": "semantic-embeddings",
       "_id": "ldJ9C5oBYmL2EI9TGdMP",
       "_score": 17.655077,
       "_source": {
         "text": "Rocky Mountain National Park  is one of the most popular national parks in the United States. It receives over 4.5 million visitors annually, and is known for its mountainous terrain, including Longs Peak, which is the highest peak in the park. The park is home to a variety of wildlife, including elk, mule deer, moose, and bighorn sheep. The park is also home to a variety of ecosystems, including montane, subalpine, and alpine tundra. The park is a popular destination for hiking, camping, and wildlife viewing, and is a UNESCO World Heritage Site."
       }
     },
     {
       "_index": "semantic-embeddings",
       "_id": "k9J9C5oBYmL2EI9TGdMP",
       "_score": 12.741274,
       "_source": {
         "text": "Yellowstone National Park is one of the largest national parks in the United States. It ranges from the Wyoming to Montana and Idaho, and contains an area of 2,219,791 acress across three different states. Its most famous for hosting the geyser Old Faithful and is centered on the Yellowstone Caldera, the largest super volcano on the American continent. Yellowstone is host to hundreds of species of animal, many of which are endangered or threatened. Most notably, it contains free-ranging herds of bison and elk, alongside bears, cougars and wolves. The national park receives over 4.5 million visitors annually and is a UNESCO World Heritage Site."
       }
     },
     {
       "_index": "semantic-embeddings",
       "_id": "lNJ9C5oBYmL2EI9TGdMP",
       "_score": 11.813252,
       "_source": {
         "text": "Yosemite National Park is a United States National Park, covering over 750,000 acres of land in California. A UNESCO World Heritage Site, the park is best known for its granite cliffs, waterfalls and giant sequoia trees. Yosemite hosts over four million visitors in most years, with a peak of five million visitors in 2016. The park is home to a diverse range of wildlife, including mule deer, black bears, and the endangered Sierra Nevada bighorn sheep. The park has 1,200 square miles of wilderness, and is a popular destination for rock climbers, with over 3,000 feet of vertical granite to climb. Its most famous and cliff is the El Capitan, a 3,000 feet monolith along its tallest face."
       }
     }
   ]
 }
}
```

And that’s all you need to do! With an EIS-powered semantic search index you get superior ingest performance, easy token-based pricing, and a service that’s available when you need it.

For a detailed example and tutorial, please refer to the Elastic [docs](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis) for ELSER on EIS and the [tutorial](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text).

## So how does this work?

The [Elastic Inference Service](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis) runs on Elastic’s infrastructure, providing access to machine-learning models on demand.

The team used [Ray](https://www.ray.io/) to build out the service, specifically using the [Ray Serve](https://docs.ray.io/en/latest/serve/index.html) libraries to run our machine learning models. This runs on top of Kubernetes and uses pools of NVIDIA GPUs in the Elastic Cloud Platform to perform the model inference operations.

Ray gives us a lot of great benefits:

* It works out of the box with [PyTorch](https://pytorch.org/), [Tensorflow](https://www.tensorflow.org/), and other ML libraries;
* It’s Python-native and supports custom business logic, allowing easy integration with models in the Python ecosystem;
* It’s robust and works across heterogeneous GPU pools, allowing fractional resource management;
* It supports response streaming, dynamic batching, and plenty of other useful features.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt91e8b430f49f5bf1/6a17ef6c1480092116b48819/a8cf3b5364acffca1ecd355f749cb648c7956ea4-1210x777.png)

When an inference API request comes in for semantic search, we have the ELSER model up and running and ready to generate your sparse embeddings. Running on GPUs allows us to efficiently parallelise operations, which is particularly helpful if you have a lot of documents you need to ingest regularly.

## What’s next?

In future versions of Elastic, ELSER via EIS will be the default semantic text setting, so you won’t even have to specify the inference id when you create the semantic index. We’ll be adding the ability to change an index to use semantic search via EIS without needing to do any reindexing. Finally, and most excitingly, we’ll be adding new models to support reranking and [Jina’s multilingual and multimodal embedding models](https://www.elastic.co/blog/elastic-jina-ai).

Stay tuned for future blog posts with further technical details of how the service works and more news about models and features!

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter