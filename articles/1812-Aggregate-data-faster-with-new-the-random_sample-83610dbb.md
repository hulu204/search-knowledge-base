---
title: 'Aggregate data faster with new the random_sampler aggregation'
company: Elastic
tag: 工程相关
date: 2022-04-20
url: https://www.elastic.co/search-labs/blog/aggregate-data-faster-with-new-the-random-sampler-aggregation
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Aggregate data faster with new the random\_sampler aggregation

Aggregate billions of documents in milliseconds instead of minutes with Elastic. Learn more about how the new random\_sampler aggregation gives you statistically robust results at a lower cost.

April 20, 2022

[Benjamin Trent](/search-labs/author/benjamin-trent)[Thomas Veasey](/search-labs/author/thomas-veasey)

[AI](/search-labs/blog/category/ai)

Jump to

Share

With 8.2, the Elastic Stack gives users the [`random_sampler`](https://www.elastic.co/guide/en/elasticsearch/reference/master/search-aggregations-random-sampler-aggregation.html) aggregation. It adds the capability to randomly sample documents in a statistically robust manner. Randomly sampling documents in aggregations allows you to balance speed and accuracy at query time. You can aggregate billions of documents with high accuracy at a fraction of the latency. This allows you to achieve faster results with fewer resources and comparable accuracy — all with a simple aggregation.

Let's run through some basic details, best practices, and how it works, so you can try it out in the Elasticsearch Service today.

## Delivering speed and accuracy

Random sampling in Elasticsearch has never been easier or faster. If your query has many aggregations, you can quickly obtain results by using the [`random_sampler`](https://www.elastic.co/guide/en/elasticsearch/reference/master/search-aggregations-random-sampler-aggregation.html) aggregation.

```
POST _search?size=0&track_total_hits=false
{
  "aggs": {
    "sampled": {
      "random_sampler": {
        "probability": 0.001,
        "seed": 42
      },
      "aggs": {
        ...
      }
    }
  }
}
```

All the above aggregations nested under `random_sampler` will return sampled results. Each agg is roughly seeing only 0.1% of the documents (or 1 in every 1000th document). Where computational cost correlates with the number of documents, the aggregation speed increases. You may have also noticed the “`seed`” parameter. You can provide a `seed`to get consistent results on the same shards. Without a seed, a new random subset of documents is considered and you may get slightly different aggregated results.

How much faster is the `random_sampler`? The speed improves according to the provided probability as fewer documents are aggregated. The improvements relative to probability will eventually flatten out. Each aggregation has its own computational overhead regardless of the number of documents. An example of this overhead cost is comparing multi-bucket to single metric aggregations. Multi-bucket aggregations have a higher overhead due to their bucket handling logic. While speed is improved for multi-bucket aggregations, the rate of that speed increase will flatten out sooner than single metric.

![expected speedup](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1427bb522f9a2e33/6a17113be8fbce617c39fd55/e6a33afc9b30709dd5606bfb23726005f40bb803-800x600.png)

Figure 1. The speedup expected for aggregations of different constant overhead.

Here are some results on expected speed and error rate over an APM data set of 64 million documents.

The calculations are from: 300 query and aggregation combinations, 5 seeds, and 9 sampling probabilities. In total, 13,500 separate experiments generated the following graphs for median speedup and median relative error as a function of the downsample factor which is 1 / sample probability.

![median speedup](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd264a08140ef2bed/6a17113dacf0883d26be9c4d/77697af30ebd43c64216df0a9e99951191dd612d-800x600.png)

Figure 2. Median speedup as a function of the downsample factor (or 1 / probability provided for the sampler).

![median error](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1f3876b646dd7b14/6a17113e1949f77a4ae7ab20/047bb5dd28bedaee14998168d71ac152e3ea4392-800x600.png)

Figure 3. Median relative error as a function of the downsample factor (or 1 / probability provided for the sampler).

With a probability of 0.001, for half of the scenarios tested, there was an 80x speed improvement or better with a 4% relative error or less. These tests involved a little over 64 million documents but spread across many shards. More compact shards and larger data can expect better results.

But, you may ask, do the visualizations look the same?

Below are two visualizations showing document counts for every 5 minutes over 100+ million documents. The total set loads in seconds and is sampled in milliseconds. This is with almost no discernible visual difference.

![sampled vs unsampled count](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0e84bd402ad8ec58/6a171140b339d56a6976a0c2/925ab6b529edb5065ec7d0f1886f7bc3eaa7da62-800x158.png)

Figure 4. Sampled vs unsampled document count visualizations.

Here is another example. This time the average transaction by hour is calculated and visualized. While visually these are not exactly the same, the overall trends are still evident. For a quick overview of the data to catch trends, sampling works marvelously.

![sampled vs unsampled average](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt583f18fbd2c02001/6a171141acf0885acabe9c51/1998189c574de515e1bff2dca886bd923a2af584-800x250.png)

Figure 5. Sampled vs. unsampled average transaction time by hour visualization.

## Best practices for using sampling aggregation

Sampling shines when you have a large data set. In these cases you might ask, should I sample before the data is indexed in Elasticsearch? Sampling at query time and before ingestion are complimentary. Each has its distinct advantages.

When sampling at ingest time, it can save disk and indexing costs. However, if your data has multiple facets, you have to stratify sampling over facets when sampling before ingestion, unless you know exactly how it will be queried. This suffers from the [curse of dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality) and you could end up with underrepresented sets of facets. Furthermore, you have to cater for the worst case when sampling before ingestion. For example, if you want to compute percentiles for two queries, one which matches 50% of the documents and one which matches 1% of documents in an index, you can get away with 7X more downsampling for the first query and achieve the same accuracy.

Here is a summary of what to expect from sampling with the `random_sampler` at query time.

![relative error](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt908ecf7a4a90ba82/6a1711436234e00ddcdb1ada/3a1cc19429ee33b95e6a0ab6eed2413665a5e0bd-640x480.png)

Figure 6. Relative error for different aggregations.

Sampling accuracy varies across aggregations (see Figure 5 for some examples). Here is a list of some aggregations in order of descending accuracy: [percentiles](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-percentile-aggregation.html), [counts](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-valuecount-aggregation.html), [means](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-avg-aggregation.html), [sums](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-sum-aggregation.html), [variance](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-extendedstats-aggregation.html), [minimum](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-min-aggregation.html), and [maximum](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-metrics-max-aggregation.html). Metric aggregation accuracy will also be affected by the underlying data variation: the lower the variation in the values, the fewer samples you need to get accurate aggregate values. The minimum and maximum will not be reliable with outliers, since there is always a reasonable chance that the sampled set misses the one very large (or small) value in the data set. If you are using terms aggregations (or some partitioning such as date histogram), aggregate values for terms (or buckets) with few values will be less accurate or missed altogether.

Aggregations also have fixed overheads (see Figure 1 for an example). This means as the sample size decreases, the performance improvement will eventually level out. Aggregations which have many buckets have higher overheads and so the speedup you will gain from sampling is smaller. For example, a [terms aggregation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-terms-aggregation.html) for a high cardinality field will show less performance benefit.

If in doubt, some simple experiments will often suffice to determine good settings for your data set. For example, suppose you want to speed up a dashboard; try reducing the sample probability while the visualizations look similar enough. Chances are your data characteristics will be stable and so this setting will remain reliable.

## Uncovering how sampling works

Sampling considers the entire document set within a shard. Once it creates the sampled document set, sampling applies any provided user filter. The documents that match the filter and are within the sampled set are then aggregated (see Figure 7).

![request data flow](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltfed879f2c11f87c2/6a171144ab7f08018ddb9f8f/9145ccea9747229b2d08a8badf6120c20bd0e271-800x227.png)

Figure 7. Typical request and data flow for the random\_sampler aggregation.

The key to the sampling is generating this random subset of the shard efficiently and without statistical biases. Taking [geometrically distributed random](https://en.wikipedia.org/wiki/Geometric_distribution) steps through the document set is equivalent to uniform random sampling, meaning each document in the set has an equally likely chance of being selected into the sample set. The advantage of this approach is that the sampling cost scales with p (where p is the probability configured in the aggregation). This means no matter how small p is, the relative latency of performing the sampling adds will remain fixed.

## Ensuring performance reliability and accuracy

To achieve the highest performance, accuracy, and robustness, we evaluated a range of realistic scenarios.

In the case of `random_sampler,` the evaluation process is complicated by two factors:

1. It cuts right across the aggregation framework and so it needs to be evaluated with many different combinations of query and aggregation,
2. The results are random numbers, so rather than running just once, you need to run multiple times and test the statistical properties of the result set.

We began with a proof of concept that showed that the overall strategy worked and the performance characteristics were remarkable. However, there are multiple factors which can affect implementation performance and accuracy. For example, we found the off-the-shelf sampling code for the geometric distribution was not fast enough. We decided to roll our own using some tricks to extract more random samples per random bit along with a very fast quantized version of the log function. You also need to be careful that you are generating statistically independent samples for different shards. In summary, as is often the case, the devil is in the details.

Undaunted, we wrote a test harness using the [Elastic Python client](https://elasticsearch-py.readthedocs.io/en/stable/) to programmatically generate aggregations and queries, and perform statistical tests of quality.

We wanted the approximations we produce to be unbiased. This means if you run a sampled aggregation repeatedly and averaged the results it would converge towards the true value. Standard machinery allows you to test if there is statistically significant evidence of bias. We used a [t-test](https://en.wikipedia.org/wiki/Student%27s_t-test) for the difference between the statistic and true value for each aggregation. In over 300 different experiments, the minimum p-value was around 0.0003 which — given we ran 300 experiments — has about a 9% odds of occurring by chance. This is a little low, but not enough to worry about; furthermore the median p-value was 0.38.

We also tested whether various index properties affect the statistical properties. For example, we wanted to see if we could measure a statistically significant difference between the distribution of results with and without index sorting. A [K-S test](https://en.wikipedia.org/wiki/Kolmogorov%E2%80%93Smirnov_test) can be used to check if samples come from the same distribution. In our 300 experiments the smallest p-value was around 0.002 which occurs with odds of about 45% by chance.

## Get started today

We're not done with this feature yet. Once you have the ability to generate fast approximate results, a key question is: how accurate are those results? We're planning to integrate a confidence interval calculation directly into the aggregation framework to answer this efficiently in a future release. Learn more about random\_sampler\_aggregation in this documentation. You can explore this feature and more with a [free 14-day trial of Elastic Cloud](https://cloud.elastic.co/registration?elektra=whats-new-elastic-8-1-0-blog).

*The release and timing of any features or functionality described in this post remain at Elastic's sole discretion. Any features or functionality not currently available may not be delivered on time or at all.*

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter