---
title: 'Tripling the query performance of lexical search'
company: Vespa
tag: 工程相关
date: 2025-03-27
url: https://blog.vespa.ai/tripling-the-query-performance-of-lexical-search/
account: 
origin: harvest3-202607
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Geir Storli](/assets/avatars/geirst.jpg)

[Geir Storli](/authors/geirst/ "Geir Storli")
  
Senior Principal Vespa Engineer

![Tor Brede Vekterli](/assets/avatars/vekterli.jpg)

[Tor Brede Vekterli](/authors/vekterli/ "Tor Brede Vekterli")
  
Senior Principal Vespa Engineer

27 Mar 2025

# Tripling the query performance of lexical search

![](/assets/2025-03-27-tripling-the-query-performance-of-lexical-search/emil-widlund-xrbbXIXAWY0-unsplash-crop.jpg)

Photo by [Emil Widlund](https://unsplash.com/@emilwidlund)
on [Unsplash](https://unsplash.com/photos/photo-of-brown-wooden-bookshelf-xrbbXIXAWY0)

Despite AI-powered searching having changed how much of the world’s information is discovered and accessed, classical
information retrieval techniques are still highly relevant—especially when the strengths of the two approaches are
combined.

Large text indexes, for e.g., [RAG searching](https://docs.vespa.ai/en/llms-rag.html) may have billions of documents
stored across many terabytes of data. Searching through such a number of documents in mere milliseconds puts a lot of
pressure on finite disk, memory, and CPU resources, and optimizations that reduce the load are therefore very welcome.

We have added several tunable query-time optimizations to Vespa that in our experiments *triple* the performance of
natural language text search on average when used together. This happens with only a marginal expected loss of query
result quality.

The optimizations are described in greater detail below, but at a high level:

1. Reduce the required precision for very common words, greatly reducing disk reading and memory caching overhead.
2. Automatically filter out very common words based on statistics in the indexed data.
3. Greatly reduce the number of internal result candidates, in turn reducing ranking costs.

These optimization parameters are available in Vespa version 8.503.27 and beyond.

## Background

Until recent years, searching has primarily been the domain of *words*. Words in a query are matched against words in an
*index*, often exactly. This is known as *lexical search*. However, human language is full of ambiguities—different
words may mean the same thing, and similar words may mean completely different things depending on the context.

In an attempt to work around the nuances of language, techniques such as
[stemming](https://en.wikipedia.org/wiki/Stemming) and query expansion
are used to let a query match documents that use different words but where the *semantics* are (hopefully)
the same. We generally refer to the words that end up being part of the final index or query as *“terms”*. It is crucial
that any process that modifies terms—such as stemming—is performed identically (and always) both when indexing and
querying, or the terms will not match between the two.

Today, more and more searching happens in high-dimensional vector space through the use of *embeddings*.
Embeddings intend to capture *semantics*, independently of the exact words used to represent them.
The closer two pieces of text are in meaning, the closer their embeddings should be in high-dimensional space.
Embeddings are typically created with pre-trained transformer-based language models, and indexed and queried
using [approximate nearest neighbor](https://docs.vespa.ai/en/approximate-nn-hnsw.html) data structures.

Since embedding models are trained using machine learning, the more common a concept is (and therefore more frequently
occurring in the training data), the more likely it is to be represented well by embeddings.
This is conceptually—and perhaps paradoxically—the inverse of how we consider relevance for lexical search, where
uncommon terms are treated as more relevant for the query. One example is searching for someone with a rare name living
in New York. The concept of living in New York is likely well represented in the embedding vector space, but the person
with the rare name is not. Conversely, for lexical search, the term `living` is so common that it might not even be
considered when evaluating the query, but the terms making up the name will be considered highly relevant.

The pragmatic solution for this problem is *hybrid search* which combines the best of both worlds—vector search for
semantics and lexical search for specifics.

Vespa offers rich out-of-the-box support for hybrid search, see
our [Hybrid Text Search Tutorial](https://docs.vespa.ai/en/tutorials/hybrid-search.html) as a starting point.

In this blog post, we will cover the lexical search part of hybrid search.

## Challenges

Lexical search uses an inverted index that maps each term to all the documents that contain the term. To enable phrase
[matching](https://docs.vespa.ai/en/text-matching.html) and proximity-based
[ranking](https://docs.vespa.ai/en/ranking.html),
this index frequently includes every position a term occurs in each document. This mapping is known as a *posting list*.

The distribution of word frequencies in a natural language is not uniform—some words are vastly more common than
others (see [Zipf’s law](https://en.wikipedia.org/wiki/Zipf%27s_law#Word_frequencies_in_natural_languages)).
For an arbitrary English text, consider how often the words “the”, “a”, “of” etc. occurs at least once in the text
compared to a word such as “Zoidberg”. We refer to this as the word’s *document frequency*. I.e. a word that occurs
at least once in 42% of all documents in the corpus has a document frequency of 42%.

Example of word document frequencies extracted from the English Wikipedia corpus:

| Word | Frequency |
| --- | --- |
| the | 99.8937% |
| in | 99.0566% |
| and | 98.5016% |
| of | 98.3955% |
| a | 97.5289% |
| to | 92.2856% |
| was | 87.9532% |
| (…) |  |
| may | 27.2400% |
| made | 27.1815% |
| (…) |  |
| living | 6.6859% |
| mid | 6.6797% |
| (…) |  |
| puns | 0.0415% |
| seinfeld | 0.0415% |
| (…) |  |
| zoidberg | 0.0014% |
| (…) |  |

Very common words are often referred to as *[“stopwords”](https://en.wikipedia.org/wiki/Stop_word)* in an
information retrieval setting. A classic strategy is explicitly removing stopwords during indexing and/or querying,
but this needs a curated list and is inherently language-specific.

When not removed, stopwords have disproportionately massive posting lists. This is because they are present in most
documents and are present many times *within* each document. These posting lists take up a lot of space, both on disk and
in memory caches.

Since natural language queries are increasingly becoming the norm, such queries will also include many stopwords.
Evaluating a query with many stopwords may require reading much data from large posting lists on disk.

From a query evaluation perspective, we are faced with a paradox: the least important terms are by far the most
expensive to evaluate.

Aside from the size of posting lists, another fundamental performance challenge is controlling how many documents we end
up *ranking* as part of queries. Ranking cost is generally linear in the number of candidate documents, so if we want
our queries to efficiently reach hundreds of millions—or billions—of documents, we can’t afford to rank a large
percentage of these every time.

Ranking documents involves running a series of algorithms and mathematical formulas to compute a score per candidate
document, which attempts to capture how relevant the document is for the query. One of the most popular ranking
algorithms is [BM25](https://docs.vespa.ai/en/reference/bm25.html), which uses information on how frequent query terms
occur within—and across—documents to compute a relevance score. Vespa allows for arbitrarily sophisticated user-supplied
ranking formulas, often built around foundational functions such as BM25.

For any query with multiple terms, a choice must always be made whether we require *all* (or a subset) of the terms
to be present in a candidate document or just *some* of the terms. These choices are represented by logical `AND` and
`OR` operators, respectively.

Intuitively, using `AND` will produce fewer hits than `OR`. However, `AND` risks finding too few *relevant* hits since
it’s not a given that all relevant documents contain *all* query terms. Using `OR` will find all relevant hits, but the
presence of stopwords will cause the number of candidate hits to be very large, in turn causing ranking to be excessively
expensive.

Ideally, we would like to strike a balance between the two. Luckily, Vespa’s built-in
[weakAnd](https://docs.vespa.ai/en/using-wand-with-vespa.html#weakand) query operator allows us to do just that.
Conceptually, *weakAnd* starts as an `OR` search, then becomes more and more `AND`-like as increasingly relevant
hits are added. Documents can be quickly rejected as possible candidate hits based on whether their internal scores
pass the dynamic *weakAnd* threshold. The *weakAnd*-internal scoring is a fixed, linear BM25-like function that only
considers whether a term is present in a document, i.e., no frequency or position information from documents is used.
This is a much simpler function than the arbitrary (potentially expensive) user-supplied ranking expression. Still, this
restriction is a requirement for the early-out filtering algorithm to work as designed.

The performance of a query using *weakAnd* benefits greatly from making ranking more efficient and reducing the number
of hits produced. In the next section, we will examine how the optimization parameters we recently added to Vespa help
achieve this.

## What we did

Based on the above challenges, we have focused on three areas of improvement for lexical search:

### Use more compact posting lists for common terms

One observation is that since common terms occur frequently in the text, their position relative to other terms may not
be of high relevance, especially when paired with semantic search. However, the presence or absence of a common term may
still be a useful signal, especially as a tie-breaker.

We have introduced a
new [`filter-threshold`](https://docs.vespa.ai/en/reference/schema-reference.html#rank-filter-threshold) parameter that
allows common terms to be handled at query time using a bit vector instead of an explicit posting list. For common
terms, only a single bit of information is exposed to the ranking framework; does the document contain the term or not?
This also explains the parameter name—common terms are reduced to behaving as a binary *filter*. This makes ranking
similar to how scoring is done internally in the *weakAnd* operator.

The definition of “common” depends on the parameter value; it is a normalized document frequency in the range [0, 1].
Example: `filter-threshold: 0.05` means that all terms that occur in at least 5% of all documents in the corpus will
be considered common and will use bit vectors instead of posting lists.

### Avoid using large posting lists altogether

The `filter-threshold` parameter greatly reduces the overhead of common terms. But as with many things in life, doing
*nothing* is even faster than doing *just a little bit*.

We have introduced a
new [`stopword-limit`](https://docs.vespa.ai/en/reference/schema-reference.html#weakand-stopword-limit) parameter to use
when the *weakAnd* operator doesn’t need any signals for whether a word exists in a document. Terms that occur more
frequently across documents than the stopword limit will be ignored completely.
As with `filter-threshold`, this uses a normalized document frequency value; e.g., `stopword-limit: 0.6` means ignore all
words that occur in at least 60% of all documents.

Stopwords are not considered part of ranking—it is as if they were removed from the query before being passed to
Vespa, but without the need to maintain stopword lists.

### Reduce the number of hits produced by weakAnd

The previous two methods make evaluating documents containing common terms much cheaper. But we still produce
approximately the same number of hits as we did before, and as mentioned previously, ranking cost is close to linear in
the number of candidate hits.

We have introduced a
new [`adjust-target`](https://docs.vespa.ai/en/reference/schema-reference.html#weakand-adjust-target) parameter, which
dynamically lets the *weakAnd* operator reduce the number of produced hits by excluding documents that *only* contain
common terms in common with the query. As with `filter-threshold` and `stopword-limit`, it is specified as a normalized
document frequency.

`adjust-target` enforces a lower limit on the internal *weakAnd* score a document can have before it can even be
considered a potential hit. The internal score of a document is the sum of the inverse document frequency contributions
of its matching query terms. The minimum score limit is dynamically determined per query to be equal to the score of
the query term whose document frequency is closest to the configured value.

Example: given the query `"where to look at moose in Norway?"` an `adjust-target` value set lower than the document
frequency of the terms `to`, `at`, `where` and `in` would exclude documents that only match one or a few of those terms,
as their score would be too low.

These parameters can be used alone or in any combination, depending on what tradeoffs make sense for your application.
They can be set in a [rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) or
[overridden per query](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching).

Bear in mind that the “no free lunch” principle applies—*reducing* the number of signals available for ranking cannot
*increase* overall search quality. Measure search quality with and without these parameters to learn what optimizations
make sense for your particular use case.

## Experiments

We conducted a set of experiments to test how the new tuning parameters affected the quality and query performance
of lexical search. We wanted to establish a baseline that would improve query performance without significantly impacting quality.

### Quality

To test the effect on quality, we used three datasets from
the [BEIR benchmark](https://github.com/beir-cellar/beir/wiki), which is widely used for evaluating information
retrieval models. These datasets were used:

* [TREC-COVID](https://ir.nist.gov/covidSubmit/index.html)
* [NFCorpus](https://www.cl.uni-heidelberg.de/statnlpgroup/nfcorpus/)
* [MS MARCO](https://microsoft.github.io/msmarco/)

For each dataset, we used the [schema](https://docs.vespa.ai/en/schemas.html) below
with [BM25](https://docs.vespa.ai/en/reference/bm25.html) as the baseline ranking function.
Then, for each of the three tuning parameters, we added extra rank profiles to test a range of values for a given parameter:

* *weakAnd* `stopword-limit`: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
* *weakAnd* `adjust-target`: [0.0001, 0.001, 0.01, 0.02, 0.05]
* `filter-threshold`: [0, 0.01, 0.05, 0.10, 0.20]

```
schema doc {
    document doc {
        field title type string {
            indexing: summary | index
            index: enable-bm25
        }
        field text type string {
            indexing: index
            index: enable-bm25
        }
    }
    rank-profile baseline inherits default {
        first-phase {
            expression: bm25(title) + bm25(text)
        }
    }
}
```

The following table shows the results of the quality test. By comparing
the [nDCG@10](https://github.com/beir-cellar/beir/wiki/Metrics-available) scores, we observe when a given parameter
starts to have a negative effect on quality.

| Parameter | Value | TREC-COVID   nDCG@10 | NFCorpus   nDCG@10 | MS MARCO   nDCG@10 |
| --- | --- | --- | --- | --- |
| baseline |  | 0.6518 | 0.3429 | 0.2285 |
| stopword-limit | 0.8 | 0.6531 | 0.343 | 0.2286 |
| stopword-limit | 0.7 | 0.6512 | 0.3432 | 0.2286 |
| stopword-limit | 0.6 | 0.6512 | 0.3424 | 0.2283 |
| stopword-limit | 0.5 | 0.616 | 0.3426 | 0.2259 |
| stopword-limit | 0.4 | 0.5533 | 0.3424 | 0.2259 |
| stopword-limit | 0.3 | 0.5552 | 0.3408 | 0.226 |
| stopword-limit | 0.2 | 0.5125 | 0.3411 | 0.2258 |
| stopword-limit | 0.1 | 0.4526 | 0.3319 | 0.2251 |
| adjust-target | 0.05 | 0.6518 | 0.3423 | 0.2285 |
| adjust-target | 0.02 | 0.6518 | 0.3409 | 0.2285 |
| adjust-target | 0.01 | 0.6518 | 0.3422 | 0.2286 |
| adjust-target | 0.001 | 0.6518 | 0.3363 | 0.2289 |
| adjust-target | 0.0001 | 0.6518 | 0.3397 | 0.2291 |
| filter-threshold | 0.2 | 0.6518 | 0.3429 | 0.2283 |
| filter-threshold | 0.1 | 0.6518 | 0.3429 | 0.2286 |
| filter-threshold | 0.05 | 0.6518 | 0.3429 | 0.2296 |
| filter-threshold | 0.01 | 0.6518 | 0.3429 | 0.2232 |
| filter-threshold | 0 | 0.6518 | 0.3429 | 0.1736 |
| optimized |  | 0.6512 | 0.3423 | 0.2296 |

For *weakAnd* `stopword-limit`, we see a noticeable change in nDCG@10 score between 0.5 and 0.6 for the TREC-COVID dataset.
The other datasets are less impacted. For *weakAnd* `adjust-target`, the changes in quality are less prominent. Between 0.001
and 0.01, we see a small change for the NFCorpus dataset. For `filter-threshold`, the quality changes are also less
prominent. For the MS MARCO dataset, we see a slight change between 0.01 and 0.05.

For each parameter, we selected the value where the quality impact was negligible and summarized them into an *optimized* rank
profile as seen below. As we will see in the next section, this combination of parameters positively impacts query
performance.

```
rank-profile optimized inherits baseline {
    filter-threshold: 0.05
    weakand {
      stopword-limit: 0.6
      adjust-target: 0.01
    }
  }
}
```

### Performance

To explore query performance, we used a [Wikipedia dataset](https://dumps.wikimedia.org/backup-index.html) with 13.6M
articles and the [SQuAD](https://www.kaggle.com/datasets/stanfordu/stanford-question-answering-dataset)
question-answering dataset. We used a schema similar to the one above. An attribute field was added to simulate
in-memory metadata per article. The exact application package is
found [here](https://github.com/vespa-engine/system-test/blob/master/tests/performance/mmap_vs_directio/app/).

We deployed the application on [Vespa Cloud](https://cloud.vespa.ai/). The machine used for the single content node was
an AWS c6id.2xlarge instance on with:

* 8 vCPUs
* 16 GiB memory
* 474 GiB of NVMe SSD storage
* IO capacity: 134,167 IOPS (536,668 KiB/s)

This instance was selected so that the size of the disk index (containing the *title* and *text* fields) would not fit in
physical memory. This is also typical in a production scenario.
After feeding the article dataset, this was the state of the content node:

* Memory usage in steady state: 7.3 GiB (60% of total 12.1 GiB allocated to Vespa)
* Total disk index size: 23.8 GiB
* Total memory headroom: 4.8 GiB (which is only 20% of the disk index size)

Vespa reads disk index files via virtual memory mappings, where the contents of a file can be accessed as if reading a
regular memory buffer. When running query load on the system, the Linux kernel transparently loads parts of the files
into physical memory based on where reading is taking place in the mapped range. The kernel can also transparently
unload parts of the files from physical memory depending on the memory pressure on the host. Using virtual memory
simplifies memory management since caching decisions are deferred to the kernel.

The kernel can be provided with hints on how to handle the mapped memory using the `madvise` system call. We have
experimented with the following hints:

* **NORMAL** - Default behavior. Assumes that data is accessed in “clusters” and therefore performs both read-behind and
  read-ahead around the accessed address.
* **SEQUENTIAL** - Assumes data is accessed sequentially and only performs read-ahead. This is a good fit for disk
  index posting list files.

The tool [vespa-fbench](https://docs.vespa.ai/en/performance/vespa-benchmarking.html#vespa-fbench) was used to perform
query benchmarking. We used two different rank profiles (*baseline* and *optimized*), different number of query clients ([1, 2, 4, 8]),
and `madvise` settings ([`NORMAL`, `SEQUENTIAL`]). Each benchmark was executed for 10 minutes. Between
each run, we cleared the Linux pagecache and restarted the content node processes. These metrics were sampled:

* **Average latency** - The average latency in milliseconds among all query requests, measured by vespa-fbench.
* **99 percentile latency** - The maximum latency in milliseconds experienced by 99% of all query requests, with only 1% of
  requests taking longer.
* **QPS** - The average number of queries per second handled, measured among all query requests.
* **CPU cores** - The average number of CPU cores used to handle the content node’s query workload (max 8.0). This
  also includes CPU time spent waiting for I/O.
* **I/O read** - The amount of data read from disk (KiB/s) on the content node while handling the query workload.
* **QPS per CPU core** - The result of dividing QPS by CPU cores and shows the system’s effectiveness while handling the
  query workload.
* **QPS per CPU core ratio** - The ratio between QPS per CPU core for a given run and the same run with *baseline* ranking and
  `madvise` `NORMAL`. This shows the raw performance improvement.

The following table summarizes the results:

| MMAP madvice | Ranking | Clients | Average latency (ms) | 99 percentile latency (ms) | QPS | CPU cores | I/O read (KiB/s) | QPS per CPU core | QPS per CPU core ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| normal | baseline | 1 | 164.6 | 1205.4 | 6.1 | 1.01 | 17500 | 6.01 | 1 |
| normal | baseline | 2 | 106.5 | 547.1 | 18.8 | 1.89 | 42000 | 9.96 | 1 |
| normal | baseline | 4 | 76.7 | 335.6 | 52.1 | 3.78 | 95000 | 13.8 | 1 |
| normal | baseline | 8 | 68.1 | 299.9 | 117.5 | 6.95 | 210000 | 16.9 | 1 |
| normal | optimized | 1 | 60.6 | 443 | 16.5 | 1.11 | 17500 | 14.88 | 2.5 |
| normal | optimized | 2 | 40.4 | 248 | 49.6 | 1.94 | 45000 | 25.55 | 2.6 |
| normal | optimized | 4 | 32.9 | 143.3 | 121.7 | 3.63 | 75000 | 33.5 | 2.4 |
| normal | optimized | 8 | 29.9 | 121.8 | 267.8 | 6.74 | 140000 | 39.71 | 2.3 |
| sequential | baseline | 1 | 30.2 | 142 | 33.1 | 0.95 | 170000 | 34.97 | 5.8 |
| sequential | baseline | 2 | 31.2 | 139.7 | 64.1 | 1.88 | 340000 | 34.05 | 3.4 |
| sequential | baseline | 4 | 40.9 | 174.9 | 97.8 | 3.9 | 615000 | 25.06 | 1.8 |
| sequential | baseline | 8 | 83.3 | 300.3 | 96 | 6.95 | 615000 | 13.81 | 0.8 |
| sequential | optimized | 1 | 16.2 | 58 | 61.7 | 0.94 | 85000 | 65.93 | 11 |
| sequential | optimized | 2 | 16.6 | 61 | 120.7 | 1.79 | 185000 | 67.43 | 6.8 |
| sequential | optimized | 4 | 17.6 | 68.5 | 227.2 | 3.56 | 360000 | 63.76 | 4.6 |
| sequential | optimized | 8 | 23.9 | 88.9 | 335.3 | 6.82 | 615000 | 49.19 | 2.9 |

Let’s first focus on the results with `madvise` `NORMAL`. We see an improvement of around 2.5x when using the *optimized*
rank profile compared to *baseline*. In both cases, a large portion of CPU time was spent waiting for I/O,
and the gain is significant because of the reduction in the amount of data read from posting lists.
This is mainly achieved by using the `filter-threshold` tuning parameter.

When using `madvise` `SEQUENTIAL`, we see even more significant improvements. First, with *baseline* rank profile, the improvement is up
to 5x compared to `madvise` `NORMAL` with low query load (1-2 clients). With the `SEQUENTIAL` setting the I/O sub-system is better
utilized, such that less CPU time is spent waiting for I/O, and more on matching and ranking.
However, the performance is a bit weaker when the system is fully utilized (with 8 clients).
An additional observation is that the 99 percentile latencies are significantly reduced, and the overall performance is more stable.

The largest improvement is achieved using `madvise` `SEQUENTIAL` and the *optimized* rank profile. This results in a
3-11x improvement compared to the starting point. Both the average and 99 percentile latencies are also very stable
across the runs, and the QPS is gradually increased when adding more clients. This combination of settings results in a
stable and predictable performance.

Note that the performance results were observed on a system that was limited on physical memory, and where a significant
amount of disk index posting lists files are mapped in and out of memory. With more available memory, the performance
gains are most likely reduced. Still, up to 2x improvements are expected.

Also note the unusual latency results with `madvise` `NORMAL` and the *baseline* rank profile.
Normally, latencies increase when adding more load to the system with more clients.
However, in this case we observe the opposite.
The main reason seems to be that the I/O sub-system is not properly utilized when the load is low.
With 1 client, ~17500 KiB/s was read from disk. With 8 clients, ~210000 KiB/s was read from disk.
The difference in I/O is 12x, while the difference in load is 8x. This indicates the I/O sub-system was
50% more efficient when handling the highest load.
In addition, 19x more queries were executed with 8 clients compared to 1 client during the 10 minutes of benchmarking.
This means high latencies during the first minute (to warmup the I/O sub-system) have less impact for 8 clients.

## Summary

In this blog post, we have seen how introducing new tuning parameters triples the query performance of
lexical search. By using a combination of these parameters, less data is read from disk index posting lists, while the
*weakAnd* query operator produces fewer hits. All without any significant impact on quality.
In addition, the MMAP `madvise` setting for disk index posting list files is changed to `SEQUENTIAL`,
significantly improving 99 percentile query latencies with better utilization of the I/O sub-system.
The effect for customers are reduced hardware costs, lower query latencies, or a combination of both.
All of this is available in Vespa 8.503.27.

## Read more

[![Elasticsearch vs Vespa Performance Comparison](/assets/2024-11-06-elasticsearch-vs-vespa-performance-comparison/overall_perf.png)](/elasticsearch-vs-vespa-performance-comparison/)
[## Elasticsearch vs Vespa Performance Comparison

#### Detailed report of a comprehensive performance comparison between Vespa and Elasticsearch for an e-commerce search application.](/elasticsearch-vs-vespa-performance-comparison/)

[![Redefining Hybrid Search Possibilities with Vespa - part one](/assets/2024-01-19-redefining-hybrid-search-possibilities-with-vespa/trent-erwin-UgA3Xvi3SkA-unsplash.jpg)

Photo by [Trent Erwin](https://unsplash.com/@tjerwin?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash) on [Unsplash](https://unsplash.com/photos/black-framed-eyeglasses-and-black-pen-UgA3Xvi3SkA?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)](/redefining-hybrid-search-possibilities-with-vespa/)
[## Redefining Hybrid Search Possibilities with Vespa - part one

#### This is the first blog post in a series on hybrid search. This first post focuses on efficient hybrid retrieval and representational approaches in IR](/redefining-hybrid-search-possibilities-with-vespa/)

[![](/assets/logo/vespa-logo.svg)

## Vespa Performance

#### Sizing, performance, and benchmarking with Vespa](https://docs.vespa.ai/en/performance/ )

[« Modernize your retrieval pipeline with ModernBERT and Vespa](/modernized-retrieval-modernbert-vespa/)
[Introducing Vespa Voice — Your Signal for What’s Next in AI-Driven Search Infrastructure »](/introducing-vespa-voice-your-signal-for-whats-next-in-ai-driven-search-infrastructure/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)