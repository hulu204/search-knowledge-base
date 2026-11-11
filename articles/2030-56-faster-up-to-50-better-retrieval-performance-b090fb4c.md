---
title: "56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker"
company: Elastic
tag: 排序
date: 2026-07-27
url: https://www.elastic.co/search-labs/blog/jina-reranker-35-legal-medical-structured-data
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

Jina Reranker 3.5 beats v3 by 50%+ on case law, closes the gap with models 7x its size on legal, medical, and financial benchmarks, and beats them outright on structured data. It's a drop-in replacement for v3, with no API changes.

July 27, 2026

[Felix Wang](/search-labs/author/felix-wang)[Scott Martens](/search-labs/author/scott-martens)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

`jina-reranker-v3.5` is a 600 million parameter reranker that delivers major gains over its predecessor, [`jina-reranker-v3`](https://jina.ai/models/jina-reranker-v3), on legal retrieval, and closes most of the gap to models seven times its size on legal, medical, and financial reranking. On long documents, it runs up to 56% faster than `jina-reranker-v3` and scores over 50% higher on case law retrieval. It also beats Qwen3-Reranker-4B on the STaRK structured data benchmark."It’s a drop-in replacement for v3 users and requires no changes to the code that accesses the model.

## What’s a reranker and how does it work?

A *reranker* is an AI model used near the end of an information retrieval pipeline, after other modules have assembled a short list of candidate matches to a query. It’s trained to order the candidate list from best matching to least. Using a specialized model focused purely on ranking candidate matches can improve result quality dramatically.

Jina AI’s latest rerankers use a technique called *late interaction*, where queries and documents are encoded separately into lists of token embeddings that reflect each token’s semantics in context and then compared to each other.

This is an AI analog of lexical and grammatical disambiguation.

For example, consider the meaning of the word *match* in these two sentences:

* She looked for a match to light the candle.
* She looked for a match on Tinder.

The first sentence might be a match for queries about matchboxes; the second for queries about romance.

Transformer-based models do this kind of in-context disambiguation but bring much richer information into the token embeddings they produce. The word *match* might have a semantic embedding near to words like *fire* or *illumination* in the first sentence, while in the second, it might be closer to *smartphone* or *swipe*.

Late interaction rerankers generate these context-enriched token embeddings for both the query and the candidate documents and then compare them to produce sortable scores. They’re completely agnostic about how candidate match lists are created. The reranker works exactly the same when combined with lexical search schemes, like BM25, AI-driven semantic embeddings-based retrieval, or hybrid and federated search systems that may retrieve multiple candidate lists from different sources or using different algorithms. Of course, the results always depend on the quality of the candidates, so a reranker can’t fix bad first-stage retrieval, but it almost always improves whatever you’ve got.

`jina-reranker-v3.5` is a *listwise* reranker using the [*last-but-not-late*](https://jina.ai/news/jina-reranker-v3-0-6b-listwise-reranker-for-sota-multilingual-retrieval/#:~:text=query%2Ddocument%20interaction%20%22-,last%20but%20not%20late,-.%22%20It%27s%20%22last) technique developed for `jina-reranker-v3`. The query and a list of candidate matches are passed into the model together and processed in one pass, returning a numerical score for each candidate. This enables the model to use context information from the query and the full candidate list to make sense of the entire input, producing better results because of the richer information available to it.

`jina-reranker-v3` proved that listwise rerankers with last-but-not-late interaction can compete with the largest models on general reranking benchmarks. Only `jina-reranker-v3.5` and models with over four billion parameters beat it on [Massive Text Embedding Benchmark (MTEB) reranker tasks](https://mteb-leaderboard.hf.space/benchmark/MTEB(Multilingual%2C%20v2)). However, this approach places strict limits on candidate list sizes. The query and all candidate matches must fit in the input context window of the model.

## What problems does Jina Reranker v3.5 solve?

Despite having frontier-level performance overall, `jina-reranker-v3` has some notable performance gaps:

### Domain-specific text retrieval

`jina-reranker-v3` was trained on general text corpora and, as a result, it underperforms on important use cases, particularly:

* Legal texts, like case law and contract clauses.
* Medical literature, like clinical trials and patient records.
* Financial datasets and other texts full of important numbers.
* Computer programming and IT documentation.
* Product catalogs full of technical terminology and specifications.

### Structured data: Tables, JSON, and key-value records

Vast quantities of essential, real-world data is encoded in spreadsheets, tables, key-value lists, and structured records, like JSON data. However, rerankers trained purely for textual comparison, like `jina-reranker-v3`, perform poorly on this kind of data.

### Compute costs for long candidate lists

The self-attention architecture at the core of most text-processing AI models means that memory and compute requirements grow quadratically with the size of its input. This makes `jina-reranker-v3`, like other AI models, very computationally expensive to run with a full input context window. But, to make the most effective use of the model, we want to put as many match candidates as possible into its input. When it’s at its most useful, it’s also slower and more expensive to run.

We’ve developed `jina-reranker-v3.5` specifically to address these issues without reducing its performance on general purpose text retrieval.

## What’s new in Jina Reranker v3.5?

`jina-reranker-v3.5` contains a modified self-attention mechanism that enhances performance, increases processing speed, and reduces the resources required at inference time to process a full input context window. We’ve also introduced a new three-stage self-distillation training process better suited to the sliding-window architecture of large input context models.

We’ve also curated and used training data focusing on the performance gaps we identified in `jina-reranker-v3`, including:

* Multilingual legal texts drawn from diverse international sources.
* Medical texts drawn largely from scientific literature and materials used for other AI projects, including a collection of Chinese medical question-answer pairs.
* Financial industry data, including investment-related question-answer pairs, regulations, and tables with numbers and associated texts.
* Structured data, especially from ecommerce sources and public corpora of tables.
* Expanded multilingual and cross-language texts.

For details on the data sources and technical innovations in `jina-reranker-v3.5`, see [our technical report](https://arxiv.org/abs/2607.18152).

## How Jina Reranker 3.5 performs on retrieval benchmarks

| Parameters | 597 million |
| --- | --- |
| Input modalities | Text only |
| Context window size | 131,072 tokens |
| Maximum number of candidate matches | No fixed limit, but all candidates and query must fit in the context window. |
| Languages | Training in 52 languages |

### General text reranking performance (BEIR and MIRACL)

`jina-reranker-v3.5` improves on `jina-reranker-v3`’s performance on general text reranking benchmarks. On the English-language [Benchmarking Information Retrieval (BEIR) benchmark](https://github.com/beir-cellar/beir), the average score has increased enough to surpass the frontier [Qwen3-Reranker-4B](https://huggingface.co/Qwen/Qwen3-Reranker-4B) and [0.6B](https://huggingface.co/Qwen/Qwen3-Reranker-0.6B) models and Mixedbread AI’s rerankers.

![Jina Reranker v3.5 BEIR benchmark results compared to Qwen3 and Mixedbread rerankers](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt2be1aaecef5d0cbd/6a6a33f854090e576714707e/52c2c0bd6269881eb4e2716a81442030dbf23458-2048x785.png)

We’ve also improved `jina-reranker-v3`’s multilingual reranking performance on the Multilingual Information Retrieval Across a Continuum of Languages (MIRACL) benchmark. Only the four billion parameter Qwen3 reranker regularly beats `jina-reranker-v3.5`’s score.

![Jina Reranker v3.5 MIRACL multilingual benchmark results across 18 languages](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta9d9b745a3c23efd/6a6a33f899442c66f1df1d8c/cc9ba1d219b1c77ef0840c86c038088a66b40f6d-2048x785.png)

### Legal, medical, and financial reranking

The [Retrieval Embedding Benchmark (RTEB) suite](https://huggingface.co/blog/rteb) consists of diverse domain-specific retrieval benchmarks. `jina-reranker-v3.5` outperforms `jina-reranker-v3` on all RTEB tasks related to law, medicine, and finance. Only the large Qwen3 reranker, at almost seven times as many parameters, has better average performance in those three domains.

![Jina Reranker v3.5 RTEB domain-specific benchmark results for legal, medical and financial retrieval](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6024d5c8ac1355ac/6a6a33f9b62af41d832635d8/1426abb0397e0b9d7c8115334ca5c4f899fa8fb6-2048x693.png)

The new model shows particularly strong improvements for legal data, beating `jina-reranker-v3`’s score by over 50% on case law retrieval tasks.

| Task | Reranker v3 | Reranker v3.5 | Improvement v3 to v3.5 |
| --- | --- | --- | --- |
| AILA-Case | 20.82 | 32.55 | +11.73 (56%) |
| AILA-Statute | 32.15 | 46.16 | +14.01 (44%) |
| LegalQuAD | 81.84 | 83.09 | +1.25 (1.5%) |
| LegalSum | 69.64 | 70.99 | +1.33 (1.9%) |

### Structured data reranking (Struct-IR and STaRK benchmarks)

We evaluated `jina-reranker-v3.5`'s structured data reranking on two benchmarks: [Struct-IR](https://neurips.cc/virtual/2025/loc/mexico-city/poster/121702) and [STaRK](https://stark.stanford.edu/). Both benchmarks contain AI-generated JSON text data covering a variety of applications, including product records, scientific papers, and biomedical knowledge bases.

![Jina Reranker v3.5 structured data benchmark results on Struct-IR and STaRK](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1deca80ed81995d5/6a6a33f79b96f21e21baf2be/b847be39e6387c4d4eaf754c5d758fc59fad4349-2048x717.png)

`jina-reranker-v3.5` improves substantially on `jina-reranker-v3`’s score on the Struct-IR benchmark, once again only exceeded by Qwen3-Reranker-4B. On the STaRK benchmark, `jina-reranker-v3.5` beats all the other models we tested, of any size.

### Inference speed: Latency benchmarks for short and long documents

The longer the candidate documents get, the more significant the architectural improvements we’ve brought to `jina-reranker-v3.5` are. To verify this, we used two retrieval datasets distinguished by large differences in the average document length:

| Dataset | Avg. doc length | jina-reranker-v3 | jina-reranker-v3.5 | Speedup |
| --- | --- | --- | --- | --- |
| BEIR Natural Questions | 145.5 tokens | 371.1 ms | 305.3 ms | 22% |
| RTEB AILAcasedocs | 1,904.0 tokens | 16,064.9 ms | 10,290.9 ms | 56% |

`jina-reranker-v3.5` is significantly faster in both cases. On the Natural Questions benchmark, there’s a 22% speedup compared to `jina-reranker-v3` with average request latency falling from 371.1 ms to 305.3 ms. Each query from the AILAcasedocs benchmark is much larger (more than 10 times larger on average) so it naturally takes longer to rerank on average: 16,064.9 ms for `jina-reranker-v3` and 10,290.9 ms for `jina-reranker-v3.5`. This represents a 56% speedup for the newer model, representing less latency for applications and lower computer costs.

## When should you use Jina Reranker v3.5?

Reranking improves search precision in practically every case, and `jina-reranker-v3.5` has applications in a wide variety of information retrieval contexts. However, it has some limitations. The table below summarizes our best-practice advice:

| Use case | Recommendation |
| --- | --- |
| General text retrieval in common international languages | Use `jina-reranker-v3.5`. |
| Legal, financial, and medical domain retrieval | Use `jina-reranker-v3.5`. |
| Semi-structured data, tables, product information texts for ecommerce | Use `jina-reranker-v3.5`. |
| Non-text or mixed-media data | Use `jina-reranker-m0`, which supports both text and image input. |

## How to use Jina Reranker 3.5 with the Elastic Inference API

`jina-reranker-v3.5` is available via the [Jina API](https://jina.ai/reranker/) with free tokens to try it out. It’s also available via the [Elastic Inference API](https://www.elastic.co/docs/explore-analyze/elastic-inference/inference-api) and [Elastic Inference Service](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis).

If you’re already using `jina-reranker-v3`, all you have to do is change the name of the model in the `model` field of your request to the Jina API or `model_id` field when configuring an Elastic Inference API endpoint. The two models have completely identical interfaces.

You can install `jina-reranker-v3.5` as a [Jina On-Prem container](https://www.elastic.co/search-labs/blog/on-prem-ai-jina-embedding-models) to get a completely self-contained server that runs on your own hardware. The model weights are also available to download for testing and research. Follow the instructions on the [model’s page at Hugging Face](https://huggingface.co/jinaai/jina-reranker-v3.5). In both cases, the model is available under a [CC BY-NC-4.0 license](https://creativecommons.org/licenses/by-nc/4.0/deed.en), so you’re free to try it out for testing, building prototypes, or doing scientific research. For commercial use, please contact Elastic sales.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt17731ab0c6ec66f6/6a6a33d140a4941014ca5c9a/09bc6dac4e6a86c7877f8ed78d68f5d581aeffa9-1999x1200.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Integrations](/search-labs/blog/category/integrations)

### On-prem in under 5 minutes: Jina embedding models now available for on-prem deployment

July 23, 2026|[Scott Martens](/search-labs/author/scott-martens)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt14665f5adef8d917/6a4695c72d406b3bb9ba2bb2/3668b433275c8d75fbc0729346123ea87307d012-1999x1125.png)

[Jina AI](/search-labs/blog/category/jina-ai)

### Small model, big benchmarks: how Jina-VLM beat the competition at 2.4B and what ICLR told us is coming next

May 27, 2026|[Andreas Koukounas](/search-labs/author/andreas-koukounas)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt99fb16c79484a00f/6a54fb02600d7743b9e424d9/43df5ec915eae1b9f1534d3acaf2e58732733d9b-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Jina AI](/search-labs/blog/category/jina-ai)[ML Research](/search-labs/blog/category/ml-research)

### How BBQ shrinks Jina v5 embeddings by 29x without losing recall in Elasticsearch

July 10, 2026|[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt1d9669e8c7a62bf6/6a170ee7a929cf0371ae0a87/42f72633f1e5453dbfd47730b5f776429f9f633e-721x420.png)

[Jina AI](/search-labs/blog/category/jina-ai)

### Jina embeddings v3 now available on Gemini Enterprise Agent Platform Model Garden

April 22, 2026|[Sa Zhang](/search-labs/author/sa-zhang)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter