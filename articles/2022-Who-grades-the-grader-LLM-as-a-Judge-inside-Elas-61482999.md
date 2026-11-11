---
title: 'Who grades the grader? LLM-as-a-Judge inside Elasticsearch Workflows'
company: Elastic
tag: 评测
date: 2026-07-06
url: https://www.elastic.co/search-labs/blog/rag-evaluation-elasticsearch-workflows
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Who grades the grader? LLM-as-a-Judge inside Elasticsearch Workflows

Find out if your RAG agent is ready to ship. Score it on correctness, faithfulness and retrieval quality using only Elasticsearch Workflows and two Claude models.

July 06, 2026

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

[Agentic AI](/search-labs/blog/category/agentic-ai)[AI](/search-labs/blog/category/ai)[Python](/search-labs/blog/category/python-programming)

Jump to

Share

Build a complete RAG [evaluation pipeline](https://docs.langchain.com/langsmith/evaluation-concepts#offline-evaluations) inside [Elasticsearch Workflows](https://www.elastic.co/docs/explore-analyze/workflows): no external eval framework, no extra infrastructure. A small model answers questions from your knowledge base; a stronger model scores each answer on correctness, faithfulness and context relevance. On a 35-case HotpotQA test, Claude Haiku 4.5 scored 0.74 correctness and 0.90 faithfulness: enough to pinpoint exactly where retrieval or reasoning breaks down. The knowledge base, judgement list, workflow execution and scored results all live in the same system.

## Prerequisites

* An Elastic Cloud cluster or self-managed Elasticsearch/Kibana 9.4+. You can [start a free trial](https://cloud.elastic.co/registration) if you don't have one.
* Python 3.13

## What is LLM-as-a-Judge?

LLM-as-a-Judge uses a stronger language model to automatically score the outputs of a weaker one, replacing inconsistent, unscalable manual review.

Evaluating a RAG system by hand works for a few questions, but it doesn’t scale. If you change your retrieval strategy, your prompt, or your model, you need to recheck every answer. That takes time, and humans are inconsistent scorers.

The [**LLM-as-a-Judge**](https://en.wikipedia.org/wiki/LLM-as-a-Judge) pattern solves this by typically using a strong language model to score the outputs of a weaker one. The idea is straightforward: If a language model can reliably tell whether an answer is correct, you can automate quality checks across hundreds of test cases in minutes.

In this article, the pipeline has two stages:

* **Stage 1 (Answer):** Claude Haiku 4.5 receives a question plus passages retrieved from a knowledge base and produces an answer. This is the model you’re evaluating.
* **Stage 2 (Judge):** Claude Sonnet 4.6 receives the same question, the ground-truth answer (the known correct answer), the candidate answer (Stage 1's output), and the passages. It scores the response on three axes.

### **The three RAG evaluation metrics: correctness, faithfulness, context relevance**

| Metric | What it measures | What a low score means |
| --- | --- | --- |
| correctness | Does the candidate match the ground truth? | The agent answered the wrong thing. |
| faithfulness | Is the answer grounded in the retrieved passages? | The agent hallucinated (made something up). |
| context\_relevance | Are the retrieved passages relevant to the question? | Retrieval brought the wrong documents. |

Together, these three metrics tell you *where* a problem lives. A high `correctness` with low `context_relevance` is a red flag: The model answered correctly despite poor retrieval, likely by falling back on its own training data. That works for public knowledge, like Wikipedia, but breaks on private data the model has never seen. A complementary approach [using Ragas metrics with Elasticsearch](https://www.elastic.co/search-labs/blog/elasticsearch-ragas-llm-app-evaluation) explores these evaluation dimensions from a framework-based perspective.

## How to load and index the HotpotQA dataset

The pipeline uses HotpotQA in the distractor configuration: multi-hop questions, each paired with 10 context paragraphs, stored across two Elasticsearch indices. You can follow along with the complete [notebook for this article](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/workflows-evaluate-accuracy-agent-responses/notebook.ipynb), which includes the setup, connection, and all helper code. For this tutorial, you’ll need your `ELASTICSEARCH_URL` and an `ELASTICSEARCH_API_KEY`, which you can obtain by following the [connection details guide](https://www.elastic.co/docs/solutions/elasticsearch-solution-project/search-connection-details), and your `KIBANA_URL`, found on the [Kibana access page](https://www.elastic.co/docs/deploy-manage/deploy/elastic-cloud/access-kibana).

The pipeline uses two [AI connectors](https://www.elastic.co/docs/reference/kibana/connectors-kibana/ai-connector) configured in Kibana: **Anthropic Claude Haiku 4.5** as the answering model (small, cheap, fast) and **Anthropic Claude Sonnet 4.6** as the judge (more capable). This pipeline answers the question: *Is Haiku good enough on this task to be used in production?*

We use [HotpotQA](https://huggingface.co/datasets/hotpotqa/hotpot_qa) in the `distractor` configuration. Each question ships with 10 context paragraphs: two that support the answer and eight distractors. These paragraphs are indexed into the knowledge base that Stage 1 retrieves from. The questions are multi-hop, meaning the answer requires combining information from two different paragraphs.

We sample a subset of questions, flatten their context paragraphs into a knowledge base index, and store the question-answer pairs in a separate judgement list. The data ends up in two Elasticsearch indices:

### **Knowledge base: Context passages**

`hotpot-knowledge-base` holds the context passages that the answering model retrieves from. Each document has a `title` and a `passage`:

```
{"title": "Ed Wood (film)", "passage": "Ed Wood is a 1994 American biographical period comedy-drama film..."}
```

The `passage` field is copied to `semantic_content` (mapped as [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text)) so Stage 1 can retrieve relevant passages using a natural language query without managing embeddings manually.

Elasticsearch automatically generates the embeddings for the indexed passages and for the queries at [semantic search](https://www.elastic.co/docs/solutions/search/semantic-search) time.

```
INDEX_NAME = "hotpot-knowledge-base"

if es_client.indices.exists(index=INDEX_NAME):
    es_client.indices.delete(index=INDEX_NAME)

es_client.indices.create(
    index=INDEX_NAME,
    mappings={
        "properties": {
            "title": {"type": "keyword"},
            "passage": {
                "type": "text",
                "copy_to": "semantic_content",
            },
            "semantic_content": {
                "type": "semantic_text",
                "inference_id": ".jina-embeddings-v5-text-small",
            },
        }
    },
)
print(f"Created index: {INDEX_NAME}")
```

### **Judgement list: Questions and expected answers**

`hotpot-judgement-list` holds the evaluation cases. Each document has a `question` and an `answer` (the ground truth):

```
{"question": "Were Scott Derrickson and Ed Wood of the same nationality?", "answer": "yes"}
```

The `answer` field contains the right answer. The judge in Stage 2 compares the answering model's output against it.

## How the Elasticsearch Workflow runs the evaluation

This [introduction to building automation with Elastic Workflows](https://www.elastic.co/search-labs/blog/elastic-workflows-automation) covers the core concepts of triggers, steps, and data flow in detail.

![Flowchart showing an evaluation pipeline where a Judgement List provides questions and expected answers, a Knowledge Base supplies context passages, Semantic search retrieves top four passages, Haiku 4.5 generates an answer, Sonnet 4.6 scores it against the expected answer, and eval‑results record correctness, faithfulness, and context relevance.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltaff44cfcbcd21fc3/6a55018853c8537c803920aa/b41c6765cadd4a46fa9f76a18defed351c4a36ab-2000x1444.png)

### **Workflow definition**

The workflow is defined in YAML and uploaded via the [Workflows API](https://www.elastic.co/docs/explore-analyze/workflows/steps) (Elastic 9.4+). Here’s the complete definition:

```
WORKFLOW_YAML = """
name: agent_accuracy_eval
description: >
  Batch evaluation. Loads the judgement list, iterates each case with
  a foreach, runs stage 1 (RAG answer with Haiku) and stage 2 (LLM
  judge with Sonnet), and indexes every score into the eval results
  index.
enabled: true

consts:
  kbIndex: hotpot-knowledge-base
  judgeIndex: hotpot-judgement-list
  resultsIndex: eval-results

triggers:
  - type: manual

steps:
  # Load the judgement list (all cases we want to evaluate).
  - name: load_cases
    type: elasticsearch.search
    with:
      index: "{{ consts.judgeIndex }}"
      query:
        match_all: {}
      size: 35

  # One iteration = one evaluation.
  - name: eval_loop
    type: foreach
    foreach: "{{ steps.load_cases.output.hits.hits }}"
    steps:
      - name: retrieve
        type: elasticsearch.search
        with:
          index: "{{ consts.kbIndex }}"
          query:
            semantic:
              field: semantic_content
              query: "{{ foreach.item._source.question }}"
          size: 4

      - name: agent_answer
        type: ai.prompt
        with:
          connector-id: Anthropic-Claude-Haiku-4-5
          prompt: >
            You are a Wikipedia QA assistant. Answer the question
            using ONLY the passages provided. Keep the answer short
            (one line). If the passages do not contain the answer,
            reply "unknown".

            Question: {{ foreach.item._source.question }}

            Passages:
            1. {{ steps.retrieve.output.hits.hits[0]._source.passage }}
            2. {{ steps.retrieve.output.hits.hits[1]._source.passage }}
            3. {{ steps.retrieve.output.hits.hits[2]._source.passage }}
            4. {{ steps.retrieve.output.hits.hits[3]._source.passage }}

      - name: judge
        type: ai.prompt
        with:
          connector-id: Anthropic-Claude-Sonnet-4-6
          prompt: >
            You are a STRICT evaluator. Score the candidate answer
            against the ground truth on three axes. Each score MUST
            be exactly one of these three values: 0.0, 0.5, or 1.0.
            Do not return any other number.

            correctness:
              1.0 = candidate contains the ground truth answer exactly
                    or an unambiguous synonym, and nothing factually wrong.
              0.5 = partially correct (one side of a multi-hop right,
                    or mostly right with minor noise).
              0.0 = wrong, missing, or contradicts the ground truth.

            faithfulness:
              1.0 = every factual claim is supported by the passages.
              0.5 = mostly supported, one minor unsupported claim.
              0.0 = contains at least one unsupported claim.

            context_relevance:
              1.0 = the passages contain enough to answer the question.
              0.5 = partial coverage (one hop covered, the other missing).
              0.0 = passages do not cover the answer.

            Be harsh. If in doubt between two scores, pick the lower one.

            Question: {{ foreach.item._source.question }}
            Ground truth: {{ foreach.item._source.answer }}
            Candidate: {{ steps.agent_answer.output.content }}
            Passages:
            1. {{ steps.retrieve.output.hits.hits[0]._source.passage }}
            2. {{ steps.retrieve.output.hits.hits[1]._source.passage }}
            3. {{ steps.retrieve.output.hits.hits[2]._source.passage }}
            4. {{ steps.retrieve.output.hits.hits[3]._source.passage }}
          schema:
            type: object
            properties:
              correctness:
                type: number
                minimum: 0
                maximum: 1
              faithfulness:
                type: number
                minimum: 0
                maximum: 1
              context_relevance:
                type: number
                minimum: 0
                maximum: 1
            required:
              - correctness
              - faithfulness
              - context_relevance

      # Persist each scored case so the notebook can query it later.
      - name: save
        type: elasticsearch.index
        with:
          index: "{{ consts.resultsIndex }}"
          document:
            qid: "{{ foreach.item._source.qid }}"
            question: "{{ foreach.item._source.question }}"
            ground_truth: "{{ foreach.item._source.answer }}"
            candidate: "{{ steps.agent_answer.output.content }}"
            correctness: "{{ steps.judge.output.content.correctness }}"
            faithfulness: "{{ steps.judge.output.content.faithfulness }}"
            context_relevance: "{{ steps.judge.output.content.context_relevance }}"
"""
```

Let's walk through the key parts:

* `consts`**:** Named constants for index names. This keeps the YAML clean and makes it easy to point the same pipeline at a different dataset.
* `load_cases`**:** An `elasticsearch.search` step that pulls all test cases from the judgement list.
* `eval_loop`**:** A `foreach` step that iterates over the search results. Each iteration runs the four nested steps:

  + `retrieve`**:** Runs a semantic search against the knowledge base using the question as the query.
  + `agent_answer`**:** An `ai.prompt` step that sends the question plus the top four retrieved passages to Haiku. The `connector-id` field references the Kibana AI Connector.
  + `judge`**:** Another `ai.prompt` step, this time hitting Sonnet. The `schema` block forces the model to return a typed JSON object with exactly the fields we need. No markdown fences, no regex, no parsing on read. The `minimum` and `maximum` constraints keep scores in the 0–1 range.
  + `save`**:** An [`elasticsearch.index`](https://www.elastic.co/docs/explore-analyze/workflows/steps/elasticsearch) step that writes each scored case to the results index. Because the judge output is already parsed JSON (thanks to `schema`), we can reference individual fields directly: `{{ steps.judge.output.content.correctness }}`.

## Upload and run the workflow

Elastic 9.4 ships a REST API for workflows. We use three endpoints:

* `POST /api/workflows` to create the workflow from YAML.
* `POST /api/workflows/{id}/run` to start an execution.
* `GET /api/workflows/executions/{id}` to poll until it finishes.

With 35 test cases, the workflow takes a few minutes to complete. Each iteration involves a semantic search, a large language model (LLM) call for the answer, another LLM call for the judge, and an index operation.

## How to read and interpret RAG evaluation results

Each scored case is already a document in the `eval-results` index with typed score fields. No parsing needed: We query the index and compute the mean for each metric.

### **Aggregated RAG evaluation scores across 35 test cases**

The bar chart below shows the mean score for each metric across all 35 test cases (Haiku as answering model):

![Bar chart titled “Mean judge scores (Anthropic Claude Haiku 4.5 as answering model)” showing three vertical bars for correctness (0.74, blue), faithfulness (0.90, green), and context relevance (0.86, orange), with the y‑axis labeled “Score (0‑1).”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8fc304a29d91496f/6a55018a38d6ffd49da791d2/fbd823c03f7c9f2a30a12c1e3d76c2a9347f8c7e-690x390.png)

In this evaluation run using Claude Haiku 4.5 as the answering model, the results were::

* **correctness: 0.74:** It got roughly 7 out of 10 questions right. For multi-hop Wikipedia questions, this is reasonable but leaves room for improvement.
* **faithfulness: 0.90:** When Haiku does answer, it stays grounded in the passages. Hallucination is not a major problem here.
* **context\_relevance: 0.86:** The semantic retrieval brought relevant passages most of the time, though some multi-hop questions needed passages that weren’t in the top four.

The gap between faithfulness (0.90) and correctness (0.74) tells us the model is not making things up, it just misses the right answer on harder questions. That’s a retrieval or reasoning problem, not a hallucination problem. Increasing the number of retrieved passages or switching to a stronger model for the hardest cases are both viable paths forward.

## What the RAG evaluation results mean for production

We built a complete evaluation pipeline that runs entirely inside Elasticsearch. The knowledge base, the judgement list, the workflow execution, and the scored results all live in the same system.

The workflow YAML is version-controllable, replayable, and can be triggered via the API. If you update your knowledge base or change your answering model, you rerun the same pipeline and compare the new scores against the old ones.

For this specific dataset, the numbers suggest that Haiku is faithful but not always correct on multi-hop questions. Whether that’s good enough depends on your use case, with your own data. The point of the eval pipeline is to give you the data to make that decision with confidence, instead of guessing.

## Next steps

From here, you can:

* **Expand the judgement list** with domain-specific questions that reflect your actual production traffic.
* **Swap the answering model** to compare how different models perform on the same test set.
* **Schedule the workflow** to run automatically after new documents are indexed.
* **Build a Kibana dashboard** over the `eval-results` index to track quality over time.

Related articles:

* [How to Build AI Agentic Workflows with Elasticsearch](https://www.elastic.co/search-labs/blog/ai-agentic-workflows-elastic-ai-agent-builder)
* [Agent Builder & Workflows: Create AI agents that perform actions](https://www.elastic.co/search-labs/blog/agent-builder-one-workflow)
* [RAG retrieval evaluation & optimization with DeepEva](https://www.elastic.co/search-labs/blog/rag-retrieval-elasticsearch-deepeval)

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blte3979255ddfc7f45/6a17e25ffaa913812f93c7cb/92c517a2e7b36122a18feee317a0215981b62b6b-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Operations](/search-labs/blog/category/operations)

### Your agents have been keeping receipts: turning Elastic Agent Builder's built-in OTel traces into token cost dashboards in Kibana

July 28, 2026|[Meghan Murphy](/search-labs/author/meghan-murphy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltda47d75430c4fa7c/6a17f5cae3179149242d5963/d5d04bbcfc3925f48f3487ea4c7e0dd2205316d0-720x420.jpg)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Integrations](/search-labs/blog/category/integrations)

### One prompt, a complete workflow: Elastic's AI agent writes your automation for you

July 28, 2026|[Tinsae Erkailo](/search-labs/author/tinsae-erkailo)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3bad6b045392e641/6a170f43a29299c189d010cc/80907fd072e72d6ec902470b449c9f337957a0d7-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)

### Managing agentic memory with Elasticsearch

January 16, 2026|[Someshwaran Mohankumar](/search-labs/author/someshwaran-mohankumar)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter