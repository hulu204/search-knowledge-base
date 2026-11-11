---
title: 'SIGIR 2026｜OxygenSearch 之生成式检索偏好对齐 RAD-DPO 技术解析'
company: 京东
tag: 搜索
date: 2026-06-23
url: http://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247516001&idx=1&sn=49f66ab9abd63c8702f5b8d9f2c0d9f2&chksm=f9f228b2ce85a1a4efff37c8e2098d802dc0cf90ff44e40502ea51b908a33b6870d4f304fa9a#rd
account: 京东零售技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EgokX6dYz7w5aQ0Oibibh5lYSfCl3kx7PlsBVoiapO6lHzABlkGycUHpcPCnlib3nicCTDFjy41HzcuHEggVgg0Fd21uoEQlSuUJYc/640?wx_fmt=png&from=appmsg)

**本文导读**

本文针对OxygenSearch生成式检索在电商搜索中的偏好对齐难题，提出鲁棒自适应去噪偏好优化（RAD-DPO）方案，通过 session 级多标签全局对比、Token 级梯度阻断与动态奖励加权，缓解多正例概率挤压、公共前缀误伤和伪负例噪声问题，提升主站搜索生成式检索的效果与鲁棒性。

基于本工作的论文已被 SIGIR2026 接收，欢迎阅读交流。

· 链接：https://arxiv.org/abs/2602.23964

· 论文：RAD-DPO: Robust Adaptive Denoising Direct Preference Optimization for Generative Retrieval in E-commerce

· 作者：Zhiguo Chen, Guohao Sun, Yiming Qiu, Xingzhi Yao, Mingming Li, Huimu Wang, Yangqi Zhang, Songlin Wang, Sulong Xu

**01**

**背景**

生成式检索（GR）的技术范式

在电商搜索领域，“生成式检索”范式逐渐兴起并得到越来越多的关注。生成式检索通过将海量商品（SKU）编码为结构化的语义 ID（Semantic ID, SID），将检索任务转化为一个自回归生成任务 。

• SID 的构建原理：通常采用层次化聚类（如 RQ-VAE 或 RQ-Kmeans）构建。这种“由粗到细”的层级结构使得模型能够通过Beam Search在十亿级商品库中实现毫秒级响应。

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EywgCx2X0hUvsaejrRWvL2LFXqV9XvIcy4cGCXqyOsibxrRmFj1jt9puOaRhVh5273lO9ClZB1jETKsL9ftwRMn6N4JHicNqPm8/640?wx_fmt=png&from=appmsg)

• 训练阶段：一般分为语义对齐预训练（Pre-train）、个性化对齐指令微调（SFT）和偏好对齐优化（DPO/RL）三个阶段 。

## 为什么需要DPO？

OxygenSearch针对的电商场景拥有极其丰富的隐式偏好信号（如曝光、点击、加购、下单）。传统的精排模型通过交叉熵或序关系损失来吸收这些信号，而 GR 模型在经过 SFT（指令微调）后，仍需进一步对齐用户意图 。相比其他强化学习算法如 GRPO、PPO、DPO 的优势在于其不依赖额外的 Reward Model，实现简单且样本获取成本低。

## GR场景下的特殊挑战

不同于自然语言处理（NLP）任务，生成式检索下的 DPO 具有以下独特性 ：

1. 梯度冲突（Shared Prefixes）：SID具有层级性，正负样本常共享类目前缀 。标准 DPO 在惩罚负样本时，会无差别地打压这些正确的前缀路径，导致类目生成的震荡 。

2. 噪声敏感（Pseudo-negatives）：电商的“未点击”并不等同于“不相关”，可能是位置偏见导致的。强行对比这种“伪负例”会扭曲模型的语义表示 。

3. 概率挤压（Squeezing Effect）：电商 Query 通常对应多个相关正样本（Multi-label）。打压负样本（尤其是难负样本和伪负样本）的同时可能会压缩长尾正样本的概率空间 。

**02**

**算法演进：主流偏好对齐方案对比**

我们对现有的 DPO 类算法进行了调研整理，选取其中的代表性方法总结如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7GTlf9ynzOdY5mEjrOdE5PdHnTT4ycKyuVLh2YkjKFD05UgPkuYg780OaO4XvndpxuNj59KBZO7bOTzAQJpaDlkbSK2pUQpHeo/640?wx_fmt=png&from=appmsg)

整体趋势可以概括为：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FBPDOYm3Ku6GTblcxsU1csVcNnicwqWQ1ReZZjrhJNquicvtJqJYibkrNqUdTLkWINicR7jIuLERWYHlYibTWYEmCW0qFka535RibdE/640?wx_fmt=png&from=appmsg)

在生成式检索/推荐后训练对齐领域，逐渐有工作开始针对SID的层次化结构进行token级的细粒度优化，例如 APAO 和 OneSearch-V2 提出的 TPMA-GRPO，他们采用了不同的策略对 SID 前缀 token 做单独建模增强。

一句话总结：**DPO 变体的演进主线是从“简单 pair-wise 序列级偏好优化”，逐步走向“低成本、多样本、token 级、噪声鲁棒、prefix-aware 和结构感知”的优化范式；RAD-DPO 的核心定位是把这些趋势进一步落到生成式检索的 SID 结构和伪负例问题上。**

**03**

**RAD-DPO 核心技术方案：面向 SID 结构的鲁棒偏好对齐**

前面我们分析了标准 DPO 在生成式检索场景下的三个核心问题：**公共前缀被误伤、隐式反馈噪声敏感、多正例概率挤压**。RAD-DPO 的设计目标，就是把通用的序列级偏好优化，改造成更适合 OxygenSearch 电商 SID 生成的结构化偏好学习方法。

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7H6Z6vUNIP54Vicv7fo3Xj4z5PgNcibyYia3yaleT8zye76Ss59icG0zjBu8dfDa00nLicMhSGHGL9nKOiaQw8ndYcavEVMXmwDGXwSo/640?wx_fmt=png&from=appmsg)

从整体上看，RAD-DPO 由三个相互配合的模块组成：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7E4ebPdBXTdibNL7l5ypInrnmX3rmSPA3mLuUtR7CcKYia5TVNrqHfxkTH6cAXibTv109picaeVJveombHN2lOpWOut8xEZjoibqe7w/640?wx_fmt=png&from=appmsg)

## 从 pair-wise DPO 到 session 级偏好学习

标准 DPO 通常以三元组形式训练：![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7Hkwrzv5HribfczACMWHOpj7jb9iayCIHcNro7uYtZkoiaI2ia7ibJvonM0xibfyAIreQgU3CXhPd8jsSztbt0yW8Oib0lPmng3b9WIrw/640?wx_fmt=png&from=appmsg)

其中![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7HQhMYhVKq6ycHMPCGk5c9W9HNP08JeUUsYyrrDGJBKuBN4f7fpJg1bibHZcqCvVcU7yJGYCsEU6euaibuttNlrBjA4ZrbhsBes0/640?wx_fmt=png&from=appmsg)是输入 prompt，![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7HG8Qdv2e4Nyt51lUe0u3yBBJRFFp8NZkYcSjuutwBFqvCiasBncLBpBPiaNYgcwuICJ0GsPjNzeL3Q3lzicYzEp8VF12ZmdXPBhQ/640?wx_fmt=png&from=appmsg)是 preferred response，![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7HSe3Vx98zU6Vibba3KVTvRgUDZch068ybJMm54fcvLIm4iaR4c61WbiawSEvTia4ibHo8raz5vMib9Eq6obsO5jRpVCsX0Ck3IzSbibU/640?wx_fmt=png&from=appmsg)是 rejected response。这个范式在自然语言生成中较为自然，但在电商搜索中存在两个不匹配点：

第一，一个 query/session 下往往不止一个正样本。用户可能点击多个商品，也可能点击后下单其中一个商品，这些行为都代表不同强度的正反馈。

第二，一个负样本也不一定是真负样本。曝光未点击可能来自位置偏差、图片吸引力、价格因素或随机点击行为，而不一定说明商品与 query 完全无关。

因此，RAD-DPO 不再把样本拆成孤立的正负 pair，而是以 session 为单位构造训练样本。对于输入 prompt ![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FeCnQTaJVACHpyclGQeNyHPpIXgeTukOrAyPAMolw5HhzFjibibayvic4bicPDkDMCJRxLpbdURKO3UhGouUDMz3qX2qtOto0RC9A/640?wx_fmt=png&from=appmsg)，将用户点击、下单等正反馈商品组成正样本集合：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7H2JSTUVIxKQt8FSGfJialu4Cb94icibwue9xOHsU4wdhoySfVMUQ6Xcd6zV4pXhqpeRhBJJ61t1STA4hlsBGwLCvSZBPoDnzR82w/640?wx_fmt=png&from=appmsg)

将同 session 下曝光未点击商品以及从全局候选池中采样的商品组成负样本集合：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7ELeXWSDStd9ber03ajG8QNNqJWtuhu0h8Qu7LSY4PlO68YUibTavbzYAyRgJNiaXEGCK4nriajW1v27oGPkaw6OBZaH8ia3CAIOibg/640?wx_fmt=png&from=appmsg)

基于这种样本组织方式，RAD-DPO 的总目标由两部分组成：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7HiauVlpYdxU6icfPQHSnABDoNzL6IkJyvIS2m044z3ax5Hq07ibRKibs7Wp2ibWPlvVs6LiaJiciak8mSWZiaR25vQoOkk5yJYIrASVjia4/640?wx_fmt=png&from=appmsg)

其中，![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7Giaic4FumbdA5L7hg4ubjrPjYqVs6LKpDmEFsOtlhIaaIthwLMXn2LdtmxewibKliaLMG5sHGj1PiaofMOfcC95JhVEhNbYhiagGZVE/640?wx_fmt=png&from=appmsg)负责提升所有正样本的生成概率，避免只偏向单个强正例；![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7HYXicWvUjmFgVnb8nFSibPQjiaS4QLhZN7hyCTryyibNYsYZAibcedG6wWCHOr3yVpwgbRSbH1l87qXswMuibDdSNqEfBnDGMOAORyE/640?wx_fmt=png&from=appmsg)负责建立正负样本之间的偏好间隔。

这个设计可以理解为：**SFT 项负责“扩大正样本覆盖”，Preference Loss 负责“拉开正负差距”**。

## MLGC：多标签全局对比，缓解正样本概率挤压

在电商搜索中，一个 query 往往对应多个合理商品。例如用户搜索“跑步鞋”，点击了 A 品牌，也可能加购 B 品牌，甚至最终下单 C 品牌。这些商品都在不同程度上满足用户需求。如果训练时只把某一个商品作为唯一 winner，其他有效商品就无法被显式提升，甚至会在概率竞争中被压低。

为此，RAD-DPO 首先在正样本集合上加入全局 SFT 项：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7G4hxmn8XM0x9hcmr254FibsrcmvDDQbf4eqUkEgANCPk0GvtEVVvXBcuW5rAQSz7xS9ftyLia0mwJgXRzhbfzE4OmU7bLYpvxtY/640?wx_fmt=png&from=appmsg)

这个公式的含义很直接：同一个 session 中的所有正反馈商品都应该被提升，而不是只提升一个“最强正例”。这部分可以缓解 pair-wise DPO 中的概率挤压效应，即某个正样本概率被拉高时，其他同样合理的正样本概率被挤压的问题。

在偏好对比部分，RAD-DPO 从![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7GWdJRo8v2KdYUibhibvgdzBFt26uTyvnKUCia0XIGAeDicV8iah2e3JPFNMufVFGINFtgWjyOIYehB2icMKsVuhvvH8T2FJ4HdZ3tvU/640?wx_fmt=png&from=appmsg)中选择最高层级的正样本![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EnwNKjCviaicRKFBML24FKYfEznbTOxlnmdoicpJl6ibUqJbZfXFusJ0361AdGVP6iaicjMlDhetl5aKJEqa3JB3Wpibop0MpjiasaVNo/640?wx_fmt=png&from=appmsg)，例如下单商品，作为代表性 winner，并将其与整个负样本集合![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EjktG3RMYDMicpkWsB6nVibdiaDYQGIPo6TqM5y6dVYMg1rgJ2YIthOY3R4Lic5l0fibXMKfKZNicDpjwpCvfufRcwjBPJnQVE0IXTg/640?wx_fmt=png&from=appmsg)同时进行 list-wise 对比。

为了降低训练成本，RAD-DPO 采用 reference-free 形式，不再引入冻结的 reference model，而是使用长度归一化后的 log-probability 作为隐式 reward：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7EsZ2AyGZ5IggP6RJicf5seM9LSSQWLA00FEHwXUXny8icXP8aibsJSg4K2hp8SUbiaVt56aY9Rt9xyZsloZbDgBQ2hHYw4XBcONPc/640?wx_fmt=png&from=appmsg)

对于定长 SID 做长度归一化实际意义不大，但为了兼容变长 SID 这里选择和 SimPO保持一致。

基础的 list-wise preference loss 可以写为：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FB7wV87R6tu1WSQApIIu1omgCN1Stq69mkia3PaeJsFzKPviaC3m0YoNuCBOmF42Mpa0BzEIjSjBCucnrngffhI7eBXwCvicjpYo/640?wx_fmt=png&from=appmsg)

其中，β控制偏好优化强度，![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7E9pbq0js80BdolQYrqfjdewwMxIohqiabNWVUZiba9ULKZfHDIkQbU1osROtBDjLicZgInZxjVC9DA9LxBEoacPQLqc1lRvqRLTY/640?wx_fmt=png&from=appmsg)用于聚合多个负样本。相比逐个构造 pair，这种形式可以一次性利用多个负样本，并且会自然强化 hard negative：如果某个负样本的 reward 接近正样本，它对 loss 的贡献更大；如果某个负样本已经明显低于正样本，它的影响会相对减弱。

因此，MLGC 的关键不只是“多采几个负样本”，而是把偏好学习从局部 pair-wise 判断，提升为 session 级全局对比。模型看到的不再是单个正负 pair，而是当前 query 下正样本集合和负样本集合之间的**整体关系**。

## TLGD：Token 级梯度截断，保护 SID 公共前缀

SID 与普通自然语言 response 最大的不同在于：SID 是层级结构。前缀 token 往往表示粗粒度语义，例如类目、品牌、语义簇；后缀 token 才进一步区分具体商品。

例如：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7HVDvfHGmglaMehPOPia6Bv07JT3bJ4uC0DPtacDnPZLgQsbcCwUTzCHNDbzvjnEmDHPH66EIk226kKNicWSVXaibEACic1agOqsQg/640?wx_fmt=png&from=appmsg)

正样本和负样本共享前缀 [A,B]，它们可能属于同一类目或相近商品簇，只是在最后一层具体商品上不同。此时，标准 DPO 会降低整个负样本![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FJKFEYzIdQ6iagjEdNmFXm1hmZ0cUnENbw0ib4IbGEdnDfOveZvTOD8T2hFPUq0LYXLs3o4bVHxMkxyBMIDavYrweveM5fSeNZU/640?wx_fmt=png&from=appmsg)的概率：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7Ed8mTVdbh5KhwiaKHzYpvuickLCZia1V2ibxef0z1mcU8uYPia4rEqRSR9pMdPSgEyQhQPDQLEpn4oibCU71JpULnuU7hup5FCstdBs/640?wx_fmt=png&from=appmsg)

问题在于，负样本中的 [A,B] 其实也是正样本的正确前缀。标准 DPO 在打压![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7HQO9kWOL0mCGm5f2euZb7Nh11NmzqhC9BdBxiaFb0NwBsiaXNkibibCmyk3pMQaY2VBHFgUIfhNQ4IYs12l7V79hH3KqAGfuL760I/640?wx_fmt=png&from=appmsg)时，会把这些公共前缀也一起打压，导致同一批 token 同时收到“提升”和“降低”的梯度信号。这会造成正确前缀路径生成震荡，并可能破坏预训练阶段学到的层级语义表示。

RAD-DPO 的解决方法是 TLGD，即 Token-Level Gradient Detachment。它的核心思想是：

> 前向计算时，负样本公共前缀仍然参与 likelihood 计算；反向传播时，切断负样本公共前缀上的梯度，只在正负样本真正分叉的位置之后进行惩罚。

具体来说，先计算正负样本的最长公共前缀长度 kkk，然后定义 token 级差异指示函数：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7ETWpUwlib5RS3cbOyCR5Ccg8T8icRfj7u52kSL5bbr0J0EkthEEhk15AibXKPdHHQPDgMRKHqbPPkaFiaOsycX57Co34zW1o0qw6A/640?wx_fmt=png&from=appmsg)

其中，t≤k表示当前位置属于共享前缀，t>k表示当前位置进入差异后缀。

为了让公式更清晰，可以先定义单个 token 的 log-probability：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7GDN8cKhREUgAXic0Libptl0mQwicvsnWL2OTWe4LMW1gM2WRzlyTb7NbbbPQtZWDXfU37p1ZbYASWjicZKo1OYfxXtXicJjL1kDOoQ/640?wx_fmt=png&from=appmsg)

那么经过 TLGD 处理后的负样本 log-likelihood 为：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FicloMWSajX2mcYklicQLHXHD4ewy8ibmg8KscLc2JmV3YBWTKrx8p0PfdBYj6q0y9wS16WbGoXwjyKlo8pZeic1VIC0F2d3gm8ibE/640?wx_fmt=png&from=appmsg)

其中 SG[⋅] 表示 Stop-Gradient 操作。

这个公式可以分成两部分理解：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7EqeR4rexKw9UBrqbLXnGkpt1dPjibfSgqmhSAibQHZOnicfJVYIBJyePJjibjKZkTA0vbM4wARKwHJuAaS1xeTzMeicYWRhWv6bzAc/640?wx_fmt=png&from=appmsg)

对应公共前缀部分。它在前向时保留数值，但反向时不传梯度。

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7Grgibob8dmTCNntbAHcQzKogecQRUUz5bt87t5LtibEqIR4FQUfoMja0Wm6iacgcsqv8grBUHnNSccwc9JBDnCzsW3CZutib7BHaA/640?wx_fmt=png&from=appmsg)

对应差异后缀部分。它既参与前向计算，也正常参与反向传播。

因此，对于前面的例子：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7En6EZKd2cAtUhG8G2FCwcnMLd0YlxnCFqblMHKUMbTNiadQTy0icD4PgPlUYQ9xtEqPNRs3bLxIJnqKE4gh3VJzyr9kdHiafrOq8/640?wx_fmt=png&from=appmsg)

标准 DPO 会打压负样本中的![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7FxHGic16S0rkUiayRic7woE5eibx1ryJia0uUaFcvOoFAaUIxmZHcB6rRYHDUoe288UmKl4bcibwcYD7hO5YR2EJXLST4FIng72Krzc/640?wx_fmt=png&from=appmsg)，而 TLGD 只会对真正区分正负样本的![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7F0H2x3J92YMrDATicF2H5hTZwgLxHVku2fsp6KIWUJrgZiafPz2BT5IliaWRgicZ8nuaC125MJKevOM7qFjw3hZyZXKsibMsb8CPcw/640?wx_fmt=png&from=appmsg)产生负向梯度，公共前缀 A,B 不再被误伤。

TLGD 的本质，是**把“整条负样本序列打压”改造成“只在分叉点之后打压”**。这与 SID 的层级语义结构高度匹配：公共前缀代表粗粒度正确语义，应当保护；后缀代表具体商品差异，才是偏好优化真正应该作用的位置。

## RDRW：动态奖励加权，降低伪负例误伤

除了结构化前缀问题，电商隐式反馈还存在大量噪声。曝光未点击不一定代表商品不相关，可能只是因为位置靠后、图片不吸引人、价格不合适，或者用户已经点击了另一个相似商品。

如果把这些样本都作为强负例，模型会被迫把一些语义相关商品推远，导致召回空间变窄。RAD-DPO 的思路是：**如果一个负样本和正样本在模型表示空间中非常相似，那么它更可能是伪负例或模糊负例，对它的惩罚应当更轻。**

论文使用模型生成 EOS token 时最后一层 hidden state 作为序列级表示。记：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7H4ibSCZ18XEU4pX6dMCPrONvHdiaZKO7h6Hk2UNfk3wgoE5t7NIVr8YYZBQpNnvvstpCFBwLA2RickerFLPGe1W9DRzwPWdwzb1M/640?wx_fmt=png&from=appmsg)

为模型在输入x条件下生成 SID y 并到达 EOS token 时的最终 hidden state。对于正样本![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7G6UDTgr0KO5ygszgKqAHqiaDlRp6j3yiaia1RpklWI2kgAm6pv62iajflHRosCO44O5XL5RmhicibyR6p2RmuibsSbeHia5v8HwdaWDxg/640?wx_fmt=png&from=appmsg)和负样本![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7Ed0zOe2k77tblEPyWvYwymwpIbe1ZdfFQYJEuapAsaoYkics1I89Ejc8Ybs1mq1cfeNhBzbbicbA4zibr5eiblbbjvicS425EeqQGs/640?wx_fmt=png&from=appmsg)，计算余弦相似度：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7GZDrzoIv2PxHeDibiaDOzqe3vbYeG9ZmJx3dicb1aVUxmulEiaGzmPJb3w7hRq5PQZCw9VpDnlUooJFL67CdwODgZZN609z8y7Qics/640?wx_fmt=png&from=appmsg)

这里选择 EOS hidden state，是因为它包含了完整 SID 路径生成后的整体语义信息，比单个 token 表示更适合判断两个商品序列是否相近。

为了避免使用固定阈值，RAD-DPO 设计了一个统计 warm-up 阶段：先缓存前N=4096个 pair 的相似度，构造基准分布 S，然后计算三个分位点：![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FicuuX4XmeXgJ7ibUfL2SRgichflyF7Z0QEnAa9AOGWtjic6vJ48pN8Mm2yPyKtOWPujkJefDwFYmlB8pdicDHmN14v6okMAZ0mm5Q/640?wx_fmt=png&from=appmsg)

这些分位点会随着训练过程动态更新，以适应模型表示空间的变化。这样做的好处是，模型不是用人工经验判断“相似/不相似”，而是根据当前训练状态自适应地识别模糊负样本。

负样本惩罚权重定义为：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EKCGSBia0rxvLQSdPbdOhT4X0Qxtic65sAbSSFE5xnAtXWF72lNdluB6TdmBy2nhvcBBGnJus2Cq9c94JG97Q9XuoIboCe8XZMw/640?wx_fmt=png&from=appmsg)

其中λ=12，用于控制平滑过渡曲线的陡峭程度。

这个函数的含义是：

当![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7GWKIv2ib2glwCNGIEjzPRRh7pQUiby072aCmzohlzdyiaDPtm2ibfnbHYoBmuaz8HqpEbwHuwkAqYm8OYAAFc9Ll2GMws2pGGM1o4/640?wx_fmt=png&from=appmsg)时，正负样本相似度较低，负样本更可能是真负例，因此保留完整惩罚。

当 ![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EB5wiaLFOpPvjf5qwa1Kt6ZEDpvqpf4y4hR0GYDExtRAAQVeBICvL0aXBH5blibwUsTcj9Ypc78ZpHo5IzicN4ZlFXJLKE6Fia6ok/640?wx_fmt=png&from=appmsg)时，样本处于模糊区间，使用平滑函数逐步降低惩罚强度。

当![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7HuWkcTv8SzzjkP7p9tGfkASAOCI8VwJPZ15p1zibyKUOyibdl8kziaDabfIGefz54ib3QTYMicLox2MZ3IWT4dTWuiaulVbuEHvwmMQ/640?wx_fmt=png&from=appmsg)时，正负样本非常相似，负样本更可能是伪负例，因此惩罚权重降到 0.5，避免过度打压。

最终，将 TLGD 和 RDRW 同时引入后，RAD-DPO 的 preference loss 可以写为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7Gxngljq8cQichEw4JOSSU0UfEn0Tr3ibj7DFmibiarIBYClWMvKtLT5JPbhJwqePqqBDAN6L9KDyQiaEia09bgNSTIrUz629zj8Is64/640?wx_fmt=png&from=appmsg)

其中，正样本 reward 为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7G3aJ81pa4bKHiaFKa8XgV9Y89ZiaT5qkzcN78XbpJZ0KFLPJa0HuicgEibbceErGViaPIEPO8LkC2IicH4fcYeSXQQELJjf3lIInboA/640?wx_fmt=png&from=appmsg)

负样本 reward 为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7ELWoqQc08BwGcgc7rjEMjn0bRZGTeibyoMSvs1MkfibhBOyyVHc667npjC2kLex3aWRgndn1icGOIicKXia2gKf6HU23Bj8CgiagW4E/640?wx_fmt=png&from=appmsg)

这里的![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7HK3H4fUaHQd2OpWuChkPL0CstozlafU6aa8FZKhQNJKbUEZafSvMg7aKJww58Qw4jzEDLw53fkxxGpnwt6bIbwgbaESyXO2l8/640?wx_fmt=png&from=appmsg)已经是经过 TLGD 处理后的负样本 log-likelihood。也就是说，最终 loss 中同时包含两层保护：

第一，TLGD 控制负样本梯度作用在哪些 token 上。

第二，RDRW 控制每个负样本整体惩罚强度有多大。

因此，RAD-DPO 不是简单地“降低负样本概率”，而是更加精细地回答了两个问题：**哪些 token 应该被惩罚，以及这个负样本应该被惩罚多重**。

## 三个模块的整体协同

可以将 RAD-DPO 的三个模块理解为一个逐层收敛的设计：

首先，MLGC 定义了训练视角。它把偏好学习从单个 pair 扩展到 session 级多标签学习，使模型同时看到多个正样本和多个负样本，缓解多正例场景下的概率挤压。

其次，TLGD 定义了梯度作用位置。它利用 SID 的层级结构，只切断负样本共享前缀上的梯度，避免把正确的类目路径当作负反馈打压。

最后，RDRW 定义了负样本惩罚强度。它利用模型自身表示判断正负样本是否相似，对疑似伪负例进行软惩罚，降低隐式反馈噪声带来的过拟合风险。

可以概括为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7G2uCpcXpEbAtC5QFmzIuV7xn4u5UdCRk1SeOyVfBHD5wvScYssWWgXCYmnKMN0M1oa4oQsIjXegVxWaKtt28Kia8sbkk113wia4/640?wx_fmt=png&from=appmsg)

相比标准 DPO 的“单正例、单负例、整序列、等权重”优化，RAD-DPO 更适合生成式检索中的结构化 SID 输出。

这一设计也自然引出一个工程问题：既然 RAD-DPO 要在一个 session 内同时处理多个正负样本，如果仍然沿用传统 DPO 的拼接方式，就会带来严重的重复计算。为了解决这个问题，我们进一步设计了高效的 Label Packing 训练方案，这也是 RAD-DPO 能够在大规模工业数据上落地的关键。

**04**

**实现细节**

RAD-DPO 在方法层面将偏好学习从 pair-wise 扩展到了 session-level multi-label contrast，但这也带来了新的工程挑战：一个 prompt 需要同时和多个正样本、负样本计算 log-probability。如果简单复用标准 DPO 训练框架，就会出现大量重复计算。

在传统实现中，通常会把 prompt 和每个 response 分别拼接：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7GzW59WnfyLdZyNo1HSE2gzrX5auvqxMfkR1DLeSia1SIOzwa37IMic3IcOGysCnDS6QPeia2QAoLQ0HicjcZm1Aljhxc5R8Vhfv2Q/640?wx_fmt=png&from=appmsg)

然后分别执行前向计算。对于一个正样本和n个负样本，prompt会被重复编码**1+n次**。

在自然语言任务中，这个问题可能不明显，因为 response 通常较长，prompt 的占比不一定高。但在生成式检索中情况完全不同：prompt 往往包含 query、用户画像、历史行为序列等结构化特征，长度可能达到上百个 token；而 SID response 通常只有少数几个 token。也就是说，计算量主要集中在 prompt 上，重复编码 prompt 会造成显著的显存和算力浪费。

因此，MLGC 不只是一个 loss 设计问题，也必须配套一个高效的 batch 组织方式。RAD-DPO 采用的核心方案是 **Label Packing**。

## Label Packing：把多候选样本压到一次前向中

Label Packing 的基本思路是：对于同一个 prompt，不再将每个候选 response 单独拼接，而是把所有正负候选都拼接到同一条 unified sequence 中：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7FmXHYUJGU6wJlxaIG9W1hb55QDia1pFWR3OpUxqWsIAfNYTVB2VqLDibZibibcle7JFKHIMdTh2NPOSibXPpbJ7P2GYRicHn0hULSibI/640?wx_fmt=png&from=appmsg)

这样，prompt 只需要计算一次，所有候选 SID 的 log-probability 都可以在同一次 forward pass 中得到。

但直接拼接会带来一个问题：不同候选之间可能互相看到彼此的 token，导致信息泄露。例如负样本在计算时看到正样本 SID，或者后一个候选看到前一个候选的答案，这会破坏条件独立性。

为了解决这个问题，RAD-DPO 使用自定义的 **Block-diagonal Attention Mask**。如下图所示，prompt 对所有候选可见，但不同候选之间互不可见。

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FZleEd3icaOWa0KGyXczosgXKarf1pjZICspVLe2dXv2N753oRKG86kvFBhEicU9sibWK62L478erib12Psib4pMQdXfb58uTg53HI/640?wx_fmt=png&from=appmsg)

可以把 attention 可见性理解为：

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7FsiaCxOCiaial1UVmIZrwn3f9RiaUMicPAGiagTTcPlD0R4DONJy35iakvtqGcaLD69OYn5j1icAUO1XeXVDLGBeX6RPseGThbV0ibYWF4/640?wx_fmt=png&from=appmsg)

也就是说，每个 candidate 的计算逻辑仍然等价于单独输入：![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7EssribGzcRvM8cDtZ1EqKcSgeVwZ5J6CuJDQ7Stctia0yYrGrpCzjVF4CicasNwLJMgFPqutDRxO93J8qZWZPQY9rnmWqvdebQa4/640?wx_fmt=png&from=appmsg)，但多个 candidate 被打包到同一次 forward 中完成。

## Attention Mask 与 Position ID 的两个关键细节

Label Packing 要正确工作，有两个关键点。

第一个关键点是 **候选之间互不可见**。

对于任意两个不同候选![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7Eiaicl88oIF5NC4aOW6PPD2Hzz9Qgb9heib5mn2QHd8VKwe6InEg35Gpq4ZyRUDm6BA8bwRqkF7nNHVIn1Yia7ibV9WuzXgIVO85wE/640?wx_fmt=png&from=appmsg)和![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7EPau1wdLYhXHx51Flv1YshsTgHlvHWeRI1xG9ZiafgVKHe0LZI3mq6siaN9066Ciay5sFoartiaYaUQ7icJ4WGMXRkYOdB5cs6iclqg/640?wx_fmt=png&from=appmsg)，它们之间的 attention 应被 mask 掉：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7GmJ8f3qAtibC91rUGoDeMmdbmrj4kh6uD5JUJkTD52h2fic9xsC6TkD1HlQRZR9UzTib6UeWhVseAkV8R0DiciaH1hmHnUeaNQc3PM/640?wx_fmt=png&from=appmsg)

这样可以保证每个候选的 log-probability 只依赖 prompt 和自身前缀，不会偷看到其他候选的 token。

第二个关键点是 **不同候选的 Position ID 需要对齐**。

如果只是简单把多个 candidate 依次拼接，那么第一个 candidate、第二个 candidate、第三个 candidate 的绝对位置不同，正样本永远在前面。模型可能通过位置差异区分样本，而不是基于内容学习偏好。

因此，RAD-DPO 对所有 candidate 的 Position ID 进行对齐，使它们共享相同的相对位置编码，从而防止信息泄露。

## 性能收益

从工程视角看，Label Packing 和 reference-free 设计保证了 RAD-DPO 可以在大规模搜索日志上高效训练，训练效率和SFT处于同一水平，远高于GRPO等强化学习算法。

• 显存：由于去掉了参考模型（SimPO 路线），**显存消耗降低近50%**。

• 吞吐：对比传统拼接方式，单次前向即可完成所有样本计算，训练**吞吐提升了 300%**。

**05**

**实验分析**

为高效验证离线指标，我们在 3 千万小数据集上进行了对比实验，实际上线前的训练会放大到上亿量级的数据，经验证 RAD-DPO 训练后的指标提升会更明显 。

**整体对比：**

**![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7F02ia2dzUSibMzicdG7FfLDfVz94mHwFvibwJ7NLfy1BGrAOicVjjdZqibC8jRBTn4DDBxHMooPPTIiaSicZllgkYVibLPnlyTmsrgbv4U/640?wx_fmt=png&from=appmsg)**

1. 全方位领先：在所有召回（Recall）和 MRR 指标上，RAD-DPO 均优于 SFT 及其他 DPO 变体。

2. 模型规模可扩展性：随着模型参数从 0.6B 扩展到 8B，RAD-DPO 的领先优势持续扩大（如 8B 模型下 SID-level MRR 提升至 0.3246）。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/X88aRGfff7HGzViaDew253NHNUaR4CibIDA9f6Tf6PvnqkkvGMyGHO53lRBQJFPgzaY5GlN5YKrXJ7CWEBxAjw1CxKoAc6uuSjd2Bv2libbF64/640?wx_fmt=png&from=appmsg)

1. 数据效率：Figure 3 显示，即使在 10M 的训练数据下，RAD-DPO 依然能保持对 SFT 的显著相对提升。

![](https://mmbiz.qpic.cn/mmbiz_png/X88aRGfff7G5K4lIQvVkZC8QbEwZNVIQ7NdgUJTXvGD6zVjOVnyrDx1PCScEftdficicf6CmZIka1JlTT1TE6FHf7dCib3dPkiahL3djGSqbacs/640?wx_fmt=png&from=appmsg)

需要强调的是，论文中的结果为了对比公平，统一只使用了 3000 万条训练样本，实际上线时 RAD-DPO 可高效训练上亿数据，指标会有进一步提升。

**06**

**总结与展望**

RAD-DPO 是生成式检索从理论走向大规模工业应用的关键方案 。它系统性地解决了结构化 SID 生成中的前缀冲突、隐式噪声以及多标签概率挤压问题 。通过 TLGD 梯度截断保护了层级结构的稳定性，通过 RDRW 实现了自适应降噪，并在工程上利用 Label Packing 实现了极高的训练吞吐 。

未来优化：

1. 引入更丰富的样本类型：探索引入相关性样本，进一步提升检索结果的相关度（pgood） 。

2. 训练阶段融合：探索 SFT 与 DPO 的单阶段联合训练，减少分阶段训练带来的分布偏移和成本增加。

3. 精细化 Token 优化：针对不同位置的 Token 设计差异化的损失权重，进一步挖掘生成式模型的建模能力 。

— END —

---

[往期论文回顾](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzUyMDAxMjQ3Ng==&action=getalbum&album_id=3723857788540567554&subscene=90&scenenote=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyMDAxMjQ3Ng%3D%3D%26tempkey%3DMTM3NF81T2g1SVJXYjJYR3U5ZHVVQllnMHdoZkFKcjd2bFMxTmlJNXNIYlhpZERMWkNPNDNNNTdnQ3hUS0E4UGlaclBqai1zYXp4OTFFUUtSa1RLa0Q3QUtFdU1vQmtsWlkxejhSNXhlbE5LMDg3cU1IQjJOTEFwbHZMV0M2SHlZT2Vsay1OeUFBdjF4eUltT2VYQ01pdjZLM2ozb2ZsUlkzclpDUDlabXh3fn4%253D%26chksm%3D79f2298d4e85a09b79a0d4699a9ca53f97acfe68d2f14079fdd8fbf5410056fbf2253ab25f0e%26scene%3D90%26xtrack%3D1%26sessionid%3D1779157934%26subscene%3D93%26clicktime%3D1779157942%26enterid%3D1779157942%26flutter_pos%3D0%26biz_enter_id%3D4%26jumppath%3D1109_1779157678012%252C20020_1779157679839%252C1001_1779157933156%252C1104_1779157935417%26jumppathdepth%3D4%26ascene%3D56%26devicetype%3DiOS26.4.2%26version%3D1800492d%26nettype%3D3G%2B%26abtest_cookie%3DAAACAA%253D%253D%26lang%3Dzh_CN%26countrycode%3DCN%26fontScale%3D106%26exportkey%3Dn_ChQIAhIQucQF15bMx3d7G%252BLd5aD8yhLhAQIE97dBBAEAAAAAAMB0DmIMnXwAAAAOpnltbLcz9gKNyK89dVj0ABU2gWs%252B%252BNrElUugEjPyN9PSiOfRafUD29togX9OVBRG49jHTKOEmKJCyYWlOk3LoYxRpRn1RPfK7TiBgGneAaZ1mR59yZYWfc8AMyG5GaBd6qMFskePi2o8B60xate4qk7aJX2YBiHiQqncP7iimp0y8nLKwuz%252BHx%252FmcvSP364bvK8E8kKadLuDnBbDxIG67axejJiaolUYu68pst%252BbaXb9RmKogRde5rloUKYvTD%252BXNMOvgRr%252BD0PDzA%253D%253D%26pass_ticket%3DEM2H0CUka0%252BtHy9a7V%252FQWqDWEJKPn%252B06m8w7ejndWl9QxBKjkPJMnfQ1efXu%252FsUp%26wx_header%3D3&nolastread=1#wechat_redirect)

[ICASSP 2026｜Sparse-Up：高精三维几何生成技术与应用前沿](https://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247515915&idx=1&sn=04acbf0330124600941071b168ebe38c&scene=21#wechat_redirect)

[ICML 2026｜RTPrune：受两阶段阅读启发、面向 DeepSeek-OCR 高效推理的词元剪枝](https://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247515850&idx=1&sn=26f3135fadbe42eabd068bd906e55d9f&scene=21#wechat_redirect)

[SIGIR 2026｜语义 ID 也能“因材施教”：让生成式检索兼顾精准与泛化](https://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247515829&idx=1&sn=07c75dd6c19ebd06cb560eb01ba5e322&scene=21#wechat_redirect)

关注「京东零售技术」，了解更多～