---
title: '电商搜索H1提升AI-Coding质量实践 RD & QA'
company: 百度
tag: 搜索
date: 2026-06-03
url: http://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247607023&idx=1&sn=abb96ea9a094246d2156cf5054719ac7&chksm=c03f1293f7489b85bbfc78cb62bda740171819e6a0ded7f92c7a6557bfe621497312542c5bad#rd
account: 百度Geek说
origin: wechat-mp
---
。![图片](https://mmbiz.qpic.cn/mmbiz_gif/5p8giadRibbOib5eKA9DvsnapbBokh883cWMjGKcouP64pz9gW7ayIktXwzlApWmhiawhw9RdHV0cHIv7ubnatc8lQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=0)

点击蓝字，关注我们

![图片](https://mmbiz.qpic.cn/mmbiz_gif/5p8giadRibbOichNxgNgW2xyHYqnHnww2mnGT5PC84tpKOThGv2k88zXbdh8DTfA38RniadrhC3y4JagKaIEPTNPlQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=1)

作者 | O.Wen

导读

introduction

AI-Coding时代，质量管理的核心从“是否管”转向“如何管”。通过建立Harness工程基础设施与全栈能力组织形态，结合三层约束框架（输入/生成/输出），可系统化提升AI生成代码的质量与可控性。RD与QA的协作目标对齐为“让AI代码安全上线”，协作模式从线性交接升级为闭环共建，QA左移至标准制定阶段，RD输出标准化Spec，共同实现测试效率提升与交付质量保障。三类项目实践表明，该方法能显著压缩开发周期、提升异常发现速度、增强系统可维护性，为组织级AI-Coding质量管控提供了可行路径。

*全文 4343 字，预计阅读时间 6 分钟*

GEEK TALK

01

背景

**1.1 AI-Coding质量命题分析 -  代码生成效率、线上稳定性、交付周期 的关系**

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy7ibkictCvEicus78loQBhdeYZUWueTbCWnAF53bASoggqUwSrNibeClCofJES996UibnuBsoqJfmOZxbvibibNWwovQ8I4wfGBQrYP4I/640?wx_fmt=png&from=appmsg)

1.1.1 AI-RD 和 AI-QA 为什么重要 

基于 信通院 [【中国信通院】AI4SE行业现状调查报告（2026年）] 

https://www.fxbaogao.com/view?id=5333095  报告 整理 

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy5zZicgf4siaPic3Hsd7MJMp9cEkTX0uqpsA8o2CtuywC7OI8pJiatLbxhRYxjqSZYRAHH74VDNSf0TrZYK4GuLqHk79o0IjZ6OR40/640?wx_fmt=png&from=appmsg)

**1.2 传统软件工程 VS AI coding 软件工程对比**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7g8a51ibvgf5jeOjicU2YSQO235Nq4ARZsJwuYQymYEnDicFpMbiceIBcJvxpE6tw3klqIklquyG9e1zMUgUko8DwOMFS4ZUYUCUA/640?wx_fmt=png&from=appmsg)

**1.3 AI Coding 现状(电商) 和 痛点**

80% 的代码是 AI 生成的，****质量已经不是"要不要管"，是"怎么管才管得住"****。

> 数据使用维度  2026.4 vs  2026.01

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7Xw5ALaPokHKaOAxetF0smqpZKH5EqG9pOVa8YaGicibrwo1exhUvuqfV9xRs4MNZ6I0nz5BrjIL5UWof2IxtVuYqYpgPjOdIeE/640?wx_fmt=png&from=appmsg)

GEEK TALK

02

概述：建立统一认知框架

****核心结论：Harness 工程是基础设施，全栈能力是组织形态****——这两个支撑起 RD 和 QA 的新协作模式。

> ****关于 Harness 的三篇重要的博客：****
>
> HashiCorp : https://mitchellh.com/writing/my-ai-adoption-journey  2026.2.5 Harness 名字起源，驾驭工程；
>
> Openai : https://openai.com/zh-Hans-CN/index/harness-engineering/   2026.2.11 , Agent-first, 5个月100万行代码实践；
>
> Anthropic  : https://www.anthropic.com/engineering/harness-design-long-running-apps  2026.3.24  AI连续执行10个小时，完成可交付任务，大模型的上下文焦虑、生产验收分离；

**2.1 核心公式**

****Agent = Harness + LLM****

****质量 = 输入约束 × 生成约束 × 输出约束****

****拉通 = RD 定义边界 + QA 定义标准 + 共建资产****

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7MYEYJGibb5s84tGzOs5afia30jJouP0b5LbxOHlSPI3pcO5YibdLwoEescRE25BZyfGDRoI5LicqQicbqmtDLJn8bywRLdbt7uliao/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy7iaAxtcLdibYt8SP1YawBTFPf8Svvp6kiaVEtkY42Cicb2x2WCJAAJGOiapiaUjOZQS0ExhqCQDO0DynpaAq2m9aAjNL7q81iajY1yhY/640?wx_fmt=png&from=appmsg)

GEEK TALK

03

实践 - 三种不同类型项目

# 

我们的实践按项目复杂度递进：****品牌卡****（传统迭代）→ ****榜单****（架构改造）→ ****穿搭助手****（Agent 系统）。

共同点是 ****Harness 工程 + 全栈能力****，差异在 RD/QA 协作侧重点

3.0.1 三类需求概览：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy4Wb3vWib2Jvor0KgTXbdmIFKdd6gfomRu7dK0TCBdhgF7Vy4uqDhDgmn3FAujlT70mic7O9ibceBGno0Nq3BgSmVgzAV2hb9MKdY/640?wx_fmt=png&from=appmsg)

3.0.2 不同类型项目 AI流程改造方式：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy5TrVoBbIpfcE0aMfyvv1XJEeksWicpGOBt3qS5h6PAbL43PHwK1wKXXYeEv22tib86yhrMVR3fuibiawof2xiaPZsKsMRoapJAGJUw/640?wx_fmt=png&from=appmsg)

**3.1 品牌卡迭代 — 传统产研项目**

****High light:****

老人接新业务：****4 代码库 / 3 技术栈（Go/Python/Vue）/ 1 人全栈**** → 技术评审时已完成研发 ****50%+****，整体周期减少 ****20%+****

3.1.1 项目背景

品牌卡内循环商家入驻需求，是典型的 ****"老人接新业务"**** 场景，技术架构涉及在线、离线、运营平台 4 代码库 + 3 技术栈。传统模式下这类需求最容易卡在 ****"前几天熟悉业务"****，多语言跨度对角色分工是巨大挑战。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy713mWakgYrMDhyCxNyzmG2mgIiano6P7MB0NiamicTw8qwlpZe43UW1PYZYsHicEIuM2DOXvgeDa2fOIvP3YzWhnDocH8jKqBtqRc/640?wx_fmt=png&from=appmsg)

## ****△ 产品需求****

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy53Nia5QicFQKBlqfTh54eBwDKPVFwVDhDIysFh3voHuMYNnUNEicSfsTKpXoRREhC9aUYpnJAYiao5j9foVPXEQPfaDGSZCzjBjgA/640?wx_fmt=png&from=appmsg)

## ****△ 研发实现 - 配置平台****

****平台地址****：

https://ecom.baidu-int.com/search/brand/brandShopMapping

3.1.2 核心解法：Harness 三件套 + 全栈 + 平台化

通过对应手段 ，该项目在整体技术调研、开发、联调阶段 时间周期 由10人/天 降低至了 4人/天 。

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy6MbDgnpTQpEc8R8dUwG2lXS7AEEsia5wzhicKrm7jBy6ia5nAvJlWYQibQSFhiaaiaEyb2gvFdEgQfUruI6qib7hkQ0dDoODic9yRmCR4/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy76XDLqe2S5KrkWn1wSlaXgDb6FEwKMPT3wobnSS8WGN0YDHSLB7AVer60DDYplgNzic9Oy6LtPd9OS6iav1msJTjYIzzyy7ECfM/640?wx_fmt=png&from=appmsg)

3.1.3 RD&QA 智能测试协同 

通过 ****RD 与 QA 在需求理解、Spec 前置评审、AI 辅助 Case 生成、Bug 定位与边界验证等环节形成协同闭环****，实现了测试效率和交付质量的同步提升。本次测试中，原计划排期 3 天的测试任务，服务端测试仅用 1.5 天便完成，测试周期压缩约 30%。

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy7wibrqeCtJuGSKEy3uvemibb3dhs1tsgWYhVLBBqwphLhH9sAbE41aMKg03JQPKPQtOV78dpg3fqj9KUyaosSMn8Qxn1Ow1GET8/640?wx_fmt=png&from=appmsg)

* ****RD 前置输出标准化 Spec 文档：****RD 基于业务需求和技术实现方案，提供规范化的技术 Spec，明确功能逻辑、数据流转、接口约束、异常处理及边界场景，为 QA 测试设计提供清晰输入。
* ****QA 基于 Spec 快速生成测试 Case：****QA 结合 RD 提供的 Spec 文档、搜索电商后端用例生成SKILL 以及 AI 能力，分钟级生成高覆盖度测试 Case，提前识别核心验收标准和潜在风险点。
* ****RD 与 QA 共同提升 Bug 定位与修复效率：****在测试过程中发现 Bug 后，QA BugFix 数字员工可自动响应，基于 AI 快速完成问题归因分析和代码修改建议。QA 能够带着更明确的问题定位和修复思路与 RD 沟通，减少反复确认成本。
* ****QA 自主完成边界场景验证，减轻 RD 支持成本：****过去边界场景验证高度依赖 RD 解释和协助，现在 QA 可基于 Spec、AI 生成能力和代码理解能力，自主完成边界 Case 设计与验证，边界 Case 测试效率提升约 60%。
* ****形成 RD 与 QA 双向协作闭环：****RD 通过规范化 Spec 提升需求与技术表达质量，QA 通过 AI 更高效地理解业务逻辑、定位关键代码并反馈高质量测试结果。双方在需求评审、Case 生成、Bug 定位、修复建议和回归验证中形成闭环协作，推动智能测试从“测试执行提效”升级为“研发测试协同提效”。

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy7Wcp15Y5LX7iatkwvIoOXwfcTcWAFiboibF2fIAIf0GiaibnMUVHK6TbfZB9Ic8sdoHaYGEgjOlJVctZkPYzJpk3BgNDdCdsAHmgeQ/640?wx_fmt=png&from=appmsg)

## ****△ Bug Fixed****

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy4mWhiaHJXTT2eEpmEkoy2fOpXP442g2eBWAuqe6XxxKBxh4ApGssAMwpvsicyuAPLSMOrufGVFPIWOTicn7bnFqn7v0rQCibiarQZc/640?wx_fmt=png&from=appmsg)

## ****△ 基于 Spec 用例生成****

3.1.4 关键洞察

****业务熟悉****从 ****天级压到小时级****，意味着团队对****插入需求和陌生方向****的承接能力变强了。

****变化本质****：以前先写方案等产品确认再开发；现在边调研边开发，拿着实际跑起来的 Demo 去对齐，需求澄清来回次数明显减少。

**3.2 榜单自动化 — 架构改造项目**

****High light  : 1 RD × 6 周**** → 完整数据生产 & 评估流程打通；涉及 ****8 代码库 / 3 技术栈****；****13 算子****；含在线/离线/评估/算子多技术栈系统。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy74YgEzhlz6HLacdiaEY7cPpoakC9rnzsTMWicGHfIkWE8dWCMfIYkSkpiaiaHP57BrdFMAAEs87plWGOxFwVnQENiccyHxwuhsd8oE/640?wx_fmt=png&from=appmsg)

3.2.1 项目痛点

****原流程****：策略+人工线下评估  → 平台入库上线。  数据流跨 4 层存储（content-platform → rank-strategy → ecbase → SNDB），全链路靠人串。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy6ca6FsV06gH9oHnNVmic7kLNcgONYZmL7SiaWVzQRkGpzJh4y0fySIp5xwscvosHEj6d8ZmaFu6pDf2VCBjiagnXDxGw4XulLUkk/640?wx_fmt=png&from=appmsg)

****实际效果****：****平台能力示例****

****ecbase内容生产平台****

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy5wj2O3ib73ImDD0Oeq832E0LVJ4m8yicTgQCytn3n6s0est5ZOQbZ6XHZNlL1mAWYF1MuhbnibZn9KF70wLOibeIDUVqMiaHquUcn4/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy46IEv864MakOtqTYsDLSFCFCcfRvw8aMSwHEhGLns5z3Wempxjl1VF04lYRIfWRXEjuq32kib3F6hrSfyicoznlLQA2oUpxeFmY/640?wx_fmt=png&from=appmsg)

****eflow算子平台****

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy4NsVJkicvDAn4XdCCabXYSjw1iawbRlJrkiaU3Wx6PgYd8fBPcfdzMcdIH4wMtTlW7M5ibM5RO1GFnVvu9tQd61TyvtbeTthppnMo/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7RPDXhrAyScagf25q2JFLzfj4pIXf2QkCE2CqicAcXV1OVVHrficJpUge1Zu6KEkjhIqmicD6j1Tu8j6Cp3ho4iab2alOibd2SKARw/640?wx_fmt=png&from=appmsg)

3.2.2 解决方案：算子化架构 + Harness 约束 + 开发/测试模式变更

#### 3.2.2.1 算子化架构 + Harness 约束

****算子化架构（13 算子）****：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7V2X0SA9v4Dy4YAu24CrbJcyP8HTLEYibasZuHSu1XiaoHqGibhO3jAS2yxQiaAmWuKpyDjZgdvwXTLuvslKKLya0qQGujWppYiaEQ/640?wx_fmt=png&from=appmsg)

****Harness 工程约束****：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7Njj3P5pNRDV8C2YtDE9Te31Dqibqia5sW32spcycCvw4WWoNibujyd1KHlP0Kzic8XqUXDaU9bVXa3eia7x0k5eib7Mjx8Ric9R44dg/640?wx_fmt=png&from=appmsg)

****技术选型****：Python 3.14 + eflow-operator + Pydantic Settings + OpenAI SDK + instructor + ruff/mypy/pytest 三重检查 + doubao-seed（主）/ deepseek-r1（降级）

****开发：****

使用工作区模式 ，提供更多的更准确的上下文给到 大模型 ，  先统一沉淀各模块系统wiki , 然后产出设计文档 ，进行整体review

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/D0qMsFCrMy6U5iatGyngwPxwEQF9cN5pT7Cn9qcptHuibhjOicaaSzcTtiaUfLJptm2ic23eAXYibosfe00tYYhbA94u8jUhrFqLXyBGpYFG00oh0/640?wx_fmt=jpeg&from=appmsg)

## ****△ 架构文档统一沉淀梳理****

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy7oOQDTTQXc8v5BGmEswIO9hW84ASiaClpNSW2OwZ2SrEao8Sh11TtIHCet7gYgicnetcbicnicTHB3akSAJpB45iaj2JNqhOhbQ3To/640?wx_fmt=png&from=appmsg)

## ****△ 整体方案Review****

****测试：****

TDD驱动 ， 包含 unit / itp / e2e 多种测试任务

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy6HI5EasOvRAfA1SYeu1Q8tH9w2qGJasX40QBoU0H4Niaic0fuQSlDVCqZYAsVjPycxBW4LW3xCykU4oDy7bcVttjYELtMoxqbHw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy4iaibSB2Ut7eY8uRF3xSjk9Dbvcw13KoMx4Af4rwsyrlPSMTn0EiaU3Z1kMEib62eQ50y7mTI6sBmvpe8Ezz9MX6kEBIlmqqQ24JY/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/D0qMsFCrMy5kobhmZw1LSZAJUZ6kZoicqeYbzsM3EGyNibx5fYkc8mFR3qD2qeu0MQichfsW6m5uhhtlq7GRrwA9d8uobib5iau9heaOdD25vmib8/640?wx_fmt=jpeg&from=appmsg)

****审计验证****：13 算子三阶段审计，发现 ****3 个代码问题（1 高/1 中/1 低）已修复****；13 项逻辑差异闭环（2 修复 / 3 TODO / 5 无需处理 / 3 不纳入）；Top2000 策略召回率 ****75%****（PV 覆盖 95.5%）；上榜理由召回率 ****99%****。

3.2.3 效果对比

```
改造前：策略 → 人工 Excel → 多轮审核 → 手动脚本提交入库 → 流式同步改造后：策略提交 → 平台批量任务 → eflow 算子生产 → 自动聚合 → 自动入库 → 自动同步﻿
```

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy4Nuhr2LKoeibCPTSeBshGbstsUMcDAgahCYniaGJaLRolnicma3nqNJb2m8ePGVwiczqFHKk1yoxBKnkic0PScp3PWfIzy1TIngOL8/640?wx_fmt=png&from=appmsg)

3.2.4 RD & QA 协同

****QA 必须左移到数据契约定义阶段****：

* ****测试重点变了****：从"测功能" → ****"测数据正确性和链路可靠性"****
* ****介入时机变了****：从接口写完后测试 → ****算子接口定义时就参与****
* ****关键产出****：数据契约定义、链路可回滚性测试、算子审计标准
* ****协作模式****：与 RD 共同制定算子 I/O 规范，确保数据一致性

**3.3 穿搭助手 — Agent 项目 ⭐**

Agent 项目最能体现 RD/QA 协作的本质变化，且涉及完整工程闭环。

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy7I1hda557OPntzVaf5HjKC38JnSt4MTia05SiaUibjodFExuibfOfefQsibeW6CobjH3CLicYMRzTibVegoJiaZAt62zdIo5jlWWKCCfE/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy5lUicZ3k5MYibs5nzsiciaVXUNNjiaqGTfV6z65w5S6FHdda8l5Gykiciaic2QJIcTJXGPMfymIzIDEuTtEdAK3Yl6YAW3cDZhxibnBKicA/640?wx_fmt=png&from=appmsg)

3.3.1 研发阶段→ 4 项平台能力

> ****核心理念****：好的 Agent 是不断迭代、评估出来的；可观测、可追踪至关重要。传统的中台 Agent 平台业务适配差，自己造轮子在 模型+harness 工程成熟的今天，成本已经很低。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy7eJShJpvJQHaP8bvtFxrDrBFUO5uciaOnpicmfhia08nVE7s3aGd6rM19NMiaCgn3sGA4icyibp9ZcLqW3VjXPUL8iaCwklvZ7YRNeSU/640?wx_fmt=png&from=appmsg)

****调研期间****：调研期间同时完成项目demo 编写（前后端、可交互的原型）， 技术详设时直接使用主对话Agent的****实际工程效果****进行 评审 （RD产出）；

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy68uO2XiaIicjB5F5Xfy9K0xk2n80AtcCyMYCGibwMeibA2qfWVS1xneeFj1MHoELwLZ40NNGcxwMo5fTbMYIE69Bic2zV80jPAMVHw/640?wx_fmt=png&from=appmsg)

## ****△ 产品需求****

|  |  |
| --- | --- |
| ***△ 技术详设-RD产出的交互图*** | ***△ 技术详设-RD产出的交互图*** |

## 

* ****对话评估****http://philandzhen.bcc-szzj.baidu.com:8960/

|  |  |  |
| --- | --- | --- |
| ***△ 对话评估-测试用例*** | ***△ 评估结果列表*** | ***△评估详情 - 实际产品效果+性能分析*** |

* ****prompt调试 + 数据集管理****：

|  |  |
| --- | --- |
|  | ***△ 数据集管理*** |

* ****全链路Trace ：整体情况概览 + 各阶段工具调用/tokens使用/耗时****

http://philandzhen.bcc-szzj.baidu.com:8000/trace?session=da7ec441-367d-495f-9f8b-77ce5ac9605c

* ****线上效果监控trace**** : 结合 日志埋点/采集 + 普罗米修斯大屏展

https://console.cloud.baidu-int.com/mtgrafana/p/d/S4PdKN2Dk/chuan-da-zhu-shou?orgId=467&var-ds=Prometheus%E7%9B%91%E6%8E%A7&var-tool\_name=All&from=1776700800000&to=1776787199000&var-cluster=All&var-namespace=All

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy6WxQiccTP5eJ9ysAFPyHicl0ibbG9T7Yriau8qB5X0d44ZvydnkGaRWS9ic7TJ5DO8Q3a0D3ynrqZBvG9uY6SE714gH2nCXVoWTqzE/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy5dblIHicmjozbhPCcxQSsAzxplBuUibJH8AN0YvxBN7DtNHL3UGsIicJNAKkjOR7ORvHdpt7iaqNH1ftznXmLtlYaE4uv8JYibHNeQ/640?wx_fmt=png&from=appmsg)

3.3.2 QA 智能测试 

> ****核心理念****：****人定义标准，AI 执行验证****——把"经验驱动的人工判断"变为"规则驱动的 AI 自动校验"。

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy4WWt1PmjM6DBFRaKaxc9gv59RibibPAoX9N4mCVPCHK9pL9RcjSMqJOwzKibf2tLW5Jd3yCAC4jzko8RHaY1xq9235nb3Wwt96HA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy5uFVtImYfWNANGvT7xibWk2rMvHicMGVNBr1qsO2hQibOfBYC4fRqaKTLDOH54NtrDjT5G2tsFG3L9ia9DicxOAU1x7ROnWAATwoHw/640?wx_fmt=png&from=appmsg)

#### 3.2.2.1 AI智能测试实践

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy41nXK5qdYTGLw0o4VasO0UzHSRRaRDsvibJPawphia4ry827k1B1Wqow0jNQvZSC945ia03lLz5IF9FibG0MFfR6V0O0sFOqO6GlU/640?wx_fmt=png&from=appmsg)

* ****用例生成****

+ ****痛点****

  · 手工用例生成：需求文档 / 功能描述 / 技术文档（输入）→ AI 解析需求意图 & 业务规则 → 自动识别测试维度（功能点、边界、异常） → 生成结构化用例（用例名、前置条件、测试步骤、预期结果）→ 输出标准化用例集
+ ****方案****

  · 基于整库理解的接口用例生成：获取变更→变更分析→生成可执行参数→生成接口测试用例（覆盖边界值、异常值、典型值）

  · 边界值、异常分支依赖个人经验，经验不足则大概率遗漏

  · 测试维度拆解不系统，等价类划分不完整

  · 新人上手慢，同一需求不同人写出的用例质量差异显著

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy5TaZZvK1licM1SY1RGKo1jfU0URQ4qktsK7p18Le4k04Co7dQTHxfv9W0IelZ8LQXQbTWCEGXtAX0DG1z9ObsoMbMoMpEok8J0/640?wx_fmt=png&from=appmsg)

+ 收益

  · 生成效率：天级（人工编写） → 小时级（AI 自动生成+人工review）

  · 场景覆盖：依赖个人经验 → 系统化维度覆盖，减少盲区

  · 一致性：风格各异 → 标准化输出，可直接复用

  · 可维护性：手工更新 → 增量精准更新
+ ****效果示例****

基于需求文档+技术文档的手工用例生成：

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy4brE0p1TIwRnx2nuOUAD2InWO5Kz3OAUeib0Gicx0zIrTXZ2ibdOblib7ibtxrS8rTqj0u4JXRcLNIC2r5Y4QqNXyG0f7a8xvPTgxQ/640?wx_fmt=png&from=appmsg)

