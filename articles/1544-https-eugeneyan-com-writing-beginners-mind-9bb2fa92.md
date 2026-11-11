---
title: 'https://eugeneyan.com//writing/beginners-mind/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/beginners-mind/
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

# Embrace Beginner's Mind; Avoid The Wrong Way To Be An Expert

[
[learning](/tag/learning/)
]
 · 11 min read

When we learn something new, such as a programming language, we start as beginners. We can learn and follow the rules and apply them in a narrow context. However, we don’t understand the bigger picture and get lost outside of that specific context.

Imagine that I enroll in a [MOOC](https://en.wikipedia.org/wiki/Massive_open_online_course) on `R` and learn about statistical analysis, machine learning, and [`Shiny`](https://rstudio.github.io/shinydashboard/) dashboards. As part of machine learning, I learn that I should [split the data into train and test](https://www.rdocumentation.org/packages/caret/versions/6.0-86/topics/createDataPartition) sets. I apply this in assignments and Kaggle and everything works fine—this is the *narrow* context.

Then, perhaps I get the opportunity to apply my new skills in a *wider* context—I build a model, validate it (via random train-test split), and deploy it. However, the offline and online (i.e., A/B test) metrics don’t match up. Eventually, I figure out that I should use a [time-based split](https://www.fast.ai/2017/11/13/validation-sets/) so future data doesn’t *leak* into the training set.

With the benefit of the wider context, I encountered challenges and failures (read: lessons) that were not part of the MOOC assignments. As a result, I got to see the bigger picture; I know there’s still lots to learn. Thus, I continue to learn and progress through the stages of beginner, intermediate, and so on.

> The more I learn, the more I realise how much I don’t know. – Albert Einstein

## From beginner to … expert beginner

But what happens if I *don’t* see the bigger picture?

Let’s assume I work in the HR department of a widget manufacturer. Everything—from headcount to payroll to vacation balance—is run in Excel. I apply my newfound `R` skills to automate my work via one-off scripts. This involves calculating statistics on factory sites and displaying it via a `Shiny` dashboard on the department desktop. In the eyes of my manager and team, I’m an absolute rockstar ninja wizard. I get showered with praise and am promoted to manager of HR data science.

I might not know about proper ML validation, deployment, unit tests, or even version control. I certainly haven’t done any of that. But who cares? We don’t need it. I’m now the manager of HR data science. I’m now… an “expert”.

To those in the know, I’m clearly still a beginner. But my context is narrow and I don’t see the bigger picture. Thus, I don’t know that there’s still lots to learn, lots to do. However, because I’ve achieved a modicum of success (through *narrow* applications of what I learned) and others call me an expert, I now view myself as an expert. As a result, I stop learning. I’m now stuck at a local optima. **I’ve become an [expert beginner](https://daedtech.com/how-developers-stop-learning-rise-of-the-expert-beginner/)**.

Suppose I stay in that same role, within HR, for 10 years. At the end of it, do I have 10 years of experience, or one year of experience repeated 10 times?

An army of expert beginners led by an expert beginner

As head of HR data science, I hire a team of data scientists. Eventually, some team members will suggest new technology (e.g., Python, Docker) or practices (e.g., version control, unit testing).

However, I’m the most experienced (read: longest tenure) and the expert-est expert. I dismiss ideas and technology that I’m unfamiliar with. “Oh, I see you’re new here. Yes, Python sounds like a good idea but the Chief HR Officer really likes the `Shiny` dashboard that I built.” “Haha, we don’t need unit tests! I live and breathe this code every day—there’s no need to test it”.

Team members who can see the bigger picture are disappointed by the outdated technology and incorrect practices. They see no room for learning and growth. As a result, **the most talented and ambitious leave** (if they know what’s best for them). For those who stay—hurray! There’s less competition. They’ll toe the line and one day, they’ll be a *senior* expert beginner and teach new joiners their “expert” ways.

This leads to the [Dead Sea effect](http://brucefwebster.com/2008/04/11/the-wetware-crisis-the-dead-sea-effect/) where you’re **left with your least talented and effective** people. They’re grateful to have a job and settle in for a couple of years (or decades). Now, the team has (d)evolved into an army of expert beginners who follow the directions of the top expert beginner.

![The expert beginners are entrenched and can’t be replace](/assets/dead-sea.webp "The expert beginners are entrenched and can’t be replace")

The expert beginners are entrenched and can’t be replaced (source: [Scott Adams](https://dilbert.com/strip/2010-12-02))

Because expert beginners have learned “everything” there is to learn, tried “everything” there is to try, and done “everything” there is to do, there’s nothing new to learn, try, and do. The team stops trying new ideas—“Oh we don’t use Docker here. We have VMs!”—and the organization stops innovating.

This partly explains some industries getting disrupted. The iPhone disrupting Nokias and Blackberrys, AWS disrupting on-premise hardware, Stripe disrupting payment processing, Tesla disrupting… you get the idea.

![The expert beginner doesn't see the bigger picture and is thus stuck](/assets/climbed-it-all.webp "The expert beginner doesn't see the bigger picture and is thus stuck")

The expert beginner doesn't see the bigger picture; thus, he is stuck.

## The beginner’s mind is always a student

How do we prevent stagnation (and possibly becoming an expert beginner)? How do we stay open-minded and constantly learning and experimenting?

**One way is [Shoshin](https://en.wikipedia.org/wiki/Shoshin) (beginner’s mind)**. It’s a concept from Zen Buddhism on having an attitude of openness, eagerness, and no preconceptions, even when our knowledge of the subject is advanced. In other words, to think *just* like a beginner.

> In the beginner’s mind there are many possibilities, but in the expert’s there are few. – Shunryu Suzuki

With beginner’s mind, regardless of your experience and expertise, you **stay curious and approach new ideas and experiences as a student**. Even when new technology or methods don’t fit your paradigm, you’re open to learning and trying it. Students don’t say “That’s not how we do things here”.

Sometimes, when others view us as experts, we let it get to us. We stay within our narrow subject matter expertise and stop exploring new ideas and possibilities. We avoid newer, bigger challenges so we don’t make mistakes; we stick to what has worked in the past. This helps preserve our expert identity.

> The most dangerous phrase in the language is, “We’ve always done it this way.” – Grace Hopper

But this doesn’t make sense. In my field of data science, new tools (e.g., Spark, Docker, Airflow) and methods (e.g., embeddings, attention, pre-training) constantly improve on the state of the art (SOTA)—it’s useful, if not essential, to keep up to date. (That said, fundamental techniques like regression and decision trees are often a solid baseline.)

## The beginner’s mind keeps on pedalling

Learning is like cycling. When we start pedalling (from a standstill), it takes effort and time to gain momentum. Nonetheless, we’ll pick up speed and begin gaining distance.

We might look back at where we started and think “Wow, I’ve come a long way. Perhaps I don’t have to pedal as hard; perhaps I don’t have to pedal at all.” If we stop pedalling, the initial momentum might carry us slightly further, but eventually, we’ll come to a standstill. While we don’t lose the distance covered, we’re not gaining distance either. (Though in fast-paced fields like tech, if you don’t move forward, *you begin to move backward*.)

Here, distance is knowledge (and achievements); momentum is learning. While distance is correlated with expertise, the relationship is not as strong as we think (e.g., one year of experience repeated 10 times). I think momentum (the ability to learn and adapt quickly) is part of expertise as well. The experts I know are often reading or hacking. At work, they can synthesize their mental prototypes and tailor solutions based on context.

To maintain momentum, **the beginner’s mind continues to pedal regardless of the distance they’ve covered**. It’s not surprising that many successful people are—and continue to be—voracious readers and learners. Warren Buffet, Bill Gates, Elon Musk, just to name a few. Do you know any successful person that doesn’t read or learn?

> The illiterate of the 21st century will not be those who cannot read and write, but those who cannot learn, unlearn, and relearn. – Alvin Toffler

Note: Not all knowledge is the same

There’s knowledge that we gain from books and courses—we’re tested on this in exams. Then, there’s [(tacit) knowledge](https://commoncog.com/blog/the-tacit-knowledge-series/) that we gain from practice—we’re tested on this in life.

> You cannot get educated by this self-propagating system in which people study to pass exams, and teach others to pass exams, but nobody knows anything.  
>   
> You learn something by doing it yourself, by asking questions, by thinking, and by experimenting. 🧠
>
> — Richard Feynman (@ProfFeynman) [August 17, 2020](https://twitter.com/ProfFeynman/status/1295411496407556096?ref_src=twsrc%5Etfw)

For example, learning to ride a bicycle. We can’t learn to ride a bike by reading a textbook. The **only way to learn is by actually doing it**. We’re going to lose balance and fall, but eventually, we’ll figure it out. Also, our ability to ride a bike is **transferable** to other two-wheeled transport. Once we learn how to ride a regular bike, we’ll have a gentler learning curve on mountains bikes, tandem bikes, and even e-scooters.

Similarly, some skills and knowledge **can only be gained through practice**. They’re usually **transferable** across multiple domains too. For example, what’s the most suitable way to [serve models in production](https://bugra.github.io/posts/2020/5/25/how-to-serve-model/)? There are some common patterns: compute offline and cache, serve via microservice, embed in the main app. Do these patterns differ across domains? Not much. Which is the best approach for our use case? Well, it depends—knowing the answer is tacit knowledge.

> [pic.twitter.com/jGcy74wKP1](https://t.co/jGcy74wKP1)
>
> — Nader Dabit (@dabit3) [July 7, 2020](https://twitter.com/dabit3/status/1280545282032271361?ref_src=twsrc%5Etfw)

Often, such skills and knowledge are **fundamental** and can be thought of as building blocks (or [first principles](https://jamesclear.com/first-principles)). For example, in programming, we learn about conditionals, iteration, and data structures. In distributed data processing, we learn about map, reduce, and shuffle. Once we understand these fundamentals, it’s easier to pick up another programming language or distributed processing framework. It also helps us write more effective software and [ETL](https://en.wikipedia.org/wiki/Extract,_transform,_load) jobs.

Mastering the fundamentals also helps with the [metagame](https://commoncog.com/blog/to-get-good-go-after-the-metagame/). The meta (i.e., higher-order factors) changes constantly. For example, [natural language processing](/writing/nlp-supervised-learning-survey/) has evolved rapidly from recurrent models to embeddings to attention to pre-training.

If we’ve been paying attention, we might have noticed *cross-pollination* of [ideas from computer vision](https://pakodas.substack.com/p/nlp-keeps-stealing-from-cv-) (e.g., transfer learning). Also, the big improvements due to unsupervised learning (e.g., [Word2vec](/writing/nlp-supervised-learning-survey/#word-embeddings-to-learn-from-unlabelled-data-2013), [T5](/writing/nlp-supervised-learning-survey/#everything-is-text-to-text), [GPT-3](https://openai.com/blog/openai-api/)) demonstrate that *data is king*. Lastly, as models grow bigger to push on the SOTA, we see another meta—*more compute wins* (i.e., [The Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html)).

## How to develop beginner’s mind and keep pedalling

If you’re convinced about beginner’s mind, here are some suggestions on mindset:

* **Stay humble**. Yes, we should take pride in our accomplishments. But we should never think our learning is complete or that we’re infallible. This requires us to be patient with ourselves, to be able to say “I don’t know”, and to be okay with failure.
* **Be curious** and open-minded to try new ideas, even if they don’t match our preconceptions. Explore new approaches instead of “how we’ve always done it”.

And some habits to keep learning:

* **Build and tinker**. Some skills are best gained via practice. At work, continue to contribute code (if you can). Outside of work, find time to try new tools and techniques. This keeps us up-to-date and grounded in the details.
* **Read widely**. Read a paper or three each week, take notes, and discuss with your peers. (Shameless plug: [`applied-ml`](https://github.com/eugeneyan/applied-ml) and [`ml-surveys`](https://github.com/eugeneyan/ml-surveys) are great collections.)
* **Engage with the wider community**. Attend meetups and conferences. They help us see the bigger picture outside our roles and organizations. Attend one meetup per quarter and one conference per year. With most of them online now, it’s easier.

If you’re leading a team or organization, **create a culture of learning**. Encourage your team to read and discuss papers. Give your team the space to explore and fail. Celebrate A/B tests as they help us learn more about the customer—even those, especially those, that didn’t work out. Encourage external learning (e.g., company brown bags, meetups, conferences). When hiring, don’t over-index on education qualifications or years of experience.

There’s *always* more to learn.

> Expert mind: Nothing's new  
> Beginner mind: Everything's new  
>   
> Expert mind: Look how far I've come  
> Beginner mind: Look how far it goes  
>   
> Expert mind: We've always done it this way  
> Beginner mind: There's always a better way  
>   
> The Beginner's mind keeps learning <https://t.co/trMxZPuaDv>
>
> — Eugene Yan (@eugeneyan) [August 26, 2020](https://twitter.com/eugeneyan/status/1298421733628600320?ref_src=twsrc%5Etfw)

**Thanks** to Yang Xinyi, [Sara Campbell](https://tinyrevolutions.substack.com/), [Stew Fortier](https://stewfortier.com/), [Dan Hunt](https://danhunt.com/), and [Joel Christiansen](https://joelc.io/) for reading drafts of this.

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Aug 2020). Embrace Beginner's Mind; Avoid The Wrong Way To Be An Expert. eugeneyan.com.
> https://eugeneyan.com/writing/beginners-mind/.

or

```
@article{yan2020beginner,
  title   = {Embrace Beginner's Mind; Avoid The Wrong Way To Be An Expert},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2020},
  month   = {Aug},
  url     = {https://eugeneyan.com/writing/beginners-mind/}
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

[« NLP for Supervised Learning - A Brief Survey](/writing/nlp-supervised-learning-survey/)
[Mailbag: I'm Now a Senior DS—How should I Approach this? »](/writing/mailbag-senior-ds/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---