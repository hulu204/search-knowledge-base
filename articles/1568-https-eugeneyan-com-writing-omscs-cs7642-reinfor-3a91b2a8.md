---
title: 'https://eugeneyan.com//writing/omscs-cs7642-reinforcement-learning/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/omscs-cs7642-reinforcement-learning/
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

# OMSCS CS7642 (Reinforcement Learning) Review and Tips

[
[omscs](/tag/omscs/)
[learning](/tag/learning/)
[deeplearning](/tag/deeplearning/)
[python](/tag/python/)
]
 · 6 min read

> You might also be interested in this [OMSCS FAQ](/writing/georgia-tech-omscs-faq/) I wrote after graduation. Or view all OMSCS related writing here: [`omscs`](/tag/omscs).

I know, I know, I’m guilty of not writing over the last four months. Things have been super hectic with project Voyager at Lazada, switching over to the new platform in end March and then preparing for our birthday campaign in end Apr. Any free time I had outside of that was poured into the Georgia Tech Reinforcement Learning (CS7642), which is the subject of this post.

The course was very enriching and fun. Throughout the course, we learnt techniques that allow one to optimize outcomes while navigating the world, and were introduced to several [seminal](https://www.semanticscholar.org/paper/Learning-to-Predict-by-the-Methods-of-Temporal-Sutton/6ce57ab17fcd507b856a79874063b59555c76b3a) and [cutting edge](https://www.nature.com/articles/nature14236) (at least back in 2018) papers. I highly recommend this course for anyone who’s part of the Georgia Tech OMSCS.

An especially fun project involved landing a rocket in OpenAI’s LunarLander environment. This was implemented via deep reinforcement learning approaches. Here’s how the agent did on its first try (in reinforcement learning, we refer to the “models” as agents; more [here](https://www.cs.ubc.ca/~murphyk/Bayes/pomdp.html)). As you can see, it crashed right onto the surface. =(

## Why take this course?

At the tail end of the Machine Learning class I took last fall, a small introduction to reinforcement learning was made. We learnt about model-based methods such as Value Iteration and Policy Iteration, as well as model-free methods such as Q-learning.

I was intrigued by model-free methods and thought it might be an interesting and practical approach to model aspects of people in the world, without a complete model of human characteristics. For example, their behavior on a website (where each click gives more information about what they will click next), their health (where each doctor’s visit or activity provides information on their overall health), etc.

## What’s the course like?

In terms of workload, this class is pretty heavy. Most students reported spending up to 30 - 40 hours weekly, and even then, some still could not complete the projects.

There are about 2 hours of lectures weekly. However, these lectures largely skim the surface, and lean more towards theory. Thus, you’ll also find yourself spending an hour or two viewing additional external material (David Silver’s videos are excellent for this) and the office hours by the TAs.

There’s one small homework assignment due almost every week, except on weeks where projects are due. These are largely aimed at connecting the theory to the practical, though I found some of them unnecessarily theoretical and low-level (e.g., design a Markov decision process that would take Policy Iteration more than 15 iterations to solve). These account for 30% of the overall grade, and one is expected to complete all of them. They can take about 2 - 8 hours, depending on whether you see the “trick” or not.

There are also three big projects, which involved writing papers no more than five pages long. The first one involved replicating the seminal [TD-lambda paper by Sutton](https://www.semanticscholar.org/paper/Learning-to-Predict-by-the-Methods-of-Temporal-Sutton/6ce57ab17fcd507b856a79874063b59555c76b3a), while the third one involved replicating a [paper on multi-agent reinforcement learning](https://www.semanticscholar.org/paper/Correlated-Q-Learning-Greenwald-Hall/ca2663037065112facee22586ff23e760fe3f34b), including correlated equilibrium.

The second project deserves special mention—we built a deep reinforcement learning agent to land a rocket in [OpenAI’s LunarLander environment](https://gym.openai.com/envs/LunarLander-v2/)! This was very fun and provided hand-on experience with deep reinforcement learning. This included reading up and replicating DeepMind’s groundbreaking papers on Reinforcement Learning. The projects account for 15% of the overall grade each, and took upwards of 30 hours for me (i.e., coding, running experiments, writing).

There was one gigantic exam at the end of the course, covering topics from the entire course and is the remaining 25% of the overall grade. The exam format was 25 True/False questions with explanations—just indicating true or false without any explanation would not earn you any points, even if it was correct. I prepared for these largely focused on the lectures and was able to get by.

It wouldn’t be complete if I didn’t mention the excellent TAs that the course had. The TAs held office hours once, sometimes twice, a week, to help clarify on the lectures and provide guidance on the homework, projects, and exams. The class would not have been half as enriching without them. Of the four courses I’ve taken so far, the TAs in Reinforcement Learning were by far the best (though Pedro in Computer Vision was excellent as well).

## Landing the LunarLander

For the OpenAI LunarLander, the goal is to land on the moon. There are four discrete actions available: do nothing, fire left orientation engine, fire main engine, fire right orientation engine. The state is the coordinates and position of the lander.

The reward is a combination of how close the lander is to the landing pad and how close it is to zero speed, basically the closer it is to landing the higher the reward. There are other things that affect the reward such as, firing the main engine deducts points on every frame, moving away from the landing pad deducts points, crashing deducts points, etc. This reward function is determined by the Lunar Lander environment. The game or episode ends when the lander lands, crashes, or flies off away from the screen.

We had previously seen how it performed (badly) on iteration 1, but let’s just watch it crash and burn again.

On iteration 125, it’s descending at a somewhat lower speed than iteration 1, but still far from successful.

On iteration 1000, it manages to land successfully. Nonetheless, it was unduly slow in doing so and there’s plenty of room for improvement.

On iteration 2000, it finally manages to land successfully in a fairly short amount of time.

## What did I learnt?

The class teaches the fundamentals of reinforcement learning, starting with model-based methods such as value iteration and policy iteration. It also covered model-free methods such as Q-learning (i.e., the classic, tabular approach) and deep Q-learning (personally, I applied a Double DQN in the second project). In additional to single-agent approaches, it also covered multi-agent approaches and game theory, and explored multi-agent reinforcement learning.

In addition, the class provided significant practice with reading, understanding, and replicating papers. We learnt that this is a very difficult task, with most papers not clearly documenting their parameters, libraries, and code. Replicating the experiments was made harder given advances in technology—certain algorithms that performed poorly (e.g., failed to converge) during time of publishing might converge with current technology). One exception to this was DeepMind’s papers on reinforcement learning that provided a lot of detail on their algorithms, pseudo code, and parameters.

## What’s next?

I’m excited to learn further how reinforcement learning can help with understanding and predicting human behavior better, especially behavior that has a temporal aspect (e.g., customer journey on a website, a person’s health over time, etc). Hopefully I will be able to find useful use cases to apply them at work.

In addition, there’re plenty of excellent resources available online for further learning, such as:

* David Silver’s [seminars](https://www.youtube.com/watch?v=2pWv7GOvuf0&list=PLqYmG7hTraZDM-OYHWgPebj2MfCFzFObQ) which are largely introductory level and cover Sutton
* Google and Berkeley’s [Deep RL Bootcamp](https://sites.google.com/view/deep-rl-bootcamp/lectures)

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jul 2018). OMSCS CS7642 (Reinforcement Learning) Review and Tips. eugeneyan.com.
> https://eugeneyan.com/writing/omscs-cs7642-reinforcement-learning/.

or

```
@article{yan2018reinforcement,
  title   = {OMSCS CS7642 (Reinforcement Learning) Review and Tips},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2018},
  month   = {Jul},
  url     = {https://eugeneyan.com/writing/omscs-cs7642-reinforcement-learning/}
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
[deeplearning](/tag/deeplearning/)
[python](/tag/python/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Big Data & Analytics Summit - Data Science Challenges @ Lazada](/speaking/data-science-challenges-impact-lazada-talk/)
[OMSCS CS6460 (Education Technology) Review and Tips »](/writing/omscs-cs6460-education-technology/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---