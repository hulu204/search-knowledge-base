---
title: 'ICDM论文：探索跨会话信息感知的推荐模型'
company: 美团
tag: 推荐
date: 2020-12-10
url: http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651755958&idx=2&sn=bb2a7e9e3817d9993a9137dfeb6b5ec4&chksm=bd124cfb8a65c5ed3453a6473b556df1968e9f983da94bcab6610f718bfed2b37be5bd3ad7ae&mpshare=1&scene=1&srcid=0117wmg82Cvm9SxD2roqqbzV&sharer_sharetime=1673957290926&sharer_shareid=c032e8bde4d276951619cca1ff0debb1#rd
account: 美团技术团队
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsUrXicw2VXTQTVVN5yxXWEacdY1ZdxTH195Pgibtib8EENJRMia3tzEnyVfgyfAgRibMssKqwlE186TLSw/640?wx_fmt=png)

**总第429****篇**

**2020年 第53篇**

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVLR21NicmyQxcmiaqQ2KOJJj2JLwgJL4KSbo7CcuMF1hLf4xFjGQiaDRhSPyERxWGChWYP47Oc4sKGA/640?wx_fmt=png "undefined")

会话推荐是推荐领域的一个子分支,  美团平台增长技术部也在该领域不断地进行探索。不久前，该部门提出的跨会话信息感知的时间卷积神经网络模型CA-TCN被国际会议ICDM NeuRec Workshop 2020接收。本文会对论文中的CA-TCN模型进行介绍，希望能对从事相关工作的同学有所帮助或者启发。

ICDM的全称International Conference on Data Mining，是由IEEE举办的世界顶级数据挖掘研究会议，该会议涵盖了统计、机器学习、模式识别、数据库、数据仓库、数据可视化、基于知识的系统和高性能计算等数据挖掘相关领域。其中ICDM NeuRec Workshop旨在从应用和理论角度系统地讨论推荐系统的浅层和深层神经算法的最新进展，该Workshop征集了有关开发和应用神经算法和理论以构建智能推荐系统的最新且重要的贡献。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNsq5ZRH4PrIvtIFAlZcoX82acSMd4cISMduOYXOC1Un96CJP1Jw2I1A/640?wx_fmt=png)

**背景**

在大数据时代，推荐系统作为系统中的基础架构，开始扮演着越来越重要的角色，推荐系统可以为用户挑选出自己感兴趣的商品或者内容，从而来减少因信息爆炸带来的一些影响。目前，业界提出的很多推荐模型取得了巨大的成功， 但是大部分推荐方法常常是需要根据明确的用户画像信息进行推荐，然而在一些特定的领域，用户画像的信息有可能无法被利用。

为了解决这个问题， 会话推荐（Session-based Recommendation）任务被提了出来，会话推荐任务是根据用户在当前会话的行为序列去预测用户的下一个行为，而不需要依赖任何的用户画像信息[1]。目前，会话推荐任务已广泛应用于多个领域，例如下一个网页推荐、下一个POI推荐、下一个商品推荐等等。为了覆盖多个领域，所以“会话”的概念不仅限于交易，而是指一次或者一定时期内的消费或者访问的元素集合。

每一个会话（Session）都是一个item的转移序列，所以会话推荐任务可以很自然地被视为序列推荐任务，基于循环神经网络（RNN）的会话推荐模型[2]是应用的主流模型。但是基于RNN模型只对item之间的连续单向转移关系进行建模，而忽略了会话中其他item之间的转移关系。随着图神经网络的热点爆发，基于图结构的会话推荐模型如SR-GNN[3]、GC-SAN[4]被提出来，希望能够克服该点不足。基于图结构的会话推荐模型将会话的item转移序列构建成一个图结构，然后应用图神经网络模型来探索多个item之间复杂的转移关系。目前，基于图结构的会话推荐模型已经成为了State-of-the-art的解决方法，但它们仍然具有一定的限制， 观察如下：

* **观察 1**：几乎所有现存的会话推荐方法都仅仅关注于会话的内部信息，而忽略了跨会话的外部信息 （跨会话的相互影响），跨会话信息往往包含着非常有价值的补充信息，有利于更准确地推断当前会话的用户偏好。如下图所示，以Session 3中的Item\_3 Airpods为例， 现存的方法仅仅关注当前会话Session3中的Item\_9对Item\_3的影响而忽略了其他会话的影响。对于Session1而言, 用户可能具有买耳机的意图而进行同品类比较，所以item\_2和item\_4会对item\_3产生一个品类的影响；对于Session 2而言, 用户可能比较喜欢Apple品牌，所以item\_5和item\_6会对item\_3产生一个品牌的影响。根据上面的观察可知，在Item\_Level层次的跨会话影响对于更好地推断item的全局表示至关重要。同时，不同的会话之间也可能具有相似的用户意图和行为模式， 所以对于Session-Level的跨会话影响对于更准确地预测用户在当前会话中的下一个动作也起着非常重要的作用。

  ![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklN0cCJsIR4CNo0cEqmic537dNxKGNPnjAXt1JOGTZ7fv5YvY6kSib3p25g/640?wx_fmt=png "图1 跨会话item的Toy样例")

  图1 跨会话item的Toy样例
* **观察 2**：基于图结构的会话推荐方法在构建图的过程中，将出现在不同时间步的相同item都视为一个相同节点，这样会丢失序列中的位置信息，以至于不同的序列会话构建出的Session图结构是完全相同的。例如两个不同的会话Session S1:v\_i-->v\_j-->v\_i-->v\_k-->v\_j-->v\_k 与Session S2: v\_i-->v\_j-->v\_k-->v\_j-->v\_i-->v\_k，在下图2中，它们对应的图结构是完全相同的，这不可避免地限制了模型获得准确会话表示的能力。此外，在会话图构造中，仅仅直接连接的两个相邻item之间会建立边，意味着只有在当前item之前最后点击的item才是当前item的一阶邻居，如图2所示。但出现在一个相同会话中，即使没有被连续点击的item之间也具有一定的联系，所以图结构对于保留序列的长期依赖性具有有限的能力。相反，对于时序卷积神经网络（TCN）[5]模型，Causal Convolution使当前item的接受域中的items都可以直接作为一阶邻居进行卷积，并且具有的Dilated Convolution使得较远的items也可以直接作为一阶邻居对其产生影响。

  ![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNLXZVByWyBrYpCl2QUtia4xvq93oYicvFiceFSwaSw8ISX7xYpDpgKCW5g/640?wx_fmt=png "图2 图结构对于序列数据的建模示意图")

  图2 图结构对于序列数据的建模示意图

**相关工作介绍**

现有的会话推荐方法大致可以分为两类， 分别是基于协同过滤方法和基于深度学习方法：

* **基于协同过滤方法**：协同过滤方法是在推荐系统中被广泛使用的通用方法，协同过滤方法主要可以分为两大类：基于KNN查找方法和基于相似度建模方法。基于KNN查找方法是通过查找Top-K个相关的users或items来实现推荐，基于KNN查找方法可以通过查找与当前会话中最后一个item最相似的item来实现基于会话的推荐。最近，KNN-RNN[6]探索将RNN模型与KNN模型相结合，通过RNN模型来提取会话序列信息，然后查找在与当前Session相似的Session中出现的item来实现推荐。对于基于相似度建模的方法，CSRM[7]通过记忆网络将距离当前会话时间最近的m个会话中包含的相关信息进行建模，从而来获得更为准确的会话表示，以提高会话推荐的性能。
* **基于深度学习方法**：深度学习方法凭借其强大的特征学习能力在多个领域获得了令人满意的成果，对于会话推荐任务而言，循环神经网络RNN是一个直观的选择，可以利用其提取序列特征的优势来捕获会话内复杂的依赖关系。GRU4Rec[2]利用门控循环单元（GRU）作为RNN的一种特殊形式来学习item之间的长期依赖性，以预测会话中的下一个动作。之后的一些工作，是通过在基于RNN模型的基础上增加注意力机制和记忆机制等对模型进行了改进和扩展，其中NARM[8]探索了一种具有注意力机制的层次编码器，可以对当前会话中用户的序列行为和主要意图进行建模。最近， 随着图神经网络模型的飞速发展，出现了依赖图结构的会话推荐模型，SR-GNN首先提出将每个会话映射为一个图结构，并利用图神经网络模型GNN来建模item之间的复杂转移关系。之后，GC-SAN通过加入Self-Attention机制进一步扩展了SR-GNN模型，从而成为了State-of-the-art的解决方法。

CA-TCN模型与现有方法都存在着明显的差异。一方面，CA-TCN探索Item-Level和Session-Level的跨会话影响，以提高推荐性能，与其他的协同过滤方法的区别有两个：1. CA-TCN同时考虑了跨会话信息对item和Session不同层次的影响，而CSRM仅仅考虑了Session层次。2. CA-TCN构建了跨会话的全局Cross-Session item图和Session-Context图，通过GNN来探索复杂的跨会话影响。另一方面，与基于RNN和基于GNN的模型相比，CA-TCN模型克服了RNN模型无法并行以及图结构缺失位置和长期依赖信息的不足。

**跨会话感知的时间卷积神经网络模型（CA-TCN）**

**1. 模型整体框架**

网络的整体框架如下图3所示。给定会话序列数据，首先，我们构造一个Cross-Session Item-Graph来链接出现在不同会话中且有关系的items， 然后经过图神经网络输出包含全局信息的item向量。将得到的item向量输入到TCN模型中输出蕴含会话序列信息的item表示，根据Item-Level Attention机制来整合item的表示进而获得Session表示。此后，根据Session表示之间的相似度构建Session-Context Graph图以对Session层次的跨会话关系进行建模。最后，根据Session的表示以及item的表示进行预测。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNT2VdvdmJsYw3TCpzKvf1icjYoTMNOESzIveYWCKox7IGjPUPOAcrHAQ/640?wx_fmt=png "图3 CA-TCN模型总体框架图")

图3 CA-TCN模型总体框架图

**2. 跨会话Item图（Cross-Session Item-Graph）**

在第一阶段，我们构建Cross-Session Item-Graph有向图G\_ item，其中图中的每个节点代表一个item，（v\_s\_i, v\_s\_i+1）作为一条边，代表在会话s中用户在v\_s\_i之后点击了v\_s\_i+1。与现有方法相比，跨会话的G\_item图能够在所有的会话中出现的item之间建立链接， 因此G\_item不仅可以获取会话的内部信息，同时可以得到非当前会话的外部信息。G\_item的图的核心在于将所有的item放在了一起通盘考虑，然后用各个会话中的点击行为给item之间建立链接，不同会话的点击信息汇总在一起使得item之间的关系连接更加丰富。

为了充分利用G\_item图结构中的信息，CA-TCN将item的点击顺序和共现次数考虑在内。对于点击顺序，建立带有方向的邻接矩阵A\_in和A\_out来建模输入和输出方向。在邻接矩阵的基础上，根据item之间的共现次数为不同的边设置不同的权重，得到权重矩阵Weight\_in和Weight\_out。通过分配不同的权重，具有更多共现次数的item将发挥更大的作用，反之亦然，从而避免了噪音影响。

接下来，我们开发GNN模型来捕捉复杂的跨会话信息在item\_\_level的影响，GNN将每一个item映射为一个d维的embedding v∈R^d，得到包含跨会话信息的全局item向量（item\_vector）。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNeHc5srYLQPJibj9a2nXiaPGYu3FtFGp3IqHPgZd220Ku078A88ddQbFw/640?wx_fmt=png)

**3. 时间卷积神经网络模型（TCN Model）**

在第二阶段，我们采用时间卷积神经网络TCN来对会话序列进行建模，获取会话s的全局和局部表示。每一个会话s由多个item组成，输入会话s包含的item全局向量化表示（item\_vector）到时间卷积神经网络（TCN）模型中。对于会话中的每一个item进行因果和膨胀卷积的计算，进行会话序列信息的抽取。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNZQKkt9mSycrxwNYZkQS208fpU9fKzKUuG55MZjfyYRWkTZBnrD0JOg/640?wx_fmt=png)

采用会话中最后一个item的TCN输出作为会话s的局部（local）信息，以正确获取用户的当前兴趣：

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNwf06bP29yjElZoKLCibZx5sicxWG0zacdMJK6mwLefO3G80TS4GMcZLw/640?wx_fmt=png)

此外，采用会话s包含的items的表示以加权求和的方式得到会话的全局（global）表示（session\_vector），捕捉用户的全局信息。其中为了区分不同的item对于会话的影响程度不同，采用item层次注意力机制，使得会话表示更加专注于重要程度高的items。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNt655ZN3qwTMqyZMCicF22vMss9Uu7PBMI37xtb4DRajGiagicQiaicSJVzQ/640?wx_fmt=png)  
![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNYgn2eFTvIYicALNWib4GUFL8bMGPgSL9iaqBNNxbNp0BOTJXXGGaVCO1Q/640?wx_fmt=png)

**4. 会话上下文感知图（Session-Context-Graph）**

会话的local表示和global表示只专注于当前的会话，而忽略了会话间的影响。为了克服该不足，我们构建一个上下文感知的会话图结构（Session-Context-Graph）来考虑不同会话之间复杂的关系。

在会话图中，每一个节点代表一个会话s, 边的链接代表两个会话之间具有相似性。我们需要考虑的一个重要问题是如何决定一条边是否存在。对于每一对会话，我们计算其二者表示的相似度，然后采用根据相似度值的KNN-Graph[9] 模型来决定一个会话节点的邻居。在构建会话图结构之后，我们采用会话层的注意力机制以及图神经网络模型[10]来整合会话邻居节点对其自身的影响，同时会话层的注意力将会话之间的相似度也考虑在内，最终得到基于会话上下文敏感的会话表示。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNhy4Ib4S5NRn6aMWuiad7BRS6QibG6GP5eiczw23ibibMia2micoZ6BUTh3Olg/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNVliavibGibv2UZn3ibDS9hlianyKWZv4SFl0QBPMA2fQasaLLtG3YO2ib5hQ/640?wx_fmt=png)

**5. 点击预测**

为了更好地预测用户的下一个行为，我们采用融合函数将会话的局部表示，全局表示以及基于跨会话信息的表示进行融合，得到最终的会话表示：

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNKsKSviajx6rSXjDGNXpslYRIAowdIICqvFdyCtrEyn9jSOWB0nFqmicw/640?wx_fmt=png)

最后，我们根据item和session的表示去预测每一个候选item成为用户下一个点击的概率，根据概率进行逆序排序，筛选出概率值排在前预设位数对应的商品，作为用户偏好商品并进行推荐。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNBsn6dWiafe0rG8u8VPreznUc8ap06zMnEsjMiaAvllf3RTceHLB3yeYA/640?wx_fmt=png)

**实验评估**

为了评估所提出的CA-TCN的性能，我们使用了两个广泛应用的基准数据集，即Yoochoose和Diginetica， 模型性能评估结果如下表所示，CA-TCN优于目前的基于RNN以及图结构的State-of-the-art解决方法。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklN7hnR1AibPRd7xtjuw9A3646No54oQgHQSPyKPdXB2kd77ESLjzXCGDg/640?wx_fmt=png "表1 会话推荐任务的性能比较")

表1 会话推荐任务的性能比较

此外，我们进行消融实验以评估CA-TCN中每个组成部分的影响，组成部分包括TCN模型，Cross-Session Item-Graph和Session-Context graph。下图的实验结果证明了CA-TCN通过利用TCN模型和跨会话信息在会话推荐任务上都实现了性能的逐步提升。

* **CA-TCN(ca.exl)**：是CA-TCN的变体，它仅包含时间卷积神经网络、Cross-Session Item-Graph和Session-Context graph的跨会话信息不包含在内。
* **CA-TCN(sc.exl)**：是CA-TCN的变体，其中包含了Cross-Session Item-Graph的item-level的跨会话信息，但不包括session-level的Cross-Session Item-Graph。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsU7qN6QqZlKJ3GAgkkfJklNewy4BmibFZG2vcDqiaMicPmeu1eYPicHI9HyCGIaTibAsKu86Lic6Iicm7ibkw/640?wx_fmt=png "图4 CA-TCN模型不同组成部分的实验结果")

图4 CA-TCN模型不同组成部分的实验结果

**未来工作**

目前该论文已经申请了专利，后续我们将在美团多个业务线的会话推荐和序列推荐任务上进行探索落地。特别地， CA-TCN模型在电商数据集Yoochoose上进行了性能验证，证明CA-TCN模型适用于具有商品属性的电商场景，未来在“团好货”和“美团优选”等具有商品属性的业务线中都可以尝试应用。

**参考文献**

[1]. S. Wang, L. Cao, and Y. Wang, “A survey on session-based recommender systems,”arXiv preprint arXiv:1902.04864, 2019.

[2]. B. Hidasi, A. Karatzoglou, L. Baltrunas, and D. Tikk, “Session-based recommendations with recurrent neural networks,”arXiv preprintarXiv:1511.06939, 2015.

[3].S. Wu, Y. Tang, Y. Zhu, L. Wang, X. Xie, and T. Tan, “Session-based recommendation with graph neural networks,” in Proceedings of the AAAI Conference on Artificial Intelligence, vol. 33, 2019, pp. 346–353.

[4]. C. Xu, P. Zhao, Y. Liu, V. S. Sheng, J. Xu, F. Zhuang, J. Fang, and X. Zhou, “Graph contextualized self-attention network for session-based recommendation.” inIJCAI, 2019, pp. 3940–3946.

[5]. S. Bai, J. Z. Kolter, and V. Koltun, “An empirical evaluation of generic convolutional and recurrent networks for sequence modeling,”arXivpreprint arXiv:1803.01271, 2018.

[6]. D. Jannach and M. Ludewig, “When recurrent neural networks meet the neighborhood for session-based recommendation,” inRecSys ’17, 2017.

[7]. M. Wang, P. Ren, L. Mei, Z. Chen, J. Ma, and M. de Rijke, “A collaborative session-based recommendation approach with parallel memory modules,” in Proceedings of the 42nd International ACM SIGIR Conference on Research and Development in Information Retrieval, 2019, pp. 345–354.

[8].J. Li, P. Ren, Z. Chen, Z. Ren, T. Lian, and J. Ma, “Neural attentive session-based recommendation,” in Proceedings of the 2017 ACM on Conference on Information and Knowledge Management, 2017, pp. 1419–1428.

[9]. W. Dong, C. Moses, and K. Li, “Efficient k-nearest neighbor graph construction for generic similarity measures,” in Proceedings of the 20thinternational conference on World wide web, 2011, pp. 577–586.

[10].P. Veliˇckovi ́c, G. Cucurull, A. Casanova, A. Romero, P. Lio, and Y. Bengio, “Graph attention networks,”arXiv preprint arXiv:1710.10903, 2017.

**作者信息**

本文作者叶蕊、张庆、恒亮，均来自美团平台增长技术部。

----------  END  ----------

**招聘信息**

美团用户增长技术部，美团用户增长核心团队，长期招聘搜索、推荐、NLP算法及后台工程师，坐标北京。感兴趣的同学可投递简历至：luohengliang@meituan.com（邮件主题请注明：美团用户增长技术部）。

**也许你还想看**

**|**[CIKM 2020 | 一文详解美团6篇精选论文](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651755561&idx=2&sn=4b18f9ae1c8d6a791f9e5f0b062f176d&chksm=bd124d648a65c472cbeb6fbf91bb90a6933bffd4b505ff5c2dd86a25506cad977501edb7a4c4&scene=21#wechat_redirect)

**|** [ACM MM顶会论文 | 对话任务中的“语言-视觉”信息融合研究](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651753574&idx=2&sn=aa9b159cd0852f66a0fdaf0d0de6932f&chksm=bd12552b8a65dc3d95d95812c423e6794013a1d0ffc7a0f7b8c76ac40fead2691722b91bdd9a&scene=21#wechat_redirect)

**|**[推荐算法实践](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=203555773&idx=1&sn=cd0b997032cd9163f2a878defc8588a8&chksm=2f3edaf0184953e66a2132f5dee6934a7c804b8ccabbd0dc49188b1eddfa11c4c66f6d19183c&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsUrXicw2VXTQTVVN5yxXWEacsJ3aFxXFol84VVW89JYtgorr2aQnLz2YzwrVicCFXS7hEPGWvVJ6LWg/640?wx_fmt=png)