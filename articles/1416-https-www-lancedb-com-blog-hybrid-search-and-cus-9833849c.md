---
title: 'https://www.lancedb.com/blog/hybrid-search-and-custom-reranking-with-lancedb-4c10a6a3447e'
company: LanceDB
tag: 排序
date: 
url: https://www.lancedb.com/blog/hybrid-search-and-custom-reranking-with-lancedb-4c10a6a3447e
account: 
origin: en-rss
---
# Hybrid Search and Custom Reranking with LanceDB

[LanceDB](/author/lancedb)

•

February 19, 2024

•

[Engineering](/category/engineering)

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-001](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

Search has historically been a complex problem in computer science. This is partly due to limitations in natural language or contextual understanding, and partly due to the absence of a universal ranking method that works well for all cases. Although the original premise still applies today, LLMs have vastly improved contextual reasoning and understanding. This allows searching for semantically similar points in a knowledge base and tests for ranking them based on a given context. Let’s see how!

Broadly, this blog covers two classes of search — *Semantic* and *keyword-based* search.

### Semantic Search

Semantic Search or vector similarity search relies on vector embedding to search for the most relevant results. The intuition behind this method is that a well-trained deep learning model, which performs all internal operations (or “sees” all data) as vector embeddings, has a good map of where a given query sits in its embedding space. Once the positionality of query embeddings is located, it finds the top-k nearest points to get the relevant search results.

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-002](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-002.avif)

The position of an embedding in vector space captures some semantics of the data. Points close to each other in vector space are considered similar (or appear in similar contexts), and points far away are deemed dissimilar. This means that semantic search works on the extracted meaning of the given docs and query and not necessarily on the keywords themselves.

### **Keyword-based Search**

This is the well-known and traditional way of searching through a knowledge base. There are varied algorithms designed for some specific cases, but the general premise of keyword-based search is that it works on the lexical attributes of the query and not its semantics. This is useful in some cases, as we’ll see next.

### Hybrid Search

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-003](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-003.avif)

Hybrid Search is a broad (often misused) term. It can mean anything from combining multiple methods for searching, to applying ranking methods to better sort the results. In this blog, we use the definition of “hybrid search” to mean using a combination of keyword-based and vector search.

## The challenge of (re)ranking search results

Once you have a group of the most relevant search results from multiple search sources, you’d likely standardize the score and rank them accordingly. This process can also be seen as another independent step — reranking.

There are two approaches for reranking search results from multiple sources.

* **Score-based**: Calculate final relevance scores based on a weighted linear combination of individual search algorithm scores. Example — Weighted linear combination of semantic search & keyword-based search results.
* **Relevance-based**: Discards the existing scores and calculates the relevance of each search result — query pair. Example — Cross Encoder models

Even though there are many strategies for reranking search results, none works for all cases. Moreover, evaluating them itself is a challenge.

## Compare search and reranking methods easily with LanceDB

Here’s some evaluation numbers from experiment comparing these re-rankers on about 800 queries. It is modified version of an evaluation script from [llama-index](https://github.com/run-llama/finetune-embedding/blob/main/evaluate.ipynb) that measures hit-rate at top-k.

### **With OpenAI ada2 embeddings**

Vector Search baseline — `0.64`

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-004](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-004.avif)

Vector Search baseline — `0.59`

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-005](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-005.avif)

With this context, let us now test hybrid search with different rerankers using LanceDB.

The dataset we’ll query is Airbnb’s financial report, which can be found [here](https://d18rn0p25nwr6d.cloudfront.net/CIK-0001559720/8a9ebed0-815a-469a-87eb-1767d21d8cec.pdf). It’s inspired by GitHub user virattt’s [GitHub gist](https://gist.github.com/virattt/9f41b2cd1e8f65e672127999ad443f15) comparing speeds of reranker models. The Colab to reproduce the results below can be found [here](https://colab.research.google.com/github/lancedb/lancedb/blob/main/docs/src/notebooks/hybrid_search.ipynb).

## Ingestion

We’ll start by ingesting the entire dataset by recursively splitting the text into smaller chunks and embedding it using the OpenAI embedding model.

Using LangChain makes this a single line process. Here’s how your LanceDB table would look.

```
table = ...
LanceDB.from_documents(docs, embedding_function, connection=table)
table.to_pandas().head()
```

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-006](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-006.avif)

In the original example, tvectorDB is queried to retrieve the specific reasons as to why Airbnb’s operating costs were high for that year.

```
query = "What are the specific factors contributing to Airbnb's increased operational expenses in the last fiscal year?"
```

## Semantic Search

