---
title: 'Vespa Neural Search Tutorial'
company: Sease
tag: 召回
date: 2023-02-06
url: https://sease.io/2023/02/vespa-neural-search-tutorial.html
account: 
origin: harvest3-202607
---
Hi readers!  
In this blog post, we are going to explore how to do a **Neural Search in Vespa** through an end-to-end tutorial.

Through practical examples we will see how to:

* **Prepare suitable documents**
* **Export a suitable neural model** and use it in Vespa
* **Configure Vespa for Neural Search**
* **Run Nearest Neighbor queries**, combining them with filters and textual search

## 1. Download Vespa

To keep everything simple, we use a **minimal local Vespa**.  
To install it, we follow the **Vespa [quick-start](https://docs.vespa.ai/en/vespa-quick-start.html) guide**. As mentioned in the official documentation, before going on, **be sure to comply with all the prerequisites**.

To install Vespa:  
`brew install vespa-cli`

For our tutorial, we create a project with the following structure:

![](https://i0.wp.com/sease.io/wp-content/uploads/2023/01/imgonline-com-ua-ReplaceColor-jdLlQ9PbMl.jpg?fit=507%2C344&ssl=1)

* + the *documents* folder will contain the python script to convert MSMarco data into a document format suitable for Vespa and the two folders with the input (*msmarco\_documents*) and output (*vespa\_documents*) files.

* + the *model* folder will contain the python script to export a sentence transformer from HuggingFace and convert it into an ONNX format suitable for Vespa, and *files* that contain the necessary model files (model and vocabulary).

* + the *schemas* folder will contain the document schema file.

* + the *service.xml* will define the Vespa configuration and components.

* + the *vespa-feed-client* tool for feeding documents into Vespa.

All the material can be found in [our GitHub repository](https://github.com/SeaseLtd/vespa-neural-search-tutorial):

## 2. Prepare Documents

Now that we have Vespa installed, let’s start creating our documents.

For this tutorial, we take one corpus of [**MS MARCO**](https://microsoft.github.io/msmarco/), a collection of large-scale information retrieval datasets for deep learning. In particular, we download the **passage retrieval collection**: [collection.tar.gz](https://msmarco.blob.core.windows.net/msmarcoranking/collection.tar.gz) and extract the **first 10k documents** of it. We then put this file in the *msmarco\_documents* folder as *documents\_10k.tsv*.

To push MS Marco data in Vespa, we need to manipulate it and create documents with the format supported by Vespa. To do this, we use the ***convert\_msmarco\_data\_to\_vespa\_format.py*** Python script in the *documents* folder.

To keep a clear environment we install all the dependencies in [Anaconda](https://www.anaconda.com/products/distribution).  
Let’s start by creating a *conda* environment to manage the necessary libraries:

```
				
					conda create -n vespa_tutorial_env python=3.10 &amp;&amp; conda activate vespa_tutorial_env
				
			
```

Now we are ready to generate the documents. Here is the script to use:

```
				
					import random

if __name__ == "__main__":
    fields_list = ["id", "text", "color"]
    categorical_list = ["yellow", "red", "blue", "green", "white", "black", "pink", "orange"]

    input_file = open("./msmarco_documents/documents_10k.tsv", "r")
    output_file = open("./vespa_documents/collection_for_feeding.json", "w")
    document = ""
    count = 1
    for line in input_file.readlines():
        text = line.split("\t")[1]
        categorical_value = random.randint(0, 7)
        document = document + "{\"put\": \"id:doc:doc::" + str(count) + "\","
        document = document + "\"fields\": {\"text\": \"" + text.replace("\\d", "d").replace("\\", "")[:-1] + "\","
        document = document + "\"color\": \"" + categorical_list[categorical_value] + "\"}"
        document = document + "}\n"
        count = count + 1
    output_file.write(document)
    output_file.close()
    input_file.close()
				
			
```

Where:

1. *./msmarco\_documents/documents\_10k.tsv* is the path of the **input file**, from which to take the documents.
2. *./vespa\_documents/collection\_for\_feeding.json* is the path of the **output file**, where to write the generated Vespa documents.

Then let’s execute the script with the following command:

```
				
					cd documents
python convert_msmarco_data_to_vespa_format.py
				
			
```

Each document we created contains:

1. An incremental **id** (starting from 1)
2. A **text** field containing the text of the MS Marco document
3. A random **color** field was added just to show how filter queries work with neural search

The final generated file (*collection\_for\_feeding.json*) in the *vespa\_documents* output folder looks like this:

```
				
					{
	"put": "id:doc:doc::1",
	"fields": {
		"text": "The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was...",
		"color": "yellow"
	}
} {
	"put": "id:doc:doc::2",
	"fields": {
		"text": "The Manhattan Project and its atomic bomb helped bring an end to World War II. Its legacy of peaceful uses of atomic energy continues to have an impact on history and science.",
		"color": "pink"
	}
} {
	"put": "id:doc:doc::3",
	"fields": {
		"text": "Essay on The Manhattan Project - The Manhattan Project The Manhattan Project was ...",
		"color": "red"
	}
}
				
			
```

This is the required [document JSON format](https://docs.vespa.ai/en/reference/document-json-format.html#document-operations) when feeding documents with the [vespa-feed-client](https://docs.vespa.ai/en/vespa-feed-client.html) tool we will use later.

## 3. Export the Neural Model

Now that we have the documents, we can focus on preparing the neural model.  
First of all, we need to download the desired model.

For this tutorial, we use the **[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) sentence transformer** **from HuggingFace**. It is a **BERT** model of roughly 90MB with an *hidden\_size* (the *embedding\_dimension*) of 384.

We can directly download the vocabulary (the *[vocab.txt](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/main/vocab.txt)* file) while for the model we need to convert it since **Vespa supports only the [ONNX model format](https://docs.vespa.ai/en/onnx.html)**.

In order to do this, we use a python script that requires [PyTorch](https://pytorch.org/) and the [transformers](https://huggingface.co/docs/transformers/installation) library of HuggingFace.  
To install it:  
`pip install torch`  
`pip install transformers`

Now we are ready to convert the model.  
The file we execute is the ***[export\_model.py](https://github.com/SeaseLtd/vespa-neural-search-tutorial/blob/main/model/export_model.py)***. This is taken from the Vespa [simple-semantic-search](https://github.com/vespa-engine/sample-apps/blob/a7f555fdb943a4a42a723f56664dec2fe1252f1e/simple-semantic-search/) GitHub example, specifically the [export\_model\_from\_hf.py](https://github.com/vespa-engine/sample-apps/blob/a7f555fdb943a4a42a723f56664dec2fe1252f1e/simple-semantic-search/export_model_from_hf.py) file:

```
				
					# Copyright Yahoo. Licensed under the terms of the Apache 2.0 license. See LICENSE in the project root.
from transformers import BertModel
import torch

encoder = BertModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Vespa bert embedder expects these inputs and outputs
# Vespa implements the pooling, default average
input_names = ["input_ids", "attention_mask", "token_type_ids"]
output_names = ["output_0"]

input_ids = torch.ones(1,32, dtype=torch.int64)
attention_mask = torch.ones(1,32,dtype=torch.int64)
token_type_ids = torch.zeros(1,32,dtype=torch.int64)
args = (input_ids, attention_mask, token_type_ids)
torch.onnx.export(encoder,
  args=args,
  f="./files/minilm-l6-v2.onnx",
  do_constant_folding=True,
  input_names = input_names,
  output_names = output_names,
  dynamic_axes = {
    "input_ids": {0: "batch", 1:"batch"},
    "attention_mask": {0: "batch", 1: "batch"},
    "token_type_ids": {0: "batch", 1: "batch"},
    "output_0": {0: "batch"},
  },
  opset_version=14)
				
			
```

This script downloads the *sentence-transformers/all-MiniLM-L6-v2* model from HuggingFace and exports it to a file (*./files/minilm-l6-v2.onnx*) with the right ONNX format.

Let’s execute this with:

```
				
					cd model
python export_model.py
				
			
```

We can now deactivate our *conda* environment since we do not need it anymore:

```
				
					conda deactivate
				
			
```

## 4. Configure Vespa

### Services

Now let’s define the [services](https://docs.vespa.ai/en/tutorials/news-2-basic-feeding-and-query.html#services-specification) in our Vespa application.  
Here we’ll not go too much into detail since we pretty much keep the default configuration.

Here is the *services.xml* file we created:

```
				
					&lt;?xml version="1.0" encoding="utf-8" ?&gt;
&lt;services version="1.0" xmlns:deploy="vespa" xmlns:preprocess="properties"&gt;

    &lt;!-- See https://docs.vespa.ai/en/reference/services-container.html --&gt;
    &lt;container id="default" version="1.0"&gt;

        &lt;!-- See https://docs.vespa.ai/en/embedding.html#bertbase-embedder --&gt;
        &lt;component id="bert" class="ai.vespa.embedding.BertBaseEmbedder" bundle="model-integration"&gt;
            &lt;config name="embedding.bert-base-embedder"&gt;
                &lt;transformerModel path="model/files/minilm-l6-v2.onnx"/&gt;
                &lt;tokenizerVocab path="model/files/vocab.txt"/&gt;
            &lt;/config&gt;
        &lt;/component&gt;

        &lt;document-api/&gt;
        &lt;search/&gt;

        &lt;nodes&gt;
            &lt;node hostalias="node1" /&gt;
        &lt;/nodes&gt;
    &lt;/container&gt;

    &lt;!-- See https://docs.vespa.ai/en/reference/services-content.html --&gt;
    &lt;content id="text" version="1.0"&gt;
        &lt;redundancy&gt;2&lt;/redundancy&gt;
        &lt;documents&gt;
            &lt;document type="doc" mode="index" /&gt;
        &lt;/documents&gt;
        &lt;nodes&gt;
            &lt;node hostalias="node1" distribution-key="0" /&gt;
        &lt;/nodes&gt;
    &lt;/content&gt;

&lt;/services&gt;
				
			
```

Let’s focus on the **[embedding](https://docs.vespa.ai/en/embedding.html) component**:

```
				
					&lt;component id="bert" class="ai.vespa.embedding.BertBaseEmbedder" bundle="model-integration"&gt;
    &lt;config name="embedding.bert-base-embedder"&gt;
        &lt;transformerModel path="model/files/minilm-l6-v2.onnx"/&gt;
        &lt;tokenizerVocab path="model/files/vocab.txt"/&gt;
    &lt;/config&gt;
&lt;/component&gt;
				
			
```

This is the model we use to create vectors from the text, specifically we exploit the [BertBaseEmbedder](https://docs.vespa.ai/en/embedding.html#bertbase-embedder) component of Vespa. The only things to pay attention to are the *transformerModel* and *tokenizerVocab* paths which should point to the model and the vocabulary files we want to use.

### Schema

Finally, we can define the Vespa [schema](https://docs.vespa.ai/en/schemas.html) (*doc.sd* file in the *schemas*folder) for our Neural Search. This is the file containing our documents’ field definitions and the ranking profiles we will use at query time.

Let’s see what it looks like and explore each part in detail.  
The ***doc.sd*** file: [here](https://github.com/SeaseLtd/vespa-neural-search-tutorial/blob/main/schemas/doc.sd)

##### Fields Definitions

Let’s start with the fields definitions:

```
				
					document doc {
    # Field that contains MSMarco document's text
    field text type string {
        indexing: summary | index
        index: enable-bm25
    }

    # Field that contains our random color
    field color type string {
        indexing: summary | index
        rank: filter
    }

}

# Field that contains the vector(extracted from text)
field embedding type tensor&lt;float&gt;(x[384]) {
    indexing: input text | embed bert | attribute | index
    attribute {
        distance-metric: euclidean
    }
    index: hnsw
}
				
			
```

Here we define three fields:

1. **Text**: it contains the MS Marco text of each document.
2. **Color**: it contains the random color we assign to each document in the document preparation step.
3. **Embedding**: it will contain the numeric vector representing the corresponding text in the text field. Here we define a tensor<float> with a dimension of 384 which corresponds to the output of our neural model. This field has three parameters set: indexing, attribute, and [index](https://docs.vespa.ai/en/reference/schema-reference.html#index).

Let’s look in more detail at the embedding parameters.

###### Indexing

As said in Vespa [documentation](https://docs.vespa.ai/en/schemas.html#indexing): *“Indexing instructions have pipeline semantics similar to Unix shell commands, with data flowing from left to right. They can perform complex transformations on field values, or just send the field value unchanged to the next sections of the index structure.”*.

In our case the [pipeline](https://docs.vespa.ai/en/embedding.html#embedding-a-document-field) is:

```
				
					input text | embed bert | attribute | index

				
			
```

Here the content of the *text* field is taken as input for the embedding generation. The vector is created through the *bert* embedder (id of the embedder defined in the *services.xml* file) and then added as an in-memory attribute. Finally, it is indexed.

###### Attribute

As said in Vespa [documentation](https://docs.vespa.ai/en/reference/schema-reference.html#attribute): *“attribute contained in [field](https://docs.vespa.ai/en/reference/schema-reference.html#field) or [struct-field](https://docs.vespa.ai/en/reference/schema-reference.html#struct-field). Specifies a property of an index structure attribute.”*.  
It’s necessary when we define the [distance-metric](https://docs.vespa.ai/en/reference/schema-reference.html#distance-metric) to use with the [nearestNeighbor](https://docs.vespa.ai/en/reference/query-language-reference.html#nearestneighbor) query operator, in our case the euclidean distance.

###### Index

As said in Vespa [documentation](https://docs.vespa.ai/en/reference/schema-reference.html#attribute): *“attribute contained in [field](https://docs.vespa.ai/en/reference/schema-reference.html#field) or [struct-field](https://docs.vespa.ai/en/reference/schema-reference.html#struct-field). Specifies a property of an index structure attribute.”*.  
It’s necessary when we define the [distance-metric](https://docs.vespa.ai/en/reference/schema-reference.html#distance-metric) to use with the [nearestNeighbor](https://docs.vespa.ai/en/reference/query-language-reference.html#nearestneighbor) query operator, in our case the euclidean distance.

##### Rank Profiles

In Vespa, [rank profiles](https://docs.vespa.ai/en/ranking.html#rank-profiles) are used to define ranking expression functions and settings which can be selected at query time. Different profiles can have different relevance expressions, different metrics, and ranking behaviors; allowing different query features in the input.

Our first [rank profile](https://docs.vespa.ai/en/ranking.html#rank-profiles) is the *pure\_neural\_rank* profile.

###### Pure Neural Rank Profile

```
				
					# Rank profile that implements a pure Neural Search
rank-profile pure_neural_rank {
    num-threads-per-search: 1

    inputs {
        query(first_query) tensor&lt;float&gt;(x[384])
        query(second_query) tensor&lt;float&gt;(x[384])
    }
    first-phase {
        expression: closeness(field, embedding)
    }
    match-features {
        closeness(field, embedding)
        closeness(label, first_query) 
        closeness(label, second_query)
        distance(field,embedding)
    }

}
				
			
```

**The aim of this profile is to execute a pure Nearest Neighbor search. Taking in input one or two embeddings at query time and returning the nearest documents.**

Here we defined three [elements](https://docs.vespa.ai/en/reference/schema-reference.html#rank-profile):

* [Inputs](https://docs.vespa.ai/en/reference/schema-reference.html#inputs): query features consumed by the ranking expression in this profile.
* [First-phase](https://docs.vespa.ai/en/reference/schema-reference.html#firstphase-rank): the ranking configuration to be used for [first-phase](https://docs.vespa.ai/en/phased-ranking.html) of ranking.
* [Match-features](https://docs.vespa.ai/en/reference/schema-reference.html#match-features): the [rank features](https://docs.vespa.ai/en/reference/rank-features.html) to be returned with each hit, computed in the *match* phase.

**INPUTS**

For Neural Search we defined the possibility to pass two tensors in the query: `query(first_query)` and `query(second_query)`. Both will be tensors generated by our *bert* embedder at query time. These vectors are passed in the `inputs.query()` query parameter like:

```
				
					input.query(first_query)=embed(#of calories to eat to lose weight)
				
			
```

Where `embed()` is the function calling our *bert* embedder to create vectors from text.

**FIRST-PHASE**

Here we define the expression for the relevance computation.  
Vespa supports multiple rank phases. For this tutorial, we just set the first-phase ranking, but if you are interested, more details can be found [here](https://docs.vespa.ai/en/phased-ranking.html).

We choose [closeness](https://docs.vespa.ai/en/reference/rank-features.html#attribute-match-features-normalized) as the metric, which is used with the [nearestNeighbor](https://docs.vespa.ai/en/reference/query-language-reference.html#nearestneighbor) query operator. This metric internally uses the *distance* defined in the *embedding* field of the schema.

When a generic `closeness(field, embedding)` expression is used with two query tensors passed, the document relevance will be the max closeness between the ones computed for each vector. Therefore:

```
				
					max{closeness(label, first_query), closeness(label, second_query)}
				
			
```

**MATCH-FEATURES**

In *match-features* we can define the useful metrics we want to monitor in the results. This indeed is the list of rank features to be included with each result hit.

For the purposes of this tutorial, we will show:

* `closeness(field, embedding)` the final document closeness (the max closeness explained before).
* `closeness(label, first_query)` the closeness between the document and the first query vector.
* `closeness(label, second_query)` the closeness between the document and the second query vector.

To show the closeness of the two different vectors, we use **query annotations** and specifically **labels**.  
These are defined at query time in the *nearestNeighbor* method and uniquely identify the vectors. For example, for the first tensor we can define:

```
				
					{label:'first_query', targetHits:100}nearestNeighbor(embedding, first_query)
				
			
```

We will see real usages in the query examples; further ones in the documentation can be found [here](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#multiple-nearest-neighbor-search-operators-in-the-same-query).

###### Hybrid Rank

Let’s see the second profile:

```
				
					# Rank profile that implements a combination of Neural and Textual Search
rank-profile hybrid_rank inherits pure_neural_rank {
    inputs {
        query(textWeight) : 1.0
        query(vectorWeight) : 1.0
    }
    first-phase {
        expression {
            query(textWeight) * bm25(text) +
            query(vectorWeight) * closeness(field, embedding)
        }
    }
    match-features {
        closeness(field, embedding)
        bm25(text)
    }
}
				
			
```

Here we would like to **compute a more complex relevance that takes into account both the lexical ranking (with *bm25*) and the neural one (with *closeness*)**. This profile inherits the *pure\_neural\_rank* profile, therefore we first read the tensors and compute the closeness in *pure\_neural\_rank*, then we find the final relevance with the new formula.

**INPUTS**

As *inputs*for this profile, we define two **weights**: one for *text* relevance and one for *vector* relevance. They are used in the first-phase ranking expression. If no values are passed, the default 1 weight is assigned.

**FIRST-PHASE**

As the relevance formula, we defined the sum of the *bm25* score computed on the text field with the closeness computed in the *pure\_neural\_rank* profile, multiplied by their corresponding weights.

**MATCH-FEATURES**

Finally, we print the *closeness* and *bm25* values computed for each document hit.

###### Neural Rank Sum Closeness

Let’s see the last profile.

```
				
					# Rank profile that implements a different relevance metric for the pure Neural Search
rank-profile neural_rank_sum_closeness {
    num-threads-per-search: 1

    inputs {
        query(first_query) tensor&lt;float&gt;(x[384])
        query(second_query) tensor&lt;float&gt;(x[384])
    }
    first-phase {
        expression: closeness(label, first_query) + closeness(label, second_query)

    }
    match-features {
        distance(field, embedding)
        closeness(field, embedding)
        closeness(label, first_query) 
        closeness(label, second_query)
    }

}
				
			
```

In this profile, we would like to use **as relevance the sum of the closenesses computed for each tensor** passed at query time.

## 5. Indexing Documents

The last thing we need before making queries is to push documents into Vespa.  
In order to feed multiple documents at once, we need to **download and install [vespa-feed-client](https://docs.vespa.ai/en/vespa-feed-client.html)**.

We can do this with:

```
				
					F_REPO="https://repo1.maven.org/maven2/com/yahoo/vespa/vespa-feed-client-cli" &amp;&amp; F_VER=$(curl -Ss "${F_REPO}/maven-metadata.xml" | sed -n 's/.*&lt;release&gt;\(.*\)&lt;.*&gt;/\1/p') &amp;&amp; curl -SsLo vespa-feed-client-cli.zip ${F_REPO}/${F_VER}/vespa-feed-client-cli-${F_VER}-zip.zip &amp;&amp; unzip -o vespa-feed-client-cli.zip
				
			
```

Then, we use [docker](https://www.docker.com/) to run Vespa. Be sure to have it installed before **starting Vespa** with:

```
				
					vespa config set target local
docker run --detach --name vespa --hostname vespa-container --publish 8080:8080 --publish 19071:19071 vespaengine/vespa
vespa status deploy --wait 300
vespa deploy --wait 300
				
			
```

and **index documents**:

```
				
					./vespa-feed-client-cli/vespa-feed-client --file ./documents/vespa_documents/collection_for_feeding.json --endpoint http://localhost:8080
				
			
```

## 6. Queries

Let’s now go in-depth into Neural Search queries.

### Exact Nearest Neighbor Search

To exploit neural search, Vespa provides the `nearestNeighbor`() method. It allows us to perform both, exact and approximate nearest-neighbor searches.

This is an example of a query doing an **exact nearest neighbor search** (`approximate:false`):

```
				
					vespa query "yql=select * from doc where {approximate:false,targetHits: 100}nearestNeighbor(embedding, first_query)" "input.query(first_query)=embed(#of calories to eat to lose weight)" "ranking=pure_neural_rank"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 597
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4753",
                "relevance": 0.18904411884161854,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.18904411884161854,
                        ...
                        "distance(field,embedding)": 4.289770483882663
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4753",
                    "text": "For a healthy daily calorie count, allow 10 calories per pound of body weight ...",
                    "color": "green"
                }
            },
            {
                "id": "id:doc:doc::4528",
                "relevance": 0.1750265633743142,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1750265633743142,
                        ...
                        "distance(field,embedding)": 4.713418470437464
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4528",
                    "text": "... calories in each gram -- 1 g of fat provides 9 calories. If you consume 2,500 calories per day, ...",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::9349",
                "relevance": 0.17466600309410665,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.17466600309410665,
                        ...
                        "distance(field,embedding)": 4.725212590232682
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::9349",
                    "text": "The Zone diet typically caps daily calories for women at 1,200 and 1,500 for men...",
                    "color": "pink"
                }
            },

...
				
			
```

The most important parameters of this query are:

* + The [`targetHits`](https://docs.vespa.ai/en/nearest-neighbor-search.html#querying-using-nearestneighbor-query-operator) (**required**) query annotation.   
    It specifies the number of results that one wants to expose to first-phase ranking per node involved in the query. This is a lower bound per node, and with exact search, more hits than *targetHits* are exposed to first-phase ranking.

* + The [`approximate`](https://docs.vespa.ai/en/reference/query-language-reference.html#approximate) query annotation.  
    It specifies if we want to do an exact or approximate nearest neighbor search. The exact search is set through the `approximate:false` setting, otherwise, the default `approximate:true` is used and an approximate search is done.

* + `first_query` variable.  
    It should match the query input defined in the rank profile. It is used inside the `nearestNeighbor` and the `input.query()` methods to specify the input we are passing.

* + `input.query()` method.  
    It defines one of the inputs for the rank profile we are using. In this case, it passes the embedding to our neural query. `embed()` is the method calling the embedder defined in *service.xml* (if multiple embedders are used, an *id* needs to be given as explained [here](https://docs.vespa.ai/en/embedding.html#embedding-a-query-text)) and computing the vector for the textual query *“#of calories to eat to lose weight”*.

* + `ranking=pure_neural_rank` parameter.  
    It defines which rank profile to use for the query. In this case, we are going to use the *pure\_neural\_rank*.

### Approximate Nearest Neighbor Search

To use the approximate nearest neighbour [[1]](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#approximate-nearest-neighbor-search), omit the `approximate` parameter, which is *true* by default:

```
				
					vespa query "yql=select * from doc where {targetHits: 100}nearestNeighbor(embedding, first_query)" "input.query(first_query)=embed(#of calories to eat to lose weight)" "ranking=pure_neural_rank"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 100
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4753",
                "relevance": 0.1890441216634541,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1890441216634541,
                        ...
                        "distance(field,embedding)": 4.289770404922987
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4753",
                    "text": "For a healthy daily calorie count, allow 10 calories per pound of body weight ...",
                    "color": "green"
                }
            },
            {
                "id": "id:doc:doc::4528",
                "relevance": 0.1750265612999238,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1750265612999238,
                        ...
                        "distance(field,embedding)": 4.713418538152102
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4528",
                    "text": "... If you consume 2,500 calories per day, your fat intake should range from 56 g to 97 g. Recommendations for fat are further specified by type of fat.",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::9349",
                "relevance": 0.1746659943912434,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1746659943912434,
                        ...
                        "distance(field,embedding)": 4.7252128754956635
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::9349",
                    "text": "The Zone diet typically caps daily calories for women at 1,200 and 1,500 for men...",
                    "color": "pink"
                }
            },
...
				
			
```

### Approximate Nearest Neighbor with Query Filter

It is possible to integrate the nearest neighbor search with [filters](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#combining-approximate-nearest-neighbor-search-with-query-filters).  
Let’s do this filtering on the color field with:

```
				
					vespa query "yql=select * from doc where {targetHits: 100}nearestNeighbor(embedding, first_query) AND color contains 'yellow'" "input.query(first_query)=embed(#of calories to eat to lose weight)" "ranking=pure_neural_rank"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 100
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4528",
                "relevance": 0.1750265612999238,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1750265612999238,
                        ...
                        "distance(field,embedding)": 4.713418538152102
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4528",
                    "text": "... If you consume 2,500 calories per day, your fat intake should range from 56 g to 97 g...",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::4947",
                "relevance": 0.16819859694194497,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.16819859694194497,
                        ...
                        "distance(field,embedding)": 4.945352804251736
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4947",
                    "text": "How Many Calories are in the Alcohol ...",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::9348",
                "relevance": 0.1666637050622998,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1666637050622998,
                        ...
                        "distance(field,embedding)": 5.000106619651799
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::9348",
                    "text": "You can use Weight Loss Resources to follow the Zone diet by setting your target nutrition profile ...",
                    "color": "yellow"
                }
            },
...
				
			
```

Here Vespa returns only documents with the color *yellow* since it uses **pre-filtering**. For further details on how filtering works in Vespa take a look at these references [[2]](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#controlling-filter-behavior) [[3]](https://blog.vespa.ai/constrained-approximate-nearest-neighbor-search/)

As mentioned in Vespa [documentation](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#strict-filters-and-distant-neighbors): *“With strict filters, the neighbors that are returned might be of low quality (far distance). One way to combat this is to use the [distanceThreshold](https://docs.vespa.ai/en/reference/query-language-reference.html#distancethreshold) query annotation parameter of the nearestNeighbor query operator.”*.  
Since the value of the distance depends on the [distance-metric](https://docs.vespa.ai/en/reference/schema-reference.html#distance-metric) used. By adding the [distance(field,embedding)](https://docs.vespa.ai/en/reference/rank-features.html#distance(dimension,name)) rank-feature to the match-features of the rank profile, it is possible to analyze what distance could be considered too far.

This can be defined in the query as:

```
				
					vespa query "yql=select * from doc where {distanceThreshold: 5.0, targetHits: 100}nearestNeighbor(embedding, first_query) AND color contains 'yellow'" "input.query(first_query)=embed(#of calories to eat to lose weight)" "ranking=pure_neural_rank"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 2
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4528",
                "relevance": 0.1750265612999238,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1750265612999238,
                        ...
                        "distance(field,embedding)": 4.713418538152102
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4528",
                    "text": "Fat is the most energy-dense macronutrient, which means it contains the most calories ...",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::4947",
                "relevance": 0.16819859694194497,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.16819859694194497,
                        ...
                        "distance(field,embedding)": 4.945352804251736
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4947",
                    "text": "How Many Calories are in the Alcohol You Like to Drink? import 2014-05-19T05:40:13+00:00...",
                    "color": "yellow"
                }
            }
        ]
    }
}
				
			
```

As you can see, now only two documents are returned, those with a distance of less than 5.

### Hybrid Sparse and Dense Retrieval Methods

The just-seen dense retrieval can be [combined](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#hybrid-sparse-and-dense-retrieval-methods-with-vespa) with traditional sparse retrieval. As described in rank profiles, we have implemented this behavior in the definition of the *hybrid\_rank* rank profile.

In order to use it, just change the ranking with the *hybrid\_rank* one:

```
				
					vespa query "yql=select * from doc where {targetHits: 100}nearestNeighbor(embedding, first_query) OR text contains 'exercise'" "type=weakAnd" "ranking=hybrid_rank" "input.query(first_query)=embed(#of calories to eat to lose weight)"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 135
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4761",
                "relevance": 9.125252513334813,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "bm25(text)": 8.97712592472415,
                        "closeness(field,embedding)": 0.1481265886106627
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4761",
                    "text": "A report by the Mayo Clinic indicates that proper nutrition can boost any exercise ...",
                    "color": "white"
                }
            },
            {
                "id": "id:doc:doc::8732",
                "relevance": 9.081256342626082,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "bm25(text)": 8.95203518376092,
                        "closeness(field,embedding)": 0.12922115886516217
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::8732",
                    "text": "The form of exercise increases...",
                    "color": "black"
                }
            },
            {
                "id": "id:doc:doc::4756",
                "relevance": 8.669726817466929,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "bm25(text)": 8.498001371344154,
                        "closeness(field,embedding)": 0.17172544612277515
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4756",
                    "text": "As a rule of thumb, weight loss is generally 75 percent diet and 25 percent exercise...",
                    "color": "green"
                }
            },
...
				
			
```

This query combines the *nearestNeighbor* operator with the *[weakAnd](https://docs.vespa.ai/en/reference/query-language-reference.html#weakand)* operator using logical disjunction (OR)(you can find more information about how weakAnd works [here](https://docs.vespa.ai/en/using-wand-with-vespa.html#weakand)). This type of query enables retrieving both based on semantic (vector distance) and traditional sparse (exact) matching.

To be able to compute *bm25* metric for the text field, we add the *“OR text contains ‘exercise'”* condition to the query.

For how we defined the rank profile, it is also possible to pass *text* and *vector* weights to the relevance expression. In this first query example, no weights are given in input to the query and therefore the default value of 1 is assigned to both. The relevance is indeed the sum of *bm25* and *closeness*.  
The [weights](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#hybrid-sparse-and-dense-retrieval-methods-with-vespa) for the relevance formula can be set with the `ranking.features.query()` method as:

```
				
					vespa query "yql=select * from doc where {targetHits: 100}nearestNeighbor(embedding, first_query) OR text contains 'exercise'" "type=weakAnd" "ranking=hybrid_rank" "input.query(first_query)=embed(#of calories to eat to lose weight)" "ranking.features.query(textWeight)=0.5" "ranking.features.query(vectorWeight)=30"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 135
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4756",
                "relevance": 9.400764069355333,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "bm25(text)": 8.498001371344154,
                        "closeness(field,embedding)": 0.17172544612277515
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4756",
                    "text": "As a rule of thumb, weight loss is generally 75 percent diet and 25 percent exercise...",
                    "color": "green"
                }
            },
            {
                "id": "id:doc:doc::4761",
                "relevance": 8.932360620681955,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "bm25(text)": 8.97712592472415,
                        "closeness(field,embedding)": 0.1481265886106627
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4761",
                    "text": "A report by the Mayo Clinic indicates that proper nutrition can boost any exercise routine ...",
                    "color": "white"
                }
            },
            {
                "id": "id:doc:doc::4277",
                "relevance": 8.836020903237696,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "bm25(text)": 8.165063896210217,
                        "closeness(field,embedding)": 0.1584496318377529
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4277",
                    "text": "11 8. âExercise is an effective method of weight management.âs cardio, resistance training or flexibility work, rely on the nutrition you provide them through your diet...",
                    "color": "black"
                }
            },
...
				
			
```

Thanks to weights, we were able to give more importance to the closeness in the final relevance. We can see the new behavior on document *4756* which moved up in the rankings.

### Multiple Nearest Neighbor Search Operators in the Same Query

It is also possible to query with [multiple embeddings](https://docs.vespa.ai/en/nearest-neighbor-search-guide.html#multiple-nearest-neighbor-search-operators-in-the-same-query). To do this, just combine multiple *nearestNeighbor* operators in the query:

```
				
					vespa query "yql=select * from doc where ({label:'first_query', targetHits:100}nearestNeighbor(embedding, first_query)) OR ({label:'second_query', targetHits:100}nearestNeighbor(embedding, second_query))" "ranking=pure_neural_rank" "input.query(first_query)=embed(#of calories to eat to lose weight)" "input.query(second_query)=embed(diet zone strategy)"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 161
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::4753",
                "relevance": 0.1890441216634541,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1890441216634541,
                        "closeness(label,first_query)": 0.1890441216634541,
                        "closeness(label,second_query)": 0.11298739153572483,
                        "distance(field,embedding)": 4.289770404922987
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4753",
                    "text": "For a healthy daily calorie count, allow 10 calories per pound of body weight -- so a 150-pound woman ...",
                    "color": "green"
                }
            },
            {
                "id": "id:doc:doc::4528",
                "relevance": 0.1750265612999238,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1750265612999238,
                        "closeness(label,first_query)": 0.1750265612999238,
                        "closeness(label,second_query)": 0.11656046297833024,
                        "distance(field,embedding)": 4.713418538152102
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4528",
                    "text": "Fat is the most energy-dense macronutrient, which means it contains the most calories in each gram ...",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::9349",
                "relevance": 0.1746659943912434,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1746659943912434,
                        "closeness(label,first_query)": 0.1746659943912434,
                        "closeness(label,second_query)": 0.13456681371668433,
                        "distance(field,embedding)": 4.7252128754956635
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::9349",
                    "text": "The Zone diet typically caps daily calories for women at 1,200 and 1,500 for men...",
                    "color": "pink"
                }
            },
...
				
			
```

Here we used the *pure\_neural\_rank* rank profile, where the relevance is the max *closeness*.  
In order to change the relevance computation, and use the **sum of the closenesses** of the two vectors, just change the ranking to *neural\_rank\_sum\_closeness* rank profile:

```
				
					vespa query "yql=select * from doc where ({label:'first_query', targetHits:100}nearestNeighbor(embedding, first_query)) OR ({label:'second_query', targetHits:100}nearestNeighbor(embedding, second_query))" "ranking=neural_rank_sum_closeness" "input.query(first_query)=embed(#of calories to eat to lose weight)" "input.query(second_query)=embed(diet zone strategy)"
				
			
```

**RESPONSE**

```
				
					{
    "root": {
        "id": "toplevel",
        "relevance": 1.0,
        "fields": {
            "totalCount": 161
        },
        "coverage": {
            "coverage": 100,
            "documents": 10000,
            "full": true,
            "nodes": 1,
            "results": 1,
            "resultsFull": 1
        },
        "children": [
            {
                "id": "id:doc:doc::9349",
                "relevance": 0.30923280810792775,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1746659943912434,
                        "closeness(label,first_query)": 0.1746659943912434,
                        "closeness(label,second_query)": 0.13456681371668433
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::9349",
                    "text": "The Zone diet typically caps daily calories for women at 1,200 and 1,500 for men...",
                    "color": "pink"
                }
            },
            {
                "id": "id:doc:doc::9348",
                "relevance": 0.30526075530543645,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1666637050622998,
                        "closeness(label,first_query)": 0.1666637050622998,
                        "closeness(label,second_query)": 0.13859705024313665
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::9348",
                    "text": "You can use Weight Loss Resources to follow the Zone diet by setting your target nutrition...",
                    "color": "yellow"
                }
            },
            {
                "id": "id:doc:doc::4753",
                "relevance": 0.3020315131991789,
                "source": "text",
                "fields": {
                    "matchfeatures": {
                        "closeness(field,embedding)": 0.1890441216634541,
                        "closeness(label,first_query)": 0.1890441216634541,
                        "closeness(label,second_query)": 0.11298739153572483
                    },
                    "sddocname": "doc",
                    "documentid": "id:doc:doc::4753",
                    "text": "For a healthy daily calorie count, allow 10 calories per pound ...",
                    "color": "green"
                }
            },
...
				
			
```

As explained before, in these two final examples we exploit labels to show the *closeness* values for each query tensor separately.

## Summary

Vespa provides a comprehensive and highly customizable way to implement neural search.  
There are a lot of pros to the provided product:

* the possibility to integrate a custom model in Vespa
* the possibility to create embeddings internally just by calling the embedder in the *services.xml*
* the way filtering is managed, with pre-filtering as the default
* the possibility to customize the relevance expression by combining different metrics
* the possibility to easily debug relevance by printing all the necessary metrics separately

Due to the high customization, we do not find the system implementation straightforward. It was necessary to do a great study of all the components and configurations before being able to deploy also a minimal system. Documentation is detailed but sometimes a bit difficult to follow since the same feature/concept can be described on several different pages.

Anyway, we found Vespa to be a good system for implementing neural search and a note of merit must be given to the [Slack channel](http://slack.vespa.ai/) on which the Vespa team is very active and helpful.

Thank you for reading and see you in the next blog post!

## Need Help With This Topic?​​

If you’re struggling with Neural Search in Vespa, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Vespa search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Neural Search in Vespa, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Vespa search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)