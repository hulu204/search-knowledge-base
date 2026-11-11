---
title: 'Verify Requests from Google Crawlers and Fetchers'
company: Google
tag: 爬虫抓取
date: 2026-01-01
url: https://developers.google.com/search/docs/crawling-indexing/verifying-googlebot
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Crawling infrastructure](https://developers.google.com/crawling?hl=zh-cn)
* [文档](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers?hl=zh-cn)

发送反馈

使用集合让一切井井有条

根据您的偏好保存内容并对其进行分类。

# 验证来自 Google 抓取工具和抓取器的请求

您可以验证对您服务器的请求是否确实[来自 Google](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers?hl=zh-cn)。可以验证 Googlebot 等抓取工具以及其他请求。如果您担心自称是 Google 的垃圾内容发布者或其他麻烦制造者在访问您的网站，则会发现该方法非常有用。

Google 抓取工具和抓取器分为三类：

| 类型 | 说明 | 反向 DNS 掩码 | IP 范围 |
| --- | --- | --- | --- |
| [常见抓取工具](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers?hl=zh-cn) | 用于 Google 产品的常见抓取工具（例如 Googlebot）。它们始终会遵循自动抓取的 robots.txt 规则。 | `crawl-***-***-***-***.googlebot.com` 或 `geo-crawl-***-***-***-***.geo.googlebot.com` | [common-crawlers.json](https://developers.google.com/static/crawling/ipranges/common-crawlers.json?hl=zh-cn) |
| [特殊情况下的抓取工具](https://developers.google.com/crawling/docs/crawlers-fetchers/google-special-case-crawlers?hl=zh-cn) | 为 Google 产品（例如 AdsBot）执行特定功能的抓取工具，并且被抓取的网站与产品之间已就访问权限或针对滥用的特定抓取或提取达成协议。这些抓取工具可能遵循 robots.txt 规则，也可能不遵循。 | `rate-limited-proxy-***-***-***-***.google.com` | [special-crawlers.json](https://developers.google.com/static/crawling/ipranges/special-crawlers.json?hl=zh-cn) |
| [用户触发的抓取器](https://developers.google.com/crawling/docs/crawlers-fetchers/google-user-triggered-fetchers?hl=zh-cn) | 最终用户触发抓取操作的工具和产品功能。例如，[Google 网站验证工具](https://support.google.com/webmasters/answer/9008080?hl=zh-cn)会响应用户请求。由于是用户请求的抓取，因此这些抓取器会忽略 robots.txt 规则。  由 Google 控制的抓取工具源自 `user-triggered-fetchers-google.json` 对象中的 IP，并解析为 `google.com` 主机名。`user-triggered-fetchers.json` 对象中的 IP 解析为 `gae.googleusercontent.com` 主机名。例如，如果 Google Cloud (GCP) 上运行的网站具有需要根据该网站用户的请求提取外部 RSS Feed 的功能，便会使用这些 IP。 | `***-***-***-***.gae.googleusercontent.com` 或 `google-proxy-***-***-***-***.google.com` | [user-triggered-fetchers.json](https://developers.google.com/static/crawling/ipranges/user-triggered-fetchers.json?hl=zh-cn)、[user-triggered-fetchers-google.json](https://developers.google.com/static/crawling/ipranges/user-triggered-fetchers-google.json?hl=zh-cn) 和 [user-triggered-agents.json](https://developers.google.com/static/crawling/ipranges/user-triggered-agents.json?hl=zh-cn) |

您可以通过以下两种方法验证 Google 发来的请求：

* [手动验证](#manual)：如果是一次性查找，请使用命令行工具。对于大多数用例，此方法足以满足需求。
* [自动验证](#automatic)：如果是大规模查找，请使用自动解决方案将抓取工具的 IP 地址与已发布的 Google IP 地址列表进行比对。

## 使用命令行工具

1. 使用 `host` 命令对日志中访问服务器的 IP 地址运行 DNS 反向查找。
2. 验证域名是 `googlebot.com`、`google.com` 还是 `googleusercontent.com`。
3. 使用 `host` 命令对在第 1 步中检索到的域名运行 DNS 正向查找。
4. 验证该域名与日志中访问服务器的原始 IP 地址是否一致。

**示例 1**：

```
host 66.249.66.1
1.66.249.66.in-addr.arpa domain name pointer crawl-66-249-66-1.googlebot.com.

host crawl-66-249-66-1.googlebot.com
crawl-66-249-66-1.googlebot.com has address 66.249.66.1
```

**示例 2**：

```
host 35.247.243.240
240.243.247.35.in-addr.arpa domain name pointer geo-crawl-35-247-243-240.geo.googlebot.com.

host geo-crawl-35-247-243-240.geo.googlebot.com
geo-crawl-35-247-243-240.geo.googlebot.com has address 35.247.243.240
```

**示例 3**：

```
host 66.249.90.77
77.90.249.66.in-addr.arpa domain name pointer rate-limited-proxy-66-249-90-77.google.com.

host rate-limited-proxy-66-249-90-77.google.com
rate-limited-proxy-66-249-90-77.google.com has address 66.249.90.77
```

## 使用自动解决方案

或者，您也可以通过将抓取工具的 IP 地址与 Google 抓取工具和抓取器的 IP 范围列表进行比对，按 IP 地址识别 Googlebot：

* [常见抓取工具，例如 Googlebot](https://developers.google.com/static/crawling/ipranges/common-crawlers.json?hl=zh-cn)
* [AdsBot 等特殊抓取工具](https://developers.google.com/static/crawling/ipranges/special-crawlers.json?hl=zh-cn)
* [用户触发的抓取工具（用户）](https://developers.google.com/static/crawling/ipranges/user-triggered-fetchers.json?hl=zh-cn)
* [用户触发的抓取工具 (Google)](https://developers.google.com/static/crawling/ipranges/user-triggered-fetchers-google.json?hl=zh-cn)
* [用户触发的代理](https://developers.google.com/static/crawling/ipranges/user-triggered-agents.json?hl=zh-cn)

对于可借以访问您网站的其他 Google IP 地址（例如通过 [Apps 脚本](https://developers.google.com/apps-script?hl=zh-cn)），请将访问 IP 地址与通用 [Google IP 地址列表](https://www.gstatic.com/ipranges/goog.json)进行比对。请注意，JSON 文件中的 IP 地址以 [CIDR 格式](https://wikipedia.org/wiki/Classless_Inter-Domain_Routing)表示。

发送反馈