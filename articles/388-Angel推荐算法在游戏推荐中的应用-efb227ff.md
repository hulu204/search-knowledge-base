---
title: 'Angel推荐算法在游戏推荐中的应用'
company: 腾讯
tag: 推荐
date: 2020-12-24
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247517980&idx=2&sn=bc82b69449a005f76284a475c46a7ec2&chksm=fbd73570cca0bc66302d7bdb893e4c391197004baf376a0fa3e52ad68052ba7bc66ee0e0a723&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm29QzxAljUoGZRkqTlIsC8eCBOcR9N5Xkx2YMuyYybfktILtialUfKX8Zjz6zeSy9s1gEUg7063Q2Q/640?wx_fmt=png)

文章作者：王培军 腾讯 高级工程师

整理编辑：李沛欣

出品平台：DataFunTalk、AI启蒙者

**导读：**Angel是腾讯自研的分布式高性能的机器学习平台，支持机器学习、深度学习、图计算以及联邦学习等场景。Angel的深度学习平台已应用在腾讯的很多个场景中。本次分享为大家介绍Angel推荐算法在游戏推荐中的应用。主要内容包括：游戏平台上的游戏推荐、Tesla平台上的推荐算法、经典算法的线性特点、DeepFM算法的非线性特点、DeepFM应用过程。

# **01**

# **游戏平台上的游戏推荐**

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiaFMXHN7f1H2U65RTSltGjfRHKdJBhxxNNMeLmIXiaibcXnRrtECHXJlXw/640?wx_fmt=png)

这张图看到的是Steam平台上的一个游戏推荐的应用。Steam平台主要是使用标签的推荐方法，它的标签主要是基于用户选择去收集的信息。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeia7wUu5YPDZ3k1l4fepz89jYVlMnrbk0bPqiaSIAgCWWrH5Vmn8Nsj42g/640?wx_fmt=png)

Steam平台的特点在于游戏的内容比较多，深度也比较深一些。

如果item比较多，而且使用用户比较多，那就可以通过用户来选择一些标签，能够抽象出其实本来是需要协同过滤ALS的算法计算的因变量的特征向量。

也就是说，Steam是用人工选择的方式，用集体智慧的方式来抽象出特征向量。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiaT1y5C5TNa6bpPBDe0swnIWWd3ewndNVZTic6uVibww0Okq94icoaAoBcQ/640?wx_fmt=png)

这是Wegame平台上的一个活动。它的推荐算法并没有使用人工抽取标签的方式，而使用了CF算法，以及在用户行为数据的基础上使用Deep FM算法。

# **02**

# **Tesla平台上的推荐算法**

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiaSOOjfRXyrvk2XuibULxONicYntvibU53JI599PWFiaDQrPibRvPxq0Jf7Kw/640?wx_fmt=png)

这个是特斯拉平台上的推荐算法。如果你要在外网试用，可以到下面的网址进行试用：

https://cloud.tencent.com

在试用的过程中，根据wiki文档生成相关的模型，定义相关的参数，就可以使用了。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiawGico7WQNicj66FicliaXSBDicbGCxwfPWMpIo568Q0fPA6e1OI0oW2M9Lw/640?wx_fmt=png)

特斯拉平台上也可以使用一些传统的算法，就像CF-ALS算法，可以把Rank、Lambda、Alpha这几个重要的参数，通过一个迭代的方式去选择合适的超参数，就可以使用了。

# **03**

# **经典算法的线性特征**

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiaKbCLcEsl9mEzqt1AueZ2mnyDn8eTkHEg35x89jDIbLoJFibPmUqEqlA/640?wx_fmt=png)

如果是基于内容的标签推荐，不用集体智慧的抽象，在很多情况下就是一个主观的先行判断。

另一种是协同过滤——或基于物品，或基于用户，或者是联合的协同过滤，会存在稀疏矩阵和长尾推荐的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiao2xbicPNoNwRTIcH9KE4WM9bibOvV2vRTVutQo9kibyS6QiaBsiaNCzEOEQ/640?wx_fmt=png)

此时会出现一个问题：这是基于物品点击率比较高的协同过滤，但游戏大部分推荐的并不是都是热门物品。如果我们想在经典算法的基础上对一些点击比较少的物品进行推荐，也就是对这些长尾的物品进行推荐，如何去实现呢？

此时可以先做一个聚类，再应用一个协同过滤的算法。如果是经典的算法，有一个很大的核心的问题：怎么去结合用户画像，还有物品画像，参与到DeepFM的建立？

# **04**

# **DeepFM的非线性特征**

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiaicoiaXTibwbTBtkmUaLZZtqX7wHomTT8icVhYuCCYicOaX2lNibWoYFRGsYA/640?wx_fmt=png)

其实CF算法中输入的是Item Id和 User ID，但是Deep FM在输入UserID和Item Id之外，还可以输入用户或者物品特征。另外也可以对特征进行一个二次交叉：二次标签的特征组合，在本质上还是比较依赖于原来所采集的特征，而且特征组合也仅仅是二次的一个特征表达。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeia9VfOib5dmSc5hXgkhpicCYzibIvIxMZRtElwczFv4V0icP4eHlGRrXic9iaw/640?wx_fmt=png)

DeepFM的各种非线性特征，其实比较类似于CNN算法里面，在识别分类过程中所作的权重分解。上图是在CNN的过程中，做的一个热力图。其中CNN是对图像做了一个分类。这个分类依据，是Class之前所做的权重分布，从Deep FM的一部分的模型研发而来的一部分。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiaMCL44q0kE7GDmRHSrM3vrk7ajoh2hicDb9SP1AhgFATia2BHTDnB5tQA/640?wx_fmt=png)

Deep FM模型的random部分有很多类别特征的。类别特征是用人工选择出来的categorical Features。而Deep FM在自动归类分群的过程中，有一个自动embedding 离散维度的推荐过程。一般我们可以根据误差的自动调整，来调整这个特征的维度组合。类似于推荐过程中自动聚类分群的过程，这就解决了传统算法的问题。如果只输入一个User ID或者是Item ID，就无法使用用户画像和物品画像，进行信息的分群，这样Deep FM就成为了一个可以根据误差进行自动调整，自动聚类分群的推荐工具。

# **05**

# **DeepFM应用过程**

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiasDwlZo6q8WHug5HiaC4ERvZwJQeKFxicszlMGKNLUjVVDVp4QUkbsYJg/640?wx_fmt=png)

在进行数据运营过程中，一般会使用到的工具是Vector assembler，将输入的字段组合成一个Vector，再对Vector进行标准化。

另一种情形则是在Deep FM的过程中进行编码，如果有单列的类别值，如何进行、转换成一个稀疏矩阵？一般来说可以使用手工编码，但这个方式比较低效。这时可以使用Feature Hasher，可以自动把几列类别值转换成一个技术矩阵，把稀疏矩阵和由连续值组成的vector和Hash feature组成vector，合成一个Vector，再把这个Vector作为一个Deep FM的输入，就可以比较方便进行数据计算了。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeia7QkcG8TMibJf7tJSvz6HCL18SLJlyMIUvibWl6P0EvczRibvPHJOFzbTw/640?wx_fmt=png)

这里面有几个经验：

* Validation AUC与点击率的对应关系：就是说在算法的训练的过程中，会输出一个Validation AUC，这个AUC很大情况下会和点击率有对应关系。在算法的模型训练过程中AUC比较低的话，点击率可能比较高，但是如果AUC比较高，其点击率一般情况下也比较高。
* 特定场景下的target 数据产生的模型只能应用到特定场景下的点击率评估：你可能会需要使用到3个采集位置。这三个位置前面的Target数据就是用户在item下面点击数据，如果你运用3个模型，每一个模型应用在3个特定位置下，应该会得到一个更好的效果，而尽量不要把3个位置下的Target的数据合并为一个Target数据。因为这和Deep FM的特征的抽象能力相关，也就是说Deep FM有比较强的特征抽取能力，Target数据会反向传递到特征的采集过程中，会比较依赖于这个特征的场景。
* Deep FM 的参数调整比较简单，因为一旦收敛，AUC 的提升跟训练数据集的大小最密且：因为增加更多的训练数据，AUC提升会比较明显一点。
* 数据精排需要过滤已拥有，已玩过,并且根据业务需要重排数据，比如重点展示新游，热销等。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm12TmlcE7NZZPeGD1RHHBeiavnAY5nvyNuZdHMHE3G0lXVQYbsXT9QM0fDuOjM1cdwDfVmxwF6tJaA/640?wx_fmt=png)

* FM 需要输入 user\_id 作为训练数据：Deep FM是从FM演化过来的，FM的训练和使用的过程中，一般会是要用User Id做一个输入，真正FM的User ID会在大数据情况下形成一个大的标签。
* FM 的user\_id 在大数据环境下会形成很大的标签数据，例如：如果有1000万用户，一台一个输入进去，在水平层这边特征就会比较大。
* FM 的user\_id 会形成冷启动的瓶颈，并且导致更新频率受到限制：传统的FM算法和CM算法，是一定要输入User ID的，那样就会产生一个冷启动的问题。也就是说，如果用户没有参与到每天的活动中，其实是没法在预测阶段做输入的。但是Deep FM则不同，如果对自己的特征比较自信，也就是说你的输入除了User ID之外，还有很多特征。因为Deep FM还会有比较强的特征抽取的能力，也就是自动特征组合能力。此时可以不输入User ID，只输入用户的特征或者是物品的特征，就会避免冷启动问题，而且更新频率会更快。
* DeepFM 的特征输入可以替代user\_id 的输入：比如在一个活动刚开始没多久，收集了一定数量的数据的情况下，特征是比较丰满的，就可以对用户和User ID，Item ID等没有接触到的数据进行一个预测。

![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm29QzxAljUoGZRkqTlIsC8eukCVUkWCToEcYUdbpfkXIwjgR4poFyiaXu1LksllgibqVmOmmj19he0g/640?wx_fmt=png)

最后感谢TEG的同学在tesla平台/智能钛平台上的辛勤工作，为业务提供了优秀的spark内存计算平台和前沿的机器学习算法！

**以上就是今天的分享，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

---

**作者介绍：**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjVM5ay753UNrpJCaePicd32N9BvcVoLWn8uQ0ic5B3Nk3zoicl0VYm2Y0TkxUgyBXvKEib5NMJqsvicFw/640?wx_fmt=png)

********王培军********

腾讯 | 高级工程师

王培军，腾讯高级工程师，主要负责wegame平台的广告系统和深度学习与系统的结合探索。

**会员福利：**

DataFunTalk年度会员卡限时福利：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhxKrz92XEfMRpzHEfLwiasy2TbQUxfT7TFAljcabwqS5gBPK89tVa4icibuwlA4qILOKXMbs8ZVicpFw/640?wx_fmt=jpeg)

**社群推荐：**

欢迎加入 **DataFunTalk 推荐算法**交流群，跟同行零距离交流。**识别二维码**，添加小助手微信，**入群。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjWF4KeBlBY77bxkY6RkGYibHjAzoDzvpicWmiamn1unXwekUjw5gfc21jwoGBMEPxsUy3SW0RKicjZYA/640?wx_fmt=jpeg)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近600位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，9万+精准粉丝。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaalkxbGB7NU2Paq7KM3MPhXtxKJy9M6Bs8EicpUtqCUe6fgfV4HSiaHs7Q/640?wx_fmt=jpeg)

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**