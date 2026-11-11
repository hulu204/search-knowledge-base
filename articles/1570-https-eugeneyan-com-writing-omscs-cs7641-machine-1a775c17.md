---
title: 'https://eugeneyan.com//writing/omscs-cs7641-machine-learning/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/omscs-cs7641-machine-learning/
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

# OMSCS CS7641 (Machine Learning) Review and Tips

[
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[machinelearning](/tag/machinelearning/)
[python](/tag/python/)
]
 · 4 min read

> You might also be interested in this [OMSCS FAQ](/writing/georgia-tech-omscs-faq/) I wrote after graduation. Or view all OMSCS related writing here: [`omscs`](/tag/omscs).

I haven’t had time to write the past few months because I was away in Hangzhou to collaborate and integrate with Alibaba. The intense 9-9-6 work schedule (9am - 9pm, 6 days a week) and time-consuming OMSCS Machine Learning class ([CS7641](https://omscs.gatech.edu/cs-7641-machine-learning)) left little personal time to write.

Thankfully, CS7641 has ended, and the Christmas holidays provide a lull to share my thoughts on it.

## Why take this class?

Why take another machine learning course? How will it add to my experience in applying machine learning on real world problems?

Truth be told, I am victim to imposter syndrome. Most of my machine learning knowledge and skills are self-taught, based on excellent MOOCs including those by [Andrew Ng](https://www.coursera.org/learn/machine-learning/) and [Trevor Hastie and Rob Tibshirani](https://online.stanford.edu/courses/sohs-ystatslearning-statistical-learning). CS7641 provided an opportunity to re-visit the fundamentals from a different perspective (focusing more on algorithm parameter and effectiveness analysis).

![Impact of the C parameter on SVM's decision boundary](/assets/svm-decision-boundary.webp "Impact of the C parameter on SVM's decision boundary")

Impact of the C parameter on SVM's decision boundary

Additionally, CS7641 covers less familiar aspects of machine learning such as randomised optimisation and reinforcement learning. These two topics were covered at an introductory, survey level, and provided sufficient depth to understand how these algorithms work, and how to apply them effectively and analyse outcomes.

![Effectiveness of randomised optimisation algorithms on the travelling salesman problem (randomised hill climbing, simulated annealing, genetic algorithm, MIMIC)](/assets/random-optimization.webp "Effectiveness of randomised optimisation algorithms on the travelling salesman problem (randomised hill climbing, simulated annealing, genetic algorithm, MIMIC)")

Effectiveness of randomised optimisation algorithms on the travelling salesman problem (randomised hill climbing, simulated annealing, genetic algorithm, MIMIC)

## What’s the class like?

There are 2 - 3 hours of lectures weekly, largely consisting of Charles Isbell and Micheal Littman taking turns to “teach” each other various machine learning topics. Lectures are interspersed with occasional jokes and word puns, keeping them humorous (if you’re a geek like me).

There are four assignments covering: (i) supervised learning, (ii) unsupervised learning and dimensionality reduction, (iii) randomised optimisation, and (iv) reinforcement learning. Peers complained about the lack of clarity on assignment requirements. Those without machine learning background felt they were thrown into the deep end and had no inkling how to start. Expectedly, assignment grades averaged around 40 - 60, though it improved slightly with each assignment. Assignments made up 50% of the overall grade. Expect to spend 40 - 60 hours per assignment.

Exam-wise, there is a mid-term and a (non-cumulative) final, each 25% of overall grade. These were difficult and required one to have an in-depth and intuitive understanding of the material to do well. The median for the mid-term was 51 and 59 for the final. We had 90 minutes for the mid-term (which was barely sufficient) and 180 minutes (and fewer questions) for the final—most people finished the final early.

Across previous semesters, about 40% of students dropped out. Of the remaining, about 60% received an A, while most of the rest received a B. If you’re planning to take CS7641, persevere past the mid-term and you should receive a passing grade. Assignments are 50% of the overall grade—start on them early to do well. They require more research, analysis, visualisations, and writing than a regular paper. Assignments focused more on demonstrating understanding and in-depth analysis of algorithm effectiveness, and less on coding up algorithms from scratch.

## What did I learnt?

For supervised and unsupervised learning, I gained deeper fundamental understanding of how each type of algorithm worked. This included why each performed better on different datasets, why some overfit less, why some require more data, etc. Much of the learning came from visualising algorithm effectiveness across varying amounts of data, parameters, types of problems, etc. I gained increased rigour in analysing algorithm effectiveness, and how to thoughtfully apply different algorithms to different problems.

CS7641 also provided good exposure to randomised optimisation and reinforcement learning techniques. These were new to me and the class provided sufficient depth to determine whether to invest additional time on them. Personally, I enjoyed reinforcement learning, its temporal nature, and how learns on new data points in the “exploration” (vs “exploitation”) phase.

![Effectiveness of reinforcement learning algorithms on a simple grid world](/assets/reinforcement-learning.webp "Effectiveness of reinforcement learning algorithms on a simple grid world")

Effectiveness of reinforcement learning algorithms on a simple grid world

## What’s next?

With the increased rigour gained in analysing algorithm effectiveness, I aim to apply it to my work in Lazada, to do more analysis and gain greater intuition on algorithm outcomes. I will also share the knowledge gained, to help the team improve on their understanding and analysis on algorithm effectiveness.

In addition, I aim to reinforce my learning on reinforcement learning (haha), and take the reinforcement learning class (CS7641, also by Charles and Micheal) next term. I’ve heard many good reviews about it—can’t wait!

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Dec 2017). OMSCS CS7641 (Machine Learning) Review and Tips. eugeneyan.com.
> https://eugeneyan.com/writing/omscs-cs7641-machine-learning/.

or

```
@article{yan2017machine,
  title   = {OMSCS CS7641 (Machine Learning) Review and Tips},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2017},
  month   = {Dec},
  url     = {https://eugeneyan.com/writing/omscs-cs7641-machine-learning/}
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
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[machinelearning](/tag/machinelearning/)
[python](/tag/python/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« My first 100 days as Data Science Lead](/writing/my-first-100-days-as-data-science-lead/)
[INSEAD Lunchtime Talks - How Lazada uses Data »](/speaking/insead-how-lazada-uses-data-talk/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---