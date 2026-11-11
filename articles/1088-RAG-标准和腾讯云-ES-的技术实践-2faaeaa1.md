---
title: 'RAG 标准和腾讯云 ES 的技术实践'
company: DataFun
tag: 问答/RAG
date: 2024-07-03
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247728853&idx=1&sn=062e0a05ce9a97ded8c998b2d20fe3d2&chksm=fbd8ccb9ccaf45af64d70c016e8bfff1035be3435e7d90f331dc17777b7c2e02b3924be9f4fd#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgqiaLxNxa7Fhbz8BmDjw7ZgX3m9BBiaS1MIxpPIdAuUjRMnZcICkFQC1m34ovg7z3ibZ8PYE9iaibt8xg/640?wx_fmt=jpeg)

**导读** 本文将介绍 RAG 标准和腾讯 ES 的技术实践。

****主要内容包括以下四大部分：****

1. RAG 背景及标准制定

2. ES RAG 解决方案和优势

3. 腾讯云 ES RAG 能力增强

4. 腾讯云 ES RAG 应用实践

分享嘉宾｜任翔 腾讯 腾讯云大数据ES产品负责人 

编辑整理｜张彬

内容校对｜李瑶

出品社区｜DataFun

---

**01**

**RAG****背景及标准制定**

**1.****搜索技术的演进**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOgKD4HMibR50EemKZQJIibEdDQX7RVm7fboIhpSKvtq8ibpqNzsbTFfHBQ/640?wx_fmt=png&from=appmsg)

**在介绍 RAG 之前，首先来回顾一下搜索技术的演进，因为 RAG 与搜索技术的发展是紧密相关的。**

**搜索是人们生活中的一个非常基础的需求，已渗透到生产生活的方方面面。在早期，真正的搜索技术问世之前，要检索一些内容通常要依靠分类管理。当时的检索效率是非常低的，并且能够检索的数据规模也很小。直到倒排索引技术推出后，引发了一场革新，它推动了整个搜索效率的提升。倒排索引实现了秒级毫秒级的响应速度，在 TB 甚至 PB 级的数据规模上快速查找反馈。然而倒排索引技术存在一个缺点，因为其本质是基于关键字进行比较，所以还是限制在文本搜索的领域，对图片、视频的搜索无法实现。另外，它也无法很好地理解语义，比如搜索计算机和电脑这两个词，在关键字比较的维度里，它们会被认为是不一样的。后来出现的向量化技术就很好地解决了语义理解的问题。**

**向量化技术可以将文字或者图片、视频的特征进行提炼，形成多维向量。并通过在向量空间中计算这些向量之间的距离关系，比如欧式距离等，判断两个内容之间的相关性。这样就极大地拓展了搜索的范围，可以支撑对图片、视频等多模态内容的检索。**

**到此为止，仍属于传统搜索的范畴。因为在用户提出一个问题之后，返回的还是一个结果的列表。需要用户在这个结果列表里面自己去进行分析总结，最后得到想要的答案。整体的效率仍然是比较低的，而实际上人们更希望搜索的反馈能够直接给出问题的答案。随着近年来 AI 技术的爆发，Transformer 等深度的基于注意力神经网络的技术的出现，又一次革命性地推动了整个搜索技术的演进。**

**如今，大模型已经可以从非常海量数据中搜索我们问题相关的内容，并且进行总结提炼，非常好地回答我们的问题。企业非常希望将这一技术进步应用到实际生产中，然而实践过程中我们发现仍存在着种种障碍。这就是 RAG 技术出现的原因，它可以作为一个桥梁帮助我们更好地解决搜索的问题。**

**2. RAG****检索增强生成**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOQItO1ST2diaia0Jbk0LbMP9UL7GsDh1ib6QtKWB5xOuOOiaibQmnSGoW4vA/640?wx_fmt=png&from=appmsg)

**RAG****的英文全称为 Retrieval Augmented Generation，即检索增强生成。它是通过检索一个外部的知识库，来改善大模型的内容生成效果。**

**我们知道，大模型是一个预训练模型，是预先训练好的，这也带来了一些问题，在训练好时，其知识也就停留在了那一刻，之后发生的事情它可能就不知道了。另外，大模型检索的是互联网上公开的一些信息，而它对企业或行业特有的一些知识是缺乏的。这些问题导致大模型常常出现幻觉。**

**RAG****技术就提供了一种方案，企业可以把本地的一些专业知识提交给大模型，而不需要投入海量的计算资源去重新做预训练，就可以让大模型更好地回答专业领域的各种问题。RAG 现在主要的应用场景包括知识问答、智能客服、专家系统等等。**

**3.****信通院检索增强生成 RAG 技术标准**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QO2icFicD9079UicF9CtpfrQXADqy0SRxxf9sgW3icpRSNyk9qtbbSyq7o7g/640?wx_fmt=png&from=appmsg)

**为了帮助企业了解如何搭建一个 RAG 应用，信通院组织了四十余家企业共同编写了《检索增强生成（RAG）技术要求》标准。该标准包含了知识库的构建、知识的检索、内容生成、质量评估、平台能力等五大能力域，17 个能力子域，50 个能力项。这里特别值得提到的是，腾讯云是其中的一个核心企业，也是首个通过 RAG 权威标准认证的企业。**

**腾讯云 ES 是国内公有云首个能够实现从自然语言处理到向量生成/存储/检索，并与大模型集成的端到端的一站式技术平台。接下来将详细介绍 ES RAG 解决方案。**

**02**

**ES****RAG****解决方案和优势**

**1.****Elasticsearch(****简称 ES):海量数据搜索和分析引擎**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOmqItM19yCUZgNWJIz28uXWgLVOfE7F2ejyVy5BgSKzuHlspRyrwhrw/640?wx_fmt=png&from=appmsg)

**ES****的全称是 Elasticsearch，它是全球目前排名第一的搜索引擎。在国内应用也非常广泛。ES 的一大特点是采用分布式，所以能够处理海量数据。针对搜索方面，ES 具有全文检索、向量检索以及 RAG 等关键搜索技术。**

**2.****ES****在 RAG 领域的一站式解决方案**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOSEJcXouEoZhMMjAtqN0BEcltNCFo99HJV5LibZxqEWOjTkibGFSAkoCA/640?wx_fmt=png&from=appmsg)

**ES****在 RAG 领域的解决方案如上图所示。一个传统的用法就是当用户有一个问题的时候，将问题直接提交给大模型，大模型根据自己的知识去给出回答。如果遇到企业私域信息，大模型不知道答案，那么 ES 就会通过 RAG 方案，将问题给到我们的知识库。知识库中不仅有文本，还会有图片、视频，我们会提前把这些内容进行向量化。在检索过程中，进行文本和向量的联合召回，得到一个 TopN list。把这个 list 和用户自己的问题一起构成一个 prompt，再提交给大模型。这时，大模型就可以很好地去回答这个问题了。**

**3.****ES****拥有你所需的所有功能**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOXa0btcX7j11n7qyE0m0j6lCRZlV9FTeWGNFQKPxNq3BwZswWNC8khg/640?wx_fmt=png&from=appmsg)

**和目前其它一些技术方案不同的是，ES 不需要依赖多个技术栈去配合，在一个 ES 技术栈里面就结合了向量生成、存储、索引、检索以及大模型等多项技术，因此可以大幅降低成本。**

**RAG****的关键技术之一就是向量化。和传统的向量数据库相比，ES 不仅可以实现向量的存储和搜索向量的生成，同时还支持混合搜索、模型的灵活选择和部署、聚合分析，以及基于权限的一些管理等等。**

**4.****向量转换**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QO6jYuic8635y8BCMpnjY7GR8k6iaIqobX0kiaVl9iavRqlKq9nYDVuH7eww/640?wx_fmt=png&from=appmsg)

**在 ES 中，向量转换非常灵活。首先 ES 中包含内置优化的模型，比如 ELSER 和 Multigual-e5。另外它也支持第三方模型，可以将第三方模型部署到ES 上，也可以基于 inference API，直接去调用在 OpenAI 和 HuggingFace 上的模型，实现在线的向量转换。**

**5.****召回排序**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOVFt5qHQsIPZ2yE5BrVY5ia0dIKszRG2Vy5QP1avDhy7LawnGNWKqibBg/640?wx_fmt=png&from=appmsg)

**在召回排序方面，目前，对文本和向量混合检索的召回排序还存在一定挑战。因为传统的方法中，我们需要将不同维度召回的信息进行归一化处理，而归一化的评分尺度、分布的差异，这些都会对最后的排序带来挑战和质量上的影响。ES 中已经内置了 RRF 导数融合排序，以及 LTR 基于模型的排序能力。一方面是更加便捷，另一方面其成熟度也为网络排序质量提供了更好的保证。**

