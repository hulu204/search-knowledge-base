---
title: '小红书引擎架构团队ICDE 2026新成果：CCD感知编排突破多核CPU向量搜索性能天花板'
company: 小红书
tag: 召回
date: 2026-05-18
url: http://mp.weixin.qq.com/s?__biz=Mzg4OTc2MzczNg==&mid=2247495272&idx=1&sn=2668ecaeb4fd0d7c4d03b875c0c65277&chksm=cfe44c9ff893c589ba77eeec98594a07ef8b72593d18d5e91b1ce50031c20276a547131c0e73#rd
account: 小红书技术REDtech
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/P9Hs04VFGRkxIxGoxwIWzOcpjgZEw9NpXbpXDaXYiahCOVHYsLsc1aI200lfAKkt5w3tllEwEtZ9NbbKGDiazXZ9zqEsDPNWLVloZkfCibjQNQ/640?wx_fmt=jpeg)

近日，小红书引擎架构团队在 ICDE 2026 发表论文《CCD–Level and Load-Aware Thread Orchestration for In-Memory Vector ANNS on Multi-Core CPUs》，提出了一种面向多核 CPU 的 CCD 级负载感知和线程编排向量检索框架，该框架通过 CCD 级缓存亲和性调度与冷热负载感知映射，系统性解决了现代多核服务器 CPU 上向量近似最近邻检索（ANNS）的性能扩展瓶颈问题。在小红书搜推广核心业务真实负载下，吞吐量最高提升 **3.7×**，P999 长尾延迟降低 **30%~90%**，CPU 缓存未命中率降低了 6%~30%，总 CPU 停顿时间减少了 20%~80%。相关研究成果发布于 ICDE  2026会议上，**ICDE**（International Conference on Data Engineering）是数据库与数据工程领域的顶级会议，与 VLDB、SIGMOD 并称数据库三大顶会，聚焦数据库系统、数据管理、大规模数据处理等方向。

论文链接：

https://arxiv.org/abs/2605.10090

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRm7vibZFMibDEXW1A7vOlu3Tp5iacUd0549w3pIWrIuSlF6P93AS6icdrhpa2gmxc3WoAgdfdFRyV8Y0Zr8cQWcxUfah5naPic2Aic74/640?wx_fmt=png)

**1.1 背景与挑战**

近似最近邻搜索（Approximate Nearest Neighbor Search，ANNS）是支撑现代搜索、推荐和广告等业务系统的核心基础设施，其目标是在高维向量空间中，以近似代替精确的方式快速定位 Top-K 相似结果，兼顾检索质量与计算效率。典型的 ANNS 算法涵盖基于图结构的 HNSW（Hierarchical Navigable Small World）和基于倒排索引的 IVF（Inverted File Index）系列，这些算法在工业界已获得极为广泛的应用。

小红书作为国内最大的生活方式分享社区，搜索、推荐、广告等核心业务每日需要处理数千万级 QPS 的向量检索请求，维护着数千张规模从百万到百亿不等的向量索引表，服务对象涵盖笔记、商品、用户等多类实体。在严格的延迟 SLA 约束下，基于 CPU 内存型向量索引是团队在线服务的主流技术路线之一。

为应对持续快速增长的业务规模，团队引入了 AMD EPYC 系列 CCD（Core Complex Die）多 Chiplet 架构 CPU。这类 CPU 通过在单个 Socket 内集成多个 CCD 物理芯粒来扩展核心数：以 AMD EPYC 4代 Genoa 为例，单 Socket 集成 12个 CCD，每个 CCD 拥有独立的 32MB L3 缓存和 8个物理核心合计 96核。这种架构在核心数上实现了量的飞跃，理论上应带来近似线性的吞吐提升。然而，实际部署后的表现令人失望：在 96核配置下，HNSW 实际吞吐量仅达到理论峰值的 82%；在配置了 2 到 12个 CCD 的情况下，IVF 的加速比仅约为 1.6倍至 2.8倍。远低于预期的线性扩展。

这一现象促使团队展开深入的性能分析，最终揭示了隐藏在 CCD 架构背后的系统性问题：现有的线程调度框架完全不感知 CCD 架构的拓扑特性，导致大量的跨 CCD 缓存失效，使得增加的计算资源不仅未能有效转化为性能提升，反而因缓存污染和内存带宽竞争加剧了系统性能劣化。

**1.2 核心贡献**

本文的核心贡献包括以下三个方面：

**其一**，首次系统性地刻画和量化了工业级向量 ANNS 服务在 CCD 多核 CPU 上的负载特征，包括访问局部性分布、跨 CCD 流量倾斜、长尾延迟成因等，为后续的系统优化提供了可靠的问题定义与数据支撑。

**其二**，提出了 CCD 感知的冷热自适应映射算法。该算法基于在线流量估算，将向量表动态映射到 CCD，通过冷热配对策略避免 Hot-Hot 同驻，实现各 CCD 流量均衡，并采用滑动窗口平滑过渡，自适应感知业务负载的动态变化。

**其三**，提出了拓扑感知的层级化任务窃取策略。通过感知 CPU 的物理拓扑结构，建立三级窃取优先级，在保障负载均衡的同时，将跨 CCD 任务迁移降至最低，打通了缓存亲和性与负载均衡长期对立的工程矛盾。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRkbiaaextD5xq8faXyv4ndw0oQBX9Nsp8G07SWognO5Evy8TDmxUWGzniarNic158mS7Sxt1MHtiahaJeBJsb8a6pWyX4w45gZoado/640?wx_fmt=png)

**2.1 CPU 缓存感知调度研究**

向量检索领域，HNSW 和 IVF 是最为广泛应用的两类算法。HNSW 通过分层图结构实现了优秀的召回率与查询速度的平衡，hnswlib 是其最常用的开源实现。IVF 系列（IVFFLAT、IVFPQ等）通过向量量化与倒排索引，在内存效率和检索速度间取得平衡， FAISS 是工业界最常用的实现。

在多核调度层面，现有系统通常依赖 OpenMP 或自研的线程池框架。OpenMP 采用工作共享（Work Sharing）模型，适合高度规则化的并行任务；自研线程池如百度的 bthread，基于全局任务窃取（Global Work Stealing）模型，在任务不均衡场景下有更好的负载均衡效果。然而，这些框架均未针对 CCD 多 Chiplet 架构的拓扑特性进行优化，在 CCD 架构 CPU 上的表现存在系统性瓶颈。

缓存感知调度在操作系统和高性能计算领域已有较多研究。NUMA（Non-Uniform Memory Access）感知调度是较为成熟的方向，通过将任务绑定到特定 NUMA 节点，减少跨节点内存访问延迟。然而， CCD 架构与 NUMA 在物理结构上有本质差异： CCD 的独立 L3 缓存是其与 NUMA 节点的最大不同，且现有操作系统对 CCD 拓扑的感知和调度支持极为有限。

在向量检索领域，现有工作主要聚焦于算法层面的优化（如量化精度、图索引结构），对系统运行时调度层面的研究相对空白。本文是**首个专门针对 CCD多 Chiplet 架构，面向向量 ANNS 在线服务场景的线程编排研究**，填补了这一空白。

**2.2 跨 CCD 调度导致缓存亲和性破坏**

CCD 架构的关键特性在于每个 CCD 拥有独立的 L3 缓存。当某张向量表的查询请求被调度到不同 CCD 的线程上处理时，同一张表的向量数据会被重复加载到多个 CCD 的 L3 缓存中，无法在 CCD 间共享，形成大量冗余的内存访问。

以 HNSW 为例，其查询过程涉及对图结构的随机游走访问，访问的节点向量数据存在显著的时间局部性（短时间内同一批查询会反复访问相同的"热节点"）。若这些查询被分散到不同 CCD 上处理，热节点数据就需要在多个 CCD 的 L3 缓存中各存一份，不仅浪费宝贵的 L3 缓存空间，还因缓存争用导致驱逐频发，Cache Miss 率居高不下。

对线上数据的分析表明，在 10秒的滑动时间窗口内，不同向量表的访问频率呈现显著的 Zipf-like 分布：少数热表承载了绝大多数的查询流量。这种局部性分布，使得 CCD 感知的静态映射策略具有较高的收益稳定性。

**2.3 Hot-Hot 同驻引发的缓存污染**

即便单个 CCD 上只调度一张向量表，也可能面临缓存污染问题。当多张高流量向量表被同时调度到同一个 CCD 时，它们会相互争夺有限的 32MB L3 缓存空间。由于不同向量表的数据量差异可达数个数量级（从 10K 向量到 15M 向量），热表的数据往往远大于单个 CCD 的 L3 缓存容量。多张热表同驻一个 CCD，会使得各自的热点数据持续相互驱逐，即形成所谓的 Hot-Hot Co-location 问题，使得 L3 缓存的实际命中率远低于理论值。

实测显示，在未优化的 Round-Robin 调度策略下，部分场景中 L3 Cache Miss 率比优化后高出 6%~30%，导致大量本可在 L3 缓存内完成的计算退化为对内存的访问，内存带宽成为严重瓶颈，CPU 利用率也因长时间的 Memory Stall 大幅下降。

**2.4 全局任务窃取破坏访问局部性**

bthread 等采用全局任务窃取（Global Work Stealing）策略的调度框架，其设计目标是最大化 CPU 利用率，当某个线程的本地任务队列为空时，允许从任意其他线程的队列窃取任务。

这一策略在传统计算场景下非常有效，但在 CCD 架构的向量 ANNS 场景中却适得其反：被窃取的任务往往来自处理另一张向量表的线程，不仅任务与当前线程所在 CCD 的缓存数据无关，还会使原本计划利用 CCD 局部性的任务被打乱。

线上监控数据显示，在未优化的 bthread 调度框架下：

● HNSW 场景跨 CCD 任务窃取率高达 **~75%**

● IVF 场景跨 CCD 任务窃取率高达 **~80%**

几乎每次任务窃取都伴随着完整的缓存失效和重新预热，CPU Stall 时间占比因此大幅升高，抵消了多核并行带来的计算增益。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRnHhEy3bRMwTFmJ6EDYma7xfZoFULKALGHu8p7RmIIlZ3TjmOOH8vG9qKY0ziaWPm5icrBKRlmUiaYZJNjIktAgRwptib5tWuGGz7w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRmxlBlFtptfyfzgEJErf1zG3icIX5kTXb5a6hETDe6uWjBzJf1eI6HyZeLrEsa5VSnAqqjz1CgqWnGdB9b4anNZf6KhAM0XIwuI/640?wx_fmt=png)

针对上述三大根因，小红书引擎架构团队提出了 **CCD–Level and Load-Aware Thread Orchestration Framework（CCD感知自适应线程编排框架）。**该框架作为独立的中间层嵌入现有向量索引与底层调度系统之间，对上层索引算法完全透明，对下层操作系统调度无依赖，实现 Drop-in 替换。框架整体分为三大核心模块：统一任务提交接口、冷热感知映射调度器、拓扑感知层级化任务窃取机制。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRku2wic6AmPojV6RAmSZ7kFmoORCVjyx0cdnpBCSP5TqybSZZFNjoW6Fcqa2hxfVSElOPHTdMXQWbEibtpibqod3lQEicfwyKXqibr4/640?wx_fmt=png)

**3.1 统一任务提交接口**

为兼容 HNSW 和 IVF 两种截然不同的并行模式，框架设计了统一的任务提交接口，并且同时支持两种并行粒度：

表间并行（Inter-query Parallelism）：适用于 HNSW 场景。每个查询作为一个独立任务在单个核心上完整执行，多个查询在同一 CCD 的多个核心上并行处理，同一张表的所有查询尽量调度到同一 CCD。这种模式使得该 CCD 的 L3 缓存能够有效缓存 HNSW 图结构中的热点节点，在连续查询间实现缓存复用。

表内并行（Intra-query Parallelism）：适用于 IVF 场景。单个查询被拆分为多个子任务（对应不同聚类列表的扫描），在同一 CCD 的多个核心上并行完成，最终聚合得到 Top-K 结果。这种模式使得单次查询的延迟更低，适合 IVF 场景中对单次查询延迟敏感的业务需求。

