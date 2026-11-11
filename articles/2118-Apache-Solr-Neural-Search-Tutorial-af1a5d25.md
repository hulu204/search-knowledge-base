---
title: 'Apache Solr Neural Search Tutorial'
company: Sease
tag: 召回
date: 2023-01-31
url: https://sease.io/2023/01/apache-solr-neural-search-tutorial.html
account: 
origin: harvest3-202607
---
Hi readers!  
In this blog post, we will explore our Neural Search contribution to Apache Solr, providing a detailed description of what is already available through an end-to-end tutorial.

To better understand how the vector-based approach is improving search and to learn more about the Apache Lucene/Solr implementation, we suggest starting by reading our two previous blog posts:

* + [Apache Solr Neural Search](https://sease.io/2022/01/apache-solr-neural-search.html)

* + [Apache Solr Neural Search Knn benchmark](https://sease.io/2022/01/apache-solr-neural-search-knn-benchmark.html)

The purpose of this post is not to go into implementation details but to show in practice how you can use this new Apache Solr feature to index and search vectors and then run a full end-to-end neural search.  
Through practical examples we will see how:

1. **Apache Solr implementation works**, with the new field type and query parser introduced
2. **To generate vectors from text** and integrate large language models with Apache Solr
3. **To run KNN queries** (with and without filters) and how to use them for reranking

## Apache Solr Neural Search Pipeline

Let’s start with an overview of the end-to-end pipeline to implement Neural Search with Solr:

1. Download Apache Solr
2. Produce Vectors Externally
3. Create an index containing a vector field
4. Index documents
5. Search exploiting vector fields

We now describe each section in detail, so that you can easily reproduce this tutorial.

## 1. Download Solr

Neural Search has been released with Apache Solr 9.0 in May 2022.  
This tutorial uses the latest version (9.1), which you can download from [here](https://solr.apache.org/downloads.html).

Solr can be installed in any supported system (Linux, macOS, and Windows) where a Java Runtime Environment (JRE) version 11 or higher is available [[1](https://solr.apache.org/guide/solr/latest/deployment-guide/system-requirements.html)].

*Take a look at the [instructions](https://www.apache.org/dyn/closer.cgi#verify) for verifying the integrity of the downloaded file, both the sha512 key and the PGP key.*

Extract the downloaded file to a location where you want to work with it, open the terminal from that folder and run Solr locally:

```
				
					bin/solr start
				
			
```

You can now navigate to the Solr admin interface: <http://localhost:8983/solr/>

## 2. Produce Vectors Externally

In order to execute a search that exploits vector embeddings, it is necessary to:

1. Train a model outside Solr.
2. Create vector embeddings from documents’ fields with a custom script.
3. Push the vectors to Solr.

For this tutorial, we use a Python project that you can easily clone from our [GitHub](https://github.com/SeaseLtd/approaching-neural-search) page.

###### Python Requirements

To replicate this exercise, you just need to install the following requirements in your python environment:

```
				
					python==3.8.0
sentence-transformers
pysolr
				
			
```

###### NLP Model and Corpus

For encoding text into the corresponding vectors, we did not train a model but we used a pre-trained(and fine-tuned) model called **[all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)**, which is a natural language processing (NLP) sentence transformation model.  
The model type is **BERT**, the *hidden\_size* (so the *`embedding_dimension`*) is 384, and it is roughly 80MB.

For this tutorial, we took one corpus of [MS MARCO](https://microsoft.github.io/msmarco/), a collection of large-scale information retrieval datasets for deep learning. In particular, we downloaded the passage retrieval collection: [collection.tar.gz](https://msmarco.blob.core.windows.net/msmarcoranking/collection.tar.gz) and indexed roughly 10k documents of it.

###### Create vector embeddings

Here is the python script to run in order to automatically create vector embeddings from a corpus:

```
				
					from sentence_transformers import SentenceTransformer
import torch
import sys
from itertools import islice

BATCH_SIZE = 100
INFO_UPDATE_FACTOR = 1
MODEL_NAME = 'all-MiniLM-L6-v2'

# Load or create a SentenceTransformer model.
model = SentenceTransformer(MODEL_NAME)
# Get device like 'cuda'/'cpu' that should be used for computation.
if torch.cuda.is_available():
    model = model.to(torch.device("cuda"))
print(model.device)

def batch_encode_to_vectors(input_filename, output_filename):
    # Open the file containing text.
    with open(input_filename, 'r') as documents_file:
        # Open the file in which the vectors will be saved.
        with open(output_filename, 'w+') as out:
            processed = 0
            # Processing 100 documents at a time.
            for n_lines in iter(lambda: tuple(islice
            (documents_file, BATCH_SIZE)), ()):
                processed += 1
                if processed % INFO_UPDATE_FACTOR == 0:
                    print("processed {} batch of documents"
                    .format(processed))
                # Create sentence embedding
                vectors = encode(n_lines)
                # Write each vector into the output file.
                for v in vectors:
                    out.write(','.join([str(i) for i in v]))
                    out.write('\n')

def encode(documents):
    embeddings = model.encode(documents, show_progress_bar=True)
    print('vector dimension: ' + str(len(embeddings[0])))
    return embeddings

def main():
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
    batch_encode_to_vectors(input_filename, output_filename)

if __name__ == "__main__":
        main()
				
			
```

**RESPONSE**

```
				
					processed 1 batch of documents
Batches: 100%|██████████| 4/4 [00:04&lt;00:00,  1.08s/it]
vector dimension: 384
...
...
processed 100 batch of documents
Batches: 100%|██████████| 4/4 [00:02&lt;00:00,  1.35it/s]
				
			
```

[SentenceTransformers](https://www.sbert.net/index.html) is a Python framework that you can use to compute sentence/text embeddings; it offers a large collection of [pre-trained models](https://www.sbert.net/docs/pretrained_models.html) tuned for various tasks and in this case, we use **all-MiniLM-L6-v2** which maps sentences to a 384-dimensional dense vector space.

The python script takes as input a file containing 10k documents (i.e. a small part of the MS MARCO passage retrieval collection):

```
				
					sys.argv[1] = "/path/to/documents_10k.tsv"
				
			
```

*e.g. 1 document*

*The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.*

It will output a file containing the corresponding vectors:

```
				
					sys.argv[2] = "/path/to/vectors_documents_10k.tsv"
				
			
```

*e.g. 1 document*

```
				
					0.0367823,0.072423555,0.04770486,0.034890372,0.061810732,0.002282318
,0.05258357,0.013747136,-0.0060595,...,0.0054274425
				
			
```

It is necessary to push the obtained embeddings to Solr (we will see this in the section on Indexing documents).

## Struggling implementing Neural Search in Apache Solr?

No need to worry! We have a recorded training waiting for you. You will be able to understand perfectly how to integrate Neural Search into Apache Solr, at your own pace and rhythm!

[Click here](https://sease.io/information-retrieval-mini-training/end-to-end-apachesolr-neural-search-tutorial)

## 3. Create an index containing a vector field

After installing and starting Solr, the first thing to do is to create a **collection** (i.e. a single index and associated transaction log and configuration files) in order to be able to index and search.

Here is the command to create the ‘***ms-marco***‘ collection:

```
				
					bin/solr create -c ms-marco
				
			
```

To keep this tutorial as simple as possible, let’s review and edit the configuration files, in particular:

solrconfig.xml

It defines indexing options, RequestHandlers, highlighting, spellchecking, and various other configurations.

Here is our minimal configuration file:

```
				
					&lt;?xml version="1.0" ?&gt;
&lt;config&gt;
  &lt;dataDir&gt;${solr.data.dir:}&lt;/dataDir&gt;

  &lt;directoryFactory name="DirectoryFactory"           class="${solr.directoryFactory:solr.NRTCachingDirectoryFactory}"/&gt;
  &lt;schemaFactory class="ClassicIndexSchemaFactory"/&gt;

  &lt;luceneMatchVersion&gt;LATEST&lt;/luceneMatchVersion&gt;

  &lt;updateHandler class="solr.DirectUpdateHandler2"&gt;
    &lt;commitWithin&gt;
      &lt;softCommit&gt;${solr.commitwithin.softcommit:true}&lt;/softCommit&gt;
    &lt;/commitWithin&gt;
  &lt;/updateHandler&gt;

  &lt;requestHandler name="/select" class="solr.SearchHandler"&gt;
    &lt;lst name="defaults"&gt;
      &lt;str name="echoParams"&gt;explicit&lt;/str&gt;
      &lt;str name="indent"&gt;true&lt;/str&gt;
      &lt;str name="df"&gt;text&lt;/str&gt;
    &lt;/lst&gt;
  &lt;/requestHandler&gt;
&lt;/config&gt;
				
			
```

schema.xml

It is the entry point that allows defining your data model, so the fields to be indexed and the type for the field (text, integers, etc.).

Solr starts with the managed schema enabled, but for simplicity and to manually edit the file, we switched to the static schema. For more information read [here](https://solr.apache.org/guide/solr/latest/configuration-guide/schema-factory.html#switching-from-managed-schema-to-schema-xml).

Again, we keep it as minimal as possible, including only the necessary fields:

```
				
					&lt;schema name="ms-marco" version="1.0"&gt;
  &lt;fieldType name="string" class="solr.StrField" omitNorms="true" positionIncrementGap="0"/&gt;
  &lt;!-- vector-based field --&gt;
  &lt;fieldType name="knn_vector" class="solr.DenseVectorField" vectorDimension="384" omitNorms="true"/&gt;
  &lt;fieldType name="long" class="org.apache.solr.schema.LongPointField" docValues="true" omitNorms="true" positionIncrementGap="0"/&gt;
  &lt;!-- basic text field --&gt;
  &lt;fieldType name="text" class="solr.TextField"&gt;
    &lt;analyzer&gt;
      &lt;tokenizer class="solr.StandardTokenizerFactory"/&gt;
      &lt;filter class="solr.LowerCaseFilterFactory"/&gt;
    &lt;/analyzer&gt;
  &lt;/fieldType&gt;

  &lt;field name="id" type="string" indexed="true" stored="true" multiValued="false" required="false"/&gt;
  &lt;field name="text" type="text" indexed="true" stored="true"/&gt;
  &lt;field name="vector" type="knn_vector" indexed="true" stored="true" multiValued="false"/&gt;
  &lt;field name="_version_" type="long" indexed="true" stored="true" multiValued="false"/&gt;
  &lt;uniqueKey&gt;id&lt;/uniqueKey&gt;

&lt;/schema&gt;
				
			
```

The schema is the place where you tell Solr how it should build indexes from input documents. It is used to configure fields, specifying a set of field attributes to control which data structures are going to be produced.

As defined in our schema, documents consist of 3 simple fields:

1. the **`id`**
2. the document `text` (the source field with the text to transform into vectors)
3. the **`vector`** that stores the embeddings generated by the Python script seen in the earlier section

**Currently, *docValues* and *multiValued* are not supported for dense vector fields.**

The **dense vector field** [[1](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)] gives the possibility of indexing and searching dense vectors of float elements. In this case, we have defined it with:

* **name**: field type name
* **class**: solr.DenseVectorField
* **vectorDimension**: The dimension of the dense vector to pass in, which needs to be equal to the model dimension. In this case *384*.

***CURRENT** **LIMITATION**:  
The maximum cardinality of the vector is currently limited to **1024**, for no particular reason other than to be performance-conscious; it may be increased in the future, but for now, if you want to use a larger vector size, you need to customize the Lucene build and then set it in Solr.*

We left the other parameters with default values, in particular:

* **similarityFunction**: the vector similarity function used to return the top K most similar vectors to a target vector. The default is **euclidean**, otherwise, you can use **dot\_product** or **cosine**.
* **knnAlgorithm**: the underlying *knn* algorithm to use; **hnsw** is the only one supported at the moment.  
  **– hnswMaxConnections**: controls how many of the nearest neighbor candidates are connected to the new node. The default is **16**.  
  **– hnswBeamWidth**: the number of nearest neighbor candidates to track while searching the graph for each newly inserted node. The default is **100**.

***hnswMaxConnections***and***hnswBeamWidth***are advanced parameters, strictly related to the current algorithm used; they affect the way the graph is built at index time, so unless you really need them and know what their impact is, it is recommended not to change these values. In the*[Solr documentation](https://solr.apache.org/guide/solr/latest/query-guide/dense-vector-search.html)*, you can find the mapping between the Solr parameters and the*HNSW 2018 paper *parameters*.*

**N.B.**  
Once all the configuration files have been modified, it is necessary to **reload the collection** (or stop and restart Solr).

## 4. Index documents

Once we have created both the vector embeddings and the index, we are ready to push some documents.

Vector indexing in Solr is fairly straightforward and not much different from a multi-valued float.

We use [pysolr](https://pypi.org/project/pysolr/), a Python wrapper for Apache Solr, to index batches of documents.  
Here is the python script:

```
				
					import sys
import pysolr

## Solr configuration.
SOLR_ADDRESS = 'http://localhost:8983/solr/ms-marco'
# Create a client instance.
solr = pysolr.Solr(SOLR_ADDRESS, always_commit=True)

BATCH_SIZE = 100

def index_documents(documents_filename, embedding_filename):
    # Open the file containing text.
    with open(documents_filename, "r") as documents_file:
        # Open the file containing vectors.
        with open(embedding_filename, "r") as vectors_file:
            documents = []
            # For each document creates a JSON document including 
            both text and related vector. 
            for index, (document, vector_string) in enumerate
            (zip(documents_file, vectors_file)):

                vector = 
                [float(w) for w in vector_string.split(",")]
                doc = {
                    "id": str(index),
                    "text": document,
                    "vector": vector
                }
                # Append JSON document to a list.
                documents.append(doc)

                # To index batches of documents at a time.
                if index % BATCH_SIZE == 0 and index != 0:
                    # How you'd index data to Solr.
                    solr.add(documents)
                    documents = []
                    print("==== indexed {} documents ======"
                    .format(index))
            # To index the rest, when 'documents' list &lt; BATCH_SIZE.
            if documents:
                solr.add(documents)
            print("finished")

def main():
    document_filename = sys.argv[1]
    embedding_filename = sys.argv[2]
    index_documents(document_filename, embedding_filename)

if __name__ == "__main__":
    main()
				
			
```

**RESPONSE**

```
				
					==== indexed 100 documents ======
==== indexed 200 documents ======
...
finished
				
			
```

The python script will take in input 2 files, the one containing text and the one containing the corresponding vectors:

```
				
					sys.argv[1] = "/path/to/documents_10k.tsv"
sys.argv[2] = "/path/to/vectors_documents_10k.tsv
				
			
```

For each element of both files, the script creates a single JSON document (including the id, the text, and the vector) and adds it to a list; when the list reaches the BATCH\_SIZE set, the JSON documents will be pushed to Solr.  
E.g. JSON:

```
				
					{
	'id': '0',
	'text': 'The presence of communication amid scientific minds was equally important to the success of the Manhattan Project as scientific intellect was. The only cloud hanging over the impressive achievement of the atomic researchers and engineers is what their success truly meant; hundreds of thousands of innocent lives obliterated.\n',
	'vector': [0.0367823, 0.072423555, 0.04770486, 0.034890372, 0.061810732, 0.002282318, 0.05258357, 0.013747136, -0.0060595, 0.020382827, 0.022016432, 0.017639274, ..., 0.0054274425]
}
				
			
```

After this step, 10 thousand documents have been indexed in Solr and we are ready to retrieve them based on a query.

## Struggling implementing Neural Search in Apache Solr?

No need to worry! We have a recorded training waiting for you. You will be able to understand perfectly how to integrate Neural Search into Apache Solr, at your own pace and rhythm!

[Click here](https://sease.io/information-retrieval-mini-training/end-to-end-apachesolr-neural-search-tutorial)

## 5. Search exploiting vector fields

To make some queries, we downloaded the passage retrieval queries from MS Marco: [queries.tar.gz](https://msmarco.blob.core.windows.net/msmarcoranking/queries.tar.gz)

The query reported in the following examples is: `"what is a bank transit number"`.  
To transform it into vectors and use it in the KNN query, we run the python script *single-sentence-transformers.py* (from our GitHub project):

```
				
					from sentence_transformers import SentenceTransformer

# The sentence we like to encode.
sentences = ["what is a bank transit number"]

# Load or create a SentenceTransformer model.
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Compute sentence embeddings.
embeddings = model.encode(sentences)

# Create a list object, comma separated.
vector_embeddings = list(embeddings)
print(vector_embeddings)
				
			
```

The output will be an array of floats that must be copied into your queries:

```
				
					[-9.01364535e-03, -7.26634488e-02, -1.73818860e-02, ..., ..., -1.16323479e-01]
				
			
```

The following are several examples of neural search queries:

##### KNN query

From the searching perspective, a new query parser has been introduced to Solr: **knn Query Parser**

It takes as input only a few parameters:

* **f**: field where vector embeddings are stored
* **topK:**the number of nearest neighbors you want to retrieve
* **vector query**: a list of floats values between square brackets representing the query

**REQUEST**

```
				
					curl -X POST http://localhost:8983/solr/ms-marco/select?fl=id,text,score -d '
{
  "query": "{!knn f=vector topK=3}[-9.01364535e-03, -7.26634488e-02, -1.73818860e-02, ..., -1.16323479e-01]"
}'
				
			
```

**N.B.**The query should be a *POST*, because the vector is likely going to exceed the number of accepted characters for a GET URL. For ease of reading, in reporting the query we have reduced the length of the (very long) vector by inserting dots.

**RESPONSE**

```
				
					{
  "responseHeader":{
    ...,
    ...,
  "response":{"numFound":3,"start":0,"maxScore":0.44739443,"numFoundExact":true,"docs":[
      {
        "id":"7686",
        "text":["A. A federal tax identification number ... to identify your business to several federal agencies responsible for the regulation of business.\n"],
        "score":0.44739443},
      {
        "id":"7691",
        "text":["A. A federal tax identification number (also known as an employer identification number or EIN), is a number assigned solely to your business by the IRS.\n"],
        "score":0.44169965},
      {
        "id":"7692",
        "text":["Letâs start at the beginning. A tax ID number or employer identification number (EIN) is a number ... to a business, much like a social security number does for a person.\n"],
        "score":0.43761322}]
  }}
				
			
```

Having set *topK=3*, we got the best three documents for the query “*what is a bank transit number*“.

Again, for ease of reading, we limited the information included in the query response to a specified list of fields (**`fl`** parameter), without printing the (very long) dense vector field.

##### KNN + Pre-filtering

To overcome the limitation of post-filtering, described in the [documentation of Solr 9.0](https://solr.apache.org/guide/solr/9_0/query-guide/dense-vector-search.html#usage-with-filter-queries), **Pre-Filtering** has been introduced with Apache Solr 9.1

This contribution offers the possibility of running a filter query so that the scope of the search can be reduced first and then search for *topK* neighbors.

The knn vector-based search in your main query and the classic lexical search in the filter query:

**REQUEST**

```
				
					curl -X POST http://localhost:8983/solr/ms-marco/select?fl=id,text,score -d '
{
  "query" : "{!knn f=vector topK=3}[-9.01364535e-03, -7.26634488e-02, -1.73818860e-02, ..., -1.16323479e-01]",
  "filter" : "id:(7686 7692 1001 2001)"
}'
				
			
```

**RESPONSE**

```
				
					{
  "responseHeader":{
   ...,
   ...,
  "response":{"numFound":3,"start":0,"maxScore":0.44739443,"numFoundExact":true,"docs":[
      {
        "id":"7686",
        "text":["A. A federal tax identification number ... of business.\n"],
        "score":0.44739443},
      {
        "id":"7692",
        "text":["Letâs start at the beginning. A tax ID number ... for a person.\n"],
        "score":0.43761322},
      {
        "id":"1001",
        "text":["The 23,000-square-mile (60,000 km2) Matanuska-Susitna ... in 1818.\n"],
        "score":0.33552456}]
  }}
				
			
```

The results are prefiltered by the “*fq=id:(7686 7692 1001 2001)*” and then only the documents from this subset are considered candidates for the knn retrieval.  
Having set *topK=3*, knn query extracted the top 3 documents from a subset of 4.

##### Hybrid Search

Another available feature is to combine hybrid dense and sparse retrieval.  
In Apache Solr, there are query parsers that allow you to build a query by combining the results of different query parsers; such as the [boolean query parser](https://solr.apache.org/guide/solr/latest/query-guide/other-parsers.html#boolean-query-parser) where you can define multiple clauses that are going to affect how the search results are matched from your index and scored in your ranking.

In the following example, we define 2 `should` clauses: the first is a lexical clause, while the second clause is a pure vector-based search clause.

**REQUEST**

```
				
					curl -X POST http://localhost:8983/solr/ms-marco/select?fl=id,text,score -d '
{
    "query": {
        "bool": {
            "should": [
            "{!type=field f=id v='7686'}",
 "{!knn f=vector topK=3}[-9.01364535e-03, -7.26634488e-02, -1.73818860e-02, ..., -1.16323479e-01]"
            ]
        }
    }
}'
				
			
```

**RESPONSE**

```
				
					{
  "responseHeader":{
   ...}},
  "response":{"numFound":3,"start":0,"maxScore":4.4451337,"numFoundExact":true,"docs":[
      {
        "id":"7686",
        "text":["A. A federal tax identification number ... of business.\n"],
        "score":4.4451337},
      {
        "id":"7691",
        "text":["A. A federal tax identification number ... by the IRS.\n"],
        "score":0.44169965},
      {
        "id":"7692",
        "text":["Letâs start at the beginning. A tax ID number ... for a person.\n"],
        "score":0.43761322}]
  }}
				
			
```

In this case, the final list of search results is a combination of documents derived from both clauses (should), with*id:7686* having a higher score since, by matching both clauses, the two scores are added together.

##### Re-ranking query

It is currently possible to use [Query Re-Ranking](https://solr.apache.org/guide/solr/latest/query-guide/query-re-ranking.html) with the knn Query Parser.

Query Re-Ranking allows you to run a simple query (*q*) for matching documents and then reorder documents using the scores returned from a more complex query (knn query in this case).

**REQUEST**

```
				
					curl --location -g --request POST "http://localhost:8983/solr/ms-marco/select?q=id:(1001 7686 7692 2001)&amp;fl=id,text,score&amp;rq={!rerank reRankQuery=$rqq reRankDocs=4 reRankWeight=1}&amp;rqq={!knn f=vector topK=4}[-9.01364535e-03, -7.26634488e-02, ..., -1.16323479e-01]"
				
			
```

N.B.  
For ease of reading, we have decoded this query, but to make it work, you will simply have to encode the values (to remove the spaces, e.g. `q=id:(1001%207686%207692%202001)`, rq=`{!rerank%20reRankQuery%3D%24rqq%20reRankDocs%3D4%20reRankWeight%3D1}`) and disable the bash history expansion.

**RESPONSE**

```
				
					{
  "responseHeader":{
   ....}},
  "response":{"numFound":4,"start":0,"maxScore":3.9977393,"numFoundExact":true,"docs":[
      {
        "id":"7686",
        "text":["A. A federal tax identification number ... of business.\n"],
        "score":4.4451337},
      {
        "id":"7692",
        "text":["Letâs start at the beginning. A tax ID number ... for a person.\n"],
        "score":4.4353523},
      {
        "id":"1001",
        "text":["The 23,000-square-mile (60,000 km2) Matanuska-Susitna ... in 1818.\n"],
        "score":3.9977393},
      {
        "id":"2001",
        "text":["The researchers were in Baltimore on Tuesday ... believed.\n"],
        "score":3.9977393}]
  }}
				
			
```

The use of knn Query Parser for Re-Ranking is not recommended at the moment, for the following reasons.

What happens here is that the second pass score (deriving from the reRank query) is calculated only for documents within the k-nearest neighbors of the target vector to search and the current major limitation is that it is calculated **on the whole index** (not a subset of documents deriving from the main query).

In fact, in this case:

* for *id:7686* and *id:7692* the first pass score (deriving from the main query `q`) was added to the second pass score and multiplied by the multiplicative factor (`reRankWeight`)
* for *id:1001* and *id:2001* the original document score remains unchanged since they match the original query but not the knn re-ranking query (out of the *topK*).

Therefore, you’re not running a one-to-one rescoring of each of the first-pass retrieval search results but you just effectively intersect them with the knn results.

## Future Works

Our recent open source contributions finally brought the [neural search into Apache Solr](https://sease.io/2022/01/apache-solr-neural-search.html) and we hope this tutorial helps you to understand how you can leverage this new Solr feature to improve your search experience!

There is still some work to do, in particular, we are planning to contribute to Apache Solr:

* A **model management tool** that could be a separate VM and leverage a different storage system (instead of Zookeeper). The idea is to manage Language Models in a similar way that the Learning To Rank integration does.
* An **update request processor** that takes in input a BERT model and does the inference vectorization at **indexing time**, to automatically enrich documents.
* A **query parser**, which takes in input a BERT model and does the inference vectorization at **query time**, in order to automatically encode the query.

## Need Help With This Topic?​​

If you’re struggling with Neural Search in Apache Solr, don’t worry – we’re here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click here](mailto:info@sease.io)

## Need Help with this topic?​

If you're struggling with Neural Search in Apache Solr, don't worry - we're here to help! Our team offers expert services and training to help you optimize your Solr search engine and get the most out of your system. Contact us today to learn more!

[Click Here](mailto:info@sease.io)