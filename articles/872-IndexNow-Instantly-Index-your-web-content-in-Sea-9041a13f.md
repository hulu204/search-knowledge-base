---
title: 'IndexNow - Instantly Index your web content in Search Engines'
company: Bing
tag: 爬虫抓取
date: 2021-10-18
url: https://blogs.bing.com/webmaster/october-2021/IndexNow-Instantly-Index-your-web-content-in-Search-Engines
account: 
origin: harvest2-202607
---
October182021

# IndexNow - Instantly Index your web content in Search Engines

Ensuring timely information is available for searchers is critical. Yet historically one of the biggest pain points for website owners has been to have search engines quickly discover and consider their latest website changes. It can take days or even weeks for new URLs to be discovered and indexed in search engines, resulting in loss of potential traffic, customers, and even sales.  
  
[IndexNow is a new protocol](https://www.indexnow.org/) created by Microsoft Bing and Yandex, allowing websites to easily notify search engines whenever their website content is created, updated, or deleted. Using an API, once search engines are notified of updates they quickly crawl and reflect website changes in their index and search results.  
  
IndexNow is an initiative for a more efficient Internet: By telling search engines whether an URL has been changed, website owners provide a clear signal helping search engines to prioritize crawl for these URLs, thereby limiting the need for exploratory crawl to test if the content has changed. In the future, search engines intend to limit crawling of websites adopting IndexNow.  
  
IndexNow is also an initiative for a more open Internet: By notifying one search engine you will notify all search engines that have adopted IndexNow.

## How to adopt IndexNow API?

### For developers

If you are a developer, good news, IndexNow is very easy to adopt.

1. Generate a key supported by the protocol using our [online key generation tool](https://www.bing.com/indexnow).
2. Host the key in text file named with the value of the key at the root of your website.
3. Start submitting URLs when your URLs are added, updated, or deleted. You can submit one URL or a set of URLs per API call.

   Submit one URL is easy as sending a simple HTTP request containing the URL changed and your key.

   [https://www.bing.com/indexnow?url=url-changed&key=your-key](https://www.bing.com/IndexNow?url=url-changed&key=your-key)

See detailed instructions at the [Microsoft Bing IndexNow site](https://www.bing.com/indexnow) or the [IndexNow protocol website](https://www.indexnow.org/).

### For non-developers

Good news, many popular platforms have adopted or are planning to adopt IndexNow. If you are using one of these platforms, there is nothing that you will have to do once they have adopted IndexNow.

### Websites

Many large websites (such as eBay, LinkedIn, MSN, GitHub, Bizapedia and more) have adopted Microsoft Bing Webmaster URL submission API and are planning migration to IndexNow. If you publish content or products on these sites, your content will automatically receive the benefits of faster publishing.

#### Content Management Systems (CMS)

We are encouraging all Web Content Management Systems to adopt IndexNow to help their users get their latest website content immediately indexed and minimize crawl load on their websites.

* [WordPress](https://wordpress.org/): Microsoft Bing provided the [open-source code to support IndexNow](https://github.com/WordPress/wordpress-develop/pull/1712) to help WordPress and other CMSs to adopt IndexNow.
* [Wix](https://www.wix.com/) plans to integrate IndexNow.
* [Duda](https://www.duda.co/) will support IndexNow in a few weeks.

#### Content Delivery Networks (CDN)

* [Cloudflare](https://www.cloudflare.com/) is a global network platform. Cloudflare’s network exists between customers and servers that originate content. Cloudflare see trends in the way crawlers and bots access website resources allowing them to proactively send us signals on which crawls are likely to yield fresh content and which are not. Read more about how Cloudflare is supporting IndexNow.org [here](https://blog.cloudflare.com/cloudflare-now-supports-indexnow/).
* [Akamai](https://www.akamai.com/) is the leading content delivery network services provider across all industries including media, software delivery, commerce, and finance. Customers rely on Akamai to provide their users with flawless and up-to-date experiences. By integrating with IndexNow, Akamai plans to make those experiences even better. Read more about Akamai’s plan [here](https://blogs.akamai.com/blog/news/what-microsoft-bings-indexnow-means-for-cdn-users).

#### SEO companies

Key players in the SEO industry are adopting

* [Botify](https://www.botify.com/) plans to integrate IndexNow in its [FastIndex solution](https://www.botify.com/blog/botify-partners-with-bing-promote-indexing-of-your-sites-critical-pages-in-real-time), part of the Botify Activation suite.
* [oncrawl](https://www.oncrawl.com/) plans to integrate IndexNow in their offering.
* [onely](https://www.onely.com/) plans to integrate IndexNow in their offering.
* [Yext](https://www.yext.com/) plans to integrate IndexNow in their offering.

## Let’s evolve the industry

The IndexNow protocol can help the entire industry get their content indexed faster, while using less resources. This helps business get the most timely and relevant information to their customers while creating a better overall experience for everyone.  
  
We will continue to learn and improve at larger scale and adjust crawl rates for sites implementing IndexNow. Our goal is to give each adopter the maximum benefit in terms of indexation, crawl load management and freshness of the content to searchers.  
  
Please refer [here](https://www.indexnow.org/) for more details into implementation. In case you face any challenges during the integration, you can [reach out to us](mailto:bwtsupport@microsoft.com?subject=IndexNow).  
  
Thanks!   
Microsoft Bing Webmaster Tools team