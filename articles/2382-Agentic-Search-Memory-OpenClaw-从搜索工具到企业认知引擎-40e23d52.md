---
title: 'Agentic Search + Memory：OpenClaw 从搜索工具到企业认知引擎'
company: DataFunTalk
tag: 搜索/RAG
date: 2026-08-25
url: https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw%3D%3D&mid=2247780268&idx=2&sn=bfd00cc964e1607fd9ad4624c6bb0639
account: DataFunTalk
origin: weread-history-2024
---
![]()

**导读** 企业研究的效率瓶颈已经不是‘信息不够’，而是信息泛滥带来的认知负荷，以及信息获取与信息消化之间的速度差。传统搜索可以快速返回关键词匹配结果和链接列表，但复杂研究仍需要人工理解需求、拆解问题、追踪依赖、交叉验证，再把分散的信息组织成可直接使用的结论。与此同时，每次搜索彼此独立、历史结论难以延续，也使研究过程难以持续积累。

OpenClaw 将这一过程拆成两条能力线：Agentic Search 负责提升单次研究质量，把静态检索变成 Agent 自主驱动的“理解—规划—执行—反馈”闭环；Agentic Memory 负责知识复用，把对话、事实、结论和技能转化为可持续召回的记忆。两者连接后，一次研究的结果不再只服务当前任务，还可以成为下一次研究的起点。

**主要内容包括以下几个部分：**

1. 为什么企业研究不能停留在关键词检索

2. Agentic Search：把搜索变成动态研究闭环

3. Agentic Memory：五步流程把研究结果变成可复用记忆

4. Search × Memory：让每一次研究抬高下一次的起点

分享嘉宾｜陈梦成 阿里云智能集团技术专家

内容校对｜韩珊珊

出品社区｜DataFun

---

01

为什么企业研究不能停留在关键词检索

传统链路是“输入关键词—文档列表—人工阅读—人工综合”。它面临三个直接问题：关键词匹配和链接列表只能完成被动响应，无法直接满足“得出结论”或“产出交付物”；复杂研究往往包含相互依赖的子问题，人工拆解、追踪和交叉验证会消耗大量精力；LLM 无状态，每次会话从零开始，用户偏好、历史结论会随着上下文截断而消失。

![]()

真实的研究链路则是“理解需求—拆解子问题—多源获取—交叉分析—结构化输出”。这里的关键变化，是研究从“被动响应”转向“主动推理”：先识别用户真正要解决的问题，再确定任务边界和优先级；随后构建任务计划，调用不同信息源和工具；信息返回后还要继续判断、整合和修正，而不是把检索结果直接交给用户。

![]()

要支撑这条链路，需要同时具备深度意图理解、多步推理与动态规划、多工具协同、多模态检索和标准化交付能力。意图理解负责识别领域、粒度、时效、受众等隐式约束；规划负责把复杂目标拆成依赖明确的子任务；工具覆盖联网搜索、爬虫、企业知识库、代码执行等能力；PDF、图表、视频等内容还需要统一感知和整合；最终再通过 Skills、ACP 等方式向外围系统提供标准化能力。

![]()

在这一结构中，Agentic Search 与 Agentic Memory 分工明确。Agentic Search 通过联网搜索、爬虫、BrowserUse、多模态知识库等能力解决“这一次研究能否做好”；Agentic Memory 通过事实提取、向量检索、冲突判别等机制解决“这一次研究能否沉淀并在下一次复用”。前者保证研究质量，后者让研究结果持续积累。

![]()

两大引擎并不是相互独立的外挂能力，而是接入同一研究流程。Search 负责在当前任务中持续获取和处理信息，Memory 则在任务前后参与历史信息召回与新结果沉淀，使当前研究与过去研究发生关联。

![]()

02

Agentic Search：把搜索变成动态研究闭环

Agentic Search 的核心不是增加一次检索，而是让“理解—规划—执行—反馈”连续运行。任务首先进入深度意图理解阶段。系统拆解领域、粒度、时效、受众等约束，识别优先级；如果需求仍然模糊，则通过生产级 HITL 进行反问和澄清，把用户的一句话转化为可执行的研究目标。

随后进入多步推理与动态规划。研究目标被拆成依赖明确的子任务 DAG。没有依赖的节点可以并行，有前置关系的任务按依赖顺序执行。DAG 不只是任务清单，它直接影响整个任务的执行效果和效率。只有依赖关系被表达清楚，系统才能判断哪些任务可以同时推进、哪些必须等待前置结果。

规划也不是一次性的。执行结果可以反向触发计划重排，任务在运行过程中持续调整，形成“边做边推理”的动态闭环。工具调用同样不是把所有问题交给一个万能工具，而是在联网搜索、企业知识库、浏览器代理、IPython Sandbox、DataAgent 等能力之间选择。多个工具可以并行，同一子任务也可以通过多源信息进行交叉验证。

反馈环节负责把工具返回的结果重新转化为下一步行动依据。返回内容可能是 PDF 章节、图表数值、视频片段或表格数据，系统需要先进行结构化感知，提炼有效信息写回上下文，再判断继续、修正还是终止。闭环因此不只是“再调一次工具”，而是“理解结果—形成判断—继续行动”。

![]()

为了让这条链路进入生产环境，工程架构分为服务编排层 AgentManager、执行引擎层 AgentScope 和运行环境层 Sandbox。配套能力包括开源 ACP 协议、断点重连与级联中断、多级并发、生产级 HITL、OpenTelemetry 全链路可视化、数据与内容安全、降级与限流机制、无 AK 鉴权机制。架构同时考虑灵活性和可扩展性，新 Agent 框架可以尽量减少对现有架构的改动；运行环境则通过 Sandbox 隔离，降低任务之间的相互干扰。

![]()

多模态处理是研究闭环能否稳定工作的基础环节。系统支持 pdf、doc、docx、ppt、video 等格式，既需要解决大文件解析，也要保证文件内部的数据定位准确。一个演示同时输入四份不同格式的中考数学试卷，文档内部包含文本、图片和表格，任务需要完成解析、问题定位和推理，整体执行约三分钟。

另一个长文件案例输入约 169 页 PDF，围绕其中一页表格提问，任务在一分多钟内完成，并定位到相应信息、解析表格内容，核对结果正确。两个案例强调的并不是“文件能否打开”，而是从异构非结构化内容解析，到问题召回、文件内定位，再到基于内容完成回答的一整条链路。

多格式解析最终服务于研究结果的可信度。文件处理需要同时兼顾格式覆盖、解析性能、大文件能力和定位精度；只有真正找到问题对应的数据，后续报告才能建立在明确的信息基础上。

![]()

多模态能力还延伸到知识库索引和召回。视频数据经过离线索引后，在线提问可以结合字幕和关键帧进行召回。《瑞克和莫蒂》第一季被整体导入知识库后，系统可以围绕具体问题找到相关字幕与关键帧，并以多模态方式返回信息。

这条链路覆盖从离线解析、索引到在线检索和结果组织。对于视频数据，召回对象不再只是一个完整视频文件，而可以进一步落到字幕信息和关键帧，使多模态知识能够进入后续分析过程。

![]()

信息源也不局限于单一知识库。私域数据包括知识库、用户文件和数据库，公域数据可以通过 websearch、crawler、BrowserUse 获取；还可以与 DMS DataAgent 等其他 Agent 打通。多路信息完成召回后，再进入提取、整合与加载流程，为最终报告提供统一材料。

![]()

03

Agentic Memory：五步流程把研究结果变成可复用记忆

没有记忆时，用户需要不断重复背景，历史结论难以关联新任务，经验也无法沉淀为可复用资产。Agentic Memory 用 Extract、Embed、Store、Retrieve、Fuse 五步流程处理这一问题。

![]()

Extract 负责从对话中提取关键事实，由 LLM 识别实体、偏好、结论等高价值信息；Embed 通过 Embedding Engine 生成统一向量表示，同一套 Embedding 同时服务事实记忆和技能库；Store 使用 ElasticSearch VectorStore 持久化向量和原始文本，支持增量写入，并通过 LLM 冲突判别减少矛盾事实并存。

在线阶段由 Retrieve 和 Fuse 完成。用户 query 向量化后，在 ElasticSearch 中执行 BM25 + KNN 多路融合召回，覆盖 Memory、Skill 和知识库；召回结果可以经过 Reranker 排序，再注入 Agent 上下文，与当前任务信息融合成增强 Prompt。由此形成从离线提取、向量化和存储，到在线召回、排序与融合的完整链路。

![]()

OpenClaw 的记忆体系还需要跨越单次上下文窗口。在同一会话内，Memory 可以扩展上下文利用；跨会话时可以继续使用历史信息；在同一 UID 下，跨设备也可以保持记忆可见和可用。接入方式包括 Skills 和插件机制，使 Memory 可以直接进入实际任务流程，而不是停留在独立的存储模块。

![]()

04

Search × Memory：让每一次研究抬高下一次的起点

Agentic Search 和 Agentic Memory 连接后，研究任务会形成连续飞轮：任务进入后由 Agent 自主规划和执行，得到研究结论；结论写入 Memory；下一次任务自动召回历史信息，以更高的起点开始；新的结果再次写回记忆。用户反馈还会继续推动模型和策略更新，使 Search 与 Memory 形成双向增强。

这条飞轮对应三个阶段。初期主要减少上下文重建；中期通过历史结论持续复用，提高研究的一致性和深度；长期则把一次次研究中积累的事实、结论、偏好和技能沉淀为企业专有认知资产。积累的对象不只是某一次回答，而是能够继续参与后续任务的研究成果。

![]()

从搜索工具到 Agentic Search，是从“被动”走向“主动”；加入 Agentic Memory 后，是从“无状态”走向“有记忆”；Search 与 Memory 相互反哺后，又从“独立积累”走向“双向增强”。当这套机制进入团队协作，研究能力也从个人助手进一步延伸到团队资产。

最终，搜索不再止于找到文档，记忆也不只是保存聊天记录。两者共同承担的是一条持续运行的研究基础设施：获取信息、理解需求、规划执行、形成结果，再把有效结果写入记忆并用于下一次任务。研究质量与知识复用因此被放进同一个循环，每一次搜索都能够成为后续研究继续积累的起点。

![]()

**以上就是本次分享的内容，谢谢大家。**

复制链接开通Agentic Search：https://help.aliyun.com/zh/open-search/search-platform/getting-started/agentic-search?spm=a2c4g.11186623.0.0.61a242a78j4xRG

钉钉扫码加入群聊

![]()

![]()

往期推荐

[OpenAI Codex 负责人亲自回应：模型没变，Agent 为什么突然更烧 Token？](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780236&idx=1&sn=4302549f7f9e799f0aa68b1d3e684205&scene=21#wechat_redirect)

[GitHub万星项目核心开发者：从NL2SQL到NL2Pipeline，Data Engineering Agent该怎么建](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780236&idx=2&sn=a39d824f1a97ed70e0a0b331c1565d56&scene=21#wechat_redirect)

[别再给 Agent 默认最强模型了：Databricks 开始同时选择 Model 和 Harness](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780236&idx=3&sn=94a89993066f33de37cbde8f7d863d3a&scene=21#wechat_redirect)

[Google前首席科学家 Jeff Dean：模型越强，真正值钱的反而越在“模型之外”](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780210&idx=1&sn=defb2a4d4de07399185da90c9f74af3a&scene=21#wechat_redirect)

[Palantir把Claude、OpenAI和Google的Agent接到了Ontology之上](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780210&idx=3&sn=fcbf267b82dbd14a34cb563d7c822f50&scene=21#wechat_redirect)

[资本开始买“语义层”了：Graphwise 获控股投资，AI Agent 的新基础设施正在成形](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780203&idx=3&sn=d550398a08db949f9d09806681a4d46e&scene=21#wechat_redirect)

[OpenAI 开源 Codex Harness：Claude、Google、DeepSeek 都押注了同一层](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780150&idx=1&sn=78c0f675ab2e4fe35b47a441e1c608a9&scene=21#wechat_redirect)

[Palantir开始给Agent算“工时”了：企业Agent正在进入可观测时代](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780150&idx=3&sn=32fa27c57d815794fbd310c0e3816863&scene=21#wechat_redirect)

[资本开始买“语义层”了：Graphwise 获控股投资，AI Agent 的新基础设施正在成形](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780067&idx=2&sn=4547d3e24b7d4c47b064bcb0b9fdd373&scene=21#wechat_redirect)

[Semantic Layer正在变质：Google开始把“关系”塞进Agent上下文](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247780041&idx=2&sn=9bd4f1936f4b5960b3d61e7500b6d18e&scene=21#wechat_redirect)

![]()

点个在看你最好看

SPRING HAS ARRIVED

![]()