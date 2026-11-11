---
title: '多模态检索：UniNote 让内容表征与排序“合二为一”'
company: 小红书
tag: 排序
date: 2026-07-24
url: http://mp.weixin.qq.com/s?__biz=Mzg4OTc2MzczNg==&mid=2247495811&idx=1&sn=be436d855b70d48773142f374187731f&chksm=cfe45274f893db62e2c4b01f83c75e17b0178f15daf2e8aee2dcd99e492ba16071f65d172237#rd
account: 小红书技术REDtech
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/P9Hs04VFGRlRsibA9wvMF9Hq5z3o9ckiaicJ5W8Xkx66pYm0zB4L4yMibnUibugOc0eicqz3jGYibuNkcicu4Hu03fKhOwjNnfWhTcjxn17ia8vVNXtI/640?wx_fmt=jpeg&from=appmsg)

多模态检索：UniNote 让内容表征与排序“合二为一” **UniNote: A Unified Embedding Model for Multimodal Representation and Ranking**

作者：Jinghan Zhao, Wenwei Jin, Anqi Li, Jintao Tong, Luya Mo, Jiawei Li, Bin Li, Yao Hu

单位：小红书、上海交通大学、华中科技大学、北京理工大学

论文链接：

https://arxiv.org/abs/2605.29287v2

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRkhZaawo1LtmGaicgkre442z3CyJ5JrVeapPmrr8RtexIX1C5eRsEdMjN5pVtIAaibtiaQWz4Tq4cwNpsTcfS1P8g5w1ftOeGwTbM/640?wx_fmt=png&from=appmsg)

一张图片、一个标题、一段正文、几行 OCR 文字.……当这些信号混杂在一条笔记里，如何让模型在一次检索中既挖掘局部元素，又细粒度刻画候选与查询之间的相关性？这是工业级多模态检索 Item-to-Item (Item2Item)面临的真实挑战。传统方案通常将嵌入表示与排序拆分为两个独立阶段，导致系统效率低下、延迟高，并且难以在精度与计算成本间取得平衡。我们提出了 **UniNote**，这是一个统一的多模态嵌入模型，将表示学习与排序能力融合于单一模型中。通过创新的两阶段训练范式（对比  SFT 强化表示 + 强化学习排序优化），UniNote 在单次嵌入传递内实现了与复杂两阶段检索-排序范式相当的性能，同时大幅降低了计算延迟。相关研究结果已被 KDD2026 录用。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRmwfSXqOGCZkxufse9bjFMXwtF2ueqLfhvwqQM2c7WvEjTEz7qib36Llvib52VTGVl6xzNNVtBhSg0NIFdfLvIYszxtfMNtlhNQk/640?wx_fmt=png&from=appmsg)

小红书平台的用户生成内容（UGC）构成了典型的复杂多模态目标（笔记 Note，可拓展为 Item）。每一篇笔记不仅包含文本（标题与正文）和视觉序列（多张图像），还囊括了跨模态的细粒度元素（如图像中的关键 OCR 信息）。

实现此类复杂内容的精准多模态表征与相似度检索，面临两项主要挑战。

* **嵌入与排序的两阶段处理机制：**传统检索系统依赖“召回-重排”流水线架构，两个阶段各自优化不同目标，信息无法流通，且增加了检索的（资源/时间）成本。
* **全局表示与细粒度需求的冲突。**以 MLLM 为代表的 backbone 架构将全局内容压缩成单一表示，对于支持 Item2Item 检索场景的细粒度检索需求并未特殊适配。多模态内容（图片、文字、OCR 文本等）包含丰富的多层次语义信息。如何在不同粒度级别上进行有效的表示学习，既能捕获全局语义又能保留细粒度特征，是一个关键挑战。

核心问题：能否设计一个统一模型，在单次前向传递中同时完成多粒度嵌入和精准排序，并且良好适配 Item2Item 检索场景？

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRlV79YreImibuQ69icrnE3CaEZ3iaRVCC1pX8SLibwVrWRrPQsO3cySMibhiakYjIic0okUVVOa61wqBwoRiasFb3jMTG1nES5M4w04KJA/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRnMroACQ0DBSlNsibuzibJ2NeicibicXmaD5gOT57rE83c9IT0E7CwPHjnBKicVia8ZdJbC1fDn5tMgzxzm5Gt5tud0okKiaib3hx8LWN80/640?wx_fmt=png&from=appmsg)

UniNote 的核心思路，是**从统一 Embedding 的维度让模型同时具备良好的表示能力与排序能力。**为此，我们设计了“SFT学习表示 → 强化学习重排”的渐进式两阶段训练范式，并辅以 Matryoshka Representation Learning（MRL）实现多粒度弹性表示支持不同需求业务。

UniNote的核心逻辑如下：

**1. 统一表示**：用多模态大语言模型（MLLM）作为骨干网络对 Item(Note) 图文多模态数据压缩表示，以实现 Item2Item 检索任务的统一表示，这些任务包括：

* 原子对齐(Atomic Alignment)： I2T，T2I
* 从属检索(Subordinate Retrieval)：I2Note，T2Note
* 语义提取(Semantic Extraction)：Note2I，Note2T
* OCR感知(OCR Perception)：OCR2Note，I2OCR，OCR2I
* 内容相关性检索(Content Relevance)：Note2Note

**2.****统一架构**：消除“Embedder + Reranker”的两阶段管道，用一次嵌入传递替代复杂的多模型级联。

**3.****弹性部署**：通过 MRL “俄罗斯套娃”机制，在训练时对不同粒度表征表示联合优化损失函数，确保向量在任意维度截断时都保持高质量语义区分能力，支持不同场景业务下的高性价比需求。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRn716VyweH4KCpiboFHs3hypxScaTYHwco6csk4iclp4SfNOEAQFlJiapibzJ0lsTovuvficWd24iblJsbVdv96D5xEze6agvEh0K4Ek/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRk80Lziac76jYh8ECSUOSepLOPgOsr9aiceqp6ww7x4sIk9cVPB9sgNCZCCiax4o733n94FAvnJibP5bLicd9199g4gmSJv7XIHmgRI/640?wx_fmt=png&from=appmsg)

**SFT 学习表示：构建坚实的嵌入基础**

第一阶段的目标是将 MLLM 从生成模型改造为高质量的嵌入模型。相较 CLIP 等双塔结构，MLLM 架构提供跨模态融合的表征优势。我们取最后一层的 last token 作为表征，图像与文本在自注意力过程中实现跨模态交换，通过 prompt 引导的方式将输入上下文压缩至最后一个 token。

对比 SFT 的核心是构建高质量的 pair 对，此目标下，在数据和训练策略上，主要包括三个关键部分：

* **模态替换防“走捷径”：**训练“局部-全局”检索时（如图像到笔记），正样本笔记本身包含该查询图像。为强制模型通过高层语义理解来建立图文关联，我们将笔记中的查询图像替换为同语义的文本描述，防止模型依赖低级像素匹配完成检索。
* **多粒度难负样本挖掘：**我们以相似度计算为基础筛选方式，在此基础上进行 Item 拆分以便过滤样本重叠等伪负样本。另外，我们人工设计了基于规则的反事实难负样本合成策略：通过删去正候选样本中的目标元素，得到与正样本内容重叠极大的负样本。
* **JS 散度对称优化：**参考 UniME-v2 等方法的设计，我们采用 Jensen-Shannon 散度替代传统的 KL 散度作为损失函数，保证了优化方向的对称性和训练稳定性，为后续 RL 阶段提供均衡稳健的嵌入初始化。

**强化学习重排：从“找到相似”到“排好顺序”**

对比学习优化的是全局向量空间结构，对局部排序的精细性关注不足。第二阶段引入强化学习，**直接以排序质量作为优化目标。**

* **强化学习的引入：**排序本质上是一个组合优化问题，评估的是一整个排列的质量，而非单个样本的独立打分。RL 的奖励函数可以直接度量整个排序列表的质量，通过策略梯度实现端到端优化。
* **数据构造方式：**在Item2Item任务中，我们关注内容语义层面的重叠度，为此我们的做法，是将一条笔记分割为内容不重叠的两部分 A 和 B，A 作为查询，B 与 A 中不同数量的图片组合构成相关性递减的候选列表，再混入噪声笔记。这种方式无需人工标注即可获得高质量的排序监督信号。
* **分层奖励函数。**我们采用 Group Relative Policy Optimization（GRPO）算法，并设计了独特的分层奖励函数兼顾“惩罚坏排序”与“奖励好排序”的精细奖励机制：

      • 无关笔记惩罚与相关笔记奖励：对于召回结果，依据相关性判定给予基础惩罚/奖励。

      • 排序优化：由绝对位置奖励与相对位置顺序组成，分别刻画预测排序位置和多样本的相关性分数顺序。

      • 上述奖励函数维度分别从召回覆盖率和召回精准性两个原则出发，我们通过随机排序证明了奖励函数的单调递增性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRnOKzUFNOH7ibqv0vOkfjoqianupfHsiacO6GyKy3aHDj6VABJMiah7eyxjW7bX2PIVhl1TDe5w8fcPJqWcV5sibEauq0vapNsINNxg/640?wx_fmt=png&from=appmsg)

**MRL 多粒度表示：向量里的“俄罗斯套娃”**

受 Matryoshka Representation Learning 启发，UniNote 让同一个嵌入向量在不同维度截断时都保持有意义的语义信息：提供 64/512/1024/4096 四档压缩模式。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRkjzmffWr2TtkkaiaxhS2CSeAeCQuVTUseXK1uIxAIwOODaVdpSyOHmPOrBeWh4B8JTbvFLCxKdDwUibaFPu6qN6KUAUddRkibxkQ/640?wx_fmt=png&from=appmsg)

**主实验：I2I 任务的良好表现**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRnYYF7au81XkpzfoXjxyavgPr5YOV2wcgQ8icL2ciaAEMo9bQxMCYAicOqYticEdrrWusNHY4DEGY4gLOA7kmicOSW8sUeRYjULNmto/640?wx_fmt=png&from=appmsg)

实验证明，在几乎所有定义的 Item2Item 任务上， UniNote 均超越了当前的强基线模型 RzenEmbed 和 Qwen3VL-Embedding-8B。基线模型在从属检索与语义提取任务上表现较差，归因于现有模型训练所面对的场景单一，缺乏对多模态内容中“全局-局部”细粒度关系的建模能力，而 UniNote 通过数据驱动和两阶段训练，平衡了全局表征与局部检索的需求。

另外，实验结果显示，UniNote 在 I2OCR 任务上的收益较为微弱，这源于模型设计优先考虑高层语义映射，牺牲了 OCR 所需的底层细粒度字符识别能力。未来我们将引入针对性的数据集来提升模型对文字特征的敏感度，进而补齐这一短板。

注：由于 Note2Note 任务的正候选样本不唯一，因此指标计算方式不同于其余几项任务，R\*@1 反映了 multi-label nature（定义见论文附录）下的查全率。

**消融实验**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRkDnsU8cT4HbHFpyeNDaFiantC7mmU46EibraIqdbTnpkzict8Rw5H0Aqq9UaiacNjIrl8b7rV41GibjQEicDk4FNsb7Mj5cJ0yHG9Bc/640?wx_fmt=png&from=appmsg)

我们分别针对难负样本挖掘策略和两阶段训练方法进行了消融实验。

* **难负样本挖掘策略：**从随机负样本到完整的多粒度挖掘策略，模型获得了最大 23.3%的提升，证明随机采样难以学到高区分度的表示。引入基于规则的反事实难负样本挖掘则在基础难负样本筛选（基于相似度）的基础上进一步得到提升，验证了反事实规则的设计能够强迫模型区分细微语义差异。
* **两阶段训练方法：**通过引入RL过程，模型的 R@5 和 P@5 指标分别提升了 1.4% 和 3.4%。通过考虑相关性和分层奖励函数，RL 阶段有效刻画了模型对内容相关性的感知排序能力。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRlwMAiavJM51AUicQEic0kYCIGoChicmhVNFDwmVw2tyBfHgC5iaALByggezXH2k0qHM1Df6mrRyubNfQdPyWicEE4MMZboVZtyiciaUiaI/640?wx_fmt=png&from=appmsg)

**MRL 多粒度压缩效果验证**

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRl9FNXWuf91Pazww0I5icSlzn2N0zNic7BKGrHAlwuuISPDs6HE7elTo3PFRNhIgzOiaUvedlWHfjTxtZ7FpicfOwVAry8DNOt2f7A/640?wx_fmt=png&from=appmsg)

我们评估了模型在4种嵌套特征维度（64,512,1024,4096)下的检索表现，其中检索性能总体上随着特征维度的增加而呈现上升趋势。

当维度压缩到 512 维时，绝大多数检索任务的性能已经非常接近满维度 (4096维) 的表现；而当维度被极限压缩到 64 维时，虽然性能不可避免地出现下降，但模型在图文对齐、从属检索和语义提取等任务上依然保留了约 70% 的检索能力。

上述结果验证了 UniNote 生成的表征具有良好的信息密度分布。这使得在实际工业部署中，业务方可以根据不同场景的需求，灵活选择特征维度。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRnwQuLetyUNh6lw5dINv02dHrs1KGTWDhqiaU2PwibHXAvZHYzBTibgq5ou4qmD771O9rZK2JgvvYSlkxIgg8e7zfqDvKjCibVEZ8Q/640?wx_fmt=png&from=appmsg)

UniNote 提出了一种全新的统一嵌入范式，将多模态表示学习与排序优化融合于单一模型，为工业界 Item2Item 检索提供了一种新的解决思路。为实现我们的目标，我们提出对比学习与强化学习有机结合为渐进式训练范式，并用分层奖励函数优化内容相关性感知排序。未来，我们将继续探索“相关性”这一主题，将 Item2Item 的检索拓展到 Any2Any 场景支持任意场景下的检索需求。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRnYaNaHaAibVJUXkgEoBLNwMAB1WNaleSnN6UmUibibfhuKHmWPP6uR7fVAKFV8NPJtem1yrBJUt2ssTBdBXHBTaay3siaT4rD7uUc/640?wx_fmt=png&from=appmsg)

**小红书内容增长团队招人啦～**

招聘内容/多模态大模型算法工程师/算法专家，方向：内容结构化、内容表征、热点挖掘与趋势预测、图文/视频质量建模、Anti-AI/Anti-GEO 治理等；熟悉预训练、SFT、RL、语义表征、时序建模、多模态理解及 PyTorch/HuggingFace/DeepSpeed 等框架，有相关项目经验、顶会论文、开源项目、竞赛奖项者优先；地点：北京/上海/杭州，社招/校招/实习均可。

投递邮箱：

jinwenwei@xiaohongshu.com

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRlUFBjWarTpiaSCEpxkWmEG5AvgkdVz9ZDZ4kSvibdQ7q4rwKHn4XWB6B6ibPZhks7HkfOQD41jIweK2fo2qy5ZbOrwVn0nIibAlac/640?wx_fmt=png&from=appmsg)