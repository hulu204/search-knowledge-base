---
title: 'Reranking with an Elasticsearch-hosted cross-encoder from Hugging Face'
company: Elastic
tag: 排序
date: 2024-11-04
url: https://www.elastic.co/search-labs/blog/elasticsearch-cross-encoder-reranker-huggingface
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Reranking with an Elasticsearch-hosted cross-encoder from Hugging Face

Learn how to use a model from Hugging Face to host and perform semantic-reranking in Elasticsearch.

November 04, 2024

[Jeff Vestal](/search-labs/author/jeff-vestal)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

In this short blog, I’ll show you how to use a model from Hugging Face to perform semantic reranking in your own Elasticsearch cluster at search time. We will download the model using Eland, load a dataset from Hugging Face, and perform sample queries using retrievers, all in a Jupyter notebook.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltbdfafde22e3805e7/6a170285b339d5f841769e64/132ad8f017800892e594040ad9bb003eb03979e8-3072x1536.png)

## Overview

If you are unfamiliar with Semantic Text, check out these resources:

* What it is
* Why you would want to use it
* How to create an inference API and connect it to an external service
* How to use a retriever query for re-ranking

Please review the following links:

* [What is semantic reranking and how to use it?](https://www.elastic.co/search-labs/blog/elastic-semantic-reranker-part-1)

  + Learn about the trade-offs using semantic reranking in search and RAG pipelines
* [Semantic reranking in Elasticsearch with retrievers](https://www.elastic.co/search-labs/blog/semantic-reranking-with-retrievers)

  + This blog includes a video presentation and an overview of everything you need to get started.
* [Elastic Docs - Semantic re-ranking](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-reranking.html#semantic-reranking-in-es)

  + This excellent doc guide talks about use cases, encoder model types, and re-ranking in Elasticsearch

The code in this blog and accompanying notebook will also get you started, but we aren’t going to go in-depth on the what and why.

Also, note that I’ll show code snippets below, but the best way to do this yourself is to follow the [accompanying notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/re-ranking-elasticsearch-hosted/re-ranking-elasticsearch-hosted.ipynb).

## Step zero

I will also assume you have an Elasticsearch cluster or serverless project you will use for this guide. If not, head on over to [cloud.elastic.co](https://cloud.elastic.co/registration?onboarding_token=search&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs) and sign up for a free trial! You'll need a [Cloud ID](https://www.elastic.co/guide/en/kibana/8.16/search-space-connection-details.html#find-cloud-id-cloud-self-managed) and [Elasticsearch API Key](https://www.elastic.co/guide/en/kibana/current/api-keys.html).

I’ll wait...

## Model selection

The first (real) step is choosing a model to use for re-ranking. A deep discussion of selecting a model and evaluating results is outside the scope of this blog. Know that, for now, [Elasticsearch only supports cross-encoder models](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-reranking.html#semantic-reranking-models).

While not directly covering model selection, the following blogs give a good overview of evaluating search relevance.

[Evaluating Search Relevance](https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-1) (three-part series)

[Search relevance tuning: Balancing keyword and semantic search](https://www.elastic.co/search-labs/blog/search-relevance-tuning-in-semantic-search)

For the guide, we are going to use the [cross-encoder/ms-marco-MiniLM-L-6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2). This model used the MS Marco dataset for retrieval and re-ranking.

## Model loading

To load an NLP model from Hugging Face into Elasticsearch, you will use the Eland Python Library.

Eland is Elastic's Python library for data frame analytics and loading supervised and NLP models into Elasticsearch. It offers a familiar Pandas-compatible API.

The code below is from the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/re-ranking-elasticsearch-hosted/re-ranking-elasticsearch-hosted.ipynb) section "Hugging Face Reranking Model."

```
model_id = "cross-encoder/ms-marco-MiniLM-L-6-v2"

cloud_id = "my_super_cloud_id"
api_key = "my_super_secred_api_key!"

!eland_import_hub_model \
--cloud-id $cloud_id \
--es-api-key $api_key \
--hub-model-id $model_id \
--task-type text_similarity
```

Eland doesn’t have a specific `rerank` task type; we use the text\_similarity type to load the model.

This step will download the model locally where your code is running, split it apart, and load it into your Elasticsearch cluster.

## Cut to

In the notebook, you can follow along to set up your cluster to run the re-ranking query in the next section. The setup steps after downloading the model shown in the notebook are:

* Create an Inference Endpoint with the rerank task

  + This will also deploy our re-ranking model on Elasticsearch machine learning nodes
* Create an index mapping
* Download a dataset from Hugging Face - [CShorten/ML-ArXiv-Papers](https://huggingface.co/datasets/CShorten/ML-ArXiv-Papers)
* Index the data into Elasticsearch

## Re-rank time!

With everything set up, we can query using the text\_similarity\_reranker [retriever](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#text-similarity-reranker-retriever). The text similarity reranker is a two-stage reranker. This means that the specified retrievers are run first, and then those results are passed to the second re-ranking stage.

Example from the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/re-ranking-elasticsearch-hosted/re-ranking-elasticsearch-hosted.ipynb):

```
query = "sparse vector embedding"

# Query with Semantic Reranker
response_reranked = es.search(
    index="arxiv-papers-lexical",
    body={
      "size": 10,
      "retriever": {
        "text_similarity_reranker": {
          "retriever": {
            "standard": {
              "query": {
                "match": {
                  "title": query
                }
              }
            }
          },
        "field": "abstract",
        "inference_id": "semantic-reranking",
        "inference_text": query,
        "rank_window_size": 100
      }
    },
    "fields": [
      "title", 
      "abstract"
    ], 
    "_source": False
    }
)
```

The [parameters](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#_parameters_7) for the text\_similarity\_reranker above are:

* ``retriever` - Here, we do a simple match query with a standard retriever for lexical first-stage retrieval. You can also use a [knn](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#knn-retriever) retriever or an [rrf](https://www.elastic.co/guide/en/elasticsearch/reference/current/retriever.html#rrf-retriever) retriever here.
* `field` - The field from the first-stage results the re-ranking model will use for similarity comparisons.
* `inference_id` - The ID of the inference service to use for re-ranking. Here, we are using the model we loaded earlier.
* `inference_text` - The string to use for the similarity ranking
* `rank_window_size` - The number of top documents from the first stage the model will consider.

You may wonder why `rank\_window\_size` is set to 100, even though you might ultimately want only the top 10 results.

In a two-stage search setup, the initial lexical search provides a broad set of documents for the semantic re-ranker to evaluate. Returning a larger set of 100 results increases the chances that relevant documents are available for the semantic re-ranker to identify and reorder based on semantic content, not just lexical matches. This approach compensates for the lexical search's limitations in capturing nuanced meaning, allowing the semantic model to sift through a broader range of possibilities.

However, finding the right `rank\_window\_size` is a balance. While a larger candidate set improves accuracy, it may also increase resource demands, so some tuning is necessary to achieve an optimal trade-off between recall and resources.

## Comparison

While I’m not going to provide an in-depth analysis of the results in this short guide, What may be of general interest is to look at the top 5 results from a standard lexical match query and the results from the re-ranked query above.

This dataset contains a subset of ArXiv papers about Machine Learning. The results listed are the titles of the papers.

The “**Scored Results**” are the top 10 results using a standard retriever

The “**Reranked Results**” are the top 10 results after re-ranking

|  | Scored Results | Reranked Results |
| --- | --- | --- |
| 0 | Compact Speaker Embedding: lrx-vector | Scaling Up Sparse Support Vector Machines by Simultaneous Feature and Sample Reduction |
| 1 | Quantum Sparse Support Vector Machines | Spaceland Embedding of Sparse Stochastic Graphs |
| 2 | Sparse Support Vector Infinite Push | Elliptical Ordinal Embedding |
| 3 | The Sparse Vector Technique, Revisited | Minimum-Distortion Embedding |
| 4 | L-Vector: Neural Label Embedding for Domain Adaptation | Free Gap Information from the Differentially Private Sparse Vector and Noisy Max Mechanisms |
| 5 | Spaceland Embedding of Sparse Stochastic Graphs | Interpolated Discretized Embedding of Single Vectors and Vector Pairs for Classification, Metric Learning and Distance Approximation |
| 6 | Sparse Signal Recovery in the Presence of Intra-Vector and Inter-Vector Correlation | Attention Word Embedding |
| 7 | Stable Sparse Subspace Embedding for Dimensionality Reduction | Binary Speaker Embedding |
| 8 | Auto-weighted Mutli-view Sparse Reconstructive Embedding | NetSMF: Large-Scale Network Embedding as Sparse Matrix Factorization |
| 9 | Embedding Words in Non-Vector Space with Unsupervised Graph Learning | Estimating Vector Fields on Manifolds and the Embedding of Directed Graphs |

## Your turn

Hopefully, you see how easy it is to incorporate a re-ranking model from Hugging Face into Elasticsearch so you can start re-ranking. While this isn't the only re-ranking option, it can be helpful when you are running air-gapped, don't have access to an external re-ranking service, wants to control costs or have a model that works particularly well for your dataset.

## Try it Now!

You can try the accompanying notebook in a live workshop environment for free!

[**Click here to head over to the lab now.**](https://play.instruqt.com/elastic/invite/ydxhehbmhcfs)

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3c6ae6e21526155c/6a170288d7c0228442de6337/3850e31aab367e1ab1c7c254de7650b802935c1a-3390x1888.png)

Try out the accompanying notebook in a live lab environment now.

[Click this link](https://play.instruqt.com/elastic/invite/ydxhehbmhcfs) to head over to the lab environment!

If you haven't clicked on one of the many links to the [accompanying notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/re-ranking-elasticsearch-hosted/re-ranking-elasticsearch-hosted.ipynb), now's the time!

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