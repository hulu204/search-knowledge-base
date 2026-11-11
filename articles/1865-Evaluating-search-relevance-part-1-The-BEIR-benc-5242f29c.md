---
title: 'Evaluating search relevance part 1 - The BEIR benchmark'
company: Elastic
tag: 评测
date: 2024-07-16
url: https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-1
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Evaluating search relevance part 1 - The BEIR benchmark

Learn to evaluate your search system in the context of better understanding the BEIR benchmark, with tips & techniques to improve your search evaluation processes.

July 16, 2024

[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)[Thomas Veasey](/search-labs/author/thomas-veasey)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

Part of the series:

[Evaluating search relevance](/search-labs/blog/series/evaluating-search-relevance)

In this series

Share

This is the first in a series of blog posts discussing how to think about evaluating your own search systems in the context of better understanding the BEIR benchmark. We will introduce specific tips and techniques to improve your search evaluation processes in the context of better understanding BEIR. We will also introduce common gotchas which make evaluation less reliable. Finally, we note that LLMs provide a powerful new tool in the search engineers' arsenal and we will show by example how one can use them to help evaluate search.

## Understanding the BEIR benchmark in search relevance evaluation

To improve any system you need to be able to measure how well it is doing. In the context of search [BEIR](https://arxiv.org/abs/2104.08663) (or equivalently the Retrieval section of the [MTEB](https://huggingface.co/spaces/mteb/leaderboard) leaderboard) is considered the “holy grail” for the information retrieval community and there is no surprise in that. It’s a very well-structured benchmark with varied datasets across different tasks. More specifically, the following areas are covered:

* Argument retrieval (ArguAna, Touche2020)
* Open-domain QA (HotpotQA, Natural Questions, FiQA)
* Passage retrieval (MSMARCO)
* Duplicate question retrieval (Quora, CQADupstack)
* Fact-checking (FEVER, Climate-FEVER, Scifact)
* Biomedical information retrieval (TREC-COVID, NFCorpus, BioASQ)
* Entity retrieval (DBPedia)
* Citation prediction (SCIDOCS)

It provides a single statistic, nDCG@10, related to how well a system matches the most relevant documents for each task example in the top results it returns. For a search system that a human interacts with relevance of top results is critical. However, there are many nuances to evaluating search that a single summary statistic misses.

## Structure of a BEIR dataset

Each benchmark has three artefacts:

* the corpus or documents to retrieve
* the queries
* the relevance judgements for the queries (aka `qrels`).

Relevance judgments are provided as a score which is zero or greater. Non-zero scores indicate that the document is somewhat related to the query.

| Dataset | Corpus size | #Queries in the test set | #qrels positively labeled | #qrels equal to zero | #duplicates in the corpus |
| --- | --- | --- | --- | --- | --- |
| Arguana | 8,674 | 1,406 | 1,406 | 0 | 96 |
| Climate-FEVER | 5,416,593 | 1,535 | 4,681 | 0 | 0 |
| DBPedia | 4,635,922 | 400 | 15,286 | 28,229 | 0 |
| FEVER | 5,416,568 | 6,666 | 7,937 | 0 | 0 |
| FiQA-2018 | 57,638 | 648 | 1,706 | 0 | 0 |
| HotpotQA | 5,233,329 | 7,405 | 14,810 | 0 | 0 |
| Natural Questions | 2,681,468 | 3,452 | 4,021 | 0 | 16,781 |
| NFCorpus | 3,633 | 323 | 12,334 | 0 | 80 |
| Quora | 522,931 | 10,000 | 15,675 | 0 | 1,092 |
| SCIDOCS | 25,657 | 1,000 | 4,928 | 25,000 | 2 |
| Scifact | 5,183 | 300 | 339 | 0 | 0 |
| Touche2020 | 382,545 | 49 | 932 | 1,982 | 5,357 |
| TREC-COVID | 171,332 | 50 | 24,763 | 41,663 | 0 |
| MSMARCO | 8,841,823 | 6,980 | 7,437 | 0 | 324 |
| CQADupstack (sum) | 457,199 | 13,145 | 23,703 | 0 | 0 |

**Table 1**: Dataset statistics. The numbers were calculated on the test portion of the datasets (`dev` for `MSMARCO`).

**Table 1** presents some statistics for the datasets that comprise the `BEIR` benchmark such as the number of documents in the corpus, the number of queries in the test dataset and the number of positive/negative (query, doc) pairs in the `qrels` file. From a quick a look in the data we can immediately infer the following:

* Most of the datasets do not contain any negative relationships in the `qrels` file, i.e. zero scores, which would explicitly denote documents as irrelevant to the given query.
* The average number of document relationships per query (`#qrels` / `#queries`) varies from 1.0 in the case of `ArguAna` to 493.5 (`TREC-COVID`) but with a value `<`5 for the majority of the cases.
* Some datasets suffer from duplicate documents in the corpus which in some cases may lead to incorrect evaluation i.e. when a document is considered relevant to a query but its duplicate is not. For example, in `ArguAna` we have identified 96 cases of duplicate doc pairs with only one doc per pair being marked as relevant to a query. By “expanding” the initial qrels list to also include the duplicates we have observed a relative increase of ~1% in the `nDCG@10` score on average.

```
{
  "_id": "test-economy-epiasghbf-pro02b",
  "title": "economic policy international africa society gender house believes feminisation",
  "text": "Again employment needs to be contextualised with …",
  "metadata": {}
}
{
  "_id": "test-society-epiasghbf-pro02b",
  "title": "economic policy international africa society gender house believes feminisation",
  "text": "Again employment needs to be contextualised with …",
  "metadata": {}
}
```

**Example of duplicate pairs in ArguAna. In the qrels file only the first appears to be relevant (as counter-argument) to query (“test-economy-epiasghbf-pro02a”)**

When comparing models on the MTEB leaderboard it is tempting to focus on average retrieval quality. This is a good proxy to the overall quality of the model, but it doesn't necessarily tell you how it will perform for you. Since results are reported per data set, it is worth understanding how closely the different data sets relate to your search task and rescore models using only the most relevant ones. If you want to dig deeper, you can additionally check for topic overlap with the various data set corpuses. Stratifying quality measures by topic gives a much finer-grained assessment of their specific strengths and weaknesses.

One important note here is that when a document is not marked in the `qrels` file then by default it is considered irrelevant to the query. We dive a little further into this area and collect some evidence to shed more light on the following question: “How often is an evaluator presented with (query, document) pairs for which there is no ground truth information?". The reason that this is important is that when only shallow markup is available (and thus not every relevant document is labeled as such) one Information Retrieval system can be judged worse than another just because it “chooses” to surface different relevant (but unmarked) documents. This is a common gotcha in creating high quality evaluation sets, particularly for large datasets. To be feasible manual labelling usually focuses on top results returned by the current system, so potentially misses relevant documents in its blind spots. Therefore, it is usually preferable to focus more resources on fuller mark up of fewer queries than broad shallow markup.

## Leveraging the BEIR benchmark for search relevance evaluation

To initiate our analysis we implement the following scenario (see the [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/evaluating-search-relevance-part-1/retrieve-and-rerank.ipynb)):

1. First, we load the corpus of each dataset into an Elasticsearch index.
2. For each query in the test set we retrieve the top-100 documents with BM25.
3. We rerank, the retrieved documents using a variety of SOTA reranking models.
4. Finally, we report the “judge rate” for the top-10 documents coming from steps 2 (after retrieval) and 3 (after reranking). In other words, we calculate the average percentage of the top-10 documents that have a score in the `qrels` file.

The list of reranking of models we used is the following:

* [Cohere's](https://docs.cohere.com/reference/rerank) `rerank-english-v2.0` and `rerank-english-v3.0`
* [BGE-base](https://huggingface.co/BAAI/bge-reranker-base)
* [mxbai-rerank-xsmall-v1](https://huggingface.co/mixedbread-ai/mxbai-rerank-xsmall-v1)
* [MiniLM-L-6-v2](https://huggingface.co/cross-encoder/ms-marco-MiniLM-L-6-v2)

|  | Retrieval | Reranking |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- |
| Dataset | BM25 (%) | Cohere Rerank v2 (%) | Cohere Rerank v3 (%) | BGE-base (%) | mxbai-rerank-xsmall-v1 (%) | MiniLM-L-6-v2 (%) |
| Arguana | 7.54 | 4.87 | 7.87 | 4.52 | 4.53 | 6.84 |
| Climate-FEVER | 5.75 | 6.24 | 8.15 | 9.36 | 7.79 | 7.58 |
| DBPedia | 61.18 | 60.78 | 64.15 | 63.9 | 63.5 | 67.62 |
| FEVER | 8.89 | 9.97 | 10.08 | 10.19 | 9.88 | 9.88 |
| FiQa-2018 | 7.02 | 11.02 | 10.77 | 8.43 | 9.1 | 9.44 |
| HotpotQA | 12.59 | 14.5 | 14.76 | 15.1 | 14.02 | 14.42 |
| Natural Questions | 5.94 | 8.84 | 8.71 | 8.37 | 8.14 | 8.34 |
| NFCorpus | 31.67 | 32.9 | 33.91 | 30.63 | 32.77 | 32.45 |
| Quora | 12.2 | 10.46 | 13.04 | 11.26 | 12.58 | 12.78 |
| SCIDOCS | 8.62 | 9.41 | 9.71 | 8.04 | 8.79 | 8.52 |
| Scifact | 9.07 | 9.57 | 9.77 | 9.3 | 9.1 | 9.17 |
| Touche2020 | 38.78 | 30.41 | 32.24 | 33.06 | 37.96 | 33.67 |
| TREC-COVID | 92.4 | 98.4 | 98.2 | 93.8 | 99.6 | 97.4 |
| MSMARCO | 3.97 | 6.00 | 6.03 | 6.07 | 5.47 | 6.11 |
| CQADupstack (avg.) | 5.47 | 6.32 | 6.87 | 5.89 | 6.22 | 6.16 |

**Table 2**: Judge rate per (dataset, reranker) pairs calculated on the top-10 retrieved/reranked documents

From **Table 2**, with the exception of `TREC-COVID` (>90% coverage), `DBPedia` (~65%), `Touche2020` and `nfcorpus` (~35%), we see that the majority of the datasets have a labeling rate between 5% and a little more than 10% after retrieval or reranking. This doesn’t mean that all these unmarked documents are relevant but there might be a subset of them -especially those placed in the top positions- that could be positive.

With the arrival of general purpose instruction tuned language models, we have a new powerful tool which can potentially automate judging relevance. These methods are typically far too computationally expensive to be used online for search, but here we are concerned with offline evaluation. In the following we use them to explore the evidence that some of the BEIR datasets suffer from shallow markup.

In order to further investigate this hypothesis we decided to focus on MSMARCO and select a subset of 100 queries along with the top-5 reranked (with Cohere v2) documents which are currently not marked as relevant. We followed two different paths of evaluation: First, we used a carefully tuned prompt (more on this in a later post) to prime the recently released [Phi-3-mini-4k](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct) model to predict the relevance (or not) of a document to the query. In parallel, these cases were also manually labeled in order to also assess the agreement rate between the LLM output and human judgment. Overall, we can draw the following two conclusions†\dag†:

* The agreement rate between the LLM responses and human judgments was close to 80% which seems good enough as a starting point in that direction.
* In 57.6% of the cases (based on human judgment) the returned documents were found to be actually relevant to the query. To state this in a different way: For 100 queries we have 107 documents judged to be relevant, but at least 0.576 x 5 x 100 = 288 extra documents which are actually relevant!

Here, some examples drawn from the `MSMARCO`/`dev` dataset which contain the query, the annotated positive document (from `qrels`) and a false negative document due to incomplete markup:

Example 1:

```
{
  "query":
    {
        "_id": 155234,
        "text": "do bigger tires affect gas mileage"
    },
  "positive_doc":
    {
        "_id": 502713,
        "text": "Tire Width versus Gas Mileage. Tire width is one of the only tire size factors that can influence gas mileage in a positive way. For example, a narrow tire will have less wind resistance, rolling resistance, and weight; thus increasing gas mileage.",
    },
    "negative_doc":
    {
        "_id": 7073658,
        "text": "Tire Size and Width Influences Gas Mileage. There are two things to consider when thinking about tires and their effect on gas mileage; one is wind resistance, and the other is rolling resistance. When a car is driving at higher speeds, it experiences higher wind resistance; this means lower fuel economy."
    }
}
```

Example 2:

```
{
  "query":
    {
        "_id": 300674,
        "text": "how many years did william bradford serve as governor of plymouth colony?"
    },
  "positive_doc":
    {
        "_id": 7067032,
        "text": "http://en.wikipedia.org/wiki/William_Bradford_(Plymouth_Colony_governor) William Bradford (c.1590 \u00e2\u0080\u0093 1657) was an English Separatist leader in Leiden, Holland and in Plymouth Colony was a signatory to the Mayflower Compact. He served as Plymouth Colony Governor five times covering about thirty years between 1621 and 1657."
    },
    "negative_doc":
    {
        "_id": 2495763,
        "text": "William Bradford was the governor of Plymouth Colony for 30 years. The colony was founded by people called Puritans. They were some of the first people from England to settle in what is now the United States. Bradford helped make Plymouth the first lasting colony in New England."
    }
}
```

Manually evaluating specific queries like this is a generally useful technique for understanding search quality that complements quantitive measures like nDCG@10. If you have a representative set of queries you always run when you make changes to search, it gives you important qualitative information about how performance changes, which is invisible in the statistics. For example, it gives you much more insight into the false results your search returns: it can help you spot obvious howlers in retrieved results, classes of related mistakes, such as misinterpreting domain-specific terminology, and so on.

Our result is in agreement with relevant research around `MSMARCO` evaluation. For example, [Arabzadeh et al.](https://arxiv.org/pdf/2109.00062) follow a similar procedure where they employ crowdsourced workers to make preference judgments: among other things, they show that in many cases the documents returned by the reranking modules are preferred compared to the documents in the MSMARCO `qrels` file. Another piece of evidence comes from the authors of the [RocketQA](https://arxiv.org/pdf/2010.08191) reranker who report that more than 70% of the reranked documents were found relevant after manual inspection.

†\dag† Update - September 9th: After a careful re-evaluation of the dataset we identified 15 more cases of relevant documents, increasing their total number from 273 to 288

## Main takeaways & next steps

* The pursuit for better ground truth is never-ending as it is very crucial for benchmarking and model comparison. LLMs can assist in some evaluation areas if used with caution and tuned with proper instructions
* More generally, given that benchmarks will never be perfect, it might be preferable to switch from a pure score comparison to more robust techniques capturing statistically significant differences. The work of [Arabzadeh et al.](https://arxiv.org/pdf/2109.00062) provides a nice of example of this where based on their findings they build 95% confidence intervals indicating significant (or not) differences between the various runs. In the accompanying [notebook](https://github.com/elastic/elasticsearch-labs/blob/main/supporting-blog-content/evaluating-search-relevance-part-1/retrieve-and-rerank.ipynb) we provide an implementation of confidence intervals using [bootstrapping](https://en.wikipedia.org/wiki/Bootstrapping_(statistics)).
* From the end-user perspective it’s useful to think about task alignment when reading benchmark results. For example, for an AI engineer who builds a RAG pipeline and knows that the most typical use case involves assembling multiple pieces of information from different sources, then it would be more meaningful to assess the performance of their retrieval model on multi-hop QA datasets like HotpotQA instead of the global average across the whole BEIR benchmark

In the [next blog post](https://www.elastic.co/search-labs/blog/evaluating-search-relevance-part-2) we will dive deeper into the use of Phi-3 as LLM judge and the journey of tuning it to predict relevance.

### Frequently Asked Questions

#### What is the BEIR benchmark?

BEIR is a well-structured benchmark with varied datasets across different tasks. It covers these areas: open-domain QA, passage retrieval, fact-checking, biomedical retrieval, and more. It provides a standard for evaluating search relevance.

#### What is nDCG and what is it used for?

NDCG (Normalized Discounted Cumulative Gain) is a metric that evaluates the quality of search engine rankings by measuring how well the order of results reflects their relevance.

### Related Content

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt29bbbf4463c73d8a/6a6a33fa55755baeaa2bd248/a6563ee307cc2d29722c490b043ee736c46974f3-1280x720.png)

[Jina AI](/search-labs/blog/category/jina-ai)[Relevance](/search-labs/blog/category/relevance)[ML Research](/search-labs/blog/category/ml-research)

### 56% faster, up to 50% better retrieval performance: What's inside Jina's new 600 million parameter listwise reranker

July 27, 2026|[Felix Wang](/search-labs/author/felix-wang)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltcd9291668fb96d26/6a6a33f58c87dc83b00d067e/6f40d849745ffb10d753d47d76c12b4639213c90-2382x1326.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)[Elastic Cloud Serverless](/search-labs/blog/category/elastic-cloud-serverless)

### 17% faster search, zero config: auto-calibrating vector quantization in Elasticsearch

July 28, 2026|[Tommaso Teofili](/search-labs/author/tommaso-teofili)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt097721c03648a84e/6a6a33ef0a222b4c70877f32/8f6b95800c65fe389d3e8d8281e8e8dc351f734d-992x342.png)

[ES|QL](/search-labs/blog/category/esql)[ML Research](/search-labs/blog/category/ml-research)[Agentic AI](/search-labs/blog/category/agentic-ai)

### How Elasticsearch detects multiple change points in time series with 0.99 recall

July 24, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt950edbc25d291821/6a6119f01b1d495dc56f181b/31783975126874424fc20c3c96bd95fe28d5f201-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[ML Research](/search-labs/blog/category/ml-research)

### How Elasticsearch auto-tunes vector quantization to hit your recall target

July 21, 2026|[Thomas Veasey](/search-labs/author/thomas-veasey)|[+1](#)

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/bltf58ffc7bd7f3c826/6a469777945073eeed30d267/0fa30e54796aeb49baaa760590fa6dd3ee863c2d-1280x720.png)

[Vector Database](/search-labs/blog/category/vector-database)[AI](/search-labs/blog/category/ai)[ML Research](/search-labs/blog/category/ml-research)

### Elasticsearch DiskBBQ delivers 7x faster vector search than Qdrant on network-attached storage

June 24, 2026|[Sachin Frayne](/search-labs/author/sachin-frayne)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter