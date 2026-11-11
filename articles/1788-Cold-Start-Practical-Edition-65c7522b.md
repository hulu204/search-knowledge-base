---
title: 'Cold Start, Practical Edition'
company: Tunkelang
tag: 排序
date: 2024-09-16
url: https://dtunkelang.medium.com/cold-start-practical-edition-1b95720d4795
account: Tunkelang
origin: harvest3-202607
---
# Cold Start, Practical Edition

If you are a search application developer or some other kind of machine learning practitioner, you have probably encountered a cold start problem: launching a data-driven application without any data to drive it. There are many ways to tackle this problem, such as [transfer learning](https://en.wikipedia.org/wiki/Transfer_learning), bootstrapping with a heuristic approach, and [explore-exploit](https://en.wikipedia.org/wiki/Exploration-exploitation_dilemma) (aka [multi-armed bandits](https://en.wikipedia.org/wiki/Multi-armed_bandit)).

In practice, however, the cold start problem usually requires more than just collecting behavioral data to train a machine-learning model. You have to populate the index. Before that, you must determine what content or products you will make available through your application. After all, making stuff findable only matters if there is demand for it. Speaking of demand, you must acquire users; “if you build it, they will come” only works in the [movies](https://en.wikipedia.org/wiki/Field_of_Dreams). You have to assemble the talent, technology, and data that will enable you to deliver a successful search application. Finally, you must define success metrics and commit to achieving them.

While the cold start problem in theory is an elegant framing amenable to algorithmic solutions, the cold start problem in practice is a messy collection of real-world challenges.

For search and machine learning engineers, it can be difficult to shift focus from clean technical challenges to messy problems that span beyond models and algorithms. However, delivering practical results requires you to address those challenges. Engineering is a real-world discipline, and succeeding in it means embracing the real world in all its messy glory.

For example, when Zappos launched, it faced skepticism about the business model of selling shoes online. Rather than investing in inventory and warehouses, the founder went to local stores, took pictures of shoes, and posted them on the site. When customers purchased shoes, he bought them at the local store and shipped them himself. Of course, this model was not sustainable, but that was never its intention. Rather, it was a great way to test demand and thus [optimize for the speed of learning](https://www.linkedin.com/pulse/20130107080320-50510-optimizing-for-the-speed-of-learning).

So, when you think about launching a new search application or extending an existing one to another domain, vertical, or locale, by all means, consider the technical challenges. Launching a data-driven application when you lack behavioral data from your hopefully future users is hard!

However, recognize that the most important cold start problems may not be the technical ones. Even if your deep expertise is in machine learning and software engineering, remember that your success as a search application developer depends on overall success, not just technology.

Being a successful search application developer also means knowing something about your domain, the competitive landscape, the process of hiring search talent, the expectations of other stakeholders, etc. That might not be what you learned in your information retrieval and machine learning classes, but it is critical to your success in the real world.

Have the humility to seek help in areas outside your expertise and invest in closing those gaps. The problems are hard, but they are all surmountable. And, like the Zappos founder, always optimize for the speed of learning.
