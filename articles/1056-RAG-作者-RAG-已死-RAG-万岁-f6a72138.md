---
title: 'RAG 作者：RAG 已死，RAG 万岁！'
company: DataFun
tag: 问答/RAG
date: 2025-04-24
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764763&idx=1&sn=1b5100bb5e145b8bd789b00c2a531d0f&chksm=fbdb7977ccacf0614649a61cd999f7f08730167fb3c73d3ac7012c6af781c441f396fb59ff23#rd
account: DataFunTalk
origin: wechat-mp
---
![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPiafSvZlXNBAb9YpHibXF3jibHicibh9L4fBeAM4IAfibQSibCBG8tIWKkjmCmAKv3Wic5DkibVPDL79YQnLwA/640?wx_fmt=png&from=appmsg)

转自 | Datawhale

本文作者 Douwe Kiela，RAG 论文（Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks）作者之一。

以下为全文：

每隔几个月，人工智能领域就会经历类似的模式。一个具有更大上下文窗口的新模型问世，社交媒体上便会充斥着“RAG 已死”的宣言。Meta 最近的突破再次引发了这场讨论——Llama 4 Scout 惊人的 1000 万（理论上）token 上下文窗口代表着一次真正的飞跃。

但这些论断——无论是针对上下文窗口的突破、微调技术的进步，还是模型上下文协议（MCP）的出现——都误解了 RAG 的目的，以及为何它在人工智能领域将永远占有一席之地。

**01**

**RAG 的初衷**

五年前，我在 Meta 基础人工智能研究中心（FAIR，前身为 Facebook 人工智能研究中心）的团队提出了 RAG（Retrieval-Augmented Generation，检索增强生成）的概念。RAG 的目标是利用外部知识来增强模型，创造一种结合了参数化记忆和非参数化记忆的两全其美的解决方案。

简单来说，RAG 通过检索语言模型未经训练的数据源中的相关信息，并将其注入模型的上下文中，从而扩展了语言模型的知识库。

这种方法旨在解决生成式语言模型的许多固有缺陷：

* **无法访问私有（企业内部）数据：** 模型通常基于公共数据进行训练，但往往需要那些不断变化和扩展的专有信息。
* **过时的参数知识：** 即使模型频繁更新，其训练数据截止日期与当前时间之间总会存在差距。
* **幻觉和归因问题：** 模型经常编造听起来合理但错误的信息。RAG 通过将回答基于真实来源，并提供引文让用户核实信息，解决了这个问题。

听起来耳熟吗？现在已经不是 2020 年了，但这些同样的问题至今依然存在。甚至可以说，随着组织推动 AI 系统处理日益复杂和关键的任务，这些问题变得更加突出了。核心挑战依然是：我们如何将强大的生成式模型与公司所依赖的海量知识库连接起来？

**02**

**为什么我们仍然需要 RAG（并且永远需要）**

高效而精确的检索在人工智能中将始终扮演重要角色。这一点在一个广为流传的 LinkedIn 帖子中得到了很好的阐述，但我将重申为什么我们不能仅仅将所有数据加载到模型的上下文中：自首个具备大上下文窗口的 LLM 问世以来，RAG 就一直面临“消亡”的论调。

---

该 LinkedIn 帖子：  
  

一些值得注意的 RAG“死亡宣告”包括：

* 2023 年 5 月：Anthropic 的 Claude，上下文窗口达 10 万 token
* 2024 年 2 月：Google 的 Gemini 1.5，上下文窗口达 100 万 token
* 2025 年 3 月：模型上下文协议（Model Context Protocol）让你能直接与你的数据对话 (注：原文日期可能是笔误)

但现实情况是：

即使拥有高达 200 万 token 这样惊人的上下文窗口，当前的长上下文 LLM 也只能处理演示性质的数据集（toy datasets）。  
例如，100 万 token 的上下文窗口（大致）相当于约 1500 页文档。  
这对于演示来说很亮眼，但对于生产级别的应用而言是不足够的。

不过，让我们假设我们拥有一个无限 token 的上下文窗口：

* **可扩展性与成本**：处理数百万 token 速度缓慢，且在计算和财务上都代价高昂。即使计算成本在下降，延迟对于应用程序来说也可能是一个大问题。
* **性能下降**：LLM 仍然受困于“中间丢失”（lost in the middle）的问题。这意味着它们无法有效利用长文本中间部分的信息。通过剔除不相关文档并避免“大海捞针”的情况，您将获得更好的结果。
* **数据隐私**：将 所有 数据提供给基础模型可能引发严重的数据隐私问题。尤其是在医疗保健或金融服务等受到严格监管的行业，您需要对数据强制执行基于角色的访问控制。

**底线是：您同时需要长上下文 LLM 和 RAG。**

但既然“RAG”这个术语似乎如此具有争议性，那我们不妨这样说：  
我们不必非得称之为 RAG。  
我们可以就叫它 **检索 (retrieval)**。  
或者叫 **上下文筛选 (context curation)**。

无论您决定怎么称呼它，能够控制进入上下文窗口的数据质量，将决定最终生成输出的质量。

毕竟，垃圾进，垃圾出。

---

* **可扩展性** – 您的企业知识库是以 TB 或 PB 来衡量的，而不是 token。即使有 1000 万 token 的上下文窗口，您仍然只能看到可用信息的极小一部分。这就是为什么检索技术的创新一直快速发展，混合搜索、查询转换、自我反思、主动检索以及对结构化数据的支持等方面的进步，都在帮助您在知识库中找到正确的信息。
* **准确性** – 有效的上下文窗口与产品发布时宣传的大相径庭。研究一致表明，模型在远未达到其官方极限时性能就会下降。在实际测试中，同样的模式也会出现，模型难以准确引用深埋在其上下文中的信息。这种“上下文悬崖”意味着仅仅将更多内容塞入窗口并不会带来更好的结果。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vI9nYe94fsFeQHAfXvgnjavn7RFpoYyX05EPOgyicicGEb3VZfKqFm0RQoVudQREvQcdXGFkL5aic5a0crbYEY2Sw/640?wx_fmt=png)

* **延迟** – 将所有内容加载到模型上下文中会导致响应时间显著变慢。对于面向用户的应用程序，这会造成糟糕的用户体验，人们会在得到答案前就放弃交互。基于检索的方法可以通过仅添加最相关的信息来提供更快的响应。
* **效率** – 你会在需要回答一个简单问题时去读完整本教科书吗？当然不会！RAG 提供了相当于直接翻到相关页面的能力。处理更多 token 不仅更慢，而且极其低效，并且比使用 RAG 精准定位所需信息要昂贵得多。

  **03**

  **警惕错误的二分法**

在谷歌搜索“RAG vs”，你会看到一长串建议的查询补全——“长上下文”、“微调”、“MCP”。这种框架设定制造了一种人为的选择，并没有反映这些技术实际上如何协同工作的最佳方式。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vI9nYe94fsFeQHAfXvgnjavn7RFpoYyX5gSRKGzCcvbEaxXSl7FkYf76hAZM3By8LXBufohD7EJcqzUDF3GyeA/640?wx_fmt=png)

实际上，这些概念没有一个是相互排斥的，甚至不是相互冲突的——它们都以互补的方式帮助解决前沿模型的局限性：

* **RAG** 提供了访问模型知识库之外信息的途径
* **微调** 改善了信息处理和应用的方式
* **更长的上下文** 允许检索更多信息供模型推理
* **MCP** 简化了 Agent 与 RAG 系统（及其他工具）的集成

我们在生产环境中看到的最复杂的 AI 系统结合了这些方法，根据各自的优势来使用每种工具，而不是宣布某一个获胜并将其他工具抛弃。

正如一位 Twitter 用户最近所说：“声称大型 LLM 上下文窗口取代了 RAG，就像说因为有足够的内存（RAM）就不需要硬盘一样。”正是如此！你的电脑有磁盘、内存和网卡是有原因的。它们服务于不同的目的，并作为一个系统协同工作。RAG、微调和大型上下文窗口在 AI 中也是如此。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/vI9nYe94fsFeQHAfXvgnjavn7RFpoYyXicMv14y5cnzcFXLKyz1JCQ4PiaqtxvyIlScDUtaicSIJEHDXiafaXIy0ag/640?wx_fmt=png)

**04**

**结论**

我们不需要在 RAG 与长上下文窗口、微调或 MCP 之间做出选择。真正能创造价值的 AI 解决方案不会固守单一方法；它们会根据要解决的具体问题混合搭配使用工具。

但下一次宣称“RAG 已死”的论调出现只是时间问题，所以，如果你将来想引用这篇文章，可以在 isragdeadyet.com 找到它。这个网站将作为一个活生生的证明，展现检索在 AI 系统中持久的重要性，并且每当下一波“RAG 已死”的帖子不可避免地出现时，它都会更新。

## 如果你的系统无法利用你的专有数据，持续提供过时信息，或者缺乏你所需的专业知识，那么让我们谈谈。我们构建了一个将智能检索与前沿 LLM 相结合的系统，来解决这些长期存在的难题。因为重要的不是哪种技术在某场人为的竞赛中获胜，而是构建能够真正解决实际问题的方案。”

原文链接：https://contextual.ai/blog/is-rag-dead-yet/

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPga2sQTDda6S6r3BEST5iaj8pGy6eaZPwc4AsiciaVnk4c0tkbicaJa180wnIqTYEPp8an61ugBKHO2jw/640?wx_fmt=png&from=appmsg)

往期推荐

[小红书多云统一数据加速层解决方案](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764726&idx=1&sn=b44fbc0c0d0e72ba462a35f79bb74778&scene=21#wechat_redirect)

[重塑全球数据库格局：TiDB 在 DB-Engine 的排名跃迁方法论！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764712&idx=1&sn=7a689adbb862062de20177d4b48e634b&scene=21#wechat_redirect)

[关于MCP最值得看的一篇：MCP创造者聊MCP的起源、架构优势和未来](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764712&idx=2&sn=60d9e6f26f4fd85e92b7f5d65566de66&scene=21#wechat_redirect)

[基于DeepSeek数据爬取新范式](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764686&idx=1&sn=2f3571f51d06fee33492079ada3295b3&scene=21#wechat_redirect)

[Cursor AI客服戏精上身编造"单机政策"，程序员集体炸锅：这届GPT学会PUA用户了！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764692&idx=1&sn=76111663e132d1d218c0dc7037b903d1&scene=21#wechat_redirect)

[未来已来：一场大会揭秘AI如何改写人机协作规则](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764674&idx=2&sn=087d7ef5ada48e50988bbe04836182b1&scene=21#wechat_redirect)

[人形机器人半马冠军，为什么会选择全尺寸？](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764672&idx=1&sn=cc8bc52c2c2bb51d44083cd1600cc698&scene=21#wechat_redirect)

[硅谷AI初创要让60亿人失业，网友痛批人类叛徒！Jeff Dean已投](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764566&idx=1&sn=358852f5991598153683e65a088ba5c8&scene=21#wechat_redirect)

[基于DeepSeek的舆情分析落地实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764502&idx=1&sn=c4b152b72f117b341cfff045534ffcf4&scene=21#wechat_redirect)

[Chat2DB创始人姬朋飞：AI在 text2sql应用领域的实践](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764523&idx=2&sn=41e4af204045e06cee33a2cd9753cb2f&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640)