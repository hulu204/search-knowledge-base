---
title: 'Building a control plane to govern ecommerce search'
company: Elastic
tag: 工程相关
date: 2026-05-01
url: https://www.elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Building a control plane to govern ecommerce search

How to build a governed control plane for ecommerce that composes conflicting search policies into a single execution plan (without code changes).

May 01, 2026

[Alexander Marquardt](/search-labs/author/alexander-marquardt)[Honza Král](/search-labs/author/honza-kral)[Taylor Roy](/search-labs/author/taylor-roy)

[Operations](/search-labs/blog/category/operations)

Part of the series:

[Governed search patterns](/search-labs/blog/series/governed-search-patterns)

In this series

Share

[Part 1](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-improve-retrieval) and [part 2](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-zero-deploy) of this series established why ecommerce search needs a *governance layer*, a decision layer between the user's query and the retrieval engine that classifies intent, enforces constraints, and routes to the correct retrieval strategy (for example, BM25, semantic, hybrid). This post shows how to build that layer using a simple architectural primitive where query interpretation policies are stored as documents and retrieved at query time via fast reverse matching. Because new retrieval policies (for example, “boost brand X” or “only show category Y”) don’t require code changes, the result is a routing layer that stays stable while policies evolve and that keeps the retrieval engines safe in high-stakes environments. If you want to see the end result of this architecture before reading further, check out this video: [Fixing Search Relevance in Seconds: Introducing PRISM](https://www.youtube.com/watch?v=e1GuL9CYWAk).

## Why query interpretation is often a challenge

Storing policies as code (if/else blocks in the application layer) produces tens of thousands of lines of brittle logic that lacks any indexing for efficient policy retrieval at query time. Iteration is slow (a single query behavior change may require a six-week deployment cycle), accountability is unclear (why did results change?), and business users cannot modify search behavior without engineering involvement. This is shown on the left side in the following image:

![Image with two headings, “Policies as code” on the left and “Policies as data” on the right. The left side shows conditional code blocks defining query‑handling rules with notes about deployment, change cycles, and sequential evaluation. The right side shows JSON policy objects with titles, match terms, actions, filters, and priorities, along with notes about storage in an Elasticsearch index, update behavior, and indexed matching.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb84f89f4d9029df7/6a170f806234e077cddb1ab6/4e2cd5244ef8b9a05af6337a4825252f321a9a43-1377x768.png)

Storing policies as data in an Elasticsearch index is shown on the right side of the above image. This approach solves all of the issues associated with hard-coded query resolution logic. However, for this to work, you need a way to quickly determine which policies match the user query and how conflicts should be resolved. This is where the governed control plane comes in.

## The control plane pattern

A governed control plane sits between the raw user query and an Elasticsearch retrieval. It receives user text as its input, and its output is an execution plan that includes filters, boosts, and retrieval routing decisions.

![Diagram illustrating two search flows through a governed control plane: one where a text query for “oranges” is rewritten with a category constraint before product lookup, and another where a semantic query for “gift for grandpa” is rewritten and routed to retrieve matching products from a product catalog.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0585c90830d63d02/6a170f82964cea7a5908bc8b/5562da5de521f3c83ed55a13e9be87ca7fa70109-546x489.png)

A control plane pipeline consists of:

1. **User query:** A user enters a string of what they’re looking for, such as “oranges” or “gift for grandpa”.
2. **Policy lookup:** Match the user query against the policy index.
3. **Return matching policies:** Policies that match the user query are returned from the policy index.
4. **Policy application:** The control plane analyzes these returned policies and composes matched policies into a single coherent execution plan that includes filters, boosts, overrides, and guardrails and that applies the appropriate retrieval method (for example, lexical versus semantic versus hybrid).
5. **Execute:** The modified *intent-aware* Elasticsearch query is passed to the application to be executed against a product catalog index.
6. **Explain (optional):** In addition to creating a query that provides business and intent-aligned results, the control plane provides an optional explainability payload to show which policies were triggered and how they were combined.

Finding which policies should be applied for a user’s search string requires a fast reverse-matching primitive, which we solve with the [percolator query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-percolate-query). After retrieving relevant policies, combining multiple matched policies into a unified execution plan requires a judgment framework: priorities, conflict strategies, consumed phrase tracking, and cascading transformations that apply policies in sequence rather than independently. Additionally, the most appropriate retrieval technology needs to be selected (for example, [BM25](https://www.elastic.co/elasticon/conf/2016/sf/improved-text-scoring-with-bm25) for “oranges” versus [semantic search](https://www.elastic.co/docs/solutions/search/semantic-search) for “gift for grandpa”).

## Policy lookup: Checking the query before searching for products

When a shopper types a query, a search system with a governed control plane doesn’t send that query directly to be executed against the product catalog. First, the query is checked against a set of stored policies and modified to reflect the intent of the query and business priorities.

### Policy structure

Each policy is a simple document that defines two things:

* **Match criteria:** What query text should cause this policy to fire. This could be an exact phrase, a single word, a pattern, or a combination.
* **Action:** What to do when the policy fires. This could be applying a category filter, excluding products, extracting a price constraint, or changing the retrieval strategy.

The system finds all matching policies, composes them into an execution plan, and only then runs the product search. Taken together, policies act like a knowledgeable store associate who understands what you’re looking for and walks you to the right aisle.

### The policy pattern

The first articles in this series introduced examples of policies in action: constraining "oranges" to the produce category, treating "without peanuts" as an exclusion, and routing "gift for grandpa" to semantic retrieval. The key architectural point is that in each case, the query is checked against stored policies before the product search begins. The policies determine what constraints to apply, which text to modify, and which retrieval strategy to use. The query against the product catalog comes after the policies have been applied and a new rewritten query has been created.

### Why this is fast

An enterprise ecommerce system might have millions of products but only hundreds or thousands of policies. The policy lookup step is searching against a small curated index, not the full product catalog, and is therefore fast. And because policies are stored as data in their own index, a merchandiser adding a new policy doesn't touch the application code, and an engineer optimizing the product search doesn't touch the policy index. The two concerns evolve independently.

The examples above describe what happens conceptually. Under the hood, the policy lookup is implemented using the Elasticsearch [percolator query](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-percolate-query) type, which is purpose-built for this kind of pattern: matching incoming text against a set of stored queries. [Part 4](https://www.elastic.co/search-labs/blog/elasticsearch-percolator-search-governance) in this series provides a hands-on deep dive into the percolator implementation, including index mappings, boundary markers, and highlight-driven phrase tracking. With the lookup mechanism covered in depth in Part 4, let's turn to what a policy document actually contains and how the control plane composes multiple policies into a single execution plan.

## Example policies

Now that we've seen what policies do conceptually, let's look at what they actually contain. The two policies below have been designed to intentionally conflict, which will demonstrate the conflict resolution system described in subsequent sections.

### Cheap chocolate

The policy shown below detects if a user has submitted a search containing the phrase “cheap chocolate”. If so, results are restricted to the “Chocolates” and “Milk chocolates” categories. This policy also applies a price filter of $2. Also, notice that this policy has a priority of 210; we’ll come back to this when we discuss conflict resolution in more detail.

The filter mode and conflict strategy settings shown here (hard\_filter, soft\_boost, restrict, override) are explained in detail in the conflict resolution section below.

![Interface showing a rule configuration with a match phrase for “cheap chocolate,” category and price filters, a phrase‑removal field, and priority settings.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltada4d46e2ab26208/6a170f836f7f04f91f914924/bbcd66b20fc3aa861b5880ca67daf8e809698717-1002x890.png)

When the above policy is activated, a search for “cheap chocolate” respects the price filter of $2 and restricts results to the “Chocolates” and “Milk chocolates” categories. Example results are shown below:

![Interface showing a rule configuration with a match phrase for “cheap chocolate,” category and price filters, a phrase‑removal field, and priority settings.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt368bdfbb9a6e5a5e/6a170f8566c4f975a1f8c10f/3f373af9a985864315d7639440a416e45a882a1b-1133x1146.png)

### Christmas chocolate

The policy shown below is an example of a policy that one could imagine applying at Christmas. This example restricts results to “Christmas foods and drinks” and “Christmas sweets”, boosts any products that are also in the “Advent calendars” category, and applies a price filter of less than $7 to focus on affordable seasonal items. Additionally, notice that this policy has a priority of 300. We’ll come back to this when we discuss conflict resolution in more detail.

![Screenshot of an Elasticsearch rule query interface showing a match_phrase query for “chocolate,” filter rules based on categories and price, conflict handling options, and rule priority settings.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta3428d211f2d8304/6a170f86839dfa0049dcffb3/8f1179342d0e05cf78266d142b046021a3694368-1007x941.png)

When the above policy is activated without any conflicting policies, a search for “chocolate” respects the price filter of $7, and restricts results to the “Christmas food and drinks” and “Christmas sweets” categories, and boosts any products tagged as “Advent calendars”. Example results are shown below:

![Search results page showing a query for “chocolate” with category and brand filters on the left and a list of chocolate advent calendar products with images, prices, categories, and descriptions on the right.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0e7f1fe91b2cadcd/6a170f8866c4f90b0af8c113/662b0e40cb3a9291c17816c33169e9ff5b68f98d-1129x1085.png)

## Combining matched policies

The policy lookup described above is half the story. The other half is what happens when multiple policies match the same query.

In any nontrivial deployment, a single query will routinely trigger several policies at once. "Cheap chocolate" will match both of the policies that we demonstrated above. Each policy is correct in isolation. The challenge is composing them into a single, coherent execution plan without contradictions, without double-counting, and without one policy silently undoing the work of another.

This isn’t a lookup problem; it’s a judgment problem. The system must decide:

* **Order of application:** If a negation policy removes "without peanuts" from the query, does the price policy still see the original text or the modified text?
* **Filter conflicts:** If two policies set different price ceilings, which one wins? Is the loser silently dropped, or does it degrade gracefully into a soft boost?
* **Phrase ownership:** If two policies both matched on the same word and the first one already consumed it, should the second one still fire?

A naive implementation (apply all matched policies independently, merge the results) breaks as soon as policies interact. The architecture needs an explicit model for how policies compose. The next two sections describe that model: a priority and conflict resolution framework; and a cascading transformation model that makes policy interaction deterministic.

The key insight is that policy application isn’t a set of independent operations; it’s a cascading transformation. Each policy receives the rewrite state produced by all higher-priority policies and transforms it further:

initial state → [Policy A] → state' → [Policy B] → state'' → ... → execution plan

The state carries the rewritten query text, accumulated filters, current intent, and any synonym expansions. A high-priority policy can remove text from the query, and every subsequent policy sees the modified query, not the original. Context accumulates. Order matters.

## Precedence and conflict resolution: Determinism matters

The specific conflict strategies are a design choice. Different organizations may resolve conflicts differently, depending on their business requirements. The following approach illustrates the kind of judgment framework a control plane needs. The important thing is not these specific strategies but that the system has explicit, deterministic strategies rather than letting conflicts resolve through unpredictable interactions.

### Priority ordering

Policies are sorted by priority (highest first). When multiple policies match the same query, they’re applied in priority order. If two policies try to set the same filter field, the higher-priority policy's declared strategy for that field takes precedence. If there are multiple policies triggered that have the same priority, then the policy with the highest ID is given precedence (as if it were assigned a higher priority); this choice ensures deterministic behavior when conflicts arise.

### Per-field resolution, not per policy

A critical design principle: Conflict resolution operates per field (for example, brand, category, or description), not per policy. When two policies produce filters that overlap on specific fields, only those specific fields are affected by the conflict resolution strategy, and the resolution strategy is defined by the highest-priority matching policy. Non-conflicting fields from both policies survive intact.

This matters because the alternative of a per-policy approach would force the system to either accept or reject an entire policy when only one of its fields conflicts.

Per-field resolution preserves the maximum amount of useful constraint information.

### Three settings per filter field

Each filter field in a policy has three independent settings:

**Filter mode:** How the filter is applied when there’s no conflict.

* `hard_filter` (default): Applied as an [Elasticsearch](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query#score-bool-filter) [`bool.filter`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-bool-query#score-bool-filter) clause. This is useful for excluding unrelated products entirely. For example, restricting a search for "oranges" to the produce category eliminates hits such as orange juice and orange marmalade. Non-matching documents are completely excluded from results.
* `soft_boost`: Applied as an [Elasticsearch](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query) [`function_score`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query) weight with a configurable `boost_weight`. Documents that match get a ranking boost, but non-matching documents aren’t excluded. This is useful for something like boosting a brand, without excluding other brands.

### Conflict strategy

What happens when a lower-priority policy sets the same field:

* `override`: This high-priority policy's value wins; the lower-priority value is dropped entirely. Valid for all field types.
* `restrict`: Take the more restrictive numeric value (for example, the lower ceiling for price\_\_max, the higher floor for price\_\_min). Valid for numeric range fields only.
* `merge`: Combine both values into a union. Valid for non-numeric fields only.
* `soft_boost`: Convert the conflicting filter to a `function_score` weight with a configurable `boost_weight` instead of a hard filter. For more details on function\_score boosting, see [Influencing BM25 ranking with multiplicative boosting in Elasticsearch](https://www.elastic.co/search-labs/blog/bm25-ranking-multiplicative-boosting-elasticsearch). This is only valid for non-negation fields.

**Value:** The actual filter value (for example, a categories list, a price threshold).

**Strategies by field type:** Not all strategies make sense for all field types. For instance, an exclusion is inherently binary, so it cannot be soft-boosted. The following table shows which strategies are available for each field type:

| Field type | Available strategies | Default |
| --- | --- | --- |
| Negation fields (\_\_not, \_\_match\_\_not) | override, merge | override |
| Numeric range fields (\_\_max, \_\_min, \_\_gt, \_\_lt) | restrict, override, soft\_boost | restrict |
| All other fields (keyword, text) | soft\_boost, override, merge | soft\_boost |

Negation fields cannot be soft-boosted because exclusions are binary. Converting "never show canned foods" to "slightly prefer not-canned-foods" fundamentally changes the semantics; a product from "canned foods" would still appear, just ranked slightly lower, which defeats the purpose of the exclusion.

## A concrete example: Searching for "cheap chocolate" during a Christmas campaign

Suppose a merchandiser has created the two policies for chocolate that we previously demonstrated, a lower priority one for cheap chocolate and another higher-priority chocolate-related policy that will be enabled during Christmas. If both of these policies are enabled, then how these are combined depends on the filter mode and conflict strategy of the higher-precedence policy. If both of the previously discussed policies are enabled, they’ll be combined as follows:

![Screenshot showing a transformation pipeline where an initial query “cheap chocolate” is modified by multiple rules, including added category and price filters, conflict resolution behavior, rule priorities, and a final transformed query of “chocolate.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf930b42611a6126c/6a170f8aacf088ae28be9c1b/0405e193522172bde283180df96ed3651178fafc-529x447.png)

This shows two conflicts, one on categories and one on price. It’s worth noting that the query that will be executed after this transformation has the following characteristics:

* Only products from the “Christmas foods and drinks” and “Christmas sweets” categories will be shown.
* Within those categories, if the products are also tagged as being in the “Advent calendars” category, they’ll be boosted up by 3x.
* A price filter for $2 is applied, which came from the lower-priority policy (because the higher-priority policy specified to “Restrict” on conflict).
* The word “cheap” is removed, only returning products matching “chocolate”.

With both of these policies enabled, “cheap chocolate” returns results similar to the image shown below:

![Search results page showing a query for “cheap chocolate,” with category and brand filters on the left and a list of chocolate advent calendar products with images, prices, and product details on the right.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7e3c2ee36f963e8c/6a170f8ccdacbf5be17d2ac2/01bbab1c5bd3d0fd37e39c25973d60141f9796e9-1126x1123.png)

### Relaxing constraints

Perhaps the retailer doesn’t want to exclude products in the categories of “Chocolates” and “Milk chocolates” during Christmas. The settings on the Christmas policy might have overreached and inadvertently removed categories applied by the “cheap chocolate” policy. This is an example that shows why it might be more desirable to combine lower-priority policies with conflicting higher-priority policies. For example, we could modify the Christmas chocolates promotion so that instead of “Override” on conflict, we do a soft boost. The change to that policy would be as follows:

![User interface showing a search policy rule with field set to Categories, operator set to Equals, values “Christmas foods and drinks” and “Christmas sweets,” conflict handling set to Soft with priority 1, and filter mode set to Hard filter.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbb7393566aeab705/6a170f8db0367d5b6472bde2/45e88311014d67933ca8cf8381d8f91de090e2b4-1090x103.png)

After this modification, the query rewriter transformation pipeline execution for “cheap chocolate” looks as follows:

![Screenshot of a transformation pipeline showing how the initial query “cheap chocolate” is modified by multiple rules, including category filters, price limits, soft boost and hard filter modes, conflict handling outcomes, rule priorities, and a final query of “chocolate.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6b4453b35b5f8ef0/6a170f8fb339d5ba9b76a09a/396b360e48327421c2c38bcf4a039fb1a6d5a8e0-519x445.png)

With the soft boost on conflict, the conflicting filters are converted into soft boosts rather than being dropped. The query that will be executed on the product catalog after this transformation has the following characteristics:

* Because “On conflict” is specified as “Soft boost” on the higher-priority policy, the conflicts will be converted to boosts as follows:

  + Products from the “Christmas foods and drinks” and “Christmas sweets” categories will have a boost of 1x applied to them.
  + Products from the “Chocolates” and “Milk chocolates” categories will have a boost of 3x applied to them.
* As in the previous example, if the products are also tagged as being in the “Advent calendars” category, they’ll be boosted up by 3x.
* As in the previous example, a price filter for $2 is applied.
* The word “cheap” is removed, only returning products matching “chocolate”.

With relaxed filtering, results look as follows:

![Search results page for the query “cheap chocolate,” showing category and brand filters on the left and a product list on the right, with multiple chocolate items, prices, categories, and a total of 6,895 results indicated at the top.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0288336675c509ef/6a170f917d8d6723bc70e808/7a68c54d878dadfe8b1821dd3860b7b60f9ce45f-1126x1123.png)

### Overriding price from a high-priority policy

Or perhaps the retailer wants to allow slightly more expensive chocolates to be shown during Christmas by increasing the price max to $7. To ensure that the max price from the Christmas chocolates policy is not overridden if someone searches for “cheap chocolates”, we can set the conflict mode on the price to “override” rather than “restrict”, as follows:

![User interface showing a search policy rule with field set to Price, operator set to Less than, value set to 7, conflict handling set to Override, and filter mode set to Hard filter.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltae1b40d312cf59e6/6a170f92cdacbfa1277d2ac6/c2621e6513281f545b84eb77362f2b93e1c46a1f-996x70.png)

With this override, the query for “cheap chocolate” ignores maximum price that is defined in the “cheap chocolate policy” and only applies the price specified in the “Christmas chocolates” policy, as follows:

![Screenshot of a transformation pipeline detailing how the initial query “cheap chocolate” is processed by two filter rules, showing added category and price filters, hard filter and soft boost modes, conflict handling outcomes, rule priorities, and removal of a price filter due to a conflict.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4a47aa71c925b4a3/6a170f94ab7f0863d3db9f6d/d50da7900beb3c08439e9fd79cbe2ddd98196441-511x389.png)

This is similar to the previous example, with the difference being that the max price is set to the $7 value from the higher-priority policy because that policy specified “Override” on conflict. With the Christmas price filter taking precedence, the results look as follows:

![Search results page for the query “cheap chocolate,” showing category and brand filters on the left and a list of chocolate products on the right, including multiple advent calendars with images, prices, categories, and a displayed total of 10,000 results.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2b9ac1a62437c967/6a170f96839dfa3f58dcffb9/635ee6353ba84727486e7e053764788fb26b6f44-1134x1079.png)

These three variations (override, soft\_boost, and override on price) demonstrate a key property of the system: A merchandiser can change how two policies interact by modifying a setting on a single field within a single policy, without deploying any code. The conflict strategy is the lever that controls business behavior.

## Consumed phrase tracking

There’s a subtler form of conflict: two policies that match on the same phrase. If a higher-priority policy removes "without peanuts" from the query, a lower-priority policy that also matched on "without" has nothing left to act on. The system detects if the matched phrase is no longer present in the rewritten query and skips the lower-priority policy.

Intent policies are exempt from consumed phrase tracking: They set the retrieval strategy based on the original query match, regardless of what text has been removed by higher-priority policies.

Priority ordering, per-field conflict resolution, and consumed phrase tracking together give the control plane a deterministic composition model. With that foundation in place, the system can make a routing decision that would be risky without it.

## Governance makes retrieval strategy safe

An important insight about routing to the correct retrieval method (text, semantic, or hybrid) is that it executes after governance. If your policies have already enforced "produce category”, then semantic retrieval becomes far less risky because the candidate set is constrained. A semantic search over 500 product items is a very different proposition from a semantic search over 500,000 SKUs. Governance narrows the blast radius before retrieval begins.

For example, without governance, a semantic query for “Fruit high in vitamin C under $4”, in addition to fruits, might return vitamin bottles, carrots, and green pepper. The control plane ensures that these undesired results aren’t even considered as part of the semantic expansion.

![Diagram showing a search query flowing from a user through an application server and control plane, where matching rules are looked up, the query is rewritten with semantic intent including category and price constraints, and results are retrieved from a product catalog with non-matching products excluded.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltdaa3ff1bb3afaa36/6a170f97acf088954bbe9c1f/6dccd5b8a94bfa81f68e3d1c4ad8929ce8cc4e5e-990x378.png)

With that constraint in place, the control plane applies pragmatic routing logic:

* **Lexical** for navigational and head queries where deterministic precision matters.
* **Semantic** for descriptive discovery queries where concept matching helps.
* **Hybrid** selectively, when constraints have already been enforced and the business accepts broader recall.

## From architecture to implementation

The governed control plane translates business intent into deterministic, composable execution plans, without embedding that logic in application code. Policies are data: matched at query time, resolved through explicit per-field conflict strategies, and applied as cascading transformations that produce explainable results. Elastic Services Engineering has built and deployed this architecture for enterprise ecommerce teams, using repeatable patterns and accelerators that compress the path from concept to production. You can see a demo of our implementation of a control plane on YouTube at: [Fixing Search Relevance in Seconds: Introducing PRISM](https://www.youtube.com/watch?v=e1GuL9CYWAk).

### **What's next in this series**

The next post goes hands-on with the implementation: how the Elasticsearch percolator powers the policy lookup, including index mappings, boundary markers, highlight-driven phrase tracking, and concrete query examples.

## Put governed ecommerce search into practice

The control plane architecture described in this post (per-field conflict resolution, cascading policy transformations, and governance-constrained retrieval routing) was designed and built by Elastic Services Engineering. Every pattern, screenshot, and transformation pipeline shown in this series comes from a working system built by Elastic Services Engineering and validated against enterprise-scale product catalogs.

If you want to implement a governed, policy-driven control plane on Elasticsearch, [Elastic Services](https://www.elastic.co/consulting) can get you there faster.

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