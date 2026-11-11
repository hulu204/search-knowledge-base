---
title: 'https://eugeneyan.com//writing/what-i-love-about-scrum-for-data-science/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/what-i-love-about-scrum-for-data-science/
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

# What I Love about Scrum for Data Science

[
[mechanism](/tag/mechanism/)
[agile](/tag/agile/)
[leadership](/tag/leadership/)
[datascience](/tag/datascience/)
]
 · 10 min read

A couple of years ago, I started (read: was made) to adopt scrum in my work.

I didn’t like it. The concept of estimation was vague to me: How do we estimate effort for data exploration or research? And after we move something from `In Progress` to `Done`, can we move it back? This happens often (in data science) where we need to revisit an upstream step, such as [data preparation](https://dataladder.com/data-preparation-guide/) or feature engineering, to improve downstream modelling.

Despite my initial concerns (and violent objections), Scrum grew on me. Now, I find it almost indispensable. Some data science folks find this unusual, so I thought I’d pen some of these views here. Specifically, I’ll discuss [time-boxed iterations](#time-boxed-iterations-speed-up-learning--limit-loss), [prio](#prioritization-gets-everyone-focused-on-the-important), [demo](#demos-boost-morale-and-promote-accountability), and [retro](#retrospectives-feedback-loop-for-improvement).

**But first, a disclaimer: I’m no Agile expert.** I don’t have proper training on Agile or a Scrum certificate. Also, we modified Scrum so it worked for us, thus it’s likely different from conventional Scrum–what works for you might be different too.

Aside: Primer on Scrum vs. Kanban

Scrum is organised in sprints, usually 1 - 2 weeks each, with the goal of shipping each sprint; Kanban operates on continuous delivery and release. I’ve added resources at the end that have a more in-depth discussion.

![Scrum for Data Science (vs. Kanban)](/assets/scrum-vs-kanban.webp "Scrum for Data Science (vs. Kanban)")

With Kanban, you continuously pick up tasks from the board. With Scrum, you iterate in sprints.

## Time-Boxed Iterations Speed Up Learning & Limit Loss

A common issue in data science projects is getting derailed by trips down the rabbit hole of research and premature optimization: The model would perform better if we had *that* data. Should we try a different technique? Or add more layers? Or build an ensemble—yeah, ensembling rocks!

There’s *always* something.

**However, research and improving model performance—on its own—doesn’t serve customers**. It needs to be implemented, integrated, and deployed. *Then*, we can measure how much it helps customers and the organization. Here’s where time-boxing shines. Each iteration has a clearly defined deliverable and a bounded timeline. This helps the team make progress towards the finish line and not get lost in the woods.

Aside: What are DS Deliverables?

They don’t have to be the same as regular engineering deliverables; I mean, they can be, but they don’t have to. Engineering-oriented tasks and deliverables are relatively straightforward and definitely achievable. They kinda look like this:

* Develop an ETL job
* Create a feature store
* Develop an inference API

On the other hand, research-oriented tasks have a more open problem space and a higher chance of failure:

* Explore if our data can solve this problem
* Research ML approaches to achieve this metric
* Improve click-thru rate and conversion

For some engineering PMs, these research-oriented tasks can take some getting used to. These tasks can lead to non-positive outcomes such as:

* We don't have the right data now
* We cannot achieve the desired metric
* The A/B test was not positive

While such “failures” make it seem like there was no progress, IMHO, the learning (from research and experimentation) *is* the deliverable.

> "I haven't failed–I've just found 10,000 that won't work." - Thomas Edison

**I apply time-boxing like how I would have a budget for bets, especially research-oriented ones.** At the start, we might bet one or two iterations to figure out the problem space. If it results in “The target metric is 95% accuracy; we achieved 85%”, we can double down. But if the gap is too wide to close—with a reasonable amount of resources—we might choose to move on.

**Time-boxed iterations provide for regular check-ins and feedback**, as well as a way to limit loss—think of it as a [stop-loss](https://www.investopedia.com/terms/s/stop-lossorder.asp). It makes clear how many bets you can make in a year. Or if you’re a start-up with limited runway, how many bets you have remaining.

## Prioritization Gets Everyone Focused on The Important

[Zen of Python](https://www.python.org/dev/peps/pep-0020/) line 2: `Explicit is better than implicit.` This is what we try to achieve with sprint “prio”, which involves representatives from the business and the data team.

**For our stakeholders, prio gives them a say on the importance and urgency of each task**. This ensures alignment between business goals and our data science efforts. It gives stakeholders transparency on the effort for each task, which helps to earn trust. They also become aware of the costs involved with frequently changing priorities and context switching, and generally try to tone it down.

**Each business function has a budget** (i.e., data science effort) they can allocate to their projects. Prio makes clear that—with limited resources—not everything is important and urgent. And changing priorities mid-sprint is gonna cost ya. Sometimes, business leaders *deliberately* remove tasks (from their backlog) to set constraints on their own team.

> “Deciding what not to do is as important as deciding what to do.” - Steve Jobs

For the data team, **prio provides good input and feedback**. Business leaders have strong intuition on which efforts will move the needle most, and which are simply a waste of time. Through prio (and further interactions), this intuition rubs off on the data team. Over time, we gain the ability to quickly cut to the crux of the data science (and business) problem.

Perhaps more importantly, **prio ensures alignment**. The data team is made aware of organizational needs and the associated level of urgency. This discipline prevents distraction by the “latest and greatest” tech or fun ideas that may not be essential.

Also, we learn that, sometimes, deploying something that’s 80% done in one - two months is 10x better than deploying something 99% done in *six* months. It can even be a matter of keeping the lights on, due to sudden policy changes (e.g., GDPR) or events (e.g., COVID-19).

Aside: Estimations, what about that?

Truth be told, I still haven’t fully figured it out. You would expect that estimation error (i.e., `actual - estimated`) has a normal distribution. But in reality, it has a fat long tail. A two-week estimate is more likely to take two months than two days. (Welp, I guess we can’t use [linear regression as errors are not homoscedastic](https://en.wikipedia.org/wiki/Linear_regression#Assumptions).)

![Scrum for Data Science (Estimation errors)](/assets/estimation-vs-actual.webp "Scrum for Data Science (Estimation errors)")

5-10% of the time, estimation errors fall in the long tail which really wreaks the iteration.

Nonetheless, estimations are useful in prioritization. If someone needs a project done in two weeks but we estimate it at 2 - 3 months effort, it’s a clear non-starter. I treat estimations like projected spending and time boxes as hard budgets. (*Please*, don’t take estimations as deadlines carved in stone; see previous paragraph.)

(Note: Past estimates and actuals are useful in guiding future estimates. Do we always underestimate certain tasks (e.g., data acquisition)? What was the actual effort required?)

## Demos Boost Morale and Promote Accountability

**People enjoy demos**. Both giving and attending them. Demo-ers are excited to show (off) their work—hey, they take pride in it! Demos are also a venue to get feedback and suggestions for improvement. I’ve seen many types of demos, including:

* Visualisations on interesting, useful data
* Research and experimentation numbers
* Prototypes with basic UI
* Log tracing to isolate a bug or performance bottleneck
* New infra capabilities (e.g., Docker for model rollbacks)

**Demos also promote accountability**. The teams I’ve been in operate with high [autonomy and responsibility](https://www.slideshare.net/eugeneyan/culture-at-lazada-data-science-80794046#13): We trust everyone to do our best work and don’t micromanage. (This is similar to [Netflix’s Freedom and Responsibility](https://jobs.netflix.com/culture#freedom-and-responsibility).)

> “With great freedom comes great responsibility.” - Uncle Ben Parker (maybe)

What winds up happening is members striving to give regular demos—peer pressure perhaps? That said, it’s not necessary for everyone to give a weekly demo. Demos are usually done after a chunk of work or milestone, which usually happens every 2 - 8 weeks.

The entire organization has an open invite to data science demos. For the most part, we have to lure them with 🍻 beer, 🍕 pizza, and 🍿 chips. But when they show up, they understand better what we do in our geek cave. Sometimes, ideas are sparked, leading to new initiatives and collaboration.

**Finally, demos increase the team’s [bus factor](https://en.wikipedia.org/wiki/Bus_factor).** A better understanding of one another’s work increases the [data replication](https://hadoop.apache.org/docs/r1.2.1/hdfs_design.html#Data+Replication) of tribal knowledge. It’s also a great way for new members to get up to speed on what the team is doing, as well as gain context on data science initiatives and data.

## Retrospectives: Feedback Loop for Improvement

**Retrospectives provide an open and safe venue for team feedback**. It’s simple—just divide a whiteboard into three sections: `Enjoyable`, `Frustrating`, and `Puzzling` and you’re good to go. We reflect on the past sprint and list aspects of our work or events that fall into those buckets. Often, multiple people face the same issue and we just `+1` it.

![Scrum for Data Science (Retrospectives)](/assets/retrospective2.webp "Scrum for Data Science (Retrospectives)")

Celebrate the enjoyable, follow-up and resolve the frustrating and puzzling.

The `Enjoyable` bucket is often used to celebrate wins and express gratitude. We also share improvements to our workflow (e.g., “no meetings from x - y o’clock ”) or infra (e.g., “more Hadoop nodes, yay!”). I find that, often, these enjoyable tasks have an element of challenging people’s abilities and helping them grow.

The `Frustrating` and `Puzzling` buckets contain challenges and feedback that leaders should pay close attention to. They’re often non-technical (e.g., “Too many meetings!”, “Not enough innovation!”). Puzzling issues may require help from the team to deep dive the root cause (e.g., “Our DB chokes every couple days though restarting it solves the issue”). Disciplined follow-up on these feedback beats back the entropy that creeps in over time.

## What Are The Downsides to This?

**Yes, there’s some cost associated with what I’ve mentioned.** Prio takes an hour, demos take an hour (often more, as people have so much to share), and retros take 30 - 60 mins. That’s about 3 - 4 hours each iteration. IMHO though, the resultant benefits of alignment, learning, and continuous growth *far* outweigh the cost.

> Better to move in the right direction, albeit slower, than fast on the wrong path.

I’ve also gotten feedback that time-boxing can constraint data science and innovation. I acknowledge this; it won’t work in all teams (e.g., academia, research-focused.) It does well in [lean start-up](https://en.wikipedia.org/wiki/Lean_startup) environments though, where we have to quickly figure out what works for consumers (and Mr Market).

From experience, **it’s *really difficult* to estimate the impact of a new model or improved features.** Users may not take to that sophisticated hybrid recommender. Half the time, something that took three months—or even three weeks—had more impact than a year-long project. Yeap, that’s a coin toss—thus, I prefer to *toss the coin more often.*

## Conclusion

At first glance, it seems awkward to apply Scrum to data science. However, I’ve grown to enjoy certain aspects of it, and seen how it helps teams to stay focused, ship, and grow. Hopefully, this essay has convinced you a bit.

If you’re a Scrum Master reading this, you might not consider this “true” Scrum. I accept that. But hey, as the [Agile Manifesto](https://agilemanifesto.org) suggests—People over Process. *Adapt it so it works for your team and you.*

## Further reading

* [Kanban vs. Scrum (Atlassian)](https://www.atlassian.com/agile/kanban/kanban-vs-scrum)
* [Agile vs Scrum vs Waterfall vs Kanban (smartsheet)](https://www.smartsheet.com/agile-vs-scrum-vs-waterfall-vs-kanban)
* [What is Scrum (scrum.org)](https://www.scrum.org/resources/what-is-scrum)
* [Scrum (Wikipedia)](https://en.wikipedia.org/wiki/Scrum_(software_development))
* [Kanban (Wikipedia)](https://en.wikipedia.org/wiki/Kanban_(development))
* [Does scrum ruin great engineers or are you doing it wrong?](https://stackoverflow.blog/2020/06/29/does-scrum-ruin-great-engineers-or-are-you-doing-it-wrong/)

**Thanks** to Yang Xinyi, [Stew Fortier](https://stewfortier.com/), [Dan Hunt](https://danhunt.com/), [Joel Christiansen](https://joelchristiansen.com), and [Compound](https://wehuddleup.typeform.com/to/ZILDKb) for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jun 2020). What I Love about Scrum for Data Science. eugeneyan.com.
> https://eugeneyan.com/writing/what-i-love-about-scrum-for-data-science/.

or

```
@article{yan2020scrum,
  title   = {What I Love about Scrum for Data Science},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Jun},
  url     = {https://eugeneyan.com/writing/what-i-love-about-scrum-for-data-science/}
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
[agile](/tag/agile/)
[leadership](/tag/leadership/)
[datascience](/tag/datascience/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« How to Apply Crocker's Law for Feedback and Growth](/writing/how-to-apply-crockers-law-for-feedback-and-growth/)
[What I Do Before a Data Science Project to Ensure Success »](/writing/what-i-do-before-a-data-science-project-to-ensure-success/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---