---
title: 'Exploring Solr Internals : The Lucene Inverted Index'
company: Sease
tag: 索引构建
date: 2015-07-26
url: https://sease.io/2015/07/exploring-solr-internals-lucene.html
account: 
origin: harvest3-202607
---
Thanks for your quick reply Alessandro Benedetti.

My business problem is “get all the distinct values/terms of a field (type: keyword)”.  
As you suggested, I can do with elasticsearch terms aggregation only when the field has doc\_values enabled. Somehow, I got the doc\_values enabled and I’m trying to do term aggregation to solve same business problem. I got the list of unique values for my field. But, now the issue is, the elasticsearch is going through all the documents to fetch the list of unique values present in that index (confirmed by evaluating the response below) . But i have only around 3000 unique values for that field

“hits”: {  
“total”: 14041450,  
“max\_score”: 0.0,  
“hits”: []  
}

Is there a way that I get the list of unique values of a field with hits limited to the number of unique values? (Because there will be lot of documents being added up on daily basis as the terms of the field could grow rapidly, in that case i do not want elasticsearch to go through all the documents just to get the list of unique values of the field)

Loading...