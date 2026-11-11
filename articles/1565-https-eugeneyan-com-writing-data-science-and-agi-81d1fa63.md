---
title: 'https://eugeneyan.com//writing/data-science-and-agile-frameworks-for-effectiveness/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/data-science-and-agile-frameworks-for-effectiveness/
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

# Data Science and Agile (Frameworks for Effectiveness)

[
[mechanism](/tag/mechanism/)
[agile](/tag/agile/)
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
]
 · 14 min read

This is the second post in a 2-part sharing on Data Science and Agile. In the last post, we discussed about the aspects of Agile that work, and don’t work, in the data science process. You can find the previous post [here](/writing/data-science-and-agile-what-works-and-what-doesnt/).

> Follow-up: [What I Love about Scrum for Data Science](/writing/what-i-love-about-scrum-for-data-science/)

## A quick recap of what works well

**Periodic planning and prioritization**: This ensures that sprints and tasks are aligned with organisational needs, allows stakeholders to contribute their perspectives and expertise, and enable quick iterations and feedback

**Clearly defined tasks with timelines**: This helps keep the data science team productive and on track, and being able to deliver on the given timelines — the market moves fast and doesn’t wait.

**Retrospectives and demos**: Retrospectives help the team to improve with each sprint, and provide feedback and insight into pain points that should be improved on. Demos help the team to learn and get feedback from one another. If stakeholders are involved, demos also provide a view into what the data science team is working on.

## What about aspects that don’t work well?

**Difficulty with estimations**: Data science problems tend to be more ill-defined, with a larger search space for solutions. Thus, estimations tend to be tricker with a larger variance in error. One way around this is to have budgets for story-points / man days, and to time-box the experiments.

**Rapidly changing scope and requirements**: The rapidly evolving business environment may bring with it constantly changing organizational priorities. To mitigate this, have periodic prioritisations with stakeholders to ensure alignment. This also helps stakeholders better understand the overhead cost of frequent context switching.

**Expectations for engineering-like deliverables after each sprint**: Project managers and senior executives with an engineering background might expect working software with each sprint. This may require some engagement and education to bring about mindset change. While the outcome from each sprint may not be working code, they are also valuable (e.g., experimental results, research findings, learnings, next steps).

**Being too disciplined with timelines**: A happy problem is being too efficient and aligned with business priorities. Nonetheless, a data science team should be working on innovation. To take a leaf out of Google’s book, a team can build in 20% innovation time. Innovation is essential for 10x improvements.

## How to adapt Agile for Data Science

In light of the points discussed above, how can we more effectively apply agile/scrum to data science?

Here, I’ll share some frameworks/processes/ideas that worked well for my teams and I — hopefully, they’ll be useful for you too. Namely, they are:

* Time-boxed iterations
* Starting with Planning and Prioritisation, Ending with Demo and Retrospective
* Writing up projects before starting
* Updated mindset to include innovation

## Time-boxed Iterations

![Time-boxed Iterations](/assets/time-boxed-iterations.webp "Time-Boxed Iterations")

One framework I find helpful is “time-boxed iterations”. The focus is on having various iteration phases within each project, and within each iteration, ideas and outcomes are validated to a satisfactory level before moving to the next iteration.

This ensures consistent feedback at each stage of the project, especially at the early stages where things are most uncertain. The worst thing that can happen is spending significant time and resources on a project and finding that it is not what stakeholders really needed (because most people can’t articulate what they really need). Or that it will not be adopted/used. In addition, having time-boxed iterations prevents R&D endeavours from becoming a blackhole.

Let’s go through each of the four stages listed above.

### Feasibility Assessment

This is where we engage with stakeholders early on to clarify the problem statement, intent, deliverables, and constraints. Once there is sufficient clarity on the context, the data science team can then begin to assess if the problem can be solved by existing data.

If it can be solved by the existing data, what level of performance can we expect? For example, if the problem is product classification, is the ballpark estimate at 50% precision, or 90%? These initial metrics make a big difference to the usability of the product — 50% would make it hard to use, though still significantly better than a random guess, considering thousands of categories.

> The main question in this stage is: Given the existing data, are we able to get a reasonable level of performance? Should we expend more resources on it?

Let’s assume the desired accuracy level is 95%. If the ballpark estimate is 90%, with some time and effort, we might be able to achieve 95% accuracy. However, if the ballpark estimate is 70% (and a 25% gap is pretty big in data science), perhaps we should move the project to the backlog and work on steps to improve performance. This could involve additional data collection, transfer learning, research, etc.

Usually, this step can be done fairly quickly, in about 2–4 weeks, assuming it is an in-house project and familiarity with the data.

### Proof of Concept (POC)

If the initial performance from the feasibility assessment was satisfactory, we move on to developing a POC. This involves building a minimum viable product (MVP) to demonstrate technical feasibility. The aim is to have working code and machine learning model(s) to validate the initial idea and implementation.

Validation can be done either via local validation, or AB testing, and the results shared with stakeholders to gather feedback on the level of performance.

> The main question here: Is this good enough to expend additional resources to into production? Does it meet the performance requirements (e.g., model performance, latency, etc.)?

Depending on the POC outcomes, we’ll decide whether or not to (i) deploy to production and iterate, or (ii) refine the POC further (because we’re so close), or (iii) revisit the project another time because the gap between a usable product and the existing MVP is too wide.

With an experienced team, the POC could be wrapped-up in about 4–8 weeks, depending on the complexity of the project.

### Deploy to Production

If everything has been going well so far, great! Next, we get to put our solution into production where it can make real impact. This usually involves working with data engineering (which may help with scheduling, scaling, monitoring, etc.) and the core engineering team for integration into the platform.

Code should be refactored to optimise for maintainability, performance, scalability, and robustness. Invest time to develop automated test cases and documentation, so others can easily learn about and understand the project, as well as contribute features and maintenance effort.

Deployment to production can take anywhere from 3–9 months, depending on several factors include infrastructure (e.g., on premise or cloud), technical performance requirements, security, etc.

Some laymen, eager for results, might ask: “Don’t we have a working POC already? Why not just deploy that into production? Why do we need to spend more time?” Production-quality code focuses on resilience, maintainability, extensibility, scalability, etc. These aspects can be costly.

> A software engineer, with experience at Google, Microsoft, Amazon, and Oracle, shared on Quora that a research prototype took 2 man-months, while a production-quality version required 117 man-months. That’s approximately 60x more time!

### Operational Maintenance

Lastly, after deploying into production, the data product will require some effort maintaining it, as well as new features/models requested.

The size of this effort depends on the complexity of the product, as well as the amount of tech debt (which can come with hasty deployments, poor design, etc.).

Overall, the entire process from business request to production could take between 6–12 months.

The framework emphasises on frequent check-ins with organisational stakeholders, ensuring that the data product developed is aligned with the organizational needs and allow for stakeholder feedback. There are also two major checkpoints, (i) feasibility assessment and (ii) POC outcomes, where the critical “go-ahead” decision is needed before the escalation of commitment and resources. Taken together, this helps ensure alignment with the organization.

## Starting with Planning and Prioritisation, Ending with Demo and Retrospective

There are rituals I find very useful (and enjoy) at the start and end of each sprint. These are likely already part of your existing agile practices, though I thought it would be good to emphasise them.

At the start of each sprint, it is important to go through planning and prioritisation.

Planning involves the data science team organising their tasks and effort based on the organization needs and priorities. Given the high level intent and deliverables, how can it be broken down into scoped tasks with estimates? Anything more than 2 days of effort should ideally be broken down further. I often plan for slightly more than achievable by the team for each sprint, before going to stakeholders for prioritization.

In prioritization, each task is assigned a level of importance/urgency. This is sometimes done with stakeholder involvement. When stakeholders are involved, it provides them with a clearer picture of the effort expended on their requests. In addition, they can provide their input and feedback, or suggest different ideas and approaches.

Then at the end of each sprint, we have the demo and retrospective — this is especially enjoyable.

Demos allow the team to share checkpoints and achievements in their past sprint(s). This provides for learning across the whole team, increasing your bus factor. In addition, this provides an opportunity for the rest of the team to provide feedback on one another’s work, leading to improvements.

> Lastly, the team has a chance to “show off” their pride and joy from the past sprint(s), and have everyone celebrate team achievements, which is highly motivating.

After that, we also have a retrospective which provides a chance for everyone to take stock of current sprint. What went well? What didn’t? How can we improve? The team learns and gains from each demo and retrospective, making the next sprint slightly more effective and efficient.

## Writing up projects before starting

I highly encourage team members to begin each project by spending some time planning the project and writing it up.

Putting words into a document helps to clarify one’s thoughts, especially when the ideas and projects are nebulous.

The document also acts as a map that one can refer to at any time to ensure that the project is on track. Here’s a standard template that I find useful:

* What is the problem or opportunity?
* What is the intent?
* What is the desired outcome and/or success metric?
* What is the deliverable?
* What are the benefits?
* What are the dependencies and constraints?

First, always start with the current situation — what is the problem or opportunity? Is there an existing approach to address it? What is the current performance level? Is the problem one where data and data science can help with? For example, it could be that an e-commerce website is currently classifying new products manually.

> Assuming each person can classify 2,000 products daily, with a target of adding 1 billion new products in a year, this translates to 500 thousand man days (or 2,000 people assuming 250 working days a year). This is clearly a bottleneck to scaling.

