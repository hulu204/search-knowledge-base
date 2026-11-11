---
title: 'https://eugeneyan.com//writing/why-read-papers/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/why-read-papers/
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

# How Reading Papers Helps You Be a More Effective Data Scientist

[
[learning](/tag/learning/)
]
 · 6 min read

“Instead of manually checking our data, why not try what LinkedIn did? It helped them achieve 95% precision and 80% recall.”

My teammate then shared how [LinkedIn](https://engineering.linkedin.com/research/2011/high-precision-phrase-based-document-classification-on-a-modern-scale) used *k*-nearest neighbours to identify inconsistent labels (in job titles). Then, LinkedIn trained a support vector machine (SVM) on the consistent labels; the SVM was then used to update the inconsistent labels. This helped them achieve 95% precision on their job title classifier.

This suggestion was the most useful in our discussion. Following up on it led to our product classifier’s eventual accuracy of 95%. How was she able to contribute that critical insight, I asked. “Oh, I just read papers every now and then”, she replied. To be specific, she tries to read 1 - 2 papers weekly, usually around topics that the team was working on.

By reading papers, we were able to learn what others (e.g., LinkedIn) have found to work (and not work). We can then adapt their approach and not have to reinvent the rocket. This helps us **deliver a working solution with lesser time and effort**.

> If I have seen further than others, it is by standing upon the shoulders of giants. – Isaac Newton

Reading papers also **widens our perspective**. Though we may work in narrow slices of data science, developments in tangential research are often helpful. For example, the idea of [word embeddings and graphs](/writing/recommender-systems-graph-and-nlp-pytorch/) have been useful in recommender systems. Similarly, [ideas from computer vision](https://pakodas.substack.com/p/nlp-keeps-stealing-from-cv-)—such as transfer learning and data augmentation—have been helpful for natural language processing (NLP).

Reading papers also **keeps us up to date**. The field of NLP has made large advances in the past decade. Nonetheless, by reading the most crucial 10 or so papers, we can quickly get up to speed. By being up-to-date, we become more effective at work, thus requiring less time and effort. We then have more time to read and learn, leading to a virtuous cycle.

## How to choose what papers to read?

If we’re starting on this habit, we can just **read whatever interests us**—most papers will have something to teach us. Reading about topics we’re interested in also make it easier to build the habit.

We could also select papers based on **practicality**. For example, we might need to quickly understand a domain for a project. Before starting on a project, I almost always [set aside time for a literature review](/writing/what-i-do-during-a-data-science-project-to-ensure-success/#research-what-others-have-done-and-what-worked). Spending a couple of days diving into papers can save weeks, if not months, of dead-ends and unnecessarily reinventing the wheel.

**Recommendations** are also a handy way to identify useful papers to read. One hack is to follow people we admire on social media, or subscribe to curated newsletters—I’ve found these sources to have a high information-to-noise ratio.

What papers do I read? Out of practicality, I mostly read papers related to work. This allows me to immediately apply what I’ve read and thus reinforce my learning. Outside of work, I have an interest in [sequences](https://github.com/eugeneyan/applied-ml#sequence-modelling) and tend to read about [NLP](https://github.com/eugeneyan/applied-ml#natural-language-processing) and [reinforcement learning](https://github.com/eugeneyan/applied-ml#reinforcement-learning). I’m especially fond of papers that share what worked and what didn’t, such as through ablation studies. This includes the papers on [Word2vec](https://arxiv.org/abs/1301.3781), [BERT](https://arxiv.org/abs/1810.04805), and [T5](https://arxiv.org/abs/1910.10683).

## How to read papers?

A google search for “how to read papers” returns innumerable useful results. But if you find it overwhelming, here’s a couple that I found helpful:

* The *classic* [three-pass approach](https://web.stanford.edu/class/ee384m/Handouts/HowtoReadPaper.pdf) (and a [three-minute video](https://www.youtube.com/watch?v=SKxm2HF_-k0) version)
* [OMSCS 6460 How To Read An Academic Paper](http://omscs6460.gatech.edu/research-guide/how-to-read-an-academic-paper/): Advice from a favourite Prof
* [Interviews](https://www.sciencemag.org/careers/2016/03/how-seriously-read-scientific-paper) with other scientists sharing their approach
* An [approach](https://cseweb.ucsd.edu/~wgg/CSE210/howtoread.html) for engineering-research papers
* [Reassurance](https://www.sciencemag.org/careers/2016/01/how-read-scientific-paper) that we’re not the only ones finding it hard

My method is similar to the three-pass approach. In the example below, I’ll share how I read several recsys papers to learn about the metrics of novelty, diversity, serendipity. etc.

**In the first pass**, I scan the abstract to understand if the paper has what I need. If it does, I skim through the headings to identify the problem statement, methods, and results. In this example, I’m specifically looking for formula on how to calculate the various metrics. I give all papers on my list a first pass (and resist starting on a second pass until I’ve completed the list). In this example, about **half of the papers** made it to the second pass.

![List of papers remaining after first pass](/assets/paper-list.webp "List of papers remaining after first pass")

After the first pass, 30+ papers were reduced to 14—that’s good effort saved.

**In the second pass**, I go over each paper again and **highlight the relevant sections**. This helps me quickly spot important portions when I refer to the paper later. Then, I take notes for each paper. In this example, the notes were mostly around metrics (i.e., methods, formula). If it was a literature review for an application (e.g., recsys, product classification, fraud detection), the notes would focus on the methods, system design, and results.

![Sample paper notes](/assets/lit-note.webp "Sample paper notes")

Sample notes from three papers; notes specific to metrics boxed in red.

For most papers, the second pass suffices. I’ve captured the key information and can refer to it in future if needed. Nonetheless, I sometimes do a third pass if I’m reading papers as part of a literature review, or if I want to cement my knowledge.

> Reading furnishes the mind only with materials of knowledge; it is thinking that makes what we read ours. – John Locke

**In the third pass**, I synthesize the common concepts across papers into their own notes. Various papers have their own methods to measure novelty, diversity, serendipity, etc. I consolidate them into a single note and compare their pros and cons. While doing this, I often find gaps in my notes and knowledge and have to revisit the original paper.

![Sample metric notes](/assets/perm-note.webp "Sample metric notes")

Sample notes on the serendipity and unexpectedness metric.

Lastly, if I think it’ll be useful for others, I write about what I’ve learnt and publish it online. Relative to starting from scratch, having my notes as a reference makes writing much easier. This has led to pieces such as:

* [Beating the Baseline Recommender with Graph & NLP in Pytorch](/writing/recommender-systems-graph-and-nlp-pytorch/)
* [Serendipity: Accuracy’s Unpopular Best Friend in Recommenders](/writing/serendipity-and-accuracy-in-recommender-systems/)
* [NLP for Supervised Learning - A Brief Survey](/writing/nlp-supervised-learning-survey/)

## Try it for yourself

Before jumping deep into your next project, spend a day or two scanning through a couple of relevant papers. I’m confident it’ll save you time and effort in the medium to long term. Not sure where to start? Here are some useful resources to start with:

* [Papers with Code](https://paperswithcode.com): ML Research with the code to implement it
* [`applied-ml`](https://github.com/eugeneyan/applied-ml): Papers on how organizations built and deployed ML systems
* [`ml-surveys`](https://github.com/eugeneyan/ml-surveys): Survey papers summarising recent ML advancements
* [Google Scholar Alerts](https://scholar.google.com/intl/en/scholar/help.html#alerts): Updates when new publications match your query
* [42 Papers](https://42papers.com/): Trending papers in AI and Computer Science

> Why read papers? Because it:   
>   
> • Widens our perspective  
> • Keeps us up to date  
> • Helps us deliver with less time & effort  
>   
> Here, I'll share some ways to pick papers, how-to resources, and my approach (with screenshots).<https://t.co/7hGjxpkUvZ>
>
> — Eugene Yan (@eugeneyan) [September 2, 2020](https://twitter.com/eugeneyan/status/1300954984461156352?ref_src=twsrc%5Etfw)

**Thanks** to Yang Xinyi for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Aug 2020). How Reading Papers Helps You Be a More Effective Data Scientist. eugeneyan.com.
> https://eugeneyan.com/writing/why-read-papers/.

or

```
@article{yan2020read,
  title   = {How Reading Papers Helps You Be a More Effective Data Scientist},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Aug},
  url     = {https://eugeneyan.com/writing/why-read-papers/}
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
[learning](/tag/learning/)
]
  or [![](/assets/icon-search.svg)Search](/search/ "Search")

[« Mailbag: I'm Now a Senior DS—How should I Approach this?](/writing/mailbag-senior-ds/)
[Datacast Podcast - Effective Data Science with Eugene Yan »](/speaking/datacast-eugeneyan/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---