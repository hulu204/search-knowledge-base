---
title: 'https://www.lancedb.com/blog/opensearch-vs-lancedb-for-vector-search-query-cost-and-infrastructure'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/opensearch-vs-lancedb-for-vector-search-query-cost-and-infrastructure
account: 
origin: en-rss
---
# OpenSearch vs LanceDB for Vector Search: Query Cost and Infrastructure

[Justin Miller](/author/justin-miller)

•

May 11, 2026

•

[Engineering](/category/engineering)

![1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c-fig-001](../images/1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Choosing a vector database usually comes down to a tradeoff between a managed search service and an embedded library. OpenSearch and LanceDB sit on opposite ends of that spectrum: one runs as a distributed cluster with a rich feature set (full-text search, security, aggregations, multi-tenancy), the other as a columnar file format you query directly from your application. Both are good at vector search. This post sets ingestion aside and focuses on the steady-state question that dominates the bill once data is loaded: **what does it cost to run queries, and what infrastructure do you need to keep running?**

The workload is the same on both sides: 287,360 images from the COCO 2017 dataset, embedded with [Google’s SigLIP 2](https://huggingface.co/google/siglip2-so400m-patch14-384) (SoViT-400M, 384px) into 1152-dimensional, L2-normalized vectors. From there, costs are projected to 1M, 10M, and 100M documents.

## Setup

Both systems index the same data: 287,360 images from the COCO 2017 dataset, embedded with [Google's SigLIP 2](https://huggingface.co/google/siglip2-so400m-patch14-384) (SoViT-400M, 384px) into 1152-dimensional vectors, L2-normalized. The embeddings parquet is 46.6 GB with most of that is inline JPEG image bytes alongside the vectors and metadata.

| Metric/Component | Value |
| --- | --- |
| Dataset | COCO 2017 (all splits) |
| Images | 287,360 |
| Embedding model | `google/siglip2-so400m-patch14-384` |
| Vector dimensions | 1152 |
| Normalization | L2 (unit vectors) |
| Average image size | ~160 KB JPEG |

Both systems use the same vectors and the same image set. The difference is where each piece lives, not what it is.

## Storage Architecture

The two systems split bytes differently between expensive (RAM/EBS attached to a search node) and cheap (object storage) tiers.

### OpenSearch: Vectors on the Cluster, Images in S3

```
OpenSearch cluster
├── HNSW index (Lucene segments, RAM + EBS)
└── document fields: image_id, caption, s3_uri ──┐
                                                 │
S3 bucket (separate)                             │
└── 287,360 JPEG files (~46 GB) ◄────────────────┘
```

OpenSearch documents store the vector, the metadata fields, and an `s3_uri` (or path) pointing at the image. The Lucene HNSW graph and the vectors themselves live on the search node (partly in RAM, partly on EBS) and the application fetches the image from S3 after the search returns the URI. This is a clean split: the search node handles ranking, S3 handles bulk storage. It does mean two systems to operate (search cluster + bucket policy), but image bytes never touch the cluster’s RAM, EBS, or replication pipeline.

### LanceDB: Everything in Lance Format

```
S3 bucket
└── coco_clip_embeddings.lance/
    ├── vectors (1152-dim float32, optionally SQ8)
    ├── metadata (image_id, caption, etc.)
    └── image_bytes (raw JPEG, lazily read)
```

LanceDB stores vectors, metadata, and image bytes together as columns in Lance files on S3. Lance is columnar, so a nearest-neighbor search reads only the vector and metadata columns; the `image_bytes` column is fetched lazily, by row, when the application accesses it. The index is built and persisted alongside the data, in the same S3 prefix.

### What’s Equivalent (and What Isn't)

Image storage cost is essentially the same in both designs: ~160 KB JPEGs sitting in S3 Standard at $0.023/GB/month. What differs is what runs on the always-on tier: OpenSearch keeps vectors and the HNSW graph hot on a search node; LanceDB pulls index pages from S3 into a memory-mapped cache on demand. That distinction is what drives the cost curves below.

## Query Results

Both systems return the same top result for a query using the first image embedding (a man on a moped):

#### **OpenSearch**

```
Rank   Score      Image ID     Caption
1      1.0000     391895       A man with a red helmet on a small moped on a di...
2      0.9064     252839       cattle grazing on grass along the side of a road...
3      0.9033     253446
4      0.8949     490582       A man and a woman on a motorcycle in helmets.
5      0.8941     550859
```

#### **LanceDB**

```
Rank   Distance   Image ID     Caption
1      0.0000     391895       A man with a red helmet on a small moped on a di...
2      0.4941     580784
3      0.4995     579451
4      0.5030     169633       there is a man riding a bike and waving
5      0.5132     191824
```

OpenSearch reports cosine similarity (higher is better), LanceDB reports cosine distance (lower is better). Both retrieved the exact match at rank 1. The remaining results differ because OpenSearch uses Lucene’s HNSW with default parameters while LanceDB uses IVF\_HNSW\_SQ with scalar quantization; different approximate-nearest-neighbor structures will diverge past the exact match. Recall@10 against an exact baseline is comparable on this dataset (both well above 0.95) once each index is tuned.

Latency in single-client testing was sub-50 ms p95 on both systems for a top-10 query at 287K vectors. At higher QPS and larger corpora, the limiting factor shifts: OpenSearch is bounded by node CPU and HNSW graph traversal in RAM, LanceDB by S3 latency for cold pages and by partition fan-out for IVF.

### AWS Cost Comparison

The numbers below cover **steady-state query infrastructure only**, that is, the always-on cost of keeping the index queryable, not one-time ingestion or backfill. Pricing is us-east-1 on-demand at the time of writing.

A few shared assumptions to make this fair:

* Both indexes use scalar quantization to 8 bits (Lucene SQ for OpenSearch, IVF\_HNSW\_SQ for LanceDB), which roughly quarters the in-memory vector footprint vs. raw float32.
* OpenSearch sizing follows AWS’s guidance that the HNSW graph and quantized vectors should fit in roughly 50% of node RAM, with the remainder for the JVM, Lucene segments, and OS cache.
* LanceDB sizing assumes a single query node with a memory-mapped cache; the index is read from S3 with the working set served from local RAM/page cache.
* Image bytes (~160 KB × N) sit in S3 Standard at $0.023/GB/month for both systems.
* “Single instance” is shown for clarity. Production deployments typically add a replica/standby on each side, which doubles the compute line for both.
* S3 GET costs for LanceDB queries are listed separately at an assumed sustained 10 QPS (≈26M requests/month), they grow with query volume, not corpus size.

### Cost Model

Every line in the tables below comes out of the same handful of formulas. Let:

| Symbol | Meaning | Notes |
| --- | --- | --- |
| N | Number of documents, expressed in millions | Example: 100 for 100M |
| d | Vector dimensions | 1152 here |
| b | Bytes per vector element | 4 for float32, 1 for SQ8 |
| M | HNSW graph degree | Lucene default 16; LanceDB uses 32 |
| img\_KB | Average image size in KB | Approximately 160 |
| QPS | Sustained queries per second |  |

A useful identity to keep in mind: **1 GB ≈ 1 billion bytes ≈ 1 million KB**. That’s what lets the formulas below land in GB without scientific notation.

**Vector data.** Each vector takes `d × b` bytes; multiplied by N million docs gives gigabytes:

`vector_GB = N × d × b / 1000`

For 100M docs at d=1152, SQ8: `100 × 1152 × 1 / 1000 = 115.2 GB`. Raw float32 would be 4× that = 460.8 GB.

**HNSW graph memory.** Each node holds M edges as 4-byte ints in the bottom layer, with a small fraction of nodes appearing on upper layers. A practical upper bound:

`hnsw_GB ≈ N × M × 4 × 1.05 / 1000      # the 1.05 covers upper layers`

For 100M docs, M=16: `100 × 16 × 4 × 1.05 / 1000 ≈ 6.7 GB`.

**OpenSearch node RAM sizing.** AWS’s published guidance for the k-NN plugin is that the in-memory portion (vectors + graph) should occupy roughly half of node RAM, leaving the rest for the JVM heap, segment cache, and OS:

`required_RAM_GB = 2 × (vector_GB + hnsw_GB)`

For 100M, SQ8, M=16: `2 × (115.2 + 6.7) ≈ 244 GB`. The smallest Amazon OpenSearch Service instance that comfortably holds that with headroom for merges and snapshots is r6g.12xlarge.search at 384 GB.

**EBS for OpenSearch index segments.** Lucene segment files on disk are roughly the same size as the in-memory index, plus headroom for merges (a 2× rule of thumb is standard) and a small per-document metadata footprint (call it 500 bytes for `image_id`, `s3_uri`, `caption`). With 500 bytes/doc, metadata weighs `N × 0.5 GB` for N million docs:

`index_disk_GB = 2 × (vector_GB + hnsw_GB + N × 0.5)`

For 100M: `2 × (115.2 + 6.7 + 50) ≈ 344 GB`. At gp3’s $0.08/GB-month that’s about $28/month.

**S3 image storage.** Same on both systems. With image size in KB and N in millions, image storage in GB is just the product:

`image_storage_GB = N × img_KB  
S3_image_cost    = image_storage_GB × $0.023/GB-month`

For 100M docs at 160 KB/image: `100 × 160 = 16,000 GB`, so `16,000 × $0.023 ≈ $368/month`.

**S3 storage for LanceDB vectors + metadata.** LanceDB persists the quantized vectors and metadata columns alongside the images in the same Lance dataset, so this just adds the non-image bytes to S3:

`lancedb_index_GB = vector_GB + N × 0.5  
S3_index_cost    = lancedb_index_GB × $0.023/GB-month`

For 100M, SQ8: `115.2 + 50 ≈ 165 GB → $3.80/month`.

**Compute, monthly.** AWS bills hourly; one month ≈ 730 hours:

`compute_per_month = hourly_price × 730`

So r6g.12xlarge.search at $4.024/hr is `4.024 × 730 ≈ $2,937/month`; c6g.4xlarge at $0.544/hr is `0.544 × 730 ≈ $397/month`.

**S3 GET costs for LanceDB queries.** S3 Standard charges $0.0004 per 1,000 GET requests in us-east-1, which is the same as $0.40 per million; both forms appear in AWS documentation. Assume each query reads, on average, one coalesced range (Lance batches partition reads). With 86,400 seconds/day × 30 days/month ≈ 2.6 million seconds/month:

`gets_per_month_M = QPS × 2.6        # in millions of GETs  
S3_get_cost      = gets_per_month_M × $0.40        # i.e. gets × $0.0004 / 1,000`

At 10 QPS: `10 × 2.6 ≈ 26 million requests`, so `26 × $0.40 ≈ $10.40/month`. Linear in QPS, independent of corpus size.

```
vector_GB         = 100 × 1152 × 1 / 1000        = 115.2 GB
hnsw_GB           = 100 × 16 × 4 × 1.05 / 1000   =   6.7 GB
required_RAM_GB   = 2 × (115.2 + 6.7)            = 243.8 GB  → r6g.12xlarge.search (384 GB)
metadata_GB       = 100 × 0.5                    =    50 GB
index_disk_GB     = 2 × (115.2 + 6.7 + 50)       =   344 GB

OpenSearch compute = $4.024/hr × 730 hr          = $2,937/mo
OpenSearch EBS     = 344 GB × $0.08/GB-mo        =    $28/mo
S3 images          = 100 × 160 = 16,000 GB × $0.023  =  $368/mo
OpenSearch total                                 ≈ $3,333/mo

LanceDB compute    = $0.544/hr × 730 hr          =   $397/mo
LanceDB index S3   = (115.2 + 50) GB × $0.023    =     $4/mo
S3 images          = 16,000 GB × $0.023          =   $368/mo
S3 GETs @ 10 QPS   = 26 million × $0.40/M        =    $10/mo
LanceDB total                                    ≈   $779/mo
```

The same formulas drive every row in the tables below, only N changes.

#### 287K Documents (~46 GB images)

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.large.search (16 GB, 2 vCPU) | c6g.medium (2 GB, 1 vCPU) |
| Compute (730 hr) | $122/mo | $25/mo |
| EBS / index storage | ~$2/mo (gp3, 20 GB) | $0 (in S3 below) |
| S3 (vectors+metadata) | n/a | <$1/mo |
| S3 (images, ~46 GB) | ~$1/mo | ~$1/mo |
| S3 GETs @ 10 QPS | n/a | ~$10/mo |
| Total | ~$125/mo | ~$37/mo |

At this scale OpenSearch fits comfortably on the smallest managed node. LanceDB runs on a tiny compute-optimized instance because the working set is well under 1 GB.

#### 1M Documents (~160 GB images)

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.xlarge.search (32 GB, 4 vCPU) | c6g.large (4 GB, 2 vCPU) |
| Compute (730 hr) | $245/mo | $50/mo |
| EBS / index storage | ~$5/mo (gp3, 60 GB) | $0 |
| S3 (vectors+metadata) | n/a | ~$1/mo |
| S3 (images, ~160 GB) | ~$4/mo | ~$4/mo |
| S3 GETs @ 10 QPS | n/a | ~$10/mo |
| Total | ~$254/mo | ~$65/mo |

#### 10M Documents (~1.6 TB images)

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.4xlarge.search (128 GB, 16 vCPU) | c6g.xlarge (8 GB, 4 vCPU) |
| Compute (730 hr) | $980/mo | $100/mo |
| EBS / index storage | ~$3/mo (gp3, 35 GB) | $0 |
| S3 (vectors+metadata) | n/a | ~$1/mo |
| S3 (images, ~1.6 TB) | ~$37/mo | ~$37/mo |
| S3 GETs @ 10 QPS | n/a | ~$10/mo |
| Total | ~$1,020/mo | ~$148/mo |

At 10M with the formulas above: `vector_bytes = 11.5 GB`, `hnsw_bytes ≈ 0.7 GB`, so `required_RAM ≈ 24 GB`, the r6g.4xlarge.search (128 GB) has comfortable headroom. LanceDB’s working set during a typical IVF probe is a small fraction of the index, so a c6g.xlarge with a memory-mapped cache is enough.

#### 100M Documents (~16 TB images)

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.12xlarge.search (384 GB, 48 vCPU) | c6g.4xlarge (32 GB, 16 vCPU) |
| Compute (730 hr) | $2,937/mo | $397/mo |
| EBS / index storage | ~$28/mo (gp3, 344 GB) | $0 |
| S3 (vectors+metadata) | n/a | ~$4/mo (SQ8) |
| S3 (images, ~16 TB) | ~$368/mo | ~$368/mo |
| S3 GETs @ 10 QPS | n/a | ~$10/mo |
| Total | ~$3,333/mo | ~$779/mo |

These are the numbers from the worked example above. Even with a wide compute gap, image storage in S3 is the same on both sides because the image strategy is identical (the bytes live in S3 either way). The compute delta is what’s left after equalizing storage.

### What’s Driving the Curves

There are three main forces behind the cost curves:

1. **OpenSearch compute scales with the in-memory index size.** Even with quantization, the HNSW graph + quantized vectors must fit on a node’s RAM to hit single-digit-millisecond latencies. When the workload crosses a node-size threshold, the compute cost steps up sharply.
2. **LanceDB compute scales with QPS, not corpus size.** Index pages come from S3 and are cached in RAM as queries touch them. A larger corpus can lead to more cold-page reads, but the steady-state memory footprint depends on the hot working set created by the query pattern.The tradeoff is per-query S3 GET costs that grow linearly with traffic.
3. **Image storage costs are essentially the same in both designs.** In both cases, the image bytes live in S3, so that part of the cost curve is identical at each scale. The cost difference comes from where the vector index is stored and served from.

OpenSearch can narrow the compute gap further with binary quantization (32× memory reduction) or by moving cold partitions to disk-based ANN, at the cost of recall and tail latency. LanceDB can absorb higher QPS by adding read replicas (each is just another small EC2 reading the same S3 prefix) or by enabling an SSD-backed cache to cut S3 GETs. Both have levers; the table above uses the most common configuration on each side.

## Index Configuration

#### OpenSearch (Lucene HNSW, SQ8)

```
"settings": {
    "index": {
        "knn": True,
        "knn.algo_param.ef_search": 100,
    }
},
"mappings": {
    "properties": {
        "embedding": {
            "type": "knn_vector",
            "dimension": 1152,
            "method": {
                "name": "hnsw",
                "space_type": "cosinesimil",
                "engine": "lucene",
                "parameters": {"encoder": {"name": "sq"}},
            },
        },
        "s3_uri":   {"type": "keyword"},
        "image_id": {"type": "keyword"},
        "caption":  {"type": "text"},
    }
}
```

#### LanceDB (`IVF_HNSW_SQ`)

```
num_partitions = 1 if num_rows < 1_000_000 else int(math.sqrt(num_rows))
m = 32 if num_rows > 100_000 else 20
ef_construction = 400 if num_rows > 500_000 else 300

table.create_index(
    metric="cosine",
    vector_column_name="vector",
    index_type="IVF_HNSW_SQ",
    num_partitions=num_partitions,
    m=m,
    ef_construction=ef_construction,
)
```

Both indexes use 8-bit scalar quantization on the vectors and HNSW for the graph traversal. LanceDB layers an IVF partitioning step on top, which is what lets it touch a small fraction of the index per query at large corpora.

### Operational Complexity

| Concern | OpenSearch | LanceDB |
| --- | --- | --- |
| Runtime | Managed cluster (or JVM in your container) | Embedded library / sidecar process |
| Dependencies | OpenSearch domain, IAM, VPC | pip install lancedb, S3 bucket |
| Other features available | Full-text, BM25, aggregations, security, multi-tenancy | Vector + columnar scans only |
| Scaling out | Add data nodes, rebalance shards | Add read replicas reading the same S3 prefix |
| Image serving | Application reads from S3 by URI | Returned in query results, lazily fetched |
| Backup | Snapshot API to S3 | Lance files already in S3 |
| Can scale to zero | No, domain runs 24/7 | Yes, queryable from cold S3 |

#### OpenSearch: Vectors + References

```
OpenSearch Container (Docker/JVM)
├── HNSW index in JVM heap (~2.7 GB)
├── Lucene segments on EBS (~1.8 GB)
└── image_path: "data/coco_images/000000391895.jpg" <-- just a string

S3 / CDN / Filesystem (separate)
└── 287,360 JPEG files (~55 GB)
```

OpenSearch stores vectors in JVM heap for kNN search. The HNSW graph must fit entirely in memory. Images live somewhere else entirely. Your application needs to resolve the path, fetch the file, and serve it. That's additional infrastructure to deploy, secure, and pay for.

#### LanceDB: Everything Inline

```
Lance files on disk/S3
└── coco_clip_embeddings.lance/
    ├── vectors (1152-dim float32)
    ├── metadata (image_id, caption, etc.)
    └── image_bytes (raw JPEG)        <-- stored inline, ~46 GB total
```

LanceDB stores vectors, metadata, and image bytes together in columnar Lance files. A search query returns everything, including the image, in a single read.

```
results = table.search(query_vec).limit(10).to_pandas()
img = Image.open(io.BytesIO(results.iloc[0]["image_bytes"]))
```

The Lance format is columnar with data stored in fragments, so reading vectors for search doesn't touch the image bytes column. Only when you access `image_bytes` does it read those pages. Memory-mapping lets the OS handle caching. LanceDB doesn't load everything into RAM.

### AWS Cost Comparison

Using the cost estimator from the project at three scales:

#### 287K Documents (This Benchmark)

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.large.search (16 GB, 2 vCPU) | c6g.medium (2 GB, 1 vCPU) |
| Compute | $0.167/hr | $0.034/hr |
| Storage | EBS $0.0002/hr + S3 images $0.002/hr | S3 $0.002/hr |
| Total | $0.17/hr ($125/mo) | $0.04/hr ($26/mo) |
| Ratio | - | 4.7x cheaper |

OpenSearch needs a memory-optimized instance because the HNSW graph lives in JVM heap. LanceDB memory-maps from disk, so a 2 GB compute-optimized instance is sufficient.

#### 1M Documents

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.xlarge.search (32 GB, 4 vCPU) | c6g.medium (2 GB, 1 vCPU) |
| Total | $0.34/hr ($248/mo) | $0.04/hr ($30/mo) |
| Ratio | - | 8.4x cheaper |

At 1M vectors, OpenSearch needs to double its instance size. LanceDB stays on the same instance. The working set (memory-mapped pages actually accessed during queries) is still well under 1 GB.

#### 10M Documents

| Component | OpenSearch | LanceDB |
| --- | --- | --- |
| Instance | r6g.8xlarge.search (256 GB, 32 vCPU) | c6g.xlarge (8 GB, 4 vCPU) |
| Total | $2.74/hr ($1,976/mo) | $0.20/hr ($143/mo) |
| Ratio | - | 13.8x cheaper |

At 10M vectors with 1152 dimensions, OpenSearch needs 94 GB of JVM heap for the HNSW graph. That requires an r6g.8xlarge, a 256 GB machine at $2.67/hr just for compute. LanceDB's working set is ~2 GB, served by a $0.14/hr instance.

#### Why the Gap Widens

OpenSearch cost scales with **RAM** because vectors must fit in JVM heap. Memory-optimized instances are expensive. LanceDB cost scales with **storage** (S3 at $0.023/GB/month) because it memory-maps columnar files and only loads the pages needed per query. Storage is cheap. As document counts grow, OpenSearch jumps to larger (and disproportionately expensive) instance tiers, while LanceDB's compute stays roughly flat.

```
Cost scaling (approximate):
  OpenSearch:  O(num_docs × dims × instance_price_per_GB_RAM)
  LanceDB:     O(num_docs × dims × s3_price_per_GB) + fixed_small_compute
```

## Index Configuration

#### OpenSearch

OpenSearch uses HNSW with Lucene's defaults. The kNN index is configured at index creation:

```
"settings": {
    "index": {
        "knn": True,
        "knn.algo_param.ef_search": 100,
    }
},
"mappings": {
    "properties": {
        "embedding": {
            "type": "knn_vector",
            "dimension": dim,
            "method": {
                "name": "hnsw",
                "space_type": "cosinesimil",
                "engine": "lucene",
            },
        },
    }
}
```

#### LanceDB

The `IVF_HNSW_SQ` index parameters are derived from table statistics:

```
# Single HNSW graph for tables under 1M rows
num_partitions = 1 if num_rows < 1_000_000 else int(math.sqrt(num_rows))

# More graph connectivity for larger tables
m = 32 if num_rows > 100_000 else 20
ef_construction = 400 if num_rows > 500_000 else 300

table.create_index(
    metric="cosine",
    vector_column_name="vector",
    index_type="IVF_HNSW_SQ",
    num_partitions=num_partitions,
    m=m,
    ef_construction=ef_construction,
)
```

Scalar quantization (SQ) compresses each float32 to 8 bits during search, reducing memory bandwidth with minimal recall loss. The index builds in 68 seconds for 287K vectors.

## Migration Path

The project includes a live migration script that reads from an OpenSearch index via scroll API and writes the data to LanceDB, while pulling image bytes inline:

```
# Scroll through OpenSearch documents
for doc in scroll_opensearch(client, INDEX_NAME):
    image_path = IMAGES_DIR / doc["file_name"]
    image_bytes = image_path.read_bytes() if image_path.exists() else b""

    records.append({
        "image_id": doc["image_id"],
        "vector": doc["embedding"],
        "image_bytes": image_bytes,  # inline the image
        # ... metadata fields
    })
```

You can migrate incrementally without needing to regenerate embeddings. The vectors come from OpenSearch, the images from disk, and everything lands in a single LanceDB table.

### Operational Complexity

| Concern | OpenSearch | LanceDB |
| --- | --- | --- |
| Runtime | JVM in Docker container | Embedded Python library |
| Dependencies | Docker/Podman, JVM tuning, REST API | `pip install lancedb` |
| Startup | `docker compose up`, wait for health check | `db = lancedb.connect("path")` |
| Scaling | Add nodes, rebalance shards | Add storage (S3/disk) |
| Image serving | Separate S3/CDN infrastructure | Included in query results |
| Backup | Snapshot API to S3 | Copy files |
| Monitoring | `_cat/indices`, `_cluster/health`, JMX | `table.count_rows()`, `ls -la` |
| Can scale to zero | No, domain runs 24/7 | Yes, just files on S3 |

OpenSearch’s higher base cost buys a host of added capabilities (full-text relevance, RBAC, aggregations, multi-tenancy) that LanceDB OSS doesn’t come with. If you need those, the comparison stops being apples-to-apples. See [LanceDB Enterprise](https://docs.lancedb.com/enterprise) for a scalable, distributed deployment of LanceDB with storage and compute separation and a host of additional features.

## When to Use Which

**Choose OpenSearch when:**

* You need vector search alongside full-text, BM25, filters, and aggregations in the same query
* You need built-in security, RBAC, and multi-tenancy
* You already operate the Elastic/OpenSearch ecosystem and the team’s expertise is there
* You want sub-10ms p99 latency at high QPS without tuning a cache layer

**Choose LanceDB when:**

* Vector search is a core part of your use case, not an add-on
* You want vectors, metadata, and binary payloads (multimodal data) in a single columnar storage layer
* Your workload is bursty and benefits from scaling read replicas independently of storage
* Cost matters and you’re willing to trade some feature breadth to handle larger scales at a lower operating cost

## Summary

1. **Image storage does not materially affect the cost comparison.** Both designs put image bytes in S3 at $0.023/GB/month; that line is identical at every scale.
2. **Where the index lives drives the cost.** OpenSearch keeps vectors + HNSW graph hot on a search node; LanceDB serves them from memory-mapped Lance files on S3.
3. **OpenSearch compute scales with index RAM.** With SQ8 quantization, the curve is gentler than raw float32, but crossing node-size boundaries still roughly doubles the bill.
4. **LanceDB compute scales with QPS.** Steady-state cost is dominated by a small compute instance plus S3 GETs that grow with traffic, not corpus size.
5. **Feature breadth is part of the price.** OpenSearch’s higher base cost buys full-text, security, and aggregations; if you need those, the gap shrinks.
6. **At 100M docs**, the worked example shows ~$3,333/mo for OpenSearch vs ~$779/mo for LanceDB on equivalent SQ8 indexes, about 4.3x, with image storage identical on both sides ($368/mo).

The numbers above are a worked example, not a universal claim. Different recall targets, latency SLOs, redundancy requirements, or feature needs (full-text, RBAC) will move both lines. The point is to compare like with like (same quantization, same image storage strategy) and surface the real driver: where the index lives.

All code, benchmarks, and the cost estimator are available at [opensearch-lancedb-migration](https://github.com/justinrmiller/opensearch-lancedb-migration).

The dataset is available on Hugging Face here: [jrmiller/coco-2017-siglip2-embeddings](https://huggingface.co/datasets/jrmiller/coco-2017-siglip2-embeddings)

![1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c-fig-002](../images/1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c/figure-002.avif)

[Justin Miller](/author/justin-miller)

Senior Software Engineer

[GitHub](https://github.com/justinrmiller)[Linkedin](https://linkedin.com/in/justinraymiller)

![1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c-fig-003](../images/1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c/figure-003.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c-fig-004](../images/1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c/figure-004.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c-fig-005](../images/1424-https-www-lancedb-com-blog-opensearch-vs-lancedb-a2b4cb0c/figure-005.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb