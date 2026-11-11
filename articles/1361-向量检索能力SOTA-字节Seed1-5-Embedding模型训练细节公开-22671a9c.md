---
title: '向量检索能力SOTA，字节Seed1.5-Embedding模型训练细节公开'
company: 字节跳动
tag: 召回
date: 2025-05-13
url: http://mp.weixin.qq.com/s?__biz=MzI1MzYzMjE0MQ==&mid=2247514515&idx=1&sn=78bab831f872f773ce0ddf22c3d81be5&chksm=e9d37271dea4fb676a11ff6a29d1093bba0b5219bf82084b16e8ea1028c66c33cb3c3d08a5cd#rd
account: 字节跳动技术团队
origin: wechat-mp
---
字节跳动 Seed 团队最新向量模型 Seed1.5-Embedding 公布技术细节，该模型基于 Seed1.5 (Doubao-1.5-pro) 进一步训练。在权威测评榜单 MTEB 上，Seed1.5-Embedding 达到了中英文 SOTA 效果。除了通用 Embedding 任务外，团队还额外优化了模型在推理密集的检索任务上的能力，并在对应榜单 BRIGHT 上也达到 SOTA。

团队认为，Seed1.5-Embedding 可作为搜索任务中的关键组件，高质量地将用户输入文本、文档信息转换为向量并建立匹配关系。该模型 API 接口将于近期在火山方舟平台开放，欢迎保持关注：

HuggingFace: https://huggingface.co/ByteDance-Seed/Seed1.5-Embedding

向量模型（Embedding Model）可将输入文本的语义编码到高维空间的表征向量中，使得相关文本之间的向量相似度更高，能够支撑检索、分类、聚类等各项下游任务，从而在搜索、推荐、内容理解等场景中被广泛应用。

随着大模型技术迅猛发展，向量模型基座也由 BERT 向大模型迁移，并从更大的参数量中，获得更强编码能力；同时，向量模型作为检索增强生成（RAG）机制的关键组件，可为大模型引入外部知识使其产生可靠的回复，其重要性进一步凸显。

近日，字节跳动 Seed 团队公开最新向量模型—— Seed1.5-Embedding。

Seed1.5-Embedding 重点在以下 3 个方面进行了优化和迭代：

* 设计两阶段对比学习训练流程并精心构造训练数据，充分强化模型的通用表征能力；
* 从预训练和后训练语料中，构造出推理密集型检索数据（需要深度理解查询和文档的匹配关系，而非简单的字面匹配或语义匹配），并用其优化模型；
* 使用少量激活参数的 MoE 模型作为基座，并通过 MRL 训练支持多个向量维度，实现较高的运行速度和灵活的存储开销。

针对向量模型能力评测，MTEB 是目前最主流的通用榜单，涵盖多种语言（中文、英文等），多类任务（检索、聚类、分类等），包括 Google、NVIDIA 在内，多家厂商自研向量模型均参与了 MTEB 评估。同时，BRIGHT 榜单因专门用于评估向量模型的推理密集型检索能力，任务设计侧重考察查询和文档的深层理解与推理能力，同样受到社区的广泛关注。

Seed1.5-Embedding 面向上述两个评测榜单，在中英文领域均取得了 SOTA 的效果，超越 Gemini-Embedding（Google）、NV-Embed（NVIDIA）、GTE、Conan 等同类模型。

具体表现如下：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCwYB4XWgzbXYCqticQ592d4AesHhMojCybNkt6KASrgtkBCAmkoXCQYA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

**MTEB\_v2（英文，通用任务）榜单**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCWzjWUolDDzp4pibpj2fGjoVksBicgJmDTdDFhibKZscpv5ibA9mUNo2yGA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)CMTEB（中文，通用任务）榜单

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCxAzweQo5s04FZ7FESySeqN0ajhwAFtTFkXhBuEzdpnjudqiaEEE0gCg/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

**BRIGHT（英文，推理密集型检索）榜单**

**1. 基于 MoE 的向量模型：让 AI “听懂”搜索需求，也能复用文本特征**

当传统搜广推技术与大模型浪潮彼此碰撞，向量模型也相应面临着更高要求：

（1）向量模型须具备强大的通用能力，精准建模文本的深层语义，从而为大模型引入最适合的外部知识；

（2）现实中，搜索场景经常涉及查询、深入理解文档，向量模型须在建模语义的基础上，进一步提升推理能力，以捕捉、建模复杂的匹配关系；

（3）向量模型须在运行和存储时足够高效，以支持各种下游场景的实际应用。

**为满足上述要求，团队从****向量****模型****的****设计，到训练、数据工程，进行一系列优化和改进：**

在模型结构上，团队使用 Siamese 双塔向量模型结构，取所有 token 表示的平均作为最终文本向量，查询与文档之间通过 cosine 相似度计算匹配得分。其依托 Seed1.5 预训练 LLM，并将单向注意力改为双向，构建出一个小规模 MoE 模型，且查询侧和文档侧模型参数共享，保证了较高的运行效率。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCZUicLCibCoiaLJwcRyDg2MeR6qnjz7zYKddVMUsyXnYh7046tRWFibUyAQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

在实际应用中，向量模型的查询侧负责将用户输入转为向量，帮助 AI 理解查询意图。团队为不同任务定制了指令，引导模型学习相应的匹配方式。文档侧则不使用指令输入，从而使文档向量可在多任务间复用。

## 2. 二阶段训练：逐步建立模型通用表征能力，支持不同尺寸向量

预训练大模型面向生成任务，其目标是基于隐层表示，预测下一个 token，而向量模型是面向表征任务，其目标是基于隐层表示进行相似度计算。为了将大模型改造成为向量模型，团队采用二阶段训练，逐步建立模型的通用表征能力。

* 第一阶段：让模型充分建模不同文本匹配模式

我们使用无监督数据进行预微调（pre-finetune），通过大量数据进行对比学习，将单向 Attention 的生成模型改造成为双向 Attention 的编码模型，并让模型充分建模各种文本匹配模式。

这些数据形式均为（查询文本，相关文本）对，包含网页标题-段落，QA 平台问题-答案，论文标题-摘要等各种形式。我们使用标准的 InfoNCE loss：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCTdGIVf6GhO48qaIURuW5vvajFXzNAhzzTuticyjT0cMwrbZyib0hibAnA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

其中![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCCTfABKV06eMjicVicLhp6VF2DwooDlkNBVNtheCvrrz8DUk3XXbWtic5A/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)是正例文档, ![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrC2uYcuuhZ9NzcictCKHYUVlFB5ko9yenjnkrG2ZFpN6XRQJY86gFI96Q/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)是负例文档，q,d 分别是查询向量和文档向量,![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCcY5SUT4Kic5z2tVj9yV1XZRPtItBlH79cyicMbTdyVlrgPYicXv9Vx9fA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)为温度系数。在第一阶段训练中，我们仅使用 in-batch 负例（同 batch 内其他查询对应的文本）。

* 第二阶段：让模型学习不同任务中的最佳表征模式

我们使用有监督数据和合成数据进行微调（fine-tune），将检索以及各种任务的数据混合，进行多任务优化，让模型自行学习各个任务最佳的表征模式。

由于 Sentence Text Similarity（STS）任务的目标是学习拟合 Ground-Truth 打分，以衡量两个句子之间的语义相似程度，而 InfoNCE 仅能基于 1 - 0 标签学习，所以，团队在 STS 任务上使用了 CoSENT loss，其余任务使用 InfoNCE loss。

注意在本阶段中，团队还引入难负例（和查询有一定程度语义匹配，但并不能完全匹配），并对检索数据使用 in-batch 负例和难负例，而别的任务仅使用难负例，以进一步强化模型的分辨能力。

为了支持下游任务中不同尺寸的向量（维度 M = {256,512,1024,2048}）使用场景，团队对效果和存储开销进行权衡，使用了 MRL 优化 InfoNCE loss 和 CoSENT loss，在一个高维向量中嵌套多个低维向量，减少嵌入向量大小同时，保持性能，具体形式如下：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCEI3ias7icCvHz8YMTW7ibdibDicJUlvIbf3mQQSIeBsYfxAibSF3Q44ibBgdg/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

## 3. 优化数据构成和质量，提升检索任务表现

检索是向量模型最重要的应用场景，难度也最高。该类任务中，向量模型要能准确建模文本语义，从海量文档中定位相关信息。为提升模型在此类场景学习效果，团队设计了三个数据工程策略，优化数据构成和质量。

* **负例挖掘**

难负例，即——和查询有语义相似但是并不能完全正确匹配的文本，可有效提升向量模型效果，让其能区分细粒度相关性，而通常做法中，使用开源模型挖掘的负例，时常无法贴合待训练模型的偏好。

为此，团队设计了迭代式难负例挖掘策略：根据待训练模型模型自身偏好挖掘难负例，从而筛选出更“刁钻”的难题，供模型训练，以进一步提升其能力。

* **伪负例过滤**

InfoNCE 是一种用于对比学习的损失函数，旨在将查询向量和正例向量拉近，和负例向量推远，因此，负例的质量对学习效果至关重要。但训练过程中，语料库中存在的没有标注的正例，可能会被当作负例（伪负例），该类数据会混淆模型的学习信号，导致效果变差。

具体在第二阶段训练中，检索任务的负例既包含挖掘得到的难负例，又包含 in-batch 负例。其中，难负例中可能存在过难的伪负例，此外，在使用 in-batch 负例时，由于不同查询是经过随机采样组成 batch，因此，当语料库较小或查询分布较为集中时，同 batch 内不同查询对应的文本也可能构成伪负例。

针对这两种情况，团队在挖掘难负例时和计算 in-batch 负例 loss 时，会自动过滤和正例过于相似的文本，从而避免伪负例影响学习。

* **合成数据**

在实际应用中，各种检索场景的匹配模式不同，这要求向量模型不仅能支持语义匹配，还应当能通过推理来理解复杂的查询和文本，并建模深层匹配关系。为此，团队分别针对通用场景和推理密集场景构造数据。

在通用场景下，团队先 prompt Seed1.5 模型根据语料库中文档生成多样化查询，并仅保留相关度较高的查询-文档对。针对保留下来的查询-文档对，团队应用前文提及的负例挖掘方法挖掘难负例。

在推理密集场景下，由于文档和查询均较为稀缺，团队从大量没有标准答案的难查询出发，从文档库中挖掘候选并用大语言模型筛选正例与难负例，进而得到推理密集型检索场景的训练数据。

**4. 中英文场景通用能力与推理检索能力均为 SOTA**

测试结果显示，Seed1.5-Embedding 在MTEB榜单中英文任务上超过 gemini-embedding、Conan-embedding-v2 等业界具有代表性的向量模型，证明了其通用能力。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCjBnKyaN8F8fqdRSLObXfhYELicHA8RwzyQkrHXMu7RzbpfxR1cx64bA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

AVG 为所有任务效果平均值，结果来自 MTEB 榜单

通用任务之外，Seed1.5-Embedding 在推理密集型检索 BRIGHT 榜单上也超过其他同类模型，并且在 Biology、Earth Science、Coding 等基于 StackExchange 上的复杂搜索上与现有模型拉开显著差距，证明该模型能深入理解查询和文档侧的输入，并建模两者之间复杂的匹配关系。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrChuuM8LoHGy22QGAz3Bbz4MJvWgXFOuN11wXLgr5BHwKUoFS757IaRA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

基线模型效果来自于论文《BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval》和《ReasonIR: Training Retrievers for Reasoning Tasks》

最后，我们在检索这一最重要任务上消融了各项设计带来的影响，结果如下：

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESuhicXibv9aISjlY0qZCg6eUrCpn7Sekmru3ekR6wkzSwhm6fRXArrdJAxtzWJ4MDZOkkowBdicicL1EjQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

团队基于消融实验，还得到以下观察：

（1）第一阶段预微调、迭代式难负例挖掘、负例过滤三者对通用任务检索效果均有一定提升。负例过滤在英文上效果更加明显，该现象源于多个英文数据集文档数较少，同时面临伪难负例和伪 inbatch 负例的情况；

（2）合成数据可提升英文检索表现以及推理密集型检索效果，在中文上，训练数据则较为充足，团队没有使用合成数据。

这些现象促使团队在训练向量模型时，更关注训练数据的数量和质量，前者能够让 LLM 更好地从生成范式迁移到表征范式，后者能够保证向量模型的检索效果。

团队还认为，可以使用合成数据定向优化特定的检索场景，让模型学习对应场景下特别的匹配模式。

 5. 写在最后 

Seed1.5-Embedding 的 API 接口将于近期在火山方舟平台开放，此外该模型以及相关技术将很快被应用于豆包 APP 的搜索召回中，从而提升检索的精度，更好地服务用户。

未来，团队将继续探索扩增模型参数带来的影响，并尝试覆盖面更广、通用性更强的数据构建方式，从而进一步扩展向量模型的能力边界。此外，团队还将探索下一代向量模型训练范式，期望用更自然、高效的方式将生成大模型能力迁移到向量表征任务上。

[1] MTEB: Massive Text Embedding Benchmark. 

[2] BRIGHT: A Realistic and Challenging Benchmark for Reasoning-Intensive Retrieval. 

[3] Improving Text Embeddings with Large Language Models.

[4] Towards General Text Embeddings with Multi-stage Contrastive Learning. 

[5] NV-Embed: Improved Techniques for Training LLMs as Generalist Embedding Models. 

[6] Gemini Embedding: Generalizable Embeddings from Gemini. 

[7] Conan-embedding: General Text Embedding with More and Better Negative Samples. 

[8] CoSENT（一）：比Sentence-BERT更有效的句向量方案 

[9] ReasonIR: Training Retrievers for Reasoning Tasks. 

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/IrH3BAPESujnpqJBYt5qgOL3uBkhJgrxkPY5HAa1YAnxORCtHvXqsKyVht2wAXUPKRAia2b59lc3gTWGLyd2zwA/640?wx_fmt=jpeg&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)

[![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESujnpqJBYt5qgOL3uBkhJgrxMSCBtObLtVJ2bqxE2j0KBooTyGGZ1QMQsOhXpnbWKoqhcCaMicvwibRQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)](https://mp.weixin.qq.com/s?__biz=MzkzMDY5MzYxNg==&mid=2247490396&idx=1&sn=f3aad78c2ee3742f9953e27ba08d4137&scene=21#wechat_redirect)

[![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/IrH3BAPESujnpqJBYt5qgOL3uBkhJgrxIN4BJOh3vzv02HjicrJKRSDYq0Y3icXH6anSK8V6o4TiaKMlhM14P6o2w/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1)](https://mp.weixin.qq.com/s?__biz=MzkzMDY5MzYxNg==&mid=2247490844&idx=1&sn=e518e26d459d5d34fd800aba221ccec8&scene=21#wechat_redirect)

****点击“阅读原文”，了解更多团队信息！****