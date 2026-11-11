---
title: 'Understanding Embeddings in the Italian Language – Part 2'
company: Sease
tag: 召回
date: 2026-09-24
url: https://sease.io/2026/09/understanding-embeddings-in-the-italian-language-part-2.html
account: 
origin: en-rss
---
Hi everyone! Welcome back!

This blog post is the second one of the series related to my Master’s thesis (if you missed the first one, here is the [link](https://sease.io/2026/09/understanding-vector-embeddings-in-the-italian-language-part-1.html) 😉).  
This time we’ll cover:

* Embedding models used in the study
  + LaBSE
  + multilingual-e5-large
  + bge-m3

Hope you’ll find this study helpful!

## Embedding Models

Since the company aimed to replace OpenAI’s model for vector search, we focused our search on alternative embedding models they could use. In particular, we looked for (open-source) multilingual models in a benchmark called [MTEB](https://huggingface.co/mteb) (Massive Text Embedding Benchmark, from [HuggingFace](https://huggingface.co/)).

Here it is an overview of the 3 embedding models selected for this study.

### LaBSE: Language-Agnostic BERT Sentence Embedding

[*LaBSE*](https://huggingface.co/sentence-transformers/LaBSE) [[1](#1)] is a multilingual sentence embedding model developed by Google AI. It is designed to encode text from 109 different languages in a shared vector space.

Its architecture consists of a 12-layer transformer [[2](#2)] that leverages a vocabulary size of 500,000 tokens, ensuring comprehensive coverage across the supported languages (including Italian). The window size is only 256 tokens for this model. This is the smallest of the neural embedding models, with a total of approximately 471.517.440 parameters.

The embedding networks in *LaBSE* are initialised using pre-trained BERT weights and further trained through two techniques: Masked Language Modelling (MLM) and Translation Language Modelling (TLM). The MLM pre-training uses monolingual data from sources like CommonCrawl and Wikipedia, while TLM employs concatenated bilingual translation pairs derived from a bitext mining system.

The embedding related to the [`CLS]` token is used as the embedding of the full text. For computational efficiency, the model uses a dot-product scoring function to compute pairwise similarity scores on the embeddings. The softmax operation is applied to the resulting scores to classify the embeddings.

*LaBSE* model achieved medium results on benchmarks such as the MTEB (English text embeddings), scoring an *nDCG@10* of 45.2.

Despite its capabilities, the model has some limitations. For example, it truncates long texts to a maximum of 256 tokens, which surely affects its performance on longer documents. Additionally, while it performs robustly across many languages, some low-resource languages may experience reduced effectiveness. Moreover, the embedding dimension is 768, which is lower compared to the other models that will be presented later. That could result in a lower representation capability.

### multilingual-e5-large

The [*multilingual-e5-large*](https://huggingface.co/intfloat/multilingual-e5-large) model [[3](#3)] represents a multilingual extension of the English e5 model, allowing it to support more than 100 languages. Developed based on the XLM-RoBERTa architecture, it comprises 24 layers and generates embeddings of 1024 size. The window size is 512 tokens for this model. This is the middle neural embedding model in terms of parameters, with a total of 559.890.432 parameters.

It is trained through a two-stage methodology. First, it undergoes weakly-supervised contrastive pre-training on approximately 1 billion multilingual text pairs from diverse sources (e.g., Wikipedia, mC4, and Reddit). This is followed by supervised fine-tuning on 1.6 million high-quality labelled datasets, incorporating mined hard negatives and knowledge distillation to enhance embedding quality.

The input handling of *multilingual-e5-large* requires specific prefixes for queries and documents’ passages, denoted as “query: ” and “passage: “, respectively.

The embedding of the full text is computed with the element-wise mean of all the embeddings of the tokens that compose the text.

The model achieved good results on benchmarks such as MTEB (English text embeddings) and MIRACL (multilingual retrieval across 16 languages). In the MTEB, *multilingual-e5-large* scored an *nDCG@10* of 61.5. **In the MIRACL dev set, this model achieved an average (on all languages)nDCG@10 of 66.5.**

Despite its impressive capabilities, the model has some limitations. For example, it truncates long texts to a maximum of 512 tokens, which may affect its performance on longer documents. Additionally, while it performs robustly across many languages, some low-resource languages may experience reduced effectiveness.

### bge-m3

[*bge-m3*](https://huggingface.co/BAAI/bge-m3) [[4](#9)], developed by the Beijing Academy of Artificial Intelligence (BAAI), is an advanced sentence transformer model that stands out for its multi-functionality, multi-linguality, and multi-granularity capabilities (the 3 Ms). Developed based on the XLM-RoBERTa architecture adapted by the RetroMAE method (a retrieval-oriented pre-training paradigm based on the Masked Auto-Encoder [[5](#10)]), it comprises 24 layers and generates embeddings of size 1024. One of the standout features of this model is its window size of 8192 tokens, allowing it to accommodate entire documents. This is the largest of the neural embedding models, with a total of 567.754.752 parameters.

This model is developed to address significant challenges in multi-linguality, retrieval functionalities, and input granularity. By learning a shared semantic space enables both monolingual retrieval within individual languages and cross-lingual retrieval between different languages, supporting more than 100 world languages. This versatility makes *bge-m3* a powerful tool for multilingual and cross-lingual applications.

The model is designed to generate embeddings that are not restricted to a single retrieval approach. Instead, it supports multiple retrieval paradigms, including dense retrieval, sparse retrieval, and multi-vector retrieval. The `[CLS]` token embedding is optimised for dense retrieval, whereas embeddings derived from other tokens enable sparse and multi-vector retrieval functionalities. We decided to stick to the default one in the sentence-transformers library, using the embedding related to the `[CLS]` token as the embedding of the full input text.

The *bge-m3* training process incorporates several innovative techniques to enhance the quality of the embeddings. One key advancement is the introduction of a self-knowledge distillation framework. **This approach jointly learns and reinforces the three retrieval functionalities mentioned above**. These signals act as teacher guidance, enabling the model to improve performance through an ensemble learning approach.

To further optimise training, the model employs a high-performance batching strategy that facilitates large batch sizes, contributing significantly to the discriminative power of the embeddings. In addition, the training process benefits from extensive and high-quality data curation. This includes leveraging unsupervised data from vast multilingual corpora, integrating related supervised datasets, and synthesising data to address gaps in scarce training samples. Each of these data sources complements the others and is applied at different training stages, ensuring a robust training process.

The model achieved remarkable results on benchmarks such as MTEB (English text embeddings) and MIRACL (multilingual retrieval across 16 languages). **In the MIRACL dev set, this model achieved an average (on all languages) nDCG@10 of 71.5**.

### text-embedding-3-small

The [*text-embedding-3-small*](https://openai.com/index/new-embedding-models-and-api-updates/) model is an embedding model from OpenAI, designed to enhance the performance of text representation tasks while being cost-effective.

Compared to its predecessor, *text-embedding-ada-002*, the *text-embedding-3-small* model delivers a clear boost in performance. The average score on the multi-language retrieval benchmark (MIRACL) has risen from 31.4% to 44.0%, while the average score on English tasks (MTEB) has increased from 61.0% to 62.3%.

The price for using *text-embedding-3-small* has been reduced significantly (by five times compared to the previous model), making it more accessible to developers. The cost is low: $0.00002 per 1,000 tokens.

The model produces embeddings with a size of 1536 dimensions, allowing for a rich representation of the text’s semantic content; however, this also slightly downgrades efficiency.

## REFERENCES

[1] F. Feng, Y. Yang, D. Cer, N. Arivazhagan, and W. Wang, “Language-agnostic bert sentence embedding,” 2022. [Online]. [Link](https://arxiv.org/abs/2007.01852).

[2] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, “Attention is all you need,” 2023. [Online]. [Link](https://arxiv.org/abs/1706.03762).

[3] L. Wang, N. Yang, X. Huang, L. Yang, R. Majumder, and F. Wei, “Multilingual e5 text embeddings: A technical report,” 2024. [Online]. [Link](https://arxiv.org/abs/2402.05672).

[4] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, “Bge m3-embedding: Multilingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation,” 2024. [Online]. [Link](https://arxiv.org/abs/2402.03216).

[5] S. Xiao, Z. Liu, Y. Shao, and Z. Cao, “Retromae: Pre-training retrieval-oriented language models via masked auto-encoder,” 2022. [Online]. [Link](https://arxiv.org/abs/2205.12035).

## Bringing Information Retrieval research into production

Research is where better search starts. If you're exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[Talk to our search experts](mailto:info@sease.io)

## Bringing Information Retrieval research into production

Research is where better search starts. If you’re exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[Talk to our search experts](mailto:info@sease.io)