---
title: 'From judgment lists to trained Learning to Rank (LTR) models'
company: Elastic
tag: 排序
date: 2026-03-31
url: https://www.elastic.co/search-labs/blog/learning-to-rank-models-judgment-lists
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# From judgment lists to trained Learning to Rank (LTR) models

Learn how to transform judgment lists into training data for Learning To Rank (LTR), design effective features, and interpret what your model learned.

March 31, 2026

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

[Relevance](/search-labs/blog/category/relevance)

Jump to

Share

In [Evaluating search query relevance with judgment lists](https://www.elastic.co/search-labs/blog/judgment-lists-search-query-relevance-elasticsearch), we built lists and used the `_rank_eval` API to measure search quality. Though this approach gave us an objective way to evaluate changes, improving relevance still requires manual query tuning.

If judgment lists answer the question, **“How good is my ranking?,”** Learning To Rank (LTR) answers, **“How do I systematically make it better?”**

In this article, we take the next step: using those judgment lists to train an LTR model using [XGBoost](https://xgboost.ai/), [Eland](https://eland.readthedocs.io/en/latest/), and Elasticsearch. We’ll focus on understanding the process rather than on implementation details. For the complete code, refer to the [companion notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb).

## What is LTR?

[LTR](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr) uses machine learning (ML) to build a ranking function for your search engine. Instead of manually tuning query weights, you provide examples of proper rankings (your [judgment list](https://www.elastic.co/search-labs/blog/judgment-lists)) and let the model learn what makes documents relevant. In Elasticsearch, LTR works as a second-stage reranker following retrieval of documents from Elasticsearch:

* **First stage:** A standard query ([BM25](https://www.elastic.co/blog/practical-bm25-part-1-how-shards-affect-relevance-scoring-in-elasticsearch), vector, or [hybrid](https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch)) retrieves candidate documents quickly.
* **Second stage:** The LTR model reranks the top results using multiple signals it learned to combine.

![Flowchart showing a two‑stage retrieval and LTR reranking process in Elasticsearch, from user query to final ranked results.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt36337e61d1ff54fb/6a17dd5725daab2fe008a13e/926c037f84e211b6fb5a44a0849823151ab0fa0a-1712x1852.png)

For a deeper introduction, see [Introducing Learning To Rank (LTR)](https://www.elastic.co/search-labs/blog/elasticsearch-learning-to-rank-introduction) in Elasticsearch.

## The journey from judgment list to model

A judgment list tells us which documents should rank highly for a given query. But the model cannot learn directly from document IDs. It needs numerical signals that explain *why* certain documents are potentially relevant.

The process works like this:

1. **Start with judgments.** Query-document pairs with relevance grades, so you define that doc1 is a good match for “DiCaprio performance” search terms.
2. **Extract features.** For each query-document pair, compute numerical signals, some about the document alone (for example, popularity), and others about how the query and document interact (for example, BM25 score).
3. **Train the model.** The model learns which feature patterns predict high grades.
4. **Deploy.** Deploy the trained model to your Elasticsearch cluster.
5. **Query.** Use the model to rerank search results.

![Flowchart showing how document features from a search query are used to train an LTR model, which is then deployed to an Elasticsearch cluster.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blte2d834c840f21943/6a17dd59faa91365f393c75d/b43ac8c8f6dd519b28a6ed2b89328b6e76c71e02-1999x1125.png)

The key insight is that features must capture what your judgments are measuring. If your judgment list rewards popular thriller movies but your features only include text-matching scores, the model has no way to learn what makes those documents relevant.

## What are features?

[*Features*](https://www.elastic.co/docs/solutions/search/ranking/learning-to-rank-ltr#learning-to-rank-feature-extraction) are numerical values that describe a query-document pair. In Elasticsearch, we define features using queries that return [scores](https://www.elastic.co/search-labs/blog/elasticsearch-scoring-and-explain-api). There are three types:

* ***Query-document features*** measure how well a query matches a document. Eland provides the `QueryFeatureExtractor` utility to define these features, which computes the BM25 relevance score for each query-document pair:

```
QueryFeatureExtractor(
    feature_name="title_bm25",
    query={"match": {"title": "{{query}}"}}
)
```

This extracts the BM25 score from the title field for each document relative to the query.

* ***Document features*** are properties of the document that don’t depend on the query. You can extract these using [`script_score`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-script-score-query) or [`function_score`](https://www.elastic.co/docs/reference/query-languages/query-dsl/query-dsl-function-score-query):

```
QueryFeatureExtractor(
    feature_name="popularity",
    query={
        "script_score": {
            "query": {"exists": {"field": "popularity"}},
            "script": {"source": "return doc['popularity'].value;"}
        }
    }
)
```

* ***Query features*** describe the query itself, like the number of terms. These are less common but can help the model handle different query types.

## Designing your feature set

Choosing features isn’t random. Each feature should capture a signal that might explain why users prefer certain documents. Let's look at the features from the LTR notebook and understand the reasoning:

| Feature | Type | Purpose |
| --- | --- | --- |
| `title\_bm25` | Query-document | Title matches are strong relevance signals. For example, a movie titled Star Wars should rank highly for the query "star wars". |
| `actors\_bm25` | Query-document | Some users search by actor name. If they search for "leonardo dicaprio movies", they should get films starring Leonardo DiCaprio. |
| `title\_all\_terms\_bm25` | Query-document | This is a stricter version of title matching where all query terms must be present. It helps distinguish between exact matches and partial ones. |
| `actors\_all\_terms\_bm25` | Query-document | This is the same stricter matching logic as described above but applied specifically to actors. |
| `popularity` | Document | Users generally prefer well-known movies over obscure ones when relevance is similar. A popular Star Wars film should rank above a low-budget parody with "Star Wars" in the title. |

Notice the strategy here:

* **Multiple signals for the same concept.** We have both `title_bm25` (lenient) and `title_all_terms_bm25` (strict). The lenient version scores any document where at least one query term matches the title, and the strict version requires all the terms to be present. For short queries, the lenient match might be enough; whereas for longer, more specific queries, strict matching might be more important. The model can learn when to rely on each.
* **Text features plus quality features.** Text matching alone can return irrelevant documents that happen to contain the right words. The popularity feature lets the model boost well-known, quality content when text scores are similar.
* **Coverage for different query types.** Some queries target titles ("star wars"), and others target actors ("dicaprio movies"). Having features for both means that the model can handle diverse searches.

When designing your own features, ask yourself, "What signals would a human use to decide if this document is relevant?" Those are your candidate features.

## Building the training dataset

Once features are defined, we extract them for every query-document pair in our judgment list. The result is a training dataset where each row contains:

* The query identifier.
* The document identifier.
* The relevance grade (from our judgment list).
* All feature values.

Here’s a simplified example:

| `query\_id` | `query` | `doc\_id` | `grade` |
| --- | --- | --- | --- |
| qid:1 | star wars | 11 | 4 |
| qid:1 | star wars | 12180 | 3 |
| qid:1 | star wars | 278427 | 1 |
| qid:2 | tom hanks movies | 857 | 4 |
| qid:2 | tom hanks movies | 13 | 3 |

A few things to notice:

**NaN values are normal.** When a query doesn’t match a field, the feature returns no score. The movie *Star Wars* has a high `title_bm25` but no `actors_bm25` because the query "star wars" doesn’t match any actor names.

**Queries are grouped during training.** The `query_id` column tells the model which documents to compare against each other. For "star wars", it learns that document 11 (grade 4) should rank above document 278427 (grade 1).

But here’s the important part: The model doesn’t memorize these specific queries. Instead, it learns general patterns, like "documents with high `title_bm25` AND high `popularity` tend to have high grades." When presented with a new query, the model applies these learned patterns to rank the results.

**Features must explain grade differences.** Look at qid:1: The grade 4 document has a higher `title_bm25` and higher `popularity` than the grade 1 document. These patterns are what the model learns.

## Training the LTR model

With the training dataset prepared, we train an [XGBoost](https://xgboost.readthedocs.io/en/stable/) model with a ranking objective. The model builds decision trees that learn patterns like:

* "If `title_bm25` > 10 and `popularity` > 50, predict high relevance."
* "If `title_bm25` is missing but `actors_bm25` > 12, still predict moderate relevance."

Here's how the training process works in practice:

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

During training, the model tries different combinations of these rules and measures how well the resulting rankings match your judgment grades. It uses a metric called [Normalized Discounted Cumulative Gain (NDCG)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) to score itself. A perfect NDCG of 1.0 means that the model's ranking exactly matches your judgments. Lower scores mean that some relevant documents are ranking below where they should be.

The training also uses a technique called [early stopping](https://xgboosting.com/early-stopping/). If the model's score stops improving for several rounds, training halts automatically. This prevents the model from memorizing the training data too closely, which would hurt its ability to generalize to new queries.

The [companion notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb) contains the complete training code.

## Understanding what your LTR model learned

After training, XGBoost can show you which features the model relied on most. You can generate a feature importance chart using XGBoost's built-in visualization:

```
from xgboost import plot_importance

plot_importance(ranker, importance_type="weight")
```

The `importance_type="weight"` parameter shows how often each feature was used in tree splits. Here’s the resulting chart:

![Horizontal bar chart titled “Feature importance,” created with XGBoost's built-in visualization, showing F‑score values for several model features, with popularity as the highest‑scoring feature.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt9053752dd72d06cd/6a17dd5a63baff7ac7741b44/67608c24c50a8775b6e70fa7f522d7b58cefc764-734x460.png)

The F score counts how many times each feature was used to make split decisions across all trees in the model. Higher values mean that the model relied on that feature more often.

In this example:

* `popularity` **(2178):** The most important feature. The model frequently uses popularity to separate relevant from nonrelevant documents.
* `title_bm25` **(1642):** Second-most important. Title matches matter a lot for movie searches.
* `actors_bm25` **(565):** Moderately important. This is useful for queries that mention actors.
* `title_all_terms_bm25` **(211):** Occasionally useful. The stricter matching helps for some queries.
* `actors_all_terms_bm25` **(63):** Rarely used. The model found this feature less predictive.

This chart helps you iterate on your feature set. If a feature that you expected to be important shows near-zero importance, investigate why. Maybe the feature extraction is not working as intended, or maybe that signal doesn’t actually predict relevance in your judgment data.

## Deploying and using the LTR model

Once trained, upload the model to Elasticsearch using Eland:

```
MLModel.import_ltr_model(
    es_client=es_client,
    model=ranker,
    model_id="ltr-model-xgboost",
    ltr_model_config=ltr_config,
    es_if_exists="replace",
)
```

Once uploaded, the model can be used as a [rescorer retriever](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/retrievers/rescorer-retriever) to be combined with other [retrievers](https://www.elastic.co/docs/solutions/search/retrievers-overview) for multistage search pipelines:

```
GET movies/_search
{
  "retriever": {
    "rescorer": {
      "rescore": {
        "window_size": 50,
        "learning_to_rank": {
          "model_id": "ltr-model-xgboost",
          "params": {
            "query": "star wars"
          }
        }
      },
      "retriever": {
        "standard": {
          "query": {
            "multi_match": {
              "fields": ["title", "overview", "actors", "director", "tags", "characters"],
              "query": "star wars"
            }
          }
        }
      }
    }
  }
}
```

Response (simplified):

```
 "hits": {
    "total": {
      "value": 852,
      "relation": "eq"
    },
    "max_score": 25.165691,
    "hits": [
      {
        "_index": "movies",
        "_id": "11",
        "_score": 25.165691,
        "_source": {
          "title": "Star Wars"
        }
      },
      {
        "_index": "movies",
        "_id": "12180",
        "_score": 25.092865,
        "_source": {
          "title": "Star Wars: The Clone Wars"
        }
      },
      {
        "_index": "movies",
        "_id": "181812",
        "_score": 23.456198,
        "_source": {
          "title": "Star Wars: The Rise of Skywalker"
        }
      },
      {
        "_index": "movies",
        "_id": "140607",
        "_score": 23.320757,
        "_source": {
          "title": "Star Wars: The Force Awakens"
        }
      },
...
```

The first-stage query retrieves candidates using BM25. The LTR model then reranks the top 50 results using all the features it learned to weight.

For the sake of the example, the `multi_match` query alone would return some less relevant results on the first positions that LTR helped to fix:

```
{
  "hits": [
    {
      "_index": "movies",
      "_id": "11",
      "_score": 10.971989,
      "_source": {
        "title": "Star Wars"
      }
    },
    {
      "_index": "movies",
      "_id": "12180",
      "_score": 9.923633,
      "_source": {
        "title": "Star Wars: The Clone Wars"
      }
    },
    {
      "_index": "movies",
      "_id": "1022100",
      "_score": 8.9880295,
      "_source": {
        "title": "Andor: A Disney+ Day Special Look"
      }
    },
    {
      "_index": "movies",
      "_id": "278427",
      "_score": 8.845748,
      "_source": {
        "title": "Family Guy Presents: It's a Trap!"
      }
    },
    ...
  ]
}
```

## Conclusion

The path from judgment lists to a working LTR model involves three key steps: designing features that capture relevance signals, building a training dataset that pairs those features with your judgment grades, and training a model that learns the patterns.

Our [previous article](https://www.elastic.co/search-labs/blog/judgment-lists-search-query-relevance-elasticsearch) becomes the starting point for this process. Your grades define what "relevant" means and how to measure it, and your features give the model the signals to predict it.

For the complete implementation with a dataset of 9,750 movies and 384,755 judgment rows, see the [LTR notebook](https://github.com/elastic/elasticsearch-labs/blob/main/notebooks/search/08-learning-to-rank.ipynb). For advanced use cases, like personalized search, see [Personalized search with LTR](https://www.elastic.co/search-labs/blog/personalized-search-elasticsearch-ltr).

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