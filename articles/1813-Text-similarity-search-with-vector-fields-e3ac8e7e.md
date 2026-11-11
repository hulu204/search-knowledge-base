---
title: 'Text similarity search with vector fields'
company: Elastic
tag: 召回
date: 2022-10-06
url: https://www.elastic.co/search-labs/blog/text-similarity-search-with-vectors-in-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Text similarity search with vector fields

This post explores how text embeddings and Elasticsearch’s new dense\_vector type could be used to support similarity search.

October 06, 2022

[Julie Tibshirani](/search-labs/author/julie-tibshirani)

[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

From its beginnings as a [recipe search engine](https://www.elastic.co/about/history-of-elasticsearch), Elasticsearch was designed to provide fast and powerful full-text search. Given these roots, improving text search has been an important motivation for our ongoing work with vectors. In Elasticsearch 7.0, we introduced experimental field types for high-dimensional vectors, and now the 7.3 release brings support for using these vectors in document scoring.

This post focuses on a particular technique called text similarity search. In this type of search, a user enters a short free-text query, and documents are ranked based on their similarity to the query. Text similarity can be useful in a variety of use cases:

* **Question-answering:** Given a collection of frequently asked questions, find questions that are similar to the one the user has entered.
* **Article search:** In a collection of research articles, return articles with a title that’s closely related to the user’s query.
* **Image search:** In a dataset of captioned images, find images whose caption is similar to the user’s description.

A straightforward approach to similarity search would be to rank documents based on how many words they share with the query. But a document may be similar to the query even if they have very few words in common — a more robust notion of similarity would take into account its syntactic and [semantic](https://en.wikipedia.org/wiki/Semantic_similarity) content as well.

The natural language processing (NLP) community has developed a technique called text embedding that encodes words and sentences as numeric vectors. These vector representations are designed to capture the linguistic content of the text, and can be used to assess similarity between a query and a document.

This post explores how text embeddings and Elasticsearch’s dense\_vector type could be used to support similarity search. We’ll first give an overview of embedding techniques, then step through a simple prototype of similarity search using Elasticsearch.

> **Note:** Using text embeddings in search is a complex and evolving area. This blog is not a recommendation for a particular architecture or implementation. Start here to learn how you can enhance your search experience with the power of [vector search](https://www.elastic.co/what-is/vector-search).

## What are text embeddings?

Let's take a closer look at different types of text embeddings, and how they compare to traditional search approaches.

### Word embeddings

A [word embedding](https://en.wikipedia.org/wiki/Word_embedding) model represents a word as a dense numeric vector. These vectors aim to capture semantic properties of the word — words whose vectors are close together should be similar in terms of semantic meaning. In a good embedding, directions in the vector space are tied to different aspects of the word’s meaning. As an example, the vector for "Canada" might be close to "France" in one direction, and close to "Toronto" in another.

The NLP and search communities have been interested in vector representations of words for quite some time. There was a resurgence of interest in word embeddings in the past few years, when many traditional tasks were being revisited using neural networks. Some successful word embedding algorithms were developed, including [word2vec](https://papers.nips.cc/paper/5021-distributed-representations-of-words-and-phrases-and-their-compositionality.pdf) and [GloVe](https://nlp.stanford.edu/pubs/glove.pdf). These approaches make use of large text collections, and examine the context each word appears in to determine its vector representation:

* The word2vec Skip-gram model trains a neural network to predict the context words around a word in a sentence. The internal weights of the network give the word embeddings.
* In GloVe, the similarity of words depends on how frequently they appear with other context words. The algorithm trains a simple linear model on word co-occurrence counts.

Many research groups distribute models that have been pre-trained on large text corpora like Wikipedia or Common Crawl, making them convenient to download and plug into downstream tasks. Although pre-trained versions are sometimes used directly, it can be helpful to adjust the model to fit the specific target dataset and task. This is often accomplished by running a 'fine-tuning' step on the pre-trained model.

Word embeddings have proven quite robust and effective, and it is now common practice to use embeddings in place of individual tokens in NLP tasks like machine translation and sentiment classification.

### Sentence embeddings

More recently, researchers have started to focus on embedding techniques that represent not only words, but longer sections of text. Most current approaches are based on complex neural network architectures, and sometimes incorporate labelled data during training to aid in capturing semantic information.

Once trained, the models are able to take a sentence and produce a vector for each word in context, as well as a vector for the entire sentence. Similarly to word embedding, pre-trained versions of many models are available, allowing users to skip the expensive training process. While the training process can be very resource-intensive, invoking the model is much more lightweight — sentence embedding models are typically fast enough to be used as part of real-time applications.

Some common sentence embedding techniques include [InferSent](https://arxiv.org/abs/1705.02364), [Universal Sentence Encoder](https://arxiv.org/abs/1803.11175), [ELMo](https://arxiv.org/abs/1802.05365), and [BERT](https://arxiv.org/abs/1810.04805). Improving word and sentence embeddings is an active area of research, and it’s likely that additional strong models will be introduced.

### Comparison to traditional search approaches

In traditional information retrieval, a common way to represent text as a numeric vector is to assign one dimension for each word in the vocabulary. The vector for a piece of text is then based on the number of times each term in the vocabulary appears. This way of representing text is often referred to as "bag of words," because we simply count word occurrences without regard to sentence structure.

Text embeddings differ from traditional vector representations in some important ways:

* The encoded vectors are dense and relatively low-dimensional, often ranging from 100 to 1,000 dimensions. In contrast, bag of words vectors are sparse and can comprise 50,000+ dimensions. Embedding algorithms encode the text into a lower-dimensional space as part of modeling its semantic meaning. Ideally, synonymous words and phrases end up with a similar representation in the new vector space.
* Sentence embeddings can take the order of words into account when determining the vector representation. For example the phrase "tune in" may be mapped as a very different vector than "in tune".
* In practice, sentence embeddings often don’t generalize well to large sections of text. They are not commonly used to represent text longer than a short paragraph.

## Using embeddings for similarity search

Let’s suppose we had a large collection of questions and answers. A user can ask a question, and we want to retrieve the most similar question in our collection to help them find an answer.

We could use text embeddings to allow for retrieving similar questions:

* During indexing, each question is run through a sentence embedding model to produce a numeric vector.
* When a user enters a query, it is run through the same sentence embedding model to produce a vector. To rank the responses, we calculate the vector similarity between each question and the query vector. When comparing embedding vectors, it is common to use [cosine similarity](https://en.wikipedia.org/wiki/Cosine_similarity).

[This repository](https://github.com/jtibshirani/text-embeddings) gives a simple example of how this could be accomplished in Elasticsearch. The main script indexes ~20,000 questions from the [StackOverflow dataset](https://github.com/elastic/rally-tracks/tree/master/so), then allows the user to enter free-text queries against the dataset.

We’ll soon walk through each part of the script in detail, but first let’s look at some example results. In many cases, the method is able to capture similarity even when there was not strong word overlap between the query and indexed question:

* "zipping up files" returns "Compressing / Decompressing Folders & Files"
* "determine if something is an IP" returns "How do you tell whether a string is an IP or a hostname"
* "translate bytes to doubles" returns "Convert Bytes to Floating Point Numbers in Python"

### Implementation details

[The script](https://github.com/jtibshirani/text-embeddings/blob/blog/src/main.py) begins by downloading and creating the embedding model in TensorFlow. We chose Google’s Universal Sentence Encoder, but it’s possible to use many other embedding methods. The script uses the embedding model as-is, without any additional training or fine-tuning.

Next, we create the Elasticsearch index, which includes mappings for the question title, tags, and also the question title encoded as a vector:

```
"mappings": {
"properties": {
"title": {
"type": "text"
},
"title_vector": {
"type": "dense_vector",
"dims": 512
}
"tags": {
"type": "keyword"
},
...
}
}
```

In the mapping for dense\_vector, we’re required to specify the number of dimensions the vectors will contain. When indexing a title\_vector field, Elasticsearch will check that it has the same number of dimensions as specified in the mapping.

To index documents, we run the question title through the embedding model to obtain a numeric array. This array is added to the document in the title\_vector field.

When a user enters a query, the text is first run through the same embedding model and stored in the parameter query\_vector. As of 7.3, Elasticsearch provides a [cosineSimilarity function](https://www.elastic.co/guide/en/elasticsearch/reference/7.6/query-dsl-script-score-query.html#vector-functions) in its native scripting language. So to rank questions based on their similarity to the user’s query, we use a script\_score query:

```
{
"script_score": {
"query": {"match_all": {}},
"script": {
"source": "cosineSimilarity(params.query_vector, 'title_vector') + 1.0",
"params": {"query_vector": query_vector}
}
}
}
```

We make sure to pass the query vector as a script parameter to [avoid recompiling the script](https://www.elastic.co/guide/en/elasticsearch/reference/7.6/modules-scripting-using.html#prefer-params)() on every new query. Since Elasticsearch does not allow negative scores, it's necessary to add one to the cosine similarity.

| **Note:** this blog post originally used a [different syntax for vector functions](https://www.elastic.co/guide/en/elasticsearch/reference/7.3/query-dsl-script-score-query.html#vector-functions) that was available in Elasticsearch 7.3, but was deprecated in 7.6.
|

### Important limitations

The script\_score query is designed to wrap a restrictive query, and modify the scores of the documents it returns. However, we’ve provided a match\_all query, which means the script will be run over all documents in the index. This is a current limitation of vector similarity in Elasticsearch — vectors can be used for scoring documents, but not in the initial retrieval step. Support for retrieval based on vector similarity is an important area of [ongoing work](https://github.com/elastic/elasticsearch/issues/42326).

To avoid scanning over all documents and to maintain fast performance, the match\_all query can be replaced with a more selective query. The right query to use for retrieval is likely to depend on the specific use case.

While we saw some encouraging examples above, it’s important to note that the results can also be noisy and unintuitive. For example, "zipping up files" also assigns high scores to "Partial .csproj Files" and "How to avoid .pyc files?". And when the method returns surprising results, it is not always clear how to debug the issue — the meaning of each vector component is often opaque and doesn’t correspond to an interpretable concept. With traditional scoring techniques based on word overlap, it is often easier to answer the question "why is this document ranked highly?"

As mentioned earlier, this prototype is meant as an example of how embedding models could be used with vector fields, and not as a production-ready solution. When developing a new search strategy, it is critical to test how the approach performs on your own data, making sure to compare against a strong baseline like a match query. It may be necessary to make major changes to the strategy before it achieves solid results, including fine-tuning the embedding model for the target dataset, or trying different ways of incorporating embeddings such as word-level query expansion.

## Conclusions

Embedding techniques provide a powerful way to capture the linguistic content of a piece of text. By indexing embeddings and scoring based on vector distance, we can compare documents using a notion of similarity that goes beyond their word-level overlap.

We’re looking forward to introducing more functionality based around the vector field type. Using vectors for search is a nuanced and developing area — as always, we would love to hear about your use cases and experiences on [Github](https://github.com/elastic/elasticsearch) and the [Discuss forums](https://discuss.elastic.co/)!

### Frequently Asked Questions

#### What is text similarity search?

Text similarity search is a type of search in which a user enters a short free-text query, and documents are ranked based on their similarity to the query. It can be useful in a variety of use cases, such as question-answering, article search, and image search.

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