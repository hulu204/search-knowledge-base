---
title: '快手 Dragonfly 策略引擎的设计与应用'
company: DataFun
tag: 搜索
date: 2023-12-16
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247699295&idx=1&sn=7126999aa8e875f3c2c2ca8ad60d7b68&chksm=fbd87933ccaff025d85bb82d7d9f558e37cc78e4000882cfbdd5110d19b16c1c8d86f35f0ce8#rd
account: DataFunTalk
origin: wechat-mp
---
**![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzicG4JNibg4fM4icRVwXP5UmibMEaiaiapF9TBxMcG8Aguyicy2ica6QzY0gjnzMZudFHyibWhWXhbIMJdC6w/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiajvrlw9oGnZDr4mJsGCMibYT1XdmEKk3V5VVrdqicJHnCzmhLw84YaQiaictMEUM4XJGGlwicleggoaFA/640?wx_fmt=png&from=appmsg)

**导读**本文将分享在设计和应用策略引擎方面，快手是如何应对逻辑复杂且难以抽象的系统问题的。

******主要包括以下五部分：******

1. 问题与挑战

2. Dragonfly 框架介绍

3. 生态建设

4. 规划展望

5. 问答环节

分享嘉宾｜方剑冰 快手 推荐系统架构师

编辑整理｜张翎

内容校对｜李瑶

出品社区｜DataFun

---

**01**

**问题与挑战**

**1.** **问题背景**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvpyzd70sPqLy1HO8U6icKBVQlicfWr3ic9ooVunC9hrrS0qhopmsUtx5YQ/640?wx_fmt=png&from=appmsg)

从 2018 年开始，快手的整个业务呈现快速发展的状态，团队也在快速扩张中。在过去的五年中，DAU 从 1 亿增长至 3.76 亿。在 2021 年，快手的 DAU 已经超过了 3 亿。主要推荐场景也从早期的发现页、关注页和同城页等几个主要页面，扩展到了如今的上百个推荐场景，包括电商、直播、增长、海外及本地生活等等。

伴随着业务的快速发展，研发团队从几十人扩大到了上千人。在这种背景下，业务方面产生了两个主要诉求：第一个是希望快速搭建一个新的推荐场景；另一个是快速复制有效的策略。

**2.** **问题**

早期，为了满足这两个诉求，开发团队选择复制已有功能的架构代码，以加速开发过程。然而，随着场景数量的不断增加，这种方式已难以接受。因此，从长远来看，快手需要重新审视并优化现有的代码架构，以确保其能够适应未来的发展需求。

同时，这种做法还会增加整个架构的维护难度。在快手，架构和算法人员配比较低，导致架构工程师压力较大。在线系统所有代码都是用 C++ 语言编写的，随着算法团队人数的增加，系统越来越复杂，对线下代码质量的把控变得更加困难。经常因为代码 bug 导致线上稳定性问题。

另外，工程团队和算法团队之间存在天然的目标差异。例如，算法团队追求快速迭代和实验上线，而工程团队更看重系统维护成本。因此，快手需要平衡两个团队的需求和目标，以确保整个系统的稳定性和可维护性。

另一种严重的情况是，项目的整个算法和工程代码写在同一个工作空间中，导致代码存在严重的耦合现象，就像 DNA 双链结构，彼此相互支撑，又相互纠缠在一起。这就意味着双方都可能对对方产生一些意外的影响。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvfZIwiaba1aYdooomOxhoFhKF4A7KqWK3BXHWlicibnXBW8vpnEL5jicX7w/640?wx_fmt=png&from=appmsg)

在这样一个模式下，工程团队往往会陷入循环重构的怪圈。随着系统迭代时间的不断增长，整个系统的复杂度也逐渐提高。当达到一定阈值时，工程团队需要投入大量人力进行系统的重构。重构完成后，系统的复杂度会降低到一定水平，但随着时间的推移，经过一两年的迭代，系统又会变得复杂起来，需要再次重构。这种周而复始的现象每 1~2 年就会发生一次。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvdqpcwDWTWjvcbVUOC789JMHaOcl4kLod7OKRa27LoMIR8hEQ2Ga1aQ/640?wx_fmt=png&from=appmsg)

