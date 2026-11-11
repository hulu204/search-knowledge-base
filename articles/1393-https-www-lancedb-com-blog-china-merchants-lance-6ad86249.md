---
title: 'https://www.lancedb.com/blog/china-merchants-lancedb-story'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/china-merchants-lancedb-story
account: 
origin: en-rss
---
# Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

[China Merchants Lion Rock AI Lab](/author/china-merchants-lion-rock-ai-lab)

•

July 13, 2026

•

[Case Study](/category/case-study)[Physical AI](/category/physical-ai)

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-001](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

For humans, folding clothes is an everyday action that requires no thought. But in deformable-object manipulation for embodied AI, it is one of the hardest tasks. Clothing is a typical amorphous, deformable object: grasp it anywhere, and the overall structure changes with it. The task tests deformable perception, dual-arm coordination, contact control, long-horizon execution, and state recovery. Its difficulty increases continuously with the initial state and the type of garment.

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a509640059d0c9f016a70ac_demo_fold_shirt%20(1).gif)

A real-robot demonstration of a clothes-folding task. Two robotic arms fold a short-sleeved shirt from a flattened state. Every demonstration like this needs to be recorded completely and in alignment.

To train a policy that can fold arbitrarily wrinkled clothes, one of the bottlenecks is data, especially complete real-robot trajectories that cover long-horizon deformable manipulation, dual-arm coordination, and recovery from failures. We connect data collection, training, deployment, and trajectory sampling into a closed-loop data iteration pipeline. Every real-robot execution links together signals from training, deployment, state recording, and human intervention. To make these heterogeneous signals settle into data assets that can feed training again, the prerequisite is a data infrastructure that can carry them in a unified way and support repeated revisions.

## **PART 01 | The Challenge: When Standard Robotics Formats Meet New Workloads**

In embodied AI, data is often collected by episode. An episode can be understood as a complete trajectory: the robot starts from an initial state, executes a continuous interaction, and continues until the task ends. A common access pattern for embodied AI training is to randomly sample a certain timestep from an episode and simultaneously read multi-camera frames, robot states, action commands, language annotations, and human-intervention labels. LeRobot has become an important and widely adopted format in robotics, with strong momentum from the Hugging Face ecosystem. Like many general-purpose dataset formats, it works well for many robotics workflows, but this project pushed into a more specialized workload: “multimodal + high-frequency random access + frequent modification.”

### **LeRobot Native Format: Tradeoffs of Snapshot-Style Organization**

LeRobot uses an “exported snapshot” style of organization: states and actions are stored as Parquet, videos are stored as MP4, and alignment relies on episode\_index and timestamp in the metadata. Across different versions, this design has produced the following structural issues:

1. **Data updates and movement become expensive at this scale.**LeRobot relies on the columnar format Parquet. Parquet reads in row groups by column, so retrieving a single frame requires decoding an entire row group. It has no native blob semantics, so large binary blocks must either be stored externally or stuffed into cells, causing read amplification. Row-by-row deletion and column evolution are not design goals either. For this workload, using Parquet as the primary training storage format creates read-amplification and update-cost challenges. Traditional workflows often package data from different modalities during collection, for example as HDF5, upload it, download the whole package again for processing, and upload it again. A single dataset can easily reach hundreds of GB. It is repeatedly moved between edge devices, local machines, and the cloud, leaving copies everywhere and creating data version-management problems.
2. **Aligning heterogeneous signals requires additional orchestration.**In one episode, there may be 100 Hz robot-arm state data, multiple 30 fps video streams, low-frequency language instructions, and per-frame source labels. Their frequencies and types differ by several orders of magnitude. The raw data is usually distributed across multiple sources: video is stored as MP4, robot-arm states are stored as Parquet, and annotations are scattered in external JSON metadata files. During training, every sample retrieval requires opening the video, seeking, decoding, and then aligning non-visual signals by timestamp. States, video, and metadata remain physically separated. LeRobot v2 uses implicit alignment through episode\_index + timestamp, requiring glue code to reconstruct the data before training. LeRobot v3 adds sharded Parquet index tables, bringing “table joins” inside the table, but in essence the index still points to separate files rather than inline storage, so management cost remains high.
3. **Frame-level access and private-object-storage streaming introduce extra complexity.**Retrieving any given frame requires opening the video file, seeking to a keyframe, and decoding forward. Direct frame-level random access requires extra indexing and decoding logic, and frame-level annotation can become harder to manage. Although LeRobot v3 supports streaming from Hugging Face Hub, the frame-level decoding cost remains unchanged. In addition, LeRobot lacks native streaming support; datasets usually need to be downloaded in full to local storage. LeRobot v3 introduces StreamingLeRobotDataset for streaming training from Hugging Face Hub, but it does not yet cover general S3 or object storage. Private deployments or offline scenarios still require landing the data locally for batch processing.

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-003](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-003.png)

The diagram compares two workflows that both store data in S3.

This is not a criticism of LeRobot. It is a reflection of a different storage requirement. The requirements are keeping long-horizon multimodal robotics data mutable, randomly accessible, and directly usable from object storage.

## **PART 02 | The Solution: Core Problems and How Lance Addresses Them**

This section explains how we use Lance to reorganize this type of data: long videos are cut into GOP-scale blobs, where GOP means Group of Pictures. Video, actions, states, and annotations are aligned in the same table. More importantly, the data keeps a single source of truth in object storage, S3. Collection, processing, and training all directly read and write the same copy, avoiding the back-and-forth movement of “package → upload → download for processing → upload again.” On top of this, Lance supports versioned modifications and random frame reads.

### **Problem 1: Data Modification Must Be Low-Cost, While Preserving a Single Source of Truth**

Collection is streaming, and cleaning is iterative. Removing abnormal episodes and modifying annotation columns must be low-cost. At the same time, datasets often exceed hundreds of GB, and edge devices and personal workstations usually do not have enough storage. Lance solves both problems: no modification rewrites the original data, and the data exists as only one copy in object storage, S3. Every client directly reads the same copy.

For the same “change one thing” operation, the costs of the two formats differ dramatically. Parquet files are immutable. Deleting one row, changing one value, or adding one column all require pulling down the entire file, reading it into memory, modifying it, and writing the whole thing back. The larger the data, the more expensive this becomes. Sometimes modifying a single annotation requires rewriting tens of GB of data.

Lance does not rewrite existing data. An append only adds a fragment, a delete writes a deletion vector, and adding a column writes a new column file. Even if an existing value is modified, only the affected fragment is rewritten, not the whole dataset. Because there is only one cloud copy, if an episode annotation is found to be wrong, it only needs to be fixed once; all downstream consumers will get the updated result the next time they read. Every change automatically leaves behind an immutable version, so version=N can precisely reconstruct the dataset state at that time.

```
# Incremental append / delete / add column -- none rewrites the original data
lance.write_dataset(new_episode, uri, mode="append")
ds.delete("episode_index = 7")  # tombstone; no rewrite
new_cols = pa.table({"mid_objects": detected_objects})  # output from an offline detection job
ds.add_columns(new_cols)  # add a column without touching the original video

# Data exists as only one copy in S3:
# the same line of code can read directly from a local path or s3://,
# with no need to materialize the whole dataset locally.
ds = lance.dataset("s3://<bucket>/training_data/..._30HZ.lance")
ds.to_table(
    columns=["action", "observation_state"],
    filter="episode_index = 0"
)

# Every write automatically creates an immutable version:
# return to any state and trace which dataset version trained which model.
lance.dataset(uri, version=42)
```

### **Problem 2: Heterogeneous Alignment: Multiple Rhythms Land in the Same Row**

First, a concept: GOP, or Group of Pictures, is the basic unit of video encoding formats such as H.264. A GOP begins with a keyframe, or I-frame, that can be decoded independently. It is followed by several predicted frames, P-frames or B-frames, which only record differences from neighboring frames. Because many frames store only “differences,” video can be compressed to a small size. But the cost is that decoding any frame inside a GOP requires starting from the keyframe and decoding forward frame by frame. This is the root cause of why randomly retrieving one frame from a long video is expensive, and it is exactly the core problem this design solves.

There is a seemingly contradictory point here: video is compressed and stored by GOP, meaning a group of consecutive frames, and one blob contains several frames. How can we still achieve “one row, one frame”? The key is in our data schema design. The row does not store the frame itself. Instead, it stores a reference to a GOP blob, plus two indexes: gop\_index, which identifies which GOP the frame belongs to, and frame\_index\_in\_gop, which identifies which frame it is inside that GOP. The target design is for multiple rows in the same GOP to share the same underlying compressed bytes through ref\_id. The bytes are stored only once, with zero redundancy. When reading a specific row, the system only decodes the GOP it points to and then extracts the frame at frame\_index\_in\_gop.

