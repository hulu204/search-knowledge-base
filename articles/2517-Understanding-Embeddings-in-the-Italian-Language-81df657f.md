---
title: 'Understanding Embeddings in the Italian Language – Part 1'
company: Sease
tag: 召回
date: 2026-09-17
url: https://sease.io/2026/09/understanding-vector-embeddings-in-the-italian-language-part-1.html
account: 
origin: en-rss
---
Hi everyone!

In this series of four blog posts, I’m going to describe my master’s degree dissertation done with the supervision of Prof. Alberto Testolin at the University of Padova, in collaboration with Siav S.p.a, a company based in Italy. The primary objective of this project is to assess the effectiveness of open-source multilingual embedding models in handling the Italian language within the semantic search task, and to investigate fine-tuning as a means of enhancing their performance.

This series is spread across four blog posts, which will cover:

* Part 1 will contain a first part where the motivation behind the study is presented, and also an overview of all the datasets used in the process, training, validation, and testing.
* Part 2 will cover all the embedding models used in this study.
* Part 3 will explore all the methodologies adopted during the development of this work, from how we fine-tuned the model to how we dealt with statistical assessment of the results.
* Part 4 will be the last, covering the exposition of the results, and I will sum up what I found from this thesis.

Let’s start with part 1, then. Hope you’ll find this study helpful!

## Motivation

Have you ever found yourself reading tons of documents related to a topic, ending up overwhelmed by the too-big load of information? Yeah, me too! Now, the next step is the following: can we develop a system capable of providing a more readable answer (for example, in a natural language fashion) for us? This could have several significant benefits to the company using this system.

First, the ease of interaction is greatly improved. When users ask a question in plain language, they expect a direct response that addresses their query, rather than having to search through multiple documents or links to find relevant information. Second, there is a notable reduction in information overload for the user. Simply presenting users with documents or links to resources can often overwhelm them, especially when the query is complex. In this case, natural-language answers make it more inclusive and user-friendly.

The main idea is to use a Large Language Model (LLM) as a kind of search engine, bypassing the need to examine various websites ranked by traditional algorithms or, even better, enhancing them. The goal is for the model to generate a natural language response directly. To achieve this, the most straightforward approach might be to rely on the assumption that the LLM has already learned the necessary information during its training. By simply providing a query describing the topic of interest, one could hope the model would infer the answer. Although this may seem like a viable alternative, there exists a phenomenon known as “hallucination”, where the model produces conceivable responses, but the content is incorrect or entirely fabricated. This occurs because LLMs generate output based on patterns learned during training.  
This also means that the information learned by an LLM is fixed to the time of its training data. For instance, if we were to ask it questions about current events, it would either be unable to provide an answer or would likely generate fabricated information. As a result, they may often provide confident yet inaccurate responses, particularly when the query falls outside their knowledge base.

A potential solution to this problem is Retrieval-Augmented Generation (RAG). It combines the natural language generation capabilities of LLMs with external retrieval systems, offering a solution to some of the key limitations inherent in LLMs, particularly the issues of hallucination, incomplete or outdated information, and limited domain-specific knowledge.

In a RAG system, instead of relying solely on the pre-trained LLM parameters, which include knowledge only from its training data, the system retrieves the most relevant documents from a predefined external database. These documents are then passed as input to the LLM, ensuring that the model has access to up-to-date or domain-specific information to generate a response. This allows RAG systems to provide an additional layer of transparency by allowing users to trace the sources of the generated responses. When the LLM generates an answer based on retrieved documents, those documents can be presented alongside the response, enabling users to verify the information and build trust in the system.

A huge problem in RAG is to be able to retrieve the right documents to send as context to the LLM. The retrieval step represents a fundamental component of any RAG pipeline, as the quality of the retrieved documents directly determines the effectiveness and reliability of the generated output.

The company, Siav S.p.A., assigned me this work with the idea of starting to replace paid OpenAI’s embeddings with the goal of reducing costs and retrieving better quality results from vector search, since they had some complaints while using OpenAI’s model specifically for the Italian language.

Summing up, this study was conducted to evaluate the feasibility of replacing paid embeddings with privately fine-tuned or pre-trained models, in terms of cost, accuracy, and latency, on an Italian-only dataset. The next step will be to exploit these results for doing RAG, but this is out of scope for this work.

## Datasets

In this section, we explore the datasets used to train and evaluate both the new privately fine-tuned models and the native ones (used in a feature-extraction fashion). We decided to use 2 different datasets:

* [mMARCO](https://github.com/unicamp-dl/mMARCO) for training purposes
* [DBpedia-Entity-v2](https://github.com/iai-group/DBpedia-Entity/) [[1](#1)] for validation and testing purposes

### Training

The [unicamp-dl/mmarco](https://github.com/unicamp-dl/mMARCO) dataset is a multilingual version of the Microsoft MS MARCO [[2](#1)] passage ranking dataset, created by researchers at the University of Campinas (Unicamp) [[3](#3)] in Brazil. This dataset is composed of 14 different languages, but we are interested only in the Italian part. Each language is composed of about 39 million samples. Every sample is a triplet, composed of:

* query text;
 * list of positive documents’ text;
 * list of negative documents’ text.

The dataset serves as the foundation for fine-tuning the models that we will describe later.

### Validation/Test

*DBpedia-Entity-v2* *[[1](#1)]* is a standard test collection for entity search over the DBpedia knowledge base, and the dataset is available under the MIT license. The dataset is provided by the Hugging Face website ([April 2024 version](https://huggingface.co/datasets/mteb/dbpedia)). DBpedia is a community effort. It was released in 2017 and is a result of a collaborative effort between the [IAI](https://iai.group/) group of the University of Stavanger, the Norwegian University of Science and Technology, Wayne State University, and Carnegie Mellon University.

The dataset is divided into 3 parts:

* corpus;
* queries;
* qrels.

##### Corpus

Our corpus includes roughly 4.6 million documents from DBpedia, with each entry organised into three fields: an *id*, a *title*, and the *text*.

##### Queries

Queries are organised into four categories:

* SemSearch ES: These are short and ambiguous queries that search for a particular entity.
* INEX-LD: These are keyword queries, much more like traditional Information Retrieval.
* List Search: These are made to find a particular list of entities.
* QALD-2: These are classical questions in natural language.

This leads to a total of 467 queries structured as a couple: (*query-id*, *query-text*). **67 of them are used as validation queries, and the other 400 as test ones**.

The distribution is the following:

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Category** | **#queries** | **Type** | **R1** | **R2** |
| SemSearch ES | 113 | named entities | 12.5 | 3.0 |
| INEX-LD | 99 | keyword queries | 23.5 | 9.2 |
| ListSearch | 115 | list of entities | 18.1 | 12.7 |
| QALD-2 | 140 | NL questions | 28.4 | 29.8 |
| **Total** | **467** |  | **21.0** | **14.7** |

*Query categories in DBpedia-Entity-v2. R1 and R2 refer to the average number of relevant and highly relevant documents per query, respectively. [[1](#1)]*

##### Qrels: Relevance Judgements

This section of the dataset contains 49,280 relevance judgments—also known as *qrels*—organised as *(query-id, corpus-id, score)*. The score can take the values ∈ {0, 1, 2}, each representing a different degree of relevance:

* Highly relevant (2): the entity is a direct answer to the query (i.e., the entity should be among the top answers).
 * Relevant (1): the entity helps one to find the answer to the query (i.e., the entity can be shown as an answer to the query, but not among the top results).
 * Irrelevant (0): the entity has no relation to the intent of the query (i.e., the entity should not be shown as an answer)

**To simplify this study, we decided to deal with “highly relevant” and “relevant” degrees of relevance as if they were the same. In this way, we are able to compute even Boolean IR metrics.** To do so, we assign the value of 1 to both relevant classes and keep the zero value to the irrelevant documents.

Since we are interested in the application of embeddings for the Italian language, we translated the entire dataset (corpus and query texts), which was fully in English, into Italian using an open-source transformer-based model [[4](#4)] made by the Language Technology Research Group of the University of Helsinki, specifically trained to translate from English to Italian, namely [opus-mt-en-it](https://huggingface.co/Helsinki-NLP/opus-mt-en-it) [[5](#5)][[6](#6)]. **We decided to address translation problems by using a Google Translate API.** We used a Python script to translate the *DBpedia-Entity-v2* dataset [[1](#3)] query through [opus-mt-en-it](https://huggingface.co/Helsinki-NLP/opus-mt-en-it), and then we used the Google Translate API to refine the translation errors.

## REFERENCES

[1] F. Hasibi, F. Nikolaev, C. Xiong, K. Balog, S. E. Bratsberg, A. Kotov, and J. Callan, “DBpedia-entity v2: A test collection for entity search,” in Proceedings of the 40th International ACM SIGIR Conference on Research and Development in Information Retrieval, ser. SIGIR ’17.

[2] P. Bajaj, D. Campos, N. Craswell, L. Deng, J. Gao, X. Liu, R. Majumder, A. McNamara, B. Mitra, T. Nguyen, M. Rosenberg, X. Song, A. Stoica, S. Tiwary, and T. Wang, “MS marco: A human generated machine reading comprehension dataset,” 2018. [Online]. [Link](https://arxiv.org/abs/1611.09268).

[3] L. Bonifacio, V. Jeronymo, H. Q. Abonizio, I. Campiotti, M. Fadaee, R. Lotufo, and R. Nogueira, “mmarco: A multilingual version of the ms marco passage ranking dataset,” 2022. [Online]. [Link](https://arxiv.org/abs/2108.13897).

[4] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, “Attention is all you need,” 2023. [Online]. [Link](https://arxiv.org/abs/1706.03762).

[5] J. Tiedemann and S. Thottingal, “OPUS-MT — Building open translation services for the World,” in Proceedings of the 22nd Annual Conference of the European Association for Machine Translation (EAMT), Lisbon, Portugal, 2020.

[6] J. Tiedemann, M. Aulamo, D. Bakshandaeva, M. Boggia, S.-A. Grönroos, T. Nieminen, A. Raganato, Y. Scherrer, R. Vazquez, and S. Virpioja, “Democratizing neural machine translation with OPUS-MT,” Language Resources and Evaluation, no. 58, pp. 713–755, 2023.

## Bringing Information Retrieval research into production

Research is where better search starts. If you're exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[Talk to our search experts](mailto:info@sease.io)

## Bringing Information Retrieval Research Into Production

Research is where better search starts. If you’re exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[Click here](mailto:info@sease.io)