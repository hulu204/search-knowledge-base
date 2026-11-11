---
title: 'Understanding Embeddings in the Italian Language – Part 4'
company: Sease
tag: 召回
date: 2026-10-08
url: https://sease.io/2026/10/understanding-embeddings-in-the-italian-language-part-4.html
account: 
origin: en-rss
---
Hi everyone! Welcome back!

This blog post is the fourth (and last) one of the series related to my Master’s thesis (if you missed the third one, here is the [link](https://sease.io/2026/01/understanding-embeddings-in-the-italian-language-part-3.html↗) 😉).  
We’ll cover:

* Results
* Conclusions
* Future works

Hope you’ll find this study helpful!

## Results

In these comparisons, we consistently use the *nDCG@10* metric as our primary measure, as it captures the relevance of the top 10 retrieved documents, emphasising how well each model ranks relevant results at the highest positions.

The histogram below reports the performance of different model configurations. Model names encode both the adopted search strategy and the presence of adapter-based fine-tuning. Models denoted only by their name rely on feature extraction, while the suffix **`_hy`** indicates a hybrid search strategy combining semantic and lexical retrieval. The term `adapt` refers to models fine-tuned using adapters; when the adapter type is not explicitly specified, a linear adapter is assumed. Finally, the combination **`_hy adapt`** identifies a hybrid search configuration applied to an adapter fine-tuned model.

![2531-Understanding-Embeddings-in-the-Italian-Language-d0a21fb8-fig-001](../images/2531-Understanding-Embeddings-in-the-Italian-Language-d0a21fb8/figure-001.webp)

*A histogram giving a visual representation of the performance of the different models in the case of the exhaustive search for the asymmetric case.*

Each epoch for the *LaBSE* model took 3 minutes, while for the other two models, *multilingual-e5-large* and *bge-m3*, it took 10 minutes per epoch. It should be noted that *bfloat16* was used as a data type, which significantly accelerated the training. In fact, before switching data type, the times were 10 and 30 minutes, respectively, for the models mentioned above.

The batch size was chosen with the aim of minimising computation time. This was achieved by manually monitoring the utilisation of the available GPU using the command nvidia-smi and conducting tests to maximise its usage. Consequently, each model has a different batch size, and the selected hyperparameters for all our models are detailed in the table below.

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Model** | **Embedding dimension** | **Adapter** | **Learning Rate** | **Batch size** | **Adapter Memory** |
| LaBSE | 768 | linear | 0.005 | 256 | 2.25 MB |
| mult-e5-large | 1024 | linear | 0.001 | 128 | 4.00 MB |
| bge-m3 | 1024 | linear | 0.00025 | 128 | 4.00 MB |
| bge-m3 | 1024 | non-linear (ReLU w/ 512 inner dim) | 0.001 | 32 | 16.01 MB |

*Best hyperparameters selected for each model configuration.*

The number of parameters for each adapter is very small, resulting in model files that occupy minimal memory. When initialising our custom embedding model, it is sufficient to import the corresponding pre-trained model from [HuggingFace](https://huggingface.co/) and update only the adapter parameters with those obtained from our fine-tuning.

The significant reduction in batch size for the *bge-m3* model, after investigating the GPU memory usage during training, is believed to be due to the model’s large context window (8196 tokens). In fact, when very long documents were processed by the model, the allocated memory increased dramatically. To avoid this issue, we had to reduce the batch size to only 32 documents at a time.

Obviously, the memory usage of the adapter parameters varies depending on the embedding size. For example, *LaBSE* is the lightest (with an embedding size of 768), while the adapters for *multilingual-e5-large* and *bge-m3* share the same size. However, when using a 1-hidden-layer adapter, the memory usage increases accordingly due to the additional parameter: the size of the hidden layer.

Hybrid search combines the outcomes of a vector-based search with BM25F —a keyword-based search method from the BM25 family— by fusing the two result sets. For this analysis, we used the default Weaviate configuration for hybrid search without any exploration of hybrid search parameters/fuse methods, as our primary focus was on evaluating neural models.

We tested our models on the 400 queries of the *DBpedia-Entity-v2* test set [[1](#3)], with inference times measured using the fastest available search strategy between exact kNN search and HNSW-based approximate search, which in practice corresponds to HNSW. This search strategy is significantly more scalable for databases with a large number of documents, at the cost of slightly lower retrieval accuracy.

In the histogram at the beginning of this section, the results are statistically significant at a 0.001% level in the comparison between the fine-tuned and non-fine-tuned models, marked with the \* (asterisk) symbol, indicating where the p-value is less than 0.001.

Results from the Wilcoxon signed-rank test showed that the fine-tuned model outperformed its non-fine-tuned version for the two models *LaBSE* and *multilingual-e5-large*, suggesting that it retrieves more relevant documents within the top 10 results. This improvement is particularly important in a RAG context, where retrieving high-quality supporting documents improves the generation relevance score.

Our best model among all those presented is the *multilingual-e5-large* with a linear adapter, fine-tuned by us, achieving an *nDCG@10* of 53.89 and an average inference time of 47 milliseconds per query.

As for the *bge-m3* model, unfortunately, we were unable to improve its performance with the resources we had. This could be the subject of future investigations. We also decided to stop trying to improve this model, as the results with *multilingual-e5-large* were quite promising, as we will discuss in the next section.

### multilingual-e5-large with adapter vs text-embedding-3-small

We decided to test all our models with *text-embedding-3-small*. The only one worth testing was our best model: *multilingual-e5-large* with an adapter.

Once again, we used the *Wilcoxon signed-rank test* to verify the significance of our results. It turns out that our model is statistically better with a p-value < 0.05, which is indicated with the $ (dollar) symbol. Although this is not an excellent result, considering that it was tested on a relatively small test set (*n=400* samples), it is still a good outcome.

In the future, we could consider using our best fine-tuned model instead of the OpenAI model, thus avoiding the costs associated with embeddings and API calls during usage. The models we have presented are also capable of running on machines equipped only with CPUs, although with significantly longer times for the computation of the query embedding. As for the search in the database, it is still conducted through a Docker container that utilises the CPU. The inference times were measured locally on my personal machine, which is equipped with a laptop GPU 1050Ti and a 9th-generation i5 processor. These times will inevitably improve on more performant machines.

|  |  |  |
| --- | --- | --- |
| Model | Embedding dimension | Average search time |
| LaBSE linear | 768 | 32 ms |
| multilingual-e5-large linear | 1024 | 47 ms |
| bge-m3 | 1024 | 52 ms |
| text-embedding-3-small | 1536 | 615 ms |

*Average search times using the HNSW algorithm for the test set of 400 queries, based on the embedding dimension of each model.*

It can be observed that the inference times increase by an order of magnitude when using OpenAI embeddings (615 ms compared to 47 ms for the *multilingual-e5-large* model). This is due to both the API call to the client and the fact that the search must be performed on embeddings with a size of 1536 instead of 1024. In a potential RAG application, this is highly relevant as we want the documents to be retrieved as quickly as possible, to then be fed into a language model capable of extracting and reformulating the information present in the documents. This second step takes more time because an LLM typically has many more parameters.

The cost of generating embeddings using the *text-embedding-3-small* model is 0.28$ (via batch processing to minimise API calls), as the 150,000 documents selected from the *DBpedia-Entity-v2* dataset [[1](#3)] consist of 13,782,932 tokens. However, it is important to note that each user query incurs an additional API call to embed the query text into a vector. Although this cost is relatively low, it is not negligible.

The total cost of training the *multilingual-e5-large* model, including grid search (2 hours) and training (1 hour and 40 minutes) on a g5.xlarge machine costing 1.258$ per hour, amounts to 4.61$.

On the other hand, embedding generation for other models was cost-free, as it was performed in approximately one hour on my personal machine equipped with a 1050 Ti Mobile GPU, as mentioned earlier.

## Conclusions

In short, the most important findings are summarised as follows:

* **Adapter-based fine-tuning works:** Our approach significantly improved two out of three models (*multilingual-e5-large* and *LaBSE*), with gains confirmed by strong statistical significance (p < 0.001).
* **Competitive performance:** The adapter-enhanced *multilingual-e5-large* even outperformed OpenAI’s *text-embedding-3-small* on our test set (p < 0.05).
* **Cost and efficiency advantage:** The adapter-enhanced *multilingual-e5-large* also surpassed *text-embedding-3-small* in terms of lower cost and faster average search time.
* **Model limitations:** Fine-tuning *bge-m3* did not lead to improvements, suggesting that not all architectures benefit from adapter-based methods.
* **Data type usage**: The use of *bfloat16* decreased training time by a factor of 3.
* **Constraints of the study:** Results are based on a relatively small document database (150K) and translated datasets, which may limit generalizability.

## Future Works

Future research could build on this work in several ways. Exploring alternative fine-tuning techniques, such as prompt-tuning or prefix-tuning, might uncover more effective methods for adapting models to specific tasks for the Italian language. Investigation of failed fine-tuning techniques might be further pursued.

Additionally, a reranking strategy could be implemented to increase the reliability of the retrieved documents. This would further boost performance in our pipeline.

More than that, limitations related to the dataset use could be addressed by using pre-aligned English-Italian datasets, trying to eliminate translation-related biases. Moreover, a domain-specific dataset could be explored, and the models evaluated could be tested to determine whether they perform effectively only in general scenarios or are better suited for specific use cases, like in legal or medical domains.

Furthermore, pre-processing stages like query rewriting could be integrated into the pipeline, where we can prompt LLM to rewrite the queries, providing further context to address any lack of specific semantic load, thereby ensuring the optimal relevance of the generated answers.

Another promising direction involves embedding the fine-tuned models into a complete RAG pipeline. Such an integration would provide valuable insights into their performance in real-world applications, particularly when tested on larger or specialised datasets, such as legal or medical domains.

Additionally, incorporating user-centred evaluation metrics would offer a clearer understanding of system effectiveness. Testing under adversarial conditions or with noisy queries could further assess the robustness of the models.

Finally, making fine-tuned models and code publicly available could encourage community-driven improvements and support the development of open-source alternatives to proprietary embedding systems.

By addressing these limitations and exploring these future directions, subsequent studies could advance semantic search capabilities for Italian and other languages, promoting more accessible NLP solutions.

## REFERENCES

[1] F. Hasibi, F. Nikolaev, C. Xiong, K. Balog, S. E. Bratsberg, A. Kotov, and J. Callan, “DBpedia-entity v2: A test collection for entity search,” in Proceedings of the 40th International ACM SIGIR Conference on Research and Development in Information Retrieval, ser. SIGIR ’17.

## Bringing Information Retrieval research into production

Research is where better search starts. If you're exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[talk to our experts](mailto:info@sease.io)

## Bringing Information Retrieval research into production

Research is where better search starts. If you’re exploring new approaches to ranking, embeddings, vector search, or search quality evaluation, our team can help you understand how they perform on your own data and use case.

[Talk to our experts](mailto:info@sease.io)