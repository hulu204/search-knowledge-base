---
title: 'An open‑source Hebrew analyzer for Elasticsearch lemmatization'
company: Elastic
tag: 查询理解
date: 2026-02-17
url: https://www.elastic.co/search-labs/blog/elasticsearch-lemmatization-hebrew-analyzer
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# An open‑source Hebrew analyzer for Elasticsearch lemmatization

An open-source Elasticsearch 9.x analyzer plugin that improves Hebrew search by lemmatizing tokens in the analysis chain for better recall across Hebrew morphology.

February 17, 2026

[Lily Adler](/search-labs/author/lily-adler)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

Hebrew is morphologically rich: Prefixes, inflections, and clitics make exact-token search brittle. This project provides an open-source Hebrew analyzer plugin for Elasticsearch 9.x that performs neural lemmatization in the analysis chain, using an embedded DictaBERT model executed in-process via ONNX Runtime with an INT8-quantized model.

## **Quick start**

Download the relevant [release](https://github.com/liladler/elasticsearch-analysis-hebrew-plugin/releases) or build and install (Linux build script generates Elasticsearch‑compatible zip):

```
./scripts/build_plugin_linux.sh
```

Install in Elasticsearch:

```
/path/to/elasticsearch/bin/elasticsearch-plugin install file:///path/to/heb-lemmas-embedded-plugin-<ES_VERSION>.zip
```

Test:

```
curl -k -X POST "https://localhost:9200/_analyze" \
  -H "Content-Type: application/json" \
  -u "elastic:<password>" \
  -d '{"tokenizer":"whitespace","filter":["heb_lemmas","heb_stopwords"],"text":"הילדים אוכלים את הבננות"}'
```

## Why Hebrew search is different

Hebrew is morphologically rich: Prefixes, suffixes, inflection, and clitics all collapse into a single surface form. That makes naive tokenization insufficient. Without true lemmatization, search quality suffers; users miss relevant results due to simple variations in form. This project tackles that by embedding a Hebrew lemmatization model inside the analyzer itself, so every token passes through a neural model before indexing and querying.

### Example

Users may search for the lemma “בית” (house), but documents might contain:

* בית (a house)
* בבית (in the house)
* לבית (to the house)
* בבתים (in houses)
* לבתים (to houses)

Without lemmatization, these become different surface tokens; lemmatization normalizes them toward the same lemma (בית), improving recall:

![Hebrew analyzer for Elasticsearch lemmatization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbce7cc588b978eca/6a170e4facf0888338be9bec/d3dfd40569b3f4bfc79df639a49ae995e92b0bc1-1600x983.png)

## What this plugin does

Rather than relying on rule-based stemming, the analyzer runs a Hebrew lemmatization model as part of the Elasticsearch analysis chain and emits one normalized lemma per token. Because the model is neural, it can use local context within each analyzed segment to choose a lemma in ambiguous cases—while still producing stable tokens that work well for indexing and querying. The analyzer:

* Runs a Hebrew lemmatization model inside Elasticsearch.
* Produces better normalized tokens for Hebrew text.
* Supports stopwords and standard analyzer pipelines.

## The result: Fast, reliable lemmatization

This analyzer is optimized for real‑world throughput:

* ONNX Runtime in‑process inference.
* INT8-quantized model for lower latency and memory footprint.
* Java Foreign Function Interface (FFI) for high‑performance native inference.

The result: fast, reliable lemmatization with predictable operational behavior.

To evaluate performance, we ran a benchmark in a Docker container (4 cores, 12 GB RAM) on 1 million large documents (5.7 GB of data) from the Hebrew Wikipedia dataset. You’ll find the results below:

| Metric (search) | Task | Value | Unit |
| --- | --- | --- | --- |
| Min throughput | hebrew-query-search | 409.75 | ops/s |
| Mean throughput | hebrew-query-search | 490.65 | ops/s |
| Median throughput | hebrew-query-search | 491.85 | ops/s |
| Max throughput | hebrew-query-search | 496.13 | ops/s |
| 50th percentile latency | hebrew-query-search | 7.02242 | ms |
| 90th percentile latency | hebrew-query-search | 10.7338 | ms |
| 99th percentile latency | hebrew-query-search | 19.0406 | ms |
| 99.9th percentile latency | hebrew-query-search | 27.165 | ms |
| 50th percentile service time | hebrew-query-search | 7.02242 | ms |
| 90th percentile service time | hebrew-query-search | 10.7338 | ms |
| 99th percentile service time | hebrew-query-search | 19.0406 | ms |
| 99.9th percentile service time | hebrew-query-search | 27.165 | ms |
| Error rate | hebrew-query-search | 0 | % |

## Open source and Elastic‑ready

The plugin is fully open source and works on:

* Elastic open‑source distributions.
* Elastic Cloud.

You can build it yourself or download prebuilt releases and install it like any other plugin.

To upload the analyzer plugin to Elastic Cloud, navigate to the **Extensions** section within your Elastic Cloud console and proceed with the upload.

![Open source and Elastic‑ready for Hebrew analyzer for Elasticsearch lemmatization](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt63c562ad175596ae/6a170e517d8d6737f070e7ca/e2e8731aeb884e91624f2c8c0998cf8de08a16e3-1402x1600.png)

## Credits

This project is a fork of the Korra ai Hebrew analysis plugin (MIT), which was implemented by [Korra.ai](http://Korra.ai) with funding and guidance from the National NLP Program led by MAFAT and the Israel Innovation Authority.

This fork focuses on Elasticsearch 9.x compatibility and running lemmatization fully in-process via ONNX Runtime, using an INT8‑quantized model and bundled Hebrew stopwords. Lemmatization is powered by DictaBERT [`dicta-il/dictabert-lex`](https://huggingface.co/dicta-il/dictabert-lex) (CC‑BY‑4.0).

Huge thanks to the Dicta team for making high-quality Hebrew natural language processing (NLP) models available to the community.

## Links

* [GitHub repo](https://github.com/liladler/elasticsearch-analysis-hebrew-plugin)
* [Releases](https://github.com/liladler/elasticsearch-analysis-hebrew-plugin/releases)

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt021070497c8cbd23/6a170aeab0367d782c72bd0e/c506a0f5c0a33ca6f85454d4f742d7cb266a7b78-715x413.png)

[Relevance](/search-labs/blog/category/relevance)

### ES|QL, you know, for Search - Introducing scoring and semantic search

April 16, 2025|[Ioana](/search-labs/author/ioana-alina-tagirta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt93506c893fb19bb9/6a6119fea2ee17d20274edab/b08939addf8cfa92dd0b31211ff0a86511eb582c-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[Relevance](/search-labs/blog/category/relevance)[Jina AI](/search-labs/blog/category/jina-ai)

### A picture is worth 1.5x the words: What we learned benchmarking product search embeddings

July 16, 2026|[Sofia Vasileva](/search-labs/author/sofia-vasileva)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter