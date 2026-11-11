---
title: 'OpenSearch Semantic Sentence Highlighting Explained'
company: Sease
tag: 搜索相关性
date: 2025-09-08
url: https://sease.io/2025/09/opensearch-semantic-sentence-highlighting-explained.html
account: 
origin: harvest3-202607
---
Hi there!

In this post, we explore OpenSearch’s new feature, **Semantic Sentence Highlighting**, introduced in v3.0, how it works, and the differences between it and the [Apache Solr Neural Highlighting Plugin](https://sease.io/apache-solr-neural-highlighting-plugin), our internal product.

## Outline

* Background and Problem Statement
* How Semantic Sentence Highlighting Works in OpenSearch v3.0
* Semantic Highlighting Query Example
* Differences between OpenSearch Semantic Highlighting and Sease Solr Neural Highlighting Plugin

## Background and Problem Statement

Traditional highlighting is based on matching exact words and comes with several drawbacks. It doesn’t do well when there are no exact keyword matches, so it often misses important content with similar meaning. It also has trouble finding multiple relevant parts in a document and can’t highlight text in a way that reflects the true meaning or intent of the search query. Let us take an example were we have the following doc text and a search query:

```
				
					text="Symptoms such as headache are common. Conditions like diabetes require ongoing management"

query="health issues"
				
			
```

In the example above, traditional highlighting is ineffective because there are no keyword matches. This is where semantic highlighting comes into play. Unlike traditional keyword-based highlighting, semantic highlighting captures the context and preserves full sentence structure. In the above example, the semantic highlighter would capture words that are similar to the search query:

`text="Symptoms such as headache are common. Conditions like diabetes require ongoing management"`

In OpenSearch v3.0, semantic sentence highlighting is introduced and it improves search explainability by using machine learning to identify and highlight sentences that match the meaning of the user’s query, rather than just exact keywords.

## How Semantic Sentence Highlighting Works in OpenSearch

The following diagram originates from the OpenSearch Semantic Sentence Highlighting [RFC](https://github.com/opensearch-project/neural-search/issues/1175) (Request for Comments) and depicts the high-level architecture of the feature:

![](https://i0.wp.com/sease.io/wp-content/uploads/2025/08/image-16.png?fit=800%2C179&ssl=1)

The core of the highlighting framework is implemented in the Neural Search plugin (see the [PR](https://github.com/opensearch-project/neural-search/pull/1193)) and integrated with the ML Commons plugin for neural-based highlighting based on the Sentence-Level Question Answering (QA) model (see the [PR](https://github.com/opensearch-project/ml-commons/pull/3600)). When there is a search request with semantic highlighting, the request goes through the following steps:

1. **Validate Config**: Validate highlighting configuration parameters such as query text, model ID from options, etc.
2. **Prepare Text**: Extract query text using a query text extractor based on query types—match, term, boolean, neural, and hybrid.
3. **Machine Learning Plugin Request**: The request contains a question and context to highlight relevant sentences in the context based on the given question.
4. **Segment & Process Text**: Segment the context into sentences, encode the sentences and the question to get tokens, and translate the model response, where 1 means the sentence is relevant and 0 means the sentence is irrelevant.
5. **Model Inference**: Perform sentence highlighting inference to the QA model.
6. **Highlight Spans**: Add relevant sentence details such as start index, end index, sentence itself, and position in the sequence of sentences.
7. **Format Response**: Update the text query by appending pre and post-tags based on the QA model response – adjusting with start and end positions.

As we walk through the implementation details, let’s take a look at some classes (see the OpenSearch highlight module on [GitHub](https://github.com/opensearch-project/neural-search/tree/main/src/main/java/org/opensearch/neuralsearch/highlight) or the [PR](https://github.com/opensearch-project/neural-search/pull/1193)).  
In the Neural Search plugin, [SemanticHighlighter](https://github.com/opensearch-project/neural-search/blob/main/src/main/java/org/opensearch/neuralsearch/highlight/SemanticHighlighter.java) gets registered along with [SemanticHighlighterEngine](https://github.com/opensearch-project/neural-search/blob/3fa34c6445d2d2b46b6fada9d7a3db4626f6260f/src/main/java/org/opensearch/neuralsearch/highlight/SemanticHighlighterEngine.java) and [QueryTextExtractorRegistry](https://github.com/opensearch-project/neural-search/blob/3fa34c6445d2d2b46b6fada9d7a3db4626f6260f/src/main/java/org/opensearch/neuralsearch/highlight/extractor/QueryTextExtractorRegistry.java). The semantic highlighting request invokes the **SemanticHighlighter**. It is integrated with OpenSearch’s existing highlighter framework.

The **`SemanticHighlighter`** class wraps **`SemanticHighlighterEngine`** , which is the core to get the highlighted sentences. The **`SemanticHighlighterEngine`** wraps both **`QueryTextExtractorRegistry`**, **`MLCommonsClientAccessor`** classes.  
The **`SemanticHighlighterEngine`** fetches the Question-Answering (QA) model response by submitting the question and context via **`MLCommonsClientAccessor`**. The QA model response includes the start and end indices of the highlighted sentences. Using these indices, pre and post-tags e.g. **`<em>...</em>`** are applied to format the highlighted sentences. Then it passes the final response to the **`SemanticHighlighter`**.

**`QueryTextExtractorRegistry`** is a registry for query text extractors and manages the extraction process. It gets an appropriate extractor based on the query type to extract the query text. The supported query types are **`NeuralKNNQuery`**, **`TermQuery`**, **`HybridQuery`**, and **`BooleanQuery`**.

`MLCommonsClientAccessor` is an ML helper client to perform sentence highlighting inference and highlight relevant sentences in the context based on the given question. This class acts as a bridge between the Neural Search and ML Commons plugins.

In the ML Commons plugin, **`SentenceHighlightingQATranslator`** class is responsible for several core operations:

* Tokenizes both the question and the context using a Hugging Face tokenizer
* Segments the context into individual sentences
* Associates each token with its corresponding sentence ID
* Manages chunking for contexts that exceed the model’s maximum token limit
* Interprets the model’s output to determine which sentences answer the question

The result is a set of highlighted sentences, each returned with its text and positional metadata from the original context—enabling clear visualization and straightforward extraction of relevant information.

To note that, the QA model is based on the BERT architecture. And it performs binary predictions. For each sentence, it outputs either 1 or 0, where 1 indicates a relevant sentence (that answers the query) and 0 indicates a non-relevant sentence.

## Semantic Highlighting Query Example

Let’s see a query sample using this feature in OpenSearch.   
First, we need to follow the prerequisite steps documented in the OpenSearch [docs](https://docs.opensearch.org/docs/latest/tutorials/vector-search/semantic-highlighting-tutorial/) which are update cluster settings, create an index (index name: **`neural-search-index`**), register and deploy the ML models, and configure an ingest pipeline.   
These steps were already covered in detail in our earlier blog posts, like **[OpenSearch Neural Search Plugin Tutorial](https://sease.io/2022/12/opensearch-neural-search-plugin-tutorial.html)** or **[OpenSearch KNN Plugin Tutorial](https://sease.io/2024/01/opensearch-knn-plugin-tutorial.html).**

Next, we index some sample documents:

```
				
					POST /neural-search-index/_doc/1{
  "text": "Rising rates of mental health disorders such as anxiety, depression, and eating disorders are increasingly reported among adolescents and young adults. These issues are often linked to academic stress and lack of physical activity."
}

POST /neural-search-index/_doc/2
{
  "text": "Youth today face more health issues due to digital lifestyle. Constant screen time, social comparison on social media make them depressed, build low self-esteem."
}

POST /neural-search-index/_doc/3
{
  "text": "Despite facing physical and mental health challenges, many young people today remain resilient and motivated. They actively seek self-improvement and engage in communities that promote healthy lifestyles. Their openness to discussing mental health and prioritizing well-being marks a shift toward greater awareness and proactive care."
}

POST /neural-search-index/_doc/4
{
  "text": "Practicing mindfulness, seeking help from counselors, and staying connected with supportive peers play a key role. Schools and families can support by promoting open conversations, mental health education. But young people have to be motivated in doing this."
}
				
			
```

After indexing sample documents, we perform semantic highlighting using a neural search query (an abstraction over k-NN that accepts raw text as input and generates embeddings on the fly) with the semantic highlighter:

```
				
					POST /neural-search-index/_search
{
  "_source": {
    "excludes": ["text_embedding"]
  },
  "query": {
    "neural": {
      "text_embedding": {
        "query_text": "youth health problems",
        "model_id": "1_jy7JYBs6feJmwsZPcP", 
        "k": 2
      }
    }
  },
  "highlight": {
    "fields": {
      "text": {
        "type": "semantic"
      }
    },
    "options": {
      "model_id": "7_gE7ZYBs6feJmwscPf9" 
    }
  }
}
				
			
```

In the code snippet above, we have two main components: the **`query`** and **`highlight`** parts. In the query section, we use the **`neural`** query to retrieve documents that are semantically similar to the input query text. This is powered by a sentence embedding model belonging to the Sentence‑Transformers framework (SBERT), which is available at [HuggingFace](http://huggingface/sentence-transformers/all-MiniLM-L6-v2).   
In the highlight section, we define the fields to which highlighting should be applied. In this case, for the “text” field, the highlighter type **`semantic`** is used along with the sentence-highlighting model identified by [amazon/sentence-highlighting/opensearch-semantic-highlighter-v1](https://docs.opensearch.org/docs/latest/ml-commons-plugin/pretrained-models/#semantic-sentence-highlighting-models), which is available at [opensearch-semantic-highlighter-v1](https://huggingface.co/opensearch-project/opensearch-semantic-highlighter-v1) .

After registering and deploying the models via the ML Commons plugin, a **`task_id`** is returned. You can then use the [Tasks API](https://docs.opensearch.org/docs/latest/ml-commons-plugin/api/tasks-apis/index/) to monitor the deployment status and retrieve the unique model\_id assigned to each model. As shown above, these IDs must be referenced via the `model_id` parameter within the `text_embedding` block for neural queries and within the **`options`** block for semantic highlighting.   
The semantic highlighter relies entirely on model inference, rather than traditional offset methods like postings or term vectors.

In this example, we search for **`"youth health problems"`**, and the returned results include semantically relevant highlights:

```
				
					"hits": [
      {
        ...
        "highlight": {
          "text": [
            "&lt;em&gt;Youth today face more health issues due to digital lifestyle.&lt;/em&gt; Constant screen time, social comparison on social media make them depressed, build low self-esteem."
          ]
        }
      },
      {
       ...
        "highlight": {
          "text": [
            "&lt;em&gt;Rising rates of mental health disorders such as anxiety, depression, and eating disorders are increasingly reported among adolescents and young adults.&lt;/em&gt; &lt;em&gt;These issues are often linked to academic stress and lack of physical activity.&lt;/em&gt;"
          ]
        }
      }
]  
				
			
```

As seen in the output, both documents include relevant highlights wrapped in **`<em></em>`** tags by default. To change the highlighting tags, see [Changing the highlighting tags](https://docs.opensearch.org/docs/latest/search-plugins/searching-data/highlight/#changing-the-highlighting-tags). The tagged spans capture contextually meaningful sentences related to “youth health problems” such as digital lifestyle, anxiety, depression, academic pressure, and social media influence.

Semantic highlighting ensures that entire sentences with strong relevance, not just keyword matches, are surfaced, making results more useful and readable.

## Differences between OpenSearch Semantic Highlighting and Sease Solr Neural Highlighting Plugin

We have compared the semantic highlighting implementation approaches in OpenSearch and the Sease [Apache Solr Neural Highlighting Plugin](https://sease.io/apache-solr-neural-highlighting-plugin).

The following table illustrates the differences between semantic sentence highlighting in OpenSearch v3.0 and the Sease neural highlighting plugin in Solr v9.x. Overall, OpenSearch semantic highlighter takes a sentence-level QA model approach, whereas Sease Solr neural highlighter utilises a token-level extractive QA model-based solution.

![](https://i0.wp.com/sease.io/wp-content/uploads/2025/08/image-15.png?fit=795%2C772&ssl=1)

I hope you found this post helpful. Feel free to share your thoughts or questions in the comments.

Thanks for reading — stay tuned for more insights!

## Need Help with this topic?​

If you're struggling with OpenSearch semantic sentence highlighting, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with OpenSearch semantic sentence highlighting, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your OpenSearch search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)