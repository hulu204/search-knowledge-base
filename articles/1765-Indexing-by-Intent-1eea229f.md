---
title: 'Indexing by Intent'
company: Tunkelang
tag: 索引构建
date: 2023-12-18
url: https://dtunkelang.medium.com/indexing-by-intent-6645ed26d033
account: Tunkelang
origin: harvest3-202607
---
# Indexing by Intent

Search developers mostly focus on mapping queries to results. This perspective is natural, insofar as search starts with the user formulating a query and (hopefully) ends with finding a result that satisfies the query. But sometimes it is useful to invert this perspective, mapping results to queries that represent search intents.

In effect, we are just flipping a [duality](https://queryunderstanding.com/exploring-search-intent-as-a-duality-c0c260500599): instead of modeling each query as a bag of documents, we model each document as a bag of queries. We can then ask questions like which queries that match the document can actually retrieve it (which turns out to be a [useful recall metric](https://queryunderstanding.com/using-retrievability-to-measure-recall-b991eb241ded)!).

Modeling documents as bags of queries is an old idea. In 2010, [Jeremy Pickens](https://www.linkedin.com/in/jeremy-pickens-4b81bb5/), [Matthew Cooper](https://www.linkedin.com/in/mlcooper/), and [Gene Golovchinsky](https://www.linkedin.com/pulse/20130819070021-50510-remembering-gene/) proposed a “[reverted index](https://dl.acm.org/doi/10.1145/1871437.1871571)” similar to what I am proposing here. They in turn drew inspiration fro, [Leif Azzopardi](https://www.strath.ac.uk/staff/azzopardileifdr/) and [Vishwa Vinay](https://www.linkedin.com/in/vishwa-vinay-b1b6881/)’s 2008 work on [accessibility in information retrieval](https://thenoisychannel.com/2008/04/22/accessibility-in-information-retrieval/), which borrowed the concept of “accessibility” from land use and transportation planning. After all, search is a journey!

But sometimes an old idea needs new life. Here are some direct ways to apply the bag-of-queries model:

- **Measuring recall.** The idea is to take a representative sample of documents, find queries for which the result is relevant, and see how often those queries retrieve the documents. More details in this post on “[Using Retrievability to Measure Recall](https://queryunderstanding.com/using-retrievability-to-measure-recall-b991eb241ded)”.

- **Detecting spam / abuse.** A document should be about something, and the bag-of-queries model gives us a searcher-centric representation of that aboutness. If the queries in the bag are spread out over too much of the intent space, that suggest that the document is trying to be too many things to too many people — which is usually a sign of spam or abuse.

- **Supply / demand alignment.** In ecommerce, content, and talent marketplaces, suppliers often struggle to find their place in the competitive landscape. Modeling their offerings as bags of queries helps them understand what demand they are targeting, which in turn can help them pursue niches where demand exceeds supply.

I expect that these applications only scrape the surface of what we can do with the bag-of-queries model. An important nuance is that [queries are not the same as search intents](https://queryunderstanding.com/search-queries-and-search-intent-1dec79ad155f). It is likely that, even if a document maps to a single intent, that intent will be expressed by a variety of different queries.

Regardless, this duality serves as a reminder that, just as queries target results, results effectively target queries. Search is about connecting intents to satisfaction of those intents, and connection is a two-way street.
