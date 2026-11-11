---
title: 'https://blog.vespa.ai/onnx-external-data-in-vespa-embedders/'
company: Vespa
tag: 搜索
date: 
url: https://blog.vespa.ai/onnx-external-data-in-vespa-embedders/
account: 
origin: en-rss
---
{
}

[Subscribe](https://vespa.ai/subscribe/)

# Vespa Blog

We Make AI Work

Share

![Bjørn C Seime](/assets/avatars/bjorncs.jpg)

[Bjørn C Seime](/authors/bjorncs/ "Bjørn C Seime")
  
Sr Principal Software Engineer

![Thomas H. Thoresen](/assets/avatars/thomas.jpg)

[Thomas H. Thoresen](/authors/thomas/ "Thomas H. Thoresen")
  
Principal Software Engineer

27 Mar 2026

# Using Large ONNX Models with External Data in Vespa Embedders

![Using Large ONNX Models with External Data in Vespa Embedders](/assets/2026-03-27-onnx-external-data-in-vespa-embedders/onnx-external-data-splash.png)

Many popular ONNX models exceed the 2 GB [protobuf](https://protobuf.dev/) format limit and store their weights in separate external data files.
Until recently, these models could not be used directly in Vespa’s built-in embedders.

This was a long requested feature on our tracker (see [GitHub issue #28761](https://github.com/vespa-engine/vespa/issues/28761)).

## The 2 GB limitation

[ONNX](https://onnx.ai/) uses Google’s Protocol Buffers as its serialization format.
Protobuf has a hard limit of 2 GB on message size.
For smaller models, this is not a problem — all tensor data (the model weights) is embedded directly in the `.onnx` file,
making it self-contained.

As models grow larger, they inevitably hit this limitation.
For a model exceeding 2 GB, ONNX tooling splits it into two parts:

* A small **`.onnx` file** containing the model graph structure (typically a few hundred KB to a few MB).
* One or more **external data files** (commonly named `.onnx_data`) containing the actual tensor weights.

Note that reduced-precision variants of these models (INT8, FP16, etc.) are often small enough to fit in a single self-contained `.onnx` file.
The external data split primarily affects the full-precision versions.

Previously, if you pointed a Vespa embedder at a model with external data files, ONNX Runtime would fail to load it
because the data files were not available alongside the model file.

## What changed

Vespa embedders now automatically handle ONNX models with external data files.
When you configure an embedder with a URL pointing to an `.onnx` file,
Vespa inspects the model to check whether it references any external data files.
If it does, Vespa downloads those files automatically before loading the model.

This feature is available starting from Vespa 8.544.

## How to use it

Here is an example using EmbeddingGemma 300M, which uses external data:

```
<container id="default" version="1.0">
  <component id="gemma" type="hugging-face-embedder">
    <transformer-model
      url="https://huggingface.co/onnx-community/embeddinggemma-300m-ONNX/resolve/main/onnx/model.onnx"/>
    <tokenizer-model
      url="https://huggingface.co/onnx-community/embeddinggemma-300m-ONNX/resolve/main/tokenizer.json"/>
    <max-tokens>2048</max-tokens>
    <prepend>
      <query>task: search result | query: </query>
      <document>title: none | text: </document>
    </prepend>
  </component>
</container>
```

If you are deploying to [Vespa Cloud](https://cloud.vespa.ai/), you can also use models from the
[Vespa Model Hub](https://docs.vespa.ai/en/rag/model-hub.html) that use external data.
For example, the Multilingual-E5-large model (will be available on Vespa Cloud 8.668+):

```
<container id="default" version="1.0">
  <component id="e5" type="hugging-face-embedder">
    <transformer-model model-id="multilingual-e5-large"/>
    <max-tokens>512</max-tokens>
    <prepend>
      <query>query: </query>
      <document>passage: </document>
    </prepend>
  </component>
</container>
```

This works with our ONNX-based embedders:

* [`hugging-face-embedder`](https://docs.vespa.ai/en/embedding.html#huggingface-embedder)
* [`colbert-embedder`](https://docs.vespa.ai/en/embedding.html#colbert-embedder)
* [`splade-embedder`](https://docs.vespa.ai/en/embedding.html#splade-embedder)

It’s also possible to use [private models](https://docs.vespa.ai/en/reference/rag/embedding.html#private-model-hub) — authentication tokens are propagated when downloading external data files.

## Current limitations

There are a few constraints to be aware of:

* **Embedders only.** Models used directly in [ranking expressions](https://docs.vespa.ai/en/ranking/onnx.html)
  must still be self-contained and under 2 GB.
* **URL-referenced or Model Hub models only.** Models bundled in the
  [application package](https://docs.vespa.ai/en/application-packages.html)
  using the `path` attribute do not support external data.
  Models referenced via `url` or `model-id` (Vespa Cloud) are supported.
* **External data files must be co-located with the model.**
  The external data files are resolved relative to the model URL.
  They must be in the same directory (or a subdirectory) as the `.onnx` file.

See the [ONNX model documentation](https://docs.vespa.ai/en/ranking/onnx.html#limitations-on-model-size-and-complexity)
for the full list of requirements.

If you need more extensive support for ONNX models with external data — for example in ranking expressions —
feel free to [file an issue](https://github.com/vespa-engine/vespa/issues).

## Read more

[![](/assets/logo/vespa-logo.svg)

## Ranking with ONNX Models

#### Full reference for using ONNX models in Vespa](https://docs.vespa.ai/en/ranking/onnx.html )

[![](/assets/logo/vespa-logo.svg)

## Embedding in Vespa

#### Guide to configuring embedding models in Vespa](https://docs.vespa.ai/en/embedding.html )

* [#embedding](/tags#embedding)
* [#onnx](/tags#onnx)

[« Asymmetric Retrieval: Spend on Docs, Embed your Queries for Free](/asymmetric-retrieval-spend-on-docs-queries-for-free/)
[The Vespa Cloud Metrics Dashboard »](/the-vespa-cloud-metrics-dashboard/)

![Vespa Blog](/assets/logo/vespa-logo.svg)   Never miss a **story** from us, subscribe to our newsletter
[Subscribe](https://vespa.ai/subscribe/)