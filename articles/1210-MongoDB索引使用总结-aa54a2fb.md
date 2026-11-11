---
title: 'MongoDB索引使用总结'
company: 腾讯
tag: 索引构建
date: 2024-04-17
url: http://mp.weixin.qq.com/s?__biz=MjM5ODYwMjI2MA==&mid=2649783300&idx=1&sn=decc01bc4b085419d3398b695fd68d14&chksm=beccef7f89bb66695a893eff3b533d77dd0d250b72794bc49dd5f5265eb087aedbe2fc786478#rd
account: 腾讯技术工程
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_gif/j3gficicyOvasIjZpiaTNIPReJVWEJf7UGpmokI3LL4NbQDb8fO48fYROmYPXUhXFN8IdDqPcI1gA6OfSLsQHxB4w/640?wx_fmt=gif)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvauCTKmIUakdm23FkH2QA8wNyhWQkhLdrEXxOJslKicflGTqKdANHNXOcibGhcJ5fWVic0UbTNNhFJ3Vw/640?wx_fmt=png)

作者：mingkai

> MongoDB 是目前最流行的文档型数据库。MongoDB 的采用类 json 的存储格式对开发者来说非常友好。本文梳理了 MongoDB 索引的底层结构以及使用经验，不足之处欢迎大家指正。

### 背景

MongoDB 提供范围广泛的索引类型和功能以及特定于语言的排序顺序，以支持对数据的复杂访问模式。 MongoDB 索引可以按需创建和删除来适应不断变化的应用程序需求和查询模式，并且可以在文档中的任何字段上声明，包括嵌套在数组中的字段。本文介绍一下 MongoDB 中的索引底层结构、索引遍历过程、建索引以及如何使用。

### 基本使用

#### 分类

MongoDB 中的索引与其他数据库系统中的索引类似。 MongoDB 在集合级别定义索引，并支持 MongoDB 集合中文档的任何字段或子字段的索引。 常见的有以下类型： 键索引、复合索引、多键索引、地理空间索引、全文本索引和哈希索引。

#### 创建/删除/隐藏

1. MongoDB 使用 createIndex() 方法来创建索引：

   ```
   `db.collection.createIndex(keys, options)`
   ```

   语法中 Key 值为你要创建的索引字段，1 为指定按升序创建索引，如果你想按降序来创建索引指定为 -1 即可。

   ```
   `db.col.createIndex({"a":1})`
   ```

   createIndex() 方法中你也可以设置使用多个字段创建索引（关系型数据库中称作复合索引）。

   ```
   db.col.createIndex({"a":1,"b":-1})
   ```

2. 删除索引：

   ```
   db.collection.dropIndex
   ```

   删除索引在底层直接删除文件，然后修改元数据

3. 从 4.4 开始支持隐藏索引

   ```
   db.collection.hideIndex(<index>)
   ```

   在删除索引前，可以先隐藏索引，查看集群是否异常后，才真正删除索引， 可有效帮助业务判断索引是否可以删除。

### 数据结构

#### 底层文件存储

MongoDB 底层是如何存储数据的，一个 collection 一个文件吗?索引在底层是如何组织的？ 一个 collection 对应到底层存储引擎就是一个文件，另外每个索引也是单独的文件，每个数据和索引文件的默认结构是 b 树，用户建表的时候也可以指定 lsm 结构，不过绝大多数用户基本都是使用 b 树结构，本文的讨论主要围绕 b 树这种结构来进行。

比如用户建一个普通的表，默认会带一个\_id 索引，会产生俩个文件，一个文件存放数据，一个存放\_id 索引，这俩个文件通过 RecordId 来连接，用户每插入一条数据，mongo 会生成一条与之对应的自增的 RecordId, 不过用户不感知，RecordId 是与 mysql 中的自增主键类似。数据文件是 RecordId 到数据的映射， \_id 索引文件是\_id 到 RecordId 的映射，如果通过指定\_id 查询，会现在\_id 索引文件中找到 RecordId, 然后再到数据文件中查询数据，如果用户再新建索引，那么在 wt 就会再新建一个文件，同样按 b 树组织，该文件记录了索引到 RecordId 的映射，用户使用索引查询时，同样的如同\_id 索引，先找到 RecordId, 然后再到数据文件中查询数据。

```
可以通过以下方式查找数据对应的RecordId  
PRIMARY> db.coll.find().showRecordId()  
{ "_id" : ObjectId("647861f72b531acaacf4afb2"), "a" : 1, "b" : 1, "$recordId" : NumberLong(1) }  
{ "_id" : ObjectId("647861fa2b531acaacf4afb3"), "a" : 1, "b" : 2, "$recordId" : NumberLong(2) }
```

#### 底层格式存储

在 MongoDB 的 Schema-free 架构下，索引字段可以存储不同类型的值，在索引 b 树中，有个基本的问题，实现不同类型的比较呢？ MongoDB 通过 BSON 结构来存储数据，具体结构的解析可见[BSON 结构解析](https://cloud.tencent.com/developer/article/2058958) ，并且规定了不同类型之间的[大小关系](https://www.mongodb.com/docs/v4.0/reference/bson-type-comparison-order/)。

```
1. MinKey (internal type)  
2. Null  
3. Numbers (ints, longs, doubles, decimals)  
4. Symbol, String  
5. Object  
6. Array  
7. BinData  
8. ObjectId  
9. Boolean  
10. Date  
11. Timestamp  
12. Regular Expression  
13. MaxKey (internal type)
```

在这个限制下， 就只需要对比同种类型的大小了，BSON 的基本比较流程如下：先比较类型，如果类型一样才使用 BSONElement::compareElements 比较值。

但是对于索引如果直接使用上述方法去做大小比较，具有以下的俩个缺点：

1. [BSONElement::compareElements](https://github.com/mongodb/mongo/blob/v4.4/src/mongo/bson/bsonelement.cpp#L285) 的性能低，主要是 BSON 结构的序列化和反序列化；
2. BSON 结构是 MongoDB 定义的，对于 wt 引擎层是无法识别。

#### 高效的二进制比较方式-keystring

##### 简介

在 MongoDB 中设计了 [KeyString](https://github.com/mongodb/mongo/blob/master/src/mongo/db/catalog/README.md#keystring) 结构，将所有类型可以归一化为 string， 然后使用 memcmp 进行**二进制比较**。 KeyString 的组成方式为：

```
`字段1类型 +  字段1二进制 + 字段2类型  +  字段2二进制 + ... + <discriminator> + 结尾标识符(0x04) + <recordId>`
```

那 KeyString 是怎么转的呢？类型之间有大小关系，那么 keystring 的前几个字节必定与类型相关，实际上使用第一个字节来存储类型， 相关类型定义如下：

```
const uint8_t kMinKey = 10;  
const uint8_t kUndefined = 15;  
const uint8_t kNullish = 20;  
const uint8_t kNumeric = 30;  
const uint8_t kStringLike = 60;  
const uint8_t kObject = 70;  
const uint8_t kArray = 80;  
const uint8_t kBinData = 90;  
const uint8_t kOID = 100;  
const uint8_t kBool = 110;  
const uint8_t kDate = 120;  
const uint8_t kTimestamp = 130;  
const uint8_t kRegEx = 140;  
const uint8_t kDBRef = 150;  
const uint8_t kCode = 160;  
const uint8_t kCodeWithScope = 170;  
const uint8_t kMaxKey = 240;
```

##### 字符串和数字转换

下面通过常用的字符串以及数字类型来举例说明， 如一条文档{a:"abcd"} ，索引为{a:1}, 生成的 keystring 为：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibkTY3ebrbkmmAnez3eLg0oUDTYEKuNs70UyYyibbOEmYdFJ4oRC6zU48w/640?wx_fmt=other)

各个字段的含义为：

1. 类型为 60，表示 string 类型；
2. 值为 97 98 99 100 0，对应了“abcd”的 ASCII 码， 最后的 0x00 表示字符串类型结束；
3. 整个 keyString 的结束符 kEnd 等于 4。
   方便演示，将类型和值的转换记作 ks， 结束符为 kEnd，即：

   ```
   ks("abcd") + kEnd = 60 97 98 99 100 0 4
   ```

如果一条文档{a:"abcd"， b:"a" } ，索引为{a:1,b:1}, 那么生成的 keystring 为：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibk3cqAzksBBE0hWtvOOdic7gib6wPyXTKyhCIjErS5zvTHpycDAkqBl3qA/640?wx_fmt=other)

再看下整数类型： {a:"NumberInt(1)}， 对应的 KeyString 为：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibkuXMVF6p2CB2X4RdNqlCHEKasPWC6MdFdsR19ExtnY0Xia4NEiaCWAiaNg/640?wx_fmt=other)

与 string 类型相比 43 要比 60 要小， 所以不同类型可以通过第一个字节快速比较大小。 同样的 4 表示结束符， 43 表示类型， 2 表示 value， 这里有俩个问题 1） 为什么不使用类型值不是 kNumeric=30 呢？ 2) value 为什么不是 1， 而是 2 呢？ 带着以上问题，接下来详细分析下最复杂的数值类型转换。

##### 数值类型转换

数字类型比较是最复杂的方法，个整性数可以大端存储然后对比大小，但是涉及到实现整性数和浮点数的比较问题就复杂了。 为了解决上述问题， 按照数字所需要占用字节的大小和正负划分了 22 种数字类型， 如下：

```
const uint8_t kNumericNaN = kNumeric + 0;  
const uint8_t kNumericNegativeLargeMagnitude = kNumeric + 1;  // <= -2**63 including -Inf  
const uint8_t kNumericNegative8ByteInt = kNumeric + 2;  
const uint8_t kNumericNegative7ByteInt = kNumeric + 3;  
const uint8_t kNumericNegative6ByteInt = kNumeric + 4;  
const uint8_t kNumericNegative5ByteInt = kNumeric + 5;  
const uint8_t kNumericNegative4ByteInt = kNumeric + 6;  
const uint8_t kNumericNegative3ByteInt = kNumeric + 7;  
const uint8_t kNumericNegative2ByteInt = kNumeric + 8;  
const uint8_t kNumericNegative1ByteInt = kNumeric + 9;  
const uint8_t kNumericNegativeSmallMagnitude = kNumeric + 10;  // between 0 and -1 exclusive  
const uint8_t kNumericZero = kNumeric + 11;  
const uint8_t kNumericPositiveSmallMagnitude = kNumeric + 12;  // between 0 and 1 exclusive  
const uint8_t kNumericPositive1ByteInt = kNumeric + 13;  
const uint8_t kNumericPositive2ByteInt = kNumeric + 14;  
const uint8_t kNumericPositive3ByteInt = kNumeric + 15;  
const uint8_t kNumericPositive4ByteInt = kNumeric + 16;  
const uint8_t kNumericPositive5ByteInt = kNumeric + 17;  
const uint8_t kNumericPositive6ByteInt = kNumeric + 18;  
const uint8_t kNumericPositive7ByteInt = kNumeric + 19;  
const uint8_t kNumericPositive8ByteInt = kNumeric + 20;  
const uint8_t kNumericPositiveLargeMagnitude = kNumeric + 21;  // >= 2**63 including +Inf
```

那么划分类型的依据是哪些呢？

1. 存储时，只存绝对值，正负是不同的类型， 可以加速判断，负数一定比整数小；
2. 根据数字整数部分所需要占用字节的大小来区分不同类型；
3. 特殊范围的值 大数`大于等于2**63包括+Inf` , `-小于等于2**63包括-Inf`, (0,1.0) ，（-1.0，0）等，
4. 特殊值特殊处理，比如：0、NaN 等；
   总的来说通过数字的不同范围区分了不同的类型， 不仅可以节省空间，一定也能加速大小比较判断，不同字节数的数字只需判断类型即可。

特殊范围的值 这些值只能是浮点数类型这些子类型的 Double 的编码相对容易很多，只需要按照 Double 原有格式稍作处理，然后使用大端模式编码即可；

问题是如何对比存在交集的值，比如整数 1 和浮点数 1.5， 先看下以上俩个值转成 keyString：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibkgD1GmTYnzMDicsKeqq7GPJCnsoZz5jKwngHdN5VgoCszxszFXqOr0tQ/640?wx_fmt=other)

