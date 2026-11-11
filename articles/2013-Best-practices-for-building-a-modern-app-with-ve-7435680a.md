---
title: 'Best practices for building a modern app with vector search'
company: Elastic
tag: 召回
date: 2026-06-09
url: https://www.elastic.co/search-labs/blog/vector-search-best-practices-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Best practices for building a modern app with vector search

Exploring six vector search tips for building modern AI search applications entirely on Elasticsearch, with an opinionated rationale at each architectural decision.

June 09, 2026

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

[Vector Database](/search-labs/blog/category/vector-database)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Agentic AI](/search-labs/blog/category/agentic-ai)

Jump to

Share

Building a modern AI application means stitching together a lot of moving parts: an embedding model provider, a vector store, a hybrid retrieval layer, a large language model (LLM) orchestrator, and some kind of script to interact with the parts. Most tutorials show you how to wire up each piece separately. This one shows you how to build all of them with Elasticsearch alone. I chose Elasticsearch as my vector database because it supports hybrid search and out-of-the-box quantization, so you get semantic understanding, keyword precision, and fast similarity search without bolting on extra infrastructure. Along the way, it explains why each architectural decision matters.

*We'll use Python to demonstrate each tip, but none of them are language-specific; you could follow along just as well with the* [*Kibana Dev Tools console*](https://www.elastic.co/docs/explore-analyze/query-filter/tools/console)*, the Kibana UI, or any* [*Elasticsearch client*](https://www.elastic.co/docs/reference/elasticsearch-clients)*.*

## Prerequisites

* **Elasticsearch 9.3+** (Elastic Cloud Serverless or self-managed). [Start a free trial](https://cloud.elastic.co/registration).
* **Kibana** access with an API key that has full privileges for Analytics (required for Elastic Agent Builder and Elastic Workflows)
* **Python 3.9+**

```
pip install elasticsearch python-dotenv requests
```

* **Environment variables** in a `.env` file:

```
ELASTICSEARCH_URL=https://your-cluster-url
ELASTICSEARCH_API_KEY=your-api-key
KIBANA_URL=https://your-kibana-url
```

## What we're building

By the end of this tutorial, you'll have a working app with five layers running on Elastic. If you want to skip ahead and run the code, grab the companion [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/modern-app-vector-search-best-practices-elasticsearch/notebook.ipynb).

* **Managed inference:** Embeddings without managing machine learning (ML) infrastructure.
* **Semantic index:** An index designed for both BM25 and [semantic search](https://www.elastic.co/docs/solutions/search/get-started/semantic-search).
* **Hybrid retrieval** **(reciprocal rank fusion [RRF]):** The best of lexical and semantic search combined.
* **AI agent:** A natural language interface over your data.
* **Automated workflow:** A scheduled pipeline that fetches, indexes, and summarizes new content.

Elastic allows you to use all five layers in just one deployment.

![Architecture diagram showing how raw data flows from a data source through Elastic Workflows into an Elasticsearch index with semantic and BM25 search using EIS, then is queried by an AI Agent via hybrid retrieval.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6e51871edd245c4c/6a47761d31bdbb10d78b4381/bc50b1fe9914a9d1c6e4da9bdb470ace8411400a-1999x1254.png)

## Tip 1: Use managed inference instead of external embedding APIs

The first decision in any vector search project is where to generate embeddings. The obvious answer is to call an external API (OpenAI, Cohere, Jina AI) directly, but this means managing a separate billing account, API key rotation, rate limit monitoring, and network latency on every document you index.

Another option is to use [Elastic Inference Service](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis) (EIS), a managed GPU-accelerated inference layer built into Elasticsearch. You configure it once, and embeddings are generated inside the Elastic infrastructure as documents are indexed.

For this tutorial, we’ll use [**jina-embeddings-v5-text**](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text)**,** an out-of-the-box model with high performance for retrieval-optimized embeddings.

### When to use EIS vs. an external API

Use EIS when you want a single Elastic billing account and your organization doesn’t have a default model for all its systems. Use an external provider when your team has chosen an unsupported model across systems and needs the same embeddings everywhere for consistency.

```
es_client = Elasticsearch(ELASTICSEARCH_URL, api_key=ELASTIC_API_KEY)

# Jina Embeddings v5 comes with a preconfigured endpoint in EIS.
# No need to create a custom inference endpoint, just reference the preconfigured ID.
INFERENCE_ENDPOINT_ID = ".jina-embeddings-v5-text-small"
print(f"Using preconfigured inference endpoint: {INFERENCE_ENDPOINT_ID}")
```

The inference endpoint is now ready. Elasticsearch will call it automatically whenever you index a document into a field that uses [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text).

## Tip 2: Design hybrid-ready indices from day one

A common mistake is designing your index for semantic search and later trying to add hybrid search. Hybrid search requires both semantic retrieval and BM25. Retrofitting this after you have millions of documents means a full reindex.

The correct pattern is to use [`copy_to`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/copy-to) at mapping time. Keep the original text fields for BM25, and automatically copy their content into a dedicated `semantic_text` field for vector search.

```
INDEX_NAME = "tech-articles"

index_mappings = {
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "copy_to": "semantic_field",
                "fields": {"keyword": {"type": "keyword"}},
            },
            "content": {"type": "text", "copy_to": "semantic_field"},
            "category": {"type": "keyword"},
            "published_date": {"type": "date"},
            "semantic_field": {
                "type": "semantic_text",
                "inference_id": INFERENCE_ENDPOINT_ID,
            },
        }
    }
}

if not es_client.indices.exists(index=INDEX_NAME):
    response = es_client.indices.create(index=INDEX_NAME, body=index_mappings)
    print(f"Created index: {INDEX_NAME}")
else:
    print(f"Index '{INDEX_NAME}' already exists, skipping creation")
```

A few things to understand about this mapping:

* `title` is a [`text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/text) field with a [`keyword`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/keyword) subfield, available for BM25 [full-text search](https://www.elastic.co/docs/solutions/search/full-text) and for [aggregations](https://www.elastic.co/docs/explore-analyze/query-filter/aggregations) and filtering via `title.keyword`.
* `content` is a standard `text` field, used for full-text search.
* `copy_to: "semantic_field"` means Elasticsearch automatically populates `semantic_field` from `title` and `content` at ingest time. You don't need to send `semantic_field` in your documents.
* `semantic_text` with `inference_id` tells Elasticsearch to call the EIS endpoint to generate embeddings for `semantic_field` automatically.

To understand why to use `copy_to` instead of separate semantic fields, see the [Elasticsearch guidance on searching as few fields as possible](https://www.elastic.co/docs/deploy-manage/production-guidance/optimize-performance/search-speed#search-as-few-fields-as-possible).

## Tip 3: Use bulk operations for scalable ingestion

Never index documents one at a time in a production application. Each individual `index` request is a separate HTTP call.

Elasticsearch exposes the [`_bulk`](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk) [API](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-bulk) for batching multiple index operations into a single HTTP request. Combine it with a [generator function](https://wiki.python.org/moin/Generators) to avoid loading your entire [dataset](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/modern-app-vector-search-best-practices-elasticsearch/dataset.jsonhttps://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/modern-app-vector-search-best-practices-elasticsearch/dataset.jsonhttps://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/modern-app-vector-search-best-practices-elasticsearch/dataset.jsonhttps://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/modern-app-vector-search-best-practices-elasticsearch/dataset.jsonhttps://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/modern-app-vector-search-best-practices-elasticsearch/dataset.json) into memory.

```
from elasticsearch import helpers

def build_data(json_file, index_name):
    """Generator that yields documents for bulk indexing."""
    with open(json_file, "r") as f:
        data = json.load(f)

    for doc in data:
        yield {"_index": index_name, "_source": doc}

try:
    success, failed = helpers.bulk(
        es_client,
        build_data("dataset.json", INDEX_NAME),
    )
    print(f"{success} documents indexed successfully")

    if failed:
        print(f"Failed documents: {failed}")
except Exception as e:
    print(f"Error: {str(e)}")

# Verify document count
count = es_client.count(index=INDEX_NAME)
print(f"Total documents: {count.body['count']}")
```

### Generator pattern vs. list

Loading all documents into a list before calling `helpers.bulk()` works, but it loads everything into memory at once. A generator yields documents on demand, which means your memory usage stays constant regardless of dataset size.

## Tip 4: Use a hybrid search strategy

[Hybrid search](https://www.elastic.co/what-is/hybrid-search) combines BM25 (lexical) and semantic retrieval to get the benefits of both: the precision of term matching and the contextual understanding of dense vector search. With your index already designed to support both BM25 and semantic search, the question is how to merge the two ranked result lists.

Elasticsearch provides built-in methods to combine semantic and full-text strategies through its [retrievers framework](https://www.elastic.co/docs/solutions/search/retrievers-overview). In this blog post, we’ll talk about [RRF](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) and [linear combination](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/linear-retriever), the two methods that were designed to fuse semantical and BM25 results. Each takes a different approach to combining results, and the right choice depends on your data and how much tuning you want to invest.

### [Reciprocal rank fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion)

RRF is the [recommended](https://www.elastic.co/docs/solutions/search/hybrid-search) starting point for hybrid search, as it ignores raw scores and merges results based on rank positions alone. A document ranked third in semantic and fifth in BM25 gets a combined score based on those positions, not the raw numbers. This makes it robust against mismatched score scales; it requires almost no tuning and works well out of the box. The tradeoff is that RRF discards score magnitude: A document that scores dramatically higher than others in one retriever won't get extra credit for that gap.

Elasticsearch also supports [weighted RRF](https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf) for scenarios where you need to boost one retriever over another without switching to score-based merging.

```
def hybrid_search_rrf(query: str, size: int = 3):
    """Hybrid search using RRF."""

    response = es_client.search(
        index=INDEX_NAME,
        body={
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {
                            "standard": {
                                "query": {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["title^2", "content"],
                                    }
                                }
                            }
                        },
                        {
                            "standard": {
                                "query": {
                                    "match": {"semantic_field": {"query": query}}
                                }
                            }
                        },
                    ],
                    "rank_window_size": 50,
                    "rank_constant": 20,
                }
            },
            "size": size,
            "_source": ["title", "category"],
        },
    )

    return response
```

### Reranking with jina-reranker-v3

RRF is fast and reliable, but it ranks by position and has no way to model how well a document actually answers the question. A reranker fixes that. It takes the top-N candidates from RRF and rescores them using a cross-encoder model that reads the query and each document together, producing a relevance score grounded in meaning rather than rank position.

[jina-reranker-v3](https://www.elastic.co/docs/explore-analyze/machine-learning/nlp/ml-nlp-jina#jina-reranker-v3) is available through EIS and uses listwise reranking. It evaluates up to 64 documents in a single inference call using cross-document context, which gives it a global view of the candidate set rather than scoring each document independently.

First, create the reranker inference endpoint:

```
RERANKER_INFERENCE_ID = "jina-reranker-v3-endpoint"

reranker_config = {
    "service": "elastic",
    "service_settings": {"model_id": "jina-reranker-v3"},
}

try:
    es_client.inference.put(
        inference_id=RERANKER_INFERENCE_ID,
        task_type="rerank",
        body=reranker_config,
    )

    print(f"Created reranker endpoint: {RERANKER_INFERENCE_ID}")
except Exception as e:
    if "already_exists" in str(e).lower():
        print(f"Reranker endpoint already exists: {RERANKER_INFERENCE_ID}")
    else:
        raise
```

Then wrap the RRF retriever inside `text_similarity_reranker`:

```
def hybrid_search_with_reranking(query: str, size: int = 3):
    """Hybrid search: RRF retrieval followed by Jina Reranker v3."""
    response = es_client.search(
        index=INDEX_NAME,
        body={
            "retriever": {
                "text_similarity_reranker": {
                    "retriever": {
                        "rrf": {
                            "retrievers": [
                                {
                                    "standard": {
                                        "query": {
                                            "multi_match": {
                                                "query": query,
                                                "fields": ["title^2", "content"],
                                            }
                                        }
                                    }
                                },
                                {
                                    "standard": {
                                        "query": {
                                            "match": {"semantic_field": {"query": query}}
                                        }
                                    }
                                },
                            ],
                            "rank_window_size": 50,
                            "rank_constant": 20,
                        }
                    },
                    "field": "semantic_field",
                    "inference_id": RERANKER_INFERENCE_ID,
                    "inference_text": query,
                    "rank_window_size": 25,
                }
            },
            "size": size,
            "_source": ["title", "category"],
        },
    )

    return response
```

RRF does the heavy lifting; it efficiently narrows thousands of candidates to the top 25 using rank fusion. The reranker then reads the query and document together and reorders those 25 by true semantic relevance.

## Tip 5: Add AI reasoning with Agent Builder

That's where [Elastic Agent Builder](https://www.elastic.co/docs/explore-analyze/ai-features/agent-builder/get-started) comes in, allowing you to quickly create LLM-powered agents that utilize your Elasticsearch data as the source using natural language queries. Unlike [LangChain](https://docs.langchain.com/) or [LlamaIndex](https://www.llamaindex.ai/) (which require you to bring your own LLM, manage prompts, and configure retrieval pipelines), Agent Builder is native to Kibana: It has built-in tracing, uses your existing Elasticsearch indices, and supports [Elasticsearch Query Language](https://www.elastic.co/docs/reference/query-languages/esql) (ES|QL) for precise data access alongside semantic search. It also provides communication with external systems via Model Context Protocol (MCP) server, or agent-to-agent (A2A) servers.

The agent for this tutorial uses the [**Elastic Managed LLM**](https://www.elastic.co/docs/reference/kibana/connectors-kibana/elastic-managed-llm) by default, which is available on Elastic Cloud with no additional API key or connector configuration.

```
headers = {
    "kbn-xsrf": "true",
    "Authorization": f"ApiKey {ELASTIC_API_KEY}",
    "Content-Type": "application/json",
}

# Create a custom ES|QL tool that returns articles filtered by publish date.
# Custom tools expose a specific parameterized query the agent can invoke safely,
# without giving it free-form access to the entire cluster.
esql_tool_payload = {
    "id": "tech-articles-recent",
    "type": "esql",
    "description": (
        "Returns recent articles from the knowledge base filtered by publish date. "
        "Use this when the user asks about recent content, articles from a specific "
        "time period, or wants to browse by date."
    ),
    "tags": ["analytics", "tech-articles"],
    "configuration": {
        "query": (
            "FROM tech-articles "
            "| WHERE published_date >= ?startDate "
            "| KEEP title, category, published_date "
            "| SORT published_date DESC "
            "| LIMIT ?limit"
        ),
        "params": {
            "startDate": {
                "type": "date",
                "description": "Start date for filtering articles (ISO 8601, e.g. 2024-01-01)",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of articles to return",
            },
        },
    },
}

response = requests.post(
    f"{KIBANA_URL}/api/agent_builder/tools",
    headers=headers,
    json=esql_tool_payload,
)

if response.status_code == 200:
    print(f"Created custom ES|QL tool: {esql_tool_payload['id']}")
else:
    print(f"Error creating tool: {response.text}")

agent_payload = {
    "id": "tech-articles-assistant",
    "name": "Tech Articles Assistant",
    "description": "An AI assistant that helps users find information about technology topics from our knowledge base.",
    "configuration": {
        # Uses Elastic Managed LLM by default. No connector_id needed.
        "tools": [
            {
                "tool_ids": [
                    "platform.core.search",
                    "platform.core.execute_esql",
                    "tech-articles-recent",
                ]
            }
        ],
        "instructions": f"""You are a helpful assistant that answers questions about technology topics.

Use the search tool to find relevant articles from the '{INDEX_NAME}' index.
Use the tech-articles-recent tool when the user asks about recent or time-filtered content.
When searching, prefer semantic search for natural language questions.
Always cite the article titles when providing information.
If you cannot find relevant information, say so clearly.""",
    },
}

