---
title: 'Elasticsearch hybrid search'
company: Elastic
tag: 召回
date: 2025-02-17
url: https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Elasticsearch hybrid search

Learn about hybrid search, the types of hybrid search queries Elasticsearch supports, and how to craft them.

February 17, 2025

[Valentin Crettaz](/search-labs/author/valentin-crettaz)

[Vector Database](/search-labs/blog/category/vector-database)[Hybrid Search](/search-labs/blog/category/hybrid-search)

Part of the series:

[Vector search introduction and implementation](/search-labs/blog/series/vector-search-introduction-and-implementation)

In this series

Share

This article is the last one in a series of three that dives into the intricacies of vector search (aka semantic search) and how it is implemented in Elasticsearch.

The [first part](https://www.elastic.co/search-labs/blog/introduction-to-vector-search) was focused on providing a general introduction to the basics of embeddings (aka vectors) and how vector search works under the hood.

Armed with all the vector search knowledge learned in the first article, the [second article](https://www.elastic.co/search-labs/blog/vector-search-set-up-elasticsearch) guided you through the meanders of how to set up vector search and execute k-NN searches in Elasticsearch.

In this third and last part, we will leverage what we have learned in the first two parts and build upon that knowledge by delving into how to craft powerful hybrid search queries in Elasticsearch.

## The need for hybrid search

Before diving into the realm of hybrid search, let’s do a quick refresh of what we learned in the [first article](https://www.elastic.co/search-labs/blog/introduction-to-vector-search) of this series regarding how lexical and semantic search differ and how they can complement each other.

To sum it up very briefly, lexical search is great when you have control over your structured data and your users are more or less clear on what they are searching for. Semantic search, however, provides great support when you need to make [unstructured data](https://www.elastic.co/what-is/unstructured-data) searchable and your users don’t really know exactly what they are searching for. It would be fantastic if there was a way to combine both in order to squeeze as much substance out of each one as possible. Enter hybrid search!

In a way, we can see hybrid search as some sort of “sum” of lexical search and semantic search. However, when done right, hybrid search can be much better than just the sum of those parts, yielding far better results than either lexical or semantic search would do on their own.

Running a hybrid search query usually boils down to sending a mix of at least one lexical search query and one semantic search query and then merging the results of both. The lexical search results are scored by a similarity algorithm, such as [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) or [TF-IDF](https://en.wikipedia.org/wiki/Tf%E2%80%93idf), whose score scale is usually unbounded as the max score depends on the number and frequency of terms stored in the inverted index. In contrast, semantic search results can be scored within a closed interval, depending on the similarity function that is being used (e.g., [0; 2] for cosine similarity).

In order to merge the lexical and semantic search results of a hybrid search query, both result sets need to be fused in a way that maintains the relative relevance of the retrieved documents, which is a complex problem to solve. Luckily, there are [several existing methods](https://arxiv.org/abs/2210.11934) that can be utilized; two very common ones are **Convex Combination** (CC) and **Reciprocal Rank Fusion** (RRF).

Basically, Convex Combination, also called Linear Combination, seeks to combine the normalized score of lexical search results and semantic search results with respective weights and β\betaβ (where 0≤α,β0 \leq \alpha, \beta0≤α,β), such that:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt60d98d5886c5c0c1/6a17f38caf47b64c6dcde0cd/93cc63a6bcd759b2d217162b25c7ef389fbcce05-866x68.png)

CC can be seen as a weighted average of the lexical and semantic scores Weights between 0 and 1 are used to deboost the related query, while weights greater than 1 are used to boost it.

RRF, however, doesn’t require any score calibration or normalization and simply scores the documents according to their rank in the result set, using the following formula, where k is an arbitrary constant meant to adjust the importance of lowly ranked documents:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt125d0bdacbe5b587/6a17f38e4b055d2fde432334/2771584645207e423b16186f7314349f5f474062-656x78.png)

Both CC and RRF have their pros and cons as highlighted in Table 1, below:

*Table 1: Pros and cons of CC and RRF*

|  | Convex Combination | Reciprocal Rank Fusion |
| --- | --- | --- |
| Pros | Good calibration of weights makes CC more effective than RRF | Doesn’t require any calibration, fully unsupervised and there’s no need to know min/max scores |
| Cons | Requires a good calibration of the weights and the optimal weights are specific to each data set | Not trivial to tune the value of k and the ranking quality can be affected by increasing result set size |

It is worth noting that not everyone agrees on these pros and cons depending on the assumptions being made and the data sets on which they have been tested. A good summary would be that RRF yields slightly less accurate scores than CC but has the big advantage of being “plug & play” and can be used without having to fine-tune the weights with a labeled set of queries.

Elastic decided to support both the [CC](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#_combine_approximate_knn_with_other_features) and [RRF](https://www.elastic.co/guide/en/elasticsearch/reference/8.8/release-highlights.html#add_support_for_reciprocal_rank_fusion_rrf_to_search_api) approaches. We’ll see how this is carried out later in this article. If you are interested in learning more about the rationale behind that choice, you can read this great [article](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid) from the Elastic blog and also check out this excellent [talk on RRF](https://haystackconf.com/eu2023/talk-2/) presented at Haystack 2023 by Elastician Philipp Krenn.

## Timeline

After enabling brute-force kNN search on dense vectors in 7.0 back in 2019, Elasticsearch started supporting approximate nearest neighbors (ANN) search in February 2022 with the 8.0 release and hybrid search support came right behind with the 8.4 release in August 2022. Figure 1, below, shows the Elasticsearch timeline for bringing hybrid search to market:

![Hybrid search timeline for Elasticsearch](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt90662126c783adf9/6a17f38f42022960d529f720/b0a9917e83a62d305818855cb52741350c02415f-1018x469.png)

*Figure 1: Hybrid search timeline for Elasticsearch*

## The anatomy of hybrid search in Elasticsearch

As we’ve briefly hinted at in our [previous article](https://www.elastic.co/search-labs/blog/vector-search-set-up-elasticsearch), vector search support in Elasticsearch has been made possible by leveraging **dense** vector models (hence the `dense_vector` field type), which produce vectors that usually contain essentially non-zero values and represent the meaning of unstructured data in a multi-dimensional space.

However, dense models are not the only way of performing semantic search. Elasticsearch also provides an alternative way that uses **sparse** vector models. Elastic created a sparse NLP vector model called [**Elastic Learned Sparse EncodeR**](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html), or ELSER for short, which is an out-of-domain (i.e., not trained on a specific domain) sparse vector model that does not require any fine-tuning. It was pre-trained on a vocabulary of approximately [30,000 terms](https://ml-models.elastic.co/elser_model_1.vocab.json), and as it’s a sparse model most of the vector values (i.e., more than 99.9%) are zeros.

The way it works is pretty simple. At indexing time, the sparse vectors containing term/weight pairs are generated using the `inference` ingest processor and stored in fields of type `sparse_vector`, which is the sparse counterpart to the `dense_vector` field type. At query time, a specific DSL query also called `sparse_vector` replaces the original query terms with terms available in the ELSER model vocabulary that are known to be the most similar to them given their weights.

### Sparse or dense?

Before heading over to hybrid search queries, we would like to briefly highlight the [differences between sparse and dense models](https://www.elastic.co/search-labs/lexical-ai-powered-search-elastic-vector-database#dense-versus-sparse-vector-retrieval). Figure 2, below, shows how the piece of text *“the quick brown fox”* is encoded by each model.

In the sparse case, the four original terms are *expanded* into 30 weighted terms that are closely or distantly related to them. The higher the weight of the expanded term, the more related it is to the original term. Since the ELSER vocabulary contains more than 30,000 terms, it means that the vector representing *“the quick brown fox”* has as many dimensions and contains only ~0.1% of the non-zero values (i.e., ~30 / 30,000), hence why we call these models sparse.

![Comparing sparse and dense model encoding for hybrid search](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blta21b1ba403767ca3/6a17f3913e03d7c5d34f2db5/0e4ae7327e20cae4429cd8b3eef1aed15c6f4ff9-1600x662.png)

*Figure 2: Comparing sparse and dense model encoding*

In the dense case, *“the quick brown fox”* is encoded into a much smaller embeddings vector that captures the semantic meaning of the text. Each of the 384 vector elements contains a non-zero value that represents the similarity between the piece of text and each of the dimensions. Note that the names we have given to dimensions (i.e., `is_mouse`, `is_brown`, etc.) are purely fictional, and their purpose is just to give a concrete description of the values.

Another important difference is that sparse vectors are queried via the *inverted index* (yes, like lexical search), whereas as we have seen in previous articles, dense vectors are indexed in specific graph-based or cluster-based data structures that can be searched using *approximate nearest neighbors (ANN) algorithms*.

We won’t go any further into the details of how ELSER came to be, but if you’re interested in understanding how that model was born, we recommend you check out [this article](https://www.elastic.co/search-labs/blog/introducing-elastic-learned-sparse-encoder-elser) from the Elastic Search Labs, which explains in detail the thought process that led Elastic to develop it. If you are thinking about evaluating ELSER, it might be worth checking Elastic’s [relevance workbench](https://www.elastic.co/demo-gallery/relevance-workbench), which demonstrates how ELSER compares to a normal BM25 lexical search. We are also not going to dive into the process of downloading and deploying the ELSER model in this article, but you can take a moment and turn to the [official documentation](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html#download-deploy-elser) that explains very well how to do it.

### Hybrid search support

Whether you are going to use dense or sparse retrieval, Elastic provides hybrid search support for both model types. The first type is a **mix** of a lexical search query specified in the `query` search option and a vector search query (or an array thereof) specified in the `knn` search option. The second one introduces a new search option called `retriever` (introduced in 8.14 and GA in 8.16) which also contains an array of search queries that can be of lexical (e.g., `match`) or semantic (e.g., `sparse_vector`) nature.

If all this feels somewhat abstract to you, don’t worry, as we will shortly dive into the details to show how hybrid searches work in practice and what benefits they provide. In this article, we are going to focus on the second option using retrievers.

#### Hybrid search with dense models

Hybrid search using retrievers basically boils down to running a lexical search query mixed with an [approximate k-NN search](https://www.elastic.co/search-labs/blog/vector-search-set-up-elasticsearch#approximate-k-nn-search) in order to improve relevance. Such a hybrid search query is shown below:

```
POST my-index/_search
{
  "size": 10,
  "_source": false,
  "fields": [ "price" ],
  "retriever": {
    "rrf": { 
      "retrievers": [ 
        {
          "standard": { 
            "query": {
              "match": {
                "text-field": "fox"
              }
            }
          }
        },
        {
          "knn": { 
            "field": "title_vector",
            "query_vector": [0.1, 3.2, 2.1],
            "k": 5,
            "num_candidates": 100
          }
        }
      ]
    }
  }
}
```

As we can see above, a hybrid search query simply leverages the `rrf` retriever that **combines** a lexical search query (e.g., a `match` query) made with a `standard` retriever and a vector search query specified in the `knn` retriever. What this query does is first retrieve the top five vector matches at the global level, then combine them with the lexical matches, and finally return the ten best matching hits. The `rrf` retriever uses [RRF ranking](https://www.elastic.co/guide/en/elasticsearch/reference/current/rrf.html) in order to combine vector and lexical matches.

The RRF ranking formula can be further parametrized by two variables called `rank_constant` and `rank_window_size` (defaults to `size`) that can be specified in the `rrf` retriever section, as shown below:

```
POST my-index/_search
{
  "size": 10,
  "_source": false,
  "fields": [ "price" ],
  "retriever": {
    "rrf": { 
      "retrievers": [ 
        ...same as above...
      ],
      "rank_constant": 60, 
      "rank_window_size": 100
    }
  }
}
```

This query runs the same way as the previous one, except that `rank\_window\_size` documents (instead of only 10) are retrieved from the vector and lexical queries and then ranked by RRF. Finally, the top documents ranked from 1 to `size` (e.g., 10) are then returned in the result set.

The last thing to note about this hybrid query type is that RRF ranking requires a commercial license (Enterprise), but if you don’t have one, you can still leverage hybrid searches with CC scoring or by using a trial license that allows you to enjoy the full feature set for one month.

#### Hybrid search with sparse models

The second hybrid search type for querying sparse models works exactly the same way as for dense vectors.. Below, we can see what such a hybrid query looks like:

```
POST my-index/_search
{
  "_source": false,
  "fields": [ "text-field" ],
  "retriever": {
    "rrf": { 
      "retrievers": [ 
        {
          "standard": { 
            "query": {
              "match": {
                "text-field": "fox"
              }
            }
          }
        },
        {
          "standard": { 
            "query": {
              "sparse_vector": {
                "field": "ml.tokens",
                "inference_id": ".elser_model_1",
                "query": "a quick brown fox jumps over a lazy dog"
              }
            }
          }
        }
      ]
    }
  }
}
```

In the above query, we can see that the `retrievers` array contains one lexical `match` query as well as one semantic `sparse_vector` query that works on the ELSER sparse model that we introduced earlier.

#### Hybrid search with dense and sparse models

So far, we have seen two different ways of running a hybrid search, depending on whether a dense or sparse vector space was being searched. At this point, you might wonder whether we can mix both dense and sparse data inside the same index, and you’ll be pleased to learn that it is indeed possible. One concrete application could be that you need to search both a dense vector space with images and a sparse vector space with textual descriptions of those images. Such a query would look like this where we combine a `standard` retriever with a `knn` one:

```
POST my-index/_search
{
  "_source": false,
  "fields": [ "text-field" ],
  "retriever": {
    "rrf": { 
      "retrievers": [ 
        {
          "knn": {
            "field": "image-vector",
            "query_vector": [0.1, 3.2, ..., 2.1],
            "k": 5,
            "num_candidates": 100
          }
        },
        {
          "standard": { 
            "query": {
              "sparse_vector": {
                "field": "ml.tokens",
                "inference_id": ".elser_model_1",
                "query": "a quick brown fox jumps over a lazy dog"
              }
            }
          }
        }
      ]
    }
  }
}
```

In the above payload, we can see a `sparse_vector` query searching for image descriptions within the ELSER sparse vector space, and in the `knn` retriever a vector search query searching for image embeddings (e.g., “brown fox” represented as an embedding vector) in a dense vector space. In addition, we leveraged RRF by using the `rrf` retriever.

You can even add another lexical search query to the mix using another `standard` retriever, and it would look like this:

```
POST my-index/_search
{
  "_source": false,
  "fields": [ "text-field" ],
  "retriever": {
    "rrf": { 
      "retrievers": [ 
        {
          "knn": {
            "field": "image-vector",
            "query_vector": [0.1, 3.2, ..., 2.1],
            "k": 5,
            "num_candidates": 100
          }
        },
        {
          "standard": { 
            "query": {
              "match": {
                "text-field": "brown fox"
              }
            }
          }
        },
        {
          "standard": { 
            "query": {
              "sparse_vector": {
                "field": "ml.tokens",
                "inference_id": ".elser_model_1",
                "query": "a quick brown fox jumps over a lazy dog"
              }
            }
          }
        }
      ]
    }
  }
}
```

The above payload highlights that we can leverage every possible way to specify a hybrid query containing a lexical search query, a vector search query, and a semantic search query.

#### Limitations

The main limitation to be aware of when evaluating the ELSER sparse model is that it only supports up to 512 tokens when running text inference. So, if your data contains longer text excerpts that you need to be fully searchable, you are left with two options: a) use another model that supports longer text, b) split your text into smaller segments, or 3) if you are on 8.15 or above, you can leverage the `semantic_text` field type, which handles automatic chunking.

### Optimizations

It is undeniable that vectors, whether sparse or dense, can get quite long, from a few dozen to a few thousand dimensions depending on the inference model that you’re using. Also, whether you’re running a text inference on a small sentence containing just a few words or a large body of text, the generated embeddings vector representing the meaning will always have as many dimensions as configured in the model you’re using. As a result, these vectors can take quite some space in your documents and, hence, on your disk.

The most obvious optimization to cater to this issue is to configure your index mapping to remove the vector fields (i.e., both `dense_vector` and `sparse_vector`) from your source documents. By doing so, the vector values would still be indexed and searchable, but they would not be part of your source documents anymore, thus reducing their size substantially. It’s pretty simple to achieve this by configuring your mapping to exclude the vector fields from the `_source`, as shown in the code below:

```
PUT my-index
{
  "mappings": {
    "_source": {
      "excludes": [
        "text_embedding.predicted_value",
        "ml.tokens"
      ]
    },
    "properties": {
      "text": {
        "type": "text"
      },
      "ml": {
        "properties": {
          "tokens": {
            "type": "rank_features"
          }
        }
      },
      "text_embedding": {
        "properties": {
          "predicted_value": {
            "type": "dense_vector",
            "dims": 384,
            "index": true,
            "similarity": "cosine"
          }
        }
      }
    }
  }
}
```

In order to show you some concrete numbers, we have run a quick experiment. We have loaded an index with the msmarco-passagetest2019-top1000 data set, which is a subset of the [Microsoft MARCO Passage Ranking](https://microsoft.github.io/MSMARCO-Passage-Ranking/) full data set. The 60 MB TSV file contains 182,469 text passages.

Next, we have created another index containing the raw text and the embeddings vectors (dense) generated from the [msmarco-MiniLM-L-12-v3](https://huggingface.co/sentence-transformers/msmarco-MiniLM-L-12-v3) sentence-transformer model available from Hugging Face. We’ve then repeated the same experiment, but this time configuring the mapping to exclude the dense vector from the source documents.

We’ve also run the same test with the ELSER sparse model, one time by storing the `sparse_vector` field inside the documents and one time by excluding them. Table 2, below, shows the size of each resulting index, whose names are self-explanatory. We can see that by excluding dense vector fields from the source, the index size is divided by 3 and by almost 3.5 in the rank feature case.

| Index | Size (in MB) |
| --- | --- |
| index-with-dense-vector-in-source | 376 |
| index-without-dense-vector-in-source | 119 |
| index-with-sparse\_vector-in-source | 1,300 |
| index-without-sparse\_vector-in-source | 387 |

Admittedly, your mileage may vary, these figures are only indicative and will heavily depend on the nature and size of the unstructured data you will be indexing, as well as the dense or sparse models you are going to choose.

A last note of caution worth mentioning concerning this optimization is that if you decide to exclude your vectors from the source, you will not be able to use your index as a source index to be reindexed into another one because your embedding vectors will not be available anymore. However, since the index still contains the raw text data, you can use the original ingest pipeline featuring the `inference` processor to regenerate the embeddings vectors.

## Let’s conclude

In this final article of our series on vector search, we have presented the different types of hybrid search queries supported by Elasticsearch. One option is to use a combination of lexical search (e.g., `query`) and vector search (e.g., `knn`); the other is to leverage the newly introduced `retriever` search option with `sparse_vector` queries.

We first did a quick recap of the many advantages of being able to fuse lexical and semantic search results in order to increase accuracy. Along the way, we reviewed two different methods of fusing lexical and semantic search results, namely Convex Combination (CC) and Reciprocal Rank Fusion (RRF), and looked at their respective pros and cons.

Then, using some illustrative examples, we showed how Elasticsearch provides hybrid search support for sparse and dense vector spaces alike, using both Convex Combination and Reciprocal Rank Fusion as scoring and ranking methods. We also briefly introduced the Elastic Learned Sparse EncodeR model (ELSER), which is their first attempt at providing an out-of-domain sparse model built on a 30,000 tokens vocabulary.

Finally, we concluded by pointing out one limitation of the ELSER model, and we also explained a few ways to optimize your future hybrid search implementations.

If you like what you’re reading, make sure to check out the other parts of this series:

* [Part 1: A Quick Introduction to Vector Search](https://www.elastic.co/search-labs/blog/introduction-to-vector-search)
* [Part 2: How to Set Up Vector Search in Elasticsearch](https://www.elastic.co/search-labs/blog/vector-search-set-up-elasticsearch)

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