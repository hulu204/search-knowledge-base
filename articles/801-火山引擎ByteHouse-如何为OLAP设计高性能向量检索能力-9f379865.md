---
title: '火山引擎ByteHouse：如何为OLAP设计高性能向量检索能力？'
company: 字节跳动
tag: 工程相关
date: 2024-05-09
url: https://cloud.tencent.com/developer/article/2415974
account: 
origin: harvest-202607
---
[java进阶架构师](https://cloud.tencent.com/developer/user/2899014)

## 火山引擎ByteHouse：如何为OLAP设计高性能向量检索能力？

关注作者

[*腾讯云*](https://cloud.tencent.com/?from=20060&from_column=20060)[*开发者社区*](https://cloud.tencent.com/developer)

[文档](https://cloud.tencent.com/document/product?from=20702&from_column=20702)[建议反馈](https://cloud.tencent.com/voc/?from=20703&from_column=20703)[控制台](https://console.cloud.tencent.com/?from=20063&from_column=20063)

登录/注册

[首页](https://cloud.tencent.com/developer)

学习

活动

专区

圈层

工具

[MCP广场![](https://qccommunity.qcloudimg.com/image/new.png)](https://cloud.tencent.com/developer/mcp)

文章/答案/技术大牛搜索

搜索关闭

发布

java进阶架构师

[社区首页](https://cloud.tencent.com/developer) >[专栏](https://cloud.tencent.com/developer/column) >火山引擎ByteHouse：如何为OLAP设计高性能向量检索能力？

# 火山引擎ByteHouse：如何为OLAP设计高性能向量检索能力？

![作者头像](https://ask.qcloudimg.com/custom-avatar/2899014/gtk1a2tbre.jpg)

java进阶架构师

关注

发布于 2024-05-09 10:49:36

发布于 2024-05-09 10:49:36

6010

举报

文章被收录于专栏：[Java进阶架构师](https://cloud.tencent.com/developer/column/4827)Java进阶架构师

> 点击“阅读原文”，即可下载《ByteHouse向量检索技术指南》

## **背景**

随着LLM技术应用及落地，数据库需要提高向量分析以及AI支持能力，向量数据库及向量检索等能力“异军突起”，迎来业界持续不断关注。简单来说，向量检索技术以及向量数据库能为 LLM 提供外置的记忆单元，通过提供与问题及历史答案相关联的内容，协助 LLM 返回更准确的答案。

不仅仅是LLM，向量检索也早已在OLAP引擎中应用，用来提升非结构化数据的分析和检索能力。ByteHouse是火山引擎推出的云原生数据仓库，近期推出高性能向量检索能力，本篇将结合ByteHouse团队对向量数据库行业和技术的前沿观察，详细解读OLAP引擎如何建设高性能的向量检索能力。

## **负载特征**

向量检索的目标是查找与给定向量最相似的 k 个结果，广泛用于以图搜图、推荐系统等场景。近两年，随着大模型的普及，而基于向量检索构建的大模型检索增强功能，能够显著改善大模型的结果准确率低的问题，得到了广泛的关注。因此，向量检索相关技术，以及基于向量检索的向量数据库的概念逐渐流行起来，成为数据库领域一个热门话题。

实际使用场景中，向量检索针对的数据集大小通常会在 million 甚至 billion 级别，而查询延迟通常会要求在数毫秒到百毫秒内返回，因此，通常不会使用 brute force 的方式进行计算，而是会使用具有特殊结构的向量检索索引的方式来计算，比较流行的向量索引算法有 HNSW、Faiss IVF 等。

![](https://developer.qcloudimg.com/http-save/yehe-2899014/bc0f229f197306b0dbe81af09a57377a.png)

这类基于向量索引的向量检索负载大概具有以下几个特点：

* 构建时间长，资源消耗大：索引的构建时间通常比较长，远大于数据插入的时间，以常用的 gist1M 数据集为例不同类型的索引构建时间大概需要几十秒甚至上百秒。此外，构建索引通常需要消耗较多的 CPU 及内存资源。因此，在实现向量检索功能时，需要考虑如何高效管理索引构建任务需要的资源，保证构建速度的同时，也不会影响其他任务的进行。
* 内存计算：HNSW、Faiss IVF 类索引都需要将索引结构全部读取到内存中，而索引结构通常会包含有所有向量数据的原始数据以及一些额外的结构相关数据，因此其大小通常会大于向量数据的总量，由于结构较大每次加载索引时间会比较长，对于查询低延迟和高 QPS 的需求场景通常需要索引常驻内存。因此，向量检索功能需要考虑如何支持内存计算，并考虑内存资源的高效管理。
* 融合查询：用户通常需要查询相近向量的很多其他属性信息，通常也需要结合一些标量过滤条件进行更符合预期的结果筛选。因此，向量检索功能需要考虑如何降低从向量检索到其他属性读取的额外开销，同时考虑如何与过滤语句结合。

## **设计思路**

### **现有架构局限性分析**

ByteHouse 当前已经有一整套 skip index 的实现。向量索引可以作为一种新型的 skip index 来引入使用。然而，原本的 skip index 体系并不能高效支持向量检索相关计算，主要体现在以下几点：

1 当前没有针对 skip index 的 cache 机制，因此无法保证向量索引常驻内存

2 当前 skip index 只用于查询计划执行前做 mark level 的过滤，过滤的结果需要通过额外的距离计算才能获取到 topK 的结果，而不是直接使用 skip index 计算的结果来获取，计算上存在冗余。

3 skip index 只能按照 mark 粒度（mark \* granule）来进行构建，对于数据量较大的 data part 而言，会存在多个 skip index，带来更多的 IO 与计算的开销。

考虑到以上几点，我们认为现有的 skip index 架构不能支持高性能的向量检索计算，因此，我们重新针对向量检索场景设计了一套全新的架构方案。

### **整体架构**

ByteHouse 的向量检索功能整体的架构如下图所示：

![](https://developer.qcloudimg.com/http-save/yehe-2899014/c402921e3157add289963c8e62d2b3b2.png)

向量索引方面，我们接入了 hnswlib、faiss 两个比较流行的检索算法库，支持 HNSW、IVF\_PQ、IVF\_PQ\_FS 等多种常用索引。另外，考虑到向量检索需要在内存中执行，还加入了向量索引缓存机制，确保查询涉及的 data part 的索引能够常驻内存，以实现低延迟的向量检索。

另外，我们基于现有 skip index 逻辑，添加了对应索引的构建语句支持，指定每个 data part 只构建一个索引。

考虑到构建资源消耗较高，在索引构建流程上，针对此类索引，添加了构建资源（CPU）控制机制，并且针对内存使用较大场景（IVF 类型索引的 train 方法），提供了 on disk 的构建逻辑。

查询执行方面，我们在查询的各个层次针对向量检索相关的查询进行了 Pattern 识别与 Query 改写，目前主要识别 order by L2Distance/cosineDistance + limit topK 相关查询，并针对向量检索的计算特点，实现了一个全新的 SelectWithSearch 算子来执行实际的向量检索与其他属性读取操作。

新旧执行链路比较如下：

Skip Index Based Pipeline

![](https://developer.qcloudimg.com/http-save/yehe-2899014/ffdc3dbf483015edbafa42af826591f5.png)

New Pipeline

![](https://developer.qcloudimg.com/http-save/yehe-2899014/eaec8880109ad44838f62304f440a9c6.png)

构建语句例子如下：

代码语言：javascript

复制

代码语言：javascript

复制

```
CREATE TABLE test_ann
(
    `id` UInt64,
    `label` String,
    `vector` Array(Float32),
    INDEX v1 vector TYPE HNSW('DIM=960, METRIC=COSINE')
)
ENGINE = MergeTree
ORDER BY id
```

查询语句例子如下：

代码语言：javascript

复制

```
select 
    id， 
    label,
    dist 
from test_ann 
prewhere label = '...'
order by cosineDistance(vector, [query_vector]) as dist 
limit 100
```

代码语言：javascript

复制

### 

### **优化**

1 向量列读取操作消除：

* 识别向量列是否只在向量检索操作中需要，如果是，则在最终的读盘操作中，去掉向量列，减少不必要的读取操作

2 向量检索计算前置：

* 默认执行流程中，我们会为每个 data part 创建一个 SelectWithSearch 算子，计算时会针对单个 part 执行向量检索与其他属性的读取，由于读取任务最小的读取单元是一个 mark，这样的执行计划总的读取行数最大可为 (part\_num \* mark\_size \* topK) 行。造成的结果是性能会随 part 数量增多而不断下降。为了优化多 part 场景的查询性能，我们提出了一种向量检索前置的优化思路，即在执行计划实际执行之前，将所有 part 的向量检索全部先进行计算，得到全局的 topk 个结果，再进行各个 part 的其他属性读取，这样改造后，每次查询要读取的行数最高为 (mark\_size \* topK) ，实际场景测试中，latency 会有 2x 以上的提升。

![](https://developer.qcloudimg.com/http-save/yehe-2899014/f77a286056d54758497fdb694eac58da.png)

3 Cache Preload

当前支持的向量索引需要加载到内存中以后才能进行高性能的向量检索计算。在查询执行到向量检索相关操作时，如果发现待计算的 data part 对应向量索引未存在与 vector index cache 中，则需要首先调用 load 操作将 index load 到内存中，查询则需要等待 load 结束后才能继续执行。vector index load 操作会显著增加查询的执行实现，尤其是对于新写入的 data part 或者 server 重新启动的场景。针对这个问题，我们添加了 cache preload 的机制，在 data part 生成后，以及 server 启动过程中，将 index load 自动到内存中，并且添加特定的 setting，支持 table level 以及 global 的 cache preload 配置。该机制为当前支持的 HaMergeTree、HaUniqueMergeTree 引擎都添加了支持。

## **性能评测**

我们使用 VectorDBBench 对 ByteHouse 以及专用向量数据库 Milvus 进行了评测。ByteHouse 同等 recall 情况下，QPS 好于 Milvus，同时在数据插入时间上，也是优于 Milvus。

![](https://developer.qcloudimg.com/http-save/yehe-2899014/d01b7b9e70147b5fd453b7e525b87c05.png)

## **未来规划**

当前已经实现了高性能向量数据库的基本框架，但是，在资源消耗、性能以及易用性上，仍有很多需要探索和改善的方面。后续 ByteHouse 将继续针对低资源消耗向量索引、查询性能优化、易用性、大模型生态等方面进行探索。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)，分享自微信公众号。

原始发表：2024-05-06，如有侵权请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除

[设计](https://cloud.tencent.com/developer/tag/17423)

[索引](https://cloud.tencent.com/developer/tag/17462)

[olap](https://cloud.tencent.com/developer/tag/15032)

[高性能](https://cloud.tencent.com/developer/tag/17273)

[内存](https://cloud.tencent.com/developer/tag/17382)

本文分享自 java进阶架构师 微信公众号，前往查看

如有侵权，请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)  ，欢迎热爱写作的你一起参与！

[设计](https://cloud.tencent.com/developer/tag/17423)

[索引](https://cloud.tencent.com/developer/tag/17462)

[olap](https://cloud.tencent.com/developer/tag/15032)

[高性能](https://cloud.tencent.com/developer/tag/17273)

[内存](https://cloud.tencent.com/developer/tag/17382)

评论

登录后参与评论

0 条评论

热度

最新

登录 后参与评论

推荐阅读

目录

* 背景

* 负载特征

* 设计思路
  + 现有架构局限性分析
  + 整体架构
  + 优化

* 性能评测

* 未来规划

领券

* ### 社区

  + [技术文章](https://cloud.tencent.com/developer/column)
  + [技术问答](https://cloud.tencent.com/developer/ask)
  + [技术沙龙](https://cloud.tencent.com/developer/salon)
  + [技术视频](https://cloud.tencent.com/developer/video)
  + [学习中心](https://cloud.tencent.com/developer/learning)
  + [技术百科](https://cloud.tencent.com/developer/techpedia)
  + [技术专区](https://cloud.tencent.com/developer/zone/list)
* ### 活动

  + [自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)
  + [邀请作者入驻](https://cloud.tencent.com/developer/support-plan-invitation)
  + [自荐上首页](https://cloud.tencent.com/developer/article/1535830)
  + [技术竞赛](https://cloud.tencent.com/developer/competition)
* ### 圈层

  + [腾讯云最具价值专家](https://cloud.tencent.com/tvp)
  + [腾讯云架构师技术同盟](https://cloud.tencent.com/developer/program/tm)
  + [腾讯云创作之星](https://cloud.tencent.com/developer/program/tci)
  + [腾讯云TDP](https://cloud.tencent.com/developer/program/tdp)
* ### 关于

  + [社区规范](https://cloud.tencent.com/developer/article/1006434)
  + [免责声明](https://cloud.tencent.com/developer/article/1006435)
  + [联系我们](mailto:cloudcommunity@tencent.com)
  + [友情链接](https://cloud.tencent.com/developer/friendlink)
  + [MCP广场开源版权声明](https://cloud.tencent.com/developer/article/2537547)

### 腾讯云开发者

![扫码关注腾讯云开发者](https://qcloudimg.tencent-cloud.cn/raw/a8907230cd5be483497c7e90b061b861.png?imageView2/2/w/200)

扫码关注腾讯云开发者

领取腾讯云代金券

### 热门产品

* [域名注册](https://cloud.tencent.com/product/domain?from=20064&from_column=20064)
* [云服务器](https://cloud.tencent.com/product/cvm?from=20064&from_column=20064)
* [区块链服务](https://cloud.tencent.com/product/tbaas?from=20064&from_column=20064)
* [消息队列](https://cloud.tencent.com/product/message-queue-catalog?from=20064&from_column=20064)
* [网络加速](https://cloud.tencent.com/product/ecdn?from=20064&from_column=20064)
* [云数据库](https://cloud.tencent.com/product/tencentdb-catalog?from=20064&from_column=20064)
* [域名解析](https://cloud.tencent.com/product/dns?from=20064&from_column=20064)
* [云存储](https://cloud.tencent.com/product/cos?from=20064&from_column=20064)
* [视频直播](https://cloud.tencent.com/product/css?from=20064&from_column=20064)

### 热门推荐

* [人脸识别](https://cloud.tencent.com/product/facerecognition?from=20064&from_column=20064)
* [腾讯会议](https://cloud.tencent.com/product/tm?from=20064&from_column=20064)
* [企业云](https://cloud.tencent.com/act/pro/enterprise2022?from=20064&from_column=20064)
* [CDN加速](https://cloud.tencent.com/product/cdn?from=20064&from_column=20064)
* [视频通话](https://cloud.tencent.com/product/trtc?from=20064&from_column=20064)
* [图像分析](https://cloud.tencent.com/product/imagerecognition?from=20064&from_column=20064)
* [MySQL 数据库](https://cloud.tencent.com/product/cdb?from=20064&from_column=20064)
* [SSL 证书](https://cloud.tencent.com/product/ssl?from=20064&from_column=20064)
* [语音识别](https://cloud.tencent.com/product/asr?from=20064&from_column=20064)

### 更多推荐

* [数据安全](https://cloud.tencent.com/solution/data_protection?from=20064&from_column=20064)
* [负载均衡](https://cloud.tencent.com/product/clb?from=20064&from_column=20064)
* [短信](https://cloud.tencent.com/product/sms?from=20064&from_column=20064)
* [文字识别](https://cloud.tencent.com/product/ocr?from=20064&from_column=20064)
* [云点播](https://cloud.tencent.com/product/vod?from=20064&from_column=20064)
* [大数据](https://cloud.tencent.com/product/bigdata-class?from=20064&from_column=20064)
* [小程序开发](https://cloud.tencent.com/solution/la?from=20064&from_column=20064)
* [网站监控](https://cloud.tencent.com/product/tcop?from=20064&from_column=20064)
* [数据迁移](https://cloud.tencent.com/product/cdm?from=20064&from_column=20064)

Copyright © 2013 - 2026 Tencent Cloud. All Rights Reserved. 腾讯云 版权所有

[深圳市腾讯计算机系统有限公司](https://qcloudimg.tencent-cloud.cn/raw/986376a919726e0c35e96b311f54184d.jpg) ICP备案/许可证号：[粤B2-20090059](https://beian.miit.gov.cn/#/Integrated/index)![](https://qcloudimg.tencent-cloud.cn/raw/eed02831a0e201b8d794c8282c40cf2e.png)[粤公网安备44030502008569号](https://beian.mps.gov.cn/#/query/webSearch?code=44030502008569)

[腾讯云计算（北京）有限责任公司](https://qcloudimg.tencent-cloud.cn/raw/a2390663ee4a95ceeead8fdc34d4b207.jpg) 京ICP证150476号 |  [京ICP备11018762号](https://beian.miit.gov.cn/#/Integrated/index)

[问题归档](https://cloud.tencent.com/developer/ask/archives.html)[专栏文章](https://cloud.tencent.com/developer/column/archives.html)[快讯文章归档](https://cloud.tencent.com/developer/news/archives.html)[关键词归档](https://cloud.tencent.com/developer/information/all.html)[开发者手册归档](https://cloud.tencent.com/developer/devdocs/archives.html)[开发者手册 Section 归档](https://cloud.tencent.com/developer/devdocs/sections_p1.html)

Copyright © 2013 - 2026 Tencent Cloud.

All Rights Reserved. 腾讯云 版权所有

登录 后参与评论

000推荐