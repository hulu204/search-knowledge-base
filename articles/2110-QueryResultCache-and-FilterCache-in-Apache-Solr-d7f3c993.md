---
title: 'QueryResultCache and FilterCache in Apache Solr'
company: Sease
tag: 工程相关
date: 2022-04-14
url: https://sease.io/2022/04/queryresultcache-and-filtercache-in-apache-solr.html
account: 
origin: harvest3-202607
---
Hi Dominique,  
if you look at the source code of the cache key, the `start` and `rows` parameters are not discriminant.  
The values `start` and `rows` impact the number of elements stored in the cache in the following way.  
Given `queryResultWindowSize=20` we have:  
start=0, rows=10, the cache keeps the first 20 results  
start=10, rows=10, the cache keeps the first 20 results  
start=20, rows=10, the cache keeps the first 40 results  
That being said, there is another parameter `queryResultMaxDocsCached` so, if `start + rows > queryResultMaxDocsCached`, the cache won’t be used.

Loading...

[Reply](#comment-3016)