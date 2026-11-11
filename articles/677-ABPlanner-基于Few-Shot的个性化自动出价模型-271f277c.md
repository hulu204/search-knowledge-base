---
title: 'ABPlanner：基于Few‑Shot的个性化自动出价模型'
company: 阿里妈妈
tag: 广告
date: 2026-02-06
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497020&idx=1&sn=dcf878c99ca76a9324be342ca13a1f00&chksm=c1d781d088b0b4093d5389cc547569448ef68b6ff160380f4c502946bc9b25d2d580392d5950&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
## 摘要 本文研究互联网在线广告场景下的自动出价问题，聚焦于如何通过基于上下文的学习来获得上层的预算分配策略，以实现在仅用少量样本（Few‑Shot）的情况下为广告主快速适配个性化出价模型。 在线广告中，广告主常使用平台的自动出价服务来竞拍广告位，目标是在预算约束下最大化累计展示价值。但由于出价环境因广告主而异，制定个性化出价模型具有挑战性。为此，本文提出 ABPlanner（Adaptable Budget Planner），一种在少量样本条件下可自适应的预算规划器，用于提升预算约束下自动出价的效果。该方法基于分层出价框架，将整个出价过程划分为多个短期阶段，并在各阶段分配预算，指导底层自动出价模型按计划执行。ABPlanner 通过顺序决策实现自适应：在每轮投放过程中根据历史数据调整预算计划，使其能在仅需少量样本的情况下快速适应不同广告主，具有良好的样本效率。大量仿真与真实 A/B 测试表明，ABPlanner 显著提升了广告主的价值。 基于本工作的论文已被 KDD'25 ADS Track 接收，欢迎阅读交流。 论文：An Adaptable Budget Planner for Enhancing Budget-Constrained Auto-Bidding in Online Advertising 作者：Zhijian Duan, Yusen Huo, Tianyu Wang, Zhilin Zhang, Yeshu Li, Chuan Yu, Jian Xu, Bo Zheng, Xiaotie Deng 下载：https://dl.acm.org/doi/10.1145/3690624.3709414

1. 引言

实时出价（RTB）在在线广告中至关重要，每当展示机会出现时，广告拍卖实时触发。RTB的速度和效率使广告主能针对特定受众并实时优化投放。为应对环境的复杂性，广告主常采用自动出价策略，借助算法和模型快速作出出价决策。自动出价器的目标是在预算限制下最大化累计展示价值 [1]。由于展示的价值和价格未知，这一问题可视为在线随机背包问题，理想策略是优先赢得性价比高的展示。然而，由于展示信息的随机性及出价过程的高频次，任务复杂；且不同广告主面临不同环境，使策略优化更具挑战 [2][3]。

为应对这些挑战，本文提出ABPlanner，一个少量样本自适应预算规划器，用于增强预算约束下的自动出价。ABPlanner基于分层出价框架，将长时间回合划分为短阶段，高层预算规划器负责在各阶段分配预算，基础出价器依据分配计划在阶段内出价。这一结构能根据展示随时间的变化调整策略，同时降低基础出价器的决策复杂度。ABPlanner被建模为顺序决策者，其决策过程遵循马尔可夫决策过程（MDP）。每轮投放对应一个决策步骤，预算计划调整为动作，历史数据作为提示，使ABPlanner能逐步适应广告主并实现样本高效学习。其训练可采用PPO [4]等深度强化学习算法。

我们在模拟和真实环境中评估了ABPlanner的性能。实验结果表明，高层规划器显著提升了基础出价器的效果，ABPlanner对新广告主具备良好适应性。在真实广告系统的A/B测试中，ABPlanner显著提升了累计展示价值。

## 2. 分层出价框架

我们考虑预算约束下的自动出价问题，自动出价器代表广告主参与顺序拍卖，在预算内最大化赢得展示的累计价值。设为顺序到达的展示数量（通常未知），每个展示具有价值和市场价格。自动出价器提交出价，若则赢得展示，获得价值并支付，我们用＝表示是否赢得展示。问题可形式化为：