response = requests.post(
    f"{KIBANA_URL}/api/agent_builder/agents",
    headers=headers,
    json=agent_payload,
    verify=True,
)

if response.status_code == 200:
    agent_data = response.json()
    agent_id = agent_data.get("id")
    print(f"Created agent: {agent_id}")
else:
    print(f"Error creating agent: {response.text}")
    agent_id = None
```

Once created, you can chat with the agent programmatically:

```
def chat_with_agent(agent_id: str, message: str):
    """Send a message to the agent and get a response."""
    chat_payload = {"input": message, "agent_id": agent_id}

    response = requests.post(
        f"{KIBANA_URL}/api/agent_builder/converse",
        headers=headers,
        json=chat_payload,
        verify=True,
    )

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text, "status_code": response.status_code}

# Example conversation
if agent_id:
    result = chat_with_agent(
        agent_id, "What are the best practices for building RAG applications?"
    )
    print(json.dumps(result, indent=2))
```

The agent has access to three tools:

* `platform.core.search`: For semantic and keyword search over your index.
* `platform.core.execute_esql`: For ad-hoc analytical queries using ES|QL.
* `tech-articles-recent`: A custom ES|QL tool with a predefined query for date-filtered browsing.

The LLM decides which tool to use based on the question. Custom tools let you expose specific query patterns that the agent can invoke safely.

### When to use Agent Builder vs. LangChain/LlamaIndex

Use Agent Builder when you want native Kibana integration, built-in execution tracing, and direct access to ES|QL without custom tool implementation. Use LangChain or LlamaIndex when you need to connect multiple data sources beyond Elasticsearch, use model providers not yet supported by Agent Builder, or require custom agent architectures (multi-agent or reflection loops, among others).

## Tip 6: Automate with Elastic Workflows

Search pipelines often have a recurring pattern: Fetch new data from an external source, index it, and then trigger some action. You can implement this using external tools, but Elastic Workflows gives you a YAML-based alternative that runs inside Elasticsearch.

[**Workflows**](https://www.elastic.co/docs/explore-analyze/workflows) is a technical preview feature that lets you define multistep automation pipelines using declarative YAML. It supports HTTP calls, Elasticsearch operations, conditional logic, loops, and (most relevantly here) invoking AI agents as a step.

***Note:*** *Workflows is in technical preview as of Elasticsearch 9.3. The API and YAML syntax may change in future releases. To enable the Workflows UI, go to* ***Kibana: Stack Management > Advanced Settings****, and set* `workflows:ui:enabled` *to* `true`*. Find detailed information* [*here*](https://www.elastic.co/docs/explore-analyze/workflows/get-started#workflows-prerequisites)*.*

The workflow below is a Hacker News digest: It fetches the top five stories from the [Hacker News API](https://github.com/HackerNews/API), indexes each one into our `tech-articles` index (with automatic embedding via EIS), and then asks the AI agent to summarize the article's topics.

![Flowchart showing an Elastic workflow that fetches top stories from the Hacker News API, indexes them with embeddings into Elasticsearch, and invokes an AI Agent to generate a summary.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbcbc396333f202b8/6a47761bde9777e82eca63af/c01e76cc6d27b39825aeab29baa7a5db73a3b43b-1999x1125.png)

Create this workflow by pasting the YAML into the Kibana Workflows UI:

```
name: Hacker News Digest
description: >
  Fetches the latest top stories from the Hacker News public API, indexes them
  into Elasticsearch with semantic embeddings, then asks the AI agent to
  summarize the key themes from the freshly ingested content.
enabled: true
tags: ["ingestion", "hacker-news", "agent", "demo"]

consts:
  indexName: tech-articles
  hnApiBase: "https://hacker-news.firebaseio.com/v0"
  agentId: tech-articles-assistant

triggers:
  - type: manual   # change to "schedule" with a cron expression for automation

