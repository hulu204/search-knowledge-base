---
title: 'Golden search datasets are anything but'
company: softwaredoug
tag: 搜索
date: 2026-10-26
url: https://softwaredoug.com/blog/2026/10/26/search-golden-sets-fail.html
account: 
origin: en-rss
---
Want to prove you’ve improved search? Build a golden set of query-document pairs. Then begin experimenting.

Or so you’re told.

I wrestle mightily with search evals. Improvements on golden sets don’t always translate to better user experience. Sadly, futzing with ‘better’ evals doesn’t always pay off with better search.

Let’s critique the classic research eval regime of what you’re “supposed to do” based on BEIR style retrieval datasets. Then talk about some tweaks and viable alternatives to answer narrower, but more exacting questions, about a system’s relevance.

Let’s dig in!

## What’s in an Information Retrieval dataset?

What do these datasets entail? They give us a *query* and what results are relevant / irrelevant for that. Classically called a *judgment list*.

Below we have the judgments for intentionally misspelled `!awnmower` query from Amazon ESCI. ESCI labels perfectly relevant results a grade of 3. Irrelevant results get a grade of 0.

| Query | Grade | Doc ID | Product Title (Shortened) |
| --- | --- | --- | --- |
| !awnmower tires without rims | 3 | B08L3B9B9P | MaxAuto Turf Tires with Rims |
| !awnmower tires without rims | 3 | B07C1WZG12 | Husqvarna Tire Wheel Assemblies |
| !awnmower tires without rims | 3 | B077QMNXTS | MaxAuto 16x6.50-8 Mower Tires |
| !awnmower tires without rims | 3 | B06XX6BM2R | MARASTAR Craftsman Front Tire Assemblies |
| !awnmower tires without rims | 3 | B0089RNSNM | Honda Rear Mower Wheels |
| !awnmower tires without rims | 3 | B005O5Y3QI | Carlisle Turf Saver Tire |
| !awnmower tires without rims | 3 | B0018TWDOI | Oregon Universal Plastic Wheel |
| !awnmower tires without rims | 2 | B07P4CF3DP | Turf Tractor Tires with Rims |
| !awnmower tires without rims | 2 | B01DBGLLUC | John Deere Front Tire Assemblies |
| !awnmower tires without rims | 2 | B0089RA0HY | Honda Front Mower Wheels |
| !awnmower tires without rims | 1 | B01M3SJ699 | Dr.Roc Tire Changing Tool Kit |
| !awnmower tires without rims | 0 | B075SCHMPY | RamPro Utility Tires with Wheels |
| !awnmower tires without rims | 0 | B082K7V2GZ | NEIKO Tire Changing Tool Kit |
| !awnmower tires without rims | 0 | B00N16T5D8 | Honda HRR Replacement Wheel Kit |
| !awnmower tires without rims | 0 | B00004RA3F | American Lawn Mower Push Reel |
| !awnmower tires without rims | 0 | B01H3KC5U2 | Craftsman Front Drive Wheels |

Your dataset might not be 0-3. It might be 1-10, or 0-1. Read the instructions on the tin of your dataset.

## Putting a number on relevance

Our Whiz Bang scientists have built a new search algorithm. They claim it produces amazing search results. We kick the tires with our `!awnmower` query, getting the following ‘meh’ search results.

| query | doc\_id | grade | rank |
| --- | --- | --- | --- |
| !awnmower tires without rims | B01DBGLLUC | 2 | 1 |
| !awnmower tires without rims | B0089RA0HY | 2 | 2 |
| !awnmower tires without rims | B0089RNSNM | 3 | 3 |
| !awnmower tires without rims | B075SCHMPY | 0 | 4 |
| !awnmower tires without rims | B082K7V2GZ | 0 | 5 |

Exactly how ‘meh’ is the query? Let’s put a number on it using the grades of the retrieved results.

Well we know ‘3’ is the highest possible grade. We could just average the grades out of total possible grades (here 2+2+3+0+0 / (3+3+3+3+3) or ~0.4667). We’d call that Precision or P@5 - the proportion of correct top 5 results.

Weighing by the rank would seem prudent. Who cares if the 30th result is correct when the 1st one is wrong? Below we weigh by`1 / rank` before summing. A sum weighed by rank is called [Discounted Cumalitive Gain](https://en.wikipedia.org/wiki/Discounted_cumulative_gain) or DCG (note DCG actually uses 1 / log2(rank)).

| query | doc\_id | grade | rank | discounted gain |
| --- | --- | --- | --- | --- |
| !awnmower tires without rims | B01DBGLLUC | 2 | 1 | 2/1=2.0 |
| !awnmower tires without rims | B0089RA0HY | 2 | 2 | 2/2=1.0 |
| !awnmower tires without rims | B0089RNSNM | 3 | 3 | 3/3=1.0 |
| !awnmower tires without rims | B075SCHMPY | 0 | 4 | 0/4=0.0 |
| !awnmower tires without rims | B082K7V2GZ | 0 | 5 | 0/5=0.0 |
|  |  |  |  | 4.0 (summed DCG@5) |

How good could we do at this DCG@5 metric? Let’s look at the ideal search results. For this query, we could fill all 5 slots with 3s. That’d give an ideal DCG of 6.35:

| Query | doc\_id | grade | rank | gain |  |
| --- | --- | --- | --- | --- | --- |
| !awnmower tires without rims | B08L3B9B9P | 3 | 1 | 3/1=3 |  |
| !awnmower tires without rims | B07C1WZG12 | 3 | 2 | 3/2=1.5 |  |
| !awnmower tires without rims | B077QMNXTS | 3 | 3 | 3/3=1 |  |
| !awnmower tires without rims | B06XX6BM2R | 3 | 4 | 3/4=0.25 |  |
| !awnmower tires without rims | B0089RNSNM | 3 | 5 | 3/5=0.6 |  |
|  |  |  |  | 6.35 | <-summed iDCG@5 |

We can normalize DCG, giving *Normalized* Discounted Cumulative Gain (NDCG) of `4.0 / 6.35 = 0.6299`.

Seems reasonable. But let’s walk through what can go wrong.

## Problem 1: What if the ideal is poor?

Retrieval can work perfectly. NDCG can be 1. But users still complain about irrelevant results.

Why? The corpus doesn’t have anything useful for the query (or at least nothing labeled).

In the query above, we’re lucky to have a healthy balance of relevant / irrelevant results. But consider this `star wars rug` query from [Wayfair WANDS dataset](https://github.com/wayfair/WANDS):

| Query | Grade | Doc ID | Product Title |
| --- | --- | --- | --- |
| star wars rug | 1 (partial) | 5204 | barrett multicolor area rug |
| star wars rug | 1 (partial) | 9137 | geometric purple area rug |
| star wars rug | 1 (partial) | 9138 | delcastillo geometric purple area rug |
| star wars rug | 1 (partial) | 9140 | oloughlin geometric purple area rug |
| star wars rug | 1 (partial) | 9150 | rodrigue geometric purple area rug |
| star wars rug | 1 (partial) | 12098 | green/red/gray area rug |
| star wars rug | 1 (partial) | 22768 | corina soccer time area rug |

There’s nothing labeled relevant for this query. At best, we can retrieve partial matches. So ideal DCG itself is actually quite poor. An algorithm getting NDCG=1 would say “we retrieved as best we could, but there’s nothing useful to find here”.

### Going against the classic NDCG ideal

What can you do? Choose a better ideal DCG.

In industry settings, I prefer an NDCG that errs towards pessimism. Try showing your boss shit results with NDCG=1, you won’t have a good time :).

Instead of tying NDCG to the query, compute an ideal DCG@5 of five results filled with max grade (`[3, 3, 3, 3, 3]` for ESCI). I call this Max NDCG or NDCG-m in honor of [Max Irwin](https://www.linkedin.com/in/maxirwin) who argued for this definition of NDCG. In NDCG-m, the ideal DCG is the exact same for every query.

The counterargument: now we’re not measuring the retrieval algorithm. We’re also measuring our corpus’s ability to satisfy the query. However, if you’re working on a real user problem, you care more about the latter. What’s the point of working on an algorithm with a query set poorly served by the corpus?

Every query has a best possible NDCG-m. Consider `star wars rug` cases, lacking relevant results for a query. Here NDCG-m would be less than 1. At best we can retrieve `DCG(1,1,1,1,1)`. WANDs highest grade is 2, so we’d compute an NDCG-m with: `DCG(1,1,1,1,1) / DCG(2,2,2,2,2)`. That’s about ~0.33. OTOH, classic NDCG all 1s would be an NDCG of 1: `DCG(1,1,1,1,1) / DCG(1,1,1,1,1)`.

Average the best possible NDCG-m over every query in your dataset, you get a sense of how many queries lack positive labels. In WANDS, the max NDCG-m@10 is about 0.77. Meaning a good portion of queries don’t have relevant results to fill in all 10 results. However, with, ESCI the NDCG-m is closer to 0.93, indicating a healthier dataset.

## What about missing labels?

Labeling can be incomplete. The `!awnmower` query above only has 16 labeled results. When tuning relevance, it’s very easy for this to happen:

| query | doc\_id | grade | rank | gain |  |
| --- | --- | --- | --- | --- | --- |
| !awnmower tires without rims | B01DBGLLUC | 2 | 1 | 2/1=2.0 |  |
| !awnmower tires without rims | B0089RA0HY | 2 | 2 | 2/2=1.0 |  |
| !awnmower tires without rims | B087BRYT1Z | NA | 3 | ??/3=?? |  |
| !awnmower tires without rims | B075SCHMPY | 0 | 4 | 0/4=0.0 |  |
| !awnmower tires without rims | B082K7V2GZ | 0 | 5 | 0/5=0.0 |  |
|  |  |  |  | ?? | <-summed DCG@5 |

We retrieved a result at rank 3 with no label. That’s actually pretty tepid. A more severe algorithm change could return all unlabeled results, leaving us confused.

Researchers tell us to grade missing labels as 0 / irrelevant. That assumption can work if (big if) we confidently labeled anything that’s even a little bit relevant. Then we just assume everything else has no relevance signals.

Unfortunately, in even static corpuses, we see plenty of relevant looking unlabeled results. When playing with [agentic search strategies](https://softwaredoug.com/blog/2026/06/08/three-kinds-of-agentic-search), an agent recently retrieved the following from ESCI for `warehouse clearance open box` - all unlabeled results, all saying “Open Box” in the title.

| Query | Grade | Doc ID | Rank | Product Title (Shortened) |
| --- | --- | --- | --- | --- |
| warehouse clearance open box | NA | B084BGC5LR | 1 | Audient EVO 4 Audio Interface (Open Box) |
| warehouse clearance open box | NA | B01NCTOOH6 | 2 | Kicker CompC Subwoofer (Open Box) |
| warehouse clearance open box | NA | B0035BCRRU | 3 | Herman Miller Mirra Chair (Open Box) |
| warehouse clearance open box | NA | B07DPW8N62 | 4 | Seina Folding Utility Cart (Open Box) |
| warehouse clearance open box | NA | B07DQ4HZVX | 5 | Seina Heavy Duty Cart (Open Box) |
| warehouse clearance open box | NA | B073W78G1S | 6 | Seina Compact Folding Cart (Open Box) |
| warehouse clearance open box | NA | B000X4LR64 | 7 | Honeywell Dual-Tone Siren (Open Box) |
| warehouse clearance open box | NA | B005QXLI98 | 8 | Look Keo Road Pedals (Open Box) |
| warehouse clearance open box | NA | B00ZIB9GKG | 9 | Intex Filter Pump Seals (Open Box) |
| warehouse clearance open box | NA | B06Y1BWQD6 | 10 | iHome Bluetooth Lantern Speaker (Open Box) |

The ideal search results, however, don’t appear obviously relevant to the query, despite the label:

| Query | Grade | Doc ID | Rank | Product Title (Shortened) |
| --- | --- | --- | --- | --- |
| warehouse clearance open box | 3 (Exact) | B00R92CL5E | 1 | NETGEAR Wi-Fi Range Extender |
| warehouse clearance open box | 3 (Exact) | B014FGIUNI | 2 | Tork Jumbo Paper Towels |
| warehouse clearance open box | 3 (Exact) | B07F3HM54Z | 3 | MASVIS Queen Mattress Pad |
| warehouse clearance open box | 3 (Exact) | B07PHC96YD | 4 | Simple Modern Insulated Water Bottle |
| warehouse clearance open box | 3 (Exact) | B07T3K6R1B | 5 | Drill Brush Cleaning Kit |
| warehouse clearance open box | 3 (Exact) | B085ZRKQHP | 6 | Solar Outdoor String Lights |
| warehouse clearance open box | 2 (Substitute) | B0893396SX | 7 | ALORAIR Industrial Air Scrubber |

We truly don’t know whether the labeled results are more / less relevant than the retrieved results.

Maybe there was a sampling bias in what was labeled, and we just missed these? Or perhaps the unlabeled results are truly not as relevant for reasons related to a buried bit of metadata? Maybe putting “Open Box” in the title implies some kind of low quality to users, so they don’t click on those results? Reviews are poor? The shipping sucks? Maybe they’re expensive?

We can’t know. We can say though, that it’s suspicious. In a real life setting, you’d want those to be labeled.

### One solution: NDCG-f

If we *do* trust the existing labels, we can evaluate with a filtered variant of NDCG. Instead of labeling irrelevant results as 0, we ignore unlabeled results. We evaluate each query on a filtered sample.

I call this NDCG-filtered (NDCG-f for short).

For example, let’s say we retrieve this hypothetical mix of labeled / unlabeled results for query `!awnmower tires without rims`

| Query | Grade | Doc ID | Rank | Product Title (Shortened) |
| --- | --- | --- | --- | --- |
| !awnmower tires without rims | 2 | B07P4CF3DP | 1 | Turf Tractor Tires with Rims |
| !awnmower tires without rims | NA | B012345678 | 2 | TurfMaster 13x5.00-6 Replacement Tires Only |
| !awnmower tires without rims | 3 | B077QMNXTS | 3 | MaxAuto 16x6.50-8 Mower Tires |
| !awnmower tires without rims | .. | .. | .. | .. |
| !awnmower tires without rims | 3 | B005O5Y3QI | 10 | Carlisle Turf Saver Tire |
| !awnmower tires without rims | 3 | B08L3B9B9P | 11 | MaxAuto Turf Tires with Rims |
| !awnmower tires without rims | .. | .. | .. | .. |
| !awnmower tires without rims | 2 | B07P4CF3DP | 20 | Turf Tractor Tires with Rims |
| !awnmower tires without rims | NA | B012345611 | 21 | YardGrip Tubeless Mower Replacement Tires |
| !awnmower tires without rims | 1 | B01M3SJ699 | 22 | Dr.Roc Tire Changing Tool Kit |

Let’s rerun this, filtering in only any result with a label. We squeeze out anything unlabeled, getting this:

| Query | Grade | Doc ID | Rank | Product Title (Shortened) |
| --- | --- | --- | --- | --- |
| !awnmower tires without rims | 2 | B07P4CF3DP | 1 | Turf Tractor Tires with Rims |
| !awnmower tires without rims | 3 | B077QMNXTS | 2 | MaxAuto 16x6.50-8 Mower Tires |
| !awnmower tires without rims | 3 | B005O5Y3QI | 3 | Carlisle Turf Saver Tire |
| !awnmower tires without rims | 3 | B08L3B9B9P | 4 | MaxAuto Turf Tires with Rims |
| !awnmower tires without rims | 2 | B07P4CF3DP | 5 | Turf Tractor Tires with Rims |
| !awnmower tires without rims | 1 | B01M3SJ699 | 6 | Dr.Roc Tire Changing Tool Kit |

Compare the second ranking vs the first. The labeled results are in the same order, we’ve now just omitted the unlabeled ones.

Now with this filtered set we compute NDCG.

We’re not measuring *the true relevance of top N*. We are answering a narrower question: “within the universe of labeled results, does our system put relevant above irrelevant?”. A high NDCG-f says we’ve ordered the labeled results against each other correctly. That’s a useful, minimum bar to clear. But not the end-all-be-all prediction we’ll win an A/B test.

Still, I would rather answer this narrower question reliably than make grand claims with noisy evals.

This limited, but reliable, measure helps us at least find regressions. Knowing somewhere, you placed a known irrelevant result above a known relevant one indicates a problem. Something to investigate.

We can study, further, whether NDCG-f also correlates to user perceptions of relevance. Do wins in NDCG-f correspond to A/B testing wins? Or other positive signals for relevance? That boils down to

1. How much you trust that your labels cover every way a result can be relevant / irrelevant?
2. How well covered is your top N with labeled results?

If we’ve provided sufficient coverage of different types of positive / negatives, we perhaps can infer something about a promising search approach. The relative ranking of these might say something about the broader universe of similar search results. In Chapter 12 of [AI Powered Search](http://aipoweredearch.com) I discuss using active learning to detect blindspots in eval datasets. In this case, selecting to be shown to users to gather clickstream data.

At a minimum, we need to expect that unlike golden sets, search evals need constant care and labeling. Data and algorithms shift. New results appear at the top. Expect labeling to be an ongoing practice, not one-and-done.

## Maybe just treat it as a unit test

Should NDCG escape containment from the search team?

The most value I’ve gotten out of NDCG and pals isn’t to make predict A/B test winners. It’s to simply build a type of unit test about search. *I* label some results that prove my idea works, then I tweak until I get the order I want. I make no claims other than the code I write should order results in a certain way.

For example, I want to implement query understanding where results of a certain category appear above other categories. I might build a little test set, and prove to myself, over a set of queries that I’ve acheived NDCG=1. That doesn’t mean the search is good, it just means it works as I expected.

Problems start when we try to communicate search metrics outside the search team. That’s when it gets really complex, and offline evals tend to stop serving us as well as just running an A/B test.

## Don’t trust one system of evaluation

I wrote in [grug-brained evals](https://softwaredoug.com/blog/2025/06/22/grug-brained-search-eval) you can accomplish A LOT with simple, easy to understand evaluations.

NDCG is one, very limited, evaluation system. Even if it has the veneer of decades of research. It’s rather limited in practice. You have a lot of options people initially discount as silly, but turn out to actually work.

Each of these deserves its own in-depth blog post:

1. Measure the absolute change of an algorithm change (not just whether the change turns out to be “good”). Metrics like [Ranked-Biased Overlap](https://dl.acm.org/doi/10.1007/978-3-031-15037-1_11)
2. Within those results that change: produce side-by-side search results for evaluation by domain experts. See whether experts prefer one ranking or another
3. Build unit test style evals: if you search for query ‘red shoes’ the top results should all have `category:footwear`. Literally write that test! Or measure how often it occurs.
4. Study search clickstream data at the [session level evaluations not query level](https://softwaredoug.com/blog/2026/03/30/session-vs-query-based-search-evals). Replay individual sessions of the `red shoes` query to see if you reduce the rank of what’s clicked on across all sessions
5. Emerging LLM as a judge techniques like [Blitzrank](https://blitzrank.ai/) to derive an LLMs pairwise preference for a search result given a query.

I barely scratched the surface in this post. We don’t talk enough about search evals, eager to test a cool idea out in BEIR. But that doesn’t help teams practically face their problems.

Don’t overbuild evals. Instead of making grand, difficult to trust, claims, prefer evals with narrower claims with higher confidence.

---

### Starting in November: AI-Powered Search — Modern Retrieval for Humans & Agents

 [![AI-Powered Search course with Doug Turnbull and Trey Grainger](/assets/media/2026/ai-powered-search/course-social.jpg)](https://maven.com/search-school/ai-powered-search) 

Learn the latest AI search skills with the authors of *AI-Powered Search*. Join Doug Turnbull and Trey Grainger to explore modern retrieval for humans and agents. [Explore the course on Maven.](https://maven.com/search-school/ai-powered-search)

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---