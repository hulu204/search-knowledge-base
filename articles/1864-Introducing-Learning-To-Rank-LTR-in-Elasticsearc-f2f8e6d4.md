---
title: 'Introducing Learning To Rank (LTR) in Elasticsearch'
company: Elastic
tag: 排序
date: 2024-07-15
url: https://www.elastic.co/search-labs/blog/elasticsearch-learning-to-rank-introduction
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Introducing Learning To Rank (LTR) in Elasticsearch

Discover how Learning To Rank (LTR) can help you to improve your search ranking and how to implement it in Elasticsearch.

July 15, 2024

[Aurélien Foucret](/search-labs/author/aurelien-foucret)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

Starting with Elasticsearch 8.13, we provide an implementation of [Learning To Rank](https://www.elastic.co/guide/en/elasticsearch/reference/current/learning-to-rank.html) (LTR) natively integrated into Elasticsearch. LTR uses a trained machine learning (ML) model to build a ranking function for your search engine. Typically, the model is used as a second stage re-ranker, to improve the relevance of search results returned by a simpler, first stage retrieval algorithm.

This blog post will explain how this new feature can help in improving your document ranking in text search and how to implement it in Elasticsearch.

Whether you are trying to optimize an eCommerce search, build the best context for a Retrieval Augmented Generation(RAG) application or craft a question answering based search on millions of academic papers, you have probably realized how challenging it can be to accurately optimize document ranking in a search engine. That's where Learning to Rank comes in.

## Understanding relevance features and how to build a scoring function

Relevance features are the signals to determine how well a document matches a user's query or interest, all of which impact [search relevance](https://www.elastic.co/what-is/search-relevance). These features can vary significantly depending on the context, but they generally fall into several categories. Let’s take a look at some common relevance features used across different domains:

* **Text Relevance Scores** (e.g., [BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables), TF-IDF): Scores derived from text matching algorithms that measure the similarity of document content to the search query. These scores can be obtained from Elasticsearch.
* **Document Properties** (e.g., price of a product, publication date): Features that can be extracted directly from the stored document.
* **Popularity Metrics** (e.g., click-through rate, views): Indicators of how popular or frequently accessed a document is. Popularity metrics can be obtained with [Search analytics](https://www.elastic.co/enterprise-search/search-analytics) tools, of which Elasticsearch provides out-of-the-box.

The scoring function combines these features to produce a final relevance score for each document. Documents with higher scores are ranked higher in search results.

When using the Elasticsearch Query DSL, you are implicitly writing a scoring function that weights relevance features and ultimately defines your search relevance

## Scoring in the Elasticsearch Query DSL

Consider the following example query:

```
{
  "query": {
    "function_score": {
      "query": {
        "multi_match": {
          "query": "the quick brown fox",
          "fields": ["title^10", "content"]
        }
      },
      "field_value_factor": {
        "field": "monthly_views",
        "modifier": "log1p"
      }
    }
  }
}
```

This query translates into the following scoring function:

```
score = 10 x title_bm25_score + content_bm25_score + log(1+ monthly_views)
```

While this approach works well, it has a few limitations:

* **Weights are estimated**: The weights assigned to each feature are often based on heuristics or intuition. These guesses may not accurately reflect the true importance of each feature in determining relevance.
* **Uniform Weights Across Documents**: Manually assigned weights apply uniformly to all documents, ignoring potential interactions between features and how their importance might vary across different queries or document types. For instance, the relevance of recency might be more significant for news articles but less so for academic papers.

As the number of features and documents increases, these limitations become more pronounced, making it increasingly challenging to determine accurate weights. Ultimately, the chosen weights become a compromise, potentially leading to suboptimal ranking in many scenarios.

A compelling alternative is to replace the scoring function that uses manual weights by a ML-based model that computes the score using relevance features.

## Hello Learning To Rank (LTR)!

[LambdaMART](https://www.microsoft.com/en-us/research/uploads/prod/2016/02/MSR-TR-2010-82.pdf) is a popular and effective LTR technique that uses gradient boosting decision trees [(GBDT](https://en.wikipedia.org/wiki/Gradient_boosting#Gradient_tree_boosting)) to learn the optimal scoring function from a judgment list.

The judgment list is a dataset that contains pairs of queries and documents, along with their corresponding relevance labels or grades. Relevance labels are typically either binary, (e.g. relevant/irrelevant) or graded (e.g between 0 for completely irrelevant and 4 for highly relevant). Judgment lists can be created manually by humans or be generated from user engagement data, such as clicks or conversions.

The example below uses a graded relevance judgment.

![judment list example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt36917248d619fee7/6a170e0b66c4f9484cf8c0d0/297f931b6b1565aaf4b7de9648fa73f145337c45-798x560.png)

LambdaMART treats the ranking problem as a regression task using a decision tree where the inner nodes of the tree are conditions over the relevance features, and the leaves are the predicted scores.

![decision tree example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0c683e8ebff2a960/6a170e0d4a531be33636a9e7/07ce40d7902e8b7cbd6246a369c7f36191c18937-1440x864.png)

LambdaMART uses a gradient boosted tree approach, and in the training process it builds multiple decision trees where each tree corrects errors of its predecessors. This process aims to optimize a ranking metric like NDCG, based on examples from the judgment list. The final model is a weighted sum of individual trees.

[XGBoost](https://xgboost.readthedocs.io/en/stable/) is a well known library that provides an [implementation](https://xgboost.readthedocs.io/en/stable/tutorials/learning_to_rank.html) of LambdaMART, making it a popular choice to implement ranking based on gradient boosting decision trees.

## Getting started with LTR in Elasticsearch

Starting with version 8.13, [Learning To Rank](https://www.elastic.co/guide/en/elasticsearch/reference/current/learning-to-rank.html) is integrated directly into Elasticsearch and associated tooling as a technical preview feature.

### Train and deploy an LTR model to Elasticsearch

[Eland](https://eland.readthedocs.io/en/v8.13.1/) is our Python client and toolkit for DataFrames and machine learning in Elasticsearch. Eland is compatible with most of the standard Python data science tools like Pandas, scikit-learn and XGBoost.

We highly recommend using it to train and deploy your LTR XGBoost model, as it provides features to simplify this process:

1. The first step of the training process is to define the relevant features of the LTR model. Using the Python code below, you can specify the relevant features using the Elasticsearch Query DSL.

```
from eland.ml.ltr import LTRModelConfig, QueryFeatureExtractor

feature_extractors=[
    # We want to use the score of the match query for the fields title and content as a feature:
    QueryFeatureExtractor(
        feature_name="title_bm25_score",
        query={"match": {"title": "{{query_text}}"}}
    ),
    QueryFeatureExtractor(
        feature_name="content_bm25_score",
        query={"match": {"content": "{{query_text}}"}}
    ),
    # We can use a script_score query to get the value
    # of the field popularity directly as a feature
    QueryFeatureExtractor(
        feature_name="popularity",
        query={
            "script_score": {
                "query": {"exists": {"field": "popularity"}},
                "script": {"source": "return doc['popularity'].value;"},
            }
        },
    )
]

ltr_config = LTRModelConfig(feature_extractors)
```

1. The second step of the process is to build your training dataset. At this step you will compute and add relevance features for each rows of your judgment list:

![judgment kist with features example](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt1a1668945beda7f7/6a170e0e8b73cb45ff18a0c0/9648cf6585f91bba82502548bf48092c5d3ce251-1360x718.png)

To help you with this task, Eland provides the FeatureLogger class:

```
from eland.ml.ltr import FeatureLogger

feature_logger = FeatureLogger(es_client, MOVIE_INDEX, ltr_config)

feature_logger.extract_features(
    query_params={"query": "foo"},
    doc_ids=["doc-1", "doc-2"]
)
```

1. When the training dataset is built, the model is trained very easily (as also shown in the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb#Building-the-training-dataset)):

```
from xgboost import XGBRanker
from sklearn.model_selection import GroupShuffleSplit

# Create the ranker model:
ranker = XGBRanker(
    objective="rank:ndcg",
    eval_metric=["ndcg@10"],
    early_stopping_rounds=20,
)

# Shaping training and eval data in the expected format.
X = judgments_with_features[ltr_config.feature_names]
y = judgments_with_features["grade"]
groups = judgments_with_features["query_id"]

# Split the dataset in two parts respectively used for training and evaluation of the model.
group_preserving_splitter = GroupShuffleSplit(n_splits=1, train_size=0.7).split(
    X, y, groups
)
train_idx, eval_idx = next(group_preserving_splitter)

train_features, eval_features = X.loc[train_idx], X.loc[eval_idx]
train_target, eval_target = y.loc[train_idx], y.loc[eval_idx]
train_query_groups, eval_query_groups = groups.loc[train_idx], groups.loc[eval_idx]

# Training the model
ranker.fit(
    X=train_features,
    y=train_target,
    group=train_query_groups.value_counts().sort_index().values,
    eval_set=[(eval_features, eval_target)],
    eval_group=[eval_query_groups.value_counts().sort_index().values],
    verbose=True,
)
```

1. Deploy your model to Elasticsearch once the training process is complete:

```
from eland.ml import MLModel

LEARNING_TO_RANK_MODEL_ID = "ltr-model-xgboost"

MLModel.import_ltr_model(
    es_client=es_client,
    model=trained_model,
    model_id=LEARNING_TO_RANK_MODEL_ID,
    ltr_model_config=ltr_config,
    es_if_exists="replace",
)
```

To learn more about how our tooling can help you to train and deploy the model, check out this end-to-end [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb#Building-the-training-dataset).

### Use your LTR model as a rescorer in Elasticsearch

Once you deploy your model in Elasticsearch, you can enhance your search results through a [rescorer](https://www.elastic.co/guide/en/elasticsearch/reference/8.13/filter-search-results.html#rescore). The rescorer allows you to refine a first-pass ranking of search results using the more sophisticated scoring provided by your LTR model:

```
GET my-index/_search
{
  "query": {
    "multi_match": {
      "fields": ["title", "content"],
      "query": "the quick brown fox"
    }
  },
  "rescore": {
    "learning_to_rank": {
      "model_id": "ltr-model-xgboost",
      "params": {
        "query_text": "the quick brown fox"
      }
    },
    "window_size": 100
  }
}
```

In this example:

* First-pass query: `The multi_match` query retrieves documents that match the query `the quick brown fox` in the title and content fields. This query is designed to be fast and capture a large set of potentially relevant documents.
* Rescore phase: The `learning_to_rank` rescorer refines the top results from the first-pass query using the LTR model.

  + `model_id`: Specifies the ID of the deployed LTR model (`ltr-model-xgboost` in our example).
  + `params`: Provides any parameters required by the LTR model to extract features relevant to the query. Here `query_text` allows you to specify the query issued by the user that some of our features extractors expect.
  + `window_size`: Defines the number of top documents from the search results issued by the first-pass query to be rescored. In this example, the top 100 documents will be rescored.

By integrating LTR as a two stage retrieval process, you can can optimize both performance and accuracy of your retrieval process by combining:

* Speed of Traditional Search: The first-pass query retrieves a large number of documents with a broad match very quickly, ensuring fast response times.
* Precision of Machine Learning Models: The LTR model is applied only to the top results, refining their ranking to ensure optimal relevance. This targeted application of the model enhances precision without compromising overall performance.

## Try LTR yourself!?

Whether you are struggling to configure search relevance for an eCommerce platform, aiming to improve the context relevance of your RAG application, or you are simply curious about enhancing your existing search engine's performance, you should consider LTR seriously.

To start your journey with implementing LTR, make sure to visit our [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb#Building-the-training-dataset) detailing how to train, deploy, and use an LTR model in Elasticsearch and to read our [documentation](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb#Building-the-training-dataset). Let us know if you built anything based on this blog post or if you have questions on our [Discuss forums](https://discuss.elastic.co/) and [the community Slack channel](https://communityinviter.com/apps/elasticstack/elastic-community).

### Frequently Asked Questions

#### How does Learning To Rank (LTR work?

LTR uses a trained machine learning (ML) model to build a ranking function for your search engine. Typically, the model is used as a second-stage re-ranker, to improve the relevance of search results returned by a simpler, first-stage retrieval algorithm.

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