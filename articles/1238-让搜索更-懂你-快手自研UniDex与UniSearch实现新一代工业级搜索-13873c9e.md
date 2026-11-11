---
title: '让搜索更“懂你”：快手自研UniDex与UniSearch实现新一代工业级搜索'
company: 快手
tag: 搜索
date: 2025-11-20
url: http://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247498365&idx=1&sn=de0a2684938a655c9faea1313b0bba5f&chksm=cebbdaa7f9cc53b1a388737bcd04eb7b589140fe6e183fc7e5d680d747e2ab1f216ceca6fabe#rd
account: 快手技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_gif/ZxDY5TMPs0EqL7dlyXD8OFyXn6yNGvQ8uEibL6TkOHqFvaK0bR9GEhZicTHuDtaTficMGS88ecXKIVPnFJCTMz7aQ/640?wx_fmt=gif&from=appmsg#imgIndex=0)

**一、引言**

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

当你在搜索框里键入几个简单的词，期待平台能读懂你模糊的意图，从海量视频中精准找到那一个。然而，这看似简单的瞬间，实则是对现代搜索系统的复杂考验。

面对“怎么做糖醋排骨最好吃”这样的口语化提问，传统搜索如同一位依赖固定关键词的“图书管理员”，难以理解“最好吃”背后的深层需求。而当你想找一个“刚刚开播的热闹游戏直播间”，这种对极致时效性的要求，更让传统系统力不从心。

现代搜索系统通过深度语义模型对用户查询词（query）和待检索文档（doc）进行建模，其中文档侧的表征对相关结果的展示起着至关重要的作用。如何让搜索引擎不仅能“听懂”你的话，还能“猜透”你的心，甚至能预见那些你尚未明确表达的需求？这要求搜索技术必须从机械的“关键词匹配”，进化到深度的“语义理解”与主动的“内容生成”。

为了让搜索能像推荐一样“懂用户”、甚至“懂视频本身”，快手团队开始尝试一条新路径：用更智能的语义表征替代传统 Term，用能理解、能生成的模型重构整个搜索链路。在这样的探索中，新一代工业级搜索体系 UniDex 与 UniSearch 逐步成形。

团队以视频语义 ID 表征为基础，从“判别”和“生成”两大范式出发：

* 首创 Model-based 倒排方案 UniDex，全量替换 Term-based 倒排，大幅降低系统存算资源的同时，将响应速度提升了25%；
* 创新生成式搜索架构 UniSearch，首次实现编码和生成联训，打造真正的端到端生成式搜索方案，并在直播搜索场景中创造了近两年最大的直播间进间数收益。

**二、判别式变革 —— 主搜场景，统一语义倒排 UniDex**

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

倒排索引是搜索引擎的核心召回机制，随着系统的不断迭代，倒排索引逐渐暴露出一些问题，如离线资源消耗大、动态更新成本高以及泛化能力不足等。为了提升倒排索引的泛化能力，同时保留其在匹配和检索方面的优势，研究人员基于判别式思想，构建了统一的语义倒排方法 UniDex。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0H6hVDr9KTnVHuxcL87VyQRWec12lgbScQ9BhHVEDxbqldicLnic6gr69ITD3utA2XicyxMtjlhxkXjg/640?wx_fmt=png&from=appmsg)

论文链接：https://arxiv.org/pdf/2509.24632

2.1 技术创新

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

业界倒排系统通常由两个核心模块组成：召回（Touch）模块和排序（Rank）模块。Touch 模块基于倒排索引进行 Term 级检索获取候选集，Rank模块计算Query-候选集打分。传统倒排召回包含多路人工Touch方法（同义词扩展、Term省略、实体归一等），以及数十种策略/模型特征等启发式规则的 Rank 方法。UniDex 通过提出 UniTouch 和 UniRank，分别统一了传统倒排的Touch和Rank模块，避免了繁复的人工设计。在保障相关性和长尾需求的情况下，大幅节省链路资源消耗，为搜索体验带来增益。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0H6hVDr9KTnVHuxcL87VyQRlqHOEaeF9R1JprJpKB0ZHovqGMEmj9gD0Kct49icEqAzMu4hQJ6CMYg/640?wx_fmt=png&from=appmsg)

图 1 传统倒排检索和 UniDex 对比示意图

UniDex完整架构流程图如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0H6hVDr9KTnVHuxcL87VyQRdPoYbu580HrcmD10cgdpEykDu1ZVVrQymiaLAy6XcLdAGH4cf9Iehjw/640?wx_fmt=png&from=appmsg)

图 2 UniDex 整体结构图

2.1.1 UniTouch

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

（一）语义编码

1.FSQ量化：以 Query 为例，Query 侧拼接多组可学习的 Token，经过 Encoder 编码产出多组稠密向量Q\_i，经过 FSQ 量化为离线语义 ID。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0H6hVDr9KTnVHuxcL87VyQRtV9Ptv5hxibUOJW7SYf4pTwmf0bAibDFXPqZ8MfUkl4ok0icaPQ8hJtvQ/640?wx_fmt=png&from=appmsg)

图 3 基于FSQ的量化模块示意图

具体地，Query/Doc 经过编码器分别产出一组语义向量

和，通过可学习的线性投影矩阵降维后经过 FSQ 分别离线化为 K 值维的 SID （K值经验地设置为2）：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycHfTjfVYmhYX4qwIjd0cUmM8rttsJrDBC6ZnX8LpbQrm2eL1iaKUUjJg/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyycyiap1wCavg9AVNR2qCDJdosjXGhgEN21ibLtJdnNYic3icZ5sB9fP31tHQ/640?wx_fmt=png&from=appmsg)

其中，

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycFweibhwWG4eaEydKWd64Vyx8yPNAiaxVibGh7mH2jWWYnd0qbmEGaUQyg/640?wx_fmt=png&from=appmsg)

通过另一组升维的投影映射得到：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycptPnFh4B8WVib1GphbfpRuNwiawuHGicNqUJkV7BtpCkDX4J9VqvQY7Tw/640?wx_fmt=png&from=appmsg)

重构后的：能够更高效地将 SID 训练融入下游任务目标，同时保证表征的连续性与训练过程的稳定性。

2.EWGS梯度优化：FSQ 采用的STE方法未考虑量化误差。UniDex 构建 FSQ-EWGS 对量化梯度的回传过程进行优化，提高量化网络训练的稳定性和准确性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyyc7rtrnmeCVyC2YxWdwevItZJXbKGDKPWtiaOkb31GiaRWZVsbLLksO9WA/640?wx_fmt=png&from=appmsg)

图 4 基于EWGS梯度优化的的FSQ量化示意图

量化梯度优化公式可表示为：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycFzg4MtRStP3tO6ia9FDozT0km4qDRibW7OhC5whkic4LnM1hnpqqjaLDw/640?wx_fmt=png&from=appmsg)

其中为经Down-Proj线性映射得到的低维dense向量。

3.Token-Matching 机制：构建 Token-Matching 模块驱动模型强化训练/检索一致性。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyycu1MUpt0pvzfjibCD0DYqHMjsI5QYWVWHNTSYDHz8nDLb0YoFRhP6mnw/640?wx_fmt=png&from=appmsg)

图 5 UniTouch Token-Matching 示意图

Token-Matching 打分计算如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycyQcYsJQ9UMECHmAFkjBr5gho6FxQ0KqAxZIf4sgl8hlKpsqQbtmPMA/640?wx_fmt=png&from=appmsg)

该方法从本质上更好地保持 UniTouch 模型训练阶段与检索阶段之间的一致性，与倒排索引范式高度契合。倒排索引的核心逻辑是：Query 端与 Doc 端任一 SID 匹配即可召回；而 Mean 或 Sum 方法要求 Query 端所有 SID 均需与文档端 SID 达到一定相关度才能检索，这与倒排机制相悖。

（二）学习策略

1.Contrastive Learning：学习搜索链路的排序逻辑，提升模型的排序性能。采用分段可学习的 ListWise InfoNCE Loss，将 Query 对应下低于当前视频档位的其他视频作为负样本，同时在同 Batch 内采样随机负例。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyycl2XRAuPVzicjvVNQ1MGIqKV9CniaaVdTbu06EtE8kzEJiasuaQibC24LEg/640?wx_fmt=png&from=appmsg)

其中是分桶且动态学习的温度系数，表示负例的集合。

2.Matching Loss：引入针对高档位相关正例的 Matching 损失目标，强化模型使 Query 与高相关视频产出相同 SID 的能力。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycxnPEic20apcW2AnViajgicCzw9SlRzsdVbE3MXrFw0GfpJNicwfDNOMjYw/640?wx_fmt=png&from=appmsg)

其中，表示高档位正样本。

3.Quantization Regularization：引入量化正则项，以缓解 TensorRT 推理加速带来的浮点精度（Float）损失，二进制量化正则损失（Binary-Quant RegLoss）定义如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycxibHHa8lKIgdX23sMo1VlQj58OzcCJMy3tdia2uPNJcTEW1mRCZCd37g/640?wx_fmt=png&from=appmsg)

2.1.1 UniRank

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

在UniDex的新索引检索范式下，引入UniRank重构排序机制，释放语义检索潜力。

#### （一）语义编码

1.UniRank框架

UniRank 采用与 UniTouch 相似的双塔架构设计。二者的核心差异在于：UniRank 以提升语义匹配准确度为核心目标，将 Query 与视频的语义信息分别编码为多个 128 维稠密向量（Dense Vector），并执行 Token-level 细粒度交互。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycGByn73iafKeKCeN5aticDV7VLXt3wBKKXTBBiaXfm0oqZr3Nib7ATLRowg/640?wx_fmt=png&from=appmsg)

图 6 UniRank模型示意图

2.Token-level Interaction

通过拼接多组可学习 CLS 头，实现 Token-level 延迟交互，进而完成 Query 与视频的细粒度语义交互：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycWPPHqAs4RfbYQr2FZFHVp0s2K3ptuAVqBx9kQXayDEWZJ3SicrfYJew/640?wx_fmt=png&from=appmsg)

图 7 UniRank Token-level交互示意图

Token-level Interaction 驱动 Query 侧所有语义 Token 向量均参与最终排序得分的决策过程，强化模型的表征能力：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyychMvSyOHic1kwF2nR4qLFFFuSlVJz73OVZwxAGyHzdG7xDSUOFXnAJfQ/640?wx_fmt=png&from=appmsg)

（二）学习策略

1.Pointwise Relevance Loss：蒸馏精排模型的相关性得分，提升模型的相关性判别准确度。

2.InfoNCE  Loss：同UniTouch的对比损失，学习搜索链路序，提升排序能力。

2.2 实时检索

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

在线检索阶段，Query 侧经在线推理生成 SID 集合，系统实时下发语义倒排检索请求，经 UniRank 排序后得到最终检索结果。视频侧 SID 通过离线与实时两大通路进行更新，由此实现了从 Term-based 到 Model-based 倒排索引的完全替换。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyyc3libcicv6l9dkBZHREweG9XTBb2vtqamKgWoJEr9rQj4yf9siaZTsdbAg/640?wx_fmt=png&from=appmsg)

图 8 UniDex实时检索流程

2.3 实验效果

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

2.3.1 UniDex离线效果

UniDex在 RS 数据集上，Recall@300 较基线Sparse模型提升14.18%，MRR@10 提升10.02%，突破传统稀疏化检索依赖Term匹配的局限，同时可规避ANN检索复杂度高、资源需求大、对检索规模敏感的缺陷。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyycjpzib2zDib41TRyibTaOwicrK1xNWsm9YMHfuicEjQ7j8TyARxIpeQoMyBQ/640?wx_fmt=png&from=appmsg)

2.3.2 在线A/B实验

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycmYrIWYXRy8Y2XkOQ3IAt0QIvUZ9rriabqglo8yFljQNibU2VPiaEtz45Q/640?wx_fmt=png&from=appmsg)

UniDex 的表现均优于快手线上基准倒排召回，同时UniDex大幅降低系统资源消耗，降低计算成本，进一步改善用户体验。

**三、生成式创新 —— 直播垂搜，统一生成式 UniSearch**

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

直播搜索是快手重要的搜索流量来源，也是短视频应用场景中的新业务领域，为应对直播业务场景高时效性要求的挑战，快手搜索技术团队设计了统一的生成式搜索架构，提升用户体验并优化搜索效率。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyyciaox4sQThb99wHOjSXZtmtv40AiccYOsj9QSv4DNNfEsel9xeZBvGhpA/640?wx_fmt=png&from=appmsg)

论文链接：https://arxiv.org/pdf/2509.06887

3.1 技术创新

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

与以往依赖多阶段模型的级联系统不同，UniSearch 采用统一架构，在同一框架内完成端到端训练与推理，消除各阶段目标之间的不一致性，降低系统复杂度。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycydsBjTClJm0F5Os8HJXkzU5xh8IfaQJsibI0SNrQvwiavYH6RgwH4aIA/640?wx_fmt=png&from=appmsg)

图 9 UniSearch 结构整体框图

#### 3.1.1 UniTouch建模：真端到端

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycibCduDLUjTJ4LlkISmxAZv96OCLWbcBQ7s60s9TcorzHsRsYQfHeicMw/640?wx_fmt=png&from=appmsg)

         图 10 级联链路（MCA）& 现有生成式系统架构 & 统一生成式搜索 UniSearch 对比

先前的生成式搜推模型（如 OneRec）采用两阶段训练，item离散化表示和item生成任务，这会导致两阶段目标不一致。为此，设计了“真端到端”的训练架构 UniSearch，将 Search Generator 和 Video Encoder 统一到一个训练框架。

Search Generator 采用 “Encoder-Decoder” 架构，输入为搜索词、用户特征序列等。使用 <cls> 来表征 query 侧整体语义向量。Decoder 侧自回归地预测出视频的语义 ID。

Video Encoder，为每个视频学习潜在 embedding 表示和语义 ID。Encoder 的输入为视频侧特征，输出为Learnable Token对应的语义序列表征。同时Video Encoder有一个用于离散化的 VQ Codebook，用于将连续的Embedding 转化为语义ID。

通过联训 Search Generator 和 Video Encoder，UniSearch 能够缓解 item 生成和 item 表征之间的鸿沟，实现整个生成搜索框架的统一与连贯性。

####

#### 3.1.2 离线训练：残差渐进式

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycxbTiaZcxNfcQcnflRgJEVPmgUibxZwiaOUv5URbn7ByQz9gcnL6C9kxzg/640?wx_fmt=png&from=appmsg)

图 11 码本学习约束

1.残差对比语义学习

UniSearch 将传统生成式工作中的采用类似于 RQ-Kmeans 的残差聚类过程，建模到了语义学习的过程中：与采用两阶段残差聚类的残差量化方法（如 RQ-Kmeans）相比，该方法实现了端到端的训练，避免了由分步训练带来的目标不一致问题。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyyc3MIXgMW46QCE6NCE8hlfibuaNSEnZ2jV6s0wdBmFeu7gJ85j2eRyRpA/640?wx_fmt=png&from=appmsg)

公式中 sg(·) 代表梯度截断。

2.渐进式粗到细建模目标

query-video 残差对比学习的建模目标模拟了级联链路由“召回->粗排->精排”的漏斗结构，构建了一种层次化的语义刻画模式。具体来说 学习类召回的分档逻辑， 学习类粗排的分档逻辑，...,  学习更精细化的精排分档逻辑。

3.码本离散化学习

与依赖后聚类方法的工作不同，UniSearch 采用 VQ-VAE 方法，在训练过程中联合更新码本（codebook）。对于每个语义向量，VQ-VAE 编码器在可学习的码本中执行最近邻查找，获得量化后的 及其对应的语义 ，同时让量化向量和原语义向量 相互逼近。码本损失如下：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycVL2urskJktsffBLQpRdey28Fs66TwtMibG3AIiaPR5mCOBU6t3icWNaHg/640?wx_fmt=png&from=appmsg)

同时，引入了 SimVQ 策略，即在量化层之后增加一个线性层协同优化，避免了码本坍塌问题。这样，借助 VQ 模块，视频可以以完全端到端的方式被离散化为语义 ID，从而避免了离线聚类所带来的不一致性问题。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycYlMdviah8RPwibXiby5A6dM5vgY14tgyduHlvOibQxZnBeUibsVbRibWwkmQ/640?wx_fmt=png&from=appmsg)

图 12 生成式训练

生成约束较为常规，在这里额外采用了一种拒绝采样的训练策略，即根据标签判断出的低质量样本会被过滤掉，并且针对不同质量等级的样本，会相应地对其损失进行加权。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyyc2BT3Cuvt3QQ54siaq4OicicibmHzQficmleuicqZRSdTyQnbMCbR2hSaq9wg/640?wx_fmt=png&from=appmsg)

为不同档位的样本的权重。UniSearch 整体的训练目标为上述各个分量的加和，实现了 query-video 语义对齐、视频离散化以及生成的联合优化。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycUTvia2VrcZ3V2X584p5DMXonU75YPuYicTucHkbsOibHQBepWbloML0icg/640?wx_fmt=png&from=appmsg)

#### 3.1.3 在线训练：搜索偏好强化学习

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycOTBUqoKu6uLyjWGg2KBpuciaVC3krxUiahlSc2cbAQicQ4H6GTBzSDxYA/640?wx_fmt=png&from=appmsg)

图 13 奖励系统与 SPO

在离线训练结束后，UniSearch 线上模型通过接收当前搜索系统对生成结果的评估以及用户的真实反馈，将学习搜索偏好下的生成模式。据此，整个Reward系统包括 2 部分：（1）线上精排奖励；（2）用户行为反馈奖励。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycxicAEIMjjOqexnzcSpWGMsTod2aiafXtsnxTsbokZd488R3HuHTQPAxQ/640?wx_fmt=png&from=appmsg)

类似于 GRPO，UniSearch 应用了搜索业务感知的强化学习优化 Search Preference Optimization (SPO) 来进一步提升生成性能。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyychB5KL79esuOMnVgMD8MF5RErocxbE4iceNLYrnTmkqbRQvZypkGWzVw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyyctxtKJOauuQlVzvmoRqyIRfusPeWKibCCEq0ZupHtCGxS9Q4l5E9bBpQ/640?wx_fmt=png&from=appmsg)

#### 3.1.4 推理：动态Trie约束

直播搜索具有明显的时效性特性，在不同时刻，直播间的表征会发生剧变，这就需要对直播码本进行监听与实时更新。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycpyCLjEurEicyBudBmWdoTbiaIrP1nHyXpnbnVvur3xegiaVaYicMDHT7BA/640?wx_fmt=png&from=appmsg)

图 14 UniSearch 在直播搜索的实时链路应用

UniSearch 链路主要由 3 部分构成：

1. 生成模型：采用上文所述的“encoder-decoder”架构的模型，实时接受 Query 和上下文输入，产出码本概率分布；

2. 动态 Trie 树构建与搜索：首先构建码本生产服务，以 1 min 的时间窗口来更新直播间表征，实时生产直播间 id 映射到最新码本的数据流；动态 Trie 树模块实时监听数据流，更新当前有效直播间的码本路径；生成模型产出的码本概率分布，在动态 Trie 树上进行beamsearch搜索，保证了生成结果的合法性。

3. Reward System：实时地对生成模型的产出进行奖励，用于指导模型的在线训练。

3.2实验效果

![图片](https://mmbiz.qpic.cn/mmbiz_gif/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpOJU39ibq099jzBQWc58JpZFeNaCMpNorSSGqK5D0LMibVjPgjoPBYSvQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1&tp=wxpic#imgIndex=6)

3.2.1 离线结果

UniSearch 在离线评估中始终优于各项基线方法。在相同模型规模下，UniSearch-6 Layer 在 MRR 指标上超越其他 6 层基线，并在 Recall@300 上达到了接近 12 层基线的性能。这表明统一的训练目标不仅提升了生成结果的相关性，也显著改善了整体生成质量。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycnEYXsc8U7J6QqdhVra10UKlNOTTtQiaRibCTKdlXia8O3xIZbEibyIYPSw/640?wx_fmt=png&from=appmsg)

3.2.2 在线实验

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycHJ5RUicMYMP7mzxSg08uVpC6f5xXlDdJE7q8tbbSPJ45fHOGOmIkDkQ/640?wx_fmt=png&from=appmsg)

将 UniSearch 部署至在线直播搜索链路后，多项指标取得了显著收益。其中直播进间次数 +3.31% 为近两年来的最高提升。直播搜索的换Query率 -0.382% 也取得了明显降低，标志了直播搜索质量的有效提升。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycrxqJDaBMI24wh9iaSBldZxtUoHyZLH3gEriaAqagibzTIjJwpYscEnoYg/640?wx_fmt=png&from=appmsg)

图 15 分视角下探分析

对进间次数进行下探，发现新用户贡献了 58.73% 的提升，占总增量一半以上。这表明 UniSearch 返回的结果对新用户吸引力更高，具有明显的拉新潜力。

四、结语

![](https://mmbiz.qpic.cn/mmbiz_svg/ZqDaDiccbgkjkXh51mrAMoT3ZCACkYnlug8cUETdh9Day9fNPrUxPnf16aImK9XpkTCvMufrR9HiaPqbFKCRMxoMlZmAlwZCog/640?wx_fmt=svg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

快手搜索团队结合大模型技术，以视频 SIDs 为基础，探索下一代工业搜索系统，通过判别和生成双范式的共同努力，推动搜索技术的革新。具体来说，判别式方法通过在查询（query）侧和文档（doc）侧之间实现 SIDs 的精确匹配，变革了传统的倒排索引方式；生成式方法则通过直接生成从查询到文档的 SIDs，创新了一种真端到端生成式搜索新范式。快手正积极探索，大胆求证，立足技术前沿，为用户提供更智能和高效的搜索体验。

- END -

欢迎加入

![](https://mmbiz.qpic.cn/mmbiz_png/kTR2HQBMfv2z7RLABU4sI66ckQLJVCVpF09GTXcEcG4Fy9SdWsPp2icyibcRsickibvTSQXgITrJPOF9bApGEbyZvg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=21)

**「我们是谁」**

我们是快手社科线-搜索技术部，作为快手算法核心部门，始终站在大数据与人工智能技术发展的前沿，致力于将大模型（LLM）技术与海量数据深度融合，打造行业领先的智能搜索平台，持续推动用户体验与技术能力的协同进化。部门业务覆盖电商搜索、视频搜索与AI搜索等多个核心方向，聚焦于构建精准、高效、智能的新一代搜索系统。

### **「热招岗位」**

### 💼 搜索算法工程师

（1）参与综合短视频，直播，电商，本地，社交和多语言等搜索业务，用大规模机器学习，强化学习，多模态预训练等技术提升搜索质量，用户留存和点击率等核心业务指标；

（2）负责搜索query 意图分类，query 表征，query推荐，视频内容理解&多模态表征，多模态语义召回和相关性等搜索核心技术，提升搜索用户渗透率和相关性；

（3）负责搜索用户行为分析，语义和行为混合检索，多序列&多任务粗排，精排，重排等搜索排序技术，提升搜索质量和内容消费指标；

（4）负责搜索生态和机制，参与搜索混排，多目标优化，异构内容混排，短期和长期目标平衡，冷启动等搜索机制和算法。

### 💼 电商搜索算法工程师

（1）参与亿级用户规模的电商搜索优化，提升电商搜索场景的GMV、购买用户数、点击率、转化率等核心指标，提升用户电商搜索购物体验，促进生态良性发展；  
（2）参与机器学习与深度学习算法的核心研发工作，对搜索全链路进行建模优化，包括但不限于召回、相关性、粗排、精排、机制等，深度进行序列建模、迁移学习、强化学习、对比学习、多模态大模型等的算法和系统研发；  
（3）针对海量用户行为数据，提供基于分布式计算的算法解决方案，大幅提升算法计算规模和性能；  
（4）参与搜索推荐机制的顶层设计，结合业务战略，优化电商流量结构和GMV结构，促进电商生态的健康发展。

### 💼 搜索推荐算法工程师

（1）参与亿级用户规模视频推荐和交互产品推荐，提升用户体验、时长、留存等核心指标；  
（2）分析海量用户行为数据和视频数据，挖掘用户侧和item侧有效特征，提升推荐效果；  
（3）参与机器学习、深度学习领域研发工作，不限于网络模型设计与优化；  
（4）探索多模态大模型的前沿技术，通过加强视频和文本的理解，提升产品体验和业务效果。

### 【任职要求】

1、硕士及以上学历；  
2、熟悉自然语言处理、数据挖掘、机器学习等，有较强数据分析能力；  
3、熟练使用C/C++或Python。  
加分项：  
1、有搜索、推荐、广告、大数据等大型项目经验优先

2、熟悉大语言模型、强化学习相关技术  
3、国内和国际顶级会议发表论文的作者优先。

### 【投递方式】

### 投递简历至邮箱：HR直投 xiaoyubo03@kuaishou.com 或 relevance@kwai.com

”

【相关阅读】[![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5QzyycptBHZdux8HiaSxgO5n8s6CyoibxJqK5Ir1LyXy4ANXmjHXEUrqOZhvWA/640?wx_fmt=png&from=appmsg)](https://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247498243&idx=1&sn=16d56fe2da2ef00b8f7ef3324634cfee&scene=21#wechat_redirect)

[![](https://mmbiz.qpic.cn/sz_mmbiz_png/ZxDY5TMPs0HxGQ5FFtgfvZpk3A5Qzyycwlyg6oia92VicyKaY4foPRBqxKicaTRhxSnsAv2icxtiayEVY9mvqCH8OmQ/640?wx_fmt=png&from=appmsg)](https://mp.weixin.qq.com/s?__biz=Mzg2NzU4MDM0MQ==&mid=2247498146&idx=1&sn=4fa3ebecc5ac44102a2c86b842a92293&scene=21#wechat_redirect)