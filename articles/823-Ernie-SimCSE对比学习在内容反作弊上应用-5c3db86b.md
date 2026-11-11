---
title: 'Ernie-SimCSE对比学习在内容反作弊上应用'
company: 百度
tag: 搜索
date: 2022-11-17
url: https://juejin.cn/post/7166809706470572069
account: 
origin: harvest2-202607
---
# Ernie-SimCSE对比学习在内容反作弊上应用

[百度Geek说](/user/4186596000416094/posts)

2022-11-17
  
2,453
 
阅读10分钟

   

![在这里插入图片描述](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/a9f26dcf8abc4166b69f9e76a4eedb07~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

作者 | ANTI

> 导读
>
> AI技术在不同行业和业务被广泛的应用，本文介绍了反作弊团队在与spammer对抗愈演愈烈的趋势下，不断探索前沿技术，将百度NLP预训练模型结合对比学习用于解决spam内容中知道提问群发推广作弊的技术方案。
>
> 本次分享，首先介绍了知道提问群发推广作弊的形态，分析传统反作弊方案在此形态下的优缺点，对比了对比学习的数据增强和SimCSE两种方法，并分享了SimCSE论文中loss的缺点，最终引入『ernie预训练模型 + SimCSE』的解决方案，解决了线上大面积推广作弊问题。

> *全文4845字，预计阅读时间13分钟。*

# **01 背景**

百度作为最大的中文检索引擎，在满足正常用户检索需求的同时，吸引了大量的黑产用户，以非正常手段提高搜索结果排名，达到从中获益的目的。百度知道作为百度的重要子产品，也是全球最大互动问答社区，具有很高的hack价值，吸引了一大批spammer的『青睐』，spammer会不断试探反作弊系统的边界，不断寻找突破点，一旦攻破，短时间内就会爆发，降低用户体验，大大影响品牌美誉度。下面我们选择提问推广类作弊为例给大家介绍下这类作弊的识别算法：推广类作弊是社区最常见的作弊形式，被称为社区“牛皮藓”，该作弊具有范围广、团伙性强、变种多、变化快的特点。

知道的群发推广提问是不同用户推广相同实体，包括的类别包括培训类、医美类等，典型作弊如下：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/ab8b8d7ab5c9428bb3b582ca3a5e2537~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

传统的反作弊手段通常包括单提问和用户两个纬度来识别：

**1.单提问识别**：通过挖掘作弊pattern、训练语义分类模型来识别推广提问，优点是能够短时间内一定程度快速控制线上问题。

**2.用户识别**：用户纬度分为单一作弊用户识别和作弊用户群体识别，优点是可以在单提问基础上进一步对用户及其回答进行挖掘识别。

传统的挖掘方式对于提问和用户的刻画是通过人工feature，存在泛化性差、容易被绕过的缺点，不能应对内容变种多和快特点，而文本表示能够学习文本的稳定性表达，同时能够利用表达来刻画提问之间的相似性关系，因此，我们引入了文本表示学习来解决该类问题。

# **02 文本表示&对比学习**

## **2.1 文本表示**

文本表示学习就是将一段文本映射到低纬向量空间，获取句子的语义表示，大致经历过四个阶段：

* **阶段1**：统计类型，此阶段比较典型的是利用TD-IDF抽取关键词，用关键词表示表征整个句子。
* **阶段2**：深度模型阶段，此阶段方式较多，自从glove、word2vec等词粒度的表示出现后，在此基础有比较多的魔改，从对句子中的词向量简单平均、到有偏平均SIF[1]，后来引入CNN、LSTM等模型利用双塔、单塔方式进行学习句子表示，比较典型的几个工作有：
* 微软在排序搜索场景的DSSM[2]，将word进行hash减少词汇个数，对word的表示进行平均得到句子原始表达，经过三层MLP获取句子表示。
* 多伦多大学提出的Skip-Thought[3]，是word2vec的skip-ngram在句子表达的延伸，输入三个句子，用中间一句话，预测前后两句话。
* IBM的Siam-CNN[4]，提出了四种单塔、双塔不同的架构，利用pairwise loss作为损失函数。
* facebook的InferSent[5]，在双塔的表示基础上，增加了充分的交互。
* **阶段3**：Bert、Ernie等预训练大模型阶段，在此阶段比较基础典型的工作有：
* 由于Bert通过SEP分割，利用CLS运用到匹配任务场景存在计算量过大的问题，Sentence-BERT[6]提出将句子拆开，每个句子单独过encoder，借鉴InferSent的表示交互，来学习句子表达。
* **阶段4**：20年在图像领域兴起的对比学习引入到NLP。

## **2.2 对比学习**

对比学习是一种模型架构，也是无监督学习的一种，最开始是应用到了CV领域，通过对M图片进行数据增强得到N图片，将M和N图片输入encoder后得到表示Vm和Vn，如果两个表达相近则说明encoder学习的效果比较好。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/bc6d7a32bab64197be494218f83bee1d~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)
![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e52b32c76b9c4714982bea6220cc4708~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)
![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/55d859c515fc4e8aba79073516d25873~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)
![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/078b9aaf13de42518b364ad29ff3162b~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

比如上面四张图片，对于有监督的分类任务来说，需要分辨出每张图片到底是孙悟空还是猪八戒，训练数据需要具体标注出每一张图片的label。而对于无监督的对比学习来说，不需要区分图片是孙悟空还是猪八戒，只需要学习的表示能够表达前两张图片是相似的，后两张图片是相似的即可，也就是『相似的东西表示越相似，不相似的东西越不相似』。

对比学习的一般训练过程：

1.通过数据增强的方式构造训练数据集，对于一条数据，数据集需要包含正例（相似的数据）和负例（不相似的数据）。

2.将正例和负例同时输入到encoder模型中。

3.最小化正例之间的距离，最大化负例之间的距离，进行参数更新。

由于对比学习的目标是『相似的东西表示越相似，不相似的东西越不相似』，其核心实质上是需要找到『相似』的数据也就是正例，和『不相似』的数据也就是负例。通常，上面过程中的正例构造方式是相似term替换、term随机删除、回译等方法，而负例的选取是随机的，一般是In-batch negtives。在训练过程中，一个数据量大小为N的batch内，对于每个输入除了一对互为正例的数据，余下的N-2条都是负例。

## **2.3 SimCSE**

SimCSE（Simple Contrastive Learning of Sentence Embeddings）[7]是EMNLP2021中的一项工作，其简单的思想，确有着较好的效果收获了学术和工业界的巨大关注。SimCSE之前的对比学习中的相似性获取是通过数据增强的方式实现的，也就是在样本中添加噪声获取的，企图让模型从数据层面获取共性，而SimCSE从利用dropout从模型角度添加噪声，企图获取更稳定的共性抽取模型。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/6f1c37f5a2cb4c88a4e2f0503b961b8b~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

SimCSE提供了无监督（上图a）和有监督（上图b）两种架构，由于业务需要我们只用了无监督方式，其基本思路是：

1.同一个batch内的数据两次输入模型。

2.由于有dropout机制存在，对于同一句子的两次输出是不同的，两次输出互为正例，其他为负例。

3.最小化目标函数，进行参数更新。

论文中，在一个batch中，样本i的损失函数为对比学习的**InfoNCE Loss[8]**：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/4efac32a10d94b9fad07abf66848abb7~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

最终模型的效果在各个数据集上基本处于碾压的存在。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/68085947a6f24f36b5d2784846d6e124~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

# **03 应用**

由于业务需求是当有新增提问时，获取历史相似提问簇，因此整个过程分为三个阶段：

step1：训练ernie-SimCSE，获取句子encoder，本阶段主要获取编码器用来获取句子的语义向量；

step2：构建语义索引库，本阶段主要是得到语义索引，用于检索相似向量；

step3：反作弊策略，将相似向量用于反作弊策略，用于识别群发推广。

## **3.1 ernie-SimCSE**

目前对于预训练模型的应用从『预训练』+『子任务finetune』的模式过渡为『预训练』+『领域预训练』+『子任务finetune』，我们选取的encoder模型为当前中文领域最好的ernie模型，在ernie模型基础上增加SimCSE，训练过程为：

1. 在预训练基础上添加搜索Q-T匹配任务的训练，得到Ernie-Search，通过大规模点击日志构建Q-T图，我们在这张图上通过随机游走采样出q-t-q-t序列S = [q0 , t1 , …, qN-1 , tN] ，然后在这个序列上执行针对序列 S 的遮盖词预测完成预训练任务；
2. 在Ernie-Search的基础上利用，单独利用知道提问数据进行进一步post-train，得到Ernie-Search-ZD；
3. 在Ernie-Search-ZD，添加SimCSE对比学习，获取最终的模型Ernie-SearchCSE。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/fe5836a548754e1dbb0cd9698ac55861~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

## **3.2 问题及优化**

论文中的损失没有计算增强后的样本之间的损失，原因可能是由于计算成本的考虑，我们对损失进行了改进，对于增强后的数据也纳入负例的损失计算：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/f73f103e381448daa40a219ebe9fcf30~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

## **3.3 模型效果**

为了观测模型的最终效果，我们选取了之前的17个目标case，以及随机选取10个其它句子：

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/de3faeb9027a49dba17ca2a21de1ca93~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

由下方热力图可以看出，符合当初模型预期，前10个的相似性远大于后10个的相似性。对于提问『北京肋软骨隆鼻刘彦军做的怎么样？』检索索引库中语义最相似TOP 10获取疑似变形推广。

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/d3f717a08d6e49ab8c08f6d02a1ae40e~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

![图片](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0d319cdf8a4044e7b6764587f4e7a401~tplv-k3u1fbpfcp-zoom-in-crop-mark:1512:0:0:0.awebp)

# **04 总结**

语义索引在应用方面是一把双刃剑，一方面，相比传统的反作弊手段具有更好的泛化性能，另一方面，随着数据量的增加，索引库也会增加，存在计算复杂的问题。NLP领域目前已经处于相对成熟的阶段，在大模型预训练学习广而全的知识上，也为各行业、产品线的具体业务赋能，在此基础上，仍然有许多出色的工作不断涌现，我们也会持续探索前沿算法在业务上的落地，不断打击作弊内容，维护百度的内容生态安全，不断提升用户体验。

**——END——**

**参考资料**：

[1] Arora, S., Liang, Y., & Ma, T. (2019). A simple but tough-to-beat baseline for sentence embeddings. Paper presented at 5th International Conference on Learning Representations, ICLR 2017, Toulon, France.

[2] Huang P S, He X, Gao J, et al. Learning deep structured semantic models for web search using clickthrough data[C]//Proceedings of the 22nd ACM international conference on Information & Knowledge Management. 2013: 2333-2338.

[3] Kiros R, Zhu Y, Salakhutdinov R R, et al. Skip-thought vectors[J]. Advances in neural information processing systems, 2015, 28.

[4] Feng M, Xiang B, Glass M R, et al. Applying deep learning to answer selection: A study and an open task[C]//2015 IEEE workshop on automatic speech recognition and understanding (ASRU). IEEE, 2015: 813-820.

[5] Conneau A, Kiela D, Schwenk H, et al. Supervised learning of universal sentence representations from natural language inference data[J]. arXiv preprint arXiv:1705.02364, 2017.

[6] Reimers N, Gurevych I. Sentence-bert: Sentence embeddings using siamese bert-networks[J]. arXiv preprint arXiv:1908.10084, 2019.

[7] Tianyu Gao, Xingcheng Yao, and Danqi Chen. 2021. SimCSE: Simple Contrastive Learning of Sentence Embeddings. In Proceedings of the 2021 Conference on Empirical

[8] van den Oord, A., Li, Y., and Vinyals, O., “Representation Learning with Contrastive Predictive Coding”, *arXiv e-prints*, 2018.

**推荐阅读**：

[质量评估模型助力风险决策水平提升](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2F7yAL9Uw6JJJPQmFSki54Vg "https://mp.weixin.qq.com/s/7yAL9Uw6JJJPQmFSki54Vg")

[合约广告平台架构演进实践](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2F3ltb8HKPD6ZdXsMUeBBlMg "https://mp.weixin.qq.com/s/3ltb8HKPD6ZdXsMUeBBlMg")

[AI技术在基于风险测试模式转型中的应用](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FTf5jBCoru45v-E5FYx6-Fw "https://mp.weixin.qq.com/s/Tf5jBCoru45v-E5FYx6-Fw")

[Go语言躲坑经验总结](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FVS7DZg9qb_QmqAKqm_zc-Q "https://mp.weixin.qq.com/s/VS7DZg9qb_QmqAKqm_zc-Q")

[PaddleBox：百度基于GPU的超大规模离散DNN模型训练解决方案](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2Fo-ZoRnAMnINGHVALj7DQRA "https://mp.weixin.qq.com/s/o-ZoRnAMnINGHVALj7DQRA")

[聊聊机器如何"写"好广告文案?](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%2FCXFB337vdq8NuDTrjzCxmw "https://mp.weixin.qq.com/s/CXFB337vdq8NuDTrjzCxmw")