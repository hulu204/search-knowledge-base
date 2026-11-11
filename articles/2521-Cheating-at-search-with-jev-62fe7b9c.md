---
title: 'Cheating at search with jev'
company: softwaredoug
tag: 搜索
date: 2026-09-22
url: https://softwaredoug.com/blog/2026/09/22/jev-query-understanding.html
account: 
origin: en-rss
---
You could summarize 33% of my career over the last 2.5 years as “classifying queries with LLMs.” I teach a [whole course on it](https://maven.com/softwaredoug/cheat-at-search).

So, I took [jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) out on a query classification test drive.

## What am I classifying, exactly?

The [Wayfair WANDS dataset](https://github.com/wayfair/WANDS) has labeled query-document pairs. If, say 80%, of the relevant products for a query goes with a product, I consider this the ground-truth category for a query.

So if `red sofa` has these judgments

| Query | Relevant Product | Product Category |
| --- | --- | --- |
| red sofa | Crimson sectional | Furniture |
| red sofa | Leather couch | Furniture |
| … | … | ?? |
| red sofa | Weird sofa | Furniture |

We clearly see a pattern where a large proportion of this query’s relevant documents are “Furniture”. We can safely declare that’s the category the query should be classified to.

Now I have a ground truth:

| Query | Correct Category |
| --- | --- |
| red sofa | Furniture |
| office sofa | Unknown |
| desk | Office |
| dog bowl | Pets |
| … | … |
| christmas tree | Holiday decor |

## Don’t classify ambiguous cases

While ostensibly I’m writing this article about some hot shit new technology (jev) when I really want to point out is the importance of a classifier saying “I don’t know”. We need precise answers, and that may mean reducing recall / coverage over every query.

Why?

* Not every query has a label, some we abstain from labeling because its too ambiguous (some queries, like “office sofa”, have relevant results in many categories)
* If we DID produce a label for ambiguous cases, it’d be disastrous as we’ll exclude many relevant results in retrieval

So I treat a predicted category, when the ground truth is “Unknown” as a failure when evaluating.

## Jev vs LLM implementation

Jev classifies with the concept of a “choice”, implemented like this:

```
client = TypeSafeClient()
response = client.system_one(
   state=query,
   questions={
      self.field: Choice(
         instructions=self._prompt(query),
         criteria={
           "Furniture": "A search for products used to make a room suitable for living or working, such as chairs, tables, and beds."
           "Home Improvement": "A search for products and services that help improve the functionality, aesthetics, or value of a home, such as tools, paint, and renovation services."
           "Décor & Pillows: "A search for products used to enhance the aesthetic appeal of a space, including decorative items, pillows, and other accessories."
            ...
      )
   }
)
```

This produces a prediction with a confidence from 0-1. I can set a threshold like 0.9. Then override any prediction confidence < 0.9 as “Unknown”. I should see higher accuracy at lower coverage (i.e. a nice AUC curve) as I adjust my threshold floor.

I compare the accuracy of my jev approach to the classic prompt-based classification (with GPT-5 / GPT-5-mini). For that implementation, of a clean list, I’m forced to stuff decision criteria into the prompt:

```
Which category best describes the query?

It's very important to choose "Unknown" if its unclear

{query}

Category descriptions:

Furniture: A search for products used to make a room suitable for living or working, such as chairs, tables, and beds.
Home Improvement: A search for products and services that help improve the functionality, aesthetics, or value of a home, such as tools, paint, and renovation services.
Décor & Pillows: A search for products used to enhance the aesthetic appeal of a space, including decorative items, pillows, and other accessories.
...
```

We ask OpenAI to respond with structured outputs, where [legal return values](https://developers.openai.com/api/docs/guides/structured-outputs) are `["Furniture", "Home Improvement", "Décor & Pillows", ..., "Unknown"]...`. The basic outlines of the code [can be found here](https://github.com/softwaredoug/search-experiments/blob/main/research/query_understanding/query_understanding_jev_thresholds.md).

## Which is more accurate?

More detailed results [can be inspected here](https://github.com/softwaredoug/search-experiments/blob/main/research/query_understanding/query_understanding_jev_thresholds.md), but you can see the tradeoff in accuracy below:

![](/assets/media/2026/jev-query-understanding/image1.png)

You can see gpt-5 and gpt-5-mini blunder ahead, trying to predict everything. However, jev gives us an opportunity to calibrate our precision, trading off coverage for accuracy.

That’s non-negotiable in search. We can confidently use categories when confidence=0.99. Perhaps we’re so confident, we just filter retrieval to that. But be a bit more dubious when our cutoff goes lower. In these cases, maybe we treat the query classification as a softer, additive boost.

None of this measures latency or cost. In my experience, jev is at least an order of magnitude cheaper on both fronts.

## What would be next in query understanding?

Query understanding is large and chronically underappreciated in retrieval. Some additional pointers below if you actually put this in production.

### Predict a list, not one label

It’s often better to predict a set of possible categories.

If most “office sofa” relevant products exist in `["Furniture", "Office"]`, then whet we can measure is our classifier’s ability to recall relevant labels. Ideally our classifier would return this exact list:

`["Furniture", "Office"]`

Evaluating this looks different. We suddenly need to measure:

* **Did we omit a relevant category?** It’d be problematic to omit a category with relevant results. So we measure *recall* first and foremost: what percentage of ground truth received a prediction.
* **How similar is the predicted list to ground truth?** It’s not as bad to over-predict additional categories, because we’re still *somewhat* focused on a bias towards some of the right categories. But it gets progressively less valuable as the predicted size increases.

### Query understanding works best hierarchically, not flat

Users think hierarchically when it comes to language. Naive searchers use broad, ambiguous terms like “dress shoes”. Expert searchers get very specific and zero-in on exacting terms like “oxford shoes”. Even in something as simple as *color* some users will say “crimson” or “oxblood”. My smooth brain will use “red”. The reality of query understanding is rarely a flat list of tags, it’s a hierarchy:

```
footwear > dress shoes > oxford shoes
footwear > athletic > running shoes
...
```

I guarantee you 95% of when someone says they think they need a knowledge graph, they really need a hierarchical vocabulary or taxonomy. I frequently find search use cases that need a vocabulary modeled hierarchically. I almost never one that needed an actual knowledge graph.

Hierarchical classification becomes its own challenge. It’s very important to get broad categories correct to prevent catastrophic mistakes. Narrower and narrower categories remain important, but create fewer glaring errors. Add to this the very large vocabulary of a big hierarchy (10K? 100K items?). You quickly get into [extreme multi-label classification territory](https://www.amazon.science/blog/using-generative-ai-to-improve-extreme-multilabel-classification).

For the classification itself: Luckily Jev [has documentation on hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification). I’ve written about using LLM hallucinations of plausible categories, then [resolving them to the real vocabulary as another approach](https://softwaredoug.com/blog/2026/08/10/hypothetical-classifications).

## Have fun!

I’ve often said query understanding is the 3rd pillar of retrieval after traditional dense / sparse. Jev seems like a fantastic tool to help tackle these problems, but don’t take the evaluation of the model for granted if you want to master its power!

And if you want to hack on this, I’ve [jevving-up my Cheat at Search course, starting in October](https://maven.com/softwaredoug/cheat-at-search) :)

---

### Join me for a Retrieval Augmented Gathering

 [![Retrieval Augmented Gathering](/assets/media/2026/retrieval-augmented-gathering.png)](https://maven.com/lls/f27953) 

![](/assets/media/headshot2.jpg)

#### Doug Turnbull

 [More from Doug](/)  
 [Twitter](https://twitter.com/softwaredoug/)  |  [LinkedIn](https://www.linkedin.com/in/softwaredoug/)  |  [Newsletter](https://softwaredoug.kit.com) |  [Bsky](https://bsky.app/profile/softwaredoug.bsky.social)

---