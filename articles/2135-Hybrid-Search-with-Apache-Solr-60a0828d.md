---
title: 'Hybrid Search with Apache Solr'
company: Sease
tag: 召回
date: 2023-12-12
url: https://sease.io/2023/12/hybrid-search-with-apache-solr.html
account: 
origin: harvest3-202607
---
Hello,

I am trying to construct a hybrid search query, our application has a pagination setup that users rely on to retrieve results. While the pagination works well with the edismax parser using the rows attribute, we’re experiencing an issue when using BoolQParser. The rows parameter is being overwritten by the topK parameter from the knn query.

Here’s my current query:

{!bool should=”{!edismax qf=’title\_desc’}generative ai” should=”{!knn f=title\_desc\_vector topK=20}[{{vector}}]”}

Is there a way to implement pagination with knn parser, specifically for this type of query?

Thank you for your help.

Loading...

[Reply](#comment-5776)