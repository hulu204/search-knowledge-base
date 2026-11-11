---
title: 'Elasticsearch percolator for ecommerce search governance: translating ambiguous queries into controlled retrieval strategies'
company: Elastic
tag: 查询理解
date: 2026-05-04
url: https://www.elastic.co/search-labs/blog/elasticsearch-percolator-search-governance
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch percolator for ecommerce search governance: translating ambiguous queries into controlled retrieval strategies

Learn how to use the Elasticsearch percolator to implement search governance. In this blog, we outline the patterns needed to create a governed policy engine in production and create a controlled retrieval strategy.

May 04, 2026

[Alexander Marquardt](/search-labs/author/alexander-marquardt)[Honza Král](/search-labs/author/honza-kral)[Taylor Roy](/search-labs/author/taylor-roy)

[Operations](/search-labs/blog/category/operations)

Part of the series:

[Governed search patterns](/search-labs/blog/series/governed-search-patterns)

In this series

Share

This post is a technical deep dive into the Elasticsearch implementation of the control plane architecture described in [Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture), showing how to build it using the Elasticsearch percolator. It outlines the patterns used to implement a deterministic, governed policy engine in production.

## **From architecture to implementation**

[Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture) described the control plane architecture: reverse matching as a lookup primitive, policy documents that separate match from action, and cascading transformations that compose multiple policies into a single execution plan. This post goes hands-on with the Elasticsearch feature that powers the policy lookup: the [percolator query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-percolate-query).

The percolator is a natural fit for governance because it inverts the direction of search in exactly the way a control plane needs. This post walks through the implementation step by step, starting with a clear explanation of what the percolator does and why it matters, and then moving through index design, policy storage, query-time evaluation, and multi-policy composition.

## **How normal search works**

In an ecommerce system, you may have hundreds of thousands or millions of product documents containing fields such as `title`, `category`, and `price`. When a user searches for matching documents, you're asking Elasticsearch to compare the user’s search string against one or more stored fields in these product documents. Elasticsearch's default analyzer, [the standard analyzer](https://www.elastic.co/docs/reference/text-analysis/analysis-standard-analyzer), lowercases text and splits it into tokens. A search for “oranges” matches “Oranges” because of lowercasing. With a language-aware analyzer that includes stemming, it also matches “orange” because both forms reduce to the same stem. For example, the following [match query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-match-query) returns documents that have “orange” or “oranges” in their `“title”` field.

```
POST products/_search
{
  "query": {
    "match": {
      "title": "oranges"
    }
  }
}
```

So for the above query, Elasticsearch returns the product documents whose `title` field matches “oranges”, which could include results such as “Orange Fruit Spread”, “Orange Juice”, “Juicy oranges”, “Orange Marmalade”, and so on. The key point to remember is that Elasticsearch is commonly used to compare a search string against documents and to return the documents that match the search string.

![A diagram comparing an incoming search string to stored product titles, showing matches for three titles containing “orange” and no match for two titles that do not.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt806e1c8c115bc9b6/6a170dba67045b634645c266/ba758f25616f2106d245ce0d47926c174766e028-642x318.png)

## **The governance problem: Finding relevant policies before searching for products**

As established in [Parts 1 through 3](https://www.elastic.co/search-labs/blog/series/governed-search-patterns), a governed search system does not send the user's search string directly to the product catalog. First, it checks whether any policies apply to that search string.

A merchandiser has decided that when someone searches for exactly "oranges", results should be restricted to the Oranges category, eliminating orange juice, orange marmalade, and orange soda. That business decision is stored as a policy. When a user types "oranges", the control plane needs to find that policy, read its instructions, and modify the search against the product catalog accordingly. In order to do this, the control plane needs to figure out which stored policies are relevant for this search string.

An enterprise deployment might have hundreds or thousands such policies. Checking them one by one with if/else logic is the application-layer anti-pattern described in [Part 2](http://elastic.co/search-labs/blog/ecommerce-search-governance-zero-deploy). What we need is a way to store all of those policies in an index and instantly find the ones that match a given search string. This is where the percolator comes in.

## **Flipping the direction: The percolator**

We previously mentioned that in a normal search, Elasticsearch is commonly used to compare a search string against documents and to return the documents that contain that search string.

The percolator inverts this. With a percolator, you have an index where each document stores a query pattern, and then an incoming search string is checked against these stored queries to determine which of these stored query patterns has triggered.

![A diagram showing several stored query patterns tested independently against an incoming search string, with “oranges” producing a match and all other patterns returning no match.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1e7e2966bf46474d/6a170dbba929cf500aae0a57/1e6348531d1c0be57b385f51d248488cf58489ff-642x279.png)

For governance, the "stored query patterns" are policies. Each policy contains a pattern that describes the kind of search string it should match. For example, does the search string exactly match “oranges”, or does the search string contain “olive oil”? The incoming string is the user's search text, which arrives at query time and needs to be checked against all stored policy patterns. This is covered in a [related PRISM video at 4:09](https://youtu.be/Ap5K2Y00Xjc?t=246).

## Step by step: How a search for "oranges" finds its policy

### The policy

A merchandiser has authored a policy that matches if a user searches for exactly "oranges" without any other words. Once the percolator matches, the remainder of the document includes the rules that the control plane will use to build the Product query; in this example, one of the rules is to restrict (filter) results to the Fruits category.

```
{
  "percolator": {
    "match_phrase": { "query": "START oranges END" }
  },
  "rule_type": "filter",
  "rule_args": {
    "filters": [
      {
        "field": "categories",
        "values": ["Fruits"],
        "mode": "hard_filter",
        "on_conflict": "soft_boost",
        "on_conflict_boost_weight": 1.0
      }
    ]
  },
  "priority": 0,
  "enabled": true
}
```

The `percolator` field contains the pattern that defines when this policy should fire. In this case, it matches the phrase `"START oranges END"`. The `rule_type` and `rule_args` fields define what the policy should do when it fires. The `START` and `END` tokens are boundary markers, which we will explain shortly.

You can see how a policy is authored in the PRISM Studio UI at [2:52 of the related PRISM video](https://youtu.be/Ap5K2Y00Xjc?t=172).

### The user searches

A shopper types "oranges" into the search bar.

### The control plane checks for matching policies

Before searching the product catalog, the control plane intercepts the user search string, wraps it in boundary markers, and sends it to the percolator:

```
POST policies/_search
{
  "query": {
    "percolate": {
      "field": "percolator",
      "document": {
        "query": "START oranges END"
      }
    }
  }
}
```

The string `"START oranges END"` is checked against all stored policy patterns. Internally, Elasticsearch runs the stored policy patterns against this string and returns the ones that match. That's the percolator. The user's search string was checked against all stored policy patterns, and the ones that matched were returned. No if/else chains. No sequential evaluation. The index handles the matching.

### The control plane applies the policy

The control plane reads the matched policies’ actions. The above policy instructs the control plane to restrict results to the Fruits category. The control plane builds the final Elasticsearch query against the product catalog as follows:

```
POST products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "title": "oranges" } }
      ],
      "filter": [
        { "terms": { "categories": ["Fruits"] } }
      ]
    }
  }
}
```

The user searched for "oranges”. The product catalog receives a query for "oranges" constrained to the Fruits category. Because of this constraint, orange juice, orange marmalade, and orange soda are excluded.

### Why "orange marmalade" does NOT trigger the oranges policy

Suppose a different user searches for "orange marmalade”. The control plane wraps the string and percolates: `"START orange marmalade END"`. The oranges policy's pattern is `match_phrase: "START oranges END"`. The oranges policy does not match and therefore the policy isn’t applied, and the results aren’t constrained to the Fruits category.

This is the purpose of the `START` and `END` boundary markers. Without them, a policy that matches on the word "oranges" could accidentally fire on a query like "orange marmalade". By wrapping the user's search string with `START` and `END` and including those markers in the policy's pattern, we ensure that the policy only fires when "oranges" is the complete search string, without any other words. This matches both the shoppers and the merchandiser's intent.

## A second policy: "olive oil" on the stemmed field

Not every policy needs an exact string match. The “olive oil” policy matches on a stemmed field, so it fires regardless of minor word-form variations:

```
{
  "percolator": {
    "bool": {
      "should": [
        { "match_phrase": { "query.stemmed": "START olive oil END" } }
      ]
    }
  },
  "rule_type": "filter",
  "rule_args": {
    "filters": [
      {
        "field": "categories",
        "values": ["Olive oils"],
        "mode": "hard_filter",
        "on_conflict": "soft_boost",
        "on_conflict_boost_weight": 1.0
      }
    ]
  },
  "priority": 300,
  "enabled": true
}
```

This policy's pattern matches against `query.stemmed` instead of `query`. When the user's search string arrives, it’s stored in both a `query` field (the exact text) and a `query.stemmed` field (analyzed with a stemming analyzer that reduces words to their stems, so "olives" and "olive" both reduce to the same stem, as do "oils" and "oil"). The policy's pattern is checked against the stemmed version of the string, so it fires regardless of minor word-form variations.

The `START` and `END` boundary markers work on the stemmed field, as well, ensuring this policy only fires when "olive oil" is the entire search string, not when it appears as part of something longer.

The rest of this post covers the implementation details that make this production-ready: the index mapping that supports both matching modes, how highlights drive phrase removal and consumed phrase tracking, and how multiple conflicting policies compose into a single execution plan.

## **The policy index mapping**

The policy index needs a percolator field to hold stored query patterns and a text field that mirrors the structure of the incoming search string the percolator will match against. The mapping below is simplified for clarity. A production deployment is more complex, using custom analyzers to handle boundary markers, variable pattern matching (for example, recognizing that "under $4" contains a currency value), and other kinds of analysis.

```
PUT policies
{
  "mappings": {
    "properties": {
      "percolator": {
        "type": "percolator"
      },
      "query": {
        "type": "text",
        "fields": {
          "stemmed": {
            "type": "text",
            "analyzer": "stemming"
          }
        }
      },
      "rule_type": { "type": "keyword" },
      "rule_args": { "type": "object", "enabled": false },
      "priority": { "type": "integer" },
      "enabled": { "type": "boolean" }
    }
  }
}
```

The index is named `policies` because each document represents a complete governed policy as defined in [Part 2](http://elastic.co/search-labs/blog/ecommerce-search-governance-zero-deploy). This includes match criteria, action, priority, and metadata. The `rule_type` and `rule_args` fields contain the action component of the policy, which contain the instructions that the control plane will use to compose the query for execution against the product catalog.

The `query` field is the string that the percolator matches against. It has two variants: an exact version and a stemmed version. When the user's search string arrives, it’s placed into this field in the temporary in-memory index. Policies that match on `query` see the exact string; policies that match on `query.stemmed` see the stemmed version.

## **Percolating with highlights, filtering, and sorting**

The simple examples above showed minimal percolation requests. In practice, the control plane adds highlighting, filters disabled policies, and sorts by priority:

```
POST policies/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "percolate": {
            "field": "percolator",
            "document": {
              "query": "START olive oil END"
            }
          }
        },
        {
          "term": { "enabled": true }
        }
      ]
    }
  },
  "highlight": {
    "fields": {
      "query": {
        "matched_fields": ["query.stemmed"]
      }
    }
  },
  "sort": [
    { "priority": { "order": "desc" } }
  ]
}
```

The highlight configuration uses `"query"` as the field key with `"query.stemmed"` in `matched_fields`. This tells Elasticsearch's unified [highlighter](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/highlighting) to return highlights on the parent `query` field but to also consider matches from the `query.stemmed` subfield when determining which tokens to highlight. This is what allows a policy that matches on the stemmed field to still produce accurate highlight spans on the original text, which the control plane needs for phrase removal and consumed phrase tracking.

The `enabled: true` filter ensures that disabled policies are skipped. The `sort` on priority ensures that higher-priority policies are returned first, so the control plane can process them in the correct order for cascading transformations. The `highlight` field is the most important addition; it tells us exactly which words in the user's search string triggered each match.

The response for an "olive oil" search may look as follows:

```
{
  "hits": {
    "hits": [
      {
        "_id": "en_2c3021c8",
        "_source": {
          "rule_type": "filter",
          "rule_args": {
            "filters": [
              {
                "field": "categories",
                "values": ["Olive oils"],
                "mode": "hard_filter",
                "on_conflict": "soft_boost",
                "on_conflict_boost_weight": 1.0
              }
            ]
          },
          "priority": 300
        },
        "highlight": {
          "query": ["<em>START olive oil END</em>"]
        }
      }
    ]
  }
}
```

## **Why highlights matter**

Notice the highlight in the response: `"<em>START olive oil END</em>"`. Elasticsearch is telling us exactly which words in the user's search string caused the policy to match. This isn’t cosmetic. The highlight metadata drives two critical downstream behaviors:

**Phrase removal.** Some policies need to remove the matched text from the search string before constructing the product catalog query. For example, a policy that matches on "cheap" removes that word and converts it into a price filter instead. The highlight identifies exactly which span of the search string the policy matched, so the system knows what to remove.

**Consumed phrase tracking.** As described in [Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture), when multiple policies match the same search string, a higher-priority policy might remove words that a lower-priority policy also matched on. By comparing each policy's highlight against the current (evolving) search string, the system can detect that a phrase has been consumed and skip the lower-priority policy. This prevents double-processing and ensures deterministic behavior.

You can learn more about how highlighting works in [this article](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/how-es-highlighters-work-internally).

## **From percolation to execution plan**

The percolator returns a set of matching policies. But as [Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture) described, the lookup is only half the story. The other half is composing those matches into a coherent execution plan. Here’s what that looks like for a concrete query.

### **Worked example: "Cheap chocolate" during a Christmas campaign**

Suppose the system has two active policies: the "Cheap chocolate" policy (priority 210) and the "Christmas chocolates" policy (priority 300), both described in detail in [Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture).

**Step 1: Percolate.** The user searches for "cheap chocolate." The control plane wraps the search string as `"START cheap chocolate END"` and sends it to the percolator. Two policies match: The "Cheap chocolate" policy's pattern matches on the phrase "cheap chocolate"; and the "Christmas chocolates" policy's pattern matches on "chocolate" via the stemmed field.

**Step 2: Sort by priority.** The percolator returns both policies, sorted by priority in descending order. The “Christmas chocolates” policy (300) is processed first, followed by the “Cheap chocolate” policy (210).

**Step 3: Apply the cascading transformation.** This is the `initial state → [Policy A] → state' → [Policy B] → state'' → execution plan` model from [Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture).

The “Christmas chocolates” policy (priority 300) applies first:

* Adds a category hard filter: "Christmas foods and drinks," "Christmas sweets".
* Adds a price filter: less than $7.
* Adds a category soft boost: "Advent calendars" (3x).

The “Cheap chocolate” policy (priority 210) applies next against the modified state:

* Attempts to add a category hard filter: "Chocolates," "Milk chocolates"; but the Christmas policy already set this field with `on_conflict: override`, so the Cheap chocolate categories are dropped.
* Attempts to add a price filter: $2, the Christmas policy set `on_conflict: restrict` for price, and $2 is more restrictive than $7, so $2 wins.
* Removes "cheap" from the search string.

**Step 4: Build the Elasticsearch query.** The control plane assembles the execution plan into a single Elasticsearch query against the product catalog:

```
POST products/_search
{
  "query": {
    "function_score": {
      "query": {
        "bool": {
          "must": [
            { "match": { "title": "chocolate" } }
          ],
          "filter": [
            { "terms": { "categories": ["Christmas foods and drinks", "Christmas sweets"] } },
            { "range": { "price": { "lt": 2 } } }
          ]
        }
      },
      "functions": [
        {
          "weight": 1
        },
        {
          "filter": { "terms": { "categories": ["Advent calendars"] } },
          "weight": 3
        }
      ],
      "score_mode": "sum",
      "boost_mode": "multiply"
    }
  }
}
```

The original search string was "cheap chocolate”. The query that reaches the product catalog is a governed, intent-aware retrieval plan: The word "cheap" has been consumed and converted into a price constraint, results are restricted to Christmas seasonal categories, Advent calendar products receive a ranking boost, and the price ceiling reflects the more restrictive value from the lower-priority policy. Every transformation is deterministic, traceable, and explainable.

For a quick overview about how these multipliers interact with the base BM25 score, see [8:45 in the related PRISM video](https://youtu.be/Ap5K2Y00Xjc?t=525), where we briefly discuss multiplicative boosts.

## **Why this scales**

The percolator is efficient for this use case because of the asymmetry: An enterprise ecommerce system might have millions of products but only hundreds or thousands of governance policies. The percolator is checking one incoming search string against that set of stored policy patterns, not scanning the full product catalog. The cost is proportional to the number of policies, and Elasticsearch applies internal optimizations (indexing terms from stored query patterns, short-circuiting Boolean logic) to keep matching fast.

Adding a new policy is just indexing a new document. Disabling one is a field update. No code changes, no deploys, no restarts.

## **From lookup to governed retrieval**

The percolator provides the fast reverse-matching primitive that makes the control plane architecture from [Part 3](http://elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture) practical at scale. Policies are data which are stored and indexed, and efficiently matched against incoming search strings. The control plane composes matching policies into a governed execution plan through the cascading transformation and per-field conflict resolution described in Part 3. And the retrieval engine executes the governed execution plan against the product catalog.

The result is a system where a merchandiser can author a new policy without touching application code, test it against representative queries, promote it to production, and immediately see the effect. The percolator makes the policy lookup fast; the control plane makes the policy composition deterministic; and the governed workflow makes the whole process safe.

## **What's next in this series**

The next post in this series extends the governed control plane into new territory. It introduces a **multi-tier search architecture**, explaining how to orchestrate strict, relaxed, and semantic retrieval while maintaining stable pagination and facets.

## **Put governed ecommerce search into practice**

The percolator-based control plane described in this post, from index mappings and boundary markers to highlight-driven phrase tracking and cascading policy composition, was built by Elastic Services Engineering as part of our repeatable ecommerce search accelerators. Every query example and policy structure shown here comes from a working system validated against enterprise-scale product catalogs.

If you want to implement a governed, policy-driven control plane on Elasticsearch, Elastic Services can get you there faster. Contact [Elastic Professional Services](https://www.elastic.co/consulting).

## Join the discussion

Have questions about search governance, retrieval strategies, or ecommerce search architecture? Join the broader [Elastic community conversation](https://discuss.elastic.co/).

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3979255ddfc7f45/6a17e25ffaa913812f93c7cb/92c517a2e7b36122a18feee317a0215981b62b6b-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Operations](/search-labs/blog/category/operations)

### Your agents have been keeping receipts: turning Elastic Agent Builder's built-in OTel traces into token cost dashboards in Kibana

July 28, 2026|[Meghan Murphy](/search-labs/author/meghan-murphy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd9be3378b7b18d00/6a6a33c6d137a512563e106b/86ddf69cfc68919fb0f708eb190c18fdc2b9479a-1999x1200.png)

[AutoOps](/search-labs/blog/category/autoops)[Elastic Cloud Hosted](/search-labs/blog/category/elastic-cloud-hosted)[Operations](/search-labs/blog/category/operations)

### Faster Elasticsearch issue triage with redesigned AutoOps

July 23, 2026|[Ori Shafir](/search-labs/author/ori-shafir)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt69260cf1c6f964e3/6a17db030b0bed6f52dd346e/5d64716981e76396b401fd069d0a635b6929ba94-720x420.jpg)

[Operations](/search-labs/blog/category/operations)

### Multi-tier search with Elastic for ecommerce search governance: Fixing poor recall

May 06, 2026|[Alexander Marquardt](/search-labs/author/alexander-marquardt)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt4be28a2b56f0f75b/6a6119e91b1d4902a46f1813/2997670e3ebae815e16cb1a336542a9ddd0de77e-1999x1072.png)

[Operations](/search-labs/blog/category/operations)

### 98.9% faster queries, 4x more indexing throughput: a systematic Elasticsearch performance diagnosis

July 15, 2026|[Aleksandar Panov](/search-labs/author/aleksandar-panov)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter