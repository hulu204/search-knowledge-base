---
title: 'Understanding Embeddings in the Italian Language – Part 3'
company: Sease
tag: 召回
date: 2026-10-01
url: https://sease.io/2026/10/understanding-embeddings-in-the-italian-language-part-3.html
account: 
origin: en-rss
---
Hi everyone! Welcome back!

This blog post is the third one of the series related to my Master’s thesis (if you missed the second one, here is the [link](https://sease.io/2026/09/understanding-vector-embeddings-in-the-italian-language-part-2.html) 😉).  
We’ll cover:

* Methodologies:
  + Main evaluation metric
  + Relational database Dbpedia-Entity-v2
  + Baselines for evaluation
  + Virtual Machines and Data Types
  + Fine-tuning
  + Wilcoxon signed-rank test
  + Vector database

This will be a pretty long one. Hope you’ll find this study helpful!

## Methodologies

### Main Evaluation Metric

The main evaluation metric used in this work is normalised Discounted Cumulative Gain, considering only the top 10 returned documents. *nDCG@k* measures the quality of the ranking, giving more weight to the positions at the top of the list, and the formula is the following:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-001](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-001.webp)

where

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-002](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-002.webp)

In the above formula, *rel(i)* is an indicator function telling us if the i-th document is relevant (and it takes value 1) or not (and it takes value 0), and *IDCG@k* is the ideal *DCG@k*, so the one computed when all the relevant documents are retrieved in the top spots.

### Relational Database Dbpedia-Entity-v2

Looking at the structure of the dataset, we decided to create a Relational Database containing the translated dataset of *DBpedia-Entity-v2* [[1](#3)], since the original structure of the dataset was already splitted in 3 different files: queries, documents, and qrels, where qrels defines a many-to-many relationship between documents and queries. This choice is motivated by the fact that each sample of both files containing queries and documents had a unique id, and the qrels file links the two previous files through the unique identifiers of queries and documents, while also providing a relevance judgment score that indicates the degree of relevance of each document with respect to a given query. More than this, I wanted to learn to interact with relational databases, and, looking at the structure of the data, we decided to go for it, using an ORM called SQLModel. The result is illustrated in the following UML diagram:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-003](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-003.webp)

It’s very important to note that **`Doc`** table has a field called **`is_subsampled`**. This field is the one that identifies the documents used in both validation and test processes. To limit both computational cost and training time, we decided to reduce the number of documents in this dataset. In this way, at indexing time, we avoid computing an excessive number of embeddings. The documents carrying this flag are those that appear in the relevance judgments section of the DBpedia-Entity-v2 [[1](#1)]. Since these were not sufficient and we aimed to include additional ones, we decided to randomly add further documents from the test dataset until reaching a total of 150k documents.

The class **`Chunk`** represents chunks of documents, created during pre-processing. The chunking strategy was straightforward: each document was split into segments matching the model’s maximum window size. To preserve continuity across boundaries, adjacent chunks were created with a small overlap of 50 to 100 tokens, depending on the model’s window size. At the end, each document keeps its text, but each element in the **`Chunk`** table is a chunk related to one model coming from a specific document. This creates a one-to-many relationship between the **`Document`** table and the **`Chunk`** table.

### Baselines for Evaluation

Just to give a comparison with (non-tuned) lexical search systems, in our study, we decided to also add two well-known count-based systems:

* TF-IDF
* BM25

##### TF-IDF

TF-IDF, which stands for Term Frequency-Inverse Document Frequency, is a widely used statistical measure in NLP and information retrieval that **evaluates the importance of a word within a document, considering its frequency across the entire collection of documents, known as a corpus.**

The Term Frequency (TF) component measures how frequently a term *t* appears in a particular document *d*.

To understand the intuition behind TF, consider the following assumption: terms that appear often in a document are usually more representative of its content, since they signal what the document is *about*. Conversely, if a term appears rarely, it contributes less to describing the document’s topic. TF captures this by increasing the weight of recurring terms and dampening the influence of those that appear only once or twice.

The formula for TFt,d can be expressed as:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-004](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-004.webp)

It is common to squash the raw frequency a bit, using the log10 of the frequency instead, resulting in a loss of the amplitude.

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-005](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-005.webp)

On the other hand, Inverse Document Frequency (IDF) assesses how common or rare a term is across all documents in the corpus. It helps reduce the weight of terms that occur frequently in many documents, thus highlighting terms that are more unique and potentially more informative. IDFt is calculated using the following formula:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-006](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-006.webp)

The final TF-IDFt,d score for a term is obtained by multiplying its TFt,d and IDFt values:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-007](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-007.webp)

