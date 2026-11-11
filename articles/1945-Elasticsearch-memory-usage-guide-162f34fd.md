---
title: 'Elasticsearch memory usage guide'
company: Elastic
tag: 工程相关
date: 2025-07-22
url: https://www.elastic.co/search-labs/blog/elasticsearch-memory-usage
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch memory usage guide

Exploring Elasticsearch memory requirements and the different types of memory statistics.

July 22, 2025

[Valentin Crettaz](/search-labs/author/valentin-crettaz)

[Inside Elastic](/search-labs/blog/category/inside-elastic)[Basics](/search-labs/blog/category/basics)

Jump to

Share

## **Elasticsearch memory requirements**

The Elasticsearch process is very memory intensive. Elasticsearch uses a JVM (Java Virtual Machine), and best practices recommend allocating close to 50% of the memory available on a node to the JVM. The JVM relies on memory so that the Lucene process can access index values very fast. The other 50% is left to the file system cache which keeps data that is regularly accessed in memory.

For a full explanation of JVM memory management, read [this blog](https://www.elastic.co/search-labs/blog/elasticsearch-heap-size-jvm-garbage-collection). It is also common to receive warnings from the different types of [circuit breakers](https://www.elastic.co/docs/reference/elasticsearch/configuration-reference/circuit-breaker-settings).

### **jvm.mem**

The most important memory section is the JVM heap.

```
GET _nodes/stats/jvm
```

The output looks like this:

```
"jvm" : {
   	"timestamp" : 1603351829573,
   	"uptime_in_millis" : 150932107,
   	"mem" : {
     	"heap_used_in_bytes" : 258714272,
     	"heap_used_percent" : 24,
     	"heap_committed_in_bytes" : 1073741824,
     	"heap_max_in_bytes" : 1073741824,
     	"non_heap_used_in_bytes" : 192365488,
     	"non_heap_committed_in_bytes" : 209186816,
```

Note that the heap\_used\_in\_bytes in a healthy JVM will follow a saw tooth pattern due to the garbage collection process, increasing steadily up to around 70%, then reducing sharply to 30% when garbage collection occurs.

The JVM heap\_max\_in\_bytes will depend on the value set in jvm.options file, and you should set it to be 50% of the RAM available for your container or server.

For more information on JVM heap issues, please see: [Heap size usage and JVM garbage collection in Elasticsearch](https://www.elastic.co/search-labs/blog/elasticsearch-heap-size-jvm-garbage-collection).

## **Explaining the different types of memory statistics**

When looking at the memory statistics, we need to be aware that many Elasticsearch applications are running inside containers on much larger machines. This is typical if you are using a hosted service such as AWS Elasticsearch service or Elastic cloud, or if you are running Elasticsearch on Docker or Kubernetes. In such cases, it’s important to be careful to interpret the memory statistics available to us.

There are various memory statistics available from the Elasticsearch monitoring APIs, as explained below:

```
GET _nodes/stats/os
	"os" : {
   	"timestamp" : 1603350306857,
   	"cpu" : {
     	"percent" : 13,
     	"load_average" : {
       	"1m" : 3.37,
       	"5m" : 3.18,
       	"15m" : 2.8
     	}
   	},
   	"mem" : {
     	"total_in_bytes" : 16703369216,
     	"free_in_bytes" : 361205760,
     	"used_in_bytes" : 16342163456,
     	"free_percent" : 2,
     	"used_percent" : 98
   	},
   	"swap" : {
     	"total_in_bytes" : 1023406080,
     	"free_in_bytes" : 1302528,
     	"used_in_bytes" : 1022103552
   	},
   	"cgroup" : {
     	"cpuacct" : {
       	"control_group" : "/",
       	"usage_nanos" : 2669636420088
     	},
     	"cpu" : {
       	"control_group" : "/",
       	"cfs_period_micros" : 100000,
       	"cfs_quota_micros" : -1,
       	"stat" : {
         	"number_of_elapsed_periods" : 0,
         	"number_of_times_throttled" : 0,
         	"time_throttled_nanos" : 0
       	}
     	},
     	"memory" : {
       	"control_group" : "/",
       	"limit_in_bytes" : "9223372036854771712",
       	"usage_in_bytes" : "4525641728"
     	}
   	}
 	}
```

The above statistics are for a development node running on Docker. Let’s interpret the sections we received here:

### **os.mem**

The first section “os.mem” refers to the host server where the machine is running. In this case we are running on Docker, so 16GB refers to the memory of the **host** machine where the container is running. Note that it is quite normal for a machine to be using close to 100% of its memory, and this does not indicate a problem.

### **os.swap**

The “os.swap” section again refers to the host machine. In this case, we can see that the host machine allows swapping. This is quite normal when we are running a container inside a host with swapping still enabled. We can double check that **inside** the Docker container no swap is permitted by running:

```
GET _nodes?filter_path=**.mlockall
```

### **os.cgroup**

Finally, we can see the “os.cgroup” section which refers to the container itself. In this case, the container is using 4GB of memory.

#### **process.mem**

We also have access to a statistic virtual memory:

```
GET _nodes/stats/process
 	"process" : {
   	"timestamp" : 1603352751181,
   	"open_file_descriptors" : 436,
   	"max_file_descriptors" : 1048576,
   	"cpu" : {
     	"percent" : 0,
     	"total_in_millis" : 1964850
   	},
   	"mem" : {
     	"total_virtual_in_bytes" : 5035376640
   	}
```

Note that “process.total\_virtual\_in\_bytes” includes the entire memory available to the process, including virtual memory available via mmap.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter