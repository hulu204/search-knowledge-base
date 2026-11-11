---
title: '百度新一代流式计算系统DStream3'
company: 百度
tag: 时效性
date: 2019-09-07
url: https://www.infoq.cn/article/59q2vwK54zScTNXPUiQY
account: 
origin: harvest2-202607
---
[![logo](https://static001.geekbang.org/static/web/nuxt/www.infoq.cn/logo.BJF4WFeC.png)](/)

[首页](https://www.infoq.cn/)

[AI会议 hot](https://www.infoq.cn/archives)

[AI课程 hot](https://time.geekbang.org/resource?pt=1)

[AI应用 hot](https://agicamp.com/?utm_source=infoqbar)

[报告](https://www.infoq.cn/minibook)

[HarmonyOS](https://www.infoq.cn/zones/harmonyos/)

[Snowflake new](https://www.infoq.cn/space/snowflake)

更多 **



** 写点什么

#### **创作场景

**

* 记录自己日常工作的实践、心得
* 发表对生活和职场的感悟
* 针对感兴趣的事件发表随笔或者杂谈
* 从 0 到 1 详细介绍你掌握的一门语言、一个技术，或者一个兴趣、爱好
* 或者，就直接把你的个人博客、公众号直接搬到这里

登录/注册

* 企业动态
* 行业深度
* AI&大模型
* 出海
* 后端
* 芯片&算力
* 架构
* 大数据
* 软件工程
* 云计算
* 大前端
* 管理/文化

# 百度新一代流式计算系统 DStream3

* 程怡

* 2019-09-06
* 本文字数：542 字

  阅读完需：约 2 分钟

![](https://static001.infoq.cn/resource/image/aa/6e/aafff58a9799758d1c2ecceada7bcd6e.png?x-oss-process=image/resize,w_726)

* ![logo](https://static001.geekbang.org/static/web/nuxt/www.infoq.cn/logo.BJF4WFeC.png)

  促进软件开发及相关领域知识与创新的传播
* :   [关于我们](https://www.infoq.cn/about)
  :   [我要投稿](https://www.infoq.cn/contribute)
  :   [合作伙伴](https://www.geekbang.org/partner)
  :   [加入我们](https://www.lagou.com/gongsi/j43775.html)
  :   [关注我们](https://infoq.cn/official/account)
* 联系我们
  :   [内容投稿：editors@geekbang.com](mailto:editors@geekbang.com)
  :   [业务合作：hezuo@geekbang.com](mailto:hezuo@geekbang.com)
  :   [反馈投诉：feedback@geekbang.com](mailto:feedback@geekbang.com)
  :   [加入我们：zhaopin@geekbang.com](mailto:zhaopin@geekbang.com)
  :   联系电话：010-64738142
  :   地址：北京市朝阳区望京北路9号2幢7层A701
* InfoQ 近期会议
  :   [北京 · QCon 全球软件开发大会 2026.4.16-18](https://qcon.infoq.cn/2026/beijing?utm_source=infoq&utm_medium=footer)
  :   [上海 · AICon 全球人工智能开发与应用大会 2026.6.26-27](https://aicon.infoq.cn/2026/shanghai?utm_source=infoq&utm_medium=footer)
* 全球 InfoQ
  :   ![会议图片](https://static001.infoq.cn/resource/image/55/38/55cd81623e36f5ab7a7db74d60b74838.png)[InfoQ En](https://www.infoq.com/)
  :   ![会议图片](https://static001.infoq.cn/resource/image/95/13/95fe851c02c86120e9037eada6a36d13.png)[InfoQ Jp](https://www.infoq.com/jp/)
  :   ![会议图片](https://static001.infoq.cn/resource/image/2a/3e/2aa440b6d94e94f64c508f16da38933e.png)[InfoQ Fr](http://www.infoq.com/fr/)
  :   ![会议图片](https://static001.infoq.cn/resource/image/4e/1e/4e737ce82bc7c8a1c2f2307bcea9a11e.png)[InfoQ Br](http://www.infoq.com/br/)

Copyright © 2026, Geekbang Technology Ltd. All rights reserved. 极客邦控股（北京）有限公司 | [京 ICP 备 16027448 号 - 5](https://beian.miit.gov.cn/)[![京公网安备](data:image/png;base64,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)京公网安备 11010502039052号](http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=11010502039052) [| 产品资质](https://time.geekbang.org/hybrid/certificates)