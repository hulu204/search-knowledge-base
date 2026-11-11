---
title: '深入剖析开源大模型+Langchain框架智能问答系统性能下降原因'
company: 腾讯
tag: 问答/RAG
date: 2023-12-12
url: http://mp.weixin.qq.com/s?__biz=MjM5ODYwMjI2MA==&mid=2649781382&idx=1&sn=5b5976b30d75737338d1cf9fb8e2f673&chksm=becce7fd89bb6eebea76733b1f47e4af160f7e7dbefe0b52c0471c33e5c4e7dbe2f963f9f68f#rd
account: 腾讯技术工程
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_gif/j3gficicyOvasIjZpiaTNIPReJVWEJf7UGpmokI3LL4NbQDb8fO48fYROmYPXUhXFN8IdDqPcI1gA6OfSLsQHxB4w/640?wx_fmt=gif)

作者：barry

大模型（LLM）相关理论研究与工程实践随着 GPT3 的发布，在学术界、工业界大爆发，备受各行各业关注，并涌现出一些赋能行业、促进生产力、生产关系变革的实践。GPT3 [1] 以及斯坦福计算机学院近 100+ 教授联名论文 [2] 将大模型列为第三轮 AI 浪潮，相对于传统的机器学习与深度学习，以 GPT3 为例的大模型涌现出处理各类任务的新范式：zero-shot、few-shot、in-context 等，同时也支持深度学习领域的 finetune，新范式让大模型能够低成本、快速处理各种任务，极大的缩短了数据准备与工程开发流程。

其中，in-context 作为随着大模型涌现的范式，被大规模的应用到各种知识库问答、资料汇总等领域中，开源社区对 in-context 也非常活跃地响应，推出了 langchain [3]、向量数据库 [4] 等系列优秀框架与技术基座。但是，基于 langchain + 开源大模型在实践过程中也会遇到系列不尽人意的问题，本文将深入剖析 langchain + 开源大模型用于搭建基于公司语料库（iwiki、oncall、码客）上的缺陷，剖析利用开源方案进行实践过程中性能下降的根本原因。

### **常规方案**

#### **架构**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvaszxKPUL2401icfs3c3M3MZlqiaYr7CfttAFlVsLnLcPcDvsm0W5uEPe7LJDmbBgibuxaDrmjg1rILdw/640?wx_fmt=png)

图1 基于 langchain + LLM 做知识问答的常规方案

基于 langchain + 大模型 in-context 能力来搭建智能问答系统的常规方案如上图所示，包含 3 个核心模块：数据服务，在线 QA 服务，以及大模型。下面分别详细说明一下各个模块具体做些什么？他们是如何串联在一起完成整个问答任务的？再反过来看看为什么业界基于 openAI 实践很棒，而如果换成基于开源自研后性能下滑很多？

#### **数据服务**

**数据对方案的性能影响极其重要，高质量的数据对模型的提升非常显著；但数据处理是一个 caseBycase、包含很多经验与 tricks 的事情，例如文档中的截图、表格、公式、超链接、附件、架构图、流程图、代码片段等等，本文不予以展开分析。**

**做数据最需要关注的是模型的输入及格式**。做知识问答系统本质是自然语言处理的一个任务，因此，数据形态必须是文本，这是最基本的原则，所以如果数据包含非文本类的形态，例如图片（iwiki、码客、oncall 存在大量截图），就需要处理一下，每个人的处理方式和策略不一样，处理得好，最终系统性能会表现好一些。数据服务包含 3 个步骤，格式化（format）、切割（split）、向量化（vectorize）。

* **格式化。**解析不同源数据（csv、pdf、json、html、markdown、txt 等）到统一格式，并进行预处理与过滤

**为什么以及如何进行预处理与过滤？**

参考所选 LLM 在训练/ instruction finetune 处理数据方式（去掉特殊字符、换行空格等）同步处理数据。这么做的原因是 LLM in-context 应该和 训练/instruction finetune 的数据处理方式保持一致，可以保证 in-context 效果达到最佳。所以格式化的第二步，和选用的 LLM 相关。

* **切割（split）。**将格式化的长字符串按照一定策略切分为若干个切片（chunk）。

**为什么要进行切割？**

看到上述框架图绝大多数人应该有的一个疑问。如果深入思考的话会发现 embedding（text2vec，文本转化为向量）以及 LLM encoder 对输入 tokens 都有限制。embedding 会将一个 text（长字符串）的语义信息压缩成一个向量，这是他的能力，但我们需要重点关注他的局限性，其中之一就是 text 包含的 tokens 有限制，一段话压缩成一个向量是 ok，但一本书压缩成一个向量可能就丢失了绝大多数语义。LLM encoder tokens 的限制在模型结构（利用 next token 进行 pre train）是就定义了，后续也无法更改，而 in-context 本质是把语料注入到 prompt，整个 prompt 不能超过 LLM 的 tokens 限制， 汇总如下公式：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvaszxKPUL2401icfs3c3M3MZlDN64yBc2n66aSNCwfNULvDZO7DpDgd5ibZYCvkHgn9tj20NDJEO9gAw/640?wx_fmt=png)

为了确保格式化的语料能够满足上述约束，因此需要切割原始语料。

**如何切割？**

通常采用固定长度切割（满足上面公式约束下），但固定长度切割容易破坏自然段落的语义，因此需要在上面公式约束与段落语义保留双重约束下，灵活设计方案，切割后的语料片段称为 chunk。

* **向量化与存储。**

**为什么进行向量化？**

NLP 领域近 10 年来最朴素最广泛应用的一个技术 embedding 就是将 text 的语义信息转为向量表达，从而基于此向量来处理 NLP 领域中的一系列任务，例如通过向量相似性来衡量两句话语义是否一致等。

**向量化的评价指标有哪些？**

Huggingface 有一个 embedding 的 benchmark，如链接：<https://huggingface.co/spaces/mteb/leaderboard>。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvaszxKPUL2401icfs3c3M3MZlwnSDOVFrH4GjVXqy7IZiaMH98klJUrzEibIccO3EP1G8KAHicCvic9d7Xw/640?wx_fmt=png)

图2 huggingface embedding 综合能力排序

业界通常用 embedding 所得向量长度及其在各 NLP 子任务上的准确率来评估 embedding 模型。原则上：embedding 所得向量长度越长越好，过长的向量也会造成 embedding 模型在训练中越难收敛。分类（Classification）、聚合 (Clustering)、语义相似 (Pair Classification)、排序（Reranking）和召回（Retrieval）等子任务常用来评估 embedding 模型的优劣，准确率越高，embedding 的性能越好。

**向量如何存储与检索？**

向量的存储与检索是一门特别复杂的课题，涉及向量检索（包含很多相似性度量算法，向量压缩等知识）和向量存储，当前火热的向量数据库方向就是因此而生，在规模不大的情况下用 faiss 做检索够用了，未来有机会将专题就这个点开展分析，这里不予以赘述**。**

#### **在线 QA 服务**

在线 QA 服务是串联大模型与存储向量数据库之间的纽带，大模型不能将数据库所有数据拿去做 in-context，实际上，大模型 in-context 能包含的 chunks 十分有限，在线QA服务核心就是挑选出合适的 chunks 给大模型。在线 QA 服务通过企微、webapi等方式对外提供交互，包含 3 个核心功能模块：用户问题向量化、prompt 组装、筛选 chunks。其中，在线 QA 服务核心在于筛选 chunks，这一步对整体性能至关重要。

* **用户问题向量化。**

同数据服务 chunks 向量化一样，采用同一个 embedding 模型对用户问题进行向量化。

* **prompt 组装。**

将用户问题，筛选出的 chunks 组装成 prompt，prompt 即为大模型的输入，整个 prompt 不超过大模型输入 tokens 长度的限制，以 openAI gpt-3.5-turbo 为例，输入 tokens 限制为 4096，假设每个 chunks 固定长度为400，不考虑 prompt 不变字符串的长度，gpt-3.5-turbo 最多可以放 10 个 chunks 进行 in-context 学习。

* **筛选 chunks。**

在用户问题与 chunks 经同一 embedding 模型将 text 转为向量：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvaszxKPUL2401icfs3c3M3MZlagBAux9utvWS6ibKib2SCySF9zQI1uyHVN01lzlweJytjZSAvoUKF4aQ/640?wx_fmt=png)

(M 是 chunks 的总数量)，langchain 给的方案是通过计算之间：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvaszxKPUL2401icfs3c3M3MZlfmd9aC4eEFz093h7OtKvVbma4ibeDdvAmR5UicQA4LJ2NfRdLfEnzVcw/640?wx_fmt=png)

的相似度（cos、BM25、knn、欧氏距离等）并倒排来决定哪些 chunks 被召回。本质上前者是 Question，而后者是 Answer，因此 langchain 是利用了 embedding 在召回（Retrieval）任务上的能力来筛选 chunks， 如图 2 红色垂直列所示，这符合问答系统的初衷。**非常值得注意的是：embedding 在召回任务上的准确率是其在所有 NLP 任务重最差的一个，QA 任务在语义空间上的表达远不如分类、聚合等任务。**常规方案中，langchain 直接召回排序 top8 chunks 给大模型进行 in-context 推理 (gpt-3.5-turbo 4096 tokens)。

#### **大模型**

问答系统使用了 LLM in-context 的推理能力，将筛选出来的若干个 chunks 传给大模型，让大模型基于这些 chunks 来回答用户问题，有个限制是整个 prompt 的 tokens 长度不要超过 LLM 输入 tokens 限制，不然 GPU 会报 OOM。LLM in-context 的推理能力本质是其在阅读理解，因此，选择问答系统的 LLM 需要重点关注其在阅读理解任务上的性能，好的 LLM 可以非常精准的从一组 chunks 中寻找并总结出用户 query 对应的答案。

#### **串联**

将上述各功能模块的逻辑串联一起，从整体的视角观察一下 langchain + 大模型做问答系统整个方案的实践。

LLM 需要上游提供一些语料 chunks，结合 chunks、用户query、自身阅读理解能力完成知识问答。对问答准确率影响最大的因素是 chunks 的质量（是否包含正确答案），LLM 自身阅读理解能力。同时， LLM 输入 token 长度限制导致 prompt 中 chunks 的数量有一定约束，原则上，chunks 数量越多，包含正确答案的概率越大，同时也导致模型的推理速度变慢。

LLM 上游主要目的是召回出候选的 chunks，常规方案使用的是 embedding 处理召回任务的能力，对于一步召回直接注入到 prompt（无精排逻辑），假如传给 LLM prompt k 个 chunks，那么对于召回来说，只需要相似性算法倒序排序前 k 个 chunk 中包含正确答案即可，即关注 embedding 在召回任务中 TopK 的准确率。

综上所属，常规方案中对智能问答系统准确率影响最大的几个因素如下：

1、embedding 在 Retrieval 任务中 TopK 的准确率 （受 embedding 模型自身能力、Retrieval 算法、K等三个因素影响）

2、K 的大小，K 原则越大越好，但是 LLM 的 tokens 限制导致 K 由不能太大。

**（上述 1、2 的都是为了从数据库海量 chunks 中选择出包含正确答案的 chunks）**

3、LLM 自身阅读理解与总结推理能力。

### **openAI 与开源 LLM**

**为什么 langchain + openAI 全家桶准确率特别高，换成开源 LLM 性能下降很多？**

使用 openAI 全家桶构建智能问答系统必用两个能力：openAI 的 embedding 与 gpt-3.5-turbo 模型。

