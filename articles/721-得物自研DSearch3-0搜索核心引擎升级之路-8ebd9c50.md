---
title: '得物自研DSearch3.0搜索核心引擎升级之路'
company: 得物
tag: 工程相关
date: 2025-05-14
url: https://juejin.cn/post/7503854158718992393
account: 
origin: harvest-202607
---
# 得物自研DSearch3.0搜索核心引擎升级之路

[得物技术](/user/2392954206960247/posts)

2025-05-14
  
341
 
阅读14分钟

   

## 一、背景

随着交易和社区搜索业务稳步快跑，基建侧引擎越来越复杂，之前搜索底层索引查询结构已经存在较为严重的性能瓶颈。成本和运维难度越来越高。在开发效率上和引擎的稳定性上，也暴露出了很多需要解决的运维稳定性和开发效率短板。而在引擎的业务层部分也需要逐步升级，来解决当前引擎中召回层和业务层中各个模块强耦合，难维护，迭代效率低下等问题。

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/73458d86dbb44d15bf8f3babf2116986~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=eAaFYWzKuuJBS3KZE3xWO8IxBlw%3D)

## **二、引擎开发技术方案**

### **DSearch1.0索引层整体结构**

DSearch1.0的索引结构比较特殊一些，总体上使用了全局rcu的设计思想，整体架构上单写多读，所以实现了并发高性能无锁读，内部数据结构都是无锁数据结构，所以查询性能高。在写操作上因为rcu**机制实现写入无锁。整体上优点读性能高，没有传统段合并操作带来的磁盘抖动。缺点是索引地址和操作系统强相关，运维复杂，热更新**受限。全局地址分配难以并行写入，构建瓶颈明显。无法对浪费的内存进行回收导致内存空间利用率低，索引空间占用大。总体结构如图所示：

![图片](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/4d5f99996bac43559d2810ce214dcf84~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=CrHYmDFMfcbmKPMAq%2FyxSbgGzqk%3D)

### **DSearch2.0的索引升级**

**DSearch2.0分段索引整体设计**

引擎2.0索引升级采用经典段合并架构，除了继承了段合并中优异的高性能写入性能和查询已经索引合并等优势外，针对段合并中频繁的正排字段更新等带来的高IO缺点。我们设计了新的正排字段原地更新索引，使新的DSearch2.0引擎拥有Redis的高性能写入和查询，也拥有lucene的紧凑索引和索引合并带来的内存空间节省的优势。

**※ 索引段结构**

1. 每个索引段包含了文档文件，用于紧凑存放document中的各个字段的详细信息。字符串池文件是对document中所有的字符串进行统一顺序存储，同时**对字符串进行ID化**，每个字符串ID就是对应于字符串池中的**offset偏移**。
2. 可变数组文件是专门存放数组类型的数据，紧凑型连续存放，当字段更新的时候采用文件追加append进行写。最终内存回收通过段**之间的compaction进行**。FST索引文件是专门存放document中全部字符串索引。每个fst的node节点存放了该字符串在字符串池中的偏移offset。而通过字符串的offset，能够快速在倒排termoffset数组上二分查找定位到term的倒排链。
3. 倒排文件是专门存放倒排docid，词频信息、位置信息等倒排信息，其中docid倒排链数据结构会根据生成段的时候计算docid和总doc数的密度来做具体判断，**如果密度高于一定阈值就会使用bitmap数据结构，如果小于一定阈值会使用array的数据结构**。
4. 标记删除delete链主要是用于记录段中被删除的document，删除操作是软删除，在最后查询逻辑操作的时候进行最后的过滤。
5. 实时增量的trie树结构，实时增量段中的前缀检索和静态段中的前缀检索数据结构不一样，trie因为能够进行实时更新所以在内存中使用trie树。
6. 段中的metadata文件，metadata文件是记录每个段中的核心数据的地方，主要记录段内doc数量，段内delete文档比例，实时段的metadata会记录kafka的offset等核心数据。

![微信图片_2025-05-14_105656_384.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/9e558c5542c94ae090a445d25767db1e~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=ocbe9XrqHIWu6PtkoRav5az5kBY%3D)

**Document文档和索引结构**

**※** **Document文档数据结构**

1. Document文档使用紧凑型存储，其中array和字符串类型单独存放，其他字段连续存放，string和array字段存放。
2. array字段类型数据直接存放在可变数组文件区，连续追加写。
3. string字符串池对所有字符串进行连续存放，多个doc中同一个字符串引用同一个字符串地址，节省大量字符串存放空间。

