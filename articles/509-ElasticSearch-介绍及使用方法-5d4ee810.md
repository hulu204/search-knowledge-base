---
title: 'ElasticSearch   介绍及使用方法'
company: 360
tag: 工程相关
date: 2019-12-27
url: http://mp.weixin.qq.com/s?__biz=MzkzNzI0MDMxNQ==&mid=2247487444&idx=1&sn=21618afb5aacc0ea224afdbb1e4fa155&chksm=c2933c40f5e4b5569ab5b0dd73d9a5233eee75dab93b53d23b9541e9230193a2560ce90869a8&mpshare=1&scene=1&srcid=0117mZBwP4XZjMn1x1cMkohc&sharer_sharetime=1673957427902&sharer_shareid=c032e8bde4d276951619cca1ff0debb1#rd
account: 360技术工程
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaoyyCXr7hticv8jvEic1dT4sFsC1ZrEfSpvyg9j2f8xicoAXlgrvDJkcDg/640?wx_fmt=png)

**简介**

ElasticSearch是一款基于 Apache Lucene的开源搜索引擎产品，之后成了独立的商业公司，继而发布了ELK等一系列产品，特点是开源、分布式、准实时，标准的RESTFul接口等。

ElasticSearch可以单机部署，也可以集群部署。ES的分布式属性，可以轻松的处理超过单机负载能力的数据量，集群也是无间断服务的一种解决方案。

**整体架构**

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYabQ379fRh4lic3niczcHgib5d57fhaPkHaMxPlGKD7YRFjicT6qSZQtfFWg/640?wx_fmt=png)

**基本概念**

* **Node**：单个的ElasticSearch服务实例。
* **Master**：负责监督、控制其它节点的工作。
* **Data**：持有数据，并提供数据的索引功能，主要用途是索引和查询数据。
* **协调节点**：每一个节点都是一个潜在的协调节点，协调节点会处理请求，将各分片里的数据汇集起来一并返回给客户端，ES的节点需要有足够的CPU和内存去处理协调节点的gather 阶段。
* **索引**：EasticSearch将数据存储在一个或多个索引中， 用SQL领域的术语来类比，索引就像数据库，可以向索引中写入文档或者从索引中读取文档，内部使用Lucene。
* **分片**：ES将数据分散到多个物理的Lucene索引，这些Lucene索引就称为分片。分散分片的过程，称之为sharding。
* **主分片**：主分片的数量在索引创建时就被配置好了，之后无法改变，除非创建一个新索引并重新索引全部数据。
* **副本分片**：副本主要有以下作用，1 分担访问压力；2 给ES集群提供安全机制；3会增加写入的时长。

* **类型（type）**

5.x 版本中index和 type为一对多关系，不同type定义对应的mapping。

6.x 版本中index和 type为一对一关系。

7.x 版本中移除了type，一个索引只定义一个数据类型。

将来会在8.x中彻底移除。

* **文档（doc）**

doc是ES中的主要实体：

1. 对于所有使用ES的案例来说，最终都会被归结到文档的搜索之上。
2. 文档由字段构成，每个字段包含字段名以及一个或多个字段值。
3. 从用户端的角度看，文档是一个Json对象。

* **集群健康状态**

**Green**：表示所有主分片和副本分片都可用。

**Yellow**：表示所有主分片可用，但不是所有副本分片都可用。

**Red**：表示部分主分片处于不可用状态

**ES操作**

**索引设计**

**索引设计主要包括 mapping和setting两部分**

Settings用于设置分片和副本数

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaVHWKIgHJ145vbFEAOt3sBmtUOeDUEEp5y5raIccVwFHOm5jCSXU3Kg/640?wx_fmt=png)

**查看setting：**

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYatzFjte6zdDL4AT18nteOuese3QBleQ4O7QKIp2CWxVIHFttytaoTVA/640?wx_fmt=png)

**Mapping（映射）**

mappings用于设置字段和类型。

动态mapping：根据索引的数据动态的生成 mapping

不建议使用动态mapping，主要原因：

1. 会引发性能下降。
2. 影响磁盘空间的使用。
3. 导致与预期查询不符的结果。

查看mapping语法：

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaFGBnAWDKsjENfPotVgueTAYQNtkjugqU7CeUdVtMS4ktWqHTOAzMibA/640?wx_fmt=png)

**模板**

Logstash 使用事件中的时间戳来生成索引名，@timestamp 为 2019-10-01 00:00:01 事件将被发送至索引 logstash-2019.10.01 中，通常我们想要控制新建索引的设置（settings）和映射（mappings）

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaUv2UVJkxEd9ud9qZd0BVKbhwdqPNr0uadjmm3h2DibmGYSJnRmFbTVA/640?wx_fmt=png)

上面的API做了如下操作：

* 创建一个名为 my\_logs 的模板；
* 将这个模板应用于所有以 logstash- 为起始的索引；
* 设置模版的顺序级别；
* 限制主分片数量为 10；
* 为所有类型禁用 \_all 域。

常用API：

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaC9GQ4kXJXTpvRCBypiaOhTZSzBtibBvO9ibLLaTWlNJSgM5AibTV7MMjOw/640?wx_fmt=png)

**写入操作****：**

实际过程中，提交操作会进行一次完整的 HTTP POST 请求和 ES indexing，单条数据是一种极大的性能浪费，ES 设计了批量提交方式， bulk接口：

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaad7gYZWC13icWWxQdDhRbnm8XaF0PKvhibs4yrS0Gd8U66ANmoujol6A/640?wx_fmt=png)

Bulk像一个集合，把一系列操作批量提交，这在很大程度上提高了ES的写入效率。

**bulk的使用和大小设置**

1. 整个bulk请求需要被加载到接收请求节点的内存里，所以请求越大，给其它请求可用的内存就越小。因此，有一个最佳的bulk请求大小，超过这个大小，性能不再提升而且可能降低。
2. 最佳大小，并不是一个固定的数字, 取决于硬件、文档的大小和复杂度以及索引和搜索的负载情况。
3. 开始的数量可以在1000~5000个文档之间，如果文档非常大，可以使用较小的批次。通常着眼于你请求批次的物理大小是非常有用的，一千个1kB的文档和一千个1MB的文档大不相同。
4. 一个好的批次最好保持在5-15MB大小间。

**数据检索过程**

数据检索主要分为两个阶段，**query**阶段和**fetch**阶段：

**query**阶段：

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaZ1uhQ6e2FDGK9xkV7TvuZwnQsED6r3flMdhpfCxf7FicicVonKVBs9BA/640?wx_fmt=png)

1. 客户端发送一个search请求到Node 3上，然后Node 3会创建一个优先级队列（大小=from+size）。
2. Node 3转发这个search请求到索引里面每一个主shard或者副本shard上，每个shard会在本地查询然后添加结果到本地的排序好的优先级队列里面。
3. 每个shard返回docId和所有参与排序字段的值到优先级队列里面，然后再返回给coordinating节点也就是Node 3，然后Node 3负责将所有shard里面的数据合并到一个全局的排序列表。

**Fetch阶段：**

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaqgxzdribVh6t2mic4DEnYM2lSMMwIVhJeyEuFAgpWfXO5G9CxSQPicPCA/640?wx_fmt=png)

1. coordinating节点标识了那些document需要被拉取出来，并发送一个批量的mutil get请求到相关的shard上。
2. 每个shard加载相关document，如果需要它们将会被返回到coordinating 节点上。
3. 一旦所有的document被拉取回来，coordinating节点将会返回结果集到客户端上。

**scroll 读取（游标查询）**

**优点：**

Scroll 有效地执行大批量的文档查询，而又不用付出深度分页的代价，类似于传统数据库中的cursor。

**scroll使用方法：**

游标查询每次返回一个新字段 \_scroll\_id。每次做下一次游标查询时， 需要把前一次查询返回的字段 \_scroll\_id 传递进去

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaiccV0hPnuk0GbkahicsYv2SibkONXSaIqiaibQQQDAZusnozvoNqGc0Et8w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYa8dG0EBzY91mF10mI5PtibJSLLCXaibczMjpM4ibenWIib2dw2vy44YsozQ/640?wx_fmt=png)

在一些语言如 Python、perl的ElasticSearch包中，提供了这个功能易用的封装。

**别名 Index aliases**

别名很简单，但是能解决重建索引必须更新应用中索引名的问题，实现索引切换的无缝过渡。

别名像一个快捷方式或软连接，可以指向一个或多个索引，需要注意，别名不能与索引同名。

**相关API：**

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYa8qVCIu3TI3O39ZHfGu8BbRrsTPwIqNymaxmzhgZicdLFhRJniaQMcAfg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaNAAzCib73ov6Aabu3HFUlLiaHWUHOCIPh8x6zqeVhk2FgqKP3FLrhEcg/640?wx_fmt=png)

**重命名别名：**

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbqyek86x8GaMJE7cJCGjYan3MWNbvicVic8wtPF9kWFZibaQgyKcYTFjHhhzIiaWRML5ibZ3HibevBCULA/640?wx_fmt=png)

针对DSL查询，浅显的优化建议：

1. 正确使用 match、match\_phrase、term， 区分 must 、must\_not 、should等Bool查询
2. 尽量多使用filter
3. 如果不必须涉及相关性和评分的话，尽量避免相应的操作
4. 合适的数据类型（如Mapping中合理使用keyword类型）

**结束语**

本篇文章主要介绍了ElasticSearch的基本概念和实践中常用的一些方法，并没有涉及深层原理和优化的知识，在DSL、读写优化、7.x新版本等方面，还有不少知识点可以深入研究。

**关注我们**

界世的你当不

只做你的肩膀

无

![](https://mmbiz.qpic.cn/mmbiz_jpg/IwabbYzTYkbqyek86x8GaMJE7cJCGjYaMcNBJnmq49KIBwCmdcFUdxMmcJibmMJtMLj7slib0ecvA8hSGW8gtbNA/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_jpg/IwabbYzTYkbqyek86x8GaMJE7cJCGjYanRwBjNWCltriavzoiayechwYfshqxwJJFqu6icjxsHI54pUI1XqnxvrbA/640?wx_fmt=jpeg)

360官方技术公众号

技术干货|一手资讯|精彩活动

空·