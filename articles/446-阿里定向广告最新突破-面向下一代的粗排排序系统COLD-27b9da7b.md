---
title: '阿里定向广告最新突破：面向下一代的粗排排序系统COLD'
company: 阿里妈妈
tag: 粗排
date: 2020-08-18
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247505774&idx=1&sn=63efc686d3dda67fa4631e5550560476&chksm=fbd76502cca0ec141440482e048196119101abd0a56dd5dba7c9a18f46ba8f0358e3a458408b&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgxBP9s4glicBX52cplV822vrJCP5icouEwldVT8UCdUprEraay6j8oVWIejviaB99pb8Thjz2pargjA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeDv6OTBP2PXtScic1ffcCDLCz2lTo9rliaCvSMuBYPNZk6BDoXhqAGKMA/640?wx_fmt=png)

文章作者：萧瑟 阿里妈妈

内容来源：炼丹实验室@知乎

**导读：**这次向大家分享的工作是我所在的阿里定向广告团队在DLP-KDD 2020发表的文章：COLD: Towards the Next Generation of Pre-Ranking System。COLD是我们新一代粗排排序系统，目前已经在阿里定向广告各主要业务落地并取得了巨大的线上效果提升。论文地址：

https://arxiv.org/abs/2007.16122

**01**

**粗排简介**

在搜索，推荐，广告等需要进行大规模排序的场景，级联排序架构得到了非常广泛的应用。以阿里的在线广告系统为例，按顺序一般包含召回，粗排，精排，重排序等模块。粗排在召回和精排之间，一般需要从上万个广告集合中选择出几百个符合后链路目标的候选广告，并送给后面的精排模块。粗排有很严格的时间要求，一般需要在10～20ms内完成打分。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeexCLfsCkaJhS0Ku3kZepOVQPPQeSnpxmsoGVP0VicxNFGUBKW1IsiaURA/640?wx_fmt=jpeg)

**02**

**发展历程**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeejmWh7Z8uQ3g7UiaBEiclibphLdwicJHcSIGHeL1Wa9OWJu2PqYibUgSz7vg/640?wx_fmt=jpeg)

粗排在工业界的发展历程可以分成下面几个阶段：

* 最早期的第一代粗排是静态质量分，一般基于广告的历史平均CTR，只使用了广告侧的信息，表达能力有限，但是更新上可以做到很快。
* 第二代粗排是以LR为代表的早期机器学习模型，模型结构比较简单，有一定的个性化表达能力，可以在线更新和服务。
* 当前最广泛应用的第三代粗排模型，是基于向量内积的深度模型。一般为双塔结构，两侧分别输入用户特征和广告特征，经过深度网络计算后，分别产出用户向量和广告向量，再通过内积等运算计算得到排序分数：

  ![](https://mmbiz.qpic.cn/mmbiz_svg/vDwntJFbiafuycxRJ9Q3GiaZC7kkAnTJtGD2nibYibntcexcKxdcVRWqJsdB0Q3ty2nzO0S3jqQspQLwewrLdiaWibaRdGWuL8fmNa/640?wx_fmt=svg)

向量内积模型相比之前的粗排模型，表达能力有了显著提升，但是仍然有很多问题：

* 模型的表达能力仍然受限：向量内积结构虽然极大的提升了运算速度，节省了算力，但是也导致模型无法使用交叉特征，能力受到极大限制。
* 模型实时性较差：因为用户向量和广告向量一般需要提前计算好，而这种提前计算的时间会拖慢整个系统的更新速度，导致系统难以对数据分布的快速变化做出及时响应，这个问题在双十一等场景尤为明显。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeen38Yrz9RInPGQQx4cqjuPqSM4xbyHwk3O7Ra2RNVW6hZSzHVUKCfg/640?wx_fmt=jpeg)

**03**

**COLD模型**

前面粗排的相关工作仅仅把算力看做系统的一个常量，模型和算力的优化是分离的。我们重新思考了模型和算力的关系，从两者联合设计优化的视角出发，提出了新一代的粗排架构COLD (Computing power cost-aware Online and Lightweight Deep pre-ranking system). 它可以灵活对模型效果和算力进行平衡。COLD没有对模型进行限制，可以支持任意复杂的深度模型。这里我们把GwEN ( group-wise embedding network) 作为我们的初始模型结构。它以拼接好的特征embedding作为输入，后面是多层全连接网络，支持交叉特征。当然，如果特征和模型过于复杂，算力和延时都会难以接受。因此我们一方面设计了一个灵活的网络架构可以进行效果和算力的平衡。另一方面进行了很多工程上的优化以节省算力。

**1. 网络结构**

精简网络的方法有很多，例如网络剪枝 ( network pruning)，特征筛选 ( feature selection)，网络结构搜索 ( neural architecture search)等。我们选择了特征筛选以实现效果和算力的平衡。当然其他技术也可以进行尝试。具体来说，我们把SE (Squeeze-and-Excitation) block引入到了特征筛选过程中，它最初被用于计算机视觉领域以便对不同通道间的内部关系进行建模。这里我们用SE block来得到特征重要性分数。假设一共有M个特征，ei表示第i个特征的embedding向量，SE block把ei压缩成一个实数si。具体来说先将M个特征的embedding拼接在一起，经过全连接层并用sigmoid函数激活以后，得到M维的向量s：

![](https://mmbiz.qpic.cn/mmbiz_svg/vDwntJFbiafuycxRJ9Q3GiaZC7kkAnTJtGU2BElx9wP2nxsLDK7oDKAOFolUwhETLHWic8uYHibQrOX5cX9SZ43eSDPDjyX1eKkp/640?wx_fmt=svg) 

这里向量s的第i维对应第i个特征的重要得分，然后再将si乘回到ei，得到新的加权后的特征向量用于后续计算。

在得到特征的重要性得分之后，我们把所有特征按重要性排序，选择K组不同的候选特征，并基于GAUC，QPS和RT指标等离线指标，对效果和算力进行平衡，最终在满足QPS和RT要求情况下，选择GAUC最高的一组特征组合，作为COLD最终使用的特征。后续的训练和线上打分都基于选择出来的特征组合。通过这种方式，可以灵活的进行效果和算力的平衡。

**2. 工程优化**

为了给COLD使用更复杂的特征模型打开空间，工程上也进行了很多优化。在阿里定向广告系统中，粗排的线上打分主要包含两部分：特征计算和网络计算。特征计算部分主要负责从索引中拉取用户和广告的特征并且进行交叉特征的相关计算。而网络计算部分，会将特征转成embedding向量，并将它们拼接进行网络计算。

**① 并行化**

为了实时低延时高吞吐的目标，并行计算是非常重要的。而粗排对于不同广告的计算是相互独立的，因此可以将计算拆分成并行的多个请求以同时进行计算，并在最后进行结果合并。特征计算部分使用了多线程方式以进一步加速，网络计算部分使用了GPU。

**② 列计算转换**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeeeJKzLe8ktuAyo5pQdicHeUtT1a6icibYx3x1Kl2rAmM5Mm375lYu6jdA/640?wx_fmt=jpeg)

特征计算的过程可以抽象看做两个稀疏矩阵的计算，一个是用户矩阵，另一个是广告矩阵。矩阵的行是batch\_size，对于用户矩阵来说batch\_size为1，对于广告矩阵来说batch\_size为广告数。矩阵的列是featue group的数目。常规计算广告矩阵的方法是逐个广告计算在不同feature group下特征的结果，这个方法符合通常的计算习惯，组合特征实现也比较简单，但是这种计算方式是访存不连续的，有冗余遍历，查找的问题。事实上，因为同一个feature group的计算方法相同，因此可以利用这个特性，将行计算重构成列计算，对同一列上的稀疏数据进行连续存储，之后利用MKL优化单特征计算，使用SIMD (Single Instruction Multiple Data)优化组合特征算子，以达到加速的目的。

**③ Float16加速**

对于COLD来说，绝大部分网络计算都是矩阵乘法，而NVIDIA的Turning架构对Float16和Int8的矩阵乘法有额外的加速，因此引入Float16计算对提升性能非常必要 。但是Float16会损失计算精度，特别是在sum-pooling的情况下，数值有可能超出Floa16的范围。为了解决这个问题，一种方式是使用BN。但是BN本身的参数范围也有可能超过Float16. 因此只能使用混合精度的方式，对于BN层使用Float32，而后面的层使用Float16。另一种方式是使用参数无关的归一化方式，例如log函数。但是log函数不能处理负数，并且输入值接近0的时候会输出绝对值较大的数字。因此我们设计了一种分段平滑函数，我们叫做linear-log来解决这个问题：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeJGmAZOoCXGljjFzymandkMb7ZrYFzP8DFQvRHx3TpKEXws7WGiaicsPg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeJWWcD6Wl4bvOt4K8lBAfr2Q9jMob4V3GicM2p14RjqpMliaJgCgF7Jng/640?wx_fmt=jpeg)

从函数图像可以看出，linear\_log函数可以将Float32的数值处理到一个比较合适的范围。所以如果我们将linear\_log函数放到第一层，那么就可以保证网络的输入参数在一个比较小的范围内。具体实践上，linear\_log函数对COLD模型的效果基本没有影响。使用Float16以后，CUDA kernel的运行性能有显著提升，同时kernel的启动时间成为了瓶颈。为了解决这个问题，我们使用了MPS (Multi-Process Service)来解决kernel启动的开销。Float16和MPS技术，可以带来接近2倍的QPS提升。

**3. 在线服务架构**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeANe5NVADFbQmUaUSCfRXOScI8VTgX5rewtc8nRF2bSesVcPMQMLarw/640?wx_fmt=jpeg)

COLD没有限制模型的结构，训练和在线打分都是实时化的，可以带来以下两个优点：

* 在线学习的引入使COLD与向量内积模型相比，可以更及时的响应数据分布的变化，对新广告冷启动也更为友好。
* 实时架构对于模型迭代和在线A/B测试都更有利。向量内积模型由于用户向量和广告向量需要提前计算好，在线A/B测试也更为困难。实时架构也使COLD模型可以更快的更新，避免了向量内积模型的更新延迟问题。

**04**

**实验结果**

这里COLD模型使用了7层全连接的网络结构。离线评估指标除了GAUC之外，还包含了top-k recall，用于评估粗排和精排的对齐程度。

![](https://mmbiz.qpic.cn/mmbiz_svg/vDwntJFbiafuycxRJ9Q3GiaZC7kkAnTJtGpXVIO4wQSibicU8CrTEiawUfUqo2fUWzo3Aiap3FZ2LsXcxS2DriaB0LjW8cG7CjQibibhF/640?wx_fmt=svg)

这里top k候选集合和top m候选集合均为粗排的输入打分集合。top k集合是粗排选出的，而 top m集合是精排选出的，排序指标是eCPM(eCPM = pCTR\*bid)。这里的精排模型是DIEN。我们使用QPS (Queries Per Seconds, which measures the throughput of themodel) 和RT (return time, which measures the latency of model)来评估系统性能的影响。

**1. 模型效果评估**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeewPumcALdWqsWXj292O2PR7KesCibiaX5h0Fm5stf1HUxLCkOtzlpyOaw/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeZphBtDALXllYS6MND0o4PZCuzqoXaTt22rfUFGVfe8YNAFdrHibzeXQ/640?wx_fmt=jpeg)

离线效果评估可以看到COLD在GAUC和Recall上都优于向量内积模型。在线效果上，COLD与向量内积模型相比在日常CTR +6.1%，RPM + 6.5%。双十一CTR+9.1%，RPM+10.8%，提升显著。

**2. 系统性能评估**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeetkBuMGs96LUq6GTtYwU9bIeqcLYIdxEf7dxiaI3Znvc4hcMnb3HmPlg/640?wx_fmt=jpeg)

从Table 3可以看到，向量内积模型的系统性能最好，而精排的DIEN的系统性能最差，COLD则在两者之间取得了平衡。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeetswdrIgRzXU1BBUyZLr09Syl9Sibwphc9RdWlKxnTn0ribE2edqgMf1g/640?wx_fmt=jpeg)

COLD在得到特征重要性分数以后，会选出不同的候选特征，并基于离线指标进行特征选择。Table 4列了几组供选择的特征，可以看到COLD是考虑效果和系统性能以后的折中。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhIGzFK8FfnFS8Ld1BKZibeeJK4xbOiaDIfXOXImpEONyww5xLReoF0q7hlk3YduIFlcODyP75jQ4kQ/640?wx_fmt=jpeg)

Table 5表明，工程优化上引入Float16和MPS优化以后，QPS提升了1倍，效果显著。

**05**

**总结**

这里我们向大家详细介绍了阿里定向广告的新一代粗排架构COLD。它是新的算法和算力联合迭代视角下的产物。COLD把算力作为一个变量进行优化，提供了一种更灵活的方式可以实现效果和算力的平衡。COLD的训练和在线打分都是实时的，可以更好的适用数据分布的变化。2019年以来，COLD已经在阿里定向广告的各主要业务上得到广泛应用并取得了显著的效果提升。

**原文链接：**

https://zhuanlan.zhihu.com/p/186320100

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个三连击呗~~

---

**社群推荐：**

欢迎加入 DataFunTalk 广告算法交流群，跟同行零距离交流。如想进群，请识别下面的二维码，根据提示自主入群。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgnvG7iat6bFV7s6GLyLbNlj4BXEtoqQricmT6sm3lZemw1jV4wFsDySiaxZLImIHpTmibyjRKX6c1Rqw/640?wx_fmt=jpeg)

**文章推荐：**

[阿里妈妈：基于动态背包的多场景广告序列投放算法](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247505578&idx=1&sn=bc6f551bc83039cebe016ba87cdf8a46&chksm=fbd764c6cca0edd0befcbb887b5b15f10296de6cd6d92ed3382221fcb367c92079b99c895914&scene=21#wechat_redirect)

[阿里妈妈点击率预估中的长期兴趣建模](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247496080&idx=1&sn=70f79a37a6000965fa96bccf893b9c40&chksm=fbd743fccca0caeadb59820801597c51353b0a4ba080d2caf66eccb6644102c2fe674ffcb378&scene=21#wechat_redirect)

[阿里妈妈：电商预估模型的发展与挑战](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247490293&idx=1&sn=4dcd1cf5f945c03c98ed3401afb7983d&chksm=fbd4a899cca3218f328a661da553b470e018eeeef2ca3bf2696140ef045f1805f89b8c3a596a&scene=21#wechat_redirect)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近500位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，7万+精准粉丝。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaalkxbGB7NU2Paq7KM3MPhXtxKJy9M6Bs8EicpUtqCUe6fgfV4HSiaHs7Q/640?wx_fmt=jpeg)

🧐**分享、点赞、在看**，给个**三连击**呗！**👇**