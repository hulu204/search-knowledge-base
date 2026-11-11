---
title: 'RAG 引擎在办公场景下的工程化与算法创新'
company: DataFun
tag: 问答/RAG
date: 2026-05-24
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247777455&idx=3&sn=2708458f9e0f6e5308e95f4c11390f68&chksm=fbdb0ec3ccac87d5d39a7a0cb0cdb60cacc357cf46e082d9af79f34b7d8431873975ecc8dfa0#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgy5iabDRHIYKpOHjhlorpibRwGaOibDfjibyiaiaZQY3CX6oxeln5tyYunQKJEenTMenAuZsojYKFdSFiaJQ/640?wx_fmt=png&from=appmsg)

**导读** 随着大模型的飞速发展，中国大模型与 OpenAI 大模型的差距正不断缩减，然而，在应用落地方面，大模型仍面临着诸多挑战。本文将聚焦于 RAG 这一大模型前沿技术，分享其在办公领域的应用实践。

****今天的介绍会围绕下面五点展开：****

1. 背景介绍

2. RAG 核心技术架构

3. RAG 构建挑战与实践

4. 总结

5. Q&A

分享嘉宾｜付一韬中移动信息技术有限公司高级NLP算法工程师

编辑整理｜马同学

内容校对｜李瑶

出品社区｜DataFun

---

![图片](https://mmbiz.qpic.cn/mmbiz_png/cr9YyS063QrVstianyX9gPA4EZicfkbyKdBQyPtQHPwSLJePicuZmXcBiaLaRSTWrY6UibPpAaeNxLjOSiaeHaSvdHMg/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=2)

![图片](https://mmbiz.qpic.cn/mmbiz_gif/CGEwnc7DGPkXwCkjLX8HzCgjKO1KuxPTWw8L9BNNTM3b8WVfHQxV3vIibDycqksck67KWnnVu75ctUZFfpde2kw/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

📥 获取完整《RAG2.0 引擎架构与实战》电子书

企业正在寻找能真正落地的高效 RAG 解决方案？

本文分享的《RAG2.0 引擎设计挑战和实现》只是起点——我们为你准备了更系统、更深入的独家技术合集，涵盖以下关键内容：

• RAG2.0 技术架构全景图与实施路径

• 混合检索体系（向量+全文+知识图谱）的优化策略

• 企业级 RAG 的评估指标、效果对比与调优经验

• 知识图谱与 Agentic RAG 在复杂问答中的落地案例

• 开源框架 RAGFlow + 向量数据库 Infinity 的整合指南

👇 向下滚动，免费获取完整电子书，开启你的 RAG2.0 落地之旅。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgw2QqBLhBNOY2AMYKyXj9r7vLs3PBpk8nYrE60ciapnKVusNYyicTrOPBicicmh0rZS4xnvUs92FKmicjA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/66Px0lScLmhsSQ81eCsVKJ3rdZkSvWiajhKcPGVl5T8wjtDrfJwp0JOA6IpdLIBVawKV3q1zsXaOP95lR6Gm0zg/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=5)

**01**

**背景介绍**

大模型在应用落地上存在的主要问题包括：

* 幻觉问题：大模型在没有答案的情况下提供虚假信息。
* 新鲜度问题：由于模型知识更新较慢、周期较长、成本问题等导致模型内容不够新鲜。
* 数据安全与隐私问题：数据存在泄露和滥用等风险。

为解决上述问题，RAG 应运而生。

RAG，即检索增强生成（Retrieval-Augmented Generation），是通过结合检索系统和生成模型来提高语言生成的准确性和相关性。

RAG 具有几方面的优势：

首先，它可以在生成内容时引入外部知识，从而提供更加符合上下文语境的回答。

其次，RAG 与预训练模型不同，RAG 的内部知识可以很容易修改甚至实时补充。

最后，相比于微调技术，RAG 具备可观测性、可解释性等优势，从而可以有效降低大模型的幻觉。

RAG 并不是单一组件，它是由多个组件组成的复杂系统。

RAG 系统组件包括：

* 数据源：存储被检索的信息。
* 数据处理模块：负责将数据转换为适合 RAG 系统使用的格式。
* 检索器（Retriever）：根据用户查询从数据源中检索相关信息。
* 排序器（Ranker）：将最相关的信息呈现给 LLM 用于内容生成。
* 生成器（Generator）：结合用户查询和相关信息，通过 LLM 生成最终的响应。

**02**

**RAG****核心技术架构**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74umXHGd8ELoxgrW3GdIjD7UP088SIlUS6yaF6XoiaBCiaNBfYPDKRVyibA/640?wx_fmt=png&from=appmsg)