steps:
  # Step 1: Fetch top story IDs from Hacker News
  - name: fetch_top_stories
    type: http
    with:
      url: "{{ consts.hnApiBase }}/topstories.json"
      method: GET

  # Step 2: For each story ID, fetch details and index into Elasticsearch
  - name: process_stories
    type: foreach
    foreach: "${{ steps.fetch_top_stories.output.data | slice: 0, 5 }}"
    steps:
      - name: fetch_story_detail
        type: http
        with:
          url: "{{ consts.hnApiBase }}/item/{{ foreach.item }}.json"
          method: GET

      - name: index_story
        type: elasticsearch.request
        with:
          method: POST
          path: "/{{ consts.indexName }}/_doc"
          body:
            title: "{{ steps.fetch_story_detail.output.data.title }}"
            content: "{{ steps.fetch_story_detail.output.data.text | default: steps.fetch_story_detail.output.data.title }}"
            category: "hacker-news"
            url: "{{ steps.fetch_story_detail.output.data.url }}"

  # Step 3: Ask the agent to summarize the freshly indexed stories
  - name: ask_agent
    type: ai.agent
    with:
      agent_id: "{{ consts.agentId }}"
      message: "What are the main themes and topics from the latest Hacker News stories?"

  - name: log_summary
    type: console
    with:
      message: "${{ steps.ask_agent.output }}"
```

The [`ai.agent`](https://www.elastic.co/docs/explore-analyze/workflows/steps/ai-steps) step in the workflow calls the Agent Builder agent you'll create in the next section. This is the **bidirectional agent-workflow pattern**: Workflows handle deterministic tasks (HTTP calls, indexing, looping) and delegate reasoning to agents. Agents handle open-ended questions and delegate structured execution to workflows.

Here you can see the final results of the workflow:

![Screenshot of an Elastic workflow execution output showing the step-by-step processing of Hacker News stories, including fetch, index, and AI agent summary generation with themed results.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0395b77c54d97f30/6a4776215581827078a7580e/3b872eac9261f81469a4651e794027e046d7cea8-1999x1253.png)

## Conclusion

We walked through six tips for building a modern AI search application entirely on Elasticsearch, from managed inference and hybrid-ready index design, through scalable ingestion and hybrid retrieval with RRF, to automated workflows and AI agents. Together, these practices give you a production-grade AI search application running entirely on Elasticsearch, without external orchestrators, separate vector databases, or additional embedding API accounts.

## Recommended lectures

* [Deep dive on](https://www.elastic.co/search-labs/blog/semantic-text-chunking-index-options) [`semantic_text`](https://www.elastic.co/search-labs/blog/semantic-text-chunking-index-options) [chunking options](https://www.elastic.co/search-labs/blog/semantic-text-chunking-index-options) for long documents.
* [Weighted RRF](https://www.elastic.co/search-labs/blog/weighted-reciprocal-rank-fusion-rrf) for fine-tuning hybrid search relevance.
* [Agent Builder GA announcement](https://www.elastic.co/search-labs/blog/agent-builder-elastic-ga) for the full feature overview.
* [jina-embeddings-v5-text models](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text) just released February 2026.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltdfa35fbcbbf4959f/6a1705b9dc55de19a4e00d07/e54132e915217063e9ed0ec45059c6cfc38e31dd-1280x720.png)

[ES|QL](/search-labs/blog/category/esql)[Vector Database](/search-labs/blog/category/vector-database)

### LINQ to Elasticsearch ES|QL: Write C#, query Elasticsearch

April 01, 2026|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt88526af16bafdb7c/6a17d7807f6f15825dc0998d/d11e1ba058784ec92b8953fb8db62e1bad21c210-720x420.jpg)

[Integrations](/search-labs/blog/category/integrations)[Vector Database](/search-labs/blog/category/vector-database)[AI tools](/search-labs/blog/category/ai-tools)

### 4 NVIDIA AI tasks, 1 Elasticsearch API: Embeddings, chat, completion, and rerank

July 21, 2026| [Jan Kazlouski](/search-labs/author/jan-kazlouski)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter