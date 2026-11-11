---
title: 'ACL 2025 杰出论文 | 小红书 AI 搜索和北理工提出“容量差距法则”'
company: 小红书
tag: 搜索
date: 2025-11-04
url: http://mp.weixin.qq.com/s?__biz=Mzg4OTc2MzczNg==&mid=2247493933&idx=1&sn=bb7154f296262e1046e97a96fc96d90d&chksm=cfe44bdaf893c2cc04495673d75aa9a01f5a73cbf0062e675e1e30539e9f68148a0a6b57012c#rd
account: 小红书技术REDtech
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/vxnkL2N86IspAFXHsiarchgNptGaccAcLOCVqw6aHicrc8mpkpWiaYVOhmWuyzsWrcH4IcmgsLaI5hEjaoUN5VdNg/640?wx_fmt=jpeg&from=appmsg)

在ACL 2025大会上，小红书 AI 搜索团队与北京理工大学宋大为教授团队的合作论文 《**Towards the Law of Capacity Gap in Distilling Language Models**》 荣获杰出论文奖（**Outstanding Paper Award**）。该研究首次提出“容量差距法则（Law of Capacity Gap）”，揭示了在语言模型蒸馏中，学生模型与教师模型的最优规模关系呈线性规律（约为 2.5 倍），大幅降低了寻找最佳教师模型的算力成本，并成功将蒸馏效率与性能推向帕累托前沿。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLmsN1wmhC6csCIbaHHEC2orXM1JDLvsJbBQBxoO3gWx2aWsDK2edsaA/640?wx_fmt=png&from=appmsg)

小红书 AI 搜索团队和北京理工大学宋大为教授团队合作论文 《Towards the Law of Capacity Gap in Distilling Language Models》 在自然语言处理顶级国际会议 ACL 上获得**杰出论文奖（Outstanding Paper Award）。**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcL3PKQnp0ibw2fhx4Aelp76TSPhkwHrzJKxe1jthzJic7pPHXcg1YE948A/640?wx_fmt=png&from=appmsg)

获奖论文《Towards the Law of Capacity Gap in Distilling Language Models》主要关注大规模语言模型（Large Language Model）蒸馏中的**“容量差距诅咒”（Curse of Capacity Gap）****现象**：当学生模型与教师模型的规模差距过大时，性能最优的学生模型未必来自规模最大的教师模型，而确定对应最优教师模型规模往往需要高昂的算力成本。该研究受到语言模型规模定律（Scaling Law）的启发，通过一系列小规模试验，探索给定学生模型规模与其最优教师模型规模之间的数学关系，并首次发现二者呈线性关系（最优教师规模约为学生规模的 2.5 倍），提出了**容量差距法则（Law of Capacity Gap）**。该法则不仅显著减少了确定最优教师模型规模所需的计算成本，还在跨规模实验中验证了其稳健的外推能力，并据此成功蒸馏出高效小型模型 MiniMA。

**Github Repo**：

https://github.com/GeneZC/MiniMA

**Huggingface Model:**

https://huggingface.co/GeneZC/MiniMA-3B

**Arxiv Link**：

https://arxiv.org/abs/2311.07052

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLYY1EKBaUOX84o782JDHogwaV7GRAPGHkymaedw9h0O3t98PDp1JCeA/640?wx_fmt=png&from=appmsg)

语言模型蒸馏主要是指利用教师–学生的范式，将较大规模的模型（教师模型）的知识尽可能无损地迁移到较小规模的模型（学生模型）上，从而获得更好的效率和可接受的性能。

但是语言模型蒸馏因教师模型和学生模型规模差异较大而面临着一个反直觉的现象，即容量差距灾难（Curse of Capacity Gap）。如下图，与性能最佳学生模型相匹配的最优教师语言模型，未必是参数量最大的模型。具体而言，如图所示（上部分），对于分别从 GPT-2-medium（3.8 亿参数）、GPT-2-large（8.1 亿参数）和 GPT-2-xlarge（16 亿参数）蒸馏得到的约 3 亿参数学生模型，性能最佳的学生模型（以困惑度衡量，越低越好）反而源自 GPT-2-large 教师模型，而非参数规模最大的 GPT-2-xlarge。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLTsxlZVd5y0meKOrib6VnHa8J9SPr5B2kO4mR9nPGv8f62sWLRu3NNpw/640?wx_fmt=png&from=appmsg)

在这种现象下，越来越多样化的教师模型导致了容量差距不可能三角（Impossible Triangle of Capacity Gap）。即为了确定最优的教师模型，需要针对不同规模的教师语言模型进行枚举式蒸馏实验，从而导致了对于特定规模的学生语言模型，其最佳性能所对应的最优教师模型规模并非无法在小算力的基础上被发现。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLOC3kc2YJ1uwrhMia5f9kN9iawIdJ7QiaQjTxVPFPRkV4DlmqibjP0ekzuA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLSX1tNZMO4ViaAU97yuabJArBMc9UiaNZSyzsxribwbW9sOT6Nn4hEQVyg/640?wx_fmt=png&from=appmsg)

面对这一不可能三角困境，我们能否将容量差距的诅咒转化为定律？能否以最低计算开销为约束，基于目标学生模型规模确定最优教师模型规模？为此，我们提出一个基本假设：在目标学生模型规模与最优教师模型规模之间，存在一种完美适配的数学关系——即容量差距法则。

为了发现这一法则，我们进行了大量的小规模试验，对于其中的每个试验，我们：

1. 每次选取特定规模的预训练语言模型作为教师模型；
2. 将教师模型裁剪至特定稀疏度作为学生模型；
3. 执行从教师模型到学生模型的知识蒸馏；
4. 观测获得最佳学生模型性能的最优教师模型规模规律。

从试验中，我们观察并形式化最优教师模型的规模应为给定学生模型规模的 2.5 倍，如下图中横坐标为给定学生模型规模，纵坐标为该学生模型对应的最优教师模型规模。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLVklORH9mmSpsiblMiarmE8F0qLGcSDNHamfBkXHC2Gc76CLYBtvNqahA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLFKfNavoTA9M25qbaZSUfia5QvvR9Aj9eQAIibEzUKjMAeAW65JnNOzYg/640?wx_fmt=png&from=appmsg)

为了验证上述法则的规模外推性，我们分别从 LLaMA-{7,13,70}B 模型蒸馏得到 MiniMA-3B，以验证 MiniMA-3B 是否如容量差距法则预期那样，从 LLaMA-7B 获得最佳蒸馏效果。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLylfHZKGtO3umpcgnkTzwWtKhlFUcANzgY0Y6rYbiad9wiabvcNxibOYuA/640?wx_fmt=png&from=appmsg)

实验证明，3B 参数的语言模型从 LLaMA-7B 蒸馏效果最佳，这与我们提出的容量差距法则完全吻合。

并且通过法则指导下的语言模型蒸馏，在当时的小型语言模型中获得了最先进的计算效率与性能的帕累托前沿（Pareto Frontier ）。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLMFaEtncM4uWVmQte6ckXErAoPLhOzZYZkt5icvFPM6AfztSvsRy8B3g/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcLd3uYGnvjz95U1ibozeXwYqkvjRnmCeibl7geVwaX9DfcY9z6KQ1rDHXg/640?wx_fmt=png&from=appmsg)

针对大语言模型时代的知识蒸馏容量差距问题，我们提出了突破性的研究视角，以应对这一不可能三角困境。通过先导性试验，我们成功将容量差距灾难转化为可量化的法则。更大规模的实验进一步验证了该定律的普适性，并由此建立了当前最优的计算效率–性能帕累托前沿。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IspAFXHsiarchgNptGaccAcL5YiclT7s6GvpvgSuMbEeWJyiauHyyZvZmwuqQIWbzZAly6ES5Ea4SCRg/640?wx_fmt=png&from=appmsg)

**Core Contributors**

**张辰**

北京理工大学博士，研究方向为语言模型效率优化，尤其是长文本场景。ACL、EMNLP、NAACL 等会议发表论文 20 余篇，谷歌学术引用 1500+ 次。

**李秋池**

哥本哈根大学助理教授，致力于构建基于量子理论的语言表征与理解框架，通过复值神经网络或张量网络将这些理论应用于信息检索与自然语言处理任务。在自然语言处理顶级会议及期刊上发表50余篇论文。

**宋大为**

北京理工大学教授，长期从事信息检索、自然语言处理及人工智能领域的研究工作，旨在构建符合人类信息推理和认知特点的多模态信息获取、交互和知识发掘理论与方法。在相关领域发表发表论文 220+ 篇。

叶哲宇

帝国理工学院硕士，小红书 NLP 团队算法工程师，DMLC 开源社区成员。在 ACL、ICLR、NAACL、EMNLP、SIGIR 等顶会发表多篇论文，研究涵盖大模型应用、多模态推理与 AI Agent。

**高龑**

小红书AI搜索负责人，推动小红书搜索向下一代搜索演进，硕士毕业于中科院计算所，研究方向包括大模型，自然语言处理和计算机视觉，在相关领域顶级期刊和会议发表相关论文 20余篇。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IsNYLO34qtHtVEKo9ib9nygzvXVutW4Nkg1PSrwnS2W34xl6apu6CPa9WVtrymVINCE23nNA3giaEeA/640?wx_fmt=png&from=appmsg)

**招聘岗位**

**搜索算法工程师-社区搜索**

AI搜索算法工程师-社区搜索

以上岗位点击链接即可直达投递入口~

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86ItCOHnde0X71uZk2WIfMe2fUODD3FUy68wkuMKtYFemZ9nibrdJicnHyNF7vqEpiaG4MBPWJ5YtaWRYg/640?wx_fmt=other&from=appmsg&wxfrom=5&wx_lazy=1&wx_co=1&tp=webp)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/vxnkL2N86IuJC563ribGrUDxNntcJXZBM3PmwibhVFMmTckicKyCAibxx59icVPG0a0f7nC6f4g3BYQ8TJvbunvm4Fg/640?wx_fmt=other&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)

**往期精彩内容指路**

[玩疯了！今年1024，小红书技术人这么过...](https://mp.weixin.qq.com/s?__biz=Mzg4OTc2MzczNg==&mid=2247493909&idx=1&sn=27c23026a0c9cb34a8427bbdf9dee206&scene=21#wechat_redirect)

**[让我们一起恭喜小红书算法团队同学~](https://mp.weixin.qq.com/s?__biz=Mzg4OTc2MzczNg==&mid=2247493774&idx=1&sn=1131f1984f49a0b9ff968cca72bb7f0f&scene=21#wechat_redirect)**

[行业领先！小红书智创音频技术团队打造SOTA对话生成模型 FireRedTTS-2](https://mp.weixin.qq.com/s?__biz=Mzg4OTc2MzczNg==&mid=2247493755&idx=1&sn=dc0636cae11fbd278431c9fef55751ed&scene=21#wechat_redirect)

**添加小助手，了解更多内容**

**微信号 / REDtech01**

![图片](https://mmbiz.qpic.cn/sz_mmbiz_jpg/vxnkL2N86IuJC563ribGrUDxNntcJXZBMrlK9ZRbNunXeksLRknwCErDzoE7Ol8wK4zCWeicydFeM2ddQG5eoARg/640?wx_fmt=other&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1)