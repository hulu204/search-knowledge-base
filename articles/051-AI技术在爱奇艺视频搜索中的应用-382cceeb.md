---
title: 'AI技术在爱奇艺视频搜索中的应用'
company: 爱奇艺
tag: 搜索
date: 2024-09-26
url: https://mp.weixin.qq.com/s/K02gGawk_4Ej5rWlPxfAZQ
account: 爱奇艺技术产品团队
origin: readme
---
当前AI技术已经全面在爱奇艺搜索引擎中落地应用。与传统搜索仅能查找片名不同，爱奇艺的AI搜索功能让用户能够在搜索阶段使用更多模糊信息获得想找的影片。首次将生成式AI技术应用于角色搜索、剧情搜索、明星搜索、奖项搜索和语义搜索五大场景。通过对模糊搜索query的精准理解提供了多样化的内容推荐，使用户能够通过几个简单的关键词，快速找到与影视剧密切相关的热门角色、经典剧情场景和明星阵容等内容，标志着找片和搜片进入了AI时代,而这些相关创新实践在用户体验和内容分发效果上都获得了积极反馈。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/unymlvueOvvyd5uAJxNNBxJSzcfqEUszWN8u0YibpxnHaTrQfwcG5iclsaBIGokOxHibDVRHSibrO9rQGga4icFcejQ/640?wx_fmt=png&from=appmsg)

上述两张图展示了AI搜索在爱奇艺搜索中的产品样式。它们分为三个主要部分：顶部的“TIPS”，这部分以“为你找到以下作品”开头，通过简短精炼的一句话来介绍影片的信息。中部的影视卡片是为用户找到的影片内容，用户可以通过点击这些卡片直接观看影片。底部的“你还可以这样搜/问”是query引导词，用于引导用户进一步进行搜索和提问。接下来，我们将分别介绍这三部分的相关技术点。

***01******#***

**基于COT技术的TIPS生成**

# 

TIPS信息是用户第一眼看到的信息，TIPS的信息可以快速了解影片的信息，通过这些信息用户能迅速掌握影片详情，对于用户的观影决策起着至关重要的辅助作用。

由于影片信息繁多，包括演职员信息和剧情信息，它们合并起来可能会超过上千字。如何用简洁的语言为每部作品生成一条有吸引力的TIPS，是一项非常具有挑战性的工作。经过多次实验，我们最终确定使用COT技术生成TIPS。

Chain-of-Thought(CoT)[1]是一种改进的Prompt技术，旨在提升大规模语言模型在复杂推理任务上的表现，特别是针对复杂的数学问题，例如算术推理、常识推理和符号推理。CoT技术通过要求模型在输出最终答案之前，将一个复杂问题逐步分解为多个子问题，依次进行求解，从而提升模型的推理能力。一个简单的CoT实例如下图所示：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/unymlvueOvtgIUiaoUZYfq1p8ibThHsRwJLQTE9hPPQUtwnbUHruFCvJM0X9zl5PuoWiabyKpVVmLBeCBKRfOpC7g/640?wx_fmt=jpeg&from=appmsg)

## 图1 COT简介

类似的，我们将TIPS生成任务拆解为两个步骤。第一步，从众多信息中提取影片的亮点，从而过滤掉原内容中大量无用信息，保留核心信息。第二步，将亮点信息最终组织成一条有吸引力的TIPS内容。

以《手机》这部作品为例，第一步，从原始内容抽取出亮点信息：

著名从业者：导演冯小刚，主演张国立、葛优

改编信息：改编自刘震云同名小说《手机》

吸引点：冯式幽默, 讽刺现实, 婚姻危机, 三角恋

剧情简介：本片讲述了主持人严守一因手机导致婚姻危机的故事

然后，根据以上信息模型再进行总结，生成这部作品的推荐语：

《手机》由冯小刚执导，葛优、张国立主演，改编自刘震云同名小说，是现实题材与冯式幽默的完美结合。

具体的执行过程可参考下图：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/unymlvueOvtgIUiaoUZYfq1p8ibThHsRwJmXJjb9bWFvetsaedIriaAqEJ2p9LgK5CDbzD1aayFibzaypvUqX7AiacA/640?wx_fmt=jpeg&from=appmsg)

## 图2 影片TIPS生成流程

# 

***02******#***

**语义找片**

# 

除了根据片名进行搜索，我们的AI搜索功能还支持多种搜索方式，包括角色搜索、剧情搜索、明星搜索、奖项搜索和语义搜索等。这些功能的引入为观众提供更加全面和个性化的搜索体验。由于剧情等内容通常具有更高的复杂性，要求更强的语义理解能力，我们采用了先进的RAG（Retrieval-Augmented Generation）技术来提升搜索效果。RAG技术，是一种通过检索外部知识来增强生成模型输出的方法。它不仅依赖于模型的内在知识，还能访问实时更新的权威数据，进行提高生成内容的准确性和相关性。

如下图，展示了RAG技术和常规搜索引擎以及大模型技术的差异。第一个图是我们熟悉的常规的搜索引擎，首先输入query，然后从搜索引擎中获取数据并排序后展示搜索结果。第二个图是直接使用大模型进行回答，同样先输入query，然后由大模型直接给出答案。第三个图使用RAG技术，与前两种不同的是，首先从搜索引擎中获取相关的结果进行排序，然后将搜索结果送入大模型产出最终的答案。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/unymlvueOvvyd5uAJxNNBxJSzcfqEUszaLic5VEJyDPrHwuI2jXKibrGE4DKG42QKRs6114zAnsdRPOQh8ZwcGlg/640?wx_fmt=png&from=appmsg)

## 图3 常规搜索引擎，大模型问答和RAG技术对比

常规的RAG技术主要包括三个步骤：数据索引构建、检索和生成。下面我将以视频领域的AI搜索为例，介绍下AI搜索的实践经验。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/unymlvueOvvyd5uAJxNNBxJSzcfqEUsz2hnjgDg4v4BibbU669N0s6VPM5ialUtg2JHZINcoPt5vQ6BBw9m4K8YQ/640?wx_fmt=png&from=appmsg)

## 图4 RAG技术基本流程

## **索引构建**

数据预处理包含多个步骤，包括加载多种数据格式、获取不同数据源、进行数据过滤、压缩和格式化等。同时，还需要提取与影视相关的元信息，如影片名称和演职员信息。接下来，我们对数据进行清洗，识别并纠正原始数据中的错误，例如缺失值、重复记录和格式错误。最终，将数据转换为统一格式并进行存储。下面以向量索引为例，重点阐述索引涉及的两个关键技术：1. 选择合适的chunk块大小；2. 选择合适的Embedding模型。

### **Chunk块大小的选择**

在创建索引之前，我们需要先确定chunk块的大小。chunk大小会影响索引的精度和效率。一般来说，chunk块越小，索引的精度越高，但存储空间和计算开销也会增加。相反，chunk块越大，索引精度会降低，但存储空间和计算开销也会减少。因此，我们需要在精度和效率之间找到一个平衡点。

另一种方法是采用自适应的chunk大小，根据文本的特点动态调整chunk块的大小。例如，对于结构化的文本，如问答对或者对话轮，可以将整个语义块作为一个chunk。而对于较长的段落，可以根据标点符号或者换行符将其拆分为多个chunk。

Jina-ai提出了一种Late Chunking[2]方法，该方法先对文本进行Embedding，然后再进行分块。具体步骤是首先将Embedding模型应用于整个文本，为每个token生成一个包含丰富上下文信息的向量。接着，对这些token向量序列进行平均池化，进而得到考虑了整个文本上下文的chunk Embedding。

在视频AI搜索中，我们根据不同的数据类型采用不同的切分算法。对于较短的文本内容，由于信息较为内聚，我们采用了固定长度的chunk方法。对于大部分较长且信息量分布复杂的文本内容，我们尝试了多种基于语义的切分方法和Late Chunking方法进行实验对比。经过实验后，最终选定了自适应语义切分方法，这种方法在保障同一语义内容被切到同一块的同时，也能保证整体chunk块的大小统一。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/unymlvueOvvyd5uAJxNNBxJSzcfqEUszYVrEvVfORP8jSSQe55joliciaAXUxYpjbVac3dTZ3MlbPndlXCK2Ouxw/640?wx_fmt=png&from=appmsg)

图5 chunk切分实验

### **Embedding模型选择**

Embedding是将文本、图像、音频和视频等转换为向量矩阵的过程，也就是变成计算机可以理解的格式。Embedding模型的质量直接影响到后续检索的效果，特别是语义相关度。随着技术的发展，新的Embedding模型不断涌现，其效果也在不断提升。最近的一些研究表明，基于领域微调的模型可以显著提高Embedding的效果，从而提升后续任务的准确性。

基于此，我们对当前市面上Embedding模型进行了实验，并对主流模型使用视频领域的数据进行微调。实验结果表明，经过领域微调的Embedding效果在部分任务上明显优于通用的Embedding模型。以下是我们实验过程中效果较好的Embedding模型：

**1、OpenAI** **embedding****模型**：OpenAI提供了几种不同大小的embedding模型：text-embedding-ada-002（1536维）、text-embedding-3-small（1536维）、text-embedding-3-large（256维和3072维）。在MTEB基准测试中，text-embedding-3-large模型的3072维版本性能最好，256维版本次之。但在自定义数据集上评估时，大型、小型和Ada模型之间的性能差异没有MTEB基准测试中那么显著。

**2、Google embedding****模型**：Google提供了一些大型多语言embedding模型，如LaBSE（768维）、MURIL（512维）等。

**3、Cohere embedding****模型**：Cohere的embedding模型支持多种语言，维度为1024。在自定义数据集上的评估中，Cohere模型的性能介于OpenAI和Google之间。

**4、BGE embedding****模型**：BGE（BAAI General Embedding）模型由北京智源研究院开发，是一系列通用语义向量模型，旨在提供高效的文本嵌入功能。该模型在MTEB排行榜上表现出色，尤其是在中英文语义检索精度和整体语义表征能力上，超越了许多同类模型，如OpenAI的text-embedding-ada-002。

通过这些实验和评估，我们能够进一步优化和选择最适合具体应用场景的Embedding模型，从而提升AI搜索最终效果。

### **重排序**

Rerank模块在优化搜索结果排序方面起到了关键作用。它的主要目的是在初步检索后的候选chunk列表基础上，进一步优化排序，把对最终回答最重要和最相关的chunk排在前面。向量检索可能会召回一些相关性较低的候选项，引入Rerank模型可以在此基础上进一步优化结果，降低为生成提供的参考内容中的无效信息。同时，向量检索只考虑了query和候选在向量空间的语义距离，而Rerank可以进一步考虑上下文信息、句法结构等其他语义关系。下面介绍一些我们尝试过的Rerank方法：

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/unymlvueOvvyd5uAJxNNBxJSzcfqEUszY7k6GQShPoo0uMczJrJvtmia2iaP9gJlcrORpnTib15KgPtaX2qic6n5TA/640?wx_fmt=jpeg)

图6 cross-encoder和bi-encoder技术方案

1、交叉编码器模型(cross-encoder)[3]：将query和候选文档拼接后通过transformer编码器计算相似度分数。

2、双塔编码器模型(bi-encoder)[3]：分别编码query和候选文档为向量后计算相似度。

3、基于排序的模型：将query-doc对作为输入，预测相关性得分。

4、基于预训练语言模型的模型：在预训练模型的基础上进行fine-tune，可以利用预训练过程中积累的丰富知识。

经过实验和评测，我们发现基于预训练语言模型的方法在我们的AI搜索策略中效果最优。除此之外，为了获得更加精确的结果，我们在Rerank模块中还引入了一些视频领域特殊的打分策略。这些包括：人名（明星，角色）匹配打分策略，频道匹配打分和标签的匹配打分策略。这些策略的引入使得搜索结果更加精准。

### **生成大模型**

在RAG架构中，生成大模型（Generative Large Model）是其核心组件之一，负责基于检索到的相关文档生成最终的回答或内容。这类模型通常是经过大规模预训练的语言模型，例如GPT系列、BERT、T5等，具备强大的文本生成能力，能够在理解输入上下文的基础上生成连贯且有意义的答案。由于可选模型众多，各个生成大模型的不同版本和参数量在最终效果上常有显著差异。我们评估了市面上多款大模型和内部研发的大模型，最终选择了一个在准确率和召回率上表现最佳的模型。

在大模型prompt工程上，我们也采用了一些常见的prompt工程方法来进行实验，以下三个是我们实验比较有效的方法：

* 思维链（Chain of Thought）：通过将解题过程逐步融入Prompt，促进模型的逻辑推理能力。例如，使用“让我们一步一步思考”这样的提示，帮助模型更好地理解复杂问题。
* 自动化Prompt优化：利用机器学习算法自动调整Prompt，结合用户历史数据和当前输入，生成个性化的Prompt，以适应不同用户的需求。
* 结构化感知多任务元提示优化（SAMMO）：将Prompt建模为结构化对象，允许在优化过程中搜索更丰富的变换集，从而提升Prompt的性能和灵活性。

以自动化Prompt优化为例，由于用户输入的query类型多样，且检索目标也各不相同，有时需要检索剧情，有时需要检索演员等多种源数据。基于此，我们构建了自动化上下文组装技术，针对不同的检索需求、检索来源和检索数据进行自适应的prompt构建。通过这种方式，我们能够突出当前最匹配的检索内容，从而获得更优的生成效果。

***03******#***

**query引导**

query引导模块基于用户当前的问题进行扩展，向用户推荐一些相关的搜索词。这一模块可以帮助用户更快速找到所需信息，减少输入时间，同时引导用户发现其他新内容或兴趣点，从而提高用户粘性和使用时长。在AI搜索中，我们设计了query引导服务主要包括三部分：1. 语料库构建，2. 召回算法，3. 排序算法。

## **corpus构建**

在语料库构建过程中，为了满足用户多样化的找片荐片需求，我们主要采用了两种生产方式。第一类语料库基于基础数据，如标签、明星、角色等信息构建，这部分数据覆盖了用户大多数找片荐片的需求。第二类语料库基于影视剧情数据，利用大模型对剧情内容生成具有吸引力的query，这些query语义信息丰富且多样化，能够满足用户更深层次的找片荐片需求。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/unymlvueOvtgIUiaoUZYfq1p8ibThHsRwJVojWiaHRy3a9t1WibrsziavZE1roibY1V7aNlvCeTJpXtIibwwbmLNGn42w/640?wx_fmt=jpeg)

图7 corpus构建流程

## **召回和排序**

query引导模块中的推荐词通常是与用户当前query相关的词语或基于回答内容的扩展问题。因此，在召回阶段，我们需要覆盖这两类信息。

例如，当用户搜索“推荐一些古装剧”时，我们需要在query层面召回与“古装探案”或“古偶仙侠”等相似题材相关的影视作品。同时，在回答内容层面，用户可能会对推荐中的某些影视作品的相关信息（如主演、角色、剧情等）感兴趣，因此我们也需要召回这些扩展问题。

基于此，我们设计了基于相似度召回的query召回链路和基于KV召回的query召回链路。这两种召回链路的结合应用，不仅提升了用户找到感兴趣内容的效率，还增强了用户的粘性和探索欲望。同时在排序模块，我们结合用户的画像（用户的年龄、性别、地区等人口统计学信息），上下文特征（当前的排序列表）以及历史行为特征等，训练了一个针对query的排序模型，通过综合考虑这些特征，能够更准确地预测用户对候选内容的兴趣，并将最相关和优质的内容排在前列，不仅提升了用户体验，也增加了用户在平台上的停留时间和满意度。

![](https://mmbiz.qpic.cn/sz_mmbiz_jpg/unymlvueOvtgIUiaoUZYfq1p8ibThHsRwJtjZyFicOTY4Y8U1lKEDlW1A0FTmLeTqGIVtASAEYePqIiaBCpf6qoqFA/640?wx_fmt=jpeg)

图8 query引导召回流程

***04******#***

**总结**

AI技术的创新突破和AI应用在爱奇艺搜索场景的落地，不仅优化了用户搜索体验，提升了观看时长，也为个性化内容推荐和获取精彩片段开启了新的可能。随着更多技术的持续探索和创新应用，我们期待能持续推动以科技驱动的娱乐体验，为用户带来更为丰富和个性化的观影体验。

**参考文献：**

[1] Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

[2] Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models

[3] Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks

![](https://mmbiz.qpic.cn/sz_mmbiz_png/unymlvueOvvXwhLEYHkepiaFicVMpbsBLVD8UBl8EaQ4j9XwcUpjafibX1SuB6zZOJGy2VDN9gjgQa4xM9tnh3fHQ/640?wx_fmt=png&from=appmsg)

**也许你还想看**

[会员业务出口网关的设计与实现](http://mp.weixin.qq.com/s?__biz=MzI0MjczMjM2NA==&mid=2247498407&idx=1&sn=70feddaca7e169dc43e044479f866b21&chksm=e9756684de02ef92ff2cfaee66ebe9ea2bb2a0647debb75238171bbba296bc22b2539e595189&scene=21#wechat_redirect)

[爱奇艺广告智能算力探索与实践](http://mp.weixin.qq.com/s?__biz=MzI0MjczMjM2NA==&mid=2247498380&idx=1&sn=240bf32d603b0bd1fa4818f2b473a120&chksm=e97566afde02efb98cf98a79d8552e43093241a433c3254d298d0dd5cfb43d80600f2c934bbc&scene=21#wechat_redirect)

[奇异果TV热修复实践](http://mp.weixin.qq.com/s?__biz=MzI0MjczMjM2NA==&mid=2247498342&idx=1&sn=a979705f7c759059a0d80b6241ebd727&chksm=e9756645de02ef534ca184f2db03067f556d38c41b9275f2ca1bc29d814fadc2e6c2d55a8627&scene=21#wechat_redirect)