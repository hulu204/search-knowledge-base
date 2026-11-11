---
title: '7倍性能提升｜阿里云AnalyticDB Spark向量化能力解析'
company: DataFun
tag: 召回
date: 2024-08-15
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247737263&idx=2&sn=d2ee5c9ad02721b33d40ee870eb40d89&chksm=fbd8edc3ccaf64d51e6ca2a90f1fa38be06123beac9fd9a1ddceae6982281635a6b75d3d9221#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT8fCxgG5FDL5ajxpNUFwpSibQNiawaf8PzDCTF0m323iaBUaZJpTUuk2aQ/640?wx_fmt=png&from=appmsg)

**1. AnalyticDB Spark产品架构**

AnalyticDB Spark（后简称ADB Spark）是在**阿里云瑶池旗下**的**云原生数据仓库AnalyticDB MySQL**产品架构下提供的开源Spark引擎，用于满足客户复杂的离线处理场景和机器学习场景。

▶︎ ADB Spark上层面向用户提供多种调度入口，包括控制台，DMS以及Spark常用的spark-submit脚本等。

▶︎ 中间的管控服务提供资源、元数据、多租户以及安全管理等能力。

▶︎ 下层提供弹性Serverless形态的Spark，Spark集群通过统一的元数据服务管理库表信息，并通过统一的管控底座申请弹性资源。

▶︎ 底层是ADB Spark支持的数据源，一类是OSS/MaxCompute等通过AnyTunnel/STS Token进行授权访问的数据源，另一类是用户VPC下如ADB/RDS/HBase等需要通过ENI弹性网卡技术打通不同VPC网络才能访问的数据源。

整体架构图如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwTT9ayaameDAibFicQwxrNCuOb3Q8lgyzibvEcoyZfHGAypH5frYEJtnnXQ/640?wx_fmt=png&from=appmsg)

本文主要介绍在当前架构下，ADB Spark如何通过向量化引擎提升性能。优化后的ADB Spark是开源Spark性能的**6.98倍**。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT8fCxgG5FDL5ajxpNUFwpSibQNiawaf8PzDCTF0m323iaBUaZJpTUuk2aQ/640?wx_fmt=png&from=appmsg)

**2. 为什么做Spark向量化计算**

Spark当前已经是比较稳定成熟的项目，自从Spark 2.4以来，算子级别的优化十分有限。大多数的优化工作都在执行计划方面，如AQE、动态分区裁剪等。算子计算的速度已经达到了瓶颈。如下图是Spark各版本的HashAgg、HashJoin和TableScan算子性能情况（越高表示性能越好）。在现在的Spark架构下Spark很难获得重大的算子级别的性能突破。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwTz1nPZ9OJDeo91yQ41kRopgAuOWA9nQTZwt1CibKwVYBDFR5xehBqbAw/640?wx_fmt=png&from=appmsg)

现代的SQL引擎常常能有更好的算子性能。如ClickHouse、Arrow等，这些在Native引擎的实现中使用列式数据结构、向量化等优化，有着比Spark的Java栈的行式处理更好的性能。Spark想要有大的性能提升，向量化是必不可少的手段。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT8fCxgG5FDL5ajxpNUFwpSibQNiawaf8PzDCTF0m323iaBUaZJpTUuk2aQ/640?wx_fmt=png&from=appmsg)

**3. 业界的Spark向量化方案**

业界的OLAP引擎里，向量化计算在已经是比较核心和成熟的优化能力。比如开源的Doris，Clickhouse或者企业自研的Redshift等，都有比较成熟的向量化方案。

Databricks在2022年正式发布了向量化引擎**Photon**，还发表了相关的论文Photon-A Fast Query Engine for Lakehouse Systems[1]，从测试效果看Photon性能非常好，但并没有开源，这也提供了对Spark加速的新思路。同年Kyligence和Intel合作开源了项**Gluten**，Gluten依赖Native Engine作为Backend，将算子下推到Velox或ClickHouse上加速执行。经过两年的社区迭代，当前Gluten已经支持了Spark的大部分算子和UDF。快手内部也一直在尝试Spark算子向量化，并且开源了Spark向量化处理插件**Blaze**，Blaze作为中间层，基于Rust语言的DataFusion来做向量化算子执行。除此之外苹果也开源了**datafusion-comet**，同样也是基于DataFusion和Arrow来做Spark算子向量化。

总之，在提升Spark性能方案上，很多公司都在尝试Spark向量化技术来进一步加速Spark的算子性能。

[1] 论文地址：*https://people.eecs.berkeley.edu/~matei/papers/2022/sigmod\_photon.pdf*

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT8fCxgG5FDL5ajxpNUFwpSibQNiawaf8PzDCTF0m323iaBUaZJpTUuk2aQ/640?wx_fmt=png&from=appmsg)

**4. ADB Spark的向量化方案**

为了提供高性价比的Spark能力，2022年底ADB Spark也开始调研向量化方案。分别从算子兼容性、社区活跃度和落地使用场景数等综合考虑各个方案。而在最初的性能摸底中，Gluten + Velox的方案就获得了1.76倍的性能提升。之后 ADB Spark 团队也和 Intel Gluten 团队展开了深度的讨论和合作，最终ADB Spark选择**Gluten + Velox**作为向量化方案。

**4.1 Gluten + Velox流程**

Spark的Gluten + Velox方案中，Gluten会沿用Spark原有的框架，以Plugin的方式集成到Spark中。当一个SQL进来，Driver会通过Spark的Catalyst模块把SQL转成 Spark的物理计划，然后物理计划会传递给Gluten。然后Gluten中的规则会将执行计划的算子转换为Native Engine的执行算子。如果在执行计划中遇到了不支持的算子，Gluten会将算子会退为Spark的Java算子执行，并且嵌入行列转换的算子来做兼容。

执行计划生成后，Driver会将执行计划下发到Executor上，Executor再将执行计划转换成实际的Velox执行的算子，通过调用JNI使用Velox库执行。

整体来看，Gluten仍然沿用Spark本身的SQL解析、优化逻辑，替换的只是最终实际执行的算子，将支持的算子使用Velox执行。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwTUmTibvdicyJxtduW21DKlW5s4V88hnJwnibtVAicLl6gJibKhsxyicBsnw8w/640?wx_fmt=png&from=appmsg)

**4.2 ADB Spark Native Engine特性**

ADB Spark在集成Gluten + Velox的Native Engine能力同时，还做了多方面的建设。包括安全性、易用性和性能优化等。

**4.2.1 全密态计算**

为满足客户对于安全方面的诉求，ADB Spark团队联合达摩院团队面向隐私计算领域携手打造的全密态密云原生大数据计算引擎，让可信安全的一站式数据交换迈上了平台化的新阶梯，满足对安全有诉求的场景，全自研的TEE引擎也通过了信通院最高级别的安全认证。客户通过简单配置即可开启全密态计算，使用成本极低。

ADB Spark Native Engine也适配了全密态计算，提供安全、快速、易用的分析能力。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwTzTiceGmsQVHXw6zYNNgydqfDiaW7iakSicYMlicLBKWOkCLKyI8B2l2rmSA/640?wx_fmt=png&from=appmsg)

**4.2.2 易用性增强**

开源Spark使用Gluten需要使用繁琐的配置，需要较高的使用和理解成本。而ADB Spark仅需一条配置就可以开启Native Engine，而且会为用户提供较优的默认配置，提高易用性。

而且访问OSS（对象存储）的数据源是Spark进行数据分析的常用场景。开源提供的hadoop-oss访问OSS需要配置明文ak，而使用明文ak可能会有信息安全风险。ADB Spark基于阿里云RAM系统自研了RAM&STS方案，Spark Driver/Executor会周期性的请求元数据服务中心刷新STS Token，从而实现免AK访问OSS数据源。这个特性不仅在非Native Engine场景支持，同时也在Native Engine的Velox访问OSS中也做了支持。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwTDkRTzEQ0rcpk95k4ojGxmbS1qMYufq4XtD5s5PSbO7bCvtJasEzO3A/640?wx_fmt=png&from=appmsg)

**4.2.3 UDF支持**

我们在推广用户使用ADB Spark Native Engine的过程中，部分客户的query中使用了较多的Spark UDF，如from\_json，from\_csv等。这类UDF当前在Gluten社区中尚未支持，客户测试场景下会因为UDF不支持导致算子回退到Java引擎，中间引起了较多的行列转换开销导致性能较差。

ADB Spark针对这些场景做了重点优化，当前from\_json等UDF已经在内部发布上线，客户测试SQL中也未出现算子回退导致额外的行列转换开销。

**4.2.4 集成智能缓存**

ADB团队自研的湖上**智能缓存Lakecache**，能够提供高效且稳定可靠的IO加速能力。本我们将向量化引擎集成智能缓存，实现性能的进一步提升。

Velox集成Lakecache加速的基本流程如下：Velox中读OSS的算子会被代理给Lakecache CPP Client。Client首先会从Lakecache Master中获得需要数据的Lakecache Worker，然后会给Worker发读请求。Worker在收到读请求后会从OSS上拉取数据并缓存，然后返回给请求的Executor。如果是读请求，或者多次向Lakecache请求数据失败，Client还会触发熔断机制，直连OSS。防止因为偶发的Lakecache服务不可用导致用户作业失败。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT1jLfSn58b7XkGjQibOa66OS8TfCN47KU3HyaicR7vJibgDuLjUvM3ImHw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT8fCxgG5FDL5ajxpNUFwpSibQNiawaf8PzDCTF0m323iaBUaZJpTUuk2aQ/640?wx_fmt=png&from=appmsg)

**5. ADB Spark性能**

**5.1 测试信息**

**5.1.1 测试对比项**

|  |
| --- |
| **测试对比项** |
| 开源 Spark 3.2.0 |
| ADB Spark 3.2.0 |

**5.1.2 数据集**

TPC-H 1T 全query

**5.1.3 ADB spark集群规格**

Driver：2core8g

Executor：40 \* 2core8g

**5.2 测试结果**

TPC-H测试下，query的总耗时如下：

|  | 开源Spark | ADB Spark |
| --- | --- | --- |
| 总耗时  (秒) | 4351.506 | 623.273 |

各query的耗时对比如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwTEnIvvxOBaGmSaAicB6N5qT7B1tCsKxjkX31v9rOeL3a5THZaq4wk1Jw/640?wx_fmt=png&from=appmsg)

从TPC-H 1T测试的整体结果来看，**ADB Spark的性能是开源Spark的6.98倍**。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/Hk1ceA7cQUDQyJDiaqU1LMacFVrxCVpwT8fCxgG5FDL5ajxpNUFwpSibQNiawaf8PzDCTF0m323iaBUaZJpTUuk2aQ/640?wx_fmt=png&from=appmsg)

**6. 总结和未来规划**

ADB Spark通过向量化技术，以及将向量化技术和智能缓存技术融合，较开源Spark性能提高了6.98倍。我们对未来的规划有以下几点：

**6.1 全网开放向量化能力**

当前我们的向量化能力在客户邀测阶段，未来会开放该功能，让更多客户进行体验。

**6.2 支持更多的场景**

支持更多的客户场景，包括但不限于：

* Gluten/Velox持续跟进社区。当前Gluten/Velox社区更新迭代很快，我们会保持月度测试和跟进社区Gluten/Velox的能力。
* 支持更多的数据源，如jindo fs，aws s3等。
* 更多客户通用的自定义场景的适配，如支持客户常用的UDF。

**6.3 软硬件结合**

如ADB Spark向量化引擎与阿里云倚天结合，进一步提升性能。

点击了解 **云原生数据仓库AnalyticDB**

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/Hk1ceA7cQUAnFZuia8Cteyq8mFiceNkmBZiaG9LOvsUkSwQqc0f42G0pmrHYvqc9l1Hwcc8Qlqz3UsNzpYZcmscng/640?wx_fmt=gif&from=appmsg&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp)

喜欢就请 点赞/分享/在看 哦