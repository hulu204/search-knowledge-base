---
title: 'Search Quality Evaluation with LLMs: the Dataset Generator'
company: Sease
tag: 评测
date: 2026-07-01
url: https://sease.io/2026/07/search-quality-evaluation-with-llms-the-dataset-generator.html
account: 
origin: harvest3-202607
---
Hi there! In this post, we are excited to introduce a brand new tool: **the Dataset Generator**. We will walk through the following:

* Building Relevance Datasets Challenge
* Introducing The Dataset Generator
* How The Dataset Generator Works
* Why The Dataset Generator Matters
* Getting Started With The Tool

Before we dive into the tool, let us first unpack a key challenge: why is building relevance datasets so hard?

## Building Relevance Datasets Challenge

Evaluating the quality of search results is substantial in search engines. Search teams need reliable datasets where queries are mapped to documents, each with a relevance rating. While extracting queries from production logs is often straightforward, assigning meaningful relevance ratings to query-document pairs is a cumbersome task. The process is mundane and time-consuming, relying on subjective human judgment. This reliance on raters often introduces bias, leading to inaccurate ratings.

Building high-quality offline evaluation datasets has become a chimera for the industry. The lack of such datasets hinders the ability to measure and improve search quality in a systematic and reproducible way.

## Introducing The Dataset Generator

To address this challenge, we developed the Dataset Generator, an open-source tool designed to automate the generation of relevance datasets for search evaluation. **The Dataset Generator leverages the power of Large Language Models (LLMs) to generate natural language, keyword-based queries, and assign relevance ratings, reducing the manual effort required**.

It is a CLI tool that has the following key features:

* **Flexible configuration**: Uses a YAML configuration file, allowing users to specify the search engine type (supported engines: Solr, Elasticsearch, OpenSearch, Vespa), document filters, fields to use, and more.
* **Query Template:** The template is used to retrieve documents from the search engine.
* **Query Generation**: Generates queries from an index/collection or uses user-predefined queries.
* **Relevance Rating**: Uses LLMs (from well-known services such as OpenAI or Google ones) to score the relevance of document-query pairs, simulating expert judgment at scale.
* **Different Output Formats**: Supports output formats compatible with evaluation tools, including [Quepid](https://github.com/o19s/quepid), [RRE](https://github.com/SeaseLtd/rated-ranking-evaluator), and [MTEB](https://github.com/embeddings-benchmark/mteb).
* **Autosaving and Explainability:** Optionally saves progress and stores LLM rating explanations, supporting transparency and reproducibility.

## How The Dataset Generator Works

1. First, we set up the configuration files: **config.yaml** and the LLM configuration to specify the search engine, source document fields, the number of documents to retrieve, output format, and other settings.
2. Next, the system connects to the search engine to retrieve documents from the corpus of information based on the defined filters and returns the document fields listed in the config.yaml.
3. Once the documents are retrieved, they are passed to the LLM, which generates queries based on their content. Those queries are merged with the ones provided by the user (optional) to have a single query set.
4. For each query-document pair, the LLM assigns a relevance score, which can be either binary or graded (as configured in the config file).
5. Finally, once all triplets (query, document, rating) are produced, the dataset is saved in the specified format (Quepid, RRE, or MTEB), making it ready for use in search evaluation tools.

The following diagram illustrates the overall process:

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/03/Screenshot_20260505_171531.png?fit=800%2C642&ssl=1)

## Why The Dataset Generator Matters

Initially, we referred to building relevance datasets as a chimera. Because it requires human experts to rate query–document pairs manually, which is a long, tedious process, it might lead to biased ratings and is nearly impossible to scale.

Therefore, we developed the Dataset Generator tool to address this issue by leveraging large language models to automate query generation and relevance ratings. **It transforms the manual, error-prone task into an efficient, repeatable, and scalable process**.

By automating the most labour-intensive parts of dataset creation, the tool empowers teams to build high-quality evaluation datasets quickly and consistently. This makes offline search quality evaluation accessible to more organisations, helping to close the gap between theory and practice in search relevance engineering.

## Getting Started With The Tool

The Dataset Generator is open-source and available on [GitHub](https://github.com/SeaseLtd/llm-search-quality-evaluation). Check out the [README](https://github.com/SeaseLtd/llm-search-quality-evaluation/blob/main/README.md) for setup instructions and configuration examples. Whether you are a search engineer or researcher, the Dataset Generator can help streamline your search evaluation process.

Thanks for reading! We’d love to hear your feedback.