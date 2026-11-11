---
title: 'Short queries, formal documents: how HyDE improved semantic search precision by 50% in Elasticsearch'
company: Elastic
tag: 召回
date: 2026-07-07
url: https://www.elastic.co/search-labs/blog/hyde-semantic-search-elasticsearch
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Short queries, formal documents: how HyDE improved semantic search precision by 50% in Elasticsearch

HyDE boosts semantic search precision and recall by 50% on short queries. Here's how to implement it in Elasticsearch with the Inference API and semantic\_text.

July 07, 2026

[Jeffrey Rengifo](/search-labs/author/jeffrey-rengifo)

[AI](/search-labs/blog/category/ai)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

[Hypothetical Document Embeddings (HyDE)](https://arxiv.org/abs/2212.10496) improves semantic search precision and recall by 50% on short, casual queries against formal document corpora, without reindexing or changing your embedding model. The technique works by asking an LLM to generate a hypothetical document that matches your query, then using that document's embedding as the search vector. The fake document gets discarded; only real results come back. This post shows you how to implement HyDE in Elasticsearch using the [Inference API](https://www.elastic.co/docs/api/doc/elasticsearch/group/endpoint-inference) and [`semantic_text`](https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/semantic-text), measure it against a baseline with precision, recall and MRR, and decide when it's worth the extra LLM round trip.

## Prerequisites

* Elastic Cloud cluster or Elasticsearch 9.x+ ([start a free trial](https://cloud.elastic.co/registration))
* Python 3.9+
* An OpenAI API key for hypothetical document generation.

## What is HyDE, and why does it work?

HyDE closes the embedding gap between short queries and formal documents by generating a full-length hypothetical document in the same register as the corpus before embedding.

An embedding doesn't just encode a topic. It encodes topic, register, vocabulary density, and sentence structure, all packed into one vector. A four-word casual query, like "[adamw](https://huggingface.co/docs/bitsandbytes/reference/optim/adamw) vs Adam transformers", carries a handful of semantic signals, so its embedding sits in a vague region of the vector space. A 200-word abstract covering the same subject packs dozens of reinforcing terms (weight decay, gradient update, convergence, generalization) that anchor its embedding much more precisely. The result: A semantic search for the short query can drift toward loosely related papers instead of landing on the best matches.

HyDE closes this gap by asking an LLM to write a document in the same style as the corpus before embedding, a strategy that complements other [query rewriting techniques for improving search quality](https://www.elastic.co/search-labs/blog/query-rewriting-llm-search-improve). The flow looks like this:

![A flowchart showing a query “why adamw transformers” leading to a hypothetical document about AdamW and transformer architectures and then embedding into a vector search that returns three search results titled “Understanding AdamW through Proximal Methods,” “Trainable Weight Averaging for Fast Convergence,” and “Subformer: Exploring Weight Sharing.”](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt93a5427364d1de85/6a55e6e124d080d63d8be859/08a534d19eb2e8ef64cd4bc5760efae181c45d29-1999x1311.png)

The hypothetical document doesn’t need to be factually correct. It may contain false details, and that’s fine, because the document is thrown away after its embedding is extracted. The user only ever sees real documents from the index.

This technique was introduced in [Precise Zero-Shot Dense Retrieval without Relevance Labels](https://arxiv.org/abs/2212.10496) (Gao et al., 2022).

## How to set up HyDE in Elasticsearch

All the code snippets will be available in the [companion notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/hyde-hypothetical-document-embeddings-elasticsearch/notebook.ipynb), if you prefer to run everything at once.

### **Load the ML arXiv dataset**

We sample 5,000 papers from [CShorten/ML-ArXiv-Papers](https://huggingface.co/datasets/CShorten/ML-ArXiv-Papers): machine-learning arXiv titles and abstracts. This gives us a corpus of formal, technical documents, the kind where short queries struggle most.

```
from datasets import load_dataset

dataset = load_dataset("CShorten/ML-ArXiv-Papers", split="train")
dataset = dataset.shuffle(seed=42).select(range(5000))
print(f"Sampled {len(dataset)} papers")
```

### **Index with semantic\_text**

Elasticsearch as a vector database lets us handle embedding generation, storage, and search in a single system. We use the `.jina-embeddings-v5-text-small` inference endpoint, preconfigured in Elastic Cloud. The [`copy_to`](https://www.elastic.co/guide/en/elasticsearch/reference/current/copy-to.html) parameter lets a single `semantic_text` field cover both `title` and `abstract`, so both fields are embedded and searchable through one vector. This [walkthrough of the semantic\_text GA release](https://www.elastic.co/search-labs/blog/elasticsearch-semantic-text-ga) covers the full capabilities of this field type, including semantic highlighting.

```
INDEX_NAME = "arxiv-ml-papers"

es_client.indices.create(
    index=INDEX_NAME,
    mappings={
        "properties": {
            "title": {"type": "text", "copy_to": "semantic_content"},
            "abstract": {"type": "text", "copy_to": "semantic_content"},
            "semantic_content": {
                "type": "semantic_text",
                "inference_id": ".jina-embeddings-v5-text-small",
            },
        }
    },
)
```

[Bulk-index](https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-bulk.html) all 5,000 papers:

```
from elasticsearch import helpers

def build_bulk_actions(dataset, index_name):
    for i, item in enumerate(dataset):
        yield {
            "_index": index_name,
            "_id": i,
            "_source": {
                "title": item["title"],
                "abstract": item["abstract"],
            },
        }

success, failed = helpers.bulk(
    es_client,
    build_bulk_actions(dataset, INDEX_NAME),
    refresh=True,
)
print(f"Indexed {success} papers into '{INDEX_NAME}'")
```

### **Create the chat completion inference endpoint**

We register an OpenAI `gpt-4o-mini` endpoint via the Elasticsearch Inference API. Routing the LLM call through Elasticsearch (instead of calling OpenAI directly) keeps API key handling, retries, and observability inside your cluster:

```
from elasticsearch import NotFoundError

HYDE_INFERENCE_ID = "hyde-completion"

try:
    es_client.inference.delete(inference_id=HYDE_INFERENCE_ID)
except NotFoundError:
    pass

es_client.inference.put(
    task_type="completion",
    inference_id=HYDE_INFERENCE_ID,
    inference_config={
        "service": "openai",
        "service_settings": {
            "api_key": OPENAI_API_KEY,
            "model_id": "gpt-4o-mini",
        },
    },
)
print(f"Created inference endpoint: {HYDE_INFERENCE_ID}")
```

### **Baseline semantic search in Elasticsearch**

Before introducing HyDE, we need a reference point. Here’s a simple [semantic search](https://www.elastic.co/docs/solutions/search/semantic-search) function using the [semantic query](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-semantic-query.html):

```
def search(query_text, size=5):
    response = es_client.search(
        index=INDEX_NAME,
        query={
            "semantic": {
                "field": "semantic_content",
                "query": query_text,
            }
        },
        size=size,
        _source=["title", "abstract"],
    )
    return response["hits"]["hits"]

def print_hits(hits):
    for i, hit in enumerate(hits, 1):
        print(f"{i}. [{hit['_score']:.3f}] {hit['_source']['title']}")
```

```
query = "why does adamw train transformers better than plain adam"
baseline_hits = search(query)
print(f"Query: {query}\n")
print("Top 5 (raw query):")
print_hits(baseline_hits)
```

Results:

```
Top 5 (raw query):
1. [0.792] Understanding AdamW through Proximal Methods and Scale-Freeness
2. [0.760] Maximizing Communication Efficiency for Large-scale Training via 0/1 Adam
3. [0.741] VectorAdam for Rotation Equivariant Geometry Optimization
4. [0.731] Fast Adversarial Training with Adaptive Step Size
5. [0.727] Adaptive Divergence for Rapid Adversarial Optimization
```

The top result is relevant, but results 3–5 drift toward "adversarial training" and "rotation equivariant geometry," both off-topic. The baseline query is too short to anchor the embedding in the right neighborhood.

## Generate a hypothetical document with the Inference API

Now we ask the LLM to write a hypothetical abstract that would be a perfect match for our query. The prompt asks for formal academic register, 150–200 words, matching the density of real arXiv abstracts:

```
def generate_hypothetical_abstract(query):
    prompt = (
        "You are helping improve search over a corpus of machine learning "
        "paper abstracts from arXiv.\n\n"
        "Given a short user query, write ONE plausible research paper abstract "
        "(150-200 words) that would be a perfect match for that query. Use the "
        "formal register and density of a real arXiv abstract: methods, setup, "
        "findings. Do not add a title, headings, or any explanation. Return "
        "only the abstract text itself.\n\n"
        f"User query: {query}\n\nHypothetical abstract:"
    )

    response = es_client.inference.completion(
        inference_id=HYDE_INFERENCE_ID,
        input=prompt,
    )
    return response["completion"][0]["result"].strip()
```

```
hypothetical = generate_hypothetical_abstract(query)
print(hypothetical)
```

```
In this paper, we investigate the training dynamics of Transformer
models utilizing the Adam and AdamW optimization algorithms. While
Adam has been widely adopted for training deep learning models due
to its adaptive learning rates and momentum, we demonstrate that
the integration of weight decay in the AdamW variant substantially
improves the generalization capabilities of Transformers. Our
experimental setup encompasses a series of benchmark tasks, including
language modeling and text classification, where we train various
Transformer architectures (BERT, GPT-2, and T5) with both optimizers.
Through a comprehensive series of ablation studies, we reveal that
AdamW effectively decouples weight decay from the gradient updates,
leading to more stable learning dynamics and reduced overfitting.
Furthermore, we analyze the impact of hyperparameter tuning on
convergence rates and model performance, showing that AdamW
consistently outperforms Adam, particularly in scenarios with limited
training data.
```

This hypothetical abstract is dense with transformer-specific optimization vocabulary: weight decay, gradient updates, convergence, generalization, ablation studies. That vocabulary is what will pull the embedding toward the right neighborhood.

## HyDE search

Now we search with the hypothetical document instead of the original query:

```
hyde_hits = search(hypothetical)
print("Top 5 (HyDE):")
print_hits(hyde_hits)
```

```
Top 5 (HyDE):
1. [0.839] Understanding AdamW through Proximal Methods and Scale-Freeness
2. [0.761] Optimizing the optimizer for data driven deep neural networks
3. [0.759] Trainable Weight Averaging for Fast Convergence and Better Generalization
4. [0.757] Subformer: Exploring Weight Sharing for Parameter Efficiency in
           Generative Transformers
5. [0.756] 8-bit Optimizers via Block-wise Quantization
```

The results shifted. "VectorAdam" and "adversarial training" papers are gone, replaced by papers about weight averaging for convergence, parameter efficiency in transformers, and optimizer quantization, all closer to what the original query was really asking about.

## Does HyDE improve semantic search? Evaluation results

HyDE improved precision and recall by 50% on two of the three test queries. The third query already named both optimizers explicitly, so the baseline embedding was already well-anchored.

We define a hand-curated judgment set for three queries, listing the papers considered relevant, and measure standard retrieval metrics:

* **Precision@5:** Fraction of the top 5 that are in the relevance set.
* **Recall@5:** Fraction of the relevance set captured in the top 5
* **MRR:** Reciprocal rank of the first relevant hit (0 if none).

```
RELEVANT_DOCS = {
    "why does adamw train transformers better than plain adam": {
        "Understanding AdamW through Proximal Methods and Scale-Freeness",
        "Maximizing Communication Efficiency for Large-scale Training via 0/1 Adam",
        "Subformer: Exploring Weight Sharing for Parameter Efficiency in Generative Transformers",
        "Train Large, Then Compress: Rethinking Model Size for Efficient Training and Inference of Transformers",
        "Trainable Weight Averaging for Fast Convergence and Better Generalization",
    },
    "is mixture of experts worth it for small language models": {
        "Task-Specific Expert Pruning for Sparse Mixture-of-Experts",
        "Exploring Extreme Parameter Compression for Pre-trained Language Models",
        "Train Large, Then Compress: Rethinking Model Size for Efficient Training and Inference of Transformers",
        "Balancing Expert Utilization in Mixture-of-Experts Layers Embedded in CNNs",
        "Deep Ensembles on a Fixed Memory Budget: One Wide Network or Several Thinner Ones?",
        "Learning Factored Representations in a Deep Mixture of Experts",
    },
    "how do you stop catastrophic forgetting during fine-tuning": {
        "Understanding the Role of Training Regimes in Continual Learning",
        "SupportNet: solving catastrophic forgetting in class incremental learning with support data",
        "Explain to Not Forget: Defending Against Catastrophic Forgetting with XAI",
        "Few-shot Continual Learning: a Brain-inspired Approach",
        "Online Continual Learning under Extreme Memory Constraints",
        "Continual Learning in Deep Neural Network by Using a Kalman Optimiser",
        "On Tiny Episodic Memories in Continual Learning",
    },
}
```

```
import re

def normalize(title):
    return re.sub(r"\s+", " ", title).strip()

def metrics(hits, relevant, k=5): 
    relevant_norm = {normalize(t) for t in relevant}
    titles = [normalize(h["_source"]["title"]) for h in hits[:k]]
    hits_in_top = sum(1 for t in titles if t in relevant_norm)
    precision = hits_in_top / k
    recall = hits_in_top / len(relevant_norm) if relevant_norm else 0.0
    mrr = 0.0
    for rank, t in enumerate(titles, start=1):
        if t in relevant_norm:
            mrr = 1 / rank
            break

    return {"precision@5": precision, "recall@5": recall, "mrr": mrr}
```

Run both methods across all three queries, and collect results:

```
results = [] 
for query, relevant in RELEVANT_DOCS.items(): 
    baseline_hits = search(query)
    hyde_hits = search(generate_hypothetical_abstract(query))
    results.append({ 
        "query": query,
        "relevant": relevant,
        "baseline_hits": baseline_hits,
        "hyde_hits": hyde_hits,
    })
```

### **Results**

![Two bar charts titled “HyDE vs baseline on a hand‑curated judgment set.” The top chart shows precision@5 scores and the bottom chart shows recall@5 scores for three queries about AdamW, mixture of experts, and catastrophic forgetting. Orange bars for HyDE are equal to or higher than blue bars for baseline.](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt95eeccbb45804471/6a55e6e328aa675797e60a5c/3aeb002935bb258617e4f994a1f9dfe9af08b23b-996x690.png)

HyDE improved precision and recall on queries 2 and 3 but tied with the baseline on query 1. Query 1 ("why does adamw train transformers better than plain adam") already names both optimizers explicitly, so the baseline embedding lands close to the right papers without extra help. The hypothetical abstract adds density but also commits to specific framing, which can swap one relevant paper for another without a net gain. Queries 2 and 3 are vaguer and give the baseline less to anchor on. Here the hypothetical document fills the gap with domain vocabulary the short query lacks, pulling the embedding into a more precise region of the vector space.

## When to use HyDE (and when not to)

HyDE is not a universal upgrade. Here’s when it helps and when to be careful:

**Good candidates for HyDE:**

* Short, casual queries against a corpus of formal documents (academic papers, legal filings, technical reports).
* Domain-specific corpora where the register gap between how users ask and how documents are written is large.
* Retrieval pipelines where precision or recall are not good enough, as a low-cost technique to improve results without reindexing or changing your embedding model.

**Practical considerations:**

* Use a small, fast model since the hypothetical only needs to be topically correct, not factually perfect.
* Cache hypothetical documents for repeated or similar query patterns to avoid redundant LLM calls.
* Consider running HyDE selectively: Use it for short queries (under ~10 words), and skip it for longer, more specific queries that already carry enough semantic signal.

## Conclusion

HyDE closes the embedding distribution gap between short queries and formal documents by using an LLM-generated hypothetical document as the search vector. The Elasticsearch Inference API handles both the LLM generation and the embedding step without leaving the cluster, keeping the implementation compact.

On our dataset, HyDE improved precision and recall by 50% on two out of three test queries and tied on the third. That said, it isn’t free: It adds an LLM round trip to every query, and when the model commits to one interpretation of an ambiguous question, it can narrow retrieval instead of broadening it. It’s an interesting alternative, but first evaluate your own data before adopting it as a default.

## Next steps and further reading

* [Try the notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/hyde-hypothetical-document-embeddings-elasticsearch/notebook.ipynb)
* [Elasticsearch Inference API documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html)
* [semantic\_text field type reference](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html)
* [Hybrid search: Overview and hybrid search queries](https://www.elastic.co/search-labs/blog/hybrid-search-elasticsearch)
* [Mapping embeddings to Elasticsearch field types](https://www.elastic.co/search-labs/blog/mapping-embeddings-to-elasticsearch-field-types)

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