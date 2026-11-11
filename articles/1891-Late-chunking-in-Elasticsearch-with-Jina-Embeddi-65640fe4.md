---
title: 'Late chunking in Elasticsearch with Jina Embeddings v2'
company: Elastic
tag: RAG
date: 2024-11-22
url: https://www.elastic.co/search-labs/blog/late-chunking-elasticsearch-jina-embeddings
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Late chunking in Elasticsearch with Jina Embeddings v2

Using the Jina Embeddings v2 model in Elasticsearch, implementing late chunking, and exploring the pros and cons of long context embeddings models.

November 22, 2024

[Gustavo Llermaly](/search-labs/author/gustavo-llermaly)

[AI](/search-labs/blog/category/ai)[Vector Database](/search-labs/blog/category/vector-database)

Jump to

Share

In this article, we will configure and use [`jina-embeddings-v2`](https://huggingface.co/jinaai/jina-embeddings-v2-base-en), the first open-source 8K context-length embeddings model, starting with an OOTB implementation using `semantic_text` and then implementing Late Chunking.

## Long-context models

We generally see embedding models with a context length of 512 tokens, which means that if we try to create a longer embedding, only the first 512 tokens will be added to the vector field. The problem with these short contexts is that the chunks will not be aware of the entire context but only the text within the chunks:

![512_chunks](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt717516864fff2ba2/6a17de03148009e096b48645/ae7a9321297fc5ad7b8ae1ead16e4f9d66788258-1031x642.png)

As you can see in the image, in `Chunk 1` we know we are talking about Sarah Johnson, but in `Chunk 2` we lost the direct reference. So, as the document gets longer, it might miss the dependencies to when Sarah Johnson was first mentioned and don’t connect that “Sarah Johnson”, “She”, and “Her” refer to the same person. This of course can get even more complex if there’s more than one person addressed as she/her, but for now let’s see the first way to address this issue.

Traditional long-context models that aim at generating text only care about dependencies on previous words so that the last tokens in the input matter more than earlier ones because a text generator’s task is to produce the next word after the input. However, Jina Embeddings 2 model is trained through three key stages: initially, it undergoes masked word pre-training using the 170 billion-word English C4 dataset. Next, it employs pairwise contrastive training with text pairs known to be similar or dissimilar, using a new corpus from Jina AI to refine embeddings so similar texts are closer and dissimilar ones are further apart. Finally, it is fine-tuned with text triplets and negative mining, incorporating a dataset with sentences of opposite grammatical polarity to improve handling of cases where embeddings might otherwise be too close for sentences with opposite meanings.

So, let’s see how this works: a longer context length allows us to keep in the same chunk the references to the first time Sarah Johnson was mentioned:

![8k_chunks](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt00ee9acbd854472c/6a17de047f6f1508a3c09a1b/55200ff4634367e808e8385ffe11766c392cf236-1039x642.png)

However, this also has its drawbacks. The fact that the context is larger means you are putting more information within the same dimensional space. This compression may dilute the context, removing potentially important information from the embeddings. Another drawback is that generating longer embeddings takes more computing resources. Finally, in a RAG system the size of the text chunk defines how much information you are sending to the LLM, which will affect precision, cost, and latency. The good news is that you don't have to use the whole 8K tokens, you can find a sweet spot based on your use case.

![chunking_strategies](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt25684cc3940c3c5d/6a17de062f4a5c5f23fa87e8/f9a2d33bbd5b099e66fe9e1f4946ff574ce0a765-761x305.png)

Jina, in an effort to bring together the best of both worlds, proposes an approach called [Late Chunking](https://jina.ai/news/late-chunking-in-long-context-embedding-models/). Late Chunking consists of chunking the text *after* embeddings, instead of chunking the text first, and then creating the embeddings for each isolated chunk. For this, you need a model capable of creating context-aware embeddings, and then you can chunk the generated embeddings while keeping the context, i.e. dependencies and relations between chunks.

We are going to set up the `jina-embeddings-v2` model in Elasticsearch and use it with [semantic\_text](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text), and then create a custom setup for Late Chunking.

## Steps

1. [Creating Endpoint](https://www.elastic.co/search-labs/blog/jina-embeddings-chunking-elasticsearch#creating-endpoint)
2. [Creating index](https://www.elastic.co/search-labs/blog/jina-embeddings-chunking-elasticsearch#creating-index)
3. [Indexing data](https://www.elastic.co/search-labs/blog/jina-embeddings-chunking-elasticsearch#indexing-data)
4. [Asking questions](https://www.elastic.co/search-labs/blog/jina-embeddings-chunking-elasticsearch#asking-questions)
5. [Late Chunking implementation](https://www.elastic.co/search-labs/blog/jina-embeddings-chunking-elasticsearch#late-chunking-implementation)

### Creating endpoint

With our HuggingFace [Open Inference Service integration](https://www.elastic.co/guide/en/elasticsearch/reference/8.15/infer-service-hugging-face.html), running HuggingFace models is very simple. You just have to open the model [web page](https://huggingface.co/jinaai/jina-embeddings-v2-base-en), click **View Code** under **Inference API**, and grab the API URL from there. In that same screen you can **Manage your tokens** to create the API Key.

For more details about creating security tokens you can visit [this](https://huggingface.co/docs/hub/en/security-tokens).For the purpose of this article setting it as a `read` token is ok.

Once you have the `url` and `api_key`, go ahead and create the [inference](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html) [endpoint](https://www.elastic.co/guide/en/elasticsearch/reference/current/inference-apis.html):

```
PUT _inference/text_embedding/jina-embeddings-v2-base-en
{
  "service": "hugging_face",
  "service_settings": {
    "api_key": "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 
    "url": "https://api-inference.huggingface.co/models/jinaai/jina-embeddings-v2-base-en" 
  }
}
```

*If* *you get this* *error* *"Model* *jinaai/jina-embeddings-v2-base-en is currently loading", it means that the model is warming up.* *Wait* *a couple* *of* *seconds* *and try* *again.*

### Creating index

We are going to use [semantic\_text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html) field type. It will take care of inferring the embedding mappings and configurations, and doing the passage chunking for you! If you want to read more about it, you can go to this great [article](https://www.elastic.co/search-labs/blog/semantic-search-simplified-semantic-text).

```
PUT jina-embeddings
{
  "mappings": {
    "properties": {
      "super_body": {
        "type": "semantic_text",
        "inference_id": "jina-embeddings-v2-base-en"
      }
    }
  }
}
```

This approach will give us a great starting point by handling vector configuration and documents chunking for us. It will create 250-word chunks with a 100-word overlap. For customizations like increasing the chunk size to leverage the 8K context size, we have to go through a [longer process](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-search-inference.html) we will explore in the Late Chunking section.

### Indexing data

When using `semantic_text` we are covered. We just index data as usual.

```
PUT jina-embeddings/_bulk
{ "index" : { "_index" : "jina-embeddings", "_id" : "1" } }
{"super_body": "Sarah Johnson is a talented marine biologist working at the Oceanographic Institute. Her groundbreaking research on coral reef ecosystems has garnered international attention and numerous accolades."}
{ "index" : { "_index" : "jina-embeddings", "_id" : "2" } }
{"super_body": "She spends months at a time diving in remote locations, meticulously documenting the intricate relationships between various marine species. "}
{ "index" : { "_index" : "jina-embeddings", "_id" : "3" } }
{"super_body": "Her dedication to preserving these delicate underwater environments has inspired a new generation of conservationists."}
```

### Asking questions

Now we can use the semantic search query to asks questions to our data:

```
GET jina-embeddings/_search 
{
  "query": {
    "semantic": {
      "field": "super_body",
      "query": "who inspired taking care of the sea?"
    }
  }
}
```

The first result will look like this:

```
{
    "_index": "jina-embeddings",
    "_id": "1",
    "_score": 0.64889884,
    "_source": {
        "super_body": {
            "text": "Sarah Johnson is a talented marine biologist working at the Oceanographic Institute. Her groundbreaking research on coral reef ecosystems has garnered international attention and numerous accolades.",
            "inference": {
                "inference_id": "jina-embeddings-v2-base-en",
                "model_settings": {
                    "task_type": "text_embedding",
                    "dimensions": 768,
                    "similarity": "cosine",
                    "element_type": "float"
                },
                "chunks": [
                    {
                        "text": "Sarah Johnson is a talented marine biologist working at the Oceanographic Institute. Her groundbreaking research on coral reef ecosystems has garnered international attention and numerous accolades.",
                        "embeddings": [
                            -0.0064849486,
                            -0.014192865,
                            0.028806737,
                            0.0026694024,
                            ... // 768 dims
                        ]
                    }
                ]
            }
        }
    }
}
```

## Late Chunking implementation

Now that we have configured the embeddings model, we can create our own Late Chunking implementation in Elasticsearch. The process will require the following steps:

1. Create mappings

```
PUT jina-late-chunking
{
  "mappings": {
    "properties": {
      "content_embedding": { 
        "type": "dense_vector", 
        "dims": 768, 
        "element_type": "float",
        "similarity": "cosine"
      },
      "content": { 
        "type": "text" 
      }
    }
  }
}
```

2. Load data

*You* *can find the full implementation in the* *supporting* [*Notebook*](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/how-to-use-jina-v2-embeddings/how-to-use-jina-v2-embeddings.ipynb).

We are not using the ingest pipeline approach here because we want to create special embeddings, instead we are going to use a python script which key role is getting annotations for the positions of the chunk tokens, generating embeddings for the whole document, and then chunking the embeddings based on the length we provide:

With this code you can define the text chunks size by splitting by sentence and getting chunk positions.

```
def chunk_by_sentences(input_text: str, tokenizer: callable):
    """
    Split the input text into sentences using the tokenizer
    :param input_text: The text snippet to split into sentences
    :param tokenizer: The tokenizer to use
    :return: A tuple containing the list of text chunks and their corresponding token spans
    """
    inputs = tokenizer(input_text, return_tensors='pt', return_offsets_mapping=True)
    punctuation_mark_id = tokenizer.convert_tokens_to_ids('.')
    sep_id = tokenizer.convert_tokens_to_ids('[SEP]')
    token_offsets = inputs['offset_mapping'][0]
    token_ids = inputs['input_ids'][0]
    chunk_positions = [
        (i, int(start + 1))
        for i, (token_id, (start, end)) in enumerate(zip(token_ids, token_offsets))
        if token_id == punctuation_mark_id
        and (
            token_offsets[i + 1][0] - token_offsets[i][1] > 0
            or token_ids[i + 1] == sep_id
        )
    ]
    chunks = [
        input_text[x[1] : y[1]]
        for x, y in zip([(1, 0)] + chunk_positions[:-1], chunk_positions)
    ]
    span_annotations = [
        (x[0], y[0]) for (x, y) in zip([(1, 0)] + chunk_positions[:-1], chunk_positions)
    ]
    return chunks, span_annotations
```

This second function will receive the annotations and the embeddings of the whole input to generate embedding chunks.

```
def late_chunking(
    model_output: 'BatchEncoding', span_annotation: list, max_length=None
):
    token_embeddings = model_output[0]
    outputs = []
    for embeddings, annotations in zip(token_embeddings, span_annotation):
        if (
            max_length is not None
        ):  # remove annotations which go bejond the max-length of the model
            annotations = [
                (start, min(end, max_length - 1))
                for (start, end) in annotations
                if start < (max_length - 1)
            ]
        pooled_embeddings = [
            embeddings[start:end].sum(dim=0) / (end - start)
            for start, end in annotations
            if (end - start) >= 1
        ]
        pooled_embeddings = [
            embedding.detach().cpu().numpy() for embedding in pooled_embeddings
        ]
        outputs.append(pooled_embeddings)

    return outputs
```

This is the part that puts it all together; tokenize the entire text input, and then pass it to the `late_chunking` function to chunk the pooled embeddings.

```
inputs = tokenizer(input_text, return_tensors='pt')
model_output = model(**inputs)
embeddings = late_chunking(model_output, [span_annotations])[0]
```

After this process, we can index our documents:

```
# Prepare the documents to be indexed
documents = []
for chunk, new_embedding in zip(chunks, embeddings):
    documents.append(
        {
            "_index": "jina-late-chunking",
            "_source": {
                "content_embedding": new_embedding,
                "content": chunk,
            },
        }
    )
# Use helpers.bulk to index
helpers.bulk(client, documents)
```

You can find the notebook with the full example step by step [here](https://github.com/elastic/elasticsearch-labs/tree/main/supporting-blog-content/how-to-use-jina-v2-embeddings/how-to-use-jina-v2-embeddings.ipynb).

Feel free to experiment with different values in the `input_text` variable.

3. Running queries

You can now run semantic search against the new data index:

```
GET jina-late-chunking/_search
{
  "knn": {
    "field": "content_embedding",
    "query_vector_builder": {
      "text_embedding": {
        "model_id": "jina-embeddings-v2-base-en",
        "model_text": "berlin"
      }
    },
    "k": 10,
    "num_candidates": 100
  }
}
```

The result will look like this:

```
{
  "_index": "jina-late-chunking",
  "_id": "gGDN1JEBF7lnCNFTVZBg",
  "_score": 0.4930191,
  "_source": {
    "content_embedding": [
      -0.9107036590576172,
      -0.57366544008255,
      1.0492067337036133,
      0.25255489349365234,
      -0.1283145546913147... 
    ],
    "content": "Berlin is the capital and largest city of Germany, both by area and by population."
  }
}
```

## Conclusion

Although still experimental, late-chunking has potentially many benefits, especially in RAG , since it allows you to keep key context information when you chunk your texts. Additionally, Jina embedding model helps to store shorter vectors, thus taking less space in memory and storage, and speeding up search retrieval. So, both of these features together with Elasticsearch enhance both efficiency and effectiveness in managing and retrieving information when using vector search.

### Frequently Asked Questions

#### What is Late Chunking?

Late Chunking is a method that consists of chunking the text after embeddings (instead of chunking the text first) and then creating the embeddings for each isolated chunk.

#### What is Jina-embeddings-v2?

Jina-embeddings-v2 is the first open-source 8K context-length embeddings model.

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