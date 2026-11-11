---
title: 'Lance × DuckDB: SQL for Retrieval on the Multimodal Lakehouse Format'
company: LanceDB
tag: 工程相关
date: 2026-01-12
url: https://www.lancedb.com/blog/lance-x-duckdb-sql-retrieval-on-the-multimodal-lakehouse-format
account: 
origin: harvest3-202607
---
# Lance × DuckDB: SQL for Retrieval on the Multimodal Lakehouse Format

[Xuanwo](/author/xuanwo)

•

January 12, 2026

•

[Engineering](/category/engineering)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029ab0065f57b2bfaac29_lance-duckdb.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

The challenge with building efficient, scalable retrieval systems isn’t that teams are unable to build a vector index (that part is well understood) — it’s that the end-to-end workflow from a data management perspective is fragmented: embeddings live in one place, text and metadata in another, evaluation slices in a third, and the “analysis” layer is often a separate pipeline that requires copying data into yet another format.

[Lance](https://lance.org/) is an open lakehouse format for multimodal AI, built to address these challenges. The Lance format spans three layers of the lakehouse stack: it’s a file format, a table format, *and* a catalog spec. The goal is simple: to build a complete, open-source lakehouse format for multimodal data that can serve as the durable and scalable data plane for AI and ML.

Today, we’re happy to announce the new [Lance × DuckDB extension](https://github.com/lance-format/lance-duckdb). This makes it *much* easier to use Lance as the lakehouse layer for retrieval and RAG by bringing Lance into DuckDB natively. With this extension, you can query, scan, and write Lance datasets directly from SQL. You can run vector search, full-text search, and hybrid search as SQL table functions, and then immediately join, aggregate, debug, and materialize results *without leaving DuckDB*.

**💡 Here’s a TL;DR if you want a quick mental model of what we cover in this post:**

* Lance is the open lakehouse format for multimodal AI (data plane).
* DuckDB is a portable SQL query engine (compute plane).
* The extension makes search and retrieval feel like regular SQL operators on top of your multimodal lakehouse datasets.

## Why this matters for Retrieval & AI teams

#### Treat Lance as the open lakehouse layer for multimodal AI

Lance’s design intentionally spans the file, table, and catalog spec layers of the lakehouse stack. This separation of concerns matters: your underlying data stays stable within the file format (compute engines may come and go) — and you can keep your multimodal datasets and embeddings where they already live (object storage), using the table and catalog layers, without rebuilding a new storage stack every time you change your compute engine.

#### Put retrieval inside the lakehouse, and inside SQL

Lance’s larger goal is to provide hybrid search plus analytics on the same dataset. DuckDB’s vision is to provide developers a familiar SQL interface for all their workflows. The Lance × DuckDB extension makes that combination practical by exposing retrieval operators as table functions in SQL, allowing direct scans of `.lance` datasets by path.

#### Make iteration loops faster: retrieve → analyze → materialize 🔁 repeat

These days, most teams building retrieval systems for RAG and agents need to:

* Add features and labels over time
* Slice and evaluate data repeatedly
* Save reproducible top-k subsets and hard negatives

DuckDB gives you the **analysis surface**. Lance gives you a durable **dataset format** to store and manage those artifacts right next to the source data.

## What you get by using the Lance × DuckDB extension

Let’s briefly list the standout features of the extension before going into a 5-minute quickstart below.

1. **Direct scanning of Lance datasets**: After installing and loading the extension, DuckDB can query a Lance dataset by pointing SQL at a **`.lance`** path.
2. **Retrieval operators as SQL table functions**: The extension adds SQL-friendly table functions for retrieval that operate natively on the Lance table underneath: **`lance_vector_search`**, **`lance_fts`** and **`lance_hybrid_search`**, for vector search, full-text search, and hybrid search, respectively. All these functions **push down work into Lance**, so you get all the benefits of fast retrieval while writing SQL.
3. **Organize your datasets with namespaces**: When you **`ATTACH`** a [**Lance namespace**](https://lance.org/format/namespace/) , running **`CREATE TABLE`** creates datasets managed by that namespace (similar to how catalogs work in other systems). This is a nice way to keep “derived datasets” (data slices, hard negatives, reranked features) organized without having to remember path specifiers.
4. **Cloud-native access via DuckDB secrets**: Keep using DuckDB’s familiar cloud connectivity features to access object-storage URIs like **`s3://...`** and more. You simply configure a secret with a scoped prefix once, and then query the dataset path directly.

## 5-minute quickstart

In this section, we’ll go through examples that cover hybrid retrieval, joins, and materialized slices, all done with SQL from the comfort of your DuckDB CLI.

#### Install and load the extension

Install the extension as follows. If you’ve already installed the extension before, you can just update it.

```
INSTALL lance FROM community;
LOAD lance;

-- UPDATE if you've installed a previous version.
UPDATE EXTENSIONS;
```

#### Create a small retrieval table (text + embedding) and write to Lance

Let’s create a simple Lance dataset about animals and the noises they make. This is done using SQL DDL/DML as shown below. The query generates data in SQL and writes a new Lance dataset.

```
COPY (
  SELECT *
  FROM (
    VALUES
      (1, 'duck',   'quack', [0.9, 0.7, 0.1]::FLOAT[3]),
      (2, 'horse',  'neigh', [0.3, 0.1, 0.5]::FLOAT[3]),
      (3, 'dragon', 'roar',  [0.5, 0.2, 0.7]::FLOAT[3])
  ) AS t(id, title, text, vec)
) TO './docs.lance' (FORMAT lance, mode 'overwrite');
```

#### Hybrid search in SQL

You can now call hybrid search as a table function in SQL, which is pushed down and executed at the Lance table layer. A hybrid search query lets you combine a full-text search query with a vector search query via a linear combination of scores. The hybrid search results contain a `_hybrid_score` (larger is better, so we sort in descending order).

```
SELECT id, _hybrid_score, _distance, _score
FROM lance_hybrid_search(
  './docs.lance',
  'vec',  [0.8, 0.7, 0.2]::FLOAT[],
  'text', 'the duck surprised the dragon',
  k = 10,
  alpha = 0.5,
  oversample_factor = 4
)
ORDER BY _hybrid_score DESC;
```

#### Join retrieval results to metadata/features and slice data

You can also do joins between DuckDB tables and Lance tables. The example below joins results from a hybrid search query run on a Lance dataset and a regular DuckDB table `doc_meta`.

```
CREATE TABLE doc_meta AS
SELECT * FROM (VALUES
  (1, 'train', 0.12),
  (2, 'train', 0.34),
  (3, 'eval',  0.56)
) AS t(id, split, quality_score);

SELECT r.id, r._hybrid_score, r._distance, r._score, m.split, m.quality_score
FROM lance_hybrid_search(
  './docs.lance',
  'vec',  [0.8, 0.7, 0.2]::FLOAT[],
  'text', 'the duck surprised the dragon',
  k = 50,
  alpha = 0.5,
  oversample_factor = 4
) r
JOIN doc_meta m USING (id)
WHERE m.split = 'eval'
ORDER BY r._hybrid_score DESC
LIMIT 50;
```

#### Materialize the top-k slice and write back into Lance

The extension supports both reads and writes. In the example below, we materialize the top-k results from our hybrid search query and write them to a new Lance dataset.

```
COPY (
  SELECT r.*
  FROM lance_hybrid_search(
    './docs.lance',
    'vec',  [0.8, 0.7, 0.2]::FLOAT[],
    'text', 'the duck surprised the dragon',
    k = 50,
    alpha = 0.5,
    oversample_factor = 4
  ) r
  ORDER BY r._hybrid_score DESC
  LIMIT 50
) TO './topk_eval_slice.lance' (FORMAT lance, mode 'overwrite');
```

## Cloud integration

Using the extension, you query your Lance data where it lives, whether on your local machine or on object stores in the cloud. The example below shows how to create an S3-scoped secret, and then directly query your Lance datasets on S3 in SQL.

```
CREATE SECRET (
  TYPE LANCE,
  PROVIDER credential_chain,
  SCOPE 's3://bucket/'
);

SELECT *
FROM 's3://bucket/path/to/dataset.lance'
LIMIT 5;
```

The key takeaway is: configure access to cloud storage once, then treat the dataset path as a queryable input in the future.

## A note for users of the earlier Python + PyArrow workflow

If you’ve previously used DuckDB with LanceDB in Python, that integration is done via Apache Arrow, which enables zero-copy data sharing. DuckDB can also push down column selections and basic filters to reduce scanned data. **This remains a great option for Python-first exploration and notebooks**.

However, Arrow boundaries can limit the expressivity of pushdowns for more production-style access patterns. We [previously](https://lancedb.com/blog/benchmarking-random-access-in-lance/#duckdb-integration) called out that DuckDB’s Arrow integration has extremely limited filter pushdown in some cases, which can translate into large latency differences for certain access patterns. We’re happy to announce that the Lance × DuckDB extension is not constrained by that interface boundary, giving us more room to improve pushdown, parallelism, and diagnostics in the future.

## Conclusions

> One open lakehouse, with multiple compute engines for search & retrieval, accessible within a familiar SQL interface.

‍

[Lance](https://lance.org/) is designed to be the open lakehouse format for multimodal AI: an open-source, durable, and performant data layer on object storage that supports multimodal datasets at immense scale.

[DuckDB](https://duckdb.org/) is an open-source, developer-friendly database and compute engine that provides a convenient SQL interface. With the Lance × DuckDB extension, you get first-class SQL operators for retrieval within a modern query engine, while operating on top of an open lakehouse format. You can run vector, FTS, or hybrid retrieval, immediately join to features and metadata, compute analysis and evaluation data on-the-fly, and materialize and reproduce slices of the data back into Lance, all using the SQL syntax you’re already familiar with.

If you’re building RAG systems, retrieval pipelines for agents, or working with very large multimodal AI datasets on object storage, you now have a concrete way to unify your retrieval and analytics workloads without copying data between formats.

Install the Lance × DuckDB extension, point DuckDB at a Lance dataset, and run your first retrieval query now!

## Links

Check out the following pages to learn more about this extension and reach out to us on [Lance Discord](https://discord.gg/lance) with your comments and feedback!

* Lance homepage: [lance.org](https://lance.org/)
* [‍](https://lance.org/)Lance format specification: [lance.org/format](https://lance.org/format)
* [‍](https://lance.org/format)Lance × DuckDB extension repo: [github.com/lance-format/lance-duckdb](https://github.com/lance-format/lance-duckdb)
* [‍](https://github.com/lance-format/lance-duckdb)DuckDB community extension page: [duckdb.org/community\_extensions/extensions/lance.html](https://duckdb.org/community_extensions/extensions/lance.html)
* [‍](https://duckdb.org/community_extensions/extensions/lance.html)LanceDB DuckDB extension docs: [docs.lancedb.com/integrations/data/duckdb](https://docs.lancedb.com/integrations/data/duckdb)
* [‍](https://docs.lancedb.com/integrations/data/duckdb)Background on Arrow pushdown limitations: [lancedb.com/blog/benchmarking-random-access-in-lance/](https://lancedb.com/blog/benchmarking-random-access-in-lance/)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c2da58e972a1401f760beb_xuanwo.avif)

[Xuanwo](/author/xuanwo)

ASF Member. Apache OpenDAL PMC Chair. VISION: Data Freedom. Working on RBIR with LanceDB.

[GitHub](https://github.com/Xuanwo)[Linkedin](https://www.linkedin.com/in/xuanwo/)[Twitter](https://x.com/OnlyXuanwo)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a567183dd1ae093c21b81d5_opt3.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a50fef0022a597f28313428_hero%20img.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a510da7aa738b84d6e9c040_preview-image.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb