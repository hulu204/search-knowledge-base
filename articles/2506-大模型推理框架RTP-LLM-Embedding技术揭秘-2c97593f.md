---
title: '大模型推理框架RTP-LLM Embedding技术揭秘'
company: 阿里技术
tag: 搜索/RAG
date: 2025-03-19
url: https://mp.weixin.qq.com/s?__biz=Mzg4NTczNzg2OA%3D%3D&mid=2247507336&idx=1&sn=aa44a3be4c6bc068532002a7c4bff599
account: 阿里技术
origin: weread-history-2024
---
![]()

这是2025年的第24篇文章

（ 本文阅读时间：15分钟 ）

**01**

**背景介绍**

Embedding（嵌入）是现代机器学习和深度学习的重要组成部分，通过将离散数据映射到连续向量空间，解决了高维稀疏性和语义表达的问题。它在自然语言处理、推荐系统、计算机视觉等领域有着广泛的应用。﻿RTP-LLM是阿里巴巴智能引擎团队自研的大模型推理加速引擎，作为一个高性能的大模型推理解决方案，它已被广泛应用于阿里内部，本文将介绍项目在Embedding框架上的实践和思考。

在我们的生产环境中，主要存在两种使用Transformer模型实时生成Embedding的场景：一类是部署在云服务器或者内部大模型服务平台的Pytorch Huggingface模型，用于计算Embedding或者进行重排/分类；另一类是搜推广场景，使用Tensorflow的Bert模型计算商品和用户的相似度。这两类场景性能表现都一般，因此我们希望能够提供一个解决方案，能够在部署方便的前提下，优化上述两种场景Transformer Embedding计算的耗时和吞吐，减少资源消耗。

**02**

**问题描述**

前文描述的两类场景性能不好的问题可以分成两方面，模型算子实现和外围请求调度策略。

﻿

在模型性能层面，Pytorch和Tensorflow模型默认都没有使用高性能的FlashAttention算子，没有做算子融合，在模型参数大的情况下也没有量化支持。并且原生pytorch模型launch开销大，GPU执行效率低[1]。

在外围请求层面，搜推广场景的请求基本都是大批次请求，在进入模型时在序列长度维度对齐，这种凑批方式会导致无用计算增加，进而增加时间；而在线上服务平台层面，单个请求批次太小，无法充分发挥GPU算力 。

因此我们希望解决方案在提供高性能算子（FlashAttention，Elementwise算子合并等），模型量化的同时，在调度层对大批次请求去除空洞、对多个小批次请求进行合并的方式，解决上述的问题。

**03**

**方案调研**

在设计方案时，vLLM和TensorRt-LLM都没有支持Bert模型的Embedding功能，因此最初我们考虑的解决方案是TritonServer+TensorRT Backend。TritonServer使用C++编写，同时提供HTTP和GRPC服务，支持不同请求间凑批和多种请求调度策略；TensorRT Backend提供了GPU上的高性能算子，并且支持通过编译的方式从Pytorch代码转换onnx graph最后构建TensorRT Engine。

这套方案在性能和自动化部署两个角度都非常符合我们的需求，但是存在以下几个方面的问题：

#### "差一口气"的token级别凑批

长度较短的请求在GPU上运行的瓶颈是显存带宽而不是算力，因此合并请求有助于提高算力资源的利用率，从而提高吞吐。而对于不同请求间的凑批，传统的做法是使用padding。假设输入tensor的shape是二维的[batch, seq]，则在seq维度padding到最大值，在batch维度concat。但是这样的做法增加了无用的计算量，对于seq维度差异大的场景显然不合算。

这个问题有解决办法，Triton Server侧实现了Ragged Batching[2]，将输入打平成一维做concat以避免padding，这种凑批方式我们称之为token级别凑批。并且TensorRT的Bert模型支持使用Variable Sequence Length[3]，通过这种方式构建的引擎支持token维度凑批的输入。但是这种引擎无法通过编译的方式构建，必须编写TensorRT插件代码，在产品上非常不灵活。

#### 模型支持欠缺

在Pytorch->ONNX->TensorRT Engine的构建模式下，除Bert外很多模型支持的都不是很好。以Layernorm操作为例，由于Layernorm计算公式中有平方和的累加，因此在半精度下经常会越界导致结果nan。

Tensorrt的解决方式是识别ONNX图中的LayerNormalization算子，将这部分运算使用fp32精度来解决。但是这两年流行的大语言模型（Large Lanuage Model, 简称LLM）很多使用了Rmsnorm代替Layernorm，ONNX里没有Rmsnorm的算子，所以TensorRT无法识别到这个结构，会在FP16/BF16精度下进行这部分网络的计算，导致模型输出错误。

#### 跨设备支持不友好

TensorRT仅提供了Nvidia GPU上的模型加速，如果希望在AMD或者CPU上进行高性能计算，则需要额外开发Triton Server的backend，开发成本大。

基于上述的考虑，最终我们没有使用上述方案，而是在我们自研的大模型推理引擎RTP-LLM[4]中开发了Embedding模块。RTP-LLM集成了Cuda/Rocm/Arm的高性能算子，对主流大模型都有比较完善的支持，并且框架内天然支持token级别凑批，在性能和迁移性方面都解决了上述提到的痛点。在RTP-LLM中支持Embedding功能，我们可以更多的把开发重心放在如何便捷的部署各种类型的Embedding模型。

**04**

**框架设计**

在介绍Embedding框架之前，先简单介绍下RTP-LLM在大模型场景下的生成链路：用户请求在编码后会先进入调度器（Scheduler），调度器管理请求生成所需要的资源，并在每轮生成时选择一批请求到执行器（Executor）。执行器根据请求的生成阶段（Prefill/Decode）将请求组装成模型接受的格式送到模型层执行，最后将结果更新后送回调度器进行下一轮调度。相比LLM框架，Embedding框架做了以下三处改动：

﻿

调度层：Emebedding可以认为是大模型生成中的Prefill阶段，但是不需要保留KVCache。针对这个特点，我们简化了Scheduler和Executor里的流程，并且允许请求不申请KVCache，减少显存的占用。同时在Embedding Scheduler会在限制范围内尽量的进行请求凑批，在单条请求延迟在接收范围的同时提高服务吞吐。

﻿

后处理：LLM的后处理流程通常是采样，但是Embedding的后处理流程多种多样。对于同一个模型，在不同的下游任务下，会使用不同的网络处理Transformer层输出。这些网络结构大部分定义在Python Embedding库中（Sentence Transformer / Flag Embedding等），小部分作为里的Python文件附带在checkpoint文件中。由于后处理流程相比Transformer网络耗时占比非常小，因此Embedding框架中这部分网络仍在Python中构建，在运行时通过pybind11调用，并且支持用户使用SentenceTransformer配置自定义这部分逻辑。小部分性能敏感的场景则支持通过c++重写后处理代码以达到更好的性能。﻿

请求层：和生成式任务相比，部分Embedding任务的结果较大（[batch, hidden\_size] / [batch, sequence\_length, hidden\_size]），使用json存储会产生较大的响应包，且使用HTTP协议在json序列化和反序列化都会有较大也会产生额外的开销，最终造成性能上的损失，因此对部分场景我们也支持了RPC协议访问，包括开源的Grpc和内部Arpc两种方式请求Embedding，减少这部分开销。

最后我们实现的Embedding框架如下图：

﻿![]()

**05**

**模型量化**

RTP-LLM中对模型的量化有WeightOnly INT8/INT4量化、Dynamic SmoothQuant[5]和FP8量化，这些量化方法通过提升Transformer模型的矩阵乘速度的方式加速模型推理。在大部分LLM场景这些量化都有不错的表现，但是在搜推广场景上这些优化都没有收益，原因如下：

* WeightOnly量化仅适用于矩阵乘输入数据(activation)远小于权重(weight)的场景，此时矩阵乘是访存瓶颈任务，WeightOnly量化通过降低模型权重大小的方式减少访存需求，从而加速矩阵乘。而搜推广场景使用隐乘大小是768的Bert模型，这时矩阵乘权重shape为[768, 768], [768, 2304]和[768, 3072]，而输入数据的大小平均是[3840, 768]，此时矩阵乘是计算瓶颈任务，而WeightOnly量化需要在运行时反量化增加了计算量，甚至会拖慢矩阵乘的速度。

* Dynamic SmoothQuant量化通过同时量化矩阵乘输入数据和权重成INT8数据格式，并使用INT8 Tensor Core的方式，同时加速了模型权重读取和计算的速度，对于矩阵乘本身有明显的加速。但是不同于在加载模型时就量化好的权重，将输入量化成INT8的过程是实时的，因此需要引入额外开销。实际测试我们发现在[3840, 768]的输入下，量化输入的新增时间基本和矩阵乘加速节省一致，因此SmoothQuant在这个场景下也无法发挥作用。

* FP8可以认为是w8a8量化的升级版，在保持较高精度的同时使用FP8 Tensorcore进行计算，而且框架还支持了FP8的FlashAttention，但是搜推广场景线上大部分卡是A10/V100，在硬件上缺少FP8的支持。﻿

最后我们开发了Static SmoothQuant的方式加速Bert模型，Static SmoothQuant（下称StaticQuant）和Dynamic SmoothQuant（下称DynamicQuant）的区别在对DynamicQuant操作中有一个Reduce操作统计数据的最大值，这一步会引入比较大的开销。

StaticQuant将这一步放在训练时，通过统计训练数据中最大值近似，因此需要耗费的时间大大减少。并且StaticQuant的量化是一个Elementwise操作，可以通过算子融合的方式合并到Gemm和Layernorm算子中，进一步降低耗费的时间，具体前后对比如下：

﻿![]()﻿

我们以输入shape为[3840, 768]的情况下A10机器上测试，StaticQuant模型单个请求耗时2.9ms，对比原始模型4.9ms降低40%。上线后量化模型对比原始模型效果损失在0.1%以内，达到了预期效果。

**06**

**总结与展望**

我们基于RTP-LLM实现了Embedding框架，支持部署Transformer结构的Embedding模型及其下游任务（Reranker/Classifier），在请求上支持HTTP/ARPC/GRPC协议，在部署上支持用户使用SentenceTransformer自定义后处理逻辑。Embedding引擎已服务了淘宝主搜等多个在离线场景，并成功度过双十一洪峰。虽然当前已解决许多问题，但未来仍有很多优化空间：

* HTTP服务的入口目前还在Python侧，这导致HTTP请求会受限于Python的性能，在高并发短请求时无法充分发挥引擎性能。在近期我们会改用C++ HTTP服务解决这部分问题。
* 由于后处理部分输入格式是完全确定的，可以引入torch的compile技术减少kernel launch消耗。
* 参考vLLM的Multi-Step Scheduling[6]，将Scheduler和Executor改成是生产者消费者模式，并行化请求调度，数据传输和模型执行，进一步提高框架性能。﻿

除此之外，我们也将尝试框架层之上的优化。比如目前我们使用的负载均衡策略是RoundRobin，但是线上Bert集群的平均延迟和p99延迟仍有很大差距，原因是在机器上有并发的大批次请求，导致单个请求排队，是否有更好的策略能够在Embedding这种高qps短rt的场景让流量更加均匀呢？诸如此类的问题都需要我们继续探索和优化。

RTP-LLM项目已在 GitHub上开源，欢迎大家与我们交流共建！

![]()

参考资料

[1] Accelerating Generative AI with PyTorch II: GPT, Fast

https://pytorch.org/blog/accelerating-generative-ai-2/

[2] TritonServer Ragged Batching

https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user\_guide/ragged\_batching.html

[3] Bert Variable Sequence Length

https://github.com/NVIDIA/TensorRT/tree/release/10.7/demo/BERT#variable-sequence-length

[4] RTP-LLM

https://github.com/alibaba/rtp-llm

[5] SmoothQuant: Accurate and Efficient Post-Training Quantization for Large Language Models

https://arxiv.org/abs/2211.10438

[6] vllm multi-step scheduling

https://github.com/vllm-project/vllm/issues/6854

![图片]()

![图片]()

欢迎留言一起参与讨论~