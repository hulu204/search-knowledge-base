---
title: 'https://eugeneyan.com//writing/omscs-cs6440-intro-to-health-informatics/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/omscs-cs6440-intro-to-health-informatics/
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

# OMSCS CS6440 (Intro to Health Informatics) Review and Tips

[
[omscs](/tag/omscs/)
[learning](/tag/learning/)
]
 · 7 min read

> You might also be interested in this [OMSCS FAQ](/writing/georgia-tech-omscs-faq/) I wrote after graduation. Or view all OMSCS related writing here: [`omscs`](/tag/omscs).

## Why take this class?

In general, I’m keenly interested in HealthTech (and [EdTech](/writing/omscs-cs6460-education-technology/)). One key reason I decided to enroll in OMSCS was due to the electives on health tech. The syllabus for IHI looks like a primer on the key technologies and standards in health technology, such as FHIR, EHRs, PHRs, etc. In addition, the weekly live lectures were a draw as they involved guest lecturers who were actively building health tech applications, both in startups and established enterprises.

However, the ratings on [OMSCentral](https://omscentral.com/course/CS-6440) were poor. The average rating was 3 / 5, one of the poorest among all the classes I’ve taken. Average difficulty was 2 / 5, with the average workload of about 6.5 hrs a week. With regard to the average workload, the bulk of it depends on your group project, which has team size of 4 - 6 people. With a good team, the workload should be light with everyone pulling their own weight—else, be prepared to spend significant time on it.

What’s the course like?
Overall, the course covers three main sections:

* Healthcare system and data (e.g, Electronic health records, personal health records, etc.)
* Healthcare interoperability (e.g., Fast Healthcare Interoperability Resources (FHIR), RxNorm, CPT, ICD, LOINC, NDC, HealthVault, etc.)
* Future healthcare applications (e.g., public / population health, data and analytics, etc.)

There were a lot of lecture videos to watch. However, I found the videos to be a less effective mode of information transmission. I have pretty low expectations for videos, but these were very dry and consisted mainly of the lecturer at his desk, (most likely) reading from a teleprompter. The transcripts were made available and I mostly referred to these when revising for the exams. Reading provides higher bandwidth and lower entropy that video watching.

Nonetheless, this was compensated by Dr. John Duke, MD having live lectures twice a week and inviting guest speakers to share about their work in the healthcare industry. This included speakers from Cerner, Emory, Goggle, as well as other startups that are helping to improve healthcare. Having a guest lecture every week is no mean feat and the team really put in a lot of effort into preparing this.

![Health Informatics](/assets/health-informatics.webp "Health Informatics")

Live lectures with great practitioners twice a week.

For the overall workload, there were three sections, namely: (i) individual assignments (30 points), (ii) team project (35 points), and (iii) participation (35 points).

The individual assignments involved hands-on activities to give you a feel of using FHIR (java required here!) and the other healthcare standards and data repositories taught in the lectures. These may involve code, especially Java, or trying some online tool and copy-pasting the JSON result. These were auto graded with immediate feedback on a platform called INGInious.

For the team project, it involved first forming a group of 4 - 6 people on Piazza or Canvas. This can get pretty hectic, especially if you’re left towards the end without a group. Highly encouraged to form your groups early—usually, the people who post on the group forming boards early tend to be more “on-the-ball” and likely to be good teammates ;).

After forming your groups, you then indicate your preference for a healthtech problem, working with external mentors on developing a solution. For our class, a list of applications was made available and teams had to pick which ones they wanted to work on. Projects seems largely assigned on a first-come-first-served basis.

Throughout the project, there were multiple deliverables, from the weekly progress reports, to the four video presentations on the application (each team member must present at least once). The final deliverable also had to be deployed on the class infrastructure and involved using Docker, Rancher, Kubernetes, and Jenkins.

