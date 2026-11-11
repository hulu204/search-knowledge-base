---
title: 'GLiNER as an Alternative to LLMs for Query Parsing - Introduction'
company: Sease
tag: 查询理解
date: 2025-10-13
url: https://sease.io/2025/10/gliner-as-an-alternative-to-llms-for-query-parsing-introduction.html
account: 
origin: harvest3-202607
---
Hi Information Retrieval community,  
In this series, we will be talking about **[GLiNER](https://arxiv.org/pdf/2311.08526)**, a flexible Named Entity Recognition (NER) model designed to identify any *type of entity*.

This topic will be divided into two blog posts:

* In this first post, we will explore how GLiNER works, highlighting its underlying architecture and how it differs from traditional NER models.
* A second post will follow, focused on [evaluating GLiNER as a potential alternative to Large Language Models (LLMs) for **query parsing tasks**](https://sease.io/2025/10/gliner-as-an-alternative-to-llms-for-query-parsing-evaluation.html). We will run a comparative example and discuss whether GLiNER might be a better choice.

## Limitations of Traditional NER Models

Let’s start with a brief definition of Named Entity Recognition ([NER](https://en.wikipedia.org/wiki/Named-entity_recognition)).  
NER is a core technique in Natural Language Processing ([NLP](https://en.wikipedia.org/wiki/Natural_language_processing)) that automatically detects and classifies key entities — such as people, organisations, locations, and dates —from unstructured text. By extracting these entities, NER helps convert raw text into structured data. This capability is especially valuable in search applications, where recognising entities within user queries enhances query parsing.

Nowadays, traditional NER models encounter significant challenges:

* They are constrained by a fixed set of predefined entity types (i.e., the specific entities on which they were trained).
* They require large amounts of manually labelled data, which is time-consuming and expensive to produce.
* Their performance tends to drop when exposed to variations in language, style, or context that differ from the training data.
* These models struggle to adapt to new or evolving entity categories without retraining, making them inflexible and domain-dependent. Retraining is often resource-intensive and not always practical.

This is where GLiNER comes in, offering greater flexibility, zero-shot generalisation, and reduced reliance on labelled data, making it more suitable for diverse and dynamic NER tasks.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/01/Screenshot-2025-07-08-alle-15.22.44.png?fit=800%2C306&ssl=1)

*Comparative Table: Traditional NER Models vs. GLiNER*

## GLiNER

GLiNER, short for Generalist and Lightweight Model for Named Entity Recognition,  is a Named Entity Recognition (NER) model designed to identify any entity type using a bidirectional transformer encoder (BERT-like).

Let’s try to explain GLiNER’s architecture in simple terms.

### Architecture

As we can see from the model architecture picture below, there are three main components:

1. A pre-trained textual encoder
2. A span representation module
3. An entity representation module

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/01/Screenshot-2025-06-25-alle-13.17.28.png?fit=800%2C453&ssl=1)

*Model Architecture. From the [original paper](https://arxiv.org/pdf/2311.08526).*

##### 1) A pre-trained textual encoder

The first component of the model architecture is the **pre-trained textual encoder**, which plays a fundamental role in transforming raw text into meaningful numerical representations (embeddings) for each token. The textual encoder is a **Bidirectional Transformer Language Model** **(BiLM)**, based on a **BERT-like architecture**, that has been pre-trained on large corpora and can capture rich contextual information for each token by simultaneously leveraging context from both the left and the right of each token across the entire input sequence. Among various encoders tested, the authors of the paper report that **[DeBERTa-v3](https://arxiv.org/pdf/2111.09543)** performs best when used as the backbone of the system.

**INPUT** – The encoder takes in input a **single, unified textual sequence** that includes both:

* **The entity types to look for**, written in natural language (e.g., *“person”*, *“location”*, *“organization”*), and
* **The sentence/text**where those entities should be identified.

For example, the input might look like this:

```
				
					person [ENT] location [ENT] date [SEP] Elton John performed in New York in 2022.
				
			
```

The entity types are separated by a special learned token `[ENT]`, while the entire list of types is separated from the input sentence using the `[SEP]` token, just like in BERT-style models.

**OUTPUT** – The encoder returns two types of representations:

1. **Token embeddings**: contextualised vector representations for each token in the sentence.
2. **Entity type embeddings**: for each entity type included in the prompt.

##### 2) A span representation module

After the pre-trained textual encoder generates the initial token embeddings, these are passed to the span representation layer, which computes a single embedding for each possible span (a contiguous sequence of words).

**INPUT**: Token embeddings. For each possible span (a group of tokens), the module produces a single embedding for that span using a two-layer feedforward neural network (FFN). The FFN operates on the concatenated representations of the boundary tokens, allowing the model to capture the overall meaning of the span.

**OUTPUT**: a **span embedding** for each possible text span. To avoid a combinatorial explosion, the maximum span length is set to **12 tokens**.

##### 3) An entity representation module

The next step involves transforming the entity type embeddings into a form that makes them directly comparable to the representations of text spans.

**INPUT**: Each entity embedding is passed through a two-layer feedforward neural network (FFN).  
**OUTPUT**: A set of **refined entity vectors**, one for each entity type.

##### Matching Spans with Entity Types

After generating the embeddings for both spans and entity types, the model aims to identify which spans correspond to which entity types. Rather than assigning labels directly, it measures the similarity between each span and each entity type by comparing their vectors within a **shared latent space**.

For each possible combination of span and entity type in a sentence, the model calculates a **matching score** by taking the **dot product** of their embeddings and applying a **sigmoid function** to convert the result into a probability between 0 and 1. The higher the score, the more likely it is that the span belongs to that entity type. If a span like *“Elton John”* has an embedding close to the vector for *person*, the model assigns a high score (for example, 0.94), indicating strong confidence that it is indeed a person.

###### Traning Phase

During training, the model learns to distinguish correct span–entity type pairs from incorrect ones. The goal is simple:

* For **positive pairs** (e.g., *“Elton John“* + *person*), the model is penalised if the score is too low.
* For **negative pairs** (e.g., *“Elton John“* + *location*), it is penalised if the score is too high.

This learning process is guided by a **binary cross-entropy loss**, with an **indicator function** identifying whether a pair is positive or negative. Over time, the model learns to assign **high probabilities to correct pairs** and **low probabilities to incorrect ones**, gradually improving its ability to identify which spans represent which entity types.

###### Decoding Phase

At inference time, the model applies the same scoring mechanism described above (dot product + sigmoid function). Once the scores are computed, a **greedy span selection** strategy is applied: only **spans** **with a score above 0.5 are selected**. To efficiently choose the best candidates, a **priority queue** is used, ranking spans based on their matching scores.

## The Evolution of GLiNER

Since its debut in 2023, GLiNER has gone through several iterations (up to version 2.1), each introducing more robust models and improved multilingual capabilities.  
In addition, in August 2024, the [GLiNER Multi-Task](https://arxiv.org/pdf/2406.12925) model was released with the goal of extending the original GLiNER approach to handle multiple tasks, not just Named Entity Recognition (NER), such as Open NER, Relation Extraction, Summarization, Question-answering and Open Information Extraction.  
For a full and up‑to‑date list of available GLiNER models, check out the Hugging Face page [here](https://huggingface.co/models?library=gliner).

However, GLiNER presents some limitations, as shown in these two blog posts [[1](https://medium.com/@shahrukhx01/illustrated-gliner-e6971e4c8c52), [2](https://blog.knowledgator.com/meet-the-new-zero-shot-ner-architecture-30ffc2cb1ee0)]:

* Entity representations are conditioned on their order due to the Transformer’s positional encoding layer, which does not make much sense for NER tasks where entity order is irrelevant.
* Performance degrades when the number of entity types exceeds approximately 30.
* Since the model works by concatenating entity labels and input text into a single sequence, if the number of entity labels is much higher than the number of words in the input text, it creates unnecessary and inefficient computational overhead.

For these reasons, two new architectures have been introduced recently:

* **Bi-encoder models** (such as [ModernGLiNER](https://huggingface.co/knowledgator/modern-gliner-bi-large-v1.0)), which process the input text and entity labels separately, using two distinct transformer models (as you can see from the picture below: a bi-directional sentence transformer as entity type encoder and a bi-directional transformer for encoding input sequence).
* **Poly-encoder models**, which extend the bi-encoder approach by introducing a post-fusion step that explicitly models the interaction between the input text and the entity representations.

![](https://i0.wp.com/sease.io/wp-content/uploads/2026/01/Screenshot-2025-07-03-alle-16.30.08.png?fit=800%2C526&ssl=1)

*Bi-encoder model Architecture from the blog post* *[Meet the new zero-shot NER architecture](https://blog.knowledgator.com/meet-the-new-zero-shot-ner-architecture-30ffc2cb1ee0)*

A deep dive into these architectures is beyond the scope of this blog; this was just meant to give you an overview of how the GLiNER models have evolved. The same holds for this [blog post](https://blog.knowledgator.com/llm2encoders-e7d90b9f5966), where the authors highlight other limitations of the original GLiNER models, including:

* training on relatively small text corpora (limiting the overall generalisation capabilities)
* reliance on outdated encoder architectures
* lack of support for modern optimisations like flash-attention
* strict context window limits (up to 512 tokens), with performance degrading when extended ([reference](https://github.com/urchade/GLiNER/issues/183))

To overcome these limitations, newer models such as [knowledgator/gliner-llama-1B-v1.0](https://huggingface.co/knowledgator/gliner-llama-1B-v1.0) have been introduced. These models adopt the **LLM2Vec approach**, which transforms decoder-only architectures (like LLaMA, GPT, or Qwen) into bidirectional encoders (like BERT). This strategy enables the use of advanced language models while retaining the efficiency and task-specific benefits of encoder-based designs.

---

This concludes our introduction to GLiNER. To see whether GLiNER can be a viable alternative to large language models (LLMs) for **query parsing**tasks, stay tuned for the second blog post in this series.

## Need Help With This Topic?​​

If you’re struggling with GLiNER, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with GLiNER, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)