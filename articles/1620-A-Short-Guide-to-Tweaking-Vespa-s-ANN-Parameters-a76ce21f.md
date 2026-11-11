---
title: "A Short Guide to Tweaking Vespa's ANN Parameters"
company: Vespa
tag: 召回
date: 2025-09-04
url: https://blog.vespa.ai/tweaking-ann-parameters/
account: 
origin: harvest3-202607
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Jan Böker](/assets/avatars/boeker.jpg)

[Jan Böker](/authors/boeker/ "Jan Böker")
  
Software Engineer

04 Sep 2025

# A Short Guide to Tweaking Vespa's ANN Parameters

With the latest [Additions to HNSW in Vespa](/additions-to-hnsw/),
most notably ACORN-1,
the amount of parameters in Vespa can easily be overwhelming.
This companion blog post
briefly explains how one should tweak the ANN parameters in Vespa
to achieve the best possible performance for a given data set.

#### Strategy Thresholds for Filtered ANN Search

In the [Additions to HNSW in Vespa](/additions-to-hnsw/) blog post,
we described the different strategies available in Vespa for ANN search with filters:

1. Exact Nearest-Neighbor Search with Pre-Filtering
2. HNSW Search with Post-Filtering
3. HNSW Search with Pre-Filtering
4. HNSW Search with Pre-Filtering: Check Filter First/ACORN-1

That is, when compared to the
[Query Time Constrained Approximate Nearest Neighbor Search](/constrained-approximate-nearest-neighbor-search/) blog post,
we have a new, fourth strategy.
As described there, Vespa automatically chooses a strategy based on the filter hit ratio
of the query.
The
[rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) parameters/[query API](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching) parameters
that control these choices are:

* **post-filter-threshold**/**ranking.matching.postFilterThreshold** - default 1.00,
* **filter-first-threshold**/**ranking.matching.filterFirstThreshold** - default 0.00 and
* **approximate-threshold**/**ranking.matching.approximateThreshold** - default 0.05, respectively.

The following is an updated version of the flowchart that details
how the choice of strategy for an ANN query with filtering is made.

![ANN Parameter Flowchart](/assets/2025-09-04-tweaking-ann-parameters/flowchart.svg)  
***Figure 1** How Vespa chooses a strategy for an ANN query with filters*

Hence, with the default values an HNSW search with pre-filtering is used unless
the hit ratio is below 5%, where we fall back to an exact search.
Post-filtering and ACORN-1 are not used by default.

#### Setting the Threshold Parameters

In this example, we run Vespa with 1 million vectors from the
[data set used in the Luceneutil benchmark](https://github.com/mikemccand/luceneutil)
in a development environment running locally on a modern Mac,
where we selected documents at random to obtain filters to use.
These vectors are 768-dimensional float vectors obtained from embedding
Wikipedia articles.
We are going to tweak the threshold parameters in Vespa to achieve response-time and recall curves
that are as flat as possible across the different hit ratios.
We do not use post-filtering, but instead switch between the following three strategies:

1. HNSW Search with Pre-Filtering when the percentage of filtered-out documents is low,
2. HNSW Search with Pre-Filtering: Filter First/ACORN-1 when the percentage of filtered-out documents is high,
3. Exact Nearest-Neighbor Search when the percentage of filtered-out documents approaches 100%.

The point at which we switch from (1) to (2) and from (2) to (3) in Vespa is controlled by the
[rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) parameters/[query API](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching) parameters

* **filter-first-threshold**/**ranking.matching.filterFirstThreshold** - default 0.00 and
* **approximate-threshold**/**ranking.matching.approximateThreshold** - default 0.05, respectively.

As we are not using post-filtering, the interesting part of the flowchart is what happens
after the execution of the pre-filter.
Given a filter with a hit ratio of *hit-ratio*, the choice of algorithm in Vespa is made as follows:

1. HNSW Search with Pre-Filtering if *hit-ratio ≥ filter\_first-threshold*,
2. HNSW Search with Pre-Filtering: Filter First/ACORN-1 if *filter-first-threshold > hit-ratio ≥ approximate-threshold*,
3. Exact Nearest-Neighbor Search if *approximate-threshold > hit-ratio*.

This means that, with the default values of the parameters, only (1) and (3) are used:
the fallback to the exact search happens when the *hit-ratio* falls below *0.05*.
To get a feeling for how this behaves, let us run a benchmark with 100 target hits on our data set.

![ANN: Default Parameters](/assets/2025-09-04-tweaking-ann-parameters/default.svg)  
***Figure 2** Performance with Vespa’s default parameters*

One can clearly see the response time increase with more restrictive filters
and spike at a hit ratio of *0.05*.
We can improve the response time by switching to the ACORN-1 strategy.
Since the response time already starts to increase
when around 60% of documents are filtered out, i.e., at a hit ratio of *0.4*,
we set the *filter-first-threshold* to *0.4*.
Note that this value is dependent on the data set at hand. For other data sets,
the response time might increase earlier or later, so one should find out
where it makes sense to use ACORN-1 for the specific data set at hand.
A benchmark with *filter-first-threshold* set to *0.4* then yields the following.

![ANN: Tweaked *filter-first-threshold*](/assets/2025-09-04-tweaking-ann-parameters/tweakedfft.svg)  
***Figure 3** Adapted filter-first-threshold to enable ACORN-1*

We avoid the increase in response time starting to happen when around 60% of documents are filtered out.
This however, is not free and comes at the cost of a small drop in recall, which we have to accept.
However, since we did not adjust the *approximate-threshold* yet, the fallback to an exact search
happens too early and we see a sudden spike in response time.
Ideally, we want to set the *approximate-threshold* parameter such that the fallback
happens when the costs of an ACORN-1 search and an exact search are roughly the same.
Note that the cost of an exact nearest neighbor search
is heavily dependent on the number of vectors and the dimension of the vectors used,
so in general, the more vectors you have and the larger they are,
the later you want to fall back to an exact search.
At the same time, it is important not to completely disable the fallback to an exact search
since the recall for ACORN-1 will inevitably degrade at some point.
In our example, let us set *approximate-threshold* to *0.01*.

![ANN: Tweaked *approximate-threshold*](/assets/2025-09-04-tweaking-ann-parameters/tweakedat.svg)  
***Figure 4** Adapted approximate-threshold to fall back to an exact search at a later point*

As one can observe, this completely avoids the spike in response time
at the cost of the recall dropping further when more documents are filtered out.
On this data set, the drop in recall is still acceptable, and we could leave the parameters like this.
If you have more documents,
however, and have chosen a lower *approximate-threshold*, you might see a more drastic
dip in recall. To counteract this, one can increase the *filter-first-exploration* parameter.
Let us see what happens when we change it from the default value to *0.4*.

![ANN: Tweaked *filter-first-exploration*](/assets/2025-09-04-tweaking-ann-parameters/tweakedffe.svg)  
***Figure 5** Increased filter-first-exploration to increase recall*

The recall just before the exact fallback increased, but so did the response time.
As seen in the [Additions to HNSW in Vespa](/additions-to-hnsw/) blog post, one has to be careful not to increase the exploration
value too much. Otherwise, one risks loosing the benefits of ACORN-1.
For better readability, let us compare the results with the default values and
the tweaked values in a single plot.

![ANN: Tweaked *filter-first-exploration*](/assets/2025-09-04-tweaking-ann-parameters/tweaked.svg)  
***Figure 6** Default vs. tweaked behavior*

#### Tweaking Recall Parameters

In the previous subsection, we tweaked the threshold parameters while searching for 100 target hits.
Depending on the data set and the number of target hits that we actually query for, the recall might be too low. How do we avoid this?
The usual way is to increase the number of target hits and
then to ignore the additional results. This can be done either directly or by using the
[*hnsw.exploreAdditionalHits*](https://docs.vespa.ai/en/reference/query-language-reference.html#hnsw-exploreadditionalhits) annotation.
The following plot shows how large the effect of increasing this is when querying for 10 hits.

![Effect of increasing exploreAdditionalHits](/assets/2025-09-04-tweaking-ann-parameters/recall_by_extended_hits.svg)  
***Figure 7** Effect of increasing exploreAdditionalHits when querying for 10 hits (without filters)*

Note that this is not free and comes at the cost of response time!
As seen in the [Additions to HNSW in Vespa](/additions-to-hnsw/) blog post, it might be beneficial to instead use the
[rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) parameter/[query API](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching) parameter

* **exploration-slack**/**ranking.matching.explorationSlack** - default 0.00

