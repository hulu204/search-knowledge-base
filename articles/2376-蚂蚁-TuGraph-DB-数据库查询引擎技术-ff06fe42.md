---
title: '蚂蚁 TuGraph-DB 数据库查询引擎技术'
company: DataFun
tag: 搜索
date: 2024-01-17
url: https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw%3D%3D&idx=1&mid=2247704594&sn=9f3ea886f548409beea3b391ca64dbad
account: DataFunTalk
origin: wayback-wechat
---
**![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-001](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-001.png)**

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-002](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-002.gif)

**导读** 本文详细介绍了 TuGraph-DB 数据库查询引擎。

******本次分享包括以下三大部分：******

1. 图查询语言介绍

2. 查询引擎介绍

3. 架构及演进计划

分享嘉宾｜黄科 蚂蚁集团 技术专家 

编辑整理｜彭爽

内容校对｜李瑶

出品社区｜DataFun

---

**01**

**图查询语言介绍**

首先来介绍一下图查询语言的发展历程，大致可以分为三个阶段：图数据库起步、图查询语言起步和图查询语言迭代。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-003](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-003.png)

第一个阶段从 2000 年开始，当时还没有图查询语言。Neo4j 希望以 network 的形式，也就是图的形式，去构建数据。当时图数据库的概念还不普遍，当然图的概念可以回溯到上世纪 70 年代甚至更早。在这一时期没有查询语言，因此是使用 Java API 去做，使用 2-3 个接口获取点，然后基于一个点，获取它一度的初边，以这样的形式描述一个图查询。现在看来，无论是 TuGraph 还是 Neo4j，图查询的过程都是遵循最初做图查询的思路，就像 TuGraph 最初也是先有一个 API 的层次，再在上层搭建查询语言。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-004](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-004.png)

第二个阶段是图查询语言的起步和发展阶段。最早是 Gremlin，然后是 Neo4j 于 2011 年发布的第一个版本的 Cypher。2012 年 Cypher 成为声明式语言，也就是大家现在习惯使用的通过起点和路径描述查询的方式。2015 年后图查询语言有了迅猛的发展，先是 Oracle 的 PGQL，之后 Neo4j 将 Cypher 开源为 openCypher。2017 年前后 TuGraph 开始加入进来，也是以 openCypher 的标准做了查询语言。2018 年 Cypher 形式化语义的论文发表 Cypher2018。大部分现已成熟的查询语言、图数据库，都是在这十年间如雨后春笋般发展起来的。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-005](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-005.png)

第三阶段就是我们现在正在经历的图查询语言迭代阶段。2019 年开始，GQL 成为了国际标准，开始致力于统一不同图查询语言的标准。到了 2023 年，TuGraph 也开始逐步实现 GQL。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-006](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-006.png)

上图中罗列了各种查询语言及其厂商。这些查询语言可以分为两大类：声明式（Declarative）和命令式（Imperative）。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-007](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-007.png)

声明式图查询语言，包括常见的 Cypher、PGQL、G-CORE，当然 G-CORE 没有具体的实现，但是它的设计是源自于 Cypher 的。这种声明式的语言更加类似于 SQL，更强调查询的目的，而不是查询的过程，比较依赖于查询优化。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-008](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-008.png)

命令式的语言，比如 GSQL 和 Gremlin。严格意义上讲，它们是混合式的，因为也会有 select from 嵌入在自己的语句里面。从形式上看，它们更像 Python 这样的语言，因此它们会做的事情更多，这也就意味着用户学习和使用成本会更高。其实与声明式语言的区别在于，具体优化过程是由人来做还是机器来做。比如如果对图了解很多，能直接写图的存储过程，那么使用 GSQL 就会更方便。命令式语言最大的特点就是能写更复杂的图计算能力，例如 page
rank。当然，用存储过程去做，再嵌入声明式的语言，也可以实现类似的能力。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-009](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-009.png)

再来讲一下前面提到的国际标准 GQL。GQL 在设计上参考了 openCypher、PGQL、GSQL 和 G-CORE，但其核心思想基本上都来自于 openCypher 语言，所以它是一个声明式语言。蚂蚁内部，TuGraph 和 GeaFlow 两个产品都有接入 GQL。长期来看，GQL将会统一声明式查询语言。十年后，就像关系型数据库只有 SQL 语言一样，图数据库声明式语言中也会只剩下 GQL 这一种语言。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-010](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-010.png)

现阶段，GQL 还有很多问题，语义方面还没有讨论得非常明确，描述能力也比较有限。比如 FINBENCH，就是看查询语言或者图数据库有哪些瓶颈。上图中展示了 FINBENCH 里面的 complex-read1，金融场景里面查资金流向是比较常见的，比如从一个起点查一个账户，访问出度1-3度的边，就是一个不定跳的过程，如果是资金交易，会有时间要求，比如这笔转账流水是一个时间递增的序列，现在的声明式语言还不能很清晰地描述这种不定跳加时间递增的情况。

考虑到 GQL 将会在图数据库领域实现标准化，蚂蚁现在对 GQL 支持的力度是很大的，除了 TuGraph、GeaFlow 能支持 GQL，其它一些还没有开源的产品基本上也以 GQL 为方向去做接入。

**02**

**查询引擎介绍**

接下来介绍 TuGraph 4.0 图查询引擎。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-011](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-011.png)

其实在 4.0 版本发布之前，我们 GQL 的语法文件就已经开源了，放在 TuGraph family 里面。4.0 版本实现了 GQL 的能力，当然能力仍比较有限，目前支持 SNB 和 FINBENCH 所有的 SHORT 查询。具体实现可能和开源的语法文件有一些变动，这也是我们认为 GQL 本身不成熟的地方，现在是两个分叉，未来一两年之后，这两个分叉再合并。

近期我们有两项重要的计划，第一是完善 GQL 语法的支持范围，目前仅支持 SNB 和 FINBENCH 的一些最基础的东西，之后会尽快增加比如 DDL 等更多方面的支持。另一件事是架构上的改造，引入一套全新的 GEAX 优化引擎，其目的是希望做一套更通用、对开源社区更友好的优化引擎。

其它方面的计划包括，加入更加完善的 Test Suite 和相应的工具，以及使用查询语言去打榜 SNB 或者 FINBENCH。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-012](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-012.png)

提到 SNB 和 FINBENCH，基准测试对于数据库或者查询引擎来说都是非常重要的，但并不是衡量一个查询语言的唯一标准。查询语言的评价维度包括性能、描述能力、健壮性和查询优化等等。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-013](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-013.png)

比如查询优化，最简单 Cypher 写法 1 相较于写法 2 更易优化。如果要打一个很好的榜单，一定会用写法 1 的形式，因为写法 2 不一定会优化到，但最终用户使用写法1的体验和效果可能会很差。因此我们对于查询语言的要求会比打榜更高一些。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-014](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-014.png)

TuGraph 的具体使用方法，**可以参见以下链接：**

**03**

**架构及演进计划**

下面介绍一下现有的架构，以及后期在架构层面可能会做的改动。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-015](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-015.png)

上图是 TuGraph 现在最原始的架构。查询进来，解析到 AST，然后可能有一些验证，到 Planner 出来一个执行计划，根据一些 Schema 信息或者一些统计信息进行优化，之后放入一个执行引擎里面去执行。

目前有两个最大的问题，第一是要支持多个查询语言 Cypher 和 GQL。万幸的是，虽然 GQL 是一个全新的查询语言，但其总体思想来自于 Cypher，体系上可以理解为一样，因此我们可以做到对两种语言的支持。

另一个问题是要支持更多的存储引擎，目前 TuGraph 是一个简单的单机版本，蚂蚁内部已经有分布式的图数据库和一些图计算系统，需要将这些不同的存储引擎都接到我们的查询引擎之上。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-016](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-016.png)

关系型数据库和图数据库的层次是比较接近的，因此我们参考了 Calcite 系统。Calcite 是一个完整的查询处理系统，能够提供 DBMS 所需要的许多常用功能，甚至可以接近一个图数据库系统，支持完整的查询语言的优化、解析、验证。我们参考它的架构去做一个类似的处理系统，实现更丰富的算子，在图的优化上能做得更多。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-017](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-017.png)

参考这个架构，我们会做 TuGraph 下一个版本的查询引擎的改造，这个改造是在整个执行引擎之上的一层改造。参见上图，右边是 Data Processing System，和 Calcite 的设计类似。左边 GeaX 中有几个核心的模块，第一个就是图语法表示（GST），Quary 解析完之后，这里加了一层抽象，这层抽象能够保证同时支持两个相似的语言，比如 Cypher 和 GQL。同时有一套独立的逻辑算子，能够描述整个查询，有单独的优化器，这里的优化器也支持可插拔的功能。这样整个系统就分为了两部分，前面的查询语言的处理，以及后面的计算和存储。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-018](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-018.png)

GeaX 为 TuGraph 提供处理和优化图查询语言的能力，其特点包括，架构与 Calcite 相似，支持查询语言解析、校验、优化。严格意义上 GeaX 不算是一个图计算引擎，因为它把计算的部分全部剥离了，最终产出的是一个逻辑执行计划。另外，GeaX 支持多语言，支持不同的优化器，这些优化器是可插拔的，不同类型的优化器有不同的规则。GeaX 的目标不仅仅是作为一层查询语言接在 TuGraph 上，还能够实现轻松地将 GQL 查询语言接到任何一个图相关的引擎上，比如一个人一个月就能够为 GraphScope 提供 GQL 的能力，这样也为 GQL 成为统一的图声明式查询语言提供帮助。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-019](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-019.png)

通过上图的对比可以看出，GeaX 和 Calcite 在框架设计上是比较接近的，当然具体优化器的能力会有不同，这也正是 GeaX 框架的优势之一，可以放不同的优化器在这里。

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-020](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-020.png)

这个架构是我们未来 3-6 个月要去做的事情，现在已经迈出了第一步，实现了 geax-front-end。目前 parser 这一层已经实现。大概在 3-6 个月左右会有一版迭代，可能会有 GeaX 的出现。我们希望能做一个很简单的 play ground 给用户用，用户能在对 TuGraph 没有很多了解的情况下，尝试去看 GQL 的查询语言生成的逻辑执行计划是什么样的，通过看逻辑执行计划，判断这个查询是不是复杂，是不是可以去增加一些优化规则。

**以上就是本次分享的内容，谢谢大家。**

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-021](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-021.gif)

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-022](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-022.png)

**分享嘉宾**

INTRODUCTION

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-023](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-023.gif)

********黄科********

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-024](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-024.gif)

****蚂蚁集团****

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-025](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-025.gif)

**技术专家**

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-026](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-026.gif)

蚂蚁集团技术专家，负责 TuGraph-DB 数据库查询引擎的开发。

## 

 优质内容推荐阅读

往期推荐

[如何将知识图谱与AIGC结合？京东是这么做的](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247704367&idx=1&sn=4bd85affff9c1204e6792ca8a1f68b36&chksm=fbd86d43ccafe455b4941c53edad3869e8bea6a68c0293ce35fdbd8f0c8212c64fa3c881b15e&scene=21#wechat_redirect)

[如何使用 JIT 技术实现高效的数据库表达式求值](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247704166&idx=1&sn=45d5dc41bc4ff48a606a25f01cda9730&chksm=fbd86c0accafe51c9982c2c79c15b57709492df9ef9675900394c91dbbbb65ccf4dc6ed19005&scene=21#wechat_redirect)

[Alluxio 在网易大数据的应用与优化实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247704126&idx=1&sn=5da48f987992e41a786aaf242e090cf7&chksm=fbd86c52ccafe5447ea09ed0b02b78c7fcfe46798b6230e5a439b4e069958803d1f7a29b55cb&scene=21#wechat_redirect)

[数据集成产品的技术演进与实际应用-FastData DCT](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247704120&idx=1&sn=fc54c998152a96ebd9d4bad5fff9d0e1&chksm=fbd86c54ccafe54253b9a93a4cb3fb3f9f7c5485ef55ab72b79d5fb5aa73125ce37d49aad0ef&scene=21#wechat_redirect)

[深度剖析! 广发证券 Apache Kyuubi 构建“提效可控”大数据赋能层](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247703989&idx=1&sn=8439b9c500862cae25f626cf95a78e1b&chksm=fbd86fd9ccafe6cf58443870b41b2b38be5f15f25fbf6f6fd08d219c8b7b21a226e8c273e66e&scene=21#wechat_redirect)

[重新定义流计算：第三代流处理系统 RisingWave 的 2024 年展望](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247703401&idx=1&sn=08d595fb59a31bf014bd0efd0eb23ade&chksm=fbd86905ccafe013c80bc7fa25e6c3c7a3a4065111d270957fab2fb9916230464af22d5396e4&scene=21#wechat_redirect)

[阿里云湖仓存储系统设计剖析和性能优化](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247703376&idx=1&sn=a155a814f1cf126d9f30ae93ca1fe377&chksm=fbd8693cccafe02afec76214b7d28a315312044bdaca71aab3173fb9f1866c6480096131fe9a&scene=21#wechat_redirect)

[滴滴大数据成本治理实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247703298&idx=1&sn=4c93dd9460b2af16fd5da8556387f540&chksm=fbd8696eccafe078de38bbd8b05b6b6affb09419319e07f616fd4eeaebdbc42e36bc30ee3272&scene=21#wechat_redirect)

[百度推荐排序技术的思考与实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247702263&idx=1&sn=7378ae0412e88210e9f17b3be93fe812&chksm=fbd8649bccafed8d6b059e6c9b12eabafce6f0a5bdedcb37c88be8673bfebc4aa55b021bd815&scene=21#wechat_redirect)

[蚂蚁营销推荐场景上的因果纠偏方法](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247702137&idx=1&sn=49955e2983631aaec85f906c3c322c29&chksm=fbd86415ccafed036cc98e51a1e6914e46bd076d3ead46e95caf514273b48dbca609b61fedcd&scene=21#wechat_redirect)

[使用 OpenLLM 构建和部署大模型应用](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247701948&idx=1&sn=9284ae9ed4000909be5a8860268d483b&chksm=fbd867d0ccafeec652f3fa2c9e8b38b0bb0c2d6c321806f1ff28bb67ee3fd92bfc8148865400&scene=21#wechat_redirect)

[OLAP 的技术研发与思考--ClickHouse 2023 总结和 2024 展望](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247701908&idx=1&sn=473d0d2992507e502fa3238d2b9048c3&chksm=fbd867f8ccafeeeebac7653e06ed3693fc03bc658da4b98c7b2667eadcc50af3bacdd7ca6bb4&scene=21#wechat_redirect)

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-027](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-027.gif)

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-028](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-028.png)

点个在看你最好看

![2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42-fig-029](../images/2376-蚂蚁-TuGraph-DB-数据库查询引擎技术-ff06fe42/figure-029.png)