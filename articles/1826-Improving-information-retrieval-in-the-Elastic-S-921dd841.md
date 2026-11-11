---
title: 'Improving information retrieval in the Elastic Stack: Improved inference performance with ELSER v2'
company: Elastic
tag: 工程相关
date: 2023-10-17
url: https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-1
account: 
origin: harvest3-202607
---
[Blog](/search-labs/blog)

# Improving information retrieval in the Elastic Stack: Improved inference performance with ELSER v2

Learn about the improvements we've made to the inference performance of ELSER v2, achieving a 60% to 120% speed increase over ELSER v1.

October 17, 2023

[Thomas Veasey](/search-labs/author/thomas-veasey)[Quentin Herreros](/search-labs/author/quentin-herreros)[Valeriy Khakhutskyy](/search-labs/author/valeriy-khakhutskyy)

[ML Research](/search-labs/blog/category/ml-research)

Jump to

Share

It is well known that modern transformer based approaches to information retrieval often come with significantly higher resource costs when compared with traditional statistical approaches, such as BM25. This can make it challenging to apply these techniques in production. At large scale, at least as much attention needs to be paid to the resource usage of any retrieval solution as to its relevance in order to produce something practically useful.

In this final two part blog of our series, we discuss some of the work we did for retrieval and inference performance for the release of version 2 of our Elastic Learned Sparse EncodeR model (ELSER), which we introduced in [this](https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance) previous blog post. In 8.11 we are releasing two versions of the model: one portable version which will run on any hardware and one version which is optimized for the x86 family of architectures. We're still making the deployment process easy though, by defaulting to the most appropriate model for your cluster's hardware.

In this first part we focus on inference performance. In the [second part](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-2) we discuss the ongoing work we're doing to improve retrieval performance. However, first we briefly review the relevance we achieve for BEIR with ELSER v2.

## Improved relevance for BEIR with ELSER v2

For this release we extended our training data, including around 390k high quality question and answer pairs to our fine tune dataset, and improved the FLOPS regularizer based on insights we discussed in the [past](https://www.elastic.co/search-labs/may-2023-launch-information-retrieval-elasticsearch-ai-model). Together these changes gave us a bump in relevance measured with our usual set of BEIR benchmark datasets.

We plan to follow up with a full description of our training data set composition and the innovations we have introduced, such as improvements to [cross-encoder distillation](https://www.elastic.co/search-labs/may-2023-launch-information-retrieval-elasticsearch-ai-model) and the FLOPS regularizer at a later date. Since this blog post mainly focuses on performance considerations, we simply give the new NDCG@10 for ELSER v2 model in the table below.

![ELSER v2 relevance](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt3b3ec48ee7e69a9a/6a17d852148009492eb485d2/356fc70da41148b7aa784e3eb99c5c282b425289-1440x220.png)

NDCG@10 for BEIR data sets for ELSER v1 and v2 (higher is better). The v2 results use the query pruning method described below

## Quantization in ELSER v2

Model inference in the Elastic Stack is run on CPUs. There are two principal factors which affect the latency of transformer model inference: the memory bandwidth needed to load the model weights and the number of arithmetic operations it needs to perform.

ELSER v2 was trained from a BERT base checkpoint. This has just over 100M parameters, which amounts to about 418 MB of storage for the weights using 32 bit floating point precision. For production workloads for our cloud deployments we run inference on Intel Cascade Lake processors. A typical midsize machine would have L1 data, L2 and L3 cache sizes of around 64 KiB, 2 MiB and 33 MiB, respectively. This is clearly much smaller than model weight storage (although the number of weights which are actually used for any given inference is a function of text length). So for a single inference call we get cache misses all the way up to RAM. Halving the weight memory means we halve the memory bandwidth we need to serve an inference call.

Modern processors support wide registers which let one perform the same arithmetic operations in parallel on several pieces of data, so called SIMD instructions. The number of parallel operations one can perform is a function of the size of each piece of data. For example, Intel processors allow one to perform 8 bit integer multiplication in 16 bit wide lanes. This means one gets roughly twice as many operations per cycle for int8 versus float32 multiplication and this is the dominant compute cost in an inference call.

It is therefore clear if one were able to perform inference using int8 tensors there are significant performance improvements available. The process of achieving this is called quantization. The basic idea is very simple: clip outliers, scale the resulting numbers into the range 0 to 255 and snap them to the nearest integer. Formally, a floating point number xxx is transformed using ⌊255u−l(clamp(x,l,u)−l)⌉\left\lfloor\frac{255}{u - l}(\text{clamp}(x, l, u) - l)\right\rceil⌊u−l255​(clamp(x,l,u)−l)⌉. One might imagine that the accuracy lost in this process would significantly reduce the model accuracy. In practice, large transformer model accuracy is fairly resilient to the errors this process introduces.

There is quite a lot of prior art on model quantization. We do not plan to survey the topic in this blog and will focus instead on the approaches we actually used. For background and insights into quantization we recommend [these](https://arxiv.org/pdf/2004.09602.pdf) [two](https://arxiv.org/pdf/2106.08295.pdf) papers.

For ELSER v2 we decided to use dynamic quantization of the linear layers. By default this uses per tensor symmetric quantization of activations and weights. Unpacking this, it rescales values to lie in an interval that is symmetric around zero - which makes the conversion slightly more compute efficient - before snapping. Furthermore, it uses one such interval for each tensor. With dynamic quantization the interval for each activation tensor is computed on-the-fly from their [maximum absolute value](https://arxiv.org/pdf/1910.06188.pdf). Since we want our model to perform well in a zero-shot setting, this has the advantage that we don't suffer from any mismatch in the data used to calibrate the model quantization and the corpus where it is used for retrieval.

The maximum absolute weight for each tensor is known in advance, so these can be quantized upfront and stored in int8 format. Furthermore, we note that attention is itself built out of linear layers. Therefore, if the matrix multiplications in linear layers are quantized the majority of the arithmetic operations in the model are performed in int8.

Our first attempt at applying dynamic quantization to every linear layer failed: it resulted in up to 20% loss in NDCG@10 for some of our BEIR benchmark data sets. In such cases, it is always worthwhile investigating hybrid quantization schemes. Specifically, one often finds that certain layers introduce disproportionately large errors when converted to int8. Typically, in such cases [one performs layer by layer sensitivity analysis](https://arxiv.org/pdf/2004.09602.pdf) and greedily selects the layers to quantize while the model meets accuracy requirements.

There are many configurable parameters for quantization which relate to exact details of how intervals are constructed and how they are scoped. We found it was sufficient to choose between three approaches for each linear layer for ELSER v2:

1. Symmetric per tensor quantization,
2. Symmetric per channel quantization and
3. Float32 precision.

There are a variety of tools which can allow one to observe tensor characteristics which are likely to create problems for quantization. However, ultimately what one always cares about is the model accuracy on the task it performs. In our case, we wanted to know how well the quantized model preserves the text representation we use for retrieval, specifically, the document scores. To this end, we quantized each layer in isolation and calculated the score [MAPE](https://en.wikipedia.org/wiki/Mean_absolute_percentage_error) of a diverse collection of query relevant document pairs. Since this had to be done on CPU and separately for every linear layer we limited this set to a few hundred examples. The figure below shows the performance and error characteristics for each layer; each point shows the percentage speed up in inference (x-axis) and the score MAPE (y-axis) as a result of quantizing just one layer. We run two experiments per layer: per tensor and per channel quantization.

![sensitivity analysis](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt11f252bd4b884241/6a17d854505ac3ae43ad8979/bd4ce4e581df45dba17db6fbf29d3c51eb5f46df-1440x654.png)

Relevance scores MAPE for layerwise quantization of ELSER v2

Note that the performance gain is not equal for all layers. The feed forward layers that separate attention blocks use larger intermediate representations so we typically gain more by quantizing their weights. The MLM head computes vocabulary token activations. Its output dimension is the vocabulary size or 30522. This is the outlier on the performance axis; quantizing this layer alone increases throughput by nearly 13%.

Regarding accuracy, we see that quantizing the output of the 10

th feed forward module in the attention stack has a dramatic impact and many layers have almost no impact on the scores (< 0.5% MAPE). Interestingly, we also found that the MAPE is larger when quantizing higher feed forward layers. This is consistent with the fact that dropping feed forward layers altogether at the bottom of the attention stack has recently been [found](https://arxiv.org/pdf/2012.11881.pdf) to be an effective performance accuracy trade off for BERT. In the end, we chose to disable quantization for around 20% of layers and use per channel quantization for around 15% of layers. This gave us a 0.1% reduction in average NDCG@10 across the BEIR suite and a 2.5% reduction in the worst case.

So what does this yield in terms of performance improvements in the end? Firstly, the model size shrank by a little less than 40%, from 418 MB to 263MB. Secondly, inference sped up by between 40% and 100% depending on the text length. The figure below shows the inference latency on the left axis for the float32 and hybrid int8 model as a function of the input text length. This was calculated from 1000 different texts ranging for around 200 to 2200 characters (which typically translates to around the maximum sequence length of 512 tokens). For the short texts in this set we achieve a latency of around 50 ms or 20 inferences per second single threaded for an Intel Xeon CPU @ 2.80GH. Referring to the right axis, the speed-up for these short texts is a little over 100%. This is important because 200 characters is a long query so we expect similar improvements in query latency. We achieved a little under 50% throughput improvement for the data set as a whole.

![ELSER v2 quantization speed up](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt7167321e6cbbddf8/6a17d855a29299e0a7d02b00/146101eb589fb3e43df41a6137870167efcb1949-1422x948.png)

Speed up per thread from hybrid int8 dynamic quantisation of ELSER v2 using an Intel Xeon CPU

## Block layout of linear layers in ELSER v2

Another avenue we explored was using the [Intel Extension for PyTorch (IPEX)](https://github.com/intel/intel-extension-for-pytorch). Currently, we recommend our users run Elasticsearch inference nodes on Intel hardware and it makes sense to optimize the models we deploy to make best use of it.

As part of this project we rebuilt our inference process to use the IPEX backend. A nice side effect of this was that ELSER inference with float32 is 18% faster in 8.11 and we see increased throughput advantage from hyperthreading. However, the primary motivation was the [latest Intel cores](https://en.wikipedia.org/wiki/Sapphire_Rapids) have hardware support for [bfloat16](https://en.wikipedia.org/wiki/Bfloat16_floating-point_format) format, which makes better performance accuracy tradeoffs for inference than float32. We wanted to understand how this performs. We saw around 3 times speedup using bfloat16, but only with the latest hardware support; so until this is well enough supported in the cloud environment the use of bfloat16 models is impractical. We instead turned our attention to other features of IPEX.

The IPEX library provides several optimizations which can be applied to float32 layers. This is handy because, as discussed, we retain around 20% of the model in float32 precision.

Transformers don't afford simple layer folding opportunities, so the principal optimization is [blocking](https://oneapi-src.github.io/oneDNN/dev_guide_understanding_memory_formats.html) of linear layers. Multi-dimensional arrays are usually stored flat to optimize cache use. Furthermore, to get the most out of SIMD instructions one ideally loads memory from contiguous blocks into the wide registers which implement them. The operations performed on the model weights in inference alter their access patterns. For any given compute graph one can in theory work out the weight layout which maximizes performance. The optimal arrangement also depends on the instruction set available and the memory bandwidth; usually this amounts to reordering weights into blocks for specific tensor dimensions. Fortunately, the IPEX library has implemented the optimal strategy for Intel hardware for a variety of layers, including linear layers.

The figure below shows the effect of applying optimal block layout for float32 linear layers in ELSER v2. The performance was averaged over 5 runs. The effect is small however we verified it is statistically significant (p-value < 0.05). Also, it is consistently slightly larger for longer sequences, so for our representative collection of 1000 texts it translated to a little under 1% increase in throughput.

![ELSER v2 with IPEX](https://images.contentstack.io/v3/assets/bltefdd0b53724fa2ce/blt82eeb4fb8bff7718/6a17d857420229171c29f465/0ddbbe75dbc777cc17340567de02fe262ca54142-1374x956.png)

Speed up per thread from IPEX optimize on ELSER v2 using an Intel Xeon CPU

Another interesting observation we made is that the performance improvements are larger when using [intra-op parallelism](https://pytorch.org/docs/stable/notes/cpu_threading_torchscript_inference.html). We consistently achieved 2-5% throughput improvement across a range of text lengths using both our VM's allotted physical cores.

In the end, we decided not to enable these optimisations. The performance gains we get from them are small and they significantly increase the model memory: our script file increased from 263MB to 505MB. However, IPEX and particularly hardware support for bfloat16 yield significant improvements for inference performance on CPU. This work got us a step closer to enabling this for Elasticsearch inference in the future.

## Conclusion

In this post, we discussed how we were able to achieve between a 60% and 120% speed-up in inference compared to ELSER v1 by upgrading the libtorch backend in 8.11 and optimizing for x86 architecture. This is all while improving zero-shot relevance. Inference performance is the critical factor in the time to index a corpus. It is also an important part of query latency. At the same time, the index performance is equally important for query latency, particularly at large scale. We discuss this in [part 2](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-2).

*The release and timing of any features or functionality described in this post remain at Elastic's sole discretion. Any features or functionality not currently available may not be delivered on time or at all.*

*Elastic, Elasticsearch and associated marks are trademarks, logos or registered trademarks of Elasticsearch N.V. in the United States and other countries. All other company and product names are trademarks, logos or registered trademarks of their respective owners.*

* **Part 1:** [Steps to improve search relevance](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-search-relevance)
* **Part 2:** [Benchmarking passage retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-benchmarking-passage-retrieval)
* **Part 3:** [Introducing Elastic Learned Sparse Encoder, our new retrieval model](https://www.elastic.co/search-labs/blog/elastic-learned-sparse-encoder-elser-retrieval-performance)
* **Part 4:** [Hybrid Retrieval](https://www.elastic.co/blog/improving-information-retrieval-elastic-stack-hybrid)
* **Part 5:** [Improved inference performance with ELSER v2](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-1)
* **Part 6:** [Optimizing retrieval with ELSER v2](https://www.elastic.co/search-labs/blog/introducing-elser-v2-part-2)

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

![](https://static-www.elastic.co/v3/assets/bltefdd0b53724fa2ce/blt9d9912c8d4187096/6a1704f5b0367d30e672bc17/54a6e5197f5721b36fc65f27387d29803ed35589-721x420.jpg)

[ML Research](/search-labs/blog/category/ml-research)[Python](/search-labs/blog/category/python-programming)

### Evaluating search relevance part 1 - The BEIR benchmark

July 16, 2024|[Thanos Papaoikonomou](/search-labs/author/thanos-papaoikonomou)|[+1](#)

### Ready to build state of the art search experiences?

Sufficiently advanced search isn’t achieved with the efforts of one. Elasticsearch is powered by data scientists, ML ops, engineers, and many more who are just as passionate about search as you are. Let’s connect and work together to build the magical search experience that will get you the results you want.

[Try it yourself](https://github.com/elastic/elasticsearch-labs)Subscribe to newsletter