1. 同样的最后的 4 表示结束符；
2. 43 表示了 kNumericPositive1ByteInt 类型，并且需要空出一个 bit 来表示数字是否包含小数部分，如果没有小数部分就将其设置位 0， 有小数部分就将其设置为 1，所以上述提到的{a:1} 对应的值就为 1 左移 1 位再将最后一个 bit 标识为 0，等于 2；{a:1.5}对应的整数值为 1 左移 1 位再将最后一个 bit 标识为 1， 结果就是 3， kNumericPositive1ByteInt 中的 1Byte 表现在一个数的整数左移一位所需要的 byte 数为 1， 如果浮点数没有小数部分最后一个 bit 也要标识为 0；
3. `128 0 0 0 0 0 0` 表示小数部分，表示 0.5，整数部分加小数部分加起来一共 8 位，剩下 7 个 byte 来表示小数部分。

为什么需要用最后一个 1bit 位来表示是否含有小数部分呢？如果没有这个 bit 位， 俩个数整数部分长一样的话，Double 的小数部分要和 Int 后面的结束符 0x4 来比较了，避免比较出现的误差，还能加快比较；double 本身是 8 位， 现在转成 keyString 还是 8 位。虽然上面提到浪费了一个 bit 来表示是否包含小数部分，现在 8 位只表示绝对值了，正负在类型体现了，不会有精度的丢失。对于小数部分为 0 的浮点数， 生成的 keystring 与与之对应的整数一样。

##### keyString 的优点

1. 转换成二进制， 优秀的比较性能；
2. 可以实现不同类型的快速比较；
3. 针对数值类型进行细化，解决了整数类型和浮点数类型转换的兼容性问题， 以及节省存储成本。

##### 在索引中的使用

MongoDB 中使用索引查询数据会有 2 个阶段：

1. **查索引**，通过索引字段的 KeyString 找到对应的 RecordId；
2. **查数据**, 根据 RecordId 找到 BSON 文档；

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibkoK2cQVtibC1ceW0YhjF1KuRrJPcW65JybNarwlbTZ26bBW0LL8vr3qg/640?wx_fmt=other)

(/tencent/api/attachments/s3/url?attachmentid=2948416)

就是说普通索引在底层引擎中索引 b 树中的 key

```
ks(索引field对应的值) + kEnd + RecordId
```

\_id 索引在底层引擎中索引 b 树中的 key

```
ks(索引field对应的值) + kEnd
```

1. **普通索引的 key 包含 RecordId**

非唯一普通索引的 key 包含 RecordId，是因为 WT 引擎中的 Key 是唯一的，但是索引中的 Key 是不唯一的。比如 {a: 1} 索引，很多条 BSON 文档的 "a" 字段都能等于 1，因此在存储索引的时候必须通过方法进行区分。 在 MongoDB 中，由于每个文档都有独立的 RecordId，这样将 RecordId 作为后缀就能保证唯一性。

1. **唯一索引的 key 也包含 RecordId**

普通的唯一索引，上述问题不存在， 但是为什么唯一索引的 key 也包含 RecordId 呢？ 主要是为了解决主从同步的时，从节点的 oplog 并发回放的，回放时的乱序可能会临时打破索引的唯一性质。举个例子，主上依次进行以下三个操作： insert {\_id:1, a:1} remove {\_id:1} 和 insert {\_id:2, a:1}。a 字段为唯一索引， 从上根据\_id 做 hash 然后并发回放时 一个线程回放 insert {\_id:1, a:1}和 remove {\_id:1}，另外一个回放 insert {\_id:2, a:1}。 remove {\_id:1} 和 insert {\_id:2, a:1}的顺序得不到保证，最终可能的一种顺序为： insert {\_id:1, a:1}， insert {\_id:2, a:1}以及 remove {\_id:1}， 对 a 索引进行重复插入了{a:1}， 所以回放时就得暂时不检查 a 索引的唯一性，需要按照上述的方式采用 RecordId 作为后缀。

