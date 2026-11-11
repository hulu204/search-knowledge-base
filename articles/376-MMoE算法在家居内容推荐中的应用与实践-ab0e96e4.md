---
title: 'MMoE算法在家居内容推荐中的应用与实践'
company: 阿里淘系
tag: 多目标&多任务
date: 2021-02-05
url: http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650418474&idx=1&sn=6b1e3ff914e68607c006a07a5b880296&chksm=8396e532b4e16c24734511e21872e995f5191943628eca791eb819a3899cfd6904996d09f461&scene=27#wechat_redirect
account: 大淘宝技术
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_gif/33P2FdAnju95xNQaJWFlU3fWicicxBac5nuOMtveZ6lxCCnoZU1Xd6ITUVhoibJib5eyx6d2hePhGFNbQ4nT3Gicgpg/640?wx_fmt=gif)

淘宝躺平频道是手机淘宝内主推家居类商品的内容场景化导购平台（以下简称躺平）。频道中的内容主要以场景搭配为主，内容内挂载了多个商品锚点，点击商品锚点可以跳转到商品详情页。躺平强调算法大数据搭配及D端设计师理念，内容以多种形态迎合消费者的家居类需求。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMIcpGTQKLhNPORoBNTxiaUm4vuoic5AON15wd3Ifkl2ZSicNOlMicYZtflQ/640?wx_fmt=png)

用户可以通过以下3种方式进入淘宝躺平频道：

1）关注躺平家居，然后在手淘顶部ICON区域主动访问；

2）搜索躺平关键词访问；

3）点击手机淘宝首页猜你喜欢的躺平内容卡片。

## 

## 

## **多目标优****化&MMoE**

---

用户进入躺平频道页后，浏览和点击内容卡片进入内容详情页，点击内容详情页的商品锚点进入商品详情页，进而进行收藏加购等行为。业务最终的目标是GMV的提升，因此，业务模型涉及的优化目标包含了一跳点击，二跳点击，以及进入商品详情页后的收藏加购下单。我们当前的精排模型主要考虑了用户在场景内的一跳点击，缺乏对二跳以及后续相关行为的建模，与我们最终的优化目标是有gap的。因此，实现躺平频道的家多目标优化是模型深度优化和完成业务目标的必要途径。

### **▐****多目标优化方法**

已有的多目标优化方式包括：

* 通过sample weight进行多目标优化[1]；
* 多个模型stacking；
* Shared bottom NN  model[2,3,4]；
* MMoE多目标模型[5]等。

方式1本质上并不是对多目标进行建模，而是把不同的目标折算成一个目标，并且相关的折算可能需要多次AB测试才能确定；方法2需要更多的模型参数，模型规模变大，线上serving需要更多的时间开销；方式3在基于深度学习的推荐模型中引入shared bottom layer来加强参数共享，通过多个目标的模型联合训练，减小模型的参数规模，同时防止模型过拟合，但是Shared bottom NN model能够成功的前提，是预测的目标之间的相关性比较高，对于差异性比较大的目标，简单粗暴的共享bottom layer反而容易造成不同任务之间的相互干扰。

MMoE是方法3的一个改进版本，其思想是所有目标共享多个experts，但是考虑到不同任务之间的特异性，为每一个目标设置一个gate，用来控制不同目标选择每个expert的信号占比，类似于weighted sum pooling操作。MMoE通过共享experts学习到不同任务的联系和差异，提高了每个任务的学习效率和质量，同时通过gates来平衡多个任务对experts信号的选择，不要求目标之间必须是高相关性的。

### **▐  MMoE模型介绍**

MMoE模型的结构(下图c)基于广泛使用的Shared-Bottom结构(下图a)和MoE结构，其中图(b)是图(c)的一种特殊情况。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UM4awdm42NFJqLFGJ9v6r1u55BMNK1LicVEZprrY18R5fia1t8qWqPuoJw/640?wx_fmt=png)

* **Shared-Bottom Multi-task Model**

如上图a所示，shared-bottom网络位于底部，多个任务共用这一层，我们将其表示为函数f。往上，K个子任务分别对应一个tower network，表示为![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnjuicwBUagFVBL9a2ctu3Yv7Rh8qFGBpYvXJpuokicqS6aQAZOfFxd0wU2iaZyicXycNqYXgiaw6y6qXuTlg/640?wx_fmt=jpeg)，每个子任务的输出![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMPRBN2GvZ0mZh0l7qOD2cFvhZWjWOgWMUPiaibmdJjDcXgnJxcInncqhw/640?wx_fmt=png)。

* **Mixture-of-Experts**

MoE模型可以形式化表示为![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMTYQIHQPa4Ko3rGkLdrm97aKBpycsW4nk5e8DRVwkFcHQFXskzibbxlg/640?wx_fmt=png)，其中![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMW8NB0Hv8Wdib3kuskQOAIuz99rK3wVT6n8xk8iaxtMmmNkmxPrXgov4g/640?wx_fmt=png)， ![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMupdgaohNo9wthgMwOKWVq2AfxEbLko1ZDXCQiaBibeHgCicJMrgJa0sag/640?wx_fmt=png)是n个expert network（expert network可认为是一个神经网络）。g 是组合experts结果的gating network，其输出是对不同experts的权重。

* **MMoE模型: Multi-gate Mixture-of-Experts**

MMoE模型的思想是用MoE结构替换shared-bottom网络中的函数 f ，如上图c所示，可形式化表达为：![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMmRnibm9u82qQ553nmUxuas5guFk7pKtSL7H49FY2pVHibxa3ib3nkYDxg/640?wx_fmt=png), 其中 ![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMP15bXgJZlSFpfAy5Ev5U5MYcPmYzhAsJKfVqRKhpDvFta8mhicweFUQ/640?wx_fmt=png)，输入是input feature，输出是不同任务在所有experts上的权重。

**MMoE在躺平多目标优化实践**

---

基于MMoE的灵活性及高可扩展性，我们选择MMoE作为躺平多目标优化模型，并对其进行了4个维度的优化和实验。

### **▐** **底层特征处理，引入局部激活单元**

 

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMoTqmU6eGJAoNMo0unL7DXl5ibjWsS6abmVu8Kl7ftZ57mS4iadeI9Few/640?wx_fmt=png)

在传统的Embedding + MLP模型中，首先将大规模稀疏输入特征映射到低维Embedding向量中，然后通过pooling转换为固定长度向量，最后再把它们连接在一起输入到MLP以学习特征之间的非线性关系。这样存在的问题是：将多个特征向量压缩到一个固定长度的表示向量来学习特定用户所有的兴趣表示，限制了模型的能力，使得模型很难从历史行为中提取用户变化的兴趣。参考Deep Interest Network模型[6]，我们在MMOE底层特征向量处理中引入局部激活单元，提取用户跟当前内容相关的向量表示。

 

### **▐****加入线性特征&线性结构**

在深度模型中，主要通过学习到的低维度稠密向量实现模型的泛化能力，从而实现对未见过的内容进行泛化推荐。 在躺平多目标优化中，我们不仅需要模型具备泛化能力，同时也希望模型能够通过线性逻辑对模型泛化的规则进行修正。在如何引入线性逻辑对MMoE进行优化方面，我们实现了5个版本优化方案，其中第4种方案的实验效果最优：

1) 线性模型输出 + MMoE网络输出作为最终预测结果；

2) 将线性特征输入到MMoE各任务Tower网络全连接层；

3) 将线性特征输入到MMoE专家网络和门控网络；

4) 在3)的基础上，同时结合1)；

5) 在2)的基础上，同时结合1)。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMUZnLeUKpx23ZOehVicB40uaGmGrMKwnYvEcsM6GmCYYVwpNOwDBzfwA/640?wx_fmt=png)

## 

### **▐****多目标Loss权重调参**

在多目标学习中，每一组loss之间的数量级和学习难度不一样，如何平衡多个loss得到较优的效果也是一个值得研究的课题。在比较简单的多目标组合中，一般通过调超参就可以；对于比较复杂的多任务loss之间的平衡，可以参考其他loss权重优化的方法[7]，这也是我们的多目标模型后续优化和探索的方向。

在躺平多目标前期实践中，只有一跳点击和二跳点击两个目标，目标组合相对简单，做法是直接看这几个loss输出的值，将他们调整到几个loss平衡的状态，然后开始根据训练验证的曲线，调整一下相对的权重。在实验了多组相对权重后，发现对于目前躺平一跳点击率和二跳点击率多目标优化而言，相对权重是1:1的效果最优，ctr和cvr预测的离线AUC分别提升0.24%和6.01%；

 

### **▐****三目标优化&结构瘦身**

除了对用户的一跳和二跳点击行为进行建模，我们还把用户通过躺平频道进入商品详情页后的收藏加购等行为视作第3跳目标进行建模，引入了三跳相关的样本和特征，使用MMoE进行三目标优化。并且考虑到目前设计的MMoE模型实际上包含了5层深度神经网络，线上打分消耗时间较长，我们对模型进行合理减层减参的“瘦身”试验，最终将模型调整至3层深度，取得了较好的效果；

 

