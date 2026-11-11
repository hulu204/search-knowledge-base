---
title: 'Gradient   Normalization在多任务学习中的优化实践'
company: 阿里淘系
tag: 多目标&多任务
date: 2022-03-29
url: http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650457145&idx=1&sn=569530d4129f0ba122b79ddd66e6e742&chksm=83960c21b4e18537aa1edaead0ecf40f1e74aec662f1bc69d8a166b55085862d16211aa661a6&scene=27#wechat_redirect
account: 大淘宝技术
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_gif/33P2FdAnju95xNQaJWFlU3fWicicxBac5nuOMtveZ6lxCCnoZU1Xd6ITUVhoibJib5eyx6d2hePhGFNbQ4nT3Gicgpg/640?wx_fmt=gif)

本系列文章包含每平每屋过去一年在召回、排序和冷启动等模块中的一些探索和实践经验，本文为该专题的第四篇。

第一篇指路：[冷启动系统优化与内容潜力预估实践](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650453241&idx=1&sn=d30e011ac9e416aab54eb76378b43f39&chksm=83967ce1b4e1f5f79ce2067171d9c6336269edb47c88992ba765376438534ba13a6b83da287f&scene=21#wechat_redirect)

第二篇指路：[GNN在轻应用内容推荐中的召回实践](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650454966&idx=1&sn=a5721d265ed07138fdad3c8e1d06b727&chksm=839673aeb4e1fab8164ef508bfeddc4f4cfc2c76d8163cf209c871df94a0c3fb0b1fd7f9c9b6&scene=21#wechat_redirect)

第三篇指路：[基于特征全埋点的精排ODL实践总结](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650455296&idx=1&sn=06621faf40213e4e56a3211a88a6e234&chksm=83967518b4e1fc0e38716b43f07fb863fa12b2f1ac1e8b2afb2ef0d062f091b3e375dde8f0f3&scene=21#wechat_redirect)

前言

在每平每屋以及我们团队负责的其他一些场景，MMoE多任务模型是精排阶段常用的模型。在每平每屋场景中，我们使用MMoE模型，对场景中的三个任务同时进行点击率预估，即内容的一跳点击、内容详情页点击以及跳转的商品详情页点击。MMoE结构有别于简单的Hard Parameter Sharing的方式，可以通过模型去学习不同任务之间哪些参数共享(Experts)，共享的程度如何(Gates)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0b93N9Mibt0AQHTaZI6FrfdyJa8JCptib5sKkXjxLeFzibEhND6PuD57tWA/640?wx_fmt=png)

建模

MMoE是从Model Structure的角度来对共享参数做精细化控制，并在很多场景都取得了提升。除了Model Structure之外，我们还可以从Model Dynamics的角度去考虑优化。由于不同任务之间天然存在着数据量、样本分布、难易程度的差别，导致在训练过程中，收敛速度、收敛结果都会存在不小的差异。Model Dynamics希望在模型训练过程中去动态调整训练的速度等变量。

建模

Model Dynamics的优化，一般通过loss函数来实现。常见的多任务模型loss，可以简单对多个任务的loss相加得到，如下所示

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bTHGtQhSFjG2hxkhG45ibny5TJSEPVicg3j6BPwJyjiaq8a7zUDVKazvtQ/640?wx_fmt=png)

这种方式的不合理之处是显然的，训练的loss很容易被一些loss特别大的任务所主导，导致最终的优化未能取得预期的效果。一个简单的优化是基于人工经验，对多个任务的loss分别赋予一个固定权重，但是这个权重在整个训练周期中是固定的，并没有考虑到不同的训练阶段，权重可能变化的情况。

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bg4xa4YjicSqXwf1ib6G6f8OkEtA4nIjsgbNaQdGMqVB264vVZVZg05jg/640?wx_fmt=png)

一个更合理的加权方式，应该是动态的，这里我们对权重![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0b2ACrciaiaC0Jtoa2AOrianNfZDzdMNU9QIQsyd5KibmVOh8QXncANz8uTg/640?wx_fmt=png)通过2个参数来控制，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bUdic8UiaABjm3AqkXkEgxfpmuJS7kBibfcE8PDZ4SYxZGnr4hKoibmibF0Q/640?wx_fmt=png)为训练的steps数，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bA2u6f8sEVZtdKw99ENfvLYUXU8caQehHf9xp7CK0omEib0SVFuUtTibw/640?wx_fmt=png)为其他可能的参数。接下来的介绍我们都是基于这个框架展开，演示一些实际的实现方式

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bic961hC5ZPAMFSY4OManMxQDticQJKF3OfEn43cDBnh10sTCB1T4dR9g/640?wx_fmt=png)

#### ▐  Dynamic Weight Averaging

#### 

DWA发表于CVPR 2019的论文《End-to-End Multi-Task Learning with Attention》，核心公式如下所示

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0b8OWKOp8Xibw0icMjn3agl7KibLmszicFIibYWvDniaZRrtAxRtovnYfrqv0g/640?wx_fmt=png)

1. ![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bzWRwYtPsmJSGTRicESCJeue53cRiceNfW1MkeLBibvCyk20pLNSg3tyXg/640?wx_fmt=png)表示任务![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bZ808ccZEyAe0DGDdVUtRZjNxtcbC5uaeEvvuia8rvYOu3icTkQVHLDdQ/640?wx_fmt=png)在![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bKuuJVFqCibplzibkdYEeOWbAticAXc4Dibze2GgXTriamrLBaR4KmicHgvPQ/640?wx_fmt=png)步时的训练loss，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bQBHavJrAHWf2Hqnib07jSMibCrWsXjYtlZdV6GQWrRNpvEzON51zoPSA/640?wx_fmt=png)表示此时的loss下降速度，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bqciaia9Siaquaw4zk3BxOCXll0PYgyUGv4nNsvhSx0Z2SQtgYNldvG7icw/640?wx_fmt=png)越小，训练速度越快
2. ![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bQuDHmOu42RT2xNLPGFHWqnOAFS7Jydg47BYjWJTZDSGYTrcW1BYxog/640?wx_fmt=png)代表不同任务loss的权重，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bY6zSg66HGb9XVEAhOucKZqc4GZYgJj7b4BFaFYlBjic1hjDhQ36CP8Q/640?wx_fmt=png)为任务的数量，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bygwwBcr6j9iauSaJBLfqFm84Pic5NKu0iaVfLJ07FWU6cKsFWakkk7mqw/640?wx_fmt=png)为一个temperature参数，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bo3oibXGgCyVXx5fABiaL1j3WkoBoiaH0n6Bk7ZytuHoJmAhQY8v5JSo7w/640?wx_fmt=png)时，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bwnEeG25sQuksh4BM2xibyAT7BdUtZSAicXnibxEMFiaCWsqCBFtg0WpsRg/640?wx_fmt=png)为softmax，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0biaL0Ctz2kialusOWBMmbPj3YuLpH7dbd6565oKLBMHh6h38OmllIHmdw/640?wx_fmt=png)时，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bwnEeG25sQuksh4BM2xibyAT7BdUtZSAicXnibxEMFiaCWsqCBFtg0WpsRg/640?wx_fmt=png)为1。直观的结果来看，loss收敛越快的任务，获得的权重越小

#### ▐  Dynamic Task Prioritization

#### 

DTP发表于ECCV 2018的论文《Dynamic task prioritization for multitask learning》，核心公式如下所示

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bfTrnFa60xNPeg9rdGSD5UXAqJ4qtQ9BvwicRC3UqQHUPybIiccOEB4dw/640?wx_fmt=png)

1. ![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bmYgjKhF8dlw8Im0fBzf6mRYpfr0dn5JoiaapkaEaxQEha29v5vvXy8Q/640?wx_fmt=png) 表示在![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bVOCXyfoYIIdaubPTzB2Fucrrqgc5AXibNKc4PzN6sDiavTeIviaGeyk9Q/640?wx_fmt=png)步时的某衡量KPI值，取值为[0, 1] 之间，例如在分类任务里，KPI可以是分类的准确率。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0buFGhwibpxpc6IbjYXG4y8LuYbn3tibPqiaAWXaBmczb4mohfgyKq3uJUw/640?wx_fmt=png)是一个固定的temperature参数，可用于人工调节
2. ![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bPYdDFlOYE4oFOWcgQK9zN6LXojqDibNQGNhqVyK4xekA8Kr0hJIOUAA/640?wx_fmt=png)代表不同任务loss的权重。直观的结果来看，KPI越高的任务，获得的权重越小

#### ▐  Gradient Normalization

#### 

GradNorm发表于ICML 2018的论文《Gradnorm: Gradient normalization for adaptive loss balancing in deep multitask networks》，其核心思想相对前述的DWA和DTP更为复杂，核心观点为

1. 不仅考虑loss收敛的速度，进一步希望loss本身的量级能尽量接近
2. 不同的任务以相近的速度训练(与gradient相关)

我们同样还是从![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bBPMicCq6cBgA41djic5FSakKBbgmiaSI7dZ1d3gfttXLdV7jVdSzac21w/640?wx_fmt=png)这个公式出发，作者定义了两个loss，一个是常规的标签loss，即![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bpiaP96cRoqxECpibxTC6Rh4GfljzPia3rLGVpMpt1SKFU7FibthfqhmiaeA/640?wx_fmt=png)，另一个loss为gradient loss，是一个和权重![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bRmxpjC9RvrUUMNtahC32YsQ1PGEu4zia3MVMLAsmTJpXSnf2cr3K3YA/640?wx_fmt=png)相关的loss

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0b9GVq1NbTDWegWszPI8WmiaRicNibgC1KzBRsA1zoUiblnreAicJoibRhPsbA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bD7YyzIMAnrfwbmKSfdmk75C6M7gIqOt6jMiaA7AnJOpBUXIlb6QVcog/640?wx_fmt=png)为模型参数的子集，也是我们要应用Gradient Normalization的参数集，在论文中作者选择的是模型中共享参数的最后一层。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bFibtLOVOjE62ibDmg8fAMCg4fl0iawianMPqnKVuUTh3weqN9f6FcdFNyA/640?wx_fmt=png)为![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0blNjnTu4wIS0qq0bDvvVFtm83iadcXzFFQLq7mEw3HMsR25eJjhwLKQw/640?wx_fmt=png)

对![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bzMjXzIU7eXDXsOFAlWfDniaZG5kxXUWncwxCrrFWT18zzUfFrUUlFgg/640?wx_fmt=png)求导后的 gradient的 L2范式，主要用来表征loss的量级。 为全部![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bcG0iaKBIbLs55veYlvSDCuegw8eqCcw1W3q4Epg1WlxaAEtVcpH9GhQ/640?wx_fmt=png)的均值

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0b4jicamV3tIwulhLSoQXxZgLz8MhuD3HcWHHhibUShm5TWufaONenXmiag/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bceXKXA1GL8zKp6vfTko88NHPicVlOMWpQo8BNxiara1mLWX8cYs9aicPw/640?wx_fmt=png)用于衡量任务训练的反向速度，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bQP9OeACSrqicEAVmKCTe96UT1m1ew5p1RIvFOcAnMWAYnD9ncRpRA5w/640?wx_fmt=png)越大，表明任务训练越慢，这点和DWA的思想接近，但是这里使用的是第一步的loss，而不是DWA中的前一步loss。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bzOK1iakicfW9sLsibJUtbyIUmWHrmZImvb6gdLaMCp8ibQicvXNSHiatDoibg/640?wx_fmt=png)用于衡量任务训练的相对反向速度，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bzOK1iakicfW9sLsibJUtbyIUmWHrmZImvb6gdLaMCp8ibQicvXNSHiatDoibg/640?wx_fmt=png) 越大，表明任务相对所有任务而言训练较慢。最终我们得到的gradient loss

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bNbmz3FJDkKRjicg6eJic1kX1SOmevicC3Libo0DgR7nCWNQE6yD7ImK1oQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bLGyrYyuDZECUf8wrx1AUphY1kql8PvPb5ScbpErZ5KD3dFVjA3Hiayw/640?wx_fmt=png)表示理想的梯度标准化后的值。这里的gradient loss只用于更新![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bj2z7qdL0tuUUGiclDiaCGoib1gywrXiaWTlnht3FBgYI245CicVOWNGF02w/640?wx_fmt=png)。![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bj2z7qdL0tuUUGiclDiaCGoib1gywrXiaWTlnht3FBgYI245CicVOWNGF02w/640?wx_fmt=png)还会经过最终的renormalize，使得![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bUVMhq4oQPB2m1xu4Z375JQzEe5viamh5OZV5vYU1vaY9jjdeicrzzt9Q/640?wx_fmt=png)，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bwQkXfzXlicJYHZ4txC9akDJHicVgb1NKF7EZ8PwiaOGYQQ3q6k1FEibibuw/640?wx_fmt=png)为任务的数量。从gradient loss的定义来看，![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bnaQXRwXbyuaFS5bAMSvLTMw1xuJoQFKZy6V7llgLIRQRNwYMOV8iaVg/640?wx_fmt=png)越大，表明任务训练越快，gradient loss 越大；![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0btLbIuN6xCBOXicgIQn2ktIYHXarGbHwbdL5bebDkraIYfibH0EUNp3Eg/640?wx_fmt=png)表征loss 量级的变化，不论![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bG9dHIFuIScWSunTEIzEMdvVbLleUEVVQFrBkrFdguahbicemD5QAaEQ/640?wx_fmt=png)过大或者过小都会导致gradient loss 变大。

