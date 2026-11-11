---
title: 'Solr Document Classification – Part 1 – Indexing Time'
company: Sease
tag: 工程相关
date: 2015-07-04
url: https://sease.io/2015/07/solr-document-classification-part-1-indexing-time.html
account: 
origin: harvest3-202607
---
Hi, Alessandro, can you share some example on how to use this feature?

I never used Solr before, but today I downloaded solr-6.1.0-68 which I think already contains your modifications.

I then created a demo core:

./solr create -c demo

And also modified solr/demo/conf/solrconfig.xml file and added:

title\_t^1.5,author\_s  
 cat\_s  
 bayes

I loaded few documents:

curl <http://localhost:8984/solr/demo/update> -d '  
[  
 {“id” : “book1”,  
 “title\_t”:[“The Way of Kings”],  
 “author\_s”:”Brandon Sanderson”,  
 “cat\_s”:”fantasy”,  
 “pubyear\_i”:2010,  
 “ISBN\_s”:”978-0-7653-2635-5″  
 }  
]'

curl <http://localhost:8984/solr/demo/update> -d '  
[  
 {“id” : “book2”,  
 “title\_t”:[“The Way of Kings”],  
 “author\_s”:”Brandon Sanderson”,  
 “cat\_s”:”fantasy”,  
 “pubyear\_i”:2010,  
 “ISBN\_s”:”978-0-7653-2635-5″  
 }  
]'

curl <http://localhost:8984/solr/demo/update> -d '  
[  
 {“id” : “book3”,  
 “title\_t”:[“The Way of Kings”],  
 “author\_s”:”Brandon Sanderson”,  
 “cat\_s”:”fantasy”,  
 “pubyear\_i”:2010,  
 “ISBN\_s”:”978-0-7653-2635-5″  
 }  
]'

But what query shall I use to see the auto classification results?

Loading...

[Reply](#comment-9)