基于整库理解的接口用例生成：

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy5jQ3NrheaGeg0FbxD8T9ZM6bkfGoA3dnuKjNXESL4VicVHIklWOB3OUK34ibGcnNynibq9EQ4pct1KObhGzfLOWvKOcA5VN4o2b4/640?wx_fmt=png&from=appmsg)

* ****功能测试****

+ 人负责定义标准，AI 负责执行验证。将"经验驱动的人工判断"转变为"规则驱动的 AI 自动校验"，实现测试能力从点覆盖到面覆盖的质变。

+ ****痛点：****部分功能点逻辑验证场景多，手工测试耗时久
+ ****方案：****
+ ****收益：****分钟级完成人工需数小时的验证覆盖

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy4wloD955bfFflhMNN7fGLQJ4IibdNjqIw4URRtn0xtbZaIVj96rf5vx9xia6zFCL4ZIOVWvCCwuwRYUicB3m7BSbibCkr3NGJluP4/640?wx_fmt=png&from=appmsg)

* ****交付AIQA****

+ ****痛点****

  ****· 信息分散，协同低效：需求、进展、文档散落多个系统，项目成员无法快速获取全貌，频繁跨平台切换耗费大量时间****

  ****· 进展同步全靠手动：日报依赖人工收集汇总，信息滞后、遗漏风险高****

  ********· 需求与项目割裂：需求卡片与项目群缺乏关联，无法快速溯源需求进展状态********

+ ****方案****

  · 建设交付AIQA，将项目关键信息整合到侧边栏进行统一展示，自动统计项目进度并发送项目进展日报

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy63Ay4PddicWftcoibbhyTlDave7ibKibsBktiaNEutTRfIiaf7x80Df2X2LzNp5yOwQFoC0EsWKNm7s28lBZJtvDiaLiapgBxGafQp1OU/640?wx_fmt=png&from=appmsg)

+ ****收益****

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy46NKAnTvVDRDSDOvJs5rsRicXno50vBunlGxJ8wh472g7FM2J2Bzkewg6jn5MfFoZAWyDowOKSicJtsQkIKesv3pLJZeykicnWfc/640?wx_fmt=png&from=appmsg)

+ ****效果示例****

|  |  |
| --- | --- |
| ***△ 侧边栏*** | ***△ 侧边栏*** |

|  |  |
| --- | --- |
| ***△ 侧边栏*** | ***△ 侧边栏*** |

|  |  |
| --- | --- |
| ***△ 项目日报*** | ***△ 项目日报*** |

GEEK TALK

04

RD/QA 协作 SOP

三个不同类型的项目，几个核心认知：

* ****质量定义变了****：以前"代码能跑"就算合格，现在还得知道它为什么能跑、生成过程合不合规、出问题怎么定位
* ****协作目标对齐了****：RD 要快交付，QA 要找 bug，两边天然有张力；但 AI 时代目标对齐了——让 AI 生成的代码安全上线，两边是队友
* ****流程必须闭环****：线性的开发→测试→上线兜不住 AI 代码的隐蔽风险，得在生成前定标准、生成中实时管控、生成后复盘

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy6FXv1QptwKHTKB4DLlg4xzrU3bR6bFnKRl6jwNOBnl3MRW6IvMhFvPL0RUFjXQYKGfaresuWGrV6YxVRsua1LAVR3a995gQzQ/640?wx_fmt=png&from=appmsg)

GEEK TALK

05

后续计划

![](https://mmbiz.qpic.cn/mmbiz_png/D0qMsFCrMy41E4QUUKAw17cPIAnMcxSIibG1qWUSzPJ89IhCZwAsicSygbYulPSNVibTCPxc63qog3Xl8yMSbrCmic6RoqHa6oibOiburnQ1Y3Zao/640?wx_fmt=png&from=appmsg)

**5.1 团队**

1. 小组：持续提升团队内成员 AI工具使用技巧， 激发同学的主观能动性，针对实际业务痛点，沉淀标准，落地工具；
2. 部门：协同其他角色同学一起在具体场景落地相关Agent助手、工具能力，逐步积累经验和信心； 由点及面逐步进行落地完善；

**5.2 业务**

空间维度：点

能力维度：标准化

****核心目标：验证可行性，输出标准****

****核心产出：规范、流程、清单****

## 进展：

给大模型做好知识导航， 完善AGENTS.md ， 根据具体业务场景，沉淀SOP ，针对性创建skills；

指导思想：5.14 https://claude.com/blog/how-claude-code-works-in-large-codebases-best-practices-and-where-to-start

实践落地：部分skill 工具示例

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy6XNKB0clp803qHfTmrGAhJypQBJAJWyVntO08xibO3ccnZRgcXC1rz5iaGicJjBXkckE7WdJzmiaARTxuv116Jy38VxRYdIJrtHOs/640?wx_fmt=png&from=appmsg)

空间维度：线

能力维度：工具化

****核心目标：打通单链路，固化标准****

****核心产出：工具、数据、闭环****

## 进展：

电商搜索小助手、上线check工具、搜索诊断工具 、报警诊断修复工具； 针对不同场景的工具逐步完善；

|  |  |  |
| --- | --- | --- |
| ***△ 电商搜索小助手*** | ***△ 电商搜索小助手*** | ***△ 电商搜索小助手*** |

|  |  |
| --- | --- |
| ***△ 诊断出卡工具*** | ***△ 报警诊断修复工具*** |

空间维度：面

能力维度：平台化

****核心目标：全组织推广，能力复用****

****核心产出：平台、中台、知识库****

## 进展：

平台化对应能力，存量业务/代码 进行配置化改造 ； 增量能力，针对具体场景，沉淀对应平台能力；逐步将各种工具能力接入，逐步落地为基础建设，向中台化演进；

电商搜索平台能力概览：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy755XV1siaF3FiblF9MQeVAuS74VZnydcMKHkRxLsM3RrmL0wtgjf6Ib8xPM345xc8wzc0hZlqwZHNibJMFXlF3L15xNPcpfAVBsw/640?wx_fmt=png&from=appmsg)

## ****△ 电商搜索中台能力****

Agent-eval平台能力：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/D0qMsFCrMy4UakYeKSKZpGEVrSm7Esaqbl17Pj5wDovypVJFUYD4AkAWHR0ngh8K5VWibhHY4mCvtRyYvI9Dqiamia4m6n6LicL7SDVWres7MIE/640?wx_fmt=png&from=appmsg)

## ****△ Agent-eval平台****

空间维度：网

能力维度：智能化

****核心目标：组织级智能，自主进化****

****核心产出：智能体、自治系统****

## 进展：探索中

END

**推荐阅读**

[用数据说话：贴吧 AI CR（小码哥）落地 10 周，bug密度下降 66.87%](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247606943&idx=1&sn=805a8afb96422f9aafbf909919df8faf&scene=21#wechat_redirect)

[告别死锁和陈旧语法、告别性能瓶颈：新手Gopher 秒变 Go 语言大神](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247606926&idx=1&sn=f48de5a0e4e22e2fbcb65c1655194f58&scene=21#wechat_redirect)

[RenderFlow：百度垂类搜索展现服务的 Agentic 代码交付实践](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247606907&idx=1&sn=16ee44f4deaee5fac7cc7d3a7a78bfe2&scene=21#wechat_redirect)

[网盘存量代码迁移实战：我们如何用三层架构管住 AI 的输出](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247606898&idx=1&sn=33f302232a8c61f321eb23e9f25ed454&scene=21#wechat_redirect)

[PRD → Goal → After-Goal：AI 主导全流程研发实践](https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247606885&idx=1&sn=fe072e366c4ebb50a14f6c0c1d2bd330&scene=21#wechat_redirect)

![图片](https://mmbiz.qpic.cn/mmbiz_png/5p8giadRibbO9x9T3iaxknhz6B4v4PPxvGEAlXibefUzgTftSnnT6QficHvz0w4T1CtHpDD8ZDU7NiaAjkHFssZN9IYA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp)

一键三连，好运连连，bug不见👇