每次进行这样的大型重构，对工程团队的消耗非常大，导致团队成员很难集中精力去关注其它更有价值的架构升级。因此，如何打破这个循环重构的宿命就成为了一个急需解决的关键问题。

经过深入分析，团队发现了问题的核心原因是业务代码和架构代码之间存在过度的耦合。为了解决这个问题，快手自主研发了一套策略引擎框架。下面将详细介绍该框架是如何解决这些问题的。

**02**

**Dragonfly****框架介绍**

**1.** **Dragonfly****是什么**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvae8M9GICjA4kwo47JZbR7RuialB5Ps8kt2NhD0UQenrgUOnG91mqVMw/640?wx_fmt=png&from=appmsg)

Dragonfly 在定位上是一个面向搜广推领域的通用图引擎框架及其周边工具所构建的开发生态。该系统为快手内部搜广推服务提供了统一的基座引擎，同时为上层业务提供了灵活的流程编排能力。

在底层，内置了一些高效的数据模型，并提供了丰富的周边工具。上图展示了整个架构，最上层是各个搜广推领域的策略引擎，下面是支持策略服务、召回服务、粗排精排服务的核心层，最底下是图调度引擎。通过DSL算子编排，成功地将算法的开发模式从 C++ 为主转变为以 Python 为主。

**2.** **策略编排**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvRibliaBK6I8ibQniaMicjEbH5Dm8pm0LnoldEbiaeqUYEzSuJLv4xyxpPwVw/640?wx_fmt=png&from=appmsg)

上图中展示了一段代码示例，以 Dragonfly 编写策略的方式呈现，非常直观。代码定义了一个 flow 流程对象，类似于工作流的概念。在这个 flow 中，提供了很多方法，每个方法背后都有一个相应的算子。通过脚本，可以很容易理解这个流程。前两个方法是两步召回，从索引和服务中做召回，之后进行去重、曝光、过滤等。再根据 dislike 特征进行过滤截断。接着进入下一个阶段，进行多样性的打散，然后进行截断并返回。

通过 Python 的 DSL 描述，算法同学可以不编写 C++ 代码，而是通过 Python 脚本简单、直观地描述一段策略流程，这个 DSL 脚本将被编译成一个 Json 文件，交给线上的 C++ 服务运行。这样既享受了 Python 编写逻辑的便利性，也没有牺牲线上的性能。

为了实现这个效果，我们做了两个核心的抽象：流程抽象和数据抽象。

**3.** **流程抽象**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvH2Kua5Huib6j6QeBmztwbZazibcib4HF4B92ertFp8bbQubxPQwq8ibXOQ/640?wx_fmt=png&from=appmsg)

利用算子化的方法加上 DAG 来拆分和抽象整个业务功能为各个算子。这些算子包括一些通用的算子，如过滤、召回、模型预估等。这些算子基本上由架构编写和维护，各个业务可以直接复用，无需重复编写。

通过自定义算子来满足一些通用算子无法满足的定制化的业务逻辑。这些自定义算子可以由业务人员自行编写，以实现高度灵活的需求。

通过使用先前展示的 Python DSL，开发人员可以轻松编排这些算子。并且，由于这个脚本本质上是一段 Python 代码，因此可以在此基础上利用 Python 自身语法能力实现更复杂的代码拆分及模块化管理等功能。

整个 DAG 构图方式是基于数据驱动的隐式构图，因此，所有的算子都可以做到全流程漂移。

如图所示，假设我们有一个包含六个算子的 flow，其中 B、C、D 三个是异步的算子，它们分别有下游依赖 E 和 F。根据数据依赖关系和拓扑序，可以唯一地反推出一幅 DAG 图，其中 B、C 是并行的关系，B、C、E 整体与 D 也是并行的关系。因此，整个流程的处理结构就像上图中部所示。

通过这样的构图机制，理论上可以构建出任意复杂的业务逻辑和业务流程。这里提到的可全程漂移意味着，如果将各个方法随意换位置，那么构图的结构也会自动发生变化。

最后，整个流程的调度是一个全程无锁的设计，以支持在线的高并发需求。

**4.** **数据抽象**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvVEZibwpKmptoF89gUwr2TlsWtC0RRPxj8rfcqCxRHs4CI4yHJIg2pmw/640?wx_fmt=png&from=appmsg)

除了流程抽象，Dragonfly 具备的另一项重要抽象能力是对数据的抽象。它提供了一种高性能的数据结构，叫做 DataFrame 表结构，类似于大数据领域中列存表的概念。

从逻辑上看，DataFrame 表结构就像图示的二维数据表，以 item 侧的数据为例，每行代表一个 Item，每列代表其属性或特征。Common 侧的数据实际上也是类似的，但因为 common 的数据对于所有item都是共享的，所以作为底层使用一个特化单行的 DataFrame 结构去承载。通过这样的 DataFrame 结构，可以比较容易地实现统一数据接口的能力。例如，Dragonfly 架构为上层提供的是一个简单的键值化数据接口，如果一个 item 想访问一个特征的值，只需要传入 item 的 key（一般是 item \_id） 和 like 这个名字，就能获取到这个值。Schema Free 的特点确保了在线系统不需要因为添加新的特征或数据而频繁重新编译，这比 protobuf 更加易用和高效。

此外，Dragonfly 框架对结构进行了诸多性能优化，例如零拷贝技术，这种技术贯穿于索引数据以及DataFrame间的数据传递等各个方面。

Dragonfly 框架更高级的功能是对逻辑表的全面支持。在复杂的业务场景中，可能需要处理一张大型物理表，每个团队只需要专注于其中的一部分流程。因此，可以基于底层物理表创建逻辑表，这一概念类似于数据库中的视图。与视图的只读不同，Dragonfly 架构创建的逻辑表具有可读写性，可以作为其他团队划分数据操作空间的参考。通过这种方式，整个团队可以更清晰、更灵活地管理其数据操作空间。

通过统一数据接口，我们得以轻松地进行数据读写管控，可以轻易地梳理并监控在线数据的读写使用情况，包括是否存在不合规的数据使用。整个框架内置了安全保障机制，确保了数据的并发安全。

**5.** **DSL** **层提供高阶抽象能力**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvWnh3AwsAHSuTpcDKY2YcG09eWGSteQ8ulhL4bJ8K09DdibtJNn2jscA/640?wx_fmt=png&from=appmsg)

前面介绍的是框架底层的核心能力，但用户主要会感知到的是 DSL 这一层。Dragonfly 提供了一些更高阶的抽象能力，如标准算子的封装，用户可以直接使用。对于用户来说，同步或异步是无感的，只需要简单地调用算子接口，无需关心底层是同步还是异步实现。

此外，Dragonfly 在底层提供了分支流程控制、数据并行计算等高阶功能。如上图展示了数据并行计算的示例，假设要计算某个分数，类型为 double，如果每个计算的分数需要一毫秒，那么 8 个串行计算就需要 8 毫秒。但是，实际上每个分数的计算都是独立的，可以将其视为数据上的并行操作。通过框架提供的 @ parallel 装饰器，可以指定参数将数据分片，每片包含 4 个 item，每个线程处理一片数据，实现并行操作，将 8 毫秒降低到 4 毫秒。原理上跟向量化加速是一样的。

对于流程，Dragonfly 提供了@async装饰器帮助将子流程异步化，还提供了模块化组件帮助上层 DSL 构建更复杂的业务逻辑。与传统的 C++ 代码实现相比，使用 Dragonfly 的 DSL 只需要简单地添加装饰器即可实现诸多复杂的功能。

**6.** **分层解耦**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvazmAicc0iam7fZ1OVGl1UzvZKBwl7SLh3L8rK3Fic0FBT724VM0a5vvuQ/640?wx_fmt=png&from=appmsg)

通过 Dragonfly Python DSL 我们将整个算法和架构的研发工作空间进行划分和隔离，实现层次分明。在 DSL 之上是算法的工作空间，算法人员只需要编写DSL编排算子并提交配置，而无需关心底层算子的实现。在 DSL 之下是架构的工作空间，架构人员只需要编写算子，并提供二进制文件以运行配置。架构对于上层业务逻辑无需关心。这样就实现了清晰的层次划分，使得两者之间不会产生强烈的耦合效应，避免了互相干扰的情况。

**7.** **应用现状**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvVdZv9qE4WUoTOXiccV4cqk5ViaeH96CcDheNicUmk1yKEPBibevnHZK5Sg/640?wx_fmt=png&from=appmsg)

当前，Dragonfly 已经支撑了整个搜推广领域的上千个在离线服务的运行，实现了覆盖整个推荐在线核心链路的技术模式。如图，应用范围不仅覆盖策略服务，还包括整个链路上的召回服务、粗排精排重排等服务。

通过采用这一套技术模式，实现了几个重要的目标。首先，统一的技术模型实现了整个在线服务协议。这个技术模型也为我们提供了便利的监控条件，可以轻松监控整个链路每个服务的内部算子情况、CPU 消耗等系统资源指标。此外，一些底层优化和编译器优化也可以通过一次开发，在所有服务中复用。

当所有服务都采用这一套模式时，全链路将呈现一个灵活的状态。这意味着链路节点上的每个节点都可以灵活地切分和融合。如果某个节点的服务随着业务迭代时间的延长而变得臃肿，导致单机资源无法承受，可以将其从大单体服务切分为两个小单体服务。同样，如果发现某些服务对单机的资源消耗过低，可以将上下游的两个服务进行灵活融合，将其变为一个服务。这种灵活的架构可以像微架构一样，使我们能够灵活地调整整个链路的架构，包括新旧服务的迁移。根据迁移经验，采用这一套技术模式可以使原有服务的 C++ 代码量减少 50~80%，显著降低了代码的复杂性和线上稳定性安全风险。

**03**

**生态建设**

**1.** **生态工具**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvsdBff7OzvXziaibfTBjrlhxlib9wXkzcPL8poxTQ9YGicP6goSDJjibvZVQ/640?wx_fmt=png&from=appmsg)

为了让业务团队高效地使用这个框架，仅仅做好一个框架是远远不够的。要让用户充分体验到这个框架的优势，需要构建一个庞大的生态系统工具。

上图展示了目前提供的相关工具。这些工具覆盖了整个策略研发的全流程，包括上线前的编码辅助、功能调试，以及上线后的指标监控和报警分析。这套框架的最大优势在于，所有这些生态工具都可以做到一次建设全业务复用。接下来介绍几个重点工具。

**2.** **Playground**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvETPj3IKphSBlNGFic7xOQyRekV57Y6fL3VX1DKHaciaxuticwGg6xY97Q/640?wx_fmt=png&from=appmsg)

这是网页版调试工具，用户可以在页面上直接编写 DSL，并通过网页运行查看结果。通过这个网页版工具，用户可以实现零部署的在线编写调试。秒级响应，用户可以在 Python 代码中简单构造输入输出数据，并执行查看效果。用户除了可以直接查看结果，也可以通过 Python print 查看流程中的特征数据，或查看底层 C++ 算子的 glog 日志。这样可以帮助用户方便地调试程序逻辑。

**3.** **白盒化回查**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvyqicegZ1p0wiaFzac6FVw7DyakKPe5icH57GHvOa4KNbxR2Q98K3u3hbQ/640?wx_fmt=png&from=appmsg)

针对已经上线的在线服务，如果出现不良情况需要调查，整个框架具备自动打点的功能。通过用户 ID（uid），可以追踪历史记录中某条请求的完整执行情况；可以了解到该请求经过了哪些算子，每个算子的耗时和输出数据等详细信息。通过这种方式，开发人员可以进行历史追踪，排查可能出现的问题。

**4.** **可视化**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvsSeofwD9QdJIXBWBzibNh3CHyIVXmhgc62nJicjsNwxficQeQYRS5UA2Q/640?wx_fmt=png&from=appmsg)

通过这种方式，可以从上至下、由粗到细地展示业务流程，能够更清晰、直观地了解整个业务流程的概况。

**5.** **代码治理**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dv4PoLrib2rtZ0xO2wXZh4n8Tz4EE6xKTdYwPotnD2DHX1dKmMBmQSehg/640?wx_fmt=png&from=appmsg)

许多开发团队都面临着算法代码无限膨胀的问题，需要一个有效的预防机制。Dragonfly 框架可以自动监测在线运行的无用算子并进行召回，甚至可以识别无用的分支。这样，系统可以定期生成报告，比如右侧的按分支生成的报告。这个报告可以精确地定位到哪位作者在哪个文件、哪个函数中写了哪个无用的分支，以及它已经有多少天没有被使用过了。

有了这样的报告，就可以直接定位到编写无用代码的人，将报告发送给相关作者，促使其进行深入剖析并删除这些无用的代码。这样，可以有效防止代码无限膨胀，避免给未来的系统精简和重构带来不必要的压力和消耗。

**04**

**规划展望**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvDAJKnrB4Wo7yjRjOia2JAnFibClibFgIjNclvwp7x7kricBQUXOrNu4WVw/640?wx_fmt=png&from=appmsg)

展望整个框架，未来将在以下三个方面持续发力：

**1.** **性能方面**

正在进行中的工作是提供 numa-aware 的能力。新一代 CPU 架构正在转向多 numa 的架构，这可能让已有服务的性能未处于最佳状态。为了充分发挥硬件性能，需要上层代码能够更深入地感知 CPU 架构。目前框架可以帮助上层算子更简单的感知到 numa 架构的情况，并灵活控制内存分配策略，以实现更优的访存性能。

此外还可以根据整个链路关系执行图优化，以降低线上服务耗时，并将这种优化扩展到全链路。

**2.** **管控力方面**

得益于全链路统一基座引擎的支持，可以轻松实现全链路特征管理和数据血源追踪。未来，系统将能够自动检测出哪些数据已无用并直接将其删除。

同时我们将建设系统的自净化能力，实现代码治理的自动化。系统将能够识别出无用的逻辑或低效代码，并从代码库中定期自动删除，从而持续保证系统的健壮性。

**3.** **产品化方面**

希望在未来加强整个生态工具链的建设，提供更智能的工具，用 AI 技术驱动更高效的研发流程。

系统也将致力于提供更完整的综合解决方案，甚至提供 to B 的能力。

如果您对此领域感兴趣并希望加入我们的行列，共同创造卓越的成果，请将简历发送至邮箱 fangjianbing@kuaishou.com。我们将一起致力于构建更强大、更智能的工具和服务。谢谢大家的参与和支持！

**05**

**问答环节**

**Q1****：****D****ragonfly****的自定义算子的表达能力是否会比较有限，或者说它是否总能翻译成 C++，还是能够覆盖一些比较复杂的 C++ 的推荐逻辑。**

**A1****：**取决于对算子抽象的程度。因为这个算子并不是直接翻译成 C++ 代码，而是由 C++ 代码组装起来。比如要做一个过滤，需要首先把过滤相关的逻辑先抽象出来，有哪些是公用的，哪些是可以配置化的，抽象出一个过滤的核心逻辑，给大家复用，而并不是直接在 Python 里面写一个很细致很具体的过滤代码，然后把它翻译过来。算子并不是细到代码行级别的粒度。

**Q2****：****自定义算子的拆分粒度是什么？在实际开发中是否属于自定义算子，是工程侧还是算法侧的同学去决定这件事情。**

**A2****：**这件事一般会是算法侧自己去开发，工程侧一般会去开发一些通用性的算子。自定义算子这部分会存在一些现实的问题，比如不同算法同学的抽象能力以及代码能力是不一样的，他们对自定义算子的粒度把控以及设计可能是存在欠缺的，会导致自定义算子的复用性很有限。

**Q3****：****第三个问题是关于控制流的，和 TensorFlow 的图的本质区别是什么？控制流具体是如何实现的？**

**A3****：**概念上类似于 TensorFlow，也是数据驱动的构图方式。TensorFlow 直接暴露成一个变量，通过变量的传递就能推断出数据依赖关系。但数据在我们 DSL 中是一个隐藏的概念，比如文中的例子，类似 ctr、pctr 这样的数据，它算是作为一个配置项，体现在某一个算子的配置里面。从代码级别上来看，并没有存在这么一个 pctr 的 python 变量去承接这个数据，而是隐藏在 DSL 之下的一个概念，因为数据关系非常复杂，很难用变量传递去表达清晰。这是与 TensorFlow 的一个区别。TensorFlow 是通过参数传递的方式进行数据传递，而我们的控制流是通过函数的配置，它的入参有一个叫 pctr 的字面量值，后续某一个算子有一个 pctr 的值作为它配置的输入，这样去判断出它的前后依赖关系，所以整个逻辑也都是靠拓扑加数据依赖的方式去构图。总之，原理上类似，但具体实现细节上不太一样。

**Q4****：****关于微服务划分，Dragonfly 实现的文件是一个微服务，想了解一下 DSL 中的算子的组织和微服务的划分有什么样的关系？**

**A4****：**一个 DSL 实际上最终对应的是一个服务的配置，比如策略服务，最终会生成一个 Json 的配置，然后交给系统去部署运行起来，对应的下游的召回粗排精排重排，也分别有一个独立的配置。等同于一个 DSL 对应一个线上的服务节点。如果要做节点拆分，实际上就是把 DSL 前半部分的方法调用摘出来，把它挪到另外一个 DSL 的文件里面。

**以上就是本次分享的内容，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUiaUMwM8I3NYH3SVrllWIPIMQXDtN5DqCLRhFwFhR9RictLsYYBpOwibjfw/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjJEcwZbH76dgmLgKNLp1dvZGrFLJYSXl6Ynd7cB4y0FCznzk8PZtyoxujPic3PaUxO0ryrmqlusvw/640?wx_fmt=jpeg&from=appmsg)

**分享嘉宾**

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

********方剑冰********

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

****快手****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**推荐系统架构师**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

方剑冰，清华大学硕士，现负责快手自研通用策略引擎 Dragonfly 的生态研发，此前在微软亚洲工程院 Bing 团队参与搜索和浏览器日志数据平台的建设，于 2018 年加入快手作为核心人员从零开始建设快手推荐中台，拥有丰富的在线服务架构经验。

![](https://mmbiz.qpic.cn/mmbiz_png/CzXmD0LHvdj3nVY9EDHLhpH4VvJeiaia0BjslvVI4lWY8dcyW3FMvredibDW5kTgOSp10IDoUmoS4yNgZpNRmQFoQ/640?wx_fmt=png)

直播推荐

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiajvrlw9oGnZDr4mJsGCMibYrq5ibszfySkbKAh4rWMTpazwgSibNONWeJBibRxKk5SXr98pZOJS5GV6Q/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/CzXmD0LHvdj3nVY9EDHLhpH4VvJeiaia0BjslvVI4lWY8dcyW3FMvredibDW5kTgOSp10IDoUmoS4yNgZpNRmQFoQ/640?wx_fmt=png)

往期优质文章推荐

往期推荐

[知乎舰桥平台的三板斧-内部营销篇](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247699241&idx=2&sn=760c70e816f561df7f16b41098fed6ba&chksm=fbd87945ccaff053d2e71245637ead575fdc128c6c4c57e1ead769fc37541ce9437b7eed2c05&scene=21#wechat_redirect)

[知乎舰桥平台如何打造内容运营平台提升业务能力？](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247698033&idx=1&sn=661e2f6fe0a03bfb798487019e4fc483&chksm=fbd8741dccaffd0b6312f00c3518cffac34e88af504f574f70047a14520f932ac571e4ab4c11&scene=21#wechat_redirect)

[盘点AB实验长期影响评估的方法论](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247699047&idx=2&sn=da27e75d7102f0820a22a0fc7d2252fa&chksm=fbd8780bccaff11dff4f4fedd2639754b8b4c4897400a4a161fee422fe74e65d40a545c3cecb&scene=21#wechat_redirect)

[从 Elasticsearch 到 SelectDB，观测云实现日志存储与分析的 10 倍性价比提升](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247698448&idx=1&sn=75d159daa355d2e67a64fe341bd2ac81&chksm=fbd87a7cccaff36ae5fd072288324b5ca6f1e28f97de33ee510a0d8bcff04db9f5cb7e259009&scene=21#wechat_redirect)

[大模型是推荐系统的解决方案吗？](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247698376&idx=2&sn=d91a404e8455d3d655d5bfc10d002259&chksm=fbd875a4ccaffcb2c4a0c6b7a97334bfc44a75a82d7e2a8699d7c477ae6288de1883c47f4858&scene=21#wechat_redirect)

[OLAP技术的选择，进化和思考](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247698150&idx=1&sn=68cb0adf08c58330fe73f59f86c1df5a&chksm=fbd8748accaffd9c2e48b9e35c84ce4db19ec97322912d5e89bfcdfc02284320f017fe67bb7f&scene=21#wechat_redirect)

[AB实验平台建设实践助力业务决策-货拉拉](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247698058&idx=2&sn=9f0aa004c7daba11dfa38e12a7338c48&chksm=fbd874e6ccaffdf03267fe8924ad48ae6ef6072e025881f36a42e6e1e6657050ca364b42c898&scene=21#wechat_redirect)

[Alluxio SDK 在 Presto/Trino 中的应用](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247698055&idx=1&sn=a935a45ef615af60ad30fdbeef022a84&chksm=fbd874ebccaffdfd9d9d33734be242d946e59d3c0d10e7b2307360d2524b56c6511ec8438ad5&scene=21#wechat_redirect)

[大语言模型分布式训练的量化分析与最佳实践,以 GPT-175B 为例](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247697077&idx=1&sn=e91922809be64b424763e33b3e948840&chksm=fbd870d9ccaff9cf5051a9c7cf127d2afe44ef94e2fcc6cf0b98c485162b2445b59e456c0af6&scene=21#wechat_redirect)

[降本不增“笑”的正确打开方式](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247696688&idx=1&sn=431af18d0a62e3bd50bc062bc12da0c4&chksm=fbd8735cccaffa4ac829390732f7c4ce06890e26095229b5bf6eed6613790ebae40d59736ab8&scene=21#wechat_redirect)

[网易数帆 指标中台构建核心技术解析](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247696570&idx=1&sn=8cbd1a7579f3d1be0bd58d264f5bf194&chksm=fbd872d6ccaffbc04f089c22f56a16e0c1da4f79302ae81938fc5982e6a5360e4395e399eba5&scene=21#wechat_redirect)

[Apache Celeborn 社区的今天和明天](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247696575&idx=1&sn=b794b9ab8e26cd575bc058bb29eaf512&chksm=fbd872d3ccaffbc55484d88c0800825c8d1404e4ff56e25e0d1b183d01d8a7482bc351abcdd2&scene=21#wechat_redirect)

[小红书推搜场景下如何优化机器学习异构硬件推理突破算力瓶颈！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247696503&idx=1&sn=0e063217f9a0075903533d7076f225ad&chksm=fbd8721bccaffb0dc3e284e4fd4701d9635c92a1a972438f8efe05a8f75733bcbc5fc8851da3&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/kyGmFPwv1yoyd6fBWwiaPS0c2G7Z96VE461PMpVjVGAEDFlFB1vgHibC6ZSoS6qicJCd6Cx9Wa1gKsr91CKGpXGOA/640?wx_fmt=png)

DataFun

![](https://mmbiz.qpic.cn/sz_mmbiz_png/kxCmTUBqscJrhZZHLWiczibzQKOzTVPy1Da66VJXX1INDsjiaWZydmtGyBJL07JDNNTwYd3LzRhqonmlefNLF732w/640?wx_fmt=png)

点个在看你最好看