统一接口的设计使框架可以无缝替换现有生产环境中的 bthread/OpenMP 调度逻辑，工程改造成本极低。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRllnUdPF3HmoSgooXPPWia96OMT0ff4rpDXlibiaUDURoU9wI9coVM7ticqABsKXoXiaCHy82NWRJVk68JL2jiadrpq5FT2XsClu6TWM/640?wx_fmt=png)

**3.2 冷热感知映射调度器**

调度器的核心任务是决定每张向量表在哪个 CCD 的线程池上处理，以及何时更新这个决策。

为准确量化各向量表的内存访问压力，框架基于搜索参数在线实时估算每张表的内存访问量（Memory Traffic）。基于流量估算结果，框架将所有向量表按内存访问量从高到低排序，然后通过贪心双端扫描算法进行 CCD 映射。

算法核心逻辑如下：每次从流量最高的表（热表）开始，将其与当前累计流量最低的 CCD 配对，同时将流量最低的表（冷表）也配置到该 CCD，形成 Hot-Cold 配对。通过冷热配对，使得每个 CCD 内部的总内存流量趋于均衡，同时避免多张热表同驻一个 CCD 引发的缓存争抢（Hot-Hot Co-location）。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRkhCdFsBxYVqYDRsS74Sl7JYKILicC2WAXv2zj8cLxLhSE5vIoHiaBXlbkc199Oia5slVEVztWIBNxeIuvWObT02LGtNgrTeDq8HM/640?wx_fmt=png)

业务流量随时间变化，不同时段的向量表访问热度会发生显著漂移。为此，框架采用可调节的时间窗口，例如：

● 快速窗口（10秒）：捕获短期流量波动，用于检测热表的快速变化。

● 慢速窗口（60秒）：捕获中期趋势，用于稳定的基线映射。

当快速窗口检测到当前映射与实际流量分布的偏差超过阈值时，在后台生成新的映射快照，并通过版本隔离机制平滑切换：正在执行中的旧任务继续在原 CCD 上完成，新提交的任务按新映射路由。这种设计保证了重映射期间无明显的延迟抖动。

**3.3 拓扑感知的层级化任务窃取**

在维持 CCD 内部任务路由的基础上，框架还需处理实际运行中的负载不均衡问题——某些 CCD 可能因为临时流量波动出现饥饿或过载。框架通过感知 CPU 硬件拓扑，建立三级窃取优先级机制来解决这一问题：

**第一级：本地队列弹出（Local Dequeue）**

线程优先从自己的本地任务队列中取任务执行，无任何跨 CCD 开销，这是零开销的理想情况。

**第二级：同 CCD 内窃取（Intra-CCD Stealing）**

当本地队列为空时，线程从同一 CCD 内其他线程的队列中窃取任务。由于同一 CCD 内的线程共享同一块 L3 缓存，被窃取的任务所需的向量数据很可能已经在 L3 缓存中存在，缓存命中率损失极小。

**第三级：跨 CCD 窃取（Cross-CCD Stealing，受严格限制）**

仅当同 CCD 内所有线程的任务队列均为空，且目标CCD存在严重积压（负载超过预设阈值）时，才允许触发跨 CCD 任务窃取。由于这种情况意味着整个 CCD 都处于空闲状态，此时发生缓存失效的代价相对可接受。

通过这一三级策略，跨 CCD 任务窃取率从 ~75%（HNSW）/ ~80%（IVF）骤降至 <10% / ~5%，在保持全局负载均衡的同时，极大降低了因任务迁移导致的缓存失效与 CPU Stall 损耗。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRn3Owk2GTH05IGeMaq58P1pIibfdshqibQfJSSf6bWDfmmTianfCl22WTGsziaWUdwEylttggvfaklrJD0qXywaUc25hd6pI7oo5Hg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRmpo2TPxj0fNO2dUnUOnOLpOsHBZKRb5bfpEibxrfKqtbR0024vcnmBjvYRVJIJf2RVGEgcvrXDH1CHjvibIMTksraATS8F1ht4A/640?wx_fmt=png)

**4.1 实验环境**

**硬件配置：**

● AMD EPYC 96 核（4代Genoa，12 CCD，每CCD 8核，L3 32MB/CCD）

● AMD EPYC 48 核（2代Rome，12 CCD，每CCD 4核，L3 16MB/CCD）

● 内存：576GB DDR5（Genoa）/ 512GB DDR4（Rome）

**测试数据：**

● 60个HNSW表：向量规模1M~10M，维度64~256，全部来自小红书线上真实服务

● 15个 IVF 表：向量规模10K~15M，维度64~256，全部来自小红书线上真实服务

● 测试负载：线上真实 QPS 流量，IVF Recall 90%，HNSW Recall 99%约束下测量

**实验对照：**

|  |  |  |
| --- | --- | --- |
| 版本 | 调度策略 | 说明 |
| V0 | Round-Robin / FAISS-InterQueryParallel | 原始方案，  无感知调度 |
| V1 | bthread全局任务窃取 | 现有最优方案，  无CCD感知 |
| V2 | 本文CCD感知框架 | 新方案 |

**4.2 吞吐量与扩展性**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRnffWQnhw8ibchtM44EtibEziaPCIINpHQu2gc5yLY9g1KC6pTPPzgh4kicfJ8XSAPb92bYejRbwiasq3e7c0sYIlvXZAWvaPCp6Piao/640?wx_fmt=png)

HNSW 场景，在 96核 Genoa CPU 上，V2 的饱和吞吐量达到 100+ KQPS，V0/V1约为 70 KQPS。更重要的是，V2 在 CCD 数量从 4个扩展到 12个的过程中呈近线性扩展，突破了 V0/V1 在 82% 理论利用率附近的瓶颈。

IVF 场景，在相同硬件下，V2 的饱和吞吐量达到 35 KQPS，V1 约为 25 KQPS，V0 仅约 10 KQPS。IVF 场景因每次查询的数据访问量更大，跨 CCD 缓存失效的代价更高，因此 CCD 感知框架的收益比 HNSW 更加显著。

**4.3 延迟改善**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRmtnE2OD5yuVP88IQQsjFD5pofkIDib58UG0YORlyvQ2p3aw4KywZZ5TxPqn2GLJoLw7xLYsk6T5jLfRT828iasCju4rgFICFSicI/640?wx_fmt=png)

在相同 QPS 负载下，P50（中位延迟）降低  30%~50%，P999 （长尾延迟）降低 60%~90%。长尾延迟的大幅改善尤为关键，P999 延迟直接影响最慢那批用户的体验。而此前长尾延迟高的根本原因正是偶发的跨 CCD 任务窃取引发的缓存重新预热——这在 V2 中被完全消除。在 1000秒的持续压测中，V2 的延迟曲线全程平滑无毛刺，而 V1 则出现间歇性的延迟尖峰（峰值比 V2 高出 2x~5x），这些尖峰对应的正是高频跨 CCD 任务窃取事件。

**4.4 硬件指标深度分析**

通过 CPU PMU 计数器对底层硬件指标的采集，进一步验证了 CCD Framework的作用机制：

|  |  |  |
| --- | --- | --- |
| 硬件指标 | V1 | V2 |
| L3 Cache Miss率（HNSW） | 基准 | 下降 6%~15% |
| L3 Cache Miss率（IVF） | 基准 | 下降 15%~30% |
| CPU Stall占比（HNSW） | 基准 | 下降 20%~40% |
| CPU Stall占比（IVF） | 基准 | 下降 40%~80% |
| 跨CCD窃取率（HNSW） | ~75% | <10% |
| 跨CCD窃取率  （IVF） | ~80% | ~5% |

L3 Cache Miss 率的下降直接说明了更多的向量计算在 L3 缓存内完成，减少了对内存的访问；CPU Stall 占比的下降则反映了 CPU 等待内存数据的时间大幅减少，计算资源得到了更充分的利用。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRkGWw3YVeuBffiazqAyVvbRaewd27724lJnN6dghy9Ee7vm2C9bfMRTPANKo6fjCXJM0KTscmQ6lRzCmcjuZVSwEicTNibZzaCUfc/640?wx_fmt=png)

本文系统性地分析了工业级向量 ANNS 服务在 CCD 多核 CPU 上面临的性能扩展瓶颈，提出了首个面向 CCD 架构的向量检索线程编排框架。框架通过冷热感知映射与拓扑感知任务窃取两大核心机制，同时解决了缓存亲和性与负载均衡两个长期对立的工程挑战，在不更换硬件、不修改索引核心代码的前提下，实现了最高 3.7× 的吞吐量提升和高达 90% 的长尾延迟降低。

该论文部分技术已于今年4月申请专利公开

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRnQeE7dEXHQyHrvPgL6JjznlxUw2cg4vr7J5bQfGmZBZZxOTpfACbkJnsM7RT64icxgiacEqubeISMC7fTg1Ycpr7Aa5rvZXFqHE/640?wx_fmt=png)

我们是小红书引擎架构团队，专注于打造 AI 时代下业界领先的搜推广一体化架构。团队深耕搜推广场景「存-检-算」技术闭环，在大数据处理、索引存储与检索、模型训推优化等方向积累了深厚的技术优势，团队技术成果发表过 WWW/ICDE/OSDI 等顶会论文，曾获得过 CIKM 2024 最佳应用研究论文奖，通过技术升级持续赋能小红书搜索、推荐、广告、电商、直播等多个核心业务。

本工作的主要作者包括黄宇辰，马百腾，孙一平，石旸，陈晓，钟晓诚等。

![](https://mmbiz.qpic.cn/mmbiz_png/P9Hs04VFGRlC2Yaicam5QcFXjRicEiaeiaHeCH3MaHgwxwic22lLOhBx0tNcwu8f0qneATdBXKvdhxZQKloljud0dGFbdt6A7tR64uhKg7sax2cQ/640?wx_fmt=png)

【REDstar】索引存储架构开发

**工作职责**

1.  深度参与小红书搜索/推荐/广告等核心业务，负责向量存储引擎、特征存储引擎、参数服务器、KVCache 等核心基础设施的研发与迭代，满足业务对高性能数据存储和检索的需求；

2.  攻克高并发、高可靠、高扩展场景下向量检索、特征存储、PS、KVCache 等方向的技术难关，识别架构瓶颈并推动体系化的架构升级；

3.  参与软硬件协同优化，探索 CCD 架构、NUMA 感知调度、SIMD 加速、新型存储介质等在 AI 存储与模型训推场景下的工程落地；

4.  深度跟踪顶级学术会议（OSDI/ISCA/VLDB/SIGMOD等）的前沿研究，将论文方向转化为可落地的工业级系统能力，并积极在顶会发表原创研究成果；

**任职资格**

1.  本科及以上学历，计算机、软件工程、电子工程等相关专业；

2.  编程基础扎实，熟练掌握 C++，具备良好的系统设计与工程实现能力；

3.  深入理解操作系统、计算机体系结构、分布式系统原理；有高性能计算、存储引擎或数据库内核开发经验者优先；

4.  对向量检索、近似最近邻算法（HNSW/IVF/PQ/量化等）有系统了解者优先；有 GPU/异构计算开发经验者优先；

5.  在顶级会议（OSDI/VLDB/SIGMOD/ISCA等）发表过论文者，或参与过有影响力开源项目（hnswlib/FAISS/Milvus等）者优先；

6.  有强烈的技术好奇心，善于发现深层问题、提出系统性方案并快速验证落地。

欢迎感兴趣的同学投递简历至：

zhongxiaocheng@xiaohongshu.com

![](https://mmbiz.qpic.cn/sz_mmbiz_png/P9Hs04VFGRmmhzu5Z5ZHaGs7u21oho3ZqhPSqJtDujLVI52BI8YP5tvTEZA8Bk57y4GO8sHlSrGr4k5WYhicmgYN8suIwN2F4u9vrbIiavV80/640?wx_fmt=png)