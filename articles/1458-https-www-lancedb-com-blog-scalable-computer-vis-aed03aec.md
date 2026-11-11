---
title: 'https://www.lancedb.com/blog/scalable-computer-vision-with-lancedb-voxel51-d8b65066d5f6'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/scalable-computer-vision-with-lancedb-voxel51-d8b65066d5f6
account: 
origin: en-rss
---
# Scalable Computer Vision with LanceDB & Voxel51

[LanceDB](/author/lancedb)

•

July 13, 2023

•

[Engineering](/category/engineering)

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-001](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## Importance of dataset analysis in CV

Dataset analysis is an essential step in any computer vision project. It allows us to understand the data that we are working with, identify any potential problems, and make sure that the data is as representative as possible of the real world. This is especially important once the model architecture is fixed due to deployment constraints, as the best way to improve performance is via iteration on datasets.

[Voxel51](https://voxel51.com) is a set of open-source tools for computer vision. The FiftyOne query language allows you to explore and analyze your data in a variety of ways. You can use the query language to find specific images, objects, or features.

With this integration with LanceDB, Voxel51 can leverage its fast, robust, and setup-free vector search capabilities.

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-002](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-002.avif)

## LanceDB: The serverless vectorDB

LanceDB is an open-source, serverless, multi-modal vector database.

* It is built with persistent storage, which greatly simplifies retrieval, filtering, and management of embeddings.
* It supports vector similarity search, full-text search, and SQL.
* Native support for JavaScript/TypeScript

To enable the LanceDB backend in Voxel51, simply pass `backend="lancedb"` in supported operations

```
import fiftyone.brain as fob

fob.compute_similarity(
    ...
    backend="lancedb",
)
```

## **Example use cases**

### Sort dataset by similarity

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-003](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-003.gif)

### Get similar images to a given id

```
import fiftyone as fo
import fiftyone.brain as fob

fob.compute_similarity(
    ...
    backend="lancedb",
)
id = dataset.first().id
view = dataset.sort_by_similarity(id, k=30)

session = fo.launch_app(view)
session.wait()
```

### Search by Text queries

```
query = "a photo of a dog"
view = dataset.sort_by_similarity(query, k=10, brain_key="lancedb_index")
```

The integration allows various customizations that can be found in the docs.

## LanceDB interface integrates into the Python data ecosystem

LanceDB is compatible with the Python data ecosystem and can be used with pandas, NumPy, and Arrow.

```
lancedb_index = fob.compute_similarity(…)
table = lancedb_index.table

# Integration with Python data ecosystem
df = table.to_pandas()  # get the table as a pandas dataframe
pa = table.to_arrow()   # get the table as an arrow table
```

More use cases and examples using voxel51 with LanceDB backend are available in the [integration docs](https://docs.voxel51.com/integrations/lancedb.html#lancedb-integration).

Visit LanceDB [repo](https://github.com/lancedb/lancedb) and [docs](https://lancedb.github.io/lancedb/) to see more examples and integration.

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-004](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-004.jpg)

[LanceDB](/author/lancedb)

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-005](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-005.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-006](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-006.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec-fig-007](../images/1458-https-www-lancedb-com-blog-scalable-computer-vis-aed03aec/figure-007.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb