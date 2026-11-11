---
title: 'Entity resolution with Elasticsearch & LLMs, Part 2: Matching entities with LLM judgment and semantic search'
company: Elastic
tag: 工程相关
date: 2026-02-26
url: https://www.elastic.co/search-labs/blog/elasticsearch-entity-resolution-llm-semantic-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Entity resolution with Elasticsearch & LLMs, Part 2: Matching entities with LLM judgment and semantic search

Using semantic search and transparent LLM judgment for entity resolution in Elasticsearch.

February 26, 2026

[Jessica Moszkowicz](/search-labs/author/jessica-moszkowicz)

[AI](/search-labs/blog/category/ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Part of the series:

[Entity resolution with Elasticsearch](/search-labs/blog/series/entity-resolution-with-elasticsearch)

In this series

Share

In [Part 1](https://www.elastic.co/search-labs/blog/entity-resolution-llm-elasticsearch), we prepared our watch list and extracted entity mentions. Now we’re ready to answer the hard question: Which entity does a mention actually refer to? Let's return to the example in the first blog of this series, which set up why we need entity resolution: "The Swift update is here!" Imagine that this headline is accompanied by a bit more context:

1. The new Swift update is here! Developers are eager to try out the new features.
2. The new Swift update is here! The new album will drop next month.

With this added context, we should be able to resolve the name "Swift" to the correct entity.

In the [previous post](https://www.elastic.co/search-labs/blog/entity-resolution-llm-elasticsearch), we set up our watch list and enriched the entities with additional context. Looking at our examples above, we need to have at least the following two entities in the list: Taylor Swift and Swift Programming Language. We also covered how we extract entity mentions from text. Both of these examples would extract "Swift". With these ingredients in place, the enriched watch list, and the extracted entities, we’re finally ready to introduce the star of the show: entity matching.

**Remember:** This is an educational prototype designed to teach entity-matching concepts. Production systems might use different large language models (LLMs), custom matching rules, specialized judgment pipelines, or ensemble approaches combining multiple matching strategies.

## The problem: Why matching is hard

Human language is a remarkable thing. One of the most interesting properties of it is its endless creativity. We can generate and understand an infinite number of new sentences. Is it any wonder, then, that exact matches in entity resolution are rare? Authors strive to be creative when they can. It would get quite tedious if we had to write and read full names whenever an entity is mentioned. So, while exact matches are easy, the reality is that we need a more sophisticated approach to entity resolution: one that’s robust enough to handle at least some of the boundless creativity of human authors. That’s why we separate the problem into two steps: Use Elasticsearch to retrieve plausible candidates at scale, and then use an LLM to judge whether those candidates truly refer to the same real-world entity.

## The solution: Three-step matching with transparent LLM judgment

We’re in the midst of a paradigm shift in how we use computers. Just as the rise of the internet took us from localized computing to a globally connected network, generative AI (GenAI) is fundamentally changing how content, code, and information are created. In fact, the educational prototype that accompanies this series was almost exclusively "vibe coded" using an LLM with careful prompting by the author. This is not to say that LLMs have or even will reach the kind of productivity inherent with human language, but it does mean that we now have a powerful resource to help with entity resolution.

A common pattern we use with GenAI is retrieval augmented generation (RAG). Here, *retrieval* means retrieving entity candidates (not generating answers), and the LLM is used strictly for match evaluation and explanation. While we *could* ask an LLM to help us with end-to-end entity resolution, that’s a costly approach, both in terms of time and money. RAG helps LLMs do their work by using more efficient ways to provide context to the LLM, thereby empowering the LLM to efficiently help with entity resolution.

For the retrieval part of RAG, we again turn to Elasticsearch. We first find potential matches using a combination of exact matching, matching against aliases, and hybrid search, which combines keyword and semantic search. Once we find these potential matches, we send them to an LLM for judgment. The LLM acts as the final match evaluator. We also make the LLM explain its reasoning, an important differentiator with other entity resolution systems. Without these explanations, entity resolution is a black box; with them, we can see for ourselves why a match makes sense.

## Key concepts: Three-step matching, hybrid search, and transparent LLM judgment

**What is three-step matching?** At the onset of this project, we hypothesized that semantic search will be a crucial part of the system, but not every match requires such sophisticated search. In order to find matches efficiently, we take a progressive approach to the problem. First, we check for exact matches using keyword search. If we find such a match, our work is done and we can move on. If exact matching fails, we turn to alias matching. In the prototype, alias matching is also done using exact matching with keywords, for simplicity. In production, you might expand this step with normalization, transliteration rules, fuzzy matching, or curated alias tables. If we still haven't found a potential match in the first two steps, then it's time to bring in semantic search via Elasticsearch's hybrid search with reciprocal rank fusion (RRF).

**What is hybrid search?** In Elasticsearch, we can use semantic search to find meaningful matches that take context into account. Elasticsearch is widely used for vector search and hybrid retrieval. Semantic similarity is powerful for meaning, but it’s not a substitute for structured filtering (for example, by time ranges, locations, or identifiers), and it’s often unnecessary when an exact match is available. Elasticsearch made its mark with lexical search, which is great at tasks where semantic search doesn't fit. To take full advantage of both approaches, we use lexical search alongside semantic search in a single hybrid query. We then merge the results to find the most likely matches using RRF. In the prototype, the top two results become potential matches that can be sent for LLM judgment.

**Why LLM judgment?** LLM judgments and explanations allow our system to handle ambiguity and context transparently. This is vital for cases like "the president", which could refer to multiple entities, depending on the context, but it also makes things like nicknames and cultural variations work well in the system. Finally, when we consider mission-critical tasks, like identifying entities from sanctions lists, we need to know why a match was accepted in order to trust the system. Crucially, the LLM does not search the full corpus; it evaluates only the small set of candidates returned by Elasticsearch.

## Real-world results: Matching with LLM reasoning

A major challenge for any natural language processing task is the creation of a golden document, an "answer key" that tells us what the expected results are. Without this, it's next to impossible to judge how well a system performs on a task, but creating such a document can be a laborious process. For the entity resolution prototype, we turned again to GenAI to help set up data we could test against.

We first defined several challenge types, such as nicknames and transliteration, and then asked the LLM to create a tiered collection of datasets that would get progressively larger and more challenging for the system. The creation of the datasets was less straightforward than one might hope. The LLM had a strong propensity for "cheating" by making it too easy to get the right answer. For example, one of the challenge types focused on semantic context. This type included things like resolving "Russian author" to "Leo Tolstoy". The LLM incorrectly put "Russian author" as an alias for "Leo Tolstoy", which negated the need for hybrid search to find the match.

After several refactorings to fix issues like this, we had five dataset tiers to work with. Tiers 1–4 were progressively larger with more challenge types. Tier 5 was the "ultimate challenge" dataset, made up of the trickiest examples from all challenge types. All of the test data is available in the [comprehensive evaluation directory](https://github.com/jesslm/entity-resolution-lab-public/tree/main/comprehensive_evaluation).

To evaluate our prompt-based entity resolution approach, we focused our attention on the tier 4 dataset. An important note is that the evaluation was conducted as a controlled experiment so that we could focus on entity match quality. The watch list data was pre-enriched with context, and entities were extracted from the article ahead of time. This ensured that evaluation was focused on matching rather than on extraction accuracy. This isolates match quality; end-to-end performance would additionally depend on extraction recall and enrichment quality.

### Evaluation dataset

The tier 4 evaluation dataset provides a comprehensive test of the system's capabilities:[1]

* **Watch list entities:** 66 entities across diverse types (people, organizations, locations).
* **Test articles:** 69 articles covering real-world entity resolution scenarios.
* **Expected matches:** 206 expected entity matches across all articles.
* **Challenge types:** 15 different challenge types testing various aspects of entity resolution.

The challenge types included in the dataset are:

* **Nicknames:** "Bob Smith" → "Robert Smith" (seven articles).
* **Titles and honorifics:** "Dr. Sarah Williams" → "Sarah Williams" (five articles).
* **Semantic context:** "Russian author" → "Leo Tolstoy" (eight articles).
* **Multilingual names:** Handling names in different scripts (six articles).
* **Business entities:** Corporate name variations (seven articles).
* **Executive references:** "Microsoft CEO" → "Satya Nadella" (five articles).
* **Political leaders:** Title-based references (five articles).
* **Initials:** "J. Smith" → "John Smith" (three articles).
* **Name order variations:** Different name ordering conventions (three articles).
* **Truncated names:** Partial name matches (three articles).
* **Name splitting:** Names split across text (three articles).
* **Missing spaces/hyphens:** Formatting variations (two articles).
* **Transliteration:** Cross-script name matching (two articles).
* **Combined challenges:** Multiple challenges in one article (six articles).
* **Complex business:** Hierarchical business relationships (five articles).

Let's see how prompt-based entity resolution performed.

### Overall performance

The results show that there's a lot of promise with LLM-powered match evaluation, but they also reveal a significant reliability issue. Because each candidate pair must be evaluated by the LLM, failures in structured output can suppress acceptance and recall even when retrieval is working well.

| Metric | Value |
| --- | --- |
| Precision | 83.8% |
| Recall | 62.6% |
| F1 score | 71.7% |
| Total matches found | 344 |
| LLM acceptance rate | 44.8% |
| Error rate | 30.2% |

### The error rate problem

Recall that the first step we take in the prototype is to create potential match pairs using Elasticsearch. Each of these potential matches needs to be evaluated by the LLM. To efficiently process all of those matches, we batch the LLM calls together. This reduces API costs and latency, but there’s also an increased risk of getting malformed JSON in the output. As batch size increases, the JSON becomes longer and more complex, making it more likely that the LLM will generate invalid JSON. This is where the 30% error rate stems from. In the evaluation, we used a batch size of five matches per request. Even with this conservative batch size, we still see JSON parsing failures, which skews the evaluation results significantly.

## What's next: Optimizing LLM integration

Now that we've matched entities using semantic search and LLM judgment, we have a complete entity resolution pipeline. This approach introduces a new failure mode, however, when the model’s judgment is correct, but its output isn’t usable. We can optimize the LLM integration for better reliability and cost efficiency. In the next post, we'll explore how to use function calling for structured output, which provides guaranteed structure and type safety while reducing errors and costs.

## Try it yourself

Want to see entity matching in action? Check out the [Entity Matching notebook](https://github.com/jesslm/entity-resolution-lab-public/tree/main/notebooks#:~:text=5%20minutes%20ago-,03_entity_matching_v3.ipynb,-Initial%20public%20lab) for a complete walk-through with real implementations, detailed explanations, and hands-on examples. The notebook shows you exactly how to match entities using three-step search, hybrid search with RRF, and LLM-powered judgment with reasoning.

**Remember:** This is an educational prototype designed to teach the concepts. When building production systems, consider additional factors, like model selection, cost optimization, latency requirements, quality validation, error handling, and monitoring, which aren't covered in this learning-focused prototype.

## Notes

1. These datasets are synthetic and designed for education; they approximate real challenges but are not representative of any single production domain.

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