---
title: '用于看一看list-wise推荐系统的HRL-Rec模型简述 | AAAI-2021'
company: 腾讯微信
tag: 推荐
date: 2021-06-13
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247543407&idx=2&sn=5ef8d7ada9e6060d0f88c303602b3db5&chksm=fbd79803cca01115ac9ea59e34afb653d3d9f1f7fd2857f77d6252cd0cd62aa1f47d7434a93e&scene=27
account: DataFunTalk
origin: xlsx
---
![](https://mmbiz.qpic.cn/mmbiz_gif/0jZVszE9o7aux1AibyQkWx4SticXfSUIn66vy2nVog74ltNCsxnXvhzhouAicf3EX6OvxicQ52ugIXQvxKDkDlAmTQ/640?wx_fmt=gif)

本文基于AAAI-2021论文《Hierarchical Reinforcement Learning for Integrated Recommendation》。

**导语**

真实世界的信息流推荐系统往往需要同时推荐不同类型的异质item（例如文章、视频、新闻、商品等），也拥有多种多样的信息源（例如不同垂类网站等）。一个综合推荐系统（integrated recommendation，例如微信看一看主推荐流）需要在一个主页面中混合推荐这些异质信息源的item。由于异质信息源的item特征不尽相同，彼此之间也难以比较，我们通常会使用不同的频道（channel）推荐不同异质信息源的item，以便于模型定制化和解耦。在这种情况下，用户在item级别的偏好和在channel级别的偏好都很重要。

在这篇工作中，我们提出一个分层强化学习模型Hierarchical reinforcement learning framework for integrated recommendation (HRL-Rec)用于看一看list-wise推荐系统（为每次用户请求推荐一个item list）。

HRL-Rec将推荐RL模型分为两层：low-level RL agent是一个频道选择器（channel selector），负责在list-wise推荐中生成一个channel序列；high-level RL agent是一个物品推荐器（item recommender），负责在channel selector生成的channel list的限制下推荐具体的item。我们设计了多样的损失函数帮助模型快速稳定地收敛，也融入了多种reward满足真实推荐系统的需求。我们进行了大量的离线、线上、消融、参数和稳定性实验，实验结果验证了我们HRL-Rec的有效性。HRL-Rec已经部署于微信看一看线上系统，服务海量用户。

**一、模型背景与简介**

真实推荐系统往往需要处理多种多样的多源异质数据（例如不同介质、不同信息源的数据）。综合推荐系统（integrated recommendation）需要同时推荐这些多源异质数据，来满足用户对于信息的个性化及多样化需求。下图1给出了一个经典综合推荐系统的示意图。在图中，不同信息源的信息往往会通过不同频道（channel）进行召回和粗排，筛选后的优质结果再混合在一起进行最后的排序。这样的设计解耦了不同数据源的数据处理和模型设计，能够增加系统的稳定性和灵活性。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2SIw3QelicYhTA8xzNSVWRFkZmFEg1uHst75VB3a2LP6mKQcDtqUdlKg/640?wx_fmt=png)

图1：一个真实的综合推荐系统示意图

一个好的综合推荐系统需要满足推荐准确性、多样性和系统稳定性，因此往往会面临着以下几个挑战：

（1）多源异质信息拥有的特征和排序策略不尽相同，融合部分需要仔细设计；

（2）在item级别的偏好之外，用户也会有在channel级别的偏好（例如A用户特别喜欢某数据源的信息）。这些偏好信息需要在排序模型中被强调；

（3）真实推荐系统需要关注系统稳定性，而一个channel上的扰动（例如数据丢失或者模型更新）可能会对整个系统造成严重影响。

目前的综合推荐系统并没有系统性地考虑解决这些问题的方法。

为了解决以上挑战，我们提出了一种新的分层强化学习模型Hierarchical reinforcement learning framework for integrated recommendation (HRL-Rec)，旨在同时建模用户的item-level和channel-level的偏好。

具体地，HRL-Rec建立于一个list-wise综合推荐系统上，包含有两个RL agents。其中，low-level RL agent是一个频道选择器（channel selector），负责在list-wise推荐中生成一个channel序列。这个序列被看做是一组channel constraints；high-level RL agent是一个物品推荐器（item recommender），负责在前述生成的channel constraints和多种rewards下推荐具体的item。我们综合考虑了两个部分RL agents的loss、supervised loss和similarity loss，在online exploration的用户真实反馈下对模型进行学习。这种分层强化学习的结构不仅能够提升模型推荐效果，也解耦了不同channel和item的偏好，提升了线上模型部署的稳定性和灵活性。

在实验部分，我们基于微信看一看系统进行了一系列离线和线上实验。HRL-Rec在所有指标上都取得了最好的效果。我们还在消融实验和模型稳定性实验部分证明了模型各个模块的有效性以及线上模型的稳定性。HRL-Rec已经部署于微信看一看线上系统，服务海量用户。这篇工作的贡献点总结如下：

1、我们系统性地提出并研究了综合推荐系统的任务和挑战，提出一个全新的HRL-Rec模型。据我们所知，这是第一篇融合分层强化学习和综合推荐任务的工作。

2、我们针对综合推荐任务设计了一种新的分层强化学习模型，融合了多种reward、损失函数和online exploration等策略，以保证模型的稳定快速收敛。这样的分层强化学习框架可以运用于大多数有多源信息的推荐系统，对于用户不同粒度的兴趣进行建模。

3、我们在离线和线上的多种实验上都取得了最好的实验结果，并且将HRL-Rec成功部署于微信看一看线上系统。

**二、模型结构**

我们提出的HRL-Rec示意图如下。HRL-Rec需要针对用户的每一个request（例如进入系统，刷新等），从多源异质信息源中提供一个推荐item列表，使用分层强化学习机制进行建模。图2给出了一个整体模型的示意图。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2BgJ44oZeKbCiaumlRkbBeJsUM3uCnpGwjCyAjIibrHZovict7Ubrb2jsg/640?wx_fmt=png)

图2：HRL-Rec的整体结构

具体地，在list的t位置，频道选择器（channel selector, LRA）首先基于list中已经推荐的前t-1个item信息（以及历史item信息）和user/context信息，推荐一个channel c\_t。然后，物品推荐器（item recommender, HRA）在频道c\_t的限制下，给出一个具体的item d\_t。HRL-Rec的low-level/high-level states, actions, rewards分别记录如下，其中LRA和HRA的action分别为生成一个channel或item。需要注意的是，我们在channel selector和item recommender中关注着不同维度（channel-level V.S. item level）的信息，这一点可以从state和reward的设计中看出。在item recommender中，我们综合考虑了点击次数、时长、多样性和新颖性四项指标设计reward，以提升用户多维度的体验。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2UxtfUE1Tw96wj3q88Z0lIQem7A7icFIzq1SLPAialmjA0qibiaicHxCBVDg/640?wx_fmt=png)

我们在channel selector和item recommender中使用了相似的网络结构，在一些特征上体现出channel和item的细微差别，基于DDPG进行训练。以channel selector为例，我们首先对每个历史item的feature fields进行特征交互：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2Gn216mQ7BNccgMngfibiaGVvQB2ud89uEMiaNaPoNXeqicZcj0usQjvcFQ/640?wx_fmt=png)

随后，这些序列化的历史item被输入进一个序列模型得到state的表示：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2icbfW7ACiaNgssWekHOW7zq95MApwsNsQvVhVjuS4hQr9TTBSZXzIAxQ/640?wx_fmt=png)

Actor和Critic则基于state输出结果：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2hl8A5jzquWiajebU8uRAsFiaMmiczcgKxsVfXeKsticSZ6bP2ujs9jhpPA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2xibcuU0LWhpDHKsZrfpTdgfO56AfN7U4jkiaevibV1yXYuTM1M5gTtj9w/640?wx_fmt=png)

我们基于online exploration进行有用户真实反馈的强化学习探索，按照DDPG的训练方式进行模型训练和更新。为了帮助模型在分层强化学习的框架下稳定收敛，我们还在DDPG的loss外增加了一个监督loss和相似度loss：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2Kw4VUAia7OFMvhHz0YqysCbjU9GzYdhP4RuboyAbrQnLfESfFnHJ4ibQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2dKLdQibuTFzeftcNMygPAuRkx1GhicubdC4Tne1HFwHKHwk58akYXfkA/640?wx_fmt=png)

前者直接使用交叉熵优化点击模型，后者拉近Actor生成的虚拟动作和实际item向量的距离，使得LRA和HRA能够生成尽可能真实的动作（即channel和item）。最终，我们得到以下loss：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2klQXFgKNPno7dUNzcNbvITJ4UBJxL7Rjgw41l32jSCFaZ58NHKIr5w/640?wx_fmt=png)

**三、实验结果**

我们在微信看一看的离线和在线数据上进行了丰富的实验，结果如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2k0SEBuEzbQX6aRg4OGH2D9CJXyLhJpC9sAxYfrzTkLyEOwUlia3Xv5A/640?wx_fmt=png)

图3：HRL-Rec离线实验

线上实验中，HRL-Rec模型在点击率和平均点击次数上都取得了显著提升。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2qvaUWWPHib3XuwepWTtwTTHKT9fBB8WvkWSKyTZ5NSrmxAZiaIJRZZdg/640?wx_fmt=png)

图4：HRL-Rec在微信看一看的线上实验

我们还进行了一系列消融实验和参数实验，证明模型各个模块的有效性以及参数的合理性：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2gGQaQOFWK4LdBqRva7hW42r0w1GWE4XDXIKUTlTFynBjcmvcM105ww/640?wx_fmt=png)

图5：HRL-Rec消融实验

最后，我们还对HRL-Rec模型在真实综合推荐系统上的稳定性进行了实验。多源异质信息在带来多样性的同时也不可避免地带来了不稳定性。一个数据源信息的剧变或者其对应channel的算法模型的异常，可能会给整个推荐系统都带来扰动，影响用户认知和体验（例如，一个综合推荐系统如果突然只能刷出视频，对用户体验和系统认知是一个极大的负面影响）。

我们认为一个真实综合推荐系统的各个channel的比例能够反映整个推荐系统的稳定性，每周同一天同一个时刻的不同channel比例应该是大致相似的。所以，我们采集了连续两周的baseline和HRL-Rec模型的不同channel比例并画成趋势图，观察其变化是否稳定。图6展示了这种变化抖动趋势，我们可以明显地看出HRL-Rec在两周的channel变化趋势几乎重合——这说明了HRL-Rec具有较好的系统稳定性，能够抓住用户长期的对于channel的整体偏好。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2ojKolunOvrflydKhgibawNKvY2RdK2xfACbl0bmFTFqJMNZdWYrhthA/640?wx_fmt=png)

图6：HRL-Rec系统稳定性实验结果

**四、总结**

在这篇工作中，我们系统性地研究了综合推荐系统这个在真实世界中广泛使用的场景，并提出一个新的基于分层强化学习的HRL-Rec框架，抓住用户不同粒度的偏好。模型在线上和离线使用中均取得最佳结果，并且消融实验、参数实验和系统稳定性实验也证明了模型的鲁棒性。HRL-Rec已经部署于微信看一看系统，服务海量用户。

我们认为，在综合推荐系统这个任务下，异质信息统一评价体系、异质信息多样性研究、产品规则和模型的融合等等课题，都是兼具工业实用价值和学术研究价值的方向，期待未来能有更多的相关工作。

\*论文作者是来自腾讯微信的ruobingxie, modriczhang, rysanwang, xiafengxia, goshawklin

**参考文献**

[1] Chen M, Beutel A, Covington P, et al. Top-k off-policy correction for a REINFORCE recommender system[C]//Proceedings of the Twelfth ACM International Conference on Web Search and Data Mining. 2019: 456-464.

 

[2] Chen X, Li S, Li H, et al. Generative adversarial user model for reinforcement learning based recommendation system[C]//International Conference on Machine Learning. PMLR, 2019: 1052-1061.

 

[3] Cheng H T, Koc L, Harmsen J, et al. Wide & deep learning for recommender systems[C]//Proceedings of the 1st workshop on deep learning for recommender systems. 2016: 7-10.

 

[4] Guo H, Tang R, Ye Y, et al. DeepFM: a factorization-machine based neural network for CTR prediction[J]. arXiv preprint arXiv:1703.04247, 2017.

 

[5] Hidasi B, Karatzoglou A, Baltrunas L, et al. Session-based recommendations with recurrent neural networks[J]. arXiv preprint arXiv:1511.06939, 2015.

 

[6] Ie E, Jain V, Wang J, et al. Reinforcement learning for slate-based recommender systems: A tractable decomposition and practical methodology[J]. arXiv preprint arXiv:1905.12767, 2019.

 

[7] Lillicrap T P, Hunt J J, Pritzel A, et al. Continuous control with deep reinforcement learning[J]. arXiv preprint arXiv:1509.02971, 2015.

 

[8] Mnih V, Badia A P, Mirza M, et al. Asynchronous methods for deep reinforcement learning[C]//International conference on machine learning. PMLR, 2016: 1928-1937.

 

[9] Song W, Shi C, Xiao Z, et al. Autoint: Automatic feature interaction learning via self-attentive neural networks[C]//Proceedings of the 28th ACM International Conference on Information and Knowledge Management. 2019: 1161-1170.

 

[10] Zhang J, Hao B, Chen B, et al. Hierarchical reinforcement learning for course recommendation in MOOCs[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2019, 33(01): 435-442.

 

[11] Zhao D, Zhang L, Zhang B, et al. MaHRL: Multi-goals Abstraction Based Deep Hierarchical Reinforcement Learning for Recommendations[C]//Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval. 2020: 871-880.

 

[12] Zhao X, Xia L, Zhang L, et al. Deep reinforcement learning for page-wise recommendations[C]//Proceedings of the 12th ACM Conference on Recommender Systems. 2018: 95-103.

**微信AI**

不描摹技术的酷炫，不依赖拟人的形态，微信AI是什么？是悄无声息却无处不在，是用技术创造更高效率，是更懂你。

微信AI关注语音识别与合成、自然语言处理、计算机视觉、工业级推荐系统等领域，成果对内应用于微信翻译、微信视频号、微信看一看等业务，对外服务王者荣耀、QQ音乐等产品。

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

---

**社群推荐：**

欢迎加入 **DataFunTalk 推荐算法**交流群，跟同行零距离交流。**识别二维码**，添加小助手微信，**入群。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgSAicVLFUvtl7hVcamwKKNAFE5CmDVqWZH8Z3Ba93W1fC0ZBrqPlttuUVGgCK22iaKVNdbnUdWibViaQ/640?wx_fmt=jpeg)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100+线下和100+线上沙龙、论坛及峰会，已邀请近1000位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章400+，百万+阅读，10万+精准粉丝。

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**