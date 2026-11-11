---
title: 'Semantic text in Elasticsearch: Simpler, better, leaner, stronger'
company: Elastic
tag: 索引构建
date: 2025-03-13
url: https://www.elastic.co/search-labs/blog/elasticsearch-semantic-text-ga
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Semantic text in Elasticsearch: Simpler, better, leaner, stronger

Our latest semantic\_text iteration brings a host of improvements. In addition to streamlining representation in \_source, benefits include reduced verbosity, more efficient disk utilization, and better integration with other Elasticsearch features. You can now use highlighting to retrieve the chunks most relevant to your query. And perhaps best of all, it is now a generally available (GA) feature!

March 13, 2025

[Mike Pellegrini](/search-labs/author/mike-pellegrini)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

We’ve gone on quite a journey with the `semantic_text` field type, and this latest iteration promises to make semantic search simpler than ever. In addition to streamlining `semantic_text` representation in `_source`, benefits include reduced verbosity, more efficient disk utilization, and better integration with other Elasticsearch features. You can now use highlighting to retrieve the chunks most relevant to your query. And perhaps best of all, it is now a generally available (GA) feature!

## Semantic search evolution

Our approach to semantic search has evolved over the years, with the goal of making it as simple as possible. Prior to the `semantic_text` field type, performing semantic search required manually:

* Configuring your mappings to be compatible with your embeddings.
* Configuring an ingest pipeline to use a ML model to generate embeddings.
* Using the pipeline to ingest your docs.
* Using the same ML model at query time to generate embeddings for your query text.

