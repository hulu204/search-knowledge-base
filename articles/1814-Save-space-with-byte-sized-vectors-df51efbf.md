---
title: 'Save space with byte-sized vectors'
company: Elastic
tag: 索引构建
date: 2023-01-23
url: https://www.elastic.co/search-labs/blog/save-space-with-byte-sized-vectors
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Save space with byte-sized vectors

Elasticsearch is introducing a new type of vector that has 8-bit integer dimensions. This is 4x smaller than the current vector with 32-bit float dimensions, which can result in substantial space savings.

January 23, 2023

[Jack Conradson](/search-labs/author/jack-conradson)[Benjamin Trent](/search-labs/author/benjamin-trent)

[AI](/search-labs/blog/category/ai)

Jump to

Share

Elasticsearch is introducing a new type of vector in 8.6! This vector has 8-bit integer dimensions, where each dimension has a range of [-128, 127]. This is 4x smaller than the current vector with 32-bit float dimensions, which can result in substantial space savings.

You can start indexing these smaller, 8-bit vectors right now by adding the [*element\_type parameter*](https://www.elastic.co/guide/en/elasticsearch/reference/current/dense-vector.html#dense-vector-params) with the *byte* value to your vector mappings, similar to the example below.

```
{
    "mappings": {
        "properties": {
            "my_vector": {
                "type": "dense_vector",
                "element_type": "byte",
                "dims": 3,
                "index": true,
                "similarity": "dot_product"
            }
        }
    }
}
```

But what if your existing vectors' dimensions don't fit into this smaller type? Then we can use the process of quantization to make them fit, often with only a small loss of precision!

## Let's quantize

Let's start by defining quantization. Quantization is the process of taking a larger set of values and mapping them to a smaller set of values. More specifically, in our case this would be taking the range of a 32-bit float and mapping it to the range of an 8-bit integer for each dimension in a vector. (This should not be confused with dimensional reduction, which is a different topic. This is only reducing the range of the values for the existing dimensions.)

This leads to two further questions. What is the actual range of our 32-bit float vectors? And what function should we use to do the mapping? The answers vary significantly based on use-case.

As an example, one of the simplest forms of quantization is taking the dimensions of normalized 32-bit vectors and linearly mapping them to the full range of the dimensions of 8-bit vectors. Using Python, this would look something like the following:

```
import numpy as np
import typing as t

def quantize_embeddings(text_and_embeddings: t.List[t.Mapping[str, t.Any]]) -> t.List[t.Mapping[str, t.Any]]:
    quantized_embeddings = np.array([x['embedding'] for x in 
query_and_embeddings])
    quantized_embeddings = (quantized_embeddings * 128)
    quantized_embeddings = quantized_embeddings.clip(-128, 
127).astype(int).tolist()
    return [dict(item, **{'embedding': embedding}) for (item, 
embedding) in zip(text_and_embeddings, quantized_embeddings)]
```

This is only a single example, though. There are many other useful quantization functions. For your specific use case, it's important to evaluate what method of quantization will give you the best results relative to the trade-off between space reduction, relevance, and recall.

## Some real-world numbers

8-bit vectors and quantization are great and all, but do they really reduce space in a real-world use case? The answer is unequivocally YES! And substantially. This is all while they continue to give good results without hurting relevance and recall. Elasticsearch even has all the tools you need to do that evaluation yourself with our [rank evaluation API](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-rank-eval.html).

Now, let's look at some numbers generated from a real-world example with the following setup:

1. All data was gathered using Elasticsearch in Cloud with two gcp.data.highcpu.1 64GB nodes
2. Data was collected from the [NQ dataset (Natural Question)](https://ai.google.com/research/NaturalQuestions/download), built by Google, used in BEIR
3. The embeddings model was [sentence-transformers%2Fall-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
4. Quantization to generate 8-bit integer vectors was applied to the 32-bit float vectors collected from the data using the previous example Python snippet

Then we make some magic happen and collect results based on this setup:

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| category | Median kNN Response Time | Median Exact Response Time | Recall@100 | NDCG@10 | Total Index Size (1p, 1r) |
| byte | 32ms | 1072ms | 0.79 | 0.38 | 5.8gb |
| float | 36ms | 1530ms | 0.79 | 0.38 | 16.4gb |
| % Reduction | 11% | 30% | 0% | 0% | 64% |

And our results look fantastic. Let's break down each one.

* **Median kNN Response Time:** This response time is collected using [approximate kNN search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#approximate-knn) against our example data set. This type of search uses Lucene's HNSW graph as the backing data structure. We see an 11% increase in response time for byte versus float.
* **Median Exact Response Time:** This response time is collected using [exact kNN search](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html#exact-knn) against our example data set. This type of search uses a script to iterate through every vector in the data set and will return the best possible results. We see a large improvement of 30% reduction in response time!
* **Recall@100:** This shows us if the most relevant results are included in the top 100. This is important to show if our quantization function worked well. We can see that the numbers are identical for byte versus float, which means that our relevance even after quantizing is just as good for byte as it is for float.
* **@NDCG@10:** This shows us how good the quality of our first 10 results is. This is another important metric to evaluate if our quantization function worked well. Once again, the numbers are identical between byte versus float, so we can rest assured that our results are still just as good even after quantization.
* **Total Index Size (1p, 1r):** This is the total index size used for our vectors' index with a single partition and a single replica. For this metric, we disabled source, which we recommend for all vector fields in which the ingested vector data is unmodified so it's not stored twice. **And we see a massive 64% reduction in total index size!** This doesn't quite reach the 4x difference between a byte and float because of additional overhead for the HNSW data structure including graph connections, but it's still a quite substantial size reduction.

Byte vectors are all ready to go as part of 8.6, and we encourage you to fire up a cluster in [Elastic Cloud](https://www.elastic.co/cloud/) and give them a try!

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