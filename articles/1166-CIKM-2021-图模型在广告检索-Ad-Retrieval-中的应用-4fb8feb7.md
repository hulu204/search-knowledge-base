---
title: 'CIKM 2021 | 图模型在广告检索（Ad Retrieval）中的应用'
company: 阿里妈妈
tag: 搜索
date: 2021-12-15
url: http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490345&idx=2&sn=bca169f92bce0b789189bfc3215db9c2&chksm=c0095d4af77ed45ce82dd547680ac618c5405a709eb504197e999c0b3ca77a3e42f130ca02fe#rd
account: 阿里妈妈技术
origin: wechat-mp
---
# ▐ 1. 摘要

图模型能够有效的挖掘数据中的关系信息来增强数据表示，在研究和工业领域都被广泛应用。阿里妈妈搜索广告技术团队于2019年开源了工业界首个支持大规模分布式的深度图学习平台Euler（https://github.com/alibaba/euler），被业界广泛使用（Github Star：2.7K）。基于Euler框架，我们进行了在不同算法模块的多版算法迭代升级，本文针对电商检索系统中海量用户行为以及多视图并存（如共同点击、共同竞买或文本相似等）带来的挑战，我们将介绍在搜索广告检索模块（ad retrieval）中的一种可扩展的多视图广告图匹配引擎（SMAD）。利用电商商品体系的类目树结构，我们提出了一种类目相关性约束下的图采样和分割算法，可以实现大规模图的分布式训练；同时，为了更好的捕捉多视图结构，我们提出了一种并行的多视图训练模型，可以将不同视图下的信息有机融合起来。在阿里搜索广告场景中，该方法在相关性、覆盖率和平台营收等指标上均取得了明显的效果。该项工作论文发表在 CIKM 2021 ，欢迎交流讨论。

# ▐ 2. 引言

在电商搜索平台中，用户通过搜索词（Query）来反映其意图，平台会给用户返回一系列产品，包括广告（Ad）和自然商品（Item）。为了平衡效率和效果，如图（1）左下所示，业界搜索系统通常采用多阶段的搜索架构：首先使用简单高效的模型从大规模的广告候选集中检索出更小规模的相关的广告（广告检索模块，ad retrieval），然后使用更加复杂精细的模型对检索出广告进行排序（排序模块，ad ranking）。在本文中，针对广告检索模块，我们提出使用图嵌入技术来得到 Query 和 Ad 的表征，并通过 ANN（Approximate Nearest Neighbor）来检索相关广告，保证计算效率的同时使用图模型的表征能力优势提升匹配效果。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc7fkcB7WPmWicHcxS0Kialthz31r0mShMBX1AtQTOrHyKxa2Rib4dy1dLQnGJTJVCeibC3dRNHVJFepYA/640?wx_fmt=png)

图（1）：淘宝搜索广告系统架构，包含了广告检索和广告排序两个阶段。在广告检索阶段，我们提出了SMAD检索算法，通过图学习的方式来学习用户搜索和广告之间的匹配关系。

然而，直接将传统的图嵌入方法[2, 4-8]应用于电商搜索广告中的检索任务，会遇到可扩展性和相关性下降的问题。考虑到工业场景下具有数十亿规模的节点（Query、Item 和 Ad），因此需要多台机器来存储图数据，从而产生较高的通信成本。此外，在全图上进行随机游走可能导致相关性下降，例如，一个 Query 节点“连衣裙”和一个连衣裙相关的Ad节点有共同点击连边，而后者与“毛衣”相关的商品也具有共同点击关系（例如，在同一个 Query “女装”下），现有的方法[3，7]因为没有限制从“连衣裙”到“毛衣”的随机游走路径从而无法保证相关性。此外，在类似淘宝的电商平台，在 Query 和 Item/Ad 之间有多种类型的关系，例如共同点击，文本相似等等，可以把每种关系将节点关联起来的图看成是一种“视图”（view），单独视图通常都是稀疏和有偏的，需要对多视图进行融合来实现互补。同时，淘宝上有数十种节点属性，包括类目、品牌、店铺等，充分利用这些信息可以提升模型的泛化能力。因此，我们希望设计一种方法能够有效利用丰富的节点属性和多视图信息来提升模型效果。

在本文，我们提出了一个新颖的广告检索框架，即可扩展的多视图广告检索（Scalable multi-view ad retrieval，SMAD），并已在淘宝广告的生产环境中部署。其创新之处包括以下三个方面：

首先，我们提出利用电商系统中的类目树以及图的聚集性来进行游走和采样。在电商平台中，每个节点（Query/Item/Ad）均会被分配到类目树中的某一个节点（如图（2）所示）。为了尊重用户的搜索意图，Query 和 Ad 应该在同一个子类目下进行匹配。具体地，SMAD 通过类目树的性质来进行子图内邻居搜索，这种简单有效的策略能显著提升通信和计算效率，同时能够增强 Query 和 Ad 之间的相关性。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4FSKbib7VXb2dvHy2nOlA9aYkpbxZ4JdravT18yMmADrICqu28H1Jhvs8MsZmRS0hbTfahz8jp6vQ/640?wx_fmt=png)

图（2）：类目树示例，搜索词”实木北欧床”隶属于“住宅家具”的子类“床类”的子类“实木床”

其次，我们提出了一个有效的并行深度神经网络（Parallel deep Neural Network，PNN）架构来从节点丰富的属性和节点间多视图关系中学习到节点表示信息。具体地，它对每个关系视图学习一个DNN表示，根据节点在不同视图中的特征和相关程度来学习特定视图下的节点表征，最后使用注意力机制将同一个节点的多个视图表征融合为一个更加鲁棒的表征。

最后，我们提出了一个高效的分布式模型部署方案，该模型将大规模图分解为多个较小的子图，并可以独立地在本地运行，从而实现训练的并行化。我们将 SMAD 部署在淘宝的无线广告搜索平台中，并通过离线和在线A/B测试来表明我们的系统可以显著提高广告检索性能以及提升平台收入和用户体验。

# ▐ 3. SMAD模型训练和应用

图（1）左上展示了 SMAD 在 Query 和 Ad 之间进行匹配的流程。它首先从用户的历史行为以及 Query 和 Item 的文本描述中构建一个多视图的 Query-Item-Ad 关系图，然后基于类目约束下的随机游走生成训练样本，最后应用 PNN 模型来学习图中每个节点的表示，并被用来进行最终的广告检索。下面将详细介绍 SMAD 的设计细节。

## 3.1 多视图构建

在 SMAD 中，Query-Item-Ad 图由三种类型的节点组成，包括Query、Item和Ad，每个节点都包含ID、类目、品牌、价格等特征。图中包含以下边类型：

1）点击关系边，给定在一个用户搜索请求下的点击序列，其中代表被点击的自然结果商品（item）或广告商品（ad）。我们在两个被点击的Item（或Ad）节点和之间建立共同点击边，以及在每个被点击节点与Query节点之间建立点击边。

2）文本相似关系边。由于电商系统中每天都会新建新的广告，我们需要依靠其文本属性进行冷启动。具体地，我们计算Query和Item/Ad标题之间的Jaccard相似性，并作为权重来建立文本相似边。

3）共同竞价关系边。在广告搜索平台中，广告主通常会为每个广告指定一组<竞价词，价格>，用来表达他们希望触达的流量和此广告被用户点击时支付的金额。如果两个广告至少有一个相同的竞价词，它们就会被建立一条共同竞价边。

## 3.2 类目树约束下的图采样

我们使用随机游走[3, 7]策略来生成训练样本。一方面，正如上文中所提到的，在游走过程中相关性会衰减；另一方面，大规模图训练的时间代价也很高。由于图的规模很大，无法装入单台机器的内存中，所以一般进行分布式图存储，使得在训练过程中需要在机器间进行大量的通信。为了解决这些问题，我们根据电商系统中的分层类目树结构，建立了一个有效的采样和图划分策略。具体地，在淘宝上，一个类目树包含了大约几万个类目，最多有5个级别，例如“圆领衫≤长袖针织衫≤毛衣≤上衣≤女装”。Query、Item和Ad节点都可以被分配至类目树中的某一个节点。

### 3.2.1 类目约束下的随机游走

我们提出了一种类目树约束下随机游走，要求游走路径需要遵守类目层次，也就是说，游走的路径必须是非递增的。通过进入更低级的子类目或者在同一子类目上停留更长时间更能够表达用户的真实意图，例如图（3）中的“𝑣0（搜索女性时装）→𝑣1（点击裙子Item1）→𝑣2（搜索裙子）→𝑣3（点击裙子Item2）”为一个合理的游走，这是搜索场景的一个特点，与没有提供明确意图的推荐应用很不相同[9, 11]。给定一个基于关系元路径的有效游走，我们在滑动窗口内提取正节点对 ，其中  表示正节点。负采样是为了给源节点𝑣生成负节点，为了使增加学习的鲁棒性和模型的能力，我们既在与𝑣不同类目空间下采样简单的负样本，同时也在与𝑣相同类目空间下采样负样本。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc7fkcB7WPmWicHcxS0KialthzXXpnibCC8YYk6GZiaFfx4quFcG0XpTvlDoXMD8nwicTyu78RUCuW2P8jw/640?wx_fmt=png)

图（3）：类目树约束下的随机游走。图中展现了一个合理的游走路径。其中红色节点是Query节点。

### 3.2.2 类目约束下的子图切分策略

基于上述的类目约束下的随机游走策略，图数据可以被分解为独立的子图。子图可以独立的在本地运行，实现大规模并行，从而带来巨大的通信与计算效益提升。如图（3）所示，子图由同属某一叶子类目的节点构成。非叶子类目的节点则被切分到多个以其为邻居节点的子图上。例如节点 （搜索女装）有两个邻居节点 （点击连衣裙1）和 （点击毛衣1），那么节点  会被切分为两个节点，分别附加到“连衣裙”和“女士毛衣”两个子图中。通过节点切分，边集可以根据源节点和目标节点所在的叶子类目进行拆分，并且跨子图的边可以被移除（比如构图时不创建）。此外如果两个非叶子类目节点互相连接，我们允许它们的拆分复制体在相应的子图中也互相连接（见图3）。通过这些方法，我们得到了大量不相交的子图。

## 3.3 PNN模型结构

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc7fkcB7WPmWicHcxS0KialthzuDjKXojp01SWiceFbh1yNGkYjuziaPLyWFtnLxgcHpCGzbNtn0K7Eyicg/640?wx_fmt=png)

图（4）：PNN（Parallel DNN）模型架构。各个视图的DNN分支共享同一个嵌入层。正负节点共享相同的中间网络层。除了节点ID，节点属性也被引入到DNN中。

SMAD采用了一种新颖的并行DNN架构（PNN），如图（4）所示，用于在多视图属性图上进行表征学习。模型结构分为两个模块：

**(i) 独立视图学习。** DNN架构有多个并行分支，分别对应于不同视图（即游走方法中的不同类型关系或元路径）。每个分支初始共享嵌入(EMB)层，用于编码原始节点特征为统一的特征向量。每个分支最后包括视图特定层，用于学习对应视图中节点的相似度。针对视图  下具备  类型的节点 ，分支分别采用不同的特征变换层  来学习其向量 。为了促进多视图的协作，我们允许具备同一类型  的节点在不同视图中共享特征变换层 。因此，如果定义 ， 为节点类型和视图（边类型）个数，那么模型一共学习  个全连接神经网络分支，用来编码  个视图中  种类型的源节点，以及  个全连接神经网络分支，用来编码  种类型的目标节点。

**(ii) 基于注意力机制的视图结合。** 我们设计了注意力机制用来建模不同视图的重要性。注意到对  类型的节点 ，它包含  个视图的表征，在此基础上使用注意力机制设计手段，我们选择 softmax 来学习不同视图的重要性：

其中  表明不同视图下表征的重要性， 表明节点  学习到的特定稳定表征， 是可学习的向量，表明哪些  类型的节点在  视图中更重要。相似度高的节点往往具备相似的特定视图表征，因此相似的视图往往更受关注。

**损失函数。** 为了保留多视图属性图的拓扑结构信息，我们使用如下损失函数：

其中  是 sigmoid 函数， 是学习稳定表征的损失函数， 是在每个视图中学习节点相似度的正则项， 是用来控制正则项权重的参数。、、 分别是节点  的稳定表征、正样本及负样本，对应到视图  上，其表征分别为 、 及 。

## 3.4 实现细节

我们使用已经开源的分布式图学习框架 Euler 进行图存储和模型训练。训练结束后，使用一个类 Faiss 检索，进行近似 KNN 计算，基于节点 Embedding 进行相似广告召回。实验相关配置如下：使用高斯分布进行模型参数的随机初始化；采用 Adam 作为优化器；batch size 设置为 512；学习率设置为 0.001；使用50台阿里云上的虚拟机进行实验，每个虚拟机配置 28个CPU核 + 30GB 内存。

# ▐ 4. 实验评估

为了验证SMAD的有效性，我们进行全面的离线实验和在线A/B测试。

## 4.1 对比方法

实验主要对比了一些经典的广告召回模型：

* 基于图的用户历史行为建模方法：SimRank++、BKR；
* 基于语义的向量化召回：DSSM、Search2vec、MVE。

同时，为了方便对比 SMAD 中每个结构设计的效果，我们也将 SMAD 的一些变体模型作为 baseline：

* SMAD（random）：将SMAD中采样方法替换为标准的随机游走；
* SMAD（no-attribute）：只使用ID类特征作为模型的输入，不使用其他属性特征
* SMAD（no-attention）：去掉SMAD中的attention聚合结构，只用单视图进行点击边的训练

## 4.2 离线评估结果

我们基于一份人工标注的 query-ad/item-ad 数据，进行相关性评估，作为离线模型的评估数据。这份人工标注的数据收集于淘宝搜索广告场景的日志，一共抽取了20000个 query-ad 对和20000个 item-ad 对，并基于相关程度人工将其分为“bad”、“fair”、“good”、“excellent”和“perfert”五个等级。对于每个 query 或者 item，有10个候选广告进行选择。我们使用 macro NDCG 进行模型的离线评估，并赋予上述5个等级分值（grade）如下：bad-1，fair-2，good-3，excellent-4，perfect-5。我们使用  作为 NDCG 的 label，使用排序位置的 log 作为 NDCG 的分母。我们基于上文提到的淘宝搜索场景数据进行构图和离线模型训练。该图包含了1亿的 Query 节点、1亿 Item 节点、1千万 Ad 节点，百亿级别的用户行为边和文本相似度边。为了减少训练过程中的通讯开销，我们将这张大图基于类目分解成不同的子图，从而实现模型的并行化训练。子图的分解极大的优化了模型训练的计算和通讯开销。下表展示了 SMAD 在 Euler 系统下的运行性能，整张图 SMAD 的训练时间少于24小时。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc7fkcB7WPmWicHcxS0Kialthz7k8ibmxaax1xl8YRdawt0X9931GibFOseJiaO0IkG8qyq3NuqxqEI2hbA/640?wx_fmt=png)

表（1）：不同batch size下的运行时间对比

实验结果如下表所示。从表中可以看出，在这份离线数据上，SMAD效果远高于其他baseline。对比其他的基于图的或者基于向量化的广告召回方法，SMAD得益于其有效的点边信息汇聚，多视图异构建模和Query-Item-Ad高阶关系提取，取得了不错的离线收益。同时也验证了这种新型PNN结构和基于数据分布的邻居检索方式的有效性。通过SMAD和SMAD变体模型的对比实验结果，进一步验证了每个结构模块的有效性。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc7fkcB7WPmWicHcxS0Kialthz9bI8aD6ptnqiceGH4EcjCSMZKgM13amHhgyr7RgwbBXqrzx3jaLuXCA/640?wx_fmt=png)

表（2）：和比较流行的各种方法的对比实验结果

## 4.3 在线A/B测试

我们在淘宝搜索广告召回系统中进行了上述模型的在线实验。并使用 CTR，RPM 和 PVR（有广告展示的请求占比）作为在线实验评估指标。如下表所示，对比 SimRank++，BKR 和 Search2vec 模型，SMAD 分别获得了CTR+5%，+5.5%和+1.5%的在线收益。实验结果验证了 SMAD 可以更优的刻画搜索意图和广告的匹配程度。同时，PVR也获得了+3%，+2%和+1%的提升，说明 SMAD 模型可以覆盖更多的搜索请求。通过 SMAD 与 SMAD（random）的对比发现，随机游走和随机采样方法并不能很好的刻画广告与当前请求的相关度，导致在线 CTR 和 RPM 均出现明显下跌。与 SMAD（no-attribute）对比发现，得益于丰富的属性特征引入，SMAD 显著提升了 CTR 和 PVR。与 SMAD（no-attention）对比发现，attention 聚合方式的引入可以提升 PVR 指标。

# ▐ 5. 结论

本文介绍了一种海量规模广告召回框架 SMAD，该框架将广告场景下用户行为抽象成图，并引入丰富的点边属性，通过衡量结构相似度，多视图建模相关性，从而实现 Query 和 Ad 的有效匹配。我们采用了一种基于搜索广告类目树结构的训练策略，并提出一种多视图网络模型汇聚 Query-Item-Ad 多维度异构关系和信息，在淘系十亿级别图数据上进行的离在线实验也充分证明了 SMAD 的有效性。

# 参考文献

[1] IoannisAntonellis,HectorGarciaMolina,andChiChaoChang.2008.Simrank++: query rewriting through link analysis of the click graph. Proceedings of the VLDB Endowment 1, 1 (2008), 408–421.

[2] Shaosheng Cao, Wei Lu, and Qiongkai Xu. 2016. Deep neural networks for learn- ing graph representations. In Thirtieth AAAI Conference on Artificial Intelligence.

[3] Yuxiao Dong, Nitesh V Chawla, and Ananthram Swami. 2017. metapath2vec: Scalable representation learning for heterogeneous networks. In Proceedings of the 23rd ACM SIGKDD international conference on knowledge discovery and data mining. ACM, 135–144.

[4] MihajloGrbovic,NemanjaDjuric,VladanRadosavljevic,FabrizioSilvestri,Ri- cardo Baeza-Yates, Andrew Feng, Erik Ordentlich, Lee Yang, and Gavin Owens. 2016. Scalable semantic matching of queries to ads in sponsored search advertis- ing. In Proceedings of the 39th International ACM SIGIR conference on Research and Development in Information Retrieval. ACM, 375–384.

[5] Aditya Grover and Jure Leskovec. 2016. node2vec: Scalable feature learning for networks. In Proceedings of the 22nd ACM SIGKDD international conference on Knowledge discovery and data mining. ACM, 855–864.

[6] Po-Sen Huang, Xiaodong He, Jianfeng Gao, Li Deng, Alex Acero, and Larry Heck. 2013. Learning deep structured semantic models for web search using clickthrough data. In Proceedings of the 22nd ACM international conference on Information & Knowledge Management. ACM, 2333–2338.

[7] BryanPerozzi,RamiAl-Rfou,andStevenSkiena.2014.Deepwalk:Onlinelearning of social representations. In Proceedings of the 20th ACM SIGKDD international conference on Knowledge discovery and data mining. ACM, 701–710.

[8] Meng Qu, Jian Tang, Jingbo Shang, Xiang Ren, Ming Zhang, and Jiawei Han. 2017. An attention-based collaboration framework for multi-view network repre- sentation learning. In Proceedings of the 2017 ACM on Conference on Information and Knowledge Management. ACM, 1767–1776. 

[9] JizheWang,PipeiHuang,HuanZhao,ZhiboZhang,BinqiangZhao,andDikLun Lee. 2018. Billion-scale commodity embedding for e-commerce recommendation in alibaba. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. ACM, 839–848.

[10] SuYan,WeiLin,TianshuWu,DaoruiXiao,XuZheng,BoWu,andKaipengLiu. 2018. Beyond keywords and relevance: a personalized ad retrieval framework in e-commerce sponsored search. In Proceedings of the 2018 World Wide Web Conference. International World Wide Web Conferences Steering Committee, 1919–1928.

[11] Rex Ying, Ruining He, Kaifeng Chen, and Pong Eksombatchai. 2018. Graph Con- volutional Neural Networks for Web-Scale Recommender Systems. In Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. ACM.

END

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif)

**欢迎关注[「阿里妈妈技术」](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247484017&idx=1&sn=eac2d6d4293e99c93ee86d031a972b6e&chksm=ce8a4728f9fdce3e21daf5d9cf049af872282e3a85bf59382f12a3f1ff5a8d2bba6ca6188bbf&scene=21#wechat_redirect)，了解更多~**

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc4FSKbib7VXb2dvHy2nOlA9aFaMtrVWGIticBGBM2ZPHdu3LmlHGW4A0CCLR0e6GC6cyS6f3VY1ExSw/640?wx_fmt=gif)

疯狂暗示↓↓↓↓↓↓↓