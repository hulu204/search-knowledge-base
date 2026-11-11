---
title: 'WWW’26 Oral | DARA：面向在线推广的小样本预算分配双阶段RL‑LLM框架'
company: 阿里妈妈
tag: 广告
date: 2026-05-08
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497286&idx=1&sn=cab98b831fcdf3ea5c22728c2e92cc0e&chksm=c1fcd359ada4b24a95a27c7a5910b880b80b5f060e6d1a801317640b5c232dbbe14ee21292c8&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
# 摘要

在线上推广投放中，客户需要在预算约束下最大化获胜曝光的累计价值。然而，大多数客户只有有限的历史数据，传统强化学习（RL）方法难以在这种“小样本”场景下表现理想。大型语言模型（LLMs）通过上下文学习可以从少量数据中概括规律，但在数值精度方面存在不足。为了兼顾泛化能力和精细化决策，阿里妈妈决策智能平台团队提出 DARA（Dual‑phase Adaptive Reasoning and Allocation）框架。DARA 将预算分配任务拆解为两个阶段：第一阶段利用小样本推理器根据有限历史数据生成高层预算计划；第二阶段利用精细优化器根据动态反馈逐步调整预算。此外，引入了 RL 微调策略 GRPO‑Adaptive，通过定期更新参考模型提升 LLM 的推理精度。在真实和模拟环境上，DARA 显著降低了边际投资回报率（ROI）的方差，超过传统基线模型。该工作成果收录于WWW 2026。

论文标题：DARA: Few-shot Budget Allocation in Online Advertising via In-Context Decision Making with RL-Finetuned LLMs

作者：Mingxuan Song, Yusen Huo, Bohan Zhou, Shenglin Yin, Zhen Xiao, Jieyi Long, Zhilin Zhang, Chuan Yu

链接：https://arxiv.org/pdf/2601.14711

# 一、引言

实时竞价（RTB）场景下，客户需在固定预算内最大化累计回报。由于预算有限且回报函数呈现边际收益递减特性，如何跨时间段合理分配预算成为关键。传统方法使用手工启发式策略或单一 RL 模型，但难以在动态环境中泛化。近期的大语言模型展现出在小样本情况下的强大推理能力，通过上下文提示即可完成复杂任务。然而，单阶段 LLM 通常缺乏数值敏感性，难以进行精确的预算优化。

作者观察到预算规划自然包含两类问题：一是从有限历史数据中提取规律并制定高层计划，二是结合实时反馈进行细粒度调整。单一模型难以同时兼顾这两个阶段，因此需要拆分任务并结合强化学习提升模型的数值推理能力。

基于上述分析，作者提出了双阶段决策框架 DARA。其设计理念是：早期决策更依赖于小样本泛化，而后期调整需要对实时反馈敏感，并进行精细化控制。为解决 LLM 数值不敏感问题，作者引入了动态 KL 正则化的 RL 微调算法 GRPO‑Adaptive，周期性更新参考模型以避免模型退化。此外，作者构建了真实数据环境和可控的仿真环境，为训练提供多样化场景。

# 二、预备知识

## 1. 预算分配模型

在一个推广活动中，总预算记为 。将预算划分为  个时间段，记  为第  段的预算支出， 为该支出带来的期望收益，则整体 ROI 为收益总和除以总预算：

由于  固定，最大化 ROI 等价于在  的约束下最大化总收益。作者假设每个  函数可微、严格递增且凸度减小，这体现了投入越多带来的边际回报会降低。最优条件是各时间段的边际收益相等。因此，预算规划的目标可以近似为使各时间段边际 ROI 的方差最小。

## 2. 相关工作

传统预算分配方法包括手工规则和基于 RL 的模型，但往往忽视时间段之间的相互影响或者难以快速适应环境变化。层次化 RL（HiBid）将预算决策分为高层分配与低层竞价，但缺乏在线自适应机制。基于 LSTM 的 ABPlanner 受限于数据量少和环境动态变化。近年来，大型语言模型在小样本学习方面表现出色，能够通过上下文提示快速泛化。然而，单一 LLM 缺乏数值敏感性，难以应对复杂决策问题。这些挑战激发了利用双阶段架构和 RL 微调提升小样本预算分配能力的研究。

# 三、方法

DARA 框架包括环境建模、小样本提示生成、双智能体决策以及 RL 微调策略。下文将逐一介绍。

## 1. 环境建模与问题定义

作者提出2种环境训练环境：真实数据环境基于企业级推广投放数据构建，模拟了实际市场的成本和 ROI 动态；仿真环境通过可控的多项式/指数函数生成预算–回报曲线，使模型能够在多样化场景中学习。在这些环境中，预算分配任务被形式化为：给定历史小样本数据集 ，其中  表示第 i 个预算向量， 为对应的边际 ROI 向量，目标是在总预算 B 约束下生成新的预算向量  使得边际 ROI 方差最小。

![image.png](https://mmecoa.qpic.cn/mmecoa_png/YbDPHqs6VYMmGlfPy35aSmBKibTJ3Gfb7MRgKV7RYVqNKlkzVyhU6abMM7m8xPKDIIbMcEhiazt9IT9TdQX7JdvaNzl439rboYiccw3ovzIJHM/640?wx_fmt=png&from=appmsg)![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYOm7Ih1DVFe7TkeFg1ibHRBSicmKzReMTLTndUsA84iazsofvVib1ySUrJT2NiaIZ9KJ4W5pkwBK4QCrNKvCIO8bHNtTdUNoqjahLzg/640?wx_fmt=png&from=appmsg)

## 2. 小样本提示（Few‑shot Prompting）

针对预算规划的数据稀缺性，作者设计了一种提示模板，将目标描述、小样本数据、历史尝试记录和输出格式组合成结构化的 Prompt，输入给 LLM。这样，模型可以利用少量示例形成初始分配策略，输出包含预算向量以及策略解释，增强决策的可解释性。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYPBOlkRr0eVykA29vLWDicwJic8NrLJsErhKbA5Bvmpfrby04z1fUiauQYvx2p6m5cFyCALYl3RkQDSmRzbvicYWktPwBTX2A2swibY/640?wx_fmt=png&from=appmsg)

## 3. 双阶段协同智能体

DARA 将任务拆分为两个阶段：

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYMXXPS2c7Cac9Puxt1ibp7OBARwCOVviaCuwwNIVv1TDFjvDicHMk4vUS2W1icyGWC7DUX8yb5NGl2Ora57tZhYnjWHxGvMH0gVy8s/640?wx_fmt=png&from=appmsg)

• 小样本推理器（Few‑shot Reasoner）：根据少量历史预算记录，生成第一天的预算分配方案，关注全局趋势和策略；  

• 精细化优化器（Fine‑grained Optimizer）：从第二天起，根据推理器输出的预算和每个时间段的边际 ROI 反馈，局部调整预算。优化器使用滑动窗口机制记录最近几次决策和反馈，以便动态更新策略。

算法 1 总结了双阶段协同的流程：首先通过小样本推理器生成初始预算，随后在每个周期内根据反馈调整预算，直到满足终止条件。这种架构将泛化和优化解耦，使不同 LLM 能各司其职，避免单模型的能力瓶颈。

# 4. RL 微调策略：GRPO‑Adaptive

在将强化学习应用于 LLM 微调时，GRPO（Group Relative Proximal Optimization）是一种常见的基础算法。其核心思想是通过组内相对优势估计来稳定策略更新，并借助 KL 散度约束防止策略偏离参考模型过远。然而，作者在实验中发现了一个关键瓶颈：**当参考策略**  **在整个训练过程中保持静态不变时，模型对结构化推理和数值精度的敏感性会逐渐下降。** 这是因为随着策略持续优化，当前策略与固定参考策略之间的分布差距越来越大，KL 正则化项会产生越来越强的"拉回力"，将模型束缚在一个已经过时的基线附近，最终导致推理能力退化——这在预算分配这类需要多步精确数值计算的任务中尤为致命。

## 5. GRPO‑Adaptive：动态参考模型更新机制

为解决上述问题，作者提出 **GRPO‑Adaptive（GRPO‑A）**，其核心改进在于：**周期性地将当前策略快照替换参考模型，并在新基线上重置 KL 正则化项。**

具体而言，每经过  次 GRPO 更新后，执行以下三步操作：

**1）快照当前策略**：对当前参数  进行深拷贝；

**2）替换参考模型**：用该快照覆盖静态参考策略 ，得到动态参考策略 ；

**3）重置 KL 基线**：KL 散度约束从新的参考点重新计算，而非累积偏离原始起点。

这样，优化目标从标准 GRPO 的固定锚点形式，演变为动态锚点形式：

周期性更新

其中  控制奖励最大化与策略稳定性之间的权衡， 为 KL 散度。

## 6. 裁剪优势加权目标

在具体实现层面，GRPO‑A 沿用 GRPO 的裁剪优势加权（Clipped Advantage-Weighted）损失：

其中优势项  对  条采样轨迹进行组内归一化：

通过组内相对奖励归一化，模型能够在不依赖全局价值函数（Critic）的情况下，高效识别哪些输出更优，并通过 PPO 风格的裁剪参数  防止单步更新过大。

## 7. 训练流程设计

为了在多样化场景中训练出具有泛化能力的策略，作者设计了**多环境轮换采样**机制：每固定  步后随机切换至新的仿真环境（包含  条全新的边际 ROI 曲线），从而避免模型过拟合于某一固定分布。完整的 GRPO‑Adaptive 训练流程如 Algorithm 2 所示，其核心步骤如下：![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYNMJTAJCiberc6VpWF5Qlt2RH0ugiaEHxwTWbygoDdia82xBWF70a53aV8g4UnrE7NPmrPq3LQPrMoiaz7jxr8m1SbtL8H6VyEgQXA/640?wx_fmt=png&from=appmsg)

# 四、实验

作者在真实推广平台数据和仿真环境上验证 DARA 的效果。数据环境包括真实的电商推广日志和基于多项式函数生成的模拟曲线。主要评价指标为边际 ROI 方差，指标越小表示预算分配越平衡。实验结果表明：

![image.png](https://mmecoa.qpic.cn/mmecoa_png/YbDPHqs6VYPu0QmGXlx0ib7fPTIh2MXtvGVTIe5mYDtVzMObo4bF9ocM6zpN3f6Dgt0D8oT39fhhXBxw3xXKORw28L6vibB86Zvn14sPZicaiaw/640?wx_fmt=png&from=appmsg)

• 在真实数据环境中，DARA 在各步骤上都显著优于 DPO、HiBid、Q‑MCKP 和 ABPlanner 等基线模型。DARA 能够在后期阶段进一步降低方差，说明精细化优化器有效利用反馈改进策略。  

• 单阶段 LLM（无或有 RL 微调）表现较差，方差较高；双阶段架构显著改善了性能，即使不使用 RL。  

• 在双阶段模型中引入 RL 微调后，方差进一步降低。RL 帮助小样本推理器生成更具战略性的初始计划，使精细化优化器更敏感于反馈。  

• 敏感性分析显示，DARA 对时间段数量的选择不敏感，在 2–10 个时间段的设置下均能获得 10.6%–12.2% 的收益提升。此外，参考模型更新频率对模型表现有显著影响，适中的更新频率（如 60）可获得最低方差，而过快或过慢更新都会削弱效果。

# 五、总结与展望

DARA 框架通过将预算分配任务拆分为小样本推理和精细化优化两个阶段，结合 RL 微调提升了 LLM 的数值推理能力，在在线推广预算规划中取得了显著效果。关键贡献包括：提出双智能体架构、设计动态参考模型更新的 GRPO‑Adaptive 算法、构建真实和仿真环境以提升泛化能力。实验表明，该方法在稳定性和适应性方面均显著超过现有基线。

DARA 的思路展现了大语言模型与强化学习在决策智能领域结合的巨大潜力。未来工作可以探索更复杂的预算约束（如跨多推广平台协同分配）、引入注意力机制捕获时间序列特征，以及在不同规模的 LLM 上验证方法的可迁移性。此外，如何降低训练成本并保证部署效率，也是工业界进一步推广的关键问题。

# 💡 关于我们

阿里妈妈决策智能平台团队在技术上主要聚焦于决策智能算法的研发，包括自动出价、预算与推广分配、Uplift 模型预估等方向。代表性成果包括 AIGB（生成式自动出价模型）、Bid2X（通用竞价环境建模框架）、DARA（小样本预算分配框架）等，并在 KDD、NeurIPS、WWW 等顶级会议上发表论文。在业务上负责阿里妈妈的核心产品“新享”和“营销托管”。其中，“新享”是淘系最大的由商家出资的权益发放产品；“营销托管”则是业内首个将权益与推广联合进行营销的产品，业务正处于快速增长阶段。团队与高校紧密合作并荣获多项合作奖项。

欢迎聪明、靠谱的小伙伴加入我们！（社招、校招、实习生、高校合作、访问学者等均开放）

📮 简历投递邮箱：zhangzhilin.pt@alibaba-inc.com

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&randomid=pugabtu8&tp=webp#imgIndex=9)

****也许你还想看****

[阿里妈妈工程技术核心岗实习热招！在AI与商业的交汇点，定义下一代广告引擎](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497272&idx=1&sn=f7dda34358e13d1823991dd84dc37899&scene=21#wechat_redirect)

[CVPR'26 | 从任务统一到模态协同：电商通用多模态表征MOON 2.0](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497237&idx=1&sn=9b083aade6d67f83da4204d0f0981fd4&scene=21#wechat_redirect)

[WSDM’26｜阿里妈妈直通车提出搜推广系统通用用户大模型LUM](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497179&idx=1&sn=194cfcffb87f1a1d6b7e818023237dd2&scene=21#wechat_redirect)

[AAAI’26 Oral｜Agent基于用户长期行为的个性化偏好理解的评估和优化](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497146&idx=1&sn=6f4bb20de1d5d4601f81e8f43b4ae999&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=15)

喜欢要“分享”，好看要“点赞”哦ღ~