---
title: 'Elasticsearch autocomplete search'
company: Elastic
tag: 查询理解
date: 2025-02-19
url: https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch autocomplete search

Exploring different approaches to handling autocomplete in Elasticsearch, from basic to advanced, including search as you type, query time, completion suggester, and index time.

February 19, 2025

[Amit Khandelwal](/search-labs/author/amit-khandelwal)

[Basics](/search-labs/blog/category/basics)

Jump to

Share

In this article, we will cover how to avoid critical performance mistakes, why the Elasticsearch default solution doesn’t cut it, and important implementation considerations.

All modern-day websites have autocomplete features (search as you type) on their search bar to improve the user experience (no one wants to type entire search terms…). It’s imperative that the autocomplete be faster than the standard search, as the whole point of autocomplete is to start showing the results while the user is typing. If the latency is high, it will lead to a subpar user experience.

Below is an autocomplete search example on the famous question-and-answer site, Quora. This is a good example of autocomplete: when searching for “elasticsearch auto”, the following posts begin to show in their search bar:

![Autocomplete search example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt007b9a71e641ae2f/6a17f4246df7311a630a1057/d4dfbfcdbecad041728ed2d24b906836a5942f40-553x434.png)

Note that in the search results, there are questions relating to the auto-scaling, auto-tag and autocomplete features of Elasticsearch. Users can further type a few more characters to refine the search results.

## Approaches for autocomplete in Elasticsearch / search as you type

There are multiple ways to implement the autocomplete feature which broadly fall into four main categories:

1. [Search-as-you-type](https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search#1.-search-as-you-type)
2. [Query time](https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search#2.-query-time)
3. [Completion suggester](https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search#3.-completion-suggester)
4. [Index time](https://www.elastic.co/search-labs/blog/elasticsearch-autocomplete-search#4.-index-time)

## 1. Search as you type

It is a data type intended to facilitate the autocomplete queries without prior knowledge of custom analyzer setup. Elasticsearch internally stores the various tokens (edge n-gram, shingles) of the same text, and therefore can be used for both prefix and infix completion.

It can be convenient if you are not familiar with the advanced features of Elasticsearch, which the other three approaches require. Not much configuration is required in Search as you type to make it work with simple use cases and code samples.ore details are available in our [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-as-you-type.html).

## 2. Query time

Autocomplete can be achieved by changing [match queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html) to [prefix queries](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-prefix-query.html). While match queries work on token (indexed) to token (search query tokens) match, prefix queries (as their name suggests) match all the tokens starting with search tokens, hence the number of documents (results) matched is high.

As explained, prefix query is not an exact token match, rather it’s based on character matches in the string which is very costly and fetches a lot of documents. Elasticsearch internally uses a [B+ tree](https://en.wikipedia.org/wiki/B%2B_tree) kind of data structure to store its tokens. It’s useful to understand the internals of the data structure used by inverted [indices](https://www.elastic.co/blog/what-is-an-elasticsearch-index) and how different types of queries impact the performance and results.

Elasticsearch also introduced [Match boolean prefix query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-bool-prefix-query.html) in ES 7.2 version. This is a combination of Match and Prefix queries and has the best of both worlds. It’s especially useful when you have multiple search terms. For example, if you have `foo bar baz`, then instead of running a prefix search on all the search terms (which is costly and produces fewer results), this query would prefix search only on the last term and match previous terms in any order. Doing this improves the speed and relevance of the search results.

## 3. Completion suggester

This is useful if you are providing suggestions for search terms like on e-commerce and hotel search websites. The search bar offers query suggestions, as opposed to the suggestions appearing in the actual search results, and after selecting one of the suggestions provided by the completion suggester, it provides the search results.

For the completion suggester to work, suggestions must be indexed as any other field. You can also optionally add a weight field to rank the suggestions.

This approach is ideal if you have an external source of autocomplete suggestions, like search analytics.

### Code samples

#### Index definition

```
PUT movies
{
  "mappings": {
    "properties": {
      "movie_name": {
        "type": "completion"
      }
    }
  }
}
```

#### Response

```
{
  "acknowledged": true,
  "shards_acknowledged": true,
  "index": "movies"
}
```

#### Indexing suggestions

```
PUT movies/_doc/1?refresh
{
  "movie_name" : {
    "input": [ "Avengers", "Infinity War" ],
    "weight" : 34
  }
}
```

#### Response

```
{
  "_index": "movies",
  "_id": "1",
  "_version": 1,
  "result": "created",
  "forced_refresh": true,
  "_shards": {
    "total": 2,
    "successful": 1,
    "failed": 0
  },
  "_seq_no": 0,
  "_primary_term": 1
}
```

#### Searching

```
POST movies/_search?pretty
{
  "suggest": {
    "song-suggest": {
      "prefix": "inf",        
      "completion": {         
          "field": "movie_name"  
      }
    }
  }
}
```

#### Response

```
{
  "took": 2,
  "timed_out": false,
  "_shards": {
    "total": 1,
    "successful": 1,
    "skipped": 0,
    "failed": 0
  },
  "hits": {
    "total": {
      "value": 0,
      "relation": "eq"
    },
    "max_score": null,
    "hits": []
  },
  "suggest": {
    "song-suggest": [
      {
        "text": "inf",
        "offset": 0,
        "length": 3,
        "options": [
          {
            "text": "Infinity War",
            "_index": "movies",
            "_id": "1",
            "_score": 1,
            "_source": {
              "movie_name": {
                "input": [
                  "Avengers",
                  "Infinity War"
                ]
              }
            }
          }
        ]
      }
    ]
  }
}
```

## 4. Index time

Sometimes the requirements are just prefix completion or infix completion in autocomplete. It’s not uncommon to see autocomplete implementation using [custom-analyzers](https://www.elastic.co/guide/en/elasticsearch/reference/current/configure-text-analysis.html), which involves indexing the tokens in such a way that it matches the user’s search term.

If we continue with our example, we are looking at documents that consist of “elasticsearch autocomplete”, “elasticsearch auto-tag”, “elasticsearch auto scaling” and “elasticsearch automatically”. The default analyzer won’t generate any partial tokens for “autocomplete”, “autoscaling” and “automatically”, and searching “auto” wouldn’t yield any results.

To overcome the above issue, [edge ngram](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-edgengram-tokenizer.html) or [n-gram tokenizer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-ngram-tokenizer.html) are used to index tokens in Elasticsearch, as explained in the [documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenizers.html), and [search time analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-analyzer.html) to get the autocomplete results.

The above approach uses Match queries, which are fast as they use a string comparison (which uses hashcode), and there are comparatively less exact tokens in the index.

## Performance consideration

Almost all the above approaches work fine on smaller data sets with lighter search loads, but when you have a massive index getting a high number of auto suggest queries, then the SLA and performance of the above queries is essential. The following bullet points should assist you in choosing the approach best suited for your needs:

* Ngram or edge Ngram tokens increase index size significantly, providing the limits of min and max gram according to application and capacity. Planning would save significant trouble in production.
* Allowing empty or few character prefix queries can bring up all the documents in an index and has the potential to bring down an entire [cluster](https://www.elastic.co/guide/en/elasticsearch/reference/current/high-availability.html). It’s always a better idea to do a prefix query only on the term (on a few fields) and limit the minimum characters in prefix queries. This can be now solved by using the [boolean Match prefix query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-bool-prefix-query.html) as explained above.
* ES provided “search as you type” data type tokenizes the input text in various formats. As it is an ES-provided solution which can’t address all use-cases, it’s always a better idea to check all the corner cases required for your business use-case. In addition, as mentioned it tokenizes fields in multiple formats which can increase the Elasticsearch index store size.
* Completion suggests separately indexing the suggestions and doesn’t address the use-case of fetching the search results.
* Index time approaches are fast as there is less overhead during query time, but they involve more grunt work, like re-indexing, capacity planning and increased disk cost. Query time is easy to implement, but search queries are costly. This is very important to understand as most of the time users need to choose one of them and to understand this trade-off can help with many troubleshooting performance issues.

### Frequently Asked Questions

#### What are the approaches for implementing autocomplete in Elasticsearch?

There are multiple ways to implement the autocomplete feature in Elasticsearch, including search-as-you-type, query time, completion suggester, and index time.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt6d8bd040a15da207/6a17e422414c640e67945116/ef9edded97edd7c919e617e648e62016155cde56-720x420.jpg)

[Basics](/search-labs/blog/category/basics)

### Parsing JSON fields in Elasticsearch

October 17, 2025|[Valentin Crettaz](/search-labs/author/valentin-crettaz)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt373f9290a1371dd7/6a17122e0c48579b2001abba/fd87bff40e296ebce871d631c86fd0245f11c796-1440x960.jpg)

[Javascript](/search-labs/blog/category/javascript-programming)[Basics](/search-labs/blog/category/basics)

### Automatically updating your Elasticsearch index using Node.js and an Azure Function App

June 04, 2024|[Jessica Garson](/search-labs/author/jessica-garson)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1a0bf009f00b1c80/6a1711fa4a531b3db636aa9f/c7c174d6408b23fca482664c608f9e8849243d96-1440x720.jpg)

[Basics](/search-labs/blog/category/basics)

### Adding document level security (DLS) to your internal knowledge search

January 22, 2024|[Sean Story](/search-labs/author/sean-story)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d7e4a5bbd9427c2/6a170e4d0e2e4905b641a1b7/04f1738a38cead88c9a67b0f863171b4b43010ab-1600x913.png)

[Basics](/search-labs/blog/category/basics)

### Elasticsearch plugin for UBI: Analyze user data in Kibana

September 26, 2025|[Eduard Martin](/search-labs/author/eduard-martin)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltc31c3bf0d453d846/6a170e12cdacbfdf6a7d2a7e/3ae41b1f2876d2ad11c8e2b79bbf79955d6902aa-1440x840.png)

[Java](/search-labs/blog/category/java-programming)[Basics](/search-labs/blog/category/basics)

### Testing Elasticsearch. It just got simpler.

March 19, 2026|[Piotr Przybyl](/search-labs/author/piotr-przybyl)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter