---
title: 'Semantic Search (Text to Vector) with Apache Solr'
company: Sease
tag: 召回
date: 2025-07-17
url: https://sease.io/2025/07/semantic-search-text-to-vector-with-apache-solr.html
account: 
origin: harvest3-202607
---
Dense vector search was introduced in Apache Solr 9.0 in [2022](https://sease.io/2022/01/apache-solr-neural-search.html) and since then it has received substantial adoption from the community.  
Text vectorisation had to happen outside Solr, as there was no support to encode text to vector within the search engine transparently.  
Apache Solr 9.8 changes this, introducing a module that allows interaction with well-known large language model providers such as OpenAI, Cohere, HuggingFace, and Mistral AI via the open-source library LangChain4j.

## Traditional (keyword) Search Problems

One of the biggest problems we’ve seen in many traditional search engines is the ‘[vocabulary mismatch problem](https://en.wikipedia.org/wiki/Vocabulary_mismatch)‘:

Incorrect or not exhaustive search results are returned because the terms used at query time (lexicon) don’t match the terms used in the documents of the corpus of information.

**i.e.**

queries and documents use different terms to describe the same concepts (or closely related).

![](https://i0.wp.com/sease.io/wp-content/uploads/2025/07/image-4.png?fit=2688%2C1680&ssl=1)

## Vector Search

A solution to the problem is to **use Large Language Models** (specifically fine-tuned for sentence similarity) **to encode text to a numerical vector**, in a way that sentences that are semantically similar are encoded to vectors that are close to each other in the vector space.

In this way, searching for content that is semantically close to a query sentence maps to running a k-nearest-neighbor query on vectors.

![](https://i0.wp.com/sease.io/wp-content/uploads/2025/07/image.png?fit=2688%2C1680&ssl=1)

Up to Solr 9.7, as you can see from the diagram, the text vectorisation had to happen outside Solr, the search engine was only able to handle vectors, not supporting end-to-end semantic search transparently.

## Semantic Search from Apache Solr 9.8

This changes with Apache Solr 9.8: with the introduction of the LLM module, you can configure Solr to talk with an external service to do the text vectorisation for you, offering a transparent semantic search experience end-to-end.

![](https://i0.wp.com/sease.io/wp-content/uploads/2025/07/image-5.png?fit=2688%2C1680&ssl=1)

Once configured with a vectorisation model (and we’ll see shortly how to do it), Solr is able to encode text to vector (both at query and indexing time) and run vector search to find relevant to the user information need.

## llm module (from Apache Solr 9.8, January 2025)

This module:

* stores the configuration to access text vectorisation APIs external to Solr ([Langchain4j](https://github.com/langchain4j/langchain4j) is internally used to interact with such APIs).
* implements a query parser (that encodes the query to a vector and then builds a Knn query)
* implements an Update Request Processor to vectorise the content of textual fields

To [enable the module](https://solr.apache.org/guide/solr/latest/configuration-guide/solr-modules.html) you can follow the standard Solr documentation:

* bin/solr start -e techproducts -Dsolr.modules=llm
* add a <str name=”modules”> tag to your [solr.xml](https://solr.apache.org/guide/solr/latest/configuration-guide/configuring-solr-xml.html)
* environment variable SOLR\_MODULES (e.g. in solr.in.sh or solr.in.cmd)
* system property solr.modules

Once enabled you can configure and use its internal components (the query parser and the update request processor).

## Models

A text-to-vector model has the responsibility of encoding text to vector.

At the time of writing only external models are supported: the text encoding doesn’t happen in the Solr JVM nor locally: ONLY EXTERNALLY.

A model (with the parameters to access it) is described via a JSON payload.

the Solr vectorisation model specifies the parameters to access the APIs, the model doesn’t run internally in Solr.

A model is described by these parameters:

**`class`**

|  |  |
| --- | --- |
| **Required** | **Default**: none |

The model implementation. Accepted values:

* `dev.langchain4j.model.huggingface.HuggingFaceEmbeddingModel`.
 * `dev.langchain4j.model.mistralai.MistralAiEmbeddingModel`.
 * `dev.langchain4j.model.openai.OpenAiEmbeddingModel`.
 * `dev.langchain4j.model.cohere.CohereEmbeddingModel`.

**`name`**

|  |  |
| --- | --- |
| **Required** | **Default**: none |

The identifier of your model is used by any component that intends to use the model (**`knn_text_to_vector`** query parser).

**`params`**

|  |  |
| --- | --- |
| Optional | **Default**: none |

Each model class has potentially different parameters. Many are shared but for the full set of parameters of the model you are interested in please refer to the official documentation of the LangChain4j version included in Solr: [Vectorisation Models in LangChain4j](https://docs.langchain4j.dev/category/embedding-models).

Currently four [models are supported](https://solr.apache.org/guide/solr/latest/query-guide/text-to-vector.html#supported-models): Hugging Face, MistralAI, OpenAI and Cohere.

To upload the model from a file: a **`/path/myModel.json`** file, please run:

```
				
					curl -XPUT 'http://localhost:8983/solr/techproducts/schema/text-to-vector-model-store' --data-binary "@/path/myModel.json" -H 'Content-type:application/json'
				
			
```

To view all models:

```
				
					http://localhost:8983/solr/techproducts/schema/text-to-vector-model-store
				
			
```

To view a model (‘model1’):

```
				
					http://localhost:8983/solr/collection/schema/text-to-vector-model-store/
model1
				
			
```

To delete a model (‘model1’):

```
				
					curl -XDELETE 'http://localhost:8983/solr/techproducts/schema/text-to-vector-model-store/model1'
				
			
```

## Indexing Time

The ‘llm’ module introduces the ‘solr.llm.textvectorisation.update.processor.TextToVectorUpdateProcessor’, a component that processes a Solr document in input, enriching it with a vectorised encoding of a textual field.

```
				
					&lt;updateRequestProcessorChain name="textToVector"&gt;
  &lt;processor class="solr.llm.textvectorisation.update.processor.TextToVectorUpdateProcessorFactory"&gt;
   &lt;str name="inputField"&gt;_text_&lt;/str&gt;
   &lt;str name="outputField"&gt;vector&lt;/str&gt;
   &lt;str name="model"&gt;dummy-1&lt;/str&gt;
  &lt;/processor&gt;
  &lt;processor class="solr.RunUpdateProcessorFactory"/&gt;
 &lt;/updateRequestProcessorChain&gt;
				
			
```

Adding this component to an update request processor chain means that all documents you index will be enriched with a vector, encoded from the ‘inputField’ using the model in the parameters.

The content of your document (‘inputField’) is sent to a remote hosted model. Be careful with your performance and privacy requirements!

## Enrich Documents with Vectors on a Second Pass

##### Naive Approach

Vectorising is considered slow (especially when network latency is added to the picture).  
You may want to first index your documents and then, in the background, add the vectorised fields.

Unfortunately, right now Solr doesn’t offer the capability of building the vector data structures in the background after the traditional indexing is complete (making it searchable and later vectorised).

There are still some workarounds that can mitigate the situation a bit.

A first approach is to define two update request processor chains, identical except one adds the vectorisation:

```
				
					&lt;updateRequestProcessorChain name="no-vectorisation"&gt;
  &lt;processor class="solr.processor1"&gt;
   ...
  &lt;/processor&gt;
   ...
  &lt;processor class="solr.processorN"&gt;
   ...
  &lt;/processor&gt;
  &lt;processor class="solr.RunUpdateProcessorFactory"/&gt;
 &lt;/updateRequestProcessorChain&gt;
				
			
```

You first target the ‘no-vectorisation’ chain and index all your documents.

```
				
					&lt;updateRequestProcessorChain name="vectorisation"&gt;
&lt;processor class="solr.processor1"&gt;
   ...
  &lt;/processor&gt;
...
&lt;processor class="solr.processorN"&gt;
   ...
  &lt;/processor&gt;
&lt;processor class="solr.llm.textvectorisation.update.processor.
TextToVectorUpdateProcessorFactory"&gt;
   &lt;str name="inputField"&gt;_text_&lt;/str&gt;
   &lt;str name="outputField"&gt;vector&lt;/str&gt;
   &lt;str name="model"&gt;dummy-1&lt;/str&gt;
  &lt;/processor&gt;
  &lt;processor class="solr.RunUpdateProcessorFactory"/&gt;
 &lt;/updateRequestProcessorChain&gt;
				
			
```

Once it’s finished, you re-index all your documents targeting the second.

The effect you’ll see is that vectors will be added increasingly, while your documents become searchable lexically in a shorter amount of time.

Internally Solr will re-index everything, so there’s a lot of data traffic (data is sent again to Solr), lot of cpu waste (text is processed again and data structures rebuilt), a lot of deletions behind the scenes (each updated document is deleted and added again) and a lot of segment merges (as new segments are created).

Be careful with this approach as it affects the number of segments, deleted docs and merges that happen behind the scenes in Solr. For small scale systems this may be neglectable, but scaling up this negative aspect can be extremely important.

##### Partial Updates

A slightly better solution is to use partial updates:  
you avoid sending the full document again to Solr when you want to add vectors.

This time, the chains look slightly different:

```
				
					&lt;updateRequestProcessorChain name="no-vectorisation"&gt;
  &lt;processor class="solr.processor1"&gt;
   ...
  &lt;/processor&gt;
   ...
  &lt;processor class="solr.processorN"&gt;
   ...
  &lt;/processor&gt;
  &lt;processor class="solr.RunUpdateProcessorFactory"/&gt;
 &lt;/updateRequestProcessorChain&gt;
				
			
```

The ‘no-vectorisation’ looks exactly the same; you first index all your documents in a traditional way, executing all the update request processors you like.

Then, when you want to run the second pass to add the vectors, you target a new chain that only contains the text-to-vector processor (+ the mandatory ones).

```
				
					&lt;updateRequestProcessorChain name="vectorisation"&gt;
…
&lt;processor class="solr.llm.textvectorisation.update.processor.
TextToVectorUpdateProcessorFactory"&gt;
   &lt;str name="inputField"&gt;_text_&lt;/str&gt;
   &lt;str name="outputField"&gt;vector&lt;/str&gt;
   &lt;str name="model"&gt;dummy-1&lt;/str&gt;
  &lt;/processor&gt;
  &lt;processor class="solr.RunUpdateProcessorFactory"/&gt;
 &lt;/updateRequestProcessorChain&gt;
				
			
```

At this point, you can define a boolean field in your schema that keeps track of what documents have been vectorised already and just partially update that field, targeting the vectorisation chain:

```
				
					&lt;field name="vectorised" type="boolean" indexed="true" stored="true" docValues="true" default="false"/&gt;

re-index all your docs {"id":"mydoc","vectorised":{"set":true}}
				
			
```

Each partial update will just set the new field to ‘true’, with no data waste in networking. Solr will set the field and run the vectorisation chain that will take in input the field to be vectorised and encode it for each document.

The benefits in comparison to the naive solution are still minimal, as all the deleted and inserts will happen anyway, but at least we avoid the data networking transfer.

A big nice to have here would be an equivalent of the [in place update](https://solr.apache.org/guide/solr/latest/indexing-guide/partial-document-updates.html#in-place-updates) for the vectors.

Interested in helping or sponsoring new Solr features like in place vectorisation? [Reach out to us!](https://sease.io/contacts)

## Query Time

Once you have your vectors indexed, running a natural language query is quite simple with the ‘org.apache.solr.llm.texttovector.search.TextToVectorQParserPlugin’.

First you define it in your solrconfig.xml:

```
				
					&lt;queryParser name="knn_text_to_vector" class="org.apache.solr.llm.texttovector.search.TextToVectorQParserPlugin"/&gt;
				
			
```

Then, at query time, you just use it as you would for the knn query parser, but rather than passing the vector, you pass the natural language query and a reference to the model you want to use for vectorisation.

```
				
					?q={!knn_text_to_vector model=modelName f=vectorField topK=10}a query
				
			
```

Behind the scenes, Solr will use the model to vectorise your query text and then run a vector search.

The text of your query is sent to a remote hosted model. Be careful with your performance and privacy requirements!

## What's next?

![Apache Lucene/Solr AI Roadmap Do You Want to Make It Happen?](https://i0.wp.com/sease.io/wp-content/uploads/2023/10/Copia-di-Blog-post-3.jpg?fit=800%2C450&ssl=1)

There’s plenty of future work we want to contribute to enhance this new, exciting functionality:

* **Local** models (to run on your local machine or potentially in the Solr JVM)
* In place vectorisation update
* Vector search optimisations
  + nested/multi vectors -> in progress [[Github](https://github.com/apache/solr/pull/3316)]
  + scalar quantisation -> in progress [[Github](https://github.com/apache/solr/pull/3385)]
  + binary quantisation
  + new knn queries (especially the Seeded one)
* Retrieval augmented generation
  + conversational search (including short\long term memory)
* Query/document expansion
* LLM highlighter/explainer
* From natural language to structured queries
* Better hybrid search

## Do you want to know more?

Check my talk at Berlin Buzzwords 2025

[Click Here](https://www.youtube.com/watch?v=9KJTbgtFWOU)

## Do you want to know more?

Check my talk at Berlin Buzzwords 2025

[Click here](https://www.youtube.com/watch?v=9KJTbgtFWOU)