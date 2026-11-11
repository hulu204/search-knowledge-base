---
title: 'Effective Query Triage'
company: Tunkelang
tag: 查询理解
date: 2024-11-26
url: https://dtunkelang.medium.com/effective-query-triage-31b4e6b116a4
account: Tunkelang
origin: harvest3-202607
---
# Effective Query Triage

Search evaluation requires a variety of strategies.

Evaluating search experiments, such as [A/B tests](https://queryunderstanding.com/a-b-testing-for-search-is-different-f6b0f6f4d0f5), should focus on the size and direction of their impact.

Alerting and monitoring focus on detecting anomalies in normally stable metrics — metrics that are not supposed to make sudden, dramatic change.

Both strategies focus on aggregates. Indeed, most metrics reflect some sort of aggregation, and metrics-focused evaluation tends to involve the statistical analysis of changes in metrics, whether between different experimental treatments or over time.

In contrast, query triage starts with bad queries — individual examples of problems. The problems are like bits of sand than can be [grown into pearls](https://en.wikipedia.org/wiki/Pearl_growing). Done right, query triage uses individual bugs to motivate broader solutions.

An effective query triage process requires three elements: sourcing queries, identifying causes of failure, and scoping potential solutions. While query triage is as much an art as a science, consciously following these steps makes it possible to pursue a principled and effective process.

### Sourcing Queries

Query triage starts with identifying “bad” queries.

What makes a query bad? Usually these are queries that exhibit significant problems with precision (i.e., relevance), recall, ranking, or result diversity.

What makes a query bad should be clear and uncontroversial. If there isn’t a consensus about whether or how a query is bad, then it’s not worth arguing about it. Stick to queries that everyone agrees are bad for the same reason. And work as a team to align on how you evaluate search quality!

Where do bad queries come from? A common source is user reporting, whether from ordinary users or employees — including CEOs who email examples of bad queries to search team employees, adorned with a “[?](https://www.inc.com/bill-murphy-jr/5-years-later-jeff-bezos-just-confirmed-jeff-bezos-question-mark-method-that-scares-heck-out-of-everyone-at-amazon-heres-how-it-works.html)”.

On one hand, reported queries reflect real user complaints. On the other hand, the reporters tend to be unrepresentative of the broader user population.

An alternative is to source bad queries from query logs based on anomalous metrics (e.g., no results, low clickthrough or conversion rate). Mining bad queries this way ends to trigger a fair number of false positives, but it can be an excellent way to generate candidates that can then be vetted manually before being added to the query triage queue.

### Identifying Causes of Failure

Once we have a queue of bad queries to triage, the next step is identifying what makes them bad. At a high level, bad queries usually have problems with [precision](https://en.wikipedia.org/wiki/Precision_and_recall#Precision), [recall](https://en.wikipedia.org/wiki/Precision_and_recall#Recall), [ranking](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e), or [diversity](https://queryunderstanding.com/thoughts-on-search-result-diversity-1df54cb5bf4a). Or perhaps they have a more fundamental problem with [query understanding](https://en.wikipedia.org/wiki/Query_understanding).

This high-level characterization of the cause is a good start, but a more useful characterization is one that narrows down the problem a bit.

For example, if search returns iPhone cases for the query is “iphone 14”, we might characterize the problem as that of showing accessories when the searcher is looking for a product. Or if a search for “sweatshirts” fails to return results called “hoodies”, we might characterize the problem as a failure to return results that match a synonym of a query word.

Identifying the cause of failure is a balancing act. An overly specific cause may suggest an immediate direction to fix the problem, but it is unlikely to generalize to a meaningful class of queries. Conversely, an overly broad cause is unlikely to suggest meaningful directions to fix the problem.

A useful practice is to develop a list of causes and grow the list slowly. The ideal size depends on the search application and personal taste, but a good list probably contains on the order of 10 to 20 identified causes of failure.

### Scoping Potential Solutions

Having identified the cause of a bad query, we must decide whether, when, and how to prioritize fixing it. That depends first on the scope and severity of the problem, and then on how much of the problem is fixable.

The scope of the problem is a key factor: we are unlikely to prioritize a meaningful investment to fix a single query. But if we find a problem that affects a significant amount of traffic, we are more likely to prioritize a fix.

Another key factor is the severity of the problem. A precision failure in the top few results is more severe than a failure at the bottom of the page. A recall failure is more severe if it leads to empty result sets, or if it removes bestselling products. Measuring severity rigorously is hard, but it’s worth making a rough estimate, even if it is based on a gut feeling.

If the product of the scope and severity is significant enough to justify investing in a fix, we explore potential solutions. A solution may only be partial: for example, it may be difficult to generally solve the problem of showing accessories for product queries, but significantly easier to solve the problem of showing iPhone cases showing up for iPhone queries.

Again, scoping is a balancing act. A narrower solution will have a smaller impact, but it may be simpler, faster, and cheaper to implement. Even if a broader solution offers a higher potential return on investment, consider erring on the side of quick fixes. When in doubt, [reduce scope](https://queryunderstanding.com/reduce-scope-9c46d7632b60).

### Keep Calm and Triage On

Query triage is as much an art as a science. Still, it’s helpful to understand the process and be conscious of the tradeoffs. The most important thing is to iterate, learn, and use query triage to prioritize product development.