**6.****混合搜索**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOuvP4A6fa06zxNj4G09pkYY2upwkHzPRjLotSib8tBeTtj3ozCs6YxKQ/640?wx_fmt=png&from=appmsg)

再来看一下混合搜索。

向量搜索具有诸多优势，比如可以更好地理解和处理自然语言，通过上下文更好地理解语义关系。并且因为是基于语义理解，所以可以轻松实现跨语言。另外还可以支持图片、视频等多模态的搜索。

同时我们也看到其局限性，比如精确匹配和短文本情况下的语义理解不够准确，导致结果的相关性比较差。另外可解释性比较差，所以调优难度也比较大。向量本身对计算资源的要求也比较高。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOs1VpRy9jrj5cuDsShh0rk0CuZibNrfryH2cBnicmXdZNBiaQialTDfIsng/640?wx_fmt=png&from=appmsg)

因此，比较好的做法是文本和向量混合搜索，从而结合二者的优势，弥补其缺陷。可以通过关键字加向量搜索这种搭配。比如通过向量检索，先将一批相关性的内容收到，然后再通过关键字去做进一步的精准匹配。这样可以提高准确性和可信度。另一方面，混合搜索还可以丰富搜索内容，以满足不同的用户查询需求和偏好。利用关键词检索的逻辑运算、排序、过滤等能力，可以帮助我们实现更复杂的查询需求。并且关键词检索的文本匹配和高亮显示，也可以使检索结果更易于理解。

**7.****ES****在向量检索与 AI 增强上的优势小结**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QO4DCxNGKbWibqlLAuI0cqH5JiaafCmJicPcStQCdo0zG6P42R3UKJ3mHbA/640?wx_fmt=png&from=appmsg)

ES 在 RAG 方向上的优势包括：

* 低门槛：独立的技术栈，可以一站式完成向量的生成、存储/索引、检索。很多工作不再需要开发，通过配置的方式即可实现。因此大幅降低了接入门槛。
* 高性能：支持百万级 QPS，千亿级销量规模，是其分布式结构和灵活的弹性所带来的一个优势。
* 更精准：支持文本和向量混合检索，提升了搜索的准确性。
* 更智能：可以和大模型无缝集成，轻松构建 AI 智能问答应用。

**03**

**腾讯云 ES****RAG****能力增强**

接下来介绍腾讯云 ES 在 RAG 方面所做的能力增强。

```
1. 专有机器学习节点，助力向量生成和检索
```

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOrsqDF9SZEo7pUSRhkCVttjB09iaUvIFyEicPVtCUjCnHT24LYbdK2UvQ/640?wx_fmt=png&from=appmsg)

首先在腾讯云上支持专有机器学习节点。在这个新学习节点上，可以去做模型的上传、管理和部署，实现一站式的向量生成和检索，可以有效提升向量推理能力。同时，与数据节点隔离，因此可以保证在线业务不会受到向量本身的生成性能的影响，使检索业务更加稳定。

**2.****全球唯一支持****GPU 的 ES 服务，与腾讯自研“芯”技术紫霄软硬结****合**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QO5HAxibmYAEMKPl4RB8sEPJ4O4bKfu89j0TwEjGgyVNl1ibaUreEakWPQ/640?wx_fmt=png&from=appmsg)

ES 目前是全球唯一支持 GPU 的 ES 服务。与腾讯自研的紫霄 GPU 做了结合，可以充分利用 GPU 的高性能，帮助向量的生成，从而提高检索效率。

**3.****针对向量场景自研技术优化，查询性能提升 3-10 倍**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOLKGiaup3KnoxThGB7rygrib9DgrgibHk7ghG2Q1eL1pEua50gjaqgSqWg/640?wx_fmt=png&from=appmsg)

针对向量场景做了很多内核方面的自研技术优化，比如针对向量场景一般数据规模相对较小、读多写少的特点，我们做了分片架构的优化。可以合并查询和归并的流程，帮助查询性能的提升。同时进行了块存储跟查询的优化，通过对 segment 的合并收敛，减少查询随机 IO，这也进一步提升了查询性能。另外，还包括查询并行化、lucence 查询缓存锁改造等等。这些技术使查询性能提升了 3 到 10 倍。

**04**

**腾讯云 ES****RAG****应用实践**

**1.****业务场景**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOPfYheIZ6MCZu6QpkHgJiakNZgc2x9YCTdub4JfRfJlRoBoesmfb76gw/640?wx_fmt=png&from=appmsg)

最后来介绍一下腾讯 ES RAG 的应用实践，这里分享的案例是微信读书的“AI 问书”。微信读书是一个用户非常广泛的在线读书平台，在这个平台上，提供了海量的书籍和内容，整体的目标是希望突破传统的搜索，能够提供更智能的搜索体验，并且更好地理解用户问题，同时支持开放式问题的检索。

**2.****技术挑战**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOm42MLqcxbMZSXBPBErnBPSGufQt0KsFbvy5DAnvFmzUoAFTFfcx94w/640?wx_fmt=png&from=appmsg)

该项目中的技术挑战包括：

* 数据规模大：超 10 亿的量级，且仍在持续增长。
* 运维成本高：向量化部分在外部单独去做，再去匹配到一个系统，这会带来多套系统之间搭配的问题，增加了运维成本。
* 稳定性要求高：该平台用户体量较大，因此对稳定性的要求比较高。
* 查询性能要求高：面对 ToC 场景，查询延迟的要求较高，要达到毫秒级返回。

针对上述挑战，我们构造了 ES 基于 RAG 的一站式解决方案。

**3.****基于腾讯云 ES 的一站式 RAG 方案**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QORo2TmHYRHfXm74ib9HZic0NyIz4BLN70M2G7DuhfUbYicOCRBNA2z1B9g/640?wx_fmt=png&from=appmsg)

这里可以看到和前文中的架构类似。在接收到用户的检索词后，先在整个书籍内容的私有数据域中进行检索。这里采用混合检索，包括文本内容的返回和向量内容的返回，这里可以在一个专有的 ES 机器节点上进行向量的转换，利用 GPU 的性能，模型也是采用一个自定义模型上传，以此方式实现搜索目标。

**4.****独有混合搜索能力**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOZ4fzPOibviaQD8hb7orjZzl2QUuYyjSdRzALEmsvU2dNfibkhvIdRj29w/640?wx_fmt=png&from=appmsg)

具体来看一下混合搜索的能力，文本和向量在这里可以做统一的召回。在引擎层面，有文本、向量、数值等各种索引；同时，支持分词、同义词、实体识别、情感分析等对查询分析的理解；在此基础之上，支持多路召回，混合打分；最后将内容一起提交给大模型，实现智能问答的效果。

**5.****方案价值**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QOZsU8PdvDEVysGsDmPn9ZH89nsfezG0lVf34eJnomZVCkhibzX6r3WOQ/640?wx_fmt=png&from=appmsg)

整体方案带来的价值包括以下几大方面：

* 开发实现效率高：基于一站式的框架，通过配置的方式即可实现，提升了整体的效率。
* 运维投入低：基于 ES 独立架构，减少了运维投入。
* 高准确率：混合搜索使搜索准确率大幅提升。
* 查询效率高：高并发场景下，可以做到 10 亿级向量查询延迟低至毫秒级。
* 存储成本低：支持 LZ4 等压缩算法，可有效降低存储成本。
* 稳定可靠：基于 ES 的资源内核里面的熔断限流技术，可很好地解决高并发和大查询的问题，为业务保驾护航。

**以上就是本次分享的内容，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUiaUMwM8I3NYH3SVrllWIPIMQXDtN5DqCLRhFwFhR9RictLsYYBpOwibjfw/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyawG5xCOSRibQ81YM9aZ2QObS73T5bibFiaXEmVVVg65BmjcdfyzYh7mskiaDEnRia9VaZuPatZgEYusw/640?wx_fmt=png&from=appmsg)

**分享嘉宾**

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****任翔****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****腾讯****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

**腾讯云大数据ES产品负责人**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

丰富的 toB 和 toC 产品经验，负责腾讯云 ES 从 0 到 1 建设和商业化增长，曾从事即时通信、安全、社区等产品工作，拥有十余项专利。

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPgqiaLxNxa7Fhbz8BmDjw7ZgX3m9BBiaS1MIxpPIdAuUjRMnZcICkFQC1m34ovg7z3ibZ8PYE9iaibt8xg/640?wx_fmt=jpeg)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPgqiaLxNxa7Fhbz8BmDjw7Zg9HURPuXnhRq0cMt69pXR2OYVh5bJbtaa6jhmUgjGN0bkx2BNqq3yrg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640?wx_fmt=png)

点个在看你最好看

SPRING HAS ARRIVED