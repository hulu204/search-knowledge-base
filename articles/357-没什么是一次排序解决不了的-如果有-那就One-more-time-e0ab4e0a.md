---
title: '没什么是一次排序解决不了的，如果有，那就One   more time'
company: 阿里淘系
tag: 推荐
date: 2021-04-17
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247539967&idx=2&sn=6c386bbb663d5c15432c4b319e7cab15&chksm=fbd7ee93cca06785618c0a96e69fb9ec45af73e9a1bcfa4cf03e33c2e14b81409702676b878e&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
↑↑↑关注后"星标"**炼丹笔记**

炼丹笔记干货

**作者：九羽**

**Personalized Re-ranking for Recommendation(ResSys'19)**

**问题背景**

![](https://mmbiz.qpic.cn/mmbiz_png/US10Gcd0tQEfcffueY0reDaT8agHibMbkl6VPJicIaSLBOMT46hKst5wjTztibed2dJsrke6B0nRpRPvJXnC2mlSg/640?wx_fmt=png)

    说起排序，对排序的认知还停留在召回阶段召回的item经过粗排过滤，剩下较少的item在精排中打分，按epcm或者其他策略挑选出最终要曝光的item。**重排**是一种考虑到推荐items之间关系和影响的排序模式，常规的推荐系统仅仅考虑<user, item>对的角度，**并不会考虑items间作为一个list进行推荐之后的互相影响**。

![](https://mmbiz.qpic.cn/mmbiz_jpg/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbwmUcPfWm33u8c1jnHkFibicWYxBLRSfzPFbrpHJGzRkjASicE0wMuZTOw/640?wx_fmt=jpeg)

    举个例子，排序模型往往都是point-wise的，一个DNN加丰富的user/item/上下文特征预估点击率，在召回的100个item候选集中排序取出Top10的item进行推荐展示。但是，在实际情况里，这10个item**展示给用户时是会相互影响**的，这样就导致排序模型线下预估与线上实际点击情况之间是有偏差的。

    那么，产生这种情况的原因是什么呢？

    首先是我们在**排序阶段并没有考虑到item之间的影响**，其次**用户对不同场景（或者逻辑）下看到的item list的反馈是不同的**。比如，在信息流场景中，如果展示的20个内容中有同一主题（理财科普），对于**有点击意图**的用户，类似的内容排在一起时，用户**点击颜值较高**或者知名大V的内容的概率会增大；对于**没有点击意图**的用户，展示给用户更加多样性的内容，更适合用户去探索与发现，这时推荐的多样性就变得更重要了。

    Re-rank模型将常规rank模型的输出作为模型输入，强化item之间的关系以及item与用户的关系进行One more time排序。对于不同用户来说，list中item的分布应该具有比较大的差异。

**模型结构**

![](https://mmbiz.qpic.cn/mmbiz_png/US10Gcd0tQEfcffueY0reDaT8agHibMbkl6VPJicIaSLBOMT46hKst5wjTztibed2dJsrke6B0nRpRPvJXnC2mlSg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbhODZvWtnrsuWpqUwXH7ZaibTcqbF37qLo0cRY1eBBU1v21VxK6eLu8g/640?wx_fmt=png)

PRM的模型结构，是一个比较传统的multi-head结构，输入Initial List是一个精排模型输出的推荐集合，然后依次经过输入层, 编码层和输出层三部分后，输出的Re-ranked List是重排序。

![](https://mmbiz.qpic.cn/mmbiz_png/siayVELeBkzWBXV8e57JJ4OyQuuMXTfadZCia0bN2sFBfdbTRlFx0S97kyKKjic5v6eaZ8cY4WQt0UEu4dkyowHYg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/rl6daM2XiabyLSr7nSTyAzcoZqPAsfe5tOOrXX0aciaVAfibHeQk5NOfQTdESRsezCwstPF02LeE4RHaH6NBEB9Rw/640?wx_fmt=png)

输入层Input Layer

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbHaj8kVJ30ApvFZfh321yMYdH802ticy9viaHszgDiahxKQia1VqRAlVK5A/640?wx_fmt=png)

    输入层由**原始特征、个性化特征、位置特征**三部分组成。

    其中，![](https://mmbiz.qpic.cn/mmbiz_svg/AhLk989Zrl2fbtqV8oeRC00HqEORbdaW5ABiaGbibChZOTqJIloADKsf78fNgdrIZBs7CrffvsBX9ANesujOiawrIt4nicaZiaLuP/640?wx_fmt=svg)是item在精排模型时的原始特征；

    ![](https://mmbiz.qpic.cn/mmbiz_svg/AhLk989Zrl2fbtqV8oeRC00HqEORbdaWp6ylLBMAadEibX12Bzj3z6ecDwaSdHdUXvRCYJjc2AhbySpGukksTvOQIAiblc4Iwc/640?wx_fmt=svg)是用户与item的一个交叉特征，通过预训练Pre-train得到的个性化矩阵；

    ![](https://mmbiz.qpic.cn/mmbiz_svg/AhLk989Zrl2fbtqV8oeRC00HqEORbdaW1hfl4wrklPCPENoh4vIlGwNMUx5rL8z1sszQU8XLf188FcRtd10eUOu3Az8PSvxV/640?wx_fmt=svg)是一个Position embedding位置向量，主要是利用精排模型产出的排名作为位置信息；

    上述的三组embedding是输入层的组成部分。

![](https://mmbiz.qpic.cn/mmbiz_png/siayVELeBkzWBXV8e57JJ4OyQuuMXTfadZCia0bN2sFBfdbTRlFx0S97kyKKjic5v6eaZ8cY4WQt0UEu4dkyowHYg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/rl6daM2XiabyLSr7nSTyAzcoZqPAsfe5tOOrXX0aciaVAfibHeQk5NOfQTdESRsezCwstPF02LeE4RHaH6NBEB9Rw/640?wx_fmt=png)

编码层Encoding Layer

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbibicAIewIP73eD4mRKdiaAdeQkGzeSOFZ5V6kYvg8icyicBREZVagJDbjGw/640?wx_fmt=png)

    编码层目标在于整合对列表中物品的相互影响，以及用户行为和列表中物品的相互影响。这里利用Transformer中self-attention结构来实现任意两个Item的交叉，从而获得Item互相间的影响。

    在Attention中， **Q**uery，**K**ey和**V**alue都是同一个输入的embedding矩阵，然后经过Multi-Head Attention。公式如下：

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbm4ib3qUTpEyr3AVSeCkdSbgvonm0yr75n4xa7gsUT3WMIa2TI5Ol3kg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEb7FItagmkscZEhx7D0qgdZ9AZk5Vn3RJE8QmenmiaKacvVAlY6Db32yw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEb4JNhJDvFZKwVWKAIqBRytN8iatJRlM6bFoJMwgXs2ocq0hCUIjibKcQA/640?wx_fmt=png)

    经过FFN增强模型和输入向量不同维度之间的交互，将多个Attention进行stack，组合成更复杂和更高维的交互信息。

![](https://mmbiz.qpic.cn/mmbiz_png/siayVELeBkzWBXV8e57JJ4OyQuuMXTfadZCia0bN2sFBfdbTRlFx0S97kyKKjic5v6eaZ8cY4WQt0UEu4dkyowHYg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/rl6daM2XiabyLSr7nSTyAzcoZqPAsfe5tOOrXX0aciaVAfibHeQk5NOfQTdESRsezCwstPF02LeE4RHaH6NBEB9Rw/640?wx_fmt=png)

输出层Output Layer

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEb9GEZ4JHeqfuRn9pcx6VLOJpqx8ajCMdUnzbJoUO2wnfuHk3GPW0RDQ/640?wx_fmt=png)

    经过FFN增强模型和输入向量不同维度之间的交互，将多个Attention进行stack，组合成更复杂和更高维的交互信息。

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEb3MY4K2vK8M61K1axdhVdJfZsHpJQG8iaXzm5Uen2vbw0yxcQfHxY6Iw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbozRL3b8qMZC4HCibM4hT22h0VLnXtFsH7HssKAWgWh2gPXpnWopEGWw/640?wx_fmt=png)

    最后，以点击预估作为目标，通过Softmax和Cross-entropy进行训练后通过Score排序依次展示给用户。

**个性化预训练:Pre-train**

![](https://mmbiz.qpic.cn/mmbiz_png/US10Gcd0tQEfcffueY0reDaT8agHibMbkl6VPJicIaSLBOMT46hKst5wjTztibed2dJsrke6B0nRpRPvJXnC2mlSg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEb7jnM5EGB3Oo6VTw4AYeEf8R8fOYxPibFA12MFVibBVPcM6OqZphS9veA/640?wx_fmt=png)

    ![](https://mmbiz.qpic.cn/mmbiz_svg/AhLk989Zrl2fbtqV8oeRC00HqEORbdaWp6ylLBMAadEibX12Bzj3z6ecDwaSdHdUXvRCYJjc2AhbySpGukksTvOQIAiblc4Iwc/640?wx_fmt=svg)是用户与item的交叉特征，通过预训练Pre-train得到的个性化矩阵。因此Pre-train模块将CTR作为目标，利用网络的隐层向量实现个性化。

   其中![](https://mmbiz.qpic.cn/mmbiz_svg/AhLk989Zrl2fbtqV8oeRC00HqEORbdaWpLOv5PsVHygRrYRcynBZRlMGDR6Q3AJicgkyDGQwQ1VdA4n46rqTuux91laaicSeA0/640?wx_fmt=svg)表示用户的历史行为信息，Item表示物品信息，User表示用户信息。可以看出个性化向量的预训练网络就是一个CTR预估网络，Sigmoid输出的是用户的点击概率。

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbrkGtmjbicWwIqBjYY6RD6DgnglTTrpJN1nepia9d0OQ2bAoSq9JISbPQ/640?wx_fmt=png)

    其中D是展示给用户的items集合，y是用户是否点击。

**实验效果**

![](https://mmbiz.qpic.cn/mmbiz_png/US10Gcd0tQEfcffueY0reDaT8agHibMbkl6VPJicIaSLBOMT46hKst5wjTztibed2dJsrke6B0nRpRPvJXnC2mlSg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbQgQX6xxJ3xqrumhWORGXJThRAVWDTDVv6nqzaibPFibYCiagA6GlkIC3g/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbhThjnr4oA4RYEmsdn4LYLGbbpslXLAEnZefwkic1FrBiaxGywh7zjCLQ/640?wx_fmt=png)  

**拓展总结**

![](https://mmbiz.qpic.cn/mmbiz_png/US10Gcd0tQEfcffueY0reDaT8agHibMbkl6VPJicIaSLBOMT46hKst5wjTztibed2dJsrke6B0nRpRPvJXnC2mlSg/640?wx_fmt=png)

 我们知道，最常见的考虑时序性的模型是RNN和Transformer，所以经常把这两类模型用在重排模块，这是很自然的事情。一般的做法是：排序Top结果的物品有序，作为RNN或者Transformer的输入，RNN或者Transformer明显可以考虑在特征级别，融合当前物品上下文，也就是排序列表中其它物品，的特征，来从列表整体评估效果。RNN或者Transformer每个输入对应位置经过特征融合，再次输出预测得分，按照新预测的得分重新对物品排序，就完成了融合上下文信息，进行重新排序的目的。

    除了本篇**Re-Rank**文章之外，炼丹笔记还分享了《[**Revisit Recommender System in the Permutation Prospective**](http://mp.weixin.qq.com/s?__biz=Mzg4MzU1NjQ2Mw==&mid=2247498279&idx=1&sn=f73e72e5d54865e8e15d92baa3d6de4e&chksm=cf471327f8309a31cbd1d8cc8fd72c2f6886a9963cd024c22ddb16f253f1a56b3c7c8f2ae353&scene=21#wechat_redirect)》一文，论文提出了两阶段的重排序框架PRS(Permutation Retrieve System)，分别是PMatch阶段和PRank阶段，![](https://mmbiz.qpic.cn/mmbiz_jpg/CuZzSF5jYZw6sS0k81DnictCEiaLAMlDEbEMic8GZibAKCy5KqBpq9xtd8jEsPYhpIhoULt5XvIxWSiaSqI9hdgTRZQ/640?wx_fmt=jpeg)

    **PMatch**一句话总结就是，把上百个item的排列都给list-wise模型预估排列分不现实，PMatch负责挑选出候选的排列。

    **PRank**就比较简单了，先离线训练一个模型，该模型输入是一个长度为n的序列 (x1, x2, ..., xn)，然后输入到Bi-LSTM里，就会得到n个隐向量，每个隐向量concat用户特征和序列中每个item的原始特征，过mlp预测点击率即可。

**参考文献**

![](https://mmbiz.qpic.cn/mmbiz_png/US10Gcd0tQEfcffueY0reDaT8agHibMbkl6VPJicIaSLBOMT46hKst5wjTztibed2dJsrke6B0nRpRPvJXnC2mlSg/640?wx_fmt=png)

* Personalized Re-ranking for Recommendation
* https://zhuanlan.zhihu.com/p/100019681
* https://www.zhihu.com/people/yuconan
* https://zhuanlan.zhihu.com/p/358568019
* [排序rank后重排re-rank](http://mp.weixin.qq.com/s?__biz=Mzg4MzU1NjQ2Mw==&mid=2247498279&idx=1&sn=f73e72e5d54865e8e15d92baa3d6de4e&chksm=cf471327f8309a31cbd1d8cc8fd72c2f6886a9963cd024c22ddb16f253f1a56b3c7c8f2ae353&scene=21#wechat_redirect)

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

---

**社群推荐：**

欢迎加入 **DataFunTalk 搜索推荐**交流群，跟同行零距离交流。**识别二维码**，添加小助手微信，**入群。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjWF4KeBlBY77bxkY6RkGYibHjAzoDzvpicWmiamn1unXwekUjw5gfc21jwoGBMEPxsUy3SW0RKicjZYA/640?wx_fmt=jpeg)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近600位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，10万+精准粉丝。

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**