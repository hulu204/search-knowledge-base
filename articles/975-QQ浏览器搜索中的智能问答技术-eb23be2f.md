---
title: 'QQ浏览器搜索中的智能问答技术'
company: DataFun
tag: 问答/RAG
date: 2022-09-13
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247595025&idx=2&sn=196bc2207c4dd653c4a155498e2b73c8&chksm=fbd6c67dcca14f6b21576e316564346cf85eb39de60dab2a4d51f34348cbd1b6c4989687ce01#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhmUd5UXOkFRiaj1Dhy972icTQGmBrf64u32betCPH13OaricuqRmoMJP39YZsrBpsLuFgFct54jusqg/640?wx_fmt=png "NLP峰会.png")

---

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdVufwhmB6j3gZSNuWfX0AT8WLazXibJr75lQOOct91cXbuFmLSj8yhXQ/640?wx_fmt=png "截屏2022-07-05 下午6.22.56.png")

分享嘉宾：姚婷 腾讯 专家研究员

编辑整理：王惠灵 合肥工业大学

出品平台：DataFunTalk

**导读：**智能问答是人工智能领域中一个比较受关注的方向，目前广泛应用于各种垂直或综合的搜索引擎、智能客服、智能助手以及智能手机、车载音箱等。本次分享的主题是QQ浏览器搜索中的智能问答技术，主要分为以下几个部分：

**1.背景介绍**

* 智能问答在搜索中的应用
* 搜索中的Top1问答

**2.关键技术**

* 搜索问答的技术框架
* KBQA：基于知识图谱的问答
* DeepQA：基于搜索+机器阅读理解的问答

**3.前沿研究**

* 端到端问答
* 知识指导的问答
* 多模态问答

**01**

**背景介绍**

**1. 问答在搜索中的应用**

问答的核心是通过理解语言和运用知识来进行提问和回答。从应用角度看，由于人类有获取信息的需求和旺盛的好奇心，问答的场景无处不在；从研究角度看，问答是认知智能的前沿之一。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdpUsyIPccwPOrzMliaOkNTgSjYLPTB8mwibibHcXl3JDsu8v26hDibvOZEA/640?wx_fmt=png)

问答在搜索场景的应用可以分为两类。一类是满足用户的直接搜索需求，即在搜索结果页给用户提供精准的答案，例如Top1问答卡片。另一类是通过问答的方式与用户交互，来帮助用户澄清、细化和延伸需求，例如推荐和对话形式的问答。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMd06QcQ2ktiaJ3Xv4CwjjJ6OR4pqIz4CyBGkiaPvKqMFZRTvQh8FoSUFyQ/640?wx_fmt=png)

**2. 搜索中的Top1问答**

下图展示了QQ浏览器搜索中Top1问答的一些产品形态，包括短答案、长答案、列表答案、视频答案、集合和图片答案。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdRtJUibqiau2DD3rgeTUZhLB3On4fG8V4optZqnc8zYbXJHcVibktd5D0w/640?wx_fmt=png)

**02**

**关键技术**

**1. 搜索问答技术与系统**

搜索中问答的明确需求占比接近1/4。这些问题不限领域，不限类型，一般可分成事实类和非事实类。搜索中问答的数据源是多种多样的。从资源类型上看，包括网页、UGC（用户生产内容，如社区问答）和PGC（专业生产内容，例如自媒体号）。从文本的组织形态上来讲，数据可以分成结构化、半结构化和无结构化三种。结构化的数据具有一定约束，以知识图谱为代表；半结构化数据的典型代表是开放生态构建或者从社区问答抽取的具有一定格式的问答对数据；无结构化数据广泛存在，例如普通的网页文本。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdrdfSRyQic6URTW81lj2auIrIqn0OKBJmPCfMdjKz9A4TLl76iaurNZaA/640?wx_fmt=png)

搜索中的问答技术主要分为KBQA和DeepQA。

**KBQA指基于知识图谱的问答**，面向的是结构化数据，底层是离线构建的知识图谱，在线通过问题解析、图谱查询和推理得到答案，主要适用于事实类问题。

**DeepQA是一系列基于搜索和机器阅读理解（MRC）的问答技术**，可以处理更广泛的非结构化数据，基于离线问答内容构建和理解，在线通过搜索获得候选文档、使用机器阅读理解技术来抽取答案，能解决更多问题需求类型。在实际应用中，针对不同类型的数据，我们构建了三套DeepQA系统，分别是优质问答数据源上的独立检索系统、全网搜索结合在线MRC的通用问答系统、以及端到端问答系统。

**下图右侧展示的是搜索问答系统的整体架构**。离线部分是问答内容的构建和理解，比如对专业生产内容做质量和权威性分析、从全网数据中进行问答对的挖掘和选取等；数据源包括网页库、优质问答库和知识图谱；在线部分包括搜索问答结果的召回和排序、段落匹配和答案抽取、知识图谱检索和推理计算等，以及问答融合决策从多源结果中决定最终展现给用户的答案。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdUVW4icpPcPBmxWzvhhI1LNicHDV1MBSpNCe0dPkrnuE9NCmicshEjLJcg/640?wx_fmt=png)

**2. KBQA：基于知识图谱的问答系统**

图谱问答系统的数据依据不同实体更新的要求分为三路，数据通过直接的三元组索引查询或者图数据库存储检索系统应用。

在线图谱问答的流水线之一是语义解析的方法，系统先对查询进行领域分类以装配不同类型的处理流程（例如汉语诗词类、单实体类、多实体关系类），然后对查询进行语法树分析和形式逻辑规约，在三元组中递归查询和拼装得到最终答案。该方法的优点是支持一些复杂的查询推理，且在规则适用的范畴内准确率较高。另一种流水线是基于深度学习的方法，系统首先识别出具有问答意图的查询，然后通过深度模型识别查询问题中的实体，对实体属性和查询表达进行深度语义匹配映射，计算出候选结果并进行清洗和排序得到答案。该方法的优点是对查询语义理解较好，泛化性强，召回率较高。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdw1sdIZzwbW0XgHGEibDKfXRG5SuyAdwnmLGdFVia5eErH0ciaqBukCCQQ/640?wx_fmt=png)

**3. DeepQA：基于搜索+机器阅读理解的问答系统**

下面主要围绕DeepQA相关工作展开介绍。

早期的DeepQA系统具有非常复杂的流水线，例如IBM的Waston，以及2017年第一版“立知“问答。系统包括多个数据挖掘和机器学习模块，在问题分析、答案候选的特征抽取、评分排序等诸多环节都可能有错误的传播和积累，可扩展性不强。2017年以后，斯坦福的陈丹琦等人提出了一个面向规模文档集的开放域问答系统——DrQA，系统定义了一种新的开放域问答实现方式，即通过检索和深度机器阅读理解（MRC）产生答案。在SQuAD等公开数据集和评测的推动下，深度机器阅读理解发展迅速，在查询和文档语义建模、上下文信息交互建模、答案抽取和预测方式建模上都不断涌现新的方法，2019年机器阅读理解系统甚至在事实类问答上超过了人类水平。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdt27cDLLkmpl4MHwpxgm4ogBSrdUTJsUp2qFR8y7icdo0JntFOpo9tCQ/640?wx_fmt=png)

然而在真实的搜索场景中，DeepQA仍然面临着很多挑战。首先是用户的需求纷繁复杂，表达方式也千差万别，而互联网数据规模巨大，需求检索匹配的难度很大。其次是网页数据多种多样，页面类型和格式繁多、质量参差、答案的形式不一，机器阅读理解面临较大的挑战。

下面介绍一些应对搜索场景的问题我们所做的工作。

**（1）短答案MRC**

短答案MRC任务的定义是从搜索结果的多个文档中抽取唯一的答案片段，并提供支持答案的文本来源。这个任务会面临以下一些挑战：

**①搜索结果噪声过多**

噪声包括不相关结果、不一致答案等。短答案抽取模型是一个多文档段落抽取的模型，我们将搜索排名topN（常用N=10）的文档段落输入到BERT中进行表示建模，然后预测段落中答案的起始位置。为了解决输入文档不相关的问题，我们将“答案存在性判别”和“答案起止位置预测”两个目标进行联合训练；为了应对各文档的答案不一致问题，我们加入了多文档交互，将多个文档中包含答案概率最大的片段拼接起来进行建模，信息融合之后再预测文档包含答案的概率。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdq2PzjXmLc2zxZorhqfqn1H0aXAACYRAb6sVQ1lA6SBQparkg0wdIlQ/640?wx_fmt=png)

**②答案出现常识性错误**

常识性错误即模型输出无意义答案，例如边界错误、答案类型错误。我们的做法是引入一些外部知识，例如百科、知识图谱等，给候选文档中符合答案类型的实体打上特殊的标记，在建模过程中加强对它们的关注。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdiavW5OiakQ7LaZibiaLibDe3ia29GYwT2CNpGvBKOwrqKmuDEZqsXhPJrvSg/640?wx_fmt=png)

**③鲁棒性问题**

这里鲁棒性问题指的是由于过拟合导致模型输出不稳定。Dropout是一种有效的减少过拟合的方式，但它的缺点是不能保持输出的一致性。我们应用了R-Drop，通过将Dropout作用于输出层，降低了训练和测试的不一致性，同时引入对称KL散度作为正则项，增强了输出的稳定性。在实验过程中，我们发现对输出层使用两次dropout效果较好。此外我们还对训练数据进行了同语义问题的数据增强，加入相同语义query下的段落输出部分的KL-Loss，增强了模型的稳定性。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdOIStbBF4N7CiamYw39Gl2tQZNdmH7LQqo1NdFEz6PHZPPpe6E9Ileog/640?wx_fmt=png)

**④答案归一化和多span问题**

在抽取式阅读理解中，由于多文档表述的不一致，往往会遇到答案归一化的问题，比如“安全带使用期限是几年”的问题答案可能有“3到5年”、“3年至5年等”；而且还有答案并不是连续判断，比如“沉鱼落雁指的是谁”这个问题中，答案可能对应文档中两个片段（span）。为了解决上述问题，我们尝试用生成式阅读理解方法，以Fusion-in-Decoder（FiD）为例，将检索得到的多文档分别进行编码表示，拼接起来输入到decoder生成统一的答案。

实践中利用大规模点击日志文档生成查询进行预训练，利用短答案日志构建大量弱监督数据进行自训练，有效提升了生成式阅读理解的效果。由于生成模型输出的答案得分其实是语言模型的困惑度，不能很好地刻画答案本身的置信度，我们训练了一个生成答案的置信度预测模型，对答案输出进行决策。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdLrVV4XLQtBhbVdfMqMHk39sKIGic19m8iaYmIasnU1XOfMJtwMy6WnLw/640?wx_fmt=png)

**（2）长答案MRC**

相比短答案，长答案MRC受到的研究关注相对较少，一方面因为问题更加复杂，数据集稀缺，另一方面因为长答案在内容和表达方式上有不确定性，评价起来也相对较难。

搜索场景中长答案和短答案主要有以下几个方面的差异：

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdg2aeTwtPpYiajMYI60gD0du0oTMsuMZp6NFKq9MGlhz4YVb26NCghMw/640?wx_fmt=png)

**①长答案MRC-组合式问答**

针对长答案包含信息量大、不连续的特点，我们提出了一种“组合式问答”的任务形式：从搜索结果的单个文档中抽取出一组片段来合成精选摘要答案。任务输入为给定问题和文档的完整片段组合，输出为答案片段组合。评价方式为片段预测的F1和人工评价相结合。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdqLOb85IZnPoGLJqLBB6r6GwJITfDYTgvyvm4Kpte1fHn0CSkiasNcDw/640?wx_fmt=png)

组合式问答模型的整体框架基于BERT，输入是问题和进行了启发式分句的文档句子序列，输出是每个句子是否是答案的概率。**我们引入了两个非常有用的设计。**

**第一个是引入页面的结构信息**。由于网页的HTML能够一定程度上反映页面结构、文本关联以及展示内容的重要度等特征，我们选择了部分网页标签作为符号输入到模型中。

**第二个是引入针对性的预训练任务。**—般预训练都是建模句子级别的关系，没有有效挖掘文档结构的信息；我们引入了两类相关的预训练任务，一类是问题选择（QS），即随机替换一个问题并预测；另一类是节点选择（NS），可以对句子和符号进行随机替换或打乱顺序。这样的预训练任务可以让模型更深刻地理解问题和长文本的内容。

由于文档具有层级结构，一个自然的想法是利用图网络来建模。我们尝试在模型输出侧增加图网络，将句子中词的连接、句子之间的连接以及问题和句子的连接用图结构表示并通过Attention Mask实现，实验表明加入层次结构信息的效果提升明显。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdIicQ7ibLaOhQKe7kGFCfndpWqwuUQbbuXA10Smt0OHKNtpNgSFeV48yA/640?wx_fmt=png)

长答案阅读理解中同样可以采用短答案阅读理解类似的**思路**：（1）同时预测文档可答概率和答案句子概率；（2）引入门机制学习文档和句子的关系；（3）使用R-drop提升鲁棒性。

我们发现模型对问题的理解仍然不够充分。举一个极端的例子：当不输入问题，直接针对文档预测长答案，模型仍然能够达到一定的抽取效果。说明阅读理解模型输出的答案受到文档本身的影响较大，而对问题的关注不够。为了解决这个问题，我们做了一些数据样本增强和对抗的工作。一方面通过主动学习不断优化训练数据，让模型学习到更多不会的能力，另一方面通过点击日志挖掘同一个文档下语义相同或不同的query。由于同一个文档中的不同部分可以回答不同的问题，这样可以让模型更关注问题相关的信息，而不是文档本身。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdaiboOpqNarC1WsomKBliarHsxiceMcZpZbibLkDBD9HJAD4yGFV0EQ4Fvw/640?wx_fmt=png)

**（3）长答案MRC-判断类观点问答**

对于判断类观点问答任务，考虑到用户不会仅仅满足于论断，而会更关心论据，我们设计了一个模型，首先抽取能够回答问题的长答案，即论据，然后根据该论据做论断的分类，产生一个短答案。

模型的整体结构是基于长答案模型结构的改进，在抽取长答案的同时，将query、title和长答案抽取过程中最高概率答案句拼接起来输入判断模块。通过论据抽取和论点分类两个目标的联合学习，模型可以解决短答案抽取无法解决的问题。比如在下图的例子中，对于“把兔子关在笼子里好吗”这个问题，短答案抽取并不能直接抽取出“好”或者“不好”的答案片段，而通过分类可以知道它是一个否定的回答。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdVnKvUQlMIiaTx9qMz2MiclDFh8ZqKbbQkKT0icTNoa91PG5ibohvMdM0eg/640?wx_fmt=png)

**（4）问答式搜索**

DeepQA的一个重要部分是从大规模数据检索出相关候选文档，才能通过阅读理解模型抽取答案。传统搜索更关注相关性，即文档和问题相关，而问答更关注检索结果是否能回答问题，这是问答式搜索和传统搜索的不同。

问答式搜索系统需要一种更细粒度、更精准的语义检索匹配方式。稠密段落检索，即通过深度语义表示学习，从大规模文本中检索出和查询相关的段落，包括自然段、任意句子、词片段。稠密段落检索是稠密向量检索的一种。传统基于关键字词构建的倒排检索（稀疏检索），虽能精确地召回结果，但是会面临比较严重的语义鸿沟问题；而稠密向量检索是解决查询和文档之间语义鸿沟的有效手段，但是从符号到向量的表示过程损失了一定的语义。所以需要对稠密向量表示进行优化，并设计合适的向量检索和语义匹配方法。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdnIRwQLpuZS6LAe56xa1QRibNZjpJ2DsIRK8LAO1BxRCvoxfDDYaAribQ/640?wx_fmt=png)

问答式搜索也是一个从大规模数据到少量能抽取答案的文档的金字塔式筛选过程。为了提高在线服务效率，在面向海量数据的召回和初排阶段一般使用非交互式匹配模型，待检索到一定规模的相关候选后再采用更精细化也更加耗时的交互式匹配模型。交互式和非交互式匹配模型各有其优缺点，如图所示。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdlOpG2d9wKqADmBFVCzzqra46zzpfMiasqpbPTzrT2c2iaMib3dTt1xgdg/640?wx_fmt=png)

* **稠密段落检索模型**

我们选用非交互式异形双塔模型进行稠密段落检索的Query-Passage语义表示学习。通过网页搜索日志和问答对数据可以获取大量的正负样本，从而进行大规模对比学习。

这里介绍一种向量表示的优化方法——Barlow-Twins。通过在训练目标里加上一个相关性去除目标，降低向量表示的冗余性，使得训练出来的向量在空间的分布非常均匀。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdWz8QGlalohQbVaBp4kAiblZJNx1SlEzEyY7OjJNKvvNrByEG8icSTpxg/640?wx_fmt=png)

负采样方法是对比学习中非常重要的一环，对稠密向量表示效果有很大影响，我们对负采样进行了两个方面的优化：

一个是很多相关工作都会采用的Cross-batch负采样，在多 GPU 并行训练时，将其它 GPU 批次内的全部段落作为当前问题的负样本，极大地增加了负样本数，也使得训练效率得到很大提升。Cross-batch负采样还能缓解训练和推理时负样本分布的不一致性，因为在问答式搜索中，模型需要从大规模数据集中找到相关答案候选，但训练过程见到的查询段落样本通常远小于预测时的候选数据规模，这会导致模型在训练时表现良好而在应用中不够好。

另一个是提升负样本的质量。一方面需要让负样本对模型来说更难，这样能学习到更多的知识。另一方面要尽可能少地引入False Negative样本。我们提出了混合降噪负采样策略：先通过非降噪负采样，例如已有的召回模型（BM25、初始训练的召回模型等）进行Top-K采样，这样得到的样本相对较难，当然也会引入一些False Negative；然后进行降噪负采样，通过训练一个Re-ranker对样本进行筛选，去除实际可能是正例的噪声；两者结合训练，实验证明效果提升非常明显。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMds2JlplfQEARsBBJRRl03tIeRwqUMt8YZelDQtsgOueH6RhWjEXv7Wg/640?wx_fmt=png)

* **Query-Passage交互匹配模型**

召回阶段的核心任务是区分答案相关和不相关的候选，召回之后就需要通过匹配更进一步排序这些候选文档。这里简要介绍一下我们的Query-Passage交互匹配模型。

模型训练主要分三个阶段，首先利用大规模网页数据，包括百科、微信、知乎以及问答点击页面等多样的数据进行预训练；接下来是对比式弱监督训练，通过点击和曝光未点击数据、问答对结合负采样构造正负样本；最后在人工标注的问答匹配数据上进行训练。人工标注的样本有四类标签，分别是完全不相关、相关、能部分回答问题、能完整地很好回答问题。为了进一步提升模型效果，我们还使用了自训练技术，利用人工标注数据训练模型之后，通过该模型进行大量的自动化标注并从中筛选一些高质量标注数据，继续训练原始模型。多次迭代之后，模型的泛化性能会有较大的提升。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdsN0XofSibicJcWn0FsLvGBK6icUibqnCcFl5WvtpKcDXj9IibG9GRuiaTE1Q/640?wx_fmt=png)

**03**

**前沿研究**

下面介绍开放域智能问答的一些相关前沿研究和进展。

**1. 端到端问答**

近年来关于开放域端到端问答的研究如火如荼，下图摘自ACL 2020 Tutorial: Open domain question and answering，对端到端问答系统发展的总结。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMd37kHxqGrMJSw6E8zicmFMdMiclTLJFHFJTDK0UOnUupib0fCzaGprhvxQ/640?wx_fmt=png)

第一代端到端问答模型采取两阶段的方式，通过检索器和阅读器串联来进行答案提取，例如DrQA；前面我们所讲的DeepQA系统也是遵循这种范式的设计；第二代的模型为阅读器和检索器联合优化的模型，如R3、DenSPI；第三代的模型不需要检索器，直接通过模型生成答案，如T5、GPT3。

检索器和阅读器的联合优化是一个难点。一种方法是将检索的文档看做隐变量，依靠EM优化语义表示模型和生成模型，即通过阅读器的输出概率作为检索器优化的目标，反过来再基于检索器的输出优化阅读器的输出概率。这样交替进行同时提升阅读器和检索器的效果。我们尝试了一种Hard-EM的方法，直接把预测答案是否包含于检索文档作为硬匹配信号来优化文档检索的过程。如下图所示，通过答案硬匹配文档获得训练三元组<q, d, a>，然后训练FiD答案抽取模型，再利用新的答案抽取模型预测出来的更优质的答案，继续硬匹配和过滤候选文档输入。几轮循环之后答案抽取的EM和F1指标均得到提升。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdzcGMuicgDbDyMaHWVhr96Z41jOwp5Zic9duj73UCMhy8xFm7zYxkcw2A/640?wx_fmt=png)

**2. 知识指导的问答**

如何在深度模型中引入知识也是问答研究的热点。真实场景中有很多问题需要知识推理，比如“小汽车科目二多少分及格”这个问题，示例的法规文本里没有明确的描述，但是可以根据推理得到答案；“葡萄籽油的食用方法”这个问题，不同答案中包含的“知识点”相互存在冲突和分歧，需要进行知识验证。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdH5aGwXwKICtJjIibe56QB4uPAJmSpbm74batRdO4zY8P87mqDUIFgZA/640?wx_fmt=png)

知识指导的问答相关工作，有一种是把特定的知识输入到答案抽取模型一起学习，比如K-BERT，把原输入中实体所涉及到的三元组通过软位置编码的方式融合到输入中，从而引入了实体相关的知识。另一类方法是通过知识增强的预训练模型提升下游任务的效果。

QQ浏览器搜索内容技术团队还提出了一种知识增强预训练的方法，该模型引入了三类知识性任务，包括远程关系监督分类、三元组文本mask预测、以及同类实体替换预测，训练过程中将这三类任务和语言模型任务结合在一起训练。为了保证原始模型的参数在训练过程中不会有灾难性遗忘，设计了一个新的知识记忆结构，将原有模型的所有参数固定住，只用这个新的知识记忆矩阵承载上面多任务引入的知识。实验证明知识增强的预训练在很多下游任务上都能够获得一定的提升，尤其是在上下文不充分的短文本任务上。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdOwmcTm2OFdMV3DTe200P1Vt5SmBBCEnpByJcnb7rYthsqOU9K6Yrcg/640?wx_fmt=png)

**3. 多模态问答**

当前越来越多的优质内容以视频形式存在，从文本答案到视频答案也是一个大的趋势。基于视频载体的问答需要对视频内容进行感知分析+语义分析，进而通过显示/隐式的语义表示和计算（检索、匹配、阅读、生成）得到视频化的答案。

