---
title: 'Reduce Google Crawl Rate'
company: Google
tag: 爬虫抓取
date: 2026-01-01
url: https://developers.google.com/search/docs/crawling-indexing/reduce-crawl-rate
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Crawling infrastructure](https://developers.google.com/crawling?hl=zh-cn)
* [文档](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers?hl=zh-cn)

发送反馈

使用集合让一切井井有条

根据您的偏好保存内容并对其进行分类。

# 减慢 Google 抓取速度

Google 抓取工具基础架构采用先进的算法来确定网站的最佳抓取速度。我们的目标是，每次访问您的网站时都尽可能多地抓取网页，但不会过多地占用服务器的带宽。在某些情况下，Google 抓取您的网站可能会给您的基础架构带来沉重负载，或在服务中断期间产生不必要的费用。为了避免这种情况，您可以决定减少 Google 抓取工具发出的请求数量。

## 了解导致抓取量急剧增加的原因

抓取速度急剧提升可能是由于您网站的结构效率低下或网站存在其他问题。根据我们过去收到的报告，最常见的原因包括：

* 网站上网址的配置效率低下，这通常是由网站的特定功能导致的：
  + 网站的分面导航或其他排序和过滤功能
  + 包含特定日期的大量网址的日历
* [动态搜索广告定位条件](https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors?hl=zh-cn#adsbot)

我们强烈建议您与托管公司联系，并查看服务器的近期访问日志，以了解流量的来源，并了解是否符合上述导致抓取量急剧增加的常见原因。然后，请参阅我们关于[管理对分面导航网址的抓取](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation?hl=zh-cn)和[优化抓取效率](https://developers.google.com/search/docs/crawling-indexing/troubleshoot-crawling-errors?hl=zh-cn#improve_crawl_efficiency)的指南。

## 紧急减少抓取器流量（紧急情况）

**警告**：减慢 Google 的抓取速度将会产生广泛的影响，请谨慎考虑。对于 Google 搜索，Googlebot 发现的新网页数量会减少，现有网页的刷新频率会降低（例如，价格和商品库存状况可能需要更长时间才能体现在 Google 搜索中），被移除的网页保留在索引中的时间可能会更长。对于 Google Ads，您的广告系列可能会被取消或暂停，并且您的广告可能无法投放。

如果您急需让抓取速度在短时间（如几个小时或 1-2 天）内减慢，则应向抓取请求返回 `500`、`503` 或 `429` HTTP 响应状态代码（而非 `200`）。在遇到大量包含 `500`、`503` 或 `429` HTTP 响应状态代码的网址时（例如，如果您[停用了您的网站](https://developers.google.com/search/docs/crawling-indexing/pause-online-business?hl=zh-cn)），Google 的抓取基础架构会减慢对您网站的抓取速度。
抓取速度减慢会影响您网站的整个主机名（例如 `subdomain.example.com`），同时影响对会返回错误的网址和会返回内容的网址的抓取。这些错误的数量减少后，抓取速度会自动重新开始提升。

**警告**：我们不建议您长时间（即超过 1-2 天）这么做，因为这可能会对您的网站在 Google 产品中的呈现效果产生负面影响。例如，对于 Google 搜索，如果 Googlebot 一连数天在同一网址上发现上述状态代码，可能会将该网址从 Google 索引中移除。

## 降低抓取速度的特殊请求

如果向 Google 抓取工具提供错误之举在您的基础架构上不可行，您可[提交特殊请求](https://search.google.com/search-console/googlebot-report?hl=zh-cn)，报告抓取速度异常偏高的相关问题，并在请求中提及您网站的最佳抓取速度。您不能请求提高抓取速度，并且请求可能需要几天时间才能得到评估和满足。

发送反馈