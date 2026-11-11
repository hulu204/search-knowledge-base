---
title: 'Result diversification using Vespa result grouping'
company: Vespa
tag: 排序
date: 2021-11-11
url: https://blog.vespa.ai/result-diversification-with-vespa/
account: 
origin: harvest3-202607
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Jo Kristian Bergum](/assets/avatars/jobergum.jpg)

[Jo Kristian Bergum](/authors/jobergum/ "Jo Kristian Bergum")
[Follow](https://twitter.com/jobergum)
  
Chief Scientist

11 Nov 2021

# Result diversification using Vespa result grouping

![Decorative
image](/assets/2021-11-11-result-diversification-with-vespa/robert-lukeman-_RBcxo9AU-U-unsplash.jpg)

Photo by [Robert
Lukeman](https://unsplash.com/@robertlukeman?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText) on [Unsplash](https://unsplash.com/s/photos/nature?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText)

Result diversification is a broad topic, and this blog post only scratches the surface of
the problem. One might classify result diversification as a multi-objective list optimization
problem. Conceptually, the core search or recommendation ranking function produces a ranked list of documents
scored on a per-document basis. On the other hand, diversification looks at the overall list of ranked
documents. From a high level perspective, the diversity constraints could be expressed as a
similarity function which re-order or remove similar matches to obtain an
ordering that optimizes variety. This post does not cover query intent diversification where
query specification is ambiguous and where the engine might show different types of results based on most probable query intents.

# Life of a query in Vespa

Before getting into the details on result diversification with
Vespa, one needs to have a basic understanding of the distributed query execution in
Vespa. For a query request that asks for a list of 100 best-ranking hits, the Vespa
stateless container layer will fan out the query to the content nodes. Each content node
produces a locally ranked list of top 100 *hits* out of potentially hundreds of millions of
documents *matching* the query specification. The stateless layer
merges the top 100 ranking *matches* from
all the content nodes and retains the global 100 top-ranking hits.
The number of hits that are returned is controlled by the
[hits](https://docs.vespa.ai/en/reference/query-api-reference.html#hits)
or the [YQL limit](https://docs.vespa.ai/en/reference/query-language-reference.html#limit-offset) parameter.
See also [Vespa search sizing](https://docs.vespa.ai/en/performance/sizing-search.html)
for more details on Vespa query execution and scaling Vespa deployments.

In the following sections, a differentiation is made between between *hits* and
*matches*, where
matches are documents that match the query formulation. *Hits* are a typically a small subset of the
matches that are surfaced to the stateless search container.

# Introducing Vespa Grouping Language

The [Vespa grouping language](https://docs.vespa.ai/en/grouping.html) is a list processing
language that describes how the query
*matches* should be grouped, aggregated, and presented in results as *hits*. A grouping
statement takes the list of all *matches* to a query as input and groups/aggregates it,
possibly in multiple nested and parallel ways to produce the result output.

The Vespa grouping list processing language runs over matches selected by the query formulation,
supporting matches retrieved by traditional query filters, keywords, and nearest neighbor
search. Thus, the Vespa grouping framework allows building rich search experience result
pages with facets and list diversification irrespective of the query retrieval method.

# Using Vespa Grouping Language

The following [YQL](https://docs.vespa.ai/en/reference/query-language-reference.html) query
asks for ten best ranking *hits* from a *doc* document type
[ranked](https://docs.vespa.ai/en/ranking.html) by the default ranking profile:

```
select * from doc where userQuery() limit 10;
```

The list of *hits* is not diversified in any way, just a flat list
of ten top ranking hits out of possible millions of *matches* out of possible billions of
documents in the index.

In the first example of using Vespa grouping language, one can imagine there has been an
offline process which have categorized documents
into a predefined *category*, uniquely identified by a numeric identifier.

```
schema doc {
  document doc {
    field title type string {..}
    field category type int {
      indexing: summary | attribute
    }
    field doc_embedding type tensor<int8>(x[128]) {}
  }
  rank-profile default inherits default {
    first-phase { expression { .. }} 
  }
  document-summary short {
    summary title type string {
      source: title
    }
  }
}
```

Fields used in grouping expressions must be declared with [attribute](https://docs.vespa.ai/en/attributes.html).

The following [YQL](https://docs.vespa.ai/en/query-language.html) query
groups results for a *userQuery()* by *category*.

```
select * from doc where userQuery() limit 10 | all(group(category) max(10)
each(max(2) each(output(summary(short)))));
```

The above query and grouping specification groups all matches
by the category field. The undiversified ranked list of ten hits are
retained in the result set when using *limit 10*.
The hits from the diversified result set is emitted
by the *each(output(summary()))* expression.

To remove the un-diversified ranked list use *limit 0*:

```
select * from doc where userQuery() limit 0 | all(group(category) max(10)
each(max(2) each(output(summary(short)))));
```

Groups are by default sorted by the maximum hit relevancy score within the
group. The outer *max(10)* controls the maximum number of groups
returned. In
addition, the two highest-ranking hits (*max(2)*) is emitted for each of the
unique groups, in this case, categories.
The Vespa grouping API supports [pagination](https://docs.vespa.ai/en/grouping.html#pagination)
using continuation tokens.
In the above example, the grouping expression used a single document attribute, it is also
possible to group by expressions. See the [grouping
reference](https://docs.vespa.ai/en/reference/querying/grouping-language.html) documentation.
In the below example the group identifier is a concatenation of category and brand:

```
all(group(cat(category,brand)) max(10)
each(max(2) each(output(summary(short)))));
```

### Dense retrieval with nearest neighbor search

Result grouping is also supported when using dense retrieval with the
[nearest neighbor search query
operator](https://docs.vespa.ai/en/nearest-neighbor-search.html):

```
select * from doc where
([{"targetHits":100}]nearestNeighbor(doc_embedding,query_embedding)) limit 0 |
all(group(journal) max(10) each(max(2) each(output(summary(short)))));
```

In the dense retrieval case, using the (approximate) nearest neighbor search operator,
the number of *matches* exposed to grouping is limited by the *targetHits*.
This behavior is due to the nature of the
approximate nearest neighbor search. There is no clear separation between a
*match* or no-match like with sparse term-based query retrieval.

# Controlling group ordering

The default
[ordering](https://docs.vespa.ai/en/grouping.html#ordering-and-limiting-groups)
of groups is, as mentioned, the maximum relevance score of the hits in the group.

```
all(group(category) max(10) each(max(1) each(output(summary(short)))))
```

Is the equivalent of

```
all(group(category) order(-max(relevance())) max(10) each(max(1)
each(output(summary(short)))))
```

The *-* denotes descending sort order.

It is possible to order groups by more complex expressions working on
*match* aggregates like *sum()* and *count()*, for example:

* Number of *matches* in the group times the maximum relevance:
  *order(-max(relevance())\*count())*
* The sum of a document attribute times the
  maximum relevance *order(-max(relevance())\*sum(ctr))*

# Fine-tuning result diversification with phased execution

The grouping examples in previous sections
are using “bucketing” as the diversity similarity
function. The advantage of group bucketing is scalability. It is fast to compute globally over many nodes,
over many matches. The downside is that the expressiveness of the diversity similarity function is limited.

Once the grouped result *hits* have been computed in parallel over all content nodes,
the resulting *hits* can be post-processed using a more complex diversity similarity function. At
the post processing stage the potential large number of matches have been reduced to lists of top ranked hits. Therefore,
the diversity similarity function can use a richer set of features and compute complexity.

This type of architecture is a phased or tiered architecture where the first phase selects
diverse “bucketed” candidates efficiently over potentially a large number of matches and
the subsequent phases post processes the results using a more complex diversity function:

* Vespa grouping language is used to fetch candidate documents which are diversified and
  ranked using bucketing.
* Post processing logic on the top result ranking lists from the parallel grouping execution and
  implements a more complex diversity similarity function

It is also considerably easier to implement custom business logic like “Never display more than four of type x for users of type z” in
the post processing stage. The downside of custom post-processing is that it complicates pagination support.

Post-processing diversity and business logic routines are best added by writing [stateless
searchers](https://docs.vespa.ai/en/applications/searchers.html), for example implementing
this [diversity algorithm](https://tech.ebayinc.com/engineering/diversity-in-search/).
Deploying the post processing logic in a searcher avoids network round trips and serialization and
de-serialization. The internal communication protocol between stateless and stateful Vespa nodes
is binary and is secured using mTLS so there is considerably less overhead doing round trips between
a stateless searcher component and the content nodes.

The custom searcher function can also build and process the grouping request and response programmatically, see
[Searcher grouping api](https://docs.vespa.ai/en/grouping.html#search-container-api).

# Serving performance

Four main components drive serving performance of query requests that
use Vespa result grouping. In order of importance:

* The number of matches the query produces per node. All the document matches
  get
  exposed to the grouping framework. The total result hit count of the query is
  equal to the number of *matches* exposed to grouping.
* The total number of unique values in the field.
* Ordering groups - using ordering expressions involving aggregates like count()
  or sum() is more resource-intensive than using the default max relevance order.
* Finally, the number of nodes involved in the query.

The query selection logic controls the number of *matches*.
Therefore, efficient
retrievers like [weakAnd/wand](https://docs.vespa.ai/en/using-wand-with-vespa.html)
or [approximate nearest neighbor
search](https://docs.vespa.ai/en/approximate-nn-hnsw.html)
expose fewer matches to ranking and grouping.
Thus, reducing the number of matches can improve the serving performance significantly and
also, enhance the quality of the groups as low-scoring documents are excluded from the
result grouping phase.
The grouping language also allows limiting the number of *matches* that are grouped.
For example, to limit the number of *matches* per node, use an

```
all(max(K) all(group(category) .... ))
```

In this expression, *K* is the maximum number of matches per
node that grouping runs over. Only top-K ranked from the matching and ranking phases
are considered.

It’s also possible to limit the number of *matches* exposed to grouping by using
the [match-phase
degradation](https://docs.vespa.ai/en/graceful-degradation.html#match-phase-degradation) ranking
feature. The *match-phase* limit sets an upper limit on the number of documents matched and ranked,
using a document side quality attribute. The match phase degradation feature supports diversity,
so that the matches exposed to grouping also are diversified. The *match-phase* diversification is
currently not supported for the approximate nearest neighbor search operator.

The number of unique values the field is data-dependent, fewer unique values is better.
The number of nodes in the cluster
to which the query is fanned out increases network bandwidth. The performance
impact could be mitigated using the
[precision](https://docs.vespa.ai/en/reference/querying/grouping-language.html#precision) parameter,
limiting the number of
unique groups returned to the stateless container nodes and reducing network bandwidth
usage.

# Summary

This blog post covered how to use Vespa result grouping to produce a mixed
result set for both search and recommendation use cases. As many search and recommendation
use cases it is best solved using a phased execution with gradually increasing complexity.

This post only covered
single-level grouping expressions.
However, the Vespa grouping framework also allows
running multi-level grouping. For
example, group by category, then by brand to further diversify the result.
For further reading, see [result
grouping](https://docs.vespa.ai/en/grouping.html) and
[result grouping
reference](https://docs.vespa.ai/en/reference/querying/grouping-language.html).

## Read more

[« Vespa Product Updates, September 2021](/vespa-product-updates-september-2021/)
[Vespa increases HTTP visiting throughput ten-fold or more »](/sliced-visiting/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)