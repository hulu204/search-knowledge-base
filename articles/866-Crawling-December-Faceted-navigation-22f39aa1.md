---
title: 'Crawling December: Faceted navigation'
company: Google
tag: 爬虫抓取
date: 2024-12-17
url: https://developers.google.com/search/blog/2024/12/crawling-december-faceted-nav
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 抓取 12 月：分面导航

2024 年 12 月 17 日，星期二

我们刚刚发布了[关于分面导航最佳实践的新文档](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation?hl=zh-cn)，该文档[最初发布为一篇博文](https://developers.google.com/search/blog/2014/02/faceted-navigation-best-and-5-of-worst?hl=zh-cn)。
以下是新文档页面中的一些重要内容的摘要。

分面导航是一种非常棒的方式，可帮助用户在您的网站上找到所需内容，但如果不谨慎实施，可能会演变为一场 SEO 噩梦。为什么？因为它可以生成近乎无限数量的网址，从而导致：

* **过度抓取**：搜索引擎浪费时间抓取对搜索用户毫无价值的无数网址。
* **发现速度变慢**：过度抓取会减慢系统发现重要新内容的速度。

事实上，迄今为止，网站所有者向我们反馈的过度抓取问题中，最常见的来源便是分面导航。而在绝大多数情况下，只要遵循一些最佳实践，就可以避免出现此类问题。但我们先来梳理一下一些信息。

## 网址问题

分面导航中的每个过滤条件组合通常会创建一个唯一的网址。例如：

```
https://example.com/items.shtm?products=fish&color=radioactive_green&size=tiny
```

更改任何参数（`product`、`color` 或 `size`）都会创建一个新网址，从而导致网址数量激增。这就是问题所在：几乎无限数量的新网址等待被发现。我们来解决这个问题。

## 两种方法

1. **屏蔽分面导航网址**：
   * 如果您不需要将这些网址编入索引，请使用 `robots.txt` 禁止抓取。
   * 或者，使用网址片段 (`#`) 作为过滤条件，因为搜索引擎通常会忽略它们。
2. **优化分面导航网址（如果您需要 Google 抓取这些网址，无论成本如何）**：
   * 为网址参数使用标准 `&` 分隔符。💩 不是合适的参数分隔符字符。
   * 在网址路径中保持顺序一致的过滤条件。
   * 对于没有结果的过滤条件组合，返回 `404` 状态代码。
   * 除非您别无选择（例如，[您有一个单页面应用](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics?hl=zh-cn#avoid-soft-404s)），否则请避免将空白结果重定向到通用的“找不到”页面。

## 重要注意事项

* 您还可以使用 `rel="canonical"` 将变体内容指向主页面，以帮助整合信号。系统需要一段时间才能发现这一机制。
* 过滤条件链接上的 `rel="nofollow"` 可能会阻止抓取，但必须一致地应用。也就是说，指向这些页面的所有链接（内部和外部）都必须具有 `rel="nofollow"` 属性。
* 抓取分面导航网址始终会消耗服务器资源，并且可能会影响新内容的发现。

如果您对[关于分面导航最佳实践的新文档](https://developers.google.com/search/docs/crawling-indexing/crawling-managing-faceted-navigation?hl=zh-cn)有任何建议或需要解释说明，请使用该文档中的反馈工具告诉我们。如果您对分面导航非常感兴趣，并想与他人讨论相关问题，请访问[搜索中心社区](https://goo.gle/sc-forum)，您也可在 [LinkedIn](https://www.linkedin.com/showcase/googlesearchcentral/) 上找到我们。

发布者：[Gary Illyes](https://developers.google.com/search/blog/authors/gary-illyes?hl=zh-cn)

---

## 想详细了解抓取？请查看整个“抓取 12 月”系列：

发送反馈