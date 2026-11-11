---
title: 'ICLR 2021 | 美团AutoML论文：鲁棒的神经网络架构搜索 DARTS-'
company: 美团
tag: 搜索
date: 2021-03-25
url: http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651761213&idx=2&sn=250afb8a82c92d53b4b6d44667b7fd95&chksm=bd1273708a65fa66d4aa4bdba3ab7eb2108107a71cdf9c7f52a9bead15a6f14ad262105628d4#rd
account: 美团技术团队
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsUrXicw2VXTQTVVN5yxXWEacdY1ZdxTH195Pgibtib8EENJRMia3tzEnyVfgyfAgRibMssKqwlE186TLSw/640?wx_fmt=png)

**总第441****篇**

**2021年 第011篇**

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVLR21NicmyQxcmiaqQ2KOJJj2JLwgJL4KSbo7CcuMF1hLf4xFjGQiaDRhSPyERxWGChWYP47Oc4sKGA/640?wx_fmt=png "undefined")

高质量模型的设计和更新迭代是当前 AI 生产开发的痛点和难点，在这种背景下，自动化机器学习（AutoML）应运而生。2017年，谷歌正式提出神经网络架构搜索（Neural Architecture Search，NAS），并成为 AutoML 的核心组成部分。美团技术团队也对AutoML领域进行了积极探索，本文系美团与上海交通大学合作的一篇被深度学习顶会 ICLR 2021 收录的论文解读。

## 背景

美团日益增长的用户侧和商家侧业务对人工智能（AI）技术有着非常广泛和强烈的诉求。从用户角度出发，美团 AI 在外卖之外，有到店消费、酒店旅游等200多个生活服务场景，均需要 AI 来提升用户体验。从商家角度出发，美团 AI 将帮助商家提高效率、分析运营状况，比如能对用户评论进行细粒度分析，来刻画出商家服务现状、商家竞争力分析，以及商圈洞察等等，为商户提供精细化经营建议。

目前，美团 AI 涉及的研发领域，包括自然语言理解、知识图谱、搜索、语音识别、语音生成、人脸识别、文字识别、视频理解、图像编辑、AR、环境预测、行为规划、运动控制等。AI 技术在这些场景中落地的两个关键部分是规模化的数据和先进的深度学习模型，其中高质量模型的设计和更新迭代是当前 AI 生产开发的痛点和难点，亟需自动化技术来辅助并提升生产效率。在此情景下应运而生的技术叫做自动化机器学习（AutoML）。AutoML 被认为是模型设计的未来解决方案，能够将 AI 算法工程师从手动设计的繁复试错中解放出来。

谷歌 2017 年正式提出神经网络架构搜索（Neural Architecture Search，NAS）[1] 用于自动化生成模型架构，这项技术即被业界寄予厚望，成为 AutoML 的核心组成部分。凭借日益增强的算力和持续迭代的 NAS 算法，视觉模型在架构层面诞生了像 EfficientNet、MobileNetV3 等影响力深远的系列模型，NAS 也应用到了视觉、NLP、语音等领域的很多方向 [2,3]。NAS 作为生成 AI 模型的 AI，其重要意义不言而喻。美团在 NAS 方向也开展了深入性的研究，对该领域保持着积极的探索。

本文介绍美团和上海交通大学合作的文章 DARTS-[4]，该文即将发表在 ICLR 2021 顶会上。ICLR （International Conference on Learning Representations）全称是国际学习表征会议，2013 年由两位深度学习大牛、图灵奖得主 Yoshua Bengio 和 Yann LeCun 牵头创办。ICLR 成立至今仅七年，但它已得到学术界的广泛认可，被认为是“深度学习领域的顶级会议”。ICLR 的 h5 指数为 203，在所有科学出版物中排名第 17，超过了 NeurIPS、ICCV 和 ICML。本届 ICLR 共有 2997 篇论文提交，最终接收 860 篇，包括 53 篇 Oral（接收率 6%），114 篇 Spotlight，693 篇 Poster，接收率为 28.7%。

## 神经网络架构搜索简介

神经网络架构搜索（NAS）的主要任务是如何在有限时间和资源下搜索得到最优的模型。NAS 主要由搜索空间、搜索算法、模型评估三部分组成。NAS 最早在视觉分类任务中验证，在分类任务中常见的搜索空间分为基于子结构单元（Cell）和基于子结构块（Block）两种，前者的特点是具有丰富的图结构，将相同的单元串联再组成最终的网络。后者是直筒型的，搜索的焦点就在于每层子结构块的选取。

按搜索算法分类，NAS 主要包括基于强化学习（Reinforcement Learning，RL）、基于遗传算法（Evolutionary Algorithm，EA）、基于梯度优化（Gradient-Based）的方法。RL 方法通过生成并评估模型来获取反馈，根据反馈来调整生成的策略，从而生成新的模型，循环这一过程直到最优。EA 方法将模型结构编码为可以交叉和变异的“基因”，通过不同的遗传算法来获取新一代的基因，直到达到最好。EA 方法的优点在于可以处理多种目标，比如一个模型的优劣有参数量、计算延迟、性能指标等多个考察维度，EA 方法便很适合在多个维度进行探索和演进。但 RL 和 EA 均比较耗时，主要受限于模型评估部分，一般采取全量、少量训练的方法。最新的 One-Shot 路线采用训练一个包含所有子结构的超网来评估所有子网的方式，可以从很大程度上提高 NAS 的效率。但同期，基于梯度优化的 DARTS 方法更为高效，成为当下 NAS 方法主流的选择。

DARTS 由卡耐基梅隆大学（CMU）的研究者刘寒骁等人提出，全称为可微分的神经网络架构搜索（Differentiable Architecture Search， DARTS） [5] ，大幅提高了搜索效率，受到了业界的广泛认可。可微分方法（DARTS）基于梯度优化，它首先其定义了一个基于有向无环图（DAG）的子结构（Cell），DAG 有四个中间节点（下图 Figure 1 中灰色方框），每条边有多个可选算子（由不同颜色的边表示），通过 softmax 加和不同边的结果作为到下个节点的输入。堆叠这样的子结构可以形成网络的主干。

DARTS 将搜索过程看作对堆叠而成的主干网络（也称为超网，或过参数化网络）的优化过程。这里每条边被赋予了不同的结构权重，并和网络权重一起交叉进行梯度更新。优化完成后结构权重大（由粗线条表示）的作为最终子网的算子，并将该子网作为搜索结果（Figure 1d 展示了最终的 Cell 结构）。这个过程（ Figure 1 从 c 到 d）将连续的结构权重硬性截断为离散值，比如 0.2 变为 1， 0.02 变为 0，而这样会产生所谓的离散化偏差（Discretization Gap）。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wEG0w2MB0S9gcWNJB7LuwmrZ6gicWFXiaXEtGbbM9ZZ5LAxAoB3CeibNsA/640?wx_fmt=png)

### 神经网络架构搜索的难点

简单总结目前神经网络架构搜索主要需要解决的难点在于：

* 搜索过程的**高效性**：搜索算法耗费的计算资源和时间要在可接受的范围，从而可以在实践中得到广泛的应用，直接支撑面向业务数据集的模型结构搜索；
* 搜索结果的**有效性**：搜索得到的模型要在多个数据集上有很好的性能，且又很好的泛化性能和领域迁移能力，比如搜索得到的分类主干网可以很好地迁移到检测和分割任务，并且有很好的表现；
* 搜索结果的**鲁棒性**：在具有有效性的同时，多次搜索的结果要相对稳定，即提高搜索的可靠性，降低试错成本。

### 可微分方法的缺点和改进方法

可微分神经网络架构搜索方法的不足之处就是鲁棒性较差，容易产生性能崩塌，即搜索过程中的超网性能表现很好但推断出的子网存在大量的跳跃连接（Skip Connection），严重削弱了最终模型的性能。基于DARTS 涌现出了非常多的改进工作，比如 Progessive DARTS[6]，Fair DARTS[7]，RobustDARTS[8]，Smooth DARTS[9] 等。其中， ICLR 2020 满分论文 RobustDARTS 提出用 Hessian 特征根作为衡量 DARTS 出现性能崩塌的征兆，但计算特征根又非常耗时。而且在标准的 DARTS 搜索空间下，RobustDARTS 在 CIFAR-10 数据集上的搜索得到的模型性能并不突出。这促使我们思考怎么提高鲁棒性，同时又提高有效性。针对这两个问题，业内有不同的分析和解决方法，代表性的分别是 Fair DARTS （ECCV 2020） 、 RobustDARTS （ICLR 2020） 和 Smooth DARTS （ICML 2020）。

Fair DARTS 观察到大量跳跃连接的存在，并着重分析了其可能的产生原因。文章认为，跳跃连接在可微分的优化过程中，存在竞争环境下的不公平优势（Unfair Advantage），导致跳跃连接容易在竞争中胜出。因此，FairDARTS 提出放宽竞争环境（Softmax 加和）为合作环境（Sigmoid 加和），使得不公平优势带来的影响失效。最终选取算子方式也与 DARTS 不同，通过采取阈值截断，比如选取结构权重高于 0.8 的算子，此时跳跃连接可以和其他算子同时出现，但这样等同于增大了搜索空间：原先的子网中，两个节点之间最终只选取一个。

RobustDARTS（简称 R-DARTS） 通过计算 Hessian 特征根来判断优化过程是否出现崩塌，文章认为，损失函数地貌（Loss Landscape）存在尖锐的局部最优点（Sharp Local Minima，Figure 5a 右侧点），离散化过程（α\* 到 αdisc）会导致从优化较好的尖锐点偏移到优化较差的地方，从而导致最终模型性能下降。R-DARTS 发现这个过程和 Hessian 特征根关系密切 （Figure 5b）。因此可认为，Hessian 特征根变化幅度过大时优化应该停止，或者通过正则化手段来避免 Hessian 特征根产生大幅变化。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wErTtjVjmXXuN9IuBBeLj8UlLib5VaaI2gzkUtDLe2zksaDR8fzbeKeg/640?wx_fmt=png)

Smooth DARTS （简作 SDARTS）遵循了 R-DARTS 的判断依据，采取基于扰动的正则化方法，对 Hessian 特征根进行了隐式的约束。具体来讲，SDARTS 对结构权重给予了一定程度的随机扰动，使得超网具有更好的抗干扰性，同时对损失函数地貌有平滑作用。

## DARTS-

### 跳跃连接的工作机制分析

我们首先从跳跃连接的工作机制进行分析性能崩塌现象。ResNet [11] 中引入了跳跃连接，从而使得反向传播时，网络的浅层总包含对深层的梯度，因此可以缓解梯度消失的现象。如下式（i ，j，k 表示层数，X 为输入，W 为权重，f 为计算单元）。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wmqiaGhoGSib82gSpu4DS04mUAaEFT6IJVnJTQOp1sE66gfPmH1dhjjEA/640?wx_fmt=png)

为了理清跳跃连接对残差网络性能的影响，我们在 ResNet 上做了一组验证性试验，即对跳跃连接加上可学习的结构权重参数 β，此时我们的梯度计算则变为下式：

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wzKY6LrS4ZOd7untrJjYBReyaNAJsACq94OUYTJuQ9cvgmWFFia5qMEw/640?wx_fmt=png)

三次实验分别初始化 β 为 {0, 0.5, 1.0}，我们发现 β 总能快速增长到 1 附近（Figure 2）来增大深层梯度向浅层的传递，进而缓解梯度消失的现象。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVzzgER0oCgNL3SCmZdkib9M0WaQic8ARhiamJX1iao2OSia3oxUHt5H8o5iawdTyIYghZWkvfWMBMz51cA/640?wx_fmt=png)

在 DARTS 中，跳跃连接跟 ResNet 类似，当具有可学习参数时，其结构参数也具有这种趋势，从而促进超网的训练。但正如 Fair DARTS [7] 提到的，同时带来的问题就是对其他算子来讲跳跃连接存在不公平优势。

### 解决崩塌的办法：增加辅助跳跃连接

根据上述的分析，DARTS- 指出跳跃连接（下图 Figure 1 中 Skip）存在双重作用：

* 作为可选算子本身，参与构建子网。
* 与其他算子形成残差结构，从而产生对超网优化产生促进作用。

第一个作用是预期其要发挥的作用，从而与其他算子公平竞争。第二个作用是跳跃连接具有不公平优势的原因，促进了优化，但干扰了我们对最终搜索结果的推断。

为了将第二个作用剥离出来，我们提出额外增加一条跳跃连接（Auxiliary Skip），并使其结构权重 β 从 1 衰减到 0（简便起见，使用线性衰减），这样可以使得超网和子网保持结构上的一致性。Figure 1 （b）图示出了一个子结构中两个节点间的连接情况。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVzzgER0oCgNL3SCmZdkib9MSY0MMEUic9BwXuWJfMytDe3DaNY6OwGtP1RmeSPteUhlicf2sc2YNMEg/640?wx_fmt=png)

除了增加的辅助跳跃连接，DARTS- 优化过程和 DARTS 大同小异。首先根据 Figure 1 （b）构建超网，选取一种 β 衰减策略，然后采取交替迭代优化超网权重 w 和结构权重 α，具体见下面的算法描述（Algorithm 1）。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVzzgER0oCgNL3SCmZdkib9Mib1uuFG9flAoQlIYqYcNQY1X1tVScpGyjCv2YaJYYzKqa86OABQ1DkQ/640?wx_fmt=png)

在本方法中，我们去掉了用指示信号（Indicator）发现性能崩塌的做法，比如 R-DARTS 中的特征根，从而消除了 DARTS 的性能崩塌，因此命名为 DARTS-。另外根据 PR-DARTS [12] 的收敛理论来分析，辅助跳跃连接具有平衡算子间竞争的作用，且当 β 衰减后，算子间的公平竞争依然保持。

### 分析和验证

#### Hessian 特征根变化趋势

在 R-DARTS 以及 DARTS 采用的多个搜索空间下，DARTS- 发现了子网性能增长（Figure 4b）但 Hessian 特征根变化幅度过大（Figure 4a）的情形，这个结果成为了 R-DARTS 所提出原则的反例，即采用 R-DARTS 判定准则，我们会漏掉一些好的模型。这也说明了 DARTS- 可以带来不同于 R-DARTS 的模型结构。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wicNMCd1C5JN7bZmiayNzsgSKFoHpoJjvjqic8ic8snaERT0FTDwGiaq2uOA/640?wx_fmt=png)

#### 验证集准确率地貌

验证集准确率的地貌可以一定程度上说明模型的优化过程难易。DARTS （Figure 3a）在最优解附近范围的地貌相对陡峭，等高线比较疏密不均，而 DARTS- 则表现得舒缓平滑，等高线更为均匀。另外更为光滑的地貌也不容易出现尖锐的局部最优点，一定程度也减少了离散化偏差。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wkZXZPXemGInicxYVq33Ox7fhicpoYCialUiaz8xrWBe94Kv2STkSmqWCdw/640?wx_fmt=png)

### 实验结果

#### 模型结构

Figure 9 给出了我们在 DARTS 搜索空间 S0 和 Robust DARTS 搜索空间 S1-S4 得到的网络结构。Figure 10 是在 MobileNetV2 的搜索空间下 ImageNet 数据集上进行直接搜索的结果。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14woI7c5zBQD5Up501uwqugxQiateNnDwzCAluTu3L4TYyqFdmFrxDxK5A/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wGicGxwMr55icib966L5NC1MA7W2J2kQgLQruJGqPnR4hUDYCDUzsBPeRQ/640?wx_fmt=png)

#### 分类任务结果

在标准分类数据集 CIFAR-10 和 ImageNet 上 DARTS- 均取得了业界领先的结果，如下表所示：

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wm4RcaibicRbOia6pYEmNvuiaV8ZsTxtLP4Kwhbze6VJVsUFuhz3ZBluHBg/640?wx_fmt=png)

在 RobustDARTS 提出的检验鲁棒性的多个搜索空间 S1-S4 中，DARTS- 搜索得到的模型性能优于 R-DARTS 和 SDARTS。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wJkVUCS8a2hSwpUiaWhAZxrGIkkecrPtjH35dQSdTUHgcXB1u296po0Q/640?wx_fmt=png)

#### NAS 算法评测

NAS-Bench-201[10] 是用于衡量 NAS 算法的评测基准工具之一，DARTS- 也取得了优于其他 NAS 算法的结果，而且最好结果基本逼近了基准中最好的模型。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsXmQQA2wTiaFfUU2LQ7lk14wfoI5YEf29WdMXwnYH07WW733iauTQL2BpArnxAW2wkl1sMzGq939sJg/640?wx_fmt=png)

#### 迁移能力

DARTS-A 作为主干网在 COCO 数据集目标检测任务上也优于之前 NAS 模型的性能，mAP 达到了 32.5%。

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVzzgER0oCgNL3SCmZdkib9Mx4JS93QqzWelyLECbOscphlItLY1gRaUn3BUdXJxDz2WuBQWuGlFvw/640?wx_fmt=png)

综合来看，DARTS- 方法继承了DARTS 的高效率，且在标准数据集、NAS 基准评测、R-DARTS 搜索空间中证明了其鲁棒性和有效性，在检测任务中也证明了其领域迁移的能力，从而印证了搜索方法本身的优越性，解决了当前神经网络架构搜索中的一些难题，将会对 NAS 研究和应用产生积极的推动作用。

## 总结及展望

本次美团在 ICLR 2021被收录的文章 DARTS-，重新了梳理 DARTS 搜索结果不够鲁棒的原因，分析了跳跃连接的双重作用，并提出了增加带衰减系数的辅助跳跃连接来对其进行分离的方法，使得内层原生的跳跃连接只表现其作为可选操作的功能。我们同时对 R-DARTS 所依赖的特征根进行深入分析，发现了其作为性能崩塌标志会出现反例的情形。未来 DARTS- 作为高效、鲁棒且通用的搜索方法，期望在其他领域任务和落地中得到更多的拓展和应用。关于文章的更多细节，请参考原文。实验代码已经在 [GitHub](https://github.com/Meituan-AutoML/DARTS-) 开源。

AutoML 技术可以适用于计算机视觉、语音、NLP、搜索推荐等领域，视觉智能中心 AutoML 算法团队旨在通过 AutoML 技术赋能公司业务、加速算法落地。目前该论文已经申请了专利，本文算法也集成到美团自动化视觉平台系统中，加速自动化模型生产和迭代。除了视觉场景外，我们后续将探索在搜索推荐、无人车、优选、语音等业务场景中的应用。

## 作者简介

祥祥、晓星、张勃、晓林等，均来自美团视觉智能中心。

## 参考文献

1. Learning Transferable Architectures for Scalable Image Recognition, <https://arxiv.org/abs/1707.07012>.
2. NAS-FPN: Learning scalable feature pyramid architecture for object detection， <https://arxiv.org/abs/1904.07392>.
3. Auto-deeplab: Hierarchical neural architecture search for semantic image segmentation， <https://arxiv.org/abs/1901.02985>.
4. DARTS-: Robustly Stepping out of Performance Collapse Without Indicators， <https://openreview.net/forum?id=KLH36ELmwIB>.
5. DARTS: Differentiable Architecture Search，  <https://arxiv.org/pdf/1806.09055.pdf>.
6. Progressive Differentiable Architecture Search: Bridging the Depth Gap between Search and Evaluation， <https://arxiv.org/pdf/1904.12760>.
7. Fair DARTS: Eliminating Unfair Advantages in Differentiable Architecture Search， <https://arxiv.org/pdf/1911.12126.pdf>.
8. Understanding and Robustifying Differentiable Architecture Search，<https://openreview.net/pdf?id=H1gDNyrKDS>.
9. Stabilizing Differentiable Architecture Search via Perturbation-based Regularization， <https://arxiv.org/abs/2002.05283>.
10. NAS-Bench-201: Extending the Scope of Reproducible Neural Architecture Search ，<https://openreview.net/forum?id=HJxyZkBKDr>.
11. Deep Residual Learning for Image Recognition， <https://arxiv.org/abs/1512.03385>.
12. Theory-inspired path-regularized differential network architecture search，<https://arxiv.org/abs/2006.16537>.

**阅读更多**

---

[前端](https://t.1yb.co/jo7r)**|**[算法](https://t.1yb.co/jsdG)**|** [后端](https://t.1yb.co/jsWK)**|**[数据](https://t.1yb.co/jqRZ)

[安全](https://t.1yb.co/jo7v)**|**[Android](https://t.1yb.co/jui4)**|** [iOS](https://t.1yb.co/jtXE) **|** [运维](https://t.1yb.co/jo7K)**|**[测试](https://t.1yb.co/jtsX)

----------  END  ----------

**招聘信息**

美团 AutoML 算法团队致力于研发业界一流的自动化机器学习技术，提升公司人工智能产品线的生产效率，服务业务包括视觉、无人车、语音、搜索推荐等。团队目前正在招聘 2022 届校招实习生，欢迎感兴趣的同学发送简历至：chuxiangxiang@meituan.com。

**也许你还想看**

**|**[美团里的科学家和外卖中的 AI](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651752194&idx=2&sn=f2108cee75503206554c02d050a20e79&chksm=bd125e4f8a65d7598fe48f048cc7a5713910b5eb6a28207bf6e41dc2e137de1a4ba32bd8e9a2&scene=21#wechat_redirect)

**|** [美团餐饮娱乐知识图谱——美团大脑揭秘](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651749520&idx=1&sn=e905e4ecefca3be58b46f59dcfb4b202&chksm=bd12a5dd8a652ccb499914b029b898651946e21b5d7acc3fc2229c7afbc3d2f490ba685cbef0&scene=21#wechat_redirect)

**|** [CIKM 2020 | 一文详解美团6篇精选论文](http://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651755561&idx=2&sn=4b18f9ae1c8d6a791f9e5f0b062f176d&chksm=bd124d648a65c472cbeb6fbf91bb90a6933bffd4b505ff5c2dd86a25506cad977501edb7a4c4&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsUrXicw2VXTQTVVN5yxXWEacsJ3aFxXFol84VVW89JYtgorr2aQnLz2YzwrVicCFXS7hEPGWvVJ6LWg/640?wx_fmt=png)