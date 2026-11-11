---
title: 'GenAI for customer support — Part 4: Tuning RAG search for relevance'
company: Elastic
tag: 搜索相关性
date: 2024-08-22
url: https://www.elastic.co/search-labs/blog/elser-rag-search-for-relevance
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# GenAI for customer support — Part 4: Tuning RAG search for relevance

This series gives you an inside look at how we're using generative AI in customer support. Join us as we share our journey in real-time, focusing in this section on tuning RAG search for relevance.

August 22, 2024

[Antonio Schönmann](/search-labs/author/antonio-schonmann)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

Part of the series:

[GenAI for customer support](/search-labs/blog/series/genai-for-customer-support)

In this series

Share

> This blog series reveals how our Field Engineering team used the Elastic stack with generative AI to develop a lovable and effective customer support chatbot. If you missed other installments in the series, be sure to check out [part one](https://www.elastic.co/blog/genai-customer-support-building-proof-of-concept), [part two](https://search-labs.elastic.co/search-labs/blog/genai-customer-support-building-a-knowledge-library), [part three](https://search-labs.elastic.co/search-labs/blog/genai-elastic-elser-chat-interface), the [launch blog](https://www.elastic.co/blog/generative-ai-customer-support-elastic-support-assistant), and [part five](https://www.elastic.co/search-labs/blog/genai-customer-support-observability).

Welcome to part 4 of our blog series on integrating generative AI in Elastic's customer support. This installment dives deep into the role of Retrieval-Augmented Generation (RAG) in enhancing our AI-driven Technical Support Assistant. Here, we address the challenges, solutions, and outcomes of refining search effectiveness, providing action items to further improve its capabilities using the toolset provided in the Elastic Stack version *8.11*.

Implied by those actions, we have achieved a **~75% increase in top-3 results** relevance and gained over **300,000 AI-generated summaries that we can leverage for all kinds of future applications**. If you're new to this series, be sure to review the earlier posts that introduce the core technology and architectural setup. If you missed the last blog of the series, you can find it [here](https://www.elastic.co/search-labs/blog/genai-elastic-elser-chat-interface).

## RAG tuning: A search problem

Perfecting RAG (Retrieval-Augmented Generation) is fundamentally about hitting the bullseye in search accuracy 🎯:

* Like an archer carefully aiming to hit the center of the target, we want to focus on **accuracy** for each hit.
* Not only that, we also want to ensure that we have the best targets to hit – or **high-quality data**.

Without **both together**, there's the potential risk that large language models (LLMs) might hallucinate and generate misleading responses. Such mistakes can definitely shake users' trust in our system, leading to a deflecting usage and poor return on investment.

To avoid those negative implications, we've encountered several challenges that have helped us refine our search accuracy and data quality over the course of our journey. These challenges have been instrumental in shaping our approach to tuning RAG for relevance, and we're excited to share our insights with you.

That said: **let's dive into the details!**

## Our first approach

We started with a lean, effective solution that could quickly get us a valuable RAG-powered chatbot in production. This meant focusing on key functional aspects that would bring it to operational readiness with optimal search capabilities. To get us into context, we'll make a quick walkthrough around four key vital components of the Support AI Assistant: [*data*](#data), [*querying*](#query), [*generation*](#generation), and [*feedback*](#feedback).

### Data

As showcased in the [2nd blog article of this series](https://search-labs.elastic.co/search-labs/blog/genai-customer-support-building-a-knowledge-library#elastic-supports-knowledge-library), our journey began with an extensive database that included over 300,000 documents consisting of *Technical Support Knowledge Articles* and various pages crawled from our website, such as Elastic's *Product Documentation* and *Blogs*. This rich dataset served as the foundation for our search queries, ensuring a broad spectrum of information about Elastic products was available for precise retrieval. To this end, we leveraged Elasticsearch to store and search our data.

### Query

Having great [data](#data) to search by, it's time to talk about our querying component. We adopted a standard Hybrid-Search strategy, which combines the traditional strengths of **BM25**, *Keyword-based Search*, with the capabilities of *Semantic Search*, powered by **ELSER**.

For the semantic search component, we used `text_expansion` queries against both `title` and `summary` embeddings. On the other hand, for broad keyword relevance we search multiple fields using `cross_fields`, with a `minimum_should_match` parameter tuned to better perform with longer queries. Phrase matches, which often signal greater relevance, receive a higher boost. Here’s our initial setup:

```
const searchResults = await client.elasticsearchClient({
  // Alias pointing to the knowledge base indices.
  index: "knowledge-search", 
  body: {
    size: 3,
    query: {
      bool: {
        should: [
          // Keyword-search Component. 
          {
            multi_match: {
              query,
              // For queries with 3+ words, at least 49% must match.
              minimum_should_match: "1<-1 3<49%", 
              type: "cross_fields",
              fields: [
                "title",
                "summary",
                "body",
                "id",
              ],
            },
          },
          {
            multi_match: {
              query,
              type: "phrase",
              boost: 9,
              fields: [
                // Stem-based versions of our fields. 
                "title.stem",
                "summary.stem",
                "body.stem",
              ],
            },
          },
          // Semantic Search Component.
          {
            text_expansion: {
              "ml.inference.title_expanded.predicted_value": {
                model_id: ".elser_model_2",
                model_text: query,
              },
            },
          },
          {
            text_expansion: {
              "ml.inference.summary_expanded.predicted_value": {
                model_id: ".elser_model_2",
                model_text: query,
              },
            },
          },
        ],
      },
    },
  },
});
```

### Generation

After search, we build up the system prompt with different sets of instructions, also contemplating the ***top 3*** search results as context to be used. Finally, we feed the conversation alongside the built context into the LLM, generating a response. Here's the pseudocode showing the described behavior:

```
// We then feed the context into the LLM, generating a response.
const { stopGeneration } = fetchChatCompletionAPI(
  {
    // The system prompt + vector search results.
    context: buildContext(searchResults), 
    // The entire conversation + the brand new user question.
    messages, 
    // Additional parameters.
    parameters: { model: LLM.GPT4 } 
  },
  {
    onGeneration: (event: StreamGenerationEvent) => {
      // Stream generation events back to the user interface here...
    }
  }
);
```

The reason for not including more than 3 search results was the limited quantity of tokens available to work within our dedicated Azure OpenAI's GPT4 deployment (PTU), allied with a relatively large user base.

### Feedback

We used a third-party tool to capture client-side events, connecting to *Big Query* for storage and making the JSON-encoded events accessible for comprehensive analysis by everyone on the team. Here's a glance into the Big Query syntax that builds up our feedback view. The

`JSON_VALUE` function is a means to extract fields from the event payload:

```
  SELECT
    -- Extract relevant fields from event properties
    JSON_VALUE(event_properties, '$.chat_id') AS `Chat ID`,
    JSON_VALUE(event_properties, '$.input') AS `Input`,
    JSON_VALUE(event_properties, '$.output') AS `Output`,
    JSON_VALUE(event_properties, '$.context') AS `Context`,
    
    -- Determine the reaction (like or dislike) to the interaction
    CASE JSON_VALUE(event_properties, '$.reaction')
      WHEN 'disliked' THEN '👎'
      WHEN 'liked' THEN '👍'
    END AS `Reaction`,
    
    -- Extract feedback comment
    JSON_VALUE(event_properties, '$.comment') AS `Comment`,

    event_time AS `Time`
  FROM
    `frontend_events` -- Table containing event data
  WHERE
    event_type = "custom"
    AND JSON_VALUE(event_properties, '$.event_name') IN (
      'Chat Interaction', -- Input, output, context. 
      'Chat Feedback', -- Feedback comments.
      'Response Like/Dislike' -- Thumbs up/down.
    )
  ORDER BY `Chat ID` DESC, `Time` ASC; -- Order results by Chat ID and time
```

We also took advantage of valuable direct feedback from internal users regarding the chatbot experience, enabling us to quickly identify areas where our search results did not match the user intent. Incorporating both would be instrumental in the discovery process that enabled us to refine our RAG implementation, as we're going to observe throughout the next section.

## Challenges

With usage, interesting patterns started to emerge from feedback. Some user queries, like those involving specific [*CVEs*](https://en.wikipedia.org/wiki/Common_Vulnerabilities_and_Exposures) or *Product Versions* for instance, were yielding suboptimal results, indicating a disconnect between the user's intent and the *GenAI* responses. Let's take a closer look at the specific challenges identified, and how we solved them.

### #1: CVEs (Common Vulnerabilities and Exposures)

Our customers frequently encounter alerts regarding lists of open CVEs that could impact their systems, often resulting in support cases. To address questions about those effectively, our dedicated internal teams meticulously maintain *CVE-type* Knowledge Articles. These articles provide standardized, official descriptions from Elastic, including detailed statements on the implications, and list the artifacts affected by each CVE.

Recognizing the potential of our chatbot to streamline access to this crucial information, our internal *InfoSec* and *Support Engineering* teams began exploring its capabilities with questions like this:

```
👨🏽 What are the implications of CVE's `2016-1837`, `2019-11756` and `2014-6439`?
```

For such questions, one of the key advantages of using RAG – and also the main functional goal of adopting this design – is that we can pull up-to-date information, including it as context to the LLM and thus making it available instantly to produce awesome responses. That naturally will save us time and resources over fine-tuned LLM alternatives.

However, the produced responses wouldn't perform as expected. Essential to answer those questions, the search results often lacked relevance, a fact which we can confirm by looking closely at the search results for the example:

```
{
  ...
  "hits": [
    {
      "_index": "search-knowledge-articles",
      "_id": "...",
      "_score": 59.449028,
      "_source": {
        "id": "...",
        "title": "CVE-2019-11756", // Hit!
        "summary": "...",
        "body": "...",
        "category": "cve"
      }
    },
    {
      "_index": "search-knowledge-articles",
      "_id": "...",
      "_score": 42.15182,
      "_source": {
        "title": "CVE-2019-10172", // :(
        "summary": "...",
        "body": "...",
        "category": "cve"
      }
    },
    {
      "_index": "search-docs",
      "_id": "...",
      "_score": 38.413914,
      "_source": {
        "title": "Potential Sudo Privilege Escalation via CVE-2019-14287 | Elastic  Security Solution [8.11] | Elastic",  // :(
        "summary": "...",
        "body": "...",
        "category": "documentation"
      }
    }
  ]
}
```

With just one relevant hit (`CVE-2019-10172`), we left the LLM without the necessary context to generate proper answers:

```
The context only contains information about CVE-2019-11756, which is...
```

The observed behavior prompted us with an interesting question:

> How could we use the fact that users often include close-to-exact CVE codes in their queries to enhance the accuracy of our search results?

To solve this, we approached the issue as a search challenge. We hypothesized that by emphasizing the `title` field matching for such articles, which directly contain the CVE codes, we could significantly improve the precision of our search results. This led to a strategic decision to conditionally boost the weighting of title matches in our search algorithm. By implementing this focused adjustment, we refined our query strategy as follows:

```
    ...
    should: [
        // Additional boosting for CVEs.
        {
          bool: {
            filter: {
              term: {
                category: 'cve',
              },
            },
            must: {
              match: {
                title: {
                  query: queryText,
                  boost: 10,
                },
              },
            },
          },
        },
        // BM-25 based search.
        {
          multi_match: {
             ...
```

As a result, we experienced much better hits for CVE-related use cases, ensuring that `CVE-2016-1837`, `CVE-2019-11756` and `CVE-2014-6439` are top 3:

```
{
  ...
  "hits": [
    {
      "_index": "search-knowledge-articles",
      "_id": "...",
      "_score": 181.63962,
      "_source": {
        "title": "CVE-2019-11756",
        "summary": "...",
        "body": "...",
        "category": "cve"
      }
    },
    {
      "_index": "search-knowledge-articles",
      "_id": "...",
      "_score": 175.13728,
      "_source": {
        "title": "CVE-2014-6439",
        "summary": "...",
        "body": "...",
        "category": "cve"
      }
    },
    {
      "_index": "search-knowledge-articles",
      "_id": "...",
      "_score": 152.9553,
      "_source": {
        "title": "CVE-2016-1837",
        "summary": "...",
        "body": "...",
        "category": "cve"
      }
    }
  ]
}
```

And thus generating a much better response by the LLM:

```
🤖 The implications of the CVEs mentioned are as follows: (...)
```

Lovely! By tuning our Hybrid Search approach, we significantly improved our performance with a pretty simple, but mostly effective *Bob's Your Uncle* solution (like some folks would say)! This improvement underscores that while semantic search is a powerful tool, understanding and leveraging user intent is crucial for optimizing search results and overall chat experience in your business reality. With that in mind, let's dive into the next challenge!

### #2: Product versions

As we delved deeper into the challenges, another significant issue emerged with queries related to specific versions. Users frequently inquire about features, migration guides, or version comparisons, but our initial search responses were not meeting expectations. For instance, let's take the following question:

```
👨🏽 Can you compare Elasticsearch versions 8.14.3 and 8.14.2?
```

Our initial query approach would return the following top 3:

* [Elasticsearch for Apache Hadoop version 8.14.1 | Elasticsearch for Apache Hadoop [8.14] | Elastic](https://www.elastic.co/guide/en/elasticsearch/hadoop/current/eshadoop-8.14.1.html);
* [APM version 8.14 | Elastic Observability [8.14] | Elastic](https://www.elastic.co/guide/en/observability/current/apm-release-notes-8.14.html)*;*
* [Elasticsearch for Apache Hadoop version 8.14.3 | Elasticsearch for Apache Hadoop [8.14] | Elastic](https://www.elastic.co/guide/en/elasticsearch/hadoop/8.14/eshadoop-8.14.3.html).

Corresponding to the following `_search` response:

```
{
  ...
  "hits": [
    {
      "_index": "search-docs",
      "_id": "6807c4cf67ad0a52e02c4c2ef436194d2796faa454640ec64cc2bb999fe6633a",
      "_score": 29.79520,
      "_source": {
        "title": "Elasticsearch for Apache Hadoop version 8.14.1 | Elasticsearch for Apache Hadoop [8.14] | Elastic",
        "summary": "...",
        "body": "...",
        "url": "https://www.elastic.co/guide/en/elasticsearch/hadoop/current/eshadoop-8.14.1.html",
        "category": "documentation"
      }
    },
    {
      "_index": "search-docs",
      "_id": "9233c6b53a9d2e8b5daf1f68e7d82590516f0dfc23d979783ea1146854dc9d63",
      "_score": 27.19520,
      "_source": {
        "title": "APM version 8.14 | Elastic Observability [8.14] | Elastic",
        "summary": "...",
        "body": "...",
        "url": "https://www.elastic.co/guide/en/observability/current/apm-release-notes-8.14.html",
        "category": "documentation"
      }
    },
    {
      "_index": "search-docs",
      "_id": "392a39dd81933523d6018cac5ae4fc38b31de4ae3e1c0f1655d98191133c4e8a",
      "_score": 26.7618,
      "_source": {
        "title": "Elasticsearch for Apache Hadoop version 8.14.3 | Elasticsearch for Apache Hadoop [8.14] | Elastic",
        "summary": "...",
        "body": "...",
        "url": "https://www.elastic.co/guide/en/elasticsearch/hadoop/8.14/eshadoop-8.14.3.html",
        "category": "documentation"
      }
    }
  ]
}
```

Being irrevocably irrelevant, they ended up resulting in a completely uninformed answer from the chatbot, affecting the overall user experience and trust in the Support AI Assistant:

```
🤖 As of my last update, Elasticsearch 8.14.2 and 8.14.3 had not been released, and there were no official release notes available for these versions. Elasticsearch follows a rapid release cycle, and new versions often include bug fixes, performance improvements, and occasionally new features. However, without specific release notes or announcements from Elastic, I cannot provide details on what is new in these hypothetical versions.

To find the most up-to-date information on Elasticsearch releases, you should check the official Elastic website or their GitHub repository for the latest release notes. Release notes are typically published alongside the software release and provide a comprehensive list of changes, including new features, enhancements, bug fixes, and known issues
```

Further investigating the issue we collected valuable insights. By replaying the query and looking into the search results, we noticed three serious problems with our crawled *Product Documentation* data that were contributing to the overall bad performance:

1. [**Inaccurate semantic matching**](#a-inaccurate-semantic-matching): Semantically, we definitely missed the shot. Why would we match against such specific articles, including two specifically about Apache Hadoop, when the question was so much broader than Hadoop?
2. [**Multiple versions, same articles**](#b-multiple-versions-same-articles): Going further down on the hits of the initially asked question, we often noticed multiple versions for the same articles, with close to exactly the same content. That often led to a top 3 cluttered with irrelevant matches!
3. [**Wrong versions being returned**](#c-wrong-versions-being-returned): It's fair to expect that having both *8.14.1* and *8.14.2* versions of the *Elasticsearch for Apache Hadoop* article, we'd return the latter for our query – but that just wasn't happening consistently.

From the impact perspective, we had to stop and solve those – else, a considerable part of user queries would be affected. Let's dive into the approaches taken to solve both!

#### A. Inaccurate semantic matching

After some examination into our data, we've discovered that the root of our semantic matching issue lived in the fact that the `summary` field for *Product Documentation-type* articles generated upon ingestion by the crawler was just the first few characters of the `body`. This redundancy misled our semantic model, causing it to generate vector embeddings that did not accurately represent the document's content in relation to user queries.

As a data problem, we had to solve this problem in the data domain: by leveraging the use of GenAI and the GPT4 model, we made a team decision to craft a new AI Enrichment Service – introduced in the [2nd installment of this blog series](https://search-labs.elastic.co/search-labs/blog/genai-customer-support-building-a-knowledge-library#enriching-document-sources). We decided to create our own tool for a few specific reasons:

* We had unused PTU resources available. Why not use them?
* We needed this data gap filled quickly, as this was probably the greatest relevance detractor.
* We wanted a fully customizable approach to make our own experiments.

Modeled to be generic, our usage for it boils down to generating four new fields for our data into a new index, using [*Enrich Processors*](https://www.elastic.co/guide/en/elasticsearch/reference/current/ingest-enriching-data.html) to make them available to the respective documents on the target indices upon ingestion. Here's a quick view into the specification for each field to be generated:

```
const fields: FieldToGenerate[] = [
  {
    // A one-liner summary for the article.
    name: 'ai_subtitle', 
    strategy: GenerationStrategy.AbstractiveSummarizer,
  },
  {
    // A longer summary for the article.
    name: 'ai_summary', 
    strategy: GenerationStrategy.AbstractiveSummarizer,
  },
  {
    // A list of questions answered by the article.
    name: 'ai_questions_answered', 
    strategy: GenerationStrategy.QuestionSummarizer,
  },
  {
    // A condensed list of tags for the article.
    name: 'ai_tags',
    strategy: GenerationStrategy.TagsSummarizer,
  }
];
```

After generating those fields and setting up the index *Enrich Processors*, the underlying RAG-search indices were enriched with a new `ai_fields` object, also making ELSER embeddings available under `ai_fields.ml.inference`:

```
{
  ...
  "_source": {
    "product_name": "Elasticsearch",
    "version": "8.14",
    "url": "https://www.elastic.co/guide/en/elasticsearch/hadoop/8.14/eshadoop-8.14.1.html",
    "ai_fields": {
      "ai_summary": "ES-Hadoop 8.14.1; tested against Elasticsearch 8.14.1. ES-Hadoop 8.14.1 is a compatibility release, aligning with Elasticsearch 8.14.1. This version ensures seamless integration and operation with Elasticsearch's corresponding version, maintaining feature parity and stability across the Elastic ecosystem.",
      "ai_subtitle": "ES-Hadoop 8.14.1 Compatibility Release",
      "ai_tags": [
        "Elasticsearch",
        "ES-Hadoop",
        "Compatibility",
        "Integration",
        "Version 8.14.1"
      ],
      "source_id": "6807c4cf67ad0a52e02c4c2ef436194d2796faa454640ec64cc2bb999fe6633a",
      "ai_questions_answered": [
        "What is ES-Hadoop 8.14.1?",
        "Which Elasticsearch version is ES-Hadoop 8.14.1 tested against?",
        "What is the purpose of the ES-Hadoop 8.14.1 release?"
      ],
      "ml": {
        "inference": {
          "ai_subtitle_expanded": {...},
          "ai_summary_expanded": {...},
          "ai_questions_answered_expanded": {...}
        }
      }
    }
  }
  ...
}
```

Now, we can tune the query to use those fields, making for better overall semantic and keyword matching:

```
   ...
   // BM-25 Component. 
   {
      multi_match: {
        ...
        type: 'cross_fields',
        fields: [
          ...
          // Adding the `ai_fields` to the `cross_fields` matcher.
          'ai_fields.ai_subtitle',
          'ai_fields.ai_summary',
          'ai_fields.ai_questions_answered',
          'ai_fields.ai_tags',
        ],
      },
   },
   {
      multi_match: {
        ...
        type: 'phrase',
        fields: [
          ...
          // Adding the `ai_fields` to the `phrase` matcher.
          'ai_fields.ai_subtitle.stem',
          'ai_fields.ai_summary.stem',
          'ai_fields.ai_questions_answered.stem',
        ],
      },
   },
   ...
   // Semantic Search Component.
   {
      text_expansion: {
        // Adding `text_expansion` queries for `ai_fields` embeddings.
        'ai_fields.ml.inference.ai_subtitle_expanded.predicted_value': {
          model_id: '.elser_model_2',
          model_text: queryText,
        },
      },
    },
    {
      text_expansion: {
        'ai_fields.ml.inference.ai_summary_expanded.predicted_value': {
          model_id: '.elser_model_2',
          model_text: queryText,
        },
      },
    },
    {
      text_expansion: {
        'ai_fields.ml.inference.ai_questions_answered_expanded.predicted_value':
          {
            model_id: '.elser_model_2',
            model_text: queryText,
          },
      },
    },
    ...
```

Single-handedly, that made us much more relevant. More than that – it also opened a lot of new possibilities to use the AI-generated data throughout our applications – matters of which we'll talk about in future blog posts.

Now, before retrying the query to check the results: **what about the multiple versions problem?**

#### B. Multiple versions, same articles

When duplicate content infiltrates these top positions, it diminishes the value of the data pool, thereby diluting the effectiveness of GenAI responses and leading to a suboptimal user experience. In this context, a significant challenge we encountered was **the presence of multiple versions of the same article.** This redundancy, while contributing to a rich collection of version-specific data, often cluttered the essential data feed to our LLM, reducing the diversity of it and therefore undermining the response quality.

To address the problem, we employed the

*Elasticsearch API* `collapse` parameter, sifting through the noise and prioritizing only the most relevant version of a single content. To do that, we computed a new `slug` field into our *Product Documentation* crawled documents to identify different versions of the same article, using it as the *collapse field* (or *key*).

Taking the *Sort search results* [documentation page](https://www.elastic.co/guide/en/elasticsearch/reference/8.14/sort-search-results.html) as an example, we have two versions of this article being crawled:

* [Sort search results | Elasticsearch Guide [8.14] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/8.14/sort-search-results.html)
* [Sort search results | Elasticsearch Guide [7.17] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/sort-search-results.html)

Those two will generate the following `slug`:

> guide-en-elasticsearch-reference-sort-search-results

Taking advantage of that, we can now tune the query to use `collapse`:

```
...
const searchQuery = {
  index: "knowledge-search",
  body: {
    ...
    query: {...},
    collapse: {
      // This is a "field alias" that will point to the `slug` field for product docs.
      field: "collapse_field" 
    }
  }
};
...
```

As a result, we'll now only show the top-scored documentation in the search results, which will definitely contribute to increasing the diversity of knowledge being sent to the LLM.

#### C. Wrong versions being returned

Similar to the [CVE matching problem](#1-cves-common-vulnerabilities-and-exposures), we can boost results based on the specific versions being mentioned, allied with the fact that `version` is a separate field in our index. To do that, we used the following simple regex-based function to pull off versions directly from the user question:

```
/**
 * Extracts versions from the query text.
 * @param queryText The user query (or question).
 * @returns Array of versions found in the query text.
 * @example getVersionsFromQueryText("What's new in 8.14.2? And 8.14.3?") => ['8.14.2', '8.14.3'] 
 */
const getVersionsFromQueryText = (queryText: string) : string[] => {
  let results = null;
  const versions = [];
  // Will match `x.y.z` or `x.y` 
  const versionRegex = /\b\d+\.\d+(\.\d+)?\b/gi;

  while ((results = versionRegex.exec(queryText))) {
    const [version] = results;
    versions.push(version);
  }

  return versions;
};
```

We then add one more query to the `should` clause, boosting the `version` field accordingly and getting the right versions to the top (whenever they're mentioned):

```
    // Additional boosting for versions.
    ...(versions.length > 0 ? [
    {
      bool: {
        filter: {
          term: {
            category: 'documentation',
          },
        },
        must: {
          terms: {
            version: versions,
            boost: 4,
          },
        },
      },
   }] : []),
    // BM-25 Component.
   {
      multi_match: {
        ...
        type: 'cross_fields',
        fields: [
          ...
    ...
```

With [**A**](#a-inaccurate-semantic-matching), [**B**](#b-multiple-versions-same-articles) and [**C**](#c-wrong-versions-being-returned) solved, we're probably ready to see some strong results!

### Let's replay the question!

By replaying the previously tried question:

```
👨🏽 Can you compare Elasticsearch versions 8.14.3 and 8.14.2?
```

And therefore running the Elasticsearch query once again, we get dramatically better results consisting of the following articles:

* [Elasticsearch version 8.14.3 | Elasticsearch Guide [master] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/master/release-notes-8.14.3.html)
* [Elasticsearch version 8.14.2 | Elasticsearch Guide [master] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/master/release-notes-8.14.2.html)
* [Release notes | Elasticsearch Guide [8.14] | Elastic](https://www.elastic.co/guide/en/elasticsearch/reference/8.14/es-release-notes.html)

Consequently, we have a better answer generated by the LLM. More powerful than that – in the context of this conversation, the LLM is now conscious about versions of Elasticsearch that are newer than the model's cut-off date, crafting correct answers around those:

```
🤖 Certainly! Here's a formatted summary of the changes in Elasticsearch versions 8.14.2 and 8.14.3:

**Elasticsearch 8.14.2:**

- **Known Issue:**
  - Upgrading clusters from version 8.11.4 or earlier with non-master-eligible nodes may result in new functionality not being registered. This is fixed in version 8.15.0.

- **Bug Fixes:**
  - **Data streams:** Fixed lazy rollover request to rollover the target data stream once.
  - **ES|QL:** Addressed ESQL cancellation for exchange requests and issues with SingleValueQuery.LuceneQuery.
  - **Infra/Scripting:** Added array size check before returning array item in script doc values.
  - **Infra/Settings:** Ensured file settings readiness is guarded on file settings support.
  - **Machine Learning:** Resolved IndexOutOfBoundsException during inference.
  - **Mapping:** Re-defined index.mapper.dynamic setting for smoother 7.x to 8.x upgrades.
  - **Ranking:** Corrected the 'from' parameter when using sub_searches and rank.
  - **Search:** Supported hexstring for byte painless scorers and fixed tracking of collapse with docvalue_fields.

**Elasticsearch 8.14.3:**

- **Known Issue:**
  - Same as in 8.14.2 regarding the upgrade process and non-master-eligible nodes.

- **Bug Fixes:**
  - **Cluster Coordination:** Ensured tasks preserve versions in MasterService.
  - **ES|QL:** Implemented a compute listener.
  - **Mapping:** Set ignore_malformed only for the @timestamp automatically.
  - **TSDB:** Prohibited setting or updating the index.time_series.end_time in normal indices.

For both versions, users should be aware of the known issue related to upgrading clusters and follow the recommended resolution until the fix is available in version 8.15.0.

**URL References:**
- [Elasticsearch 8.14.2 Release Notes](https://www.elastic.co/guide/en/elasticsearch/reference/master/release-notes-8.14.2.html)
- [Elasticsearch 8.14.3 Release Notes](https://www.elastic.co/guide/en/elasticsearch/reference/master/release-notes-8.14.3.html)
```

Exciting, right? But how can we quantify the improvements in our query at this point? **Let's see the numbers together!**

## Measuring success

To assess the performance implied by our changes, we've compiled a test suite based on user behavior, each containing a question plus a curated list of results that are considered relevant to answer it. Those will cover a wide wide range of subjects and query styles, reflecting the diverse needs of our users. Here's a complete look into it:

```
...
const initialCases: Array<TestCase> = [
  {
    query: 'Can you compare Elasticsearch versions 8.14.3 and 8.14.2?',
    expectedResults: [...], // Elasticsearch version 8.14.3 | Elasticsearch Guide | Elastic, Elasticsearch version 8.14.2 | Elasticsearch Guide | Elastic.
  },
  {
    query: "What are the implications of CVE's 2019-10202, 2019-11756, 2019-15903?",
    expectedResults: [...], // CVE-2016-1837; CVE-2019-11756; CVE-2014-6439. 
  },
  {
    query: 'How to run the support diagnostics tool?',
    expectedResults: [...], // How to install and run the support diagnostics troubleshooting utility; How to install and run the ECK support diagnostics utility.
  },
  {
    query: 'How can I create data views in Kibana via API?',
    expectedResults: [...], // Create data view API | Kibana Guide | Elastic; How to create Kibana data view using api; Data views API | Kibana Guide | Elastic.
  },
  {
    query: 'What would the repercussions be of deleting a searchable snapshot and how would you be able to recover that index?',
    expectedResults: [...], // The repercussions of deleting a snapshot used by searchable snapshots; Does delete backing index delete the corresponding searchable snapshots, and vice versa?; Can one use a regular snapshot to restore searchable snapshot indices?; [ESS] Can deleted index data be recovered Elastic Cloud / Elasticsearch Service?.
  },
  {
    query: 'How can I create a data view in Kibana?',
    expectedResults: [...], // Create a data view | Kibana Guide | Elastic; Create data view API | Kibana Guide [8.2] | Elastic; How to create Kibana data view using api.
  },
  {
    query: 'Do we have an air gapped version of the Elastic Maps Service?',
    expectedResults: [...], // Installing in an air-gapped environment | Elastic Installation and Upgrade Guide [master] | Elastic; Connect to Elastic Maps Service | Kibana Guide | Elastic; 1.6.0 release highlights | Elastic Cloud on Kubernetes | Elastic.
  },
  {
    query: 'How to setup an enrich processor?',
    expectedResults: [...], // Set up an enrich processor | Elasticsearch Guide | Elastic; Enrich processor | Elasticsearch Guide | Elastic; Enrich your data | Elasticsearch Guide | Elastic.
  },
  {
    query: 'How to use index lifecycle management (ILM)?',
    expectedResults: [...], // Tutorial: Automate rollover with ILM | Elasticsearch Guide | Elastic; ILM: Manage the index lifecycle | Elasticsearch Guide | Elastic; ILM overview | Elasticsearch Guide | Elastic.
  },
  {
    query: 'How to rotate my ECE UI proxy certificates?',
    expectedResults: [...], // Manage security certificates | Elastic Cloud Enterprise Reference | Elastic; Generate ECE Self Signed Proxy Certificate; ECE Certificate Rotation (2.6 -> 2.10).
  },
  {
    query:
      'How to rotate my ECE UI proxy certificates between versions 2.6 and 2.10?',
    expectedResults: [...], // ECE Certificate Rotation (2.6 -> 2.10); Manage security certificates | Elastic Cloud Enterprise Reference | Elastic; Generate ECE Self Signed Proxy Certificate.
  }
];
...
```

But how do we turn those test cases into quantifiable success? To this end, we have employed Elasticsearch's [Ranking Evaluation API](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html) alongside with the [Precision at K (P@K)](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html#k-precision) metric to determine how many relevant results are returned between the first *K* hits of a query. As we're interested in the top 3 results being fed into the LLM, we're making K = 3 here.

To automate the computation of this metric against our curated list of questions and effectively assess our performance gains, we used *TypeScript/Node.js* to create a simple script wrapping everything up. First, we define a function to make the corresponding *Ranking Evaluation* API calls:

```
const rankingEvaluation = async (
    // The query to execute ("before" or "after").
    getSearchRequestFn: (queryText: string) => string
) =>
    const testSuite = getTestSuite();
    const rankEvalResult = await elasticsearchClient.rankEval({
      index: 'knowledge-search',
      body: {
    metric: {
      precision: {
        k: 3,
        relevant_rating_threshold: 1,
      },
    },
    // For each test case, we'll have one item here.
    requests: testSuite.map((testCase) => ({
      id: testCase.queryText,
      request: getSearchRequestFn(testCase.queryText),
      ratings: testCase.expectedResults.map(({ _id, _index }) => ({
        _index,
        _id,
        rating: 1, // A value >= 1 means relevant.
      })),
    })),
      },
    });
    // Return a normalized version of the data.
    return transformRankEvalResult(rankEvalResult);
}
```

After that, we need to define the search queries *before* and *after* the optimizations:

```
// Before the optimizations.
const getSearchRequestBefore = (queryText: string): any => ({
  query: {
    bool: {
      should: [
        {
          multi_match: {
            query: queryText,
            minimum_should_match: '1<-1 3<49%',
            type: 'cross_fields',
            fields: ['title', 'summary', 'body', 'id'],
          },
        },
        {
          multi_match: {
            query: queryText,
            type: 'phrase',
            boost: 9,
            fields: [
              'title.stem',
              'summary.stem',
              'body.stem',
            ],
          },
        },
        {
          text_expansion: {
            'ml.inference.title_expanded.predicted_value': {
              model_id: '.elser_model_2',
              model_text: queryText,
            },
          },
        },
        {
          text_expansion: {
            'ml.inference.summary_expanded.predicted_value': {
              model_id: '.elser_model_2',
              model_text: queryText,
            },
          },
        },
      ],
    },
  },
});

// After the optimizations.
const getSearchRequestAfter = (queryText: string): any => {
  const versions = getVersionsFromQueryText(queryText);
  const matchesKeywords = [
    {
      multi_match: {
        query: queryText,
        minimum_should_match: '1<-1 3<49%',
        type: 'cross_fields',
        fields: [
          'title',
          'summary',
          'body',
          'id',
          'ai_fields.ai_subtitle',
          'ai_fields.ai_summary',
          'ai_fields.ai_questions_answered',
          'ai_fields.ai_tags',
        ],
      },
    },
    {
      multi_match: {
        query: queryText,
        type: 'phrase',
        boost: 9,
        slop: 0,
        fields: [
          'title.stem',
          'summary.stem',
          'body.stem',
          'ai_fields.ai_subtitle.stem',
          'ai_fields.ai_summary.stem',
          'ai_fields.ai_questions_answered.stem',
        ],
      },
    },
  ];

  const matchesSemantics = [
    {
      text_expansion: {
        'ml.inference.title_expanded.predicted_value': {
          model_id: '.elser_model_2',
          model_text: queryText,
        },
      },
    },
    {
      text_expansion: {
        'ml.inference.summary_expanded.predicted_value': {
          model_id: '.elser_model_2',
          model_text: queryText,
        },
      },
    },
    {
      text_expansion: {
        'ai_fields.ml.inference.ai_subtitle_expanded.predicted_value': {
          model_id: '.elser_model_2',
          model_text: queryText,
        },
      },
    },
    {
      text_expansion: {
        'ai_fields.ml.inference.ai_summary_expanded.predicted_value': {
          model_id: '.elser_model_2',
          model_text: queryText,
        },
      },
    },
    {
      text_expansion: {
        'ai_fields.ml.inference.ai_questions_answered_expanded.predicted_value':
          {
            model_id: '.elser_model_2',
            model_text: queryText,
          },
      },
    },
  ];

  const matchesCvesAndVersions = [
    {
      bool: {
        filter: {
          term: {
            category: 'cve',
          },
        },
        must: {
          match: {
            title: {
              query: queryText,
              boost: 10,
            },
          },
        },
      },
    },
    ...(versions.length > 0
      ? [
          {
            bool: {
              filter: {
                term: {
                  category: 'documentation',
                },
              },
              must: {
                terms: {
                  version: versions,
                  boost: 4,
                },
              },
            },
          },
        ]
      : []),
  ];

  return {
    query: {
      bool: {
        should: [
          ...matchesKeywords,
          ...matchesSemantics,
          ...matchesCvesAndVersions,
        ]
      },
    },
    collapse: {
      // Alias to the collapse key for each underlying index. 
      field: 'collapse_field' 
    },
  };
};
```

Then, we'll output the resulting metrics for each query:

```
const [rankEvaluationBefore, rankEvaluationAfter] =
  await Promise.all([
    rankingEvaluation(getSearchRequestBefore), // The "before" query.
    rankingEvaluation(getSearchRequestAfter), // The "after" query.
  ]);

console.log(`Before -> Precision at K = 3 (P@K):`);
console.table(rankEvaluationBefore);

console.log(`After -> Precision at K = 3(P@k):`);
console.table(rankEvaluationAfter);

// Computing the change in P@K.
const metricScoreBefore = rankEvaluationBefore.getMetricScore();
const metricScoreAfter = rankEvaluationAfter.getMetricScore();

const percentDifference =
  ((metricScoreAfter - metricScoreBefore) * 100) / metricScoreBefore;

console.log(`Change in P@K: ${percentDifference.toFixed(2)}%`);
```

Finally, by running the script against our *development* Elasticsearch instance, we can see the following output demonstrating the P@K or (P@3) values for each query, *before* and *after* the changes. That is – how many results on the top 3 are considered relevant to the response:

![Script output for the ranking evaluation using the P@K metric](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta011b61ca9ef32e9/6a17d7be7b54f914718b371c/c89071c3194eb69f251b6716ea6341a6e423c684-1061x580.png)

## Improvements observed

As an archer carefully adjusts for a precise shot, our recent efforts into relevance have brought considerable improvements in precision over time. Each one of the previous enhancements, in sequence, were small steps towards achieving better accuracy in our RAG-search results, and overall user experience. Here's a look at how our efforts have improved performance across various queries:

#### Before and after – `P@K`

> Relevant results in the top 3: `❌ = 0`, `🥉 = 1`, `🥈 = 2`, `🥇 = 3`.

| Query Description | P@K Before | P@K After | Change |
| --- | --- | --- | --- |
| Support Diagnostics Tool | 0.333 🥉 | 1.000 🥇 | +200% |
| Air Gapped Maps Service | 0.333 🥉 | 0.667 🥈 | +100% |
| CVE Implications | 0.000 ❌ | 1.000 🥇 | ∞ |
| Enrich Processor Setup | 0.667 🥈 | 0.667 🥈 | 0% |
| Proxy Certificates Rotation | 0.333 🥉 | 0.333 🥉 | 0% |
| Proxy Certificates Version-specific Rotation | 0.333 🥉 | 0.333 🥉 | 0% |
| Searchable Snapshot Deletion | 0.667 🥈 | 1.000 🥇 | +50% |
| Index Lifecycle Management Usage | 0.667 🥈 | 0.667 🥈 | 0% |
| Creating Data Views via API in Kibana | 0.333 🥉 | 0.667 🥈 | +100% |
| Kibana Data View Creation | 1.000 🥇 | 1.000 🥇 | 0% |
| Comparing Elasticsearch Versions | 0.000 ❌ | 0.667 🥈 | ∞ |
| Maximum Bucket Size in Aggregations | 0.000 ❌ | 0.333 🥉 | ∞ |

**Average** `P@K` **Improvement: +78.41% 🏆🎉**. Let's summarize a few observations about our results:

**Significant Improvements**: With the measured overall **+78.41%** of relevance increase, the following queries – *Support Diagnostics Tool*, *CVE implications*, *Searchable Snapshot Deletion, Comparing Elasticsearch Versions* – showed substantial enhancements. These areas not only reached the *podium* of search relevance but did so with flying colors, significantly outpacing their initial performances!

**Opportunities for Optimization**: Certain queries like the *Enrich Processor Setup*, *Kibana Data View Creation* and *Proxy Certificates Rotation* have shown reliable performances, without regressions. These results underscore the effectiveness of our core search strategies. However, those remind us that precision in search is an ongoing effort. These static results highlight where we'll focus our efforts to sharpen our aim throughout the next iterations. As we continue, we'll also expand our test suite, incorporating more diverse and meticulously selected use cases to ensure our enhancements are both relevant and robust.

## What's next? 🔎

The path ahead is marked by opportunities for further gains, and with each iteration, we aim to push the RAG implementation performance and overall experience even higher. With that, let's discuss areas that we're currently interested in!

1. **Our data can be futher optimized for search**: Although we have a large base of sources, we observed that having semantically close search candidates often led to less effective chatbot responses. Some of the crawled pages aren't really valuable, and often generate noise that impacts relevance negatively. To solve that, we can curate and enhance our existing knowledge base by applying a plethora of techniques, making it lean and effective to ensure an optimal search experience.
2. **Chatbots must handle conversations – and so must RAG searches**: It's common user behavior to ask follow-up questions to the chatbot. A question asking "How to configure Elasticsearch on a Linux machine?" followed by "What about Windows?" should query something like "How to configure Elasticsearch on a Linux machine?" (not the raw 2nd question). The RAG query approach should find the most relevant content regarding the entire context of the conversation.
3. **Conditional context inclusion**: By extracting the semantic meaning of the user question, it would be possible to conditionally include pieces of data as context, saving token limits, making the generated content even more relevant, and potentially saving *round trips* for search and external services.

## Conclusion

In this installment of our series on GenAI for Customer Support, we have thoroughly explored the enhancements to the Retrieval-Augmented Generation (RAG) search within Elastic's customer support systems. By refining the interaction between large language models and our search algorithms, we have successfully elevated the precision and effectiveness of the Support AI Assistant.

Looking ahead, we aim to further optimize our search capabilities and expand our understanding of user interactions. This continuous improvement will focus on refining our AI models and search algorithms to better serve user needs and enhance overall customer satisfaction.

Stay tuned for more insights and updates as we continue to push the boundaries of what's possible with AI in customer support, and don't forget to join us in our next discussion, where we'll explore how Observability plays a critical role in monitoring, diagnosing, and optimizing the performance and reliability of the Support AI Assistant as we scale!

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1092d0334a5b571c/6a572545f71286c608af57e4/3e67c4eeaa3d9411e97ee8b2ae74078a8177a911-2048x1143.avif)

[Operations](/search-labs/blog/category/operations)[Inside Elastic](/search-labs/blog/category/inside-elastic)

### Your compliance posture just got an upgrade: Elasticsearch now supports FIPS 140-3

July 07, 2026|[Fabio Busatto](/search-labs/author/fabio-busatto)

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbe7de1872f1527e3/6a17de303e9e452974ba1374/a70c5403064d5bbceff66a17373332362227f13c-720x420.jpg)

[Inside Elastic](/search-labs/blog/category/inside-elastic)

### How Elasticsearch cuts time-series storage by 34% with synthetic \_id and bloom filters

May 28, 2026|[Tanguy Leroux](/search-labs/author/tanguy-leroux)|[+2](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter