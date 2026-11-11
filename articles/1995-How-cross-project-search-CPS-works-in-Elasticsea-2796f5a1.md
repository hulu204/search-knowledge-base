---
title: 'How cross-project search (CPS) works in Elasticsearch Serverless'
company: Elastic
tag: 工程相关
date: 2026-04-30
url: https://www.elastic.co/search-labs/blog/cross-project-search-elasticsearch-serverless
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How cross-project search (CPS) works in Elasticsearch Serverless

Elastic Cloud Serverless cross-project search (CPS) treats index expressions as cross-project by default. This post explains how TransportSearchAction scopes projects, resolves index expressions, skips projects with no matches, and validates index resolution against allow\_no\_indices and ignore\_unavailable.

April 30, 2026

[Matteo Piergiovanni](/search-labs/author/matteo-piergiovanni)[Pawan Kartik](/search-labs/author/pawan-kartik)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

With the introduction of cross-project search (CPS) in our Elastic Cloud Serverless offering, we wanted to provide our customers with a streamlined search experience. Our vision is for our users to not worry about which project the data is stored in but instead to focus on the information they want an answer for.

Users familiar with [cross-cluster search](https://www.elastic.co/docs/explore-analyze/cross-cluster-search) (CCS) know that to include a remote cluster in a search you must specifically reference it with a cluster alias prefix, such as `remote:metrics*` (or `*:metrics*` to target all remotes). With CPS, "bare" index names or patterns such as `metrics*` in a search index expression implicitly reference all instances of that index that can be found on the origin project and on all of its linked projects.

In this post, we pull back the curtains on how the Elasticsearch TransportSearchAction, the code that underlies the \_search API (and \_async\_search) APIs, determines which indices, aliases, and datastreams to search on which projects when running a cross-project search.

![How the Elasticsearch TransportSearchAction works](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt591412c6f782c796/6a17059b0c48574aa701a96e/9a7c9134b4509dab0dbe26def7e058c40562cfd5-2400x1350.webp)

## Analyzing index expressions

One important consequence of the new CPS model is that the Elasticsearch query parameters [`allow_no_indices`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search#operation-search-allow_no_indices) and [`ignore_unavailable`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search#operation-search-ignore_unavailable) require different handling than before. In general, these parameters control whether a search should throw an error if a concrete index name (for example, "logs") cannot be found or isn’t accessible (`ignore_unavailable=false`), or a wildcard pattern (for example, "logs\*") doesn’t match anything or if there are no indices at all to search (`allow_no_indices=false`).

In CCS, those parameters are analyzed on each cluster separately: Each cluster can just consult which indices, aliases, or data streams exist locally. But in CPS, we need to account for whether each resource (index, alias, or data stream) referenced by an index expression matches on *any* project (origin or linked), rather than *every* project.

To illustrate, suppose a user has one linked project (`linked1`) and they issue a cross-project query with index expression `logs*,metrics-1`, along with `allow_no_indices=false,ignore_unavailable=false`. As long as we find one resource (index, alias, or data stream) that matches `logs*` and one that matches `metrics-1` on any project, then the search can proceed. If metrics-1, for example, is found on linked1 but not the origin project, that suffices to pass the `ignore_unavailable=false` constraint. Only if it’s found nowhere would we throw an IndexNotFoundException.

To handle this, the \_search API in cross-project search mode needs to gather information from each linked project before kicking off the actual search.

The serverless node that receives the \_search REST request is considered to be the origin project, and it acts as the overall search coordinator. To fully analyze and process an index expression before kicking off the actual search, the search coordinator needs to:

1. Determine which projects are in scope for the search.
2. Determine which indices, aliases, or data streams should be searched in each individual project.
3. Do a final reconciliation step of all the information gathered: 1) Have we found all the indices required to proceed (as defined by the allow\_no\_indices and ignore\_unavailable settings)?; and 2) Are there any projects that should be skipped since they have no matching indices?

To illustrate, we’ll follow a CPS request against the \_search API from start to finish. Suppose that the incoming user request is to search `metrics*` and that the origin project has two indices which match the expression, namely `metrics-ES` and `metrics-KB`, and that the origin project is linked to projects `P1` and `P2`, where `P1` has index `metrics-ES` and `P2` has no index, alias, or data stream that matches `metrics*`.

## Determining projects in scope

The search coordinator starts by grabbing the full list of linked projects from Elasticsearch cluster state. It then determines, based on [Universal Identity and Access Management](https://www.elastic.co/docs/explore-analyze/cross-project-search#security) (UIAM) credentials provided with the query, which of those projects the user has access to and keeps the subset of projects that the user is allowed to access.

If a `project_routing` parameter is present on the request, that can further limit which projects are in scope for the query. For instance, `"project_routing":"_alias:_origin"` would cull the list to just the origin project, while `"project_routing":"_alias:P*"` would include the linked projects P1 and P2 and remove the origin project from the list of projects in scope for the query.

The index expression itself can also limit which projects to access. Qualified index expressions, like `"P*:metrics*",` would indicate that we should search only on projects whose alias starts with "P". For our case, the "bare" or unqualified index expression `"metrics*"` means "search on all projects that are in scope," where "in scope" is modified by security access and project\_routing.

## Determining which indices each project has

Once we know which projects to search, we need to determine which matching indices each one has. To support this, the search coordinator creates a `ResolvedIndexExpressions` data structure that allows tracking which indices on each project should be included in the search.

For each index expression provided by the user, that data structure tracks:

* Original expression: The index expression, as provided by the user.
* Local resolution: The local expressions that will replace the original together with the resolution result.
* Remote expressions: A set of remote expressions one for each project a query can target.

On the search coordinator that received the request, we’ve so far been able to determine which projects are in scope (origin, P1, and P2) and which, if any, matching indices exist on origin. So, for our example search against `metrics*`, we’ll have the following structure at that point in time:

* Original expression: `metrics*`.
* Local resolution: `SUCCESS`, `<metrics-ES, metrics-KB>`.
* Remote expressions: `<P1:metrics*, P2:metrics*>`.

The remote expressions are left unresolved until we later contact the P1 and P2 projects to fill in that information.

The index resolution can be any of the following:

* `SUCCESS`: Local resolution completed successfully.
* `NOT_VISIBLE`: Indicates that a non-wildcard expression was resolved to nothing, either because the index doesn’t exist or is closed.
* `UNAUTHORIZED`: Indicates that the expression could be resolved to a concrete index, but the requesting user isn’t authorized to access it.
* `NONE`: No local resolution was attempted, typically because the expression is remote-only (for example, `P1:index`).

## Check indices on the linked projects

In the search API, how we check for indices on the linked projects depends on whether the cross-project search is being run with [minimize round trips](https://www.elastic.co/docs/explore-analyze/cross-cluster-search#ccs-min-roundtrips-true) or not. Most searches in CPS are set internally to run with minimize\_roundtrips=true, so we’ll focus on that pathway.

In CCS, where index expression analysis is done locally on each cluster, we just send the same request to every cluster and, with minimize\_roundtrips=true, each remote cluster sends back an entire SearchResponse that the primary search coordinator collects and eventually merges into all the other responses it receives.

By contrast, for CPS, an additional phase was introduced to search where we contact each linked project to assess which indices are present and which ones the user has access to. This is an additional round trip that uses `ResolveIndexAction`, the class that implements the functionality of the [`_resolve/index`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-search#operation-search-ignore_unavailable) endpoint. Upon receiving the `ResolveIndex` responses from all the linked projects, we can fill in the ResolvedIndexExpressions data structure on the primary search coordinator. For this case, since `P1` has index `metrics-ES` and `P2` has no matching indices, the updated data structure would be:

* Original expression: `metrics*`.
* Local resolution: `SUCCESS`, `<metrics-ES, metrics-KB>`.
* Remote expressions: `<P1: SUCCESS <metrics-ES>, P2: NOT_VISIBLE>`.

## CPS validator

Once we have all the linked project information, we can run the validation to honor the `IndicesOptions` specified by the caller.

If the user had specified a qualified index expression (for example, original=`P1:metrics*`), the CPS validator needs to make sure that project `P1` has at least one index matching `metrics*`, otherwise a 404 index not found exception would be returned to the user. In other words, qualified expressions imply that an index, alias, or data stream matching that name must be present on all projects specified by the qualifier.

On the other hand, for “bare” (unqualified) CPS index expressions (for example, original=`metrics*`), we only need to check whether the original index expression exists anywhere.

For the example we’re following in this post, the ResolveIndexExpressions show that at least one index, alias, or data stream matching `metrics*` was found, so the search can proceed.

However, we can also see that the P2 cluster has no matching indices. In that case, we can remove it from the rest of the query. So now, for the actual query, we’ll:

* On the origin project, search `metrics-ES, metrics-KB`.
* On the `P1` project, search `metrics-ES`.
* Skip the `P2` project. Note: Since it wasn’t included in the query at all, it won’t show up on the [\_cluster/details](https://www.elastic.co/docs/explore-analyze/cross-project-search#cps-examples) of the SearchResponse.

## Conclusions

We’ve described how the TransportSearchAction class in Elasticsearch supports some key new features of cross-project search. That class supports a large number of Elasticsearch REST APIs, such as, \_search, \_async\_search, \_msearch, \_eql, \_sql and \_count, all of which use the mechanisms described in this document.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### How we optimized refresh costs in Elasticsearch Serverless

July 31, 2024|[Francisco Fernández Castaño](/search-labs/author/francisco-fernandez-castano)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltb2cd04a86700d5c2/6a17d715e3179138882d567d/016f5f2a90974dd53416d7d12f8776e802a0eef8-1440x823.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Ingest autoscaling in Elasticsearch

July 29, 2024|[Pooya Salehi](/search-labs/author/pooya-salehi)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3b371b70b12b9ef/6a170f240e2e49999441a1de/3c4c1e99b892f026b7aba098973593f8298e2ea6-1280x717.png)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Elasticsearch replicas for load balancing in Serverless

March 24, 2026|[Andrei Dan](/search-labs/author/andrei-dan)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt84da396c370b06ec/6a170cfa6234e00dd3db1a55/d92e2e9fbae1dca1f18e623b2f5eb2a835307130-1600x1066.jpg)

[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### Autosharding of data streams in Elasticsearch Serverless

December 10, 2024|[Andrei Dan](/search-labs/author/andrei-dan)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter