---
title: 'The Importance of Setting the "lastmod" Tag in Your Sitemap'
company: Bing
tag: 爬虫抓取
date: 2023-02-01
url: https://blogs.bing.com/webmaster/february-2023/The-Importance-of-Setting-the-lastmod-Tag-in-Your-Sitemap
account: 
origin: harvest2-202607
---
February12023

# The Importance of Setting the "lastmod" Tag in Your Sitemap

If you're running a website, it's essential to have a [sitemap](https://sitemaps.org/) that helps search engines understand the pages it contains and when they are updated. It’s highly recommended to adopt [IndexNow](https://www.indexnow.org/)  to instantly inform search engines about latest content changes on your websites.

For XML sitemaps, one of the most critical tags that you can include in your sitemap is the "lastmod" tag. In this blog, we will discuss the significance of the "lastmod" tag and provide guidance on its proper implementation.

The "lastmod" tag is used to indicate the last time the web pages linked by the sitemaps were modified. This information is used by search engines to determine how frequently to crawl your site, and to decide which pages to index and which to leave out. The inclusion of the "lastmod" tag in your sitemap is crucial as it allows search engines to easily determine when a page was last updated. Without it, search engines may delay crawling updated content or may over-crawl your website as they cannot accurately determine if the content has been modified.

A recent study at Bing revealed that among websites with at least one URL indexed by Bing:

* 58% of hosts have at least one XML sitemap (sitemap known by Bing).
  + 84% of these sitemaps have a lastmod attribute set.
    - 79% have lastmod values correct.
    - 18% have lastmod values not correctly set.
    - 3% has lastmod values for only some of the URLs.
  + 16% of these sitemaps don’t have a lastmod attribute set.
* 42% of hosts don’t have one XML sitemap (Bing does not know it)

The most prevalent issue with incorrectly set "lastmod" values in XML sitemaps is that they are identical, as in the example provided.

```
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>http://www.example.com/</loc>
      <lastmod>2023-01-23</lastmod>     
   </url>
   <url>
      <loc>http://www.example.com/catalog?loc=vacation_jupiter</loc>
      <lastmod>2023-01-23</lastmod>
   </url>
   <url>
      <loc>http://www.example.com/catalog?loc=vacation_mars</loc>
      <lastmod>2023-01-23</lastmod>
   </url>
</urlset>
```

After consulting with webmasters, we discovered that the date on most XML sitemaps was set to the date of generation of the sitemap, rather than the date of content modification.

As a result, we have made improvements to sitemap.org for improved clarity by incorporating the following statement:

*Note that the date must be set to the date the linked page was last modified, not when the sitemap is generated.*  
  
It is possible for sitemaps to have the same dates, as websites may publish multiple pages on the same day without updating them. However, if we observe that the dates are consistently set to the current date, we will suspect the validity of those dates and may disregard them.

### **How to set the lastmod?**

To set the "lastmod" tag in your sitemap, you'll need to include it in the <url> tag for each page that you want to include in your sitemap. This date should be in [W3C Datetime format](http://www.w3.org/TR/NOTE-datetime). Most common format used are the ones specifying the date YYYY-MM-DD (example 2022-12-28) and the ones specifying date and time YYYY-MM-DDThh:mm:ssTZD  (example 2022-12-19T17:15:30+01:00) , and it should be set to the date that the page was last modified.  
  
Also, the "lastmod" tag should be regularly updated when the page is updated for search engines to understand the frequency of updates. To ensure this, it is recommended to generate your sitemaps at least daily.

### **How Bing uses lastmod tag?**

As a result of this study, we are revamping our crawl scheduling stack to better utilize the information provided by the "lastmod" tag in sitemaps. This will enhance our crawl efficiency by reducing unnecessary crawling of unchanged content and prioritizing recently updated content. We have already begun implementing these changes on a limited scale and plan to fully roll them out by June.

### **What’s about sitemap changefreq and priority tags?**

Our analysis revealed that the majority of "changefreq" and "priority" tags in sitemaps are not set correctly. They are often assigned the same values across a sitemap and do not accurately reflect the likelihood of a page being updated or the relative importance of a URL in comparison to others. As a result, Bing largely disregards these fields.

### **Conclusion**

In conclusion, the lastmod tag is an especially important signal of your website's sitemap. By including it and setting the correct value, you can help search engines crawl your site more efficiently, improve your pages' indexing, and increase your site's visibility in search engine results pages. Make sure to set and keep the lastmod tag updated in your sitemap to keep your website up to date and visible to search engines.  
  
Fabrice Canel  
Principal Product Manager  
Microsoft Bing