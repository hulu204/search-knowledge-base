---
title: 'Query Expansion with LLMs: Searching Better by Saying More'
company: Jina
tag: 搜索
date: 2025-02-18
url: https://jina.ai/news/query-expansion-with-llms-searching-better-by-saying-more/
account: 
origin: harvest2-202607
---
Query expansion has long been a go-to technique for supercharging search systems, though it's taken a backseat since semantic embeddings came onto the scene. While some might think it as outdated in our current landscape of RAG and agentic search, don't count it out just yet. In this deep dive, we'll explore how combining automatic query expansion with [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) and LLMs can level up your search game and deliver results that really hit the mark.

## [*tag*](#what-is-query-expansion "What is Query Expansion?")What is Query Expansion?

Query expansion was developed for search systems that judge relevance by matching words from queries with documents that contain them, like [tf-idf](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) or other “sparse vector” schemes. That has some obvious limitations. Variant forms of words interfere with matching, like “ran” and “running”, or “optimise” vs. “optimize.” Language-aware preprocessing can mitigate some of these problems, but not all of them. Technical terms, synonyms, and related words are much harder to address. For example, a query for medical research about “coronavirus” will not automatically identify documents that talk about “COVID” or “SARS-CoV-2”, even though those would be very good matches.

Query expansion was invented as a solution.

The idea is to add additional words and phrases to queries to increase the likelihood of identifying good matches. This way, a query for “coronavirus” might have the terms “COVID” and “SARS-CoV-2” added to it. This can dramatically improve search performance.

![Flowchart outlining a search engine's query expansion process, featuring a user's coronavirus query and related terms.](https://cms.jina.ai/content/images/2025/02/QueryExpansion1.png)

Figure 1: Query Expansion Flowchart with Thesaurus

It’s not easy to decide what terms should be added to a query, and there’s been a lot of work on how to identify good terms and how to weight them for tf-idf-style retrieval. Common approaches include:

* Using a human-curated thesaurus.
* Data-mining large text corpora for related words.
* Identifying other terms used in similar queries taken from a query log.
* Learning what words and phrases make good query expansions [from user feedback](https://en.wikipedia.org/wiki/Rocchio_algorithm).

However, semantic embedding models are supposed to eliminate the need for query expansion. Good text embeddings for “coronavirus”, "COVID" and “SARS-CoV-2” should be very close to each other in the embedding vector space. They should naturally match without any augmentation.

But, while this should be true in theory, real embeddings made by real models often fall short. Words in embeddings may be ambiguous and adding words to a query can nudge it towards better matches if you use the right words. For example, an embedding for “skin rash” might identify documents about “behaving rashly” and “skin creme” while missing a medical journal article that talks about “dermatitis.” Adding relevant terms will likely nudge the embedding away from unrelated matches toward better ones.

## [*tag*](#llm-query-expansion "LLM Query Expansion")LLM Query Expansion

Instead of using a thesaurus or doing lexical data mining, we looked at using an LLM to do query expansion. LLMs have some important potential advantages:

* **Broad lexical knowledge**: Because they’re trained on large, diverse datasets, there is less concern about selecting an appropriate thesaurus or getting the right data.
* **Capacity for judgment**: Not all proposed expansion terms are necessarily appropriate to a specific query. LLMs may not make perfect judgments about topicality, but the alternatives can’t really make judgments at all.
* **Flexibility**: You can adjust your prompt to the needs of the retrieval task, while other approaches are rigid and may require a lot of work to adapt to new domains or data sources.

Once the LLM has proposed a list of terms, query expansion for embeddings operates the same way as traditional query expansion schemes: We add terms to the query text and then use an embedding model to create a query embedding vector.

![Flowchart detailing the query expansion process for coronavirus surface stability, with labeled sections and connecting arrow](https://cms.jina.ai/content/images/2025/02/QueryExpansion2.png)

Figure 2: Query Expansion of Embeddings with an LLM

To make this work, you need:

* Access to an LLM.
* A prompt template to solicit expansion terms from the LLM.
* A text embedding model.

## [*tag*](#trying-it-out "Trying It Out")Trying It Out

We’ve done some experiments to see if this approach adds value to text information retrieval. Our tests used:

* One LLM: [Gemini 2.0 Flash](https://deepmind.google/technologies/gemini/flash/) from Google.
* Two embedding models to see if LLM query expansion generalizes across models: [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) and [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2).
* A subset of the [BEIR benchmarks](https://github.com/beir-cellar/beir) for information retrieval.

We performed our experiments under two prompting conditions:

* Using a general prompt template to solicit expansion terms.
* Using task-specific prompt templates.

Finally, we wrote our prompts to solicit different numbers of terms to add: 100, 150, and 250.

Our code and results are [available on GitHub](https://github.com/jina-ai/llm-query-expansion/) for reproduction.

[GitHub - jina-ai/llm-query-expansion: Query Expension for Better Query Embedding using LLMs

Query Expension for Better Query Embedding using LLMs - jina-ai/llm-query-expansion

![](https://cms.jina.ai/content/images/icon/pinned-octocat-093da3e6fa40-1.svg)GitHubjina-ai

![](https://cms.jina.ai/content/images/thumbnail/llm-query-expansion)](https://github.com/jina-ai/llm-query-expansion/)

## [*tag*](#results "Results")Results

### [*tag*](#using-a-general-prompt "Using a General Prompt")Using a General Prompt

After some trial and error, we found that the following prompt worked well enough with Gemini 2.0 Flash:

```
Please provide additional search keywords and phrases for 
each of the key aspects of the following queries that make 
it easier to find the relevant documents (about {size} words 
per query):
{query}

Please respond in the following JSON schema:
Expansion = {"qid": str, "additional_info": str}
Return: list [Expansion]
```

This prompt enables us to batch our queries in bundles of 20-50, giving an ID to each one, and getting back a JSON string that connects each query to a list of expansion terms. If you use a different LLM, you may have to experiment to find a prompt that works for it.

We applied this setup with [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) using the [asymmetric retrieval adapter](https://jina.ai/news/jina-embeddings-v3-a-frontier-multilingual-embedding-model). Using this approach, queries and documents are encoded differently — using the same model but different LoRA extensions — to optimize the resulting embeddings for information retrieval.

Our results on various BEIR benchmarks are in the table below. Scores are nDCG@10 ([normalized Discounted Cumulative Gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) on the top ten items retrieved).

| Benchmark | No Expansion | 100 terms | 150 terms | 250 terms |
| --- | --- | --- | --- | --- |
| **SciFact** (Fact Checking Task) | 72.74 | 73.39 | 74.16 | **74.33** |
| **TRECCOVID** (Medical Retrieval Task) | 77.55 | 76.74 | 77.12 | **79.28** |
| **FiQA** (Financial Option Retrieval) | 47.34 | **47.76** | 46.03 | 47.34 |
| **NFCorpus** (Medical Information Retrieval) | 36.46 | **40.62** | 39.63 | 39.20 |
| **Touche2020** (Argument Retrieval Task) | 26.24 | 26.91 | 27.15 | **27.54** |

We see here that query expansion has in almost all cases resulted in improved retrieval.

To test the robustness of this approach, we repeated the same tests with `all-MiniLM-L6-v2`, a much smaller model that produces smaller embedding vectors.

[sentence-transformers/all-MiniLM-L6-v2 · Hugging Face

We’re on a journey to advance and democratize artificial intelligence through open source and open science.

![](https://cms.jina.ai/content/images/icon/favicon-29.ico)

![](https://cms.jina.ai/content/images/thumbnail/all-MiniLM-L6-v2.png)](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

The results are in the table below:

| Benchmark | No Expansion | 100 terms | 150 terms | 250 terms |
| --- | --- | --- | --- | --- |
| **SciFact** (Fact Checking Task) | 64.51 | **68.72** | 66.27 | 68.50 |
| **TRECCOVID** (Medical Retrieval Task) | 47.25 | 67.90 | **70.18** | 69.60 |
| **FiQA** (Financial Option Retrieval) | **36.87** | 33.96 | 32.60 | 31.84 |
| **NFCorpus** (Medical Information Retrieval) | 31.59 | **33.76** | 33.76 | 33.35 |
| **Touche2020** (Argument Retrieval Task) | 16.90 | **25.31** | 23.52 | 23.23 |

We see here an even larger improvement in retrieval scores. Overall, the smaller model profited more from query expansion. The average improvement over all tasks is summarized in the table below:

| Model | 100 terms | 150 terms | 250 terms |
| --- | --- | --- | --- |
| [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) | +1.02 | +0.75 | **+1.48** |
| `all-MiniLM-L6-v2` | **+6.51** | +5.84 | +5.88 |

The large difference in net improvement between the two models is likely due to `all-MiniLM-L6-v2` starting from a lower level of performance. The query embeddings produced by [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) in asymmetric retrieval mode are better able to capture key semantic relationships, and thus there is less room for query expansion to add information. But this result shows how much query expansion can improve the performance of more compact models that may be preferable in some use cases to large models.

Nonetheless, query expansion brought meaningful improvement to retrieval even for high-performance models like [jina-embeddings-v3](/?sui&model=jina-embeddings-v3), but this result is not perfectly consistent across all tasks and conditions.

For [jina-embeddings-v3](/?sui&model=jina-embeddings-v3), adding more than 100 terms to a query was counterproductive for the FiQA and NFCorpus benchmarks. We can’t say that more terms are always better, but the results on the other benchmarks indicate that more terms are at least sometimes better.

For `all-MiniLM-L6-v2`, adding more than 150 terms was always counterproductive, and on three tests, adding more than 100 didn’t improve scores. On one test (FiQA) adding even 100 terms produced significantly lower results. We believe this is because [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) does a better job of capturing semantic information in long query texts.

Both models showed less response to query expansion on the FiQA and NFCorpus benchmarks.

## [*tag*](#using-task-specific-prompting "Using Task-Specific Prompting")Using Task-Specific Prompting

The pattern of results reported above suggests that while query expansion is helpful, using LLMs risks adding unhelpful query terms that reduce performance. This might be caused by the generic nature of the prompt.

We took two benchmarks — SciFact and FiQA — and created more domain-specific prompts, like the one below:

```
Please provide additional search keywords and phrases for 
each of the key aspects of the following queries that make
it easier to find the relevant documents scientific document 
that supports or rejects the scientific fact in the query 
field (about {size} words per query):
{query}
Please respond in the following JSON schema:
Expansion = {"qid": str, "additional_info": str}
Return: list [Expansion]
```

This approach improved retrieval performance almost across the board:

| Benchmark | Model | No Expansion | 100 terms | 150 terms | 250 terms |
| --- | --- | --- | --- | --- | --- |
| SciFact | [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) | 72.74 | **75.85 (+2.46)** | 75.07 (+0.91) | 75.13 (+0.80) |
| SciFact | `all-MiniLM-L6-v2` | 64.51 | **69.12 (+0.40)** | 68.10 (+1.83) | 67.83 (-0.67) |
| FiQA | [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) | 47.34 | 47.77 (+0.01) | **48.20 (+1.99)** | 47.75 (+0.41) |
| FiQA | `all-MiniLM-L6-v2` | **36.87** | 34.71 (+0.75) | 34.68 (+2.08) | 34.50 (+2.66) |

Scores improved under all conditions except adding 250 terms to SciFact queries with `all-MiniLM-L6-v2`. Furthermore, this improvement was not enough to make `all-MiniLM-L6-v2` beat its own baseline on FiQA.

For [jina-embeddings-v3](/?sui&model=jina-embeddings-v3), we see that the best results came with 100 or 150 added terms. Adding 250 terms was counterproductive. This supports our intuition that you can add too many terms to your query, especially if their meaning begins to drift from the target.

## [*tag*](#key-considerations-in-query-expansion "Key Considerations in Query Expansion")Key Considerations in Query Expansion

Query expansion clearly can bring gains to embeddings-based search, but comes with some caveats:

### [*tag*](#expense "Expense")Expense

Interacting with an LLM adds latency and computational costs to information retrieval, and may add actual costs if you use a commercial LLM. The moderate improvement it brings may not justify the expense.

### [*tag*](#prompt-engineering "Prompt Engineering")Prompt Engineering

Designing good prompt templates is an empirical and experimental art. We make no representation that the ones we used for this work are optimal or portable to other LLMs. Our experiments with task-specific prompting show that changing your prompts can have very significant effects on the quality of the outcome. Results also vary considerably between domains.

These uncertainties add to the cost of development and undermine maintainability. Any change to the system — changing LLMs, embedding models, or information domain — means rechecking and possibly reimplementing the entire process.

### [*tag*](#alternatives "Alternatives")Alternatives

We see here that query expansion added the greatest improvement to the embedding model with the poorest initial performance. Query expansion, at least in this experiment, was not able to close the performance gap between `all-MiniLM-L6-v2` and [jina-embeddings-v3](/?sui&model=jina-embeddings-v3), while [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) saw more modest improvements from query expansion.

Under the circumstances, a user of `all-MiniLM-L6-v2` would get better results at a lower cost by adopting [jina-embeddings-v3](/?sui&model=jina-embeddings-v3) rather than pursuing query expansion.

## [*tag*](#future-directions "Future Directions")Future Directions

We’ve shown here that query expansion can improve query embeddings, and that LLMs offer a simple and flexible means of getting good query expansion terms. But the relatively modest gains suggest more work to be done. We’re looking at a number of directions for future research:

* Testing the value of terminological enhancement in generating document embeddings.
* Looking at the possibilities for query enhancement in other AI search techniques like reranking.
* Comparing LLM-based query expansion to older and computationally less expensive sources of terms, like a thesaurus.
* Training language models specifically to be better at query expansion and providing them with more domain-specific training.
* Limiting the number of terms added. 100 may be too many to start with.
* Finding ways to identify helpful and unhelpful expansion terms. Any fixed number we impose on query expansion is not going to be a perfect fit and if we could dynamically evaluate suggested terms and keep only the good ones, the result would likely be a lift in performance.

This is very preliminary research, and we’re optimistic that techniques like this will bring further improvements to Jina AI’s search foundation products.