关键在于优先赢得高性价比展示。然而和在决策时不可得，只有可见，在赢得展示后才揭示，问题等价于一个在线随机背包问题。挑战在于：一是和分布具有显著随机性，二是出价过程覆盖大量展示，使得决策过程长且复杂。

为缓解上述问题，我们引入分层框架，通过高层预算规划器增强基础自动出价器。我们将出价过程划分为个阶段，每阶段可基于时间或展示数量划分，并建立预算计划。每阶段预算作为该阶段的预算限制或辅助参考，供基础出价器 [5]使用。规划者目标是在预算内为广告主设计预算计划，以最大化预期累计收益：

其中为第阶段在预算计划下的预期收益。注意，我们向出价器提供完整的，使其可利用全局信息做决策，同时期望考虑了出价器行为和广告主的不确定性。

## 3. 自适应预算规划器

一种简单的预算分配方法是拟合每阶段的预算-收益函数并直接优化预算计划。但该方法依赖大量历史数据，样本效率低，难以适应新广告主或数据稀缺的场景。

为实现样本高效的规划，我们提出ABPlanner，一个少量样本自适应预算规划器。ABPlanner被建模为马尔可夫决策过程（MDP）中的顺序决策者，能动态调整预算计划，并利用过往回合数据作为提示，缓解日志稀缺或过时问题。整个算法流程如下图所示：

![ABPlanner_diagram.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYOx6lLjiak1rynZOmc4ZWXg4MgTSa6N8qEr3s5kfDJ7FbYwEWfKyGxlnUetHMObQsy7OHFQ3TbAy5LyjuzUhGzFVyBESgyyH2ME/640?wx_fmt=png&from=appmsg)

对广告主，我们在初始回合接收预算计划，可设为均分或采用历史平均预算消耗。ABPlanner随后在每个出价回合调整计划，建模为MDP：

* 状态：，包含总预算、历史预算分配、收益和成本。
* 动作：，表示预算调整方向。
* 转移：依据，下层自动出价者完成出价，收集阶段收益与成本。
* 奖励：，鼓励逐回合提升收益。

ABPlanner目标是最大化个出价回合内的期望累计奖励： ，其中期望是关于广告主。

我们使用深度强化学习方法训练ABPlanner，具体细节见原论文。

## 4. 实验

我们进行了模拟实验和在线实验。

### 4.1 模拟实验

我们在两个模拟环境中验证ABPlanner：一个基于合成数据，另一个使用真实数据构建的半模拟环境。结果表明，随着出价周期推进，ABPlanner逐步利用更多历史信息，显著提升广告主的累积回报。

![模拟实验.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYMzhic3RC72XibQblCGHSObqiciaN9IdzRLyCn6mOvPjGquk6rEjLnHibF49uqL8aicIbia9G58hXUqWUcgXncMmJlQ19U9u7LMyY9zC4/640?wx_fmt=png&from=appmsg)

在半模拟环境中，ABPlanner还能智能识别性价比高的时间段进行预算倾斜：

![预算分配.png](https://mmecoa.qpic.cn/mmecoa_png/YbDPHqs6VYOibsZIRAwpTDZvKicpQSdzLYsjzv1AG0icjwpEjozdA6vo6A5UjbyHCaU7LhQjhb6aiaE2rfv5dvUcQgty3IicibvNiaeZWodgefwJ00/640?wx_fmt=png&from=appmsg)

### 4.2 在线实验

在线实验将一天划分为个阶段（每小时一个），以一天为一个出价回合，基础自动出价器使用线性规划。ABPlanner在推断过程中持续收集数据并更新策略。

结果显示，ABPlanner在大多数指标上超越基线，特别是在后两天转化次数显著提升，表现出持续优化能力。此外，其在多数天中降低了总成本，有助于提高平台收入。第四天起，转化数量持续上升，验证了其基于预测转化率优化策略的有效性。

![线上实验.png](https://mmecoa.qpic.cn/mmecoa_png/YbDPHqs6VYOJ4pZ9iczISjXrfiaBHxelibKGUyyKALyfnA97Pe4DremL50HgKRL7d8dNtgSAu7fT7fJpicsvBGY85pXr45C2YA54c3bkN4Q1vHU/640?wx_fmt=png&from=appmsg)

## 5. 总结

本文提出ABPlanner，一种少量样本自适应预算规划器，用于提升在线广告中的预算约束自动出价效果。ABPlanner基于分层出价框架，将出价回合划分为多个阶段，并通过高层预算规划器生成预算分配计划，从而捕捉时间变化并简化基础出价器的决策。ABPlanner被建模为马尔可夫决策过程（MDP），将每轮预算调整视为一次动作，利用少量历史回合数据动态优化预算分配策略。大量实验验证了其有效性与适应性，且在真实广告系统中的部署展示了其实际可行性。未来方向包括：联合优化预算规划器与基础自动出价器，实现更紧密协同；以及探索逐阶段动态预算调整机制，以实现更精细和灵活的出价控制。

## 6. 参考文献

[1] Balseiro, S. R., & Gur, Y. (2019). Learning in repeated auctions with budgets: Regret minimization and equilibrium. Management Science, 65(9), 3952–3968.

[2] Wang, H., et al. (2023). HiBid: A cross-channel constrained bidding system with budget allocation by hierarchical offline deep reinforcement learning. IEEE Transactions on Computers.

[3] Li, P., Hawbani, A., et al. (2018). An efficient budget allocation algorithm for multi-channel advertising. In ICPR 2018, 886–891.

[4]Schulman, J., et al. (2017). Proximal policy optimization algorithms. arXiv:1707.06347.

[5] He, Y., Chen, X., Wu, D., et al. (2021). A unified solution to constrained bidding in online display advertising. In Proceedings of the KDD '21, 2993–3001.

## 💡 关于我们

决策智能平台团队在业务上负责阿里妈妈的核心产品“新享”和“营销托管”。其中，“新享”是淘系最大的由商家出资的权益发放产品；“营销托管”则是业界首个将权益与广告联合进行营销的产品，业务正处于快速增长阶段。在技术方面，团队主要聚焦于决策智能算法的研发，包括自动出价、权益与广告的分配与投放、Uplift 模型预估等方向。我们的技术处于业界前沿，代表性成果包括：AIGB（业界首个生成式自动出价模型）、Bid2X（通用竞价环境建模框架）、RL-based Bidding（Offline RL、Iterative RL等）、Neural Auction（工业界首个智能拍卖机制）等，相关工作已发表在 KDD、NeurIPS、WWW 等国际顶级学术会议上，并引发广泛关注。此外，我们还发起了全球首个自动出价竞赛，并开源了大规模自动出价仿真环境 AuctionNet。团队与高校保持紧密合作，承担了多项学术合作项目，并荣获集团“优秀合作项目”奖项。

欢迎聪明、靠谱的小伙伴加入我们！（社招、校招、实习生、高校合作、访问学者等均开放）

**📮**简历投递邮箱：zhangzhilin.pt@alibaba-inc.com

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&randomid=pugabtu8&tp=webp#imgIndex=9)

****也许你还想看****

[让 AI 写出生产级代码：阿里妈妈效果广告引擎AI Coding实践](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497012&idx=1&sn=13abef9387090e5f716e4dbb3f421c07&scene=21#wechat_redirect)

[广告平台智能优惠券：撬动商家ROI与平台增长 | KDD’25](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496932&idx=1&sn=19140f0c93b3806f16e939476a656a15&scene=21#wechat_redirect)

[KDD'25  |  Bid2X：基于基础模型视角的广告竞价环境建模](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496899&idx=1&sn=4ef3db0db5b208fc5306c2bd51545e5d&scene=21#wechat_redirect)

[让逻辑「漂」起来：阿里妈妈广告引擎Serverless（GaaS）架构揭秘](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496921&idx=1&sn=70f568577ffbf6fc51a1f08aec0423cf&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=15)

喜欢要“分享”，好看要“点赞”哦ღ~