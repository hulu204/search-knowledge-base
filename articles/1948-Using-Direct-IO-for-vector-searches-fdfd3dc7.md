---
title: 'Using Direct IO for vector searches'
company: Elastic
tag: 工程相关
date: 2025-08-08
url: https://www.elastic.co/search-labs/blog/knn-vector-search-rescoring-direct-io
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Using Direct IO for vector searches

Using rescoring for kNN vector searches improves search recall, but can increase latency. Learn how to reduce this impact by leveraging direct IO.

August 08, 2025

[Simon Cooper](/search-labs/author/simon-cooper)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In Elasticsearch 9.0, we introduced [kNN vector rescoring](https://www.elastic.co/docs/solutions/search/vector/knn#dense-vector-knn-search-rescoring) for searches over fields using quantized vectors. While rescoring significantly improves recall, it can substantially increase latency in some situations. To understand why, we’ll examine what rescoring does and how Lucene and the operating system manage data on disk. We’ll also explain how enabling direct IO affects latency.

## How vector rescoring works

An HNSW quantized vector index stores:

1. The HNSW graph used to navigate the vector space
2. The quantized vector data as bits
3. The original raw vector data as 32-bit floats

When an approximate kNN search is performed, the HNSW graph is navigated to find the *k*-nearest vectors to the search vector, using the quantized vector data. If rescoring is enabled, the graph is oversampled by a factor of 3 by default, meaning that 3\**k* quantized vectors are searched for in the graph. The rescoring step then filters those 3\**k* oversampled quantized vectors down to the *k* nearest vectors using the unquantized raw vector data.

For each oversampled quantized vector, the original raw vector is retrieved and compared against the search vector to find the *k* nearest actual vectors, which are then returned from the query. This operation requires a random-access read into the raw vector data for every oversampled vector. And the raw vector data can be very large—often taking up 90-95% of the whole index, which can be many, many gigabytes or terabytes.

## Why the page cache becomes a bottleneck

When the operating system reads data from disk—whether SSD, NVMe, or spinning disk—it caches a copy of the data read into RAM in case the data or data around it is needed again. This is usually done in 4KB *pages*; hence, it’s called the *page cache*. The OS uses any spare RAM in the system for the page cache:

```
$ free -m
       total  used   free  shared  buff/cache  available
Mem:   31536  14623  6771  1425    12021       1691
```

*In this example, the system has 32GB of RAM. 15GB is being used by running programs, and 12GB is being used by the page cache and other buffers.*

So, in order to read data from disk, the OS first copies the relevant pages being requested from disk into memory. Then, that data is made available to the running program to access. If there is not enough free RAM to store the just-read page, an existing page is evicted from the page cache, and the new page replaces it.

But which page should be evicted? This is the age-old software engineering problem of *cache invalidation*. Modern OSs have gotten pretty good at deciding which pages are unlikely to be needed in the future, but they can’t (yet) predict the future. And the random-access pattern of vector rescoring is completely unpredictable, leaving the OS to essentially guess which page should be evicted.

This is a problem. The raw vector data for the oversampled vectors could be located anywhere in the index, and there could be a *lot* of pages to read depending on *k*. This might mean the OS needs to evict many pages during rescoring—including those which have the HNSW graph on them.

```
$ sar -B 1
 pgpgin/s  pgpgout/s   fault/s  majflt/s
112099.20   16493.60  11562.00  10761.60
```

That’s a *lot* of page faults.

See, the OS doesn’t *know* what the pages are used for, or what’s on them. It also doesn’t know that the HNSW graph is used at the start of every vector query on that index. To the OS, these are just bytes on disk, along with information on previous access times. If the HNSW graph’s pages are evicted, then some or all of it needs to be reloaded for the next vector query. And disk access times are *long*, at least compared to memory access times. Tens of microseconds for NVMe, hundreds for SSDs, and many milliseconds for HDDs.

The effect of this is that when vector data gets large enough to no longer fit entirely in the page cache, the OS starts swapping out pages for every single query—causing query performance to plummet dramatically, as it constantly switches between the HNSW graph and the raw vectors. An extra few gigabytes of vector data can cause query latency to increase by *100x*, and sometimes even more.

## Direct IO to the rescue

So what’s to be done? The page cache is controlled by the OS, not Elasticsearch—so can we actually do anything about that? Fortunately, we can. Besides providing various hints to the OS about the purpose of the data read from disk (which the OS can use or not as it sees fit), we can also tell the OS to *bypass the page cache completely*, and just read directly from disk for every access. This is called ‘direct IO’.

Obviously, this is much slower than reading from an already-cached page in RAM, but it stops existing pages from being evicted from the page cache to store the new page. Importantly, this allows the OS to leave the HNSW graph in memory, where it belongs.

The effect of direct IO on search latency in low-memory scenarios is dramatic (note the logarithmic scale):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt116c86e3982f57da/6a17dc57af47b65f1acdde4d/f6019aabf221c56454c7455c6da67a3fc1147fc2-892x548.png)

However, it does come at a cost. Because direct IO forces the page cache to be bypassed, turning on direct IO when there *is* enough memory to store all the vector data causes a huge slowdown:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbcfabf87bc5a9570/6a17dc59420229c54229f4d0/64fb223d771c223294c8db6d8387407ad3cc8192-892x548.png)

Ideally, we would detect when vector data is being swapped in and out of the page cache, but that’s tricky with the tools available within the JVM. We’re working on it, but we’re not there yet.

## When (and when not) to enable direct IO?

As you can see, turning on direct IO when your vector data is too large for RAM dramatically reduces the high latencies of kNN vector searches in such situations. But, turning on direct IO when you *do* have enough memory causes a large slowdown.

Starting in Elasticsearch 9.1, you can use direct IO for vector rescoring on `bbq_hnsw` indices. For now, it’s turned off by default, since it can cause a performance drop when enough memory is available. But if you are seeing very large latencies in your vector searches, try [adding the JVM option](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/approximate-knn-search#use-direct-io-when-the-vector-data-does-not-fit-in-ram)
`-Dvector.rescoring.directio=true` to enable direct IO for all rescoring on `bbq_hnsw` indices.

We’re looking into different ways to expose that option in the future, and to evaluate the various performance differentials for future Elasticsearch versions. Nonetheless, if you find that it improves your vector search performance, do let us know!

Note that there is a [known issue for Elasticsearch 9.1.0](https://www.elastic.co/docs/release-notes/elasticsearch/known-issues#elasticsearch-9.1.0-known-issues) where direct IO is turned *on* by default. This will be fixed in Elasticsearch 9.1.1. We’re continuing to evaluate the uses of direct IO and how this access method might be used in the future.

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