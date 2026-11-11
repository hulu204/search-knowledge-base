---
title: '全民K歌内容挖掘与召回'
company: 腾讯音乐
tag: 召回
date: 2021-04-01
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247537974&idx=1&sn=116f1bcaa683ea35587b0483d9599d4d&chksm=fbd7e75acca06e4c560519cac81cb324be3737b524beca1a249ac114dbfa99109e1fb71361f7&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhcGeLLX52819XRN6vGlX0pEnvuOCkTaUicKUxKDkBaf2NdsUMXQRDaLApoEXaa3Q74HUibv0EGG5Ng/640?wx_fmt=jpeg)

分享嘉宾：timmyqiu 腾讯音乐 应用研究

编辑整理：郭真继

出品平台：DataFunTalk

**导读：**推荐系统一般分为两部分，召回阶段和排序阶段。召回阶段是从全量数据中挑选出用户可能感兴趣的一部分数据，供后面的排序阶段使用。全民K歌作为一个拥有大量用户上传作品的平台，如何挖掘用户上传的内容作为推荐的候选集，也需要精心设计。

今天的介绍会围绕下面四点展开：

* 内容挖掘
* 召回模型
* 召回模型实践
* 总结和展望

**01**

**内容挖掘**

首先和大家分享下全民K歌进行内容挖掘在业务上的必要性。

**1. 内容挖掘--重要性**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJW7PgBLCb2iaPJZKBfcIYZe7mcHjwuDowLB09jOoKbicRTqkI7tEGIOicA/640?wx_fmt=jpeg)跟普通的召回相比，全民K歌作为一个UGC（User Generated Content，也就是用户生成内容，即用户原创内容），存在着两种用户：内容创作者和内容消费者。两者对于平台的诉求是不一样的：内容消费者和其他平台的用户一样，希望看到好的内容，获得好的用户体验。而内容创作者更看重自己发布的作品被更多的人去看到，去喜欢。所以如果单纯从个性化分发的角度去看待问题，推荐的目标是为了满足内容消费者短期的需求，在短期内可能对于消费规模上会有一个增益。但是长期来看，这种方式会导致推荐流量分配越来越集中到少数作者。大量作者因为得不到推荐流量，缺少创作激励，会导致平台创作者的流失。这样对于平台的生态来说是不理的。所以除了个性化分发的视角以外，还有一个从内容生态视角进行考虑的，从内容生态视角触发的一个机制。这个机制就是内容挖掘机制。

**2. 内容挖掘—目标**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJicEar7zQoGPialyrjNRDtwR3pwUHEDTWvfaDfFQJEH46YMy068bzL96g/640?wx_fmt=jpeg)内容挖掘的目标是持续发现优质内容，建立优质流量通路。为了实现这个目标，内容挖掘主要分为两个模块

* 内容准入机制：从内容创造者上传的内容中筛选出优质作品，进入到推荐系统链路
* 分发通路：内容创作者上传内容中筛选出优质作品之后，需要一个稳定的分发通路，保证这些优质资源能够让用户看到。

这两个模块也是经历了一系列的迭代和优化过程，下面将详细介绍迭代过程。

**3. 内容挖掘—迭代**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJHRHau7MZ4Q0qr21BWm7F0zdDeVWicYhtzKibZic4PpcjefzC6qWQO5ViaA/640?wx_fmt=jpeg)在内容准入方面，一开始用的是人工存量挖掘。靠人工对上传的资源进行打分。这样做可以获取到高质量的资源，但是人工操作费时费力，效率很差，时效性也无法获得保证。后面为了提高效率尝试用一些人工标注的特征进行模型预估来识别优质内容，但是这些模型都存在一些问题。现在用的方案是基于视频音频本身的特征来做优质内容的识别，然后用人工的一些辅助审核来帮助实现的内容准入。

在内容分发方面，一开始完全是基于推荐系统的自然分发，然后在此基础上，为了更好的激励内容创作者，增加了冷启动内容保量机制。现在采用的是多级分发，针对不同的反馈效果去给一个作品做多流量的分发机制。

**4. 内容挖掘—方案**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJxOiaMl1Gyfpqlian3g4JxVbiaFxsPO3hvO4u2vQzJPNnMcdAAuhq3lBkw/640?wx_fmt=jpeg)从整体上看，内容挖掘一共有三部分组成：

① 内容准入：内容准入部分是由TME创新团队提供的深度神经网络模型，将一些普通内容和优质内容进行人工标注之后训练模型。对于新发的音频和视频资源，模型会根据他的唱功、视频质量等一系列特征来判断内容好坏。对于音频资源通过模型打分之后直接进入到推荐候选池中，对于音频资源还需要通过人工审核才能入库。通过这样的流程就可以很高效的从每日发布的500w资源中挖掘出可以推荐的资源。

② 分级分发：从用户创作的内容挖掘出优质资源之后，跟着的就是冷启动阶段。根据用户的账号等级，给资源初始曝光量，在曝光量打到设定的值之后根据反馈的数据与资源的平均数据进行对比，如果反馈效果更好的话就增加曝光量，在扩大曝光几次之后，如果资源的反馈仍然比较好，就用双塔模型对资源进行一个保量。

③ 召回：召回模型采用的是双塔模型，不过和传统的双塔模型相比，这里只用到了作品的源信息，没有用到后续的信息。

在完成保量过程之后优秀的作品会转入到流量流转阶段，这个阶段和分级分发类似，每个推荐周期结束后根据一些指标对内容进行评估。比如看点击率、完播率这些，根据这些表现来确定是不是要把它放到更大一级的流量池里面去分发。

**02**

**召回模型**

完成了内容创作者资源的挖掘之后，从每日上传的内容里面可以获取到比较优秀的内容，构建内容池，然后对这个内容池来做个性化召回。

**1. 召回模型—总览**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJ6udRVqA8ofGODCM2QEq3ykqC6Xd7xhDcGjxicATy853DNGW431pcSYg/640?wx_fmt=jpeg)全民K歌的召回主要分为三类：

* 属性召回：用户在看什么内容，说明用户对于这类属性的物品有一个偏好，然后可以根据这些偏好去做点对点的召回，召回一些带有用户偏好属性的内容；
* 模型召回：从用户和item的建模角度，把用户和item建模到同一个向量空间，之后可以按照相关检索去为用户做一个召回；
* 其他召回：除了上述两种召回以外，基于实时热门内容、LBS（基于位置服务）、关系链召回也可以召回少量数据作为补充。

**2. 召回模型—画像属性召回**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJtAddZMBMG5ia94dGgXiaiaKuFXwUqhaIUicxyb7tN2dapARbfRAeFkeviaA/640?wx_fmt=jpeg)基于用户画像的属性召回的原理比较简单：根据全平台的流水（如搜索、播放、点赞、分享、关注和点唱等用户行为），实时计算用户在我们平台的各个维度（如音频标签、视频标签、伴奏、歌手、创作者）的偏好。最终选取用户比较高的偏好维度的一系列属性来为用户去做召回。这种召回对于用户的感知性很强，因为召回结果和用户的实时行为时有强相关的关系。

**3. 召回模型—属性向量化**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJhLib5F0j8PoblfPCayvr2LhxA7TmlNiaEgpKyBmaQn6Z59njfydHA9Uw/640?wx_fmt=jpeg)单纯用点对点的属性召回是存在问题的：这样的召回比较死板，没有考虑到属性之间的相似性。为了解决这个问题，这里引进了属性向量化，训练属性的embedding，根据属性直接的相似关系进行相似扩展。比如用户喜欢的伴奏，可以扩展到相似的伴奏然后寻找作品。用户喜欢某个作者，也可以扩展到风格相似的作者。

**03**

**召回模型实践**

在介绍完召回模型的理论部分之后，下面介绍一下召回模型的实践以及实践中的探索优化

**1. 召回模型实践—模型化召回**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJzPOLKVp50HrDDPaNSIOPf7ic3TrsYt8wY5OlIbrGARyZpYFVz8PYvfQ/640?wx_fmt=jpeg)模型化的召回是相似性的表征建模：通过模型把用户和物品encode到相同维度的向量空间，在最后一层进行相似性交互（cosine，dot等相似性计算方法），线上通过最近邻来召回最相似的内容。

模型化召回典型结构有三种：

* 只有Embedding层：矩阵分解
* 用户单塔+softmax:Youtube-DNN
* 双塔+cosine：DSSM

全民K歌线上采用的是第三种结构，和排序模型相比有几个需要注意的问题：

* 相比排序，召回面临的搜索空间更大。排序只是把少量内容进行打分然后按照分数从高到低排序，但是召回要面临的数据更多，而且数据分布也不相同，所以选择负样本非常重要。
* 线上检索速度有要求，时间太长会影响用户体验，所以无法引入用户的item的交叉特征，导致模型的表达能力比起排序模型偏弱。
* 作为个性化分发的起点，需要引入debias机制，缓解bias循环

**2. 召回模型实践—负样本选取**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJcejQtWzKX7c2R8uY0D3scRv5CjWn37F36oYrmxrkfANNzjwLQ9zHhw/640?wx_fmt=jpeg)在排序和召回模型两块工作中，看到的内容视角是不一样的。在召回阶段，候选的物品是整个全集；而在排序阶段，候选的物品只是全集的子集，因为待排序的物品是召回模型筛选之后的结果。正是视角的不同，所以召回和排序的采样方法不一样。在召回阶段，随机负采样的效果往往优于曝光未点击。

**3. 召回模型实践—增强单塔的表达能力**

用于召回的双塔模型存在一个问题：不能用到用户和item之间的交互特征，前面说过这样导致的结果就是导致表达能力偏弱。所以需要做一些优化来增强单塔的表达能力。具体的做法是利用用户比较稳定的一些行为序列，再加上用户的用户画像的的一些基础信息，根据这些来构建用户的隐藏的表征。然后基于这个表征，去筛选用户的动态，比如播放、点击这种比较稳定的行为动态，这样就能得到一些和当前预测目标更相关的信息。

**4. 召回模型—最终模型**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJUu1qEwx1hIJvq02yxEU0zcLDV65yOcRG8ZzB2e0FJPrnBcIU3oIiaMQ/640?wx_fmt=jpeg)最终经历了热度负采样、Hard-Negative Mining和序列Attention三个优化之后，整体的模型上线之后效果得到了比较不错的提升，说明这些工作是有效的。

**5. 召回模型实践—Debias**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJQETJDgUIm58G91l58HuVYKOrNPrJb4ics0VBeYsWvdKrsYDkfNM2EpQ/640?wx_fmt=jpeg)实践中发现推荐系统中存在着比较明显的bias循环：用户对于一个物品的转化，包括一个曝光的漏斗和一个曝光到转化的漏斗。如果我们只考虑转换这一层的漏斗，就会有夸大高曝光物品的可能，这就会偏离用户的真实偏好。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJ8IvznMoMJg5MuGUn1xShbCd92PvRxmXYqujz0NQRsgAPSJ7SrjctNA/640?wx_fmt=jpeg)为了验证这个猜想，在全民k歌中选取了一个场景来做测试，采用的方案是全局样本补充+IPS加权的方案，包括以下的操作：

* （user,item,rating）从推荐场景扩充到全平台主动性为
* Rating的置信度与Propensity Score关联起来，降低高曝光正样本的权重，增加低曝光正样本的权重
* IPS变换和截断

这个方案上线以后也取得了一定的收益，说明bias的循环是存在的。采取上述方案Debias是成功的。

**04**

**总结和展望**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPia7dUCU2buSDRRGMNOBfGoJQv3j9hPfAWJ5aQOI7ibLGj7vop4ib2w3gtUiaT1HReTGKQexniczhn9tibg/640?wx_fmt=jpeg)**在未来，我们还会在三个方面进一步探索，一是通过更精细的流量分发控制提升优质内容的冷启及进入高展的速度；二是实时画像又统计方式切换到模型方式；三是模型召回也加入多目标的思考。**

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

---

**文章作者：**

**![](https://mmbiz.qpic.cn/mmbiz_png/vrk53t8Tibicp5YGsEVGaHEBa0bTdvqYFZCoUoT8HkmAVp48Um8Hpwu9fibq5eW22bQwXwKbBQAs1TN3XlialJUD8A/640?wx_fmt=png)**

**timmyqiu**

腾讯音乐 | 应用研究

2016年南京大学计算机系硕士毕业，同年加入腾讯SNG数字音乐部，先后负责过QQ音乐的画像和每日30首推荐的算法相关工作。2018年底至今在全民K歌负责UGC作品的推荐算法开发与相关的工程实现。

**社群推荐：**

欢迎加入 **DataFunTalk 推荐算法**交流群，跟同行零距离交流。**识别二维码**，添加小助手微信，**入群。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjWF4KeBlBY77bxkY6RkGYibHjAzoDzvpicWmiamn1unXwekUjw5gfc21jwoGBMEPxsUy3SW0RKicjZYA/640?wx_fmt=jpeg)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近600位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，10万+精准粉丝。

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**