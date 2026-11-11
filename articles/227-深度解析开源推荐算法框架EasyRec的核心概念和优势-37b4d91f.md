---
title: '深度解析开源推荐算法框架EasyRec的核心概念和优势'
company: 阿里
tag: 工程相关
date: 2022-04-26
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247569807&idx=2&sn=8d133978b9c78529d6c83c756c4a242d&chksm=fbd663e3cca1eaf58e2fe5d7c88430ada4ffac92e7a96082906c03666d3fdc28548c59c1078f&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/lAStFsJ0Pm36LPkTamqb0m4Ot0Lpm9wMaLwl995z1lhoHib6lqybIqI4LIJZcs3z1uctw159bXibiaaWMJwSvt3nA/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhDyFwhQQibvFyAElC95zfv6I7GPTuuFCRGIStK68o6tGic1YuuHHQyn0sr8aBya2Lic4bqKvZbQEicfw/640?wx_fmt=png)

文章作者：程孟力 阿里巴巴

内容来源：阿里灵杰@知乎

**导读：**随着移动App的普及，个性化推荐和广告成为很多App不可或缺的一部分，它们在改善用户体验和提升App收益方面都产生正向作用。深度学习在搜广推领域的应用也已经非常深入，并且给各种场景的效果带来了巨大的提升。针对推荐流程的各个阶段，业界已经有很多的模型，这些模型大部分也有开源的实现，但是这些实现通常散落在Github的各个角落，其数据处理和特征构造的方式各有差异。

如果我们想要在一个新的场景里面应用这些模型，通常需要做比较多的改动：

* 输入的改造，开源的实现的输入格式和特征构造通常和线上不一致，适配一个算法通常需要1-2周左右的时间，还难免因为对代码的不熟悉引入bug，如果要尝试5个算法的话，就需要5倍的改造时间。如果算法资源有限，这时候是不是就要忍痛割爱，放弃一些可能有效果的尝试了？
* 开源的实现很多只是在公开数据集上取得了比较好的效果，在公开数据集上的最优参数也不一定适合实际的场景，因此参数调优也需要较大的工作量；有时候效果不好，并不是因为方法不行，而是选的参数不太好。如果没有系统化的调参方法，很多算法也就是简单试一下，没有deep explore，哪来对算法的深入理解呢? 为什么看似简单的改进，你没有能够发现呢？为什么你也尝试了类似的方向，但是没有搞出来效果呢? 效果通常都是用算力和数不尽的尝试堆出来的；
* 开源的实现用的是TensorFlow 1.4，而线上用的TensorFlow 2.3，好多函数的参数都变掉了(此处心里是不是想骂Google一百遍，当初信誓旦旦说好的API不再变呢); 很多开源的实现由于没有在实际场景中验证过，所以其可靠性也是存疑的，可能就会少了个dropout，少了一个bn，效果相差甚远；
* 费了九牛二虎之力把模型效果调好了，发现上线也会有很多问题，比如训练速度太慢、内存占用太大、推理qps跟不上、离线效果好在线效果贵等等。遇到这么多问题，你还有精力去做你的下一个idea吗？你还能斗志昂扬，坚持不懈地去探索新方向吗？

这些问题搞得我们心有余而力不足、天天加班到深夜、不知何时是个头：想要验证一个简单的idea都要使出九牛二虎之力。所谓天下武功，唯快不破，对于搜广推领域的算法同学来说，尤其如此：通过快速迭代才能验证更多的想法，发现更多的问题，找出最优的特征和模型结构。速度慢了的话，可能你的模型还没调好，业务目标就变了，前端的布局也改了，你的业务方可能都不相信你了，你也就没机会上线了。

说到这里，我们的诉求就比较明确了，我们就是想少写代码，甚至不写代码就能验证我们的想法。针对这些问题和诉求，我们推出一个全新的、一步到位的推荐建模框架，致力于帮助大家解决在推荐建模、特征构造、参数调优、部署等方面的问题，让大家少写代码，少干重复的没有意义的脏活累活（这些EasyRec都承包了），少趟一些坑少踩一些雷（这些EasyRec都替你趟了），让大家能够快速上线验证新的idea，提升推荐模型的迭代效率。

**01**

**优势**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRncYau1ap3zpIDrM2RqeOcTAmQ0Jq64iajgmaQJNZgJwAjfrpiclOR6FQ/640?wx_fmt=png)

和其他建模框架相比，EasyRec在以下几个方面具备显著的优势：

1. **支持多平台和多数据源训练**。

* 支持的平台包括: MaxCompute（原ODPS）、 DataScience（基于Kubernetes）、 DLC（deep learning container）、Alink、本地；
* 支持的数据源包括: OSS, HDFS, HIVE, MaxCompute Table, Kafka, Datahub；
* 用户通常只需要定义自己的模型，在本地测试通过后，就可以在多种分布式平台上进行训练。

2. **支持多种TensorFlow版本**(>=1.12, <=2.4, PAI-TF)，能够无缝地对接用户的环境，不需要对代码做迁移和改动。

3. **支持主流的特征工程的实现**，特别是显示交叉特征，能够显著提升效果。

4. **支持HPO自动调参**，显著降低了用户的调参工作量，并在多个场景中提升了模型效果。

5. **实现了主流的深度模型**，覆盖召回、排序、粗排、重排、多目标、多兴趣等。

6. **支持EarlyStop, BestExport**, 特征重要性，特征选择、模型蒸馏等高级功能。

**02**

**架构**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRt5kuWAbXSTib5iaCAHhUG7K9q5gCXHvqtGVXS76oSqTywsXf3eKFCYLw/640?wx_fmt=png)

EasyRec建模框架整体上是基于Estimator的数据并行训练方式，通过Parameter Server的结构支持多机多卡的训练。EasyRec的主要模块包括输入、特征构造、深度模型、Loss和Metric，每个模块都可以自定义。

针对用户在用TF进行训练可能遇到的多种问题，如worker退出失败、使用num\_epoch evaluator无法退出、auc计算不准确等，EasyRec做了深度优化。

针对AdamOptimizer训练速度慢、异步训练慢机、hash冲突、大样本空间负采样等问题，EasyRec结合PAI TF（PAI优化过的TensorFlow）和AliGraph也做了深度优化。

**03**

**模型**

EasyRec内置了业界先进的深度学习模型, 覆盖了推荐全链路的需求，包括召回、粗排、排序、重排、多目标、冷启动等。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRALqwwibud3zIQazxic2JmnoN6pNpFbQ3qwd3esS8LqGRyfZAeutDhr0A/640?wx_fmt=png)

同时EasyRec也支持用户自定义模型。

如下所示，在EasyRec里面实现自定义模型，只需要定义模型结构、Loss、Metric三个部分，数据处理和特征工程是可以直接复用框架提供的能力的，因此能够显著节省用户的建模时间和成本，能够将精力focus在模型结构的探索上。针对常见的模型类型如RankModel、MultiTaskModel等，Loss和Metric部分也可以直接复用父类的定义。

```
class CustomModel(EasyRecModel):  
  def __init__(self, model_config, feature_configs, features,                labels=None, is_training=False):      super(CustomModel, self).__init__(model_config, feature_configs,                                         features, labels, is_training)      # build wide features from feature_group with name "wide"       self._wide_features, _ = self._input_layer(self._feature_dict, "wide")      # build deep features from feature_group with name "deep"      self._deep_features, self._deep_feature_lst = self._input_layer(          self._feature_dict, "deep")  
  def build_predict_graph(self):      self._prediction_dict["logits"] = DNN(self._deep_features) + \          LINEAR(self._wide_features)      self._prediction_dict["probs"] = \          tf.nn.sigmoid(self._prediction_dict["logits"])      # it is necessary to return the prediction_dict,       # which is required by the framework      return self._prediction_dict  
  def build_loss_graph(self):      # build losses      loss = tf.losses.sigmoid_cross_entropy(self._labels[0],                                              self._prediction_dict['logits'])      self._loss_dict["custom_loss"] = loss      return self._loss_dict  
  def build_metric_graph(self, eval_config):      # build auc metric      metric_dict = {}      metric_dict["auc"] = tf.metrics.auc(self._labels[0],                                           self._prediction_dict["probs"])      return metric_dict
```

**04**

**自动调参和自动特征工程**

EasyRec自动调参接入了PAI AutoML自动调参的能力，实现了对多种参数的自动调优。

EasyRec里面定义的任意参数都是可以搜索的，常见的参数包括hash\_bucket\_size, embedding\_dim, learning\_rate，dropout, batch\_norm, 特征选择等。当你对某些参数拿不准时，就可以启动自动调参来帮助你寻找最优的设置；通过自动寻优得到的参数通常会比拍脑袋设置的参数要好，有时候还会带来意外的惊喜。

特征工程通常是提升推荐效果的关键，做高阶的特征组合通常有助于提升模型效果，但是高阶组合的空间非常大，无脑组合会导致特征爆炸，拖累训练和推理的速度。

因此，EasyRec引入了自动特征工程(AutoFeature)的能力，自动寻找有提升的高阶特征，进一步提升模型的效果。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRLkL7WL7qKuG4C47MzFh395NwVzRzarQVGlagqQGg9QI4kMqTOoWf0g/640?wx_fmt=png)

**搜索结果（top5）：**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRocKCBKnHsYnbricScMicYnIehZzFR2xBDibdr5b3RXYSIH60fqmCibiagBQ/640?wx_fmt=png)

**05**

**模型部署**

EasyRec模型可以一键部署到PAI EAS环境，也可以通过tf serving部署。

为了提升inference性能，EasyRec引入了PAI Blade的能力做placement优化，op fusion，子图去重等功能，通过上述优化qps提升30%以上，rt下降50%。未来还将引入FP16的功能，进一步提升inference性能，降低memory的消耗。

为了支持超大规模的Embedding，EasyRec对大模型做了拆分和op替换，将Embedding存储到Redis等分布式缓存里面，突破了内存的限制。从Redis获取embedding会比内存慢，通过对高频id进行cache等来降低对redis的访问来提升embedding lookup的速度。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRntXhfry3YgA2u0ExQOreKAvpmm00Nrvj439r6ekoW1npUxmSIAQx7w/640?wx_fmt=png)

**06**

**特征一致性**

特征工程是搜广推流程里面的关键部分，也通常是造成线上线下效果不一致的原因。为了能够在快速迭代中保持离线在线的一致性，通常采用的方法是线上线下采用同一套代码。

* **离线训练数据的构造流程：**

首先，构造user feature(包含实时和离线两部分), item feature和context\_feature；然后，join上训练样本(包含label)；最后，经过特征工程的jar包生成输入EasyRec的训练样本。

* **上线的流程：**

将user feature(离线部分)和item feature导入Redis、Hologres等分布式存储，推荐引擎根据user\_id和item\_id去查询对应的特征，调用特征工程的库进行加工之后，送入EasyRec模型预测。

在线部分的实时特征通常是使用blink、alink等支持流式计算的平台来生成的，而离线部分的实时特征构造有两种方式：离线模拟和在线落特征。

这两种方式各有优缺点：由于日志丢失等问题，离线模拟通常会和线上有少量的不一致；在线落特征如果要增加新的特征通常要等待比较长的时间才能攒够样本。我们的解决方案是在线将用户行为的序列落下来，然后离线通过相同的jar包来加工出各种统计特征，如1h/2h/../24h的点击次数。

在线特征工程对计算效率要求比较高，而计算量也比离线要大：

离线计算的样本通常是1个user配对m个曝光的item(召回模型的话，会增加一些随机采样的负样本), 而线上计算的样本是1个user配对n个item(n>>m)。在线计算如果采用naive的计算方式，将一次请求展开成n个样本分别进行计算，效率通常是跟不上的。不难发现其中user feature的部分做了比较多的重复计算，对user feature做计算效率的优化，能够显著提升线上的qps。我们结合淘系内部使用的Feature Generation模块做了深度优化，包括内存分配、字符串解析、重复计算消除、多线程并行计算等，在保证一致性的前提下，显著提高了计算的效率。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRSy6glAbsicY5y9NRp0dqKoLNMAxsamXZq5LP8UfN7e09oQrBDJ2iceaw/640?wx_fmt=png)

**07**

**增量训练和实时训练**

增量训练通常能够带来效果的显著提升，原因在于增量训练见过了更多的样本，对embeding部分训练地更加充分。

EasyRec支持从上一天的checkpoint restore，然后在新的一天的数据上继续训练。为了快速适应新闻、节假日、大促等场景的样本分布发生快速变化的场景，我们提供了对实时训练的支持。EasyRec通过Blink来构造实时样本和特征，并调用Feature Generation对特征进行加工，然后通过Kafka、DataHub读取实时的样本流进行训练。

实时训练的稳定性比较重要，我们在训练过程中对正负样本比、特征的分布、模型的auc等做实时的监控，当样本和特征的分布变化超过阈值时，报警并停止更新模型。保存checkpoint时，EasyRec会同步记录当前训练的offsets(多个worker一起训练时，会有多个offset)，当系统发生故障重启时，会从保存的offsets恢复训练。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPg93GiczkaQW4ABsibZRSyxhRB27mV5YHyctfSkDlLSokzickJq2Q0nz7uyF1qLiaiaOv5QsAD1mA5wDNg/640?wx_fmt=png)

**08**

**效果验证**

EasyRec在多个用户场景中得到了验证，场景中包括商品推荐、信息流广告、社交媒体、直播、视频推荐等。

以下是部分客户在他们场景中使用EasyRec取得的提升:

* 某APP广告推送: AUC提升1个点，线上ctr提升4%，资源消耗降低一半；
* 某大型直播APP: 基于EasyRec MultiTower模型AUC提升2%；
* 某大型社交媒体: 基于EasyRec MultiTower模型AUC提升6%，线上效果提升50%；
* 某大型电商平台：基于Easyrec DSSM模型，线上UV价值提升11%，UVCTR提升4%；
* 某短视频APP：基于EasyRec DBMTL模型，线上时长提升30%，+多模态特征进一步提升10%。

**09**

**最后**

最后，EasyRec已经通过Github开源：

github.com/alibaba/EasyRec

在此欢迎各位同路人共建，包括：丰富各个场景的特征构造，引入更多在实际场景中验证过的模型，提升模型离线在线推理的性能，等等。

在这个日益内卷的行业，我们希望能够通过这样一个开源的工作，形成合力，照亮我们共同的路。在这里，我们也像前辈xgboost致敬，希望这个工作能够像xgboost一样发扬光大，影响深远。

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

**免费福利：**

[互联网核心应用算法宝藏书PPT电子版下载！](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247567556&idx=1&sn=8c995fb7305a0712c855632d82bf2d22&chksm=fbd67aa8cca1f3be7c3a2c8b169d25e32313c41a6768a11113edb00750ac33cbac3f230c640d&scene=21#wechat_redirect)

[大数据典藏版合集PPT电子书下载！](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247567526&idx=1&sn=f334ffc73327460605d8c58eec0ef2c2&chksm=fbd67acacca1f3dc8a5d2f88c434518b556580970d237910064f8e086ce32d5b594fbc6694e5&scene=21#wechat_redirect)

**活动推荐：**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjHRrQ5oQL09ic10H9PMxzWI8JOZVGPJYyw8hkmicamicUVNL5t9QAdlurrULQ3OQbl3mIyWK8lyYiaMQ/640?wx_fmt=png)

**关于我们：**

**DataFun：**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100+线下和100+线上沙龙、论坛及峰会，已邀请近1000位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章500+，百万+阅读，13万+精准粉丝。

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**