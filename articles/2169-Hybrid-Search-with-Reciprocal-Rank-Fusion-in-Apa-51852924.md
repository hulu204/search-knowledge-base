---
title: 'Hybrid Search with Reciprocal Rank Fusion in Apache Solr'
company: Sease
tag: 召回
date: 2026-03-03
url: https://sease.io/2026/03/hybrid-search-with-reciprocal-rank-fusion-in-apache-solr.html
account: 
origin: harvest3-202607
---
When using the /combined handler with combiner=true and combiner.algorithm=rrf, the response.numFound value does not match the total number of documents accessible through pagination.

The issue appears when combining:

a lexical query  
a vector knn query  
RRF ranking

The /combined handler reports:

“numFound”: 12

However:

page 1 returns 10 documents  
page 2 returns 7 additional documents

Total accessible documents: 17

This causes pagination inconsistencies in applications such as VuFind.  
Reproduction  
Request 1  
curl -X POST “http://localhost:8983/solr/biblio/combined” \  
-H “Content-Type: application/json” \  
-d ‘{  
“queries”: {  
“lexical”: {  
“lucene”: {  
“query”: “remote”  
}  
},  
“vector”: {  
“knn”: {  
“f”: “vector”,  
“topK”: 10,  
“query”: “[ … ]”  
}  
}  
},  
“limit”: 5,  
“fields”: [“id”, “text”, “score”],  
“params”: {  
“combiner”: true,  
“combiner.query”: [“lexical”, “vector”],  
“combiner.algorithm”: “rrf”,  
“combiner.rrf.k”: 60  
}  
}’  
Response  
{  
“response”: {  
“numFound”: 12,  
“start”: 0,  
“maxScore”: 0.032786883,  
“numFoundExact”: false,  
“docs”: [  
{  
“id”: “Deposita\_a49459c17b467e4644495ef17743413f”,  
“score”: 0.032786883  
},  
{  
“id”: “Deposita\_f38467af78bea565d49e46e7a78bc020”,  
“score”: 0.016129032  
},  
{  
“id”: “Deposita\_40b28c8aa65045ccf22ec5514609cf41”,  
“score”: 0.016129032  
},  
{  
“id”: “Deposita\_bcfbe2121e96c16cd7648170e6f581a1”,  
“score”: 0.015873017  
},  
{  
“id”: “Deposita\_b02ae19e94561bcdf0442c9bd5932d71”,  
“score”: 0.015873017  
}  
]  
}  
}  
Request 2  
curl -X POST “http://localhost:8983/solr/biblio/combined” \  
-H “Content-Type: application/json” \  
-d ‘{  
“queries”: {  
“lexical”: {  
“lucene”: {  
“query”: “remote”  
}  
},  
“vector”: {  
“knn”: {  
“f”: “vector”,  
“topK”: 10,  
“query”: “[ … ]”  
}  
}  
},  
“limit”: 10,  
“fields”: [“id”, “text”, “score”],  
“params”: {  
“combiner”: true,  
“combiner.query”: [“lexical”, “vector”],  
“combiner.algorithm”: “rrf”,  
“combiner.rrf.k”: 60  
}  
}’  
Response  
{  
“response”: {  
“numFound”: 12,  
“start”: 0,  
“maxScore”: 0.032786883,  
“numFoundExact”: false,  
“docs”: [  
{  
“id”: “Deposita\_a49459c17b467e4644495ef17743413f”,  
“score”: 0.032786883  
},  
{  
“id”: “Deposita\_bcfbe2121e96c16cd7648170e6f581a1”,  
“score”: 0.031024532  
},  
{  
“id”: “Deposita\_f38467af78bea565d49e46e7a78bc020”,  
“score”: 0.016129032  
},  
{  
“id”: “Deposita\_40b28c8aa65045ccf22ec5514609cf41”,  
“score”: 0.016129032  
},  
{  
“id”: “Deposita\_b02ae19e94561bcdf0442c9bd5932d71”,  
“score”: 0.015873017  
},  
{  
“id”: “Deposita\_6e3dbb471db7b6d1364095e1410dc8d6”,  
“score”: 0.015625  
},  
{  
“id”: “Deposita\_351041e6853db20b3ef4754a5d4dc18b”,  
“score”: 0.015625  
},  
{  
“id”: “Deposita\_8f1e0370a5ec12698289a186fabf9bdf”,  
“score”: 0.015384615  
},  
{  
“id”: “Deposita\_06cdd28fb957103e19328d5cc3b061d7”,  
“score”: 0.015384615  
},  
{  
“id”: “Deposita\_859ceaeaa2a0a1d2472cd15562dfe0cd”,  
“score”: 0.015151516  
}  
]  
}  
}

Loading...

[Reply](#comment-10617)