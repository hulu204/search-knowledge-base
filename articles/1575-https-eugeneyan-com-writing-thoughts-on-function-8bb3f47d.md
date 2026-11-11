---
title: 'https://eugeneyan.com//writing/thoughts-on-functional-programming-in-scala-course-coursera/'
company: eugeneyan
tag: 搜索
date: 
url: https://eugeneyan.com//writing/thoughts-on-functional-programming-in-scala-course-coursera/
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

# Thoughts on Functional Programming in Scala Course (Coursera)

[
[learning](/tag/learning/)
]
 · 4 min read

At [Lazada](https://www.linkedin.com/company/lazada/)’s Data Science team, I use Spark a fair bit, especially when the data gets big (e.g., online behavioural and transaction data). While PySpark, the Python API for Spark was available when I started, I decided early on to code in Scala. Perhaps I relished the challenge or just wanted to pick up a new language.

## Why take the Functional Programming in Scala course?

Before the course, my programming skills in Scala were mainly self taught, through the school of hard knocks and stackoverflow. Thus, when the [course](https://www.coursera.org/learn/progfun1) was made available on Coursera, I saw the opportunity to learn about the fundamentals of Scala (away from Spark) and its syntax in a structured fashion.

## How is the course like?

The course is taught by Martin Odersky, designer of the Scala programming language. It follows a structure commonly found in MOOCs—approximately two hours of lectures (more theoretical) and a lab assignment taking three hours (more practical) weekly.

Over the course of six weeks, Martin taught about:

* Functional programming design (call-by-value vs. call-by-name, def vs. val, etc)
* Scala programming concepts (higher order functions, classes, objects, traits, types, etc)
* Scala’s class hierarchy and data structures (lists, vectors, maps, etc)
* Basic Scala syntax
* Pattern matching (no, not regex)
* Sub typing, Variance (covariant, contravariant, non variant)

I found the main challenge not to be Scala’s syntax, or working with a compiled language. Rather, the main challenge was thinking through the logic of solving problems through recursion. While I’ve wrote recursive algorithms before, I haven’t quite grokked it yet.

In the course, almost all assignments were solved through tail-recursion. At work, I mostly think about data in the form of tables, strings, or graphs—solving problems recursively doesn’t come up much.

## What did I learn from the course?

While the course focused on the scala language and functional programming paradigm, I gained two other lessons that I value just as much.

There was a lot of emphasis on a key software engineering practice—testing (using ScalaTest). Beginning in week one, the practice of writing unit tests was taught and encouraged. Throughout the course, Martin actively shared about edge cases in the code, and how they can be formalized and easily checked consistently in a unit test.

The lab assignments progressively taught more sophisticated ScalaTest methods, and how to test more effectively. Improving on the practice of testing will make my code more robust, my work more efficient, and me a better data scientist in the long run.

I also gained practice in breaking problems down and solving them through tail recursion. I’ve come across user-defined functions in Spark that lead to a stack overflow error when executed. Putting in additional thought and writing them in a tail recursive fashion fixed this issue and also led to efficiency improvements. Nonetheless, I’ll probably won’t be actively thinking about recursive solutions at work unless absolutely necessary.

## What’s next?

The course was excellent for learning about the thinking that went into the design of Scala as a functional language, and how to use Scala more effectively.

At the concluding lecture, Martin recommended additional learning resources. Two are worth highlighting here. First, there’s the [Scala School](https://twitter.github.io/scala_school/) by Twitter that covers the basics, collections, simple build tool (SBT) and more. Martin also recommended the [Scala Exercises](https://www.scala-exercises.org/) by 47 Degrees that covers more features of Scala through solving simple exercises in the browser interactively. I find Scala Exercises to be more practical and likely to improve my software engineering skills in Spark more.

## Conclusion

I highly recommend this short six-week course if you would like to learn the basics of Scala from the designer of Scala himself. Martin is fantastic teacher and taught effectively through online videos and lab assignments. The forums were also very helpful. Here, you’ll find people who are stuck on the same problem as you are, and teaching assistants providing helpful hints.

Questions? Want to follow my journey? Reach out on Twitter [@eugeneyan](https://twitter.com/eugeneyan)!

  

If you found this useful, please cite this write-up as:

> Yan, Ziyou. (Jul 2016). Thoughts on Functional Programming in Scala Course (Coursera). eugeneyan.com.
> https://eugeneyan.com/writing/thoughts-on-functional-programming-in-scala-course-coursera/.

or

```
@article{yan2016scala,
  title   = {Thoughts on Functional Programming in Scala Course (Coursera)},
  author  = {Yan, Ziyou},
  journal = {eugeneyan.com},
  year    = {2016},
  month   = {Jul},
  url     = {https://eugeneyan.com/writing/thoughts-on-functional-programming-in-scala-course-coursera/}
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

[« First post!](/writing/first-post/)
[Product Classification API Part 1: Data Acquisition »](/writing/product-categorization-api-part-1-data-acquisition-and-formatting/)

---

Join **11,800+** readers getting updates on machine learning, RecSys, LLMs, and engineering.

Get email updates

---