---
title: 'Lance File 2.1: Smaller and Simpler'
company: LanceDB
tag: 工程相关
date: 2025-03-27
url: https://www.lancedb.com/blog/lance-file-2-1-smaller-and-simpler
account: 
origin: harvest3-202607
---
# Lance File 2.1: Smaller and Simpler

[Weston Pace](/author/weston-pace)

•

March 27, 2025

•

[Engineering](/category/engineering)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca15434b62e37edd3c7c73_lance-file-2-1-smaller-and-simpler.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Almost a year ago I announced we were going to be embarking on a journey to build a new 2.0 version of our file format. Several months later, we released a beta, and last fall it became our default file format. Overall, I’ve been super pleased with how well it worked. As we’ve been working with the community and stressing the format in production, we’ve identified a number of areas for improvement. We’ve been working on a 2.1 format for a few months to address these insights.

As our 2.1 format enters beta I wanted to take some time and look back on the 2.0 format and talk about what worked, what didn’t work, and what we’re going to be doing differently in 2.1.

## 2.0: We Got Rid of Row Groups

The most direct success of the 2.0 format, by far, was getting rid of row groups. We have not missed them…ever…at all. We have not lost any opportunity for parallelism or performance and we have removed the single biggest foot gun from Parquet. I described my reasoning for this already [in an earlier post](/lance-v2/) so I don’t need to go into details here.

## 2.0: We Filled the I/O Queue

The most important performance concept in modern I/O, whether it is NVMe or cloud storage, is queue depth. If you do not have enough concurrent I/O requests in flight, you will leave bandwidth on the floor. In fact, it’s even better to have too many I/O requests even though you face overhead and fairness issues. In 2.0 we built a scheduling algorithm to hit whatever queue depth we wanted, in priority order, without going over our parallelism budget. So we don’t even have to pay those overhead and fairness costs.

![Disk Utilization Comparison](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b358_Disk-Utilization.avif)

If your disk/NIC isn't screaming then we aren

I discussed most of this in depth [in an earlier post](/file-readers-in-depth-parallelism-without-row-groups/). However, I was not prepared for just how effective this was. I had hoped, originally, to match Parquet’s scan speed while introducing random access. I figured this meant we would be slower than Parquet until we figured out compression. However, I was surprised to find that Lance often beats Parquet in full scans. This turned out to be true even when the file was 2-3 times bigger!

## 2.0: Our Flexible Container Format um…Flexed?

The overall structure of the file format has worked great. Our encoding scheme for 2.0 evolved significantly as it was developed. In 2.1 we pretty much reworked everything related to encodings. The protobufs have been many, and they have been varied, and they have enabled extremely rapid prototyping. Through all of this, I have not once encountered any reason to change the overall file structure. Pages, column descriptors, and a file footer are a simple, consistent, and extremely flexible structure.

![Lance File Format Structure](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b347_High-Level-Structure.avif)

Lance file format in four words

**💡 Victory Tour Complete**

Ok, the victory tour is over. I’m sure there’s other cool 2.0 things I could talk about but this is a retrospective and I suspect everyone is really just here to read the juicy takes about what went wrong.

## 2.1: We’re Squeezing out Compression via Structural Encoding

The 2.0 format has very little compression, primarily limited to dictionary compression and a few other tricks. This often surprises people coming from Parquet, but the truth is, compression isn’t as critical for us. Our primary goal is working well with multimodal data such as embeddings, tensors, audio, video images, etc. These types are typically compressed already (often with lossy compression) and they’re so large that any compression of metadata isn’t as significant as you might expect. As a result, compression was a lower priority and, as we started using 2.0 internally, and customers started adopting it in production, we realized we needed to tie things off and ship something stable.

That being said, we’ve found some areas where compression is significant. Compression metadata doesn’t have much impact on overall storage costs, but it can significantly speed up things like prefiltering. Also, semantic text is a very common part of our user’s datasets, and some of these text-heavy datasets (e.g. Common Crawl, Fineweb, Github Code) have massive text columns which need solid compression.

Integrating compression into Lance is trickier than it might seem. Compression is implicitly related to I/O scheduling. For example, if you delta encode your values, or you strip out NULLs during compression, then it can become difficult to extract a single value from the compressed output. Fortunately, while we were working on 2.0, we had two brilliant interns run various experiments into compression, and this really helped us nail down these integration points and refine our encoding traits. What we discovered is that we were mashing together two different concepts. In 2.1 we have split the generic step of “encoding” into **structural encoding** and **compressive encoding**.

I’m going to be writing an entire blog post on this topic but structural encoding tells us how an “array” is split into a series of “buffers”. Compressive encoding then focuses on how those buffers can be compressed. For example, in Arrow, we have a well defined standard for splitting an array into buffers. But…there are too many buffers! (this turns out to be bad for random access). In Parquet, we have a completely different standard for splitting an array into buffers that uses far fewer buffers, but can introduce read amplification. In Lance 2.1 we now have two different strategies that we switch between depending on the size of the value.

![Structural Encoding Comparison](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b35c_Structural-Encoding.avif)

Dividing structure into buffers can be important for random access

In fact, there was one more lesson for us. Once we figured out structural encoding we suddenly discovered a way to create a taxonomy for compression algorithms. For example, **transparent** compression algorithms (like bitpacking) support random access while **opaque** compression algorithms (like delta encoding) do not. You may think we obviously just use transparent compression everywhere but—and here is where the magic comes in—the structural encoding that you choose controls which category of compressive encodings you are allowed. There are times in Lance 2.1 where opaque compression is perfectly valid! I promise I will write a lot more about this later.

## 2.1: We’re Knocking Out the 1-2 IOP Challenge

As I was working on 2.0 encodings I would often refer to something I called the “1-2 IOP challenge” (it’s a punchy name 😉). The dream was to come up with an encoding so that I could access any element in an array in a single IOP (for fixed width data types) or 2 IOPS (for variable width data types). This sounds simple at first. We all know how to grab a string/binary value. First we grab the offsets and then we grab the value.

Unfortunately, it seems that someone has told customers about fancy data types. Also, customers love NULL values. As an example, let’s look at what happens if you have a list of strings (e.g. tags, facets, etc.). This one array has many pieces of information.

What does this mean? Well, if you’ve been keeping up on your Arrow column format homework you know that we now have a struct validity buffer, a list validity buffer, a list offsets buffer, a string offsets buffer, a string validity buffer, and a string values buffer. In Lance 2.0 this, unfortunately, meant that we needed to perform 6 IOPS to fetch a single value. We have failed the 1-2 IOP challenge.

![Bad Tag Access Pattern](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b34e_Bad-Tag-Access.avif)

In 2.0 we spent too many IOPS to read a single value

In Lance 2.1 it turns out the answer is once again related to the idea of structural encodings. Recall that the structural encoding tells us how an array is split into buffers (that’s important because it controls our IOPS). What’s more, the structural encodings all have a concept known as a **repetition index**. The union of these two concepts turns out to be exactly what we need for the 1-2 IOP challenge and I am proud to say that we have solved it. No matter what data type you have, no matter how complex it is, no matter how many layers of validity you’ve stashed away, we can access any value in 1 or 2 IOPS. I’ll definitely be writing more on this concept soon.

![Good Tag Access Pattern](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b354_Good-Tag-Access.avif)

In Lance 2.1 we only need 2 IOPS (and sometimes just 1) for the same data!

## 2.1: We’re Pushing Statistics so Far Down they Fall Out

During the 2.0 development process we had a working prototype of pushdown filtering. I didn’t love it but it worked. It then broke. We fixed it. Then it broke again. As I write this that defunct prototype is still lurking in the code, but I’ve come to figure out why it just didn’t stick.

There’s a lot of reasons for this but I’ll boil them down to “introducing all this compute complexity in the file format, when you have a fully functional and complex query engine just sitting there, is just a lot of work for little gain”. What’s more, keeping statistics decoupled from encoding can be [helpful for performance too](https://vldb.org/cidrdb/papers/2025/p19-prammer.pdf).

It turns out the answer, for us, is that statistics based pushdown is “just another index” (technically a *primary* index) and it is much easier for us to store this information **outside the file** (just like we do with all our other indices). This concept may sound strange but it has existed for a very long time, it just had a different name, the [zone map](https://docs.oracle.com/en/database/oracle/oracle-database/21/dwhsg/using-zone-maps.html#GUID-BEA5ACA1-6718-4948-AB38-1F2C0335FDE4) (just not the one you use for planting your garden).

![External Indices Flow](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b34a_External-Indices.avif)

Once you can read arbitrary ranges from files then many things become possible

By storing these indices outside the file we can pick which columns we want to index after we’ve already written the file. We can also retrain the index with a different block size without rewriting the file. What’s more, we just so happen to have infrastructure for managing external indices lying around.

I can already hear you asking, “what if I don’t have a query engine lying around?”. Well, in that case we will give you one. We take some kind of compute engine like [Datafusion](https://datafusion.apache.org) (or possibly just arrow-rs) and shove it into a plugin. This plugin calculates the index during write and stores it in the file as a free global buffer. Then, during read, the plugin will apply the filter.

## 2.1 We’re Experiencing Deja Vu with I/O Scheduling

One of the things we got right in 2.0 was I/O scheduling. It turns out this is one of the things we also got wrong. We could saturate the bandwidth on full scans but random access on NVMe is tricky. A good NVMe can perform close to a million reads a second (the $200 disk I have at home for playing games daily development can achieve ~800K reads/s). This means an average latency of almost 1 microsecond.

![Synchronous I/O Issues](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a341fdf18ba1e5b351_Sync-I-O.avif)

These gaps can be larger than the time it takes for the I/O to run!

At the risk of stating the obvious, this is not a lot of time. In 2.0 our poor little read request requires two thread transfers. First we put it in a queue to the I/O thread. Then we put the response back into a queue for the decode thread. As a result we were spending 2-3 microseconds of overhead for a request that only takes a single microsecond. Adding a fully synchronous blocking API brought our file reader from 40K values/second to 400K values/second in some low-level benchmarking! As part of the stabilization for 2.1 I’m hoping to look into this further, and make up new terms like “semi-synchronous I/O”.

## 2.1 Timeline

The 2.1 format is now officially in beta. There are a few known limitations but it should work for most types. Follow our work and track its completion [here](https://github.com/lance-format/lance/milestone/4). If you want to run experiments you can enable the 2.1 format in a few ways:

### Dataset Level

```
import lance
import pyarrow as pa

data = pa.table({"x": range(1000)})
ds = lance.write_dataset(data, "/tmp/test_ds", data_storage_version="2.1")
print(ds.data_storage_version)  # Should be 2.1
```

The `data_storage_version` is set when a new dataset is created and will control all data written by that dataset.

### File Level

```
import lance
import pyarrow as pa

data = pa.table({"x": range(1000)})
ds = lance.write_dataset(data, "/tmp/test_ds", data_storage_version="2.1")
print(ds.data_storage_version)  # Should be 2.1
```

If you’d prefer to work directly with Lance files for experimentation or lower-level access we have python bindings for a file reader/writer.

**⚠️ Beta Warning**

By “beta” we mean “files you write with the beta may not be readable in the future”. Please do NOT use unstable / beta versions with production data.

Over the next few months we will be adding new tests, fixing some remaining todos, dogfooding, and tuning the performance. We encourage you all to try it out and do your own experiments. Feel free to start filing bugs about 2.1 and we will take a look. I’ll also be writing additional blog posts going over the new features at a much lower level.

## **Join the Conversation!** 👩‍💻

We’re always happy to chat more on our [Discord](https://discord.gg/G5DcmnZWKB) and on [Github](https://github.com/lance-format/lance). Feel free to ask for more details or help us find better ways to do things! If something doesn’t work or could be faster then let us know too.

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c2da58e972a1401f760bdc_weston-pace.avif)

[Weston Pace](/author/weston-pace)

Data engineer from the open source space, working on LanceDB, Arrow, Substrait.

[GitHub](https://github.com/westonpace)[Linkedin](https://www.linkedin.com/in/weston-pace-cool-dude/)[Twitter](https://x.com/westonpace)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a567183dd1ae093c21b81d5_opt3.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a50fef0022a597f28313428_hero%20img.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/6a510da7aa738b84d6e9c040_preview-image.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb