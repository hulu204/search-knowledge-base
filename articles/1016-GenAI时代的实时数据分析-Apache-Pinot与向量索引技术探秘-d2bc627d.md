---
title: 'GenAI时代的实时数据分析：Apache Pinot与向量索引技术探秘'
company: DataFun
tag: 索引构建
date: 2024-08-16
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247737433&idx=1&sn=3e6f39e600ba0bbd468bf8128cc1058b&chksm=fbd89235ccaf1b233ca0af587b4c08dd0cfccd26c25806d325a362de5da79a922aed874c1a2b#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaPpRlN4EwcNHsvy9YckZMVGh3Wr7G1xXHnClg4RibhtGpWFewjvSY4XjDf1smdeppfLIMIib0IDI8Q/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaPpRlN4EwcNHsvy9YckZMVj08w3iazHTuicQNPeIGHPOqMico63vo6UKD0lTDMCrMDyzqib4casHFr8Q/640?wx_fmt=png&from=appmsg)

**导读** 本文将分享如何使用 Apache Pinot 将实时数据分析和检索增强生成 RAG 结合起来。

****主要内容包括以下四个章节：****

1. 实时 OLAP 的兴起

2. Apache Pinot 体系结构

3. Apache Pinot 对 AI 的支持

4. 总结

分享嘉宾｜付翔 StarTree 联合创始人

编辑整理｜菊

内容校对｜李瑶

出品社区｜DataFun

---

**01**

**实时****OLAP****的兴起**

**1.****数据价值随时间的变化**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LquiaUtAM4SNRWw5ZtPaP6AoibmdSuowcFnUprjgcB2m3BNibxbTrria7QtA/640?wx_fmt=png&from=appmsg)

如上图所示，可以看出，对于单个事件来说，数据价值会随着时间逐渐降低，比如，用户对小红书上某个帖子或淘宝上的产品发生了点击行为，之后就会有相关的产品或广告的推荐，以及进行步更多的链接、视频等各式各类的推荐，推荐的效果在点击发生当时最有用，之后效果会递减。同时，由于有很多人有类似的数据，我们可以在这些数据上做一些聚合分析，这类聚合分析的价值会随着时间和数据量的增加而增加。之前我们会把大部分的时间和精力都聚焦在这类批式的后处理的分析上，而对实时数据分析的关注较少。

随着实时机器学习以及数据分析应用的发展，实时数据的价值越来越多地被挖掘出来。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqCRJumtiaCbWGCf8QlyXJkdETU3jYelmKaIRKqM3XtnzJHaib8BicWfROg/640?wx_fmt=png&from=appmsg)

过去，数据分析更多是面向公司内部的分析，比如运营数据分析等；未来，数据分析将更多用来服务最终用户。比如，推荐算法，本身就是用户自己的数据来训练模型，通过把用户的数据变为产品又给用户使用，完成整个数据的生命周期，并且能给用户更好的体验。

**2.****实时数据分析边界拓展**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqW5ejK4pnWo1U5WEVcibrrVEg6ecD60WIlzI15iaXHWhyP4Oknpw6qeVQ/640?wx_fmt=png&from=appmsg)

实时数据分析的边界也在不停地拓展。比如：

* 在应用上，由面向内部的数据分析变成面向用户、面向对象的数据分析；
* 在数据的结构上，从结构化数据（如 SQL 表，定义好行列的数据类型）变成半结构化数据或非结构化的数据（如文本数据、Json 数据），甚至对于音频、视频的数据，可以把它们做成 embedding，存入数据库以进行更多的分析和查找；
* 在数据准确性上，对查询的准确一致性支持也更强；
* 在分析的复杂度上，原来只能做一些特点维度或切片的分析，未来可以支持复杂的 Full-SQL 语义的实时分析；
* 在数据量级上，从 TB 级增加到 PB 级；
* 在使用场景上，从特定的应用场景，到用户可探索的场景，包括机器学习和 AI 相关的各类应用场景。

