---
title: 'https://www.lancedb.com/blog/lance-file-format-2-2-taming-complex-data'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/lance-file-format-2-2-taming-complex-data
account: 
origin: en-rss
---
# Lance File Format 2.2: Taming Complex Data

[Xuanwo](/author/xuanwo)

•

March 9, 2026

•

[Engineering](/category/engineering)

![1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881-fig-001](../images/1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

At LanceDB, we have a saying internally: “***100B*** *is the new* ***100M***.”

A hundred million records *used to* qualify as a large multimodal dataset. Today, the frontier is pushing toward a hundred billion and beyond. Meanwhile, the pace of AI/ML is redefining what data infrastructure must handle. Training data is no longer just text and embeddings; multimodal models now rely on images, audio, video, and other large artifacts. RAG and agentic systems need vectors paired with rich, fast-changing metadata. Feature engineering schemas are growing deeper and evolving with every product iteration. And as datasets keep scaling, storage cost has become a hard constraint, not a footnote.

These trends all point in the same direction: a data format for ML/AI must handle complex types, large objects, schema evolution, and compression well, *all at once*.

Lance file format 2.2 (**`data_storage_version="2.2"`**) is built around exactly these needs. Format 2.1 laid the groundwork with structural encoding, bringing random-access I/O down to 1–2 round trips. Format 2.2 builds on that foundation with a redesigned Blob V2, flexible nested field evolution, native Map types, and a broad uplift in compression. The result is a format that’s better suited for multimodal, dynamic, large-scale AI data workloads.

**💡 2.2 refers to the file format version**

The version numbers mentioned in this post (2.0, 2.1, and 2.2) refer to the Lance **file format version** (the **`data_storage_version`** parameter), which is separate from the Lance library release versions you may see on GitHub.

* The file format version governs how data is encoded and stored on disk.
* The library version determines which format versions can be read and written via the SDK.

The following sections highlight what’s new in Format 2.2.

## Blob V2: Large Files as First-Class Citizens

Previously, Lance supported large object storage by tagging **`LargeBinary`** fields with **`lance-encoding:blob`** metadata, which we called Blob v1. That worked for basic cases, but it still stored every blob inline in the file. This made very large objects awkward to handle, required writing the full blob data into Lance, and could not take advantage of external files that already existed in object storage.

Just as importantly, the hard parts were not only file-layout problems. They were also table problems: compaction, lifecycle management, and integrating external objects without forcing everything to be rewritten into the dataset. Blob V2, introduced in format 2.2, is a ground-up redesign shaped by both layers, and it is a good example of Lance’s broader end-to-end format strategy. For new projects, Blob V2 is the recommended path. Legacy blob data remains readable under format 2.2.

One key result is **adaptive storage layout**. At write time, Blob V2 automatically picks the best storage strategy based on the actual data: small payloads are stored inline within data pages, medium payloads are packed into shared blocks, and large payloads go into dedicated regions. This automatic tiering avoids small-file bloat while maintaining steady read/write performance across a wide range of blob sizes.

Another key result is **external blob management**. Blob V2 uses the **`lance.blob.v2`** extension type identifier, writes go through dedicated **`blob_field`** and **`blob_array`** constructors, and reads return lazy **`BlobFile`** handles that stream bytes on demand. More importantly, you can register media files in external storage (S3 paths, GCS paths, etc.) directly into a Lance table without copying the data into the dataset. For teams sitting on large media assets, this changes the game: a URI, or even a byte range within a URI, can become part of Lance’s unified management without bulk rewriting.

A typical write example is below:

```
import lance
import pyarrow as pa
from lance import blob_array, blob_field

schema = pa.schema([
    pa.field("id", pa.int64()),
    blob_field("data"),
])

table = pa.table(
    {
        "id": [1, 2],
        "data": blob_array([b"inline-bytes", "s3://bucket/path/video.mp4"]),
    },
    schema=schema,
)

# External URIs outside dataset base paths require this write option
ds = lance.write_dataset(
    table,
    "./blobs.lance",
    data_storage_version="2.2",
    allow_external_blob_outside_bases=True,
)

# Returns a BlobFile handle for streaming access
blob = ds.take_blobs("data", indices=[0])[0]
with blob as f:
    print(f.read())
```

**`take_blobs`** returns lazy handles. No data is fetched at this point. Bytes are pulled on demand only when you call **`f.read()`**, making it well-suited for streaming large files.

The migration path is straightforward: new projects should use the v2 API directly; existing projects can follow the batched migration examples in the docs to switch over gradually. Type definitions, streaming reads, external references: one API covers all scenarios.

## Nested Schema Evolution

This is an area we feel strongly about based on our experience maintaining feature engineering projects. Say you have a schema like this:

```
{
  "user_profile": {
    "basic": {"age": 25, "gender": "M"},
    "behavior": {"last_7d_click": 120, "embeddings": [0.1, 0.2, 0.3]}
  }
}
```

Later, the product team needs a **`country`** field inside **`basic`**. Format 2.1 only supported dropping sub-columns from structs. In format 2.2, Lance also supports adding new fields into nested structs, including list-of-struct layouts, without rewriting the existing parent data. For all-null additions, this can be a metadata-only operation; for materialized additions, Lance appends the new field data while keeping existing data files intact. Reads automatically synthesize missing nested children as nulls when needed:

```
import lance
import pyarrow as pa

table = pa.table(
    {
        "user_profile": [
            {"basic": {"age": 25, "gender": "M"}},
            {"basic": {"age": 30, "gender": "F"}},
        ]
    }
)
dataset = lance.write_dataset(table, "nested_schema_demo.lance", data_storage_version="2.2")

# Add a new nested field as an all-null column (metadata-only in format >= 2.2)
dataset.add_columns(
    pa.schema([
        pa.field(
            "user_profile",
            pa.struct([
                pa.field(
                    "basic",
                    pa.struct([
                        pa.field("country", pa.string()),
                    ]),
                ),
            ]),
        ),
    ])
)
```

Under the hood, Lance assigns stable field IDs to nested fields and tracks physical column metadata separately, which allows new nested children to be introduced without rewriting the original parent column payload. This removes the need for full data compaction during many schema evolution workflows.

## Native Map Type

This started with a team working on user profiling: “We process millions of users’ dynamic tags every day. String keys, string or integer values. Does Lance have a good solution?” At the time, every option had trade-offs. Splitting into separate columns worked for fixed keys. JSON was flexible but slow to query. Structs were type-safe but rigid. They ended up simulating a Map with List+Struct. It worked, but the code was littered with manual serialization and deserialization.

Format 2.2 makes Map a first-class citizen in the spec:

```
import pyarrow as pa

schema = pa.schema([
    ("user_id", pa.int64()),
    ("tags", pa.map_(pa.string(), pa.string()))
])
```

Physically, a Map is stored as **`List<Struct<key, value>>`**, but the logical and encoding layers treat it as its own type:

* **Clear semantics**: The schema declares Map directly. Readers and writers no longer need to agree on a List+Struct convention.
* **Efficient encoding**: Offsets and entries are encoded separately, reusing the structural encoding framework from format 2.1. Random access still takes just 1–2 I/O operations.
* **Evolvable**: Format 2.2’s nested evolution capabilities extend to Maps. You can independently add or remove fields on key or value sub-columns without rewriting the entire column.

For users, the most immediate payoff is simpler code. Hand-rolled JSON parsing and column-splitting logic can simply be removed.

## Encoding and Compression

Format 2.2 is a comprehensive compression upgrade. Format 2.1 established a two-layer architecture that separates structural encoding from compression. Format 2.2 extends compression coverage to more data types and encoding paths, achieving multi-fold space reductions compared to format 2.0 in many scenarios, all while preserving Lance’s scan and random-access performance.

Key changes:

* **General Block Compression**: The single biggest change in format 2.2. Data blocks larger than 32KB are automatically compressed with LZ4, with zero configuration needed. For higher compression ratios, you can specify zstd via metadata.
* **RLE Block Encoding**: RLE has been promoted from mini-blocks to full block-level encoding. Columns with many repeated values (status fields, category labels, etc.) see significant gains.
* **Dictionary Value Compression**: Dictionary-encoded values are now compressed with LZ4 by default. You can customize the algorithm and level through **`lance-encoding:dict-values-compression`**.
* **Generalized Constant Layout**: Pages where every value is identical (all nulls, all the same default, etc.) are represented by a single inline scalar. Storage overhead is effectively zero.
* **Mini-block Enhancement**: The maximum chunk size has been raised from 32KB (u16) to 128KB+ (u32). This does not change the default behavior, but it allows larger chunks when they are beneficial for compression.
* **Variable Packed Struct**: Packed storage now extends from fixed-width fields to variable-width fields. Each sub-field is compressed independently, then transposed into a row-major layout. This is a good match for ML training workloads that read a group of features at once.

The combined effect: format 2.2 applies compression automatically to most data types, out of the box. Text, JSON, sparse features, and highly repetitive label columns see the most improvement. High-entropy data like embeddings and pre-compressed images benefit less. We recommend benchmarking with your own data:

```
import lance
import pyarrow as pa

data = pa.table({"id": [1, 2, 3], "text": ["a", "b", "c"]})
ds = lance.write_dataset(data, "test.lance", data_storage_version="2.2")
print(f"Rows: {ds.count_rows()}")
# Compare the data directory size across different data_storage_version values
```

## Upgrade Strategy

Like previous versions, Lance Format 2.2 is opt-in. To use it, you need to specify it explicitly:

```
import lance
import pyarrow as pa

data = pa.table({"id": [1, 2], "value": ["x", "y"]})
lance.write_dataset(data, "my_dataset.lance", data_storage_version="2.2")
```

The default file format version is **`stable`** (the latest stable format supported by your installed Lance version), giving you full control over the upgrade pace and enough room to test across environments.

The list below describes our recommended rollout strategy:

1. **Upgrade all environments first**: Make sure every reader has a Lance library version that supports format 2.2 (check the release notes for the specific version). The safest approach is to upgrade library versions across all environments uniformly.
2. **Pilot with non-critical datasets**: Write a batch of data in format 2.2, run all downstream tasks, and compare performance and storage metrics.
3. **Expand gradually**: Move from peripheral workloads to core production data.

## When to Use It

The following scenarios benefit most:

* **Rapidly evolving nested structures**: ML feature engineering, user profiling, complex event processing, and any workload where schemas change frequently.
* **Dynamic key-value attributes**: Event tracking data, experiment parameters, and sparse features. The Map type eliminates a lot of glue code.
* **Multimodal data management**: Images, videos, audio, and other large objects managed uniformly through Blob V2. One API for every scenario.
* **Storage efficiency**: Text, JSON, sparse features, and similar data see significant space savings from format 2.2’s encoding improvements.

If your data model is already stable, you can upgrade at your own pace. Format 2.2 is fully backward-compatible with format 2.1 and 2.0 data for reads. The upgrade window is yours to decide.

## Roadmap

Now that Format 2.2 has been formalized, our focus is shifting toward the following:

* **Variant Type**: More and more users store semi-structured data as JSON. We have introduced JSONB, but its query performance still falls short of our expectations. We plan to introduce a Variant type that preserves the flexibility of semi-structured data while delivering columnar query and compression performance.
* **Native Media Type Support**: In multimodal workflows, images, audio, and video need format-aware metadata beyond raw storage. Think of an image’s width, height, and encoding format, or an audio file’s sample rate and channel count. Today this metadata is scattered across application code. We plan to support media types natively in the type system, letting Lance understand the physical characteristics of data at the storage layer and providing a better foundation for downstream decoding, transcoding, and indexing.
* **Discrete Vectors**: Current vector indexing is built primarily for continuous floating-point embeddings. With the rise of quantization techniques and token-level representations, demand for binary vectors, integer vectors, and other discrete vector types is growing steadily. We plan to support discrete vectors natively in both the encoding and indexing layers for more efficient storage and retrieval.
* **Richer Encoding Algorithms**: The general block compression and RLE in format 2.2 are just the beginning. We are exploring encoding algorithms targeted at specific data distributions (frame-of-reference, patched encoding, ALP, and others) to push compression ratios and decoding speeds further.
* **Intelligent Encoding Tuning**: Today, encoding decisions are mostly rule-based. We plan to introduce adaptive encoding selection driven by data sampling. At write time, we analyze data distributions and automatically match each column with its optimal encoding combination. During compaction, we re-evaluate and adjust encoding strategies based on actual data characteristics, so storage efficiency improves as data accumulates.

Our goal is clear: to make Lance **the standard data format for AI/ML workloads**. From multimodal storage and dynamic schemas to efficient compression and intelligent encoding, every iteration closes the gap between data infrastructure and the demands of modern models. Format 2.2 is a major step in that direction.

Thank you to everyone who has filed issues, tested beta releases, and contributed PRs to this release. Every improvement in Lance is rooted in real-world use cases and feedback. If you are looking for a data format purpose-built for AI workloads, come join us. Let’s define the next generation of ML data infrastructure together!

![1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881-fig-002](../images/1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881/figure-002.avif)

[Xuanwo](/author/xuanwo)

ASF Member. Apache OpenDAL PMC Chair. VISION: Data Freedom. Working on RBIR with LanceDB.

[GitHub](https://github.com/Xuanwo)[Linkedin](https://www.linkedin.com/in/xuanwo/)[Twitter](https://x.com/OnlyXuanwo)

![1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881-fig-003](../images/1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881-fig-004](../images/1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881-fig-005](../images/1434-https-www-lancedb-com-blog-lance-file-format-2-2-30495881/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb