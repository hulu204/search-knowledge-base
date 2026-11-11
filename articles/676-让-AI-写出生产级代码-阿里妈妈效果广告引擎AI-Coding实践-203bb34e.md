---
title: '让 AI 写出生产级代码：阿里妈妈效果广告引擎AI Coding实践'
company: 阿里妈妈
tag: 工程相关
date: 2026-01-28
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497012&idx=1&sn=13abef9387090e5f716e4dbb3f421c07&chksm=c17982c1ed6728d05b9287c42f1216e91b29e06591cdecafa71891138944d2109f3c5d60cb62&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
一、引言：“严肃场景”的AI Coding并非唾手可得

随着大模型技术的迅猛发展，AI Coding 已成为提升研发效率的关键手段。然而，在大型、复杂的生产系统中，直接使用通用 AI 编程模型往往陷入 "能用但不好用，可用但不可信" 的困境：

* 通用 AI 编程模型在单点、明确的任务（如函数补全、单元测试生成、简单逻辑实现）上表现尚可，但在复杂系统的开发中难以胜任
* 目前主流实践仍停留在 "vibe coding" 阶段——开发者凭直觉编写提示词，再通过人工整合与验证结果，效率与可靠性均受限
* 实际工程项目普遍存在模块高度耦合、质量要求严苛、上下文庞杂等问题，而通用模型缺乏对私有代码库规范与系统语义的理解

本文将分享阿里妈妈效果广告引擎团队在 AI Coding 领域的探索与实践经验。依托历时三年打造的 CommonAds 研发体系，我们构建了智能研发助手**「元芳」**，并通过集成至 IFLOW-CLI 以多 Agent 协同的方式，探索出一套可胜任于「严肃的广告引擎场景的高质量代码生成解决方案」，具体包括以下三个关键维度：

* AI Friendly的架构支持：CommonAds 研发体系在设计之初即具备良好的 "AI 友好性" ——模块解耦清晰、接口规范统一、上下文可追溯，为大模型生成高质量、高可靠性的代码提供了坚实基础。
* 规范驱动的多Agent方案：「元芳」代码生成体系的核心设计理念——"规范驱动、上下文工程、Agent优先"，在此基础上构建一整套规范体系，这是实现稳定、可控AI编码的根本保障。
* 工程化落地实践：通过 IFLOW-CLI 与 元芳 MCP Server 的深度集成，我们将上述理念转化为可运行、可扩展的工程能力。借助架构设计、能力沉淀与工具链闭环，真正实现了 AI Coding 在大型生产系统中的规模化应用。

本文完整作者：加比，零言，山衍，应灵，潇劼

## 二、前置探索：引擎代码资产的AI Friendly重塑是AI Coding的重要前提

### 1. AI友好的引擎架构

阿里妈妈效果广告投放已全面进入跨渠道时代，这意味着同一产品能力需在搜索、展示 等多个引擎中实现。面对大量跨渠道业务探索和迭代需求，传统的独立建设支持垂直业务发展的广告引擎1.0版本以及统一引擎基座的2.0版本已显得力不从心。

我们的做法是**构建一个具备统一业务抽象且提供细粒度能力供复用的CommonAds层**，来帮助各引擎间实现能力拉通，确保全域投放的一致性和高效迭代，进而最终走向各引擎全面拉通的3.0时代。

阿里妈妈效果广告引擎经过3年的建设，持续将内部多个广告引擎的**能力进行沉淀、复用**，最终形成了现在完善的CommonAds研发体系，其**多层&解耦**的架构天然具备 **AI-Friendly** 特性，是我们探索高质量代码生成的基石。

* **多层架构，职责清晰：**

+ **Util层**：底层的通用工具层，包含各种框架能力、数据处理能力等
+ **Helper层**：对数据表的原子操作进行封装，以方便用户对表执行各种通用操作
+ **算子层**：用户自定义算子，完成一个具体而独立业务逻辑的组装
+ **子图层**：引擎外部可感知的图结构定义，实际代码部署的基本单元

* **核心优势，AI友好：**

+ ✅ 每个层级职责单一，层内接口清晰。不互相耦合，只有调用关系
+ ✅ 代码细粒度、注释丰富，易于被大模型理解与生成
+ ✅ 任务拆解路径明确，避免"不知道在哪写、怎么写"的模糊地带

### 2. 与AI编码流程的完美契合

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUVHMiavm5B9IguJPHqSDmicbLFwhRsh9SDVpND3aJGBhWBeBvhU3upXcHg/640?wx_fmt=png&from=appmsg)

图1、CommonAds与AI编程的清晰对应关系

在此基础之上 ，我们建设了阿里妈妈-效果广告引擎的智能研发助手**「元芳」**，依托 CommonAds **清晰的体系架构**和**明确的编码规范**来驱动大模型进行高质量代码生成。

基于「元芳」的代码生成能力，我们在近半年成功实现引擎中不少新增核心算子由大模型生成入库，初步验证了当架构和规范足够清晰时， AI 在大型系统中规模化编码的可行性。

## 三、整体方案：“减法”与“加法”是构建可信AI编程范式的核心

我们认为，真正的AI编码应该是严苛约束下的精准工程。「元芳」的核心逻辑在于：通过明确规范做“减法”，收敛大模型自由度以实现确定性；通过丰富上下文与多 Agent 架构做“加法”，沉淀领域知识并强化执行能力。在推进代码生成能力落地的过程中，我们构建了一套完整的解决方案，具体围绕**3个设计原则**和**1套规范体系**展开。

* **原则一：规范驱动**

+ **核心理念：** AI编码不是自由发挥，而是在**严格编码spec**（编码术语澄清、复用接口查询、接口编码规范 等等）指导下的增量开发
+ **正向循环：** 规范驱动AI生成 → 分析生成效果 → 优化接口设计和编程规范 → 提升AI生成质量

* **原则二：上下文工程约束**

+ **核心理念：** AI的能力边界，由我们对工程体系的抽象深度和规范完备性决定，这些信息以**各种形式的上下文**加载给模型
+ **实现路径：** 元芳的工作重心在于构建各类可查询、结构化的**上下文知识库**，并将其转化为模型可理解的提示词与验证规则

* **原则三：Agent优先**

+ **核心理念：** AI编码不是简单的代码生成工具，而是具备推理、规划、决策能力的**智能体（Agent）**，以期最大程度释放大模型的智能
+ **价值释放：** 传统模式止步于"prompt in, code out"，而Agent模式解锁了AI的系统性思维。它能处理模糊需求、应对复杂场景、在不确定性中寻找最优解，成为真正的智能研发助手

直接让大模型端到端地完成从需求到代码的生成是不切实际的。因此，我们将整个**代码开发流程拆解**为若干明确的阶段，每个阶段由专门设计的**智能体（Agent）**负责执行，并通过一系列**上下文工程**为其注入丰富且高度相关的上下文信息。这种多Agent协同的架构不仅提升了整个流程的可扩展性，也增强了其可解释性。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUVwv7m2cq27aWgcGU0XAZZOL6OytX9TCPeHdyBaDx7QmDE1YPuVBpOTw/640?wx_fmt=png&from=appmsg)

图2、多Agent合作的代码生成全流程

基于上述原则，我们构建了**一套规范体系**：为需求到代码的每个阶段都明确相关规范、可检索知识库和其他辅助信息，并将这些内容作为上下文动态加载至对应的Agent中。此举显著提升了各阶段输出的准确性与一致性，有效抑制了模型幻觉，使最终结果更贴合预期。具体来说包括：

* **研发过程拆解**：需求判断 → 编码依赖 → 编码执行 → 风格对齐 → 单测完善
* **编码可见代码提取**：筛选高质量、易复用的工具接口，用于模型代码生成时的功能复用
* **引擎编码基础知识**：广告引擎中 子图/算子 等基本概念的澄清，确保正确生成/使用相关接口
* **CommonAds编码规范**：代码风格、颗粒度要求等，代码生成过程中遵循，并通过检查脚本强制约束
* **CR记录的编码细节**：历史CR信息抽取，作为编程规范的增量信息，针对性优化
* **单测接口使用**：编写单测所用的统一接口，以及单测覆盖率统计脚本

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUVhuW9Fc5ZNkLGFGkdJLS0nfcQpp9vugY9dt4YM1rIyK2bhkDK0rcNRw/640?wx_fmt=png&from=appmsg)

图3、覆盖全流程的编码规范

## 四、技术实践：基于 IFLOW-CLI 与 MCP Server 的工程化落地

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUVMjt6eDwsyeuYxoEZmiaiboHBkvmGe60SeibKuZ0NTtJAibNia0d0CWt3ehQ/640?wx_fmt=png&from=appmsg)

图4、元芳MCP Server架构

首先我们完成了**开发环境适配**，使得团队同学可以在开发机中使用IFLOW-CLI，并支持在IFLOW中执行代码编译、构建等必须的开发操作。

![image (9)_副本.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUV8NcgkiahrNzDzVL1EUU3qbCGcAHcTa2PrJs7A8US8dyrFTsp77mgmCw/640?wx_fmt=png&from=appmsg)

图5、在开发所用容器环境内使用IFLOW

基于IFLOW支持的 **Tools、Hooks、Agents、Memory** 等多种拓展形式将「元芳」的各种 编码计划生成、可用接口检索、编译验证、使用日志捞取 等等能力，进行实现和沉淀，并统一通过 **元芳-MCP Server** 部署。具体而言：

* **Servers：**广告引擎多个不同用途的MCP server通过元芳的自动化流程同步到用户IFLOW本地
* **Tools：**对于编码阶段所需的各类规范、所需要查询的各类引擎编码知识信息，这些基本能力我们都以工具形式统一提供。
* **Agents：**我们对于需要执行复杂流程，或者基于结果持续修复的需求，建设了一批Agents
* **Hooks：**元芳所涉及各类配置、功能的拉取和更新，用户使用日志的捞取和上传等都通过Hook进行实现
* **Memory：**沉淀CommonAds代码库一些框架知识、接口概念、引擎黑话等，避免用户重复输入给IFLOW
* **数据回收与分析：**记录IFLOW和元芳的使用日志，再和最终入库代码做关联来统计AI浓度及分析编码效果

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUVClFOmHSyQO9fWyDFfQQw8TB9SCNZHHDImbKLURibWZ5AedoGnGHTGYA/640?wx_fmt=png&from=appmsg)

图6、MCP Tools示例

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48YnIGpJsZy9CwlDP1kvZrUVibvyiaErXLTuyBSn5XibkoshSiaSicIa8Cooz2tIYC997A2V1owS1hUjbtw/640?wx_fmt=png&from=appmsg)

图7、Agents示例

## 五、全景演示：AI赋能从需求到代码的全链路闭环

接下来通过一个具体的示例来展示「元芳」完成 "从需求到代码" 的完整流程。

#### 1. 需求说明：

```
子图：广告主 × 流量场景xxx参数调整能力  
1. 背景与目标  
当前观测到，在部分流量场景下 xxx参数存在低估，为优化商业效果，需在特定流量场景下，对符合条件的广告主进行参数调整，以优化广告展现效果。  
  
2. 功能逻辑说明  
系统需执行以下逻辑：  
2.1 判断是否命中参数调整策略：  
    ○ 根据当前请求的 流量场景 code 和 广告主id，组合生成 query_key，规则如下：  
    ○ 查询广告主黑名单数据表，若 query_key 存在于表中，则跳过系数调整；  
    ○ 若不在黑名单中，则继续下一步。  
2.2 获取并应用参数修改：  
    ○ 从实验参数配置中读取两个动态参数：  
        ■ target_code：目标流量场景 code（整型）  
        ■ ratio：参数提升系数（浮点型，如 1.3 表示参数 ×1.3）  
  
    ○ 若当前请求的 流量场景 code 等于 target_code，则将原始算法参数乘以 ratio 作为最终参数；  
    ○ 否则，保持原始参数不变；
```

需求的**基本功能说明**，作为给IFLOW的原始输入。

#### 2. 整体流程：

首先，通过**「编码计划生成Agent」**根据用户输入的需求说明产出一份详细的**编码计划**，将其作为蓝图用于指导后续代码生成的全流程。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYn6iaMXcdzicUVXHicXxJYuQa38TvToEsakQzrNaXBo7DtcCAf9o1dHujGg/640?wx_fmt=png&from=appmsg)

图8、编码计划生成Agent的system\_prompt示例

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnk3fuiahib2NmISs3Gsu7Zrv3F9a25Z6px99jiaA16pVtiaekxYkpF8M8OQ/640?wx_fmt=png&from=appmsg)

图9、用户与Agent的交互流程示例

基于编码计划的产出规范，Agent根据用户的输入并与用户进行**多轮交互**，以确定需求所涉及的各种细节用于产出正确、完整的**编码计划文档**。在这一过程中，会额外调用**「接口检索Agent」**来针对本次任务涉及的功能在CommonAds代码库中找寻**可复用的高质量接口**：

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnESmq88fTG60os50PzwHXlic6peqzEdg7E9OHCwtVUTCs7UcR7F9DF3w/640?wx_fmt=png&from=appmsg)

图10、接口检索Agent

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYne42B9hd7fzQItX3BNiaU94icWLf8XLoUhCq3tk4m39DbdJ3cF5mznQtw/640?wx_fmt=png&from=appmsg)

图11、接口检索Agent返回结果

完成上述流程后，已经获得了：**详细的需求说明、完整的实现细节、可用的接口列表**，再**基于memory**中CommonAds的**编程知识、引擎黑话** 等信息，「编码计划生成Agent」就可以产出一份详细、完整的编码计划：

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnUPXuicfVzDia6B9eEwExGhRJ5bXMGtY2AsOUbtYPzoUUHiah5Oa13LkoA/640?wx_fmt=png&from=appmsg)

图12、编码计划文档

产出的编码计划文档，其内容包括：**详细的功能说明、输出输出表的结构、具体完整的执行步骤、可用接口列表、部分示例代码**。 再基于这份编码计划，通过**「代码生成Agent」**生成对应的业务代码。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnfTH6P6wjSSO4st7NSFTmibEm11KB6QD9fMFg2Q9f8ODWcgTB6icjdZfQ/640?wx_fmt=png&from=appmsg)

图13、代码生成Agent

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnelKXS54ibFwe5khvhG0EE0ibYcoVjz5p9FPQc09zLZHeiaYvWn8r5nVibQ/640?wx_fmt=png&from=appmsg)

图14、生成的python结果代码

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnPTrlufvPv7k9RFS2o5wS53Q8WG0e8eRJkfqjibl27unzTxTJS0sVoEw/640?wx_fmt=png&from=appmsg)

图15、生成的c++结果代码

完成业务代码生成后，通过 **「单测生成Agent」**产出对应的单测。并通过调用**「覆盖率验证工具」**的方式给大模型提供**「尝试-验证-纠错」**的空间，以**持续修复代码逻辑和提升单测覆盖率**，保证了代码生成的质量。如下所示：

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnwXnlc3X3eZFNv1ib3pOLHA5ibw7PI02ygXYeJfgvd9DF79OIZLHBs5yg/640?wx_fmt=png&from=appmsg)

