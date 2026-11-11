---
title: 'Crawler Hints Update: Cloudflare Supports IndexNow and Announces General Availability'
company: Cloudflare
tag: 工程相关
date: 2021-10-18
url: https://blog.cloudflare.com/cloudflare-now-supports-indexnow/
account: 
origin: harvest2-202607
---
[Speed & Reliability](/tag/speed-and-reliability/)

[Crawler Hints](/tag/crawler-hints/)[Product News](/tag/product-news/)[SEO](/tag/seo/)[Speed & Reliability](/tag/speed-and-reliability/)

October 18, 2021

# Crawler Hints Update: Cloudflare Supports IndexNow and Announces General Availability

![Alex Krivit](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW44Q0QQ4YF44E63CZ5V25R6.jpg&w=32&h=32&q=60&f=webp&fit=cover&position=center)![Abhi Das](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW44NQJBFB30ENKFQV69Y7S2.jpeg&w=32&h=32&q=60&f=webp&fit=cover&position=center)

[Alex Krivit](/author/alex/)Â andÂ [Abhi Das](/author/abhi/)

8 minute read

COPY URL

This post is also available in [íêµ­ì´](/ko-kr/cloudflare-now-supports-indexnow/).

![BLOG-749 Embedded Image - iQ8CFG](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW45GB054J318PCCTAMQN6M2.png&w=1200&h=675&f=webp&fit=cover&position=center)![](data:image/bmp;base64,Qk32BAAAAAAAADYAAAAoAAAACAAAAAgAAAABABgAAAAAAMAAAAATCwAAEwsAAAAAAAAAAAAAlW9Yk2xZkmlcmnFlpn9uqoZxoX5ojmxam3FbnnZlp4Z8t5uSxKqfxaqctJaHmHVloXNdqIBwu56U0Luz3svC28a8xKqeon1vpHNdroV1xaqf3MnB6NfQ4s/Gya+lp4F0o3JcrYVzxKic2MO64c3F2cK6waWbpX9xn3BZqH9supuMyK2hyq+lwKGZrouBnXdomm5WoXljrot4tJGBr4d6o3ZqmGxflW9emG1VnnZfqYNuq4NwonJhlFxMjlpKkmta)

In the midst of the [hottest summer on record](https://www.nbcnews.com/science/environment/us-just-hottest-summer-record-rcna1957), Cloudflare held its first ever [Impact Week](https://www.cloudflare.com/impact-week/). We announced a variety of products and initiatives that aim to make the Internet and our planet a better place, with a focus on environmental, social, and governance projects. Today, weâre excited to share an update on Crawler Hints, an initiative announced during Impact Week. [Crawler Hints](/crawler-hints-how-cloudflare-is-reducing-the-environmental-impact-of-web-searches/) is a service that improves the operating efficiency of approximately [45%](https://radar.cloudflare.com/) of the Internet traffic that comes from web crawlers and bots.

Crawler Hints achieves this efficiency improvement by ensuring that crawlers get information about what theyâve crawled previously and if it makes sense to crawl a website again.

Today we are excited to announce two updates for Crawler Hints:

1. **The first**: Crawler Hints now supports [IndexNow](https://www.indexnow.org/), a new protocol that allows websites to notify search engines whenever content on their website content is created, updated, or deleted. By [collaborating with Microsoft](https://blogs.bing.com/webmaster/october-2021/IndexNow-Instantly-Index-your-web-content-in-Search-Engines) and Yandex, Cloudflare can help improve the efficiency of their search engine infrastructure, customer origin servers, and the Internet at large.
2. **The second**: Crawler Hints is now generally available to all Cloudflare customers for free. Customers can benefit from these more efficient crawls with a single button click. If you want to enable Crawler Hints, you can do so in the **Cache Tab** of the Dashboard.

### What problem does Crawler Hints solve?

Crawlers help make the Internet work. Crawlers are automated services that travel the Internet looking forâ¦ well, whatever they are programmed to look for. To power experiences that rely on indexing content from across the web, search engines and similar services operate massive networks of bots that crawl the Internet to identify the content most relevant to a user query. But because content on the web is always changing, and there is no central clearinghouse for *when* these changes happen on websites, search engine crawlers have a Sisyphean task. They must continuously wander the Internet, making guesses on how frequently they should check a given site for updates to its content.

Companies that run search engines have worked hard to make the process as efficient as possible, pushing the state-of-the-art for crawl cadence and infrastructure efficiency. But there remains one clear area of waste: excessive crawl.

At Cloudflare, we see traffic from all the major search crawlers, and have spent the last year studying how often these bots revisit a page that hasn't changed since they last saw it. Every one of these visits is a waste. And, unfortunately, our observation suggests that 53% of this crawler traffic is wasted.

With Crawler Hints, we expect to make this task a bit more tractable by providing an additional heuristic to the people who run these crawlers. This will allow them to know when content has been changed or added to a site instead of relying on preferences or previous changes that might not reflect the true change cadence for a site. **Crawler Hints aims to increase the proportion of relevant crawls and limit crawls that donât find fresh content, improving customer experience and reducing the need for repeated crawls.**

Cloudflare sits in a unique position on the Internet to help give crawlers hints about when they should recrawl a site. Donât knock on a websiteâs door every 30 seconds to see if anything is new when Cloudflare can proactively tell your crawler when itâs the best time to index new or changed content. Thatâs Crawler Hints in a nutshell!

If you want to learn more about Crawler Hints, see the [original blog](/crawler-hints-how-cloudflare-is-reducing-the-environmental-impact-of-web-searches/).

### What is IndexNow?

[IndexNow](https://www.indexnow.org/) is a standard that was [written by Microsoft](https://blogs.bing.com/webmaster/october-2021/IndexNow-Instantly-Index-your-web-content-in-Search-Engines) and Yandex search engines. The standard aims to provide an efficient manner of signaling to search engines and other crawlers for when they should crawl content. Cloudflareâs Crawler Hints now supports IndexNow.

> *ââIn its simplest form, IndexNow is a simple ping so that search engines know that a URL and its content has been added, updated, or deleted, allowing search engines to quickly reflect this change in their search results.*- [www.indexnow.org](https://www.indexnow.org/)

By enabling Crawler Hints on your website, with the simple click of a button, Cloudflare will take care of signaling to these search engines when your content has changed via the IndexNow protocol. You donât need to do anything else! Â

What does this mean for search engine operators? With Crawler Hints youâll receive a near real-time, pushed feed of change events of Cloudflare websites (that have opted in). This, in turn, will dramatically improve not just the quality of your results, but also the energy efficiency of running your bots.

### Collaborating with Industry leaders

Cloudflare is in a unique position to have a [sizable portion of the Internet](https://w3techs.com/technologies/overview/proxy) proxied behind us. As a result, we are able to see trends in the way bots access web resources. That visibility allows us to be proactive about signaling which crawls are required vs. not. We are excited to work with partners to make these insights useful to our customers. Search engines are key constituents in this equation. We are happy to collaborate and share this vision of a more efficient Internet with Microsoft Bing, and Yandex. We have been testing our interaction via IndexNow with Bing and Yandex for months with some early successes. Â

This is just the beginning. Crawler Hints is a continuous process that will require working with more and more partners to improve Internet efficiency more generally. While this may take time and participation from other key parts of the industry, we are open to collaborate with any interested participant who relies on crawling to power user experiences.

> *âThe cache data from CDNs is a really valuable signal for content freshness. Cloudflare, as one of the top CDNs, is key in the adoption of IndexNow to become an industry-wide standard with a large portion of the internet actually using it. Cloudflare has built a really easy 1-click button for their users to start using it right away. Cloudflareâs mission of helping build a better Internet resonates well with why I started IndexNow i.e. to build a more efficient and effective Search.â***- ***Fabrice Canel****, Principal Program Manager***

![](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201%201%22%3E%3Crect%20width%3D%221%22%20height%3D%221%22%20fill%3D%22rgb(243%2C243%2C243)%22%2F%3E%3C%2Fsvg%3E)![BLOG-749 Embedded Image - HYWfyA](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW482R904RPA0625X6QAZ5VS.png&w=240&h=60&f=webp&fit=cover&position=center)

> *âYandex is excited to join IndexNow as part of our long-term focus on sustainability. We have been working with the Cloudflare team in early testing to incorporate their caching signals in our crawling mechanism via the IndexNow API. The results are great so far.â***- ***Maxim Zagrebin****, Head of Yandex Search***

![](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201%201%22%3E%3Crect%20width%3D%221%22%20height%3D%221%22%20fill%3D%22rgb(243%2C243%2C243)%22%2F%3E%3C%2Fsvg%3E)![BLOG-749 Embedded Image - mmC1MS](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW45C1BN0K0P17TYSMSX3ST4.png&w=240&h=68&f=webp&fit=cover&position=center)

> *"DuckDuckGo is supportive of anything that makes search more environmentally friendly and better for end users without harming privacy. We're looking forward to working with Cloudflare on this proposal."***- ***Gabriel Weinberg****, CEO and Founder***

![](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201%201%22%3E%3Crect%20width%3D%221%22%20height%3D%221%22%20fill%3D%22rgb(243%2C243%2C243)%22%2F%3E%3C%2Fsvg%3E)![BLOG-749 Embedded Image - 8XaJlS](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW45S2K1XTPWNXQYDKMHHNJY.jpg&w=221&h=62&f=webp&fit=cover&position=center)

### How do Cloudflare customers benefit?

Crawler Hints doesnât just benefit search engines. For our customers and origin owners, Crawler Hints will ensure that search engines and other bot-powered experiences will always have the freshest version of your content, translating into happier users and ultimately influencing search rankings. Crawler Hints will also mean less traffic hitting your origin, improving resource consumption. Moreover, your site performance will be improved as well: your human customers will not be competing with bots!

And for Internet users? When you interact with bot-fed experiences â which we all do every day, whether we realize it or not, like search engines or pricing tools â these will now deliver more useful results from crawled data, because Cloudflare has signaled to the owners of the bots the moment they need to update their results.

### How can I enable Crawler Hints for my website?

Crawler Hints is free to use for all Cloudflare customers and promises to revolutionize web efficiency. If youâd like to see how Crawler Hints can benefit how your website is indexed by the worlds biggest search engines, please feel free to opt-into the service:

1. Sign in to your Cloudflare Account.
2. In the dashboard, navigate to the **Cache tab.**
3. Click on the **Configuration** section.
4. Locate the Crawler Hints sign up card and enable. It's that easy.

![](data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%201%201%22%3E%3Crect%20width%3D%221%22%20height%3D%221%22%20fill%3D%22rgb(243%2C243%2C243)%22%2F%3E%3C%2Fsvg%3E)![How to enable crawler hints with one-click](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW48902VQ1JPPSHVE7PBW1A2.png&w=715&h=220&f=webp&fit=cover&position=center)

Once youâve enabled it, we will begin sending hints to search engines about when they should crawl particular parts of your website. Crawler Hints holds tremendous promise to improve the efficiency of the Internet.

### Whatâs next?

Weâre thrilled to collaborate with industry leaders Microsoft Bing, and Yandex to bring IndexNow to Crawler Hints, and to bring Crawler Hints to a wide audience in general availability. We look forward to working with additional companies who run crawlers to help make this process more efficient for the whole Internet.

![]()

Discuss Online

## Related tags

[Crawler Hints](/tag/crawler-hints/)[Product News](/tag/product-news/)[SEO](/tag/seo/)[Speed & Reliability](/tag/speed-and-reliability/)

Follow on Social Media

* ![Cloudflare](/images/placeholder__cloudflare.png)Cloudflare
* ![Alex Krivit](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW44Q0QQ4YF44E63CZ5V25R6.jpg&w=32&h=32&q=60&f=webp&fit=cover&position=center)[Alex Krivit](/author/alex/)
* ![Abhi Das](/_image?href=https%3A%2F%2Fblog.cloudflare.com%2F_emdash%2Fapi%2Fmedia%2Ffile%2F01KW44NQJBFB30ENKFQV69Y7S2.jpeg&w=32&h=32&q=60&f=webp&fit=cover&position=center)[Abhi Das](/author/abhi/)

## Subscribe to receive notifications of new posts

Email address

Weâll never share your email address.

Subscribe

Thanks for subscribing! Check your inbox to confirm.