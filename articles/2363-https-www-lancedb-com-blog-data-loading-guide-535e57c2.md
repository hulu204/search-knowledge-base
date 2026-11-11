---
title: 'https://www.lancedb.com/blog/data-loading-guide'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/data-loading-guide
account: 
origin: en-rss
---
# Data Loading for AI/ML: A Comprehensive Guide

[Weston Pace](/author/weston-pace)

•

August 13, 2026

•

[Engineering](/category/engineering)

![2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2-fig-001](../images/2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2/figure-001.png)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

In machine learning tasks, "data loading" is the process of moving data into some kind of algorithm. Typically we are training some kind of model but there are many different variations.  So many that I find myself always balancing between overly-specific examples and overly-broad generics.

I/O STAGE  CPU STAGE  GPU STAGE                      Storage  Database                                            Host Machine  CPU · RAM                      GPU  Model

The challenge I face in explaining data loading is that it is both extremely simple (iterate a dataset) and full of nuance (this whole guide). Data loading is also the bridge between the data world and the model world and topics are often confusing only because of the choices in terminology. In this article I will attempt to give a comprehensive overview of the data loading process, from the perspective of a data engineer. I'll explain the concepts, describe the challenges, and explain common performance pitfalls. While this article will be focused on `pytorch` and `lancedb` the information should apply to other libraries as well.

To begin with, let's consider a very specific example: supervised fine tuning (SFT) applied to model named Qwen2.5-0.5B-Instruct using the Alpaca dataset. What we are doing is taking a large generic model and fine tuning it to perform a more narrowly tailored task. The model is ~1GB of weights.  Note that the model has already been fine tuned (hence the "-Instruct" suffix) but it is small and readily available and we can always fine tune it further. The Alpaca dataset is a nice open dataset of instruction/response pairs consisting of about 25MB of data and 50K rows.

Qwen 2.5  Generic understanding                        Alpaca  50K instruction pairs    +  fine-tuning              Fine-tuned Model  Instruction answering

## The Simplest Data Loader

If this sounds complex, it isn't. Let's look at things in code:

```
model = load_model("Qwen2.5-0.5B-Instruct")
tbl = open_table("alpaca")

for batch in tbl:
    train(model, batch)
    transformed = transform(batch)
```

That's really all there is to it. We want to take some data, transform it a little, let the model take a look at it, and then we're done. There is quite a bit more nuance, as we are regrettably going to see, but we should not forget the basic premise of what data loading is.

## Setting the Stage(s)

Models are traditionally trained on GPUs. Data is traditionally stored on some kind of object storage or disk. Some amount of "data transform" traditionally happens on the CPU. This gives us three stages in our standard data loader.

### The I/O Stage

The I/O stage is when we are loading our data from storage into (usually) the CPU. The resource at play here is distinct from CPU/GPU capabilities. If we are loading from cloud storage we probably care about the NIC(s) attached to the server.  We might have hundreds of concurrent HTTP requests to maximize throughput. If we are loading from disk we care about what kind of disk is attached and we typically don't need as much concurrency.

Cloud Storage                              CPU        HTTP                  NVMe SSD                              CPU        io\_uring            InfiniBand                  GPU        GPUDirect                                

Different examples of the I/O stage

Normally these resources are rated in GB/s. Capacities can range from a pretty solid baseline of 1GB/s to experimental storage systems that can deliver TB/s. We also have to consider IOPS/s. If we are performing small reads then we may be IOPS limited instead of bandwidth limited. A good baseline might be 1000-5000 IOPS/s for cloud storage all the way to tens of millions of IOPS/s for high-performance NVMe servers.

###### I/O is Rarely the Bottleneck

As a data engineer this fact is somewhat surprising.  We're used to I/O being the limiting factor in just about every data-intensive application out there.  However, LLMs are...well...large.  For every tiny (<1KB) token that we pass through an LLM we need to perform billions of computations.  This is vastly more compute-intensive than traditional OLAP tasks.

### The CPU Stage

The next stage is to prepare the data for the GPU. The details at this stage are highly flexible. The first part is typically decompressing and decoding the bytes we receive from storage. This is familiar to me as a data engineer. Next, however, we might to do things like "normalization", "transformation", and "tokenization". To be honest, it doesn't really matter.  I normally just smile and nod when this part is described to me.

ENCODED IMAGES  CPU DECODE  GPU STAGE                                    Encoded Images  JPEG · binary                                            BOTTLENECK        CPU Decode  Decoding JPEG images                      IDLE      GPU  Idle · waiting                            

A poorly optimized CPU stage (e.g. JPEG decoding with one worker) can easily become a bottleneck.

A good baseline is probably about 1GB/s per core. Extremely simplistic decoding can handle tens or hundreds of GB/s per core. Very expensive decoding (e.g. decoding JPEG images) can drop far below those speeds.  The parallelism here is typically based on the number of cores we have available.  This can vary from instance to instance and cloud to cloud.

We can also try and skip the CPU stage entirely.  We can pre-tokenize our data and store the already transformed data, reducing the amount of CPU work needed in our actual training task. We can also push the work into the GPU, allowing the GPU to decode and transform the data.  However, since the GPU is probably the bottleneck then the last thing we want to do is put *more* work onto it.

### The GPU Stage

Finally we are ready to actually train the model or run inference. Rating GPUs is incredibly difficult because the capabilities of a GPU are so flexible. The most common scoring we see is "tokens per second" and this is going to be a model-dependent score.  So the tokens per second on Qwen will be different than the tokens per second on DeepSeek.  This can make it difficult to spec out the performance of our entire pipeline but we discuss that more in the next section.

I/O STAGE  CPU STAGE  GPU STAGE  I/O  CPU  GPU          

Pipeline throughput is limited by the narrowest stage — adding capacity to wider stages won't help until you've addressed the bottleneck.

In this era of foundation models the models themselves are extremely large. The amount of compute needed per byte is massive. We should expect the GPU to be the bottleneck. Typically, the goal of data loading is to feed data to the GPU fast enough that the GPU is never idle.

### Other Stages

The three stage model described above is the most common scenario, but not the only one.  For example, it is not too uncommon to load data from multiple data sources and stitch them together or we might do some remote processing in the CPU stage introducing additional communication.  Stage boundaries are just places where our resources or parallelism change.  Most of the rest of this article will be focused on a simple three stage solution (although there is one section on shuffling where we split the I/O into two stages for a four stage model) but the tools and techniques apply to other scenarios as well.

## Performance Goals

The ultimate performance goal is for model training to run as fast as possible. For a data loader that typically means we want to load data fast enough to keep the GPU busy at all times. The exact answer will always depend on your circumstances, but as of 2026, a good rule of thumb is **"not that fast"**.

I'd love to quantify that further but even if we know the capabilities of our hardware it can be difficult to convert from compressed bytes (I/O throughput) to in-memory bytes (CPU throughput) to tokens (GPU throughput). Let's look at a concrete example.  In the introduction I provided an example where we fine-tune Qwen with the Alpaca dataset.  Let's run on this test machine:

* CPU: 16 cores (Intel Xeon, 2.00 GHz)
* Disk: Local NVMe (virtual disk)
* GPU: 1x L40S (48GB RAM)

The fastest I can get the training to run is 16K tokens per second.  So how fast do we need the I/O stage and CPU stages to be? In other words, how many bytes per second do we need to satisfy 16K tokens per second?

‍  
I have yet to find a concrete guide for mapping from compressed bytes to tokens.  The answer is typically "it depends on your tokenizer" which is an extremely unsatisfying answer.  In practice there is not *that* much variation. I've found that the bytes/token ratio is primarily based on the modality of your input.  Here are some numbers that are likely off significantly but close enough for napkin math.

* Text: 10 in-memory bytes/token, 5 compressed bytes/token
* Images: 1000 in-memory bytes/token, 100 compressed bytes/token
* Video: Same as images, most video is processed in small segments which are just a group of pictures
* Audio: 10K in-memory bytes/token, 5K compressed bytes/token

Since our Alpaca experiment deals with text, we can multiply our tokens per second by 10 to get bytes per second.  That means, to keep our GPU fed and happy, we need a whopping…160KB/s of data which probably only means about 80KB/s of I/O 🐌 since we have compression.  Now, if we're reading our data in random order, we might also need to care about IOPS per second.  In `lancedb`, we use the Lance file format, and so we need 1-2 IOPS per value.  In our example above the GPU is able to consume at most 200 rows/second and so we need 200-400 IOPS/second.

Both our throughput and IOPS are something we can easily deliver directly from cloud storage.  However, we can make the task more challenging.  Let's consider some different hardware.

| Hardware | Bytes / second | IOPS / second |
| --- | --- | --- |
| L40S | 160 KB/s | 400 IOPS/s |
| L40S × 8 | 1.28 MB/s | 3.2K IOPS/s |
| B200 | 800 KB/s | 2K IOPS/s |
| B200 × 8 | 6.4 MB/s | 16K IOPS/s |

As we scale up the hardware available on a single server we increase the I/O requirements.  For these text based applications our bandwidth is easily achievable even when we're pulling directly from cloud storage.  However, if we want to fetch data in purely random order, we are going to run into trouble on larger instances.  We might need to cache data locally in NVMe storage, use some kind of block-based shuffling algorithm, distribute across more CPUs, use multiple buckets, or avoid the shuffle entirely.  We discuss these options later.

### Is I/O Bandwidth Ever a Challenge?

So far, considering the Alpaca example, it seems like bandwidth should be trivially achievable (while IOPS/s might be more challenging).  To make this more challenging we can either make the tokens more expensive (more bytes per token) or make the model smaller (less GPU work per token).  For example, I'm able to get an L40S to consume 150MB/s of image data if I use an extremely lightweight model (ResNet-18).  This means we might need up to 6GB/s to feed B200x8 which could actually be challenging (but should be possible) when going directly from cloud storage.

I/O BANDWIDTH REQUIREMENT  Larger Model Sizes      GPU Performance    Complex Data Modalities    Efficient Architectures

Forces acting on I/O bandwidth requirements

There are also examples where read amplification can create a throughput challenge.  For example, when training video, it is common to train on segments (e.g. 16 frames) of a larger video.  If your data loading code is loading the entire video, slicing out 16 frames, and then discarding the rest, you will almost certainly run into bandwidth limits.  In Lance, we overcome this particular limitation by allowing for partial reads of blobs.

Looking at our above table we might also expect challenges when working with audio. However, the reason audio's numbers are so high is because we typically convert audio to text first before passing it to an LLM. Audio is a *terrible* encoding for text.  In practice however, this audio-to-text conversion is a great candidate for computing offline, before we start the training process.  Still, there could be some very interesting data loading challenges involving the streaming of live audio.

To summarize this section, I think we will need at least a 10x improvement in GPU throughput on most models before we are going to need to really start worrying about bandwidth.  That's good news for us data engineers.

## Distributed Parallelism

We have a disk, a server, and a GPU, and we need to move the data from one end to the other.  We've just seen that the GPU work required is pretty intense, and our training throughput is likely to be low. In fact, it is so terribly slow that we probably want to distribute the work across many GPUs.

I've been sticking to data engineering terms so far but for this section I want to introduce a few machine learning terms because you'll likely come across them when working with data loading. **World size** is the number of GPUs we are training with. Each GPU gets assigned a unique index which we call the **rank**. These GPUs are spread across one or more **nodes** (servers hosting the GPUs).

Ok, "node" is not really a machine learning term. It's also not standardized.  Node, server, host, box, VM, instance...you get the picture.  Just keep in mind that we have physical servers (which define our hardware), the containers running on them (which define our constraints), processes running on those containers, and threads running in those processes.  In this section I am mainly talking about distributing the work across multiple GPUs. There is a future section discussing process & thread based parallelism.

### Data Parallelism

The simplest type of distributed training is "data" parallelism — we distribute our data across our GPUs so that each GPU trains on a subset of the data. If we train the same dataset on X GPUs then the total training time will be 1/X the original training time.  This is also going to be very familiar territory to a data engineer where we are used to working with partitioned data.

Split 1    Split 2    Split 3    Split 4    Split 5    Split 6    Dataset                                    GPU 0                        GPU 1                        GPU 2                        

Data parallelism — the dataset is divided into splits assigned round-robin across GPUs, so each GPU trains on a different subset simultaneously.

### Model Parallelism

Another way to distribute the work is to distribute the model itself. Each GPU trains only a part of the overall model. There are two styles: **tensor** parallelism (split elements of each layer across GPUs) and **pipeline** parallelism (split layers themselves across GPUs). Model parallelism makes it possible to break up an extremely large model that might not fit on a single GPU, but does not generally give you faster training throughput.  In this style of parallelism all of the GPUs need to see the exact same data.

### 3D Parallelism

We don't need to pick just one. All of these approaches are complementary. We can combine data parallelism, tensor parallelism, and pipeline parallelism. That being said, for the rest of this article, when I talk about distributed compute, I am mainly talking about data parallelism, as that has the biggest impacts on data loading.

STAGE 1  STAGE 2    PIPELINE PARALLELISM      Split A    Split B    Data                              GPU 0    tensor                  GPU 1                  GPU 2    tensor                  GPU 3                          GPU 4    tensor                  GPU 5                  GPU 6    tensor                  GPU 7              DATA PARALLEL  DATA PARALLEL                                

3D parallelism: data parallelism (Split A vs Split B) × tensor parallelism (GPU pairs 0/1, 2/3, 4/5, 6/7) × pipeline parallelism (Stage 1 → Stage 2)

## Data Loader APIs

Now that we have set the stage, we can finally start talking about data loading itself. A model training application is normally going to have many moving parts and data loading is just a piece of a larger whole.  There are many different model training frameworks, but for the purposes of this guide, they should all be fairly similar.  We will focus on `pytorch` , which is the most well known library.  In Pytorch the task of data loading belongs to a DataLoader.

The Pytorch **`DataLoader`** is capable of doing quite a few things such as shuffling, sampling, and transformation (via the `collate_fn, though that isn't` *`really`* `what it is for)`. The dataloader takes a **`Dataset`** as input. You can then iterate the DataLoader to get batches of data:

```
model = load_model("Qwen2.5-0.5B-Instruct")
tbl = open_table("alpaca")
dataset = StreamingDataset(tbl)
dataloader = DataLoader(dataset)

for batch in dataloader:
    transformed = transform(batch)
    process(model, transformed)
```

Hopefully this is simple so far.

### Dataset Types

The pytorch `Dataset` is an abstract class which should be extended by a concrete implementation.  There are actually two different abstract classes, which give us two styles of data loading.

#### Map Style Datasets

`torch.utils.data.Dataset` is for "*map-style*" datasets. You implement two methods (plus an optional third for better performance):

```
def __len__(self) -> int:
    # Return the number of samples in the dataset
def __getitem__(self, index: int):
    # Return the sample at the given index
def __getitems__(self, indices):
    # Return the samples at the given indices (optional, preferred if defined)
```

As you can see, map style datasets are geared towards indexed access. For example, a pandas DataFrame is a natural fit for a map style dataset. If `__getitems__` is defined then it will be preferred, allowing you to batch up the database calls you make.  This helps amortize some of the per-call overhead.

#### Iterable Style Datasets

The base class `torch.utils.data.IterableDataset` requires a single method:

```
def __iter__(self):
    # Return an iterable of samples
```

An iterable dataset is geared towards a streaming block-based API. In `lancedb` we provide `StreamingDataset` which is an iterable-style dataset. By default we return a python dict because it is an easy-to-use universal representation.  We also have a lower level utility, the `Permutation`, which can act as a map style dataset.

###### Batched based iteration does not mean sequential access

Don't mistake an iterable dataset for sequential access to storage.  We may still access the storage itself in a random order.  We just return the results in a batched fashion.

#### Which Style to Choose?

A map-style dataset is the easiest to slap together and it also lets the DataLoader take responsibility for shuffling and sampling. However, Pytorch's default sampler is pretty basic.  It cannot handle sophisticated shuffling approaches or pre-filtering.  These choices can be customized but that puts the burden on the user of the dataset to use it properly.

An iterable-style dataset takes full responsibility for shuffling and sampling.  This means an iterable dataset can choose more advanced options and make a more complete API available to the user.  For example, if you are using `StreamingDataset` then you can set a `filter` and a prefiltering sampler will be configured automatically.

## Batched I/O & Collation

`StreamingDataset` reads batches of data from disk (controlled by `read_batch_size`), but then yields one sample at a time. The `DataLoader` then has a `batch_size` parameter and reassembles samples into a batch. In other words, we slice our batch into samples and then reassemble it. If you're reading closely then this is the part where you assume I'm either joking or confused but it turns out it is not *completely* foolish. Storage tends to use a column-major format (efficient for compression and decoding) while models tend to require row-major data. A transpose is inevitable.  Still, we can be slightly more efficient in the collation if we need to.

COLUMN-MAJOR  ROW-MAJOR  img  txt  lbl  id  img  txt  lbl  id                                                                    img  txt  lbl  id  read\_batch\_size · 1024 rows            collate\_fn                                                                                                                          batch\_size · 256 rows each

A column-major Arrow RecordBatch (read\_batch\_size rows) is split and transposed into row-major mini-batches (batch\_size rows each) by the StreamingDataset and collate\_fn.

### Collation Function

In Pytorch, all of this reassembly happens in the `collate_fn`. The default implementation expects a list of 1D tensors, numpy arrays, python lists, or python dicts. Part of the reason the default behavior for `StreamingDataset` is to return a list of python dicts is so that the default `collate_fn` works just fine.  However, this means that in addition to the inevitable transpose we are also doing an extraneous conversion to a native python representation (arrow->python->torch) which can be less efficient.

If we want to accelerate this we can modify our dataset to provide row-major batches using a transform function and skip collation entirely by setting `batch\_size` to `None` and do the transpose and pytorch conversion entirely in our transform function. Alternatively, we can use a different transform function, for example, we could pick one that returns a list of 1D pytorch tensors.  The default collation will then stack these tensors.  This avoids the python representation but still means we are allocating an extra one-row-at-a-time representation.  Both are more efficient than the default but unless you have a very fast GPU pipeline it probably isn't something you need to worry about.

## Prefetching & Queues

The standard Pytorch DataLoader offers prefetching (also called readahead or buffering). While the GPU is processing the current batch, we can go ahead and load one or more future batches. Then when the GPU is ready for another batch, we already have one prepared.  Unfortunately, this is somewhat limited, because it doesn't allow us to easily pipeline our I/O and our compute.

In `StreamingDataset,` prefetching is provided by default.  A prefetch queue exists between the I/O stage and the compute stage to store raw, loaded rows.  A second queue exists after the CPU stage to store transformed rows.  This means the Pytorch prefetch queue is mostly redundant, but only if you don't have a `collate\_fn`.  If you do have a `collate\_fn` then the Pytorch prefetch queue can buffer the collation work.  However, this is likely to be slightly less efficient than just skipping collation and doing everything in the transform.

I/O    FASTEST      I/O QUEUE                FULL        CPU    MEDIUM      CPU QUEUE                FULL        GPU    SLOWEST

In this example queues fill because each upstream stage produces faster than the downstream stage consumes. A full queue is a good sign.  It means we always have data available for the next stage.  If the CPU queue stays empty then our GPU    will be underutilized

## CPU Parallelism

### Multi-processing

PyTorch uses multi-processing for parallelism when `num_workers` is set greater than zero. The primary advantage is it bypasses Python's global interpreter lock (GIL). The most important configuration for multi-processing is the [start method](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.set_start_method):

* **spawn**: Each worker is started as a subprocess. Simple but has the highest overhead in both RAM and time.
* **fork**: Less overhead than spawn, but forking a multi-threaded process that has already started is generally dangerous.
* **forkserver**: A safe compromise that forks as soon as you call `set\_start\_method` and before any multi-threaded libraries have started (hopefully).

**Recommendation**: Use forkserver and call `set_start_method` in your main method before you have started any work.  As  
long as the library imports (which will have already run) do not start any threads then you are probably ok.  If one or more  
libraries *does* do significant work at import time you may need to delay the import.

### Multi-threading

Multi-threading requires code to have been written in a certain way but gives considerable advantages because threads share memory:

* **Less RAM**: processes each have their own memory space for prefetch buffers, caches, and I/O buffers. With multi-threading these are shared.
* **Less overhead**: when performing I/O against cloud storage we often want more threads than cores. To saturate a 10GBps link we probably want around 100 concurrent requests, even if we only have 16 cores. Achieving this through multiprocessing alone is impractical.
* **Shared cache**: `lancedb` aggressively utilizes in-memory caching. With multiprocessing, each process independently loads the dataset manifest and opens file handles.
* **Avoids over-subscription**: `lancedb` defaults to 64 concurrent requests to object storage. If you create 16 `lancedb` worker processes you end up with 1024 concurrent requests — object storage gets overwhelmed and you start seeing retries.

**Recommendation**: In LanceDB we use multi-threading.  If you are using `StreamingDataset` then set `num_workers` to 0 or 1.  Setting it to 1 allows you to pipeline the collation and GPU pinning. The transform function (described below) will be parallelized across threads.  The `StreamingDataset` does support values above 1 but you are unlikely to see better performance unless your transformation is GIL-bound.

## Transformation

After we load data from storage we typically need to process it: decompress and decode from the storage format into an in-memory format, tokenize, and normalize. All of this transformation can be done on the CPU or the GPU.

**It is VERY easy for this transformation to become the bottleneck in a model training application — often NOT because we have insufficient resources but because the transformation is applied very inefficiently.**

PyTorch has no formal concept of transformation. It is very common for applications to utilize the `collate_fn` for applying transformation.  Or, the batches are transformed in the main python script after they are fetched out of the data loader.  It's important to note that PyTorch will not parallelize calls to `collate_fn` on a single worker.  If you are doing transformation in `collate_fn` then you are forced you into multi-processing which is less efficient.

In `StreamingDataset` we allow you to specify a `transform` function. The transform function is applied using a python thread pool which means a single worker still uses multiple threads. Furthermore, `StreamingDataset` inserts a queue between the I/O stage and the transform, splitting the transform work into a separate pipeline, so that while you are applying the transform we will continue reading data from the database.

Data  I/O THREAD    Thread 0                            Thread 1                            Thread 2                            Thread 3                          OUTPUT QUEUE                                                                                FULL                                                                                                                                                                                                      

The I/O thread dispatches batches one at a time to each transform thread, but threads process in parallel — up to three running simultaneously. Processed batches are delivered to the output queue as each thread finishes.

### Precomputing the Transformation

If your CPU transformation step is expensive then you may want to consider precomputing the transformation.  This can be especially valuable when working with images or video where the tokenized form of the data might be considerably smaller than the raw data itself.  Precomputing a transformation is also helpful when you have multiple epochs or plan on doing multiple training runs as you can compute the transformation once instead of multiple times.

The main difficulty is that it can be complex to establish and maintain your precomputing pipeline. Fortunately, the feature engineering capabilities in the enterprise version of LanceDB make precomputed transformations pretty easy.  You can add your transformation as a virtual column and it will be computed automatically in the background.

## Pinning & GPU Transfer

Once the data has been transformed we need to get the data to the GPU for processing.  This involves two steps, pinning the memory and the host-to-device (H2D) transfer.

### Pinned Buffers

Every process has a virtual address space.  There is a mapping from this virtual space to the actual physical space the RAM occupies.  Various activities can cause the physical location to change while the virtual location remains consistent.  The classic scenario is that the RAM is swapped to disk but even if you disable swap there are still actions (e.g. memory compaction) which can relocate physical RAM.

GPUs cannot tolerate this relocation and so the H2D transfer expects data to be in “page locked” or **pinned** memory.  This almost always means a copy must be done before the data is transferred to the GPU.  This copy is to take the data out of regular RAM and put it into pinned RAM.  It is possible to avoid this copy if you allocate your data in page locked memory in the first place.  However, avoiding this extra copy can be pretty difficult and is not typically needed when training large models, so I’ll only mention it as a potential thing to investigate if you happen to be CPU-bound.

Pageable MemoryPinned MemoryRegular RAMpages can relocateextra copyPinned Bufferpage-lockedH2DGPUPinned RAMalready page-lockedH2D · no copyGPU

With pageable memory (left) the OS can relocate physical pages, so the GPU driver must first copy data into a page-locked buffer before the H2D DMA transfer. With pinned memory (right) the physical address is guaranteed not to move, so the GPU reads directly — no intermediate copy.

If you are doing any kind of multi-processing (i.e. `num_workers > 0`) then you can often benefit from setting `pin_memory=True` on the pytorch DataLoader.  This will do the pinning on the main process, on a dedicated thread.  Pinning **must** be done on the same process that is controlling the GPU.  So if `num_workers > 0` then there is no benefit to pinning on the worker processes themselves.

However, if you are fully single process and multi-threaded (`num_workers == 0`) AND you don’t have any kind of collation step, then you could benefit from explicitly pinning the memory on the worker threads, as part of the transform function.

### H2D Transfer

The next step is the transfer to the GPU.  This is initiated by the `.to(device)` calls.  However, if you set `non_blocking=True` (and you probably should) then this won’t complete as part of the call.  Instead, the task to transfer the data will be added to the stream’s list of tasks.

The concept of GPU streams is out of scope for this guide. However, most GPUs can run compute at the same time they are transferring data.  This is useful, though when training large models this might not be as important as you think.  For example, in the instruct fine-tuning example we probably spend less than 0.1ms transferring data for every 100ms we spend performing arithmetic.  Even if we do pipeline that transfer it will give at most a 0.1% boost to throughput.

However, if you are transferring more data, or your model is lighter weight, this may become more important.  In that case you can use multiple streams.  While one stream is crunching data the other stream can be transferring data.

### Can’t we Optimize This?

There is an entire sub-discipline of data engineering built around maximizing the throughput of data into the GPU.  Specialized hardware, libraries, and techniques can lead to hundreds of GBps of throughput into the GPU.  If you start to hear terms like DMA, RDMA, device-side decode, or Mellanox then you’re probably straying into this territory.

There is absolutely nothing wrong with this, \*\*if you need it\*\*.  However, be cautious of straying into this area as a premature optimization.  These specialized high-throughput solutions are useful for OLAP style business analytics but (at least today) are overkill for training large models.  In fact, they may even hurt, as they might require you to move more work to the GPU, which is already struggling to do model training. If you benchmark your data loading in isolation, without consideration for your real use case, you can pour years of engineering time into something you will never use.

I am not going to cover these techniques in this guide but it can be useful to know they exist.  If your GPU task can process 10 GBps of data or more then it may be time to start seriously considering them.

## Shuffling

Proper model training recommends that samples be provided in random order. Unfortunately, cloud storage was not built for efficient random access. Maximizing throughput typically requires large contiguous reads. In `lancedb` we try and minimize the IOPS required to get each value, but this will only go so far.

Sequential AccessRandom Access1 large contiguous read per batch6 separate seeks per batchrow 0row 23row 0row 23batch 1: rows 0–5, batch 2: rows 6–11, …batch 1: row 1, row 7, row 13, row 2, row 19, row 10

Sequential access reads each batch as one large contiguous block — the storage bar advances in order. Shuffled access must seek to each row individually, one I/O per row.

When working with NVMe storage we typically have extremely high IOPS rates.  However, random access speeds can still be limited due to read amplification.  For example, when using the Parquet format, you typically need to load a full page (normally defaults to 1MiB) of data to load a single value.  If your values are 1KiB, this will give you a 1000x reduction in available bandwidth.  Fortunately, `lancedb` uses the Lance file format which doesn't suffer from read amplification.

No Read Amplification100× Read Amplificationrow 0row 23BYTES READ PER ROW ACCESS10 B transferred · exact matchpage 0page 1page 2page 3BYTES READ PER ROW ACCESS100 KB transferred · 10 B useful1M rows/s × 10 B = 10 MB/s1M rows/s × 100 KB = 100 GB/s

Without read amplification each row access transfers only the data needed. With 100× amplification (e.g. Parquet's large page size), reading a 10-byte label requires transferring 100 KB — demanding 100 GB/s of NVMe bandwidth to sustain 1M rows/s.

###### The performance hit might not matter

`lancedb` run against cloud storage should be able to load thousands of samples per second which is often more than enough for model training with a few GPUs per server.

### Fancy Shuffles

If you do need more speed, there are a number of pseudo-shuffle algorithms:

* **Reservoir sampling**: reads sequentially into a reservoir then drains it in random order.  We do not have a reservoir  
  sampling implementation in `StreamingDataset` as we find the shuffle to be too localized.
* **Block shuffling**: instead of shuffling each row, shuffle blocks of rows. In `StreamingDataset` you can utilize block shuffling by setting `shuffle_clump_size`. Setting this to 10 will shuffle blocks of 10 rows, leading to 10x fewer IOPS.

### Materialize the Shuffle

Another approach is to write the shuffled data to a temporary location first, then scan it sequentially. This doesn't reduce overall wall-clock time but allows you to preload the data while your GPUs are performing other tasks.

## Caching

Caching can allow for both better performance and reduced costs. Streaming data sequentially from cloud storage is highly efficient, fast, and cheap. But this breaks down in two scenarios:

* **Random data**: fully random access leads to excessive IOPS pressure on cloud storage.
* **Remote data**: cross-region or cross-cloud transfers are slow and can become expensive.

### Local Cache

The simplest caching solution is a local cache. Download from cloud storage and cache the data on a fast disk attached to the GPU server.  This provides higher IOPS and generally doesn't require extra infrastructure (assuming you already have a fast disk attached which is common).  However, the data is typically lost when the host is decommissioned (very common when spinning GPU spot instances up and down for training). In `StreamingDataset` you can set the `cache_dir` parameter for local caching.

### Remote Cache

A more sophisticated solution is a dedicated caching service co-located with your compute.  The enterprise version of LanceDB has a cache that can fetch multiple rows per request.  This allows you to achieve similar IOPS as the local disk.  Furthermore, data is not lost and the cache can be shared by multiple GPU servers.

Local CacheRemote Dedicated CacheCloud StorageGPU SERVERCachelocal SSD / RAMfastGPUCloud StorageCache Serverbatch APIfastGPU Servertraining machine

Local cache (left): data lands on the GPU server itself. Remote cache (right): data lands on a remote server with a fast cache API.

### Streamlining Cache

Caching only accelerates repeated accesses to the same data.  The initial download must still come from cloud storage.  If you are running multiple epochs or multiple training runs then caching can be utilized easily.  However, if you are only running a single epoch, or your data is larger than your cache, then you may need to get clever.

#### Prewarming

One solution is to prewarm the cache.  This is just downloading the data in advance of your training run.  This approach is most useful when using a remote cache and all the data you need fits in the cache.  You can spin up a cheap instance to download the data first.  Then you can spin up your expensive GPU instances to run the full training run against the prewarmed cache.

#### Two-stage I/O w/ Localized Shuffle

We can combine caching and shuffling to overcome IOPS limitations in cloud storage.  We are essentially adding a fourth stage, a second I/O pipeline.  First, we fetch from cloud storage sequentially with large contiguous requests, and we store the data into a local NVMe cache.  Second, we read from NVMe in random order, using the Lance format to avoid read amplification.  This  
introduces some startup delay (we must wait until we have the first few sequential chunks before returning any rows) but you don't need to download the entire dataset just to get started.

It also requires a specialized shuffle.  First, you shuffle large contiguous blocks into splits.  These are what gets downloaded during the first stage.  Then you apply a row-level shuffle using a localized shuffle that limits how far a row can move.  This will have some slight impact on the randomness of our shuffle.  However, it avoids the need to fully download all of our data before we start and effectively pipelines the download.

## Splits

If we have multiple GPUs and we are doing data parallelism then we need to divide our data across the GPUs.  If you’re working with a map-style dataset you can have Pytorch’s data loader do this for you by using the `DistributedSampler` (assuming you’re not also using a custom sampler to apply pre-filtering, in which case you’ll need to figure this out yourself). If you’re using an iterable-style dataset then the dataset will need to manage this.  The `StreamingDataset` will take care of this for you.  However, it’s important to know that there are a variety of ways this row splitting can be achieved.

Round-robindisjoint accessRandomrandom, disjointHashstable assignmentSequentialcontiguous blocks

How 16 rows are assigned across 4 splits under each split strategy. Round-robin and random scatter chunks across all splits, forcing disjoint reads from storage. Hash produces a similar scatter but the assignment is deterministic — unchanged by unrelated inserts or deletes. Sequential gives each split one contiguous block, enabling large sequential reads.

### Round-robin

The simplest way to divide the rows across multiple splits is to just assign them in round-robin fashion.  From a storage perspective, this is about the worst possible choice.  This is the `DistributedSampler` default if you specify `shuffle=False`.  The access pattern will be very disjoint.  If you have many splits you’ll end up with random access.  If you just have a few splits the requests will probably all get coalesced together and you’ll end up with each worker downloading the entire dataset.  If you insert any rows in the middle of your dataset, or delete any rows, you will completely change the assignment.  On the plus side you will get a very broad distribution of data across each of the workers.

### Random

Another simple way to divide the rows is to randomly assign rows to splits.  There are a few ways to do this but a simple one is to shuffle the indices and slice the shuffled indices.  The storage access pattern will be similar to round-robin (i.e. poor) and you will get a broad distribution.  If you insert any rows or delete any rows you will completely change the assignment.

### Hash

A slightly more complex way to perform the assignment is to mask off a hash of one or more columns.  Assuming your hash has good statistical properties you will end up with something very similar to random.  However, if you insert or delete any rows then the assignments will not change.  This can help to reduce the variability in your training runs.

### Sequential

If you have a lightweight model, are not interested in shuffling, and want to maximize I/O speeds, then a sequential split is best.  Here we take the first batch of 1/N rows and assign it to the first split.  Then we take the next batch and assign it to the second split.  This way each split ends up with a contiguous block of rows.  Inserting rows in the middle or deleting rows will not modify this split assignment much.  However, your splits will not have a broad distribution of the dataset.  So this should probably only be used if you are sure there is not order-based patterns in your data.

### Epochs

When training with a small amount of data we need to train multiple epochs.  This means we need to run our training dataset through our model multiple times.  In many cases the number of epochs is not fixed.  Instead, we evaluate our model after each epoch, and only continue if our model still appears to be converging (however, we also give up if we hit some limit). It's common to change the iteration order (shuffle our data) between each epoch.  If we are using a cache then we should take care to only shuffle the rows, and not the split assignments.  This way, our data does not migrate to a different server and disrupt our cache.

## Resumability

Training a model can take hours or even days. GPUs can suffer hardware failure, code can crash, instances can be knocked offline. Creating a fault-tolerant training loop is not optional.

From the data loading perspective this is a fairly easy task: just save the state of data loading and resume from it later. The `StreamingDataset` has the method `state_dict` which saves off the important state (seed, number of splits, epoch, and samples consumed so far). The `load_state_dict` method can be used to resume from a saved state.

You will need to incorporate these checkpoint and restore methods into your larger training loop.  Typically a checkpoint will also require saving off the current state of the model in addition to saving off the state of the data loader.  Full instructions on how to do this are beyond this guide.

## Elastic Determinism

There is one final wrinkle involved with resumability, and that is elastic determinism.  Imagine we are training with 8 GPUs and so we create 8 splits.  Later, one of the GPUs suffers a hardware failure.  Fortunately, we recently saved off a copy of the state dictionary.  Unfortunately, we now have 8 splits and 7 GPUs.  If we give the extra split to one of the GPUs we now have twice as much work on that GPU.  If we redivide the data into 7 splits then our saved state is meaningless and cannot be resumed.  What we want is something called \*elastic determinism\* which means we can train on a different number of GPUs but still provide data in the same order.

When I first encountered this problem I thought it seemed impossible.  I thought the ask was that each GPU receive the same samples in the same order.  However, if we have the same dataset but have fewer GPUs then naturally each GPU is going to see more samples than before.  Or if we have more GPUs, then each GPU is going to see fewer samples than before.  So it seems impossible we’d generate the same model.  However, when we are training with multiple GPUs, we are actually keeping the GPUs in lock step.  Each GPU calculates on a small number of rows, and then the results from each GPU are shared and the model is updated across all GPUs.  Each step processes a single "global batch" across all GPUs.

Now our goal becomes more clear.  We don't need each GPU to have the same batches as before.  Instead, we want each global batch to contain the same samples as before.  If we have more GPUs then our per-device batch size is smaller.  If we have fewer GPUs then our per-device batch size is larger.  However, in both cases, we can structure it so that each batch contains the same number of rows.

To do this, we pick a large number of splits, larger than the number of GPUs we have available.  That's because our splits have to be evenly divisible across our GPUs.  For example, if we pick 48 splits we can train with 1, 2, 3, 4, 6, 8, 12, 16, 24, or 48 GPUs and we will get the same global batches.  We can also, as alluded above, begin training with 8 GPUs, and then if one fails, restart training with 6 GPUs.  Or we can begin training with 8 GPUs, and then if some other training job completes and frees up another 8 GPUs we can stop our job and restart it with 16 GPUs to speed it up.

2 GPUs6 splits each1234567891011123 GPUs4 splits each1234567891011124 GPUs3 splits each123456789101112

The same 12 splits (numbered identically in every row) are reassigned as GPU count changes. With 2 GPUs each handles 6 splits; scale to 4 GPUs and each handles 3. Because the splits themselves never change, every global batch contains the same rows regardless of how many GPUs are running.

## Observability

It can be difficult to identify where the bottleneck is during data loading.  This is especially true when the bottleneck is in the I/O or CPU stages.  PyTorch does not offer the APIs we need for profiling or identifying these bottlenecks but the `StreamingDataset` does and so this section is specific to the `StreamingDataset`.

### Queue Depth

Monitoring queue sizes is the simplest way to identify your bottleneck. You can use the `raw_queue_depth` and `prefetch_queue_depth` methods to inspect the current queue size. In the Alpaca demo from the introduction we get the following results:

```
20:26:03 epoch 1/100 step 100 | loss 1.6436 | 11,101 tok/s | 134.4 rows/s | 0/0/48704/3264 | gpu% 97%
```

The `0/0/48704/3264` tells us: 0 unscanned rows, 0 raw rows, 48,704 rows in the prefetch queue, 3,264 rows processed by the GPU. This is a clear GPU bottleneck and exactly what we hope to see.

* **GPU bottleneck**: `0/0/FULL/N` — prefetch queue is full, GPU can't keep up.
* **CPU bottleneck**: `0/FULL/0/N` — raw queue is full, transform is too slow. Verify your transform is releasing the GIL or batch your transformation.
* **I/O bottleneck**: `FULL/0/0/N` — both queues are empty, reads are too slow. Check read batch size and oversubscription.

I/O Bottleneckraw queue · emptyprefetch queue · emptyCPU Bottleneckraw queue · FULLprefetch queue · emptyGPU Bottleneckraw queue · FULLprefetch queue · FULL

Queue fill states for each bottleneck type. GPU bottleneck (both queues full) is the desired steady state — the pipeline is working efficiently. I/O and CPU bottlenecks starve downstream stages.

### Operation Timing

Although queue depth is typically the most intuitive metric to use we can also look at the time spent at each stage.  The `fetch_time` method will tell us how much time we spend performing I/O.  This is cumulative across all workers (and if there are multiple splits in a worker then across all splits).  It’s only a rough image of the actual time spent loading data from cloud storage however as the underlying read calls will do a certain amount of readahead and will have their own parallelism.  In other words, 1s of fetch waiting time might be backed by 100 independent requests which each took 100ms.

The `transform_time` is a little easier to reason about.  It is the cumulative time spent applying transform functions.  Assuming your transform functions are non-blocking then this will be an accurate measure of CPU time.  You should be able to divide by the number of CPUs and compare with the wall-clock time to get a sense for how much of the CPU is spent on transforms and how close you are to transforms becoming a bottleneck.

## Troubleshooting

In this last section, which may grow with time, I hope to point out some common pitfalls and explain their remedies.  These are largely built from my own experiences, my coworkers’ experiences, and the experiences of users and customers that I’ve had the pleasure to work with.  If you have something you’d like to add to this list then feel free to reach out with your suggestions!

This section is split into two parts, I/O bottlenecks and CPU bottlenecks.  You can read the above section on observability to learn how to identify which stage is your bottleneck.  Note that there is no section on GPU bottlenecks!  A GPU bottleneck is entirely possible and I’ve run into a few (e.g. GPU batch size too small, need to use pytorch compile, etc.) but I am not nearly enough of an expert to provide advice on such things.

### I/O Bottlenecks

If you’re bottlenecked on I/O then either your storage pipe is not large enough or your dataset implementation is not efficient enough to utilize the storage.  First, you’ll want to measure how much data you are transferring, and how many IOPS you are issuing.  Compare this with the specs for your storage to determine if you are close to capacity or not.  If you are, you’ll need to find a way to reduce the amount of data or IOPS.  If you’re not close to capacity then you’ll need to figure out why your dataset isn’t downloading efficiently.

### Reading Extraneous Data

One common problem is that you are reading more data than you need.

#### Reading too many rows

If you’re applying post-filtering (filtering after you load the data) then you can easily be reading too many rows.  For example, maybe you have a filter that only matches 1% of your data.  In this case you probably don’t want to be filtering in memory, and should find a way to only read the rows you need.

If you’re using `StreamingDataset` with `filter` then you are already using pre-filtering.  First, we will read only the filter columns, and we will calculate the matching row ids.  Next, we read all the columns you need, but only for the matching rows.  If the filter is expensive, or requires reading a large amount of data to calculate, then you should look into creating an index to speed up the filtering phase.

Another potential culprit is **read amplification**.  This is common with classic file formats like Parquet or ORC.  These are typically configured with fairly large page sizes by default (100KB to 1MB).  This page size is the minimum amount you must read to fetch a single value.  If you’re reading in random order, especially from a fast disk (which can provide plenty of IOPS), then this read amplification might be your problem.  Note that `StreamingDataset` is built for `lancedb` which utilizes the Lance file format, which does not suffer from read amplification, and so this is probably not your problem.

Post-filterROWS LOADED300 rows loaded · 30 rows match filterPre-filterROWS LOADED30 rows loaded · all match filter

Post-filtering reads every row then discards non-matches; I/O scales with dataset size regardless of selectivity. Pre-filtering reads only the matching rows.

#### Reading too many columns

Most datasets will return all columns by default.  In model training it is pretty common to create a large number of columns as you are learning about your data.  You probably don’t need all of these columns for your training algorithm.  You should always specify which columns you need when you setup your dataset.  For example, in `StreamingDataset`, you can provide the `columns` argument to provide a list of columns.

However, it is important to note that column selection is typically most useful when working with columnar storage (such as LanceDB).  If your data is stored in a row-based storage system (e.g. Postgres or CSV) then column selection isn’t as valuable.  In these systems it’s often easier (or simply required) to grab an entire row’s worth of data, regardless of how many columns you want to access.

All Columns8 COLUMNS LOADED8 columns transferred per rowColumn Selection2 COLUMNS LOADED2 columns transferred per row

With columnar storage, unneeded columns (dashed outlines) are never read from disk. Specifying only required columns via the `columns` parameter cuts I/O proportionally.

#### Reading too much per-value

This last category of reading too much is pretty unique to multi-modal data, especially when working with video.  For example, we may have a video dataset where each sample is a single frame (or sequence of frames) in a video.  In these cases a common mistake is to accidentally read the entire video just to obtain the frames we need.  Modern video formats (e.g. mp4) should make it possible to seek to and read the target frames (with some minor amount of read amplification) in just a few IOPS.

Load Entire FileDATA TRANSFERRED100 MB video loaded · 200 KB frame usedSeek to FrameDATA TRANSFERRED200 KB transferred · exact frame seek

Reading an entire video to extract one frame is the per-value equivalent of read amplification. Seekable formats like MP4 let you jump directly to the target timestamp.

### Incorrect Read Batch Size

If you’ve confirmed you aren’t reading too much data then one of the most common culprits is an improper read batch size.  Data loaders are normally going to either pull one GPU batch worth of data or, even worse, they will pull data one row at a time.  This leads to excessive overhead.  A dataset’s ideal batch size will often be much larger than the GPU batch size.  For example, when working with small data types, `lancedb` will often prefer a batch size in the thousands.

How exactly you configure your read batch size (and whether it can even be configured independently of your GPU batch size) will depend on your dataset implementation.  In `StreamingDataset` you can provide a `read_batch_size`.  The default is quite small (64) to avoid OOMs when dealing with very large data types.  Setting this larger can often provide a good boost to I/O time.

Batch Size = 1COST PER ROWrequest overhead dominates per-row costBatch Size = 64COST PER ROWoverhead amortized · mostly data transfer

Each I/O request carries fixed overhead (API call, auth, header parsing). Batch size 1 pays full overhead per row; a larger batch amortizes that cost across many rows.

### I/O Oversubscription

If we are doing multi-processing then we can often encounter I/O oversubscription.  Most datasets are configured to utilize the disk (or NIC) as much as possible.  For example, when using a `StreamingDataset` you will see 64 concurrent requests to object storage.  If you have 16 processes (`num_workers=16`) then this could lead to 1024 concurrent requests to object storage.

If this happens then you will start to see a large number of retries (which themselves can increase pressure on object storage) and your throughput will grind to a halt.  Fortunately, `StreamingDataset` is built on `lancedb` which has an AIMD retry mechanism that works similar to TCP throughput windows and should allow the system to self-heal.  However, it can still often be beneficial to learn how to configure the I/O parallelism of your dataset (in `lancedb` there are environment variables that can control this)`,`especially if you are not using lancedb.

Safe2workers×64req/worker=128concurrentwithin object storage limitsOversubscribed16workers×64req/worker=1,024concurrentthrottled · retries cascade

Each worker independently issues concurrent requests, so total object storage concurrency multiplies. Reduce per-worker I/O parallelism proportionally as worker count increases.

## CPU Bottlenecks

CPU bottlenecks are a bit harder to systematically solve.  Still, there are a number of common culprits, listed below.  If none of these culprits apply then CPU bottlenecks should also be straightforward to profile.  Ask an LLM to find an appropriate profiling tool and take a look at where the CPU time is being spent.

### No Transform Parallelism

One of the most common bottlenecks I’ve seen is a complete lack of transform parallelism.  For example, PyTorch users that have set `num_workers=1` while putting all of their transform code into the `collate_fn`.  If you have a CPU bottleneck you should hopefully see your CPU running close to 100%.  A CPU bottleneck combined with an underutilized CPU will often point to serialization in your code somewhere and the simplest culprit is simply not enabling parallelism at all.

### GIL Contention

If you do have parallelism enabled, and you are still seeing an underutilized CPU, then another common point of serialization could be the GIL.  Ideally you can confirm that the libraries you are using in your transform function release the GIL when they do any heavy compute.  If there are no GIL-releasing alternatives (for example, your entire transform is written in plain python), then multi-processing may be a necessary evil.

GIL-locked4 THREADS · SERIALIZEDthreads take turns · ~4× wall timeGIL-releasing4 THREADS · PARALLELall threads run simultaneously · 1× wall time

GIL-locked threads queue up for execution one at a time (dashed wall-time marker at left). Libraries that release the GIL during heavy compute — numpy, PyTorch, Pillow — let all threads run truly in parallel.

### Multiprocessing Overhead

While multi-processing can allow for parallelism in the presence of GIL-locked transforms it does add its own overhead.  This is time spent spinning up the additional processes (especially when using spawn instead of forkserver) or the extra pickle / IPC overhead required to send data back and forth between processes.  While this is less severe than a lack of parallelism you should make sure that `num_workers` is not too high and that pytorch is configured to keep workers alive.

Spawn per BatchCOST PER BATCHspawn overhead dominates each batchPersistent WorkersCOST PER BATCHstartup amortized · mostly useful work

Spawning a new process per batch pays full fork+import cost on every call. Persistent workers (PyTorch default with `persistent_workers=True`) pay that cost once and reuse the process pool.

### Transform Isn’t Batched

Transform functions will often receive batches of data as input.  It is very common for users to then turn around and write a row-by-row python loop.  While this is often fine as a starting point, it can lead to higher CPU overhead, and potentially become a bottleneck.  For example, if you need to decode images, a common starting approach is to iterate each row, call a decode function, do some transformation on the row, and stitch together the results.  However, libraries like `torchvision` will often allow for batching the decode and transform, often leading to significant speedups.

Row-by-row LoopCOST PER BATCHPython loop overhead per rowBatched TransformCOST PER BATCHvectorized ops · minimal overhead

A Python loop over rows adds interpreter overhead for every element. Passing the whole batch to a library like torchvision or numpy processes all rows in one vectorized call.

### CPU Oversubscription

CPU oversubscription is similar to (though perhaps not as bad) I/O oversubscription.  If you have multiple processes running, and each process is trying to use all available cores, then you’ll have more compute threads than you have cores.  A slight amount of CPU oversubscription can sometimes be beneficial (e.g. to allow you to make progress on a different thread when a page fault is hit) but too much oversubscription leads to an excess of context switches which can quickly start to add up.

If you’re doing any kind of multiprocessing, and you’re using a library that does thread-based parallelism of your transforms (e.g. `StreamingDataset`) then you should make sure to configure the parallelism appropriately.

Balanced4workers×4threads=16compute threadsmatches 16-core machineOversubscribed8workers×4threads=32compute threads2× threads vs cores · context switch overhead

Each worker spawns its own thread pool, so total compute threads multiply. Halve per-worker thread count when doubling worker count to stay within available cores.

### I/O Blocked Transforms

We generally think of the transform stage as all CPU work.  However, in some cases, we have additional I/O that we perform during the transform stage.  For example, we may be using a remote HTTP service to calculate embeddings or otherwise transform our data.  In these cases the remote service is going to have its own idealized parallelism, which may be larger or smaller than the number of CPUs we have available.  Furthermore, we might have other work we need to do before or after the HTTP call, and we want to pipeline this work.

While this problem can be roughly solved with some amount of CPU thread oversubscription it is potentially beneficial to setup a formal pipeline (with queue).  This would allow the remote service to be treated as a fourth stage, with its own independent level of parallelism and prefetch.

Blocking HTTPSINGLE TIMELINECPUwaitCPUwaitCPUwaitCPU idles during every HTTP callPipelinedCPUHTTPHTTP requests overlap CPU workCPU stays busy · shorter wall time

When HTTP calls block the CPU, the transform stage stalls on every request. A separate queue lets the HTTP stage run at its own concurrency while the CPU processes the previous batch.

## Conclusion

Data loading is the task of feeding the GPU with data quickly enough that the GPU never needs to pause. Given the slow speed of large model training this is a goal we should generally always be able to hit. However, data loading is often misunderstood and poorly configured.  Things like large per-row overheads, inefficient parallelism, and poor hardware utilization can lead to data loader bottlenecks. A basic understanding of data engineering principles should typically lead to an efficient data loader.

‍

![2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2-fig-002](../images/2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2/figure-002.avif)

[Weston Pace](/author/weston-pace)

Data engineer from the open source space, working on LanceDB, Arrow, Substrait.

[GitHub](https://github.com/westonpace)[Linkedin](https://www.linkedin.com/in/weston-pace-cool-dude/)[Twitter](https://x.com/westonpace)

![2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2-fig-003](../images/2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2/figure-003.jpg)

### Announcing Reverie Summit: What AI’s Next Breakthroughs Are Made On

LanceDB

•

August 3, 2026

announcing-reverie-summit-2026

![2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2-fig-004](../images/2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2/figure-004.png)

### ⚡ Multi-Bit RaBitQ Without Refine, 🌋 Bytedance’s Lance-Based AI Stack, 🤖 Lance for Embodied AI Data

ChanChan Mao

•

July 31, 2026

newsletter-july-2026

![2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2-fig-005](../images/2363-https-www-lancedb-com-blog-data-loading-guide-535e57c2/figure-005.png)

### Feature Engineering for Multimodal Data: From Laptop to Cluster with LanceDB

Justin Miller

•

August 5, 2026

feature-engineering-examples