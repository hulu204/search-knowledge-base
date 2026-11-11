---
title: 'Seasonality'
company: Tunkelang
tag: 时效性
date: 2017-11-06
url: https://queryunderstanding.com/seasonality-5eef79d8bf1c
account: 
origin: harvest3-202607
---
# Seasonality

[![Daniel Tunkelang](https://miro.medium.com/v2/resize:fill:64:64/0*-Mm-tInUos0gj_X8.jpg)](https://dtunkelang.medium.com/?source=post_page---byline--5eef79d8bf1c---------------------------------------)

[Daniel Tunkelang](https://dtunkelang.medium.com/?source=post_page---byline--5eef79d8bf1c---------------------------------------)

3 min read

·

Oct 30, 2017

--

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D5eef79d8bf1c&operation=register&redirect=https%3A%2F%2Fqueryunderstanding.com%2Fseasonality-5eef79d8bf1c&source=---header_actions--5eef79d8bf1c---------------------post_audio_button------------------)

Share

Whether it’s the time of year or the time of day, the time when someone performs a search sometimes help us determine the searcher’s intent. As with [location](/geographical-context-77ce4c773dc7), it’s important to determine which queries are time-sensitive and then determine how temporal context can help us understanding them.

**Query Seasonality**

Search behavior often exhibits [seasonality](https://en.wikipedia.org/wiki/Seasonality). Certain queries are more frequent at particular times of year, i.e., their probability is time-sensitive. For example, many people search for flowers in the week leading up to Valentine’s Day.

Sometimes, it’s not the query probability but the intent that is time-sensitive. For example, someone searching for jackets on a clothing site in the summer probably has different intent than someone making the same search in winter. In other cases, the time of day matters: for example, a search for local restaurants at noon on a weekday often reflects a different intent than the same search on a Saturday evening.

When queries exhibit seasonality, temporal context helps us better estimate their probability — which is particularly useful for [autocomplete](/autocomplete-69ed81bba245). On a site that sells clothing, for example, a *c* in late October would be likely to complete to *costume*, while in mid-December it more likely completes to *christmas.*

**Determining Seasonality**

How do we determine that a query is seasonal? For frequent queries, we can measure the [variance](https://en.wikipedia.org/wiki/Variance) of when queries occur over time and compare it to that of queries performed throughout the year. We can apply the same approach for queries that are sensitive to particular times of day, but for simplicity we’ll focus on time of year.

The [variance of a random variable with uniform distribution](https://en.wikibooks.org/wiki/Statistics/Distributions/Uniform) between the real values a and b is 1/12 (b-a)². If we uses years as units, then a query occurring uniformly throughout the year has a variance of 1/12.

In contrast, a query that occurs only on a single day of the year (uniformly throughout that day) has a variance of (1/365)² \* (1/12) — over 100,000 times lower than that of a query occurring uniformly throughout the year. In general, the variance correlates negatively to seasonality.

**Caveats**

A few caveats are in order about computing seasonality this way:

* It’s important to normalize based on overall query frequency throughout the year, since overall query traffic may exhibit its own seasonality.
* The year ends where it begins, but our formula for variance treats December 31 as being a year from January 1. A heuristic to mostly avoid this problem is to compute variance two ways, first starting the year on January 1, and then starting the year on July 1, and using whichever yields to lower variance.
* This approach only works for frequent queries. For infrequent queries, the variance is essentially noise. We would need to use a more sophisticated approach to determine that a class of query exhibits seasonality, or a machine learning approach that treats the query probability as a regression problem.

Finally, a query may have seasonal intent even though the query itself isn’t seasonal, as in the example of jackets for summer and winter. In those cases, we need to determine which documents exhibit seasonality (using the above variance approach for documents rather than queries), and then determine whether document engagement for a query correlates to time of year or day.

**Summary**

Context often helps us understand queries. In the last three posts, we’ve addressed [session context](/session-context-4af0a355c94a), [location](/geographical-context-77ce4c773dc7), and seasonality. Seasonality is especially useful for predicting query probability and thus improving autocomplete. But remember that context is a secondary signal — the searcher’s query will always be the primary signal for establishing intent.

**Previous:** [**Location as Context**](/geographical-context-77ce4c773dc7)

**Next:** [**Personalization**](/personalization-3ed715e05ef)