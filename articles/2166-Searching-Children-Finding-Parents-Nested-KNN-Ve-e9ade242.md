---
title: 'Searching Children, Finding Parents: Nested KNN Vector Search in Solr'
company: Sease
tag: 召回
date: 2026-01-15
url: https://sease.io/2026/01/nested-knn-vector-search-in-solr.html
account: 
origin: harvest3-202607
---
Hi there! We are excited to introduce a new feature coming to Solr 10.1: **KNN search on nested vectors via Block Join** contributed by Sease, [Alessandro Benedetti](https://sease.io/about/alessandro-benedetti-2) ([merged PR](https://github.com/apache/solr/pull/3316/)). In this post, we will cover:

* Challenge: Current KNN Search in Solr
* KNN Block Join Query
* Nested KNN Search Example

## Challenge: Current KNN Search in Solr

Before we dive into the new functionality, let’s unpack a **key limitation in the existing Solr vector search implementation**. When dealing with large documents, we often hit token limits capped by embedding models. Also, a long text vector representation loses precision on the semantic meaning.

A common strategy is to generate multiple vectors for a single document. In Solr, this is handled via **Block Join and nested documents**.   
Previously, Solr lacked an efficient mechanism to perform a KNN search on child documents (chunks) while returning the ranked parent documents (original text). Specifically, the main problem was that there was no guarantee that K parents would be returned after selecting N children: first, the whole children set was retrieved and then collapsed to the parents.  
This means that selecting children didn’t imply any check on the uniqueness of their parents.

## KNN Block Join Query

The **KNN Block Join query** is a powerful addition because it bridges the gap between granular data and top-level results. It enables searching across specific child paragraphs and surfacing the most relevant parent documents in a single request.

In Solr 10.1, this is implemented as additional parameters within the **`KnnQParser`**. The execution relies on two primary parameters (**`parents.preFilter`** and **`childrenOf`**) to navigate the parent-child relationship:

|  |  |  |  |
| --- | --- | --- | --- |
| **Parameter Name** | **Required** | **Default** | **Description** |
| parents.preFilter | Optional (If used, `childrenOf` param is needed) | None | filter query on parent document metadata |
| childrenOf | Mandatory if `parents.preFilter` is used | None | query that matches the set of ALL possible parent documents |

As the KNN Block Join query bridges two different document levels (parent-child), Solr executes it in three steps:

##### Step One: Diversified KNN query

The **`{!knn}`** vector search is executed on child documents. If any prefiltering on children or parents metadata (via **`parents.preFilter`**) is applied, Solr narrows the search space while calculating vector similarities. The **`childrenOf`** parameter ensures that Solr only calculates distances for documents defined as “children” in the nested structure.  
At this step, only children belonging to unique parents are returned (only the best child per parent is returned).

##### Step Two: Block Join

Once Solr has a list of matching child documents from Step One, it executes the Block Join parent query. It maps the matching children documents back to their corresponding parent documents. And it aggregates the similarity scores from the matching children and assigns that value to the parent. This ensures the parent documents are ranked based on the relevance of their most specific, matching child documents.

##### Step Three: Child Transformer

After parent documents are identified and ranked, Solr retrieves the top-level fields from **`fl`** for the parents. For each parent, the **`[child]`** transformer executes a separate internal search. It uses `childFilter` to fetch the child documents that matched the original KNN search and adds them into the parent result.

## Nested KNN Search Example

We will walk through a step-by-step use case of nested KNN search in Solr.

To test this feature, we are using the **Solr 10.x (main branch)**. For this demonstration, we initialise a collection named **`testcore`** with a single Solr node (Standalone mode).

##### Defining the Schema

The core of this implementation is the vector field definition. We are using the [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) embedding model, which produces vectors with 384 dimensions.

In the **`schema.xml`**, the field is defined using **cosine similarity** to calculate the distance between vectors:

```
				
					&lt;fieldType name="knn_vector" class="solr.DenseVectorField"
           vectorDimension="384"
           similarityFunction="cosine"
           knnAlgorithm="hnsw"/&gt;

&lt;field name="vector" type="knn_vector" indexed="true" stored="true"/&gt;
				
			
```

##### Indexing the Data

To demonstrate the nested KNN search, I used a subset of the [RealTimeData/bbc\_news\_alltime](https://huggingface.co/datasets/RealTimeData/bbc_news_alltime) dataset. For the sake of simplicity, I applied a naive chunking strategy with a 100-word limit per chunk to ensure high semantic precision. And each text chunk was converted into a vector using the [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)  embedding model from Sentence Transformers. Note that to use **Block Join**, we must index the chunks as **nested child documents** under their respective parent documents. We can index nested child documents using [JSON-structured children](https://solr.apache.org/guide/solr/latest/indexing-guide/indexing-nested-documents.html) or [anonymous children](https://solr.apache.org/guide/solr/latest/indexing-guide/indexing-nested-documents.html#indexing-anonymous-children) with **`_childDocuments_`** . We will demonstrate both ways, though the first one is recommended.

First of all, we need to add a field **`_root_`** to the schema to index nested documents:

```
				
					&lt;field name="_root_" type="string" indexed="true" stored="false" docValues="false" /&gt;
				
			
```

For the **JSON-structured children**, we need parent-child relationship tracking, we can add the **`_nest_path_`** field type and name:

```
				
					&lt;fieldType name="_nest_path_" class="solr.NestPathField" /&gt; 
&lt;field name="_nest_path_" type="_nest_path_" /&gt;
				
			
```

Optionally, we can also add **`_nest_parent_`** field to store parent IDs under child documents:

```
				
					&lt;field name="_nest_parent_" type="string" indexed="true" stored="true" /&gt;
				
			
```

Now, we can index the documents using **JSON-structured children** stored in the `chunks`:

```
				
					[
  {
    "id": "doc_0",
    "title_t": "Watch: The Londoner who races against buses  - BBC News",
    "content_t": "When people want to improve their fitness, many will go to the gym or join a sports club. That was not the route for Jordan Izzett - after lockdown, he decided to race against London's buses to improve his health...",
    "vector": [0.05614076554775238, -0.018275713548064232, 0.009141994640231133, -0.04260682314634323, -0.0302545428276062, 0.10058693587779999, ...],
    "type_s": "parent",
    "chunks": [
      {
        "id": "doc_0_chunk_0",
        "content_chunk_t": "When people want to improve their fitness, many will go to the gym or join a sports club. That was not the route for Jordan Izzett - after lockdown, he decided to race against London's buses to improve his health...",
        "vector": [0.04435167461633682, 0.03151167929172516, 0.013601190410554409, -0.04917684569954872, -0.031929079443216324, 0.09469131380319595, ...],
        "type_s": "child",
        "_nest_parent_": "doc_0"
      },
      {
        "id": "doc_0_chunk_1",
        "content_chunk_t": "like doing a normal run, but with a competitive element,\" he says. He does not recommend it for any fresh starters, however. Listen to the best of BBC Radio London on Sounds and follow BBC London on Facebook, external, X, external and Instagram, external.",
        "vector": [0.04457193985581398, -0.1145293340086937, 0.02342628687620163, -0.02455621398985386, -0.044924043118953705, 0.04106786102056503, ...],
        "type_s": "child",
        "_nest_parent_": "doc_0"
      }
    ]
  }
]
				
			
```

Notice that **`_nest_parent_`** is added under the chunks field, representing the parent ID.

Alternatively, we can also index documents using the `_childDocuments_` as **anonymous children**, which results in a flattened list of documents (all documents are siblings instead of a parent-child relationship):

```
				
					[
  {
    "id": "doc_0",
    "title_t": "Watch: The Londoner who races against buses  - BBC News",
    "content_t": "When people want to improve their fitness, many will go to the gym or join a sports club. That was not the route for Jordan Izzett - after lockdown, he decided to race against London's buses to improve his health... ",
    "vector": [0.05614076554775238, -0.018275713548064232, 0.009141994640231133, -0.04260682314634323, -0.0302545428276062, 0.10058693587779999, ...],
    "type_s": "parent",
"_childDocuments_":[
{
    "id": "doc_0_chunk_0",
    "content_chunk_t": "When people want to improve their fitness, many will go to the gym or join a sports club. That was not the route for Jordan Izzett - after lockdown, he decided to race against London's buses to improve his health...",
    "vector": [0.04435167461633682, 0.03151167929172516, 0.013601190410554409, -0.04917684569954872, -0.031929079443216324, 0.09469131380319595, ...],
    "type_s": "child"
  },
  {
    "id": "doc_0_chunk_1",
    "content_chunk_t": "like doing a normal run, but with a competitive element,\" he says. He does not recommend it for any fresh starters, however. Listen to the best of BBC Radio London on Sounds and follow BBC London on Facebook, external, X, external and Instagram, external.",
    "vector": [0.04457193985581398, -0.1145293340086937, 0.02342628687620163, -0.02455621398985386, -0.044924043118953705, 0.04106786102056503, ...],
    "type_s": "child"
  }
]
  }
]
				
			
```

##### Nested KNN Vector Search

Once the documents are indexed in Solr, we can execute a complex query – a nested vector search using a **KNN Block Join**. We run a KNN vector search on child documents with pre-filtering on parent metadata and retrieve the top-K (**`topK=3`**) parent documents.

First, we take the user’s query (for example, keyword *‘attack’*) and generate a vector using the [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model:

```
				
					[-0.0008323239744640887, 0.10418761521577835, -0.015891294926404953, 0.086622454226017, -0.013051033951342106, 0.05209134891629219,...]
				
			
```

Next, we have **KNN Block Join** POST request. While the syntax might look a bit intimidating at first glance, it is quite logical once we decompose it:

```
				
					curl -X POST "http://localhost:8983/solr/testcore/select" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'q={!parent which=$allParents score=max v=$children.q}' \
  -d 'children.q={!knn f=vector topK=3 parents.preFilter=$filterParents childrenOf=$allParents}[-0.0008323239744640887, 0.10418761521577835, -0.015891294926404953, 0.086622454226017, -0.013051033951342106, 0.05209134891629219]' \
  -d 'allParents=type_s:parent' \
  -d 'filterParents=title_t:"New Orleans"' \
  -d 'fl=id,score,chunks,title_t,content_chunk_t,[child fl=id,content_chunk_t childFilter=$children.q]'
				
			
```

Let’s break down the POST request query components and see how they work under the hood:

```
				
					q={!parent which=$allParents score=max v=$children.q}
				
			
```

The **‘q’** parameter uses the Block Join Parent Query Parser (**`'!parent`‘** ) to retrieve parent documents. It identifies parents via the criteria in the `which` parameter and returns those whose child documents match the query specified in the**`'v=children.q`‘.** Additionally,**‘`score=max`‘** sets the scoring mode: the parent document is assigned the score of its highest-scoring child:

```
				
					children.q={!knn f=vector topK=3 parents.preFilter=$filterParents childrenOf=$allParents}[-0.0008323239744640887, 0.10418761521577835, -0.015891294926404953, 0.086622454226017, -0.013051033951342106, 0.05209134891629219]
				
			
```

The**`'children.q`‘** defines the KNN vector search logic to be executed against the child documents (**chunks** in our example). The `{!knn f=vector topK=3 ...}` finds the top 3 most child chunks based on the input embedding. The **‘`parents.preFilter`=$filterParents’** filters out parents to shrink the vector search space to the children of the relevant parents. The final piece, **‘`childrenOf`=$allParents’** defines the scope of which documents are considered children:

Note that the vector in the POST request is composed by six floats for simplicity; in practice, this array must match the exact dimension size defined in the schema for the vector field.

```
				
					"allParents": "type_s:parent"
				
			
```

In the **‘allParents’** metadata, we specify parents via **`type_s`** to distinguish between parents and children.  
This is a query that returns all the parents.

```
				
					filterParents=title_t:"New Orleans"
				
			
```

In the **‘filterParents’** metadata, we filter for parent documents containing the phrase *“New Orleans”* in their **`title_t`** field.

```
				
					"fl": "id,score,chunks,title_t,content_chunk_t,[child fl=id,content_chunk_t childFilter=$children.q]"
				
			
```

For the field list (`fl`), we define the fields to be returned in the result set: **`id`**, **`score`**, **`chunks`**, **`title_t`**, and **`content_chunk_t`**.

Notice that the field **`content_chunk_t`** is listed in **two** places: once in the top-level **`fl`** param and again inside the**‘`child`‘** transformer:

Even though content\_chunk\_t only exists in the child documents, it must be explicitly declared in the top-level field list for the child transformer to successfully retrieve and map it. Omitting it from the top level will result in missing data in the response.

After submitting the request to Solr, we get the following response:

```
				
					"response": {
        "numFound": 3,
        "start": 0,
        "maxScore": 0.64710826,
        "numFoundExact": true,
        "docs": [
            {
                "id": "doc_65",
                "title_t": "New Orleans attacker acted alone, FBI now believes - BBC News",
                "score": 0.64710826,
                "chunks": [
                    {
                        "id": "doc_65_chunk_14",
                        "content_chunk_t": "reaction to the attack was one of \"anger and frustration\". The White House said Mr Biden had called the city's mayor this morning to offer \"full federal support\"..."
                    }
                ]
            },
            {
                "id": "doc_98",
                "title_t": "New Orleans new year celebrations turn to terror and tragedy  - BBC News",
                "score": 0.6350503,
                "chunks": [
                    {
                        "id": "doc_98_chunk_4",
                        "content_chunk_t": "calling for urgent help captured in chaotic radio chatter. \"I have at least six casualties. I have an office doing chest compressions on one..."
                    }
                ]
            },
            {
                "id": "doc_87",
                "title_t": "Moment New Orleans attacker approaches busy street - BBC News",
                "score": 0.62282187,
                "chunks": {
                    "id": "doc_87_chunk_0",
                    "content_chunk_t": "CCTV footage shows the moment before the New Orleans attack suspect drove down Bourbon Street ramming into crowds..."
                }
            }
        ]
  }
				
			
```

The result includes three (topK=3) parent documents, each containing the top-ranked child document as determined by the cosine similarity function against the vector for the query *‘attack’*.

That wraps up this example on nested KNN search. Thanks for reading! I hope you found this useful. Stay tuned for more blog posts, and feel free to reach out with any questions.

## Need Help with this topic?​

If you're struggling with nested KNN vector search in Apache Solr, don't worry - we're here to help!
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)

## Need Help With This Topic?​​

If you’re struggling with nested KNN vector search in Apache Solr, don’t worry – we’re here to help!  
Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)