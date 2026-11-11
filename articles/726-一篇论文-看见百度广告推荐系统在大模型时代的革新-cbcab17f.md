---
title: '一篇论文，看见百度广告推荐系统在大模型时代的革新'
company: 百度
tag: 广告
date: 2025-04-08
url: https://juejin.cn/post/7490458997540421647
account: 
origin: harvest-202607
---
# 一篇论文，看见百度广告推荐系统在大模型时代的革新

[百度Geek说](/user/4186596000416094/posts)

2025-04-08
  
417
 
阅读14分钟

   

我们见证了 DeepSeek R1，用强大的推理能力再次点燃 AI 智力增长的火箭。

在上个星期，OpenAI 给 GPT-4o 的一波图像生成更新又让全网陷入了梗图、甚至玩梗视频制造的火热氛围中。

![](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/939bbe4a3c764e4fa08883f57c8fe5cb~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=PE%2Fkhpxg79zsfdxiMfKFDhDFSlk%3D)

用 GPT-4o 渲染过的《星际穿越》电影片段。

AI 的「想象力」一次又一次震撼着我们，基于先进大模型的应用正在越来越多的领域引发革命，被改变的也包括科技领域本身。

比如，生成式 AI 正在改变人们获取信息的方式。很多人认为，大型语言模型（LLM）既然强于生成和推理，那么应该也能从用户的历史行为中洞察出深层次的兴趣，进而为推荐系统找到全新的可能性。

既然生成式 AI 能通过已知上下文预测生成新内容，那么已知一些人们感兴趣的内容，AI 应该也可以预测出他们的下一个兴趣点。这个预测的内容可以是一篇文章、一段视频、某个品牌的商品或是 App 上的服务。

近日，百度推荐广告团队在广告生成式推荐取得了新成果，其构建的生成式 AI 推荐系统实现了前所未有的效果。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/26e2d43b12d943bca578bd50ffbfc4c5~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=JmYiKTA3BMMGLd9SG8DabYVsfus%3D)

* 论文标题：Sparse Meets Dense: Unified Generative Recommendations with Cascaded Sparse-Dense Representations
* 论文 ArXiv：[arxiv.org/pdf/2503.02…](https://link.juejin.cn?target=https%3A%2F%2Farxiv.org%2Fpdf%2F2503.02453 "https://arxiv.org/pdf/2503.02453")

在科技行业中，推荐系统虽不如图像生成、代码生成那样具有极高的讨论度，但一直是数字生态举足轻重的一部分。它在电商平台、视频 App 和社交网络上广泛出现，是提供符合用户偏好个性化内容的核心技术。

ChatGPT 推出以来，生成式检索（Generative Retrieval）逐渐成为了推荐系统领域最热门的研究方向。与传统的序列推荐方法不同的是，生成式模型可以根据用户的行为更加直接的进行预测，由 AI 模型处理复杂的用户 - 商品交互，可以提供推理和小样本学习等新能力，大幅提高推荐准确性和多样性。

尽管把生成式 AI 引入推荐系统的创新已有不少，但与序列密集检索方法相比，生成式检索方法仍然面临一些挑战，比如它们往往难以进行细粒度相似性建模。

谷歌的 TIGER 是推荐系统生成检索的知名方法，如图 1（左下）所示；百度则新提出了级联组织双表征生成式检索（Cascaded Organized Bi-Represented generAtive Retrieval，COBRA），这是一个将生成式和密集检索高效融合的框架。图 1（右）展示了 COBRA 的推理范式。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/9a36495a79c249ddac9ef3626aab0598~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=3F5GJ2TelQ8l8x9Hwnua9PNUdic%3D)

COBRA 研究的主要贡献如下：

* 级联双表示的检索框架：COBRA 作为一种新型生成式推荐框架，可在生成稀疏 ID 和稠密向量之间交替。通过将稠密表示合并到 ID 序列中，COBRA 弥补了基于 ID 的方法固有的信息损失。使用稀疏 ID 作为生成稠密向量的条件可以降低稠密表示的学习难度。
* 端到端训练可学习的稠密表示：COBRA 利用原始特征数据作为输入，通过端到端训练生成稠密表示。与静态嵌入不同，COBRA 的稠密向量是动态学习的，可捕获语义信息和细粒度细节。
* 生成过程由粗到细：在推理过程中，COBRA 首先生成稀疏 ID，然后将其反馈到模型中以生成精细的稠密表示，从而提取细粒度兴趣表征。此外，该研究还提出了 BeamFusion 来实现推荐多样性和精度的灵活可控。
* 全面的实证验证：通过对多个基准数据集的大量实验，研究证明了 COBRA 在推荐准确率方面的表现优于现有的 SOTA 方法，验证了 COBRA 在推荐任务中真实有效性。

## 01 生成式检索 几波技术演进

其实，在形成如今 COBRA 方案之前，百度研究团队针对广告场景中的生成式推荐任务，经历了多个阶段的技术探索，并针对暴露出来的技术缺陷持续优化与完善。

在生成式推荐任务中，大模型要预测的 item 是综合体（如广告标题、品牌、多模信息等）⽽并⾮简单的 token。因此，1）如何对 item 进行表征，2）基于表征进行序列建模是生成式推荐的两个核心问题。

最开始，百度采用了「纯⽂本表征 + LLM 建模」的方案，直接利用 LLM 进行推荐。通过标题、落地页等文本来表征 item，虽然可以辅助理解用户意图、提升可解释性，但超长的输入导致了巨大的资源和性能开销，运行成本较高。随后尝试通过短语来表征 item，但短语很容易出现信息压缩过度、表达不全的情况，难以全面描述 item 的各种属性。此外，item 之间的序列关系偏重兴趣协同而并非单纯的语义关系，与 LLM 建模的语义关系存在着鸿沟。

在意识到无法简单的直接使用现有方法后，研究团队开始考虑对 item 进行压缩表达，全面满足性能、信息完备、item 关系建模的要求。

因此，研究团队形成了「稠密表征 + 对⽐学习度量」的方案，核心在于将 item 表征为稠密向量。为此，他们引入了一个编码器逐个对 item 内容进行编码，使得 item 序列转变为一组向量序列并输入到一个 Causal Decoder 中；接着通过 Next Item Prediction 的方式完成模型训练，在训练中引入对比学习，使得编码器、解码器能够同步更新。在推理阶段，算法通过编码器输出 item 向量来构建索引，并通过向量序列输入到解码器中获取用户表征，最终完成 ANN 召回。

这一方案的优势在于表达能力强，可以完整利用 item 原始信息，对比学习保证了端到端训练，进一步建模序列中隐含的协同信息。虽然 item 信息利用和序列关系建模两大关键问题得到了有效解决，但仍然是在较大稠密空间上建模，缺少了兴趣探索过程，建模复杂度并未降低。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/9becd3dc70cf4c7e972dc56312457c0f~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=CUX5J42fXc5YOM7FR3z0LqVK9f0%3D)

「稠密表征 + 对⽐学习度量」方案概览。

接下来，研究团队受到谷歌 TIGER 的启发，尝试了「稀疏表征 + 稀疏 ID ⽣成」的方案，通过稀疏 ID 来表征 item。

完整的实现过程是这样的：首先通过商业预训练模型对广告特征进行嵌入，然后使用残差量化变分自编码器（RQ-VAE）将嵌入向量量化为带层次结构的 ID Tuple（如 L1、L2、L3），最后将 ID 序列输入到 Causal Transformer 并通过下一个 ID 预测来建模序列。在推理阶段，在给定行为序列的情况下，模型可以通过自回归方式来生成下一个可能的广告 ID。

稀疏表征的引入充分发挥出了「嵌入 + 量化」的作用，将 item 转化为 ID，使模型在压缩空间中学习用户兴趣转移，尤其适合高度个性化推荐场景中的「千人千面广告推送」。然而，受限于相互隔离的「嵌入、量化、序列建模」，不可避免地出现了信息损失，导致对用户偏好的精细变化捕捉效果较弱。

在尝试了以上技术方案之后，研究团队认识到了单一表征方式难以同时兼顾粗粒度类别信息和细粒度特征信息的局限性，提出了 COBRA 框架，通过级联方式融合稀疏 ID 和稠密向量表征，形成了「稀疏 - 稠密级联表征 + ⽣成度量⼀体化」方案，大大增强了模型的灵活性和适应性。

## 02 COBRA 框架的四大创新

下图为 COBRA 的整体框架，在集成了级联稀疏 - 稠密表征和由粗到细生成之后，实现了当前 SOTA 级别的推荐性能。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/d576b9f2383e48eca10b20e403d6750d~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=hYgQg68sl8537wKv2b%2B8cMjJVDQ%3D)

一是级联稀疏 - 稠密表征。

