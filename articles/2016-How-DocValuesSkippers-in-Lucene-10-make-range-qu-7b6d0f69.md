---
title: 'How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage'
company: Elastic
tag: 索引构建
date: 2026-06-12
url: https://www.elastic.co/search-labs/blog/docvaluesskippers-lucene-range-queries
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How DocValuesSkippers in Lucene 10 make range queries faster without doubling your storage

DocValuesSkippers add block-level skipping to Lucene DocValues fields, speeding up range queries on sorted or insert-ordered indexes with less than 0.1% storage overhead.

June 12, 2026

[Alan Woodward](/search-labs/author/alan-woodward)

[Lucene](/search-labs/blog/category/lucene)[Index Data](/search-labs/blog/category/index-data)

Jump to

Share

DocValuesSkippers add block-level skipping to Lucene DocValues, making range queries significantly faster on fields that correlate with document insert order or index sort, without duplicating your data into a block k-dimensional (BKD) tree. The skipper index takes up less than 0.1% of the base DocValues field size, adds minimal overhead at index time, and Lucene applies it automatically at query time when available. If your index has a defined sort, or if your timestamps, counters or numeric fields were written roughly in order, enabling skippers can cut the number of documents your range queries need to touch.

## **The problem: DocValues are great for reading, not so much for searching**

Lucene can store numeric values in two ways: DocValues are column-oriented per-document storage which allow fast lookup of the values for individual documents; a [BKD tree](https://en.wikipedia.org/wiki/K-D-B-tree) is an index structure allowing for efficient range searches. DocValues are used for sorting, faceting, and aggregating, but they’re not as useful for searching, as most queries will end up checking every document in the index. Table scans are slow! So, for fast querying and fast aggregation, you need both of these data structures, essentially storing the same data twice.

In many cases, though, there’s an inherent structure to the index, which means that numeric values in a DocValues field correlate roughly with the internal docid [2]; for example, log entries with a timestamp are likely to be added to an index approximately in order, so documents with a lower docid will also have a lower timestamp. And if an index sort is defined on an index, there will be an exact correlation between field values and docid for fields that are part of the sort. A full BKD index is overkill here; what we really want is a data structure that chunks up the column-based storage into blocks and allows queries to efficiently identify if a block can be excluded from the search. Enter the DocValuesSkipper.

## **What is a DocValuesSkipper?**

A DocValuesSkipper is an optional, hierarchical skip index covering a DocValues field, added to [Lucene 10.0](https://github.com/apache/lucene/pull/13449) by Ignacio Vera of Elastic. At write time, you can enable a skipper by setting the DocValuesSkipIndexType on a FieldType or by using one of the `indexedField` sugar methods on XXDocValuesField classes.

The base DocValues field in each index segment [1] is divided into blocks of 4096 documents, with each block recording its min/max docid, the minimum and maximum value found in the block, and the number of documents that it covers (which can be different from maxDoc - minDoc, if some documents have missing values). The hierarchy is then built by merging consecutive intervals, so eight intervals in the base layer are recorded as a single larger interval in layer 1, up to four levels deep. The coarsest level covers approximately 2 million docs per block.

![Diagram showing the DocValuesSkipper hierarchical skip index with four levels of document intervals and a list of stored attributes (minDocID, maxDocID, minValue, maxValue, docCount).](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9ec7a04e3bdbfd9f/6a467b337eb22d59efdfc54d/c07100b6fcc74dba250e6853b1c5ef1edabbedfc-1920x1080.png)

DocValuesSkippers can be enabled for numeric, sorted\_numeric, sorted, and sorted\_set DocValues types. For the latter two types, the values in the skip index are ordinals [3].

## **How do DocValuesSkippers accelerate range queries?**

Lucene can use skippers under the hood to accelerate a number of query-time operations:

* **Range queries** can use a skipper-based block iterator to quickly skip over blocks of documents that fall entirely outside the range of interest. They can also use the skipper to build a two-phase iterator that improves performance when the range query is combined with more expensive queries, such as phrase matches.
* **Sort pruning** can use skippers to exclude blocks from consideration for top-k queries; once enough matching documents have been found to populate the results list, any document with a sort value lower than the bottom document in the list can be skipped.
* **MultiTermQueries**, such as regex or wildcard, can be rewritten as ordinal range queries, and the skipper then used in the same way as for a numeric range query.

## **When to use DocValuesSkippers: correlated fields vs. random data**

If the skipper field is part of (or correlated with) the index sort, the values in the field will cluster by docid, meaning the skip blocks will have tight min/max bounds and large regions of the document space can be excluded from searches.

Conversely, if the values are randomly distributed across documents, every block will span nearly the full value range and nothing can be skipped, so the skipper index will be pure overhead.

| Field characteristic | Skipper effectiveness |
| --- | --- |
| Correlated with index sort | High: tight min/max bounds, large skip regions |
| Insert-order correlated (e.g. timestamps) | High: approximate correlation still benefits |
| Randomly distributed values | Low: blocks span full value range, nothing skipped |
| Part of a defined index sort | Highest: exact value-docID correlation |

Skipper indexes take up very little disk space (typically less than 0.1% of the size of the base DocValues field) but do add some overhead at index and merge time, so they’re best used on fields that have some correlation with the index order.

## **What's next for DocValuesSkippers in Lucene**

There are a number of possible future improvements to DocValuesSkippers in the pipeline, both at index time (improving build time, using skipper metadata to streamline merge operations) and for querying or aggregations (better cardinality estimations, adding more metadata to allow fast sum and average calculations). Watch this space!

## References

[1] **docid:** An integer value that Lucene uses internally to identify individual documents in the index.

[2] **segment:** A Lucene index is divided into a number of immutable index segments, and searches will run over each segment separately (consecutively or concurrently) before combining the results at the end of the process to produce a whole-index result view.

[3] **ordinal:** Term-based DocValues store information in a dual structure: A terms dictionary contains all the term values for the field, each with an associated ordinal number, and then a column-based numeric DocValues field assigns an ordinal to each document. This means that documents can be compared efficiently as the comparison can use the integer ordinal; the original term can be retrieved by looking up the ordinal in the terms dictionary.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5d70b25967c2194e/6a17d732b1e11383f879f0ca/13c3c0053e2968fb835ba2f90f34bec3a011b5c0-880x592.webp)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)

### Elasticsearch vs. OpenSearch: Vector Search Performance Comparison

June 26, 2024|[Ugo Sangiorgi](/search-labs/author/ugo-sangiorgi)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt762b38f91bd71c8e/6a170db8b339d547bb76a048/368db71c500e72d20fe225fe44c2c40231e29765-721x420.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Bringing maximum-inner-product into Lucene

September 01, 2023|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf9fcbf843affc566/6a1706b8964ceaea3208bab9/7884e35f40c15fe349379ef7ae4648b21708962f-1070x712.jpg)

[Lucene](/search-labs/blog/category/lucene)

### Concurrency bugs in Lucene: How to fix optimistic concurrency failures

February 07, 2025|[Benjamin Trent](/search-labs/author/benjamin-trent)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt0cccbdeaa4571db2/6a17057dc1e8a52e10f881e0/2fff360ef055df5980c696adffeb49f4b125a268-1913x1182.png)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[ML Research](/search-labs/blog/category/ml-research)

### Better Binary Quantization (BBQ) vs. Product Quantization

November 18, 2024|[Benjamin Trent](/search-labs/author/benjamin-trent)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blteae4d50ff68aee45/6a17052114b270ecdde3c52d/119d3db739fcef08ffcb976e6d9d3bb0c204fb1f-1300x700.png)

[Lucene](/search-labs/blog/category/lucene)

### What happened in Lucene land in 2023?

January 12, 2024|[Adrien Grand](/search-labs/author/adrien-grand)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter