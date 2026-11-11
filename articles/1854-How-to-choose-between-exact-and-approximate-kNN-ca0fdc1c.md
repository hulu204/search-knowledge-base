---
title: 'How to choose between exact and approximate kNN search in Elasticsearch'
company: Elastic
tag: 召回
date: 2024-05-20
url: https://www.elastic.co/search-labs/blog/knn-exact-vs-approximate-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How to choose between exact and approximate kNN search in Elasticsearch

Learn more about exact and approximate kNN search in Elasticsearch, and when to use each one.

May 20, 2024

[Carlos Delgado](/search-labs/author/carlos-delgado)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

## What is kNN?

[Semantic search](https://www.elastic.co/what-is/semantic-search) is a powerful tool for relevance ranking. It allows you to go beyond using just keywords, but consider the actual meaning of your documents and queries.

Semantic search is based on [vector search](https://www.elastic.co/what-is/vector-search). In vector search, the documents we want to search have [vector embeddings](https://www.elastic.co/what-is/vector-embedding) calculated for them. These embeddings are calculated using machine learning models, and returned as vectors that are stored alongside our document data.

When a query is performed, the same machine learning model is used to calculate the embeddings for the query text. Semantic search consists of finding the closest results to the query, by comparing the query embeddings to the document embeddings.

kNN, or [k nearest neighbors](https://en.wikipedia.org/wiki/K-nearest_neighbors_algorithm), is a technique for obtaining the top k closest results to a specific embedding.

There are two main approaches for calculating kNN for a query using embeddings: Exact and approximate. This post will help you:

* Understand what exact and approximate kNN search is
* How to prepare your index for these approaches
* How to decide which approach is best for your use case

## Exact kNN: Search everything

One approach for calculating the closer results would be comparing all the existing document embeddings with the one for the query. This would ensure that we're getting the closest matches possible, as we will be comparing all of them. Our search results would be as accurate as possible, as we're considering our whole document corpus and comparing all our document embeddings with the query embeddings.

Of course, comparing against all the documents has a downside: it takes time. We will be calculating the embeddings similarity one by one, using a similarity function, over all the documents. This also means that we will be scaling linearly - having twice the number of documents will potentially take twice as long.

Exact search can be done on vector fields using [script\_score with a vector function](https://www.elastic.co/guide/en/elasticsearch/reference/8.9/knn-search.html#exact-knn) for calculating similarity between vectors.

## Approximate kNN: A good estimate

A different approach is to use an approximation instead of considering all the documents. For providing an efficient approximation to kNN, Elasticsearch and Lucene use Hierarchical Navigation Small Worlds [HNSW](https://www.elastic.co/es/blog/introducing-approximate-nearest-neighbor-search-in-elasticsearch-8-0).

HNSW is a graph data structure that maintains links between elements that are close together, at different layers. Each layer contains elements that are connected, and are also connected to elements of the layer below it. Each layer contains more elements, with the bottom layer containing all the elements.

![HNSW overview](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd495779fe61c872a/6a17d85ab1e1133df079f0fe/197e96fa2d234954ee843c7859cfdcb0637d09dd-960x540.jpg)

Figure 1 - An example of a HNSW graph. The top layer contains the initial nodes to start the search. These initial nodes serve as entry points to the lower layers, each containing more nodes. The lower layer contains all nodes.

Think of it as driving; there are highways, roads and streets. When driving on a highway you will see some exit signs that describe some high-level areas (like a town or a neighborhood). Then you get to a road that has directions for specific streets. Once you get to a street, you can reach a specific address and the ones that are in the same neighborhood.

HNSW is similar to that, as it creates different levels of vector embeddings. It calculates the highway that is closer to the initial query, and chooses the exits that look more promising to keep looking for the closer addresses to the one we're looking for. This is great in terms of performance, as it doesn't have to consider all documents, but uses this multi-level approach to quickly find an approximation of the closer ones.

But, it's an approximation. Not all nodes are interconnected, meaning that it's possible to overlook results that are closer to specific nodes as they might not be connected. The interconnection of the nodes depends on how the HNSW structure is created.

How good HNSW is depends on several factors:

* How it is constructed. The HNSW construction process will consider a number of candidates to track as the closer ones to a specific node. Increasing the number of candidates to consider will produce a more precise structure, at the cost of spending more time creating it at indexing time. The `ef_construction` parameter in the [dense vector index\_options](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html#dense-vector-params) is used for this.
* How many candidates we're considering when searching. When looking for the closer results, the process will keep track of a number of candidates. The bigger this number is, the more precise it will be, and the slower our search will be. The `num_candidates` in [kNN parameters](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#tune-approximate-knn-for-speed-accuracy) controls this behavior.
* How many segments we're searching. Each segment has a HNSW graph that needs to be searched for, and its results combined with the other segment graphs. Having fewer segments will mean searching fewer graphs (so it'll be faster), but will have a less diverse set of results (so it will be less precise).

Overall, HNSW offers a good tradeoff between performance and recall, and allows fine tuning both at indexing and query side.

Searching using HNSW can be done using the [kNN search section](https://www.elastic.co/guide/en/elasticsearch/reference/8.9/knn-search.html#semantic-search) in most of the situations. Using a [kNN query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html) is also possible for more advanced use cases, like:

* Combining kNN with other queries (as part of bool queries, or pinned queries)
* Using `function_score` to fine tune the scoring
* Improve aggregations and field collapse diversity

You can check about kNN query and the differences to the kNN search section in [this post](https://www.elastic.co/search-labs/blog/knn-query-elasticsearch). We'll dive into when you'll want to use this method versus the others below.

## Indexing for exact and approximate search

### dense\_vector field type

There are two main indexing types for dense\_vector fields you can choose from for storing your embeddings:

* **flat** types (including *flat* and *int8\_flat*) store the raw vectors, without adding HNSW data structures. dense\_vectors that use flat indexing type will always use exact kNN - the kNN query will actually perform an exact query instead of an approximate one.
* **HNSW** types (including *hnsw* and *int8\_hnsw*) create the HNSW data structure, allowing approximate kNN search to be used.

Does it mean that you can't use exact kNN with HNSW field types? Not really! You can use both exact kNN via a [*script\_score query*](https://www.elastic.co/guide/en/elasticsearch/reference/8.9/knn-search.html#exact-knn), or use approximate kNN via the [*kNN section*](https://www.elastic.co/guide/en/elasticsearch/reference/8.9/knn-search.html#semantic-search) and the [*kNN query*](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html). This allows more flexibility depending on your search use case.

Using HNSW field types means that the HNSW graph structure needs to be built, and that takes time, [memory](https://www.elastic.co/guide/en/elasticsearch/reference/8.9/tune-knn-search.html#_ensure_data_nodes_have_enough_memory) and disk space. If you'll just be using exact search, you can use the flat vector field type. This ensures that your embeddings are indexed optimally and use less space.

Remember to always [avoid storing your embeddings in \_source](https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-knn-search.html#_exclude_vector_fields_from_source) in any case, to reduce your storage needs.

### Quantization

Using [quantization](https://www.elastic.co/search-labs/blog/scalar-quantization-101), either flat (int8\_flat) or HNSW (int8\_hnsw) types of indexing will help you reduce your embeddings size, so you will be able to use less memory and disk storage for holding your embeddings information.

As search performance relies on your embeddings fitting as much as possible in memory, you should always look for ways of reducing your data if possible. Using quantization is a trade off between memory and recall.

## How do I choose between exact and approximate kNN search?

There's no one-size-fits-all answer here. You need to consider a number of factors, and experiment, in order to get to the optimal balance between performance and accuracy:

### Data size

Searching everything is not something you should avoid at all costs. Depending on your data size (in terms of number of documents and embedding dimensions), it might make sense to do an exact kNN search.

As a rule of thumb, having less than 10 thousand documents to search could be an indication that exact search should be used. Keep in mind that the number of documents to search can be filtered in advance, so the effective number of documents to search can be restricted by the filters applied.

Approximate search scales better in terms of the number of documents, so it should be the way to go if you're having a big number of documents to search, or expect it to increase significantly.

![Exact vs approximate kNN benchmark](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7746637ec0736661/6a17d85b1d1b83e58793e2f0/33c8b5a4584c6a4ae35032b6e9678b78a6121f69-723x420.png)

Figure 2 - an example run of exact and approximate kNN using 768 dimensions vectors from the [so\_vector rally track](https://github.com/elastic/rally-tracks/tree/master/so_vector). The example demonstrates the linear runtime of exact kNN vs the logarithmic runtime of HNSW searches.

### Filtering

Filtering is important, as it reduces the number of documents to consider for searching. This needs to be taken into account when deciding on using exact vs approximate. You can use [**query filters**](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-filter-context.html) for reducing the number of documents to consider, both for exact and approximate search.

However, approximate search takes a different approach for filtering. When doing approximate searches using HNSW, query filters will be applied *after* the top k results have been retrieved. That's why using a query filter along with a kNN query is referred to as a [**post-filter**](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html#knn-query-filtering) **for kNN**.

![Post filtering in kNN](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte9bc1f03f1d516aa/6a17d85d4b055d1579432067/9d0dcb10eb496a19c304d6d2e57372cff5e2cbf9-956x266.jpg)

Figure 3 - Post-filtering in kNN search.

The problem with using post-filters in kNN is that the filter is being applied *after* we have gathered the top k results. This means that we can end up with less than k results, as we need to remove the elements that don't pass the filter from the top k results that we've already retrieved from the HNSW graph.

Fortunately, there is another approach to use with kNN, and is specifying a filter in the kNN query itself. This filter applies to the graph elements as the results are being gathered traversing the HNSW graph, instead of applying it afterwards. This ensures that the top k elements are returned, as the graph will be traversed - skipping the elements that don't pass the filter - until we get the top k elements.

![Pre filtering in kNN](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9f94afd652ab7740/6a17d85efaa913b0ca93c6f6/44170f49b2ab4d5d783690a10f046a217957c02b-777x280.jpg)

Figure 4 - Pre-filtering in kNN search.

This specific kNN query filter is called a **kNN** [**pre-filter**](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-knn-query.html#knn-query-filtering) to specify that it is applied *before* retrieving results, as opposed to applying it afterwards. That's why, in the context of using a kNN query, regular query filters are referred to as post-filters.

Using a kNN pre-filter affects approximate search performance, as we need to consider more elements while searching in the HNSW graph - we will be discarding the elements that don't pass the filter, so we need to look for more elements on each search to retrieve the same number of results.

## Future enhancements for kNN

There are some improvements that are coming soon that will help with exact and approximate kNN.

Elasticsearch will add the possibility to **upgrade a dense\_vector type** from flat to HNSW. This means that you'll be able to start using a flat vector type for exact kNN, and eventually start using HNSW when you need the scale. Your segments will be searched transparently for you when using approximate kNN, and will be transformed automatically to HNSW when they are merged together.

A **new exact kNN query** will be added so a simple query will be used to do exact kNN for both flat and HNSW fields, instead of relying on a script score query. This will make exact kNN more straightforward.

## Conclusion

So, should you use approximate or exact kNN on your documents? Check the following:

* How many documents? Less than 10 thousand (after applying filters) would probably be a good case for exact.
* Are your searches using filters? This impacts how many documents will be searched. If you need to use approximate kNN, remember to use kNN pre-filters to get more results at the expense of performance.

You can compare the performance of both approaches by indexing using a HNSW dense\_vector, and comparing kNN search against a script\_score for doing exact kNN. This allows comparing both methods using the same field type (just remember to change your dense\_vector field type to flat in case you decide to go for exact search!)

Happy searching!

### Frequently Asked Questions

#### How to choose between exact and approximate kNN search in Elasticsearch?

Having less than 10 thousand documents to search could be an indication that exact search should be used. Approximate search scales better in terms of the number of documents, so it should be the preferred choice if you have a big number of documents or expect it to grow significantly.

#### What is the difference between exact and approximate kNN search?

Exact kNN calculates the closer results by comparing all the existing document embeddings with the one for the query, ensuring accuracy but requiring more time. In contrast, approximate kNN provides an efficient approximation to kNN.

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