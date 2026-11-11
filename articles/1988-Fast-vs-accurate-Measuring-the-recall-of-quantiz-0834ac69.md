---
title: 'Fast vs. accurate: Measuring the recall of quantized vector search'
company: Elastic
tag: 评测
date: 2026-03-20
url: https://www.elastic.co/search-labs/blog/recall-vector-search-quantization
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Fast vs. accurate: Measuring the recall of quantized vector search

Explaining how to measure recall for vector search in Elasticsearch with minimal setup.

March 20, 2026

[Jeff Vestal](/search-labs/author/jeff-vestal)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

Everyone wants vector search to be instant. But high-dimensional vectors are heavy. A single 1,024-dimension float-32 vector takes up significant memory, and comparing it against millions of others is computationally expensive.

To solve this, search engines like Elasticsearch use two main optimization strategies:

1. **Approximate search (hierarchical navigable small world [HNSW]):** Instead of scanning every document, we build a navigation graph to jump quickly to the likely neighborhood of the answer.
2. **Quantization:** We compress the vectors (for example, from 32-bit floats to 8-bit integers or even 1-bit binary values) to reduce memory usage and speed up calculations.

But optimization often comes with a tax: **accuracy**.

The fear is valid: "If I compress my data and take shortcuts during the search, will I miss the best results?" "Does this optimization degrade the relevance of my search engine?"

To prove that Elastic’s quantization doesn’t degrade results, we built a repeatable test harness using the [**DBPedia-14**](https://huggingface.co/datasets/fancyzhx/dbpedia_14) [dataset](https://huggingface.co/datasets/fancyzhx/dbpedia_14) to calculate exactly how much accuracy (specifically, **recall)** we trade for speed when using default optimizations in Elasticsearch.

tldr: It’s likely much less than you think. Check out the [notebook here](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/fast_vs_accurate_measuring_the_recall_of_quantized_vector_search/vector_recall_notebook.ipynb), and try it yourself

## **The definitions (for the non-experts)**

Before we look at the code, let’s level-set on some terms.

* **Relevance versus recall:** **Relevance** is subjective (did I find good stuff?). **Recall** is mathematical. If there are 10 documents in the database that are the *perfect* mathematical matches for your query, and the search engine finds nine of them, your recall is 90% (or 0.9).
* **Exact search (flat):** Sometimes called the "brute force" method. The search engine scans every single document in an index and calculates the distance.

  + *Pros:* 100% perfect recall.
  + *Cons:* Computationally expensive and slow at scale.
* **Approximate search (HNSW):** The "shortcut" method. The search engine builds an [HNSW](https://www.elastic.co/search-labs/blog/hnsw-graph) graph. It traverses the graph to find the nearest neighbors.

  + *Pros:* Extremely fast and scalable.
  + *Cons:* You might miss a neighbor if the graph traversal stops too early.

## **The experiment: Exact versus approximate**

To test recall, we used the **DBPedia-14** dataset, a large dataset of titles and abstracts across 14 ontology classes, commonly used for training and evaluating text categorization models. Specifically, we’ll focus on the "Film" category. We wanted to compare the optimized production settings against a mathematically perfect ground truth.

For this experiment, we are using the [jina-embeddings-v5-text-small](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text) model, a state-of-the-art multilingual model that leads industry benchmarks for text representation. We chose this model because it defines the current standard for high-performance embeddings. By combining Jina v5’s elite accuracy with Elasticsearch’s native quantization, we can demonstrate a search architecture that is both computationally efficient and uncompromising on retrieval quality.

We set up an index with dual mapping. We ingested the same text into two different fields simultaneously:

1. `content.raw`with type: `flat`. This forces Elasticsearch to perform a brute-force scan of the full Float32 vectors. This returns exact match results and will be used for our baseline.
2. `content`with type `semantic_text`. With defaults using HNSW + Better Binary Quantization (BBQ). This is the standard, optimized production setting for approximate match.

### **The Recall@10 test**

For our metric, we used Recall@10.

We picked 50 random movies and ran the same query against both fields.

* If the **exact (flat)** search says the top 10 neighbors are IDs [1, 2, 3... 10].
* And the **approximate (HNSW)** search returns IDs [1, 2, 3... 9, 99].
* We found nine out of the top 10 correctly. The score is **0.9**.

Here’s the mapping we used:

```
# The "Control Group": Forces exact brute-force scan
"raw": {
    "type": "semantic_text",
    "inference_id": ".jina-embeddings-v5-text-small",
    "index_options": {
        "dense_vector": {
            "type": "flat"
        }
    }
}
```

**The results: The "flat line" of success**

We ran a scale test, reloading the full dataset and testing against index sizes of 1,000 to 40,000 documents.

Here’s what happened to the recall score:

| Documents | Recall@10 score |
| --- | --- |
| 1,000 | 1.000 (100%) |
| 5,000 | 0.998 (100%) |
| 10,000 | 0.992 (99.4%) |
| 20,000 | 0.999 (99.0%) |
| 40,000 | 0.992 (98.8%) |

The results were incredibly stable. Even as we scaled up, the approximate search matched the brute-force exact search **>99% of the time**.

![vector search stability: Recall vs  Index Size](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt8168a0a4946bade7/6a170e154a531b61b536a9eb/a4bfacb1d0cce6fdf6df0e1a9d4fc5d4007a66da-1999x1209.png)

## **Why did it work so well?**

You might expect that compressing vectors to binary values would hurt accuracy more than this. The reason it doesn't lies in how Elasticsearch handles the retrieval.

Most embedding models today output Float32 vectors, which are large. To make search efficient, Elasticsearch uses quantization for high-dimensional vectors. Specifically, since 9.2, it uses [BBQ](https://www.elastic.co/search-labs/blog/elasticsearch-9-1-bbq-acorn-vector-search) by default.

BBQ uses a **rescoring** mechanism:

1. **Traversal:** The search engine uses the compressed (quantized) vectors to traverse the HNSW graph quickly. Because the vectors are small, it can efficiently over-sample, gathering a larger list of candidates (for example, the top 100 roughly similar docs) without a performance penalty.
2. **Rescore:** Once it has those candidates, it retrieves the full-precision values for just those few documents to calculate the final, precise ranking.

This gives you the best of both worlds, the speed of quantization for the heavy lifting, and the precision of floats for the final sort.

## **Can we do better?**

It’s worth noting that the results we’re seeing here are using default settings and a random sampling of data. Think of this as a high-performance starting point. While Jina v5 is a beast, these recall scores aren't a "one size fits all" guarantee for every dataset. Every data collection has its own quirks, and while you can definitely tune things further to squeeze out even more performance, you should always benchmark against your own specific data to see where your ceiling is.

## **Conclusion**

This is a very small-scale test. But the point of the exercise is not to measure the embedding model or BBQ specifically, it’s to demonstrate how you can easily measure the recall of your dataset with minimal setup.

If you want to run this test on your own data, you can check out the [notebook here](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/fast_vs_accurate_measuring_the_recall_of_quantized_vector_search/vector_recall_notebook.ipynb) and try it yourself.

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