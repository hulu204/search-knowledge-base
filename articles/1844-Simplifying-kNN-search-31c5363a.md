---
title: 'Simplifying kNN search'
company: Elastic
tag: 召回
date: 2024-04-17
url: https://www.elastic.co/search-labs/blog/simplifying-knn-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Simplifying kNN search

Elastic's kNN search has evolved. This blog explains the simplification of kNN search, where k and num\_candidates are now optional.

April 17, 2024

[Panagiotis Bailis](/search-labs/author/panagiotis-bailis)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In this blog post we'll take a deep dive into our efforts on making the onboarding experience to kNN search just a bit easier!

## Vector search overview

Vector search has been available for quite some time on Elasticsearch through the use of a new dedicated `knn` search type, while we also introduced kNN as a query in the `8.12.0` release (more on this [amazing blog post](./knn-query-elasticsearch) we recently published!).

While the execution flow and the applications of each approach have some differences, the syntax to do basic kNN retrieval is pretty much similar. So, a typical `knn` search request looks like this:

```
GET products/_search
{
    "knn": {
     "field": "my_vector",
     "query_vector": [1, 2, 3],
     "k": 5,
     "num_candidates": 10
   }
}
```

The first couple of params are pretty much intuitive: we specify where the data is stored (`field`) and what we want to compare it against (`query_vector`).

The `k` and `num_candidates` params on the other hand are a bit more obscure and require some understanding in order to fine-tune them. They are specific to the algorithm & data structure that we use, i.e. HNSW, and exist mainly to control the amount of graph exploration we want to do.

Elasticsearch docs are a great resource for all things around search, so taking a look at the [knn section](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-search.html#search-api-knn) we have:

> `k`: Number of nearest neighbors to return as top hits. This value must be less than `num_candidates`.

> `num_candidates` -> The number of nearest neighbor candidates to consider per shard. Needs to be greater than `k`, or `size` if `k` is omitted, and cannot exceed 10,000. Elasticsearch collects `num_candidates` results from each shard, then merges them to find the top `k` results. Increasing `num_candidates` tends to improve the accuracy of the final `k` results.

However, when you're first met with something like this, it really isn't that obvious what these values should be, and properly configuring them could turn out to be a challenge. The larger these values are, the more vectors we'll get to explore, but this will come with a performance cost. Once again we're met with the ever present tradeoff of accuracy vs performance.

To make kNN search just a bit easier and more intuitive to use, we decided to make these parameters optional, so that you'd only need to provide where and what you want to search, and you could tune them if you only really need to. While seemingly a rather small change, it makes things much more clear! So, the above query could now simply be rewritten as:

```
GET products/_search
{
    "knn": {
     "field": "my_vector",
     "query_vector": [1, 2, 3]
   }
}
```

## Simplifying kNN search by making `k` and `num_candidates` optional

So we want to make `k` and `num_candidates` optional. That's great! How should we set the default values though?

![magic](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0fd64c77f371ed31/6a17e7c1ec0f8952cc5a6627/58938e515811ea25f62073bd01e3c24b0b2343c6-480x480.gif)

There are two options at this point. Pick something that looks like a good option, ship it, and hope for the best, or do the hard work and make extensive evaluations to let data drive our decisions. Here at Elastic, we love such challenges, and want to make sure that any decision taken is justified and for good reason!

Just above, we stated that `k` for kNN search is the number of results we get back from each shard, so one obvious default here would be to just use `size`. So, each shard would return `size` results, and we would merge & sort them to find the global top `size` results. This also works really nice with the kNN query where we don't have a `k` param at all, but instead we operate based on the request's `size` (remember that `knn` query behaves just like any other query such as `term`, `prefix`, etc). So, `size` seems like a sensible default that would cover most of the use cases (or at least be good enough during the onboarding experience!).

`num_candidates` on the other hand is something that is much more different. This parameter is specific to the `HNSW` algorithm and controls the size of the nearest neighbor queue we'll consider (for the curious: this is equivalent to the `ef` parameter in the [original paper](https://arxiv.org/pdf/1603.09320.pdf) )

There are multiple approaches we could take here:

* we could account for the size of each graph and come up with a function that would calculate the appropriate `num_candidates` for `N` indexed vectors
* we could take a look at the underlying data distribution and try to guesstimate the needed exploration (maybe by also considering HNSW's entry points)
* we could assume that `num_candidates` is not directly related to the indexed data, but rather to the search request, and ensure that we'll do the needed exploration to provide good enough results.

As a start and to keep things simple, we looked into setting a `num_candidates` value relative to `k` (or `size`). So, the more results you actually want to retrieve, the higher the exploration we'll perform on each graph to make sure that we escape from local minima. The candidates that we'll focus mostly on are the following:

* `num_candidates = k`
* `num_candidates = 1.5 * k`
* `num_candidates = 2 * k`
* `num_candidates = 3 * k`
* `num_candidates = 4 * k`
* `num_candidates = Math.max(100, k)`

It's worth noting here that more alternatives were initially examined but higher values provided little benefit, so for the rest of the blog we'll focus mostly on just the above.

Having a set of `num_candidates` candidates (no pun intended!) we now focus on the `k` parameter. We opted to account for both standard searches as well as very large `k` values (to see the actual impact of the exploration we do). So, the values we decided to focus more upon were:

* `k = 10` (to account for the requests where no`size` is specified)
* `k = 20`
* `k = 50`
* `k = 100`
* `k = 500`
* `k = 1000`

## Benchmarking & experimentation for simplifying kNN search

### Data

As there is no one-size-fits-all solution, we wanted to test with different datasets that had varying attributes. So, different number of total vectors, dimensions, as well as generated from different models, so different data distributions.

At the same time we have `rally` available, which is an awesome tool for benchmarking Elasticsearch (<https://github.com/elastic/rally>), and supports running a bunch of queries & extracting metrics for a number of vector datasets. Here at Elastic, we make extensive use of rally and rely on it for all our nightly benchmarks, which you can check [here](https://elasticsearch-benchmarks.elastic.co)!

Running a benchmark on rally is as simple as running the following:

```
pip3 install esrally && esrally race --track=dense-vector
```

To this end, we slightly modified the tracks (i.e. rally's test scenarios) to include additional metric configurations, added some new ones, and ended up with the following set of tracks:

* `dense-vector` (2M docs, 96dims): <https://github.com/elastic/rally-tracks/tree/master/dense_vector>
* `so-vector` (2M docs, 768 dims): <https://github.com/elastic/rally-tracks/tree/master/so_vector>
* `cohere-vector` (3M docs, 768 dims): <https://github.com/elastic/rally-tracks/tree/master/cohere_vector>
* `openai-vector` (2.5M docs, 1536dims): <https://github.com/elastic/rally-tracks/tree/master/openai_vector>
* `Glove 200d` (1.2M, 200dims) new track created based on <https://github.com/erikbern/ann-benchmarks> repo

It's also worth noting that for the first couple of datasets, we would also like to account for both having one vs multiple segments so we included 2 variants of each,

* one where we execute `force_merge` and have a single segment, and
* one where we rely to the underlying `MergeScheduler` to do its magic and end up with how many segments it sees fit.

### Metrics

For each of the above tracks, we calculated the standard recall and precision metrics, latency, as well as the actual exploration that we did on the graph by reporting the nodes that we visited. The first couple of metrics are evaluated against the *true nearest neighbors*, as in our scenario, this is the gold standard dataset(remember we're evaluating how good the *approximate* search is, and not the quality of the vectors themselves). The `nodes_visited` attribute has been recently added to knn's profile output (<https://github.com/elastic/elasticsearch/pull/102032>) so, with some minor changes to the track definitions in order to extract all needed metrics, we should be good to go!

### Benchmarks

Now that we know what we want to test, which datasets to use, and how to evaluate the results, it's time to actually run the benchmarks!

To have a standardized environment, for each test we used a clean `n2-standard-8 (8 vCPU, 4 core, 32 GB memory)` cloud node. The Elasticsearch configuration, along with necessary mappings and all else needed, is configured and deployed through `rally`, so it's consistent for all similar tests.

Each of the dataset above was executed multiple times, gathering all metrics available for all candidate sets defined, making sure that no results were one-offs.

### Results

The recall - latency graphs for each of the specified datasets & param combinations can be found below (higher and to the left is better, latency is measured in ms):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc8d346c3eba0e226/6a17e7c2be60861800004736/1b6334dd6e043ad753a09fe3a3a0c22a40ea59a7-1440x809.png)

Dense Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta0df21ee1c3a9218/6a17e7c463baff12aa741c4a/30ea1750434c9265ea0d1bf035dcf4021038cfc8-1440x830.png)

Dense Vector Multiple Segments

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt19f7b2d323ae187b/6a17e7c54b055dafdb4321e7/88b9573393eadf0260b5dd24ca07e7f9ef8280ee-1440x821.png)

SO Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt61f769d327e519aa/6a17e7c7be6086031700473a/c50fe7982d7634e6c141db8cbcc694de8193d499-1440x835.png)

SO Vector Multiple Segments

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8bddf58dcf8927db/6a17e7c8be60864d8600473e/0049305e2a32b7bb8b0b8cda3d4cd5924134218f-1440x832.png)

Glove Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3b55f6ae6364f09c/6a17e7c9e3179176da2d57db/0338fd7b51915d5b3e8c440ff7135d3efc66f53a-1440x820.png)

