---
title: 'JVM STW 和 Dubbo 线程池耗尽的相关性｜得物技术'
company: 得物
tag: 搜索相关性
date: 2024-02-23
url: http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247522085&idx=1&sn=2dbde65692a51ade7f942ae7f6035c99&chksm=c161c27af6164b6c59076fcc121e0816212e2fc6936a27f2b1b07e87734ff0f146ceb7b0880c#rd
account: 得物技术
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_gif/AAQtmjCc74DZeqm2Rc4qc7ocVLZVd8FOASKicbMfKsaziasqIDXGPt8yR8anxPO3NCF4a4DkYCACam4oNAOBmSbA/640?wx_fmt=gif)

**目录**

一、背景

二、Thread pool is EXHAUSTED介绍

三、玄学Thread pool is EXHAUSTED

四、为什么不消费socket recv buffer

五、怎么追溯JVM进程STW

六、总结

**一**

**背景**

# 在日常的技术支持过程中，经常会遇到如下玄学问题的咨询：

* 从监控上看，进程资源占用正常。
* 从监控上看，服务流量平稳，没有流量突增。
* 从监控上看，线程池状态正常，没有瓶颈。

但是，在上述条件下，上游调用方还是时不时反馈偶现 **`Thread pool is EXHAUSTED`**！

接下来笔者来把这个问题系统梳理下，帮助大家厘清这个问题的本质。

**二**

**Thread pool is EXHAUSTED介绍**

# **`Thread pool is EXHAUSTED`**是 Dubbo 中一个非常常见的现象，要理解它首先需要理解 Dubbo 服务端的线程模型。

Dubbo 服务端线程模型，我们站高一点鸟瞰的话，它本质上是一个经典的“生产-消费”模型：

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYvfhbekROPIpMu589NicZNmibJtrMF1JmPGnvUvFbkUDlvib9khqwvzPHA/640?wx_fmt=png&from=appmsg)

需要注意的是，与常见的“生产-消费”模型不一样的是，中间的队列容量为 0，不会暂存、堆积请求。

详见：`java.util.concurrent.SynchronousQueue`

如果请求入列失败，则直接快速失败，中断请求处理。其实细想也很合理，实时请求链路上如果暂存、堆积请求的话，要是链路上某个环节抖动了一下，直接全链路雪崩。

详见：`org.apache.dubbo.remoting.transport.dispatcher.WrappedChannelHandler#sendFeedback`

当网络层的生产速率大于业务层的消费速率时，就会产生 **`Thread pool is EXHAUSTED`**异常。导致该异常的业代码层面的原因本质就是：**请求处理慢导致消费慢**。

在这个本质下，有如下典型的原因：

* DB 慢查询，能产生 P1 故障的那种。
* 锁，互斥锁引起的并发度低，导致请求处理慢。
* 死锁，极端一点的锁问题，业务层线程全被夯死了。
* 网络抖动，导致向下游的请求耗时变长。
* 别的类似的...

可以看到，上述常见的导致线程池满的原因，总会在监控上留下痕迹。只要能从监控信息上定位到请求处理瓶颈，那总是能对症下药优化好的，总的来说，有问题，但是问题不大。

有时也总会遇到监控数据看起来一切正常，但线程池耗尽了的情况，这就有点让人头皮发麻了。

**三**

**玄学Thread pool is EXHAUSTED**

# 所谓的玄学 Thread pool is EXHAUSTED，指的是类似开头描述的那种，从监控层面排查、追溯发现业务层请求处理没有瓶颈、没有抖动。线程池监控数据看起来也一直很健康，但是就是发生了线程池耗尽问题，影响了业务。

如果一直停留在 Java 进程层面看问题，那是无解了。但是如果我们把格局打开，视角再下沉一点，可能又有新思路了。

上面我们说过了，服务进程内的 Dubbo 框架线程模型是“生产-消费”模型，那在操作系统协议栈层面呢？数据从网卡流入进程的交互模型是什么样的呢？

我们站高一点鸟瞰的话，数据从网卡流入进程的交互模型本质上也是是一个经典的“生产-消费”模型：

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IY3ibicDic6Su3byofBV5InDXACfl5jhzKd66bJH7ZmL01HCqibmqLzp9tkw/640?wx_fmt=png&from=appmsg)

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYRX0M0oAhwmicBhjDBiakhwSmG1bPxG2zicMALlib7Lw9fg0nFBIKguNadg/640?wx_fmt=png&from=appmsg)

协议栈和进程中间也有一个缓冲队列，就是大家肯定都背过的八股文里常说的用于流量控制的 TCP 环形缓冲区。

在 Java 语言层面暴露的 API 如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYrxvZTaBZ5DSprmwIwFcY8kGvK5ic4nxBIMMPXSCsDMfYgoD0S3L0I6A/640?wx_fmt=png&from=appmsg)

`java.net.``Socket#setReceiveBuf``ferSize`

总之，经过上述分析(洗脑)，大家都知道了，操作系统协议栈和 JVM 进程间存在一个数据缓冲区。

正常来说，基于这个数据缓冲区的生产-消费速率是匹配的，因为 TCP 的流量控制可以背压，最终会让两端速率匹配上。

但是，如果说突然因为某些原因，JVM 进程抖动了一下，从 `socket recv buffer`中消费数据的逻辑突然停顿了一下，如下图：

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYVEWwh2EOewukTcHFaVDF9WT055iaFkwzwA7b7rW8MWByGWMAcmXlibzw/640?wx_fmt=png&from=appmsg)

这个时候，网卡还在源源不断接收数据，然后投递到 `recv buffer`，直到 `recv buffer`满，TCP 协议才会让对端减速。

到这个时候，`recv buffer`里可能已经缓存了大量的 Dubbo 请求数据等待进程消费、读取、解码、触发业务逻辑。

小请求场景下更明显，比如一个请求 100byte，如果 `socket recv buffer`的容量是 1024 byte 的话，那一个连接上可以缓冲 10 个小请求。

然后 JVM 进程停了一下又恢复了，进程里的网络层代码(Netty)会快速读取 `recv buffer`中的数据，投递到业务层（Dubbo）。

总结来说就是 `socket recv buffer`在特定场景下变成了请求蓄水池，然后脉冲式的一下子倾泻到业务层，进而会导致 Dubbo 线程池满。

这个过程发生的很快，按固定周期采样的监控数据无法体现这个过程。因为把尺度放大的话，由于对端发送请求的速率是稳定的，所以这个服务进程宏观监控视角上的平均 QPS 一直都是稳定的。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYqbznCoEQJQZtfuLr9vvHiaEjC4WXdjUqyoic1VMsy66ictMIApvicBDm2w/640?wx_fmt=png&from=appmsg)

**如图，在监控数据采样周期的时间尺度上，QPS 是稳定的。但是在更小的时间尺度上，QPS 产生了波峰波谷。**

**四**

**为什么不消费****`socket recv buffer`**

# 进程消费 `socket recv buffer`的职责一般是由进程内网络层代码来承担，常见的网络层如 Netty，一般都是死循环（EventLoop）消费 `socket recv buffer`的。所以正常情况下，消费延迟是可控的。

所以，如果网络层精心设计的死循环消费的代码不消费 `socket recv buffer`中的数据了，最大的可能是消费 `socket recv buffer`数据的线程（如 Netty 中的 EventLoop）停顿了。

线程停顿的原因，如果排除了对网络层库（比如 Netty）的错误使用，那往往是 JVM 进程直接整个停顿了，也就是 **STW**。

一说到 STW，大家可能就不困了，条件反射的就想着 GC 了。这里必须要科普一点就是：**GC 会导致 STW，但是不光 GC 会导致 STW**。

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYLUpNbfWIcLSEYUkviaib1xsdX92Ww4J372cXicLPt1LqLqxCiaEb2TffSw/640?wx_fmt=png&from=appmsg)

**GC 是 STW 的充分不必要条件**

STW 机制是 JVM 内部的一个基础机制，JVM 作为一个托管业务代码的 Runtime，在运行时进行一些**监管、清理、优化等动作**的时候，为了保证数据视图稳定一致、避免数据竞争，就会想办法让进程里的线程都停下来，让 JVM 执行托管动作。

JVM 将上述的**监管、清理、优化等动作**按 OOP 思想（模板方法设计模式）抽象为 `VM_Operation`类，需要执行托管动作时就创建 `VM_Operation`，入列、出列、STW、执行，也就是说 `VM_Operation`会触发 STW。

详见：Hotspot 垃圾回收之 VM\_Operation 源码解析（https://blog.csdn.net/qq\_31865983/article/details/103788358）

JDK8 源码中搜索到的 `VM_Operation`子类有：

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYLHK05b172GeREZVZZYzicmqCBdHKlTFqNVWu0p7IvDTd2ia6FL7kFtPQ/640?wx_fmt=jpeg&from=appmsg)

VM\_Operation 驾到，所有线程统统闪开~

**五**

**怎么追溯JVM进程STW**

# 一路分析下来，我们发现压力全来到了 STW 这边，那么问题来了，我怎么知道 JVM 在事发时有没有 STW 过？

JVM STW 之前一定会先进入安全点，所以线索又到了安全点这里。

STW 和安全点的关系详见：JVM stop the world（https://zhuanlan.zhihu.com/p/91937583）

JVM 暴露了安全点的进、出事件日志，可以通过开关打开，后续可以通过安全点时间日志追溯。

添加如下启动参数，即可打开安全点事件日志：

```
-XX:+PrintSafepointStatistics -XX:PrintSafepointStatisticsCount=1
```

```
日志示例：
```

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYusGhNZaK5QXNMENsH0ia4j3IeRILjPAqOBunMpcQfYUSlMO4D6mhqnA/640?wx_fmt=png&from=appmsg)

在 JVM 启动 5.141 秒后，因为【撤销偏向锁】进入安全点，STW 持续了 0.0000782 秒，其中让所有线程停下来花了 0.0000269 秒。

详见：通过 JVM 日志来进行安全点分析（https://developer.aliyun.com/article/486349）

**六**

**总结**

# 如上述的 Thread pool is EXHAUSTED 异常，结合应用层框架原理和底层网络原理可以推导出如下问题路径：

* JVM STW阻塞了应用层网络框（Netty）IO读写。
* 网络数据驻留、堆积在协议栈 Buffer 中。
* JVM STW解除后，应用层网络框架（Netty）快速的读取协议栈 Buffer 中的数据。
* 形成流量尖刺，超过应用层RPC框（Dubbo）的承载能力。
* 产生Thread pool is EXHAUSTED 异常。

同时，在诊断应用层框架或代码的异常行为时，在仔细审查、推敲代码逻辑以外，必要时还需要视角向下，考虑基础设施、底层能力的特性、行为。

---

**往期回顾**

[1. 大模型在产品原型生成中的应用实践｜得物技术](http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247521456&idx=1&sn=0ecc393d411d03bc768011544d6b1f5c&chksm=c161c1eff61648f9f53bbf793e3b5af19b3c8d3662a47bf2ee28ccf1606d436bfc10912ef1ec&scene=21#wechat_redirect)  
[2. DartVM GC 深度剖析｜得物技术](http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247521401&idx=1&sn=24c10848eccceecf76e5032ca57142c6&chksm=c161c126f61648301923866575a904b90665067f79dc58338810b361974b3401dd07039011dd&scene=21#wechat_redirect)  
[3. 互动游戏团队如何将性能体验优化做到TOP级别｜得物技术](http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247521212&idx=1&sn=7fcb6ef435ea83905dc4f9eac5c3d8e1&chksm=c161c6e3f6164ff51f20256e3da661c53a7daffde2cb0347c1e1de2931997f0b8e00f25e30cd&scene=21#wechat_redirect)  
[4. 得物自动化平台执行器设计与实现](http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247520208&idx=1&sn=82edddb58bb4fda7b2180eccd5569411&chksm=c161da8ff6165399ac1bb10d76225762f5f75e6cdd0155f6ec00ba764d07d731d339b35b4267&scene=21#wechat_redirect)  
[5. SpEL应用实战｜得物技术](http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247519342&idx=1&sn=9f420501acb0f912bf3b2296c6b1125f&chksm=c161d931f61650275e8bc6e9729bab3aa7d448ae4ecd117c9e72b915c9eaf06d8fd4245457b1&scene=21#wechat_redirect)  
[6. 得物大模型平台接入最佳实践](http://mp.weixin.qq.com/s?__biz=MzkxNTE3ODU0NA==&mid=2247519126&idx=1&sn=df81bb7d0c9694ac721cb012326a2f5d&chksm=c161dec9f61657dfd5d242431e686ddd500c8f7e94d149fc3d18835230f3631196434ad1f0ad&scene=21#wechat_redirect)

---

\*文/羊羽

关注得物技术，每周一、三、五更新技术干货  
要是觉得文章对你有帮助的话，欢迎评论转发点赞~  
未经得物技术许可严禁转载，否则依法追究法律责任。

“

**扫码添加小助手微信**

如有任何疑问，或想要了解更多技术资讯，请添加小助手微信：

![](https://mmbiz.qpic.cn/mmbiz_jpg/AAQtmjCc74CAGS6PldJufoMwZe4UZ1IwmaXQ5n9mkpElaPtrunYoYgbIB7sib5m1qD2jfErd5MZ449jicmLWqTZg/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

---

**线下活动推荐**

主题：得物技术沙龙-稳定生产专场

时间：2024年3月10日（周日）14:00-18:00

地点：上海·杨浦区黄兴路221号互联宝地C2栋5楼培训教室（宁国路地铁站1号口）

活动亮点：本次得物技术沙龙-稳定生产专场主题为**全景应急保障&可观测性系统建设**，将在上海（线上同步直播）为你带来五个令人期待的演讲话题：

得物NOC团队负责人-夏玉好-《得物全景应急保障体系建设》

得物可观测性平台产品负责人-袁国华-《得物全景可观测性产品建设》

...and more

PS：沙龙讲师持续邀请中，大家想听哪位大厂技术专家前来分享可以在评论区与我们互动，说不定本次沙龙就会来与大家见面交流哦～

希望通过以上话题的分享，以及得物技术沙龙-稳定生产专场这个交流平台，能够促进不同领域的同好者们知识和经验的共享，对内提升个人专业素养和技能水平，为职业发展打下良好基础，对外促进行业内的合作与交流，推动行业的发展和创新。

**快快点击下面图片报名吧~**

![](https://mmbiz.qpic.cn/mmbiz_png/AAQtmjCc74CU7S9201ewQqaCdPpoL0IYAjSoW4ZhqfCib2xFZ4DSXH4MmBdwXQGePwiccaSwNMUEgHxCyqRP9v1Q/640?wx_fmt=png&from=appmsg)