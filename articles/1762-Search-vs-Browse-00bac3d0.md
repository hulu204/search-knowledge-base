---
title: 'Search vs. Browse'
company: Tunkelang
tag: 查询理解
date: 2023-12-01
url: https://dtunkelang.medium.com/search-vs-browse-e01538e438fb
account: Tunkelang
origin: harvest3-202607
---
# Search vs. Browse

One of the oldest distinctions in information access is between searching and browsing. Does a user initiate an information-seeking journey by typing keywords into a search box, or by browsing a category hierarchy?

### Search vs. browse is a false dichotomy.

Search vs. browse is a false dichotomy, since users employ both strategies to achieve highly overlapping goals. For example, a user looking for men’s shoes on an ecommerce site can either type the query “mens shoes” into the search box or browse through the category hierarchy.

In fact, the strategies that users employ often depend as much on application design as on their personal preferences. A larger, more prominent search box encourages search, while a more prominent link to to view the category hierarchy encourages browse. Autocomplete design can have a big impact too — particularly the decision of whether or not to present category browse pages as autocomplete suggestions. Also, some applications redirect common keyword queries to browse pages.

So we should not assume that users set out to search vs. browse.

### Focus on the user’s intent.

Instead of assuming that users have principled reasons for deciding whether to search or browse, we should focus on understanding their information-seeking intent.

We know that [multiple search queries can express the same intent](https://queryunderstanding.com/query-similarity-49dde9f78043). We can extend this idea to browse. Users who search for “mens shoes” express the same intent as those who browse to the “Men’s Shoes” category.

By recognizing the user’s underlying intent, we can not only improve the user experience, but also aggregate expressions of the same intent to make our learning from user behavior most robust.

The “bag-of-documents” model that establishes [query similarity](https://queryunderstanding.com/query-similarity-49dde9f78043) for search applies just as well to browse. In either case, we can represent an intent as the mean (or some other aggregation) of associated document vectors, and then compare the two mean vectors using cosine similarity. The bag-of-documents model takes advantage of documents being relatively large and self-contained, as well as of the ability to reduce noise through aggregation.

### Support the user’s journey.

Information-seeking needs vary in their [complexity](https://queryunderstanding.com/supporting-the-searchers-journey-when-and-how-568e9b68fe02). If a user is looking for a particular known product or document, the process should be simple and painless. In contrast, a user who needs to explore and learn about options and tradeoffs is better served by a richer experience.

Search may be a more intuitive way to looking for a particular result, but it can also be the starting point for exploration. Conversely, browsing seems synonymous with exploration, but it can also be how users follow what they believe to be the shortest path to the result they are looking for.

Supporting users’ journeys requires us to understand these journeys. The best way to achieve that understanding is to aggregate and learn from historical user behavior. Some search queries lead immediately to results, while others tend to launch a more complex series of pagination, filtering, reformulation, etc. The same holds for browse. We can use direct statistical analysis to understand frequent journeys,and then use machine learning to generalize to an understanding of infrequent journeys.

### Remember: it’s about the user, not your org.

One of the worse consequences of the sharp distinction between search and browse is that two different teams tend to be responsible for them — and sometimes those teams even compete for glory and resources. Remember: it’s not about you or your organization. It’s about helping users find what they are looking for. So make sure that your org structure, analytics, and other internal processes don’t get in the way of helping your users achieve their goals — through search, browse, or both.
