---
title: '云音乐预估系统建设与实践'
company: 网易
tag: 精排&CXR预估
date: 2022-06-15
url: http://mp.weixin.qq.com/s?__biz=MzI1NTg3NzcwNQ==&mid=2247486449&idx=1&sn=489c7b0383800ddcc36a9a72af81f3c3&chksm=ea2e7cd7dd59f5c15d2ed2adcd1db35f89d92c8390ed956f0b298a658def93410a4c6668f715&mpshare=1&scene=1&srcid=0117rJEidptu50XAatgGRbHk&sharer_sharetime=1673958981682&sharer_shareid=c032e8bde4d276951619cca1ff0debb1#rd
account: 网易云音乐技术团队
origin: readme
---
> 作者：大人物

## 1. 什么是预估系统？

    预估系统的核心任务是完成模型计算，可以认为模型就是一个函数（**举例：f(x1, x2)= ax1 + bx2 +c**）。其中参数a、b、c是通过模型训练得出的权重值，自变量x1与x2就是特征，模型计算就是使用自变量x1与x2求解的过程。  
    因此预估框架需要做的是：构造函数输入（特征），计算函数得到结果（模型计算）。即：**特征抽取、模型计算**。

![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMO2aDPtkdibOZCyK89XXHH97FhgaPibhwgGG4pNQQTG9KQ3ic5OZMjRztGw/640?wx_fmt=png)

* **特征抽取**  
  特征是对某个行为相关信息的抽象表达。推荐过程中某个行为信息必须转换成某种数学形式才能被机器学习模型所学习。为了完成这种转换，就必须将行为过程中的信息以特征的形式抽取出来。
* **模型计算**  
  集成机器学习库，加载机器学习平台训练出的模型，按照模型结构执行既定的矩阵、向量等计算。

## 2. 预估系统的设计思考

### 2.1 通用方案的局限

    业内常见的方案是特征处理服务 + tfserving模型计算服务，这种方案是将特征处理和模型计算分服务部署。在特征数量不大时可以提供较好的支持，但特征数量一旦变多，就会出现明显的性能问题，主要是因为特征要跨网络（跨进程）传递给底层机器学习库，这样就会带来多次编解码与内存拷贝，会造成巨大的性能开销。

### 2.2、新系统的思考

根据业务需求，并吸取通用方案存在的优缺点，我们构建了新的高性能预估系统，该系统指导思路是：

* **高性能**：追求特征抽取与模型计算高性能，提供大规模特征抽取和大规模模型计算的能力。
* **抽象与复用**：系统分层设计，分层复用；线上线下特征抽取逻辑复用；特征抽取提出算子概念，建立算子库，实现特征复用。
* **实时化**：实现样本采集实时化、模型训练实时化和模型更新实时化。
* **可扩展性**：特征抽取提供自定义算子接口，方便自定义算子的实现；模型计算提供集成多种机器学习库的能力。

下图展示了云音乐预估系统架构：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOyibnpETp58IC0b94QQdTR2icJp71l412R2Eq4hxCFhDLVS1Oa8nXxGQg/640?wx_fmt=png)

## 3. 预估系统的建设过程

一个优秀的预估系统需要解决如下三个问题：

* 如何解决特征和模型的高效迭代？
* 如何解决预估计算的性能问题？
* 有没有机会通过工程手段提升算法效果？

### 3.1 特征与模型的高效迭代

#### 3.1.1 系统分层设计

系统分层设计，仅暴露上层接口层，不同业务间完全复用中间层和底层实现，较大程度减少代码开发。

* **底层框架层**：该层提供异步机制、任务队列、session管理、多线程并发调度、通络通信相关的逻辑、外部文件加载与卸载等
* **中间逻辑层**：封装查询管理、缓存管理、模型更新管理、模型计算管理等功能
* **上层接口层**：按照执行流程提供HighLevel接口，算法在此层实现逻辑

下图展示了框架分层设计：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOKEGqgnt6cwt1OdVxohd4Lra2uAwpr8xVcAcruN6cuLlBGHyXJU0LHA/640?wx_fmt=png)

#### 3.1.2 配置化完成模型计算全流程

按照执行流程，把处理过程分成三个阶段，分别是：数据查询、特征抽取、模型计算。在框架中对每个阶段进行抽取和封装，并提供配置化描述语言来完成各个阶段的逻辑表达。

##### (1) 数据查询

通过XML配置表名、查询key、缓存时间、查询依赖等就能实现特征数据的外部查询、解析、缓存全流程。如下所示：

```
<feature_tables>  
    <table name="music-rec-fm_set_action" alias="trash_song" tag="user" key="user_id"/>  
    <table name="music_fm_dsin_user_static_ftr_dpb" alias="u_static" tag="user" key="user_id"/>  
    <table name="alg_song_ua_rt" alias="u_rt_red" tag="user" key="user_id" subkey="1"/>  
    <table name="fm_dsin_song_promoted_info_feature_dpb_mdb" alias="item_promoted" tag="item" key="item_id" cache_time="7200" cache_size="800000" query_type="sync"/>  
    <table name="fm_dsin_song_static_feature_dpb_mdb" alias="item_static" tag="item" key="item_id" cache_time="7200" cache_size="800000" query_type="asyc"/>  
</feature_tables>
```

特征数据查询配置化带来了开发效率的大幅提升，用几行配置就实现了以往需要大量编码才能实现的特征查询功能。

##### (2) 特征抽取

开发特征抽取库，封装特征抽取算子，开发特征计算DSL语言，通过配置化完成整个特征抽取过程。如下所示：

```
<feature_extract_config cache="true" log_level="3" log_echo="false" version="2">  
    <fea name="isfollowedaid" dataType="int64" default="0L" extractor="StringHit($item_id, $uLikeA.followed_anchors)"/>  
    <fea name="rt_all_all_pv" dataType="int64" default="LongArray(0, 5)" extractor="RtFeature($all_all_pv.f, 2)"/>  
    <fea name="anchor_all_impress_pv" dataType="int64" default="0" extractor="ReadIntVec($rt_all_all_pv, 0)"/>  
    <fea name="anchor_all_click_pv" dataType="int64" default="0" extractor="ReadIntVec($rt_all_all_pv, 1)"/>  
    <fea name="anchor_all_impress_pv_id" dataType="int64" default="0" extractor="Bucket($anchor_all_impress_pv, $bucket.all_impress_pv)"/>  
    <fea name="anchor_all_ctr_pv" dataType="float" default="0.0" extractor="Smooth($anchor_all_click_pv, $anchor_all_impress_pv, 1.0, 1000.0, 100.0)"/>  
    <fea name="user_hour" dataType="int64" extractor="Hour()" default="0L"/>  
    <fea name="anchor_start_tags" dataType="int64" extractor="Long2ID($live_anchor_index.start_tags,0L,$vocab.start_tags)" default="0L"/>  
</feature_extract_config>
```

特征抽取库的会在下面详细介绍。

##### (3) 模型计算

对模型加载、参数输入、模型计算等进行封装，通过配置化实现模型加载与计算全流程。具体特点如下：

* 预估框架集成tensorflow core，支持多种模型形态。
* 支持多模型加载，支持多模型融合打分。
* 支持多buf模型更新，自动实现模型预热加载。
* 支持多种格式的参数输入（Example和Tensor），内置Example构造器和Tensor构造器，对外屏蔽复杂的参数构造细节，简单易用。
* 扩展多种机器库，例如paddle、gbm等。

```
<model_list>  
    <!-- pb模型，tensor输入，指定out_names -->  
    <id model_name="model1" model_type="pb" input_type="tensor" out_names="name1;name2" separator=";" />  
  
    <!-- savedmodel模型，tensor输入，指定out_names -->  
    <id model_name="model2" model_type="mdl" input_type="tensor" out_names="name1;name2" separator=";" />  
      
    <!-- savedmodel模型，example输入，指定out_aliases -->  
    <id model_name="model3" model_type="mdl" input_type="example" out_aliases="aliase1;aliase2" separator=";" signature="serving_default" /></model_list>
```

通过上述配置，可以完成模型加载，模型输入构造，模型计算全流程。用几行配置实现了之前需要大量编码才能实现的模型计算功能。

#### 3.1.3 封装特征抽取框架

特征抽取目的是将非标准的数据转换成标准的数据，然后提给机器学习训练平台和在线计算平台使用。特征抽取分为离线过程和在线过程。

下图展示了什么是特征抽取：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOIfcoAnyqDqo6iacHLL3UrHM4RG31boxNiapjIwSoe7Z4ATNNtQveickOg/640?wx_fmt=png)

##### 3.1.3.1 特征抽取存在哪些问题？

* **一致性难以保证**

线上抽取与线下抽取因平台不同（语言不同）需要开发多套代码，从而会引发逻辑不一致的问题。一致性问题一方面会影响算法效果，另一方面一致性校验会带来高昂工程落地成本。

* **开发效率低**

特征生产和特征应用要对应多套系统，新增一个特征要改多处代码，开发效率低下。

* **复用难**

框架缺乏对复用能力的支撑，特征计算逻辑差异大，导致团队间数据复用难，资源浪费、特征价值无法充分发挥。

##### 3.1.3.2 如何解决上述问题？

###### (1) 抽象算子

提出算子概念，将特征计算逻辑封装成算子。为了实现算子抽象，首先必须定义统一的数据协议（标准化算子的输入与输出），这里我们采用动态PB技术，根据特征的元数据信息，采用统一的方式处理任意格式的特征。  
并且建立平台通用算子库和业务算子库，实现了特征数据和特征计算的复用能力。

###### (2) 定义特征计算DSL语言

基于算子，我们设计了特征计算表示语言DSL，通过该语言可以支持多阶抽取和抽取依赖， 通过基础算子的多种组合可以实现复杂的特征计算逻辑，提供丰富的表达能力。DSL表达式如下：

![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMO8VwB7Z3zsZbQR2tT0h4dHrYyxAtRxqWMtqoibS5L6j3SHNmvaNx91EQ/640?wx_fmt=png)  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOWB1c5u4MPLjrxsNFF8Djn80qSaiaticia7XhPkWkjYtgvuDpfRlrkdQtw/640?wx_fmt=png)

###### (3) 解决逻辑不一致问题

    出现特征计算逻辑不一致根本原因是因为特征计算分为离线过程和在线过程，离线特征计算一般是在Spark平台和Flink平台（使用scala或java语言），而在线特征计算一般c++环境。平台和语言的不一样，就导致相同的特征计算逻辑要开发多套代码，多套代码间就可能出现逻辑不一致的问题。  
    为了解决上述问题，就必须实现特征处理逻辑多平台兼容。考虑到在线程计算平台使用的是c++语言，以及c++的高性能和多平台（多语言）运行的兼容性，于是特征处理核心库采用c++语言实现，对外提供c++接口（支持在线计算平台）、java接口（支持spark和flink平台）。并提供一键编译的方式，编译后生成so库和jar包，方便集成到各个平台中运行。

下图展示了特征抽取跨平台解决方案：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMO4iaVyGngz3L4dTnxPIz3mzvReDxb7COCk0sww6eQyhicOwrV8X6VKtpg/640?wx_fmt=png)

    通过封装特征抽取库，提供特征抽取跨平台运行能力，实现一次代码编写，多平台（多语言）运行，从而解决多平台特征抽取逻辑不一致的问题；通过算子封装、算子库建立，实现了特征与特征计算的高度复用；通过开发特征计算DSL语言，实现配置化开发特征抽取的能力。基于上述建设，极大的提升了我们在特征抽取上的开发效率。

### 3.2 高性能预估计算

    预估服务是计算密集型服务，对性能要求极高，尤其在处理复杂特征和复杂模型时，性能问题表现的尤为突出，我们在开发预估系统时有很多性能上的思考和尝试，下面将详细介绍。

#### 3.2.1 无缝集成高性能机器学习库

    前面介绍过传统预估方案是将特征处理服务和模型计算服务分进程部署，这样就会涉及到特征的跨网络传输、序列化、反序列化和频繁且大量的内存申请和释放，尤其是推荐场景特征量大，会带来较大的性能开销。下图展示了服务部署和特征传输的过程：

下图展示了传统方案服务部署和特征传输：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMO1ek1SXcZrv7nM1rzQbo9O7OOzDE5SfqLHnKDhZqic421ibWKA2zGR5Pw/640?wx_fmt=png)

    为了解决上述问题，在新的预估系统中，将高性能机器学习库TF-core无缝集成到预估系统内，即特征处理和模型计算同进程部署。这样可以实现特征指针化操作，避免序列化、反序列化、网络传输等开销，较大程度提升性能。

下图展示了新预估系统特征传输：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOjEjmPfySloWVByxtMibM0UPN9H9VkywsiaPhgv6nvicF2wnvS0pvHiaFzQ/640?wx_fmt=png)

#### 3.2.2 全异步架构

    为了提升计算能力，我们采用了全异步架构设计。计算框架异步处理、外部调用无阻塞等待，最大程度将线程资源留给实际计算。机器过载时，会自动丢弃任务队列中超时的任务，避免机器/进程被拖垮。

下图展示了异步架构设计：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMONLQLvE9PfCZvLXqibEiaicmG71GKoqBDIFxxvWjCpAwBeZc1HvadHDwfA/640?wx_fmt=png)

#### 3.2.3 多级缓存

    推荐场景的请求由一个User和一批候选Item组成（50-1000个不等），而热门Item的数量仅在十万或者百万级别，Item的特征分为离线特征（小时级或者天级更新）和实时特征（秒级或者分钟级更新）。基于推荐场景的请求特点，Item特征完全可以通过请求触发的方式缓存在进程内，在超时时间内可以直接使用缓存中的内容，避免无效的外部查询、特征解析和特征抽取。不仅能大大降低外部存储的查询量，也能大大降低预估服务的资源占用。  
    目前预估服务在特征数据查询和特征抽取计算缓环节使用了缓存机制。在缓存设计上采用了线程池异步处理、分多个桶保存缓存结果减少写锁碰撞等措施提升缓存查询性能。并且提供多种特征查询及缓存策略：

* **同步查询&LRU缓存**  
  适用特征重要且特征规模庞大的特征（性能低）

  适用于特征不太重要且规模庞大的特征（性能中）

  适用于特征规模在千万以下的特征（性能高）

+ **特征批量导入**
+ **异步查询&LRU缓存**

下图展示了预估系统缓存机制：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOACF2XBpzCoyLnMTLv7CQWSPypAn6dD4XT9dqHaibU6TZZeFQficlE42g/640?wx_fmt=png)

#### 3.2.4 合理的模型输入建议

    针对Tensorflow的模型输入，Tensor输入的性能会优于Example输入的性能。下图一展示了Example输入的timeline图，下图二展示了Tensor输入的timeline图。可以明显的发现使用Example作为模型输入时，在模型内有较长的解析过程，并且在解析完成前，后面的计算op无法并发执行。

下图展示了Example输入的Timeline：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOnzPoq3hgxVYMbiaLyghpbYReZeDuLzQSBq37iaPg1aYuY8ZJQuUneo3g/640?wx_fmt=png)

下图展示了Tensor输入的Timeline：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOq0ibMXf8b2N9ib7dmIrQqnz02ICdGVicX06Inmib2VicoH2TL1A9DHGXhrg/640?wx_fmt=png)

##### (1) 为什么使用Tensor输入可以提高性能？

主要是可以减少Example的序列化和反序列化，以及ParseExample的耗时。

##### (2) 相比Example，用Tensor输入存在哪些问题？

Tensor构造逻辑逻辑复杂，开发效率低  
需要关注Tensor维度细节，如果Tensor改变（添加、删除、维度改变等）都需要重新开发Tensor构造代码

**为了兼顾Tensor输入的高性能和Example输入的开发便捷性，在预估系统中开发了一套Tensor构造器，即保证了性能，也降低开发难度。**

#### 3.2.5 模型加载与更新优化

    在模型的加载与更新上尝试多种优化策略，其中包括：支持模型双buf热更新、支持模型自动预热加载、旧模型延时卸载等方法提升模型加载性能。通过上述优化方式可实现大模型分钟级热更新，线上请求耗时无抖动，为模型实时化提供基础。

下图展示了模型自动预热方案：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOvDBquS350FVtPEpagJyK3YfnXHyszzOOQ8NBrIZt9AmaYzwOeH3Xdg/640?wx_fmt=png)

### 3.3 通过工程手段提升算法效果

预估系统除了要保证高可用、低延时等核心要素外，能否通过一些工程手段带来算法效果的提升呢？我们从特征、样本、模型等维度做了一些思考和尝试。

#### 3.3.1 传统预估方案中存在哪些可以优化的点？

##### (1) 特征穿越的问题

    传统的样本生产方式，存在特征穿越的问题。样本拼接是将用户行为和特征进行拼接，用户行为是用户在t-1时刻对预估结果产生的行为，正确的做法是t-1时刻的用户行为与t-1时刻的特征进行拼接，但是传统做法是只能用t时刻的特征进行拼接，即导致t时刻的特征出现在t-1时刻的样本中，从而导致特征穿越的产生。出现特征穿越会导致训练样本不准，从而导致算法效果下降。

![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOJBJhPAcByNES0h0E9DuILXPXBlVGLhLZtbLbm0H3QicnmicwP3qP8jJQ/640?wx_fmt=png)

##### (2) 模型实时性不够

    传统推荐系统是天级别更新用户推荐结果，实时性差，无法满足实时性要求很高的场景。例如直播中主播开播状态、直播内容变化、业务环境调整等都需要推荐系统能实时感知。

#### 3.3.2 如何解决上述问题？

    为了解决上述问题，我们开发了模型实时化方案。该方案是基于预估服务，将预估时的状态（请求内容、当时使用的特征等）实时保存到kafka，并通过traceid与ua回流日志做关联。这样就能确保用户标签与特征能一一对应，从而解决特征穿越的问题。  
    并且该方案也实现样本流秒级落盘，为模型增量训练提供了样本基础。在训练侧实现了模型增量训练，并将训练产出的模型实时推送到线网服务。具体实现如下如图：

下图展示了模型实时化方案：  
![](https://mmbiz.qpic.cn/mmbiz_png/KV8By3euEQhm8aJXhBLQNW1LKzO50IMOaTR0ZiaM0ibRfqP3sic6RWvDayuwMF6tDsygK4Xb3GmyzAR9VJEd9JWNA/640?wx_fmt=png)

**通过模型实时化方案，实现样本实时保存，从而解决特征穿越的问题；实现模型分钟级训练和更新，能让模型及时捕捉新动态和新热点。从而提升算法效果。**

> 本文发布自网易云音乐技术团队，文章未经授权禁止任何形式的转载。我们常年招收各类技术岗位，如果你准备换工作，又恰好喜欢云音乐，那就加入我们 staff.musicrecruit@service.ne...