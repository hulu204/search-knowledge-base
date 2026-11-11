---
title: "LLM Judges aren't the shortcut you think"
company: softwaredoug
tag: 评测
date: 2025-11-02
url: https://softwaredoug.com/blog/2025/11/02/llm-judges-arent-the-shortcut-you-think
account: 
origin: harvest3-202607
---
Is “LLM as a judge” overhyped? After years of implementing LLM judges for clients, I find more of them recognize the limitations.

LLM judges fail for the same reason any evaluation method fails: teams lack good data+evaluation to begin with. LLM judges aren’t the shortcut teams hope. Instead, they are themselves a thing that needs data and monitoring to get use out of.

Let me walk through the pitfalls of LLM as a judge (for search) that you’ll encounter.

## LLM as a judge

When I talk about LLM as a judge, my focus is search. I mean creating a [judgment list](https://softwaredoug.com/blog/2021/02/21/what-is-a-judgment-list). For search that means labeling how relevant a document is for a query. How relevant is the product “garden trowel” for a `q=shovels`? Maybe this “garden trowel” is less relevant than “iron spade”?

In the ancient past, to improve the search, I would be limited to a tiny hand-labeled judgment list. Labeling by hand is expensive. Datasets drift out of date quickly. New use cases arise. So we constantly need humans to relabel.

These costs inspire teams to use LLMs to build judgments, They:

1. Start with a ground truth of human labels
2. Build a prompt to approximate that ground truth
3. Apply those prompts to go beyond the ground truth to new query / documents

If done well, we can sit at our laptop, tinker with relevance algorithms, and continue to tune without bother humans for non-stop relabeling.

Sounds promising. But teams often ignore many of the assumptions and nuance underlying the task of LLM labeling. Let’s go through them, and we’ll see at the end, maybe LLMs should play a different role in evaluation?

## Problem one - LLM evals don’t know what’s engaging to users

Users’ ever-evolving lizard brains drive conversions. And while optimizing for just lizard brains would itself be a nightmare, so would only focusing on an LLM’s opinion.

LLMs do a better job approximating *human evaluations*. In search, we call these evaluations *explicit* judgments. They use human labelers’ basic knowledge of the world to label a result as *topically relevant* to the query or not.

Topical relevance is only one kind of relevance. As an example, for a search of “articles about harry potter”. The article is either factually about Harry Potter or its not. We might also consider other gradations:

* Is the article well written?
* Is it article from an authoritative source?
* Is the article about a tangential topic? Dumbledore vs Gandalf etc?

All of which relate to topicality, authority, and knowledge. An LLM excels at this — LLMs live in a world of facts and knowledge.

But LLMs don’t have limbic systems. So their evaluations come with limitations.

In real search applications, “relevance” goes beyond topicality. I worked at Reddit on search. A search for “harry potter” might mean anything from a memes, to drama about JK Rowling, to every kind of juicy controversy, spicy post, or oddity. People search for “cybertruck” not for reviews but to see silly videos.

Then there’s the more mundane. I found at Shopify, users preferred plain or black clothing over flashy items based on their clicks. Unless you tell an LLM this (because you’ve done the analysis) an LLM won’t intrinsically catch this.

Often the “topical” part of search is relatively easy. But engaging search, that captures these human oddities, must go beyond world-knowledge to at least get *some* of a user’s lizard brain.

## Problem two - the last 10% of disagreement is the important stuff

Many teams get excited when they immediately see 70-80% agreement with human labelers. With a bit of tuning, they can inch closer to 90%.

In my experience, that last bit of human-LLM disagreement matters. Those are the non-obvious cases. Search deals with a big [hard negatives](https://zilliz.com/ai-faq/what-is-hard-negative-mining-and-how-does-it-improve-embeddings) challenge. Those examples that deceptively seem relevant naive search algorithms (or labelers), but are, in fact irrelevant. That last 10-30% might be what more careful labelers would catch. Or represented in clickstream based labels.

For example on this furniture dataset, a LLM doesn’t understand that a “bistro table” is meant for ***outdoor*** use in US furniture lingo. That’s not obvious to an LLM: The LLM imagines I’m opening a restaurant.

Simple algorithms often capture that first 80-90%. It’s the 10-20% you need great labels for. So pay attention not just to coverage. But for which use cases.

A 90% coverage might be good regression tests, it might not help you go beyond easier wins.

## Problem three - sneaky overfitting

So far, I’ve mentioned a few strange cases the LLM judge might miss: a bistro table is meant for outdoor usage. Users preferring darker clothing items.

The savvy prompt engineer will want to fill the prompt with examples to help the LLM perform better on these cases.

But beware overfitting to these particular failure cases.

With every new rule, you push the model’s meager attention away from the general problem, and towards your exceptions. Layer example after example, and you’ll find yourself with a brittle system focused excessively on specific use cases.

Overfitting with prompts can be sneaky. Playing whack-a-mole with your eval data can degrade generality. You can get perfect results on the eval set, only to expand to unseen queries, and find the gains no longer hold.

To do a good job, you need holdout data you’re not tuning against. A set of judgments you don’t peak at. Because peaking might cause you to sneak a change into the prompt, making the holdout less useful as an independent validation step.

Add rules and exceptions carefully, you’ll be surprised how easy it is to pull an LLM away from its generality.

## Problem four - LLMs only evaluate the document it sees

LLMs only evaluate the document it sees. IE:

```
Query: outdoor seating
Product Name: Bistro Table
Product Description: Enjoy this lovely bistro table on your porch...
```

Is this enough information for evaluating the product? Is it what a user sees?

Suddenly, you decide to add new information about the product

```
Query: outdoor seating
Product Name: Bistro Table
Product Description: Enjoy this lovely bistro table on your porch...
Category: Outdoors
```

What are we evaluating truly?

* The products relevance?
* The usefulness of a set of product properties for determining relevance?
* How comprehensively you’re describing products to an LLM?

Really it gets down to a classic problem in search. There’s perceived relevance - the relevance of the product, as it appears in your product page. Then there’s actual relevance - the detailed, thoughtful understanding of your product by a user. A lot depends not just on true relevance, but how it’s presented to users.

## Problem five - Your LLM judge can’t be trusted on novel use cases

I assume the goal of LLM as a judge in to align to human labelers. But rarely do those judgments comprehensively represent every use case.

Search metrics with human evals don’t go up-and-to-the-right. They seesaw as teams reactively label, solve, label, solve ad infinitum. In my experience it’s rare to find a team build a true, comprehensive human labeled evals covering every use case. Even if we did, we’d need to account for evolving search use cases.

The flow usually goes like this: we want to solve a problem (search by product name). So we capture some judgments for that use case. Relevance starts low. We work a bit to improve this use case and it goes up. Yay!

But the boss comes to our desk and suggests we have a new problem to solve: search of furniture by the room (living room, etc). We gather more labels. We know we’re bad at this use case. So search metrics go back down. Sad 😟

We solve that use case, it goes back up to where it was before. Repeat. Up and down. See-saw.

This presents a problem for an LLM judge. If our human labels only focus on a subset of use cases, **we’re also aligning our LLM judges on a subset of use cases.**

Our LLM judge generalizes to just a piece of the problem. The LLM judge can’t be trusted on a new use case until we measure it’s abilities in that use case.

So if you seesaw its human labeling, you must seesaw the alignment of the LLM judge to the use cases we capture in human eval. As we adopt a new use case, we need more human labels. We need to retest the LLM judge. And so on.

The task of human labeling does not end with LLM Judges. In fact its even more crucial.

## How to LLM as a judge

Here’s how I use LLM judges:

* To extend labels on use cases I already measure decently to new queries (because I can trust alignment of the LLM on this use case)
* As a safeguard against regressions

I trust the LLM judge to flag a regression on the use cases my human labels cover. The LLM is aligned and measured against these. I don’t trust the LLM to discover new, unexpected ways users search. I look to the users for that, not LLMs.

Still many teams don’t even do decent monitoring of topical relevance. There are plenty of obviously broken search engines. The ones that would benefit from an LLM judge, likely would benefit from rounds of human labeling first needed before blindly trusting an LLM judge.

## We already have automated data labeling at home kids

If we have enough labels to evaluate LLM as a judge on a use case, we have enough to train an ML model to recover those labels. We can then see a better place LLM’s fit into evaluation:

* LLMs focus on factual, topical parts of the problem. But miss other parts of the problem
* LLMs might see a subset of the content features
* Other non-LLM features might help us better evaluate relevance (embedding similarity, text matches, etc)
* Other ground-truths (besides human) might be a better definition of relevance (ie engagement based labels)

Instead of LLM as a Judge, **why not Learning to Rank as a judge?** We seem to have forgotten that ranking models provide value beyond directly deploying them to production. They can help guide more manual search tuning as well.

I’m becoming more of a fan of LLM-for-feature-generation over LLM as a judge. LLMs can cover the topical part of relevance. You can ask them “Which of these product names is more relevant to the query?”. The downstream, traditional ML model is agnostic to where the features come from. They could be an embedding similarity, LLM decision, lexical similarity, or more.

That’s much more my interest these days. When someone says “LLM as a judge” I nod and say yes let’s build that, but then go on and probably look into using LLM features heavily in a larger model. LLMs can be very useful for rapid feature development: they’re promptable and easy to play with.

If you’re interested in this approach, check out this [blog post](https://softwaredoug.com/blog/2025/01/21/llm-judge-decision-tree) and the corresponding [Haystack talk](https://www.youtube.com/watch?v=S7EXkGDcd7A). Also a talk from Shopify [choosing cross encoders for evaluation over LLMs](https://www.albertocastelo.com/blog/2024-06-12-mices-talk)

Enjoy!

---

### Upcoming course: Build your own vector database

 [![Build your own vector database](/assets/media/2026/vectordb-social.png)](https://maven.com/softwaredoug/vectordb) 

Want to understand what makes embedding retrieval fast, relevant, and useful in real AI systems? Join [Build your own vector database](https://maven.com/softwaredoug/vectordb) and build the core pieces yourself, from embeddings and indexing to search and retrieval.

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---