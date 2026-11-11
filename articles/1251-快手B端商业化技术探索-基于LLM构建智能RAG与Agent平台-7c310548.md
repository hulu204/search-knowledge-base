---
title: '快手B端商业化技术探索：基于LLM构建智能RAG与Agent平台'
company: 快手
tag: 问答/RAG
date: 2024-09-20
url: http://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247490759&idx=1&sn=6dc3ac8a5126bb5edee9b9a508fd832a&chksm=ceb83c1df9cfb50bd471321cc4353f23e1eca234e2496ef2f54211066f0bc4e884dee18187b0#rd
account: 快手技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpWVF4VKQ1wpuB9K5UQ6vuYgB9JScIGibdBJloTp6cM8pZCUabZ6TiaGbg/640?wx_fmt=png)

**导读**

大模型技术正以前所未有的速度与各领域融合，为各行各业带来变革，围绕快手B端商业化的业务场景，本文详细阐述了构建基于LLM的Agent技术平台的策略、挑战及解决方案，为您带来宝贵的见解与启示。

**一、大模型应用建设背景**

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg)

快手商业化业务中台，作为核心支撑，全面赋能内部的一线销售、运营团队，以及外部的代理商和服务商。面对大模型技术的浪潮，我们精准捕捉智能化转型的先机。面对众多可选择的技术路径，经过我们进行了深入剖析与审慎考量，最终决定将战略重心聚焦于RAG与Agent技术的研发与应用。

RAG，作为我们的助手，通过检索、增强与生成三大环节的紧密协作，精准匹配并高效解决用户查询，显著提升信息处理的效率与质量。而Agent技术，则扮演着智能体的角色，它不仅具备高度的自主性与交互能力，还能在复杂多变的业务环境中灵活应对，执行多样化的任务。

在这一过程中，我们果断舍弃了与当前业务场景关联度不高或短期内难以产生显著效益的技术方向，如AIGC的某些特定应用、过于细分的垂直领域探索等，以确保资源能够集中投入到RAG与Agent技术的深耕细作之中。通过此次聚焦，我们能够加速推动快手商业化业务的智能化进程，为一线团队提供更加智能、高效、便捷的工作体验，同时也为公司创造更加卓越的商业价值与社会效益。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNKD8TZngcfib4iaWepGn3K4m4FM9EH9UbCtTZl3LEf17JxSGes3eFosickg/640?from=appmsg&wx_fmt=png)

**快手商业化B端业务场景**

**二、SalesCopilot技术平台的诞生与演进**

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg)

***SalesCopilot平台诞生的背景***

![](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif)

在当前的商业环境中，销运团队作为企业连接市场与客户的桥梁，面临着众多挑战。然而，随着业务规模扩大，一系列痛点逐渐显现，亟待通过产品建设来加以解决。

* 知识碎片化：业务多元化发展，各类重要产品知识、营销通案、政策、流程文档等关键信息，往往未能有效整合零散地分布在不同的团队或个人手中，进而导致信息获取不便利。
* 问题解决慢：在日常工作中，销运团队需要与多个部门或团队进行协作。然而，由于架构和人员的变动，当面临问题时无法快速定位到对接人，加之人工响应的时效性难以保证，这进一步加剧了问题解决效率。
* 销运支持资源有限：即便增加人力也无法赶上日益增长的业务需求，且宝贵的经验与专业知识难以得到有效传播与深入交流。

针对上述痛点，快手商业化团队急需开发一款集知识管理、团队协作与智能答疑于一体的产品。基于此，第一个应用销帮帮智能客服应运而生。在智能化升级的过程中，我们逐步沉淀打造了SalesCopilot技术平台。在项目的推进过程中，逐渐意识到，通过实践积累经验，我们有能力并且有责任构建一个能够支撑多元化智能应用的技术底座。因此，我们采取了双轨并行的策略：一方面，持续孵化并优化智能客服等应用，另一方面，则为技术平台的SaaS架构布局打下坚实基础。

***SalesCopilot系统架构***

![](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif)

下图为SalesCopilot系统架构图，它展现了我们这一愿景的具体实现路径，其概括为“三横一纵”。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNK6aShVBMntC7cRRicDzIPQiaWLytcPJR52wH9ZhFTqfga98eibKulCrh0g/640?from=appmsg&wx_fmt=png)

**SalesCopilot技术平台**

在“三横”结构中，最底层且最为核心的是AI引擎层，这一层是技术平台的智慧大脑，集成了RAG等前沿技术，实现了知识的检索、增强与生成，为上层应用提供了强大的智能支撑。同时，业务意图（Agent）模块作为桥梁，精准对接业务需求与底层AI能力，确保系统的灵活性与适应性。此外，效果评测中心及语义向量相关组件的加入，进一步提升了AI引擎的性能与精确度。

第二层是ChatHub层，它专注于智能客服场景，提供了一个可扩展的框架，用于集成并优化多种智能客服能力。这一设计既满足了当前业务需求，更为未来功能的拓展预留了充足空间。最上层则是业务应用层，它以租户为核心，实现了数据的个性化隔离与业务的灵活定制。每个租户都能在此层构建自己的专属应用，享受定制化的智能服务。而“一纵”则是指贯穿于整个架构的插件框架与多租户框架。这两个框架构成了SalesCopilot平台化的基石，它们不仅保障了系统的稳定性与可扩展性，还使得平台能够轻松应对多业务、多场景的挑战，为技术的长远发展奠定了基础。

***深入浅出AI引擎的RAG技术***

![](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif)

****LLM的局限性****

RAG是在大模型应用后，很快被大家识别和接受的技术范式，其独特之处在于对大型语言模型局限性的有效弥补，以下是大模型的局限性：

* **幻觉问题：**在自由生成文本时，可能产生与现实不符的“幻觉”内容，影响信息的准确性。
* **知识时效性问题：**模型训练成本高昂，且知识库难以实时更新，导致对新信息的反应滞后。
* **记忆容量局限：**无状态chat服务，prompt长度有限，当前模型难以保留长记忆。
* **数据安全问题：**私域数据参与训练存在不可控安全隐患。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNKIUibibVwiadOpX1zxPwjTQJ6RKMGVJ2ZCEnv0OiaiakulkEfnvtib7RpkskQ/640?from=appmsg&wx_fmt=png)

**大模型的优势与局限性**

**RAG技术链路**

RAG技术链路分为离线与在线两大核心部分：

**离线链路：**此部分包括知识构建与知识预处理，而知识构建与运营是RAG运转的基础。构建技术链路只是起点，若缺乏专业团队对知识库进行持续运营、质量把控及规模扩张，就如同汽车缺乏燃油难以驰骋。知识预处理则包括切片、Embedding等常规操作，以及快手特有的知识下钻能力，该能力能够深入挖掘知识间的关联，由于快手大部分知识都是以云文档的格式存在的，且包括对内、对外两种形式，彼此引用与扩展。通过快手自研的知识下钻技术，将原本看似独立的200篇文档扩展至1000余篇，极大地丰富了知识库的广度和深度。通过GraphRAG本地化实践，融合LLM技术与图谱技术，提升了跨chunk和跨文档的全局知识问答效果。离线链路还包含多路召回（向量检索、ES检索、GraphRAG）的强语义知识索引建构，为在线链路的业务效果提供索引数据支撑。

**在线链路：**作为RAG技术的核心执行部分，在线链路由检索（R）、向量召回（A）与生成（G）三大环节紧密组成。自多路召回策略上线以来，其效果在向量匹配上已实现了显著提升，高达70%的增幅，然而，随着用户需求的日益多样化与复杂化，对Query的深入理解与优化成为了新的挑战。用户提问的随意性与不可预测性，倒逼我们不断调整Query解析策略，提升系统对追问、反问等复杂场景的应对能力，而这些能力会慢慢成为引导这个系统进一步发展的关键点。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNKANlG63UCaF4ibShDDrUEdibG8bd6hkdToOFtMHY39usqQYW0ZsPJ23Ug/640?wx_fmt=png&from=appmsg)

#### ****RAG技术链路****

#### ****业务中的实际应用****

在实际应用中，销帮帮智能客服在12个直客行业和渠道业务部中，销售人员覆盖率达到42.8%。在知识管理方面，更是实现了质的飞跃。原本由五人维护的270余篇知识文档，在销帮帮的助力下，下钻扩展至1000余篇，知识库的丰富度与深度均得到了明显提升。此外，机器人的拦截率达到78%左右。多路召回和精排应用实施后，效果提升非常显著，在评测阶段，知识问答平均分百分比提升了70.68%。

在业务实践中，不可避免地会遭遇诸多挑战，这些挑战可大致归为以下几大类：

首先，RAG系统本身便蕴含着复杂性与深度。用户的提问往往泛化而不明确，这类提问初看之下或被视为不佳案例（Bad Case），但深入分析后，实则发现了模型需要增加追问和问题分类理解能力。漏召回与回答准确率的不足，则可通过引入多路召回与精排策略得以有效缓解，进而提升系统性能。最后是领域“黑话”带来的问题，要求我们在垂直领域内深耕细作，积累专业知识。

大模型虽强，却也并非无所不能。其总结能力的不稳定性便是一大痛点，需通过精细调整Prompt来优化。在此过程中，确保拥有可靠的评测工具至关重要，它能确保每次调整都能带来正面效果，避免在解决一个问题时引入新的问题，导致原本表现良好的案例（Good Case）反遭损害。同时，大模型在处理长上下文时的局限性也需我们关注，尝试有限多轮对话的优化路径，以更贴近用户的真实使用场景。

最后是用户需求和当前功能的不匹配。我们发现了一个显著的趋势：用户在与客服交互时，越来越多地采用先图片后提问的方式。这一现象则揭示了用户对于多模态交互的强烈需求。当前功能的局限性与用户日益增长的多元化需求之间，形成了一道亟待跨越的鸿沟。这要求我们不断创新，将图像识别、语音识别等先进技术融入产品中，以满足用户更加丰富的交互需求。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNKFLIG3VrusavWYeMrk0ePlhU5OmPia4fYpgVbia7aT5tuzHm1dYhS4mlA/640?from=appmsg&wx_fmt=png)

**业务实践中的挑战**

***Agent技术的全面解析***

![](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif)

****Agent的技术链路****

在深入探讨我们的Agent实践时，我们已超越了简单的“tool use”范畴，向着更加智能与全面的方向发展。Agent的核心价值，不仅在于其工具性应用的层面，更在于其作为连接业务与用户需求的桥梁角色。它能精准回应用户期待，高效解决用户问题，这一过程中，Agent需紧密集成于系统之中，充分利用业务接口、数据模型等核心资源。

为了实现Agent的高效运行，我们构建了一套接口与意图的schema体系。在schema中，定义了每个业务意图的名称、详尽描述及具体示例（即“shot”），这些信息对于大模型而言，是理解API逻辑、把握业务意图的关键钥匙。在实践初期，大模型在意图识别上的表现不尽如人意。一方面我们优化了Prompt，将若干意图shot融入其中；另一方面我们升级了LLM，部署了qwen2-7b，最后由于Prompt长度有限，我们对意图清单做粗排以支持300+的意图识别，之后整体的意图识别效果得到显著提升。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNK5yUNNEcFp2iaSQz00qNjHxx77pohEUacVCTmhgRaNH3ARrZ8TyibfoCQ/640?from=appmsg&wx_fmt=png)

**Agent的技术链路**

#### ****Agent的意图执行****

意图的执行策略涵盖了从简至繁的多种模式，每种模式都针对特定场景需求而设计。最基本的是单Plugin模式，它实现了意图与API的直接映射。在这种模式下，用户的简单需求（如搜索网页、查询天气）能够迅速转化为API调用，直接返回结果。

然而，在复杂多变的业务场景中，这种模式显得力不从心。面对复杂的业务逻辑，如销售场景中查询客户合同进度，这里可能涉及到这个客户是不是合法的、签的是哪个合同、签了多少钱……，我们需要引入多Plugin意图执行能力。这一能力允许我们将复杂的任务拆解为多个子任务，每个子任务由不同的Plugin处理。目前，实现这一能力主要有两种方式：一种是预定义执行逻辑，即在明确意图后，通过人工编排大模型的执行路径；另一种则是大家谈得比较多的ReAct模式，即让AI在推理过程中动态决定执行步骤。虽然推理+执行这个概念特别性感，但稳定性不佳，比如说AutoGPT最好的表现只有50%左右，直接把这套东西推到线上系统是不可接受的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNKaBMbx7tzXbOgIKxd4hwngDO8xiaXQQlS0A4rw0m3KMDYicXuRlqGZr4g/640?from=appmsg&wx_fmt=png)

**意图执行**

在业务实践中，有两种意图执行方式。其一，我们采用了自然语言处理技术，直接从用户的言语中精准捕捉其意图，并立即启动相应的执行流程。另一种方式则更为简洁一些，识别到用户的意图后，通过弹出卡片界面的方式进行确认，并快速执行最终任务。

***大模型的关键设计与效果评测***

![](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif)

另外，关于我们大模型设计的核心理念，主要聚焦于以下三点：

* **可插拔，**能根据需求快速替换或更新模型，支持多模型协作，让不同任务调用最适合的模型；
* **LSP，**LLM Specific Prompt/模型专用提示LLM各有调性，皆有适合自己的Prompt风格；
* **量化LLM，**量化大模型通过减少参数精度来降低资源需求，仅少量智能损失可跑高性能跑在CPU上。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNKHsjx8gGGfgS3y3eyN5kGOtz1k9Ric6AB6wpUaGmTQtIl2m9ZTn1rtJw/640?from=appmsg&wx_fmt=png)

**大模型的应用策略**

在探索大模型驱动的应用研发这一领域时，我们深知自己正置身于一个“不确定性”之中。每一环节，一旦与大模型紧密相连，便无可避免地伴随着效果的波动与不确定性。因此，构建一个高效、精准的评测中心，对于确保系统的可控性与效果的持续提升必不可少。我坚信，评测中心对于大模型驱动的应用研发而言，是不可或缺的基石。它赋予了我们驾驭不确定性的能力，只有如此，我们才能确保系统在不断迭代中稳步前行，真正实现效果的持续提升。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Ho9QcS5vOnRlquCIUvYiaNK64avic7wTibwALfrclsm5ficD82Al4YoFKFFPqULMsc9s9uKU46RZbDUw/640?from=appmsg&wx_fmt=png)

**效能评测中心**

**三、大模型应用研发的思考**

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg)

在此，我总结了大模型应用研发过程中的四点关键思考，希望对大家有所帮助！

第一生产力：智能化技术平权。大模型技术的革新，真正实现了智能化技术的普惠与平权。大模型通过提供先进的算法和庞大的数据处理能力，使得即使是资源较少的小企业或小团队也能利用顶级的AI技术进行产品开发和业务优化。这一转变，极大地降低了技术门槛，加速了创新项目的孵化，让智能化不再是大型机构的专属，而是成为推动各行各业转型升级的强劲动力。

  

第二RAG效果提升：乘积效应。RAG效果提升是一个非常系统性的工作，要做到比较好的效果，有非常多的智能化和工程策略的事情要做，没有银弹，要抓关键细节一个个去做实做深。从Query理解到知识维护，再到多路召回策略的优化，每一个环节精细打磨，都是实现效果飞跃的关键。当效果达到70%后，则更需保持耐心与毅力，继续深挖细节，以精益求精的态度，逐步突破瓶颈，迈向更高的巅峰。

第三路径选择：从垂直细分领域开始。在开始研发大模型应用时，我们深思熟虑后决定采取一条从垂直细分领域切入的路径。这一决策并非偶然，而是基于对当前技术发展阶段和市场环境的深刻洞察。大模型技术，尽管已取得显著进展，但仍处于其发展历程的初期阶段，尚未形成成熟、标准化的应用范式。因此，盲目追求构建一个包罗万象的通用Agent平台，不仅可能因技术的不成熟而遭遇重重困难，还可能因研发周期的漫长和用户反馈的滞后，错失先机。相反，我们选择从具体、明确的垂直细分领域入手，这些领域往往具有清晰的应用场景和迫切的智能化需求。通过在这些领域内深耕细作，我们能够快速验证大模型技术的有效性，并积累宝贵的实践经验。同时，阶段性地选取具有代表性的标杆应用进行重点开发，树立行业标杆流。在这一过程中，我们同步进行架构布局，为未来的平台化发展奠定根基。

  

第四需求趋势：多模态。展望未来，多模态交互将成为Agent发展的重要趋势。这一趋势不仅符合人类自然交互的习惯，更以其信息密集、表达丰富的特点，为用户带来更为绝佳的交互体验。随着技术的不断进步与成熟，我们有理由相信，多模态能力将不断提升，为Agent的发展注入新的活力与可能。

”

欢迎加入

![](https://mmbiz.qpic.cn/mmbiz_png/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpF09GTXcEcG4Fy9SdWsPp2icyibcRsickibvTSQXgITrJPOF9bApGEbyZvg/640?wx_fmt=png)

**「我们是谁」**

快手商业化技术部/业务中台研发中心专注于为销售、运营、代理商等提供全方位支持，同时为经营管理团队提供决策和流程优化的技术平台。我们的系统包括CRM、政策预算、业绩客户开发、代理商管理、客户账号基础设施、大数据产品及大模型应用，形成销售和代理商服务客户的一站式工具箱。

我们高度重视人才发展，通过数据科学、智能AI和高效工程体系提升业务效率，推动商业化增长。团队成员享有技术培训和技能提升机会，部门致力于培养创新力与技术先进性，支持员工成长。  
  
**「我们的使命」**  
提升商业化后链路业务效率，利用卓越工程、大数据和大模型助力业绩提升。  
  
**「欢迎加入」**  
诚邀有志之士投递简历，期待您的加入！

长按识别二维码或点击阅读原文，查看具体招聘岗位及需求。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0E975sNXYZRtV62rQeDSyd86tn5N7Lpc6ibib7aT1srU2RCKVOJvgFyyBCpjcdDv7ibTRuDbHrDBZVHQ/640?wx_fmt=png&from=appmsg)

投递邮箱：mateng03@kuaishou.com  
简历命名：招聘类型-姓名-联系方式

”