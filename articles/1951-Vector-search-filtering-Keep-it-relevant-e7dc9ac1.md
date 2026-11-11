---
title: 'Vector search filtering: Keep it relevant'
company: Elastic
tag: 召回
date: 2025-09-03
url: https://www.elastic.co/search-labs/blog/vector-search-filtering
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Vector search filtering: Keep it relevant

Performing vector search to find the most similar results to a query is not enough. Filtering is often needed to narrow down search results. This article explains how filtering works for vector search in Elasticsearch and Apache Lucene.

September 03, 2025

[Carlos Delgado](/search-labs/author/carlos-delgado)

[Vector Database](/search-labs/blog/category/vector-database)[Lucene](/search-labs/blog/category/lucene)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Vector search is not enough to find relevant results. It's very common to use filtering criteria that will help narrow down search results and filter out irrelevant results.

Understanding how filtering works in vector search will help you balance the performance and recall tradeoffs, as well as discovering some of the optimizations used to make vector search performant when filtering is used.

## Why filtering?

Vector search has revolutionized how we find relevant information in large datasets, allowing us to discover items that are semantically similar to a query.

However, simply finding similar items isn't enough. We often need to narrow down the search results based on specific criteria or attributes.

Imagine you're searching for a product in an e-commerce store. A pure vector search might show you visually similar items, but you might also want to filter by price range, brand, availability, or customer ratings. Without filtering, you'd be presented with a vast array of similar products, making it difficult to find exactly what you're looking for.

Filtering enables precise control over the search results, ensuring that the retrieved items not only align semantically but also meet all the necessary requirements. This leads to a much more accurate, efficient, and user-friendly search experience.

This is where Elasticsearch and Apache Lucene excel—using effective filtering across various data types is one of the key differences with other vector databases.

## Filtering for exact vector search

There are two main ways of performing exact vector searches:

* Using a `flat` index type for your dense\_vector field. This makes `knn` searches use exact search instead of approximate.
* Using a [script\_score query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-script-score-query#vector-functions) that uses vector functions to calculate the score. This can be used with any index type.

When executing exact vector search, all vectors are compared to the query. In this scenario, filtering will help performance as only the vectors that pass the filter need to be compared.

This does not impact the result quality, as all vectors are considered anyway. We're just filtering in advance the results that are not interesting, so we can reduce the number of operations.

This is very important, as it can be more performant to execute an exact search instead of an approximate search when the applied filters result in a small number of documents.

The rule of thumb is to use exact search when fewer than 10k documents pass the filter. [BBQ](https://www.elastic.co/search-labs/blog/better-binary-quantization-lucene-elasticsearch) indices are much faster for comparisons, so it makes sense to use exact search when less than 100k for based indices. Check out [this blog post](https://www.elastic.co/search-labs/blog/knn-exact-vs-approximate-search) for more details.

In case your filters are always very restrictive, you may consider indexing focusing on exact search instead of approximate search by using a `flat` index type instead of an HNSW-based one. For more details, see [the properties of index\_options](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector#dense-vector-params).

## Filtering for approximate vector search

When executing approximate vector search, we trade result accuracy for performance. Vector search data structures like HNSW efficiently search for approximate nearest neighbors on millions of vectors. They focus on retrieving the most similar vectors by doing the least amount of vector comparisons, which are expensive to calculate.

This means that other filtering attributes are not part of the vector data. Different data types have their own indexing structures that are efficient for finding and filtering them, like terms dictionaries, posting lists and doc values.

Given that these data structures are separate from the vector search mechanism, how do we apply filtering to vector search? There are two options: applying filters after vector search (postfiltering) or before vector search (prefiltering).

Each of those options has pros and cons. Let's dive deeper into them!

### Postfiltering

Postfiltering applies filters after vector search has been done. This means that filters are applied after the top k most similar vector results have been found.

Obviously, we can potentially get less than k results after applying the filters to the results. We could of course retrieve more results from vector search (higher k value), but we won't be sure that we'll be getting k or more after applying the filters.

Postfiltering’s advantage is that it doesn't change the runtime behaviour of vector search—vector search is unaware of filtering. But, it does change the final number of results retrieved.

The following is an example of postfiltering using the [knn query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query). Check that the filtering clause is separate from the knn query:

```
{
  "query": {
    "bool": {
      "must": {
        "knn": {
          "field": "image-vector",
          "query_vector": [54, 10, -2],
          "k": 5,
          "num_candidates": 50
        }
      },
      "filter": {
        "term": {
          "file-type": "png"
        }
      }
    }
  }
}
```

Postfiltering is also available for the knn search using [post-filter](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/filter-search-results#post-filter):

```
{
  "knn": {
    "field": "image-vector",
    "query_vector": [54, 10, 2],
    "k": 5,
    "num_candidates": 50
  },
  "post_filter": {
    "term": {
      "file-type": "png"
    }
  }
}
```

Keep in mind that you need to use an explicit post-filter section with the knn search. If you don't use a post-filter, knn search [will combine nearest neighbors results](https://www.elastic.co/docs/solutions/search/vector/knn#_combine_approximate_knn_with_other_features) with other queries or filters instead of doing a post filter.

### Prefiltering

Applying filters before the vector search will first retrieve the documents that satisfy the filters, and then pass down that information to the vector search.

Lucene uses [BitSets](https://github.com/apache/lucene/blob/7a60d7ce92392181e137361336e5196bd486cdd9/lucene/core/src/java/org/apache/lucene/util/BitSet.java) to efficiently store the documents that satisfy the filter condition. Vector search then traverses the HNSW graph, taking into account the documents that satisfy the condition. Before adding a candidate to the results, it checks that it's contained in the BitSet of valid documents.

However, the candidate must be explored and compared to the query, even if it's not a valid document. The effectiveness of HNSW relies on the connection between the vectors in the graph—if we stopped exploring a candidate, it would mean that we could be skipping its neighbors as well.

Think of it as driving to get to a gas station. If you discard any roads that don't have a gas station on them, it's improbable that you'll get to your destination. Other roads may not be what you need, but they *connect* you to your destination. Same with vectors on an HNSW graph!

So it follows that applying prefiltering is less performant than not applying filters. We need to do the work on *all* the vectors we visit in our search, and we need to throw away the ones that don't match the filter. We're doing more work and taking more time to get our top k results.

The following is an example of pretfiltering in the Elasticsearch Query DSL. Check that the filtering clause is now part of the knn section:

```
{
  "knn": {
    "field": "image-vector",
    "query_vector": [54, 10, -2],
    "k": 5,
    "num_candidates": 50,
    "filter": {
      "term": {
        "file-type": "png"
      }
    }
  }
}
```

Prefiltering is available for both [knn search](https://www.elastic.co/docs/solutions/search/vector/knn#knn-search-filter-example) and [knn query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-knn-query#knn-query-filtering):

```
{
  "query": {
    "knn": {
      "field": "image-vector",
      "query_vector": [-5, 9, -12],
      "k": 5,
      "filter": {
        "term": {
          "file-type": "png"
        }
      }
    }
  }
}
```

#### Prefiltering optimizations

There are a couple of optimizations that we can apply to ensure prefiltering is performant.

We can switch to exact search if the filter is very restrictive. When there are few vectors to compare, it's faster to perform an exact search on the few documents that satisfy the filter.

This is an optimization that is applied automatically in [Lucene](https://github.com/apache/lucene/blob/eb876b618da5d04c1ad14b04a48321638318493a/lucene/core/src/java/org/apache/lucene/search/AbstractKnnVectorQuery.java#L218) and Elasticsearch.

Another optimization method involves disregarding the vectors that do not satisfy the filter. Instead, this method checks neighbors of the filtered vectors that do pass the filter. This approach effectively reduces the number of comparisons as the filtered vectors are not considered, and continues to explore vectors connected to the current path.

This algorithm is ACORN-1, and the process is described in detail in [this blog post](https://www.elastic.co/search-labs/blog/filtered-hnsw-knn-search).

## Filtering using Document Level Security

[Document Level Security (DLS)](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/controlling-access-at-document-field-level#document-level-security) is an Elasticsearch feature that specifies the documents that user roles can retrieve.

DLS is performed using queries. A role can have a query associated with indices, which effectively limits the documents that a user who belongs to that role can retrieve from the indices.

The role query is used as a filter to [retrieve the documents that match it](https://github.com/elastic/elasticsearch/blob/c3a1cb34294e902a9f46d7e840ea09965019f456/x-pack/plugin/core/src/main/java/org/elasticsearch/xpack/core/security/authz/accesscontrol/SecurityIndexReaderWrapper.java#L92), and are cached as a BitSet. This BitSet is then used to wrap the underlying Lucene reader, so only the documents that were returned from the query are considered *live—*that is, they exist on the index and have not been deleted.

As the live documents are [retrieved from the reader](https://github.com/apache/lucene/blob/a211d30097a8e3264d3ef073a054bd31eb847231/lucene/core/src/java/org/apache/lucene/search/AbstractKnnVectorQuery.java#L196) to perform the knn query, only the documents available to the user will be considered. If there is a prefilter, the DLS documents will be [added to it](https://github.com/apache/lucene/blob/a211d30097a8e3264d3ef073a054bd31eb847231/lucene/core/src/java/org/apache/lucene/search/AbstractKnnVectorQuery.java#L204).

This means that DLS filtering works as a prefilter for approximate vector search, with the same performance implications and optimizations.

DLS with exact search will have the same benefits as applying any filter—the fewer documents that are retrieved from DLS, the more performant an exact search will be. Consider as well the number of documents returned by DLS—if DLS roles are very restrictive, you may consider using exact search instead of approximate search.

## Benchmarking

At Elasticsearch, we want to make sure that vector search filtering is efficient. We have [a specific benchmark for vector filtering](https://elasticsearch-benchmarks.elastic.co/#tracks/so_vector/nightly/default/90d) that performs approximate vector searches with different filtering to ensure that vector search keeps retrieving relevant results as fast as possible.

Check the [improvements](https://elasticsearch-benchmark-analytics.elastic.co/app/dashboards#/view/43b63e80-5ba2-11ed-aede-a742809feed4?_g=(refreshInterval:(pause:!t,value:60000),time:(from:'2025-05-28T01:27:58.456Z',to:'2025-06-30T13:53:26.430Z'))&_a=()) when ACORN-1 was introduced. For tests where only 2% of the vectors pass the filter, query latency is reduced to 55% of the original duration:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt820cb0b715cf291c/6a17e227dbb4ff8d49fb5615/3eac3748a33376fc97d957364a5c1f5108d5c58b-1023x896.png)

## Conclusion

Filtering is an integral part of search. Ensuring that filtering is performant in vector search, and understanding the tradeoffs and optimizations, is what makes or breaks an efficient and accurate search.

Filtering impacts performance for vector search:

* Exact search is faster when using filtering. You should consider using exact search instead of approximate search if your filtering is restrictive enough. This is an automatic optimization in Elasticsearch.
* Approximate search is slower when using prefiltering. Prefiltering allows us to get the top k results that match the filter, at the cost of slower search.
* Postfiltering does not necessarily retrieve the top k results, as they may be filtered via the filter when it's applied.

Happy filtering!

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