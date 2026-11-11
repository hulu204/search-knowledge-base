---
title: 'Unsupervised document clustering with Elasticsearch + Jina embeddings'
company: Elastic
tag: 工程相关
date: 2026-04-10
url: https://www.elastic.co/search-labs/blog/unsupervised-document-clustering-elasticsearch-jina-embeddings
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Unsupervised document clustering with Elasticsearch + Jina embeddings

A practical, reproducible approach to unsupervised document clustering with Elasticsearch and Jina embeddings.

April 10, 2026

[Matthew Adams](/search-labs/author/matthew-adams)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Jina AI](/search-labs/blog/category/jina-ai)

Jump to

Share

Vector search starts with a query, but what if you don't have one?

Organizations accumulate large document collections, like support tickets, legal filings, news feeds, research papers, and need to understand what's in them before they can ask the right questions. Without labels or training data, manually reviewing thousands of documents is impractical. Traditional search doesn't help when you don't know what to search for.

This post walks through an Elasticsearch-native approach to unsupervised document clustering and temporal story tracking that addresses this discovery problem. By the end, you can trace story arcs like this across days:

![Temporal story chains flowing across February 2025 — each colored path is a story persisting across days, with link width showing kNN overlap strength](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta8c243e0c5773440/6a17093fa6c2b98c86e7968c/100a60a7fb85da8ab3813fd071a82c93f2c3f318-1300x650.png)

**What you'll discover:**

