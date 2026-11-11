---
title: 'Low-memory benchmarking in DiskBBQ and HNSW BBQ'
company: Elastic
tag: 索引构建
date: 2025-10-23
url: https://www.elastic.co/search-labs/blog/elasticsearch-latency-low-memory-diskbbq-hnswbbq-benchmark
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Low-memory benchmarking in DiskBBQ and HNSW BBQ

Benchmarking Elasticsearch latency, indexing speed, and memory usage for DiskBBQ and HNSW BBQ in low-memory environments.

October 23, 2025

[John Wagster](/search-labs/author/john-wagster)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Recently, we introduced our new [DiskBBQ](https://www.elastic.co/search-labs/blog/diskbbq-elasticsearch-introduction) format for vector storage and search within Elasticsearch. One of the main advantages of exploring subsets of the vectors from the entire set of data is that we can better manage what’s loaded on heap and needed at query time to satisfy a query. This, of course, leads to the inevitable question: How low can we go? Where do we start to see major drop-offs in performance? For this blog, we’ll consider any performance degradation as a low-memory scenario. Now let’s go see what we can find.

## Show me the numbers

### Search

In our introductory blog, we talked about some high-level numbers. Let’s look back at the high-level query timings graph and dig a little deeper:

![Figure 0: Shows search latency in milliseconds vs RAM / JVM Heap](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt20b1810f3eb4d5c0/6a17ef705ea30f506064b696/7ff26931543d46f9da0c917de58ba2ba574ab469-1334x822.png)

Figure 0: Shows search latency in milliseconds vs RAM / JVM Heap

DiskBBQ degrades in search latency, but is much more well-behaved than HNSW BBQ, which behaves exponentially as memory becomes increasingly restricted. But what does DiskBBQ look at in comparison as we add more memory?

Here’s those actual numbers laid out. And you can better see how DiskBBQ behaves in lower memory states. It definitely benefits from more RAM to better cache more clusters of vectors. Particularly, we rely heavily on off-heap cache, and as that increases, we see better performance until the whole of the quantized vectors are resident.

| Type | Ram / Heap | Latency (ms) |
| --- | --- | --- |
| DiskBBQ | 101m / 10m | 15.83 |
| DiskBBQ | 150m / 100m | 12.13 |
| DiskBBQ | 250m / 150m | 7.46 |
| DiskBBQ | 350m / 250m | 3.65 |
| DiskBBQ | 450m / 350m | 2.38 |
| DiskBBQ | 550m / 450m | 2.41 |
| HNSW BBQ | 101m / 10m | - |
| HNSW BBQ | 150m / 100m | 289.7 |
| HNSW BBQ | 250m / 150m | 26.81 |
| HNSW BBQ | 350m / 250m | 7.7 |
| HNSW BBQ | 450m / 350m | 3.06 |
| HNSW BBQ | 550m / 450m | 3.14 |

Here’s an additional run of 1m vectors only on DiskBBQ. Here, I did less to refine the exact ratios of RAM and Heap, and instead typically set one to half the other. We’ve also run it with up to 10g of RAM here. What’s interesting is to note the inflection point where the algorithm is no longer in a low memory configuration and no longer benefits from additional memory, in this case around `800m/400m`.

| RAM / Heap | Latency (ms) |
| --- | --- |
| 101m / 10m | 18 |
| 150m / 75m | 12.13 |
| 200m / 100m | 11.02 |
| 300m / 150m | 4.26 |
| 400m / 200m | 3.47 |
| 500m / 250m | 3.5 |
| 800m / 400m | 2.73 |
| 1.2g / 600m | 2.76 |
| 1.5g / 750m | 2.74 |
| 3g / 1.5g | 2.83 |
| 5g / 2.5g | 2.78 |
| 8g / 4g | 2.73 |
| 10g / 5g | 2.79 |

### Indexing

Let’s also take a look at the indexing performance.

![Figure 1: Shows index time in milliseconds vs RAM / JVM Heap](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt82c6159819fd196d/6a17ef71ddf97d08bb910be9/790bf340586821ee92c3f6e1a19aa64f9be527e6-1370x860.png)

Figure 1: Shows index time in milliseconds vs RAM / JVM Heap

As overall memory reduces, DiskBBQ indexing degrades gracefully. HNSW BBQ, however, simply falls apart once memory gets very restricted. And downright fails in scenarios where DiskBBQ continues to operate. Again, let’s look at the numbers to get a better understanding of what’s happening.

| Type | Ram / Heap | Index Time (ms) |
| --- | --- | --- |
| DiskBBQ | 550m / 450m | 183377 |
| DiskBBQ | 750m / 650m | 187123 |
| DiskBBQ | 1g / 850m | 82397 |
| DiskBBQ | 2g / 1500m | 64567 |
| DiskBBQ | 3g / 2000m | 39002 |
| DiskBBQ | 4g / 2500m | 38448 |
| HNSW BBQ | 550m / 450m | - |
| HNSW BBQ | 750m / 650m | - |
| HNSW BBQ | 1g / 850m | - |
| HNSW BBQ | 2g / 1500m | 322338 322338 |
| HNSW BBQ | 3g / 2000m | 273239 |
| HNSW BBQ | 4g / 2500m | 278005 |

As DiskBBQ can utilize more off heap cache space, larger chunks of particularly the raw vectors stay resident, which is especially useful as we partition the space with [hierarchical k-means](https://www.elastic.co/search-labs/blog/k-means-for-vector-indices).

## Evaluation methodology

First, we isolate the two algorithms, DiskBBQ and HNSW BBQ, within Elasticsearch and compare them. We’ll focus on some reasonable defaults like the default merge policy within Elasticsearch. For 1m vectors, this gives us about ~12 segments. Not huge, but still interesting in low memory configurations.

To help facilitate this, we have the `KnnIndexTester` utility in Elasticsearch, which can do evaluations of different KNN algorithms.

Here’s what it looks like to invoke it:

```
./gradlew :qa:vector:checkVec --args="/Users/jwagster/Desktop/knn_dbpedia_config.json"
```

And here’s what that configuration looks like for DiskBBQ:

```
[{
  "doc_vectors" : ["/data/corpus-dbpedia-entity-E5-small-0.fvec", "/data/corpus-dbpedia-entity-E5-small-1.fvec", "/data/corpus-dbpedia-entity-E5-small-2.fvec", "/data/corpus-dbpedia-entity-E5-small-3.fvec", "/data/corpus-dbpedia-entity-E5-small-4.fvec"],
  "query_vectors" : "/data/queries-dbpedia-entity-E5-small-0.fvec",
  "num_docs" : 1000000,
  "num_queries" : 400,
  "visit_percentage": 10,
  "ivf_cluster_size": 384,
  "over_sampling_factor": 5,
  "index_type" : "ivf",
  "k" : 10,
  "index_threads" : 4,
  "quantize_bits": 1,
  "reindex" : true,
  "force_merge" : true,
  "vector_space" : "maximum_inner_product",
  "dimensions" : -1
}]
```

It’s worth paying particular attention to things like `visit_percentage` which indicates how much of a segment we explore before giving up. And `over_sampling_factor,` which will help with recovering quality during rescoring given that we’re using [BBQ](https://www.elastic.co/search-labs/blog/scalar-quantization-optimization) to reduce the overall size of our indices.

And here’s what that configuration looks like for [HNSW](https://arxiv.org/abs/1603.09320):

```
[{
  "doc_vectors" : ["/data/corpus-dbpedia-entity-E5-small-0.fvec", "/data/corpus-dbpedia-entity-E5-small-1.fvec", "/data/corpus-dbpedia-entity-E5-small-2.fvec", "/data/corpus-dbpedia-entity-E5-small-3.fvec", "/data/corpus-dbpedia-entity-E5-small-4.fvec"],
  "query_vectors" : "/data/queries-dbpedia-entity-E5-small-0.fvec",
  "num_docs" : 1000000,
  "num_queries" : 400,
  "ivf_cluster_size": 385,
  "over_sampling_factor": 5,
  "index_type" : "hnsw",
  "num_candidates" : 1000,
  "k" : 10,
  "index_threads" : 4,
  "quantize_bits": 1,
  "reindex" : true,
  "force_merge" : true,
  "vector_space" : "maximum_inner_product",
  "dimensions" : -1
}]
```

The configurations are set up to provide roughly the same recall in this case ~0.89. Note that for HNSW, we quantize to a single bit using BBQ just as we did with DiskBBQ.

We can use the `KnnIndexTester` utility and isolate it from the rest of the system using Docker. We disable swap and control for the total memory allocated to the container for our experiments.

Here’s an example of what that looks like with a simple HelloWorld.java

```
docker run -v /elasticsearch:/elasticsearch -v /data:/data -v /root/.gradle:/root/.gradle --name dev --workdir /elasticsearch --memory="60m" --memory-swap="60m" -it openjdk:24-jdk-slim-bookworm java /elasticsearch/HelloWorld.java
```

And here’s what it looks like when invoking the KnnIndexTester QA Utility:

```
docker run -v /elasticsearch:/elasticsearch -v /data:/data -v /root/.gradle:/root/.gradle --name dev --workdir /elasticsearch --memory="101m" --memory-swap="101m" -it --rm openjdk:24-jdk-slim-bookworm java -Des.nativelibs.path=/elasticsearch/libs/native/libraries/build/platform/linux-aarch64 -Djava.util.concurrent.ForkJoinPool.common.parallelism=8 -Dorg.apache.lucene.store.defaultReadAdvice=normal -XX:+UnlockDiagnosticVMOptions -XX:+DebugNonSafepoints -XX:+HeapDumpOnOutOfMemoryError --add-modules=jdk.incubator.vector --enable-native-access=ALL-UNNAMED -Xms10m -Xmx10m -cp /elasticsearch/qa/vector/build/classes/java/main:/elasticsearch/qa/vector/build/resources/main:/elasticsearch/server/build/distributions/elasticsearch-9.2.0-SNAPSHOT.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-grouping/10.2.2/da045cff5cfc86869be34338935e8d65456f7bd2/lucene-grouping-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-highlighter/10.2.2/571fda0e8a9bf54896ab592143a09b39fdb036ee/lucene-highlighter-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-queryparser/10.2.2/bb94dc5a00f01ccc7dc6804388bc7fe9f0070c75/lucene-queryparser-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-sandbox/10.2.2/85c59725df3e564f69fe34e568373367b32781fe/lucene-sandbox-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-queries/10.2.2/6dfc2197d9deacb699d7dc04f0afa919c926695e/lucene-queries-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-codecs/10.2.2/92fcaca5ac2264bf35ae1c95f1961527dc1a21bb/lucene-codecs-10.2.2.jar:/elasticsearch/libs/simdvec/build/distributions/elasticsearch-simdvec-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/plugin-analysis-api/build/distributions/elasticsearch-plugin-analysis-api-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/tdigest/build/distributions/elasticsearch-tdigest-9.2.0-SNAPSHOT.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-suggest/10.2.2/ddb40a1559e45d77c9417c8f6e6bb29c4c4dba8d/lucene-suggest-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-analysis-common/10.2.2/2c35eb96330d96b6ffb61856ce2cd886a5656c81/lucene-analysis-common-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-backward-codecs/10.2.2/848ccaaadbcc97c84c09ad808fe4354af00449d9/lucene-backward-codecs-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-facet/10.2.2/a81ff8e4b40d2510b88aa55084d7d6cb280500a3/lucene-facet-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-join/10.2.2/f1cd23b8d1773ec6b62f1972d47dae9102721f33/lucene-join-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-memory/10.2.2/8709740d758b9358d0c9e3f4fcd34c9604740e20/lucene-memory-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-misc/10.2.2/47de3cefc3aa78ba11593d72c60f5b17a611c73/lucene-misc-10.2.2.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.lucene/lucene-core/10.2.2/336a9c4b24e5704bd5fd71af794cce80f479a3ae/lucene-core-10.2.2.jar:/elasticsearch/libs/native/build/distributions/elasticsearch-native-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/cli/build/distributions/elasticsearch-cli-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/logging/build/distributions/elasticsearch-logging-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/x-content/build/distributions/elasticsearch-x-content-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/lz4/build/distributions/elasticsearch-lz4-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/core/build/distributions/elasticsearch-core-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/geo/build/distributions/elasticsearch-geo-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/plugin-api/build/distributions/elasticsearch-plugin-api-9.2.0-SNAPSHOT.jar:/elasticsearch/libs/grok/build/distributions/elasticsearch-grok-9.2.0-SNAPSHOT.jar:/root/.gradle/caches/modules-2/files-2.1/org.hdrhistogram/HdrHistogram/2.1.9/e4631ce165eb400edecfa32e03d3f1be53dee754/HdrHistogram-2.1.9.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-api/2.19.0/ea1b37f38c327596b216542bc636cfdc0b8036fa/log4j-api-2.19.0.jar:/root/.gradle/caches/modules-2/files-2.1/org.apache.logging.log4j/log4j-core/2.19.0/3b6eeb4de4c49c0fe38a4ee27188ff5fee44d0bb/log4j-core-2.19.0.jar:/root/.gradle/caches/modules-2/files-2.1/co.elastic.logging/log4j2-ecs-layout/1.2.0/ba51fb2064cd5f6bc136e95c1463e3e68d823403/log4j2-ecs-layout-1.2.0.jar:/root/.gradle/caches/modules-2/files-2.1/co.elastic.logging/ecs-logging-core/1.2.0/37a47ec302777aca9f8ea10b7316f3a79d5d6202/ecs-logging-core-1.2.0.jar:/elasticsearch/libs/entitlement/build/distributions/elasticsearch-entitlement-9.2.0-SNAPSHOT.jar:/root/.gradle/caches/modules-2/files-2.1/com.carrotsearch/hppc/0.8.1/ffc7ba8f289428b9508ab484b8001dea944ae603/hppc-0.8.1.jar:/root/.gradle/caches/modules-2/files-2.1/org.lz4/lz4-java/1.8.0/4b986a99445e49ea5fbf5d149c4b63f6ed6c6780/lz4-java-1.8.0.jar:/root/.gradle/caches/modules-2/files-2.1/org.jruby.joni/joni/2.1.29/3cb751702e1194ff24259155db4d37e9383d4320/joni-2.1.29.jar:/root/.gradle/caches/modules-2/files-2.1/org.jruby.jcodings/jcodings/1.0.44/a6884b2fd8fd9a56874db05afaa22435043a2e3e/jcodings-1.0.44.jar:/root/.gradle/caches/modules-2/files-2.1/net.sf.jopt-simple/jopt-simple/5.0.2/98cafc6081d5632b61be2c9e60650b64ddbc637c/jopt-simple-5.0.2.jar org.elasticsearch.test.knn.KnnIndexTester knn_dbpedia_diskbbq_config.json
```

## How low can we go?

The most exciting thing that may not be readily apparent is that we measured additional heap settings down to 10MB, and anything less than this, and log4j can’t be initialized in our utility. We’re able to run the entire container in 101MB of memory, and anything less than this, and the OS sends a SIGKILL (exit 137) every time Java attempts to load the utility itself while attempting to load the index files off heap. While it’s somewhat slow, our test framework shows that it’s still pretty fast overall, with a query latency in this configuration taking only ~15ms.

I’m having fun. Let’s poke some more. What if I just want to know what’s the absolute smallest possible heap I can get here? Well, if you create a program called HelloWorld.java and shove a one-line program into it like this:

```
public class HelloWorld { public static void main(String[] args) { System.out.println("Hello, World!"); } }
```

The smallest JVM you can run that one program on is 2m. As in this will fail:

```
java -Xmx1m -Xms1m HelloWorld.java
```

With this error message:

```
Error occurred during initialization of VM
Too small maximum heap
```

But what happens when I try to run that program in the smallest possible memory settings we can use with `openjdk:24-jdk-slim-bookworm`. Here’s the actual smallest environment we can run in:

```
docker run -v /elasticsearch:/elasticsearch -v /data:/data -v /root/.gradle:/root/.gradle --name dev --workdir /elasticsearch --memory="50m" --memory-swap="50m" -it --rm openjdk:24-jdk-slim-bookworm java /elasticsearch/HelloWorld.java
Hello, World!
```

Anything lower than this and Docker executes a SIGKILL for OOM, presumably for seemingly innocuous tasks such as loading the HelloWorld.java file. We need at least 50MB just to do anything in the `openjdk:24-jdk-slim-bookworm` container.

So when running the DiskBBQ algorithm, we’re not quite at the bottom, but it does run in just 60MB of RAM. Remember, the JVM heap is taking up about 10MB of that total 101MB mentioned above. And DiskBBQ is likely taking most of the 50MB of off heap RAM in our smallest feasible configuration. That’s a pretty impressive stable configuration, particularly in comparison to HNSW. In HNSW we must load the entire graph of all vectors; otherwise, queries fall off a performance cliff.

## Conclusion

With the introduction of the `bbq_disk` format for vector storage and search within Elasticsearch we now have a more elegant way of handling low memory environments. Previously with HNSW we would see a particularly sharp drop in runtime and indexing performance when memory was not adequate to maintain the entire graph in memory. We've made significant strides in reducing the size of the HNSW graph in memory by introducing more intelligent quantization via (BBQ)[FIXME source], but as more vectors are added, the same problem emerges just at higher scales. DiskBBQ provides a novel approach to bypass some of the inherent flaws in HNSW.

DiskBBQ is available in [Elasticsearch Serverless](https://cloud.elastic.co/home)!

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