Therefore, storage is at GOP granularity, which keeps compression efficient, while access is at frame granularity, where one row precisely corresponds to one frame. In other words, it is “stored with video compression, accessed with frame organization,” and this mapping layer connects the two.

With this Lance schema design, table rows are no longer aligned by default to camera-frame timestamps. Instead, the finest granularity is the highest-frequency robot control or state sampling time. Actions and states are preserved one by one at their native high frequency. Camera images are mapped by timestamp to the nearest video frame, and the row stores the GOP blob reference and in-GOP frame index. Metadata such as fps, task, train/test split, and joint names are written into the schema metadata, making the dataset self-describing and self-contained. Downstream users can obtain all information immediately after opening the dataset.

Besides making the dataset self-contained and reducing random read/write cost, this storage layout provides an additional benefit: the robot’s action and state sampling rate is far higher than the camera rate, for example joints at about 100 Hz and cameras at about 30 fps. Traditional methods are forced to choose one of two options: either align all signals to camera frames, which reduces actions to the camera rate and loses high-frequency information, or create a separate row for every high-frequency sample, which stores the same video segment repeatedly and greatly increases storage cost. Our “GOP blob + row-level reference” approach breaks this tradeoff. Rows are built at the high action frequency, so no action sample is lost. Video is compressed once by GOP, and the intended Lance layout lets multiple rows share the same blob through ref\_id. The result is: all high-frequency actions are preserved, with zero video duplication.

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-004](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-004.png)

One Lance schema row contains identification/time, action/state for two 14-dimensional arms, multi-camera video blobs, and language/annotation data in the same table row. Metadata such as fps, task, split, and joint names is embedded in the table itself.

Below is a PyArrow schema closer to the implementation. The video columns are Lance blob columns. In the schema they are written as pa.binary(), but this is only their logical representation. It does not mean that every row inlines a copy of image bytes. At the physical layer, Lance manages them through blob references, offsets, and manifests. Multiple rows in the same GOP share the same underlying compressed bytes through ref\_id. Actions, states, language, and source labels are aligned with the row as ordinary columns.

```
import pyarrow as pa

schema = pa.schema([
    # episode / sample identity
    pa.field("episode_index", pa.int64()),
    pa.field("frame_index", pa.int64()),  # training-sample index, NOT a raw camera frame number
    pa.field("timestamp_ns", pa.int64()),
    pa.field("task", pa.string()),
    pa.field("split", pa.string()),

    # robot state / action, e.g. dual-arm 14 DoF
    pa.field("observation_state", pa.list_(pa.float32(), 14)),
    pa.field("action", pa.list_(pa.float32(), 14)),

    # multi-camera video as Lance blob columns
    # logical blob reference; physical bytes are shared by ref_id
    pa.field("observation_images_cam_env", pa.binary()),
    pa.field("observation_images_cam_env_ref_id", pa.uint64()),
    pa.field("observation_images_cam_env_gop_index", pa.int32()),
    pa.field("observation_images_cam_env_frame_index_in_gop", pa.int16()),

    pa.field("observation_images_cam_left", pa.binary()),
    pa.field("observation_images_cam_left_ref_id", pa.uint64()),
    pa.field("observation_images_cam_left_gop_index", pa.int32()),
    pa.field("observation_images_cam_left_frame_index_in_gop", pa.int16()),

    pa.field("observation_images_cam_right", pa.binary()),
    pa.field("observation_images_cam_right_ref_id", pa.uint64()),
    pa.field("observation_images_cam_right_gop_index", pa.int32()),
    pa.field("observation_images_cam_right_frame_index_in_gop", pa.int16()),

    # language / labels
    pa.field("language_instruction", pa.string()),
    pa.field("source", pa.string()),  # human / policy / intervention
    pa.field("is_intervention", pa.bool_()),
], metadata={
    b"camera_fps": b"30",      # camera frame rate
    b"control_hz": b"100",     # robot control / state sampling rate; rows are built at this rate
    b"gop_size": b"8",
    b"joint_names": b"left_0,...,right_6",
})
```

### **Problem 3: Read/Write Performance: Video-Level Size, Image-Level Random Reads**

Whole MP4 videos have a high compression ratio, but retrieving any single frame requires decoding from a keyframe. Frame-by-frame JPEG gives fast random reads, but storage cost grows by multiples. Our video storage design is a tradeoff between the two: video is encoded by H.264 GOP, preserving video-level compression, while an index is built for every frame, so retrieving any frame only decodes the GOP it belongs to. GOP size is an adjustable parameter. In our tests, the best range was around GOP 8. The Python code for randomly reading N frames from the dataset is:

