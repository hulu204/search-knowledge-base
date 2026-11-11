---
title: 'Multilingual vector search with the E5 embedding model'
company: Elastic
tag: 召回
date: 2023-09-12
url: https://www.elastic.co/search-labs/blog/multilingual-vector-search-e5-embedding-model
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Multilingual vector search with the E5 embedding model

Here's how multilingual vector search works and how to use Elasticsearch with the multilingual E5 embedding model, including examples.

September 12, 2023

[Josh Devins](/search-labs/author/josh-devins)

[Vector Database](/search-labs/blog/category/vector-database)[Python](/search-labs/blog/category/python-programming)

Jump to

Share

Vector search has taken the search and information retrieval world by storm in recent years. It has the ability to match the semantics of queries with documents, to incorporate context and meaning of text, and provides users with natural language querying abilities like never before. Vector search is a great source of context for prompting large language models (LLMs), and it's powering more and more modern search experiences in the age of Generative AI. This blog goes over multilingual vector search, explains how it works, and how to use Elasticsearch with E5 embeddings models. It also showcases examples of multilingual search across languages.

## Why multilingual embeddings?

When researchers first started working with and training embedding models for vector search, they used the most widely available datasets they could find. These datasets however tended to all be in the English language. Queries were in English, Wikipedia articles indexed were in English, and quickly the non-English speaking world took notice. Language-specific language models slowly started to pop up for languages like German, French, Chinese, Japanese and so on. However those models only worked within that language. With the power of embeddings, we also have the ability to train models which embed multiple languages into the same "embedding space", using a single model. You can think of an embedding space as a language agnostic, mathematical representation (dense vector) of the concepts that sentences (queries or passages) represent where embeddings close to each other in the embedding space have similar semantic meaning.

Since we can embed text, images and audio into an embedding space, why not embed multiple languages into the same embedding space? This is the idea behind multilingual embedding models. With aligned training datasets — datasets containing similar sentences in different languages — it's possible to make the model learn not the translation of words between languages, but the relationships and meaning underlying each sentence irrespective of language. This is a true cross-lingual model, capable of working with pairs of text in any of the languages it was trained on. Now let's see how to use these aligned multilingual models.

## Let's consider a few examples

For this exercise, we'll map sentences from English and German into the same part of the embedding space, when they have the same underlying meaning. Let's say I have the following sentences that I'd like to index and search over. For the non-German speakers out there, we've provided the direct English translation of the German sentences. 😉

* id=doc1, language=en, passage="I sat on the bank of the river today."
* id=doc2, language=de, passage="Ich bin heute zum Flussufer gegangen." (English: "I walked to the riverside today.")
* id=doc3, language=en, passage="I walked to the bank today to deposit money."
* id=doc4, language=de, passage="Ich saß heute bei der Bank und wartete auf mein Geld." (English: "I sat at the bank today waiting for my money.")

In the example queries that follow, we show how multilingual embeddings can overcome some of the challenges that [traditional lexical retrieval faces for multilingual search](https://www.elastic.co/blog/multilingual-search-using-language-identification-in-elasticsearch). Typically we talk about vector search overcoming the limitations of lexical search's semantic mismatch and vocabulary mismatch. Semantic mismatch is the case where the tokens (words) we use in the query have the same form as in the indexed documents, but different meanings. For example the "bank" of a river doesn't have the same meaning as a "bank" that holds money. With vocabulary mismatch, we're faced with the tokens being different, but the underlying concept or meaning is similar to meaning represented in the document. We may search for "ATM" which doesn't appear in any document, but is closely related to a "bank that holds money". In addition to these two improvements over lexical search, multilingual (cross-lingual) embeddings add language independence, allowing query and passage to be in different languages. For a deeper look into how vector search works and how it fits with traditional lexical search, have a look at this webinar: [How vector databases power AI search](https://www.elastic.co/virtual-events/how-vector-databases-power-ai-search).

Let's try a few search examples now and see how this works.

### Example 1

*Query*: "riverside" (German: "Flussufer")
*Results*:

1. id=doc1, language=en, passage="I sat on the bank of the river today."
2. id=doc2, language=de, passage="Ich bin heute zum Flussufer gegangen." (English: "I walked to the riverside today.")

In this example, the translation of "riverside" is "Flussufer" in German. The semantic meaning however matches the English phrase "bank of the river", as well as the German keyword "Flussufer", so we match on both documents.

### Example 2

*Query*: "Geldautomat" (English: "ATM")
*Results*:

1. id=doc4, language=de, passage="Ich saß heute bei der Bank und wartete auf mein Geld." (English: "I sat at the bank today waiting for my money.")
2. id=doc3, language=en, passage="I walked to the bank today to deposit money."

In this example, the translation of "Geldautomat" is "ATM" in English. Neither "Geldautomat" nor "ATM" appear as keywords in any of the documents, however the semantic meaning is close to both the English phrase "bank … money", and the German phrase "Bank … Geld". In this case, the context matters and the query is referring to the kind of bank that holds money, and not the bank of a river, so we match only on the documents that refer to that kind of "bank", but we do so across languages based on the semantic meaning and not on keywords.

### Example 3a

*Query*: "movement"
*Results*:

1. id=doc3, language=en, passage="I walked to the bank today to deposit money."
2. id=doc2, language=de, passage="Ich bin heute zum Flussufer gegangen." (English: "I walked to the riverside today.")

In this example, we're searching for the kind of motion represented in the text. We're interested in motion or walking and not sitting or being stationary in one place. As such, the closest documents are represented by the German word "gegangen" (English: "have gone to") and the English word "walked".

### Example 3b

*Query*: "stillness"
*Results*:

1. id=doc4, language=de, passage="Ich saß heute bei der Bank und wartete auf mein Geld." (English: "I sat at the bank today waiting for my money.")
2. id=doc1, language=en, passage="I sat on the bank of the river today."

If we invert the query from Example 3a and look for "stillness" or lack of movement, we get the "opposite" results.

## Multilingual E5 embedding model

In December 2022, Microsoft released a new general-purpose embedding model called E5, or **E**mb**E**ddings from bidir**E**ctional **E**ncoder r**E**presentations. (I know, naming things is hard.) This model was trained on a special, English-only curated dataset called CCPairs, and introduced a few new methods to their training process. The model quickly shot to the top of numerous benchmarks, and after the success of that model, they set their sights on non-English. In addition to embedding models for English, Microsoft later trained a variant of their E5 models on multilingual text, using a variety of multilingual datasets, but with the same overall process as their English counterparts. This showed that their training process was a large part of what helped produce such good English language embeddings, and this success was transferred to multilingual embeddings. In some English-only benchmarks, the multilingual embeddings are even better than other embeddings trained only on English datasets! For those interested, check out the [MTEB retrieval benchmark](https://huggingface.co/spaces/mteb/leaderboard) for more details.

As has become common practice for embedding models, the E5 family comes in three sizes, allowing users to make tradeoff decisions between effectiveness and efficiency for their particular use-case and budgets.

* **Effectiveness** of embeddings refers to how good they are at a task, as measured on a specific dataset. For semantic search this is a retrieval task and is measured using a [search relevance metric](https://opensourceconnections.com/blog/2020/02/28/choosing-your-search-relevance-metric) like nDCG@10 or MRR@10.
* **Efficiency** of embeddings and embedding models is influenced by:

  1. How many dimensions the vectors are that the model produces, which impacts the storage needs (on disk and in memory) and how fast are they to search for.
  2. How large the embedding model is (number of parameters), which impacts the inference latency or the time it takes to create the embeddings at both ingest and search time.

Below we can see the three multilingual E5 models and their characteristics, with effectiveness measured on a multilingual benchmark [Mr. TyDi](https://github.com/castorini/mr.tydi) (see, naming is hard). For a baseline and as a comparison, we've included the BM25 (lexical search) effectiveness scores on Mr. TyDi, [as reported by the E5 authors](https://huggingface.co/intfloat/multilingual-e5-base#benchmark-results-on-mr-tydi).

|  | Effectiveness: Avg. MRR@10 | Efficiency: dimensions | Efficiency: parameters |
| --- | --- | --- | --- |
| BM25 | 33.3 | n/a | n/a |
| multilingual-e5-small | 64.4 | 384 | 118M |
| multilingual-e5-base | 65.9 | 768 | 278M |
| multilingual-e5-large | 70.5 | 1024 | 560M |

## Elasticsearch for multilingual vector search with E5

Elasticsearch enables you to generate, store, and search vector embeddings. We've seen an introduction to multilingual embeddings in general, and we know a little bit about E5. Let's take a look at how to actually wire all this together into a search experience with Elasticsearch. This blog has an accompanying [notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/multilingual-e5/multilingual-e5.ipynb) which shows all the code in detail with the examples above, using Elasticsearch end-to-end.

Here's a quick outline of what's required:

1. Create an [Elastic Cloud](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs) deployment with one ML node of size 8GB or larger (or use any Elasticsearch cluster with ML nodes)
2. Setup the [multilingual-e5-base](https://huggingface.co/intfloat/multilingual-e5-base) embedding model in Elasticsearch to embed text at ingest via an [inference processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-processor.html)
3. Create an index and ingest documents into an ANN index for approximate kNN search
4. Query the ANN index using a [query\_vector\_builder](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#knn-semantic-search)

Let's have a look now at a few code snippets from the [notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/multilingual-e5/multilingual-e5.ipynb) for each step.

### Setup

With an Elastic Cloud cluster created or another Elasticsearch cluster ready, we can upload the embedding model using the [eland](https://eland.readthedocs.io/en/v8.9.0/) library.

```
MODEL_ID = "multilingual-e5-base"

!eland_import_hub_model \
    --cloud-id $CLOUD_ID \
    --es-username elastic \
    --es-password $ELASTIC_PASSWORD \
    --hub-model-id intfloat/$MODEL_ID \
    --es-model-id $MODEL_ID \
    --task-type text_embedding \
    --start
```

Now that the model has been uploaded to the cluster and is ready for inference, we can create the [ingest pipeline](https://www.elastic.co/guide/en/elasticsearch/reference/current/ingest.html) which contains an [inference processor](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-processor.html) to perform the embedding of the text field of our choosing. When using Enterprise Search features such as the [web crawler](https://www.elastic.co/guide/en/enterprise-search/current/crawler.html), you can [manage ingest pipelines](https://www.elastic.co/guide/en/enterprise-search/current/ingest-pipelines.html) through the Kibana UI as well.

```
client.ingest.put_pipeline(id="pipeline", processors=[{
    "inference": {
        "model_id": MODEL_ID,
        "field_map": {
            "passage": "text_field" # field to embed: passage
        },
        "target_field": "passage_embedding" # embedded field: passage_embedding
    }
}])
```

### Indexing

For the simple examples above, we use just a very simple index mapping, but hopefully it gives you an idea of what your mapping might look like too.

```
mapping = {
    "properties": {
        "id": { "type": "keyword" },
        "language": { "type": "keyword" },
        "passage": { "type": "text" },
        "passage_embedding.predicted_value": {
            "type": "dense_vector",
            "dims": 768,
            "index": "true",
            "similarity": "cosine"
        }
    },
    "_source": {
        "excludes": [
            "passage_embedding.predicted_value"
        ]
    }
}
```

With an index created from the above mapping, we're ready to ingest documents. You can use whatever ingest method you'd like, as long as the ingest pipeline that we created at the beginning is referenced (or set as default for your index). Note that as with other embedding models, E5 does have a token limit (512 tokens or about 400 words) so longer text will need to be chunked into individual passages — for example with LangChain or another tool — before being ingested. Here's what our example documents look like.

```
passages = [
   {
        "id": "doc1",
        "language": "en",
        "passage": """I sat on the bank of the river today."""
    },
    {
        "id": "doc2",
        "language": "de",
        "passage": """Ich bin heute zum Flussufer gegangen."""
    },
    {
        "id": "doc3",
        "language": "en",
        "passage": """I walked to the bank today to deposit money."""
    },
    {
        "id": "doc4",
        "language": "de",
        "passage": """Ich saß heute bei der Bank und wartete auf mein Geld."""
    }
]
```

### Search

The documents have been indexed and embeddings created, so we're ready to search!

```
client.search(index="passages", knn={
    "field": "passage_embedding.predicted_value",
    "query_vector_builder": {
        "text_embedding": {
            "model_id": MODEL_ID,
            "model_text": f"query: {q}",
        }
    },
    "k": 2, # for the demo, we're always just searching for pairs of passages
    "num_candidates": 5
})
```

And that's it! With the above steps, and the complete code from the [notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/multilingual-e5/multilingual-e5.ipynb), you can build yourself a multilingual semantic search experience completely within Elasticsearch.

**Note of caution:** E5 models were trained with instructions prefixed to text before embedding it. This means that when you want to embed text for semantic search, you must prefix the query with "query: " and indexed passages with "passage: ". For further details and other use-cases requiring different prefixing, please refer to [the FAQ in the multilingual-e5-base model card](https://huggingface.co/intfloat/multilingual-e5-base#faq).

## Conclusion

In this blog and the accompanying [notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/multilingual-e5/multilingual-e5.ipynb), we've shown how multilingual vector search works, and how to use Elasticsearch with E5 embeddings models. We've motivated this by showing examples of multilingual search across languages, but in fact the same E5 embedding model can be used within a single language as well. For example if you have just a German corpus of text, you can freely use the same model and the same approach to search that corpus with just German queries. It's all the same model, and the same embedding space in the end!

Try out the [notebook](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/multilingual-e5/multilingual-e5.ipynb), and be sure to [spin up a Cloud cluster of your own](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs) to try multilingual semantic search with E5 on the language and dataset of your choice. If you have any questions or want to discuss multilingual semantic search, join us and the entire Elastic community in our [discussion forum](https://discuss.elastic.co/).

### Frequently Asked Questions

#### What are multilingual embedding models?

Multilingual embeddings models are models that can embed multiple languages into the same 'embedding space', enabling cross-lingual search capabilities. These models are capable of working with pairs of text in any of the languages they were trained in.

#### What is the E5 embedding model?

The E5 embedding model, or Embeddings from Bidirectional Encoder Representations was introduced by Microsoft. It has state-of-the-art performance in zero-shot and multilingual settings.

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