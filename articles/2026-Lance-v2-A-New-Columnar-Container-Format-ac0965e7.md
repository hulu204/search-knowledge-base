---
title: 'Lance v2: A New Columnar Container Format'
company: LanceDB
tag: 工程相关
date: 2024-04-13
url: https://www.lancedb.com/blog/lance-v2
account: 
origin: harvest3-202607
---
# Lance v2: A New Columnar Container Format

[Weston Pace](/author/weston-pace)

•

April 13, 2024

•

[Engineering](/category/engineering)

![](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69ca1212e6cf302339d9fb19_lance-v2.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

## Why a New Format?

Lance was invented because readers and writers for existing column formats did not handle AI/ML workloads efficiently. Lance v1 solved some of these problems but still struggles in a number of cases. At the same time, others ([btrblocks](https://github.com/maxi-k/btrblocks), [procella](https://research.google/pubs/procella-unifying-serving-and-analytical-data-at-youtube/), [vortex](https://github.com/fulcrum-so/vortex)) have found similar issues with Parquet in their own use cases. I’d like to talk about a new format, Lance v2, that will solve these issues, but first let me describe the various use cases we have learned about by working with modern workloads.

### Point Lookups

A point lookup is a query that accesses a small set of rows. This is essential whenever you are using a secondary index. For example, both semantic search and full text search end up as point lookups in LanceDB. Parquet’s main challenge with point lookups is that its encodings are not designed to be “sliceable” and you typically need to load an entire page of data to access a single row. This is especially bad for multi-modal workloads because our values are typically quite large and coalescing is much harder.

![Parquet Point Lookups Challenge](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaae4_parquet-point-lookup.avif)

Parquet faces challenges satisfying point lookups

## Wide Columns

Wide columns are columns where each value is very large. Traditional db workloads use fairly small columns (floats, doubles, etc.) Strings are often the largest column but even they are usually quite small in practice. In ML workloads we often want to store tensors like semantic search embeddings (e.g. 4KiB CLIP embeddings) or even images (much larger).

![Wide Columns Challenge](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaad5_wide-columns-grouping.avif)

Picking a good row group size is impossible when a file has a wide column

### Very Wide Schemas

Many user workloads involve very wide schemas. These can range from finance workloads (which sometimes have a column per ticker) to feature stores (where there can be thousands of features for a given record). Parquet and other columnar formats help by giving us powerful column projection but we still need to load the schema metadata for all columns in the file. This is a significant cost for low-latency workloads and potentially memory intensive when caching metadata across many files.

![Wide Schemas Performance](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaacf_wide-schemas.avif)

Many Parquet readers do not perform well on very wide schemas, even with highly selective column projection

### Flexible Encodings

Parquet supports a powerful set of encodings, but it doesn’t keep up with the development of new, sometimes purpose-specific, encodings. Adding a new encoding requires modifying the file reader itself. This is difficult as there are many Parquet implementations and development of Parquet has slowed now that the technology has matured.

### Flexible Metadata

In Parquet, an encoding can only control what goes into the data page. This means that encodings have no access to the column or file metadata. For example, consider dictionary encoding, where we know the dictionary will be constant throughout a column. We would ideally like to put the dictionary in the column metadata but we are instead forced to put it into every single row group. Another use case is skip tables for run length encoded columns. If we can put these in the column metadata then we can trade slightly larger metadata for much faster point lookups into RLE encoded columns.

![Metadata Flexibility Issues](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaade_flexible-metadata-parquet.avif)

A lack of metadata flexiblity forces some unfortunate encoding decisions in various cases

### And More

We have considered more use cases, some of them perhaps a bit esoteric, when building Lance v2, and I don’t want to bore you by listing them exhaustively. Instead, here is a short list of remaining things we have considered and incorporated that don’t merit further explanation:

## The Format

Now let me describe the [Lance v2 format](https://github.com/westonpace/lance/blob/821eb0461e7e474155485db32ac589b1933ef251/protos/file2.proto) (take a look, it’s less than 50 lines of protobuf) and explain how it solves the various use cases I have mentioned above.

![Lance v2 Format Overview](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaaf1_lance-v2-format.avif)

🥱

The rest of this article goes into detail about the file format’s design decisions. If your goal is just to understand what problems we are solving then you can skip it or feel free to come back and read later when you’re well rested.

## Feature 1: Encodings are Extensions

Lance v2 does not have encodings. These are handled entirely by extensions. The file readers and writers are completely unaware of any kind of encoding (even plain encoding). The data producer’s choice of what encoding to use and the details of how that encoding works are determined by plugins. New encodings can be written without any modification to the file format, the file writer, or the file reader. This is done by storing all encoding descriptions as protobuf “any” messages. This is why we refer to Lance v2 as a “columnar container format” (inspired by [container formats](https://en.wikipedia.org/wiki/Container_format) used for storing video).

### Corollary 1: There is No Type System

The Lance format itself does not have a type system. From Lance’s perspective, every column is simply a collection of pages (with an encoding) and each page a collection of buffers. Of course, the Lance readers and writers will actually need to convert between these pages into typed arrays of some kind. The readers and writers we have written use the [Arrow type system](https://arrow.apache.org/docs/format/Columnar.html).

The primary benefit is that it keeps the specification of the format simple. I do not have to tell you what types are supported and waste time describing them. It also helps avoid creating “yet another type system”

![Lance v2 Conceptual Overview](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaae7_Lance-v2-Conceptual-Overview.avif)

### Corollary 2: Empowering Encoding Developers

This makes it extremely easy to add a new encoding to Lance and helps to make the ecosystem fragmentation that Parquet has seen (e.g. mixed support for page lookups, delta encoding, etc.) more manageable. If I develop some new encoding then I just need to publish a .proto file to standardize how the encoding is described and write at least one implementation of the encoder/decoder. If a user tries to read a file written with this encoding, and their reader does not support it, then they will receive a helpful error “this file uses encoding X and the reader has not been configured with a decoder”. They can then figure out how to install the decoder (or implement it if need be). All of this happens without any change to the Lance format itself.

For example, take a look at our [current set of encodings](https://github.com/lance-format/lance/blob/v0.10.10/protos/encodings.proto), which encode Arrow data in a fairly plain format.

## Feature 2: Abolish Row Groups

Row groups (or stripes) are a clever idea that have outlived their usefulness. Some days, it feels like I keep [writing](https://stackoverflow.com/a/76782501) the same [book](https://lists.apache.org/thread/4nhbwplpj351g1xjqh5wqtb0nz3vw30k) on finding the proper balance for this finicky parameter. If the row group size is too small then you end up with excess metadata, poor performance, and most importantly, you end up with runt pages which are below the optimal read size for a filesystem (and you can’t coalesce your way out of this problem because the pages you want are pretty much guaranteed to be maximally spread throughout the file).

If the row group size is too large then, at a minimum, you are going to require a significant amount of RAM to be buffered in your file writer. However, many existing Parquet readers (e.g. pyarrow) treat the row group size as the unit of computation. This means that you end up using way too much RAM when reading a file too.

![Row Group Conundrum](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaaed_Row-Group-Conundrum.avif)

Row groups are a bad choice for multi-thread parallelism (within a process). Imagine you have 10 cores and so you try to read 10 row groups at once. Each row group reader now has to read (let’s say) 5 columns. This means you will launch 50 IOPS simultaneously. First, this is possibly over-scheduling your I/O. Second, in the average / expected case you won’t start compute until roughly all 50 of these IOPS complete. There are much better ways to do multi-thread parallelism (pipeline parallelism instead of data parallelism).

![Row Group Multithreading Issues](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaae1_Row-Group-Multithreading.avif)

Row groups are a reasonable choice for multi-process parallelism. But…so are files. From our perspective, a file with 10 row groups is no different than 10 files. If you need multi-process parallelism then just make 10 files. This will be easier to manage anyways (e.g. sharding)

Lance v2 does away with row groups, and the best part is that there are zero tradeoffs. You will get maximally sized data pages with minimal RAM buffering in the writer and reader. The trick is fairly simple, *we do not require pages within a column to be next to each other*. When a column writer has accumulated enough data it will flush a page to disk. Since pages should be larger than the minimum read of the filesystem there is no penalty to performance when reading a single column in entirety. Some writers will write lots of pages. Some writers will only write a single page throughout the entire file.

This may sound fantastical or exotic but this is actually very close to what happens in parquet-rs today when the file has only a single row group and a page lookup table is used. We are simply making this the norm and, because we do that, we can be a bit more flexible in the way we write the file.

### Corollary 1: Ideal Page Sizes

Each column writer will have its own buffer that it uses when writing pages. These can all be configured to match the ideal page size for your filesystem (e.g. 8MiB is a good choice for S3). The only time a page will be less than 8MiB is when it is the last page for that column within the file.

Imagine you are writing 10Mi rows to a file using 8MiB pages. One column is 8-byte doubles and so you want to write 10 pages (probably less with compressive encodings). Another column is a boolean column and so you only need to write 1 page (you can fit 64Mi bools into an 8MiB page).

### Corollary 2: Decoupling I/O and Compute

Now, imagine we are reading that file, let’s pretend there are only those two columns. First we will read the first double page and the boolean page (there is only one). As soon as those two 8MiB reads complete now have 1Mi values of the double column and 10Mi values of the boolean column.

We get to choose the batch size for our read, completely independent of our I/O size. Let’s assume we decided we want to process 10Ki rows at a time. Once those two pages arrive we can launch 100 decode tasks, one for each 10Ki rows we have. While those decode tasks are running we can fetch the remaining double pages.

![Lance Read Architecture](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaad8_Lance-Read-Architecture-2-.avif)

## Feature 3: Flexibility

Columns in Lance do not need to be the same length. When writing a Lance file, it is possible to write an “array at a time” instead of writing a “batch at a time” (or even a mixture of the two approaches). Data can be placed in a page buffer, a column buffer, or a file buffer. This allows the format to be more flexible and opens up the door to a whole new branch of use cases that Parquet is not eligible for.

### Corollary 1: “True” Column Projection

The Lance metadata is structured in such a way that each column’s metadata is in a completely independent block. Partly this is possible because there is no “schema” (though you can store one in the file-wide metadata if you want) since there are no types. What this means is that you can read a single column without reading any metadata from any other column. It should be possible to have hundreds of thousands or even millions of columns in a Lance file with no impact on performance.

### Corollary 2: Fluidity Between Data & Metadata

Back when Arrow-cpp was initially being developed there was some confusion on how dictionary encoding should work. Dictionary encoding encodes an array into “indices” and a “dictionary”. The indices take the normal spot in the data page…but what about the dictionary? Should the dictionary be considered *data* (and part of the record batches) or *metadata* (and part of the schema)? Both approaches have pros and cons. Eventually, since Parquet chose to store dictionaries as data then Arrow followed suit (although the IPC format occupies a strange middle ground). On the other hand, Lance v1 chose the opposite approach because putting dictionaries in the data pages gave point lookups unreasonable latency.

Lance v2 allows the writer to choose the most appropriate location. If the dictionary can be provided up front then the writer should put it in the column metadata. If it differs from page to page then the writer should write page specific dictionaries. This fluidity goes way beyond dictionaries however. Skip tables for RLE and zone maps (discussed further soon) can also be placed in column metadata. Even nullability information can be stored in the column metadata (e.g. if a column only has a few nulls the put the nullability in the metadata to avoid another IOP on point lookups).

![Flexible Metadata Approaches](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaadb_Flexible-Metadata-1-.avif)

What’s more, any piece of information that is truly file-wide (e.g. the arrow schema of the data or a common dictionary shared by several columns) can be stored into a space for file-wide buffers. Encodings can make this decision (where to store a piece of data) on-the-fly based on the data they are writing.

### Corollary 3: Statistics are Encoding Metadata

In Parquet, file statistics (e.g. zone maps) are a 1st-class entity and part of the top-level format. However, this means a format change is required to support a new kind of statistics. It turns out, there are many ways to store statistics (e.g. skip tables in RLE, histograms, bloom filters, etc.) and so this is kind of inconvenient. Also, making them part of the top-level format means your zone map resolution is tied to your data page size, encouraging either small pages or large zones (this is not as bad as it seems, as tiny pages in big column chunks can be coalesced, unlike tiny pages in tiny column chunks discussed earlier, but the two concepts still don’t need to be related).

![Statistics as Metadata](https://cdn.prod.website-files.com/69b2da72cae7eea2b0091d5f/69c029a90065f57b2bfaaaf4_StatsAsMetadata.avif)

In Lance v2, statistics are just a part of the encoding process. A zone map is just a proxy layer in the encoding and the resulting zone maps can be stored in the column metadata (in the same way any piece of information can be stored in the column metadata). These can then be utilized on read to apply pushdown filters the same way zone maps are used today. Switching to a different statistics format is simply another encoding and doesn’t require a change in the format.

## We Can Use Your Help

We currently have an initial implementation that only uses simple encodings and doesn’t yet use offer most of the features discussed, but it adds the groundwork for the format. We have verified that performance is on par with the best Parquet readers (currently this is only true when data is not very compressible but we expect this will be true in general as we add better encodings). The one thing we do not need at the moment is development help. However, we need help in just about every other way.

`import pyarrow as pa  
  
from lance.file import LanceFileReader, LanceFileWriter  
  
# It's still early days so doing too much more than this will  
# probably break :)  
table = pa.table({  
    "my_list": [[1, 2, 3], [4, 5]],  
    "my_struct": [  
        { "x": 1, "y": 1 }, { "x": 2, "y": 2 }  
    ],  
    "my_col": [11.0, 12.0]  
})  
  
# No surprise in reader/writer API I hope  
with LanceFileWriter("/tmp/foo.lance", schema=table.schema) as writer:  
    # Currently only support writing a batch at a time, array at a  
    # time API to come later  
    writer.write_batch(table)  
  
reader = LanceFileReader("/tmp/foo.lance", schema=table.schema)  
# Can read whole table (to_table) or batch at a time (to_batches)  
assert table == reader.read_all().to_table()  
  
# Perhaps the most interesting bit is we can print the metadata to  
# see what encodings are used and how big the metadata is  
print(reader.metadata())`

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