---
title: 'How to measure and improve Elasticsearch search recall: from 0.43 to 0.75 with hybrid search'
company: Elastic
tag: 召回
date: 2026-05-04
url: https://www.elastic.co/search-labs/blog/elasticsearch-relevance-tuning-improve-recall
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# How to measure and improve Elasticsearch search recall: from 0.43 to 0.75 with hybrid search

Learn how to measure and improve search recall in Elasticsearch by combining BM25 lexical search with Jina AI vector embeddings, using the rank\_eval API to validate the improvement with real numbers.

May 04, 2026

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

[Lexical search](https://www.elastic.co/docs/solutions/search/full-text) using the [BM25 ranking algorithm](https://www.elastic.co/blog/practical-bm25-part-1-how-shards-affect-relevance-scoring-in-elasticsearch) is cheap, fast, and very effective for a wide range of queries. But it has a blind spot: queries that don't share tokens with your documents. In this article, you’ll measure exactly where BM25 falls short. We'll use Elasticsearch's [ranking evaluation API](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval) (`rank_eval`) and close that gap by adding [Jina AI embeddings](https://www.elastic.co/search-labs/es/blog/jina-embeddings-v3-elastic-inference-service) through [Elastic Inference Service](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis) (EIS). You’ll see the recall score go from `0.43` to `0.75` and understand why.

## What is recall?

[Recall](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#k-recall) measures on a scale from `0` to `1` how many of the documents that your users actually want appear somewhere in your search results. If a query should surface three products and your search returns only two of them in the top 10, `recall@10 = 0.67` for that query. It’s a set-based metric: It doesn’t care about the position of the relevant documents within those *k* results. A relevant document in position 10 counts the same as one in position 1. Having a high recall means that you’re not losing relevant results.

![Venn diagram illustrating how Recall@10 is calculated by showing the overlap between all relevant documents and the top 10 results retrieved by BM25, resulting in a Recall@10 score of 0.40.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5ffd147b13705680/6a170a6fe8fbce11a539fc22/b13af2a5d0ca055535d8bfe3dfe4b3d1093ee6da-1457x796.png)

The diagram shows two sets: all relevant documents (left) and what BM25 actually retrieved (top 10, right). Only the intersection counts toward recall, `prod_1` and `prod_2` were found, while `prod_3`, `prod_4`, and `prod_6` were missed entirely. Result: `Recall@10 = 2/5 =` `0.40`.

## Prerequisites

Let's get down to business to better understand how recall works. This demonstration uses Python. You can follow along with it on the companion notebook ([notebook.ipynb](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/relevance-tuning-improving-recall-adding-vectors/notebook.ipynb)), where every code block is a cell ready to run.

The code provided uses the following:

* Elasticsearch 9.3+
* Python 3.10+

```
pip install elasticsearch pandas plotly python-dotenv
```

* A `.env` file with your Elasticsearch credentials

```
ELASTICSEARCH_URL=https://your-cluster-url
ELASTICSEARCH_API_KEY=your-api-key
```

## The dataset

We’ll use a product catalog of 1,000 products, spanning categories such as footwear, electronics, tools, and more.

Each document has four fields:

| Field | Type |
| --- | --- |
| `title` | text |
| `description` | text |
| `brand` | keyword |
| `category` | keyword |

The dataset is loaded from [`dataset.csv`](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/relevance-tuning-improving-recall-adding-vectors/dataset.csv).

## The power and limits of lexical search

BM25 is the default ranking algorithm in Elasticsearch and most search engines. It scores documents by how often your query terms appear in them, adjusted for document length and the frequency of those terms across the entire index. You get [analyzers](https://www.elastic.co/docs/reference/text-analysis/analyzer-reference) on top: lowercase normalization, stemming, and stopword removal. A query for "running shoes" will match "Running Shoes" and likely "run" as well.

This works well for a large class of queries:

* "running shoes" immediately matches products with those exact tokens in the title.
* "bluetooth speaker" surfaces portable audio products because the tokens appear verbatim.

The results are deterministic and explainable: A document ranks highly because the query terms appear in it. Debugging relevance is straightforward.

### Where it breaks

Now let’s try these queries against the same catalog:

* **"skincare routine":** The word "routine" doesn’t appear in any product title. BM25 can partially match on "skincare," but face serums, body oils, and moisturizers are described using terms like "vitamin C," "retinol," or "brightening," none of which overlap with the query. Products that form a complete skincare routine are scattered across the index with no shared token to anchor them.

```
ID: B06XX6DS3P, Score: 9.0552, Title: Replenix Retinol Smooth + Tighten Body Lotion - Collagen-Boosting, Regenerating Anti-Aging Body Cream, Reduces Appearance of Stretch Marks, 6.7 oz.

  ID: B08XMPKJ1L, Score: 5.2699, Title: Bio-Oil Skincare Body Oil (Natural) Serum for Scars and Stretchmarks, Face and Body Moisturizer Hydrates Skin, with Organic Jojoba Oil and Vitamin E, For All Skin Types, 6.7 oz

  ID: B01CY764KQ, Score: 5.0057, Title: Nike Up Or Down Men Deodorant - Pack of 2 | Long-Lasting Fragrance, Body Spray Combo for Men | Deodorant for Active Living | Nike Men's Deo Set | Ultimate Odor Protection | Grooming Essentials | Signature Nike Scent | High-Performance Men's Deodorant
```

* **"pet travel accessories":** This is a use-case grouping, not a product category. A dog sling carrier, a pet car seat, and a travel crate are all relevant, but their descriptions talk about portability, safety, and comfort rather than "travel accessories." BM25 matches "pet" broadly but has no signal to distinguish travel-specific products from the rest of the pet catalog.

```
ID: B0BVV7BKTW, Score: 7.4371, Title: Large Foldable Travel Duffel Bag with Shoes Compartment

ID: B07TNPHYNV, Score: 6.6455, Title: 40 Pieces Christmas Bronze Jingle Bells Craft Small Bells

ID: B08R8FRW53, Score: 6.6335, Title: CUBY Dog and Cat Sling Carrier
ID: B08QMCQYGM, Score: 6.5259, Title: YTFGGY Whiteboard Pinstripe Tape 6 Rolls 1/8"
ID: B0CP3LQSWM, Score: 6.2994, Title: Portable Dog Water Bottle 32 Oz
```

This is a **recall problem**. The relevant documents exist in your index. BM25 just cannot find them because the user's words and the document's words do not match closely enough.

Adding synonyms helps for known cases. But you cannot enumerate every way a user might express an intent. That is where vectors come in.

## Why you should measure recall

Before fixing a problem, you need to quantify it.

[**Recall@k**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#k-recall) measures how many of the documents that your users actually want appear somewhere in your search results. Formally:

```
Recall@k = (relevant documents found in top k) / (total relevant documents)
```

[**Precision@k**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#k-precision) measures the top k results and how many are actually relevant:

```
Precision@k = (relevant documents in top k) / k
```

High precision means that the results you do return are good. In ecommerce, missing a relevant product (low recall) is often worse than showing a slightly imperfect result (lower precision), because a hidden product is a lost sale.

Elasticsearch's `rank_eval` API lets you measure both systematically. You provide a list of queries, each with a set of rated documents, and Elasticsearch computes the metrics for you across all queries.

## Setting up the evaluation

The `rank_eval` API needs a **ratings dataset**: a mapping of queries to the documents that are relevant for each one, along with a relevance grade (0 = not relevant, 1 = relevant, 2 = highly relevant).

In the notebook, this is the [judgments list](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr#learning-to-rank-judgement-list):

```
judgments = [
    # Query 1: "running shoes" BM25 handles well (tokens appear in product titles) 
    {"query_id": "q1", "doc_id": "B09NQJFRW6", "grade": 2, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B08JMD4LMM", "grade": 2, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B08VRJ6F2Q", "grade": 2, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B07S8NRRWR", "grade": 2, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B01HD620I8", "grade": 2, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B07DX86321", "grade": 2, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B0968YVLQ8", "grade": 1, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B093QJ39ZS", "grade": 1, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B096FGSC39", "grade": 1, "query": "running shoes"},
    {"query_id": "q1", "doc_id": "B01GVQWVV2", "grade": 1, "query": "running shoes"},

    # Query 2: "skincare routine" intent-based, "routine" never appears in product titles
    {"query_id": "q2", "doc_id": "B08XMPKJ1L", "grade": 2, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B0BN3WQB92", "grade": 2, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B0BT7B7P5T", "grade": 2, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B00NPA2WEY", "grade": 2, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B06XX6DS3P", "grade": 1, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B07PDRD1KT", "grade": 1, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B074J7869B", "grade": 1, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B08JV31QW4", "grade": 1, "query": "skincare routine"},
    {"query_id": "q2", "doc_id": "B00K3TVJMQ", "grade": 1, "query": "skincare routine"},

    # Query 3: "study desk setup" intent-based, products are desks/stands/organizers
    {"query_id": "q3", "doc_id": "B08CS35J2T", "grade": 2, "query": "study desk setup"},
    {"query_id": "q3", "doc_id": "B09B3LFDXJ", "grade": 2, "query": "study desk setup"},
    {"query_id": "q3", "doc_id": "B07W58LMND", "grade": 1, "query": "study desk setup"},
    {"query_id": "q3", "doc_id": "B0CHYDX91L", "grade": 1, "query": "study desk setup"},

    # Query 4: "pet travel accessories" use-case grouping, products are carriers/crates/seats
    {"query_id": "q4", "doc_id": "B08R8FRW53", "grade": 2, "query": "pet travel accessories"},
    {"query_id": "q4", "doc_id": "B01MYUYX33", "grade": 2, "query": "pet travel accessories"},
    {"query_id": "q4", "doc_id": "B003C5RKE4", "grade": 2, "query": "pet travel accessories"},
    {"query_id": "q4", "doc_id": "B09GF8GBF6", "grade": 1, "query": "pet travel accessories"},
    {"query_id": "q4", "doc_id": "B0CP3LQSWM", "grade": 1, "query": "pet travel accessories"},
]
```

The mix is intentional: `q1` is a query that BM25 handles well (exact tokens in product titles), while `q2`, `q3`, and `q4` are intent-based queries where the user's intent is expressed as a concept rather than specific product keywords.

## Measuring BM25 baseline recall

First, set up the Elasticsearch client and index the raw text data:

```
import os
import json
import pandas as pd
import plotly.graph_objects as go
from elasticsearch import Elasticsearch, helpers
from dotenv import load_dotenv

load_dotenv()

es = Elasticsearch(
    os.getenv("ELASTICSEARCH_URL"),
    api_key=os.getenv("ELASTICSEARCH_API_KEY")
)

INDEX_NAME = "ecommerce-products"
```

Now build the `rank_eval` request for BM25. Each request in the list combines a query with its ratings:

```
judgments_df = pd.DataFrame(judgments)

bm25_requests = []
for query_id, query_text in (
    judgments_df[["query_id", "query"]].drop_duplicates().values
):
    relevant_docs = judgments_df[judgments_df["query_id"] == query_id]
    ratings = [
        {"_index": INDEX_NAME, "_id": row["doc_id"], "rating": row["grade"]}
        for _, row in relevant_docs.iterrows()
    ]

    bm25_requests.append({
        "id": query_id,
        "request": {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["title", "description"]
                }
            }
        },
        "ratings": ratings,
    })

bm25_eval = {
    "requests": bm25_requests,
    "metric": {"recall": {"k": 10, "relevant_rating_threshold": 1}},
}

bm25_result = es.rank_eval(index=INDEX_NAME, body=bm25_eval)
print("BM25 Recall@10:", bm25_result.body["metric_score"])
```

Result:

```
BM25 Recall@10: 0.43
```

`0.43` means that across all four queries, BM25 finds only 43% of the documents it should find. The shortfall is concentrated in the intent-based queries: "skincare routine" misses face serums and body oils because "routine" never appears in product titles, and "pet travel accessories" retrieves off-topic pet products while missing carriers and crates described in terms of portability and safety rather than "travel accessories."

This is our baseline. Now we have a number to beat.

## Adding vector search with Jina embeddings

[`Vector search`](https://www.elastic.co/docs/solutions/search/vector) encodes documents and queries as high-dimensional vectors, a type of vector made up of hundreds or thousands of numerical values, each encoding a specific feature of the data it represents. Documents with similar meaning end up close together in vector space, even if they share no words. "Gym equipment" and "dumbbell set" will be nearby because the concepts are related. I chose Elasticsearch as my vector database because it supports hybrid search, giving me both semantic understanding and keyword precision out of the box.

[EIS](https://www.elastic.co/docs/explore-analyze/elastic-inference/eis) includes out-of-the-box support for embedding models through its [inference API](https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-inference).

### Step 1: Using Jina embeddings v5 as an inference endpoint

```
INFERENCE_ENDPOINT_ID = ".jina-embeddings-v5-text-small"
```

If your cluster has GPU resources (available in Elastic Cloud and Elasticsearch 9.3+), the embeddings are generated on GPU, which is significantly faster than CPU inference and removes the performance trade-off that historically made vectors expensive at scale.

Why Jina embeddings specifically? [jina-embeddings-v5-text](https://www.elastic.co/search-labs/blog/jina-embeddings-v5-text) is a multilingual model (119+ languages) with a 32,000-token context window and support for task-specific [Low-Rank Adaptation (LoRA) adapters](https://arxiv.org/abs/2106.09685). It works well for short product descriptions out of the box. Read more about `jina-embeddings-v5-text` model [here](https://huggingface.co/jinaai/jina-embeddings-v5-text-small).

### Step 2: Create the index with a semantic field

```
index_mappings = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "copy_to": "semantic_field"},
            "description": {"type": "text", "copy_to": "semantic_field"},
            "brand": {"type": "keyword"},
            "category": {"type": "keyword"},
            "semantic_field": {
                "type": "semantic_text",
                "inference_id": INFERENCE_ENDPOINT_ID,
            },
        }
    }
}

if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=index_mappings)
    print(f"Created index: {INDEX_NAME}")
```

The [`semantic_text`](https://www.elastic.co/docs/solutions/search/semantic-search/semantic-search-semantic-text) field type is the key here. It’s a higher-level abstraction over [`dense_vector`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/dense-vector): You point it at an inference endpoint, and Elasticsearch takes care of generating embeddings automatically.

The [`copy_to`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/copy-to) property on `title` and `description` means content from both fields flows into [`semantic_field`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text) for embedding, so a single vector captures the full product representation.

### Step 3: Index the products

```
def bulk_index(products, index_name):
    actions = []
    for product in products:
        doc_id = product.get("_id")
        source = {k: v for k, v in product.items() if k != "_id"}
        action = {"_index": index_name, "_source": source}
        if doc_id:
            action["_id"] = doc_id
        actions.append(action)

    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    if failed:
        for error in failed:
            print(f"Error: {error}")
    else:
        print(f"Successfully indexed {success} documents")

bulk_index(products, INDEX_NAME)
```

At index time, Elasticsearch calls the inference endpoint for each document and stores the resulting embedding in `semantic_field`. No extra code on your side.

## Hybrid search: Combining BM25 and vectors with RRF

Adding vectors improves recall, but using vectors alone risks losing precision on exact-match queries; "running shoes" should still rank verbatim matches first. Hybrid search retains the lexical component specifically to preserve that precision.

Hybrid search with [Reciprocal Rank Fusion](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion) (RRF) keeps the best of both:

* BM25 handles exact and near-exact queries with high precision.
* Semantic search handles intent-based and multilingual queries with high recall.
* RRF combines the two ranked lists into a single ranking.

The RRF formula assigns each document a score based on its rank in each result list:

```
score = sum(1 / (rank_constant + rank))
```

A document that ranks highly in both lists gets a higher combined score. The `rank_constant` controls how much weight lower-ranked documents receive.

```
hybrid_requests = []

for query_id, query_text in (
    judgments_df[["query_id", "query"]].drop_duplicates().values
):
    relevant_docs = judgments_df[judgments_df["query_id"] == query_id]
    ratings = [
        {"_index": INDEX_NAME, "_id": row["doc_id"], "rating": row["grade"]}
        for _, row in relevant_docs.iterrows()
    ]

    hybrid_requests.append({
        "id": query_id,
        "request": {
            "retriever": {
                "rrf": {
                    "retrievers": [
                        {
                            "standard": {
                                "query": {
                                    "multi_match": {
                                        "query": query_text,
                                        "fields": ["title", "description"],
                                    }
                                }
                            }
                        },
                        {
                            "standard": {
                                "query": {
                                    "match": {
                                        "semantic_field": {"query": query_text}
                                    }
                                }
                            }
                        },
                    ],
                    "rank_window_size": 50,
                    "rank_constant": 5,
                }
            }
        },
        "ratings": ratings,
    })

hybrid_eval = {
    "requests": hybrid_requests,
    "metric": {"recall": {"k": 10, "relevant_rating_threshold": 1}},
}

hybrid_result = es.rank_eval(index=INDEX_NAME, body=hybrid_eval)
print("Hybrid Recall@10:", hybrid_result.body["metric_score"])
```

Result:

```
Hybrid Recall@10: 0.75
```

Hybrid improves substantially over BM25 (`0.43`) and preserves precision for exact-match queries like "running shoes."

## Results: Before and after

Here’s the full comparison across all three approaches:

```
methods = {
    "BM25 (Lexical)": bm25_requests,
    "Hybrid (BM25 + Vectors)": hybrid_requests,
}

recall_metric = {"recall": {"k": 10, "relevant_rating_threshold": 1}}

comparison_data = []
for method_name, requests in methods.items():
    result = es.rank_eval(
        index=INDEX_NAME,
        body={"requests": requests, "metric": recall_metric}
    )
    comparison_data.append({
        "method": method_name,
        "recall@10": result.body["metric_score"]
    })

comparison_df = pd.DataFrame(comparison_data)
print(comparison_df.to_string(index=False))
```

Result:

| Method | Recall@10 |
| --- | --- |
| BM25 (Lexical) | 0.43 |
| Hybrid (BM25 + Vectors) | 0.75 |

![Bar chart comparing Recall@10 between BM25 lexical search and hybrid search combining BM25 with vectors, showing hybrid search achieving significantly higher recall.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt5a1d72b57056fe64/6a170a71c1e8a56c58f882ab/e49f6c10516b0a48a0ad75962c6590ee07311407-700x500.png)

Breaking it down by query:

![Grouped bar chart comparing Recall@10 between BM25 lexical and hybrid search across four product queries, showing hybrid search consistently outperforming lexical search for each query.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt871347f754c866d0/6a170a73839dfa40abdcfeb4/40e36dcb7b34cbf4649c512bcb60cef60f1778a6-700x500.png)

## Conclusion

Throughout this post, we saw that BM25 lexical search is reliable when users type exact queries, but it loses recall when they search by intent rather than keywords. Using `rank_eval`, we established a reproducible baseline to measure that gap with real numbers. From there, we added a `semantic_text` field powered by Jina embeddings and ran the evaluation again. The result: Hybrid search improved recall from `0.43` to `0.75` while preserving precision on exact-match queries, though the actual margin will depend on your query mix.

The pattern scales beyond this example: Collect judgments from your users' actual queries, run `rank_eval` as a baseline, add `semantic_text`, and measure again. You'll know exactly what improved and by how much.

## Next steps

* Dive deeper into recall and vector search: [Recall and vector search quantization](https://www.elastic.co/search-labs/blog/recall-vector-search-quantization) by Jeff Vestal
* Add reranking for even better precision on the top results
* Explore [Elasticsearch hybrid search documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html)
* Read more about the [`rank_eval`](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html) [API](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html)

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9dd95ca3f3bd2004/6a17f8153e9e457308ba165d/69d9c14dac7e255e3df6c3aa15c84ac6564c3401-720x420.jpg)

[Hybrid Search](/search-labs/blog/category/hybrid-search)

### Built with Elastic: Hybrid search for Cypris – the world’s largest innovation database

May 06, 2025|[Elastic Team](/search-labs/author/the-elastic-team)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt3382265814939417/6a170df3a929cf1246ae0a61/fceada10b0c09d6a4a372f137bb3040e1ff41fbf-1600x895.png)

[ES|QL](/search-labs/blog/category/esql)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### Hybrid search and multistage retrieval in ES|QL

January 08, 2026|[Ioana](/search-labs/author/ioana-alina-tagirta)|[+2](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt360319cdeac21a74/6a6119f81b1d49b36a6f1823/8aaf734953fe5ae677062bf06aef7352f186657c-1280x720.png)

[Agentic AI](/search-labs/blog/category/agentic-ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)[Relevance](/search-labs/blog/category/relevance)

### AI shopping agents: Why context comes before the query

July 20, 2026|[Matthew Adams](/search-labs/author/matthew-adams)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt63218799e944e16d/6a1710ef6f7f04ee68914952/93d8e0d84fb4cfbf5e51df85df7ec2e600d9dcc7-1088x607.png)

[Hybrid Search](/search-labs/blog/category/hybrid-search)[Integrations](/search-labs/blog/category/integrations)[Java](/search-labs/blog/category/java-programming)

### Hybrid search with Java: LangChain4j Elasticsearch integration

March 11, 2026|[Laura Trotta](/search-labs/author/laura-trotta)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltc58be329ffebcd60/6a17043e47d49c0bc62d88ab/70fb0ff949f6db9ac9b8a28ecb4329ab915ebf46-720x420.png)

[AI](/search-labs/blog/category/ai)[Hybrid Search](/search-labs/blog/category/hybrid-search)

### Entity resolution with Elasticsearch, part 4: The ultimate challenge

March 13, 2026|[Jessica Moszkowicz](/search-labs/author/jessica-moszkowicz)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter