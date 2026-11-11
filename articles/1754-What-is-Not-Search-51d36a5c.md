---
title: 'What is Not Search?'
company: Tunkelang
tag: 工程相关
date: 2022-11-22
url: https://dtunkelang.medium.com/what-is-not-search-a0ded6c8c9c3
account: Tunkelang
origin: harvest3-202607
---
# What is Not Search?

When all you have is a hammer, everything looks like a nail. Search is [unquestionably my hammer](https://www.linkedin.com/in/dtunkelang/), so it’s easy for me to frame everything as a search problem. After all, doesn’t a problem imply a ***search*** for a solution?

But seriously, a lot of problems do look like search, even if they don’t involve a search box and a ranked list of results.

[Recommender systems](https://en.wikipedia.org/wiki/Recommender_system) often use search engines under the hood, especially for [item-based](https://en.wikipedia.org/wiki/Item-item_collaborative_filtering) recommendations where the item is the query.

[Question answering](https://queryunderstanding.com/question-answering-94984185c203) is often implemented, at least in part, using [passage retrieval](https://paperswithcode.com/task/passage-retrieval), which is… search.

And then there are organizations that use a search engine like Elastic as their primary data store — not that I’m recommending this!

But you can see how it’s easy to frame, if not all problems, then at least all information access problems as search problems.

I’d like to limit the scope of search, if only out of self-interest. After all, if everything is search, then nothing is search. Besides, not all information access problems are search problems. I’ll try to draw two lines, bounding from below and above what is ***not*** search.

### Hash Tables and Binary Trees are Not Search Engines

For those of you who don’t remember your introductory algorithms class — or never took one — a [hash table](https://en.wikipedia.org/wiki/Hash_table) is a standard implementation of the [dictionary (or associative array) abstract data type](https://en.wikipedia.org/wiki/Associative_array).

A dictionary allows you to store key-value pairs and retrieve them by key. Hash tables implement both operations efficiently. If your keys are ordered and you’d like some additional operations — like enumerating the keys in order or retrieving the key closest to one not in the dictionary —to be efficient, then you can use some kind of [binary tree](https://en.wikipedia.org/wiki/Binary_tree), or a [skip list](https://en.wikipedia.org/wiki/Skip_list).

Most developers rely on their language’s native dictionary implementation and don’t waste time sweating the details, except during [interviews](https://www.youtube.com/watch?v=gUTuESHKbXI).

And these data structures are wonderful! But they aren’t search engines. You could even question whether a [nearest-neighbor index](https://en.wikipedia.org/wiki/Nearest_neighbor_search) is a search engine, but I’d say that’s at least where things get fuzzy — especially when you start to make tradeoffs between result quality and computational costs.

I’d stipulate that a search engine has to have some notion of “best effort” rather than exact retrieval. Much of the complexity of a search engine comes from decisions made in indexing, retrieval, scoring, and ranking to optimize for searcher happiness and business metrics.

It’s true that you have to choose the initial capacity and reload factors for a hash table — and the hash function! But if all of your tradeoffs are strictly computational, it’s probably not a search problem.

### **Artificial General Intelligence (AGI) Is More Than Search**

Now let’s look at the other end of the spectrum.

[Question answering](https://queryunderstanding.com/question-answering-94984185c203) feels like a search problem. And often it is. If your question is “Where is the nearest sushi restaurant that’s open right now?”, that’s clearly a search problem. Specifically, it’s a [query understanding](https://queryunderstanding.com/) problem to represent the intent as something like “Retrieve restaurants where category equals sushi and current time is between opening time and closing time, then sort by distance from my location.”

You can also agonize over tradeoffs, such as whether to include restaurants that serve sushi but don’t specialize in it, to exclude restaurants close in 5 minutes, to include supermarkets as restaurants, etc. You’re making a best effort that goes beyond strictly computational tradeoffs.

But let’s say that you want to know which sushi restaurants were founded by the children of immigrants that came to the US through Ellis Island. That’s not a search problem, it’s a research problem! In order to answer it, you’ll need to find an appropriate collection of data stores — with no guarantee that all of the necessary information exists in available records — and then make a plan to synthesize information from them. I’d say to “[join](https://en.wikipedia.org/wiki/Join_(SQL))” them, but that doesn’t even begin to suggest the complexity of the problem.

In my view, this kind of problem is too complex to be considered a search problem. Indeed, it requires solving multiple search problems. But the real challenge is coming up with a higher-order plan. If you can do that beyond a trivial scope, I’d say you’ve achieved [artificial general intelligence (AGI)](https://en.wikipedia.org/wiki/Artificial_general_intelligence).

### Don’t Worry, There’s Still Tons Between the Lines!

So, not all problems are search problems. Not all information access problems are search problems. But tons of them are. Knowing the boundaries helps guide your choice of solutions — and consultants. So if you’re working on search, have no fear. There’s still tons to do.
