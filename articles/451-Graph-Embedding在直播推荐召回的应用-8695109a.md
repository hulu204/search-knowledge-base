---
title: 'Graph Embedding在直播推荐召回的应用'
company: BIGO
tag: 召回
date: 2020-07-23
url: https://mp.weixin.qq.com/s/364uvoiVmUrXhlM6W3yeGg
account: BIGO技术
origin: readme
---
***01***

**概述**

推荐系统已经成为互联网平台的流量分发中枢，其核心架构主要包含三层：

1)  **Recall层**，负责从全量的item池里筛选出用户可能感兴趣的item；

2)  **Rank层**，根据推荐系统的整体目标对Recall层召回的item进行排序后截取topN；

3)  **Rerank层**，综合排序目标、用户体验和平台生态对Rank层选取的item做最终的展示布局。

![](https://mmbiz.qpic.cn/mmbiz_png/NWxUKhtEg13GHgaSZ6PXP0c0KwmZQdo1bX4xpshciaTaulDjlZ5RNib78zLEnsZtsqcZEiaAEM3lVC6myXKCTDKxg/640?wx_fmt=png)

图1

召回模块决定了排序效果的上限，Bigo Live直播推荐早期的召回主要是基于两种方式：

**一、****主播热度**，例如主播的观看人数、点赞人数、送礼人数、转发数、评论数等；

**二、用户和主播的亲密度**，例如用户对主播的历史观看时长、用户对主播的其他作品的观看数、用户对主播的关注等。

这样的召回方式能保证召回的主播的质量，一定程度保证了用户的体验，但是这也导致了马太效应，流量越来越集中在头部主播，长尾主播很难获得有效流量。针对这个痛点，我们在召回模块引入了基于邻域的协同过滤(ItemCF和UserCF)、基于隐向量的协同过滤(NCF)、YouTube DNN、DSSM双塔模型和Graph Embedding来丰富召回通道。这些召回策略的引入，显著提升了我们直播推荐系统的核心指标，其中Graph Embedding在直播召回中效果提升尤为亮眼。

**Graph Embedding通过随机游走，既会生成多阶节点(主播或用户)构成的序列，也会生成局部节点构成的序列，再经过Word2Vec学习(上下文相近Embedding向量相似)，不但可以挖掘到局部节点之间的关系，还可以挖掘多阶节点之间的关系，通过u2i、i2i、u2i2i和u2u2i可以有效拓展推荐的覆盖度和多样性。**由DFS游走得到的序列，节点的上下文更倾向于包含多阶邻居节点，因此两个节点，只要它们的多阶邻居整体相近，即使不直接相连，它们的Embedding向量也比较相似，这增加节点间的同质性；由BFS游走得到的序列，节点的上下文至多包含邻居节点的1阶邻居，所以局部相连比较多的节点，它们的上下文比较相近，因此它们的Embedding向量比较相似，这增加节点间的同构性。**综上所述，对于直播场景，Graph Embedding能有效学习到主播与主播之间、用户与用户之间及用户与主播之间的多阶关系，可以增强推荐主播的同质性和同构性，提升直播推荐的覆盖度和多样性。**

本文将介绍Graph Embedding在我们直播推荐场景召回中的实践运用。

***02***

**Graph Embedding在直播召回上应用**

Graph Embedding在直播召回上应用的主要包含三个流程：

1、**网络图构建**，根据用户的行为数据来构建网络图。网络图的构建方式对最终效果影响比较大，需要结合场景来设计点和边的选取；

2、**样本生成和模型训练**，利用随机游走生成训练样本，并利用深度模型训练样本得到节点的Embedding向量。在生成训练样本前，要确定好Embedding向量建模的方式，方便生成符合模型目标的训练样本；

3、**ANN检索**，利用ANN检索出topN个相似主播。

**1. 网络图构建**

图的构建方式有两种：

**一、同构图**(图2)，根据用户的session行为序列来构建有向图，图中节点是主播，用户在同一个session里对主播A产生观看、点赞等有效行为，接着对主播B产有效行为，则从主播A的节点到主播B的节点引一条有向边，边的权重根据用户对两个节点(主播)的行为和系统优化目标来确定，如果主播A到B后续还能产生重复边，需要对边的权重做相应的融合加强。

**二、异构图**(图3)，根据用户对主播的观看、点赞、转发、关注、送礼等行为关系来构建图，图中节点包含主播和用户两种类型，边的类型由观看、点赞、转发、关注、送礼等用户行为组成的结构体(struct)来表达，边权重可以结合系统优化目标、边的结构体和节点本身的属性来确定。

在我们的直播场景对两种建图方式都进行了尝试，异构图的收益显著高于同构图，我们觉得主要是因为异构图中包含了更丰富的用户信息和用户行为信息，使得最终的Embedding向量更加有效。

![](https://mmbiz.qpic.cn/mmbiz_png/NWxUKhtEg13GHgaSZ6PXP0c0KwmZQdo1GRhtff5jXgD8ejedYNibj6mAjKYDa3atA24Uqbgia84FY8fYPMT1icZkA/640?wx_fmt=png)

图2

![](https://mmbiz.qpic.cn/mmbiz_png/NWxUKhtEg13GHgaSZ6PXP0c0KwmZQdo1gsEW9zGD3rZichdvXKBCTpbycJxD25TRcmeYdiboWAn9LkwC2eyoicH9A/640?wx_fmt=png)

图3

**2. 样本生成及模型训练**

对于同构图(图2)，我们利用**DeepWalk**，从每个节点游走，每次游走产生长度为L的主播序列，将这些序列作为word2vec的训练样本，使用Skip-Gram学习得到主播Embedding向量。

对于异构图(图3)，我们使用**Node2vec Walk**，从每个节点游走，每次游走得到长度为L的序列。对于每个序列，通过滑窗口得到正例对  。如果只想生成特定类型的节点序列，可以根据节点类型和边结构体过滤出特定类型节点序列。另外，对于这个正例对  ，我们同时负采样生成K个负节点，这样就构造出一个训练样本  ，使用DSSM训练这些样本，其中  是模型输入，edge根据其结构体的值来对模型参数做不同限定，所以对于同一个节点，可以表征出它在边结构体不同限定下的Embedding向量，然后将这些Embedding向量做自适应融合成该节点最后的Embedding向量。例如，观看、点赞、送礼各自对应一组参数，这样一个主播就有来自观看、点赞、送礼的三个Embedding向量表征，我们再将这个主播对应的观看、点赞、送礼的Embedding向量表征融合成主播最终的Embedding向量。对于样本  ，设它最终被融合成的向量表示为  ，那么它对应的loss可以表示成 其中，

![](https://mmbiz.qpic.cn/mmbiz_png/NWxUKhtEg13GHgaSZ6PXP0c0KwmZQdo1ktX7EYH3cDvZQueAd7Unuq8ap3lE1oISWxUVgK523pcfDD3CJSt8Zg/640?wx_fmt=png)

为了充分学习节点关系和更贴近场景，我们设计了边权重为节点属性和边结构体的函数，即   ，不仅关注边结构体的取值，还考虑节点的自身属性(如主播的颜值、营收等，用户的观看总时长、送礼总数等)，这样既能对高频节点进行打压和对低频节点进行扶持，还能让样本更接近直播场景，可以有效提升Embedding向量的最终效果。同时，随机采样得到的负节点要满足两个要求：

**一、负节点和正节点分布要一致。**如果正节点分布和负节点分布相差太大，模型会倾向于记住正负节点表面差异，而忽略了节点之间的内在关联。我们进行带权负采样，能使得正负节点分布尽量相近。

**二、负节点和源节点之间要具有相关性。**在实际直播推荐场景，负节点和源节点本来就具有某种弱相关关系，另外，如果负节点和源节点完全无关，会导致模型很容易分辨出正负样本，学习出来的Embedding向量实际效果不明显。在选择负样本的时候，我们参考了节点的Side Information信息和源节点的Session信息，使得负样本和源节点之间具有弱相关性。

**3. ANN检索**

得到节点的Embedding向量，将主播的Embedding向量存入线上ANN引擎(如Faiss、Annoy、Hnswlib)，线上通过用户的行为特征，查找或者计算相应的节点(用户本身或者用户关联的主播)的向量，通过ANN引擎召回最相似的topN个主播。ANN检索的过程离线进行也可以，未必一定在线，要根据场景更新频率、线上性能等具体情况来确定。

***03***

**解决问题的有效尝试**

**1. 长尾用户推荐**

长尾用户由于行为比较少，进行随机游走生成样本少，会导致其Embedding向量训练不充分，从而导致推荐效果不如人意，针对这个问题，我们尝试了以下解决方案：

一、通过异构图，增加召回用户节点n阶领域内的用户节点对应的亲密度主播(图4)，提升了长尾用户推荐覆盖和质量。

二、对用户分桶计算Embedding向量，用桶之间的相似度来衡量用户的相似度。用户分桶之后，采用桶内用户的行为日志，来学习对应桶的Embedding向量，有效缓解了长尾用户因训练数据少而导致Embedding向量学习不充分的问题。

三、扩充数据，融合用户的社交网络和其它APP行为等数据，同时结合知识图谱做扩展，提升了长尾用户推荐效果。

![](https://mmbiz.qpic.cn/mmbiz_png/NWxUKhtEg13GHgaSZ6PXP0c0KwmZQdo1eHIVDlQjoKRt8zV45CX2mj3lZE5jsXTEaOYOLXArtG6PtE23b7icY7w/640?wx_fmt=png)

图4

**2. 长尾主播推荐**

对于长尾主播，我们除了使用Exploration-Exploitation、流量扶持等传统技术来让更多优质主播获得有效曝光外，还尝试了在Graph Embedding扩展主播Embedding来源。由于长尾主播(尤其是新主播)曝光历史很少，单纯使用用户行为生成的图网络，学习到的Embedding效果不明显，针对这个问题，在模型训练时，我们对主播加入Side Information的Embedding来补充其Embedding(图5)，**其中Side Information包含封面类型、标签、国家、语言、性别、年龄等，和主播ID相比，这些属性具有很好的泛化能力，能够提高模型的稳定性，使历史行为记录较少的主播也能获得合理的Embedding表示，让这部分主播的获得有效的曝光。**

![](https://mmbiz.qpic.cn/mmbiz_png/NWxUKhtEg13GHgaSZ6PXP0c0KwmZQdo1icycGYibTQ18D1cl8LRbt4ibiaweEfvdhO641ENBMJDH2uBy8rr6SQsP2g/640?wx_fmt=png)

图5

***04***

**总结**

我们在直播推荐的召回环节引入了**Graph Embedding技术**，提出在召回阶段利用用户观看、送礼、点赞、分享、关注等行为构建一个大规模异构图，并利用DeepWalk在图节点上充分游走生成符合场景的训练样本，使节点Embedding向量得到充分学习，拟合出潜在同质关系信息，显著提升了主播召回的相关性，提升了用户的留存；同时Graph Embedding能挖掘出潜在的同构关系，提升主播召回的多样性和新颖性，提升了用户体验；另外，利用Side Information的深度网络进行知识泛化学习，在一定程度上解决了用户覆盖、新主播面临的冷启动问题。

随着Graph Embedding技术在工业中收益逐步显现，学术界对Graph Embedding技术加大了研究，出现了很多优秀的算法模型，例如，HERec推荐模型在异构图中，基于随机游走生成节点序列，筛选出有效同构节点序列，学习节点的Embedding向量。Metapath2vec在异构图上随机游走抽取节点结构信息，再用Skip-Gram算法学习节点的Embedding向量。HINE基于metapath游走来计算节点之间的相似度，将其作为监督信号来指导节点Embedding向量的学习。JRL推荐模型利用异构图信息学习用户和Item的Embedding向量，再通过外层学习用户和Item的联合表示来做召回。

**直播推荐的内容是实时动态的，还有用户的直接交互，涉及文本、图片、视频、音频等多模态内容，图神经网络有强大的表示能力，自身还在不断的迭代更新，Graph Embedding在直播挖掘方面有很大潜力。**我们在召回中引入Graph Embedding，一定程度上解决了系统问题，显著提升了线上核心指标。我们的工作只是GraphEmbedding应用的初步尝试，希望通过我们的实践，能启发大家挖掘出更多Graph Embedding在直播场景的有效运用方式。

**参考文献**

[1] B Perozzi. Deepwalk: Online learning of social representations [2014]

[2] A Grover. Node2vec: Scalable Feature Learning for Networks [2016]

[3] WL Hamilton. Inductive Representation Learning on Large Graphs [2017]

[4] T Mikolov. Distributed Representations of Words and Phrases and theirCompositionality [2013]

[5] J Wang. Enhanced Graph Embedding with Side Information [2018]

[6] J Tang. LINE: Large-scale Information Network Embedding [2015]

[7] C Shi. Heterogeneous Information Network Embedding for Recommendation[2017]

[8] Y Dong. metapath2vec: Scalable representation learning forheterogeneous networks [2017]

[9] Z Huang. Heterogeneous Information Network Embedding for Meta Pathbased Proximity [2017]

[10] Y Zhang. Joint representation learning for top-n recommendation withheterogeneous information sources [2017]

版权声明

转载本网站原创文章需要注明来源出处。因互联网客观情况，原创文章中可能会存在不当使用的情况，如文章部分图片或者部分引用内容未能及时与相关权利人取得联系，非恶意侵犯相关权利人的权益，敬请相关权利人谅解并联系我们及时处理。