上图是《Modular RAG》论文中的一张图，展示了 RAG 核心架构。

其中最左侧是传统的 RAG 架构，包括创建索引、检索、大模型对检索内容生成。中间部分是进阶的 RAG，增加了检索前的预处理过程，例如 query rewrite 检索词改写，以及 HyDE 基于假设的文档生成；还增加了检索后的后处理过程，例如 rerank 排序、过滤，最后把相关内容给大模型进行生成。

RAG 与搜广推类似，是由很多组件构成的一套系统，如上图右侧展示了模块化 RAG 的构成。其中每一个组件都做了拆分，包括索引、前处理、后处理、生成，以及路由、知识指引等组件。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74qvo1lxRdruCBq2CprpJFeETcyhsIojj0UneicKmCC9lHdIV4DWgMovQ/640?wx_fmt=png&from=appmsg)

我们设计的 RAG 系统架构如上图所示，自下而上包括：

* 最底层是算法组件，算法组件与服务剥离开，仅对算法进行控制，包括 OCR 的识别、多轮的 query 改写、文本分词、表格识别等。
* 上一层是流程构建，包含了离线入库和在线问答。离线入库包含文档解析、分词和向量生成、索引构建。在线问答包括 query 改写、混合检索、文档排序以及大模型生成。在离线和在线的下层，还会应用向量数据库、ES、MySQL 等。
* 在最上层是用户配置管理，包括知识库的管理、模型管理，对话生成规则等。

系统设计优势如下：

* 分层设计，功能模块化；
* 水平扩展，通用化；
* 算法可插拔，升级透明；
* 低成本、易维护。

我们设计 RAG 系统的整体思路：当接收到用户提问后，进行检索、排序、生成结果，最后将结果反馈给用户。

* 在检索阶段，通过文档解析、query 改写以及混合检索的方式，能够快速地检索出一批可能相关的候选文档，以保证搜检索回来的相关文档**“搜的更全”**。
* 在排序阶段，通过粗排序、精排序以及知识过滤的方式，在这些候选文档里找出最相关的文档，并按相关性进行排序，以保证这些文档的排序**“排的更好”**。
* 在生成阶段，通过知识排版，再结合用户提问和提示词模板组成提示词输入给大模型，进而保证对用户提问的回答能够**“回答的更准”**。

下图是问答流程图，分离线和在线两个部分。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74EziaekZIjGJHbsETRZa5F0j4iblkIyN4SrIn4sW3zToYauruQGja6gkA/640?wx_fmt=png&from=appmsg)

在离线部分，知识库手册、规范等 PDF、Docs 文档解析之后，划分为知识块，然后构建索引，包括文本索引和向量索引。

在线部分，当用户来提问的时候，就可以通过混合检索、全文检索和向量检索，获取候选的知识片，然后对知识进行重排序之后，得到前 topK 内容，最后再组织成提示词输入给大模型。

![图片](https://mmbiz.qpic.cn/mmbiz_png/cr9YyS063QrVstianyX9gPA4EZicfkbyKdBQyPtQHPwSLJePicuZmXcBiaLaRSTWrY6UibPpAaeNxLjOSiaeHaSvdHMg/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=2)

![图片](https://mmbiz.qpic.cn/mmbiz_gif/CGEwnc7DGPkXwCkjLX8HzCgjKO1KuxPTWw8L9BNNTM3b8WVfHQxV3vIibDycqksck67KWnnVu75ctUZFfpde2kw/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

📥 获取完整《RAG2.0 引擎架构与实战》电子书

企业正在寻找能真正落地的高效 RAG 解决方案？

本文分享的《RAG2.0 引擎设计挑战和实现》只是起点——我们为你准备了更系统、更深入的独家技术合集，涵盖以下关键内容：

• RAG2.0 技术架构全景图与实施路径

• 混合检索体系（向量+全文+知识图谱）的优化策略

• 企业级 RAG 的评估指标、效果对比与调优经验

• 知识图谱与 Agentic RAG 在复杂问答中的落地案例

• 开源框架 RAGFlow + 向量数据库 Infinity 的整合指南

👇 向下滚动，免费获取完整电子书，开启你的 RAG2.0 落地之旅。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgw2QqBLhBNOY2AMYKyXj9r7vLs3PBpk8nYrE60ciapnKVusNYyicTrOPBicicmh0rZS4xnvUs92FKmicjA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/66Px0lScLmhsSQ81eCsVKJ3rdZkSvWiajhKcPGVl5T8wjtDrfJwp0JOA6IpdLIBVawKV3q1zsXaOP95lR6Gm0zg/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=5)

**03**

**RAG****构建挑战与实战**

下面从“搜的更全“、“排的更好”、“回答的更准”三个方面介绍中国移动在 RAG 实践过程中遇到的挑战和应对方案。

**1.****搜的更全**

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74YldW2Nj5FWCchuFTYtQnkFNXAqhEAicwqnWt2xWZueCscrpbpdia3m0w/640?wx_fmt=png&from=appmsg)

离线阶段，用户上传文档后，通过 OCR 识别、布局识别、表结构识别和知识切片等流程后，创建索引，调用向量模型以及分词器，将向量数据写到数据索引库中。

在线阶段，用户发起 query 请求后，通过 query 改写，主要是多轮 query 改写。然后通过检索之后，把相应的检索结果传给下一个模块。

接下来，从文档解析开始介绍。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb749oO2iahtTjk7LPlibgPsta0RT2XtW1ozbkom8YcaASnic0J5PgTSgYbEg/640?wx_fmt=png&from=appmsg)

前面介绍过，RAG 相比于大模型有很多优势，其中两点优势在短时间内无法被替代。第一点是版式多样的文档数据，RAG 可以针对版式各异的文档进行解析，解析出逻辑块之后并进行问答。第二点是答案溯源，因为答案通过文档解析，并把相关文档切片内容展示给用户，可以验证答案可靠性，从而提高问答系统可信度。这两点优势，均需要强大的文档解析流程，所以文档解析是 RAG 系统中最重要的一个前置工作。

上图文档示例中，包括标注页眉页角，标题内容、子标题还有表格等内容。文档解析，既需要保证内容不损失，又需要保留文档结构。

我们文档解析的方案是基于 RAGFlow 的 DeepDoc 模块进行二次开发，DeepDoc 模块最大的特色是多样化的文档智能处理，可以对多种不同格式文档进行深度解析。在中国移动内部，文档数据更多是 PDF 和 word 文档，所以我们对这两类文档进行了重点优化。

针对 word 文档，由于 word 本身存在版面结构，因此无需单独进行版面分析，只需要数据切分即可。但是 PDF 文档则不同，PDF 每一页是一张图片，所以需要对版面元素进行恢复，表格识别以及阅读顺序还原。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74v9CE9l6ib35iaZ7HSVVHEEaVDQSEXmiaEvfIeiaCU2mFMvGRD7tD3IEYaA/640?wx_fmt=png&from=appmsg)

接下来进行数据切分。数据切分包括两步，第一步是结构切分，即通过版面结构进行区域区分，比如标题、子标题、内容等；第二步是在每个区域内部再进行长度切分，长度切分是因为文章包含大段文字。切分后的单元是用于检索的文本块，切分过短，检索准确，但输入到大模型的内容会有损失；切分过长，比如切片长度 512，可能会存在内容混乱的情况，无论是在检索还是在排序阶段，都不能做到与用户的原文一致，信息会有损失，所以需要平衡切片长度。

最后，我们分别调用了文本分词以及向量模型，对文本块进行处理，写入索引。通过以上操作后，整个离线流程已完成。

接下来是在线的用户提问。在用户多轮提问过程中会存在上下文的指代和信息缺失情况。上图例子中，分别是两种典型场景，我们最终通过指代消歧和信息补全对 Query 进行改写来保证用户提问的信息完整性。

我们的解决方案是将多轮 Query 改写转换为关系抽取任务，指代消歧和信息补全看作关系，指代实体/指代词/补全信息/插入位置看作实体，采用 TPLinker 模型构建。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74UNiaCarnc5sbjIBiaia0svSdjs74JTu2ialRHME0njvp6UxCj2UZYgoyjw/640?wx_fmt=png&from=appmsg)

下一步是混合检索，主要包括两个部分，第一部分是左边的向量检索，另一部分是右边的全文检索，即先进行分词，然后通过 BM25 算法进行检索。最后这两个检索结果聚集之后，最后统一进入排序模型。全文检索和向量检索，各有优势。

向量检索能够理解相近语义，并能进行跨语言和多语言理解，以及多模态理解。其容错性和泛化能力非常强。全文检索则专注于精确匹配，尤其适用于短文本和实体词关键词的检索。它能够检索出低频词，并且具有较高的可解释性，不是黑盒操作。混合检索旨在融合这两种检索方式的优势，实现互补。

混合检索的优势在于其能够提高检索的准确性和可行性，通过结合向量检索和全文检索的互补性来实现。它能够满足不同用户的偏好和需求，得益于向量检索的泛化能力。此外，混合检索还具备全文检索的强大功能，如逻辑运算、排序和过滤，这对于处理复杂查询非常有帮助。混合检索的可解释性也较强，能够高亮显示哪些词被检索，从而提供清晰的解释。

通过结合离线文档解析、多轮查询改写以及混合检索，可以确保搜索结果的全面性，使得所有相关内容都能进入候选池，从而在进入下一环节时不会有信息损失。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74FrHALXf4RciaCFncydFfo4c2O4yCpT08ib4XyclyEqyKsFZVgrbHsLvA/640?wx_fmt=png&from=appmsg)

在对开源分词模型进行比较时，我们发现 jieba 和百度的 lac 分词粒度过细，而 texsmart 的分词粒度则过粗，例如它会将“全面建设社会主义现代化国家”这一长词组合并在一起。这样的分词方式虽然在某些情况下没有问题，但如果用户搜索时不太可能使用这么长的词汇，而是可能使用“社会主义现代”、“现代化”、“现代化国家”等短语，那么这种分词方式可能导致检索不到相关内容。因此，我们认为 cutword 模型的分词粒度相对适中，既能够正确切分，也能合理合并。

在向量模型的选择上，我们对比了多种模型，包括 BGE-M3、网易的 BCE、M3E 和 GTE 等。在我们的场景下进行了相关性评测后，最终选择了 BGE-M3 和 BCE 这两个模型，因为考虑到双模型能够达到检索互补的目的。尽管后续出现了许多大模型生成向量和其他更新的向量模型，我们也进行了测试和评估，但新增的向量模型对系统的意义不大，因此并没有采用它们。目前使用的这两个模型已经能够满足我们线上使用的需求。

**2.****排的更好**

在完成“搜的更全”这一步骤后，接下来是如何做到“排的更好”。

下面是整体流程图。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb746lUHric3QRbicmWj8VqzmCbSwhPiabhkqiashia7j0AhqJUVb8tQ2iaDSia0A/640?wx_fmt=png&from=appmsg)

在完成混合检索并获取 100 个检索结果后，我们采用了一个两阶段的排序策略来进一步提高检索的准确性。首先，进行粗排序，这一阶段会从 100 个结果中筛选出 20 个最相关的候选项。随后，对这 20 个候选项进行精细化的排序，最终选出 5 个最为精确的内容。在这一过程中，我们还会进行知识过滤，以确保最终输出的内容符合我们的要求。常规的 RAG 系统中没有粗排序和知识过来部分，由于业务场景效果问题，我们特别增加了粗排序和知识过滤这两个步骤，以进一步提升检索质量和准确度。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74NC6doZtDtUibAJBBhibu2Adk4vyJ0m7cjO2ormQkwzUTvY6cm77uuVyA/640?wx_fmt=png&from=appmsg)

粗排序 RRF 是一种倒数排序融合技术，用于将不同相关指标的多个结果组合成单个结果。在混合检索中，我们得到多个不同来源的排序内容，但它们各自的排序得分（如 BCE 和 BGE 的得分）是不可比的。RRF 通过依赖相对排名而非绝对得分来解决这个问题，适用于两个或多个查询场景。

RRF 的公式显示在左侧部分，通过一个可变参数 k 和文档在不同路径中的排名进行计算。例如，对于 BM25 排序结果为 a、b、c，而向量排序结果为 b、c、a，通过计算每个文档在不同路径的排名和，得到最终排名得分。RRF 的优势在于它不依赖相关得分，而是仅使用排名，这使得它简单且有效，无需模型操作。它适用于多路召回场景，通过 RRF 选择 topn 后再进行重排序，这有助于提升重排序性能和效率，同时减少因召回过多导致的排序压力。此外，混合检索后的文档可以通过 RRF 进行合并和去重。

接下来，介绍一个粗排序模型，ColBERT。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74fyM2Cxumpyma4J8gj73t7oBIJylbQiaFxgcyfvs9GMvqfIeRvf1mUgA/640?wx_fmt=png&from=appmsg)

该模型采用了延迟交互的方式。从上图可以看出，其结构类似于双塔模型，包含 query 向量和文档向量。不同之处在于，ColBERT 在每个 token 层面进行计算，最终汇总得分。

ColBERT 的核心思想是延迟交互，即在处理的最后阶段进行交互。与传统的交互式模型 CrossEncoder 不同，ColBERT 采用了双编码方式，离线处理文档编码，在线仅对 query 进行编码，从而显著提高处理速度。

与双塔式模型相比，ColBERT 能够输出多个向量。普通的双塔模型在生成向量后即完成处理，而 ColBERT 则为每个 token 计算一个向量，从而在最后一层保留语义信息，实现每个 token 的交互。

在排序计算阶段，ColBERT 引入了延迟交互和相似度函数，通过计算 query 中每个 token 向量与所有文档向量之间的相似度，得出最终的得分。

有关 ColBERT 的详细介绍和实验验证，可以参考张颖峰老师的《延迟交互模型，为什么是下一代 RAG 的标配？》文章，其中详细阐述了该模型的性能和可信度。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74dqHYMHEK3w7q3ZGyLuNJJJ1OgECTSBwp8vynBcHJibJAUZAvjicUUicmw/640?wx_fmt=png&from=appmsg)

继两个粗排序模型之后，我们还有一个精排序列模型。引入精排序模型的必要性在于，例如向量模型可能将“大连医科大学怎么样”与“大连理工大学怎么样”判定为相似度高，而与“大连医科大学的百度百科介绍”相似度低。尽管如此，当用户询问大连医科大学时，他们并不希望了解大连理工大学的信息。这表明双塔模型在构建时只考虑了相似性而非相关性，即它只关注了类似同义词的内容，而忽略了实际的相关性。

因此，我们采用了基于交互的重排序模型，该模型从一开始就在两边进行交互，从而能够更准确地判断向量模型的相似度。向量模型与 Reranker 模型之间存在差异：向量模型可以在离线时创建，而排序模型只能在在线时操作。向量模型的优势在于其高效率和简单实施，但缺点是缺乏深度，可能忽略用户的意图。相比之下，排序模型能够深刻理解上下文并进行高级语义分析，但其计算密集型，模型复杂，后置时间较长，这也是精排训练模型的特点。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74yg4WQAUicpGw7rNoFnmhib4v2toWbibibAahtXYEWbN1Ua5s8KG1HreN0w/640?wx_fmt=png&from=appmsg)

我们介绍了三个模型：RRF、ColBERT 以及基于交互的 Cross Encoder 模型，它们都用于排序。RRF 和 ColBERT 在性能上有显著优势。RRF 不需要模型介入，而 ColBERT 能够离线预处理文档，在线只需计算 query，并通过 Max Sim 对每个 token 进行计算，因此耗时较短。

RRF 和 ColBERT 均可作为粗排序模型。基于交互的模型由于需要在线计算 query 和文档，耗时较长，但准确性高。我们可以先通过索引召回 100 个结果，然后通过粗排序选出 TOP20，再使用交互式模型进行重排序，以此达到效率和准确性的平衡。这三个模型可以组合使用，也可以单独作为排序模型操作。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74uJLP3ku0wMJWXww38oDXqWr7gqcSLJ3XibsovfibYicFwWaqKVIkeEsLA/640?wx_fmt=png&from=appmsg)

上面介绍了三个排序模型，那么为什么需要知识过滤呢？尽管拥有排序模型，但对于大型模型来说，检索内容后可能包含无关知识，这是排序模型无法解决的。因此，需要一个知识过滤模块，通过 NLI 任务评估检索知识与问题的相关性，以提高问答准确性。

选择知识过滤模块的优势在于，可以基于业务数据训练一个二分类的模型，这个成本要远远低于训练一个排序模型。另外，还可以根据不同的业务场景来决定是否选择该模块，以达到模块可插拔的优点。

**3.****回答的更准**

在实现了全面的搜索和有效的排序之后，我们关注如何提高回答的精确度。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74bpbZMzvlXG97QaBccehVZqjC7ZukAONmTGlhia1VjyjwoCzoVYlw6fw/640?wx_fmt=png&from=appmsg)

整个流程是当排序知识文本块之后，接着进行知识排版，并将这些排版后的知识与用户的问题整合到一个模板中。例如，将知识排版内容放入提示词模版的"knowledge"部分，用户提问放入"question"部分，并将组合后提示词传给大模型进行生成。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74xibaLgTaf4co4HmekiavOj9dNPb2N0cXuZKvibV758jiaIZHibLPS2tyfOQ/640?wx_fmt=png&from=appmsg)

在实际业务场景中，我们可能会遇到上下文知识的局限性，例如在分片时对粒度的选择（如 128、256 或 512 个 token）。我们还需要考虑如何避免信息的损失和如何召回上下文。例如，当用户询问“什么情况下，信息处理者可以处理个人信息？”和“个人信息处理的一般规定有哪些？”时，我们需要根据不同区域的具体条款提供答案，这时不同的分片粒度也无法完美解决这样的问题，另外不同的分片粒度可能会影响检索和排序的准确性。

为了解决这一问题，我们考虑了两种不同的块：较小的块用于提高检索能力，而较大的块用于提供更丰富的语义信息。我们首先评估不同分片大小的性能和质量，选择一个效果的平衡点。在离线阶段，我们通过文档解析了解层次结构，并在入库时将这些结构存储。在线阶段，我们使用同层或父层进行上下文补全。

还需要注意的是，在排序过程中可能会出现重复内容，因此需要进行汇总和去重，然后组装提示词。另外，在组装提示词时，需要注意如果相关知识内容距离用户的提问太远，大模型可能无法生成准确的回答。因此，我们需要确保知识排序的内容与用户提问尽可能接近。

最后，我们通过知识排版和提示词模板为大模型提供输入。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74qpzNcMSe1dr8YQRVxItnGguNljia77yAwQpfaJGQcvxctibrlQprzZpA/640?wx_fmt=png&from=appmsg)

尽管如此，仍可能存在一些问题，例如事实性不足或逻辑缺失。为了解决这些问题，我们采用 FoRAG 两阶段生成技术的方案：首先生成大纲，然后基于大纲扩展生成最终答案。这要求模型在生成答案时必须与用户的提问、上下文和提纲输入相匹配。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74c4IcUjn86DEsfTpeic2TPj5B7vgZb3fNIz9IibzoiaBgXibECKoOry2VKA/640?wx_fmt=png&from=appmsg)

上图是一个提示词模板，先组织成相应的结构，生成提纲，然后再回答，这种方法可以提高回答的结构性和完整性。

![图片](https://mmbiz.qpic.cn/mmbiz_png/cr9YyS063QrVstianyX9gPA4EZicfkbyKdBQyPtQHPwSLJePicuZmXcBiaLaRSTWrY6UibPpAaeNxLjOSiaeHaSvdHMg/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=2)

![图片](https://mmbiz.qpic.cn/mmbiz_gif/CGEwnc7DGPkXwCkjLX8HzCgjKO1KuxPTWw8L9BNNTM3b8WVfHQxV3vIibDycqksck67KWnnVu75ctUZFfpde2kw/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=3)

📥 获取完整《RAG2.0 引擎架构与实战》电子书

企业正在寻找能真正落地的高效 RAG 解决方案？

本文分享的《RAG2.0 引擎设计挑战和实现》只是起点——我们为你准备了更系统、更深入的独家技术合集，涵盖以下关键内容：

• RAG2.0 技术架构全景图与实施路径

• 混合检索体系（向量+全文+知识图谱）的优化策略

• 企业级 RAG 的评估指标、效果对比与调优经验

• 知识图谱与 Agentic RAG 在复杂问答中的落地案例

• 开源框架 RAGFlow + 向量数据库 Infinity 的整合指南

👇 向下滚动，免费获取完整电子书，开启你的 RAG2.0 落地之旅。

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/EBaibcQicPxgw2QqBLhBNOY2AMYKyXj9r7vLs3PBpk8nYrE60ciapnKVusNYyicTrOPBicicmh0rZS4xnvUs92FKmicjA/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

![图片](https://mmbiz.qpic.cn/sz_mmbiz_png/66Px0lScLmhsSQ81eCsVKJ3rdZkSvWiajhKcPGVl5T8wjtDrfJwp0JOA6IpdLIBVawKV3q1zsXaOP95lR6Gm0zg/640?from=appmsg&wxfrom=5&wx_lazy=1&tp=webp#imgIndex=5)

**04**

**总结**

最后对本次分享的内容进行一下总结。

**分享总结：**

* 首先，在办公领域的 RAG 构建中，我们在构建系统和构建算法两个方面进行了实践。
* 在检索方面，通过文档解析、多轮 query 改写和混合检索等方式，确保检索到的相关文档**“搜的更全”**。
* 在排序方面，采用粗排序、精排序和知识过滤等方法，保证文档的相关性排序**“排的更好”**。
* 最后，在生成方面，通过知识排版和提示词模板的组装方式，确保大模型**“回答的更准”**。

**一点心得：**

* 构建一个基础的 RAG 系统相对容易，但要做得优秀则较为困难，因为需要关注每一个细节，不能将所有压力都放在大模型上，而应确保每一步都执行到位。
* 一个生产级别的 RAG 系统的目标是优化检索和排序，贴近业务，按需设计。
* 在实际应用中，需要工程和算法方面共同努力，因为 RAG 系统需要大量的对比、验证和优化。

以上就是本次分享的内容，谢谢大家。

**05**

**Q&A**

**Q1****：达到哪些指标后系统可以上线运行？**

A1：在系统上线前，我们会进行文档测试、提问和标准答案的人工评估。在企业环境中运行时，我们会收集不同部门的反馈，包括 badcase 和 goodcase，并据此整理内容以满足上线要求。主要评估指标包括 badcase 的解决率和整体准确率，这些评估主要针对用户需求。

**Q2****：在同层和父层上下文信息不完整时，如何补全？**

A2：如果上下文信息不完整，需要根据当前层的结构进行补全。例如，如果文档位于第二层的第五个位置，可以将第二层的所有内容以及上一层和下层的部分内容补全回来。具体补全策略取决于业务需求和分片大小，确保输入给大模型的内容不超过其最大输入限制。

**Q3****：如何提高系统速度？如果延迟过长怎么办？**

A3：需要分析延迟的原因。如果硬件条件和模型加速措施得当，效率可以满足用户需求。如果硬件资源受限，可能需要选择轻量级的排序模型，如 Colbert，以适应业务场景。

**Q4****：除了 chunk size 之外，还有哪些优化点？**

A4：确保文档解析时不丢失信息，并将其完整地存储到索引中，保留清晰的结构。切片的大小应根据实际场景和数据情况来确定。

**Q5****：如何处理音视频数据？**

A5：目前我们尚未处理音视频数据，但计划引入多模态技术以支持企业场景中的图片内容问答。

**Q6****：对于包含长表格的 PDF 文档，如何提高问答的准确率？**

A6：目前我们将整个表格输入到大模型中。如果能精准定位到表格的特定区域，将有助于提高回答的准确率。目前我们还未能做到这一点，仍需将整个表格内容输入模型。

**以上就是本次分享的内容，谢谢大家。**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUiaUMwM8I3NYH3SVrllWIPIMQXDtN5DqCLRhFwFhR9RictLsYYBpOwibjfw/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/EBaibcQicPxgyRHpdEZ2PFvII3OKpiaAb74wcrONJjr3Pg6pL7h3YaF0Q5hFAPZP87G8mxFLtuTmOKNsvGjKbqHLQ/640?wx_fmt=jpeg&from=appmsg)

**分享嘉宾**

INTRODUCTION

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****付一韬****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

****中移动信息技术有限公司****

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

**高级NLP算法工程师**

![](https://mmbiz.qpic.cn/mmbiz_gif/zHbzQPKIBPhlaUHIqJNZPg7JDND9IHUialrXwjteBuH3REA4cLnT99241NIHziaO0icaml9Eqqdve1E9DsDeVArkg/640?wx_fmt=gif&tp=webp&wxfrom=5&wx_lazy=1)

付一韬，高级 NLP 算法工程师，曾就职于汽车之家、新浪等公司，现任中移动信息技术有限公司的智能问答产品算法技术负责人。拥有多年丰富的 NLP 算法落地经验，擅长文本分类、信息抽取、知识图谱和智能问答。

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640)