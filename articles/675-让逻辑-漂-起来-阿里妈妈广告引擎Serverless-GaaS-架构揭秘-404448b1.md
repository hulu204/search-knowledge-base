---
title: '让逻辑「漂」起来：阿里妈妈广告引擎Serverless（GaaS）架构揭秘'
company: 阿里妈妈
tag: 工程相关
date: 2026-01-15
url: https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496921&idx=1&sn=70f568577ffbf6fc51a1f08aec0423cf&chksm=c10d43e67ae14254561730a6d8fea4dcebf0394c371c78ff4f09915b2c3d747e8fbc2862fba0&scene=0&xtrack=1#rd
account: 阿里妈妈技术
origin: harvest-202607
---
# 一、“通” 是阿里妈妈效果广告过去几年的核心主题之一

2021年之前，阿里妈妈广告业务是搜索广告、展示广告、直播广告等多驾马车各自发展的局面。2021年阿里妈妈推出了「万相台」，一定程度实现了客户一笔钱可投放到阿里妈妈的所有土地上。2024年8月进一步推出了「万相台无界」，允许客户一笔钱在关键词/人群/货品全站/直播短视频各场景间自由腾挪，在不同土地上最优分配。这样**「预算通」、「土地通」**的产品，给了客户更多自由度，同时也给了技术侧更多的优化抓手，对于广告主和广告平台来说是双赢的。

不同引擎承接不同土地的流量，是业界共识的架构范式。如何让一笔钱花在不同的土地上，要解决同一个花钱逻辑如何同时在不同引擎生效的问题。换言之，业务上的「预算通」其实需要「引擎通」。

在这样以「通」为主题的业务和技术发展趋势之下，我们提出了[Serverless](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490372&idx=1&sn=78c29b30b59305a43f44c4d6a1d4b7e4&scene=21#wechat_redirect)的广告引擎架构范式，使得业务能力可以「一处开发按需集成」。更进一步，我们实现了 开发、测试、实验、生产交付 全链路迭代颗粒度对齐到「能力」，而阿里妈妈广告引擎对能力的承载形式是Graph（有向无环图），因此我们提出**Graph as a Service（GaaS）**的新玩法。GaaS已经很好地帮助业务解决了跨引擎/跨模块出价的迭代效率问题（开发自测提效: **1倍**以上；变更发布提效：70%），对不同场景、在离线系统能力复用也提供了巨大的助力。

在广告引擎这样一套复杂的系统中真正落地Serverless范式，是有挑战的，业界也鲜有耳闻。本文简要介绍了GaaS背后的思想，主要的方案，以及实际业务落地情况。

本文完整作者：应灵，飞驳，天形，子瑞，画沙

# 二、GaaS的核心是从开发到交付全链路颗粒度对齐到Graph

GaaS是阿里妈妈广告引擎以业务能力（通过图实现）为基本单元的交付范式。相较传统Serverless方案（如 FaaS），GaaS聚焦于在满足对系统低延迟、重数据、高频迭代 等系统约束的前提下实现敏捷交付。

我们将广告在线引擎逻辑进行「细粒度重构」，形成诸多合适粒度的Graph。GaaS核心提供对Graph的规范化封装，同时在Graph粒度上，提供 开发、自测、实验、发布 能力。具体包含了如下5个核心组成部分：

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZJo94uCgHPJyBN2Ol2J9RJsl7gdVDiaLHnAXwYbeED0vfuyPJTX7URFt7DFnaR3XMh8KsOckD5f0A/640?wx_fmt=png&from=appmsg)

图1: GaaS核心能力体系架构全景图

* **基于能力重塑**：基于运行时、数据表达、范式统一的全图化引擎，以业务能力为粒度对引擎业务做整体做细粒度重塑，是GaaS运转的底层逻辑支撑。
* **面向能力开发**：构建以算子（底层计算逻辑）、编排、数据为整体的编译部署单元，实现业务视角的“能力”与工程交付视角的“图”概念对齐，是GaaS的工程基础。
* **面向能力自测**：解决在线引擎运行时环境的轻量级拉起难题，将能力的测试从集成测试轻量化为本地单测，是GaaS的效率核心。
* **面向能力实验**：解决能力升级后对所关联业务的实验感知、拉起及统一验证问题，避免图复用后验证成本的线性增长，是GaaS可持续推广的成本保障。
* **面向能力发布**：解决能力触发多业务发布的数据部署与发布效率问题，实现引擎变更以能力版本做统一对齐，是GaaS的最后一公里拼图。

# 三、来时的路：通过几个「统一」，让引擎逻辑片段互认

GaaS的基础是，要有粒度适当的逻辑片段可构建在线引擎全链路流程，然后这些逻辑片段的部署不受模块/服务限制。在往期文章[《新时期的阿里妈妈广告引擎》](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490372&idx=1&sn=78c29b30b59305a43f44c4d6a1d4b7e4&source=41&poc_token=HJHkWWmjSj8lk35_K1DRkrgHwWgFo2oNWMlagwyY&scene=21#wechat_redirect)的工作中，我们通过以下三个「统一」实现了上述基础要求：

* **统一运行时**： 将引擎从控制流全面切换为数据流模式，实现了业务编排与底层执行的解耦。引入图编译优化以保障高吞吐、低延迟的同时，让开发者从复杂的数据分发与并行编排中解脱，专注于逻辑迭代。基于此实现各引擎各模块的**运行时互认**。
* **统一数据抽象**： 将各类异构数据统一建模为 Table（二维表）并交由框架自动化管理，使业务开发能够通过配置化方式**透明地消费数据**视图，显著解决了广告引擎重数据依赖的痛点，提升了交付效率。
* **统一业务抽象**：规范业务算子通过标准的Schema交互，并剔除了“大Session（Context）”数据总线，推动了逻辑片段的原子化与**无状态化**，为算子在各模块间的“自由漂移”及全链路逻辑重组扫清了障碍。

在上述三个「统一」的工作之上，阿里妈妈广告引擎具有了业务能力在不同模块、引擎之间互认的技术前提。我们进一步对业务逻辑进行体系化建模：基于 BP 能力与土地机制对引擎能力实施 MECE 式拆解并以图粒度承载，实现了以图为标准交付物的引擎研发范式。

以无界BP的“设置预算及出价”能力为例，通过统一的出价范式定义，我们实现了不同土地（搜索、展示）、不同营销场景、不同出价方式在底层共享同一套“出价内核”。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZJo94uCgHPJyBN2Ol2J9RJxQrXTUibHRPSo91tKKpBJQwBia9wMAL3icvOQ17xBYQWVXsHdcEzY1PYA/640?wx_fmt=png&from=appmsg)

图2: 出价子图的动态漂移示意（在线高性能场景 vs 实验低成本场景）

进一步地，针对出价实验在重数据模块（如检索节点）拉起资源成本高的挑战，我们利用**图漂移能力**，支持出价子图根据场景灵活切换部署位置：在线接流阶段部署于“本地”以追求极致性能；实验阶段则“漂移”至远端节点，以极低的部署成本实现快速迭代。

# 四、面向能力开发：将引擎逻辑片段抽象为Graph，是GaaS的前提

阿里妈妈广告引擎基于**EADS图引擎框架**搭建，图可以表达一段任意粒度的引擎/业务逻辑，小到一张图中可以只有一个UDF（算子），大到召回引擎的完整图描述，甚至整个广告引擎都是一张可在一个进程中被EADS框架加载执行的图。基于之前描述的数据总线Table、运行时框架等统一的基建，引擎逻辑抽象为Graph已具备充分的技术可行性。

* **Graph定义**：Graph包含基于python脚本（TableAPI）描述的DAG流程、业务自定义UDF（C++）插件、算子所依赖的数据schema定义 等。
* **Graph调用**：可以在TableAPI描述中，通过「图接口」直接完成对子图的调用。
* **Graph编译：**根据图编译脚本（bazel BUILD）描述的主图（A）调用依赖子图（B）的方式（inline/local/remote），完成主图A到子图B的实际编译部署物。这一过程可类比C++程序对第三方库的处理方式——根据需求选择静态依赖、动态依赖或RPC调用。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZJo94uCgHPJyBN2Ol2J9RJEfQictKIZ3uHxyVBzuYgZzDibeBUmgPcVbib3MCCLtfPSqRsXicB0E2ibuA/640?wx_fmt=png&from=appmsg)

图3：面向能力开发

# 五、面向能力自测：让Graph可以Local化跑起来，是GaaS的灵魂

集成测试是引擎迭代的重要质量保障。 GaaS打通了开发侧算子集成与图集成相关能力, 也对集成测试提出了「更高」/「更全」/「更广」的需求, 只通过传统的应用粒度的回归, 已经不能满足GaaS模式下**所测即所变的要求**。因此，Local化的集成自测呼之欲出。

图测试需要准备输入Table，索引数据，校验输出Table, 我们将这些流程的业务接口统一暴露为Python接口, 将图测试用例设计为Python测试用例, 通过Python的易用性与「AI-Friendly」特性, 降低图测试的构造门槛, 使图测试作为开发环节的必选项。我们将整个流程抽象为「测试图构造」, 「本地运行时」, 「数据构造与结果断言」:

* **测试图构造**:  提供接口Mock能力，实现对测试图进行上下游数据Mock构造。提供Mock过程中对图执行流程的必要改写能力, 从而将原图重构为测试图，进而实现图的本地运行。
* **本地运行时**:  提供小索引构建能力，利用图编译能力完成对被测试子图的编译、校验逻辑插入及具体调用。最终实现了本地运行Graph所需要依赖的简化，且优化单图测试时间到分钟级。
* **数据构造与结果断言**:  在图测试中提供了基于Python的Table数据结构, 支持业务使用Python完成图测试输入数据构造与输出结果断言,  极大地提升了图测试的易用性。

通过「测试图构造」, 「本地运行时」, 「数据构造与结果断言」等模式, 我们成功将一个EADS图的集成测试建模为在Python中的一段UT测试逻辑, 这大大优化了传统的基于生产实验环境的集成回归逻辑, 提供了真正的面向「能力」的集成回归, 使业务能根据能力丰富图回归, 有效地保证了GaaS的安全落地。

![图交付公众号.svg](https://mmecoa.qpic.cn/mmecoa_svg/kSiaeFj92SMwgk83beYzQYnv8TlxDFVv3JOpfMPy7MMJrDUgbFkRjetYhw2IBSVJgDiaJG7Ylw3PWJK0ur1Jd94mheogZic4kwQ/640?wx_fmt=svg&from=appmsg "图4：面向能力自测")

图4：面向能力自测

# 六、面向能力实验：通过Graph触发实验验证，是GaaS生产落地的关键步骤

实验是引擎迭代的关键步骤，在这个环节，不仅要验证迭代的效果，更要验证迭代的稳定性。阿里妈妈在过去几年已规模化应用了引擎模块级的生产实验能力，对生产流量和资源进行科学敏捷管理，实现了引擎模块迭代的低成本高效验证。

在面向能力迭代的背景下，也需要面向能力（即Graph）建设配套的生产实验能力，这是GaaS走向生产的关键基础设施。这套实验能力包括以下几点：

* **Graph血缘分析**：构建维护Graph到模块的拓扑关系，是面向Graph的精准实验以及后续精准生产发布的关键能力。在没有拓扑关系的情况下，只能人工识别实验对象，难以避免出现遗漏或者实验资源浪费。我们的系统在引擎代码变更后，可自动提取并更新这一拓扑关系。
* **Graph精准实验**：用户以Graph为视角触发实验，系统基于血缘分析结果，精准定位需要实验的模块和业务场景，自动的进行相关实验构建、部署和流量接入。这一过程中用户只需要提供Graph及其变更信息，即可保证受影响的模块和业务场景都可以被验证到。
* **全局实验分析**：多业务场景实时效果监测和结果聚合，多引擎模块下钻到Graph的实时监控，这些基础能力有效的保障了Graph实验的最终目标，一次实验得到包括效果和稳定结论的各业务场景的正确验证结果。

基于面向Graph的实验能力，阿里妈妈广告引擎实现了GaaS高效的**「一处开发，多处验证」**。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZJo94uCgHPJyBN2Ol2J9RJvozCia5NONbQWNOsUeEQzmkqDOibA2bhQP5FORQao6VVpxvGythGtDOA/640?wx_fmt=png&from=appmsg)

图5：面向能力实验

# 七、面向能力发布：通过Graph发起生产变更，是GaaS的使命

面向能力即Graph的发布，能力成功交付到生产系统才是GaaS使命的达成，GaaS的Serverless理念在这一环节得到最终体现。面向Graph的Serverless发布主要体现在以下两点

* **Graph精准发布**：用户以Graph为视角触发生产变更，同样基于血缘分析结果，精准定位需要变更的模块和业务场景，并行进行多模块的生产变更。针对不同业务场景对Graph的差异化使用，我们对Graph发布流程进行了概念抽象，来满足这一诉求。
* **Graph灵活部署**：GaaS的一个核心Serverless能力是Graph作为可独立运行的实体，具备可灵活漂移部署的特性。Graph可以被模块本地inline调用从而获取最优的调用延迟，或者被远程调用获取最佳的迭代隔离性，也可以被动态子图调用来平衡调用延迟和迭代效率，不同的业务场景可灵活调整部署方式。

基于面向Graph的发布能力，阿里妈妈广告引擎实现了GaaS高效的「**一处开发，多处发布**」

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZJo94uCgHPJyBN2Ol2J9RJOmFJ5hDTdCaibcLJViaWdH5Umt697vvXd4A5WAxzXXvGyic5KbJoWZq4A/640?wx_fmt=png&from=appmsg)

图6：面向能力发布

# 八、完整秀出来：广告引擎GaaS对智能出价迭代的体验提升

以智能出价为例，GaaS显著提升了引擎能力的交付效率。作为广告引擎的核心商业能力，智能出价被广泛集成于多种流量土地（搜索、展示、内容等）的多个阶段。其核心逻辑包含了：个性化出价算子（C++ 实现）、横向复用的通用出价内核子图，以及支撑在线计算的算法数据。

在GaaS落地前，尽管逻辑可复用，但交付碎片化严重：集成侧需手动维护复杂的编译配置，逻辑验证深度绑定物理服务部署，效果验证需逐个渠道手动同步。这种按服务粒度发布的模式，节奏慢且极易导致全链路版本不一致（漏发）。

![](https://mmecoa.qpic.cn/sz_mmecoa_png/sZ8T6nJp48ZJo94uCgHPJyBN2Ol2J9RJOFISKx5EBZFgZ3eZ5E4v23DOqIgvNMpuVXAVHF3XSrnp3qlTJt0gmg/640?wx_fmt=png&from=appmsg)

图7：完整案例——智能出价在 GaaS 落地前后的全链路交付流转对比

GaaS从根本上解决了上述问题。如图所示，在不降低验证质量的约束下，出价交付被收敛为统一的“图资产”交付，实现了研发效率与质量的双重飞跃：

* **开发阶段**：智能出价子图提供者保障所需能力的闭环交付及验证，从而**规避了在不同部署集成时的差异化兼容问题**。

  ```
  load("eads_graph")  
    
  eads_graph(  
      name = "bidding_graph",  
      graph_main = "bidding_graph.py",  
      # 仅需申明图内新增的  
      # 编排、算子逻辑、数据  
      py_deps = [],  
      eads_udfs = [  
        ":bidding_udf",  
      ],  
      eads_datas = [  
        ":my_promotion_bidding_data"  
      ],  
      # 通过图之间的依赖关系解决  
      # 间接依赖编排、算子的依赖关系  
      graph_deps = [  
        "//graph:fetch_param_graph",  
      ],  
  )
  ```
* **自测阶段**：以往依赖完整服务的集成测试，现在被轻量化为基于标准 I/O 的图自测。通过 Mock 输入表与算法数据，**在本地即可完成高仿真的逻辑闭环验证**。GaaS首次实现了Graph逻辑的本地测试，大大降低生产变更的返工频率。

  ```
  from turing_script.ad_table import AdTable  
  from bidding.graph import bidding_graph  
    
  class BiddingTestCase(EADSGraphTestCase):        
      # 用于执行图测试  
      def test_demo(self):  
          # 支持子图输入输出表构造        
          ad_table = AdTable.from_csv_file("ad_input.csv")  
          in_tables = {"ad": ad_table}  
          expect_table = AdTable.from_csv_file("ad_output.csv")  
    
          # 执行待测试子图  
          out_tbls = self.run_graph(inputs=in_tables, fetches=["ad"])  
    
          # 验证结果  
          assert table_equal(ad_table, expect_table)
  ```
* **实验阶段**：**实现了全局实验的一键启动**。依托图血缘能力，系统可自动识别出价子图升级所涉及的引擎模块，并同步完成相关业务场景的流量配置。在效果回收阶段，支持全域维度的指标聚合以及面向特定业务维度的深度下钻分析。以该场景为例，GaaS方式实验效率提升70%。
* **发布阶段**：**生产发布全由出价子图变更驱动**。利用血缘识别联动多个服务发起发布；同时，针对不同业务场景对调用延迟与开发效率的平衡需求，支持子图以“内联融合（Inline）”或“跨图调用”的差异化范式进行灵活部署，实现性能与灵活性兼得。以该场景为例，GaaS方式发布效率提升75%。

# 九、展望：GaaS不是终点，大模型时代，AI研发扑面而来！

我们通过图粒度的在线引擎能力建模，围绕图交付的基建升级，构建了基于GaaS的引擎能力交付范式，本质是面向在线广告引擎场景构建了一种AI-Friendly的软件工程架构。这套软件工程思想在大模型时代依然行之有效，甚至可以说正当其时：

* 更清晰的逻辑拆分本质上是更精准的领域建模，让大模型“理解代码”更有迹可循
* 更明确的引擎能力拆解是更精细的工程规范，让大模型“新增代码”更有理可依
* 更多颗粒度（Graph）的可测性是更强的质量抓手，让大模型“验证逻辑”更有底气

基于这套 AI-Friendly 的架构，我们已经在**引擎研发范式的AI化重塑**上迈出了坚实的一步：

* **Source Code As Document**：我们构建了以代码为主要依据的知识库，实现了日常编码建议、功能答疑、运维知识查询由向人咨询到向Agent咨询的转变。很大程度解决了文档缺、文档老、文档不准 的研发顽疾。
* **AI·Coding**：以编码规范 及 依赖知识（代码知识、业务知识） 为基础，我们实现了从原始需求出发，到技术方案生成、算子/子图编码、本地验证、实验拉起 等，端到端可由AI Agent辅助完成。部分领域的产品需求已默认通过AI辅助开发。

未来，我们将继续探索AI Agent与引擎架构更加激进、更加深入的融合，敬请期待！

# 💡 关于我们

我们是阿里妈妈广告引擎团队，是支撑着国内最大广告业务的核心技术力量之一。我们正在用前沿技术重塑广告引擎的未来：用Serverless架构、AI-Coding 持续提升研发效率，用GPU/PPU推高算力天花板，用数据驱动探索大盘提效。真诚欢迎具备扎实的C++编程、数据结构算法基础，对高性能、分布式架构有经验，对AI研发有兴趣 的同学加入，一起玩转新时代的广告引擎！欢迎投递简历。

**📮 简历投递邮箱**：taobao\_techhire@service.alibaba.com

END

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc6nDBjJbezO2dMG543RhUibcELU7juTxCMBicyhVZFabfkasM6z5KADwjiar6FZz9icibn5FYdllnUENbQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&randomid=pugabtu8&tp=webp#imgIndex=9)

****也许你还想看****

[阿里妈妈展示广告引擎动态算力再探索：面向业务收益的机器自适应调配](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490392&idx=1&sn=981d9dcd2158af2de6b1a064ffee92f9&scene=21#wechat_redirect)

[阿里妈妈展示广告引擎新探索：迈向全局最优算力分配](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490372&idx=2&sn=70199c83ced6d0ca55c71590c8513c00&scene=21#wechat_redirect)

[新时期的阿里妈妈广告引擎](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490372&idx=1&sn=78c29b30b59305a43f44c4d6a1d4b7e4&scene=21#wechat_redirect)

[KDD'25  |  Bid2X：基于基础模型视角的广告竞价环境建模](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247496899&idx=1&sn=4ef3db0db5b208fc5306c2bd51545e5d&scene=21#wechat_redirect)

**关注****[「阿里妈妈技术」](https://mp.weixin.qq.com/s?__biz=Mzg5NTk4MDMwMA==&mid=2247490308&idx=1&sn=66643c1468bcec7a05449aedea9dc603&source=41&scene=21#wechat_redirect)，****了解更多****~**

![图片](https://mmbiz.qpic.cn/mmbiz_gif/0bUHKeoZbc5sXK3vmdVml8YvHjw8nTribOFowib9cDK9PXhlrIibXGePJMRPwXkx1DUVE2ru1bfTHvpsp0Rj6B6ibQ/640?wx_fmt=gif&wxfrom=10005&wx_lazy=1&tp=webp#imgIndex=15)

喜欢要“分享”，好看要“点赞”哦ღ~