---
title: 'Hulu在Content   Embedding的探索与实践'
company: Hulu
tag: 召回
date: 2021-01-29
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247522939&idx=1&sn=8dfedad371667ef3ebd5621cbb882a25&chksm=fbd72817cca0a1015e484b805bd5ef5c9442b47e1f45a9643cfc56bbc7a5787bad19ae4d1351&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
**![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjTuPYwSYmjVJxtZDZEFrXJSAiaPqb8u3WgHqFxITvhsfqtJibbPEbLiccJdk3aymNMRzeo6Uwb9oyyQ/640?wx_fmt=png)**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhdshbvB4BOnhtyWJ8icnFEcYTkXBLOQHicg6Y87AibVaquzcWiaZO5ibY7ic9513BqTWib7loVMh1NOiaAAw/640?wx_fmt=png)

分享嘉宾：江云胜@Hulu

编辑整理：许晏铭

出品平台：DataFunTalk

**导读：**Hulu是美国领先的互联网视频流媒体平台，拥有大量的电影、电视剧等视频资源，对这些内容的理解和表示是Hulu的一个重要研究方向。Content Embedding技术将内容表示为向量，以利于后续算法、模型的处理和分析。本次分享将介绍Hulu在content embedding方面的一些实践和尝试，包括embedding的生成及其在业务场景中的应用。

**01**

**About Hulu**

Hulu是一个视频流媒体平台，主要由三个要素构成，分别是用户 (users)、内容 (contents) 和广告 (ads)。Hulu的商业模式也是围绕着这三个要素进行的，即Hulu花钱购买内容资源并提供广告展示位，用户付费观看内容，广告主付费购买广告位。

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4P0MXcwF9hUiaFMOCQdpaRibA9lic5AceCFiawJ874EhodBdgvs7M73CIMA/640?wx_fmt=jpeg)**

**1. Contents on Hulu**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4Jpd3rjuTp8kU2NJDKN7GyWd5qLrqCd8vqDjQ5NQu8Q0LYqa5SA6tLA/640?wx_fmt=jpeg)**

Hulu提供了种类丰富的内容资源，主要是电影、电视剧，以及一些体育、新闻、儿童相关的节目；既有点播的内容 (VOD contents)，也有直播频道 (LIVE channels)。

**2. Content understanding in Hulu**

Hulu的内容理解可以分为四个不同的层次：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4Jan7F5Rek1ABQPC2vUzjKxhA5ahW94EcYze4aDeGFas6xom26XTjXQ/640?wx_fmt=jpeg)

* 第1层，对视频的理解，比如检测和识别视频中出现的特定目标、事件、场景、明星演员、商标等，以及一些特定的片段（如片头、片尾、highlight片段等）；
* 第2层，对整个剧集（包括电影、电视剧）的理解，比如为每个剧打一些标签 (tags) 或生成向量表征 (embeddings)，或者分析剧与剧之间的相关性等；
* 第3层，对collection的理解，这里的collection是Hulu页面上每一行所展示的剧构成的集合，我们需要为每个collection也生成一个表征，并分析不同collection之间的关系，以及思考如何用算法来辅助collection的创建；
* 第4层，对内容在Hulu平台上生命周期的理解，主要是分析用户与内容之间的交互信息。

**3. Contents & corresponding metadata/videos**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4Jg41svSBx0WRicPzzs7Oia3ek0zPY2LC0epqV6wChSpT3uuKwylezzQA/640?wx_fmt=jpeg)**

Hulu上的每个剧集（电影/电视剧），除了最直接的视频资源外，还有一些与之相关的信息，包括剧的标题 (title)、简介 (description)、导演 (director)、演员 (actor)、主题 (topic)、类型 (genre)、标签/关键词 (tag/keyword)、获奖情况 (award)、分级情况 (rating)、字幕信息 (caption)、海报/封面图 (cover image) 等。

**4. How to represent contents?**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPhdshbvB4BOnhtyWJ8icnFEc7vaPGdmvXicEze8X14zdBzmX6h6D8pY8eH5EeQzIsW28uazO8vXfg3Q/640?wx_fmt=jpeg)**

上面提到，与一个剧集相关的数据有很多（如下右图所示），它们具有不同的形式（标签类、文本类、图像、视频、音频等），从不同维度刻画剧集，具有丰富的信息。那么，如何综合考虑这些信息，给每个剧一个表征呢？表征，从某种意义上来说也是一种信息压缩，用更简洁、有效、本质的形式来刻画一个东西。典型的表征有如下几种：

* ID类型的表征，用一个id（一般是数字或字符串）来表示一个剧集。这类表征只能反映出两个剧是相同的或者不同的（看id是否相同），不能带来其它额外信息。One-hot encoding也是这类表征的一种形式。
* 标签类型的表征，用若干个关键词来刻画一个剧集，每个关键词具有一定的语义信息，比较方便人类理解。
* 向量类型的表征，用一个向量来标识一个剧集，这类表征可以很方便地用在后续的模型和计算中，对机器比较友好。我们接下来要介绍的content embedding就属于这一类表征。

**02**

**Generation of content embeddings**

**1. Content embedding**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4xsdIIwHib3R7icv2mD1x1y9jGIYiaib4cTysmBckyPsAlRdSiaCGibt8wGrQ/640?wx_fmt=jpeg)**

Embedding是数学上的一个概念，指把一个数学结构经过某种映射嵌入到另一个数学结构中，这个映射需要保持某种意义下的结构不变性。类似地，content embedding是将剧集映射到一个低维稠密的向量空间中，并尽可能让内容相似的剧对应的embedding向量也比较接近。在Hulu，生成content embedding时需要考虑多种不同模态的数据，包括标签类数据（导演、演员、类型、标签/关键词等）、文本数据（标题、简介等）、图像（海报、封面图等）、视频、音频等；另外，考虑到电影/电视剧都是长视频，要压缩为一个低维向量需要很高的压缩率，并且在算法的训练和测试过程中都没有ground-truth可以参考，因此生成content embedding还是一个比较有挑战性的任务。

**2. Tag-based embeddings (Graph Embedding)**

**Step 1：**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4Dzn5ycTwKwtpBOJKuF1K5pQJd0YdU4mxNU6rlVL30LiayjicibJgTxlUQ/640?wx_fmt=jpeg)**

首先，介绍如何利用剧集的标签类型数据来生成content embedding。前面提到，每个剧集都或多或少会有一些标签类型信息，比如导演、演员、类型、关键词/标签等，我们把它们称为该剧的属性 (attribute) 信息。由此，我们可以构建一个content-attribute graph，其中剧集和属性是该 graph 中节点，它们之间的对应关系用graph中的边来连接。由于不同的剧可能有相同的属性（比如两个剧有相同的导演或关键词），这些共同的属性节点可以将不同的剧连接起来，如下图所示，最终会构成一个非常庞大的content-attribute graph。

**Step 2：**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4icFPLyGSnmyMj4nYJKUkL1Hdn6Fia3GlHDgic6E2pmUDrAbVVtLE0X2Rg/640?wx_fmt=jpeg)**

有了content-attribute graph之后，可以用node2vec 技术为graph中每个节点（包括剧节点和属性节点）学习出一个embedding向量，其中剧节点对于的向量即为我们需要的content embedding。大致的步骤是先根据graph采样获得一些path，然后调用word2vec方法学习得到节点的embeddings。我们略过细节，这里的基本思路是：如果graph中两个节点之间的path越多，则希望它们对应的embedding向量越接近。

**3. To be improved …**

上述基于content-attribute graph生成的content embedding，有如下几个不足的点：

* 只使用了标签类型数据，没有考虑非标签类型的文本数据（如标题、简介等）；
* 在标签类型数据中，GraceNote keywords和genres是最重要的，但它们的覆盖率并不高，很多剧会缺失这些数据；
* 构建content-attribute graph时候，并没有利用上这些标签的语义信息（只根据标签是否相同来构建graph中的连接边）；
* 在建模过程中，不同类型的标签之间没有足够的信息交互。

**4. Considering non-tag textual data**

接下来，我们思考如何利用非标签类型的文本数据（标题、简介等）。我们尝试了两种处理方法：

* 方法一：直接根据文本数据生成content embedding；
* 方法二：先根据文本数据预测出一些标签，然后将预测的标签加到前面的content-attribute graph来生成更高质量的content embedding。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4WLNCic1uujqKw5yGSmctibu3KGmCBDAjEb6IgooKySIjfK1icQKicxEYEQ/640?wx_fmt=jpeg)

上图是我们尝试的方法一，对于剧集简介，先用BERT模型得到句中每个token的embedding，然后利用SIF算得每个句子的embedding，最后将剧集简介中所有句子的embedding做平均后得到整个剧集简介的embedding。这个方法的效果比较一般，接下来我们重点介绍方法二。

**Metadata-BERT:**

**use metadata to predict/complement content tags**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ44AMGZMzJA0KWI8azpOreibbc4uoY3zib660PBibibPsBicIjz1w7pLWrhsA/640?wx_fmt=jpeg)**

方法二，主要是先根据文本数据来预测剧集的一些标签信息，然后将这些标签加到content-attribute graph中，接着调用前面的tag-based embedding方法即可。我们对原始BERT模型进行了改进，使得它可以接受各种类型的数据作为输入，包括标签类型数据 (tag-like metadata) 和非标签类型的文本数据 (non-tag textual metadata) 。新的模型被称为Metadata-BERT，它能根据输入的metadata信息预测出更多的tags，可以作为原始标签数据的一个扩展和补充。Metadata-BERT模型利用GraceNote keywords数据进行训练，在测试集上的标签预测准确率达到83%（比原始BERT的61%有显著提升）。将Metadata-BERT预测出来的标签添加到之前的content-attribute graph中，能够进一步丰富graph的节点和边，从而产生质量更高的content embedding。

**5. Further: how about visual/audio data?**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ43HkBfEWKEDmAibgn20YewQIlgK2LPj5tEfTWdkKNiboHZDIhbsC9C6Hg/640?wx_fmt=jpeg)**

除了上述提到的标签类型数据和非标签类型的文本数据，一个剧还有对应的音频资源和视频资源。与前面的数据不同，音视频信息是一帧一帧的，一部剧是由一个图片序列和音频序列构成的。如何将整个序列转化为一个embedding向量，这是我们需要重点考虑的地方。我们的做法是：先将整个视频的视频帧和音频帧抽出来，然后用一些神经网络（如Inception/VGGish）为每个视频帧和音频帧提取特征，最后用一些聚合模型（如NeXtVLAD/BERT等）将帧级的特征聚合为整部剧的embedding。整个模型可以借助一些诸如标签预测、推荐排序等任务来训练。

**6. A try: two-level-BERTs for v/a embedding learning**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4QYXCYvpaNp6sXFGssdbqBmb0S5TIYPRDvnjF0zKPx6uN9eB5I3WuAg/640?wx_fmt=jpeg)**

我们做了一个尝试，用两层BERT模型来做推荐业务中的CTR预估任务，简单来说，就是先用一个BERT模型来聚合视频的帧级/片段级的特征，以得到每部剧的content embedding向量；然后再用一个BERT模型来聚合用户信息，主要是历史观看记录 (history\_shows) 以及目标剧集 (target\_show)；最后再接MLP进行CTR预估。这个框架比较大，将content embedding的学习直接放到具体的推荐业务中，是一个end-to-end的学习过程；缺点是两个BERT模型体量太大，收敛不太稳定。

**7. Overview: generation of content embeddings**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4jicgsDLLJCbyrLEpHq1yFNmKZecQrPm7FvXI3KZ0PE0kSyA6lvKKpjw/640?wx_fmt=jpeg)**

上图是content embedding生成过程的一个概览图。图中的 content data包括剧的metadata信息、视频文件和字幕文件，其中metadata又分为标签型数据和非标签型的文本数据，而视频文件又包含视觉图像和音频信息。针对不同类型的数据，我们采用不同的模型，从而产生不同的 content embeddings，而这些不同的embedding也融合成一个终极embedding。在实际应用中，可以根据业务特点来使用不同类型的embeddings，或者使用最终的融合版embedding。

**03**

**Applications of content embeddings**

**1. Content similarity**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4WXGGicSGicVhTfbDgyLaibjtUshqjYL4Yk9K3BbT2q7lwp91yJqnicSv5g/640?wx_fmt=jpeg)**

接下来我们介绍content embedding的一些应用。content embedding最直接的应用是可以简单方便地计算两个剧在内容上的相似性（比如计算embedding向量的余弦相似性）。下图右侧是完全基于content embedding向量计算出的与“钢铁侠”最相关的剧，可以看到大部分结果都还是比较合理的。在推荐业务中，很多时候需要计算show-to-show relevance，而内容相似性可以作为其中的一个重要因子（其它可能需要考虑的因子包括基于用户co-watching信息的相关性等）。Show-to-show relevance可以应用在Hulu的You May Also Like (YMAL)、UpNext等场景中，下图左侧是Hulu的YMAL页面。

**2. Content embeddings as features in TV/Movies ranker, PCS, etc.**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4VhClMuMcoaLiccDhd4aIs4Yjo8Xq4iaicGKxa3r3RWEgjne6FMBJRMtug/640?wx_fmt=jpeg)**

Content embedding的另外一个应用是可以作为很多算法、模型的输入特征。如上图所示，左边是Hulu推荐业务中对TV/Movie的排序模型，右边是对Home页面的collections的排序模型，这两个模型中都使用了content embeddings作为输入特征（图中绿色框所示）。

**3. Content embeddings for content cold start (in Retriever)**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4nDLo707plIOnHrzlCNUdQYD7WdsxT3vn8DYouLnibrXElHboPBxK2UQ/640?wx_fmt=jpeg)**

Content embedding在内容冷启动方面也有着重要应用。以推荐系统的召回模型为例，如果召回模型只是基于用户的co-watching信息（如下图左侧分支），这样对于新加入的内容或冷门内容，可能采集不到足够多的用户观看记录，从而影响召回效果。这时候可以根据content embedding来构建另外一个基于内容信息的召回分支（如下图右侧分支），然后再用一些方法（比如gate函数）将两个分支融合起来（如下图中间的分支所示），从而提升对新内容或冷内容的召回效果。

**4. Collection modeling with content embeddings**

前面提到，Hulu页面上每一排展示的内容被称为一个collection（一个collection也即若干个剧构成的一个集合）。在Hulu的Home页面，会根据用户的行为数据对collection进行动态选择和排序，这就需要大量的collections供算法选择，仅靠editor手动创建collections是非常低效和耗时的。这里我们尝试利用算法，从如下几个角度来加速collection的创建：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4cX3RHv6bwZFibX2ILHDejsg0b1bicwcEEraI2xtFksuS1cFIhEmRdu6g/640?wx_fmt=jpeg)

* 对已经存在的collections进行建模，从而可以对collection里面的剧进行扩展和更新；
* 在editor手工创建collections时，让editor可以根据embeddings或tags来搜索相似的剧集，或者直接根据editor已选的剧作为种子来自动推荐合适的剧加入到collection中，从而提高collection的创建效率；
* 用算法直接创建collections，然后经过人工审核并命名后即可入库。

**04**

**Thinking**

**最后，关于content embedding的一些思考：**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgpVZHffjavFLZkGE15FwZ4VbHGdKzM4uf7XPouUh5k9bULoKBAhiaWfnj64iaVnxVDI3yaCiaHHlXrw/640?wx_fmt=png)

* 如何评价content embedding的效果？是建立一套以内容为主视角的评价指标，还是看embedding在推荐、搜索等业务中的效果？
* Content embedding与具体业务场景之间的gap。比如，content embedding的训练通常与业务目标是分开的，如何保证content embedding在业务场景中的效果呢（泛化性能）？如何利用业务相关的数据集或任务来调整content embedding呢？是否可以直接用业务相关的任务对content embedding进行end-to-end的训练？是提供内容理解的数据（比如像content embedding这种），还是提供内容理解的能力（比如算法模块等）更好呢？

上述问题都是开放的，没有定论，欢迎大家思考和讨论。

**今天的分享就到这里，谢谢大家。**

---

在文末分享、点赞、在看，给个3连击呗~

---

**嘉宾介绍：**

![](https://mmbiz.qpic.cn/mmbiz_png/vrk53t8TibicrOhUKmZqaRcO3v2ib1EJI9wiaUgcgTjBMprq6j51zLoGcaTGC3oDNLYq07cjMrYmhTDjQ0aoAbdqtQ/640?wx_fmt=png)

**江云胜**

Hulu | Senior Research Lead

**社群推荐：**

欢迎加入 **DataFunTalk NLP**交流群，跟同行零距离交流。**识别二维码**，添加小助手微信，**入群。**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjWF4KeBlBY77bxkY6RkGYibHjAzoDzvpicWmiamn1unXwekUjw5gfc21jwoGBMEPxsUy3SW0RKicjZYA/640?wx_fmt=jpeg)

**关于我们：**

**DataFunTalk**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100场线下沙龙、论坛及峰会，已邀请近600位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章300+，百万+阅读，9万+精准粉丝。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPjDjicR2yOx02wNZLtRyVjaalkxbGB7NU2Paq7KM3MPhXtxKJy9M6Bs8EicpUtqCUe6fgfV4HSiaHs7Q/640?wx_fmt=jpeg)

🧐**分享、点赞、在看**，给个**3连击**呗！**👇**