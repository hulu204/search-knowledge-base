---
title: 'Googlebot will soon speak HTTP/2'
company: Google
tag: 爬虫抓取
date: 2020-09-17
url: https://developers.google.com/search/blog/2020/09/googlebot-will-soon-speak-http2
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# Googlebot 即将支持 HTTP/2 使用集合让一切井井有条 根据您的偏好保存内容并对其进行分类。

2020 年 9 月 17 日，星期四

自 2020 年 11 月起，Googlebot 将开始通过 HTTP/2 抓取某些网站。

自从主流浏览器开始支持 HTTP 的第二个主要修订版本（[即 HTTP/2，简称 h2](https://en.wikipedia.org/wiki/HTTP/2)）以来，网络专业人员[向我们咨询过](https://support.google.com/webmasters/thread/3884161?hl=zh-cn) Googlebot 能否通过升级后的最新版协议抓取内容。

今天，我们在此宣布：从 2020 年 11 月中旬开始，Googlebot 将支持通过 HTTP/2 抓取部分网站。

## 什么是 HTTP/2

正如前文所述，HTTP/2 是 [HTTP 的第二个主要版本](https://tools.ietf.org/html/rfc7540)，即互联网主要用于传输数据的协议。HTTP/2 比其前身更加可靠、高效、快捷，这是因为它所采用的架构以及为客户端（例如您的浏览器）和服务器实现的功能更为强大。如需详细了解 HTTP/2，请参阅关于 [HTTP/2 主题](https://developers.google.com/web/fundamentals/performance/http2?hl=zh-cn)的长篇文章。

## 我们为什么进行这项更改

一般情况下，我们希望这项更改能够使系统在抓取时更高效地使用服务器资源。借助 h2，Googlebot 可以与服务器建立单一 TCP 连接，并高效地通过该连接并行传输多个文件，而无需建立多个连接。建立的连接越少，服务器和 Googlebot 抓取时所用的资源就越少。

## 运作方式

在第一阶段，我们会通过 h2 抓取少量网站，然后逐渐扩大范围，通过 h2 抓取更多网站，这些网站可能会从最初支持的功能（例如请求多路复用）中获益。

Googlebot 会根据以下两点来确定是否通过 h2 抓取网站：该网站是否支持 h2；通过 HTTP/2 抓取内容能否使该网站和 Googlebot 受益。如果您的服务器支持 h2，并且 Googlebot 已经从您的网站上抓取了大量内容，您可能已经有资格升级连接，无需采取任何操作。

如果您的服务器仍然只支持 HTTP/1.1，也没关系。通过此协议抓取内容没有明显的缺点；抓取的质量和数量也将保持不变。

## 如何选择停用

我们的初步测试表明，这不会对索引编制造成任何问题或负面影响，但我们理解，您可能出于各种原因希望停止通过 HTTP/2 抓取您的网站。为此，您可以对服务器做出以下指示：在 Googlebot 尝试通过 h2 抓取您的网站时返回 [421 HTTP 状态代码](https://tools.ietf.org/html/rfc7540#section-9.1.2)。如果这种方法在目前还不可行，您可以[向 Googlebot 团队发送消息](https://www.google.com/webmasters/tools/googlebot-report?hl=zh-cn)（但这只是临时解决方案）。

如果您对 Googlebot 和 HTTP/2 还有其他疑问，请参阅[您可能会提出的问题](#questions)。如果找不到您想要问的问题，请通过 [Twitter](https://twitter.com/googlesearchc) 和[帮助论坛](https://support.google.com/websearch/community?hl=zh-cn)与我们联系。

发布者：Jin Liang 和
[Gary Illyes](https://garyillyes.com/+)

## 您可能会提出的问题

### 为什么现在要升级 Googlebot？

用于支持 Googlebot 通过 h2 抓取内容的软件已经足够成熟，能够在生产环境中使用。

### 我是否需要尽快升级服务器？

这完全由您自己决定。不过，只有在网站支持 h2 并且通过 h2 进行抓取对网站明显有好处时，我们才会改为通过 h2 抓取。如果通过 h2 抓取没有明显的优势，Googlebot 仍会继续通过 h1 抓取。

### 如何测试我的网站是否支持 h2？

[Cloudflare](https://blog.cloudflare.com/tools-for-debugging-testing-and-using-http-2/) 发布了一篇博文，其中介绍了测试网站是否支持 h2 的各种方法，不妨了解一下！

### 如何将我的网站升级到 h2？

这完全取决于您的服务器。我们建议您与服务器管理员或托管服务提供商联系。

### 如何让 Googlebot 通过 h2 抓取我的网站？

您无法这样做。如果网站支持 h2，就可以通过 h2 进行抓取，但前提是这样做可以让网站和 Googlebot 受益。例如，如果通过 h2 抓取不会明显节约资源，那么我们只会继续通过 HTTP/1.1 抓取网站。

### 为什么不通过 h2 抓取所有支持 h2 的网站？

我们通过评估发现，通过 h2 抓取对某些网站（例如 QPS 极低的网站）几乎没有任何好处。因此，我们决定只有在对网站有明显好处时才改为通过 h2 抓取。我们会继续评估性能提升情况，将来可能会变更改用标准。

### 如何知道自己的网站是不是通过 h2 抓取的？

如果网站符合通过 h2 抓取的条件，在 Search Console 中注册的网站所有者将收到一条消息，说明日后部分抓取流量可能会通过 h2 传输。此外，您还可以查看服务器日志（例如，如果您的网站在 Apache 上运行，可以查看 access.log 文件）。

### Googlebot 支持哪些 h2 功能？

Googlebot 支持 h2 的大多数功能。我们仍在评估一些可能对渲染有益的功能（例如服务器推送）。

### Googlebot 是否支持明文 HTTP/2 (h2c)？

不支持。您的网站必须使用 HTTPS 并支持 HTTP/2，才符合通过 HTTP/2 抓取的条件。这与现代浏览器的处理方式相同。

### Googlebot 是否会使用 ALPN 扩展来确定通过哪个协议版本进行抓取？

应用层协议协商 (ALPN) 仅适用于允许通过 h2 抓取的网站，而且唯一能收到响应的协议是 h2。如果服务器在传输层安全协议 (TLS) 握手期间做出响应且协议版本不是 h2，Google 将退避，然后再使用 HTTP/1.1。

### 不同的 h2 功能对抓取有何帮助？

h2 有很多优势，但最明显的优势如下：

* **多路复用和并发**：建立的 TCP 连接越少，消耗的资源就越少。
* **标头压缩**：大幅缩减 HTTP 标头的大小，可节约资源。
* **服务器推送**：此功能尚未启用；仍处于评估阶段。此功能可能对渲染有益，但目前我们无法下定论。

若要详细了解特定的 h2 功能及其与抓取的关系，欢迎通过 [Twitter](https://twitter.com/googlesearchc) 咨询我们。

### Googlebot 通过 h2 抓取时，可以抓取更多内容或更快地抓取内容吗？

h2 的主要优势是能够同时在服务器端和 Googlebot 端节约资源。无论通过 h1 还是 h2 抓取内容，都不会影响我们将您的网站编入索引的方式，因此也不会影响我们计划从您的网站中抓取的内容量。

### 通过 h2 抓取的网站会享有排名优势吗？

不会。

发送反馈