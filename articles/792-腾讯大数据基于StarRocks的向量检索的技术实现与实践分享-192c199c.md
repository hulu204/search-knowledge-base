---
title: '腾讯大数据基于StarRocks的向量检索的技术实现与实践分享'
company: 腾讯
tag: 工程相关
date: 2025-02-05
url: https://cloud.tencent.com/developer/article/2493289
account: 
origin: harvest-202607
---
[腾讯大数据](https://cloud.tencent.com/developer/user/1009891)

## 腾讯大数据基于StarRocks的向量检索的技术实现与实践分享

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

[社区首页](https://cloud.tencent.com/developer) >[专栏](https://cloud.tencent.com/developer/column) >腾讯大数据基于StarRocks的向量检索的技术实现与实践分享

# 腾讯大数据基于StarRocks的向量检索的技术实现与实践分享

![作者头像](https://ask.qcloudimg.com/raw/yehe-133f028/kcz4ys866s.png)

腾讯大数据

关注

发布于 2025-02-05 10:57:28

发布于 2025-02-05 10:57:28

5320

举报

文章被收录于专栏：[腾讯大数据的专栏](https://cloud.tencent.com/developer/column/1408)腾讯大数据的专栏

随着LLM技术的爆发式发展，RAG技术是解决LLM幻觉、知识更新困难等问题的关键技术。天穹OLAP StarRocks团队在此之际，积极在StarRocks上拓展向量检索的能力，并在混元部分场景下完成落地重构，赋能业务，实现了相关向量检索场景下的性能提升及使用成本降低，相关功能已积极贡献给了StarRocks社区。StarRocks 社区的年度盛会——StarRocks Summit Asia 2024 将于 12 月 7 日在北京隆重登场。 腾讯大数据的研发工程师赵裕隆将在会上详细展开讲解腾讯大数据在StarRocks上实现向量检索的技术原理及在腾讯内的实践案例，敬请期待。

内容概要

此次分享讲介绍当前业内向量检索技术及其在大数据领域的实现方式，并详细介绍了腾讯大数据在StarRocks上实现向量检索的技术原理及在腾讯内的实践案例，同时总结当前碰到的挑战及未来规划，干货满满！

![](https://developer.qcloudimg.com/http-save/yehe-1009891/179ed95f224cca2dc323984a365b644d.png)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/fbfd6f1e37b146d56283a314227ffcce.png)

StarRocks 社区作为连接用户、平台方、业务方、技术爱好者与学术人员的开放平台，始终致力于打造标准化的行业解决方案，让每一位参与者都能在实践中汲取经验，在交流中碰撞创新。
在过去三年的交流中，与数百家社区用户共同探讨了大数据领域的主要挑战：
随着实时分析需求的激增，企业面临着传统数仓的“数据孤岛”难题、复杂的数据治理挑战、海量数据存储的成本和扩展性考验，以及 AI 时代下对数据多样性与高级分析能力的迫切需求......

**Lakehouse is ALL you need**

本届峰会以 “Lakehouse is ALL you need” 为主题，聚焦 "Data + AI" 时代的极速统一架构 Lakehouse，深入探讨其在各行业的实践应用、云原生架构的独特优势以及更多创新场景的可能性。

届时，来自知名企业的技术专家将齐聚一堂，分享关于 StarRocks 核心技术、Lakehouse 生态构建及其宝贵的实践经验。从技术落地到最佳实践，从性能优化到生态发展，这将是一场涵盖全方位视角的技术盛宴！

无论你是正在规划湖仓架构的技术决策者，寻求架构优化方案的实施者，又或是关注数据技术创新的从业者都能在这里找到有价值的参考和启发。

立即扫码报名

![](https://developer.qcloudimg.com/http-save/yehe-1009891/25d7cdc12daa20dd7009a3f2680644ec.png)

PS：完成线下报名的用户，审核通过后会给您发送现场签到二维码，签到二维码是唯一入场凭证，请注意保留。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)，分享自微信公众号。

原始发表：2024-11-29，如有侵权请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除

[腾讯](https://cloud.tencent.com/developer/tag/17464)

[大数据](https://cloud.tencent.com/developer/tag/10796)

[架构](https://cloud.tencent.com/developer/tag/17314)

[实践](https://cloud.tencent.com/developer/tag/17428)

[数据](https://cloud.tencent.com/developer/tag/17440)

本文分享自 腾讯大数据 微信公众号，前往查看

如有侵权，请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)  ，欢迎热爱写作的你一起参与！

[腾讯](https://cloud.tencent.com/developer/tag/17464)

[大数据](https://cloud.tencent.com/developer/tag/10796)

[架构](https://cloud.tencent.com/developer/tag/17314)

[实践](https://cloud.tencent.com/developer/tag/17428)

[数据](https://cloud.tencent.com/developer/tag/17440)

评论

登录后参与评论

0 条评论

热度

最新

登录 后参与评论

推荐阅读

相关产品与服务

大数据

全栈大数据产品，面向海量数据场景，帮助您 “智理无数，心中有数”！

[产品介绍](https://cloud.tencent.com/product/bigdata-class?from=21341&from_column=21341)

[2026上云采购 | AI焕新·智启新局](https://cloud.tencent.com/act/pro/featured-202607?from=21344&from_column=21344)

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