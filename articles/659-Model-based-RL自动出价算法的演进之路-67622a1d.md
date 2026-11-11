---
title: 'Model-based RL自动出价算法的演进之路'
company: 阿里妈妈
tag: 广告
date: 2025-01-09
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247494372&idx=1&sn=a4327f5a3523b4213c34901b69ff5ead&chksm=c14009c38d0e16356a3a2e859130d682120da3bda21ffb3b96c05214e8808dffcf9e7d0d4b0f&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
▐ 导读

近年来，强化学习自动出价算法已成为智能投放领域的标志性技术，然而其所存在的在离线不一致、线上数据覆盖空间受限等关键问题尚未被完全解决。在本文中，我们提出一种Model-based RL（MBRL）自动出价算法训练新范式，进一步缓解上述两点挑战。经过一年的迭代，MBRL自动出价算法已在阿里妈妈万相台无界版全站推场景、货品场景、关键词场景和精准人群推广场景中完成扩流，显著增强了投放效果。未来，在基于监督学习的预训练方法逐渐收敛的趋势下，MBRL以其高效的样本利用率与基于探索超越数据集的能力，将进一步赋能生成式自动出价算法，焕发新的活力。

## 1. 概述

近年来，出价产品智能化已经成为在线广告行业的主要发展趋势之一。广告主只需要表达预算、优化目标及拿量成本，自动出价（Auto-bidding）算法就会代表广告主在海量流量上进行自动化竞价，以满足广告主的营销诉求。然而每个广告主的竞价流量数量众多且复杂多变，自动出价算法需要找到一个能够在整个投放周期内满足设定成本并效果最优的出价序列，是一个复杂的序列决策问题。随着机器学习的发展，从19年开始，以擅长序列决策问题著称的强化学习（Reinforcement Learning，RL）算法逐渐用于自动出价算法中。强化学习以试错学习（Trial&Error）为基本思想，在没有明确的最优出价序列的监督信号条件下，通过学习不同出价序列的反馈数据，逐步优化出价策略。至今，强化学习出价算法已经在业界大规模落地，显著提高了投放效果。

### 1.1 强化学习自动出价算法的范式变迁

纵观强化学习自动出价算法的发展历程，整体上经过了由基于离线仿真器训练（Simulation-based RL Bidding，简称SBRL，代表算法USCB [1]等）到抛弃离线仿真器、直接利用线上真实数据训练（Offline RL Bidding，简称ORL，代表算法CQL [2]等）的范式转变\*（如图1中①和②所示）。众所周知，强化学习训练中的试错学习过程需要与问题对应环境交互以产生反馈样本，然而出于安全和效率考虑，线上竞价环境无法在强化学习训练中使用，因此一个自然的想法便是人为构建一个可以模拟线上竞价环境的离线仿真器用于训练，这就是SBRL范式。在19年到21年间的强化学习自动出价算法多采用SBRL范式进行训练。然而当时的离线仿真器多采用简单规则构建，与线上真实环境的gap很大，**在离线不一致问题**较为严重（见3.3.2实验1）。为缓解在离线不一致问题，从22年开始，一种主流的解决思路是能否抛弃离线仿真器、直接利用线上真实数据进行训练，这便是ORL范式的基本思路。然而线上真实数据集往往由单一的线上主模型产生，其覆盖的状态-出价空间有限，在没有离线仿真器可以进一步交互的条件下，ORL无法利用到数据集覆盖空间之外的状态-出价数据进行训练，**导致训练得到的自动出价策略通常被限制在线上真实数据集附近，优化幅度较小**（见3.3.2实验2）。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1Pialdw0bOGbvfdKicLEC7LvaVJYPxMY81LvWHXX7V4cTUZNJqTcbucHg/640?wx_fmt=png&from=appmsg)

图1. 强化学习自动出价算法的范式变迁。整体上其经过了由基于离线仿真器训练（SBRL）到抛弃离线仿真器、直接利用线上真实数据训练（ORL）的范式转变。本文提出了一种基于环境模型建模的新强化学习自动出价范式（MBRL）。

> \*图1展示的均为在没有进一步与线上竞价环境交互下的强化学习自动出价范式变迁。实际上，可以设计线上探索方法以扩充数据集&获得新反馈，这种线上探索的方法可以与上述每一种offline范式结合，升级为online的范式。online范式升级与图1展示的范式变迁正交，本文不做重点讨论，online范式的详细方法可见[3]。

### 1.2 MBRL自动出价算法演进之路Overview

23年10月，我们开始尝试基于环境模型的强化学习自动出价算法训练新范式（Model-based RL Bidding，简称MBRL）。如图1中③所示，MBRL的基本思路为：基于线上真实数据，利用深度学习训练一个泛化性较好的神经网络环境模型以模拟线上竞价环境，其所产生的数据在经过置信度处理后作为离线虚拟数据丰富训练集，与线上真实数据共同训练出价策略，构成 **“虚实融合”** 的训练新范式。MBRL避免了SBRL中对于离线仿真器的不精确（如果做精准会很复杂）的人工构建，通过深度学习实现对线上真实数据所包含竞价环境信息的提取，大幅缓解了在离线不一致问题；对比ORL范式，MBRL进行了丰富且可靠的训练数据扩充，打破了ORL中出价策略在只在数据集附近优化的束缚，为优化幅度的提升开拓了空间。

24年，我们将MBRL成功迁移到具有ROI约束的TargetROAS计划上，其中我们新增了Lagrange对偶梯度法计算ROI约束下的出价策略梯度，并利用神经网络环境模型提供梯度计算所需数据，**提出了具有收敛性理论保证的Lagrange-MBRL算法**。同年，我们针对MBRL训练中存在的问题进行技术打磨，大幅提升了其训练稳定性。

**至今，MBRL已经在阿里妈妈万相台无界版的货品场景、关键词场景、精准人群推广场景和全站推场景中完成扩流，在大盘覆盖计划中带来** **消耗 +3.5% / GMV +4.5%****的收益，显著增强了广告主的投放成效。**

## 2. Preliminary：自动出价问题建模

为了便于后续算法展开，在本节我们给出自动出价问题的形式化建模并描述了出价的调控过程。考虑一个广告主的单个投放计划在一个投放周期（设定为一天）内的投放过程，自动出价问题可以统一形式化为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1cdcKibpcJ7QMGF9scsZJc1LO6UFBVET8SFEQic2XhuqRjFiaGl46icPH5Q/640?wx_fmt=png&from=appmsg)

其中  代表第  个流量是否竞得  和  分别代表第  个流量的价值和竞得的扣费， 为第  个成本约束，  为广告主设定的预算。在本文中，我们主要考虑在阿里妈妈万相台无界版中消耗占比最多的两类自动出价问题：

* **BCB（Budget Constrained Bidding）问题**：只有预算约束，没有成本约束；
* **TargetROAS（Target Return on Ad Spend ）问题**：成本约束为ROI约束。

对于这两种问题而言，在第  个流量上的最优出价形式为 [1]，其中  是未知参数。基于此，我们设定投放周期内的**调控过程**为：在每个流量上采用上述出价形式，并且每隔固定的时间间隔对  进行一次调节，整个调控周期中共有  次  的调节。上述调控过程可以利用马尔可夫决策过程（Markov Decision Process，MDP） 进行建模，其中  为状态空间， 为动作空间：出价动作  即为  的调整幅度； 为状态转移函数，是由竞价环境决定的； 为奖励函数，针对BCB问题和TargetROAS问题需要进行不同设计。我们构建一个神经网络模型  用来学习每个时刻最优的  调整幅度，令  为神经网络的参数。我们称  为出价策略，也是最终要学习的目标。

下面我们将分别介绍针对阿里妈妈万相台无界版中消耗占比最多的BCB和TargetROAS两类计划的MBRL算法及其实验结果。

## 3. 针对BCB问题的MBRL算法

### 3.1 Overview

针对BCB问题的MBRL算法整体流程如图2所示：

* 首先，我们基于线上真实数据拟合一个**神经网络环境模型**，并且利用出价策略与环境模型进行大量交互以产生丰富的离线虚拟数据。得利于神经网络的泛化性，神经网络环境模型可以大幅降低离线虚拟数据的在离线不一致问题；
* 其次，离线虚拟数据会经过**置信度处理**，以进一步降低神经网络环境模型的不准确性对出价策略训练产生的负面影响。其中我们以环境模型的拟合方差来衡量离线虚拟数据的置信度，并对离线虚拟数据中的奖励函数进行正比于置信度的惩罚，从而避免环境模型的错误“乐观”（即对于奖励函数的高估）对出价策略训练带来误导；
* 最后，离线虚拟数据与线上真实数据混合，一起作为训练集对出价策略  进行“虚实融合”训练。训练中我们发现：利用传统的RL方法训练会使得出价策略的各种离线指标不收敛的情况，这为后续的模型挑选带来困难。经过分析认为这种不收敛是由于贝尔曼方程的自举误差带来的，尤其在利用缺乏状态转移偏差修正的离线虚拟数据训练的情况下，这种自举误差更为严重。为此，我们设计了**COMBO+MICRO的训练方法**对离线虚拟数据的状态转移偏差进行限制以缓解自举误差，提升了出价策略训练的稳定性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ11LYHOY7PVEj6ib0laiagic8HHhCVAehKqbibIgMpJgUxBJKy0RFycrnMdg/640?wx_fmt=png&from=appmsg)

图2. 针对BCB问题的MBRL算法整体流程。

### 3.2 算法模块细节

下面分别介绍神经网络环境模型、置信度处理机制和COMBO+MICRO训练方法这三个主要模块。

#### 3.2.1 神经网络环境模型

神经网络环境模型以状态 （或其历史序列）和出价动作 （或其历史序列）作为输入，输出奖励函数和下一时刻状态的高斯分布均值和方差，并通过重参数化的方式确定具体的奖励函数和下一时刻状态的预估值 和 。神经网络环境模型可以采用任意的网络结构，例如MLP、ResNet、Transformer等，拟合能力越强的网络结构越有助于提高环境模型的精度，也越有助于增强MBRL训练的出价策略  的性能。神经网络环境模型的训练是一个典型的监督学习问题，我们采用最大似然函数作为损失函数，并利用线上真实数据作为训练集，梯度更新其参数直到收敛，之后神经网络环境模型的参数便被freeze，在后续流程中不再变动。

3.2.2 置信度处理机制

为进一步降低神经网络环境模型预估的不准确性对策略训练带来的负面影响，我们对其产生的离线虚拟数据进行进一步的置信度处理。具体而言，在离线虚拟数据加入策略的训练集之前，我们对其中预估的奖励值施加一定的惩罚，由  变为 ，即

惩罚项

其中  代表惩罚项。这样做的目的是使得策略对线上真实数据集外的数据产生一定程度上的“悲观”，从而避免由于神经网络环境模型对状态空间中某些区域的错误乐观（即对奖励值的高估）而导致的策略性能下降，可以证明：利用置信度处理后的奖励  训练可以提升出价策略在真实竞价环境中性能的下界[4]。那么如何设计惩罚项  的具体形式呢？注意到由于神经网络往往在数据稠密的地方拟合效果好，方差小；在数据稀疏的地方拟合效果差，方差大，如图3所示，因此神经网络环境模型的拟合方差是一种天然的  选择。因此我们训练  个神经网络环境模型，让他们同时输出对于的奖励函数预测，并计算这些预测值的方差，记为 ，则惩罚项 的具体形式为：

其中  为常数。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ10ckZ4xQJk3qUO5CXkdcQszoUd1ic73pYEbdenbCeapdSVB1ZOaDY2yA/640?wx_fmt=png&from=appmsg)

#### 3.2.3 COMBO+MICRO训练算法

**Q值不稳定问题**：理论上任意RL算法均可以用于此处出价策略的训练，然而我们在实验过程中发现使用传统RL算法（例如SAC[3]）训练出价策略的各项离线指标抖动较大，其中出价策略的Q值仍可能会不合理的持续升高，甚至无法收敛（如图4所示），这对策略的挑选带来影响。经过分析我们认为这种不收敛性来自于Q函数TD-loss中贝尔曼算子带来的误差累计。具体而言，TD-loss为：

其中  是基于当前Q函数估计的贝尔曼算子，公式为：

可以看到，TD-loss实际是一个以  为近似groundtruth的MSE-loss，而  中的第二项  就是Q函数本身，即Q函数的更新是自举的，Q函数的不准确性本身会导致其更新的不准确性，尤其在训练初期，Q函数不准确度很高，传统RL算法缺失了对Q函数本身的限制。此外，**在置信度处理时我们仅对神经网络环境模型产生的奖励函数进行处理，而没有对其状态转移估计  的不准确性进行处理**，神经网络环境模型可能产生不合理的远离线上真实数据集的 ，导致  值较高，从而带来Q函数的高估和不收敛问题。

**COMBO+MICRO训练算法**：针对Q值仍可能存在的高估和不收敛问题，我们参考了COMBO算法 [6]和MICRO算法[7]的思路，对两者进行融合，在原来Q函数损失函数的基础上做如下两项改动：

* **COMBO**：对线上真实数据集之外的数据(s,a)进行均匀采样 ，并打压其Q值。由于Q值是后续累计奖励的期望，因此COMBO可以看成是对置信度处理机制的增强。
* **MICRO**：考虑  的不确定性对  的影响，避免神经网络环境模型的不合理的  预估带来Q函数高估。具体而言，我们对神经网络环境模型预估的  进行采样，取最小的Q值作为  中的第二项，即 。

结合上述两项改动，得到最终的Q函数更新函数如下所示（红色为新增部分）：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1mF6gbwib3acUDlPk6cfjpOMLcictwck87Sicbzkmr2XXoxPIEK3z8h6Eg/640?wx_fmt=png&from=appmsg)

其中  为正则化系数，用于平衡真实数据集中的状态动作对和环境模型生成的状态动作对之间的保守性， 是均匀分布， 是真实数据集， 是混合数据集，由线上真实数据和神经网络环境模型生成的离线虚拟数据组成， 为 分布：若 ，则 ；否则  是神经网络环境模型的预估值， 从其输出的高斯分布中采样。

### 3.3 实验结果

#### 3.3.1 线上实验

MBRL在阿里妈妈万相台无界版货品场景、关键词场景、精准人群推广场景的BCB计划上均取得了显著效果，带来消耗 +1.3% / GMV +5.0% / ROI +3.7% 的收益。

#### **3.3.2 消融实验**

为了进一步验证MBRL有效性，我们对MBRL进行了如下消融实验：

* **神经网络环境模型准度评估**：验证相比SBRL中的简单离线仿真器是否可以缓解离在线不一致问题？

+ 实验设置：神经网络环境模型与SBRL中常用的简单GSP环境模型进行对比；
+ 实验结果：状态转移MAE **-68.3%** ，奖励函数MAE **-90.0%** ；
+ 结论：神经网络环境模型可以大幅缓解在离线不一致问题。

* **出价策略轨迹与线上真实数据集距离评估**：我们已知MBRL相比ORL性能更好，我们想进一步查看性能更好的出价策略的轨迹与线上真实数据间的距离是否更大，以证明MBRL可以突破线上真实数据集的束缚寻优。

+ 实验设置：观测MBRL出价策略和ORL出价策略到线上真实数据集之间的Wasserstein距离；
+ 实验结果：效果较好的MBRL出价策略的轨迹会比效果较差的ORL出价策略的轨迹离线上真实数据集更远（ **+15.55%** ）。
+ 结论：验证了相比ORL是否可以探索出更优异的轨迹；

* **训练稳定性评估**：验证提出的COMBO+MICRO算法是否可以提升出价策略训练的稳定性？

+ 实验设置：对比了无COMBO+MICRO（图中MBRL-V1，蓝线）和包含COMBO+MICRO方法的MBRL（图中MBRL-V2，黄线）在9个稳定性指标上的稳定性差异；
+ 实验结果：如图5所示，增加COMBO+MICRO算法后，MBRL的训练稳定性有了明显的提升。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1qYkxJfD95icFyogf88pblqHhwMKJ24cW2VFIQibLMJy1pbHbWUIWOFsw/640?wx_fmt=png&from=appmsg)

图5. 无COMBO+MICRO（MBRL-V1，蓝线）和包含COMBO+MICRO方法的MBRL（MBRL-V2，黄线）在9个稳定性指标上的稳定性差异。可以看到增加COMBO+MICRO算法后，MBRL的训练稳定性有了明显的提升。

## 4. 针对TargetROAS问题的Lagrange-MBRL算法

与BCB问题不同，TargetROAS问题中存在额外的ROI约束，如何训练满足ROI约束的出价策略是算法的设计关键。一种常用的处理ROI约束的方式是在奖励函数中额外加入ROI惩罚项，进行reward shaping。然而ROI只有在投放周期结束时才可以计算，导致ROI惩罚项只存在于最后一步的奖励函数中，造成了奖励稀疏的问题。此外，reward shaping的方式缺乏收敛的理论保证，这些都给TargetROAS出价策略训练带来困难。为此，我们提出了Lagrange-MBRL方法缓解了上述问题。

### 4.1 Lagrange-MBRL Overview

Lagrange-MBRL算法的整体框架如图6所示，主要包含拉格朗日对偶梯度法和神经网络环境模型两个模块，其中**拉格朗日对偶梯度法给出了出价策略更新的方式，而神经网络环境模型则提供了用于支持出价策略进行拉格朗日对偶梯度法更新的数据**。两个模块的基本思路如下：

* **拉格朗日对偶梯度法**：拉格朗日对偶梯度法从理论上计算出出价策略的梯度，并通过原域和对偶域交替的方式进行更新，实现了在保障ROI达标的基础上优化出价策略。对比reward shaping的方式，拉格朗日对偶梯度法可以通过根据ROI达标情况自动调节对偶系数的方式保障ROI约束，避免了稀疏ROI惩罚项的引入。此外拉格朗日对偶对偶梯度法具备收敛性的理论保障。
* **神经网络环境模型**：我们沿用BCB问题的MBRL算法中的神经网络环境模型方法，基于线上真实数据拟合神经网络环境模型以生成训练样本，产生用于拉格朗日拉对偶梯度法更新的数据。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1xOSUcbS8eicZiaFmmlqjHQBGRLSnGKUwpm3gtIibPrdMTDy1tCiaSz3vFA/640?wx_fmt=png&from=appmsg)

图6. Lagrange-MBRL算法的整体框架。

由于Lagrange-MBRL中神经网络环境模型的构建和训练与上一节相同，因此下文中主要对拉格朗日对偶梯度法进行介绍。

### 4.2 拉格朗日对偶梯度法

为方便后文的算法展开，我们对TargetROAS问题进行重新表述。在此，我们考虑同时拥有上界和下界ROI约束的TargetROAS问题：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1xeg3mbSxRHuhAhaLTGq7ul92B0mCNv6ZiaNfibGzIibPoTghoQNlGicEVw/640?wx_fmt=png&from=appmsg)

其中  为出价策略参数， 表示一个投放周期内的拿量总和， 表示一个投放周期内的总消耗， 表示广告主设置的目标ROI值； 分别表示ROI的上界和下界限制系数，

**等价问题**：利用拉格朗日函数，上述Target ROAS问题可以等价地写为:

其中  为拉格朗日函数，其表达式如下所示：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1YUAMPjLJE7aQCOc7mmDDAADPicAWJGpM9gib2H3Xq4fpCAzQoia3iaaW8A/640?wx_fmt=png&from=appmsg)

其中  为拉格朗日系数， 对应超额约束（即ROI上界约束）， 对应欠额约束（即ROI下界约束）。此外，我们把超过ROI上界的幅度称为超额幅度，把低于ROI下界的幅度成为欠额幅度。

**对偶域-原域更新框架**：对于该等价问题，我们借鉴经典的Primal-Dual Optimization（PDO[8]）更新框架：首先随机初始化 ，然后交替进行对偶域和原域的更新。在对偶域中，我们固定 ，利用拉格朗日函数相对  的梯度更新  ，如下面公式(1)所示，其中与0取max是为了保障  非负；在原域中，我们固定  ，利用拉格朗日函数相对  的梯度更新 ，如下面公式(2)所示。可以证明，该框架可收敛到局部最优（[8]中的定理7）。对偶域-原域更新的整体框架如下所示。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48YnRFKecyqCK6gFOO1iabwBbmcuicXxDiaZ5R90tUB4py2pjibQDlzmPL1Cd6q88EOanqlH538AvaFjdg/640?wx_fmt=png&from=appmsg)

**在对偶域更新中**，我们推导拉格朗日函数  相对  的梯度， ，得到  更新的解析表达式如下所示。可以看到更新表达式有明确的物理含义，其中  的更新表达式即为超额幅度， 的更新表达式即为欠额幅度。直观上， 如同ROI约束的监控器，可以自动感知超额和欠额幅度，并控制着拉格朗日函数中“超额和欠额惩罚项”的幅度，相比人工设定的固定惩罚项系数具有自动感知的优势。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1ib5SC9e9jeNj1wGwb5EysDibOFFYvBZ7ibDxg1Kv55CickDicxFa07zwm5g/640?wx_fmt=png&from=appmsg)

**在原域更新中**，我们推导拉格朗日函数  相对于出价策略参数  的梯度，，其解析表达式如下所示。可以看到出价策略梯度由拿量梯度和消耗梯度两部分构成。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1xN9ngg7R3Gn2T0dtacWjH5gYWg9sKIbicESqMsbz4kNoY0fWzSPHD8A/640?wx_fmt=png&from=appmsg)

可以利用经典策略梯度定理得到拿量梯度和消耗梯度的表达式。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ11UkaPLb3icvYdibfpkRQ2dqygrqdAtbYJpuSjyuZO6lMGuDKd32BVqkg/640?wx_fmt=png&from=appmsg)

其中  分别表示在状态s和出价a下按照出价策略到一天结束的累积拿量和消耗。

**至此，我们给出完整的拉格朗日梯度更新框架**如下所示：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1sibTo8lkONCxKgTcKDgDVHJcO3r6icpqiaUkzgaoxabMcIE1yQ6M5I7FQ/640?wx_fmt=png&from=appmsg)

其中  均需要当前出价策略的轨迹样本才可以计算，因此我们沿用了MBRL中的神经网络离线仿真器进行训练样本的生成。

下面展示了Lagrange-MBRL的整体算法流程。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48byDKEauuMJKzhEBibhjEuJ1CxA7N8gympKdCpPl2OwrQiaAWOZwTzSdaPKj07kgjhcEiaCtqib7uPhtQ/640?wx_fmt=png&from=appmsg)

### 4.3 实验结果

#### 4.3.1 在线实验

我们在阿里妈妈万相台无界版全站推场景的 TargetROAS 计划上分别进行了Lagrange-MBRL的计划AB和预算AB实验，两个实验结论基本一致：带来消耗 +6.8% / GMV +3.8% / 达标率基本持平的效果提升。

#### 4.3.2 消融实验

在消融实验中，我们考察拉格朗日对偶梯度法在训练过程中对于ROI约束的保障作用。

* **实验设置**：分别利用拉格朗日对偶梯度法和reward shaping的方法在10个不同的seed下训练出价策略。考察在训练过程中出价策略在10000个计划上超额和欠额的幅度情况（理想情况均应逐渐下降）。
* **离线实验结果**：如图7所示，可以看到利用拉格朗日对偶梯度法训练过程中出价策略的超额和欠额幅度均逐渐减小，而reward shaping方法则不能实现同时下降。特别地，拉格朗日对偶梯度法可以有效降低超额幅度，验证了拉格朗日对偶梯度法对于ROI约束的保障作用的优势。
* **线上实验结果**：超额交付计划比例-1pt，双边达标率+0.3pt，与离线结果一致。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/sZ8T6nJp48YnRFKecyqCK6gFOO1iabwBbBe4cicsG2mib7Mjgf696ibLB6cYaY7XUkxPicxXWAY2u5nE8FibAQiczBalA/640?wx_fmt=png&from=appmsg)

图7. 拉格朗日对偶梯度法和reward shaping方法在训练中出价策略的超额和欠额幅度的变化趋势。

## ▐  关于我们

**阿里妈妈智能广告平台算法团队** 主要负责建设阿里妈妈万相台无界版广告产品的算法体系和阿里妈妈决策智能平台，紧密围绕淘系电商商家的不同营销需求，利用最先进的算法技术帮助商家获得最极致的广告投放效果和体验，主要涉及强化学习、深度学习、运筹优化等前沿技术，团队发表过多篇NeurIPS、ICML、KDD等顶会论文。我们始终相信并且一直践行着通过技术创新来提升效率、变革商业、普惠商家。

**📮** **简历投递邮箱**：

alimama\_tech@service.alibaba.com

## ▐  参考文献

[1] He Y, Chen X, Wu D, et al. A unified solution to constrained bidding in online display advertising[C]//Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery & Data Mining. 2021: 2993-3001.

[2] Kumar, A., Zhou, A., Tucker, G., & Levine, S. (2020). Conservative Q-Learning for Offline Reinforcement Learning. ArXiv, abs/2006.04779.

[3][新一代自动出价范式：在线强化学习SORL框架](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490403&idx=1&sn=46d538de12615973de06e9f83ec07814&scene=21#wechat_redirect)

[4] U, T., Thomas, G., Yu, L., Ermon, S., Zou, J. Y., Levine, S., ... & Ma, T. (2020). Mopo: Model-based offline policy optimization. Advances in Neural Information Processing Systems, 33, 14129-14142.

[5] Haarnoja, T., Zhou, A., Abbeel, P., & Levine, S. (2018, July). Soft actor-critic: Off-policy maximum entropy deep reinforcement learning with a stochastic actor. In International conference on machine learning (pp. 1861-1870). PMLR.

[6] Yu T, Kumar A, Rafailov R, et al. Combo: Conservative offline model-based policy optimization[J]. Advances in neural information processing systems, 2021, 34: 28954-28967.

[7] Liu X Y, Zhou X H, Li G T, et al. MICRO: Model-Based Offline Reinforcement Learning with a Conservative Bellman Operator[J]. arXiv preprint arXiv:2312.03991, 2023.

[8] Chow, Y., Ghavamzadeh, M., Janson, L., & Pavone, M. (2018). Risk-constrained reinforcement learning with percentile risk criteria. Journal of Machine Learning Research, 18(167), 1-51.

END

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp)

也许你还想看：

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[新一代自动出价范式：在线强化学习SORL框架](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490403&idx=1&sn=46d538de12615973de06e9f83ec07814&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[生成式拍卖：感知排列外部性的整页优化机制](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247494280&idx=1&sn=baf0e33c613c90a2075dbf1ab8697aac&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[PerBid：在线广告个性化自动出价框架](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490859&idx=1&sn=ed2ee3202c4897241ddba02e8e51edac&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)******** [强化学习在广告延迟曝光情形下的保量策略中的应用](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490902&idx=1&sn=ec8ec6708988e978672cebc348f84ea9&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[Bidding模型训练新范式：阿里妈妈生成式出价模型（AIGB）详解](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490421&idx=1&sn=55bc3b7f2ec6a70b029572516011082f&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[AIGB：基于生成式模型的自动出价优化新范式](http://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247492971&idx=1&sn=0f47a81aec1798cc2272bbea255dc508&chksm=c00aa308f77d2a1e290761c92575ddbc9f97b7ed4152811746a857d85b7602fbd0816eced327&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[万字长文，漫谈广告技术中的拍卖机制设计（经典篇）](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490419&idx=1&sn=5387da760a2bd8ea8e9c9e274f0b5a31&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[开源 | AuctionNet: 针对大规模博弈环境的出价决策Benchmark](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247494171&idx=1&sn=8c78e8b19a9214ca48c252071738bd7f&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp)

喜欢要“分享”，好看要“点赞”哦ღ~