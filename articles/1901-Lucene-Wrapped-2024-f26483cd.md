---
title: 'Lucene Wrapped 2024'
company: Elastic
tag: 工程相关
date: 2025-01-03
url: https://www.elastic.co/search-labs/blog/apache-lucene-wrapped-2024
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Lucene Wrapped 2024

2024 has been another major year for Apache Lucene. In this blog, we’ll explore the key highlights.

January 03, 2025

[Chris Hegarty](/search-labs/author/chris-hegarty)

[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

Apache Lucene has seen significant activity in 2024, with numerous releases including the first major update in three years, packed with exciting improvements and new features. Let’s explore some of the key highlights.

## Lucene & the community

A project is only as strong as the community that supports it. Despite more than 20 years of development, the Lucene project remains vibrant and thrives thanks to its passionate and active contributors.

In 2024, the Lucene project has seen more than 2,000 commits from 98 unique contributors, and almost 800 pull requests. The number of contributors continues to grow, with new committers and PMC members joining the project and helping drive its success.

## Lucene 10

2024 saw the first major release in almost 3 years - Lucene 10, with more than 2,000 commits from 185 unique contributors. While the development model that Lucene follows allows to deliver many improvements and features in minor releases, a major release affords the opportunity to bring larger features and modernizations. For example, Lucene 10 requires a minimum of Java 21. Bumping the minimum Java version ensures that Lucene can continue to take advantage of improvements that modern Java provides.

The primary focus of Lucene 10 is to better utilize the hardware on which it runs. Let's take a quick look at some of the main highlights:

* **More search parallelism** - while search execution is already parallelized across segments, we now go further, parallelizing within segments. This decouples on-disk representation from the execution performance, allowing even single segments to benefit from the number of cores on modern systems.
* **Better I/O parallelism** - the straightforward synchronous I/O model that Lucene uses has been enhanced with a prefetch stage. This informs the OS that a region of an index file will be needed in the very near future, while not blocking the calling thread.
* **Better CPU and storage efficiency with sparse indexing** - Lucene 10 introduces support for sparse indexing, sometimes called primary-key indexing or zone indexing in other data stores.

For more information about Lucene 10, check out the dedicated [article](https://www.elastic.co/search-labs/blog/apache-lucene-10-release-highlights) on Lucene 10.

## Lucene research and innovation

In 2024, Lucene has seen a surge of research and innovation, particularly in the areas of machine learning integration, vector search, and optimization for large-scale datasets, with reference form 10 separate [research papers and publications](https://scholar.google.com/scholar?as_ylo=2024&q=lucene&hl=en&as_sdt=0,5). Some of the key research areas and developments include:

* **Vector Search and Embedding Support** - Lucene provides a powerful and scalable solution for vector-based search, enabling semantic retrieval at scale. By leveraging Lucene's robust indexing and search infrastructure, users can combine the best of traditional text search with the advanced capabilities of modern vector search, making Lucene a comprehensive solution for a wide range of search and information retrieval tasks.
* **Hybrid Search Models** - Research has also delved into hybrid search techniques, where Lucene combines traditional keyword-based search with modern vector-based retrieval. By merging term-based indexes with dense vector representations, Lucene can deliver more accurate and contextually relevant search results, bridging the gap between the precision of traditional search engines and the flexibility of semantic search.

The ongoing research efforts in 2024 demonstrate Lucene’s adaptability to the evolving needs of modern search technologies, particularly in the context of AI, semantic search, and big data applications. The project continues to grow as a powerful, flexible, and efficient platform for both traditional and cutting-edge search use cases.

## 2024 Lucene releases

Although not an exact reflection, the sheer volume of releases highlights the ongoing dedication and energy of the community. These updates include major enhancements to vector search performance and efficiency, support for madvise, optimizations for postings list decoding, further speed improvements through SIMD, and much more.

Here’s the full list of releases:

* [10.1.0](https://lucene.apache.org/core/corenews.html#apache-lucenetm-1010-available) (2024-12-20)
* [9.12.1](https://lucene.apache.org/core/corenews.html#apache-lucenetm-9121-available) (2024-12-13)
* [10.0.0](https://lucene.apache.org/core/corenews.html#apache-lucenetm-1000-available) (2024-10-14)
* [9.12.0](https://lucene.apache.org/core/corenews.html#apache-lucenetm-9120-available) (2024-09-28)
* [8.11.4](https://lucene.apache.org/core/corenews.html#apache-lucenetm-8114-available) (2024-09-24)
* [9.11.1](https://lucene.apache.org/core/corenews.html#apache-lucenetm-9111-available) (2024-06-27)
* [9.11.0](https://lucene.apache.org/core/corenews.html#apache-lucenetm-9110-available) (2024-06-06)
* [9.10.0](https://lucene.apache.org/core/corenews.html#apache-lucenetm-9100-available) (2024-02-20)
* [8.11.3](https://lucene.apache.org/core/corenews.html#apache-lucenetm-8113-available) (2024-02-08)
* [9.9.2](https://lucene.apache.org/core/corenews.html#apache-lucenetm-992-available) (2024-01-29)

You can find more information and release notes at the [Lucene Core](https://projects.apache.org/project.html?lucene-core) page. Additionally, there are equivalent [PyLucene](https://projects.apache.org/project.html?lucene-pylucene) releases.

## Wrapping up

As Lucene matures, it continues to flourish thanks to its dedicated and vibrant community. As we’ve seen, 2024 has been an incredibly productive year, and we now look ahead to the exciting developments that 2025 will bring.

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