---
title: '蜻蜓FM信息流推荐探索与实践'
company: 蜻蜓FM
tag: 推荐
date: 2021-05-26
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247541942&idx=1&sn=60eeeb4a69f817d2cff29750f8b7fbdb&chksm=fbd796dacca01fcc8ff53c481fb219368b24b48b4e44c068f588b9d1921742ef973663cf23c6&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVHPQeicSKia9smZY5C7Vic7OYNwPicbxAWektV8VQsiaJFgI4jnBqZ4iaChibA/640?wx_fmt=png)

文章作者：季飞 蜻蜓FM 推荐技术负责人

内容来源：作者授权

出品平台：DataFunTalk

**导读：**如今的推荐系统在互联网中随处可见，无论是刷抖音、逛淘宝还是看新闻背后都有强大的推荐系统的支持。音频行业的内容如何分发？如何提高用户发现音频内容的效率？蜻蜓FM作为国内首家互联网音频媒体平台，在音频行业深耕了10年，对此也有一些沉淀和经验想要和大家分享。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVdUialBuDlujlK7faXLBwPL3DxSWouiboOXe6ZicEr9AtXmtUB7cNuBOPQ/640?wx_fmt=jpeg)

主要内容包括：

* 蜻蜓首页场景怎样从人工运营演进到个性化推荐
* 蜻蜓信息流推荐由哪些算法组成，彼此怎么配合
* 整体推荐系统架构及算法模型如何部署到线上
* 蜻蜓信息流推荐场景后续发展的一些思考

**01**

**场景**

**1. 人工推荐时期**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVDebZVLNMICMAlU2icSo0Fwrqo5gL82GbxYN2YevKoBFmLxjibDcNffUA/640?wx_fmt=jpeg)

早期蜻蜓首页流量的分发是以模块形式展示，每个模块可配置横排和竖排的个数。此时只有个性推荐模块的内容由推荐算法生成，其他模块则是由运营人工维护。模块中的内容需要运营定期进行更换，展示内容的更新完全依赖人工，效率显得很低。

为了提高运营人工工作效率，我们引入了策略推荐。

**2. 策略推荐时期**

策略推荐时期运营的工作由之前每天更新模块中的内容，变成了为模块绑定内容库和选择合适的排序策略。内容库中的内容是由配置的分类、属性动态生成和更新，运营为单个模块的配置基本可以做到了一劳永逸。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVhu4QrV4icbSyZFqgxicOGWJZiasvwJAiaGibHib230iaqhnBAJ23b1vEI5v8A/640?wx_fmt=jpeg)

模块之间怎么排序？模块中的内容排序策略怎么选才能收益最大化？成了新的挑战。

**3. 个性推荐时期**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVKbVIpSvmvme9lAy8f5LgQYWh0SMHTs0APFbcOFeTP3xJvotLdnSjoA/640?wx_fmt=jpeg)

通过数据发现个性推荐模块效率高于其他策略推荐的模块，首先尝试了扩大个性推荐模块中内容的数量，由3个变6个。验证了对首页整体效果有提升后，把多个模块合并成一个信息流的个性化推荐的想法应运而生，线上AB实验结果表明信息流的个性化推荐各项指标均高于多个模块的策略推荐。信息流的形态是单排还是双排？经过AB实验，最后选择了效果更优的双排。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVFBE86BOxn04AdfsMSCCV4ic3mK0Gu61mGPB1DwxX6X74NxrO6k2B8cw/640?wx_fmt=jpeg)

个性推荐时期运营对于少数专辑依然会有流量扶持、推广的的述求，在个性化推荐的基础上增加了投放系统。投放系统中还支持通过不同标题、封面对单个投放计划生成多个创意，多个创意之间数据表现好的沉淀下来推广到更多的场景中。运营不再局限于选择内容，更为重要的是重新组织创造了内容，充分发挥出了运营在想象力、创造力上的价值。

**4. 小结**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVSBZLm98SjVJX1gKnGNG83n2ua8e8yTQUD5K2F8B9EHuXvibH50LRgbw/640?wx_fmt=jpeg)

首页场景经历人工推荐、策略推荐、个性推荐三个阶段。策略推荐基本解决了人工效率问题，个性推荐进一步解放人力的同时也带来了数据指标的显著提升。

**02**

**算法**

伴随着首页场景的演进，蜻蜓的推荐算法也在不断的完善和迭代。

