---
title: 'https://eugeneyan.com//speaking/machine-learning-in-healthcare/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//speaking/machine-learning-in-healthcare/
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

# DataTalksClub - Building an ML System; Behind the Scenes

[
[machinelearning](/tag/machinelearning/)
[production](/tag/production/)
]
 · 5 min read

This week, I had the opportunity to give a behind the scenes tour of building a machine learning system for Southeast Asia’s largest hospital group, at the DataTalks.Club conference. The video is available below. We’ll discuss a few key points in this post.

• • •

## Overall design: From data to endpoint, and back to data

![Image](/assets/datax-healthtech.jpg "Design of the machine learning system")

Design of the machine learning system, from data to model endpoint.

The grey dashed line (on the left) separates the hospitals’ environment from ours. Hospitals store the data, include patient, doctor, and case information. This data is periodically extracted, encrypted, and transported to our [SFTP server](https://www.ipswitch.com/resources/best-practices/sftp-server). We then decrypt, validate, and store the raw, unstructured data (e.g., CSVs, parquet files, etc.) in our [staging area](https://en.wikipedia.org/wiki/Staging_(data)). The raw data is then parsed and stored in our [RDBMS](https://en.wikipedia.org/wiki/Relational_database).

The data science workflow reads the data (from the tabular databases) and puts it through the pipeline, including data preparation, feature engineering, machine learning, and model validation. (For more details, please view the talk.)

The trained model is stored in our model store. Models can take various formats, such as [pickle](https://docs.python.org/3/library/pickle.html) files, library-specific formats (e.g., [PyTorch](https://pytorch.org/tutorials/beginner/saving_loading_models.html)), or [Docker](https://www.docker.com) images that include serving code. These models are then pushed to the publishing server, which versions and deploys the models. Model versioning lets us easily rollback model deployments, providing an insurance policy (in case a deployment goes awry).

Each hospital has a unique model endpoint and stores the predictions received (we also log these predictions on our end). This completes the entire cycle and provides a feedback loop to validate and improve model performance.

Logging and monitoring is done via the [ELK](https://www.elastic.co/what-is/elk-stack) stack, orchestration via [Airflow](http://airflow.apache.org), and endpoint publishing via [Jenkins](https://www.jenkins.io). Implementation was done in Python and deployed on [Azure](https://azure.microsoft.com/en-us/) (a common cloud provider used by healthcare organizations in Southeast Asia).

## Most prod systems should use time-based validation

![Image](/assets/datax-validation.jpg "The difference between a random-split and a time-based split")

The difference between a random-split and a time-based split.

In most production systems, our data will have a strong temporal aspect. Thus, using random train-test split or cross-validation will give an overly optimistic result. This was especially so in our data where many patients had more than one visit, and a random split might lead to using *future* hospital visits to predict *past* hospital visits. Thus, a time-based split should be used instead.

There are exceptions to this though. For example, a product classifier which categorizes products based on image or text (e.g., title, description). The relationship between the images/text and product classification is likely stable over time. Thus, there probably isn’t much difference between a random-split or a time-based split.

![Image](/assets/datax-validation2.jpg "Data leaks if we're not using a time-based validation split.")

Data leaks happen if we're not using a time-based validation split.

## Miscellaneous tips and key takeaways

During the Q&A, the conference organizer, Alexey, chimed that the slides on miscellaneous tips and key takeaways were probably the most important. I agree. Here’s a brief rundown:

![Image](/assets/datax-misc.jpg "Three simple bullet points that had a lot of impact")

Three simple bullet points that had outsized impact on overall outcomes.

**Take time to learn from domain experts and users.** While developing and improving our system, I visited the hospitals and observed the nursing and counter staff use their existing system, and eventually, our new system. This helped me learn about the assumptions and heuristics they adopted while using the systems, providing insight into new features (for our ML model) that reduced error. I also consulted hospital administrators for advice on how to better understand and clean the data—this also helped reduce error.

**More data and/or features != better model.** My initial approach was to use *all* the data from the various hospitals to build a single model—I assumed the model could learn about the idiosyncrasies of each hospital. This was not the case (or perhaps my models were underpowered). Building a separate model for each hospital worked **much** better (i.e., significantly lower error). In hindsight, this makes sense as each hospital was different in price point (e.g., 5-star hotel vs. public hospital), surgery and disease specialization, doctors, etc.

**Proper engineering practices make life easier.** Beyond engineering practices in our code (e.g., [test cases](https://eugeneyan.com/writing/testing-ml/), [linting, type checking](https://eugeneyan.com/writing/setting-up-python-project-for-automation-and-collaboration/), etc.), adopting version control on model artifacts let us rollback “defective” models if we ever needed to (we never did). Docker helped us encapsulate and horizontally scale our model endpoints, while the ELK stack provided much-needed visibility across our entire pipeline. All this made deploying and operating the ML system much easier.

**Machine learning is <20% of the effort—the methodology and engineering process are more important.** Much of the improvements to the system came from engaging with stakeholders to understand the problem, defining the right proxy metrics, and grokking the data. Also, as the architecture diagram shows, machine learning is really only a small part of the overall system. And I didn’t cover the topics of infra, networking, maintenance, monitoring, etc.

I shared a similar sentiment on Vicki Boykis’ question, and some people seemed to agree.

> Much of the impact happens outside coding.  
>   
> • Picking the right problems to solve  
> • Defining proxy metrics that match the real world  
> • Learning quickly about existing solutions  
> • Designing the simplest system to a complex problem  
> • Maintaining it with minimal ops overhead
>
> — Eugene Yan (@eugeneyan) [February 6, 2021](https://twitter.com/eugeneyan/status/1358130509788835840?ref_src=twsrc%5Etfw)

• • •

A common bottleneck I see in start-ups and [SMEs](https://en.wikipedia.org/wiki/Small_and_medium-sized_enterprises) is to focus too much on applying machine learning on batch data, usually CSVs, to achieve artificially strong results that are overfitted and not replicable in production. I hope this talk provided a greater understanding of how to avoid this, and develop a production-grade ML system.

> Thanks to [@Al\_Grigor](https://twitter.com/Al_Grigor?ref_src=twsrc%5Etfw) for inviting me to speak at the [@DataTalksClub](https://twitter.com/DataTalksClub?ref_src=twsrc%5Etfw) conference! It was a pleasure sharing what went on behind the scenes while building an ML system for Southeast Asia's largest hospital group.   
>   
> Video and summary 👇<https://t.co/KQDKGVOvMK>
>
> — Eugene Yan (@eugeneyan) [February 11, 2021](https://twitter.com/eugeneyan/status/1359676848490205184?ref_src=twsrc%5Etfw)

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Feb 2021). DataTalksClub - Building an ML System; Behind the Scenes. eugeneyan.com.
> https://eugeneyan.com/speaking/machine-learning-in-healthcare/.

or

```
@article{yan2021healthcare,
  title   = {DataTalksClub - Building an ML System; Behind the Scenes},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2021},
  month   = {Feb},
  url     = {https://eugeneyan.com/speaking/machine-learning-in-healthcare/}
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
[machinelearning](/tag/machinelearning/)
[production](/tag/production/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Growing and Running Your Data Science Team](/writing/data-science-teams/)
[How to Win a Data Hackathon (Hacklytics 2021) »](/writing/how-to-win-data-hackathon/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---