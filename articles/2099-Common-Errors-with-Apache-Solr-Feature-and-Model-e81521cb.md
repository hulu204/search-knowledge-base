---
title: 'Common Errors with Apache Solr Feature and Model Stores'
company: Sease
tag: 工程相关
date: 2021-03-08
url: https://sease.io/2021/03/common-errors-with-apache-solr-feature-stores-and-models.html
account: 
origin: harvest3-202607
---
Hi Sunit,  
I try to answer your questions.  
1. What do you mean by “to recover the core”? With the collection reload you are not losing any data and LTR remains enabled.  
2. You can find models and data in two files called \_schema\_model-store.json and \_schema\_feature-store.json. These files are usually in the \_default folder inside the configs folder. I’ve never tried it, but you can probably change these files manually and upload them to the configuration folder using zookeeper. (if you do not want to use the proper delete API).  
3. You can clean the caches by reloading the collection. I do not think there is a way to clean only the cache you like. If you want a cache to be clean at the restart you can set the autowarming parameter to 0 for that cache.

I hope this helps.  
Cheers!

Loading...

[Reply](#comment-840)