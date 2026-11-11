---
title: 'OCPC   广告算法在凤凰新媒体的实践探索'
company: 凤凰
tag: 广告
date: 2019-09-25
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247494020&idx=1&sn=df65908cdaf57d02eee8280d86d66949&chksm=fbd75be8cca0d2fe2d69d89a70eced34ba467acbf26fefe1bf40edea36a07e76406612383fd5&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGMXqicg3SKQa9748uDHGIoSDohnc79iaHGDsEIWiawWia3Iic6QRrwcD8NDw/640?wx_fmt=png)

分享嘉宾：凤凰新媒体广告算法团队

编辑整理：陈道昌

内容来源：2019 DataFun Live 01

出品社区：DataFun

注：欢迎转载，转载请在留言区内留言。

**导读：**广告算法在优化点击率和竞价机制等提升平台收益的过程中，如果不能保证广告主转化的质和量就会影响到平台生态的稳定发展，因此在 CPC 的基础上，我们探索了 OCPC 模式，并在实际中成功应用。

本次分享的题目为 OCPC 广告算法在凤凰新媒体的实践探索，主要内容包括：

* 背景介绍
* CVR 预估
* 二价机制和智能出价
* OCPC 算法
* 技术架构

**▌****背景介绍**

**1. 凤羽简介**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGJ6Yygqr2rDFMSNiclCbdSvZ5pQjqtkib6Y0ib2RyxbKbSDWFqE9T4Xc0Q/640?wx_fmt=png)

凤羽是凤凰卫视程序化广告变现优质品质曝光平台，汇聚了凤凰网、手机凤凰网、凤凰新闻客户端、凤凰视频客户端等多项业务，每天为凤凰网提供20亿次优质流量的曝光。

**2. 什么是 OCPC**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGYTQOtPZ5eyNgZcNuFJ0veNpvZsHj6lfYfxfefnPrpro1hX6liayNHQw/640?wx_fmt=png)

OCPC 是效果广告最近两年比较好的业务模式，广告主关心的还是成本 ROI，同时能跑量。 

CPC 按点击付费，广告主基本都接受这种付费方式。本质上，广告主会根据凤羽的 CPC 消耗，核算他的转化成本。所以广告主为了优化这个成本，他可能调低 CPC，但是抢不到量；选择做人群、时间定向，基于经验论或者数据反馈；或者跑人群包等等。

相比传统的 CPC 业务效果广告，OCPC 本质上，是通过算法把优化工作替广告主做了。而且由于有更好的手段，所以效果更好。OCPC 还是按照点击付费，但是 OCPC 一般情况下，客户不再出点击价，出的是目标成本价 CPA。OCPC 一般分第一阶段和第二阶段。第一阶段用于数据的冷启动，第二阶段用于积累数据。

**3. 定义问题**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYG61RghdQUWEN043MPJiburOw8NyYPAxGWhTuMJsa8AbLebGXT1XGObtQ/640?wx_fmt=png)

CPA 有两个目标：

目标1：转化率上升，转化成本下降， ECPM 上升，从而提高客户转化率。

目标2：成本稳定，消耗稳定，从竞价机制上提出优化点。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGzS4RqGiaqodhW3rqib3Y9YeZn7ibvb40dTdiaQyeicgicQlMggoMB31GF6HQ/640?wx_fmt=png)

相对应的，我们的目标是在客户指定成本的情况下，每天相对稳定的跑量。

我们提出了三种优化手段：

* 二价机制，二价机制指的是出价格抢这次的流量，只需支付第二名的价格。
* 智能出价，相比二价机制的自然分配，智能出价是一种流量的更积极分配。会根据目标，进行智能的出价操作。
* CVR ( 转化率 ) 预估，CVR 预估是整个阶段的基础，问题是 CVR 预估的样本非常稀少，需要做到多准确？

**▌****CVR 预估**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGCjavD10nlUz99UyOmxxk1Fq2aThgNyd2jmClrnfibFe1iaRcIybrGMkg/640?wx_fmt=png)

由于在数据非常稀少的时候，很难做出准确和泛化的 CVR 预估，而 OCPC 可以完成。因为我们用到了二价机制，抢到的流量是第二名的价格，不过只要 CVR 的偏差可控，比如小于二价的 Gap，也能获得不错的成本控制。第二层面是 CVR 预估虽然有不准的成分，但我们可以通过智能出价来做经验控制，比如拿转化率高的部分，也可以把成本降下，从这个角度分析，CVR 预估不用特别准确。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGArEia2QqRpL4VvCSyia1JpSLl2Ja4LicvKTjH6tyKAZj2PmSh4pYyUia3Q/640?wx_fmt=png)

关于 CVR 数据稀疏的问题。新的客户在冷启动阶段的转化不到100个，使用不到100个的转化建立用户的转化率的预估，这个问题是比较困难的。其次，点击转化率与曝光转化率其实不一致，这是一个漏斗序列，先曝光再点击再转化。

如果用点击行为样本训练模型行预估点击转化率，在线上会出现数据不一致的情况，在数据样本比较小的时候，会有很大偏差。曝光转化率解决了样本不一致的问题，但是考虑到数据稀疏，建模后偏差过大，这种方法被弃用。

做过数据分析，发现点击率与转化率存在相关性，可以考虑将 CTR 与 CVR 一起联合训练联合建模，它们肯定有很多特征信息可以共用的。比如通过 weightedLR 做 loss 改造，在推荐等其它项目中有过不错的效果，后续可以一试。

最后，是构建一个模型还是多个模型？是分一个客户建模还是考虑同行业同目标一起建模？关键还是在于业务目标和数据情况：

OCPC 追求单个客户的完成率，要为单个客户做 ROI 达成和算法归因，同时各个客户之间的差异很大，这和全局最优化不一样。从这个角度出发，在考虑很多方法之后，决定为每个客户单独建模。所以会有很多模型，有很多工程上的版本控制，会考虑泛化与工程准确度的需求，我们会为相似的用户做一些先验的平滑，来提升准确度。后续 OCPC 的客户非常多的时候，可以考虑同一个行业，同一转化目标的类型一起建模，数据的稀少情况也能得到一定缓解。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGT5WP6Via9zWSgicI62Fw1tbYBLf2NeEFDMR8OyNib629ILicKNfwxeVJfA/640?wx_fmt=png)

我们目前的 CVR 预估的方法，借鉴 yahoo 的论文，采用一种在线学习的基于特征子空间的 bayes 平滑算法，并融合试探、分裂策略。步骤分为以下五步：

① GBDT 训练得到若干颗树，形成多种特征子空间 ( tree )；

② 不同广告采用自己样本驱动每个子空间 ( tree )，计算 CVR ( beta 分布 )，判断置信度；

③ 在线学习：进行 CPC 模式的退化；

④ 在线学习：分裂子空间和试探子空间；

⑤ 相似广告会做贝叶斯平滑，提升准确度提升泛化性能。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGEjhdWd70OibKEuvRSfIoBEXRYK1gj6BSmVr05J7XwziamDorZH2AfC8Q/640?wx_fmt=png)

下面是关于算法的一些细节，简单的说用 GDBT 对样本和特征做随机采样，然后用随机采样出来的多对异构的多棵树，从里面提炼出各个特征子空间，然后对这些特征子空间，每一个广告、每一个客户，我会单独用自己样本探索这些特征子空间，在里面做置信度判断、CVR 预估、试探、分裂策略，来保证 CVR 的准确性和泛化性能。整个算法在实现的过程中还是存在一些问题的，大概列出了以下几个问题：

① 为什么不采用 GBDT 的预估？

希望通过在线学习和置信度控制，来得到一个可以业务进化的有效模型和策略；但是，GBDT 仍然是一个有效的预估，可以考虑结合；

② GDBT 如何构建树？选多少颗树？

原生办法利用 LightGBM 特征的采样，第二种方法是人工做交叉，去选取特征，在实践中应该选多少棵树，也是看具体业务情况。我们的经验是一般用16颗树。

③ 如何多颗树的多个子空间给出的 CVR，组合出新的 CVR？有以下的几种做法：

-> 取平均值。

-> 参考每个子空间 CVR 的方差，给出加权平均 ( yahoo )。

-> 参考每个子空间 CVR 的方差，子空间颗粒度做加权平均，子颗粒太大，方差就大，偏差也会大。

-> 取 CVR 的最大和最小，最大值不推荐，训练模型是右偏的，本来是高估的，用最大值高估现象更严重，会高估用户成本，最小值想对安全，但是最小值可能跑不出量。

在后续的实践中，我们发现做 LR 集成还是一个更通用的模式。精度会高一些，同时可以将多个相似客户一起建模，提升一定的泛化能力，也减少了模型数量。

④ 多颗树中，有的子空间置信，有的不置信，如何选择试探、退化等策略？

-> 冷启动阶段数据太少，要退化到 CPC 模型，平滑了 OCPC 的第一阶段和第二阶段；

-> 相似广告的子空间数据要做贝叶斯平滑，做 MLE 求解；

-> 试探策略，计算置信上界，乐观估计，促使拿量；用置信上界。系统中有一个试探系数来控制。实践来看，当采用适当的试探系数时候，客户的成本和平台的 ECPM 能有一个双赢。所以这个试探系数可以作为一个策略学习部分后续优化。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYG6LqAHbiaafyKu4djkCudy326f0dYiahmSABiacttibr0cVsTBlbrd9ib3lg/640?wx_fmt=png)

可以通过在线学习，进行快速试探。在线学习的一个很大的优点是可以提升准确度：

一开始样本特别稀少，CVR 预估 bias 很大，需要快速学习分裂，找到更置信更细化的子空间。另外，当竞价环境出现变化的时候，CVR 预估的偏差会大大增加，导致 OCPC 失败，比如在节假日。

比如，在正常情况下，可以拿到左边完整的特征分布的流量。但是当竞价变得激烈之后，同样的模型和策略，我只能拿到转化率很低的那部分流量，实际 CVR 的偏差就会很大。这是很失败的一个案例，在线学习能大大提高 CVR 的准确度。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGZIuDoScrcic75U3PdD5icMhrrJBUZ9BhX9lbRMG27EoPvnAXVrD3EFZg/640?wx_fmt=png)

试探策略可以加快业务进化和 CVR 收敛。基于试探策略，将流量分配给不置信的子空间。它有两点好处，如下：

① 节省 OCPC 的试探弹药。将预算更多投放给可能有高转化率的子空间；能加快 CVR 预估的收敛速度，业务快速进化到第二阶段；

② 试探有一个刷新人群的效果；偏向于给新人群。

同时，实践中发现，试探能做为一个有效的策略，来影响最终的多目标达成，所以还是一个很好的智能调价 strategy。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGbCqEB1S6VkzWoyOGDpeAFu9yyInibpXvdMAib9ZYyYGSZVkUMMW9yUYA/640?wx_fmt=png)

试探策略我们采用的是推荐常用的 UCB，为了避免样本过少，所有做了平滑，取威尔逊的置信上界。这样如果特征空间不置信，我们倾向于给它足够多的试探，就可以让客户第一阶段能更快的收敛。实际中，如果直接用置信上界去试探，由于太高的 CVR 值，可能出现跑量太快的异常情况。所以 CVR 预估值也不能太高，需要做一个上界的约束。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGTU7TVrM2ubbtdIEK0tjWRQbgXLvmcDBWLSy0H6FvL19O5kgTicazkiaw/640?wx_fmt=png)

在线学习有一个很明显的问题，转化其实是有很强的样本的延迟，不同的转化目标，不同商品，他的转化周期不一样。比如说 app 的下载转化是很快的，app 的激活可能要延迟好几天，我们在做在线学习的时候需要快速收敛，我们会以小时为单位对数据进行校验，然后开始做实时的返回学习。但是我们会对历史数据做指数平滑，同时我们会每一天、每两天、每三天为窗口的这段时间的数据重新，再重新做下全天的求证，样本延迟带来的偏差。

同时可以求解客户转化的概率的延迟分布，针对一个小时内的样本做权重上的求证。样本延迟还会带来一个问题，就是转化归因的问题，把转化归因到某一次点击上。比如三天某一个用户点击了广告并下载了 app，但是今天才实行了激活，这样的激活的转化是应该归因于三天前的点击，还是现在这一次的点击，这其实也需要自己取舍。

**▌二价机制和****智能出价**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGJ230kDupIWcB2mjJbazfpADvGIGEsyuyicSiaCkp653jpibkEnwCUc3yQ/640?wx_fmt=png)

二价机制：在实际的过程中，OCPC 客户成本的波动性相当大，同时消耗非常不稳定，根本原因是 CVR 预估做不了太准确（如果可以做的准确就有更简单的解决方案了）。我们会采用智能出价，在二价基础上会更积极，能帮客户在高 CVR 上抢量，低 CVR 上丢量。智能出价带来了更稳定的成本ROI和客户消耗，并平衡平台和广告主收益。

智能出价：在多个客户情况下，智能出价变成一个组合优化的问题。可以参考阿里论文中贪婪方法求解，其中论文中的时间复杂度还可以优化，可以使时间复杂度降低 log(N) 倍。

智能出价是一种很有效的一种手段，但是核心还是 CVR 预估要准确，并需要找到一个合理的 CVR 期望。

关于 E(cvr) 的求解，阿里和新浪据说会采取用户的多个竞品对应极限的转化率。最好有多个竞品，去掉多个竞品中的最大值与最低值，然后取平均比较准确。但是在实际业务开展的过程中，尤其是 OCPC 没有足够竞品的时候，我们采用相对低效的手段，我们取客户本身已经近似的广告最近若干次的 CVR 预估，去除最高值与最低值的10%并取平均，这是一个低效的策略。

我们还在探索基于强化学习的动态调价。但是这个需要有很大的流量来做支撑，所以不太好建模。

**▌****OCPC 算法及架构**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGtI6eJAJS6icJLnIwTl2POl5nk0keu84LiaJwwkw0Zfhka730qFzDHLNw/640?wx_fmt=png)

总结下 OCPC 算法策略的特点：

① 业务进化，包含试探和分裂的策略，我们并没有明显的 OCPC 第一阶段；

② 在线学习，可以有一个在线的校准 ( Calibration ) 效果，可以一定程度上降低偏差；

③ 在小样本的情况下，通过评估置信度，在准确和泛化中找到一个平衡，人工干预整个算法的进程；

④ 整个算法有试探、分裂等策略，在实践中有一个很快速、很明显的优化链路。

这是我们截取的客户的案例，经过短短的一周，用户的 CPC 的消耗和成本就能快速稳定下来，蓝色是 CPC 跑出来的曲线，黄色是 OCPC 跑出的曲线，可以发现 OCPC 比 CPC 的成本要低30%左右，同时 OCPC 的波动性也大大降低了，整个算法收敛的还是很快的 。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGU7sp3JiaPczBz3s8Qq9xMTwskNvSZPIC9MCmNwHQ7bOz5kxsApMAicGA/640?wx_fmt=png)

接下来谈谈 OCPC 其他的细节，除了对算法进行常规 AUC 评测、OE 评测和偏差评测之外，OCPC 还有很多的策略、方法和参数。如果都在线上开启 AB 测试，成本太高；另外，线上测试样本不足，用户的转化可能只有10几个转化，用10几个转化做 AB 测试，在统计上难以置信。

因此，我们采用虚拟测试的方法进行测试。我们会对用户一段时间内历史的竞价数据进行随机采样，把数据完全复原。然后，基于虚拟的竞价数据，针对我们新的方法和策略进行虚拟测试，观察采用新的算法，成本能否得到优化。但是会有一个问题，这种方法无法完全对等。比如客户的部分流量竞价没有成功，所以没有曝光，这部分流量的后续点击、转化概率其实都是未知的。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYG3douyeoyU1cgu3XicEhhp8eyt5HFgPqKX1zKAibpkk0OrTec6icL78hiaA/640?wx_fmt=png)

完成上述所有的手段后， 我们必须承认算法的不足，此时需要加入人工干预。干预手段包括：

① 对于已经转化的用户应该去掉，作弊的用户也去掉；

② 如果客户效果不好，可以采用刷新，促使用户流转起来；

③ 适当补量，对有问题的客户，可以通过人群补包补量，其他APP的流量引入；

④ 运营根据经验来做一些临时策略。

根据算法的表现，比如结算的 CPC 变低，可能是 CVR 预估偏低，这样的情况下可以做一定的修改。所以我们是用进化的算法+人工干预来保证每个客户的 RI。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgJ5UWF1W0lLjsBiaGJHiarYGxvoibI8VNCFMCDFpIxPeRIU8MC4JmrlGKxGyVMljIY33rIibNVIXQyqA/640?wx_fmt=png)

最后是我们 OCPC 的技术架构落地。整个过程的关键是在线学习，融合了试探、分裂、净化的策略，在线追求好的工作链路，需要做些监控保证工作正常，可以构建虚拟侧环境，在线上引入 AB 测试，整个架构相对简单，预估部分与 CTR 工程相似，包括特征工程、模型。

**▌****未来工作**

关于下一步的改善方案：

① 数据稀少，通过落地页的停留时长，来改善数据的稀疏性，停留时长与转化率有很重要的关系；

② 提升现有算法精度和泛化能力。考虑加入 GBDT 的预估值；采用特征和样本，提高 tree 的异构性；

③ 尝试采用强化学习的算法。对状态、动作空间都做一些限制，并引入确定的概率。这样在流量不大的场景下，是不是也可以求解。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhYUUTnAicmDgz064WIYEsbXHSGbTibHibFbx9W2nOrUDAFsNvia7o6XicyicpwY5w2Q2IrgTd2jstd5mPg/640?wx_fmt=png)

**文章推荐：**

[微博广告策略工程架构体系演进](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247493747&idx=1&sn=3288e75a42a8e93bc7ce34b47b811b9b&chksm=fbd75a1fcca0d3092046e1c3b0d961ef99edc8323426fdd78eae3693119a726328db7f0dd246&scene=21#wechat_redirect)

[Hulu：视频广告系统中的算法实践](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247493025&idx=1&sn=7760d40dc9c3e1d6786a180bd871b62b&chksm=fbd757cdcca0dedb87c7ee1dc74c0b055b917a92e83a26b9583cc5caac7cfce16ea3afbdd028&scene=21#wechat_redirect)

**DataFun：**

专注于大数据、人工智能领域的知识分享平台。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhicE4hS5liayK0vWlwTanNgy003rMCMPvRlktwUjR2m8icG0MbH1ByNF7RuLdibwXKsA424lHOvaIHWw/640?wx_fmt=png)

**一个「在看」，一段时光！****👇**