---
title: 'https://www.lancedb.com/blog/geneva-twelvelabs'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/geneva-twelvelabs
account: 
origin: en-rss
---
# Building Semantic Video Recommendations with TwelveLabs and LanceDB

[David Myriel](/author/david-myriel)

•

September 16, 2025

•

[Engineering](/category/engineering)

![1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c-fig-001](../images/1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

**💡 Notebook**

The code snippets in this article are shortened to keep things clear and concise. If you’d like to experiment with the full runnable version, you can find the complete notebook [**here**](https://colab.research.google.com/drive/1jZiMT1QFYGvPgrps2Vpge9CtlRKFY1L0?usp=sharing#scrollTo=046o2pt62413) .

Traditional recommendation engines usually depend on metadata—titles, tags, or transcripts. While useful, those signals don’t capture the deeper meaning of what’s happening inside a video. Imagine if your system could actually understand the visuals, audio, and context of the content itself.

That’s exactly what we’ll build in this tutorial: a semantic video recommendation engine powered by [TwelveLabs](https://www.twelvelabs.io/), [LanceDB](/), and [Geneva](https://docs.lancedb.com/geneva).

* [**TwelveLabs**](https://www.twelvelabs.io/) provides multimodal embeddings that encode the narrative, mood, and actions in a video, going far beyond keyword matching.
* [**LanceDB**](https://lancedb.com/) stores these embeddings together with metadata and supports fast vector search through a developer-friendly Python API.
* [**Geneva**](https://docs.lancedb.com/geneva) , built on [**LanceDB**](https://lancedb.com/) and powered by [**Ray**](https://lancedb.com/blog/lance-namespace-lancedb-and-ray/) , scales the entire pipeline seamlessly from a single laptop to a large distributed cluster—without changing your code.

## Why this stack?

* [**TwelveLabs**](https://www.twelvelabs.io/) : captures narrative flow and meaning, enabling natural queries like “a surfer riding a wave at sunset” to return relevant matches even without explicit tags.
* [**LanceDB**](https://lancedb.com/) : a modern vector database built on [**Apache Arrow**](https://arrow.apache.org/) , with:
  + A simple, intuitive Python interface.
  + Embedded operation—no external services required.
  + Native multimodal support for video, images, text, and vectors in the same table.
* [**Geneva**](https://docs.lancedb.com/geneva) : extends LanceDB for distributed processing. With [**Ray**](https://lancedb.com/blog/lance-namespace-lancedb-and-ray/) under the hood, it parallelizes embedding generation and large-scale searches.

## Loading and Materializing Videos

The first step is to **load your dataset** into LanceDB. Here, we’re pulling in videos from [HuggingFace](https://huggingface.co/)’s [`HuggingFaceFV/finevideo`](https://huggingface.co/datasets/HuggingFaceFV/finevideo) dataset.

`‍`Here we stream the dataset to save memory and only process 10 rows for the demo. Each item stores the raw video bytes plus helpful metadata, producing a PyArrow RecordBatch that keeps video and metadata together.

Now we persist this dataset into **LanceDB using Geneva**:

`geneva.connect()` starts a local LanceDB instance, `create_table()` writes the dataset to `videos`, and `mode="overwrite"` resets the table.

At this point, we have a **LanceDB table of videos** ready for embedding and search.

## Embedding Videos with TwelveLabs

Next, we use **TwelveLabs’ Marengo model** to generate embeddings from the raw video files.

Here we submit an embedding job to TwelveLabs, request both clip and whole‑video embeddings, then convert the result to a NumPy array for storage and search.

With **Geneva**, embeddings are automatically stored as another column:

`add_columns()` adds an `embedding` column powered by `GenVideoEmbeddings`, and `backfill()` computes it for all rows (increase `concurrency` in production).

At this stage, every video in our LanceDB table has a **semantic embedding** attached.

## Searching with LanceDB

With embeddings stored, LanceDB can run vector search queries.

Here we embed the query into `qvec`, open the `videos` table, run `.search(qvec)` with cosine similarity, and return the top matches as a pandas DataFrame. This is semantic search in action.

## Summarizing with Pegasus

Embeddings alone provide similarity, but they don’t explain *why* a result was returned. For better UX, TwelveLabs also provides **Pegasus**, a summarization model:

`pegasus1.2` creates short multimodal summaries you can store alongside results to make recommendations easier to understand.

## Scaling with Geneva and Ray

Small datasets can be managed manually, but at **enterprise scale** you need automation. Geneva + Ray handle this:

| Concern | LanceDB only | With Geneva and Ray |
| --- | --- | --- |
| Ingestion | Manual loaders | Declarative pipelines |
| Embeddings | Sequential | Parallel across many workers |
| Storage | Local tables | Distributed LanceDB tables |
| ML/Analytics | Custom scripts | Built-in distributed UDFs |

Here we declare the pipeline once and run it anywhere. Ray parallelizes the work so you can scale from a laptop to a large cluster without changing your code.

## Try it out

By combining [TwelveLabs](https://www.twelvelabs.io/), [LanceDB](/), and [Geneva](https://docs.lancedb.com/geneva) you can build a recommendation system that **understands video content directly**.

* [**TwelveLabs Playground**](https://playground.twelvelabs.io/) – Sign up for an API key and start generating video embeddings right away
* [**LanceDB Quickstart**](https://docs.lancedb.com/quickstart) – Install LanceDB locally and try your first vector search with Python
* [**Geneva Documentation**](https://docs.lancedb.com/geneva) – Learn how to scale pipelines and run distributed embedding jobs with Ray
* [**Complete Notebook**](https://colab.research.google.com/drive/1jZiMT1QFYGvPgrps2Vpge9CtlRKFY1L0?usp=sharing#scrollTo=046o2pt62413) – Explore the full runnable code with all the details

![1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c-fig-002](../images/1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c/figure-002.avif)

[David Myriel](/author/david-myriel)

Writer, Software Engineer

[GitHub](https://github.com/davidmyriel)[Linkedin](https://www.linkedin.com/in/davidmyriel/)[Twitter](https://x.com/davidmyriel)

![1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c-fig-003](../images/1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c-fig-004](../images/1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c-fig-005](../images/1443-https-www-lancedb-com-blog-geneva-twelvelabs-b41cce0c/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb