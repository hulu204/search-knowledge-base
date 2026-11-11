---
title: 'Search relevance tuning: Balancing keyword and semantic search'
company: Elastic
tag: 搜索相关性
date: 2024-05-14
url: https://www.elastic.co/search-labs/blog/search-relevance-tuning-in-semantic-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Search relevance tuning: Balancing keyword and semantic search

This blog offers practical strategies for tuning search relevance that can be complementary to semantic search.

May 14, 2024

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

## Introduction

Tuning for relevance is an essential part of user search experience. Semantic search in particular faces several challenges, many of which are solved through hybrid search and application of relevance tuning practices that have been honed by decades of research in lexical search. We'll go into some of these strategies and how you can effectively use them to tune relevance in a hybrid search world.

This blog shares some of the highlights from the Haystack 2024 talk, [Retro Relevance: Lessons Learned Balancing Keyword and Semantic Search](https://haystackconf.com/us2024/talk-6/).

## Lexical search toolbox for relevance tuning

Text search algorithms like BM25 have been around for decades, and in fact BM25 is often used synonymously with text search. [This blog post](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables) goes into how BM25 works in detail.

Analyzers, tokenizers, filters, field weights and boosts are all tools in our lexical search toolbox that give us the power to transform text in very specific ways to support both general and very specialized search use cases.

But we also have a lot of other tools at our disposal:

* Reranking is another powerful tool in this toolbox, whether it pertains to Learn to Rank, semantic reranking, etc.
* Synonyms are heavily used in keyword search to differentiate slang, domain specific jargon, and so on. General models may not handle very niche synonyms well.

These tools are used to impact relevance, but also importantly to accommodate business rules. Business rules are custom rules and their use cases vary widely, but commonly include diversifying result sets or showing sponsored content based on contextual query results or other personalization factors.

## Challenges with semantic search

Semantic search is impressively effective at representing the intent of what you're looking for, returning matching results even if they don't contain the exact keywords you specified. However - if you’re developing a search application and incorporating semantic search into your existing tech stack, semantic search is not without some pitfalls.

These pitfalls largely fall under three categories:

* Cost
* Features that semantic search inherently doesn't have yet
* Queries that semantic search by itself doesn't do well with

Cost can be money (training or licensing models, compute), or it can be time. Time can be latency (inference latency at ingest or search), or it can be the cost of development time. We don't want to spend valuable engineering time on things that are easily solved with existing tools, and instead, use that time to focus on solving the hard problems that require engineering focus.

There are also many features that people have come to expect in their search solutions; for example, highlighting, spelling correction, and typo tolerance. These are all things that semantic search struggles with out of the box today, but many UI/UX folks consider these table stakes in terms of user functionality.

As far as queries that semantic search may not do well with, these are typically niche queries. Examples include:

* Exact matches such as model numbers
* Domain specific jargon

We also have to consider requirements including business rules (for example boosting based on popularity, conversions, or campaigns), which semantic search by itself may not handle natively.

Query understanding is another issue. This could be as simple as handling numeric conversions and units of measurement, or it could be very complex such as handling negatives. You may have had a frustrating experience searching for a negative, such as “I want a restaurant that doesn't serve meat”. LLMs may be OK at returning vegetarian restaurants here, but most semantic search is going to return you restaurants that serve meat!

These are hard problems to solve and they're the ones we want to spend our valuable engineering time on.

## Benefits of hybrid search

Hybrid search is the best of both worlds: it combines the precision and functionality of BM25 text search with the semantic understanding of vector search. This leads to both better recall and better overall relevance.

To help put this in perspective, let's look at some examples:

* **Real estate:** *Modern farmhouse with lots of land and an inground pool in the 12866 zip code.* Whether the house has a pool and its ZIP code can be filters, and semantic search can be used over the style description.
* **eCommerce:** *Comfortable Skechers with memory foam insoles in purple.* The color and brand can be filters, and the rest can be covered with semantic search.
* **Job hunting:** *Remote software engineer jobs using Elasticsearch and cloud native technologies.* The job title and preference for remote work can be filters, and the job skills can be handled with semantic search.

In all the above examples, the query has something specific to filter on along with more vague text that benefits from semantic understanding.

## What does a hybrid search look like in Elasticsearch?

The phrase "hybrid search" is a little buzzwordy right now, and people might think of it differently in various scenarios. In some systems, where you have a separate vector database, this might involve multiple calls to different data stores and combining them with a service. But, one of the superpowers of Elasticsearch is that all of this can be combined in one single index and one search call.

In Elasticsearch, a hybrid search may be as simple as a [Boolean query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-bool-query.html). Here's an example of a Boolean query structure in Elasticsearch that combines text search, KNN searches, text expansion queries, and other supported query types. This can of course be combined with rescores, and everything else that makes Elasticsearch so powerful. Boolean queries are a very easy way to combine these text and vector searches into one, single query. One note about this example is that [KNN was introduced as a query](https://www.elastic.co/search-labs/blog/knn-query-elasticsearch) in addition to the top level search in 8.12, making this query structure even more powerful.

```
POST /my-index-000001/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "multi_match": { ... }
        },
        {
          "knn": { ... }
        },
        {
          "text_expansion": { ... }
        },
        {
          "rule_query": { ... }
        }
      ],
      "minimum_should_match": 1,
      "boost": 1
    }
  }
}
```

Another option is to use [retrievers](https://www.elastic.co/guide/en/elasticsearch/reference/master/retriever.html), which starting with Elasticsearch 8.14.0 are an easier way of describing these complex retrieval pipelines. Here is an example that combines a standard query as a retriever, with a kNN query as a retriever, all rolled up to use [Reciprocal Rank Fusion (RRF)](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) to rank the results.

```
POST /my-index-000001/_search
{
  "retriever": {
    "rrf": {
      "retrievers": [
        {
          "standard": {
            "query": {
              "term": {
                "text": "purple sneakers"
              }
            }
          }
        },
        {
          "knn": {
            "field": "vector",
            "query_vector": [1.25, 2, 3.5],
            "k": 50,
            "num_candidates": 100
          }
        }
      ],
      "window_size": 50,
      "rank_constant": 20
    }
  }
}
```

### Combining result sets

Now that you have a hybrid search query, how do you combine all this into a single result set? This is a hard problem, especially when the scores are virtually guaranteed to be vastly different depending on how the results were retrieved.

The classic way, using the Boolean query example, is with linear combination where you can apply boosts to each individual clause in the larger query. This is tried and true, nice old technology that we all know and love, but it can be finicky. It requires tuning to get right and then you may never get it perfect.

If you're using retrievers you can also use [RRF](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html). This is easier - you can rely on an algorithm and don't have to do any tuning. There are some trade-offs - you have less fine grained control over your result sets. RRF doesn't take BM25 boosting into account, so if you're boosting on business rules, you might not get the results you want out of the box.

Ultimately the method you should choose depends on your data and your use case.

## Tuning for relevance

Once you've created your query, tuning for relevance is a hard problem to solve, but you have several tools at your disposal:

* Business metrics. These are the most important metrics in a lot of ways: Are users clicking on results, and in eCommerce use cases for example better yet are they completing purchases? Is your conversion rate increasing? Are users spending a decent amount of time reading the content on your site? These are all measures of user experience but they’re gathered through analytics and they’re direct proof of whether your search is providing results that are actually useful. For use cases like RAG, where the results are custom, subjective, and subject to change, this might be the only way to really measure the impact of your search changes.
* User surveys. Why not ask users if they thought the results were good and bad? You do have to take some things into account such as whether users will provide truthful responses, but it’s a good way of taking a pulse of what users think of your search engine.
* Quantitative ways of measuring relevance such as MAP and NDCG. These metrics require judgment lists which can then also be used for Learn to Rank.

The single biggest trap that people can fall into, though, is tuning for one or a few “pet” queries: the handful of queries that you - or maybe your boss - enters. You can change everything about your algorithm to get that best top result for that one query, but then it can have cascading effects downstream, because now you’ve unknowingly messed up the bulk of your other queries.

The good news is that there are some tools available to help!

## Applying tools for search relevance tuning

### Query rules

Remember that pet query? Well I have good news for you - you can still have great results for that pet query without modifying your relevance algorithm, using the concept of pinned or promoted documents. At Elastic, we call these query rules. Query rules allow you to send in some type of context, such as a user-entered query string, and if it matches some criteria we can configure specific documents that we want to rank first, second, third, etc.

One great use case for query rules is the application of business rules. Another use case is “fixing” relevance. Overall relevance shouldn't be nitpicky, and we should rely on methods like ranking, reranking, and/or RRF to get it right. But there are always exceptions. Maybe overall relevance is good enough, but you have a couple of queries that people complain about? OK, just set up a rule. But you can go further if you want: it can potentially be a worthwhile investment to take a quick pass through your head queries to make sure that they're returning the right information and these users are getting a good search experience. It's not cheating to correct some of the common user-entered queries, and then focus on improving your torso and tail queries through the power of semantic search where it really shines.

So how does this work?

Elastic query rules are defined by creating a query ruleset, or a list of one or more rules. Each rule has criteria that must match the rule in order for a query to be applied, and then actions that we take on the rule if it matches. A rule can have multiple criteria, based on the metadata you send in from the client.

```
PUT /_query_rules/my-ruleset
{
  "rules": [
    {
      "rule_id": "rule1",
      "type": "pinned",
      "criteria": [
        {
          "type": "fuzzy",
          "metadata": "query_string",
          "values": [ "puggles", "pugs" ]
        },
        {
          "type": "exact",
          "metadata": "user_country",
          "values": [ "us" ]
        }
      ],
      "actions": {
        "ids": [
          "id1",
          "id2"
        ]
      }
    }
  ]
}
```

In this example, a user's query string and their location was sent in a rule - both of those criteria would have to be met in order for the rule to match. To trigger these rules at search time, you send in a corresponding rule query that specifies the metadata that you want to match on.

```
POST /my-index-000001/_search
{
  "query": {
    "rule_query": {
      "organic": {
        "query_string": {
          "query": "puggles"
        }
      },
      "match_criteria": {
        "query_string": "puggles",
        "user_country": "us"
      },
      "ruleset_id": "my-ruleset"
    }
  }
}
```

We'll apply all matching rules in the ruleset, in order, and pin the documents that you want to come back. We're currently working on plans to make this feature generally available and extend the functionality: for example to support tokenizers and analyzers on rule criteria, making it easier for non-technical people to manage query rules, and to potentially provide additional actions on top of just pinning documents.

You can read more about query rules and how to use them in this [guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-using-query-rules.html) and corresponding [blog post](https://www.elastic.co/blog/introducing-query-rules-elasticsearch-8-10).

### Synonyms

Next, let's talk about synonyms. Maybe you have some domain specific jargon that is unique to only your business and isn't in any of the current models - and you don't necessarily want to take on the expense to fine tune and train your own model.

For example: while ELSER will recognize both `pug` and `beagle` as related to `dog`, it will not recognize `puggle` (a crossbeed of pug and beagle) as a `dog`. Synonyms can help here!

Synonyms are a great way of translating this domain specific terminology, slang, and alternate ways of saying a word that may just be too specialized for a model to return the matches we want.

In Elasticsearch, we used to manage this in a way that required a lot of manual overhead - you had to upload synonyms files and reload analyzers.

In Elasticsearch 8.10, we introduced a synonyms API that makes this easier. Similar to query rules, you create synonyms sets with one or more defined synonyms, and then when you use the API to add, update, or remove synonyms it reloads analyzers for you - pretty easy!

```
PUT _synonyms/my-synonyms-set
{
  "synonyms_set": [
    {
      "id": "pc",
      "synonyms": "pc => personal computer"
    },
    {
      "id": "computer",
      "synonyms": "computer, pc, laptop, desktop"
    }
  ]
}
```

You can then update your mappings to define a custom analyzer that uses this synonyms set.

```
PUT /my-index-000001
{
  "settings": {
    "analysis": {
      "filter": {
        "synonyms_filter": {
          "type": "synonym_graph",
          "synonyms_set": "my-synonyms-set",
          "updateable": true
        }
      },
      "analyzer": {
        "my_index_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase"]
        },
        "my_search_analyzer": {
          "type": "custom",
          "tokenizer": "standard",
          "filter": ["lowercase", "synonyms_filter"]
        }
      }
    }
  }
}
```

The nice thing about synonyms being supported with analyzers is that when we do support analyzers in query rules in the future, we'll be able to support synonyms as well out of the box.

You can read more about the synonyms API and how to use it in this [guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-with-synonyms.html) and corresponding [blog post](https://www.elastic.co/blog/update-synonyms-elasticsearch-introducing-synonyms-api).

## Wrapping up

Semantic search doesn't replace BM25 search, it's an enhancement to existing search technologies. Hybrid search solves *many* problems innate to semantic search and is the best of both worlds in terms of both recall and functionality. Semantic search really shines with long tail and torso queries. Tools like query rules and synonyms can help provide the best search experience possible while freeing up valuable developer time to focus on solving important problems.

As the landscape evolves, we're getting better and better at solving some of the hard problems that come with semantic search, *and* making it easier to use both semantic and hybrid search through simplification and tooling.

Our goal as search practitioners is to return the best results possible. Our other goal is to do this as easily as possible, and minimize costs - those costs include money and time, and time can mean latency or engineering overhead. We don't want to waste that valuable engineering time - we want to spend it solving hard problems!

You can [try the features I've talked about out in Cloud](https://cloud.elastic.co/registration?utm_source=elastic-search-labs&utm_medium=referral&utm_campaign=search-labs&utm_content=article) today! Be sure to head over to our [discuss](https://discuss.elastic.co/) forums and let us know what you think.

## Watch the Haystack talk

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