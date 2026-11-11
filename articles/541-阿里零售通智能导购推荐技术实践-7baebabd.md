---
title: '阿里零售通智能导购推荐技术实践'
company: 阿里
tag: 推荐
date: 2019-07-11
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247492047&idx=1&sn=7db1f1eaadfdac75c5a0ae0e3a7beea1&chksm=fbd753a3cca0dab5fe09c091fb36c0ae9ba9ae83af38593d333bbdf61d97ee137b1577611ec0&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GbnDbYhQsEBrY9tGyKlMdOJUb4IY1bH9xC1iclqWTIgxvGjY5CAsbXuA/640?wx_fmt=png)

文章作者：零售通算法团队

编辑整理：Hoh Xil

出品社区：DataFun

注：欢迎转载，转载请注明出处。

零售通是阿里巴巴 B 类事业群针对线下零售店推出的解决方案，通过与品牌商、本地经销商紧密合作，为零售店提供品质好货，升级社区零售店的便民服务能力，肩负着“共建智能分销平台”和“让百万小店拥抱 DT 时代”的重要使命。在这种 B2b2c 新型的分销模式中，智能导购推荐不仅提供一站式 APP 进货方式，帮助小店主高效便捷地从平台批发进货，进而服务小店周边 C 端消费者，同时承载品牌商推广及自营销，赋能品牌商通过小店高效精准地触达 C 端消费者，通过智能化导购推荐技术，实现 B 端供给和 C 端需求的高效链接和精准匹配。

******▌业务背景******

零售通 APP 导购推荐主要包括大促会场、日常频道和猜你喜欢3大类核心场景，如下图1所示。左侧图为618会场入口，包括榜单主会场入口以及行业分会场入口，榜单主会场为小店主提供当季该区域最适合的商品进货清单，供小店主采购决策，行业分会场是品牌商的营销阵地，通过品牌券和红包等营销方式触达更多的小店和 C 端消费者，实现品牌商数字分销渠道下沉；右侧上图为日常频道，包括羚羚发、网红美食、进货洋货，以及精选频道和限时特价等，通过差异化的频道定位，满足不同小店主个性化的进货诉求；右侧下图为猜你喜欢，具体场景包括 APP 首页、进货单页、凑单页、商品详情页、支付成功页等推荐区块，猜你喜欢贯穿在小店主购前、购中、购后整个采购流程，提供个性化交互式沉浸式采购体验。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GDx1pRx558geONhPQc9Ah70Xza2bp3ibqMN1WpJOhvnIv6rGAcF2c1qw/640?wx_fmt=png)**

图1 零售通 APP 导购推荐场景

从图1介绍可以看出，零售通导购推荐涉及的业务领域比较广泛，通过一篇文章讲清楚整个业务领域所有的问题以及技术实践背后的思考可能不太现实，因此本文后续部分围绕零售通猜你喜欢重点展开介绍，一方面是因为猜你喜欢产品形态在诸如电商购物、本地生活、旅游出行、文化娱乐、在线教育等行业的 C 端 APP 场景比较成熟，大家阅读起来易于理解，更为重要的是我们想与大家一起分享探讨以零售通为代表的 B2b2c 猜你喜欢具有哪些业务特点？遇到了哪些技术挑战？以及我们的一些实践和经验总结。

零售通猜你喜欢贯穿在小店主购前、购中、购后整个采购流程，如下图2所示。当小店主打开零售通 APP，首页猜你喜欢提供精准流量分发入口，意图明确的小店主通过 Query 推荐引导到搜索页，意图模糊的小店通过精选爆品、品牌专辑、类目榜单等逐步引导到商品详情页；通过购前流量引导，小店主逐步进入了购中流程，此时小店主可能在商品详情页找同款，或在凑单页凑足营销活动门槛以及388包邮，亦或者在进货单页找相似品，然后在进货单页下单；商品下单后进入了购后流程，支付成功页推荐复购券引导小店再次购买。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0G2TnjypQa6nwA9nuBUAPu63ycM5pbK42avFVWiak1ibiaABMar3iceXwUHQ/640?wx_fmt=png)**

图2 零售通猜你喜欢场景

在零售通 B2b2c 业务模式下，猜你喜欢具有如下业务特点和挑战：

1. 小店主采购心智：一方面区别于 C 端用户偏冲动消费，B 端小店主比较理性，采购行为通常具有计划性和周期性，不同小店主有各自的采购深度、进货习惯，需要采用差异化的推荐策略，针对深度小店需要采用个性化推荐，基于小店主周期进货习惯以及小店内商品的库存消耗情况，为小店精准推荐补货清单，针对浅度小店，需要结合小店属性和协同过滤，为小店混合推荐潜在商品；另一方面 B 端小店主盈利诉求较强，对平台营销活动和商品的价格比较敏感，在推荐算法设计中，我们需要综合地考虑平台营销门槛以及价格因素对成交转化的影响，例如在包邮、满减满赠凑单推荐中，如何在带有约束条件下实现推荐的商品单 UV 价值最大化。

2. 线下零售特点：线下新零售是一个巨大的市场，小店主进货渠道较多，既可以通过线上 b2b 平台 ( 零售通、新通路、易酒批… )，也可以通过线下经销商批发进货，目前各个渠道覆盖的行业类目有差别，提供的商品也有特定的售卖范围，商品的区域化售卖特点比较明显，另外小店进货目的是为了服务周边 C 端消费者，其所在地理位置很大程度决定了小店能辐射的服务范围。如何结合阿里巴巴大数据能力，挖掘小店周边 C 端消费者需求，为小店提供合理的补货建议，基于 LBS 属性的小店商品推荐是一个充满挑战、值得深究的问题。

********▌技术实践********

1. 算法架构

零售通猜你喜欢技术架构如下图3所示。用户打开零售通 APP，产生的实时数据存在 ABFS，TPP 请求 ABFS、UPS 分析用户意图，通过推荐引擎 BE 召回商品返回给 TPP，TPP 接着调用 RTP 打分服务进行精排和重排，最后展现给用户。离线和实时排序模型训练和参数调优通过 PAI 和 Porsche 完成，排序模型支持 T+1 和实时更新。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GLicicMSYMIoOK1QPuY0aht6VOib5NcnCtNWpib5q7mQwfLaD4E1T9ib4IiaA/640?wx_fmt=png)**

图3 零售通猜你喜欢技术架构

推荐服务 TPP ( The Personalization Platform )，阿里个性化推荐平台，TPP 依托阿里中台强大技术架构能力，简化了数据流的调用过程，使得各种推荐算法、数据、模型能够积累、对比和复用，支持实时 AB 报表，支持算法快速迭代上线。

基础特征服务 ABFS ( Ali Basic Feature Server )，ABFS 提供统一的特征服务，实现用户基础行为特征和统计特征的收集和处理，用于实时训练反馈，实现用户特征共享和特征价值最大化。

推荐引擎 BE ( Basic Engine )，推荐场景定制的召回引擎服务，支持不同类型的召回数据在线 Union、Join、Filter 等，深度集成和定制了 KNN 库，支持向量索引的分布式构建和查询，提供向量召回能力。

在线打分服务 RTP ( Real time prediction )，RTP 接收到 TPP 传入的商品列表、上下文特征以及用户特征后，在线 FG 和打分输出，支持多种机器学习模型 ( PSLR、GBDT… )、深度学习模型 ( WDL、CNN、RNN、MultiTask… )。

模型训练 & 特征平台，Porsche 在线机器学习训练平台，基于 Blink 的实时机器学习平台，提供了日志处理、特征计算和实时建模，为算法提供端到端的秒级延时的实时模型训练能力。

2. 匹配模型

零售通匹配模型经历了从热门召回，到协同过滤，再到 DeepMatch 模型等一系列优化实践。热门召回虽然比较简单，但具有实践意义，一方面可以直接应用于热门排行榜推荐，另外也为协同过滤、DeepMatch 的算法迭代优化提供 Baseline，我们可以评估算法每次迭代相对 Baseline 的收益大小。

