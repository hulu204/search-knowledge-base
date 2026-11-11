---
title: 'Entity resolution with Elasticsearch & LLMs, Part 1: Preparing for intelligent entity matching'
company: Elastic
tag: 工程相关
date: 2026-02-12
url: https://www.elastic.co/search-labs/blog/entity-resolution-llm-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Entity resolution with Elasticsearch & LLMs, Part 1: Preparing for intelligent entity matching

Learn what entity resolution is and how to prepare both sides of the entity resolution equation: your watch list and the articles you want to search.

February 12, 2026

[Jessica Moszkowicz](/search-labs/author/jessica-moszkowicz)

[AI](/search-labs/blog/category/ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Part of the series:

[Entity resolution with Elasticsearch](/search-labs/blog/series/entity-resolution-with-elasticsearch)

In this series

Share

"The new Swift update is here!"

When you see that headline, what do you think of? For a developer, it's a call to action, time to dive into new syntax, concurrency models, and bug fixes for the Swift programming language. For a music fan, it's a completely different story, a signal that Taylor Swift has just dropped a new album or is making a major announcement.

Your brain, in a fraction of a second, performs a remarkable feat of natural language processing (NLP). It doesn't just read the word "Swift" in isolation; it uses the surrounding context (the headline's source, your personal interests, and more) to resolve that single, ambiguous word to a unique, real-world entity.

In NLP, we call this ability to disambiguate *named entity resolution* (NER), and it's something humans do all the time. Natural language is inherently ambiguous, so we need to be able to map entities like "Bill Gates" to "the founder of Microsoft" and "The Eras Tour" to "Taylor Swift's concert tour". For humans, these connections come easily; for computers, not so much. Think how disappointed a Swiftie would be when they find out the article that their smart assistant recommended is actually about programming.

This same challenge becomes critical when you're monitoring news articles for mentions of specific people or organizations. Imagine you're tracking sanctioned entities or monitoring mentions of specific companies. You have a watch list with “Sakura Shipping Group” on it, and you want to know when articles mention the company. Simple enough, right? But what happens when an article refers to “Sakura Shipping” instead of the full legal name? Or uses an abbreviation like “SSG”? Or describes it indirectly as “a major Japanese maritime logistics firm”? Or mentions the company in Japanese, as “さくら海運グループ”? Your simple text matching won’t find these mentions, even though they all refer to the same organization. For compliance and risk monitoring use cases, missing a mention could have serious consequences. You need to catch every variation, every alias, every way an entity might be referred to.

This is the problem of *entity resolution*: identifying when different mentions in text refer to the same real-world entity and determining which entity that is. To solve this, we need a system that can handle *semantic search* (understanding meaning, not just keywords), *named entity recognition* (extracting entities from text), and fast, scalable matching across millions of documents. That's why we built this prototype on Elasticsearch. It provides built-in semantic search capabilities, integrated NER models, and the scalability needed for entity resolution.

In this series, we present an educational prototype for intelligent entity resolution that deliberately separates *retrieval* from *judgment and explanation*. Elasticsearch is used to efficiently narrow the search space by combining keyword, alias, and semantic (hybrid) search. Once plausible entity candidates are identified, a large language model (LLM) is used to determine whether a candidate refers to the same real-world entity, and the model’s rationale is provided in natural language.

This division of responsibilities avoids treating LLMs as black-box retrievers, preserves explainability for sensitive use cases, and demonstrates a reusable design pattern for building transparent, Elasticsearch-native systems. We examine why this pattern is particularly effective for entity resolution, where ambiguity is common and explainability matters. The goal is not to present a production-ready solution but to teach the architectural principles behind building transparent entity resolution systems.

**Important note:** This series presents an educational prototype that teaches Elasticsearch-native entity resolution using LLM judgments. We've made some simplifying choices (such as using Wikipedia for entity enrichment) to keep the system accessible for learning. Production systems might use different data sources, additional validation steps, or more sophisticated enrichment pipelines. The goal here is to demonstrate the core concepts and architecture, not to provide a production-ready system.

This series shows how we can help computers make these necessary connections while working with a 100% Elasticsearch-native architecture. We'll explore three major innovations:

* Enhancing entities with contextual information.
* Recognizing basic and complex entities with comprehensive NER.
* Providing transparent reasoning through Elasticsearch candidate matching and LLM-powered explanations.

We'll also evaluate the system and identify an important optimization that improves the overall performance of the educational prototype.

In this first post of a four-part series, we’ll focus on preparing both sides of the entity resolution equation: your watch list and the articles you want to search.

## The problem: Why entity resolution requires preparation

Entity resolution is hard because we face challenges on both sides of the matching equation. On one side, entities can be mentioned in many different ways. A company might be referred to as "Microsoft", "Microsoft Corporation", "MSFT", or even "the Redmond-based tech giant", depending on the context and writing style. On the other hand, we need to find these mentions in articles, even when they're not obvious, such as when an article uses "the Russian President" or "F.D.R." instead of a full name.

**Why we can't just match names directly:** Without proper preparation, matching becomes unreliable. You might think, "But I can just search for 'Tim Cook' in the text, right?" Well, yes, if the article always mentions him by that exact name. But what about when it says "Apple CEO" instead? Or "Timothy D. Cook" (his full name)? Your simple text search won't find those mentions, even though they all refer to the same person.

Without entity preparation, we can't match "the Russian President" to "Vladimir Putin" because we don't know what "the Russian President" means without context. We can't match "J.R.R. Tolkien" to "John Ronald Reuel Tolkien" because we don't know that they're aliases for the same person. We can't match "Apple CEO" to "Tim Cook" because we can't understand the semantic relationship. Without indexing, finding matches means checking every entity in your watch list individually. This doesn't scale: With thousands of entities, every match becomes slow and expensive. For sanctioned individuals monitoring, this means missing critical mentions that use aliases or alternate spellings, a failure that could have serious consequences.

**Why we can't just search text directly:** Entity extraction is hard for the same reason entity resolution is hard: Entities can be mentioned in many different ways. The same person might be referred to as "J.R.R. Tolkien", "the author of *The Lord of the Rings*", or just "Tolkien", depending on the context. Without proper extraction, we can't find these mentions in the text. We'd have to manually identify every entity mention, which doesn't scale. We'd miss entities mentioned in nonstandard ways (for example, titles or abbreviations). We also wouldn't capture the context around entity mentions, which is crucial for accurate matching.

The solution is a two-phase system that prepares both your watch list and the articles you want to search.

## The solution: Two-phase preparation system

To solve entity resolution, we need to prepare both sides of the matching equation. First, we enrich and index our watch list entities to enable semantic search. Second, we extract entity mentions from articles using hybrid techniques that capture explicit and implicit references. Together, these phases create the foundation for intelligent entity matching.

### Phase 1: Preparing your watch list

The solution to preparing entities is to *enrich* them with meaningful contexts. This enables our entity matching system to work effectively. We'll explain how context helps in a bit, but let's walk through the prototype's simple implementation first.

Our watch list of entities may be provided in multiple formats. The Office of Foreign Assets Control (OFAC) provides sanctions lists that include first and last names, addresses, and identifying information, such as passport numbers, date and place of birth, and nationality information [1]. While this provides a good amount of context, in practice many of these fields are omitted when the values are unknown for the given entity. Some lists may be just a set of names. The most helpful lists for our purposes come out of the box with rich descriptions, as is often the case with commercial or curated datasets.

The three-component system used in the prototype starts by managing our entities and organizing their metadata. Since entity lists can vary in the amount of information they contain, our prototype is designed to work with whatever it receives. The JSON format supports entities with minimal information (just a name and type) or full information (with aliases, descriptions, metadata, and more). For example, an entity might be as simple as:

```
{
  "name": "J.R.R. Tolkien",
  "entity_type": "person"
}
```

Or it might include additional context:

```
{
  "name": "J.R.R. Tolkien",
  "entity_type": "person",
  "description": "English writer and philologist, author of The Lord of the Rings",
  "aliases": ["John Ronald Reuel Tolkien", "J.R.R. Tolkien", "Tolkien"],
  "priority": "medium"
}
```

The system handles both cases gracefully during enrichment. For the prototype, the enrichment process adds context from Wikipedia (specifically, the first paragraph of the entity's Wikipedia page) for entities that don't already have context [2]. This Wikipedia context helps with semantic matching, but it doesn't add other fields, like aliases or full names; those must come from the original dataset. (In production, you might use other approaches for enrichment, including an agentic system that figures out where to find the context information for a given entity. This is beyond the scope of our prototype, but it’s an exciting feature we could add in the future.) Finally, we index the entities in Elasticsearch with semantic search capabilities, creating a searchable index that understands meaning rather than just text.

#### **Key concepts: Semantic search and indexing**

**What is semantic search?** *Semantics* refers to the meanings of words and phrases. Figuring out meaning is usually easy for humans, but it's much more challenging for computers to "get" because it requires a depth of understanding that’s difficult to program. Semantic search works by turning this challenge into a math problem, something that computers are very good at [3].

Think of semantic search like map coordinates for meaning. Just as latitude and longitude tell you where something is on a map, semantic embeddings tell you where something is in "meaning space." Whereas traditional keyword search requires exact matches, semantic search relies on describing that "location" in a multidimensional vector space. For example, you might have the coordinates for a specific "big red building". When you search for a "small red building", semantic search looks in the "neighborhood" for similar concepts in the vector space. Your big red building might appear as a nearest neighbor, but the relevance score will be lower because parts of the meaning don't match.

Getting back to our example, when you search for "Apple CEO", semantic search can find "Tim Cook" because the semantic embeddings capture the meaning that both refer to the same person, even though they use completely different words. This capability is invaluable when monitoring for sanctioned individuals, as aliases and code names may be used to evade detection.

**Why Elasticsearch for entity indexing?** Elasticsearch has built-in semantic search capabilities using embedding models, like EmbEddings from bidirEctional Encoder rEpresentations (E5) [4]. This means we can create an index that understands meaning, not just text. When we index our enriched entities, Elasticsearch creates semantic embeddings that capture each entity's meaning, enabling intelligent matching later.

**What is the** ***mapping schema*****?** The mapping schema defines how we structure entity data in Elasticsearch. Our schema includes several field types optimized for different search strategies, including:

* **Keyword fields** (`id,` `name.keyword`, `aliases.keyword`): For exact matching on entity names and aliases.
* **Text fields** (`name`, `name_lower`, `context`, `aliases`): For traditional, case-normalized full-text search with BM25 scoring.
* **Semantic text fields** (`name_semantic`, `context_semantic`): For vector-based similarity search using the multilingual-e5-small model.

This hybrid mapping enables multiple search strategies: exact matching for precise names, keyword search for aliases, and semantic search for meaning-based matching. Even better, Elasticsearch supports *hybrid search*, allowing us to use both keyword and semantic search simultaneously.

#### **Before and after entity preparation**

Before entity preparation, you have a simple list without much context, possibly nothing more than a name: "J.R.R. Tolkien". That's it. You can only match exact text matches, which means you'll miss "John Ronald Reuel Tolkien", "Tolkien", and any other variations. For sanctioned individuals, this means missing critical mentions that use aliases or alternate spellings.

After entity preparation, you have a rich, searchable index. "Vladimir Putin" is now enriched with Wikipedia context, and if your original dataset included aliases, like "Путин" or "Vladimir Vladimirovich Putin", those are indexed as well. The entity also has semantic embeddings that capture its meaning. The Wikipedia context helps semantic search understand that "The Russian President" refers to Vladimir Putin, enabling that match. If "Путин" was provided as an alias in your original dataset, exact matching handles that. Semantic variations work because your semantic embeddings understand meaning. For sanctioned individuals, this comprehensive preparation ensures you catch every mention, regardless of how the name is written or what alternative name is used.

### Phase 2: Extracting entities from articles

Now that we have a searchable watch list, we need to extract entity mentions from articles. This is where article processing comes in.

**Remember:** This is an educational prototype designed to teach entity extraction concepts. Production systems might use different NER models, custom extraction rules, or specialized extraction pipelines tailored to specific domains or languages.

We extract entities from articles using a hybrid NER approach that combines machine learning with pattern-based extraction. First, we process articles to prepare them for extraction. Then, we extract entities using a hybrid extraction approach that combines NER performed in Elasticsearch (using a deployed XLM-RoBERTa model) with pattern-based extraction to catch entities that NER might miss.

This hybrid extraction approach provides several benefits. NER automatically finds entity mentions in text, even when they're not obvious. Pattern-based extraction catches entities that NER might miss, like titles and compound entities. We preserve the context around each entity mention, which helps with matching decisions later. The approach scales well, allowing us to process thousands of articles automatically, not just a few manually.

#### **Key concepts: NER, pattern-based extraction, and hybrid extraction approach**

**What is NER?** *Named entity recognition* is a machine learning technique that identifies named entities in text. When we run NER on an article, it finds mentions like "Microsoft", "Seattle", and "Washington" and labels them as organization, location, or person entities.

**Why use NER in Elasticsearch?** Using NER in Elasticsearch maintains our 100% Elasticsearch-native architecture, which simplifies the entity resolution prototype's design. Instead of managing separate services for entity extraction and search, everything runs in one system. You can perform NER during document ingestion using inference pipelines, and the extracted entities are immediately available for indexing and searching. This unified approach reduces complexity, eliminates network calls between services, and makes deployment and management easier. The XLM-RoBERTa model is trained to recognize entities in multiple languages, so we can extract entities from articles in different languages without needing separate models for each language. For information on deploying NER models in Elasticsearch, see the [Elasticsearch NER documentation](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-ner-example).

**What is pattern-based extraction?** *Pattern-based extraction* uses rules and patterns to find entities that NER might miss. For example, NER might not recognize "the author of *The Lord of the Rings*" as an entity mention, but pattern-based extraction can catch titles and roles like "the CEO" or "the President". However, pattern-based extraction is language-specific. The patterns need to be defined for each language you want to support. This is a significant drawback for multilingual systems, but it's acceptable for our educational prototype, which focuses on demonstrating the core concepts. Production systems might use language-specific pattern sets or alternative approaches for multilingual support.

**How do they work together?** The hybrid extraction approach combines both techniques. NER finds obvious entity mentions like "J.R.R. Tolkien", while pattern-based extraction catches variations that NER might miss, such as "the author of *The Lord of the Rings*". Together, they provide comprehensive coverage of entity mentions in text.

When we extract entities from an article mentioning "the author of *The Lord of the Rings*", we get:

* Text: "author of *The Lord of the Rings*"
* Type: PERSON (from pattern-based extraction)
* Confidence: 0.85
* Context: "The author of *The Lord of the Rings* published a new edition"

#### **Before and after entity extraction**

With NER-only extraction, we might find "J.R.R. Tolkien" and "*The Lord of the Rings*" in the article, but we'd miss "the author of *The Lord of the Rings*" because NER doesn't recognize descriptive phrases as entity mentions.

With hybrid extraction, we find both "J.R.R. Tolkien" (from NER) and "the author of *The Lord of the Rings*" (from pattern-based extraction). This comprehensive coverage enables better matching later, since we can match both the name and the descriptive phrase to our watch list.

## What's next: Matching entities to our watch list

Now that we've prepared both sides of the entity resolution equation, we have everything we need for intelligent matching:

* A searchable watch list enriched with context and indexed for semantic search.
* Extracted entity mentions from articles using hybrid NER.

Preparation gives us the raw ingredients, but it doesn’t tell us which entity a mention actually refers to. In the next post, we'll explore how to match these extracted entities to our watch list using semantic search and LLM-powered judgment that handles ambiguity and context transparently.

## Try it yourself

Want to see the preparation process in action? Check out these notebooks for complete walkthroughs with real implementations, detailed explanations, and hands-on examples:

* [**Entity preparation notebook**](https://github.com/jesslm/entity-resolution-lab-public/tree/main/notebooks#:~:text=3%20minutes%20ago-,01_entity_preparation_v3.ipynb,-Initial%20public%20lab)**:** Shows you exactly how to enrich entities with Wikipedia context, create semantic search indexes, and prepare your watch list for intelligent matching.
* [**Article processing notebook**](https://github.com/jesslm/entity-resolution-lab-public/tree/main/notebooks#:~:text=3%20minutes%20ago-,02_article_processing_v3.ipynb,-Initial%20public%20lab)**:** Shows you exactly how to extract entities from articles using hybrid NER, handle multilingual content, and process compound entities.

**Remember:** This is an educational prototype designed to teach the concepts. When building production systems, consider additional factors, like data source reliability, validation pipelines, error handling, monitoring, compliance requirements, domain-specific NER models, custom extraction rules, and quality validation that aren't covered in this learning-focused prototype.

## References

1. [OFAC Sanctions List Search](https://sanctionslist.ofac.treas.gov/Home/)
2. The datasets used for the prototype also use a special field, 'explicit\_context', in lieu of getting the context from Wikipedia. We do this to control for the entity preparation step when we're testing other components such as entity matching.
3. [The big ideas behind retrieval augmented generation](https://www.elastic.co/blog/retrieval-augmented-generation-explained#semantic-search:~:text=what%20we%E2%80%99ll%20do.-,Turning%20semantic%20search%20into%20a%20math%20problem,-Let%E2%80%99s%20begin%20with)
4. [E5 in Elasticsearch](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-e5)

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