**3.****典型的数据分析技术栈**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqDWWC3icjWZ6JdRdhfa0C1bybGUJVmibLlJ96RwkwQl0bMCg7By5ToVgA/640?wx_fmt=png&from=appmsg)

上图是一个典型的数据分析技术栈。左边是数据的生成端，在各种设备上，生成各种原始数据；中间是基于用户或产品特性的数据，比如，电商的订单数据，广告的事件数据，这些数据存到 OLTP，如 MySQL 数据库中，或 Kafka 的消息队列；接下来，OLAP 分析端，离线分析端一般会将 ETL 来的数据，存入数仓或数据湖里，实时分析端一般从 Kafka 直接消费进入实时数据库中。这里的目标是低数据查询延时、高数据查询精度，并支持更大的查询量。

**02**

**Apache Pinot****体系结构**

**1.****Apache Pinot****简介**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqBaY5mFgiaIsPe8L9cG6YtS6wyYHMBRr7hcF85HEW7VWjHXFvlJKFhgQ/640?wx_fmt=png&from=appmsg)

Apache Pinot 是一个支持高可用、高并发、低延时的快速实时分布式 OLAP。为了方便处理互联网上的用户数据，Apache Pinot 是采用列式存储的 OLAP，并且可以与 Kafka 集成起来，进行实时数据处理。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lqmkzkd4Kb8YPK9bMKB3fSp6WghUY2LVHcEPl3mqSdeTeGPyh4xD1Diaw/640?wx_fmt=png&from=appmsg)

Apache Pinot 已在一些大公司里被使用。在 LinkedIn 支持每秒上百万事件，20 万 QPS 的毫秒级查询；在 stripe 上，支持单表 1 千亿行，数据量超 PB，2 万 QPS，25 毫秒查询延时；Uber 也是对实时性要求很高的应用，用 Pinot 来实现地理信息的查询。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqD3tYdF9of6j4jP32MCyWs0LLs8FpRJyCAEwDv4cX2owKZsibDz0y1zg/640?wx_fmt=png&from=appmsg)

Pinot 是 Apache 基金会的项目，所有内容都完全开源，很多公司都在使用，如上图所示。大家如果有兴趣，也欢迎试用，并在社区中交流。

**2.****Apache Pinot****架构**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqFQiaSPyr0aH46hmKsrRvic8v2oo5Qty5GSD0sJY4GapsSXbiaylUwH8Rg/640?wx_fmt=png&from=appmsg)

Pinot 采用 Lambda 架构，架构图所示，包括：

* Pinot Controller。作为集群和数据管理。使用 Zookeeper、Helix 来进行集群和数据的管理，使用 Restful API 来进行沟通。
* Pinot Broker。作为 Pinot 的查询层，所有请求先到 Broker，再通过它分配给具体的离线和在线服务，分别查询，之后再将结果合并起来。
* Pinot Server。分为在线和离线数据服务器，在线部分直接从 Kafka 消费数据，离线部分可以从离线和远端存储层读取数据；
* 离线数据存储（Segment Store）。离线部分的数据存储在远程 HDFS、Amazon S3 等比较便宜的存储上，作为备份和分层查询使用；
* 实时数据导入(Real-time Ingestion)。从各种实时的数据源（如 Kafka、Kinesis）把数据消费进来，实时消费的数据会被写到本地数据服务器并且上传到离线数据存储用于备份。
* 离线数据导入(batch
  ingestion)。离线数据可以通过微批任务，把原始数据读出后，再写到离线存储中，然后就可以通知集群，将离线数据下载供查询使用。

**3.****索引**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqEF7dKWsA3ibzTUUlbOHA2BPudmwXSMmQplf2MxRdYFa3YbIxBRLZmSg/640?wx_fmt=png&from=appmsg)

为了支持低延时、高并发的查询，Pinot 的工程优化目标是尽量减少单次查询需要扫描的数据量。

为此 Pinot 实现了很多索引来帮助缩小查询范围，包括常见的反向索引、排序索引，以及对于特殊数据格式和类型的索引，如区间范围的索引、半结构化 Json 数据的索引、地理信息的索引等。

