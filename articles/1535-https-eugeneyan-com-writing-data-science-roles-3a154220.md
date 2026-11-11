---
title: 'https://eugeneyan.com//writing/data-science-roles/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/data-science-roles/
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

# Applied / Research Scientist, ML Engineer: What’s the Difference?

[
[datascience](/tag/datascience/)
[machinelearning](/tag/machinelearning/)
[engineering](/tag/engineering/)
[career](/tag/career/)
]
 · 11 min read

In 2012, the data scientist was named the [sexiest job of the 21st century](https://hbr.org/2012/10/data-scientist-the-sexiest-job-of-the-21st-century). Now in 2020, this catch-all role is more often split into multiple roles such as data scientist, applied scientist, research scientist, and machine learning engineer.

> Data Scientist (n.): Person who is better at statistics than any software engineer and better at software engineering than any statistician.
>
> — Josh Wills (@josh\_wills) [May 3, 2012](https://twitter.com/josh_wills/status/198093512149958656?ref_src=twsrc%5Etfw)

I used to get questions like “[What does a data scientist do?](/writing/what-does-a-data-scientist-really-do/)” Now, I get questions such as “What does a data/applied/research scientist do? What is a machine learning engineer? How are they different from each other?”

**Here’s my attempt to explain the goals, skills, and deliverables of each role.** If you’re trying to enter or transition within the field of data science, I hope this will help you get the right role—one that matches your interests and skills. We’ll also take a look at how data science has specialized and rebranded itself in the past decade, and what those changes mean for teams and practitioners.

**Disclaimer:** This is my personal take based on chats I’ve had with folks in various organizations and roles. It does not represent the views of my employer. Also, not all companies adopt these titles, so don’t take it too seriously if you feel like you have a title mismatch. In addition, role distinctions might blur depending on project phases.

How did data scientists “become” data analysts?

Recently, I was amused to learn that the data scientist title has gained a bad rap, with some claiming that they’re "[just glorified analysts](https://www.reddit.com/r/datascience/comments/fpcltw/data_scientists_are_just_glorified_analysts_and/)". I think this view is misguided and unfair. The data scientists that I know work on increasingly sophisticated A/B testing and inference techniques that are high-impact. Nonetheless, it’s interesting to learn how it came about.

In August 2017, the Reddit community noticed that data scientists at Facebook were [mostly doing data analyst work](https://www.reddit.com/r/datascience/comments/6vv7u2/are_data_scientists_at_facebook_really_data/). A commenter shared that the generic data science role (in Facebook) was a “product analytics data scientist”, focused on data extraction, analysis, and statistics. (Another commenter also shared how Nielsen’s Measurement Science team [became the Data Science team overnight](https://www.reddit.com/r/datascience/comments/6vv7u2/are_data_scientists_at_facebook_really_data/dm3b6kr).) To distinguish between product/analysis-focused and research-focused data scientists, Facebook created a [Core Data Science](https://research.fb.com/teams/core-data-science/) group focused on research.

Then in April 2018, Lyft [rebranded](https://medium.com/@chamandy/whats-in-a-name-ce42f419d16c) their data analysts as data scientists, and data scientists as research scientists. Here’s how they drew the line: data scientists extract insights from data, track business metrics, and drive better decision making; research scientists build math models and algorithms that power the product. Why rebrand? Lyft shared an example of losing data analytics candidates to competitors offering the data scientist title.

Data analytics and data science talent is hard to come by. If offering candidates a seemingly more prestigious title gives a competitive advantage in hiring (and at zero cost), why not? It’s likely many other teams followed suit. As a result, the data science title is now synonymous with data analytics.

## What the different roles use and deliver

### Data scientists drive better decisions via analysis

Data scientists help to size problems and opportunities, understand customers and the business, interpret A/B tests with mixed results, and so on. They have the most contact with business and product leaders and are often viewed as trusted advisors. Their work involves data analysis, visualization, and weaving a coherent narrative. They might also be called decision scientists, with [Cassie Kozyrkov](https://www.linkedin.com/in/cassie-kozyrkov-9531919/) being a famous example.

> In God we trust, all others bring data. — W Edwards Deming

Data scientists are often writing SQL/Hive/Spark queries to extract and clean data, and Python/R to run analyses and create visualizations. They might also build data pipelines and dashboards for recurring analyses.

They also have strong non-technical skills to: distill and frame problem statements, explain complex findings and recommendations, and educate the organization on the nuances of statistics and data. Their deliverables include documents, visualizations, and dashboards to provide insight and guide decisions.

### Applied scientists build ML systems to improve business outcomes

Applied scientists use ML to improve business outcomes (e.g., revenue, cost, customer experience). The systems they build may be internal (e.g., product classification, fraud detection) or customer-facing (e.g., search, recommendations). Outside of use-case driven applications, they might also develop internal datasets, tooling, and methodology (e.g., feature stores, package/docker templates, model testing & release checks).

In addition to tools for extracting and cleaning data, applied scientists also use machine learning and deep learning libraries. They may also use tools for containerization (e.g., Docker), orchestration (e.g., Airflow), CI/CD (e.g., Jenkins), and prototyping (e.g., FastAPI).

Similar to data scientists, applied scientists convert business problems (e.g., increasing revenue) into solutions (e.g., increased customer acquisition? improved search or recommendations? pricing models?) To go from problem to production, they need know-how on: building data pipelines, experimentation and prototyping, training and deploying ML models, and basic software engineering and devops. Their deliverables include code for ML systems and documents on their design, methodology, and experiments.

### Research scientists develop new methodology and techniques

We have research scientists (and academics) to thank for the brisk advances in fields such as deep learning, computer vision, and natural language processing. They tend to investigate problems that are more fundamental (e.g., model compression, image segmentation, speech-to-text) with a longer time horizon. Outside of the tech giants and research labs, few organizations have the budget and appetite to fund such roles.

> Research is creating new knowledge. — Neil Armstrong

Research scientists often work on publicly available datasets and benchmarks, such as [ImageNet](http://www.image-net.org) for computer vision, [General Language Understanding Evaluation (GLUE)](https://gluebenchmark.com) for natural language understanding, and other open-source datasets (e.g., [recommendations datasets](https://github.com/caserec/Datasets-for-Recommender-Systems), [Kaggle](https://www.kaggle.com/datasets)).

Most will use deep learning libraries—other approaches have fallen out of favor—and have deep and specialized knowledge in their niche. They also excel in literature research, reproducible experiments, and publishing papers at conferences and journals. Their deliverables include papers and code to replicate their models and results.

### Machine learning engineers build infra and platforms to grow capabilities

Machine learning engineers (MLEs) work on infrastructure and platforms that make it easier to build, deploy, and monitor machine learning models. Examples include [Michelangelo (Uber)](https://eng.uber.com/michelangelo-machine-learning-platform/), [Metaflow (Netflix)](https://metaflow.org), and [SageMaker (Amazon)](https://aws.amazon.com/sagemaker/). They might also work directly on application-specific ML systems in a capacity similar to an applied scientist, or help with deploying and scaling ML models for production.

Most MLEs have prior experience as a software engineer and have stronger backgrounds in software development, devops, and engineering best practices. Compared to Python-slinging scientists, MLEs tend to build systems on more enterprise and performant languages (e.g., Java/Scala, C++, Go).

For MLEs, there’s greater emphasis on technical design and architecture, infra, scalability, security, etc. Relative to scientists who are mainly users of tools (e.g., Docker, Airflow, Jenkins), MLEs tend to be the ones to set up the infra and processes around it—they’re essentially a software engineer with an ML tilt.

Whew, that was a lot of text; here’s a table summarizing the above.

|  | Data Scientist | Applied Scientist | Research Scientist | ML Engineer |
| --- | --- | --- | --- | --- |
| Goal | Perform analysis to guide better decisions | Build ML systems to improve business outcomes | Develop new methodology and techniques | Build infra and platforms for ML capabilities |
| Tools | SQL, Hive, Python/R, dashboards | SQL, Hive, Python, ML libraries, Docker, FastAPI, etc. | Python, deep learning libraries, LaTeX | Python, Java/Scala, C, Go, Docker, Jenkins, etc. |
| Skills | Statistical analysis, visualization, dashboarding, storytelling, A/B testing | Data pipelines, machine/deep learning, experimentation and prototyping, software engineering, devops | Research, experiments on industry/academic benchmarks, publishing papers | Software development, devops, scalability, security, etc. |
| Deliverables | Documents for insight and decisions, dashboards | Code for ML systems, documents on design, methodology, and experiments | Papers and code to demonstrate findings | Code for infra and platforms, documentation |

Summary table of the various data & ML roles

## What the various roles mean for the field

While having more titles can be confusing, the specialization *should* help clarify the goals and skills required for each role. Back in South-East Asia, all roles had the title of data scientist. The job scope was akin to rolling a dice; it might entirely involve analysis and dashboarding, or building ML systems, or client sales. Having more fine-grained titles can help job seekers and hiring managers achieve better job-fit.

Breaking down the DS role also makes it less overwhelming for newcomers. There’s an unhealthy expectation to be proficient at 23 skills/techniques and 8 tools to be a (unicorn) data scientist. Separate roles make clear it’s not necessary. Data scientists don’t have to write production code, MLEs don’t need to know the nuances of research and publishing. Specialized roles allow people to focus on their strengths and interests.

![Data Science skills](/assets/data-science-metro.webp "Data Science skills")

119 easy steps to becoming a data scientist ([source](http://nirvacana.com/thoughts/2013/07/08/becoming-a-data-scientist/))

Nonetheless, specialization takes us further from [end-to-end ownership and delivery](/writing/end-to-end-data-science/). With MLEs, one anti-pattern is scientists writing POC code in Jupyter notebooks or R and handing off to MLEs to convert the code and productionize. The context and methodology is often lost in translation and diffusion of responsibility seeps in. It also slows down iteration and increases operations and maintenance cost.

Another concern is title inflation and loss of hiring competitiveness. As Lyft shared, the possibility of [losing data analytics candidates to competitors offering “data scientist” titles](https://medium.com/@chamandy/whats-in-a-name-ce42f419d16c#394a) is real. Will this escalate with companies losing machine learning candidates if they offer the data scientist title, relative to competitors offering the research scientist or machine learning engineer title? If so, we might see the field come up with more titles (e.g., deep learning scientist, AI engineer) that might obfuscate the real work being done.

Counterpoint: New roles emerge and rebranding occurs all the time in tech

The data engineer is a recent role that’s a combination of backend engineer, database administrator, and SQL developer. The increase in data collection and storage, and growth in specialized data infra (e.g., Hadoop, Spark, Kafka, etc.) required for this role. We also see the traditional catch-all software engineer split into frontend, backend, mobile, cloud, devops, quality assurance, etc.

And before data scientists, there were statisticians.

Here’s Google’s Chief Economist, Hal Varian, explaining why *statisticians* will be the sexiest job of the 2000s. This was in Sep 2009, barely three years before the [HBR article](https://hbr.org/2012/10/data-scientist-the-sexiest-job-of-the-21st-century) on data scientists being the sexiest role of the 21st century.

And in early 2014, some also viewed data scientists as statisticians, but living in San Francisco and using a Mac.

> "A data scientist is a statistician who lives in San Fransisco" [#monkigras](https://twitter.com/hashtag/monkigras?src=hash&ref_src=twsrc%5Etfw) [pic.twitter.com/HypLL3Cnye](http://t.co/HypLL3Cnye)
>
> — Jeremy Jarvis (@jeremyjarvis) [January 30, 2014](https://twitter.com/jeremyjarvis/status/428848527226437632?ref_src=twsrc%5Etfw)

## Should our team adopt these distinct roles and titles?

It depends.

AFAIK, these roles are mostly seen in relatively larger tech organizations (i.e., data science teams of >50). At that scale, there’s sufficient volume of work for each specialized role. However, in smaller companies, there might not be the need (or luxury) to spilt the data scientist and applied scientist role, or the budget for research-focused roles with multi-year horizons. (Nonetheless, MLEs to help with production are increasingly common.)

And it appears to be a trend specific to the US. In South-East Asia, most of these roles are grouped under the title of data scientist. Nonetheless, regional tech unicorns such as [Grab](https://www.grab.com), [Shopee](https://shopee.com), and [Traveloka](https://www.traveloka.com/en-id/) have large enough teams that may require such specialized roles. Chinese giants (e.g., [Alibaba](https://en.wikipedia.org/wiki/Alibaba_Group), [Baidu](https://en.wikipedia.org/wiki/Baidu), [Tencent](https://en.wikipedia.org/wiki/Tencent)) will also have these different roles.

If you’re thinking of splitting the data scientist role into distinct specializations, please also consider the benefits of [having data scientists be more end-to-end](/writing/end-to-end-data-science/).

## Conclusion: Skills + Deliverables > Titles

> The Internet doesn’t care about your title.
>
> — Nav.al (@naval) [November 9, 2020](https://twitter.com/naval/status/1325718336399790080?ref_src=twsrc%5Etfw)

What if we’re performing the role of a `<more prestigious title>` but have a `<less prestigious title>`? Before we change jobs to upgrade titles, or accept a poorer offer with a better title, we should remind ourselves that it’s *just* a title. In the long run, focusing on deliverables expected and skills required will lead to better fit and job satisfaction.

P.S., But what if the role doesn’t match our skills and aspirations, like [this guy](https://www.reddit.com/r/datascience/comments/fpcltw/data_scientists_are_just_glorified_analysts_and/)? We’ll discuss that [here](/writing/role-title-mismatch/).

> What's the difference between data, applied, and research scientists? What about machine learning engineers?  
>   
> In this piece, we discuss:  
> • The various goals, skills, and deliverables  
> • How data scientists "became" analysts  
> • Implications for the field <https://t.co/ZWZ9pbIz5E>
>
> — Eugene Yan (@eugeneyan) [November 11, 2020](https://twitter.com/eugeneyan/status/1326348419582005261?ref_src=twsrc%5Etfw)

### Additional reading

* [Data vs. Applied vs. Research Scientist at Amazon](https://www.teamblind.com/post/Data-vs-Applied-vs-Research-Scientist-@Amazon-OiJ0KOSx)
* [Facebook - Applied Scientist vs. Research Scientist vs. Data Scientist](https://www.teamblind.com/post/Facebook---Applied-Scientist-vs-Research-Scientist-vs-Data-Scientist-pg1tHJWX)
* [Difference between Data Scientists and ML Engineer](https://www.quora.com/What-is-difference-between-a-Data-Scientist-and-a-Machine-Learning-Engineer-Which-is-better-in-terms-of-salary-and-long-term-growth-and-why-How-are-they-correlated)

**Thanks** to Yang Xinyi, Alexandra Macqueen, and [Michell C. Clark](https://twitter.com/michellcclark) for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Nov 2020). Applied / Research Scientist, ML Engineer: What’s the Difference?. eugeneyan.com.
> https://eugeneyan.com/writing/data-science-roles/.

or

```
@article{yan2020roles,
  title   = {Applied / Research Scientist, ML Engineer: What’s the Difference?},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Nov},
  url     = {https://eugeneyan.com/writing/data-science-roles/}
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
[engineering](/tag/engineering/)
[career](/tag/career/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Chip Huyen on Her Career, Writing, and Machine Learning](/writing/informal-mentors-chip-huyen/)
[How to Prevent or Deal with a Data Science Role or Title Mismatch »](/writing/role-title-mismatch/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---