[We called this setup “easy” at the time](https://www.elastic.co/search-labs/blog/chunking-via-ingest-pipelines), but we knew we could make it far simpler than this. Enter `semantic_text`.

## Semantic text in the beginning

We introduced `semantic_text` in Elasticsearch 8.15 with the goal of simplifying semantic search. If `semantic_text` is new to you, we suggest reading our [original blog post about it](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text) first for background about our approach.

We released `semantic_text` as a beta feature first for a good reason. It’s a well-known truism in software development that making something simple can be quite difficult, and `semantic_text` is no exception. There are a lot of moving pieces behind the scenes that enable the magical `semantic_text` experience. We wanted to take the time to make sure we had those pieces right before moving the feature out of beta. That time was well spent: We iterated on our original approach, adding features and streamlining storage to create a simpler, leaner version of `semantic_text` that is more supportable in the long-term.

Our original implementation relied on modifying `_source` to store inference results. This meant that `semantic_text` fields had a relatively complex subfield structure:

```
GET test-index/_doc/doc1
{
  "_index": "test-sparse",
  "_id": "doc1",
  "_source": {
    "infer_field": {
      "text": "these are not the droids you're looking for. He's free to go around",
      "inference": {
        "inference_id": "my-elser-endpoint",
        "model_settings": {
          "task_type": "sparse_embedding"
        },
        "chunks": [
          {
            "text": "these are not the droids you're looking for. He's free to go around",
            "embeddings": {
              "##oid": 1.9103845,
              "##oids": 1.768872,
              "free": 1.693662,
              "dr": 1.6103356,
              "around": 1.4376559,
              "these": 1.1396849

              …
            }
          }
        ]
      }
    }
  }
}
```

This structure created a few problems:

* It was needlessly verbose. In addition to the original value, it contained metadata and chunk information, which made API responses hard to read and larger than necessary.
* It increased index sizes on disk. Embeddings, which can be quite large, were effectively being stored twice: once in the Lucene index for retrieval purposes and again in `_source`. This significantly impacted the ability to use `semantic_text` at scale for larger datasets.
* It was unintuitive to manage. The original value provided was under the `text` subfield, which meant special handling was required to get this value for follow-up actions. This meant that `semantic_text` field values didn’t act like other field values in the `text` family, which had numerous knock-on effects that complicated our efforts to integrate it into higher-level workflows.

## Semantic text as text

Our revised implementation elegantly improves on those friction points with a focused simplification in approach to how we represent `semantic_text` in `_source`. Instead of using a complex subfield structure to store metadata and chunk information directly within the `semantic_text` field, we use a hidden [metafield](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-fields.html) for this purpose. This means we no longer need to modify `_source` to store inference results. In practical terms, it means that the document `_source` that you provide to us for indexing is the same `_source` that you will get back upon document retrieval.

```
GET test-index/_doc/doc1
{
  "_index": "test-sparse",
  "_id": "doc1",
  "_source": {
    "infer_field": "these are not the droids you're looking for. He's free to go around"
  }
}
```

Notice that there are no longer subfields like `text` or `inference` in the `_source` representation. Instead, the `_source` is as you provided it. So much simpler!

**🚨 Note that if you parse** `semantic_text` **field values returned in search results or** [**Get APIs**](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-get.html)**, this is a breaking change.** That is to say, if you parse the `infer_field.text` subfield value, you will need to update your code to instead parse the `infer_field` value. We try our best to avoid breaking changes, but this was an unavoidable side-effect of removing the subfield structure from `_source`.

There are numerous benefits to this `_source` representation simplification:

* **Simpler to work with.** You no longer need to parse a complex subfield structure to get the original text value, you can just take the field value as the original value.
* **Less verbose.** Metadata and chunk information does not clutter up API responses.
* **More efficient disk utilization.** Embeddings are no longer stored in `_source`.
* **Better integration.** It allows `semantic_text` to integrate better with other Elasticsearch features, such as multi-fields, partial document updates, and reindexing.

Let’s expand on that last point a bit because it covers a few areas. With this simplification, `semantic_text` fields can now be used as the source and target of [multi-fields](https://www.elastic.co/guide/en/elasticsearch/reference/current/multi-fields.html):

```
PUT multi-field-source-example-index
{
  "mappings": {
    "properties": {
      "inference": {
        "type": "semantic_text",
        "fields": {
          "text": {
            "type": "text"
           }
        }
      }
    }
  }
}

PUT multi-field-target-example-index
{
  "mappings": {
    "properties": {
      "text": {
        "type": "text",
        "fields": {
          "inference": {
            "type": "semantic_text"
           }
        }
      }
    }
  }
}
```

`Semantic_text` fields now also support partial document updates through the [Bulk API](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html):

```
PUT partial-update-example-index
{
  "mappings": {
    "properties": {
      "inference": {
        "type": "semantic_text"
      },
      "source_field": {
        "type": "text",
        "copy_to": "inference"
      }
    }
  }
}

POST my-index/_doc/1
{
  "inference": "a test value",
  "source_field": "another test value"
}

POST my-index/_bulk
{ "update": {"_id": "1"} }
{ "doc": {"source_field": "a different test value"} }
```

And you can now reindex into a `semantic_text` field that uses a different `inference_id`:

```
PUT source-index
{
  "mappings": {
    "properties": {
      "inference": {
        "type": "semantic_text",
        "inference_id": "my-elser-endpoint"
      }
    }
  }
}

PUT dest-index
{
  "mappings": {
    "properties": {
      "inference": {
        "type": "semantic_text",
        "inference_id": "my-e5-endpoint"
      }
    }
  }
}

POST dest-index/_doc/1
{
  "inference": "a test value"
}

POST _reindex
{
  "source": {
    "index": "source-index"
  },
  "dest": {
    "index": "dest-index"
  }
}
```

## Semantic highlighting

One of the most requested `semantic_text` features is the ability to retrieve the most relevant chunks within a `semantic_text` field. This functionality is critical for RAG use cases. Up until now, we have (unofficially) accommodated this with some hacky workarounds involving `inner_hits`. However, we are retiring `inner_hits` in favor of a more streamlined solution: highlighting.

Highlighting is a well-known lexical search technique one can apply to `text` fields. As a member of the `text` field family, it only makes sense to adapt the technique for `semantic_text`. To this end, we have added a `semantic` highlighter that you can use to retrieve the chunks that are most relevant to your query:

```
PUT highlighting-index
{
  "mappings": {
    "properties": {
      "inference": {
        "type": "semantic_text"
      }
    }
  }
}

POST highlighting-index/_doc/1
{
  "inference": ["Yosemite is one of the most popular national parks in the USA", "Park visitors should dispose of their trash properly in bear-proof trash bins to avoid attracting bears", "Bears are quite clever and curious though, so visitors should always be on the lookout for bear activity regardless"]
}

GET highlighting-index/_search
{
  "query": {
    "semantic": {
      "field": "inference",
      "query": "Where should I throw away my trash?"
    }
  },
  "highlight": {
    "fields": {
      "inference": {
        "order": "score",
        "number_of_fragments": 1
      }
    }
  }
}

{
    "took": 6,
    "timed_out": false,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 15.898441,
        "hits": [
            {
                "_index": "highlighting-index",
                "_id": "1",
                "_score": 15.898441,
                "_source": {
                    "inference": [
                        "Yosemite is one of the most popular national parks in the USA",
                        "Park visitors should dispose of their trash properly in bear-proof trash bins to avoid attracting bears",
                        "Bears are quite clever and curious though, so visitors should always be on the lookout for bear activity regardless"
                    ]
                },
                "highlight": {
                    "inference": [
                        "Park visitors should dispose of their trash properly in bear-proof trash bins to avoid attracting bears"
                    ]
                }
            }
        ]
    }
}

GET highlighting-index/_search
{
  "query": {
    "semantic": {
      "field": "inference",
      "query": "Are bears smart?"
    }
  },
  "highlight": {
    "fields": {
      "inference": {
        "order": "score",
        "number_of_fragments": 1
      }
    }
  }
}

{
    "took": 20,
    "timed_out": false,
    "_shards": {
        "total": 1,
        "successful": 1,
        "skipped": 0,
        "failed": 0
    },
    "hits": {
        "total": {
            "value": 1,
            "relation": "eq"
        },
        "max_score": 18.584934,
        "hits": [
            {
                "_index": "highlighting-index",
                "_id": "1",
                "_score": 18.584934,
                "_source": {
                    "inference": [
                        "Yosemite is one of the most popular national parks in the USA",
                        "Park visitors should dispose of their trash properly in bear-proof trash bins to avoid attracting bears",
                        "Bears are quite clever and curious though, so visitors should always be on the lookout for bear activity regardless"
                    ]
                },
                "highlight": {
                    "inference": [
                        "Bears are quite clever and curious though, so visitors should always be on the lookout for bear activity regardless"
                    ]
                }
            }
        ]
    }
}
```

See the [semantic\_text documentation](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/semantic-text.html#semantic-text-highlighting) for more information about how to use highlighting.

## Ready for primetime: semantic\_text is GA

With the `_source` representation change in place, we are now officially announcing that `semantic_text` is a generally available (GA) feature 🎉! This means that we are committed to not making any more breaking changes to the feature and supporting it in production environments. As a customer, you should feel comfortable integrating `semantic_text` into your production workflows knowing that Elastic is committed to supporting you and providing long-term continuity.

## Migrating from beta

To enable an orderly migration from the beta implementation, all indices with `semantic_text` fields created in Elasticsearch 8.15 to 8.17 or created in Serverless prior to January 30th will continue to operate as they do today. That is to say, they will continue to use [the beta \_source representation](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text#under-the-hood:-how-). We recommend migrating to the GA `_source` representation at your earliest convenience. You can do so by [reindexing](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-reindex.html) into a new index:

```
PUT my-new-index
{
  "mappings": {
    "properties": {
      "inference": {
        "type": "semantic_text"
      }
    }
  }
}

POST _reindex
{
  "source": {
    "index": "my-old-index"
  },
  "dest": {
    "index": "my-new-index"
  },
  "script": {
    "source": "ctx._source.inference = ctx._source.inference.text"
  }
}
```

Note the use of the `script` param to account for the `_source` representation change. The script is taking the value from the `text` subfield and assigning it directly to the `semantic_text` field value.

## Try semantic text

These changes will be available in stack hosted Elasticsearch 8.18+, but if you want to try them today, they are already available in Serverless. They also pair well with [semantic search simplifications](https://www.elastic.co/search-labs/blog/semantic-search-match-knn-sparse-vector) we are rolling out at the same time. Use both to take semantic search to the next level!

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