* Why **clustering embeddings** (not retrieval embeddings) matter when you want topic discovery without a query.
* How density-probed centroid classification groups documents by topic using Elasticsearch k-nearest neighbor (kNN) and batched `msearch`.
* How [`significant_text`](https://www.elastic.co/docs/reference/aggregations/search-aggregations-bucket-significanttext-aggregation) can auto-label clusters so themes are readable without training a model.
* How temporal story chains link daily clusters to show how themes evolve from day to day.

**This post is generated from a runnable Jupyter Notebook.** The inline outputs you see throughout are real results from the pipeline. Clone the [companion notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/unsupervised-document-clustering-elasticsearch-jina-embeddings) to run it yourself.

The pipeline uses ~8,500 February 2025 articles from BBC News and The Guardian as a test corpus. News is convenient because it has clear temporal behavior, but the pattern applies anywhere document discovery matters: legal review, compliance monitoring, research synthesis, customer support triage.

**Stack:**

* [**Jina v5**](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text) **clustering embeddings:** Task-specific Low-Rank Adaptation (LoRA) adapters for topic grouping. [Jina has joined Elastic](https://www.elastic.co/blog/elastic-jina-ai), and its models are available natively through [Elastic Inference Service (EIS)](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis).
* **Elasticsearch:** Scalable [kNN](https://www.elastic.co/docs/solutions/search/vector/knn), `significant_text` labeling, and vector storage.
* [**DiskBBQ:**](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction) A disk-based vector index format that combines [Better Binary Quantization (BBQ)](https://www.elastic.co/docs/reference/elasticsearch/index-settings/bbq) with hierarchical k-means partitioning for approximate nearest neighbors (ANN) acceleration. This index partitioning is internal to vector search and separate from the density-probed clustering algorithm used in this post. `bbq_disk` stores quantized vectors on disk and keeps only partition metadata in heap, dramatically reducing resource requirements, compared to `bbq_hnsw`, while maintaining high recall.
* **Global clustering + daily temporal linking:** Discovery and story evolution.

**What you'll need:**

* An Elasticsearch deployment (Elastic Cloud, Elasticsearch Serverless, or Elastic Self-Managed 8.18+/9.0+): `bbq_disk` requires 8.18 or later. The optional diversify retriever section requires 9.3+ or serverless.
* A [Jina API key](https://jina.ai/embeddings/): The free tier includes 10 million tokens, which covers the core clustering pipeline (~4.25 million tokens). The optional retrieval-versus-clustering comparison uses a second embedding pass.
* A [Guardian API key](https://bonobo.capi.gutools.co.uk/register/developer) (free).

## Setup

Install required packages:

```
pip install elasticsearch pandas numpy plotly umap-learn python-dotenv pydantic-settings datasets requests
```

Optional (only if you run scraping helpers from this repo):

```
pip install beautifulsoup4
```

Then configure API keys in a `.env` file at the project root:

```
ELASTIC_CLOUD_ID=your-cloud-id        # or ELASTIC_HOST=https://...
ELASTIC_API_KEY=your-api-key
JINA_API_KEY=your-jina-key
GUARDIAN_API_KEY=your-guardian-key
```

This notebook calls `load_dotenv(override=True)`, so local `.env` values take precedence.

```
Connected to Elasticsearch
```

## Part 1: Discovery clustering - Why clustering embeddings?

Most vector search uses **retrieval embeddings** trained to match a *query* to relevant *documents*. That's perfect for search, but not for discovery. When you want to find what topics exist in a corpus without any query at all, you need embeddings that group similar documents together.

Jina v5 solves this with **task-specific Low-Rank Adaptation (LoRA) adapters**. LoRA adds small low-rank updates to targeted internal layers while keeping most base-model weights frozen, so the model behavior shifts toward a specific task without full retraining. The same base model produces different embeddings depending on the `task` parameter:

| Task | Trained for | Use case |
| --- | --- | --- |
| retrieval.passage | Query-document matching | Search, retrieval augmented generation (RAG) |
| clustering | Topic grouping (optimized for tight clusters) | Discovery, categorization |

The clustering adapter is trained to make documents about the same topic *closer* in embedding space and documents about different topics *further apart*. The visual comparison below makes the difference concrete.

### Retrieval vs. clustering: A visual comparison

To see the difference, a sample of documents is embedded with both task types. Clustering is performed in the original 1024-dimensional embedding space; Uniform Manifold Approximation and Projection (UMAP) is used only to project those embeddings into 2D for visualization. UMAP preserves local neighborhood structure, making it useful for comparing cluster separation.

Below, the same 480-document sample is embedded with both task types and projected to 2D with UMAP. Look for tighter, more separated color groups in the clustering panel.

```
    Full dataset: 8,495 articles
    Sources: guardian: 5749, bbc: 2746
    Date range: 2025-02-01 to 2025-02-28

    Sample: 480 docs across 8 sections
    section
    Film              60
    World news        60
    Australia news    60
    Opinion           60
    Football          60
    US news           60
    Sport             60
    Business          60

    Clustering embeddings: 480
    Retrieval embeddings:  480

    UMAP projection complete
```

![UMAP comparison of retrieval vs clustering embeddings](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4b3733dccad212b6/6a1709407d8d67aaeb70e6a4/9bcf7a744900560c1c6c63a2dc3af2f9bfd33e11-1100x500.png)

*Retrieval embeddings (left) spread topics broadly; clustering embeddings (right) produce tighter, more separated groups from the same documents.*

The clustering embeddings produce tighter, more visually distinct groups. The retrieval embeddings spread topics out more evenly, ideal for search (fine-grained similarity); but for discovery, tight topical clusters are what matters.

This is why `task="clustering"` is used for the rest of this walkthrough.

### Loading the dataset

The corpus combines two news sources for February 2025:

* **BBC News** via the [RealTimeData/bbc\_news\_alltime](https://huggingface.co/datasets/RealTimeData/bbc_news_alltime) HuggingFace dataset.
* **The Guardian** via the [Guardian Open Platform API](https://open-platform.theguardian.com/).

Having multiple sources helps validate that clustering finds *topics* rather than *source-specific style*.

```
    Total articles:  8,495
    
    Source breakdown:
    source
    guardian    5749
    bbc         2746
    
    Date range: 2025-02-01 → 2025-02-28
    Days covered: 28
    
    Sample article:
      Source:  guardian
      Title:   Carbon monoxide poisoning ruled out in death of Gene Hackman and wife, police sa
      Section: Film
      Text:    Authorities have ruled out that Gene Hackman and his wife, Betsy Arakawa, died from carbon monoxide poisoning earlier this week in their home in Santa Fe, New Mexico. The Santa Fe county sheriff, Adan...
```

### Embedding with the clustering task

The Jina v5 API is called with `task="clustering"` for all documents. Embeddings are cached to disk, so subsequent runs skip the API entirely.

The API call is straightforward. The `task` parameter is the key difference from typical embedding usage:

```
payload = {
    "model": "jina-embeddings-v5-text-small",
    "input": texts,
    "task": "clustering",  # ← This selects the clustering LoRA adapter
}
```

The timing below reflects a cache hit. First run against the API takes longer, depending on corpus size.

```
    Embeddings ready: 8,495 vectors of dimension 1024
    Time: 0.6s
```

### Indexing into a single Elasticsearch index

For discovery clustering, the full month goes into one index (`docs-clustering-all`). Daily partitioning comes later for temporal story linking.

The index mapping uses [`bbq_disk`](https://www.elastic.co/docs/reference/elasticsearch/index-settings/bbq) for the vector field:

```
{
  "embedding": {
    "type": "dense_vector",
    "dims": 1024,
    "index": true,
    "similarity": "cosine",
    "index_options": {
      "type": "bbq_disk"        // hierarchical k-means partitioning for ANN index lookup; separate from this post's clustering algorithm
    }
  }
}
```

A 1024-dimensional float32 vector is 4 KB. [`bbq_disk`](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction) uses hierarchical k-means to partition vectors into small clusters, binary-quantizes them, and stores the full-precision vectors on disk for rescoring. Only partition metadata lives in heap, so memory requirements stay low even for large corpora. For workloads that can afford more heap, [`bbq_hnsw`](https://www.elastic.co/docs/reference/elasticsearch/index-settings/bbq) builds a Hierarchical Navigable Small World (HNSW) graph for faster lookups at higher resource cost.

The [`dense_vector`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector) field type supports multiple quantization strategies: `bbq_disk` and `bbq_hnsw` are the best fits for high-dimensional embeddings like the 1024-dim vectors used here.

```
    Indexed 8,495 documents into docs-clustering-all
    Time: 57.5s
```

### Clustering: Density-probed centroid classification

Traditional clustering algorithms like HDBSCAN assume you can hold the full N×d vector matrix in memory and run repeated full-pass updates. For 8,495 documents at 1024 dimensions, that's manageable (~35 MB), but the approach doesn't scale to millions of documents without additional infrastructure.

This algorithm is conceptually similar to KMeans++ initialization with Voronoi assignment and a noise floor, but it uses Elasticsearch [kNN search](https://www.elastic.co/docs/solutions/search/vector/knn) as the compute primitive, keeping almost all work server-side:

1. **Sample 5% of documents** as density probes (random sample, minimum 50).
2. **Probe density via batched** [`msearch`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-msearch) **kNN**. Each probe fires a kNN query and records the mean similarity of its neighbours. High mean similarity = dense region of embedding space. [`msearch`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-msearch) sends multiple search requests in a single HTTP call, which is critical here: Density probing generates hundreds of kNN queries, and batching them avoids per-request overhead.
3. **Select high-density seeds with diversification**: Candidates above median density are sorted by density descending and greedily accepted only when their cosine similarity to every existing seed is below a separation threshold. This is the only client-side compute (~0.01s for 8k docs).
4. **Classify all docs against centroids via** `msearch` **kNN**: Each seed acts as a centroid; a kNN search retrieves nearby documents above a similarity threshold. Each document is assigned to whichever centroid returned it with the highest score. Small clusters are dissolved to noise.

Elasticsearch handles the heavy lifting: `msearch` for density probes, `msearch` for classification, and `significant_text` for labeling. For this corpus (8,495 docs), the 5% density-probe sample launches 425 kNN probe queries, which `msearch` batches into nine HTTP calls (at batch size 50), avoiding one-request-per-probe overhead. Combined with `bbq_disk` ANN lookup, this keeps the clustering stage fast and scalable. The kNN queries use a minimal [`num_candidates`](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/approximate-knn-search) value for speed during the clustering pass; production search queries should use higher `num_candidates` values to improve recall at the cost of latency.

Clusters have natural sizes determined by the embedding space density around each centroid, not by a hard `k` cap. Dense topic regions produce larger clusters; niche topics produce smaller ones.

#### Why not KMeans or HDBSCAN?

KMeans assumes spherical clusters and requires the full N×d matrix in memory. For corpora that fit in memory, [HDBSCAN](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html) is a strong alternative. It handles arbitrary cluster shapes and has well-understood density semantics.

The density-probed centroid approach targets a different niche: corpora where you want storage, retrieval, and clustering in one system, or where scale makes client-side matrix operations impractical. It uses Elasticsearch kNN as the compute primitive, handles arbitrary cluster sizes, and keeps nearly all computation server-side.

```
    Clustered global index in 31.6s
      Total clusters: 82
      Total noise:    2420 (28.5%)
      Density probes: 425 kNN queries via 9 _msearch HTTP calls
```

#### Understanding the noise rate

The ~28% noise rate is by design, not a failure mode. Documents that don't fit any dense cluster at the configured `similarity_threshold` are left unassigned rather than forced into a poor match. This acts as a quality gate: Opinion columns, short articles, and one-off stories naturally resist clustering because they lack the thematic density that defines a coherent group.

The threshold is tunable: Lowering `similarity_threshold` produces more aggressive clustering (more documents assigned, but looser clusters), while raising it tightens clusters and increases the noise fraction. For this corpus of mixed news content, ~30% noise is a reasonable operating point. Production deployments should tune the threshold against domain-specific quality criteria.

### Automatic labels with significant\_text

Now each cluster needs a human-readable label. Elasticsearch's `significant_text` aggregation finds terms that appear unusually often in a foreground set (the cluster) compared to a background set (the full corpus).

Under the hood, it uses a statistical heuristic (JLH score by default) that balances absolute and relative frequency shifts, no machine learning, no large language model (LLM) calls. A cluster about UK politics might surface terms like `starmer`, `labour`, `downing` because those terms are disproportionately common in that cluster compared to the overall news corpus.

For this global pass, labels are computed directly against `docs-clustering-all`, so both foreground and background are drawn from the full month. In Part 2, labeling uses the daily index pattern (`docs-clustering-*`), a wildcard that lets queries span all matching indices simultaneously, to give `significant_text` a broader background for better contrast.

A minimal query shape looks like this:

```
{
  "size": 0,
  "query": { "term": { "cluster_id": "72" } },
  "aggs": {
    "label_terms": {
      "significant_text": {
        "field": "text",
        "size": 5,
        "filter_duplicate_text": true
      }
    }
  }
}
```

`significant_text` also serves as a quality gate: Clusters that produce no significant terms have no distinguishing vocabulary. They're incoherent groupings that should be dissolved back to noise rather than given a misleading label.

A lightweight deterministic cleanup step removes noisy label terms (numeric tokens, generic words) and falls back to a representative headline when needed. This keeps labels Elasticsearch native while improving readability.

```
    Sample cluster labels:
      cluster   3  (200 docs)  arsenal | mikel | villa
      cluster   1  (198 docs)  volodymyr | ukrainian | kyiv
      cluster   0  (196 docs)  hostages | hamas | israeli
      cluster   4  (187 docs)  scrum | rugby | borthwick
      cluster  52  (185 docs)  fossil | renewable | renewables
      cluster  10  (156 docs)  labour | gwynne | mps
      cluster  40  (151 docs)  novel | novels | literary
      cluster  11  (149 docs)  mewis | sarina | wiegman
      cluster  44  (143 docs)  flooding | rainfall | rain
      cluster  13  (131 docs)  doge | musk | elon
      cluster  12  (128 docs)  murder | insp | knockholt
      cluster   5  (124 docs)  putin | backstop | starmer

    Reassigned 35 docs from incoherent clusters to noise
    Total docs: 8,495
    Clustered:  6,040 (71.1%)
    Noise:      2,455 (28.9%)
```

### Visualizing the clusters

The visualizations below show what the global clustering pass discovered: a date-wise breakdown of clustered versus noise documents, a UMAP projection of the full month, and a source-mix chart confirming that clusters reflect topics rather than sources.

![Daily distribution of clustered vs noise documents](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4ed087d8b6dac2a0/6a17094260084b44543c4501/99099f5adaa945ae4097c50b0d7151c7dd28872e-1000x400.png)

Daily distribution of clustered versus noise documents across February 2025.

![Full-month UMAP projection with all documents](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf5ca320bc91131ab/6a17094366c4f95828f8bfbf/477c6c7177942955a942f85f5c881da50e517915-1100x700.png)

*Full-month UMAP projection: Each colored island is a topic cluster, gray points are noise*

![UMAP projection showing clustered documents only](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5f554a6bc2bc367b/6a170945a929cfa7a1ae0947/4f4302556c8974c416842452cf33bca06e90b966-1100x700.png)

*Clustered documents only: Removing noise reveals the topical structure more clearly*

![[UMAP projection highlighting a single cluster](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8e40c26f89ce5523/6a17094747d49c147d2d8974/327f96a79e382ef30614cb0570aa7fccd822b8f8-1100x700.png)

*Focused view highlighting one cluster (Premier League football) against all others.*

![Source mix per cluster showing topic-based grouping](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf1dd2c19ae628f1d/6a1709481949f7a630e7a9a3/acfb1524a10e24d6ff2412e7c3ec0f2b3ac75193-900x600.png)

Source mix per cluster: Both BBC and Guardian appear in every major cluster, confirming topic-based rather than source-based grouping.

Each colored island in the UMAP represents a cluster: a group of articles about the same topic discovered purely from embedding similarity. The gray noise points are articles that didn't fit cleanly into any cluster (often short articles, opinion pieces, or one-off stories).

The source breakdown chart confirms that clusters contain articles from **both** BBC News and The Guardian. The clustering is finding *topics*, not *sources*, exactly what unsupervised discovery should produce.

### Exploring cluster breadth with the diversify retriever

Plain kNN returns the documents most similar to a cluster's centroid (the dense core). But real clusters cover subtopics. The [**diversify retriever**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/diversify-retriever) uses Maximal Marginal Relevance (MMR) to surface documents that are relevant to the centroid but also *different from each other*.

The key parameter is **λ (lambda)**:

* λ = 1.0 → pure relevance (same as plain kNN).
* λ = 0.0 → pure diversity (maximally spread results).
* λ = 0.5 → balanced: that is relevant to the topic, but covering different angles.

**Version note:** The diversify retriever is available on Elastic Cloud Serverless and Self-Managed Elasticsearch 9.3+. Earlier versions can still follow the clustering and temporal linking sections; only this exploration step requires the diversify retriever.

A minimal retriever request shape looks like this:

```
{
  "size": 8,
  "retriever": {
    "diversify": {
      "type": "mmr",
      "field": "embedding",
      "lambda": 0.5,
      "query_vector": "<cluster-centroid-vector>",
      "retriever": {
        "knn": {
          "field": "embedding",
          "query_vector": "<cluster-centroid-vector>",
          "k": 50,
          "num_candidates": 100
        }
      }
    }
  }
}
```

The `type`, `field`, and `query_vector` parameters are required at the diversify level: `field` tells MMR which dense\_vector field to use for inter-result similarity, and `query_vector` provides the reference point for relevance scoring.

This lets you answer: "What does this cluster actually cover?" rather than just "What's at its center?"

```
    Exploring cluster 52 (185 docs)
    Label: fossil | renewable | renewables
    Centroid computed (dim=1024)

    ========================================================================
    Plain kNN (closest to centroid)
    ========================================================================
      1. [0.9738] Green campaigners fear ministers are poised to award billions of pounds in fresh subsidies to Drax power station, despite strong concerns...
      2. [0.9710] Thirteen more oil and gas licences could be cancelled as ministers decide new guidance for fossil fuel extraction after a landmark court...
      3. [0.9699] Experts have accused the fossil fuel industry of seeking special treatment after lobbyists argued greenhouse gas emissions from oilfields...
      4. [0.9681] Burning wood is a terrible way of producing electricity . Chopping down trees destroys habitats for wildlife, and growing new trees cannot...
      5. [0.9649] Keir Starmer will do huge damage to the global fight against climate change if he gives in to political pressure and allows the development...
      6. [0.9641] Labour will next week be confronted with stark policy choices that threaten to expose the fault lines between the Treasury and the...
      7. [0.9638] The Drax power station near Selby in north Yorkshire burns imported wood pellets  The government has agreed a new funding arrangement with...
      8. [0.9581] If you care about the world we are handing on to future generations, the news on Thursday morning was dramatic. This January was the...
    
    ========================================================================
    Diversify retriever (MMR, lambda=0.5)
    ========================================================================
      1. [0.9738] Green campaigners fear ministers are poised to award billions of pounds in fresh subsidies to Drax power station, despite strong concerns...
      2. [0.9434] Oil and gas interests have waged a coordinated campaign to kill pro-electrification policies that ban gas connections in new buildings ,...
      3. [0.9303] It was interesting to read that new licences for oil and gas production in the North Sea are being delayed by legal action ( Thirteen more...
      4. [0.9139] The US energy secretary, Chris Wright, has said he “would love to see Australia get in the game of supplying uranium and maybe going down...
      5. [0.9077] Rachel Reeves was facing criticism on Saturday night as it was confirmed that a report she cited as evidence that a third ­runway at...
      6. [0.8996] When Margaret Thatcher opened the Hadley Centre for Climate Change in 1990 journalists suggested she was attempting to appear to be doing...
      7. [0.8993] The vast majority of governments are likely to miss a looming deadline to file vital plans that will determine whether or not the world has...
      8. [0.8987] European imports of seaborne gas shipments fell by a fifth last year to their lowest level since the pandemic, according to a new report,...
    
    Overlap: 1/8 documents appear in both result sets
    
    Avg pairwise similarity (lower = more diverse):
      Plain kNN:          0.9057
      Diversify retriever: 0.6965
```

The plain kNN results cluster around one angle of the topic: the documents most similar to the centroid and to each other. The diversify retriever surfaces different facets of the same cluster: subtopics, different sources, and varied perspectives.

The diversity metric confirms this quantitatively: the average pairwise similarity is lower for the diversify retriever results, meaning that the returned documents cover more ground.

This is useful for:

* **Understanding what a cluster actually covers**, not just its center but also its edges.
* **Generating summaries**. Diverse representative docs give an LLM better material.
* **Finding representative examples** for human review or downstream labeling.
* **Quality checks**. If the diverse results look incoherent, the cluster may need splitting.

## Part 2: Temporal story chains

### Tracking stories across days

Part 1 clustered the full month globally for topic discovery. For temporal flow, the same density-probed centroid classification runs independently per day on **daily indices**, and then clusters are linked across adjacent days. Note that the daily clusters are independent of the global clusters from Part 1; each day produces its own cluster assignments and labels tuned to that day's content.

#### **The linking approach: sample-and-query**

For each cluster on day A:

1. Sample a few representative documents.
2. Run kNN against day B's index.
3. Count how many hits land in each day B cluster.
4. If the hit fraction exceeds a threshold (kNN fraction ≥ 0.4), record a link.

This is fast (only a few docs per cluster are queried, not all of them) and uses Elasticsearch's native kNN, no external tools needed.

```
Preparing daily indices for temporal linkage...

Indexed 8,495 docs into 28 daily indices

Temporal links found: 808 in 145.4s

Strongest links:
  2025.02.01 'league | arsenal | premier' -> 2025.02.02 'league | season | striker'  (100%)
  2025.02.03 'league | striker | loan' -> 2025.02.04 'league | striker | season'  (100%)
  2025.02.03 'score | operator | gedling' -> 2025.02.04 'league | striker | season'  (100%)
  2025.02.12 'playoff | leg | bayern' -> 2025.02.13 'league | players | injury'  (100%)
  2025.02.14 'league | injury | football' -> 2025.02.15 'league | premier | football'  (100%)
  2025.02.18 'russia | ukraine | talks' -> 2025.02.19 'saudi | russia | arabia'  (100%)
  2025.02.18 'football | league | bayern' -> 2025.02.19 'league | manchester | players'  (100%)
  2025.02.21 'league | premier | manchester' -> 2025.02.22 'game | players | defeat'  (100%)
  2025.02.21 'rugby | calcutta | brilliant' -> 2025.02.22 'game | players | defeat'  (100%)
  2025.02.26 'metals | kyiv | ukrainian' -> 2025.02.27 'ukraine | russia | talks'  (100%)
```

A kNN fraction of 100% means every sampled document from the source cluster landed in the same target cluster, the strongest possible cross-day link. Most links above are football-related, which makes sense: Premier League coverage runs daily with high topical consistency.

The `score | operator | gedling` → `league | striker | season` link is an example of a niche local football cluster (Gedling is a non-league club) being absorbed into the broader Premier League cluster on the next day, a natural effect of daily reclustering at different granularity.

### Building story chains

A story chain is a sequence of linked clusters across consecutive days.

Individual pairwise links tell you that Monday's "UK politics" cluster connects to Tuesday's. Chains reveal the full arc: a story that starts Monday, evolves through the week, and fades by Friday.

Chains are built greedily from links with a kNN fraction ≥ 0.4, meaning that at least 40% of sampled documents from the source cluster landed in a single target cluster. Starting from the earliest cluster, the algorithm always follows the strongest outgoing link.

```
    Strong links (kNN fraction >= 0.4): 244
    Story chains spanning 3+ days: 18
      Chain 1: 'ukrainian | kyiv | eastern' (19 days: Feb 3 → Feb 21)
      Chain 2: 'playing | opposition' (19 days: Feb 10 → Feb 28)
      Chain 3: 'tadhg | maro | cadan' (10 days: Feb 1 → Feb 10)
      Chain 4: 'invade | china | putin' (8 days: Feb 21 → Feb 28)
      Chain 5: 'elected | labour | leader' (7 days: Feb 12 → Feb 18)
      Chain 6: 'film | swift | awards' (6 days: Feb 2 → Feb 7)
      Chain 7: 'amendment | termination | reporting' (6 days: Feb 12 → Feb 17)
      Chain 8: 'officers | scene | police' (5 days: Feb 1 → Feb 5)
```

The longest chain tracks Ukraine–Russia coverage for 19 consecutive days, unsurprising given the sustained geopolitical intensity in February 2025. The second-longest follows Premier League football across 19 days of the month. Shorter chains capture award season (film/awards, six days), Six Nations rugby (10 days), and UK political leadership coverage (seven days). Each chain represents a story arc that the algorithm discovered purely from embedding similarity across daily indices.

### Sankey: Visualizing story flow

A Sankey diagram is a flow visualization where link width represents connection strength. Here, each vertical band is a day, each node is a daily cluster (sized by document count), and each colored path traces one story chain across time. Link width encodes kNN overlap strength: Thicker links mean more sampled documents landed in the target cluster. Colors are consistent per chain, so a single color path from left to right reads as one story's progression.

For example, the Ukraine–Russia chain (visible as one of the longer paths) flows continuously from early February through the third week, with consistently thick links indicating strong topical continuity across days.

![Temporal story chains flowing across February 2025](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta8c243e0c5773440/6a17093fa6c2b98c86e7968c/100a60a7fb85da8ab3813fd071a82c93f2c3f318-1300x650.png)

*Temporal story chains flowing across February 2025. Each colored path is a story persisting across days; link width indicates kNN overlap strength.*

## What this approach delivers

This walkthrough covered a complete unsupervised document clustering pipeline built on Elasticsearch:

1. **Clustering embeddings**: Jina v5's task-specific adapters produce embeddings optimized for topic grouping, not just query-document matching.
2. **Global discovery clustering**: Clustering the full month in one index maximizes cross-day topical discovery.
3. **Density-probed centroid classification**: Sample 5%, probe density via `msearch` kNN, select diverse high-density seeds, classify all docs against centroids. Elasticsearch handles the heavy compute; only seed selection runs client-side (~0.01s).
4. [`significant_text`](https://www.elastic.co/docs/reference/aggregations/search-aggregations-bucket-significanttext-aggregation) **labeling**: Significance testing produces meaningful cluster labels without any ML model or manual annotation. Clusters that produce no significant terms are incoherent and get demoted to noise — a built-in quality gate.
5. **Temporal story linking**: Daily indices and sample-and-query cross-index kNN trace how stories evolve over time.

**Key takeaways:**

* The embedding task type matters: Clustering embeddings produce measurably tighter topical groups.
* Elasticsearch can serve as both the storage layer *and* the clustering engine via [kNN search](https://www.elastic.co/docs/solutions/search/vector/knn).
* Density-probed centroid classification keeps nearly all compute server-side and produces clusters with natural sizes determined by embedding space density.
* `significant_text` is fast, interpretable, and effective for both auto-labeling and quality gating.

**When this approach is useful:**

* You have timestamped text and want topic discovery without labeled training data.
* You want one stack for storage, vector search, labeling, and temporal linkage.

**Extensions to explore:**

* Multi-period clustering (weekly, monthly rollups).
* Real-time ingestion with incremental cluster assignment.
* LLM-generated cluster summaries using the significant\_text terms as seeds.
* At larger scale, sampled KMeans centroids can serve as warm-start seeds for density-based clustering, reducing the probe phase cost.

## Try it yourself

Swap in your own timestamped document corpus; any collection of text with dates works with this pipeline. The full notebook and supporting code are available in the [companion repository](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/unsupervised-document-clustering-elasticsearch-jina-embeddings).

* [**Start a free Elastic Cloud trial**](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs): Spin up a managed cluster with `bbq_disk` support in minutes.
* [**Try Elasticsearch Serverless**](https://www.elastic.co/elasticsearch/serverless): No cluster management, scales automatically, and supports everything in this walkthrough.

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