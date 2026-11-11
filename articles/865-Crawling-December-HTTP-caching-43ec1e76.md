---
title: 'Crawling December: HTTP caching'
company: Google
tag: 爬虫抓取
date: 2024-12-09
url: https://developers.google.com/search/blog/2024/12/crawling-december-caching
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 抓取 12 月：HTTP 缓存

2024 年 12 月 9 日（星期一）

请允许我们缓存，拜托啦。

多年来，随着网络蓬勃发展，Google 抓取量也日益攀升。虽然 Google 的抓取基础架构支持启发式缓存机制，但实际上一直以来，可从本地缓存返回的请求数量在逐渐减少：10 年前，总抓取量中约有 0.026% 的内容可缓存，尽管这个数字已然不高，但如今已降至 0.017%。

## 为什么缓存很重要？

网络就像一块大拼图，缓存是其中不可或缺的那一块。缓存可让网页在用户再次访问时快速加载，节省计算资源，进而节省自然资源，并为客户端和服务器节省大量昂贵的带宽。

特别是如果您的网站非常庞大，且各个网址下的内容很少更改，那么允许在本地进行缓存，有助于我们更高效地抓取您的网站。Google 的抓取基础架构支持 [HTTP 缓存标准](https://www.rfc-editor.org/rfc/rfc9111.html)所定义的启发式 HTTP 缓存，具体而言，就是通过 `ETag` 响应和 `If-None-Match` 请求标头以及 `Last-Modified` 响应和 `If-Modified-Since` 请求标头提供支持。

我们强烈建议您使用 `ETag`，因为它不易出错（不同于 `Last-Modified` 值，它不是结构化值）。如果可以的话，请同时设置这两个值：网络会感谢您的。或许吧。

您可以自行决定内容更改是否需要客户端刷新缓存。我们建议您在内容有重大更改时要求刷新缓存；如果您仅更新了网页底部的版权日期，则可能不属于重大更改。

## `ETag` 和 `If-None-Match`

Google 的抓取工具支持基于 `ETag` 的条件请求，正如 [HTTP 缓存标准](https://www.rfc-editor.org/rfc/rfc9111.html)中所定义的那样。也就是说，若要向 Google 抓取工具发出缓存偏好设置信号，请将 `Etag` 值设为任意 ASCII 字符串（通常是内容或版本号的哈希值，但也可以是 π 的一部分，具体由您决定），该字符串因访问网址所托管内容的表示法而异。例如，如果您在同一网址下托管同一内容的不同版本（例如，移动版和桌面版），则每个版本都可以有专属的 `ETag` 值。

支持缓存的 Google 抓取工具会发送 `ETag` 值，该值是之前在 `If-None-Match header` 中抓取该网址时返回的值。如果抓取工具发送的 `ETag` 值与服务器生成的当前值相匹配，您的服务器应返回 HTTP `304`（未修改）状态代码，且没有 HTTP 正文。没有 HTTP 正文，这一点至关重要，原因如下：

* 您的服务器无需耗费计算资源来实际生成内容；也就是说，您可以节省资金
* 您的服务器不必传输 HTTP 正文；也就是说，您可以节省资金

在客户端（例如用户的浏览器或 Googlebot）上，系统会从客户端的内部缓存中检索该网址下的内容。由于不涉及数据传输，因此速度快如闪电，不仅能让用户满意，还能节省资源。

## `Last-Modified` 和 `If-Modified-Since`

与 `ETag` 类似，Google 抓取工具也支持 `Last-Modified based` 条件请求，完全符合 HTTP 缓存标准中的定义。从语义的角度来看，这与 `ETag` 的运作方式相同，二者都是使用标识符来决定资源是否可缓存。从客户端的角度来看，这可提供与 `ETag` 相同的优势。

如果您将 `Last-Modified` 用作缓存指令，我们有几点建议：

1. `Last-Modified` 标头中的日期格式必须符合 [HTTP 标准](https://www.rfc-editor.org/rfc/rfc9110.html)。为了避免出现解析问题，我们建议您使用以下日期格式：“星期几，DD Mon YYYY HH:MM:SS 时区”。例如，“Fri, 4 Sep 1998 19:15:56 GMT”。
2. 虽然 `Cache-Control` 标头的 `max-age` 不是必需字段，但建议您一并设置，从而帮助抓取工具确定何时重新抓取特定网址。将 `max-age` 字段的值设置为预计内容保持不变的秒数。例如 `Cache-Control: max-age=94043`。

## 示例

如果您和我一样，不太清楚启发式缓存的工作原理，建议您参考请求和响应链的示例，或许会有所帮助。以下两个链（一个用于 `ETag`/`If-None-Match`，另一个用于 `Last-Modified`/`If-Modified-Since`）可直观呈现其工作原理：

|  | `ETag`/`If-None-Match` | `Last-Modified`/`If-Modified-Since` |
| --- | --- | --- |
| **服务器对抓取的响应：**这是抓取工具用于保存前提条件标头字段 `ETag` 和 `Last-Modified` 的响应。 | ``` HTTP/1.1 200 OK Content-Type: text/plain Date: Fri, 4 Sep 1998 19:15:50 GMT ETag: "34aa387-d-1568eb00" ... ``` | ``` HTTP/1.1 200 OK Content-Type: text/plain Date: Fri, 4 Sep 1998 19:15:50 GMT Last-Modified: Fri, 4 Sep 1998 19:15:56 GMT Cache-Control: max-age=94043 ... ``` |
| **后续抓取工具条件请求：**条件请求基于上一个请求中保存的前提条件标头值。这些值会发送回服务器，以便在 `If-None-Match` 和 `If-Modified-Since` 请求标头中进行验证。 | ``` GET /hello.world HTTP/1.1 Host: www.example.com Accept-Language: en, hu User-Agent: Googlebot/2.1 (+http://www.google.com/bot.html) If-None-Match: "34aa387-d-1568eb00" ... ``` | ``` GET /hello.world HTTP/1.1 Host: www.example.com Accept-Language: en, hu User-Agent: Googlebot/2.1 (+http://www.google.com/bot.html) If-Modified-Since: Fri, 4 Sep 1998 19:15:56 GMT ... ``` |
| **服务器对条件请求的响应：**由于服务器端会验证抓取工具发送的前提条件标头值，因此服务器会向抓取工具返回 `304` HTTP 状态代码（没有 HTTP 正文）。后续的每个请求都会发生这种情况，直到前提条件验证失败（服务器端的 `ETag` 或 `Last-Modified` 日期发生更改）为止。 | ``` HTTP/1.1 304 Not Modified Date: Fri, 4 Sep 1998 19:15:50 GMT Expires: Fri, 4 Sep 1998 19:15:52 GMT Vary: Accept-Encoding If-None-Match: "34aa387-d-1568eb00" ... ``` | ``` HTTP/1.1 304 Not Modified Date: Fri, 4 Sep 1998 19:15:50 GMT Expires: Fri, 4 Sep 1998 19:15:51 GMT Vary: Accept-Encoding If-Modified-Since: Fri, 4 Sep 1998 19:15:56 GMT ... ``` |

如果您想让用户满意，并节省托管费用，请与您的托管/CMS 提供商或开发者讨论如何为您的网站启用 HTTP 缓存。无论如何，至少您的用户会更加满意。

如果您想讨论缓存问题，请前往距您最近的[搜索中心帮助社区](https://goo.gle/sc-forum)；如果您对我们的缓存方式有任何意见，请在与本博文一同发布的[关于缓存的文档](https://developers.google.com/search/docs/crawling-indexing/overview-google-crawlers?hl=zh-cn#http-caching)中留言反馈。

发布者：[Gary Illyes](https://developers.google.com/search/blog/authors/gary-illyes?hl=zh-cn)

---

## 想详细了解抓取？请查看整个“抓取 12 月”系列：

发送反馈