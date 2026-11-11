---
title: 'https://eugeneyan.com//writing/how-to-choose-problems/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/how-to-choose-problems/
account: 
origin: en-rss
---
# [eugeneyan](/)

* [Start Here](/start-here/ "Start Here")
* [Writing](/writing/ "Writing")
* [Speaking](/speaking/ "Speaking")
* [Prototyping](/prototyping/ "Prototyping")
* [About](/about/ "About")
* [![](/assets/icon-search.svg)](/search/ "Search")

# Choosing Problems in Data Science and Machine Learning

[
[datascience](/tag/datascience/)
[machinelearning](/tag/machinelearning/)
[leadership](/tag/leadership/)
]
 · 12 min read

Given 8 data scientists and 20 problems, how do you choose the 3 - 8 problems that the team should work on?

This post answers the second most-voted question on the [topic poll](/topic-poll/). We’ll focus on how to **choose** problems, instead of how to *solve* problems or how to *find* problems (though Amazon’s [Working Backwards](https://www.inc.com/justin-bariso/amazon-uses-a-secret-process-for-launching-new-ideas-and-it-can-transform-way-you-work.html) process is great for the latter).

I’ll start with the trusty cost-benefit analysis and discuss problems where the solutions aren’t easily quantifiable. Then, we’ll see how problems (and solutions) can range from incremental to disruptive. Finally, I’ll touch on common pitfalls when choosing problems.

## Quantifying problems via cost-benefit analysis

[Cost-benefit analysis](https://en.wikipedia.org/wiki/Cost%E2%80%93benefit_analysis) is an approach to quantify the potential returns from a decision. It usually involves assigning a dollar value to the associated costs and benefits before applying the simple formula below:

> Benefits - Costs = Overall Return (i.e., Net Benefits)

In the simplest scenario, the **benefit of solving a problem is either increased revenue or decreased cost**. Here’s an example where we try to quantify the benefit of sending customers push notifications on wish-listed items.

We work for an e-commerce company that has a wishlist function. Customers use the wishlist extensively, adding $100 million worth of products every quarter. From our analysis of wishlist products and customer behavior, we learn that customers use wishlist for two main reasons: To bookmark out-of-stock products, and to set aside products that cost higher than their usual price point.

Furthermore, we find that in any given month, 10% of wishlisted products (i.e., $10 million in value) are either restocked or have a >10% price drop. We can help customers by notifying them of such changes to products on their wishlist. Assuming our push notification system leads to a 1% conversion rate, it will generate additional revenue of $100,000 per month (0.01 x $10 million) or $1.2 million per year.

While assessing problems, we’ll also want to consider how many customers are affected (**extent**) and how serious the problem is (**severity**). To illustrate, here an example of deciding between which categories to improve product search on.

We work for an e-commerce company that has three main product categories: Fashion, Electronics, and Groceries. By analyzing search queries, we learn that customers search for these categories 50%, 20%, and 40% of the time (i.e., **extent**). We also calculate the click-through rate (CTR) and conversion of these queries and find that groceries search performs the best while electronics search performs the worse (i.e., **severity**).

We estimate we can improve fashion search by 5%, leading to an overall search improvement of 2.5% (50% of search traffic x 5% improvement). For electronics, given the problem is more severe, we estimate an improvement of 10%, leading to an overall search improvement of 2% (20% of search traffic x 10% improvement).

In the first example, we quantified the benefit at $1.2 million yearly. But this doesn’t include the improved customer experience of being notified when items are back-in-stock or have a significant price drop. (By the way, this is an [actual use case that won a hackathon](/writing/evaluating-ideas-at-a-hackathon/) and got implemented, though the numbers cited are fictitious).

In the second example, if deciding based on the numbers alone, we should choose to improve fashion search. But what if our electronics search is so bad that we’re losing customers who shop for electronics on our platform?

The point is, try to quantify as much as you can but be aware that it’s hard to fully quantify a problem. Also, overemphasis on quantifiable outcomes can sometimes lead to the wrong decisions. For example, should we work on the problem of de-ranking bad products (i.e., high return rate, low-ratings) if solving it will reduce conversion rate and revenue? If we’re only looking at directly quantifiable outcomes (i.e., reduced revenue), then no. However, I would argue that the improved customer experience (i.e., reduced return rate, greater satisfaction with the product) will more than makeup for it in the long-term.

**The second part of the equation covers cost** where a big chunk goes to compensation. Developing new features or systems requires data scientists and engineers. Take their monthly compensation and multiply it by the development time required (e.g., 3 months)—that’s the development cost. There’s also the ongoing cost of operating and maintaining the system (e.g., on-call, software updates, etc) which can cost 2 - 4 weeks every year.

The other big cost involved is infra, especially if you need to work with large volumes of data or deep learning. If we’re running in the cloud, we can estimate the cost of each job based on the time required per job, the number of [instances](https://aws.amazon.com/ec2/instance-types/) (i.e., machine) required, and the cost per instance hour. If our predictions are generated on-the-fly (i.e., online inference), we’ll also need instances to serve our model—this can get expensive, especially if we need GPUs. (If you have on-premise hardware, your costs will differ.)

## Capabilities & learning exercises apply to all problems

We’ve seen how it can be difficult to quantify customer benefits, especially if these benefits don’t directly increase revenue or reduce cost. This extends to problems where solving them has no direct customer benefit at all. However, solving such problems leads to **capabilities** and **learning** that help us to solve other problems.

**Capabilities act as multipliers**, often to reduce the cost of solving other customer-facing problems. For example, we might have the problem of getting features into production—building/adopting a feature store seems like the right solution. In this case, the feature store doesn’t generate revenue on its own, but it reduces the effort needed to put features into production (see example below).

GoJek found that [getting features into production](https://www.gojek.io/blog/feast-bridging-ml-models-and-data) was difficult. Engineers had to spend time setting up infra, and data scientists had to rewrite offline, batch feature transforms to work online. Thus, they built Feast, a feature store that allows data scientists to use features—for training and serving—via a simple API.

This enabled feature sharing across teams and reduced the time spent by data scientists brainstorming for features in their offline experiments. Feast also made it way easier to use those same features in production. This reduced the time spent getting their machine learning models into production. (More on feature stores [here](/writing/feature-stores/).)

Another example is building a pipeline that enables data scientists to deploy their own machine learning models, instead of having to wait for ML engineers. (We can rig a simple pipeline with Docker and SageMaker). Similarly, this cuts development time and cost, allowing the team to solve more problems in the same amount of time.

**Capabilities also include research and data assets**. For example, we might invest time in training embeddings of [tweets](https://blog.twitter.com/engineering/en_us/topics/insights/2018/embeddingsattwitter.html), [products](https://arxiv.org/abs/1803.02349), or [stores](https://doordash.engineering/2018/04/02/personalized-store-feed-with-vector-embeddings/) that can be used across various teams and applications. This reduces the cost of each team creating their own embeddings. Also, the addition of embeddings (as features) often gives a boost to the performance of existing machine learning systems. Similar work includes building knowledge graphs that other teams can use in their applications (e.g., [LinkedIn](https://engineering.linkedin.com/blog/2016/10/building-the-linkedin-knowledge-graph), [WalMart](https://medium.com/walmartglobaltech/retail-graph-walmarts-product-knowledge-graph-6ef7357963bc), [Airbnb](https://medium.com/airbnb-engineering/contextualizing-airbnb-by-building-knowledge-graph-b7077e268d5a)).

Taken together, engineering capabilities, research, and data assets help to reduce development costs and increase iteration rate. Assuming they cut the development cycle by half, this means we now have the time and resources to take on twice as many problems—that’s how capabilities contribute as a **multiplier**.

Another set of problems we can tackle are **learning exercises**. These are problems where we are uncertain about our ability to solve them, or if they bring any benefits. Nonetheless, solving these problems can be valuable. Thus, we might invest a month or two in a learning exercise to gain more clarity.

For example, product and business stakeholders might be bullish on the benefits of image search and recommendation, especially for categories such as fashion, furniture, and toys. However, the data science team is uncertain whether we have the capability for it (e.g., deep learning on images at scale). To gain clarity, we might conduct a series of learning exercises, first with [image classification](/writing/image-categorization-is-now-live/), then with [image search and recommendation](/writing/image-search-is-now-live/). The outcomes of these learning exercises pave the way and **allow us to solve problems that were previously thought unsolvable**.

## Incremental vs. Disruptive (aka short vs. long-term)

Other than costs and benefits, I find it helpful to also consider if the problem requires an incremental or disruptive solution. Incremental changes include improvements on existing systems (e.g., new feature columns) while disruptive changes include building a new (replacement) system. From this perspective, incremental and disruptive changes are sometimes viewed as short-term vs. long-term efforts (though there can be simple, quick solutions that are disruptive).

Incremental solutions require less time, lead to small wins, and demonstrate consistent progress. This helps the team win trust within the organization, especially if the team is new. Business stakeholders *love* incremental results that they can parade at monthly/quarterly management updates.

![From casettes to CDs to MP3s to streaming](/assets/music-s-curve.webp "From casettes to CDs to MP3s to streaming")

Jumping from S-curve to S-curve in the music industry ([source](https://stratoserve.com/2020/11/the-s-curves-of-radical-and-incremental-innovation.html))

Nonetheless, incremental improvements eventually plateau and it’ll require a disruptive solution to step up to the next innovation curve. Take music for example:

* In the 1970s, we had **cassettes and Sony [Walkmans](https://en.wikipedia.org/wiki/Walkman)**. They disrupted vinyl records and made music portable. Incremental innovation increased music storage from 60 minutes to 90 minutes though music quality remained stagnant.
* In the 1980s, **CDs** disrupted cassettes and provided a step improvement to music quality. Nonetheless, each CD could only store about [80 minutes of music](https://en.wikipedia.org/wiki/Compact_disc).
* In the 1990s, the **MP3 player** (e.g., iPod) disrupted CDs and allowed users to carry thousands of songs in their pockets.
* In the 2000s, **music streaming** (e.g., Spotify) disrupted the MP3 player. Now, users can listen to any music on demand.

From the example above, each disruptive solution provides a step-up on the customer experience, from vinyl records to cassettes (portability) to CDs (quality) to MP3 players (quantity) to streaming (on-demand).

The same applies to data and machine learning. For data processing and transformation, there’s only so much we can squeeze out of SQL queries on a traditional, non-distributed database. We’ll eventually need to bite the bullet and shift to a distributed framework such as Spark or Flink. This disruptive change leads to a step improvement, letting us work with larger amounts of data, run jobs at greater frequency, and even process streaming data.

In machine learning, switching from conventional models (e.g., linear regression, decision trees) to deep learning can also lead to step improvements in model performance. We can also advance how we use machine learning—for example, by switching from daily recommendations to [real-time recommendations](/writing/real-time-recommendations/#when-not-to-use-real-time-recommendations). Real-time recommendations can serve customers better when the customer journey is time or context-sensitive, or when we have no historical data about customers (e.g., cold-start problem).

At the risk of stereotyping, business stakeholders bias towards faster, incremental improvements while data scientists and engineers prefer working on longer-term, disruptive solutions. I’ve found that picking a mix of incremental and disruptive problems/solutions leads to the greatest benefit in the medium to long-term.

## Pitfalls: Resume driven development & Pet projects

That said, the pendulum can sometimes swing too far towards solving disruptive problems. One symptom of this is [**resume driven development**](https://completedeveloperpodcast.com/episode-172/), where engineers deliberately use new or popular technologies to embellish their resume—it’s not about what works best but what’s the *coolest*. This happens in machine learning too, where data scientists wedge the latest state-of-the-art techniques ([GPT-4](https://arxiv.org/abs/2005.14165), [Vision BERT](https://arxiv.org/abs/2010.11929), etc.) into projects.

Sadly, this happens too often in tech, where people are expected to deliver sophisticated (read: byzantine) solutions to demonstrate scope and depth. This leads to unnecessarily complex systems that cut across multiple teams, involve twice the tech needed, and apply deep learning techniques that were just published yesterday. As a result, we sometimes see a trail of husks that were abandoned when their creators got promoted or moved on.

![The dangerous animals of product management](/assets/product-animals.webp "The dangerous animals of product management")

Beware the Highest Paid Person's Opinion and Zero Evidence But Really Arrogant ([source](https://customerthink.com/the-dangerous-animals-of-product-management-and-how-to-tame-them/))

Another pitfall is jumping into a problem because it’s **someone’s pet project**. We might do this to earn the trust of important stakeholders, or because we don’t know how to (or can’t) say “no”. Sometimes, the stakeholder loses interest after we’ve poured significant time and resources into solving the problem. Or it ends up being a wild goose chase because we didn’t think through the problem enough.

When the team is new, taking on such projects can help to demonstrate value and build trust with stakeholders. Nonetheless, we’ll eventually have more problems than resources and will need to be more deliberate about choosing problems to tackle. One solution is to work with stakeholders to define the problem via a [one-pager](/writing/what-i-do-before-a-data-science-project-to-ensure-success//#first-draw-the-map-to-the-destination-one-pager) and get their commitment to follow through with the project.

## Framing it in a 2 x 2 of Benefits vs. Innovation

To summarize what we’ve discussed above, let’s try to frame it in a 2 x 2. On the vertical axis, we have benefits ranging from positive to non-positive. On the horizontal axis, we have innovation ranging from incremental to disruptive.

![Choosing problems on the scale of benefits and innovation](/assets/og_image/choosing-problems.jpg "Choosing problems on the scale of benefits and innovation")

Choosing problems on the scale of benefits (vertical axis) and innovation (horizontal axis)

**Positive & incremental**: This includes improvements to existing systems (e.g., new feature columns, updating ML architecture). Such problems allow for consistent, steady progress, and solving them helps to earn trust. Sometimes referred to as *“low-hanging fruit”*.

**Non-positive & incremental**: Sometimes, we make multiple small changes that add no value but exponentially increase complexity. Can lead to *“[death by a thousand cuts](https://en.wikipedia.org/wiki/Death_by_a_thousand_cuts_(disambiguation))”*.

**Positive & disruptive**: This includes building new systems or adopting ML breakthroughs that results in positive value within the short to medium-term. *A no-brainer*.

**Non-positive & disruptive:** This requires more thought. Are we building new capabilities that multiply the team’s output, or it is a learning exercise to unlock higher-value problems? Or is it a pitfall of resume-driven development or following the HiPPO’s opinion? *Thread carefully*.

Like most 2 x 2s, this is *oversimplifying* the real-world. Nonetheless, I hope you’ll find the concepts discussed—cost-benefit analysis, capabilities, learning exercise, incremental vs. disruptive changes—useful when choosing and prioritizing your data science and machine learning problems. Have any feedback? Let me know at [@eugeneyan](https://twitter.com/eugeneyan)!

> How to choose machine learning problems?  
>   
> • Quantify costs & benefits  
> • Focus on capabilities that multiply output  
> • Do exercises that unlock higher-value problems  
> • Avoid resume driven development & pet projs  
> • Trade off incremental vs. disruptive<https://t.co/Md359mVmC3>
>
> — Eugene Yan (@eugeneyan) [March 23, 2021](https://twitter.com/eugeneyan/status/1374153418734964736?ref_src=twsrc%5Etfw)

**Thanks** to Yang Xinyi for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Mar 2021). Choosing Problems in Data Science and Machine Learning. eugeneyan.com.
> https://eugeneyan.com/writing/how-to-choose-problems/.

or

```
@article{yan2021problem,
  title   = {Choosing Problems in Data Science and Machine Learning},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2021},
  month   = {Mar},
  url     = {https://eugeneyan.com/writing/how-to-choose-problems/}
}
```

  
Share on: 

![](/assets/icon-twitter.svg)

![](/assets/icon-linkedin.svg)

![](/assets/bluesky.svg)

![](/assets/icon-facebook.svg)

![](/assets/icon-mail.svg)

---

  

Browse related tags: [
[datascience](/tag/datascience/)
[machinelearning](/tag/machinelearning/)
[leadership](/tag/leadership/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Seven Habits that Shaped My Last Decade](/writing/seven-habits-that-shaped-my-decade/)
[TalkPython - What ML can Teach Us About Life »](/speaking/talk-python/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---