Next, from stakeholders, what is the high-level intent? With this intent, we can better understand the goal (i.e., the “what”), and the data science team can identify the best way (i.e., the “how”) to achieve it. In this case, the intent would be scale the number of products that can be added to the platform through automation.

Then, based on this intent, what is the direct desired outcome? Phrased differently, what is the success metric, if there is one pre-defined? This provides a target that guides the team through the time-boxed iteration process (see above). For example, if the intent is to automate product categorisation, some specific numbers could be 95% top-3 precision and recall with a latency of classifying 40 products per second. This latency would lead to classification of 1 billion products in 290 days. This may not be sufficient given the peaks and troughs of products being added — one way to get around this to scale horizontally (i.e., multiple APIs processing in parallel).

Given the intent, desired outcome, and success metric, what is the deliverable? Here, the data science team will brainstorm various approaches to meet the intent. Perhaps it could be an API that is integrated into the platform where sellers can upload their products. Would having a batch mode be useful and adopted? What product fields are available to build our classifier (e.g., title, image, attributes, etc.)? In this case, the deliverable could be an API that takes in product fields and returns the top-three most likely categories. This API can be exposed to both internal and external users.

With this deliverable, what are the downstream benefits to the business? This is essential for building the business case and helping the organization to see the value of the data product, and thus invest resources in it. In the case of an automated product classifier, one downstream benefit could be reduced manpower costs for product classification. You can get a good estimate based on the number of products each person can process per hour, and the hourly wage cost.

> Assuming that 90% of 1 billion products can be automatically classified, how much manpower is saved?

In addition, reducing the lead-time between product upload and going live on the site is a key metric for seller experience and making the seller platform more self-service.

Next, are there any dependencies for this project? For example, are there specific integration points, such as the product database, or the interface where sellers update their products? Are there also certain requirements for the data and model refresh frequency in order for the model to stay up-to-date and maintain acceptable performance?

Lastly, what are the constraints for the data science effort? One possible constraint would be the language (e.g., Python, Java, Scala, Go). What languages are supported? What are the frameworks allowed for use? Is distributed computing available? What is the maximum latency tolerable of the API developed? How much compute and memory is available per API server? These are some of the key questions that would determine the architecture of the final solution developed.

Having the above points thought through beforehand will provide clarity on the rest of the project. It doesn’t mean you need to have all the answers before starting on the project. What it means is that you should have thought through the process, end-to-end, and figured out the key questions before starting — at least then you know what are “known unknowns”. As suggested in the seven habits of highly effective people — “Begin with the end in mind”.

## Updated Mindset to include Innovation

There is no clear template or approach I can proposed for this.

It could begin with a conversation with senior leadership on the mandate of the data science team, which should include innovation. Once the mandate is secured with a (manpower) budget for innovation, it is important to have a program with proper accountability.

> For example, innovation projects could be allocated 2–3 weeks quarterly. They should be directly linked to a desired outcome, with downstream benefits to the organization. This helps with getting buy-in for the project as well.

Members involved should have a deliverable on sharing their learnings, outcomes, and proper code and documentation for these projects. This helps enforce accountability, and documentation helps others pick up the project easier, or when we have to revisit the project after a couple of months.

## Key Takeaways

Whew, that was a long post (and read). Thanks for staying with me so far.

Overall, Agile is a good framework to apply in the context of data science, with benefits that we can directly gain from. Though there are some aspects that may not be suitable, there are some adaptations that can be made to make it more applicable for data science teams and projects.

> The key thing to remember is that the most important thing is generating valuable work, be it working and accurate models, innovation and new approaches with 10x improvements, or learnings from failed experiments.

If adopting agile and making certain (other) adjustments help your team with achieving their goals, so be it. Don’t let it constrain the team from doing valuable work and fulfilling their potential.

With this, I end with the Agile Manifesto.

![Agile Manifesto](/assets/agile-manifesto.webp "Agile Manifesto")

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Feb 2019). Data Science and Agile (Frameworks for Effectiveness). eugeneyan.com.
> https://eugeneyan.com/writing/data-science-and-agile-frameworks-for-effectiveness/.

or

```
@article{yan2019agile3,
  title   = {Data Science and Agile (Frameworks for Effectiveness)},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2019},
  month   = {Feb},
  url     = {https://eugeneyan.com/writing/data-science-and-agile-frameworks-for-effectiveness/}
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
[datascience](/tag/datascience/)
[productivity](/tag/productivity/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Data Science and Agile (What Works, and What Doesn't)](/writing/data-science-and-agile-what-works-and-what-doesnt/)
[DATAx - A Production ML system for SEA's Biggest Hospital Group »](/speaking/machine-learning-largest-hospital-group-talk/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---