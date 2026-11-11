---
title: 'NVIDIA   Merlin HugeCTR 推荐系统框架介绍'
company: NVIDIA
tag: 精排&CXR预估
date: 2022-10-31
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247607015&idx=1&sn=640758c804a49c7fee278066b85203df&chksm=fbd6908bcca1199d272fe7ca3e6c7cde7dcdb43f33fbfc319fca414f76f5f3dc97ca443cb178&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj4byDO6jpIX971RUwKxzakFkLfxAV05KkTNSyz1JdE9N7cq484wsDpw/640?wx_fmt=gif "进群看直播.gif")

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgD4UkLqgeMp1lOPZT1j8C1bNIruffe3qYao6zupxaXAuxaJJibluYfqlShg6wwfzHPjdyu9s76wXw/640?wx_fmt=png)

**导读：**众所周知，推荐系统在新时代的互联网环境下已然出现在我们生活的各个角落，我们刷视频、在网上买东西、使用社交软件都离不开推荐系统的推荐。推荐系统也是目前互联网的增长引擎。根据麦肯锡的报道，有超过 35% 的亚马逊购买和超过 75% 的 Netflix 观看，而这些其实都是基于推荐系统相关的算法而产生的。推荐系统的推荐质量可以直接影响公司收入，可能 0.1% 的推荐准确度都会影响可能上亿的收入。

现如今公司必须要去努力地提高他们推荐系统的推荐质量和推荐效率从而拿到更好的收入。可目前互联网日益增长的这个用户数和商品数等数据的规模越来越大，推荐系统对于算力的要求也是越来越大。因此 NVIDIA 开发了 Merlin 这套系统来专门解决传统的推荐系统中可能存在的一些问题。

**本文主要分为四个部分**，第一部分是对 NVIDIA Merlin HugeCTR 推荐系统框架做整体的介绍；第二部分是关于 HugeCTR 的整体介绍， Embedding 工作模式以及重要 Feature。第三部分是 HugeCTR 的推理，主要会介绍 HugeCTR 的分级推理参数服务器（HPS）。最后一部分是介绍 Sparse Operation Kit（SOK），它能够让用户在 TensorFlow 里面去使用 HugeCTR 的一些相关特性和方法。

**全文目录：**

* Merlin 系统介绍
* HugeCTR 概览
* HugeCTR 推理
* HugeCTR Sparse Operation Kit

分享嘉宾｜石济 英伟达 推荐系统工程师

编辑整理｜崔婕 Shopee

出品平台｜DataFunTalk

---

**01**

**Merlin 系统介绍**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj1WUW2qwcGkAXl2d6mnve1u7JdKAd2cjNg7V8icyhbF5YYqY9PEiblOtw/640?wx_fmt=png)

Merlin 系统分为三大模块。首先是 NV Tabular 模块，它是 Merlin 的一个数据处理的模块。传统的 ETL Pipeline 一般都复杂而且存在速度瓶颈。但是 NV Tabular pipeline 提供了数据处理的 GPU 加速，以及有异步的数据加载器来加速整体 ETL Pipeline。第二大模块是我们的 HugeCTR，我们的 HugeCTR 主要是通过多节点多 GPU 的模型并行方式来提升整体的训练和推理的速度。第三大模块是 Triton。Triton 相当于是一个 GPU 加速的推理平台，它可以部署非常大规模的推理模型并且可以保持一个非常低的延迟和高吞吐。

**02**

**HugeCTR 概览**

HugeCTR 是一个开源的推荐系统框架。它使用 GPU 加速，主要代码构成是 CUDA C++，并且使用了非常多的 NVIDIA 自己的  GPU 加速的软件库，比如线性代数的库 cuBLAS, 深度学习的库 cuDNN，还有网络通信的库 NCCL。与此同时 HugeCTR 提供了一个类似 Keras 的非常高层的 Python API 以方便使用。HugeCTR 也持续的在向 NVIDIA MLPerf 竞赛提交成绩，并且成绩一直非常优异。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjMtl0SxQI5ElAnM697GJh4D4tHaHBJojfmvOktSPm4JtWcic441AYpgw/640?wx_fmt=png)

HugeCTR 设计之时是为了支持有超大 Embedding Table 的推荐模型的训练，这是主要设计目的。现在 HugeCTR 也支持了非常多的一些模型及他们的变种，包括 DLRM, Wide & Deep, Deep Cross Network 和 Deep FM 等。目前通过经过 GPU 加速且推荐专用的推理参数服务器，HugeCTR 也新增了相关的推理模块。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjALAKBiarICls7rlhrq5gVghHRSzltZArKSDFqCczU1H8iccTXJdAMy8g/640?wx_fmt=png)

正如前文所说，由于现阶段用户数和商品数的激增，我们在推荐场景当中用到的 Embedding Table 会变得异于寻常的规模，**动辄 100 GB 甚至上 TB** 。这是第一个很大的挑战， 因为一张 A100 的显存只有 80G，这样意味着这些 Embedding Table 肯定没有办法存在单张 GPU 的显存中。所以我们需要使用更多的 GPU 并用模型并行的方式去存储下整个 Embedding Table。

**第二个问题是在 Embedding 当中存在很多限制内存带宽的操作**。这些操作就是都在 CUDA kernel 里面进行，而这些 CUDA kernel 都是独立的，不同 Kernel 之间有很多 Shared Memory 或者 Global Memory 去加载或者存储这些中间数据，这样会造成非常大的内存瓶颈。这个的解决方案就是将这些分开的这些操作融合到一起，变成单个的 Kernel。

**第三个比较大的挑战是在模型并行的过程当中，我们需要大量 GPU 之间和节点之间的通信，这种通信也会随着 GPU 数量和节点数量提升非常的高的复杂度**。因此在这里我们也用到了 NCCL 这个 GPU 间传输库和 NVLink 和 NVSwitch 这种物理传输介质，来提高我们的整体训练效率。

当然还有一个办法可以同时解决以上三个问题，那就是采用一个混合精度的训练，我们可以用一个 16 位的浮点数去代替 32 位的浮点数去进行运算。这样的话整个 Embedding Table 会变小，并且内存压力也会减少，并且网络通信的负担也会降低。

**接下来就是针对三个问题的详细方案：**

**1. Embedding Table 的模型并行**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj0Ju7PEc6I6FyWeiaLyGsY294LmZGZRQ1xJMzkvLy9icG2pyfxUN6O48Q/640?wx_fmt=png)

针对第一个问题，即 Embedding Table 特别大导致没有办法放在单张卡上的这个问题，我们 HugeCTR 采用模型并行的方式来解决。具体的做法是我们会将 Embedding Table 拆分到多个节点的多张卡上来进行运算，然后每张卡上处理一部分的数据。这样的话，不仅能够让我们的 Embedding Table 得以完全存下，并且还能够加速整个训练的过程。

**2. CUDA Kernel 的融合**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjnzD9osVsELZbu2pxpeSMQWRoBACQN6ygEwu5S1ta5Mfr32G0ce0DNw/640?wx_fmt=png)

然后就是刚刚提到的第二个问题，比方说我们在神经网络当中有 Pooling 层， Pooling 完之后我们会 Concatenate 起来。这样的话这两个层是分开的。在这个分开的操作当中会有非常多的与存储介质进行交互的操作。这种操作会带来内存上的一些瓶颈。它的解决方案就是我们可以将这两个操作合并到一个 CUDA Kernel 里面去进行。这样我们在两个操作之间就不需要再重新地去读取和存储。我们所有的这些操作都可以在计算器里面去完成，就不需要和其他的存储介质进行交互，这样也是能够大大地减小不必要的开销。

**3. 混合精度训练**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjqnxBcElMl3eUH1WZGOH4usUricZ4JtMSvIBTPsiaIKh0IOwf26Hk0O7w/640?wx_fmt=png)

上文也提到有一个办法能够同时解决前面提到的三个问题，即同时解决模型过大、显存不够以及跨节点通信瓶颈的方法，就是采用这个混合精度的训练。混合精度训练能够同时发挥 NVIDIA TensorCore 的计算优势以及 Embedding Table 中节省存储空间和通信开销的优势。我们在每一次迭代的过程当中，优化器最终会输出的是一个 FP 32 的权重。然后它在进入下一次迭代的时候，它会被转化成 FP 16 去进行运算。目前在这个这个权重的更新和权重的转化上，是在两个不同的 Kernel 里面去进行运算的。根据之前的可以将 Kernel 融合的方式去进一步减小开销的方法，我们可以继续进行优化的一个部分，这也是我们正在做的。

**4. CUDA Graph**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjGVMRf9UFN2mCVCbx7qoSvs6dEszUgYsUN95psXGY1NOc5nxkf8cs1Q/640?wx_fmt=png)

HugeCTR 在前向和后向的计算过程当中，会启动多线程的 Kernel 来让 GPU 的利用率的尽可能的饱和。那么可以看到就在这里每一个线程里面是会有很多很多连续的 CUDA Kernel 的，他们会在神经网络里面做不一样的操作。可以看见上图里 Kernel 和 Kernel 之间是会有非常多的间隙，这是因为 CUDA Kernel 在提交启动的时候是会有一个额外的开销的，这个开销在 Kernel 数量不是很多的时候不会很明显。但当你的神经网络非常复杂的时候，比如可能有很多层，这种时候 Kernel 会非常多，那么这个开销就变得非常的重要，你没有办法去忽略这个开销。于是我们需要想一个办法，能不能去隐藏这些 CUDA Kernel 之间的不必要的开销，即 CUDA Kernel 启动的这些开销。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjWRKhxiaXjSsMjsf5q0kTJgK0SicAVtCmicHonOEXA5RwpNJKvQaQABRTA/640?wx_fmt=png)

在这里我们用到了一个技术是 NVIDIA 的 CUDA Graph。CUDA Graph 所做的就是将这些 CUDA Kernel 组织成一个有向无环图，然后去通过异步的方式隐藏掉不同  Kernel 之间启动的不必要的开销。这样做之后，可以看到我们的 CUDA Kernel 是基本上完全连续地在进行运作的，不会有没有必要的开销。

**5. HugeCTR 的 Performance**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj5x0nytaVES24oiargw5aicxCOziaPSicSEnFDJf52I3nzn9T72mWNeNT1g/640?wx_fmt=png)

上图是 HugeCTR 的 Performance 随着 GPU 的型号以及 GPU 的数量增长所带来一个变化。这里我们用的是一个 Wide & Deep 模型，在 DGX-1，DGX-2 和  DGX A100 上都进行测试。可以看到 DGX A100 相比 DGX-1，就是 A100 的卡和  v100 的卡相比是快了整整三倍的。这里面也不只是因为 Streaming Multiprocessor 的提升，也是因为很多架构上的优化。另外我们使用八张卡是比使用一张卡有 6 倍的提升的，在多卡通信复杂度会越来越高的情况下，六倍的提升还是一个相当可观的一个数据。我们也是在持续地不断地进行优化当中，让  Scaling Effect 变得更加的强。

**6. HugeCTR 在 MLPerf 竞赛上的表现**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAic6oPdyFqSial0ugj8EL0wXJKVg1ObtMibH2kPCjDlmeYMz4cPRnsIpwaDewTM6UDa76GssPSa3qA/640?wx_fmt=png)

HugeCTR 一直在为 NVIDIA 的 MLPerf 比赛提交成绩。这是一个深度学习的比赛。它主要使用的模型是 DLRM，使用的数据集是 Criteo 的 1TB 的数据集。在这里我们可以看到使用 GPU 去进行这个模型的训练显然比 CPU 有着非常大的优势。并且，随着 ML Perf 版本的迭代，v2.0 的新版本相比 v1.0 的版本有接近 70% 的提升。这里面特地为这种推荐模型做了非常多的优化。这些优化大家如果感兴趣的话，可以到 MLPerf 的官方网站（www.mlpref.org）了解详情。

**7. ONNX 模型转换器**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgAic6oPdyFqSial0ugj8EL0wiaTtksiazMSanTsS1rt1TTRt4ia8QA9uUmM1yCiabgJBNQiabd041ESLMcQ/640?wx_fmt=png)

HugeCTR 比较重要的 Feature 是 ONNX 转换器。ONNX 是目前的一个开源的通用神经网络的模型格式。可以使用上面这个非常简单的 Python API，将 HugeCTR 的模型图比如 WDL 的模型（即 WDI.JOSN 模型图），以及稠密部分的模型文件和稀疏部分的模型文件输入进来，这个转换器就会自动地将整个 HugeCTR 模型转化成一个 ONNX 模型，这样方便用户使用不同框架去训练模型。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjiciaFynKN8AQLxCfRh1bSoDITlGuHsrGtYpfo76Seicu9qTk8eiaxmcD0Q/640?wx_fmt=png)

这就是我们关于 HugeCTR 的主要功能介绍和 Embedding 方面的优化的介绍。上图是一些其他的资源比如在这次 ML Perf 1.1 中做的一些特别优化，还有最近的发布说明，以及一些可以非常容易跑起来的 Sample 和 Notebook，欢迎大家也到我们的 GitHub 上面去阅读和尝试：https://github.com/NVIDIA-Merlin/HugeCTR。

**03**

**HugeCTR 推理**

推荐系统的推理也会遇到各种各样的一些挑战：

* 模型尺寸过大
* 延迟和吞吐
* 增量更新模型
* GPU 计算和存储资源隔离

首先还是模型非常大这个问题，没有办法将模型存到单卡上。第二个问题是由于在业务上，推理相比训练有着更强的实时性的要求，于是对于延迟和吞吐更加的苛刻。第三个问题是当有增量模型的时候，我们需要快速地进行更新后模型的部署，然后马上应用到新的推理请求当中。还有一些其他的挑战，包括比如 GPU 计算和存储资源的隔离这些问题。

**为了解决这些问题，HugeCTR 开发了一个专门用于推理的参数服务器叫做 HugeCTR Hierarchical Parameter Server 简称 HPS。**接下来我会主要讲 HPS 是如何设计和工作的。为了解决我刚刚提到的那些推理过程当中可能遇到的种种挑战，我们要利用 GPU 的高内存带宽以及高运算速度的这些优势。通过分级的存储方式我们可以看到，首先 SSD 是拥有的一个最大的存储空间的，往往是十几 TB 甚至上百 TB 级别。但是从 SSD 读到 CPU Memory 里面是非常慢的，最快可能也就几十 G 每秒。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjcvINMuLv8XibzAiaSDPsz1iaZ6XiauibricjiabQWYhg9N9P8Yv1OZonR0pgQ/640?wx_fmt=png)

如果将整个 Embedding Table 都存到 SSD 是非常不合适的，因为我们读取的开销非常的大，于是我们需要合理地去利用 GPU 和 CPU 内存的读取速度快的优势去加速我们整个 Embedding 的读取。相比于 CPU 内存 GPU 内存虽然说空间存储空间没有那么大，但是好处是它可以不再需要通过 CPU 就可以直接落到 GPU 的  SM 里面进行运算，这样可以节省 90% 的时间，根据这个加载的速度来判断。

当然由于整个 Embedding Table 非常大，我们也不可能将整个 Embedding 全部存在 GPU 的 Memory 里。我们需要合理地去利用这三个存储介质去存放 Embedding Table 然后达到我们的业务需求。在这里一个比较好的解决方案就是可以将最热的那些 Embedding 存在 GPU Memory 里面，然后次热的存在 CPU Memory 里面，然后以此类推，我们可以将整个剩余的模型都存储到 SSD 当中，这样就可以提高整体的访问效率。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjCCtv7KcmfTbAP1efFnXvskzo2capoo5YOeF5MkicMBgJCq5l9ucFwkw/640?wx_fmt=png)

下面讲一下 **HPS 参数服务器的推理的架构**。GPU 内存可以存储最热的 Embedding，于是我们开发了一个叫做 GPU Embedding Cache 的缓存，来存储最热的 Embedding ，它是由我们的参数服务器来进行管理的。并且，同样的模型它们的不同实例是可以共享同样的 Embedding Cache，而整个参数服务器又会管理不同的模型。参数服务器数据后端作为 GPU Embedding Cache 的缓存架构的基石，同时它也是这个 GPU Embedding Cache 在 CPU 内存以及本地磁盘的进一步的物理拓展。通过绑定不同物理层级的存储，可以提高整个推理服务的速度，从而提高吞吐而降低延迟。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj4rvnn5Ke9mXW6DTicVP8DcxOFkj1tQjsMib8xEM5cSnhP1zR0D5HcZCQ/640?wx_fmt=png)

接下来重点讲一下**这两种数据库后端**。

* **持久型的数据库后端**

持久型的数据库后端是用本地的 SSD 作为持久化的存储介质的，它维护完整的模型参数，整个 Embedding 都会被存储到 SSD。同时它也相当于承载着一个模型参数的容错容灾的这么一个功能。相对于 GPU Embedding 的缓存与 CPU 的缓存来说，这个持久化的存储介质可以看作是一个无限的虚拟空间的存储后端，同时也是本地的一个 Key Value 查询引擎。因此我们在 HPS 当中引入了性能优化后的 RocksDB 来作为这个持久化后端的一个实现。

具体来说，我们在每一个推理节点，通过参数服务器的配置文件，就可以在本地磁盘保留整个模型的 Embedding Table。这个永久化的数据后端也是对分布式的Volatile 后端的进一步补充。第一，它提高了存储容量；第二，它提高了可用性；第三，它可以满足刚刚说的容灾的一些问题。

* **Volatile 数据后端**

相比于从 SSD 当中去加载，Volatile 的数据库后端相比于持久化的数据后端主要是以 CPU Memory 作为主要的存储介质，无论是本地还是远端它可以提供一个更加快捷的一个参数的读写功能。由于持久化的这个数据后端容量可以理解为无限大，因此它在实际的推理服务当中会非常慢。因此我们需要用这个 Volatile 的数据后端去一定程度上弥补这个持久化数据库的缺陷，去拓展有限的 GPU 内存。但是 Volatile 数据库容量本质上也是有限的。所以我们需要通过对这个参数进行分区使用多个机器的 CPU Memory 来尽可能地存储更多的模型并提高 Volatile 数据库后端的上限。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj7nibVwQZApcjQKySxGqmswEIB6X0licftjy9dRZTu6Bib11RA6bUvsW0A/640?wx_fmt=png)

在持续训练的过程当中会有一个参数更新的过程。

我们为了更好地去解耦训练端和推理端，同时保持着数据的一致性，我们用到了 Kafka 消息队列。训练端更新好的参数会通过 Message Sink 发给到 Kafka 的 Buffer 然后推理端这边会通过 Message Source 去不断地消费 Kafka Buffer 里面更新更好的模型参数，去完成推理端的模型更新以达到更快速的新模型部署。整个过程是异步完成的，不会影响正在运行的推理。并且 Kafka 的 Buffer 可以一定程度上提供比较好的容灾。比如推理节点挂了，那么在这种情况下更新好的参数还是会保存在这个 Kafka 的 Buffer 当中。当然推理端重新起来的时候，可以继续通过 Message Source 去消费这些更新好的参数。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjZQyYQ1TKzLVjQklCcfZuF5NbggIOficvBvXoJicneXOUMey4INztXCgg/640?wx_fmt=png)

下面是 **HugeCTR 分级参数服务器的一些配置使用**。我们其实就是需要配置 RocksDB 和 Redis 相关的信息。在连续的训练当中，我们还需要去配置一下 Kafka 的相关信息。比如在训练的过程当中，我们需要去配置一个 Kafka 的 Broker，提供 Kafka 的 IP 和端口，来让数据更新到指定的 Kafka 集群。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjdFHaPhOV0yG4iaTL02dpjOiczLWaY7amo64fwEXgym0cicDDTf5k36icZA/640?wx_fmt=png)

用户总体上就是用这么一个 JSON 格式的配置文件，可以任意地去搭配这些不同的数据客户后端，来合理地适配于不同业务场景所需要的推理需求，以此保证每一个部署节点充分地利用前面提到的这些存储介质。

这里是我们 HPS 总体端到端的 Setup，可以看到 HPS 是构建于 Merlin 的第三大组成部分 Triton 的推理架构之上的。正如下面完整的数据流来显示的，每一个 Triton 节点会通过这个 Volatile 数据后端去维护 CPU 缓存，同时也可以维护对应  Redis 节点的参数分区。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjjgpNs366z7ZcpLkNvubM3kABS1vfmjXw755ckfWnk0wBRXEODkqz4Q/640?wx_fmt=png)

Redis 这个集群当中的参数既可以通过训练与推理的集群共享，也可以通过订阅 Kafka 数据源来实现这个无缝的参数更新。模型在 HugeCTR 训练平台可以实时地将在线训练中的增量的模型推向这个分布式的 Kafka 队列。然后我们在 JSON  配置里面可以去通过配置让推理节点去自动地检测和监控这些消息队列，从而保证推理节点和持久化的这个数据后端是始终维护着一个完整的参数副本，为这我们整个推理的这个容错提供保障。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjFfKYkHQLfm9d7sggib0njbTd4UnzDNtryytZvgXicS2pYo2lafoIkskw/640?wx_fmt=png)

我们 HugeCTR 的分级参数服务器还在持续地优化当中。从我们第一次引入这个分级参数服务器开始，我们也进行了大量的优化，在各个后端的 Performance有着非常大的提升，尤其是 Redis 后端，也就是基于 CPU 的这个存储介质的后端有着接近 80 倍的提升。当然我们之后也会持续不断地进行更新优化，然后以达到更好的推理效果。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjicTA3bSpIds1P1nn3nxo2vibEvoY3c5GzHpemJpQPLHSdQVoNl4j4qRQ/640?wx_fmt=png)

上图是有关 HugeCTR 推理相关的一些资料，包含了一些文档，还有一些 Demo Notebook，欢迎感兴趣的各位读者到这些地方去关注、互动。

**04**

**HugeCTR Sparse Operation Kit**

接下来进入最后一部分内容，HugeCTR 的 Sparse Operation Kit, SOK 主要的Motivation 是为了能够让用户在 TensorFlow 里面也去使用 HugeCTR 的一些相关特性和优化。它里面提供了很多让用户可以用 HugeCTR 的操作方式去操作  Embedding 的方法为 TensorFlow 提供了一个 GPU 加速的解决方案。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjbRkfmTJvEnzwLFnIT9yqN9mcIDC3MfDXvIiahSpXWee5JNJqaibHUIiag/640?wx_fmt=png)

SOK 它主要是有以下几个比较重要的**特点**。第一就是它有**非常好的兼容性**，它与 TensorFlow 1 和 TensorFlow 2 都是兼容的。并且用户也**不需要重新地去编译或者去安装 TensorFlow**，直接使用 Pip Install Sok 就可以很简单地使用。

第三点就是它**与分布式的训练框架比如 Horovod 也是兼容的**。

目前行业内主流的一些训练框架基本上都不支持模型并行。因此在推荐模型这种模型非常稀疏且庞大的场景当中，如果使用一个常规的训练框架，是很难去有效利用 GPU 的资源去加速训练过程的。因此无论这些资源是在单节点还是多节点，SOK 提供了一个在训练框架当中去使用模型并行的方式去有效地利用所有的 GPU 资源。并且现在大部分的训练框架都是支持数据并行的。因此 SOK 也同时兼容了数据并行的训练，让开发者可以尽量少做代码的更改。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxj80tJiabibzMeiaVFVayJDlYFIeq2n0yRibxibJiaPoX9E8ibJkQuj3F7MRCTA/640?wx_fmt=png)

当启用了 SOK 之后用户可以搭建一个同时具有数据并行也具有模型并行的神经网络。前面提到 SOK 是同时和 Horovod 是兼容的，因此数据在送进 Embedding 层之前是可以完全按照之前 Horovod 里面的数据并行的方式去进行操作，不需要与任何其他的从数据并行到模型并行端的这些转化的工作。上图正是表达了同时支持数据并行和模型并行的一个工作流。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjjbMBMy3bJjq5XouOM2Twk5NibWbibjsWsCpePqJb2sxgglgLfpNGFnFw/640?wx_fmt=png)

接下来介绍 **SOK 的使用方法**。这里是一个 TensorFlow 的例子，我们只需要加入三段 SOK 的代码，就可以在 Horovod 中去启用 SOK 的模型并行的部分来完成一个分布式的训练，所以它易用性非常强。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjq1zJr9QSpibnOW58mmb7lhA8BUfsKxzvlAx7LHMwFw67OH8YNofojbQ/640?wx_fmt=png)

如果大家对 SOK 相关的这些内容感兴趣的话，上图是一些相关的资料，有专门的文档，也有一些非常简单的 Notebook 可以直接运行。

**05**

**问答环节**

**Q1：超过 100G 的大模型，如何单机多卡训练？**

A1：HugeCTR 支持单机多卡训练。因为如果你多张卡的话，比如在 DGX A100 上，有 8 张 A100，那么显然 100G 的模型是肯定能够存到这 8 张卡上的，所以这样的一个训练是没有问题的。

**Q2：请问 HugeCTR 支持混合 Embedding 吗？**

A2：支持混合 Embedding。

**Q3：SOK 支持 PyTorch 吗？**

A3：暂时还不支持，目前只支持 TensorFlow。PyTorch 部分持续在开发当中。

**Q4：如何保证多机多卡的效果不下降？**

A4：我们使用了 NVIDIA 自己研发一些网络通信的库，像 NCCL。我们还通过 NVSwitch 和 NVLink 去降低通信延迟带来的效果下降。

**Q5：现在 HugeCTR 有哪些厂商已经应用了？**

A5：目前 HugeCTR 已经为国内的一些互联网厂商提供了服务。

**Q6：多级多卡训练这块能介绍一下吗？然后能介绍一下怎么实现的？CheckPoint 是怎么实现的？**

A6：可以到我们的 GitHub 上面去了解详细的信息，因为我们 GitHub 上面有完整的文档介绍这块内容。

**Q7：Embedding 哈希冲突问题有考虑过吗？**

A7：用的是 Linear Probing 来解决。

**Q8：限不限制 TensorFlow 的版本？**

A8：支持 TensorFlow 1.15 和 2+ 版本。

**Q9：什么场景才能遇到 100 GB 规模的模型，需要用户 ID 、物品 ID 的稀疏笛卡集吗？**

A9：对这种情况下是可能会超过 100 GB 的模型的。如果你的模型使用了像 ID 性质的，而非统计性质的参数，比如用户今天看了多少个视频，就有可能会遇到 100 GB 规模的模型。

**今天的分享就到这里，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxje7tZtmc2tpIH8SvlxtxUlIAqkO9ouQnpClZcf6sVKmwKUEUhpZB4fw/640?wx_fmt=gif)

**｜分享嘉宾｜**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgcib7g3OBSwlOtS9lmoLPxjbfSMyYp9OknRiaVrFbibTUaP8SqJFXOrNsL2hEJkwzO3L3SYhfib60Q6Q/640?wx_fmt=png)

**石济**

**英伟达 推荐系统工程师**

本科毕业于加州大学伯克利分校，研究生毕业于康奈尔大学。现在是Nvidia Merlin HugeCTR团队的成员，主要负责推荐系统框架的设计和开发。

**｜往期文章推荐｜**

[**搜推广**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=1685834724168040450#wechat_redirect)**｜****[知识图谱](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=1511758276064051201#wechat_redirect)｜**[**NLP**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2568600449394900993#wechat_redirect)｜**[智能风控](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2005111998123999233#wechat_redirect)｜[数据科学](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=1535281267087376391#wechat_redirect)**

[**决策智能**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2558479437345030147#wechat_redirect)｜[**图机器学习**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2064480910284029953#wechat_redirect)｜[**AI基础设施**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2554085342841372673#wechat_redirect)｜[**数字人**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2171716821010219013#wechat_redirect)

[**数据治理**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=1752671276269174787#wechat_redirect)｜[**隐私计算**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2619895078488342532#wechat_redirect)｜[**大数据存储**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2403766367654363137#wechat_redirect)｜[**大数据计算**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2335878386285658115#wechat_redirect)

[**多维分****析**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=1939952422211158024#wechat_redirect)｜[**大数据基础设施**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2560139955654852609#wechat_redirect)｜[**产品经理**](https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzU1NTMyOTI4Mw==&action=getalbum&album_id=2621090541816217600#wechat_redirect)

**｜免费直播&资料｜**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgD4UkLqgeMp1lOPZT1j8C1UypuAqPicb4V9H2XRRn59kylkS3eO0XbWa70BBLwefuEvL5nx4mxGRg/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgD4UkLqgeMp1lOPZT1j8C1JdwZ6Sic3hgwJrpLUZONyZKS5XiczcLyiaJHbiblgia4qnN1uvQET1wqjIg/640?wx_fmt=png)

**｜DataFun新媒体矩阵｜**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgD4UkLqgeMp1lOPZT1j8C1hwlt6mIkI6A6pQcIqV6cibLYvrxLvEca50r0xP8pDP7WwNlmYg75cGA/640?wx_fmt=png "联系二维码.png")

**｜商务合作｜**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgD4UkLqgeMp1lOPZT1j8C1TczSftIbvfS5nnib9ogH6TlRQmKRLEicbvgA8wFIdey1oibsPNvEQh0Rw/640?wx_fmt=png "新媒体矩阵.png")

**｜关于DataFun｜**

专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100+线下和100+线上沙龙、论坛及峰会，已邀请超过2000位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章800+，百万+阅读，15万+精准粉丝。

🧐 **分享、点赞、在看**，给个**3连击**呗！**👇**