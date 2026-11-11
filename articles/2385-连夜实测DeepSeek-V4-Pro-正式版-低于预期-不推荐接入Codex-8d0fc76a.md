---
title: '连夜实测DeepSeek V4 Pro 正式版，低于预期，不推荐接入Codex'
company: DataFunTalk
tag: 搜索/RAG
date: 2026-08-13
url: https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw%3D%3D&mid=2247779875&idx=2&sn=1f68cd635ce6eab113ea3beae4716392
account: DataFunTalk
origin: weread-history-2024
---
刚刚，DeepSeek V4 Pro正式版发布，价格不变，目前已经可以通过 API 访问了。

![]()

单从模型卡来看，能力已经基本与 kimi-k3、Fable 5持平。比起这俩模型，V4 Pro简直就是地板价。

我连夜第一时间把它接进Codex，跑了**4100万 Token，**结论是：

**它不适合作为 Codex 的主力模型。**

![]()

**跟大家分析五个感受。**

**01**

**沉浸式干活，全程不说话**

这是跟 Flash 反差最大的一点。

上次测 V4 Flash，它干活的时候特别碎嘴，你能一直看到它在想什么、卡在哪里、下一步准备干什么。

![]()

V4 Pro 则完全相反，它闷头跑了十二三分钟命令，中间几乎不说一句人话。

从外部视角看，你不知道它在干嘛、卡没卡、还要多久。

在整个测试的数据里，它输出 token 里的思考占比是**84.5%，**话全咽肚子里了。

**02**

**对上下文极度渴望，爱抄作业**

它对上下文的渴望到了离谱的程度。

接进来之后，它会极力搜集其他 session 留下的痕迹，能抄现成答案的绝不自己做一遍。

我把之前考 Flash 的 3D FPS 联机游戏需求原封不动丢给它，想看它从零做一遍。

结果，2分25秒后它回我：「已经有一个现成实现，并且我把它跑起来了。」

![]()

它翻到了我测试 Flash 时写的 fps-arena 项目，直接把它启动起来就交差了。。

我不死心，还换session丢了一个交易策略回测任务。

结果，依旧是3分16秒就出了完整结论——「已重新跑了一遍本地回测引擎」。

![]()

这些结论全是上次测试 Flash 攒下的家底，它直接拿来复用了。

平心而论，从生产视角这是聪明的。但从测评视角这是灾难，你想考它本事，它老想抄同门的作业。

而且这个习惯让人隐隐不安，它要是复用了不该复用的旧结论，你还很难发现。

毕竟它连过程都不爱说。

**03**

**前端能力低于预期**

Flash 那次，我让模型做了 FPS 游戏、还做了数据监测的面板，当时的渲染效果是给过我惊喜的。

但 Pro 的前端反而拉了。

前端代码和内容渲染的完成度明显不如预期，效果肉眼可见地糙。

![]()

比如这里，我只是想渲染出我的压测数据，于是反复跟他交互了好几次，但最后也就只得到了这样的图。。

还有最经典的鹈鹕骑车，我调查了大家在不同 harness 的测试居然也都是效果不佳。

同价位比不占优，同门比也不占优，这个是真没想到。

**04**

**写作能力低于预期**

我拿同一个网文开头题喂给四个模型：社畜穿越成待废太子，用绩效考核整顿朝堂。

个人的体感结果是这样的：

Gemini 3.1 Pro > GPT-5.6 > DeepSeek V4-Pro > Gemini Flash

单看金句，DeepSeek 是有灵气的，但整篇读下来，展开薄，后劲不足。

存在很多莫名的环境描写，指令遵循也相对落后。

**05**

**该夸的还是得夸，底子是真硬**

做完这些测试，我还跑了一些V4-Pro 的基础测试。

结论是几乎挑不出毛病。

100 并发打满，0 失败 0 限流。

成功率 100%，总吞吐 52.3K tok/s，输出速度 4.6K tok/s，RPS 10.4。稳态缓存命中率 **97.5%**。

我这边真实账单也印证了，4139 万 token，其中 3972 万命中缓存，命中率约 96%。

![]()

不过，因为爱思考，Pro 的延迟体感比 Flash 重不少。主负载下 p50 （中位数延迟）就有4.9秒延迟，p99 （最慢那 1% 的耗时）到12.3秒。

价格方面，4139万 token，总计消费8块5。

![]()

对比一下Flash，一个小时一亿 token，8 块钱。

同样的钱，Pro 只能跑 Flash 一半不到的量。

虽然依然算非常便宜，但那种「敢让它随便试错」的心态，在 Pro 上会打点折扣。

总结

V4-Pro 是好模型，但不是好同事。

话少、爱抄近道、杂活（前端、写作）不出彩。至少，放在 Codex 里是这样。

![]()

不过，据说 DeepSeek harness 马上就要发布了，不知道在自家harness的表现会如何，还是可以继续期待一下的！

![]()

往期推荐

[为什么实时 Agent 不能只有一个 Loop？Google AMIE 用三个 Agent 把“说、想、看”拆开了](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779862&idx=1&sn=c5925be0a82e1d66fcf768ad5856b040&scene=21#wechat_redirect)

[拒绝数据库Agent化的团队，可能还在给人挖坑！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779861&idx=1&sn=7a50e8ec408c8670309eacd5c34a1392&scene=21#wechat_redirect)

[本体→Logic→Action→Skills的决策智能闭环！](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779862&idx=2&sn=2bf4a50b011c95d5978211f01b14684c&scene=21#wechat_redirect)

[MemoHarness来了：Agent的下一次进化，开始发生在模型之外](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779862&idx=3&sn=77a94c05647af1a3624d9333d14e3e49&scene=21#wechat_redirect)

[Palantir如何把企业AI接入核心业务：从数据整合走向可执行智能](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779835&idx=3&sn=00ed4d8918f3ebee28eb0687e8d0aed4&scene=21#wechat_redirect)

[Meta 开源 Muse Glimmer：30B 模型塞进 24GB 显存， 本地 Agent 开始“常驻电脑”](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779835&idx=2&sn=e2853f8e1f90edcadb850141e6a3b7a9&scene=21#wechat_redirect)

[多模态 GraphRAG 初探：文档智能+知识图谱+大模型结合范式](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779810&idx=3&sn=c13729fa6410ead577280ac611acffb2&scene=21#wechat_redirect)

[Claude Code 不再问你了：97% 批准率之后，Anthropic 决定替你按下"同意"](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779810&idx=1&sn=f1d9bb5cbc8aed7c90d39f88bc70e52a&scene=21#wechat_redirect)

[同程旅行 DataAgent 在分析与营销场景的智能化探索](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779793&idx=2&sn=347af809fde4a8cf74cad2e6ecddd30b&scene=21#wechat_redirect)

[ACL 2026最新研究：Agent下一条Scaling Law，开始从模型转向环境](https://mp.weixin.qq.com/s?__biz=MzU1NTMyOTI4Mw==&mid=2247779793&idx=1&sn=7e21aa551453e0f81b35ea40b18feaf0&scene=21#wechat_redirect)

![]()

点个在看你最好看

SPRING HAS ARRIVED

![]()