Let’s first take a look at the semantic search results:

```
vector_query = embedding_function.embed_query(query)
docs = table.search(vector_query).limit(5).to_pandas()

    In addition, the number of listings on Airbnb may decline as a result of a number of other factors affecting Hosts, including: the COVID-19 pandemic; enforcement or threatened
    enforcement of laws and regulations, including short-term occupancy and tax laws; private groups, such as homeowners, landlords, and condominium and neighborhood
    associations, adopting and enforcing contracts that prohibit or restrict home sharing; leases, mortgages, and other agreements, or regulations that purport to ban or otherwise restrict
    home sharing; Hosts opting for long-term rentals on other third-party platforms as an alternative to listing on our platform; economic, social, and political factors; perceptions of trust
    and safety on and off our platform; negative experiences with guests, including guests who damage Host property, throw unauthorized parties, or engage in violent and unlawful

    Made Possible by Hosts, Strangers, AirCover, Categories, and OMG marketing campaigns and launches, a $67.9 million increase in our search engine marketing and advertising
    spend, a $25.1 million increase in payroll-related expenses due to growth in headcount and increase in compensation costs, a $22.0 million increase in third-party service provider
    expenses, and a $11.1 million increase in coupon expense in line with increase in revenue and launch of AirCover for guests, partially offset by a decrease of $22.9 million related to
    the changes in the fair value of contingent consideration related to a 2019 acquisition.
    General and Administrative
    2021 2022 % Change
    (in millions, except percentages)
    General and administrative $ 836 $ 950 14 %
    Percentage of revenue 14 % 11 %
    General and administrative expense increased $114.0 million, or 14%, in 2022 compared to 2021, primarily due to an increase in other business and operational taxes of $41.3

    Our success depends significantly on existing guests continuing to book and attracting new guests to book on our platform. Our ability to attract and retain guests could be materially
    adversely affected by a number of factors discussed elsewhere in these “Risk Factors,” including:
    ...

    Table of Contents
    Airbnb, Inc.
    Consolidated Statements of Operations
    (in millions, except per share amounts)
    Year Ended December 31,
    2020 2021 2022
    Revenue $ 3,378 $ 5,992 $ 8,399
    Costs and expenses:
    Cost of revenue 876 1,156 1,499
    ...
```

The latency is very reasonable as can be seen below:

> 2.62 ms ± 107 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

These are pretty relevant results in the context of “operational expenses,” but this can further be improved by reranking the top few results returned. Results 2 and 3 are more relevant as “specific factors that increase operational expense” , and should potentially appear on top.

Let us now compare this with hybrid search and reranking applied.

## **Hybrid Search**

In LanceDB, you can easily run a hybrid search by passing the search string and simply setting the `query_type="hybrid"` keyword argument. The string query is automatically vectorized if you’ve passed the `EmbeddingFunction`.

```
docs = table.search(query, query_type="hybrid").to_pandas()
```

> 71 ms ± 25.4 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

The results are shown below:

```
    “Initial Delivery Date”); provided that the Pricing Certificate for any fiscal year may be delivered on any date following the Initial Delivery
    Date that is prior to the date that is 365 days following the last day of the preceding fiscal year, so long as such Pricing Certificate includes a
    certification that delivery of such Pricing Certificate on or before the Initial Delivery Date was not possible because (i) the information
    required to calculate the KPI Metrics for such preceding fiscal year was not available at such time or (ii) the report of the KPI Metrics Auditor,
    if relevant, was not available at such time (the date of the Administrative Agent’s receipt thereof, each a “Pricing Certificate Date”). Upon
    delivery of a Pricing Certificate in respect of a fiscal year, (i) the Applicable Rate for the Loans incurred by the Borrower shall be increased or
    decreased (or neither increased nor decreased), as applicable, pursuant to the Sustainability Margin Adjustment as set forth in the KPI Metrics

    In addition, the number of listings on Airbnb may decline as a result of a number of other factors affecting Hosts, including: the COVID-19 pandemic; enforcement or threatened
    enforcement of laws and regulations, including short-term occupancy and tax laws; private groups, such as homeowners, landlords, and condominium and neighborhood
    associations, adopting and enforcing contracts that prohibit or restrict home sharing; leases, mortgages, and other agreements, or regulations that purport to ban or otherwise restrict
    home sharing; Hosts opting for long-term rentals on other third-party platforms as an alternative to listing on our platform; economic, social, and political factors; perceptions of trust
    and safety on and off our platform; negative experiences with guests, including guests who damage Host property, throw unauthorized parties, or engage in violent and unlawful

    (a) The Borrower may, at its election, deliver a Pricing Certificate to the Administrative Agent in respect of the most recently
    ended fiscal year, commencing with the fiscal year ended December 31, 2022, on any date prior to the date that is 270 days following the last
    day of such fiscal year (the
    -50-

    Made Possible by Hosts, Strangers, AirCover, Categories, and OMG marketing campaigns and launches, a $67.9 million increase in our search engine marketing and advertising
    spend, a $25.1 million increase in payroll-related expenses due to growth in headcount and increase in compensation costs, a $22.0 million increase in third-party service provider
    expenses, and a $11.1 million increase in coupon expense in line with increase in revenue and launch of AirCover for guests, partially offset by a decrease of $22.9 million related to
    ...

    Our success depends significantly on existing guests continuing to book and attracting new guests to book on our platform. Our ability to attract and retain guests could be materially
    adversely affected by a number of factors discussed elsewhere in these “Risk Factors,” including:
    •events beyond our control such as the ongoing COVID-19 pandemic, other pandemics and health concerns, restrictions on travel, immigration, trade disputes, economic
    ...
```

