---
title: '阿里深度召回模型实践'
company: 阿里淘系
tag: 召回
date: 2020-10-23
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247509261&idx=1&sn=17a4b327f46ea40bdf4f7481f8739311&chksm=fbd71761cca09e778f3e05860d2e1333c0ba9e32c6854f1040991478f5965262ef1a0f849b4c&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgSqUNo1QscekFiaN8hrcem7WTpurZjSTib8whMJ9aeDSeOgY5jKNOLAx3ncZDibX6Iupcl9fzJeB6Zw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgsxWoxHJQg58ufp1ic0FSQHHUOwrXzWBafwjjfKU91j4V8KylYCIKHGoN9hWCicmxW7VDgXq7zUedQ/640?wx_fmt=png)

文章作者：韩宇、张跃伟 阿里巴巴

内容来源：阿里云开发者

**导读：**召回结果的好坏对整个推荐结果有着至关重要的影响，最近的一系列实践和研究表明，基于行为序列的深度学习推荐模型搭配高性能的近似检索算法可以实现既准又快的召回性能；与此同时，用户在天猫精灵上还可以进行实时指令操控，利用丰富的反馈信息改进召回模型的性能。

**01**

**背景**

传统的推荐系统通常由两部分构成，分别是 Candidate Generation（候选生成）和 Ranking（排序），以下图中经典的 YouTube 视频推荐为例[1]，整个系统分为了两层：第一层是 Candidate Generation（候选生成），负责从全量的视频中快速筛选出几百个候选视频，这一步通常也被成为 Matching（召回）；第二层是 Ranking（排序），负责对几百个视频进行精准打分并重新排序，决定最终向用户展示的结果顺序。

![](https://mmbiz.qpic.cn/mmbiz_png/EkgpOcjaJwiaCR54Vumz6R4Rubzw3bsjs7XZRFWZL2xr0wJnMZJT6ibFsgWG6TBDPVo8GaP2uWZrrTLPicGKLnfEw/640?wx_fmt=png)

图 1 YouTube 视频推荐

本文主要研究 Matching（召回）部分，这部分通常面对的是整个推荐 item 集合，既要尽可能多的保留相关性高的结果，又要保证速度，召回结果的好坏对整个推荐结果有着至关重要的影响。最近的一系列实践和研究表明，基于行为序列的深度学习推荐模型[2-4]搭配高性能的近似检索算法[5]可以实现既准又快的召回性能（这套方案通常被称为DeepMatch），和传统的召回方法相比（比如 swing、etrec、SVD），DeepMatch 的优势主要如下：

* 可以建模 user-item 间更深层次的非线性关系
* 可以在模型中使用各种 user 和 item 的特征
* 基于行为序列的模型可以建模用户不断变化的兴趣，并且能够融合用户的长短期兴趣

DeepMatch 已经广泛应用于天猫精灵推荐场景中（APP 信息流推荐、音乐推荐等）并取得了比传统 i2i 方法更好的效果，但目前的模型仍存在着一些问题，有一些关键的信息还未引入进来（以“我要听歌”场景为例，在这个场景中天猫精灵会根据用户的喜好来给用户推荐音乐）：

**负向反馈信号（Play Rate）**

初始训练日志数据中仅包含正向反馈，也即使用播放完成率高的歌曲序列训练 DeepMatch 模型。而在天猫精灵的场景中，用户有主动切歌的行为，如主动的“停止播放”、“下一首”，其中大部分这类型是用户在出现不喜欢的歌曲时触发，这些信号可以作为用户的负反馈加入到模型中。而且一些实践已经表明了负向反馈的作用[6-7]，如果能将这些信号有效的利用起来，模型有能力去捕捉用户时刻变化兴趣，在用户进行切歌行为时，减少同类型的音乐推荐。在这个场景中，我们用每首歌曲的播放完成率来表示用户反馈，完播率较大即为正反馈，完播率较小即为负反馈。

**歌曲点播 query 意图信号（Intent Type）**

天猫精灵歌曲的播放大部分由用户的 query 点播而来，每一首歌曲背后都有用户的点播意图，天猫精灵背后有一套专门的歌曲 query 意图解析，比如精确点播（歌名点播：“播放七里香”、歌手点播：“我要听刘德华的歌曲”）、推荐（风格流派推荐：“来点摇滚”、随便听听推荐：“放歌”）。通过对用户行为的分析来看，不同意图类型下的歌曲对于推荐模型贡献的权重是不同的，在模型中融入歌曲对应的意图 attention，能更准确把握用户的兴趣。因此本文提出了一种基于多任务学习和负反馈的深度召回模型。

**02**

**方法**

总体来说，由于近似最近邻检索算法的限制，我们的召回模型需要独立地对用户历史行为序列进行编码以生成用户的每一步的向量表示，然后再和 Target Item 向量做内积运算，得到打分，模型基于 Self-Attention 的架构来实现，总体结构如下：

![](https://mmbiz.qpic.cn/mmbiz_png/EkgpOcjaJwhSibAZOyu2lSAlnIibGuerNlAMte1wyCXIDXj65eHIkKiaDex7vxZw9KCOYya9gx972L5CbPic50ibFYw/640?wx_fmt=png)

图 2 模型总体结构

**1. Input Representations**

如前所述，为了建模负向反馈信号和用户意图类型信号，我们的模型引入了对 Play Rate 和 Intent Type 的表示。但初始数据集不包含这两种信号，因此我们用 Train Set 1 来表示初始数据集，Train Set 2 表示带有负向反馈信号和用户意图类型信号的数据集，我们对它们做了统一的表示。总的来说，用户历史行为序列中的每个 Item 的表示由如下四部分构成：

**① Item Embedding**

我们首先把每个 Item 嵌入到固定大小的低维向量中，Train Set 1 和 Train Set 2 共用一套 Item Vocabulary，不需要做区分：

其中，Xi为 Item 的 One-Hot 表示，Vi是 Item Embedding 矩阵，另外需要注意的是输出层和输入层共用一套 Item Embedding，这样做的目的主要是节省显存占用空间，因为推荐场景的 Item 数量是巨大的，而且有很多工作已经证明了这样的做法对于模型性能影响不会很大[2]。

**② Position Embedding**

对于行为序列任务，我们需要使用位置嵌入来捕获行为序列中的顺序信息。我们采用不同于 Transformer 原论文[8]中的 sin 和 cos 方法，直接使用 Max Sequence Length 个 Embedding 来表示不同的位置。

**③ Play Rate Embedding**

播放完成率是用户对于 Item 接受程度的一个重要反馈，在天猫精灵上，对于不喜欢的歌曲，用户通常会直接使用“下一首”指令将其切掉，这些歌曲的播放完成率就会比较低。播放完成率是一个值域在 [0, 1] 间的连续值，为了实现后面将要提到的连续值特征和离散值特征的交互，我们参照了[9]中方案，将 Play Rate 映射到了与 Item Embedding 相同的低维向量空间，具体来说，我们将 Play Rate Embedding 表示为：

其中，Xr是 Play Rate，Vr 是随机初始化的 Embedding，Er 是最终得到的 Play Rate Embedding，由于我们 Train Set 1 数据只有播放时长较高的歌曲，并且没有播放完成率的信息，因此对于 Train Set 1，我们固定所有 Play Rate 为 0.99：

  

**④ Intent Type Embedding**

用户意图类型表示了用户进入这个 Item 的方式，比如在天猫精灵端，点播（用户明确点播出的歌曲）和推荐（天猫精灵为用户推荐的歌曲）就是两种不同的 Intent Type（天猫精灵的实际场景中类型会更多），类似 Item 本身的表示，我们把 Intent Type 也映射到了一个固定的低维向量空间：

我们不知道 Train Set 1 数据中的 Intent Type，在此我们假设所有的 Train Set 1 数据的 Intent Type 全部为点播：

**2. Factorized Embedding Parameterization**

在推荐的任务中，Vocabulary Size 通常是巨大的，这导致了我们无法使用太大的 Embedding Size 来表示 Item，否则显存放不下，但很多使用 Transformer 的工作证明，提高 Hidden Size 可以有效的提升模型效果[10]，参照 ALBERT[11] 压缩模型的方式，我们首先把 Item 的 One-Hot 向量映射到一个低维度的空间，大小为E，然后再映射回高维度的空间再输入Transformer，从而把参数量从 O(V×H) 降低到了 O(V×E+E×H)，当 E≪H 时参数量会明显减少。

**3. Feedback-Aware Multi-Head Self-Attention**

在获得用户行为序列的特征表示后，我们就可以准备构建用户向量了，我们采用了注意力机制来编码用户的行为序列。如 Transformer[8] 中所述，注意力机制可以被描述为一个将 Query 和一系列的 Key-Value Pairs 映射到 Output 的函数，其中 Query，Key，Value 和 Output 都是向量，Output 被计算为 Value 的加权和，其中分配给每个 Value 的权重由 Query 与对应 Key 的打分函数计算，由于召回模型的限制，我们无法使用 Target Item 提前和用户行为序列中的 Item 做运算，因此采用 Self-Attention 的方式，直接把用户行为序列作为 Query，Key，Value 来进行计算。具体来说，我们使用了 Multi-Head Self-Attention 的方式来提升模型对于复杂交互的建模能力：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgsxWoxHJQg58ufp1ic0FSQHJiciaRicgqTg62GZiaE5qb9OpfEVwiaziaiajWsTLLtfxEfABdiac33bLkkEJA/640?wx_fmt=png)

其中， WiQ、WiK、WiV 是线性投影矩阵，h 是 head 的数量。在经典的 Transformer 结构中，Q，K，V 由 Item Embedding 和 Position Embedding 构成，在我们的模型中，我们将外部信息（播放完成率和用户意图类型）引入到 Attention 中来，我们称之为 Feedback-Aware Attention，通过对这些信息的引入，我们的模型就有能力结合用户的反馈信息感知用户对于各个歌曲的不同的偏好程度了：

除此之外我们还参照 ALBERT[11]，尝试了 Cross-layer Parameter Sharing 的方案，这种方案让每层 Transformer Layer 全部共享一组参数，同样量级（层数相同）下的 Transformer 采用该方案后实际上的效果是会有所下降的，但是参数量减少了很多，训练速度也会快很多，对于推荐这种数据规模比较庞大的场景，采用这种策略可以在尽量节约训练时间的前提下提升模型性能。

**4. Sampled Softmax Loss For Positive Feedback and Sigmoid CE Loss For Negative Feedback**

在获得用户的向量表示后，就可以定义多任务学习的目标了，由于之前我们已经统一了 Train Set 1 和 Train Set 2 的数据表示，因此这两个任务可以放在一起进行联合多任务训练。具体来说，我们的任务类似于语言模型：给定前 t 个已经听过的音乐，预测第 t+1 步用户想要听什么音乐，我们根据播放完成率的高低将信号分成两种（实际实现时会使用一个阈值来区分），一种是 Positive Feedback，这种的优化目标是使其打分排序尽量靠前，另一种是 Negative Feedback，这种的优化目标是使其打分排序尽量靠后。

如下图的左图所示，如果只做传统的 Positive Feedback Loss 的话，我们的模型可以拉近用户向量和喜欢的 Item（正向样本）的距离并拉大其和未观测 Item 的距离，但是不喜欢的 Item（负向样本）的距离可能并不会被拉开，我们希望我们的模型可以向右图一样，在做到上述特性的同时，拉大用户向量与不喜欢的 Item 的距离：

![](https://mmbiz.qpic.cn/mmbiz_png/EkgpOcjaJwiaCR54Vumz6R4Rubzw3bsjs4iaByMav0Wc2JrZnHEiciapS1fYLibZlQnUxhaxk2lPottvZqLY6VHsKdw/640?wx_fmt=png)

图 3 优化目标对比

因此我们使用了 Positive Feedback 和 Negative Feedback 结合的优化目标：

对于 Positive Feedback，我们使用 Sampled Softmax Loss 来优化。在之前的很多工作中[12-13]，Sampled Softmax Loss 已经被证明非常适用于大规模推荐召回模型，它的定义如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgsxWoxHJQg58ufp1ic0FSQHfMVgtC4wzWratiaXEV62D8WiczUWqlGXibqb3FvnsPEdJnJicqV5xjsrXQ/640?wx_fmt=png)

在使用 Tensorflow 实现的时候，sampled\_softmax 默认使用的采样器为log\_uniform\_candidate\_sampler ( TF 版 Word2Vec 基于此实现 )，它基于 Zipfian 分布来采样，每个 Item 被采样的概率只跟他词频的排序相关，采样概率不是词的频率，但是推荐中的商品和 NLP 中的词可能不同，因此我们尝试了另外两个采样器：

* uniform\_candidate\_sampler：使用均匀分布来采样
* learned\_unigram\_candidate\_sampler：这个分布会动态统计训练过程中的词表，然后计算概率并进行采样

在我们的实验中learned\_unigram\_candidate\_sampler 可以实现最好的效果。除此之外，我们发现了类似[2]中的结论，负采样的数量是一个比较重要的参数，在显存允许的情况下，适当调高负采样的数量可以有效的提升模型收敛效果。

对于 Negative Feedback，我们直接使用 Sigmoid Cross Entropy Loss 来优化，将播放完成率低的 Item 全部看成负例，使其打分尽量低：

最终的总 Loss 则为两者的加和：

**03**

**实验**

**1. 分布式训练**

推荐场景的词表大小和数据量通常是巨大的，因此我们采用了 TensorFlow 中的 ParameterServer 策略来实现分布式训练的代码。调优过程中也积累了一些经验：

① 需要注意 Embedding 分片的问题，一个是 tf.fixed\_size\_partitioner 中的 size，另外一个是embedding\_lookup 中的 partition\_strategy，需要保持他们在 Training 和 Inference 过程中的设置是相同的。

② sample\_softmax 中的代码需要根据自己的场景来做优化，比如在我们的场景中，同一个 batch 中的重复 sample item 比例比较高，把里面的 embedding\_lookup 加上 unique，可以大幅提升训练速度。

③ 灵活使用 Mask 机制，可以有效的实现各种不同的 Attention 策略。

**2. 实验结果**

离线实验的指标采用 R@N，即打分排序的前 N  项结果包含Target Item 的比例，对于正向样本，指标称为 POS@N，我们希望这个值越高越好，对于负向样本，指标称为 NEG@N，我们希望这个值越低越好。由于篇幅限制，我们只列出一组主要的实验结果，这组实验验证了 Multitask Learning 和 Negative Feedback 的效果，我们在其他策略都采用上述最优的情况下（比如优化器，采样方法等），a 采用传统 DM 方式训练，只保留完播率较高的正反馈 Item 来构建行为序列，b 在 a 的基础上加入 Play Rate、Play Type 特征，c 在 b 的基础上再加入负向反馈信号进行多任务训练：

![](https://mmbiz.qpic.cn/mmbiz_png/EkgpOcjaJwiaUmZehdh8QRHaJkueOAG9nuM3RfZG70AoOv4pomoyBPeeFzCLcMNd70b5p83724ODAw1hZzlqKZw/640?wx_fmt=png)

可以看出，加入反馈信号（Play Rate）和歌曲点播 query 意图信号（Intent Type）后，b 的效果要优于 a，再加入 Negative Feedback 目标进行 Multitask Learning 后，c 可以保证 POS@N 微小变化的情况下明显降低 NEG@N。

我们在猜你喜欢的线上场景中也证明了新方法的有效性，和基于 DM 原方案的分桶相比，新模型（DM with Play Rate/Intent Type and NEG MTL）分桶的人均播放时长提高了 +9.2%；同时该方法已经应用于天猫精灵推荐的更多场景中并取得了不错的收益。

**04**

**参考资料**

[1] Covington P, Adams J, Sargin E. Deep neural networks for youtube recommendations[C]//Proceedings of the 10th ACM conference on recommender systems. ACM, 2016: 191-198.

[2] Hidasi B, Karatzoglou A. Recurrent neural networks with top-k gains for session-based recommendations[C]//Proceedings of the 27th ACM International Conference on Information and Knowledge Management. ACM, 2018: 843-852.

[3] Sun F, Liu J, Wu J, et al. BERT4Rec: Sequential Recommendation with Bidirectional Encoder Representations from Transformer[J]. arXiv preprint arXiv:1904.06690, 2019.

[4] Li C, Liu Z, Wu M, et al. Multi-interest network with dynamic routing for recommendation at Tmall[C]//Proceedings of the 28th ACM International Conference on Information and Knowledge Management. ACM, 2019: 2615-2623.

[5] Johnson J, Douze M, Jégou H. Billion-scale similarity search with GPUs[J]. IEEE Transactions on Big Data, 2019.

[6] Paudel B, Luck S, Bernstein A. Loss Aversion in Recommender Systems: Utilizing Negative User Preference to Improve Recommendation Quality[J]. arXiv preprint arXiv:1812.11422, 2018.

[7] Zhao X, Zhang L, Ding Z, et al. Recommendations with negative feedback via pairwise deep reinforcement learning[C]//Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining. ACM, 2018: 1040-1048.

[8] Vaswani A, Shazeer N, Parmar N, et al. Attention is all you need[C]//Advances in neural information processing systems. 2017: 5998-6008.

[9] Song W, Shi C, Xiao Z, et al. Autoint: Automatic feature interaction learning via self-attentive neural networks[C]//Proceedings of the 28th ACM International Conference on Information and Knowledge Management. ACM, 2019: 1161-1170.

[10] Devlin J, Chang M W, Lee K, et al. Bert: Pre-training of deep bidirectional transformers for language understanding[J]. arXiv preprint arXiv:1810.04805, 2018.

[11] Lan Z, Chen M, Goodman S, et al. Albert: A lite bert for self-supervised learning of language representations[J]. arXiv preprint arXiv:1909.11942, 2019.

**今天的分享就到这里，谢谢大家。**

---

分享、收藏、点赞、在看，给个4连击呗~

---

**会员推荐：**

DataFun会员计划重磅发布！多重权益加持，为你筑就数据科学家之路！扫码了解更多：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgsxWoxHJQg58ufp1ic0FSQHylQK7Oia8U6aCulPribG3O3Ks2BLobeae5kMTGf7GOp0dNsJKRvlLFag/640?wx_fmt=jpeg)

**文章推荐：**

[阿里飞猪个性化推荐：召回篇](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247506153&idx=1&sn=6ce4840ec9642deb8e1c97efdc727390&chksm=fbd76a85cca0e393c44815b55af12ceca91546d32b5aa6b6340cfb3bb4dbed94d88c5f741cb0&scene=21#wechat_redirect)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近600位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，8万+精准粉丝。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaalkxbGB7NU2Paq7KM3MPhXtxKJy9M6Bs8EicpUtqCUe6fgfV4HSiaHs7Q/640?wx_fmt=jpeg)

🧐**分享、收藏、点赞、在看**，给个**4连击**呗！**👇**