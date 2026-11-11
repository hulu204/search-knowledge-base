---
title: 'How BBQ shrinks Jina v5 embeddings by 29x without losing recall in Elasticsearch'
company: Elastic
tag: 索引构建
date: 2026-07-10
url: https://www.elastic.co/search-labs/blog/bbq-quantization-jina-embeddings-v5
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How BBQ shrinks Jina v5 embeddings by 29x without losing recall in Elasticsearch

A hands-on test comparing BBQ and float32 vector indices in Elasticsearch, measuring memory, disk and recall@10 across five languages.

July 10, 2026

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

[Vector Database](/search-labs/blog/category/vector-database)[Jina AI](/search-labs/blog/category/jina-ai)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

[BBQ quantization](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) cuts the memory footprint of [Jina embeddings v5](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text) vectors by 29x in Elasticsearch. Recall@10 holds at 0.994 against a full-precision `float32` baseline. We tested this on a multilingual news corpus across five languages, using `jina-embeddings-v5-text-small` to build a raw `float32` index and a `bbq_hnsw` index from the exact same [vectors](https://www.elastic.co/what-is/vector-embedding). Then we measured memory, disk usage and retrieval quality on both. Disk usage came out nearly identical between the two indices. In-memory footprint is the number that actually decides whether your cluster fits the corpus, and it dropped from 12.71 MB to 0.44 MB for this test set. Jina v5's quantization-aware training is why the recall held.

## Prerequisites

* Elasticsearch 9.x with `jina-embeddings-v5-text-small` inference endpoint available.
* Python 3.10+,
* Elasticsearch API key,

## What is quantization?

An *embedding* is a list of numbers. By default, each number is a `float32`, which uses 4 bytes. *Quantization* stores each number with fewer bits, trading precision for space.

Like a JPEG, a *quantized vector* is a smaller, lower-fidelity copy of the original that still gets the job done.

![Cat photo at decreasing JPEG quality, illustrating the quantization trade-off between size and detail](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1ddbaed3b3d80b67/6a54faf78f017d26529ee65c/175105f9a5059885aaf92268c2ab70b2e4e3dd6f-519x600.png)

*Gradual decrease of JPEG quality (image by Michael Gäbler,* [*CC BY 3.0*](https://creativecommons.org/licenses/by/3.0/) *via Wikimedia Commons).*

| Name | Bytes / dim | 1024-d vector | Compression |
| --- | --- | --- | --- |
| `Float` (Baseline) | 4 | 4096 B | 1x |
| `int8` | 1 | 1024 B | 4x |
| `int4` | 0.5 | 512 B | 8x |
| `bbq` | ~0.14 | 142 B | ~29x |

## What is BBQ?

Better Binary Quantization (BBQ) is Elasticsearch's 1-bit quantization mode for dense vectors. Each dimension of the vector is stored as a single bit, plus a few corrective bytes per vector. Then, a rescoring step is applied at query time. This keeps the final retrieval quality close to a full precision search.

For the math behind each level, see [Scalar quantization 101](https://www.elastic.co/search-labs/blog/scalar-quantization-101), [Optimized Scalar Quantization](https://www.elastic.co/search-labs/blog/optimized-scalar-quantization-elasticsearch), and the [BBQ deep dive](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch).

### How does BBQ preserve search accuracy?

Plain 1-bit quantization leads to too high a search quality degradation on its own. BBQ maintains high retrieval quality through three mechanisms:

1. **Asymmetric precision:** Stored vectors use 1 bit per dimension.
2. **Corrective factors:** A few floats per vector record the rounding error and correct distances at scoring time.
3. **Oversample and rescore:** BBQ scans candidates with the bits and then reranks the top ones with higher precision. Fetching the top 10 means scanning about 30 candidates.

The result is the vectors that are roughly 32x smaller, with retrieval quality close to full precision. In the next section of the article, we’ll measure the memory savings and the recall on a real corpus.

## How Jina embeddings v5 works

Jina embeddings v5 is a multilingual embedding model with quantization-aware training, which makes it a natural fit for BBQ in Elasticsearch: The 1024-dimensional vectors from `jina-embeddings-v5-text-small` sit above the dimensional floor where binary quantization stays accurate, and the model is trained so that 1-bit quantization loses little quality. Its main features are:

* **One model for many tasks:** v5 uses small [Low-Rank Adaptation (LoRA) adapters](https://arxiv.org/abs/2106.09685) on top of a single base model, one for each task: *retrieval*, *text-matching*, *clustering*, and *classification*. Elasticsearch [picks the right adapter automatically](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text#getting-started) at index and query time.
* [**Matryoshka dimensions:**](https://arxiv.org/abs/2205.13147) v5 is trained so you can truncate the vector (1024, 512 to 256) and minimize search quality reduction. This is another way to shrink vectors, independent of quantization.
* **Quantization-aware training:** v5 is trained to work with BBQ, so its 1-bit vectors lose little accuracy.

We use `jina-embeddings-v5-text-small`. This model is available through [Elastic Inference Service](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis) (EIS) and outputs 1024 dimensions with 32k token context and is multilingual across 93 languages. That puts it above the [384-dimension threshold](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-quantization), below which Elasticsearch no longer defaults to `bbq_hnsw`.

Full model details are in the [Jina v5 article on Search Labs](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text).

## Setting up the BBQ vs. float32 comparison

We’ll create two indices: Both share mappings, and what changes is the `index_options.type` parameter, which tells Elasticsearch how to store the dense vector field (as raw `float32` HNSW or as 1-bit BBQ):

| Index | `index\_options` | Loaded into memory |
| --- | --- | --- |
| `vectors-float32` | `hnsw` | Raw `float32` with no quantization (baseline) |
| `vectors-bbq` | `bbq\_hnsw` | 1-bit BBQ quantization + corrective factors |

We then embed the corpus once with Jina v5, index those same vectors into both, and compare them on disk usage, memory footprint, and recall. You can follow along with the full [supporting blog content notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/quantizing-jina-embeddings-v5-bbq/quantization-jina-embeddings.ipynb).

### Connect to Elasticsearch

```
from elasticsearch import Elasticsearch, helpers

es_client = Elasticsearch(
    ELASTICSEARCH_URL, api_key=ELASTICSEARCH_API_KEY, request_timeout=120
)
es_client.info()
```

### Create the two indices

```
DIMS = 1024
FLOAT_INDEX = "vectors-float32"
BBQ_INDEX = "vectors-bbq"

def create_index(name, index_options):
    if es_client.indices.exists(index=name):
        es_client.indices.delete(index=name)

    es_client.indices.create(
        index=name,
        mappings={
            "properties": {
                "text": {"type": "text"},
                "lang": {"type": "keyword"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": DIMS,
                    "index": True,
                    "similarity": "cosine",
                    "index_options": index_options,
                },
            }
        },
    )

create_index(FLOAT_INDEX, {"type": "hnsw"})       # raw float32 baseline
create_index(BBQ_INDEX,   {"type": "bbq_hnsw"})   # 1-bit BBQ
```

*Note: In production, you can use* [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text) *to let Elasticsearch manage the mapping and inference endpoint automatically.*

### Point at the Jina v5 inference endpoint

We call the model `jina-embeddings-v5-text-small` directly (no need to create an [inference endpoint](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-put)) to turn text into vectors.

```
INFERENCE_ID = ".jina-embeddings-v5-text-small"

def embed(texts, batch_size=16):
    out = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]

        try:
            resp = es_client.inference.text_embedding(
                inference_id=INFERENCE_ID, input=batch
            )
        except AttributeError:  # older client versions
            resp = es_client.inference.inference(inference_id=INFERENCE_ID, input=batch)
        out.extend(item["embedding"] for item in resp["text_embedding"])

    return np.array(out, dtype=np.float32)

embed(["hello world"]).shape # testing
```

As result of the test, we got:

```
(1, 1024)
```

### Load a multilingual news dataset

We stream real news articles from [hotchpotch/multilingual\_cc\_news](https://huggingface.co/datasets/hotchpotch/multilingual_cc_news), a parquet mirror of CC-News. We take about 1,000 articles from five languages (around 3,000 docs total), plus a small held-out set of headlines to use as search queries. Using multiple languages also lets Jina v5 show its multilingual strength.

```
from datasets import load_dataset

LANGS = ["en", "de", "ja", "pt", "ru"]
PER_LANG_DOCS = 1000
PER_LANG_QUERIES = 20

docs, queries = [], []
for lang in LANGS:
    ds = load_dataset(
        "hotchpotch/multilingual_cc_news", lang, split="train", streaming=True
    )
    rows = [
        r
        for r in ds.take(PER_LANG_DOCS + PER_LANG_QUERIES)
        if r.get("maintext") and r.get("title")
    ]

    for row in rows[:PER_LANG_DOCS]:
        text = (row["title"] + ". " + row["maintext"]).replace("\n", " ").strip()
        docs.append({"text": text[:1000], "lang": lang})

    for row in rows[PER_LANG_DOCS:]:
        queries.append({"text": row["title"], "lang": lang})  # headlines as queries

print(f"Corpus: {len(docs)} docs | Queries: {len(queries)}")

# RES: Corpus: 3102 docs | Queries: 18
```

### Generate the embeddings and bulk index

We embed the corpus a single time and feed those exact vectors into both indices.

```
doc_vectors = embed([d["text"] for d in docs])
query_vectors = embed([q["text"] for q in queries])
```

```
def index_docs(name):
    actions = (
        {
            "_index": name,
            "_id": i,
            "_source": {
                "text": d["text"],
                "lang": d["lang"],
                "embedding": doc_vectors[i].tolist(),
            },
        }
        for i, d in enumerate(docs)
    )
    helpers.bulk(es_client, actions, refresh=True)

for name in (FLOAT_INDEX, BBQ_INDEX):
    index_docs(name)
    es_client.indices.forcemerge(index=name, max_num_segments=1)
    es_client.indices.refresh(index=name)
```

We [force-merge](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-forcemerge) to a single segment so the storage numbers are stable and comparable.

## Results: Disk versus memory

The [disk usage API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-indices-disk-usage) reports how many bytes each index spends on vectors (`knn_vectors`).

```
def vector_disk_bytes(name):
    du = es_client.indices.disk_usage(index=name, run_expensive_tasks=True)
    field = du[name]["fields"]["embedding"]
    knn = field.get("knn_vectors")
    if isinstance(knn, dict):
        return knn["size_in_bytes"]
    return field["knn_vectors_in_bytes"]

float_disk = vector_disk_bytes(FLOAT_INDEX)
bbq_disk = vector_disk_bytes(BBQ_INDEX)

N = len(docs)
float_mem = N * DIMS * 4
bbq_mem = N * (DIMS // 8 + 14)

print(f"On disk   -> float32: {float_disk/1e6:6.2f} MB | BBQ: {bbq_disk/1e6:6.2f} MB")
print(f"In memory -> float32: {float_mem/1e6:6.2f} MB | BBQ: {bbq_mem/1e6:6.2f} MB  ({float_mem/bbq_mem:.0f}x smaller)")
```

Result:

```
On disk   -> float32:  12.80 MB | BBQ:  13.25 MB
In memory -> float32:  12.71 MB | BBQ:   0.44 MB  (29x smaller)
```

On disk, the two indices are about the same size. A quantized index still keeps the raw `float32` vectors (needed for rescoring and requantization during merges) and adds the 1-bit vectors on top, so BBQ ends up slightly larger on disk.

![ Float32 stores near-continuous values; BBQ quantization rounds each dimension to one of two levels](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt480f8d535f7a67cd/6a54faf95beed09a3ec5f836/c54fff3fe10273895d7fc16e3c8f215c3538d717-583x250.png)![BBQ quantization reduces vector storage from 4,096 bytes to 142 bytes per vector, a 29x reduction](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfc4b17790ac39e76/6a54fafb9eff160936b24e85/5cede02da4a8380ef5420d993f5addac25d925b5-590x249.png)

The real savings is in memory. The HNSW scan only needs the 1-bit vectors in RAM, while the raw floats are read from disk to rescore the top candidates. We size that footprint using the documented [kNN memory formulas](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/approximate-knn-search): `float` uses `num_vectors × dims × 4` and `bbq` uses `num_vectors × (dims/8 + 14)`.

BBQ's extra bytes on disk should match the 1-bit payload we computed for memory. Here, that’s `13.25 - 12.80 = 0.45 MB` versus the computed `0.44 MB`. They line up.

![BBQ quantization in Elasticsearch: similar disk usage, but memory drops from 12.7 MB to 0.4 MB](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb1ae4f838c0b1c44/6a54fafdffefbe0991dd3dea/bf231b0290bb0661d0425384d69cb90d0222b44d-740x440.png)

## Results: Recall

To check whether the quantized index returns results similar to the float baseline, we use recall:

`recall@k = | BBQ top-k ∩ float32 top-k | / k`, averaged over all queries.

We vary the oversampling factor (`num_candidates / k`) that’s the number of candidates BBQ scans with 1-bit vectors before reranking the top ones against the original floats to find the lowest value that still matches `float32`.

```
def search_ids(index, qvec, k=10, num_candidates=10):
    resp = es_client.search(
        index=index,
        size=k,
        _source=False,
        knn={
            "field": "embedding",
            "query_vector": qvec.tolist(),
            "k": k,
            "num_candidates": num_candidates,
        },
    )

    return [h["_id"] for h in resp["hits"]["hits"]]

K = 10

# Ground truth: full-precision float32 with a wide candidate list (~exact)
ground_truth = [
    set(search_ids(FLOAT_INDEX, qv, k=K, num_candidates=2000)) for qv in query_vectors
]

oversamples = [1, 2, 3, 5, 10]
recalls = []
for f in oversamples:
    num_candidates = max(K * f, K)
    hits = 0
    for gt, qv in zip(ground_truth, query_vectors):
        got = set(search_ids(BBQ_INDEX, qv, k=K, num_candidates=num_candidates))
        hits += len(got & gt)
    recalls.append(hits / (len(query_vectors) * K))
    print(f"oversample {f:>2}x -> recall@{K} = {recalls[-1]:.3f}")
```

As a result, we have:

![Recall@10 for BBQ quantization stays near 0.989 versus float32 across oversample factors 1x to 10x](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt96c062ee246abfd4/6a54faff600d773c12e424d3/e8604775a3f9bb47c473f2ac4686b926413bf4ad-640x440.png)

BBQ starts at 0.994 recall@10 at 1x oversampling, holds there up to 3x, and then settles at 0.989 at higher factors, meaning it returns at least 98.9% of the same top-10 documents as float32 across all oversampling values. For more on how recall varies across datasets under quantization, see [Fast vs. accurate: Measuring the recall of quantized vector search](https://www.elastic.co/search-labs/blog/recall-vector-search-quantization).

## BBQ quantization results summary

The same vectors, two storage formats, and one experiment:

* **Disk:** Roughly the same (`12.80 MB` versus `13.25 MB`). BBQ keeps the raw floats around for rescoring and merging.
* **Memory:** 29x smaller (`12.71 MB` versus `0.44 MB`). This is the number that decides whether your cluster fits the corpus.
* **Recall@10:** `0.994` at 1x oversampling. Quantization-aware training pays off.

When to enable BBQ: If your dimension count is above the [384-dim floor](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-quantization), if your vectors are the dominant memory cost, and if you can afford a few extra candidates to rescore. For Jina v5 specifically, the model is trained for it, so the recall hit on most corpora is small.

## Further reading on BBQ and vector quantization

* Run the full notebook from this article in the [supporting blog content repo](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/quantizing-jina-embeddings-v5-bbq/quantization-jina-embeddings.ipynb).
* For the math behind BBQ, see [Better Binary Quantization in Lucene and Elasticsearch](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch).
* For more on Jina v5's architecture, see [Jina embeddings v5 on Search Labs](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text).
* For a broader walkthrough on adopting BBQ, see [How to implement BBQ into your use case](https://www.elastic.co/search-labs/blog/bbq-implementation-into-use-case).
* For the original research behind BBQ, see the paper [RaBitQ: Quantizing High-Dimensional Vectors with a Theoretical Error Bound for Approximate Nearest Neighbor Search](https://arxiv.org/abs/2405.12497).

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