---
title: '多任务学习最新进展：基于神经元级共享的   CTR、CVR 多任务联合预估方法'
company: Shopee
tag: 推荐
date: 2023-05-29
url: https://mp.weixin.qq.com/s/4PO6EK3b4VCKO0ibd76C9w
account: DataFunSummit
origin: readme
---
![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzicG4JNibg4fM4icRVwXP5UmibMEaiaiapF9TBxMcG8Aguyicy2ica6QzY0gjnzMZudFHyibWhWXhbIMJdC6w/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyOYZK0n4wOv9icX9VKj4FJdibJzt7iaPPg0AlzPmRdMGqbB8ys3EeNtU7naxLKS2UmIpfmMibbbkrw2Q/640?wx_fmt=png)

**导读** 本文将介绍一种基于神经元级共享的 CTR、CVR 多任务联合预估的方法。分享分为两大部分：第一部分介绍多任务学习相关发展；第二部分具体介绍我们提出的一种多任务联合预估的方法。

**全文目录如下：**

1. 多任务学习的背景介绍

2. 多任务经典模型结构

3. 一种基于神经元级共享的 CTR、CVR 多任务联合预估的方法

分享嘉宾｜陈华斌 阿里巴巴 算法工程师

编辑整理｜刘晓涛 深圳大学

出品社区｜DataFun

---

**01**

**多任务学习的背景介绍**

Stein 悖论是探索多任务学习（MTL）（Caruana，1997）的早期动机。很多东西看起来表面上是不相关的，但其实它们会服从一个潜在的相似的模式，这就是多任务学习在统计学上的基础。

在机器学习领域中，多任务学习是一种学习范式，其中来自多任务的数据被用来获得优于独立学习每个任务的性能。即便是真实世界中看似无关的任务也因数据共享的过程而存在一定的依赖性或者相关性。

**1. 多任务学习中的 CTR、CVR**

在电商行业中，经常会听到点击率（CTR，Click-Through-Rote）与转化率（CVR，Conversion Rate）这两个词，都是代表某种行为转化，同时它们也是业务分析的重要指标。**CTR 和 CVR 的区别在于两者表示着不同的广告投放指标，**可以从一定程度上反映广告投放的效果。在广告和推荐场景中，用户首先会看到平台给他生成的推荐结果，称为曝光（impression），用户会有一定的概率做点击 CTR，公式是 CTR=（点击量/展示量次数）\* 100%。如果满意就会购买产品，称为 CVR，公式是 CVR =(转化量/点击量)\*100%。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyYPqYQgB7WdBcUJsPyNbiahFSeicGEpONXZVWwECF6yDtEDGmcycgiag9Q/640?wx_fmt=png)

**上图是典型的推荐系统的示意图，**候选池->召回->精排。很多公司会在精排之后增加重排机制最后给出推荐展示。展示之后会有点击和观看。在视频推荐领域中，CVR 会根据观看视频时长来确定，即表示视频观看的完成度。CTR 预估和 CVR 预估是推荐系统中的经典目标。

多任务学习能够减少资源压力（计算成本和时间成本），充分利用各个任务的潜在关系校准单任务（样本选择偏差、样本稀疏）。但是可能会引入一些共享冲突问题。典型的粗粒度任务共享可能会引入共享冲突，用户可能存在细粒度的内容兴趣偏好。比如一个用户在电商平台上因为标题或者封面因素点击了一个商品但是并没有购买，那么在 CTR 任务中它是一个正样本，但在 CVR 任务中就可能是一个负样本。很多时候 CTR 跟 CVR 存在一定的潜在兴趣冲突。那没有很好地去解决这些冲突，多任务带来的效果可能是 CTR 和 CVR 都会下降。当然我们这个工作主要是利用 CTR 来优化 CVR，所以本篇也会重点把这个讨论放在 CVR 的优化上。

**2. 多任务学习的潜在优势**

**① 隐式数据增强**

每个任务都有自己的样本，使用多任务学习，模型的样本量会提升很多。而且数据都会有噪声，如果单学 A 任务，模型会把 A 数据的噪声也学进去。因此可以学到一个更精确的嵌入表达。

**② 注意力聚焦**

如果任务的数据噪声非常多，数据很少且非常高维，模型对相关特征和非相关特征就无法区分。多任务学习可以帮助模型聚焦到有用的特征上，因为不同任务都会反应特征与任务的相关性。

**③ 特征信息窃取**

有些特征在任务 B 中容易学习，在任务 A 中较难学习，主要原因是任务 A 与这些特征的交互更为复杂，且对于任务 A 来说其他特征可能会阻碍部分特征的学习，因此通过多任务学习，模型可以高效地学习每一个重要的特征。

**④ 表达偏差**

MTL 使模型学到所有任务都偏好的向量表示。这也将有助于该模型推广到未来的新任务，因为假设空间对于足够多的训练任务表现良好，对于学习新任务也表现良好。

**⑤ 正则化**

从机器学习角度来看，对于一个任务而言，其他任务的学习都会对该任务有正则化效果。

**02**

**多任务经典模型结构**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejySy9R1DJZaia4UXhtBc6O2quVrKgMzWicHgRjOibnhzzWjHhnR66AbGRog/640?wx_fmt=png)

推荐领域中经典的多任务模型包括 **ESMM 系列和 MMOE 系列**。

**1. ESMM 模型**

ESMM 系列使用点击信号（CTR）和点击后信号（如点 赞、收藏等）来解决转化率样本稀疏问题。该系列主要是 share bottom 的结构，底层的基础特征 user embedding 和 item embedding 都是共享学习的。常规的 share bottom，分别学习 CTR 和 CVR 任务，而作者认为是 CTR 跟 CVR 不在一个样本空间，CTR 是从曝光到点击，CVR 是从点击到转化，那 CTR 和 CVR 就不是在同一个样本空间，这样整个学习可能会带来一定的偏置。而 ESMM 的改进方式就是同时学 CTR 和 CVR，这样就转变成了一个是曝光到点击，一个是曝光到转化，整个的样本空间是一致的，可以保证推荐系统的离线训练和线上推理两个过程样本空间的一致性。整个模型比较大的收益就是来自于这样一个 share bottom，即底层 embedding 的共享。

**2. MMOE 模型**

MMOE 系列，与 SNR 和 PLE 都属于一大类，它们使用专家子网络的多门混合对多任务学习进行建模，在子网络的粒度上提供有限程度的共享。比如对于任务 A 和 B，它们在 Export 0 上共享得更多，Export 1 上共享得更少等类似这样的操作。

**03**

**一种基于神经元级共享的 CTR、CVR 多任务联合预估的方法**

**1. 模型结构**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyVEjfIVC7mlh4Toe3c3vTWgdUOiahHmJ0Hmr2JI5Fb3y1XjCfOVpsMUA/640?wx_fmt=png)

本文的工作启发来自于彩票假设理论，即一个随机初始化的网络包含一个小的子网络（中奖彩票），当迭代训练时可以与原始大型网络的性能相当（2019 ICLR 最佳论文）。我们在 base model 上通过迭代幅度剪枝， 自动提取 CTR 和 CVR 的 mask，每个任务的 mask 仅用于自身任务，也就是说交替训练 CTR 子网络和 CVR 子网络，每个任务只更新其对应子网的神经元权重。最后通过原始模型（左图）和 mask（中间）之间的哈达玛乘积生成最终模型（右图）。

这种共享和任务特定表征的方式准确响应了典型的多任务学习范式，它试图最大化共享特征，同时减少冲突。由于自动地学习了掩码/子网络 ，避免分析网络的哪一部分应该共享，哪一部分有冲突 。

**2. 训练推理**

我们的 CTR 和 CVR 任务拥有相同的 base 网络 sNET ，利用这个 base 网络来进行迭代训练，获得每个任务（不同 task\_id）特定的子网络。对于 CTR/CVR 任务：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyzAqhG2d2OEibW73EEPAeEukAhEypw97MA6MnelricCalhz9cHWBfB2Lw/640?wx_fmt=png)

**① 在初始阶段，**我们给 weight 矩阵设计对应的 mask 矩阵 mask[task\_id][0]，初始化为全 1 矩阵。

**② 接着**我们进行迭代训练，将 weight 和 mask 做 mask 运算。每训练一个 epoch，我们将 weight 元素按照绝对值进行排序，减去最小的 p% 权重，即将对应 weight 位置的 mask 设置为 0。

**③ 继续**训练一个 epoch，由于这部分 weight 的 mask 设置为 0，该部分 weight 便没有激活。使得前馈和反向传播阶段该 weight 失效。在剩余的 weight 中减去 %p 的权重，直到达到设置的迭代次数和剩余参数率。

④ 根据每轮选代完的测试结果，我们选择性能最好的 masks[task id][best]。

得到这样一个 best mask 之后，就可以开始正式地去进行 CTR、CVR 的一个训练。重新初始化 sNEt，根据 task\_id（CTR 或 CVR），然后加载对应的 mask，就得到了对应的子网络，再训练这个子网络。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyFGwianVIaNtLIdyw6IJ6s6BOAJaQBawO7rCPXkzneyians6KzvK7Dvbw/640?wx_fmt=png)

在训练剪枝过程中，我们发现并不是用很宽很大的网络效果就更好，适当减少神经元的数量对于 CTR、CVR 任务都是有提升效果的。当然如果删减得太多，效果自然也会下降。

**3. 实验结果**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyw9g7gWMYhh2Go5Y0x15BvHiaTxxeWPyrLwfFSjEeOM5Qng2XSsOicDDQ/640?wx_fmt=png)

本文使用的损失函数是 CTR 损失函数和 CVR 损失函数的加权融合，其中权重是超参数；

线上打分公式主要是 CTR、CVR 和视频时长的乘积，其中 α、β 等均是超参数；

