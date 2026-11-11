---
title: 'Making Lucene faster with vectorization and FFI/madvise'
company: Elastic
tag: 工程相关
date: 2024-04-17
url: https://www.elastic.co/search-labs/blog/lucene-and-java-moving-forward-together
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Making Lucene faster with vectorization and FFI/madvise

Discover how modern Java features, including vectorization and FFI/madvise, are speeding up Lucene's performance.

April 17, 2024

[Chris Hegarty](/search-labs/author/chris-hegarty)

[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

Over in Lucene-land we've been eagerly adopting features of new Java versions. These features bring Lucene closer to both the JVM and the underlying hardware, which improves performance and stability. This keeps Lucene modern and competitive.

The next major release of Lucene, Lucene 10, will [require a minimum](https://github.com/apache/lucene/pull/12753) of Java 21. Let's take a look at why we decided to do this and how it will benefit Lucene.

## Foreign memory

For efficiency reasons, indices and their various supporting structures are stored outside of the Java heap - they are stored on-disk and mapped into the process' virtual address space. Until recently, the way to do this in Java is with direct byte buffers, which is exactly what Lucene has been doing.

Direct byte buffers have some inherent limitations. For example, they can address a maximum of 2GB, requiring more structures and code to span over larger sizes. However, most significant is the lack of deterministic closure, which we workaround by calling [`Unsafe::invokeCleaner`](https://bugs.openjdk.org/browse/JDK-8171377) to effectively close the buffer and release the memory. This is, as the name suggests, inherently an *unsafe* operation. Lucene adds safeguards around this, but, by definition, there is still a miniscule risk of failure if memory were to be accessed after it was released.

More recently Java has added `MemorySegment`, which overcomes the limitations that we encounter with direct byte buffers. We now have *safe* deterministic closure and can address memory far beyond that of previous limits. While Lucene 9.x already has optional support for a mapped directory implementation backed by memory segments, the upcoming Lucene 10 drops support for byte buffers. All this means that Lucene 10 only operates with memory segments, so is finally operating in a *safe* model.

## Foreign function

Different workloads; search or indexing, or different types of data, say, doc values or vector embeddings, have different access patterns. As we've seen, because of the way Lucene maps its index data, interaction with the operating system page cache is crucial to performance.

Over the years a lot of effort and consideration has been given to optimizations around memory usage and page cache. First through native JNI code that calls `madvise` directly, and later with a directory implementation that uses direct I/O. However, while good at the time, both these solutions are a little less than ideal. The former requires platform specific builds and artifacts, and the latter leverages an optional [JDK-specific API](https://github.com/apache/lucene/blob/main/lucene/misc/src/java/org/apache/lucene/misc/store/DirectIODirectory.java#L75). For these reasons, neither solution is part of Lucene core, but instead lives in the further afield `misc` module. Mike McCandless has a good [blog](http://blog.mikemccandless.com/2010/06/lucene-and-fadvisemadvise.html) about this, from 2010!

On modern Java we can now use the Panama Foreign Function Interface (FFI) to call library functions native on the system. We use this, directly in [Lucene core](https://github.com/apache/lucene/pull/13196), to call `posix_madvise` from the Standard C library - all from Java, and without the need for any JNI code or non-standard features. With this we can now advise the system about the type of memory access patterns we intend to use.

## Vectorization

Parallelism and concurrency, while distinct, often translate to "splitting a task so that it can be performed more quickly", or "doing more tasks at once". Lucene is continually looking at new algorithms and striving to implement existing ones in more performant and efficient ways. One area that is now more straightforward to us in Java is data level parallelism - the use of SIMD (Single Instruction Multiple Data) vector instructions to boost performance.

Lucene is using the latest JDK Vector API to implement vector distance computations that result in efficient hardware specific SIMD instructions. These instructions, when run on supporting hardware, can perform floating point dot product computations 8 times faster than the equivalent scalar code. This [blog](https://www.elastic.co/blog/accelerating-vector-search-simd-instructions) contains more specific information on this particular optimization.

With the move to Java 21 minimum, it is a lot more straightforward to see how we can use the JDK Vector API in more places. We're even experimenting with the possibility of calling customized SIMD implementations with FFI, since the overhead of the native call is now quite minimal.

## Conclusion

While the latest Lucene 9.x releases are able to benefit from many of the recent Java features, the requirement to run on versions of Java as early as Java 11 means that we're reaching a level of complexity with 9.x that, while maybe still ok today, is not where we want to be in the future.

The upcoming Lucene 10 will be closer to the JVM and the hardware than ever before. By requiring a minimum of Java 21, we are able to drop the older direct byte buffer directory implementation, reliably advise the system about memory access patterns through `posix_madvise`, and continue our efforts around levering hardware accelerated instructions.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt762b38f91bd71c8e/6a170db8b339d547bb76a048/368db71c500e72d20fe225fe44c2c40231e29765-721x420.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Bringing maximum-inner-product into Lucene

September 01, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9ec7a04e3bdbfd9f/6a467b337eb22d59efdfc54d/c07100b6fcc74dba250e6853b1c5ef1edabbedfc-1920x1080.png)

[Lucene](/search-labs/blog/category/lucene)[Index Data](/search-labs/blog/category/index-data)

### How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage

June 12, 2026|[Alan Woodward](/search-labs/author/alan-woodward)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf9fcbf843affc566/6a1706b8964ceaea3208bab9/7884e35f40c15fe349379ef7ae4648b21708962f-1070x712.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Concurrency bugs in Lucene: How to fix optimistic concurrency failures

February 07, 2025|[Benjamin Trent](/search-labs/author/benjamin-trent)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter