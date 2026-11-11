---
title: 'OPPO基于图神经网络的搜索推荐算法与实践'
company: DataFun
tag: 搜索
date: 2023-07-16
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247666990&idx=1&sn=bb9dc6240ac3143e0599916b7245fdaf&chksm=fbd9ff42ccae7654b235e46929fce990b0ce454d113d0fb32e48eccef92db311366d04e40252#rd
account: DataFunTalk
origin: wechat-mp
---
**![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzicG4JNibg4fM4icRVwXP5UmibMEaiaiapF9TBxMcG8Aguyicy2ica6QzY0gjnzMZudFHyibWhWXhbIMJdC6w/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)**

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/EBaibcQicPxgzRmUibTibuw3DSf4EYPbrROWIQyDjIbfyUfvU5ndFy4wSPCsOBNxNlNyHbfweAlJYUaYLMlwgE28KA/640?wx_fmt=jpeg)

**导读** 本文将分享图神经网络在推荐系统中的应用，以及在oppo业务场景中的实践。

**全文目录：**

1. 图神经网络背景介绍
2. 图在推荐系统的应用范式及介绍
3. oppo业务场景实践
4. 未来展望

分享嘉宾｜楼星雨 OPPO 高级机器学习算法工程师

编辑整理｜王露露 沃尔玛

内容校对｜李瑶

出品社区｜DataFun

---

**01**

**图神经网络背景介绍**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDck6mhxv3pYcfzicPfB0DMRYbr9PbWov92lmBkqUIHfnI2kc52sh9jEg/640?wx_fmt=png)

在讲图神经网络之前，首先要提到图表征学习，那什么是图表征学习呢？在CV和NLP领域，每一张图和每一个token以及语音里面的每一段话，都可以用向量去表征，最常见的做法就是用高维稀疏向量去进行表征。但在目前深度学习比较火热的情况下，大家更倾向于把高维稀疏的表征去嵌入到低维的稠密向量空间。

图表征也一样，图只是我们看待和组织数据的一种形式。就像传统NLP或者CV领域的一些图或者文字，也可以看成图网络的结构。图是更加泛化的，除了实体还可以把各种各样的东西都以图的形式组织起来。通过一些方法把图上面的节点或者边，甚至整张图以向量的形式来表征后便可应用于大量下游任务中，比如图分类、节点分类、链接预测、社区发现，图生成等。

图表征学习也经历了因式分解、随机游走和深度模型三个阶段。图神经网络主要是针对后面两个阶段。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDBrgww1XN3MCNB4Y1aU1Nx2ib80L7PdiaVsDNsbeAJn1yKfvKUIwPEQHg/640?wx_fmt=png)

图游走类模型，本质上是基于随机游走的方法，从图结构的数据上进行采样。通过节点的采样，将图结构的学习任务转化为序列的上下文建模任务，思想借鉴于NLP中Word2Vec的方法。

在图神经网络之前，传统的因子分解方法存在着一些问题，比如对非线性拟合能力不足，并且计算复杂度非常高，当图比较大的时候，时间消耗非常高。

相比之下，图游走类的方法，比如DeepWalk、Node2Vec，有两个非常好的优点：一是可解释性强，二是可以学习到高阶相似信息。比如有六个节点的一幅图，通过随机采样可以采样出一系列节点序列，隐式的包含了图结构上面的一些拓扑信息，当然在采样过程中会损失掉一部分信息，再通过一些skip-gram的方法，相当于拉近邻居节点的表征距离，推远非临近节点的一些表征，最终就可以将图中的节点都嵌入到相同空间上。相对于因子分解方法，这种方法在计算复杂度上是非常灵活的，可以比较高效地实现嵌入工作。

但是图游走类的方法也面临一些问题，比如传统的一些图游走方法只考虑了拓扑结构的一些信息，没有用到像节点的表征之类的信息；第二个问题是图游走方法大多数都是静态表征的，比如Word2vec方法，token都是提前生成，即使上下文发生改变，表征也不会变化，这类方法没有办法端到端学习，只能提前生成好，没办法跟随着下游任务同时进行训练；第三个问题是本质上图游走方法缺少了一些参数共享的机制，参数量会随着节点的数量线性增长，因为它会为每节点都生成表征，那么当节点数量过多的时候，参数量也会过去庞大。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDE2lhwdlSMjzs6U64ZZa5c02fufAeLk4FuSPmanObyVHkGpA7C9Ieww/640?wx_fmt=png)

在图游走方法之后，出现了基于谱域的图卷积的方法，其思想是如何充分利用图结构的信息，把图信号处理和卷积的思想结合在一起。以前大多数都是基于傅里叶变换的方法，相当于把空域的表征，先转化到谱域上，在谱域上做一些操作，再映射到空域上。这种方法涉及到矩阵分解，也是复杂度非常高的一种方法。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDssJcQ4DlCdTaYUciblRQ2drNojUQcunp6TYEMf26uDmZSqMSoLjNyyw/640?wx_fmt=png)

ChebyNets和GCN两个非常经典的网络，针对复杂度的问题做了很多工作。比如ChebyNets用Chebyshev多项式来近似图滤波器，通过这种方法规避了矩阵分解的操作，极大地降低了计算的复杂度。GCN对Chebyshev采取了一阶近似，本质上就相当于一些邻居的聚合操作，将整个谱域的图卷积迁移到了空域卷积，其感受野正比于图卷积的层数。由于图卷积操作需要依赖整个邻接矩阵，当图的规模很大的时候，依然没办法避免计算复杂度过高的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBD9LdTLicKUjHqJhg5U7ibmNj0H3gtmd7t0eLFBc3NHvl7W2icKZiaX7vu1A/640?wx_fmt=png)

在目前工业界成功落地并被广泛应用于各类真实业务场景的，大多数都是基于空域的图卷积方法。前面提到的基于邻居聚合的消息传播的范式，其核心就在于消息传递过程中采用一些邻居采样的方式，比如节点采样、层级采样、子图采样等等，极大幅度降低了计算复杂度，并且通过归纳方法把transductive学习扩展成了inductive学习，对于一些新的节点，只要能够知道其邻居有哪些，就能够得到新的节点的表征，非常灵活，泛化性强且复杂度较低。

介绍完了图表征学习和图神经网络的基础背景之后，我们接下来探讨图为什么在推荐系统中能有自己的一席之地。整体可以分为两部分：一是图这种数据结构本身在推荐系统中的价值，二是图神经网络在推荐系统中的优势。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDWO1joyX3V0edeuVA5e3wS2GPWxKkKY6DvVoZibaYZdzMmDbG8ZOqFug/640?wx_fmt=png)

图在推荐系统中的价值可以归纳为四个方面：

第一是用户的行为数据天然以图的形式存在，比如用户的点击购买行为，天然的就可以用图关联起来；

第二是图直接可以将不同类型的行为包含起来；

第三是图直接将不同场景的信息关联起来，用户在不同场景下的一些行为，可以通过整张图的形式关联起来。但是如果是以非图的形式，大多数都是flatten的形式，场景之间关系只是通过特征等方式隐式表征，但是图可以将这些信息用边的形式直接关联起来，比如最上面一副社交网络图的形式。中间这幅图是知识图谱的形式，橙色的节点代表的是item，右绿色代表了属性，最下面是交互图，是用户和item之间的交互，最终三张图汇聚成一张大图，包含了非常丰富的信息，既包括了用户之间的社交，也包括了用户和item之间的各种行为，当然还包括了item固有属性之间的关联。

第四点就是基于上面丰富的信息，能够非常有效地改善推荐系统中面临的行为稀疏和冷启动的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDO60LhQAAO67zrgrOSibvAvPSg7Q47opWBDG7Tm60Tw0o1sCicZVNxpNw/640?wx_fmt=png)

上图分为两部分，上面部分是传统的模型，下面是图神经网络模型。

传统模型比如双塔模型，只依赖于两个目标节点之间的交互以及节点自身的信息，并没有直接依赖目标节点的邻居信息。在实际的运用中，比如要基于30天去构建训练集，会有时间展开的操作，基于当天的以及昨天的，以及30天前的数据构建训练集，本质上可以展开成时序图的形式。每个时间点上的图是相互独立的，比如说在t-n天前，有U1和U2两个用户，并且U2用户跟I2发生交互行为，在t-(n+1)天的时候，U1、U2和U3又跟I1和I4有一些行为交互，最终构建的训练集是针对不同的时间点的交互行为独立的当作数据样本。比如U2和I2是一条正样本，U2和I1又是一条负样本。

图神经网络的建模方式本身用到的信息会更加丰富。刚刚提到只包含了用户与用户之间的一些关联以及item之间的关联信息，如果从静态的角度来看，是直接对整张大图进行消息聚合。真正建模的时候会对时间进行展开，相当于每个时间都会贡献一部分样本。

图也可以按照时间展开，展开之后是右下角的这幅图，用到的信息会相比传统模型更加丰富，从单独的时间点对比，图上面包含的信息就会比传统模型要更加丰富。在建模时，除了用到节点本身的信息以及交互的信息之外，还会用到其它一些side
information。

除此之外，在做消息聚合的时候，图神经网络还可以依赖于之前时刻的邻居。比如说t时刻的节点聚合邻居的时候，除了聚合本时间的一些邻居节点的信息，还可以去动态的依赖于t时刻之前的一些信息，相当于整个建模从iid的样本的格式变成了非iid的形式。

总结来看，图神经网络整体建模可以用到的信息量大于等于传统模型，这是图建模的天然的优势。

**02**  
**图在推荐系统的应用范式及介绍**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDoxy3ia0ianI2XAqRGF0BaiaYzKP4HFeCXEzibOUNKvKNvTuH2Cwm8Qk0xg/640?wx_fmt=png)

推荐系统大部分都可以拆成四个模块：召回、粗排、精排和重排。本文主要讲召回和精排部分。图在推荐系统中的应用，可以从非常多的角度出发去分类，本文以场景为主，图为辅，去划分大类，再根据算法细分类。

图在召回模块的应用，一类是作为独立的召回路，另一类是和已有的主召回路做融合。如果以单独的图召回路形式存在，又可以分为图策略和图表征。

图策略根据整张图的结构，通过一些规则的定义去直接为user或者query去构建召回列表，里面会涉及到大量的与场景业务相关的规则上的知识来筛选召回列表。

图表征可以分为端到端和预训练两种方式。它们最大的区别是端到端更加依赖业务场景的监督信号，而预训练更多的是去挖掘图本身内在的一些信息。端到端又可以拆分成知识图谱、社交网络、行为网络等一些建模方式，预训练则可以划分成对比类、生成类和预测类。

除了图召回路，另外一种应用方式是图融合。是把图与双塔模型进行结合形成召回路。融合的方式也有两种，第一种是作为特征，比如通过图的一些图拓扑结构的特征，作为特征输入到双塔模型中，或者通过一些预训方式得到一些Embedding类的特征作为特征输入。还有一种是图本身模块跟随着双塔模型进行端到端的训练，图具体放在哪个塔，又可以拆分成两类，放在User塔可能是一个社交网络；放在item塔，可能是知识图谱，也可能是交互的网络；也可以在两边的塔都放入图子网络一起去学习。

精排跟召回的最大区别是精排一般只涉及一个主模型，因此这里不存在子路的概念，只会涉及图作为子网络跟精排的主模型共同参与训练，或者为精排提供特征的功能。无论是提供特征，还是精排端到端训练，图在里面的最大作用是充分发挥图本身的优势，来解决精排任务面临的一些特定的问题：比如需要特征精炼，特征稀疏、行为稀疏等情况去挖掘特征间的交互，或者去挖掘用户的兴趣，以及通过图去缓解冷启动问题，或者基于图将用户在多域上面的一些多行为统一关联起来作为丰富的表征来给到精排模型。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDmlOjHJTiaNBQ9T5K981Y9OAicXeickxKy1bpA8rM9yXSE7AupXFKGxKqw/640?wx_fmt=png)

图召回主要介绍端到端、预训练和子网络三类工作。

端到端整体以图模块为主，推荐任务为监督信号为主要来源。

图预训练也是以图模块为主，但是以自监督任务为监督信号的主要来源。比如通过预训练之后可直接以Embedding的方式进行I2I召回，甚至是U2I等召回。也可以作为初始化或者预训练好的子网络，参与到推荐任务里面进行微调。这种方法和端到端的最大区别在于监督信号在训练中是否占据主导地位。

图子网络以图模块为辅，主模型结构比如双塔结构为主。其下游目标任务比如CTR建模也是整个监督信号的主要来源。

上图中也介绍了一些经典算法，感兴趣的同学可以去详细了解每个方向的内容。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDlfsd76ohZYUibibM4JHRK1iahbUzR7dE4l7pT2gtWcXDibYf5ZAodvibQPg/640?wx_fmt=png)

精排在业界的工作主要是图特征和图子网络两块。

图特征，比如明文特征，可以加入一些拓扑特征，或者任务相关的特征，去作为当前特征的补充。预训练生成好Embedding的特征一般会针对精排某一类特定的优化方向去生成一些特征。比如冷启动的问题，可以通过图网络的方式，为id类的特征去生成一些更加丰富的表征，来针对新的item增强他的表征能力。

推特所采用的TwHIN，也是基于用户在多场景多行为的行为关系构建了非常大的图谱，基于图谱去生成user以及tweet的表征，表征可以输入到精排模型里面去参与下游训练。

图子网络，比如特征精炼、特征交互和意图挖掘，针对某种特定精排任务面对的特定问题，通过设计图神经网络的结构，来帮助精排模型针对某一类的问题提升表达能力。

**03**  
**oppo业务场景实践**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDiclw1QicvYauplPfOGibFiab3SGSjpTOEZw4k6kGfc5BFW882jQiaibqhFGw/640?wx_fmt=png)

oppo的图架构如上图所示，包含数据层、平台层、算法层和应用层，本文主要介绍的是其中基于图学习的推荐的解决方案，用在oppo搜索推荐广告的业务，除此之外还包含安全、风控、营销、增长和供应链优化等很多业务方向。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDwltMibHKictcd8aQwP9Zrc2pg0Ox4dN0aM4BQdnYwI31dhMlPiaosD0qA/640?wx_fmt=png)

oppo非常经典的一个应用场景是应用商店，作为手机厂商，应用商店是非常核心的场景。在为用户推荐app的时候，也面临一些问题：

首先推荐对相关性要求比较高，要与用户的输入意图有非常好的匹配；

另外，query分布是天然存在长尾问题的，用户在应用商店搜索的时候，虽然大量的query都集中在头部，但每个人都有一些自己的行为习惯，导致整个query呈现长尾分布的情况；

第三，存在语义不明确，例如上图中的两个场景，第一幅图是联想，用户在输入词的过程中，会为他推荐app。第二副图是用户输入完query，点击搜索，为他返回app。针对第一个场景，用户在输入的过程中还没有点搜索，但他停顿了一下就会触发一次请求，请求只是一些完整词的前缀，比如包含这个词的，存在语义非常不明确的情况。

最后是语义不匹配的问题。因为app可用到的信息从字面上来看名称非常有限，其描述大多数也是非常泛或者文本非常长的，而query是短文本。query的语义信息跟app语义空间可能会存在一些gap。

针对上述问题，我们在构建模型的时候，应该选择合适的方式去切入。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDonzwnvCgrEBR92ayMbzSX9YYx6Ngd3CiaibvVEuXLaFEEHgpeob0evRg/640?wx_fmt=png)

首先，针对相关性的要求，图端到端模型会发现模型过度依赖高阶的邻居。比如用二阶、三阶的邻居聚合时会引入一些非相似性用户噪声。因为有非常强的相关性要求，导致相关性出现明显下降。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDeHDcy1TQ4KP3TPiaDcA7ZNhcb90JjB0fL76zzSAPjBiaibxtbN48HtsXg/640?wx_fmt=png)

双塔模型本身基于节点的一些交互关系去进行建模，虽然代表泛化性，但对于相关性还是有一些比较好的保证。图网络做高级关系为辅，如果直接加到用户塔会引入一些高阶的邻居信息，同样会存在稀释用户当前意图的问题，这两点表明双塔在相关性的建模上相对图模型是会有一些优势的。

另外，query存在分布长尾的特点，直接使用基于信息建模会存在信息不充分的问题。query比较短，语义不够聚焦，直接通过语义信息去挖掘query的表征会存在挖掘不到充分信息的问题。即使扩展用户的历史query序列，对于一些新用户也是比较难覆盖的。而且用户在应用商店的行为历史并不会特别多，不像信息流或电商场景，用户会经常来点，应用商店大家下载的频率会相对较低一些。

另外用户历史的query仍然会被头部query占主的，即使扩充了query的序列，长尾query的信息量还是非常少，对建模仍然不够充分，这是传统双塔建模的不足之处。

第三点是app与query语义信息不一致的问题， app用的物料和信息相比于电商场景中的商品来说会更加有限，因为它的素材并没有那么多。另外，从广告的角度来讲，现代广告素材质量上面也会相对比较差，会存在很多图文不符的素材，比如图片跟文字没有太大关联，甚至跟整个广告都没有太大关系，只是为了诱导点击。

图模型有天然的优势去解决长尾的query与app语义无法对齐的问题，因为图模型可以基于用户的历史行为进行信息补充，也可以基于app属性通过知识图谱的方式将同类属性的一些app的信息来聚合到target
app中去增强app的表征。

双塔和图模型各有优劣点，我们最终选择在双塔右侧的item侧加入图子网络。一方面规避因为图引入而导致的相关性下降的问题；另一方面考虑到通过图的方式对双塔的表达能力进行进一步的提高。

具体结构非常简单，左边是非常经典的双塔形式，我们在右塔加入了图网络模型。左塔是use和query两个表征，右塔是针对app的表征。经过实验会发现，输的是3-hot子图来增强app的表征，用来缩减query和app的语义gap。具体来说，一阶基于query和app的交互图，一阶邻居是app直接交互的一些query；二阶是一些行为相似的app；三阶的邻居是交互稀疏的一些 app，和比较友好的一些交互稀疏。因为我们会对图做一些裁剪，对于稀疏行为的app，如果只用前两阶用到的交互类的query信息量还是非常的少。

具体使用中，参考了NIA-GCN的做法，针对每一阶的邻居分别做直接聚合，相当于每一阶邻居都将自身的信息直接传递给中心节点。最终通过自适应的学习方式将三阶表征融合在一起。

图子网络有两个要注意的点：

* 图网络边用到的特征跟app塔的特征没有共享，主要是为了防止app本身的特征表征淹没了图网络想学习到邻居关系，或者说行为关系的表征。共享因为会存在邻居信息在聚合的时候，周围的邻居都比较相似，最终聚合到的东西更多是表意特征本身的一些信息。我们把它拆开成两部分，没有共享Embedding，发现效果会更好一些。
* 第二方面，图子网络与user塔去共享query相关特征，因为最核心的是要去增强app的表征，为app添加一些交互类的query表征进去，让两边表征适当进行对齐，在对齐过程中共享Embedding才能够更好的让两边对齐。

最终实验发现，加入图子网络相比于不加，在query和item上面都有提升，尤其在item上面会有比较明显的提升。相当于用户点击下载的一部分app在加入图子网络之后会被排到序列头部位置。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDaia5ddGxTv2VagxTpNwvCw1K11l7aWoI3FutLfT37P6eEV5AiafX0orQ/640?wx_fmt=png)

在精排侧的一些工作，主要考虑到怎么去用图网络做自动特征交叉。结合了业界的一些工作，我们先按user和item去拆分特征组，特征组内部用inner-interaction方式建模，而特征组之间则通过cross-interaction来捕捉user特征和item特征之间的交互关系。图中里面每个节点都是特征，比如绿色的节点是用户特征，蓝色的是app的特征。那么在每个特征组里，节点和节点之间的连边代表交叉特征的关系。模型会自动去学习交互特征之间边权。实验中发现，自动学习边权学到的边权都是非常接近的，信息并不充分，因此使用L0正则的方式来确保边的稀疏性，让一些边权为零，也就是一些交互特征会被mask掉，这样可以自动挖掘一些比较有效的交互特征并且避免引入过多的噪声。

图中左边是正常的DNN网络，因为图子网络相对来说比较独立，整个CTR模型结构可以是任意的。只不过图网络块充当了自动特征挖掘的工作。

最后使用stacking
2-layer的方式，选了两层网络，同时可以建模低阶的比如二阶交互以及显式相对高阶的交互。最终在融合的时候也会把原始特征加进来同时输出，再跟DNN网络做融合，最终参与到下游的loss function里面。加入图网络模型，并且去掉手动的交叉特征之后，在AUC和GAUC都有一定的提升。

**03**  
**未来展望**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgp4IKKyRnqjuW6AzLVzOBDiaF1pn8F6NZPXWPfAYBLjUWtKgdanv8RJuKXbMcOVWD521hiatlVfneQ/640?wx_fmt=png)

第一点是我们希望更好地利用oppo内部用户、应用以及广告等实体在多个场景的多种交互行为，得到统一的预训练表征或模型。前文中提到的方法更多的是针对单场景，或者少量场景进行建模，我们希望充分发挥图的优势，能够将更多的场景同时关联起来，同时去得到用户或者应用广告的实体的丰富多行为的通用表征。得到表征之后可以直接用在下游的各种任务中作为特征，或者作为召回模块直接基于表征进行显式召回。

第二点是噪声过滤的问题。之前也提到了图神经网络相对于传统模型而言，最大的优势是可以用到的信息量比较多，但一般来说能用到的信息量多，噪声也会比较大。如果带来的噪声比带来的信息更多，很有可能加入图模型，反而效果不如之前。这在推荐场景也是非常显著的问题，因为用户的一些行为是比较隐式的，基于高阶的交互的时候，隐式的行为会造成内容指数级膨胀。如何在这种情况下将图结构尽量保留有用的信息，过滤噪声，也是一个值得研究的问题。

**今天的分享就到这里，谢谢大家。**

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/EBaibcQicPxgxOLHLmY7yfKJIrkicxfjQwaEIaRw65GE5mfaKbcW3BfCic6YFvE18rZyOj5MLG5QUAmGLPMAouRUww/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&wx_co=1)

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/EBaibcQicPxgxZasYapThAzR5z3HibMNg6HSNV8tGMxVd0BfRuwIImjmicCSrtECoKe1GZd7FhUMb9lic2icLz7ibYrIQ/640?wx_fmt=jpeg)

分享嘉宾

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhMVlAicK2vCJaiaJK09QvazZ9WJnwx6fbux1feibmJoFy1vos6htHIh8gVPPWAFNBl7AKxcpSAZ6xsA/640?wx_fmt=gif)

楼星雨

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhMVlAicK2vCJaiaJK09QvazZ9WJnwx6fbux1feibmJoFy1vos6htHIh8gVPPWAFNBl7AKxcpSAZ6xsA/640?wx_fmt=gif)

OPPO

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhMVlAicK2vCJaiaJK09QvazZ9WJnwx6fbux1feibmJoFy1vos6htHIh8gVPPWAFNBl7AKxcpSAZ6xsA/640?wx_fmt=gif)

高级机器学习算法工程师

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhMVlAicK2vCJaiaJK09QvazZ9WJnwx6fbux1feibmJoFy1vos6htHIh8gVPPWAFNBl7AKxcpSAZ6xsA/640?wx_fmt=gif)

2017年硕士毕业于中山大学，曾就职于平安科技和蚂蚁金服，负责自然语言理解和生成方向，并登顶SQuAD2.0和GLUE两大榜单。2021年加入OPPO研究院数据智能研究部拓扑Lab，任职高级机器学习算法工程师，目前从事图神经网络和推荐系统方向的工作。

**▌2023数据智能创新与实践大会**

**4大体系，专业解构数据智能**

**16个主题论坛，覆盖当下热点与趋势**

**70+演讲，兼具创新与最佳实践**

**1000+专业观众，内行人的技术盛会**

*现在添加好友咨询，可*****限时获取以下优惠（6选3）****

 DataFunCon北京线下峰会内部专享PPT

 DataFun平台的视频回看年卡一张，价值365元！

 数据智能地图1套，价值69元 实体印刷版

 额外送线下私董会门票（3次现场互动）价值900元！

 线上职业规划课程体验卡1张，价值1000元/小时

 专家闭门晚宴，仅限企业部门leader参加（需主办方审核）

![](https://mmbiz.qpic.cn/sz_mmbiz_png/jIzrGqwK4KWiaBmEuMeu3VhAdpfrOx4uj5ovNJiaVZFRFOMtLYicF2rqmyn9zyPkjIk6tvtTcre9AIy9W855z7KAg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

[![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPiakn6GSIAXpJPVS7UIUAAYB8JWtD6mib4EqC0fdSU3p6PVqHaSp7Uuzg3IM0Xxnp0T5GFHicU8Lniasw/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247666865&idx=6&sn=45f73969e178b0663f7d306a4b2c1598&chksm=fbd9feddccae77cb4fa2e5e3c8ea30de816b9daf981d4d5ce0cdffbf349ab1218d3e367eaf3f&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/S5UJY62OKojQ2rGAKO0tVGDCE95rYg3ObmzjjyYDjknXltNtTlv5oHwFlj82K95sODttE3icZLnibWUHKll89ibmQ/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

点个在看把好内容分享给更多人

![](https://mmbiz.qpic.cn/mmbiz_png/Z7Wamsw2LOnPAia3Da0eV0cphvoaGNH5ebhYaZyqKoXbMD9bWqxndic39qMXLksCq9yfQxGZRMVYickD2YkLMs8kw/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

![](https://mmbiz.qpic.cn/mmbiz_png/DicsabZnZZwqjJIibOTjlfg48Qm1RLmJY0my9jUEgIEXevXLDLh2vYstZbxymzuDWcI5U3pxy2lD9g9Oao3SOVPA/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

**👇**点击**阅读原文**直达线下大会官网