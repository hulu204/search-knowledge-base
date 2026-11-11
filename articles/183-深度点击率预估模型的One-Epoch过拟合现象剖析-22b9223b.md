---
title: '深度点击率预估模型的One-Epoch过拟合现象剖析'
company: 快手
tag: 广告
date: 2022-10-19
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490394&idx=1&sn=e2e8fa75c800287da824462a2206097d&chksm=c12c11c73fb47716a424a3f37d1e503363ef47a604760590e167c3a5d405ff94b8b6ba441403&mpshare=1&scene=1&srcid=1007N5NAKdanLQ5gNpr1eu8x&sharer_shareinfo=9bf5a97b4a3e5d4dfafc866bbbe57d06&sharer_shareinfo_first=9bf5a97b4a3e5d4dfafc866bbbe57d06#rd
account: 阿里妈妈技术
origin: readme
---
> 本文作者：**悦怿、珞家、惊寒、寒戍、孟诸**

## 1. 摘要

深度学习的应用极大地提升了推荐模型的效果和性能，然而业界对于推荐系统中深度模型的基础问题，例如过拟合现象，关注度依然较少。在本文中，我们将介绍阿里妈妈展示广告Rank团队对点击率(CTR)预估模型过拟合问题的研究。我们观察到CTR模型的过拟合现象非常特殊：在训练的第一个epoch结束，第二个epoch开始时，预估模型发生过拟合现象，并且在测试集上的效果急剧下降，我们称其为“one epoch现象”。为了解释该现象，我们在工业生产数据集上进行了大量实验。结果显示模型结构、模型的快速收敛（例如强优化器和较大学习率）以及特征ID的稀疏性是导致one epoch现象的关键因素。令人惊讶的是，深度模型往往在训练一个epoch后就可以达到最佳性能，这也解释了为什么许多工业推荐系统只对数据进行一次训练。我们进而提出了one epoch现象的一个可能假设，并佐以相关验证实验。希望该项工作可以使相关领域的同学关注并进一步研究深度推荐模型的过拟合现象，也期待后续研究者能够提出一种支持模型多次训练的可行方案，以期进一步提升模型效果。基于该项工作的论文已被CIKM 2022接收，欢迎阅读交流。

**论文**：Towards Understanding the Overfitting Phenomenon of Deep Click-Through Rate Models

**论文下载**：https://arxiv.org/abs/2209.06053

**代码链接**：https://github.com/Z-Y-Zhang/one\_epoch\_phenomenon

## 2. 背景

近年来，大规模深度学习算法不仅仅在计算机视觉、自然语言处理等诸多领域取得了不错的成果，也不断扩展到了其他领域。推荐模型也逐渐从以Logistic Regression（LR）为代表的浅度机器学习模型转变为基于深度神经网络Deep Neural Networks（DNN）的深度模型，并取得了极大的效果提升。然而，对于推荐系统中深度模型的一些基本问题，例如过模型拟合现象，不管是在学术界，还是在工业界的关注都相对较少。

相比于普通的深度学习模型而言，推荐系统中的深度模型在数据和模型结构上有其特殊性。以点击率预估为例，推荐系统的**数据特征通常是是高维和稀疏的** [7]，模型通常需要在具有数十亿特征的大规模数据集上进行训练，但大多数特征的出现频率非常低，呈现非常显著的长尾分布。考虑到推荐系统的数据特性，现在的深度CTR模型一般采用**Embedding和MLP的模型结构**，如下图所示：

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIPwia107RSlajqZQMNiaELBXd7O5v3bS2uxF08ldARv2syfoH0y1G7vbQ/640?wx_fmt=png)

Embedding and MLP模型结构

对于典型的CTR预估问题来说，模型的原始输入为一对用户和物品，并通常包含4类特征：用户特征（例如，用户ID、性别）、用户行为序列（例如，用户点击过的物品ID序列）、物品特征（例如，物品ID、物品类别）、上下文特征（例如时间、展示场景）。深度CTR模型首先将ID表示的离散特征通过**Embedding层**映射为低维向量，将用户行为序列通过pooling操作（例如取均值）转化为固定长度的向量。进而再把各个特征域的特征向量拼接到一起作为**MLP层**的输入，最终得到预测的点击率。

## 3. One-epoch现象

CV（计算机视觉）和NLP（自然语言处理）领域的深度学习模型通常需要训练几十个上百个epochs才能达到最优，如果发生过拟合现象，也往往是在训练过程中逐步发生。但在推荐系统中却并非如此，我们在阿里巴巴展示广告的生产环境下，将CTR模型训练3个epoch，得到的测试AUC曲线如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIWq0OMkfzBZuGTF8jmYm7NMBQUhn7o9TcuVf4ibWBDb41ic9VibbX6bIFA/640?wx_fmt=png)

展示广告深度CTR预估模型的one-epoch现象

可以发现CTR预估模型的过拟合现象非常特殊：模型AUC在第一个epoch内逐步提升，但是从第二个epoch开始，AUC效果突然剧烈下降，我们把这个现象叫做**one-epoch现象**。

展示广告Rank的生产模型采用了基于CAN [5]和STAR [6]的复杂模型结构，为了使得实验结论不局限于某一类特定的深度模型，我们进一步将模型结构和数据加以简化。具体说来，我们采用3层DNN（200X80X1）和7个简单的特征域（user\_age、user\_gender、history\_item\_IDs、history\_item\_categories、item\_ID、item\_category、scene\_ID）加以实验。在这种情况下，我们同样也观察到了one-epoch现象。同时，我们在Amazon Book和Taobao这两个广泛使用的公共数据集上进行实验，同样也观察到了one-epoch现象。当然，之前的研究论文中，也有部分文献发现了相似的现象 [2, 3]，但是此类现象并没有被重点探讨研究过。

上述实验以及相关调研发现，one-epoch现象在学术界和工业界都普遍存在。它有两个特点，(1) 恰好出现在第2个epoch开始；(2) 突然剧烈发生，导致模型精度迅速下降。针对于这两个特点，我们做了如下一系列分析。

## 4. One-epoch影响因素

为了进一步了解one-epoch现象，我们进行了大量的探索实验，整体结论如下：

1. 我们发现**Embedding+MLP结构**、**能使模型快速收敛的优化器算法**（例如学习率较大的Adam优化器）和 **稀疏特征**的使用（例如使用item\_ID等细粒度特征）与one-epoch现象的产生都密切相关；
2. 我们也验证了机器学习算法的一些核心要素，包括模型参数量、激活函数的选择、batch-size的大小、模型权重衰减（正则化项）和dropout等，但实验发现他们和one-epoch现象并没有直接的关联；
3. 虽然可以通过改变结论1中的影响因素来缓解one-epoch现象，但我们也发现这些方式都不可避免会带来精度损失。深度CTR模型取得最好的表现仅仅需要训练一个epoch！工业界的深度CTR模型一般都采用流式训练，并且只训练一个epoch，我们的实验结论或许为这种做法提供了合理性依据。

接下来，我们将分别介绍模型相关因素和特征相关因素对one-epoch现象的影响。由于篇幅所限，我们只会详述重要的部分，完整的内容可以参考论文。

### 4.1 模型相关因素

在模型结构方面，我们发现基于DNN的深度CTR模型会产生one-epoch现象，而基于LR的CTR模型在各种超参数设置下都不会发生one-epoch现象，只表现为精度上升、平稳、再缓慢下降的传统过拟合现象。这说明one-epoch现象与不同的模型结构有着密切关系。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIHibEAiaUJWOZqQ9C5gOcwbzKMVjWxGMB50d1LN477IquDY2DJ6hfQL9g/640?wx_fmt=png)

深度CTR预估模型存在one-epoch现象，而LR模型并没有

One-epoch现象是否与参数量有关呢？考虑到DNN模型的参数量比LR模型多，产生上述疑问也很自然。我们通过改变Embedding向量大小、隐藏层大小（即每层神经元数量）、MLP层数进行实验，发现不同参数设置下也都发生了one-epoch现象。值得一提的是，如下图中橙线所示，当Embedding维度为1时，也就是说每个特征用一个标量表示，深度CTR模型的参数量与LR模型的参数量差别不大，但深度模型依然发生了one-epoch现象，有理由相信与one-epoch有关的因素是深度模型采用的Embedding&MLP这种模型结构，而非模型参数量本身。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIR9QSV0PdLomtWMrIV8W0En4ZQPaJytVJdY9ichMY3micr23icPGaL1kyQ/640?wx_fmt=png)

