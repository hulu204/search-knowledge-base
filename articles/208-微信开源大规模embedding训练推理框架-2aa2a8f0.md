---
title: '微信开源大规模embedding训练推理框架'
company: 腾讯微信
tag: 召回
date: 2022-06-15
url: http://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247502213&idx=1&sn=fc146301867e6dcfc1c76eb4ead978d0&chksm=a691ba6891e6337e86096af1a44fc35fbbf5ec1c3af779b4bf84d00dc5738ceb80acfadd3df4&scene=27#wechat_redirect
account: 浅梦学习笔记
origin: readme
---
embedx 是基于 c++ 开发的、完全自研的分布式 embedding 训练和推理框架。它目前支持 **图模型、深度召回模型和图与排序、图与召回**的联合训练模型等。

embedx是腾讯 AI 领域开源协同项目，获得过开源协同优秀奖、微信最具技术价值文集奖等，经过近 3 年的迭代，已经趋向稳定和成熟，在设计和开发的过程中，参考了业界开源项目的大量经验，现将其开源反哺业界，希望该项目能持续的进行迭代。

 

项目链接请参考：https://github.com/Tencent/embedx

**01**

**项目特点一: 效率高**

**大规模图引擎：**我们设计并实现了支持十亿节点、千亿边的大规模图引擎，以 op 形式提供了包括 random walk、negative sampling 和 neighbor sampling 等多种分布式采样接口。通过层次化采样解决分布式负例采样一致性、拒绝采样解决动态随机游走效率低、partial sum解决异构的邻居采样等问题大幅的提升了分布式采样的效率。

**高性能计算引擎:**基于 deepx\_core 实现神经网络计算，deepx\_core 提供了能自动求导的静态图引擎，该引擎支持一百余个 op, 它具备大规模稀疏、高性能、跨平台等优点。目前 deepx\_core 已经对外开源，请参考 https://github.com/Tencent/deepx\_core。

我们的解决方案的性能普遍是开源框架的数倍，机器节省 30%-60%。

**02**

**项目特点二: 模型多**

**丰富的模型：**支持训练**十亿级节点、千亿级别**的图模型如 deepwalk、graphsage 等、支持训练**百亿级样本、百亿级特征**的深度召回模型如 youtubednn、dssm 等，创新性的提出并支持训练图与深度学习的联合建模模型如 **图与排序的联合建模模型** graphdeepfm、**图与召回的联合建模模型** graphdssm 等。

**模型创新：**通过解决深度模型与图模型在排序、召回等场景中的两阶段使用方式带来的优化目标不一致等难题， 在公司内首次落地了图与排序、图与召回等模型的离线训练与在线推理，在业务中取得了不错的效果。

我们沉淀了推荐、搜索、风控等领域内累计近 20个常用的模型。

**03**

**项目特点三: 实时性**

**实时流程：**为捕获用户的实时行为，我们搭建了分钟级的online learning流程，即从实时数据流消费、召回实时训练与推理（基于embedx）、排序实时训练与推理（基于deepx\_core）， **全流程在分钟级内生效！**

 

**流程改进：**在分钟级的online learning流程中，通过模型参数增量导出解决了模型训练结束后导出的效率问题，通过模型参数异步更新解决了复杂模型在线推理的效率问题，通过重要性采样纠偏实时样本的偏移分布解决了效果问题。

 

我们的解决方案具备全流程分钟级的实时能力，在多个推荐业务成功落地。

**04**

**项目应用**

embedx 累计支持公司**12 个业务、 30 多个团队使用、上线百余次**，收到合作团队多封邮件认可反馈。我们帮以下重要产品落地使用了 embedx, 并取得了性能和效果双丰收：微信看一看、微信视频号、微信搜一搜、微信支付、微信安全、腾讯新闻、应用宝、QQ 音乐、JOOX 音乐、腾讯课堂、领航平台和腾讯黑产打击等。

![](https://mmbiz.qpic.cn/mmbiz_png/W7W9IgARmG95dqAsfOMz2HZ0ERMLiaFyibGNiaNUpG3AtPr8yWtP5F6rthuylI9PTqk3rbDAssBUhQUtHau7J2Leg/640?wx_fmt=png)

**写在最后**

站在巨人的肩膀上才有了现在的embedx，它的高性能一部分来自于高效的计算引擎 deepx\_core，它的代码质量受到团队 leader  kimmy 的严格要求。

 

自 2019 年下半年启动一直保持核心开发 2~3 人的规模，我们先后攻克了图模型和深度召回模型的分布式训练、模型小时级、分钟级训练、在线推理和端到端模型创新等难题。 感谢以下开发者 yuanhang、chuan、 joyce、 hill、 tinkle 、kimmy、zhenting、yuanqing、brian、yandong、yalong在不同时间做出的贡献。

![](https://mmbiz.qpic.cn/mmbiz_png/W7W9IgARmGibWxTcD8A1yKWd7EmLsclz3FIMS1SCH1icT4KvaSrGOIAzdQZcWP3TMHds6XH2xZLVqZpX6micI0hHA/640?wx_fmt=png)

最后介绍下我们团队，我们是微信搜索应用部算法平台团队，引用 deepx\_core 开源时的一段话来再次表达我们对代码和系统的认知，“我们把代码和系统视为艺术，我们推崇小而美的系统，我为我们的工程师文化和艺术品而骄傲”。未来我们将开源更多项目，敬请期待。

---

https://github.com/Tencent/embedx

(点击文末阅读原文直接访问)

请给项目 一个 Star !

欢迎提出你的 issue 和 PR！

 国内镜像地址：

https://git.code.tencent.com/Tencent\_Open\_Source

（登录后才能访问公开项目）

腾讯工蜂源码系统为开源开发者提供完整、最新的腾讯开源项目国内镜像

## 推荐阅读

* [学习交流小组精彩内容摘要 No.99](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247502170&idx=1&sn=d6a965163474f79c982b5f9c71cf8fe5&scene=21#wechat_redirect)
* [node2vec随机游走优化思路和代码实现](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247484475&idx=1&sn=4c3941ad66f0ecaf9dcca0586cb18c44&scene=21#wechat_redirect)
* [实现大规模图计算的算法思路](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247498980&idx=1&sn=abc7777821f4545d186c45096d0f1103&scene=21#wechat_redirect)
* [大规模图算法在京东广告的实践](https://mp.weixin.qq.com/s?__biz=MjM5MzY4NzE3MA==&mid=2247496139&idx=1&sn=20fc6861519e6cfa5547ae4c7a9bf570&scene=21#wechat_redirect)

想了解更多关于**推荐系统与图算法**的内容，欢迎扫码关注公众号**浅梦学习笔记**。回复**加群**可以加入我们的交流群一起学习！

欢迎加入**星球群**，一起参与**前沿算法技术与实践经验**的分享学习。

![](https://mmbiz.qpic.cn/mmbiz_png/6QjJZbq42RZdwF3gubicCdufYFpQxOmXKPtkbFYQDcOWe6PyVOlJopa6PvKI0lsAiayiaFNCELYYgZbZ6yAr1n8IQ/640?wx_fmt=png)

****码字很辛苦，有收获的话就请********分享********、********点赞********、********在看********三连吧****👇****