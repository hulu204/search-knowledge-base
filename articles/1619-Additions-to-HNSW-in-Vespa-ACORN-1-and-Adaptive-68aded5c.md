---
title: 'Additions to HNSW in Vespa: ACORN-1 and Adaptive Beam Search'
company: Vespa
tag: 召回
date: 2025-09-04
url: https://blog.vespa.ai/additions-to-hnsw/
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

# Additions to HNSW in Vespa: ACORN-1 and Adaptive Beam Search

What do modern RAG applications, search systems, and recommender systems have in common?
They all rely heavily on nearest neighbor search of vectors.
Since exact nearest neighbor search over millions and millions of vectors is prohibitively expensive,
Vespa employs the HNSW (Hierarchical Navigable Small World) algorithm
for approximate nearest-neighbor (ANN) search, trading a bit of accuracy for a vast reduction in response time.

Five years ago, in the [Approximate Nearest Neighbor Search in Vespa - Part 1](/approximate-nearest-neighbor-search-in-vespa-part-1/) blog post,
we elaborated why our choice of algorithm for ANN fell on HNSW by showing that it
compares favorably to other algorithms for ANN search.
In HNSW, a hierarchy of graphs is used as an index, and while
there is a comparably high initial indexing cost for building the index,
the search throughput is much higher than with other algorithms.
Since then, there have been advancements in Vespa like
[multi-vector HNSW indexing](/semantic-search-with-multi-vector-indexing/),
but also some recent enhancements to the HNSW search itself.
In this blog post, we discuss these enhancements and describe the way we implemented them in Vespa.
In a companion blog post, we will present a short guide on how to make use of these parameters
by tweaking them for the specific data set you have at hand.

## Filtered Nearest Neighbor Search

Real-world applications, both search systems and recommender systems using vector search,
require *query-time constrained* vector search and not just plain vector search:
not all vectors have to be searched, but only those that pass a filter given at query time.
For example, a typical e-commerce search allows the user to filter search results using result facets.
As one would expect, exact nearest neighbor search get simpler the more restrictive the filter is:
the less vectors match the filter, the fewer distances we have to compute, the better.
For approximate nearest neighbor search via HNSW, the opposite is the case:
it gets more complicated.

#### Strategies in Vespa

