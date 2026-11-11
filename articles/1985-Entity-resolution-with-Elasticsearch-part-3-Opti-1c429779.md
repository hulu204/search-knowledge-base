---
title: 'Entity resolution with Elasticsearch, part 3: Optimizing LLM integration with function calling'
company: Elastic
tag: 工程相关
date: 2026-03-04
url: https://www.elastic.co/search-labs/blog/elasticsearch-entity-resolution-llm-function-calling
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Entity resolution with Elasticsearch, part 3: Optimizing LLM integration with function calling

Learn how function calling enhances LLM integration, enabling a reliable and cost-efficient entity resolution pipeline in Elasticsearch.

March 04, 2026

[Jessica Moszkowicz](/search-labs/author/jessica-moszkowicz)

[AI](/search-labs/blog/category/ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Part of the series:

[Entity resolution with Elasticsearch](/search-labs/blog/series/entity-resolution-with-elasticsearch)

In this series

Share

In [part 1](https://www.elastic.co/search-labs/blog/entity-resolution-llm-elasticsearch) and [part 2](https://www.elastic.co/search-labs/blog/elasticsearch-entity-resolution-llm-semantic-search) of this series, we built a complete entity resolution pipeline that included preparing entities with context and indexing them for semantic search, extracting entities from articles using hybrid named entity recognition (NER), and matching entities using semantic search and large language model (LLM) judgment. The results were promising, but JSON parsing errors significantly lowered measured accuracy by causing otherwise valid judgments to be discarded. The system wasn’t failing because it made bad judgments; it was failing because it couldn’t reliably express them.

The root of this problem was our somewhat naive choice to use prompt-based JSON generation in which the LLM generates JSON responses in text format. If we asked the LLM to judge more than a couple of matches at a time, the generated JSON was often ill-formed. To mitigate this, we were forced to reduce the processing batch size, which simply won't scale in a production system.

So the prompt-based JSON generation helped validate our approach to entity resolution, but we need a more systematic and reliable method. OpenAI function calling provides a better path by guaranteeing structure and type safety while reducing errors and costs. We chose OpenAI's functions for the educational prototype, but other LLM providers typically provide similar functionality (for example, Claude tools).

**Note:** While we discuss production challenges here, this is still an educational prototype demonstrating optimization techniques. Real production systems would need additional considerations, like monitoring, alerting, fallback strategies, and comprehensive error handling.

## Key concepts: Function calling, schema design, and cost benefits

**What is function calling?** *Function calling* is OpenAI's structured output API. With it, we can define schemas for LLM responses, so we always know exactly what we're going to get. By enforcing the JSON format rather than trying to define it in the LLM prompt, we should be able to eliminate parsing errors.

**Why is it better than prompt-based JSON?** LLMs generate nondeterministic output. One hopes that they'll at least generate content that contains the correct response, but the presentation of that response is unpredictable. With a chatbot, this is often not a problem, but our prototype is trying to programmatically process the output. Computer programs demand consistency, so when the LLM generates what we expect, everything is fine, but as soon as it goes off script, so to speak, the code errors out. We could try to account for the different possibilities, but it would be very difficult to catch everything. We could try to enforce more consistent behavior by adding something like "Always return parsable JSON". We tried this exact technique in the prototype's prompt, but we've seen that prompt-based JSON still goes off the rails pretty quickly, particularly if we try to process a batch of matches.

Function calling makes the LLM generation controllable and predictable, exactly what we need for entity resolution. To aid in the definition of the functions, we’ll also follow minimal schema design principles.

**What are minimal schema design principles?** *Minimal schema design* means defining only the fields you need, using simple types, and avoiding nested structures when possible. This reduces token usage (smaller schemas mean fewer tokens), improves reliability (simpler schemas are easier for the LLM to follow), and lowers costs (fewer tokens mean lower API costs).

**What are the cost and reliability benefits?** Since fewer errors means match processing is much more likely to succeed, even with large batch sizes, we don't have to retry judging matches. The elimination of retries reduces costs by reducing token usage, but using minimal schemas also keeps our token count down. This all leads to a less expensive and more reliable approach that’s much more suitable to use in production.

We need to check one more thing, though. While matches may be getting processed without error, are the errorless results actually correct? How does this new approach compare to the promising results we saw with the prompt-based approach?

## Real-world results: Side-by-side comparison

As we did in the previous blog, we ran the function calling approach against the tier 4 dataset, which consists of 206 expected matches across 69 articles. The results demonstrate a dramatic improvement:

| Metric | Prompt-based | Function calling | Improvement |
| --- | --- | --- | --- |
| Error rate | 30.2% | 0.0% | 100% elimination |
| Precision | 83.8% | 90.3% | +6.5pp |
| Recall | 62.6% | 90.8% | +28.2pp |
| F1 score | 71.7% | 90.6% | +18.9pp |
| Acceptance rate | 44.8% | 60.2% | +15.4pp |
| True positives | 129 | 187 | +45.0% |
| False negatives | 77 | 19 | -75.3% |

### Error elimination: The key differentiator

The most striking difference is the **complete elimination of JSON parsing errors**. This resulted in a modest precision improvement and a far more dramatic recall improvement. The precision metric captures how often the matches the system accepts were expected in the golden document. So the prototype was decent at judging matches correctly in the prompt-based approach, but function calling does that even better.

Conversely, recall tells us how many of the expected matches were found. When a batch of matches comes back with malformed JSON, the system loses all of those matches. It's likely that Elasticsearch sends many of these matches for judgment, but we lose those matches if judgment fails. The significant recall improvement shows that this hypothesis is correct. Elasticsearch identifies the potential matches and function calling verifies which of those matches are correct.

**Note:** It’s expected that Elasticsearch will find some incorrect matches because we look at the top two or three results from hybrid search. Most of the time, hybrid search returns the correct match as the top result, but having the LLM judge the top few hits ensures that we see how the LLM handles incorrect matches. If we move from the educational prototype to a production system, we’ll likely tune the Elasticsearch queries more carefully so that we only send promising matches to the LLM, further optimizing our LLM costs.

## What's next: The ultimate challenge

Now that we've optimized our LLM integration with function calling, we have a complete entity resolution pipeline with improved reliability and cost efficiency. However, can it handle the ultimate challenge? In the next post, we'll explore how the system handles diverse entity resolution scenarios across 50 different challenge types, including cultural naming conventions, business relationships, titles, and multilingual variations.

## Try it yourself

Want to see function calling optimization in action? Check out the [Function Calling Optimization notebook](https://github.com/jesslm/entity-resolution-lab-public/tree/main/notebooks#:~:text=5%20minutes%20ago-,04_function_calling_optimization_v3.ipynb,-Initial%20public%20lab) for a complete walkthrough with real implementations, detailed explanations, and hands-on examples. The notebook shows you exactly how to use function calling for structured output, compare it with prompt-based JSON, and analyze cost and reliability benefits.

**Remember:** This is an educational prototype designed to teach optimization concepts. When building production systems, consider additional factors, like multi-provider support, advanced caching strategies, monitoring and alerting, comprehensive error handling, and compliance requirements that aren't covered in this learning-focused prototype.

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