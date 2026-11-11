---
title: 'Elastic 面向 Agent 的搜索范式变迁与上下文工程！'
company: DataFun
tag: 搜索
date: 2026-07-01
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247778536&idx=1&sn=0b82df9d3596b12ef8c3898d19997917&chksm=fbdb3284ccacbb92a2638b333d720d0c9e4c0ecc4ac63056cc54843ba957393958ff011b6475#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/x9zuJeYhAAwdPicyDiaSJL1aca7tfbMJLYHibsB607yElRsmqIygETNB2Qha94YfA1HiaaVOLR1tPzzPjKDOSv6cm4QGS1B14eibj1METjJbyPwg/640?wx_fmt=png&from=appmsg)

07 月 24-25 日，Elastic 将出席 DataFun 举办的「Agentic AI Summit 超级智能体系统架构峰会·深圳站」，并邀请 Elastic 首席布道师刘晓国老师在「企业级 Agent 开发工具链」论坛，分享「Elastic MCP 及 Agentic AI - 构建可信、上下文感知能力的搜索」，详细介绍 Elastic 面向 Agent 的搜索范式变迁与上下文工程，如何通过 Elastic MCP 做自然语言查询，以及如何使用 AI Agent builder 创建 tools/skills 及 Agents 等内容。感兴趣的小伙伴，欢迎扫码参与本次大会：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/x9zuJeYhAAwKaofMqibSgKOFxib5RM1719A8s63qFcFtXreTMum64RpWRvuOJDVVRZw4RiaVmicBnb8Cm0icMXicW7gY1a5Rib0sOqBIc5762r90WU/640?wx_fmt=png&from=appmsg)

详细介绍：

刘晓国 Elastic 首席布道师

个人介绍：中国社区首席布道师。新加坡国立大学硕士，西北工业大学本硕。曾就职于新加坡科技，康柏电脑，通用汽车，爱立信，诺基亚，Linaro 非营利组织 (Linux for ARM)，Ubuntu，Vantiq 等企业。从事过电脑设计，汽车电子，计算机操作系统，通信，云实时事件处理等。从爱立信开始，诺基亚，Ubuntu 到现在的 Elastic，从事社区工作有将近 20 年的经历。喜欢分享自己所学到的知识。坚信帮助别人就是帮助自己。希望和大家一起分享及学习。欢迎大家来参阅 Elastic 官方中文博客 https://elasticstack.blog.csdn.net

分享时间：07 月 25 日 10:25 - 11:10

演讲主题：Elastic MCP 及 Agentic AI - 构建可信、上下文感知能力的搜索

内容介绍：Elasticsearch 正从全球领先的搜索引擎进化为 Agentic AI 的核心基础设施。 针对大语言模型（LLM）知识静态且缺乏实时数据访问能力的痛点，Elastic 推出了 MCP（模型上下文协议），旨在将孤立的推理引擎与外部世界无缝连接。依托 Elasticsearch 强大的向量搜索与混合搜索能力，企业可以构建具备 “上下文感知” 的高质量检索基础，并将对话历史作为长期记忆存储，有效消除 AI 幻觉。高效及准确的上下文感知是构建 AI agents 的关键因素。创建 Agents 及 tools 对于很多企业应用来说不是很容易的一件事。随着最新 Elastic 版本的推出，开发者可以在弹指之间通过 AI Agent builder 轻松创建 tools, skills 及 Agents。

这些 Agents 可以让用户轻松地使用人类自然语言对企业数据进行分析查询总结。开发者可以通过 ES|QL (类似于 SQL 查询)创建工具。对数据进行查询，统计分析，多表格关联查询形成丰富的精确的上下文供大模型进行使用；使用 MCP 来创建工具，调用其它专业/专用 MCP 服务器所提供的工具给 Elastic AI agents；通过 Workflow 来创建工具，自动化工作流。

开发者可以通过 workflow 来完成清晰而明确的工作流执行，这其中包括对已经创建的 agents 调用，对数据的管理（删除，生成等），分类，通知发送，外部 API 的调用（地理编码，天气查询等）等。这些都可以为大模型提供精确感知的上下文，从而达到更加精确的控制。Elastic Workflows（工作流）与 Elastic Agent Builder（智能体构建器）允许你将确定性的自动化流程与对话式推理能力相结合。通过在工作流执行过程中直接调用 AI 智能体，你可以将其视为一个 “推理引擎”，用于对数据进行摘要、对事件进行分类或做出决策，随后将结果传递给自动化流程中的下一个环节。AI Agents 也运行 skills。它为 agent 提供针对特定任务类型的专业能力（instructions/tools/context）。 Elastic Kibana 集成的 MCP 及 A2A 服务器可供第三方应用通过 API 进行调用。

演讲提纲：

1. 搜索市场演变

· 搜索的变迁

· 把企业数据提供给 agent 是挑战的

· 智能体时代，搜索比以往任何时候都更相关

2. Elastic MCP

· Elastic MCP 服务器介绍

· 定制 MCP 服务器

· Demo：使用 Elastic MCP 及 定制 MCP 进行自然语言查询

3. AI agents

· 什么是 Agents

· 为什么我们需要上下文工程

· Agent builder 架构

· Elastic Workflows 介绍

· Demo：使用 AI Agent builder 创建 tools/skills 及 Agents

![](https://mmbiz.qpic.cn/sz_mmbiz_png/x9zuJeYhAAx9BXkevic0GEfEzSWHkeZuRGGW6JyoF35DstDfVtrCwuaibcfVmNUap7Y7ckjaEEE35PlziaDOaSCpib6VficC9vxrFZvCsricWPSLs/640?wx_fmt=png&from=appmsg)

扫码报名