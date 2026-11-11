---
title: '基于 Iceberg 打造高效、统一的腾讯广告特征数据湖'
company: 腾讯
tag: 工程相关
date: 2025-02-05
url: https://cloud.tencent.com/developer/article/2493293
account: 
origin: harvest-202607
---
[腾讯大数据](https://cloud.tencent.com/developer/user/1009891)

## 基于 Iceberg 打造高效、统一的腾讯广告特征数据湖

关注作者

[*腾讯云*](https://cloud.tencent.com/?from=20060&from_column=20060)[*开发者社区*](https://cloud.tencent.com/developer)

[文档](https://cloud.tencent.com/document/product?from=20702&from_column=20702)[建议反馈](https://cloud.tencent.com/voc/?from=20703&from_column=20703)[控制台](https://console.cloud.tencent.com/?from=20063&from_column=20063)

登录/注册

[首页](https://cloud.tencent.com/developer)

学习

活动

专区

圈层

工具

[MCP广场![](https://qccommunity.qcloudimg.com/image/new.png)](https://cloud.tencent.com/developer/mcp)

文章/答案/技术大牛搜索

搜索关闭

发布

腾讯大数据

[社区首页](https://cloud.tencent.com/developer) >[专栏](https://cloud.tencent.com/developer/column) >基于 Iceberg 打造高效、统一的腾讯广告特征数据湖

# 基于 Iceberg 打造高效、统一的腾讯广告特征数据湖

![作者头像](https://ask.qcloudimg.com/raw/yehe-133f028/kcz4ys866s.png)

腾讯大数据

关注

发布于 2025-02-05 11:01:47

发布于 2025-02-05 11:01:47

2.2K0

举报

文章被收录于专栏：[腾讯大数据的专栏](https://cloud.tencent.com/developer/column/1408)腾讯大数据的专栏

概述：腾讯广告业务的特征生产计算每天都会处理万亿级的新增记录和 PB 级的中间数据，并管理数十 PB 规模的历史结果。为了解决海量数据在读写性能（含更新）和存储管理上的痛点，广告特征工程团队和智能湖仓团队在对比业内主流存储组件后，选取 Iceberg 来构建广告特征数据湖。

在社区版 Iceberg 的基础上，拓展共建了多流合并、行列更新兼容的湖内主键，来满足流批一体场景下高吞吐、高频次、低时延的读写更新。通过可伸缩、自适应的分区与合并策略，既解决了开源版本 Iceberg 小文件过多的问题，也通过适配 Spark SPJ（Storage Partitioned Join） 特性来提升数据加载效率。在 Iceberg 元信息模式上，将数据回溯、回滚、归档等通用操作流程化，通过自定义的 Procedure 实现了文件级粒度的元信息查询过滤和变更操作。

业务接入后，离线特征发布至在线 KV 系统的时效性提升了近一半，流式数据入库的时效性从小时级提升到了分钟级，历史特征样本补录任务加载效率提升了十倍，并且支持任意特征组数据 CDC 粒度的分钟级回溯回滚，极大提高了离线特征数据的利用效率。在存储空间上，与原有的 HDFS 方案相比减少约 30%，增量更新合并方案与社区版相比冗余数据减少约 60%，成本减少明显。

## **一、相关背景**

在腾讯广告业务中，每天会生产大量的特征数据用于广告投放推荐。当前已在广告工程团队负责生产和更新的特征共计约有近万个，数据流也达到数千条 ，每日需处理数十万亿条记录，涉及到约PB级的中间数据，日增特征结果数据超百TB。同时，为了支持不同时间周期、不同查询需求的下游使用方，需要保留过去一年以上的历史数据，并提供各种场景下的高效查询能力。高效地存储并用好这些海量特征数据，满足多引擎、多维度、多版本的使用需求，存在有很大的挑战。

在特征生产计算任务统一收敛到广告特征工程团队的大背景下，需要统一的特征存储层来收敛曾经分布散乱的离线特征数据，提供高效简洁的读写、变更、管理接口，基于一款容量伸缩良好、流批一体读写适配、Schema evolution 灵活、元信息可拓展性强的存储介质，来支持离线特征数据的生产及使用。通过对比业内主流的存储组件，广告工程与湖仓团队最终选择 Iceberg 作为特征离线存储底座，针对特征业务场景进行一系列优化，拓展共建来满足广告业务场景下的各种复杂需求。

## **二、业务架构概览**

![](https://developer.qcloudimg.com/http-save/yehe-1009891/e1740a465280ac9f44c882bac8ef3090.png)

### **2.1 数据湖存储底座选型：Iceberg vs Hudi**

### 

广告特征数据在生产流转中均有逻辑上的唯一主键，在实际读写计算使用时也都以主键约束为主，因此首先需要存储底座支持主键维度的读写更新。除主键约束外，存储底座既需要支持离线批式场景下的高效读写，也需要满足实时流式特征数据生产的高时效性要求。总的来讲，广告特征数据的存储底座需要一款能支持主键高效读写更新的流批一体存储介质。

在此之前，广告特征使用 HDFS + Hive 的传统数仓架构来存储。使用 Hive 分区表存储时，由于底层 HDFS 文件的数据不可变特性，无法直接对内容进行 Update 操作，必须使用代价昂贵的文件复写来实现更新语义，同时也无法保证更新数据的时效性。而 HBase、Kafka 等组件仅能满足批式或流式更新的部分需求，在流批一体场景下查询及引擎支持有较多的局限。

随着数据湖在其他业务上的大规模落地，我们观察到这项新兴技术能较好地契合大部分特征存储的需求，结合特征生产使用过程中一些痛点，我们对当前主流的湖仓存储组件：Iceberg 和 Hudi 进行了如下对比：

| 对比项 | Iceberg | Hudi |
| --- | --- | --- |
| 引擎支持 | Spark / Flink / Presto 等 | Spark / Flink / Presto 等 |
| 存储模式 | 元信息文件 + 列存文件 | 元信息文件 + 列存文件 + 行 Log 文件 |
| 主键 Upsert 支持 | 社区版本暂未支持，智能湖仓团队已支持 | FileGroup Index 是 HUDI 的核心组件，整体完善度高，但调整并发性能较差；社区版的 Bucket Index 方案，需要对数据规模有良好的预估才能够推测出合适的 Bucket Number |
| 文件合并 | 合并任务主要以旁路任务并行运行，可手动触发非阻塞，可自定义文件合并重写的具体策略 | 写入时在 TimeLine 上检查并注册 Instant 后异步触发，依赖外部服务系统（如字节的TMS）进行冲突检查和管理在行列文件的基础上，合并策略较固定，可以指定时间、文件大小等参数 |
| Schema evolution | 全可变兼容，版本化 Schema | 向后兼容变更，支持后追加和删除列操作 |
| 数据可见性 | 支持主分支和临时分支，对同一份数据可以实现查询级别隔离的可见性 | 对所有下游都是原子一致的可见性 |
| 数据可逆性 | 支持快照级的数据回滚，能保留中间状态数据 | 支持未合并快照数据回滚，已被行转列合并的数据无法获取变更的中间状态 |
| 并发限制 | 整体使用 Immutable Snapshot 保存每次操作的元信息，以 Branch 树结构保留全表的元信息记录，仅在主分支上有并发限制 | 以 TimeLine + Instant 方式保存元信息，Instant 之间存在严格的冲突检查，整体设计思路为阻塞式的单写入模式，业内在流式场景下的并发方案也都基本以占位 Instant 为主 |
| 文件管理难度 | 基于 Snapshot + Manifest 文件方式管理文件，每一个 snapshot 对应一组 manifest，每一个 manifest 再对应具体的数据文件，与多级分区目录模式接近，无额外特殊逻辑 | 使用行列文件并存的存储模式，功能配置参数常常会有 10+，优化和维护都有较高学习成本，而且由于这种计算逻辑和文件组织方式的耦合，计算引擎需要单独适配逻辑 |
| 元信息可查询性 | 提供了基础的元信息表供 Sql 查询，由于使用树结构存储 Snapshot 信息，接口层面也可以根据自定义参数的元信息灵活检索 | 由于 Instant 串行添加，每次查询均需完整遍历整个元信息 Timeline，对于 Delta 级别的信息支持不是很好，需要自定义参数和比较逻辑 |
| 分支演进能力 | 支持对 Snapshot 添加 Tag ，以及基于任意 Snapshot 自定义新分支，可演进变更数据 | 支持对 Instant 添加 Tag，仅提供标记功能，不支持数据变更 |

可以发现，两种湖仓开源方案都能满足特征存储的基础功能诉求，根据公开 Benchmark 测试报告，二者在绝大多数场景下的性能差异并不大。由于 Hudi 天然面向 Spark 批处理模式，在 Flink 中也基本沿用了 MapReduce 模型的过程（写入前 Instant 占位 - 数据写入 - 各 Task 上报 - Coordinator 确认提交），本质上是将流式数据在每次 Checkpoint 时划分成了批数据来串行处理，实现方式与引擎代码耦合很重。同时单 TimeLine 阻塞模式的限制很大，业内在尝试实现无冲突的并发写入时，均需要深度改造相关组件，这些历史积累的复杂系统设计导致 Hudi 拓展性不佳。而 Iceberg 在元信息上的管理和变更都十分灵活，考虑到后续功能拓展及二次开发成本，广告特征工程团队和智能湖仓团队最终选择基于 Iceberg 来优化以满足多种复杂场景的需求。

接下来，我们从特征入湖、存储管理优化和特征数据应用三个方面，给大家介绍与湖仓团队在 Iceberg 功能上的共建拓展及落地效果。

## **三、特征入湖：以主键为基础，支持流式特征分钟级更新**

基于湖仓团队研发的高效主键表的能力，批式特征数据可以高效入湖。为了满足流式特征部分列更新及多路合并的需求，我们与湖仓团队共建，通过主键表的自定义 Reduce 能力，实现了基于版本的多流拼接列更新，支持流式特征满足分钟级时效性。

### **3.1 高效主键表**

#### **3.1.1 方案及流程介绍**

Iceberg 高效主键表的核心思想是对主键进行 bucket 分桶并确保每个桶内的数据文件是按主键有序的。由于数据文件本身主键有序，对数据进行归并更新取最新的记录是个相对廉价的操作，对数据的 Upsert 操作可以转换为写入时 Append Only、读取时 Merge 的操作(Merge on Read)，以拥有良好的吞吐性能。主键表的基础读写流程如下：

1. **分桶**：使用主键对数据进行 bucket 分桶，确保每个分桶之间的主键不存在重叠。对于联合主键的场景(多个字段组成主键)，bucket 应用于整个联合主键，而不是对每个主键分别 bucket。

2. **写入** - Overwrite & Update：对于每个 bucket（通过对主键 shuffle 分桶），Iceberg writer 在写入时需要先对主键(primary\_key) + 排序列(ordering column，如有) 进行排序，确保写入的文件主键有序。对于多次写入或者 update 场景，Iceberg 直接写入新的 data 文件即可，这意味着不同的 data file 文件之间的主键可能存在重叠。去重操作在读取侧完成，合并(compaction) 操作按配置异步触发。

3. **读取 - Full & Incremental**：根据不同类型读取操作和 Snapshot 类型，获取不同的元信息文件 Manifest，全量读取时获取全部 Append snapshot 或最新一次 Overwrite snapshot 的文件列表；增量读取时则根据 [Start Snapshot, End Snapshot] 获取范围内的新增文件列表。

4. **结果合并**：由于主键表按照主键分桶，因此 Iceberg 在表扫描时，会根据 bucket 把归属于同一个 bucket 的 datafile 合并至同一个 task/reader 进行读取。一个 bucket 内的多个 data file 可能会存在重叠及重复，Reader 侧根据主键 + 排序列(ordering column，如有) 进行归并去重取最新值。这样子每个 bucket reader 得到的数据均是最新的无重复数据。

#### **3.1.2 性能分析及验证**

主键表相比较于普通表的写入，上述流程中引入的额外操作是 repartition + local sort，其中：

1. **shuffle**：对于 bucket 分桶而言，其 shuffle 操作跟一次普通的数据 shuffle 操作类似，并未引入过多的 overhead。

2. **local sort**：只在 task 内进行排序，整体代价可控。在现代 CPU 架构下，对于百万条记录的排序时间数量级应在秒级 - 分钟级（发生 Spill）。

为了验证主键表上述的性能分析，我们两组样例数据进行测试。无主键表的数据以原分区表的 Overwrite Partition 方式写入，存储在多个天分区目录中；主键表将每个天分区的数据以 Append 方式写入到表中，存储在多个 Snapshot 中。

整体写入耗时基本在分钟级别，没有显著的量级差异；读取时根据不同类型的过滤和聚合条件，无主键、主键小分桶、主键大分桶的表各有优劣：

1. 根据主键去重、过滤、聚合计算时，主键表均比无主键表更优。

2. 在超大数据量情况下，由于单文件小、溢写磁盘比例低，大分桶表明显优于小分桶表。

可以发现在主键约束条件的场景下，主键表相比普通分区表存在明显优势，且性能可以通过分桶数横向拓展，符合我们业务上侧重的主要场景。

| Group | Sql Type | 无主键表 | 主键表-256 分桶 | 主键表-1024 分桶 |
| --- | --- | --- | --- | --- |
| 测试组 1 | Select \*（无去重） | 54.9 s | 86.6 s | 56.2 s |
| Select（主键去重） | 106 s | 78.5 s | 48.4 s |
| Select（主键去重 + 内容列过滤） | 115.2 s | 79.9 s | 52.3 s |
| Count by 主键 | 108.3 s | 92.5 s | 69.8 s |
| Count by 主键 + Group by 天分区 | 755.9 s | 113.9 s | 95.2 s |
| 测试组 2 | Select \*（无去重） | 1116.8 s | 608.4 s | 262.7 s |
| Select（主键去重） | 1235.1 s | 586.8 s | 237.3 s |
| Select（主键去重 + 内容列过滤） | 1093.9 s | 568.1 s | 227.3 s |
| Count by 主键 | 超过 20min | 113.3 s | 87.8 s |
| Count by 主键 + Group by 天分区 | 257.2 s | 167.8 s |

### **3.2 列可重叠的多流数据合并**

#### **3.2.1 业内开源方案对比**

在广告流式特征更新的场景下，除了基于主键的整行数据写入之外，还有一种常见的生产方式就是将多个上游的流式数据更新合并至一行中，即多流拼接更新场景。业内在多流数据合并方案上，计算层主要通过 Flink State 来实现，使用状态 KV 来缓存和拼接出整行数据，一方面对任务的性能调优要求很高，需要对任务中的一些关键节点进行针对性的配置调优，另一方面方案通用性不强，拼接逻辑需要定制化开发，数据更新可见的时效性也不是很高。特征生产需要更加通用化的方案，以避免对计算任务点对点逐个调优，因此考虑将相关的拼接合并逻辑下推到存储侧。

调研发现，Hudi 社区实现的多路合并（PartialUpdate）的 PayLoad 方案，其实际是通过不同流写入不同的行 Log 文件，在合并时通过主键 Key 排序拼接写入到列文件中实现，有 Merge LogFile 和 Merge LogFile to BaseFile 两步。在合并 log 文件时，相同主键不同流的数据更新和拼接操作，使用记录中的Commit 版本字段来排序，每条流只能按行保留最终结果，无法支持多个流中数据列有重叠的场景。同时对一些特殊更新场景的 corner cases 处理不够好，比如不支持的 null update，即无法确认 null 值是由于未覆盖列的默认缺省，还是明确的更新内容。基于 Iceberg 主键表读时合并 MOR 的特性，我们设计并实现了新的 Reducer 算子，用来在存储侧高效支持多流列拼接的场景。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/69fa52cc7d6b725755fcda536e6459c2.png)

多流列拼接的整体实现思路是：我们将 Payload 方案中的行排序字段精确化到每一列，每个流在数据写入时，均将每个字段此次的更新版本信息（业务时间 / 写入的 timestamp）保存在表的特殊列（Merge\_Info)中，读取合并时再进行最终整行结果的解析、比较、拼接。由于数据已经根据主键预排序好，分桶内归并计算的开销远小于 Payload 方案下行文件的 group by + compare 流程。将数据的合并逻辑放到流程中最后一步，则不会在写入时引入额外开销，既能支持列有重叠的多个数据流写入，也能始终合并出正确的整行数据。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/35d03bfd80665d789921d76c7d70205e.png)

#### **3.2.2 支持流式特征分钟级入库**

在主键表对多流更新数据的支持下，为保证原有流式任务的稳定性，我们通过一条旁路消息队列作为数据缓冲，然后再将数据写入到 Iceberg 的方式实现实时流式数据入湖，并通过增量 Compact 减少小文件问题。通过优化，我们极大提升了广告流式特征落地的时效性和稳定性。在 Hudi PayLoad 方案下，由于内耦合 Compaction 操作的资源占用和任务抖动，入湖延迟非常容易产生小时级的波动，下游查询的时效性也很难保证。使用 Icebeg 多流合并方案后，Flink 写入任务本身无复杂逻辑，整体运行平稳无反压，数据入湖延迟的波动基本在分钟级。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/ca065789eaefae00f730221bffadd29b.png)

在数据入库时延和查询时效性得到保证后，我们发现能够基于分钟级的 iceberg 离线数据，统计一些在流式数据中无法快速统计的具体业务指标，如 uv 维度的 count、ratio 等，可以在无冗余数据链路的基础上，低成本协助业务更快发现线上数据的正确性问题和潜在风险。

## **四、存储管理优化：多版本、细粒度的统一接口，自适应、低冗余的文件合并**

在数据管理和存储层面，我们根据线上业务的主要使用方式进行接口收敛，利用 Iceberg 灵活的元信息机制，实现了多版本、可回溯、可回滚的读写接口，既减少了用户对线上数据生产链路的理解成本，也简化了数据运维管理的流程。通过拓展 Iceberg 元信息功能，我们将增量更新特征组的数据处理粒度提升到了行级别，使得在线数据能够实现分钟级别的 的 CDC 回溯回滚。同时通过拓展自定义策略、自适应数据规模的增量文件合并方案，减少了长周期存储下的文件冗余，相比社区方案节约近 60% 存储开销。

### **4.1 透明且统一的多版本特征读写**

#### **4.1.1 业务背景及接口方案**

广告特征数据除正常生产发布的例行周期外，同时存在质检、修正、回滚等非顺序、非例行的数据读取和写入操作，批量重跑一批历史数据也十分常见。由于 Iceberg 数据湖存储的最新版本数据可以视作线上 KV 的一个离线快照，为了满足业务对历史数据的访问诉求，我们需要对数据进行定期归档，以提供对 KV 历史状态的一组持久化记录。在这种非保序写入的场景下，我们既需要在查询时提供当前正确的快照版本数据，也需要能够将历史状态中的数据正确记录并反应数据的变化过程。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/3c950e35a94aed238ce4190648531f61.png)

为了满足上述各场景的使用需求，在 Iceberg 灵活的元信息分支模式下，我们首先将写入操作划分到三种自定义的分支中：

1. **Tmp branch**：临时分支，缓存所有写入操作的数据，仅对指定的特殊下游（如质量检测等）可见，指定下游读取后可以该分支数据进行二次操作。

2. **Main branch**：主分支，保存已通过质量检测、符合上线规范的快照数据，对全部下游可见，可视为当前线上 KV 的离线快照。

3. **History branch**：历史分支，归档历史的快照数据，对全部下游可见，后续该历史时间版本的数据，可以在此分支上继续演进修改。

通过这样的分支拆分，即可以在一张表内对同一份数据实现针对不同下游的差异可见性。临时分支既可以用于质量检测等例行生产流程中的数据缓存，也能满足其他有特殊可见性需求的下游使用方，而所有已写入主分支的数据，都是预备发布至线上的数据，发布上线操作也被限定只从主分支读数据，历史分支则用于满足一些回溯及快照查询的需求，很好的保证了数据间的隔离性。同时为了减少整个特征生产流程内的额外概念，我们选择使用生产流程中原有的数据分区时间作为历史分支的归档时间，使得分支时间等价于当前常见的 HDFS 目录 Partition 时间，在每次特征数据产出时自动携带。

针对数据回溯、回滚、归档等通用的表内数据操作，我们参考 Iceberg Procedure 将这些操作流程化，以 Spark Procedure 工具的方式旁路执行，如：

1. **Custom CherryPickProcedure**：从目标范围的 [StartSnapshot, EndSnapshot] 中，根据 Column Filter 条件获取符合条件的文件列表，构造出新的 Snapshot 追加 / 覆盖（视前一个 Snapshot 而定）到指定的 Target 分支上。

2. **HistoryBranchProcedure**：对表内数据进行归档处理，拉取出历史分支。当该业务时间与已有历史分支的业务时间存在差距时，将补全缺失的历史分支，部分复用CherryPick能力，遍历所有数据文件中的分区时间字段，过滤生成出正确的文件 Manifest，创建新的 Snapshot。

最后为了保证已归档的历史分支数据能够继续演进迭代，同时不对指定历史时间外的数据产生影响，我们会在写入前根据当前的批次时间进行比对判断，如果表内已存在相应的历史分支，则仅将本次数据写入到历史分支，并将元信息依次 cherrypick 到更晚业务时间的历史分支中，修正整体的数据结果。

#### **4.1.2 实现特征 CDC 粒度分钟级回滚**

在使用 HDFS 存储特征数据时，如果需要进行数据回滚操作，流程需要多方配合十分复杂，且回滚时效性不可预估。

1. **全量更新特征组**：只需要回滚至某一个时间点的状态，通过读取前一个正确有效分区的数据，重走数据发布流程。

2. **增量更新特征组**：由于每个分区目录内仅包含增量数据，因此缺乏全量数据快照，回滚依赖 KV 支持。

a. **回滚至某一个时间点的状态**：依赖线上 KV 的多版本支持，KV dump 正确的快照文件后，再重新加载覆盖 KV 数据，耗时很高。

b. **回滚掉某一个时间范围内的更新数据**：无法支持，只能回滚至正确的版本后，重新生产写入新数据。

在 Iceberg 数据湖存储多版本、可回溯的支持下，全量更新特征组也可以快速获取到指定时间版本快照用于重新加载，增量更新特征组也可以实现更精 细、高效的数据回滚。这里我们引入大数据领域中的CDC概念，CDC（Change Data Capture）即变化数据捕获，也称为增量数据抽取，主要用于实时监控数据源（如数据库、应用系统等）中数据的增、删、改等变化，并记录下这些变更信息，而在 Iceberg 主键表数据湖中，我们刚好可以获取任意时间范围内的变更记录，通过这些 CDC 记录，回滚流程则可以简化为:

1. **全量更新特征组**：直接读取目标时间的 Snapshot 数据，与直接读取文件差异不大。

2. **增量更新特征组**：

a. **回滚至某一个时间点的状态**：通过 Time Travel + 全量查询，可以获取到任意时间点的全量数据快照状态，无需与 KV 支持，重写流程与全量更新特征组一致。

b. **回滚掉某一个时间范围内的更新数据**：通过增量读取，可以从表内获取任意时间范围 [Start, End] 内的 CDC 记录。对 Add 操作的新数据，直接在 KV 中 delete 该 key 的记录；对 Update 的更新和 Delete 的删除操作，使用表内的前一个版本数据覆盖该 key 的记录，以此可以实现 KV 内数据的精确和快速回滚，不需要重走数据发布流程。

在特征数据湖多版本分支管理的支持下，我们在数据的回补回溯流程上也取得了一些收益。元信息文件级别的操作不涉及到具体数据文件的读写和搬迁，仅需重新构建出正确的 Manifest 信息即可，原本 TB 级数据表的修正和回滚基本需要数小时，迁移后从操作发起直至完成不超过半小时。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/60d5ac5c76f074aaf4dc19bdb230fa8e.png)

### **4.2 低冗余增量文件合并**

#### **4.2.1 现有流程与优化思路**

在上述主键表写入的场景下，一个分桶中可能会存在多个 data file，对于多路归并的算法，文件数越多、归并效率越差，同时占用内存变多，分布式引擎出现 OOM 的可能性就越大。因此，当主键表产生多次写入后，流式作业（比如 Flink）或者外部的监控服务应当主动触发 compaction 合并操作，将多个数据文件合并成一个大的数据文件。得益于 Iceberg 的 Transaction 设计，Compaction 操作是可以完全异步执行的，并不影响当前正在写入的作业或者下游查询。

主键表通过 Rewrite files 方式实现 Compaction 的功能，默认情况下会扫描当前目录下的所有文件，并将这些文件全量合并、重写为一组新的文件，后续读取合并出的新文件。在特征需要保留所有明细数据版本的场景下，由于 Compaction 是文件复写操作，同时无法直接清理删除保留周期内已合并过的旧文件，因此一定会存在数据和文件上的冗余。我们自然会想到能否根据数据的实际分布情况，仅合并目录中的部分文件，在加速数据读取的同时，减少合并产生的冗余存储。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/616427ea39929fa4d92a125ad9bcf901.png)

特征数据湖在主键表原有 Compaction Rewriter 的基础上，增加目录文件数量、文件大小划分和数据更新比例的前置检查，进一步平衡特征数据在主键表场景下，数据合并后带来的存储冗余和读取优化：

1. **文件数检查**：特征读取发布的线上任务运行资源基本固定。我们通过测试发现，当单个分桶内需要处理的数据量大于 Executor 内存，且文件数量多于一定阈值时，在 Task 处理过程中会触发较多的归并排序和磁盘溢写，读取耗时将明显增加。由于线上每次特征组写入的数据量基本接近，因此文件数量直接决定了读取时实际需要加载的数据量，所以在文件数量明显超出阈值时，强制进行一次合并操作，将多个文件合并成一个文件，去除读时归并带来的计算开销，后续读取时只需加载重写出的新文件即可。

2. **大小文件分组**：由于大文件的合并重写代价较高，我们在实际合并文件时，还采用类似于合成大西瓜的思路，优先合并目录内较小的文件，将小文件合并成大文件后，再将大文件与大文件合并，以此来避免过多的大文件复写冗余。通过目录内文件大小均值，将文件简单地进行划分为大小两种组别，分布进行校验合并，本质上减少了一些大文件合并的频度和频次。此外由于全量特征数据存在一个事实上的数据上限（如当前用户数量上限，现有广告数量上限），因此大文件组别的合并终态是多个全量数据文件合并成出一份大小基本无变化的新全量数据文件。

3. **数据更新比例检查**：增量更新特征组的数据每次均只存在一定比例的更新，当一组文件内整体更新比例较低时，合并重写出的新文件大小基本等于合并前的文件大小总和，存储冗余高，压缩效果并不明显。为了减少此类数据合并的触发，我们在数据不超过设定的单个 Bucket 容量上限时，根据 Snapshot 从旧到新的次序，依次加载文件并检查范围内的平均数据更新比例，直至平均更新比例低于目标值，仅合并该范围内符合条件的数据文件。

综上所述，整体 Compaction 策略可以概括为 ：先对文件按照大小分层（L0 .. Ln)，每层设置一个文件数目的上限阈值，当文件数到达上限时，合并该层所有文件。策略的选定基于下述 2 点假设：

1. 增量更新的比例较小时，大部分 Compact 都发生在 L0 层，大文件不会轻易重写，可以有效减少大文件的冗余。

2. 增量更新的比例较大时，大部分 Compact 都发生在 Ln 层，但新增的文件已经涵盖大部分用户，即此时大文件间彼此重合比例很高，合并后不会有额外冗余。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/f87941354adab13b81903e449883768c.png)

#### **4.2.2 同比节省冗余数据约 60%**

通过减少不必要的文件合并，增量更新合并方案在长周期运行后，测试数据表整体数据量从 3040 GB 降至 1270 GB，减少约 60%；文件数从 5642 降至 1888，减少约 2/3，在存储资源开销和对 HDFS 负载上都更优。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/a3c06a8d912d0a1408db40fca7eca697.png)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/c9c1c0438620439a5bcccd106aa2dd27.png)

## **五、特征数据应用：显著提效发布与补录**

特征数据应用有两个重要的下游场景，一个是读取发布至在线 KV，另一个是历史样本特征补录。针对读取发布场景，我们拓展了 Iceberg 原有的分区 Transform 能力，使得发布读取操作变为 MapOnly，减少 Shuffle 带来的额外耗时。针对特征补录场景，由于主键表均使用主键分桶的分区规则，我们可以利用到 Spark SPJ 特性，消除多表 join 时的 Shuffle，大幅提供多表 join 的执行效率。

### **5.1 自定义分区，MapOnly 读取提效发布**

#### **5.1.1 发布旧流程性能瓶颈**

在特征写入离线特征仓库后，发布任务需要读取离线数据，按照 Marvel 的分组方式重新 shuffle 并生成 KV File 用于加载。由于 KV 系统使用的自定义 Hash 函数且分组数固定为 8192，与线上生产任务的数据分组规则都不一致，数据 shuffle 的代价极大，导致发布任务的吞吐量和处理效率均较低。

Iceberg 内部提供根据数据列进行分组分桶（Bucket）的算法，但固定使用 MurmurHash3 规则且并不支持扩展。KV 系统分组规则出于均衡请求的目的，分组数很多（固定为 8192），直接复用到离线侧会导致 HDFS 生产出大量小文件的问题。为了进一步提升效率，我们决定将离线数据的分布方式与在线 KV 的分组方式进行一对多映射，来平衡计算和存储的 trade-off。

基于湖仓提供的 Bucket Transform，我们拓展出自定义的 KV-Bucket Transform 函数，实现表内一个分桶 Bucket 有序映射 KV 侧多个分组的对照关系，既避免了直接对照分组时离线侧小文件过多的问题，也使得发布读取生产文件时可以省去 Shuffle，能够直接以 MapOnly 的方式生成 KV File。

优化前 & 优化后的整体逻辑变化如图所示：

![](https://developer.qcloudimg.com/http-save/yehe-1009891/426514a86fad33db7536d5f0d9aca11e.png)

![](https://developer.qcloudimg.com/http-save/yehe-1009891/7fd00d6d8a9544f0c23bba6c921be25d.png)

### **5.2 SPJ 消除多表 Join Shuffle**

#### **5.2.1 SPJ 介绍与主键表适配**

在 OLAP 分析及下游补录（将特征拼接到历史样本上以生成新的样本）读取时，常常需要跨表、跨时间分区读取很多份数据，之后会根据主键 Join 后再继续分析使用。由于主键数量庞大，多表 join 操作带来的 Shuffle 开销巨大，甚至成为了主要的计算耗时。如何消除多表 join 间的 shuffle，就成为了补录和 OLAP 分析优化的主要目标。

业界对于多表 Join 的 shuffle 消除一般有两个通用的方法，一个是 mapjoin（也被称之为 broadcast join），另外一个则是 bucket join。其中 mapjoin 要求关联的多表之间存在小表，可以直接将小表整表发给多个分布式任务，避免掉大表昂贵的 shuffle 操作。由于大表 join 小表在多表 join 中仅占一小部分，map join 优化并不是普适的优化。Bucket join 的原理则是对需要 join 的两边提前做好数据预分布，利用这些预分布信息可以用来避免昂贵的 shuffle 操作。Hive/Spark 社区的 bucket join 要求数据写入时分布必须跟 hive/Spark 内置的 hash 分布一致，不然会出现数据正确性问题。因此 bucket join 在实际落地时会存在较多的限制。

Spark SPJ（Storage Partitioned Join) 是 Spark 社区利用数据 partition 信息来消除 join shuffle 的另外一个尝试，它本质上是 bucket join 的超集：和 bucket join 类似，SPJ 利用了 partition 级别的数据分布信息（partition 分布可以是 bucket 分布）来消除多表 join 的 shuffle。SPJ 除了支持 bucket 这类分区分布之外，也支持其他的 partition 变换，比如两张表都是按小时分区的，则其用小时来关联时，对应的 shuffle 也可以被消除。

SPJ 示例

假设表 A 和表 B 均对列 c1 做了 bucket 分区，则下述的 Join SQL 可以优化成无 shuffle 的。

代码语言：javascript

复制

```
SELECT * FROM A JOIN B on A.c1 = B.c1
-- Table A: bucket(c1, 4)
-- Table B: bucket(c1, 4)
```

如无 SPJ 优化，则上述 SQL 对应的执行计划为：

代码语言：javascript

复制

```
SortMergeJoin
  -- Sort
    -- Exchange
      -- Project
        -- Scan Table A
  -- Sort
    -- Exchange
      -- Project
        -- Scan Table B
```

如应用 SPJ 优化，优化 c1 和 c2 的 bucket 数据分布已经满足 join 的数据分布要求，则上述的 join 是无 shuffle 的。

代码语言：javascript

复制

```
-------- Table A  --------  Table B --------
    bucket_id = 0 <------>  bucket_id = 0
    bucket_id = 1 <------>  bucket_id = 1
    bucket_id = 2 <------>  bucket_id = 2
    bucket_id = 3 <------>  bucket_id = 3
    
-- 对应的计划为
SortMerJoin
  -- Sort
    -- Project
      -- Scan Table A
  -- Sort
    -- Project
      -- Scan Table B
```

主键表要求使用主键作为 bucket 分区，其天然满足了 SPJ 的数据分布要求，也即我们的主键表天然支持 SPJ 优化。通过规范统一特征离线存储表的分区，很多计算逻辑下可以利用 SPJ 的特性来加速任务的执行效率，在 Spark SQL 适配自定义的 Marvel Bucket Transform 后，Spark Join 的执行性能可提升 50%。

#### **5.2.2 历史特征补录效率提升12倍**

#### 

当模型需要应用新的特征时，需要先将特征拼接到历史样本上以生成新的样本进行训练，样本拼接特征开销很大。在增量更新的特征组场景下，由于 HDFS 分区存储无法获取到全量快照，因此仅拼接当天的增量数据，也损失了一些数据的准确性。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/bc83efc5db332c814eca1446746a3ec0.png)

在特征存储迁移至全列存后，将补录特征的读取精确到了特征 ID & 列级别，在抽取时可 DataSkip 掉同一个特征组中无需使用的数据，提高加载性能。补录多个特征组的数据时，利用 SPJ 的特性减少了大量预处理阶段的 Shuffle，减少补录任务的计算开销，整体补录效率提升约十倍，新特征调研周期由1周降为1天且更评估更为准确，在样本侧也迁移至 Iceberg 后可以实现全流程无 Shuffle。

![](https://developer.qcloudimg.com/http-save/yehe-1009891/7161e4be48ece497f05fb8adc78fbae7.png)

## **六、未来展望**

未来广告特征工程团队和智能湖仓团队将继续合作共建，持续优化流批一体场景下数据湖的读写性能，减少数据更新对下游的可见时延，提高数据在不同场景下的跨表加载效率。同时，针对具体的业务数据提供智能化、自适应的合并逻辑，精细化管理存储的生命周期和冗余副本。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)，分享自微信公众号。

原始发表：2024-12-05，如有侵权请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除

[数据湖](https://cloud.tencent.com/developer/tag/11418)

[数据](https://cloud.tencent.com/developer/tag/17440)

[腾讯](https://cloud.tencent.com/developer/tag/17464)

[优化](https://cloud.tencent.com/developer/tag/17554)

[存储](https://cloud.tencent.com/developer/tag/10665)

本文分享自 腾讯大数据 微信公众号，前往查看

如有侵权，请联系 [cloudcommunity@tencent.com](mailto:cloudcommunity@tencent.com) 删除。

本文参与 [腾讯云自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)  ，欢迎热爱写作的你一起参与！

[数据湖](https://cloud.tencent.com/developer/tag/11418)

[数据](https://cloud.tencent.com/developer/tag/17440)

[腾讯](https://cloud.tencent.com/developer/tag/17464)

[优化](https://cloud.tencent.com/developer/tag/17554)

[存储](https://cloud.tencent.com/developer/tag/10665)

评论

登录后参与评论

0 条评论

热度

最新

登录 后参与评论

推荐阅读

目录

* 一、相关背景

* 二、业务架构概览
  + 2.1 数据湖存储底座选型：Iceberg vs Hudi

* 三、特征入湖：以主键为基础，支持流式特征分钟级更新
  + 3.1 高效主键表
    - 3.1.1 方案及流程介绍
    - 3.1.2 性能分析及验证
  + 3.2 列可重叠的多流数据合并
    - 3.2.1 业内开源方案对比
    - 3.2.2 支持流式特征分钟级入库

* 四、存储管理优化：多版本、细粒度的统一接口，自适应、低冗余的文件合并
  + 4.1 透明且统一的多版本特征读写
    - 4.1.1 业务背景及接口方案
    - 4.1.2 实现特征 CDC 粒度分钟级回滚
  + 4.2 低冗余增量文件合并
    - 4.2.1 现有流程与优化思路
    - 4.2.2 同比节省冗余数据约 60%

* 五、特征数据应用：显著提效发布与补录
  + 5.1 自定义分区，MapOnly 读取提效发布
    - 5.1.1 发布旧流程性能瓶颈
  + 5.2 SPJ 消除多表 Join Shuffle
    - 5.2.1 SPJ 介绍与主键表适配
    - 5.2.2 历史特征补录效率提升12倍

* 六、未来展望

相关产品与服务

对象存储

对象存储（Cloud Object Storage，COS）是由腾讯云推出的无目录层次结构、无数据格式限制，可容纳海量数据且支持 HTTP/HTTPS 协议访问的分布式存储服务。腾讯云 COS 的存储桶空间无容量上限，无需分区管理，适用于 CDN 数据分发、数据万象处理或大数据计算与分析的数据湖等多种场景。

[产品介绍](https://cloud.tencent.com/product/cos?from=21341&from_column=21341)[产品文档](https://cloud.tencent.com/document/product/436?from=21342&from_column=21342)

[对象存储COS新用户低至1元！](https://cloud.tencent.com/act/pro/cos?from=21344&from_column=21344)

领券

* ### 社区

  + [技术文章](https://cloud.tencent.com/developer/column)
  + [技术问答](https://cloud.tencent.com/developer/ask)
  + [技术沙龙](https://cloud.tencent.com/developer/salon)
  + [技术视频](https://cloud.tencent.com/developer/video)
  + [学习中心](https://cloud.tencent.com/developer/learning)
  + [技术百科](https://cloud.tencent.com/developer/techpedia)
  + [技术专区](https://cloud.tencent.com/developer/zone/list)
* ### 活动

  + [自媒体同步曝光计划](https://cloud.tencent.com/developer/support-plan)
  + [邀请作者入驻](https://cloud.tencent.com/developer/support-plan-invitation)
  + [自荐上首页](https://cloud.tencent.com/developer/article/1535830)
  + [技术竞赛](https://cloud.tencent.com/developer/competition)
* ### 圈层

  + [腾讯云最具价值专家](https://cloud.tencent.com/tvp)
  + [腾讯云架构师技术同盟](https://cloud.tencent.com/developer/program/tm)
  + [腾讯云创作之星](https://cloud.tencent.com/developer/program/tci)
  + [腾讯云TDP](https://cloud.tencent.com/developer/program/tdp)
* ### 关于

  + [社区规范](https://cloud.tencent.com/developer/article/1006434)
  + [免责声明](https://cloud.tencent.com/developer/article/1006435)
  + [联系我们](mailto:cloudcommunity@tencent.com)
  + [友情链接](https://cloud.tencent.com/developer/friendlink)
  + [MCP广场开源版权声明](https://cloud.tencent.com/developer/article/2537547)

### 腾讯云开发者

![扫码关注腾讯云开发者](https://qcloudimg.tencent-cloud.cn/raw/a8907230cd5be483497c7e90b061b861.png?imageView2/2/w/200)

扫码关注腾讯云开发者

领取腾讯云代金券

### 热门产品

* [域名注册](https://cloud.tencent.com/product/domain?from=20064&from_column=20064)
* [云服务器](https://cloud.tencent.com/product/cvm?from=20064&from_column=20064)
* [区块链服务](https://cloud.tencent.com/product/tbaas?from=20064&from_column=20064)
* [消息队列](https://cloud.tencent.com/product/message-queue-catalog?from=20064&from_column=20064)
* [网络加速](https://cloud.tencent.com/product/ecdn?from=20064&from_column=20064)
* [云数据库](https://cloud.tencent.com/product/tencentdb-catalog?from=20064&from_column=20064)
* [域名解析](https://cloud.tencent.com/product/dns?from=20064&from_column=20064)
* [云存储](https://cloud.tencent.com/product/cos?from=20064&from_column=20064)
* [视频直播](https://cloud.tencent.com/product/css?from=20064&from_column=20064)

### 热门推荐

* [人脸识别](https://cloud.tencent.com/product/facerecognition?from=20064&from_column=20064)
* [腾讯会议](https://cloud.tencent.com/product/tm?from=20064&from_column=20064)
* [企业云](https://cloud.tencent.com/act/pro/enterprise2022?from=20064&from_column=20064)
* [CDN加速](https://cloud.tencent.com/product/cdn?from=20064&from_column=20064)
* [视频通话](https://cloud.tencent.com/product/trtc?from=20064&from_column=20064)
* [图像分析](https://cloud.tencent.com/product/imagerecognition?from=20064&from_column=20064)
* [MySQL 数据库](https://cloud.tencent.com/product/cdb?from=20064&from_column=20064)
* [SSL 证书](https://cloud.tencent.com/product/ssl?from=20064&from_column=20064)
* [语音识别](https://cloud.tencent.com/product/asr?from=20064&from_column=20064)

### 更多推荐

* [数据安全](https://cloud.tencent.com/solution/data_protection?from=20064&from_column=20064)
* [负载均衡](https://cloud.tencent.com/product/clb?from=20064&from_column=20064)
* [短信](https://cloud.tencent.com/product/sms?from=20064&from_column=20064)
* [文字识别](https://cloud.tencent.com/product/ocr?from=20064&from_column=20064)
* [云点播](https://cloud.tencent.com/product/vod?from=20064&from_column=20064)
* [大数据](https://cloud.tencent.com/product/bigdata-class?from=20064&from_column=20064)
* [小程序开发](https://cloud.tencent.com/solution/la?from=20064&from_column=20064)
* [网站监控](https://cloud.tencent.com/product/tcop?from=20064&from_column=20064)
* [数据迁移](https://cloud.tencent.com/product/cdm?from=20064&from_column=20064)

Copyright © 2013 - 2026 Tencent Cloud. All Rights Reserved. 腾讯云 版权所有

[深圳市腾讯计算机系统有限公司](https://qcloudimg.tencent-cloud.cn/raw/986376a919726e0c35e96b311f54184d.jpg) ICP备案/许可证号：[粤B2-20090059](https://beian.miit.gov.cn/#/Integrated/index)![](https://qcloudimg.tencent-cloud.cn/raw/eed02831a0e201b8d794c8282c40cf2e.png)[粤公网安备44030502008569号](https://beian.mps.gov.cn/#/query/webSearch?code=44030502008569)

[腾讯云计算（北京）有限责任公司](https://qcloudimg.tencent-cloud.cn/raw/a2390663ee4a95ceeead8fdc34d4b207.jpg) 京ICP证150476号 |  [京ICP备11018762号](https://beian.miit.gov.cn/#/Integrated/index)

[问题归档](https://cloud.tencent.com/developer/ask/archives.html)[专栏文章](https://cloud.tencent.com/developer/column/archives.html)[快讯文章归档](https://cloud.tencent.com/developer/news/archives.html)[关键词归档](https://cloud.tencent.com/developer/information/all.html)[开发者手册归档](https://cloud.tencent.com/developer/devdocs/archives.html)[开发者手册 Section 归档](https://cloud.tencent.com/developer/devdocs/sections_p1.html)

Copyright © 2013 - 2026 Tencent Cloud.

All Rights Reserved. 腾讯云 版权所有

登录 后参与评论

000推荐