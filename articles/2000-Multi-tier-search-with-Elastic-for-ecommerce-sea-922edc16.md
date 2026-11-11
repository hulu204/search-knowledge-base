---
title: 'Multi-tier search with Elastic for ecommerce search governance: Fixing poor recall'
company: Elastic
tag: 召回
date: 2026-05-06
url: https://www.elastic.co/search-labs/blog/multi-tier-search-ecommerce-governance
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Multi-tier search with Elastic for ecommerce search governance: Fixing poor recall

Learn how to build a multi-tier retrieval strategy used to execute ecommerce governed search plans and improve recall management. We'll cover how to orchestrate semantic matching while maintaining stable results, facets, and pagination.

May 06, 2026

[Alexander Marquardt](/search-labs/author/alexander-marquardt)[Honza Král](/search-labs/author/honza-kral)[Taylor Roy](/search-labs/author/taylor-roy)

[Operations](/search-labs/blog/category/operations)

Part of the series:

[Governed search patterns](/search-labs/blog/series/governed-search-patterns)

In this series

Share

A common issue in ecommerce search is poor recall. This occurs when a system lacks a governed fallback strategy. The solution is a multi-tier execution model. This post describes a multi-tier retrieval strategy used to execute governed search plans. It explains how to orchestrate strict, relaxed, and semantic matching while maintaining stable results, facets, and pagination.

## **From policy logic to retrieval architecture**

