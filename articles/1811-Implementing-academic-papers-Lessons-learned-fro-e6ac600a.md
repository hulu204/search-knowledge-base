---
title: 'Implementing academic papers: Lessons learned from Elasticsearch and Lucene'
company: Elastic
tag: 工程相关
date: 2021-09-29
url: https://www.elastic.co/search-labs/blog/implementing-academic-papers-lessons-learned-from-elasticsearch-and-lucene
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Implementing academic papers: Lessons learned from Elasticsearch and Lucene

Discover strategies for incorporating research papers in a software application, drawing our experiences with Elasticsearch and Lucene.

September 29, 2021

[Julie Tibshirani](/search-labs/author/julie-tibshirani)

[ML Research](/search-labs/blog/category/ml-research)[Lucene](/search-labs/blog/category/lucene)

Jump to

Share

This post shares strategies for implementing academic papers in a software application. It draws on examples from Elasticsearch and Lucene in hopes of helping other engineers learn from our experiences. You might read these strategies and think “but this is just software development!” And that would indeed be true: as engineers we already have the right practices and tools, they just need to be adapted to a new challenge.

## Background

While developing Elasticsearch, we occasionally come across an important problem with no simple or established approach to solving it. It's natural to ask “hmm, is there an academic paper that addresses this?” Other times, academic work is a source of inspiration. We'll encounter a paper proposing a new algorithm or data structure and think “this would be so useful!” Here are just a few examples of how Elasticsearch and Apache Lucene incorporate academic work:

* [HyperLogLog++](https://research.google/pubs/pub40671/) for [cardinality aggregations](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/search-aggregations-metrics-cardinality-aggregation.html)
* [C3 algorithm](https://www.usenix.org/system/files/conference/nsdi15/nsdi15-paper-suresh.pdf) for [adaptive replica selection](https://www.elastic.co/blog/improving-response-latency-in-elasticsearch-with-adaptive-replica-selection)
* [Hierarchical Navigable Small World Graphs (HNSW)](https://arxiv.org/abs/1603.09320) for nearest vector search in Lucene
* [MIC statistic](https://jmlr.csail.mit.edu/papers/volume17/15-308/15-308.pdf) to [improve machine learning classification](https://github.com/elastic/ml-cpp/pull/488)
* [Block-max WAND](http://engineering.nyu.edu/~suel/papers/bmw.pdf) for [faster top-hits retrieval in Lucene](https://www.elastic.co/blog/faster-retrieval-of-top-hits-in-elasticsearch-with-block-max-wand)
* ... and [many](https://www.elastic.co/guide/en/elasticsearch/reference/7.15/query-dsl-combined-fields-query.html) [more](https://github.com/elastic/elasticsearch/blob/b2a9328890b23e7ccf6c66a3b13d6d65e453a3dd/server/src/main/java/org/elasticsearch/search/sort/BucketedSort.java#L302-L323)

Academic papers are an invaluable resource for engineers developing data-intensive systems. But implementing them can be intimidating and error-prone — algorithm descriptions are often complex, with important practical details omitted. And testing is a real challenge: for example, how can we thoroughly test a machine learning algorithm whose output depends closely on the dataset?

## Evaluate the paper as you would a software dependency

Adding a new software dependency requires careful evaluation: if the other package is incorrect, slow, or insecure, our project could be too. Before pulling in a dependency, developers make sure to evaluate its quality.

The same applies to academic papers you're considering implementing. It may seem that because an algorithm was published in a paper, it must be correct and perform well. But even though it passed a review process, an academic paper can have issues. Maybe the correctness proof relies on assumptions that aren't realistic. Or perhaps the “experiments” section shows much better performance than the baseline, but this only holds on a specific dataset. Even if the paper is of great quality, its approach may not be a good fit for your project.

When thinking about whether to take a “dependency” on an academic paper, it's helpful to ask the same questions we would of a software package:

* Is the library widely-used and “battle tested”? → Have other packages implemented this paper, and has it worked well for them?
* Are performance benchmarks available? Do these seem accurate and fair? → Does the paper include realistic experiments? Are they well designed?
* Is a performance improvement big enough to justify the complexity? → Does the paper compare to a strong baseline approach? How much does it outperform this baseline?
* Will the approach integrate well with our system? → Do the algorithm's assumptions and trade-offs fit our use case?

Somehow when a software package publishes a performance comparison against their competitors, the package always comes out fastest! If a third party designed the benchmarks, they may be more balanced. The same phenomenon applies to academic papers. If an algorithm performs well not only in the original paper, but also appears in other papers as a strong baseline, then it is very likely to be solid.

## Get creative with testing

Algorithms from academic papers often have more sophisticated behavior than the types of algorithms we routinely encounter. Perhaps it's an approximation algorithm that trades off accuracy for better speed. Or maybe it's a machine learning method that takes in a large dataset, and produces (sometimes unexpected) outputs. How can we write tests for these algorithms if we can't characterize their behavior in a simple way?

### Focus on invariants

When designing unit tests, it's common to think in terms of examples: if we give the algorithm this example input, it should have that output. Unfortunately for most mathematical algorithms, example-based testing doesn't sufficiently cover their behavior.

Let's consider the C3 algorithm, which Elasticsearch uses to figure out what node should handle a search request. It ranks each node using a nuanced formula that incorporates the node's previous service and response times, and its queue size. Testing a couple examples doesn't really verify we understood the formula correctly. It helps to step back and think about testing invariants: if service time increases, does the node's rank decrease? If the queue size is 0, is the rank determined by response time, as the paper claims?

Focusing on invariants can help in a number of common cases:

* Is the method supposed to be order-agnostic? If so, passing the input data in a different order should result in the same output.
* Does some step in the algorithm produce class probabilities? If so, these probabilities should sum to 1.
* Is the function symmetric around the origin? If so, flipping the sign of the input should simply flip the sign of the output.

When we first implemented C3, we had a bug in the formula where we accidentally used the inverse of response time in place of response time. This meant slower nodes could be ranked higher! When fixing the issue, we [made sure to add invariant checks](https://github.com/elastic/elasticsearch/pull/70283) to guard against future mistakes.

### Compare to a reference implementation

Alongside the paper, the authors hopefully published an implementation of the algorithm. (This is especially likely if the paper contains experiments, as many journals require authors to post code for reproducing the results.) You can test your approach against this reference implementation to make sure you haven't missed important details of the algorithm.

While developing Lucene's HNSW implementation for nearest-neighbor search, we [tested against a reference library](https://issues.apache.org/jira/browse/LUCENE-9937) by the paper's authors. We ran both Lucene and the library against the same dataset, comparing the accuracy of their results and the number of computations they performed. When these numbers match closely, we know that Lucene faithfully implements the algorithm.

When incorporating an algorithm into a system, you often need to make modifications or extensions, like scaling it to multiple cores, or adding heuristics to improve performance. It's best to first implement a "vanilla" version, test it against the reference, then make incremental changes. That way you can be confident you've captured all the key parts before making customizations.

### Duel against an existing algorithm

The last section raises another idea for a test invariant: comparing the algorithm's output to a simpler and better-understood algorithm's output. As an example, consider the block-max WAND algorithm in Lucene, which speeds up document retrieval by skipping over documents that can't appear in the top results. It is difficult to describe exactly how block-max WAND should behave in every case, but we do know that applying it shouldn't change the top results! So our tests can generate several random search queries, then [run them both with and without the WAND optimization](https://github.com/apache/lucene/blob/main/lucene/core/src/test/org/apache/lucene/search/TestWANDScorer.java#L669) and check that their results always match.

An important aspect of these tests is that they [generate random inputs](https://www.elastic.co/blog/elasticsearch-testing-qa-increasing-coverage-randomizing-test-runs) on which to run the comparison. This can help exercise cases you wouldn't have thought of, and surface unexpected issues. As an example, Lucene's randomized comparison test for BM25F scoring has helped [catch bugs in subtle edge cases](https://issues.apache.org/jira/browse/LUCENE-10039). The idea of feeding an algorithm random inputs is closely related to the concept of [fuzzing](https://en.wikipedia.org/wiki/Fuzzing), a common testing technique in computer security.

Elasticsearch and Lucene frequently use this testing approach. If you see a test that mentions a "duel" between two algorithms (TestDuelingAnalyzers, testDuelTermsQuery...), then you know this strategy is in action.

## Use the paper's terminology

When another developer works with your code, they'll need to consult the paper to follow its details. The [comment on Elasticsearch's HyperLogLog++ implementation](https://github.com/elastic/elasticsearch/blob/4f22f437ee50cacb94b37b457be1da0b8ba0e8ce/server/src/main/java/org/elasticsearch/search/aggregations/metrics/HyperLogLogPlusPlus.java#L24-L39) says it well: “Trying to understand what this class does without having read the paper is considered adventurous.” This method comment also sets a good example. It includes a link to the academic paper, and highlights what modifications were made to the algorithm as it was originally described.

Since developers will base their understanding of the code on the paper, it's helpful to use the exact same terminology. Since mathematical notation is terse, this can result in names that would not usually be considered “good style”, but are very clear in the context of the paper. Formulas from academic papers are one of the few times you'll encounter cryptic variable names in Elasticsearch like [rS and muBarSInverse](https://github.com/elastic/elasticsearch/blob/4f22f437ee50cacb94b37b457be1da0b8ba0e8ce/server/src/main/java/org/elasticsearch/node/ResponseCollectorService.java#L151).

*The author's recommended way of reading a paper: with a large coffee.*

![elastic-blog-academicpaper.jpg](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt12d81453c706f7cb/6a17d80e0b0bede6badd3424/d03a8e2a50e173b15a4ec3732810c63ff53321f6-1440x1081.jpg)

## You can email the author

When working through a tough paper, you may spend hours puzzling over a formula, unsure if you're misunderstanding or if there's just a typo. If this were an open source project, you could ask a question on GitHub or StackOverflow. But where can you turn for an academic paper? The authors seem busy and might be annoyed by your emails.

On the contrary, many academics love hearing that their ideas are being put into practice and are happy to answer questions over email. If you work on a product they're familiar with, they might even list the application on their website!

There's also a growing trend for academics to discuss papers in the open, using many of the same tools from software development. If a paper has an accompanying software package, you might find answers to [common questions on Github](https://github.com/facebookresearch/faiss/issues/1928). Stack Exchange communities like “Theoretical Computer Science” and “Cross Validated” also contain [detailed discussions about popular papers](https://cstheory.stackexchange.com/questions/49296/problem-in-the-paper-stable-minimum-space-partitioning-in-linear-time). Some conferences have begun to publish all paper reviews online. These reviews contain [back-and-forth discussions](https://openreview.net/forum?id=H1eA7AEtvS) with the authors that can surface helpful insights about the approach.

## To be continued

This post focuses on the basics of choosing an academic paper and

implementing it correctly, but doesn't cover all aspects of actually deploying the algorithm. For example, if the algorithm is just one component in a complex system, how do we ensure that changes to the component lead to end-to-end improvements? And what if integrating the algorithm requires substantial modifications or extensions that the original paper doesn't cover? These are important topics we hope to share more about in future posts.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt950edbc25d291821/6a6119f01b1d495dc56f181b/31783975126874424fc20c3c96bd95fe28d5f201-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

### How Elasticsearch auto-tunes vector quantization to hit your recall target

July 21, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter