---
title: 'AI改变工作：一天内打造专属于你自己的RAG'
company: DataFun
tag: 问答/RAG
date: 2024-11-21
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247752221&idx=2&sn=3223ef32ba051e733a45ae99892ad868&chksm=fbd8a871ccaf2167815dfdf717583f26a6e2fe9263e7e6857b622f93fb9947b2ddbe7589b009#rd
account: DataFunTalk
origin: wechat-mp
---
# 

# 转自 | AI搜索引擎

**![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzicG4JNibg4fM4icRVwXP5UmibMEaiaiapF9TBxMcG8Aguyicy2ica6QzY0gjnzMZudFHyibWhWXhbIMJdC6w/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaRyTXPribtoF2zB90pHPFZPOViaSVw6W5oyAQl5LrtIHXnM6DLG3Pk3EEA4eXbG5LIicpGGO9Xz49ibg/640?wx_fmt=png&from=appmsg)

**导读** 在人工智能技术飞速发展的今天，AI搜索引擎和RAG（Retrieval-Augmented Generation）技术正在重塑我们的工作方式。本文将带您深入了解四个关键的AI工具和平台，它们可以帮助您在一天之内构建起专属的RAG系统，从而提升工作效率和智能决策能力。

**全文目录：**

1. RagFlow

2. MaxKB

3. FastGPT

4. Dify

**01**

**RagFlow**

## 

RAGFlow 是一个开源的 RAG（Retrieval-Augmented Generation）引擎，专注于深度文档理解。它为不同规模的企业和个人用户提供了一套简化的RAG工作流程。

官网链接：https://ragflow.io/

Github：https://github.com/infiniflow/ragflow/blob/main

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YWfMaLXaPBb8cG6Sy2Jibb18bIq4gDsXmkWUv7l9RlibCicPz0uZO7DBvg/640?wx_fmt=png&from=appmsg)

### 

1.1 简介

**1. 模板驱动的文本处理：**

* 提供智能且可控的文本切片技术。
* 多种文本模板可供选择，以增强文本处理的灵活性和可解释性。

**2. 降低幻觉风险：**

* 实现文本处理过程的可视化，并允许手动调整。
* 确保答案的可靠性，通过提供关键引用快照和支持追溯来源来减少幻觉（hallucination）。

**3. 异构数据源兼容性：**

* 支持多种文件类型，包括 word 文档、ppt、excel表格、txt文件、图片、pdf、影印件、复印件、结构化数据和网页等，以适应不同数据源。

**4. 自动化RAG工作流：**

* 提供全面优化的 RAG 工作流，适用于从个人到大型企业的多种生态系统。
* 支持配置大型语言模型（LLM）和向量模型。
* 采用多路召回和融合重排序技术。
* 提供易于使用的API，方便集成到各种企业系统中。

### 1.2 系统架构

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YiaBkjWdTaSkO1g4263sGgf9bjmq4N56lqfiaWenFMyTaMDAuvcMuZQdA/640?wx_fmt=png&from=appmsg)

**02**

**MaxKB**

MaxKB，即Max Knowledge Base，是一款开源的知识库问答系统，它依托于强大的LLM（大型语言模型）技术，致力于成为企业智能的中枢神经。

官网链接：https://maxkb.cn/

Github：https://github.com/1panel-dev/MaxKB

### **2.1 简介**

**1. 即时可用：**系统支持直接上传文件和自动抓取在线文档，具备文本自动分割、向量化处理以及RAG（检索增强生成）功能，提供流畅的智能问答体验。

**2. 集成便捷：**系统能够无需编码即可快速集成到现有的第三方业务系统中，赋予系统智能问答的能力，从而提升用户满意度。

**3. 配置灵活：**系统内建强大的工作流引擎，能够自定义AI工作流程，以适应复杂的业务需求。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YMYHbATriaXEIGenGo2AZrflhTDSMsDUKMZCBKKjOCWLNgYo3L1f7vDw/640?wx_fmt=png&from=appmsg)

**4. 模型兼容性：**系统支持连接多种大型语言模型，包括本地私有模型（如Llama 3、Qwen 2等）、国内公共模型（如通义千问、智谱AI、百度千帆、Kimi、DeepSeek等）以及国际公共模型（如OpenAI、Azure OpenAI、Gemini等）。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YNgVTLUmwkVquTpia2AoCmbEK0taRMxZSup6N9WZRkvlKgyrjVPHpibwQ/640?wx_fmt=png&from=appmsg)

### 2.2 技术框架和系统架构

1. 前端：Vue、logicflow

2. 后端：Python / Django

3. Langchain：Langchain

4. 向量数据库：PgSQL / pgvector

5. 大模型：Ollama、Azure OpenAI、OpenAI、Qwen、Kimi、Qianfan、Spark、Gemini、DeepSeek等。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YpjNGv3gFibyEKb94JkOK0Xf7bbia944od7j43YXqHZcQyGMniavD1V8NA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9Yo6mfEgxFkicALhaaqldcZNHD27jX3f1yoglmy9sxiazpZc9yYmfISIicQ/640?wx_fmt=png&from=appmsg)

**03**

**FastGPT**

FastGPT是一个高效的平台，专注于知识库的构建和自动化工作流程的管理。

官网链接：https://fastgpt.in/

Github：https://github.com/labring/FastGPT

### 

3.1 简介

**1. 用户友好：**提供直观的可视化操作界面，简化了用户操作。

**2. 数据处理：**支持自动化的数据预处理，减轻了准备工作的负担。

**3. 工作流编排：**基于Flow模块，允许用户灵活编排工作流程。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YZqd8Bvia0hO8TYAfGmuVA0x4mYeeC6wyqsfaicD28U3rkQ5yN6ntSXNg/640?wx_fmt=png&from=appmsg)

**4. RAG系统构建：**支持快速创建RAG（检索增强生成）系统，无需复杂的编程知识。

**5. 自动化功能：**提供自动化工作流程，简化了RAG系统的开发和应用过程。

### 3.2 系统架构

项目技术栈：NextJs + TS + ChakraUI + MongoDB + PostgreSQL (PG Vector 插件)/Milvus

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9Y85KueWASa77GcFaYmXyfkDSuKZOcJibBfXSe1pZX41FKq0JBPEtGM2Q/640?wx_fmt=png&from=appmsg)

**04**

**Dify**

Dify是一个开源的LLM应用开发平台，它结合了后端即服务（Backend as Service）和LLMOps的概念，旨在帮助开发者迅速构建生产级别的生成式AI应用。该平台的独特之处在于，它不仅面向技术人员，还使得非技术背景的用户也能轻松参与到AI应用的设计和数据管理中。

官网链接：https://dify.ai/zh

Github：https://github.com/langgenius/dify

### 

4.1 简介

**1. 工作流构建：**在可视化画布上设计和测试高效的AI工作流程，集成了丰富的功能。

**2. 模型兼容性：**系统能够无缝集成数百种专有和开源的大型语言模型（LLMs），以及数十种推理服务提供商和自托管解决方案，包括GPT、Mistral、Llama3以及与OpenAI API兼容的模型。

**3. Prompt IDE：**提供了一个直观的界面，用于创建提示、比较模型性能，并为聊天应用添加文本转语音等额外功能。

**4. RAG流程：**提供全面的RAG功能，从文档摄入到检索，支持直接从PDF、PPT等常见文档格式中提取文本。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9Ycer2R9vF8jWUu487BgaDbtNhB55H1AJU7ubxH4H6RibMGW0eWp3VmXA/640?wx_fmt=png&from=appmsg)

**5. Agent智能体：**允许基于LLM函数调用或ReAct定义Agent，并为其添加预构建或自定义工具。Dify为AI Agent提供了50多种内置工具，包括谷歌搜索、DELL·E、Stable Diffusion和WolframAlpha等。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YkJpqTRDRA9DshMjqgoLEMdx4AxV7Iz2iat6zNnCd3rPyQOVvtVia2M6w/640?wx_fmt=png&from=appmsg)

**6. LLMOps：**能够监控和分析应用程序日志和性能随时间变化，根据生产数据和标注持续优化提示、数据集和模型。

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9Y19oWRicV1b6ibgiatTl90OF60v6QAoqv1CMHjpwXBkVyjz93b1kfL1GmQ/640?wx_fmt=png&from=appmsg)

**7. 后端即服务：**Dify的所有功能都配备了相应的API，使得Dify可以轻松集成到您的业务逻辑中。

4.2 系统架构

![](https://mmbiz.qpic.cn/mmbiz_png/k47iawfCYibWGJvVibLricG4pCIB3hWluB9YAcu46RRKuaqW6zsEeEiaXNJEUG912snrtxYiaa3LbHzm6AetAP3JX9vw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhc4Zib4bVnO2KB1BxwPFrDO2OfGHMLwHDJUSicVzk4NxBX0bLNGVgpSBS1d8WucjQNU6OD8G89GpiaQ/640?wx_fmt=png&from=appmsg)

往期推荐

[京东数据架构解析：供应链效率提升与决策优化策略](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751946&idx=1&sn=568f642db0e3f1d9b372aebaa2e1e0fc&chksm=fbd8ab66ccaf22701991d0db028008e24db919752388eeb59985622320cb351d82290b7ccff5&scene=21#wechat_redirect)

[大模型推理之显存优化探索实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751886&idx=1&sn=8b7987c4f169495ba031e5aee85f6ec7&chksm=fbd8aaa2ccaf23b4ecc1c03996367b00dc36ed96a7c7f27b864a1999eec6f9b15c91025cc3e4&scene=21#wechat_redirect)

[吴恩达最新观点：LLM的下一个新兴方向是Agentic AI](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751866&idx=2&sn=0e36e4386c339252b420722e9af57219&chksm=fbd8aad6ccaf23c0673554da89f66611abb800dbdf557b461205ae3832e741731cb7957e00e4&scene=21#wechat_redirect)

[蚂蚁集团、网商银行统一动态纠偏框架，非随机缺失问题优化新视角](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751725&idx=1&sn=66ef8eea07e8488ad4dfd16fca7f014c&chksm=fbd8aa41ccaf235724ef67a833c3a41b44cc9626f3b814bfed16ce44a3a113f4f03990a0542e&scene=21#wechat_redirect)

[大模型时代下的私有数据安全与利用](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751482&idx=1&sn=2e94a3b86c4da2590044565cf7d191e8&chksm=fbd8a556ccaf2c4028781f7d8870b141bdf0275e7cd83d1384b791983b1ee523881f9010e16f&scene=21#wechat_redirect)

[通过LLMOps实现生成式AI应用运营化实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751365&idx=3&sn=e9f185c500b99c82865037ac753ad5e3&chksm=fbd8a4a9ccaf2dbf57a466ed1525e449941ffb6a11e4be06aeeb7552a6c46d2a02d4392b670b&scene=21#wechat_redirect)

[对话Nvidia黄仁勋：机器学习不仅是关于软件，而是涉及整个数据管道；机器学习的飞轮效应是最重要的](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751218&idx=1&sn=0946cbc5a5c263eaa113029286467bff&chksm=fbd8a45eccaf2d4814e9822a583fc209ed16b15a7c1e7b98f67afcb81e40e8a41bd234e97461&scene=21#wechat_redirect)

[李彦宏：大模型幻觉基本消除，这是只靠想法就能赚钱时代](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247751165&idx=2&sn=52dc8faa4bdd8d80cf95630ad260ee9d&chksm=fbd8a791ccaf2e87f028d367653583eb803cf463ad775861966f66c3b63e61dc0ee353058789&scene=21#wechat_redirect)

[百度沧海·存储统一技术底座架构演进](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247750930&idx=1&sn=d852f0f85327ef8251eb8d7b976efe4b&chksm=fbd8a77eccaf2e68eaa3435426fc67ec77bcb2f0868e55f8e33b1aaeed239338628fed531664&scene=21#wechat_redirect)

[翁荔B站分享原文：AI安全与“培养”之道](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247750818&idx=1&sn=c8fc66f32677605f860da0686144fd00&chksm=fbd8a6ceccaf2fd8c4189fd70e70b7261027745be156467343c1c6435fbbebb386c49fff4ae4&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640?wx_fmt=png)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640?wx_fmt=png)