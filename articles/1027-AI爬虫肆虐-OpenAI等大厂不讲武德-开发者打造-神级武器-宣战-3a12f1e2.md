---
title: 'AI爬虫肆虐，OpenAI等大厂不讲武德！开发者打造「神级武器」宣战'
company: DataFun
tag: 爬虫抓取
date: 2025-04-07
url: http://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764043&idx=1&sn=4d817f9b40ab92398800cb53b7df595d&chksm=fbdb7a27ccacf33175b9cec91178294c7a55ca1fda5619bfb552c2b88e76185eb832fd23a04d#rd
account: DataFunTalk
origin: wechat-mp
---
### 转自 | 新智元   编辑 | 定慧 **导读**AI爬虫是互联网最顽固的「蟑螂」，不讲规则、压垮网站，令开发者深恶痛绝。面对这种AI时代的「DDoS攻击」，极客们用智慧反击：或设「神之审判」Anubis，或制造数据陷阱，以幽默和代码让机器人自食其果。这场攻防战，正演变成一场精彩绝伦的网络博弈。

AI网络爬虫是互联网上的「蟑螂」，几乎所有软件开发者都会这样认为的。

「爬虫」是一种网络自动程序，用来浏览互联网、获取网页内容。

而在AI时代，爬虫的威胁到了让开发者不得不封锁掉某个地区所有人的访问。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bnHvXfgMjXzskickUZSaKaTj0HUs9FG00v5SPich0xVdv5neN3Zm91FWg/640?wx_fmt=png&from=appmsg)

Triplegangers是一家仅仅由七名员工运营的公司，他们花费十多年时间建立了自称是网络上最大的「人类数字替身」的数据库，即从实际人体扫描得到的3D图像文件。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bhIkjUGYPOX7GxMsXrdsfpjialZNyia093faXWFHIPaXRXMLblS9YScSQ/640?wx_fmt=png&from=appmsg)

2025年2月10日，公司CEO Oleksandr Tomchuk突然发现他们公司的电商网站「崩了」。

「OpenAI使用了600个IP来抓取数据，日志还在分析中，可能远不止这些」，Tomchuk最终发现，导致他们网站崩溃的元凶竟然是OpenAI的爬虫机器人。

「他们的爬虫正在压垮我们的网站，这就是一次DDoS攻击！」

OpenAI没有回应此次事件，该事件过去仅仅不到两个月，但AI爬虫机器人仍然活跃在网络上。

**01**

**AI爬虫不遵循「古老传统」，阻止他们是徒劳的**

其实爬虫最早并不是AI时代为了获取训练语料而诞生的。

早在搜索引擎时代，就已经有「搜索引擎机器人」，那个「古老年代」的机器人还约定俗成的遵循各个网站上会存在的一份文件——robots.txt。

这个文件告诉了机器人不要爬取哪些内容，哪些内容可以爬取。

但这份传统随着互联网的发展似乎已经被遗忘，爬虫和发爬虫也演变为一场攻防战役。

而到了如今的「大模型时代」，互联网的信息已经被LLMs吞噬一空。

阻止AI爬虫机器人是徒劳的，因为它们会撒谎、更改用户代理、使用住宅IP地址作为代理来骗过网络「防守」。

「他们会不断地抓取你的网站，直到它崩溃，然后还会继续抓取。他们会点击每一个页面上的每一个链接上，一遍又一遍地查看相同的页面」，开发者在帖子中写道。

AI机器人除了「免费」爬取信息外，还会额外增加所爬网站企业的运营费用——在这个云服务的时代，几乎所有被爬取的企业都在云上，大量的爬虫流量不仅无法带来收益，还会增加他们的云服务器账单。

更加无法预料的一点是，对于那些被「白嫖」的网站来说，甚至确切的知道被白嫖了哪些信息。

一些开发者决定开始以巧妙且幽默的方式进行反击。

**02**

**程序员打造爬虫的「神之墓地」**

FOSS开发者Xe Iaso在博客中描述了AmazonBot如何不断攻击一个Git服务器网站，导致DDoS停机。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bNlfAdLfZwx7kTXMRNhwKpuiaBMib5GxZznCqu6VUdoibPzKYexAfoqWuA/640?wx_fmt=png&from=appmsg)

所以Iaso决定用智慧反击，他构建了一个名为Anubis的工具。

Anubis是一个工作量证明检查的反向代理，请求必须通过该检查才能访问Git服务器。

它阻止机器人，但允许人类操作的浏览器通过。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7beMVWN9NMLJ4lgzM7MDb4gbGGWQLZic1HoLrnXluLibyYjVfdeHqOjqIA/640?wx_fmt=png&from=appmsg)

Iaso关于Anubis工作原理的简单介绍。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bT0Ru9m2Z5jJuQUeRaAArInt0e7n2kiaslReD1Rpj4tHLR9zUAm8wpMQ/640?wx_fmt=png&from=appmsg)

本质上，Anubis确保的是「真实人类使用的浏览器」在访问目标网站，而不是AI爬虫——除非这个爬虫伪装的足够「先进」，就像通过图灵测试一样。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bL3SSQmNBCN9syPwkztj7BVUd5ric1Wjksmq4jJGBm9rM46kHE8ulujQ/640?wx_fmt=png&from=appmsg)

有趣的部分是：Anubis是埃及神话中引导死者接受审判的神的名字。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bE0IqHIMibxlx9Esibf1GoBlUMTjib1PW2ffOuJyal1L6vm6kIw8PEVHhg/640?wx_fmt=png&from=appmsg)

「Anubis称量了你的灵魂（心脏），如果它比一根羽毛重，你的心脏就会被吃掉，然后你就彻底死了」。

这个项目的名字带有讽刺意味，在自由开源软件社区中像风一样传播开来。

Iaso在3月19日将其分享到GitHub上，仅几天时间就获得了2000个星标、20位贡献者和39个分支。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7bjRhcExqwxQL4ocEc2KOHmoMFl0gxRcqia8thnTtJfaYPZ4qOc8LXeJQ/640?wx_fmt=png&from=appmsg)

**03**

**用「复仇」的方式防御AI爬虫**

## Anubis的迅速流行表明Iaso的痛苦并非个例。

## 事实上，还有很多故事：

* SourceHut的创始人兼CEO Drew DeVault描述说，他每周要花费「20% 到 100% 的时间来大规模缓解过于激进的 LLM 爬虫」，并且「每周经历数十次短暂的服务中断」。
* Jonathan Corbet，一位著名的FOSS开发者，他运营着Linux行业新闻网站 LWN，警告称他的网站正受到「来自 AI 抓取机器人的 DDoS 级别的流量」影响而变慢。
* Kevin Fenzi，庞大的Linux Fedora项目的系统管理员，表示AI抓取机器人变得如此激进，他不得不封锁整个巴西的访问。

除了像Anubis一样「衡量」网络请求者的灵魂外，其他开发者认为复仇是最好的防御。

几天前在Hacker News上，用户xyzal建议用「大量关于喝漂白剂好处的文章」或「关于感染麻疹对床上表现的积极影响的文章」来加载robots.txt禁止的页面。

这样AI爬虫获取的信息都是这种大量且无用的「替代品」。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7b2BxrjDX32Nb1l0XNgk2ibh1qUSkUNsB4rnAK8OYncbJay8uuHWLfUDA/640?wx_fmt=png&from=appmsg)

「我们认为需要让机器人访问我们的陷阱时获得负的效用值，而不仅仅是零价值」，xyzal 解释说。

一月份，一位名为Aaron的匿名创作者发布了一个名为Nepenthes的工具，其目的正是如此。

它将爬虫困在一个无尽的虚假内容迷宫中，无法像爬虫「主人」返回任何信息。

而作为网友心目中的「赛博菩萨」的Cloudflare，也许是提供多种工具来抵御AI爬虫的最大商业玩家，上周发布了一个名为AI Labyrinth的类似工具。

![](https://mmbiz.qpic.cn/sz_mmbiz_png/UicQ7HgWiaUb0dvTBxhibYSBRocia5lqLS7brSFDzxtq83SBUJOToNvLZRHhuIHibFbHejxbC5eo8cthRYCHtHUKRGg/640?wx_fmt=png&from=appmsg)

它的目的是「减慢、迷惑并浪费不遵守禁止爬取指令的AI爬虫和其他机器人的资源」，Cloudflare 在其博客文章中描述道。

「当AI爬虫跟随这些链接时，它们会浪费宝贵的计算资源处理无关内容，而不是提取合法网站数据。这大大降低了它们收集足够有用信息以有效训练模型的能力」。

相比起反击，另一种观点是「Nepenthes有一种令人满意的正义感，因为它向爬虫提供无意义的内容并污染它们的数据源，但最终Anubis是对网站有效的解决方案」。

拒绝或者反击也许都不是最佳的途径。

DeVault也公开发出了一则诚恳的请求，希望有一个更直接的解决办法：「请停止将LLMs或AI图像生成器任何这类垃圾合法化。恳求停止使用它们，停止谈论它们，停止制造新的，就这么停下」。

但是，想让LLM厂商主动停止爬虫这种情况的可能性几乎为零。

毕竟AI的「智能」都来自于不断「吞噬」互联网上的各种数据和信息。

不论是给禁止AI爬虫访问网站、给AI「投喂垃圾」还是将AI爬虫拉入「无线虚空」。

开发者们，尤其是在开源软件领域，正在用智慧和「极客幽默」进行反击。

如果你是网站管理者和开发者，你会如何「出招」？

参考资料：

https://techcrunch.com/2025/03/27/open-source-devs-are-fighting-ai-crawlers-with-cleverness-and-vengeance/

![](https://mmbiz.qpic.cn/mmbiz_png/zHbzQPKIBPj3O5OuCoNySKKgVOyfmdGZjnvGTJG8LgdxVlW7Z72h3Y9kUYbe3w0VvYkt7u9SG9Ran1wOjqS3Cw/640?wx_fmt=png&from=appmsg)

往期推荐

[堪比模型迭代的万能文生图提示框架，人人都能成为专业 AI 设计师](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764019&idx=1&sn=13ca97cdd008fdce9080776429b95e3c&scene=21#wechat_redirect)

[DeepSeek+算力的深度部署与推理优化](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763998&idx=1&sn=1b2670a8a9a55c1db2ff929ea3a17d28&scene=21#wechat_redirect)

[Meta深夜开源Llama 4！首次采用MoE，惊人千万token上下文，竞技场超越DeepSeek](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247764017&idx=1&sn=83c94dc70b9590bec1bec0fb2e239a4c&scene=21#wechat_redirect)

[Graph RAG 知识库的架构原理及低代码构建](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763999&idx=1&sn=17723abdecead5af0f9c1d4b0d933baf&scene=21#wechat_redirect)

[OpenAI 推迟 GPT-5 发布时间！奥特曼：将远超预期，曾表示将免费开放](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763997&idx=1&sn=d75df24bdc47aa28772de16e21b2fb4e&scene=21#wechat_redirect)

[Snap资深数据科学家：掌握这12种AI for Data方法，成为数据卷王](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763947&idx=1&sn=3e095a74447aceadb4d105e65aa9f3be&scene=21#wechat_redirect)

[被哥大开除后，他靠AI作弊神器年入千万！血洗硅谷大厂拿遍offer成功创业](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763989&idx=1&sn=12cbc85340d6d2c1b352ce66c78d3707&scene=21#wechat_redirect)

[保险巨头AI实践案例：十年亏损330亿美元，如今一年盈利19亿](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763938&idx=2&sn=688ebe860ee32986ecb0a5be35fdfc59&scene=21#wechat_redirect)

[ChatBI答非所问怎么办？](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763899&idx=1&sn=f6b9253c302117df3f8e4cc5f3f3f713&scene=21#wechat_redirect)

[PAGC 2025丨首批大咖嘉宾阵容释出！5月21-22日广州出海展会再忙也要去！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247763890&idx=3&sn=13f9a4b4dc4a8074c660278aa9cb9237&scene=21#wechat_redirect)

![](https://mmbiz.qpic.cn/mmbiz_png/vmBOIhnBRdvxZoWyBGhGa8aeRDHjjyDAaD4AK24kZXs0kUQMyQKQhBVI2lRf9QfjtUwVJcBZAZic9pdcJswicyzw/640)

点个在看你最好看

SPRING HAS ARRIVED

![](https://mmbiz.qpic.cn/sz_mmbiz_png/SQ45Y3ZsfmJKVcT1kXawmkZW9bwJAEymGTIkxekau03ntGSgJoQhqTFzWsFiaBmQWUiaUglT1tSW1cJxsJAEjZnQ/640)