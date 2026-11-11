---
title: 'What Crawl Budget Means for Googlebot'
company: Google
tag: 爬虫抓取
date: 2017-01-16
url: https://developers.google.com/search/blog/2017/01/what-crawl-budget-means-for-googlebot
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 抓取预算对 Googlebot 而言有何意义 使用集合让一切井井有条 根据您的偏好保存内容并对其进行分类。

2017 年 1 月 16 日，星期一

最近，我们听到了很多种关于“抓取预算”的定义，但我们尚未找到一个能够向外部全面描述“抓取预算”含义的术语。这篇博文将会阐明我们实际上已有的定义以及这对 Googlebot 来说意味着什么。

首先，我们想强调一下，大多数发布商都不必担心下文所述的抓取预算。如果新网页预计会于发布当日被抓取，网站站长便无需重点关注抓取预算。同样，如果某个网站所拥有的网址数不足几千个，则大部分时间 Google 都会高效抓取该网站。

如果网站规模更大，或者网站会根据网址参数自动生成网页，那么网站所有者需要更加重视该如何安排抓取优先级、抓取时间以及网站托管服务器可以分配多少抓取资源。

## 抓取速度上限

Googlebot 经过精心设计，是一名优秀的网上公民。它的主要任务是抓取网站，同时确保其抓取操作不会导致网站的用户体验下降。为此，我们提出了“抓取速度上限”这个概念，用于限制对某个具体网站的最高抓取速度。

简而言之，此概念表示 Googlebot 可以使用多少同时载入的并行连接来抓取网站，以及它在完成一次抓取后需要等待多久才能执行下一次抓取。抓取速度可能会变快或变慢，具体取决于下面这几个因素：

* **抓取状况**：如果网站在一段时间内的响应速度很快，抓取速度上限便会升高，这意味着 Googlebot 可以使用更多的连接进行抓取。如果网站运行速度变慢或出现服务器错误，这一上限便会降低，Googlebot 能抓取的网页随之减少。
* [**Search Console 中设定的抓取速度上限**](https://support.google.com/webmasters/answer/48620?hl=zh-cn)：网站所有者可以降低 Googlebot 对其网站的抓取速度。但请注意，设置更高的抓取速度上限并不会自动提高抓取速度。

## 抓取需求

即使未达到抓取速度上限，如果没有索引编制需求，Googlebot 的活动量也会很小。下面这两大因素在确定抓取需求方面起着重要作用：

* **热门程度**：Googlebot 往往会更加频繁地抓取互联网上较为热门的网址，以便在我们的索引中及时更新这些网址的内容。
* **过时性**：我们的系统会努力防止索引中的网址变得过时。

此外，诸如网站迁移之类的网站级事件也可能会导致抓取需求上升，以便将新网址下的内容重新编入索引。

在综合考虑了抓取速度和抓取需求之后，我们将“抓取预算”定义为 Googlebot 可以且需要抓取的网址的数量。

## 影响抓取预算的因素

根据我们的分析，具有大量的低附加值网址可能会不利于对网站进行抓取并将其编入索引。我们发现，低附加值网址可分为以下几类（按影响程度从低到高排序）：

* [分面导航](https://developers.google.com/search/blog/2014/02/faceted-navigation-best-and-5-of-worst?hl=zh-cn)和[会话标识符](https://developers.google.com/search/blog/2007/09/google-duplicate-content-caused-by-url?hl=zh-cn)
* [网站上的重复内容](https://developers.google.com/search/blog/2007/09/google-duplicate-content-caused-by-url?hl=zh-cn)
* [软错误网页](https://developers.google.com/search/blog/2010/06/crawl-errors-now-reports-soft-404s?hl=zh-cn)
* 被黑网页
* [无限空间](https://developers.google.com/search/blog/2008/08/to-infinity-and-beyond-no?hl=zh-cn)和代理
* 劣质和垃圾内容

将服务器资源浪费在此类网页上会使确实有价值的网页失去被抓取的机会，这可能会显著延迟我们在网站上发现精彩内容的时间。

## 热门问题

如果未被抓取，网站便无法出现在 Google 搜索结果中。高效抓取网站有助于我们在 Google 搜索中将网站编入索引。

### 网站速度会影响我的抓取预算吗？错误呢？

使网站运行速度变快既能改善用户体验，又能提高抓取速度。对于 Googlebot 来说，网站运行速度快表明服务器运转正常，因此它可以通过相同数量的连接获得更多的网站内容。反之，出现大量的 5xx 错误或连接超时情况则表明服务器运转不正常，因此 Googlebot 的抓取速度会下降。

我们建议您密切关注 [Search Console 中的“抓取错误”报告](https://support.google.com/webmasters/answer/35120?hl=zh-cn)，并让服务器错误的数量保持较低水平。

### 抓取是一项排名因素吗？

抓取速度加快未必会使网站在搜索结果中的排名升高。
Google 会根据数百个指标对结果进行排名，虽然抓取对出现在搜索结果中必不可少，但它不是一项排名指标。

### 备用网址和嵌入式内容会计入抓取预算中吗？

通常，Googlebot 所抓取的任何网址都会计入网站的抓取预算中。
AMP 或 hreflang 等备用网址以及 CSS 和 JavaScript 等嵌入式内容（包括 [XHR](https://en.wikipedia.org/wiki/XMLHttpRequest) 等 AJAX 调用）可能必须被抓取，此时它们将会耗用网站的抓取预算。同样，很长的重定向链也可能会对抓取产生负面影响。

### 我可以使用 `crawl-delay` 规则控制 Googlebot 吗？

`crawl-delay` 不是一项标准的 robots.txt 规则，所以 Googlebot 不会处理它。

### `nofollow` 规则是否会影响抓取预算？

这要视具体情况而定。被抓取的任意网址都会影响抓取预算，因此即使您的网页将某个网址标记为 `nofollow`，只要您网站上的其他网页或网络上的任何网页未将相应链接标记为 nofollow，Googlebot 就仍会抓取该网址。

### 我通过 robots.txt 禁止抓取的网址是否会对我的抓取预算产生任何影响？

不会，禁止抓取的网址不会影响抓取预算。

若想详细了解如何优化我们对您网站的抓取，请阅读我们关于如何[优化抓取](https://developers.google.com/search/blog/2009/08/optimize-your-crawling-indexing?hl=zh-cn)的博文；尽管该博文发表于 2009 年，时至今日它依然适用。如果您有任何疑问，请在[论坛](https://support.google.com/webmasters/community/?hl=zh-cn)中提问！

发布者：抓取和索引编制团队的 [Gary Illyes](https://garyillyes.com/+)

发送反馈