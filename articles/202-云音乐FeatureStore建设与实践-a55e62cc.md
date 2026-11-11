---
title: '云音乐FeatureStore建设与实践'
company: 网易
tag: 推荐&特征工程
date: 2022-06-29
url: http://mp.weixin.qq.com/s?__biz=MzI1NTg3NzcwNQ==&mid=2247486528&idx=1&sn=af5d722949e17ef6388582cb79d8db39&chksm=ea2e7b66dd59f27040aeffc48f0dea150e5bc52a4e3d1b3cba7f1c9cf4ad4588d7e0c5e1a0de&mpshare=1&scene=1&srcid=0117qiTM67fWa7TSJSplzmZm&sharer_sharetime=1673959054283&sharer_shareid=c032e8bde4d276951619cca1ff0debb1#rd
account: 网易云音乐技术团队
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxEUnghb9ZL3NIZ9VJerDVpr4sl7T8LI9vWTOic3G5C7AHltejGIkNcBQ/640?wx_fmt=jpeg)
> 图片来源：https://unsplash.com/photos/ZiQkhI7417A

## 概述

> 在机器学习全流程的生命周期中，Feature Store是连接Data和Model之间的桥梁。他通过存储和管理ML过程中的数据集和数据管道，减少特征工程的重复工作，以实现高效率的特征数据开发，缩短模型迭代周期。

### 从ML-Ops到Feature-Ops

标准的机器学习系统由**“数据”、、“模型”、“代码”**三个部分组织而成，其分别对应着**“特征工程”**、**“模型训练”**、**“模型部署”**三个阶段。他们彼此关联和依赖，并在各自的阶段承担着重要的职责和功能，以完成整个机器学习过程的使命。

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxX8euwO7BAGiaz1mOSRt1rvrgfsVJiajFwIIXfFq0oySXsCdFULBYNeew/640?wx_fmt=jpeg)

data model code

随着AI应用的快速发展，并在人脸识别、广告、搜索、个性化推荐等领域有了大规模应用后，人们开始重视AI系统能力的基础建设。各大云平台厂商陆续推出了一些通用的AI平台来加速**“模型训练”**和**“模型部署”**流程，例如：AWS SageMaker、Google Vertex AI、阿里PAI等，这块流程和系统，我们可以统一称之为ML-Ops[^1]。

> the extension of the DevOps methodology to include Machine Learning and Data Science assets as first class citizens within the DevOps ecology.

随着AI平台的普及和应用，**“模型训练”**和**“模型部署”**效率得到了极大的提升，而**“特征工程”**作为整个机器学习流程的最初步骤，还停留在应用传统的数据开发流程阶段。为了满足机器学习对数据开发的各种定制化要求，AI领域逐步开始探索针对机器学习场景的数据开发解决方案，于是承接ML-Ops的Feature-Ops诞生了，业内随之也推出了一系列面向特征工程的系统，并称之为Feature Store，例如：Feast、Tecton、AWS SageMaker Feature Store、Databricks Feature Store。

### Feature Store定义

最早提出并明确Feature Store的概念，来自2017年Uber的Michelangelo Platform[^2]。他描述了Feature Store的主要目的是为了在机器学习过程中，促进特征的注册、发现以及复用，并且保证特征数据在离线批处理和在线应用程序读取时的一致性。其能够提供高性能、低延迟的数据服务（面向在线的预估场景）和高吞吐、大容量的数据服务（面向离线的训练和批预测场景）以供模型使用。

一个简单而标准的Feature Store如下所示：

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxxFGv266vAORHDD0WQBfBD61ribDRWeHumhf7lTYpjXcTdo3XIvMZlBQ/640?wx_fmt=jpeg)

Feature Store

## Music FeatureBox

### FeatureBox解决的问题

在云音乐，我们通过识别云音乐算法场景特有的业务问题，打造了云音乐自研的Feature Store - Music FeatureBox。致力于解决以下问题：

* **特征发现/治理/复用**：没有中心化的管理，不同的算法团队通常无法复用特征数据，特征工程会占用算法工程师大量的时间，且还会造成计算资源和存储资源的浪费。我们通过实现特征元数据的注册与中心化管理，来帮助特征发现/治理，以促进特征复用，加速机器学习过程中的特征工程效率。
* **高性能的特征存储和服务**：特征数据存储引擎在不同的场景有着完全不同的应用需求（训练/批预估需要扩展性好、存储空间大；实时预估需要低延迟、高响应），我们通过自研不同内核的存储引擎（MDB/RDB/FDB/TDB），并封装逻辑存储层来路由不同的物理存储引擎，在不同的场景使用不同的物理存储引擎来满足个性化的应用要求。
* **模型训练/预估使用的特征数据一致性**：用于训练和预估的特征数据往往因为不同的数据实现，而产生异构或者不一致，这会导致模型的预估产生偏差。我们在Datahub系统抽象出一层单一的数据访问层，将模型和物理存储隔离并解耦。通过统一数据访问API和自动化数据同步任务，来保证训练/预估使用的特征数据一致性。
* **特征抽取&算子复用**：因为计算的环境和数据上下文有所不同，通常模型的离线训练和在线预估会各自实现一套特征的抽取逻辑，这样的做法不仅会带来额外的开发工作量，还会造成因为跨语言、跨环境等因素所引起的计算精度不一致、质量风险和维护成本增加等问题。我们设计了一套跨语言、跨平台的算子库&特征抽取计算引擎，以达到一套算子代码库+统一的DSL语法配置能够在线上/线下各个计算环境中生效。
* **训练样本生产/管理**：从特征数据到最终喂给模型训练的样本数据集，往往会经过特征筛选、特征抽取、样本采样、样本拼接等过程，FeatureBox通过标准的API规范了该过程的输入和输出，并支持自定义数据管道且托管了整个过程的数据管道任务，以实现特征数据和模型训练的无缝对接。
* **特征质量监控和分析**：机器学习系统产生的误差很大一部分是来自于数据的问题，FeatureBox可以通过统计存储和服务中的一些指标，来帮助算法工程师发现和监控这些数据的质量问题。其中包括但不限于特征质量、特征重要性、服务的性能等。

综上所述，FeatureBox是一套针对机器学习场景定制的数据系统，用来解决Feature-Ops中所描述的问题，主要包括以下三个方面：

* **存储数据和管理元数据。**
* **创建和管理特征抽取管道。**
* **为模型训练/预估提供一致性的数据服务。**

### FeatureBox整体架构

> FeatureBox并不是单一的服务或者代码库，而是一套完整的面向机器学习流程的数据系统。

FeatureBox是基于云音乐自研的数据服务管理系统 - **"Datahub"** 构建起来的，整体的架构图如下：

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxnbr3meFcjLiaPl5uXSN25ib0SgZjbyoRoULNwHgokfJXqIRDjV0oHleA/640?wx_fmt=jpeg)

FeatureBox System

这里面模块分别有什么作用？他们之间的关系是怎么样的？下面我们来对其中几个核心模块进行详细的介绍：

### Datahub

"Datahub"是FeatureBox中最核心的模块，可以说是整个FeatureBox的基石。他构造了一套抽象的特征元数据，并且封装各种不同物理存储的API，将所有对物理数据的读写都抽象成对特征的操作。我们可以通过Datahub获取特征的Schema和Storage元数据，并且可以在任意语言和环境中使用Datahub API访问到你需要的特征数据。通过Datahub，FeatureBox能够让算法工程师对特征数据的操作在离线/实时/在线等各种环境下，保持一致的体验。

同时作为访问Storage的Proxy，Datahub也包含了序列化、压缩、埋点监控等切面化功能，以帮助用户屏蔽一些技术优化项，实现更高的读写效率。此外，Datahub还能作为数据和物理存储交互的拦截处理管道，添加各种自定义的处理过程（语法过滤、安全处理、缓存优化等）。

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxdchROzXibWy6EKBBcibic6BAJz1bkYwxiaHiatYicFPhlIAQG7RzQGvYohGQ/640?wx_fmt=jpeg)

datahub

**Schema&序列化**

要想所有的存储数据都有元数据，首先要做的第一步就是设计一套标准的table schema，能够表达目前所有业务数据的格式。而对于schema实现来说，最重要的就是value的序列化方案选型，我们需要考虑以下几点目标：

* schema要容易理解，能够方便的扩展字段
* 支持跨语言的序列化方式
* 拥有高效的编解码性能和高压缩比

根据以上几点，我们很容易想到两个备选方案，一是json，二是protobuff，这两个选型各有利弊，我们来分析一下。

***json*：**

优点 - 很容易理解，扩展性也非常好，能够兼容各种语言。

缺点 - 是string明文存储，压缩比和编解码性能都不高。

***protobuff*：**

优点 - 作为google老牌序列化方式，拥有非常好的编解码性能和压缩比，也有很好的跨语言支持能力。

缺点 - 需要生成.proto来维护schema，不利于字段动态扩展。（一个table增加字段，可能涉及线上应用、flink应用、etl应用、spark训练脚本等多个地方变更schema）。

**那么有没有办法，即能拥有pb的高效性能，又能拥有json的扩展能力呢？答案是肯定的！**

我们调研通过PB库中的`com.google.protobuf.DynamicMessage`和`com.google.protobuf.Descriptors.Descriptor`类来实现基于protobuff的元数据管理和转换，并通过开源库protostuff来实现.proto文件的动态编译，从而将protobuff格式做到像json一样可以直接通过Map<String,Object>来操作的便利性，并且不用多端同时更新发布.proto文件。

确定了value的序列化方式之后，构建table schema就容易多了。由于Datahub对于特征服务只提供KV/KKV的数据接口，那么我们定义的table schema只要在增加最为pk和sk的列就可以了，剩下的列就是value的pb schema。这样我们就能即保证存储引擎对于高效读写的要求，又保证了业务系统对于简单易用的要求。

例子：`music_alg:fm_dsin_user_static_ftr_dpb`

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxVEAwEQxk8TPxq8LRQ2gZCCPRnQwEticnCKEE94rZp1yMD4KxibeOuv3w/640?wx_fmt=jpeg)

schema

自动生成protobuff

```
syntax = "proto3";  
package alg.datahub.dto.proto;  
message UserStaticFeature {  
  repeated float userTag = 1;  
  repeated float userLan = 2;  
  repeated float userRedTag = 3;  
  repeated float userRedLan = 4;  
  SparseVector userMultiStyleSparseVector = 5;  
  repeated float userRedSongTimespan = 6;  
  repeated int32 userBaseFeatureStr = 7;  
  float userAgeType = 8;  
  float userRank = 9;  
  repeated float userSong2VectorEmbedding = 10;  
  repeated float userChineseTag = 11;  
  repeated float userTagPlayEndRate = 12;  
  repeated float userLanPlayEndRate = 13;  
  repeated float userPubTimePlayEndRateAll = 14;  
  SparseVector artistPlayEndRatioSparseVector = 15;  
  repeated float dsUserTag = 16;  
  repeated float dsUserLan = 17;  
  repeated float dsUserRedTag = 18;  
  repeated float dsUserRedLan = 19;  
  repeated float fatiRatio = 20;  
}  
message SparseVector {  
  int32 size = 1;  
  repeated int32 indices = 2;  
  repeated double values = 3;  
}
```

### Transform

"Transform"是FeatureBox除Datahub外的另一核心模块，他主要管理从特征读取到模型输入的整个过程，是机器学习系统中特征工程-模型工程衔接的纽带。Transform是由FeatureBox中注册的Feature元数据、算子元数据等编排配置而成，他能够跨语言、跨引擎的表达特征抽取的执行过程。

> 与业内的Transform定义不同，这里的Transform只是一个自定义DSL的配置描述，他表示的是整个特征抽取的的计算过程，并不包括具体的任务和任务管道（相关部分在Job Generator和Web Console的任务管理功能中）。

Transform根据实际的应用场景不同，可以分为三种情况：

| 场景 | 描述 | 特征获取 | 算子语言（兼容） | 输出类型 |
| --- | --- | --- | --- | --- |
| 离线训练 | 用于离线环境模型训练的批量Transform | 从Hive/Hdfs获取一个DataSet | java/scala/c++ | TFRecord文件 |
| 在线预测 | 用于在线环境模型预测的指定特征集合的Transform | 从Redis/Tair通过Key查询特征集合 | java/scala/c++ | Vector对象 |
| 实时特征（规划） | 用于实时特征生产的流式数据Transform | 从Kafka/Nydus获取Streaming数据 | java/scala/c++ | 动态ProtoBuf对象 |

我们可以通过同样的Transform语法（MFDL）来表达不同环境和计算引擎的特征计算执行过程，以产出最终需要特征值：

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxTVibysbTh7kbO9aGZC2W9kAAhichSR3A1LakuZczOuGWPu1D6LVwNibxg/640?wx_fmt=jpeg)

Transform

关于我们Transform模块中的MFDL是如何实现和应用的，可以阅读上篇文章云音乐预估系统建设与实践[1]的内容，其详细描述了MFDL在线上预估系统中的使用。

### Monitor

当机器学习系统出现问题时，大部分的原因来自于数据问题。因为FeatureBox包含了所有的特征存储、特征元数据、特征服务信息等功能，所以他能成为一个非常好的特征监控中心服务，来帮助整个机器学习流程定位和发现各种特征数据问题。一般的情况下，我们主要会统计和监控以下三类指标：

* 特征基础指标：“特征基础指标”是指基于存储引擎的特征数据的一些metrics统计，如特征覆盖度、存储容量、新鲜度、分布等。这些基础指标可用帮助我们快速了解一个特征的基本信息，以方便具体的算法工程师/数据开发工程师来使用或运维该特征数据。
* 特征服务指标：“特征服务指标”是指DataService/Storage等在线系统的实时运行信息，如存储指标（可用性/容量/利用率等）、服务指标（QPS/RT/错误率等）等相关指标。这些指标可以帮助你实时观察和分析当前整个FeatureBox的在线系统是否稳定可用，以确保上游业务和APP提供的服务稳定可用。
* 特征/模型偏移指标：“特征/模型偏移指标”是指通过特征重要性、模型训练/预测数据偏差等指标来表达特征数据质量。因为随着时间的推移或者一些突发的外部事件，可能会造成线上部署的模型的训练数据和实际的预测数据之间产生比较大的偏差，从而造成模型效果下降，所以我们需要统计“特征/模型偏移指标”来帮助维持生产环境中机器学习模型的效果。

关于特征基础指标和偏移检测，FeatureBox的Monitor模块主要集成TFX中的Data Validation[2]组件来实现对数据集的分析和监控。我们主要提供以下三种分析和监控功能：

* 针对静态数据集统计的可视化分析。
* 根据先验期望Schema校验数据集统计分析。
* 采用双样本对比检测数据偏差和漂移。

下图详细描述Monitor模块在整个机器学习流程中的位置和作用。

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxgMgTelJTgLuCXianmO0JqcZjrjz0HdgFNbMQnLvLWFUmpUb2Xic5BQAA/640?wx_fmt=jpeg)

Data Validation In ML

**示例：**针对数据集的基础统计信息和分布提供可视化的视图，以方便算法同学排查数据异常问题。（原生的TFDV通过jupyter notebook执行脚本以生成可视化信息，我们也可以通过采集每次统计的stats数据以展示到FeatureBox界面中）

统计视图会将特征分为连续值和离散值两类，两者都会有分布统计（连续值采用标准直方分布），另外连续值会有中位数、方差、标准差等统计。

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxqCb02mBqwzfoUCzhs5cHvo7Oicd13ib7NkecYToHPiaia1CqggswGPcDUA/640?wx_fmt=jpeg)

TFDV\_1

### Storage

"*Storage*"是FeatureBox中的物理存储层，负责存储真实的特征数据，并对上游的数据服务层提供数据的读写服务。根据不同的特征应用场景，Storage模块可以分为离线存储和在线存储。

**离线存储**：离线存储通常应用在训练或批预测场景，存储近月/近年来TB级别的特征数据，提供小时级/天级的批量读写能力。常见的离线存储有HIVE/HDFS等。

**在线存储**：在线存储通用应用在实时预测场景，只存储特征数据的最新值，并有着高响应、低延迟的要求。常见的在线存储有Redis/Tair/MySQL等。在云音乐，我们为了满足不同类型的特征存储要求和不同场景的响应要求，还基于Tair架构定制了存储引擎内核，他们分别是：

* MDB：基于内存Hash表的内存型存储引擎，有着高响应、低延迟，存储资源代价高的特点，通常用于存储对响应要求非常高的小容量特征数据的在线预测场景。
* RDB：基于RocksDB的磁盘型存储引擎，响应和延迟略不如MDB、但存储资源代价更低，能够支持数据批量更新Bulkload，通常用于存储大容量特征数据的在线预测场景。详细内容可以阅读之前的文章：自研磁盘型特征存储引擎RDB在云音乐的实践[3]。
* FDB：基于FIFO Compaction策略的RocksDB存储引擎，因为FIFO Compaction所以很适合存储日志型数据而不会带来写放大，通常用于存储Snapshot特征快照数据。
* TDB：自研的时序存储引擎，能够根据不同时间粒度聚合计算数据，但响应和延迟要低于MDB/RDB，通常用于存储带时间字段聚合的统计型特征数据。

FeatureBox通过Datahub/DataService作为路由代理，将上层业务对特征数据的读写路由并转化到实际对应的Storage连接进行操作。所以用户对底层的Storage的API和运维其实是不感知的，他们只是通过Web Console来定义Schema与选择他们特征数据更适用的Storage。这也促成了FeatureBox可以让特征存储的管理、运维、数据迁移、快速失败、扩缩容等工作变得更加方便。

![](https://mmbiz.qpic.cn/mmbiz_jpg/KV8By3euEQiasF36xMwTOFXM36ssZGtwxaO0UFBomsicq7qGdybqBakyeIaX8YlpjWSZCNZHDLVFcWvTwvdLib0hQ/640?wx_fmt=jpeg)

FeatureBox Storage

## 结语

以上就是本篇文章的全部内容，我们简单的介绍了FeatureOps和FeatureStore的定义和他所解决的问题，并以此展开讲述了云音乐自建Feature Store - FeatureBox的主要设计和模块功能，希望能给对特征工程感兴趣的小伙伴带来启发和帮助。因为篇幅问题，在整个Featur Store中还有非常多的细节没有展开，大家可以关注后续的文章。

[^1]: MLOps SIG[4][^2]: Michelangelo Platform[5]

### 参考资料

[1]

云音乐预估系统建设与实践: *https://zhuanlan.zhihu.com/p/529175986*

[2]

Data Validation: *https://github.com/tensorflow/data-validation*

[3]

自研磁盘型特征存储引擎RDB在云音乐的实践: *https://zhuanlan.zhihu.com/p/481746458*

[4]

[MLOps SIG: *https://github.com/cdfoundation/sig-mlops/blob/master/roadmap/2020/MLOpsRoadmap2020.md*

[5]

[Michelangelo Platform: *https://eng.uber.com/michelangelo-machine-learning-platform*