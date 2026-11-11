---
title: 'WSDM’26｜阿里妈妈直通车提出搜推广系统通用用户大模型LUM'
company: 阿里妈妈
tag: 推荐
date: 2026-03-27
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497179&idx=1&sn=194cfcffb87f1a1d6b7e818023237dd2&chksm=c146d4dbac95f341dbcba3f96cf07f3805952c9498f86590b024ef9ab2e6045d74314b960993&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
> 小结： 自24年开始，生成式预估模型在阿里妈妈直通车主场景全面落地，阿里妈妈直通车预估团队联合淘天集团未来生活实验室打造的通用用户大模型LUM，在精排CTR预估模型上已全量上线两期，**累计贡献大盘CTR+4.5%的显著收益**。

# 1. 背景

## 1.1 算力驱动的范式跃迁

大语言模型的崛起并非偶然的技术跃迁，而是算法设计与硬件特性深度对齐的必然结果。这一进程经历了三个关键阶段：2017年，Transformer通过自注意力机制摆脱RNN的序列依赖，实现高度并行的计算结构；2020年，Scaling Law的发现揭示模型性能随参数量、数据量和计算量呈幂律增长；2022年，FlashAttention、DeepSpeed等工程技术的成熟使MFU普遍超过30%，千亿参数模型成为可复制的工业实践。

LLM的成功可归结为三个关键特征：**统一的token表示**将文本、代码、图像等纳入同一建模框架；**生成式的自回归目标**使模型隐式学习数据的联合分布；**以GEMM为主导的计算流**与Tensor Core深度适配，实现算力的高效转化。三者共同揭示了一条普适规律：**当算法设计与硬件特性对齐时，智能随算力投入稳定增长。**

## 1.2 预估模型的结构性困局

反观搜推广预估模型，则走在一条不同的发展轨迹上。从FM/FFM的显式特征交叉，到DIN/DIEN的序列注意力建模，再到DeepFM/DCN的高阶交互，每一次突破都依赖针对特定信号设计的功能模块。这条路径的本质是**基于人工先验的模块化堆叠**——模型日益复杂，但表达能力的增长依赖经验规则而非数据驱动的自动泛化。模型变得越来越复杂，但并未变得更"聪明"。

更深层的问题在于，这种建模范式与现代硬件的演进方向形成了**系统性错配**。过去八年，GPU峰值算力增长超100倍（P100 FP32 9.3 TFLOPS → H100 FP16/BF16 989 TFLOPS），而内存带宽仅提升约4.6倍——现代GPU已全面转向以Tensor Core为核心的计算密集型设计。然而，传统预估模型的计算特征恰好与之相反：

* **极低的算术强度：** 大量计算消耗在稀疏ID的Embedding查表上，后续MLP与特征交叉的计算量微弱，整体算术强度远低于Tensor Core的高效工作区间，MFU长期徘徊在个位数；
* **高度碎片化的计算流：** 多塔结构、显式交叉模块等设计催生数千个微小CUDA kernel，频繁的kernel启动与非连续内存访问成为主要开销；
* **缺乏可预测的Scaling收益：** 增加模型容量难以带来稳定的效果提升，算力投入与业务收益之间不存在可复现的Scaling关系。

最终结果是：最先进的计算芯片被用于执行高度碎片化的任务，算力潜力远未释放。问题不在于投入不足，而在于底层建模范式已与硬件环境脱节。

## 1.3 从端到端生成到通用用户基座

为突破上述困局，一些工作尝试将预估任务直接表述为生成任务，通过Transformer架构端到端执行Next-item Prediction（如HSTU）。**相比判别式模型仅需建模条件概率****、侧重分类边界学习，生成式模型需要更大的参数容量去刻画数据的联合概率分布****，因此在参数Scale up时更容易取得进一步收益。**然而，这类端到端的生成式方案（E2E-GRs）过度追求理想化目标，忽视了DLRMs在工业实践中的固有优势，引发了一系列问题：

