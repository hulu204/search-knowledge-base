---
title: 'https://eugeneyan.com//writing/omscs-cs6200-introduction-to-operating-systems/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/omscs-cs6200-introduction-to-operating-systems/
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

# OMSCS CS6200 (Introduction to OS) Review and Tips

[
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[engineering](/tag/engineering/)
]
 · 7 min read

> You might also be interested in this [OMSCS FAQ](/writing/georgia-tech-omscs-faq/) I wrote after graduation. Or view all OMSCS related writing here: [`omscs`](/tag/omscs).

Over Fall 2019, I finally completed OMSCS with my last course. It has been a fulfilling marathon over three years learning about the fundamentals of machine learning, software engineering, and building user-centric products in a structured learning environment with peers from all over the world.

For my last course, I wanted something I had no experience in, something different from my day-to-day work, and something out of my comfort zone.

Enter CS6200, Introduction to Operating Systems. The [course description](https://www.omscs.gatech.edu/cs-8803-introduction-operating-systems) mentions concurrency, synchronization, resource management, and distributed services, with projects on multithreaded programming, inter-process communication, and distributed interactions via RPC. The projects would be in C and C++. I knew little about these topics and C/C++—perfect.

The ratings on OMS Central were excellent, with a class rating of 4.4, difficulty of 3.6, and about 17 hours per week. In addition, I have only heard good reviews from others who have taken it. (As an aside, I found the difficulty to be on par with [ML](/writing/omscs-cs7641-machine-learning/), [RL](/writing/omscs-cs7642-reinforcement-learning/), and [AI](/writing/omscs-cs6601-artificial-intelligence/) (4.1 – 4.3), and the effort to be slightly higher at about 20 – 30 hours a week, especially for the initial projects.)

Seems like a great last course (or so I thought). As I confirmed my course selection, I rationalized that it would be useful to gain knowledge and familiarity at the OS level, though I’m not sure how it’ll be applied in my work (as a data scientist).

Well was I in for a *surprise* (read: **shock**).

Within the first week of project 1, I knew I was in trouble. I had either overestimated my ability to pick up C, or underestimated the sophistication of the projects, or both.

The first project had us working to send images between processes at the byte level (i.e., looping over all bytes) and implementing multithreaded servers and clients—I was in way over my head. I only completed 80% of it.

However, over the course of the projects and lessons, I found myself enjoying cracking my head on the material. From designing servers and clients that communicated via shared memory, to learning about synchronization and inter-process communication APIs/gRPC and using them, to understanding how CPU, memory, and disk work in distributed processes, as I look back, it was a lot of fun.

All in all, this is a course I **highly recommend**, though students should have a baseline understanding of C.

## What’s the course like?

Half of the learning comes from hands-on implementation. There were three main projects (40%) and an optional side project (bonus 4%). The main projects have a similar theme: *Moving data between processes in a multithreaded fashion.*

Projects 1 and 3 are in C, while project 4 is in C++ and uses gRPC and protocol buffers. If you come into the class without any C knowledge, there might be some teething pains.

**Project 1** involved sending messages and files via sockets. It starts off slow where students implement the protocol specified and send simple strings (as warmup). Then, these string messages are used as client requests for files, which the server has to respond with sending a file (i.e., an image) over a socket. As a finale, this has to be multithreaded and the implementation throughput is tested. Multithreading it involved working with synchronization constructs such as mutexes and conditional variables. This project took me about 60 hours and I only managed to complete 80% of it.

![](/assets/gftransfer.webp)

The predefined protocol for client server communication

**Project 2** was an optional project that provided up to 4% extra credit. The deliverable was a paper on how to performance test the multithreaded server and client implemented in project 1 (e.g., how would performance scale as the number of threads increase?). No implementation was involved though significant detail on the experiment methodology was required. This project is only evaluated at the end of the course for students that are close to the grade cutoffs (e.g., between A and B, or B and C).

**Project 3** involved transferring files over shared memory. Thee bulk of it was figuring out the design of a server and client that communicates via shared memory and message queues, and how to use synchronization constructs to prevent race conditions. This can be daunting for students with little prior OS and engineering background. Thankfully, TAs and peers were there to provide suggestions and guidance. After the steep learning curve of project 1, I found project 2 slightly easier. It took 30 – 40 hours to fully complete.

![](/assets/shared_memory_part2.webp)

Building a cache server based on shared memory

**Project 4** had us learning about transferring files via remote procedure calls, specifically, gRPC. At a high level, we were building a DropBox that would keep files across clients in sync via a central server. To start, we implemented RPCs for clients to fetch, store, delete, and list files on the server. Then, these RPCs were used to build a distributed file system to sync files across clients via the server. I.e., if a new file was added to client 1, this should be automatically uploaded to the server, and replicated on other clients.

**Exams** accounted for the majority of the grade, with the midterms making up 25% and the finals 30%. The finals are non-cumulative (i.e., only covers material after the midterm). The exams mainly evaluate on understanding the content from the lectures and papers and comprised of multiple choice and calculations. If you understand the fundamentals of the course content and the calculations in the lectures (i.e., can replicate them instead of just at the handwavy level), you should be able to do decently well.

**Class discussions** took place on Piazza and Slack. 5% was allocated as participation points, though like project 2, this was only evaluated for students at the borderline between grade cut-offs. From the TAs, this was about 2-3% of students in each cohort.

The Piazza forum was fairly standard. Prof Ada and the TAs are active on them and share important information there.

The **slack channels** deserve special mention. The TAs and students were much more active on Slack. The TAs mainly took a Socratic (though it can come across as trolling) approach towards providing advice that largely involves asking questions to help students think deeper about their design and implementation. Many students credit successful completion of projects to the guidance from the TAs and their peers on slack, where past advice and suggestions are easily searchable. Nonetheless, it can be a bit of a firehose at times where I would wake up and find 600+ new messages overnight (given the time difference).

As one award-winning TA put it, *Piazza is the classroom, Slack is the class lobby*.

## What did I learn?

Reflecting on when I first started CS6200, I have come a long way and learnt a lot, largely because I had no relevant knowledge and experience initially.

Specific to programming languages, I **gained familiarity with C and C++**, strongly typed compiled languages that require you to do your own memory management. While I don’t have the proficiency to write production level code (yet?), I can read and understand packages built on C/C++, and maybe build small prototypes.

On the course material, I came away with a greater appreciation of **inter-process communication and synchronization**. It was eye opening to build clients and servers that move data at the byte level through sockets, shared memory, and RPCs. The class also provided a greater understanding of the synchronization constructs available such as mutexes, spin locks, semaphores, etc.

For those who are interested, here are some great resources on the [Linux APIs for inter-process communication](http://man7.org/conf/lca2013/IPC_Overview-LCA-2013-printable.pdf) and [gRPC](https://grpc.io/docs/quickstart/cpp/). Overall, I highly recommend this class for anyone looking to get a basic understand of how operating systems work.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Dec 2019). OMSCS CS6200 (Introduction to OS) Review and Tips. eugeneyan.com.
> https://eugeneyan.com/writing/omscs-cs6200-introduction-to-operating-systems/.

or

```
@article{yan2019ios,
  title   = {OMSCS CS6200 (Introduction to OS) Review and Tips},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2019},
  month   = {Dec},
  url     = {https://eugeneyan.com/writing/omscs-cs6200-introduction-to-operating-systems/}
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

[« DataScience SG x ODSC Meetup - Applying ML to Healthcare](/speaking/machine-learning-in-production-for-healthcare-talk/)
[Building a Strong Baseline Recommender in PyTorch, on a Laptop »](/writing/recommender-systems-baseline-pytorch/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---