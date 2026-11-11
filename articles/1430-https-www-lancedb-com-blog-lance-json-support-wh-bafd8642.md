---
title: 'https://www.lancedb.com/blog/lance-json-support-why-you-might-not-really-need-variant'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/lance-json-support-why-you-might-not-really-need-variant
account: 
origin: en-rss
---
# Lance JSON Support: Why You Might Not Really Need Variant

[Jack Ye](/author/jack-ye)

•

April 9, 2026

•

[Engineering](/category/engineering)

![1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642-fig-001](../images/1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

We recently released [Lance file format 2.2](https://www.lancedb.com/blog/lance-file-format-2-2-taming-complex-data), bringing [Blob v2 support](https://www.lancedb.com/blog/lance-blob-v2) and [impressive performance improvements](https://www.lancedb.com/blog/lance-format-v2-2-benchmarks-half-the-storage-none-of-the-slowdown). Since then, the most frequently requested addition has been Variant type support. Users see the industry momentum (Spark 4.0, Parquet spec, Delta Lake, Iceberg V3, Arrow, DuckDB) and assume Variant is the key to efficient JSON storage and processing.

But here's what we've found: when users dig into what they actually need, many discover that Lance already does it. JSONB provides efficient binary storage at the file layer. Scalar indexes (BTree, bitmap, bloom filter) enable fast field access. Data evolution lets you explicitly extract frequently-queried fields into columns with consistent schemas across all files. Full-text search indexes enable text search across JSON documents natively.

This post walks through each of these capabilities, compares them to what Variant offers, and explains why Lance's unified design across file format and table format layers might already be everything you need.

## Background: What is Variant, and What It Achieves

Before diving into Lance's JSON capabilities, let's understand what Variant is and why it has gained so much attention.

### A Brief History

The concept of a native semi-structured data type in analytical databases isn't new. **Snowflake** introduced its `VARIANT` type as a core feature, allowing users to load and query JSON, XML, and other semi-structured formats without predefined schemas. **Amazon Redshift** followed with `SUPER`, offering similar capabilities for its data warehouse users.

The open-source ecosystem took notice. As data lakehouses became the architecture of choice, there was growing demand to bring these capabilities to open formats. **Apache Spark 4.0** introduced native Variant support, and this drove standardization efforts across the ecosystem. The **Parquet** community [finalized the Variant specification in mid-2025](https://www.mail-archive.com/dev@parquet.apache.org/msg26539.html), with **Delta Lake** and **Iceberg V3** both adopting it as their answer to semi-structured data in the lakehouse.

### The Two Components of Variant

Variant achieves its goals through two key mechanisms:

**Variant Encoding**: A compact binary serialization format that replaces raw JSON text. Instead of storing JSON as strings that must be parsed on every read, Variant encoding stores values in a binary format that preserves type information and enables efficient field access without parsing overhead.

**Variant Shredding**: Shredding automatically extracts commonly occurring fields from the semi-structured data into separate Parquet columns. The goal is to bring columnar benefits — better compression, predicate pushdown, and column pruning — to fields that are frequently accessed, while keeping the flexibility of schema-on-read for everything else.

On paper, this sounds ideal. But as we'll see, Lance's existing capabilities already deliver most of these benefits through a different, and arguably more transparent, approach.

## Efficient Storage for Unstructured JSON Data

### What Lance Does

Lance stores JSON data internally as **JSONB** using the `lance.json` Arrow extension type.

JSONB has a long history as the proven solution for semi-structured data storage. [PostgreSQL introduced JSONB in 2014](https://www.postgresql.org/docs/current/datatype-json.html), and it quickly became one of the most popular features driving PostgreSQL adoption. The format stores JSON documents as compact binary blobs that preserve the full structure while eliminating the parsing overhead of raw JSON text. Over the past decade, JSONB has become the de facto standard for storing semi-structured data in databases — well-understood, battle-tested, and supported by a vast ecosystem of tools.

Lance brings this proven approach to the data lakehouse. Each JSON document is serialized into an efficient binary representation, providing fast query performance for nested field access and compatibility with Apache Arrow's JSON type.

### Using It Today

Storing JSON data in Lance is straightforward:

```
import lance
import pyarrow as pa
import json

# Create test data with JSON columns
json_data = [
    {"user": {"name": "Alice", "age": 30}, "tags": ["python", "ml"]},
    {"user": {"name": "Bob", "age": 25}, "tags": ["rust", "db"]},
    {"user": {"name": "Charlie"}, "tags": []},
]

json_strings = [json.dumps(d) for d in json_data]
json_arr = pa.array(json_strings, type=pa.json_())

table = pa.table({"id": [1, 2, 3], "data": json_arr})

# Write to Lance
lance.write_dataset(table, "users.lance")
```

Once stored, you can query any nested field using Lance's built-in JSON functions:

```
dataset = lance.dataset("users.lance")

# Extract values using JSONPath
result = dataset.to_table(
    filter="json_extract(data, '$.user.name') = '\"Alice\"'"
)

# Type-safe extraction with json_get_*
result = dataset.to_table(
    filter="json_get_int(data, 'age') > 25"
)

# Check field existence
result = dataset.to_table(
    filter="json_exists(data, '$.user.age')"
)

# Array operations
result = dataset.to_table(
    filter="json_array_contains(data, '$.tags', 'python')"
)
```

### How It Compares to Variant

Both JSONB and Variant Encoding solve the same fundamental problem: eliminating the overhead of parsing raw JSON text on every query. The key difference lies in their encoding approach.

JSONB encodes each document independently as a self-contained binary blob. Variant, on the other hand, operates on columnar batches — it can look across multiple documents and encode shared structure more efficiently. In theory, when documents vary significantly in their structure, JSONB and Variant perform similarly. But when documents share a common shape, Variant's columnar encoding can achieve better compression.

To quantify this, we benchmarked Lance JSONB against Parquet Variant (without shredding) using item metadata from the [Amazon Reviews 2023 dataset](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023) — a real-world dataset where different product categories have different attribute keys in their JSON `details` field, making it a good test of semi-structured data handling. We used DuckDB 1.5.1 to write Parquet Variant files with shredding disabled (`variant_minimum_shredding_size = -1`) — shredding duplicates data into separate columns, which inflates file size, and we only want to compare the encoding efficiency here. We used pylance to write Lance files with `data_storage_version="2.2"`.

The results confirm our theory above: the gap depends heavily on the nature of your JSON documents:

**Text-heavy categories** (Books, Kindle Store, Electronics, etc.) — documents dominated by long free-text descriptions, reviews, and variable-length content:

| Category | JSON Size | Lance JSONB | Parquet Variant | JSONB / Variant |
| --- | --- | --- | --- | --- |
| Books | 221.2 MB | 113.6 MB | 121.4 MB | 0.94x |
| Kindle Store | 221.2 MB | 113.6 MB | 121.4 MB | 0.94x |
| Electronics | 150.1 MB | 64.4 MB | 64.5 MB | 1.00x |
| Musical Instruments | 154.0 MB | 68.6 MB | 65.5 MB | 1.05x |
| Software | 136.6 MB | 66.7 MB | 57.0 MB | 1.17x |

When documents are dominated by free-text content, JSONB and Variant perform similarly — within 5-17% of each other. Text doesn't benefit much from Variant's cross-row encoding because the actual values are unique per document.

**Structured metadata categories** (Home & Kitchen, Fashion, Beauty, etc.) — documents with repetitive key names and short, categorical values:

| Category | JSON Size | Lance JSONB | Parquet Variant | JSONB / Variant |
| --- | --- | --- | --- | --- |
| Amazon Fashion | 35.7 MB | 37.2 MB | 10.1 MB | 3.69x |
| Gift Cards | 6.1 MB | 6.3 MB | 1.8 MB | 3.52x |
| All Beauty | 33.2 MB | 34.6 MB | 11.1 MB | 3.11x |
| Clothing, Shoes & Jewelry | 133.4 MB | 137.6 MB | 52.5 MB | 2.64x |
| Home & Kitchen | 176.2 MB | 180.8 MB | 77.2 MB | 2.34x |

For highly structured metadata with repetitive keys and short values, Variant's columnar encoding shines — achieving 2-4x better compression than JSONB. The repeated key names and common value patterns compress extremely well across rows.

**Mixed categories** (products with some shared attributes and many category-specific fields):

| Category | JSON Size | Lance JSONB | Parquet Variant | JSONB / Variant |
| --- | --- | --- | --- | --- |
| Electronics | 150.1 MB | 64.4 MB | 64.5 MB | 1.00x |
| Beauty & Personal Care | 138.1 MB | 62.6 MB | 60.0 MB | 1.04x |
| Cell Phones & Accessories | 131.5 MB | 55.0 MB | 51.0 MB | 1.08x |
| Office Products | 161.4 MB | 71.4 MB | 68.8 MB | 1.04x |
| Sports & Outdoors | 138.0 MB | 64.5 MB | 60.2 MB | 1.07x |
| Video Games | 163.8 MB | 70.7 MB | 67.7 MB | 1.04x |
| Mixed (all 33 categories) | 266.5 MB | 122.7 MB | 114.2 MB | 1.07x |

Categories with some shared attributes and many category-specific fields land right in the middle — JSONB and Variant within **0-8%** of each other. The mixed-all row interleaves documents from all 33 product categories into a single dataset, simulating the realistic case of a single table ingesting JSON from multiple sources with varying schemas.

> **💡 The takeaway  
> ‍  
> ‍**Variant's columnar encoding wins on highly structured metadata with repetitive keys and short categorical values. But consider the data that's actually driving demand for semi-structured storage today: agent and AI workloads. Tool calls, chain-of-thought traces, retrieval-augmented generation contexts, multi-modal payloads — these documents are text-heavy, deeply nested, and wildly heterogeneous across rows. That's exactly the regime where JSONB matches Variant's storage efficiency — and as we'll show in the following sections, Lance pairs this with scalar indexing, data evolution, and full-text search that go well beyond what Variant offers.

## Scalar Indexing on JSON Fields

### What Lance Does

Lance allows you to create **scalar indexes on any JSON subfield**. This is Lance's secret weapon for semi-structured data. Rather than relying on full document scans, you can explicitly declare which fields matter for your queries and build indexes on them — just like you would for regular columns. Need fast equality and range lookups? Create a BTree index. Working with low-cardinality categorical fields? Use a bitmap index. Want efficient substring matching? Build an ngram index.

### Using It Today

```
from lance.indices import IndexConfig

# Create a BTree index on the "x" field inside the JSON column
dataset.create_scalar_index(
    "data",
    IndexConfig(
        index_type="json",
        parameters={"target_index_type": "btree", "path": "x"}
    ),
)

# Inspect the query plan to confirm index usage
print(dataset.scanner(filter="json_get_int(data, 'x') = 10").explain_plan())
# ScalarIndexQuery: query=[json_get_int(data, 'x') = 10]@data_idx
#   MaterializeIndex
#     LanceScan: ...
```

This approach gives you the best of both worlds: the flexibility of semi-structured data with the query performance of indexed columns. You don't need to flatten your JSON or define a rigid schema upfront. Just index the fields you query most, and let Lance handle the rest.

### How It Compares to Variant

The [Parquet Variant specification](https://parquet.apache.org/docs/file-format/types/variantencoding/) does not include any statistics or indexing mechanism for unshredded Variant data. Without shredding, queries on Variant fields require scanning the entire binary blob — there's no min/max statistics, no bloom filters, no way to skip data based on field values.

The only path to query acceleration in Variant is **shredding** — extracting fields into separate Parquet columns that then benefit from standard columnar statistics. But shredding is a write-time decision, and we'll discuss more about it in the next section.

Lance takes a fundamentally different approach: you can add indexes to JSON fields **after** the data is written, without restructuring your data. Need to accelerate a new query pattern? Add an index. No longer querying a field? Drop the index. Want to support multiple query patterns on the same field? Create multiple indexes — a BTree for range queries and an ngram index for substring search.

This flexibility comes from Lance being both a file format and a table format that integrate seamlessly. Indexes are managed at the table level, separate from the data files, and can be added or removed without touching the underlying data. Variant, by contrast, is a file format feature — all optimizations must be baked into each Parquet file at write time, with no mechanism for table-level enhancements after the fact. Any attempt to complement Variant at a higher level — whether through a table format, catalog, or compute engine — inevitably results in redundancy in the system or an underutilization of the Variant feature itself.

## Shredding of Frequently Accessed JSON Fields

### What Lance Does

**Data evolution**, a.k.a. backfilling column data without rewriting existing data, has been a core Lance feature from day one — and is probably a favorite among ML/AI practitioners. For JSON documents, that means you can "shred" JSON fields into proper columns. If you discover that a JSON field is frequently accessed and would benefit from being a first-class column, you simply add it with a transformation.

### Using It Today

```
# "Shred" a JSON field into a proper column
dataset.add_columns({
    "user_name": "json_get_string(data, 'name')"
})
```

With LanceDB Enterprise, you can take this further using the Feature Engineering capability. Define a UDF once, and the virtual column becomes available for queries — with automatic backfilling handled by the system:

```
# pip install geneva (LanceDB Feature Engineering library)
from geneva import udf

@udf(data_type=pa.string(), auto_backfill=True)
def extract_user_name(data: str) -> str:
    import json
    doc = json.loads(data)
    return doc.get("user", {}).get("name", "")

# Add the column with the UDF - backfilling happens automatically
table.add_columns({"user_name": extract_user_name})

# Create an index on the new column for fast queries
table.create_scalar_index("user_name", index_type="BTREE")

# The column is now available for indexed queries
results = table.search().where("user_name = 'Alice'").to_list()
```

This creates a new column `user_name` that extracts the `name` field from your JSON data. The transformation is:

* **Explicit**: You decide exactly which fields to extract
* **Versioned**: The change is tracked in Lance's table history
* **Consistent**: Works uniformly across all files in your table

You can also add multiple derived columns at once, and even nest them within structs for better organization.

### How It Compares to Variant

We believe Lance's data evolution is a strictly better experience than Variant shredding:

#### Generality

The core idea behind shredding is compelling: extract useful information from a complex binary structure into columnar form for read-time acceleration. But why limit this to semi-structured JSON or XML documents? What about extracting metadata from images, or features from videos? And why stop at extracting the field as-is — why not allow any arbitrary transformation defined by a UDF?

Lance's data evolution is essentially a much more generalized version of Variant shredding. It can extract and transform data from any column type — JSON, blobs, images, embeddings — into new derived columns. Variant shredding is a special case of this pattern, narrowly scoped to semi-structured data. Lance gives you the same capability applied to all of your multimodal data.

#### Schema Consistency

The [Parquet Variant specification](https://parquet.apache.org/docs/file-format/types/variantshredding/) explicitly acknowledges that "different files may contain conflicting shredding schemas. That is, files may contain different typed\_value columns for the same Variant with incompatible types." Reading a table requires reconciling potentially different physical layouts across files. With Lance, your derived columns are defined at the table level and work consistently across all files — no reconciliation needed.

#### Storage Flexibility

With Variant shredding, the decision of what to shred is baked in at write time — you can't change it later without rewriting your data. With Lance, you have finer control: you can define a UDF-backed virtual column without materializing it at all, computing values on-demand. When you do need materialization for performance, you can choose to backfill only a specific subset of rows rather than the entire table. This flexibility lets you adapt to changing query patterns without costly data rewrites.

#### The "Automatic" Shredding Problem

When we talk about Variant shredding being "automatic", what does that actually mean in practice? For example, here is what Spark's [`InferVariantShreddingSchema`](https://github.com/apache/spark/blob/master/sql/core/src/main/scala/org/apache/spark/sql/execution/datasources/parquet/InferVariantShreddingSchema.scala) algorithm does:

1. Buffer up to 4096 rows per task
2. Analyze the buffered sample to find common fields
3. Shred any field appearing in ≥10% of the sample
4. Apply that schema to the entire file

This approach has fundamental limitations:

**If your documents are highly similar**, the algorithm extracts essentially all common fields into separate columns. Although you've gained flexibility compared to using strict struct types, the shredded result is essentially the same columnar layout — except now you've implicitly stored the same information twice: once in the shredded columns and once in the Variant metadata and value blob. People are usually unaware of this implicit storage cost when shredding kicks in aggressively.

**If your documents are heterogeneous**, the first 4096 rows may not be representative of the rest of your data. Fields that are common in the sample but rare overall get shredded unnecessarily, while fields that become common later in the file remain unshredded. And since each file/task infers its own schema independently, you end up with the schema inconsistency problem mentioned above.

**If you want more intelligent shredding** — say, shredding only fields you actually query, or shredding based on global statistics rather than local samples — your only real option is to rely on a vendor product that will "intelligently" figure it out for you — a black box optimization you can't inspect or customize.

Lance's approach is refreshingly straightforward: you explicitly declare which fields to extract as columns, and Lance handles the rest. No guessing, no vendor magic — just transparent data evolution that works exactly as you'd expect. And if you do want an intelligent layer on top, that's what the [LanceDB Multimodal Lakehouse](https://www.lancedb.com/download) provides. But even with just the open-source tools, you have full control over what gets optimized and how.

## High-Performance Search of JSON Terms

### What Lance Does

In many applications, you need to perform fuzzy text searches across your JSON documents — not just exact field matching, but finding records that *mention* a particular term anywhere in their structure. For example: "Does this document reference San Francisco?" or "Find all records mentioning 'machine learning' regardless of which field contains it."

Lance supports creating **full-text search (FTS) indexes on JSON columns**. This enables fast text search across all text content within your JSON documents, with support for stemming (matching "running" when searching for "run"), case-insensitive matching, and stop word removal.

#### How JSON Tokenization Works

When you create an FTS index on a JSON-type column, Lance automatically detects it and uses a **triplet format** to tokenize the JSON structure: `path,type,value`. The `base_tokenizer` you specify controls how text values are split into words (e.g., `simple` for simple English, `jieba` for Chinese), while Lance handles another layer of tokenization that automatically flattens the JSON structure. For example, given this JSON:

```
{"title": "Machine Learning", "location": {"city": "San Francisco"}}
```

Lance tokenizes it into searchable terms like:

* `title,str,machine`
* `title,str,learning`
* `location.city,str,san`
* `location.city,str,francisco`

This allows you to search for values within specific JSON paths, or search across all paths for a term.

### Using It Today

Create an FTS index on your JSON column:

```
import lance
import pyarrow as pa
import json
from lance.query import MatchQuery

# Create a table with JSON documents
documents = [
    {"title": "AI Research Lab", "location": {"city": "San Francisco", "state": "CA"}},
    {"title": "Data Science Hub", "location": {"city": "New York", "state": "NY"}},
    {"title": "ML Startup", "location": {"city": "San Francisco", "state": "CA"}},
]

json_strings = pa.array([json.dumps(d) for d in documents], type=pa.json_())
table = pa.table({"doc": json_strings, "id": range(len(documents))})
dataset = lance.write_dataset(table, "documents.lance")

# Create an FTS index on the JSON column
dataset.create_scalar_index("doc", index_type="FTS")

# Verify the FTS index is being used
scanner = dataset.scanner(
    full_text_query=MatchQuery("location.city,str,san francisco", "doc")
)
print(scanner.explain_plan())
# ScalarIndexQuery: query=FullTextSearch(doc, "location.city,str,san francisco")@doc_idx
```

The FTS index supports multiple query types:

* **MatchQuery**: Searches for terms within specific JSON paths
* **BooleanQuery**: Combines multiple conditions with AND/OR/NOT logic
* **PhraseQuery**: Exact phrase matching (requires `with_position=True` when creating the index)
* **Fuzzy search**: Approximate matching with configurable edit distance

### How It Compares to Variant

Variant doesn't provide any built-in full-text search capabilities. It focuses on efficient storage and columnar access patterns, but searching for text within semi-structured documents requires additional tooling — you'd need to integrate with external search engines like Elasticsearch or Solr, creating yet another data silo.

This is where Lance's architecture shines. Lance is designed as both a file format and a table format with clear separation of concerns — the file format handles efficient columnar storage, while the table format handles indexing, transactions, and query optimization. By owning both layers, we can build features like FTS indexes at the table layer that work natively on JSON columns stored in the file layer, without requiring external systems. You can combine scalar BTree indexes for exact equality and range queries, FTS indexes for text search, and even vector indexes for semantic search — all on the same table, with a unified query interface.

## Conclusions

Although Lance does not yet support Variant in format 2.2, you can already do almost everything you want with your JSON documents using Lance in a highly efficient and scalable manner:

* **Efficient storage**: JSONB provides compact binary encoding at the file layer, without the metadata overhead of Variant's shredding structures.
* **Fast field access**: Scalar indexes (BTree, bitmap, bloom filter) on JSON paths give you O(1) lookups without needing columnar extraction.
* **Query-aware optimization**: Data evolution lets you explicitly extract frequently-queried fields into columns — you decide what to optimize based on your actual query patterns, not sampled data or vendor black-box optimization.
* **Generalized data evolution**: Unlike Variant shredding which is limited to semi-structured documents, data evolution works on any column type — JSON, blobs, images, embeddings — with arbitrary UDF transformations, not just field extraction.
* **Schema consistency**: Derived columns are defined at the table level, so all files have the same schema — no reconciliation needed.
* **Full-text search**: FTS indexes on JSON columns enable text search natively, without external systems.

You get explicit control over what gets optimized, with consistent behavior across all your data.

### What This Means for Lance Variant Support

With all that said, Variant is still super cool. It's a technically impressive solution to a real problem, and as our benchmarks above showed, there is a real storage benefit in encoding semi-structured data as Variant rather than JSONB — especially for structured metadata workloads where Variant achieves 2-4x better compression. Users whose data fits those characteristics should be able to choose Variant as their encoding.

We plan to support Variant in our next iteration for exactly this reason. When we do, it would complement rather than replace our existing capabilities. Table-level data evolution would still handle shredding with consistent schemas. Unified indexing would work the same way on Variant columns as it does on JSONB today. The key insight is that *table format* features — indexing, transactions, data evolution, search — work hand in hand with *file format* encoding to deliver end-to-end performance for real-world workloads. Storage encoding is only one piece of the puzzle.

### What This Means for Lance Users Today

Lance's JSON support is ready to use today, especially if you're storing **agent and AI data**. As our benchmarks show, agent workloads fall squarely in the regime where JSONB already matches Variant on storage, and you get all the table-level capabilities on top: you can add indexes after the fact, evolve your schema without rewriting data, and avoid the pitfalls of sample-based automatic shredding on data whose structure changes from one request to the next.

If you're building agentic AI applications or AI training infrastructure — whether it's [using LanceDB to back OpenClaw](https://www.lancedb.com/blog/openclaw-memory-from-zero-to-lancedb-pro), powering [autonomous agents with Seed 2.0](https://www.lancedb.com/blog/openclaw-lancedb-seed2), or building a [multimodal memory layer for any AI agent](https://www.lancedb.com/blog/openclaw-lancedb-memory-layer) — Lance's JSON support already gives you everything you need: compact storage, post-hoc indexing, data evolution, and full-text search. You don't need to wait for Variant support to arrive.

‍

![1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642-fig-002](../images/1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642/figure-002.avif)

[Jack Ye](/author/jack-ye)

Data engineer and table format specialist, working on distributed systems and modern data lake architectures.

[GitHub](https://github.com/jackye1995)[Linkedin](https://www.linkedin.com/in/yezhaoqin/)

![1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642-fig-003](../images/1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642-fig-004](../images/1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642-fig-005](../images/1430-https-www-lancedb-com-blog-lance-json-support-wh-bafd8642/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb