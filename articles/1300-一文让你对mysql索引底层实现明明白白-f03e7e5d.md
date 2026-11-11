---
title: '一文让你对mysql索引底层实现明明白白'
company: 京东
tag: 索引构建
date: 2024-01-18
url: http://mp.weixin.qq.com/s?__biz=MzUyMDAxMjQ3Ng==&mid=2247504988&idx=1&sn=9d864776624b50046b4e986306762943&chksm=f9f2438fce85ca99f136444b10c37ab22750158978a62152124658094f49ef20a9835073c949#rd
account: 京东零售技术
origin: wechat-mp
---
# 我们在数据查询过程中，经常会因为慢sql引发线上问题，那么怎么快速地提高数据库查询速率？ MySQL索引可以极大地提升查询效率，那么为什么查询效率高？索引原理又是什么？本文将对数据结构介绍和索引实现原理进行逐步分析。

**一、索引到底是什么**

* 索引是帮助mysql高效获取数据的排好序的数据结构
* 索引是存储在文件里的
* 数据结构：二叉树 HASH BTREE

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93XDKMsN9oMnCcyqpxNuffrniaJpZSl8slEaQvPC65SGAVISW20PqSOO8Q/640?wx_fmt=png&from=appmsg)

如果没有索引的话，循环一条一条地找，找一次就是一次IO，这样速度就会很慢。

我们知道数据库数据都是存在磁盘上的，当我们查找数据时，就会从磁盘上取数据,每取一次就是一次IO，IO是非常耗时的，为了速度快会把数据放到缓存里，然后在缓存里进行操作。

****二、磁盘存取原理****

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93XLgYN4oMxhn2u4jBdQAeV8CpIXQl9vUByszszEE313WopHOGqkIQAKQ/640?wx_fmt=png&from=appmsg)

当查找数据的时候，就是磁头循环找此道，就会一直循环查找，一次查找就是一次IO，IO是很耗时的。

****三、Mysql数据结构详解****

就拿上面的7条数据来说，如果没有索引，当我们查找第7条数据时，就会循环7次，如果有百万级别的数据，那么就会查找百万次，显然这样是不行的，就需要数据结构算法来优化，那我们就从二叉树----HASH---BTREE来一一说起。

**【 3.1 二叉树 】**

二叉树节点保存的都是单个索引，高度会随着数据增大而增高，但是比一条一条的循环会快。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRkoOVx68gP17Y4P61V4SQ7QRjUTOu3nHf7snC3wMsibZDo322dYGpaK5Q/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRkjbYhRH8kGEVvw4ZpuRLHYcZuhI52oRpVZTeSI8vXT8X518kbA4WV4g/640?wx_fmt=jpeg)

不用二叉树是因为极端情况下会出现单边增长，这样在数量大的情况下，和一条一条查找没有区别。

**【 3.2 红黑树 】**

红黑树有自平衡性质，不会出现单边增长，它会动态自旋转，在性能上比二叉树又高一点，但是mysql也没有用这种数据结构，因为数据量超大的情况下，数据高度也会一直增大，在最终这个树高度也非常大，解决不了根本问题。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRk1t6SWyfYhUSFNtvEAexUw7kOr6NTx1AuHlz25icE3vKtRfYrBla3QibA/640?wx_fmt=jpeg)

**【 3.3 HASH 】**

hash算法一次就会定位到文件指针，速度快，但是还是没有用，如果范围查找的话就没有办法了，如果只是内存中的话，他的时间复杂度是O(1),速度会会很快，但是索引文件也是保存在磁盘上，而且hash是不连续的放在磁盘上的，这样查询起来也很慢，这才是不用hash的最根本原因。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93Xn2xWtEspgG6guj5qAENls04362etfwvKC6Mebc9EwAoEe3JTcnlC2g/640?wx_fmt=png&from=appmsg)

**【 3.4 B-TREE 】**

相比上面的数据结构，b-tree增加了横向大小（度Degree），那么在高度上就减小了，查找次数就少了。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93X7iahsia5UNRLjoo3NqYUxNkaRaBw6HVXjHOeK5NCvXVib8ZSUWKXV6RMA/640?wx_fmt=png&from=appmsg)

15，56，77.。。。。是索引，data就是对应的一行数据

那么在横向的度上最大多少合适呢？？总不能横向上一直扩展下呀，磁盘一次IO，就是取一个横向的节点（度），把一个节点的数据放在缓存中，那么一次IO也不能把所用的数据全取出来，所以最好是一次io，就把这个节点全取处理，电脑操作系统从磁盘一次取数据到内存中一般是4K，而mysql取一次数据一般是**16K**，所以横向节点一般设置为**16K**。因为一个节点设置成16K的话，这个节点保存了索引和索引对应行的数据，那么这个节点横向保存不了太多的数据，所以，这种数据结构也不合适，引入新的数据结构。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93Xia7HdQPdF4gzfMWyPibnyTkC7O4MdlGH1lL6x0q4kNicaKHqkCiaY2TFpA/640?wx_fmt=png&from=appmsg)

**【 3.5 B+Tree 】**

查找一次数据就是和磁盘一次IO，一次IO会把这个数据相邻的数据一下全部查处理，这样速度会更快，这样的一页就是咱们说的一个节点（4K），分配空间的时候也是一页一页分配的，这样会更快，一页就是一个节点。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93XWfBjibvzT3S8b4M8N0t0r1b2rf7Hc1Hfdj76gWqwwrgTBVtV0raY7YQ/640?wx_fmt=png&from=appmsg)

**mysql 常用的引擎有MyISAM和InNoDb,两种引擎的索引结构是不一样的。**

**MyISAM的数据结构：**

.frm表结构文件 .myd表数据文件 .myi表索引文件

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRkNFP6cYjxCBjGVmVc9SS7OyUacqr7OicwxOvU9NjLewPh6xwMvwQDmeg/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/MrFJyDNenFics1OIRdQwoibMbib11AHh93X19tHBodWhA9oEiarBVLxA78XxvtWXWjVVdLN0LIAcALNTka2C37c8FQ/640?wx_fmt=png&from=appmsg)

myisam引擎的主键索引数据结构是左上图，普通索引是右上图，叶子节点存的不是数据本身，是数据文件指针，和b\_tree数据不一样，注意：每类的索引，都是各自的树，不是混合在一起的。

.frm表结构文件 .ibd 表数据和索引文件

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRk3h2AVjLShNv81ZibicmwYdqlB0siagVB3zvichHU5MrM2kTjBLicruSoVaQ/640?wx_fmt=jpeg)

**‍****InnoDB索引实现(聚集)：**

* 数据文件本身就是索引文件
* 表数据文件本身就是按B+Tree组织的一个索引结构文件
* 聚集索线引一叶节点包含了完整的数据记录----（主键）
* 为什么InnoDB表必须有主键，并且推荐使用整型的自增主键？
* 为什么非主键索引结构叶子节点存储的是主键值？（一致性和节省存储空间)

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRkd3R52nXPm8a38yfFQSBzhFkNfHIKGTkibgeuh4Vq03YSDTmlaaL1GvQ/640?wx_fmt=jpeg)

主键索引是聚集索引，因为叶子节点是所有的数据，就是一行数据，非主键索引叶子节点只包括索引和主键，再用主键找对应数据。

非主键索引叶子节点只包括索引和主键，再用主键找对应数据，这样是为了节省空间和数据一致性。

**联合索引：**

**要满足最左原则**

联合索引(col1, col2, col3)也是一棵B+树，其非叶子节点存储的是第一个关键字的索引，而叶子节点存储的则是三个关键字col1、col2、col3三个关键字的数据，且按照col1-col2-col3的顺序进行排序。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/MrFJyDNenF9Dfa07k7M0bR4oqX6UhVRkRsC0XBh5V2NIqso1brZLpLST4Um8GMhYLgtzl5HTeM0kJhzKslPfPw/640?wx_fmt=jpeg)

例如：

如果执行: SELECT \* FROM T WHERE B=‘赵六’ AND C=123;

那么无法使用索引，因为索引是用A字段先排序的，如果没有先确定A，直接查找B和C，那么将会是全表查询。

如果执行: SELECT \* FROM T WHERE A=‘30’ ;

那么，会先找到A字段，再在A等于30的数据中（比如有很多条），找B等于DE的数据。这样是可以用到索引的‍

如果执行: SELECT \* FROM T WHERE A=‘18’ AND C=345;

那么，A字段可以索引，而C不能索引。所以可以部分索引，也比全表查询快

如果执行 : SELECT \* FROM T WHERE B=DE AND C=1234 and A=‘2’

是用到索引的，在and的情况下如果把第一个放到最后位置也是能用到索引的

现在我想大家应该了解了什么为什么是最左原则。因为，B+树是按照最左边的字段以此构建的。

-    **END**    -