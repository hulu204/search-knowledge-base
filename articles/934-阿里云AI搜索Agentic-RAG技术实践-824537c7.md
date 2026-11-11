---
title: '阿里云AI搜索Agentic RAG技术实践'
company: DataFun
tag: 问答/RAG
date: 2025-11-18
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247772209&idx=4&sn=717ecdff2a2e6b9b38e66a4b44638664&chksm=fbdb1a5dccac934ba637848d6e9bc1fa91ccb10f3a4765e1b1dddc2d36d719dcb7c06fb9a928#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhTia191MRUMDiacXVJ4Y3YS8Xibicn0O9liacYp7Aia6iaYKqDSicvuWPKibvibUGXGET00pxW6Jiaicn07KRGjQ/640?wx_fmt=png&from=appmsg)

《阿里云AI搜索Agentic RAG技术实践》

本文基于阿里云AI搜索负责人邢少敏的技术分享，系统阐述了阿里云AI搜索在应对高并发、多模态数据及复杂多跳查询等场景下的技术挑战与解决方案。文章重点解析了Agentic RAG架构从单Agent到多Agent系统的演进路径，通过规划、检索、生成等多模块协作实现复杂意图的精准理解与响应。文中详细探讨了多路检索链路的设计，包括如何通过向量、文本、数据库与图数据的混合召回策略提升查询覆盖率和准确性。此外，全文还涵盖了自研引擎的优化细节、GPU加速在索引构建与查询阶段的量化收益对比，以及NL2SQL、多模态搜索等扩展能力的实现方案，读者可通过原文获取完整的架构图、性能评估数据及产品落地案例。

文章来自《智能体架构与实践：构建下一代推荐与搜索系统》电子书

识别下方二维码进群即可领取电子书

![图片](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhIvR2GdBqAqicJvjpadj48pLvZkAcr93jeyLkP6noPqbyibIjmGsLXBcI0NUXUYWEvz3SM3dnyBrtw/640?wx_fmt=png&from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

《华为诺亚解析：推荐系统的技术演进及大模型应用实践》

本文系统回顾了推荐系统从深度学习到大语言模型（LLM）及AI Agent时代的技术演进，重点探讨了如何解决传统推荐系统中隐式反馈噪声大、语义理解能力不足以及用户意图挖掘困难等核心挑战。文章通过分析列表式与对话式两种推荐形态的演变路径，详细介绍了将大语言模型作为特征增强器与推荐流程组件融合的技术方案，其中以华为诺亚方舟实验室的KAR项目为例，重点阐释了通过因式分解提示技术和多专家知识适配器实现语义知识向推荐嵌入空间的高效映射。文中还深入分析了知识适配器中多专家网络的设计如何平衡文本特征维度与推荐模型实时性要求这一关键实现细节。此外，全文进一步扩展探讨了对话推荐系统中LLM的提示工程与微调策略、AI Agent的多能力协同架构，以及跨平台推荐生态的未来方向，完整内容包含具体模型结构图、AUC提升1.5%的量化结果及线上AB测试数据，读者可参考原文获取详细技术实现与实验分析。

文章来自《智能体架构与实践：构建下一代推荐与搜索系统》电子书

识别下方二维码进群即可领取电子书

![图片](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhIvR2GdBqAqicJvjpadj48pLvZkAcr93jeyLkP6noPqbyibIjmGsLXBcI0NUXUYWEvz3SM3dnyBrtw/640?wx_fmt=png&from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

GRAB：百度推荐广告生成排序模型技术实践

本文系统性地阐述了百度商业技术团队为突破传统深度学习推荐模型（DLRM）的性能瓶颈，在广告推荐排序场景中设计并全量上线的生成式推荐排序模型GRAB（Generative Ranking for Ads at Baidu）。文章重点解决了传统模型在特征工程边际效益、序列表征信息损失及泛化推理能力方面面临的技术挑战。

核心方案借鉴大语言模型（LLM）的“Scaling Law”与Transformer架构，将用户历史行为与目标广告在统一表征空间中进行端到端的生成式序列建模，以替代依赖大规模离散特征与人工特征工程的传统范式。文中重点剖析了为适配推荐场景特性所设计的Q-Aware RAB因果注意力机制，该机制通过查询感知的相对偏置，实现了对复杂交互与时间信号的自适应建模。

此外，全文还详细阐述了针对训练效率与过拟合问题设计的STS两阶段训练算法、应对模型热启动的异构Token表征与双Loss堆叠策略，以及保障高并发在线推理的KV-Cache等关键技术细节与优化方案，并提供了模型全量上线后取得的量化业务收益。读者可通过阅读原文进一步了解完整的架构设计、与其他技术路径的对比分析及问答环节中的实践探讨。

文章来自《智能体架构与实践：构建下一代推荐与搜索系统》电子书

识别下方二维码进群即可领取电子书

![图片](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhIvR2GdBqAqicJvjpadj48pLvZkAcr93jeyLkP6noPqbyibIjmGsLXBcI0NUXUYWEvz3SM3dnyBrtw/640?wx_fmt=png&from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

目录： 

1. 多智能体交互系统赋能 AI 向善新实践

2. 基于大模型智能体的知识发现与数据科学应用

3. 顺丰科技：多智能体系统（OpenAI Swarm）的可观测性研究与实践

4. 华为诺亚解析：推荐系统的技术演进及大模型应用实践

5. GRAB：百度推荐广告生成排序模型技术实践

6. 运用 Elasticsearch 进行向量搜索及创建 RAG 应用

7. 阿里云AI搜索Agentic RAG技术实践

8. 从大数据到大模型：搜索推荐技术的前沿探索

![图片](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjGBZJxiaKBdIicl8ZoDgAlnGYjmlohBU0kX5DpW4VktECCOPeXKFwdZyzibEZltMy2XzUndIYXmaEpA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)