图 2 huggingface embedding benchmark 中 openAI 发布的 [text-embedding-ada-002 （2021/09 ）](https://platform.openai.com/docs/guides/embeddings/types-of-embedding-models)最大输入 tokens 限制是 8191，输出维度是 1536，在 Retrieval 中 top1 的准确率是 49.25%。这组数据表明 openAI embedding 模型具有非常棒的语义表达能力，能够非常好的将问题、答案映射到相近的语义向量空间中，可以说该 embedding 模型是业界最强的映射 QA 能力的模型。

openAI 的商用模型 gpt-3.5-turbo 输入 tokens 限制为 4096，如果切片每个 chunks 长度为 400，embedding 可以召回近 10 个候选 chunks，即 text-embedding-ada-002 模型 top10 的准确率即可近似为问答系统的整体准确率（做信息流推荐召回排序的同学应该了解，top1 准确率接近50%，top10 的准确率会很惊人），而 gpt-3.5-turbo 自身的阅读理解也高出开源 LLM 一个水平，能够精准的从所有的 chunks 中找到准确答案。

综上: openAI 全家桶中 embedding 在 Retrieval 任务的高性能、gpt-3.5-turbo 的阅读理解能力，输入 tokens 够长等三个重要因素，是常规基于 langchain + openAI 做智能问答系统，用用户问题向量与语料内容向量进行相似性计算并直接召回给 prompt，最终能够取得非常好效果的重要原因。

openAI embedding 与 gpt-3.5-turbo 强劲性能掩盖了一些问题，这些问题在基于开源 LLM 做自研问答系统时被暴露，直接导致开源 LLM 方案性能下降。

openAI 全家桶与开源 LLM 方案的对比如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvaszxKPUL2401icfs3c3M3MZlp7AuibhChEVicGO1D2Qxicib86xHanHqnJt2PX7CPI9fhibseI8A5AfNMhQ/640?wx_fmt=png)

在 Retrieval 任务的语义关联映射上，openAI 的 embedding 模型能力远高于开源 LLM（15 个百分点以上）；LLM token 的限制，导致采用 openAI 召回的 chunks 数量比开源 LLM 多一倍；同时在阅读理解能力上，gpt-3.5-turbo 能够非常好的从一系列 chunks 中找到并总结出最佳答案，而开源 LLM 在这方面能力稍微逊色一些。综上，选择目前开源最好的组合方案：llama 的 vicuna13B 与中文领域开源最好的 embedding 模型 [GanymedeNil/text2vec-large-chinese · Hugging Face](https://huggingface.co/GanymedeNil/text2vec-large-chinese)，采用常规的 langchain + openAI 技术框架，性能会下降很多。

### **总结**

通过全文分析，总结出开源 LLM 大模型在 openAI + langchain 通用的技术方案下，性能不佳的原因主要如下：

* 使用 Question-Answer （embedding Retrieval） 作为召回排序是性能不佳最根本的原因，开源的中文 embedding 模型在 Retrieval 任务上表现不佳。
* 模型输入 tokens 限制导致候选的 chunks 数量少于 openAI 模型近一倍，是整体准确率低于 openAI 全家桶的一个重要原因。
* 模型自身在阅读理解与总结任务上的不足，也对整体性能有一定的影响。

洞悉问题是进步的第一步，本文重点从 embedding 与 LLM 两个角度来剖析 langchain + 开源大模型搭建智能问答系统性能下降的原因，下篇也将从这两个角度逐步分析如何基于 lanchain + 开源大模型搭建高性能智能问答系统。

**引文**

[1] Brown T, Mann B, Ryder N, et al. Language models are few-shot learners[J]. Advances in neural information processing systems, 2020, 33: 1877-1901.

[2] Bommasani R, Hudson D A, Adeli E, et al. On the opportunities and risks of foundation models[J]. arXiv preprint arXiv:2108.07258, 2021.

[3] [GitHub - hwchase17/langchain: ⚡ Building applications with LLMs through composability ⚡](https://github.com/hwchase17/langchain)

[4] [GitHub - milvus-io/milvus: A cloud-native vector database, storage for next generation AI applications](https://github.com/milvus-io/milvus)

点击下方卡片进入公众号

回复：**2023红包封面**

可以抽奖最新红包封面

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvatAdHdXLwSMplPmIoBmUSh0Miap1uU6astvkqFib1DjQIcQ4Sib361tiaTkTjoLEcVVLhY6WkmZy4e9hg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/j3gficicyOvasOHYuGEic5USJwXGgWfxiaIXz2uxcnbFsTuYvRdoias1ajkEa7Qd81r31CJCMQ8OK6YfMYjw2OXz3EA/640?wx_fmt=gif)