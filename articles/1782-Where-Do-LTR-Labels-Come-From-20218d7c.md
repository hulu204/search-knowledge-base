---
title: 'Where Do LTR Labels Come From?'
company: Tunkelang
tag: 排序
date: 2024-08-06
url: https://dtunkelang.medium.com/where-do-ltr-labels-come-from-ee00892c74b3
account: Tunkelang
origin: harvest3-202607
---
# Where Do LTR Labels Come From?

The most common goal that my search clients express is a desire to improve their ranking. I always start by managing their expectations and helping them understand the [limitations of what they can learn from their data](https://queryunderstanding.com/learn-to-rank-learn-to-be-humble-06fef2b7c4cf). This post sketches out some challenges of obtaining labeled training data to implement machine-learned ranking, aka [learning to rank (LTR)](https://en.wikipedia.org/wiki/Learning_to_rank).

### Mining Searcher Behavior

Most search applications obtain implicitly labeled training data for ranking from [searcher behavior](https://queryunderstanding.com/evaluating-search-measuring-searcher-behavior-5f8347619eb0). Specifically, they derive positive examples from results that searchers observe and engage with, and negative examples from results that searchers observe but do not engage with.

Searcher behavior is a great source of signal, but it comes with caveats.

**The training data comes from queries entered by searchers.** Hence, it excludes labels for infrequent queries absent from the logs. The availability of labels for a query is proportional to the query’s frequency. We can see this as a bug or a feature. On one hand, we may fail to learn about an important minority of search traffic. On the other hand, a model trained on this data optimizes for the distribution of actual searcher traffic.

**The search application design affects how searchers query.** Factors from the size and placement of a search box to the details of the [autocomplete](https://queryunderstanding.com/autocomplete-69ed81bba245) implementation affect the kinds of queries that searchers end up making. Hence, training a ranking model should be in coordination with the overall search application design. Moreover, changes to the search application design can invalidate a model trained on historical behavior.

**The training data comes from results that searchers observe.** Hence, it excludes labels for results that are not retrieved or are buried deep in the results. Most labels are for results that appear on the first page. Again, we can see this as a bug or a feature. On one hand, it does not learn about results that searchers do not observe. On the other hand, a model trained on this data optimizes for reranking the first page of results. Also, changes to the retrieval strategy — such as shifting from traditional token-based retrieval to [AI-powered neural retrieval ](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b)— can invalidate a model trained on historical behavior.

**Engagement is an underspecified and imperfect signal.** When a searcher performs a query and observes a result, the decision of whether to engage with it can interpreted as a positive or negative judgment. But how do we define engagement? Clicks are frequent, but they are weak signals: they cost the searcher nothing and bring no value to the business. Conversions are stronger signals, but their sparsity makes it harder to train a model without massive amounts of data. Finally, non-engagement can be the absence of a signal rather than a negative signal.

**We must infer which results searchers observe but do not engage with.** A common heuristic is assuming that searchers observe all results ranked above the results they engage with. This heuristic assumes that searchers scan through results sequentially. A variation of this heuristic is to also assume that searchers observe the results immediately below the results they engage with. What about queries where searchers do not engage with any results? For these queries, a common heuristic is assuming that searchers observe the top-ranked results. There are other approaches, from mining historical engagement statistics to instrumenting browsers or apps. Regardless, all of these approaches are best-effort guesses.

I hope that these concerns communicate some of the nuances involved in mining searcher behavior to train a machine-learned ranking model.

### Collecting Human Judgments

An alternative or complementary strategy to obtain labeled training data for ranking is to collect [explicit human judgments](https://queryunderstanding.com/evaluating-search-using-human-judgement-fbb2eeba37d9) of query-result pairs. Explicit judgments avoid some of the challenges of implicit judgments, such as how to interpret engagement. Using explicit judgments also allows us to learn about queries and results not exposed in the search application.

However, explicit human judgments also have drawbacks.

**Human judgments are expensive and time-consuming.** The cost of collecting human judgments is, not surprisingly, proportional to the number of judgments collected. While search traffic produces millions of labels for free, a comparable set of human judgments costs many thousands of dollars and can take weeks — if not months — to collect.

**Setting up a process to collect judgments is a significant upfront cost.** Designing the human judgment task requires writing guidelines that cover the most common scenarios. The other significant upfront cost is implementing a pipeline to generate the query-result pairs to be evaluated. The pipeline can sample query logs to obtain a representative sample of search traffic, or it can even generate a synthetic query set. There is also the decision of which results to include, e.g., should evaluation focus on the top-ranked results that searchers are most like to observe? Finally, the pipeline has to capture all of the data it will need to present to evaluators.

**Evaluators are limited by their ability to empathize with searchers.** When searchers perform queries, their subsequent behavior reflects the goals their queries represent. In contrast, evaluators have to guess the searcher’s intent expressed by a query. That should be straightforward for questions of objective relevance, e.g., that a pair of sneakers matches the query “athletic shoes”. However, many queries introduce subjective elements, e.g., “fancy shirt”. Also, while searchers might choose one relevant result over another because of factors like price or quality, an evaluator who is not the searcher can only reliably evaluate relevance.

As we can see, explicit human judgments address some shortcomings of labels derived from searcher behavior but have drawbacks of their own.

### In Practice, Be Practical

I started this post by saying that, when clients express a desire to improve ranking, I start by managing their expectations. I hope the challenges enumerated above serve that purpose! Nonetheless, there are practical ways to obtain labeled data to train a ranking model.

**Before investing heavily in ranking, invest in improving retrieval.** Ranking does best with fine-grained distinctions among relevant results to optimize their order. If non-relevant results appear on the first page, invest more in retrieval and [relevance](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e), as well as in [query](https://queryunderstanding.com/introduction-c98740502103) and [content](https://medium.com/content-understanding/what-is-content-understanding-4da20e925974) understanding.

**Use human judgments for evaluation, rather than for training.** The cost of training a model using human judgments is high, and the resulting model is unlikely to capture signals beyond objective relevance. However, it is cost-effective to use human judgments for evaluating relevance: the scale and cost are much lower than those needed to train a ranking model.

**Focus on high-impact traffic.** Not all queries benefit equally from ranking improvements. Some queries may already be performing optimally, or close enough that there is no meaningful room for improvement. These can include queries that perform well (e.g., exact matches for titles or product names) and queries that perform badly because of low signal (e.g., [broad](https://queryunderstanding.com/broad-and-ambiguous-search-queries-1bbbe417dcc), [low-specificity](https://queryunderstanding.com/query-specificity-a6156f4043eb) queries). As with all software development efforts, it is important to prioritize efforts based on expected ROI.

So, the next time a junior member of your team asks you where labels come from, you do not need to trot out the old story of the label stork. Labels for LTR come from a lot of hard work, and hopefully a lot of love.