图16、生成的c++单测文件

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnib7r0qcH14qpzEhfbRGjNpHiaG2rPtbzxWwFw9oLMCSyibiauibBR89Rmrw/640?wx_fmt=png&from=appmsg)

图17、单测及覆盖率优化流程示例

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnyNgB5sUw6pdWxShymorK5En7Ul9edRuhwJI8qicacTY7jDkkvOqnMibw/640?wx_fmt=png&from=appmsg)

图18、单测及覆盖率优化执行结果

完成上述流程后，进入提交代码CR前的最后一步：代码验证环节。通过**「代码验证Agent」**对于不符合CommonAds代码库入库要求的代码自动进行**代码拆分&优化、统一代码风格** 等处理，此时代码质量基本处于可入库的状态，即可进入人工CR环节。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZeVXibyF59bjrzHX5XopOYnaS1rJHxZOXyMDVXUCRkPZxXalsUbZXYbTmqldsv5uQ2xOZIF80bUwQ/640?wx_fmt=png&from=appmsg)

图19、代码验证Agent执行结果

#### 3. 最终效果：

* ✅ 代码风格与编程规范完全对齐CommonAds代码库
* ✅ 正确复用代码库中已有的高质量接口，避免重复造轮子
* ✅ 函数设计合理，保持细粒度。同时注释完整
* ✅ 单测风格统一，覆盖率高，有效验证各种场景的正确性和鲁棒性
* ✅ 除需求细节确认外，基本全流程自动化，用户介入少

## 六、未来展望：夯实AI-Friendly基础，延伸AI研发的“左右两端”

在夯实当前AI Coding能力的基础上，我们正从思路延伸与基础巩固两个维度同步推进，以构建更完整、更智能、更可持续的下一代研发体系。具体来说：

* 思路延伸：致力于实现端到端智能研发（需求 → 可实验分支）的完整研发流程，持续完善各类规范、建设&优化编码知识库、打通需求到部署的全流程自动化，并基于用户反馈持续迭代代码生成效果。

* 基础巩固：针对CommonAds代码库中部分历史代码可读性不足、耦合度高的问题，我们将采取“架构师主导、AI执行”的人机协同模式，通过批量重构核心支撑层来提升代码的可读性与易用性，并持续丰富知识库内容，使引擎代码更易于被AI理解与使用。

---

# 💡 关于我们

我们是阿里妈妈广告引擎团队，是支撑着国内最大广告业务的核心技术力量之一。我们正在用前沿技术重塑广告引擎的未来：用Serverless架构、AI-Coding 持续提升研发效率，用GPU/PPU推高算力天花板，用数据驱动探索大盘提效。真诚欢迎具备扎实的C++编程、数据结构算法基础，对高性能、分布式架构有经验，对AI研发有兴趣 的同学加入，一起玩转新时代的广告引擎！欢迎投递简历。

**📮 简历投递邮箱**：taobao\_techhire@service.alibaba.com

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&randomid=pugabtu8&tp=webp#imgIndex=9)

****也许你还想看****

****[让逻辑「漂」起来：阿里妈妈广告引擎Serverless（GaaS）架构揭秘](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496921&idx=1&sn=70f568577ffbf6fc51a1f08aec0423cf&scene=21#wechat_redirect)****

****[阿里妈妈展示广告引擎动态算力再探索：面向业务收益的机器自适应调配](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490392&idx=1&sn=981d9dcd2158af2de6b1a064ffee92f9&scene=21#wechat_redirect)****

****[阿里妈妈展示广告引擎新探索：迈向全局最优算力分配](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490372&idx=2&sn=70199c83ced6d0ca55c71590c8513c00&scene=21#wechat_redirect)****

****[广告平台智能优惠券：撬动商家ROI与平台增长 | KDD’25](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496932&idx=1&sn=19140f0c93b3806f16e939476a656a15&scene=21#wechat_redirect)****

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=15)

喜欢要“分享”，好看要“点赞”哦ღ~