数据集使用的是一个较小的短视频场景，用户量一千万左右，视频一千一百万左右。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyibWCJ4zs2g1cw4TQhRbw3icoPQfsldoLTeDDUK7uCfm1Obo1U5KWoL6Q/640?wx_fmt=png)

对于离线实验，其中 hardsharing model 这是最经典的 share bottom，对于 CVR 任务 MSE 大概是 0.136，它大概能让 MSE 下降 0.9%；我们工作的一个基本结构是 S\_weight，它能让 CVR 在 MSE 下降 3% 。

线上实验，包括 4 组实验：

① 单任务的 CTR \* 单任务的 CVR\* 时长；

② 单任务的 CTR \* share bottom 的结构学 CVR\* 时长；

③ 单任务的 CTR \* S\_weight 的 CVR（就是我们的工作）\* 时长；

④ S\_weight 的 CTR、CVR \* 时长。

从浏览效果来看，单任务的 CTR \* S\_weight 的 CVR 效果是最好的，这也是符合预期的一个结果，因为 CTR 的样本一般是比较充足的。但是如果用 S\_weight 的 CTR、CVR 联合上线，可以看到它的 CTR 还有 CVR 的指标上效果会有一点提升。我们的推断是这两个任务有一定的协同性。

我们的方法与单任务模型和经典的层级共享模型进行了比较，分别证明了 CVR MSE 的相对减少 3.78% 和 2.48%。

**04**

**总结**

① 我们是业界第一个尝试应用神经元连接级共享来解决 CVR 多任务学习的工作，缓解了共享冲突问题，自动学习共享的神经元权重，与之前的粗粒度子网络/层级共享方法相比，这是一种范式转变。

② 我们的方法部署到了某亿级用户视频线上系统中，实现了比单任务方法显著的性 能改进。证明了其在实际工业应用中的价值。

③ 该方法可以很容易地推广到推荐系统中的其他任务中，例如点赞率、评论率等。

④ 相关工作已经加入 onerec 项目：https://github.com/xuanjixiao/onerec。

**以上就是本次分享的内容，谢谢大家。**

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/EBaibcQicPxgzjlMlhID01vQnAmcEJXejybd1J7ia7RLlb0GqkJTX4iagVDtK2lrIhItnlqgtphkqqnJzD3fnQ7Chw/640?wx_fmt=gif)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgzjlMlhID01vQnAmcEJXejy2SLU0mBIJuLxo7gSK2qNDPuIqicnlHKCZ1N5ibibbUTGBhgCrCUTyIvyQ/640?wx_fmt=png)

分享嘉宾

INTRODUCTION

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyAj2WGTCQhVibqibnzibS9CZ5Qpqpn6b93WcEfGqx8vkeS3IN0UU3tzTxg/640?wx_fmt=gif)

陈华斌

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyAj2WGTCQhVibqibnzibS9CZ5Qpqpn6b93WcEfGqx8vkeS3IN0UU3tzTxg/640?wx_fmt=gif)

阿里巴巴

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyAj2WGTCQhVibqibnzibS9CZ5Qpqpn6b93WcEfGqx8vkeS3IN0UU3tzTxg/640?wx_fmt=gif)

**算法工程师**

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/EBaibcQicPxgzjlMlhID01vQnAmcEJXejyAj2WGTCQhVibqibnzibS9CZ5Qpqpn6b93WcEfGqx8vkeS3IN0UU3tzTxg/640?wx_fmt=gif)

中科院自动化所硕士。曾在腾讯视频实习，现任职于淘宝推荐算法团队。

**今日推荐**

🔥 零距离对话全球顶尖技术专家、学者、业界领袖，与国内外技术同行探讨：大模型、生成式AI、敏捷数据分析、智能湖仓、数据安全与合规等热门话题

⏰ 活动时间：6/27-28 9:00-17:00

☕️ 活动地点：上海·世博中心

🎁活动亮点：

* 31个主题论坛，覆盖当下热点与前沿技术
* 覆盖汽车、金融、游戏、医疗、电商等行业
* 多个互动项目，现场体验类ChatGPT应用的快速构建

👇扫码报名参会：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhsPaGcoGERfZgbzG6KBJwn8DZ8MjIgiazgaQau4hZs7a43z4BGJo5amia2UOnsophxDSeXGR0ILJ1A/640?wx_fmt=jpeg&wxfrom=5&wx_lazy=1&wx_co=1)

**\*PS：报名后扫描下方二维码进群，第一时间了解峰会动态、官方抽奖信息，活动当天到场签到，还可领取DataFun独家《数据智能知识地图》1份（印刷版）！**

![](https://mmbiz.qpic.cn/mmbiz_png/vrk53t8Tibicp1NMbzB6kHXXGl6jreCQ1Zdx61vN2x6Q8NNLakMv4cibsVFy9nA9ZGF7TKibhyt3gnKoZTQOwqtDKg/640?wx_fmt=png&wxfrom=5&wx_lazy=1&wx_co=1)

👇点击**“阅读原文”**亦可报名参会～