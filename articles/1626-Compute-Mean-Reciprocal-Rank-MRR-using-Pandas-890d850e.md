---
title: 'Compute Mean Reciprocal Rank (MRR) using Pandas'
company: softwaredoug
tag: 评测
date: 2021-04-21
url: https://softwaredoug.com/blog/2021/04/21/compute-mrr-using-pandas
account: 
origin: harvest3-202607
---
If we’re building a search app, we often want to ask ‘How good is its relevance?’ As users will try millions of unique search queries, we can’t just try 2-3 searches, and get a gut feeling! We need to put a robust number on search quality. As you experiment, you’ll want to compute such a statistic over thousands of queries. For this reason, I want to look at how Pandas can be used to rapidly compute one such statistic: **Mean Reciprocal Rank**.

[Mean Reciprocal Rank](https://en.wikipedia.org/wiki/Mean_reciprocal_rank) or MRR measures how far down the ranking the first relevant document is. If MRR is close to 1, it means relevant results are close to the top of search results - what we want! Lower MRRs indicate poorer search quality, with the right answer farther down in the search results.

As MRR really just cares about the ranking of the first relevant document, it’s usually used when we have ‘one relevant result’ to our query. This occurs in applications such as question answering, where one result is labeled relevant. Such as in the two questions below:

| Query | Relevant Document |
| --- | --- |
| How far away is Mars? | NASA Mars Website |
| Who is PM of Canada? | Justin Trudeau Wikipedia |

Each question here has one labeled, relevant answer. In question answering, everything else is presumed irrelevant.

If we search for “How far away is Mars?” and our result listing is the following, note how we know the rank of the correct answer. We can then compute a *reciprocal rank* or just `1 / rank` in the examples below

| Query | Relevant Document | rank | recip. rank |
| --- | --- | --- | --- |
| How far away is Mars? | Mars, God of War | 1 |  |
|  | NASA Mars Website | 2 | 1/2 |
|  |  |  |  |

Then, similarly, we search for “Who is PM of Canada?” we get back:

| Query | Relevant Document | rank | recip. rank |
| --- | --- | --- | --- |
| Who is PM of Canada? | Joe Biden’s Website | 1 |  |
|  | Conor Landry for PM! | 2 |  |
|  | Justin Trudeau Wikipedia | 3 | 1/3 |

We see in the tables above the reciprocal rank of each query’s first relevant search result - in other words `1 / rank` of that result. The mean of these two reciprocal ranks is `1/2 + 1/3 == 0.4167`. This is the **mean** *reciprocal rank* or *MRR*. An MRR close to 1 means relevant results tend to be towards the top of relevance ranking.

Of course, we do this over possibly many thousands of queries! Which is where Pandas comes in.

## An MRR walk-thru in MSMarco with Pandas

MSMarco is a question-answering dataset used in competitions and to prototype new/interesting ideas. You can find the datasets [here](https://microsoft.github.io/msmarco/).

For exploring MRR, for now we really just care about one file for MSMarco, the [qrels](https://trec.nist.gov/data/qrels_eng/). This holds the [judgment list](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list) used as the ground truth of MSMarco. A judgment list, is just a term of art for the documents labeled as relevant/irrelevant for each query. How we arrive at what’s relevant / irrelevant is itself a complicated topic, and I recommend my [previous article](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list) if you’re curious.

But for now, let’s just dive into MSMarco’s data, if we load the qrels file, we can inspect its contents:

```
judgments = pd.read_csv('data/msmarco-doctrain-qrels.tsv.gz', delimiter=' ', header=None)\
              .rename(columns={0:'qid', 1:'iteration', 2: 'docid', 3: 'relevancy grade'})[['qid', 'docid', 'relevancy grade']]
judgments.head(20)
```

Output:

|  | qid | docid | relevancy grade |
| --- | --- | --- | --- |
| 0 | 3 | D312959 | 1 |
| 1 | 5 | D140227 | 1 |
| 2 | 12 | D213890 | 1 |
| 3 | 15 | D1033338 | 1 |
| 4 | 16 | D508131 | 1 |
| 5 | 18 | D2286511 | 1 |
| 6 | 24 | D69114 | 1 |
| 7 | 26 | D1350520 | 1 |
| 8 | 31 | D304123 | 1 |
| 9 | 42 | D1439360 | 1 |
| 10 | 48 | D322379 | 1 |
| 11 | 51 | D920249 | 1 |
| 12 | 54 | D361377 | 1 |
| 13 | 55 | D1366317 | 1 |
| 14 | 60 | D246777 | 1 |
| 15 | 63 | D1450821 | 1 |
| 16 | 67 | D494640 | 1 |
| 17 | 68 | D1896896 | 1 |
| 18 | 69 | D2155744 | 1 |
| 19 | 70 | D2845225 | 1 |

Notice how each unique query (the `qid`) has exactly one document labeled as relevant. A search solution would be evaluated on how well it gets that one document (in this case an answer to a question) towards the top of the ranking. This is what we want our MRR metric to help measure.

So we might implement some kind of search system, and issue a couple of queries. It returns the following ranked search results:

```
search_results = pd.DataFrame([
                        # Results for query id 1185869
                        # 'How far away is Mars?''
                        {'rank': 1,
                         'docid': 'D2008201', 
                         'qid': 1185869},
                        {'rank': 2,
                         'docid': 'D59219',
                         'qid': 1185869},
                         
                        # Results for query id 5
                        # 'Who is PM of Canada?''
                        {'rank': 1,
                         'docid': 'D494640', 
                         'qid': 5},
                        {'rank': 2,
                         'docid': 'D123456', 
                         'qid': 5},
                        {'rank': 3,
                         'docid': 'D140227', 
                         'qid': 5},
                       
                       ])
search_results
```

Output:

|  | rank | docid | qid |
| --- | --- | --- | --- |
| 0 | 1 | D2008201 | 1185869 |
| 1 | 2 | D59219 | 1185869 |
| 2 | 1 | D494640 | 5 |
| 3 | 2 | D123456 | 5 |
| 4 | 3 | D140227 | 5 |

Our first step would be to label each search result as relevant or not from our judgments. We do this by merging the judgments into the search results. Effectively this is just a left join of judgments into our search results on the query, doc id. Any correct answers are labeled a 1, everything else we force to 0 (assumed irrelevant):

```
labeled_search_results = search_results.merge(judgments, how='left', on=['qid', 'docid']).fillna(0)
labeled_search_results
```

Output:

|  | rank | docid | qid | relevancy grade |
| --- | --- | --- | --- | --- |
| 0 | 1 | D2008201 | 1185869 | 0 |
| 1 | 2 | D59219 | 1185869 | 1 |
| 2 | 1 | D494640 | 5 | 0 |
| 3 | 2 | D123456 | 5 | 0 |
| 4 | 3 | D140227 | 5 | 1 |

In the next bit of code, we inspect the best rank for each relevancy grade. In other words: what’s the lowest rank that `relevancy grade == 1` occurs? Notice how in the output, we have a breakdown of the best rank (the min rank) each relevancy grade was seen at. We see, for example, qid 5, the best rank for relevancy grade of 1 is rank 3.

```
relevances_rank = labeled_search_results.groupby(['qid', 'relevancy grade'])['rank'].min()

relevances_rank
```

Output:

```
qid      relevancy grade
5        0.0                1
         1.0                3
1185869  0.0                1
         1.0                2
Name: rank, dtype: int64
```

Of course, for reciprocal rank calculation, we only care about where relevant results ended up in the listing. Next we filter to just the relevancy grades of 1s for each query:

```
ranks = relevances_rank.loc[:, 1]
ranks
```

Output:

```
qid
5          3
1185869    2
Name: rank, dtype: int64
```

These are the ranks of each relevant document per query! We can now compute the reciprocal rank for each query.

```
reciprocal_ranks = 1 / (ranks)
reciprocal_ranks
```

Output:

```
qid
5          0.333333
1185869    0.500000
Name: rank, dtype: float64
```

Finally we arrive at the mean of each query’s reciprocal rank, by, you guessed it, taking the mean.

```
reciprocal_ranks.mean()
```

0.41666666666666663

And that is oooone mean reciprocal rank! :)

## That’s all folks

This is just a dumb one-off post, mostly to help me remember how I arrived at some code ;). Please do [get in touch](http://linkedin.com/in/softwaredoug) if you noticed any mistakes or have thought (or want to join me and my fellow relevance engineers at Shopify!).

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---