---
title: '阿里妈妈：电商预估模型的发展与挑战'
company: 阿里妈妈
tag: 精排&CXR预估
date: 2019-05-20
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247490293&idx=1&sn=4dcd1cf5f945c03c98ed3401afb7983d&chksm=fbd4a899cca3218f328a661da553b470e018eeeef2ca3bf2696140ef045f1805f89b8c3a596a&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX638p7REfibBdE24XMpW8GVBpq53fX8HgS24SBeYqLMC5y75vlCoCz7DQ/640?wx_fmt=png)

分享嘉宾：周国睿 阿里妈妈 算法专家

编辑整理：鞠芳

内容来源：AI 科学前沿大会

出品社区：DataFun

注：欢迎转载，转载请注明出处

**本次分享内容提纲：**

* 电商数据个性化预估的特性
* 阿里妈妈模型迭代路径
* Where to Go

一、**电商数据个性化预估的特性**

首先介绍一些基础的背景知识，阿里的展示广告按展示元素主要分为 Banner 广告和单品广告两种，所有广告内容由 id 、图、文三部分组成。因为展示广告面向的是用户的非搜索行为，用户不会向平台输入一个明确的意图，需要我们推测用户的意向。广告的个性化预估问题主要是，根据用户的历史数据，来预估其对于某个广告商品点击、收藏、购买的可能性。与 facebook 等社交媒体网站通过上传照片、点赞等行为来推荐多种元素广告相比，电商场景中有一个显著特点，预估的 candidate 节点内容与用户的历史行为节点内容是同质化的，都是商品。

可以通过三个主要维度来描述：

* 显式内容：imag , text , reviews 等内容信息
* 账户体系描述：item , shop , cate 等 id 信息
* 最终反馈：buy , fav , cat 等行为信息

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6PcnsUzI4stfeXKEPibibRGIJ7VHNOWFBjXWbk8IgRNe95Hs9e6kicb06w/640?wx_fmt=png)

**二、**阿里妈妈模型迭代路径****

随着历史的推演，从2012年起，阿里妈妈的预估模型也在不断的迭代和创新，演进路线如图所示：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6jxLRZyuWS5WOjJoia6f9F0kf9KyGicvkZ2BQy3do3OLjYWXbRd7K0MibA/640?wx_fmt=png)

**MLR**

大规模特征和逻辑回归模型的组合是点击率预估模型的传统经典方法。通过大规模的 id 和特征能够获得更高分辨率的样本描述。这种方法下，模型结构相对固定，优化方法上讲也更注重系统效率。从效果上看工作重心主要在大量的特征工程，通过人工经验对特征进行组合、运算，解决 LR 无法表达非线性关系的问题。但是这样的迭代模式整体受到人工能力制约，不够智能。

MLR ( 分片线性学习 ) 算法是解决此类问题的一个非线性算法，其主要思想是将在一个平面线性不可分的数据，分为多片，投影到不同的高维平面，实现线性可分。同类的解决这类问题的常用方法还有 GBDT+LR 的组合。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6l0iaeecp44tMqXDsyBMJEicvhxUf7S1ASkstROvMiayjJCaxq1Js4CRHQ/640?wx_fmt=png)

**第一代深度 CTR 模型**

随着硬件的发展，算力、数据量的进一步提升，深度学习在诸多领域如图像、NLP 、语音都取得了突破性的进展。阿里妈妈在经历了从2015年的一系列探索后，在2016年尝试了第一代深度学习算法，网络结构相对简单，主要就是 embedding 层+MLP，效果却相对 MLR 得到了显著提升。分析原因主要是传统算法因为算了和数据问题，模型的 capacity 有限，非常依赖人的先验知识在有限的 capacity 下设计高效的模型。而算力和数据利用量提升后，模型的 capacity 通过深度学习出现了量级的增加，拟合能力得到了显著的提升。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6waSvSugsOAeIk6EFPuOkpxmA5rWpE1ovuuVAF9Tar090Otia2W7MB2w/640?wx_fmt=png)

阿里妈妈认为和传统的研发模型相比，深度学习具有通用的优化器，使得模型设计和优化问题解耦，模型设计组件化，从而能够更快的设计验证更加复杂的模型。

但是，复杂并不是终点，算力和数据都存在上限，采用深度学习要走的更远，模型结构和数据分布的匹配将是研究的方向，例如 CNN 对于图像数据，RNNs 对于语音和文本的数据都有很好的适应性。那么适合电商数据的模型结构是什么？这一问题，成为深度兴趣网络诞生的源头。

**深度兴趣网络 ( DIN )**

电商用户的兴趣存在多样性的特性，即一个消费者会同时有多种多样的兴趣，在喜欢一件大衣的同时，也可能喜欢一个杯子，又同时是电子产品的爱好者。在第一代深度学习网络中，我们将用户的历史行为 encode 成为一个固定的向量，实际上，直接通过一个固定向量去表示这种多种多样的兴趣爱好是十分困难的。我们可以通过扩大这个向量的维度来提升它的表达能力，但是这样会带来计算复杂度增加和过拟合等问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX68VnFibSsQ7UNvoAvianztCcFE6sNKbib9xyVDcxSU1kic5H7Iia3qTKQgIQ/640?wx_fmt=png)

这时我们注意到，用户一系列的历史行为和一个目标商品相关的通常只有其中的几个。采取类似 attention 的机制 ( Activation Unit ) ，选取和某一商品相关的用户历史行为，就可以动态的使用一个定长的向量来表征用户多样的兴趣，这是 DIN 模型的核心内容。而前文提到的用户行为和商品的同质化，使得这种模型的效果更好。

具体的网络结构如下图，其中 Activation Unit 设计的比较简单，主要是由于工业界时延等要求的限制：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6LXnBYrRsPQhLjUkq0EGWU8xJEYEyevnUMssYT8g45hibWnniaTicmYh3Q/640?wx_fmt=png)

DIN 模型使得阿里妈妈广告的 CTR ( 点击率 ) 上升了10%，CVR ( 转化率 ) 提升了3.3%，GPM ( 千次展现用户成交金额 ) 提高了12.6%。

**CrossMedia 网络**

在网络结构调整告一段落后，阿里妈妈致力于将图文数据作为特征增加到模型中去。主要原因是，图文是用户直接接收的信号。并且图问信息和 ID 类特征不同，ID 类特征的所有信息都源于样本里和 label 共现信息的反馈，而图文本身具有物理含义，所以其具有更好的泛化性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6ktWGpPE6THdq9V74GWsNGfOtOr1c6eUeYFffhmqrgoSezIcsVPqJ8w/640?wx_fmt=png)

在这一过程中的挑战主要在于图片的数据过大。一个用户如果有一千多个历史行为，和商品组合后有100亿样本，涉及图片数据会达到上百T，对于存储和 I/O 都会造成很大的压力。

最终的解决方案是，将图片数据存储在远端 server，并在 server 上采用神经网络提取图片为一个低维的向量，在样本中将图片存储为一个 id，计算时通信获取压缩后的图片向量，实现效果和效率之间的一个 tradeoff 。

**Deep Interest Evolution**

在 DIN 研究的时候，阿里妈妈发现 RNNs 的时序网络，不能在电商预估场景中得到良好的表现。原因是由于用户的历史行为可以被看做是很多个兴趣的很多采样点混合在一起的综合序列，其中存在着很多随机跳转。例如，形式化某个用户的一段历史行为序列：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6uZG1YL5phDwbfAm7mqbmZibjJ02tL5BVEaNLeTOPFTtep4RemPB9VtA/640?wx_fmt=png)

其中，![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6GjZRpNQcVBNiaWMotNA1VbzDHBBTiaTFLKzaJP2DgibuAf91HqcEYRLqg/640?wx_fmt=png) 代表兴趣空间内的两种不同兴趣。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6NZA3lto0uf05FghaV1uP6ofsOFzUNpwZ8vSW9weveE6coiaVJwBJoUA/640?wx_fmt=png)

