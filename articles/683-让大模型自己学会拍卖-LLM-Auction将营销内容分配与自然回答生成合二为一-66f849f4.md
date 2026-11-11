---
title: '让大模型自己学会拍卖！LLM-Auction将营销内容分配与自然回答生成合二为一'
company: 阿里妈妈
tag: 广告
date: 2026-05-16
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497300&idx=1&sn=68108cfc6fe78f2bbc8d44c48557896b&chksm=c151ded37a68030155612d3e7e263b1298a03d0b5637189741ed6c0ddf105246237d6354b117&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
**导语**：当 ChatBots、AI 搜索等大模型应用成为用户获取信息的主要入口，营销内容该如何融入生成式回答？固定展位式的在线营销方案还能否成立？如果拍卖对象不再是离散位置，而是大语言模型的输出分布，机制设计又该如何定义“最优分配”？本文介绍阿里妈妈展示机制策略团队在 AI Native 营销机制上的最新探索：**LLM-Auction**。

## 概述

随着 ChatGPT、Perplexity 等基于大语言模型（Large Language Model，LLM）的应用重塑用户的信息获取方式，在线营销的商业化范式也在发生变化。当前工业界常见做法仍是“外挂式”营销位，即在 LLM 回复的固定位置插入营销卡片。这沿用了传统在线营销的展位思路，却没有真正利用 LLM 的推理、理解和生成能力。

![case.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYP52ze9YeBq54uQmQA3qn27zSEsSc7wjkOHWSmeGoZ5MfaOYYb7WtYhTYxWBXeSmEf21fpr3Fd5aHXjTLP7WlgbvbS6bANgLCg/640?wx_fmt=png&from=appmsg "图1 当前业界的主要营销形态（左：Perplexity；中：ChatGPT；右：Google AI Mode）")

图1 当前业界的主要营销形态（左：Perplexity；中：ChatGPT；右：Google AI Mode）

学术界前沿逐渐将目光转向 LLM 原生营销，即让营销内容以原生文本形式自然融入到LLM生成回答结果中的营销形态。这一形态变化背后，是机制设计对象的变化。传统机制分配的是有限、离散、位置明确的展位；LLM 原生营销要分配的，则是一个由上下文、用户需求、候选内容和客户出价共同决定的输出分布。这带来两个核心挑战。第一，经典位置拍卖失效，因为“被分配到哪里”不再有清晰的离散定义。第二，现有方法很难同时兼顾上下文理解与计算效率：若先拍卖后生成，就难以刻画营销内容与周围文本之间的外部性效应；若先生成后拍卖，又需要随客户数量呈线性增长的 LLM 推理成本，难以支撑高并发场景。

为了解决上述挑战，LLM-Auction 的核心思路即让 LLM 自己学会拍卖。具体来说，我们将营销内容分配与回复生成统一建模为偏好对齐问题，使 LLM 的输出分布本身成为分配规则。在线服务阶段只需一次生成，就能同时完成自然回答生成和营销内容分配，在不增加额外 LLM 推理开销的前提下取得更高的分配效率。

LLM-Auction的论文已经上传至arXiv，欢迎大家阅读和交流。

论文：LLM-Auction: Generative Auction towards LLM-Native Advertising

作者：Chujie Zhao, Qun Hu, Shiping Song, Dagui Chen, Han Zhu, Jian Xu, Bo Zheng

链接：https://arxiv.org/abs/2512.10551

## 1. 背景

当 LLM 驱动的 ChatBots 和 AI 搜索成为流量入口，营销内容不再只能以独立卡片形式出现在回答之外。举例来说，当用户询问“帮我规划一个 5 天的夏威夷旅行”时，更原生的方式不是在回答旁边附加卡片，而是在行程规划中自然融入住宿、餐饮、出行等相关推荐。营销效果来自内容与任务场景的结合，而不是单纯来自展位曝光。

![llm-native-back.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYPW4awURTFviaq1zia87LHzaLRXb4VXmJOHpmiau1uKKw58JKTIPGX7Zd6mBpWgLUCeNRpYvib2TTYH9RbGmWjW6qMsfpF3gZqdXQ0/640?wx_fmt=png&from=appmsg "图2 外挂式营销 v.s. LLM原生营销及相关拍卖机制对比")图2 外挂式营销 v.s. LLM原生营销及相关拍卖机制对比

这也意味着，客户出价影响的不应只是某个固定位置，而是 LLM 在当前语境下如何组织回答、是否纳入某条营销内容、以及以什么方式纳入。换言之，分配从“谁占哪个位置”变成了“输出分布如何因出价而改变”。

然而，这种变化让传统机制面临两个核心挑战：

**（1）传统拍卖机制的失灵：**

广义二价（Generalized Second-Price，GSP）等经典机制依赖预先定义好的离散位置：位置越靠前，价值通常越高。但在 LLM 原生营销中，营销内容可以出现在不同段落、以不同语气和粒度被表达，并与上下文互相影响。离散位置不再足以描述分配结果，传统机制也就无法直接套用。

**（2）现有拍卖机制的两难：**

现有方法大致可以分为两类：

* **先拍卖后生成**：如RAG-Auction[1]，先通过拍卖决定纳入哪些营销内容，再让 LLM 基于分配结果生成回复。这类方法推理开销低，但需要提前确定内容数量和位置，难以建模“LLM生成的自然内容对目标营销内容的影响”的外部性，导致分配效率次优。
* **先生成后拍卖**：如Token Auction[2]和MOSAIC[3]等，先生成多个候选回复，或在生成过程中聚合多个客户偏好，再通过拍卖选择最终输出。这类方法更能感知上下文，但推理成本通常随客户数量或候选回复数增长，在工业级高并发场景中会成为瓶颈。

面对上述挑战，LLM-Auction 提出了第三条路径：**将拍卖直接融入生成过程**。模型不再是拍卖后的文案生成器，而是机制的一部分；一次推理既生成回答，也给出分配结果。

## 2. 方案：LLM-Auction框架

要把拍卖融入 LLM 生成过程，必须回答三个递进问题：第一，没有固定展位，机制到底在分配什么？第二，如何让 LLM 学会按机制目标生成，同时捕捉上下文外部性？第三，在新的分配设定下我们该如何计费？

LLM-Auction 框架正是沿着这条逻辑展开：先把输出分布定义为分配对象，再把机制目标转化为偏好对齐信号，让 LLM 在一次生成中完成分配与回复生成，最后基于分配空间的性质设计计费规则。下面我们展开具体的介绍。

### 2.1 问题建模：把输出分布作为分配对象

第一个问题是分配对象。如果沿用“先定义位置，再决定谁被分配”的建模方式，我们必须提前规定营销内容数量、展示位置和表达形式，也无法评估内容与上下文之间的相互影响。因此，LLM-Auction 不再把某个离散位置作为分配对象，而是把给定用户请求、用户画像、候选营销内容和客户出价后的 LLM 输出分布作为分配对象。

形式化地，考虑个客户，其中第  个客户拥有私有价值  和固定营销内容 。给定上下文 （包含用户问题 、用户画像  和候选营销内容集合 ）以及出价向量 ，LLM  将输入映射为输出分布 ，并从中采样最终回复。拍卖机制为 ，其中  同时作为生成模型和分配规则， 为计费规则。机制目标为：

其中表示第个营销内容在输出分布上的期望效果指标（如点击率CTR、转化率CVR等）；表示营销内容植入数量、格式、真实性等约束，KL散度项用于限制模型过度偏离预训练LLM。这样一来，机制目标就不再是“把谁放到哪个位置”，而是让模型在分布层面对客户价值、内容相关性和用户体验进行动态权衡。

### 2.2 生成式分配：从机制目标到模型偏好

定义了分配对象之后，第二个问题是如何优化它。由于 LLM 的输出分布本身就是分配结果，优化分配规则可以转化为对 LLM 进行偏好对齐训练：让模型更倾向生成全局机制目标更高的回复。这样，拍卖不再是生成前后的外部决策，而是通过训练内化为模型的生成偏好。

#### 2.2.1 机制奖励模型

偏好对齐需要比较同一输入下不同回复的优劣。但是真实在线场景中，同一用户请求和同一组出价通常只会产生一个展示结果，很难直接获得多个候选回复的**反事实反馈**。为此，LLM-Auction 构建了基于效果预估的奖励模型，用参数化模型  估计第  个营销内容在回复  和上下文  下的点击率或转化率。

与传统在线效果预估不同，这个模型只用于离线训练，因此可以把完整回复作为条件输入，显式学习营销内容与周围文本之间的外部性。奖励函数定义为：

该奖励将客户出价、预估效果与体验约束统一起来，为 LLM 对齐训练提供机制层面的反馈信号。

#### 2.2.2 迭代式奖励-偏好优化

基于奖励模型，我们可以使用经典的偏好对齐方法（如DPO等）对LLM进行后训练。但是，直接用奖励模型训练 LLM 会遇到**分布偏移**问题：随着模型逐渐优化，其生成分布相比预训练分布会发生显著偏移，导致效果预估模型的准度随之下降。LLM-Auction 因此提出迭代式奖励-偏好优化（Iterative Reward-Preference Optimization，IRPO），交替更新效果预估模型和 LLM 策略，逐步缓解偏移的影响。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYNPaia1Ck8BU2nYpmjKQ4ndyWxIJjVAvJzYC58icz830LJRcYQl6k1Z31K2GcgL3ceiboH9lMUl96GicC3KnCuXu6qicWcZjVCPdWzc/640?wx_fmt=png&from=appmsg "图3 LLM-Auction训练流程图")图3 LLM-Auction训练流程图

IRPO具体包括两个阶段：

* 在线阶段：固定LLM，部署上线收集用户真实反馈，更新效果预估模型。
* 离线阶段：固定奖励模型，对每个训练样本采样M个回复，计算奖励分数，选取最高奖励回复作为正例，构建偏好对进行DPO训练。第轮的DPO损失为：

其中为与获胜回复奖励差超过阈值的负例集合。

#### 2.2.3 生成式分配的机制性质

经过偏好对齐后，我们期望模型学到的生成式分配规则具备可解释、可参与的机制性质。一个可落地的拍卖机制不仅要提升效率，还要让客户相信“出价会以可预期方式影响结果”。我们证明了 LLM-Auction 的分配满足随出价的**单调性**：客户提高出价，不会获得更差的期望效果。

同时，由于分配对象从离散展位变为连续输出分布，LLM-Auction 还呈现出**连续性**：出价的微小变化会带来分配结果的平滑变化。这区别于传统离散展位拍卖中常见的阶梯式分配结果，也说明 LLM-Auction 不是简单地把营销信息塞进回答，而是在分布空间中形成可解释的分配规则。该性质也进一步影响了后续计费规则的设计。

### 2.3 从分配性质到一价计费

最后，在分配性质的基础上我们来回答第三个问题，即如何计费。在传统离散展位场景中，往往采用广义二价计费，即计费是客户获得当前分配结果所需的最低出价。但在 LLM-Auction 的连续分配空间中，微小出价变化只会带来微小分配变化，**传统“二价”概念会趋近于客户自身出价**。因此，LLM-Auction 采用一价计费规则：

即客户付费等于其出价乘以对应营销内容的期望效果指标。我们进一步证明了，一价计费在两类客户行为模型下具有良好的激励性质：

* 对于效用最大化（Utility Maximizer）客户，存在混合策略纳什均衡。
* 对于带ROI约束的价值最大化（Value Maximizer）客户，真实出价是占优策略，满足激励相容性。

## 3. 实验结果

### 3.1 实验环境

当前LLM 原生营销机制设计的一个关键瓶颈在于缺乏标准化、定量化的大规模评估。此前研究多依赖定性分析或小规模实验，难以复现真实营销竞价中的规模、反馈和上下文复杂性。为此，我们构建了一个基于 LLM-as-a-judge 的仿真环境，用于模拟 LLM 应用中的完整营销投放链路和用户反馈流程。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYN5fkKNiaOvMiaia5DCUprDeGmFlEuOMO3ZaKYiancKRJnN8y6szibse7xBibyBgXUlfaqIdnJFZ62RDDnyIz1Ec6CbMSV8h1kteD1Iw/640?wx_fmt=png&from=appmsg "图4 LLM原生营销仿真环境示意图")图4 LLM原生营销仿真环境示意图

该环境包含两个模块：① Ad-LLM 负责与机制协作，生成融合营销内容的回复；在 LLM-Auction 中，它就是训练得到的 LLM 自身。② User-LLM 模拟用户 query 生成、阅读回复后的点击反馈。

我们构造了 3k 个合成用户画像，并由 User-LLM 为每个画像生成 5 个 query，共得到 15k 个用户 query。候选营销内容池来自淘宝，覆盖 50 个类目的 100 个真实营销素材。对每个 query，我们为每个候选内容从 1 到 100 的整数区间随机采样出价，并将 15k 样本划分为 12k 训练样本和 3k 测试样本。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYPMUmgnwncmUibyZ50jeFib6eYG0KIMbxeHkDuReV5yZ29b5qRSaNsCr5dw5vW56w0Fw4EbKZGFHibApFH40x2wr74GTAF09te4u0/640?wx_fmt=png&from=appmsg "图5 LLM原生营销仿真环境的示例（蓝色下划线标注为营销内容相关的文本）")图5 LLM原生营销仿真环境的示例（蓝色下划线标注为营销内容相关的文本）

图 5 展示了仿真环境中的一个具体示例，其中营销内容需要以 `@营销标题@[营销ID]` 的格式插入。更多实现细节请参阅论文。

### 3.2 分配效率对比

我们将LLM-Auction与四个baseline进行了对比：

* Pre-trained LLM：未经过微调的base LLM，本文所有实验均采用Qwen3-4B作为基座模型完成。
* RAG-Auction[1]：一种先拍卖后生成机制，先基于检索相关性完成广告分配，LLM基于分配结果生成融合广告输出响应。
* MOSAIC[3]：当前最先进的先生成后拍卖机制，推理过程中并行采样多个LLM输出响应，再通过拍卖选择最优响应输出。
* LLM-Auction (Oracle)：在仿真环境中直接获取用户对同一问题下不同 LLM 回复的反馈，用于 LLM 后训练。该基线近似理想效果预估模型，可作为 LLM-Auction 的上界参考。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYODm3OA1e9XzXFdhxUuk74n1WJfKz0RtjwUssKwvvfn2IHIKefh6hOjYFC7JmyTw5giakibqicydxFdZU7KMuh3PWoNQfNneicsDxY/640?wx_fmt=png&from=appmsg "表1 机制分配效率对比实验")表1 机制分配效率对比实验

从表1中可以看出，LLM-Auction在收入和奖励（综合考虑收入与用户体验）两个机制效率指标上均大幅领先所有基线方法。相比当前最优的后生成机制MOSAIC，LLM-Auction收入提升59.1%，奖励从-15.27提升至81.86，且不需要额外的LLM推理开销。Oracle版本的LLM-Auction的性能进一步预示了，随着效果预估模型精度的提升，LLM-Auction仍有可观的提升空间。

### 3.3 机制性质验证

除分配效率外，我们也验证了 LLM-Auction 的机制性质。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYM4OHsp0ojELd7ZgSzNuvPkGUrCjickyQESKSkvRicTrbhkUUM2BtAPeticqF8t17lwJeQrDlmEwNfktdqBibEiaiaGIQdn1dsxBmqcg/640?wx_fmt=png&from=appmsg "图6 机制性质验证实验")图6 机制性质验证实验

为验证单调性，我们在测试集上进行出价扰动实验：对每个样本随机选择一个候选营销内容扰动其出价，并用用户对该内容的点击量度量分配结果。结果如图6（a）所示，预训练 LLM（Epoch 0）的分配结果与出价几乎无关；随着训练进行，二者相关性逐渐增强，并在 3 个 epoch 后实现单调分配。

为验证连续性，我们固定一个训练集中未出现过的用户 query 和一个目标营销内容，将该内容的出价以最小间隔 1 从 1 提高到 100。对每个出价采样 200 个 LLM 回复，并统计目标内容点击次数。如图6（b）所示，分配结果随出价平滑变化，与传统离散展位拍卖的阶跃式变化明显不同，也进一步支持了一价计费规则。

此外，我们也进行了消融实验与定性的结果分析。通过消融实验我们验证了核心模块的效果：①完整的LLM回答作为输入对于分配规则的训练有显著正向效果，②迭代式的IRPO训练可以缓解分布偏移，使机制性能稳定提升。同时，定性的案例展示出：①相比预训练 LLM，LLM-Auction 对营销内容的分配有更好的语义匹配性，并会将营销内容自然融入回答叙事；②LLM-Auction会提高高出价内容在回复中的呈现优先级。更详细的结果请参阅论文获取。

## 4. 总结与展望

LLM 原生营销的关键不只是“把营销内容写进回答”，而是当商业化对象变成 LLM 输出分布后，如何重新设计兼顾效率、体验、激励和计算成本的机制。LLM-Auction 将拍卖机制设计与 LLM 对齐技术结合，提出了首个统一分配与生成的基于学习的机制框架：通过偏好对齐让 LLM 自身成为分配规则，天然建模上下文外部性，并在不增加额外推理开销的情况下获得更高分配效率。

LLM-Auction是迈向基于学习的 AI Native 营销机制的一步探索。未来我们将继续推进三个方向：

1）更大规模、更真实的评测基准：当前仿真环境在规模、多样性和用户行为模拟上仍有局限，未来我们会搭建工业规模的数据集，并结合Agent等技术对用户行为进行更好的建模[4,5]，打造更可靠的机制评估体系。

2）更优的计费规则：LLM-Auction目前采用简单的一价计费规则，未来会进一步探索基于学习的动态计费规则，在更广泛的客户行为设定上实现更好的激励性质。

3）更全面的价值体系：超越当前点击归因设定，探索更契合 AI 原生应用的基于内容的效果度量方案，并在奖励函数中引入回答可信度、营销内容忠实性等更完善的用户体验与业务约束指标。

参考文献

[1] MohammadTaghi Hajiaghayi, Sebastien Lahaie, Keivan Rezaei, and Suho Shin. Ad auctions for llms via retrieval augmented generation. In Advances in Neural Information Processing Systems (NeurIPS), volume 37, pp. 18445–18480, 2024.

[2] Paul Dutting, Vahab Mirrokni, Renato Paes Leme, Haifeng Xu, and Song Zuo. Mechanism design for large language models. In Proceedings of the ACM Web Conference 2024, WWW ’24, pp.144–155, 2024.

[3] Ermis Soumalias, Michael Curry, and Sven Seuken. Truthful aggregation of LLMs with an application to online advertising. In The Thirty-ninth Annual Conference on Neural Information Processing Systems (NeurIPS), 2025.

[4] Wang, Lei, et al. User behavior simulation with large language model-based agents. ACM Transactions on Information Systems 43.2 (2025): 1-37.

[5] Liu, Fei, et al. Recoworld: Building simulated environments for agentic recommender systems. arXiv preprint arXiv:2509.10397 (2025).

# 🏷 关于我们

我们是阿里妈妈展示机制策略算法团队，致力于不断优化阿里展示营销技术体系，驱动业务增长，推动技术持续创新；我们不断升级架构以支撑阿里妈妈展示营销业务稳健&高效迭代，深挖商业化价值并优化客户投放效果，孵化创新产品和创新商业化模式，优化营销生态健壮性；我们驱动机制升级，并已迈入 Deep Learning for Mechanisms 时代，团队始终走在技术创新前沿，在ICML、KDD、WWW、WSDM、CIKM等领域知名会议上持续发表高水平论文。真诚欢迎具有大模型、机器学习和机制设计背景的同学加入我们！

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=14)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=15)

喜欢要“分享”，好看要“点赞”哦ღ~