同时，对于聚合查询，相比于对于全维度的预聚合，Pinot
内部可以根据维度的，动态的聚合结果，使得查询效率更高。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqOH8wdvjvCib8WlUBdOAvqhn8MX0icsiaQic22AOziakSM2N0bvFGY1UTJBQ/640?wx_fmt=png&from=appmsg)

**4.****可插拔架构**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lq35jlZVNAiaiaDI72vOIYGnpXlRTBHyPhibdOBWmgQ1ibMw6PNJvicaiaQQCw/640?wx_fmt=png&from=appmsg)

Pinot 采用可插拔架构，查询层、索引层、存储层都支持 SPI 接口，用户可以方便地在 Pinot 上进行二次扩展开发。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqEibY1PL3ibJH9mbQTcSWMSKEpnwEcsnRSRIfUxiaGlBJ516OL0oWq48kQ/640?wx_fmt=png&from=appmsg)

上图展示了 Pinot 的可插拔架构。基于 Pinot SPI 包，开发者可以配置开发自己的数据存储、输入格式、流式引擎、索引、查询等。开发者只需要写一些简单的实现，就可以构建、打包然后应用，非常方便。比如，作者仅花一周左右时间，就实现了向量索引功能。

**03**

**Apache Pinot****对****AI****的支持**

下面将介绍在 AI 时代，Pinot 如何支持 AI 应用。

**1.****Pinot****作为向量数据库**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqCu7RjTUN7jAqG77M1gdH8z2dCSIDRT1Gnuhz3q6SNZtB7aeoqhfjlA/640?wx_fmt=png&from=appmsg)

Pinot 可以作为一个向量数据库为 AI 提供 Embedding 数据存储以及向量检索。

Embedding 可以看成一个浮点数的数组，存到数据库中。有了 Embedding 向量后，当一个向量进来，需要查询和这个向量最相似的 K 个结果。

这类应用场景有很多，如常见的搜索场景和推荐场景。

例如二手车搜索场景。用户可能会去二手车网站，搜索想要的车。在搜索过程中，用户会有很多偏好，比如喜好品牌、年份区间、价格区间、颜色、天窗等。直接使用筛选的话，结果可能过多或过少。我们可以把用户搜索的偏好描述，作为一个 Embedding，存入数据库。然后根据用户偏好描述，返回一个与描述相似的 topK 排序，展示给用户。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqhfeEVhlVRSLRhcHpFVIFFgeN9jAB79skb4cVplYroHU0ibrY4ZGoDicA/640?wx_fmt=png&from=appmsg)

用户推荐餐厅场景。可以根据用户历史喜欢吃的东西，同时结合用户当前的描述，生成一个 Embedding，存储起来。然后根据 Embedding，给用户推荐和他偏好相近的产品，这可以得到更好的用户产品体验。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lq0TGh9LgZvhKxIb1c1bYln4Ks9lqGPicMcPiahj8l0LtkDbXPz1rbUzhg/640?wx_fmt=png&from=appmsg)

**2.****实时检索增强生成****RAG**

为什么需要实时呢？比如问 ChatGPT，“在足球界，药厂是什么梗？”，回答“勒沃库森”“但至今未能获得联赛冠军”，而熟悉足球的小伙伴会知道，“勒沃库森”在 2024 年第一次获得德甲联赛冠军。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lqup2BBqW8tcxL9Qh9mJV6JOoLM7pYiaxO0VU1OrVm2dq14Bdn7zicZqiaw/640?wx_fmt=png&from=appmsg)

因此，可以看出 LLM 模型和数据都是有时效性的，如果没有最准确最实时的数据，可能获取不到准确的结果。通过 RAG 和实时向量数据库的帮助，模型可以提供更实时和准确的结果。

**3.****用** **Pinot****实现实时****RAG**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lq4ShQegZnmdVSKNI4iaIzLB84NN74Xr7OPOL2IOraWHrfmAL6IKPEpXw/640?wx_fmt=png&from=appmsg)

为了实现实时 RAG，在向量数据方面，我们需要通过将原始数据变成 Embedding，存到向量数据库中，从而提供给用户查询。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqkrcGtzSFRkqk1pJuLc1OH2fhcH3A1uSabibia8ZGKASsCjVicpib9CWJfA/640?wx_fmt=png&from=appmsg)

上图是一个一般的流程，用来实现用户回复中对于实时数据的要求。

将原始文本文件、音频或照片根据 Embedding 模型，得到他们的 Embedding 表示，写入 Kafka 并存入 Pinot，这样实时的数据流就变成向量进入了向量库。

对于一个用户，将他的问题，也转换成对应的 Embedding，然后通过向量相似性搜索，就可以找到一堆类似的数据；这些数据称为加强上下文（Enhance Context），也就是把相关的文本和用户本身的问题合在一起，交给 Prompt，再通过 LLM，生成给用户的回答。

通过这样的数据处理，可以将实时数据流与 RAG 结合起来，达到更好的准确性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lq0OR51yQnJUf3ibibBduluxANafUVwSEf0CEWj2QvgK0ia9J7ghXdkalKQ/640?wx_fmt=png&from=appmsg)

Pinot 提供了很多向量计算的支持，比如距离计算函数，支持 L1、L2、余弦、点积等距离。可以根据不同的用户场景，选择不同的距离计算方法，达到不同的效果。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqF6XW2ONH3AnlEAy7dHpgcC6dRfiaxsvA0um7Fk7jzVsKmgvp9tSuerw/640?wx_fmt=png&from=appmsg)

Pinot 通过向量索引可以提高查询效率。采用 HNSW 算法，来建立向量索引，然后通过多层迭代的方式，帮助用户输入的向量，找到离它最近的 n 个向量。这样相对于全表扫描对每个向量都计算一个距离的方法，计算复杂度大幅降低。

而对于开发者来说，这个查询也很简单。如上图右边代码所示，定义了算法使用的距离，以及向量相似度查询的语句，返回 10 条最近的结果。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqP8VF0JFHVQ9x4IcmQgZXu3cic8GRSCPkTlSVWAGAVLMEbv7s06qGUDQ/640?wx_fmt=png&from=appmsg)

算法在不同数据集上的性能表现如上图所示。我们使用了 Lucene Benchmark，采用 Lucene 的 HNSW 算法的实现。大家也可以点击链接去看看不同算法的实现和性能，因 Lucene 也是开源的，我们会跟社区一起进行性能优化。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhUcKIv2buL7j98CDXao6LqTicZicSXCHkPpCh0mbBiaK3nib6IicdO6j3DLia3WypOayjefmXR3hcXoYmg/640?wx_fmt=png&from=appmsg)

通过混合负载，可以将 OLAP 和向量数据库结合起来，以实现维度数据的过滤，并结合其它数据，提高 prompt 的准确度。

比如，用户可以有产品评价数据的 Embedding，也有产品本身的特征，比如 SKU\_ID，类别等。在做向量查询时，需要根据类别等维度特征过滤，再做相似性查询，查完的结果合起来，输出给 Prompt，进行后面的反馈生成。

**04**

**总结**

最后，对本次分享的主要内容进行一下总结。

* 通过实时 RAG 可以帮助用户获得更好的用户体验；同时，用户也可以使用他们自己的数据来辅助结果生成。
* Pinot 作为一个实时向量数据库，可以提供更加实时准确的查询。
* Pinot 通过结构化数据和半结构化或非结构化数据的混合负载，一起为用户提供数据分析与应用服务。

**以上就是本次分享的内容，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUiaUMwM8I3NYH3SVrllWIPIMQXDtN5DqCLRhFwFhR9RictLsYYBpOwibjfw/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhUcKIv2buL7j98CDXao6Lq8kpJUufICMnvR0M6HmHZYkALedQcqWJ5H5hn78kvicziccWfG1bSdwCQ/640?wx_fmt=jpeg&from=appmsg)

**分享嘉宾**

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****付翔****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****StarTree****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

**联合创始人**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

付翔是一位经验丰富的软件工程师和企业家，目前担任云原生数据分析 SaaS 公司 StarTree 的联合创始人。

在创建 StarTree 之前，他作为 Uber 流式数据平台的架构师，在技术行业做出了重大贡献。在那里，他应对了数据服务、处理和分析方面的复杂挑战，支持了 Uber Rides、Uber Eats 和 Uber Freight 等各种应用。

在加入 Uber 之前，付翔在 LinkedIn 主要负责 Apache Pinot 的开发。Apache Pinot 是一款开源分布式的实时 OLAP 数据库。他也是 Apache Pinot 的创始人和项目管理委员会（PMC）成员。

付翔于清华大学获得了电子工程的本科学位，之后在佐治亚理工学院获得了计算机的硕士学位。

活动推荐

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaPpRlN4EwcNHsvy9YckZMV4tGSCmHQL4A9uAbfz2uwtdA35BNTB8YGvIaQ64ib1wjsJjYAbIwDxyA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPiaPpRlN4EwcNHsvy9YckZMVZTicKWhqOrL6vg45pEick32rR3lZS7YoXOKsSj2LyOkibIeFVmozvD1PA/640?wx_fmt=jpeg&from=appmsg)

往期推荐

[金融，大模型落地的关键场景！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247737263&idx=1&sn=2b75d2896fa2cd748a60df8c85a12517&chksm=fbd8edc3ccaf64d55e6b457ae2a67b346b193848508ef9b2097973edad5eb46f220b831c9cc1&scene=21#wechat_redirect)

[打造 LLMOps 时代 Prompt 数据驱动引擎](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247736296&idx=1&sn=26456430b2d71363d6ae881ef3c6e25a&chksm=fbd8e984ccaf6092326125340fb66fa074ea4069faeb67f61fc236bed7a84424467546d09dfb&scene=21#wechat_redirect)

[基于大模型的数据治理应用新范式](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247736201&idx=1&sn=ab8e8a67a6d17657b290d302faed204d&chksm=fbd8e9e5ccaf60f3006acd29794f216edcf69865c232be3a64059a6effd22b8a0838175ad901&scene=21#wechat_redirect)

[阿里云智能大数据演进](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247736015&idx=1&sn=f1064e9849c95006c41e5b024e97cdd3&chksm=fbd8e8a3ccaf61b5b5ae818cf33d03cdc90aa1ffa619582177e57c1a01065bdebc342d945ea8&scene=21#wechat_redirect)

[Agent+Copilot：大模型在智能运维领域的应用](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247734999&idx=1&sn=b45b981dd4ad43a05385ab46b0f0d94b&chksm=fbd8e4bbccaf6dad5d9eab547f8411a6ac2c76682393a2e4db1d26910b19c0613199b006ff59&scene=21#wechat_redirect)

[从0到1，掌握大模型RAG技术原理与应用](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247734954&idx=1&sn=7d3bc7d9c1090905125f0319494a4674&chksm=fbd8e4c6ccaf6dd068f0ec12d066daaa4da1bc4e72e95a2e723dd027cf72e5281f3d8304cef2&scene=21#wechat_redirect)

[社交传播和影响力算法在腾讯游戏中的应用实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247734871&idx=1&sn=d884a4bff92eeb634f0649684bd37fd2&chksm=fbd8e43bccaf6d2dc3ca26f889e7fea1ba612341b2bc28e237c1b3ca4d3ea08e076f52285f9b&scene=21#wechat_redirect)

[多场景多任务统一建模在网易云音乐的算法实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247734622&idx=1&sn=392276910ae8b49364ea803dc3d118a5&chksm=fbd8e732ccaf6e24c4d64c00fa22ce2a647b756b26c4fcaa0f33eed60a5711cb6d24e10dfb49&scene=21#wechat_redirect)

[Data+LLM：数据治理新范式探索](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247734395&idx=1&sn=4c72a3c19b26d3d49e615aee1b44b673&chksm=fbd8e617ccaf6f01d89d37ee2efe426eea330bd96976e0d838238b386a9f1ae42bf801c4d939&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640)