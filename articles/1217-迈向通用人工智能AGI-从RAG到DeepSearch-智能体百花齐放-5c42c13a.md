---
title: '迈向通用人工智能AGI：从RAG到DeepSearch，智能体百花齐放'
company: 腾讯
tag: 问答/RAG
date: 2025-08-29
url: http://mp.weixin.qq.com/s?__biz=MjM5ODYwMjI2MA==&mid=2649795559&idx=1&sn=4ffeb12b38c1ba6a102ad6bdefb80f6f&chksm=becc389c89bbb18a85393e2bdfb2559336a74c37f450830550c3098b482dcf824a96bcd6da54#rd
account: 腾讯技术工程
origin: wechat-mp
---
进入今天的文章之前，先和大家唠几句彩蛋。因为今天有点特别，是周五，周末来临的日子。也是有点特别的一天——“七夕节”。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvavdrYg6rkaZc4I19KO30zIZqxeEAUjricYJsDzGjjDs8qcofcuFkTPnwlgcKSponY0ub5p7PRU1e9Q/640?wx_fmt=png&from=appmsg)

问问各位今天想好怎么过了么？🐶  

要送什么礼物了么？🐶

什么，没买礼物？‼️

那小编今天来给大家送点礼。鲜花什么的，就算了，今天到处都是。

送什么礼呢？咱是一个知识类公众号，就抽奖送7个微信读书会员年卡吧~

点击下面卡片，关注「腾讯技术工程」，中奖概率会更高哦~

然后只要动动手指，点击上面的「参与抽奖」就行了，非常简单。

抽到的朋友，会联系你发放会员卡号。多读书，多好书，明年的七夕来告诉我，你都读了些什么有意思的书😎😎

好，彩蛋就到这里。下面进入技术干货文的学习🐶

> 为了应对LLMs内在知识的有限性，检索增强技术RAG（AI + Search）应运而生。智能体的自主性面临着知识边界问题和能力边界问题，这两个边界问题也分别对应着模型知识和能力拓展的两大利器：信息和工具。无论是边界问题还是拓展利器，对模型本身的能力（尤其是深度思考推理能力）要求都很高。相应地，模型训练范式也在逐渐从有监督微调向强化学习后训练过渡。以AI Search或者Search Agent为基础，其他各种Coding Agent、Browser Agent等智能体百花齐放，并且未来的趋势是通用型智能体。

### 需求背景：模型内在知识的有限性

模型的内在知识是经过训练从大量数据中学习得到的。但是训练数据总是有限的，它的有限性主要体现在两个方面：

1. 训练数据的收集有截止日期（cut-off）限制，无法囊括超过过截止日期的的新生数据，即模型的内在知识有严格的时效性问题，相应地，模型也就不适合回答对时效性要求很高的问题；
2. 训练数据通常是公开的，而私域数据通常无法收集到，即便训练方可以利用自己的专有数据或者购买到一些专有数据，总还“隐藏着”很多没有被挖掘或者无法挖掘的私域数据，所以如果没有见过具体垂直领域的保密数据，模型通常在某个公司内部具体业务上表现不佳。

新生数据和私域数据也可以认为是“长尾信息”，这种看法其实主要是对从这些数据有需求的人群分布来看的，毕竟相比全体人类而言，某个公司的某个业务的专有数据的需求方和使用方总是极少数的。

训练数据的这两个局限性，可以统一落脚到数据分布的有限性，进而延伸至模型的泛化性问题，也是机器学习领域一直待解决的 **超出分布（OOD out-of-distribution）** 问题，尤其是遇到长尾信息时。我认为OOD问题和泛化性本质上是一个概念，可以看作是“一体两面”，OOD 说明的是一种现象，即测试数据分布与训练数据的分布不同，也称为超出了训练数据的分布；而泛化性是说在这一现象下的表现，模型在未见过的数据分布上的性能出现了下降，也即是模型的性能存在泛化性问题。

### 解决方法：通过知识检索来增强

相应地，模型内在知识也是有限的，通常有2种解决方法：一种是需要训练，也即发生在训练阶段，另一种不需要训练，通常发生在推理阶段。

前者很好理解，我们可以将新生数据或者私域知识作为新的数据集去继续预训练或者后训练微调模型，从而将新的知识注入到模型中。