Cohere Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8acd246a6c7dccb8/6a17e7cbb1e1136a5379f286/7f49d7c495ac0551ec39d4abca967ed2310894bd-1440x794.png)

OpenAI Vector

Narrowing down to the **dense\_vector** and **openai\_vector** tracks for the absolute values of latency@50th percentile and recall we have:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt220da5b824c5d362/6a17e7cdbe6086f260004742/5080ade2db94963bbadc2e9d47653a9ff9a5679d-1440x998.png)

Dense Vector latency@50

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcec8d4b5ea64c864/6a17e7ce4b055d24d14321eb/97c1989390bc86e8b95d3fc992fe521bbf160491-1440x998.png)

Dense Vector recall

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7f5e5a2365cbed5a/6a17e7d0033c8d6ffb6bb1ac/b6595e4c1b94a663677a1def7ee4d12a183dd4ae-1440x998.png)

OpenAI latency@50

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt23b3deb0d648ccc3/6a17e7d12f4a5c736cfa88ff/b046616136f7c0ea780a49da38f9645fa0071904-1440x998.png)

OpenAI Recall

Similarly, the 99th percentile of the HNSW graph nodes visited for each scenario can be found below (smaller is better):

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt80582f75b6da2d1e/6a17e7d31480094f58b48751/65ba9bd863875a0dee9f751738f859dabc2302c7-1440x950.png)

Dense Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt02f4983fc5b34e8a/6a17e7d5be6086c973004746/3dda1ef284c84d7e37aa2813e7fcb8f18e655e3a-1440x970.png)

Dense Vector Multiple Segments

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6daf12b342141293/6a17e7d63e03d75da14f2c82/bb3d0cf68bd3aa8fbde4100778441bcdd3c08210-1440x976.png)

SO Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt853ece37ba817d7d/6a17e7d83e03d721c14f2c86/1b48d771e66ffeeb7b8f8c16222fb1c51330768e-1440x967.png)

SO Vector Multiple Segments

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt40b8cfc4173bb5d0/6a17e7d9414c642bf8945190/e3191c404dcd44d62a8053413820f750b02b5ca1-1440x979.png)

Glove Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt390d5f64f0e483f9/6a17e7db25daab4b1708a24d/0d47cd9f8853be7ce2997753a8fc869f9e6b7c17-1440x960.png)

Cohere Vector

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb9f09fa8a2fa7310/6a17e7dc1d1b83f40d93e463/91e4fe9d6d283a06b907868dd593f447240fa77e-1440x960.png)

OpenAI Vector

### Less is more\*

\*well not in all cases, but hey :)

Taking a look at the results, two things stand out:

* Having one vs many segments clearly affects recall & latency metrics in an inversely proportional manner. Having less segments decreases latency (as we have fewer graphs to traverse, i.e. searches to run) which is great, but it also affects recall in the opposite manner, as it is quite possible that some good candidates will be left out (due to a fewer `num_candidates` lists).
* Even with little exploration we can achieve good enough recall in almost all cases, which is great!

We're constantly aiming at improving multi-segment search ([a great example can be found in this post](./multi-graph-vector-search)) so we expect that this tradeoff will be less of an issue going forward (the numbers reported here do not include these improvements).

Taking all things into account, the two main options we discussed were the following:

* `num_candidates = 1.5 * k` - this achieves good enough recall in almost all cases, with very good latency scores.
* `num_candidates = Math.max(100, k)` - this achieves slightly better recall especially for lower `k` values, with the tradeoff though of increased graph exploration and latency.

After careful consideration and (lengthy!) discussions, we opted to go with the former as the default, i.e. set `num_candidates = 1.5 * k`. We had to do far less exploration and recall was greater than 90% in almost all the cases we tested (with some significantly higher reported numbers as well), which should yield a good enough onboarding experience.

## Conclusion

How we handle kNN search at Elastic is always evolving and we're constantly introducing new features and improvements, so these parameters and this evaluation overall could very well be outdated pretty soon! We're always on the lookout and whenever that happens we'll make sure to follow up and adjust our configurations appropriately!

One important thing to remember is that these values only act as sensible defaults for simplifying the onboarding experience and for very generic use cases. One can easily experiment on their own datasets and adjust accordingly based on their needs (e.g. recall might be much more important than latency in some scenarios).

Happy tuning 😃

### Frequently Asked Questions

#### What's the default value for num\_candidates in kNN search?

The default value for num\_candidates is 1.5 \* k. This achieves good enough recall in almost all cases, with very good latency scores.

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