协同过滤主要基于图结构，现实世界中的图主要分为 user-user 同质网络 ( 社交网络、Facebook… )，以及 user-object ( 电商、视频… ) 二部图网络两种。零售通导购推荐 CF 主要基于 user-object 网络，分为 item-CF 和 user-CF 两种，item-CF 侧重于挖掘 item 之间关系，通过用户历史共现行为计算 item 之间相似度，离线计算方便，应用较为广泛，其中图的相似度计算有很多种[1]，例如 Cosine、Adamic/Adar、Jaccard、PageRank、simRank…，目前零售通 item-CF 主要采用阿里巴巴自主研发的 eTREC 和 Swing，算法原理如下图4所示，线上实践证明，相比于传统 item-CF，eTREC 和 Swing 抗噪声更强，并且通过调参能一定程度抑制“哈里波特”和长尾现象。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GmXFz6uUUiasfZHYjK2JsXk02XwiaSMo9Y2z2RdxKCfethOlSwo37sI5A/640?wx_fmt=png)**

图4 Item-CF 相似度计算

上述 Item-CF 在零售通进货单相似商品推荐、APP 首页猜你喜欢基于用户实时行为触发 U2I2I 召回等场景，取得了不错的业务效果，但都是基于用户共同行为关系挖掘的 I2I 算法，召回限定在有用户历史行为的商品候选集中，推荐的商品的发现性偏弱，容易导致“越推越窄”的问题，因此我们尝试了 Graph embedding I2I，在 User-Item 二部图加权采样 ( 带权重的随机游走 )，采用 Skip Gram 模型 ( DeepWalk[2]、Node2Vec[3]… ) 训练出商品的 Embedding，使用语义距离计算得出商品之间的距离，截取 TOPK 相似度商品作为商品的 embedding I2I，目前已经在进货单推荐场景上线。

在 Graph Embedding I2I 的基础上，我们目前正在尝试加入商品的 Side Information，进一步提升 Embedding 的泛化学习能力，更好地解决长尾以及商品冷启动问题，如图5所示[4]。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GO5zzRydDCzf4dS8meysichesTZ9HgVccHsfuPQpjE1D0KbeUWibiaUtyQ/640?wx_fmt=png)**

图5 Graph embedding I2I

前面介绍了 item-CF 在零售通导购推荐场景的应用，同样 user-CF 在零售通导购推荐也有相关业务实践和结果，我们知道 user-CF 多用于挖掘有共同兴趣的小团体，第一节业务背景中已经谈到小店的 LBS 属性非常明显，下面我们介绍如何将传统的 user-CF 与小店 LBS 属性相结合，深挖小店 U2U 相似度模型，为小店主推荐的新颖性更好的商品。

零售通小店有哪些关键 LBS 属性呢？如图6所示，我们通过小店 APP 采购行为分析以及线下小店走访调研发现，小店商圈 ( 学校、医院、高端住宅... ) 和面积 ( 20平米、50平米、100平米… ) 是影响小店采购的关键因素，商圈刻画了小店周边 C 端消费人群和消费目的，也是商品售卖和品牌营销重要的区域粒度，小店面积则反映小店满足消费者需求的能力，因此同一商圈、面积差不多的小店在消费需求、商品结构、供给能力、采购习惯等方面相似度较高。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GM1AnMibFiamnRyhN3NFRic2XyB45kt8DgFta13RYat0IknwkhcIgwyQMw/640?wx_fmt=png)**

图6 小店 LBS 属性信息

user-CF 核心是小店相似度计算，首先我们通过小店商圈、城市层级、区域街道、面积等因子，计算小店间 LBS 属性相似度，其次基于小店主在零售通的采购商品序列，通过 Doc2vector 训练小店主的向量表示，通过 simHash 计算向量距离，得出 APP 采购行为相似度，最后综合考虑 LBS 属性相似度、APP 采购行为相似度两方面计算得出小店相似度得分。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0Guwu4wiaxJEcxZ5VjBFUuSM7Xa62s9UD3gccNq4wI4HkoNib98VIP2iaxw/640?wx_fmt=png)**

图7 小店相似度计算

基于上述思路，我们开发了一套基于小店属性的 user-CF 混合推荐模型，如下图8所示，该模型综合考虑了不同生活习惯及气候因素的地域差异、不同消费能力的城市层级差异、同城市不同街道区域的差异，以及不同小店群的进货习惯，在 APP 猜你喜欢取得了不错的业务效果。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0Gbyrj2kmz8zEibz2jakbGsAkTFbQtqic0xb9DtachFQCzBS9EhUCmggVw/640?wx_fmt=png)**

图8 基于小店属性的 user-CF 推荐

前面介绍了零售通导购推荐热门召回、协同过滤相关技术实践，在深度匹配模型方面，我们也正在进行了一系列尝试，如图9所示[5,6]，深度匹配对用户和商品在同一空间进行向量表达，通过用户向量在线召回 TopK 个与其近邻的商品向量，得到用户感兴趣的商品,增加 Side Information 能进一步提升用户和商品的 High-Level 表达能力。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0G7zXxeIQ33icmibvSpeHecGJMpvQ6Y9J67ibkro3lR6jrpeYYVu35fenQQ/640?wx_fmt=png)**

图9 Multi-Interest Network with Dynamic Routing ( MIND ) 模型

3. 排序模型

零售通导购推荐排序包括粗排、精排、重排三个阶段，由于召回商品集数量较大，考虑到性能因素，需要通过粗排截断选取 topN 商品传递给精排，精排对 topN 商品针对特定的业务目标精准排序，重排主要实现业务策略及干预，下面我们重点介绍精排模型。

深入理解业务目标、扎实的特征工程以及细致的模型选型和调参，对于排序模型迭代至关重要。零售通导购推荐业务目标为 CTR、CVR、SKU 宽度等，基于上述目标，我们重点展开在特征工程和模型演进方面的相关工作。

排序模型的特征可以归纳为以下几大类：

* 离散特征：小店 id 类，如小店 id、区域 id 等；商品 id 类，如商品 id、类目 id 等；上下文类，如星期几、天气等；以及上述 id 类特征的交叉组合。
* 连续特征：主要包括小店、商品的基础统计特征，小店-商品的交叉统计特征，以及小店周边 C 端消费者的统计特征。
* 序列特征：小店周期性采购的商品序列；小店实时搜索 Query 序列、点击的商品序列等。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0G7DHRiaYoGnUDccOxZeUe8JC1R4bMaMe6MDNfWE5hicOq9wlhXkMVGh1A/640?wx_fmt=png)**

图10 零售通导购推荐排序模型演进

零售通导购推荐排序模型演进如图10所示，传统的机器学习模型 ( LR、GBDT、GBDT+LR… ) 通过特征工程持续迭代，目前在已经取得了较好的业务效果，目前作为排序模型迭代的基线。

传统的机器学习模型需要大量的人工经验构建原始特征以及组合交叉，人力成本较高，随着 Deep Crossing[7]、 Wide&Deep[8] 等相继在2016年提出，深度学习模型在特征学习表达、模型效果等方面有诸多优势，基于此我们上线了基于 TensorFlow 的深度排序模型 ( FM[9]、WDL、DeepFM[10]… )，挖掘小店主、商品、C 端消费者、以及天气、时间、营销活动等深层次隐含特征关系，提升排序模型的表达能力和泛化能力，另外我们正在开展 Attention、Transformer[11] 在排序模型的相关实践与应用。

**********▌********************特色探索**********

零售通 APP 货架具有新零售 B2b2c 导购推荐特色，APP 端货架真实还原线下小店内货架的商品结构和位置摆放，通过一站式货架商品组合售卖，提供品类级别的分销解决方案，提升线下小店进货效率，最大化小店经营坪效，同时通过货架链接品牌商资源，打造成为品牌商面对线下消费者营销的主阵地。

零售通 APP 货架导购技术核心是基于 LBS 的精准组货推荐和商品成列算法，基于阿里巴巴大数据中台，结合小店周边消费者线上数据 ( 支付宝、淘宝、饿了么… ) 和线下数据 ( 大润发、POS… )，以及小店主在阿里经济体全域行为数据，运用大数据和算法的力量，推荐最适合线下零售小店盈利增收的商品组合货架，实现“让线下没有难做的生意”。

**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GwQXKeIfBp3qPTwtYV3BChibiaIDCA7pK99teicH6OXbkHYPp0I9aibic7Eg/640?wx_fmt=png)**

图11 零售通导购推荐 - APP 货架

************▌总结思考************

本文介绍了阿里零售通智能导购推荐技术实践，从业务背景、算法架构、匹配模型、排序模型、特色探索等方面，我们重点概述 B2b2c 推荐的特点、算法迭代中的思考以及实践经验的总结，当然受限于篇幅，推荐算法其他部分，诸如意图识别、文案展示、营销表达、多物料混排等，我们没有一一展开详述，有兴趣的同学可以线下深入讨论，我们希望借着分享线下新零售推荐算法的机会，与大家一起交流学习，共同进步。新零售面向线上线下亿万消费者，充满各种技术挑战，大家一起努力加油。（报名方式见文末海报）

**▌参考文献**

[1] The Link Prediction Problem for Social Networks[2004]

[2] Deepwalk: Online learning of social representations (SBU 2014)

[3] Node2vec: Scalable Feature Learning for Networks (Stanford 2016)

[4] Billion-scale Commodity Embedding for E-commerce Recommendation in Alibaba. (Alibaba 2018)

[5] Multi-Interest Network with Dynamic Routing for Recommendation at Tmall (Alibaba 2019)

[6] Behavior Sequence Transformer for E-commerce Recommendation in Alibaba(Alibaba 2019)

[7] Deep Crossing: Web-Scale Modeling without Manually Crafted Combinatorial Features (Microsoft 2016)

[8] Wide & Deep Learning for Recommender Systems (Google 2016)

[9] Factorization machines (ICDM 2010)

[10] DeepFM: a factorization-machine based neural network for CTR prediction (HIT-Huawei 2017)

[11] Attention Is All You Need (NIPS 2017)

****************▌阿里巴巴零售通介绍：****************

阿里巴巴零售通以“共建智能分销网络、让百万小店拥抱DT时代”为使命愿景，是一个为城市社区零售店提供订货、物流、营销、增值服务等的互联网服务平台，是阿里巴巴商业操作系统的有机组成部分，过去三年业务体量一直呈爆发式增长。

******************▌阿里巴巴零售通算法团队介绍：******************

阿里巴巴零售通算法团队，致力于用数据和算法的力量，帮助社区小店智能化经营和提升消费者体验，同时和品牌商、供应商打造低成本、高效率的数字化分销渠道。团队有来自国内外顶级高校和一流公司的优秀人才，技术氛围浓厚，简单有冲劲。在这里，你可以依托阿里巴巴集团业界最先进的大数据处理和分布式计算平台，运用机器学习/深度学习、数据挖掘、运筹优化等前沿技术，解决新零售场景下有特色、有挑战的算法问题。期待更多优秀的算法人才加入，共创新零售的浪潮！

******************▌零售通职位推荐：******************

Base：杭州

岗位名称：算法专家，高级算法专家

简历投递地址（点击文末阅读原文）：

https://job.alibaba.com/zhaopin/position\_detail.htm?spm=a2obv.11410903.0.0&positionId=66604

******************▌!!! 想了解更多关于新零************************************售相关的算法技术吗？******************

******************7月19日，******************由阿里零售通主办，DataFun 协办的技术沙龙来到北京，并邀请到来自阿里零售通的俩位技术大咖，为您带来新零售下渠道分销数字化变革、ToB 精准营销算法实践方面的分享。

欢迎大家识别下图中的二维码，免费报名参与活动！

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPiaGXXEoUpib89iaRCq2HSibh0GdkV0ZscLaoaPrAc7iaVjsLSib0iaBQWhU78F9YFoozXltc4oA02foDt8w/640?wx_fmt=jpeg)**