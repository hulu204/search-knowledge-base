---
title: 'https://eugeneyan.com//writing/omscs-cs6300-software-development-process/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/omscs-cs6300-software-development-process/
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

# OMSCS CS6300 (Software Development Process) Review and Tips

[
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[engineering](/tag/engineering/)
]
 · 5 min read

> You might also be interested in this [OMSCS FAQ](/writing/georgia-tech-omscs-faq/) I wrote after graduation. Or view all OMSCS related writing here: [`omscs`](/tag/omscs).

Recently, I completed the Georgia Tech OMSCS [Software Development Process (CS6300)](http://omscs.gatech.edu/cs-6300-software-development-process) course over the summer. It was very enriching—I learnt about proper software engineering practices and created apps in Java and Android. Here’s an overview of my experience, for those who are considering taking it.

## Why did I take this course?

Since entering the data and technology industry a couple of years ago, I’ve always felt the need to improve my skills in software engineering. This is compounded by my lack of (i) a computer science degree (I studied psychology) and (ii) hardcore software industry experience.

Via online course and work experience (at IBM and Lazada), I picked up decent coding and engineering skills. While I’m able to build robust and maintainable data products in Python and Scala (Spark), I felt the need for a formal class on software engineering fundamentals so as to develop more sophisticated applications with greater efficiency. This includes learning about good architecture design, software development cycles, etc.

## What did we build during the course?

For the summer 2017 run of SDP6300, the bulk of the work revolved around two main projects and multiple smaller individual assignments:

Team project: Teams of 3 - 4 built an Android App where users could login and solve cryptogram puzzles. Solutions and scores for each puzzle were to be persisted locally as well as updated on an external web service. Users can then view a global leaderboard with top player scores. It also required functionality for administrative users to add new players and cryptograms. This had to be built over 3 weeks—many teams found this barely enough.

View: Screens of our Android App

![Software Development Process User Screen](/assets/software-development-process-user-screen.webp "Software Development Process User Screen")

Player features and screens

![Software Development Process Admin Screen](/assets/software-development-process-admin-screen.webp "Software Development Process Admin Screen")

Admin features and screens

Individual project: The objective was to build a command line Java program to replace words in a text file. Normally, this shouldn’t be too difficult but it included the requirement to have five separate options that could be combined (e.g., replace even occurrences only, maintain case of original word, etc.). This was built via a test-driven development (TDD) approach, by writing multiple test cases before building any functionality. The instructor also provided fiendish test cases to ensure our app was up to snuff. There was also a black-box testing task that required achieving 100% statement coverage and identifying at least 3 bugs. This project took 3 weeks.

Individual assignments: This included an Android development task (to prepare the class for the Android team project), developing a UML (Unified Modelling Language) diagram for an App, white-box test case creation, etc.

## What’s the course like?

Compared to Computer Vision (which I took last semester), I found the workload to be slightly lighter.

There were approximately 30 minutes of lectures, as well as a deliverable, every week. On some weeks, there were deliverables for both the team project and the individual assignments (tough!).

All the assignments were based on Java and Android, and are obviously easier if one has prior experience. If not, expect to spend 2 - 3x more time on each assignment picking up the required Java and Android along the way. I found this Lynda course on [Java Essentials](https://www.lynda.com/Java-tutorials/Java-Essential-Training/377484-2.html) helpful. Nonetheless, developing the apps in Java and Android remained challenging.

Professor Alex Orso is very enthusiastic, responsive on Piazza, and held helpful office hours sessions weekly, even when he’s travelling. Together with the TAs, they provided prompt support on the forums. Classmates with Java background were also forthcoming with Java and Android guidance on Piazza and Slack. Most questions on Piazza were answered promptly.

Assignments wise, it was satisfying to build an Android App with multiple screens, local persistence, and a connection to an external web service. I gained experience developing software across multiple timezones, with team members having very diverse skill sets. In our team of four, we had one experienced Java programmer, one intermediate Python developer, one PM, and myself.

Thankfully, there were no exams (I was getting burnt out towards the end).

## What did I learn?

First and foremost, how to develop applications in Java and Android. Though I probably won’t get to practice much (my work’s tech stack is largely Scala/Python), it was good mental exercise to learn a new language. Personally, I derived a great sense of achievement building a fully functional Android app with basic UI.

I also gained knowledge and experience in software engineering tools and practices that non-CS students wouldn’t learn in college. This includes TDD, testing and coverage, white-box and black-box testing, object oriented design, agile development methods, documentation best practices (e.g., requirements, test cases, use cases), etc.

From the team project, I gain experience with software engineering in an asynchronous, distributed environment that involved shifting roles. I started as the test engineer, writing test specs and unit tests. Then, I moved to being an Android dev, building the functionality and screens for the Admin users. After that, I switched back to testing and fixing critical bugs.

## So what’s next?

I intend to actively apply the software development practices gained, in both my work and personal projects. This includes:

* Creating separate branches for each jira ticket, before merging into the development and master branches
* Being more rigorous with testing, test coverage, and documentation
* Developing code that is (hopefully) easier to maintain via object oriented design

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Aug 2017). OMSCS CS6300 (Software Development Process) Review and Tips. eugeneyan.com.
> https://eugeneyan.com/writing/omscs-cs6300-software-development-process/.

or

```
@article{yan2017software,
  title   = {OMSCS CS6300 (Software Development Process) Review and Tips},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2017},
  month   = {Aug},
  url     = {https://eugeneyan.com/writing/omscs-cs6300-software-development-process/}
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
[engineering](/tag/engineering/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Tech in Asia - My Journey in Data Science and Advice for others](/speaking/my-sharing-with-tech-in-asia-talk/)
[SMU - What is Data Analytics and How do I get into it? »](/speaking/sharing-at-singapore-management-university-on-data-analytics-talk/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---