而后者是在推理阶段直接将新的知识输入到模型的上下文中，然后模型通过充分利用其本身的上下文学习（in-context learning）能力，根据给定上下文信息去更好地回答用户问题。这里所讲的上下文学习能力不仅仅局限于无训练（training-free）的多样本学习（few-shot learning）能力，还包括更广泛的指令遵循（instruction following）能力。而且输入的新知识与当前任务和用户当前具体输入的问题是密切相关的。

具体的新知识又可以分为2种：

1. 通用的知识，即适用于当前任务和用户所有问题，这种知识可以直接一次性固定放在模型的系统提示词中；
2. 特定问题的知识，即直接与每个具体问题相关联，这种知识通常需要使用用户当前问题通过信息检索技术从相应知识库中召回相关知识，然后再与当前问题一块放在用户提示词中——这种方式也即是如今常见且通用的**检索增强生成（RAG Retrieval-Augmented Generation）**技术。

#### RAG演化的3个阶段

RAG演化总览图如下所示：

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvasFbqEoRGNAzs2xJLzaM5DGI8LibQedo1nzkVF1icvNswUibkJOUHktffOt2DwDRBvDwcNWdUpHpRLHw/640?wx_fmt=png&from=appmsg)

##### 简单的固定2步骤

RAG最开始采取的是一个简单明了的固定流程，即先检索再生成。而且每次固定先检索一次，通常整体执行一轮。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvasFbqEoRGNAzs2xJLzaM5DG92QhortwlzpUct6EEW03hPrzZYOaARVorMCOyiaGVDmlKcYrOxfDWIQ/640?wx_fmt=png&from=appmsg)

##### 优化用户问题和检索技术

然后为了提升检索效果，也即是为了最终的生成效果，开始从2个方向进行优化，分别是用户问题和检索技术。

前者是通过一些传统NLP或者直接使用LLMs对用户的原始问题进行优化，优化的直接目的是提升召回率，具体的方法有很多种，初级的方法有规范化、改写、扩展等，需要用于文本检索，高级的方法有假设文档（Hypothetical Document ）、上下文适应（Context Adaptation）等，主要用于语义检索。

* 假设文档是使用LLMs生成的假设可以回答用户问题的文档，其核心理念是拉近查询问题与索引文档之间的距离，也可以认为是将查询与文档（query vs document）的不对称检索（retrieval）转换成假设文档与目标文档之间的对称文本相似匹配（text similarity matching TSM 或者 semantic textual similarity STS）。
* 上下文适应的目的是使用户问题适应当前上下文（包括任务、提示、补充知识等），使其自身更加具有完整性（包含相关上下文）和独立性（自洽，不需要其他说明），整体也可以称之为“上下文落地”（context grounding）。如此优化后的查询问题可以更好地定位到符合上下文并且与当前用户问题相关的知识。其中有一种与这一理念相通的具体方法——退一步提示（[Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models](https://arxiv.org/abs/2310.06117)）。 退一步的核心思想是从具体问题和具体细节出发，通过抽象化处理得到高层次的概念或者第一性原理，即从更高层更抽象的角度来看问题。其实它就是引导LLMs先思考相关背景基础知识（先做背景调查，显式地将前置依赖提供出来），再回答当前的具体问题。虽然退一步提示是作为一种提示工程方法被提出来的，但是其理念和特性可以很好地应用于上下文适应任务上来优化用户问题。

后者优化检索技术，从基础的文本检索、向量检索、混合检索乃至知识图谱检索，到使用交叉编码器（cross-encoder）进行重排，再到使用LLMs甚至推理模型进行重排。

这两者是相辅相成的，通常需要前后搭配使用，以达到最好的效果。

##### 从固定工作流到自主智能体

但是这两个阶段都还是人工设计为主，整体流程虽然更复杂了但基本也还是固定的。最后随着推理模型的出现和发展壮大，RAG从逐渐升级到Agentic RAG，即从之前的人为设计好的固定工作流程慢慢进化到更加自主的智能体系统。智能体自主性的第一个层面是直接根据当前的上下文信息经过推理（深度思考）然后直接决定下一步执行检索的问题和检索策略。其中可用或者建议的用户问题优化策略和可用的检索配置都直接通过上下文信息暴露给模型，模型在深度思考阶段推理和决定合适或者最佳的优化策略，即利用模型强大的推理能力（深度思考能力）自主地完成优化。第二个层面是模型可以根据之前的执行结果自主地判断是否还需要继续搜索以及还有哪些需要进一步探索的缺失之处，这样整个智能体系统可以循环多次搜索步骤直到收集到足够的上下文信息来回答用户最初的问题。

Agentic RAG的整体框架本质上其实是推理模型兴起之前的ReAct框架（[ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)），而现如今有了推理模型的加持。不仅如此，最近非常流行的DeepSearch和DeeppResearch也主要基于ReAct框架。其实无论是最开始的朴实RAG，还是如今的Agentic RAG抑或DeepSearch和DeepResearch，都可以统称为AI Search，即通过AI技术来搜索外部知识来为LLM（更好地）回答用户问题补充上下文信息。Jina AI也在博客《[A Practical Guide to Implementing DeepSearch/DeepResearch](https://jina.ai/news/a-practical-guide-to-implementing-deepsearch-deepresearch)》中指出：其实DeepSearch和DeepResearch都算是对RAG的“品牌再造”（rebranding），即一种商业手段。

当然，现在的Agentic RAG或者AI Search已经不仅仅借助于检索来增强回答，LLMs 的工具调用（Tool / Function Calling）能力更能够拓展模型的能力边界。所以可以将如今的Agentic RAG中的“R”（Retrieval）统一替换成“T”（Tool），即TAG（Tool-Augmented Generation）。同时我又发现一个新的说法“集成工具的推理”TIR（Tool-Integrated Reasoning），比如[ToRA: A Tool-Integrated Reasoning Agent for Mathematical Problem Solving](https://arxiv.org/abs/2309.17452)。这个说法将之前的生成Generation升级为了推理Reasoning，以突出推理模型（reasoning models），同时使用集成Integreated替换了之前的增强Augmented，突出模型的推理能力与工具调用能力之间的有机融合（integration）和协同作用（synergy），即推理能力思考调用哪个工具以及如何调用所选工具，工具调用的结果返回到模型的上下文中指导下一步更好的推理，并且循环往复。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvasFbqEoRGNAzs2xJLzaM5DGhy5niacwQe9QjoC5USTEQwBicXbRInnPa9ymThQT5j2sdFasibRSdYlibw/640?wx_fmt=png&from=appmsg)

模型的推理能力和工具调用能力极大地升级强化了ReAct框架的自主性，之前的工作流Workflow也就进化到了智能体Agent。而引入了智能体的概念后，我们就可以从强化学习（Reinforcement Learning）的角度来理解和分析如今围绕LLMs构建的智能体系统。而且，众所周知，推理模型本身就是通过强化学习算法后训练得到的。

#### Agentic RAG 所面临的边界条件

智能体的自主性（autonomy）固然好，但是面临着2个边界条件：**知识边界和能力边界**，并且二者息息相关。

知识边界很好理解，正如我们开头讲到的模型的内在知识是有限的，也即是有边界的，但是在面对具体的用户任务和问题时，这个边界具体在什么位置呢？这是一个非常具有挑战性的问题。如果人工可以精准定位模型知识边界的话，则我们通常不会去让模型来推理判断。因为后者本身具有随机性，而且还有尚待缓解乃至解决的幻觉问题。举个通俗的例子，如果我们可以使用计算器完成计算的话，则不会也不建议去使用大模型。

而我们现在转向大模型来判断知识边界就是因为人造的规则有局限性，比较死板而且不灵活，需要持续不断地人工投入。而大模型（尤其推理模型）本身能力很强，而且也在不断地得到增强。总的来说，大模型的上限很高拓展性很强，又非常灵活，可以适应不同的任务场景和输入输出。所以使用大模型来推理（深度思考）其自身内在知识是否足以回答当前问题以及内在知识与当前问题之间还有哪些差距需要弥补，然后去针对性地获取外部知识。整个过程很像是一个人在被人提问时回想和思考脑海里已有的知识，如果没有相关知识储备和治理，则需要请求外援，比如上网搜索或者咨询内行专家。

能力边界是指大模型的能力是有限的，类似大模型主动获取外部知识来弥补其内在知识与当前问题之间的差距，我们也希望大模型能够判断其自身能力与当前任务需求之间的差距然后主动请求外部工具来弥补能力缺陷。比如大模型的计算能力有限，当遇到数值计算乃至通用的程序执行任务时，最好的解决方式是调用相应的工具（计算器或者代码解释器）。而人类就是这么做的，典型地，计算器或者更通用且强大的计算机可以弥补人类在计算方面的不足或者拓展人类的计算能力。

其实从某种程度上来说，知识边界也是能力边界的一种，毕竟人类通常也将“好记性”作为一种个人能力。知识边界主要关注理论知识层面的不足，能力边界主要关注实践能力层面的短板。事实上，获取外部知识是需要使用外部工具的，具体使用哪些工具以及如何使用工具属于能力边界的范畴。然后获取的知识再输入到模型中，用来反哺知识边界，而有了更多知识（更多上下文信息）也有益于工具的选择。单独将知识边界独立出来是因为知识是理论基础，其他实践工具是能力拓展。正所谓“巧妇难为无米之炊”，一个厨师再精通各种厨具和熟悉各种烹饪技巧，但是没有米也就“英雄无用武之地”。相应地，好的食材更能展现厨艺，二者是相辅相成相得益彰的。

从强化学习的角度来看，一个智能体与外界环境交互的通用范式是先进行广度探索再进行深度挖掘（exploration before exploitation）。其实这种范式也就先后分别对应知识边界和能力边界。

与计算机做一个类比，中央处理器（CPU）负责计算，具体数据保存在内存里，如果内存放不下则还有外存，CPU从内存读取数据，如果内存没有则需要从外存读取，然后启动处理流程，其自身可以执行一些计算，如果处理不了则需要调用其他工具，最后再将处理后的数据写回内存，如果内存放不下则还需要写到外存中，循环往复直到任务完成。

智能体的内存就是其内在知识，外存是互联网、教科书或者内行专家。如果内存中的内在知识不够，则需要从外存中获取外部知识，即知识边界。大模型LLMs非常善于文本处理（自身的看家本领），但是对于数值计算和代码执行（可以统称为计算能力）并不擅长，即能力边界。这个时候，就需要请求外部工具的帮助。经过内外部工具处理后的信息如果比较多或者没有长度没有超出LLMs的上下文窗口大小，则可以直接放在模型的上下文中（即内存中）；相反如果太长或者超出了LLMs的上下文窗口大小，则需要保存在外部知识库中（即外存中）。

#### DeepSearch

有了信息和工具之后，再加上一个智慧大脑（推理模型），我们就很自然地得到了深度搜索（DeepSearch）。目前DeepSearch或者DeepResearch的论文和应用有很多([OpenAI Deep Research](https://openai.com/index/introducing-deep-research/)、[Anthropic Multi-Agent Research System](https://www.anthropic.com/engineering/built-multi-agent-research-system)、[JinaAI Deep(Re)Search Guide](https://jina.ai/news/a-practical-guide-to-implementing-deepsearch-deepresearch)、[Kimi-Researcher](https://moonshotai.github.io/Kimi-Researcher/)、[ByteDance DeerFlow](https://deerflow.tech/)、[Google Gemini Search Agent](https://github.com/google-gemini/gemini-fullstack-langgraph-quickstart)等），总体的技术范式和实现大同小异，与前文所讲的Agentic RAG基本一致，这里不再一一赘述。

下面我们可以看一下Jina AI和Google Gemini的方案，二者整体都很简洁，主要面向AI Search垂直领域。整个智能体系统的核心仍然是推理模型及其深度思考能力，具体在AI Search领域，该深度思考能力用来思考判断当前上下文是否足够回答用户问题以及如果不够的话生成后续的检索问题（即gap问题）。除此之外，AI Search通常只有一个检索工具，用来获取外部知识。

|  |  |
| --- | --- |
| Jina AI深度搜索的实现 | Google Gemini Search Agent框架示意图 |
| Jina AI深度搜索的实现 |  |

如果再加入和拓展一些信息检索之外的工具，比如代码解释器、计算机系统或软件控制等工具，那么就可以得到Coding Agent（比如[Cursor](https://cursor.com/)、[Trae](https://www.trae.ai/)、[Cline](https://cline.bot/)、[Github Copilot](https://github.com/features/copilot)等）、Browser Agent（比如[Fireworks Broswer Agent](https://fireworks.ai/blog/opensource-browser-agent)）、Computer Agent（比如[OpenAI Computer Use](https://platform.openai.com/docs/guides/tools-computer-use)和[Anthropic Computer Use](https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/computer-use-tool)）等垂直应用Agent。

总的来说，AI Search是其他垂直AI应用Agent的前置依赖和基础。同理，以人类为例，阅读是创作的基础和前提。具体地说，AI Search主要用来阅读（read），而其他智能体（比如Coding Agent）的主要目的是创作（write）。LangChain 的博客《[How and when to build multi-agent systems](https://blog.langchain.com/how-and-when-to-build-multi-agent-systems/)》中提到以阅读为主的多智能系统通常比以创作为主的多智能体系统更加容易些。

这个很好理解，普通人通常可以阅读四大名著，钻研深入的读者也理解更深度些，但是现实是绝大多数人是写不出来类似四大名这种经典作品的。原创或者自研比阅读和使用要高几个维度。类似地，生成对抗网络（GAN）中生成器（generator）通常比判别器（discriminator）的参数量更大，一个小的LLM可以用来评估另外一个参数量更大的LLM的生成内容。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvasFbqEoRGNAzs2xJLzaM5DGZqUooz7hc2CFu8chKyZntl7c17p1zwOXpQwPHcdfxEBSFogDSibKnQw/640?wx_fmt=png&from=appmsg)

从工作的角度来看，阅读（学习）不是目的，创作（干活）才是。创业公司[Cognition AI](https://cognition.ai/)发布的[DeepWiki](https://deepwiki.com/)产品支持对一整个代码仓库进行问答甚至DeepResearch，即让AI来帮助我们进行代码阅读和理解，即AI Search。同时这个创业公司发布的Coding Agent产品[Devin](https://devin.ai/)号称为全球首个AI软件工程师，即让AI充当或者替代人类去编写软件，即AI Coding。

#### 总结与展望

从长期来看，LLMs 内在知识的有限性会一直存在，相应地，检索增强的需求也一直都会存在。从最初朴素的RAG方案，到加入了很多人工设计（各种查询检索优化和工具调用）的精密复杂的RAG工作流，再到围绕推理能力（推理模型）构建的具有自主性的Agentic RAG（比如DeepSearch），AI Search的目的没有改变，变化的是模型能力（推理能力和工具调用能力）和设计范式（从死板的人类工程到灵活的模型自主性）。

当然，也是得益于模型能力的提升才更好地驱动了设计范式的升级。而且这种范式升级非常契合Rich Sutton的《[苦涩的教训](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)》，即从长期来看通过搜索和学习来扩展计算量的通用型方法胜过以人为中心的方法，其中学习就是训练（大模型的[scaling law](http://arxiv.org/abs/2001.08361)）。

智能体系统自主性面临着2个边界问题，即知识边界和能力边界，也分别对应LLMs应用的2大抓手：信息和工具。从目前来看，大（语言）模型仍然是数据驱动的，所以要想解决这2个边界问题，仍然需要从训练数据着手，进行针对性的模型训练。

同时考虑到信息空间和工具库都是不断扩展的，环境是动态的（dynamic），并且与环境交互是多轮或多步的（long horizon），目前的训练方式也从有监督微调（SFT）逐步升级进化到强化学习（RL）后训练，以获得更好的自主性、泛化性、灵活性，比如[Search-R1](http://arxiv.org/abs/2503.09516)、[ReSearch](http://arxiv.org/abs/2503.19470)、[Kimi-Researcher](https://moonshotai.github.io/Kimi-Researcher/)、[SimpleTIR](https://simpletir.notion.site/report)、[Alibaba Web Agent系列](https://github.com/Alibaba-NLP/WebAgent)等。正所谓授人以鱼不如授人以渔，SFT 更像是前者的授人以鱼，而RL更像是后者的授人以渔。

诚如月之暗面在技术博客《[Kimi-Researcher: End-to-End RL Training for Emerging Agentic Capabilities](https://moonshotai.github.io/Kimi-Researcher/)》中提到的未来愿景：从一个专注于搜索与推理的智能体，逐步演化为能够运用不断扩展的工具集解决各类复杂任务的通用型智能体，这和迈向通用人工智能（AGI）的愿景也是一致的。

![](https://mmbiz.qpic.cn/sz_mmbiz_gif/j3gficicyOvasVeMDmWoZ2zyN8iaSc6XWYjZ7Hx6Udjjk2BGLzC9ahJq7ibxDd1RGA0c9NYZc1husEsvb3tY4FcWPQ/640?wx_fmt=gif&from=appmsg)

![](https://mmbiz.qpic.cn/sz_mmbiz_png/j3gficicyOvasVeMDmWoZ2zyN8iaSc6XWYj5q5PQEOc5ibURPb03vnRibrxC3UR8xzdyATfiawTYRV2vJvBnAIcE1FeQ/640?wx_fmt=png&from=appmsg)