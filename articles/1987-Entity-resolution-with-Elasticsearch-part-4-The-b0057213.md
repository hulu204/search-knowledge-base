---
title: 'Entity resolution with Elasticsearch, part 4: The ultimate challenge'
company: Elastic
tag: 工程相关
date: 2026-03-13
url: https://www.elastic.co/search-labs/blog/entity-resolution-elasticsearch-llm-challenges
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Entity resolution with Elasticsearch, part 4: The ultimate challenge

Solving and evaluating entity resolution challenges in a highly diverse “ultimate challenge” dataset designed to prevent shortcuts.

March 13, 2026

[Jessica Moszkowicz](/search-labs/author/jessica-moszkowicz)

[AI](/search-labs/blog/category/ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Part of the series:

[Entity resolution with Elasticsearch](/search-labs/blog/series/entity-resolution-with-elasticsearch)

In this series

Share

We’ve now seen intelligent entity resolution implemented in two ways. Both approaches begin the same way: entity preparation and extraction, followed by candidate retrieval with Elasticsearch. From there, we evaluate those candidates using a large language model (LLM), either through prompt-based JSON generation or through function calling, and require the model to provide a transparent explanation for its judgment.

As we saw in the [previous post](https://www.elastic.co/search-labs/blog/elasticsearch-entity-resolution-llm-function-calling), the consistency provided by function calling is not just a nice optimization; it’s essential. Once we removed structural errors from the evaluation loop, results on standard scenarios (such as those in the tier 4 dataset) improved dramatically.

Yet there’s an obvious question left to answer:

*Does this approach still work when things get genuinely messy?*

Real-world entity resolution rarely fails because of simple cases. It fails when names cross languages, cultures, writing systems, time periods, and organizational boundaries. It fails when people are referenced by titles instead of names, when companies change names, when transliterations aren’t consistent, and when context (not spelling) is the only thing tying a mention to a real-world entity.

So, for the final post in this series, we put the system through what we called **the ultimate challenge**.

## What makes this the ultimate challenge?

In earlier evaluations, we tested the system using increasingly complex datasets. By the time we reached tier 4, discussed in the previous post, we were already dealing with a mix of nicknames, titles, multilingual names, and semantic references. Those tests showed that the architecture itself was sound, but that reliability issues, especially malformed JSON, were suppressing recall.

With function calling in place, we finally had a stable foundation. That gave us the opportunity to ask a more interesting question:

*Can one unified pipeline handle* ***many different kinds*** *of entity resolution problems at once?*

The ultimate challenge dataset was designed to push precisely on that dimension.

Instead of focusing on a single difficulty (like nicknames or transliteration), this dataset combines **50+ distinct challenge types**, including:

* Cultural naming conventions.
* Title-based references.
* Business relationships and historical name changes.
* Multilingual and cross-script mentions.
* Compound challenges that mix several of the above.

Crucially, this isn’t about optimizing for any one narrow use case. It’s about testing whether the *design pattern* holds up when the rules change from entity to entity.

## The dataset at a glance

The ultimate challenge dataset consists of:

* **50 entities**, spanning people, organizations, and institutions.
* **~60 articles**, with varying structure and linguistic complexity.
* **51 distinct challenge categories**, grouped broadly into:

  + Cultural naming conventions.
  + Titles and professional context.
  + Business and organizational relationships.
  + Multilingual and transliteration challenges.
  + Combined and edge‑case scenarios.

Earlier in the series, we saw that using generative AI (GenAI) to create datasets can be a mixed blessing. Without it, assembling sufficiently large and diverse test data would be extremely difficult. But left unchecked, the model has a tendency to make things too easy.

On an early generation pass, for example, we discovered that the model had included phrases like “the Russian president” as explicit aliases for Vladimir Putin. That might seem reasonable today, but it defeats the purpose of testing contextual resolution. What happens if the article is discussing Russia in the 1990s? The system should infer the correct entity from context, not rely on a hard-coded alias.

For that reason, this dataset was deliberately designed so that **shortcuts don’t work**. Aliases are not explicitly listed when the system is expected to infer meaning. Descriptive phrases are not prelinked to entities. Correct matches often depend on article-level context, not just local text.

**Important note:** Although we demonstrate the system’s capabilities across diverse scenarios, this is still an educational prototype. Production systems handling real-world sanctioned-entity monitoring would require additional validation, compliance checks, audit trails, and specialized handling for sensitive use cases.

## Why these scenarios are hard

Back in the first post in this series, we introduced a simple but ambiguous example: “The new Swift update is here!” The challenge is that “Swift” can resolve to multiple real-world entities, depending on context. That example captures a broader truth: Natural language is inherently ambiguous.

Entity resolution, therefore, is not just a string-matching problem. Humans routinely rely on shared knowledge, cultural norms, and situational context to resolve references, and we rarely even notice we’re doing it.

Consider a few common cases:

* A title like “the president” is meaningless without geopolitical and temporal context.
* A company name may refer to a parent, a subsidiary, or a former brand depending on when the article was written.
* A person’s name may appear in different orders, scripts, or transliterations, depending on language and culture.
* The same phrase can legitimately refer to different entities in different contexts, and the system must be able to *reject* matches just as confidently as it accepts them.

There is no single rule set that handles all of this cleanly. That’s why this prototype separates concerns so aggressively:

* Elasticsearch narrows the candidate space efficiently and transparently.
* The LLM is used only where judgment is required and is forced to explain itself.
* Retrieval and reasoning remain distinct steps.

This separation becomes even more important as the diversity of challenge types increases.

## How the system handles diversity without special cases

One of the most interesting outcomes of this evaluation is what *didn’t* change:

* We did **not** add special logic for Japanese names.
* We did **not** add custom rules for Arabic patronymics.
* We did **not** add hard-coded mappings for historical company names.

Instead, the system relied on the same core ingredients introduced earlier in the series:

* Context-enriched entities indexed for semantic search.
* Hybrid retrieval (exact, alias, and semantic) in Elasticsearch.
* A small, well-defined set of candidate matches.
* LLM judgment constrained by function calling and minimal schemas.

This suggests that the system’s flexibility comes from **representation and architecture**, not from an ever-growing collection of rules.

When the system succeeds, it’s because the right candidates are retrieved and the LLM has enough context to explain why a reference does (or does not) map to a specific entity.

## Results: How did it perform?

On the ultimate challenge dataset, the system produced the following overall results:

* **Precision:** ~91%
* **Recall:** ~86%
* **F1 Score:** ~89%
* **LLM acceptance rate:** ~72%

### Performance across challenge types

Breaking down results by challenge type reveals strengths and limitations:

**Strongest performance (100% F1 score)** was observed in areas such as:

* Cross-script matching (Cyrillic, Korean, Chinese business entities).
* Hebrew scenarios (patronymics, professional titles, religious titles, transliteration).
* Business hierarchies (aerospace, diversified manufacturing, multidivision corporations).
* Professional titles (academic, military, political, religious).
* Combined Japanese scenarios involving multiple writing systems.

**Strong performance (80–99% F1 score)** included:

* International political figures (98%).
* Historical name changes (90%).
* Complex business hierarchies (89%).
* Japanese company names (93%).
* Cross-script transliteration (86%).
* Arabic patronymics (86%).

**More challenging areas** included:

* Advanced transliteration (Chinese, Korean): 0% F1.
* Certain Japanese scenarios (honorifics, name order, writing system variation): ~67% F1.
* Some Arabic scenarios (company names, institutional references): ~40% F1.

What’s important here is *why* the system struggled in these cases. The failures were not due to the overall approach breaking down, but to limitations in specific components, most notably the dense vector model used for semantic search in certain multilingual scenarios.

Because retrieval and judgment are cleanly separated, improving performance does not require rewriting the system. Swapping in a more capable multilingual embedding model, enriching entity context, or refining retrieval strategies would improve results across these categories without changing the core architecture.

From an architectural standpoint, that’s the real success metric.

## What this tells us about the design

Looking back across the series, a few patterns stand out:

* **Preparation matters more than clever matching.** Enriching entities with context up front dramatically reduces ambiguity later.
* **LLMs are most valuable as judges, not retrievers.** Asking them to explain *why* a match makes sense is far more powerful than asking them to search.
* **Reliability enables accuracy.** Function calling didn’t just clean up JSON; it unlocked recall that was already latent in the retrieval step.
* **Generalization beats specialization.** A small number of well-chosen abstractions handled dozens of challenge types without custom logic.

This is why the prototype is intentionally Elasticsearch-native and intentionally conservative in how it uses LLMs. The goal isn’t to replace search; it’s to make search explainable in situations where meaning matters.

## Final thoughts

The ultimate challenge wasn’t about chasing perfect metrics; it was about answering a more fundamental question:

*Can a transparent, search-first, LLM-assisted architecture handle real-world entity ambiguity without collapsing into rules or black boxes?*

For this educational prototype, the answer is yes, with clear caveats around production hardening, compliance, monitoring, and data quality. If you’re building systems that need to justify *why* an entity match was made, this pattern is worth serious consideration. I hope this series has shown that entity resolution doesn’t have to be mysterious. With the right separation of concerns, it becomes something you can reason about, measure, and improve.

This work also suggests a broader architectural pattern. What emerges is a slight but important evolution of classic retrieval augmented generation (RAG). Instead of allowing retrieval to feed generation directly, we introduce an explicit evaluation step. The LLM is first used to judge and sanity-check retrieved candidates, and only those approved results are allowed to augment generation. You can think of this as Generation-Augmented Retrieval-Augmented Generation with Evaluation, or GARAGE, because who doesn’t love a good acronym.

What other use cases could benefit from this pattern? Systems that require trust, transparency, and defensible reasoning are natural candidates. Future work in this area should prove as compelling as the results we’ve seen here, and I’m excited to see where the community takes it next.

## Next steps: Try it yourself

Want to see the ultimate challenge in action? Check out the [**Ultimate Challenge notebook**](https://github.com/jesslm/entity-resolution-lab-public/tree/main/notebooks#:~:text=5%20minutes%20ago-,05_ultimate_challenge_v3.ipynb,-Initial%20public%20lab) for a complete walkthrough, with real implementations, detailed explanations, and hands-on examples.

The complete entity resolution pipeline demonstrates the core concepts and architecture needed for production use. You can use it as a foundation to build systems that monitor news articles, track entity mentions, and answer questions about which entities appear in which articles, all while retaining transparency and explainability.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter