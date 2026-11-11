---
title: 'https://www.lancedb.com/blog/one-table-to-train-your-robot-lancedb-as-the-data-layer-for-lerobot'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/one-table-to-train-your-robot-lancedb-as-the-data-layer-for-lerobot
account: 
origin: en-rss
---
# One table to train your robot: LanceDB as the data layer for lerobot

[Ayush Chaurasia](/author/ayush-chaurasia)

•

July 20, 2026

•

[Applications](/category/applications)

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-001](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Robotics datasets are conceptually simple: camera streams paired with a compact table of states, actions, timestamps, and task descriptions. Their storage stacks usually are not. Most split those modalities across Parquet files, MP4s, manifests, and application-specific bookkeeping.

LanceDB brings them into one queryable data layer that can train, stream, search, validate, and curate the same dataset. This post looks at robotics data broadly rather than targeting a particular framework. We use [LeRobot](https://github.com/huggingface/lerobot), the field’s emerging open standard, as the worked example because it provides a clean, reproducible path from dataloader benchmarks through closed-loop evaluation.

## The state of robotics data

Robot-learning data is video plus structured metadata: one or more camera streams, proprioceptive state, actions, timestamps, and task descriptions. Nearly every robotics stack stores it in roughly the same way:

* Columnar files for structured values
* Chunked MP4 files for camera streams
* Manifests and metadata to keep the two aligned

The [LeRobot v3 format](https://huggingface.co/docs/lerobot/lerobot-dataset-v3) is the canonical open implementation of this layout.

Video is the right container for camera streams. The coordination layer around it is where things become painful. A shuffled VLA training batch with a 50-step action chunk may need to seek across many MP4 files and repeatedly decode GOPs just to retrieve the requested frames. The same layout also cannot directly answer questions such as *“show me every frame where the gripper is above the stove.”* That requires a separate indexing or feature-extraction pipeline.

[lerobot-lancedb](https://lancedb.github.io/lerobot-lancedb/) replaces the loose collection of files and manifests with two coordinated Lance tables: a frame-level table for structured columns and a blob table containing the **same MP4 bytes**. And because it's one table rather than a pile of files and manifests, the layout is an **enforced schema,** not a convention. Every episode a robot uploads either fits this contract or gets rejected at write time. There is no silent mismatch where the Parquet metadata claims an episode contains 214 frames while its MP4 contains only 212:

```
frames table — one row per frame            videos table — one row per episode × camera
─────────────────────────────────────       ─────────────────────────────────────────
episode_index      int64                    episode_index   int64
frame_index        int64                    camera          string
timestamp          float32                  video           large_binary
task               string                     └─ metadata: lance-encoding:blob=true
observation.state  fixed_size_list<float32>[8]
action             fixed_size_list<float32>[7]
emb_image          fixed_size_list<float32>[768]   ← added later, zero-copy
```

The dataset stays video-sized (1.9 GB for LIBERO's 273k frames), decoded pixels are bit-exact vs the source videos, and the format gives you what the glue can't: fast frame-level random access, S3 byte-range streaming, and secondary indexes on the same table. Everything below is measured on a 4×H100 box, and the code to reproduce it is in the [lancedb/training example](https://github.com/lancedb/training) repo.

## LanceDB dataloader for robotics

LanceDB's LeRobot plugin is  optimized for faster dataloading. It uses LanceDB's blob encoding to lazily seek requested frames from episodes without loading the entire file in memory.

The test: [ACT](https://huggingface.co/docs/lerobot/en/policies#act) (~50M params) on [DROID-100](https://huggingface.co/datasets/lerobot/droid_100) (3 cameras per frame). Identical 4×H100 training runs, same seed, same mp4 bytes. The only variables are the data layer and the CPU budget, pinned identically for both backends.

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-002](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-002.png)

The full 20k-step wall clock at the 4 vCPU budget: **50m04s for Lance vs 1h55m37s for the baseline (2.31×)** Loss curves match to the third decimal at every logged step. Same bytes, same model, same result. One of them just waits on its dataloader.

The gap depends on how dataloader-bound the run is. Give the run plenty of CPU and the loader hides.  **The faster your GPUs get, the bigger this gap gets.** The LanceDB dataloader for LeRobot can get up to **3-5x** speedup or more when using enterprise. With efficient data loaders,  your GPU spends less time waiting for data:

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-003](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-003.png)

Below, we show a few examples that evaluate models we trained.

#### **"Transfer the cube to the other arm", before vs after:**

“transfer the cube to the other arm” (episode 0)

BEFORE: untrained ACT, 0%

AFTER: trained on Lance in 53 min, success

“transfer the cube to the other arm” (episode 1)

BEFORE: untrained ACT, 0%

AFTER: trained on Lance in 53 min, success

## Using LanceDB with Lerobot

You can use LanceDB dataloader by swapping out the base loader with a single line change

```
from lerobot_lancedb import LeRobotLanceVideoDataset

dataset = LeRobotLanceVideoDataset(
    "lerobot/droid_100", root="./droid100_lance",
    delta_timestamps=delta_timestamps,   # resolved from your policy config as usual
    return_uint8=True,
)
# everything downstream is unchanged: EpisodeAwareSampler, DataLoader, your train loop
```

Converting an existing dataset is a single command:

```
lerobot-convert-to-lance-video --repo-id=your/dataset --src-root=... --output=./ds_lance
```

## Training a VLA: SmolVLA on LIBERO

Next, let's look at the popular VLA class of models. We finetuned SmolVLA (450M, language-conditioned) on the LIBERO benchmark with both backends. Identical 40k-step recipes, task strings flowing through the language collate, evaluated closed-loop over all four suites, 100 episodes per suite per model.  at 450M the GPU is the bottleneck and both formats keep it fed.

‍

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-004](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-004.png)

Here's every suite, same model before and after fine-tuning, side-by-side:

libero\_spatial: 80% after finetuning

BEFORE: smolvla\_base, 0%

AFTER: trained on Lance, success

libero\_object: 89% after finetuning

BEFORE: smolvla\_base, 0%

AFTER: trained on Lance, success

libero\_goal: 77% after finetuning

BEFORE: smolvla\_base, 0%

AFTER: trained on Lance, success

libero\_10: 82% after finetuning

BEFORE: smolvla\_base, 0%

AFTER: trained on Lance, success

> 💡 **One evaluation "gotcha" we hit so you don't have to** LeRobot's `--policy.n_action_steps` controls how much of SmolVLA's 50-step action chunk executes open-loop before re-planning, and it dominates measured success. The same checkpoint that scores 82% closed-loop scores 14.8% when it executes 10 steps per chunk (72% at 1 step, 1% at 25). If your LIBERO numbers look inexplicably bad, check this flag before blaming your model.

## Training directly from remote object store

Base LeRobot has no remote object storage streaming  path. You sync the dataset down, then train. The Lance reader takes an `s3://` URI directly and does byte-range reads against the blob column. No local copy ever gets created. With LanceDB, you get fast streaming from object storage so you can keep your GPUs fed, without having to copy expensive data every time you train. This is useful when your dataset grows from a few gigabytes to petabytes in size. LanceDB also supports streaming GCS, Azure and Hugging Face Buckets.

| read pattern (8 workers) | parquet+mp4, local NVMe | Lance, streamed from S3 | Lance, local NVMe |
| --- | --- | --- | --- |
| DROID (3 cams) | 722 | **897** | 1,709 |
| ALOHA sim | 817 | **1,013** | 2,296 |
| LIBERO (2 cams, SmolVLA pattern) | 1,271 | **1,445** | 3,111 |

The table shows samples per second in a same-region bucket, with the time-to-first-batch is 10 to 15 seconds. At 16 workers the S3 numbers grow to 1,690 to 2,458 samples/s. That's enough to fully feed every training configuration above with the dataset never touching the machine.

There are several other advantages of using LanceDB as your data layer for robotics:

* No dataset volume at all: the GPU node needs disk for checkpoints, not data
* No sync step
* Node boots, training starts, first batch in seconds. one copy shared by N nodes
* Cheaper storage: object storage runs roughly 3 to 4× cheaper per GB than the SSD volumes you'd otherwise sync to, and robotics corpora only grow
* Fine-tuning on curated set: because it can random-access over S3, a **curated slice** can train against a corpus that never fits on the node at all. You read the 50 GB you selected out of the 10 TB you own

## Add features and evolve your data for free

LanceDB supports zero-copy [data evolution](https://lance.org/guide/data_evolution/), i.e, when add a new column (feature), it only writes the new data to the existing table and doesn't copy the original data. At terabyte scale (or beyond), this process saves a lot of time, storage and I/O. Feature engineering is a critical piece for training good models. LanceDB's feature engineering package, [Geneva](https://docs.lancedb.com/geneva) allow you to run feature engineering jobs at scale on LanceDB tables, without creating expensive copies, messing with k8s/Spark cluster configs or being gated on infra support.

As a researcher, you only worry about defining the right features, without being bogged down by the infrastructure needed to compute them at scale. LanceDB Enterprise takes care of distributing the jobs across workers, smart checkpointing, and more.

### Backfill features with Geneva

We added a SigLIP2 embedding column with the feature engineering capabilities in LanceDB Enterprise, using stateful UDFs (where the model is loaded once per worker), batched (batches arrive as Arrow arrays), and GPU-scheduled.

```
from geneva import udf

@udf(data_type=pa.list_(pa.float32(), 768), num_gpus=1, input_columns=["index"])
class EmbedAgentview:                      # stateful: SigLIP2 loads once per worker
    def __call__(self, index: pa.Array) -> pa.Array:   # batched
        # decodes pixels straight from the Lance video blob table
        ...

tbl.add_columns({"emb_image": EmbedAgentview(lance_root)})
tbl.backfill("emb_image", concurrency=2)   # 273,465 frames ≈ 10 min on 2 GPUs
```

Two things are worth noticing here. The UDF reads pixels from the *video blob column*, so the Frames table never stores image bytes. And the write does zero-copy schema evolution: a commit that adds a new embedding column, with **no rewrite** of the video blob column.

## Curation: Index it, search it

#### **"The microwave door is open" top hits across 273k frames**

‍

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-005](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-005.png)

That's a text query against the frame embeddings, answered by the same table the DataLoader reads. With Parquet+MP4 you'd need an embedding store, an index service, and a manifest pipeline to do this. Three systems that can drift out of sync with your training data.

### Four more things the same table answers

**Near-duplicate episodes.** Embed once, and redundancy pruning becomes a simple search problem. Comparing mid-episode frames across all 1,693 episodes at over 0.995 cosine similarity. Drop one before training.

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-006](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-006.png)

‍

**Outlier mining.** Within a task, the frames farthest from the task's visual centroid are your teleop glitches and camera-occlusion moments. Episode 217 shows up twice in the top-5 anomalies for the microwave tasks: the arm swallowing the lens. Exactly the frames to eyeball before they pollute a fine-tuning run.

‍

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-007](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-007.png)

**Hybrid queries.** Full-text and vector search compose. *"the gripper is holding the object in the air"* restricted to `task LIKE '%basket%'`. "*Find me mid-grasp frames in basket tasks*" becomes one call.

**Time travel.** Every schema evolution and backfill committed a table version (this table has 26 versions). You can open the exact table version a run trained on and reproduce it later.

## Training on the curated dataset

Curation only matters if it feeds back into training. Here a SQL filter on the task column becomes an episode list, and the episode list becomes a fine-tuning dataset.

```
eps = tbl.search().where(f"task IN ({object_tasks})") \
         .select(["episode_index"]).to_pandas()["episode_index"].unique()
# → 454 episodes, 66,984 frames; feed straight into --dataset.episodes
```

Now we run training directly from the source dataset filtering only the desired episodes. It went from 0% to \*\*77% on its suite in 10k steps\*\*, about 35 minutes of training. The 40-task generalist still wins the suite at 89%. At this scale, multi-task transfer beats a narrow fine-tune.

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-008](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-008.png)

## Efficiently store large video blobs with Blob v2

The video table stores each mp4's raw bytes in a `large_binary` column whose field metadata`(lance-encoding:blob=true`) turns on Lance's blob encoding. Values live in blob-oriented data files, the column materializes as lightweight (position, size) descriptors, and returns lazy file-like handles that support byte-range reads, locally or over S3. `torchcodec` decodes straight from those in-memory buffers. That's why conversion is instant, pixels are bit-exact, the dataset stays video-sized, and a shuffled DataLoader still gets frame-level random access.

## The real world is 1000× bigger

Everything above was for a 1.9 GB benchmark. That's small enough to measure cleanly, but just large enough that almost any storage decision can show its significance. A robotics program does not remain 1.9 GB in size. A fleet of robots recording a few cameras can easily produce this amount of data *every few minutes*. The corpora we've worked with in the wild, like VPT-scale video datasets and multi-terabyte teleop archives, sit **3-4 orders of magnitude** above this example. That's where the two-system layout really breaks down:

* ‍**Ingestion becomes continuous, not a one-time conversion:** Thousands of robots and sim workers appending episodes at the same time need atomic, conflict-free writes into one namespace, not a directory of Parquet shards and a manifest that two writers race to update. Lance commits are atomic and versioned, and the schema contract from the intro is enforced on every write, so a fleet can't silently upload malformed episodes.
* ‍**Syncing the dataset to the node** stops being a small startup delay step and becomes an expensive op. A fast streaming dataloader is the way out: one copy in object storage, and every trainer streams byte ranges of exactly the slice it needs.
* **Curation stops being optional.** At 273k frames you can eyeball your data. At **200M+** frames, the only way to find duplicates, teleop glitches, or the 50 GB actually worth training on is the machinery above (embeddings, indexes, SQL over the same table), running as distributed jobs instead of a notebook.
* **A 10-minute, 2-GPU backfill becomes a thousand-GPU-hour job.** It will be preempted, it will hit bad rows, and it has to resume. That's exactly why backfills in LanceDB (via Geneva) are checkpointed and distributed via stateful UDFs that handle the heavy-lifting, rather than manually running them with for-loops.
* **Lineage becomes a compliance question**. When a policy misbehaves on a real robot, "which table version, which episode list, which checkpoint" has to be answerable months later. Table versions and versioned splits scale with the table. Manifest files and tribal knowledge don't.

This is the workload [LanceDB Enterprise](https://docs.lancedb.com/enterprise/) runs for production AI teams: the same open Lance format underneath, plus the operational layer this scale demands. High-throughput distributed ingestion into object storage. Automatic compaction and index maintenance as the corpus grows. Feature backfills are scheduled across GPU fleets. Petabyte-scale scan throughput to keep multi-node trainings fed. And SLA-backed serving of the same tables for search and curation.

The worked example above is the whole system in miniature. Enterprise is what it looks like when the fleet, not the benchmark, sets the scale. Check out the [training examples](https://github.com/lancedb/training) repo for all the code, and learn more about lerobot-lancedb [here](https://lancedb.github.io/lerobot-lancedb/). Lots more to come soon!

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-009](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-009.avif)

[Ayush Chaurasia](/author/ayush-chaurasia)

ML Engineer @ LanceDB

[GitHub](https://github.com/ayushchaurasia)[Linkedin](https://www.linkedin.com/in/ayushchaurasia/)[Twitter](https://x.com/ayushchaurasia)

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-010](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-010.png)

### Why CrewAI Rebuilt Agent Memory on LanceDB, Powering 2B+ Agent Executions

CrewAI

•

July 23, 2026

crewai-rebuilt-agent-memory-on-lancedb

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-011](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-011.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9-fig-012](../images/2357-https-www-lancedb-com-blog-one-table-to-train-yo-dfdf02c9/figure-012.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story