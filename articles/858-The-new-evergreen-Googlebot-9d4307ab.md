---
title: 'The new evergreen Googlebot'
company: Google
tag: 爬虫抓取
date: 2019-05-07
url: https://developers.google.com/search/blog/2019/05/the-new-evergreen-googlebot
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 持续更新的新版 Googlebot 使用集合让一切井井有条 根据您的偏好保存内容并对其进行分类。

2019 年 5 月 7 日，星期二

Googlebot 是一款抓取工具，它会访问网页并将这些网页添加到 Google 搜索索引中。之前，我们在社区的活动和社交媒体中收到最多的问题是：是否可以让 Googlebot 永远适配最新的 Chromium？今天，我们很高兴地告诉大家，现在 Googlebot 可以在将网页呈现给 Google 搜索时运行最新的 Chromium 呈现引擎（本博文发布时最新版本为 74 版）。以后我们会定期更新 Googlebot 的呈现引擎，确保始终支持最新的网络平台功能。

## 对您有何意义

与先前版本相比，Googlebot 现在可支持 1000 多种新功能，例如：

* ES6 和更新的 JavaScript 功能
* [可轻松实现延迟加载的 IntersectionObserver](https://developers.google.com/web/fundamentals/performance/lazy-loading-guidance/images-and-video?hl=zh-cn#lazy_loading_images)
* [Web Components v1 API](https://developers.google.com/web/fundamentals/web-components?hl=zh-cn)

您应该检查一下自己是否仍在进行转换或专门针对 Googlebot 使用 polyfill；如果是这样，请您考虑是否还有这样做的必要。但目前仍存在一些限制，请参阅 [JavaScript 相关问题排查方法](https://developers.google.com/search/docs/crawling-indexing/javascript/fix-search-javascript?hl=zh-cn)并观看[有关 JavaScript 搜索引擎优化 (SEO) 的系列视频](https://www.youtube.com/watch?v=wSwzfEn5-6A&%3Blist=PLKoqnv2vTMUPOalM1zuWDP9OQl851WMM9&hl=zh-cn)。

对此有些想法？您可以在 [Twitter](https://twitter.com/googlesearchc) 或[网站站长论坛](https://support.google.com/webmasters/community/?gpf=%23%21forum%2Fwebmasters&hl=zh-cn)中与我们联系，或加入我们[线上咨询交流时间](https://developers.google.com/search/events/join-office-hours?hl=zh-cn)。

发布者：网站站长趋势分析师团队的 [Martin Splitt](https://50linesofco.de)，自称“友善的互联网精灵”

发送反馈