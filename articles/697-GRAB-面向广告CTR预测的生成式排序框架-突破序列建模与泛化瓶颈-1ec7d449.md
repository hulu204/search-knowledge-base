---
title: 'GRAB：面向广告CTR预测的生成式排序框架，突破序列建模与泛化瓶颈'
company: 百度
tag: 排序
date: 2026-02-05
url: https://juejin.cn/post/7602928386596880410
account: 
origin: harvest-202607
---
# GRAB：面向广告CTR预测的生成式排序框架，突破序列建模与泛化瓶颈

[百度Geek说](/user/4186596000416094/posts)

2026-02-05
  
324
 
阅读3分钟

   

近日，百度商业技术团队释出生成式排序框架**GRAB（Generative Ranking for Ads at Baidu）技术细节论文**。传统深度学习推荐模型（DLRM）长期存在的泛化能力不足、行为序列建模瓶颈，百度商业技术团队以大语言模型（LLM）规模化经验为启发，推出生成式排序建模范式，将用户序列建模重塑为第一级结构。我们设计了因果动作感知多通道注意力（CamA）、先序列后表征训练（STS）等关键算法，实现了开箱式端到端序列化建模；线上结果显示，GRAB相较传统DLRM体系收入提升3.05%、CTR提升3.49%，并呈现出随交互序列、模型规模增长的稳定Scaling能力。

论文链接：[[arxiv.org/abs/2602.01…](https://link.juejin.cn?target=https%3A%2F%2Farxiv.org%2Fabs%2F2602.01865%255C "https://arxiv.org/abs/2602.01865%5C")]

中文解读：[[微信公众号](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyODMzMjY3OQ%3D%3D%26mid%3D2247484426%26idx%3D1%26sn%3D01fdc7bb9b6f74e12e7f5f7326698162%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzUyODMzMjY3OQ==&mid=2247484426&idx=1&sn=01fdc7bb9b6f74e12e7f5f7326698162&scene=21#wechat_redirect")]

## **01 面向CTR预测的“生成式排序”新范式**

长期以来，DLRM体系在广告推荐/排序场景中占据主流，但在复杂用户行为序列下，往往需要重度特征工程与稀疏/稠密特征协同，仍可能出现对长序列利用不足、跨场景泛化受限等问题。GRAB以端到端生成式框架重构CTR建模流程，通过统一建模与训练策略，增强对长历史交互信息的吸收能力，并将用户行为中的关键“动作信号”纳入因果视角下的注意力建模，以更稳定地刻画时序动态与意图演化。

![http://oscimg.oschina.net/AiCreationDetail/up-7b20423443bfb5b463d4e3c254ff463d.png](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/9e752a38b1fc488cbcd862e0cdfcc60a~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785393258&x-signature=JDwE6X%2BFEfEU0rtqDd%2FvWY9J8lo%3D)

*△GRAB模型设计核心结构*

## **02 三项关键创新：从结构到训练的系统性升级**

1. **端到端生成式框架**（End-to-End Generative Framework）将CTR预测问题重构生成式排序范式，降低对传统DLRM中显式特征工程与复杂组件堆叠的依赖，使整体建模路径更统一、更可扩展。

2. **因果动作感知多通道注意力**（Causal Action-aware Multi-channel Attention, CamA）在多通道注意力结构中显式刻画用户行为序列中的动作信号及时空关系，更有效捕捉“时序动态 + 行为动作”的耦合信息，从而提升预测质量与稳定性。

3. **面向规模化的训练策略**（Sequence-Then-Sparse, STS）提出“先序列、后稀疏（STS）”训练组织方式，在保证序列建模能力的同时兼顾稀疏特征与训练效率需求，为工业级大规模ID特征与自回归序列化训练与部署提供可落地的优化路径。

## **03 线上核心场景全量部署：收益与CTR实现稳定提升**

在线上部署实验中，GRAB相较既有DLRM体系取得显著改进：**收入提升3.05%**，**CTR提升3.49%**。同时，模型呈现出明确的Scaling-Law：随着纳入更长的用户交互序列，更大的模型尺寸，其表达能力提升表现为**单调、近似线性增长**，显示出对长序列信息的更强利用效率与更好的扩展潜力。

GRAB的价值不仅体现在指标提升，更在于其面向工业推荐系统的可扩展路径：通过生成式建模范式与推荐场景的结合，在“数据、计算、算法”的约束下，提供了可复用的算法框架与工程化实现方案，为后续更长上下文、更强泛化能力的广告排序模型演进奠定基础。