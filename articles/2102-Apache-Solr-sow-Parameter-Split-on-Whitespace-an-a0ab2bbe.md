---
title: 'Apache Solr sow Parameter (Split on Whitespace) and Multi-Field Full-Text Search'
company: Sease
tag: 查询理解
date: 2021-05-19
url: https://sease.io/2021/05/apache-solr-sow-parameter-split-on-whitespace-and-multi-field-full-text-search.html
account: 
origin: harvest3-202607
---
Hi,  
I’m trying to experiment with the sow param but am experiencing something weird.  
For my queries that are processed by Solr with sow=false, I am able to set it to true and see the results change. But for those that end up in a “term centric” search, setting sow=false is not working for me. Even if i set sow=false, I still see term centric search happening in the parsed query and no changes in the result set. Any idea why this might be happening or how I can make it work please?  
Thanks

Loading...

[Reply](#comment-2468)