### **▐****效果**

我们将训练得到的多目标模型用于躺平频道的内容推荐和躺平内容外投场景的精排阶段，上线完整AB7天，线上A/B Test结果如下：

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnjuib0oCZKQAQQ6jjPTykVW4UMcCiazzoWib8NUNCk7rrOtkXHYlSU0bacsmJHG9xsf1erCDbrR8DJ93kg/640?wx_fmt=png)

MMoE模型的引入及我们所做的相关优化实践使躺平频道的二跳点击率得到了较大提升，前期优化中一跳点击率稍微负向，主要是因为目前的baseline是只基于ctr优化的，引入MMoE多目标优化后模型的优化变成了对场景多个目标的综合优化，对比ctr的特化模型的效果略差，但是整体的多跳目标有大幅提升，这是符合预期的。

## 

## **总结与展望**

---

本文对MMoE模型在躺平多目标优化的实践进行了介绍和讨论。在综合考虑场景特点以及其他相关多目标优化方法的优缺点后，选择了MMoE模型对躺平频道场景用户行为和内容特点进行精排建模，并不断优化。线上AB结论证明了MMoE在躺平频道多目标建模的可行性以及相关优化的有效性。目前的MMoE模型主要应用于多跳点击率的优化，在后续的优化中，我们将考虑引入GMV相关特征和信息，进一步深入优化模型和提升场景最终GMV，同时，正如上面提到的，后续我们也将考虑尝试其他的Loss权重优化方法，不断优化模型使其在场景落地的收益最大化。

## **参考文献**

[1] Covington P, Adams J, Sargin E. Deep neural networks for youtube recommendations[C]//

Proceedings of the 10th ACM conference on recommender systems. 2016: 191-198.

[2] https://arxiv.org/pdf/1706.05098.pdf

[3]  Caruana R. Multitask Learning: A Knowledge-Based Source of Inductive Bias ICML[J]. Google Scholar Google Scholar Digital Library Digital Library, 1993.

[4] https://lumingdong.cn/multi-task-learning-in-recommendation-system.html

[5] Ma J, Zhao Z, Yi X, et al. Modeling task relationships in multi-task learning with multi-gate mixture-of-experts[C]//Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. ACM, 2018: 1930-1939.

[6] Zhou G, Zhu X, Song C, et al. Deep interest network for click-through rate prediction[C]//Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. 2018: 1059-1068.

[7] Alex Kendall, Yarin Gal, Roberto Cipolla. Multi-Task Learning Using Uncertainty to Weigh Losses for Scene Geometry and Semantics. CVPR, 2018.

✿  **拓展阅读**

[![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8oboSlriamq5aGFtHnpJFTCuPqRja0UEPryT1xPe5iaAw18VIJCfr9dhn79gUmgUAwp07YCKjD2D4w/640?wx_fmt=png)](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650412376&idx=1&sn=da835d9366fef6a903c8d17a4fb2e53e&chksm=8396dd40b4e154563f856a86ce6a3b240ed832ef509805d29da18e12f5b0cda786e3b76e21ff&scene=21#wechat_redirect)

[![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8D0ZDO6Ryt5xhbr5pcY9dkVPv0wxOSqRQ8fVQvO33qn1nGanYtxDIsPluYfAx7qWpoMxTv4IZWyg/640?wx_fmt=png)](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650413430&idx=1&sn=32c89ea3222d341bf3014854f69fd239&chksm=8396d16eb4e1587838f99a6859668a3588b0762155c1a13872d3f419efa3f75c5a532d7d38fe&scene=21#wechat_redirect)

[![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju94mfCRzlLsNmvQ3KU0YG4kGT1fGVmAYfMBGFIpUxMCUkA612OIvQBaogElywMpZPjEFVU6icWlQAw/640?wx_fmt=png)](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650410892&idx=1&sn=69a89072e83f6ff2b9333622ad390fdd&chksm=8396c794b4e14e829b625fa26568dd112f94edbdc97ec4984a2daf5ee5187e2283c397e36d48&scene=21#wechat_redirect)

**作者|**罗玲（至夏）

**编辑|**橙子君

**出品|**阿里巴巴新零售淘系技术

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju9qJSYLusYZ20IeW1JcwLxOmYpQKzz1XI7PlgmOA3cPARTxwZuKFw6osZsksibeH7HrS9oiaVooQSZQ/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9I3TY9EP8M3D7oDuMfTuEh37yxribyjc3viaicCKBT9nJhqBcib36SSRaib3vIobcZbx93RYyf9QvgzOA/640?wx_fmt=png)