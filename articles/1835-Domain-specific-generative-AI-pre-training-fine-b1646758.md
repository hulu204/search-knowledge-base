---
title: 'Domain specific generative AI: pre-training, fine-tuning, and RAG'
company: Elastic
tag: RAG
date: 2023-11-22
url: https://www.elastic.co/search-labs/blog/domain-specific-generative-ai-pre-training-fine-tuning-rag
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Domain specific generative AI: pre-training, fine-tuning, and RAG

Explore strategies for integrating domain-specific knowledge into large language models (LLMs) through pre-training, fine-tuning, and RAG.

November 22, 2023

[Steve Dodson](/search-labs/author/steve-dodson)

[AI](/search-labs/blog/category/ai)

Jump to

Share

There are a number of strategies to add domain specific knowledge to large language models (LLMs), and more approaches are being investigated as part of [an active research field](https://acl2023-retrieval-lm.github.io/). Methods such as pre-training and fine-tuning on domain specific datasets allow the LLM to reason and generate domain specific language. However, using these LLMs as knowledge bases is still prone to hallucinations. If the domain language is similar to the LLM training data, using external information retrieval systems via Retrieval Augmented Generation (RAG) to provide contextual information to the LLM can improve factual responses. Ultimately, a combination of fine-tuning and RAG may provide the best result.

The blog attempts to describe some of the basic processes for storing and retrieving knowledge from LLMs. Followup blogs will describe different RAG strategies in more detail.

|  | Pre-training | Fine-tuning | Retrieval Augmented Generation |
| --- | --- | --- | --- |
| Training duration | Days to weeks to months | Minutes to hours | Not required |
| Customisation | Requires large amount of domain training data Can customise model architecture, size. tokenizer etc. Creates new “foundation” LLM model | Add domain-specific data Tune for specific tasks. Updates LLM model. | No model weights. External information retrieval system can be tuned to align with LLM. Prompt can be optimised for task performance. |
| Objective | Next-token prediction | Increase task performance | Increase task performance for specific set of domain documents |
| Expertise | High | Medium | Low |

## Introduction to domain specific generative AI

Generative AI technologies, built on large language models (LLMs), have substantially progressed our ability to develop tools for processing, comprehending, and generating text. Furthermore, these technologies have introduced an innovative information retrieval mechanism, wherein generative AI technologies directly respond to user queries using the stored (parametric) knowledge of the model.

However, it's important to note that the parametric knowledge of the model is a condensed representation of the entire training dataset. Thus, employing these technologies for a specific knowledge base or domain beyond the original training data does come with certain limitations, such as:

* The generative AI's responses might lack context or accuracy, as they won't have access to information that wasn't present in the training data.
* There is potential for generating plausible-sounding but incorrect or misleading information ([hallucinations](https://aclanthology.org/2021.findings-emnlp.320.pdf)).

Different strategies exist to overcome these limitations, such as extending the original training data, fine-tuning the model, and integrating with an external source of domain-specific knowledge. These various approaches yield distinct behaviours and carry differing implementation costs.

## Strategies for integrating domain-specific knowledge into LLMs

### Domain specific pre-training for LLMs

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt928972dfb98a9f9c/6a1711fc0e2e4915dc41a26a/85cabbc57c68146c67a4bf978e1dd5549a20923c-960x540.png)

LLMs are pre-trained on huge corpora of data that represent a wide range of natural language use cases:

| Model | Total dataset size | Data sources | Training cost |
| --- | --- | --- | --- |
| PaLM 540B | 780 billion tokens | Social media conversations (multilingual) 50%; Filtered web pages (multilingual) 27%; Books (English) 13%; GitHub (code) 5%; Wikipedia (multilingual) 4%; News (English) 1% | 8.4M TPU v2 hours |
| GPT-3 | 499 billion tokens | Common Crawl (filtered) 60%; WebText2 22%; Books1 8%; Books2 8%; Wikipedia 3% | 0.8M GPU hours |
| LLaMA 2 | 2 trillion tokens | “mix of data from publicly available sources” | 3.3M GPU hours |

The costs of this pre-training step are substantial, and there’s a significant amount of work required to curate and prepare the datasets. Both of these tasks require a high level of technical expertise.

In addition, pre-training is only one step in creating the model. Typically, the models are then fine-tuned on a narrower dataset that is carefully curated and tailored for specific tasks. This process also typically involves human reviewers that rank and review possible model outputs to improve the model’s performance and safety. This adds further complexity and cost to the process.

Examples of this approach applied to specific domains include:

* [ESMFold](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v1.full.pdf), [ProGen2](https://arxiv.org/pdf/2206.13517.pdf) and others - LLM for protein sequences: protein sequences can be represented using language-like sequences but are not covered by natural language models
* [Galactica](https://arxiv.org/pdf/2211.09085.pdf) - LLM for science: trained exclusively on a large collection of scientific datasets, and includes special processing to handle scientific notations
* [BloombergGPT](https://arxiv.org/pdf/2303.17564.pdf) - LLM for finance: trained on 51% financial data, 49% public datasets
* [StarCoder](https://arxiv.org/pdf/2305.06161.pdf) - LLM for code: trained on 6.4TB of permissively licensed source code in 384 programming languages, and included 54 GB of GitHub issues and repository-level metadata

The domain-specific models generally outperform generalist models within their respective domains, with the most significant improvements observed in domains that differ significantly from natural language (such as protein sequences and code). However, for knowledge-intensive tasks, these domain-specific models suffer from the same limitations due to their reliance on parametric knowledge. Therefore, while these models can understand the relationships and structure of the domain more effectively, they are still prone to inaccuracies and hallucinations.

### Domain specific fine-tuning for LLMs

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt6649b2195ef435cb/6a1711fde8fbce8a4e39fd73/f9c42e2b3fae929312f17d429fea1c11e44357f9-960x540.png)

Fine-tuning for LLMs involves training a pre-trained model on a specific task or domain to enhance its performance in that area. It adapts the model's knowledge to a narrower context by updating its parameters using task-specific data, while retaining its general language understanding gained during pre-training. This approach optimises the model for specific tasks, saving significant time compared to training from scratch.

#### Examples

* [Alpaca](https://crfm.stanford.edu/2023/03/13/alpaca.html) - fine-tuned LLaMA-7B model that behaves qualitatively similarly to OpenAI’s GPT-3.5
* [xFinance](https://www.stochastic.ai/blog/xfinance-vs-bloomberg-gpt) - fine-tuned LLaMA-13B model for financial-specific tasks. Reportedly outperforms BloombergGPT
* [ChatDoctor](https://arxiv.org/pdf/2303.14070.pdf) - fine-tuned LLaMA-7B model for medical chat.
* [falcon-40b-code-alpaca](https://huggingface.co/jinaai/falcon-40b-code-alpaca) - fine-tuned falcon-40b model for code generation from natural language

#### Costs: fine-tuning vs. pre-training LLMs

Costs for fine-tuning are significantly smaller than for pre-training. In addition, novel methods such as parameter-efficient fine-tuning ([PEFT](https://github.com/huggingface/peft)) methods (e.g. [LoRA](https://arxiv.org/pdf/2106.09685.pdf), adapters, prompt tuning, and in-context learning as described above) enable very efficient adaptation of pre-trained language models (PLMs) to various downstream applications without fine-tuning all the model's parameters. For example,

| Model | Fine-tuning method | Fine-tuning dataset | Cost |
| --- | --- | --- | --- |
| Alpaca | Self-Instruct | 52K unique instructions and the corresponding outputs | 3 hours on 8 80GB A100s:24 GPU hours |
| xFinance | Unsupervised fine-tuning and instruction fine-tuning using xTuring library | 493M token text dataset; 82K instruction dataset | 25 hours on 8 A100 80GB GPUs:200 GPU hours |
| ChatDoctor | Self-Instruct | 110K patient-doctor interactions | 3 hours on 6 A100 GPUS: 18 GPU hours |
| falcon-40b-code-alpaca | Self-Instruct | 52K instruction dataset; 20K instruction-input-code triplets | 4 hours on 4 A100 80GB GPUs: 16 GPU hours |

Similar to domain-specific pre-trained models, these models typically exhibit better performance within their respective domains, yet they still face the limitations associated with parametric knowledge.

### Enhancing LLMs with Retrieval Augmented Generation (RAG)

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/bltabcd8f29eadaa390/6a1711ffb0367d9da172be36/1dde84a8973bbf045dc9024ee5619ee5b7459a9f-960x540.png)

LLMs store factual knowledge in their parameters, and their ability to access and precisely manipulate this knowledge is still limited. This can lead to LLMs providing non-factual but seemingly plausible predictions (hallucinations) - particularly for unpopular questions. Additionally, providing references for their decisions and updating their knowledge efficiently remain open research problems.

A general purpose recipe to address these limitations is RAG, where the LLM's parametric knowledge is grounded with external or non-parametric knowledge from an information retrieval system. This knowledge is passed as additional context in the prompt to the LLM and specific instructions are given to the LLM on how to use this contextual information. This keeps it more inline with the discussion so far about parametric knowledge. The advantages of this approach are:

* Unlike fine-tuning and pre-training, LLM parameters do not change and so there are no training costs
* Expertise required to simple implementation is low (although more advanced strategies exist)
* Response can be tightly constrained to context returned from the information retrieval system, limiting hallucinations
* Smaller task specific LLMs can be used - as the LLM is being used for a specific task rather than a knowledge base.
* Knowledge base is easily updatable as it requires no changes to the LLM
* Responses can cite sources for human verification and link outs

Strategies to combine this non-parametric knowledge (i.e. retrieved text) with an LLM’s parametric knowledge is an [active area of research](https://acl2023-retrieval-lm.github.io/slides/3-architecture.pdf).

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt04a78b28c5eab515/6a171201cdacbf9af27d2b12/beec836f570eaf9a6a5945ee869e1d37e89e3190-1014x463.png)

Some of these approaches involve modifying the LLM in conjunction with the retrieval strategy and so can not be classified as distinctly as the definitions in this blog. We will dive into more details in further blogs.

## Example

In a simple example, we utilised a fine-tuned LLaMA2 13B model, which was based on the information from this [blog](https://towardsdatascience.com/leveraging-qlora-for-fine-tuning-of-task-fine-tuned-models-without-catastrophic-forgetting-d9bcd594cff4). This model underwent fine-tuning using AWS blog posts published after the LLaMA2 pre-training and fine-tuning data cutoff date, specifically those from July 23rd, 2023. We also ingested these documents into a Elasticsearch and established a simple RAG pipeline. In this pipeline, model responses are generated based on the retrieved documents serving as context. Red highlights indicate incorrect responses, and blue highlights correct responses.

![](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt04470fdb73579b8d/6a171203839dfac0f5dcfffd/55da35f1cce6f015d38b1e49f16c47d12da95f74-960x540.png)

However, it's important to note that this is just a single example and does not constitute a comprehensive evaluation of fine-tuning versus RAG, but provides an example of fine-tuning before [useful for form, not facts](https://www.anyscale.com/blog/fine-tuning-is-for-form-not-facts).. We plan to conduct more thorough comparisons in upcoming blogs.

### Frequently Asked Questions

#### What strategies can be used to add domain-specific knowledge into large language models (LLMs)?

Several strategies can be employed to integrate domain-specific knowledge into large language models (LLMs). These include pre-training the model, fine-tuning it, and utilizing Retrieval Augmented Generation (RAG).

#### How does Retrieval Augmented Generation (RAG) enhance generative AI models?

Retrieval Augmented Generation (RAG) enhances generative AI models by providing contextual information from external sources, improving factual responses and reducing hallucinations.

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