不同Embedding向量大小都发生了one-epoch现象

模型优化器与one-epoch现象有紧密关联。在尝试了Adam、RMSprop、SGD等不同优化器后，我们发现Adam和RMSprop在大多数情况下都有更快的收敛速度，也更容易出现one-epoch现象。我们进一步观察到，学习率也与one-epoch现象也有一定关联。在极小的学习率下，one-epoch现象不太明显甚至完全消失，但模型的精度无法保障。简言之，能使模型快速收敛的优化器算法也更容易导致one-epoch现象。

此外，我们也分析了batch-size大小和激活函数的影响，发现他们和one-epoch现象基本没有关联。同时，我们也尝试了多个缓解过拟合的技术，包括权重衰减和dropout，发现他们对于解决one-epoch问题几乎没有帮助。

### 4.2 特征相关因素

工业界CTR模型的训练数据通常具有高度稀疏性 [7]。关于特征稀疏性，我们在这里提供一个直观的理解，如果一个特征域拥有的不同ID数越多、每个ID的平均出现次数越少，那么该特征域的稀疏性就越大。例如，下表所示的生产数据集中，item\_ID和history\_item\_IDs是两个稀疏最大的特征域。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIneU5I7mAdtibYsVoZWH476x9N77Ubq1p98LSwdUY5k3ffxnXMiacc6uQ/640?wx_fmt=png)

为了说明one-epoch现象与特征稀疏性的关联，我们尝试降低特征稀疏性并加以实验。具体说来，我们采用三种简单而普遍的方法：(1) 过滤（filter），过滤掉出现频率最低的ID，将他们替换为默认值；(2) 哈希（hash），使用较小的哈希表来对每个ID做映射；(3) 不使用稀疏性强的特征域，例如不使用item\_ID和history\_item\_IDs这两个特征域。篇幅所限，下图只展示哈希实验的结果，m为哈希表大小占原始ID数的比例，m越小则数据稀疏性越低。可以发现随着数据稀疏性降低，one-epoch现象逐渐减轻直至消失。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIro9jMzNIhxLCSPRXR3sLr8PlqjpEjLEG74f59QmQULPOCiatkI8qe4g/640?wx_fmt=png)

通过哈希降低数据稀疏性可以缓解深度CTR模型的one-epoch现象

事实上，上述三种方法都可以缓解甚至消除one-epoch现象，但都会存在一定的精度损失。这表明特征稀疏性与one-epoch现象密切相关，同时这也可以解释为什么部分场景训练的CTR模型不会遇到one-epoch现象——如果只用粗粒度特征或者采用过滤/哈希的方式降低了数据稀疏性，模型是可以训练多个epoch的。

## 5. One-epoch现象解释

上述实验仅仅揭示了一些和one-epoch相关的算法/数据因素，但是没有回答one-epoch现象产生的根本原因。接下来，我们给出一个假设，试图解答其产生的原因。

首先介绍一下符号。我们把样本经过Embedding层以后的稠密向量记为，那么MLP层可以看做是在联合概率分布上进行训练的分类器。我们把模型已经训练过的样本记作，把没有训练过的样本记作（为了方便理解，这里我们不对样本的训练次数进行区分)。下图中，训练样本在第一个epoch学习之前是，而对其计算损失模型更新之后，它就变为，因此训练样本在第二个epoch就变成了。测试样本自始至终都是。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIYgYC7MribuNDWHribfAQwmLR2FsKy5g35VGtMdic9BK07o1jamly7XubA/640?wx_fmt=png)

One-epoch现象的原因解释

基于以上符号，我们提出了如下假设：与有显著不同。在第二个epoch开始时，MLP迅速适配到，进而导致了one-epoch现象。

上图为该假设提供了形式化描述。在第一个epoch训练时，MLP拟合的是（白色三角形），此时训练数据与测试数据（白色圆形）分布一致，模型正常训练。但是在第二个epoch开始时，MLP快速适配到由蓝色三角形表示的，训练数据和测试数据的分布差异性使得过拟合快速发生，导致one-epoch现象。下面我们给出验证实验。

### 5.1 的变化

我们首先验证是否在第二个Epoch开始时发生了较大变化。为了量化分布的变化，我们将采用-distance指标来衡量和之间的差异 [4]。-distance是量化两个分布之间差异的指标，在我们的实验中，更大的-distance对应着着更大的Embedding分布的差异，从而正负样本更容易被MLP分类器所分开，MLP拟合更容易。

如下图所示，在训练过程中我们分别在训练集和测试集上计算-distance，可以发现其在第二个epoch开始时突然增大，这一现象也验证了的变化，同时说明第二个epoch时，MLP的拟合任务要容易得多。对于测试集，所有样本从头到尾都是未经训练的，对应的-distance也没有明显变化。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIRL0VjeJy8yhVGIpicUaWLzHKibibVNTY7WpNia2yeZx4xN4quHJPbzPLSQ/640?wx_fmt=png)

训练集和测试集上的A-distance，值越大表示分布差异越大，也越容易被区分

我们进一步分析了与稀疏特征之间的关系。发现在第二个epoch开始时，稀疏特征域（item\_ID、history\_item\_IDs）的-distance突然增加，而其他特征域（如age）则没有明显变化，这也说明了的变化主要是由稀疏特征主导，这与我们之前观察到的特征稀疏性的影响是一致的。进一步，我们还发现当one-epoch现象不发生时，没有明显变化，这说明的改变是发生one-epoch现象的必要条件 [论文Fig 12]。

### 5.2 MLP迅速拟合

我们接下来验证MLP层在第二个epoch开始时，是否可以快速拟合。在训练过程中，我们通过计算每层参数更新量的范数来监测模型的参数更新。如下图所示，MLP的参数更新量（图b, c, d）在第二个epoch开始时突然变大，而Embedding层的变化相对较小（图a），这就验证了我们之前提出的假设：MLP在第二个epoch刚开始时，通过参数的大量更新迅速适配到。

![](https://mmbiz.qpic.cn/mmbiz_png/0bUHKeoZbc4IJvSbkibdfIlibkILXPxEHIaKPaYJyC1CFU8pqxTUOkd1njicz5P6AOdBwtEfxHf08ac1TsrLmp5xw/640?wx_fmt=png)

模型参数更新量，MLP更新在第2个epoch有突变

与此同时，我们还进行了另一个实验来验证我们的假设。在第一个epoch训练结束后，对于MLP层和Embedding层而言，我们fine-tune其中一个而冻结另一个。实验发现fine-tune Embedding冻结MLP层没有one-epoch现象，而fine-tune MLP冻结Embedding则会导致one-epoch现象。也说明one-epoch现象与MLP在第二个epoch快速变化有关。

## 6. 总结与展望

与CV和NLP等深度学习模型的应用不同，深度CTR模型的过拟合呈现出one-epoch现象，即模型在训练的第二个epoch开始时，精度突然急剧下降。这个现象广泛存在于学术界和工业界的CTR模型中。通过大量实验，我们观察到one-epoch现象与模型结构、使模型快速收敛的优化器算法、稀疏特征的使用均有关联。同时，我们也提供了一个合理的假设用于解释one-epoch现象。

对于深度CTR模型而言，我们能否通过训练多个epoch以提升模型精度？为此，我们也尝试了一些方法，例如学习率衰减、在第二个epoch时仅仅fine-tune部分模型参数等。生产数据集上的实验显示，这些方法均无法带来明显的性能提升，最优模型通常在只训练一个epoch时得到。这也解释了为什么工业界深度CTR模型一般只过一遍数据。

虽然本文只关注CTR模型，但本文的研究方法同样也适用于转化率/收藏加购等其他用户行为预估的模型。我们相信one-epoch现象是推荐系统领域一个有趣而基础的问题，也希望未来的研究能够为解决此问题提供更多思路。

References

1. Zhao-Yu Zhang, Xiang-Rong Sheng, Yujing Zhang, Biye Jiang, Shuguang Han, Hongbo Deng, and Bo Zheng. Towards understanding the overfitting phenomenon of deep click-through rate models. In CIKM 2022. https://arxiv.org/abs/2209.06053
2. Guorui Zhou, Xiaoqiang Zhu, Chenru Song, Ying Fan, Han Zhu, Xiao Ma, Yanghui Yan, Junqi Jin, Han Li, and Kun Gai. 2018. Deep interest network for click-through rate prediction. In SIGKDD 2018.
3. Jieming Zhu, Jinyang Liu, Shuai Yang, Qi Zhang, and Xiuqiang He. 2021. Open benchmarking for click-through rate prediction. In CIKM 2021.
4. Shai Ben-David, John Blitzer, Koby Crammer, Fernando Pereira, et al. 2006. Analysis of representations for domain adaptation. In NeurIPS 2006
5. Weijie Bian, Kailun Wu, Lejian Ren, Qi Pi, Yujing Zhang, Can Xiao, Xiang-Rong Sheng, Yong-Nan Zhu, Zhangming Chan, Na Mou, Xinchen Luo, Shiming Xiang, Guorui Zhou, Xiaoqiang Zhu, and Hongbo Deng. 2022. CAN: Feature Co-Action Network for Click-Through Rate Prediction. In WSDM 2022
6. Xiang-Rong Sheng,Liqin Zhao, Guorui Zhou, Xinyao Ding, Binding Dai, Qiang Luo, Siran Yang, Jingshan Lv, Chi Zhang, Hongbo Deng, and Xiaoqiang Zhu. One Model to Serve All: Star Topology Adaptive Recommender for Multi- Domain CTR Prediction. In CIKM 2021
7. Biye Jiang, Chao Deng, Huimin Yi, Zelin Hu, Guorui Zhou, Yang Zheng, Sui Huang, Xinyang Guo, Dongyue Wang, Yue Song, et al. 2019. XDL: An Industrial Deep Learning Framework for High-Dimensional Sparse Data. DLP-KDD.

END

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**也许你还想看**

************[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)************[点击率模型特征交叉方向的发展及CAN模型介绍](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486846&idx=1&sn=8312c06303dbad4882eece7f8e382cad&chksm=ce8a4827f9fdc131e4f333a30a72f2a68268f0b437e5035924c3502b346b5dfda84883483cd6&scene=21#wechat_redirect)

********[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)********[EXTR：面向外部性的工业级广告点击率预估框架](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247489367&idx=1&sn=c881fbd33a8dabeac1d804e6435652be&chksm=ce8a520ef9fddb185af2326623607824c9538ddd869925e440da664485c367b5fc3a7beeee12&scene=21#wechat_redirect)

****[丨](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247486152&idx=3&sn=809bd50723323056a50fb2ec575ad643&chksm=ce8a4f91f9fdc687caa6ff6ed8c91700c872e1da8615979921dbad070742bd06d351162ecd48&scene=21#wechat_redirect)****[多场景下的星型CTR预估模型STAR](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247485923&idx=1&sn=cb4a5f6840a795a87728f80855819a4b&chksm=ce8a4cbaf9fdc5ac80f4fa0dcc3e495b38fef7edf4754a821e492696dd78f865cb46945b486c&scene=21#wechat_redirect)

**[关注](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247484017&idx=1&sn=eac2d6d4293e99c93ee86d031a972b6e&chksm=ce8a4728f9fdce3e21daf5d9cf049af872282e3a85bf59382f12a3f1ff5a8d2bba6ca6188bbf&scene=21#wechat_redirect)****[「阿里妈妈技术」](http://mp.weixin.qq.com/s?__biz=Mzg3MDYxODE2Ng==&mid=2247484017&idx=1&sn=eac2d6d4293e99c93ee86d031a972b6e&chksm=ce8a4728f9fdce3e21daf5d9cf049af872282e3a85bf59382f12a3f1ff5a8d2bba6ca6188bbf&scene=21#wechat_redirect)，****了解更多****~**

![](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc4IGeDxYKoB688oSt1FT2KVc8RCeBzQu4HsHstt8dptZjHh7AbKE4fN4qIq6iause5SENjy85icf7pA/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

喜欢要“分享”，好看要“点赞”ღ~

↓欢迎留言参与讨论↓