我们现在做的一个比较初步的工作是利用视频的语音和字幕进行视频文本化，然后通过阅读理解结合文本生成的技术进行视频答案摘要，通过文本生成和字幕时间匹配，还能得到视频分段以及关键帧标签。右图是我们在视频问答做出来的短答案摘要的效果，相对于文本答案可以给用户提供更多便捷性的帮助。未来还有更多基于多模态内容的问答研究值得探索。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdGAzibhyUrqpptx4cQhHyNpRZjw1NibHW5sgdG2JWp4RjNG7CoOJQpWNw/640?wx_fmt=png)

**04**

**Q&A**

**Q1：针对用户的query，KBQA和DeepQA的执行顺序是什么?**

A1：两者是同步进行的，最后根据答案产生的情况做决策。DeepQA这边还会有一个问题分类的模块，判断问题的答案是短答案还是长答案。所以底层是多个系统的并行，包括KBQA系统、短答案系统和长答案系统。

**Q2：自己尝试后发现DeepQA的响应非常慢，工业应用中通过什么方式来提高问答响应的速度?**

A2：响应的速度分为两个方面，检索模块和阅读理解模块的响应。需要看这两部分分别耗时，也需要分别优化。检索模块往往会通过分层筛选的方式来限制输入文本的数量。计算越复杂的模块，输入文本数量越少。召回阶段我们采用非交互式模型快速获得相关文本，排序阶段再使用更复杂的交互式模型进行少量精细化计算。最后阅读理解模块的文本输入相对更少了，目前只针对Top10结果去做计算。以上是系统层面的优化。

具体到模型优化的话，可能就会需要具体看输入的文本长度、模型复杂度，模型所使用的推理系统，推理器和硬件的匹配情况等。最主要的是需要去分析响应时间慢的瓶颈的问题，然后再针对性解决。

**Q3：针对用户的query也会有拼写纠错的处理，什么时候会触发这个处理？怎么处理?**

A3：纠错不是问答独有的问题，是整个搜索系统面临的问题。在搜索的最开始也就是查询分析的模块，不仅有纠错，还有查询的分词，查询重要度的分析，查询词之间的关系分析等。纠错往往是搜索前置的模块，纠错之后的处理也会有不同，比如对置信度非常高的纠错，可以直接修改查询。系统更保险的做法是触发二次查询，也就是将原词的搜索结果和纠错后的搜索结果同时拿到，然后再根据结果的反馈综合决策。

‍

**今天的分享就到这里，谢谢大家。**

‍

---

在文末分享、点赞、在看，给个3连击呗~

---

**01****/****分享嘉宾**

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPg5uZSQKuohGHiaFPXq9WicX5TUBPOvpftJA9kD6zaPxeTKIFny9j3rsnNKnYHuWqa5Qq5B3icpx38sg/640?wx_fmt=jpeg)

**姚婷**

**腾讯**专家研究员

---

毕业于清华大学计算机系，从事自然语言处理、搜索排序、智能问答方向的研究工作，负责主导了搜狗搜索“立知”问答系统研发。目前担任腾讯PCG搜索应用部专家研究员，负责QQ浏览器搜索中智能问答技术的研究和落地应用。

---

**02/免费下载资料**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPjzgVcygl8VzOvFCFTicRibMdO07XROFbonFhTjOh7KmWhwQoeofewHIH4hhLyUqHIFXPZT7lrxvTUw/640?wx_fmt=png "算法专题书.png")

**03****/****报名看直播 免费领PPT**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiadT56pcrUJNhpgkUuoOX4gT7GLRByuHWeZRyicUafyBqzTaKib55ibT5unw0y6Nib30VUiaIUBpHU8NUQ/640?wx_fmt=png "公众号尾banner.jpg")

**04****/****关于我们**

**DataFun：**专注于大数据、人工智能技术应用的分享与交流。发起于2017年，在北京、上海、深圳、杭州等城市举办超过100+线下和100+线上沙龙、论坛及峰会，已邀请超过2000位专家和学者参与分享。其公众号 DataFunTalk 累计生产原创文章700+，百万+阅读，14万+精准粉丝。

🧐 **分享、点赞、在看**，给个**3连击**呗！**👇**