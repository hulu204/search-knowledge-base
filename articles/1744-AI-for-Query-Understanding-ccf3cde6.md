---
title: 'AI for Query Understanding'
company: Tunkelang
tag: 查询理解
date: 2021-07-07
url: https://dtunkelang.medium.com/ai-for-query-understanding-d8c073095fff
account: Tunkelang
origin: harvest3-202607
---
# AI for Query Understanding

In the past decade, the incredible progress in [word embeddings](https://en.wikipedia.org/wiki/Word_embedding) and [deep learning](https://en.wikipedia.org/wiki/Deep_learning) has fueled an interest in [neural information retrieval](https://www.microsoft.com/en-us/research/uploads/prod/2017/06/fntir2018-neuralir-mitra.pdf). An increasing number of folks believe that it’s time to retire the traditional [inverted indexes](https://en.wikipedia.org/wiki/Inverted_index) (aka posting lists) that search engines use for retrieval and ranking.

In its place, they advocate a model where search engines use neural networks to represent documents and queries as vectors, and then use [nearest neighbor search](https://en.wikipedia.org/wiki/Nearest_neighbor_search) — or more sophisticated ranking models — to retrieve and rank results.

This revolutionary approach is tempting, but — in my view — misdirected. As I argue below — and as you can learn how to implement [here](https://queryunderstanding.com/using-ai-to-understand-search-intent-1fef055e901f) — the right place to focus AI efforts is query understanding.

**The traditional information retrieval approach is limiting.**

The neural retrieval approach is tempting, because it addresses some of the most frustrating limitations of the traditional information retrieval in general, and inverted indexes in particular.

The traditional retrieval and ranking approach uses a variety of factors, such as [BM25](https://en.wikipedia.org/wiki/Okapi_BM25), to ensure [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision). These factors tend to be highly sensitive to individual keywords. For example, a search for “iphone cases” typically returns slightly different results than a search for “iphone case” — even though the search intents are almost certainly identical.

Similarly, traditional [query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) methods, such as [stemming](https://queryunderstanding.com/stemming-and-lemmatization-6c086742fe45) and [synonyms](https://queryunderstanding.com/real-talk-about-synonyms-and-search-bb5cf41a8741), as well as [query relaxation](https://queryunderstanding.com/query-relaxation-342bc37ad425), tend to take the query too literally because they focus on keywords rather than the overall query intent. As a result, they can make egregious errors, such as returning iPhone cases when someone performs a search for a “case of apples”.

Embeddings and deep learning allow us to holistically represent and target intent, rather than relying on a reductionist approach based on keywords.

But applying this representation directly to ranking and retrieval skips a critical step: query understanding.

**The best place to address query intent is query understanding.**

[Query understanding](https://queryunderstanding.com/introduction-c98740502103) is what happens before the search engine retrieves and ranks results: it comprises the searcher’s process of expressing an intent as a query and the search engine’s process of determining that intent. Query understanding involves a combination of [holistic and reductionist](https://queryunderstanding.com/query-understanding-divided-into-three-parts-d9cbc81a5d09) steps, the holistic steps considering the query as a whole, and the reductist steps breaking the query down into separately analyable parts.

Holistic query understanding with embeddings and deep learning is a great way to look beyond keywords and recognize [queries that represent similar or equivalent intent](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f). Before retrieving and ranking results, query understanding can map the query to a representation that canonicalizes the class of equivalent queries. Doing so often allows the search engine to aggregate behavioral signals, such as clicks and purchases, that would otherwise be fragmented among the various expressions of a given intent. Holistic query understanding can also classify the query into a topic or product [taxonomy](https://queryunderstanding.com/taxonomies-and-ontologies-8e4812a79cb2).

Reductionist query understanding can also be valuable. In particular, [recognizing entities](https://queryunderstanding.com/entity-recognition-763cae840a20) in queries leads to a richer representation of the query than treating the query as a sequence of keywords. Not only can entity recognition can drive [query scoping](https://queryunderstanding.com/query-scoping-ed61b5ec8753) to improve precision (e.g., recognizing whether “apple” is a brand or product type), but it can also provide context to intelligently [expand](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) or [relax](https://queryunderstanding.com/query-relaxation-342bc37ad425) entities to increase recall (so that we don’t confuse iPhone cases with cases of apples).

**Use AI intelligently.**

Embeddings and neural networks are powerful tools, and we are only beginning to realize their potential to revolutionize search. But search is more than retrieval and ranking. Search starts with users expressing their intent through queries. Hence, the highest-leverage way to improve search is to through better query understanding.

So let’s focus our AI efforts on this critical part of the search stack. By not taking queries so literally, we will literally revolutionize search!