The project could largely be hit-or-miss, depending on your external mentor. Throughout the project, we learnt that our external mentor, a research lab in Georgia State University, had been working on this project for FIVE years. Mind boggling. I can’t even imagine taking more than six months to have a functioning MVP. Also, our TA seemed new and was unable to help with the technical queries and difficulties we had with the infrastructure. Often, the resources (e.g., URL links) provided were wrong, load balancers were set up incorrectly, and settings and pipelines erroneously triggered. Thankfully, I was able to reach out to the TA in charge of infrastructure and he got things resolved quickly.

With regard to participation, it’s a somewhat misleading term. The bulk of it involved six case studies that were covered in the live lectures. Usually, some context is provided, often in the form of a medical case, with one or two questions for students to research and write about. Sample questions include: “How could healthtech have helped prevented this incorrect prescription?”, “How could healthtech help diabetics better control their condition?”. Some of the questions were fairly nebulous and I often had no idea if I was on the right track or not.

In addition, there were four “Check your understanding”s which were largely aimed at making sure students understood what was required of them in the course and project deliverables.

In addition, there were two exams (six points each), which were the mid terms and finals. These were open book and fairly easy. You should be able to breeze through it with the transcripts.

More about the class syllabus here: [https://cs6440.gatech.edu](https://cs6440.gatech.edu/)

## What did I learn?

Overall, the course covered a lot of general knowledge around the different types of healthcare data and standards available. Particularly interesting was the lesson on Microsoft HealthVault (Update: NOW DEPRECATED), I saw it as a way to put patients’ medical records in their own hands, so they could have complete overview of it. Unfortunately, Microsoft has also announced that HealthVault will not be supported after 20 Nov, 2019. Notwithstanding, learning about the great variety of data standards in healthcare helped to provide greater context of the industry I’m in, and provide applicable knowledge on what resources and tools are available.

For the group project, I learnt to work in a distributed team, with people from all around the world in different timezones. We had people from Mauritius, India, Vienna, the US, and Singapore. In addition, the tech stack chosen was something I was less familiar with (Javascript). Thankfully, I was able to pick up the basics of JS fairly quickly and contributed to part of the front-end development. In addition, I had a chance to apply my skills by setting up the deployment pipeline using Docker, Rancher, and Jenkins.

## Unfortunately, not a course I would recommend

Of all the classes I’ve taken so far, this is by far the worst, and is also the only class I would not recommend to the average student. Unless you’re really interested in healthtech (like I am), it would be difficult for you to sit through the lectures and work through the (tedious) assignments. The learning you derive from it is also very specific to healthcare and likely not applicable if you’re not in the healthcare industry.

Nonetheless, it is a fairly low workload course, which makes it ideal for pairing with another moderate workload course (e.g., [ML4T](/writing/omscs-cs7646-machine-learning-for-trading/)), which is exactly what I did.

## What’s next?

I’m excited to start using some of the resources shared and apply them to my current work in a healthtech start-up. Data interoperability is a tricky issue that makes it difficult to scale how we work with different data sources from various insurance and healthcare providers. Perhaps we can apply some of the pre-existing and widely adopted standards. If not, there are also valuable lessons in how the standards were created that we can apply when creating our own data schema.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Aug 2019). OMSCS CS6440 (Intro to Health Informatics) Review and Tips. eugeneyan.com.
> https://eugeneyan.com/writing/omscs-cs6440-intro-to-health-informatics/.

or

```
@article{yan2019health,
  title   = {OMSCS CS6440 (Intro to Health Informatics) Review and Tips},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2019},
  month   = {Aug},
  url     = {https://eugeneyan.com/writing/omscs-cs6440-intro-to-health-informatics/}
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
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« OMSCS CS7646 (Machine Learning for Trading) Review and Tips](/writing/omscs-cs7646-machine-learning-for-trading/)
[Goodbye Wordpress, Hello Jekyll! »](/writing/goodbye-wordpress-hello-jekyll)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---