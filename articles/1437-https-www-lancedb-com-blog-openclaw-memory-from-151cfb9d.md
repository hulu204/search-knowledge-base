---
title: 'https://www.lancedb.com/blog/openclaw-memory-from-zero-to-lancedb-pro'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/openclaw-memory-from-zero-to-lancedb-pro
account: 
origin: en-rss
---
# Memory for OpenClaw: From Zero to LanceDB Pro

[Prashanth Rao](/author/prashanth-rao)

•

March 26, 2026

•

[Engineering](/category/engineering)

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-001](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

OpenClaw agents are stateless by default. Every conversation starts from scratch — your agent has no idea what the user said yesterday, what preferences they’ve expressed, or what facts came up three sessions ago. For a coding assistant or a one-off task runner, that’s fine. But if you’re building something that acts more like a long-term collaborator — a personal assistant, a research partner, an advisor that knows your project history — statelessness is a dealbreaker.

OpenClaw solves this with [**memory plugins**](https://docs.openclaw.ai/tools/plugin#memory-plugins) : drop-in backends that persist and retrieve facts across sessions. The agent stores memories as it goes, and when a question comes up that depends on something from the past, the plugin surfaces the relevant chunks automatically. But memory plugins vary widely in how they retrieve. The default is a SQLite-backed index (**`memory-core`**), but in this post, we’ll show how using [**LanceDB**](https://github.com/lancedb/lancedb) can yield better results.

We’ll look at the results from three memory backends, measuring each one against a public memory benchmark dataset, and show exactly what changes between them. The results are summarized at a high level below:

| Backend | How It Retrieves | Accuracy | Avg Latency |
| --- | --- | --- | --- |
| `memory-core` | SQLite-backed index | 52% | 8.4s |
| `memory-lancedb` | Vector similarity search | 76% | 4.8s |
| `memory-lancedb-pro` | Vector search + cross-encoder reranking | 80% | 14.3s |

The results show a significant improvement in performance when moving from the default **`memory-core`** plugin to a LanceDB-backed one, but the reasons are more nuanced than just “vector search is better” — the way tools are called and the capabilities of the underlying plugin matter. Adding a reranker adds a small further quality boost, but the story is as much about the tradeoffs (latency, complexity, configuration) as it is about the accuracy numbers. By the end of this post, you’ll understand what each backend does under the hood, how to set it up, and which one fits your use case.

## Memory Plugins in OpenClaw

Each memory backend is a drop-in OpenClaw memory plugin. As a user, all you do is configure which one to use in the **`openclaw.json`** file. Then, start the gateway, and your agent’s memory tools route to that backend automatically.

### 1. memory-core

This is the built-in baseline that stores memories as markdown files in your workspace and indexes them into SQLite using two virtual tables: an [**FTS5**](https://www.sqlite.org/fts5.html) full-text search index for keyword matching, and a [**`sqlite-vec`**](https://github.com/asg017/sqlite-vec) vector index (**`vec0`**) for embedding similarity over OpenAI **`text-embedding-3-small`** vectors (1536 dimensions). Retrieval combines both signals, then uses a two-step tool flow: **`memory_search`** to find chunks, then **`memory_get`** to read them.

At search time, the gateway queries both indexes and merges the results, but the agent still makes two round trips and decides what to fetch. Although the flow is transparent (you can see exactly what was searched and what was read), putting retrieval decisions on the agent creates more room for error.

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-002](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-002.avif)

### 2. memory-lancedb

This plugin relies on vector search: it embeds memory chunks using OpenAI’s **`text-embedding-3-small`** and retrieves them by semantic similarity with [**LanceDB**](https://lancedb.github.io/lancedb/) , an embedded retrieval library that stores embeddings alongside text in Lance tables.

Using this plugin, you get one tool call (**`memory_recall`**) with one round trip. The agent asks a question and gets back the most relevant chunks. The plugin handles embedding the query, searching for vectors by semantic similarity and returning results, so the agent doesn’t need to make any tool-calling decisions.

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-003](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-003.avif)

### 3. memory-lancedb-pro

This is a more advanced plugin that includes vector search plus cross-encoder reranking. It generates a broad candidate pool via embeddings, then uses a cross-encoder model ( [**jina-reranker-v3**](https://jina.ai/models/jina-reranker-v3) ) to rerank candidates by how well each one actually answers the query.

From the agent’s perspective, this looks identical to memory-lancedb — the same **`memory_recall`** call, the same response shape. The reranking stage happens entirely inside the plugin. The difference is that the plugin casts a wider net (40 candidates instead of a small top-k), then uses the cross-encoder to rerank them by true relevance before returning the final results.

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-004](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-004.avif)

## Measuring Memory: The LOCOMO Benchmark

When using a memory plugin, how do you know if your memory is actually retrieving the right thing? To gain confidence, you need a benchmark of questions with known answers that test whether the system can recover specific facts from stored conversations.

We use [**LOCOMO**](https://github.com/snap-research/locomo) , a conversational long-term memory benchmark from Snap Research. Each sample is a multi-session dialogue between two people, and the evaluation questions ask for facts that require more than just keyword matching to answer.

Here’s a concrete example. In one LOCOMO dialogue, session 1 is timestamped **`1:56 pm on 8 May, 2023`**, and one of the turns says:

> "I went to an LGBTQ support group yesterday and it was so powerful."

The benchmark question is: *“When did Caroline go to the LGBTQ support group?”* The gold answer is **7 May 2023**.

Notice what the memory system has to do: retrieve the right turn, pay attention to the relative word “yesterday,” combine it with the session timestamp, and produce the correct date. LOCOMO is full of this kind of light temporal reasoning, plus coreference resolution (who is “she”?), inference (what can you conclude from these facts?), and identity questions (what are this person’s preferences?).

The dataset organizes questions into four categories:

| Category | What It Tests | Example |
| --- | --- | --- |
| Identity/Preference | Remembering who someone is or what they like | "What is Alex's favorite cuisine?" |
| Temporal | Date math and time references | "When did Caroline attend the support group?" |
| Inference | Drawing conclusions from stored facts | "Why might Jordan be stressed?" |
| Coreferential | Resolving pronouns and references | "What did she decide about the job?" |

### How We Judge Answers

An LLM grades each answer as CORRECT or WRONG using a generous rubric. The judge is told the following as part of its prompt:

> *Be generous in grading. If the generated answer clearly refers to the same fact, count it as CORRECT. For dates and times, count format differences or relative wording as CORRECT if they refer to the same date or time period.*

This matters because many correct answers are naturally variable. “7 May 2023” and “last Friday” can both be right if they refer to the same date relative to that mentioned in the context. The benchmark measures factual recovery, not exact string matches.

The LLM judge returns structured JSON with a verdict and one sentence of reasoning, making it easy to audit individual decisions after a run.

## Apples-to-Apples Setup

For the comparison to be meaningful, every backend must see the same corpus. This is the single most important design decision in the benchmark.

Here’s how it works:

1. **memory-core** chunks each LOCOMO session into markdown and indexes the chunks into SQLite. Those chunk texts become the canonical unit.
2. **memory-lancedb** reads those exact chunk texts and their embeddings from the SQLite index, then writes them into a LanceDB table.
3. **memory-lancedb-pro** migrates from the prebuilt LanceDB store, preserving the same chunks and vectors.

To keep the comparison fair and ensure every backend works from the same chunks, no summarization or rewriting happens during ingest. Every backend retrieves against the actual stored chunk text. This means differences in benchmark scores are attributable to retrieval quality, not to differences in what was stored.

### Setting Up the Benchmark

The benchmark harness lives in [**this repo**](https://github.com/lancedb/locomo-eval) . The setup is straightforward:

Each backend has a setup script that configures OpenClaw with the right plugin and settings. You run the setup script, start the gateway, and then run the benchmark:

The setup scripts are all available [**here**](https://github.com/lancedb/locomo-eval) . They generate an **`openclaw.json`** config file that tells the gateway which memory plugin to load, where to store data, and what retrieval settings to use. You don’t need to edit this file manually — the scripts handle everything.

## Backend 1: memory-core (Baseline)

**`memory-core`** is OpenClaw’s built-in memory. It stores memories as markdown files in your workspace and indexes both the text and embeddings into a SQLite database. When your agent needs to recall something, it uses two tools: **`memory_search`** to find relevant chunks, then **`memory_get`** to read them.

The setup script configures a minimal OpenClaw environment:

**Strengths:** It’s simple, transparent, and local. The indexed markdown files are human-readable. There are no external dependencies beyond SQLite. For beginners, this is the easiest way to add memory to an OpenClaw agent.

**Limitations:** The two-step retrieval flow (search, then get) is harder for the agent to use reliably than a single recall tool. As memories accumulate, retrieval speed from the SQLite index can also suffer compared to a purpose-built vector database.

The benchmark with memory-core is run as follows:

The LLM used for the agent responses and the judge is kept constant: **`openai/gpt-4.1-mini`** for all runs.

**Result: 52/100 correct (52%).** The baseline establishes a floor. About half the questions are answered correctly — the other half are missed because the right chunk either wasn’t retrieved or the agent couldn’t compose the answer from what it found.

## Backend 2: memory-lancedb (Vector Search)

[**memory-lancedb**](https://docs.openclaw.ai/tools/plugin#core-shipped-with-openclaw) is an alternate core memory plugin that ships with OpenClaw, and it uses LanceDB as the dedicated storage layer for memories. The same chunk embeddings that memory-core stores in SQLite are now stored in LanceDB’s columnar Lance tables. Note that the plugin does not automatically create a vector index, because Lance’s nearest-neighbor vector search is very fast for even hundreds of thousands (or even millions) of vectors on a local machine.

The key config differences in OpenClaw are as follows:

Two settings are important for benchmarking:

* **`autoCapture: false`** — prevents the plugin from automatically storing new memories during the benchmark run.
* **`autoRecall: false`** — prevents the plugin from automatically injecting memories into every conversation turn. This is necessary for a fair comparison because the two LanceDB plugins inject recalled context differently. Leaving it on would muddy the comparison before retrieval quality even enters the picture.

The agent interface is also simpler. Instead of two tools (**`memory_search`** + **`memory_get`**), the LanceDB plugin exposes a single **`memory_recall`** tool that returns relevant chunks in one call. Fewer tool calls means fewer opportunities for the agent to go wrong.

This setup is run as follows:

**Result: 76/100 correct (76%).** This is the biggest single improvement in the progression — a 24-point jump over the baseline. Since the vector retrieval doesn’t rely on a vector index, the accuracy gain is primarily driven by two factors: the simpler single-tool interface (**`memory_recall`** instead of **`memory_search`** + **`memory_get`**) reduces agent errors, and the pure-vector search avoids the FTS keyword signal that can dilute results with thematically related but factually wrong chunks.

## Backend 3: memory-lancedb-pro (Vector Search + Reranking)

The [**memory-lancedb-pro**](https://github.com/CortexReach/memory-lancedb-pro) plugin adds several capabilities beyond vanilla vector search: it comes with built-in hybrid retrieval (vector search + BM25), noise filtering, recency scoring, and metadata conventions. But the capability we care about most for improving retrieval quality is **cross-encoder reranking**.

### What Is Cross-Encoder Reranking?

Standard embedding-based retrieval works in two separate steps: embed the query, embed each document, then compare the vectors. This is fast because all the embeddings can be precomputed, but it has a limitation — the query and document never “see” each other during scoring. Two chunks that are semantically close but factually different can end up with nearly identical similarity scores.

A cross-encoder fixes this. It takes the query and a candidate document *together* as input and scores them in a single forward pass. Because the model can attend to the specific relationship between the query and the document, it’s much better at distinguishing “this is about the same topic” from “this is the specific fact being asked about.”

The tradeoff is speed. A cross-encoder can’t precompute anything — it has to score every candidate pair at query time. That’s why it’s used as a **reranker** rather than a first-stage retriever: vector search quickly narrows thousands of memories down to a manageable candidate pool, then the cross-encoder reranks that smaller set by true relevance.

The Pro plugin uses [**jina-reranker-v3**](https://jina.ai/models/jina-reranker-v3) as its default cross-encoder. After the initial vector search returns candidates, each candidate is scored against the query by the Jina model, and the final ranking blends the reranker score with the original retrieval score at a 60/40 ratio (60% reranker, 40% original).

### Tuned Retrieval Profile

To get better results, the Pro plugin’s retrieval settings needed to be configured for the task. The setup script exposes all the knobs at the top of the file, making it easy to run experiments:

Here’s what each setting does and why it’s set this way:

**`vectorWeight=1.0 / bm25Weight=0.0`**: BM25 (keyword matching) is disabled entirely. This might seem counterintuitive for a “hybrid” retriever, but on LOCOMO’s short factual queries, keyword overlap was actively harmful. Many queries share common words with multiple memories. BM25 would pull in thematically related but factually wrong chunks, diluting the candidate pool. Pure vector search produces a cleaner set of candidates for the reranker to work with.

**`candidatePoolSize=40`**: A broad initial pool. Since the reranker will rerank everything, we want to cast a wide net at the vector search stage. 40 candidates gives the cross-encoder enough material to find the right chunk even if it wasn’t in the top 5 by embedding similarity alone.

**`minScore=0.35 / hardMinScore=0.30`**: Score floors that filter out clearly irrelevant results. The **`hardMinScore`** is set lower than it might otherwise be (0.30 vs 0.40) to let borderline candidates survive into the reranking stage. A chunk that scores 0.32 by vector similarity might be the correct answer — the reranker can figure that out, but only if the chunk makes it past the filter.

**`rerank=jina`**: Enables the Jina cross-encoder pass. This is the setting that actually activates reranking. You’ll need a **`JINA_API_KEY`** in your **`.env`** file.

**`filterNoise=true`**: Removes low-quality results after reranking. Even with a reranker, some candidates are noise.

**Lifecycle scoring neutralized**: **`recencyWeight`**, **`timeDecayHalfLifeDays`**, **`reinforcementFactor`**, and **`maxHalfLifeMultiplier`** are all set to zero. These features boost recent or frequently-accessed memories, which is useful for a real assistant but meaningless for a static benchmark where all memories were ingested at the same time.

To enable Jina reranking, add the API key to your **`.env`**:

The following commands are then run:

**Result: 80/100 correct (80%).** We can see a 4-point improvement over vanilla LanceDB. The cross-encoder reranker is doing what it’s designed to do — taking a broad set of semantically similar candidates and identifying which one actually answers the question.

## Results

Each backend was used to run the benchmark over the first 100 rows of the dataset. The following table summarizes the results.

| Backend | Rows | Correct | Wrong | Completion Rate | Avg latency (s) |
| --- | --- | --- | --- | --- | --- |
| `memory-core` | 100 | 52 | 48 | 0.54 | 8.4 |
| `memory-lancedb` | 100 | 76 | 24 | 0.76 | 4.8 |
| `memory-lancedb-pro` | 100 | 80 | 20 | 0.80 | 14.3 |

The progression tells a clear story.

**The biggest jump is from SQLite-backed retrieval to a dedicated vector store** (52% → 76%). If you’re using memory-core today and want better retrieval, switching to memory-lancedb is the simplest high-impact change you can make. It’s also the faster backend, thanks to LanceDB’s native vector search capabilities and the lack of reranking overhead.

**Cross-encoder reranking adds a further quality boost** (76% → 80%). The improvement is smaller but meaningful, especially for queries where multiple memories are semantically close. The tradeoff is latency: each query now includes an API call to Jina’s reranker, which significantly increases the response time compared to vanilla LanceDB. In some cases, higher latency is tolerable for better retrieval quality, so this tradeoff may be worth it for some users.

### Running at Scale

For larger benchmark runs, the gateway serializes requests through a single-lane queue, so in-process concurrency doesn’t help. The **`run_parallel.py`** script solves this by splitting rows across 4 subprocesses:

This produces the same output format as a single-process run but finishes significantly faster.

## Key Takeaways

**Using LanceDB is simple and produces higher quality results than the baseline.** The jump from SQLite-backed retrieval to LanceDB is the single biggest improvement. If you’re adding memory to an OpenClaw agent for the first time, consider starting with **`memory-lancedb`**.

**Cross-encoder reranking helps when precision matters.** If your use case involves many semantically similar memories — think a long-running assistant that has discussed the same topics multiple times — switching to the **`memory-lancedb-pro`** plugin that includes a reranker can distinguish between “related to the topic” and “the specific fact being asked about.” However, this can significantly increase latency, so the tradeoff is worth keeping in mind.

**Precision beats breadth for factual queries.** On short, specific questions, more retrieval features can hurt. BM25 keyword matching, recency boosts, and other scoring layers can flood the candidate pool with plausible but wrong results. Sometimes the best tuning is turning things off.

**A vector index isn’t strictly necessary.** Neither LanceDB plugin in this benchmark creates a vector index — brute-force search over the Lance columnar format is fast enough. Systems that bolt vector search onto an existing store (like SQLite via **`sqlite-vec`**) often force users to reason about index types, extensions, and tuning parameters right upfront. LanceDB treats embeddings and complex multimodal data as first-class citizens in a format purpose-built for fast random access, producing low-latency vector search results on millions of vectors even on a local machine.

## What’s Next

There are several areas worth exploring beyond what this benchmark covers:

* **Full-dataset runs.** The current results are based on 100 QA pairs. Running all 1,540 LOCOMO questions would give more definitive numbers and reveal performance patterns across question categories.
* **Configurable reranker blending.** The Pro plugin currently hardcodes the reranker blend at 60% reranker / 40% original score. Making this configurable could yield further gains.
* **Interactive memory exploration.** A **`lancedb-query`** skill that lets an agent probe the LanceDB store directly would make memory-backed agents easier to debug and more useful for complex retrieval scenarios.
* **Smart format evaluation.** The Pro plugin supports richer memory representations (L0/L1/L2 text layers — short abstract, overview, and full content). We deliberately disabled this for the benchmark to keep the comparison fair, but understanding how much those richer metadata layers help in real-world usage is an interesting open question.

## Conclusions

The results here speak for themselves: a single memory plugin change — moving from SQLite row-based lookup to vector retrieval in LanceDB — delivers a significant accuracy gain, and layering a cross-encoder reranker on top pushes it further still. The best part is that none of this requires you to operate infrastructure. LanceDB runs embedded, right alongside your agent, with zero servers to manage.

**Try it yourself.** Install **`memory-lancedb`** in your OpenClaw agent and run a few conversations. Depending on the kinds of memories in your data, you’ll notice the difference in retrieval quality immediately — especially on questions that require recalling specific facts from long conversation histories. If you need even sharper recall, enable Jina reranking with **`memory-lancedb-pro`** and compare the results side by side.

**Reproduce and extend our benchmark.** The full evaluation harness, including the LOCOMO dataset, ingestion scripts, runner, and LLM judge, is open source in [**this repo**](https://github.com/lancedb/locomo-eval) . Fork it, swap in your own memory backend, tune the knobs, and see where you land. If you find a configuration that does better than your baseline, we’d love to hear about it!

**Dive deeper into LanceDB.** If this post is your first encounter with embedded vector search, the [**LanceDB documentation**](https://docs.lancedb.com/) is the best next step. Understanding how Lance tables store embeddings alongside metadata, how vector indexing works at scale, and how to write custom rerankers will give you the foundation to push these results even further — or to build entirely new retrieval patterns that go beyond what the current plugins offer.

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-005](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-005.avif)

[Prashanth Rao](/author/prashanth-rao)

AI Engineer @ LanceDB

[GitHub](https://github.com/prrao87)[Linkedin](https://www.linkedin.com/in/prrao87/)[Twitter](https://x.com/tech_optimist)

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-006](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-006.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-007](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-007.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d-fig-008](../images/1437-https-www-lancedb-com-blog-openclaw-memory-from-151cfb9d/figure-008.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb