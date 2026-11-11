---
title: '打破信息茧房！快手搜索多视角正样本增强引擎 CroPS 入选 AAAI 2026 Oral'
company: 快手
tag: 召回
date: 2026-01-13
url: https://juejin.cn/post/7594358540048695331
account: 
origin: harvest-202607
---
# 打破信息茧房！快手搜索多视角正样本增强引擎 CroPS 入选 AAAI 2026 Oral

[快手技术](/user/3736571181793721/posts)

2026-01-13
  
315
 
阅读10分钟

   

短视频搜索业务是向量检索在工业界最核心的应用场景之一。然而，当前业界普遍采用的“自强化”训练范式过度依赖历史点击数据，导致系统陷入信息茧房，难以召回潜在相关的新鲜内容。

针对这一问题，快手搜索团队提出了一套全新的检索数据引擎 CroPS（Cross-Perspective Positive Samples）。该方法通过引入用户换 Query 数据、推荐流数据以及大模型生成的世界知识，多视角丰富了正样本信号，并结合层次化标签分配（HLA）策略和 H-InfoNCE 损失函数，实现了对相关性的精细化建模。

\*\*目前，CroPS 已在快手搜索业务中实现全量部署，服务亿级用户。\*\*实测表明，该方案在具备极强的架构普适性的同时，显著提升了 CTR 与长播率，并有效降低用户换 Query 率，优化用户搜索体验。

目前，本工作相关成果《CroPS: Improving Dense Retrieval with Cross-Perspective Positive Samples in Short-Video Search》已被人工智能顶级会议 AAAI 2026 Oral 接收。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/9c77a4dc1b644812ac776e0e3a996508~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=%2FBoURL6K%2BdGGQw3iMh3vr0kYOOs%3D)

论文链接：[arxiv.org/pdf/2511.15…](https://link.juejin.cn?target=https%3A%2F%2Fxie.infoq.cn%2Flink%3Ftarget%3Dhttps%253A%252F%252Farxiv.org%252Fpdf%252F2511.15443v1 "https://xie.infoq.cn/link?target=https%3A%2F%2Farxiv.org%2Fpdf%2F2511.15443v1")

## 一、背景

当前工业界主流的向量检索模型通常采用对比学习范式进行训练，拉近 Query 与正样本在向量空间中的距离，同时推远与负样本的距离，从而学习内容相关性。

然而，在绝大多数工业系统中，训练数据的正样本高度依赖历史曝光日志中的用户交互行为（如点击），导致“自强化”循环发生。具体而言，模型倾向于检索与历史高频点击内容相似的视频，用户受限于展示结果，只能在有限内容中选择和反馈，而这些反馈又再次作为正样本进入下一轮训练，进一步强化了模型原有的偏好。

这种机制不可避免地引发了严重的样本偏差。一方面，大量潜在相关但从未获得曝光机会的优质长尾内容，被系统性地排除在正样本之外，甚至在随机负采样过程中被错误标记为负样本。这种偏差使模型的检索视野逐渐狭窄，搜索结果变得保守且单一。另一方面，由于缺乏对新颖内容的探索能力，用户的搜索体验逐渐固化，难以在结果中获得惊喜或满足探索性需求。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/0017d1e5810a4b448b3e99f26544f0f8~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=g6uPzyVYeXOPrSBVdXOuMjf7BpM%3D)

以往的学术研究多致力于改进模型结构（如引入交互更复杂的 Poly-Encoder）或优化负采样策略（如挖掘困难负样本），从而提升检索性能。虽然这些方法在一定程度上增强了对已知内容的判别能力，但始终在历史曝光数据的界限内打转，无法从根本上缓解正样本来源单一所带来的“信息茧房”效应。

**针对这一挑战，快手搜索团队提出了 CroPS 框架，从根源上打破数据闭环。CroPS 首次在业界引入“跨视角”的正样本信号，重塑了检索模型的训练图景。**

## 二、方法

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/4d011da1646241be9e154a840b772a4c~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=BfcMu%2FYKfyBoYSzKKadFH463RlI%3D)

### 2.1 多视角正样本增强引擎 CroPS

为了打破数据边界，CroPS 框架构建了一个包含三个维度的正样本增强引擎，分别利用用户换 Query 行为、推荐系统反馈以及大语言模型（LLM）的世界知识，来全方位地丰富语义空间。

1. **基于用户换 Query 行为的查询级增强**

在真实的搜索场景中，用户往往难以一次性精准表达意图。当用户输入查询词 A 却未能找到满意结果时，通常会进行查询重构，输入语义相关但表述不同的查询词 B。如果用户在查询词 B 的结果下产生了深度交互，那么该交互视频在语义上极有可能是查询词 A 的理想正样本，尽管它从未在 A 的结果中获得足够的曝光。

CroPS 敏锐地捕捉到了这种“意图连续性”。通过分析用户在短时间窗口内的改写序列，并利用轻量级语义判别器进行过滤，系统能够将改写后获得的成功点击“回流”给原始查询，利用用户的修正行为来纠正模型的语义偏差。

1. **打破搜推壁垒的系统级增强**

推荐系统拥有海量用户消费数据，并且其算法机制天然倾向于发散和探索，因此推荐流中的视频往往具有更丰富的多样性。CroPS 建立了一套跨系统的信号桥接机制：对于同一个用户，如果他在推荐信息流中深度消费了某个视频，且该视频在语义上与用户近期的搜索词高度相关，该视频就会被引入作为搜索模型的正样本。

通过这种跨系统的信号融合，搜索模型能够利用推荐系统的探索能力，将用户感兴趣但未主动搜索到的内容纳入召回视野，从而有效缓解单一系统带来的位置偏差和曝光偏差。

1. **引入大模型的知识级增强**

当平台现有的内容库或日志无法覆盖某些长尾、复杂查询时，单纯依赖内部数据是无解的。为此，CroPS 引入了大语言模型（LLM）作为“虚拟检索器”和“内容生成器”，利用 LLM 蕴含的丰富世界知识生成高质量合成样本。

具体而言，系统采用单样本提示（One-shot Prompting）策略，让 LLM 扮演视频内容专家，针对特定查询生成包含标题、描述和标签的虚拟视频元数据。将这些合成数据作为正样本，训练双塔模型，相当于将外部世界的常识与逻辑“蒸馏”进检索模型中。

这一方法使得模型在面对“冷门”或“从未见过”的搜索 query 时，仍能够凭借语义理解能力找到相关内容，从而彻底突破平台存量数据的限制。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/496638804798484286d0c394bb46560d~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=5daB1NWO4kZPhFwd3ETaCbjNT%2B8%3D)

### 2.2 层次化标签分配 (HLA)

HLA 的核心是解决 CroPS 多源正样本的“可靠性差异”问题。不同来源的正样本（比如：用户换 Query 后产生互动的视频、推荐流中的视频）与用户真实需求的契合度各不相同。如果一视同仁进行训练，模型可能难以抓住重点。

因此，HLA 为样本分配“分层标签”，让模型能够识别样本的重要程度，从而学习更细粒度的相关性，更好地契合系统优化目标。具体来说，HLA 将样本划分为“正样本相关层级”和“负样本层级”，为后续训练提供“细粒度监督信号”，不同类型样本对应固定标签，具体如下：

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/f8ee647f95ce483a80b8d3d7d7260001~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=YVOW9pmvvFudHTAnWuM852e5GYM%3D)

### 2.3 H-InfoNCE 损失函数

传统的语义召回采用的是 InfoNCE 进行优化，默认“样本只有正/负两种标签”，会逐个对比 “单个正样本” 和 “对应的负样本”，无法区分 HLA 里“高标签正样本（如上图 Table 1 的标签 5）”和“低标签正样本（如上图 Table 1 的标签 3）”的层次化差异。

而 H-InfoNCE 在训练时，将“当前样本”与“标签严格低于它的所有样本”进行对比。这不仅突显了高优先级样本的重要性，也使学习目标与 HLA 的层级逻辑完全对齐，实现细粒度的语义区分。例如：

* 若当前样本是“用户换 Query（标签 5）”，H-InfoNCE 会将其与“标签 ≤4 的所有样本（包括推荐正例、曝光未点击样本、负样本等）”一起对比，强制模型学习“标签 5 样本与查询的相似度，必须高于所有低标签样本”。
* 若当前样本是“曝光未点击样本（标签 3）”，则只需对比“标签 ≤2 的样本”。

通过这种方式，模型能够逐步掌握“高标签样本更重要”的排序逻辑。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/d7090af4f2a847a0b6cd17bfab779933~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=IKNp6HmCpP7tCr6cclOUCryFb3c%3D)

H-InfoNCE 在这里通过样例标签矩阵、样本 mask 矩阵等得到了高效实现。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/f1c8bfb56fbc474eae178375b9759904~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=nGqdOIjNoWh82asfLoFpH6n410w%3D)

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/ac0aaff6c265413e9ab7c4ce8e90de84~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=B2qKKtYbmSwstXTBg9Wy77jBf00%3D)

## 三、实验结果

为了验证这一框架的有效性，团队构建了两类测试集，来衡量模型的召回率 Recall@100：

（1）CT：用户点击测试数据集，即用户点击的视频作为正例；

（2）QR：用户换 Query 测试数据集，即用户换 Query 后消费的视频作为正例。

同时也引入了相关性标注测试数据集，以 NDCG@4 为监测指标，作为模型的相关性表征能力度量。

### 3.1 离线实验

论文中主要比较了三类主流方法：

（1）经典方法：BM25（概率排序基线）、NCE（传统对比学习）；

（2）神经网络方法：DPR（双编码器稠密检索）、ANCE（动态难负样本采样）、ADORE+STAR（NN 模型引入筛选负例）；

（3）负采样策略：TriSampler（基于样本的空间位置进行的负例采样）、FS-LR（多级别负标签策略）。

在离线实验测试中，CroPS 相较于最强基线 FS-LR 在 CT 数据集上提升 9.5%，在换 Query 测试集 QR 上提升 7.1%。同时 NDCG@4 和 最强基线相当（67.4%->67.0%）

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/32b9e67a3f514684a994be8a5378fbd3~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=TlvIR%2F5LMv6e7c%2BxeJ7sLn3h5fA%3D)

### 3.2 在线实验

在快手搜索的大规模 A/B 测试中，CroPS 带来了全方位的业务增长：

* 点击率（CTR）显著提升了 0.869%，长播放率（LPR）提升了 0.483%，表明召回的内容不仅相关度高，而且内容质量足以吸引用户长时间驻留。
* 用户换 Query 率（RQR）下降了 0.646%，意味着用户“一次搜对”的概率大幅增加，不再需要频繁更换搜索词来找到想要的内容，直接反映了用户搜索体验的质变。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/228508b3213142df85162d9369f338d9~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=bQIfrPNDj1fhckP5pyUnnH3JHcY%3D)

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/c82df0752fca4d8aa5101db18e2e5915~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b-r5omL5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785216195&x-signature=PqMDAqimjcK5gHDvsbnodldofdA%3D)

## 四、总结与展望

CroPS 证明了在工业检索系统中，正样本增强是缓解“信息茧房”问题的有效钥匙，能够提升系统上限。通过跨视角引入多样化信号，并结合精细化优化策略，CroPS 成功打破了自强化训练的边界。未来，快手搜索团队将进一步探索 CroPS 与生成式检索（Generative Retrieval）方法的融合，持续挖掘大规模语言模型在搜索全链路中的潜力。