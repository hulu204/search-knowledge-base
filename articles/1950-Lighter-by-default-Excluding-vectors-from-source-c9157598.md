---
title: 'Lighter by default: Excluding vectors from source'
company: Elastic
tag: 索引构建
date: 2025-08-26
url: https://www.elastic.co/search-labs/blog/elasticsearch-exclude-vectors-from-source
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Lighter by default: Excluding vectors from source

Elasticsearch now excludes vectors from source by default, saving space and improving performance while keeping vectors accessible when needed.

August 26, 2025

[Jim Ferenczi](/search-labs/author/jim-ferenczi)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

We’re updating how Elasticsearch stores vector fields like `dense_vector`, `sparse_vector`, and `rank_vector`. Now, in **Serverless** and coming in **v9.2**, **vector fields will be excluded from** `_source` **by default** for newly created indices.

This change reduces storage overhead out of the box, improves indexing performance, and aligns Elasticsearch’s behavior with what users expect from a modern vector search engine.

## Why change the default?

Until now, Elasticsearch has stored vectors in both `doc_values` (used for similarity search) and `_source` (used for retrieval). However, most vector workloads don’t need the original vector in the search response—just the top-k results and a few metadata fields.

Storing large vectors twice is wasteful. It increases index size, slows down indexing, and inflates search responses. In most cases, users don’t even realize they’re retrieving multi-kilobyte vectors per document.

This change avoids that duplication while preserving Elasticsearch’s strength: fast access to structured metadata stored in `_source`, such as titles and URLs.

## A rare but necessary change

We don’t typically make breaking changes in minor versions or in Serverless environments. But in this case, we are confident that the benefits far outweigh the disruption.

We’ve seen many users hit performance issues or bloated responses due to vectors being stored and returned by default. Instead of requiring extra configuration, we’re making the efficient path the default:

```
"index.mapping.exclude_source_vectors": true
```

This setting is now **enabled by default for all newly created indices** whether you're using Elasticsearch in Serverless, ESS, or self-managed deployments.

**Existing indices are unaffected**. For any index created prior to this change, the setting remains `false`, and vector fields will continue to be stored and returned in `_source` as before.

## Rehydration: it just works

**Rehydration** means Elasticsearch can add the indexed vector back into `_source` when needed, even if it’s not stored there. This happens automatically for:

* **Partial updates**
* **Reindex**
* **Recovery**

These workflows continue to work seamlessly, even though the vector is no longer physically stored in \_source.

You can also trigger it manually in a search request using the `_source` option (see below).

## Precision trade-offs

Elasticsearch stores vectors internally as 32-bit floats, which is the format used during indexing and similarity search. However, vectors may be provided in JSON as higher-precision types like `double` or even `long`.

When `_source` no longer stores the original input, any rehydrated vector will reflect the **float** representation used for indexing. In nearly all use cases, this is what matters for search and scoring.

But if you need to preserve the **exact input precision**—for example, when you must retrieve the original `double` values instead of the indexed 32-bit floats—you must disable the setting at index creation time:

```
"index.mapping.exclude_source_vectors": false
```

This ensures the original vector values are preserved in the original `_source` on disk.

## Accessing vector fields when needed

If your application needs vector values in search responses, you can retrieve them explicitly.

* Use the `fields` option:

```
POST my-index/_search
{
  "fields": ["my_vector"]
}
```

Returns the indexed vector field alongside hits, outside of `_source`.

* Re-enable vector inclusion in `_source`:

```
POST my-index/_search
{
  "_source": {
    "exclude_vectors": false
  }
}
```

This option rehydrates the indexed version of the vector fields back into `_source` for that response.

## What’s the impact?

We benchmarked this change using the [OpenAI Vector Rally track](https://github.com/elastic/rally-tracks/tree/master/openai_vector).

The standout result:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte71795d543725df7/6a17ea04ec0f8985995a6670/6200bde499a4cdbdbdcc629ce0ba6fd3db50370b-1247x980.png)

Impact of excluding vectors from \_source.

This leads to:

* Faster indexing
* Less disk I/O
* Reduced resource usage

Especially in high-volume vector workloads.

## Final thoughts

Elasticsearch is a full-featured vector search engine, and we are committed to ensuring it works well by default. This change removes inefficiencies that most users didn’t even know were there while preserving all functionality.

You still get fast metadata access via `_source`, seamless behavior for updates and recovery, and the ability to opt in to returning vector values when needed. If preserving the original vector exactly matters, that flexibility is still supported, you just need to opt in.

For most users, things just work better out of the box.

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