---
title: '快手LCRON：工业级级联排序系统一体化建模新范式，助力商业化收入增长'
company: 快手
tag: 广告
date: 2025-07-23
url: https://mp.weixin.qq.com/s/RA_VMSfRMDfaQmKrpD0fow
account: 快手技术
origin: readme
---
![](https://mmbiz.qpic.cn/sz_mmbiz_gif/ZxDY5TMPs0EqL7dlyXD8OFyXn6yNGvQ8uEibL6TkOHqFvaK0bR9GEhZicTHuDtaTficMGS88ecXKIVPnFJCTMz7aQ/640?wx_fmt=gif&from=appmsg)

在推荐系统和广告平台等大规模Top-K集合选择应用中，级联排序（Cascade Ranking）架构已成为业界的主流。传统的训练方法通常侧重于Cascade Ranking系统的单阶段优化，却忽略了阶段间的复杂交互，导致系统整体性难以达到最优。尽管近期研究开始探索交互感知型训练范式，但仍面临两大挑战：

1. 训练目标难以与级联排序的整体目标（即准确选出ground-truth items）保持一致；
2. 未能充分学习各阶段间的高效协同模式。

为应对上述挑战，本文提出了LCRON训练框架（Learning Cascade Ranking as One Network）：

* 利用全空间样本为模型提供富含反馈信号与系统链路信息的训练样本，并为模型训练提供与系统链路同分布的数据环境；
* 针对系统端到端的集合选择目标，引入可微分的代理loss，从而直接优化Ground-truth项目在整个级联排序过程中生存概率的下界，确保了训练目标与系统最终目标高度对齐；
* 根据推导出的下界的特性，进一步为每个阶段设计了一个辅助损失函数，以驱动该下界的缩紧。这些辅助损失协同作用，旨在有效驱动整体损失的降低，从而促进各阶段之间形成更为鲁棒和高效的协作模式，实现更高效的 top-k 集合选择。

我们在公开基准数据集和快手实际工业应用中对LCRON进行了广泛的实验验证。实验结果表明，LCRON在多种实验环境中均显著优于现有方法，有效地解决了级联排序训练中的关键局限性。目前，LCRON已于2025年1月在快手商业化场景全量部署，统一了召回与粗排模型的训练，显著提升了广告收入，并成为线上占比最大的通路。本工作相关成果已被机器学习顶级会议 ICML 2025 接收，并在会议上做了报告。相关代码已开源。

论文标题：Learning Cascade Ranking as One Network

论文链接：https://icml.cc/virtual/2025/poster/44498

代码链接：https://github.com/kwai/LCRON

**一、项目背景**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp)

***1.1 Cascade Ranking系统的形式化***

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

在Cascade Ranking系统中，大量的初始候选项目集通过一系列连续的过滤阶段进行处理，以高效地识别最相关的结果。每个阶段应用一个特定的模型 来评估和选择输入集合中的一个子集作为下一阶段的输入。设  表示级联系统中的总阶段数，初始候选库存大小为。对于任何给定的阶段i，我们将输入候选样本空间定义为，其中包含个项目。经过第阶段模型处理后，输出由 个选定项目组成。

为了表述对项目进行排序的过程和结果，我们定义为按模型的得分降序排列的集合的有序向量，并将 定义为的前K个项目。有了训练好的模型集合 ，可以通过顺序过滤操作获得级联排序系统的最终输出集 ，可以形式化为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKPe1TCpCMc5nN6ItNWc2licAgPwAl2PUpZ5K0C3aKahqYDOV4pZEAtaw/640?wx_fmt=png&from=appmsg)

我们将ground-truth集合定义为基于用户反馈(user feedback)或奖励系统(reward system)被认为最优的项目集合。级联排序系统训练范式的目的是使用从系统收集的训练数据优化的召回率：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKhHDrrCPqcFwkibWkrN4fXT6rfp620J1wO3O6m4MhgX3RswNicZKVpAAA/640?wx_fmt=png&from=appmsg)

其中 是 的大小，是的大小，并且 。这里，是指示函数，如果条件为真则返回 1，否则返回 0。

***1.2 高效Cascade Ranking系统的关键需求***

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

下图展示了三个例子，用于说明高效Cascade Ranking系统需要满足的两个条件：

* 较强的排序能力：高效的Cascade Ranking首先需要保证各阶段模型有不错的排序能力。我们可以用每个阶段模型在全库候选上的排序准确性来衡量其排序能力。

* 较强的协同互补能力：通常我们认为模型的排序能力上限和模型容量强相关，当模型固定时，Cascade Ranking系统性能的天花板将取决于阶段间的协同互补能力。“协同互补”主要体现在：1）Match阶段送出的集合提前规避了Rank模型易高估的低质item，使Rank在Match输出集合上筛选的精准性优于Rank在全库候选上筛选的精准性，2）Rank阶段模型在Match输出集合上能准确辨别item的质量。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EYlrzT7ybYdws4iaADM8K8qyiaRFEmibia9fQYmuFenCo4IeAk6ibN6TCgzgMslqzazf0iazmQShXrTBHQ/640?wx_fmt=png&from=appmsg)

在第一个例子中，Match和Rank两个阶段都有较强的排序能力，因此Match阶段送出的集合包含全部的ground-truth项目，和较多质量较高的项目，但由于Match和Rank的协同性较差，Match送出的集合恰好包括一些Rank容易高估的低质ad，因此Rank筛选时这些低质ad对ground-truth造成了挤占。最终系统只选出了7/10的ground-truth。

在第二个例子中，Match和Rank的排序能力较弱，Match阶段送出的集合只包含7/10的Ground-truth项目、且包含很多低质项目；虽然Rank在全部候选上的排序能力虽然不佳，但Rank和Match阶段有很好的协同和互补，Rank模型在Match输出集合上有较强的排序能力，最终也能和第一个例子一样选出7/10个Ground-truth项目。

在第三个例子中，Match和Rank有相对较强的排序能力和较强的协同互补能力，因而整个系统选出了所有的ground-truth，达到了最优状态；而如果单独让Match或Rank在全库集合上筛选个项目，都无法选出全部的Ground-truth。

业界通常对Cascade Ranking中的不同stage进行单点迭代，如固定精排训练召回模型，此时算法工程师们往往不断追求前链路模型与后链路模型的“一致性”。然而，基于这些例子，我们不难发现：追求“一致性”的终点是让Cascade Ranking系统达到用最后阶段的、最复杂的模型做全库打分的状态，而重视协同互补能力的学习则有可能让Cascade Ranking突破这一天花板。

***1.3 传统方法的问题与挑战***

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

早期的级联排序系统训练方法通常独立地优化每阶段，分别进行样本构建、学习目标设计以及代理损失函数的定义。这种碎片化的训练方式忽略了各阶段之间的交互关系，导致训练目标与整个系统的最终目标之间存在偏差。具体而言，这些方法会面临两个关键挑战：

1、学习目标与系统目标不对齐：大多数现有方法并没有直接优化级联排序的端到端召回率，这会让模型对“排序能力”和“协同能力”的学习无法平衡到系统最优的状态。

2、缺乏协同的学习能力：缺乏对各个阶段之间交互与协作能力的学习。

近年来的一些研究尝试解决上述挑战：

* ICC ：作为早期尝试之一，ICC 部分解决了挑战1和2，它通过 LambdaRank 融合不同阶段的预测得分并联合优化。然而，其阶段间的交互仍然是单向的，限制了双向协作的学习能力。
* RankFlow：该方法引入迭代训练范式，利用上游阶段动态决定下游阶段的训练样本，以解决挑战2。尽管 RankFlow 相比独立训练和 ICC 均有显著提升，但其迭代训练过程可能带来一些不稳定性，导致收敛到次优的结果。
* FS-LTR：该方法通过全空间训练学习在线系统的交互与协作模式，解决了挑战2，并在性能上超越了 RankFlow。然而，无论是 RankFlow 还是 FS-LTR，都没有显式地解决训练目标与系统目标不对齐的问题（即挑战1）。
* ARF：该方法强调学习目标应与级联排序的目标对齐，并基于可微排序提出新的召回代理损失函数。然而，ARF 仅关注单阶段模型，无法全面应对挑战1和2。

综上所述，据我们了解，现有方法均未能同时有效解决上述两个核心挑战，这凸显了对更全面解决方案的迫切需求。

**二、研究方案**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp)

为了解决上述问题，让Cascade Ranking系统能面向端到端目标进行高效、协同的学习，我们提出了LCRON，它统一了Cascade Ranking系统的样本构建和学习目标、代理loss。我们以一个两阶段的级联排序系统（T=2）为例来简要说明我们的方法的基本思想，该方法可以很容易地扩展到更多阶段的系统。更多技术方案细节可以参考论文原文。

***2.1 全空间样本构建***

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

设和分别表示检索模型和排序模型。的输入空间、的输入和输出空间分别为、和。我们将真实标签集合记为，也称为。对于给定的一次曝光，设表示用户信息，表示物品信息，表示这对的标签，。一次曝光的训练样本可以表示为如下式所示：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKIFaOwqdtBZUibRPheV3qAjx4SkdLRtq2Avx6ovxE7l4FQHHGvd2G7iaA/640?wx_fmt=png&from=appmsg)

其中 表示从中采样的样本数量，且。 

设表示对在其所在阶段中采样后的降序排名索引（值越大表示排名越靠前）。标签的取值由其所处阶段的顺序以及在该阶段内的排名共同决定。具体来说，对于任意两个样本对和，其标签和满足以下条件：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrK17bxvvGWniaopgdXGRbDyvxFrYZcia4x7JAYzVpIv4GgKI0afbGiaznoQ/640?wx_fmt=png&from=appmsg)

其中 表示 所属的阶段比 更靠后， 表示 在同一阶段中的排名高于。

***2.2 端到端代理Loss***

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

我们的目标是设计一个高效的代理损失函数，使其与整个级联排序系统的 指标保持一致。我们可以将优化级联排序中的问题转化为一个“生存概率”问题，使模型能够估计出真实标签被级联排序系统选中的概率。注意，是的大小。设表示模型在训练数据上的预测向量。令表示数据中每个广告被模型选中进入 top-的概率向量。其中是阶段的quota。的总和应为。

令系统输出的生存概率向量为 ，标签为一个二值向量，表示是否为真实标签。我们可以使用 与 的交叉熵损失来优化真实标签被级联排序选中的概率，如下式所示：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKKbbUqtxRg2yBw2E7Jthktl5FHuXmGe5uX0iaFicKwgWu9Zh5nEesibwFw/640?wx_fmt=png&from=appmsg)

设 表示从  中采样的结果， 表示采样的概率。则可表示为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKg6kico8YFiaMpO65bShPZW07ZHI4VU2iaicvqDAC9yM612jRGmdryC7OvA/640?wx_fmt=png&from=appmsg)

则 可表示为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKJibCzqMjeSyeWpGeSnuq9GG6FBTHbLwCAqtaa7WcKyzG01bRdQoInKQ/640?wx_fmt=png&from=appmsg)

其中 与均为向量，表示点积，表示逐元素乘法，表示所有元素为的向量。由于采样和积分操作导致难以直接优化，我们希望为其找到一个近似的代理。我们定义。可以证明是的一个下界，因为 恒成立：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKFibjAv0SO8SF0g5sUkqZqX2daXJQxJibXZk3qRohuicejmQ7pSCDCGObA/640?wx_fmt=png&from=appmsg)

接下来的问题是如何获得一个可微分的  ，从而优化  。

为此，我们引入排列矩阵这个概念作为方法的基础。对于给定向量 及其排序后的向量，存在唯一的排列矩阵使得。的元素为二值，取值为 0 或 1。令表示将向量按降序排序的排列矩阵。具体地，表示是中第大的元素。基于排列矩阵，在中选择的 top-k 元素可表示为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKQBWsCxYSNKJaMr5vtATZGDM9UosADAWyEWuWCP2h4VwYocZmm0xXNg/640?wx_fmt=png&from=appmsg)

其中 是一个二值向量，表示每个物品是否被模型选中，表示模型的排列矩阵的第行。显然，可以解释为的分布，其中表示通过硬排序得到的 top-选择。为了实现基于梯度的优化，我们可以将松弛为随机变量，并通过最大似然进行优化。

具体来说，这可以基于可微分排序技术（如NeuralSort，SoftSort等），通过将硬排列矩阵 （按降序排列）松弛为软排列矩阵来实现。可微分排序方法通常通过对每一行应用带有温度参数的 softmax，生成一个行归一化的软排列矩阵。当时，收敛于硬排列矩阵。设为模型的软排列矩阵，其中表示物品被排在第位的概率。我们可以将 top-选择概率与级联排序系统的端到端损失分别表示为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKicNkxLMHNia0BQcLNRiaQGBCicPOxruwibBGibw7ExnsptIpZXdd6YCkDnJQ/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKScuEMNEanEgwht5tMOgK5uibOibnFzRVBVjibiael6HSiciclrg64Ik1slHw/640?wx_fmt=png&from=appmsg)

其中 表示逐元素除法运算符。 表示在训练过程中需要停止梯度。上述端到端损失 可以直接优化ground-truth items通过所有级联阶段的生存概率，做到了直接面向系统目标学习，因此能自适应地做好”各阶段全局排序能力”与“阶段间交互协同能力”学习的最优权衡，实现系统目标的最大化。

***2.3 用于缩紧下界的辅助Loss***

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=webp)

由于 优化的是ground-truth items通过整个级联排序系统的生存概率的下界，该下界的tightness可能影响整体性能，但本身无法优化该下界。为此，我们对与其下界之间的gap进行了分析，与 之间的差距可以表示为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKvibNQXnGBw1XoUnGic3ibKYKljMCZ0Hh93St3ARDoxkTlbP77ia7m08j6w/640?wx_fmt=png&from=appmsg)

这里我们推导出了  的一个理论上界。注意，，且， 。

接下来我们考虑模型输出之间的关系如何影响  。对于给定的，将视为唯一变量来最小化 ，显然必须满足以下条件：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKhKpL9CddEMymGdTNE4n3vwQzruicNXFq7PEoibFIAHg5XIAcV7QY4rRQ/640?wx_fmt=png&from=appmsg)

其中 表示向量的第个元素，表示中前大元素的索引。这表明，若两个模型的 top项一致，有助于减小。

为此，我们为每个阶段的模型引入了 用于缩紧  ，如下式示：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HUe79EwJPVibdz5RID96zrKpm34Ypib4iaQ9TrYfApIOrGvqz3ibnq5fbLm44TYQsibU42WEwW8gTBTAA/640?wx_fmt=png&from=appmsg)

 为检索模型和排序模型提供相同的监督信号，因而可以优化与的一致性，隐式地对齐与，使 所对应的下界更加紧致。

**三、实验验证**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp)

为全面验证 LCRON 的有效性，我们分别在公开数据集和快手商业化场景进行了实验。

1、公开数据集实验

我们基于RecFlow数据集（据我们所知，目前唯一包含系统链路全空间样本的Public Benchmark）进行了实验，分别验证了LCRON在两阶段（DSSM+DIN）和三阶段（DSSM+MLP+DIN）的Cascade Ranking的实验效果。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EYlrzT7ybYdws4iaADM8K8qG2ibbxJllaqQkYcekgv4yFbHnExSA2a3Z6mIN7s4vTyS8p0twazVSVg/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EYlrzT7ybYdws4iaADM8K8qx92DQCnUEibAmpArpbvfncdV4vulPMne7a4XbHvlLaGMxYsPCNWq7mQ/640?wx_fmt=png&from=appmsg)

实验结果表明（见上表），LCRON 在端到端Recall 指标（表中Joint）上显著优于所有基线方法，表明其在优化级联排序系统方面的有效性。值得注意的是，虽然LCRON 并未在所有单阶段指标上（例如排序模型的 Recall）都占优，但其在联合指标上的显著提升突显了阶段间协同优化的重要性。注：表中除了Joint一栏外，其他栏均为不同stage的模型在全库item集合上的评价指标。

此外，我们还进行了一系列补充实验以进一步验证 LCRON 在不同设置下的有效性与鲁棒性。这些实验包括不同可微排序算子的影响、超参数 tau的敏感性分析，以及在不同学习率和批次大小下的性能表现等，更多实验细节可以阅读论文原文。

2、快手商业化场景实验

为了评估 LCRON 在实际工业应用中的影响，我们将其部署在快手的广告系统中。

实验采用了DSSM+MLP的两阶段Cascade Ranking，训练所得的模型分别上线到召回和粗排阶段。实验结果表明，与 FS-LambdaLoss 和 ARF 两种基线方法相比，LCRON 在收入和广告转化率等关键指标上均取得了显著提升，验证了其工业落地价值。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EYlrzT7ybYdws4iaADM8K8qeCYw3ianW1DxySPQb5MG9rdQRbuWgqv4y8Tpq7HibfHVBOG6IXTQiaiatw/640?wx_fmt=png&from=appmsg)

**四、业务应用与展望**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp)

LCRON已于2025年1月在快手商业化场景全量部署，统一了召回与粗排模型的训练，显著提升了广告收入，并成为线上占比最大的通路。近期，将部分两段式召回通路的排序模型升级为LCRON后，也带来了显著的业务收益。LCRON将整个级联排序系统作为统一网络进行端到端训练，其模型便于一体化部署在单一服务中，可以有效精简引擎模块、降低链路通信与存储开销，展现出显著的系统成本优化潜力，这也是我们未来的重点工作方向。

- END -

”

欢迎加入

![图片](https://mmbiz.qpic.cn/mmbiz_png/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpF09GTXcEcG4Fy9SdWsPp2icyibcRsickibvTSQXgITrJPOF9bApGEbyZvg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1)

**「我们是谁」**  
我们是快手商业化算法团队，负责快手国内及海外多场景的变现算法研发，致力于建设领先的广告变现算法，通过算法驱动商业营销增长，不断优化用户和客户体验，引领行业创新型解决方案，推动行业变革。如果你也对信息流广告业务感兴趣，并且具备搜广推、大模型、NLP、CV等相关背景，欢迎加入我们！

### **「招聘岗位」**

### 💼 社招&校招&实习：

* 广告算法工程师-【模型方向】（北京）
* 广告大模型算法工程师（北京）

**「欢迎加入」**

简历投递：wenshiyang@kuaishou.com

”

【相关阅读】

[![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0EYlrzT7ybYdws4iaADM8K8qPRvOdyLibIQWo8Hibiapnqfa5XP0eAZPujao0AwheBRnZicX1h1FJfXicpw/640?wx_fmt=png&from=appmsg)](https://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247496537&idx=1&sn=11ddf9ba1427d51a0bb146d51b3591b9&scene=21#wechat_redirect)

[![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HRpAW5ganTFXKvUibShxZZcQQlsrsAvd0Jtkau0zT4n0GeXgqjwujic8kuOMtyAIfezxGnnd1E7ChA/640?wx_fmt=png&from=appmsg)](https://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247496739&idx=1&sn=e14ccdd63577836c9927bf2043dfac52&scene=21#wechat_redirect)