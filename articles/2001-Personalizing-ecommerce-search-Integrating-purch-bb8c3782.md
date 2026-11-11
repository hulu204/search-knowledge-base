---
title: 'Personalizing ecommerce search: Integrating purchase history and user cohorts'
company: Elastic
tag: 排序
date: 2026-05-11
url: https://www.elastic.co/search-labs/blog/elasticsearch-personalized-search-governed-ecommerce
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Personalizing ecommerce search: Integrating purchase history and user cohorts

Learn how to create a personalized ecommerce search experience in Elasticsearch without breaking governance. This post explains how to boost products a shopper has purchased before and how to activate cohort-specific policies based on user profiles.

May 11, 2026

[Alexander Marquardt](/search-labs/author/alexander-marquardt)[Honza Král](/search-labs/author/honza-kral)[Taylor Roy](/search-labs/author/taylor-roy)

[Operations](/search-labs/blog/category/operations)

Part of the series:

[Governed search patterns](/search-labs/blog/series/governed-search-patterns)

In this series

Share

[Parts 1 through 5](https://www.elastic.co/search-labs/blog/series/governed-search-patterns) of this series describe a governed control plane that classifies intent, enforces constraints, resolves policy conflicts, and routes to the appropriate retrieval strategy, all before the product catalog is queried. Every mechanism described so far treats all shoppers identically. A search for "chocolate" produces the same governed result set, whether the shopper is a vegan, a parent buying for a child's birthday, or a halal-observant consumer.

This post introduces two personalization mechanisms that extend the governed control plane without changing its architecture. Both mechanisms stack multiplicatively with the governance layer from Parts 1 through 5: Policies still fire, constraints are still enforced, conflicts are still resolved, and personalization signals are composed into the same governed query, ensuring that the results Elasticsearch returns are already personalized.

The first mechanism boosts products the individual shopper has purchased before. The second activates cohort-specific policies based on the shopper's profile. Together, they demonstrate that personalization is not a separate system bolted alongside search or applied as post-retrieval processing; it’s a natural extension of the policy-driven control plane.

For a deep dive into the mathematics of the personalization techniques used in this post, see [Personalizing search in Elasticsearch without ML post-processing](https://alexmarquardt.com/elastic/personalizing-search-in-elasticsearch-without-ml-post-processing/) and [Cohort-aware ranking in Elasticsearch](https://www.elastic.co/search-labs/blog/ecommerce-search-relevance-cohort-aware-ranking-elasticsearch).

To see a live demonstration of how purchase history can be used to boost search results for returning customers, watch the video: [Explainable Personalization: Boosting Search with Purchase History](https://www.youtube.com/watch?v=TGf_pOWHA5M).

## Individual purchase history boosting

The simplest form of personalization is also one of the most effective: If a shopper has bought a product before, boost it when they search for something related. A shopper who regularly buys a particular brand of chocolate chip cookies should see those cookies ranked higher when they search for "cookies", not because a model predicted a preference, but because there’s direct behavioral evidence.

### How it works

When a search request includes a user identifier, as would be the case for a user that has an open session, the control plane runs two Elasticsearch queries in parallel using a thread pool:

1. The percolator query against the policy index (the same governance lookup described in Parts 3 and 4).
2. A purchase history query against a `user_purchases` index, filtered to the specific user by `term(user_id)` and then matching the current search string against that user's product titles.

These run concurrently (neither waits for the other), so the personalization lookup adds no meaningful latency to the governance pipeline.

The purchase history query uses [Elasticsearch's text analysis](https://www.elastic.co/docs/manage-data/data-store/text-analysis) (stemming, tokenization) when matching the current search string against stored product titles. This means a search for "cookies" will match a past purchase of "brownie cookies" through standard text analysis, without requiring exact string matching.

### Computing boost weights

Not all past purchases deserve the same boost. The weight accounts for two intuitive factors: how often the shopper bought the product, and how recently. A product purchased 15 times last week is a much stronger signal than a product purchased once six months ago. The weighting uses logarithmic scaling on frequency (so a single heavily purchased item doesn't overwhelm everything else) and exponential decay on recency (so older purchases fade naturally over time).

For the mathematical details of the boost formula, see [Personalizing search in Elasticsearch without ML post-processing](https://alexmarquardt.com/elastic/personalizing-search-in-elasticsearch-without-ml-post-processing/).

### How it becomes a query

The purchase history boosts are composed into the query as the outermost scoring layer, wrapping the governance policy filters and boosts from Parts 3 and 4 and any [business-signal boosts, such as margin and popularity](https://www.elastic.co/search-labs/blog/function-score-query-boosting-profit-popularity-elasticsearch) (which we’ll explore in Part 7). This means a product that’s removed by a governance policy won’t reappear because of a purchase history boost. *Governance* controls the result set; *personalization* adjusts ordering within it. Products without any purchase history are not penalized. Their governed ranking is preserved, though products with relevant purchase history will rank above them, all else being equal.

![A flowchart shows how a user’s search for “oranges” moves through an application server, a control plane, purchase history and policy lookups, and then a product catalog index to return orange product results.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt731e67dfd3bd6ee2/6a17e9523e9e4582bbba14b6/80f0285bd80935703d39b7a4e1fd6094d71af0aa-545x273.jpg)

### Why query Elasticsearch on every search?

The purchase history is queried from Elasticsearch on every search rather than cached in the application layer. This is a deliberate design choice. Because the query matches the current search string against product titles using Elasticsearch's text analysis pipeline, the system benefits from the same stemming, tokenization, and language handling that powers the product search itself. A cached in-memory lookup would require reimplementing that analysis or accepting cruder matching.

To see why this ordering matters, consider a shopper who previously purchased orange juice and now searches for "oranges”. The purchase history query matches "orange juice" against the search term "oranges" through text analysis and computes a boost for that product. But the governance layer has already constrained "oranges" to the produce category, filtering out orange juice entirely. The purchase history boost for orange juice is present in the query, but it has no effect because there’s no matching document in the governed result set for it to act on. The shopper sees fresh oranges, ranked by relevance and personalization. The governance guardrail holds.

The performance cost is minimal: The purchase history index is small (a user's purchase history is typically dozens to hundreds of documents, not millions), and the query runs in parallel with the percolator lookup, so it doesn't extend the critical path.

### Example query for “spring water” without user history

If a non-logged-in user or a user that has never purchased “spring water” searches, they might see results similar to the following:

![A webpage displays search results for “spring water”, showing a search bar, category and brand filters, and three product listings with details such as brand, composition, and price.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt90249896bcf2b8c2/6a17e954af47b685f5cddfcf/1d03558c8f6492a0999e1ac4f1d22680c8f3a6ce-1130x1028.png)

### Example user purchase history

On the other hand, a user called Carol has a shopping history that contains the following products:

![A digital interface titled “Purchasing Profile” shows a shopper named Carol with two cohorts and a list of recently purchased items, including quantities, last purchase dates, and time since each purchase.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3aa784ccb0653a0d/6a17e95563baffd6b7741c8d/31c1fb789efc6cef673984e9711d571efce8ed27-661x523.png)

### Example search for “spring water” with the above purchase history

If Carol searches for “spring water”, she’ll see personalized results that reflect what she has purchased in the past. Looking at the purchase history above, she purchased “Carbonated Spring Water” (the green bottle) above, about 40 times, and most recently two days ago. If she searches for “spring water”, then that product is boosted up, as we know that she likes it. Notice that in the non-personalized results, the Rubicon spring water was the first hit instead.

![A web page shows search results for “spring water”, listing product details, prices, and filter categories for beverages and brands.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf243c5ef1a1808ba/6a17e95763baff5d73741c91/6fce63ff051e345a79fef934cd6e71ba113ae585-1159x1062.png)

## Cohort-aware policy activation

Individual purchase history works well for returning customers with established behavior. But many shoppers are new, anonymous, or browsing outside their usual patterns. For these shoppers, cohort membership provides a different kind of personalization, one based on who the shopper is, not what they've done.

A vegan shopper searching for "chocolate" should see vegan chocolate ranked higher. A halal-observant shopper searching for "snacks" should see halal-certified options prominently. A health-conscious shopper searching for "yogurt" should see probiotic options boosted.

### Cohorts as policies, not product tags

Products already carry their normal attributes, including fields like `dietary_restrictions: ["vegan"]` or `dietary_restrictions: ["halal"]`. The question is where the logic lives that connects a shopper's cohort to those product attributes.

The naive approach would be to hard-code that mapping in the application layer or in the search template: If the user is vegan, add a boost on `dietary_restrictions: "vegan"`. But this is the same application-layer spaghetti described in [Part 1](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-improve-retrieval), and it creates the same operational friction: Adding a new cohort or changing what a cohort means requires a code change.

The governed control plane keeps the cohort logic in the policy engine instead. A cohort policy bridges two things: a shopper's cohort membership (for example, “vegan”) and a product attribute (for example, `dietary_restrictions: “vegan”`). The policy defines the connection: When a shopper in the vegan cohort searches, boost products where `dietary_restrictions` includes “vegan”.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte15937af719dff39/6a17e95925daab370608a274/2b6fe359774bbea059aaf93f3fa4a03eb31233ea-544x290.jpg)

Because cohort logic lives in the policy engine rather than application code, this means:

* Adding a new cohort can be done by creating a new policy; no product reindexing required.
* Cohort policies use the full rule engine: They can add filters, apply soft boosts, expand synonyms, change retrieval strategy, or any other action a policy can take.
* Cohort behavior is managed through the same admin UI as all other policies: A merchandiser can create, test, and promote cohort policies through the Author → Test → Promote workflow described in [Part 2](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-zero-deploy).

### Example vegan cohort policy

A merchandiser creates a cohort policy with the following characteristics:

* **Cohorts:** `["vegan"]`.
* **Match criteria:** Matches any query (or a specific product category).

**Action:** Soft boost on `dietary_restrictions: "vegan"` with a boost weight of 2.

![A web interface titled “Edit rewrite policy” shows fields for policy ID, title, description cohort selection, rule query options, rule type, filter settings, and more, with a focus on the cohort containing “vegan” and one on the value "vegan”.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt835034b54f6790b8/6a17e95b7b54f980408b391e/fc58bbd97c0dd1fa3ce757394ca117d0789c52f6-1080x1018.png)

### How cohort activation works

Each policy document has a `cohorts` field. Universal policies that apply to all shoppers regardless of cohort can leave this field blank, and these will internally be assigned a value of `"_all"` by the control plane. Cohort-specific policies store their target cohort names, such as `["vegan", "kosher", “sweet_tooth”]`.

When a search request includes a user profile, the control plane constructs a simple `terms` filter for the percolator query:

```
{ "terms": { "cohorts": ["_all", "vegan", "health_conscious"] } }
```

This single filter includes all universal policies plus the user's cohort-specific policies. The `_all` sentinel makes this a clean inclusion filter: No `must_not` or `exists` queries are needed to handle the case where a policy has no cohort restriction.

The percolator then evaluates policy matches as usual. The only difference is that the candidate policy set has been narrowed to those relevant to this shopper's cohorts. Everything downstream (cascading transformations, per-field conflict resolution, consumed phrase tracking) operates identically to the non-personalized flow described in Parts 3 and 4.

### Non-vegan (standard) user results when searching for “chocolate”

When a non-vegan user searches for chocolate, there’s no vegan cohort boost applied to their results. They would often see non-vegan chocolates in the top hits, as follows:

![A web page shows search results for “chocolate”, with category and brand filters on the left and three chocolate product listings with descriptions, prices, and specifications.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltc5244b19c2162f5b/6a17e95d3e03d727f74f2cb6/5bade79944ef294e2cb835cfd6e3231392e8fbd0-1159x1104.png)

### Vegan cohort policy results when searching for “chocolate”

When a vegan-cohort shopper searches for "chocolate", this policy is included in the percolator candidate set. It matches, and the control plane applies a soft boost to vegan-certified chocolates. The boost is multiplicative: Vegan chocolates rank higher, but non-vegan chocolates are not fully excluded because the above filter is defined as a *soft boost*, which we described in detail in Part 3 of this series.

![A web page shows search results for “chocolate”, with category and brand filters on the left and three chocolate product listings with descriptions, prices, and specifications, with a focus on the circled vegan labels.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf73ce626bcd3d66d/6a17e95f2f4a5c5341fa8934/fc6f7ec6a9de30f3a6d8f32bb9ee7ec457dea458-1138x1255.png)

However, if the shopper explicitly searches for "Hershey milk chocolate", the vegan boost still applies but may be outweighed by the stronger text relevance of Hershey milk chocolate products.

![A web page shows search results for “Hershey milk chocolate”, with category and brand filters on the left and three Hershey’s chocolate product listings, with detailed descriptions, prices, and nutritional information.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0e7487727387e524/6a17e9617b54f965ab8b3922/f47bb8bfa58106f897c4c6c143494f4367355528-1136x1142.png)

A shopper outside the vegan cohort searching for the same query never sees the “vegan cohort” policy; it’s not in their candidate set. The governance layer is identical; only the active policy set differs.

### Cohorts with purchase history

A vegan shopper with extensive purchase history gets vegan-cohort-specific policy activation as well as purchase history boosts. For new or anonymous shoppers, implied cohort membership alone provides meaningful personalization without requiring any behavioral data (for example, perhaps an anonymous user has only searched for vegan products, and so we classify them as a member of the vegan cohort). A shopper who self-identifies as halal-observant during account creation immediately receives halal-tailored results on their first search.

![A flow diagram shows how a search for “oranges” moves through an application server, a control plane, history and policy lookups, and then a product index to return orange products.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt89044f002807c2e4/6a17e962af47b64034cddfd3/81af35a533a567d99324860c8e69cf9752533c8f-545x301.jpg)

## How personalization layers compose

The nesting order of `function_score` layers matters. From innermost to outermost:

1. **Base query:** The keyword or semantic match with named queries (`fulltext_match`, `title_phrase_match`).
2. **Governance policy layer:** Hard filters as `bool.filter` clauses, soft boosts as `function_score` functions (Parts 3 and 4).
3. **Business-signal boosts:** Margin and popularity boosting (which we’ll explore in Part 7).
4. **Purchase history boosts:** The outermost `function_score` layer.

This ordering ensures that governance controls the result set (what appears), business signals adjust ranking within that set (what appears first from the retailer's perspective), and purchase history adjusts ranking further based on individual behavior (what appears first from the shopper's perspective). Each layer wraps the previous one multiplicatively, so the effects compound rather than conflict.

## What this means operationally

Personalization through the governed control plane preserves every operational property described in Parts 1 and 2:

* **Zero-deploy changes.** Cohort policies are created, tested, and promoted through the admin UI. Adding a new dietary cohort or adjusting a boost weight requires no code changes and no engineering involvement.
* **Auditability.** Every cohort policy is a discrete, versioned document. When a merchandiser asks, "Why are vegan products ranking higher for this user?", the answer is a specific policy with a specific priority, visible in the debug panel alongside every other policy that fired for that query.
* **Conflict resolution.** Cohort policies participate in the same per-field conflict resolution described in Part 3. If a cohort policy's category boost conflicts with a campaign policy's category override, the conflict is resolved deterministically by the same priority and strategy framework, no special handling needed.
* **Measurability.** Because cohort policies are discrete and individually toggleable, their impact on conversion, click-through, and add-to-cart rates can be measured independently, just like any other policy in the system.

## What's next in this series

The next post explores another dimension of the governed control plane: how margin and popularity boosting can be tuned per query through policies, turning economic optimization into a governance decision rather than a static configuration.

See Part 7: Query-governed economic optimization: Per-query margin and popularity boosting

## Put governed ecommerce search into practice

The personalization patterns described in this post (individual purchase history boosting and cohort-aware policy activation) were designed and built by Elastic Services Engineering as part of our repeatable ecommerce search accelerator. Both mechanisms integrate with the governed control plane architecture described throughout this series. Contact [Elastic Professional Services](https://www.elastic.co/consulting).

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