**※** **倒排索引文件结构**

1. 倒排索引文件存放docid倒排和Tf以及位置position数据。其中内存实时段中的倒排索引数据结构是固定一种类型array类型。而内存实时段固化为静态段的时候，倒排数据结构会根据docid中的密度进行选择array和bitmap存储。当docid密度大于一定阈值是bitmap，反之是array结构。
2. Tf数据结构是一个uint16的数组，数组长度和docid的数组长度一致，所以当确定了某个docid时候，也随即确定了它的tf信息。
3. postion信息存储是一个二维数组的格式，第一层数组存放的是对应于term的在字符串池的offset，因为term在字符串池中已经ID化，所以offset可以表示唯一term。第二层数组是该term在字段中多次出现的位置，使用uint16存储。

**※** **前缀检索文件**

1. FST静态段文件

   a. 静态段中前缀是fst的数据结构，因为fst一旦建立是不能够进行修改的，所以在段合并的时候需要对所有term进行排序然后再构建fst结构。

   b. fst的node节点存放了对应于term的字符串池的offset。当需要查询一个term的倒排结构时候，需要先查询该term的字符串池的offset，然后拿该offset去倒排的termoffset文件中二分查找找到对应的倒排positionlist结构拿到对应倒排。所以一次term到倒排的查询需要查询一次fst+一次二分查询。

   c. term到倒排的查询一次fst+一次二分查找效率不高，所以针对term到倒排查询，新增了第二种HashMap索引，直接通过term到倒排的offset索引，这个选项在建表的时候可以配置。
2. 实时段RcuTrie树索引

   a. 实时段中需要支持边写边读，前缀检索需要支持并发读写。引擎中trie树是rcu实现，单线程更新，多线程并发读，trie树写更新节点内存延迟回收。

![微信图片_2025-05-14_105704_249.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/1410cb836b2f4ceb9de2edee87c757e5~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=IOEfMwD9fsVfR7pKAdUXkaWiWP0%3D)

**倒排索引和查询树逻辑**

**※** **倒排链优化**

1. DSearch1.0的roaringbimap倒排索引在低密度数据量上存在一些瓶颈，比如对于倒排链比较短的情况下，roaringbitmap的container大部分都是array结构，在倒排链查询和合并都会进行一次二分查找，在大面积的倒排链合并中是个相当大的性能瓶颈。
2. 针对上面所说的情况对roaringbitmap进行了精简，只存array或者bitmap合并的时候不需要查找，直接链式合并。

**※** **逻辑树合并优化**

1. DSearch2.0重点从逻辑语法树和倒排入手，优化语法树，减少合并树高，从二叉树合并变成单层合并。
2. 优化倒排链合并方式，采用原地倒排链合并，消除倒排合并临时对象，同时引入多线程并行合并，减少长尾提高性能。

![微信图片_2025-05-14_105712_581.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/a5515e01fda74edd84c07e64fc9290d2~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=KxW8dMDn1Y3UYjwHtXfh7IdP1qQ%3D)

**增量更新逻辑**

**※** **增量实时写入逻辑**

1. 引擎支持多个并发实时段，这个由配置文件通过配置来进行配置。多个实时段能够提升并发写入的性能。
2. 每个实时段对应一个写入队列，提高并发写入吞吐。
3. 每个段真实写入一条信息会同步原子更新消费的kafka的offset，用于对后面进程重启等恢复数据做准备。
4. 当进程重启或者异常退出时候，会读取metadata文件中的最后一条kafka offset进行重新消费增量在内存中重新构建新的正排、文档和倒排等信息，完成数据的恢复。

![微信图片_2025-05-14_105722_614.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/63e431f843a94c93938cb09db378a820~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=%2BwrMYkUj%2FqNs5J9u8pvw%2FmYE%2Ft4%3D)

**实时段固化和段合并策略**

**※** **实时段固化逻辑：**

1. 当实时段内随着增量写，doc文件大小超过128M时候会进行内存实时段固化操作。
2. 固化操作开始时，会先生成新的内存实时段，老的内存实时段会变成只读内存段。
3. 遍历按整个只读内存段，构建新的索引和新的正排结构生成新的静态段。

**※** **段合并策略：**

1. 实时段固化的小静态段因为大小比较小，会优先和之前固化后的小段进行合并，按照1，2，4，8进行合并，逐步合并成静态段最大的上限。
2. 静态段的合并触发策略是当静态段中delete的doc比例超过了30%会触发静态段之间的合并，合并会按照近邻合并原则，从左右近邻中选取一个最小doc数的段进行合并，进而新生成一个新的段。

![微信图片_2025-05-14_105730_298.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/a90922bda40b4401a8b07ca54d371a07~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=thG885cV0MoSla0QKLB4SUdECCs%3D)

**查询和更新中的并发控制**

**※** **查询流程**

引擎查询时候，先遍历查询实时段，然后再查询静态段。实时段查询存在最大增量查询截断，当实时段查询到最大增量截断时实时段停止查询。

实时段查询后，查询静态段。静态段中包含了全量构建索引的全量最大offset记录同时全量的doc是通过质量分进行排序，所以在全量段查询的时候，先遍历质量分最大的全量段，逐步往后面静态段查询，直到查询到全量截断。

实时段查询和静态段查询结果进行merge作为最终的查询结果。

**※** **更新并发控制**

因为DSearch2.0的索引更新是直接在实时段或者静态段进行更新，所以存在多线程读写问题。尤其是正排字段更新写入量大更新频繁。同时更新涉及到所有的实时段和静态段，较为复杂。

为了解决正排字段和倒排的更新问题，新版本引擎引入了document文档锁池，对每个doc进行hash计算落到锁池中具体一个锁上来减少锁冲突，当前锁池内有多个个文档锁。文档锁在文档进行拷贝和更新的时候会进行锁住。

### **DSearch3.0搜索核心升级**

**异步非阻塞图调度框架**

![微信图片_2025-05-14_105739_148.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/29b3be8ab8d64b6ca5c5760d76480e3f~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=aFbDaUHM1J0EGaMMI7x2yh%2BnZy8%3D)

**※** **引擎主要改造：**

1. **图框架支持RPC**异步非阻塞请求：引擎图框架RpcServer服务使用brpc的异步处理无需同步阻塞等待调度完成，只需框架调度完算子返回结果，不阻塞RpcServer线程，例如：当前引擎调用neuron服务是同步调用，当neuron服务负载高阻塞时，同步调用会导致拖住引擎RpcServer处理线程，新的异步非阻塞模式引擎client在调用引擎后已经返回，等待引擎RpcServer中异步调度框架中remote异步算子回调，减少外部服务影响引擎。
2. **减少线程切换：** 图框架调度器会优先调度当前运行线程，同时使用M:N类型的bthread线程池，线程切换会更小，执行效率高。
3. **RPC服务和框架算子独立：** 引擎RPC服务和框架算子完全解耦，跨集群部署算子服务无需任何改造，实现算子脱离运行环境。
4. **高效的算子异常处理和超时机制：** 每个算子维护自己的运行超时时间和请求到算子调度执行的超时时间，对整个请求流程中各算子执行更加精准。
5. **动态图支持：** 图框架支持静态图和动态图业务组合式调用。支持静态子图和动态子图调用等复杂业务组合。
6. **复杂子图支持：** 图框架支持嵌套子图，支持自调用模型，可以实现复杂单节点多功能调用。

**算子间数据交换Table设计**

![微信图片_2025-05-14_105745_282.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/49653fc936f5436fb16d26ddd9148e91~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=3HxhVIbTWmm%2BQ1Jz98VS8QpQdMM%3D)

**※** **引擎主要改造：**

1. **列式数据共享优化：** 算子交换数据全部存放在Table列中，Table中全部共享列式数据，省去大面积数据拷贝，大幅提升引擎业务执行性能。
2. **兼容引擎索引中doc数据：** 引擎索引中doc行式存储有很多优点，比如多字段访问效率高等，Table设计中考虑了行式存储优点，不仅存高频的列字段也储存了引擎内部的doc*以及对应FieldDef*，能直接方便访问索引数据，接口统一，易于迭代。
3. **打通FlatBuffer序列化协议：** 当前引擎FlatBuffer序列化传输协议和引擎内部数据出口需要多次遍历转换，需要拷贝很多数据，新Table的设计内部数据列和FlatBuffer内部的数据列互转互通，节省大量内部拷贝同时避免了字段兼容等问题。
4. **支持原地排序和标记删除：** Table数据表，支持原地sort操作和标记删除操作，节省数据排序时大量数据的拷贝和删除操作中导致的数据重排等拷贝操作，提升性能。

**算子间数据交换Table设计**

![微信图片_2025-05-14_105752_514.png](https://p9-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/532380cac2d14f56acb10b7997ec5619~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785296154&x-signature=XTWrvOofrIdcFJOtentXO%2BMC4Ic%3D)

**※** **引擎主要改造：**

1. **动态图支持：** DSsearch3.0支持动态图编排，主要通过业务方通过动态编排请求来组织对应的算子编排逻辑，实现业务方自主编排调度逻辑，方便整体业务开发。
2. **Remote远程调用支持：** 通过开发远程异步调用算子，支持DSearch3.0跨集群调用，实现多机算子化互联互通。提高引擎的整体纵向拓展能力。
3. **引擎算子库复用：** 通过设计统一的算子接口，开发基础的可复用框架算子，支持配置化组合运行图，实现业务逻辑快速复用和开发，提高整体引擎开发效率。

## **三、性能和效果提升**

DSearch在2024年Q1季度索引升级开发完成后逐步推全到交易和社区等各个主场景业务中，最后拿到了很多超预期结果：

**索引内存优化超出预期：** 社区搜索和交易搜索总索引单分片优化60%。

**构建和写入性能优化超出预期：** 社区搜索和交易搜索主表写入性能提升10倍。

**索引更新优化超预期：** 社区和交易主表更新时间提升接近10倍。

**性能优化符合预期：** 社区搜索平均rt降低一倍，P99晚高峰降低2倍。

## **四、总结**

DSearch引擎从开始的DSearch1.0的搜索引擎逐步经历了DSearch2.0的分段式索引改造升级，又经历了DSearch3.0的全图化引擎升级。逐步将DSearch引擎升级到业界较为领先的支持内存型、磁盘型多段式搜索引擎，为支持得物业务的发展做出了重要的贡献，后续DSearch会围绕着通用化、自迭代、高性能等多个方向继续升级，将DSearch引擎迭代到业界领先的引擎。

算法团队大量HC，欢迎加入我们：[得物技术大量算法岗位多地上线，“职”等你来！](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzkxNTE3ODU0NA%3D%3D%26mid%3D2247537831%26idx%3D1%26sn%3Ddb1464cd87a75dd8f7bcf512fb50bf70%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247537831&idx=1&sn=db1464cd87a75dd8f7bcf512fb50bf70&scene=21#wechat_redirect")

**往期回顾**

1. [以细节诠释专业，用成长定义价值——对话@孟同学 ｜得物技术](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzkxNTE3ODU0NA%3D%3D%26mid%3D2247539238%26idx%3D1%26sn%3D4fcfbfecbafe02c10172b7832416465c%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247539238&idx=1&sn=4fcfbfecbafe02c10172b7832416465c&scene=21#wechat_redirect")

2. [最近爆火的MCP究竟有多大魅力？MCP开发初体验｜得物技术](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzkxNTE3ODU0NA%3D%3D%26mid%3D2247539225%26idx%3D1%26sn%3D811dee1e2b17f5b1249d14f19b69f171%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247539225&idx=1&sn=811dee1e2b17f5b1249d14f19b69f171&scene=21#wechat_redirect")

3. [得物可观测平台架构升级：基于GreptimeDB的全新监控体系实践](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzkxNTE3ODU0NA%3D%3D%26mid%3D2247539175%26idx%3D1%26sn%3D6dc5659dc94a0bc356dddf69df69a83b%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247539175&idx=1&sn=6dc5659dc94a0bc356dddf69df69a83b&scene=21#wechat_redirect")

4. [得物自研DGraph4.0推荐核心引擎升级之路](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzkxNTE3ODU0NA%3D%3D%26mid%3D2247539014%26idx%3D1%26sn%3D90a168b730490ae84a0917863ad3e077%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247539014&idx=1&sn=90a168b730490ae84a0917863ad3e077&scene=21#wechat_redirect")

5. [大语言模型的训练后量化算法综述 | 得物技术](https://link.juejin.cn?target=https%3A%2F%2Fmp.weixin.qq.com%2Fs%3F__biz%3DMzkxNTE3ODU0NA%3D%3D%26mid%3D2247538986%26idx%3D1%26sn%3Db6b82a790a3c696bce27704472e799b2%26scene%3D21%23wechat_redirect "https://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247538986&idx=1&sn=b6b82a790a3c696bce27704472e799b2&scene=21#wechat_redirect")

文 / 苏黎

关注得物技术，每周更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。