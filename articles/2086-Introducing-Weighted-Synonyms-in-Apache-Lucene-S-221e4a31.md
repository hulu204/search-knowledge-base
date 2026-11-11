---
title: 'Introducing Weighted Synonyms in Apache Lucene/Solr'
company: Sease
tag: 查询理解
date: 2020-03-02
url: https://sease.io/2020/03/introducing-weighted-synonyms-in-apache-lucene.html
account: 
origin: harvest3-202607
---
Hi Alessandro,

Here’s my debug output and some additional info:

I’m using StandardAnalyzer for search, and my SynonymGraphFilter has default configuration as in your example.

Query: +Synonym(morphology\_term\_original\_name\_key:neoplasm^0.7 morphology\_term\_original\_name\_key:tumor^0.8 morphology\_term\_original\_name\_key:tumour^0.6)

1.0 = weight(Synonym(morphology\_term\_original\_name:neoplasm^0.7 morphology\_term\_original\_name:tumor^0.8 morphology\_term\_original\_name:tumour^0.6) in 0) [BooleanSimilarity], result of:  
1.0 = score(BooleanWeight), computed from:  
1.0 = boost, query boost

If I use the BM25Similarity, the printout is as follows:

0.75188845 = weight(Synonym(morphology\_term\_original\_name:neoplasm^0.7 morphology\_term\_original\_name:tumor^0.8 morphology\_term\_original\_name:tumour^0.6) in 0) [BM25Similarity], result of:  
0.75188845 = score(freq=0.8), computed as boost \* idf \* tf from:  
1.3862944 = idf, computed as log(1 + (N – n + 0.5) / (n + 0.5)) from:  
1 = n, number of documents containing term  
5 = N, total number of documents with field  
0.5423729 = tf, computed as freq / (freq + k1 \* (1 – b + b \* dl / avgdl)) from:  
0.8 = termFreq=0.8  
1.2 = k1, term saturation parameter  
0.75 = b, length normalization parameter  
1.0 = dl, length of field  
2.4 = avgdl, average length of field

Loading...