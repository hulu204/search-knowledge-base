---
title: '如何合理规划Elasticsearch的索引｜得物技术'
company: 得物
tag: 索引构建
date: 2025-04-09
url: http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538473&idx=1&sn=0a83895ef8dcd555e9926151a989b663&chksm=c1610276f6168b609a3eb40d97dfb98f0e5f96f31f9d50ee0b50e4a47e93cc7b007b66366163#rd
account: 得物技术
origin: wechat-mp
---
![](http://mmbiz.qpic.cn/mmbiz_gif/AAQtmjCc74DZeqm2Rc4qc7ocVLZVd8FOASKicbMfKsaziasqIDXGPt8yR8anxPO3NCF4a4DkYCACam4oNAOBmSbA/640?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**目录**

一、背景

二、什么是index(索引)

三、索引结构详解

    1. 别名

    2. 映射

    3. 字段类型

    4. 针对字段类型选择的几条建议

    5. 索引结构与关系性数据库对比

四、索引(Shard)结构-分片与副本

    1. 什么是Shard

    2. 分片数规划

    3. 索引与资源消耗的关系

五、总结

**一**

**背景**

随着ES在业务场景中的使用逐渐增多，平台对ES集群的稳定性、管理、运维的压力逐渐增大，通过日常的运维情况来看，发现用户对ES的了解熟悉程度参差不齐，经常性的遇到索引创建不规范，或者参考别人索引的创建脚本进行创建索引，对索引没有一个比较清晰的认知，对索引结构的规划也寥寥无几，为此，平台使用了一些列手段来帮助用户提前合理规划模板，比如索引、模板的创建接入飞书审批流，平台侧会逐一结合业务场景和ES集群情况详细沟通确定索引或者模板结构；又比如ES内核增加业务不停服的动态扩分片能力，旨在进行不合理索引的治理提升ES集群稳定性（索引一旦创建分片是不能修改的），我们内部改动ES**源码实现了不停服动态扩分片。**

因此有必要从ES的索引讲起，让大家对ES的索引从概念、原理到使用有一个清晰的认知，希望日常业务场景中用到ES的同学能够抽时间读一下。当然文章避免不了存在主观的分析，大家可以在文章底部进行评论或者私聊我们，一起探讨。好了废话不多说了，现在开始介绍。

**二**

**什么是index(索引)**

> 下面会针对索引的组成和基本结构结合官方文档逐一介绍。

**基本概念**

index(索引)是索引是具有相似特征的文档（Document）集合，类似于关系型数据库中的表。每个索引都具有自己唯一的名称与\_id。并且可以进行不同的参数配置与mapping映射。以适应不同的业务场景。索引中的最小单位是文档。每一条文档(doc)都是一个json格式的数据对象。包含了实际的具体数据以及该数据所对应的元数据。文档可以是结构化，半结构化或非结构化的数据。索引在elasticsearch中被用于存储，检索与分析数据。通过对索引进行搜索与聚合操作可以快速地找到相关的文档。

> 官方描述：The index is the fundamental unit of storage in Elasticsearch, a logical namespace for storing data that share similar characteristics. After you have Elasticsearch deployed, you’ll get started by creating an index to store your data.

> 翻译：索引是Elasticsearch中存储数据的基本单位，是一个逻辑命名空间，用于存储具有相似特性的数据。在部署Elasticsearch后，您将通过创建索引来存储数据。

> An index is a collection of documents uniquely identified by a name or an alias. This unique name is important because it’s used to target the index in search queries and other operations.
>
> 翻译：索引是一种文档集合，通过名称或别名唯一标识。这个唯一名称非常重要，因为它用于在搜索查询和其他操作中定位索引。

**三**

**索引结构详解**

索引结构详解

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74DuGh6pQPQBewsshibR6bswdIAviaibichtnz0ZYGmskE8HMpLyibeYThjVwI7iase61wlQZhucRXF2lpIg/640?wx_fmt=png&from=appmsg)

```
创建索引结构PUT /index_demo{  "aliases" : {    "index_demo_alias" : { }  },  "mappings" : {    "properties" : {      "id" : {        "type" : "long"      },      "name" : {        "type" : "text",        "fields" : {          "keyword" : {            "type" : "keyword",            "ignore_above" : 256          }        }      },      "status" : {        "type" : "keyword"      },      "createDate" : {        "type" : "long"      }    }  },  "settings" : {    "index" : {      "refresh_interval" : "5s",      "number_of_shards" : "3",      "number_of_replicas" : "1"    }  }}
```

> ignore\_above属性说明：
>
> - ignore\_above的默认值通常为256个字符，这意味着任何超过256个字符的字符串将不会被索引或存储。
>
> - 该参数仅适用于keyword类型的字段，因为这些字段主要用于过滤、排序和聚合操作，不需要进行全文搜索。
>
> - ignore\_above的值以字符为单位计算，包括英文字符和汉字。例如，一个汉字和一个英文字符都算作一个字符。
>
> - 性能优化：通过限制字段长度，可以减少索引大小和查询时间，从而提高性能。
>
> - 避免资源浪费：对于包含大量数据的字段，如日志文件中的长字符串，可以通过ignore\_above避免不必要的存储和索引。

> 官方描述：Strings longer than the ignore\_above setting will not be indexed or stored. For arrays of strings, ignore\_above will be applied for each array element separately and string elements longer than ignore\_above will not be indexed or stored.

**别名**

别名将其生命置于群集状态内，由主节点（master node) 管理; 这意味着如果你有一个名为 xiaoming 的别名指向一个名为 potato 的索引，那么开销就是群集状态映射中的一个额外键，它将名称 xiaoming 映射到具体的索引字符串。这意味着与其他指数相比，别名的重量要轻得多; 可以维护数千个而不会对集群产生负面影响。

> 官方原话：An alias points to one or more indices or data streams. Most Elasticsearch APIs accept an alias in place of a data stream or index name.

> Aliases enable you to:
>
> - Query multiple indices/data streams together with a single name
>
> - Change which indices/data streams your application uses in real time
>
> - Reindex data without downtime

> 翻译：别名（Alias）可以指向一个或多个索引或数据流。大多数Elasticsearch API接受别名代替数据流或索引名称。别名的功能包括：
>
> - 使用单一名称查询多个索引/数据流；
>
> - 实时更改应用程序使用的索引/数据流；
>
> - 在不中断服务的情况下进行扩分片。

可以看到索引有上面三个作用，**平台建议为每个索引添加别名**（动态扩分片依赖别名）。添加别名可以在索引创建时和创建后再添加，即索引可以随时添加，但是平台还是建议你在创建索引时候指定别名，**避免动态扩分片时候再去修改代码重新部署应用。**

**添加别名的几种方式**

**1. 创建索引时指定别名**

```
PUT /test_index{    "settings" : {        "number_of_shards" : 1,        "number_of_replicas" : 1    },    "aliases":{"test_alias":{}},    "mappings" : {        "properties" : {            "field1" : {                 "type" : "text"             },            "createdAt": {                "type": "date",                "format": "yyyy-MM-dd HH:mm:ss"           }        }    }}
```

**2. 已存在的索引添加别名**

```
POST /_aliases{  "actions": [    {      "add": {        "index": "test_index", # 索引名        "alias": "test_alias" # 别名      }    }  ]}
```

**3. 别名更换**

> 别名更换可以零停机进行动态扩分片。

```
POST /_aliases{  "actions": [    {      "add": {        "index": "existing_index",        "alias": "test_alias" # 别名      },      {        "remove": {          "index": "old_index",          "alias": "old_test_alias" # 别名        }      }    }  ]}
```

**映射**

建立索引时需要定义文档的数据结构，这种结构叫作映射。在映射中，文档的字段类型一旦设定后就不能更改。因为字段类型在定义后，elasticsearch已经针对定义的类型建立了特定的索引结构，这种结构不能更改。借助映射可以给文档新增字段。另外，elasticsearch还提供了自动映射功能，即在添加数据时，如果该字段没有定义类型，elasticsearch会根据用户提供的该字段的真实数据来猜测可能的类型，从而自动进行字段类型的定义。

**字段类型**

字段类型（Field Type）是定义数据格式和索引方式的重要概念，它决定了字段在索引中的存储、搜索和聚合行为。下面针对日常用到最多的三个字段类型进行解释，text、keyword、Numeric（Integer、Long）。

**Text**

text字段类型是Elasticsearch中用于全文搜索的核心字段类型。它通过分析器将文本拆分为单个词，并存储为倒排索引，适用于非结构化文本的搜索和分析。然而，由于其经过分析器处理，不适用于排序和聚合操作。

**1. 特点**

* **全文搜索：**text字段类型主要用于存储和索引可读的文本内容，例如邮件正文、产品描述、新闻文章等。这些字段会被分析器（analyzer）处理，将字符串拆分为单个词（term），以便进行全文搜索。
* **分词处理：**text字段支持分词器（tokenizer），可以根据语言和需求选择不同的分词策略（如标准分词器、正则表达式分词器等）。分词后的结果会存储为倒排索引，便于快速检索。
* **不适用于排序和聚合：**由于text字段经过分析器处理，其原始字符串无法直接用于排序或聚合操作。如果需要排序或聚合，通常需要结合keyword字段类型。
* **支持多字段映射：**可以通过多字段（multi-field）映射同时使用text和keyword类型，以满足全文搜索和精确匹配的需求。

**2. 使用场景**

* **全文搜索：**适用于需要对文本内容进行模糊搜索的场景，例如搜索引擎、新闻网站、商品搜索等。
* **文本分析：**可以结合分析器（如TF-IDF、BM25等）进行文本相似性搜索或评分计算。
* **日志分析：**用于分析和搜索日志文件中的文本内容，提取关键信息。
* **内容管理：**在内容管理系统中，用于存储和搜索文档、文章等内容。

**3. 官方建议**

> Use a field as both text and keyword
>
> Sometimes it is useful to have both a full text (text) and a keyword (keyword) version of the same field: one for full text search and the other for aggregations and sorting. This can be achieved with multi-fields.
>
> 通过多字段映射同时使用text和keyword类型，可以实现全文搜索和精确匹配的双重需求。

**4. 平台建议**

* 明确业务使用场景，如果不需要进行模糊搜索的话，设置为keyword类型，来避免分词带来的存储开销，增加系统压力。

**Keyword**

keyword字段类型是一种用于存储和索引结构化数据的字段类型。

**1. 特点**

* **不进行分词：**keyword字段类型不会对字段值进行分词处理，而是将其作为整体存储。这意味着字段值会被原样存储到倒排索引中，不会被拆分成单独的单词或短语。
* **精确匹配：**由于字段值不进行分词，keyword字段类型非常适合用于精确匹配查询，例如查找特定的电子邮件地址、身份证号或状态码等。
* **tips：**在term查询中可以结合case\_insensitive属性，忽略大小写对值进行搜索，但不支持terms查询。
* **支持排序和聚合：**keyword字段类型可以用于排序和聚合操作，例如按状态码统计数量或按用户ID进行分组。
* **存储效率高：**由于不需要分词，keyword字段类型的存储开销较低，适合存储大量具有唯一性或固定值的字段。

**2. 使用场景**

* **精确查询：**适用于需要精确匹配的场景，例如查找特定的电子邮件地址、身份证号、状态码等。
* **排序和聚合：**当需要对数据进行排序或聚合时，keyword字段类型是理想选择。例如，按用户ID排序或按状态统计数量。
* **标签和分类：**用于存储标签、分类等结构化数据，例如用户画像标签（学生、IT、教师等）。
* **唯一性字符串：**适用于存储具有唯一性的字符串，如SpuId、货号、得物订单号等。

**Numeric**

数值类型，包含long、interger、short、byte、double、float等数字类型。

**1. 特点**

* **整数类型：**适用于范围查询、排序和聚合操作。由于整数类型占用空间较小，推荐优先使用范围较小的类型（如 integer 或 long）以提高索引和搜索效率。
* **浮点类型：**适用于需要高精度的计算场景。如果数据范围较大或精度要求不高，可以使用 scaled\_float 类型并设置合适的 scale 值。
* **选择合适的类型：**在满足需求的前提下，尽量选择范围较小的类型以节约存储空间和提升性能。

> tips
>
>   如果确定业务使用场景，建议keyword代替数值类型字段，如果不确定则采用多字段，keyword在term查询中性能更佳。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74DuGh6pQPQBewsshibR6bswdf6POnSfoibMzNLqiaOCGvSicEQ7Q1Etl1pfbjpicIrHasXj9pWU7yc5MicA/640?wx_fmt=png&from=appmsg)

**针对字段类型选择的几条建议**

1. 针对Text和数值类型场景的字段，尽量改成keyword字段类型，来提升查询速度。
2. 在不确定业务查询有哪些需求的情况下，设置多字段类型keyword。
3. 枚举字段没有特殊业务场景下，统一使用keyword字段类型。
4. 业务不需要范围查询的话，使用keyword字段类型（支持聚合和排序的）。
5. 对keyword字段类型进行模糊查询会性能较差，使用多字段类型wildcard来模糊查询性能更高。
6. 尽量不要使用聚合查询，text的fielddata会加大对内存的占用，如有需求使用，建议使用keyword。
7. 需要中文分词的话，不要使用默认分词器，推荐使用ik\_smart，ik\_max\_word会生成更多的分词，其中含有重复的内容，需谨慎使用。
8. 时间字段不要使用keyword，除非点查，推荐使用date/long类型，支持范围查询，建议精确到分钟，会提高查询效率。
9. keyword字段类型不适用于模糊wildcard查询，建议使用wildcard字段类型。

   ![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74DuGh6pQPQBewsshibR6bswdgUhzDW6PIyOocxxPicv6w1vAfxGErQicFkriaD9vOtLtySNvW7vy2ARaw/640?wx_fmt=png&from=appmsg)
10. 日期的查询条件为now时，并不能有效利用缓存，尽量换成绝对时间值。
11. ES默认字段个数最大1000，但建议不要超过100，对于不需要建立索引的字段，不写入ES。
12. 将不需要建立索引的字段index数据设置为false，对字段不分词，不索引可以减少很多运算操作。
13. 不建议或者禁止每次写入后立马进行显示的refresh，refresh会带来较高的磁盘IO，和CPU消耗，甚至有可能导致ES宕机。
14. 持续补充......

**索引结构与关系性数据库对比**

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74DuGh6pQPQBewsshibR6bswddyOVowlibIicQE3bISBzPDE3yF7nmJeS8TLVh8bzVlLRVUphKhcGpEYA/640?wx_fmt=jpeg&from=appmsg)

**四**

**索引(Shard)结构-分片与副本**

**什么是Shard**

**基本概念**

分片是管理文档的一个数据单元，分片是Elasticsearch中逻辑概念。ES内部把索引中文档进行按照一定路由规则（文档\_id的hash值与分片数取余）进行路由到不同的存储数据单元，存储数据单元就是分片。你可以理解为MySQL的分表。

ElS的逻辑分片就是一个Lucene索引，一个ES索引是分哦的集合，当ES在索引中搜索的时候，他发送查询到每一个属于索引的分片（Lucene索引）进行检索，最后合并每个分片的结果得到一个全局的结果集。

**分片划分**

分片分为**primary shard(主分片)**和**replicate shard(副本分片)**。

* **主分片：**索引的基本数据存储单元，每个索引被水平拆分为多个主分片，每个分片都是互相独立的。包含一部分索引的数据与索引的结构(segement)。每个分片都可以在集群中不同的节点上进行移动与复制。以提高数据的可用性与容错性。
* **副本分片：**主分片的完整拷贝，用于冗余存储和容灾，副本分片和主分片在ES节点数足够的情况下不会同时存在一个ES节点。

注意：单分片的记录条数不要超过上限2,147,483,519。

* **主副分片分布示意图**

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74DuGh6pQPQBewsshibR6bswdvfjBHiaYwRj7ttlic0U9lyk18WS75e2xday2ceBVLw6hhKcvrN8gXWwg/640?wx_fmt=jpeg&from=appmsg)

**分片的功能**

**1. 主分片**

* **数据存储与写入：**所有文档通过路由算法（如 hash(\_id) % num\_primary\_shards（主分片数））分配到主分片，主分片负责处理索引、更新、删除等写操作。
* **扩展性：**通过增加节点和分片分布，实现数据的水平扩展。
* **不可变性：**主分片数量在索引创建时通过 number\_of\_shards 参数设定，创建后无法修改（需重建索引）。

**2. 副本分片**

* **高可用性：**当主分片所在节点宕机时，副本分片自动升级为主分片（和对应的主分片不在一个节点），避免数据丢失和服务中断。
* **读取负载均衡：**副本分片可并行处理查询请求，提升读吞吐量。
* **动态调整：**副本分片数量通过 number\_of\_replicas 参数动态配置，支持按需扩展或缩减。

**分片数规划**

> 分片的基本概念和功能咱们咱们已经了解，在日常ES运维过程中发现不少同学对分片和数量的设置没有什么概念，照搬其他同学的比较多，这是严重错误的。咱们在实际的业务场景中也要做好分片（主副）数量的规划，来避免慢查、数据倾斜、磁盘容量浪费等问题。
>
>  当索引分片数量过多时，可能会对ES性能产生不利影响。因为每个分片都需要一定量的内存来存储索引数据和缓存，从而导致内存消耗增加。另外当查询或写入数据涉及多个分片时，ES需要在节点之间进行传输和协调数据，从而增加网络开销，这也会导致查询和写入性能的降低。可见分片数量的选择需要慎重考虑。

索引在不同场景中，其分片分设置是不一样的，接下来咱们会在下面四个场景中来进行阐述。

**读场景**

索引单分片20g~40g，尽量减少分片数，可以降低热点，因为当分片数过多时，就容易出现长尾子请求，即有可能部分子请求因ES集群节点异常、Old GC、网络抖动等延迟响应，导致整个请求响应缓慢。另一方面，拆分过多的子请求无法提升数据节点请求吞吐，不能充分利用 CPU。在尽量减少主分片数的情况下，同时也可以适当增加副本数，从而提升查询吞吐。

**写场景**

索引单分片10g~20g，小分片更有利于数据写入。小分片维护的segment数量远低于大分片，在数据刷新落盘与段合并上更有优势。由于单分片数据量更少，在写入时数据可以更快地缓存至内存中并通过refresh参数更快的持久化至磁盘中。

**日志存储场景**

* 需要考虑每日写入集群的数据总量大小。通过过数据量与数据节点数评估索引分片数量。
* 在日志存储后是否需要兼顾查询与聚合性能。合理大小的分片数据量能够提高查询效率。
* 根据日志持久化策略，采用按月/周/天的策略生成索引。并使用ILM(索引生命周期管理策略)动态对日志索引进行完整生命周期的管理。
* 建议副本数设置为0来减少磁盘容量成本。

**小数据量索引业务场景**

对于数据量比较小的索引，增加索引分片数并不一定会带来性能提升，反而可能会带来一些负面影响。

首先，增加索引分片数会增加集群的管理开销，包括维护分片的状态、备份和恢复分片等。如果索引数据量比较小，这种开销可能会超过性能提升带来的收益。

其次，增加索引分片数可能会导致数据分布不均衡，从而影响查询性能。具体来说，如果某些分片中的数据量过小，可能会导致这些分片的查询性能比其他分片差。此外，如果查询涉及到多个分片，数据的合并操作也会增加查询时间。

因此，对于数据量比较小的索引，在查询场景下，通常建议将分片数设置为1或2，以避免不必要的开销和性能问题。如果需要提高查询性能，可以考虑配置索引副本，优化查询语句或使用缓存。

**通用场景**

* 根据实际业务场景提前规划预算索引数据量，做好分片数量规划（索引一旦创建无法修改分片数）。
* 分片数量：推荐公式：主分片数 ≈ 总数据量 / 单分片容量上限（官方建议单分片10-50GB，单个分片文档数在1亿条以内，日志场景可放宽至50-100GB）。

  > 注意：分片数量平台强烈建议或者要求设置为ES data节点角色的整数倍。

* 副本数量：增加副本数可提升读性能，但会降低写入速度（需同步更多副本），因此在读场景可以酌情考虑。
* 如果索引是时序类，或者数据过大，单分片几百G，可以结合生命周期和索引模板进行索引滚动管理。
* 平台不建议使用自动移routing值进行分片，默认使用文档\_id就好。

  > 原因：使用自定义routing值进行路由分片的话很容易产生数据倾斜，另外ES内部会多一些计算逻辑来如何进行分片路由，在写入较高的场景下也会有一定的性能损耗。

* 控制分片数量，分片数不是越多越好，过多分分片，也会造成ES集群元数据管理的压力，降低系统的性能损耗。
* 设置total\_shards\_per\_node，将索引压力分摊至多个节点。
* index.routing.allocation.total\_shards\_per\_node参数可以限制每个节点上的shard数量，从而将索引的压力分摊到多个节点，这样可以提高集群性能和可用性，避免某个节点过载导致整个集群出现问题。
* index.routing.allocation.total\_shards\_per\_node是一个索引级别设置（创建索引和对已有索引进行设置），语法如下：

```
PUT <index_name>/_settings{    "index.routing.allocation.total_shards_per_node":<number_of_shards>}<index_name>为索引名字，<number_of_shards>表示每个节点上该索引的分片数量。
```

**持续调整索分片**

对于集群分片的调整，通常不是一蹴而就的。随着业务的发展，不断新增的子业务 或 原有子业务规模发生突变，都需要持续调整分片数量。

**索引与资源消耗的关系**

**分片数量与内存消耗**

> 每个分片都是独立的Lucene索引，需要维护倒排索引、缓存等内存结构。分片数量过多会导致以下问题：

* **内存占用激增：**每个分片默认占用约10-30MB内存（含元数据），数千分片可能消耗数十GB内存。
* **文件句柄耗尽：**集群总分片数过多会占用大量文件描述符，可能触发"too many open files"错误。
* **CPU热点问题：**分片分配不均会导致部分节点负载过高。

**Segment碎片化**

> 分片由多个segment组成，segment数量过多会：

* **增加IO压力：**查询需遍历多个segment文件。
* **占用堆内存：**每个segment需加载部分元数据到内存，百万级segment可能消耗数GB内存。
* **影响GC效率：**频繁的segment合并会触发Full GC。

**五**

**总结**

创建一个索引需要结合业务使用场景考量字段类型选择和是否需要索引分词，按照数据规模和业务增长速度来确定分片和副本的数量的大小。索引的结构直接影响集群的稳定性，因此我们在创建索引的时候要养成习惯，作为技术方案的一环去仔细打磨这样才能保证线上的稳定性。

大家工作中遇到的一些稳定性问题，和使用上的一些问题都可以找我们一起探讨，寻找最优解。

**往期回顾**

[1.](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538394&idx=1&sn=51f91adc969a03f7c8baa31f6cc39c67&scene=21#wechat_redirect)[DPP推荐引擎架构升级演进之路｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538394&idx=1&sn=51f91adc969a03f7c8baa31f6cc39c67&scene=21#wechat_redirect)

[2.](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538378&idx=1&sn=f8bed5e8db97d0b0cd05c630aa55e712&scene=21#wechat_redirect)[Cursor 在前端需求开发工作流中的应用｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538378&idx=1&sn=f8bed5e8db97d0b0cd05c630aa55e712&scene=21#wechat_redirect)

[3.](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538355&idx=1&sn=9b67aef240411de3423aef55e222f82f&scene=21#wechat_redirect)[得物 iOS 启动优化之 Building Closure](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538355&idx=1&sn=9b67aef240411de3423aef55e222f82f&scene=21#wechat_redirect)

[4.](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538314&idx=1&sn=a1f2d25a7a11fd50b543c6591317fd41&scene=21#wechat_redirect)[分布式数据一致性场景与方案处理分析｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538314&idx=1&sn=a1f2d25a7a11fd50b543c6591317fd41&scene=21#wechat_redirect)

[5.](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538302&idx=1&sn=f85057dbe21821f68f9d9cd3b72fb8cb&scene=21#wechat_redirect)[从对话到自主行动：AI应用如何从 Chat 进化为 Agent？开源项目源码深度揭秘｜得物技术](https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538302&idx=1&sn=f85057dbe21821f68f9d9cd3b72fb8cb&scene=21#wechat_redirect)

文 / 阳光

关注得物技术，每周一、三更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。

“

**扫码添加小助手微信**

如有任何疑问，或想要了解更多技术资讯，请添加小助手微信：

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74DuGh6pQPQBewsshibR6bswdEjgX9CvCxgyjibfSK161fR8bm7OuqQVbYX6TjuAiclNbVkV8Rpjsu5Vg/640?wx_fmt=jpeg&from=appmsg)