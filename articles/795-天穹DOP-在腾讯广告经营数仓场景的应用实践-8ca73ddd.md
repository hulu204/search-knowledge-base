---
title: '天穹DOP 在腾讯广告经营数仓场景的应用实践'
company: 腾讯
tag: 工程相关
date: 2024-06-27
url: https://cloud.tencent.com/developer/article/2432314
account: 
origin: harvest-202607
---
[腾讯大数据](https://cloud.tencent.com/developer/user/1009891)

## 天穹DOP 在腾讯广告经营数仓场景的应用实践

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

腾讯大数据

[社区首页](https://cloud.tencent.com/developer) >[专栏](https://cloud.tencent.com/developer/column) >天穹DOP 在腾讯广告经营数仓场景的应用实践

# 天穹DOP 在腾讯广告经营数仓场景的应用实践

![作者头像](https://ask.qcloudimg.com/raw/yehe-133f028/kcz4ys866s.png)

腾讯大数据

关注

发布于 2024-06-27 13:09:33

发布于 2024-06-27 13:09:33

7960

举报

文章被收录于专栏：[腾讯大数据的专栏](https://cloud.tencent.com/developer/column/1408)腾讯大数据的专栏

![](https://developer.qcloudimg.com/http-save/yehe-1009891/d3be22265de12ebb93a030a5a3eabf51.png)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/28788252bc90286a4369086636b3c581.png)

■ 腾讯广告经营数仓是腾讯广告打造的数据分析和数据服务平台，**它提供了包括数据运营分析、广告优化分析在内数据分析支持，以及数据可视化服务。**经营数仓积累了大量的广告效果数据、客户管理信息和产品工具数据，**为腾讯内众多的数据分析和运营分析用户提供便捷高效的 SQL 取数服务。**为了保障数据查询服务的稳定与高效，该数仓不仅采用了Spark引擎，还部署了Presto集群，目的是能够根据用户提交的SQL的特点，智能选择最合适的查询引擎。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/e94c2cebc6055bc0c6c07378ba59ee9b.png)

经营数仓承载了大量广告相关数据，这些数据存在显著的热点效应，被频繁访问的热点数据给 底层存储造成了很大压力，数据存储节点的请求堆积明显，不仅影响了经营数仓的任务执行时间，还会给访问该存储集群的其他任务产生影响。因此需解决热点数据问题，来降低任务执行时间，提升底层存储的可用性。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/4d9967c9be0559d47dc3ecf2b571fd85.png)

对此场景，天穹DOP团队，设计了缓存架构解决热点数据问题，并通过一系列实践措施，对查询效率和存储性能进行了重点优化：

■ 统计 SQL 执行与数据表访问的频率，找到热点库表信息；

■ 统计存储引擎审计日志，分析得到高频访问的存储路径，通过存储路径反推得到库表信息；

■ 将两种渠道分析的结果取交集，分析得到数据热点表。

识别并区分出热点和非热点数据后，通过天穹 DOP Cache 路径级的黑白名单能力，就可以保证热点数据访问 DOP Cache，非热点数据直接访问底层存储。对于热点数据，天穹 DOP Cache 通过高性能 SSD 介质和 IO 隔离能力，可以提升读取性能。另外，天穹 DOP Cache 为上层应用提供了 Hadoop API 、Posix 以及 S3 等多种接入方式，经营数仓只需要进行少量改造即可接入，任务 SQL 不需要任何变动。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/b750a66e0e53753b7589d750229a114f.png)

**1.整体架构**

■ 经营数仓分析工具是自助的数据提取与数据分析服务平台，具备 SQL 查询、点选、数据聚合以及可视化等能力，可以通过 JDBC/HTTP 等方式承载用户 SQL 请求，数据平台调用 Spark/Presto 等引擎进行数据分析，天穹DOP Cache 集群作为数据缓存层，负责热点数据的缓存，承接热数据 IO，整体架构如图：

![](https://developer.qcloudimg.com/http-save/yehe-1009891/34c7af583bb7db92dea880cde6edaa38.png)

**2.DOP Cache 智能缓存管理与性能优化功能**

**基于 ZK 的黑白名单功能**

![](https://developer.qcloudimg.com/http-save/yehe-1009891/f4e5c6286814cc0445f0f207b40a9d97.png)

DOP Cache Client 通过前缀匹配算法满足可配置的数据访问需求，支持路径级黑白名单能力。配置了不同访问规则的多组黑白名单信息通过 ZK 管理，使用 ZK config ID 区分，另外，client 侧缓存 & 超时同步机制可以避免海量的 client 实例引起的 ZK 节点负载陡增问题。

**段内存管理算法**

通过监控日志发现部分 DOP Cache worker 节点出现了 direct memory OOM，通过 ，Kona- profiler 和 MAT 分析堆栈信息，发现 direct memory 中存在大量内存碎片。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/b7c269ba4ff07cc52c97a2d26aa2e044.png)

源码分析后发现 DOP Cache worker 内存分配算法存在优化空间，然后调研并实现了段内存管理算法：将内存分为 128 KB ~ 2MB 不等的多层，线程请求内存时分配一块满足要求的最小内存，减少无法重复使用的内存碎片。

**3.基于Journal tailer的数据一致性方案**

数据一致性问题是缓存架构面临的突出问题。经营数仓场景采用读写分离的架构：写流量落盘持久化存储，读流量接入缓存。这种场景需要考虑数据一致性与实时性。由于经营数仓场景的的任务对于实时性要求相对宽松，可以引入自研的 Journal tailer 组件解决数据一致性，架构如下：

![](https://developer.qcloudimg.com/http-save/yehe-1009891/61b8fb5f416f51423f4b3e56df066c68.png)

■ **DOP Cache**

缓存引擎，承接读流量，向 Journal tailer 注册监听路径，接收 Journal tailer 的通知并完成数据同步。

■ **DOP-FS（HDFS)**

持久存储层，承接写流量，完成数据持久化，数据变化通过 Journal node 完成同步 。

■ **Journal Node Cluster**

持久化存储的 journal 同步与管理集群，保证持久化存储的状态一致性。

■ **Journal tailer**

持久化存储监听器负责管理监听路径列表，当路径出现变化 （create, delete, append 等）时通知上层组件。Journal tailer 组件提供了 client sdk，支持上层业务组件注册监听路径。它的工作原理是分析持久化存储的 edit log，当过滤到监听路径相关的 edit log时，通知注册该监听路径的组件。Journal tailer 已支持多节点部署提供服务，提升集群可用性，同时满足分钟级以下延迟的一致性需求。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/76a4c577119faa761ffbb85ee3d69161.png)

目前，腾讯广告经营数仓场景的 Presto 和 Spark 两种计算引擎接入 天穹DOP Cache，加速用户任务。

在日均查询量稳定的情况下，观察任务运行时间 P99 曲线，加速效果明显。Spark 场景任务平均等待耗时和任务平均执行时间均**下降 40%+**。Presto 场景任务平均耗时**下降 30%+。**此外，引入天穹 DOP Cache 后，底层存储节点的请求峰值整体**下降 50%+**，提升了底层存储系统的稳定性。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/968bd15b506a9c26b5b53a343bcd0393.png)

通过实施上述方案，腾讯广告业务数据仓库场景中SQL的平均执行时间有了显著下降。为了进一步优化体验，后续大数据团队还将在客户端版本升级和元数据同步方案两个方面持续进行迭代改进：

■ 开发HCFS-adapter组件，减轻用户在DOP Cache客户端SDK版本升级过程中的变更负担。

■ 增强Journal tailer的功能：支持一组Journal tailer集群同时监控多个底层存储系统，提升Journal tailer的服务性能，简化部署和运维流程。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/3fe269a7f90e81a89c3c5e42d93b00e9.jpg)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/bb0c56fa659ec083df73cd615d1a3bce.jpg)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/9883e37bde7e5d10e6a78aff08e03315.jpg)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/28d85953cade4b46e86a57083e84b445.png)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/93d3eb009509f006213ba8c2820b8991.png)

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)，分享自微信公众号。

原始发表：2024-06-26，如有侵权请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除

[存储](https://cloud.tencent.com/developer/tag/10665)

[缓存](https://cloud.tencent.com/developer/tag/10670)

[实践](https://cloud.tencent.com/developer/tag/17428)

[数据](https://cloud.tencent.com/developer/tag/17440)

[腾讯](https://cloud.tencent.com/developer/tag/17464)

本文分享自 腾讯大数据 微信公众号，前往查看

如有侵权，请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)  ，欢迎热爱写作的你一起参与！

[存储](https://cloud.tencent.com/developer/tag/10665)

[缓存](https://cloud.tencent.com/developer/tag/10670)

[实践](https://cloud.tencent.com/developer/tag/17428)

[数据](https://cloud.tencent.com/developer/tag/17440)

[腾讯](https://cloud.tencent.com/developer/tag/17464)

评论

登录后参与评论

0 条评论

热度

最新

登录 后参与评论

推荐阅读

相关产品与服务

对象存储

对象存储（Cloud Object Storage，COS）是由腾讯云推出的无目录层次结构、无数据格式限制，可容纳海量数据且支持 HTTP/HTTPS 协议访问的分布式存储服务。腾讯云 COS 的存储桶空间无容量上限，无需分区管理，适用于 CDN 数据分发、数据万象处理或大数据计算与分析的数据湖等多种场景。

[产品介绍](https://cloud.tencent.com/product/cos?from=21341&from_column=21341)[产品文档](https://cloud.tencent.com/document/product/436?from=21342&from_column=21342)

[对象存储COS新用户低至1元！](https://cloud.tencent.com/act/pro/cos?from=21344&from_column=21344)

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