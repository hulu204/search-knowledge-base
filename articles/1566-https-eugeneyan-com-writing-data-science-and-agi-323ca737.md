---
title: 'https://eugeneyan.com//writing/data-science-and-agile-what-works-and-what-doesnt/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/data-science-and-agile-what-works-and-what-doesnt/
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

# Data Science and Agile (What Works, and What Doesn't)

[
[agile](/tag/agile/)
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
[🔥](/tag/🔥/)
]
 · 13 min read

Since I last posted on moderating a panel on [Data Science and Agile](/speaking/data-science-and-agile-can-or-not-talk/), some have reached out for my views on this. This topic is also discussed among the data science community, with questions on how agile can be incorporated into a data science team, and how to get the gains in productivity.

Can agile work well with data science? (Hint: If it can’t, this post, and the [next](/writing/data-science-and-agile-frameworks-for-effectiveness/), won’t exist.)

> Follow-up: [Data Science and Agile (Frameworks for effectiveness)](/writing/data-science-and-agile-frameworks-for-effectiveness/)

> Follow-up: [What I Love about Scrum for Data Science](/writing/what-i-love-about-scrum-for-data-science/)

In this post, we’ll discuss on the strengths and weaknesses of Agile in the context of Data Science. At risk of irritating agile practitioners, I may refer to [Agile](https://en.wikipedia.org/wiki/Agile_software_development) and Scrum interchangeably. Nonetheless, do note that Scrum is an agile process framework, and there are others such as [Kanban](https://resources.collab.net/agile-101/what-is-kanban), etc. In the next post, I’ll share some agile adjustments and practices that have proven to be useful—at least in the teams I’ve led. Stay tuned!

Data science is part software engineering, part research and innovation, and fully about using data to create impact and value. Aspects of data science that work well with agile tend to be more of the engineering nature, while those closer related to research tends not to fit as well.

## What aspects of agile work well with data science?

TL; DR:

* Planning and prioritisation at the start of each sprint
* Clearly defining tasks with deliverables and timelines
* Retrospectives and Demos at the end of each sprint

## Planning and Prioritisation at the start of each Sprint

In most of my past teams, sprints are usually one or two weeks long, and we’ve found this to be a good length. Each sprint starts with a planning and prioritisation meeting which helps to align the data team with the needs of the organization.

Planning and prioritisation begins with engagement with stakeholders. Scrum provides for explicit prioritisation with stakeholders and provides the framework to have a good overview of the tasks planned (and delivered), as well as their associated complexity and effort needed. With Scrum, stakeholders have a view on their “budget” for each sprint, providing them with better context to decide on trade-offs in scope and participate in sprint planning.

Having regular planning and prioritisation meetings provide (internal and external) stakeholders a better understanding of the costs associated with each data science effort, and the overhead associated with frequently changing priorities and context switching. This ensures alignment between the data team and its stakeholders, with stakeholders being conscientious about their data effort budget, and the data team being aware of organizational needs and how they can effectively contribute.

> Such planning and prioritisation helps the data team to practice one of the seven habits of highly effective people—“First things first”.

## Clearly defining tasks with deliverables and timelines

One common issue faced by data science projects is a lack of focus, or getting derailed by investigations that go down the rabbit hole. This is partially due to the innate curiosity drives most data scientists, and partially due to the ill-defined nature of data science problems.

Defining tasks beforehand with clear timelines help to mitigate this issue. Having a clear, expected deliverable for each task aligns with one of the seven habits of highly effective people—“Begin with the end in mind”.

When approached with a new request, it helps to have the data science lead, or someone with more experience, to help define the tasks and deliverables. For example, if trying to understand why net promoter score (NPS, a measure of customer experience) went down, the expected deliverables could include analysis on various aspects of customer experience, such as:

* Delivery (e.g., timeliness, package arrival condition)
* Product (e.g., product ratings, reviews, price)
* Customer service (e.g., waiting times, number of touch points, customer service ratings)
* App metrics (e.g., spammy notifications, slow loading times, confusing UI).

This would help narrow down the causes for the drop in NPS. Next, we can assess the impact of lower NPS on the business. Do customers with lower NPS spend less (i.e., cart size, purchase frequency, absolute spend)? Are they less active on the app or have they turned off notifications? Are they at risk of attrition?

Defining these questions and hypotheses upfront provide milestones for data scientists as they conduct their analysis. In addition, sharing these tasks with the stakeholders can elicit useful information and feedback based on their expertise.

The process is similar for building data products, where most projects have a similar flow:

* Data extraction: A minimum set of denormalised data across the organization’s data sources
* Data preparation: Consistent formatting, lower cased strings, nulls filled, outliers and seldom occurring values handled.
* Feature engineering: Label/one-hot encoding, normalisation/scaling of continuous variables, various additional feature engineering
* Validation: Setting up the framework to validate (i.e., random sampling, time-based sampling); defining the right machine learning and AB testing metrics
* Machine learning: Assessing multiple models quickly, deciding the most suitable techniques, parameter tuning, more feature engineering, ensembling
* MVP and demonstration of results to stakeholders: Expected improvements to current metrics, expected effort and cost of production, roadmaps
* AB testing: Traffic splitting and sampling; sample size and power consideration, collection of AB testing results and data

The above examples only list some of the tasks required at a very high level. A natural question from stakeholders will be—“how long will it take?”. Data scientists with a few years of experience can usually give a fairly accurate estimate of the effort required. Nonetheless, this may vary based on the environment (e.g, infra, security, bureaucracy), data quality, and skills of the data scientist(s).

Take for example, the development of a data product—should it take two years? If it’ll improve organizational outcomes by 10x, perhaps. If the improvement is 10%, maybe not, though it depends. Thus, setting clear timelines before the start of the project, based on the estimated value of the project, helps set the right context for the data science team. Depending on the timeline, whether it’s 6 weeks or 6 months to build an MVP, the data science team can allocate effort to each of the steps appropriately.

## Retrospectives and Demos at the end of each sprint

Two rituals I especially enjoy are the retrospectives and demo sessions at the end of each sprint. Their aim is to help the team learn from each other, celebrate our achievements, and get feedback on how to do better for the next sprint. Considering that each takes about 30 - 60 minutes yet contribute so much to team growth, satisfaction, and well-being, they have very high return on investment (of time).

At each retrospective, the team reflects on the past week’s sprint. There are many ways on how this can be done, but here’s an approach I’ve found to work. Everyone fills up the whiteboard with points on what they found:

* Enjoyable: What aspects of the sprint and tasks did they enjoy? What were some achievements that we should celebrate?
* Frustrating: What aspects of work were frustrating? Were these challenges more of the technical nature? Or business nature? Or politics? What can we do to improve? What were the learnings from it?
* Puzzling: What puzzled you in the course of the week? Has anyone else on the team encountered it before? Are there any ideas on next steps?

> If the retrospective is done weekly, it helps the team to grow and gain from each sprint. Given a 5% improvement from each weekly retrospective, after a year, the team will be 1.05 ^ 52 = 12x better!

For the demo session, the team gets together to share significant milestones completed in the past sprint(s). It is not necessary for everyone to demo every week—usually, demos are done after a significant chunk of work, or a specific milestone, which can take anywhere between 2 - 8 weeks.

At the demo, the team can learn from each others’ experiences, as well as provide feedback. This greatly helps with team development, where a bunch of great people continuously develop and grow through learning and feedback from the people around them. This also helps to increase the [bus factor](https://deviq.com/bus-factor/), and helps more junior members of the team to level up on the more advanced methods, or gain context on the organization and data.

In addition, demos promotes accountability within the data science team, where people strive to demo something periodically. Inviting the larger organization to the demo also promotes better understanding of data science efforts and ideas on how the data team can help with the organization’s goals.

## What aspects of Agile make it hard to apply in Data Science

TL; DR:

* Data Science efforts are more ill-defined and thus more difficult to estimate
* Scope and requirements may change very quickly
* Expectations that Data Science sprints should have deliverables like engineering sprints
* Being too good/disciplined at Scrum

## Data Science efforts are more ill-defined and thus more difficult to estimate

Data science problems are ill-defined relative to engineering problems—this makes estimation harder. For example, when a problem is provided, it is not always straightforward which data should be used. Once the dataset is decided upon, how much effort is needed in data exploration, cleaning and preparation, feature engineering, assessing multiple models, and then achieving the target metric? While the process can be properly defined, the amount of effort for each task may vary greatly across projects.

Let’s assume you’re given the task of increasing conversion on an e-commerce website by improving its ranking algorithm, with a target of at least 5% increase (any less and it maybe difficult to detect through AB testing). This is a relatively large project to scope, with many uncertainties.

* Will the data be clean and conform to our assumptions, or will there be weird artefacts in the data?
* If there are issues in the data, why? Is the tracker not working correctly? Or is it due to unusual user behaviour?
* What is the impact on the analysis, and the system developed?
* How should this problem be modelled? Should it be a learning to rank problem, where products are ranked based on each category and search term?
* Or is it a classification problem based on click, or add-to-cart, or checkout?
* Or perhaps it’s a regression problem based on clicks, add-to-carts, checkouts, or revenues?
* What should the success metric be? Clicks? Purchases? Revenues? Should it be an absolute value (i.e., total purchases) or a rate (i.e., conversion rate)?

Based on the simple example above, the intent and desired outcomes are clear. However, there are multiple paths to arriving at the destination.

> The search space is large and there are many things to try, which leads to difficulty in estimating the number of experiments needed and the effort of each experiment.

## Scope and requirements may change very quickly

Due to the nature of the business, the scope and/or requirements from stakeholders may change rapidly. As the data is being explored for answers, the required analyses and solution may change as the work is being done. For example, stakeholders may have firm convictions on the cause of a problem and the required solution, but the data may suggest something else instead. As a result, the planned scope of work and tasks will have to pivot accordingly. This can be disruptive to the sprint if done too often.

Relative to software engineering, data science as a discipline is relatively younger and less mature. (Yes, some may argue that data science is just statistics—which is mature—with a sexier packaging. Perhaps this is better addressed via another essay). Software engineering is a fairly mature discipline with relatively well-defined problems and design patterns, and thus tasks that are easier to scope. Data science is younger, with problems that are harder to define, and solutions that are not as straightforward. This difference makes breaking down projects into small, well-defined tasks, more difficult.

## Expectations that Data Science sprints should have deliverables like engineering sprints

Many people familiar with agile or scrum—likely from an engineering context—expect working code at the end of each sprint. When first applying scrum to data science, most project managers try to have a well defined outcome or deliverable. In the context of engineering, this might be setting up some infra, implementing a new feature, or developing a new front-end. In these cases, there is clearly a tangible result that they can “hold in their hands” (sort of) and report upwards, such as through demonstration of the new feature or front-end.

However, in the case of data science, this gets a bit tricky. Sometimes, data science work involves analysis where someone expects an answer, or a machine learning model which contributes to measurable improvement in certain metrics. Such acceptance criteria are hard to define while scoping tasks and assigning PM tickets. Furthermore, given that data science is partly research, timeline-loving PMs may find the lack of clear deadlines disorientating. This leads to frustrated PMs where their expected outcomes are not met, and unduly stressed out data scientists who don’t have the time and space to innovate and find optimal solutions.

## Being too good/disciplined at Scrum

Is being too good at something ever a problem? Perhaps. Sometimes, when teams become very aligned with the business, and are very disciplined with meeting scrum-specific deadlines, a different kind of problem may occur.

Business stakeholders understand best which projects can immediately make an impact on users and business outcomes. On the flip side, they are usually very focused on the day-to-day, and usually more on near term goals. Having priorities set solely by the business may lead to risks of being overly focused on the short-term, and missing out on opportunities for innovation that may lead to 10x or 100x improvements.

Coupled with a data science team that is used to scrum and deadlines, this may lead to the (happy) problem of being overly focused on finishing their tasks before the sprint ends and accomplishing their story points. This appears to be productive (“Look at all the story points we completed! What a beautiful burn-down chart”) but may be deceptively ineffective—the urgent (and sometimes less important) is prioritised and executed efficiently over the important but not urgent.

The data science team has strengths in “listening to the data” and research. Applying innovation to improve organisational outcomes should be part of their mandate.

## So can Data Science be Agile or not?

“This post seems conflicting—first you tell me agile works well with data science, then you raise all the problems with it.”

Hopefully, after laying out some of the pros and cons, you’ll have a better idea of how to apply agile to data science, and the potential pitfalls. Despite some of the challenges, I believe agile and data science go well with each other—else I wouldn’t have adopted it in my past teams.

To address some of the issues raised, some simple adjustments can be made to the process and mindset—I’ll share about these in the next post. Stay tuned!

Update: This is the first post in a 2-part sharing on Data Science and Agile. In the next post, we discuss about some frameworks for effectively applying Agile to Data Science. You can find the next post [here](/writing/data-science-and-agile-frameworks-for-effectiveness/).

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jan 2019). Data Science and Agile (What Works, and What Doesn't). eugeneyan.com.
> https://eugeneyan.com/writing/data-science-and-agile-what-works-and-what-doesnt/.

or

```
@article{yan2019agile2,
  title   = {Data Science and Agile (What Works, and What Doesn't)},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2019},
  month   = {Jan},
  url     = {https://eugeneyan.com/writing/data-science-and-agile-what-works-and-what-doesnt/}
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
[agile](/tag/agile/)
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
[🔥](/tag/🔥/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« DataScience SG Meetup - Panel On the Different Roles in Data](/speaking/different-roles-in-data-talk/)
[Data Science and Agile (Frameworks for Effectiveness) »](/writing/data-science-and-agile-frameworks-for-effectiveness/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---