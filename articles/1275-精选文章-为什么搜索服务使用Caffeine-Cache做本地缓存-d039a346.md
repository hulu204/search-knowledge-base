---
title: '精选文章｜为什么搜索服务使用Caffeine Cache做本地缓存'
company: 得物
tag: 搜索
date: 2021-03-28
url: http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247485337&idx=1&sn=fd66de3421005c42713446e6dfd441e4&chksm=c16252c6f615dbd0efb22c4d35418a07487a31c5f51e34a16f2c6078d4319d2e23fd34a15c46#rd
account: 得物技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAeHU0Uckn6YaDST9SJ0Xk3HW5cyEPIh4KWrSZScO50I0iaicibKRibWs7Uxw/640?wx_fmt=jpeg)

**Caffeine Cache**

搜索服务

本地缓存

**〇、何时使用本地缓存？**

Redis、Memcached 等分布式内存缓存能够显著提高服务性能与可用性，不仅检索数据比硬盘存储的数据库更快，也很容易随流量做线性扩容。

尽管存在这些优势，仍然有一个关键问题没有解决：分布式缓存往往部署在专属的服务器集群上，应用的每次访问都需要至少一次跨越网络的请求。

本地缓存将数据存储在服务本地内存中，解决了使用缓存必须进行一次网络IO的缺点，但其本身也存在一定的局限性。

在本篇初始，先看一下本地缓存与分布式缓存各自的优势与缺陷。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAer221LDKiaic3kLTMYWd9eycnnbLua8JQcbsUTc5chgfkaY5S6FSBd4IQ/640?wx_fmt=png)

**一、搜索服务本地缓存**

搜索服务中，有大量数据会被几乎每一次请求访问，比如用户画像、商品信息、社区动态信息、倒排池等，这些数据的共同特点是对一致性容忍度较高，且大多有明显的热点。

为了更小RT与更高可用性，搜索服务大量使用了本地缓存做这些数据的一级缓存，Redis 与 ElasticSearch 作为二级缓存。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAerFVzAic5N7RJichDUg8m3NZpn7uBhJ5Hia2Oiafr2B1NOrhXkEYnReicbAQ/640?wx_fmt=png)

* 服务启动时，将频繁使用的数据提前加载至内存中，这部分内存不会过期且异步定时更新，减小缓存雪崩风险。
* 搜索服务上游发起的请求，根据 UID 做一致性哈希，保证相同用户的每次请求都被转发到相同的节点上，避免用户画像缓存的冗余。
* 异步更新被访问的一级缓存，使用独立的流处理服务更新二级缓存。

  在用户请求过程中几乎不访问磁盘数据库，也不同步等待缓存写入，性能提升的同时避免缓存击穿。
* 提供可以强制刷新本地缓存的 API，收到请求的节点通过Redis发布订阅模式通知到所有其他节点，作为数据一致性的兜底。

**二、Caffeine Cache**

最简单的本地缓存其实可以使用 ConcurrentHashMap，但要支持更多功能比如逐出策略、过期策略、异步更新等就比较困难。

SpringBoot 1.x 版本使用了 Guava Cache 做默认的本地缓存实现，提供了很方便的 API。

自 SpringBoot 2.x 版本开始，Guava Cache 被 “来自未来的缓存” Caffine Cache 取代。

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAe8FUk7Xn65DFlcfJcMZEo4wHYoKjxmvVpjSVxxEOka4oDeHeOGj4BIw/640?wx_fmt=jpeg)

从压测结果看，Caffeine 的并发读写效率完爆 Guava Cache，是当之无愧本地缓存之王。

关于 Caffine Cache 的 API 使用，网上的资料很多而且与 Guava Cache 很像，所以本文将重点放在其高性能的实现原理上。

幸运的是，在Github 仓库可以找到 Caffeine 开发者自撰写的设计思想，它将一个看似简单的本地缓存功能优化推向了另一个高度，甚至形成了一套方法论，对于任何复杂的工程实现都有启发意义。

**三、经典的 LRU、LFU**

衡量缓存淘汰算法之标准一是命中率、二是内存开销。