When you don’t specify any reranker, LanceDB uses the `LinearCombinationReranker` by default. This takes a weighted linear combination of the vector and full-text (keyword-based) search scores to produce the final relevance score.

## **LinearCombinationReranker**

By default, this method assigns a vector search score a weighting factor of `0.7` and full-text or FTS search score a weight of `0.3`.

```
from lancedb.rerankers import LinearCombinationReranker

reranker = LinearCombinationReranker(weight=0.9)

docs = table.search(query, query_type="hybrid").rerank(reranker=reranker).to_pandas()
```

This method faster than other model-based rerankers, as no model inference or API requests are made during the reranking operation.

## **CohereReranker**

This uses Cohere’s [Rerank API](https://docs.cohere.com/docs/rerank-overview) to rerank the results. It accepts the reranking model name as a parameter. By default, it uses the `english-v3` model, but you can easily switch to a multi-lingual model if your data isn’t just in English.

```
from lancedb.rerankers import CohereReranker

reranker = CohereReranker()  # or CohereReranker(model_name="")
docs = table.search(query, query_type="hybrid").rerank(reranker=reranker).to_pandas()
```

> 605 ms ± 78.1 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

**Results**: (Only showing first three lines of each doc for brevity)

```
    Increased operating expenses, decreased revenue, negative publicity, negative reaction from our Hosts and guests and other stakeholders, or other adverse impacts from any of the
    above factors or other risks related to our international operations could materially adversely affect our brand, reputation, business, results of operations, and financial condition.
    In addition, we will continue to incur significant expenses to operate our outbound business in China, and we may never achieve profitability in that market. These factors, combined
    with sentiment of the workforce in China, and China’s policy towards foreign direct investment may particularly impact our operations in China. In addition, we need to ensure that
    our business practices in China are compliant with local laws and regulations, which may be interpreted and enforced in ways that are different from our interpretation, and/or create

    Made Possible by Hosts, Strangers, AirCover, Categories, and OMG marketing campaigns and launches, a $67.9 million increase in our search engine marketing and advertising
    spend, a $25.1 million increase in payroll-related expenses due to growth in headcount and increase in compensation costs, a $22.0 million increase in third-party service provider
    expenses, and a $11.1 million increase in coupon expense in line with increase in revenue and launch of AirCover for guests, partially offset by a decrease of $22.9 million related to
    ...

    Table of Contents
    Airbnb, Inc.
    Consolidated Statements of Operations
    (in millions, except per share amounts)
    ...

    Our success depends significantly on existing guests continuing to book and attracting new guests to book on our platform. Our ability to attract and retain guests could be materially
    adversely affected by a number of factors discussed elsewhere in these “Risk Factors,” including:
    •events beyond our control such as the ongoing COVID-19 pandemic, other pandemics and health concerns, restrictions on travel, immigration, trade disputes, economic
    ...

    In addition, the number of listings on Airbnb may decline as a result of a number of other factors affecting Hosts, including: the COVID-19 pandemic; enforcement or threatened
    enforcement of laws and regulations, including short-term occupancy and tax laws; private groups, such as homeowners, landlords, and condominium and neighborhood
    associations, adopting and enforcing contracts that prohibit or restrict home sharing; leases, mortgages, and other agreements, or regulations that purport to ban or otherwise restrict
    ...
```

Cohere Reranker better ranks the results as it is powered by a model designed for this task, i.e., calculating the relevance of given documents in relation to the given query. This is different from the linear combination as it relies only on the existing scores of individual search algorithms (vector search and FTS). Here are the relevance scores given to each of these docs by the cohere reranker. It is evident that the first two docs are highly relevant.

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-007](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-007.avif)

