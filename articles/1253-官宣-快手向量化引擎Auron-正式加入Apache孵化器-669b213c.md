---
title: '官宣 | 快手向量化引擎Auron 正式加入Apache孵化器'
company: 快手
tag: 召回
date: 2025-08-28
url: http://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247497310&idx=1&sn=685f8970aa1874ba431a267e05962dba&chksm=cebbd684f9cc5f928f2e63507e962fdf9805666f7a23d9b1fb81ec545a698d90e8512f46b0a9#rd
account: 快手技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_gif/ZxDY5TMPs0EqL7dlyXD8OFyXn6yNGvQ8uEibL6TkOHqFvaK0bR9GEhZicTHuDtaTficMGS88ecXKIVPnFJCTMz7aQ/640?wx_fmt=gif&from=appmsg)

近期，由快手开源并捐赠的向量化引擎Auron项目（原Blaze项目）正式进入全球最大开源基金会（ASF）的孵化器，移交到Apache软件基金会名下。这是Auron项目及其社区发展的重要里程碑，标志着项目可以依托ASF成熟的开源治理范式，融入全球开源共同体，获得更可持续的创新动能与影响力。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Gvicibiazzc6ibzCyu4UoCKEvmaLS0niapzocHgYm84x3I1vMvE17ORB66ibT5X8lD6LEpUttlJpYAdpIA/640?wx_fmt=png&from=appmsg)

**一、Auron介绍**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1)

Auron是基于向量化技术开发的一套Native执行引擎，可以充分利用Native代码和SIMD指令向量化优势，以实现减少资源开销、加速执行的目的。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Gvicibiazzc6ibzCyu4UoCKEvmBr4Ng9tO1RFJNon8Sl2G6Fx1TibeHmftJyA8Iw1cJz5EzLTJ8dwllcw/640?wx_fmt=png&from=appmsg)

图1：Auron架构图

其核心能力包括：

* 原生执行：采用Rust实现，消除JVM开销以取得更好的性能表现；
* 向量化计算：基于Apache Arrow列式格式构建，充分利用SIMD指令优化批处理；
* 可插拔架构：与Apache Spark无缝集成，同时设计上支持未来扩展至其他计算引擎；
* 生产环境强化优化：开发了多级内存管理、优化Shuffle格式及自适应执行策略等优化机制，并在生产环境大规模应用落地。

基于Auron，在TPC-DS上相比Spark可以取得2+倍的性能提升：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Gvicibiazzc6ibzCyu4UoCKEvmicD0XOp6GjN9kR6mGct30vUlcuaIpNB1zrLcvImCdSb8sZGL6ze4ibpA/640?wx_fmt=png&from=appmsg)

图2: Beachmark性能对比

**二、Auron发展历史与现状**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1)

2022年1月，快手大数据Spark引擎团队正式启动了Blaze项目，项目一开始便选择全面拥抱开源社区，全部代码在GitHub上公开可见。历经一年多的迭代，2023年9月，Blaze在TPC-H/TPC-DS等Beachmark上取得了显著的性能提升。同时，团队也围绕生产环境进行了大量优化，并在快手内部实现了大规模应用。目前，Blaze在快手日均运行数十万个任务、处理EB级别数据，展现出卓越的性能和稳定性，为快手每年节约数千万元服务器成本。

在社区运营方面，快手于2024年1月展开了开源社区的管理工作。自Blaze开源以来，已累计发布了10余个版本，GitHub上的Star数量超过1.5K。该项目吸引了来自全球的30多位开发者积极贡献代码，社区活跃度不断提升。凭借出色的性能、稳定性和易用性，Blaze被滴滴、携程、汽车之家、58同城、OPPO等多个行业的公司广泛使用，并在应用过程中，获得一致好评。

2025年8月，Blaze项目正式进入ASF孵化器，并更名为Auron（发音： [ˈɔːrɑːn] ），其灵感来源Aura（能量场）。Auron寓意为大数据引擎所带来的强大性能，未来，Auron社区也将会提供更多先进功能，如Flink引擎、数据湖系统、GPU/DPU硬件的集成等。

**三、加入Apache孵化器**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1)

加入Apache软件基金会孵化，源于我们对开源生态的深刻认同，以及对项目长期可持续发展的考量。目前Auron已在多家公司应用落地，验证了其实用价值。然而，开源项目的生命力不仅依赖技术先进性，更需要通过开放的社区治理、多元的贡献者参与和透明的决策机制实现持续进化。我们始终相信，开源的价值在于“共享”与“共创”。

## 我们将严格遵守Apache的治理规范，推动项目代码、文档与社区的全面透明化，吸引更多开发者参与技术迭代，与Apache生态中的其他大数据项目（如Spark/Flink/Celeborn等）形成技术互补，共同推动大数据领域的技术持续创新。

## 

我们坚信，在Apache基金会的指导与社区的支持下，Auron项目将加速成长为具有全球影响力的开源项目，为技术创新贡献长期价值。

**四、致谢**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1)

感谢来自Auron社区的所有贡献者，以及我们上游项目贡献者的付出！

感谢众多用户对于Auron项目的信任及推广！

特别致谢Calvin Kirs作为本项目的Champion，Xuanwo、Becket Qin和Nicholas Jiang担任本项目导师，在Auron项目进入ASF孵化器的过程中，各位给予了很大支持和帮助！

关注 Auron 官方公众号，即时获取最新资讯！

欢迎加入

![图片](https://mmbiz.qpic.cn/mmbiz_png/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpF09GTXcEcG4Fy9SdWsPp2icyibcRsickibvTSQXgITrJPOF9bApGEbyZvg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1)

**我们诚挚地邀请对Auron感兴趣的各位开发者和用户加入开源社区，共同推动项目进一步的发展，您可以通过以下方式关注和了解社区的最近动态，期待您的加入！**

* GitHub仓库：

  https://github.com/apache/auron/
* 官方网站：

  https://auron.apache.org/
* 订阅邮件组：

  dev-subscribe@auron.apache.org

”

【END】