**1. 推荐算法流程**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnV6IMYUcKsuF4ic74wZk54po85KbiaibT13wxhOaXnKyJicZPP7Ep4XD5YUA/640?wx_fmt=jpeg)

推荐算法的流程大致如下：内容池中达到推荐标准的内容的有几十万个，召回层从中选出用户可能喜欢的几千个进入粗排层，召回层的覆盖度决定了整体推荐内容的覆盖上限。粗排层从召回结果中挑选出几百个给到精排层，粗排层主要为了减小在线算力减轻精排的压力。精排层选几十个给到重排层，精排层专注于推荐的准确性。最后，重排层对推荐结果进行重新排序给到用户，这一层兼顾准确性的同时还需要保证多样性。

级联结构简单，分工明确。兼顾了覆盖度、性能、准确性和多样性。

**2. 多路召回**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnV2mbw9cS2xMVhvqS5uiaMzrRV7rovn2TeWKMyY11Vl2lFzX5J5NyI0bA/640?wx_fmt=jpeg)

熟悉了推荐的算法的大致流程后，首先，我们来了解一下多路召回。多路召回在蜻蜓主要分为三类：基于内容、协同过滤和Embedding向量召回。基于内容的召回包括热门、属性、上新策略的召回；协同过滤包括User Based和Item Based；Embedding向量召回有Word2vec和Bert。召回环节处理的数据量大，复杂度不能太高，多路召回的设计可以方便加入新的策略或者算法。我们在实践中发现，早期建立完善指标，追踪每路召回的效果，有助优胜劣汰；召回的效果并不是召回算法越复杂越好，不同的业务特点不一样适合的召回也可能不一样，比如蜻蜓当下表现最优的召回来自ItemCF和热门；随着召回的算法越加越多，新的召回需要与现有召回有差异性、互补才会有存在的价值。召回环节还会承载业务及平台建设的使命比如用户和物品的冷启动、业务流量扶持等，召回环节的好坏直接决定了后续环节的上限。

**3. 粗排**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVSMeetHCPMke53Ndrz5KotW8WhZmomFuJickeqkmQlsx95nYVsibUIjwQ/640?wx_fmt=jpeg)

接着是粗排，早期的推进系统中粗排常常用简单的融合策略进行，实践中发现粗排中引入算法是值得的。策略的组合较多测试周期长，双塔模型的应用既解决了多路召回组合的效率问题，又避免了精排的性能问题。

双塔模型扩展性好便于自由添加自定义的网络，User和Item塔解偶，同时点积的计算所需算力小。在蜻蜓为了保障粗排推理数据的实时性，User向量的生成及点积的计算都是实时的。粗排的加入在数据指标指标上也获得了不错的收益，其中信息流UV收听转化率增加了3.54%，人均收听时长增加了5.44%。

**4. 精排**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnV5V3Z8ve4BicmThzicSSrQm3qkmwmkOMRmx3AdV1sNnKOnXWB7MSECiciaQ/640?wx_fmt=jpeg)

然后是精排，精排往往在推荐系统中最受关注，精排直接对准确性负责，相对容易拿到直接的收益。我们在精排的投入相对较大，从中获得的收益也相对颇多。蜻蜓的精排经历了三个阶段：线性模型的逻辑回归和FM、树模型的XGBoost以及神经网络模型的DeepFM。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVNMuLOrOqdlZiaIBwzJIXibOc3Z7PEFp8jpDjpXR6TTHcF3jMAA6Xpu4Q/640?wx_fmt=jpeg)

XGBoost迭代时间最久，其中模型参数的调优、特征挖掘（包括交叉特征和实时特征的引入）、日志数据的准确性优化以及实时排序，这些整体给在线收听数据带来了近35%的提升。XGBoost之后我们尝试过许多模型包括XGBoost+LR，Wide&Deep等均没有取得预期的收益，在DeepFM上的尝试探索则获得了9.3%收听相关指标的提升。DeepFM顺理成章地成为了精排模型的主力，也开启了蜻蜓推荐算法在深度学习道路上的大门。

**5. 重排**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVLichYCYy7BJnBicssw2ruqYZ6YPwftLxtcjpZkEGNzN9UKPlo9gxbX6g/640?wx_fmt=jpeg)

最后是重排，重排跟召回一样承载了很多业务向的目标和期许。这里主要讲一下多样性，提升多样性一方面希望打破推荐系统的信息茧房，另一方面也希望提升用户的长期使用体验。开始是通过打散策略实现，当前主要是MMR和DPP两个算法在尝试迭代，实验中MMR表现优于DPP，这里简单介绍一下。MMR(Maximal Marginal Relevance)最大边际相关性算法，保证相关性的同时提高多样性。通过λ参数来调节多样性和相关性的权重，λ越大相关性越高，λ越小则多样性越高。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVf5lMqlKZknB9J7lD5E9GwW0dJ6XdFDRkGJdPmV1jicdbiagd3kraSzVA/640?wx_fmt=jpeg)

MMR算法中有两个相似度，用户和物品的相似度用精排的打分值来表示，物品之间的相似度基于协同过滤的物品相似度。重排的预期是达到帕累托最优，在其他指标都不降低的情况下，提升多样性指标。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVsaE4R5wOMp0pqkImhaEtt5dicwcQegFH7J4c7HWjB4tvYgZicCRR57UA/640?wx_fmt=jpeg)

最终也达到了预期，人均曝光专辑数量增加8.84%，人均收听二级分类数量提升7.06%。

**03**

**架构**

**1. 整体架构**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVnsbicWzt5fI8fnRFh346JKuTZKKjGfwdBAEbfgaLSNlmR4Nm99PaOsw/640?wx_fmt=jpeg)

推荐系统能高效稳定地运作，离不开优秀的架构支持。蜻蜓的推荐架构是典型的三层架构，即离线、近线、在线三层。离线层负责数据的处理、模型的训练以及数据报表；近线层实时特征处理、召回、粗排；在线层承载了用户请求响应、精排、重排以及投放系统等业务逻辑。

**2. 算法模型部署**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVPt0KmAmVXWGibWPn1jic6sAsHaNZc5rrOtLUU4YBtfsGnpNeiceCrJIHQ/640?wx_fmt=jpeg)

算法模型如何高效地部署到线上？是算法和工程同学共同面临的挑战。开始的时候我们的模型预测服务和推荐API都是用Golang实现，特征的获取处理在推荐API测完成，模型预测服务负责加载模型并对对获取的数据进行预测。在线特征拼接处理使用Golang，离线特征拼接处理使用Scala，跨语言的对齐与校验耗费了开发很多的时间。离线和在线能否公用一套算子进行特征的拼接与处理？为此我们将模型预测服务切换成了Scala的Play框架，基于Scala开发出了一个feature获取处理的库，给Spark和Play共同使用，保证了特征处理逻辑层面的一致性。同时，模型预测服务中增加了对多模型、多版本的支持以及模型的自动更新进一步提高了模型部署的效率。

**04**

**展望**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVwFSCf0yX8ngvnsyRg68lHtTceKIicScxeqflh2trkyvjBvibsnzH4tiaw/640?wx_fmt=jpeg)

首页信息流推荐从0到1建立起来，迭代、优化、完善到现在取得了不错的增长，面向未来还有许多工作需要我们去尝试和探索。内容方面，如何帮助新品内容一步一步变成曝款，产品、研发、运营如何合作建立出完善的内容生态系统；业务方面，信息流支持的业务越来越多包括专辑、直播、听单、节目、广播等，多业务如何更好的融合在一起也是一个挑战；用户方面，新用户的冷启动，沉默用户、潜在流失用户如何激活还有很长的路要走；算法方面，模型的训练如何做到更加实时，多目标的排序是否有望代替单目标排序。这些都将是我们接下来探索的方向。

**今天的分享就到这里，谢谢大家。**

**团队内推：**

蜻蜓 FM 智能运营团队目前正在招聘推荐算法和 Golang 开发，感兴趣的同学请将简历发送至下方邮箱，直接与技术负责人对话~

jifei@qingting.fm

---

在文末分享、点赞、在看，给个3连击呗~

---

**文章作者：**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVm8XuqBu1dib7fGJS87tM10aFtavvEnLibbwuujcBf27oXvtDAI5OXQMQ/640?wx_fmt=png)

**季飞**

蜻蜓FM | 推荐技术负责人

9年推荐、搜索相关工作经验，目前负责蜻蜓FM推荐、搜索等流量分发业务的架构与算法开发工作。

**活动推荐：**

6月1-3日，张宏江携手Bengio等图灵奖得主及200+AI领袖，邀您参加2021北京智源大会啦，30+论坛全覆盖，识别海报二维码即可报名～

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg9JKGkGU7BGZzW2l4MNMnVFR4z42g8icRmSW8Q40mWQ4dvF4z8YgrP77SDLVIeNXdibiaHSAOHzibKbA/640?wx_fmt=png)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近600位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，10万+精准粉丝。

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**