## ColBERT Reranker

The ColBERT model powers Colbert Reranker. It uses the [Hugging Face implementation](https://huggingface.co/vjeronymo2/mColBERT) locally.

```
from lancedb.rerankers import ColbertReranker

reranker = ColbertReranker()
docs = table.search(query, query_type="hybrid").rerank(reranker=reranker).to_pandas()["text"].to_list()
```

> 950 ms ± 5.78 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

The results are below.

```
    Made Possible by Hosts, Strangers, AirCover, Categories, and OMG marketing campaigns and launches, a $67.9 million increase in our search engine marketing and advertising
    spend, a $25.1 million increase in payroll-related expenses due to growth in headcount and increase in compensation costs, a $22.0 million increase in third-party service provider
    expenses, and a $11.1 million increase in coupon expense in line with increase in revenue and launch of AirCover for guests, partially offset by a decrease of $22.9 million related to
    ...

    Our future revenue growth depends on the growth of supply and demand for listings on our platform, and our business is affected by general economic and business conditions
    worldwide as well as trends in the global travel and hospitality industries and the short and long-term accommodation regulatory landscape. In addition, we believe that our revenue
    growth depends upon a number of factors, including:
    ...

    Our success depends significantly on existing guests continuing to book and attracting new guests to book on our platform. Our ability to attract and retain guests could be materially
    adversely affected by a number of factors discussed elsewhere in these “Risk Factors,” including:
    •events beyond our control such as the ongoing COVID-19 pandemic, other pandemics and health concerns, restrictions on travel, immigration, trade disputes, economic
    ...

    In addition, the number of listings on Airbnb may decline as a result of a number of other factors affecting Hosts, including: the COVID-19 pandemic; enforcement or threatened
    enforcement of laws and regulations, including short-term occupancy and tax laws; private groups, such as homeowners, landlords, and condominium and neighborhood
    associations, adopting and enforcing contracts that prohibit or restrict home sharing; leases, mortgages, and other agreements, or regulations that purport to ban or otherwise restrict
    ...

    Table of Contents
    Airbnb, Inc.
    Consolidated Statements of Operations
    ...
```

Colbert is similar to the Cohere reranker in that it doesn’t use the existing scores from vector and full-text searches. The results are similar to Cohere’s, except for the top 1 result.

LanceDB also supports other rerankers, including an experimental prompt-based [OpenAI reranker](https://github.com/lancedb/lancedb/blob/main/python/python/lancedb/rerankers/openai.py), a Cross-encoder reranker, and others. Most of the results @ Top5 were found to be similar the ones shown above.

Subjectively, Cohere had a slight edge in getting the most relevant result (top 1), which the others missed, and considering it also included a network roundtrip, so the speed of 600ms is pretty impressive, too. This is also consistent with the evaluation results.

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-008](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-008.avif)

**Note**: Cohere is an API-based reranker, and the speed is subject to internet connection quality

## Bring your own reranker

Recognizing that ranking is a complex problem with varying requirements for every use case, hybrid Search in LanceDB is designed to be **very** flexible. You can easily plug in your own reranking logic. To do so, you can implement the base `Reranker` class as follows:

```
from lancedb.rerankers import Reranker

class MyCustomReranker(Reranker):
    def rerank_hybrid(self, query: str, vector_results: pa.Table, fts_results: pa.Table) -> pa.Table:
        combined_results = self.merge(vector_results, fts_results)  # Or custom merge algo
        # Custom Reranking logic here

        return combined_results

reranker = MyCustomReranker()
table.search((vector_query, query)).rerank(reranker=reranker).to_pandas()
```

We’ve shown how you can apply reranking to significantly improve your retrieval quality with relatively small additions to your code base (by only adding a small additional latency). For RAG applications, better retrieval can significantly improve downstream generation, so it’s worth spending some time trying out this feature on your existing LanceDB workflows. We’d love to hear back from the community wwhat you build with this exciting feature!

To learn more about LanceDB, hybrid search, or available rerankers, visit our [documentation page](https://docs.lancedb.com/search/hybrid-search) and chat with us on [Discord](https://discord.com/invite/zMM32dvNtd) about your use cases!

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-009](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-009.jpg)

[LanceDB](/author/lancedb)

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-010](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-010.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-011](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-011.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c-fig-012](../images/1416-https-www-lancedb-com-blog-hybrid-search-and-cus-9833849c/figure-012.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb