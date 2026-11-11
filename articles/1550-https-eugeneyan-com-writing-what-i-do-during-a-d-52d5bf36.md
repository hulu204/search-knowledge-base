---
title: 'https://eugeneyan.com//writing/what-i-do-during-a-data-science-project-to-ensure-success/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/what-i-do-during-a-data-science-project-to-ensure-success/
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

# What I Do During A Data Science Project To Deliver Success

[
[mechanism](/tag/mechanism/)
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
]
 · 7 min read

> ”A vision and strategy aren’t enough. The long-term key to success is execution. Each day. Every day.” – Richard M. Kovacevich

Having a solid [project plan](/writing/what-i-do-before-a-data-science-project-to-ensure-success/) (and [development workflow](/writing/setting-up-python-project-for-automation-and-collaboration/)) is half the battle won. However, execution can be tricky–it’s easy to lose sight of the goal or be lured by the sirens of shiny tech and sexy research. Here are some common pitfalls:

* Unnecessarily reinventing the wheel and tinkering too much on research
* Poor team communication and alignment and not asking for help
* Building something users don’t need or want (the worst and *most common* issue)

To keep myself on track and execute effectively, I tried a variety of practices and habits. Here, I’m sharing those that worked best with you.

> This is part two (during) of a three-part series on data science project practices. Also see [part 1 (before)](/writing/what-i-do-before-a-data-science-project-to-ensure-success/) and [part 3 (after)](/writing/why-you-need-to-follow-up-after-your-data-science-project/).

## Research What Others Have Done (And What Worked)

Before designing a solution, I usually **start with a literature review**. How have other people framed the problem? What data did they use? What worked (and didn’t work)?

The intent is to *quickly* identify approaches that *have* worked and build on them. It doesn’t have to be exhaustive; a week of research is usually enough. For example, when I was researching about how to [build a product classifier](/writing/product-categorization-api-part-1-data-acquisition-and-formatting/), I found the following papers helpful:

* [High-precision phrase-based document classification](https://engineering.linkedin.com/research/2011/high-precision-phrase-based-document-classification-on-a-modern-scale) (`LinkedIn`)
* [Large-scale item categorization for e-commerce](https://dl.acm.org/doi/10.1145/2396761.2396838) (`DianPing`, `eBay`)
* [Chimera: Large-Scale Classification using ML, Rules, and Crowdsourcing](http://pages.cs.wisc.edu/~anhai/papers/chimera-vldb14.pdf) (`Walmart`)

I learnt how other teams had cracked the problem and the results they achieved. The Chimera paper showed that manual labelling and hand-crafted rules helped to bootstrap the data and system before machine learning was introduced. The hard-won lessons from the papers informed much of my system’s design.

Working based on others’ research doesn’t mean we can’t, or won’t, do innovation of our own. It’s just the first step towards an MVP we can quickly test with customers. Once we know we’re on the right track, we can do further in-house research.

> Here’s my repository of [`applied-ml`](https://github.com/eugeneyan/applied-ml) papers, articles, and videos. I’d be grateful if you add other relevant materials or simply leave a star 😊

## Experiment and Iterate Quickly

After we’ve surveyed the landscape of how to frame the problem and possible solutions, we’ll want to iterate through them quickly. This means **running quick, albeit scrappy, experiments** to assess for feasibility and narrow the search space.

I’ve found Jupyter notebooks to be a great balance of code, documentation, and results. Combined with a [simple experimentation workflow](https://github.com/eugeneyan/papermill-mlflow) (using `jupyter`, `papermill`, and `mlflow`), we can quickly evaluate and record baselines for each approach.

## Stand-ups and EODD for Alignment and Feedback

IMHO, **[stand-ups](https://martinfowler.com/articles/itsNotJustStandingUp.html) are essential for starting a productive day right.** They only cost 15 minutes but have so many benefits: alignment, communication, an avenue to get feedback and help. I’ve had stand-ups with varying cadences, from daily to twice a week, and they all work well to keep the team aligned.

Here’s a scenario: At today's stand-up, you mention that you’re planning to start building the data pipeline. However, you’re unaware that the datastore is not ready; starting your task now would lead to indecipherable errors and wasted effort. Thankfully, you’re informed of this blocker during stand-up. Thus, you plan to work on some other task instead, and circle back to the data pipeline when you’re unblocked.

Stand-ups help the team to work efficiently together. They are especially useful now with everyone working from home and not having spontaneous synchronous communication.

Aside: Stand-up dos and don’ts

Stand-ups are a regular affair and without conscious effort, bad habits may creep in over time. I find the following to be useful reminders:

* Do listen to what the team is saying and if someone needs help; don’t rehearse what you’re planning to say.
* Do raise challenges; don’t let someone report on the same task daily without offering help.
* Do be kind to people new to stand-ups; don’t make judgements on velocity or what’s not important to share about.

**Standard engineering stand-ups can be a formal, rushed process**—15 minutes and people will want to jump into deep work right after. As a result, newer or more junior members may hesitate to ask for help during stand-ups, or even during the rest of the day when everyone seems so busy.

To mitigate this, **I introduced the end-of-day debrief (EODD)**. Relative to stand-ups, EODD is optional and has a more informal nature. Despite being informal, we have a fixed calendar slot. The team is often so busy with meetings or work, especially the senior folk, that EODD gets deprioritized—a fixed slot signals its priority. Similar to stand-ups, the cadence is flexible though I suggest a minimum of once a week

![End-of-day debrief](/assets/eodd.webp "End-of-day debrief")

End-of-day debriefs are meant to be casual. No preparation required, 100% feedback & learning.

I’ve found teams to enjoy EODD (and external teams enjoy listening in too). The time is often used to share unusual findings, bounce a crazy idea, get help on a persistent bug, or ask for a methodology review (though this may require a follow-up deep dive). It comes across almost like office hours.

Despite being an informal, no preparation, meeting, the impact on the team is significant. Idea collaboration happens more often, bugs get fixed faster, methodology flaws are prevented, and knowledge is transferred. For data science teams, the discussion and review nature of EODD complements the engineering nature of stand-ups.

## Stakeholder Check-ins to Align on Business Goals

As we make progress, it’s good habit to **check-in with stakeholders regularly** to keep them updated. Check-ins ensure our work and eventual deliverable is aligned with the overall customer needs and business goals.

Stakeholder check-ins are also a useful source of feedback. When I share about data irregularities and how I’m cleaning it, stakeholders often drop valuable insider knowledge and suggest clever fixes—these greatly reduce effort and accelerate progress.

**Demos are a great check-in format.** I find that having a simple app is the best way to helping users understand what the deliverable is–when there’s an app they can use and interact with, everything becomes clear. Setting up a simple [Flask](https://flask.palletsprojects.com/en/1.1.x/) app (or more recently, [FastAPI](https://fastapi.tiangolo.com/)) doesn’t take too long but goes a long way in getting concrete feedback.

Aside: Internal tech-team demos

Other than stakeholder demos, people look forward to internal tech team demos too (including the person giving the demo). At internal tech demos, we can discuss the nitty-gritty details and results, and get technical feedback.

Here’s an example of possible demos when building a recommender system:

* [Preparing the data and building the train-val set](/writing/recommender-systems-baseline-pytorch/#parsing-json)
* [Building a baseline: Methodology and results](/writing/recommender-systems-baseline-pytorch/#implementation-1-matrix-factorization-iteratively-pair-by-pair)
* [Improvements on the baseline: What worked and what didn’t](/writing/recommender-systems-graph-and-nlp-pytorch/#implementation-3-node2vec)

## Adopt What Works Well For Your Team

Those are the simple practices that have worked for me and my teams–I’m confident they’ll work for you too. If I had to suggest, start with having literature reviews before designing solutions, as well as a weekly end-of-day debrief. They’re simple to implement and provide high return on time invested.

Above all, pick and adapt these practices to fit your team’s existing culture and cadence—[people over process](https://agilemanifesto.org/). Let me know how it goes in the comments below.

> ”A vision and strategy aren’t enough. The long-term key to success is execution. Each day. Every day.” – Richard M. Kovacevich  
>   
> How do we deliver consistently, while avoiding the pitfalls of reinventing the wheel or building ML systems users don't want? <https://t.co/XMXGWgb954>
>
> — Eugene Yan (@eugeneyan) [July 15, 2020](https://twitter.com/eugeneyan/status/1283208709334691840?ref_src=twsrc%5Etfw)

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jul 2020). What I Do During A Data Science Project To Deliver Success. eugeneyan.com.
> https://eugeneyan.com/writing/what-i-do-during-a-data-science-project-to-ensure-success/.

or

```
@article{yan2020project,
  title   = {What I Do During A Data Science Project To Deliver Success},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Jul},
  url     = {https://eugeneyan.com/writing/what-i-do-during-a-data-science-project-to-ensure-success/}
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

[« How to Update a GitHub Profile README Automatically](/writing/how-to-update-github-profile-readme-automatically/)
[Why You Need to Follow Up After Your Data Science Project »](/writing/why-you-need-to-follow-up-after-your-data-science-project/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---