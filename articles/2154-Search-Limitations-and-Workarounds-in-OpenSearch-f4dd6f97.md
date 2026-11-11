---
title: 'Search Limitations and Workarounds in OpenSearch Sease -'
company: Sease
tag: 工程相关
date: 2025-07-14
url: https://sease.io/2025/07/limitations-and-workarounds-in-opensearch.html
account: 
origin: harvest3-202607
---
Hi there!

Over the past few months, we worked on a client project to build a web search engine from scratch. We have integrated features such as **hybrid search,** which combines keyword (lexical) search and vector (semantic) search, and **semantic highlighting**, where the highlighter relies on the meaning of the context. While building search systems, we encountered some challenges.   
We used OpenSearch v2.17, and this version posed several limitations. We had to engineer and tweak features that were not supported in the version. In this post, we would like to share some OpenSearch limitations that we have discovered in the project and provide their practical workarounds.

## Outline:

* Hybrid Search
  + Hybrid Query Limitations
  + Custom Implementation Workarounds
  + Native Support Introduced in OpenSearch v2.19
* Semantic Highlighting
  + Semantic Highlighting Limitation and Our Workaround
  + Native Support in OpenSearch v3.0
* Did-you-mean Suggester

## Hybrid Search

Why should we use Hybrid Search at all?  
In recent years, combining traditional keyword search with vector search, known as hybrid search, has become prevalent in modern search applications. This approach provides more relevant results by matching exact query terms and broader semantic meaning through vector embeddings.

##### Hybrid Query Limitations

Although OpenSearch began introducing hybrid search support in its v2.11 roadmap, later versions such as v2.17 still lacked several essential features needed to make hybrid search viable in production.   
One of the main hybrid search features – **pagination –** is still not supported as of the version. The hybrid query returns all results at once.   
Moreover, in order to merge documents that are matched, there are mainly two types: score-based normalisation and rank-based combination. The current [hybrid query](https://docs.opensearch.org/docs/2.17/query-dsl/compound/hybrid/) uses only score-based [min-max normalisation](https://en.wikipedia.org/wiki/Feature_scaling). In other words, the **rank-based combination technique**, Reciprocal Rank Fusion (RRF), is not incorporated within the neural search plugin. Besides those main points, when testing the hybrid query locally, we have observed several issues. Duplicate results with negative scores appear if the normaliser pipeline is not properly configured. In addition, to dive into how scores are calculated in a hybrid query, we tried to use the **explain functionality**, but the feature doesn’t fully support hybrid query.

##### Custom Implementation Workarounds

After experimenting and seeing the existing hybrid query limitations, we have decided to implement a custom hybrid search. We have taken a simple approach: use a multi-match query for traditional keyword search and a k-NN query for semantic search and fuse both results using the RRF technique. Let’s see a simplified code snippet:

```
				
					hybridSearch(String userQuery, int pageNumber, int pageSize) {
        var size = pageNumber * pageSize;
        var lexicalResults = lexicalSearch(userQuery, 0, size);
        var vectorResults = vectorSearch(userQuery, 0, size);

        var mergedResults = fuseResults(lexicalResults, vectorResults)
                                    .stream()
                                    .skip((long)(pageNumber - 1) * pageSize)
                                    .limit(pageSize)
                                    .toList();
        return mergedResults;
}
				
			
```

Here, to calculate how many total results to retrieve from each source (lexical and vector), we take **`pageNumber * pageSize`** that ensures you have enough items to skip previous pages and still get enough results for the current one. Once we have results from both searches, we combine the results using a custom RRF service. In the RRF service, we have `fuseResults` call, which takes both results and merges them based on the following formula:

For an item at the position **`i`**, the RRF score is:

```
				
					score = 1.0 / (K + i)
				
			
```

where **`i`** is the rank, the position of the document, and K is constant ([K=60](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf) magic number from the official paper).

The following snippet shows the simplified `fuseResults` method:

```
				
					fuseResults(&lt;T&gt; lexicalResults, &lt;T&gt; vectorResults) {
 return Stream
   .concat(
     range(0, lexicalResults.size())
       .mapToObj(i -&gt; Map.entry(lexicalResults.get(i), 1.0 / (K + i))),
     range(0, vectorResults.size())
       .mapToObj(i -&gt; Map.entry(vectorResults.get(i), 1.0 / (K + i))))
   .collect(groupingBy(Map.Entry::getKey,summingDouble(Map.Entry::getValue)))
   .entrySet()
   .stream()
   .sorted(Map.Entry.comparingByValue(reverseOrder()))
   .map(Map.Entry::getKey)
   .toList();
}
				
			
```

For each item in the lexical and vector result lists, we create a map of <item, score>, group duplicate items (same document appearing in both lists), and sum their scores. We finally sort by the total RRF score (descending) and return only the original result items (not their scores).

Now we have a fused list of results from **`fuseResults(...)`**. For pagination, we use Java Stream methods:

* **`skip(...)`** — to skip items belonging to previous pages, and
* **`limit(...)`** — to keep only the items for the current page.

This ensures that the final response contains exactly the subset of results corresponding to the requested **`pageNumber`** and **`pageSize`**.

##### Native Support Introduced in OpenSearch v2.19

In OpenSearch v2.19, significant improvements have been made within the hybrid search. In hybrid queries, the Reciprocal Rank Fusion ([RRF](https://opensearch.org/blog/introducing-reciprocal-rank-fusion-hybrid-search/)) normalisation technique is introduced [[PR](https://github.com/opensearch-project/neural-search/pull/874)].   
We define a search pipeline using the RRF technique:

```
				
					PUT /_search/pipeline/rrf-pipeline
{
  "description": "Post processor for hybrid RRF search",
  "phase_results_processors": [
    {
      "score-ranker-processor": {
        "combination": {
          "technique": "rrf"
        }
      }
    }
  ]
}
				
			
```

So then we use **`rrf-pipeline`** in the hybrid query:

```
				
					GET /web/_search?search_pipeline=rrf-pipeline
{
  "query": {
    "hybrid": {
      "queries": [
        {/* lexical keyword search */},
        {/* semantic search */}
      ]
    }
  }
}
				
			
```

For lexical keyword search, we use **`multi-match`** query and **`knn`** with **`nested`** field for semantic search:

```
				
					{
  "query": {
    "hybrid": {
      "queries": [
        {
          "multi_match": {
            "query": "test",
            "fields": ["title", "description"],
            "type": "best_fields"
          }
        },
        {
          "nested": {
            "path": "chunks",
            "query": {
              "knn": {
                "chunks.embedding": {
                  "vector": [/* LLM generated embeddings */],
                  "k": 100
                }
              }
            }
          }
        }
      ]
    }
  }
}
				
			
```

Moreover, pagination was also incorporated into the hybrid search [[PR](https://github.com/opensearch-project/neural-search/pull/1048)]. It is controlled by a combination of three parameters: **`pagination_depth`**, **`from`** and **`size`**.

`pagination_depth` controls how many results are retrieved per shard and per sub-query before the results are merged.

`from` and `size` define the final result window returned to the user after merging, deduplication, and reranking.

In the example below:

```
				
					GET /web/_search?search_pipeline=rrf-pipeline
{
  "from": 5,
  "size": 10,
  "query": {
    "hybrid": {
      "pagination_depth": 20,
      "queries": [
        {
          "multi_match": {
            "query": "test",
            "fields": ["title", "description"],
            "type": "best_fields"
          }
        },
        {
          "nested": {
            "path": "chunks",
            "query": {
              "knn": {
                "chunks.embedding": {
                  "vector": [/* LLM generated embeddings */],
                  "k": 100
                }
              }
            }
          }
        }
      ]
    }
  }
}
				
			
```

Here’s how it works:

* There are two sub-queries (**`multi_match`** and `knn`).
* Each one retrieves up to **`pagination_depth = 20`** results per shard.
* Assuming we have 3 shards, that’s:
  + **`20 × 3 = 60 results`** for **`multi_match`**
  + `20 × 3 = 60 results` for **`knn`**
  + Total of 120 results before merging
* After duplicates are removed and scores normalized via RRF, the final results are trimmed starting from the fifth entry and limited to the top 10 results (because of **`from = 5`** and **`size = 10`**).

The following diagram shows how pagination works, stemming from the [OpenSearch blog](https://opensearch.org/blog/navigating-pagination-in-hybrid-queries-with-the-pagination_depth-parameter/)

![](https://i0.wp.com/sease.io/wp-content/uploads/2025/12/pagination.png?fit=1982%2C1284&ssl=1)

It’s important to note that `pagination_depth` is applied first, retrieving a larger pool of results from each shard for each sub-query. Then, after merging, deduplication, and reranking, the **`from`** and **`size`** parameters are applied to trim the final result list that is returned to the user.

For more details on how pagination works in-depth, check out the [OpenSearch blog](https://opensearch.org/blog/navigating-pagination-in-hybrid-queries-with-the-pagination_depth-parameter/).

## Semantic Highlighting

Semantic sentence highlighting improves search explainability by using machine learning to identify and highlight sentences that match the meaning of the user’s query, rather than just exact keywords. Unlike traditional keyword-based highlighting, semantic highlighting captures the context and preserves full sentence structure.

##### Limitations and Our Workaround

[Semantic sentence highlighting](https://docs.opensearch.org/docs/latest/tutorials/vector-search/semantic-highlighting-tutorial/) was officially introduced in OpenSearch v3.0. Since we were using v2.17, we had to implement a custom workaround. The core objective was **to highlight the top‑k search results with the most semantically relevant sentences**, enhancing explainability for the user. To achieve this, we followed a two-step approach:

1. **Retrieve the top‑k documents** using a lexical search.
 2. **Pre-filter by their document IDs**, then run a (k-nearest neighbor) **k-NN search** at the chunk level to extract the most semantically relevant snippets from those documents.

To trigger the k-NN search asynchronously from the frontend, we considered two options:

* sending **a single request** containing all k document IDs, or
 * sending **k separate requests**, one per document.

We ultimately chose the second approach – one request per document to perform the k-NN search.

The following diagram illustrates this pipeline:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/12/unnamed.png?fit=800%2C244&ssl=1)

Below is a simplified version of the k-NN search implementation:

```
				
					Query knnSearch(String userQuery, int topK, List&lt;String&gt; ids) {
    var embeddings = getEmbeddings(userQuery);

    return Query.of(q -&gt; q.nested(nested -&gt; nested
        .path("chunks")
        .query(nq -&gt; nq.knn(knn -&gt; knn
            .field("chunks.embedding")
            .vector(embeddings)
            .k(topK)
            .filter(ids)
        ))
    ));
}
				
			
```

In the code above, **`getEmbeddings()`** generates a vector representation of the query using a text embedding model. The query searches inside the chunks field (a nested list of document paragraphs). Then it performs the k-NN search over **`chunks.embedding`**. If **`ids`** are provided, the filter restricts the results to those document IDs only.

**This workaround helped us bridge the gap, given that semantic sentence highlighting was introduced in later versions that we hadn’t upgraded to.**

##### Native Support in OpenSearch v3.0

Starting with OpenSearch v3.0, semantic sentence highlighting is now natively supported. This feature allows the system to highlight sentences based on semantic meaning, using a machine learning model. This feature works with any query type — lexical, vector, neural, or hybrid. We’ll be covering this topic in more depth, including real-world examples, in our next blog post. Stay tuned!

## Did-you-mean Suggester

According to the [OpenSearch Docs](https://docs.opensearch.org/docs/latest/search-plugins/searching-data/did-you-mean/), to implement did-you-mean suggestions for phrases, the **Phrase Suggester** method is used, which utilises n-gram language models to suggest phrases rather than individual words. This feature does not actually require n-grams to suggest phrases. We have tested that if the text analysis chain doesn’t break the text into n-grams and uses a plain chain (e.g. standard tokenizer, language analyzers), the spellchecker still works with this feature.

The following code snippet shows the simplified implementation:

```
				
					var suggesters = configuration.getPhraseSuggestionsFields()
       .stream()
       .map(fieldName -&gt; Map.entry(fieldName,
            FieldSuggester.of(fs -&gt; 
               fs.phrase(p -&gt; p.field(fieldName)
                    .maxErrors(0.99)
                    .highlight(hl -&gt; hl.preTag("&lt;b&gt;").postTag("&lt;/b&gt;"))
                ))))
                .collect(toMap(Map.Entry::getKey, Map.Entry::getValue));
				
			
```

In our configuration via **getPhraseSuggestionsFields**, we provided certain fields such as title, description body\_text. FieldSuggester calls **`phrase(...)`** on the given fields mentioned above. And several options are included: **maxErrors(…)** option allows errors in the spellings and **`highlight(...)`** configures suggestion highlighting with a bold (<b></b>) match.

## Conclusion

Overall, this was a hands-on look at the limitations of OpenSearch v2.17 with the practical workarounds.

Thanks for reading — stay tuned for more deep dives as we explore new features and real-world solutions in search.

## Need Help with this topic?​

If you're struggling with OpenSearch, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with OpenSearch, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)