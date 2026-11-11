---
title: 'Sitemaps ping endpoint is going away'
company: Google
tag: 爬虫抓取
date: 2023-06-26
url: https://developers.google.com/search/blog/2023/06/sitemaps-lastmod-ping
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 站点地图 ping 端点即将停用

站点地图 ping 端点已完全弃用。

2023 年 6 月 26 日，星期一

[站点地图协议于 2005 年推出](https://googleblog.blogspot.com/2005/06/webmaster-friendly.html)，旨在帮助搜索引擎探查新网址，并帮助调度对已发现网址的新抓取操作。协议是一项非常受欢迎的协议，已有超过 15 年未发生变化。
尽管总体思路仍然有用，但在当今的互联网中，某些方面已变得不太实用。

为此，我们将宣布弃用站点地图“ping”端点，并就如何使用 `lastmod` 元素提供更多建议。

## 站点地图 ping

站点地图协议定义了一种[未经身份验证的 REST 方法](https://sitemaps.org/protocol.html#submit_ping)，用于将站点地图提交至搜索引擎。我们的内部研究（以及 Bing 等其他[搜索引擎](https://blogs.bing.com/webmaster/may-2022/Spring-cleaning-Removed-Bing-anonymous-sitemap-submission)）告诉我们，目前这些未经身份验证的站点地图提交内容并不是很实用。实际上，就 Google 搜索而言，绝大部分提交内容都会成为网络垃圾。因此，我们即将停止支持站点地图 ping，且端点会在 6 个月后停止运作。您仍可以[通过 robots.txt 和 Search Console 提交站点地图](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview?hl=zh-cn)，但向已弃用的 REST 端点发送的 HTTP 请求（“ping”）将导致 `404` 错误。使用此端点的任何现有代码或插件都不会引发 Google 搜索问题；您无需进行任何更改（但使用端点也不会执行任何有用的操作）。

## `lastmod` 元素

经过多年观察，我们发现 `lastmod` 元素在提供它的网站的实用程度各有不同。这可能是由发布内容的类型造成的，也可能是由内容管理系统导致的。但现在，`lastmod` 在许多情况下确实有用，我们会将其用作抓取调度信号，调度对我们之前所发现网址的抓取操作。

为使 `lastmod` 元素发挥作用，首先需要采用受支持的日期格式（详见 [sitemaps.org](https://sitemaps.org/protocol.html#lastmoddef)）；如果未采用受支持的格式，Search Console 会在您提交站点地图后立即告知您。其次，需要与现实保持一致。如果网页是在 7 年前进行的更改，但您在 `lastmod` 元素中告知我们更改是在昨天进行的，我们最终不会再相信网页的上次修改日期相关信息。

您可以为您的站点地图中的所有网页使用 `lastmod` 元素，也可以只为您相信的网页使用该元素。例如，某些网站软件可能无法轻松识别首页或某个类别网页的上次修改日期，因为它只汇总网站上的其他网页。在这些情况下，可以为这些网页忽略 `lastmod`。

我们所说的“上次修改”实际上是指“上次**重大**修改”。如果您的 CMS 更改了边栏或页脚中的一段无关紧要的文字，您无需更新该网页的 `lastmod` 值。
但是，如果您更改了主要文本、添加或更改了结构化数据，或者更新了某些链接，请务必更新 `lastmod` 值。

```
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
      <lastmod>2005-01-01</lastmod>
      <loc>http://www.example.com/</loc>
      <changefreq>monthly</changefreq>
      <priority>0.8</priority>
  </url>
</urlset>
```

一个包含所有可能元素的简单站点地图的示例；数据来源：[sitemaps.org](https://sitemaps.org/protocol.html)

如果仔细观察站点地图代码段中的 `xmlns` 属性，您会发现 URI 使用的是 HTTP，而不是 HTTPS。这种情况是正常的：它是对用于解析 XML 中元素的解析器的参考。请不要就此提供更多文档反馈。

## `changefreq` 和 `priority`

Google 仍然根本不使用 `changefreq` 或 `priority` 元素。具体来讲，`changefreq` 在概念上与 `lastmod` 也是重叠的。`priority` 元素是一个非常主观的字段。根据我们的内部研究，此元素通常无法准确反映某个网页相对于网站其他网页的实际优先级。

想要详细了解站点地图？请参阅[我们的文档](https://developers.google.com/search/docs/crawling-indexing/sitemaps/overview?hl=zh-cn)以及 [sitemaps.org](https://sitemaps.org)。如果您只是想就站点地图与我们交流，可以在 [Google 搜索中心论坛](https://goo.gle/sc-forum)和 [Twitter](https://twitter.com/GoOgLeSeArChC) 联系我们。

发布者：[Gary Illyes](https://developers.google.com/search/blog/authors/gary-illyes?hl=zh-cn)

发送反馈