* **训练与应用不一致：** 生成式目标能刻画行为依赖与分布，但难以直接满足预估对序和准度的要求；
* **性能瓶颈：** ODL训练的时效性与在线推理的RT约束难以兼顾，性能限制制约了模型的Scale up；
* **灵活性不足：** 新增行为类型（如退款行为、新场景行为）需重训整个模型，难以适应快速变化的业务需求；
* **兼容性缺失：** 工业级系统中积累的特征体系与模型参数难以被E2E模型有效继承。

更根本的是，无论DLRMs还是E2E-GR，本质上都是面向**单一任务**构建的——召回有召回的模型，预估有预估的模型，各自为战。而用户长周期、多场景、多模态的行为序列，是搜推广系统中信息密度最高的数据源；对这份数据的理解不应在每个下游任务中被重复建构，算力和数据价值不应在重复投入中被稀释。

要释放这一数据潜力并实现与现代硬件的高效对齐，关键在于构建一个**高信息密度、高计算效率、可多任务复用**的通用用户建模范式。为此，阿里妈妈直通车团队联合淘天集团未来生活实验室团队提出了Large User Model (LUM)——**一个面向工业场景的通用用户基座大模型。LUM以Transformer自回归预训练为核心，从终身行为序列中学习用户兴趣的深层结构，计算流以GEMM为主导、MFU超40%，并通过**"PreTrain → PostTrain → Application"三阶段范式实现生成式建模能力与判别式生产系统的有机结合，一次建模、多处复用。

目前，LUM已经在阿里妈妈直通车主场景**全量上线**，带来了CTR+4.5%，消耗+2%的显著提升。

更多 LUM 细节可参考WSDM26论文：Unlocking Scaling Law in Industrial Recommendation Systems with a Three-step Paradigm based Large User Model（https://arxiv.org/abs/2502.08309）

团队其他大模型工作直达：

* 与LUM配合，预估模型主体结构通过统一架构融合基座输出与实时特征，推理过程高度规整，随规模扩展持续提效。全量两期，累计贡献大盘消耗+4.5%的显著受益，细节可参考论文：From Scaling to Structured Expressivity: Rethinking Transformers for CTR Prediction（https://arxiv.org/abs/2511.12081）
* 更多预估x大模型总结详见：[从算力迷途到范式新生：生成式预估模型的思考与实践](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496763&idx=2&sn=f8da7cdef06dcf263dd169e3bb3c9421&scene=21#wechat_redirect)

# 2. 通用用户大模型LUM

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYMF0LiceYZQY5EEdRcS8jV8icRvyRNudEWU9wyWuynJSaGiaJiaXP3eMMdxWLf5rOxSDG6UMHwnWMvsxO1Xog5lXjtxKeiakbyKr7YY/640?wx_fmt=png&from=appmsg)

**受到LLM应用的启发，整体来看，LUM分为三个阶段：**

* **阶段一：**承接了解锁“Scaling Law”的任务，通过增加模型参数和丰富各式各样的用户行为，理解搜推广下的语言体系&协同信号，**此时Large User Model与下游任务无关**
* **阶段二：**通过构造不同trigger，来提取与下游强相关的知识，达到**生成式->判别式**转换目的，适配下游各种应用；同时实现了较轻的推理过程，并可以结合缓存等应用，响应了在线生产模型对高效连续流式训练和低时延在线计算的需求
* **阶段三：**以增量信号的方式引入到各个生产模型中去，**无缝衔接各类生产模型**，满足工业级的效果&性能需求，在保持DLRMs灵活性和兼容性的基础上，最大程度发挥生成式模型的能力

## 2.1「阶段一」LUM 预训练

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYPHYvRb7AvFDvaFQ9ic6xF6XKqFHrsnEh9RGonEL0gicd1lFlAtlW53qZiacSc3L3PpsPSXaJQYDV7twt7ML1zeR7nPvwXDF7aQRY/640?wx_fmt=png&from=appmsg)

* **Tokenization：**将用户历史行为tokenize成〈condition token， item token〉，其中Condition Token 描述item 的context信息，比如场景、query等信息，Item Token描述商品信息。

  ![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYOjzQGWlpOE9JD6XvAcffYoslcuMMI5GQKBmkZ4llOgKibSTRl0eJYiaJYoJS5E1ZuntPeneqMCLPTFB9UjpusXjf0GHd5YIBsog/640?wx_fmt=png&from=appmsg)
* 结构：整体分为两层，分别为Token encoder 和 User encoder

+ Token encoder：将各类id、统计、内容特征拼接后编码，表征单一Token的信息

其中，表示item token侧()的各类特征（如cate id、brand id等）与condition token侧()的各类特征（如query、scene等）；通过拼接后线形映射得到编码结果

\* User encoder：经过Token encoder后，再通过一个自回归transformer结构进一步处理同一用户历史行为序列中的各Token，建模用户偏好和协同信息

* 任务：定义「Next-condition-item Prediction」任务，即基于历史行为序列和当前的Condition Token，预测下一个商品

其中，c与i分别代表condition token与item token，通过交错形式组合成序列，以自回归形式预测下一商品概率。此外引入condition token后，能通过设置不同的condition，可以在联合分布中triggering想要的信息。

训练目标方面，由于工业场景中的商品量级过大（数十亿），直接在其上计算概率分布难以实现，因此采用InBatch的对比式损失函数，利用同批次内的商品互为负样本（规模约22k）以近似全库负样本

采用标准InfoNCE loss，其中，sim为相似度量，LUM一期中采用cosine相似度；K为同batch内的负样本数量。

## 2.2 「阶段二」LUM Triggering

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYO3XhrN6icp472g9icgyBGsI9kFOaHtQUv3YsJCEqTE4l0ExvWxLvdjFm1aoUf91A0z3LvM4mB3zR2ibXhknKc6tHw3Hp9GpjXLsI/640?wx_fmt=png&from=appmsg)

类似LLM中的**prompt engineering**，LUM可设置不同的Condition Token(比如不同场景、不同query)，通过在Condition token上“**prompt engineering**”，来灵活的获得用户不同Condition下的推理的偏好，而这种偏好可以和下游应用任务强相关。比如搜索场景，则设置Condition token为当前请求的query，来激活LUM的知识，就可以知道用户在该query下的偏好。

## 2.3 「阶段三」LUM CTR应用

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYPuQ4ksOG9ttp8XqjgbvjIZjs4gD4nqNQPKaem4gN0TISbk9qn9l0FHAWzCMLKWCMuQD1wntpibPjfZCba1WDb6bIashGnJqeVc/640?wx_fmt=png&from=appmsg)

通过将阶段二的产出信息用作CTR模型特征，实现生成式模型与判别式模型的联合提效。整体而言，应用思路分为两个方面：

**1) Direct Feature Incorporation：**直接将阶段二产出的序列和表征作为特征加入到CTR模型中。

**2) Interest Matching via Similarity Measurement：**通过target item和生成的序列item进行相似度计算来衡量用户对于target的偏好。

# 3. 实验与部署

## 3.1 离线实验

首先对比了LUM、E2E-GR以及传统DLRM模型上的效果，不论是公开数据集还是内部数据，在下游的召回和预估任务上均取得了最优的效果（如下图所示）：

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYMvAXE0ian2YjPzgaNkZKzSjw0B6gLP2hAicIntl5cliaiaiciaHoarUcGsVhzc9uiac9sxIc9RevBQnl9pUY0E2c9yF7fLv8yzowBNuY/640?wx_fmt=png&from=appmsg)![image.png](https://mmecoa.qpic.cn/mmecoa_png/YbDPHqs6VYPicTJrYZhUhL5xUmwQ0Pp0UNQHheDQ9FjtiboYXSuE9ww4WJwiaEFliaYpMniaERsa0tJWPrf55FpKZVqv89qLn9sLIkUkibX1lueXQ/640?wx_fmt=png&from=appmsg)

同时LUM是一个通用的三阶段框架，把他作用于不同的CTR模型上，均有显著的AUC提升。此外，正式因为LUM的通用性，可以无缝衔接online CTR模型，取得相比于生产的进一步AUC收益。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYODhicrfHZLoIfD5Ug5nAuquOTdq9pYVWoV90dAF8ROQEwbOYgLT5g2xmIasqqc6AVTMH83iaUBoxa1qm0QMTia9Een3lnmROAdy8/640?wx_fmt=png&from=appmsg)![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYOZV5RNtPxWjSKsMNRFrLCeBLZBg7SyXjKhj5lBav3aibG5ebHnsZWHPuPKtFfLQWWfficc90PwsvJGEdyK1IBNL8nR7qiaXiaNY0s/640?wx_fmt=png&from=appmsg)

最后，对于LUM进行了Scaling Law分析，从模型的size (19M->7B) 和sequence length (256->8192)均发现存在power law的关系。

![image.png](https://mmecoa.qpic.cn/sz_mmecoa_png/YbDPHqs6VYPdeaCJwDZkTBKveAWK2Qgsqd6tM6NDJLiaF2ibCeB4rKyVpOsbWh0weeWFgLTgHibRzcGkSHw0cmCuZ2iaVlBCbibRibuAlZCiaticaj8/640?wx_fmt=png&from=appmsg)

## 3.2 在线

**在线部署：**对于用户的实时请求，LUM实时推理阶段与召回&粗竞并行，来获取更多的时间buffer，同时采用Cache的方式降低总QPS；最终LUM的实时推理结果给到精竞CTR消费。

![image.png](https://mmecoa.qpic.cn/mmecoa_png/YbDPHqs6VYOoh8M61oRlIb1Qkv4fM23ngsZIP6ibFXDs1dWZxsYWguicB4ctnNKs9KI27aaFG7FewEjpWLaNgROLia3xiaC3kLpIdIPrAneLibibk/640?wx_fmt=png&from=appmsg)

**在线效果：**在阿里妈妈搜索核心主场景的精竞CTR预估阶段全量上线，取得CTR+4.5%，消耗+2%的显著提升。

# 4. AI Infra：让大模型真正跑起来

算法设计再好，跑不起来就是空中楼阁。LUM从预训练到在线推理，背后有两套关键的基础设施在支撑。

## 4.1 Blaze-O1：面向搜推广场景的高性能推理引擎

LUM上线的一个核心挑战是：在线实时推理的RT和吞吐怎么保障？AI Inference团队为此建设了Blaze-O1推理引擎，为工业级召回与排序场景提供高吞吐、低延时的LLM实时推理和检索能力。几个关键设计：

* **异构算子混合编排，解除单一后端依赖**：基于统一的 Operator 抽象，支持 Torch 子图、手写 CUDA 算子及 TensorRT-LLM Engine 子图的混合编排，可在同一计算图内无缝集成自研高性能算子与主流推理优化引擎；算子层统一适配 GPU、PPU、AMD 等多种硬件后端，实现一份计算图、多种异构硬件部署。
* **多流 DAG 并行调度，释放极致并发性能**：执行引擎基于 DAG 实现算子级并行调度，支持 Tokenizer、Prefill 及业务前后处理的并发执行；核心链路采用 C++ 实现，避免 Python GIL 带来的并发限制和延迟抖动，提升系统延时稳定性。调度层支持一致性哈希、Round-Robin 和负载均衡等流量分发策略，推理层支持多子进程、多线程及多 CUDA Stream 并行执行，在满足时延约束的前提下最大化单机吞吐。
* **GPU化向量检索，打通检索与推理链路：**支持基于 GPU 的 HNSW 等向量检索能力，具备多卡协同存储、检索、D2D 访问和 INT8 量化加速能力，实现向量召回与 LLM 推理的一体化闭环，减少 PCIe 传输和数据拷贝开销，进一步提升搜推广场景下的检索效率与在线推理性能。
* **Large KV Cache，适合搜推广的前缀缓存复用**：为应对搜推广场景下用户规模大、行为间隔长、KV Cache 复用空间不足的问题，采用 User-id 级一致性哈希路由减少冗余存储，并构建单机多卡 GPU 显存、CPU 内存和磁盘的多级存储能力，结合 LRU 淘汰策略保留热点数据、下沉冷数据，提升 Prefix KV Cache 命中率与复用效率。

在上述推理引擎的支撑下，Blaze-O1 在线业务的 MFU 和延迟约束下的端到端吞吐均取得显著提升，为大模型在工业级场景的规模化落地提供了坚实的推理基座。

## 4.2 RecIS：统一的稀疏-稠密训练框架

LUM的训练同样面临挑战：推荐模型正演变为**稀疏-稠密混合模式**——稀疏部分负责大规模特征Embedding计算，稠密部分是Transformer等深度网络。传统基于TensorFlow的框架在稀疏训练上有积累，但在灵活性和与大模型生态的衔接上存在短板；PyTorch生态在稠密模型优化上更成熟，但对工业级稀疏训练的支持尚不完善。

为此，团队开发了RecIS（Recommendation Intelligence System），基于PyTorch生态构建统一的稀疏-稠密训练框架：

* **统一框架：** 满足工业级推荐模型结合多模态、大模型的训练需求，LUM的预训练直接受益于此；
* **稀疏部分面向访存优化：** 性能超越基于TensorFlow的推荐模型训练；
* **稠密部分对接PyTorch生态：** 借助FlashAttention、FSDP等成熟的优化技术，保障Transformer大模型训练效率。

RecIS为LUM从"能跑"到"跑得好"提供了底层训练基础设施的保障。

# 相关工作：

[1] Unlocking Scaling Law in Industrial Recommendation Systems with a Three-step Paradigm based Large User Model, WSDM 26

[2] UQABench: Evaluating User Embedding for Prompting LLMs in Personalized Question Answering，KDD 25

[3] RecIS: Sparse to Dense, A Unified Training Framework for Recommendation Models

[4] From Scaling to Structured Expressivity: Rethinking Transformers for CTR Prediction

#

# 💡 关于我们

阿里妈妈直通车预估团队专注于核心预估算法的研发与创新，致力于在超大规模场景下，运用人工智能前沿技术打造高效、精准、智能的预估解决方案。团队在CTR/CVR预估、序列建模、特征交叉、多模态融合及预估大模型等方向持续深耕，成果丰硕，近年来已在 NeurIPS、KDD、WWW、SIGIR等国际学术会议发表多篇论文。同时真诚欢迎对搜推广算法与AI技术充满热情的同学加入！（社招/校招/实习 均有HC）

**📮**招聘邮箱：bencheng.ybc@taobao.com

阿里妈妈工程平台 AI Infra 团队，致力于打造面向搜推广场景以及 GenAI / AI Agent 应用的生产级 AI Infra 平台。团队服务于淘天电商核心业务，承担模型超大规模 Embedding 表征学习、Sparse-Dense 模型及 Dense 大模型的训练与推理平台建设与性能优化。在高性能在线服务与训练平台、分布式系统、异构计算和 AI 编译优化等方向，团队具备扎实的工程实践与前沿技术积累，持续探索业界领先的技术方案与落地能力。团队校招、实习均有 HC，欢迎加入！

**📮**联系邮箱：liuzhengyu.lzy@taobao.com；yunlong.xyl@taobao.com

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&randomid=pugabtu8&tp=webp#imgIndex=9)

****也许你还想看****

[AAAI’26 Oral｜Agent基于用户长期行为的个性化偏好理解的评估和优化](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497146&idx=1&sn=6f4bb20de1d5d4601f81e8f43b4ae999&scene=21#wechat_redirect)

[WWW'26 | 克服多重延迟：阿里妈妈展示推广提出级联延迟反馈建模新框架](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497108&idx=1&sn=70f66a9b0c32c888faf66962d43b173c&scene=21#wechat_redirect)

[阿里妈妈提出直播推广轻量好用的出价算法 | KDD'25](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497066&idx=1&sn=8ddc879a59a0c7e673380acd620467ac&scene=21#wechat_redirect)

[开放下载 | 2025 阿里妈妈技术年刊来啦！](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247497046&idx=2&sn=fac385aaa941150a329c61b4c40a774e&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=15)

喜欢要“分享”，好看要“点赞”哦ღ~