---
title: 'Oxygen 9N-LLM生成式推荐训练框架'
company: 京东
tag: 工程相关
date: 2026-02-04
url: https://juejin.cn/post/7602512064977354815
account: 
origin: harvest-202607
---
# Oxygen 9N-LLM生成式推荐训练框架

[京东零售技术](/user/4233576972293643/posts)

2026-02-04
  
233
 
阅读27分钟

   

引言：生成式推荐作为推荐系统领域一个蓬勃发展的新范式，为整个领域带来了新的思路和机遇。它在处理复杂语义、提升推荐多样性、突破效果天花板以及优化系统架构方面展现出巨大潜力，但同时也给训练引擎带来新要求与新挑战。

为了更好的支撑零售算法业务以更高的效率、更低的成本探索这一新方向，**京东零售九数算法平台团队凭借在训练引擎领域多年的技术积累，建设了一套多框架（TensorFlow/PyTorch）、多硬件（GPU/NPU）、多场景（传统/生成式）的统一训练引擎Oxygen 9N-LLM**。该引擎深度整合TensorFlow与 PyTorch双框架、统一适配GPU与NPU异构硬件，有效解决了框架与硬件的兼容性问题，其内置的大规模稀疏Embedding训练引擎、定制化UniAttention加速库、基于Ray的统一RL训练框架等核心组件，协同优化稀疏与稠密参数计算、解决注意力计算以及强化学习流程等系统性难题，加速推动了生成式推荐范式在工业场景的落地（如[OxygenREC](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzUyMDAxMjQ3Ng%3D%3D%26mid%3D2247515195%26idx%3D1%26sn%3Db8271354b4c7db10c68f712f819103ea%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247515195&idx=1&sn=b8271354b4c7db10c68f712f819103ea&scene=21#wechat_redirect")）。

九数算法平台隶属于京东零售平台产品与研发中心AI Infra与大数据计算部，负责建设服务京东电商业务的AI Infra基础设施。

### **一、背景与挑战**

传统深度学习推荐模型经多年迭代优化，已面临特征工程潜力逼近上限、用户意图建模难度高、级联架构易放大误差、算力利用率不足等核心问题，成为制约其效果进一步提升的核心瓶颈。

LLM 生成式模型爆发式崛起后，将生成式算法与技术应用于推荐领域已成为业界研究热点，即生成式推荐（Generative Recommendations, GRs）。作为区别于传统推荐的新范式，它借助生成式模型强大的序列建模能力，将推荐问题重构为序列生成任务，预测用户可能的下一步操作或偏好物品，为突破传统推荐模型瓶颈提供了全新思路。在这一新兴范式的探索进程中，Meta 的 GR 工作率先验证了 Scaling Law 在推荐系统中的有效性，为生成式推荐的规模化发展奠定了关键基础。在此之后，业界探索了不同技术路径的生成式推荐方案，且在实际工业场景中实现了显著的线上效果提升，充分验证了其商业价值。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/b74e1bf496f3480386fbf2118fa87869~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=hh1qYPwJHicLAxxmtK5n%2B%2Fryrxo%3D)

图1：传统和生成式推荐范式对比

然而，在这一新范式下，模型呈现出的新特性也使得其在工业场景的规模化训练面临多重挑战：

**样本的效率和灵活性要求更高：** 生成式场景中样本包括万级用户行为序列，外加多模态特征引入，存储成本扩大上百倍；长序列特征tokenizer/lookup以及多模态特征加载与解码，训练节点的CPU和内存成为瓶颈点，预处理耗时也成倍增长。在TB/PB级的样本、TB级别参数下，断点恢复效率也是影响训练整体效率的非常关键因素。

**模型架构跨界融合与框架协同鸿沟：** 生成式推荐采用 T5、GPT-Decoder 等类 LLM 结构，结合 MoE 混合架构，融合传统推荐的稀疏特征与 LLM 的稠密生成特性。但这一跨界架构导致技术栈冲突，传统推荐依赖成熟的 TensorFlow 生态（尤其是大规模稀疏 Embedding 方案），而 LLM 相关优化（低精度量化、多维分布式并行）集中在 PyTorch 生态，两者鸿沟使得框架协同能力缺失，TensorFlow 下实现 LLM 类优化成本极高，PyTorch 在稀疏 Embedding 处理上性能与扩展性不足。

**模型规模双向扩展与训练效率挑战：** Scaling Law 驱动下，生成式推荐的稀疏与稠密参数规模同步大幅提升。结合全站全域数据及用户全生命周期序列，模型既要处理 TB 级动态词表与异构特征，稠密参数规模更扩展至 B 级（较传统推荐模型的 0.01B～0.02B 提升至少两个数量级），这种双向规模激增给训练带来非常大的效率挑战。

**更加复杂的训练流程：** “预训练-监督微调-强化学习”已成为生成式推荐领域的常见训练流程。在强化学习（RL）阶段，通过设计精巧的奖励系统以及融合多目标业务策略，从而进一步提升模型效果。然而，与标准大语言模型的强化学习（如GRPO）相比，生成式推荐的RL训练更为复杂，其挑战在于其架构（多种自定义组件，如特征拼接模块与Reward服务接口）、工程（实现TB级稀疏与B稠密参数的高效同步）、系统复杂性（融合在线学习的分钟级更新需求），这些独特的复杂性使得现有的大语言模型RL框架（如VeRL、TRL）难以直接复用。

针对上述痛点与挑战，九数团队依托训练引擎领域多年技术积淀，打造了支撑多框架（TensorFlow/PyTorch）、多硬件（GPU/NPU）、多场景（传统 / 生成式）的统一训练框架 9N-LLM。该框架深度融合 TensorFlow与PyTorch 双框架，统一适配 GPU 与 NPU 异构硬件，通过协同优化稀疏与稠密参数的存储计算、注意力计算及强化学习流程等系统性问题，助力生成式推荐范式在京东业务场景快速落地（如OxygenREC）。

### 二、9N-LLM生成式推荐训练框架

9N-LLM 从底层引擎、核心组件到整体框架，为生成式推荐训练提供了全链路解决方案。其搭载的样本引擎、大规模分布式稀疏 Embedding 引擎、底层稠密加速库及 RL 训练模块，可轻松支撑10万级序列、10TB 级稀疏、10B 级规模稠密的生成式推荐模型训练，MFU（硬件算力利用率）最高达40%以上，目前该框架已落地京东主站APP的多个核心流量场，为生成式推荐探索和落地提供坚实支撑，核心特性如下：

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/16498b03b14d43a9adeca7acaad3d6af~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=tKhiqjN9E8xdhWHRCillswEzcZ0%3D)

图2：9N-LLM整体架构图

**高效样本引擎**：基于Ray Data构建分布式样本框架，解耦样本与模型计算，支持节点横向扩缩容。对样本预处理算子进行向量化改造，提升样本处理效率。通过把Embedding化的序列存放到KV系统，在训练过程中动态拼接Embedding，可以显著减少样本存储成本，灵活的样本拼接方案支撑复杂的训练流程。在分布式样本处理框架下，提供了行粒度样本管理能力，为大规模训练提供样本无损的断点恢复方案。

**大规模分布式训练引擎：** 为弥合生成式推荐中TensorFlow稀疏生态与PyTorch稠密生态的技术鸿沟，我们自主研发了新一代大规模分布式训练引擎，该引擎通过对PyTorch进行深度升级，采用HBM-MEM 分层缓存设计及五级流水线强一致同步训练并行架构，可实现 10TB 级稀疏 Embedding 分布式多机扩展训练，性能达开源 SOTA 方案的 1.14-2.4 倍，内置梯度累积、量化导出等基础训练组件，搭配频次 / 概率 / ShowClick 等准入淘汰策略、动态学习率调度等完备调优方案，具备分钟级在线学习增量导出及 Kafka 参数实时推送能力；同时，针对生成式推荐场景SeqPack/LabelPack等定制化掩码场景，基于 Cutlass/Triton/Tilelang 深度优化打造的Attn加速库，**较 FlexAttention/Compile 性能提升 70%/3.0倍**。

**灵活的RL训练能力：** 依托 Ray 分布式计算框架构建强化学习训练体系，通过抽象 SingleController 与 DistributeWorker 核心组件实现架构解耦，可灵活适配Collocated与Disaggregated两种模式，满足不同规模场景下的资源调度需求。内置高效的 IPC（进程间通信）参数同步机制，Loss 计算模块及可扩展的算法组件库，结合样本和训练引擎，能够灵活匹配应生成式推荐场景中多样化的自定义业务逻辑，包括复杂奖励机制设计、动态策略调整、多目标优化需求等，均能通过组件化配置实现灵活支撑，兼顾训练效率与业务适配性。

GPU/NPU全面硬件适配，近0切换成本：全面覆盖京东GPU/NPU 硬件，多硬件间迁移成本近乎为零，原有代码可在 NPU 与 GPU 环境间近无缝切换。

本文后续章节将结合核心技术要点，从样本引擎、训练优化、训练流程三个方面，深入阐述九数生成式推荐训练的系统化解决方案。

### 三、高效样本引擎

相比传统的 LLM 训练，生成式推荐训练场景消费样本量大、训练耗时长、训练节点多。尤其是引入 RL 训练后，多阶段训练组网复杂，需要使用更加灵活的方式完成推理结果与特征的重组。因此，9N-LLM从 IO 吞吐、样本灵活性、训练稳定性三个方面提供了强有力的样本解决方案。

**3.1、向量化样本处理，提升 IO 吞吐效率**

PyTorch 原生 DataLoader 机制在样本预处理阶段存在数据处理效率低，极易成为训练瓶颈点。为提升海量样本的消费效率，9N-LLM样本引擎从样本文件读取、解析、预处理一直到输送给模型训练的全链路上，应用向量化的技术来加速样本的处理，提升 IO 吞吐效率。

**Parquet 列存样本**：支持按列读取特征，不会像行存样本浪费大量的 IO 带宽；列存样本具有非常高的压缩率，可以成倍减少存储成本；基于 SIMD 向量化和多线程技术能够提供极致的解压缩效率。

**链式向量化消费链路**：支持用户使用 `dataset.map().prefetch().take()`模式来消费样本，在调用链路上基于 arrow 内存列式对象 RecordBatch 提升数据处理效率。用户可以在 `map(fn)`函数中传入向量化的 `fn`来加速样本预处理，如基于 pyarrow.compute 实现的 lookup、truncate 等数据加工操作。另外通过 `prefetch`实现 IO Free 机制，用于评估模型极限性能。

**DataLoader 向量化改造**： Dataset 和 Collator 间交互的元素从单行元素改造为 Batch，避免了样本拆分与重组开销。原本在 Collator 内部执行的函数，通过向量化改造并迁移到 `map(fn)`函数中，让 Collator 专注于 Tensor 的构建，并且尽可能把标量类的 Tensor 进行压缩处理，减少父子进程间的数据交互开销。

**3.2、动态样本，降低存储成本并提高样本灵活性**

**3.2.1、动态特征拼接，提供灵活高效样本构建方式**

在生成式推荐的 GRPO 流程里面，由 Policy Model 推理生成的 sampling 样本，需要拼接上 item feature 再交给 Reward Model 使用。传统的做法是 sampling 样本写入到 Hive/Kafka 后，再由 Spark 等计算引擎进行离线样本拼接，这样会导致三个阶段的训练比较割裂，并且会存储大量冗余的 item feature。

样本引擎开发了基于 HBase 的动态特征拼接方案，支撑灵活的样本处理方式，用户可以提前把不同的 item features 导入到不同的 HBase 表中。Reward Model 直接从 Kafka/Hive 表中取得推理结果，使用主键去拼接 HBase 中的 item features 进行后续的训练流程。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/1021e24bdbfd477c806076a4b65d75a4~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=ALDJAAPkrndzsdtZ7NqVn7q2JD0%3D)

图3：动态特征拼接

**3.2.2、Fixed-Period User Event 特征压缩，减少无效存储和冗余计算**

传统的训练模式下，用户的每一次曝光都会保存一条样本，在训练过程中需要对同一个用户的相同特征进行多次计算。而在生成式推荐模型中，是对用户的行为序列建模，我们可以把同一用户一段时间内的多次曝光聚合在一起，构成 Fixed-Period User Event 特征。一方面显著减少了 Common 特征的存储成本，另外在特征预处理过程中只需要执行一次特征编解码，并根据行为的产生时间生成掩码，避免模型训练过程中的特征穿越现象，同时是生成式推荐模型计算加速的核心依赖。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/d300c8f867054e0393a6b45b6d507329~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=vMpdk817wW0ST4Xh9aBvM5VyR0M%3D)

图4：Fixed-Period User Event 特征压缩

**3.3、样本无损的断点续训/续推，提升算力资源利用效率**

为应对训练中由软硬件故障引发的训练中断，需支持任务失败恢复。为了充分利用闲置资源，9N-LLM支持训练/推理过程中动态扩缩容节点，并支持动态样本分发，即在弹性训练/推理场景下支持样本无损的断点续训/续推，提升算力资源利用效率，如图5和图6所示：

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/e0bd3740197a400db54688fca73ce56c~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=Jkknb8enPy1MW1nWYL%2BsBt78Fro%3D)

为此，样本引擎构建了行粒度样本无损断点续训/续推解决方案，主要包含以下能力：

**行级标识：** 在整个训练/推理链路中传递每条样本的唯一行级元信息，精确记录样本消费进度；

**快速定位：** 当任务失败恢复时，能快速跳过已消费的样本，避免无效 IO；

**动态 sharding：** 当发生扩缩容时，在 worker 间均匀分配未被消费的样本；

**模型与数据同步：** 建立样本 ckpt 与模型 ckpt 的同步机制，模型恢复时同步加载样本 ckpt；

**分布式样本处理：** 基于 Ray Data 构建分布式的样本处理能力，支持样本处理资源的横向动态扩缩容。

### 四、大规模稀疏分布式引擎

生成式推荐新范式下，大规模稀疏参数仍是保障模型效果的核心支撑。9N-LLM重构了零售场景已成熟落地的训练引擎，同时兼容TensorFlow/PyTorch、GPU/NPU 硬件；其依托多级缓存、五级流水线的核心架构设计，同时凭借完备的调参策略机制，可支撑 10TB 级稀疏参数高效的横向扩展训练。

**4.1、多级 Cache + 全 GPU/NPU 计算/通信架构：10TB 级稀疏参数存储与计算基石**

整体上，稀疏参数通过模型并行互不重叠分散在不同训练节点上，稠密参数则通过数据并行在所有节点上复制。每次迭代时，各节点读取本地数据，按稀疏参数分片规则对样本中的 Key 进行分桶，并通过 All2All 将 Key 发送到对应节点，同时查询对应的 Embedding 向量，再通过 All2All 传回各节点，随后执行前向与反向传播。稠密参数的梯度通过 AllReduce 在各节点间同步，稀疏参数的梯度则通过 All2All 传输并更新对应的 Embedding 向量。

为支撑万亿级稀疏参数的训练，引擎采用Device/Host Memory 多级存储 + 全 GPU计算/通信核心架构。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/187bb818f5dd497c9959634d7fc03d07~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=jqQ65wQ22KKmCopbxKDJAZ4XXxk%3D)

图7：分布式分层存储架构

**Device/Host Memory 分布式分层 KV 存储架构：** 该架构以HBM-MEM分层设计为核心，实现大规模稀疏参数的高效访问。训练过程中，稀疏参数会被组织为独立的键值对分片，采用无重叠策略存储于各训练节点的主机内存Host Memory中（例如，当分片总数为 256、训练节点数（rank 数）为 8 时，各分片与节点的对应分布关系如图8所示）。同时通过无锁队列访问和并行读取更新机制，可将Mem Embedding查询、更新、Save/Load效率提升数倍。

![image.png](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/490ef61e4e3a43dcbf738579370acc1f~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=y7RMgMRaE8orcf%2BR2%2BlJD1%2FoOd0%3D)

图8：稀疏参数分片示意图

与此同时，设备内存Device Memory承担缓存核心角色，其会提前加载并保存未来 N 个训练步骤中所需的全部 Embedding 参数。分层设计下，每个训练步骤无需频繁从主机内存读取数据，而是利用设备内存的高带宽特性直接从缓存中快速获取所需参数，从而降低参数读取延迟，是实现10TB级参数可扩展、高效存取的核心。

**全 GPU/NPU 计算与通信：** Emb 的查询、梯度同步采用 GPU Direct RDMA 集合通信，以最大化带宽利用；依托对称内存（Symmetric Memory）技术，构建非阻塞单边 All2All 通信模式，接收方无需阻塞等待，大幅降低通信延迟；同时结合流水线分片技术，在多个测试场景中实现 All2All 吞吐量 5%～30% 的提升。同时，针对所有 Embedding 操作（Id 输入分片、Embedding查询、Embedding Grad 聚合、稀疏优化器、Embedding 参数更新），我们均重新使用 CUDA/Triton/Tilelang 实现和优化，以充分释放硬件计算潜能。

**4.2、强一致同步五级流水线：性能为业界开源最佳性能的1.14～2.44倍**

分层 MEM-HBM 架构虽解决了10 TB 级参数的横向扩展难题，但在训练流程中，从 MEM 查询训练所需 Embedding、再将更新后的 Embedding 写回 MEM 的过程中，面对大规模、超长序列、高频率的查询与更新场景，CPU 串行查询、H2D/D2H数据拷贝的等待耗时会大幅增加，直接制约了整个模型的训练效率（如图9中红色部分）。以一个简单例子来说，如训练Batch size 为2048， 序列长度为1w（70%重复），Dim为1024， 则单次查询量约23.4GB （2048*10000*1024*4/(1024*1024*1024)*(1-0.7)） ，H2D耗时大约为400～800ms（PCIE 5.0x16 单向带宽实测约30～50GB）。

![image.png](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/4904bd2e45824f0082f8a65e40440f2b~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=OsnDSMqdPk0wXX0kXPgIZq4cdqw%3D)

我们实现了动态词表的多级流水方案，通过拆解流程、并行掩盖的核心思路重点解决该问题，将原本串行的 “数据准备- Embedding 查询-模型计算” 全链路，整理为五个阶段：

**Data Prefetch：** 样本读取和样本解析；

**Data H2D：** 将MEM中解析后样本拷贝至Device；

**Input Dist：** 提取样本中的稀疏特征Key，根据词表分片规则，将Key进行分桶并进行AllToAll，确保每个设备仅接收与自身负责的 Embedding分片匹配的key；

**Emb Lookup：** 根据接受到的Key在Host MEM 侧完成Embedding向量查询，再将查询到的 Embedding 向量拷贝至Device；

**Fwd/Bwd/Opt：** 执行 Emb All2All，将Embedding 同步至对应的Rank；至此本次训练迭代所需的Embedding向量已在HBM就绪；接下来完整执行模型的前向计算、反向计算得到对应的梯度；执行Grad All2Alll，将梯度发送至对应Rank，进行梯度聚合并更新参数，最后将更新后的Embedding 写回MEM。

**五级流水线：通过精细化的阶段重叠执行机制实现延迟掩盖**

在训练中，当 batch 0 在 GPU 上进行核心计算时（前向传播、反向传播及参数更新），系统通过任务调度已同步推进后续多个批次（如 batch 1 至 4）的预处理工作。例如，batch 1 在查询向量，batch 2 在进行通信，batch 3 在准备数据，batch 4 则在预加载数据。这种“计算与数据准备并行”的流水线设计，有效掩盖了数据传输与通信的延迟，将等待时间转化为有效工作。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/93855301e5d947d38cc926a1e01d345e~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=hf6oyZFfdQ4uqJ6caG6Sw3jUEcg%3D)

在大规模查询更新场景下，该流水线重叠执行机制的优势更为突出 —— 其通过抵消数据预处理、传输、查询等环节的延迟开销，大幅缩短了单个训练迭代的有效耗时，比如在百G 稀疏、B级稠密模型场景测试中，可将Embedding耗时占比从15%降低至5%以内，其Embedding查询、更新性能在内部环境下测试，不同场景为业界开源最佳性能的1.14～2.44倍。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/d537a6e6b4a84dee950dfe615dad0fa5~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=0IzRAYQ4RIaAMNHHjOyguqsp0bo%3D)

**4.3、完备稀疏参数调优策略和训练机制**

围绕稀疏模型训练的全流程需求，引擎构建了覆盖Embedding准入、淘汰调优策略、定制化稀疏优化器、动态词表导入导出的完备机制，确保 10TB 级扩展下的稀疏参数精细化训练。

**4.3.1、特征准入与淘汰，精细化管理动态词表**

针对低价值特征浪费资源、引发过拟合的问题，通过灵活的准入与淘汰策略，实现动态词表的高效管理：

准入策略：支持 CountFilter（频次阈值）、ProbabilityFilter（几何分布概率）、ShowClickFilter（点击得分）三种方式，过滤低贡献特征，提升模型泛化能力并减少资源占用。

淘汰策略：提供 CountShrink（版本新鲜度）、L2WeightShrink（贡献度量化）、TimeFreqCombineShrink（时间 + 频次多维度）、ShowClickShrink（点击统计）四种选择，剔除无效特征，节约内存并保障训练效果。

**4.3.2、定制化稀疏优化器**

针对TensorFlow/PyTorch 原生优化器在稀疏场景下适配性不足的问题，引擎通过双重机制实现灵活调控：

一方面内置 Lazy Adam、RAdaGrad、AdamDecay、AdamW 等多种稀疏优化器

另外一方面支持自定义学习率调度策略，可根据训练进度动态调整稀疏参数学习率，内置主流策略，线性衰减（平稳递减）、余弦退火（平滑下降）、指数衰减（先快后慢）。

**4.3.3、动态词表 Save/Load CKPT：高效支撑大规模部署**

采用分片式词表分布设计（类模型并行），将稀疏参数拆分至多个训练节点，结合独立的稀疏部分存储机制，提升词表规模与操作效率：

核心优势：多分片并行加速查询 / 更新 / Save / Load；充分利用多节点内存 / 显存，突破词表规模上限；与 Dense 部分解耦，操作轻量、控制精细。

支持增量导出加载、低精度（FP16/INT8/INT4）量化导出，kafka流式推送，是降低线上资源、保障在线学习时效性重要优化方式。

### 五、大规模稠密计算引擎

**5.1、复用生成式训练优化技术**

得益于 PyTorch 训练框架的深度支持，以及与LLM同质的 Attention 结构设计。结合九数在LLM方面的优化经验，我们可以较为轻松的复用 LLM 训练中已验证的成熟训练优化能力。表2中列举了一些常见的优化方式，可通过便捷的配置选项、改动在 9N-LLM 中启用，能够在生成式推荐模型的训练中，平衡显存、算力、通信，以提升整体训练性能。

![image.png](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/80f4edba8ad8444ca4481ee1207d77ab~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=W7ph1A%2BERVbYb7hXGxvoRCnEvRU%3D)

表2：常见的生成式训练优化技术

**5.2、UniAttention：针对生成式推荐Attention特点加速优化**

值得注意的是，FlashAttn 作为 LLM 训练中的核心计算优化技术，通过充分利用硬件特性，如异步访存、CUDA Core/TensorCore 并行计算及寄存器优化等，能够显著降低训练显存占用，并提升常规 Causal 与 Full Attention 的计算性能。然而，在生成式推荐训练场景中，Attention 的计算形式并非标准类型，而通常更为复杂，体现在两方面：

**序列结构复杂：** 生成式推荐场景有可能将输入序列划分为多个语义区段，例如“用户特征序列段”、“用户历史行为序列段”、“当日实时行为序列段”及“曝光点击行为段”等。每个序列段可独立配置为 Full 或 Causal 注意力模式，形成混合结构。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/7d7ec459655b494585956da61a96f902~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=H2iS%2BQgS%2FrPTlDg404Lp6kNvnvo%3D)

图11：LLM与生成式推荐场景Mask对比

**训练样本聚合方式特殊：** 为了提升生成式推荐训练效率，训练样本通常按用户单日曝光点击行为进行聚合，其中实时行为与曝光样本依时间由近至远排列。这意味着较早发生的行为不可见较晚发生的行为，形成一种非对称的局部因果依赖，其 Attention 计算逻辑比传统 LLM 中的 Causal Attention 更加复杂。

因此，在该场景下通常无法直接使用高度优化的 FlashAttn，而只能依赖 PyTorch 原生算子或使用 FlexAttention 等扩展方案，是制约整体训练性能的关键瓶颈。为此，9N-LLM 推出了支持自定义掩码的专用加速库 UniAttention。该库基于 Triton/Cutlass/Tilelang 等编译器技术，针对生成式推荐中的 HSTU、GPT Decoder 和 T5 等主流结构进行了深度优化，其性能显著超越现有方案，较 FlexAttn/Compile 分别提升 70% 与 3.0 倍，为生成式推荐训练提供了关键的高性能支撑。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/187c779eadb042768339306028ac8c27~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=hhB74ZgtTHE%2Fd8woR0C3CpWSnlM%3D)

图12：UniAttention加速库

具体来说，我们深入硬件底层、结合硬件特性，从**寄存器优化**与**流水线编排**两个维度出发，基于 Cutlass 与 Tilelang 对HSTU Attn 和 SDPA算子进行了深度定制与优化。

在生成式推荐场景中，Mask 与输入数据高度相关，导致 Mask 相关计算与判断逻辑显著复杂化，进而大幅增加了寄存器压力。为应对这一挑战，我们采用了**Compute/Mask 双区间调度算法**，将矩阵乘法与 Mask 计算分别置于两个连续的独立区间执行，不仅优化了 Mask 判断流程，同时可减少20%～50% GEMM 计算与 Mask 判断次数。在流水线编排方面，UniAttention 充分利用 Hopper 架构中 **wgmma 指令的异步特性**，使矩阵运算与 Softmax、Mask 等非矩阵运算在两个 warpgroup 之间交错执行。当其中一个 warpgroup 执行非矩阵运算时，算子可调度另一个 warpgroup 并行执行矩阵运算，从而实现了 Tensor Core 算力的高效利用。通过上述两项关键优化，UniAttention 在复杂多变的 Mask 场景下实现了高性能的 Attention 算子，助力生成式推荐模型的高性能训练。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/d586e0ea970645b0a6e35d6e8bf3b23b~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=kt8Nr9SZ8RuxZINzvVgGciZJLd4%3D)

表3：UniAttention性能数据

### 六、强化学习训练能力

**6.1、生成式推荐场景的强化学习特点**

强化学习作为一种强大的决策与优化框架，是提升大模型推理能力、驱动AI Agent实现高阶自主性的关键催化剂。具体到生成式推荐场景，在经历预训练与监督微调之后，强化学习阶段被引入，其核心价值在于为模型赋予了“探索”与“自我优化”的能力，模型不再仅仅被动拟合已有数据，而是能通过与环境互动，主动发现更优的推荐策略，实现持续的效果进化。

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/91ee8d8586c348599c99054a9748d146~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=o6BzyhZ23hLTiWP92cxbtzTEjuM%3D)

图13：生成式推荐RL流程

图13展示了生成式推荐的强化学习（RL）训练过程，其核心模块（RollOut、Reward、Reference、Policy）及整体流程与大语言模型（LLM）的 RL 训练逻辑一致，均依赖灵活的任务调度、高效的资源分配与稳定高效的多节点通信，但二者在实际落地场景中存在明显差异：

**模型与样本特性不同：**

输入样本为传统稀疏 ID/SID 类型，依赖原生 PyTorch 词表或大规模稀疏词表（LLM 多为稠密文本输入）。

模型结构借鉴 LLM 核心模块，但需适配稀疏场景，Reward 打分可能复用推荐场景全量模型。

**采样与流程设计不同：**

采样采用定制化 BeamSearch，专门过滤生成 SID/IDList（LLM 侧重文本生成采样）。

训练流程存在较多自定义设计，新增特征拼接模块，RewardWorker 可能调用在线接口或 TensorFlow 模型。

**参数同步与性能挑战不同：**

推荐场景 CTR 模型稀疏参数量达 TB 级别，跨进程参数更新的同步成本极高，易引发性能问题（LLM 以稠密参数为主，参数同步逻辑更成熟）。

**6.2、基于Ray的强化学习解决方案**

9N-LLM 基于 Ray 框架构建，面向大语言模型与生成式推荐的复合训练场景，通过能力拓展与架构统一，有效应对生成式推荐中强化学习（RL）训练的关键挑战：

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/b9db5975527346ae9101016bfd8ae408~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=pcInzGVVo%2FJRA6h7BKJgiZtOUX8%3D)

图14：基于Ray的通用框架设计

**多场景兼容**：统一支持 LLM、多模态及生成式推荐、MultiAgent场景下的强化学习任务，实现跨场景训练能力复用。

**资源灵活调度**：支持节点间任意资源配置，提供 Actor 的同卡（Collocate）与分离（Disaggregated）部署模式。在同卡模式下，实现大规模稀疏参数的复用，避免冗余拷贝；进程内支持高效 IPC 通信，提升稠密参数同步效率。

**高度可定制**：Worker 内部支持自定义数据、模型、训练与离线推理流程，兼容包括大规模稀疏参数在内的自定义节点。通过 SingleController 模式与 Worker 间的灵活编排，满足生成式推荐 RL 训练中如特征拼接、跨框架调用等定制化需求。

### 七、结语

生成式推荐作为推荐系统领域一个蓬勃发展的新范式，为整个领域带来了新的思路和机遇。在过去一段时间，我们深刻认识到：样本模态日益丰富、算法架构快速迭代、硬件生态日趋多元，面对这样繁杂的多元状态，作为AI Infra，必须回归第一性原理，设计能够充分利用并随样本、计算资源指数级增长而持续扩展的AI架构。

正如图灵奖得主Richard Sutton在《苦涩的教训》中深刻指出的，AI发展的长远趋势证明，那些依赖大规模计算与通用学习的方法终将超越融入人类精巧设计的路径。这一洞见一直指引着我们的技术演进，让基础设施真正具备“随着算力增长而线性扩展”的能力。

面向未来，我们将持续推进两大核心方向的探索：

**在基础设施层面**，为应对未来硬件规模化、大规模通信瓶颈及多元算力融合的趋势，我们将重点探索通信与计算模式的根本性升级，并通过统一内存架构优化，实现跨硬件平台的高效带宽与显存利用，让算力资源的使用效率实现质的飞跃。

**在系统智能层面**，我们将与业务紧密协同，以新一代奖励模型为核心驱动，通过在线强化学习整合多模态信息与用户全生命周期行为，旨在构建一个超越短期点击指标、具备长期用户价值的、真正智能的生成式推荐系统。

## **招聘**

欢迎对AI Infra、LLM/CTR模型训练、样本引擎、算力调度感兴趣的同学加入九数团队，和我们一起打造京东智能化AI基建。

📮 简历投递：[hanpingping11@jd.com](https://link.juejin.cn?target=mailto%3Ahanpingping11%40jd.com "mailto:hanpingping11@jd.com")、[chenzhen48@jd.com](https://link.juejin.cn?target=mailto%3Achenzhen48%40jd.com "mailto:chenzhen48@jd.com")

![图片](https://p3-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/f95f75581df44de4a55bc49ffb99a064~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5Lqs5Lic6Zu25ZSu5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785303676&x-signature=ryAJPSgFcv%2FGLUf2ypTPHXrrrrc%3D)