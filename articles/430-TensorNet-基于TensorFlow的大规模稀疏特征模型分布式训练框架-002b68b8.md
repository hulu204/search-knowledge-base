---
title: 'TensorNet——基于TensorFlow的大规模稀疏特征模型分布式训练框架'
company: 360
tag: 工程相关
date: 2020-09-14
url: http://mp.weixin.qq.com/s?__biz=MzkzNzI0MDMxNQ==&mid=2247487550&idx=1&sn=68af975e460637783d0a860bfb2d694d&chksm=c29323aaf5e4aabc45b4f705d6c69583960fdae2638f2b3a5252f507ecfa088c92e1f72c6ad8&mpshare=1&scene=1&srcid=0117tJyokgtmE6m24zBKj7kA&sharer_sharetime=1673957367314&sharer_shareid=c032e8bde4d276951619cca1ff0debb1#rd
account: 360技术工程
origin: readme
---
**奇技 · 指南**

TensorNet是什么？

TensorNet是一个构建在TensorFlow之上针对广告推荐等大规模稀疏场景优化的分布式训练框架。TensorNet的目标是让所有使用TensorFlow的开发者可以快速的、方便的训练出稀疏参数超过百亿的超大模型。

**训****练带有大规模稀疏特征模型的主要挑战**

在广告、搜索、推荐等场景下的深度模型都会存在大量的高维离散稀疏特征，训练带有高维稀疏特征的模型主要有两个问题：

1. 训练样本规模大。比如对于360广告场景会有超过100TB的训练数据。
2. 模型参数多。比如对于360广告场景会有超过100亿的参数。

使用单机模式训练模型速度慢，耗时长，严重制约了模型的迭代速度，使用分布式训练已经成为业界标准。

**使用TensorFlow训练稀疏特征模型的主要问题**

TensorFlow是最受开发者欢迎的深度学习训练框架，但是TensorFlow对训练带有大规模稀疏特征的模型不太友好，主要问题有：

1. TensorFlow支持的特征维度有限。一般的，TensorFlow需要对每一个特征定义一个矩阵，这个矩阵受限于内存，往往不能太大。
2. TensorFlow分布式训练时需要同步所有的参数，这导致速度过慢。由于带有稀疏特征的模型参数多，同步开销非常大，会严重制约训练的速度。

**TensorNet——基于TensorFlow的专为大规模稀疏特征模型优化的分布式训练框架**

TensorNet在复用TensorFlow的所有功能的基础之上，专门定制使其支持大规模稀疏特征模型的训练。TensorNet的主要提升包括：

1. 使TensorFlow支持的稀疏特征的维度接近于**无限**。
2. 使TensorFlow分布式训练时同步的参数规模减小到原来的万分之一，乃至十万分之一，从而极大的提升了训练速度。在360真实业务场景下我们将原来的离线训练时间由3.5小时提升到了**25分钟**。
3. 配合TensorNet通过split graph的方法可以对在线推理的性能进行优化。在360真实场景测试中我们发现有近 **35%**的性能提升。

**TensorNet分布式训练架构**

TensorNet支持异步和同步模式训练。异步模式在仅有CPU的集群中速度提升十分显著，同步模式在网卡速度超过100GbE的GPU集群中表现突出。

**TensorNet异步训练架构**

在仅有CPU的集群中使用参数服务器的异步训练模式是训练模型速度最快的方法，TensorNet异步训练架构与TensorFlow的异步训练架构有很大的区别：

1. TensorNet将sparse参数和与dense参数分别使用不同的parameter server管理。
2. TensorNet不设单独的parameter server节点。在每个worker中都会维护一个sparse paramter server和dense parameter server。这省去了开发人员管理ps节点和worker节点的不少麻烦。
3. TensorNet对sparse参数使用分布式哈希表按照哈希值均匀分布不同的节点上。这相较于TensorFlow需要让开发者根据自身情况将tensor分布在不同的ps节点上的方法更加灵活，这不仅减小了节点通信热点的概率，还减轻了开发者的工作量。
4. TensorNet将模型的所有dense参数合并后使用分布式数组切分到不同的机器上，每次pull和push参数的时候只有一次网络请求。相较于TensorFlow对每个tensor都有一次网络请求的方法极大的减少了网络请求的次数从而提升了模型训练的速度。

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbAEndQ6yEk9C6xIp42jglQq8MEc6hkVJwia0BSTxYAZACzN4IXTa9O7kgYM6icZ7OdYRbxxmtCbZicw/640?wx_fmt=png)

**TensorNet异步训练架构**

**TensorNet同步训练架构**

TensorNet同步训练架构基本与TensorFlow的MultiWorkerMirroredStrategy架构一致，主要区别如下：

1. TensorNet使用单独的sparse parameter server节点保存所有sparse参数。通过parameter server可以解决TensorFlow支持的sparse特征维度不能太大的问题。
2. TensorNet对sparse参数做了特殊的定制化的同步。TensorNet在训练时只同步当前训练的batch所关注的稀疏特征，相较于TensorFlow会将所有参数都同步的模式通信数据减少到了原来的万分之一，乃至十万分之一。

   ![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbAEndQ6yEk9C6xIp42jglQ2ndpt47NkbAFA2y31R9EwJhlgzZQJOZAQhNjcjD8gCQLbued7sDJCw/640?wx_fmt=png)

   **TensorNet同步训练架构**

**TensorNet核心优化**

TensorNet最核心的优化是将模型的embedding tensor优化到了最小。

如下图所示，对于最简单的wide&deep模型，如果在一个广告系统中有3亿用户，那么就需要定义一个维度为3亿的embedding矩阵，在训练模型时需要在这个3亿维的矩阵上做`embedding_lookup`得到当前batch内的用户的embedding信息，近而在embedding之上做更加复杂的操作。

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbAEndQ6yEk9C6xIp42jglQTQ1aNqYEOIich8lNUOkW76m1LDgdwezDo96qHmicNSEraXicIejDIfWFg/640?wx_fmt=png)

**TensorFlow中的实现**

显而易见，在高维稀疏场景下，存在有下列问题：

1. embedding矩阵太大，占用内存多。很显然当特征较多的时候单机无法存储整个模型。
2. 分布式训练同步开销巨大。由于TensorFlow同步时是需要同步整个矩阵以便进行训练，这极大的消耗了网络带宽，拖慢了整体速度。

**TensorNet使用一个较小的，可以容纳特征在一个batch内所有数据的embedding矩阵代替TensorFlow默认实现中需要定义的较大的embedding矩阵**。

如下图所示，在batch\_size设置为1024的场景下，对于用户id特征，在TensorNet中只需要定义一个维度为1024的embedding矩阵，TensorNet的主要处理步骤如下：

1. 定义模型时定义userid的embedding矩阵的维度为一个batch内所有用户id个数的最大值。
2. 训练模型时得到当前batch内的所有用户id。
3. 将用户id排序，并按照先后顺序为每个userid分配索引，索引从0开始，对应为下图中的`virtual sparse feature`。
4. 使用userid从parameter server中获取相应的embedding向量，然后按照其对应的索引放置到embedding矩阵中。
5. 使用转换后的`virtual sparse feature`作为模型的输入。

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbAEndQ6yEk9C6xIp42jglQ5A5v3spMXZd5Em9QykSibLHctm3ELicxzsZQxodEhqxEia56G5ngIWNVA/640?wx_fmt=png)

**TensorNet中的实现**

从上述可见，TensorNet由于极大的减小了模型所需要的embedding矩阵，从而可以极大的减小分布式训练时的开销，以及通过parameter server的方式使得稀疏特征的维度可以支持到接近无限维，从而可以极大的提升模型的刻画能力。

**TensorNet Inference优化**

由于TensorNet只更改了模型的第一层，从而模型的inference也变得极其简单。

在使用TensorNet构造模型的时候，可以将模型切分为两部分，如下图所示，`embedding_lookup_graph`只在离线训练时使用，在线inference时只需要将sparse embedding导出成字典供`inference_graph`作为输入即可，具体的请参考以下系列文章：

1. 为inference准备——模型切分: https://github.com/Qihoo360/tensornet/blob/master/doc/tutorial/03-split-to-sub-graph.ipynb

2. 使用XLA方式进行在线预估: https://github.com/Qihoo360/tensornet/blob/master/doc/tutorial/04-deploy-tf-graph-online.ipynb

3. sparse embedding字典导出: https://github.com/Qihoo360/tensornet/blob/master/doc/tutorial/05-export-sparse-feature-embedding.ipynb

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkbAEndQ6yEk9C6xIp42jglQ9T9ecibP5scA2pzSVZHm0Ych5ab5DPsLafZD92nX7mhYZTWIcFSEqSw/640?wx_fmt=png)

**TensorNet中split graph inference方案**

在360内部场景中我们测试发现通过split graph配合`XLA AOT`的方法性能提升近**35%**。

**TensorNet开源及使用**

TensorNet已经成功落地应用到了360广告ctr预估相关的场景中，并取得了显著的效果，我们已将代码、文档及我们在360广告的应用经验全部整理到了项目中，欢迎关注。

**tensorNet主页**：https://github.com/Qihoo360/TensorNet

**tensornet快速上手**：https://github.com/Qihoo360/TensorNet/doc/tutorial/01-begin-with-wide-deep.ipynb

**更多文档请看**：https://github.com/Qihoo360/TensorNet/README.md

**联系方式**：张彦升(zhangyansheng@360.cn),姚磊(yaolei@360.cn)

微信交流群：

![](https://mmbiz.qpic.cn/mmbiz_jpg/IwabbYzTYkbAEndQ6yEk9C6xIp42jglQ5EKTPIQomqlNbGX0r6Hq3HGW45Vly97f64VIp1FYv6YbmNtsB2PCNA/640?wx_fmt=jpeg)

**往期精彩回顾**

## [从Java8升级到Java11](http://mp.weixin.qq.com/s?__biz=MzUxMTcwOTM4Mg==&mid=2247487476&idx=1&sn=efb4d869354ddebc05ee1b2e1ca04fa5&chksm=f96ed65dce195f4b807d73661b375a2523db544c8f64ba517a8e5a0a2f6d61d8d5fd8e38a12b&scene=21#wechat_redirect)

## [实习招聘|360云平台火热招聘中](http://mp.weixin.qq.com/s?__biz=MzUxMTcwOTM4Mg==&mid=2247486640&idx=1&sn=01931a6a29f0e2deaf1d815ab2ceed0d&chksm=f96ed519ce195c0f0287e0208174776042ef9369e662d4cc00148561659dcf3b04d75aa5a2a2&scene=21#wechat_redirect)

## [360Stack裸金属服务器部署实践](http://mp.weixin.qq.com/s?__biz=MzUxMTcwOTM4Mg==&mid=2247486893&idx=1&sn=b7169ea1c16e63ddd5d7a682be41c7eb&chksm=f96ed404ce195d123ec90851eec73f352518f03bee09721b355c6fe61ee7f03175fe19021c81&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkZUfMfH1lJ6bNr07KicibhLda4SPy4HQHJRGwmFehzhSkGOZWSPWrWEZdASV4WzqY4ibbd8bhtxbv7Hw/640?wx_fmt=png "微信图片_20200217193301.png")

![](https://mmbiz.qpic.cn/mmbiz_png/IwabbYzTYkZUfMfH1lJ6bNr07KicibhLdaMonzr9QbFGibNpCy3Qe6punia4JCZwGdZUGFfs3nAvRyicZYKCun3ib9Wg/640?wx_fmt=png)

360技术公众号

技术干货|一手资讯|精彩活动

扫码关注我们