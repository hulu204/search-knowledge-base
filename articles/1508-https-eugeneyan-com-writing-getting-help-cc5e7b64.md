---
title: 'https://eugeneyan.com//writing/getting-help/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/getting-help/
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

# What To Do If Dependency Teams Can’t Help

[
[leadership](/tag/leadership/)
[misc](/tag/misc/)
]
 · 3 min read

Other than in small organizations, most teams have interdependencies with other teams. For example, a machine learning team may rely on upstream data teams to provide feature data during offline training and online serving. The same ML team may then depend on downstream infra teams to support serving their models at scale.

What can we do if dependency teams won’t or can’t help? This is a common question during chats with peers and mentees. The typical response is to escalate. Alternatively, let’s write a lengthy JIRA ticket explaining why the request is urgent and important to meet the team’s goal. Besides these, here are some approaches I’ve found long-term success with.

**Why won’t or can’t they help?**—do we know? Often, we don’t because we didn’t [seek first to understand before trying to convince them](https://www.franklincovey.com/habit-5/). We can do this by trying to understand their constraints and priorities. Are they unable to help because of resource or technical bottlenecks? Or does our request conflict with their priority of migrating off a tech stack? Also, what does it mean for them to be successful? If we understand their constraints, we can help work around, or even remove, those constraints. If we understand their priorities, we can consciously collaborate to achieve them.

**Achieving mutual understanding hinges on earning trust.** It’s easier to be frank about constraints and priorities if we trust each other. We won’t go into a detailed discussion on how to earn trust but a few simple ways include understanding their needs and acting in their interests, listening and adapting to their feedback, and being dependable and delivering when others need your help.

**“But I’m offering to write the code, why do they refuse my help?”** Depending on the situation, your *help* can cost more effort than them doing it themselves. Imagine having a new developer help with implementing a feature in an existing system: An experienced mentor has to onboard them, provide context and documentation, and likely help with environment setup, debugging error messages, and code reviews. In the short term, this increases work instead of reducing it.

**For another team to readily accept code contributions, they need to be set up for away team work.** [Away](https://www.sledgeworx.io/away-team-work/) [team](https://pedrodelgallego.github.io/blog/amazon/operating-model/away-team-model/) work is where an *away* team implements a feature, pipeline, or integration in the *host* team’s systems. This allows away teams to unblock themselves, thus reducing inter-team dependency. Host teams may need mechanisms such as office hours for consultation, self-service documentation and onboarding, and a review process for architecture design and code. Setting up for away team work is a significant investment and thus not many teams will have that mechanism in place.

**Finally, perhaps we can frame the work as an investment**, where the dependency team invests in mentoring you for the current code contribution so you can mentor your team for future code changes. For them, it reduces the effort of supporting future requests from your team and is a trial for away team work. For you, it’s a solution to implementing what you need and an opportunity to learn and teach about the host team’s code base. Win-win.

• • •

Have you come across similar situations in the past? What helped with navigating them?

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jan 2023). What To Do If Dependency Teams Can’t Help. eugeneyan.com.
> https://eugeneyan.com/writing/getting-help/.

or

```
@article{yan2023dependency,
  title   = {What To Do If Dependency Teams Can’t Help},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2023},
  month   = {Jan},
  url     = {https://eugeneyan.com/writing/getting-help/}
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
[leadership](/tag/leadership/)
[misc](/tag/misc/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« 2022 in Review & 2023 Goals](/writing/2022-in-review/)
[Goodbye Roam Research, Hello Obsidian »](/writing/roam-to-obsidian/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---