但是使用 RecordId 后缀方式之后，主节点数据写数据时索引唯一性的检查逻辑会更复杂。

在数据插入前的检测逻辑如下：需要在索引中要插入带 RecordId 的 Key， 格式为： ks1+RecordId。首先会先将 RecordId 后缀去掉，插入 ks1，然后将其 Remove 掉，先插入后删除 KeyString 的操作利用了 wt 引擎乐观锁的特性，构成了写冲突的条件； 假设此时来了另外一个的插入操作， KeyString 相同但是 RecordId 不同，也得需要先插入 ks1， 但是 wt 引擎检查到 KeyString 已经被修改，该操作抛出异常；所以先插入后删除 KeyString 保证了对一个 KeyString 同时只能有一个索引唯一性的检查； 最后就到了实际的重复 key 检查逻辑， 找到第一条大于等于 ks1 的数据， 如果该数据的 key 前缀也正好 ks1，那么索引唯一性检查失败。

\_id 也是（自带的）唯一索引，为啥就能把 RecordId 放在 Value 部分呢？因为 oplog 回放首先会通过 \_id 进行 hash 分桶，然后多个桶之间并发回放。也就是说 \_id 不会存在乱序回放的问题，因此将 RecordId 挡在 Value 部分是没问题的，并且对于唯一索引的插入，没有索引唯一性的检查逻辑，性能也就没有损耗。

### 建立索引

#### 简介

在使用数据库过程中一般的建议是先建好索引，然后再进行业务的操作， 不过也存在一些场景由于前期设计不合理， 在数据量比较大时需要给表增加索引，以 4.0 为例有以下俩种建索引的方式， 前台建索引和后台建索引俩种方式。

#### 前后台建索引

默认情况下，使用前台建索引，不过因为持有 db 的写锁， 将阻塞 db 其他的所有操作。即该 db 上的集合的无法正常读写，直到索引创建完毕。 如果不想影响业务的使用，就需要指定参数{background:1}， 使用后台建索引的方式，但是耗费的时间会更久。

**为什么后台建立索引时间更久呢？** 先看看前台建索引的大致流程，在整个流程中，一直持有 db 的写锁，禁止读写操作， 直到索引建立完成。

> \1) 扫描整个数据文件，按照用户所要求的字段以及 recordid 生成 keystring；
> \2) 将以上生成的 keystring 暂时存到内存中， 如果所占用的内存大小达到了 500MB 或者，就排序后落盘存放在临时文件，如果数据量比较大，磁盘上会有多个 500MB 的文件，文件内 keystring 时有序的；
> \3) 对以上文件进行归并，将结果批量写到索引 b 树中（索引文件底层也是一颗 b 树）。

从以上来看前台建立索引会将数据在文件排好序， 然后**批量写入**到索引 b 树中， 要比后台索引随机写入索引 b 树性能要更高。 **为什么后台建立索引过程中允许写入还能保证索引数据的一致性呢？** 后台建索引的是直接扫描整个数据文件，期间允许读写操作， 按照用户所要求的字段以及 recordid 生成 keystring， 然后插入到索引 b 树中，并且用户的更新/插入/删除操作也会对索引 b 树进行修改。 **如何保证一遍全表扫，一边更新/插入/删除操作，保证最终数据和索引的一致性呢**？可以分成三种情况：

> **情形 1**：更新/插入/删除还没扫到的数据；**情形 2**：更新/插入/删除已经扫到的数据；**情形 3**： 更新/插入/删除和扫数据同时发生。

对**情形 1**， 如后续扫到插入时，会产生 DuplicateKey 错误，直接忽略；对于**情形 2**， 如更新/删除操作，会将之前的建立的索引删除；

**情形 3**比较难处理，需要依赖 wt 底层的事务写重入机制

```
MongoDB引擎层使用乐观锁的机制， 多个事务对同一条文档进行操作时， 其他事务感知到文档被修改后，就抛出写冲突异常，MongoDB捕获的，抛弃当前的引擎层事务， 会重新开启事务.
```

如用户一次 update 操作将{a:1}更新为{a:2}，对应索引 b 树的操作为 remove 了{a:1}，然后 insert 一条 a=2 的数据， 后台建索引线程扫描时 刚好扫到了{a:1}，也会在索引 b 树 insert 一条{a:1} 的数据，预期的最后结果是索引了只剩{a:2}， 以上的操作都在各自的 wt 事务内完成。

虽然是同时操作的，但还是有先后顺序.

1. 后台建索引线程扫描后先插入了{a:1}， 但是还没有提交， 等到用户操作需要 remove 掉{a:1}，就会触发 wt 内部的写冲突后，等待后台建索引线程对应的事务提交后，再来重试，重试时会将 a=1 这条 remove 掉，然后 insert 一条 a=2 的数据, 最终结果就是一条{a:2}.
2. 用户先 update 操作后未提交, remove 了{a:1}时通过, 因为索引 b 树不存在 a=1 这条文档, 然后插入{a:2}, 等后台建索引线程扫描后会插入了{a:1}成功, 触发不了写冲突的逻辑, 最终会剩下{a:2}以及{a:1}俩条数据,这时就会出现数据不一致的情况.

对于上述问题,其实官方早期版本中也存在, 如何进行修复呢? 其实在 remove 掉{a:1}之前, 可以先插入{a:1}, 在引擎中留下{a:1}被修改的记录, 等后台建索引线程扫描后会插入了{a:1}时, 就能救出写冲突, 抛弃当前的引擎层事务, 等用户 update 操作对应的 wt 事务提交后, 再重试时就无法扫描到{a:1}这条数据了, 最后只剩下{a:2}.

#### hybrid 建索引

那么是否有方法能够结合以上俩者的优点呢？速度又快，又不会影响客户端的操作。 从 4.2 开始，默认使用了第三种方式：**hybrid 建索引**

建索引的过程中，如前台建立索引一样， 也会扫描全表， 然后生成多个内部数据有序的临时文件，然后归并排序好批量插入到索引 b 树中，怎么处理在上述过程中的的 更新/插入/删除操作呢？**hybrid 建索引会将上述变更记录下来，然后等批量写入阶段结束后进行回放**，为了保证数据的一致性，最终会在**临界区**再回放一次回放过程中产生的变更，**临界区禁止用户写入**。 所以 hybrid 建索引即拥有前台建索引的速度又如后台建索引不会卡住用户的操作。

**所以 4.0 及以下集群需要使用后台建立索引需要指定{background:1}, hybrid 建索引在 4.2 是默认开启的，用户不需要关心.**

### 索引查询过程

#### IXSCAN 和 FETCH 阶段

在使用索引查询数据时， MongoDB 也使用火山模型， 其实比较常见的俩个阶段 IXSCAN 和 FETCH。 IXSCAN 通过扫描索引 b 树，返回 RecordId； FETCH 得到 RecordId 后从数据 b 树取出对应的 BSON 文档，直接提交给上层， 也有可能根据查询条件的不同，进行过滤后再提交给上层算子。

以用户使用较多的等值查询， 范围查询(和gt(e)等操作符）为例来介绍 MongoDB 是如何通过索引遍历数据来查询的。

#### 操作符 以及gt(e)注意点

在此之前看在无索引的情况下使用以及 gt(e)等操作符的注意点。mongo 只会比较相同的类型。如下所示， 表内有俩条数据

```
restore-test_0:PRIMARY> db.collb.find()  
{ "_id" : ObjectId("647f204a2b531acaacf4afbe"), "a" : true }  
{ "_id" : ObjectId("647f204d2b531acaacf4afbf"), "a" : 1 }
```

执行以下查询语句时， 只能找到 a 字段为数字类型的那条

```
restore-test_0:PRIMARY> db.collb.find({a:{$gte:1}})  
{ "_id" : ObjectId("647f204d2b531acaacf4afbf"), "a" : 1 }  
restore-test_0:PRIMARY> db.collb.find({a:{$lte:1}})  
{ "_id" : ObjectId("647f204d2b531acaacf4afbf"), "a" : 1 }
```

如果业务的字段具有不同类型的值，需要注意这点

#### 遍历之前-区间转换

MongoDB 会将用户的查询语句转化为区间查询。 对于等值查询会将其转化为 start 和 end 相等的左开右开区间， 比如{a:1}, 那么对应的区间为[1.0, 1.0]。 对于范围查询如{a:{$gte:1}}，就将其转换为[1.0, inf.0]， 这里的inf.0表示无穷大的正数， 为什么不是MaxKey呢？，按上面的说明可以理解为MaxKey为无穷大，比任意值都要大。前面说过在无索引遍历的情况下，使用操作符 以及gt(e) 只会比较同类型的数据，同样的索引会选择该类型的最大值作为终止条件。比如对于bool类型来说{a:{$gte:false}}就会转换成[false, true]这个区间。

但是对于一些无最大值的类型，比如 string 类型，{a:{$gte: "1" }}查询条件如何转换成区间呢？ 既然 keystring 可以在不同类型间比较， 那么我们只要取下个类型的最小值即可， 即对应的区间为["1", {})， {}表示 Object 类型，在类型顺序中属于 string 类型的下个类型。

所以虽然转换成 keystring 后，能够实现不同类型的比较， 但是在实际使用范围操作符遍历索引时， MongoDB 内部也会自动加上限制条件，保证只能取同类型数据。下面看下具体如何转换成对应的 KeyString 以及根据转换后的区间遍历过程。

##### 遍历之前-区间 keyString 转换

上文中提到如{a:1}在作为普通索引在存储时， 会转换成以下格式：

```
key: ks(1) + kEnd + RecordId  
value: typeBits
```

那么对应的区间[1.0, inf.0]是如何转换的呢? 首先并不知道 RecordId 对应多少, 那么就不能通过 wt 引擎的等值查询 search 接口直接查到对应的文档，需要使用 wt 引擎的 search\_near 接口定位到第一条大于等于查询 key 的接口, 对应的查询 key 为:

```
key: ks(1) + kEnd
```

如果是左边是开区间的(1.0, inf.0]区间呢?这个时候如何还是使用 key: ks(1) + kEnd 作为查询 key, 有可能查到多的数据， 如果需要 MongoDB 上层再过滤下，不是一个很好的选择。最好的是在编码的时候搞定, MongoDB 实际才使用时在 ks(1) + kEnd 中间添加一个标记为 kExclusiveAfter, kExclusiveAfter 标识位的值位 254, 查询 key 为:

```
key: ks(1) + kExclusiveAfte +  kEnd
```

这样使用引擎的 search\_near 接口(大于等于语义)时,就能跳过{a:1}的数据。 区间的开始和结束都转换成 KeyString 后，并不是直接将开始和结束点的 KeyString 都传给 wt 引擎，而是只传开始的 key，然后 wt 引擎开始遍历，同时 MongoDB 上层对所遍历的 key 进行判断是否在区间内。

查询区间根据所命中的数据在索引 b 树上是否连续可以分为单区间和多区间, 根据查询区间的不同, MongoDB 上层判断是否在区间的方式也不一样。

##### 单区间查询遍历

如果是单区间比如以{a:1, b:1, c:1}为索引, 指定了等值查询如{a:10} 或者{a:10, b:20}等等, 或者单个范围{a: {$lte:10}} 或者{a:10, b: {$lte:10}}等前缀全是等值判断只有最后一项为范围的查询方式，单区间所命中的数据在索引 b 树上是连续的，就能根据区间结束条件生成 KeyString，在遍历过程中由 MongoDB 上层来进行 KeyString 二进制对比， 如果对比发现超范围了，就结束遍历。

单区间遍历比较直观，也比较好理解。如果业务查询条件比较复杂，非单区间遍历，那么 MongoDB 是怎么遍历的呢？

##### 多区间查询遍历

如{a:{$in:[10, 20, 30]}) 以及使用了{a:1, b:1, c:1}，查询时按照{a:10 , c:{$lte:10}}等等相对较复杂的方式，所命中的数据在索引 b 树上不是连续的，MongoDB 就不是通过 KeyString 来判断， 而是每查询一条，都得根据 KeyString 反解生成对应的 BSON 文档， 然后再进行 BSON 比较判断是否在目标区间内， 否则就需要重定位到下一个区间， 当然如果已经在最后一个区间了， 就结束遍历。

下面用一个常见场景来分析下，假设有以下的数据集， 然后索引为{a:1, b:1, c:1}

```
数据集：  
{a:1, b:1, c:1}  
{a:1, b:1, c:2}  
{a:1, b:1, c:3}  
{a:1, b:1, c:4}  
{a:1, b:2, c:5}  
{a:1, b:2, c:1}  
{a:1, b:2, c:2}  
{a:1, b:2, c:3}  
{a:1, b:2, c:4}  
{a:1, b:2, c:5}
```

对于该语句 db.collection.find({a:"1", c:{$lte:1}}).sort({b:1, c:1})必定走索引遍历，不会有内存排序，但是索引数据在 b 树上也不是连续分布的，那么现在的问题是遍历过程中， 是否会将这十条数据全部遍历呢？

在遍历前通过分析，会确定 a、b 和 c 的取值范围, b 没有指定范围，所以时 MinKey 到 MaxKey， c 指定了是比较数字，所以左区间为-inf.0。

```
      "a" :  [ "[1.0, 1.0]"   ],  
      "b" :  [ "[MinKey, MaxKey]"  ],  
      "c" :  [ "[-inf.0, 1.0]"   ]
```

按上面的分析，这是一个多区间查询，遍历过程中会发生重定位的行为， 我们详细来看下遍历的过程： 1) 跳转（seek）到第一条大于等于 {a:1.0, b:MinKey, c:-inf.0}的数据， 即第一条数据， 判断在范围内， 满足要求; 2) 遍历到第二条数据时， 发现 c 字段不在范围内， 不满足要求， 这里会触发跳转的逻辑，不会再判断第三条， 3) 既然当前 a 和 b 是在范围内，跳转的逻辑时找到大于{a:1, b:1}的第一条即可，即跳转到{a:1, b:2, c:1}，满足要求 4) 然后重复上述的逻辑，判断{a:1, b:2, c:3}不符合要求后，需要查找大于{a:1, b:2}的数据, 就直接跳转到最后. 以上查询过程会跳转（seek）三次， 并不会扫描全部索引数据，而是扫描到了 4 条索引数据（keysExamined=4），最后判断有俩条数据时满足要求的。

