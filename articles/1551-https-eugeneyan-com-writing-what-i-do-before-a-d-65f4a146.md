---
title: 'https://eugeneyan.com//writing/what-i-do-before-a-data-science-project-to-ensure-success/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/what-i-do-before-a-data-science-project-to-ensure-success/
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

# What I Do Before a Data Science Project to Ensure Success

[
[mechanism](/tag/mechanism/)
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
]
 · 12 min read

When someone comes to me with a data science problem, I’m always rushing to dive in. Let’s explore some data, build something cool, create positive impact! Yeah… I’m impatient like that, though I like to view it positively as bias for action.

After working on a couple of projects, I started to wonder: Is this *really* faster? Was there a better way? I reflected on my work and realised that I lost time on things like:

* Climbing the wrong hill
* Using a bazooka when a fly swatter will do
* Going down rabbit holes and dead-ends

To fix this, I put in place three pre-project tasks for myself. Some team members also tried it and found it useful. Here, I’ll share about the [one-pager](#first-draw-the-map-to-the-destination-one-pager), [time-box](#then-budget-the-time-and-effort-time-box), and [breakdown](#break-it-down-to-spot-rabbit-holes-and-dead-ends).

> This is part one (before) of a three-part series on data science project practices. Also see [part 2 (during)](/writing/what-i-do-during-a-data-science-project-to-ensure-success/) and [part 3 (after)](/writing/why-you-need-to-follow-up-after-your-data-science-project/).

## First, Draw The Map To The Destination (One-Pager)

The map covers the intent, desired outcome, deliverable, and constraints.

### Intent (Why?)

What’s the problem we’re trying to solve, or the opportunity we want to gain from? How will customers benefit? *Why* are we doing this, and *why* is it important?

> “Management is doing things right; leadership is doing the right things.” - Peter Drucker

Often, we get so excited about building something—anything—that we don’t stop to ask “Why?”. We just assume that it’s a good idea to build it. But, by taking the time to think through the problem and intent, we might realise that, hey, maybe we don’t need to fix it after all. Perhaps it only affects very few customers who are likely to churn anyway. Or that opportunity for a virtual-reality shopping mall kinda stinks. Either way, we’ve nipped needless projects in the bud.

Aside: “Working Backwards” vs. “Build It And They Will Come”

Amazon’s [”Working Backwards”](https://www.quora.com/What-is-Amazons-approach-to-product-development-and-product-management/) is a great way to identify the intent, and understand “Why?”. It starts by working backwards from the customer, and how they will benefit. This is distilled in a (mock) press release for customers. If the benefits don’t come across as interesting or exciting, back to the drawing board.

![Ideal Data Science Workflow Working Backwards](/assets/working-backwards-s3.webp "Ideal Data Science Workflow Working Backwards")

Working Backwards Press Release for AWS S3

Contrast this with “Build it and they will come”. It makes for a good [movie quote](https://www.quora.com/Where-does-the-phrase-If-you-build-it-they-will-come-come-from-What-does-it-mean) but is actually pretty bad advice for product and tech. I know I’m often guilty of starting with some sexy idea or shiny new tech, building it, then trying to bolt customers on it.

What happens if customer’s *don’t* come? That’s a lot of effort down the drain. Start-ups with limited resources can’t afford this.

An unclear problem and intent also leads to another difficulty: How do we decide which solution is better? How do we know if we’re successful? By writing it down, we now have a point of reference. This can be used to compare across problems when prioritising, as well as to compare across solutions when designing.

### Desired Outcome (What?)

Now that we have the intent, we can discuss how success looks like. How well should we solve this problem? How do we measure it? In data science, this is usually a business metric such as conversion, savings from fraud reduction, net promoter score, etc.

> “If you can’t measure it, you can’t change it.” - Peter Drucker

With unlimited resources, we can solve any problem completely. But, we don’t have unlimited resources. Specifying the desired outcome, in quantifiable terms, prevents us from falling into the trap of chasing a moving target. We know when we’re past the finish line.

It also helps us decide which projects to pursue. Solving a problem to 95% could take 3-4x the effort of solving to 90%; solving to 99% might take 10-100x more. Given our limited resources (let me know if you have *unlimited* resources), we’ll likely choose not to pursue a problem that requires 99% accuracy (e.g., clinical diagnosis)—this lets us invest in something else more worthwhile.

### Deliverable (How?)

Now, we can design a deliverable that meets the intent and desired outcome. How should we solve this problem? The solution should be designed to meet the intent and desired outcome, keeping in mind the need to integrate with the existing system.

For example, an e-commerce platform has the intent of improving how customers discover and purchase products. To achieve this, should we improve search? Or recommendations? Or email campaigns? If it’s a recommender, how will we deploy it? Will it be a cache that’s updated daily? Or a service that accepts customer and/or product as input and returns a set of recommendations?

This doesn’t have to be especially detailed; for now, we don’t need the full architecture and specs. But it’s useful to have a rough sketch to get upfront buy-in from the business, product, and tech teams. We don’t need a deliverable, with all the bells and whistles, that doesn’t deliver results. We don’t want to build a real-time, multimodal, deep learning recommender that *cannot* be integrated. Be sure to get feedback on this.

### Constraints (How not?)

How *not* to solve a problem is often more important than how to solve it. Unfortunately, this doesn’t get addressed enough.

Providing teams with boundaries and constraints counterintuitively leads to greater creativity and freedom. Without constraints, we don’t know what we cannot do. Thus, we thread gingerly with incremental improvements. In contrast, with clear constraints, we know that we can do *anything except breach the constraints*—this is liberating and can lead to disruptive innovation.

Aside: Boundaries vs. Constraints

What’s the difference between boundaries and constraints?

![Boundaries vs Constraints](/assets/boundaries-vs-constraints.webp "Boundaries vs Constraints")

Keep within the boundaries; keep out of the constraints.

**Boundaries enclose or limit something**, such as the scope of a solution. For example, we might decide that our recommender will not be real-time for the first iteration. This boundary makes clear what we should *not* consider and *frees* us to focus on a recommender with daily updates.

**Constraints restrict or limit something from changing**, such as business metrics. For example, if we’re deliberately introducing new, cold-start products in search, the constraint could be “not reducing conversion by more than 5%”. This constraint *frees* us to consider ideas that could lead to a conversion drop of 0 - 5%.

While they’re technically different, I refer to them interchangeably.

Here’s a short story to illustrate a business constraint. Previously, I was given the goal of introducing new products on our search and category pages. The intent was to increase their (i.e., new product) impressions, CTR, and conversion.

The obvious way to do this is to spam search results with new products, without considering customer experience (like a search engine with *only* ads) and overall business metrics. The other extreme is to err on the side of caution with insignificant changes (e.g., one new product a day); this will have no practical impact on the business *and the goal*. Both approaches would have been suboptimal.

Thankfully, I was given a single **business constraint** to work with: “Don’t reduce conversion by more than 5%”. This provided a “budget”, as well as freedom to experiment within the constraint. As a result, we were able to ship a working solution quickly. (Note: While we expected conversion to decrease, [A/B testing](https://www.slideshare.net/eugeneyan/how-lazada-ranks-products-to-improve-customer-experience-and-conversion/37) showed that it *actually* increased, albeit non-significantly.)

**Technical constraints** are common when building machine learning systems for production. Front-end would likely have *latency* limits of under 50-100ms, as well as throughput requirements (e.g., `x` concurrent requests). We might have to adhere to a certain interface, schema, or format that consumers expect.

We might also be faced with **resource constraints**. Data science and machine learning pipelines can be compute and memory intensive. Model retraining might be required to complete in `x` hours given a cluster of `y` machines. This sets boundaries on how resource-hungry our pipelines can be, helping us focus on building something that can be deployed in production.

> “Constraints drive innovation and force focus. Instead of trying to remove them, use them to your advantage.” - 37Signals (now Basecamp)

### One-pager (Medium)

We write the intent, desired outcome, deliverable, and constraints in simple language on a single-paged document. This can be shared to stakeholders for their review, feedback, and buy-in. Doing this goes a long way to making sure that what we build will be used and was worth the effort.

This requires a certain amount of discipline from stakeholders. After all, the work comes at no cost to them. There’s nothing stopping them from changing their minds halfway through the project. However, a compelling intent and clearly defined outcomes and deliverables mitigates this risk.

Writing one-pagers is now a must-do for me (though I may not circulate them). I often get lost in the woods of research, experimentation, and development. It’s too easy to get distracted by shiny new research and tech, or forget how it’s supposed to benefit the customer. Revisiting the one-pager has always gotten me back on track.

## Then, Budget The Time and Effort (Time-Box)

Most projects start with a solution, then come up with estimates for each component and the overall design. I never understood this—it’s like writing a blank cheque.

I tend to do the opposite. Given a budget (read: time-box), how can we design a solution that fits? The intent and desired outcome determine the time-box, and the time-box determines the solution design. This is how Basecamp does it too—they have different [appetite](https://basecamp.com/shapeup/1.5-chapter-06#ingredient-2-appetite) for various problems, and scope the solutions accordingly.

More important and difficult problems should have bigger time-boxes. Between a $10 million problem and a $100 million one, the latter should get more resources and a bigger time-box. Smaller time-boxes can do with solutions with simpler techniques (e.g., regression, decision trees), freeing up effort for bigger problems that require more sophisticated solutions (e.g., deep learning).

The time-box will vary across the project stages. At the start, when we’re still exploring and uncertainty is high, we’ll want tighter time-boxes to limit wild goose chases. Once there’s more certainty of going into production, we can allocate bigger time-boxes.

> “Work expands to fill the time available for completion.” - Parkinson’s Law

Usually, we start with a **feasibility assessment**. With our existing data and technology, are we able to solve the problem? If so, to what extent? In this stage, we aim for a quick and dirty investigation. I usually time-box this at 1-2 weeks.

After determining feasibility, we proceed with a **proof of concept** (POC). In this stage, we *hack* together a prototype to assess if our solution is technically achievable. Ideally, we also test the integration points with upstream data providers and downstream consumers. Can we meet the technical constraints (e.g., latency, throughput)? Is model performance satisfactory? This usually takes a month or two.

If all goes well, we then **develop for production**. We’ll want to time-box this too. An overly generous timeline can lead to non-essential features being squeezed in and never-ending development—without actually deploying it, no one benefits from it. This usually takes 3-6 months, including infra, job orchestration, testing, monitoring, documentation, etc.

(Note: I’m hesitant to put numbers for each stage above as it *really* depends on the project and organization. Nonetheless, having them gives a sense of the relative effort I would invest in each.)

Here’s how the stages could look like (from a previous [post](/writing/data-science-and-agile-frameworks-for-effectiveness/)).

![Time-boxed Iterations](/assets/time-boxed-iterations.webp "Time-Boxed Iterations")

We gradually increase time-boxes as certainty increases.

## Break it Down to Spot Rabbit Holes and Dead-Ends

Having the one-pager and time-box improves a project’s chances of success. Usually, it’s sufficient. Nonetheless, it can be helpful to **break it down**, especially if it involves unfamiliar data or technology. The aim is to identify possible **rabbit holes** and **dead-ends** early and reduce time wasted on them.

Working with a new data source? Check-in with a DBA to understand the data integrity and how often it refreshes. No point retraining your model intraday if the data source only updates at midnight. Considering a new technology for big data processing? Consult senior data engineers on the potential challenges and blockers.

> “Foresight is not about predicting the future, it’s about minimizing surprise.” - Karl Schroeder

Ideally, the breakdown indicates which components are harder to implement or more at risk—these usually involve things we’ve not done before. We want to front-load the *risk* and start with these *scary* bits first. If a key component cannot be implemented, we should know sooner rather than later, before investing and completing the rest of the project.

When breaking it down, I often consult seniors with more expertise and experience. They usually have better intuition on potential gotchas and blockers that deserve more attention. If you’re the most senior, it’s still good to have a fresh pair of eyes look through the breakdown and identify things you might have missed. Knowing where the rabbit holes are and how to avoid them has saved me significant time in the execution phase.

## It’s Additional Thinking But It Saves Effort

This may seem like unnecessary, additional work. But it doesn’t take a lot of time, and I would argue that it reduces the total work done.

Hammering out a one-pager usually takes 1-2 days, a week at most. In fact, the *more* time you spend on the one-pager, the *more* time you *save*. Requiring more time indicates the problem and ideal solution is still unclear—starting to build now leads to wasted effort.

Similarly, proper time-boxing ensures we invest prudently on a solution based on the size of a problem. Spotting rabbit holes and dead-ends early helps us avoid them and reduces effort wastage.

*Haste makes waste.* I trust you’ll find that these habits save time *and* increase the likelihood of success. Let me know how it goes below.

**Thanks** to Yang Xinyi for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jun 2020). What I Do Before a Data Science Project to Ensure Success. eugeneyan.com.
> https://eugeneyan.com/writing/what-i-do-before-a-data-science-project-to-ensure-success/.

or

```
@article{yan2020planning,
  title   = {What I Do Before a Data Science Project to Ensure Success},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Jun},
  url     = {https://eugeneyan.com/writing/what-i-do-before-a-data-science-project-to-ensure-success/}
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
[mechanism](/tag/mechanism/)
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« What I Love about Scrum for Data Science](/writing/what-i-love-about-scrum-for-data-science/)
[Why Are My Airflow Jobs Running “One Day Late”? »](/writing/why-airflow-jobs-one-day-late/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---