```
# High-performance batched random reads:
# fetch and decode a batch of frames in parallel in one call, with Rust-side decoding.
frames = ds.take_blobs_decoded(
    "observation_images_cam_env",  # str or List[str]: one or more blob column names
    indices=batch_indices,         # List[int], required: rows to retrieve, using 0-based offsets
    concurrency=32,                # maximum concurrent I/O
    zero_copy=False,               # True: return numpy arrays that reuse Rust memory,
                                   # saving one PyO3 cross-language copy
)
```

Here, take\_blobs\_decoded() is a batched read interface we customized in the Lance Rust source code. Given a blob column and a batch of row indexes, it completes the following in one call: range-read the GOP blobs needed by those rows, decode them in parallel on the Rust side into RGB frames, and return the decoded tensors directly. Compared with opening, seeking, and decoding row by row in Python, it batches and parallelizes I/O and decoding, and pushes the work down into Rust. This is the fast path for the training DataLoader, and it is the main reason why the batched scenarios in PART 03 are several times faster than LeRobot.

Two parameters are especially important. concurrency needs to be selected according to the actual environment as the appropriate parallel decoding parameter. zero\_copy further removes cross-language copying, but the returned arrays reuse Rust memory and must be used and discarded immediately. If downstream components keep holding the arrays, memory leaks may occur.

### **Controlled GOP Design That Makes Single-Frame Random Access Feasible**

“Video-level compression + image-level random read” is not simple. Video achieves a small size through inter-frame prediction, and inter-frame prediction means that retrieving any one frame requires replaying the frames it depends on. Compression and random access are naturally in conflict. Our solution is not to change the codec, but to constrain H.264 into a controlled profile and pair it with an explicit index, turning “retrieve one frame” into “one Range GET + decode one short GOP.”

For any target frame, we guarantee four invariants:

* A single frame reads only one object and sends only one continuous Range GET.
* Decode amplification is less than or equal to MAX\_GOP, where MAX\_GOP is adjustable. In experiments we mainly compared configurations such as 4, 8, and 16.
* Every GOP starts from an IDR frame and is a closed GOP, so it can be decoded independently and does not depend on decoder state from the previous GOP. Decoding starts with an empty DPB.
* Frame localization uses an explicit index, avoiding linear scanning of the video file.

These four invariants are supported by three layers: the encoding layer, the indexing layer, and the storage layer.

#### **Encoding Layer: Determines How Many Frames Must Be Replayed to Decode One Frame**

* **GOP slicing and independent decodability.** Each GOP is encoded as an independent H.264 segment, using Annex B, access-unit alignment, and self-contained SPS/PPS headers. It can be decoded without context. The amount of decoding needed to retrieve any frame is bounded to one GOP; there is no need to replay from a keyframe in a whole long video.
* **Fixed short GOP.** keyint = min-keyint = GOP length, scene cut is disabled, and the encoder restarts for every episode. GOP boundaries are deterministic and predictable, and the upper bound of decode amplification equals the GOP length.
* **No B-frames, with zerolatency.** bframes=0 plus zerolatency makes display order equal to decoding order, so single-frame localization does not need to handle frame reordering.

#### **Indexing Layer: Determines How to Locate a Frame Without Scanning the File**

* **Explicit frame index.** Each row uses the two columns gop\_index + frame\_index\_in\_gop to locate the frame, directly determining which GOP and which frame inside that GOP.
* **Row-level deduplication with ref\_id.** Multiple rows in the same GOP share one blob. High-frequency rows do not store duplicate video bytes, and one decoded GOP can serve multiple frames inside that segment.

#### **Storage Layer: Determines How Many I/O Operations One Frame Retrieval Becomes**

* **Blob inline storage + Lance physical layout.** GOPs are inlined into the table as blob columns. The physical layout and range reads are handled by Lance’s fragments and manifests. Single-frame access becomes reading one object with one continuous Range GET, which is friendly to S3.

## **PART 03 | Experiments: Measured Numbers for the Random-Read and Storage Tradeoff**

The following data comes from preliminary tests of video\_lance on the xvla-soft-fold dataset. The goal is to verify the engineering benefits of this layout in random-frame-access scenarios for embodied AI. We do not claim that GOP 8 or the specific speedup ratios apply to all datasets and hardware environments.

### **Experiment 1: GOP Size Tradeoff Between Volume and Throughput**

The larger the GOP, the more storage is saved, but the slower random reading becomes. Under the current dataset and access pattern, the area around GOP 8 shows a good tradeoff: storage is reduced by about 42%, while single-frame throughput remains around 450 frames/s.

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-005](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-005.png)

Looking closely at this sweep, we can see two opposing curves. The marginal gain from compression decays quickly. Storage savings rise from about 36% at GOP 4 to about 42% at GOP 8, and even at GOP 128 they are only about 49%. In other words, increasing GOP from 8 to 128, which is 16 times longer, saves only about 7 additional percentage points. Random-read throughput, however, declines all the way: single-frame throughput drops from 683 frames/s at GOP 4 to 453 at GOP 8, 258 at GOP 16, and only 37 frames/s at GOP 128, about one-twelfth of GOP 8. Batched throughput similarly drops from 2650 to 280. At the other end, GOP 1 degenerates into something close to per-frame encoding, and storage does not decrease but instead increases, about 4% larger than the frame-by-frame JPEG baseline. This shows that pure intra-frame encoding is not meaningful in this scenario. Combining the two curves, GOP ≈ 8 is the sweet spot: it achieves about 42% storage savings while retaining about 453 frames/s single-frame random-read throughput and about 2134 frames/s batched random-read throughput. Further increasing GOP does not save enough storage to compensate for the random-read loss.

### **Experiment 2: Random-Read Throughput Comparison, Lance vs. LeRobot**

Random reads improve by 1.7-6.0× relative to LeRobot, across single-frame, batch, and 8-frame × 3-camera scenarios.

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-006](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-006.png)

The three scenarios correspond to three typical access patterns for training data retrieval. Scenario A is the fairest single-point comparison: both sides use dataset[i] to read samples one by one. LeRobot takes about 81 ms per sample, almost all of which is spent on video decoding. Lance takes about 48 ms, with about 8 ms for range reading and about 40 ms for decoding. Decoding itself is about 2× faster, and end-to-end speedup is 1.7×.

Scenario B lets Lance use batched parallel take\_blobs\_decoded, which batches I/O and decoding and pushes them down into Rust for parallel execution. Single-frame throughput reaches 6.0× relative to LeRobot.

Scenario C is a common access pattern in vision-language training: retrieving a temporal window of consecutive N frames at once. Lance reads the whole window in one range request, and multiple frames in the same GOP share decoding. Compared with LeRobot’s frame-by-frame seek-and-decode approach, it is 4.8× faster.

The pattern is clear: the closer the access pattern gets to a complex DataLoader, with batching, multiple cameras, and temporal windows, the greater Lance’s relative advantage. Even the most conservative single-point comparison shows a 1.7× improvement.

The two experiments answer two separate questions. Experiment 1 shows that “video-level volume + image-level random reads” is an effective tradeoff controlled by GOP size, with the optimal range around GOP 8 on this dataset. Experiment 2 shows that when this layout is applied to a real training data-loading path, it delivers 1.7-6.0× throughput improvement relative to LeRobot. It should be emphasized that the absolute numbers depend on the dataset and hardware. But the trend of “storage can be reduced, random reads can keep up, and larger batches get faster” comes from the data-structure design itself.

## **Company Introduction**

China Merchants Lion Rock AI Lab was established in September 2024 by China Merchants Group, a century-old central state-owned enterprise. Guided by the mission and vision of “giving intelligence to machines and warmth to humanity,” the lab focuses on frontier directions where embodied AI and large models converge. Its key areas include embodied foundation models, Embodied Reasoning, post-training algorithms and frameworks for large models, and other core research.

The lab follows “Robot x Agent” as its main technical direction. It is building a full-stack technical system covering multimodal data, model training, post-training optimization, embodied reasoning, robot policy learning, whole-body motion control, and advanced localization and navigation. Its goal is to break through key technical bottlenecks that allow intelligent agents to move from digital space into the physical world, and to help robots gain stronger capabilities in perception, understanding, reasoning, decision-making, and generalized execution.

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-007](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-007.svg)

[China Merchants Lion Rock AI Lab](/author/china-merchants-lion-rock-ai-lab)

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-008](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-008.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-009](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-009.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249-fig-010](../images/1393-https-www-lancedb-com-blog-china-merchants-lance-6ad86249/figure-010.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb