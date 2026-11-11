---
title: 'Calibration4CVR：2018年关于“神经元级别共享的多任务CVR”的初探'
company: Shopee
tag: 推荐
date: 2023-03-05
url: https://mp.weixin.qq.com/s/2JFY--9xDoMF5_2YCehwkg
account: DataFunTalk
origin: readme
---
👆点击上方**DataFunTalk**关注公众号，并**设为星标**🌟，可第一时间接收文章推送

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUVaia8Vew4hYgueEvticWj7n0HKFVXmDkrrHpG8Et8KKSdxXRLfy1lwWA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

**0 题记**

Calibration4CVR 是 2018 年做的一个关于 CVR 的小工作。回顾 2017-2022 年 CVR 优化进展，CVR 的预估和推荐算法中的多任务学习已经进步非常大，从早期的ESMM[1]，ESMM2[2] 到 MMOE[3]，PLE[4]，NCS4CVR[5]等结构。我们可以看到整个模型结构的脉络发展，一个是共享粒度由粗到细，从 ESMM 和 MMOE 的 layer 层或者子网络级别共享 到 基于神经元粒度的共享 Calibration4CVR（本文）/NCS4CVR；另一个是多任务中共享和冲突问题处理机制的灵活性演进，从开始的人工经验指定共享组件到最后的自动学习共享表征部分（MMOE/NCS4CVR）。我自己参与的两个工作 Calibration4CVR（2018）和 NCS4CVR（2020）基本上是沿着这两个方向进行。

*\*NCS4CVR（2020）：https://arxiv.org/pdf/2008.09872.pdf*

笔者近期感觉到 CVR 的整体脉络在 Calibration4CVR 中已经初步显现端倪，所以补上这一环的早期进展介绍，有助于大家理解发展轨迹。不少工作都是已有方向和思路的纵深演化，而大的方向近几年基本上是稳定的，也有助于各位同仁把握后续的探索。

此外，我们可以回看早期多任务 CVR 在共享粒度和自动学习共享的艰难探索尝试的一些技巧；这里边既有探索大方向的一些思考，也有为了拿线上效果的四处出击的实验尝试，虽然现在看来简单且粗糙，当时也确实算是还比较有效的几种方案，希望在实践上有所帮助。

以下基本上是当年的工作观点的重现，并无太多修改，请各位多多指正。

分享嘉宾｜肖玄基 Shopee

内容来源｜作者投稿

出品社区｜DataFun

---

**1. 前言**

多任务学习（MTL）主要解决单个任务的样本不够，导致学习不充分的问题。MTL目前在 NLP 和图像中获得良好应用，主要的方法有三种：1）特征共享 hard sharing。主要是分离需要共享和不需要共享的特征；2）参数共享。主要是松散任务参数有关 soft sharing，方法是稀疏化正则，或者 deep relation network 或者矩阵分解；3）样本共享。判断某样本属于某个任务的概率，然后进行加权降权操作[1]。即使数据比较充分，我们认为在商品推荐场景中多任务学习也可能会有效：单任务模型往往难以取得最优解，多任务学习可以从多个方向逼近最优解，从而提高泛化能力。

在推荐算法，尤其是 CVR 领域，多任务学习最重要的问题是共享和冲突的问题。共享决定了任务之间共享了哪些知识，而冲突则意味着如果两个任务潜在的有矛盾的情况需要解决，学界称之为“negative knowledge transfer”[5]。例如，用户可能有一个随机的单击，点击某个夸张的标题或虚假的封面图像，这种行为将被被特定的神经元连接通过 CTR-CVR 多任务模型中 CTR 任务学习到。尽管如此，这种学习到的表征不应该被 CVR 共享任务，因为在这种情况下 CVR 分数不会很高。针对这个问题，本文在共享哪些部分方面，从同时期的 ESMM 中的 embedding share 尝试提升到 MLP 层级的共享；在冲突解决方面，进行多种模型结构尝试自动化的决定哪些知识不应该共享，而是保持各个任务私有。

我们设计了一种基于 Representation Calibration 的网络架构来实现 CVR 多任务学习。这个工作在一开始受到广告里边的打分校准影响，通过额外的先验知识修正 CTR/CVR 的打分范围，从而能够在出价时候能够变得更加准确（可以理解为如何借助外部信息来修正任务自身的学习，从而得分更加准确）。另一方面收到当时比较火的CV中的SENets影响，通过压缩放大的方式去除信号中的噪声（可以理解为辅助任务独有的知识，对本任务可能就是噪声），从而留下对自己任务有用的信息。

**2. 模型设计**

**2.1 单任务网络**

Baseline 的单侧网络用于建模和学习单个任务，比如 CTR、CVR 等。以 CVR 为例，单侧网络主要由用户位置偏置 bias 网络和 CVR 网络两个子网络组成（见图1）。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUEIquic9ib7Ornf2AIELoH6y5wgvTAyjbuibQU5yicTVslS89CyL1kGuHsw/640?wx_fmt=png)

图1. 单任务网络结构

**2.2 Calibration Based CVR**

在整体设计上，首先我们也采用了业界常见的 embedding 层共享，即 CTR embeding 和 CVR embedding 共享。一般来说，Embeding 作为低阶特征，表达了基础意义，泛化能力较强，直接将 CTR 任务的 embedding 表达借鉴到 CVR 任务中，也能取得一定的预训练效果，这也是目前大部分 MTL 的做法。在上层 MLP 设计中，我们分别针对两个子网络采用特征校准的方法，使用 CTR 的Pos-Net 对 CVR 的 Pos-Net 进行了特征校准，使用 CTR 的 CTR-Net 中学到的知识对 CVR 的 CVR-Net 进行了校准，以解决 CVR 任务相对数据稀疏，特征表达不充分的问题（见图2）。在上层 label 层，我们没有采用 ESMM 中的全空间建模方式，ESMM 理论很简洁优美，但是实践中，我们遭遇了数值不稳定问题；另外，基于对多任务学习的理解，我们认为对于多任务中的主任务（CVR）应该显式的学习，即用自己的 label 进行学习，同时比较丝滑的把其他任务的知识迁移过来，所以并不想隐式的建模 CVR。如下图1，是一个整体框架图，框架可以扩展到更多任务，比如加购、时长等。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUNOpibBna3WDpTNU3iaOBcmcysoPUUiaOQq9q0C6l5J9VIOJpBuzcCrgpg/640?wx_fmt=png)

图2. 基于 Calibration 的整体学习网络

我们的主要工作是找到能够有效提升效果的 calibration 的结构上，设计了四种 calibration 网络结构：

**（1）CTR calibration**

CTR任务  层输出给两层 MLP，然后这层 MLP 和 CVR 任务第 i 层 concat 一起输给 CVR 任务  层。第一层 MLP 的作用是获得非线性能力，即 CTR 任务对于 CVR 特征作用是非线性的，第二层 MLP 是特征选择，即非线性转换+特征选择。（见图3）

theoretical hypothesis：ctr 通过非线性变换和特征筛选得到对 cvr 有用的信息。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUTS5Ry9F6l5l05Q1ph6Tia1fS51nwQJKz3BjG8Db1ibIICZicjLFIuvQng/640?wx_fmt=png)

图3. CTR MLP

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg4hGibl3ic3LZiatVZmP5ibu8Hnf98sTMBTuPskHjtPniaEJA2icYfGf23YzXC6qCXyPOy72NgXFcicnzwg/640?wx_fmt=png)

其中：

● 额外学习的权重，实现特征转换；

● 和为第个隐层 CTR、CVR 任务的特征表达；

● 和为校准后的 CTR、CVR 任务的特征表达；

● 为第个隐层 CVR 任务的表达；

● 非线性激活函数；

**特点：**双隐层设计，增强了 CTR 特征的非线性表达。尝试使用（sigmoid）增强非线性，在 dense layer 2 使用 L1 正则加强特征筛选。

**（2）CTR calibration**

CTR 任务  层输出给一层 MLP，然后输出乘以额外学习 scaling factor，值域范围 0~1，输出结果和 cvr 任务 i 层输出 concat，然后输出给  层。即非线性能力+特征选择。（见图4）

theoretical hypothesis：去掉 negetive transfer knowledge，保留 ctr 中对于 cvr 有用的信息。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUrg7WTZ44DiaxWGk22ZtcBJkwcTElw2OMbHDDMBo946wiblL6IibkXPqug/640?wx_fmt=png)

图4. CTR Scale

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg4hGibl3ic3LZiatVZmP5ibu8HibZ4Vx3GIaciaLYFdUoH8L35Or7YOcZv2TRia0NIUGH6FGqQsY3XvZdYw/640?wx_fmt=png)

其中：

●  额外学习的权重，实现特征转换；

●  和  为第  个隐层 CTR、CVR 任务的特征表达；

●  和  为校准后的 CTR、CVR 任务的特征表达；

●  为第  个隐层 CVR 任务的表达；

●  非线性激活函数；

●  为额外学习的（0，1）之间的 scaling factor；

**特点**：引入单隐层和 scaling factor，实现非线性和全局特征筛选。

**（3）CVR Calibration**

方法5：CTR 任务做 squeeze and excitation 操作映射到 0~1（MLP 结合 sigmoid 函数，得到校准向量）。然后乘以对应的 CVR 输出，即对 CVR 输出做校准。然后一起输出到上层。（见图5）

theoretical hypothesis：我们通过压缩原来 ctr 信息得到一个针对 cvr 各个位置特征校准的一个 calibration 向量。先是压缩 ctr 去掉无用信息，然后经过放大得到和 cvr 一致长度向量，最后通过 sigmoid 得到 0-1 值。因为是受到 cvr 监督，所以可以认为学习到的是对于校准 cvr 有用的信息

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUo21ToNicnfl1X8df26LKHVUHGXkC579IZrKZqzyEWT94bx4VicAlbDYQ/640?wx_fmt=png)

图5. CVR Calibration

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg4hGibl3ic3LZiatVZmP5ibu8HSOfXAlM27Ma617ULKc21Csgz5h4rztjicwPNGkB5XZrFoyOBflQcwqg/640?wx_fmt=png)

其中：

●  额外学习的权重，实现特征转换；

●  和  为第  个隐层 CTR、CVR 任务的特征表达；

●  为校准后的 CVR 任务的特征表达；

●  为第  个隐层 CVR 任务的表达；

●  和  为 sigmoid 和 relu 非线性激活函数；

●  为基于 CTR 任务学习的 scaling factor；

**特点**：基于CTR表达得到校准向量，作用在CVR任务上。

**（4）CVR Calibration Concat**

CTR 任务做 squeeze and excitation 操作映射到 0~1（MLP 结合 sigmoid 函数，得到校准向量）。然后乘以对应的 CVR 输出，即对 CVR 输出做校准。然后再 concat CVR 输出到上层。（见图6）

theoretical hypothesis：和上边相同，类似于残差块，以防止效果退化。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwURPkMKHjx8BERmyC0NlbgA5wx1LSvt9gz3MzG8hiciaFQ3apelT1RqZwQ/640?wx_fmt=png)

图6. CVR Calibration Concat 

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg4hGibl3ic3LZiatVZmP5ibu8HfaM2ogom2Ndan4lQou6GEy0TEgFXFoJ6ZriamNBFwXj26SZLrEPWspQ/640?wx_fmt=png)

其中：

●  额外学习的权重，实现特征转换；

●  和  为第  个隐层 CTR、CVR 任务的特征表达；

●  为校准后的 CVR 任务的特征表达；

●  为第  个隐层 CVR 任务的表达；

●  和  为 sigmoid 和 relu 非线性激活函数；

●  为基于 CTR 任务学习的 scaling factor；

**特点：**基于 CTR 表达得到校准向量，作用在 CVR 任务上，再与原有的 CVR 表达结合。

**3. 实验**

我们使用线上的天级别数据，使用多天数据进行训练，1 天数据进行测试。两侧的子网络采用和线上模型一致的网络，从结构到节点个数均一样。只是在底层共享 embeding 和 full connection 层进行 calibration layer 连接。所有数据只过一遍，CTR 和 CVR 样本交替训练。

经过多次实验和反复调优，我们的实验在某场景上线，其中 CTR MLP 方案和 CVR Calibration Concat 方案相对于 baseline 模型，离线auc都有提升；效果最好的是尤其其中 CVR Calibration 方案，**离线 AUC 绝对值提升约 0.01**，相对于 CVR baseline，线上 **CVR 提升约 2.****8%**。

CVR Calibration Concat 理论上应该比 CVR Calibration 效果更好，主要是 CVR Calibration Concat 可以同时利用 Calibration CVR 表达和 CVR 原始表达，但是实际效果没有显著提升。可能 calibaration 已经自动的学习到了保留最优的 CVR 原始表达，从而不需要残差这种原始信息映射操作。

关于 CTR 和 CVR 样本交替比例的问题，我们尝试了多种比例，并且尝试了 CVR 梯度回传不影响 CTR 本身表达的实验。实验发现：

（1）1:1的比例是最好的；

（2）当减弱 CVR 对于 embedding 的影响时候，CVR auc 下降，这说明 CTR 和 CVR 的商品 embeding 表达还是有显著不同的，需要进一步在 embedding 层做 representation calibration。

**4. 未来工作**

首先，针对现在的工作做更详细的基准测试和实验分析；其次，在 embedding 层，我们将进行聚类分析不同任务（比如 CTR 和 CVR）的表达的差异性。在 loss 层，将尝试 tripletwise 方式来建模 buy，click 和 impression 的差别以缓解多任务学习中的目标冲突。另外将尝试更多任务的 calibration，以多知识累积的方式从不同角度进行 calibration。

**5. 引用文献**

[1] Xiao Ma, Liqin Zhao, Guan Huang, Zhi Wang, Zelin Hu, Xiaoqiang Zhu, Kun Gai.  Entire Space Multi-Task Model: An Effective Approach for Estimating Post-Click Conversion Rate  in:SIGIR-2018

[2] Wen, Hong, Jing Zhang, Yuan Wang, Fuyu Lv, Wentian Bao, Quan Lin, and Keping Yang. "Entire space multi-task modeling via post-click behavior decomposition for conversion rate prediction." In Proceedings of the 43rd International ACM SIGIR conference on research and development in Information Retrieval, pp. 2377-2386. 2020.

[3] Zhao, Zhe, Lichan Hong, Li Wei, Jilin Chen, Aniruddh Nath, Shawn Andrews, Aditee Kumthekar, Maheswaran Sathiamoorthy, Xinyang Yi, and Ed Chi. "Recommending what video to watch next: a multitask ranking system." In Proceedings of the 13th ACM Conference on Recommender Systems, pp. 43-51. 2019.

[4] Tang, Hongyan, Junning Liu, Ming Zhao, and Xudong Gong. "Progressive layered extraction (ple): A novel multi-task learning (mtl) model for personalized recommendations." In Proceedings of the 14th ACM Conference on Recommender Systems, pp. 269-278. 2020.

[5]Xuanji Xiao, Huabin Chen, Yuzhen Liu, Xing Yao, Pei Liu, Chaosheng Fan, Nian Ji, and Xirong Jiang. "LT4REC: A Lottery Ticket Hypothesis Based Multi-task Practice for Video Recommendation System." arXiv preprint arXiv:2008.09872 (2020).

**今天的分享就到这里，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwU4pTZvhbMClH130byAL9aBTtymBFiaf4yMfV53RYgMfCTLuzsX092TUg/640?wx_fmt=gif)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwURftPfvPFxQYKd9J148wFgIVIgTsACItMCSov2rYicqw0lcCGcD0qBwA/640?wx_fmt=png)

分享嘉宾

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwU2H7X5N7DSv5rN7SJ1fSnTU6aKrFZC3EzVnTKZM55C5Blj4l1taicfpw/640?wx_fmt=gif)

肖玄基

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwU2H7X5N7DSv5rN7SJ1fSnTU6aKrFZC3EzVnTKZM55C5Blj4l1taicfpw/640?wx_fmt=gif)

Shopee

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwU2H7X5N7DSv5rN7SJ1fSnTU6aKrFZC3EzVnTKZM55C5Blj4l1taicfpw/640?wx_fmt=gif)

毕业于中科院软件所。曾在腾讯、阿里、百分点工作过，负责 Shopee 内容电商相关算法，包括直播、社交电商、图文视频信息流等。

**｜直播推荐｜**

**💬：从ChatGPT探索大语言模型发展新机遇**

⏰：03.09周四 14-18点

🔗：扫码查看完整议题，预约直播！

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPiaMDvNxgwIJNrOpKxs5NCGX7r9WcY1a8LfGZYwhSiaptXgsA2T4e6hypn51kuJmiaDCTliaYicGteSw3A/640?wx_fmt=jpeg)

**｜免费电子书｜**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUVaia8Vew4hYgueEvticWj7n0HKFVXmDkrrHpG8Et8KKSdxXRLfy1lwWA/640?wx_fmt=png "活动banner图.png")

**｜商务合作｜**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAaILqYAS1t3ibaibLqmBtwUAcFFR0liaaVcyC5BfjpcPnRmU0qJkF6qRSkGoCOlZtIwS0j6Gznrprg/640?wx_fmt=png "商务合作.png")

**｜往期文章精选｜**

1. [小米电商推荐算法CVR模型实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247614845&idx=1&sn=0e8c26b62cd8e2ffe5c54e6e3ee28a5d&chksm=fbd6b311cca13a07f68d47ac22d2ebc0f2fad1e082809bd0ccc8f68a5bc6f298e2bc16fa0ec1&scene=21#wechat_redirect)

2. [王志勇：贝壳CVR转化率预估模型实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247565976&idx=1&sn=a651d09cdd08268b1424c854790e3a59&chksm=fbd670f4cca1f9e25c39dea866a2b3c4ffeb954ad078e46404656f464f45eb4081307b8476cd&scene=21#wechat_redirect)

3. [多任务学习模型ESMM原理与实现](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247571544&idx=2&sn=c298c717bb79092cb8ea7adf718cf64b&chksm=fbd66a34cca1e3222d5ab2f54185cea9732528721b3f0ad3df83dc15e14a30b1d6c6f64fafa2&scene=21#wechat_redirect)

**｜关于DataFun｜**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhdKPLI48aUcJmBqVPNlGWXBQI72FmGW1fvOj15rEeibUq5q3Z8ZNh5nHDjrk3XrFic3ICYcM7LOLSQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

![](https://res.wx.qq.com/t/wx_fed/we-emoji/res/v1.3.10/assets/newemoji/Hurt.png)公众号又改推送规则啦...

将公众号设置为星标🌟，才会第一时间接收到文章推送

设置星标仅需3步👇

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPj0vL6CDm0ThYIW41gC9Cr1iaM9orNudyXqKkoE846K40soVEjAKmz2wASrtYIQJIvpIeItOM9Qjhg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**👇**点击**阅读原文**可阅读往期全部文章