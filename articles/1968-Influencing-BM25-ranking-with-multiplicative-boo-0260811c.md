---
title: 'Influencing BM25 ranking with multiplicative boosting in Elasticsearch'
company: Elastic
tag: 排序
date: 2025-12-22
url: https://www.elastic.co/search-labs/blog/bm25-ranking-multiplicative-boosting-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Influencing BM25 ranking with multiplicative boosting in Elasticsearch

Learn why additive boosting methods can destabilize BM25 rankings and how multiplicative scoring provides controlled, scalable ranking influence in Elasticsearch.

December 22, 2025

[Alexander Marquardt](/search-labs/author/alexander-marquardt)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

[BM25](https://en.wikipedia.org/wiki/Okapi_BM25) is one of the most widely used scoring models in Elasticsearch for text-based search. In many e-commerce implementations, it forms a major component of how product relevance is determined because it provides a well-understood, interpretable score that reflects how closely an item matches a shopper’s query. In addition to this text relevance, merchandising and search teams often need to influence the ranking with business metrics such as margin, stock levels, popularity, personalization, or campaign strategy, in a way that doesn’t destabilize the underlying text relevance.

The most intuitive levers for doing this are boosted [should](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query) clauses or [rank\_feature](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/rank-feature) fields. These may initially appear effective, but both approaches degrade and may even fail, as query patterns shift or catalog composition changes. Their shared limitation is that they introduce additive adjustments into a scoring system whose scale varies substantially across queries. A boost like “+2” might overwhelm the base BM25 score in one query while barely registering in another. In other words, additive methods may create brittle, unpredictable ranking behavior.

In contrast, [function\_score](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query) with multiplicative boosting provides a stable and mathematically proportional way to shape BM25 scores without distorting their underlying structure. Your application logic determines what merits uplift; `function_score` expresses that intent in a predictable and explainable way that preserves the geometry (high-level relative ordering) of the BM25 relevance signal, nudging rankings in controlled ways rather than overwhelming the core text relevance.

This article builds on two earlier pieces that demonstrated practical uses of multiplicative boosting: (1) [Boosting e-commerce search by profit and popularity with the function score query in Elasticsearch](https://www.elastic.co/search-labs/blog/function-score-query-boosting-profit-popularity-elasticsearch), and (2) [How to improve e-commerce search relevance with personalized cohort-aware ranking](https://www.elastic.co/search-labs/blog/ecommerce-search-relevance-cohort-aware-ranking-elasticsearch). Here we step back from those examples to examine the architectural principle that underlies them: why multiplicative boosting via `function_score` is one of the most reliable and scalable ways to influence BM25-based ranking in Elasticsearch.

## Why it's important to preserve base BM25 rankings

In many Elasticsearch-based applications, including e-commerce, BM25 remains a central component of how text relevance is assessed. It provides a signal that is interpretable and transparent for teams who need to understand why a product ranked where it did. These properties make BM25 particularly attractive in environments where explainability and operational predictability matter.

Because of this, most teams want to shape, rather than replace, the rankings produced by BM25. For example, they may want to allow higher-margin items to surface slightly more often, reduce exposure for low-stock products without hiding them, or highlight items aligned with a particular user segment. Ideally, this shaping should preserve the geometry of the rankings produced by the BM25 algorithm.

The difficulty arises when teams try to achieve these goals using mechanisms that add separate scoring streams on top of the base BM25 ranking. These additive adjustments are not always comparable to BM25’s scale and behave inconsistently as queries, data distributions, and catalog composition evolve. Over time, the ranking becomes brittle, unintuitive, and difficult to tune. A reliable influence mechanism must work with BM25’s scoring geometry rather than overpowering it.

The [function\_score](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query) query with multiplicative boosting provides this property. It allows teams to apply business influence in a proportional, explainable way while keeping BM25’s underlying structure intact.

## Why many approaches to influencing ranking degrade (or break) BM25

Teams often begin with mechanisms that look straightforward: boosted [should](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query) clauses, [rank\_feature](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/rank-feature) fields, or custom [script\_score](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-script-score-query) logic. These tools can be effective in their intended use cases, which is why they seem like natural levers for adding business influence. But when they are used to shape or influence BM25-based text relevance, they may create unstable, opaque, or brittle ranking behavior.

The underlying issue is that these approaches introduce independent additive scoring contributions into a system whose base BM25 values vary widely across queries, fields, and data sets. Without respecting that variability, the influence becomes unpredictable.

Below are the three most common patterns and why they fail in practice.

### 1. Additive boosts via should clauses

A boosted `should` clause feels intuitive: “Promote items that match this business rule.” But under the hood, the behavior is fundamentally additive.

Consider a query of the form:

```
GET products/_search
{
  "query": {
    "bool": {
      "must": [ { "match": { "description": "running shoes" }}],
      "should": [ { "term": { "brand": { "value": "nike", "boost": 1 }}}]
    }
  }
}
```

This kind of query results in the following behavior:

```
final_score = base_BM25 + should_BM25
```

The problem is that `base_BM25` and `should_BM25` do not scale together. As your dataset changes, or as different queries are issued, the magnitude of BM25 can shift dramatically. For example, the base BM25 scores for three products might be 12, 8, 4 in one context, and 0.12, 0.08, 0.04 in another. Such a change might happen after a catalog update or a modification to the query structure.

A boosted `should` clause adds its own BM25-style contribution to the final score. In this situation, an additive contribution (i.e. should\_BM25 = +2) behaves inconsistently:

* When base\_BM25 is small (0.12), +2 dominates the score — roughly an 18× increase.
* When base\_BM25 is large (12), the same +2 barely shifts the document — only about a 17% increase.

This instability means that the combined `must` score and `should` score have no stable meaning across queries or catalogs. A rule that slightly promotes a brand for one query can dominate the ranking for another, or become irrelevant in a third. This is not a tuning issue; it is a structural property of additive scoring.

### 2. Using rank\_feature for business influence

The `rank_feature` family is extremely useful for representing numeric qualities such as recency or popularity. It is fast, compressed, and operationally simple. However, when it is used to influence text relevance (BM25), it runs into the same structural limitation described in the previous section.

A `rank_feature` clause produces its own scoring contribution, which is then added to the BM25 score:

```
final_score = base_BM25 + feature_score
```

Just as with boosted `should` clauses, the two components do not scale together. BM25 values vary substantially across queries depending on term rarity and catalog statistics, while the `feature_score` follows the scale of the underlying business attribute being boosted (for example, popularity or recency), which typically bears no relationship to the scale of BM25. As a result, the two scoring streams drift apart as your corpus or query patterns evolve.

The consequence is the same as what we discussed above with relation to the should-clause problem:

* The feature score can dominate BM25 in one query and be negligible in another.
* Tuning becomes fragile because you are calibrating two independent scales — BM25, which varies with query term statistics, and the feature score, which varies with the business attribute’s own distribution.

Although `rank_feature` remains an excellent mechanism for representing raw numeric attributes, it is not well-suited for proportional influence on BM25, where the goal is not to add a second score but to gently shape the existing one.

### Custom scoring with script\_score

When boosted clauses or `rank_feature` fields become difficult to tune, teams often turn to `script_score` as a last resort. It provides complete freedom to manipulate the score, including adding, subtracting, multiplying, or replacing the BM25 value according to any business rule. A `script_score` query replaces Elasticsearch’s scoring pipeline with custom logic. Instead of shaping the BM25 score, the script builds a separate scoring mechanism whose behavior depends entirely on the code inside the script. While this can be powerful, it introduces three challenges that become more significant as the system grows.

**1. Opacity**

Scoring logic is hidden inside a script rather than expressed declaratively. When ranking behavior changes unexpectedly, it is difficult to understand whether the issue is the script itself, a data shift, or an interaction with BM25. Merchandisers and relevance engineers lose the ability to reason about why a document moved up or down.

**2. Performance and operational cost**

Script scoring bypasses many of Elasticsearch’s optimizations and caching pathways. Each document that matches the initial query must execute the script, often leading to higher CPU usage and unpredictable latency.

**3. Fragility when combined with BM25**

Because `script_score` allows arbitrary computations, it is easy to drift into scoring behaviors that no longer resemble BM25 or that fail to preserve its relative structure. As the dataset evolves or query patterns shift, the custom logic may interact with BM25 in unanticipated ways. A script that behaved reasonably early in development can produce surprising or unstable results once the catalog grows or data distributions change. Because `script_score` allows arbitrary math, two engineers working on different parts of the system may unintentionally encode competing scoring models, making ranking difficult to reason about as the organization scales.

## How function\_score provides predictable influence on BM25

BM25 already captures how well a document matches a query. It reflects text relevance, term rarity, document length, and the statistical shape of the corpus. When teams introduce business signals including margin, stock levels, popularity, personalization, or merchandising strategy, the goal is not to replace this relevance. The goal is to *influence it*.

This distinction is subtle but crucial. Most business requirements are proportional in nature:

* Promote higher-margin items modestly
* Reduce exposure for low-stock products, but don’t hide them
* Give this user segment a slight uplift for matching products
* Boost for popularity, but not so much that textual relevance is lost

These are naturally expressed as *percentage adjustments* rather than as fixed additive values. A merchandiser is rarely asking for “+2 points of score”; they are asking for “a little more visibility,” irrespective of the absolute numeric scale of the BM25 score. Mathematically, this means that the desired transformation is:

```
final_score = BM25 × boost_factor
```

Where *boost\_factor* might be 1.05, 1.2, or 1.5, depending on the signal. Multiplicative boosting does not attempt to reinvent scoring; it simply adjusts the BM25 output by a proportional factor. A multiplicative adjustment has three properties that align well with real-world ranking control:

1. The boost remains proportional. In other words, a 20% uplift is always a 20% uplift—whether BM25 is 0.12 or 12. The magnitude of the boost does not depend on the underlying BM25 scale.
2. BM25 retains its role as the primary signal. The multiplicative shaping nudges the ordering without overriding it. Strong textual matches still win; business logic influences but does not dominate.
3. Because the operation is multiplicative, not additive, changing the query or updating the corpus does not require re-tuning numeric constants. The boost has the same meaning everywhere.

Elasticsearch’s `function_score` query provides an elegant mechanism for expressing this pattern. By using:

* **score\_mode: “sum”** to assemble a boost factor (building the multiplier), and
* **boost\_mode: “multiply”** to apply the boost (multiplier) to BM25

You can express business intent in a way that remains stable and explainable as your data and query patterns evolve. Instead of adding a second score beside BM25, `function_score` transforms BM25 itself—shaping it gently, predictably, and in line with how merchandisers and product owners think about ranking adjustments.

## Examples in practice: How multiplicative boosting behaves in real e-commerce queries

To illustrate how multiplicative boosting works in real-world ranking scenarios, it helps to look at a small, concrete example. The goal here is not to demonstrate tuning or production-scale scoring, but rather to show how `function_score` influences BM25 in predictable, proportional ways that align with business intent.

Consider a simple catalog with three basketball shoes from three different brands: Nike, Adidas, and Reebok. The product descriptions are intentionally crafted so the BM25 scores exhibit natural differences based on query specificity and field length—just as they would in a real catalog.

### Example dataset

For the following examples, we use a small, straightforward sample dataset with the following characteristics.

| Brand | Description |
| --- | --- |
| nike | “Nike basketball shoes” |
| adidas | “New Adidas basketball shoes” |
| reebok | “Reebok basketball shoes” |

We can create an index with the above products with the following commands from Kibana Dev Tools:

```
PUT products
{
  "mappings": {
    "properties": {
      "brand":       { "type": "keyword" },
      "description": { "type": "text" }
    }
  }
}

POST products/_bulk
{ "index": { "_id": "nike-001" } }
{ "brand": "nike",    "description": "Nike basketball shoes" }
{ "index": { "_id": "adi-001" } }
{ "brand": "adidas",  "description": "New Adidas basketball shoes" }
{ "index": { "_id": "ree-001" } }
{ "brand": "reebok", "description": "Reebok basketball shoes" }
```

With this dataset, we now evaluate three queries:

* A baseline “basketball shoes” search
* The same query with a 50% promotion for Adidas and a 25% promotion for Nike
* A specific “Reebok basketball shoes” query while the Adidas and Nike promotions are still active

Each scenario highlights a different property of multiplicative boosting.

### 1. Baseline ranking: No promotion

```
GET products/_search
{
  "size": 3,
  "_source": ["brand", "description"],
  "query": {
    "match": { "description": "basketball shoes" }
  }
}
```

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt272891c9a78166c1/6a16f9d12b835f9e90f4b00b/050f44956c112ea9916d34946e9296480354f7d3-2322x1324.png)

This query returns the following results where Nike and Reebok are ranked above adidas:

| Rank | Brand | Score (BM25) |
| --- | --- | --- |
| 1/2 (tie) | nike | 0.27845407 |
| 1/2 (tie) | reebok | 0.27845407 |
| 3 | adidas | 0.24686474 |

### 2. Adding 50% Adidas uplift and 25% Nike uplift with function\_score

If marketing launches a campaign where Adidas basketball shoes should receive a 50% uplift and Nike a 25% uplift, then the application layer could construct its queries to include those uplifts as follows:

```
GET products/_search
{
  "size": 3,
  "_source": ["brand", "description"],
  "query": {
    "function_score": {
      "query": {
        "match": { "description": "basketball shoes" }
      },
      "functions": [
        {
          "filter": { "term": { "brand": "adidas" } },
          "weight": 0.5
        },
        {
          "filter": { "term": { "brand": "nike" } },
          "weight": 0.25
        },
        {
          "weight": 1.0
        }
      ],
      "score_mode": "sum",
      "boost_mode": "multiply"
    }
  }
}
```

### How the multiplier is constructed

* Base weight = 1.0
* Adidas gets an additional +0.5
* So Adidas’s multiplier = 1.5
* Nike gets an additional +0.25
* So Nike’s multiplier = 1.25
* All other brands (including Reebok) get the base weight multiplier = 1.0

### Apply multiplier:

Final score = BM25 × multiplier

| Product | BM25 | Multiplier | Final score |
| --- | --- | --- | --- |
| Adidas | 0.24686474 | 1.5 | 0.37029710 |
| Nike | 0.27845407 | 1.25 | 0.34806758 |
| Reebok | 0.27845407 | 1.0 | 0.27845407 |

### Result

Adidas moves to the top, Nike follows, and Reebok is at the bottom with no change in its score. This is exactly the behavior that multiplicative boosting is designed to produce:

* Adidas and Nike both gain visibility, but in proportion to their configured uplifts.
* The relative differences in BM25 still matter; we are reshaping the ranking, not replacing it.
* The ordering changes primarily where BM25 scores are close.

With additive boosts, the same “50% versus 25%” business intent would have to be approximated with numeric constants on an arbitrary BM25 scale, and the effect would vary drastically across queries.

## 3. Specific intent still wins: “Reebok basketball shoes”

Now run a highly specific branded query for “Reebok basketball shoes”, with the same Adidas (50%) and Nike (25%) promotions still active:

```
GET products/_search
{
  "size": 3,
  "_source": ["brand", "description"],
  "query": {
    "function_score": {
      "query": {
        "match": { "description": "Reebok basketball shoes" }
      },
      "functions": [
        {
          "filter": { "term": { "brand": "adidas" } },
          "weight": 0.5
        },
        {
          "filter": { "term": { "brand": "nike" } },
          "weight": 0.25
        },
        {
          "weight": 1.0
        }
      ],
      "score_mode": "sum",
      "boost_mode": "multiply"
    }
  }
}
```

The response shows the following results:

| Rank | Brand | Final score |
| --- | --- | --- |
| 1 | reebok | 1.3011196 |
| 2 | adidas | 0.3702971 |
| 3 | nike | 0.34806758 |

### Result

Reebok wins overwhelmingly because BM25 correctly detects strong intent for “Reebok basketball shoes”. Adidas and Nike still receive their 50% and 25% promotions, respectively, but those multipliers are nowhere near enough to override the BM25 score.

This is exactly the behavior that multiplicative boosting is designed to produce:

* When BM25 scores are close, boosts can shift the relative ordering.
* When BM25 scores differ significantly (as they do here, due to strong text matching), the same boosts have little practical effect.

Promotions influence the ranking, but they do not override the core text relevance signal.

## What this example demonstrates

These real queries illustrate the key properties of multiplicative boosting:

1. The influence is proportional, not arbitrary. A percentage-based uplift has the same proportional effect regardless of the underlying BM25 scale.
2. Text relevance remains in control. Strong brand-intent queries still surface the correct product.The system behaves intuitively. Merchandisers see exactly the ranking changes they expect.
3. The math is stable across queries. The same promotion works correctly whether the match is broad or highly specific.
4. Application logic stays clean. The business layer decides the uplift; Elasticsearch applies it predictably.

Multiplicative boosting through `function_score` preserves relevance in a predictable and controllable way, while enabling business impact.

## Application logic remains the author of influence

There is a clear separation between deciding what should be boosted and applying that boost in Elasticsearch. `function_score` handles the second task, but the first belongs firmly to application logic.

Your application logic is where decisions are made about:

* Which margin thresholds matter for your business
* Whether popularity should rise or fall based on seasonality
* How to interpret customer behavior or cohort membership
* How to encode campaign rules
* When to surface or suppress certain product groups

These are *business* decisions, not scoring decisions. Elasticsearch does not infer whether a user is budget-focused or luxury-oriented, whether a promotion is active, or whether low stock requires a visibility adjustment. Those determinations occur upstream, in the part of the system that has access to user context, session features, analytics, and business configuration. After application logic produces clear numeric signals for fields such as weights, uplift factors, thresholds, and cohort tags, a `function_score` query provides a reliable way to express those signals as controlled multipliers on BM25.

This creates a clean architectural contract:

* Application logic: decides *what* should be influenced.
* BM25 provides the core text relevance.
* `function_score` applies influence in a mathematically stable way.

Because business logic lives outside the index, teams can adjust or experiment with uplift strategies without reindexing or restructuring documents.

## Conclusion

E-commerce search must balance core text relevance with business considerations such as profitability, stock position, customer intent, seasonality, and personalization. BM25 provides a stable and interpretable foundation for text relevance, but influencing that score requires care. Business signals should shape the ranking, not overpower it.

However, the most commonly used levers such as boosted `should` clauses, `rank_feature` fields, and ad-hoc script scoring often behave unpredictably. These approaches can appear effective in early development, but their limitations emerge as soon as the catalog evolves or new query patterns arrive. Additive boosts fluctuate wildly because their impact depends entirely on the underlying scale of BM25, which varies dramatically across queries. A boost that produces a subtle nudge in one situation can dominate the ordering in another. Script scoring introduces its own challenges: opaque logic, reduced performance, and scoring behavior that becomes harder to understand or maintain over time.

Multiplicative boosting with `function_score` avoids these pitfalls by transforming BM25 proportionally rather than competing with it. Instead of adding a second, independent score component, it applies a controlled multiplier to BM25 itself. This produces the kind of predictable adjustments that merchandisers actually intend. For example, it allows slight promotions for high-margin items, modest reductions for low-stock products, or gentle uplifts for relevant user cohorts.

Equally important, the architecture remains clean. Application logic determines which business signals matter, and `function_score` applies them in a consistent, explainable way. Business teams can evolve business strategy without destabilizing relevance, and Engineering teams can refine relevance without disturbing business rules.

This principle is the foundation of the previous blogs that demonstrated how to influence e-commerce rankings: (1) [Boosting e-commerce search by profit and popularity with the function score query in Elasticsearch](https://www.elastic.co/search-labs/blog/function-score-query-boosting-profit-popularity-elasticsearch), and (2) [How to improve e-commerce search relevance with personalized cohort-aware ranking](https://www.elastic.co/search-labs/blog/ecommerce-search-relevance-cohort-aware-ranking-elasticsearch). Both approaches rely on the idea that business signals should guide BM25, not override it. Multiplicative boosting through `function_score` provides a practical, transparent, and scalable method for achieving that balance in real-world e-commerce search.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt975c900958571074/6a17d7c0abe0f277e2dfe85d/fd800d12d1c12abf68ccb7e8dd80ad7b62bec38c-1440x840.png)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### GenAI for customer support — Part 4: Tuning RAG search for relevance

August 22, 2024|[Antonio Schönmann](/search-labs/author/antonio-schonmann)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbeb5dbab80ffb03d/6a17d7104202290f4229f449/7fce63922298d2a0fcc8a5f292db74d2e0fae0a1-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Elastic Support Hub starts using semantic search

November 16, 2023|[Chris Blaisure](/search-labs/author/chris-blaisure)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt27b746cc1995e6b7/6a170efda29299de8ad010c6/e6d3186f609dd56dc5ffe33d70fa9e5cfa05b51f-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Adaptive early termination for HNSW in Elasticsearch

March 02, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd17ed30cb6a59275/6a46944fde977731a4ca54b5/e7a1b50ef019d1b5a12d49c7457d63a026e1edd0-727x496.png)

[Vector Database](/search-labs/blog/category/vector-database)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How we doubled vector search throughput on Elasticsearch Serverless

May 28, 2026|[Chris Hegarty](/search-labs/author/chris-hegarty)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter