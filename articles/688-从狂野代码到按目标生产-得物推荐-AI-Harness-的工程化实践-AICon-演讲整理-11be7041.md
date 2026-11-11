---
title: '从狂野代码到按目标生产：得物推荐 AI Harness 的工程化实践｜AICon 演讲整理'
company: 得物
tag: 工程相关
date: 2026-06-30
url: https://juejin.cn/post/7656741994434576427
account: 
origin: harvest-202607
---
# 从狂野代码到按目标生产：得物推荐 AI Harness 的工程化实践｜AICon 演讲整理

[得物技术](/user/2392954206960247/posts)

2026-06-30
  
863
 
阅读9分钟

   

本文是得物技术专家在 AICon 上海演讲整理的技术实录。

「得物推荐 AI Harness 工程化实践系列」的开篇内容，本系列共三篇连载。将系统拆解得物推荐复杂业务场景下，AI代码从生成、防护校验到安全上线的完整技术体系，逐一详解自研AI Harness整体架构框架、全流程安全防护机制、混合智能体核心算法实现，以及工业级工程落地的实战细节。

本篇（上篇）：将整体介绍团队自研的AI Harness体系，包括建设思路、全生命周期防护机制、混合智能体架构及落地效果。

## 一、从 AI Coding 到 AI Builder

AI 写代码已经不新鲜，真正困难的是：怎么让 AI 在复杂业务系统里按目标、按边界、按质量标准持续生产。得物推荐的答案不是再造一个更会写代码的工具，而是围绕 PDCA 全链路搭建一套 AI Harness，让需求可约束、执行不断点、效果可度量、经验可复用。

过去一年，AI Coding 的体验快速成熟。它能写代码、补测试、改 bug，甚至能在局部任务里表现得非常高效。但在真实工程系统里，“能跑” 并不等于 “按目标生产”。

推荐系统尤其如此：链路长、模块多，改一处可能牵动多路召回；效果变化很难解释，经验也很难沉淀成标准。AI 如果只停留在 Do 阶段，就会变成一个更快的代码生成器，而不是一个能推动业务迭代的工程伙伴。

核心变化：AI 化的不只是开发环节，而是整个周期闭环。

## 二、为什么只做 AI Coding 不够

传统工程迭代可以抽象成 PDCA：Plan 对齐目标和边界，Do 完成开发实现，Check 验证效果和风险，Act 沉淀复盘与下一轮优化。AI Coding 主要解决的是 Do，但复杂系统里的失败，往往并不只发生在 Do。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/08c506eeadd645d7b07d60de2e70c246~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=CYKcqedOI8xbswtPuREBRNs87kY%3D)

因此，我们推荐做AI的目标不是让 AI “更会写代码”，而是让 AI 进入完整迭代飞轮：目标更清晰、执行不断点、效果可量化、经验可复用。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/4d8b1a8d187f473d9c4b3d7d991f49e1~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=dEubE8zOB1TIKGpZk%2BJ%2B09RkVtI%3D)

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/0dc7556632ef479f903f28b5de06ff26~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=xI4LODqvBqAuNCuYtbmbhazyeQ0%3D)

AI Coding to AI Builder：能跑不等于按目标生产

## 三、Harness 的本质：不是铁笼，而是环境

讲 Harness 之前，可以先想一部电影：《楚门的世界》。楚门被关在一个巨大的虚假世界里，但真正有效的约束并不是摄像头、海岛或演员，而是环境本身：它让楚门觉得，这就是世界本来的样子。

好的 AI Harness 也是这样。它不是在 AI 外面挂一串硬规则，而是把目标、边界、依赖、验证和回流能力做进协作环境，让 AI 在“自然行动”的同时不容易越界。

好的 Harness 不是铁笼，是环境。它让 AI 觉得自己在自由行动，但每一步都天然处在可验证、可回滚、可复用的工程上下文里。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/572b978f3f9449258748cde605dc1c16~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=NofIg61lhGb0zp5B%2BTCAgsC%2FmYE%3D)

楚门的世界：最有效的harness是环境，让他觉得，世界本该如此

### 七阶段护栏：把 PDCA 拆成可度量协作面

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/2ef64210d6434350a94a66253385cf0f~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=wOBYobCUDNLYw5rPgLC2KZq51WY%3D)

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/741ecf3b5729402082aa7007bfdaf566~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=xT%2FJOXR77loQIdxow7P64sRYjoI%3D)

七阶段护栏：全面覆盖 PDCA

## 四、Plan：用 Contract 把需求变成护栏

很多需求失败，不是因为代码没写好，而是从一开始就理解错了。自然语言 PRD 对人已经有歧义，对 AI 更是如此。所以 Plan 阶段的核心，是把需求改造成 AI 能理解、能执行、能验证的结构化契约。

在得物推荐实践里，T-PRD 会把需求拆成 EP，每个 EP 再绑定影响范围、指标方向、稳定性红线和验收断言。以“负反馈调权”为例，产品说“用户点不感兴趣，希望少推类似商品”，工程上要拆成信号接入、多粒度降权策略、实验与指标护栏等可执行单元。

```
feature: negative_feedback_rerank
goal: 用户点“不感兴趣”后，减少相似商品曝光
scope:
  - Signal: not_interested / dislike
  - Ranking: item / spu / shop / brand
guardrails:
  - 禁止核心点击率显著劣化
  - 必须保留多样性与新颖性观察
  - 所有影响模块需具备回滚路径
```

## 五、Do：让 AI 开发零等待

AI 自主开发最怕“等人”。它写完代码跑不起来，拿不到日志，依赖服务不稳定，就会不断回头问人，最终变成一个很贵的自动补全。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/e3dddcb1db3a4ccaa3d1118ba4667132~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=P8UVNUf5fd0y%2FCR%2FAHYVJQZVn24%3D)

## 六、Check：让推荐效果 7x24 可度量

推荐系统的 Check 很难，因为很多时候团队自己也无法简单判断“这次推荐到底好不好”。传统方式依赖 AUC、GAUC、线上实验和人工评审，成本高，反馈慢。

Axis 推荐 AI 评测平台引入 AI 评审员，模拟不同用户画像，从新颖性、质量、相关性等维度对推荐结果打分。它不是替代线上实验，而是在上线前多一层体验风险雷达。AI 全量评分，专家抽样复核，再把复核知识沉淀回评测体系。

\*\*关键点：\*\*AI 评测不是为了证明模型一定对，而是为了让体验风险更早暴露、让评审口径可以持续沉淀。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/3ddf51c4dcc74ada9458dae1054eeeb5~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=iMgualcNUJ2H0Wof4iAlgyTX1U8%3D)

Check：Axis 推荐 AI 评测平台，把体验评审变成 7x24 自动评审

## 七、Act：把 Bad Case 变成下一轮能力

当线上出现异常，系统会进入 Bad Case 捕获、诊断、沙箱复盘和 Story 沉淀流程。一次问题排查不应该只留下一个结论，而应该留下下一次能直接复用的路径。

## 八、七阶段之后，还有三个深层痛点

流程护栏能解决很多问题，但 Agent 本身仍然有局限：知识会丢、行为会漂、路径不透明。这些不是某个阶段的问题，而是 Agent 工程化承载的问题。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/16dbca059bab49e6b2c525a47f5a7a2d~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=lHQCK7RXFOYkbmwB2WKQg7XBWCU%3D)

## 九、知识治理：文档给人看，Coding 给 AI 戴枷锁

有个程序员笑话：程序员最不喜欢两件事，第一是别人不写文档，第二是我写文档。AI 也一样。你不告诉它规则，它就乱跑；你用纯自然语言告诉它，它又很难稳定理解边界。

得物推荐把知识分成三层：L1 是整体架构，定义不可逾越的行动边界；L2 是模块设计文档，解释关键取舍和依赖关系；L3 是代码注释，最贴近 AI，读代码时随用随取。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/62fa6d7de5b7465e944cbc578cb693e4~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=COp8HwUb7ViZkEa5Lc1IX6XgadY%3D)

在实验中，补充 L3 注释后，简单问题准确率从 52% 提升到 91%，复杂问题准确率达到 100%；简单题整体 token 消耗下降 48%，复杂题下降 26%。单次上下文可能变长，但任务完成轮次显著减少，整体成本反而下降。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/7392f1d28f614129a61f79b05c04698f~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=OJsTtZtXNKn4wpP3HUmKmDYtT9I%3D)

L3 注释评测：让模型从猜测走向可验证

## 十、推查查：Highway 与 ATV 的混合 Agent 架构

在推荐链路排查场景里，一个现实观察是：80% 的问题是高频、可归类、可复现的，20% 的问题是长尾、复杂、需要探索的。两类问题不应该用同一种 Agent 路径解决。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/c9f6f931a34b4eba8fd854ec5e1af640~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=IiBopjEiJOyP%2FL%2FAbVIIMfBwnww%3D)

### Highway：确定性来自代码

一个经典玩笑是：女朋友让你买两根香蕉，如果看到卖苹果的，就买四根。人会脑补，到底买香蕉还是苹果；代码不会，它只会按条件执行。

Highway 的原则也一样：好的 Highway 不是更会猜，而是不脑补。把稳定路径写进代码，让每一次都在同一个地方执行、同一个地方观测、同一个地方定位错误。LLM 只负责最后的结果润色。

### ATV：长尾问题需要受控探索

剩下 20% 的长尾问题无法靠写死程序覆盖。ATV 提供工具、MCP 和约束，让 Agent 按 ReAct 方式自主拆解、调用工具、读取结果、生成结论。探索成功后，Memory 会把轨迹剪枝，把 UID 等一次性特征升维成业务变量，再经过 Dry Run 准入，沉淀为新的 Highway 能力。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/997acbfe4b334b0aa94da259490df629~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=ZxfDSIJb7yBxbtg05ZUqR3RasLo%3D)

Memory：把一次成功变成下次默认能力

## 十一、NOW：从单点提效到工程复利

当 Plan、Do、Check、Act 都被 AI Harness 纳入治理，收益就不只是“某个人写代码快了”，而是整个迭代系统开始转起来。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/81177ce0a0de40cd9eef0a532263d013~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=jgmJFLoVy7XHgTY0k3ZdienISyM%3D)

这套体系的价值，不是让 AI 替代工程师，而是让工程系统本身更适合人和 AI 一起工作。

## 十二、尾声：碳硅梦蝶

两千多年前，庄子醒来，不知道是自己梦见了蝴蝶，还是蝴蝶梦见了自己。今天的 AI 协作也有类似的错觉：我们一边给大模型写 Prompt、喂 Context、鼓励它进入创造状态；另一边，我们自己在流程、工单、SOP 和评测指标里越来越像一个接口。

于是，一个有趣的反转出现了：我们把 AI 当人用，接受它的涌现、幻觉和不确定性；同时，我们也把人当 AI 用，把沟通前提、输入输出、执行边界和健康度工程化。

Harness 就是梦境边缘。它不判断谁在做梦，只保证 AI 梦醒时有规则兜底，人类疲惫时有流程支撑。最终的命题不是“AI 会不会写代码”，而是“我们能不能把 AI 纳入一套可控、可度量、可复用的工程协作系统”。这才是从狂野代码走向按目标生产的真正跃迁。

![image.png](https://p6-xtjj-sign.byteimg.com/tos-cn-i-73owjymdk6/b9c728dd18924bd092459d8df00b9567~tplv-73owjymdk6-jj-mark-v1:0:0:0:0:5o6Y6YeR5oqA5pyv56S-5Yy6IEAg5b6X54mp5oqA5pyv:q75.awebp?rk3s=f64ab15b&x-expires=1785218464&x-signature=iAD3GkOh%2BTDBs1N24MfYMspEZE8%3D)

碳硅梦蝶：Harness 是梦境边缘，也是工程协作的安全网

**下篇预告：**「得物推荐 AI Harness 工程化实践系列」（中篇）《推荐系统诊断Agent：从"调接口"到"会思考"｜得物技术》将基于本文进一步拆解更多原理和工程落地细节。

## 往期回顾

1.[从表单到 Agent：得物社区活动搭建的 AI 实践之路](https://juejin.cn/post/7654831934091657259 "https://juejin.cn/post/7654831934091657259")

2.[从埋点需求到规则资产：Hermes Agent 重构得物数仓工作流](https://juejin.cn/post/7652175561499607081 "https://juejin.cn/post/7652175561499607081")

3.[让 Claude Code 拥有自我进化和记忆系统｜得物技术](https://juejin.cn/post/7649571695950856234 "https://juejin.cn/post/7649571695950856234")

4.[用 LLM Agent 重构告警排查流程｜得物技术](https://juejin.cn/post/7647054541487570980 "https://juejin.cn/post/7647054541487570980")

5.[HorizonVault 技术深潜：如何在 HDD 上做出 100GB/s+ 级大吞吐分布式存储｜得物技术](https://juejin.cn/post/7644440458094231595 "https://juejin.cn/post/7644440458094231595")

## 文 /三白

关注得物技术，每周更新技术干货

要是觉得文章对你有帮助的话，欢迎评论转发点赞～

未经得物技术许可严禁转载，否则依法追究法律责任。