[Part 3](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture) and [Part 4](https://www.elastic.co/search-labs/blog/elasticsearch-percolator-search-governance) provided a technical deep dive into the governed control plane and its implementation using the [Elasticsearch percolator](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/percolator). Once the logic layer has identified which policies to apply, the system must address the retrieval strategy used to execute the search.

Managing the transition from precision to recall is a critical function of any ecommerce search engine. For example, a basic search implementation often defaults to broad keyword matching. If a shopper searches for "organic Pink Lady apples", this can lead to irrelevant results, such as apple-scented dish soap, apple juice, or organic pink grapefruit, appearing at the top of the list simply because they share a common term. While these items are technically matches, they fail to satisfy the user's intent and typically lead to high bounce rates. However, a "No results" page is equally detrimental to conversion. This conflict is resolved by implementing a **three-tier execution model**, which uses the governed control plane to orchestrate a principled fallback strategy.

## **The three-tier execution model**

This architecture executes up to three retrieval tiers in a sequence, each with a specific matching logic.

### **Highest tier: Strict matching**

*Strict matching* is a lexical match that requires that **all** query terms appear in the product metadata.

* **The logic:** A search for "organic navel oranges" returns only products containing all three terms.
* **Application:** This tier provides the highest precision. When a customer types a precise product name, such as "organic navel oranges", they’re typically seeking that exact item rather than an alternative.

### **Mid-tier: Relaxed matching**

If the strict tier fails to return sufficient results, the system expands the search parameters.

* **The logic:** This tier allows for a subset of terms to lexically match, using [Elasticsearch's minimum\_should\_match](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-minimum-should-match) logic.
* **Application:** Relaxed matching maintains lexical grounding. A search for "organic navel oranges" might surface "navel oranges" (missing the "organic" term) or "organic oranges" (missing the "navel" term). These represent intuitive, keyword-based alternatives for the shopper.

### **Lowest tier: Semantic matching**

* **The logic:** This tier uses vector/semantic embeddings (such as Elastic Learned Sparse EncodeR [ELSER], E5, or Jina) to retrieve conceptually related products, regardless of direct keyword overlap.
* **Application:** A search for "organic navel oranges" might surface "mandarins" or "clementines”. This serves as the final retrieval tier, intended to provide relevant options when literal keyword matches are unavailable.

To see this multi-tier orchestration in action and how the Engine steps down from lexical to semantic matching, watch the video: [Eliminating Zero-Result Pages: PRISM’s Multi-Tier Search Fallback](https://youtu.be/k02NHvIAHsk?si=tJKwmc4ds3zjcRPF).

## **Tier orchestration: The "bucket filling" logic**

While the governed control plane provides the logic and the queries for each tier, the application layer is responsible for the execution. The application executes these tiers sequentially and excludes lower tiers once the accumulated result count on the first page reaches or exceeds 10 items (or whatever number of results you want to display on the first page). This threshold ensures a full first page of results while prioritizing the most accurate retrieval method.

### Scenario 1: High-intent search ("oranges")

The first tier returns 15 hits. Since 15 is more than 10, the current result set is locked to only strict matches (which can be paged through) and subsequent tiers are not executed.

```
Strict tier:   [##########]##### (>= 10 found: Exact matches)
Relaxed tier:  [          ]      (Tier bypassed)
Semantic tier: [          ]      (Tier bypassed)
```

### Scenario 2: Specific but limited results ("organic blood oranges")

The strict tier finds only four items. Since this is less than 10, the system triggers the relaxed tier, which finds 12 more relevant products. The combined total (16) meets the threshold of 10, so the current result set is locked to the strict and relaxed tiers. Subsequent paging will only surface results from these two tiers (preventing lower-quality semantic hits from appearing on later pages).

```
Strict tier:   [####      ]       (4 found)
Relaxed tier:  [    ######]###### (>= 6 found)
Semantic tier: [          ]       (Tier bypassed)
```

### Scenario 3: Abstract or intent-based search ("high vitamin C snacks")

Keyword matches are limited (only five hits between tiers 1 and 2). The system triggers the semantic tier to find conceptually relevant items, such as kiwis, guavas, or red peppers, to fill the result set. The result set for this query includes products from all tiers.

```
Strict tier:   [##        ]             (2 found)
Relaxed tier:  [  ###     ]             (3 found)
Semantic tier: [     #####]######################...
```

This orchestration optimizes for latency, as the computational cost of the semantic tier is only incurred when the keyword-based tiers are insufficient. Additionally, this allows fast-responding keyword results to be displayed while semantic results are integrated shortly after, maintaining a responsive user interface.

## **Determining intent via tier activation**

The logic used to fill the first page serves a critical secondary purpose: It acts as a diagnostic for user intent. The application uses the logic returned by the governed control plane to determine which tiers remain active for the current result set and paging.

If the strict and relaxed tiers together yield fewer than 10 results, the query is likely exploratory or abstract. In this case, activating the semantic tier is a benefit. Because the query is diagnosed as exploratory, the system allows the shopper to page through the entire depth of the semantic results. This provides access to conceptually related alternatives that lexical matching would have missed, which is appropriate for an abstract search.

Conversely, if the strict tier returns a robust set of results (for example, 30 hits), it confirms that the system has found high-precision matches. The user can page through those 30 hits and will likely find what they’re looking for. In this scenario, there’s no need to provide additional, less relevant exploratory hits. By disabling lower tiers for these high-precision queries, we ensure that a shopper deep diving into specific results isn’t distracted by irrelevant semantic fallback as they paginate through the current result set.

## **Governance across tiers**

A critical component of this architecture is that policies apply globally across all tiers. If a user has a "vegan" preference profile, the governed control plane injects that constraint into the strict, relaxed, and semantic queries. This ensures that even when the system uses semantic fallback to return "mandarins" for an orange search, the results remain compliant with the user's broader dietary preferences or business constraints.

## **The problem of facet instability**

A challenge with multi-tier search is maintaining consistent faceted navigation (sidebar filters). If a search for "chocolate" yields 12 strict results, the sidebar filters might show "dark" and "milk". If a user selects "dark" and the result count drops, a naive system might trigger the semantic tier to fill the page, which could suddenly introduce "red wine" into the filters due to a semantic relationship.

The governed control plane identifies which tiers contributed to the initial search and locks the facets to those tiers. This prevents the sidebar from changing unexpectedly during a filtered session, ensuring a stable user experience.

## **The pagination challenge: Seamless multi-tier paging**

Pagination in a tiered system requires precise state management. As established, the first page determines the scope of the **current result set**. If the first page required semantic results, the user can page through all available results from all three tiers. On the other hand, if the first page was satisfied by high-intent keyword matches, the semantic tier is not retrieved for that specific result set.

The governed control plane manages this through:

* **Tier locking:** The response includes an array identifying the contributing tiers. The front end returns this on subsequent requests to keep the tier composition consistent across all pages.
* **Dynamic offset calculation:** The back end calculates an offset based on the requested page and the total products returned in preceding tiers.**Example:** If the first page has returned seven strict matches and three relaxed matches, a request for page 2 (starting at index 10) would execute a relaxed tier query with an offset of three.
* **ID exclusion for lower tiers:** The system retrieves IDs from the higher tiers (which, by definition, will always be fewer than the page size threshold) and explicitly excludes them from lower-tier results using an ID-only query (which avoids the overhead of a full fetch phase for excluded items).

## **Summary**

The multi-tier approach ensures search results are precise when data is available and helpful when it is not. By providing a governed fallback sequence for the application to execute, the architecture maintains high relevance while eliminating "no results" scenarios.

## **What's next in this series**

The next posts in this series extend the governed control plane into new territory. Part 6 explores personalization (using purchase history boosting and cohort-aware policies), and Part 7 demonstrates per-query economic optimization. Stay tuned!

## **Put governed ecommerce search into practice**

The search architecture described in this post, where retrieval tiers, economic weights, and governance constraints compose into a single request, was designed and built by Elastic Services Engineering as part of our repeatable ecommerce search accelerators.

To learn more about applying these patterns to your business, [**Contact Elastic Professional Services**](https://www.elastic.co/contact)**.**

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3979255ddfc7f45/6a17e25ffaa913812f93c7cb/92c517a2e7b36122a18feee317a0215981b62b6b-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Operations](/search-labs/blog/category/operations)

### Your agents have been keeping receipts: turning Elastic Agent Builder's built-in OTel traces into token cost dashboards in Kibana

July 28, 2026|[Meghan Murphy](/search-labs/author/meghan-murphy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltd9be3378b7b18d00/6a6a33c6d137a512563e106b/86ddf69cfc68919fb0f708eb190c18fdc2b9479a-1999x1200.png)

[AutoOps](/search-labs/blog/category/autoops)[Elastic Cloud Hosted](/search-labs/blog/category/elastic-cloud-hosted)[Operations](/search-labs/blog/category/operations)

### Faster Elasticsearch issue triage with redesigned AutoOps

July 23, 2026|[Ori Shafir](/search-labs/author/ori-shafir)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt4be28a2b56f0f75b/6a6119e91b1d4902a46f1813/2997670e3ebae815e16cb1a336542a9ddd0de77e-1999x1072.png)

[Operations](/search-labs/blog/category/operations)

### 98.9% faster queries, 4x more indexing throughput: a systematic Elasticsearch performance diagnosis

July 15, 2026|[Aleksandar Panov](/search-labs/author/aleksandar-panov)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt840c7a0a5b92080f/6a1710f967045b3e5445c2cd/3793259b01a5653a7520393a2f006610de0d21e7-1280x720.png)

[Operations](/search-labs/blog/category/operations)

### Why ecommerce search needs governance

April 09, 2026|[Alexander Marquardt](/search-labs/author/alexander-marquardt)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter