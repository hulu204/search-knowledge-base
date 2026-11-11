---
title: 'Not All Recall is Created Equal'
company: Tunkelang
tag: 召回
date: 2025-02-24
url: https://dtunkelang.medium.com/not-all-recall-is-created-equal-f160274dd94c
account: Tunkelang
origin: harvest3-202607
---
# Not All Recall is Created Equal

Search application developers constantly navigate tradeoffs, particularly between [precision and recall](https://queryunderstanding.com/precision-recall-and-desirability-0384a11d916b). Precision measures the fraction of retrieved results that are relevant, while recall measures the fraction of relevant documents that are retrieved. In simple terms, precision ensures “nothing but the truth,” whereas recall strives for “the whole truth.”

However, the standard definition of recall applies to retrieval, not [ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e). A common approach prioritizes recall in retrieval while relying on ranking to surface the most relevant results. After all, if a document is excluded during retrieval, ranking cannot bring it back. That said, retrieval cannot ignore precision entirely — especially when searchers can re-sort results, such as by price or popularity.

Even this approach remains too simplistic for real-world applications. Consider e-commerce: failing to retrieve relevant best sellers is far more damaging — to both searchers and the business — than failing to retrieve products that fewer searchers want to buy.

[Cumulative gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) provides a useful framework to understand this nuance. While retrieval should aim to include all relevant results, some contribute more value than others. What we often care about is not just the fraction of relevant results retrieved, but the fraction of total utility captured. This perspective aligns with ranking metrics like discounted cumulative gain (DCG), which prioritizes surfacing the most desirable results.

The interplay between recall and ranking underscores the importance of evaluating recall-oriented retrieval changes within the broader search experience. If searchers never see the additional results — or if their experience doesn’t improve — the extra computational effort is wasted.

Measuring recall in absolute terms is notoriously difficult, as it requires exhaustive labeling of relevant documents. A more practical approach is to analyze how retrieval changes impact the results searchers actually see, particularly on the first page. Query log replays can help measure these shifts offline. While such analysis doesn’t determine whether changes are beneficial, it does establish an upper bound on their potential impact.

This approach is inherently application-specific, as it ties recall to the ranking model. If ranking is weak, improved retrieval may offer little benefit — and may even degrade performance. Fortunately, ranking can be evaluated independently by retrieving the full corpus — or approximated by using highly recall-biased retrieval techniques.

Ultimately, we should not improve recall for its own sake, nor should we assume all recall is equally valuable. Every relevant result matters, but some matter more than others. We should not judge retrieval in isolation; we need to measure its contribution to the overall search experience.
