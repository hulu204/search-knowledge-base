---
title: 'https://www.lancedb.com/blog/accelerate-vector-search-applications-using-openvino-lancedb'
company: LanceDB
tag: 搜索
date: 
url: https://www.lancedb.com/blog/accelerate-vector-search-applications-using-openvino-lancedb
account: 
origin: en-rss
---
# Accelerate Vector Search Applications Using OpenVINO & LanceDB

[LanceDB](/author/lancedb)

•

December 6, 2023

•

[Engineering](/category/engineering)

![1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c-fig-001](../images/1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c/figure-001.avif)

Table of Contents

[This is a title](#)

[This is a subtitle](#)

In this article, we'll show how to use the CLIP model from OpenAI for Text-to-Image and Image-to-Image searching. We'll also do a comparative analysis of the PyTorch model, FP16 OpenVINO format, and INT8 OpenVINO format in terms of speedup.

Here's a summary of what's covered:

1. ***Using the PyTorch model***
2. ***Using OpenVINO conversion to speed up by 70%***
3. ***Using Quantization with OpenVINO NNCF to speed up by 400%***

All results reported below are from a *13th Gen Intel® Core™ i5–13420H*\* using OpenVINO=2023.2 and NNCF=2.7.0 version.

If you'd like to code along, here's a [Colab notebook](https://colab.research.google.com/github/lancedb/vectordb-recipes/blob/main/examples/Accelerate-Vector-Search-Applications-Using-OpenVINO/clip_text_image_search.ipynb) with all the code you need to get started!

## CLIP from OpenAI

***CLIP (Contrastive Language–Image Pre-training) is a neural network capable of processing both images and text.***

CLIP is a multimodal model, which means it can process both text and images. This capability allows it to embed different types of inputs in a shared multimodal space, where the positions of images and text have semantic meaning, regardless of their format.

The following image presents a visualization of the pre-training procedure.

![1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c-fig-002](../images/1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c/figure-002.png)

## OpenVINO by Intel

OpenVINO toolkit is a free toolkit facilitating the optimization of a deep learning model from a framework and deploying an inference engine onto Intel hardware. We'll use the FP16 and INT8 formats using the OpenVINO CLIP model.  
This post demonstrates how to use OpenVINO to accelerate an embedding pipeline in LanceDB.

## Implementation

In the implementation section, we see the comparative implementation of the CLIP model from Hugging Face and OpenVINO formats, using the conceptual caption dataset.  
We start with the first step of loading the conceptual caption dataset from Hugging Face.

We will select a sample of 100 images from this large number of images

Helper ***functions to validate image URLs*** and get images and captions from image URL

Now we have prepared the dataset and we are ready to start with CLIP using Hugging Face and OpenVINO and their performance comparative analysis in terms of speed.

### PyTorch CLIP using Hugging Face

We'll start with CLIP using Hugging Face and report the time taken to extract embeddings and search using LanceDB.

Let's write a helper function to extract text and image embeddings:

### Use LanceDB for storing the embeddings & search

`‍`Extracting Embeddings of 83 images using CLIP Hugging faces model and time taken to extract embeddings.

This pipeline to extract embeddings of 83 images took **55.79 sec**.

### Data ingestion and creating embeddings in LanceDB

Next, we show how to create the embeddings and ingest them into LanceDB.

### Query the embeddings

You can easily query the embeddings via similarity in LanceDB as follows:

## CLIP model using FP16 OpenVINO format

Next, we'll show the results from the same pipeline with the CLIP F16 OpenVINO format.

Compiling the CLIP OpenVINO model

Extracting the embeddings of 83 images using CLIP FP16 OpenVINO model now takes **31.79** seconds – this is a 43% reduction!

The embeddings can be ingested to LanceDB the same as before:

We query the embeddings and run search just like before:

## NNCF INT 8-bit Quantization

You can also use 8-bit Post Training Optimization from NNCF (Neural Network Compression Framework) and run inference on the quantized model via OpenVINO Toolkit.

Here's a helper function to convert into `Int8` format using NNCF:

### Initializing NNCF and Saving the Quantized Model

### Compiling the INT8 model and Helper function for extracting features

With the updated pipeline using CLIP OpenVINO format, the time taken to extract embeddings of 83 images is brought down to just 13.70 sec! That's a 75.4% reduction from  
the original CLIP model!

We can ingest the embeddings into LanceDB as follows:

We've now shown the performance improvement using all the CLIP model formats PyTorch from Hugging Face, FP16 OpenVINO, and INT8 OpenVINO.

## Conclusions

All these results are on CPU for comparison of the PyTorch model with the OpenVINO model formats(FP16/ INT8)

| Format | Time (s) |
| --- | --- |
| PyTorch model from Hugging Face | 55.26 |
| OpenVINO FP16 format | 31.79 |
| OpenVINO INT8 format | 13.70 |

The performance acceleration achieved with an **`FP16`** model is **1.73** times the PyTorch model, which is a relatively modest (yet decent) increase in speed. However, when switching to the **`INT8`** OpenVINO format, there is a **4.03** times increase in speed compared to the PyTorch model.

Visit the LanceDB [**GitHub**](https://github.com/lancedb) to learn more about how to work with vector search at scale, and for more such tutorials and demo applications, visit the [**vectordb-recipes**](https://github.com/lancedb/vectordb-recipes/tree/main) repo. For the latest updates from LanceDB, follow our [**LinkedIn**](https://www.linkedin.com/company/lancedb/) and [**X**](https://twitter.com/lancedb) pages.

![1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c-fig-003](../images/1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c/figure-003.jpg)

[LanceDB](/author/lancedb)

![1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c-fig-004](../images/1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c/figure-004.png)

### How ByteDance’s Volcano Engine Rebuilt Its AI Stack on Lance, From Data Lake to Agent Memory at 100K+ QPS

Bytedance

•

July 13, 2026

volcano-engine-lance-agent-memory

![1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c-fig-005](../images/1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c/figure-005.png)

### Rebuilding the Data Foundation for Embodied AI with Lance: From Long Videos to Random-Access-Friendly Multimodal Samples

China Merchants Lion Rock AI Lab

•

July 9, 2026

china-merchants-lancedb-story

![1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c-fig-006](../images/1446-https-www-lancedb-com-blog-accelerate-vector-sea-5d6abd6c/figure-006.png)

### Make Handwritten Notes Searchable: Optimizing an OCR Pipeline with LanceDB

Prashanth Rao

•

July 10, 2026

make-handwritten-notes-searchable-optimizing-an-ocr-pipeline-with-lancedb