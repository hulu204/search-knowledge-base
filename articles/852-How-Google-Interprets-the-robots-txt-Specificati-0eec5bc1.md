---
title: 'How Google Interprets the robots.txt Specification'
company: Google
tag: 爬虫抓取
date: 2026-01-01
url: https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt
account: 
origin: harvest2-202607
---
* [首页](https://developers.google.com/?hl=zh-cn)
* [Crawling infrastructure](https://developers.google.com/crawling?hl=zh-cn)
* [文档](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers?hl=zh-cn)

发送反馈

使用集合让一切井井有条

根据您的偏好保存内容并对其进行分类。

# Google 如何解读 robots.txt 规范

Google 的自动[抓取工具](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers?hl=zh-cn)支持 [REP（robots 协议）](https://www.rfc-editor.org/rfc/rfc9309.html)。这意味着，在抓取某一网站之前，Google 抓取工具会下载并解析该网站的 robots.txt 文件，以提取关于网站中哪些部分可以被抓取的信息。REP 不适用于由用户控制的 Google 抓取工具（例如 Feed 订阅），也不适用于用来提高用户安全性的抓取工具（例如恶意软件分析）。

本页介绍了 Google 对 REP 的解读。有关原始标准的信息，请查看 [RFC 9309](https://www.rfc-editor.org/rfc/rfc9309.html)。

## 什么是 robots.txt 文件

如果您不希望抓取工具访问您网站中的部分内容，可以创建包含相应规则的 robots.txt 文件。robots.txt 文件是一个文本文件，其中包含关于哪些抓取工具可以访问网站的哪些部分的规则。例如，example.com 的 robots.txt 文件可能如下所示：

```
# This robots.txt file controls crawling of URLs under https://example.com.
# All crawlers are disallowed to crawl files in the "includes" directory, such
# as .css, .js, but Google needs them for rendering, so Googlebot is allowed
# to crawl them.
User-agent: *
Disallow: /includes/

User-agent: Googlebot
Allow: /includes/

Sitemap: https://example.com/sitemap.xml
```

如果您是首次接触 robots.txt，请先阅读我们的 [robots.txt 简介](https://developers.google.com/search/docs/crawling-indexing/robots/intro?hl=zh-cn)。您还可以找到[关于创建 robots.txt 文件的提示](https://developers.google.com/crawling/docs/robots-txt/create-robots-txt?hl=zh-cn)。

## 文件位置和有效范围

您必须将 robots.txt 文件放在网站的顶级目录中，并为其使用支持的协议。和其他网址一样，robots.txt 文件的网址也区分大小写。就 Google 搜索而言，支持的协议包括 HTTP、HTTPS 和 FTP。使用 HTTP 和 HTTPS 协议时，抓取工具会使用 HTTP 无条件 `GET` 请求来提取 robots.txt 文件；使用 FTP 时，抓取工具会使用标准 `RETR (RETRIEVE)` 命令，并采用匿名登录方式。

robots.txt 文件中列出的规则只适用于该文件所在的主机、协议和端口号。

## 有效 robots.txt 网址的示例

下表列出了 robots.txt 网址及其适用的网址路径的示例。
第一列包含 robots.txt 文件的网址，第二列包含 robots.txt 文件将适用及不适用的网域。

| robots.txt 网址示例 | |
| --- | --- |
| `https://example.com/robots.txt` | 这属于一般情况。该网址对其他子网域、协议或端口号来说无效。对同一个主机、协议和端口号上的所有子目录中的所有文件有效。 适用于：  * `https://example.com/` * `https://example.com/folder/file`  不适用于：  * `https://other.example.com/` * `http://example.com/` * `https://example.com:8181/` |
| `https://www.example.com/robots.txt` | 子网域上的 robots.txt 仅对该子网域有效。  适用于： `https://www.example.com/`  不适用于：   * `https://example.com/` * `https://shop.www.example.com/` * `https://www.shop.example.com/` |
| `https://example.com/folder/robots.txt` | 不是有效的 robots.txt 文件。抓取工具不会检查子目录中的 robots.txt 文件。 |
| `https://www.exämple.com/robots.txt` | IDN 等同于其对应的 punycode 版本。另请参阅 [RFC 3492](https://www.ietf.org/rfc/rfc3492.txt)。 适用于：  * `https://www.exämple.com/` * `https://xn--exmple-cua.com/`   不适用于： `https://www.example.com/` |
| `ftp://example.com/robots.txt` | 适用于： `ftp://example.com/`  不适用于： `https://example.com/` |
| `https://212.96.82.21/robots.txt` | 以 IP 地址作为主机名的 robots.txt 只在抓取作为主机名的相应 IP 地址时有效。该 robots.txt 文件并不会自动对该 IP 地址上托管的所有网站有效，但该文件可能是共享的，在此情况下，它也可以在共享主机名下使用。  适用于： `https://212.96.82.21/`  不适用于： `https://example.com/`（即使托管在 `212.96.82.21` 上） |
| `https://example.com:443/robots.txt` | 标准端口号（HTTP 为 `80`，HTTPS 为 `443`，FTP 为 `21`）等同于其默认的主机名。  适用于：   * `https://example.com:443/` * `https://example.com/`   不适用于： `https://example.com:444/` |
| `https://example.com:8181/robots.txt` | 非标准端口号上的 robots.txt 文件只对通过这些端口号提供的内容有效。  适用于： `https://example.com:8181/`  不适用于： `https://example.com/` |

## 错误处理和 HTTP 状态代码

在请求 robots.txt 文件时，服务器响应的 HTTP 状态代码会影响 Google 抓取工具使用 robots.txt 文件的方式。下表总结了 Googlebot 针对各种 HTTP 状态代码处理 robots.txt 文件的方式。

| 错误处理和 HTTP 状态代码 | |
| --- | --- |
| `2xx (success)` | 表示成功的 HTTP 状态代码会提示 Google 抓取工具处理服务器提供的 robots.txt 文件。 |
| `3xx (redirection)` | Google 会按照 [RFC 1945](https://www.ietf.org/rfc/rfc1945.txt) 的规定跟踪至少五次重定向，然后便会停止，并将其作为 robots.txt 文件的 `404` 错误来处理。这也适用于重定向链中任何被禁止访问的网址，因为抓取工具会由于重定向而无法提取规则。  Google 不会跟踪 robots.txt 文件中的逻辑重定向（框架、JavaScript 或元刷新型重定向）。 |
| `4xx (client errors)` | Google 抓取工具会将所有 `4xx` 错误（`429` 除外）解读为网站不存在有效的 robots.txt 文件，这意味着 Google 会假定没有任何抓取限制。  请勿使用 `401` 和 `403` 状态代码限制抓取速度。`4xx` 状态代码（`429` 除外）对抓取速度没有影响。 [了解如何限制抓取速度](https://developers.google.com/crawling/docs/crawlers-fetchers/reduce-crawl-rate?hl=zh-cn)。 |
| `5xx (server errors)` | 如果 Google 找到了 robots.txt 文件，但无法提取该文件，则会遵循以下行为方式：   1. 在前 12 小时内，Google 会停止抓取相应网站，但会继续尝试提取 robots.txt 文件。 2. 如果 Google 无法提取新版本，那么在接下来的 30 天内，Google 将使用上一个正常版本，同时仍会尝试提取新版本。`503 (service unavailable)` 错误会导致非常频繁的重试操作。如果没有可用的缓存版本，Google 会假定没有任何抓取限制。 3. 如果在 30 天后错误仍未更正：    * 如果 Google 能够全面抓取相应网站，则会遵循没有 robots.txt 文件时的行为方式，但仍会继续检查是否有新版本。    * 如果 Google 无法全面抓取相应网站，则会停止抓取该网站，但仍会定期请求 robots.txt 文件。 |
| 其他错误 | 对于因 DNS 或网络问题（例如超时、响应无效、重置或断开连接、HTTP 组块错误等）而无法抓取的 robots.txt 文件，系统在处理时会将其视为[服务器错误](#server-error)。 |

## 缓存

Google 通常会将 robots.txt 文件的内容最多缓存 24 小时，但在无法刷新缓存版本的情况下（例如出现超时或 `5xx` 错误时），缓存时间可能会延长。已缓存的响应可由各种不同的抓取工具共享。
Google 会根据 [max-age Cache-Control](https://www.rfc-editor.org/rfc/rfc9110.html) HTTP 标头来延长或缩短缓存生命周期。

## 文件格式

robots.txt 文件必须是采用 [UTF-8](https://en.wikipedia.org/wiki/UTF-8) 编码的纯文本文件，且各行代码必须以 `CR`、`CR/LF` 或 `LF` 分隔。

Google 会忽略 robots.txt 文件中的无效行，包括 robots.txt 文件开头处的 Unicode [字节顺序标记](https://en.wikipedia.org/wiki/Byte_order_mark) (BOM)，并且只使用有效行。例如，如果下载的内容是 HTML 格式而非 robots.txt 规则，Google 会尝试解析内容并提取规则，而忽略其他所有内容。

同样，如果 robots.txt 文件的字符编码不是 UTF-8，Google 可能会忽略不属于 UTF-8 范围的字符，从而可能会导致 robots.txt 规则无效。

Google 强制执行的 robots.txt 文件大小限制是 500 [KiB](https://en.wikipedia.org/wiki/Kibibyte)，并忽略超过该上限的内容。您可以通过整合会导致 robots.txt 文件过大的规则来减小 robots.txt 文件的大小。例如，将已排除的内容放在一个单独的目录中。

## 语法

有效的 robots.txt 行由一个字段、一个冒号和一个值组成。字段名称不区分大小写（例如，`User-agent` 和 `user-agent` 被视为相同）。可以选择是否使用空格，但建议使用空格，有助于提高可读性。系统会忽略行开头和结尾的空格。若要添加注释，请在注释前面加上 `#` 字符。请注意，`#` 字符后面的所有内容都会被忽略。常见格式为 `<field>:<value><#optional-comment>`。

Google 支持以下字段（不支持 `crawl-delay` 等其他字段）：

* `user-agent`：标识相应规则适用于哪些抓取工具。
* `allow`：可抓取的网址路径。
* `disallow`：不可抓取的网址路径。
* `sitemap`：站点地图的完整网址。

`allow` 和 `disallow` 字段也称为规则（即指令）。这些规则始终以 `rule: [path]` 的形式指定，其中 `[path]` 可以选择性使用。默认情况下，指定的抓取工具没有抓取限制。抓取工具会忽略不带 `[path]` 的规则。

如果指定了 `[path]` 值，该路径值就是 robots.txt 文件所在网站的根目录的相对路径（使用相同的协议、端口号、主机和域名）。路径值必须以 `/` 开头来表示根目录，该值区分大小写。详细了解[基于路径值的网址匹配](#url-matching-based-on-path-values)。

### `user-agent`

`user-agent` 行用来标识相应规则适用于哪些抓取工具。请参阅 [Google 抓取工具和用户代理字符串](https://developers.google.com/crawling/docs/crawlers-fetchers/overview-google-crawlers?hl=zh-cn)，获取可在 robots.txt 文件中使用的用户代理字符串的完整列表。

`user-agent` 字段名称及其值均不区分大小写。

### `disallow`

`disallow` 规则用来指定不能被 `disallow` 规则所属的 `user-agent` 行所标识的抓取工具访问的路径。
抓取工具会忽略不含路径的规则。

Google 无法将禁止抓取的网页的内容编入索引，但可能仍会将其网址编入索引并将其显示在搜索结果中，但不显示摘要。了解如何[阻止编入索引](https://developers.google.com/search/docs/crawling-indexing/block-indexing?hl=zh-cn)。

字段名称 (`disallow`) 不区分大小写，但其值区分大小写。

用法：

```
disallow: [path]
```

### `allow`

`allow` 规则用来指定相应抓取工具可以访问的路径。如果未指定路径，该规则将被忽略。

字段名称 (`allow`) 不区分大小写，但其值区分大小写。

用法：

```
allow: [path]
```

### `sitemap`

根据 [sitemaps.org](https://sitemaps.org) 规定，Google、Bing 和其他主流搜索引擎支持 robots.txt 中的 `sitemap` 字段。

字段名称 (`sitemap`) 不区分大小写，但其值区分大小写。

用法：

```
sitemap: [absoluteURL]
```

`[absoluteURL]` 行指向站点地图或站点地图索引文件的位置。
此网址必须是完全限定网址，包含协议和主机，且无需进行网址编码。此网址不需要与 robots.txt 文件位于同一主机上。您可以指定多个 `sitemap` 字段，并且可以包含的站点地图数量不受限制。站点地图字段不依赖于任何特定的用户代理，只要未被禁止抓取，所有抓取工具都可以追踪它们。

例如：

```
user-agent: otherbot
disallow: /kale

sitemap: https://example.com/sitemap.xml
sitemap: https://cdn.example.org/other-sitemap.xml
sitemap: https://ja.example.org/テスト-サイトマップ.xml
```

## 行和规则分组

通过对每个抓取工具重复 `user-agent` 行，可将适用于多个用户代理的规则组合在一起。

例如：

```
user-agent: a
disallow: /c

user-agent: b
disallow: /d

user-agent: e
user-agent: f
disallow: /g

user-agent: h
```

此示例中有四个不同的规则组：

* 用户代理“a”为一组
* 用户代理“b”为一组
* 用户代理“e”和“f”为一组
* 用户代理“h”为一组

有关组的技术说明，请参阅 [REP 的第 2.1 节](https://www.rfc-editor.org/rfc/rfc9309.html#section-2.1-2.4)。

## 用户代理的优先顺序

对于某个抓取工具而言，只有一个组是有效的。Google 抓取工具会在 robots.txt 文件中查找包含与抓取工具的用户代理相匹配的最具体用户代理的组，从而确定正确的规则组。其他组会被忽略。所有非匹配文本都会被忽略（例如，`googlebot/1.2` 和 `googlebot*` 均等同于 `googlebot`）。这与 robots.txt 文件中的组顺序无关。

如果为用户代理声明多个特定组，则这些组中适用于该特定用户代理的所有规则会在内部合并成一个组。特定于用户代理的组和全局组 (`*`) 不会合并。

### 示例

#### `user-agent` 字段的匹配情况

```
user-agent: googlebot-news
(group 1)

user-agent: *
(group 2)

user-agent: googlebot
(group 3)
```

以下为抓取工具选择相关组的方法：

| 每个抓取工具追踪的组 | |
| --- | --- |
| Googlebot News | `googlebot-news` 遵循组 1，因为组 1 是最具体的组。 |
| Googlebot（网络） | `googlebot` 遵循组 3。 |
| Googlebot Storebot | `Storebot-Google` 遵循组 2，因为没有具体的 `Storebot-Google` 组。 |
| Googlebot News（抓取图片时） | 抓取图片时，`googlebot-news` 遵循组 1。 `googlebot-news` 不会为 Google 图片抓取图片，因此它只遵循组 1。 |
| 其他机器人（网络） | 其他 Google 抓取工具遵循组 2。 |
| Otherbot（新闻） | 抓取新闻内容但未标识为 `googlebot-news` 的其他 Google 抓取工具遵循组 2。即使有相关抓取工具的对应条目，也只有在明确匹配时才会有效。 |

#### 规则分组

如果 robots.txt 文件中有多个组与特定用户代理相关，则 Google 抓取工具会在内部合并这些组。例如：

```
user-agent: googlebot-news
disallow: /fish

user-agent: *
disallow: /carrots

user-agent: googlebot-news
disallow: /shrimp
```

抓取工具会根据用户代理在内部对规则进行分组，例如：

```
user-agent: googlebot-news
disallow: /fish
disallow: /shrimp

user-agent: *
disallow: /carrots
```

`allow`、`disallow` 和 `user-agent` 以外的其他规则会被 robots.txt 解析器忽略。这意味着以下 robots.txt 代码段被视为一个组，因此 `user-agent` `a` 和 `b` 均受 `disallow: /` 规则的影响：

```
user-agent: a
sitemap: https://example.com/sitemap.xml

user-agent: b
disallow: /
```

当抓取工具处理 robots.txt 规则时，会忽略 `sitemap` 行。
例如，下面说明了抓取工具如何理解之前的 robots.txt 代码段：

```
user-agent: a
user-agent: b
disallow: /
```

## 基于路径值的网址匹配

Google 会以 `allow` 和 `disallow` 规则中的路径值为基础，确定某项规则是否适用于网站上的特定网址。为此，系统会将相应规则与抓取工具尝试抓取的网址的路径部分进行比较。路径中的非 7 位 ASCII 字符可以按照 [RFC 3986](https://www.ietf.org/rfc/rfc3986.txt) 作为 UTF-8 字符或百分号转义的 UTF-8 编码字符纳入。

对于路径值，Google、Bing 和其他主流搜索引擎支持有限形式的通配符。这些通配符包括：

* `*` 表示出现 0 次或多次的任何有效字符。
* `$` 表示网址结束。

下表显示了不同的通配符对解析的影响：

| 路径匹配示例 | |
| --- | --- |
| `/` | 匹配根目录以及任何下级网址。 |
| `/*` | 等同于 `/`。结尾的通配符会被忽略。 |
| `/$` | 仅匹配根目录。任何更低级别的网址均可抓取。 |
| `/fish` | 匹配以 `/fish` 开头的任何路径。请注意，匹配时区分大小写。  匹配项：   * `/fish` * `/fish.html` * `/fish/salmon.html` * `/fishheads` * `/fishheads/yummy.html` * `/fish.php?id=anything`   不匹配项：   * `/Fish.asp` * `/catfish` * `/?id=fish` * `/desert/fish` |
| `/fish*` | 等同于 `/fish`。结尾的通配符会被忽略。  匹配项：   * `/fish` * `/fish.html` * `/fish/salmon.html` * `/fishheads` * `/fishheads/yummy.html` * `/fish.php?id=anything`   不匹配项：   * `/Fish.asp` * `/catfish` * `/?id=fish` * `/desert/fish` |
| `/fish/` | 匹配 `/fish/` 文件夹中的任何内容。  匹配项：   * `/fish/` * `/fish/?id=anything` * `/fish/salmon.htm`   不匹配项：   * `/fish` * `/fish.html` * `/animals/fish/` * `/Fish/Salmon.asp` |
| `/*.php` | 匹配包含 `.php` 的任何路径。  匹配项：   * `/index.php` * `/filename.php` * `/folder/filename.php` * `/folder/filename.php?parameters` * `/folder/any.php.file.html` * `/filename.php/`   不匹配项：   * `/`（即使其映射到 /index.php） * `/windows.PHP` |
| `/*.php$` | 匹配以 `.php` 结尾的任何路径。  匹配项：   * `/filename.php` * `/folder/filename.php`   不匹配项：   * `/filename.php?parameters` * `/filename.php/` * `/filename.php5` * `/windows.PHP` |
| `/fish*.php` | 匹配包含 `/fish` 和 `.php`（按此顺序）的任何路径。  匹配项：   * `/fish.php` * `/fishheads/catfish.php?parameters`   不匹配项： `/Fish.PHP` |

## 规则的优先顺序

匹配 robots.txt 规则与网址时，抓取工具会根据规则路径的长度使用最具体的规则。如果规则（包括使用通配符的规则）存在冲突，Google 将使用限制性最弱的规则。

以下示例演示了 Google 抓取工具会对特定网址应用什么规则。

| 示例情况 | |
| --- | --- |
| `https://example.com/page` | ``` allow: /p disallow: / ```   **适用规则**：`allow: /p`，因为它更具体。 |
| `https://example.com/folder/page` | ``` allow: /folder disallow: /folder ```   **适用规则**：`allow: /folder`，因为规则存在冲突时，Google 会使用限制性最弱的规则。 |
| `https://example.com/page.htm` | ``` allow: /page disallow: /*.htm ```   **适用规则**：`disallow: /*.htm`，因为该规则路径更长，并且它与网址中的字符匹配得更多，因此更具体。 |
| `https://example.com/page.php5` | ``` allow: /page disallow: /*.ph ```   **适用规则**：`allow: /page`，因为规则存在冲突时，Google 会使用限制性最弱的规则。 |
| `https://example.com/` | ``` allow: /$ disallow: / ```   **适用规则**：`allow: /$`，因为它更具体。 |
| `https://example.com/page.htm` | ``` allow: /$ disallow: / ```   **适用规则**：`disallow: /`，因为 `allow` 规则仅适用于根网址。 |

发送反馈