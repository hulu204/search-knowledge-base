---
title: 'Understanding chunking strategies in Elasticsearch'
company: Elastic
tag: RAG
date: 2025-09-24
url: https://www.elastic.co/search-labs/blog/chunking-strategies-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Understanding chunking strategies in Elasticsearch

Learn the fundamentals of document chunking in Elasticsearch, compare different chunking strategies, and discover how your chunking choices impact search quality and relevance.

September 24, 2025

[Alexander Dávila](/search-labs/author/alexander-davila)

[AI](/search-labs/blog/category/ai)

Jump to

Share

When designing semantic search engines, RAG applications, or any other system that uses embeddings, one decision can make or break your search quality: how to chunk your data.

Chunking is the process of breaking down large texts into smaller, semantically meaningful pieces that can be individually embedded and searched. It becomes necessary when you're working with documents longer than your embedding model's context window, or when you need to retrieve specific, relevant passages rather than entire documents. While traditional text search indexes documents as-is, vector-based systems need a different approach for two main reasons:

1. Embedding models have a token limit that restricts how much text can be processed at once. For example, the limit for [ELSER](https://www.elastic.co/search-labs/tutorials/search-tutorial/semantic-search/elser-model) and [e5-small](https://www.elastic.co/search-labs/blog/multilingual-vector-search-e5-embedding-model) is 512 tokens. To generate meaningful embeddings, we need to divide texts; otherwise, any information contained in tokens beyond the limit is lost.
2. LLMs also have a token limit, and their attention is limited as well; therefore, it is much more efficient to send only relevant chunks rather than a whole document. Chunking yields better results and makes it harder to exceed the token limit.

Keep in mind that the specific embedding model you choose has major implications for your chunking strategy:

* Models with larger context windows allow for bigger chunks that preserve more context, while smaller context models require more aggressive chunking.
* Some models are optimized for shorter passages, while others work better with paragraphs.

In this blog, we will discuss the fundamentals of chunking and explore how using chunking strategies affects semantic search results in Elasticsearch.

## What is chunking?

Chunking is the process of breaking large documents into smaller pieces ([typically](https://www.elastic.co/search-labs/blog/late-chunking-elasticsearch-jina-embeddings)) before creating embeddings and indexing them. Instead of having a 50-page text converted into a single embedding, chunking splits it into smaller logical units that can be searched over individually.

![How the chunking process works to break down large documents into smaller ones before creating embeddings and indexing them.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3d216a7f1c8df21a/6a17eee15ea30f639664b689/4dd1ac0c3cfda565d2e5c66a4a3c2aa40bb765d7-1600x509.png)

In Elasticsearch, the [semantic\_text](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text) field type uses chunking to break down texts into smaller pieces before automatically generating the embeddings.

## Why does chunking matter for search quality?

If we do not apply chunking before generating embeddings, we can encounter some problems, such as:

* **LLM context window and attention limitations:** LLMs have a limited number of tokens they can take as a context. If we feed all the text just for a small part with relevant context, we will reach this limit more easily. Additionally, even if the text fits within the context window, LLMs suffer from attention problems such as “[lost in the middle](https://arxiv.org/abs/2307.03172)” problems, where important information is overlooked in large blocks of text.
* **Embedding quality and data loss:** An embedding from a large document might fail to capture a single concept well, being too general and diluted. Smaller chunks translate to more focused embeddings that better represent the information. On the other hand, if the text exceeds the token limits of the model, information is simply lost, as it is not taken into account when generating the embedding.
* **Results readability:** Chunking will produce results that are easy to read by humans. Instead of having to read the whole document, you can retrieve relevant sections only.

## Relationship between chunk size and search precision

The size of each chunk creates a [trade-off](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5) in vector search:

* **Smaller chunks:** Will provide more precise matches, but they might lack a meaningful context for the information to be understood.
* **Larger chunks:** Will have more context but might [include multiple concepts](https://www.elastic.co/search-labs/blog/late-chunking-elasticsearch-jina-embeddings#long-context-models), resulting in a less precise match.

**The goal is to select a chunk size so that the information is minimized while still containing useful context.** As a general guide, we can think of the size like this:

Smaller chunks:

* When you need highly specific, factual answers (like looking up definitions, dates, or specific procedures)
* When your documents contain many distinct, self-contained concepts

Larger chunks:

* When context is crucial for understanding (like analyzing arguments, narratives, or complex explanations)
* For documents in which concepts build upon each other and breaking them apart would cause a loss of meaning

To [find the right chunk size](https://www.llamaindex.ai/blog/evaluating-the-ideal-chunk-size-for-a-rag-system-using-llamaindex-6207e5d3fec5) for your use case, you can test with your own content. Monitor whether you're getting too many irrelevant results (chunks are too large) or answers that lack sufficient context (chunks are too small).

## Chunking strategies

Elasticsearch allows us to choose [different approaches](https://www.elastic.co/docs/explore-analyze/elastic-inference/inference-api#chunking-strategies) for splitting documents. You can use this comparison table to select the most appropriate strategy for your use case, considering your document structure and the model you are using:

![Pro's and con's of sentence, word, recursive and having no chunking strategy.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt75056996c66f33f5/6a17eee3a2929916cdd02d4a/39c97e8599a9de2d07f2f97b1f0cad442b02ff49-1036x970.png)

Now let’s see each strategy in action:

### Sentence chunking

This strategy splits text into one or more complete sentences to prioritize readability and semantic coherence at the sentence level.

Input:

```
Artificial intelligence is transforming healthcare through predictive analytics. Machine learning algorithms can analyze patient data to identify risk factors. Early detection of diseases saves lives and reduces costs. However, data privacy remains a critical concern. Healthcare providers must balance innovation with patient confidentiality.
```

Result array (max\_chunk\_size: 50, sentence\_overlap: 1):

```
[ "Artificial intelligence is transforming healthcare through predictive analytics. Machine learning algorithms can analyze patient data to identify risk factors. Early detection of diseases saves lives and reduces costs.",

 "Early detection of diseases saves lives and reduces costs. However, data privacy remains a critical concern. Healthcare providers must balance innovation with patient confidentiality." ]
```

### Word chunking

This strategy splits the text into individual words up to the max\_chunk\_size. This ensures consistency in chunk sizes, providing predictability for processing and storage. The downside is that it might split relevant context across multiple chunks.

Input:

```
Artificial intelligence is transforming healthcare through predictive analytics. Machine learning algorithms can analyze patient data to identify risk factors. Early detection of diseases saves lives and reduces costs. However, data privacy remains a critical concern. Healthcare providers must balance innovation with patient confidentiality.
```

Result array (max\_chunk\_size: 25, overlap: 5):

```
[
  "Artificial intelligence is transforming healthcare through predictive analytics. Machine learning algorithms can analyze patient data to identify risk factors. Early detection of diseases saves lives",
  
  "saves lives and reduces costs. However, data privacy remains a critical concern. Healthcare providers must balance innovation with patient confidentiality."
]
```

### Recursive chunking

This strategy splits the text based on a list of separators, such as newlines. It applies the separators in order and recursively. If after applying all the separators the chunks are still too large, it falls back to sentence splitting. This strategy is especially effective for formatted content (such as markdown documents).

Input:

```
# Climate Change Solutions

## Renewable Energy
Solar and wind power are becoming cost-competitive with fossil fuels. Investment in clean energy infrastructure creates jobs.

## Carbon Capture
Direct air capture technology removes CO2 from the atmosphere. These systems require significant energy input but show promise for large-scale deployment.

## Policy Changes
Government regulations can accelerate the transition to clean energy through carbon pricing and renewable energy mandates.
```

Result array (max\_chunk\_size: 30, separators: ["#", "\n\n"]):

```
[
  "# Climate Change Solutions\n\n## Renewable Energy\nSolar and wind power are becoming cost-competitive with fossil fuels. Investment in clean energy infrastructure creates jobs.",
  
  "## Carbon Capture\nDirect air capture technology removes CO2 from the atmosphere. These systems require significant energy input but show promise for large-scale deployment.",
  
  "## Policy Changes\nGovernment regulations can accelerate the transition to clean energy through carbon pricing and renewable energy mandates."
]
```

### None

This “strategy” disables chunking and creates an embedding from the complete text. It is useful for smaller texts and documents where all the context is always needed. A potential pitfall of this strategy is that the model might discard excess tokens when generating the embedding.

Input:

```
Artificial intelligence is transforming healthcare through predictive analytics. Machine learning algorithms can analyze patient data to identify risk factors. Early detection of diseases saves lives and reduces costs. However, data privacy remains a critical concern. Healthcare providers must balance innovation with patient confidentiality.
```

Result:

```
["Artificial intelligence is transforming healthcare through predictive analytics. Machine learning algorithms can analyze patient data to identify risk factors. Early detection of diseases saves lives and reduces costs. However, data privacy remains a critical concern. Healthcare providers must balance innovation with patient confidentiality."]
```

## Key Chunking Parameters

Elastic offers these customization parameters for the chunking strategy:

* **overlap**: Number of overlapping words between chunks. Used only in a word strategy.
* **sentence\_overlap**: Number of overlapping sentences between chunks. Used only in a sentence strategy.
* **separator\_group**: The predefined list of separators for the recursive chunk strategy. It can be “markdown” or “plaintext.”
* **separators**: A custom list of separators for the recursive chunking strategy. It can be a plain string or a regex pattern.
* **strategy:** The chosen strategy (sentence, word, recursive, or none).
* **max\_chunk\_size:** The maximum size of a chunk measured in words.

## Chunking in Elasticsearch

Let's see how chunking works in Elasticsearch by walking through a practical example.

Chunking settings are specified when creating an inference endpoint, and Elasticsearch automatically handles the chunking process when you index documents.

In the following example, we will create a `text_embedding` [inference endpoint](https://www.elastic.co/docs/api/doc/elasticsearch/operation/operation-inference-text-embedding) with a sentence chunking strategy and check how chunks are generated and found in a semantic query:

1. Create the inference endpoint:

```
PUT _inference/text_embedding/my-embedding-model
{
    "service": "elasticsearch",
      "service_settings": {
        "num_allocations": 1,
        "num_threads": 1,
        "model_id": ".multilingual-e5-small_linux-x86_64"
      },
      "chunking_settings": {
        "strategy": "sentence",
        "max_chunk_size": 40,
        "sentence_overlap": 0
      }
}
```

Here, we're using a maximum chunk size of 40 words without an overlap between chunks. The sentence strategy will split text at natural sentence boundaries.

Make sure you have the **multilingual e5 small** model deployed. This model has a maximum token window of 512.

2. Create an index with a **semantic\_text** field that uses our new inference endpoint:

```
PUT chunking_test
{
  "mappings": {
    "properties": {
      "my-semantic-field": {
        "type": "semantic_text",
        "inference_id": "my-embedding-model"
      }
    }
  }
}
```

When you index a document, Elasticsearch automatically applies the chunking strategy and creates embeddings for each chunk in the **my-semantic-field** field.
3. Index a sample document into our index:

```
PUT chunking_test/_doc/1
{
  "my-semantic-field": "Making perfect coffee requires attention to several key factors. Water temperature should be between 195-205°F for optimal extraction. Grind size affects brewing time and flavor strength significantly. Use a 1:15 coffee to water ratio for most brewing methods. Brewing time varies by method: pour-over takes 3-4 minutes while espresso takes 25-30 seconds. Fresh beans roasted within two weeks produce the best results."
}
```

This document will be automatically split into multiple chunks based on our sentence strategy.

4. Perform a semantic search on the index:

```
GET /chunking_test/_search
{
  "fields": [
    "_inference_fields"
  ],
  "query": {
    "semantic": {
      "field": "my-semantic-field",
      "query": "how much time should I brew my coffee for?"
    }
  },
  "highlight": {
    "fields": {
      "my-semantic-field": {
        "order": "score",
        "number_of_fragments": 1
      }
    }
  }
}
```

Let’s take a look at the query part by part:

```
"fields": [
    "_inference_fields"
  ],
```

Here, we are asking to get the title and the inference fields back; these fields include information about the endpoint, the model, and the chunks.

```
"query": {
    "semantic": {
      "field": "my-semantic-field",
      "query": "how much time should I brew my coffee for?"
    }
  }
```

This is the semantic query on my-semantic-field, it automatically uses the inference endpoint we created in step 1 to search for matches with the terms in the user\_query.

```
"highlight": {
    "fields": {
      "my-semantic-field": {
        "order": "score",
        "number_of_fragments": 1
      }
    }
  }
```

This part will bring back the top hit of the chunks generated from the text.

Now the response:

```
"hits": [
      {
        "_index": "chunking_test",
        "_id": "1",
        "_score": 0.9537368,
        "_source": {
          "my-semantic-field": "Making perfect coffee requires attention to several key factors. Water temperature should be between 195-205°F for optimal extraction. Grind size affects brewing time and flavor strength significantly. Use a 1:15 coffee to water ratio for most brewing methods. Brewing time varies by method: pour-over takes 3-4 minutes while espresso takes 25-30 seconds. Fresh beans roasted within two weeks produce the best results.",
          "_inference_fields": {
            "my-semantic-field": {
              "inference": {
                "inference_id": "my-embedding-model",
                "model_settings": {
                  "service": "elasticsearch",
                  "task_type": "text_embedding",
                  "dimensions": 384,
                  "similarity": "cosine",
                  "element_type": "float"
                },
                "chunks": {
                  "my-semantic-field": [
                    {
                      "start_offset": 0,
                      "end_offset": 135,
                      "embeddings": [
                        -0.047878783,
                          ...
                        0.02849774
                      ]
                    },
                    {
                      "start_offset": 135,
                      "end_offset": 261,
                      "embeddings": [
                        -0.019347992,
                          ...
                        0.046932716
                      ]
                    },
                    {
                      "start_offset": 261,
                      "end_offset": 356,
                      "embeddings": [
                        -0.021673936,
                          ...
                        0.03294023
                      ]
                    },
                    {
                      "start_offset": 356,
                      "end_offset": 418,
                      "embeddings": [
                        0.027161874,
                          ...
                        0.033048477
                      ]
                    }
                  ]
                }
              }
            }
          }
        },
        "highlight": {
          "my-semantic-field": [
            "Brewing time varies by method: pour-over takes 3-4 minutes while espresso takes 25-30 seconds. "
          ]
        }
      }
    ]
```

Let’s break down the response:

**Original content:**

```
"_source": {
  "my-semantic-field": "Making perfect coffee requires attention to several key factors..."
}
```

The complete original text that was indexed.

**Chunking details:**

```
  "_inference_fields": {
    "my-semantic-field": {
      "inference": {
        "inference_id": "my-embedding-model",
        "chunks": {
          "my-semantic-field": [
            {
              "start_offset": 0,
              "end_offset": 135,
              "embeddings": [
                -0.047878783,
			...
                0.02849774
              ]
            },
            {
              "start_offset": 135,
              "end_offset": 261,
              "embeddings": [
                -0.019347992,
			...
                0.046932716
              ]
            },
            {
              "start_offset": 261,
              "end_offset": 356,
              "embeddings": [
                -0.021673936,
			...
                0.03294023
              ]
            },
            {
              "start_offset": 356,
              "end_offset": 418,
              "embeddings": [
                0.027161874,
...
                0.033048477
              ]
            }
          ]
        }
      }
    }
  }
```

This shows you:

* **start\_offset/end\_offset**: Character positions where each chunk begins and ends in the original text
* **embeddings**: The vector representation of each chunk (384 dimensions for the e5-small model)
* **Number of chunks**: In this case, 4 chunks were created from our coffee brewing text

**Best matching chunk:**

```
"highlight": {
  "my-semantic-field": [
    "Brewing time varies by method: pour-over takes 3-4 minutes while espresso takes 25-30 seconds."
  ]
}
```

The highlight shows which specific chunk scored highest for our **"how much time should I brew my coffee for?"** query, demonstrating how semantic search found the most relevant content even when the exact words don't match.

## Chunking strategies experiment

### Setup

We will use the Wikipedia page for some countries in the Americas. These pages contain long texts, which allows us to demonstrate the difference between chunking and no-chunking strategies. We prepared a repository to get the Wikipedia content, and create the appropriate inference endpoints and mapping to upload the data.

1. Clone the repository:

```
git clone https://github.com/Alex1795/embeddings_chunking_strategies_blog.git
cd embeddings_chunking_strategies_blog
```

2. Install required libraries:

```
pip install -r requirements.txt
```

3. Set up environment variables:

```
export ES_HOST="your-elasticsearch-endpoint"
export ES_API_KEY="your-api-key"
```

4. Run the set\_up.py file:

```
python set_up.py
```

This script executes these steps:

* Creates two inference endpoints, both using the ELSER model to generate sparse embeddings:

  1. **sentence-chunking-demo**: Uses a sentence chunking strategy with a max chunk size of 80 and a sentence overlap of 1
  2. **none-chunking-demo**: Does not use any chunking strategy
* It creates a mapping for the index **countries\_wiki,** including two multifields for the **wiki\_article** field:

  1. wiki\_article.sentence: using the **sentence-chunking-demo** inference endpoint
  2. wiki\_article.none: using the **none-chunking-demo** inference endpoint
* It gets the Wikipedia article for each country and uploads the title and content to our new index in the **country** and **wiki\_article** fields, respectively

This might take several minutes; remember, Elastic is chunking and generating embeddings on the semantic text fields. If everything goes well, you will see the process finish correctly:

![Elasticsearch chunking strategy demo part 1](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt4e63cc5a21e131ae/6a17eee4be60862148004833/e7d1d2fb90e985e095847b65b9284b72edfa8331-1392x984.png)![Elasticsearch chunking strategy demo part 2](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt85bbc79d98bb9778/6a17eee6be608665b3004837/1782d934ee999d8d629db787006e3a886762c86a-1448x1030.png)

### Run the semantic searches

The script run\_semantic\_search.py implements several helper functions to perform the same semantic search on both semantic text fields and prints the results in tables for easier comparison. You can simply execute the script like this:

```
python run_semantic_search.py
```

You will see the results of each query defined in the demo\_queries list (add your own queries here to test):

```
demo_queries = [
        "countries in the inca empire",
        "coffee production",
        "oil and petroleum exports",
        "beach destinations",
        "hockey"
    ]
```

### Results

Let’s explore a couple of results from the queries in the demo:

**Query**: countries in the inca empire

**Strategy**: sentence chunking

![Chunking results from the quieres of the demo.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt98cf3ae45a25e0ae/6a17eee857726263411bcca0/e1370841e63047b93291ceb3da0250f5b4f21476-1600x1129.png)

We get the expected results: Peru, Ecuador, Bolivia, Chile, Argentina, and relevant chunks. For example, for Argentina, we get a very specific piece of information:

```
"the advanced Diaguita sedentary trading culture in the northwest, which was conquered by the Inca Empire around 1480"
```

As we can see, we can easily pinpoint why each document appeared in the results.

**Query**: countries in the inca empire

**Strategy**: no chunking

![Results when no chuking strategy is used from the demo.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltece97688230f9ec0/6a17eeea9da390bd9ae46544/e601bcd1128b2889ac010b0c213c57e92aa46d3c-1600x984.png)

Here we can see the same results for the top 4, but at the end we see Mexico, which was not part of the Incan Empire in any way. We can also see that the whole document is received as one relevant chunk, so we can’t really tell why any of these documents were relevant. The problem with these results is that the embedding was formed from the first 512 tokens of the text, so a lot of information was lost. Most likely, we are not getting any information about the history of each country.

**Query**: hockey

**Strategy**: sentence chunking

![Results when a sentence chunking strategy is used from the demo.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt654a61f236f8d15d/6a17eeebfaa913482793c943/4d68969829c7e7ee9c157bef09fe6f69dd553d65-1600x931.png)

We can see countries that are immediately related to hockey, like the USA and Canada, and also Argentina, Chile and Panama. In the relevant chunks column, we see how hockey is mentioned in each article.
**Query**: hockey
**Strategy**: no chunking

![Results when no chunking strategy is used from the demo.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0738573c40fcd808/6a17eeed14d90c330779b6ae/eabed249ec357194cc44d92a49dbc53c372cd160-1600x914.png)

In these results, we can see countries that are not usually related to hockey (or winter sports in general). Since the relevant text is the whole article, we can’t really see why any of these appear in the results. Also, notice that the scores are much lower than before; this indicates that these might not be good results at all, these are just the “closest” to the query, but barely related.

## Conclusion

As we can see, the use of a chunking strategy can drive the quality of the results. Without chunking, we end up with problems such as:

* **Unrelated results** (like Mexico in the Incan Empire): when the text is bigger than the token limit for our embedding model, some data is simply not included when generating the embedding, and we lose information.
* **Results explanation**: Even when results are relevant, it is much more difficult to explain why a particular document appeared from the whole text than from a relevant chunk. This can be a problem when verifying our results and building trust with our end users.
* **Efficiency**: If we are sending the results to an LLM downstream, whole documents quickly consume the context window with irrelevant information, leading to higher token costs and worse response quality.

All in all, a chunking strategy is always a good idea when dealing with texts longer than a model’s token limit. It improves results and reduces costs, making it a fundamental piece when designing AI systems.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltbca7a25e3c272aa8/6a17ffb1be60868d100049d2/6494d88d51edf6a5b31a92b8439792354eae7190-1536x1024.png)

[ES|QL](/search-labs/blog/category/esql)[AI](/search-labs/blog/category/ai)

### Using ES|QL COMPLETION + an LLM to write a Chuck Norris fact generator in 5 minutes

August 28, 2025|[Aurélien Foucret](/search-labs/author/aurelien-foucret)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blta9f7119562f10d5a/6a17f5507f6f151debc09ca3/f10a706b66a83e9df451ece25326cbcd10134e3c-721x420.jpg)

[AI](/search-labs/blog/category/ai)

### Generative AI using Elastic and Amazon SageMaker JumpStart

July 25, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt5cd8853e995046c9/6a17e7872f4a5c03b6fa88f6/52748b9e2f082718804ed9c0d8f4272f4e4f893a-1024x1024.jpg)

[AI](/search-labs/blog/category/ai)

### Retrieval Augmented Generation (RAG) using Cohere Command model through Amazon Bedrock and domain data in Elasticsearch

November 23, 2023|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt576d87464937da1e/6a17f30e0b0bed0469dd36b1/7086754859ba2cbbaf673c843013462892738c30-720x420.jpg)

[AI](/search-labs/blog/category/ai)

### Transforming data interaction: Deploying Elastic’s MCP server on Amazon Bedrock AgentCore Runtime for crafting agentic AI applications

September 04, 2025|[Uday Theepireddy](/search-labs/author/uday-theepireddy)|[+3](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt2d8725035e86f8a8/6a17fe447f6f1564f8c09d74/0564fe794e4c66d0507317822d7aa71826183d20-1311x762.jpg)

[AI](/search-labs/blog/category/ai)[.NET](/search-labs/blog/category/dot-net-programming)[Vector Database](/search-labs/blog/category/vector-database)

### How to use Elasticsearch Vector Store Connector for Microsoft Semantic Kernel for AI Agent development

December 06, 2024|[Florian Bernd](/search-labs/author/florian-bernd)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter