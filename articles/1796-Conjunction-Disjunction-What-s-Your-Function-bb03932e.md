---
title: 'Conjunction, Disjunction, What’s Your Function?'
company: Tunkelang
tag: 召回
date: 2025-01-06
url: https://dtunkelang.medium.com/conjunction-disjunction-whats-your-function-cd68bd0400a0
account: Tunkelang
origin: harvest3-202607
---
# **Conjunction, Disjunction, What’s Your Function?**

Like many folks of my generation, I grew up on [Schoolhouse Rock](https://www.youtube.com/@schoolhouserock3860), a series of animated educational shorts that aired during Saturday morning cartoons. One of its most memorable episodes was “[Conjunction Junction](https://www.youtube.com/watch?v=LjdCFat9rjI)”:

> Conjunction Junction, what’s your function?
Hooking up words and phrases and clauses.
Conjunction Junction, how’s that function?
I got three favorite cars
That get most of my job done.
Conjunction Junction, what’s their function?
I got “and”, “but”, and “or”,
They’ll get you pretty far.

Much of what search applications do is “hooking up words and phrases and clauses,” and conjunctions have always played a key role in doing so.

The earliest search applications implemented [Boolean retrieval](https://en.wikipedia.org/wiki/Boolean_model_of_information_retrieval). Searchers constructed queries using AND and OR operators, also known as [conjunction](https://en.wikipedia.org/wiki/Logical_conjunction) and [disjunction](https://en.wikipedia.org/wiki/Logical_disjunction). Some systems supported a NOT operator for negation. As the song goes, these three operators get most of the job done.

Putting NOT aside for the moment, AND and OR are quite a power couple.

[Query expansion](https://queryunderstanding.com/query-expansion-2d68d47cf9c8) [rewrites](https://queryunderstanding.com/query-rewriting-an-overview-d7916eb94b83) a query as an AND of ORs, e.g., ip lawyer -> (ip OR “intellectual property”) AND (lawyer OR attorney). Search applications do not necessarily enforce an AND across all query terms, but this is a common and sensible default, at least for short queries.

[Faceted search](https://queryunderstanding.com/faceted-search-7d053cc4fada) does something similar, performing an AND across facets and an OR within a facet, e.g., Brand: (HP OR Dell) AND Operating System: (Windows 11 OR Chrome OS). There’s no hard and fast rule that says that facets should be combined this way, but it is hard to imagine brands being combined with AND (since most products have only a single brand) or brand being combined with operating system using OR (e.g., Brand: Dell OR Operating System: Windows 11). However, there are cases where it does make sense to combine multiple values within a single facet using AND, e.g., Topic: (Machine Learning AND Information Retrieval), Features: (Water Resistance AND Bluetooth Connectivity). Of course, these cases involve facets from which it is common to assign multiple values, and such facets are something of an exception.

Interestingly, people often struggle with conjuntions in natural language search. The request “show me red and blue shirts” means “show me shirts that are red OR blue”, not “red AND blue”. Indeed, it’s not clear that a shirt that is both red and blue is a better result than one that is just one of the two colors. How confusing that people say AND when they mean OR!

And let’s not forget NOT. Negation is a potentially powerful way to filter results, e.g., phone NOT iphone. However, it is very difficult to implement negation in a way that delivers intuitive results. For example, data quality issues could lead a result containing “i phone” which is technically NOT “iphone” but is probably the kind of result the searcher intended to exclude. Synonyms, abbreviations, and other variations in vocabulary lead to similar issues. While many search applications implement a negation operator, they rarely encourage searchers to use it.

All of this discussion is about [retrieval](https://queryunderstanding.com/ranking-vs-relevance-ba672c79625e) — specifically retrieval for traditional lexical search as opposed to [AI-powered dense retrieval](https://queryunderstanding.com/ai-powered-search-embedding-based-retrieval-and-retrieval-augmented-generation-rag-cabeaba26a8b). Some folks believe this approach to retrieval is obsolete in the face of modern ranking approaches, and that we should just think of retrieval as the first stage in a ranking pipeline. I disagree, but I understand how modern approaches make it difficult to make retrieval transparent and intuitive to searchers.

Regardless, I hope this trip down memory lane serves as a reminder that the basic grammar and set operations many of us learned in grade school are still relevant in our modern age.

To wrap it up:

> Conjunction Junction, what’s your function?
Hooking up cars and making ’em function.
Conjunction Junction, how’s that function?
I like tying up words and phrases and clauses.
Conjunction Junction, watch that function.
I’m going to get you there if you’re very careful.