所以 MongoDB 针对多区间查询的场景， 为了提交查询效率， 中间会穿插跳转（seek）的情况，减少遍历的 key 值。 但是以上述查询为例， \*\*跳转（seek）的次数跟 b 字段的值范围多少有关， 在满足该种查询的情况下, 建议 b 字段的值是枚举类型，值空间是固定，避免出现较多的跳转（seek)\*\*。并且从以上流程可以看到单区间遍历是通过 KeyString 二进制比较来判断终止查询是否终止， 而多区间查询为了能够实现跳转（seek），每次比较需要把 KeyString 反解成 BSON 文档来比较， 效率比 KeyString 二进制略低。

### 使用建议

#### 遵从 ESR 原则

对于复合索引，此经验法则有助于确定索引中字段的顺序： 首先，添加运行 等值 查询的那些字段, 下一个要索引的字段应该反映查询的排序顺序, 最后的字段表示要访问的数据范围。 如{a:1, b:1, c:1} 索引， 按照以上原则设计， 在查询时，就能按索引遍历数据， 避免内存 sort 流程。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibkEWzTbYRfraNNCLicd3JtWtrwn9OdzfYWjsrxHVOJFMV8yoVic9GSzBRw/640?wx_fmt=other)

#### 执行计划确认

explain 是 MongoDB 的查询计划工具，和 MySql 的 explain 功能相同，都是用来分析一条语句的索引使用情况、影响行数、执行时间等。 explain 有三种参数分别对应结果输出的三部分数据：

* **queryPlanner：** MongoDB 运行查询优化器对当前的查询进行评估并选择一个最佳的查询计划。
* **exectionStats：**mongoDB 运行查询优化器对当前的查询进行评估并选择一个最佳的查询计划进行执行。在执行完毕后返回这个最佳执行计划执行完成时的相关统计信息。
* **allPlansExecution：**即按照最佳的执行计划执行以及列出统计信息，如果有多个查询计划，还会列出这些非最佳执行计划部分的统计信息。

建议在一个数据量较大的库上开发功能时，使用 explain 分析一下自己的语句和索引是否合理，避免在项目上线之后出现问题。MongoDB 也是采用火山模型来进行查找， 火山模型是数据库界已经很成熟的解释计算模型，该计算模型将关系代数中每一种操作抽象为一个 Operator，将整个 SQL 构建成一个 Operator 树，从根节点到叶子结点自上而下地递归调用 next() 函数。

常用 stage 解析： COLLSCAN：全表扫， 该阶段会扫描表的全部数据，从数据 b-tree 开始扫描，应当避免该 stage 的出现； IXSCAN：根据分析 sql 生成的索引范围来扫描索引 b-tree，在该 stage 中， 应关注扫描的条数是否合理； SORT\_KEY\_GENERATOR： 根据需要排序的字段生成 keystring，一般与 SORT stage 一起出现； SORT： 内存排序阶段，占用内存，应当设计合适的索引来避免该阶段； FETCH：回表操作，获取到 RecordId 后，在数据 b-tree 中查找对应的文档； PROJECTION： 选择需要返回给的字段。

#### 避免回表

通俗的讲就是，如果索引的列在所需获得的列中（因为索引是根据索引列的值进行排序的，所以索引节点中存在该列中的部分值）或者根据一次索引查询就能获得记录就不需要回表，mongo 默认的查询过程中， 在索引 b 树上找到对应的 RecorId 上， 还需在数据 b 树找对应的文档，然后进行 bson 解析。 实际上如果用户所需要的信息在索引 b 树的 key 内已经包括了，后面的回表操作是多余的，尤其是在大文档的条件下， BSON 解析比较消耗性能。

那么 MongoDB 如何去避免回表呢？

我们可以在 MongoDB 中可以通过使用 project 来选择需要返回的字段，保证所需字段在 project 条件内，特别注意 MongoDB 默认\_id 字段是需要返回的，如果确定不需要\_id 字段，需要**显式的指定\_id 为 0**，可以通过判断 explain 内是否包括 FETCH 阶段来判断是否发生了回表行为。 以某业务 cpu 使用率为例：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/j3gficicyOvatNu5Zia8x00ApI9w2YGzaibkPT5PVT3XbQE6UmH123vB8Gtb01mCJjw9zjaTSbwciarS3GRSutWUDBQ/640?wx_fmt=other)

该业务每条文档都比较大， 业务实际在使用的过程中指定 project 优化后， cpu 性能提升比较明显。

#### 减少索引的使用

在线上的业务中，发现有很多业务存储使用多余索引的情况，

1. 同个表有相同前缀的索引：
   比如{a:1, b:1, c:1} 和 {a:1, b:1} 索引，在这种情况对写入性能会有影响， 每次插入/修改/删除都不可避免的对多余的索引进行操作，这种情况应当及时清理多余的索引；
2. 如果业务刚好需要建立一个唯一索引，那么可以考虑使用\_id 索引，从上面的分析可知，\_id 索引可认为是一个 MongoDB 默认系统自带的索引， 如果用好， 就能减少一个索引。

#### 彻底了解 multiKey

所谓 multikey 是指如果一个字段的值是数组，那么为该字段创建索引时为数组中的每个元素创建一个索引键，这些多键索引支持对数组字段的有效查询。 比如文档{\_id:0, a:[1, 2, 3]}，对应的 RecordId 为 0 ， 对 a 字段建立索引时， 在索引 b 树上会插入三条数据，它们的 key 为：

```
ks(1) + RecordId(0)  
ks(2) + RecordId(0)  
ks(3) + RecordId(0)
```

用户通过{a:1}, {a:2} 以及{a:3}等查询时，都能通过索引找到 recordId 为 0 ，然后找到数据， 这种查询方式比较符合用户的使用习惯。 当然能范围查询如{a:{$lte:3}}，也会走索引，但是这会带来一个问题，在 IXSCAN 阶段三条索引数据都满足要求，那么 IXSCAN 阶段是否会返回三条同样的 RecordId， 接下来的 FETCH 阶段是否查询三次呢？ 实际上对于 multiKey 索引在遍历第一条索引数据时， MongoDB 就有有个 set记录了已经遍历了的 recordId， 当遍历第二条 `ks(2) + RecordId(0)` 以及第三条数据时就可以判断 RecordId(0) 这条 bson 文档已经被遍历过了，不需要将对应的 RecordId 提交给上层的 FETCH 阶段了。

如果对{a:1}字段建唯一索引呢？ 如果我们想继续插入如 {a:[3, 4, 5]} 对应的 RecordId 为 0，是会失败的，由于已经在索引 b 树中插入了三条数据 ks(1) + RecordId(0) 、 ks(2) + RecordId(0)和 ks(3) + RecordId(0)，新插入的 ks(3) + RecordId(1) 与 已插入的 ks(3) + RecordId(0)不同通过唯一性检查，所以这里需要注意唯一 multiKey 索引，是要求数组内的值唯一， 而不是整个数组唯一。

再看下面一个例子,表中有个俩条文档， 以{a:1}建索引

```
{_id:0, a:[1, 4]} => RecorId(0)  
{_id:1, a:[2, 3]} => RecorId(1)
```

先对 a 字段进行排序查询

```
PRIMARY> db.collection.find().sort({a:1})  
{ "_id" : 0, "a" : [ 1, 4 ] }  
{ "_id" : 1, "a" : [ 2, 3 ] }
```

然后逆序查询输出下：

```
PRIMARY> db.collection.find().sort({a:-1})  
{ "_id" : 0, "a" : [ 1, 4 ] }  
{ "_id" : 1, "a" : [ 2, 3 ] }
```

居然顺序和逆序查询结果是一样的！！！按照我们上述分析的可以仔细分析出来， 这个俩条文档需要在索引 b 树中生成 4 个 kv 对，他们的 k 如下：

```
ks(1) + Record(0)  
ks(2) + Record(1)  
ks(3) + Record(1)  
ks(4) + Record(0)
```

我们执行的查询语句会走索引，所以不管是顺序还是逆序都会先查询到 RecordId 为 0 的那条。

#### 空字段的索引

“我们的表很大，现在需要对一个不存在的字段建索引，速度会不会快很多?”，我们在线上的运营过程中遇到过以上疑问，因为建索引可以简化成俩个步骤：扫表和往索引 b 树插入数据。扫表是避免不了的，但是对应的字段为空，是不是就不会往索引 b 树中插入数据了呢？

首先我们可以看下如果索引字段为空，对应的索引 b 树中也没有对应的记录会有什么后果。用户常使用 操作符来判断字段是否存在，如果索引树中也没有对应的对的话，那么exists 操作符在查询是就不能走索引了，只能通过全表扫描的方式，这样的效率是不能接受的。

索引 b 树中需要特殊标识下字段为空的情况， 实际上在建立索引时如果字段为空， 就会认为该字段的类型为特殊的 null 类型（前文中已经提到过），db.collection.find({a:{$exists:false}})，对应的查询区间为[null, null]。所以对于开头的问题，对一个不存在的字段建索引，速度并不会快。

```
可以通过稀疏索引(或者称间隙索引)就是只包含有索引字段的文档的条目，即使索引字段包含一个空值。也就是说间隙索引可以跳过那些索引键不存在的文档。
```

#### 慢日志分析

```
{  
    "timestamp": "Thu Apr  2 07:51:50.985" ,  
    "severityLevel": "I"  
    "components": "COMMAND"  
    "namespace": "animal.MongoUser_58"  
    "operation": "find"  
    "command": { find: "MongoUser_58", filter: { $and: [ { lld: { $gte: 18351 } }, { fc: { $lt: 120 } }, { _id: { $nin: [1244093274 ] } }, { $or: [ { rc: { $exists: false } }, { rc: { $lte: 1835400100 } } ] }, { lv: { $gte: 69 } }, { lv: { $lte: 99 } }, { cc: { $in: [ 440512, 440513, 440514, 440500, 440515, 440511, 440523, 440507 ] } } ] }, limit: 30 } //具体的操作命令细节  
    "planSummary": "IXSCAN { lv: -1 }", // 命令执行计划的简要说明，当前使用了 lv 这个字段的索引。如果是全表扫描，则是COLLSCAN  
    "keysExamined": 20856, // 该项表明为了找出最终结果MongoDB搜索了索引中的多少个key  
    "docsExamined": 20856, // 该项表明为了找出最终结果MongoDB搜索了多少个文档  
    "cursorExhausted": 1, // 该项表明本次查询中游标耗尽的次数  
    "keyUpdates":0,  
    "writeConflicts":0, // 写冲突发生的数量，例如update一个正在被别的update操作的文档  
    "numYields":6801, //  
    "nreturned":0, //  
    "reslen":110, //  
    "locks": { // 在  
        Global: { acquireCount: { r: 13604 } },  
        Database: { acquireCount: { r: 6802 } },  
        Collection: { acquireCount: { r: 6802 } }  
    },  
    "protocol": "op_command",  
    "millis" : 69132, // 从 MongoDB 操作开始到结束耗费的时间，单位为ms  
}
```

与索引相关的重要字段：

1. planSummary: 命令执行计划的简要说明，当前使用了 lv 这个字段的索引，如果是全表扫描，则是 COLLSCAN，则需要重点注意了，是否设计不合理；
2. keysExamined: 该项表明为了找出最终结果 MongoDB 搜索了索引 b 树中的多少个 key；
3. docsExamined: , 该项表明为了找出最终结果 MongoDB 搜索了多少个文档， 就是根据 RecordId 往数据 b 树中查询了多少次；
4. nreturned: 该操作最终返回文档的数量。

**近期好文**

[**每个程序员都应该了解的硬件知识**](http://mp.weixin.qq.com/s?__biz=MjM5ODYwMjI2MA==&mid=2649783116&idx=1&sn=c9ac909295a595759431ed5f93093ba9&chksm=becce83789bb6121102d2a621a425c7aac933f3221f1cf31b7c86f02c24e8c4d714a73d99fa2&scene=21#wechat_redirect)

**腾讯程序员视频号直播**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvauaWA1mKBnBBjkH9JfOqthOZtto0ea1dOxIGmml7cGhHPDdMuYqsvPDvicCd9hEEccFGWljjxRHVNQ/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/j3gficicyOvasOHYuGEic5USJwXGgWfxiaIXz2uxcnbFsTuYvRdoias1ajkEa7Qd81r31CJCMQ8OK6YfMYjw2OXz3EA/640?wx_fmt=gif)