---
title: 'CausalMMM：基于因果结构学习的营销组合建模'
company: 阿里妈妈
tag: 广告
date: 2024-06-22
url: http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247492733&idx=1&sn=c48e2d610c3c5c9d19b55823e3a2f215&chksm=c1398be2d5ad7b1ff6744fa591f6e6950e5ee48ec0143d86d97942f52a23665d3d8714d93131&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
## 1. 摘要

在线广告中，**营销组合建模（Marketing Mix Modeling，MMM）** 被用于预测广告商家的总商品交易量（GMV），并帮助决策者调整各种广告渠道的预算分配。传统的基于回归技术的MMM方法在复杂营销场景下效果不尽如人意。尽管一些研究尝试使用因果结构进行更好的预测，但它们有一个严格的限制，即因果结构是事先已知且不可改变的。在本文中，我们定义了一个新的因果MMM问题，以自动从数据中发现可解释的因果结构，并得出更好的GMV预测结果。为了实现因果MMM，需要解决两个关键挑战：（1）因果异质性：不同类型广告商家的各渠道间因果关系结构差异很大。（2）营销响应模式：渠道投入对结果GMV的影响，例如在实证研究中发现的衰减效应和饱和效应。本研究认为，因果MMM需要动态地为不同广告商家发现营销行为间具体的因果结构，并且预测结果应符合先验已知的营销响应模式。因此，我们提出了CausalMMM，它在变分推断框架中集成了Granger因果，以测量不同渠道之间的因果关系，并在时态和饱和度营销响应模式的规范化下预测GMV。大量实验证明，CausalMMM不仅可以实现5.7%+的因果结构学习性能提高，在阿里妈妈真实数据上，还可以大幅提高GMV预测结果的准确性，为不同广告商家提供更可靠的GMV预测以及广告渠道间因果关系挖掘。

该项工作由阿里妈妈SDS团队和中科院计算所毕经平研究员与姚迪副研究员团队合作完成，基于该项工作整理的论文已被WSDM 2024接收，欢迎阅读交流。

**论文**：CausalMMM: Learning Causal Structure for Marketing Mix Modeling

**作者**：Chang Gong, Di Yao, Lei Zhang, Sheng Chen, Wenbin Li, Yueyang Su, Jingping Bi

**下载****（↓阅读原文↓）**：https://dl.acm.org/doi/10.1145/3616855.3635766

**延展阅读：**[CausalMTA: 基于因果推断的无偏广告多触点归因技术](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490382&idx=1&sn=de261291fbb1e49774df7ec8b8aa5feb&chksm=c0095d2df77ed43b7b9e115bb74b6e3bbe38bf204bb591508df95c2ae42f2f7087ae43be0a54&scene=21#wechat_redirect)

2. 背景

阿里妈妈目前已有丰富的广告产品，包含搜索、展示、直播、短视频、品牌等多种形态。广告主往往会将预算分配在不同广告渠道上，来覆盖用户转化旅程下的不同触点。广告主希望能精确衡量多渠道预算对整体销量的贡献，从而优化GMV、投入产出比（ROI）等目标，形成多渠道间预算投入的最优方案。

**营销组合模型**（Marketing Mix Modeling，简称MMM）是一种统计分析技术，帮助平台与广告主评估不同营销行为的效果以指导预算规划决策，并提高整体营销决策的有效性。MMM利用平台丰富的营销领域数据来训练模型，衡量各个营销渠道的影响，同时考虑店铺品牌、宏观经济、大盘等对最终转化数据有影响的非营销因素。基于对未来转化情况的预测，为后续广告投放计划提供全局预算调控指导，是在线数字广告系统中一个重要的提效手段。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicOv8S8XsG2MKYbs7u4EemUOBz5ppxsCjz7L4l9GzbDcDpbACVXNiaS2Qw/640?wx_fmt=png&from=appmsg)

图1：MMM输入-输出示意图

现有MMM工作大多可以分为两类：基于回归的方法、基于因果的方法。前者[1]基于不同渠道的消耗对GMV做回归，以回归系数解释各渠道重要性程度，但忽视了渠道之间的相互影响，影响模型的解释能力；后者[2]大多从先验知识出发预先定义因果结构，但忽略了不同商铺之间因果结构的异质性，难以用于实际场景中指导决策。因此，从传统MMM出发引入因果发现方法，动态挖掘不同店铺的因果结构，显得尤为重要。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicOxOHJpVkJEkpXfkMqBt1b4jHRVdgThfMic8cysicNvbn6iaP6I93nqBT0Q/640?wx_fmt=png&from=appmsg)

图2：MMM多渠道间的异质因果结构、上下文环境对GMV影响

然而，在MMM任务中动态挖掘因果结构并非易事，存在以下挑战：

**挑战一：因果异质性（Causal Heterogeneity）**

不同店铺特点和不同时期，渠道的因果结构和动态会有所不同。如图2(a)所示，影响销量的潜在因果驱动因素以及营销反应曲线，通常在不同品牌档次和营销事件中是异质的。与男装店铺相比，美妆店铺中品牌广告和页面浏览之间的因果效应更为关键。这种因果结构的异质性，在数据不平衡的情况下更加难以被传统MMM发现。

**挑战二：营销响应模式（Marketing Response Patterns）**

在前人的研究[3]中，已经验证了广告效果随投入发生响应的几种重要模式，如溢出效应和饱和效应。如图2(b)所示，广告投入的影响会随时间衰减，并随着投入的增加而饱和。除了因果结构，GMV曲线也受到一些背景变量的影响，如经济状况和竞争情况。因此，因果MMM中对预测目标与各变量的关心应该被精细建模，以满足各种营销响应模式。

## 3. 方法

为了解决这些挑战，我们提出了一种新的营销组合模型，称为CausalMMM，它可以同时处理因果异质性和营销模式，实现因果营销组合模型。总的来说，CausalMMM是一种基于图变分自编码器的方法，由两个关键模块组成：**因果关系编码器**（Causal Relational Encoder）和**营销响应解码器**（Marketing Response Decoder）。在因果关系编码器中，我们对店铺的历史数据进行编码，以Gumbel softmax采样生成特定的因果结构。基于因果结构，营销响应解码器被设计为满足营销响应模式的先验条件，并实现良好的预测性能。解码器中集成了顺序模型和S曲线转换，分别捕获了溢出和饱和效应。对于优化，CausalMMM直接用变分推理损失拟合历史数据，以端到端的方式学习参数。此外，CausalMMM具有理论保证，得到的因果结构是格兰杰因果[8]关系，且算法复杂度随店铺数目增加而线性增长。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicOQsMaS2VgeiazU5OfC1rAa59ZwTTg42WStMibWcHyAQVZ5WeF7ajG6cTQ/640?wx_fmt=png&from=appmsg)

图3：CausalMMM的Encoder-Decoder整体框架

### 3.1 因果关系编码器模块 Causal Relational Encoder

因果关系编码器旨在根据历史广告支出和营销目标，推断因果关系的可能性。具体来说，因果结构的联合分布可表示为，其中表示从节点i到j存在一条有向边(即)，且i≠j。由于事先不知道潜在的因果结构，我们从一个完全连通的图开始预测因果关系。利用图神经网络(GNN)在完全连通的图上传播信息，预测因果边[7]。因果关系编码器包括三个步骤，即成对嵌入、关系交互和Gumbel softmax采样。

我们首先通过广告消耗-营销目标间的成对嵌入在完全连通图中初始化边表示。成对嵌入的形式如下，这种方式以成对的方式捕捉了营销行为与目标间初始的局部信息：

在关系交互阶段，为了考虑与其他节点的关系交互，即全局信息，我们进一步计算边嵌入，其公式如下：

上述公式可以总结为通过编码器框架来推导结构分布，如下所示：

由于潜在分布是离散的，无法直接通过重参数化技巧进行反向传播学习模型参数，因此在训练过程中我们添加了Gumbel分布噪声[5]，来推断因果结构：

### 3.2 营销响应解码器 Marketing Response Decoder

解码器的目的是在推断的因果结构下建模营销响应，预测最终的营销目标。尽管基于上述推断的因果结构能够建模复杂的因果交互，但其他营销模式仍然不容忽视。营销组合建模中存在两个典型的假设：

* **时序营销反馈**（Temporal Marketing Response）：广告渠道的投资具有滞后性和时间衰减效应，即carryover effect。
* **饱和营销反馈**（Saturation Marketing Response）：广告渠道的投资收益具有边际递减效应。

如何系统地建模时间和饱和模式是一个不容忽视的问题。在大多数情况下，每个时间段内的渠道消耗相比于历史每个时间点累积的总消耗要更小。因此，我们首先建模时序模式，然后建模饱和模式。如图4所示，营销响应解码器由两个步骤组成，即时序营销响应模块和饱和营销响应模块。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicO3uzMibFO6wb782Gc7ib5dicMSZh6xLGqNMHfJvHhf4ZwbcMTkogbG205A/640?wx_fmt=png&from=appmsg)

图4：解码阶段的时序营销与饱和营销反馈建模

#### **时序营销响应模块 Temporal Marketing Response Module**

为了考虑时序特征，我们在原有的GNN消息传递机制中添加了序列模型。即，

其中，前一时间步的循环隐藏状态被用于消息传递机制。是这里使用RNN实现的序列模型，它以、当前值和前一个隐藏状态作为输入，捕捉每个营销变量的时间模式。

#### **饱和营销响应模块 Saturation Marketing Response Module**

递减收益对营销决策非常重要，因为它反映了渠道营销投资和目标收入之间的动态响应关系。在这个模块中，我们关注S-curve (Hill)变换[3]，这是建模饱和度最广泛使用的方法，我们采用基于梯度的方式来学习变换参数预测下一时刻营销目标。传统上，用于描述渠道对y的饱和效应的S-curve S(·)定义如下：

其中，α控制曲线在指数和S型之间的形状，γ表示响应曲线的拐点。它们的值受广告主、渠道、市场特性的影响。

我们通过神经网络对α和γ进行建模，输入为上下文变量C的向量。这为模型带来了更强的表示能力和可解释性[6]，因为包括店铺类型、事件和宏观趋势在内的附加信息可用于确定饱和曲线的形状。具体来说，营销目标的传统S曲线模型扩展为以下形式：

其中，fγ(·)表示用于计算市场拐点的神经网络，fα(·)是一个神经网络，其输出控制曲线在介于指数和S型之间的形状。在这个模块中，神经网络的模型能力和S曲线的显式表达能力被集成在了一起，已互补取得更好的预测效果。

基于上述两个模块，我们可以得出，分别刻画了d维渠道上的营销行为和营销目标的预测值。最终的基于历史的成对时间序列，对下一时刻多渠道、营销目标值的预测概率如下所示：

其中，σ是固定的方差项。对于多个时间步的预测，结果会以递归的方式进行调用预测，即：

### 3.3 变分优化 Variational Inference for Optimization

这一节给出了基于变分推理的优化过程。上面详述的和的参数可以根据以下内容导出：

且损失函数可以改写为变分下界（variational lower bound）：

其中，第一项是拟合数据的负对数似然，第二项是正则化的结构先验分布的KL散度。

## 4. 实验

本文分别在具有已知因果结构的仿真数据集与阿里妈妈真实数据集上实验。本文对比了CausalMMM模型与7个基准模型的实验情况，基准模型可分为两类，时序因果发现方法：Linear Granger[9]，NGC[10]，GVAR[11]，InGRA[12]；以及传统用于MMM与GMV预测的方法：LSTM[13]，Wide&Deep[14]，BTVC[4]。此外，本文还对比了三个消融方法（CM-FULL，CM-MARKOV，CM-RW）。

图5是不同模型在不同变量数目、不同时间步长、不同因果异质性下因果发现的性能，CausalMMM在三类不同设定下都有更好的表现。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicOf1sgar2o09Gnh3iaEoqB4oPcjFcVuCFV9icJMQtLLBxu9MzdxEcTZXQA/640?wx_fmt=png&from=appmsg)

图5：不同模型在不同参数下仿真数据集的预测效果

图6是GMV预测的MSE结果，比较了不同预测步长(1步、7步、30步)下各种方法的表现。我们可以观察到：

(1) 在所有比较的方法中，BTVC在M=30时表现最好，这可能归因于它明确引入了趋势和季节性信息的有益作用。

(2) 我们提出的CausalMMM在M=7时取得了最佳性能，在M=1和M=30时也达到了第二好的表现，这体现了该方法的有效性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicOtPh6vYZ72pGicmdrjqCdqJlS2MMcDUI9jE0omDTDEhYtWDF4UB5M2rg/640?wx_fmt=png&from=appmsg)

图6：CausalMMM对比因果发现、传统预测、消融方法在阿里妈妈数据上的GMV预测效果

图7可视化了在真实数据集中一家美妆店铺学习到的因果结构。我们展示对比了CausalMMM和之前最好方法GVAR学习到的11个营销渠道、页面浏览量(PV)以及营销目标(即GMV)的因果结构。在这些营销渠道中，前六个(即x-brand-0, ..., x-feed)是品牌广告渠道，旨在提高用户的认知和兴趣。相反，剩余的5个(即x-live, ..., x-effect)是效果渠道，用户在这些渠道更可能采取行动并实现转化。我们可以观察到，从品牌渠道到PV，再从PV到效果渠道存在因果关系。这些结果与营销领域专家的知识一致，并且与营销漏斗效应的结论一致。我们的方法还发现了一些有意义的关系，包括x-brand-1到x-search-1/2，表明在外部视频网站投放广告会导致电商平台上的搜索量增加。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48ZZL5O9m2LCgL1sb6GDBzicOKjgH0zYGBibXicANGP2ZO6gVEsvk54NMk5t2CXSCph6OnysTcbdaHv6w/640?wx_fmt=png&from=appmsg)

图7：CausalMMM与GVAR在阿里妈妈数据上对广告渠道因果结构的学习

## 5. 总结

MMM模型评估了不同营销行为下的营销效果，能够帮助商家从全局视角优化广告资源投放，从而提升整体营销收益。本文定义了因果营销混合模型(Causal MMM)的问题，该模型推断每个广告商家下各渠道间因果结构，并学习从渠道支出到GMV预测的映射关系。为了建模因果异质性和营销响应模式，我们提出了CausalMMM模型，该模型既能从异构数据中学习因果结构，又能建模营销响应模式。CausalMMM使用因果关系编码器和营销响应解码器。在仿真数据集和电商平台的实际商业数据上的实验结果表明，CausalMMM优于基线模型，并在应用中表现良好。

## ▐ 关于我们

🏷 **阿里妈妈SDS（Strategic Data Solutions）**团队致力于用数据让商家和平台的增长战略更加科学有效。我们为阿里妈妈全线广告客户提供营销洞察、营销策略、价值量化及效果归因的技术服务。我们将持续在数字营销领域MTA、MMM等方向进行探索和落地，欢迎各业务方关注与合作。同时，真诚欢迎感兴趣的同学和我们取得联系、互相交流。

**联系邮箱**：alimama\_tech@service.alibaba.com

📝 **CausalMMM**是阿里妈妈SDS和中科院计算所毕经平、姚迪老师团队多年合作的共同成果。双方不仅在MTA、MMM等学术领域做出了创新成果，也根据阿里独特的电商业务场景做了针对性的适配和优化，最终在学术研究与实际业务都取得满意的结果。毕老师的课题组围绕时序数据智能、网络智能、AI算法安全等领域开展研究，面向国家权益保障、国家网络与信息安全等国家重大战略需求，承担了多项国家科技重大专项、国家自然科学基金、国防预研项目和研制项目等重大项目。近三年来，课题组在KDD、WWW、ICDE、TKDE、TON等期刊会议上累计发表CCF A类论文十余篇。欢迎感兴趣的同学合作交流。

**联系邮箱**：yaodi@ict.ac.cn

## ▐ Reference

[1] Richard Wigren and Filip Cornell. 2019. Marketing Mix Modelling: A comparative study of statistical models.

[2] Aiyou Chen, David Chan, Mike Perry, Yuxue Jin, Yunting Sun, Yueqing Wang, and Jim Koehler. 2018. Bias correction for paid search in media mix modeling. arXiv:1807.03292 (2018).

[3] Yuxue Jin, Yueqing Wang, Yunting Sun, David Chan, and Jim Koehler. 2017. Bayesian methods for media mix modeling with carryover and shape effects. (2017).

[4] Edwin Ng, Zhishi Wang, and Athena Dai. 2021. Bayesian Time Varying Coefficient Model with Applications to Marketing Mix Modeling. In AdKDD'21 Workshop.

[5] Eric Jang, Shixiang Gu, and Ben Poole. 2017. Categorical Reparameterization with Gumbel-Softmax. In 5th International Conference on Learning Representations, ICLR'17.

[6] Kui Zhao, Junhao Hua, Ling Yan, Qi Zhang, Huan Xu, and Cheng Yang. 2019. A Unified Framework for Marketing Budget Allocation. In KDD'19. ACM, 1820–1830.

[7] Thomas N. Kipf, Ethan Fetaya, Kuan-Chieh Wang, Max Welling, and Richard S. Zemel. 2018. Neural Relational Inference for Interacting Systems. In ICML'18, 2693–2702.

[8] Sindy Löwe, David Madras, Richard Z. Shilling, and Max Welling. 2022. Amortized Causal Discovery: Learning to Infer Causal Graphs from Time-Series Data. In CLeaR'22, 509–525.

[9] Andrew Arnold, Yan Liu, and Naoki Abe. 2007. Temporal causal modeling with graphical granger methods. In KDD'07. ACM, 66–75.

[10] Alex Tank, Ian Covert, Nicholas J. Foti, Ali Shojaie, and Emily B. Fox. 2022. Neural Granger Causality. In TPAMI'22, 4267–4279.

[11] Ricards Marcinkevics and Julia E. Vogt. 2021. Interpretable Models for Granger Causality Using Self-explaining Neural Networks. In ICLR'21.

[12] Yunfei Chu, Xiaowei Wang, Jianxin Ma, Kunyang Jia, Jingren Zhou, and Hongxia Yang. 2020. Inductive Granger Causal Modeling for Multivariate Time Series. In ICDM 2020, 972–977.

[13] Sepp Hochreiter and Jürgen Schmidhuber. 1997. Long Short-Term Memory. Neural Comput. 9, 8 (1997), 1735–1780.

[14] Heng-Tze Cheng, Levent Koc, Jeremiah Harmsen, Tal Shaked, Tushar Chandra, Hrishi Aradhye, Glen Anderson, Greg Corrado, Wei Chai, Mustafa Ispir, Rohan Anil, Zakaria Haque, Lichan Hong, Vihan Jain, Xiaobing Liu, and Hemal Shah. 2016. Wide & Deep Learning for Recommender Systems. In RecSyS'16. ACM, 7–10.

END

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

****也许你还想看****

[****丨****CausalMTA: 基于因果推断的无偏广告多触点归因技术](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490348&idx=2&sn=52e933a5cfb385bf1a52ea3d26baeaf0&chksm=c0095d4ff77ed4590be814b46c8339d2ab76d90ea93a950044b6f5e2743048f1437724cd9b48&scene=21#wechat_redirect)

[****丨****](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247491805&idx=1&sn=7cf29232a0773879f402c15c3a29ba80&chksm=c00aa6bef77d2fa8f60a27aa2a06615aa9090bed04674b24081ceb917e06788b86d51f2dbedd&scene=21#wechat_redirect)[【阿里妈妈营销科学系列】第六篇：营销组合模型MMM](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490348&idx=2&sn=52e933a5cfb385bf1a52ea3d26baeaf0&chksm=c0095d4ff77ed4590be814b46c8339d2ab76d90ea93a950044b6f5e2743048f1437724cd9b48&scene=21#wechat_redirect)

[****丨****](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247491805&idx=1&sn=7cf29232a0773879f402c15c3a29ba80&chksm=c00aa6bef77d2fa8f60a27aa2a06615aa9090bed04674b24081ceb917e06788b86d51f2dbedd&scene=21#wechat_redirect)[广告营销场景下的隐私计算实践：阿里妈妈营销隐私计算平台SDH](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490415&idx=1&sn=2e4ce343d0c95fa44f5bc6d76dd6987e&chksm=c0095d0cf77ed41a437b392b0cce12cc6312f3275a3ab85f175da2bc8f3fcc3bc43a086b594b&scene=21#wechat_redirect)

[****丨****](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247491805&idx=1&sn=7cf29232a0773879f402c15c3a29ba80&chksm=c00aa6bef77d2fa8f60a27aa2a06615aa9090bed04674b24081ceb917e06788b86d51f2dbedd&scene=21#wechat_redirect)[开放下载 | 阿里妈妈营销科学系列上线啦！](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490360&idx=1&sn=f3f2b6b368d6f1484c894c4bf6f02234&chksm=c0095d5bf77ed44d8667278a78c9646a46c2d9c4f59e8984d4ff32d947766c10e964f2dacba7&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

喜欢要“分享”，好看要“点赞”哦ღ~