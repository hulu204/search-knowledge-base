---
title: 'https://eugeneyan.com//writing/mechanisms-for-projects/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/mechanisms-for-projects/
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

# Mechanisms for Effective Machine Learning Projects

[
[mechanism](/tag/mechanism/)
[machinelearning](/tag/machinelearning/)
[productivity](/tag/productivity/)
]
 · 7 min read

How can we improve a machine learning project’s chance of success? Over the years, I’ve explored various [mechanisms](https://docs.aws.amazon.com/wellarchitected/latest/operational-readiness-reviews/building-mechanisms.html) in both my own projects and those of my team members. Most people who tried these mechanisms ended up adopting them in future projects.

While these mechanisms were developed with machine learning projects in mind, with a few tweaks, they can be applied to other technical endeavors too.

## Pilot and co-pilot

If your team is like most teams I’ve been on, you have 2 - 3 problems for every available person. Thus, each member works on 1 or 2 problems simultaneously, with some folks taking 3 or more. And because everyone’s so busy, we barely have time to check in on each other’s projects outside of standup, planning, retrospective, etc.

This is an anti-pattern. It can lead to a project going off-track for months, or a critical error (e.g., incorrect training data, invalid train-validation split) going undetected until late in the implementation phase.

One solution is to **have a pilot and copilot for each project.** The pilot is the main project owner and is in charge of its success (or failure). They own and delegate the work as required though they’re usually responsible for the bulk of design and critical code paths.

**The copilot helps the pilot stay on track, identify critical flaws, and call out blindspots.** This includes periodic check-ins, reviewing document drafts and prototypes, and being a mandatory code reviewer. For example, the copilot should challenge the pilot if the proposed design doesn’t solve the business problem, or if the train-validation split is invalid. To be able to spot these issues, the copilot typically has experience in the problem space, or has more experience in general, similar to how senior engineers guide juniors.

For every 10 hours the pilot spends on the project, the copilot can expect to spend an hour on reviews (10% of the pilot’s effort). While this may seem excessive, copilots have helped avoid costlier rework or abandoning a project due to mistakes that snowballed.

Pilots and copilots don’t have to be from the same job family. As an applied scientist, I often partner with an engineer who helps with infrastructure, observability, CI/CD, etc. If both scientist and engineer are sufficiently experienced, they can double up as each other’s copilot. As they review each other’s work, knowledge transfer occurs organically and they learn to be effective copilots for other engineers or scientists in future projects.

Also read more on the dangers of flying solo by [Ethan Rosenthal](https://www.ethanrosenthal.com/2023/01/10/data-scientists-alone/) and [Vicki Boykis](https://vickiboykis.com/2021/08/05/the-local-minima-of-suckiness/).

## Literature review

In my earlier projects, because I was overeager, I would immediately jump into the data and begin training models. After watching me go in the wrong direction for a week or two, a merciful senior would share a paper, casually suggesting that it might be helpful to read it. It always was. After letting this happen once too often, I finally learned to start my projects with a literature review.

For a literature review, I **read papers relevant to the problem**. I’m biased towards [solutions that have been applied in industry](https://github.com/eugeneyan/applied-ml) though more academic papers have also been helpful.

While reading these papers, I’m less interested in model architecture and focus on:

* How the problem was framed: If it’s fraud detection, is it framed as a classification problem (fraud vs. no fraud) or regression problem (quantum of fraud)? Or is it framed as an [anomaly detection problem to be solved via unsupervised learning](/writing/notes-from-sparkai-summit-application-specific/#preventing-abuse-via-unsupervised-learning-24-june)?
* How input data was processed: How was data excluded, preprocessed, and rebalanced? How were labels defined? Was a [third neural class](/writing/search-query-matching/#neutral-third-class) added? How were labels augmented, perhaps via [hard mining](/writing/search-query-matching/#hard-mining)?
* How the model was evaluated offline: How was the training and validation set created? What offline evaluation metrics did they use? How did they [improve the correlation between offline and online evaluation metrics](/writing/recsys2022/#offline-online-correlation)?

To quickly go through the papers, I adopt the [three-pass approach](/writing/why-read-papers/#how-to-read-papers).

## Methodology review

This is **similar to a code review but for machine learning prototypes and experiments**. Once I have initial experiment results, I schedule a review with fellow scientists to ensure I haven’t overlooked any blindspots or committed critical errors.

During the review, I focus on understanding the methodology and the potential of the current approach. Some questions include:

* Input data and features: Am I using data that would not be available during inference? For example, if I’m [predicting hospitalization costs during pre-admission](/speaking/machine-learning-in-healthcare/), am I peeking into the future and using features such as length of hospitalization? If so, it’s a data leak as we won’t know the length of stay in advance and it’s highly correlated with hospitalization cost.
* Offline evaluation: If we’re building a forecast model, are we splitting data by time or just randomly? The former ensures we don’t learn on future data while the latter is invalid. (Most production uses cases should have data split by time.)
* Room for improvement: What’s the theoretical best result achievable (e.g., allow the model to overfit by training and inferring on the same data)? How much improvement can we expect from more data based on [learning curves](https://scikit-learn.org/stable/auto_examples/model_selection/plot_learning_curve.html#sphx-glr-auto-examples-model-selection-plot-learning-curve-py)?

To conduct methodology reviews asynchronously, like a code review, we could adopt a tool like DagsHub which supports [comments on Jupyter notebooks](https://dagshub.com/OperationSavta/SavtaDepth/src/main/Notebooks/SavtaDepth_Colab.ipynb) and [data](https://dagshub.com/nirbarazida/CheXNet/src/95c86c28ffe16ee646659ab180f61a40cfd0195d/data_labeling/data/images_001/images/00000007_000.png).

## Timeboxing

To tie it all together, we **timebox each project phase and task**. Time constraints help us focus on the most important tasks and not get bogged down in the details. Timeboxing for machine learning projects can be challenging, because compared to engineering projects, the work is relatively ill-defined. Furthermore, a large part of the work is research and experimentation which unfortunately leads to many a dead end.

But it’s because of these challenges that timeboxing is effective—**how much effort should we invest before pivoting?** In most industry settings, we don’t have limitless resources to pursue a problem for years.

(I treat timeboxes differently from estimates. Timeboxes are stretch goals while estimates are project management inputs that indicate the [upper bound of effort needed](https://erikbern.com/2019/04/15/why-software-projects-take-longer-than-you-think-a-statistical-model.html). To convert timeboxes to estimates, I usually multiply by 1.5 - 3.0.)

Here are three ways to define timeboxes.

The first—and most aggressive—approach is to take the time spent on similar projects and halve it. This forces us to be scrappy and build a minimum lovable product that we can quickly get feedback on, reducing the iteration cycle. This approach works well in startups and startup-like teams though it can be too intense to adopt all the time.

A less extreme approach is to set a timebox that is “comfortable yet challenging”. Thus, instead of halving the timebox, we reduce it by 10 - 20%. By deliberately introducing these constraints, we give ourselves the opportunity to reflect on timesinks to avoid and how to achieve more with fewer resources. This is a good default for most seasoned teams.

Finally, for greenfield projects that may be hard to scope, we can adopt standard timeboxes. For example, we might allocate two weeks for a literature review, four to eight weeks to build a prototype, and three to six months to implement it in production.

• • •

I’ve also written about other mechanisms for machine learning projects, including:

* [One-pagers](/writing/what-i-do-before-a-data-science-project-to-ensure-success/#first-draw-the-map-to-the-destination-one-pager) to clarify the intent (why) and constraints and outcomes (what)
* [Design documents](/writing/ml-design-docs/) to get feedback on the methodology and system design (how)
* [Making prototypes reproducible](/writing/why-you-need-to-follow-up-after-your-data-science-project/#make-your-work-reproducible-each-run-every-run) to avoid wasting time on retracing steps

What mechanisms do you adopt in your machine learning projects? Please share below!

**Thanks** to Yang Xinyi for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jan 2023). Mechanisms for Effective Machine Learning Projects. eugeneyan.com.
> https://eugeneyan.com/writing/mechanisms-for-projects/.

or

```
@article{yan2023projects,
  title   = {Mechanisms for Effective Machine Learning Projects},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2023},
  month   = {Jan},
  url     = {https://eugeneyan.com/writing/mechanisms-for-projects/}
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
[machinelearning](/tag/machinelearning/)
[productivity](/tag/productivity/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Goodbye Roam Research, Hello Obsidian](/writing/roam-to-obsidian/)
[Mechanisms for Effective Technical Teams »](/writing/mechanisms-for-teams/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---