同时现有的模型直接将用户的历史行为的 embedding 当做兴趣缺乏抽象、概括能力。其实，行为只是抽象兴趣的具体体现，用户的每一次行为的结果只是去兴趣下的一种选择，每一次点击的商品可能只是部分满足了用户的兴趣，并不是这个商品的所有属性都代表了用户的兴趣。而且多种兴趣存在不同的演化路径。阿里妈妈通过兴趣提取层和兴趣演化层对模型进行了优化。

* 兴趣提取层

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6rlOtU6yBTfnZEo2fibxHQiaob0vx2PRdqqEucWJq5DszbtOsZIYhjsog/640?wx_fmt=png)

该层的构想，目的是挖掘出行为背后用户抽象兴趣的表达。

通过 Embedding 的学习得到用户行为更多语义信息后，使用 GRU 隐层状态表达抽象兴趣；使用有监督的点击序列 pattern 实现辅助损失 ( auxiliary loss ) ，而非 ctr 最后点击信号——通过 t 时刻用户兴趣的表达 h(t) 和 t+1 时刻用户的点击动作 e(t+1) 和非点击负样本 e(t+1)’的动作实现一个有监督的 loss，使得 h(t) 的隐层不仅能够表达对最终 output 的影响，也能预测用户下一个行为动作，能更好的表达用户兴趣，同时有效解决长序列梯度传播问题。

* 兴趣演化层

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6EtfgZrIc8oyF6NiaK1eXyJgAShpXicExdBU7ia8WYgm3MYGKibHxHdSSbQ/640?wx_fmt=png)

兴趣不光是行为的抽象，具体到某个兴趣，还会随着时间逐渐演化。兴趣演化对行为的影响是用户可能在一段时间内对各种书籍感兴趣，而在另一段时间内需要衣服。虽然兴趣可能相互影响，但每个兴趣都有自己的发展过程，例如书籍和衣服的发展过程几乎是各自独立的。我们只关心与目标产品相关的兴趣演进过程即可。

在兴趣提取层上，阿里妈妈增加了 Attention Unit GRU，与传统 GRU 不同的地方在于在 update 门和 reset 门上乘上了一个 attention score 。首先，通过用户的历史行为计算出一个 attention 值，由此体现和未来预估目标的一个相关性权重，通过相乘，使得和目标不相关的行为，不会对 GRU 结果产生影响，相关行为才会使 GRU 结果发生迁移。

由此，从繁杂的综合序列中抽取出相关兴趣，与广告越相关的行为更新隐状态向量越多，精确捕捉当前广告相关兴趣。

* 模型效果

公开数据集效果

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6dd9TjAwibjhq5SBFd8f760sojEJNlPDF3N8lGsrWslSibrJc27gHqOFA/640?wx_fmt=png)

线下数据验证效果

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6ibSKIjI6kmOQEF21Q3qlKN7FNC40ic8ujfjib9JfWhgLuTLV0ctCcfAUw/640?wx_fmt=png)

线上 A/B test 测试效果

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6Z0Be30yu8fyUPjy0KEpzDXXFqIGmDXGDbHx7el2HumpI4JM2hhjxNg/640?wx_fmt=png)

**Rocket Launching**

随着模型复杂度的上升，在线预测的时延和 tps 就越来越难以满足。对于离线的模型，为了追求模型表现，可以足够复杂；但对于在线预测模型，需要控制模型复杂度，实现效果和性能的平衡。

为此，阿里妈妈提出了一个类似的模型蒸馏的 teacher-student 方案，压缩模型的计算复杂度。在离线的时候训练一个复杂的 teacher 模型，同时训练一个很简单的 student 模型，通过 teacher 对目标的 soft 预测结果来监督 student，同时也用真实的 label 来监督 student 。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6Xvutm9pAYyoymJViaSzkTDbApbEcmCkD8mZHlodVJMzaap9qQ00IV8g/640?wx_fmt=png)

与一般模型蒸馏不同的三个点是：

* 协同训练，teacher 和 student 一起进行训练。通过细到 batch 的数据，使 student 学习的不再是一个最优的 teacher 解，而是 teacher 模型的学习轨迹；
* 参数共享，模型一般分为表达层和决策层，student 通过参数共享能够获取 teacher 表达层训练的成果；
* 梯度 block，通过特定损失项，防止 teacher 向 student 学习。

**三、**Where to Go****

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiavjiceGFTa1rTmPVAzzWpX6vqf0BFYGrqENBSz7HKNoBfaE3H2EicY7qzbjTAdbrhYQ2fxtV6maRkA/640?wx_fmt=png)

回顾阿里妈妈模型的演化路径，从线性到非线性，再到深度学习的不断演化，模型的结构一直在变化，但是 Representation 的技术上一直没有明显的进展，展望未来的发展方向主要有两点：

1. Representation 的研究，目前一些预训练和类似 NLP 的方案在我们的场景没有良好的效果。推测可能是因为电商数据商品之间并没有如 NLP 一样词与词之间从属，双关，同义等关系，然而商品之间的结构关系已经被天然的账户体系，店铺、类目、品牌等特征很好的表达。但是我们依然会继续推进，后面会尝试 Disentangled Representation，学习电商领域的抽象表达，提取出有效的 Concept，更好的解释我们的 representation 每一维的语义信息是什么；

2. 黑盒的模型让平台离用户/商家的距离越来越远，平台自身也不能完整的理解模型的机理。希望能够构建更白盒的模型，知晓影响用户决策的 Concept，并依此联系用户和商品。产品上我们可以透传出推荐的理由和用户做更多的交互，商业营销上可以结合商家自己的卖点是什么，可以让商家更精准的实现营销诉求。

**作者介绍：**

周国睿，阿里巴巴算法专家。北京邮电大学硕士。研究领域包括大规模机器学习、自然语言处理、计算广告、推荐系统等。现负责定向广告预估方向模型算法研发，同时是阿里巴巴自研深度学习框架 XDL 核心开发者。研究成果发表于 KDD / AAAI / CIKM 等会议，其研究工作均落地于实际系统。

**——END——**

**文章推荐：**

[视频：OCPC 在凤凰新媒体的实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247490269&idx=1&sn=451a6f47209cb1fc71c1510280b1166b&chksm=fbd4a8b1cca321a7224fba10ee1505f8060e8327211fd77f506eb52b63d146c5028c76fffba7&scene=21#wechat_redirect)

[定向广告新一代点击率预估主模型——深度兴趣演化网络](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247487620&idx=1&sn=b3162fec93608788430f7e52236d998e&chksm=fbd4a2e8cca32bfea69c4e418e38d0c8709d2fe3395f74f73aaf48815ec8a41fc0d130ae4a1e&scene=21#wechat_redirect)

**加入 DataFun 社群：**

请关注社区公众号，后台回复【**JY**】

**关于 DataFun：**

DataFun 定位于最实用的数据智能平台，主要形式为线下的深度沙龙、线上的内容整理。希望将工业界专家在各自场景下的实践经验，通过 DataFun 的平台传播和扩散，对即将或已经开始相关尝试的同学有启发和借鉴。

DataFun 的愿景是：为大数据、人工智能从业者和爱好者打造一个分享、交流、学习、成长的平台，让数据科学领域的知识和经验更好的传播和落地产生价值。

DataFun 成立至今，已经成功在全国范围内举办数十场线下技术沙龙，有超过三百位的业内专家参与分享，聚集了数万大数据、算法相关领域从业者。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhicE4hS5liayK0vWlwTanNgy003rMCMPvRlktwUjR2m8icG0MbH1ByNF7RuLdibwXKsA424lHOvaIHWw/640?wx_fmt=png)

**看官点下「好看」再走呗！👇**