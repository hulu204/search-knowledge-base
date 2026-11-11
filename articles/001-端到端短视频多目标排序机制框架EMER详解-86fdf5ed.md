---
title: '端到端短视频多目标排序机制框架EMER详解'
company: 快手
tag: 推荐
date: 2025-10-30
url: https://mp.weixin.qq.com/s/vQfH48o-A6kQR4duYoWbIQ
account: 快手技术
origin: readme
---
![](https://mmbiz.qpic.cn/sz_mmbiz_gif/ZxDY5TMPs0EqL7dlyXD8OFyXn6yNGvQ8uEibL6TkOHqFvaK0bR9GEhZicTHuDtaTficMGS88ecXKIVPnFJCTMz7aQ/640?wx_fmt=gif&from=appmsg)

当你打开短视频 App，手指上下滑动的每一秒，背后都藏着一套决定 “你接下来看什么” 的排序逻辑。

过去十年，行业里的推荐排序大多依赖 “人工设计公式”—— 工程师们把 “用户会不会点赞”、“能看多久” 等指标，按经验分配权重、套进公式，算出每个视频的 “优先级分数”。

但这套模式正在遭遇瓶颈：有人喜欢 “短平快” 的搞笑视频，有人偏爱 “慢节奏” 的生活记录，一套公式怎么满足千万用户的个性化需求？当 “留存”、“时长”、“播放量” 等目标冲突时，比如推长视频能提升时长，却可能降低播放量，人工调权重又该如何平衡？

为解决这些问题，快手策略算法团队设计并落地基于模型的端到端多目标融合排序机制框架EMER。它用 “会比较、能进化的 AI 模型”，彻底替代了传统推荐排序，实验推全前的Launch实验和推全后的反转实验，均观察超过一个月，从反转实验数据来看，用户体验提升显著：

* 快手极速版App：七日留存+0.302%，App停留时长+1.392%，单列短视频观看次数+1.044%；
* 快手主App：七日留存+0.231%，App停留时长+1.199%，单列短视频观看次数+2.996%；
* EMER 还适配到了快手端到端生成式推荐系统OneRec 链路的奖励模型中，使得App停留时长提升0.56%，留存有显著正向趋势，反转实验长期观察中。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLf2NCVWESVtxUAHjruFaVkOqfq0N3zk0pn3fy0QhPEwBb7VjPVlDxiaww/640?wx_fmt=png&from=appmsg)

论文题目：An End-to-End Multi-objective Ensemble Ranking Framework for Video Recommendation

论文地址：https://arxiv.org/pdf/2508.05093

【主要贡献】

在项目推进中，快手策略算法团队重点关注了真实工业场景落地的现实难题。把落地过程中的经验总结并发布出来，希望能给大家提供一些参考：

1、短视频推荐场景中，用户满意度难定义。不同用户表达满意的行为模式迥异，甚至同一个用户对不同类别的短视频也有不一样的满意度表达方式。这就导致模型的学习目标是很难定义的。

2、排序的本质是“比较”，同一个请求内候选适配之间的比较关系是非常重要的，模型如何感知此类信息也是一个难点。

3、模型的学习目标难定义，也意味着模型的评估Metric难设计。

针对上述落地时的三个现实挑战，快手设计了一套系统性的解法。实际上，在机制模型化的同时，还推进了“群治+自治”的多业务迭代排序机制，实现以留存贡献度为流量分配依据，驱动在单列迭代的多个业务聚焦内部提效和内外部协同。EMER则具体指消费业务内部的机制模型化，多业务间仍保留较大的白盒化程度。

关于EMER的详细解读可查看该视频👇

**一、让模型学会 “比较”，而不是 “单独打分”**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

工业界广泛应用的推荐排序模块范式是两阶段的，第一阶段通过大体量模型预估用户在多个维度上的满意度，第二阶段将多目标标量化作为最终排序依据，即多目标融合排序。工业界普遍采用的标量化方法是人工设计的启发式排序公式，排序公式应用成本低、调整灵活、可解释性强，但个性化和非线性空间都很有限。

传统推荐排序模型的优点很明显 ——成本低、调整灵活、可解释性强。但缺点也同样突出：

* 个性化不足：一套公式覆盖所有用户，无法适配 “有人爱刷短剧、有人爱刷知识” 的差异需求。
* 非线性能力弱：公式只能处理简单的线性关系，没法捕捉 “用户看了A视频后，更可能喜欢B视频” 这类复杂关联。
* 多目标平衡难：当 “留存” 和 “播放量” 冲突时，只能靠工程师反复试错调权重，既耗时又难找到最优解。

过去的排序模型，本质是 “给每个视频打个独立的分，按分数排序”。快手提出的端到端多目标融合排序EMER的核心思路是 ——排序的本质是 “比较”，得让模型看多个视频之间的相对好坏。

为了让模型学会比较，EMER 从数据、特征、模型三个层面做了重构：

* 样本组织： 传统方法只看用户互动过的少数几个item。但我们知道，用户的一次请求中，其实有大量候选item。EMER是把一次请求的所有候选item（无论是否曝光）都打包成一个样本。这不仅能解决曝光偏差问题，还直接为模型提供了丰富的比较对象，并且与在线对所有候选的比较排序过程更加一致。
* 特征设计：EMER不只给模型提供单个item自身的特征，还引入了 Normalized Ranks（original item rank/total number of candidate items ）这种相对位置特征。简单来说，就是告诉模型：“这个视频在这一批候选中的排名是第几（从某单一维度的信号来看）”，让模型明确知道每个item在当前候选集中的相对地位。
* 模型架构：为了处理这种带“比较关系”的数据，EMER基于 Transformer 的网络架构。本身Transformer 天然就擅长处理序列和关系。它能显式地捕捉候选item之间的复杂关系，评估每个item对其他item的影响。最终，模型给出的得分，不再仅仅是item本身的质量分，更包含了它在当前上下文中的相对价值。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfJKoHuLCHq8vzrILhIUpTe7bAQsOCQGGzrrJkqkqoHib3C0vib9nEb35g/640?wx_fmt=png&from=appmsg)

**二、怎么让模型知道 “用户满意吗？**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

解决了数据和模型的基础问题后，下一个难点来了：如何量化用户满意度，以及如何处理多目标间的冲突。

在推荐系统领域，一个长期存在的挑战是如何构建一个有效的监督目标，以准确量化和优化用户满意度。由于用户行为的个性化和多样性，简单地用单一指标或绝对分数来衡量满意度是极其困难的。EMER 框架针对这一挑战，提出了基于相对优势满意度 + 多维满意度代理指标的方法：

相对优势满意度 ：

用户对item的多维后验（如点赞、观看时长等）都能用户某个维度的满意度，基于用户的多种反馈很难定义一个用户满意度的绝对水平。但是但可以基于用户在收到推荐后的后验反馈来判断一个一个item是否相对更优于另一个item。我们定义了层次化的满意度关系：“多重正反馈 > 单一正反馈 > 无正反馈”。对于单个item而言，收到的正反馈数量越多，其相对满意度反映。

基于此，我们采用Pairwise Logistic Loss来训练模型，使其能够学习并区分这些不同层次的满意度偏好：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfcBXGCEryCtxP3vr42Zicr1XPhDaAY5fIWwCnv3ic3AonEF8pMJbJflibw/640?wx_fmt=png&from=appmsg)

其中D代表了所有的正样本对。

多维满意度代理指标：

尽管后验反馈为满意度的量化提供了宝贵的洞察信息，但其固有的曝光偏差和信号稀疏性是无法回避的局限。因此，EMER 从多目标优化的角度引入了互补的解决方案。

在大规模推荐系统中，多任务模型能为每个候选项提供丰富的先验信号（Pxtrs）。这些信号本质上都反映了用户满意度的不同维度。我们认为，提升某个信号的排序效果，就能提升相应维度的用户满意度，所有信号的排序效果同时提升，将共同促进整体用户满意度的提高。基于此，EMER 没有这些信号简单地融合成一个标签，而是将每个先验信号作为一个独立的监督目标，旨在优化每一个信号的排序性能AUC，鉴于AUC的不可微，我们采用了可微分的pairwise代理损失函数来近似 AUC 最大化，从而鼓励模型对Pxtr优item给出更高的分数。

label : 

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfxCzBKVAsEzqdQLUm3xF85eWxJ6fY5vDD3Heyib8HgicuQsSUrlrIyl8g/640?wx_fmt=png&from=appmsg)

单个pxtr的loss：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfOpcWvvH3RQAohawAeiaN7oheiavjYGWGqRHnyj0kKibzl1z2Lficv5ZmxA/640?wx_fmt=png&from=appmsg)

其中是模型预估分。所有Pxtrs的整体loss为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLflmIHIVYGLOwZHpyTgwc5SX56icnoPSKp3w1DFtINpYG5cU6smoV7XTQ/640?wx_fmt=png&from=appmsg)

其中是不同指标loss权重，具体计算逻辑将在“自我进化”方案中展开讨论。

多维满意度代理指标除了解决基于后验的曝光偏差和信号稀疏性问题，同时能够将更多维度（包含深层转化和延迟反馈的信号的预估值等信号，此类如果直接学后验信号，存在天级以上的延迟会丢失推荐系统的实时性；基于不同领域专业知识构建的跨团队、跨业务的信号）引入，让模型能更及时地、全面地理解用户满意度，从而在排序时做出更精准的权衡和决策。

最终loss为相对满意度和多维满意度代理指标的loss总和：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfJAHER41AKPfPrcDL4QabKmC2ZyjdmR2UAI2ribib0moicETNrndI2gyeg/640?wx_fmt=png&from=appmsg)

**三、智能优化：让模型“自我进化”，平衡多目标**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

在多目标优化中，不同目标间通常存在冲突，这使得寻求最优解成为一个巨大的挑战。为了解决这一问题，EMER 提出了一个名为“自我进化”的优化方案，其核心是一个“优势评估器”（Advantage Evaluator，简称AE），它能够动态、自适应地计算各目标损失的权重。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfTeo1fbuAXBMzwPiab0DuCLd62mN7PZ0qzvoyFic34diaZbLKYReFbiaP5Q/640?wx_fmt=png&from=appmsg)

3.1 对比 “新旧模型”，自动调权重

其原理是：不同于依赖静态权重配置的传统方法，EMER 能够根据当前模型相对于之前版本模型的性能表现，自动调整不同损失的权重。当某个目标表现下降时，优势评估器会增加其权重，促使模型集中优化；反之，则会减少其权重，去关注其他效果更差的目标。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfunrV5qBgk2Ll5icUMXL27rAEKCkrYgortFzLYGvJksCImf70psUL4GQ/640?wx_fmt=png&from=appmsg)

其中代表了评估模型效果的评估指标，针对不同的业务问题可以尝试不同的指标，本次我们也将在消融实验本分进行简单的讨论。分别代表当前模型和旧模型。由于模型实时训练，可以保存模型在线预估的结果作为而无需保存旧模型版本。

自我进化在多目标融合中具备明显优势：

* 高效且自适应：无需人工调参，即可高效优化大量多样的目标，在初版模型中成功完成了多达78个目标的融合且取得了全面提升。
* 动态与个性化：以按请求级别的细粒度计算，确保模型能持续适应不同用户的个性化偏好和同一个用户随时间不断变化的行为。
* 公平和准确性：每个pxtr通过基于时间的自我比较，有效解决了不同目标间数值范围不一致的问题，确保权重计算的公平和准确。

这种“自我进化”的训练方案使得 EMER 具备了“学习如何学习”的能力，从而实现了持续和自适应的性能提升。

***3.2离在线一致性：解决“解耦悖论”***

“离在线不一致”是一个业界常见挑战。在实践中，我们遇到了一个经典的“解耦悖论”问题：离线时长和互动 AUC 都很好，但上线后总互动量显著却下降了，出现了“离在线不一致”的问题。这背后隐藏着一个根本性的问题，互动pxtr中存在着观看时间的混淆因素：离线优化的单个item的互动累计概率（pxtr）和线上追求的单位时间内的互动密度（total interactions），目标从根本上就不一致。

* 离线训练目标：优化单个item的互动概率（pxtr），其目标是让用户对每个独立的推荐item产生互动的可能性最大化。
* 在线业务目标：用户有限的会话时间内，最大化总互动次数。这意味着我们需要增加互动的“概率密度”，即在单位时间内的互动效率。

为了缓解这个问题，我们提出了一个更合理的指标：单位时间互动概率（IPUT）：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfX6ic4pAycu6avvaPpnjY1qok7z8Ks0Hg6heoZ0fhr2J2X1GdQjUEC4g/640?wx_fmt=png&from=appmsg)

通过将优化目标从 pxtr 转化为 IPUT，我们将模型的学习方向从“最大化单次互动的可能性”，精准地调整为“最大化单位时间内的互动效率”。这一方法从根本上消除了“解耦悖论”，显著提升了离线评估与在线业务表现的一致性，为模型离线的高效迭代奠定了坚实基础。

**四、落地效果和实验分析**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

***4.1 线上AB实验***

此前，快手精排的最终排序是基于融合公式(fusion formula，后面简称FF)，对每个PXTR进行变换后，通过相乘得到最终的排序分数。即一次请求中每个视频的打分可以形式化地写为。本次实验，我们在快手两个主要场景（快手极速版和快手主APP）上分别使用了机制模型进行打分，并且进行了线上的AB实验。

下面的表格是AB实验的双重差分结果。可以看到，EMER相较于融合公式的方法，在推荐系统的核心指标如LT、时长、vv和互动等指标上都取得了显著的提升！而目前的LT折线图结果则表明，LT仍然有不断上升的趋势。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfPg6g0Bt1LGyVtNc4dY1wf9nibGbmYnYtACKFHWhdAn7RJMpznPyp3pg/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfHVrWp2S1DIlyIvUibEG1pbbyiaZiahPwsO3Xxtt0vY5QQMXBxSrr3NWHQ/640?wx_fmt=png&from=appmsg)

***4.2 PXTR的一致性分析/模型在用户各维度满意度上的排序能力***

为了评估最终的排序结果和主要PXTR信号之间的一致性，我们计算了不同的排序融合方式得到的最终排序和不同pxtr（主要包括观看时长pvtr，有效播/长播/完播 pctr/plvtr/pcpr，点赞/关注/评论/转发 pltr/pwtr/pcmtr/pftr）之间的GAUC。数据如下表（表中UREM为业界最新的使用模型融合的尝试）所示，EMER方法得到的排序在大部分pxtr上均取得了最好的一致性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfvrNUfFpZfAQVEqRWTrTicObqiaFwGjtibSB1pSNG7LibRJA9TfxH9zjX1A/640?wx_fmt=png&from=appmsg)

***4.3 OneRec链路中的落地尝试***

我们同时将该方案在OneRec链路中上线，作为reward model来生效。实验结果显示，我们的适配方案可提升App停留时长+0.56%，七日留存提升0.149%。同时，该方法在快手其他业务场景也在积极尝试中。

4.4 消融实验分析

为了验证 EMER 模型里，到底是哪些设计在 “真正发力”，快手策略算法团队做了一组 “消融实验”。实验结果表明，模型中各个设计均对最终性能具有显著影响。

表1: EMER和消融版本的离线GAUC比较

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfCqsu6icBq8KGw3TwSWnMcc8IGiaaWTKYgw41HvmzurESaQH4zuE5Y4Gw/640?wx_fmt=png&from=appmsg)

表2：EMER和消融版本的在线A/B效果比较

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfr62a6W1icjH460vVYTTichnRWTRuA72XwobOCcytuHlibUgk5jAGq06icg/640?wx_fmt=png&from=appmsg)

#### 4.4.1 显式建模比较关系至关重要

EMER 通过请求级分组、Transformer 交互网络和归一化排名（Normalized Ranks），显式建模候选集内部的相对排序关系。为了验证该机制的作用，构建变体模型 EMER-NoComp，对每个候选对象进行独立打分。

结果显示，EMER-NoComp 在离线指标（见表1）与线上 A/B 测试（见表2）中均出现性能下降。这说明孤立地评估候选对象会丢失其在上下文中的相对信息。因此，显式建模候选对象间的比较关系对于提升排序质量具有关键作用。

#### 4.4.2 多维监督信号的协同作用

EMER 的监督信号由两部分构成：基于用户实际行为的后验的相对满意度信号（Posterior）与基于多维先验的满意度代理信号（Prior）。为评估其各自贡献，分别构建 EMER-NoPost（移除后验信号）与 EMER-NoPrior（移除先验信号）变体。

实验结果显示，移除任一信号均导致性能下降，表明两类信号在模型训练中均发挥重要作用。其中，EMER-NoPrior 的性能衰退更为显著。

#### 4.4.3 自进化机制保障多目标均衡

为验证自进化优化的作用，构建 EMER-NoEvolve 变体，采用固定权重训练。结果显示，该变体出现严重指标失衡：观看时长上升，但播放量（-2.347%）、转发（-8.418%）和评论（-8.109%）显著下降。即便我们尝试进行进行大量人工调参，静态权重方案仍无法超越自进化策略，验证了其在动态权衡多目标中的必要性。

进一步分析（见图1）表明，EMER 的多目标损失分布更均匀、集中且整体值更低，而 EMER-NoEvolve 损失波动大、分布分散。这说明这说明，自进化机制不只是在“调权重”，更是在持续引导模型的学习方向，避免某些目标“抢跑”或“躺平”，提升训练稳定性。

图1：loss分布比较：EMER vs. 消融版本EMER-NoEvolve

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfMRnibQ9YF9g5P3b3u8FWBug2Prns0nMia0teHiahrkuEg1aRScgXJd6qg/640?wx_fmt=png&from=appmsg)

#### 4.4.4 IPUT 对齐离线与线上效果

为验证 IPUT（单位时间交互概率）的作用，构建 EMER-NoIPUT。相比之下，基于 IPUT 构建的 ，其离线增益与线上表现高度一致。这说明 IPUT 通过建模即时反馈密度，有效对齐了离线训练目标与真实用户满意度，是保障模型实用性的关键设计。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfW5iaqgicUiamwLVwDEjr7shh8JRIUNcEGWrvoDdgGq3NBUldrKJoS56cw/640?wx_fmt=png&from=appmsg)

4.5度量分析

在自进化框架中，优势评估器需准确判断模型改进程度。我们对比了HitRate@K 、MEAN@K 和DCG@K 三种评估方式（以pxtr 为正信号）：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfpS3vwKicP923jibOK9rkfnGPn8Exc3c2pZnEibOczzMGccicphRdJQpl6A/640?wx_fmt=png&from=appmsg)

结果表明（见下表），DCG@K在几乎所有 GAUC 指标上表现最佳。因其同时考虑 item 相关性与排序位置，更能反映真实场景下的用户注意力分布。最终，EMER 采用DCG@K作为优势评估的默认指标，以确保模型向“高质量item前置”的方向优化。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0Evj3ict02OUSuZWV9wxHCLfZaFlVyWPlmJdpVxfHJfdoxhm82b1l2DQMegc4XnRfkiaV6URcLBziaRQ/640?wx_fmt=png&from=appmsg)

**五、总结**

![图片](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=4)

从 “人工调公式” 到 “AI 自进化”，EMER为排序模型的优化带来了一种全新范式。首次系统性提出个性化多目标排序场景下用户满意度缺乏统一监督信号、离在线指标不一致、候选集间关系建模不足三大核心难题。并提供了可落地、可验证的一体化解决方案。

目前，EMER 已全面部署于快手主站和极速版单列场景，取得了显著消费和留存收益，验证其在真实业务场景中的实用性和大规模可落地性。我们仍在持续探索模型学习目标的优化，比如如何定义并挖掘更能代表用户满意度的信号。对于行业来说，这套 “可落地、可验证” 的方案，或许能为更多企业的推荐系统优化，提供一份切实可行的参考。后续有进展也会发布出来跟大家交流。

【END】

![图片](https://mmbiz.qpic.cn/mmbiz_png/fx0l2Sibe0L2nssvtkSUhR9L9cJ0zaNGKZlE03JoPVyd7kOVZLjibGQqXSicffWuwONIhwiantv7E5zj7qNw5K1yqw/640?wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=36)

点个在看你最好看