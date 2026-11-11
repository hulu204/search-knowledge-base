---
title: 'Our new search index: Caffeine'
company: Google
tag: 索引构建
date: 2010-06-09
url: https://developers.google.com/search/blog/2010/06/our-new-search-index-caffeine
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Search Central](https://developers.google.com/search?hl=zh-cn)
* [Google Search Central Blog](https://developers.google.com/search/blog?hl=zh-cn)

发送反馈

# 我们的新搜索索引：Caffeine 使用集合让一切井井有条 根据您的偏好保存内容并对其进行分类。

2010年6月30日星期三

发表者：

Carrie Grimes

，软件工程师

原文链接：

[Our new search index: Caffeine](https://developers.google.com/search/blog/2010/06/our-new-search-index-caffeine?hl=zh-cn)

今天，我们正式宣布：新网络索引系统

Caffeine

的开发完成了。

Caffeine

提供的网络搜索结果比上一个版本索引的结果新

50

％，它能给我们提供最多的网络内容。现在，无论是新闻报道、博客还是论坛帖，在其发表后，您都可以比以往任何时候更快地找到相关内容的链接。

对于那些不是和我们一样以构建搜索引擎谋生的人们来说，以下是一些背景知识：当您搜索谷歌时，您在搜索的不是实时网络；相反，您搜索的是谷歌的索引，它和书背面的清单一样，可以帮助您锁定需要的信息的位置。（点击

[这里](https://www.google.com/howgoogleworks/?hl=zh-cn)

，可以清楚了解索引是如何工作。）

那么，我们为什么要创建一个新的搜索索引系统呢？网络的内容日益剧增，这不仅仅是数目和容量在增多。随着视频、图片、新闻和实时内容的出现，普通网页的内容更丰富也更复杂。此外，人们对搜索的预期也比以往更高。搜索者希望找到最新的相关内容，内容发布者希望在发布内容后立即被人搜索到。

为了紧跟网络的发展趋势并满足不断增长的用户期望，我们创建了

Caffeine

。下图将为您演示

Caffeine

与旧索引系统的工作原理的对比：

![](https://1.bp.blogspot.com/_37WocYcM2lM/TCqzN-SZZ8I/AAAAAAAAAE8/sVZKSGUVI1U/s400/caffeine.jpg)

我们的旧索引有多层结构，它们中间的更新速度不尽相同：有一些会比另外一些更新速度快，而主层则是几个星期更新一次。为了更新旧索引的一层，我们必须分析整个网络，这意味着，在我们找到网页与让您访问该网页之间，将会有很大的延迟。

在

Caffeine

系统下，我们分析网络的小部分，并在全球持续更新我们的搜索索引。当我们发现新网页，或现有网页出现新信息时，我们可以将其直接添加在索引中。这意味着您可以发现比以往任何时候都更新的信息

――

无论该信息是在什么时候、什么地方发布的。

凭借

Caffeine

我们可以检索规模巨大的网页。事实上，每秒钟

Caffeine

能平行处理上几十万个网页。如果这些网页是一堆纸的话，那么每秒钟纸堆都将长高

三英里

。

Caffeine

占据了数据库中近

1

亿

G

的储存空间，并以每天几十万

G

的速度添加新信息。存储这么多信息，您需要

625,000

个存储量最大的

iPod

才能完成；将这些

iPod

头尾相连的话，总长将超过

40

英里

。

着眼于未来，我们创建了

Caffeine

。它不仅可以保证内容更新，还能为我们创建一个更快速全面、并且随着网络信息增长而扩展的搜索引擎打下坚实基础，从而为您提供更多相关的内容。请做好准备，在未来几个月里您可以见证更多的改进。

发送反馈