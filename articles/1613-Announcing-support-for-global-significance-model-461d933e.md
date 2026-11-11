---
title: 'Announcing support for global significance models'
company: Vespa
tag: 排序
date: 2024-10-18
url: https://blog.vespa.ai/global-significance/
account: 
origin: harvest3-202607
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Gleb Sizov](/assets/avatars/gleb.jpg)

[Gleb Sizov](/authors/gleb/ "Gleb Sizov")
  
Principal Software Engineer

![Geir Storli](/assets/avatars/geirst.jpg)

[Geir Storli](/authors/geirst/ "Geir Storli")
  
Senior Principal Vespa Engineer

18 Oct 2024

# Announcing support for global significance models

We are excited to announce support for [global significance models](https://docs.vespa.ai/en/significance.html#global-significance-model) in Vespa.
This feature improves ranking for [streaming mode](https://docs.vespa.ai/en/streaming-search.html) and ensures deterministic results in multi-node deployments using indexed mode.

*Significance* measures how rare a term is in a collection of documents.
Rare terms, like “neurotransmitter”, are weighted higher in ranking than common terms, such as “body”.
Significance is used in [bm25](https://docs.vespa.ai/en/reference/bm25.html) and [nativeRank](https://docs.vespa.ai/en/reference/nativerank.html) ranking functions.

By default, Vespa calculates significance values locally on each content node, based on the documents stored on that node.
This makes ranking non-deterministic as the same query may be [processed by different node groups](https://docs.vespa.ai/en/elasticity.html#grouped-distribution) or when [documents are redistributed](https://docs.vespa.ai/en/elasticity.html) due to scaling or failure recovery.
In addition, local significance is not supported in [streaming search](https://docs.vespa.ai/en/streaming-search.html).

To address these scenarios, we introduce support for global significance models that share significance values across all content nodes, which also works in [streaming search](https://docs.vespa.ai/en/streaming-search.html).

## Example

Global significance models are specified in the [`significance` element in services.xml](https://docs.vespa.ai/en/reference/services-search.html#significance):

```
<container version="1.0">
    <search>
        <significance>
            <model model-id="significance-en-wikipedia-v1"/>
            <model url="https://some/uri/mymodel.multilingual.json" />
            <model path="models/mymodel.en.json.zst" />
        </significance>
    </search>
</container>
```

Vespa Cloud users have access to [pre-built models](https://cloud.vespa.ai/en/model-hub#significance-models), identified by `model-id`.
In addition, all users can specify their own models by providing a `url` to an external resource or a `path` to a model file within the application package.
Vespa provides a [command line tool](https://docs.vespa.ai/en/operations-selfhosted/vespa-cmdline-tools.html#vespa-significance) to generate [model files](https://docs.vespa.ai/en/significance.html#significance-model-file) from documents.
The order in which the models are specified determines the model precedence, see [model resolution](https://docs.vespa.ai/en/significance.html#model-resolution) for details.

The `significance` feature must be also enabled in the [`rank-profile` section of the schema](https://docs.vespa.ai/en/reference/schema-reference.html#significance):

```
schema example {
    document example {
        field content type string {
            indexing: index | summary
            index: enable-bm25
        }
    }

    rank-profile default {
        significance {
            use-model: true
        }
    }
}
```

## Experiments

We have conducted experiments to evaluate how a global significance model influences ranking quality, both in indexing and streaming search scenarios.

Three publicly available information retrieval datasets were used in these experiments:

1. [NFCorpus](https://www.cl.uni-heidelberg.de/statnlpgroup/nfcorpus/) - document retrieval dataset, medical domain, 3.6K docs and 323 test queries.
2. [TREC-COVID](https://ir.nist.gov/trec-covid/) - document retrieval dataset, about COVID-19, 171K docs and 50 test queries.
3. [MS MARCO](https://microsoft.github.io/msmarco/) - passage retrieval dataset, not domain specific, with ca. 8.8M docs and 7K test queries.

The global significance model was generated from English Wikipedia, which includes approximately 4.4 million articles.
We compared this model to the default local model in Vespa.
Our ranking expression is the sum of [BM25](https://docs.vespa.ai/en/reference/bm25.html) scores applied to a title and text fields.

The experiments were executed locally in a docker container with one content node.
When running on one content node the local model is generated from all documents fed to Vespa without non-determinism due to document distribution. This corresponds to a global model generated from all documents within the collection, which is ideal for large collections.
However, for streaming search, there is no local model and significance is set to a constant value.

The results are presented in the table below showing [Normalized Discounted Cumulative Gain at 10 (NDCG@10)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) for different datasets and scenarios (indexing and streaming):

![](../assets/2024-10-18-global-significance/results.png)

For the table we can see that the global model **substantially improves streaming search**.
With indexing, a slight decrease in ranking scores is observed, especially in a larger, general domain dataset like MARCO.
This can be mitigated by [generating a model from the documents themselves](https://docs.vespa.ai/en/operations-selfhosted/vespa-cmdline-tools.html#vespa-significance), rather than relying on one built from external data.

It is worth noting that the global model incurs no performance cost for indexing and querying.

## Summary

Global significance improves streaming search and provides deterministic search results in multi-node deployments.
For small document collections (less than 10k documents), models generated from large external data (e.g. Wikipedia) provide good results.
For larger collections, a model generated from the documents within the collection is recommended.
See the [significance model documentation page](https://docs.vespa.ai/en/significance.html#global-significance-model) for details.
The feature is available in Vespa as of version 8.426.8.

Got questions? Join the Vespa community in [Vespa Slack](https://slack.vespa.ai/).

## Read more

[![Visual RAG over PDFs with Vespa - A demo application in Python](/assets/2024-11-19-visual-rag-in-practice/colpali_child.png)](/visual-rag-in-practice/)
[## Visual RAG over PDFs with Vespa - A demo application in Python

#### This is a technical blog post on developing an end-to-end Visual RAG application powered by Vespa. It has link to a live demo application, and will walk you through why...](/visual-rag-in-practice/)

[![](/assets/logo/vespa-logo.svg)

## Join our Slack

#### Got questions? Join the Vespa community in Vespa Slack](https://vespatalk.slack.com/ssb/redirect )

[![](/assets/logo/vespa-logo.svg)

## Free Trial

#### Deploy your application for free. Get started now to get $300 in free credits. No credit card required!](https://vespa.ai/free-trial/ )

[« Vinted moves from Elasticsearch to Vespa](/vinted-moves-from-elasticsearch-to-vespa/)
[Deploying RAG at Scale: Key Questions for Vendors »](/deploying-rag-at-scale/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)