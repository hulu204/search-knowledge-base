---
title: '阿里妈妈深度树匹配技术演进：TDM->JTM->BSAT'
company: 阿里妈妈
tag: 召回
date: 2020-09-04
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247507022&idx=1&sn=aa4a99562a274b5fd07e5f987a5dc807&chksm=fbd76e22cca0e734f4bc319ec3b908b9b3f200bda80e20b8f65836aac4445bc6a14675aa174e&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgxBP9s4glicBX52cplV822vrJCP5icouEwldVT8UCdUprEraay6j8oVWIejviaB99pb8Thjz2pargjA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACz3TmCVc2LJCHUaCb6jUZxHCrZjHHBM75Np39KBBia5dTIEAXZp1IDnJQ/640?wx_fmt=png)

文章作者：阿里妈妈 定向广告技术团队

内容来源：作者授权

**导读：**召回阶段作为互联网搜索、推荐、广告服务架构中的重要一环，是决定了系统整体服务质量的天花板。从召回算法技术发展的过程来看，大致经历了启发式规则方法及向量检索两代技术体系。为了突破召回阶段模型能力的限制，阿里妈妈定向广告团队于2017年提出了新一代的深度树匹配技术，使得任意复杂模型都能应用于召回阶段来做全库最优检索。近年来，这一技术框架围绕着检索技术本身进行了一系列的迭代，逐步建立了一套基于Learning to Retrieve思想的方法论，实现了对超大规模匹配问题中模型、索引、检索过程三者联合的最优理论建模。接下来，本文将对这一技术体系的最新进展做详细介绍。

**01**

**背景**

当前繁荣发展的互联网行业，不管是搜索、推荐还是广告业务，其本质都是实现了人和海量信息之间的高效连接，其核心是人和信息的匹配技术。其中，"人找信息"主要通过搜索技术来实现，而基于人和信息的关系实现"信息找人"，则主要依赖推荐及广告技术。阿里作为全球领先的电商平台，成功地将海量的用户及海量的商品通过技术连接在了一起。从匹配这一核心技术出发，搜索、推荐和广告看似业务形态不同，其实技术组成却是非常相通的：搜索可以认为是一种带query相关性约束的匹配，而广告则是叠加了广告主营销意愿 ( 价格 ) 约束的匹配。所以，匹配技术的创新对推动搜索、推荐和广告业务、技术的整体发展具有基础性的作用。

就匹配技术而言，其核心问题是如何从大规模的候选集中精准地找到最优质的结果，如用户可能最感兴趣的一系列商品等。当前，大规模匹配、推荐技术的发展，由于受到算力及固有系统架构的局限，往往都是对不同技术方案的拼装或是对系统局部模块的技术升级，而没有从本质上接近匹配技术的终极目标，即如何在全库范围内，使用精准的模型进行打分、排序，进而找到最优的匹配结果。阿里妈妈精准定向技术团队，面向这一本质问题进行了一些探索，以期能够对业界趋于固化的匹配技术进行新一轮突破，从而进一步推高匹配技术与相应业务的天花板。

面向匹配问题最终目标的技术探索，在具体实现层面面临着诸多挑战。首先，精准的打分模型单次计算量往往都不小。这一问题可以通过算力升级如使用GPU推理来解决，实现小规模候选集上可用。其次，全库候选集匹配寻优最大的挑战在于，与候选集规模相对应的计算次数爆炸。当候选集的规模扩展到亿级别时，即使是采用最简单的打分模型，其整体计算量及延时往往也是在线系统不能承受的。回顾业界的匹配技术发展脉络，大致都是在解决这两个主要的挑战。第一代基于统计的启发式规则方法 ( 代表算法Item-based Collaborative Filtering, Item-CF )，通过离线相似性计算、在线检索候选集限定，解决了整体的效率问题，但匹配结果质量也受到了影响；第二代基于内积模型的向量检索范式，通过内积建模与向量索引实现了高效的全库匹配，但这一范式同时也将打分模型局限在了内积形式上，限制了模型精度的进一步提升。

为了在全库检索的基础上进一步打开模型能力的天花板，2017年阿里妈妈精准定向广告业务团队在业界率先提出了新一代任意深度学习+树型全库检索算法 ( Tree-based Deep Model，TDM )，在大规模推荐问题上取得了显著的效果提升。TDM将大规模匹配问题拆解成模型、索引、检索三个模块，提出了树索引中的兴趣建模及检索范式，首次实现了可以使用任意复杂模型的全库近似最优检索。TDM技术体系在发展的过程中，逐渐形成了以Learning to Retrieve为核心思想的迭代方法论。围绕着"如何在索引结构中，通过构造样本来学习一个检索模型，使得基于该模型的检索能够找到最优的匹配结果"这一目标，整个深度树匹配技术的发展大致经历了如下图所示的三个阶段：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACznof6hVThRQJykFic7Qykld7ib0aYzPKiblTWibOiaG9CNkX23Ma3dqDibQ8w/640?wx_fmt=png)

TDM 1.0的诞生，有着一个明确的目标，即"如何突破向量检索模式的限制，使得任意复杂的深度学习模型，都能够在有限的资源和rt范围内进行近似的全库最优检索"。围绕这一目标，我们提出了使用树索引结构+兴趣最大堆建模来训练检索模型的方案。首先，如下图所示，对于全库商品，我们使用树结构对其进行索引构建，使得商品和树的叶节点形成一一对应关系。然后，为了能够有效地训练检索模型，使其能在树索引中进行精准的检索，我们根据兴趣最大堆建模，将检索目标 ( 目标商品，ITEM6 ) 在树索引中逐层上溯，来得到检索模型在树上各层的训练目标。基于这些目标训练的检索模型，能够在树上通过**Beam Search**来进行有效的近似最优检索。树结构天然的层次性及Beam Search提供的有效剪枝，使得模型形式不再受到检索模式和rt的限制，可以充分享受兴趣建模技术发展的红利，并提供更精准的召回。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzGNfHuOrQ09zMBfzxpf68LOTW2ACHa3TIyISiaRG5oia5Vky7gzic9uB4A/640?wx_fmt=png)

在TDM 1.0的研发过程中，我们发现了在树索引结构的设定下，树结构的质量对检索模型的训练乃至整个召回结果，都有着至关重要的影响。因此，如何通过学习得到高质量的检索结构，是TDM 2.0时代想要解决的主要问题。通过构造同时包含检索模型和检索结构的目标函数，并通过类似EM的算法来进行联合学习，TDM 2.0实现了统一目标下的模型、索引联合学习 ( Joint Optimization of Tree-based Index and Deep Model, JTM )，取得了推荐效果的进一步提升。在公开数据及上的实验表明，基于JTM算法的树检索召回，在召回率指标上甚至比相同复杂度模型直接进行全库排序要更优。

深度树匹配技术体系，通过将大规模匹配问题拆解成模型、索引、检索三者，首次实现了任意复杂模型的全库近似最优检索。阿里妈妈技术团队对这一技术体系进行了进一步的透视，发现除了模型和树索引的联合学习之外，对检索过程的联合同样有潜在的空间。基于这一出发点，最新的研究成果，也即第三代TDM技术BSAT ( Beam Search aware Training, BSAT ) 提出了一种针对检索过程联合建模的任意目标最优检索技术，相关技术沉淀的论文已被ICML 2020会议接收。

论文地址：

https://proceedings.icml.cc/static/paper\_files/icml/2020/2514-Paper.pdf

接下来让我们对该工作进行详细的解读。

**02**

**现状及缺陷**

TDM技术体系中，利用基于深度神经网络构造的**打分模型**度量用户-商品偏好关系，利用**树结构**建模商品集合中的层次化关系，并基于最大堆性质利用在树节点上的正样本上溯+同层随机负采样实现对数时间的计算复杂度；在测试时，TDM利用在树结构上的**Beam Search**进行局部检索及剪枝，以实现在对数时间内召回商品子集的目的。相比于限定在一个有限的历史兴趣范畴内推荐的第一代基于统计的启发式规则方法和第二代基于内积模型的向量检索方法，TDM使得引入更加先进的打分模型 ( 例如带有Attention结构的DIN模型 ) 在实际应用中变为可能，在多个业务场景也取得了显著的效果提升。围绕着这一思想，我们基于检索结构的学习做了进一步的技术创新，提出了树结构与检索模型联合优化技术JTM，使得超大规模候选集的检索结构能够和检索模型，进行统一的建模与学习。

这些技术创新主要围绕着模型及索引两大组件的设计展开，而忽视了检索组件的重要性。Beam Search作为一个贪心的局部检索方法，在树上检索时，只会保留并扩展打分较高的节点而剪枝打分较低的节点。一旦某些符合匹配目标的商品所对应的树上节点的祖先在某层检索中被剪枝掉，这样一个检索过程就会导致召回商品子集并非最优，我们在此统称这种情况为召回性能恶化。在理想情况下，TDM应当保证基于其打分模型及树结构的beam search不会导致召回性能恶化。然而，当前TDM框架将训练与测试视为两个不同的任务从而忽视了这一点，具体表现为：

* 打分模型的训练目标是估计树上节点用户兴趣概率，而非保证基于该打分的Beam Search能够实现召回商品**集合**在实际匹配目标 ( 如召回率 ) 上最优；
* 用于训练的树上节点时通过正样本上溯+同层随机负采样产生的，但用于测试的树上节点则是通过基于打分模型输出的Beam Search召回的，即训练所用树上节点分布和测试所用节点分布并不匹配。

因此，为了保证面向任意目标的最优检索召回，有必要将Beam Search建模至TDM的训练之中，搭建一整套"模型-索引-检索"联合优化的完整理论及实践框架。而实现该目的的第一步，就是针对于面向任意目标的最优检索召回的树模型，在理论上解决如何定义、是否存在、如何训练等一系列问题。

实际上，在探索过程中我们发现，训练阶段与测试阶段的不匹配问题并不仅仅存在于TDM，而是可以广泛存在于各种树模型，如在大规模多标签文本分类问题中常用的Probabilistic Label Tree ( PLT ) 模型等等。因此，我们从这一系列树模型中抽象出其数学本质，统一地回答这一系列关于定义、存在性及训练等理论问题，并提出了可用于实践的训练算法。在离线实验中我们发现，该算法可以在不对打分模型及树结构做任何修改的情况下，极大地提高召回的精度。

**2.1 现状**

首先，我们先简要介绍一些相关的数学符号。给定用户信息空间X及商品集合I={1,...,M} ( 其中M≫1表示商品数目 )，对于任意用户x∈X，其发生交互 ( 如点击、购买或收藏等等 ) 的商品构成I的一个子集，表示为Ix。为了表示方便，我们引入0/1编码向量y∈Y={0,1}M来表示交互商品子集 ( 其中yj=1表示用户x与商品j发生了交互，而yj=0则表示没有 )。由此，用户-商品关系可以表示为一个未知的概率分布p：X×Y→R+，而训练数据集Dtr及测试数据集Dte则可以视为p(x,y)的i.i.d.采样。

诸如TDM及PLT等树模型可以统一地表示为M(T,g)。其中，T表示用作索引的树结构：假定T是一棵高度为H的b叉树且Nh表示树上第h层的节点集合，相应地，树上所有节点集合可以表示为N=Uh=0HNh。我们将第0层节点视为根节点r(T) ( 即N0={r(T)} )，第H层节点NH视为叶子节点，每个叶子节点都与商品集合中的某个商品一一对应 ( 在数学上等价于存在双射π：NH→I )。对于树上任意节点n∈N，我们用p(n)表示其父节点，C(n)表示其子节点集合，L(n)表示以n为根节点的子树的叶子节点集合，而Path(n)表示树上从根节点r(T)到n路径上的所有节点集合。g：X×N→R表示相应的打分模型：对于任意用户信息x及任意树上节点n∈N，打分模型输出相应的分数，该分数在检索中，对于不同的树模型有着不同的用法。无论是TDM还是PLT，其训练目标函数都可以表示为：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzc6RRH9Mfh2cdClnZ6GdSudYJy4ZZ1icct6N847tcWub8PCiamuNQIVOQ/640?wx_fmt=png)

在该目标函数中：

* zn=I(∑n'∈L(n)yπ(n')≥1)表示树上节点n所对应的标签。该标签用于表示该节点子树中对应于用户交互商品的叶节点的存在性，反映了该节点上的用户兴趣，且由此可定义Sh+(x)={n：n∈Nh,zn=1} ( 在TDM中，该过程被称为正样本上溯 )。图1(a)给出了这种定义的一个例子；
* lBCE(z,g)=-zlog(1=exp(-g))-(1-z)log(1+exp(g))表示交叉熵损失函数，用于度量打分模型输出g(x,n)与实际节点用户兴趣分布p(zn|x)的差异；
* Sh(y)表示用于训练的树上第h层节点集合。在TDM中，Sh(y)=Sh+(x)∪Sh-(y)，其中Sh-(y)表示在第h层上随机无放回采样得到的节点集合。在PLT中，Sh(y)={n：n∈C(n'),n'∈Sh-1+(y)}。

在测试时，TDM及PLT等树模型都采用Beam Search的方式召回商品子集。假定检索宽度为k，Bh(x)表示给定用户信息x时Beam Search在第h层召回的节点结合， B~h(x)=Un'∈Bh-1(x)C(n')表示经由Bh-1(x)在第h层扩展得到的节点集合，则Beam Search具体过程可以表示为：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzUNiaveM18Yibzqnu4eCvjvXIaaT5SafluvEXzWAkNxLzYmUzSoNGTGiaA/640?wx_fmt=png)

在该式中，pg(zn=1|x)表示打分模型g(x,n)所对应的节点用户兴趣概率估计。TDM采用直接的方式构建该估计，即

**pg(zn=1|x)=1/(1+exp(-g(x,n)))**

而PLT采用层次化的方式构建该估计，即

**pg(zn=1|x)=∏n'∈Path(n)pg(zn'=1|zp(n')=1,x)**

其中pg(zn'=1|zp(n')=1,x)=1/(1+exp(-g(x,n')))。由此得到的召回商品集合表示为{π(n)：n∈BH(x)}，而召回质量可以用基于召回集合定义的Precision, Recall或广告场景的ECPM等评价指标度量。比如，Precision可以表示为P@k=Σn∈BH(x)yπ(n)/k。不失一般性，在接下来的推导中，我们将围绕Precision展开。

**2.2 缺陷：训练-测试不匹配问题**

从2.1节对树模型训练及测试阶段的介绍可以清晰地看到，训练所用的树上节点Sh(y)与测试所用的树上节点B~h(x)间的差别。以TDM为例，Sh(y)是基于真实交互商品子集y生成的，而B~h(x)则是基于用户信息x、上层召回集合Bh-1(x)和打分模型g(x,n)生成的。这种差别使得在Sh(y)上训练的最优打分模型g(x,n)在B~h(x)上并非最优。

另一方面，树上节点标签zn=I(Σn'∈L(n)yπ(n')≥1)的定义无法保证基于pg(zn=1|x)的Beam Search过程不出现召回性能恶化现象。这一点可以通过一个简单的合成数据实验看出：假设训练数据集为Dtr={y(i)}i=1N ( 忽略用户信息 )，边缘分布参数ηj=p(yj=1)为[0,1]上的均匀采样，且其真实概率分布为p(y)=∏j=1Mp(yj)，TDM的训练可以简化为对节点用户兴趣概率的直接估计，也即pg(zn=1)=Σi=1Nzn(i)/N。在测试阶段，其召回集合BH的性能可以用regret，即regp@k(M)=(Σj∈I(k)ηj-Σn∈BHηπ(n))/k表示，其中I(k)表示根据真实概率ηj的top-k商品。regret反映了召回子集与最优商品子集的差别：regp@k(M)越大，表明召回子集质量越差；当regp@k(M)=0时，表明召回子集最优。下表展示了该合成数据实验的结果，可以看到，召回性能恶化现象 ( regret不为零 ) 普遍存在于任意训练集大小N及检索宽度k下，即便是在理想情况下N=∞，该现象依然存在。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzlMq8ohflhl2YoTsv2UyWxeHGj9vVllUZffYxKec9Mzblc5M5wMTjNQ/640?wx_fmt=png)

表1：合成数据实验结果

**03**

**解决方案**

工欲善其事，必先利其器。为了解决因训练-检索不匹配导致的树模型召回性能恶化问题，我们首先从检索视角出发，构建了一整套最优树模型的理论框架，包括最优树模型的定义、存在性及训练损失函数等等。基于该理论框架，我们提出了面向Beam Search最优的树模型训练算法。

**3.1 面向Beam Search最优的树模型**

首先，我们需要回答的问题是，从检索视角出发，什么样的树模型才是最优的。一个非常直观的想法是，最优的树模型应当保证其Beam Search召回的商品子集在相应的评价指标下最优。以Precision为例，给定用户信息x，在该评价指标下最优的召回商品子集应当为用户商品分布p(y|x)中交互概率ηj(x)=p(yj=1|x)最高的商品子集。由此，我们最优树模型的定义，如下所示：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzVb7NVicKE2Ce6SNiaroGpKKbC4KY8XBzYzyFXJvDtQUXnibTPUDjjyljw/640?wx_fmt=png)

随后，我们需要回答的问题是，在该定义下，最优树模型是否存在？我们能够证明，对于任意概率分布p：X×Y→R+及树结构T，面向Beam Search最优的树模型总是存在的，如下所示：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzRUj5UwsBJjEAvOVLVicSqgCAy3cYzPBS1ibktW6WSFO8rY1nRAOxWCWg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzd57jEH5SyZlfftZFGdB9ONmuctzVIcjFEl5RBggAqy4uBpOsucDLRw/640?wx_fmt=png)

该定理表明，对于任意概率分布p：X×Y→R+及任意树结T，面向Beam Search最优的树模型总是存在的 ( 只要其打分模型满足相应的条件 )。因此，我们可以专注于打分模型的训练而暂时不考虑树结构的优化。

接下来，我们需要解答的问题是，如何得到最优的树模型？注意到，在最优树模型的定义中，判定条件存在等价表示，即

**Ep(x)[Σn∈BH(x)ηπ(n)(x)]=Ep(x)[Σj∈I(k)xηj(x)]**

由此，我们可以非常自然地得到一个树模型的最优性度量，即

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzYDS1Z4VJwGFRH7Dwic3oIibOOtzvaxqhjichibNzz5wDGPibNKGGY3HoD6w/640?wx_fmt=png)

然而，因为在得到BH(x)的过程中存在不可导的argTopk算子，所以该度量无法直接被用作损失函数来训练。为了训练最优树模型，我们需要引入能够保证其最优解即为最优树模型的损失函数作为替代，其定义如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzEib4DhiaZfaZ7RhzrGu4cESyh60sQbQyr29vFHnhqqzGK07uPmZUKKyg/640?wx_fmt=png)

校准性的定义在理论上为用于树模型训练的损失函数提供了判定标准：如果损失函数不符合校准性的定义，即便是在训练数据无穷的理想情况下，训练得到的树模型也不可能达到零regret，也就不可能是最优树模型。在2.2节的合成数据实验中，我们已经给出了一个TDM的训练损失函数不服从校准性的例子。由此反例可以判定，从检索的角度上看，由于训练损失函数的问题，TDM及PLT均非理论最优。

**3.2 最优树模型训练算法**

基于3.1节提出的理论基础，我们可以构造训练最优树模型的损失函数并设计相应的训练算法。首先，在最优树模型的存在性定理中，p\*(zn|x)实际上提供了一种不同于TDM及PLT的树上节点标签定义方式。为以示区别，我们称之为最优树上标签，并将其表示为zn\*，也即

**z****n****\*=y****π(n')****,n'∈argmax****n'∈L(n)****η****π(n')****(x)**

zn\*与zn的不同之处可以从图1(a)及图1(c)的对比看出：可以看到，根据zn\*的定义，树上节点标签等于其子树中边缘概率ηj(x)最高的商品标签yj，由此导致了用户实际交互商品 ( yj=1 ) 所对应的树上节点并不总是被当作正样本 ( zn\*=1 )，如节点1及节点6所示。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzxzMvwb0C8AjRKNJFNkY55gr88IiaoaD2rZCe7rkx9qc7dsem4Yu1Ngg/640?wx_fmt=png)

不同树上节点标签定义方式与Beam Search召回节点对比

在实际训练中，假设打分模型对应的模型参数为θ∈Θ，则打分模型、Beam Search在第h层扩展集合、打分模型及对应的节点用户兴趣概率估计可以表示为B~h(x;θ),gθ(x,n)及pgθ(zn=1|x)。根据最优树模型的存在性定理，我们可以很自然地得到符合top-k校准性定义的损失函数，即

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACz32NeY6PD82t1md7Ac31Ayc7ZhnuGnkKDHe6XK3iaTnibOicgPSRicrDxIQ/640?wx_fmt=png)

然而，zn\*依赖于在实际训练中未知的ηj(x)，因此该损失函数依旧不能用于训练。此外，待训练的模型参数θ出现在B~h(x;θ)，由于argTopk算子不可导，该损失函数依旧不可导。为此，我们提出两项近似：

基于当前树模型M(T,gθt)估计zn\*，即

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzHbjiayFS5hC9Wzk5hovNGiaNapUFqCY8rG0VR7fhicZSibuXQQhmhjqrgA/640?wx_fmt=png)

采用分部优化的方式，优化当前树模型M(T,gθt)时，固定z^n(x;θt)及B~h(x;θt)，单独优化gθ(x,n)中的模型参数。由此，我们得到最终的训练损失函数为：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzHyKIrjWpjIpYyNRiaVM7qwicbyYrXbpnqWZ4Bial6WXM2fwFpQaopbFUA/640?wx_fmt=png)

可以看到，该损失函数与TDM等树模型的区别有两处，分别为使用B~h(x;θt)而非Sh(y)生成用于训练的树上节点集合，以及使用z^n(x;θt)而非zn作为树上节点标签。这两处区别恰好分别对应于2.2节所分析的两处训练-测试不匹配问题。

最后，相应的训练算法如下所示：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzTXcv7gXSOjlKJdalOMBibnjrLNh80jTf5NbS8DVcOSEfdNcxUdTZGNg/640?wx_fmt=png)

尽管做出了多项近似，该损失函数在一定程度上依旧保留了最优树模型的特性：定义损失函数：

**Lθt\* (y,g(x);θ)=**

**ΣHh=1Σn∈Nhwn(x,y;θ****t****)lBCE(****z****^****n(x;θt),gθ(x,n)**

其中wn(x,y;θt)＞0。由此，可以看作是Lθt\* (y,g(x);θ)在满足wn=I(n∈UHh=1B~h(x;θt))的极限情况。可以证明，Lθt\* (y,g(x);θ)满足如下定理：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzWTw5O1icMparcVmke83WuxwOGYolWibrWaPKY9eBcaJ3wGEWyfx4iadxQ/640?wx_fmt=png)

该定理表明，引入对zn\*的估计z^n(x,θ)及引入分步优化并不会对M(T,gθt)的最优性造成影响。然而，使用B~h(x;θt)而非Nh会对最优性造成影响，原因在于wn(x,y;θt)=I(n∈B~h(x;θt))不符合wn(x,y;θt)＞0的要求。在实践中，我们可以通过引入随机采样等策略来避免该问题，但通过实验我们发现，这些策略引入与否对效果的影响并不显著。因此，在后续实验中我们均直接使用Lθt\* (y,g(x);θ)损失函数。

**04**

**实验**

**4.1 实验设置**

我们使用了Amazon Books和UserBehavior两个大型公开数据集来进行实验验证。Amazon Books是用户在Amazon上的行为记录，我们选择了其中最大的Books这一子类目。UserBehavior为淘宝全网行为子集，能在一定程度上对应线上真实效果。数据集的规模如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzA4iaapiaHOf9Y1NwurhIwEXGjVZCQQ4HmE95e0ib3J5QJh6j1mo82g33A/640?wx_fmt=png)

在实验中，我们比较了如下几种不同的模型算法，包括两种非树模型算法：

* Item-CF：基本的协同滤波算法，被广泛应用于个性化推荐任务中。
* YouTube product-DNN：应用于Youtube视频推荐的向量内积检索模型。以及四种树模型算法
* HSM：层次Softmax模型（依赖前提假设Σj=1Myj=1），被广泛应用于NLP领域，作为归一化概率计算的一种替代。
* PLT：HSM的多标签版本，被广泛应用于大规模多标签文本分类任务中。
* JTM：TDM的升级版本，通过打分模型及树结构的联合优化，在这两个数据集上取得了最优结果。
* OTM：本文中提出的最优树模型训练算法。同时，我们也比较了OTM的一个变种OTM (-OptEst)，即将算法中z^n(x;θ)的估计替换为TDM及PLT中所使用的zn。

对于所有的树模型，我们采用相同的树结构及相同的打分模型网络结构。具体来说，我们使用JTM算法训练得到的树结构作为所有树模型共享的树结构，使用三层全连接网络作为所有树模型共享的打分模型网络结构。在召回性能评价上，我们使用在测试集Dte上估计的Precision@m, Recall@m和F-measure@m作为评价指标，对任意(x,y)∈Dte，其定义如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzFVHXRYTqvfVqWzW5vU20T833FF5tZ5nwPDUOMtmXLh9091P9pK65JQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzlEjZom4Y4SmKCqViawyHgVMO1M6dhZGRUWGyO7qLTgRznsZXACv9SDQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzAfWm9khnxr17MEPHdJ9g89k0THqiascuNWItoV3S7TDulDp7KVbdfjg/640?wx_fmt=png)

其中，BH(m)(x)表示在Beam Search叶子层召回集合中的top-m(m≤k)节点所构成的集合。

**4.2 实验结果**

实验结果如下图所示，可以看到，OTM的召回性能比其他方法都要好。相比于之前最优的JTM，OTM在Amazon Books及UserBehavior数据集上分别取得了29.8%及6.3%的相对recall提升。通过比较OTM及OTM (-OptEst) 可以看到，OTM性能提升主要来源于基于Beam Search生成用于训练的树上节点。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzxtAeN5P5PvVdiam02EP30zz7EGPxWndhibhOFUNNFibGhIfh0gQ8Gnu7Q/640?wx_fmt=png)

Amazon Books数据集实验结果

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiay4wjicLyT4uKAtxMibmSACzBrjAN1eWHJuSvKaK8vaicxe3sBsYDnwrv3GOa2etqlUOic08UrvzNXicw/640?wx_fmt=png)

UserBehavior数据集实验结果

**05**

**总结与展望**

从面向检索最优的角度出发，在理论层面，我们对于最优树模型的定义、存在性及训练算法等问题做出了解答，构建了一整套泛用的理论框架，是对TDM技术体系的一次重大革新；在实践层面，我们提出了OTM这一有理论保障的训练算法，在离线实验中验证了该算法相比于其他算法在召回质量上的优势。从Matching阶段的技术需求上看，我们通过理论及实验证实了将检索组件引入模型训练中能够极大地提升召回性能，并从理论上阐述了面向任意目标进行最优集合召回的方案，这是迈向"模型-索引-检索"三大组件联合优化的重要一步。在未来，我们希望能够深化三者的联系，进一步推动该方向的发展，例如：将目前固定的无参数的Beam Search检索组件升级为可以end-to-end训练的参数化检索组件；将检索组件引入打分模型及树结构的联合训练等等方向，都有巨大的潜在价值等待挖掘。

**职位内推：**

阿里妈妈定向广告算法团队诚招大数据处理和机器学习算法方向的能人志士！有意者可发简历联系：

zhuhan.zh@alibaba-inc.com

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个三连击呗~~

---

**社群推荐：**

欢迎加入 DataFunTalk 广告算法交流群，跟同行零距离交流。如想进群，请识别下面的二维码，根据提示自主入群。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgnvG7iat6bFV7s6GLyLbNlj4BXEtoqQricmT6sm3lZemw1jV4wFsDySiaxZLImIHpTmibyjRKX6c1Rqw/640?wx_fmt=jpeg)

**文章推荐：**

[阿里妈妈深度树检索技术（TDM）及应用框架的探索实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247492994&idx=1&sn=6a787521ad85f37339f880bba0cc5d63&chksm=fbd757eecca0def8ac32a1c60f49ec933096833b5b55860074fd5d305499adc85d9f833fa333&scene=21#wechat_redirect)

[阿里妈妈新一代算法 JTM：如何优化大规模推荐？](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247495660&idx=1&sn=21a5b7e811d104162609d5fef993be79&chksm=fbd75d80cca0d496995ab1135ceb4734b90553a8fd82f4c970ed48212f3d0abd98f58e4e0864&scene=21#wechat_redirect)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近500位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，7万+精准粉丝。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaalkxbGB7NU2Paq7KM3MPhXtxKJy9M6Bs8EicpUtqCUe6fgfV4HSiaHs7Q/640?wx_fmt=jpeg)

🧐**分享、点赞、在看**，给个**三连击**呗！**👇**