since it might offer a slightly better response time at the same recall.
The following plot gives an idea of the range one should aim for when increasing this parameter.

![Effect of increasing exploration-slack](/assets/2025-09-04-tweaking-ann-parameters/recall_by_slack.svg)  
***Figure 8** Effect of increasing exploration-slack when querying for 10 hits (without filters)*

That is, already small values of *0.05* and *0.1* have a huge effect, which comes at the cost of response time.
So be careful not to just set this to a large value!
When comparing the response times, we can see that the results nearly identical to slightly worse on this specific data set.

![*exploration-slack* vs *exploreAdditionalHits*](/assets/2025-09-04-tweaking-ann-parameters/slack.svg)  
***Figure 9** exploreAdditionalHits vs. exploration-slack*

Hence, on this specific data set, we can ignore the *exploration-slack* parameter and just increase the number of target hits.

## Read more

[![Additions to HNSW in Vespa: ACORN-1 and Adaptive Beam Search](/assets/2025-09-04-additions-to-hnsw/alina-grubnyak-ZiQkhI7417A-unsplash.jpg)

Photo by [Alina Grubnyak](https://unsplash.com/@alinnnaaaa?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash) on [Unsplash](https://unsplash.com/photos/low-angle-photography-of-metal-structure-ZiQkhI7417A?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)](/additions-to-hnsw/)
[## Additions to HNSW in Vespa: ACORN-1 and Adaptive Beam Search

#### This blog post highlights the latest additions to HNSW in Vespa, how to use them, and what's to come in the future.](/additions-to-hnsw/)

[![Query Time Constrained Approximate Nearest Neighbor Search](/assets/2022-05-09-constrained-approximate-nearest-neighbor-search/christopher-burns-Kj2SaNHG-hg-unsplash.jpg)

Photo by [Christopher Burns](https://unsplash.com/@christopher__burns?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/photos/Kj2SaNHG-hg?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)](/constrained-approximate-nearest-neighbor-search/)
[## Query Time Constrained Approximate Nearest Neighbor Search

#### This blog post describes Vespa's industry leading support for combining approximate nearest neighbor search, or vector search, with query constraints to solve real-world search and recommendation problems at scale.](/constrained-approximate-nearest-neighbor-search/)

[![Approximate Nearest Neighbor Search in Vespa - Part 1](/assets/2020-06-30-approximate-nearest-neighbor-search-in-vespa-part-1/search-throughput-sift.png)](/approximate-nearest-neighbor-search-in-vespa-part-1/)
[## Approximate Nearest Neighbor Search in Vespa - Part 1

#### In this blog post we explore how the Vespa team selected HNSW (Hierarchical Navigable Small World Graphs) as the baseline approximate nearest neighbor algorithm for extension and integration in Vespa....](/approximate-nearest-neighbor-search-in-vespa-part-1/)

[« Additions to HNSW in Vespa: ACORN-1 and Adaptive Beam Search](/additions-to-hnsw/)
[Vespa Newsletter, September 2025 »](/vespa-newsletter-september-2025/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)