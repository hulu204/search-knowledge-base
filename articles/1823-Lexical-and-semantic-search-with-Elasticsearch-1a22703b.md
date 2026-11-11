---
title: 'Lexical and semantic search with Elasticsearch'
company: Elastic
tag: 召回
date: 2023-10-03
url: https://www.elastic.co/search-labs/blog/lexical-and-semantic-search-with-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Lexical and semantic search with Elasticsearch

In this blog, we'll explore various approaches to retrieving information using Elasticsearch, focusing on lexical and semantic search.

October 03, 2023

[Priscilla Parodi](/search-labs/author/priscilla-parodi)

[Vector Database](/search-labs/blog/category/vector-database)[Python](/search-labs/blog/category/python-programming)[Query Languages](/search-labs/blog/category/query-languages)

Jump to

Share

Search is the process of locating the most relevant information based on your search query or combined queries and relevant search results are documents that best match these queries. Although there are several challenges and methods associated with search, the ultimate goal remains the same, **to find the best possible answer to your question**.

Considering this goal, in this blog post, we will explore different approaches to retrieving information using Elasticsearch, with a specific focus on text search: **lexical and semantic search.**

## Prerequisites

To accomplish this, we will provide Python examples that demonstrate various search scenarios on a [dataset](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/lexical-and-semantic-search-with-elasticsearch/products-ecommerce.json) generated to simulate e-commerce product information.

This dataset contains over 2,500 products, each with a description. These products are categorized into 76 distinct product categories, with each category containing a varying number of products, as shown below:

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt34415151c00ced2b/6a17d8710b0bed6c9bdd342c/4104466050f3024b6bcaf382da2a702650f62227-1440x708.png)

*Treemap visualization - top 22 values of category.keyword (product categories)*

For the setup you will need:

* Python 3.6 or later
* The [Elastic Python client](https://www.elastic.co/guide/en/elasticsearch/client/python-api/current/index.html)
* Elastic 8.8 deployment or later, with 8GB memory machine learning node
* The [Elastic Learned Sparse EncodeR](https://www.elastic.co/guide/en/machine-learning/8.9/ml-nlp-elser.html) model that comes pre-loaded into Elastic installed and started on your deployment

We will be using Elastic Cloud, a [free trial is available](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs).

Besides the search queries provided in this blog post, a [Python notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/lexical-and-semantic-search-with-elasticsearch/ecommerce_dense_sparse_project.ipynb) will guide you through the following processes:

* Establish a connection to our Elastic deployment using the Python client
* Load a text embedding model into the Elasticsearch cluster
* Create an index with mappings for indexing feature vectors and dense vectors.
* Create an ingest pipeline with inference processors for text embedding and text expansion

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt0e95406ece8f08d9/6a17d8731d1b83d32e93e2f4/54a9a490a3b0cf1b9c2228bee8eddd3f566bd435-1418x1102.png)

## Lexical search - sparse retrieval

The classic way documents are ranked for relevance by Elasticsearch based on a text query uses the Lucene implementation of the [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) model, a **sparse model for lexical search**. This method follows the traditional approach for text search, looking for exact term matches.

To make this search possible, Elasticsearch converts **text field** data into a searchable format by performing text analysis.

**Text analysis** is performed by an [analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analyzer-anatomy.html), a set of rules to govern the process of extracting relevant tokens for searching. An analyzer must have exactly one [tokenizer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenizers.html). The tokenizer receives a stream of characters and breaks it up into individual tokens (usually individual words), like in the example below:

### String tokenization for lexical search

```
#Performs text analysis on a string and returns the resulting tokens.

# Define the text to be analyzed
text = "Comfortable furniture for a large balcony"

# Define the analyze request
request_body = {
  "analyzer": "standard",
  "text": text
}

# Perform the analyze request
response = client.indices.analyze(analyzer=request_body["analyzer"], text=request_body["text"])

# Extract and display the analyzed tokens
tokens = [token["token"] for token in response["tokens"]]
print("Analyzed Tokens:", tokens)
```

Output

```
Analyzed Tokens: ['comfortable', 'furniture', 'for', 'a', 'large', 'balcony']
```

In this example we are using the default analyzer, the [standard](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-standard-analyzer.html) analyzer, which works well for most use cases as it provides English grammar based tokenization. Tokenization enables matching on individual terms, but each token is still matched literally.

If you want to personalize your search experience you can choose a different [built-in analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-analyzers.html). Example, by updating the code to use the [stop analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-stop-analyzer.html) it will break the text into tokens at any non-letter character with support for removing stop words.

```
...
# Define the analyze request
request_body = {
  "analyzer": "stop",
  "text": text
}
...
```

Output

```
Analyzed Tokens: ['comfortable', 'furniture', 'large', 'balcony']
```

When the built-in analyzers do not fulfill your needs, you can create a [custom analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-custom-analyzer.html), which uses the appropriate combination of zero or more [character filters](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-charfilters.html), a [tokenizer](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenizers.html) and zero or more [token filters](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-tokenfilters.html).

```
"analyzer":  {

  "my_analyzer": {

    "type": "custom", #For custom analyzers, use a type of custom or omit the type parameter.

    "tokenizer": "standard", #Built-in or customized tokenizer

    "filter": ["lowercase", "synonym"] #Built-in or customized token filters
  }
}
```

In the above example that combines a tokenizer and token filters, the text will be lowercased by the [lowercase filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-lowercase-tokenfilter.html) before being processed by the [synonyms token filter](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-synonym-tokenfilter.html#:~:text=Elasticsearch%20will%20use%20the%20token,applied%20to%20the%20synonym%20entries.).

## Lexical matching

[BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables) will measure the relevance of documents to a given search query based on the frequency of terms and its importance.

The code below performs a [match](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-match-query.html) query, searching for up to two documents considering *"description"* field values from the *"ecommerce-search"* index and the search query **"*****Comfortable furniture for a large balcony*****"**.

Refining the criteria for a document to be considered a match for this query can improve the precision. However, more specific results come at the cost of a lower tolerance for variations.

```
# BM25

response = client.search(size=2,
index="ecommerce-search",
query= {
  "match": {
    "description" : {  
      "query": "Comfortable furniture for a large balcony",
      "analyzer": "stop"
    }
  }
}
)

hits = response['hits']['hits']

if not hits:
  print("No matches found")

else:
  for hit in hits:
    score = hit['_score']
    product = hit['_source']['product']
    category = hit['_source']['category']
    description = hit['_source']['description']
    print(f"\nScore: {score}\nProduct: {product}\nCategory: {category}\nDescription: {description}\n")
```

Output

```
Score: 15.607948
Product: Barbie Dreamhouse
Category: Toys
Description: is a classic Barbie playset with multiple rooms, furniture, a large balcony, a pool, and accessories. It allows kids to create their dream Barbie world.

Score: 9.137739
Product: Comfortable Rocking Chair
Category: Indoor Furniture
Description: enjoy relaxing moments with this comfortable rocking chair. Its smooth motion and cushioned seat make it an ideal piece of furniture for unwinding.
```

By analyzing the output, the most relevant result is the "*Barbie Dreamhouse*" product, in the "*Toys*" category, and its description is highly relevant as it includes the terms "*furniture*", "*large"* and *"balcony*", this is the only product with 3 terms in the description that match the search query, the product is also the only one with the term *"balcony"* in the description.

The second most relevant product is a "*Comfortable Rocking Chair*" categorized as "*Indoor Furniture*" and its description includes the terms "*comfortable*" and "*furniture*". Only 3 products in the dataset match at least 2 terms of this search query, this product is one of them.

*"Comfortable"* appears in the description of 105 products and *"furniture"* in the description of 4 products with 4 different categories: *Toys*, *Indoor Furniture, Outdoor Furniture and 'Dog and Cat Supplies & Toys'.*

As you could see, the most relevant product considering the query is a toy and the second most relevant product is indoor furniture. If you want detailed information about the score computation to know why these documents are a match, you can set the [*explain*](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-explain.html) \_\_query parameter to true.

Despite both results being the most relevant ones, considering both the number of documents and the occurrence of terms in this dataset, the intention behind the query "*Comfortable furniture for a large balcony*" is to search for furniture for an actual large balcony, excluding among others, toys and indoor furniture.

Lexical search is relatively **simple and fast**, but it has limitations since it is not always possible to know all the possible terms and synonyms without necessarily knowing the user's intention and queries. A common phenomenon in the usage of natural language is **vocabulary mismatch**. [Research](https://dl.acm.org/doi/abs/10.1145/32206.32212) shows that, on average, **80% of the time** different people (experts in the same field) will name the same thing differently.

These limitations motivate us to look for other scoring models that incorporate semantic knowledge. Transformer-based models, which excel at processing sequential input tokens like natural language, capture the underlying meaning of your search by considering mathematical representations of both documents and queries. This allows for a dense, context aware vector representation of text, powering **Semantic Search**, a refined way to find relevant content.

## Semantic search - dense retrieval

In this context, after converting your data into meaningful vector values, [k-nearest neighbor (kNN)](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html) search algorithm is utilized to find vector representations in a dataset that are most similar to a query vector. Elasticsearch supports two methods for kNN search, [exact brute-force kNN](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#exact-knn) and [approximate kNN](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#approximate-knn), also known as ANN.

Brute-force kNN guarantees accurate results but doesn't scale well with large datasets. Approximate kNN efficiently finds approximate nearest neighbors by sacrificing some accuracy for improved performance.

With Lucene's support for kNN search and dense vector indexes, Elasticsearch takes advantage of the Hierarchical Navigable Small World (HNSW) algorithm, which demonstrates strong search performance across a variety of [ann-benchmark datasets](http://ann-benchmarks.com/). An approximate kNN search can be performed in Python using the below example code.

### Semantic search with approximate kNN

```
# KNN - approximate kNN

response = client.search(index='ecommerce-search', size=2,
knn={
  "field": "description_vector.predicted_value",
  "k": 50, # Number of nearest neighbors to return as top hits.
#The optimal value of k is dependent on the data. It can vary in different scenarios.

  "num_candidates": 500, # Number of nearest neighbor candidates to consider per shard.

#Increasing num_candidates tends to improve the accuracy of the final k results.

  "query_vector_builder": { # Object indicating how to build a query_vector. kNN search enables you to perform semantic search by using a previously deployed text embedding model, the steps for this process are demonstrated in the Python notebook.
    "text_embedding": { 
      "model_id": "sentence-transformers__all-mpnet-base-v2", # Text embedding model id
      "model_text": "Comfortable furniture for a large balcony" # Query
    }
  }
}
)

for hit in response['hits']['hits']:
        
  score = hit['_score']
  product = hit['_source']['product']
  category = hit['_source']['category']
  description = hit['_source']['description']
  print(f"\nScore: {score}\nProduct: {product}\nCategory: {category}\nDescription: {description}\n")
```

This code block uses Elasticsearch's kNN to return up to two products with a description similar to the vectorized query (query\_vector\_build) of "*Comfortable furniture for a large balcony*" considering the embeddings of the “*description*” field in the products dataset.

The products embeddings were previously generated in an ingest pipeline with an inference processor containing the *"*[*all-mpnet-base-v2*](https://huggingface.co/sentence-transformers/all-mpnet-base-v2)*"* text embedding model to infer against data that was being ingested in the pipeline.

This model was chosen based on the evaluation of pretrained models using *"*[*sentence\_transformers.evaluation*](https://github.com/UKPLab/sentence-transformers/blob/master/docs/package_reference/sentence_transformer/evaluation.md)*"* where different classes are used to assess a model during training. The "all-mpnet-base-v2" model demonstrated the best average performance according to the [Sentence-Transformers ranking](https://www.sbert.net/docs/pretrained_models.html) and also secured a favorable position on the [Massive Text Embedding Benchmark (MTEB)](https://huggingface.co/spaces/mteb/leaderboard) Leaderboard. The model pre-trained [microsoft/mpnet-base](https://huggingface.co/microsoft/mpnet-base) model and fine-tuned on a 1B sentence pairs dataset, it maps sentences to a 768 dimensional dense vector space.

Alternatively, there are many other models available that can be used, especially those fine-tuned for your domain-specific data.

Output

```
Score: 0.79207325
Product: Patio Sofa Set with Ottoman
Category: Outdoor Furniture
Description: is a versatile and comfortable patio sofa set, including a sofa, ottoman, and coffee table, great for outdoor lounging.

Score: 0.7836937
Product: Patio Sofa Set with Canopy
Category: Outdoor Furniture
Description: is a luxurious and comfortable patio sofa set with a canopy, providing shade and style for outdoor lounging.
```

*The output may vary based on the chosen model,* [*filters*](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#knn-search-filter-example) *and* [*approximate kNN tune*](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#tune-approximate-knn-for-speed-accuracy)*.*

The kNN search results are both in the "*Outdoor Furniture*" category, even though the word "*outdoor*" was not explicitly mentioned as part of the query, which highlights the importance of semantics understanding in the context.

Dense vector search offers several advantages:

* Enabling semantic search
* Scalability to handle very large datasets
* Flexibility to handle a wide range of data types

However, **dense vector search also comes with its own challenges**:

* Selecting the right embedding model for your use case
* Once a model is chosen, fine-tuning the model to optimize performance on a domain-specific dataset might be necessary, a process that demands the involvement of domain experts
* Additionally, indexing high-dimensional vectors can be computationally expensive

## Semantic search - learned sparse retrieval

Let’s explore an alternative approach: learned sparse retrieval, another way to perform semantic search.

As a sparse model, it utilizes Elasticsearch's Lucene-based inverted index, which benefits from decades of optimizations. However, this approach goes beyond simply adding synonyms with lexical scoring functions like BM25. Instead, it incorporates learned associations using a deeper language-scale knowledge to optimize for relevance.

By expanding search queries to include relevant terms that are not present in the original query, the [Elastic Learned Sparse Encoder](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html) **improves sparse vector embeddings**, as you can see in the example below.

### Sparse vector search with Elastic Learned Sparse Encoder

```
# Elastic Learned Sparse Encoder

response = client.search(index='ecommerce-search', size=2,
query={
  "text_expansion": {
    "ml.tokens": {
      "model_id":"elser_model",
      "model_text":"Comfortable furniture for a large balcony"                
    }
  }
}
)

for hit in response['hits']['hits']:

  score = hit['_score']
  product = hit['_source']['product']
  category = hit['_source']['category']
  description = hit['_source']['description']
  print(f"\nScore: {score}\nProduct: {product}\nCategory: {category}\nDescription: {description}\n")
```

Output

```
Score: 14.405318
Product: Garden Lounge Set with Side Table
Category: Garden Furniture
Description: is a comfortable and stylish garden lounge set, including a sofa, chairs, and a side table for outdoor relaxation.

Score: 14.281318
Product: Rattan Patio Conversation Set
Category: Outdoor Furniture
Description: is a stylish and comfortable outdoor furniture set, including a sofa, two chairs, and a coffee table, all made of durable rattan material.
```

The results in this case include the "*Garden Furniture*" category, which offers products quite similar to "*Outdoor Furniture*".

By analyzing "ml.tokens", the "rank\_features" field containing Learned Sparse Retrieval generated tokens, it becomes apparent that among the various tokens generated there are terms that, while not part of the search query, are still relevant in meaning, such as "*relax*" (comfortable), "*sofa*" (furniture) and "*outdoor*" (balcony).

The image below highlights some of these terms alongside the query, both with and without term expansion.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7e869985347b19a7/6a17d875e31791dc2c2d56a1/dd86607fce6137d843a3ec002390eaa988b432f9-1440x502.png)

As observed, this model provides a context-aware search and helps mitigate the vocabulary mismatch problem while providing more interpretable results. It can even outperform dense vector models when no domain-specific retraining is applied.

## Hybrid search: relevant results by combining lexical and semantic search

When it comes to search, there is no universal solution. Each of these retrieval methods has its strengths but also its challenges. Depending on the use case, the best option may change. Often the best results across retrieval methods can be complementary. Hence, to improve relevance, we’ll look at combining the strengths of each method.

There are multiple ways to implement a **hybrid search**, including linear combination, giving a weight to each score and reciprocal rank fusion (RRF), where specifying a weight is not necessary.

### Elasticsearch: best of both worlds with lexical and semantic search

```
# BM25 + Elastic Learned Sparse Encoder (Linear Combination)

response = client.search(index='ecommerce-search', size=2,

query= {
  "bool": {
    "should": [
    {
      "match": {
        "description" : {  
          "query": "A dining table and comfortable chairs for a large balcony",
          "boost": 1
        }
      }
    },                   
    {
      "text_expansion": {
        "ml.tokens": {
          "model_id": "elser_model",
          "model_text": "A dining table and comfortable chairs for a large balcony",
          "boost": 1
        }
      }
     }
    ]
  }
}
)

# The boost value is 1 for the text expansion and match query. This means that the relevance score of the results of these queries are not boosted. You can specify a boost value to give a weight to each score in the sum. The scores will be calculated as: score = boost value * match_score + boost value * text_expansion_score

for hit in response['hits']['hits']:

  score = hit['_score']
  product = hit['_source']['product']
  category = hit['_source']['category']
  description = hit['_source']['description']
  print(f"\nScore: {score}\nProduct: {product}\nCategory: {category}\nDescription: {description}\n")
```

In this code, we performed a hybrid search with two queries having the value "*A dining table and comfortable chairs for a large balcony*". Instead of using "*furniture*" as a search term, we are specifying what we are looking for, and both searches are considering the same field values, "description". The ranking is determined by a linear combination with equal weight for the BM25 and ELSER scores.

Output

```
Score: 31.628141
Product: Garden Dining Set with Swivel Rockers
Category: Garden Furniture
Description: is a functional and comfortable garden dining set, including a table and chairs with swivel rockers for easy movement.

Score: 31.334227
Product: Garden Dining Set with Swivel Chairs
Category: Garden Furniture
Description: is a functional and comfortable garden dining set, including a table and chairs with swivel seats for convenience.
```

In the code below, we will use the same value for the query, but combine the scores from BM25 (query parameter) and kNN (knn parameter) using the reciprocal rank fusion method to combine and rank the documents.

```
# BM25 + KNN (RRF)

response = client.search(index='ecommerce-search', size=2,
query={
  "bool": {
    "should": [
    {
      "match": {
        "description": {
        "query": "A dining table and comfortable chairs for a large balcony"
        }
      }
    }
    ]
  }
},
knn={
  "field": "description_vector.predicted_value",
  "k": 50,
  "num_candidates": 500,
  "query_vector_builder": {
    "text_embedding": {
      "model_id": "sentence-transformers__all-mpnet-base-v2",
      "model_text": "A dining table and comfortable chairs for a large balcony"
    }
  }
},
rank={
  "rrf": { # Reciprocal rank fusion
    "window_size": 50, # This value determines the size of the individual result sets per query.
    "rank_constant": 20 # This value determines how much influence documents in individual result sets per query have over the final ranked result set.
  }
}
)

for hit in response['hits']['hits']:
        
  rank = hit['_rank']
  category = hit['_source']['category']
  product = hit['_source']['product']
  description = hit['_source']['description']
  print(f"\nRank: {rank}\nProduct: {product}\nCategory: {category}\nDescription: {description}\n")
```

*RRF functionality is in technical preview. The syntax will likely change before GA.*

Output

```
Rank: 1
Product: Patio Dining Set with Bench
Category: Outdoor Furniture
Description: is a spacious and functional patio dining set, including a dining table, chairs, and a bench for additional seating.

Rank: 2
Product: Garden Dining Set with Swivel Chairs
Category: Garden Furniture
Description: is a functional and comfortable garden dining set, including a table and chairs with swivel seats for convenience.
```

Here we could also use different fields and values; some of these examples are available in the [Python notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/lexical-and-semantic-search-with-elasticsearch/ecommerce_dense_sparse_project.ipynb).

As you can see, with Elasticsearch you have the best of both worlds: the traditional lexical search and vector search, whether sparse or dense, to reach your goal **and find the best possible answer to your question.**

If you want to continue learning about the approaches mentioned here, these blogs can be useful:

* [Improving information retrieval in the Elastic Stack: Hybrid retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)
* [Vector search in Elasticsearch: The rationale behind the design](https://www.elastic.co/blog/vector-search-elasticsearch-rationale)
* [How to get the best of lexical and AI-powered search with Elastic’s vector database](https://www.elastic.co/blog/lexical-ai-powered-search-elastic-vector-database)
* [Introducing Elastic Learned Sparse Encoder: Elastic’s AI model for semantic search](https://www.elastic.co/blog/may-2023-launch-sparse-encoder-ai-model)
* [Improving information retrieval in the Elastic Stack: Introducing Elastic Learned Sparse Encoder, our new retrieval model](https://www.elastic.co/blog/may-2023-launch-information-retrieval-elasticsearch-ai-model)

Elasticsearch provides a vector database, along with all the tools you need to build vector search:

* Elasticsearch [vector database](https://www.elastic.co/elasticsearch/vector-database)
* [Vector search](https://www.elastic.co/enterprise-search/vector-search) use cases with Elastic

## Conclusion

In this blog post, we explored various approaches to retrieving information using Elasticsearch, focusing specifically on text, lexical and semantic search. To demonstrate this, we provided Python examples showcasing different search scenarios using a dataset containing e-commerce product information.

We reviewed the classic lexical search with BM25 and discussed its benefits and challenges, such as vocabulary mismatch. We emphasized the importance of incorporating semantic knowledge to overcome this issue. Additionally, we discussed dense vector search, which enables semantic search, and covered the challenges associated with this retrieval method, including the computational cost when indexing high-dimensional vectors.

On the other hand, we mentioned that sparse vectors compress exceptionally well. Thus, we discussed Elastic's Learned Sparse Encoder, which expands search queries to include relevant terms not present in the original query.

There is no one-size-fits-all solution when it comes to search. Each retrieval method has its strengths and challenges. Therefore, we also discussed the concept of hybrid search.

As you could see, with Elasticsearch, you can have the best of both worlds: traditional lexical search and vector search!

Ready to get started? Check the available [Python notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/lexical-and-semantic-search-with-elasticsearch/ecommerce_dense_sparse_project.ipynb) and begin a [free trial of Elastic Cloud](https://cloud.elastic.co/registration?onboarding_token=vectorsearch&cta=cloud-registration&tech=trial&plcmt=article%20content&pg=search-labs).

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