其中最经典的莫过于 LRU，它使用一个链表为缓存排序，每次对数据进行访问时，将数据移动至队尾，队列已满时淘汰队首。

LRU 的实现成本极低，不足之处在于它对热点数据的判断不稳定 —— 如果某热点数据在很长一段时间内都被频繁访问，仍有可能因为短时间内没有被访问而被快速淘汰。

对此又出现了 LFU 算法，它使用额外的内存记录每条缓存的使用频率，淘汰频率最低的缓存。

在访问模式比较稳定的情况下，LFU 缓存命中率比 LRU 要好，但它有三个明显的缺陷：

* 需要额外存储大量频率信息。
* 每次访问缓存都需要更新频率，并发性能低下。
* 如果访问模式出现变化，比如一个热点数据迅速冷却，也会因之前的高频率记录而难以被淘汰。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAew6qfvgKhux2MibdnN0ATNSFxPSOf0NZ3aubmIxQxK3b7c7jAC7KaSEg/640?wx_fmt=png)

如果在工程中基于这些算法实现本地缓存，还有很多问题需要解决，比如并发性能、自动过期、定时刷新功能以及如何在资源消耗和命中率中找到平衡点。

对此，Google 开源的 Guava Cache 本地缓存库对 LRU 算法进行了加强与封装，并通过分段加锁以图提高并发能力。

但是今天的主角并不是Guava Cache，而是青出于蓝的 **Caffiene Cache**。

**四、缓存字典**

“缓存字典” 即用来存储缓存数据本身的哈希表。

不同于 Guava Cache 自己实现了一个基于分段锁的功能复杂的哈希表，Caffeine 的 “缓存字典” 是对 JDK 自带 ConcurrentHashMap 的简单封装，因为其面向的 JDK8 将 HashMap 的锁粒度缩小至元素级别，并增加了红黑树来应对哈希冲突，已经有足够好的读写性能。

保持缓存字典的实现简洁（与其他高级功能分离），可以更好地发挥出 JDK8 中 HashMap 的优势，因为功能越多，导致锁粒度增大的风险就越高。

**五、频率统计**

上文提到，LFU 需要消耗很多内存资源来记录缓存访问频率。

一种容易想到的方法是使用布隆过滤器进行优化，多个缓存数据共用一个 key，对应的 value 记录这些缓存数据的总体使用频率。

以搜索服务中缓存量最大的用户画像为例：

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAe20fe5QSN3RNU6CLZaVSvicR7rsnksj5sBMgYBJnMdn3a905wBMgZyHw/640?wx_fmt=png)

理想情况下，用户A和用户B只占用数组中的一个元素，节省内存空间的同时也实现了热点数据标识。

但是对于用户D，由于他的哈希值与热点用户C重合，尽管只有一次访问，依然被作为热点数据长时间保留在内存中。

为了进一步解决问题，Caffeine Cache 使用了 Count-Min Sketch 来记录缓存使用频率，本质上是布隆过滤器的一个变种。

如果将上图的数组改为二维，每条缓存使用多种哈希算法计算哈希值作为key，最后取每个哈希值对应value的最小值，就可以极大地避免冷热数据撞key的情况。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAefj2EXA9CvyYOaH5XZmSYub8lURKbYqhmHmMa0CCe7UY0v7Lw1IQHdw/640?wx_fmt=png)

上图中，用户C被搜索的次数 min(1000, 999, 999) = 999；用户D被搜索的次数 min(1000, 1, 1) = 1。

通过改变二维数组的宽度和深度，可以在空间、性能、统计正确率之间进行权衡调整。

Caffeine 没有直接存储缓存被访问的总次数，毕竟我们只是对比缓存的使用频率，不需要准确地统计使用次数。

```
int maximum = (int) Math.min(maximumSize, Integer.MAX_VALUE >>> 1);table = new long[(maximum == 0) ? 1 : ceilingNextPowerOfTwo(maximum)];
```

通过 Caffeine 初始化 Count-Min Sketch 的源码可以看到，它创建了一个 long 类型的一维数组，数组长度是 “大于但最接近需要保留的缓存数量” 的2的n次方，这个数组就用来记录缓存使用频率。

Java 中 long 类型的长度是 64 位，Caffeine 使用每 4 位记录一个频率，四位二进制最大值1111等于15。也就是说，热点数据的频率，更准确地说是热度分，最高记为 15，最多可以使用 64/4 = 16 种哈希算法（实际使用了4种）。

假如每种哈希算法冲突的概率是10%，那么四种算法同时冲突的概率仅有 0.01%。

对于已冷却的热点数据可能长时间滞留内存的问题，Caffeine 中存在一个线程周期性地将所有缓存热度分减半。这样的设置可以在几乎不影响命中率的情况下实现内存开销可控。

**六、淘汰策略**

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAeRZy3ldCnVC6gcLfKldVX1FVYl8RNLbVptytQdxEgOMRpzzicv2B1ocw/640?wx_fmt=png)

HighScalability 网站刊登了一篇文章，前 Google 工程师提出的 W-TinyLFU 淘汰策略，为缓存提供了一个 “近乎最佳的命中率”。

Caffine Cache 的淘汰策略就是基于 W-TinyLFU 而开发，其整体分为三个部分：一个 Admission 窗口、一个 TinyLFU（即 Count-Min Sketch）、以及一个主区域。

Admission 窗口是一个 LRU 队列，长度大约是最大缓存长度的 1%，新缓存数据会首先进入 Admission 窗口。

它的存在使得一些新来的但是大概率不会再被使用的缓存数据可以被快速淘汰，也为那些有潜力成为热点的缓存提供一个保护期。

W-TinyLFU 的主区域是一个 LRU 队列，并被分为一个较大的 Protected 区和一个较小的 Probation 区。

Admission 窗口满了以后，被 LRU 算法淘汰的数据会进入 Probation 区。

主区域整体就像一个 LRU 队列正常工作，任何在 Probation 区被访问的缓存会立刻进入 Protected 区，被 Protected 区淘汰的数据会进入 Probation 区。

随着数据越来越多，最终缓存会从 Probation 区被淘汰。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAegL4Hib1PB7ApaqaXS19ianzty98hYWVJTO4pRm4TegB5E6Ydp3qWy6Dw/640?wx_fmt=png)

上图展示了缓存数据在 Caffeine 中流转和淘汰的过程，其中 Count-Min Sketch 的作用发生在红色的 “删除” 步骤之前。

当一条缓存即将被逐出 Probation 窗口时，会比较 Probation 队首元素（victimKey/受害者）和队尾元素（candidateKey/备选者/尝试将受害者逐出的缓存）在 Count-Min Sketch 中的热度分。

如果备选者热度分大于受害者，则淘汰受害者；如果备选者热度分不高于5，则淘汰备选者；否则随机淘汰一个缓存。

这样做的意图是为备选者设置一个热度分门槛，让“接纳一条缓存”不那么随意，降低对命中率的不利影响。

附上这部分操作的源码：

```
boolean admit(K candidateKey, K victimKey) {  int victimFreq = frequencySketch().frequency(victimKey);  int candidateFreq = frequencySketch().frequency(candidateKey);  if (candidateFreq > victimFreq) {    return true;  } else if (candidateFreq <= 5) {    return false;  }  int random = ThreadLocalRandom.current().nextInt();  return ((random & 127) == 0);}
```

**七、并发读写**

到目前为止所提到的优化，目的都是降低资源占用以及提高缓存命中率，而 Caffeine Cache 最大的优势是高并发下的读写速度。

多线程使用缓存的最大困难在于，读写操作都需要修改共享的状态（读操作需要更新多个 LRU 队列和 Count-Min Sketch）。

一种常规的解决方案就是采用分段锁。不幸的是，缓存的访问往往集中在某些热点数据上，分段锁能取得的性能提升十分有限。

如果锁竞争频繁，但每次拿到锁后只做很少的事情，或许可以攒起来一起做？

Caffeine 的解决思路借鉴了传统的数据库理论，把所有操作记入提交日志，稍后通过异步任务批量执行。

Caffeine Cache 使用的 “提交日志” 是环形队列缓冲区，由于缓存读多写少的特点，Caffeine 包含了多个 Read Buffer，一个 Write Buffer，每个 Buffer 可能有多个生产者，但批量提交时只需要一个消费者。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAeXPfWHGObMJS7Kgtp6LWztqbBnpSdxQzEaM4wUjCeu78zUDBQwMSsfQ/640?wx_fmt=png)

Caffeine 使用的 Read Buffer 均为无锁有界队列，队列选择基于线程的哈希值而不是缓存数据的哈希值，这样可以避免热点数据访问造成的资源竞争。

随着缓存字典中的数据增多，Read Buffer 数量也自动增加。当某个 Read Buffer 已满时，将触发一个异步任务尝试获取淘汰策略的锁，将所有缓冲区数据批量刷入。在 Buffer 已满但批量任务未完成的时间内，系统会丢弃所有新来的数据，直到 Buffer 再次变得可用。

这样做确实会丢失少量的读取日志，牺牲了一点准确性，但带来了极大的并发性能提升。

Caffeine 中的 Write Buffer 是一个传统的有界阻塞队列，每次对 Write Buffer 的写入都会尽可能地被立即消费（刷入淘汰策略）。

与 Read Buffer 不同的是，Write Buffer 不能忍受数据丢失，如果消费速度太慢，生产者只能重试。尽管如此，这样的操作对效率几乎没有负面影响，因为并发写入的瓶颈在于更新缓存字典，实际上 Write Buffer 中只会有很少量的数据，甚至大部分时候是空的。

**八、缓存状态机**

尽管多个无锁队列极大提升了并发性能，但也丢失了原始操作顺序。

一个 “插入 -> 读取 -> 更新 -> 删除” 的操作流程稍后可能以任意顺序被重放。

Caffeine 使用了状态机定义缓存的生命周期，正常情况下一条缓存的状态被标记为 Alive，当它从缓存字典中被删除但仍存在于淘汰策略中时，状态会原子性的转移为 Retired。

状态是 Retired 的缓存最终会被逐出，同时被标记为 Dead 状态，稍后被 GC 回收。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAeSyrApMUJmx65LCQB8ibRcfawZsYia2GKyU9xe3XsccibibmibRaT19fibIaQ/640?wx_fmt=png)

**九、定时过期与更新策略**

Caffeine Cache 提供了非常有用的定时过期和更新策略API，重新加载数据的逻辑通过 build() 或 buildAsync() 自定义的 CacheLoader 来实现。

```
Cache<String, Integer> cache = Caffeine.newBuilder()    // .expireAfterWrite(3, TimeUnit.SECONDS)    // .expireAfterAccess(3, TimeUnit.SECONDS)    .refreshAfterWrite(3, TimeUnit.SECONDS)    .maximumSize(100)    // .buildAsync()    .build(new CacheLoader<String, Integer>() {        @Override        public Integer load(@Nonnull String key) {...}    });  
// expireAfterWrite=[duration]: 最后一次写入后经过固定时间过期// expireAfterAccess=[duration]: 最后一次写入或访问后经过固定时间过期// refreshAfterWrite=[duration]: 创建缓存或者最近一次更新缓存后经过固定的时间间隔，更新缓存// 经测试, 若 expireAfterWrite 与 refreshAfterWrite 同时存在, refreshAfterWrite 失效; // 若 expireAfterWrite 和 expireAfterAccess 同时存在，以 expireAfterWrite 为准。
```

如果使用 buildAsync() ，缓存的重新加载过程就变成了异步执行，这样在加载期间尝试访问缓存的线程就不会被阻塞，而是拿到加载之前的值，待异步加载完毕后才能获取新值。

对于搜索这种并发量大但一致性容忍度高的服务，多数场景还是采用了这种异步加载的方式，毕竟取到旧值总比大量线程被阻塞要好。

对于定时过期与更新的实现，最简单的方法是直接维护一个时间复杂度 O(logn) 的优先级队列。Caffeine 做了进一步的优化，使整个定时策略的均摊复杂度仅有 O(1) 。

我们以定时过期为例看一下 Caffeine 是如何做到这一点的。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAeHVGG6w0ibvbSO7pIyZCniaGPHNoMqepyjo4vuJGPkbOUJ7ciaHReibnYuA/640?wx_fmt=png)

第一种情况，缓存设置的过期时间是固定值，每次被访问时刷新。

Caffeine 使用了一个很像 LRU 的双向链表，链表的头是最古老的数据，尾是最新的数据。

当一条数据被访问时，就将它移动到链表尾部。这意味着更靠近链表头部的缓存也一定更久没有被访问，当一条缓存被访问但发现已经过期时，所有比它更靠近链表尾部的缓存数据也都可以被清除。

如果每条缓存设置的过期时间都可以不同，事情好像有些复杂了，有没有想过 ScheduledThreadPool 是如何实现的？

答案是时间轮算法。

简单说说时间轮，它是一个高效的延时队列或者说定时任务调度器，任务的添加与移除都是 O(1) 复杂度，在 Kafka、Netty、Zookeeper 中都有广泛应用。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74BX10HU2Y2KfUfTk8BBIdAeAZYwuRtfqrdWv562KXqk4DticQiadotk7Xh1vhsCDbTFrwet6Fg6gxMQ/640?wx_fmt=png)

时间轮类似于一只手表，数据结构是环形队列，底层采用数组实现，数组的每个元素都可以存放一个双向链表，链表中的每一项就是具体的定时任务。

当我们需要添加定时任务时，只需要把任务放到将来被执行的时刻，然后等表针转到这个时刻时，取出该时刻下的任务链表批量执行。

对于只有三个指针的表来说，最大能表示12个小时，超过了12小时就会产生歧义，无法区分是上午还是下午。

如果我们加多几个指针呢？

比如说我们有秒针，分针，时针，上下午针、天针，月针，年针，那就能轻易表达很长的一段时间了。

到计算机的世界中，一种时间轮的实现 （Caffeine 采用的方式）类似于将秒针、分针分别用一个长度为 60 的数组表示，时针用一个长度为 24 的数组来表示。

那么定位一天内的所有时间，只需要三个极小的数组即可。当定位到 **TimeWheel[2小时][15分钟][27秒]** 时，这个元素指向一个链表，保存着所有应该在此刻被清除的缓存。如果处理时发现某条缓存没有过期（被再次访问过），则重新计算其过期时间然后插进时间轮。

对于缓存定时更新的实现，把时间轮中的定时任务由“删除”改为“标记更新”即可。

为什么是 “标记更新” 呢？

因为 Caffeine 具体实现是懒加载的，即使设置了读取数据后五秒更新，在五秒后也不会真的更新，而仅是将这条缓存标记为 “需要更新”。当这条缓存再次被访问时，才会同步或异步地触发数据重加载逻辑。

**十、总结**

至此应该包含了所有 Caffeine Cache 的关键功能设计，另有一些细节的内容，比如淘汰缓存时的软/弱引用、分层时间轮的详细实现，没有进一步展开。

Caffeine 做了什么并不重要，为什么要这样做才重要。

软件开发遇到的很多问题是相通的，所有强大的功能都是简单数据结构的组合，希望深入 Caffeine 原理后，能从其解决问题的方式得到启发，提高抽象和拆解问题的能力。

最后用 Caffeine 作者的性能优化七句箴言做个结尾吧：

Don't do it.

Do it, but don't do it again.

Do it cheaper.

Do it less.

Do it later.

Do it when they're not looking.

Do it concurrently.

**References：**

* Faheem Sohail. (2013). In-Process Caching vs. Distributed Caching. https://dzone.com/articles/process-caching-vs-distributed
* Benjamin Manes. (2016). Design Of A Modern Cache. http://highscalability.com/blog/2016/1/25/design-of-a-modern-cache.html
* Benjamin Manes. (2016). Design Of A Modern Cache—Part Deux. http://highscalability.com/blog/2019/2/25/design-of-a-modern-cachepart-deux.html
* xinzhongtianxia. (2018). 那些惊艳的算法们 —— 时间轮. http://blog.lanjingdejia.com/articles/2018/08/13/1534132662997.html

文｜狗子

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74CFh00RuVn9W60cwmsFfjTx4515do74o9iapyGajU12ltUIQz02jWYFOmESye4EJR94uLl5yhmibVAg/640?wx_fmt=jpeg)

关注得物技术

携手走向技术的云端