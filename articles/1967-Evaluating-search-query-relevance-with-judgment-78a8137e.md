---
title: 'Evaluating search query relevance with judgment lists'
company: Elastic
tag: 评测
date: 2025-12-11
url: https://www.elastic.co/search-labs/blog/judgment-lists-search-query-relevance-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Evaluating search query relevance with judgment lists

Explore how to build judgment lists to objectively evaluate search query relevance and improve performance metrics such as recall, for scalable search testing in Elasticsearch.

December 11, 2025

[Jhon Guzmán](/search-labs/author/jhon-guzman)

[Relevance](/search-labs/blog/category/relevance)[Inside Elastic](/search-labs/blog/category/inside-elastic)

Jump to

Share

Developers working on search engines often encounter the same issue: the business team is not satisfied with one particular search because the documents they expect to be at the top of the search results appear third or fourth on the list of results.

However, when you fix this one issue, you accidentally break other queries since you couldn’t test all cases manually. But how can you or your QA team test if a change in one query has a ripple effect in other queries? Or even more importantly, how can you be sure that your changes actually improved a query?

## Towards a systematic evaluation

Here is where judgment lists come in useful. Instead of depending on manual and subjective testing any time you make a change, you can define a fixed set of queries that are relevant for your business case, together with their relevant results.

This set becomes your baseline. Every time you implement a change, you use it to evaluate if your search actually improved or not.

The value of this approach is that it:

* **Removes uncertainty**: you no longer need to wonder if your changes impact other queries; the data will tell you.
* **Stops manual testing**: once the judgment sets are recorded, the test is automatic.
* **Supports changes**: You can show clear metrics that support the benefits of a change.

## How to start building your judgment list

One of the easiest ways to start is to take a representative query and manually select the relevant documents. There are two ways to do this list:

* **Binary Judgments:** Each document associated with a query gets a **simple tag**: *relevant* (usually with a score of “1”) and not-relevant (“0”).
* **Graded Judgments:** Here, each document gets a score with different levels. For example: setting a 0 to 4 scale, similar to a [Likert scale](https://en.wikipedia.org/wiki/Likert_scale), where 0 = “not at all relevant” and 4 = “totally relevant,” with variations like “relevant,” “somewhat relevant,” etc.

Binary judgments work well when the search intent has clear limits: Should this document be in the results or not?

Graded judgements are more useful when there are grey areas: some results are better than others, so you can get “very good,” “good,” and “useless” results and use metrics that value the order of the results and the user’s feedback. However, graded scales also introduce drawbacks: different reviewers may use the scoring levels differently, which makes the judgments less consistent. And because graded metrics give more weight to higher scores, even a small change (like rating something a 3 instead of a 4) can create a much bigger shift in the metric than the reviewer intended. This added subjectivity makes graded judgments noisier and harder to manage over time.

## Do I need to classify the documents myself?

Not necessarily, since there are different ways to create your judgment list, each with its own advantages and disadvantages:

* **Explicit Judgments:** Here, SMEs go over each query/document and manually decide if (or how) relevant it is. Though this provides quality and control, it is less scalable.
* **Implicit Judgments:** With this method, you infer the relevant documents based on real-user behavior like clicks, bounce rate, and purchases, among others. This approach allows you to gather data automatically, but it might be biased. For example, users tend to click top results more often, even if they are not relevant.
* **AI-Generated Judgments:** This last option uses models (like LLMs) to automatically evaluate queries and documents, often referred to as [LLM juries](https://en.wikipedia.org/wiki/LLM-as-a-Judge). It’s fast and easy to scale, but the quality of the data depends on the quality of the model you’re using and how well LLM training data aligns with your business [interests](http://interests.as/). As with human grades, LLM juries can introduce their own biases or inconsistencies, so it’s important to validate their output against a smaller set of trusted judgments. LLM models are probabilistic by nature, so it is not uncommon to see an LLM model giving different grades to the same result regardless of setting [temperature](https://www.ibm.com/think/topics/llm-temperature) parameter as 0.

Below are some recommendations to choose the best method for creating your judgment set:

* Decide how critical some features are for you that only users can properly judge (like price, brand, language, style, and product details). If those are critical, you need **explicit judgments** for at least some part of your *judgment list*.
* Use **implicit judgements** when your search engine already has enough traffic so you can use clicks, conversions, and lingering time metrics to detect usage trends. You should still interpret these carefully, contrasting them with your explicit judgement sets to prevent any bias (e.g: users tend to click top-ranked results more often, even if lower-ranked results are more relevant)

To address this, position debiasing techniques adjust or reweight click data to better reflect true user interest. Some approaches include:

* **Results shuffling**: Change the order of search results for a subset of users to estimate how position affects clicks.
* **Click models** include[Dynamic Bayesian Network](https://wiki.math.uwaterloo.ca/statwiki/index.php?title=a_Dynamic_Bayesian_Network_Click_Model_for_web_search_ranking) [**DBN**](https://wiki.math.uwaterloo.ca/statwiki/index.php?title=a_Dynamic_Bayesian_Network_Click_Model_for_web_search_ranking), [User Browsing Model](https://rsrikant.com/papers/kdd10.pdf) [**UBM**](https://rsrikant.com/papers/kdd10.pdf). These Statistical models estimate the probability of a click reflects real interest rather than just position, using patterns like scrolling, dwell time, click sequence, and returning to the results page.

## Example: Movie rating app

### Prerequisites

To run this example, you need a running Elasticsearch 8.x cluster, [locally](https://www.elastic.co/downloads/elasticsearch) or [Elastic Cloud](https://www.elastic.co/cloud/cloud-trial-overview) (Hosted or Serverless), and access to the [REST API](https://www.elastic.co/docs/reference/elasticsearch/rest-apis) or Kibana.

Think about an app in which users can upload their opinions about movies and also search for movies to watch. As the texts are written by users themselves, they can have typos and many variations in terms of expression. So it’s essential that the search engine is able to interpret that diversity and provide helpful results for the users.

To be able to iterate queries without impacting the overall search behavior, the business team in your company created the following binary judgment set, based on the most frequent searches:

| Query | DocID | Text |
| --- | --- | --- |
| DiCaprio performance | doc1 | DiCaprio's performance in The Revenant was breathtaking. |
| DiCaprio performance | doc2 | Inception shows Leonardo DiCaprio in one of his most iconic roles. |
| DiCaprio performance | doc3 | Brad Pitt delivers a solid performance in this crime thriller. |
| DiCaprio performance | doc4 | An action-packed adventure with stunning visual effects. |
| sad movies that make you cry | doc5 | A heartbreaking story of love and loss that made me cry for hours. |
| sad movies that make you cry | doc6 | One of the saddest movies ever made — bring tissues! |
| sad movies that make you cry | doc7 | A lighthearted comedy that will make you laugh |
| sad movies that make you cry | doc8 | A science-fiction epic full of action and excitement. |

Creating the index:

```
PUT movies
{
  "mappings": {
    "properties": {
      "text": {
        "type": "text"
      }
    }
  }
}
```

BULK request:

```
POST /movies/_bulk
{ "index": { "_id": "doc1" } }
{ "text": "DiCaprio performance in The Revenant was breathtaking." }
{ "index": { "_id": "doc2" } }
{ "text": "Inception shows Leonardo DiCaprio in one of his most iconic roles." }
{ "index": { "_id": "doc3" } }
{ "text": "Brad Pitt delivers a solid performance in this crime thriller." }
{ "index": { "_id": "doc4" } }
{ "text": "An action-packed adventure with stunning visual effects." }
{ "index": { "_id": "doc5" } }
{ "text": "A heartbreaking story of love and loss that made me cry for hours." }
{ "index": { "_id": "doc6" } }
{ "text": "One of the saddest movies ever made -- bring tissues!" }
{ "index": { "_id": "doc7" } }
{ "text": "A lighthearted comedy that will make you laugh." }
{ "index": { "_id": "doc8" } }
{ "text": "A science-fiction epic full of action and excitement." }
```

Below is the Elasticsearch query the app is using:

```
GET movies/_search
{
 "query": {
   "match": {
     "text": {
       "query": "DiCaprio performance",
       "minimum_should_match": "100%"
     }
   }
 }
}
```

### From judgment to metrics

By themselves, judgment lists do not provide much information; they are only an expectation of the results from our queries. Where they really shine is when we use them to calculate objective metrics to measure our search performance.

Nowadays, most of the popular metrics include

* [**Precision**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#k-precision)**:** Measures the proportion of results that are truly relevant within all search results.
* [**Recall**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#k-recall)**:** Measures the proportion of relevant results the search engine found among x results.
* [**Discounted Cumulative Gain (DCG)**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#_discounted_cumulative_gain_dcg)**:** Measures the quality of the result’s ranking, considering the most relevant results should be at the top.
* [**Mean Reciprocal Rank (MRR):**](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval#_mean_reciprocal_rank) Measures the position of the first relevant result. The higher it is in the list, the higher its score.

Using the same movie rating app as an example, we’ll calculate the recall metric to see if there’s any information that is being left out of our queries.

In Elasticsearch, we can use the *judgment lists* to calculate metrics via the [Ranking Evaluation API](https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval). This API receives as input the judgment list, the query, and the metric you want to evaluate, and returns a value, which is a comparison of the query result with the judgment list.

Let’s run the judgment list for the two queries that we have:

```
POST /movies/_rank_eval
{
 "requests": [
   {
     "id": "dicaprio-performance",
     "request": {
       "query": {
         "match": {
           "text": {
             "query": "DiCaprio performance",
             "minimum_should_match": "100%"
           }
         }
       }
     },
     "ratings": [
       {
         "_index": "movies",
         "_id": "doc1",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc2",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc3",
         "rating": 0
       },
       {
         "_index": "movies",
         "_id": "doc4",
         "rating": 0
       }
     ]
   },
   {
     "id": "sad-movies",
     "request": {
       "query": {
         "match": {
           "text": {
             "query": "sad movies that make you cry",
             "minimum_should_match": "100%"
           }
         }
       }
     },
     "ratings": [
       {
         "_index": "movies",
         "_id": "doc5",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc6",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc7",
         "rating": 0
       },
       {
         "_index": "movies",
         "_id": "doc8",
         "rating": 0
       }
     ]
   }
 ],
 "metric": {
   "recall": {
     "k": 10,
     "relevant_rating_threshold": 1
     }
 }
}
```

We’ll use two requests to \_rank\_eval: one for the DiCaprio query and another for sad movies. Each request includes a query and its judgment list (ratings). We don’t need to grade all documents since the ones not included in the ratings are considered as with no judgment. To do the calculations, recall only considers the “relevant set,” the documents that are considered relevant in the rating.

In this case, the DiCaprio query has a recall of 1, while the sad movies got 0. This means that for the first query, we were able to get all relevant results, while in the second query, we did not get any. The average recall is therefore 0.5.

```
{
 "metric_score": 0.5,
 "details": {
   "dicaprio-performance": {
     "metric_score": 1,
     "unrated_docs": [],
     "hits": [
       {
         "hit": {
           "_index": "movies",
           "_id": "doc1",
           "_score": 2.4826927
         },
         "rating": 1
       },
       {
         "hit": {
           "_index": "movies",
           "_id": "doc2",
           "_score": 2.0780432
         },
         "rating": 1
       }
     ],
     "metric_details": {
       "recall": {
         "relevant_docs_retrieved": 2,
         "relevant_docs": 2
       }
     }
   },
   "sad-movies": {
     "metric_score": 0,
     "unrated_docs": [],
     "hits": [],
     "metric_details": {
       "recall": {
         "relevant_docs_retrieved": 0,
         "relevant_docs": 2
       }
     }
   }
 },
 "failures": {}
}
```

Maybe we’re being too strict with the **minimum\_should\_match** parameter since by demanding that 100% of the words in the query are found in the documents, we’re probably leaving relevant results out. Let’s remove the **minimum\_should\_match** parameter so that a document is considered relevant if only one word in the query is found in it.

```
POST /movies/_rank_eval
{
 "requests": [
   {
     "id": "dicaprio-performance",
     "request": {
       "query": {
         "match": {
           "text": {
             "query": "DiCaprio performance"
           }
         }
       }
     },
     "ratings": [
       {
         "_index": "movies",
         "_id": "doc1",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc2",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc3",
         "rating": 0
       },
       {
         "_index": "movies",
         "_id": "doc4",
         "rating": 0
       }
     ]
   },
   {
     "id": "sad-movies",
     "request": {
       "query": {
         "match": {
           "text": {
             "query": "sad movies that make you cry"
           }
         }
       }
     },
     "ratings": [
       {
         "_index": "movies",
         "_id": "doc5",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc6",
         "rating": 1
       },
       {
         "_index": "movies",
         "_id": "doc7",
         "rating": 0
       },
       {
         "_index": "movies",
         "_id": "doc8",
         "rating": 0
       }
     ]
   }
 ],
 "metric": {
   "recall": {
     "k": 10,
     "relevant_rating_threshold": 1
     }
 }
}
```

As you can see, by removing the **minimum\_should\_match** parameter in one of the two queries, we now get an average recall of 1 in both.

```
{
  "metric_score": 1,
  "details": {
    "dicaprio-performance": {
      "metric_score": 1,
      "unrated_docs": [],
      "hits": [
        {
          "hit": {
            "_index": "movies",
            "_id": "doc1",
            "_score": 2.0661702
          },
          "rating": 1
        },
        {
          "hit": {
            "_index": "movies",
            "_id": "doc3",
            "_score": 0.732218
          },
          "rating": 0
        },
        {
          "hit": {
            "_index": "movies",
            "_id": "doc2",
            "_score": 0.6271719
          },
          "rating": 1
        }
      ],
      "metric_details": {
        "recall": {
          "relevant_docs_retrieved": 2,
          "relevant_docs": 2
        }
      }
    },
    "sad-movies": {
      "metric_score": 1,
      "unrated_docs": [],
      "hits": [
        {
          "hit": {
            "_index": "movies",
            "_id": "doc7",
            "_score": 2.1307156
          },
          "rating": 0
        },
        {
          "hit": {
            "_index": "movies",
            "_id": "doc5",
            "_score": 1.3160692
          },
          "rating": 1
        },
        {
          "hit": {
            "_index": "movies",
            "_id": "doc6",
            "_score": 1.190063
          },
          "rating": 1
        }
      ],
      "metric_details": {
        "recall": {
          "relevant_docs_retrieved": 2,
          "relevant_docs": 2
        }
      }
    }
  },
  "failures": {}
}
```

In summary, removing the minimum\_should\_match: 100% clause, allows us to got a perfect recall for both queries.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltaf4f08a8a2915180/6a170df61949f76cbfe7aaba/24d055da4348c63827ba7046fe8cafb6f47cadd8-546x628.png)

We did it! Right?

Not so fast!

By improving recall, we open the door to a wider range of results. However, each adjustment implies a trade-off. This is why defining complete test cases, using different metrics to evaluate changes.

Using judgment lists and metrics prevents you from going in blind when making changes since you now have data to back them up. Validation is no longer manual and repetitive, and you can test your changes in more than just one use case. Additionally, A/B testing allows you to test live which configuration works best for your users and business case, thus coming full circle from technical metrics and real-world metrics.

## Final recommendations for using judgment lists

Working with judgment lists is not only about measuring but also about creating a framework that allows you to iterate with confidence. To achieve this, you can follow these recommendations:

1. **Start small, but start**. You don’t need to have 10,000 queries with 50 judgment lists each. You only need to identify the 5–10 most critical queries for your business case and define which documents you expect to see at the top of the results. This already gives you a base. You typically want to start with the top queries plus the queries with no results. You can also start testing with an easy-to-configure metric like Precision and then work your way up in complexity.
2. **Validate with users.** Complement the numbers with A/B testing in production. This way, you’ll know if changes that look good in the metrics are also generating a real impact.
3. **Keep the list alive.** Your business case will evolve, and so will your critical queries. Update your judgment periodically to reflect new needs.
4. **Make it part of the flow.** Integrate judgment lists into your development pipelines. Make sure each configuration change, synonym, or text analysis is automatically validated against your base list.
5. **Connect technical knowledge with strategy.** Don’t stop at measuring technical metrics like precision or recall. Use your evaluation results to inform business outcomes.

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