过程中，级联表征将稀疏 ID 和稠密向量集成在一个统一的生成式模型中。对于每个 item，它的稀疏 ID 和稠密向量组合起来以形成级联表征。这样做可以兼顾稀疏与稠密表征的优点，获得更全面的 item 特征，其中稀疏 ID 通过离散约束提供稳定的类别基础信息，稠密向量确保模型捕获高级语义和细粒度细节。

二是交替学习的序列建模。

得益于级联表征的方式，方案中将目标 item 的概率分布建模分为两个阶段，以利用稀疏与稠密表征的互补优势。COBRA 没有选择基于历史交互序列来直接预测下一个 item，而是转为交替预测稀疏 ID 和稠密向量。具体来说，采用 Causal Transformer 统一生成式模型接收级联表征作为输入，从而捕获序列依赖关系。

三是端到端训练。

COBRA 的端到端训练过程旨在同时优化稀疏和稠密表征预测。训练过程由一个复合损失函数控制，该函数结合了稀疏 ID 预测和稠密向量预测的损失。稀疏 ID 预测损失在基于历史序列预测下一个稀疏 ID 的过程中，保证了模型的效率；稠密向量预测损失用于细化稠密向量。同时，该稠密向量由端到端的可训练编码器生成，并在训练过程中进行优化，从而适应不同推荐任务的特定需求。

这种双目标的损失函数可以实现均衡的优化过程，使模型在稀疏 ID 的指导下动态地细化稠密向量，同时端到端的训练方法可以捕获高级语义和协同信息。

最后是由粗到细生成。

作为一种高效的策略，这有助于模型解耦与模块优化，并在保证候选多样化与覆盖性的同时进一步提高精度。在推理阶段，COBRA 采用由粗到细的生成过程，先生成稀疏 ID，后细化稠密向量，如下图 3 所示。

具体地，首先基于⽤户历史交互序列，使用 Transformer 解码器建模的 ID 概率分布，并利用 BeamSearch 算法生成下一个 item 的稀疏 ID。然后，将⽣成的稀疏 ID 追加到输⼊序列中，作为条件进⼀步⽣成对应的稠密向量，捕获 item 的细粒度特征。同时引⼊ BeamFusion 机制，并结合 BeamSearch 和近邻检索分数，在确保推荐精度的同时保证召回⼴告候选的多样性。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/0b34dad185484c248f109056f71b4a25~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=hNzvOwbPx9neNAzwXJ%2FUcnAPubs%3D)

由粗到细的生成过程。

COBRA 框架为生成式推荐领域提供了一个的新范式。

## 03 多场景性能提升 已实际应用

实测效果如何？研究团队使用公开和工业数据集对 COBRA 框架进行了全面评估，并重点展示了 COBRA 提升推荐准确率和多样性的能力，并通过离线和在线评估来验证实际效果。大量实验表明，COBRA 优于目前业内最先进的方法。

在公开数据集上，研究团队使用了 Amazon Product Reviews 数据集，并重点分析了「Beauty」、「Sports and Outdoors」以及「Toys and Games」三个子集。

实现结果如下表 2 所示，其中在「Beauty」数据集上，COBRA 的 Recall@5 和 Recall@10 相比之前的最佳模型 TIGER 分别提升了 18.3% 和 11.9%；在「Sports and Outdoors」数据集上，COBRA 的 Recall@5 和 NDCG@10 相比 TIGER 分别提升了 15.5% 和 18.8%；在「Toys and Games」数据集上，COBRA 的 Recall@10 和 NDCG@10 相比 TIGER 分别提升了 24.5% 和 19.2%。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/e9e492a497df4130a930ba0c020e2981~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=%2FLm50E1KPVmmBWsOiFL1LpN5i18%3D)

对于行业数据集，研究团队采用了 Baidu Industrial 数据集，它基于百度广告平台上的用户交互日志构建，涵盖了列表页、双栏、短视频等多种推荐场景，包含了 500 万用户和 200 万条广告，全面展现了真实用户行为和广告内容。

为了验证本文策略的有效性，研究团队对 COBRA 以及移除稀疏 ID 的变体 COBRA w/o ID、移除稠密向量的变体 COBRA w/o Dense 以及移除 BeamFusion 的变体 COBRA w/o BeamFusion 进行了比较。结果如下表 3 所示，相较于三种变体，COBRA 均体现出了优势，从而验证了该框架中各个组件的有效性。

在 K=800 时，COBRA 的召回率为 0.4466，相较没有稀疏 ID 的变体提升了 43.6%， 相较没有 BeamFusion 的变体提升了 36.1%。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/689593c52157465daaa2b60e657dafbe~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=WvyhaYDRDLyacHaFomVISrOlytU%3D)

为了评估 COBRA 的表征学习能力，研究团队对广告稠密嵌入展开相似度矩阵分析，如下图 4 所示，展现了 COBRA 模型的类别内聚性和类别间分离性。相反，没有稀疏 ID 的模型变体显示出较弱的类别间分离性（图 4b），加入稀疏 ID 则可以增强内聚性和分离性（图 4c 差异矩阵定量分析）

这意味着 COBRA 不仅能够将同⼀类别的项目紧密地聚集在⼀起，还能将不同类别的项⽬有效地区分开来，从而在推荐时能够更精准地捕捉⽤户的兴趣点。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/1fdc4b630087421d80c37104c4458415~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=LD%2BAP6LLscDG2q9RjyvDvkCN0vE%3D)

进一步的可视化广告嵌入分布验证了 COBRA 的嵌入能力。通过随机抽取一万个广告，研究团队观察到了不同广告嵌入形成了明显的聚类中心，如下图 5 所示。我们可以看到，紫色、青色、浅绿色和深绿色聚类主要分别对应小说、游戏、法律服务和衣物广告。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/1a664e76ab0c40719892b91cef96cf09~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg55m-5bqmR2Vla-ivtA==:q75.awebp?rk3s=f64ab15b&x-expires=1785205820&x-signature=OyVJuPzVacwJ%2FtoUeD9i%2BoT8s04%3D)

由于与大量业务直接相关，推荐系统是一个很「卷」的领域，在百度的研究中，工程师们把 COBRA 最终策略投放到真实生产环境上跑了一圈，在 A/B 测试中实现了转化率增加 3.6%，ARPU（平均每用户收入）增加 4.15% 的好成绩。

这些业务指标提升表明，COBRA 不仅在离线评估中表现出色，还能够在实际生产环境中带来可衡量的商业价值，目前该方法在百度广告推荐业务中已经全量上线。

## 04 结语

经过一系列提升和改进，生成式 AI 已经可以做到表达清晰、预测准确，并在百度的广告推荐系统中实现了应用。与很多领域一样，推荐系统正在向着需求个性化的方向快速发展，而在这个方向上，AI 提供的解决方案已经展现出了独特的优势。

对于普通人来说，在各种 App 上，大模型驱动的推荐系统可以帮助我们获取更多有用的内容，让信息流更加聪明。

对于科技公司而言，或许在几年之内，AI 驱动的业务就可以从目前的局部智能化进化到「需求预测 - 生产调度 - 仓储物流 - 营销交付」的全流程智能化阶段。

未来，AI 应用的深度将决定业务的增长速度。

------END------

**推荐阅读**

[前沿多模态模型开发与应用实战3：DeepSeek-VL2多模态理解大模型算法解析与功能抢先体验](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247604395%26idx%3D1%26sn%3D39b4acb4b0508d5bac24db98c0763d1d%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247604395&idx=1&sn=39b4acb4b0508d5bac24db98c0763d1d&scene=21#wechat_redirect")

[秒哒首发即爆发！上线首日吸引2万用户，打造3万应用！](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247604386%26idx%3D1%26sn%3Da5256f37cf68952afbd20778f1415cf1%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247604386&idx=1&sn=a5256f37cf68952afbd20778f1415cf1&scene=21#wechat_redirect")

[秒哒，全面开放！](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247604377%26idx%3D1%26sn%3Db5e5cc97bbab7a5ca7144a25278ef884%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247604377&idx=1&sn=b5e5cc97bbab7a5ca7144a25278ef884&scene=21#wechat_redirect")

[图灵数据洞察平台-TDF（Turing Data Finder）](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247604365%26idx%3D1%26sn%3D333509ead2f5b49778c26db98b36f820%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247604365&idx=1&sn=333509ead2f5b49778c26db98b36f820&scene=21#wechat_redirect")

[两连发！文心大模型4.5及X1，上线千帆！](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzg5MjU0NTI5OQ%3D%3D%26mid%3D2247604333%26idx%3D1%26sn%3D4021da1c6fb035906fd747487bbb8a23%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=Mzg5MjU0NTI5OQ==&mid=2247604333&idx=1&sn=4021da1c6fb035906fd747487bbb8a23&scene=21#wechat_redirect")