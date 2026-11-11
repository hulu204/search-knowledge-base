---
title: '针对多目标推荐任务，微信看一看用PAPERec框架逼近帕累托最优'
company: 腾讯微信
tag: 多目标&多任务
date: 2021-06-15
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247543460&idx=2&sn=833b99ad67ff1914b94453aaa1e752c8&chksm=fbd798c8cca011de8743b244e2a39159e26691a963d6a046280b6dbdd6bd7e6f38ae4df53e33&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_gif/0jZVszE9o7aux1AibyQkWx4SticXfSUIn66vy2nVog74ltNCsxnXvhzhouAicf3EX6OvxicQ52ugIXQvxKDkDlAmTQ/640?wx_fmt=gif)

本文基于WWW-2021论文《Personalized Approximate Pareto-Efficient Recommendation》。

**导语**

真实推荐系统往往会同时关注多种目标，例如点击率、时长、多样性等。多目标优化推荐（multi-objective recommendation (MOR)）被广泛研究以解决这类问题。帕累托最优（Pareto efficiency或Pareto Optimality）代表了一种多目标优化任务中的理想状态。在帕累托最优下，多目标中的任何一个目标都不可能在不损害其他目标的前提下进行优化。帕累托优化的标量法（scalarization methods）将模型的多目标损失加权成一个整体损失函数，通过模型更新时同步调整权值实现帕累托优化，目前已运用于多目标推荐中。然而，这些工作往往对所有用户使用同一套目标权值（objective weights），没有考虑到用户对于目标的个性化偏好。

为了实现多目标推荐系统中用户的目标级别的个性化，我们提出了一个新的Personalized Approximate Pareto-Efficient Recommendation (PAPERec)框架，基于Pareto-oriented reinforcement learning模块生成用户的个性化objective weights，帮助模型近似地逼近帕累托最优。我们在微信看一看系统上部署了PAPERec模型，在离线和线上实验的多个目标上均取得最优结果。

**一、模型背景与简介**

真实世界的推荐系统往往需要同时关注多个目标（例如点击率、时长、多样性、用户留存等），以获得更好的用户口碑和体验。在不同的推荐场景下，系统对于不同目标的关注度也不尽相同。对于新闻推荐系统，时新性往往是系统关注重点，而对于视频推荐系统，用户观看时长又是另一种重要的指标。多目标优化推荐（multi-objective recommendation (MOR)）主要着眼于解决推荐系统多目标优化的问题。不同的目标之间往往互有冲突，如何同时优化所有目标成为多目标推荐系统的主要挑战。

近期，帕累托最优（Pareto efficiency）的概率被引入多目标推荐系统中，并取得了良好结果。帕累托最优代表了一种多目标优化任务中的理想状态。在帕累托最优下，多目标中的任何一个目标都不可能在不损害其他目标的前提下进行优化。在帕累托优化模型中，一个经典的方法是基于scalarization method的Multiple gradient descent algorithm (MGDA)模型[1]。scalarization通过一种线性加权的方式，将模型的多目标损失联合成一个整体损失函数。而MGDA算法使用KKT条件进行多目标优化，提出了Pareto stationary point并证明它是Pareto efficiency的必要条件，然后通过调整objective weights优化Pareto stationary point中的最小化问题，保证模型梯度下降方向是朝着帕累托最优的方向。但是，目前绝大多数推荐中的帕累托多目标优化算法使用的是一套所有用户共用的objective weights，忽略了用户对于不同目标的不同偏好度。如下图所示，用户A更加关注视频的时长指标，而用户B更加关注碎片化阅读的点击指标，我们想要在帕累托优化中考虑用户的目标级别的个性化需求，提供更加优质的个性化推荐结果。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2oMH0bDVptIJ0vibI7Hbx1PS8FuQw3YDOysouslfjfYrT859BXrcEeWQ/640?wx_fmt=png)

图1：用户的目标级别的个性化偏好示例

因此，我们提出了一种个性化近似帕累托最优的多目标推荐框架Personalized Approximate Pareto-Efficient Recommendation (PAPERec)。PAPERec在优化中近似逼近帕累托最优，基于Pareto-oriented reinforcement learning模块生成用户的个性化objective weights，保证了不同用户拥有不同的目标权值。我们基于MGDA中证明的Pareto stationary point相关结论，直接使用其最小化问题——多目标梯度导数加权和的二范数——作为Pareto-oriented RL的reward，用以迭代更新生成objective weights的相关参数。我们将PAPERec部署在微信看一看推荐系统的list-wise推荐模块，在离线和线上实验的多个目标上均取得最优结果。这篇工作的贡献点主要有以下三点：

1、我们提出一种新的个性化近似帕累托最优的多目标推荐框架PAPERec。据我们所知，这是第一个考虑目标权值个性化的帕累托最优推荐模型；

2、我们设计了一种Pareto-oriented RL模块，在真实list-wise推荐系统中通过控制个性化objective weights近似逼近帕累托最优；

3、模型通过大量离线和线上实验，证明了PAPERec的有效性。目前PAPERec正部署于微信看一看系统，服务着海量用户。

**二、背景知识**

在介绍PAPERec模型之前，我们先简单回顾一下Pareto efficiency相关的经典定义（更多细节请参考[1][2]）：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2ruh7Q7G1T6tARYZaw8weXrjBDeIib3Mb4hPiaNWhJxIqgFOvIDdJNIicw/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2LeStYRqpwn8l2a8Wj5x8PRxybNzKlrJmkZiaSqWFUTn6vBL6BCChCGg/640?wx_fmt=png)

我们基于图2给出一个帕累托优化的直观定义。我们可以说在CTR和Dwell time两个目标下，A dominates C, B dominates C，但是A和B之间没有dominate的关系。这种情况下，帕累托最优希望模型能够从C点开始优化，寻找到帕累托平面上的点（A或者B），使得空间中没有其它situation能够dominate现在的situation。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2oJNszGHubzRf9vZfhRWV7VT19kuLcAQ6OWRpDy6Y73pKRBh8TzDWXw/640?wx_fmt=png)

图2：帕累托最优示例图

在帕累托最优中，scalarization是一个常见的方法。它通过一种线性加权的方式，将模型的多目标损失联合成一个整体损失，具体如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2dpXCk5ib9HaLCNppLmkUznQgUN0QfeYZbaI8UjqXotFRjoHbYkMbUxg/640?wx_fmt=png)

需要注意这里的objective weight并不是个性化的。Scalarization方法能够根据weight的变化，使得模型朝向帕累托平面进行优化。MGDA算法提出了Pareto stationary point的概念，并证明它是Pareto efficiency的必要条件（证明详情请参考[1]）。寻找Pareto stationary point即可转化为下列优化问题：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2U7Aee6StOAc2IDeeZHWsicoC0unj1IGksYdeibZh5ibPwVuPx3EfiaTHnQ/640?wx_fmt=png)

MGDA算法证明了：（1）当这个最小化问题的解是0时，这种situation就达到了Pareto stationary point；或者（2）这个最小化问题的解得到的objective weights给出了一个能够同时优化所有目标的帕累托优化方向（详细证明请参考论文[1][2]）。我们需要利用这一点，构建PAPERec的核心个性化objective weights的模块，实现个性化近似帕累托算法。

**三、具体模型**

不失一般性，我们将PAPERec部署在微信看一看list-wise RL推荐模型上（模型结构和AAAI-2021论文[5]类似），同时关注点击率（CTR）和时长（Dwell time, DT）两个目标。为了实现个性化objective weights，我们基于scalarization设置模型的损失函数如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2n1raVdP9MUyoYfGuQvVeKqLj3xmYAIk2smJBVpQHhFajWpJic7T9afw/640?wx_fmt=png)

需要注意的是，我们在这里设置了个性化的objective weights，由一个Pareto-oriented RL模块控制生成不同user-item pair的objective weights。

具体地，PAPERec包括了两个单目标模型（single-objective model），分别优化CTR和DT，以及一个Pareto-oriented RL模块生成两者的objective weights。整体算法的伪代码如下：在每个batch下，

（1）single-objective models模块计算各个单目标的loss；

（2）基于当前各个单目标的loss，计算Pareto-oriented RL的loss，并以此更新Pareto-oriented RL；

（3）基于更新后的Pareto-oriented RL，计算新的objective weights；

（4）基于新的objective weights更新所有single-objective models。

PAPERec通过这种迭代式地更新，使得模型近似逼近帕累托最优。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2bCRLQ7wAAjNZeic7rr8tMC0Maibclhdso9F0Wk0jdRiapxQZvVx9FMQqg/640?wx_fmt=png)

Pareto-oriented RL模块是PAPERec的核心模块，负责生成个性化的objective weights。在Pareto-oriented RL模块中，我们设置state，action，reward如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h28IhMWGWJEVEtgL5ApClfNgjUiaEmrfrvajSpXY56QGgBbRKU5c2Ed2Q/640?wx_fmt=png)

其中，state表示当前list的状态（包括list中已经推荐的item的属性和objective weights），action表示产生不同的objective weights这个动作。我们直接基于Pareto stationary point的最小化问题设置了如下reward：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h28Qz75mNbo1ktsX7b8puVySLZiaeUiaVb6Zhz3Sq6tcUGjCVHDIZnhyYw/640?wx_fmt=png)

Pareto-oriented RL的优化目标通过reward，转化为最小化list内的多目标梯度导数加权和的二范数。在训练中，如果reward=0时，当前状态为帕累托最优；在其它情况下，objective weights会朝向reward最大（即二范数最小）的方向改变，慢慢接近最小化二范数的解——而这种最小化问题的解被证明是一个符合帕累托优化、能同时提升所有目标的方向。综上所述，在Pareto-oriented RL的reward的指导下，模型能够在理想状态下基于个性化的objective weights，近似朝向帕累托最优的方向优化。

我们在PAPERec中使用了DDPG进行RL的训练。模型使用Transformer和list-wise GRU等对特征交互和序列特征进行建模，具体的模型结构如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2uMeLREQm5oXJud5vDRr3yASYpcxC7AOrDviaQJ1ia9ibOpiakFh6ic3QP8g/640?wx_fmt=png)

图3：Pareto-oriented RL模型结构

我们使用了相同结构的feature encoder建立CTR导向和DT导向的单目标模型，整体的loss function融合了RL和单目标模型两个部分：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2zqia8M7lSI9RFoXH4ZZ7fKJZ7903iaOktSmPZHEdMTlwwEUKUsUgicAyg/640?wx_fmt=png)

**四、实验结果**

我们在微信看一看真实系统上部署了PAPERec模型，并且进行了离线和线上多个实验，其中离线实验的CTR和DT结果如下：

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2a92thE6Yia1kly9riczaiabOMvyFUZGLw47mlLwHMibF9HicrolBUiaL2OYw/640?wx_fmt=png)

图4：离线实验CTR和DT多目标预测结果

通过下图能够更加清楚看到不同模型之间是否存在domination的关系，可以看到PAPERec取得了最好的DT结果，并且综合结果最佳。

![](https://mmbiz.qpic.cn/mmbiz_png/0jZVszE9o7bpVHlAYaadB2jsdo7lh1h2YVvKeafwic2ko3Cz38hOJ2pukI5u1f8VicjllBNicmRFTdy8Aicl0NNZfw/640?wx_fmt=png)

图5：不同模型的多目标结果二维图

最后，我们还在objective-level personalization上进行了定量的研究。我们发现，Top 10% CTR weight的user（可以看做是模型认为这些user更关注CTR）拥有更高的CTR值。在item维度，Top 10% DT weight的item（可以看做是模型认为这些item更加关注时长）拥有更高的DT per click值。另外，我们也探索了item的不同类别对个性化objective weights的影响。我们发现video类别的item在top 10% DT weight中比top 10% CTR weight中更多，这说明video类的item被模型认为时长比点击率更重要（这也符合我们的直觉）——而article和news类别的item则刚刚相反。这一系列定量实验证明了我们的PAPERec模型能够良好地抓住objective-level personalization信息。

**五、总结**

本文针对多目标推荐任务，提出了一种个性化近似帕累托最优算法PAPERec。模型能够产生个性化的objective weights，并基于Pareto-oriented RL定制的reward函数，通过指导objective weights的变化，引导所有单目标模型的优化，使得模型能够近似朝着帕累托最优的方向优化。现在，PAPERec模型已经部署于微信看一看的线上系统，服务海量用户的个性化推荐需求。目前我们初步探索了基于帕累托最优的多目标推荐系统。我们认为基于帕累托最优的多目标推荐系统同时具有很强的学术研究和工业实用价值，值得进一步探索。

\*论文作者是来自腾讯微信的ruobingxie, yanleiliu, modriczhang, rysanwang, xiafengxia, goshawklin

**参考文献**

[1] Désidéri J A. Multiple-gradient descent algorithm (MGDA) for multiobjective optimization[J]. Comptes Rendus Mathematique, 2012, 350(5-6): 313-318.

 

[2] Sener O, Koltun V. Multi-task learning as multi-objective optimization[C]. NeurIPS, 2018.

 

[3] Lin X, Chen H, Pei C, et al. A pareto-efficient algorithm for multiple objective optimization in e-commerce recommendation[C]//Proceedings of the 13th ACM Conference on Recommender Systems. 2019: 20-28.

 

[4] Xie R, Ling C, Wang Y, et al. Deep Feedback Network for Recommendation[C]. Proceedings of IJCAI-PRICAI, 2020.

 

[5] Ruobing Xie\*, Shaoliang Zhang\*, Rui Wang, Feng Xia and Leyu Lin. Hierarchical Reinforcement Learning for Integrated Recommendation[C]. AAAI, 2021.

 

[6] Guo, Huifeng, et al. "DeepFM: a factorization-machine based neural network for CTR prediction." Proceedings of IJCAI, 2017.

 

[7] Song, Weiping, et al. "Autoint: Automatic feature interaction learning via self-attentive neural networks." Proceedings of the 28th ACM International Conference on Information and Knowledge Management. 2019.

 

[8] Ribeiro M T, Ziviani N, Moura E S D, et al. Multiobjective pareto-efficient approaches for recommender systems[J]. ACM Transactions on Intelligent Systems and Technology (TIST), 2014, 5(4): 1-20.

 

[9] Cheng W, Shen Y, Huang L. Adaptive factorization network: Learning adaptive-order feature interactions[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2020, 34(04): 3609-3616.

 

[10] Xiao L, Min Z, Yongfeng Z, et al. Fairness-aware group recommendation with pareto-efficiency[C]//Proceedings of the Eleventh ACM Conference on Recommender Systems. 2017: 107-115.

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