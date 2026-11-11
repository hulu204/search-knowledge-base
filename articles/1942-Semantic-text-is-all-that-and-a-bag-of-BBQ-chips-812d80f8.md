---
title: 'Semantic text is all that and a bag of (BBQ) chips! With configurable chunking settings and index options'
company: Elastic
tag: 索引构建
date: 2025-07-09
url: https://www.elastic.co/search-labs/blog/semantic-text-chunking-index-options
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Semantic text is all that and a bag of (BBQ) chips! With configurable chunking settings and index options

Semantic text search is now customizable, with support for customizable chunking settings and index options to customize vector quantization, making semantic\_text more powerful for expert use cases.

July 09, 2025

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Relevance](/search-labs/blog/category/relevance)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

With the [general availability](https://www.elastic.co/search-labs/blog/semantic-text-ga) of `semantic_text` search in Elasticsearch 8.18 and 9.0, our focus has primarily centered on simplicity, enhancing speed and storage, and [broadening usability](https://www.elastic.co/search-labs/blog/semantic-search-match-knn-sparse-vector) to `match`, `knn` and `sparse_vector` queries. Now, it’s time to complete this story by offering additional customization for advanced and expert use cases. This includes specifying the [quantization method](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-quantization) to use for vectors (including customizing [BBQ](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch)) or configuring customizable [chunking settings](https://www.elastic.co/search-labs/blog/elasticsearch-chunking-inference-api-endpoints) to control how `semantic_text` breaks down long input into smaller pieces of data to send into inference models.

With this in mind, we have delivered additional features that allow finer control over both chunking settings and quantization configuration.

## Customizing chunking settings

When we [introduced](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text) `semantic_text`, one of the most powerful functionalities was that it handled chunking transparently for you, without any additional configuration at the field level. This was possible because each configured [inference endpoint](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-put) has chunking settings attached to it. When ingesting documents with `semantic_text`, long documents were automatically split into chunks based on that inference endpoint configuration.

While this default chunking configuration performs exceptionally well for most use cases, there are some use cases where more granular control over chunking is required. So, we introduced configurable chunking settings to `semantic_text` that, when set, will override the default behavior configured in the inference endpoint.

It’s easy to set this up through your mappings:

```
PUT my-index
{
  "mappings": {
    "properties": {
      "my_semantic_field": {
        "type": "semantic_text",
        "chunking_settings": {
          "strategy": "sentence",
          "max_chunk_size": 250,
          "sentence_overlap": 1
        }
      }
    }
  }
}
```

In this example, we are using a `sentence` based chunking strategy. This splits data into chunks that incorporate complete sentences, up to the length of `max_chunk_size`, which in this example is 250 words. We can also define a `sentence_overlap`, which can include the same sentence in multiple chunks. Additionally, we support word based chunking strategies, which split data by individual words rather than sentence boundaries, or `none` to completely disable chunking. This is useful if you perform chunking before sending data to Elasticsearch and want to preserve those chunks without further modification. More information on how chunking works can be found in our [documentation](https://www.elastic.co/docs/explore-analyze/elastic-inference/inference-api#infer-chunking-config) and in this search labs [blog](https://www.elastic.co/search-labs/blog/elasticsearch-chunking-inference-api-endpoints).

Since chunking settings are used at request time, you can update the chunking settings at any time via a mapping update command:

```
PUT my-index/_mapping
{
  "properties": {
    "my_semantic_field": {
      "type": "semantic_text",
      "chunking_settings": {
        "strategy": "word",
        "max_chunk_size": 250,
        "overlap": 100
      }
    }
  }
}
```

Please note, however, that as with any other [update to field mappings](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-put-mapping) in Elasticsearch, this will not impact already-indexed documents. If you decide to change your chunking configuration and want all of your documents to reflect the updated chunking settings, you will have to reindex those documents.

### “Bring your own chunks”

Another chunking configuration we’ve been asked for quite a bit is the ability to completely *disable* chunking in `semantic_text` fields, for users who want to apply their own chunking strategies before indexing documents into `semantic_text`. An example is if you have a model-based chunking strategy that splits Markdown or another type of data. In this scenario you would perform your chunking first, before you ingest content into Elasticsearch.

The good news is that this is now supported as well with the `none` chunking strategy:

```
PUT my-index
{
  "mappings": {
    "properties": {
      "my_semantic_field": {
        "type": "semantic_text",
        "chunking_settings": {
          "strategy": "none"
        }
      }
    }
  }
}
```

When using the `none` chunking strategy, you can index your pre-chunked data explicitly by sending in each chunk separately in an array:

```
PUT my-index/_doc/1
{
  "my_semantic_field": [
    "These aren't the droids you're looking for",
    "He's free to go around"
  ]
}
```

Providing pre-chunked input is an expert use case, and sizing your chunks based on the model’s token limit is important. Sending in chunks exceeding the model’s token limit may result in errors or document truncation, depending on the service and model used.

## BBQ and other quantization configuration

Traditionally, `semantic_text` has relied on good [default quantization strategies](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector) for text embedding models. This strategy gets an update in 8.19 and 9.1, where we will default new indices using `semantic_text` to our state-of-the-art [BBQ](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) HNSW quantization strategy for all compatible text embedding models. We’re confident that this is the right choice for most use cases because of how much better embedding models for text have been shown to perform using BBQ.

However, we realize that you may want to update these settings - maybe you’re not ready for BBQ, or you want to try out some even better improvements to quantization in the future. Well, we’ve got your back!

For text embedding models (dense vectors), we support setting these quantization index options using any [supported dense\_vector configuration](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-params). For example, here is a way to set an index to use `bbq_flat` (using a brute force search algorithm on top of binary quantization instead of the default HNSW strategy using BBQ):

```
PUT my-index
{
  "mappings": {
    "properties": {
      "my_semantic_field": {
        "type": "semantic_text",
        "inference_id": "my-text-embedding-model",
        "index_options": {
          "dense_vector": {
            "type": "bbq_flat"
           }
        }
      }
    }
  }
}
```

These `index_options` mappings are also updatable, provided that you are updating to a compatible quantization method.

## More coming soon

You may have noticed that the `index_options` API specifies `dense_vector` index options for quantization. In the future, we will support additional index options for more than just text embedding models, such as `sparse_vector`.

## Try it out yourself

With these exciting updates, semantic search in Elasticsearch using `semantic_text` is both easy to use out of the box and configurable for more expert use cases. These enhancements are native to Elasticsearch and will work with future improvements to both chunking and quantization, and are already available in Serverless! They’ll be available in stack-hosted Elasticsearch starting with version 8.19/9.1.

Try it out today!

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