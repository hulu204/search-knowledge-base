---
title: 'bingbot Series: Maximizing Crawl Efficiency'
company: Bing
tag: 爬虫抓取
date: 2018-10-17
url: https://blogs.bing.com/webmaster/october-2018/bingbot-series-maximizing-crawl-efficiency
account: 
origin: harvest2-202607
---
October162018

# bingbot Series: Maximizing Crawl Efficiency

At the SMX Advanced conference in June, I announced that over the next 18 months my team will focus on improving our Bing crawler bingbot . I asked the audience to share data helping us to optimize our plans. First, I want to say "Thank you"  to those of you who responded and provided us with great insights. Please keep them coming!

To keep you informed of the work we've done so far, we are starting this series of blog posts related to our crawler, bingbot. In this series we will share best practices, demonstrate improvements, and unveil new crawler abilities.

Before drilling into details about how our team is continuing to improve our crawler, let me explain why we need bingbot and how we measure bingbot's success.

## First things first: What is the goal of bingbot?

Bingbot is Bing's crawler, sometimes also referred to as a "spider". Crawling is the process by which bingbot discovers new and updated documents or content to be added to Bing's searchable index. Its primary goal is to maintain a comprehensive index updated with fresh content.

Bingbot uses an algorithm to determine which sites to crawl, how often, and how many pages to fetch from each site. The goal is to minimize bingbot crawl footprint on your web sites while ensuring that the freshest content is available. How do we do that? The algorithmic process selects URLs to be crawled by prioritizing relevant known URLs that may not be indexed yet, and URLs that have already been indexed that we are checking for updates to ensure that the content is still valid (example not a dead link) and that it has not changed. We also crawl content specifically to discovery links to new URLs that have yet to be discovered. Sitemaps and RSS/Atom feeds are examples of URLs fetched primarily to discovery new links.

## Measuring bingbot success : Maximizing Crawl efficiency

Bingbot crawls billions of URLs every day. It's a hard task to do this at scale, globally, while satisfying all webmasters, web sites, content management systems, while handling site downtimes and ensuring that we aren't crawling too frequently or often. We've heard concerns that bingbot doesn't crawl frequently enough and their content isn't fresh within the index; while at the same time we've heard that bingbot crawls too often causing constraints on the websites resources. **It's an engineering problem that hasn't fully been solved yet.**

Often, the issue is in managing the frequency that bingbot needs to crawl a site to ensure new and updated content is included in the search index. Some webmasters request to have their sites crawled daily by the bingbot to ensure that Bing has the freshest version of their site in the index;  whereas the majority of webmasters would prefer to only have bingbot crawl their site when new URLs have been added or content has been updated and changed. The challenge we face, is how to model the bingbot algorithms based on both what a webmaster wants for their specific site, the frequency in which content is added or updated, and how to do this at scale.

To measure how smart our crawler is, we measure bingbot crawl efficiency. The crawl efficiency is how often we crawl and discover new and fresh content per page crawled.  Our crawl efficiency north star is to crawl an URL only when the content has been added (URL not crawled before), updated (fresh on-page context or useful outbound links) . The more we crawl duplicated, unchanged content, the lower our Crawl Efficiency metric is.

Later this month, Cheng Lu, our engineer lead for the crawler team, will continue this series of blog posts by sharing examples of how the Crawl Efficiency has improved over the last few months. I hope you are looking forward to learning more about how we improve crawl efficiency and as always, we look forward to seeing your comments and feedback.

Thanks!

Fabrice Canel  
Principal Program Manager, Webmaster Tools  
Microsoft - Bing