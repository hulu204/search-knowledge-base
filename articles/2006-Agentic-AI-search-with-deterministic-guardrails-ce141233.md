---
title: 'Agentic AI search with deterministic guardrails in Elasticsearch for safe query execution'
company: Elastic
tag: 工程相关
date: 2026-05-18
url: https://www.elastic.co/search-labs/blog/agentic-ai-search-deterministic-guardrail-query-execution
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Agentic AI search with deterministic guardrails in Elasticsearch for safe query execution

Agentic AI search systems often fail when LLMs generate queries directly. Learn how deterministic guardrails and a control plane architecture enable safe, reliable, and governed query execution with Elasticsearch.

May 18, 2026

[Alexander Marquardt](/search-labs/author/alexander-marquardt)[Honza Král](/search-labs/author/honza-kral)[Taylor Roy](/search-labs/author/taylor-roy)

[Operations](/search-labs/blog/category/operations)

Part of the series:

[Governed search patterns](/search-labs/blog/series/governed-search-patterns)

In this series

Share

[Parts 1 through 7](https://www.elastic.co/search-labs/blog/agentic-ai-search-deterministic-guardrail-query-execution) of this series described a governed control plane for ecommerce search. A user types a query. The control plane classifies intent, enforces business constraints, resolves policy conflicts, and routes to the appropriate retrieval strategy, all before the product catalog is ever queried. The entire architecture assumes that the input is a search string typed by a human shopper.

This final post asks: What changes when the input comes from an AI agent instead?

The answer is that the architecture doesn't change, but the stakes do. Every property of the governed control plane that matters for human-authored queries matters *more* when the upstream decision-maker is a large language model (LLM). Determinism, auditability, conflict resolution, and constraint enforcement become critical guardrails rather than operational conveniences, because the system producing the input is probabilistic by nature.

## The agentic search problem

The most common approach to AI-driven search is straightforward: Give the LLM the database schema, provide business rules in the prompt, and let the agent generate the query directly.

For an ecommerce chatbot, this means injecting the Elasticsearch index mapping, field types, category taxonomies, pricing logic, and business constraints into the agent's context window, and then asking the LLM to translate natural language into valid Elasticsearch Query DSL. The LLM becomes the query author.

This approach works in demos. It fails in production for four reasons.

### Context bloat

An enterprise ecommerce index mapping is not a trivial document. Field definitions, nested objects, multi-field configurations, and analyzer settings can run to thousands of tokens before any business logic is added. On top of the mapping, the agent needs category taxonomies (which in enterprise ecommerce can contain tens of thousands of values), pricing rules, brand hierarchies, eligibility constraints, and campaign logic.

The result is a context window dominated by structural metadata rather than the user's actual intent. This increases latency, increases token cost, and degrades the LLM's ability to follow instructions as the context grows. This is a well-documented phenomenon, sometimes called [*context rot*](https://www.trychroma.com/research/context-rot): As the prompt gets longer, the model's attention to any particular instruction weakens.

### Probabilistic hallucination

LLMs generate queries based on patterns in their training data and the context provided. When asked to produce Elasticsearch Query DSL, the model can hallucinate field names that don't exist, construct syntactically invalid query clauses, misapply filter types to the wrong field types, or produce queries that are syntactically valid but semantically wrong, returning results that don't match the user's intent.

Google Cloud's [BIRD benchmark for Text-to-SQL](https://cloud.google.com/blog/products/databases/how-to-get-gemini-to-deeply-understand-your-database) illustrates the ceiling of this approach. Google's state-of-the-art single-model result achieved between 70% and 80% accuracy, meaning that nearly one in four generated queries was incorrect. This is for SQL, which is far more standardized than Elasticsearch Query DSL. The error rate for LLM-generated Elasticsearch queries in a real production environment, with complex mappings and business-specific semantics, would likely be higher.

For a revenue-critical ecommerce system, a one in four query error rate isn’t a tuning problem to be solved iteratively. It’s an architectural limitation of the approach.

### The security gap

When the LLM has access to the database schema and acts as the query author, the system is vulnerable to indirect prompt injection. A user interacting with an ecommerce chatbot can craft inputs designed to manipulate the agent into generating unintended queries.

This isn’t a theoretical risk. [Prompt injection](https://www.elastic.co/blog/owasp-top-10-for-llms-guide) is one of the most actively researched attack surfaces in deployed LLM systems. The fundamental issue is that when the agent authors the query, there’s no structural boundary between user intent and query execution. The LLM is simultaneously interpreting the user's request and constructing the database operation. Any manipulation of the first directly affects the second.

### High-cardinality scaling failure

Certain ecommerce fields have extreme cardinality. A product catalog might have 17,000 category values, thousands of brand names, and hundreds of attribute combinations. Standard agentic workflows require injecting these values into the context so the LLM can select the correct one when constructing a query.

This creates an impossible trade-off: Either inject all possible values (consuming enormous context and degrading performance), inject a subset (and accept that the agent cannot reference values outside that subset), or fall back to ungoverned search. This connects directly to the core problem from [Part 1](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-improve-retrieval): If the LLM searches for “oranges” and Elasticsearch returns orange soda, the chat experience degrades in the same way a search experience does. The absence of governance means the system cannot enforce the shopper's intended resolution.

![A flow diagram shows a user request, "I want to make a refreshing drink...," leading to an LLM output of “oranges,” followed by an application server sending a text query for oranges to a product catalog, ending with results showing marmalade, whole oranges, and orange soda.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt14a980ba09d88ee8/6a16f34d66c4f98516f8bd97/f11c44feb5291002d4ec4ac79484ea39d4e48a95-642x133.png)

Retrieving relevant values dynamically based on the query is a known alternative, but it introduces an additional nondeterministic step where the retrieval itself can miss relevant values. Additionally, this adds latency and complexity to every query.

## The architectural alternative: Decoupling intent from execution

The governed control plane described in Parts 1 through 7 offers a fundamentally different approach. Instead of the LLM authoring the final query, the LLM's role is reduced to a single, well-bounded task: extracting a search intent string from the user's natural language input.

The user says: "I'm looking for cheap brown shoes." The agent's job isn’t to generate an Elasticsearch query. It’s to extract and pass along the search intent, (in this case, something like "cheap brown shoes") to the control plane. The control plane then does what it has always done: percolates the intent string against stored policies, composes matching policies through cascading transformations, resolves conflicts deterministically, and produces a governed Elasticsearch query.

The LLM never sees the index mapping. It never knows about field types, category taxonomies, or pricing thresholds. It never constructs a query clause. It operates on the natural language side of an architectural boundary that we call the *metadata air gap*, a strict separation between the probabilistic component (the LLM) and the structured data layer (schema, policies, and query construction).

![A flow diagram shows a user request, “I want to make a refreshing drink...,” leading to an LLM output of “oranges,” followed by an application server sending the query to a control plane and then receiving a rewritten query, which is used to perform a text query for oranges in the Fruits category, ending with a product lookup that returns images of oranges.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltb4d701bfa4f2f279/6a16f34e1949f70ddce7a78d/12dacc77f0c481c9ada84725eff370c7e2c4b429-642x143.png)

### What the metadata air gap provides

* **Schema blindness.** The LLM has no access to the database schema and therefore cannot generate invalid queries, hallucinate field names, or be manipulated into exposing structural information. The schema exists only on the deterministic side of the air gap.
* **Minimal context.** Instead of thousands of tokens of mapping data, business rules, and category taxonomies, the LLM's prompt contains only a persona and intent extraction instructions. This dramatically reduces token cost, latency, and context rot.
* **Deterministic execution.** Every query that reaches Elasticsearch is constructed by the control plane using human-vetted policy templates, not generated probabilistically by an LLM. Syntactic validity is guaranteed. Semantic correctness is enforced by the same policy framework that Parts 1 through 6 described.
* **Security by architecture.** Prompt injection becomes structurally ineffective. Even if a user manipulates the agent into producing an unusual intent string, that string is percolated against stored policies. If no policy matches, no query is generated. The user cannot instruct the agent to construct a query because the agent doesn't construct queries. The control plane does, and the control plane is deterministic.

## How the pieces connect

The following walkthrough shows how the governed control plane handles an agent-mediated query.

### Step 1: The user speaks to the agent

A shopper interacting with an ecommerce chatbot says: "I'm looking for cheap chocolate, nothing with peanuts."

### Step 2: The agent extracts intent

The LLM's role is intent extraction, not query generation. Given a minimal prompt that instructs it to identify the product intent, the agent produces a search intent string: "cheap chocolate without peanuts".

This is a lightweight classification task. The LLM doesn’t need the index mapping, category taxonomy, or pricing rules to perform it. It needs to understand natural language, which is exactly what LLMs are good at.

### Step 3: The control plane governs the query

The intent string "cheap chocolate without peanuts" is passed to the control plane, which percolates it against the policy index. Three policies match:

* The "cheap" policy (extracts "cheap", applies a price filter based on the product category).
* The "chocolate" policy (constrains results to chocolate categories).
* The "without" negation policy (extracts the exclusion target and applies a `must_not` filter)

The control plane applies these policies through the same cascading transformation described in [Part 3](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture) and [Part 4](https://www.elastic.co/search-labs/blog/elasticsearch-percolator-search-governance): priority ordering, per-field conflict resolution, consumed phrase tracking. If a “Christmas campaign” policy is also active, it composes with the product policies exactly as described in [Part 3,](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture) the agent's involvement doesn't change the governance model at all.

### Step 4: The governed query executes

The control plane produces a fully governed Elasticsearch query: a search for “chocolate”, constrained to the appropriate categories, with a price ceiling derived from the “cheap” policy, an exclusion filter for peanut-containing products, and any active campaign boosts applied. If the “chocolate” policy also includes economic optimization weights ([Part 7](https://www.elastic.co/search-labs/blog/ecommerce-search-optimization-query-governed)), those are applied as well. Margin boosting is set to 3.0x because “chocolate” is a browsing query where the retailer benefits from promoting higher-margin products. If the shopper has purchase history ([Part 6](https://www.elastic.co/search-labs/blog/elasticsearch-personalized-search-governed-ecommerce)), personalization signals are layered on top. This query is syntactically valid by construction and semantically correct by policy design.

### Step 5: Results return through the agent

The product results are returned to the agent, which presents them conversationally to the user. The agent's role in the return path is presentation: formatting results, answering follow-up questions, providing product details. The retrieval itself was governed, deterministic, and explainable.

## What the agent is good at (and what it isn't)

This architecture leverages the LLM for what it does well and protects the system from what it does poorly.

LLMs excel at understanding natural language intent. "I'm looking for cheap chocolate, nothing with peanuts" is a natural language understanding task, parsing intent, identifying product references, recognizing negation. LLMs handle this reliably because it's a classification problem, not a generation problem. The output is a short intent string, not a complex structured query.

LLMs struggle with precise structured output under complex constraints. Generating valid Elasticsearch Query DSL requires exact field names, correct clause nesting, appropriate filter types for each field, and consistent application of business rules across thousands of edge cases. These are exactly the properties that a deterministic system enforces trivially and that a probabilistic system enforces unreliably.

The governed control plane puts each component where it belongs: the LLM on the natural language side, the deterministic policy engine on the query construction side, and an architectural boundary between them.

## Governance constrains the blast radius

This is the same insight from [Part 3](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-control-plane-architecture), extended to the agentic context. In Part 3, we observed that governance makes semantic retrieval safer by narrowing the candidate set before retrieval begins. A semantic search over 500 products in a governed category is a fundamentally different proposition from a semantic search over 500,000 SKUs.

The same principle applies to agent-mediated queries. Without governance, an agent that misinterprets "cheap chocolate" could generate a query that searches the entire catalog with no price constraint, no category filter, and no exclusions. With governance, even if the agent produces an imperfect intent string, the control plane constrains the query to the policies that match. The worst case is that fewer policies fire, not that an unbounded query hits the product catalog.

Governance narrows the blast radius of probabilistic errors. This is true whether the probabilistic component is a semantic retrieval model or an LLM agent.

## LLM-suggested policies: Expanding coverage

[Part 2](https://www.elastic.co/search-labs/blog/ecommerce-search-governance-zero-deploy) introduced the idea that an LLM can suggest new policies that enter the same Author → Test → Promote pipeline as human-authored ones. In the agentic context, this becomes a powerful feedback loop.

An LLM can analyze query logs, identify patterns where the control plane has no matching policy (queries that fall through to unmodified retrieval), and suggest new policies to cover those gaps. A merchandiser reviews each suggestion, tests it, and promotes it if it produces the expected behavior. The governance model ensures that no LLM-suggested policy reaches production without human validation.

Over time, this creates a virtuous cycle: The control plane's policy coverage expands, the proportion of queries that require unmodified retrieval shrinks, and the system becomes progressively more governed, with every policy auditable, versioned, and individually reversible.

## The broader pattern: Deterministic guardrails for probabilistic systems

The architecture described in this series, a deterministic control plane that sits between a probabilistic input source and a data retrieval system, isn’t specific to ecommerce search. The same pattern applies wherever an AI agent needs to interact with structured data.

An agent querying a SQL database faces the same challenges: context bloat from schema injection, hallucinated column names, prompt injection risks, and high-cardinality value selection. An agent interacting with a ticketing system like Jira, a customer relationship management (CRM) system like Salesforce, or a code repository like GitHub faces analogous problems. In every case, the core architectural question is the same: Should the LLM author the query, or should the LLM extract intent and pass it to a deterministic layer that authors the query?

The governed control plane provides a repeatable answer to that question. Policies are data. Intent extraction is the LLM's job. Query construction is the control plane's job. The metadata air gap keeps them separated. And the governance framework (priority ordering, conflict resolution, cascading transformations, auditability) ensures that the deterministic layer is operationally manageable as the number of policies grows.

## Conclusion

The ecommerce search governance patterns described in this series (policies as data, the Author → Test → Promote workflow, cascading transformations, per-field conflict resolution, percolator-based reverse matching, and multi-tier fallback) were designed for a world where a merchandiser authors policies and a shopper types queries. But the architecture can enable much more than its initial use case.

When the input source is an AI agent rather than a human shopper, the governed control plane becomes the critical safety layer between a probabilistic system and a production data store. It provides the deterministic guarantees (syntactic validity, semantic correctness, auditability, and security) that enterprise systems require and that LLMs cannot provide on their own.

The deterministic control plane doesn’t replace the AI agent. It makes the AI agent safe to deploy.

## Put governed ecommerce search into practice

The governed control plane architecture described in this series, from the policy-as-data paradigm to the percolator-based lookup to personalization, economic optimization, and the agentic air gap, was designed and built by Elastic Services Engineering. Every pattern described across this series comes from a working system built and validated against enterprise-scale product catalogs.

If your team is building AI-powered search experiences and needs deterministic guardrails for agent-mediated queries, or if you want to implement a governed, business-editable search architecture on Elasticsearch, Elastic Professional Services can accelerate your implementation. Contact [Elastic Professional Services](https://www.elastic.co/consulting).

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