---
title: 'Formalizing the Robots Exclusion Protocol Specification'
company: Google
tag: 爬虫抓取
date: 2019-07-01
url: https://developers.google.com/search/blog/2019/07/rep-id
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 正式制定《robots 协议规范》 使用集合让一切井井有条 根据您的偏好保存内容并对其进行分类。

2019 年 7 月 1 日，星期一

25 年来，robots 协议 (REP) 一直是网络最基本、最重要的组成部分之一。网站所有者可以使用它来部分或完全阻止自动客户端（例如[网页抓取工具](https://en.wikipedia.org/wiki/Web_crawler)）访问其网站。

1994 年，[Martijn Koster](https://en.wikipedia.org/wiki/Martijn_Koster)（网站站长本人）在抓取工具让他的网站负载过重后制定了最初的标准。随着其他网站站长的不断投入，REP 诞生了，它已被搜索引擎采用，以帮助网站所有者更轻松地管理其服务器资源。

不过，REP 从未变成正式的[互联网标准](https://www.ietf.org/standards/)，这意味着开发者多年来对该协议的解释略有不同。自推出以来，REP 仍未更新，无法应对当今的极端情况。这对网站所有者来说是一个具有挑战性的问题，因为不明确的通行标准使得很难正确编写规则。

我们希望帮助网站所有者和开发者在互联网上打造出色的体验，而无需担心如何控制抓取工具。我们与该协议的原作者、网站站长和其他搜索引擎合作，记录了如何在新型网络上使用 REP，并将其提交给 IETF。

拟定的 REP 草稿反映了 20 多年来 robots.txt 规则的实际使用体验，囊括了 Googlebot 和其他主要抓取工具以及大约 5 亿个采用 REP 的网站。这些精细的控制措施让发布商能够决定想要抓取其网站上的哪些内容，并有可能向感兴趣的用户显示这些内容。它不会更改 1994 年创建的规则，而是定义 robots.txt 未定义的所有解析和匹配场景，并针对新型网络扩展它。值得注意的是：

1. 任何[基于 URI 的传输协议](https://en.wikipedia.org/wiki/List_of_URI_schemes)都可以使用 robots.txt。例如，不再仅限于 HTTP，也可以用于 FTP 或 [CoAP](https://en.wikipedia.org/wiki/Constrained_Application_Protocol)。
2. 开发者必须至少解析 robots.txt 的前 500 [Kib](https://en.wikipedia.org/wiki/Kibibyte)。指定文件大小上限可确保连接打开时间不会过长，从而减少服务器上不必要的负载。
3. 新的最长缓存时间（24 小时）或缓存指令值（如果有）让网站所有者可以灵活地随时更新其 robots.txt，并且抓取工具不会使用 robots.txt 请求让网站负载过重。例如，在使用 HTTP 的情况下，Cache-Control 标头可用于确定缓存时间。
4. 该规范现在规定，当以前可访问的 robots.txt 文件因服务器出现故障而无法访问时，系统会在相当长的时间内不抓取已知的禁止抓取网页。

此外，我们还更新了互联网草案中的 [Augmented Backus-Naur form](https://en.wikipedia.org/wiki/Augmented_Backus%E2%80%93Naur_form)，以便更好地定义 robots.txt 的语法，这对开发者解析代码行非常重要。

RFC 是“Request for Comments”（评论请求）的首字母缩写，意思是：我们将草稿上传至 IETF，以便向关注互联网基本构建块的开发者收集反馈意见。我们在努力为网络创作者提供必要的控制功能，以便其告诉我们他们想让多少信息可供 Googlebot 访问，并能够显示在 Google 搜索中，我们必须确保不能出错。

如果您想给我们发表评论、提出问题或打招呼，欢迎访问 [Twitter](https://twitter.com/googlesearchc) 和我们的[网站站长社区](https://support.google.com/webmasters/community?hl=zh-cn)（线上和[线下](https://developers.google.com/search/events?hl=zh-cn)）联系我们。

发布者：[Henner Zeller](https://googlebot.com/)、[Lizzi Sassman](https://www.okaylizzi.com/+) 和 [Gary Illyes](https://garyillyes.com/+)

发送反馈