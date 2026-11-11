---
title: 'HyFormer: 抖音搜索提出序列与特征交叉统一建模的排序模型'
company: DataFun
tag: 排序
date: 2026-02-13
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247775040&idx=2&sn=781838b73b542b62e4fdf8a9c57b37d7&chksm=fbdb012cccac883a92703eb950a3b0d32e363510e1d424904a51a3bdc7fb700a8239b97312fa#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhTia191MRUMDiacXVJ4Y3YS8Xibicn0O9liacYp7Aia6iaYKqDSicvuWPKibvibUGXGET00pxW6Jiaicn07KRGjQ/640?wx_fmt=png&from=appmsg)

**TLDR：**当推荐系统向着超长用户行为序列和超高维异质特征迈进时，现有的模型架构却暴露出了先天不足。大家惯用的“先序列建模，再特征交互”范式（比如用LONGER序列建模 + RankMixer特征交互），虽然有效，但本质是晚融合的设计，成了模型表达能力与扩展性的天花板。

基于上述问题，字节抖音搜索团队在业界首次提出序列建模与特征交互统一的混合Transformer框架——HyFormer，将推荐建模任务构建为一个特征交互与序列建模交替优化的过程，在保持计算效率的同时显著提升了模型的表达能力和Scaling效率，实现了抖音搜索业务指标与用户体验的双重提升。

![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOxT2wPNDiaUhH7sewDdgWjCFrmGQklVwTA6x194BDx282mdEBSwSLLRA/640?wx_fmt=png&from=appmsg)

论文：https://arxiv.org/abs/2601.12681  
关键词：排序模型、序列建模、特征交叉

## 一、研究背景

传统的推荐系统排序模型通常采用如下“两阶段”的建模范式：

1. **序列建模：** 用DIN/LONGER等结构把用户行为序列提取压缩成若干个表征。
2. **特征交叉：** 将上一步提取的序列表征与其它特征用DCN/RankMixer等结构进行交叉。

![以最经典的序列建模方法 DIN 为例，整体模型结构符合“先序列建模，后特征交叉”的“两阶段”范式](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOcF36r2WTYpzkWK9qZXURXYobQXtxrWnJTONcjAVtE4h19ZzicAbjYKA/640?wx_fmt=png&from=appmsg)

以最经典的序列建模方法 DIN 为例，整体模型结构符合“先序列建模，后特征交叉”的“两阶段”范式

虽然该范式在业界的推荐模型得以广泛应用，但也带来了明显的局限性：

* 序列建模时，Query侧往往只包含少部分信息（通常只是Target Item关联特征），而大量其它输入特征直到序列被压缩完才参与交互，从而无法使序列模块提取全面准确的信息。
* 由于特征交叉模块仅对压缩后的序列表征进行建模，以加深或加宽的方式增加参数量难以直接受益于序列建模模块，从而导致模型Scaling效率较低。

针对上述问题，我们有以下思考：

* 不应该把“序列建模”和“特征交叉”割裂开来，而应该让二者“互帮互助”——不仅需要“序列信息”来增强“特征表达”，更需要“全局上下文特征”来指导“序列信息的提取”。
* 此外，在业界实际应用的模型中，往往会有多条不同序列输入（例如搜索历史/Feed流/互动序列），强行合并进行统一建模（如OneTrans的做法）会干扰模型，应该对它们独立建模。

## 二、方法简介

针对上述问题，我们提出了HyFormer模型，整体架构如下图所示，主要包括Query Generation, Query Decoding和Query Boosting等三个部分，并通过支持多序列建模的HyFormer模块结合起来。

![HyFormer架构概览。该架构引入了从序列建模中原始候选物品衍生而来的global token，通过基于 MLP-Mixer 的特征交互方式提升长序列的检索表征能力，重新审视了长序列建模与特征交互的作用。该架构借助查询解码模块与查询增强模块的交替执行，将长序列表示建模任务构建为一个交替优化的过程。](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOd0rZf71Wp4qT2osf7bVkTNmZ0xOXYyicltLM6yLBAKJnMepjqBYZEYQ/640?wx_fmt=png&from=appmsg)

HyFormer架构概览。该架构引入了从序列建模中原始候选物品衍生而来的global token，通过基于 MLP-Mixer 的特征交互方式提升长序列的检索表征能力，重新审视了长序列建模与特征交互的作用。该架构借助查询解码模块与查询增强模块的交替执行，将长序列表示建模任务构建为一个交替优化的过程。

### 2.1 Query Generation

该模块的输入由 1️⃣ 按照语义分组的全部非序列特征 (NS Token)，以及 2️⃣ 带side info的序列特征 (Seq Token) 两部分组成。其中，我们将NS Token与不同序列的Seq Token的pooling进行拼接，并通过轻量的MLP网络映射成包含全面context信息的初始query表征。

值得注意的是，以上生成的是最底层初次序列建模用到的query，而更深层的HyFormer结构涉及到的query不会通过上述方式产生——相反，每一层都会复用前一层的query，并将更深层的交叉注意力输出作为更新后的query，用以检索长序列。随着层级加深，query能够携带逐步丰富的语义信息。

### 2.2 Query Decoding

除了在模型底层获取初始query表征Q后，我们也需要将序列里的各个元素映射成后续序列建模所需的K/V. 这里我们给出了三种可选方案：

1. Full Transformer Encoding：对序列先进行self-attention编码，使所有元素综合容纳互相的信息。
2. LONGER-style Efficient Encoding：在序列前面拼接多个 (通常远小于序列长度) 的additional token作为query，通过cross attention来抽取序列特征信息。
3. Decoder-style Lightweight Encoding：直接对序列所有元素映射 (例如使用SwiGLU) 成最终的K/V.

在得到包含target item在内丰富信息的query表征和序列所有元素的key/value表征后，我们会在HyFormer的每一层通过Cross-Attention的方式进行query decoding. 该步骤能够进一步将上下文信号注入到具备序列感知能力的query表征中；随后，解码得到的query (对应为每条序列分配的Token) 会供后续的交互模块与增强模块使用。

### 2.3 Query Boosting

经过上一步query decoding后，对应的token已包含了序列信息，但其与其它大量非序列特征的交叉仍未被充分挖掘（虽然最初我们将所有NS Token拼进了初始query里，但这远远不够）。query boosting模块则解决了这一局限。

具体来说，我们可以把所有非序列Token (例如对所有特征embedding拼接后进行切分得到) 和序列Token (每条不同序列对应不同的Token，其初始值即 query generation+decoding后输出) 拼接成一个的张量作为该模块输入，利用基于MLP-Mixer的结构将其进行mixup+pffn/smoe交互。由于残差机制的存在，我们得以在充分融合解码出来的序列信息和原始的非序列特征同时，保留交互前的较原始语义，使得query boosting成为一个重要且高效的“增量模块”，通过多层堆叠不断在前序表征基础上更新更多信息。

![从上图的 Mixup 以及PerToken FFN/SMoE 过程中不难看出，使用基于Mixer的架构能充分使序列Token和非序列Token 融合，而残差设计则能保证原有信息保留同时不断做有用的信息增量](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOUdFu2licYMG7cGcE6747ysichfrgAHEnsqUz4nGZ8cjDynAsibgUSF1Ng/640?wx_fmt=png&from=appmsg)

从上图的 Mixup 以及PerToken FFN/SMoE 过程中不难看出，使用基于Mixer的架构能充分使序列Token和非序列Token 融合，而残差设计则能保证原有信息保留同时不断做有用的信息增量

### 2.4 HyFormer模块

HyFormer 模块由多层网络堆叠而成，每一层均包含一个Query Decoding模块，其后衔接一个Query Boosting模块。在每一层中，语义查询向量通过交叉注意力机制与长行为序列进行交互，得到的序列感知表征会被进一步优化，作为后续更深层网络的输入。

通过堆叠多层该结构，HyFormer 逐步优化语义query向量，使得深层网络能够借助表达能力不断增强的表征，对长序列进行抽象建模。HyFormer 最顶层的输出会被输入至下游的MLP，以完成最终预测。该设计能够在长序列表示建模任务中，高效、灵活地将异构非时序特征与长行为序列相融合。

![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOGnjRmE1zMshRGkCPoMnYibXWtQmePicX8zKdtNKJk6tUhWqazM64SycQ/640?wx_fmt=png&from=appmsg)

## 三、实验结果

### 3.1 效果对比

在抖音搜索业务上进行验证，有三条序列，包括最长3000的长序列、top 50的搜索序列和top 50的feed序列，global token包括非序列token是13个+三个序列mean pool的token，在64卡GPU训练。我们比较了两阶段 (先序列建模后再和非序列token交叉) 和统一建模(序列和非序列统一建模) 两类模型，其中本工作提出的HyFormer模型取得最好的结果，且计算量不大。

![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOqd780mQsfAibv8ZvI6ibBj2a0rZ7ZzTn9QufBtmuhW8uYoLibYJLfPZsA/640?wx_fmt=png&from=appmsg)

### 3.2 消融实验

如下表所示，1️⃣ query包含三部分：全局非序列特征、序列pool token、target item信息，移除全局非序列特征或者序列pool token都有损；2️⃣ Query boost模块去掉global token也有损，下面BaseArch是Longer+RankMixer结构，整个改了结构；3️⃣ 多序列merge效果也有损。

![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOWwl5YLMWzj0Px2bbqfQpwSwsNIpkBxV4ev4OBTDiaIN6oUwvGLNFXdQ/640?wx_fmt=png&from=appmsg)

### 3.3 Scaling分析

我们选取的base是LONGER+RankMixer.

* 随参数量和计算量的scale up，HyFormer更优。
* 随序列长度变化，HyFormer更优。

![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOj4ibc1C80HNic5EAaFESjJdJlca4VrqSicgpoMPQfdBee69iaZR2NXVOqg/640?wx_fmt=png&from=appmsg)![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOShIbg03D33beMU3qmymNaWt5xUKruicaIpfJObvb7p8ZHbia7p8JZmKQ/640?wx_fmt=png&from=appmsg)

### 3.4 A/B指标

在抖音搜索场景中，人均观看时长、完播率、换query率均有收益。

![](https://mmbiz.qpic.cn/mmbiz_png/gUs5jjsU4qNXE5MQA0RY3zKQXBib7QSXOTtA5QQyJwZM4K8opibHPwo0VSd4bDQKRs4lFQ00hSm2MsjianDagQx5A/640?wx_fmt=png&from=appmsg)

## 四、总结与展望

本工作提出的HyFormer架构是业内首个提出“序列建模”与“特征交互”统一联合交替建模的框架。从序列建模的角度来看，该过程对应一种迭代优化流程：基于全局标记对长序列进行解码，再通过跨特征交互强化全局标记，二者交替迭代。这一设计为更全面的序列建模与特征交互提供了新颖且高效的框架，同时也为多序列建模提供了灵活的范式。大量离线与在线实验验证了将单向信息流升级为双向协同进化范式的优越性，也为未来工业界长序列表示建模任务提升了扩展上限。

我们是抖音搜索算法团队，是国内当前最领先的图文/短视频搜索业务，我们正在热招 社招 / 校招 / 实习 的同学，共同打造下一代 AI 搜索引擎。

base地：北京/杭州/上海

我们的技术方向：

* 排序大模型：探索个性化大模型、多模态大模型、生成式大模型、百万超长序列等前沿技术，不断突破技术边界，重新定义下一代搜索大模型范式，让排序更精准、更贴合用户需求。
* 机制策略：深耕LTR等排序策略、多业务重混排、流量分发机制等，优化搜索全链路效率，平衡多场景业务需求与用户体验，实现业务价值与用户价值的双赢。
* 召回技术 / 相关性技术 / 生态优化 等

欢迎加入我们，联系方式：wushikang@bytedance.com / hsy-24-6666(微信)，邮件名：[社招/校招/实习][方向][base地][姓名][学校]

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgclYstBqCYcZibcGDEVGDPalNpPJ5HKWHicUXms7ZltkDN5QIqicGR9WvtSy2CbNRlsqh1fbCibOQAicA/640?wx_fmt=png&from=appmsg)

往期推荐

[Anthropic最新2026趋势报告：人类最大一次编程革命势不可挡](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247775031&idx=1&sn=75a7e64792db2a1e1286b6005224d476&scene=21#wechat_redirect)

[RAG 落地全干货深度分享：从“效果不理想”到生产级 RAG 系统的进化之路](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247775031&idx=2&sn=519412ee9dcfd3666d9d413e7eb653d6&scene=21#wechat_redirect)

[Palantir本体论：你的数据中台失败，恰恰因为太关注“数据”本身](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247775031&idx=3&sn=db49974943e8ccaad54d1bae1add611c&scene=21#wechat_redirect)

[治理体系 + 数据上新！UltraData 数据分级治理体系发布，以科学治理赋能 AGI](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774992&idx=1&sn=9e959a9ff10f9d350bc2b9983ce6bf68&scene=21#wechat_redirect)

[OpenClaw一战封神，给大家分享6种官方不会告诉你的神级技巧。](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774987&idx=3&sn=993820dde35955d24bd968748ea063a1&scene=21#wechat_redirect)

[PLTR 封神之夜！Q4营收狂飙70%，CEO盛赞“科技界十年最佳业绩”](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774910&idx=2&sn=1058327974934a3bce438eec15c3fd03&scene=21#wechat_redirect)

[全网首份Clawdbot研究报告:《OpenClaw:AI 从聊天到行动》](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774930&idx=3&sn=7d673946ef025ed3e56fda8634820d46&scene=21#wechat_redirect)

[万亿市值一夜蒸发！Claude Cowork血洗全球软件业，老黄急了](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774942&idx=1&sn=ce71f7776f8d66bc91a25be4d74c7778&scene=21#wechat_redirect)

[AI记忆正成为新操作系统：检索已过时，生成式记忆才是未来](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774942&idx=3&sn=d801e32361560a3446f428478dbe246b&scene=21#wechat_redirect)

[OpenClaw一战封神，给大家分享6种官方不会告诉你的神级技巧。](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247774873&idx=1&sn=c76ad2385de8b2896d431454cdeb929c&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640)