In the [Query Time Constrained Approximate Nearest Neighbor Search](/constrained-approximate-nearest-neighbor-search/) blog post,
we described how Vespa integrated filters into HNSW searches.
In this section, we show how this can be improved by taking a core idea from a family of algorithms
know as [ACORN](https://arxiv.org/abs/2403.04871) into Vespa.
To this end, let us give an overview over the existing strategies before
we discuss what ACORN brings to the table.
Finally, we end with a practical tutorial on how to tune the ANN search parameters
available in Vespa.

1. **Exact Nearest-Neighbor Search with Pre-Filtering**

   Perform an exact nearest-neighbor search by iterating over all documents that pass the filter.
   This works well for very restrictive filters since the number of distance computations
   scales linearly with the number of documents that pass the filter.
   The following plot shows that computers are complicated
   and that the response time does not decrease linearly as expected.
   The main point however still stands, i.e., an exact search indeed works well
   for very few documents.

   ![Exact Search](/assets/2025-09-04-additions-to-hnsw/exact.svg)  
   ***Figure 1** Exact search across different filtering degrees*

   All plots in this section on filtered nearest neighbor search were obtained by running benchmarks with 1 million vectors from the the
   [data set used in the Luceneutil benchmark](https://github.com/mikemccand/luceneutil)
   in a development environment running locally on a modern Mac.
   These vectors are 768-dimensional float vectors obtained from embedding
   Wikipedia articles, and the filters we used were obtained by choosing documents at random.
2. **HNSW Search with Post-Filtering**

   Perform an HNSW search without using a filter.
   Then, apply the filter on the retrieved hits.
   The advantage is that the cost of the ANN search
   is the same as for unfiltered queries,
   but the disadvantage is that one cannot tell in advance how many nearest neighbors
   will be eliminated by the filter.
   In the worst case, the filter might even eliminate all hits.
   While the number of target hits
   in the HNSW search can be increased to counteract this,
   this increases the query cost
   and still does not give a guarantee on the number of hits that pass the filter.
3. **HNSW Search with Pre-Filtering**

   While performing an HNSW search, if a document with a low distance to the query is found,
   check whether it passes the filter and, if it does, add it to the candidate queue.
   This works well if most documents pass the filter. If the filter is too restrictive, however,
   a large part of the graph is traversed and a lot of distances are computed, mostly for documents that do not even pass
   the filter. This can be observed in the following plot, where the response time spikes
   when the filter gets very restrictive.

   ![HNSW: Compute Distance, Check Filter](/assets/2025-09-04-additions-to-hnsw/hnsw.svg)  
   ***Figure 2** HNSW search across different filtering degrees*

   This is the original implementation of HNSW with filtering in Vespa.
   Note that this is called *post-filtering* in the
   [ACORN paper](https://arxiv.org/abs/2403.04871).
4. **HNSW Search with Pre-Filtering: Check Filter First/ACORN-1**

   Ideally, one would like to have one set of HNSW graphs for every filter.
   This, however, is not feasible since the filter is specified at query time.
   So, why not take the subgraphs of the HNSW graphs induced by all nodes that pass the given filter?
   That is, instead of computing the distance of a found vector to the query and checking whether it passes the filter,
   one would like to check the filter first and just outright ignore nodes that do not pass the filter:
   this avoids the expensive distance computations for nodes that cannot be hits anyway.
   The difficulty with this approach is that, for a highly restrictive filter, this is likely to destroy the connectivity of the HNSW graphs.

   The [ACORN](https://arxiv.org/abs/2403.04871)
   family of algorithms attacks this connectivity issue from two sides:
   First, by constructing a set of denser HNSW graphs:
   while a node in an HNSW graph has up to *M* neighbors,
   a node used in an ACORN-γ graph has up to *γ⋅M* neighbors.
   Second, by sometimes considering 2-hop neighborhoods during the search.
   The goal of this is to avoid constructing large neighborhoods in the graphs
   as it allows to prune neighbors during construction if they can already be reached via 2 hops.
   This novel pruning step replaces the original pruning step used in HNSW
   since this original pruning step is *metadata blind*, i.e., it does not take
   possible filters into account and might prune edges critical when considering
   the subgraph induced by a filter.

   ACORN-1 is a special case of ACORN-γ with a twist.
   First, the maximum number of neighbors in the graphs is *γ⋅M = 1⋅M = M*, the same as in HNSW
   graphs. Second, the pruning step during construction is completely left out, i.e.,
   the constructed graphs correspond to these of HNSW (without the usual pruning
   step used in HNSW). Then, during search, the 2-hop neighbors of every node are fully explored.
   This additional twist means that ACORN-1 is not just ACORN-γ with *γ = 1*.
   While this sounds promising, HNSW graphs are an in-memory data structure and increasing their size by implementing ACORN directly,
   be it ACORN-γ or ACORN-1, does not seem like a good idea.
   Hence, the only sensible option we see is to use the existing HNSW graphs
   and to touch only the HNSW search by additionally exploring 2-hop neighbors.

   That is, instead of computing the distance of all neighbors of a node to the query and
   then checking which of the relevant neighbors pass the filter as before,
   we take the neighbors and 2-hop neighbors of the node, and for those that pass the filter,
   computes their distance to the query vector to see if they are relevant.
   Check out the blog post from [Lucene](https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search)
   for an awesome visualization of this!
   This idea leads to a strategy with a behavior that looks like this:

   ![Filter First: Exploration Parameter](/assets/2025-09-04-additions-to-hnsw/filter-first-exploration0.35.svg)  
   ***Figure 3** ACORN-1 across different filtering degrees*

   In the following, we describe some experiments we did with this and how we ended up with this implementation.

#### Implementing ACORN-1

So, to implement ACORN-1, when visiting a node in the HNSW search,
we take the neighbors and 2-hop neighbors of the node, and for those that pass the filter,
computes their distance to the query vector to see if they are relevant.
To avoid exploring excessive amounts of vertices, we stop the exploration once the number
of nodes found reaches the maximum degree of the graph on the current level.
Formulated as pseudocode, the exploration for node *node* looks as follows.

```
max_neighbors_to_find = max_links_for_level(level);

todo.push_back(node);

// Explore (1-hop) neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);

// Explore 2-hop neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);
```

A quick benchmark on the test data set shows that this already works quite well:

![Filter First: 2-Hop Neighbors](/assets/2025-09-04-additions-to-hnsw/filter-first-2-hops.svg)  
***Figure 4** Just exploring 2-hop neighbors with different filtering degrees*

Let us compare this to the previous plot for an HNSW search with pre-filtering where we compute distances first.

* Looking at the high-selectivity region to the left, one can see that both response time
  and recall slightly increased.
  This can be explained by the fact that we actually explore the neighbors of a neighbor
  even when this neighbor passes the filter.
  This is mostly unnecessary since its neighbors usually will be explored at some later point,
  but as the plot shows, it becomes negligible when more documents are filtered out.
* The area from 80% to 95% is where the plot really gets interesting:
  we avoid the spike in response time without a significant drop in recall.
  This is good and what we hoped for.
* When the filter gets too restrictive, in the area from 95% to 99%, the
  response time does stay low but at the cost of a significant drop in recall.
  What causes the recall to drop that much? The apparent explanation is that
  the subgraph induced by the filter gets so disconnected that even 2-hop neighbors are not enough.

So, what happens if we additionally explore 3-hop neighbors?

```
max_neighbors_to_find = max_links_for_level(level);

todo.push_back(node);

// Explore (1-hop) neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);

// Explore 2-hop neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);

// Explore 3-hop neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);
```

![Filter First: 3-Hop Neighbors](/assets/2025-09-04-additions-to-hnsw/filter-first-3-hops.svg)  
***Figure 5** Also exploring 3-hop neighbors across different filtering degrees*

This avoids the drop in recall, but causes a huge spike in response time.
With *max-links-per-node* set to the default value of 16, a node in lowest layer of the HNSW graph can have
up to *(2 ⋅ 16)³ = 32768* neighbors.
It certainly does not make sense to consider all these nodes as possible candidates
as the search gets way too undirected.
What happens when we instead only explore 3-hop neighborhoods if they are not *too large*?

```
max_neighbors_to_find = max_links_for_level(level);

todo.push_back(node);

// Explore (1-hop) neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);

// Explore 2-hop neighbors
exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);

// Explore 3-hop neighbors, but only if we have found only few 2-hop neighbors
if (todo.size() < exploration * (max_neighbors_to_find^2)) {
    exploreNeighborhoodByOneHop(todo, found, max_neighbors_to_find);
}
```

![Filter First: Exploration Parameter](/assets/2025-09-04-additions-to-hnsw/filter-first-exploration0.4.svg)  
***Figure 6** Finding the right balance of when to explore 3-hop neighborhoods*

The parameter *exploration* controls when 3-hop neighborhoods are explored.
As the plot shows, this parameter actually allows one to finely control the trade-off between
response time and recall.
This parameter is exposed in Vespa via the
[rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) parameter/[query API](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching) parameter

* **filter-first-exploration**/**ranking.matching.filterFirstExploration** - default 0.30.

To make use of this new search strategy for HNSW in Vespa, one has to adjust the
[rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) parameter/[query API](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching) parameter

* **filter-first-threshold**/**ranking.matching.filterFirstThreshold** - default 0.00.

This strategy is used when the hit ratio of the given filter is below *filter-first-threshold*, i.e.,
it is disabled by default for now.
We plan to adjust the default values of these parameters at some point in the future
such that ACORN-1 is enabled by default and the fallback to an exact search occurs later.
See the guide in the companion blog post for more details on how to set this and similar parameters in Vespa.
With tweaked ACORN-1 parameters and an adjusted fallback to an exact search, a comparison to the default settings looks as follows:
![ANN: Tweaked *filter-first-exploration*](/assets/2025-09-04-additions-to-hnsw/tweaked.svg)  
***Figure 7** Default vs. tweaked behavior for ANN*

That is roughly a 4-times increase of the number of queries per second at the cost of a manageable dip in recall around
the 95%-mark.
On other datasets, the improvement was large, but not that large.
On this data set, HNSW with pre-filtering
(without ACORN-1) performs really badly while ACORN-1 works really well:
Since the filters are chosen at random, the documents chosen by the filters are spread
out evenly in the graph.
That is, there is no correlation of a filter to the query.
If, however, we have positive correlation, i.e., the query vector
leads to a region of the graph where most documents pass the filter,
then there will not be much of a difference
between these two strategies.
Conversely, it will be interesting to observe how ACORN-1 behaves when
there is a negative correlation, i.e., the query vector leads
away from the region of the graph where most documents pass the filter.
Here, the expected outcome is that HNSW with pre-filtering works poorly
in terms of response time and ACORN-1 poorly in terms of recall.
Determining how the actual behavior of ACORN-1 in these cases is and how to
improve it is something that we have to work on in the future.

#### Comparison to Other Implementations and Ideas for the Future

The implementation of ACORN-1 in Vespa outlined above is kept as simple as possible.
Nevertheless, it leads to an enormous improvement of filtered ANN search.
How can it be improved further?
To inspire new ideas, it is always valuable to research what experience others have made
with ACORN-1.

In their blog post, [Weaviate](https://weaviate.io/blog/speed-up-filtered-vector-search)
share their experiences of implementing ACORN-1.
They stick to the original HNSW graphs just as we do.
An interesting improvement in their implementation is to
seed additional entry points for the HNSW graphs.
Having multiple entry points increases the chance of having an entry
point that passes the filter, which then helps with
queries that have negative correlation to the filter, i.e.,
the query leads to a region of the graph where nearly no vertices at all pass the filter.
This is actually a very important point as benchmarks (like in this very blog post)
often use uncorrelated queries and filters, which present the best case for
ACORN-1 but might not represent reality.
Vespa implements the original form of HNSW with only one entry point
and uses ACORN-1 only on the lowest layer of the HNSW index.
It would be interesting to see by how much this improves things and
whether the sparsity of the upper layers is a problem.

Just as Vespa, [Lucene](https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search),
uses the original HNSW index
and the ACORN-1-inspired heuristic only on the lowest layer of the graph.
The main difference is that they have more advanced heuristics for when to
explore *n*-hop neighbors for larger values of *n*.
If, for example, enough neighbor nodes pass the filter, they explore just the immediate neighborhood.
They saw a huge improvement in the number of queries per second by a factor 3.5
in their [nightly benchmark](https://benchmarks.mikemccandless.com/PreFilteredVectorSearch.html), where they employ a filter
that only lets 5% of documents pass.
Also we have experimented with more advanced heuristics deciding when to explore
extended neighborhoods and when not to. However, we found that the simple implementation
presented above already works really well, and the more advanced heuristics we tried complicated
things without a clear benefit.
As seen above, we see a similar increase when using 1 million
vectors from the data set used in their nightly benchmarks.
In the nightly Lucene benchmark, they use not 1 but 8 million vectors.
Regular testing on such large datasets is something that we definitely have to
and will incorporate into our performance tests in the future.

## Adaptive Beam Search

While using HNSW for ANN works well in practice, both in terms of response time
and recall, it does not guarantee anything about the recall of the returned vectors,
i.e., how many of the *k* returned vectors actually are among the true *k* nearest neighbors.
The search might get stuck in a local minimum, e.g., when there are a lot of nodes
with similar vectors, and return vectors that are nowhere near the true *k* nearest neighbors.
The usual way to work against this is to increase the number of target hits and
then to ignore the additional results: searching
for more hits means that the queue of candidates does not get saturated as quickly,
leading to exploration of a larger part of the graph.
In Vespa, this can be done either directly or by using the
[*hnsw.exploreAdditionalHits*](https://docs.vespa.ai/en/reference/query-language-reference.html#hnsw-exploreadditionalhits) annotation.
The following plot shows how large the effect of increasing this is when querying for 10 hits,
where we used 1 million vectors from the
[1M SIFT (128 dim) data set](http://corpus-texmex.irisa.fr/) this time.

![Effect of increasing exploreAdditionalHits](/assets/2025-09-04-additions-to-hnsw/recall_by_extended_hits.svg)  
***Figure 8** Effect of increasing exploreAdditionalHits when querying for 10 hits (without filters)*

A recent
[paper](https://arxiv.org/abs/2505.15636)
suggests that a distance-based termination condition in HNSW,
where a given slack parameter delays the termination,
can actually be advantageous over simply increasing the number of target hits and,
when averaged over a set of queries, yields comparable
recall with fewer distance computations.
They prove that this termination on graphs that they call *navigable*,
a property that guarantees that a greedy search will not get stuck in local minima,
yields a bound on the quality of the returned vectors.
While HNSW graphs are, in general, not navigable,
this nevertheless is a strong indication that using this termination condition in HNSW
actually is meaningful.
They demonstrate in their experiments that this modification of HNSW allows
to achieve the same recall with fewer visited notes when compared to just searching
for more hits.

As emphasized in the paper,
implementing the termination condition into an existing HNSW implementation essentially
boils down to changing a single line in the code. To allow for experimentation
with adaptive beam search, we have implemented it into Vespa and exposed
the slack parameter as the
[rank profile](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile) parameter/[query API](https://docs.vespa.ai/en/reference/query-api-reference.html#ranking.matching) parameter

* **exploration-slack**/**ranking.matching.explorationSlack** - default 0.00.

The following plot shows that increasing this parameter does indeed improve the recall.

![Effect of increasing exploration-slack](/assets/2025-09-04-additions-to-hnsw/recall_by_slack.svg)  
***Figure 9** Effect of increasing exploration-slack when querying for 10 hits (without filters)*

Note that, even though no filters were used to obtain this plot, adaptive beam search can also be combined
with ACORN-1.
Both increasing this slack parameter and increasing the number of target hits via *exploreAdditionalHits* comes at the cost of a higher response time.
When comparing the response times obtained for our small experiment with 10 target hits, we observe that adaptive beam search does in fact compare favorably,
allowing us to achieve the same recall at a lower response time.

![*exploration-slack* vs *exploreAdditionalHits*](/assets/2025-09-04-additions-to-hnsw/slack.svg)  
***Figure 10** exploreAdditionalHits vs. exploration-slack*

It is only a slight improvement, and whether we get an improvement at all depends
on the data set. On the
[1M SIFT (128 dim) data set](http://corpus-texmex.irisa.fr/)
used in this experiment, we saw an improvement,
while we did not on the data set used in the previous section on ACORN-1.
Hence, this is something the user has to find out for their specific data set.

## Read more

[![A Short Guide to Tweaking Vespa's ANN Parameters](/assets/2025-09-04-tweaking-ann-parameters/nina-mercado-e9YFrEBWit8-unsplash.jpg)

Photo by [Nina Mercado](https://unsplash.com/@nina_mercado?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash) on [Unsplash](https://unsplash.com/photos/brown-and-gray-metal-tools-e9YFrEBWit8?utm_content=creditCopyText&utm_medium=referral&utm_source=unsplash)](/tweaking-ann-parameters/)
[## A Short Guide to Tweaking Vespa's ANN Parameters

#### This a companion post to the previous technical blog post, explaining how to tweak Vespa's ANN parameters.](/tweaking-ann-parameters/)

[![Query Time Constrained Approximate Nearest Neighbor Search](/assets/2022-05-09-constrained-approximate-nearest-neighbor-search/christopher-burns-Kj2SaNHG-hg-unsplash.jpg)

Photo by [Christopher Burns](https://unsplash.com/@christopher__burns?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/photos/Kj2SaNHG-hg?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)](/constrained-approximate-nearest-neighbor-search/)
[## Query Time Constrained Approximate Nearest Neighbor Search

#### This blog post describes Vespa's industry leading support for combining approximate nearest neighbor search, or vector search, with query constraints to solve real-world search and recommendation problems at scale.](/constrained-approximate-nearest-neighbor-search/)

[![Approximate Nearest Neighbor Search in Vespa - Part 1](/assets/2020-06-30-approximate-nearest-neighbor-search-in-vespa-part-1/search-throughput-sift.png)](/approximate-nearest-neighbor-search-in-vespa-part-1/)
[## Approximate Nearest Neighbor Search in Vespa - Part 1

#### In this blog post we explore how the Vespa team selected HNSW (Hierarchical Navigable Small World Graphs) as the baseline approximate nearest neighbor algorithm for extension and integration in Vespa....](/approximate-nearest-neighbor-search-in-vespa-part-1/)

[« Case study: Using Vespa Cloud Resource Suggestions to optimize costs](/using-vespa-cloud-resource-suggestions-to-optimize-costs/)
[A Short Guide to Tweaking Vespa's ANN Parameters »](/tweaking-ann-parameters/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)