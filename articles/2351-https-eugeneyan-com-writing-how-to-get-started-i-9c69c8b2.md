---
title: 'https://eugeneyan.com//writing/how-to-get-started-in-data-science/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/how-to-get-started-in-data-science/
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

# How to get started in Data Science

[
[datascience](/tag/datascience/)
[learning](/tag/learning/)
[career](/tag/career/)
]
 · 9 min read

More than a handful of times have I been asked about how to get into the field of data science. This includes SMU’s Master of IT in Business classes, regular meet-ups (e.g., [DataScience SG](https://www.meetup.com/en-AU/DataScience-SG-Singapore/), and requests via email/linkedin. Though the conversations that follow differ depending on the person’s background, a significant portion is applicable to most people.

I’m no data science rockstar. Neither am I an instructor that teaches how to get into data science. Nonetheless, here’s some previously shared advice on “How to get started in Data Science”, documented here so it can be shared in a more scalable manner.

## What this post will (not) cover

This post will focus on the tools and skills (I find) essential in data science, and how to practice them. Every organization has different needs, and what’s listed is largely based on Lazada’s data science stack and process. Nonetheless, they should be applicable to most data science positions. These should be viewed as minimum thresholds, and they do not necessarily predict success in data science. They are:

* Tools: SQL, Python and/or R, Spark
* Skills: Probability and Statistics, Machine Learning, Communication
* Practice: Projects, Volunteering, Speaking and Writing

This post will not cover character traits, personalities, habits, etc. While there are some traits I find strongly correlated with success in data science (e.g., curiosity, humility, grit), we will not discuss them here. In some sense, these traits lead to success in all roles/life—not just data science.

## Tools and how to pick them up

### SQL

This is the bread and butter of every data (science) person, and will probably be for a long time. While there are GUI tools that allow querying and extracting data without writing SQL, they are often not as powerful and flexible. Writing SQL allows you to join/filter/aggregate data as you wish, and the query can be easily shared with reproducible results. Learning 20% of what SQL can do should cover 80% of what you’ll need in day-to-day tasks—the rest can be googled when needed.

Some sites provide an in-browser SQL engine, providing immediate feedback and making learning easier. Here are some I found useful:

* [w3schools](https://www.w3schools.com/SQL/deFault.asp) (step-by-step tutorial on basic SQL commands)
* [sqlzoo](https://sqlzoo.net/) (more practice and assessments on SQL)

### Python / R

While SQL is sufficient for basic analysis (using filters, aggregates, etc), you’ll soon need to do more such as statistical analyses, visualisations, machine learning, etc. Python and R have rich libraries that simplify these complex tasks. Some example libraries, for Python and R respectively, include:

* Data processing (pandas, dplyr)
* Visualization (bokeh, ggplot2)
* Machine Learning (scikit-learn, caret)

Here’s some MOOCs to pick up basic Python:

* [Interactive programming in Python](https://www.coursera.org/learn/interactive-python-1) by Coursera & Rice (introduction to the basic elements of Python programming; browser-based programming environment)
* [Introduction to Computer Science and Programming using Python](https://www.edx.org/course/introduction-to-computer-science-and-programming-7) by Edx & MIT (stepping stone to using python to tackle useful problems)

Here’s some MOOCs to pick up basic R:

* [R Programming](https://www.coursera.org/learn/r-programming) by Coursera & Johns Hopkins (introduction programming in R)
* [Introduction to Probability and Data](https://www.coursera.org/learn/probability-intro) by Coursera & Duke (the basics of R, and how to sample and explore data)

### Spark

Eventually, you’ll work with data that is unable to fit on your local machine, be it RAM or disk. To efficiently process this data, we’ll turn to distributed processing frameworks such as MapReduce. One open-sourced data processing engine that is popular is Apache Spark.

Technologies come and go, and Hadoop/Spark is no exception (though they’ll probably be around for a while). With regard to learning Spark, I find it more useful to understand the concepts of distributed storage and processing. Learn how map and reduce tasks work across distributed nodes, which actions are parallelizable and which are not. Learn about shuffle and when it occurs, and how to minimise shuffle to make jobs more efficient.

Here’s some MOOCs to pick up basic Spark:

* [Introduction to Apache Spark](https://www.edx.org/course/introduction-to-apache-spark) by EdX & Berkeley (basic Spark architecture):
* [Big data analysis with Apache Spark](https://www.edx.org/course/big-data-analysis-with-apache-spark) by EdX and Berkeley (data analysis in Spark)
* [Databricks education materials and tutorials](https://docs.databricks.com/getting-started/training-faq.html)

## Skills and how to pick them up

### Probability, statistics, and experimental design

Part of a data scientist’s role is to distinguish signal from noise and provide data-driven insights to solve problems. Probability and statistics help you find trends and insights that are significant (e.g., fashion items shown on white background, as opposed to a lifestyle background, have higher conversion).

These insights may lead to website/app changes (e.g., converting all fashion items to have a white background). As far as possible, these changes should be AB tested by showing the different versions to similar users and measuring metrics such as click-thru and conversion. For this, you’ll need valid experimental design and the right statistical analyses.

Here’s some MOOCs to pick up basic probability, statistics, and experimental design

* [Inferential statistics](https://www.coursera.org/learn/inferential-statistics-intro) by Coursera & Duke (commonly used inferential methods for numeric and categorical data)
* [Statistical Inference](https://www.coursera.org/learn/statistical-inference) by Coursera & Johns Hopkins (broad overview of statistical inference)

### Machine learning

Most people think data scientists spend 80% of their time on machine learning. My experience is the opposite—80% of the time is spent engaging with stakeholders, acquiring/preparing/exploring data, putting models into production while 20% is spent on machine learning.

Nonetheless, though machine learning is only 20% of time spent, it enables data scientists to solve problems in an automated and scalable way. For example, instead of having people manually categorize products, we can build a machine learning classifier to do it automatically, saving time, effort, and cost.

Here’s some MOOCs to pick up machine learning:

* [Machine learning](https://www.coursera.org/learn/machine-learning) by Coursera & Stanford (Andrew Ng’s famed course; one of the few that touch on gradient descent)
* [Statistical learning](https://online.stanford.edu/courses/sohs-ystatslearning-statistical-learning) by Stanford online (Machine learning from a statistical perspective)

### Communication (speaking and writing)

For data scientists, it is important to communicate findings and data products in a simple and clear manner. Most of the time, stakeholders will not have the statistical and machine learning know-how that you do—they require your help to simplify and reframe the outcomes.

Their main question will be: “How will this help me?”—you should answer this simply. While it’s amazing that you’ve created a model with excellent AUC / logloss (which they will not understand), they will not use it if you cannot demonstrate how it helps them.

My approach to improving communication has been to practice, practice, practice—which brings us to the next point.

### Practice

After completing a few MOOCs, you may find yourself yearning to practice your skills in a real world environment. Practice makes permanent—your brain’s neurons are more linked together through repeated use. Practicing and applying often allows your brain to strengthen the learned material. Here are some suggested avenues for practice.

### Start your own project

My mission is to use data to create positive impact and improve lives. To gain practice with building data products end-to-end, I built a [product classification API](/writing/product-categorization-api-part-3-creating-an-api/) using data scrapped from Amazon’s website, deployed it on AWS, and developed a frontend accessible via datagene.io.

> Update: API discontinued to save on cloud cost.

Throughout the process, I learnt a lot beyond what is normally taught in schools / MOOCs. For example, I learnt how to set up and deploy an API on AWS EC2, build a simple web app using Flask, and develop basic, user-friendly HTML pages. Specific to data, I learnt how to work with large data sets efficiently (the data was 12gb and I restricted myself to only using Python as a challenge) and how to clean real-world dirty data (yes, even Amazon has dirty data).

Eventually, I also learnt how to apply deep learning to images for [classification](/writing/image-categorization-is-now-live/) and [search](/writing/image-search-is-now-live/).

As a bonus, I ended up with a simple portfolio to demonstrate what I’ve built.

### Volunteer with NGOs

[DataKind](https://www.datakind.org/) is an NGO that helps other NGOs use data more effectively. I had the opportunity to volunteer with [DataKind SG](https://www.meetup.com/en-AU/DataKind-SG/) on one of its DataDives (similar to a 2-day hackathon).

The DataDive involved helping HOME (Humanitarian Organization for Migration Economics). HOME works for the well-being and empowerment of migrant workers in Singapore. During the DataDive, we worked on anonymising the data, creating our own data dictionaries, and data cleaning and visualisation, with the aim of answering the questions HOME had of its data.

At the end of day two, HOME had a better understanding of the migrant worker situation in Singapore, and how they could improve their operations. We also built a simple self-service dashboard so they could discover insights themselves, making the benefit from the DataDive a sustainable one.

The experience was a mini project end-to-end. You get an opportunity to work with stakeholders and real-world messy data, create social impact, and learn lots from fellow do-gooders.

 

### Speak and write

In Singapore (and most countries), there are [meet-ups](https://www.meetup.com/en-AU/) organised regularly where you can share, and gain experience in public speaking. Similarly, there are plenty of blogging sites such as wordpress, medium, etc where you can write articles and gain practice. As you work on projects, maintain a site for your writing journaling your progress and results, as well as a git repo that people can refer to.

Volunteer to write your organization’s data newsletter, or to speak at a meetup conference. I don’t think there’s a shortcut to this—but if you know of any, please let me know! From my experience, the way to getting better is to practice.

## Conclusion

And there you have it. Simple guidelines on how to get started in data science: Three tools, three skills, and three avenues for practice.

Please let me know if you found this guide useful, and if you have any suggestions for improvement. Feedback on my writing and content is also most welcome.

P.S., here’s what I shared at SMU’s MITB last year.

 
  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jun 2017). How to get started in Data Science. eugeneyan.com.
> https://eugeneyan.com/writing/how-to-get-started-in-data-science/.

or

```
@article{yan2017start,
  title   = {How to get started in Data Science},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2017},
  month   = {Jun},
  url     = {https://eugeneyan.com/writing/how-to-get-started-in-data-science/}
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
[learning](/tag/learning/)
[career](/tag/career/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« OMSCS CS6476 (Computer Vision) Review and Tips](/writing/omscs-cs6476-computer-vision/)
[SMU Masters in IT - How to get started in Data Science »](/speaking/how-to-get-started-in-data-science-talk/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---