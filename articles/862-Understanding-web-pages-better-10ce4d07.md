---
title: 'Understanding web pages better'
company: Google
tag: 索引构建
date: 2014-05-23
url: https://developers.google.com/search/blog/2014/05/understanding-web-pages-better
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 更好地了解网页 使用集合让一切井井有条 根据您的偏好保存内容并对其进行分类。

2014年5月30日星期五

原文：
[Understanding web pages better](https://developers.google.com/search/blog/2014/05/understanding-web-pages-better?hl=zh-cn)

作者：
Erik Hendriks and Michael Xu, 软件工程师；
[Kazushi Nagayama](https://plus.google.com/+KazushiNagayama/?rel=author&hl=zh-cn)

, 网站趋势分析师

[1998年](https://www.google.com/about/company/history/?hl=zh-cn)
，当我们的服务器在
[苏珊·沃西基](https://plus.google.com/+SusanWojcicki/?hl=zh-cn)
(Susan Wojcicki)的车库中运行时，我们完全没必要担心JavaScript或CSS的问题。当时，它们还没有得到广泛应用，JavaScript也只是用于开发网页元素。但眨眼间，情况便发生了翻天覆地的变化。现在，网络中随处可见大量地运用了JavaScript的丰富多彩、美轮美奂的动态网站。今天，我们将讨论Google在呈现更丰富多彩的网站方面的能力（这意味着我们在您的网站上看到的内容更像是现代网络浏览器呈现的内容），其中包括外部资源、执行JavaScript和应用CSS。

以往，我们只关注在HTTP响应主体中获取的原始文本内容，并不会实际解译运行JavaScript的标准浏览器会看到的内容。如果网页中包含由JavaScript呈现的高价值内容，那么当该网页开始显示时，我们无法让搜索者知道，这对于搜索者和网站站长来说都不是想要的结果。

为了解决这个问题，我们决定尝试通过执行JavaScript来了解网页。在当前网络规模下这一点很难做到，但我们认为这非常值得一试。一段时间以来，我们一直在逐步改善这一问题的处理方式。在过去的几个月中，我们的索引系统一直在像普通用户采用的启用了JavaScript

的浏览器一样呈现大量网页。

有时，呈现过程并非尽善尽美，这会给与您网站有关的搜索结果带来负面影响。下面，我们列出了一些潜在的问题，以及在可能的情况下如何避免这些问题的发生：

* 如果单独文件中的JavaScript或CSS等资源被屏蔽（例如通过robots.txt），从而导致Googlebot无法检索这些资源，那么我们的索引系统将无法像普通用户那样看到您的网站。我们建议您允许Googlebot检索JavaScript和CSS，以便我们可以更好地将您的内容编入索引。这一点对于移动网站来说尤为重要，因为CSS和JavaScript等外部资源有助于我们的算法了解相应网页
  [已针对移动设备进行优化](https://developers.google.com/webmasters/smartphone-sites/details?hl=zh-cn#crawling_requirement)
  。
* 如果您的网络服务器无法处理资源抓取请求，则可能会妨碍我们呈现您的网页。如果您想要确保Google可以呈现您的网页，请确保您的服务器能够处理资源抓取请求。
* 适当地将网站降级通常不失为一种非常好的方法。即使用户的浏览器没有兼容的JavaScript实现功能，这也有助于用户畅享您提供的内容。此外，这种方法还有利于停用或关闭了JavaScript的访问者以及尚无法执行JavaScript的搜索引擎。
* 有时，JavaScript可能会因为对于我们来说过于复杂或难以理解而无法执行，在这种情况下，我们将无法完整、准确地呈现相应网页。
* 有些JavaScript会移除网页中的内容（而非添加内容），这会导致我们无法将相应内容编入索引。

为了使问题更易于调试，目前我们正在开发一种工具，以便帮助网站站长更好地了解Google如何呈现其网站。我们非常期待不久后在
[网站站长工具](https://www.google.com/webmasters/tools/home?hl=zh_cn)
中为您提供此工具。

如有任何疑问，请随时访问我们的帮助论坛。

发送反馈