---
title: '大模型时代，新一代向量数据库的探索应用-DingoDB'
company: DataFun
tag: 召回
date: 2024-03-10
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708980&idx=1&sn=168afda870edc40715ca3d1eedde9c8d&chksm=fbd80358ccaf8a4ec12ef703e1428898a5283920c1f686755de5dda5ed7764d69697785f2632#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhvVATYibVSfTyknbdUSHb1t4017C76WFVM5GTY83dHtzIlHUeIQZQUaeuMosRobdQxFLiciaW1c8ibew/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhvVATYibVSfTyknbdUSHb1tp8GXNEgiaVUZQfp9xFDa6GPveua63Gj1BQeFL6ahujnsXxTMcEqYMLw/640?wx_fmt=png&from=appmsg)

**导读** 本文将从具体的技术角度，介绍 DingoDB 多模向量数据库，及其应用场景。

******主要内容包括：******

1. DingoDB 的设计理念

2. DingoDB 的产品优势和架构介绍

3. 应用场景介绍

分享嘉宾｜孟圣智 北京九章云极科技有限公司 资深架构师 

编辑整理｜梁维

内容校对｜李瑶

出品社区｜DataFun

---

**01**

**DingoDB****的设计理念**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhN7BaGL8loE8ibIicjt9resMLytnYpPahTZYmUgaMTfH8PlO2v93OTIY7A/640?wx_fmt=png&from=appmsg)

2015 年前，数据架构以数据仓库（Data Warehouse）为主，专注于结构化数据的统一存储。到 2016-2022 年期间，流行数据湖（Data Lake）的概念，扩展了数据维度并管理了更多类型的数据。最近一年，AIGC 飞速发展，数据生态随之演进到了新的数据栈时代，随着数据分析复杂度的不断提升，由最初的查询处理需求，扩展到机器学习和深度学习，又发展到了现在的自助分析、生成式内容创作（AIGC）、自动化机器学习平台（AutoML、GPT）等场景。这些都离不开对现实世界中的结构化、半结构化和非结构化数据的高效管理。需求的增长催生了新的数据生态。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNibcgB7zCa5T5X7mdtwYFDgArXYO9qFU2mUBfM9gqev191Q2NwRxbPoA/640?wx_fmt=png&from=appmsg)

在新的数据栈时代，原有数据处理流程基本不变，包括数据的来源、获取、转化、存储和计算以及利用数据进行分析预测和构建应用。未来趋势是走向"向量海"，所有非结构化数据最终会被转化为向量进行存储，基于数据结构构建实时分析处理流程，在此基础上再构建出各种数据应用。

九章云极 DataCanvas 在数据生态方面积累了丰富的经验，提出一站式解决方案，涵盖了数据摄取到数据应用的全过程，并推出了相应的成熟软件和产品来满足客户需求。DingoDB 是其中的多模向量数据库，主要目标是处理数据存储和计算，以及部分分析和预测的功能。

除了 DingoDB，还推出更多相关产品，如 TableAgent 数据分析智能体以及自有的人工智能平台和大模型。这一系列工具的目的是为了能够串联起数据处理的全流程，为用户提供一站式的解决方案，有效满足大规模数据的存储、分析和应用需求。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNAmuhxUZtO6raou1NKg4lYV2HKyJb5GNCqKPN8NdiaPl7PIjoNL1lMWQ/640?wx_fmt=png&from=appmsg)

在"Vector Ocean"时代，数据生态融合了多样化的数据类型，如图像、文档、音频和视频。这些多模态、非结构化数据通过向量化后，成为不同维度的向量集合，进而存储于大规模、高效的向量数据库中。这个数据库内部采用多种不同的数据组织形式，包括传统的数据库表结构、键值对（KV）存储，甚至可能包括文档型数据库（Document DB）。存储这些数据之后，可以支持多种应用场景，如商业智能（BI）、数据流分析、人工智能（AI）、数据科学等。

DingoDB 致力于创建一个多模态向量数据库，能够整合结构化数据和非结构化数据的存储、分析与查询。满足用户对向量查询的需求，也能够保护和利用其现有数据，并强化对向量查询的支持。

**02**

**DingoDB****的产品优势和架构介绍**

**1. DingoDB 概览**

DingoDB 支持结构化、半结构化和非结构化数据的存储，提供与 MySQL 兼容的协议和优化器。数据库底层支持键值对（KV）和向量的存储，并采用分布式存储架构，实现多模态数据的联合存储和分析。用户可以通过 SQL 指令和 API 访问数据，并支持服务器端运算。整体上是一个完整的多模态向量数据库。

DingoDB 致力于解决大规模、多模态数据存储和分析的问题，提供海量存储能力和联合分析服务。面临的挑战包括多模态数据的统一分析和融合存储的难度、数据的高可用性以及服务计算与存储的一体化问题。DingoDB 旨在简化系统之间的复杂度，提供更有效的存储方案，为用户保障数据的可靠性和完整性，同时不断研究和解决业界面临的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNzovCL2UNiaNicr4icG2BX4wUQJFUIicUsicj6YjOCGS7p316nJYbTkIpiatw/640?wx_fmt=png&from=appmsg)

作为中国信通院首批认证通过的向量数据库，DingoDB 以卓越的产品能力完成测试，通过包括 27 个必选项在内的共计 39 个测试项目，通过数量远超同期测评厂商，成为当前通过项目最多的向量数据库。

当前，DingoDB 已成为 Langchain 项目官方支持的后端存储。

**2. DingoDB 特点**

DingoDB 的产品特点主要集中在四个方面：存储、SQL 处理、API 支持和数据分析。

* 在存储方面，DingoDB 基于工业级的 Raft 协议实现多副本策略，确保了数据的强一致性和安全性。这种设计也使得数据库容易扩容，降低了用户的成本并提高了性能与可靠性。
* 在 SQL 处理方面，DingoDB 提供了统一的 SQL 处理能力，支持 MySQL 协议和索引管理。数据库支持监控化和分解化的融合分析，允许对数据进行更复杂的查询操作。
* API 层面，DingoDB 支持多种高性能 API 接口，满足如决策制定等高频业务需求，便于用户直接进行数据分析。
* 在数据分析能力上，DingoDB 通过 Python SDK 支持多模态数据的混合分析，包括向量和标量索引的混合检索。数据库同时兼容多种处理器并支持算子下推，这是一项增强查询效率和性能的强大功能。

**3.****DingoDB****架构**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNp4YgEk2f0SGbGKSTO2EtasKXSBsibSwB74oNsVibF0TuwuyJMByzcI1Q/640?wx_fmt=png&from=appmsg)

DingoDB 的逻辑架构被分为多个层次。最上层是各种应用场景，涵盖了传统关系数据库分析、语义搜索、结构化和分解化数据分析等方面，以及实时数据决策支持、提示词管理、大模型记忆体等现代火热场景。

在接口层，DingoDB 提供了与 MySQL 协议兼容的 SQL 支持、高性能的 Serving API 以及原生向量 API 的支持。在 API 下面一层提供了高效的元数据存储和资源管理能力，紧接着是查询优化器和事务管理器，负责查询和写入调度的实现。

在执行层，DingoDB 具有一个多模态执行引擎。

在存储层，DingoDB 支持关系型表、向量表，并能够对接其他类型的存储如对象存储或分布式文件系统。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNFZnvttp0nvtdmiaeVFvboEqDgXf2rzR8SXcCrAAiceiagialicSPZAXxOKA/640?wx_fmt=png&from=appmsg)

上图清晰展示了 DingoDB 从应用层到底层存储的架构设计。

应用层：DingoDB 支持多种应用场景。

协议层：包括三个接入入口，一是支持 MySQL 客户端和 JDBC Driver 的 SQL 入口；二是提供高性能的 Java SDK，可以直接连接到存储层，满足实时访问需求；三是适应 Python 环境的大模型需求，通过 Python 或 C++ SDK 实现快速接入。

计算层：主要由两部分构成——Executor 是处理分布式事务和查询优化的分布式支撑引擎；Coordinator 作为协调器，负责元数据管理和资源管理。

存储层：底层是核心的存储架构，包括原始数据存储以及向量索引和标量索引的存储。此外，DingoDB 还支持向量的动态构建和计算功能。

**4.****DingoDB****产品优势**

DingoDB 的产品优势主要体现在五个方面：

* 全面的访问接口：提供 SQL、SDK、API 等多种访问模式，支持表格和向量作为一等公民的数据模型，允许用户灵活选择和使用。
* 内建的数据高可用：所有功能和高可用性都是内建的，不需要部署外部组件，极大降低了部署和运维成本。
* 全自动弹性数据分片：支持动态配置数据分片大小，能够根据用户设置的阈值自动进行数据分片的分类和合并，无需用户担心分布式数据管理。
* 标量和向量的联合查询：支持传统索引类型以及主流向量索引类型，无缝衔接标量和向量混合检索，使得检索能力在业界领先。
* 内建实时索引构建优化：根据数据规模变化和计算资源配置，自动重新构建索引以优化数据结构，提高访问效率，用户无感知地体验到索引更新的效果。

**03**

**应用场景介绍**

DingoDB 被应用于多种场景，包括企业知识库建设、作为大型模型的记忆体、实时决策的指标分析，并且支持 VectorOcean 数据支撑平台等应用。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNRI8IdhPuwt8rMayibWRLdVta10iclJXcmLhhTXiaOTVrnLiaicbEOCC9vJw/640?wx_fmt=png&from=appmsg)

在赋能大模型应用方面，DingoDB 的应用被分为四个不同的层次，涵盖了从数据到 Embedding Model的整个流程。包括使用业界公开或自研的大型模型和 Embedding 模型来实现数据的向量化。在向量存储层面用 DingoDB 支撑各种场景，然后再去对接大语言模型去实现各种应用。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNxY3APmib6obpemuusPzuY6t1XUX4Pvzuwa4lQfCUrw3qHCPXLBycIXQ/640?wx_fmt=png&from=appmsg)

知识管家是大模型时代，基于向量数据库和大模型的一个新的应用方向。DingoDB 为知识管家提供了强有力的支撑。知识管家主要负责企业的知识管理和创造，应用场景包括智能问答、内容创作助手、智能化工作流程、企业决策辅助等等。

关于DingoDB的进一步信息和开源代码可以通过 GitHub 获取。

http://github. com/dingodb/dingo

https://github. com/dingodb/dingo-store

https://www. dingodb. com/

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNRDWfraRSrSU8kV7ETibMaoRfXq0O7b5BqP3sY9zUTJGVgOKev1RITgg/640?wx_fmt=png&from=appmsg)

**以上就是本次分享的内容，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUiaUMwM8I3NYH3SVrllWIPIMQXDtN5DqCLRhFwFhR9RictLsYYBpOwibjfw/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia1liaGgibia9pewzZjUKNFqhNbVdMg8ibdH9bS0L8UibkBdbyN6iaxHHMdCjxWTaI5moxoxMIMxpXKD6lA/640?wx_fmt=jpeg&from=appmsg)

**分享嘉宾**

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

********孟圣智********

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

****北京九章云极科技有限公司****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**资深架构师**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

DingoDB 多模向量数据库主要设计者和开发者之一，拥有多年社区开源项目开发经验，在分布式数据库、Serverless 计算、虚拟化和容器平台、高并发系统设计方面有较深入的研究，对分布式存储系统和分布式数据库方向有独到的理解。

![](https://mmbiz.qpic.cn/mmbiz_png/dyDu14T9ZVADGkApd1vMFWR71Pfq5B2M05QDPzQwEDON9v1NXxF8nMhfnzbIXR0TIztaFkS9ibLU3lm1eZFwYqA/640?wx_fmt=png)

**DataFunCon2024·上海站正式开启！**

**本次活动共邀请了60+位行业专家参与分享，聚集了1000+技术从业者参与，在这里你可以做行业交流，生态合作，寻找投资机会，了解行业发展，了解落地案例，寻求解决方案，拓展人脉。**

**扫码咨询门票**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhvVATYibVSfTyknbdUSHb1tmFSttnl3Ib35mWtNxKYeGv083Via9C3xSYmmPWMasHtdSP663Rdha3A/640?wx_fmt=png&from=appmsg)

往期推荐

[央企大数据平台架构发展趋势与应用场景](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708939&idx=1&sn=5f143c84d73d3792d799e61d3e86ce49&chksm=fbd80367ccaf8a71e93763fb29a6ff1fd6685a476833e9d4e8db5a92a3ffc1b751cbf2b51b4e&scene=21#wechat_redirect)

[Sora揭示视频生成的未来](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708899&idx=1&sn=822360bc71334d46a37411d9e82e0a4e&chksm=fbd8028fccaf8b994052d07acbf14227a168a32f86e8f9e8a772fa4065f42333842464081c74&scene=21#wechat_redirect)

[画像标签体系构建与应用实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708766&idx=1&sn=88a59d3d338420539949d7264e7420f7&chksm=fbd80232ccaf8b24184854afeb6228a468013facbf044483b531cf1c79d6c61cea2b249a7bd7&scene=21#wechat_redirect)

[长安汽车：基于云器 Lakehouse 的车联网大数据平台建设](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708725&idx=1&sn=02acb66c626df248164e8a2ed9838ce4&chksm=fbd80259ccaf8b4f7ea60fb33c70c4a5aec7e747f3d4c7ef13d851e41120d71bb776de704836&scene=21#wechat_redirect)

[金融信创湖仓一体数据平台架构实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708653&idx=1&sn=04eac391b4647a13ea18ac05644aab93&chksm=fbd81d81ccaf94971a6dd0a43255d5a6599914dee8e8330312cdd2c6143bdffd9237d0e87c68&scene=21#wechat_redirect)

[新一代数据架构的性能与成本平衡之道](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708542&idx=1&sn=c986c18b59fbf1a599e14f6e490e7773&chksm=fbd81d12ccaf940496c419d4c667a09fe6f032236fba8834e8a2b465d0d356d97602fb6b5bc6&scene=21#wechat_redirect)

[用户画像构建与应用](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708530&idx=1&sn=f86e85382608d0dafb46eaa6139ac778&chksm=fbd81d1eccaf940846bc9227e2a6e92af7b407bfa2ce9b32d72579b75af40c4e35bd81e6e79a&scene=21#wechat_redirect)

[Data Fabric 在数据集成场景的实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708501&idx=1&sn=6aa213515d365fdfe32b9af8231c8cb1&chksm=fbd81d39ccaf942f3310509c501086d3343e7465ab79fa1938818bd82791d5598957835ca0b9&scene=21#wechat_redirect)

[如何从0-1使用 Apache Arrow 构建新数据系统](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708346&idx=1&sn=0c27d88c9f6a71f29b73a5b168ac07d8&chksm=fbd81cd6ccaf95c0c17aed85e5b6f47becf857180a11558d58a7a479f5553b921b069980ce15&scene=21#wechat_redirect)

[大数据分析平台之云原生 OLAP 架构的最佳实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247708287&idx=2&sn=9d401512ecc9270ed5e351db54003e77&chksm=fbd81c13ccaf9505043a7ce959c9c67145d006a0e2aecc83aac9bca7814dc6a86754c85b6e66&scene=21#wechat_redirect)

[B 站标签系统落地实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247707910&idx=1&sn=62d736d47f5f55e5ca6326d0e5955442&chksm=fbd81f6accaf967c8ace89162341e9ed4b36f4ce8d71dadbf909e8f6b1133bf4ef71ead3c241&scene=21#wechat_redirect)

[OLAP的统一及技术趋势：StarRocks 架构和实践分享](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247707595&idx=1&sn=d863b778560c86d418b1423f04e70f5f&chksm=fbd819a7ccaf90b10aa6f6c987dbc19138f1d260fd7048a1bdb8aeaceb3009a08092165d5a41&scene=21#wechat_redirect)

[快手基于 Flink on K8s 的生产应用实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247707436&idx=2&sn=26939102ea990c3066986f066599c954&chksm=fbd81940ccaf905653304899e2b95fcbbefa73dfff2b6451833deffd7fe90915d0d26313589b&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_gif/GFLQELzeHYjlPKyibC4DhCSLcOTB16IMjSHK1axEly55sBJ2ZL8gEY8SHnGEVq5ZiaksWtsT7easUBBoRcjib8DlQ/640?wx_fmt=gif)

![](https://mmbiz.qpic.cn/mmbiz_png/PekErwtg4WKmwH3eibyzzq6s8Y3mAfMqgg4oMDqNdgewSt6icvABmJGpFQ45Bic3oZZx5iaVXrYiasFZttZOx1ticcRg/640?wx_fmt=png)

点个在看你最好看

![](https://mmbiz.qpic.cn/mmbiz_png/lNwjBmeZOpwtYL4m6wWia6fPCyrOZiaygfADsajMnp7pkAQE6vg8w3bG9iae1AribdH3EQkrcO6ziaDhcBpl7ksCEkA/640?wx_fmt=png)