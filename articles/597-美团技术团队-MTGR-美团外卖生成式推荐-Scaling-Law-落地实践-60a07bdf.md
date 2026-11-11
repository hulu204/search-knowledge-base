---
title: '[美团技术团队] MTGR：美团外卖生成式推荐 Scaling Law 落地实践'
company: 美团
tag: 生成式
date: 2025-05-15
url: https://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651780422&idx=1&sn=3c35610f1778343f4f82e3d47567ec3d&chksm=bc41cd03a36a61dc2652df83b8751d833995d48d765adb6cf572c9f9af9b6e029aa10c58cfcb&mpshare=1&scene=1&srcid=1007n1iiknl1iTGvEEyluDKs&sharer_shareinfo=b19bc8baa1aa0f76f496d1d6057cb946&sharer_shareinfo_first=b19bc8baa1aa0f76f496d1d6057cb946#rd
account: 美团技术团队
origin: xlsx
---
![](https://mmbiz.qpic.cn/mmbiz_png/hEx03cFgUsVsE4Nicq51WdnKEhcaEEYDS4h6jA6JOZ3fnENgFV1B6ianDTqaQ3nzNOjvHUB79ocldrVj4YlkAW6g/640?wx_fmt=png)

**总第614****篇 |****2025年第011篇**

美团外卖推荐算法团队基于HSTU提出了MTGR框架以探索推荐系统中Scaling Law。MTGR对齐传统模型特征体系，并对多条序列利用Transformer架构进行统一建模。通过极致的性能优化，样本前向推理FLOPs提升65倍，推理成本降低12%，训练成本持平。MTGR离在线均取得近2年迭代最大收益，且于2025年4月底在外卖推荐场景全量。本文系相关工作的实践与经验总结，希望能给从事相关方向研究的同学带来一些帮助。

**目录**

1. 引言

2. 工业界生成式推荐探索与挑战

3. 外卖业务DLRM范式迭代路径

4. 外卖业务生成式推荐落地实践

4.1 MTGR模型框架

4.2 MTGR训推引擎

4.3 Scaling效果

5. 总结与展望

**1. 引言**

深度学习中的缩放法则（Scaling Law）是指模型的一些功能属性（通常指评估的损失Loss或任务的评估指标）与模型架构或优化过程的属性（例如模型大小、训练计算量等）之间的关系。直观的理解就是探索模型算力和效果之间的联系，如OpenAI的GPT3、GPT3.5、GPT4在模型参数量、数据量、计算量逐步提升，模型能力（效果）变强。这些法则可以帮助指导深度学习模型的设计和训练。

在自然语言处理、计算机视觉等领域中，Scaling Law已经被多次验证其有效性，然而，对于推荐系统则仍处于起步阶段。目前影响较大的是工作为Meta的GR（Generative Recommendation）。生成式推荐舍弃了当前推荐系统的大量人工特征工程，采用了类似于LLM的纯序列化表示方式表示用户行为，再通过增大模型计算量的方式提升模型的能力，基于原始信息端到端地预估点击率/转化率。

美团外卖推荐场景经过近十年的面向交易目标的迭代，通过传统DLRM（Deep Learning Recommendation Model）模式进一步提升转化率变得十分困难。从生成式框架出发，外卖推荐团队基于HSTU架构针对排序模型进行优化，提出了MTGR（Meituan Generative Recommendation）这一新的架构，成功在美团核心的外卖首页推荐场景落地。对比基准模型，单样本前向推理FLOPs提升65倍，离线CTCVR GAUC + 2.88pp，外卖首页列表订单量+1.22%（近2年迭代单次优化最大收益），PV\_CTR + 1.31%。在资源使用上，训练成本与基准模型持平，在线推理资源节省12%。该工作于2025年4月底在外卖首页、频道页、小程序等核心场景完成全量。

## 2. 工业界生成式推荐探索与挑战

在LLM时代，Scaling Law被证实适用于绝大多数深度学习任务，包括语言模型、图像生成、信息检索等。然而，在推荐系统领域中，伴随用户行为爆炸式增长，传统DLRM建模不能高效的处理全量用户行为，因此往往通过序列检索 、特征工程等方式对重要信息进行加工，但这也同时也限制了模型Scaling的效果。为了解决这一问题，近一年多来，工业界针对生成式推荐展开了系统性探索，主要呈现三种技术路径：

* **生成式架构**：以Meta的GR和快手OneRec为典型，基于类LLM的Transformer架构，结合高效的FlashAttention算子实现自回归内容生成。Meta GR使用HSTU通过千亿级参数扩展验证了推荐Scaling law效果，OneRec采用Encoder-Decoder+MoE混合设计，结合DPO优化与奖励模型实现CTR/CVR与生成任务的多目标兼容。然而这类生成式方法不能使用任何交叉特征，过度依赖模型从原始的用户行为信号中学习知识，这对于低点击率且高复购率的外卖业务过于困难。
* **堆叠式架构**：如阿里LUM和字节HLLM，通过生成式技术赋能传统推荐框架。LUM采用预训练三阶段策略平衡模型容量与推理时延，HLLM构建Item/User双塔LLM分别处理特征提取与行为预测。这类架构通过离线生成高阶特征实现渐进式升级，但是在迭代范式上过于复杂，通常需要多阶段串行优化，极大增加了推荐系统的迭代成本。
* **混合式架构**：类似于生成式架构针对训练数据按用户进行压缩，减少冗余计算，但是不严格按因果顺序组织Token建模用户完整的行为链，仅借助Transformer强大的编码能力将Token编码的结果直连曝光物品的CTR/CVR等任务的预估，进而兼容两类技术优势。

MTGR也是混合式架构的一种，基于该架构，我们保留包括交叉特征在内的全部信息进行建模，采用统一的HSTU架构针对多个序列同时编码提升学习效果；此外，我们对MTGR的训练、推理框架进行针对性优化，大幅提高了MTGR在混合式架构下的计算性能表现。

## **3. 外卖业务DLRM范式迭代路径**

经典的推荐系统模型可以针对需要预估的用户-商品对，根据处理信息不同，可以把模型拆解成三个部分，User module（编码用户的历史行为序列等信息），Item module（编码候选商家的信息）以及Cross module（同时编码用户和候选的交叉信息）。根据Scaling模块的不同，我们可以简单的将过去的迭代划分为Scaling cross module（图1a）以及Scaling user module（图1b）前后两个不同阶段。此外，Item module由于一般包含信息比较简单，不作为scale up的对象。

![图1 外卖推荐DLRM范式下Scaling路径](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscN2UtUxpA7QvCyP4YYIjJcS5rgP0fkkGdnNzbknqFKJFFhmtDeg5cptg/640?wx_fmt=png&from=appmsg)

图1 外卖推荐DLRM范式下Scaling路径

* **Scaling Cross Module（2018-2022年）**：在推荐系统逐步步入深度学习阶段，迭代以Scaling Cross Module为主，如图a所示，一个经典的排序模型会将Context（时间、地点、场景等环境特征）、User profile（登陆频率、购买频次、复购倾向等用户画像特征）、用户行为序列、预估商家等全部信息在特征处理完成后拼接在一起，然后通过复杂的非线形映射得到最后的预估值，结合多任务学习，经典的非线形映射方案包括PLE、MoE、DCN、PEPNet等。这些方案从各自的角度出发针对网络的Cross Module进行优化，起到加速收敛或者平衡多目标学习的作用。外卖算法团队在过去的迭代中也遵循这一路径，在早期迭代中尝试使用类似deepFM、DCN等特征交叉网络加速收敛，后期则选择MoE架构为基座，配合较大的MLP获取Scaling收益。
* **Scaling User Module（2023年）**：然而Scaling Cross Module存在两个明显的缺点限制其效果天花板。1）Scaling存在天花板，网络复杂度到一定程度后，进一步扩大hidden units或者专家数量，收益不显著。2）推理不友好，每增加一倍计算资源，相应推理资源也会增加一倍。为了解决上述问题，在2023之后，外卖算法团队转向为Scaling User Module。如图b所示，我们先利用Context以及User profile将其映射成多个Query，然后在与用户行为序列做Multi-Query Attention，随后通过MoE（16 expert，每个expert包含三层MLP，hidden units为1336、1336、976，MoE输入维度达2~3k）进一步扩大网络的计算复杂度，再将得到的结果与原网络通过Fusion Layer融合进行预测。仅Scaling User Module，可以在预估时通过先统一计算User Module，再将其广播到不同的样本上来降低推理成本，最终，我们的方案推理成本少量增加24%，模型FLOPs增长182%，首页列表订单量+0.60%。Scaling User Module这一方案使我们的主力模型达到业内计算复杂度较为头部的水平。

然而，在过去的迭代中，无论是Scaling Cross Module还是Scaling User Module，仍存在以下两个显著缺点：1）Scaling依赖于采用MLP捕捉不同特征之间的共现关系，注意力机制使用相对较少，在深度学习的其他领域中，注意力机制对比MLP往往更加有效。2）无论是何种Scaling方案，在训练阶段都存在较大的资源成本，且优化空间较小。Meta所提出的GR方案较好的解决以上两个问题，在后续篇幅中，我们将沿着GR所提出的HSTU框架出发，采用混合式架构，尽可能的保留DLRM原始特征体系，在美团外卖业务中展开落地。

## 4. 外卖业务生成式推荐落地实践

### | 4.1 MTGR模型框架

我们所提出的MTGR整体框架如图2所示，通过MTGR，我们将这些信息编码成自然语言中的Token，然后利用HSTU架构进行建模。在这个过程中，我们：

1. 保留全部DLRM原始特征，并针对样本进行无损压缩，同时建设稀疏化存储以及计算框架将padding导致的冗余计算降低至0。
2. 利用Group LayerNorm以及动态混合掩码策略，实现用统一的HSTU架构针对不同语义空间的Token信息进行编码。
3. 我们设计了三种不同尺寸的模型（MTGR-small、MTGR-middle、MTGR-large），验证了离在线效果的Scaling Law，并使用MTGR-large在美团核心业务中取得显著受益，并完成全量。

下面，我们将对MTGR的数据、特征以及模型架构逐一展开介绍。

![图2 MTGR模型架构图](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNbAJv949gFXqMQSgDabUI8OJf7yiaIp7ic3PCWKd95WwZbvTMafiaOiasKg/640?wx_fmt=png&from=appmsg)

图2 MTGR模型架构图

#### **4.1.1 数据&特征**

在数据与特征上，我们首先对齐DLRM的特征，保留了全部的交叉特征以减少信息损失，其次针对训练数据按用户粒度实施压缩来实现MTGR高效训练，具体的：

**对齐DLRM的特征使用策略**：在我们的场景下，如表1结果所示，采用生成式方案完全抛弃交叉特征会极大的损害MTGR模型性能，为了尽可能的减少信息损失，我们所使用的特征与DLRM基本一致，这些特征包括：

* **User Profile**：用户统计信息，如登陆频次/购买频次等。
* **Context**：用户当前请求的场景信息，如哪个场景，时间，地点。
* **User Behaviour Sequence**：用户历史点击/曝光序列，其中每个item为有用户交互行为的商家，此外还包含了大量side info，包含了商家的各种属性信息（tag、品牌等）、历史统计信息（历史点击、订单数量等）、当次交互的细分行为（例如停留时长、子页面点击数量等）等，不同请求（用户）的序列长度不同。
* **Target item**：待打分商家信息，如商家ID、各种该商家的side info以及大量的基于统计的交叉特征。

![表1 交叉特征对于MTGR性能影响](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNgtBY0uV7MB72MpKy5QZI2VHzJ4IrEpeL9uqVQtzhrrBf2vicfPn7IoQ/640?wx_fmt=png&from=appmsg)

表1 交叉特征对于MTGR性能影响

* **按用户粒度压缩训练数据**：如图3所示，左图表现了传统DLRM数据组织方式，针对用户的N个曝光，在数据组织中需要存N行，在处理不同长度的序列数据时，往往使用padding进行补全。在DLRM训练时，对同一个用户的N行样本存在大量重复编码，导致计算效率较低，甚至需要结合负采样降低样本量和训练成本。为了解决这一问题，对于训练数据，MTGR针对用户粒度进行压缩，如图3右所示，将同一用户N行样本压缩成一行，同时我们采用稀疏化存储，配合JaggedTensor以及变长的HSTU算子，抛弃了全部padding操作以降低无效存储和冗余计算。额外的，为了避免训练穿越，对于用户行为序列以及target item，我们在数据中保存了其发生的原始时间戳，以用于生产掩码保证正确的因果性，具体的掩码细节将在下一节展开介绍。

![图3 DLRM与MTGR数据组织形式](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscN8icjq41htHozf13SdnQ6YMxcibWBichMIEzfkXWSbEufYAFUvaPLruGXg/640?wx_fmt=png&from=appmsg)

图3 DLRM与MTGR数据组织形式

#### 4.1.2 模型架构

在模型架构上，我们首先将输入信息Token化，再针对不同类型Token进行Group LayerNorm，并设计了一种特殊的动态混合掩码策略，以实现用统一的HSTU架构针对不同序列、用户信息、Target信息进行统一编码。具体的：

* **输入信息Token化**：我们将样本信息拆分成一个个Token。其中对于User Profile每一个特征都表示为一个Token，对于用户行为，则将每一个具体行为对应的item ID以及多个side info的Embedding表征拼接在一起再通过非线形映射组装成一个Token。同理，对于每一个曝光，我们则将item ID、对应的side info、交叉特征、时空等Context信息拼接在一起组成一Token。
* **采用HSTU架构统一建模多个序列**：我们利用HSTU架构针对Token化的输入进行统一编码，对比原方法，我们对每一层的输入都做了额外的LayerNorm以保证深层次训练的稳定性，考虑到不同与传统的LLM，我们的数据可以分组为多种类型的Token，因此，我们将LayerNorm拓展为Group LayerNorm，针对不同类别的Token采用不同的LayerNorm参数，以实现不同语义空间下Token的对齐，下表展现了采用Group LayerNorm的离线效果。

![表2 Group LayerNorm对于MTGR性能影响](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNMMXOwJChlTRdBzG5xzgwFRTN9FKxSNQWEEtHpZT4Ql0hOQ8iaFiaJvQQ/640?wx_fmt=png&from=appmsg)

表2 Group LayerNorm对于MTGR性能影响

* **引入动态混合掩码**：我们将Token简单分为历史静态特征（User Profile & Sequence），当日实时行为（Real-Time Sequence），以及曝光样本（Targets）三个部分。我们采用一种动态混合掩码，具体掩码策略如下图所示，对于历史静态特征我们不进行任何掩码操作，对于当日实时行为采用Causal mask，并结合时间戳过滤未来事件。具体来说，在训练时我们按照用户一天曝光数据进行聚合，并取最后一条实时行为。实时行为/曝光样本按照时间近至远进行排列，更远发生的实时行为看不到更近发生的实时行为。同Targets中存在部分曝光出现在某些实时行为之前，因此需要结合两者时间戳计算掩码，保证较早发生的Targets看不到较晚发生的实时行为。我们以图4为例展开说明：

+ 标有颜色表示可以被看见，每一行表示该Token可以看到哪些Token，每一列表示该Token可以被哪些Token看到。
+ 实时行为/曝光样本按照时间近至远进行排列：最近发生的曝光样本可以看到全部的实时行为，但较早发生的曝光样本只能看到部分实时行为。
+ 对于Target 1，因为它出现的时间较晚，因此它可以看到全部的User Profile & Sequence以及Real-Time Sequence；对于Target 2，有一部分Real-Time Sequence出现在其之前，因此它只能看到部分Real-Time Sequence。

![图4 MTGR动态混合掩码示意图](https://mmecoa.qpic.cn/sz_mmecoa_jpg/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscN3vsoyX1aUSvHpOWhMceoSjmib0d2UabSuEHicgTQHl76A3pf70ymsOlw/640?wx_fmt=jpeg&from=appmsg)

图4 MTGR动态混合掩码示意图

表3展示了采用动态混合掩码对比传统因果掩码的离线效果，采用动态混合掩码可以更好的发挥HSTU作为encoder的学习能力。

![表3 动态混合掩码对于MTGR性能影响](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNNw4Nre4cf446eIOqDPrkaicaRl6VeVCLKDpgNTq3aPDQ9eFaJuFibO3A/640?wx_fmt=png&from=appmsg)

表3 动态混合掩码对于MTGR性能影响

### | 4.2 MTGR训推引擎

相比传统DLRM模型，GR模型的训练和推理面临严峻挑战：

* **训练数据和稠密网络参数规模scale导致离线训练计算量激增**：按照Scaling Law的指导，模型效果的提升来自训练数据量和模型参数量的增加，带来训练计算量的大幅增加。
* **稀疏Embedding规模scale导致离线训练存储规模激增**：新模型范式引入更多的样本和特征，导致Embedding数据量大幅膨胀，给Embedding的分布式存储和通信带来严峻的性能挑战。
* **在线推理模型规模和计算量伴随模型scale激增**：模型大小和计算量膨胀显著，需要更强算力、更大显存的GPU加速卡，或者考虑CPU-GPU联合推理的异构计算模式。

为了解决上述问题，我们建设了MTGR模型训推引擎，解决模型计算量和存储量激增带来的诸多性能挑战。包含两个核心组件：

* **MTGR-Training**：支持低成本、高效率大规模分布式训练。
* **MTGR-Inference**：支持低延迟、高吞吐大规模线上推理部署。

#### 4.2.1 MTGR-Training

我们基于TorchRec构建了简单易用、高性能、可扩展的GR模型训练引擎MTGR-Training，可支持千亿参数、100GFLOPs/example甚至更大计算量的模型的高效分布式训练。

![图5 MTGR-Training系统框架图](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNR9LAS2tQln1LuJ37aSMtuZPwtJFFWAliaum4PbiahxHHcBvkHHaXoc5w/640?wx_fmt=png&from=appmsg)

图5 MTGR-Training系统框架图

如图5所示，系统框架分成三层：

* 最底层是TorchRec。TorchRec是Meta开源的稀疏模型训练框架，我们对其做了一些功能上的扩展，例如支持动态Hashtable、梯度累积等，满足业务的实际需求。另外，GR模型的Dense部分可能也会变得很大，我们借鉴LLM社区的模型并行方案（例如FSDP/Megatron）进行支持。
* 中间层就是MTGR-Training，我们的主要工作也集中在这层，其对训练流程进行了封装，包括离线/流式数据读取、训练评估流程、断点续训、离在线一致性校验、warm-start等。同时，给用户暴露简单的模型定义接口。
* 最上层是算法模型层，不同业务根据我们提供的接口定义自己的算法模型。

MTGR-Training具体的功能支持和性能优化工作总结如下表4所示：

![表4 MTGR-Training功能支持和性能优化工作](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNK3J6uspDUkE3nI9TG5PCvcM6YcPc2Mv6z02OpubyGeA5qLnpUGqriag/640?wx_fmt=png&from=appmsg)

表4 MTGR-Training功能支持和性能优化工作

下面重点介绍下Kernel优化和变长序列负载均衡的工作：

* **Kernel优化**：GR模型中最核心的计算单元就是Attention模块——HSTU。原始的pytorch实现存在算子细碎、无法支持动态序列长度、计算效率低下等问题；Triton版本的实现一定程度上解决了这个问题，但仍有较大优化空间。最终我们借鉴flash-attention的思想手写了Fused Cutlass-based HSTU kernel，通过减少内存读写次数，提高 GPU 的内存 IO 效率；同时支持变长序列的输入无需padding，大幅提升了Attention的计算效率，单算子性能相较于Triton版本提升2~3倍。

![图6 HSTU Kernel优化示意图](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNxjxLO4GXhu7OupQfIrlbnDJMibHhZvRS6ccsedd3mbF1w56ftN7O0ow/640?wx_fmt=png&from=appmsg)

图6 HSTU Kernel优化示意图

* **变长序列负载均衡**：GR模型的样本是按照用户维度去组织的，而在推荐系统中，用户序列呈现明显的长尾分布：少数用户的序列很长，大部分用户的序列都比较短。因此固定batch\_size（下文简称为BS）训练时，每张卡的计算量差别比较大，计算量大的卡会拖慢整个训练流程，因为在同步训练模式下，每个step都得等所有卡计算完才能进行梯度同步。同时为了避免出现GPU显存OOM，BS也不能预设的很大，这导致GPU并没有被充分利用。我们的解决思路也比较直观，就是引入动态BS，每张卡的BS根据实际数据的序列长度动态调整，保证计算量（total\_tokens）基本相同；同时修改梯度聚合策略，按照BS对每张卡的梯度进行加权，保证计算逻辑的一致性。如图7所示，假设2张卡进行同步训练，固定BS=4时，卡0上的用户序列比较短，是underload的，存在资源的浪费；切换到动态BS后，比较短的用户序列会组成更大的batch（4 -> 5），从而保证所有卡都是full load的，进而最大化系统吞吐。

![图7 变长序列负载均衡示意图](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNLeicmCrCK6dOgw89bEo3mIvFgkypujia4WaCiaGEgaZfSCSopZFqU9w2w/640?wx_fmt=png&from=appmsg)

图7 变长序列负载均衡示意图

总的来说，得益于用户粒度的样本聚合方式使得相同用户的大部分计算可以共享，以及MTGR-Training的诸多优化，最终我们实现了GR模型的训练成本相比DLRM baseline增加很少，有效控制了训练成本。如表5所示，不采用任何序列采样策略时，65倍计算复杂度GR模型训练成本相比DLRM baseline，只增加了1倍。

![表5 不同尺寸MTGR计算效率对比](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNNw1Sv7hUv9t3aW1ePD6kvqBYba8dvibxqEVvDicgUbTFRTM2tfV3yxiaA/640?wx_fmt=png&from=appmsg)

表5 不同尺寸MTGR计算效率对比

#### 4.2.2 MTGR-Inference

基于Nvidia软件生态，我们构建了高性能的GR模型推理引擎MTGR-Inference：

* **选择TensorRT作为模型推理框架**：[TensorRT](https://developer.nvidia.com/tensorrt)是Nvidia推出的推理优化框架，在业界广泛应用，具有较强的算子融合、低精度量化能力。
* **选择Triton Inference Server作为模型部署框架**：[Triton Inference Server](https://github.com/triton-inference-server/server)是Nvidia推出的高性能模型部署框架，在业界广泛应用，是TensorRT官方推荐的模型部署方案。

![图8 MTGR-Inference系统框架图](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNicaALbGSRM6ZfC7ozhdFhAwC6PpSEbyYomHGTGQzYA0pLuTahzLmfvQ/640?wx_fmt=png&from=appmsg)

图8 MTGR-Inference系统框架图

如图8所示，系统框架分成四层：

* 最底层是硬件层，主要适配Nvidia GPU；
* 再上层是模型推理框架层，基于TensorRT。
* 中间是我们引入的各种推理优化手段，包括特征H2D优化、CUDA Graph优化、HashTable等。其中Hashtable面向推理场景进行了极致优化，阉割掉了写的功能，进一步提升了性能。
* 最上层是模型部署层，基于Triton Inference Server进行部署。

下面详细介绍各种优化手段：

* **特征H2D优化**：推荐模型一般都包含数百个特征，将特征从Host读到GPU时，有较大的传输耗时。为了解决这个问题，我们采取了先merge后split的思路：即在Host buffer中预先开辟一块连续的空间，将不同特征拷贝至这个空间，再统一进行一次H2D，从而充分利用传输带宽。传输到GPU上后，再进行split。这个方案虽然简单，但是收益比较显著，H2D耗时从7.5ms减少至12us，整体推理延迟从19ms减少至12ms（时延降低37%），吞吐从68 req/s提升至94 req/s（吞吐提升38%）。

![图9 特征H2D优化示意图](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNgibTHsp5HWZdxOIJ2I4Pf5RvE9a3rdff4g3AfoXrpuwJSrINU2FL7eA/640?wx_fmt=png&from=appmsg)

图9 特征H2D优化示意图

* CUDA Graph优化：在我们的场景下，使用CUDA Graph优化后吞吐提升13%，不同QPS压力下，Avg延迟降低17%~52%，P99延迟降低16%~57%。
* FP16计算：FP16推理具有内存占用少、计算速度快等优势。在我们的场景下，使用FP16格式进行推理，相比FP32，吞吐提升50%；精度几乎无损（相比FP32打分diff控制在0.006以内）。

### | 4.3 Scaling效果

为了验证Scaling Law，我们设置了small、middle、large三种不同大小的MTGR模型与当前在线最好的DLRM base（Scaling User Module）进行对比。对于small、middle两个版本，我们序列的最大长度设置为3k；对于large版本，为了权衡训练效率，最大长度设置为1k。

当前DLRM base在线经历了超过2年的学习，水位线较高，MTGR则仅采用2024.10之后近半年的数据进行训练。表6展现了不同尺寸的MTGR模型离在线效果，尽管数据上有所劣势，MTGR离在线各个指标仍大幅超越了DLRM base。除了这三种尺寸外，我们离线阶段最大实现了深度22层，=1024，计算复杂度达137.87GFLOPs（约160倍DLRM）的超大规模模型，并取得了更高的离线结果，但是受推理性能限制并没有进一步在线实验。

此外，在验证Scaling Law过程中，除了传统的增加深度、宽度外，我们还特别伴随不同的模型尺寸，同步增大稀疏参数的大小（调整embedding dim），该参数作为超参数存在，且针对不同尺寸的模型以及不同类型的Token分开设置，假设某一个Token由个特征组成，每个特征的embedding dim通常会被设置为附近的整数。

![表6 不同尺寸MTGR模型Scaling Law效果](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscN3FgicrlcMo6WibrNOs7ogxianpt5k5gcibhrZXJNZbVo1QSXFFjX5XHhcg/640?wx_fmt=png&from=appmsg)

表6 不同尺寸MTGR模型Scaling Law效果

我们基于MTGR-large在美团外卖推荐业务中完成了全量，对比之前SOTA的DLRM base，MTGR单样本前向FLOPs提升65倍，达到55.76GFLOPs，图10给出了AB test阶段MTGR-large对比DLRM订单收益曲线。

![图10 MTGR-large AB test订单量对比](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXMsNLia4ic6hfqwSCxWCibscNxQLfPpBZ9D4ibB0gzZZibZ5nw2GMF50cdxgv67d999slibk6ibNJ27FqHA/640?wx_fmt=png&from=appmsg)

图10 MTGR-large AB test订单量对比

对于训练资源，采用与GR原方案一致的随机长度采样策略，优化后训练成本降低至与DLRM持平，且离在线效果基本无损；对于推理资源则节省12%，推理资源下降是由于对比DLRM，MTGR在推理阶段资源消耗对于候选数量不敏感，对比DLRM需要多分片推理来降低耗时，MTGR采用单分片推理即可，较好的提升了在线吞吐。

## **5. 总结与展望**

Scaling Law已成为当下深度学习的基本准则，但是在推荐系统领域中的探索还相对较少，我们基于HSTU提出了MTGR这一新的排序框架。MTGR保留与DLRM一致的特征体系，以避免生成式架构下丢失交叉特征带来的信息损失；在序列编码方式上，我们结合Group LayerNorm以及动态混合掩码策略提升HSTU学习效果；此外，我们还针对MTGR的训练与推理框架做了针对性优化以减少资源消耗。最终，MTGR在我们的实际业务中取得了离线CTCVR GAUC + 2.88pp，首页列表订单量+1.22%，PV\_CTR + 1.31%的收益；同时在资源上，训练资源持平，在线推理资源节省12%。

在未来，我们将与各部门继续展开紧密合作，针对以下方向持续进行探索：

* 结合LBS业务特点优化原始HSTU结构突出时空属性，进一步优化当前排序效果。
* 建立多业务全场景MTGR模型。建设基于User Center的生成式推荐框架，结合KV Cache提升全场景推理效率。
* 粗排+排序阶段融合。结合LBS下供给数量有限的特点，利用MTGR实现粗排+精排一段式打分。

## // 参考文献 //

[1] Zhai J, Liao L, Liu X, et al. Actions speak louder than words: Trillion-parameter sequential transducers for generative recommendations[J]. arXiv preprint arXiv:2402.17152, 2024.

[2] Fang Y, Zhan J, Ai Q, et al. Scaling laws for dense retrieval[C]//Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval. 2024: 1339-1349.

[3] Pi Q, Zhou G, Zhang Y, et al. Search-based user interest modeling with lifelong sequential behavior data for click-through rate prediction[C]//Proceedings of the 29th ACM International Conference on Information & Knowledge Management. 2020: 2685-2692.

[4] Si Z, Guan L, Sun Z X, et al. Twin v2: Scaling ultra-long user behavior sequence modeling for enhanced ctr prediction at kuaishou[C]//Proceedings of the 33rd ACM International Conference on Information and Knowledge Management. 2024: 4890-4897.

[5] Deng J, Wang S, Cai K, et al. OneRec: Unifying Retrieve and Rank with Generative Recommender and Iterative Preference Alignment[J]. arXiv preprint arXiv:2502.18965, 2025.

[6] Yan B, Liu S, Zeng Z, et al. Unlocking Scaling Law in Industrial Recommendation Systems with a Three-step Paradigm based Large User Model[J]. arXiv preprint arXiv:2502.08309, 2025.

[7] Chen J, Chi L, Peng B, et al. Hllm: Enhancing sequential recommendations via hierarchical large language models for item and user modeling[J]. arXiv preprint arXiv:2409.12740, 2024.

[8] Tang H, Liu J, Zhao M, et al. Progressive layered extraction (ple): A novel multi-task learning (mtl) model for personalized recommendations[C]//Proceedings of the 14th ACM conference on recommender systems. 2020: 269-278.

[9] Jacobs R A, Jordan M I, Nowlan S J, et al. Adaptive mixtures of local experts[J]. Neural computation, 1991, 3(1): 79-87.

[10] Wang R, Shivanna R, Cheng D, et al. Dcn v2: Improved deep & cross network and practical lessons for web-scale learning to rank systems[C]//Proceedings of the web conference 2021. 2021: 1785-1797.

[11] Chang J, Zhang C, Hui Y, et al. Pepnet: Parameter and embedding personalized network for infusing with personalized prior information[C]//Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining. 2023: 3795-3804.

[12] Guo H, Tang R, Ye Y, et al. DeepFM: a factorization-machine based neural network for CTR prediction[J]. arXiv preprint arXiv:1703.04247, 2017.

----------  END  ----------

**招聘信息**

算法团队来自搜索和推荐平台部/外卖搜推算法组，负责外卖主站以及神抢手和拼好饭等业务的搜索、推荐、大模型应用算法，业务核心，技术能力强，每年有多篇论文发表在KDD、SIGIR、CIKM等会议上。当前，MTGR仍在深度迭代中，机会广阔潜力大，欢迎各路英才加入，联系方式：jiangfei05@meituan.com。

工程团队来自搜索和推荐平台部/机器学习引擎组，负责美团各业务的搜索推荐机器学习引擎的工程架构工作，包括模型训练，模型推理，用户特征平台建设等。团队技术能力强，工作氛围好，当前正在深度探索下一代搜推架构等多个前沿方向，欢迎感兴趣的同学加入，联系方式：yulei37@meituan.com。

**更多招聘岗位：**[招聘 | 美团 AI 搜索：致力用 AI 技术创造极致的搜索和交互体验](https://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651780372&idx=3&sn=16b7e2a24efecd00df71b1ca42c63801&scene=21#wechat_redirect)

**活动推荐**

![](https://mmecoa.qpic.cn/sz_mmecoa_png/hEx03cFgUsXIIqy7Vr5fknueADufrYNSIVEBpfpYTeLBbq8yctKjzLEArXaib6cpzVh6yhL6znXwzfNzjafI7kQ/640?wx_fmt=png&from=appmsg)

**>**>******[点击这里报名](https://hdxu.cn/180y4)****<**<****

---

**推荐阅读**

**|**[搜索广告召回技术在美团的实践](https://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651778297&idx=1&sn=e0c8566c3f745a3a252a753e0fefd373&scene=21#wechat_redirect)

**|**[美团外卖搜索基于Elasticsearch的优化实践](https://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651772026&idx=1&sn=6ff4cb024bb416c46d5d2850a6ae77d1&scene=21#wechat_redirect)

**|**[美团搜索粗排优化的探索与实践](https://mp.weixin.qq.com/s?__biz=MjM5NjQ5MTI5OA==&mid=2651770506&idx=2&sn=53df7e69852b53b8e9a78704250a3f59&scene=21#wechat_redirect)