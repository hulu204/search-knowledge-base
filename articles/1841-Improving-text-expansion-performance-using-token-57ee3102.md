---
title: 'Improving text expansion performance using token pruning'
company: Elastic
tag: 召回
date: 2024-04-02
url: https://www.elastic.co/search-labs/blog/text-expansion-pruning
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving text expansion performance using token pruning

Learn about token pruning and how it boosts the performance of text expansion queries by making them more efficient without sacrificing recall.

April 02, 2024

[Kathleen DeRusso](/search-labs/author/kathleen-derusso)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

This blog talks about token pruning, an exciting enhancement to ELSER performance released with Elasticsearch 8.13.0!

## The strategy behind token pruning

We've already talked in great detail about [lexical and semantic search in Elasticsearch](https://www.elastic.co/search-labs/blog/articles/lexical-and-semantic-search-with-elasticsearch) and [text similarity search with vector fields](https://www.elastic.co/search-labs/blog/articles/text-similarity-search-with-vectors-in-elasticsearch). These articles offer great, in-depth explanations of how vector search works.

We've also talked in the past about reducing retrieval costs by [optimizing retrieval with ELSER v2](https://www.elastic.co/search-labs/blog/articles/introducing-elser-v2-part-2). While Elasticsearch is [limited to 512 tokens per inference field](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-limitations.html#ml-nlp-elser-v1-limit-512) ELSER can still produce a large number of unique tokens for multi-term queries. This results in a very large disjunction query, and will return many more documents than an individual keyword search would - in fact, queries with a large number of resulting queries may match most or all of the documents in an index!

![Text expansion illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6678ea7a44ce1506/6a17e7fbb1e113f47179f28c/49c43b85985f1f9bec328960e1577de9bed15658-1440x682.png)

Now, let's take a more detailed look into an example using ELSER v2. Using the infer API we can view the predicted values for the phrase "Is Pluto a planet?"

```
POST /_ml/trained_models/.elser_model_2_linux-x86_64/_infer
{
  "docs":[{"text_field": "is Pluto a planet?"}]
}
```

This returns the following inference results:

```
{
  "inference_results": [
    {
      "predicted_value": {
        "pluto": 3.014208,
        "planet": 2.6253395,
        "planets": 1.7399588,
        "alien": 1.1358738,
        "mars": 0.8806293,
        "genus": 0.8014013,
        "europa": 0.6215426,
        "a": 0.5890018,
        "asteroid": 0.5530223,
        "neptune": 0.5525891,
        "universe": 0.5023148,
        "venus": 0.47205976,
        "god": 0.37106854,
        "galaxy": 0.36435634,
        "discovered": 0.3450894,
        "any": 0.3425274,
        "jupiter": 0.3314228,
        "planetary": 0.3290833,
        "particle": 0.30925226,
        "moon": 0.29885328,
        "earth": 0.29008925,
        "geography": 0.27968466,
        "gravity": 0.26251012,
        "astro": 0.2522782,
        "biology": 0.2520054,
        "aliens": 0.25142986,
        "island": 0.25103575,
        "species": 0.2500962,
        "uninhabited": 0.23360424,
        "orbit": 0.2327767,
        "existence": 0.21717428,
        "physics": 0.2001011,
        "nuclear": 0.1603676,
        "space": 0.15076339,
        "asteroids": 0.14343098,
        "astronomy": 0.10858688,
        "ocean": 0.08870865,
        "some": 0.065543786,
        "science": 0.051665734,
        "satellite": 0.042373143,
        "ari": 0.024783766,
        "list": 0.019822711,
        "poly": 0.018234596,
        "sphere": 0.01611787,
        "dino": 0.006902895,
        "rocky": 0.0062791444
      }
    }
  ]
}
```

These are the inference results that would be sent as input into a text expansion search. When we run a text expansion query, these terms eventually get joined together in one large weighted boolean query, such as:

```
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "pluto": {
              "query": "pluto",
              "boost": 3.014208
            }
          }
        },
        {
          "match": {
            "planet": {
              "query": "planet",
              "boost": 2.6253395
            }
          }
        },
        ...
        {
          "match": {
            "planets": {
              "query": "dino",
              "boost": 0.006902895
            }
          }
        },
        {
          "match": {
            "planets": {
              "query": "rocky",
              "boost": 0.0062791444
            }
          }
        }
      ]
    }
  }
}
```

## Speed it up by removing tokens

Given the large number of tokens produced by ELSER text expansion, the quickest way to realize a performance improvement is to reduce the number of tokens that make it into that final boolean query. This reduces the total work that Elasticsearch invests when performing the search. We can do this by identifying non-significant tokens produced by the text expansion and removing them from the final query.

![Text expansion with pruning illustration](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltcbf8d0392a9bfc91/6a17e7fcfaa913ee5593c893/312f119142d5092ce6c5f6253ad115addfe894f3-1440x676.png)

Non-significant tokens can be defined as tokens that meet both of the following criteria:

1. The weight/score is so low that the token is likely not very relevant to the original term
2. The token appears much more frequently than most tokens, indicating that it is a very common word and may not benefit the overall search results much.

We started with some default rules to identify non-significant tokens, based on internal experimentation using ELSER v2:

* **Frequency**: More than 5x more frequent than the average token frequency for all tokens in that field
* **Score**: Less than 40% of the best scoring token
* **Missing**: If we see documents with a frequency of 0, that means that it never shows up at all and can be safely pruned

If you're using text expansion with a model other than ELSER, you may need to adjust these values in order to return optimal results.

**Both** the token frequency threshold and weight threshold must show the token is non-significant in order for the token to be pruned. This lets us ensure we keep frequent tokens that are very high scoring or very infrequent tokens that may not have as high of a score.

## Performance improvements with token pruning

We benchmarked these changes using the [MS Marco Passage Ranking benchmark](https://elasticsearch-benchmarks.elastic.co/index.html#tracks/msmarco-passage-ranking/nightly/default/90d). Through this benchmarking, we observed that enabling token pruning with the default values described above resulted in a 3-4x improvement in 99th pctile latency and above!

## Relevance impact of token pruning

Once we measured a real performance improvement, we wanted to validate that relevance was still reasonable. We used a small dataset against the MS Marco passage ranking dataset. We did observe an impact on relevance when pruning the tokens; however, when we added the pruned tokens back in a rescore block the relevance was close to the original non-pruned results with only a marginal increase in latency. The rescore, adding in the tokens that were previously pruned, queries the pruned tokens only against the documents that were returned from the previous query. Then it updates the score including the dimensions that were previously left behind.

Using a sample of 44 queries with judgments against the MS Marco Passage Ranking dataset:

| Top K | Rescore Window Size | Avg rescored recall vs control | Control NDCG@K | Pruned NDCG@K | Rescored NDCG@K |
| --- | --- | --- | --- | --- | --- |
| 10 | 10 | 0.956 | 0.653 | 0.657 | 0.657 |
| 10 | 100 | 1 | 0.653 | 0.657 | 0.653 |
| 10 | 1000 | 1 | 0.653 | 0.657 | 0.653 |
| 100 | 100 | 0.953 | 0.51 | 0.372 | 0.514 |
| 100 | 1000 | 1 | 0.51 | 0.372 | 0.51 |

Now, this is only one dataset - but it's encouraging to see this even at smaller scale!

## How to use: Pruning configuration

Pruning configuration will launch in our next release as an experimental feature. It's an optional, opt-in feature so if you perform text expansion queries without specifying pruning, there will be no change to how text expansion queries are formulated - and no change in performance.

We have some examples of how to use the new pruning configuration in our [text expansion query documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-text-expansion-query.html).

Here's an example text expansion query with both the pruning configuration and rescore:

```
GET my-index/_search
{
   "query":{
      "text_expansion":{
         "ml.tokens":{
            "model_id":".elser_model_2",
            "model_text":"Is pluto a planet?",
            "pruning_config": {
              "tokens_freq_ratio_threshold": 5,
              "tokens_weight_threshold": 0.4,
              "only_score_pruned_tokens": false
            }
         }
      }
   },
   "rescore": {
      "window_size": 100,
      "query": {
         "rescore_query": {
            "text_expansion": {
               "ml.tokens": {
                  "model_id": ".elser_model_2",
                  "model_text": "Is pluto a planet?",
                  "pruning_config": {
                    "tokens_freq_ratio_threshold": 5,
                    "tokens_weight_threshold": 0.4,
                    "only_score_pruned_tokens": true
                  }
               }
            }
         }
      }
   }
}
```

Note that the rescore query sets `only_score_pruned_tokens` to false, so it only adds those tokens that were originally pruned back into the rescore algorithm.

This feature was released as a technical preview feature in 8.13.0. You can [try it out in Cloud](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs) today! Be sure to head over to our [discuss](https://discuss.elastic.co/) forums and let us know what you think.

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