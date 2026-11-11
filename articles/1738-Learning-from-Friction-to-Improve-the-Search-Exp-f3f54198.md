---
title: 'Learning from Friction to Improve the Search Experience'
company: Tunkelang
tag: 评测
date: 2020-09-10
url: https://dtunkelang.medium.com/learning-from-friction-to-improve-the-search-experience-8937c71ec97a
account: Tunkelang
origin: harvest3-202607
---
# Learning from Friction to Improve the Search Experience

When we design search applications, we aspire to make the user experience frictionless. A search engine should “just work”, enabling searchers to easily express their intent and responding with exactly the results searchers need.

Unfortunately, our search applications tend to fall short of our aspirations.

Most search analytics focuses on measuring friction in the search experience. For example, the [mean reciprocal rank (MRR)](https://en.wikipedia.org/wiki/Mean_reciprocal_rank) of clicks tells us how far users have to scan down the results to find what they want. Search abandonment rate reflects how often users don’t find what they want at all. These and other metrics reflect different kinds of friction that searchers experience.

Much of the work we do in developing search applications involves reducing this friction. But we can do more with friction than strive to minimize it.

Friction is a valuable signal. It highlights the gaps between searcher intent and experience. By recognizing and analyzing friction, we can improve the search experience. Friction is feedback that we should learn from.

Here are a few examples of how we can learn from friction:

- **Analyze queries that lead to long sessions.** Not all search sessions will be quick — after all, search tasks are more complex than others. But long sessions often indicate a need to better [support the searcher’s journey](https://medium.com/@dtunkelang/supporting-the-searchers-journey-when-and-how-568e9b68fe02). For example, if searchers are paginating deeply into result sets or manually reformulating their initial search queries, there is probably room to improve the organization of search results and options for refining them.

- **Analyze differences between impressions and engagement.** When search “just works”, searchers engage with (click on, purchase, etc) results that they see. Conversely, differences between search results that receive impressions and results that drive engagement suggest opportunities to improve search. Analyzing differences in distributions, such as category, price, document length, can reveal opportunities to make search results better reflect searcher needs.

- **Analyze differences between query and session engagement.** Most searchers don’t change their minds about what they want during a session. So, if users end up engaging with results during a session that they did not engage with directly after their queries, that usually tells us that the search engine did not immediately show them what they were looking for.

All of these analyses represent variations on the same theme: when searchers are working hard to find what they want, that often means that the search engine isn’t working hard enough — or smart enough.

No search engine can deliver a perfect experience that is frictionless for all users. Indeed, not all users want a frictionless experience — sometimes, friction is a necessary part of exploration.

But for the most part, friction is unpleasant for searchers and represents an opportunity for improvement. When we develop search applications, it’s our job to detect this friction, learn from it, and translate these learnings into a better experience for searchers.
