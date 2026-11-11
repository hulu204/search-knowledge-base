---
title: 'Hulu：视频广告系统中的算法实践'
company: Hulu
tag: 广告
date: 2019-02-25
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247488177&idx=1&sn=ce32c5e9eaf50c9d7f5f3f075d632fc3&chksm=fbd4a0ddcca329cbc93e4fded3b83d59c7ab30d64206a1cf80e63289f925635bcf7eba6651a5&scene=27#wechat_redirect
account: DataFunTalk
origin: readme
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF8B5V67zohibmm1AFaibs6dM3RK60iaOrUAqdCUNVGGXODIO8rCSNpJrOg/640?wx_fmt=png)

> 分享嘉宾：李凡丁 Hulu 软件研发工程师
>
> 编辑整理：程晓杰
>
> 内容来源：DataFun AI Talk《What is Hulu thinking when you are watching Hulu?——NLP research and practice in Hulu》
>
> 出品社区：DataFun
>
> 注：欢迎转载，转载请注明出处。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF28EOu1KgzsZUiapmx9iceuO9Q76H1SJxfToLeiaLEhlJfSYTdATVVibOWw/640?wx_fmt=png)

> 前言

“当你在凝视深渊的时候，深渊也在凝视着你。”当你在看Hulu的时候，Hulu以及它背后的那些算法工程师们又在想些什么？不妨，就通过我加入Hulu以来的经历，一窥自然语言处理研发工程师在Hulu做的一点微小的工作。

本文共讲三件事，看似没什么内在联系，却是一个NLP研发工程师的切身体会和感悟。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFaFWqJrhwSAdWAjdaPIjFicx1zk7jlGyvjzFYKhQPTuibVpiaPZMEpVic1g/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFHLI1CMCFWnja2ticr26eSSZrnrkCOQjoyJxFrSsCxKSLzQpeSkSx82g/640?wx_fmt=png)

> “以史为鉴，可以知兴替”
>
> 从NLP简史出发，叩开NLP应用的大门

时间、人类、未来，都有人写其简史，NLP作为当下AI研究的热点之一，似乎鲜有人总结它的兴衰胜败。但毋庸置疑，NLP (Natural Language Processing, 自然语言处理) 涉及领域众多——语音识别、分词、词性标注、句法分析、文本分类、信息检索、自动摘要、QA、机器翻译、对话机器人、阅读理解，几乎所有跟自然语言沾边的话题都可以划分到NLP领域里。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFzghJFxttfprskr0EIibI0KsIxfvRRiaVibs78BvhTqSXhM9NI1wNyWgog/640?wx_fmt=png)

在2018年10月底，Google推出的论文BERT可谓一鸣惊人，在NLP界引起了轰动。BERT之前，哪些工作和模型可以进入NLP名人堂尚未有定论，但从文章引用数和影响力的角度不难看出一些端倪，将以下三个工作列为近20年NLP的发展具有里程碑应该并不为过。

· 2003年Bengio的NNLM；

· 2013年Mikolov的Word2vec；

· 2017年Vaswani的Transformer；

在这三个模型之前，研究者针对NLP的不同任务，通常采用各不相同的模型架构去处理。比如命名实体识别任务用HMM隐马尔科夫模型或者CRF条件随机场；再比如文本分类任务应用词袋模型、主题模型提取特征，再用LR逻辑回归或者SVM支持向量机做分类。而这三个模型，都可谓时代的开创者，被记录在NLP的史册中。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFbMEJ3hKl7nlicV3GLcOrHNiatGnvN2W7Qvc5CHMRa6yicNUnNiaRGXvZ3A/640?wx_fmt=png)

#### **1. NNLM (Yoshua Bengio, 2003)：**

上图可谓是上古时代的一张结构图，以现在的眼光来看，它其实就是一个非常简单的三层神经网络模型。沿袭语言模型（Language Model）的目标，即用前n-1个词来预测当前的词是什么，NNLM只是把这个预测模型换成了神经网络。但在当时，由于这个模型最后一层是个结点到个结点的全连接层（为词向量维度，为词表大小），模型参数过多，而且当时计算力也并不算强，训练一个NNLM模型可能需要几个月的时间。而且，针对不同任务需要训练不同的NNLM模型，资源消耗极大。但无论如何，这篇论文都具有划时代的意义，因为它统一了NLP的特征形式——即Embedding。在此之后，我们做各种NLP任务时，一般都用词向量（word embedding）的形式来表达一个词。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFy6OiciaLqurHS714TFv0g17oD2sGDZ3sRoYo3Rd2WSiaqibj8uuf6jbJ9w/640?wx_fmt=png)

#### **2. Word2vec (Mikolov, 2013)：**

从模型的角度看，Word2vec比NNLM更简单，因为它其实就是一个线性模型。但正靠着模型的大幅度简化，以及2013年深度学习和其硬件的飞速发展，Word2vec可以依赖大规模语料进行快速训练。从革新的角度，它不仅延续了NNLM的特征形式，而且不再需要针对特定任务从头训练模型，而是在一个大规模语料上先进行预训练，再利用类似迁移学习的思想，把预训练好的embedding应用到其他下游任务中。

回看当年的历史，计算机视觉之所以能蓬勃发展，很大程度上靠着ImageNet这样一个大规模、有标注的数据集。在自然语言处理领域，却并没有一个如此大规模的标注数据集。怎么办呢？从另一个角度出发，人们发现语言这个东西，在说出来或者写出来的时候就已经成为很有价值的数据了。Word2vec正是利用了人类语言学高度抽象、高度概括的特点，在一个大规模语料中训练语言模型，再将语言模型里学到的信息（embedding）应用到下游不同的NLP任务中去。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFBbaqhvmJc5jRGyZ12mI6JaJibjkBd92y33dKt6JBia5ApB3GXM6FkOVg/640?wx_fmt=png)

#### **3. Transformer (Vaswani, 2017)：**

Word2vec在NLP届问世以后，大家通常采用Word2vec作为embedding的初始值，再利用RNN、CNN、attention等深度学习模型去训练下游任务。此时，文本分类的主流模型已经变成了LSTM, charCNN等，命名实体识别领域也大多被LSTM+CRF的框架所占据。人们不禁开始思考：统一了embedding这种数据特征形式和pre-train这种特征预训练方式，我们能不能用统一的模型来处理不同的NLP任务？2017年Transformer应运而生，像无所不能的变形金刚一样，Transformer放弃了RNN、CNN的结构，完全只用注意力(Attention)机制构建模型，处理多种NLP任务。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFLru2ib6NmkXIsW5XmPABPBpAr1dFuBtqdfKibLoMWDJfx57OScVLHrlA/640?wx_fmt=png)

鉴于Transformer的模型结构较前两者复杂许多，而且又是最近一年NLP届的耀眼新星，我们不妨细看一番，以探其究竟。从结构上，Transformer可以拆分为三个部分：1）Multi-Head Attention；2）Feed-Forward Network；3）Position encoding。

A. 多头注意力Multi-Head Attention

如右上图所示，Multi-Head Attention是由Scaled Dot-Product Attention单元堆叠而成的。Attention机制想必已是耳熟能详，简单来说Attention就是seq2seq 模型中Decoder在进行解码时，学习Encoder输入中各词的权重分配。Dot-product Attention是Attention的一种形式，它把注意力表达成Q(query), K(key), V(value)三元组。其中Q是待生成的序列，V是输入的序列，K为权重。例如机器翻译任务中从源语言翻译成目标语言，V表示源语言序列，而Q就是待生成的目标语言序列；每产生Q中的一个翻译词时都需要计算与输入V中哪个词最有关系，这便是注意力权重K；Attention层之上，再经过一个softmax预测真实的翻译词。Scaled则是指在softmax计算之前，进行尺度缩放，除以跟Q和K维度有关的一个量，用以防止点积时数值过大。如果其中Q=K=V，我们一般又称其为self-attention。

把很多Scaled Dot-Product Attention单元堆叠，如同卷积一样形成通道形式，然后将结果级联到一起，再经过一个线性映射，这便是Multi-Head Attention的过程。

B. Feed-Forward Network

通过Multi-Head Attention层后，再经过一个前向神经网络Feed-Forward Network，用以增加网络的非线性。并且这个FFN添加了像ResNet一样的shortcut连接结构。

C. Position Encoding

因为在attention机制中每个词都会关注前后所有的词，导致所有词在位置信息上其实是等价的，所以Transformer中引入Position Encoding表达每个词在原始句子中的位置信息，来弥补这一缺陷。Position Encoding既可以用一个固定的函数表达，也可以用一个可学习的函数表达。实验发现两者效果差不多，干脆就采取固定的，sin族函数来表示。由于sin函数的特性，一定程度上还可以有效地表达句子中词的位置的周期性。 

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF3ZWsDPOZoWypUvqg5fQknOMapafUa831FZLx843vQn9MykEhsyHYAw/640?wx_fmt=png)

从整体上看，Transformer结构的左边是Encoder部分，右边为Decoder部分。Encoder堆叠了6个Multi-Head Attention + Feed-Forward Network + shortcut的结构。Decoder同样堆叠6层这样的结构，然后与Encoder的self-attention结果共同送入Multi-Head Attention，预测最终的输出。 

那么，Transformer结构为何能饱受青睐呢？首先，使用Attention机制后，每层的复杂度比RNN要小。再者，RNN是一个递归的模型，t时刻的计算需要依赖t时刻前的状态，很难进行并行计算。而Attention结构可以很容易地支持并行，因此可以用到更多的数据。另外，Attention机制解决了一个RNN里一直以来很难处理的长距离依赖问题。RNN中诸如LSTM模型，虽然添加了遗忘门等机制，但是依然不能很好的解决长距离依赖。Transformer由于会关注输入的每一个位置，因此可以很好的解决这一问题。Transformer也于是在之后几乎所有NLP相关的任务都展露了锋芒。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFXZtnyJsSTfKKk4FoK8gBzpMicSUE4TW4gg7u03FtmibcJ8BmanAAszqg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFacQy0TCM2JLtr1a5v31u58mOU475yGodgAocTGNaqGWoaviciaeT47Zg/640?wx_fmt=png)

#### **4. Bert：**

至此，我们既统一模型架构，也统一特征形式，下一个问题也自然而然——能不能在大规模数据集上训练一个Transformer，然后再用到其他各式各样的下游任务中？其实，包括AllenAI的ELMo，OpenAI 的 GPT，Google的Bert等，都在做这样的尝试。其中Bert从2018年10月提出便一骑绝尘，引起NLP届广泛关注，凭借的是其惊人的效果。用论文中原话来说，Bert是一个理论上非常简单，但是非常有效的模型，它在11个自然语言处理的任务场景中取得了当前最好结果，并且把GLUE benchmark提高了7.6%，在SQuAD数据集上已经超过人类表现。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF41oic10bwyfic9Zrubiajahw6PPRDIAaictpNwDQfRhYVqpFcUDXLJXniaw/640?wx_fmt=png)

上图是GLUE（General Language Understanding Evaluation）的榜单，GLUE将一些NLP任务集中在一起，可以评价一个模型在不同任务上的通用性。这个表是2018年11月份的统计，可以看出Bert当时技压群雄，比每个数据集之前最好的结果还要好。 

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFbgfo0w3kicVNbqmXwmnUUNABwDTbdeqh3qM7DOLwYvaOg4hyE65akhg/640?wx_fmt=png)

简单来说，Bert采用了Transformer中encoder的双向结构。在输入端除了有token embedding，position embedding之外，还加上了segment embedding。这主要是为了处理双句任务，比如判断两个句子之间的关系，以及Question Answering等，通过segment embedding来区分前后句子。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFa0QJhGHrFRAXtWnrJYjLxprkjMFr1kIHmrak0yrkRcxZjticDkyHfEQ/640?wx_fmt=png)

Bert的预训练包含以下两种操作，一是把句子里的一些词随机掩盖，然后让模型去预测这些词。另一个是用前一个句子来预测下一个句子。 通过优化这两个目标，Bert就可以在大规模的语料中进行训练了。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFQXJVPoR3KwEgbT3mIxjvMfB0kuAnnpg3cFZ4y2fMErLgbe1NziaDjxg/640?wx_fmt=png)

继承Transformer的优点，Bert自然也可以应用到多种不同的NLP任务中。文章提出了上图的四种架构，对应Bert四种不同的应用场景，既可以做分类任务又可以做标注任务、既能处理单个句子也能胜任双句任务，因此NLP很多问题都可以用以上模型来套用。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFCf1zcYbtgPT2yuYjh2qK0iafRwSMiawDTcax9wW4gCIfdGpBsiat1r8iag/640?wx_fmt=png)

#### **5. NLP展望**

在此也不妨分享一下我在10月底参加EMNLP会议时对NLP发展方向的一点思考。

A. 在学术上大家还是一直在追求纯粹的、优雅的、通用的模型。

B. 从现象上来看，会议中已经很少能见到非深度学习的论文，深度学习现在基本占领CV、NLP领域。

C. NLP在社会应用和工业届应用受到大家更多的关注。会议上有多个session讨论这个问题，而且参与人数众多，可以发现人们越来越关注自己的研究领域在生活中或者在产品中的应用。 这也引出我们下一部分要讨论的问题：学术研究和产品开发有什么区别和联系？这对很多刚毕业不久或还没毕业的同学来说，更容易引发共鸣和思考。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFHKeT7uaQDfcsSibJB9zefsM2R6fBICtSvQdwc1RZ3fPRFSjUStBQdicg/640?wx_fmt=png)

> “当学术研究遇到产品开发”
>
> ### 从一个算法研究工程师的角度，讲述从学校到公司的心路历程

以下将从5个方面介绍学术研究和产品开发之间的对比和利弊权衡：1. 问题的定义； 2.数据的处理；3. 模型的选择；4. 评价指标；5. 开发流程标准化。

#### **1.****问题的定义****：**

在学校时我们往往知道问题的输入是什么，只需要用一个合适的模型不断优化，来找到一个更好的解，提升模型的效果。但在公司场景中，更多时候你可能需要先定义问题是什么。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFI7kT4czEJbRjHK87YXpBTzZBCPyV6ibunhS7cEIhgpBCT5CTibUFJ8Jw/640?wx_fmt=png)

A. top-down和bottom-up：从问题产生背景上讲，问题主要分为两种方式定义：top-down和bottom-up。理想情况下bottom-up的问题一般是：你有一个创新点，然后去做一些实验进行验证，之后设计成一个小demo形式给产品经理查看，产品经理认为效果不错，再去做一些UX上的优化，最终成为一个产品特征。而top-down通常是：产品经理有一个需求，然后去找公司里哪个团队有这样的能力去做，他发现你有能力完成这个需求，找到你后针对这个项目去做POC (proof of concept)，在此基础上针对真实用户进行A/B测试，如果效果不错，最终就可以转化为产品特征。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFyYep6X1rMFKVsfVnYmPoNKPVVPKRFEOe0EFibF10CdAq7hhonkLGG1Q/640?wx_fmt=png)

B. Vagueness：但很多时候产品经理提出的需求是并不一定十分清晰，而是相对模糊，所以作为算法工程师，对问题，对通过技术能解决、善于解决什么问题要有自己的判断和见解，以此给出问题正确的定义。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF4eCNOaibb5BYeBSWhyHEdUR78pgVicFT38eckYhrlfDflgGGJ91U2qfg/640?wx_fmt=png)

C. Division：对问题要有划分，并且有策略。定义问题时需要分清哪些是重点，哪些是眼前亟待解决的问题，哪些是需要长远去看的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFdaZxPNc4fKVO3DdSQ2aic2Is0uGNuX5O7QI5fWqYfdaTju22IOaNMCA/640?wx_fmt=png)

D. Goal：先定一个小目标。在公司做产品，如果目标不同，对于问题的定义也不同。比如要分清是做一个PoC还是一个简单调研，甚至目标是做一个产品特征，这些都决定了定义问题时侧重点不一样。比如需要做一个demo，在模型的选择和实验上，就不必过分关注细节，更重要的是强调一个新的概念，新的设计或者功能。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFUIYiaSxRj41mMGnXdlAp1aTksFCFvom4qiaU5I2DjBmYTwhZqqzjQhOg/640?wx_fmt=png)

E. Cost Control：注意产品的成本控制，包括对时间、金钱、人力成本等的控制。在定义一个问题时也要考虑是不是对公司或者对问题解决的领域有长远影响？比如做一个机器学习任务，可能很多时候缺少标注数据。那我们在定义问题的时候就要计划清楚数据应该从哪来？是外包，还是自己上阵，亦或找一些实习生去做，都是成本控制所要考虑的问题。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF5Tfib87C0cIj5WLYJMZLQnLT1ib7FypWiao7ibfx0MCnBb9IDYg6icsSY9Q/640?wx_fmt=png)

#### **2.****数据的处理：**

A. 有哪些数据可以用？

Hulu有自己的视频，也包括携带的音频、字幕等，同时还有内容提供商给的一些演员、导演、类型、描述、标签等辅助信息。当然，我们还站在巨人的肩膀上，因为有很多其他组的同事、前人留下的各种各样的模型和数据供我们使用。

B. 应该使用那些数据？

数据显然不是越多越好，因为不同的数据有不同的处理难度。

C. 怎么用？

无论中英文，真实的数据中往往是比较脏的数据，显然从这些数据中训练好的模型是不可能的。在公司场景下，数据预处理是一个非常重要的环节，在NLP中包括对关联符号，标点，数字，人名等的处理，经过预处理的数据才能进入下一步，被模型所使用。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFCIcXn5EXwMX02tRmps8ibnSVRia6icgu3yxuVdHfEtZTk0pLKRo7dOARg/640?wx_fmt=png)

#### **3.** **模型****的选择：**

A. 无论做什么任务，都需要有前期调研工作，吸取前人之经验，看看在这个问题上成熟的、主流的方法有哪些。

B. 如果不知道哪个模型适合产品目标，可以先选一个最通用的模型。比如seq2seq问题就用我们刚才讲过的Transformer结构，序列标注任务用LSTM+CRF，分类任务选用TextCNN、fastText等模型。当然了，现在你都可以使用Bert。

C. 选择比较高效的模型。在公司往往要选更高效率的模型，先做出一个基准结果，评价此方法是否可行。比如公司产品开发周期为2-3个月，倘若你花很长时间调试出的模型最后效果一般无法使用，很容易就会陷入进退两难的尴尬境地。

D. 模型微调(fine-tuning)。对于模型fine-tuning分为两个部分，1) 对模型结构上的fine-tuning，比如说保留一个大模型的前面若干层，对最后的1-2层进行fine-tuning。2) 在模型的基础上加入一些人工规则。诚然，我们都在追求通用的模型架构，并且这也是AI前进的一个方向，但是现阶段的很多场景中如果不引入人工干预，单靠机器学习或者深度学习其实很难支撑产品级别的应用，所以fine-tuning有时需要一些针对用户、针对数据、针对结果的规则过滤。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFF1kLL9kAoJKxqGrPkvE76ZNIib0wJhM3mIGqrTLKeVIGSdvyib1ZIXqA/640?wx_fmt=png)

#### **4.** **评价指标**

A. 在学届，我们可能更多关注Accuracy、Recall、ROC等指标。但在公司，我们要更关注和用户行为相关的评价方式，比如展示位点击转化率CTR、用户的总观看时间等指标。

B. 采用多个版本的控制，将用户的反馈传递到模型中。比如要做在线A/B测试，但其反馈到模型的周期往往很长，这时就需要用多个版本来控制线上运行和线下实验的模型。

C. 警惕metrics trap。在学术界常用的评价指标在实际产品中往往并不适用。比如在机器翻译中多使用BLEU作为评价指标，但是此评价指标会忽略语法上的准确性。比如我们把翻译结果里的词序进行颠倒，可能BLEU评价很高，但实际却表达出截然不同的语义，这将对真实的用户体验造成极大的影响。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFqkL9rrzqnwMic3bVDu5VBPwlw1x3iax6krAg9jia00ytZQApwCe5PiarjQ/640?wx_fmt=png)

#### **5. 流程****标准化****：**

在产品开发中，流程的标准化对项目管理、开发效率、后期维护等都有着深远影响，我们将在下一部分中详细介绍。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFeDDeGhvfmh2lqd9c2kM25az5nXJfvhedP18jJhwhsX2p5CK5QnOjQA/640?wx_fmt=png)

#### **6. 总结**

总结学术研究和产品开发的区别如下：

A.从问题定义上讲：在学术研究时是明确的、没有歧义；在产品开发时是模糊的、开放的问题。

B.从数据角度上讲：学术研究时数据是干净的、规范的；在产品开发时可能会遇到脏数据。

C.从模型角度上讲：学术研究追求优雅的、创新的模型；在真实的用户场景中可能需要制定相关的人工规则。

D.从评价指标上讲：学术研究采用比较固定的评价指标；在公司场景中，则会采用一些产品导向的评价指标。

E.从工程的角度上讲：学术研究可能写一次代码，调整参数得到理想的结果就满意了；在公司，要不断进行产品迭代，观察具体数据和结果，对产品进行细致维护。

接下来，不妨从两个我最近在做的项目出发，一探在Hulu做NLP开发的真实情景：

#### **1. News****P****ersonalization：**

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFUE5mIrKZarxxwHxTcH3bNs1py0smvJ1ytCUIbfg7Co0smgPu0HOWDQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFKhE12ticsre1vWBCmWgYCFtJSDojQDEEJkPnMCPiarc2BLjSaA1k7csw/640?wx_fmt=png)

A. 问题定义：

News personalization项目的任务是给用户推荐个性化的新闻。这是一个源自产品经理的top-down的需求。它分为两个场景：一个是在用户登录时推荐，一个是用户看完新闻后推荐下一个相关的新闻。这个问题的定义比较明确，就是推荐算法。在Hulu有很多成熟的推荐算法，比如协同滤波推荐、基于DNN的推荐等。但是Hulu新闻的场景属于短视频推荐，其特点是有很多的视频数量，但是有较少的观看数量，这就决定了不太适合用基于协同滤波的推荐算法。并且新闻具有时效性，我们不能给用户推荐几年前的事情，而是需要推荐近期、甚至当天的新闻。再者，一些用户虽然在当天或者近段时间内观看比较少，但用户历史上偏好某一类新闻，这也是我们可以利用的特征。于是最后，我们将任务定义为：给新闻做分组，然后让用户去观看他喜欢的分组中最新的新闻。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFqRhPWJB2foRnOaFibIcZugOSRPbiaDUzgM2TkJan14Micor5Mib9wNjpeg/640?wx_fmt=png)

B. 数据与模型：

在此NLP任务中可用的feature包括有视频标题、关键词，简短描述、字幕（由语音转文本的模型生成）等。NLP中有很多的方法来处理这个问题，比如文本分类、聚类、主题模型等。其中Dynamic Topic Mapping就是假设我们已经有一些新闻主题，再将提取出的视频主题对应到到新闻topic上。

对于文本分类任务存在的问题是其类别是固定的，而现实中新闻的类别会随着时间的推移而变化。聚类也会存在这一问题，一些动态的聚类方法又非常复杂。于是我们设计了了Dynamic Topic Mapping方式。这主要因为我们有第三方提供的近期发生的新闻事件，一方面可以对我们对新闻提出的动态主题进行验证和监督，另一方面也可以把它们作为trending topic的信息。最后，只需要将新闻提取的新闻关键词与trending topic进行匹配即可。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFXNYxGRqoialgVvWtvDBWiaYamicchTrgAUlLslIaNzCdHW2LFfIFGsq7g/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF8qGyESbfmhzicBw6EhcTEEW3E7ntthiaMe80ey0UdYMd6vkefmbf6lHA/640?wx_fmt=png)

C. 整体架构：

上图为系统的整体架构：首先对 data去做一些数据预处理，比如：去停用词、命名实体，句法分析等。再去做词频分析，有监督分类出关键词或者无监督地提取关键词。然后将这些关键词和trending topics的关键词进行mapping，最后计算相似打分。

从目标出发，这个项目是一个PoC，我们更多的注意力是先把这个项目实现。当然之后有很多事情需要进一步迭代，比如：classification应用更复杂，更准确的模型，topic mapping里引入层次结构，优化相似性评价指标等。一旦有一定的用户实验反馈，就可以很轻松地进行下一步持续的优化。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFg8BkTIHnem9aF4RwbwL27E1dtCicVZQXwu49uQ1rYT2foyxyAHflU3Q/640?wx_fmt=png)

#### **2. Content Embedding：**

A. 问题定义：

利用每部视频的事实和描述性的标签，对视频进行embedding向量化表示。这是介于top-down和bottom-up之间的需求。从top-down角度讲：推荐系统经常会面临冷启动的问题，在用户还没有很多点击的时候，经常会推荐不出去。这时我们会将库中内容和用户看过的内容做相似度匹配，然后推荐给用户。从bottom-up角度讲：很多场景如电影、电视剧推荐，很难显式计算两个视频之间的相似度。这时丰富的标签信息可以帮助我们对show进行embedding 便于相似度计算。Content Embedding的优势有一下几个方面：1) 它是对视频标签、元数据metadata的一个高度抽象表示；2) 它适合用于DNN等各种机器学习、深度学习算法中；3)作为向量表示，它很容易集成到现有系统中；4) 可以通过直接计算两个实体在向量空间中的距离来计算它们的相似度。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFNXxlOozcpKn2379auFfC9Z1wDcib50tJ5fOOC1wxDiankYzbZqJlkuMg/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFACzjjmsaia08qs8hTWu8EnDdYibsfIXAXFBBUwWeytDvo79hz032boDQ/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFcoeHCNmGnXJ0rhORW6tZQaEDiaSRAia8OZCEPw7PptbnXy5uSVvR5Aiag/640?wx_fmt=png)

B. 数据与模型：

电影、电视剧推荐场景中可以使用的NLP特征主要：影片发布时间，评级，演员和工作人员，影片描述等；从第三方获得的外部信息，如关键字，标签，奖项，票房收入等。这些NLP特征又可以分为文本类型和标签类型。文本类型可以通过一些seq2seq模型提取高层语义特征，得到featrue representation。

对于标签类型，如果考虑实体之间的关系，可以把它看成知识图谱问题。但如果淡化实体之间关系，只考虑每个content和它共现的信息，就可以当做为network embedding的过程。在我们的场景中，要去计算两个content之间的距离，显然可以剥离掉它们之间的实体关系，于是可以采用一些网络学习的方法。最后我们选择了基于node2vec的解决方案，从理论上这是一个比较简单的模型，它的思路和Word2vec完全一致，只是需要先对图中的边进行路径采样，再将每个路径当做Word2vec中的一个句子，每个节点当做Word2vec中的一个单词，之后在这些采样路径上去学习embedding。这其中根据元数据和标签的特性又做了很多结构和优化目标上的细节调整，这里就不一一展开叙述了。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFFOOWxWWJgRnzEnGwMgERaJbrkO7kgIhOKCLiaoIlagvicPcMeP9B459A/640?wx_fmt=png)

C. 评价指标：

Content Embedding的评价有很多种方法：1) 每一部show在观看的时候有一个相关内容列表，可以用这一列表中内容的点击率作为评价标准；2) 通过人工编辑团队判断内容之间的相关性；3) 基于Content Embedding，利用用户的行为对线上的其他服务进行fine-tuning，以获得更好的线上指标；4) 用Content Embedding为特征，进行内容点击率预估等。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFgfc65GvAYgV4kxfG9rMOZtiaRxxKWs4Oib9H49OGeI8BGfL1dibFBqLog/640?wx_fmt=png)

D. 整体架构：

上图为content embedding集成到推荐系统的一个架构图。对于user，可以利用用户标签、用户上下文信息等特征得到user vector 。对于show，可以利用前文介绍的方式获得show embedding。将两者作为输入，通过一个深度神经网络来建模它们的交互信息，以此为用户进行更精准的推荐。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFwv19hkic35fHU871zaOGrfuLOGj4KwLljicTC6kO6wuWX0hQmgLvvhiag/640?wx_fmt=png)

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF1ol0bibRibhbFMk7tvau7XdoE4ibfczevPmq7GqNkPKLjOTmvP1Pv1LhA/640?wx_fmt=png)

> “你不是一个人在战斗”
>
> ### 平台、架构对于Hulu Research研发效率的长远影响

关于开发效率可以分为两类，一类是团队的效率，另一类是个人开发效率。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF1KcS6VALMyicZIQwoweibvkk0QBLcLBZOl0TAFZm3RHj1mLrQrdWB2iaw/640?wx_fmt=png)

#### **1. 团队效率：**

Hulu有五个研究团队，团队间更多时候是相对独立的，各自都在做各自的项目。但事实上，团队之间有很多数据、特征、模型其实是可以复用的。在此基础上，为了避免大家做重复性的工作，我们构建了AI Platform架构，可以为开发团队减轻重复造轮子的压力，也让研究团队能将更多精力关注于模型优化上。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFauPgdIDXAPS4oXh3GNUfGlM3kznB4l4icrnq1uJRm1WSrc2pljRN61A/640?wx_fmt=png)

AI Platform分为三层，第一层为基础架构层，第二层为机器学习数据层，第三层为AI服务层。基础架构包括对原始数据的存储、分布式的计算资源GPU的调度，分配不同节点进行机器学习、深度学习的任务等。ML数据层存放加工之后的机器学习原材料，比如Content Embedding就会存放在这里，以便日后各个team的使用和模型的迭代优化、版本控制。第三层服务层的构建是为了让模型更好地服务于线上产品，使团队能更好的管理、发布和监控模型线上的运行情况。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFF376yTDUQ1pIZpzXjNGdcQJOyiaJuV4ZEgXlkXVicfVuQunuVYmO8r7WQ/640?wx_fmt=png)

在Hulu的整个机器学习任务周期中，一般流程为：建立数据流pipeline，自动化将数据取出放入特征仓库，然后训练模型、进行评估，将稳定的模型版本存放在在模型仓库中，之后部署到线上通过AI服务层进行预测和监控等。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFjEbqDiaEalhszoVsRtoeibhOWiaRYWibS2DXeW29NFx3HSGt92WcnWpJCg/640?wx_fmt=png)

#### **2.个人开发效率：**

在公司中个人的工程实践能力也非常重要。个人工程化能力的提升是一个日积月累的过程：

A. 代码效率：在开发过程中我们需要考虑编写的代码是否高效，比如在python中选择哪个库？用哪种形式、哪种写法的函数会使程序效率更高。

B. 算法优化：从算法角度提高代码效率，类似Word2vec相对NNLM采用的Hierarchical Softmax等方式对算法进行优化，极大提高了训练效率。

C. 并行化：在公司进行项目开发，要灵活地运用大数据基础架构等底层服务对代码进行并行化，比如数据读写、训练模型时都需要考虑能否以及如何进行并行化，这样可以大幅度缩短项目的开发和迭代周期。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFOQDSic8nA4PQWSiarEUDRvSvs47RX2MTOTxtUY8UePpBag9X7AG1swwg/640?wx_fmt=png)

最后提一下《百面机器学习》，从这本书里你会看到机器学习领域有着许多值得玩味、值得思考的方面，这也是“百面”真正的寓意，供大家参考。

**作者介绍：**

**![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPguKTQViapnQl94W0z7E0tFFM55wk2jIK9Zxl2Nq4YORffcbObeBcjmN4opJf7X9vRREpAfqrYmp1w/640?wx_fmt=jpeg)**

李凡丁，毕业于北京大学信息科学技术学院。2016年6月加入Hulu内容理解团队，从事CV和NLP相关的研究和软件开发工作。

**内推职位：**

公司：Hulu

城市：北京

职位：算法工程师/高级研究员/研究员

邮箱：fanding.li@hulu.com

详细职位方向见下图：

![](https://mmbiz.qpic.cn/mmbiz_jpg/zHbzQPKIBPiaiamrhs3wTJCULnIkJrAtGHVQuPWAOmY9eb90VTFQJEYSWd2xPSP96A1kAEvjqBOL6OrxKIXgx3kw/640?wx_fmt=jpeg)

**——END——**

**文章推荐：**

[**从推荐推理奔向未来AI**](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247488030&idx=1&sn=03c7488018b9a6488d5fa01a4057cf3c&chksm=fbd4a072cca32964e7a847bca7e0aecd4bcdacfbf2a47be8f646257f4fd1808cb8472869c6d4&scene=21#wechat_redirect)

[**Sophon ：Hulu智能OLAP缓存层技术实践**](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247487934&idx=1&sn=be30bbeca1fa3311157daf08a2bd47e7&chksm=fbd4a3d2cca32ac40350c46aba98870437536e0f9acaccc5aad22ca43d708337e01540d1cb97&scene=21#wechat_redirect)

[**「回顾」Content understanding in Hulu**](http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247487021&idx=1&sn=efaff6e296d2dc1bee8624b4b2c78775&chksm=fbd4bc41cca33557ba0e01620b485bd58f86492198afd9f7dada9d54cdc2eb4d48421badb6a8&scene=21#wechat_redirect)

**本文配套PPT：**

**请关注社区公众号，后台回复【****hulu****】**

**加入DataFun社区算法群：**

**请关注社区公众号，后台回复【****DF****】**

**关于社区：**

DataFun定位于最实用的数据智能社区，主要形式为线下的深度沙龙、线上的内容整理。希望将工业界专家在各自场景下的实践经验，通过DataFun的平台传播和扩散，对即将或已经开始相关尝试的同学有启发和借鉴。

DataFun的愿景是：为大数据、人工智能从业者和爱好者打造一个分享、交流、学习、成长的平台，让数据科学领域的知识和经验更好的传播和落地产生价值。

DataFun社区成立至今，已经成功在全国范围内举办数十场线下技术沙龙，有近俩百位的业内专家参与分享，聚集了万余大数据、算法相关领域从业者。

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPhicE4hS5liayK0vWlwTanNgy003rMCMPvRlktwUjR2m8icG0MbH1ByNF7RuLdibwXKsA424lHOvaIHWw/640?wx_fmt=png)

**看官点下「好看」再走呗！****👇**