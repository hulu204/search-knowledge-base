---
title: 'Bandit算法在携程推荐系统中的应用与实践'
company: 携程
tag: 推荐
date: 2020-04-19
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247499139&idx=1&sn=c187e0108e9bd55b69e48d0c8de1887d&chksm=fbd74fefcca0c6f9290da7221b0d4b02a1d6a84913cf4950052b2050cd73e52b906d489f824e&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaayhj1qJTEN7OS1YYJvG7eAjR7GveSwjSTQ0GOlHN3yB2IVRUe6Mvj3g/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMAhhvMN31HN28HYTibibEdNYx16a3k8v04rtla5dj1icE4fliconjCEC07g/640?wx_fmt=png)

文章作者：携程技术团队

编辑整理：Hoh

内容来源：《携程人工智能实践》

出品平台：DataFun

注：转载请在后台留言“转载”。

**导读：**携程作为全球领先的 OTA 服务平台，为用户提供诸多推荐服务。下面我们介绍几个在实际推荐场景中面临的问题：

* 假设一个用户对不同类别的内容感兴趣程度不同，那么推荐系统初次遇到这个用户时，如何快速地知道他对每类内容的感兴趣程度呢？
* 假设我们有若干广告库存，如何知道给每个用户展示哪个广告能获得最大的点击收益？如果每次都推荐效果最好的广告，那么新广告何时才有出头之日呢？
* 如果只推荐已知用户感兴趣的物品，会导致马太效应。例如，在实际的场景中，部分优质物品由于初始推荐策略 ( 如热门推荐策略等 ) 被推荐的次数变多，这导致用户购买或点击的次数较多，形成的用户购买轨迹也较多。这种策略会导致头部物品得到大量曝光，而中长尾物品的曝光次数很少。如何才能科学地为用户推荐一些新鲜的物品来平衡系统的准确性和多样性呢？

Bandit 算法源于赌博学，一个赌徒去摇老虎机，一个老虎机共有 n 个外表一模一样的臂，每个臂的中奖概率为 Pi，他不知道每个臂中奖的概率分布，那么每次选择哪个臂可以做到收益最大化呢？这就是多臂赌博机 ( Multi-armed Bandit，MAB ) 问题。

将 MAB 问题进行抽象，假设老虎机共有 n 个臂，每个臂的中奖概率为 Pi，用户可以对每个臂进行尝试，每次尝试若成功则中奖概率为 1，若失败则中奖概率为 0。用户不知道每个臂的中奖概率，需要调整尝试策略，最终找到中奖概率最大的臂。

**Bandit 算法能较好地平衡探索和利用问题 ( E&E 问题 )**，无须事先积累大量数据就能**较好地处理冷启动问题，避免**根据直接收益/展现实现权重计算而产生的**马太效应**，避免多数长尾、新品资源没有任何展示机会。利用 Bandit 算法设计的推荐算法可以较好地解决上述问题。

***01***

## ********▬********

**Context-free Bandit 算法**

**1. 置信上限 ( Upper Confifidence Bound，UCB )**

Context-free Bandit 算法的思想在于采用一种乐观的态度，根据每个臂预期回报的不确定性的上界值进行选择，确定每次选出的臂。每个臂尝试的次数越多，预期回报的置信区间越窄；每个臂尝试的次数越少，预期回报的置信区间越宽。对于某个臂 ai，计算相应的预期回报分数，即：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEM1YLjpyAKuok9ZVd21U5T2c3cSGLPR73JpI0ghyFMnw1UibTC2UQfFIw/640?wx_fmt=png)

其中第一项：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMUSHgqKJC6hSK0OQ60rp2um4hL5FicrJ710ciaVasNBHSAQDxt4jbdQtA/640?wx_fmt=png)

为第 i 个臂到当前时刻 t 的平均回报，称为利用项 ( Exploitation Term )；后一项为置信度，即对第一项的回报估计的确信程度，称为探索项 ( Exploration Term )，rs为在 s 时刻观察到的收益，ni,t为第 i 个臂到当前时刻 t 的选择次数，n 为总选择次数。平衡选择已有较好表现的物品和具有潜在贡献的物品。如果物品的置信区间很宽 ( 被选次数很少，且不确定 )，那么它会倾向于被多次选择，即探索，这是算法冒风险的部分。如果物品的置信区间很窄 ( 备选次数很多，且能确定其好坏 )，那么均值大的倾向于被多次选择，即利用，这是算法保守稳妥的部分。

**2. 汤姆森取样 ( Thompson Sampling )**

汤姆森取样是一种通过贝叶斯后验采样 ( Bayesian Posterior Sampling ) 进行探索与利用的方法。采用贝叶斯思想，对奖赏分布的参数假设一个先验分布，根据观测到的奖赏更新后验分布，根据后验分布选择臂。

对于臂的奖赏服从伯努力分布，中奖概率 ( 被点击的概率 ) 即平均奖赏 θk∈[0,1]。假设第 k 个臂的奖赏分布固定但未知，即参数 θk 未知。在 Bernoulli Bandit 问题中，采用 Beta 分布对第 k 个臂的中奖概率建模，因为 Beta 分布是二项分布的共轭分布。如果先验分布为 Beta(α,β)，在观测到伯努力二元选择 ( Bernoulli Trial ) 后，后验分布变为 Beta(α+1,β) 或 Beta(α,β+1)。

* 如果候选物品被选中的次数很多，那么 Beta 分布随着 αk+βk的增大会变得更加集中，即这个候选物品的收益已经确定，用它产生的随机数基本在分布的中心位置附近，且接近这个分布的平均收益。
* 如果一个候选物品的 α+β 很大，且 α/(α+β) 也很大，那么该候选物品是一个好的候选项，其平均收益也很好。
* 如果一个候选物品的 α+β 很小，且分布很宽，即没有给予充分的探索次数，无法确定好坏，那么这个较宽的分布有可能得到一个较大的随机数，在排序时被优先输出，并用给予次数进行探索。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMD8Bb4ahNmXqG8jqsKNfbaszWOW5VFiasmTqnCsfre0SreiboffDgEiaPA/640?wx_fmt=png)

***02***

## ********▬********

**Contextual Bandit 算法**

Context-free Bandit 算法没有充分利用实时推荐的上下文特征 ( 用户偏好特征、场景特征等 )，在某一时刻对所有用户展示的物品 ( 本文案例中指创意文案 ) 是相同的。事实上，针对同一个文案，不同的用户在不同的情境下的接受程度是不同的。而 Contextual Bandit 算法充分利用了这些特征。

每个臂包含特定的随时间变化的上下文特征 **x**t，并且其回报 **r**t 和上下文特征 **x**t 直接相关，即存在一个函数 f，使得 **r**t=f(**x**t)，其中 **x**t 为实际应用中抽象出的辅助选择每个臂的特征。根据不同的互联网推荐系统场景可以产生不同的用户特征和物品特征，不同的有关函数 f 的假设会得到不同的模型，选择最大化期望回报策略：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMUg5qwdEwweV0NbQFcWefIyyCbeDiaYu88P7IsbKtBWPbpJS7VJV3FcA/640?wx_fmt=png)

其中 Ex,r 为期望。对应 Context-free 的 Thompson Sampling 算法，算法3给出一种相应的 contextual bandit 算法：Linear Thompson Sampling 算法。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMnyga3t8UhzKsnjA7H7wnEth57IA8ZSsuOvPy1vKdfFicAfNXZ2Wt79A/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMFzreuPOAEmoeaJntJJTtcibfZt2UtNhAzLKlsMfIo84o4umO1ibtcycQ/640?wx_fmt=png)

***03***

## ********▬********

**场景应用**

**1. 文案创意选择**

传统的 Test-rollout 策略分为 Testing Period 和 Post-testing Period，它在给定的测试周期内分配等量流量，挑选出指标表现最优的文案并切换全流量。但其存在下述缺陷。

* 在初始阶段，一部分用户会收到质量较低 ( 表现为 CTR 较低 ) 的文案，这会损害用户体验的效果，也会影响用户的参与度。
* 文案的表现会随着场景信息 ( 时间、地点等 ) 的变化而变化，在测试周期内得到的结论不一定适用于文案的整个生命周期。

编辑人工撰写的文案的质量有一定保证，利用 E&E 算法进行探索时不会严重地影响用户体验而导致用户流失。我们可以将文案模板优化建模为多臂 Bandit 问题，并引入 Batched Thompson Sampling ( 成批的汤姆森采样 ) 优化用户体验。在传统的 Thompson Sampling 中，只要接收到用户反馈就会更新模型参数。在实际应用中，高频的模型更新会给系统带来严重的计算负担，同时由于日志系统存在延迟问题而无法确保收到实时的点击、转化等数据，因此更理想的情况是处理一定时间段内批量的用户反馈。相关研究表明，Thompson Sampling 通过对反馈引入随机性，对数据延迟反馈和批量数据反馈相比其他 Bandit 算法更加准确。例如，UCB 是一种确定性算法，虽然可以处理较短的延迟，但是当延迟增大时，模型性能会急剧下降。Beta 分布的采样利用：

org.apache.commons.math3.distribution.BetaDistribution 

包快速实现。系统整体处理流程如图 1 所示。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMt1ibK5bFwh1vbmV8mHOd9G77MbHGrFpLaPiciavNNvhN1kw41NGCef3Pg/640?wx_fmt=png)

图 1 系统整体处理流程

**2. 更新机制**

Thompson Sampling 假设第 i 个臂拥有先验 Beta(1,1)，Beta(1,1) 是 (0,1) 的均匀分布。采用 Batched Thompson Sampling，每个臂的 Beta 分布只在每批次的结尾更新。

对于传统的 Bernoulli Bandits 的 Thompson Sampling 算法，如果观测到点击行为，被选择臂的 Beta(α,β) 更新为 Beta(α+1,β)，否则更新为 Beta(α,β+1)。

对于 Batched Thompson Sampling，采用两种更新机制：求和更新与归一化更新。

对于第 t 个批次内第 k 个臂的 Beta 分布为 Beta(αkt,βkt)；Skt 和 Fkt分别表示第 t 个批次中第 k 个臂的点击次数和非点击次数；Mt 表示总的曝光次数，K 表示臂的总数。

求和更新公式如下：

αkt+1=αkt+Skt

βkt+1=βkt+Fkt

归一化更新公式如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMpYHQAClb0ic4bZayNUEke4spqHEOf1psnhLI9Bs8JibrW8GXXNSgzeMA/640?wx_fmt=png)

Mt/K 的参数更新策略可以解决在每个数据流批次内不同臂之间的不平衡流量的分配问题。如果第 k 个臂在每个批次内有较少的点击次数，可能是由于 θk较小，或者分配到该臂的流量不足以产生足够的点击次数，这会降低算法对于噪声的容忍度。较小的 K 会放大潜在噪声。实践表明，数据噪声 ( Data Noise ) 相较于不平衡流量分配的副作用，对算法表现有更大的影响。因此，我们采用求和更新公式。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMpjB6qxlwEwN511fI048U2sjibfsZkcFkBSZn6k9vbaJIf0DygKsAGvA/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgicbGuYUNeLBgsiaSj2KhobC8FKM6vqRia5ojicCa0hdN4DydYTiaZ9eCSwa0fUC8AlapM2lsCjOaCibqA/640?wx_fmt=png)

**3. 采集无偏的数据**

在推荐系统中经常面临的一个问题是用户对根据某些策略推荐的一部分物品感兴趣并做出反馈，但是还有更多的物品实际上没有展示机会。在理想状态下，我们希望用户遍历推荐系统准备的产品列表全集。

基于这些用户交互数据，后续采用传统的有监督模型训练并上线个性化排序，实际上学习得到的排序函数是有偏的，会给推荐系统引入较大的偏置。如何尽可能地收集无偏的用户交互数据呢？传统的做法是从物料池中随机均匀采样并展示。但是这种做法会影响用户体验，降低用户的参与度，导致需要更长的时间来收集充分的用户行为反馈。我们引入一种用户友好的无偏数据收集框架来改进传统的 E&E 算法，用于解决该问题。

现有的 E&E 算法本质上不是为了消除偏差，而是最大化期望回报。一旦在探索中从未得到展示机会的物品对于某个指标 ( 如 CTR ) 的贡献被充分地利用，E&E 算法就会收敛于产生最大回报的物品。

在标准的 K-armed Bernoulli Bandit 问题中，每一轮只有一个物品会被选择。一种常见的做法是将 Item-wise Bernoulli Bandit 扩展为 List-wise Bernoulli Bandit，并将所有物品的排列视为一个臂。一种直观的做法是：从每个臂的后验分布进行采样，并以确定性的方式从中选择 top N 的臂，如算法5所示。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMoSZ3Oe5cpeiblvp8CKduvFnBxk5fJdBQoFZerugOTxb3HmGibOibkJeVg/640?wx_fmt=png)

相比于传统的 bandit 算法在每一轮确定性地选择最优的臂 ( 在这里表示为一个排序的 top N 列表 )，改为由每个 item 的参数构成的多项分布随机选择这个臂。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMcRnoE2RNgPb37mEBnMnXGiaFYib7pzm4kdtnlbmcdC4KoamYba0epItw/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEM4hcR6OzkzK3SpQLnaQDRibtr7CQoVJuDTaXZK5Gh6xQq1IfyfGyCQbw/640?wx_fmt=png)

更改 E&E 算法使得高质量的内容和低质量的内容能够相伴产生，并且高质量的内容排在前面的概率更高，使用户体验的损失可控。

**4. 策略评估**

Bandit 算法离线评估方法如下：

RA(T)=G\*(T)-GA(T)

在探索过程中，由于选择一些次优的臂，因此会增大短期的累积遗憾 ( Regret )。但是对于每个臂奖赏的评估，获取臂的平均奖赏信息可以优化算法，从而减少长期 Regret。

随着迭代轮次增大而减少 Regret，即确保 RA(T)/T 随着 T 增大而逐步减小，数学表达式如下：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMFl9ckiagNxZWajicuVvA0lm9Nv9ZnXBiaauf1uicAxTVQmBRbtKJoBiaPlQ/640?wx_fmt=png)

在理想情况下，我们进行分桶实验，划分一小部分线上真实流量评估各类 Bandit 算法，这对于 Bandit 算法的离线评估十分重要。用于离线评估的数据格式为：用户信息、展示的物品、用户对该物品的反馈 ( 点击或不点击 )，这些数据是由其他推荐策略收集到的日志信息。当 Bandit 算法的推荐与离线数据为不同的物品时，则无法获取用户反馈。这种 "Partial-label" 的天然特性用来评估 Bandit 算法与有监督算法之间的主要区别。

* 使用历史日志数据 D={(x,a,ra)}，要求每个臂以 1/K 概率被选择，满足独立同分布。
* 奖赏的反事实性：当 Bandit 算法推选的臂不等于日志中的 a 时，则无法观测到奖赏 rπ(x)。

实践中我们采用 Li 等人在 "Unbiased Offline Evaluation of Contextual-bandit-based News Article Recommendation Algorithms" 中提出的 replay 评估方法和后续 Nicol 等人的改进方法 "Improving offline evaluation of contextual bandit algorithms via bootstrapping techniques"。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMicfEvMTgjbRGoJpLKSqXoNS73DIQGLNxPSk9SeUox74PicTb5ianOt5Ig/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMIg3vQNciahfVwiatYepjbZ1q9LWCgtSbRBMBhD6JZNjto0aBQQkqicONg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMFgI3vbnoKl5ctabicBPYvX3CLhbKFW97KrJNJopycHKIvibDicWNRfuuA/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMCNoO7sUAuXBp2y9VubBx82rbic8HCsv3lrjdOvGYJ8xT86hB9D2icEkw/640?wx_fmt=png)![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMy7ic2rklEGicInX02iaaPRwPeSmmHXPicg2mk2icUEibH8t4RdALgEk4TTuQ/640?wx_fmt=png)

Jittering Technique：数据集中的每条记录在每个扩展数据 SB 中出现了 K 次。为了防止潜在的过拟合风险，在 context 特征上引入一小部分高斯噪声 ( Gaussian Noise )，这也是一种在神经网络领域中常用的技巧。

**5. 实践经验**

**① 先验的选择十分重要。**K 个臂未知的点击概率 (θ1,θ2,···θk) 采用均匀的 Beta 分布。但是事实上，某些 θ 值应该比其他值更大，采用均匀先验会损害模型，并且均匀先验没有考虑情境信息及历史经验知识。对于新上架的文案，我们并不打算直接采用均匀的 Beta 分布，而是寻找与其类似的文案 ( 利用文本和图像的相关性 ) 对其赋予先验知识。

**② 参数 α 和 β 可调整，从而可以控制采样样本的方差。**items 的先验知识可以方便地融入这些参数中。在 α 和 β 中引入参数 γ，使得参数分别变为 α/γ 和 β/γ，对后验分布稍做调整，这样不会改变后验均值，但是方差会乘系数 γ2 。当 γ 值小于 1 时，会减少探索的次数，从而获得较低的回报。

**③ 解决探索问题，势必要冒险，势必要走向未知，而这显然会伤害用户的体验**，如明知道用户肯定喜欢 A，还偏偏给他推荐某个小概率非 A。因此，我们需要保证用于探索的候选池物品本身的质量，即使用户不感兴趣，也不至于引起用户反感，避免用户流失。

**④ 在线计算时，是否需要实时采样取决于推荐服务是否要求每次 request 都进行实时响应。**对于某些场景，用户不希望看到的内容在短时间内剧烈变化。在这种情况下，我们可以每隔几分钟采样一次，然后将参数保存，在线计算时采用查表法。

**6. 优化点**

**① θk 不随时间变化，即静态环境。**Non-stationary Bandit 问题即 θk 变化较大会使在生命周期内 k 个臂的 θk 顺序剧烈变化。

**② 采用相比于点击更加复杂的回报。**例如，考虑停留时长的点击，将回报转换为 [0,1] 内的实数，从而可以有效避免作弊点击的问题。

**以上内容选自携程技术团队新作《携程人工智能实践》**

---

如果您喜欢本文，欢迎点击右上角，把文章分享到朋友圈~~

---

**—— 新书推荐 ——**

扫描下方二维码，进入购书页面

目前可享**50元**优惠~

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhtGlrwCnQLl1ZIoQfjLHEMBicdOoqVmd3BBAIAo1NRyYwuZomRTbxMmhic8hPn4eyQFOIwLxSPcZrQ/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhYUUTnAicmDgz064WIYEsbXHSGbTibHibFbx9W2nOrUDAFsNvia7o6XicyicpwY5w2Q2IrgTd2jstd5mPg/640?wx_fmt=png)

**文章推荐：**

[携程金融大数据风控算法实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247489406&idx=1&sn=9dc0dfaab0b43bc18f1a1f5565f94aab&chksm=fbd4a512cca32c04684f90b0381b07972a508631f739729ba1668a7d6b0e975315e0f43bb890&scene=21#wechat_redirect)

[携程实时智能检测平台实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247497308&idx=1&sn=3142b56c1ab370cf3f0c6b550b8a71ac&chksm=fbd74430cca0cd26b7d84fa035be25df86fd9a988c8fa22469eff3f2049c8aa13bf2a4205383&scene=21#wechat_redirect)

[携程HBase实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247486170&idx=1&sn=ab84fce49bf2097d8e4d4cc06d8b06d6&chksm=fbd4b8b6cca331a08099f75cc5bb882dccb83e4e92f5ba3e65a2e816ece50eeb5d549873195d&scene=21#wechat_redirect)

**社群推荐：**

欢迎加入 **DataFunTalk** 技术交流群，跟同行零距离交流。如想进群，请加逃课儿同学的微信（微信号：**DataFunTalker**），回复：**交流群**，逃课儿会自动拉你进群。

**关于我们：**

**DataFunTalk**专注于**大数据、人工智能**技术应用的**分享与交流**。发起于2017年，在**北京、上海、深圳、杭州**等城市举办超过**100**场线下沙龙、论坛及峰会，已邀请近**500**位专家和学者参与分享。其公众号DataFunTalk累计生产原创文章**400+**，**百万+**阅读，**5万+**精准粉丝。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaalkxbGB7NU2Paq7KM3MPhXtxKJy9M6Bs8EicpUtqCUe6fgfV4HSiaHs7Q/640?wx_fmt=jpeg)

一个**在看**，一段**时光**！**👇**