At this point, we compute TF-IDFt,d for each term *t* in the provided query *q* with each document *d* in the collection and sum all the obtained values, obtaining the following score:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-008](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-008.webp)

We chose **TF-IDF because it is a great baseline in NLP**, due to its simplicity and the fact that it is count-based. Thus, it does not account for semantic meaning or context beyond word counting, which can lead to suboptimal results for queries and documents that require deeper understanding.

##### BM25

BM25, or Best Match 25, also known as Okapi BM25, is a variant of the TF-IDF family. Developed in the 1990s, BM25 builds on earlier probabilistic models and introduces several enhancements over traditional methods such as TF-IDF.

The core components of BM25 include Term Frequency, Inverse Document Frequency, and document length normalisation. Term Frequency measures how often a term appears in a document, with BM25 employing a modified version that accounts for diminishing returns, meaning that after a certain point, additional occurrences of the term contribute less to the overall score. This adjustment helps prevent overly high scores for documents that contain many repetitions of a term.

Inverse Document Frequency evaluates the rarity of a term across the entire corpus. It operates on the principle that terms appearing in fewer documents should carry more weight, thus enhancing the relevance of documents containing these rare terms. The formula for IDF is structured to provide higher scores for terms that are less common across documents.

The length of the document is another critical factor in BM25. The algorithm normalises the scores based on the length of each document compared to the average length of the documents in the collection. This normalisation ensures that longer documents do not receive an unfair advantage simply due to their size, which could lead to skewed relevance rankings.

BM25 incorporates two tunable parameters: *k1* and *b*. The parameter *k1* adjusts the influence of term frequency, while *b* controls the extent to which the length of the document affects the score. Typically, *k1* is set between 1.2 and 2.0, and *b* is often set around 0.75.

The overall BM25 score for a document concerning a query is computed using the following formula:

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-009](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-009.webp)

Where:

* TF*qi,d* is the frequency of term *qi* in the document *d*.
* |d| is the length of the document *d*.
* |davg| is the length of the average document of all the documents in the corpus.
* IDF*qi* denotes the Inverse Document Frequency for term *qi*.

BM25 has several advantages over its predecessors. It dynamically adjusts rankings based on the distribution of terms within a collection, making it more adaptable to different types of queries and documents.

However, BM25 also has limitations. **As TF-IDF, this approach also suffers from a lack of semantic meaning or context beyond term matching.**

### Virtual Machines and Data Types

Amazon Web Services (AWS) has been used to develop this project. In this service, there are a lot of different Virtual Machines to choose from: we decided to go with an Ubuntu-based machine with a GPU called *g5.xlarge* with 24GB of vRAM and a pre-made deep learning setting to be able to track the GPU usage.

The choice of this particular GPU has been made with respect to the use of the *bfloat16* data type. It was originally developed by Google and is called the “Brain Floating Point Format”. The name comes from “Google Brain”, which is an artificial intelligence research group at Google where the idea for this data type was conceived. The *bfloat16* format uses 16 bits to represent a number (as in *float16*) but maintains the original range from *float32*. This is done by truncating the *float32* to use only 7 bits for the decimal places, which allows for fast conversion to and from a *float32*, at the expense of precision, but gaining in speed. The following image shows the differences between the three data types just described.

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-010](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-010.webp)

This datatype is supported only on some type of GPU, like the NVIDIA A10 ones adopted in the *g5* instances by AWS. **This choice gives us a 3 times faster computation of gradients during training.**

### Fine-Tuning

The idea for fine-tuning our models is to add an adapter on top of the query embedding (as introduced in [[2](#11)]), with the idea of letting the model learn to map queries’ embeddings near the documents’ embeddings. In retrieval settings, queries are typically short and information-sparse, while documents contain more context and therefore produce richer embeddings. This imbalance can lead the model to represent queries and documents in slightly different regions of the embedding space. By introducing an adapter, we give the model a mechanism to compensate for this asymmetry and align both the queries ‘ and the documents ‘ representations within a shared semantic space, making them lie close to each other.

In the paper mentioned above, the concept of “adapter” is simple: a Multi Layer Perceptron (MLP), where the input and output dimensions are the same (in our case, the dimension of the embedding). In this work, we decided to use this fine-tuning methodology only when we were not satisfied with the plain fine-tuning of the embedding models. We started simple: 0 hidden layers (so the adapter becomes just a matrix multiplication), and added one hidden layer if we were not satisfied yet. We will refer to this 2 variants as “linear adapter” and “non-linear adapter” (due to the activation function in the hidden layer, which removes linearity).

As an architectural consideration, to ensure consistency with the pre-trained models, we added a normalisation layer after the adapter. A significant advantage of using only the adapter is that we need to store only its parameters. This results in minimal memory usage, as the number of parameters is limited to

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-011](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-011.webp)

for the linear adapter and

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-012](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-012.webp)

for the non-linear one.

For the largest model tested, namely *bge-m3*, the simple linear adapter on top of the query was not working as expected: we didn’t see any improvement with any of the methods we tried. We thought that two things could cause this:

* too big chunks;
* not enough representational capacity to capture the full complexity of the transformation required between queries and documents.

So we tried both by decreasing the chunk size of the biggest model to only 512 tokens or by using a non-linear adapter with an inner dimension as a new hyperparameter.

Fine-tuning was performed only on a subset of the training dataset, as mMARCO is very large.

Referring to the documentation of the [sentence-transformer library,](https://sbert.net/) we decided to choose `TripletLoss` from the PyTorch library as the loss function for our model. This specific type of loss function requires data to be organised into triplets composed of: a query, a relevant document, and a non-relevant document. For this reason, each element of both the training and validation datasets was processed to achieve this configuration.

We decided to limit the fine-tuning to only 5M training samples and use a validation set of 10k elements, which validates 5 times per epoch, to minimise the usage of virtual machines as much as possible. We are aware that this method is not optimal, but performing a grid search on the full dataset crafted for training would have taken too much time, so it was conducted based on the results from only the first epoch (out of 10). So the full fine-tuning of the model (across all epochs) was performed only after selecting the appropriate hyperparameter configuration.

We decided to focus solely on the learning rate as the hyperparameter to optimise, given the limited computational resources and the need to avoid an excessively large grid search. In the end, the grid search for the linear adapter collapsed to the optimisation of a single parameter.

Looking at [[3](#3)], we decided to schedule the learning rate. We used the function `SequentialLR` in PyTorch, linearly increasing the learning rate in the first 10% of the training phase and decreasing cosinely in the remaining 90%, with the function `CosineAnnealingLR`. Linear increase has been chosen to simulate a linear warm-up, and cosine annealing is frequently used by the [sentence-transformer library](https://sbert.net/).

![2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887-fig-013](../images/2528-Understanding-Embeddings-in-the-Italian-Language-3a39e887/figure-013.webp)

Learning rate schedule plot, with the percentage of the used learning rate on the y-axis and over 100 iterations (example with 10 hypothetical epochs with 10 iterations each).

The learning rate is paired with the *AdamW* optimiser, which combines the classic Adam algorithm with weight decay. To avoid introducing an additional hyperparameter, we kept the weight decay at its default value of *0.01*.

|  |  |  |  |
| --- | --- | --- | --- |
| **Model** | **Adapter** | **Learning Rate** | **Adapter hidden layer dimension** (only for non-linear adapter) |
| LaBSE | linear | [5·10-6, 10-6, 5·10-5, 10-5, 5·10-4, 10-4, 0.005, 0.001, 0.05, 0.01] |  |
| multilingual-e5-large | linear | [5·10-6, 10-6, 5·10-5, 10-5, 5·10-4, 10-4, 0.005, 0.001, 0.05, 0.01] |  |
| bge-m3 | [linear, non-linear] | [5·10-6, 10-6, 5·10-5, 10-5, 5·10-4, 2.5·10-4, 10-4, 0.005, 0.001, 0.05, 0.01] | [512, 1024, 2048] |

*Tested hyperparameters for each model configuration.*

### Wilcoxon Signed-Rank Test

In NLP research, statistical tests are essential to validate whether improvements in model performance are statistically significant or due to random chance. This *Wilcoxon signed-rank test* is a non-parametric rank test for statistical hypothesis testing used to compare the locations of two populations using two matched samples, in our case, the results of the fine-tuned embedding model vs the original model on the DBpedia-Entity-v2 test set [[1](#3)].

The choice of the *Wilcoxon signed-rank test* has been made since the non-normal distribution is often observed in NLP model performance metrics. Unlike parametric tests, which assume a normal distribution of the data, non-parametric tests like the *Wilcoxon signed-rank test* do not require this assumption. This flexibility makes this test particularly suitable for our evaluations, since our data do not follow a normal distribution.

### Vector Database

These specialised databases are designed to handle both structured and unstructured data, being able to deal with integers and text, while also managing their high-dimensional vector representations, thus their embeddings. The relevance of vector databases to our semantic search domain is due to three key features. First, their efficiency is evident in their optimised design, which supports rapid searches within high-dimensional spaces. Second, they offer impressive scalability, easily accommodating large datasets and handling high volumes of queries. Finally, they achieve high accuracy by leveraging advanced algorithms that retrieve the most relevant and similar results.

We focused our evaluation on two specific vector search algorithms within the vector database: the Hierarchical Navigable Small World (HNSW) algorithm [[4](#12)] and exhaustive search.

Its older version, Navigable Small World (NSW), is a graph-based algorithm that finds approximate nearest neighbours in a dataset. The general idea here is first to imagine many nodes in a network. Each node will have short-, medium- and long-range connections to other nodes. When performing a vector search, the algorithm begins at some pre-defined entry point. From there, it evaluates connections to other nodes and jumps to the one closest to the one we hope to find. This process repeats until our nearest neighbour is found.

HNSW is an approximate K-nearest neighbour search algorithm based on navigable small world graphs with a controllable hierarchy (Hierarchical NSW, HNSW). It is fully graph-based, eliminating the need for additional search structures, which are typically used during the search stage of most proximity graph techniques. HNSW incrementally builds a multi-layer structure consisting of a hierarchical set of proximity graphs (one for each layer) for nested subsets of the stored elements. The maximum layer in which an element is present is randomly selected with an exponentially decaying probability distribution. After doing so, the element is inserted in all the layers under the selected layer. During the search, the layered graph is traversed from top to bottom, searching for the nearest neighbour in the graph of each layer. Since the upper layers contain fewer data points than the bottom ones, the neighbours in the first phases of the search are further away from each other than the ones in the following phases of the search. This concept is very similar to the one in skip lists (and, actually, the idea is borrowed from that data structure). In this way, the HNSW algorithm provides a smart solution for efficient similarity search in large datasets, since the hierarchical approach makes HNSW highly efficient for both insertion and search tasks, which is particularly valuable when working with high-dimensional vector data. HNSW offers a viable alternative to exhaustive search methods, which have become increasingly impractical in large datasets due to the time required to calculate similarity scores across all entries.

Our implementation used [Weaviate](https://weaviate.io/), a powerful vector database platform that offers robust functionality, including local deployment through Docker, which proved to be particularly practical for our work. Based on how models are trained, we used cosine similarity as our similarity metric. We were able to compare both the HNSW and exhaustive search approaches, as our dataset of 150,000 documents was manageable enough to allow both. Although the exhaustive search produced the most accurate results, HNSW showed a substantial advantage in speed. Notably, in a production environment, HNSW would be the preferred choice due to its scalability and efficiency.

## REFERENCES

[1] F. Hasibi, F. Nikolaev, C. Xiong, K. Balog, S. E. Bratsberg, A. Kotov, and J. Callan, “DBpedia-entity v2: A test collection for entity search,” in Proceedings of the 40th International ACM SIGIR Conference on Research and Development in Information Retrieval, ser. SIGIR ’17.

[2] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, M. Wang, and H. Wang, “Retrieval-augmented generation for large language models: A survey,” 2024. [Online]. [Link](https://arxiv.org/abs/2312.10997)

[3] J. Kaddour, O. Key, P. Nawrot, P. Minervini, and M. J. Kusner, “No train no gain: Revisiting efficient training algorithms for transformer-based language models,” 2023. [Online]. [Link](https://arxiv.org/abs/2307.06440)

[4] Y. A. Malkov and D. A. Yashunin, “Efficient and robust approximate nearest neighbor search using hierarchical navigable small world graphs,” 2018. [Online]. [Link](https://arxiv.org/abs/1603.09320)

## Bringing Information Retrieval research into production

Research is where better search starts. If you're exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[talk to our search experts](mailto:info@sease.io)

## Bringing Information Retrieval research into production

Research is where better search starts. If you’re exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[Talk to our search experts](mailto:info@sease.io)