GradNorm实践

我们实现的代码部分主要参考了 https://github.com/vpetren/gradnorm\_tf/blob/master/gradnorm\_tf.py 的开源部分。实验场景为每平每屋轻应用。我们首先实现了一版基于作者原始论文中描述的版本，但是发现这一版本的效果不佳，gradient loss的收敛较差且波动大。其主要原因在于![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bAy76z1mlsRibJo3CwhZWFhoU5g5j1JzcibRALk5ohxy0uvg9wf3fUc5Q/640?wx_fmt=png)中![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bwlboxRj3hKI5Dl2IhYpZxpoxdAPrXFt9hibH8WKojdmFnx1A5dS95ew/640?wx_fmt=png)为训练的第一步loss，在推荐系统的训练中，单个batch的训练loss相对来说比较不稳定，导致![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bCDpPnNCNIuUZFz90MH9LlQK1OQ8NqKVvyR46hdYicjrTj0gWCrG2xKA/640?wx_fmt=png)的计算不置信。我们同样也验证了![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bWUicZibiaicFfeJvvSnibITkbPrfs8dGykibTFMT7pk6jicZFsXHI5wuJ2fdQ/640?wx_fmt=png)的计算方式在我们的场景中也效果不佳。最终我们选用了

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0be8LzXxU06kP5nPSdt1d8ibPfCkBHA4wQHiapRZIxSeXZiaXmc9nXc5ZEg/640?wx_fmt=png)

分母设置为![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bsC2hibEicjptudQmEsODrYicibA9URPy3owOlfftA8mWSByuhYQyBnWlcw/640?wx_fmt=png)到![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bzSic5ibn6VTUjIia26icoQ8uD91QlAVbo8aw4YQia3lLRM5geYdMjHshCvA/640?wx_fmt=png)之间的![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bUtWtCSbLhtzZ3ic47k4bvdAsVvzF7dD7shiagY5lXjEKdgfwKo9EUHfA/640?wx_fmt=png)的 Moving Average

#### ▐  离线对比

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bNqzv82965EvHXoAsVkVu6EqDwrdbrdykoKwHYlWbQm5GibYen34onUg/640?wx_fmt=png)**: inv\_training\_rate对比**

|  |  |  |  |
| --- | --- | --- | --- |
| type | ctr inv\_training\_rate | cvr inv\_training\_rate | fav inv\_training\_rate |
| train gradient loss | 2 ~ 2.3 | 0.6 | 0.05 |
| no train gradient loss | 1.4 ~ 2 | 1.2 | 0.16 |

可以看到，增加了gradient loss之后，ctr任务的训练速度在相对变慢，cvr和fav两个任务的训练速度相对变快

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bDF2f5RLg8AXdh1gIZXKGibMH7Hf83LhDH6AoPCOUwPibVuklGib7Ic6tw/640?wx_fmt=png)**的变化趋势**

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju8S21rVfibEMcpJodlU6vd0bKZcufWkyY3WAKicF7aMYicmJ4FiamicJ7WsPDxFD3eMibaK1VvPcxLukUpg/640?wx_fmt=png)

**auc结果波动性**

我们对同样的模型参数组，连续训练三次，计算每次结果三个任务auc的均值和方差，我们可以发现，在不使用gn的基准组，一跳点击、二跳点击、商详点击的预估auc方差逐次增大，这也表明二跳点击和商详点击的预估任务，在相同训练参数下波动较大，表明任务训练的结果不好，这对于线上结果显然是有害的。而在使用了gn的实验组，auc的方差都保持在相对较低的水平，表明这几个任务的训练结果应当是稳定的。

|  |  |  |  |
| --- | --- | --- | --- |
| type | click auc | detail auc | fav auc |
| baseline | 0.6720 ± 0.0013 | 0.6886 ± 0.0057 | 0.6915 ± 0.0095 |
| baseline + gn | 0.6828 ± 0.0023 | 0.7078 ± 0.0014 | 0.7155 ± 0.0012 |

baseline 平均波动：0.0055

baseline + gn 平均波动：0.0016

整体训练波动被大幅缩小，尤其是在正样本比较稀疏的 detail 任务和 fav 任务上，此外加入gn之后整体auc有明显的提升。

#### ▐  线上AB

线上ab结果，pctcvr +3.49%，avg\_ipv +4.04%

|  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ab\_name | uctr\_improv | pctr\_improv | avg\_expo\_improv | avg\_click\_improv | ipv\_uctr\_improv | ipv\_pctr\_improv | uctcvr\_improv | pctcvr\_improv | avg\_ipv\_improv |
| GradNorm | 2.25% | 4.59% | 0.51% | 5.13% | -0.19% | -1.05% | 2.06% | 3.49% | 4.04% |
| Baseline AA | 0.00% | -0.15% | 0.43% | 0.27% | 0.03% | 0.02% | 0.03% | -0.13% | 0.26% |
| Baseline | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% | 0.00% |

总结

在实际推荐、搜索场景中，我们所优化的业务目标往往并不单一，使用多任务、多目标模型在目前业界比较常见。不同于MMoE、PLE等Model Structure优化，我们从Model Dynamic的角度出发，人为定义一系列"好的"Model Dynamic标准，并在建模中应用，取得了在MMoE基础上的进一步提升。两类优化具有互补性，在实际使用中可以同时应用。

团队介绍

\*本项工作是本组实习生知同在职时合作完成。

淘系技术部-淘宝智能团队

淘宝智能团队是一支数据和算法一体的团队，服务于淘宝、天猫、聚划算、闲鱼和每平每屋等业务线的二十余个业务场景，提供线上零售、内容社区、3D智能设计和端上智能等数据和算法服务。我们通过机器学习、强化学习、数据挖掘、机器视觉、NLP、运筹学、3D算法、搜索和推荐算法，为千万商家寻找商机，为平台运营提供智能化方案，为用户提高使用体验，为设计师提供自动搭配和布局，从而促进平台和生态的供给繁荣和用户增长，不断拓展商业边界。

这是一支快速成长中的学习型团队。在创造业务价值的同时，我们不断输出学术成果，在KDD、ICCV、Management Science等国际会议和杂志上发表数篇学术论文。团队学习氛围浓厚，每年组织上百场技术分享交流，互相学习和启发。真诚邀请海内外相关方向的优秀人才加入我们。如果您有兴趣可将简历发至bangzhu.gx@alibaba-inc.com，期待您的加入！

参考文献

[1] 多任务学习优化（Optimization in Multi-task learning） https://zhuanlan.zhihu.com/p/269492239

[2] Modeling Task Relationships in Multi-task Learning with Multi-gate Mixture-of-Experts, KDD 2018 https://dl.acm.org/doi/10.1145/3219819.3220007

[3] End-to-End Multi-Task Learning with Attention, CVPR 2019 https://openaccess.thecvf.com/content\_CVPR\_2019/papers/Liu\_End-To-End\_Multi-Task\_Learning\_With\_Attention\_CVPR\_2019\_paper.pdf

[4] Dynamic task prioritization for multitask learning, ECCV 2018 https://openaccess.thecvf.com/content\_ECCV\_2018/papers/Michelle\_Guo\_Focus\_on\_the\_ECCV\_2018\_paper.pdf

[5] GradNorm: Gradient Normalization for Adaptive Loss Balancing in Deep Multitask Networks, ICML 2018 http://proceedings.mlr.press/v80/chen18a/chen18a.pdf

✿  **拓展阅读**

[![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju8zZtLVahOicmUqnuRoDulXlHGAKF8y37aUDib3u6zMhWxeTSORWibV2b8UDvaNGxlwog7u5qlfpEJFg/640?wx_fmt=jpeg)](http://mp.weixin.qq.com/s?__biz=MzAxNDEwNjk5OQ==&mid=2650453241&idx=1&sn=d30e011ac9e416aab54eb76378b43f39&chksm=83967ce1b4e1f5f79ce2067171d9c6336269edb47c88992ba765376438534ba13a6b83da287f&scene=21#wechat_redirect)

**作者****|**邦祝

**编辑|**橙子君

**出品|**阿里巴巴新零售淘系技术

![](https://mmbiz.qpic.cn/mmbiz_jpg/33P2FdAnju9qJSYLusYZ20IeW1JcwLxOmYpQKzz1XI7PlgmOA3cPARTxwZuKFw6osZsksibeH7HrS9oiaVooQSZQ/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_png/33P2FdAnju9I3TY9EP8M3D7oDuMfTuEh37yxribyjc3viaicCKBT9nJhqBcib36SSRaib3vIobcZbx93RYyf9QvgzOA/640?wx_fmt=png)