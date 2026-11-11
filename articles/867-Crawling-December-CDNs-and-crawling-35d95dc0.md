---
title: 'Crawling December: CDNs and crawling'
company: Google
tag: 爬虫抓取
date: 2024-12-24
url: https://developers.google.com/search/blog/2024/12/crawling-december-cdns
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 抓取 12 月：CDN 和抓取

2024 年 12 月 24 日，星期二

内容分发网络 (CDN) 特别适合用于缩短网站的延迟时间，并且通常可以避免与网站流量相关的麻烦。毕竟，它们的主要用途是：即使网站获得大量流量，也能快速传送内容。CDN 中的"D"是指在全球范围内传送或分发内容，因此传输到用户的时间也比仅在某个数据中心托管内容更短。在本文中，我们将探讨如何利用 CDN 来提升网站的抓取速度和用户体验，还将了解抓取 CDN 支持的网站时的一些细微差别。

## 回顾：什么是 CDN？

CDN 基本上是源服务器（网站所在位置）与最终用户之间的中间媒介，并为用户提供（部分）文件。从历史上看，**CDN 最关注的是缓存**，这意味着，一旦用户向您的网站请求网址，CDN 就会将该网址的内容存储在其缓存中一段时间，以便您的服务器在一段时间内无需再次提供该文件。

**CDN 可以从靠近用户的位置向用户提供内容，从而大幅提升网站速度**。例如，如果澳大利亚的用户访问托管在德国的网站，CDN 会从澳大利亚的缓存中为该用户提供内容，从而减少全球范围内的往返时间。无论是否达到光速，[距离仍然很大](https://www.youtube.com/watch?v=gYqF6-h9Cvg&hl=zh-cn)。

最后，**CDN 是一种出色的工具，可保护您的网站过载和免受某些安全威胁**。
借助 CDN 管理的全球流量，它们可以构建可靠的流量模型来检测流量异常，并阻止看似过度或恶意的访问。例如，2024 年 10 月 21 日，[Cloudflare 的系统](https://blog.cloudflare.com/ddos-threat-report-for-2024-q3/)自动检测并缓解了持续约一分钟的 4.2 [Tbps](https://wikipedia.org/wiki/Data-rate_units#Terabit_per_second)（相当大）DDoS 攻击。

## CDN 对网站有何帮助

您可能拥有最快的服务器和最优的上行链路，并且您可能认为无需加速任何内容，但从长远来看，CDN 可以为您节省资金，尤其是如果您的网站规模较大：

* **在 CDN 上缓存**：如果媒体、JavaScript 和 CSS 等资源（甚至 HTML）是通过 CDN 缓存提供的，那么您的服务器就无需花费计算和带宽来提供这些资源，从而减少了服务器负载。这通常也意味着网页在用户的浏览器中加载速度更快，从而[提高转化率](https://www.thinkwithgoogle.com/_qs/documents/9757/Milliseconds_Make_Millions_report_hQYAbZJ.pdf)。
* **流量剧增保护**：CDN 特别擅长识别和屏蔽过度或恶意流量，即使恶意机器人或不法分子会导致服务器过载，用户仍可访问您的网站。  
  除了流量剧增防护之外，用于屏蔽恶意流量的控制功能还可用于屏蔽您不想要的流量，无论是特定的抓取工具、符合特定模式的客户端，还是一直使用同一 IP 地址的网络攻击者。虽然您也可以在服务器或防火墙上执行此操作，但使用 CDN 的界面通常会更容易。
* **可靠性**：即使您的网站停止运行，某些 CDN 也可以向用户提供您的网站。
  当然，这可能仅适用于静态内容，但这可能已经足以确保用户不会将业务转移到其他地方。

简而言之，CDN 是您的好帮手。如果您的网站规模较大，或者您预计（甚至已经）获得大量流量，那么您可能需要根据价格、性能、可靠性、安全性、客户支持、可伸缩性、未来扩展等因素，找到一款符合您需求的 CDN。请与您的托管服务或 CMS 提供商联系，了解您的选项（以及您是否已在使用某个选项）。

## 抓取对使用 CDN 的网站有何影响

在抓取方面，CDN 也可能有所帮助，但可能会导致一些抓取问题（尽管很少）。请耐心听我们讲解。

### CDN 对抓取速度的影响

我们的抓取基础架构旨在允许在由 CDN 提供支持的网站上实现更高的抓取率，CDN 是根据为我们的抓取程序提供网址的服务对应的 IP 地址推断出来的。这种方法在大多数情况下都很有效。

假设您今天开始经营一个图库照片网站，并且恰好有 1,000,007 张图片可供使用。您发布一个包含着陆页、类别页面和详情页面的网站，以展示您的所有内容，最终会生成大量网页。我们在关于[抓取容量限制](https://developers.google.com/crawling/docs/crawl-budget?hl=zh-cn#crawl-capacity-limit)的文档中解释过，虽然 Google 搜索希望尽快抓取所有这些网页，但抓取也不应让您的服务器不堪重负。如果您的服务器在面对越来越多的抓取请求时开始响应缓慢，Google 会进行节流，以防止您的服务器过载。如果我们的抓取基础架构检测到您的网站由 CDN 提供支持，则此类节流的阈值会高得多，并且假定可以同时发送更多请求，因为您的服务器很可能可以处理这些请求，从而更快地抓取您的网店。

但是，在首次访问网址时，CDN 的缓存处于“冷”状态，因为尚未有人请求该网址，所以 CDN 尚未缓存其内容，因此您的源服务器仍需要至少提供一次该网址以“预热”CDN 的缓存。这与 [HTTP 缓存的工作方式](https://developers.google.com/search/blog/2024/12/crawling-december-caching?hl=zh-cn)非常相似。

简而言之，即使您的网店由 CDN 提供支持，您的服务器也需要至少提供一次这 1,000,007 个网址。只有在初次提供网址后，CDN 才能帮助您缓存。这会给您的“抓取预算”带来很大负担，并且抓取速度可能会在几天内保持较高水平；如果您打算一次发布多个网址，请注意这一点。

### CDN 对渲染的影响

正如我们在第一篇[关于资源抓取的“12 月抓取”博文](https://developers.google.com/search/blog/2024/12/crawling-december-resources?hl=zh-cn)中所解释，将资源拆分到各自的主机名或 CDN 主机名 (`cdn.example.com`) 可能会使我们的网站渲染服务 (WRS) 更高效地渲染您的网页。不过，需要注意的是，由于连接到其他主机名会产生开销，因此此做法可能会对网页性能产生负面影响，您需要仔细考虑[网页体验](https://developers.google.com/search/docs/appearance/page-experience?hl=zh-cn)与渲染性能。

如果您使用 CDN 支持主要主机，则可以避免此问题：一个主机名用于查询，并且关键的渲染资源很可能从 CDN 的缓存中提供，因此您的服务器无需提供这些资源（并且不会影响网页体验）。

最后，请选择最适合您业务的解决方案：为静态资源使用单独的主机名 (`cdn.example.com`)、使用 CDN 为主要主机名提供支持，或者同时使用这两种方法。Google 的抓取基础架构可以毫无问题地支持这两种方法。

## 当 CDN 过度保护时

由于 CDN 具有流量剧增防护功能以及抓取工具的抓取方式，您希望能访问您网站的网络机器人有时可能会最终进入 CDN 的屏蔽名单，通常是其 Web 应用防火墙 (WAF) 的屏蔽名单。这会阻止抓取工具访问您的网站，最终可能会导致您的网站无法显示在搜索结果中。屏蔽可能会以多种方式发生，有些屏蔽方式比其他屏蔽方式对网站在 Google 搜索结果中的呈现更有害，而且由于屏蔽发生在 CDN 端，因此您可能很难（或根本无法）控制。在本文中，我们将其分为两类：硬性屏蔽和软性屏蔽。

### 硬屏蔽

硬屏蔽是指 CDN 向抓取请求发送的响应是某种形式的错误。
这些错误可以是：

* **HTTP `503`/`429` 状态代码**：发送[这些状态代码是表示暂时性屏蔽的首选方式](https://developers.google.com/crawling/docs/troubleshooting/http-status-codes?hl=zh-cn#5xx-server-errors)。这样您就有时间对 CDN 的意外屏蔽做出反应。
* **网络超时**：CDN 的网络超时会导致受影响的网址从 Google 的搜索索引中移除，因为这些[网络错误被视为终端“硬”错误](https://developers.google.com/crawling/docs/troubleshooting/dns-network-errors?hl=zh-cn)。
  此外，它们还可能会显著影响您网站的抓取速度，因为它们会向我们的抓取基础架构发出网站过载的信号。
* **带有 HTTP `200` 状态代码的随机错误消息**：也称为[软错误](https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors?hl=zh-cn#soft-404-errors)，这种情况尤其严重。如果 Google 端将错误消息视为“严重”错误（例如 HTTP `500`），Google 会将该网址从 Google 搜索中移除。如果 Google 无法将错误消息检测为“硬性”错误，则可能会将所有包含相同错误消息的网页视作重复网页，并从 Google 搜索索引中移除。由于 Google 索引编制系统没有太多动力请求重新抓取重复网址，因此从这种情况中恢复可能需要更长时间。

### 软屏蔽

当 CDN 显示“您确定您是人类”插页式内容时，可能会“弹出”（双关）类似的问题。

![Crawley 对被称为人类感到困惑](https://developers.google.com/static/search/blog/images/crawling-december-crawley-confused.png?hl=zh-cn)

我们的抓取工具实际上确信自己不是人类，也不会假装是人类。
他们只想爬行网络。不过，当出现插页式内容时，抓取工具看到的只有插页式内容，而非您的精彩网站。对于这些机器人验证插页式内容，我们强烈建议您以 503 HTTP 状态代码的形式向自动化客户端（例如抓取工具）发送明确信号，表明内容暂时不可查看。这样可以确保系统不会自动从 Google 索引中移除内容。

### 调试屏蔽

如果同时存在硬屏蔽和软屏蔽，最简单的检查方法是使用 [Search Console 中的网址检查工具](https://support.google.com/webmasters/answer/9012289?hl=zh-cn)并观察渲染的图片：如果显示的是您的网页，则表示一切正常；如果显示的是空白网页、错误或包含机器人验证的网页，则您可能需要与 CDN 联系。

此外，为了帮助您解决这些意外屏蔽问题，Google、其他搜索引擎和其他抓取工具运营商会发布[我们的 IP 地址](https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot?hl=zh-cn)，以帮助您识别我们的抓取工具，并在您认为合适的情况下，从 WAF 规则中移除被屏蔽的 IP，甚至将其列入许可名单。您可以在哪里执行此操作取决于您使用的 CDN；幸运的是，大多数 CDN 和独立 WAF 都有详细说明文档。我们稍微搜索了一下，发现了以下一些参考页面（截至本文发布时）：

* Cloudflare：<https://developers.cloudflare.com/bots/get-started/free/#visibility>
* Akamai：<https://www.akamai.com/products/bot-manager>
* Fastly：<https://www.fastly.com/products/bot-management>
* F5：<https://clouddocs.f5.com/bigip-next/20-2-0/waf_management/waf_bot_protection.html>
* Google Cloud：[https://cloud.google.com/armor/docs/bot-management](https://cloud.google.com/armor/docs/bot-management?hl=zh-cn)

如果您需要自己的网站显示在搜索引擎中，我们强烈建议您检查您关注的抓取工具是否可以访问您的网站。请注意，IP 地址可能会在您不知情的情况下自动列入屏蔽名单，因此不妨经常查看屏蔽名单，确保您的网站在搜索结果中和其他方面取得成功。如果屏蔽名单非常长（与此博文类似），请尝试只查找 IP 范围的前几个分段，例如，您可以只查找 `192.168`，而不是 `192.168.0.101`。

这是[“抓取 12 月”博文系列](https://developers.google.com/search/blog?hl=zh-cn#crawling-december)的最后一篇，希望您喜欢这些博文，就像我们喜欢撰写它们一样。如果您有任何反馈，您知道该怎么做。

发布者：[Martin Splitt](https://developers.google.com/search/blog/authors/martin-splitt?hl=zh-cn) 和 [Gary Illyes](https://developers.google.com/search/blog/authors/gary-illyes?hl=zh-cn)

---

## 想详细了解抓取？请查看整个“抓取 12 月”系列：

发送反馈