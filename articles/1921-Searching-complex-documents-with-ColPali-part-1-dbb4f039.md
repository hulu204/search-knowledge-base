---
title: 'Searching complex documents with ColPali - part 1'
company: Elastic
tag: 召回
date: 2025-03-18
url: https://www.elastic.co/search-labs/blog/elastiacsearch-colpali-document-search
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Searching complex documents with ColPali - part 1

The article introduces the ColPali model, a late-interaction model that simplifies the process of searching complex documents with images and tables, and discusses its implementation in Elasticsearch.

March 18, 2025

[Peter Straßer](/search-labs/author/peter-straer)[Benjamin Trent](/search-labs/author/benjamin-trent)

[Relevance](/search-labs/blog/category/relevance)[Vector Database](/search-labs/blog/category/vector-database)

Part of the series:

[The ColPali model series](/search-labs/blog/series/colpali-model-elasticsearch)

In this series

Share

When building search applications, we often need to deal with documents that have complex structures—tables, figures, multiple columns, and more. Traditionally, this meant setting up complicated retrieval pipelines including OCR (optical character recognition), layout detection, semantic chunking, and other processing steps. In 2024, the model [ColPali](https://arxiv.org/pdf/2407.01449) was introduced to address these challenges and simplify the process.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf422d958da10e23b/6a17f4bf420229860c29f734/f642006f1dec8a516d1949cf40abfabd2219756f-970x794.png)

Source: <https://huggingface.co/blog/manu/colpali>

From Elasticsearch version 8.18 onwards, we added support for late-interaction models such as ColPali as a tech preview feature. In this blog, we will take a look at how we can use ColPali to search through documents in Elasticsearch.

## ColPali performance

While we have [many benchmarks](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#elser-qualitative-benchmarks) that are based on previously cleaned-up text data to compare different retrieval strategies, the authors of the ColPali paper argue that real-world data in many organizations is messy and not always available in a nice, cleaned-up format.

![Example documents from the ColPali paper](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltd4d984bb201c230d/6a17f4c1414c64edb69452e1/d9b10e740bf5a055089116bee35630a8373e4436-1014x680.png)

Example documents from the ColPali paper: <https://arxiv.org/pdf/2407.01449>

To better represent these scenarios, the [ViDoRe benchmark](https://huggingface.co/spaces/vidore/vidore-leaderboard) was released alongside the ColPali model. This benchmark includes a diverse set of document images from sectors such as government, healthcare, research, and more. A range of different retrieval methods, including complex retrieval pipelines or image embedding models, were compared with this new model.

The following table shows that ColPali performs exceptionally well on this dataset and is able to retrieve relevant information from these messy documents reliably.

![ColPali retrieval performance ](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt682e41dadb4078e9/6a17f4c3414c642e6d9452e5/ce5361af7353005a0e34b3b21f1e22be4ace4559-1600x966.png)

Source: <https://arxiv.org/pdf/2407.01449> Table 2

## How ColPali works

As teased in the beginning, the idea of ColPali is to just embed the image instead of extracting the text via complicated pipelines. ColPali builds on the vision capabilities of the PaliGemma model and the late-interaction mechanism introduced by ColBERT.

![How ColiPali works](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt518c18c8c003ea47/6a17f4c5be6086e4770048d6/d26e7f36ceaac345abd3e54a52f9715e8b40ec4a-1600x965.png)

Source: <https://arxiv.org/pdf/2407.01449> Figure 1

Let’s first take a look at how we index our documents.

Instead of converting the document into a textual format, ColPali processes documents by dividing a screenshot into small rectangles and converts each into a 128-dimensional vector. This vector represents the contextual meaning of this patch within the document. In practice, a 32x32 grid generates 1024 vectors per document.

For our query, the ColPali model creates a vector for each token.

To score documents during search, we calculate the distance between each query vector and each document vector. We keep only the highest score per query vector and sum those scores for a final document score.

![ColPali late interaction mechanism for scoring ColBERT](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt79032a0038aeb8bb/6a17f4c796142a6f2ceb1c5e/4926ef745a9f686ec7810213bee4d7b561f3ca3d-1600x665.png)

Late interaction mechanism for scoring ColBERT

## ColPali interpretability

Vector search with bi-encoders struggle with the fact that the results are sometimes not very interpretable—meaning we don’t know *why* a document matched. Late interaction models are different: we know how well each document vector matches our query vectors; therefore, we can determine *where* and *why* a document matches.

![Colipali heatmap](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltf79799a18b043ea8/6a17f4c963baff4013741d8c/5a8572802071717e571be5a4d7543cfc03f5c9c8-1600x1346.png)

A heatmap of where the word “hour” matches in this document. Source: <https://arxiv.org/pdf/2407.01449>

## Searching with ColPali in Elasticsearch

We will be taking a subset of the ViDoRe test set to take a look at how to index documents with ColPali in Elasticsearch. The [full code examples can be found on GitHub](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/colpali/01_colpali.ipynb).

To index the document vectors, we will be defining a mapping with the new [rank\_vectors](https://www.elastic.co/guide/en/elasticsearch/reference/8.18/rank-vectors.html) field.

```
mappings = {
    "mappings": {
        "properties": {
            "col_pali_vectors": {
                "type": "rank_vectors"
            }
        }
    }
}

INDEX_NAME = "searchlabs-colpali"
es = Elasticsearch(<ELASTIC_HOST>, api_key=<ELASTIC_API_KEY>)
es.indices.create(index=INDEX_NAME, body=mappings)

for image_path in tqdm(images, desc="Index documents"):
    vectors = create_col_pali_image_vectors(image_path)
    es_client.index(index=INDEX_NAME, id=image_path, document={"col_pali_vectors": vectors})
```

We now have an index ready to be searched full of ColPali vectors. To score our documents, we can use the new `maxSimDotProduct` function.

```
query = "What do companies use for recruiting?"
es_query = {
    "_source": False, 
    "query": {
        "script_score": {
            "query": {
                "match_all": {}
            },
            "script": {
                "source": "maxSimDotProduct(params.query_vector, 'col_pali_vectors')",
                "params": {
                    "query_vector": create_col_pali_query_vectors(query)
                }
            }
        }
    },
    "size": 5
}

results = es.search(index=INDEX_NAME, body=es_query)
image_ids = [hit["_id"] for hit in results["hits"]["hits"]]

html = "<div style='display: flex; flex-wrap: wrap; align-items: flex-start;'>"
for image_id in image_ids:
    image_path = os.path.join(DOCUMENT_DIR, image_id)
    html += f'<img src="{image_path}" alt="{image_id}" style="max-width:300px; height:auto; margin:10px;">'
html += "</div>"

display(HTML(html))
```

![Searching with ColPali in Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbccfb326b47c2d5b/6a17f4cb3e9e4565dfba15eb/2bfc5b9d5aaf8b89dd702ccc70f62cd47b2d165c-1600x766.png)

## Key takeaways on ColPali in Elasticsearch

ColPali is a powerful new model that can be used to search complex documents with high accuracy. Elasticsearch makes it easy to use as it provides a fast and scalable search solution. Since the initial release, other powerful iterations such as [ColQwen](https://huggingface.co/vidore/colqwen2-v1.0) have been released. We encourage you to try these models for your own search applications and see how they can improve your results.

Before implementing what we covered here in production environments, we highly recommend that you check out [part 2](https://www.elastic.co/search-labs/blog/scale-late-interaction-model-colpali) of this article. [Part 2](https://www.elastic.co/search-labs/blog/scale-late-interaction-model-colpali) explores advanced techniques, such as bit vectors and token pooling, which can optimize resource utilization and enable effective scaling of this solution.

### Frequently Asked Questions

#### What is ColPali?

ColPali is a late-interaction model that simplifies the process of searching complex documents with images and tables.

#### How does ColPali works?

ColPali processes documents by dividing a screenshot into small rectangles and converting each into a 128-dimensional vector. For our query, the ColPali model creates a vector for each token. To score documents during search, the distance between each query vector and each document vector is calculated.

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