---
title: 'Havenask分布式索引构建服务--Build Service'
company: 阿里
tag: 索引构建
date: 2023-12-27
url: http://mp.weixin.qq.com/s?__biz=Mzg4NTczNzg2OA==&mid=2247501264&idx=1&sn=a49b05c3c376971a471de90620b3dde5&chksm=cfa6d533f8d15c25ac6cbf7fa3f4b0708e179e7ff6a0b429660805e03d3ce71f97f292df36db#rd
account: 阿里技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_png/6Qoz8QdUyDCpfJsmHic2aaZccICpJibvebC383RI7xmiay6uQ7Yoy6iaG6wUIgpEHib3AaS9qIzFcic68Bp7yGKO0iaicg/640?wx_fmt=png)

这是2023年的第93篇文章

（ 本文阅读时间：15分钟 ）

Havenask是阿里巴巴智能引擎事业部自研的开源高性能搜索引擎，深度支持了包括淘宝、天猫、菜鸟、高德、饿了么在内几乎整个阿里的搜索业务。本文针对性介绍了Havenask分布式索引构建服务——Build Service，主打稳定、快速、易管理，是在线系统提升竞争力的一大利器。

**01**

# **Havenask介绍**

Havenask 是阿里巴巴广泛使用的自研大规模分布式检索系统，是过去十多年阿里在电商领域积累下来的核心竞争力产品，广泛应用在搜推广和大数据检索等典型场景，在2022年云栖大会-云计算加速开源创新论坛上完成开源首发，同时作为阿里云开放搜索OpenSearch底层搜索引擎，OpenSearch 自2014年商业化，目前已有千余家外部客户。

下图展示了Havenask 中一个完整的搜索服务：在线系统、索引系统、管控系统、扩展插件，且包括了查询流、数据流、控制流。其中，索引系统负责索引数据生成的过程，还包含有文档处理与本文的主角索引构建服务 Build Service。索引构建分为三个步骤，对数据进行前置处理（例如分词、向量计算等）、产出索引、合并索引文件的处理。

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hx6EVX0GF8lXsYWCcQtkWicSt7bGu7sY8iasmTlNicH5icqFibQAJqHkAu0Hn5oRNhdWI7NbuGdUvVFdQ/640?wx_fmt=png&from=appmsg)

Havenask 支持千亿级别数据实时检索、百万 QPS 查询，百万 TPS 高时效性写入保障，毫秒级查询延迟和数据更新，并具有良好的分布式架构、极致的性能优化，能够实现比现有技术方案更低的成本，普惠更多的开发者和企业。

**02**

# **Build Service简介**

Build Service是一个分布式索引构建服务，用于Havenask中的全量表的索引构建。它可以对接本地存储、HDFS等多种数据源，快速的将原始数据构建成全量索引，并以流式工作模式进行增量索引构建。Build Service是Havenask读写分离架构的重要组成部分，独立的索引构建服务使Havenask具有下面优势：

在线系统更加稳定：将索引构建从在线系统分离，避免了索引构建对在线系统的影响，使在线系统更加稳定。

索引构建更快：特有的全量流程，使全量数据导入更快；独立的资源控制，进一步提升索引构建速度。

多版本索引管理：多版本独立的构建流程管理，使索引重建更方便，更安全。

**03**

# **Build Service架构**

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hx6EVX0GF8lXsYWCcQtkWic6ozbTYzaocPEvJIrG8mDcsK6AGruicMC8ibGaykKWjCuHhDb8OuVJFhQ/640?wx_fmt=png&from=appmsg)

*Build Service架构图*

上图是Build Service的架构，在Build Service中主要有下面几个角色：

**BS Admin：**BS Admin负责整个集群的任务调度和资源管理。BS Admin提供丰富的接口进行索引构建任务的启停，资源的调整等，BS Admin接收到这些请求之后会进行任务的调度，并配合调度系统，调度任务的执行，并维护任务的状态。

**Processor：**Processor从数据源中拉取数据进行处理，Processor可以支持多种数据源，比如HDFS、OSS等分布式文件系统，也可以对接Swift消息中间件处理实时数据。在Processor中主要是对数据进行分词、简单的数据转换等处理，开发者可以通过定制数据源reader插件和数据处理DocumentProcessor插件来扩展支持不同的数据源和数据处理逻辑。

**Builder：**Builder负责索引的构建，它将经过Processor处理的数据按照Schema的配置构建成倒排、正排、摘要索引。Builder与Processor的数据交互是通过Swift消息中间件来实现的，即Processor将处理之后的数据写到Swift，Build从Swift中读取这些数据进行索引构建。

**Merger：**Merger负责索引的定期整理，定期索引整理使索引文件更加紧凑，可以降低在线集群索引加载的内存开销，提升检索性能。索引整理时会清理已经删除的数据，将小的索引文件合并成大的索引文件，也可以按照配置在整理时根据某个字段进行离线排序，这样可以进一步提升检索性能。

在一个Build Service服务中可以有一个或者多个BS Admin，它们通过ZK进行leader选举，只有leader才会管理整个Build Service服务，其他Admin作为fllower，使服务更加稳定。一个Build Service服务可以同时管理多个表或者同一个表的不同版本的索引构建任务，每个任务都是相互隔离的，互不影响。每个索引构建任务都有各自的Processor、Builder、Merger节点进行数据的处理，索引的构建。每个索引构建任务可以独立进行资源控制，比如调整Processor节点的个数，Builder和Meger的并发度，以及这些节点的CPU和内存等。

对于Processor、Builer和Meger节点，它们只有分片（Shard）的概念，没有备份的概念。比如对于Processor，每个分片处理不同的数据，一个分片只会启动一个节点，如果某些原因启动了多个节点，多个节点之间通过ZK进行leader选举，只有leader节点才会存活并工作，非leader节点的进程会自动退出。Builder和Merger的情况与Processor类似，唯一不同的是分片数是在创建表时就确定的，它们只能基于分片数据调节并发度，因此Builder和Meger节点真实启动的个数是分片数乘以并发度。

**04**

# **索引构建流程**

![](https://mmbiz.qpic.cn/mmbiz_png/OmCbZ5JK30Hx6EVX0GF8lXsYWCcQtkWic5JOCwDT2yicNXDl18kea9GTGIYbYz7lvRTaONbYiaRPWoDFMV6FVjvLQ/640?wx_fmt=png&from=appmsg)

*索引构建流程示意图*

Build Service的索引构建分为两个阶段：全量索引构建和增量索引构建。每个索引构建任务都会先进行全量索引构建，全量结束之后会自动切换到增量索引构建阶段，增量索引构建任务会一直执行，直至这次索引构建任务停止。全量索引构建任务会首先从分布式文件系统读取原始数据构建成索引（如果没有配置，这步会跳过），全量文件处理完成之后，会继续从Swift中读取数据继续构建全量索引。这样等全量流程结束之后，全量索引中的数据已经通过消费Swift追到距离当前比较靠近的时间了，索引切上线之后不会出现较长时间的时效性延迟。

无论是全量索引构建还是增量索引构建，它们的索引构建流程是类似的。首先Processor节点会从数据源中（包括Swift）读取原始数据，然后对数据进行分词或者其他处理，处理之后的数据会转发到Swift的中。Builder和Merger的任务是交替执行的，首先Builder从Swift中读取处理之后的数据，构建成索引，索引产出在分布式文件系统中。对于全量索引构建，全量数据被全部构建为索引之后Builder就会结束；对于增量索引构建，Builder接受BS Admin的调度，将数据处理到某个时间点就会退出。Builder结束之后，Meger节点就会执行，Meger会对构建的索引按照一定的策略进行整理，整理好的索引也会写回分布式文件系统。

需要注意的是，增量索引构建时，Processor处理之后的数据不仅仅供Builder消费，在线的Searcher节点也会直接消费，将其构建成实时索引。

**05**

**Build Service定制能力**

为了满足不同业务的需求，Build Service在构建索引时支持下面三种定制能力：分析器的定制、数据源插件的定制、数据处理插件的定制。开发者可以直接修改代码将定制逻辑与Havenask一起编译成一个Binary生效，也可以建立单独的目录将其编译成动态库，通过插件的方式生效。

**分析器定制：**分析器主要用于对文档进行分词，开发者可以通过定制分析器定制自己的分词逻辑，分析器不仅会在构建索引时生效，在查询时也会生效。

**数据源插件定制：**Havenask主要支持HDFS、OSS、MaxCompute、Swift等数据源，如果要支持更多的数据源比如kafka，可以定制Processor的Reader插件。

**数据处理定制：**数据在Processor中是由一个DocumentProcessor链进行处理的，用户可以定制自己的DocumentProcessor处理类来扩展数据处理逻辑。

**06**

# **Build Service与Indexlib（核心索引库）的关系**

Indexlib是Havenask的核心索引库，提供正排、倒排、摘要等索引的实现，并在此基础上抽象出了各种表模型，比如normal表、kv等、kkv表等。但是Indexlib无法独立提供索引构建服务，必须通过Build Service才能进行索引构建。可以说，Indexlib提供了各种索引的定义，并提供了索引构建的接口，Build Service定义了流式索引构建的框架，两者相结合才使Havenask具有了强大的索引构建能力。

**07**

**总结**

# 

Build Service是一个流式的索引构建服务，能够轻松完成海量数据的索引构建，对在线系统没有任何影响，极大提高了整个集群的稳定性。独立的索引构建任务管理，可以方便、安全的对同一张表进行多次索引构建，特别适用于智能搜索场景下需要定期索引重建的场景。当然，Build Service的引入也使得整个系统的架构更加复杂，数据生效链路变长，资源开销变大，大家在使用时请根据业务情况认真选择。

Havenask 开源官网：

https://havenask.net/

Havenask 开源项目地址：

https://github.com/alibaba/havenask

阿里云 OpenSearch 官网：

https://www.aliyun.com/product/opensearch

![](https://mmbiz.qpic.cn/mmbiz_jpg/OmCbZ5JK30FPZjAibjlcJwGqiaJEt8ZZMb95WqbJUriczOlL4HxWdibDacUtiahcZQTFibTLiaPTspUoEboZrrwMiaxTgA/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_gif/OmCbZ5JK30GbpbpADRYqgC6MMvNfRPY8cGySPF2f9miavJibvCOiaUelcS2LX6uSMGEic1ztD9ECCvN2rcupEseySg/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/mmbiz_gif/OmCbZ5JK30GMpsz1kdxGBRiclB5yjhBh5iamZLYrF2BOK4YNhXbjibibx63B6o5ubgOvYGRyUa0DK6gpI9YibkKUUCQ/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

欢迎留言一起参与讨论~